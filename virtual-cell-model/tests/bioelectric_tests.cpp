#include "bioelectric_body.hpp"
#include <iostream>
#include <type_traits>
using namespace virtual_cell;
using namespace virtual_cell::electric;
void check(bool condition,const char* reason) { if (!condition) throw std::runtime_error(reason); }
bool near(double a,double b,double tolerance=1e-9) { return std::abs(a-b)<tolerance; }
template<class F> void rejects(F f) {
    bool caught=false;try {f();} catch(const std::exception&) {caught=true;}
    check(caught,"Invalid electrical input was accepted");
}
int main() {
    static_assert(std::is_copy_constructible_v<Body> && std::is_move_constructible_v<Body>);
    static_assert(std::is_nothrow_destructible_v<Body> && std::is_nothrow_destructible_v<Membrane>);
    // Successful creation/destruction needs no optional initialization or cleanup.
    {Body body;Brain brain;body.add_brain(brain);}
    {auto ready=make_body_example();check(ready.person.body().organ_count()==5,"Body composition");}
    rejects([]{Membrane bad({0,5,-65});});
    rejects([]{Membrane bad({100,-1,-65});});
    rejects([]{Membrane bad({},-65,SpikeRule{-50,-40,2});});
    rejects([]{nernst_mv(0,1,1);});
    check(nernst_mv(1,140,5)<-80,"K Nernst sign/scale");
    check(nernst_mv(1,15,145)>50,"Na Nernst sign/scale");
    check(nernst_mv(-1,10,120)<-50,"Anion Nernst sign");
    check(near(nernst_mv(1,5,5),0),"Nernst equal concentrations");
    check(near(nernst_mv(1,140,5),-nernst_mv(1,5,140)),"Nernst gradient reversal");

    Membrane rc({100,5,-65});rc.advance(20,100);
    check(near(rc.voltage_mv(),-45+(-65+45)*std::exp(-1.0)),"Analytical RC step response");
    Membrane split({100,5,-65});for(int i=0;i<200;++i)split.advance(.1,100);
    check(near(rc.voltage_mv(),split.voltage_mv()),"RC semigroup");
    Membrane capacitor({100,0,-65});capacitor.advance(10,20);
    check(near(capacitor.voltage_mv(),-63),"Pure capacitive integration and units");
    Membrane clamped({100,5,-65});clamped.advance(200,0,{{5,0}});
    check(near(clamped.voltage_mv(),-32.5,1e-6),"Parallel conductance equilibrium");
    rejects([&]{clamped.advance(-1);});
    rejects([&]{clamped.advance(1,0,{{-1,0}});});
    check(!rc.advance(0,100),"Zero time must not spike");
    rc.advance(200,0);check(std::abs(rc.voltage_mv()+65)<.001,"RC returns toward rest");

    // Compare reduced-model ISI with exact crossing plus refractory duration.
    const double exact_isi=-20*std::log(1-15.0/100)+2;
    auto measured_isi=[](double dt) {
        Membrane membrane({},-65,SpikeRule{});std::vector<double> spikes;
        for(int i=0;i<200/dt;++i) if(membrane.advance(dt,500))spikes.push_back((i+1)*dt);
        return (spikes.back()-spikes.front())/(spikes.size()-1);
    };
    const double coarse=measured_isi(.1),fine=measured_isi(.01);
    check(std::abs(fine-exact_isi)<.02,"LIF firing interval physical reference");
    check(std::abs(fine-exact_isi)<=std::abs(coarse-exact_isi)+1e-9,"Spike timing refinement");
    Membrane refractory({},-65,SpikeRule{-50,-65,2});
    check(refractory.advance(20,500),"Driven neuron spikes");
    check(!refractory.advance(1,500) && refractory.voltage_mv()==-65,"Refractory reset hold");

    auto example=make_body_example();auto& body=example.person.body();
    check(body.electrical_cells().size()==10,"Owned electrical cells");
    check(body.nervous_system().synapses().size()==6,"Nervous system wiring");
    check(body.brain().tissue(0).cell_count()==2,"Brain owns its cells");
    for (auto kind:{OrganKind::Brain,OrganKind::Heart,OrganKind::Lungs,OrganKind::Skin,OrganKind::Mouth})
        check(example.person.has_organ(kind),"Required organ missing");
    rejects([&]{body.connect(CellId::brain(99,0),example.heart_target);});
    rejects([&]{body.connect(example.heart_target,example.sensory_brain);});
    rejects([&]{body.connect(example.skin_sensor,example.sensory_brain,{1,0,0,1});});
    rejects([&]{body.add_brain(Brain{});});
    rejects([&]{body.advance_electrical(1,{{CellId::organ(99,0,0),1}});});
    check(body.electrical_time_ms()==0,"Invalid input changed time");
    body.advance_electrical(20);
    for (auto id:body.electrical_cells())check(near(body.cell(id).membrane().voltage_mv(),-65),"Unforced rest");
    // First sensory spike is near 22.45 ms; a delayed synapse cannot affect the
    // brain by 23 ms. Delivery occurs only at/after spike time + 1 ms.
    body.advance_electrical(3,{{example.skin_sensor,350}});
    check(body.cell(example.skin_sensor).membrane().spike_count()==1,"Sensor excitation");
    check(near(body.cell(example.sensory_brain).membrane().voltage_mv(),-65),"Transmission arrived before delay");
    body.advance_electrical(57,{{example.skin_sensor,350}});
    check(body.cell(example.sensory_brain).membrane().spike_count()>0,"Brain received sensory input");
    check(body.cell(example.motor_brain).membrane().spike_count()>0,"Brain integration path");
    for(auto id:{example.heart_target,example.lungs_target,example.skin_target,example.mouth_target})
        check(body.cell(id).membrane().voltage_mv()>-65,"Peripheral target electrical response");
    for (const auto& spike:body.nervous_system().spikes())check(spike.time_ms<=80+1e-9,"Future spike recorded");
    auto copy=example;const double original_voltage=body.cell(example.heart_target).membrane().voltage_mv();
    copy.person.body().advance_electrical(10);
    check(body.electrical_time_ms()==80,"Copy changed original time");
    check(body.cell(example.heart_target).membrane().voltage_mv()==original_voltage,"Copy wiring aliased original");
    auto moved=std::move(copy);moved.person.body().advance_electrical(1);
    check(near(moved.person.body().electrical_time_ms(),91),"Moved model lost owned wiring/state");
    body.advance_electrical(300);
    for(auto id:body.electrical_cells())check(std::abs(body.cell(id).membrane().voltage_mv()+65)<.01,"Recovery after stimulus");
    // Depolarizing and hyperpolarizing drives are not hard-coded positive effects.
    Membrane inhibited;inhibited.advance(10,-100);
    check(inhibited.voltage_mv()<-65,"Hyperpolarizing input sign");
    std::cout<<"All bioelectric ownership, RC, spiking, routing and body checks passed.\n";
}
