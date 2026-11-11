#pragma once
#include "bioelectric_body.hpp"
#include "person_model.hpp"

namespace virtual_cell::vision {
struct SeeingPerson {
    mind::PersonModel alex;
    electric::CellId left_optic=electric::CellId::eye(0,0,2);
    electric::CellId right_optic=electric::CellId::eye(1,0,2);
};
inline SeeingPerson make_seeing_alex() {
    SeeingPerson result{mind::PersonModel("Alex",3,{1,1,1,1,1})};
    auto scaffold=electric::make_body_example("Alex");
    auto& body=result.alex.human().body();body=std::move(scaffold.person.body());
    body.add_eyes({Eye("Left eye",ReferenceFrame({-.032,0,0})),
                   Eye("Right eye",ReferenceFrame({.032,0,0}))});
    body.connect(result.left_optic,electric::CellId::brain(0,0),{5,5,0,2});
    body.connect(result.right_optic,electric::CellId::brain(0,0),{5,5,0,2});
    return result;
}
inline mind::BoundaryObservation retinal_observation(const Body& body,
        std::array<std::size_t,2> prior_counts,double duration_ms,std::size_t interoceptive_events) {
    electric::detail::positive(duration_ms);
    std::size_t visual=0;
    for(std::size_t side=0;side<2;++side) {
        const auto count=body.cell(electric::CellId::eye(side,0,2)).membrane().spike_count();
        if(count<prior_counts[side])throw std::invalid_argument("Counts belong to a different observation interval");
        visual+=count-prior_counts[side];
    }
    // Only observable event counts cross into the observer. Optical truth audits
    // and endogenous-activation counters are excluded from this interface.
    return {visual,interoceptive_events,duration_ms};
}
} // namespace virtual_cell::vision
