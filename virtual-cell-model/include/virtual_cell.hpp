#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
#include <optional>
#include "bioelectric.hpp"

namespace virtual_cell {

inline double nonnegative(double value) {
    if (!std::isfinite(value) || value < 0.0)
        throw std::invalid_argument("Expected a finite, nonnegative value");
    return value;
}

inline double finite(double value) {
    if (!std::isfinite(value)) throw std::invalid_argument("Expected a finite value");
    return value;
}

struct ElementCounts {
    unsigned carbon, hydrogen, nitrogen, oxygen;
};

class Molecule {
    std::string name_;
    ElementCounts composition_;
public:
    Molecule(std::string name, ElementCounts composition)
        : name_(std::move(name)), composition_(composition) {}
    const std::string& name() const { return name_; }
    const ElementCounts& composition() const { return composition_; }
};

class MolecularCollection {
    std::vector<Molecule> molecules_;
public:
    void add(const Molecule& molecule) { molecules_.push_back(molecule); }
    std::size_t size() const { return molecules_.size(); }
    bool transfer_last_to(MolecularCollection& destination) {
        if (this == &destination || molecules_.empty()) return false;
        destination.molecules_.push_back(molecules_.back());
        molecules_.pop_back();
        return true;
    }
};

enum class CellAction { Remain, Differentiate };
enum class CellState { Undifferentiated, Differentiated };

// Toy energy units and utility units are separate scales throughout.
class TransitionProposal {
    double energy_;
public:
    explicit TransitionProposal(double energy) : energy_(nonnegative(energy)) {}
    double energy_required() const { return energy_; }
};

struct CellFeatures {
    double available_energy;
    double regulatory_signal;
};

// Handwritten trees demonstrate a forest interface. They are not trained models.
class TeachingForest {
public:
    double predict_success(const CellFeatures& features) const {
        nonnegative(features.available_energy);
        finite(features.regulatory_signal);
        const double first = features.regulatory_signal < 0.5 ? 0.2 : 0.8;
        const double second = features.available_energy < 3.0 ? 0.3 : 0.6;
        const double third = features.regulatory_signal < 0.6 ? 0.3 : 0.7;
        return (first + second + third) / 3.0;
    }
};

class ActionEstimate {
    double probability_, benefit_, cost_;
public:
    ActionEstimate(double probability, double benefit, double cost)
        : probability_(nonnegative(probability)), benefit_(finite(benefit)),
          cost_(nonnegative(cost)) {
        if (probability_ > 1.0) throw std::invalid_argument("Probability exceeds one");
    }
    double expected_utility() const {
        // Failure benefit is zero; utility cost is incurred either way.
        return finite(probability_ * benefit_ - cost_);
    }
};

struct RegulatorySignal {
    bool differentiation_permitted = true;
    double tissue_bias = 0.0;
    double person_bias = 0.0;
};

struct Decision {
    CellAction action;
    double selected_utility;
    std::string reason;
};

class Governor {
public:
    Decision choose(const TransitionProposal& proposal, const ActionEstimate& estimate,
                    const RegulatorySignal& signal, double energy,
                    double remain_utility, CellState state) const {
        nonnegative(energy);
        finite(remain_utility);
        finite(signal.tissue_bias);
        finite(signal.person_bias);
        if (!signal.differentiation_permitted)
            return {CellAction::Remain, remain_utility, "Higher-level permission withheld"};
        if (state != CellState::Undifferentiated)
            return {CellAction::Remain, remain_utility, "Already differentiated"};
        if (proposal.energy_required() > energy)
            return {CellAction::Remain, remain_utility, "Insufficient available energy"};
        const double score = finite(estimate.expected_utility() + signal.tissue_bias
                                   + signal.person_bias);
        if (score <= remain_utility)
            return {CellAction::Remain, remain_utility, "Remaining is at least as valuable"};
        return {CellAction::Differentiate, score, "Feasible and preferred"};
    }
};

class Cell {
    MolecularCollection contents_;
    CellState state_ = CellState::Undifferentiated;
    double available_energy_;
    double transition_energy_ = 0.0;
    Governor governor_;
    std::vector<Decision> history_;
    std::optional<electric::Membrane> membrane_;
public:
    explicit Cell(double energy = 5.0) : available_energy_(nonnegative(energy)) {}
    void add_molecule(const Molecule& molecule) { contents_.add(molecule); }
    std::size_t molecule_count() const { return contents_.size(); }
    bool transfer_molecule_to(Cell& destination) {
        return contents_.transfer_last_to(destination.contents_);
    }
    CellState state() const { return state_; }
    double available_energy() const { return available_energy_; }
    double transition_energy() const { return transition_energy_; }
    const std::vector<Decision>& history() const { return history_; }
    void attach_membrane(electric::Membrane membrane) { membrane_=std::move(membrane); }
    bool has_membrane() const { return membrane_.has_value(); }
    electric::Membrane& membrane() {
        if (!membrane_) throw std::logic_error("Cell has no electrical membrane model");
        return *membrane_;
    }
    const electric::Membrane& membrane() const {
        if (!membrane_) throw std::logic_error("Cell has no electrical membrane model");
        return *membrane_;
    }

