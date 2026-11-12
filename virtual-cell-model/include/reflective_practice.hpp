#pragma once
#include "objectives.hpp"
namespace virtual_cell::mind {
enum class ReflectiveReward : std::size_t { HealthSupport,Happiness,Knowledge,Good,Count };
struct Mantra {
    std::string words,attribution,provenance;
    ReflectiveReward reward;
};
class ReflectivePractice {
    std::array<std::size_t,4> counters_{};
    std::vector<Mantra> recollections_;
    double musical_attention_=1;
    std::size_t context_revisions_=0;
    std::vector<std::string> musical_contexts_;
public:
    void say(Mantra mantra) {
        if(mantra.words.empty() || mantra.provenance.empty())throw std::invalid_argument("Mantra needs content and provenance");
        auto index=static_cast<std::size_t>(mantra.reward);
        if(index>=counters_.size())throw std::invalid_argument("Unknown reflective reward");
        // An explicit scenario reward, not a measured physiological improvement.
        recollections_.push_back(std::move(mantra));++counters_[index];
    }
    std::size_t count(ReflectiveReward reward) const {return counters_.at(static_cast<std::size_t>(reward));}
    void revise_musical_context(double attention,std::string context="new contextual interpretation") {
        if(nonnegative(attention)>1)throw std::invalid_argument("Attention outside [0,1]");
        if(context.empty())throw std::invalid_argument("Context requires a description");
        musical_contexts_.push_back(std::move(context));
        musical_attention_=attention;++context_revisions_;
    }
    const auto& musical_contexts() const {return musical_contexts_;}
    double music_attention() const {return musical_attention_;}
    std::size_t context_revisions() const {return context_revisions_;}
    const auto& recollections() const {return recollections_;}
};
inline Mantra flowers_mantra(ReflectiveReward reward=ReflectiveReward::Happiness) {
    return {"There are always flowers, for those who choose to see.",
            "Attributed to Henri Matisse; remembered wording",
            "Michael's supplied quotation; exact historical wording and occasion unverified",reward};
}
} // namespace virtual_cell::mind
