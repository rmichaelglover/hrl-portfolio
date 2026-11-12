#include "inference_evidence.hpp"
#include "seeing_person.hpp"
#include <iostream>
using namespace virtual_cell::mind;
int main() {
    EvidenceEncoder encoder;
    const auto evidence=encoder.encode({10,10,1000},"test:counts");
    if(evidence.visually_active.value()+evidence.bodily_active.value()<=1)
        throw std::runtime_error("Fuzzy memberships were normalized into probabilities");
    BoundaryObserver observer;
    if(evidence.bayesian_external_probability!=observer.probability_external(evidence.observation))
        throw std::runtime_error("Bayesian evidence changed in encoding");
    for(int which=0;which<3;++which) {
        bool rejected=false;
        try {
            if(which==0)encoder.encode({0,0,0},"test");
            if(which==1)encoder.encode({0,0,1000},"");
            if(which==2)FuzzyMembership bad(1.1);
        } catch(const std::invalid_argument&) {rejected=true;}
        if(!rejected)throw std::runtime_error("Invalid evidence accepted");
    }
    auto seeing=virtual_cell::vision::make_seeing_alex();
    const auto& alex=seeing.alex;
    const auto body_time=alex.human().body().electrical_time_ms();
    const auto packet=alex.boundary_evidence({10,10,1000},"alex:window");
    if(packet.observation.visual_events!=10 || !alex.percepts().empty()
       || alex.human().body().electrical_time_ms()!=body_time)
        throw std::runtime_error("Encoding changed the Person or Body");
    const auto copy=evidence;
    if(copy.provenance!="test:counts")throw std::runtime_error("Value ownership failed");
    std::cout<<"Typed evidence checks passed\n";
}
