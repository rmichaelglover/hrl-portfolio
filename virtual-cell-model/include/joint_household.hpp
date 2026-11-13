#pragma once
#include "household.hpp"

namespace virtual_cell::household {
// The existing PersonModel owns both behavioral preferences and its cellular body.
// Movement does not fabricate a biochemical effect or spend cellular ATP.
struct SituatedPerson {
    mind::PersonModel person;
    motion::Point position;
    std::vector<motion::Choice> intentions;
    mind::NodeId movement_context;
    SituatedPerson(std::string name,motion::Point where)
        :person(name,3,{1,1,1,1,1}),position(where),
         movement_context(person.add_context("Shared household movement")) {
        auto scaffold=electric::make_body_example(name);
        person.human().body()=std::move(scaffold.person.body());
        person.human().body().cell(electric::CellId::brain(0,0)).add_molecule(Molecule("Water: symbolic example",{0,2,0,1}));
        person.human().body().add_eyes({Eye("Left eye",vision::ReferenceFrame({-.032,0,0}),vision::Optics{}),
                                       Eye("Right eye",vision::ReferenceFrame({.032,0,0}),vision::Optics{})});
    }
    motion::Agent proposal() const {
        motion::Agent a;a.from=position;a.preference=person.movement_preferences();
        if(intentions.size()>motion::max_choices)throw std::invalid_argument("Too many movement choices");
        a.count=static_cast<int>(intentions.size());
        for(int i=0;i<a.count;++i)a.choices[i]=intentions[static_cast<std::size_t>(i)];
        return a;
    }
};
inline motion::Decision coordinate_household(std::vector<SituatedPerson>& people,
        const std::vector<motion::Neighbor>& neighbors,int turn) {
    if(people.size()>motion::max_people||neighbors.size()>motion::max_neighbors)
        throw std::invalid_argument("Joint household budget exceeded");
    motion::Agent proposals[motion::max_people];
    for(std::size_t i=0;i<people.size();++i)proposals[i]=people[i].proposal();
    const auto decision=motion::coordinate(proposals,static_cast<int>(people.size()),
        neighbors.data(),static_cast<int>(neighbors.size()),turn);
    if(!decision.feasible)return decision;
    for(std::size_t i=0;i<people.size();++i) {
        auto& resident=people[i];
        const auto& choice=resident.intentions.at(static_cast<std::size_t>(decision.chosen[i]));
        resident.position=choice.to;
        const mind::ObjectiveVector outcomes({0,0,choice.utility,0,0});
        resident.person.observe(resident.movement_context,"Joint peaceful movement",outcomes,outcomes,1,true,
            "Exact C++ simulated swept paths; utility is an authored behavioral proxy");
    }
    return decision;
}
} // namespace virtual_cell::household
