// Recursive Creatures: a Tiny Creek artificial-life sketch.
// C++17, standard library only. The creatures are simulated agents, not
// biological organisms. Physics supplies constraints; constructors supply
// repeatable transformations; RAII owns every resource used by the run.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <utility>
#include <vector>

namespace tiny_creek {
struct Vec { double x{}, y{}; Vec operator+(Vec b)const{return{x+b.x,y+b.y};} Vec operator-(Vec b)const{return{x-b.x,y-b.y};} Vec operator*(double s)const{return{x*s,y*s};} };
double dot(Vec a,Vec b){return a.x*b.x+a.y*b.y;} double len(Vec a){return std::sqrt(dot(a,a));} Vec unit(Vec a){double n=len(a);return n>1e-9?a*(1/n):Vec{1,0};}

struct Task { std::string name; std::function<bool(const struct Creature&)> ready; std::function<void(struct Creature&,double)> apply; };

struct Creature {
    int id{}, generation{}; Vec p{},v{}; double energy=1., age=0.; int hue{}; std::array<double,3> genome{}; std::vector<Task> constructors;
    Creature(int id_,int gen,Vec pos,int color,std::array<double,3> dna):id(id_),generation(gen),p(pos),hue(color),genome(dna){
        constructors.push_back({"seek-food",[](const Creature& c){return c.energy<1.8;},[](Creature& c,double){c.energy+=.002;}});
        constructors.push_back({"reproduce",[](const Creature& c){return c.energy>2.25&&c.age>2.0;},[](Creature& c,double){c.energy-=.65;}});
        constructors.push_back({"rest",[](const Creature& c){return c.energy>1.1;},[](Creature& c,double dt){c.energy=std::min(3.0,c.energy+dt*.018);}});
    }
};

// RAII: this object owns the output stream for a complete run and closes it
// automatically on every return path, including exceptions.
class TraceFile {
    std::ofstream out_;
public:
    explicit TraceFile(const std::string& path):out_(path){if(!out_)throw std::runtime_error("cannot open trace: "+path);out_<<"{\"frames\":[\n";}
    void frame(const std::vector<Creature>& cs,int tick){if(tick)out_<<",\n";out_<<"{\"tick\":"<<tick<<",\"creatures\":[";for(std::size_t i=0;i<cs.size();++i){if(i)out_<<',';const auto& c=cs[i];out_<<"{\"id\":"<<c.id<<",\"generation\":"<<c.generation<<",\"x\":"<<c.p.x<<",\"y\":"<<c.p.y<<",\"energy\":"<<c.energy<<",\"hue\":"<<c.hue<<"}";}out_<<"]}";}
    ~TraceFile(){if(out_){out_<<"\n]}\n";out_.close();}}
    TraceFile(const TraceFile&)=delete; TraceFile& operator=(const TraceFile&)=delete;
};

class World {
    std::mt19937 rng_; int nextId_=0; std::vector<Creature> cs_; std::vector<Vec> food_;
    double wrap(double x)const{return x<0?x+1:x>1?x-1:x;}
public:
    explicit World(unsigned seed=11):rng_(seed){
        for(int i=0;i<12;++i) add_creature({.15+.7*(i%4)/3.,.18+.64*(i/4)/2.},i*29%360,0);
        for(int i=0;i<55;++i) food_.push_back({std::uniform_real_distribution<double>(.04,.96)(rng_),std::uniform_real_distribution<double>(.06,.94)(rng_)});
    }
    const std::vector<Creature>& creatures()const{return cs_;}
    void add_creature(Vec p,int hue,int gen,std::array<double,3> dna={.7,.9,.6}){cs_.emplace_back(nextId_++,gen,p,hue,dna);}
    void step(double dt){
        for(auto& c:cs_){c.age+=dt; Vec toward{}; double best=9.; for(auto f:food_){double d=len(f-c.p);if(d<best){best=d;toward=f-c.p;}} Vec steer=unit(toward)*(.28*c.genome[0]);
            for(const auto& other:cs_)if(&other!=&c){Vec away=c.p-other.p;double d=len(away);if(d<.12)steer=steer+unit(away)*(.16*(.12-d)/.12);}
            c.v=c.v+steer*dt; c.v=c.v*(.985); c.p={wrap(c.p.x+c.v.x*dt),wrap(c.p.y+c.v.y*dt)}; c.energy-=dt*(.055+len(c.v)*.02);
            for(auto& f:food_)if(len(f-c.p)<.035){c.energy=std::min(3.2,c.energy+.38);f={std::uniform_real_distribution<double>(.04,.96)(rng_),std::uniform_real_distribution<double>(.06,.94)(rng_)};}
            for(auto& task:c.constructors)if(task.ready(c))task.apply(c,dt);
        }
        std::vector<Creature> newborns; for(const auto& parent:cs_)if(parent.energy>2.25&&parent.age>2.0&&parent.generation<5){auto dna=parent.genome;dna[static_cast<std::size_t>(parent.id)%3]=std::clamp(dna[static_cast<std::size_t>(parent.id)%3]+std::uniform_real_distribution<double>(-.08,.08)(rng_),.2,1.2);newborns.emplace_back(nextId_,parent.generation+1,wrapv(parent.p+Vec{.025,-.018}), (parent.hue+37)%360,dna);++nextId_;}
        cs_.insert(cs_.end(),std::make_move_iterator(newborns.begin()),std::make_move_iterator(newborns.end())); cs_.erase(std::remove_if(cs_.begin(),cs_.end(),[](const Creature& c){return c.energy<=0.;}),cs_.end());
    }
private: static Vec wrapv(Vec p){return{p.x<0?p.x+1:p.x>1?p.x-1:p.x,p.y<0?p.y+1:p.y>1?p.y-1:p.y};}
};

void write_ppm(const std::string& path,const World& w,int side=320){std::ofstream out(path,std::ios::binary);if(!out)throw std::runtime_error("cannot write ppm");out<<"P6\n"<<side<<' '<<side<<"\n255\n";for(int y=0;y<side;++y)for(int x=0;x<side;++x){double r=10,g=25,b=35;for(const auto& c:w.creatures()){double dx=x/(double)side-c.p.x,dy=y/(double)side-c.p.y,d=std::sqrt(dx*dx+dy*dy);double glow=std::max(0.,1-d*38);r+=glow*(80+175*std::sin(c.hue*.017));g+=glow*(90+140*std::sin(c.hue*.017+2));b+=glow*(120+120*std::sin(c.hue*.017+4));}unsigned char p[3]{static_cast<unsigned char>(std::clamp(r,0.,255.)),static_cast<unsigned char>(std::clamp(g,0.,255.)),static_cast<unsigned char>(std::clamp(b,0.,255.))};out.write(reinterpret_cast<char*>(p),3);}}
}

int main(int argc,char**argv){int frames=600;if(argc>1)frames=std::max(1,std::stoi(argv[1]));std::string trace=argc>2?argv[2]:"tiny-creek-trace.json";tiny_creek::World world;tiny_creek::TraceFile log(trace);for(int i=0;i<frames;++i){world.step(.016);if(i%10==0)log.frame(world.creatures(),i);}tiny_creek::write_ppm("tiny-creek-world.ppm",world);std::cout<<"recursive-creatures frames="<<frames<<" final_creatures="<<world.creatures().size()<<" trace="<<trace<<" image=tiny-creek-world.ppm\n";}
