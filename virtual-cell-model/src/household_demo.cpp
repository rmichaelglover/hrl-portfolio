#include "household.hpp"
#include <iostream>
using namespace virtual_cell;
using namespace household;
int main() {
    auto seeing=vision::make_seeing_alex();auto& body=seeing.alex.human().body();
    SubjectiveMap map;
    // Supplied semantic frontend observations: scalar rods cannot identify objects.
    map.observe("guitar",1,-.3,.04,0,"fixture:semantic-range-bearing");
    map.observe("computer",1.5,.4,.04,0,"fixture:semantic-range-bearing");
    map.observe("Papa",2,-.5,.04,0,"fixture:semantic-range-bearing");
    map.observe("food",1,.6,.04,0,"fixture:semantic-range-bearing");
    map.observe("refrigerator",3,0,.04,0,"fixture:semantic-range-bearing");
    map.remember("Singaporean noodles",0,3,.5,"episodic:lunch; inside refrigerator");
    vision::Environment room;
    room.add({"idealized diffuse room light",{0,0,3},1e-9,500});
    body.eye(0).window().set_frame(map.eye_frame(-.032));
    body.eye(1).window().set_frame(map.eye_frame(.032));
    body.advance_in_environment(room,500);
    const auto sensory=vision::retinal_observation(body,{0,0},500,0);
    const auto evidence=seeing.alex.boundary_evidence(sensory,"household:retinal-window");
    std::cout<<"Retinal event count: "<<evidence.observation.visual_events<<"\n";
    std::cout<<"Mama currently seen: "<<map.visible_recently("Mama",0)<<"\n";
    for(int z=0;z<=3;++z)map.mark_free({0,z});
    std::cout<<"Remembered fridge route steps: "<<map.route({0,0},{0,3}).size()-1<<"\n";
    map.odometry(1,0,.03);
    body.eye(0).window().set_frame(map.eye_frame(-.032));
    body.eye(1).window().set_frame(map.eye_frame(.032));
    body.advance_in_environment(room,500);
    HouseholdPerson papa("Papa",{.8,.9,.2,.1,.8,.7});
    HouseholdPerson mama("Mama",{.4,.9,.1,.1,.7,.6},true);
    OtherModel papa_model,mama_model;papa_model.currently_visible=true;
    papa_model.hear_conversation_reply(papa.answer_conversation_invitation());
    papa_model.hear_music_reply(papa.answer_audible_music_request());
    // Mama remains unseen and her availability unknown until she replies.
    Needs needs;MusicPractice music;
    const auto options=activities(needs,papa_model,mama_model);
    HouseholdGovernor governor({1,1,2,2,2},{.2,.2,.1,.1});
    const auto actions=candidates(options);
    std::cout<<"Activity,permitted,score,joy,peace,stimulation,autonomy\n";
    for(const auto& a:options)std::cout<<a.candidate.name<<','<<a.candidate.permitted<<','
        <<governor.score(a)<<','<<a.joy<<','<<a.peace<<','<<a.stimulation<<','<<a.autonomy<<"\n";
    const auto choice=governor.choose(options,1);
    if(choice)std::cout<<"Current illustrative choice: "<<actions[*choice].name<<"\n";
    HouseholdGovernor family_governor({1,1,5,1,1},{.3,.4,.1,.1});
    const auto family_choice=family_governor.choose(options,1);
    if(family_choice)std::cout<<"Relationship-prioritizing choice: "<<options[*family_choice].candidate.name<<"\n";
    std::cout<<"Independent ten-minute lyric-practice probe follows.\n";
    music.advance(10,needs,false,true,false);
    std::cout<<"Lyric recall after ten quiet practice minutes: "<<music.lyric_recall<<"\n";
    std::cout<<"Papa: meal="<<papa.wants_meal()<<", roll="<<papa.wants_roll()<<", drink="<<papa.wants_drink()<<"\n";
    std::cout<<"Mama preferences exist independently; Alex has not read them.\n";
}
