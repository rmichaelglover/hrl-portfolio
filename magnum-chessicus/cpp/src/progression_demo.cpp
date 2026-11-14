#include "progression_logic.hpp"
#include <iostream>
using namespace magnum;
using namespace magnum::logic;
int main() {
    State initial;Progression a(initial,{"e2e4"}),b(a.end(),{"e7e5"});auto c=a.then(b);
    ModelChecker checker;
    auto target=atom(Op::Position,key(b.end().board));
    std::cout<<std::boolalpha;
    std::cout<<"Legal composition: "<<a.length()<<" + "<<b.length()<<" = "<<c.length()<<" plies\n";
    std::cout<<"Black can cooperate to reach e4/e5: "<<checker.evaluate(a.end(),reach_within(target,1,false))<<'\n';
    std::cout<<"White can force that position on Black's turn: "<<checker.evaluate(a.end(),reach_within(target,1,true))<<'\n';
    State mate("7k/8/5KQ1/8/8/8/8/8 w - - 0 1");
    auto theorem=reach_within(atom(Op::WhiteMate),1,true);
    std::cout<<"White can force mate within one ply: "<<checker.evaluate(mate,theorem)<<'\n';
    std::cout<<"Formula text: "<<text(theorem)<<"\nFormula natural code: "<<number(text(theorem))<<'\n';
    Progression cycle(initial,{"g1f3","g8f6","f3g1","f6g8","g1f3","g8f6","f3g1","f6g8"});
    PrefixArithmetic arithmetic(cycle);
    std::cout<<"Certified prefix domain: 0.."<<arithmetic.maximum()<<"\n2 * 4 = "<<*arithmetic.multiply(2,4)<<"\nS(8) exists: "<<bool(arithmetic.successor(8))<<'\n';
    std::cout<<"Same repetition-position key after eight plies: "<<(key(initial.board)==key(cycle.end().board))<<'\n';
    std::cout<<"Same complete state code: "<<(number(state_text(initial))==number(state_text(cycle.end())))<<'\n';
    std::cout<<"Conclusion: bounded arithmetic tables are faithful on their stated domain; no interpretation of unbounded arithmetic is established.\n";
}
