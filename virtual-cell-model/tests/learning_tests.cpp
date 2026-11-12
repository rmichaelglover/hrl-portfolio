#include "trainable_relaxation.hpp"
#include "compatibility.hpp"
#include <iostream>
using namespace virtual_cell::learning;
void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
Example fixture(){return {{{-.8,.3},{.5,.8},{.1,-.6},{.9,-.2}},{0,1,-1,1},{{{1,.7},{2,.3}},{{0,1}},{},{{3,1}}}};}
int main(){
    double worst=0;
    for(auto steps:{0u,1u,6u})for(double mixing:{.15,.5,1.}){
        RelaxationMachine machine(2,2,steps,mixing);auto parameters=machine.parameters();
        for(std::size_t k=0;k<parameters.size();++k)parameters[k]=.2*std::sin(k+.2);
        machine.set_parameters(parameters);const auto analytic=machine.loss_gradient(fixture());
        for(std::size_t k=0;k<parameters.size();++k){
            auto plus=parameters,minus=parameters;plus[k]+=1e-6;minus[k]-=1e-6;
            machine.set_parameters(plus);const double a=machine.loss_gradient(fixture()).loss;
            machine.set_parameters(minus);const double b=machine.loss_gradient(fixture()).loss;
            worst=std::max(worst,std::abs((a-b)/2e-6-analytic.gradient[k]));
        }
    }
    check(worst<1e-7,"Reverse-mode gradient disagrees with finite differences");
    auto example=fixture();RelaxationMachine model(2,2);auto before=model.forward(example).states.back();
    example.labels={1,0,1,0};check(before==model.forward(example).states.back(),"Reference labels entered inference");
    Example toy{{{-1,0},{-1,.1},{1,0},{1,.1}},{0,0,1,1},{{{1,1}},{{0,1}},{{3,1}},{{2,1}}}};
    Adam optimizer(model.parameters().size());const double initial=model.loss_gradient(toy).loss;
    for(int i=0;i<100;++i)optimizer.update(model,model.loss_gradient(toy).gradient,.03);
    check(model.loss_gradient(toy).loss<initial*.3,"Training loop did not learn synthetic fixture");
    check(model.contraction_bound()<=.875+1e-12,"Projected learning lost stability bound");
    auto graph=fixture();const auto forward=model.forward(graph);
    virtual_cell::mind::CompatibilityField existing(forward.states[0]);
    for(std::size_t i=0;i<graph.features.size();++i)
        for(const auto& edge:graph.neighbors[i])for(std::size_t a=0;a<2;++a)for(std::size_t b=0;b<2;++b)
            existing.add({i,a,edge.index,b,edge.weight*model.parameters()[model.compatibility_offset()+a*2+b]});
    const auto reference=existing.run(model.steps(),model.mixing(),1,0);
    for(std::size_t i=0;i<4;++i)for(std::size_t a=0;a<2;++a)
        check(std::abs(reference.strengths[i][a]-forward.states.back()[i][a])<1e-13,"Existing CompatibilityField forward mismatch");
    auto invalid=fixture();invalid.neighbors[0].push_back({1,.2});bool rejected=false;
    try{model.forward(invalid);}catch(const std::invalid_argument&){rejected=true;}
    check(rejected,"Unnormalized graph accepted");
    std::cout<<"90 parameter derivatives checked; worst absolute error="<<worst<<"; labels excluded from forward; optimizer learns; stability bound retained\n";
}
