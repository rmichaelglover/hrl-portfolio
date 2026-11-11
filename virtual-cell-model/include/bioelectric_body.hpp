#pragma once
#include "virtual_cell.hpp"

namespace virtual_cell::electric {
inline Cell passive_cell(double capacitance_pf=100,double leak_ns=5,double reversal_mv=-65) {
    Cell cell;
    cell.attach_membrane(Membrane({capacitance_pf,leak_ns,reversal_mv},reversal_mv));
    return cell;
}
inline Cell neuron(double capacitance_pf=100,double leak_ns=5) {
    Cell cell;
    cell.attach_membrane(Membrane({capacitance_pf,leak_ns,-65},-65,SpikeRule{}));
    return cell;
}

// IDs are local coordinates in this example's owned Body, not external handles.
struct BodyExample {
    HomoSapiens person;
    CellId skin_sensor=CellId::organ(2,0,0);
    CellId sensory_brain=CellId::brain(0,0);
    CellId motor_brain=CellId::brain(0,1);
    CellId heart_target=CellId::organ(0,0,0);
    CellId lungs_target=CellId::organ(1,0,0);
    CellId skin_target=CellId::organ(2,0,1);
    CellId mouth_target=CellId::organ(3,0,0);
};
inline BodyExample make_body_example(std::string name="Bioelectric example",bool wired=true) {
    BodyExample example{HomoSapiens(std::move(name))};
    Brain brain;brain.add_tissue(Tissue({neuron(),neuron()}));
    auto& body=example.person.body();body.add_brain(std::move(brain));
    for (const auto& entry:std::vector<std::pair<std::string,OrganKind>>{
            {"Heart",OrganKind::Heart},{"Lungs",OrganKind::Lungs},
            {"Skin",OrganKind::Skin},{"Mouth",OrganKind::Mouth}}) {
        Organ organ(entry.first,entry.second);
        if (entry.second==OrganKind::Skin) organ.add_tissue(Tissue({neuron(50),passive_cell()}));
        else if (entry.second==OrganKind::Heart) organ.add_tissue(Tissue({passive_cell(150,5),passive_cell(150,5)}));
        else if (entry.second==OrganKind::Lungs) organ.add_tissue(Tissue({passive_cell(80,8),passive_cell(80,8)}));
        else organ.add_tissue(Tissue({passive_cell(100,6),passive_cell(100,6)}));
        body.add_organ(organ);
    }
    // Synthetic routing, not a human connectome or anatomical axon reconstruction.
    if (wired) {
        body.connect(example.skin_sensor,example.sensory_brain,{30,4,0,1});
        body.connect(example.sensory_brain,example.motor_brain,{30,4,0,2});
        for (const auto target:{example.heart_target,example.lungs_target,example.skin_target,example.mouth_target})
            body.connect(example.motor_brain,target,{3,5,0,2});
    }
    return example;
}
} // namespace virtual_cell::electric
