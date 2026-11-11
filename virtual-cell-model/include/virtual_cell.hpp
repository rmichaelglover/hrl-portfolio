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

enum class OrganKind { Heart, Liver };

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
    std::size_t molecule_count() const {
        std::size_t total = 0;
        for (const auto& tissue : tissues_) total += tissue.molecule_count();
        return total;
    }
};

class Body {
    std::vector<Organ> organs_;
public:
    void add_organ(const Organ& organ) { organs_.push_back(organ); }
    Organ& organ(std::size_t index) { return organs_.at(index); }
    const Organ& organ(std::size_t index) const { return organs_.at(index); }
    bool has_organ(OrganKind kind) const {
        return std::any_of(organs_.begin(), organs_.end(),
                           [kind](const Organ& o) { return o.kind() == kind; });
    }
    std::size_t molecule_count() const {
        std::size_t total = 0;
        for (const auto& organ : organs_) total += organ.molecule_count();
        return total;
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
