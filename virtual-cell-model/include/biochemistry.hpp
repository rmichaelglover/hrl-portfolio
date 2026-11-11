#pragma once

#include "virtual_cell.hpp"

namespace virtual_cell::bio {

// Numerical values at API boundaries carry their unit in the type or name.
struct Millimolar { double value; explicit Millimolar(double v) : value(nonnegative(v)) {} };
struct Picolitres {
    double value;
    explicit Picolitres(double v) : value(nonnegative(v)) {
        if (v == 0) throw std::invalid_argument("Volume must be positive");
    }
};
struct Seconds { double value; explicit Seconds(double v) : value(nonnegative(v)) {} };

enum class Species : std::size_t {
    Lithium, Magnesium, Chloride, Site, LithiumSite, MagnesiumSite,
    InositolMonophosphate, Inositol, Phosphate, Water, Sodium, Count
};
constexpr std::size_t species_count = static_cast<std::size_t>(Species::Count);
// Li, Mg, Cl, C, H, O, P, an abstract enzyme-site moiety, and Na.
using Inventory = std::array<double, 9>;
struct SpeciesDefinition { const char* name; int charge; Inventory composition; };
inline const SpeciesDefinition& definition(Species s) {
    static const std::array<SpeciesDefinition, species_count> definitions{{
        {"Li+", 1, {1,0,0,0,0,0,0,0}},
        {"Mg2+", 2, {0,1,0,0,0,0,0,0}},
        {"Cl-", -1, {0,0,1,0,0,0,0,0}},
        {"E", 0, {0,0,0,0,0,0,0,1}},
        {"E:Li", 1, {1,0,0,0,0,0,0,1}},
        {"E:Mg", 2, {0,1,0,0,0,0,0,1}},
        {"inositol-monophosphate(2-)", -2, {0,0,0,6,11,9,1,0}},
        {"inositol", 0, {0,0,0,6,12,6,0,0}},
        {"HPO4(2-)", -2, {0,0,0,0,1,4,1,0}},
        {"water", 0, {0,0,0,0,2,1,0,0}},
        {"Na+", 1, {0,0,0,0,0,0,0,0,1}}
    }};
    return definitions.at(static_cast<std::size_t>(s));
}

class Compartment {
    Picolitres volume_;
    std::array<double, species_count> amounts_{}; // femtomoles; mM * pL = fmol
public:
    explicit Compartment(Picolitres volume) : volume_(volume) {}
    double volume_pl() const { return volume_.value; }
    double amount_fmol(Species s) const { return amounts_.at(static_cast<std::size_t>(s)); }
    double concentration_mm(Species s) const { return amount_fmol(s) / volume_.value; }
    // Preparation is explicit; subsequent evolution uses transfers and reactions.
    void prepare(Species s, Millimolar concentration) {
        amounts_.at(static_cast<std::size_t>(s)) = finite(concentration.value * volume_.value);
    }
    Inventory inventory() const {
        Inventory result{};
        for (std::size_t i=0; i<species_count; ++i)
            for (std::size_t j=0; j<result.size(); ++j)
                result[j] += amounts_[i] * definition(static_cast<Species>(i)).composition[j];
        return result;
    }
    double charge_fmol_e() const {
        double charge=0;
        for (std::size_t i=0; i<species_count; ++i)
            charge += amounts_[i] * definition(static_cast<Species>(i)).charge;
        return charge;
    }
    void transfer_to(Compartment& other, Species s, double amount_fmol) {
        nonnegative(amount_fmol);
        if (this == &other) return;
        auto i = static_cast<std::size_t>(s);
        if (amount_fmol > amounts_.at(i)) throw std::invalid_argument("Insufficient species");
        const double destination = finite(other.amounts_.at(i) + amount_fmol);
        amounts_[i] -= amount_fmol;
        other.amounts_[i] = destination;
    }
    // A checked stoichiometric reaction. Positive extent is in femtomoles.
    void react(const std::array<int, species_count>& stoichiometry, double extent_fmol) {
        nonnegative(extent_fmol);
        Inventory balance{};
        int charge=0;
        auto next=amounts_;
        for (std::size_t i=0; i<species_count; ++i) {
            const auto& d=definition(static_cast<Species>(i));
            charge += stoichiometry[i] * d.charge;
            for (std::size_t j=0; j<balance.size(); ++j)
                balance[j] += stoichiometry[i] * d.composition[j];
            next[i]=finite(amounts_[i] + stoichiometry[i] * extent_fmol);
            if (next[i] < 0) throw std::invalid_argument("Reaction would exhaust a reactant");
        }
        if (charge != 0 || std::any_of(balance.begin(), balance.end(),
                                      [](double x){ return x != 0; }))
            throw std::invalid_argument("Reaction does not conserve atoms, site moieties and charge");
        amounts_=next;
    }
};

inline std::array<int, species_count> binding_reaction(Species ion, Species bound) {
    std::array<int, species_count> stoich{};
    stoich.at(static_cast<std::size_t>(ion))=-1;
    stoich.at(static_cast<std::size_t>(Species::Site))=-1;
    stoich.at(static_cast<std::size_t>(bound))=1;
    return stoich;
}

struct BindingRates {
    double association_per_mm_second=1;
    double dissociation_per_second=1;
    void validate() const {
        nonnegative(association_per_mm_second); nonnegative(dissociation_per_second);
    }
};

// Backward-Euler mass action for one reversible binding reaction. Bisection on
// feasible extent preserves positivity and inventory even for stiff rates.
inline void bind(Compartment& c, Species ion, Species bound,
                 const BindingRates& rates, Seconds dt) {
    rates.validate();
    const auto stoich=binding_reaction(ion,bound);
    // Validate species combination even if dt=0 or no reaction occurs.
    c.react(stoich,0);
    if (dt.value==0) return;
    const double a=c.concentration_mm(ion), e=c.concentration_mm(Species::Site);
    const double b=c.concentration_mm(bound);
    double lo=-b, hi=std::min(a,e);
    for (int i=0; i<80; ++i) {
        const double x=lo+(hi-lo)*0.5;
        const double residual=x-dt.value*(rates.association_per_mm_second*(a-x)*(e-x)
                                          -rates.dissociation_per_second*(b+x));
        finite(residual);
        if (residual>0) hi=x; else lo=x;
    }
    const double x=lo+(hi-lo)*0.5;
    // Work in amounts and clamp only the rounding at a feasible boundary.
    const double extent=std::min(std::abs(x)*c.volume_pl(), x>=0
        ? std::min(c.amount_fmol(ion),c.amount_fmol(Species::Site)) : c.amount_fmol(bound));
    auto direction=stoich;
    if (x<0) for (auto& coefficient:direction) coefficient=-coefficient;
    c.react(direction,extent);
}

// Passive electroneutral LiCl exchange, not a voltage-gated sodium channel.
// Ideal-solution reversible pair flux is proportional to the difference of
// Li*Cl concentration products. It follows salt chemical potential, not merely
// the Li gradient. No membrane potential or channel selectivity yet.
inline void exchange_licl(Compartment& a, Compartment& b,
                          double conductance_pl_per_mm_second, Seconds dt) {
    nonnegative(conductance_pl_per_mm_second);
    if (&a==&b || dt.value==0 || conductance_pl_per_mm_second==0) return;
    const double al=a.amount_fmol(Species::Lithium),ac=a.amount_fmol(Species::Chloride);
    const double bl=b.amount_fmol(Species::Lithium),bc=b.amount_fmol(Species::Chloride);
    double lo=-std::min(bl,bc),hi=std::min(al,ac);
    for (int i=0;i<80;++i) {
        const double x=lo+(hi-lo)*0.5;
        const double force=(al-x)/a.volume_pl()*(ac-x)/a.volume_pl()
                          -(bl+x)/b.volume_pl()*(bc+x)/b.volume_pl();
        const double residual=finite(x-dt.value*conductance_pl_per_mm_second*force);
        if (residual>0) hi=x; else lo=x;
    }
    const double signed_amount=lo+(hi-lo)*0.5;
    auto& from=signed_amount>=0 ? a:b;
    auto& to=signed_amount>=0 ? b:a;
    const double amount=std::min({std::abs(signed_amount),from.amount_fmol(Species::Lithium),
                                  from.amount_fmol(Species::Chloride)});
    from.transfer_to(to,Species::Lithium,amount);
    from.transfer_to(to,Species::Chloride,amount);
}

struct ImpaseRates {
    double vmax_mm_per_second=0.02;
    double km_mm=0.1;
    double lithium_ki_mm=1;
    void validate() const {
        nonnegative(vmax_mm_per_second);
        if (nonnegative(km_mm)==0 || nonnegative(lithium_ki_mm)==0)
            throw std::invalid_argument("Km and Ki must be positive");
    }
};
inline double impase_rate(const Compartment& c,const ImpaseRates& rates) {
    rates.validate();
    const double s=c.concentration_mm(Species::InositolMonophosphate);
    return finite(rates.vmax_mm_per_second*s/(rates.km_mm
        +(1+c.concentration_mm(Species::Lithium)/rates.lithium_ki_mm)*s));
}
inline void hydrolyze(Compartment& c,const ImpaseRates& rates,Seconds dt) {
    rates.validate();
    if (dt.value==0 || rates.vmax_mm_per_second==0) return;
    // Implicit depletion with Li fixed during this substep; effective irreversible
    // kinetics, fixed protonation states. No PIP2/IP3/calcium cycle is claimed.
    double lo=0,hi=std::min(c.amount_fmol(Species::InositolMonophosphate),
                           c.amount_fmol(Species::Water));
    for (int i=0;i<80;++i) {
        const double x=lo+(hi-lo)*0.5;
        const double s=(c.amount_fmol(Species::InositolMonophosphate)-x)/c.volume_pl();
        const double v=rates.vmax_mm_per_second*s/(rates.km_mm
            +(1+c.concentration_mm(Species::Lithium)/rates.lithium_ki_mm)*s);
        if (x-dt.value*v*c.volume_pl()>0) hi=x; else lo=x;
    }
    std::array<int,species_count> stoich{};
    stoich[static_cast<std::size_t>(Species::InositolMonophosphate)]=-1;
    stoich[static_cast<std::size_t>(Species::Water)]=-1;
    stoich[static_cast<std::size_t>(Species::Inositol)]=1;
    stoich[static_cast<std::size_t>(Species::Phosphate)]=1;
    c.react(stoich,lo+(hi-lo)*0.5);
}

// All defaults below are illustrative, not measured or clinically fitted.
struct PhysiologyParameters {
    BindingRates magnesium_binding{2,1};
    BindingRates lithium_binding{1,1};
    ImpaseRates impase;
    double salt_conductance_pl_per_mm_second=0.1;
    double kinase_gain=1;
    double inositol_gain=1;
    double basal_drive=0.1;
    double inositol_half_mm=0.1;
    double response_time_seconds=5;
    void validate() const {
        magnesium_binding.validate(); lithium_binding.validate(); impase.validate();
        nonnegative(salt_conductance_pl_per_mm_second);
        nonnegative(kinase_gain); nonnegative(inositol_gain); nonnegative(basal_drive);
        if (nonnegative(inositol_half_mm)==0 || nonnegative(response_time_seconds)==0)
            throw std::invalid_argument("Response scales must be positive");
    }
};
struct PhysiologySnapshot {
    double time_seconds;
    double lithium_inside_mm;
    double productive_site_fraction;
    double impase_flux_mm_per_second;
    double inositol_mm;
    double response_proxy;
};

// A declared reference range for the synthetic proxy, not a clinical norm.
class OperatingRange {
    double lower_,upper_;
public:
    OperatingRange(double lower,double upper) : lower_(finite(lower)),upper_(finite(upper)) {
        if (lower>upper) throw std::invalid_argument("Reversed operating range");
    }
    double distance(double response) const {
        finite(response);
        return finite(std::max({lower_-response,0.0,response-upper_}));
    }
};

class LithiumPhysiology {
    Compartment outside_,inside_;
    PhysiologyParameters parameters_;
    double time_=0, response_=0;
public:
    LithiumPhysiology(Compartment outside,Compartment inside,PhysiologyParameters parameters={})
        : outside_(std::move(outside)),inside_(std::move(inside)),parameters_(parameters) {
        parameters_.validate();
    }
    const Compartment& outside() const { return outside_; }
    const Compartment& inside() const { return inside_; }
    Inventory inventory() const {
        auto result=outside_.inventory(); const auto inner=inside_.inventory();
        for (std::size_t i=0;i<result.size();++i) result[i]+=inner[i];
        return result;
    }
    double total_charge_fmol_e() const { return outside_.charge_fmol_e()+inside_.charge_fmol_e(); }
    PhysiologySnapshot snapshot() const {
        const double free=inside_.amount_fmol(Species::Site);
        const double productive=inside_.amount_fmol(Species::MagnesiumSite);
        const double total=free+productive+inside_.amount_fmol(Species::LithiumSite);
        return {time_,inside_.concentration_mm(Species::Lithium),total==0?0:productive/total,
            impase_rate(inside_,parameters_.impase),inside_.concentration_mm(Species::Inositol),response_};
    }
    void advance(Seconds duration,Seconds max_step=Seconds(0.01)) {
        if (max_step.value==0) throw std::invalid_argument("Step must be positive");
        const double count=std::ceil(duration.value/max_step.value);
        if (!std::isfinite(count) || count>10000000)
            throw std::invalid_argument("Too many integration steps");
        if (count==0) return;
        const double final_time=finite(time_+duration.value);
        const Seconds dt(duration.value/count);
        for (std::size_t i=0;i<static_cast<std::size_t>(count);++i) {
            exchange_licl(outside_,inside_,parameters_.salt_conductance_pl_per_mm_second,dt);
            bind(inside_,Species::Magnesium,Species::MagnesiumSite,parameters_.magnesium_binding,dt);
            bind(inside_,Species::Lithium,Species::LithiumSite,parameters_.lithium_binding,dt);
            hydrolyze(inside_,parameters_.impase,dt);
            const auto s=snapshot();
            const double target=finite(parameters_.basal_drive
                +parameters_.kinase_gain*s.productive_site_fraction
                +parameters_.inositol_gain*s.inositol_mm/(parameters_.inositol_half_mm+s.inositol_mm));
            response_=finite(response_+(target-response_)*(-std::expm1(-dt.value/parameters_.response_time_seconds)));
        }
        time_=final_time;
    }
};

// Synthetic preparation. LiCl is added to an otherwise fixed preparation.
// Sodium is retained as a nontransported counterion in this prototype. No
// sodium competition, water transport, or osmotic volume response is included.
inline LithiumPhysiology illustrative_physiology(Millimolar external_lithium,
                                                 PhysiologyParameters parameters={}) {
    Compartment outside(Picolitres(10)),inside(Picolitres(1));
    outside.prepare(Species::Lithium,external_lithium);
    outside.prepare(Species::Chloride,external_lithium);
    inside.prepare(Species::Magnesium,Millimolar(1));
    inside.prepare(Species::Chloride,Millimolar(2));
    inside.prepare(Species::Site,Millimolar(0.01));
    inside.prepare(Species::InositolMonophosphate,Millimolar(0.2));
    inside.prepare(Species::Inositol,Millimolar(0.05));
    inside.prepare(Species::Sodium,Millimolar(0.4)); // balances substrate charge
    outside.prepare(Species::Water,Millimolar(55500));
    inside.prepare(Species::Water,Millimolar(55500));
    return LithiumPhysiology(outside,inside,parameters);
}

} // namespace virtual_cell::bio
