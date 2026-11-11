#include "person_model.hpp"
#include <iostream>
#include <limits>

using namespace virtual_cell;
using namespace virtual_cell::bio;
void check(bool ok,const char* message) { if (!ok) throw std::runtime_error(message); }
bool near(double a,double b,double tolerance=1e-9) {
    return std::abs(a-b)<=tolerance*(1+std::max(std::abs(a),std::abs(b)));
}
template<class F> void rejects(F f) {
    bool caught=false;
    try { f(); } catch (const std::exception&) { caught=true; }
    check(caught,"Invalid input accepted");
}
void conserved(const Inventory& before,const Inventory& after) {
    for (std::size_t i=0;i<before.size();++i)
        check(near(before[i],after[i],1e-10),"Inventory not conserved");
}
double free_energy(const Compartment& a,const Compartment& b) {
    double sum=0;
    for (const auto* c:{&a,&b}) for (auto s:{Species::Lithium,Species::Chloride}) {
        const double n=c->amount_fmol(s),concentration=c->concentration_mm(s);
        if (n>0) sum+=n*(std::log(concentration)-1); // RT omitted; reference 1 mM
    }
    return sum;
}
int main() {
    rejects([]{ Picolitres bad(0); });
    rejects([]{ Millimolar bad(-1); });
    rejects([]{ Seconds bad(std::numeric_limits<double>::quiet_NaN()); });
    Compartment c(Picolitres(2));
    c.prepare(Species::Lithium,Millimolar(1));
    c.prepare(Species::Site,Millimolar(1));
    check(c.amount_fmol(Species::Lithium)==2,"Unit conversion incorrect");
    const auto original=c.inventory(); const double initial_charge=c.charge_fmol_e();
    for (int i=0;i<100;++i) bind(c,Species::Lithium,Species::LithiumSite,{1,1},Seconds(1));
    // Equal initial 1 mM pools, Kd=1 mM: b=(3-sqrt(5))/2.
    check(near(c.concentration_mm(Species::LithiumSite),(3-std::sqrt(5.0))/2),"Binding equilibrium incorrect");
    conserved(original,c.inventory());
    check(near(initial_charge,c.charge_fmol_e()),"Binding charge not conserved");
    const auto before_zero=c.inventory(); const double bound=c.amount_fmol(Species::LithiumSite);
    bind(c,Species::Lithium,Species::LithiumSite,{1,1},Seconds(0));
    check(bound==c.amount_fmol(Species::LithiumSite),"Zero time changed state");
    rejects([&]{ bind(c,Species::Lithium,Species::MagnesiumSite,{1,1},Seconds(1)); });
    conserved(before_zero,c.inventory());
    rejects([&]{ c.transfer_to(c,Species::Lithium,-1); });
    Compartment empty(Picolitres(1));
    rejects([&]{ c.transfer_to(empty,Species::Lithium,100); });
    for (int i=0;i<10;++i) bind(c,Species::Lithium,Species::LithiumSite,{1e6,1e6},Seconds(100));
    conserved(original,c.inventory());

    Compartment a(Picolitres(3)),b(Picolitres(1));
    a.prepare(Species::Lithium,Millimolar(1)); a.prepare(Species::Chloride,Millimolar(1));
    b.prepare(Species::Lithium,Millimolar(0.1)); b.prepare(Species::Chloride,Millimolar(20));
    const double energy=free_energy(a,b),al=a.amount_fmol(Species::Lithium);
    const double charge_a=a.charge_fmol_e(),charge_b=b.charge_fmol_e();
    // Li alone points a->b, but salt chemical potential points b->a.
    exchange_licl(a,b,1,Seconds(0.2));
    check(a.amount_fmol(Species::Lithium)>al,"Salt moved against chemical potential");
    check(free_energy(a,b)<=energy+1e-12,"Passive exchange increased free energy");
    check(near(charge_a,a.charge_fmol_e()) && near(charge_b,b.charge_fmol_e()),"Salt exchange changed charge");
    for (int i=0;i<100;++i) exchange_licl(a,b,1,Seconds(1));
    check(near(a.concentration_mm(Species::Lithium)*a.concentration_mm(Species::Chloride),
               b.concentration_mm(Species::Lithium)*b.concentration_mm(Species::Chloride)),"Salt equilibrium incorrect");
    // Empty destination and unavailable chloride: no flux, no negative pools.
    Compartment no_cl(Picolitres(1)),destination(Picolitres(1));
    no_cl.prepare(Species::Lithium,Millimolar(1));
    exchange_licl(no_cl,destination,1,Seconds(1000));
    check(near(destination.amount_fmol(Species::Lithium),0),"Flux without counterion");

    auto zero=illustrative_physiology(Millimolar(0));
    auto exposed=illustrative_physiology(Millimolar(1));
    auto fine=exposed;
    const auto inventory=exposed.inventory(); const double charge=exposed.total_charge_fmol_e();
    zero.advance(Seconds(60)); exposed.advance(Seconds(60)); fine.advance(Seconds(60),Seconds(0.005));
    conserved(inventory,exposed.inventory());
    check(near(charge,exposed.total_charge_fmol_e()),"System charge not conserved");
    check(near(charge,0),"Synthetic preparation is not electrically neutral");
    for (const auto* compartment:{&exposed.inside(),&exposed.outside()})
        for (std::size_t i=0;i<species_count;++i)
            check(compartment->amount_fmol(static_cast<Species>(i))>=0,"Negative pool");
    check(zero.snapshot().lithium_inside_mm==0,"Lithium appeared without source");
    check(exposed.snapshot().productive_site_fraction<zero.snapshot().productive_site_fraction,
          "Competition did not reduce productive occupancy");
    check(exposed.snapshot().response_proxy<zero.snapshot().response_proxy,"Coupled proxy did not change");
    const OperatingRange lower_range(1.35,1.42),upper_range(1.45,1.50);
    check(lower_range.distance(exposed.snapshot().response_proxy)
          <lower_range.distance(zero.snapshot().response_proxy),"Expected approach to lower range");
    check(upper_range.distance(exposed.snapshot().response_proxy)
          >upper_range.distance(zero.snapshot().response_proxy),"Expected departure from upper range");
    rejects([]{ OperatingRange invalid(2,1); });
    check(near(exposed.snapshot().response_proxy,fine.snapshot().response_proxy,0.002),"Step refinement did not agree");
    check(near(exposed.snapshot().lithium_inside_mm,fine.snapshot().lithium_inside_mm,0.002),"Transport step refinement failed");
    auto coarse=illustrative_physiology(Millimolar(1));
    auto medium=coarse,reference=coarse;
    coarse.advance(Seconds(5),Seconds(0.04));
    medium.advance(Seconds(5),Seconds(0.02));
    reference.advance(Seconds(5),Seconds(0.0025));
    check(std::abs(medium.snapshot().response_proxy-reference.snapshot().response_proxy)
          <std::abs(coarse.snapshot().response_proxy-reference.snapshot().response_proxy),
          "Step refinement failed to reduce transient response error");
    PhysiologyParameters disconnected;
    disconnected.kinase_gain=0; disconnected.inositol_gain=0;
    auto null_zero=illustrative_physiology(Millimolar(0),disconnected);
    auto null_li=illustrative_physiology(Millimolar(1),disconnected);
    null_zero.advance(Seconds(60)); null_li.advance(Seconds(60));
    check(near(null_zero.snapshot().response_proxy,null_li.snapshot().response_proxy),"Uncoupled response changed");
    check(null_li.snapshot().lithium_inside_mm>0,"Null response lacked molecular exposure");
    auto blocked_parameters=PhysiologyParameters{};
    blocked_parameters.salt_conductance_pl_per_mm_second=0;
    auto blocked=illustrative_physiology(Millimolar(1),blocked_parameters);
    blocked.advance(Seconds(60));
    check(blocked.snapshot().lithium_inside_mm==0,"Blocked transport leaked");
    check(near(blocked.snapshot().response_proxy,zero.snapshot().response_proxy),"Blocked exposure changed response");

    // Compare IMPase rates at the same substrate concentration.
    Compartment assay(Picolitres(1));
    assay.prepare(Species::InositolMonophosphate,Millimolar(0.2));
    assay.prepare(Species::Water,Millimolar(10));
    const double baseline=impase_rate(assay,{});
    assay.prepare(Species::Lithium,Millimolar(1));
    check(near(impase_rate(assay,{})/baseline,0.6),"Uncompetitive inhibition ratio incorrect");
    const auto initial_assay=assay.inventory();
    hydrolyze(assay,{},Seconds(1e6)); conserved(initial_assay,assay.inventory());
    check(assay.concentration_mm(Species::Inositol)<=0.2,"Hydrolysis exceeded substrate");
    std::array<int,species_count> bad_reaction{}; bad_reaction[0]=1;
    rejects([&]{ assay.react(bad_reaction,1); });
    rejects([&]{ exposed.advance(Seconds(1),Seconds(0)); });
    rejects([&]{ exposed.advance(Seconds(1e9),Seconds(1e-9)); });

    mind::PersonModel person("Synthetic",3,{1,1,1,1,1});
    rejects([&]{ person.advance_physiology(Seconds(1)); });
    person.attach_physiology(illustrative_physiology(Millimolar(1)));
    // Biochemical evolution has no permission gate.
    person.human().set_governance(false,0);
    person.advance_physiology(Seconds(1));
    check(person.physiology().snapshot().lithium_inside_mm>0,"Governance incorrectly stopped chemistry");
    check(person.available_action_energy()==3 && person.experiences().empty(),"Chemistry changed behavioral accounting");
    std::cout << "All biochemical conservation, equilibrium, response and integration checks passed.\n";
}
