#pragma once
#include "bioelectric.hpp"
#include <random>
namespace virtual_cell::prediction {
enum class Memory {Instantaneous,Filtered,Predictive};
class Observer {
    Memory mode_;
    double filtered_=0;
    bool initialized_=false;
public:
    explicit Observer(Memory mode):mode_(mode) {}
    double forecast(double sensed,double dt=.1,double horizon=1) {
        electric::detail::positive(sensed);electric::detail::positive(dt);electric::detail::nonnegative(horizon);
        if(!initialized_){filtered_=std::log(sensed);initialized_=true;}
        double prediction=sensed;
        if(mode_!=Memory::Instantaneous){
            const double old=filtered_;
            filtered_+=(-std::expm1(-dt))*(std::log(sensed)-filtered_);
            const double velocity=std::clamp((filtered_-old)/dt,-.5,.5);
            prediction=std::exp(filtered_+(mode_==Memory::Predictive?horizon*velocity:0));
        }
        return std::clamp(prediction,.15,6.0);
    }
};
struct Ledger {double before,incoming,outgoing,after,atp_fmol;};
class Compartment {
    double amount_;
public:
    explicit Compartment(double amount=1):amount_(electric::detail::nonnegative(amount)) {}
    Ledger advance(double influx,double dt) {
        electric::detail::nonnegative(influx);electric::detail::positive(dt);
        const double before=amount_,incoming=influx*dt;
        amount_=amount_*std::exp(-dt)+influx*(-std::expm1(-dt));
        return {before,incoming,before+incoming-amount_,amount_,incoming};
    }
};
} // namespace virtual_cell::prediction
