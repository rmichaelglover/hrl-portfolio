#pragma once
#include "seeing_person.hpp"
#include <queue>
#include <set>
#include <tuple>

namespace virtual_cell::household {
struct Place {
    int x=0,z=0;
    bool operator<(Place other) const {return std::tie(x,z)<std::tie(other.x,other.z);}
    bool operator==(Place other) const {return x==other.x && z==other.z;}
};
// Occupancy is a learned map input, not a view into unobserved world geometry.
class SubjectiveMap {
public:
    struct Landmark {double x,z,variance;double last_seen_seconds;std::string source;};
private:
    double x_=0,z_=0,yaw_=0,pose_variance_=.01;
    std::map<std::string,Landmark> landmarks_;
    std::set<Place> known_free_;
public:
    void odometry(double forward,double turn,double variance) {
        finite(forward);finite(turn);nonnegative(variance);
        yaw_+=turn;x_+=forward*std::sin(yaw_);z_+=forward*std::cos(yaw_);
        pose_variance_+=variance;
    }
    void observe(std::string identity,double range,double bearing,double variance,
                 double seconds,std::string source) {
        if(identity.empty() || source.empty())throw std::invalid_argument("Landmark requires identity and source");
        nonnegative(range);finite(bearing);nonnegative(seconds);
        if(nonnegative(variance)==0)throw std::invalid_argument("Measurement variance must be positive");
        const double x=x_+range*std::sin(yaw_+bearing),z=z_+range*std::cos(yaw_+bearing);
        const double total=variance+pose_variance_;
        auto found=landmarks_.find(identity);
        if(found==landmarks_.end())landmarks_.emplace(identity,Landmark{x,z,total,seconds,std::move(source)});
        else {
            auto& l=found->second;
            if(seconds<l.last_seen_seconds)throw std::invalid_argument("Out-of-order landmark observation");
            // Conservative replacement: correlated pose errors are not independent fixes.
            l={x,z,total,seconds,std::move(source)};
        }
    }
    void remember(std::string identity,double x,double z,double variance,std::string source) {
        finite(x);finite(z);
        if(identity.empty() || source.empty() || nonnegative(variance)==0)
            throw std::invalid_argument("Invalid remembered landmark");
        landmarks_.insert_or_assign(identity,Landmark{x,z,variance,-1,std::move(source)});
    }
    bool visible_recently(const std::string& identity,double now,double max_age=1) const {
        nonnegative(now);nonnegative(max_age);
        const auto i=landmarks_.find(identity);
        return i!=landmarks_.end() && i->second.last_seen_seconds>=0 &&
               now>=i->second.last_seen_seconds && now-i->second.last_seen_seconds<=max_age;
    }
    const auto& landmarks() const {return landmarks_;}
    vision::ReferenceFrame eye_frame(double side) const {
        finite(side);
        return vision::ReferenceFrame({x_+side*std::cos(yaw_),0,z_-side*std::sin(yaw_)},yaw_);
    }
    double pose_variance() const {return pose_variance_;}
    void mark_free(Place cell) {known_free_.insert(cell);}
    std::vector<Place> route(Place start,Place goal) const {
        if(!known_free_.count(start) || !known_free_.count(goal))return {};
        std::queue<Place> q;std::map<Place,Place> previous;
        q.push(start);previous.emplace(start,start);
        while(!q.empty()) {
            const auto p=q.front();q.pop();if(p==goal)break;
            for(auto d:std::array<Place,4>{{{1,0},{-1,0},{0,1},{0,-1}}}) {
                Place next{p.x+d.x,p.z+d.z};
                if(known_free_.count(next) && !previous.count(next)) {previous.emplace(next,p);q.push(next);}
            }
        }
        if(!previous.count(goal))return {};
        std::vector<Place> result;
        for(auto p=goal;;p=previous.at(p)) {result.push_back(p);if(p==start)break;}
        std::reverse(result.begin(),result.end());return result;
    }
};

struct Preferences {
    double conversation=0,quiet=1,music=0,appetite=.1,sweetness=.6,thirst=.3;
    void validate() const {
        for(double v:{conversation,quiet,music,appetite,sweetness,thirst})
            if(nonnegative(v)>1)throw std::invalid_argument("Preference outside [0,1]");
    }
};
// A parent owns preferences. Alex learns responses; visibility is not availability.
class HouseholdPerson {
    std::string name_;
    Preferences preferences_;
    bool occupied_;
public:
    HouseholdPerson(std::string name,Preferences p,bool occupied=false)
        :name_(std::move(name)),preferences_(p),occupied_(occupied) {preferences_.validate();}
    const auto& name() const {return name_;}
    bool answer_conversation_invitation() const {return !occupied_ && preferences_.conversation>.5;}
    bool answer_audible_music_request() const {return !occupied_ && preferences_.music>preferences_.quiet;}
    bool wants_meal() const {return preferences_.appetite>.5;}
    bool wants_roll() const {return preferences_.sweetness>.5;}
    bool wants_drink() const {return preferences_.thirst>.5;}
};
struct OtherModel {
    std::optional<bool> conversation_permission,audible_music_permission;
    bool currently_visible=false;
    // No private preference lookup: only explicitly supplied replies update beliefs.
    void hear_conversation_reply(bool yes) {conversation_permission=yes;}
    void hear_music_reply(bool yes) {audible_music_permission=yes;}
};
struct Needs {
    double hunger=.1,pleasant_food=.9,eating_effort=.2;
    double concentration=.7,relaxation=.3;
    void validate() const {
        for(double x:{hunger,pleasant_food,eating_effort,concentration,relaxation})
            if(nonnegative(x)>1)throw std::invalid_argument("Need outside [0,1]");
    }
};
struct MusicPractice {
    std::string title="Yesterday",artist="The Beatles";
    double guitar=.85,voice=.3,lyric_recall=.1;
    double incidental_learning=0,procedural_consolidation=0;
    // Numerical learning rates are explicit scenario assumptions, not fitted biology.
    void advance(double minutes,const Needs& needs,bool sing,bool recall,bool guitar_practice) {
        nonnegative(minutes);needs.validate();
        const double attention=.01+.04*needs.concentration;
        const double motor=.005+.015*needs.relaxation;
        incidental_learning+=minutes*(.001+.004*needs.concentration);
        procedural_consolidation+=minutes*(.001+.004*needs.relaxation);
        if(recall)lyric_recall+= (1-lyric_recall)*(-std::expm1(-minutes*attention));
        if(sing)voice+=(1-voice)*(-std::expm1(-minutes*attention));
        if(guitar_practice)guitar+=(1-guitar)*(-std::expm1(-minutes*motor));
    }
};
struct Activity {
    mind::Candidate candidate;
    double joy=0,peace=0,stimulation=0,autonomy=0;
};
inline std::vector<Activity> activities(const Needs& n,const OtherModel& papa,const OtherModel& mama) {
    n.validate();
    const bool music_ok=papa.audible_music_permission.value_or(false) &&
                        mama.audible_music_permission.value_or(false);
    const double eating=.6*n.hunger;
    // Five existing objective dimensions remain visible. Extra qualities are reported,
    // combined only under an explicitly chosen household policy.
    return {
        {{"Listen with headphones",mind::ObjectiveVector({.1,.1,.1,.3,0}),.1,true},.8,.9,.5,.5},
        {{"Quiet lyric recall",mind::ObjectiveVector({.1,.1,.1,.8,0}),.2,true},.6,.9,.6,.6},
        {{"Guitar and voice practice",mind::ObjectiveVector({.2,.1,.2,.7,0}),.5,music_ok},.9,.4,.9,.7},
        {{"Eat Singaporean noodle leftovers",mind::ObjectiveVector({eating,.1,.1,0,-.1}),n.eating_effort,true},n.pleasant_food-.4*n.eating_effort,.7,.3,.4},
        {{"Ask Papa about a conversation",mind::ObjectiveVector({.1,.1,.6,.2,0}),.1,papa.currently_visible && !papa.conversation_permission.has_value()},.5,.7,.4,.5},
        {{"Talk with Papa",mind::ObjectiveVector({.2,.1,.9,.3,0}),.2,papa.currently_visible && papa.conversation_permission.value_or(false)},.8,.8,.6,.5},
        {{"Contact Mama to ask availability",mind::ObjectiveVector({.1,.1,.5,.1,0}),.1,true},.5,.8,.3,.5},
        {{"Focused paid-work preparation",mind::ObjectiveVector({.1,.4,.1,.7,.8}),.6,true},.3,.6,.7,.9},
        {{"Rest quietly",mind::ObjectiveVector({.5,.1,.1,.05,0}),0,true},.5,1,.1,.5}
    };
}
class HouseholdGovernor {
    mind::MultiObjectiveGovernor goals_;
    std::array<double,4> experience_weights_;
public:
    HouseholdGovernor(std::array<double,mind::objective_count> goals,
                      std::array<double,4> experience_weights)
        :goals_(goals),experience_weights_(experience_weights) {
        for(double w:experience_weights_)nonnegative(w);
    }
    double score(const Activity& a) const {
        return goals_.score(a.candidate.outcomes)+experience_weights_[0]*a.joy+
            experience_weights_[1]*a.peace+experience_weights_[2]*a.stimulation+
            experience_weights_[3]*a.autonomy;
    }
    std::optional<std::size_t> choose(const std::vector<Activity>& options,double energy) const {
        nonnegative(energy);std::optional<std::size_t> best;
        for(std::size_t i=0;i<options.size();++i) {
            const auto& c=options[i].candidate;
            if(c.permitted && c.energy_required<=energy && (!best || score(options[i])>score(options[*best])))best=i;
        }
        return best;
    }
};
inline std::vector<mind::Candidate> candidates(const std::vector<Activity>& activities) {
    std::vector<mind::Candidate> result;
    for(const auto& activity:activities)result.push_back(activity.candidate);
    return result;
}
} // namespace virtual_cell::household