    Decision deliberate_and_execute(const TransitionProposal& proposal,
                                   const ActionEstimate& estimate,
                                   const RegulatorySignal& current_signal,
                                   double remain_utility) {
        // Deliberation and execution are separate stages in one synchronous call.
        // No externally constructed or stale Decision authorizes a transition.
        const Decision decision = governor_.choose(proposal, estimate, current_signal,
                                                   available_energy_, remain_utility, state_);
        history_.push_back(decision);
        if (decision.action == CellAction::Differentiate) {
            available_energy_ -= proposal.energy_required();
            transition_energy_ += proposal.energy_required();
            state_ = CellState::Differentiated;
        }
        return decision;
    }
};

// A finite abstract simplicial complex. Each stored simplex includes all faces.
// Vertex IDs index cells in a Tissue. Edges model adjacency; triangles are only
// explicitly declared three-way groups, never inferred from three pairwise edges.
class SimplicialComplex {
    std::size_t vertex_count_;
    std::set<std::vector<std::size_t>> simplices_;
    void insert_faces(const std::vector<std::size_t>& simplex) {
        if (!simplices_.insert(simplex).second) return;
        for (std::size_t i = 0; i < simplex.size(); ++i) {
            auto face = simplex;
            face.erase(face.begin() + static_cast<std::ptrdiff_t>(i));
            insert_faces(face);
        }
    }
public:
    explicit SimplicialComplex(std::size_t vertices) : vertex_count_(vertices) {
        simplices_.insert(std::vector<std::size_t>{}); // Empty face.
        for (std::size_t i = 0; i < vertices; ++i) simplices_.insert({i});
    }
    void add_simplex(std::vector<std::size_t> simplex) {
        std::sort(simplex.begin(), simplex.end());
        if (std::adjacent_find(simplex.begin(), simplex.end()) != simplex.end())
            throw std::invalid_argument("A simplex cannot repeat a vertex");
        for (auto vertex : simplex)
            if (vertex >= vertex_count_) throw std::out_of_range("Unknown cell vertex");
        // Keep this teaching implementation small: vertices, edges, triangles.
        if (simplex.size() > 3) throw std::invalid_argument("Only up to triangles supported");
        insert_faces(simplex);
    }
    std::size_t count(std::size_t dimension) const {
        return static_cast<std::size_t>(std::count_if(simplices_.begin(), simplices_.end(),
            [dimension](const auto& s) { return !s.empty() && s.size() - 1 == dimension; }));
    }
    std::vector<std::size_t> neighbors(std::size_t vertex) const {
        if (vertex >= vertex_count_) throw std::out_of_range("Unknown cell vertex");
        std::vector<std::size_t> result;
        for (const auto& s : simplices_)
            if (s.size() == 2) {
                if (s[0] == vertex) result.push_back(s[1]);
                if (s[1] == vertex) result.push_back(s[0]);
            }
        return result;
    }
};

class Tissue {
    std::vector<Cell> cells_;
    // Separate contact topology from the containment hierarchy.
    SimplicialComplex contacts_;
    bool permits_ = true;
    double bias_ = 0.0;
public:
    explicit Tissue(std::vector<Cell> cells)
        : cells_(std::move(cells)), contacts_(cells_.size()) {}
    std::size_t cell_count() const { return cells_.size(); }
    std::size_t molecule_count() const {
        std::size_t total = 0;
        for (const auto& cell : cells_) total += cell.molecule_count();
        return total;
    }
    Cell& cell(std::size_t index) { return cells_.at(index); }
    const Cell& cell(std::size_t index) const { return cells_.at(index); }
    void connect(std::size_t a, std::size_t b) { contacts_.add_simplex({a, b}); }
    void add_cooperative_group(std::array<std::size_t, 3> group) {
        contacts_.add_simplex({group[0], group[1], group[2]});
    }
    const SimplicialComplex& contacts() const { return contacts_; }
    void set_policy(bool permit, double bias) { bias_ = finite(bias); permits_ = permit; }
    RegulatorySignal signal(bool person_permits, double person_bias) const {
        return {permits_ && person_permits, bias_, finite(person_bias)};
    }
};

enum class OrganKind { Heart, Liver, Brain, Lungs, Skin, Mouth };

class Organ {
    std::string name_;
    OrganKind kind_;
    std::vector<Tissue> tissues_;
public:
    Organ(std::string name, OrganKind kind) : name_(std::move(name)), kind_(kind) {}
    void add_tissue(const Tissue& tissue) { tissues_.push_back(tissue); }
    Tissue& tissue(std::size_t index) { return tissues_.at(index); }
    const Tissue& tissue(std::size_t index) const { return tissues_.at(index); }
    OrganKind kind() const { return kind_; }
    const std::string& name() const { return name_; }
    std::size_t tissue_count() const { return tissues_.size(); }
    std::size_t molecule_count() const {
        std::size_t total = 0;
        for (const auto& tissue : tissues_) total += tissue.molecule_count();
        return total;
    }
};

// A physical Brain is an owned organ, distinct from the cognitive mind::Brain.
// Composition keeps the typed role without slicing a derived Organ object.
class Brain {
    Organ organ_{"Brain",OrganKind::Brain};
public:
    void add_tissue(const Tissue& tissue) { organ_.add_tissue(tissue); }
    Tissue& tissue(std::size_t index) { return organ_.tissue(index); }
    const Tissue& tissue(std::size_t index) const { return organ_.tissue(index); }
    std::size_t tissue_count() const { return organ_.tissue_count(); }
    std::size_t molecule_count() const { return organ_.molecule_count(); }
};

class Body {
    std::optional<Brain> brain_;
    std::vector<Organ> organs_;
    electric::NervousSystem nervous_system_;
    double electrical_time_ms_=0;
public:
    void add_organ(const Organ& organ) {
        if (organ.kind()==OrganKind::Brain)
            throw std::invalid_argument("Add the typed Brain with add_brain()");
        organs_.push_back(organ);
    }
    void add_brain(Brain brain) {
        if (brain_) throw std::logic_error("Body already owns a Brain");
        brain_=std::move(brain);
    }
    const Brain& brain() const {
        if (!brain_) throw std::logic_error("Body has no Brain model");
        return *brain_;
    }
    std::size_t organ_count() const { return organs_.size()+(brain_?1:0); }
    Organ& organ(std::size_t index) { return organs_.at(index); }
    const Organ& organ(std::size_t index) const { return organs_.at(index); }
    bool has_organ(OrganKind kind) const {
        if (kind==OrganKind::Brain) return brain_.has_value();
        return std::any_of(organs_.begin(), organs_.end(),
                           [kind](const Organ& o) { return o.kind() == kind; });
    }
    std::size_t molecule_count() const {
        std::size_t total = brain_?brain_->molecule_count():0;
        for (const auto& organ : organs_) total += organ.molecule_count();
        return total;
    }
    Cell& cell(electric::CellId id) {
        if (id.in_brain) {
            if (!brain_ || id.organ_index!=0) throw std::out_of_range("Unknown Brain cell address");
            return brain_->tissue(id.tissue_index).cell(id.cell_index);
        }
        return organs_.at(id.organ_index).tissue(id.tissue_index).cell(id.cell_index);
    }
    const Cell& cell(electric::CellId id) const {
        if (id.in_brain) {
            if (!brain_ || id.organ_index!=0) throw std::out_of_range("Unknown Brain cell address");
            return brain_->tissue(id.tissue_index).cell(id.cell_index);
        }
        return organs_.at(id.organ_index).tissue(id.tissue_index).cell(id.cell_index);
    }
    std::vector<electric::CellId> electrical_cells() const {
        std::vector<electric::CellId> result;
        if (brain_) for (std::size_t t=0;t<brain_->tissue_count();++t)
            for (std::size_t c=0;c<brain_->tissue(t).cell_count();++c)
                if (brain_->tissue(t).cell(c).has_membrane()) result.push_back(electric::CellId::brain(t,c));
        for (std::size_t o=0;o<organs_.size();++o)
            for (std::size_t t=0;t<organs_[o].tissue_count();++t)
                for (std::size_t c=0;c<organs_[o].tissue(t).cell_count();++c)
                    if (organs_[o].tissue(t).cell(c).has_membrane())
                        result.push_back(electric::CellId::organ(o,t,c));
        return result;
    }
    const electric::NervousSystem& nervous_system() const { return nervous_system_; }
    double electrical_time_ms() const { return electrical_time_ms_; }
    void connect(electric::CellId from,electric::CellId to,electric::SynapseParameters parameters={}) {
        if (!cell(from).membrane().can_spike())
            throw std::invalid_argument("Presynaptic cell must have a spiking membrane");
        cell(to).membrane(); // Validate recipient before modifying topology.
        nervous_system_.connect(from,to,parameters);
    }
    void advance_electrical(double duration_ms,const std::vector<electric::CurrentInput>& currents={},
                            double max_step_ms=0.05) {
        nonnegative(duration_ms);electric::detail::positive(max_step_ms);
        for (const auto& input:currents) {
            finite(input.inward_pa);cell(input.target).membrane();
        }
        for (const auto& synapse:nervous_system_.synapses()) {
            if (!cell(synapse.source).membrane().can_spike())
                throw std::logic_error("Presynaptic model was changed after connection");
            cell(synapse.target).membrane();
        }
        const double count=std::ceil(duration_ms/max_step_ms);
        if (!std::isfinite(count) || count>10000000) throw std::invalid_argument("Too many electrical steps");
        if (count==0) return;
        const double end_time=finite(electrical_time_ms_+duration_ms);
        const double start_time=electrical_time_ms_,dt=duration_ms/count;
        const auto ids=electrical_cells();
        for (std::size_t step=0;step<static_cast<std::size_t>(count);++step) {
            const double now=start_time+step*dt;
            const auto inputs=nervous_system_.interval_inputs(now,dt);
            std::vector<electric::Spike> firing;
            for (const auto id:ids) {
                double current=0;
                for (const auto& input:currents) if (input.target==id) current=finite(current+input.inward_pa);
                std::vector<electric::Conductance> channels;
                for (const auto& input:inputs) if (input.target==id) channels.push_back(input.channel);
                for (double offset:cell(id).membrane().advance_events(dt,current,channels))
                    firing.push_back({id,now+offset});
            }
            // Queue spikes only after every cell used the same interval inputs.
            std::stable_sort(firing.begin(),firing.end(),[](const auto& a,const auto& b){ return a.time_ms<b.time_ms; });
            for (const auto& spike:firing) nervous_system_.record_spike(spike.source,spike.time_ms);
        }
        electrical_time_ms_=end_time;
    }
};

class Person {
    bool permits_ = true;
    double bias_ = 0.0;
public:
    virtual ~Person() = default;
    virtual std::string describe_role() const = 0;
    void set_governance(bool permits, double bias) { bias_ = finite(bias); permits_ = permits; }
    bool permits_differentiation() const { return permits_; }
    double differentiation_bias() const { return bias_; }
};

struct Tool { double cost; double hours_saved; };

class HomoTechnicus : public Person {
public:
    std::string describe_role() const override { return "A maker and user of tools"; }
    Tool make_tool(double cost, double hours_saved) const {
        return {nonnegative(cost), nonnegative(hours_saved)};
    }
};

class HomoEconomicus : public Person {
    double value_of_time_;
public:
    explicit HomoEconomicus(double value) : value_of_time_(nonnegative(value)) {}
    std::string describe_role() const override { return "A chooser guided by subjective values"; }
    bool is_worthwhile(const Tool& tool) const {
        return finite(nonnegative(tool.hours_saved) * value_of_time_) >= nonnegative(tool.cost);
    }
};

class HomoSapiens : public Person {
    std::string name_;
    Body body_;
public:
    explicit HomoSapiens(std::string name) : name_(std::move(name)) {}
    std::string describe_role() const override { return "A human being"; }
    const std::string& name() const { return name_; }
    void add_organ(const Organ& organ) { body_.add_organ(organ); }
    std::size_t molecule_count() const { return body_.molecule_count(); }
    bool has_organ(OrganKind kind) const { return body_.has_organ(kind); }
    Body& body() { return body_; }
    const Body& body() const { return body_; }
    const Tissue& tissue(std::size_t organ, std::size_t tissue) const {
        return body_.organ(organ).tissue(tissue);
    }
    Decision consider_transition(std::size_t organ_index, std::size_t tissue_index,
                                 std::size_t cell_index, const TransitionProposal& proposal,
                                 double regulatory_feature, double benefit, double cost,
                                 double remain_utility) {
        auto& tissue = body_.organ(organ_index).tissue(tissue_index);
        auto& cell = tissue.cell(cell_index);
        const auto signal = tissue.signal(permits_differentiation(), differentiation_bias());
        const double probability = TeachingForest{}.predict_success(
            {cell.available_energy(), regulatory_feature});
        return cell.deliberate_and_execute(proposal, ActionEstimate(probability, benefit, cost),
                                           signal, remain_utility);
    }
};

} // namespace virtual_cell
