#pragma once

#include "relational_memory.hpp"
#include "objectives.hpp"

namespace virtual_cell::mind {

struct Observation {
    ObjectiveVector outcomes;
    // Event probability assigned before observing it; used for surprisal, not utility.
    double predicted_probability;
    std::string omitted_details;
};

struct Summary {
    std::size_t observation_count = 0;
    ObjectiveVector mean_outcomes;
    std::optional<double> mean_surprisal;
    std::size_t zero_probability_events = 0;
    std::size_t visited_nodes = 0;
    // Dispersion of observed scores, not a confidence interval for future outcomes.
    ObjectiveVector population_standard_deviation;
    std::vector<std::string> omissions;
};

class SummaryStore {
    std::map<NodeId, std::vector<Observation>> observations_;
public:
    void record(const Memory& memory, NodeId node, Observation observation) {
        memory.at(node);
        surprisal(observation.predicted_probability); // Validate before storing.
        observations_[node].push_back(std::move(observation));
    }
    Summary summarize(const Memory& memory, NodeId root) const {
        Summary result;
        std::set<NodeId> visited;
        std::vector<NodeId> pending{root};
        std::array<double, objective_count> mean{}, m2{};
        double surprise_mean = 0;
        while (!pending.empty()) {
            auto node = pending.back(); pending.pop_back();
            if (!visited.insert(node).second) continue;
            const auto children = memory.at(node).elements();
            pending.insert(pending.end(), children.begin(), children.end());
            const auto found = observations_.find(node);
            if (found == observations_.end()) continue;
            for (const auto& observation : found->second) {
                ++result.observation_count;
                const double n = static_cast<double>(result.observation_count);
                for (std::size_t i = 0; i < objective_count; ++i) {
                    const double value = observation.outcomes.values()[i];
                    const double delta = finite(value - mean[i]);
                    mean[i] = finite(mean[i] + delta / n);
                    m2[i] = finite(m2[i] + delta * (value - mean[i]));
                }
                const double surprise = surprisal(observation.predicted_probability);
                if (std::isinf(surprise)) ++result.zero_probability_events;
                else {
                    const auto finite_count = result.observation_count - result.zero_probability_events;
                    surprise_mean += (surprise - surprise_mean) / static_cast<double>(finite_count);
                }
                if (!observation.omitted_details.empty()) result.omissions.push_back(observation.omitted_details);
            }
        }
        result.visited_nodes = visited.size();
        result.mean_outcomes = ObjectiveVector(mean);
        if (result.observation_count) {
            result.mean_surprisal = result.zero_probability_events
                ? std::numeric_limits<double>::infinity() : surprise_mean;
            for (auto& value : m2)
                value = std::sqrt(std::max(0.0, value / static_cast<double>(result.observation_count)));
            result.population_standard_deviation = ObjectiveVector(m2);
        }
        return result;
    }
};

} // namespace virtual_cell::mind
