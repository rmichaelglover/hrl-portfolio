#include "seeing_person.hpp"
#include "study_observer.hpp"
#include <iostream>
int main() {
    auto seeing=virtual_cell::vision::make_seeing_alex();
    auto& alex=seeing.alex;
    const auto before=alex.human().body().electrical_time_ms();
    virtual_cell::study::PassiveTracker outside;
    outside.observe(virtual_cell::study::PoseSample{"synthetic-room-1","room",1,2,1,0,.01});
    alex.reflection().revise_musical_context(.8,"listening for melody in a larger context");
    alex.reflection().say(virtual_cell::mind::flowers_mantra());
    std::cout<<"Remembered mantra: "<<alex.reflection().recollections().back().words<<"\n";
    std::cout<<"Happiness reward counter: "<<alex.reflection().count(virtual_cell::mind::ReflectiveReward::Happiness)<<"\n";
    std::cout<<"Physical Body time unchanged by passive tracking: "
             <<(before==alex.human().body().electrical_time_ms())<<"\n";
}
