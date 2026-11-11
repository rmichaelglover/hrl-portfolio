#pragma once

#include "virtual_cell.hpp"

namespace virtual_cell::bio::assay {

enum class Substrate { Inositol1Phosphate, Ribose5Phosphate };
enum class Mechanism { HillActivation, HillWithInhibition, SingleSiteWithInhibition,
                       Competitive, Uncompetitive, PureNoncompetitive, Mixed };
struct Conditions {
    Substrate substrate;
    double substrate_mm;
    double magnesium_mm; // nominal assay additions, not inferred free-ion activities
    double lithium_mm;
    double ph=7.5;
    double temperature_c=37;
};
struct Parameters {
    double maximum=0.1; // conditional Delta A360/min, not a universal kcat
    double half_mm=0.2; // Mg half-activation or substrate Km, according to model
    double hill=1.8;
    double inhibition_mm=5;
    double lithium_slope_mm=1; // apparent slope constant, not a microscopic Kd
    double lithium_intercept_mm=1; // apparent intercept constant
};

// Empirical initial-rate surface for a single named bovine preparation/assay.
// Model classes describe kinetics and do not prove a unique microscopic scheme.
class InitialRateModel {
    Mechanism mechanism_;
    Parameters p_;
    static void positive(double value) {
        if (nonnegative(value)==0) throw std::invalid_argument("Positive rate parameter required");
    }
public:
    InitialRateModel(Mechanism mechanism,Parameters parameters) : mechanism_(mechanism),p_(parameters) {
        positive(p_.maximum); positive(p_.half_mm); positive(p_.hill);
        positive(p_.inhibition_mm); positive(p_.lithium_slope_mm); positive(p_.lithium_intercept_mm);
    }
    double rate_abs_per_min(const Conditions& c) const {
        nonnegative(c.substrate_mm); nonnegative(c.magnesium_mm); nonnegative(c.lithium_mm);
        finite(c.ph); finite(c.temperature_c);
        if (std::abs(c.ph-7.5)>1e-9 || std::abs(c.temperature_c-37)>1e-9)
            throw std::invalid_argument("Uncalibrated pH or temperature");
        if (mechanism_==Mechanism::HillActivation || mechanism_==Mechanism::HillWithInhibition
            || mechanism_==Mechanism::SingleSiteWithInhibition) {
            if (c.substrate!=Substrate::Inositol1Phosphate || std::abs(c.substrate_mm-0.5)>1e-9
                || c.lithium_mm!=0)
                throw std::invalid_argument("Mg curve requires 0.5 mM Ins1P and no lithium");
            if (c.magnesium_mm==0) return 0;
            const double h=mechanism_==Mechanism::SingleSiteWithInhibition?1:p_.hill;
            const double denominator=std::pow(p_.half_mm/c.magnesium_mm,h)+1
                +(mechanism_==Mechanism::HillActivation?0:c.magnesium_mm/p_.inhibition_mm);
            return nonnegative(p_.maximum/denominator);
        }
        if (c.substrate!=Substrate::Ribose5Phosphate || std::abs(c.magnesium_mm-3)>1e-9)
            throw std::invalid_argument("Li curve requires ribose-5-phosphate and 3 mM nominal Mg");
        double alpha=1,alpha_prime=1;
        if (mechanism_==Mechanism::Competitive || mechanism_==Mechanism::Mixed)
            alpha+=c.lithium_mm/p_.lithium_slope_mm;
        if (mechanism_==Mechanism::Uncompetitive || mechanism_==Mechanism::Mixed)
            alpha_prime+=c.lithium_mm/p_.lithium_intercept_mm;
        if (mechanism_==Mechanism::PureNoncompetitive)
            alpha=alpha_prime=1+c.lithium_mm/p_.lithium_slope_mm;
        return nonnegative(p_.maximum*c.substrate_mm/(alpha*p_.half_mm+alpha_prime*c.substrate_mm));
    }
};

} // namespace virtual_cell::bio::assay
