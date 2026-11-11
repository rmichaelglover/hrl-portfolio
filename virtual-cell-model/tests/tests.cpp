#include "virtual_cell.hpp"
#include <iostream>
#include <limits>

using namespace virtual_cell;

void check(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
template<class Function> void rejects(Function function) {
    bool threw = false;
    try { function(); } catch (const std::exception&) { threw = true; }
    check(threw, "Expected rejection");
}

int main() {
    const Molecule glycine("glycine", {2, 5, 1, 2});
    Cell a, b;
    a.add_molecule(glycine);
    a.add_molecule(glycine);
    check(a.transfer_molecule_to(b), "Transfer succeeds");
    check(a.molecule_count() == 1 && b.molecule_count() == 1, "Transfer conserves count");
    check(!a.transfer_molecule_to(a), "Self transfer rejected");
    Cell empty;
    check(!empty.transfer_molecule_to(a), "Empty transfer rejected");
    Tissue tissue({a, b, empty});
    a.add_molecule(glycine);
    check(tissue.molecule_count() == 2, "Stored cells are independent copies");

    tissue.connect(0, 1); tissue.connect(1, 2); tissue.connect(0, 2);
    check(tissue.contacts().count(2) == 0, "Edges do not imply a triangle");
    tissue.add_cooperative_group({2, 0, 1});
    tissue.add_cooperative_group({0, 1, 2});
    check(tissue.contacts().count(0) == 3 && tissue.contacts().count(1) == 3 &&
          tissue.contacts().count(2) == 1, "Face closure and duplicate handling");
    check(tissue.contacts().neighbors(0).size() == 2, "Contact neighbors");
    rejects([&] { tissue.connect(0, 3); });
    rejects([&] { tissue.connect(1, 1); });

    const TransitionProposal proposal(3.0);
    const ActionEstimate estimate(0.7, 10.0, 2.0);
    const Governor governor;
    auto decide = [&](RegulatorySignal signal, double energy, double remain) {
        return governor.choose(proposal, estimate, signal, energy, remain,
                               CellState::Undifferentiated).action;
    };
    check(decide({false, 100, 100}, 5, 1) == CellAction::Remain, "Permission is a hard gate");
    check(decide({true, 100, 100}, 2, 1) == CellAction::Remain, "Energy is a hard gate");
    check(decide({true, 0, 0}, 5, 5) == CellAction::Remain, "Ties remain");
    check(decide({true, -2, 4}, 5, 6) == CellAction::Differentiate, "Cascading biases");

    Cell changing(5);
    auto decision = changing.deliberate_and_execute(proposal, estimate, {true, -2, 4}, 6);
    check(decision.action == CellAction::Differentiate && changing.available_energy() == 2 &&
          changing.transition_energy() == 3 && changing.state() == CellState::Differentiated,
          "Execution updates state and energy ledger");
    changing.deliberate_and_execute(proposal, estimate, {true, 100, 100}, 0);
    check(changing.available_energy() == 2 && changing.history().size() == 2,
          "Repeated differentiation does not spend energy");

    Organ heart("heart", OrganKind::Heart); heart.add_tissue(tissue);
    HomoSapiens human("Alex"); human.add_organ(heart);
    human.set_governance(false, 100);
    check(human.has_organ(OrganKind::Heart) && human.molecule_count() == 2, "Hierarchy");
    check(human.consider_transition(0, 0, 0, proposal, 0.7, 10, 2, 0).action ==
          CellAction::Remain, "Person permission propagates through tissue");
    check(human.tissue(0, 0).cell(0).available_energy() == 5, "Rejected action costs nothing");

    rejects([] { TransitionProposal bad(-1); });
    rejects([] { ActionEstimate bad(1.1, 10, 2); });
    rejects([] { Cell bad(std::numeric_limits<double>::quiet_NaN()); });
    rejects([] { TeachingForest{}.predict_success({5, std::numeric_limits<double>::infinity()}); });
    check(std::abs(TeachingForest{}.predict_success({5, 0.7}) - 0.7) < 1e-12,
          "Teaching forest average");
    std::cout << "All virtual-cell checks passed.\n";
}
