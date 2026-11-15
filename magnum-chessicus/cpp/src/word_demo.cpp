#include "progression_words.hpp"
#include <iostream>
using namespace magnum;
using namespace magnum::logic;
using namespace magnum::logic::words;
int main() {
    auto loop=knight_loop();Word a(loop,Natural("3")),b(loop,Natural("4"));
    std::cout<<"Rules: movement-only variant; draw adjudication is absent.\nGenerator: g1f3 g8f6 f3g1 f6g8 (4 plies)\n";
    std::cout<<"Concatenation: c^3 ; c^4 = c^"<<a.then(b).cycles().decimal()<<" (7 cycles, 28 plies)\n";
    Word huge(loop,Natural("10000000000000000000000000000000000000000"));
    std::cout<<"Symbolic successor of c^(10^40): c^"<<huge.successor().cycles().decimal()<<'\n';
    try {huge.materialize(100);}catch(const ResourceLimit&){std::cout<<"100-ply expansion budget: refused; the symbolic word remains exact.\n";}
    try {Progression ordinary(State{},a.then(b).materialize(28));}
    catch(const std::invalid_argument&){std::cout<<"Same 28-ply sequence under existing standard kernel: rejected after automatic draw.\n";}
    RepeatExtension extension;
    std::cout<<"EXTRA Repeat operation: Repeat(c^3, c^4) = c^"<<extension.repeat(a,b).cycles().decimal()<<" (12 cycles, 48 plies)\n";
    std::cout<<"Concatenation-only structure: (N,0,1,+).\nWith added variable-count Repeat: (N,0,1,+,*).\n";
    std::cout<<"Multiplication is not first-order definable in the concatenation-only structure; Repeat is an explicit extension.\n";
}
