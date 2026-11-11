#include "enzyme_cycle.hpp"
#include <iostream>
#include <iomanip>
using namespace virtual_cell::bio::cycle;
int main() {
    std::cout<<"# Candidate buffered reaction cycle; microscopic rates are illustrative, not fitted.\n";
    std::cout<<"lithium_mm,time_s,free,substrate_bound,products_bound,products_lithium,expected_cycles,stationary_flux\n";
    for (double lithium:{0.0,.5,1.0,2.0,5.0}) {
        Rates r;r.lithium_mm=lithium;Ensemble population;
        for (int t=0;t<=60;++t) {
            const auto p=population.fractions();
            std::cout<<std::setprecision(14)<<lithium<<','<<t;
            for (double fraction:p) std::cout<<','<<fraction;
            std::cout<<','<<population.expected_cycles()<<','<<stationary(r).cycles_per_second<<'\n';
            if (t<60) population.advance(1,r);
        }
    }
}
