#pragma once
// Michael Emanuel Glover's joint-preference motion kernel. Freestanding C++17:
// compiled unchanged into native PersonModel and the existing Glims browser world.
namespace virtual_cell::motion {
constexpr int max_people=6, max_choices=4, max_neighbors=16;
struct Point { double x=0,z=0; };
struct Preferences {
    double progress=1.7555555555555555;
    double anticipation=1.2828234474671283;
    double roses=.7;
    double clearance=.43;
    bool protect_neighbors=true;
};
struct Choice {Point to;double utility=0;bool allowed=false;};
struct Agent {
    Point from;
    Preferences preference;
    Choice choices[max_choices];
    int count=0;
};
struct Neighbor {Point from,to;double clearance=.38;};
struct Decision {
    bool feasible=false;
    int chosen[max_people]={};
    double utilities[max_people]={};
    double score=0;
    int examined=0;
};
inline double squared_distance(Point a,Point b) {const double x=a.x-b.x,z=a.z-b.z;return x*x+z*z;}
inline double swept_squared(Point a,Point b,Point c,Point d) {
    const double x=a.x-c.x,z=a.z-c.z,vx=b.x-a.x-d.x+c.x,vz=b.z-a.z-d.z+c.z;
    const double vv=vx*vx+vz*vz;
    double t=vv>0?-(x*vx+z*vz)/vv:0;
    if(t<0)t=0;
    if(t>1)t=1;
    return squared_distance({x+t*vx,z+t*vz},{0,0});
}
inline bool finite_number(double v) {return v==v&&v<1e100&&v> -1e100;}
inline bool point_valid(Point p) {return finite_number(p.x)&&finite_number(p.z);}
inline bool preference_valid(const Preferences& p) {
    return finite_number(p.progress)&&p.progress>=0&&finite_number(p.anticipation)&&p.anticipation>=0&&
           finite_number(p.roses)&&p.roses>=0&&finite_number(p.clearance)&&p.clearance>0;
}
inline Decision coordinate(const Agent* people,int n,const Neighbor* neighbors,int k,int turn=0) {
    Decision best;
    if(n<1||n>max_people||k<0||k>max_neighbors||turn<0)return best;
    for(int i=0;i<n;++i) {
        if(!point_valid(people[i].from)||!preference_valid(people[i].preference)||people[i].count<1||people[i].count>max_choices)return best;
        for(int j=0;j<people[i].count;++j)
            if(!point_valid(people[i].choices[j].to)||!finite_number(people[i].choices[j].utility))return best;
    }
    for(int i=0;i<k;++i)if(!point_valid(neighbors[i].from)||!point_valid(neighbors[i].to)||!finite_number(neighbors[i].clearance)||neighbors[i].clearance<=0)return best;
    int indices[max_people]={},total=1;
    for(int i=0;i<n;++i)total*=people[i].count;
    double best_tie=-1e100;
    for(int combination=0;combination<total;++combination) {
        ++best.examined;int number=combination;bool safe=true;double sum=0,least=1e100,tie=0,obstruction=0;
        for(int i=0;i<n;++i) {indices[i]=number%people[i].count;number/=people[i].count;}
        for(int i=0;i<n&&safe;++i) {
            const auto& a=people[i];const auto& choice=a.choices[indices[i]];
            if(!choice.allowed){safe=false;break;}
            sum+=choice.utility;if(choice.utility<least)least=choice.utility;
            for(int j=0;j<i;++j) {
                const double clearance=a.preference.clearance>people[j].preference.clearance?a.preference.clearance:people[j].preference.clearance;
                if(swept_squared(a.from,choice.to,people[j].from,people[j].choices[indices[j]].to)<clearance*clearance-1e-12){safe=false;break;}
            }
            if(a.preference.protect_neighbors)for(int j=0;j<k;++j)
                if(swept_squared(a.from,choice.to,neighbors[j].from,neighbors[j].to)<neighbors[j].clearance*neighbors[j].clearance-1e-12){safe=false;break;}
            // Anticipate others' declared first choices. Penalize occupying the
            // space they want, while hard feasibility remains independent of utility.
            for(int j=0;j<n;++j)if(j!=i&&people[j].choices[0].allowed&&
                squared_distance(choice.to,people[j].choices[0].to)<.16)
                obstruction+=people[j].preference.anticipation*.03;
        }
        if(!safe)continue;
        for(int i=0;i<n;++i)tie+=(n-i)*people[(turn+i)%n].choices[indices[(turn+i)%n]].utility;
        const double score=sum+.2*least-obstruction;
        if(!best.feasible||score>best.score+1e-10||(score>best.score-1e-10&&tie>best_tie)) {
            best.feasible=true;best.score=score;best_tie=tie;
            for(int i=0;i<n;++i){best.chosen[i]=indices[i];best.utilities[i]=people[i].choices[indices[i]].utility;}
        }
    }
    return best;
}
} // namespace virtual_cell::motion
