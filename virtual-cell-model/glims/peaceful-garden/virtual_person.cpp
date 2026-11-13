// In honor of James Calvin Glover ("Jimmy"), Michael's brother:
// a kind biochemistry graduate of Kennesaw State University
// who wanted to study prosthetics.
// Michael Emanuel Glover's extension: preferences in a shared, peaceful world.
// The full joint planner and PGN importer live in the ROS2 peaceful garden module.
#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include "chess_preferences.hpp"

struct Point { double x, y; };
struct Preferences {
    bool protect_frogs = true;
    double personal_space = 0.75;
    double enjoy_roses = 0.9;
};

// Check the complete simultaneous motion, not only its destination.
double closest_approach(Point a, Point b, Point c, Point d) {
    const double x=a.x-c.x, y=a.y-c.y;
    const double vx=b.x-a.x-d.x+c.x, vy=b.y-a.y-d.y+c.y;
    const double vv=vx*vx+vy*vy;
    const double t=vv>0 ? std::clamp(-(x*vx+y*vy)/vv,0.0,1.0) : 0;
    return std::hypot(x+t*vx,y+t*vy);
}

class Person {
    std::string name;
    bool wants_prosthetic_support;
public:
    Preferences preferences;
    Point position, preferred_next;
    Person(std::string initial_name, bool initial_preference, Point initial_position={0,0})
        : name(initial_name), wants_prosthetic_support(initial_preference),
          position(initial_position), preferred_next(initial_position) {}
    std::string get_name() const { return name; }
    bool wants_support() const { return wants_prosthetic_support; }
    bool compatible_with(Point proposed, const Person& other, Point their_proposal) const {
        return closest_approach(position, proposed, other.position, their_proposal)
               >= std::max(preferences.personal_space,other.preferences.personal_space);
    }
    bool protects_frog(Point proposed, Point frog_now, Point frog_next) const {
        return !preferences.protect_frogs || closest_approach(position,proposed,frog_now,frog_next)>=.65;
    }
    double anticipation_weight() const { return chess_preferences::anticipation; }
};

int main() {
    Person alex("Alex",true,{1,2}), rosy("Rosy",false,{3,2});
    alex.preferred_next={2,2}; rosy.preferred_next={2,2};
    const bool both_can_move=alex.compatible_with(alex.preferred_next,rosy,rosy.preferred_next);
    std::cout << alex.get_name() << '\n' << std::boolalpha << alex.wants_support() << '\n';
    std::cout << "Both prefer the same space. Compatible? " << both_can_move << '\n';
    std::cout << "Alex can wait while Rosy moves? "
              << alex.compatible_with(alex.position,rosy,rosy.preferred_next) << '\n';
    std::cout << "Walking over a frog allowed? "
              << alex.protects_frog({2,2},{2,2},{2,2}) << '\n';
    std::cout << "Chess-informed anticipation weight: " << alex.anticipation_weight() << '\n';
    std::cout << "We can wait, take another path, and stop to smell the roses.\n";
    return both_can_move ? 1 : 0;
}
