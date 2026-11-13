#include "joint_household.hpp"
#include <iostream>
using namespace virtual_cell;
int main() {
    std::vector<household::SituatedPerson> residents;
    for(const auto& name:{"Alex","Rosy","Mama","Papa","Cypher"})residents.emplace_back(name,motion::Point{double(residents.size()),2});
    residents[0].intentions={{{.5,2},2,true},{{0,2},0,true}};
    residents[1].intentions={{{.5,2},2,true},{{1,2},0,true}};
    for(std::size_t i=2;i<residents.size();++i)residents[i].intentions={{{double(i),2},0,true}};
    const auto decision=household::coordinate_household(residents,{},0);
    std::cout<<"{\"kernel\":\"native C++ shared with Glims WebAssembly\",\"feasible\":"<<(decision.feasible?"true":"false")<<",\"people\":[";
    for(std::size_t i=0;i<residents.size();++i) {
        if(i)std::cout<<',';
        const auto& p=residents[i];const auto& body=p.person.human().body();
        std::cout<<"{\"name\":\""<<p.person.human().name()<<"\",\"organs\":"<<body.organ_count()
                 <<",\"molecules\":"<<body.molecule_count()<<",\"eyes\":2,\"movement_experiences\":"<<p.person.experiences().size()<<'}';
    }
    std::cout<<"]}\n";
}
