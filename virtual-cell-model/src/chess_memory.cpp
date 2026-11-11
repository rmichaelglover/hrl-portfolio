#include "relational_memory.hpp"
#include <iostream>

using namespace virtual_cell::mind;

int main() {
    Brain brain;
    auto& memory = brain.memory();
    const auto self = memory.create<Root>("Player's modeled context");
    const auto opponent = memory.create<Root>("Model of carla227; not the person");
    memory.include(self, opponent);
    memory.relate(self, opponent, Relation::Models);

    const auto queen = memory.create<Root>("Black queen on g2");
    const auto rook = memory.create<Root>("Black rook on e2");
    const auto king = memory.create<Root>("White king on h2");
    const auto focus = memory.create<One>("Attention to queen", std::array<NodeId, 1>{queen});
    const auto support = memory.create<Two>("Rook supports queen", std::array<NodeId, 2>{rook, queen});
    const auto mate = memory.create<Three>("Mating group", std::array<NodeId, 3>{rook, queen, king});
    memory.relate(rook, queen, Relation::Supports);
    memory.relate(queen, king, Relation::Attacks);
    memory.include(self, focus); memory.include(self, support); memory.include(self, mate);

    // Historical route, not a proof of optimal play or a generated legal move tree.
    const auto p0 = memory.create<Root>("After 18...Qxf6");
    const auto p1 = memory.create<Root>("After 19.Rfd1");
    const auto p2 = memory.create<Root>("After 19...Qxf2");
    const auto p3 = memory.create<Root>("After 20.Rac1");
    const auto p4 = memory.create<Root>("After 20...Qxg2#: checkmate");
    memory.relate(p0, p1, Relation::LeadsTo);
    memory.relate(p1, p2, Relation::LeadsTo);
    memory.relate(p2, p3, Relation::LeadsTo);
    memory.relate(p3, p4, Relation::LeadsTo);
    const Route route({p0, p1, p2, p3, p4});
    std::cout << "Historical route valid: " << std::boolalpha << route.valid_in(memory) << '\n';
    for (auto id : route.steps()) std::cout << memory.at(id).name() << '\n';

    const auto stalemate = memory.create<Root>("olk: after 27.Qxf3, stalemate");
    memory.include(self, stalemate);
    std::cout << "Distinct outcome remembered: " << memory.at(stalemate).name() << '\n';

    // Illustrative forecasts only: these probabilities were not recorded in PGNs.
    brain.model_of("carla227").move_forecasts.observe(0.6, true);
    brain.self_model().own_move_forecasts.observe(0.8, true);
    brain.self_model().opponent_model_forecasts.observe(0.7, true);
    std::cout << "Illustrative opponent forecast Brier score: "
              << *brain.model_of("carla227").move_forecasts.brier_score() << '\n';
}
