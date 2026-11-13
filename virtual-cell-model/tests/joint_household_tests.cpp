#include "joint_household.hpp"
#include <iostream>
using namespace virtual_cell;
void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
int main() {
    using namespace motion;
    check(swept_squared({0,0},{1,0},{1,0},{0,0})==0,"Swap not detected");
    check(swept_squared({0,1},{2,1},{1,0},{1,2})==0,"Crossing not detected");
    std::vector<household::SituatedPerson> people;
    people.emplace_back("Alex",Point{0,0});people.emplace_back("Rosy",Point{1,0});
    people[0].intentions={{{.5,0},2,true},{{0,0},0,true}};
    people[1].intentions={{{.5,0},2,true},{{1,0},0,true}};
    const auto molecules=people[0].person.human().molecule_count();
    const auto d=household::coordinate_household(people,{},0);
    check(d.feasible,"No compatible joint move");
    check(!(d.chosen[0]==0&&d.chosen[1]==0),"Both occupied same space");
    check(people[0].person.human().has_organ(OrganKind::Eye),"Eyes removed");
    check(people[0].person.human().has_organ(OrganKind::Brain),"Cellular brain removed");
    check(molecules>0&&people[0].person.human().molecule_count()==molecules,"Movement changed cellular conservation");
    check(people[0].person.experiences().size()==1,"Movement not in existing memory");
    Agent a;a.from={0,0};a.count=2;a.choices[0]={{1,0},10,true};a.choices[1]={{0,0},0,true};
    Neighbor frog{{1,0},{0,0},.3};
    auto f=coordinate(&a,1,&frog,1);
    check(!f.feasible,"Impossible frog swap permitted a movement");
    frog={{1,0},{1,0},.3};f=coordinate(&a,1,&frog,1);
    check(f.feasible&&f.chosen[0]==1,"Frog protection lost to high utility");
    a.choices[0].allowed=false;a.choices[1].allowed=false;
    check(!coordinate(&a,1,nullptr,0).feasible,"No-action case moved");
    a.count=5;check(!coordinate(&a,1,nullptr,0).feasible,"Invalid choice count accepted");
    std::cout<<"Joint household: crossing, yielding, frog, no-action, cellular ownership and memory checks passed\n";
}
