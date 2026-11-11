#include "relational_memory.hpp"
#include <iostream>

using namespace virtual_cell::mind;
void check(bool condition) { if (!condition) throw std::runtime_error("Memory check failed"); }
template<class F> void rejects(F f) {
    bool threw = false;
    try { f(); } catch (const std::exception&) { threw = true; }
    check(threw);
}
int main() {
    Memory m;
    auto root = m.create<Root>("root");
    auto other = m.create<Root>("other");
    auto one = m.create<One>("one", std::array<NodeId, 1>{other});
    auto two = m.create<Two>("two", std::array<NodeId, 2>{root, one});
    auto three = m.create<Three>("three", std::array<NodeId, 3>{root, one, two});
    check(m.at(root).elements().empty());
    check(m.at(one).elements().size() == 1 && m.at(two).elements().size() == 2 &&
          m.at(three).elements().size() == 3);
    m.include(root, one); m.include(other, root);
    check(m.reachable_count(root) == 3); // Cycle terminates safely.
    rejects([&] { m.create<Two>("duplicate", std::array<NodeId, 2>{root, root}); });
    rejects([&] { m.create<One>("unknown", std::array<NodeId, 1>{999}); });
    rejects([&] { m.include(one, root); });
    m.relate(root, other, Relation::LeadsTo);
    check(Route({root, other}).valid_in(m));
    check(!Route({other, root}).valid_in(m));
    rejects([] { Route empty({}); });
    ForecastRecord forecasts;
    check(!forecasts.brier_score());
    forecasts.observe(0.8, true); forecasts.observe(0.2, false);
    check(std::abs(*forecasts.brier_score() - 0.04) < 1e-12);
    rejects([&] { forecasts.observe(1.1, true); });
    Brain brain;
    brain.model_of("A").move_forecasts.observe(0.5, false);
    check(brain.model_of("B").move_forecasts.count() == 0);
    check(brain.self_model().own_move_forecasts.count() == 0);
    std::cout << "All relational-memory checks passed.\n";
}
