#include "person_model.hpp"
#include <iostream>

using namespace virtual_cell;
using namespace virtual_cell::mind;

int main() {
    PersonModel alex("Alex", 5, {1, 1, 1, 1, 1});
    const Molecule glycine("glycine", {2, 5, 1, 2});
    Cell cell; cell.add_molecule(glycine);
    Tissue tissue({cell, cell, cell});
    tissue.add_cooperative_group({0, 1, 2});
    Organ heart("Alex's modeled heart", OrganKind::Heart);
    heart.add_tissue(tissue); alex.human().add_organ(heart);

    const auto chess = alex.add_context("Chess experiences");
    const auto mate = alex.add_context("Queen and rook mate against carla227");
    alex.bind_name("queen-rook mate", mate);
    alex.bind_name("UYo057a7 finish", mate);
    alex.brain().memory().include(chess, mate);
    std::cout << alex.human().name() << ": " << alex.human().molecule_count()
              << " represented molecules; two names resolve to one memory: " << std::boolalpha
              << (alex.resolve("queen-rook mate") == alex.resolve("UYo057a7 finish")) << '\n';

    // Arbitrary categorical role labels: cooperating attacker / other role.
    // The support is handcrafted illustrative evidence, not a chess engine evaluation.
    CompatibilityField field({{0.6, 0.4}, {0.7, 0.3}});
    field.add({0, 0, 1, 0, 1.0}); field.add({1, 0, 0, 0, 1.0});
    const auto inferred = field.run();
    std::cout << "Cooperation label strengths: " << inferred.strengths[0][0]
              << ", " << inferred.strengths[1][0]
              << "; converged: " << inferred.converged << '\n';
    // Temporal carryover is explicit. Reusing this is memory, not fresh evidence.
    const auto remembered = CompatibilityField(inferred.strengths).run();
    std::cout << "Retained strength without new relations: " << remembered.strengths[0][0] << '\n';

    const std::vector<Candidate> actions{
        {"Review mating coordination", ObjectiveVector({5, 5, 4, 9, 4}), 2, true},
        {"Play another game", ObjectiveVector({5, 4, 6, 5, 4}), 2, true},
        {"Unaffordable session", ObjectiveVector({9, 9, 9, 9, 9}), 8, true}
    };
    const auto selected = alex.choose(actions);
    if (!selected || !alex.execute(actions[*selected])) return 1;
    const auto& action = actions[*selected];
    // Scores and probabilities below are illustrative, not reported by the PGN.
    alex.observe(chess, action.name, action.outcomes, ObjectiveVector({5, 5, 4, 7, 4}),
                 0.8, true, "Teaching scenario; mating motif from Rancid Randi",
                 "No clock-pressure or subjective-experience measurements");
    const auto summary = alex.summary(alex.context());
    std::cout << "Selected: " << action.name << "; remaining action energy: "
              << alex.available_action_energy() << '\n';
    std::cout << "Summary observations: " << summary.observation_count
              << "; learning prediction absolute error: "
              << alex.mean_prediction_error().at(Objective::Learning) << '\n';
    std::cout << "Brier score: " << *alex.brain().self_model().own_move_forecasts.brier_score()
              << "; observed-event surprisal: " << *summary.mean_surprisal << '\n';
}
