#include "study_observer.hpp"
#include "reflective_practice.hpp"
#include <iostream>
using namespace virtual_cell::study;
void check(bool x){if(!x)throw std::runtime_error("Study observer invariant failed");}
template<class F> void rejects(F f){bool bad=false;try{f();}catch(const std::invalid_argument&){bad=true;}check(bad);}
int main(){
 PassiveTracker t;t.observe({"motion","room",1,2,0,0,.01});
 ScanSample scan{"motion","room",1,0,.1,.1,10,{2,INFINITY,NAN,20}};
 check(t.observe(scan).nearby_returns==1);
 scan.seconds=2;check(!t.observe(scan).optical_fresh);
 scan.seconds=.9;check(!t.observe(scan).optical_fresh);
 scan.seconds=1;scan.frame="unregistered_lidar";rejects([&]{t.observe(scan);});
 rejects([&]{t.observe(PoseSample{"motion","room",.5,2,0,0,.01});});
 rejects([&]{t.observe(PoseSample{"other-session","room",1,2,0,0,.01});});
 SleepEpoch e{"sleep-recording",0,30,SleepStage::REM,12,15};e.validate();
 e.duration_seconds=0;rejects([&]{e.validate();});
 check(t.optical_pose()->x==2); // Lidar did not shift pose to a surface centroid.
 virtual_cell::mind::ReflectivePractice practice;
 practice.say(virtual_cell::mind::flowers_mantra());
 check(practice.count(virtual_cell::mind::ReflectiveReward::Happiness)==1);
 practice.revise_musical_context(.8);check(practice.context_revisions()==1);
 check(t.optical_pose()->x==2);
 std::cout<<"Session, frame, staleness, missing-return and sleep-epoch checks passed\n";
}
