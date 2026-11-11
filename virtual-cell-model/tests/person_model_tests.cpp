#include "person_model.hpp"
#include <iostream>

using namespace virtual_cell::mind;
void check(bool condition) { if (!condition) throw std::runtime_error("Integrated model check failed"); }
template<class F> void rejects(F f) {
    bool threw = false;
    try { f(); } catch (const std::exception&) { threw = true; }
    check(threw);
}
int main() {
    CompatibilityField field({{0.6, 0.4}, {0.7, 0.3}});
    field.add({0, 0, 1, 0, 1}); field.add({1, 0, 0, 0, 1});
    auto result = field.run();
    check(result.converged && result.strengths[0][0] > 0.6 && result.strengths[1][0] > 0.7);
    for (const auto& row : result.strengths)
        check(std::abs(row[0] + row[1] - 1) < 1e-12);
    auto baseline = field.run(10, 0.5, 0);
    check(std::abs(baseline.strengths[0][0] - 0.6) < 1e-12);
    CompatibilityField arbitrary({{1, 0, 2, 3}});
    check(arbitrary.run().strengths[0].size() == 4);
    check(arbitrary.run().strengths[0][1] == 0);
    CompatibilityField inhibition({{0.6, 0.4}, {0.7, 0.3}});
    inhibition.add({0, 0, 1, 0, -1});
    check(inhibition.run().strengths[0][0] < 0.6);
    check(!field.run(1, 0.5, 1, 0).converged);
    rejects([] { CompatibilityField bad({{0, 0}}); });
    rejects([&] { field.add({9, 0, 0, 0, 1}); });
    rejects([&] { field.run(0); });

    PersonModel person("Alex", 3, {1, 1, 1, 1, 1});
    auto context = person.add_context("experience");
    person.bind_name("a", context); person.bind_name("b", context);
    check(person.resolve("a") == person.resolve("b") && !person.resolve("unknown"));
    rejects([&] { person.bind_name("a", person.context()); });
    std::vector<Candidate> actions{{"feasible", ObjectiveVector({1, 2, 3, 4, 5}), 2, true},
                                 {"too costly", ObjectiveVector({9, 9, 9, 9, 9}), 4, true}};
    check(person.choose(actions) == 0);
    check(person.execute(actions[0]));
    check(person.available_action_energy() == 1 && person.spent_action_energy() == 2);
    check(!person.execute(actions[0]));
    check(person.spent_action_energy() == 2);
    person.observe(context, "feasible", actions[0].outcomes, ObjectiveVector({1, 2, 3, 2, 5}),
                   0.8, false, "test fixture");
    check(person.experiences().size() == 1);
    check(person.mean_prediction_error().at(Objective::Learning) == 2);
    const auto summary = person.summary(person.context());
    check(summary.observation_count == 1);
    check(std::abs(*summary.mean_surprisal + std::log(0.2)) < 1e-12);
    check(std::abs(*person.brain().self_model().own_move_forecasts.brier_score() - 0.64) < 1e-12);
    rejects([&] { person.observe(context, "bad", actions[0].outcomes, actions[0].outcomes,
                                2.0, true, "invalid probability"); });
    check(person.experiences().size() == 1);
    std::cout << "All integrated model checks passed.\n";
}
