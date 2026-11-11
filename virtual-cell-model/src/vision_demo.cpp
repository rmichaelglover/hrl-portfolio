#include "seeing_person.hpp"
#include <iomanip>
#include <iostream>
using namespace virtual_cell;
using namespace virtual_cell::vision;
int main(int argc,char** argv) {
    std::string scenario=argc>1?argv[1]:"light";
    if(scenario!="light" && scenario!="one-eye" && scenario!="closed" && scenario!="endogenous" && scenario!="decline") {
        std::cerr<<"Expected light, one-eye, closed, endogenous, or decline\n";return 1;
    }
    auto model=make_seeing_alex();auto& alex=model.alex;auto& body=alex.human().body();
    body.set_visual_seed(20261111);
    if(scenario=="one-eye")body.eye(0).window().set_open(false);
    if(scenario=="closed")for(std::size_t s=0;s<2;++s)body.eye(s).window().set_open(false);
    if(scenario=="decline")alex.will().intend(1,mind::Integration::Decline);
    Environment light;light.add({"Point lamp",{0,0,1},1e-10,500});
    Environment darkness;
    std::cout<<"# Reduced vertebrate-inspired eyes. Illustrative kinetics, likelihoods and attended-integration rule.\n";
    std::cout<<"time_ms,left_rod_mv,right_rod_mv,left_cgmp,right_cgmp,left_photoevents,right_photoevents,left_endogenous,right_endogenous,left_ganglion,right_ganglion,brain_spikes,p_external,integrated_feature\n";
    std::array<std::size_t,2> previous{{0,0}};double probability=.5;
    for(int t=0;t<=1500;++t) {
        if(t%100==0 && t>0) {
            const auto observed=retinal_observation(body,previous,100,0);
            probability=alex.perceive(observed,"light_activity").probability_external;
            for(std::size_t side=0;side<2;++side)previous[side]=body.cell(electric::CellId::eye(side,0,2)).membrane().spike_count();
        }
        if(t%10==0) {
            std::cout<<std::setprecision(14)<<t;
            for(std::size_t side=0;side<2;++side)std::cout<<','<<body.cell(electric::CellId::eye(side,0,0)).membrane().voltage_mv();
            for(std::size_t side=0;side<2;++side)std::cout<<','<<body.eye(side).cgmp();
            for(std::size_t side=0;side<2;++side)std::cout<<','<<body.eye(side).optical_audit().photoisomerizations;
            for(std::size_t side=0;side<2;++side)std::cout<<','<<body.eye(side).endogenous_events();
            for(std::size_t side=0;side<2;++side)std::cout<<','<<body.cell(electric::CellId::eye(side,0,2)).membrane().spike_count();
            std::cout<<','<<body.cell(electric::CellId::brain(0,0)).membrane().spike_count()<<','<<probability<<','<<alex.attended_self().feature("light_activity")<<'\n';
        }
        if(t==200 && scenario=="endogenous")body.eye(0).add_endogenous_activation(20);
        if(t<1500)body.advance_in_environment(t>=200 && t<600 && scenario!="endogenous"?light:darkness,1);
    }
}
