#pragma once

#include "hierarchical_summary.hpp"
#include "compatibility.hpp"
#include "biochemistry.hpp"
#include "observer.hpp"
#include "inference_evidence.hpp"
#include "reflective_practice.hpp"

namespace virtual_cell::mind {

struct Experience {
    NodeId context;
    std::string action;
    ObjectiveVector predicted;
    ObjectiveVector observed;
    double predicted_success;
    bool success;
    std::string provenance;
};
struct Percept {
    BoundaryObservation observed;
    double probability_external;
    std::string feature;
    double integrated_value;
};

// Coordinates existing components without changing their inheritance contracts.
// Resource budgets here concern decisions; cellular energy remains in the body.
class PersonModel {
    HomoSapiens human_;
    Brain brain_;
    SummaryStore summaries_;
    MultiObjectiveGovernor governor_;
    NodeId context_;
    double action_energy_;
    double spent_energy_ = 0;
    std::map<std::string, NodeId> names_;
    std::vector<Experience> experiences_;
    std::optional<bio::LithiumPhysiology> physiology_;
    BoundaryObserver boundary_observer_;
    ReflectivePractice reflection_;
    AttendedSelfModel attended_self_;
    std::vector<Percept> percepts_;
public:
    PersonModel(std::string name, double action_energy,
                std::array<double, objective_count> weights)
        : human_(std::move(name)), governor_(weights), action_energy_(nonnegative(action_energy)) {
        context_ = brain_.memory().create<Root>("Person's modeled context");
    }
    ReflectivePractice& reflection() {return reflection_;}
    const ReflectivePractice& reflection() const {return reflection_;}
    HomoSapiens& human() { return human_; }
    const HomoSapiens& human() const { return human_; }
    Brain& brain() { return brain_; }
    const Brain& brain() const { return brain_; }
    NodeId context() const { return context_; }
    double available_action_energy() const { return action_energy_; }
    double spent_action_energy() const { return spent_energy_; }
    const std::vector<Experience>& experiences() const { return experiences_; }
    Will& will() { return human_.will(); }
    const Will& will() const { return human_.will(); }
    BoundaryEvidence boundary_evidence(BoundaryObservation observation,
                                       std::string provenance) const {
        return EvidenceEncoder(boundary_observer_).encode(observation,std::move(provenance));
    }
    void configure_boundary_observer(BoundaryObserver observer) { boundary_observer_=std::move(observer); }
    const AttendedSelfModel& attended_self() const { return attended_self_; }
    const std::vector<Percept>& percepts() const { return percepts_; }
    void retire_representation(const std::string& feature) { attended_self_.retire(feature); }
    Percept perceive(BoundaryObservation observation,std::string feature="visual_activity") {
        const double probability=boundary_observer_.probability_external(observation);
        const double visual=static_cast<double>(observation.visual_events);
        const double sensed=visual/(1+visual);
        attended_self_.integrate(feature,probability*sensed,will());
        Percept percept{observation,probability,std::move(feature),0};
        percept.integrated_value=attended_self_.feature(percept.feature);
        percepts_.push_back(percept);
        return percept;
    }
    void attach_physiology(bio::LithiumPhysiology physiology) {
        physiology_=std::move(physiology);
    }
    bool has_physiology() const { return physiology_.has_value(); }
    const bio::LithiumPhysiology& physiology() const {
        if (!physiology_) throw std::logic_error("No physiology attached");
        return *physiology_;
    }
    void advance_physiology(bio::Seconds duration,bio::Seconds step=bio::Seconds(0.01)) {
        if (!physiology_) throw std::logic_error("No physiology attached");
        physiology_->advance(duration,step);
    }

    NodeId add_context(std::string name) {
        auto id = brain_.memory().create<Root>(std::move(name));
        brain_.memory().include(context_, id);
        return id;
    }
    void bind_name(std::string name, NodeId referent) {
        brain_.memory().at(referent);
        const auto found = names_.find(name);
        if (found != names_.end() && found->second != referent)
            throw std::invalid_argument("Name already bound to another referent");
        names_.insert_or_assign(std::move(name), referent);
    }
    std::optional<NodeId> resolve(const std::string& name) const {
        const auto found = names_.find(name);
        if (found == names_.end()) return std::nullopt;
        return found->second;
    }
    Summary summary(NodeId root) const { return summaries_.summarize(brain_.memory(), root); }

    std::optional<std::size_t> choose(const std::vector<Candidate>& candidates) const {
        return governor_.choose(candidates, action_energy_);
    }
    std::vector<std::size_t> frontier(const std::vector<Candidate>& candidates) const {
        return governor_.frontier(candidates, action_energy_);
    }
    // An explicit behavioral action budget, not a biochemical reaction simulator.
    bool execute(const Candidate& current_action) {
        nonnegative(current_action.energy_required);
        if (!current_action.permitted || current_action.energy_required > action_energy_) return false;
        const double new_spent = finite(spent_energy_ + current_action.energy_required);
        action_energy_ -= current_action.energy_required;
        spent_energy_ = new_spent;
        return true;
    }
    void observe(NodeId context, std::string action, const ObjectiveVector& predicted,
                 const ObjectiveVector& observed, double probability, bool success,
                 std::string provenance, std::string omissions = {}) {
        brain_.memory().at(context);
        surprisal(probability); // Validate probability before modifying records.
        const double realized_probability = success ? probability : 1.0 - probability;
        summaries_.record(brain_.memory(), context, {observed, realized_probability, std::move(omissions)});
        brain_.self_model().own_move_forecasts.observe(probability, success);
        experiences_.push_back({context, std::move(action), predicted, observed,
                                probability, success, std::move(provenance)});
    }
    ObjectiveVector mean_prediction_error() const {
        std::array<double, objective_count> errors{};
        std::size_t n = 0;
        for (const auto& experience : experiences_) {
            ++n;
            for (std::size_t i = 0; i < objective_count; ++i) {
                const double error = std::abs(finite(experience.predicted.values()[i]
                                                   - experience.observed.values()[i]));
                errors[i] = finite(errors[i] + (error - errors[i]) / static_cast<double>(n));
            }
        }
        return ObjectiveVector(errors); // Check experiences().empty() before interpretation.
    }
};

} // namespace virtual_cell::mind
