#include "progression_logic.hpp"
#include <iostream>
using namespace magnum;
using namespace magnum::logic;
void require(bool value,const char* why) {if(!value) throw std::runtime_error(why);}
template<class F> void rejects(F f) {bool caught=false;try{f();}catch(const std::exception&){caught=true;}require(caught,"Invalid certificate/code/formula accepted");}
int main() {try {
    std::string bytes;for(unsigned i=0;i<256;++i) bytes+=static_cast<char>(i);
    require(unnumber(number(bytes))==bytes,"All-byte number roundtrip");
    require(number("")!=number(std::string(1,'\0')),"Leading zero collision");
    for(auto code:{"","01","100","1256","1abc"}) rejects([&]{(void)unnumber(code);});
    State initial;
    Progression first(initial,{"e2e4"}),second(first.end(),{"e7e5"});
    auto combined=first.then(second);
    require(combined.length()==2,"Path composition length");
    require(combined.end().board.getFen()==Progression(initial,{"e2e4","e7e5"}).end().board.getFen(),"Path composition endpoint");
    rejects([&]{first.then(Progression(initial,{"d2d4"}));});
    rejects([&]{Progression invalid(initial,{"e2e5"});});
    Progression cycle(initial,{"g1f3","g8f6","f3g1","f6g8","g1f3","g8f6","f3g1","f6g8"});
    require(key(cycle.end().board)==key(initial.board),"Cycle placement");
    require(number(state_text(cycle.end()))!=number(state_text(initial)),"History was erased by numbering");
    require(number(cycle.text())!=number(cycle.prefix(4).text()),"Path code collision");
    PrefixArithmetic arithmetic(cycle);
    require(arithmetic.successor(7)==8&&!arithmetic.successor(8),"Successor boundary");
    require(arithmetic.add(3,4)==7&&!arithmetic.add(7,2),"Addition boundary");
    require(arithmetic.multiply(2,4)==8&&!arithmetic.multiply(3,3),"Multiplication boundary");
    require(arithmetic.multiply(0,8)==0&&!arithmetic.multiply(0,9),"Multiplication domain");
    // Exhaustive bounded arithmetic truth tables, compared to ordinary integers.
    for(std::size_t a=0;a<=8;++a) for(std::size_t b=0;b<=8;++b) {
        auto sum=arithmetic.add(a,b),product=arithmetic.multiply(a,b);
        require(bool(sum)==(a+b<=8),"Addition table domain");if(sum) require(*sum==a+b,"Addition table value");
        require(bool(product)==(a*b<=8),"Multiplication table domain");if(product) require(*product==a*b,"Multiplication table value");
    }
    auto truth=atom(Op::True);ModelChecker checker;
    require(checker.evaluate(initial,some(truth)),"Initial successor missing");
    require(checker.evaluate(initial,every(negate(atom(Op::WhiteTurn)))),"Turn alternation");
    auto impossible=some(some(negate(truth)));
    require(!checker.evaluate(initial,impossible)&&checker.visited()==821,"Complete two-ply modal enumeration");
    auto dual=negate(some(negate(atom(Op::WhiteTurn))));
    require(checker.evaluate(initial,every(atom(Op::WhiteTurn)))==checker.evaluate(initial,dual),"Box diamond duality");
    State black=first.end();State target=second.end();
    auto goal=atom(Op::Position,key(target.board));
    require(checker.evaluate(black,reach_within(goal,1,false)),"Reachability witness missing");
    require(!checker.evaluate(black,reach_within(goal,1,true)),"Cooperation confused with forcing");
    State mate("7k/8/5KQ1/8/8/8/8/8 w - - 0 1");
    require(checker.evaluate(mate,reach_within(atom(Op::WhiteMate),1,true)),"Mate-in-one derivation");
    mate.play("g6g7");
    require(!checker.evaluate(mate,some(truth))&&checker.evaluate(mate,every(truth)),"Terminal modal semantics");
    require(!checker.evaluate(mate,reach_within(negate(truth),2,true)),"Vacuous win at terminal");
    rejects([&]{Progression invalid(mate,{"h8g8"});});
    ModelChecker empty(0);bool limited=false;
    try{empty.evaluate(initial,truth);}catch(const ResourceLimit&){limited=true;}
    require(limited,"Budget exhaustion became a verdict");
    rejects([&]{unary(Op::Some,{});});rejects([&]{atom(static_cast<Op>(99));});
    auto formula=reach_within(atom(Op::WhiteMate),2,true);
    require(unnumber(number(text(formula)))==text(formula),"Formula numbering");
    require(state_text(initial)==state_text(State{}),"Query mutated caller history");
    std::cout<<"PASS: injective coding roundtrips, legal composition, history, bounded arithmetic tables, modal duality, cooperative/adversarial distinction, mate, terminals and budget refusal\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
