#include "hierarchical_summary.hpp"
#include <iostream>

using namespace virtual_cell::mind;

int main() {
    Brain brain;
    auto& memory = brain.memory();
    auto root = memory.create<Root>("Self-model context");
    auto work = memory.create<Root>("Work experiences");
    auto connection = memory.create<Root>("Connection experiences");
    memory.include(root, work); memory.include(root, connection);
    SummaryStore summaries;
    summaries.record(memory, work, {ObjectiveVector({3, 7, 2, 4, 9}), 0.8,
                                    "Illustrative scores; fatigue trajectory omitted"});
    summaries.record(memory, connection, {ObjectiveVector({7, 4, 9, 5, 3}), 0.5,
                                          "Illustrative scores; relationship history omitted"});
    const auto summary = summaries.summarize(memory, root);
    std::cout << "Root summarizes " << summary.observation_count << " observations across "
              << summary.visited_nodes << " nodes\n";
    std::cout << "Mean surprisal (nats): " << *summary.mean_surprisal << '\n';

    // Outcome proxies on a common illustrative 0–10 scale, not dollars or biology.
    const std::vector<Candidate> actions{
        {"Work overtime", ObjectiveVector({3, 7, 2, 4, 9}), 3, true},
        {"Share a meal", ObjectiveVector({7, 4, 9, 5, 3}), 2, true},
        {"Costly exhaustion", ObjectiveVector({2, 6, 1, 3, 8}), 3, true},
        {"Unavailable ideal", ObjectiveVector({10, 10, 10, 10, 10}), 20, true}
    };
    const MultiObjectiveGovernor balanced({1, 1, 1, 1, 1});
    const MultiObjectiveGovernor resources_only({0, 0, 0, 0, 1});
    std::cout << "Feasible Pareto frontier:\n";
    for (auto i : balanced.frontier(actions, 5)) std::cout << "  " << actions[i].name << '\n';
    std::cout << "Equal objective weights: " << actions[*balanced.choose(actions, 5)].name << '\n';
    std::cout << "Resources-only weights: " << actions[*resources_only.choose(actions, 5)].name << '\n';
    std::cout << "Choices describe actions; no body state has been changed.\n";
}
