#include "virtual_cell.hpp"
#include <iostream>

using namespace virtual_cell;

int main() {
    std::cout << "Virtual Cell — in honor of James Calvin (Jimmy) Glover\n";
    const Molecule glycine("glycine", {2, 5, 1, 2});
    Cell seed(5.0);
    seed.add_molecule(glycine);

    Tissue tissue({seed, seed, seed});
    tissue.connect(0, 1);
    tissue.connect(1, 2);
    tissue.connect(0, 2);
    std::cout << "Pairwise contacts: " << tissue.contacts().count(1)
              << "; three-cell groups: " << tissue.contacts().count(2) << '\n';
    tissue.add_cooperative_group({0, 1, 2});
    std::cout << "Explicit three-cell groups: " << tissue.contacts().count(2) << '\n';
    tissue.set_policy(true, -2.0);

    // Organ names identify containers; physiology is not implemented yet.
    Organ organ("Alex's modeled heart", OrganKind::Heart);
    organ.add_tissue(tissue);
    HomoSapiens human("Alex");
    human.add_organ(organ);
    human.set_governance(true, 4.0);

    std::cout << human.name() << ": " << human.molecule_count() << " modeled molecules\n";
    const auto decision = human.consider_transition(0, 0, 0, TransitionProposal(3.0),
                                                   0.7, 10.0, 2.0, 6.0);
    const auto& cell = human.tissue(0, 0).cell(0);
    std::cout << "Decision: "
              << (decision.action == CellAction::Differentiate ? "Differentiate" : "Remain")
              << "; utility: " << decision.selected_utility
              << "; reason: " << decision.reason << '\n';
    std::cout << "Energy available: " << cell.available_energy()
              << "; allocated to transition: " << cell.transition_energy() << '\n';
    std::cout << "Original seed energy: " << seed.available_energy()
              << " (composition stored independent copies)\n";

    HomoTechnicus maker;
    HomoEconomicus chooser(15.0);
    const auto tool = maker.make_tool(20.0, 2.0);
    std::cout << std::boolalpha << "Tool worthwhile: " << chooser.is_worthwhile(tool) << '\n';
}
