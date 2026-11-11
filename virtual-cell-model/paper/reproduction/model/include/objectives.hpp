#pragma once

#include "virtual_cell.hpp"
#include <optional>
#include <limits>

namespace virtual_cell::mind {

enum class Objective : std::size_t { Health, Security, Relationships, Learning, Resources, Count };
constexpr std::size_t objective_count = static_cast<std::size_t>(Objective::Count);

// Comparable, dimensionless scenario scores; higher is better in each dimension.
// These are explicit proxies, not measurements of love or intrinsic human worth.
class ObjectiveVector {
    std::array<double, objective_count> values_;
public:
    explicit ObjectiveVector(std::array<double, objective_count> values = {}) : values_(values) {
        for (double value : values_) finite(value);
    }
    double at(Objective objective) const { return values_.at(static_cast<std::size_t>(objective)); }
    const auto& values() const { return values_; }
    bool dominates(const ObjectiveVector& other) const {
        bool strictly_better = false;
        for (std::size_t i = 0; i < objective_count; ++i) {
            if (values_[i] < other.values_[i]) return false;
            strictly_better |= values_[i] > other.values_[i];
        }
        return strictly_better;
    }
};

inline double surprisal(double probability) {
    nonnegative(probability);
    if (probability > 1.0) throw std::invalid_argument("Probability exceeds one");
    // No silent clipping: an event assigned zero probability has infinite surprisal.
    return probability == 0 ? std::numeric_limits<double>::infinity() : -std::log(probability);
}

struct Candidate {
    std::string name;
    ObjectiveVector outcomes;
    double energy_required;
    bool permitted;
};

class MultiObjectiveGovernor {
    std::array<double, objective_count> weights_;
public:
    explicit MultiObjectiveGovernor(std::array<double, objective_count> weights) : weights_(weights) {
        double sum = 0;
        for (double weight : weights_) sum = finite(sum + nonnegative(weight));
        if (sum == 0) throw std::invalid_argument("At least one objective needs positive weight");
        for (auto& weight : weights_) weight /= sum;
    }
    std::vector<std::size_t> frontier(const std::vector<Candidate>& candidates, double energy) const {
        nonnegative(energy);
        std::vector<std::size_t> feasible, result;
        for (std::size_t i = 0; i < candidates.size(); ++i) {
            nonnegative(candidates[i].energy_required);
            if (candidates[i].permitted && candidates[i].energy_required <= energy) feasible.push_back(i);
        }
        for (auto i : feasible) {
            bool dominated = false;
            for (auto j : feasible)
                if (candidates[j].outcomes.dominates(candidates[i].outcomes)) dominated = true;
            if (!dominated) result.push_back(i);
        }
        return result;
    }
    double score(const ObjectiveVector& outcomes) const {
        double result = 0;
        for (std::size_t i = 0; i < objective_count; ++i)
            result = finite(result + weights_[i] * outcomes.values()[i]);
        return result;
    }
    std::optional<std::size_t> choose(const std::vector<Candidate>& candidates, double energy) const {
        std::optional<std::size_t> best;
        for (auto i : frontier(candidates, energy))
            if (!best || score(candidates[i].outcomes) > score(candidates[*best].outcomes)) best = i;
        return best; // Deterministic first-in-input tie break; empty means no feasible action.
    }
};

} // namespace virtual_cell::mind
