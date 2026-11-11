#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace virtual_cell::electric {
namespace detail {
inline double checked(double x) {
    if (!std::isfinite(x)) throw std::invalid_argument("Finite electrical quantity required");
    return x;
}
inline double nonnegative(double x) {
    if (checked(x)<0) throw std::invalid_argument("Nonnegative electrical quantity required");
    return x;
}
inline double positive(double x) {
    if (nonnegative(x)==0) throw std::invalid_argument("Positive electrical quantity required");
    return x;
}
}

// Concentration-ratio approximation to activities. Inside minus outside voltage.
inline double nernst_mv(int valence,double inside_mm,double outside_mm,double kelvin=310.15) {
    if (valence==0) throw std::invalid_argument("An ion must have nonzero valence");
    detail::positive(inside_mm);detail::positive(outside_mm);detail::positive(kelvin);
    constexpr double gas_constant=8.31446261815324,faraday=96485.33212;
    return detail::checked(1000*gas_constant*kelvin/(valence*faraday)
                           *(std::log(outside_mm)-std::log(inside_mm)));
}
struct Conductance {
    double nanosiemens;
    double reversal_mv;
    void validate() const { detail::nonnegative(nanosiemens);detail::checked(reversal_mv); }
};
struct MembraneParameters {
    double capacitance_pf=100;
    double leak_ns=5;
    double leak_reversal_mv=-65;
    void validate() const {
        detail::positive(capacitance_pf);detail::nonnegative(leak_ns);detail::checked(leak_reversal_mv);
    }
};
struct SpikeRule {
    double threshold_mv=-50;
    double reset_mv=-65;
    double refractory_ms=2;
    void validate() const {
        detail::checked(threshold_mv);detail::checked(reset_mv);detail::nonnegative(refractory_ms);
        if (reset_mv>=threshold_mv) throw std::invalid_argument("Reset must be below threshold");
    }
};

// A valid, value-owned electrical state: no init()/shutdown(), new, or delete.
// Ohmic subthreshold dynamics are physical; threshold/reset is a reduced model.
class Membrane {
    MembraneParameters parameters_;
    double voltage_mv_;
    std::optional<SpikeRule> spike_rule_;
    double refractory_remaining_ms_=0;
    std::size_t spike_count_=0;
public:
    explicit Membrane(MembraneParameters parameters={},double initial_mv=-65,
                      std::optional<SpikeRule> spike_rule=std::nullopt)
        : parameters_(parameters),voltage_mv_(detail::checked(initial_mv)),spike_rule_(spike_rule) {
        parameters_.validate();
        if (spike_rule_) {
            spike_rule_->validate();
            if (initial_mv>=spike_rule_->threshold_mv)
                throw std::invalid_argument("Spiking membrane must start below threshold");
        }
    }
    double voltage_mv() const { return voltage_mv_; }
    const MembraneParameters& parameters() const { return parameters_; }
    bool can_spike() const { return spike_rule_.has_value(); }
    std::size_t spike_count() const { return spike_count_; }
    double refractory_remaining_ms() const { return refractory_remaining_ms_; }
    std::vector<double> advance_events(double dt_ms,double inward_current_pa=0,
                 const std::vector<Conductance>& inputs={}) {
        detail::nonnegative(dt_ms);detail::checked(inward_current_pa);
        double g=parameters_.leak_ns;
        double drive=detail::checked(inward_current_pa+g*parameters_.leak_reversal_mv);
        for (const auto& input:inputs) {
            input.validate();g=detail::checked(g+input.nanosiemens);
            drive=detail::checked(drive+input.nanosiemens*input.reversal_mv);
        }
        std::vector<double> spikes;
        double remaining=dt_ms;
        while (remaining>0) {
            if (refractory_remaining_ms_>0) {
                const double held=std::min(remaining,refractory_remaining_ms_);
                remaining-=held;refractory_remaining_ms_-=held;
                voltage_mv_=spike_rule_->reset_mv;
                if (remaining==0) break;
            }
            // Inputs are constant during this local interval. Solve the crossing
            // time as well as the voltage, so reset does not lose part of a step.
            double crossing=std::numeric_limits<double>::infinity();
            if (spike_rule_) {
                if (g==0 && drive>0)
                    crossing=(spike_rule_->threshold_mv-voltage_mv_)*parameters_.capacitance_pf/drive;
                else if (g>0) {
                    const double equilibrium=detail::checked(drive/g);
                    if (equilibrium>spike_rule_->threshold_mv)
                        crossing=-parameters_.capacitance_pf/g*std::log1p(
                            -(spike_rule_->threshold_mv-voltage_mv_)/(equilibrium-voltage_mv_));
                }
            }
            if (crossing<=remaining) {
                if (spike_count_==std::numeric_limits<std::size_t>::max())
                    throw std::overflow_error("Spike counter overflow");
                if (spikes.size()>=1000000) throw std::runtime_error("Too many spikes in one interval");
                remaining-=crossing;
                spikes.push_back(dt_ms-remaining);
                ++spike_count_;voltage_mv_=spike_rule_->reset_mv;
                refractory_remaining_ms_=spike_rule_->refractory_ms;
                continue;
            }
            // pF*mV/ms = pA; nS*mV = pA. Constant-drive RC update is exact.
            if (g==0) voltage_mv_=detail::checked(voltage_mv_+drive*remaining/parameters_.capacitance_pf);
            else {
                const double equilibrium=detail::checked(drive/g);
                const double fraction=-std::expm1(-detail::checked(g*remaining/parameters_.capacitance_pf));
                voltage_mv_=detail::checked(voltage_mv_+(equilibrium-voltage_mv_)*fraction);
            }
            remaining=0;
        }
        return spikes;
    }
    bool advance(double dt_ms,double inward_current_pa=0,
                 const std::vector<Conductance>& inputs={}) {
        return !advance_events(dt_ms,inward_current_pa,inputs).empty();
    }
};

