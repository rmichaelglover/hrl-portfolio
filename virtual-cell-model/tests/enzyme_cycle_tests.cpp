#include "enzyme_cycle.hpp"
#include <iostream>
using namespace virtual_cell::bio::cycle;
void check(bool ok) { if (!ok) throw std::runtime_error("Reaction-cycle check failed"); }
bool near(double a,double b,double tol=1e-10) { return std::abs(a-b)<tol; }
template<class F> void rejects(F f) {
    bool threw=false;try { f(); } catch(const std::exception&) { threw=true; }check(threw);
}
int main() {
    Enzyme enzyme;Rates r;
    check(!enzyme.bind_lithium() && !enzyme.release_products());
    check(enzyme.bind_substrate() && !enzyme.bind_substrate());
    check(enzyme.catalyze() && enzyme.completed_cycles()==0);
    check(enzyme.bind_lithium() && !enzyme.bind_lithium());
    check(near(enzyme.product_release_rate(r),.2));
    check(enzyme.release_lithium() && !enzyme.has_lithium());
    check(!enzyme.release_lithium() && enzyme.state()==EnzymeState::ProductsBound);
    check(enzyme.bind_lithium() && enzyme.release_products());
    check(!enzyme.has_lithium() && enzyme.state()==EnzymeState::Free && enzyme.completed_cycles()==1);
    check(!enzyme.release_products() && enzyme.completed_cycles()==1);
    check(enzyme.release_probability(1,r)==0);
    check(near(event_probability(1,1),1-std::exp(-1.0)));
    check(event_probability(.2,1)<event_probability(1,1));
    check(event_probability(1,0)==0 && event_probability(0,1)==0);
    rejects([]{event_probability(1,-1);});
    rejects([]{Rates invalid;invalid.lithium_mm=-1;stationary(invalid);});
    for (double li:{0.0,1.0,5.0}) {
        r.lithium_mm=li;
        const auto expected=stationary(r);Ensemble population;
        population.advance(100,r);
        double sum=0;
        for (std::size_t i=0;i<4;++i) {
            check(population.fractions()[i]>=0);
            check(near(population.fractions()[i],expected.fractions[i]));
            sum+=population.fractions()[i];
        }
        check(near(sum,1));
        const double before=population.expected_cycles();population.advance(10,r);
        check(near((population.expected_cycles()-before)/10,expected.cycles_per_second));
        Ensemble whole,split;whole.advance(7,r);
        for (int i=0;i<70;++i) split.advance(.1,r);
        check(near(whole.expected_cycles(),split.expected_cycles()));
        for (std::size_t i=0;i<4;++i) check(near(whole.fractions()[i],split.fractions()[i]));
        // Independent exact-event sampling validates the master equation reward.
        const int n=3000;double total=0,squares=0;std::mt19937_64 rng(4721);
        Ensemble finite_time;finite_time.advance(10,r);
        for (int i=0;i<n;++i) {
            Enzyme molecule;molecule.advance(10,r,rng);
            const double cycles=static_cast<double>(molecule.completed_cycles());
            total+=cycles;squares+=cycles*cycles;
        }
        const double mean=total/n;
        const double se=std::sqrt((squares/n-mean*mean)/n);
        check(std::abs(mean-finite_time.expected_cycles())<5*se);
    }
    Rates unexposed,exposed;exposed.lithium_mm=5;
    check(stationary(exposed).cycles_per_second<stationary(unexposed).cycles_per_second);
    exposed.lithium_product_release=exposed.product_release;
    check(near(stationary(exposed).cycles_per_second,stationary(unexposed).cycles_per_second));
    Rates absent;absent.substrate_mm=0;Ensemble empty;empty.advance(10,absent);
    check(empty.expected_cycles()==0 && empty.fractions()[0]==1);
    // No instantaneous single-molecule hazard formula substitutes for competing
    // transitions: long-term occupancy/throughput comes from the full network.
    std::cout<<"All reaction-cycle, analytic, propagation and stochastic checks passed.\n";
}
