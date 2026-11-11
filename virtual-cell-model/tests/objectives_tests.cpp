#include "hierarchical_summary.hpp"
#include <iostream>

using namespace virtual_cell::mind;
void check(bool condition) { if (!condition) throw std::runtime_error("Objective check failed"); }
template<class F> void rejects(F f) {
    bool threw = false;
    try { f(); } catch (const std::exception&) { threw = true; }
    check(threw);
}
int main() {
    const ObjectiveVector a({1, 2, 3, 4, 5}), b({0, 1, 2, 3, 4});
    check(a.dominates(b) && !a.dominates(a));
    check(!a.dominates(ObjectiveVector({2, 1, 3, 4, 5})));
    MultiObjectiveGovernor governor({1, 1, 1, 1, 1});
    std::vector<Candidate> choices{{"a", a, 2, true}, {"b", b, 1, true},
                                 {"forbidden", ObjectiveVector({9, 9, 9, 9, 9}), 1, false}};
    check(governor.frontier(choices, 2) == std::vector<std::size_t>{0});
    check(governor.choose(choices, 2) == 0);
    check(!governor.choose(choices, 0));
    rejects([] { MultiObjectiveGovernor bad({0, 0, 0, 0, 0}); });
    rejects([] { MultiObjectiveGovernor bad({-1, 1, 1, 1, 1}); });
    check(surprisal(1) == 0 && std::isinf(surprisal(0)));
    rejects([] { surprisal(1.1); });

    Memory memory;
    auto root = memory.create<Root>("root");
    auto left = memory.create<Root>("left"), right = memory.create<Root>("right");
    auto shared = memory.create<Root>("shared");
    memory.include(root, left); memory.include(root, right);
    memory.include(left, shared); memory.include(right, shared); memory.include(shared, root);
    SummaryStore store;
    check(!store.summarize(memory, root).mean_surprisal);
    store.record(memory, left, {b, 1, "omitted detail"});
    store.record(memory, shared, {a, 0.5, ""});
    auto summary = store.summarize(memory, root);
    check(summary.visited_nodes == 4 && summary.observation_count == 2);
    check(summary.mean_outcomes.at(Objective::Health) == 0.5);
    check(summary.population_standard_deviation.at(Objective::Health) == 0.5);
    check(std::abs(*summary.mean_surprisal - std::log(2) / 2) < 1e-12);
    check(summary.omissions.size() == 1);
    store.record(memory, root, {a, 0, ""});
    check(std::isinf(*store.summarize(memory, root).mean_surprisal));
    rejects([&] { store.record(memory, 999, {a, 1, ""}); });
    std::cout << "All objective and summary checks passed.\n";
}
