// Super Monkey Chessballs: Tri-Engine
// C++17, standard library only. The core emits deterministic JSON snapshots
// that a raw OpenGL front end can consume without putting a graphics library
// into the physics build.
#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

namespace mcb {
constexpr double Pi = 3.14159265358979323846;

struct Vec2 { double x{}, y{}; };
Vec2 operator+(Vec2 a, Vec2 b) { return {a.x+b.x, a.y+b.y}; }
Vec2 operator-(Vec2 a, Vec2 b) { return {a.x-b.x, a.y-b.y}; }
Vec2 operator*(Vec2 a, double s) { return {a.x*s, a.y*s}; }
double dot(Vec2 a, Vec2 b) { return a.x*b.x+a.y*b.y; }
double norm(Vec2 a) { return std::sqrt(dot(a,a)); }
Vec2 unit(Vec2 a) { const double n=norm(a); return n>1e-12?a*(1.0/n):Vec2{1,0}; }

struct Ball { int id{}; Vec2 p{}, v{}; double r=.035, mass=1.; int hue{}; };
struct Move { std::string san; int ply{}; };

class MarbleEngine {
public:
    std::vector<Ball> balls;
    std::array<Vec2,3> triangle{{{.18,.18},{.82,.22},{.50,.82}}};
    double time{};
    explicit MarbleEngine(unsigned seed=7) : rng(seed) {}

    void add_ball(Vec2 p, Vec2 v, double r, int hue) {
        balls.push_back(Ball{static_cast<int>(balls.size()),p,v,r,1.,hue});
    }

    void step(double dt) {
        time += dt;
        for (auto& b: balls) {
            Vec2 force{0.,-.46};
            for (const auto& vertex: triangle) {
                Vec2 d=vertex-b.p; double d2=dot(d,d)+.018;
                force=force+d*(.006/d2);
            }
            b.v=b.v+force*dt; b.v=b.v*.998; b.p=b.p+b.v*dt;
            if (b.p.x<b.r){b.p.x=b.r;b.v.x=std::abs(b.v.x)*.82;}
            if (b.p.x>1-b.r){b.p.x=1-b.r;b.v.x=-std::abs(b.v.x)*.82;}
            if (b.p.y<b.r){b.p.y=b.r;b.v.y=std::abs(b.v.y)*.82;}
            if (b.p.y>1-b.r){b.p.y=1-b.r;b.v.y=-std::abs(b.v.y)*.82;}
        }
        for (std::size_t i=0;i<balls.size();++i) for (std::size_t j=i+1;j<balls.size();++j) collide(balls[i],balls[j]);
    }

private:
    std::mt19937 rng;
    static void collide(Ball& a, Ball& b) {
        Vec2 d=b.p-a.p; double dist=norm(d), minDist=a.r+b.r;
        if (dist<minDist) {
            Vec2 n=unit(d); double overlap=minDist-std::max(dist,1e-9);
            a.p=a.p-n*(overlap*.5); b.p=b.p+n*(overlap*.5);
            double rel=dot(b.v-a.v,n); if(rel<0){double impulse=-1.02*rel/2.;a.v=a.v-n*impulse;b.v=b.v+n*impulse;}
        }
    }
};

class ChessEngine {
public:
    std::vector<Move> moves{{"1. e4!",1},{"1... e5",2},{"2. Nf3",3},{"2... Nc6",4},
        {"3. Bb5!",5},{"3... P@c6?!",6},{"4. Bxc6!",7},{"4... P@f2+",8},
        {"11. Q@h5!",9},{"12. h8=Q#",10}};
    std::size_t cursor{};
    std::string current() const { return cursor?moves[cursor-1].san:"opening position"; }
    void advance() { if(cursor<moves.size()) ++cursor; }
};

class TriEngine {
public:
    MarbleEngine marble; ChessEngine chess; std::mt19937 rng;
    explicit TriEngine(unsigned seed=7):marble(seed),rng(seed){
        marble.add_ball({.12,.80},{.50,-.05},.035,0);
        marble.add_ball({.38,.66},{-.22,.10},.028,1);
        marble.add_ball({.68,.74},{-.12,-.04},.030,2);
    }
    void step(double dt=.016) { marble.step(dt); if(static_cast<int>(marble.time*60)%36==0) chess.advance(); }
    void json(std::ostream& out) const {
        out<<"{\"time\":"<<std::fixed<<std::setprecision(4)<<marble.time<<",\"move\":\""<<current_json(chess.current())<<"\",\"balls\":[";
        for(std::size_t i=0;i<marble.balls.size();++i){const auto& b=marble.balls[i];if(i)out<<',';out<<"{\"id\":"<<b.id<<",\"x\":"<<b.p.x<<",\"y\":"<<b.p.y<<",\"vx\":"<<b.v.x<<",\"vy\":"<<b.v.y<<",\"hue\":"<<b.hue<<"}";}out<<"]}\n";
    }
private:
    static std::string current_json(const std::string& s){std::string r;for(char c:s){if(c=='"'||c=='\\')r+='\\';r+=c;}return r;}
};
}

int main(int argc,char** argv){
    int frames=180; if(argc>1) frames=std::max(1,std::stoi(argv[1]));
    mcb::TriEngine engine(7); std::cout<<"{\"engine\":\"super-monkey-chessballs-tri\",\"frames\":"<<frames<<",\"snapshots\":[\n";
    for(int i=0;i<frames;++i){if(i)std::cout<<",";engine.step();engine.json(std::cout);} std::cout<<"]}\n"; return 0;
}
