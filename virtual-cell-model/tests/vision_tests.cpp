#include "seeing_person.hpp"
#include <iostream>
using namespace virtual_cell;
using namespace virtual_cell::vision;
void check(bool ok,const char* why) { if(!ok)throw std::runtime_error(why); }
bool near(double a,double b,double tol=1e-9) { return std::abs(a-b)<tol; }
template<class F> void rejects(F f) {
    bool rejected=false;try {f();} catch(const std::exception&) {rejected=true;}check(rejected,"Invalid vision input accepted");
}
int main() {
    check(std::abs(photon_energy_j(500)-3.972891714e-19)<1e-27,"Photon energy hc/lambda");
    rejects([]{photon_energy_j(0);});
    OpticalWindow window;
    const Emitter source{"light",{0,0,1},1e-10,500};
    Emitter distant=source;distant.position.z=2;
    check(near(window.incident_rate(source)/window.incident_rate(distant),4),"Inverse square law");
    auto infrared=source;infrared.wavelength_nm=1000;
    check(near(window.incident_rate(infrared)/window.incident_rate(source),2),"Photon count versus energy");
    auto behind=source;behind.position.z=-1;check(window.incident_rate(behind)==0,"Light behind eye");
    window.set_open(false);check(window.incident_rate(source)==0,"Closed aperture");
    window.set_open(true);window.set_frame(ReferenceFrame({},pi));
    check(window.incident_rate(source)==0,"Reference-frame orientation");
    rejects([&]{window.incident_rate({"near",{},1e-10,500});});
    Environment environment;environment.add(source);OpticalWindow sample_window;
    std::mt19937_64 rng(7391);double counts=0;const int repetitions=5000;
    const double expectation=sample_window.expected_incident(environment,10);
    for(int i=0;i<repetitions;++i) {
        const auto sample=sample_window.sample(environment,10,rng);
        check(sample.photoisomerizations<=sample.transmitted_photons && sample.transmitted_photons<=sample.incident_photons,"Optical event ledger");
        counts+=sample.incident_photons;
    }
    check(std::abs(counts/repetitions-expectation)<5*std::sqrt(expectation/repetitions),"Poisson mean not physical photon budget");
    RodTransduction rod;check(near(rod.cng_ns(),1.5),"Dark CNG conductance");
    RodTransduction light_event,internal_event;
    light_event.advance(1,1);internal_event.advance(1,1);
    check(light_event.cgmp()==internal_event.cgmp(),"Same transduction event has a hidden source label");
    rod.advance(10,20);check(rod.cgmp()<1 && rod.cng_ns()<1.5,"Phototransduction sign");
    for(int i=0;i<500;++i)rod.advance(10,0);
    check(near(rod.cgmp(),1,1e-8),"Rod recovers after activation");
    RodParameters quiet;quiet.dark_event_rate_per_second=0;
    auto seeing=make_seeing_alex(quiet);auto& body=seeing.alex.human().body();
    check(body.organ_count()==7 && body.has_organ(OrganKind::Eye),"Eyes owned by existing Body");
    check(body.electrical_cells().size()==16,"Retinal cells integrated with Body");
    check(body.nervous_system().synapses().size()==8,"Optic nerve routing");
    Environment too_close;too_close.add({"near pupil",{-.032,0,0},1e-10,500});
    rejects([&]{body.advance_in_environment(too_close,1);});
    check(body.electrical_time_ms()==0,"Invalid optical geometry advanced model time");
    body.advance_electrical(100);
    check(near(body.cell(electric::CellId::eye(0,0,0)).membrane().voltage_mv(),-40),"Dark receptor potential");
    body.eye(1).window().set_open(false);
    body.advance_in_environment(environment,400);
    check(body.eye(0).optical_audit().photoisomerizations>0,"Open eye receives photons");
    check(body.eye(1).optical_audit().incident_photons==0,"Closed eye acquired external photons");
    check(body.cell(electric::CellId::eye(0,0,0)).membrane().voltage_mv()<-40,"Light must hyperpolarize receptor");
    check(body.cell(electric::CellId::eye(0,0,2)).membrane().spike_count()>0,"Retina output spikes");
    check(body.cell(electric::CellId::brain(0,0)).membrane().spike_count()>0,"Photons reached Brain via retinal output");
    auto both_open=make_seeing_alex(),left_closed=make_seeing_alex();
    left_closed.alex.human().body().eye(0).window().set_open(false);
    both_open.alex.human().body().advance_in_environment(environment,100);
    left_closed.alex.human().body().advance_in_environment(environment,100);
    check(both_open.alex.human().body().eye(1).optical_audit().photoisomerizations
          ==left_closed.alex.human().body().eye(1).optical_audit().photoisomerizations,
          "Closing left eye changed the right eye's independent optical stream");
    const Body original=body;Body copy=original;const auto original_count=original.eye(0).optical_audit().incident_photons;
    copy.advance_in_environment(environment,10);
    check(original.eye(0).optical_audit().incident_photons==original_count,"Eye state aliased copied body");
    auto internal=make_seeing_alex();auto& inner=internal.alex.human().body();
    inner.eye(0).window().set_open(false);inner.eye(1).window().set_open(false);
    inner.eye(0).add_endogenous_activation(20);inner.advance_electrical(400);
    check(inner.eye(0).optical_audit().incident_photons==0,"Endogenous activation invented photons");
    check(inner.cell(electric::CellId::eye(0,0,2)).membrane().spike_count()>0,"Endogenous event cannot resemble a sensory response");
    mind::BoundaryObserver observer;
    const double ambiguous=observer.probability_external({4,2,1000});
    check(ambiguous>.1 && ambiguous<.9,"Boundary inference is falsely certain");
    check(observer.probability_external({12,2,1000})>ambiguous,"Visual evidence direction");
    check(observer.probability_external({2,8,1000})<ambiguous,"Interoceptive evidence direction");
    rejects([&]{observer.probability_external({1,1,0});});
    const auto obs=retinal_observation(inner,{0,0},400,0);
    // The observer accepts only counts, not optical/endogenous truth ledgers.
    check(observer.probability_external(obs)>observer.probability_external({0,0,400}),"Internally caused visual evidence was given an origin oracle");
    mind::PersonModel person("Alex",3,{1,1,1,1,1});
    const auto first=person.perceive({12,2,1000},"pattern");
    person.perceive({12,2,1000},"pattern");
    check(person.attended_self().feature("pattern")>first.integrated_value,"Attended representation did not adapt");
    const double before=person.attended_self().feature("pattern");
    person.will().intend(1,mind::Integration::Decline);
    check(person.human().will().intention().integration==mind::Integration::Decline,"Will is not owned by the Person");
    const auto declined=person.perceive({12,2,1000},"pattern");
    check(declined.integrated_value==before && person.percepts().size()==3,"Declining integration removed perception or changed representation");
    person.retire_representation("pattern");
    check(!person.attended_self().active("pattern") && person.attended_self().defined("pattern"),"Retirement annihilated concept definition");
    person.will().intend(1);person.perceive({12,2,1000},"pattern");
    check(person.attended_self().active("pattern"),"Retained concept cannot be reused");
    check(person.available_action_energy()==3,"Perception spent a behavioral action budget");
    person.will().intend(0);
    const double unattended=person.attended_self().feature("pattern");
    person.perceive({12,2,1000},"pattern");
    check(person.attended_self().feature("pattern")==unattended,"Zero attention still changed attended representation");
    std::cout<<"All photon, retina, eye ownership, boundary inference and Will checks passed.\n";
}
