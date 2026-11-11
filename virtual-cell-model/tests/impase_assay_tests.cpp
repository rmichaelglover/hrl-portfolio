#include "impase_assay.hpp"
#include <iostream>
using namespace virtual_cell::bio::assay;
void check(bool ok) { if (!ok) throw std::runtime_error("IMPase assay check failed"); }
template<class F> void rejects(F f) {
    bool rejected=false;
    try { f(); } catch (const std::exception&) { rejected=true; }
    check(rejected);
}
int main() {
    Parameters p; p.half_mm=1; p.lithium_slope_mm=2; p.lithium_intercept_mm=0.4;
    const Conditions c{Substrate::Ribose5Phosphate,1,3,0};
    for (auto mechanism:{Mechanism::Competitive,Mechanism::Uncompetitive,
                         Mechanism::PureNoncompetitive,Mechanism::Mixed}) {
        InitialRateModel model(mechanism,p);
        check(std::abs(model.rate_abs_per_min(c)-0.05)<1e-12);
        auto zero=c;zero.substrate_mm=0;
        check(model.rate_abs_per_min(zero)==0);
        auto li=c;li.lithium_mm=1;
        check(model.rate_abs_per_min(li)<model.rate_abs_per_min(c));
        auto wrong=c;wrong.substrate=Substrate::Inositol1Phosphate;
        rejects([&]{model.rate_abs_per_min(wrong);});
        wrong=c;wrong.ph=6.5; rejects([&]{model.rate_abs_per_min(wrong);});
        wrong=c;wrong.temperature_c=25; rejects([&]{model.rate_abs_per_min(wrong);});
    }
    auto high=c;high.substrate_mm=1e8;high.lithium_mm=1;
    check(std::abs(InitialRateModel(Mechanism::Competitive,p).rate_abs_per_min(high)-.1)<1e-8);
    check(std::abs(InitialRateModel(Mechanism::Uncompetitive,p).rate_abs_per_min(high)-.1/3.5)<1e-8);
    const InitialRateModel mixed(Mechanism::Mixed,p);
    auto li=c;li.lithium_mm=1;
    check(std::abs(mixed.rate_abs_per_min(li)-.1/5)<1e-12);
    Parameters mg;mg.hill=2;
    InitialRateModel activation(Mechanism::HillActivation,mg),inhibitory(Mechanism::HillWithInhibition,mg);
    Conditions m{Substrate::Inositol1Phosphate,.5,1,0};
    const auto at_one=inhibitory.rate_abs_per_min(m);
    m.magnesium_mm=100;
    check(inhibitory.rate_abs_per_min(m)<at_one);
    check(activation.rate_abs_per_min(m)>at_one);
    m.magnesium_mm=0;check(inhibitory.rate_abs_per_min(m)==0);
    m.lithium_mm=1;rejects([&]{inhibitory.rate_abs_per_min(m);});
    rejects([]{Parameters bad;bad.half_mm=0;InitialRateModel model(Mechanism::Mixed,bad);});
    std::cout<<"All conditional IMPase rate-law checks passed.\n";
}
