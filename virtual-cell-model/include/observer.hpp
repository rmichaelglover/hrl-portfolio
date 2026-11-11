#pragma once
#include "bioelectric.hpp"
#include <map>

namespace virtual_cell::mind {
enum class Integration { Permit, Decline };
struct Intention { double attention=1;Integration integration=Integration::Permit; };
// A bounded operational Will: chosen attention/integration policy. It does not
// adjudicate immune rejection, tissue survival, receptor chemistry or tolerability.
class Will {
    Intention intention_;
public:
    void intend(double attention,Integration integration=Integration::Permit) {
        electric::detail::nonnegative(attention);
        if(attention>1)throw std::invalid_argument("Attention exceeds one");
        intention_={attention,integration};
    }
    const Intention& intention() const { return intention_; }
};
struct BoundaryObservation {
    std::size_t visual_events=0,interoceptive_events=0;
    double duration_ms=1000;
};
struct BoundaryLikelihoods {
    double external_visual_mean=12,internal_visual_mean=2;
    double external_interoceptive_mean=2,internal_interoceptive_mean=8;
    void validate() const {
        for(double x:{external_visual_mean,internal_visual_mean,external_interoceptive_mean,internal_interoceptive_mean})
            electric::detail::positive(x);
    }
};
class BoundaryObserver {
    BoundaryLikelihoods likelihoods_;
    double external_prior_;
public:
    explicit BoundaryObserver(BoundaryLikelihoods likelihoods={},double external_prior=.5)
        : likelihoods_(likelihoods),external_prior_(external_prior) {
        likelihoods_.validate();electric::detail::checked(external_prior);
        if(external_prior<=0 || external_prior>=1)throw std::invalid_argument("Prior must be strictly between zero and one");
    }
    double probability_external(const BoundaryObservation& o) const {
        const double seconds=electric::detail::positive(o.duration_ms)/1000;
        const auto& p=likelihoods_;
        const double log_odds=std::log(external_prior_)-std::log1p(-external_prior_)
            +o.visual_events*std::log(p.external_visual_mean/p.internal_visual_mean)
            -(p.external_visual_mean-p.internal_visual_mean)*seconds
            +o.interoceptive_events*std::log(p.external_interoceptive_mean/p.internal_interoceptive_mean)
            -(p.external_interoceptive_mean-p.internal_interoceptive_mean)*seconds;
        if(log_odds>=0)return 1/(1+std::exp(-log_odds));
        const double odds=std::exp(log_odds);return odds/(1+odds);
    }
};
class AttendedSelfModel {
    std::map<std::string,double> features_;
    std::map<std::string,std::string> definitions_;
public:
    double feature(const std::string& name) const {
        const auto found=features_.find(name);return found==features_.end()?0:found->second;
    }
    bool active(const std::string& name) const { return features_.count(name)!=0; }
    bool defined(const std::string& name) const { return definitions_.count(name)!=0; }
    void retire(const std::string& name) { features_.erase(name); }
    void integrate(const std::string& name,double perceived_value,const Will& will,double learning_rate=.1) {
        electric::detail::checked(perceived_value);electric::detail::nonnegative(learning_rate);
        if(learning_rate>1)throw std::invalid_argument("Learning rate exceeds one");
        const auto& intention=will.intention();
        if(intention.integration==Integration::Decline || intention.attention==0)return;
        const double previous=feature(name);
        definitions_.emplace(name,"Attended estimate of "+name);
        features_[name]=electric::detail::checked(previous+learning_rate*intention.attention*(perceived_value-previous));
    }
};
} // namespace virtual_cell::mind
