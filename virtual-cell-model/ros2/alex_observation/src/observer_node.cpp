#include "study_observer.hpp"
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <diagnostic_msgs/msg/diagnostic_array.hpp>
using virtual_cell::study::PoseSample;
class Observer final:public rclcpp::Node {
    virtual_cell::study::PassiveTracker tracker_;
    std::string session_;
    std::optional<virtual_cell::study::SleepEpoch> latest_sleep_;
    rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr optical_;
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr lidar_;
    rclcpp::Subscription<diagnostic_msgs::msg::DiagnosticArray>::SharedPtr sleep_;
    rclcpp::Publisher<diagnostic_msgs::msg::DiagnosticArray>::SharedPtr report_;
    static double seconds(const builtin_interfaces::msg::Time& t){return t.sec+t.nanosec*1e-9;}
public:
    Observer():Node("alex_passive_observer") {
        session_=declare_parameter<std::string>("motion_session","synthetic-room-1");
        report_=create_publisher<diagnostic_msgs::msg::DiagnosticArray>("/alex/tracking/status",10);
        optical_=create_subscription<geometry_msgs::msg::PoseWithCovarianceStamped>("/alex/mocap/pose",10,
            [this](const geometry_msgs::msg::PoseWithCovarianceStamped& m){
                try {const auto& p=m.pose.pose.position;
                    tracker_.observe(PoseSample{session_,m.header.frame_id,seconds(m.header.stamp),p.x,p.y,p.z,m.pose.covariance[0]});
                }catch(const std::exception& e){RCLCPP_WARN(get_logger(),"Optical observation rejected: %s",e.what());}
            });
        lidar_=create_subscription<sensor_msgs::msg::LaserScan>("/alex/lidar/scan",rclcpp::SensorDataQoS(),
            [this](const sensor_msgs::msg::LaserScan& m){
                try {
                    virtual_cell::study::ScanSample s{session_,m.header.frame_id,seconds(m.header.stamp),m.angle_min,m.angle_increment,m.range_min,m.range_max,{}};
                    s.ranges.assign(m.ranges.begin(),m.ranges.end());const auto a=tracker_.observe(s);
                    diagnostic_msgs::msg::DiagnosticArray report;report.header=m.header;
                    diagnostic_msgs::msg::DiagnosticStatus status;status.name="alex/passive_tracking";status.hardware_id=session_;
                    status.level=a.optical_fresh?0:1;status.message=a.optical_fresh?"aligned optical pose; lidar occupancy support":"no fresh optical pose";
                    diagnostic_msgs::msg::KeyValue count;count.key="nearby_lidar_returns";count.value=std::to_string(a.nearby_returns);status.values.push_back(count);
                    report.status.push_back(status);report_->publish(report);
                    RCLCPP_INFO(get_logger(),"passive track: fresh=%d nearby_returns=%zu",a.optical_fresh,a.nearby_returns);
                }catch(const std::exception& e){RCLCPP_WARN(get_logger(),"Lidar observation rejected: %s",e.what());}
            });
        sleep_=create_subscription<diagnostic_msgs::msg::DiagnosticArray>("/alex/sleep/epochs",10,
            [this](const diagnostic_msgs::msg::DiagnosticArray& m){
                for(const auto& s:m.status) {
                    if(s.name!="alex/sleep_epoch" || s.hardware_id.empty())continue;
                    try {
                        std::map<std::string,std::string> values;
                        for(const auto& kv:s.values)values[kv.key]=kv.value;
                        using Stage=virtual_cell::study::SleepStage;
                        const std::map<std::string,Stage> stages{{"AWAKE",Stage::Wake},{"N1",Stage::N1},
                            {"N2",Stage::N2},{"N3",Stage::N3},{"REM",Stage::REM}};
                        const auto found=stages.find(s.message);
                        virtual_cell::study::SleepEpoch epoch{s.hardware_id,std::stod(values.at("onset_seconds")),
                            std::stod(values.at("duration_seconds")),found==stages.end()?Stage::Unknown:found->second,
                            std::stod(values.at("eog_left_rms_uv")),std::stod(values.at("eog_right_rms_uv"))};
                        epoch.validate();latest_sleep_=std::move(epoch);
                        RCLCPP_INFO(get_logger(),"separate sleep session=%s stage=%s; not fused with motion session %s",
                            s.hardware_id.c_str(),s.message.c_str(),session_.c_str());
                    }catch(const std::exception& e){RCLCPP_WARN(get_logger(),"Sleep epoch rejected: %s",e.what());}
                }
            });
    }
};
int main(int argc,char** argv){rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<Observer>());rclcpp::shutdown();}
