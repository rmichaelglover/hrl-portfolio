#pragma once
#include "virtual_cell.hpp"
#include <cstdint>
#include <limits>
#include <random>

namespace virtual_cell::bio::cycle {

enum class EnzymeState { Free, SubstrateBound, ProductsBound };
struct Rates {
    // Buffered assay concentrations are mM; on-rates mM^-1 s^-1; others s^-1.
    // Defaults are illustrative. They are not fitted microscopic IMPase rates.
    double substrate_mm=1, lithium_mm=0;
    double substrate_on=2, substrate_off=0.5, catalysis=3;
    double product_release=1, lithium_product_release=0.2;
    double lithium_on=1, lithium_off=0.5;
    void validate() const {
        for (double x:{substrate_mm,lithium_mm,substrate_off,lithium_on,lithium_off}) nonnegative(x);
        for (double x:{substrate_on,catalysis,product_release,lithium_product_release})
            if (nonnegative(x)==0) throw std::invalid_argument("Positive rate required");
        finite(substrate_on*substrate_mm); finite(lithium_on*lithium_mm);
    }
};
inline double event_probability(double rate_per_second,double seconds) {
    nonnegative(rate_per_second); nonnegative(seconds);
    if (rate_per_second==0 || seconds==0) return 0;
    return -std::expm1(-finite(rate_per_second*seconds));
}
struct Event { std::size_t target; double rate; bool cycle_completed; };
using Events=std::array<Event,2>;
inline Events events(std::size_t state,const Rates& r) {
    switch (state) {
        case 0:return {{{1,r.substrate_on*r.substrate_mm,false},{0,0,false}}};
        case 1:return {{{2,r.catalysis,false},{0,r.substrate_off,false}}};
        case 2:return {{{0,r.product_release,true},{3,r.lithium_on*r.lithium_mm,false}}};
        case 3:return {{{0,r.lithium_product_release,true},{2,r.lithium_off,false}}};
        default:throw std::invalid_argument("Unknown enzyme microstate");
    }
}

class Enzyme {
    EnzymeState state_=EnzymeState::Free;
    bool lithium_bound_=false;
    std::uint64_t cycles_=0;
public:
    EnzymeState state() const { return state_; }
    bool has_lithium() const { return lithium_bound_; }
    std::uint64_t completed_cycles() const { return cycles_; }
    bool bind_substrate() {
        if (state_!=EnzymeState::Free) return false;
        state_=EnzymeState::SubstrateBound;return true;
    }
    bool catalyze() {
        if (state_!=EnzymeState::SubstrateBound) return false;
        state_=EnzymeState::ProductsBound;return true;
    }
    bool release_products() {
        if (state_!=EnzymeState::ProductsBound) return false;
        if (cycles_==std::numeric_limits<std::uint64_t>::max()) throw std::overflow_error("Cycle count overflow");
        // Candidate joint release: if Li is bound it returns to the buffer too.
        // This is an explicit proposed pathway, not an established IMPase step.
        state_=EnzymeState::Free;lithium_bound_=false;++cycles_;return true;
    }
    bool bind_lithium() {
        if (state_!=EnzymeState::ProductsBound || lithium_bound_) return false;
        lithium_bound_=true;return true;
    }
    bool release_lithium() {
        if (!lithium_bound_) return false;
        lithium_bound_=false;return true;
    }
    double product_release_rate(const Rates& r) const {
        r.validate();
        return state_!=EnzymeState::ProductsBound?0:
            lithium_bound_?r.lithium_product_release:r.product_release;
    }
    double release_probability(double seconds,const Rates& r) const {
        return event_probability(product_release_rate(r),seconds);
    }
    // Exact Gillespie sampling for a time-homogeneous buffered assay.
    // No agent permission is required for a molecular transition.
    void advance(double seconds,const Rates& r,std::mt19937_64& rng) {
        nonnegative(seconds);r.validate();
        std::uniform_real_distribution<double> uniform(0,1);
        double remaining=seconds;
        std::size_t event_count=0;
        while (remaining>0) {
            const std::size_t index=state_==EnzymeState::Free?0:
                state_==EnzymeState::SubstrateBound?1:lithium_bound_?3:2;
            const auto outgoing=events(index,r);
            const double total=finite(outgoing[0].rate+outgoing[1].rate);
            if (total==0) return;
            const double wait=-std::log1p(-uniform(rng))/total;
            if (wait>remaining) return;
            if (++event_count>10000000) throw std::runtime_error("Event budget exceeded");
            remaining-=wait;
            const auto& event=outgoing[uniform(rng)*total<outgoing[0].rate?0:1];
            if (event.cycle_completed) { release_products();continue; }
            if (index==0) bind_substrate();
            else if (index==1 && event.target==2) catalyze();
            else if (index==1) state_=EnzymeState::Free;
            else if (index==2) bind_lithium();
            else release_lithium();
        }
    }
};

struct Stationary {
    std::array<double,4> fractions;
    double cycles_per_second;
};
inline Stationary stationary(const Rates& r) {
    r.validate();
    const double a=r.substrate_on*r.substrate_mm,b=r.lithium_on*r.lithium_mm;
    if (a==0) return {{{1,0,0,0}},0};
    const double determinant=finite(r.product_release*(r.lithium_product_release+r.lithium_off)
                                    +b*r.lithium_product_release);
    const double product_dwell=(r.lithium_product_release+r.lithium_off+b)/determinant;
    const double free_dwell=(1+r.substrate_off/r.catalysis)/a;
    const double substrate_dwell=1/r.catalysis;
    const double flux=1/finite(free_dwell+substrate_dwell+product_dwell);
    return {{{flux*free_dwell,flux*substrate_dwell,
              flux*(r.lithium_product_release+r.lithium_off)/determinant,flux*b/determinant}},flux};
}

// Master equation and cycle-count reward, propagated by Poisson uniformization.
// Expected values, not a single molecule's fractional physical state.
class Ensemble {
    std::array<double,4> probabilities_{{1,0,0,0}};
    double cycles_=0;
public:
    const auto& fractions() const { return probabilities_; }
    double expected_cycles() const { return cycles_; }
    void advance(double seconds,const Rates& r) {
        nonnegative(seconds);r.validate();
        double nu=0;
        for (std::size_t state=0;state<4;++state) {
            const auto e=events(state,r);nu=std::max(nu,finite(e[0].rate+e[1].rate));
        }
        if (seconds==0 || nu==0) return;
        const double count=std::ceil(finite(seconds*nu)/10);
        if (count>10000000) throw std::invalid_argument("Too many propagation steps");
        const double dt=seconds/count,lambda=nu*dt;
        for (std::size_t step=0;step<static_cast<std::size_t>(count);++step) {
            auto current=probabilities_;
            std::array<double,4> sum{};
            double current_reward=0,reward_sum=0;
            double weight=std::exp(-lambda),mass=0;
            for (unsigned k=0;k<200;++k) {
                for (std::size_t i=0;i<4;++i) sum[i]+=weight*current[i];
                reward_sum+=weight*current_reward;mass+=weight;
                if (k>lambda && weight<1e-17) break;
                std::array<double,4> next{};
                for (std::size_t i=0;i<4;++i) {
                    const auto outgoing=events(i,r);
                    double exit=0;
                    for (const auto& e:outgoing) {
                        next[e.target]+=current[i]*e.rate/nu;
                        exit+=e.rate;
                        if (e.cycle_completed) current_reward+=current[i]*e.rate/nu;
                    }
                    next[i]+=current[i]*(1-exit/nu);
                }
                current=next;weight*=lambda/(k+1);
            }
            if (std::abs(mass-1)>1e-12) throw std::runtime_error("Poisson truncation failed");
            for (double& p:sum) p/=mass;
            probabilities_=sum;cycles_=finite(cycles_+reward_sum/mass);
        }
    }
};
} // namespace virtual_cell::bio::cycle
