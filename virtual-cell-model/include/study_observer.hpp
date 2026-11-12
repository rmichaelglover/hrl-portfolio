#pragma once
#include "bioelectric.hpp"
#include <optional>
#include <string>
#include <vector>
namespace virtual_cell::study {
struct PoseSample {
    std::string session,frame;
    double seconds,x,y,z,position_variance;
};
struct ScanSample {
    std::string session,frame;
    double seconds,angle_min,angle_increment,range_min,range_max;
    std::vector<double> ranges;
};
struct Association {std::size_t nearby_returns=0;bool optical_fresh=false;};
// External observations own their state. There is no reference to a Person,
// and no command or disturbance path back into the person's nervous system.
class PassiveTracker {
    std::optional<PoseSample> pose_;
    double freshness_seconds_,association_radius_;
public:
    explicit PassiveTracker(double freshness=.25,double radius=.5)
        :freshness_seconds_(electric::detail::positive(freshness)),
         association_radius_(electric::detail::positive(radius)) {}
    void observe(PoseSample p) {
        if(p.session.empty() || p.frame.empty())throw std::invalid_argument("Missing session or frame");
        for(double v:{p.seconds,p.x,p.y,p.z,p.position_variance})electric::detail::checked(v);
        electric::detail::nonnegative(p.seconds);electric::detail::positive(p.position_variance);
        if(pose_ && (p.session!=pose_->session || p.frame!=pose_->frame))
            throw std::invalid_argument("New session/frame requires a new tracker");
        if(pose_ && p.seconds<pose_->seconds)throw std::invalid_argument("Out-of-order optical pose");
        pose_=std::move(p);
    }
    const auto& optical_pose() const {return pose_;}
    Association observe(const ScanSample& scan) const {
        for(double v:{scan.seconds,scan.angle_min,scan.angle_increment,scan.range_min,scan.range_max})
            electric::detail::checked(v);
        electric::detail::nonnegative(scan.seconds);electric::detail::nonnegative(scan.range_min);
        if(scan.range_max<=scan.range_min || scan.angle_increment<=0)
            throw std::invalid_argument("Invalid scan geometry");
        if(!pose_)return {};
        if(scan.session!=pose_->session || scan.frame!=pose_->frame)
            throw std::invalid_argument("Unaligned session or frame; transform first");
        const double age=scan.seconds-pose_->seconds;
        if(age<0 || age>freshness_seconds_)return {};
        Association a{0,true};
        for(std::size_t i=0;i<scan.ranges.size();++i) {
            const double r=scan.ranges[i];
            if(!std::isfinite(r) || r<scan.range_min || r>scan.range_max)continue;
            const double angle=scan.angle_min+i*scan.angle_increment;
            const double x=r*std::cos(angle),y=r*std::sin(angle);
            if(std::hypot(x-pose_->x,y-pose_->y)<=association_radius_)++a.nearby_returns;
        }
        // Surface returns support occupancy near an optical track. They are
        // neither an identified person nor an unbiased body-center measurement.
        return a;
    }
};
enum class SleepStage { Unknown,Wake,N1,N2,N3,REM };
struct SleepEpoch {
    std::string session;
    double onset_seconds,duration_seconds;
    SleepStage scored_stage;
    double eog_left_rms_uv,eog_right_rms_uv;
    void validate() const {
        if(session.empty())throw std::invalid_argument("Sleep epoch requires its recording session");
        electric::detail::nonnegative(onset_seconds);electric::detail::positive(duration_seconds);
        electric::detail::nonnegative(eog_left_rms_uv);electric::detail::nonnegative(eog_right_rms_uv);
    }
};
} // namespace virtual_cell::study
