#include "fixed_point_comparison.hpp"
#include <iostream>
using namespace virtual_cell::mind;
using namespace virtual_cell::mind::comparison;
void require(bool value) {if(!value) throw std::runtime_error("Convergence check failed");}
int main() {
    CompatibilityField field({{.8,.2},{.3,.7}});
    field.add({0,0,1,0,.25}); field.add({1,1,0,1,-.15});
    BinarySystem system(field,.4); RelaxationSolver relax(.5); NewtonSolver newton;
    auto a=relax.run(system),b=newton.run(system);
    require(a.converged && b.converged);
    for(std::size_t i=0;i<2;++i) {require(std::abs(a.state[i]-b.state[i])<2e-10);require(b.state[i]>=0 && b.state[i]<=1);}
    // Independent closed-form softmax for the first map evaluation.
    auto t=field.target(field.prior(),.4);
    double expected=.8*std::exp(.4*.25*.3)/(.8*std::exp(.4*.25*.3)+.2);
    require(std::abs(t[0][0]-expected)<1e-14);
    auto one=field.run(1,.5,.4,0);
    require(std::abs(one.strengths[0][0]-(.8+.5*(expected-.8)))<1e-14);
    RelaxationSolver tiny(1e-12); require(!tiny.run(system,1).converged);
    CompatibilityField anchored({{1.,0.}}); require(anchored.target({{.5,.5}})[0][1]==0);
    bool rejected=false; try {field.target({{.5,.6},{.3,.7}});} catch(const std::invalid_argument&) {rejected=true;} require(rejected);
    Vector answer; require(solve({{0,2},{1,3}},{4,7},answer)); require(std::abs(answer[0]-1)<1e-14 && std::abs(answer[1]-2)<1e-14);
    require(!solve({{1,1},{2,2}},{1,2},answer));
    std::cout<<"Shared map, fixed-point agreement, simplex, stopping, anchoring, pivot and singular checks passed\n";
}
