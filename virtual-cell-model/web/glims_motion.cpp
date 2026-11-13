#include "peaceful_motion.hpp"
using namespace virtual_cell::motion;
// Small C ABI: JS supplies observed positions, intentions and terrain feasibility.
// No scripted trajectories or browser-side replacement for the decision kernel.
static Agent people[max_people];
static Neighbor wildlife[max_neighbors];
static Decision result;
static int count=0,neighbors=0;
extern "C" {
void reset_motion(int n,int k) {count=n;neighbors=k;for(int i=0;i<max_people;++i)people[i]=Agent{};}
void set_person(int i,double x,double z,double clearance,double progress,double anticipation,double roses) {
    if(i<0||i>=max_people)return;
    people[i].from={x,z};people[i].preference={progress,anticipation,roses,clearance,true};
}
void set_choice(int i,int j,double x,double z,double utility,int allowed) {
    if(i<0||i>=max_people||j<0||j>=max_choices)return;
    people[i].choices[j]={{x,z},utility,allowed!=0};
    if(people[i].count<=j)people[i].count=j+1;
}
void set_neighbor(int i,double x,double z,double nx,double nz,double clearance) {
    if(i>=0&&i<max_neighbors)wildlife[i]={{x,z},{nx,nz},clearance};
}
int decide_motion(int turn) {result=coordinate(people,count,wildlife,neighbors,turn);return result.feasible?1:0;}
int selected_motion(int i) {return i>=0&&i<count&&result.feasible?result.chosen[i]:-1;}
int examined_motion() {return result.examined;}
double score_motion() {return result.score;}
}
// Freestanding support for aggregate initialization/copies (no libc import).
extern "C" void* memset(void* destination,int value,__SIZE_TYPE__ size) {
    auto* bytes=static_cast<unsigned char*>(destination);
    for(__SIZE_TYPE__ i=0;i<size;++i)bytes[i]=static_cast<unsigned char>(value);
    return destination;
}
extern "C" void* memcpy(void* destination,const void* source,__SIZE_TYPE__ size) {
    auto* out=static_cast<unsigned char*>(destination);
    const auto* in=static_cast<const unsigned char*>(source);
    for(__SIZE_TYPE__ i=0;i<size;++i)out[i]=in[i];
    return destination;
}
