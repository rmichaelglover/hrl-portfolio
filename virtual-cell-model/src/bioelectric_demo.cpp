#include "bioelectric_body.hpp"
#include <iomanip>
#include <iostream>
using namespace virtual_cell;
using namespace virtual_cell::electric;
int main(int argc,char** argv) {
    if(argc==2 && std::string(argv[1])=="--rc") {
        Membrane membrane({100,5,-65});
        std::cout<<"time_ms,voltage_mv\n";
        for(int t=0;t<=100;++t) {
            std::cout<<std::setprecision(17)<<t<<','<<membrane.voltage_mv()<<'\n';
            if(t<100)membrane.advance(1,100);
        }
        return 0;
    }
    bool spikes=false,wired=true,high_leak=false;double step=.05;
    for(int i=1;i<argc;++i) {
        const std::string arg=argv[i];
        if(arg=="--spikes")spikes=true;
        else if(arg=="--disconnected")wired=false;
        else if(arg=="--high-leak")high_leak=true;
        else if(arg=="--fine")step=.01;
        else {std::cerr<<"Unknown option\n";return 1;}
    }
    auto example=make_body_example("Bioelectric example",wired);auto& body=example.person.body();
    if(high_leak)body.cell(example.sensory_brain).attach_membrane(Membrane({100,200,-65},-65,SpikeRule{}));
    if(!spikes) {
        std::cout<<"# Passive RC + reduced spiking + delayed conductance synapses. Synthetic wiring and parameters.\n";
        std::cout<<"time_ms,input_pa,skin_sensor_mv,sensory_brain_mv,motor_brain_mv,heart_mv,lungs_mv,skin_mv,mouth_mv,skin_spikes,sensory_spikes,motor_spikes\n";
    }
    for (int t=0;t<=150;++t) {
        const double input=t>=20 && t<80?350:0;
        if(!spikes) {
          std::cout<<std::setprecision(14)<<body.electrical_time_ms()<<','<<input;
          for (const auto id:{example.skin_sensor,example.sensory_brain,example.motor_brain,
                           example.heart_target,example.lungs_target,example.skin_target,example.mouth_target})
            std::cout<<','<<body.cell(id).membrane().voltage_mv();
        for (const auto id:{example.skin_sensor,example.sensory_brain,example.motor_brain})
            std::cout<<','<<body.cell(id).membrane().spike_count();
          std::cout<<'\n';
        }
        if (t<150) body.advance_electrical(1,{{example.skin_sensor,input}},step);
    }
    if(spikes) {
        std::cout<<"time_ms,region,organ_index,tissue_index,cell_index\n";
        for(const auto& spike:body.nervous_system().spikes())
            std::cout<<std::setprecision(14)<<spike.time_ms<<','<<(spike.source.in_brain?"brain":"peripheral")
                <<','<<spike.source.organ_index<<','<<spike.source.tissue_index<<','<<spike.source.cell_index<<'\n';
    }
}
