#pragma once
#include "bioelectric.hpp"
#include <array>
#include <cstdint>
#include <random>

namespace virtual_cell::vision {
inline constexpr double planck_js=6.62607015e-34;
inline constexpr double light_m_per_s=299792458.0;
inline constexpr double pi=3.14159265358979323846;
inline double photon_energy_j(double wavelength_nm) {
    electric::detail::positive(wavelength_nm);
    return electric::detail::positive(planck_js*light_m_per_s/(wavelength_nm*1e-9));
}
struct Position { double x=0,y=0,z=0; };
inline void validate(Position p) {
    electric::detail::checked(p.x);electric::detail::checked(p.y);electric::detail::checked(p.z);
}

// A physical, classical frame: local eye position and forward axis in world coordinates.
// This class does not implement a quantum reference-frame transformation.
class ReferenceFrame {
    Position origin_;
    double yaw_radians_;
public:
    explicit ReferenceFrame(Position origin={},double yaw_radians=0)
        : origin_(origin),yaw_radians_(electric::detail::checked(yaw_radians)) { validate(origin_); }
    Position origin() const { return origin_; }
    double yaw_radians() const { return yaw_radians_; }
    double forward_cosine(Position point) const {
        validate(point);
        const double dx=point.x-origin_.x,dy=point.y-origin_.y,dz=point.z-origin_.z;
        const double distance=std::hypot(std::hypot(dx,dy),dz);
        if(distance==0) return -1;
        return (dx*std::sin(yaw_radians_)+dz*std::cos(yaw_radians_))/distance;
    }
};
struct Emitter {
    std::string name;
    Position position;
    double radiant_power_w=1e-9;
    double wavelength_nm=500;
};
class Environment {
    std::vector<Emitter> emitters_;
public:
    void add(Emitter emitter) {
        validate(emitter.position);electric::detail::nonnegative(emitter.radiant_power_w);
        photon_energy_j(emitter.wavelength_nm);
        emitters_.push_back(std::move(emitter));
    }
    const auto& emitters() const { return emitters_; }
};
struct Optics {
    double pupil_diameter_m=.003;
    double transmission=.8;
    double peak_conversion_probability=.5;
    double spectral_peak_nm=500;
    double spectral_width_nm=70;
    double half_field_radians=pi/3;
    void validate() const {
        electric::detail::positive(pupil_diameter_m);
        electric::detail::nonnegative(transmission);electric::detail::nonnegative(peak_conversion_probability);
        if(transmission>1 || peak_conversion_probability>1)throw std::invalid_argument("Optical probability exceeds one");
        electric::detail::positive(spectral_peak_nm);electric::detail::positive(spectral_width_nm);
        electric::detail::positive(half_field_radians);
        if(half_field_radians>pi/2)throw std::invalid_argument("Pupil field must face forward");
    }
};
struct OpticalAudit {
    std::uint64_t incident_photons=0,transmitted_photons=0,photoisomerizations=0;
    double incident_energy_j=0;
};
inline std::uint64_t poisson(double mean,std::mt19937_64& rng) {
    electric::detail::nonnegative(mean);
    if(mean==0) return 0;
    if(mean>1e8)throw std::invalid_argument("Photon/event count outside prototype range");
    return std::poisson_distribution<std::uint64_t>(mean)(rng);
}

class OpticalWindow {
    ReferenceFrame frame_;
    Optics optics_;
    bool open_=true;
public:
    explicit OpticalWindow(ReferenceFrame frame=ReferenceFrame{},Optics optics={}) : frame_(frame),optics_(optics) { optics_.validate(); }
    const ReferenceFrame& frame() const { return frame_; }
    void set_frame(ReferenceFrame frame) { frame_=frame; }
    void set_open(bool open) { open_=open; }
    bool is_open() const { return open_; }
    // Isotropic point-source, small-aperture far-field approximation. Values are
    // photon arrivals per second, before transmission/photopigment conversion.
    double incident_rate(const Emitter& emitter) const {
        validate(emitter.position);electric::detail::nonnegative(emitter.radiant_power_w);
        const double energy=photon_energy_j(emitter.wavelength_nm);
        const auto origin=frame_.origin();
        const double distance=std::hypot(std::hypot(emitter.position.x-origin.x,emitter.position.y-origin.y),emitter.position.z-origin.z);
        if(distance<10*optics_.pupil_diameter_m)
            throw std::invalid_argument("Emitter too close for small-aperture far-field model");
        const double cosine=frame_.forward_cosine(emitter.position);
        if(!open_ || cosine<std::cos(optics_.half_field_radians))return 0;
        const double area=pi*optics_.pupil_diameter_m*optics_.pupil_diameter_m/4;
        return electric::detail::nonnegative(emitter.radiant_power_w/energy*area*cosine/(4*pi*distance*distance));
    }
    double expected_incident(const Environment& environment,double dt_ms) const {
        electric::detail::nonnegative(dt_ms);double expected=0;
        for(const auto& emitter:environment.emitters())expected=electric::detail::checked(expected+incident_rate(emitter)*dt_ms/1000);
        return expected;
    }
    OpticalAudit sample(const Environment& environment,double dt_ms,std::mt19937_64& rng) const {
        electric::detail::nonnegative(dt_ms);OpticalAudit audit;
        for(const auto& emitter:environment.emitters()) {
            const auto incident=poisson(incident_rate(emitter)*dt_ms/1000,rng);
            const auto transmitted=std::binomial_distribution<std::uint64_t>(incident,optics_.transmission)(rng);
            const double offset=(emitter.wavelength_nm-optics_.spectral_peak_nm)/optics_.spectral_width_nm;
            const double probability=optics_.peak_conversion_probability*std::exp(-.5*offset*offset);
            const auto converted=std::binomial_distribution<std::uint64_t>(transmitted,probability)(rng);
            audit.incident_photons+=incident;audit.transmitted_photons+=transmitted;audit.photoisomerizations+=converted;
            audit.incident_energy_j=electric::detail::checked(audit.incident_energy_j+incident*photon_energy_j(emitter.wavelength_nm));
        }
        return audit;
    }
};

struct RodParameters {
    double rhodopsin_decay_ms=50,pde_decay_ms=50,cgmp_recovery_ms=100;
    double pde_gain_per_ms=.03;
    double dark_cng_ns=1.5,cgmp_half=.5,hill=3;
    double dark_event_rate_per_second=.006; // primate-inspired starting value; not a human fit
    void validate() const {
        for(double x:{rhodopsin_decay_ms,pde_decay_ms,cgmp_recovery_ms,cgmp_half,hill})electric::detail::positive(x);
        electric::detail::nonnegative(pde_gain_per_ms);electric::detail::nonnegative(dark_cng_ns);
        electric::detail::nonnegative(dark_event_rate_per_second);
    }
};
// Reduced opsin -> PDE -> normalized cGMP -> CNG conductance, not an atomistic
// cascade or a fitted human photoreceptor. Endogenous events enter the same state.
class RodTransduction {
    RodParameters parameters_;
    double active_opsin_=0,pde_=0,cgmp_=1;
public:
    explicit RodTransduction(RodParameters parameters={}) : parameters_(parameters) { parameters_.validate(); }
    double cgmp() const { return cgmp_; }
    double cng_ns() const {
        const double normalized=std::pow(cgmp_,parameters_.hill);
        const double half=std::pow(parameters_.cgmp_half,parameters_.hill);
        return parameters_.dark_cng_ns*(1+half)*normalized/(normalized+half);
    }
    void advance(double dt_ms,std::uint64_t events) {
        electric::detail::nonnegative(dt_ms);
        if(dt_ms==0) {if(events)throw std::invalid_argument("Events need a positive interval");return;}
        active_opsin_=electric::detail::checked(active_opsin_+static_cast<double>(events));
        const double r_average=active_opsin_*(-std::expm1(-dt_ms/parameters_.rhodopsin_decay_ms))/(dt_ms/parameters_.rhodopsin_decay_ms);
        active_opsin_*=std::exp(-dt_ms/parameters_.rhodopsin_decay_ms);
        const double target=parameters_.pde_gain_per_ms*r_average*parameters_.pde_decay_ms;
        pde_=electric::detail::nonnegative(pde_+(target-pde_)*(-std::expm1(-dt_ms/parameters_.pde_decay_ms)));
        const double equilibrium=1/(1+pde_);
        cgmp_=electric::detail::nonnegative(cgmp_+(equilibrium-cgmp_)*(-std::expm1(-dt_ms*(1+pde_)/parameters_.cgmp_recovery_ms)));
    }
    std::uint64_t sample_endogenous(double dt_ms,std::mt19937_64& rng) const {
        electric::detail::nonnegative(dt_ms);
        return poisson(parameters_.dark_event_rate_per_second*dt_ms/1000,rng);
    }
};
} // namespace virtual_cell::vision
