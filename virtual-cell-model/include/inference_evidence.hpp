#pragma once
#include "observer.hpp"
#include <utility>

namespace virtual_cell::mind {
// Different measures remain different types even when their ranges coincide.
class FuzzyMembership {
    double value_;
public:
    explicit FuzzyMembership(double value):value_(electric::detail::checked(value)) {
        if(value<0 || value>1)throw std::invalid_argument("Membership outside [0,1]");
    }
    double value() const { return value_; }
};
struct BoundaryEvidence {
    BoundaryObservation observation;
    double bayesian_external_probability;
    FuzzyMembership visually_active;
    FuzzyMembership bodily_active;
    std::string provenance;
};
class EvidenceEncoder {
    BoundaryObserver observer_;
    double visual_half_rate_,bodily_half_rate_;
public:
    explicit EvidenceEncoder(BoundaryObserver observer=BoundaryObserver{},double visual_half_rate=5,
                             double bodily_half_rate=5)
        :observer_(std::move(observer)),
         visual_half_rate_(electric::detail::positive(visual_half_rate)),
         bodily_half_rate_(electric::detail::positive(bodily_half_rate)) {}
    BoundaryEvidence encode(BoundaryObservation observation,std::string provenance) const {
        if(provenance.empty())throw std::invalid_argument("Evidence requires provenance");
        const double seconds=electric::detail::positive(observation.duration_ms)/1000;
        const double v=observation.visual_events/seconds,b=observation.interoceptive_events/seconds;
        return {observation,observer_.probability_external(observation),
                FuzzyMembership(v/(v+visual_half_rate_)),
                FuzzyMembership(b/(b+bodily_half_rate_)),std::move(provenance)};
    }
};
// This is evidence for inference, not a physical command or a change of Will.
} // namespace virtual_cell::mind
