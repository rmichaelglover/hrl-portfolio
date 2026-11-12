#include "household.hpp"
#include <iostream>
using namespace virtual_cell;
using namespace household;
void check(bool condition,const char* reason) {if(!condition)throw std::runtime_error(reason);}
int main() {
 SubjectiveMap map;map.remember("noodles",0,3,1,"lunch");
 check(!map.visible_recently("noodles",0),"Memory claimed current vision");
 check(!map.visible_recently("Mama",0),"Unobserved parent invented");
 map.observe("fridge",3,0,.1,0,"frontend");
 check(map.visible_recently("fridge",0),"Observed landmark absent");
 const auto old=map.landmarks().at("fridge");map.odometry(1,0,.2);
 check(map.pose_variance()>.2,"Odometry uncertainty absent");
 map.observe("fridge",2,0,.1,1,"frontend");
 check(std::abs(map.landmarks().at("fridge").z-old.z)<1e-9,"Frame transform inconsistent");
 check(!map.visible_recently("fridge",10),"Stale observation claimed visibility");
 for(int z=0;z<4;++z)map.mark_free({0,z});
 check(map.route({0,0},{0,3}).size()==4,"Known route not found");
 check(map.route({0,0},{1,3}).empty(),"Traversed unknown space");
 HouseholdPerson papa("Papa",{.9,.9,.1,.1,.8,.8});
 HouseholdPerson mama("Mama",{.9,.9,.1,.1,.8,.8},true);
 check(papa.answer_conversation_invitation(),"Willing parent declined");
 check(!mama.answer_conversation_invitation(),"Occupied parent unable to decline");
 check(!papa.answer_audible_music_request(),"Quiet preference ignored");
 check(!papa.wants_meal() && papa.wants_roll() && papa.wants_drink(),"Food preferences collapsed");
 OtherModel p,m;p.currently_visible=true;auto a=activities(Needs{},p,m);
 check(!a[2].candidate.permitted && !a[5].candidate.permitted,"Visibility became consent");
 p.hear_conversation_reply(true);a=activities(Needs{},p,m);
 check(a[5].candidate.permitted && !a[2].candidate.permitted,"Different permissions conflated");
 Needs satiated;satiated.hunger=0;
 auto appealing=activities(satiated,p,m)[3].joy;
 satiated.pleasant_food=0;satiated.eating_effort=1;
 check(appealing>activities(satiated,p,m)[3].joy,"Food appeal depended only on hunger");
 MusicPractice focused,relaxed;Needs f,r;f.concentration=1;f.relaxation=0;r.concentration=0;r.relaxation=1;
 focused.advance(10,f,false,true,false);relaxed.advance(10,r,false,true,false);
 check(focused.lyric_recall>relaxed.lyric_recall,"Attention did not affect rehearsal");
 check(relaxed.incidental_learning>0 && relaxed.procedural_consolidation>focused.procedural_consolidation,"Relaxation stopped all learning");
 check(focused.guitar==.85,"Lyric practice silently trained guitar");
 bool rejected=false;try{map.observe("bad",1,0,0,0,"test");}catch(const std::invalid_argument&){rejected=true;}
 check(rejected,"Zero measurement variance accepted");
 std::cout<<"Household checks passed\n";
}