// Indices are local to their owning Body. No graph edge holds a Cell pointer.
struct CellId {
    bool in_brain;
    std::size_t organ_index,tissue_index,cell_index;
    static CellId brain(std::size_t tissue,std::size_t cell) { return {true,0,tissue,cell}; }
    static CellId organ(std::size_t organ,std::size_t tissue,std::size_t cell) {
        return {false,organ,tissue,cell};
    }
    bool operator==(const CellId& other) const {
        return in_brain==other.in_brain && organ_index==other.organ_index
            && tissue_index==other.tissue_index && cell_index==other.cell_index;
    }
};
struct CurrentInput { CellId target; double inward_pa; };
struct SynapseParameters {
    double peak_ns=20,decay_ms=4,reversal_mv=0,delay_ms=1;
    void validate() const {
        detail::nonnegative(peak_ns);detail::positive(decay_ms);
        detail::checked(reversal_mv);detail::positive(delay_ms);
    }
};
struct Synapse {
    CellId source,target;
    SynapseParameters parameters;
    double conductance_ns=0;
};
struct ConductanceInput { CellId target; Conductance channel; };
struct Spike { CellId source; double time_ms; };

// Owns routing, conductance states and pending events by value. Body validates
// its endpoint IDs; the routing graph never owns a second copy of any cell.
class NervousSystem {
    struct Arrival { double time_ms;std::size_t synapse; };
    std::vector<Synapse> synapses_;
    std::vector<Arrival> arrivals_;
    std::vector<Spike> spikes_;
public:
    void connect(CellId from,CellId to,SynapseParameters parameters) {
        parameters.validate();synapses_.push_back({from,to,parameters,0});
    }
    const auto& synapses() const { return synapses_; }
    const auto& spikes() const { return spikes_; }
    std::size_t pending_event_count() const { return arrivals_.size(); }
    std::vector<ConductanceInput> interval_inputs(double time_ms,double dt_ms) {
        detail::nonnegative(time_ms);detail::positive(dt_ms);
        // Due arrivals are delivered at the next grid boundary. Sorting is not
        // required: event order cannot change a sum of independent conductances.
        for (const auto& event:arrivals_)
            if (event.time_ms<=time_ms+1e-10)
                synapses_.at(event.synapse).conductance_ns=detail::checked(
                    synapses_.at(event.synapse).conductance_ns+synapses_.at(event.synapse).parameters.peak_ns);
        arrivals_.erase(std::remove_if(arrivals_.begin(),arrivals_.end(),[&](const Arrival& e){
            return e.time_ms<=time_ms+1e-10;
        }),arrivals_.end());
        std::vector<ConductanceInput> result;
        for (auto& synapse:synapses_) {
            const double ratio=dt_ms/synapse.parameters.decay_ms;
            // Exact interval-average exponential g; the voltage equation uses
            // this average, so the combined time-varying solve is approximate.
            const double average=ratio==0?synapse.conductance_ns:
                synapse.conductance_ns*(-std::expm1(-ratio))/ratio;
            result.push_back({synapse.target,{average,synapse.parameters.reversal_mv}});
            synapse.conductance_ns*=std::exp(-ratio);
        }
        return result;
    }
    void record_spike(CellId source,double time_ms) {
        detail::nonnegative(time_ms);
        spikes_.push_back({source,time_ms});
        for (std::size_t i=0;i<synapses_.size();++i)
            if (synapses_[i].source==source)
                arrivals_.push_back({detail::checked(time_ms+synapses_[i].parameters.delay_ms),i});
    }
};
} // namespace virtual_cell::electric
