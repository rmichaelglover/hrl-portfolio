#include "progression_words.hpp"
#include <iostream>
#include <random>
using namespace magnum;
using namespace magnum::logic;
using namespace magnum::logic::words;
void require(bool value,const char* why) {if(!value) throw std::runtime_error(why);}
template<class F> void rejects(F f) {bool rejected=false;try{f();}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Invalid input accepted");}
int main() {try {
    auto loop=knight_loop();Word zero(loop),one(loop,Natural("1"));RepeatExtension extension;
    rejects([]{Natural invalid("01");});rejects([]{Natural invalid("-1");});rejects([]{Natural invalid("");});
    require(Natural("99999999999999999999").plus(Natural("1"))==Natural("100000000000000000000"),"Carry beyond 64 bits");
    require(Natural("10").bounded_size(10)==10&&!Natural("10").bounded_size(9),"Expansion count bound");
    require(zero.then(one)==one && one.then(zero)==one,"Word identities");
    require(one.successor().cycles()==Natural("2"),"Total symbolic successor");
    std::mt19937 random(20261114);
    for (unsigned i=0;i<1000;++i) {
        const unsigned a=random()%1000,b=random()%1000,c=random()%1000;
        Word x(loop,Natural(std::to_string(a))),y(loop,Natural(std::to_string(b))),z(loop,Natural(std::to_string(c)));
        require(x.then(y).cycles()==Natural(std::to_string(a+b)),"Length addition");
        require(x.then(y).then(z)==x.then(y.then(z)),"Associativity");
        require(extension.repeat(x,y).cycles()==Natural(std::to_string(a*b)),"Repeat multiplication");
        require(extension.repeat(x,y.then(z))==extension.repeat(x,y).then(extension.repeat(x,z)),"Repeat distribution");
    }
    Word huge(loop,Natural("10000000000000000000000000000000000000000"));
    require(huge.successor().cycles().decimal()=="10000000000000000000000000000000000000001","Huge successor");
    require(extension.repeat(huge,huge).cycles().decimal()=="1"+std::string(80,'0'),"Huge exact repetition");
    Word nines(loop,Natural(std::string(40,'9')));
    require(extension.repeat(nines,nines).cycles().decimal()==std::string(39,'9')+"8"+std::string(39,'0')+"1","Long multiplication carry chain");
    const Natural size_max(std::to_string(std::numeric_limits<std::size_t>::max()));
    require(size_max.bounded_size(std::numeric_limits<std::size_t>::max())==std::numeric_limits<std::size_t>::max(),"Maximum machine size boundary");
    require(!size_max.plus(Natural("1")).bounded_size(std::numeric_limits<std::size_t>::max()),"Conversion overflow");
    require(Natural("9")<Natural("10") && Natural("11")<Natural("12"),"Natural order");
    require(extension.repeat(huge,zero)==zero,"Zero repetitions");
    require(unnumber(number(huge.text()))==huge.text(),"Exact compressed-word coding");
    bool exhausted=false;try{huge.materialize(100);}catch(const ResourceLimit&){exhausted=true;}require(exhausted,"Huge expansion silently truncated");
    require(zero.materialize(0).empty(),"Empty expansion");
    Word two(loop,Natural("2"));auto ordinary=two.materialize(8);
    Progression standard(State{},ordinary);require(standard.length()==8,"Short word standard replay");
    bool stopped=false;try{Progression too_long(State{},Word(loop,Natural("5")).materialize(20));}catch(const std::invalid_argument&){stopped=true;}
    require(stopped,"Standard rules silently replaced by variant");
    // Independently replay a concrete word beyond the standard draw boundary.
    auto board=loop->root();auto long_moves=Word(loop,Natural("40")).materialize(160);
    for (const auto& uci:long_moves) {
        auto move=chess::uci::uciToMove(board,uci);auto choices=legal(board);
        require(std::find(choices.begin(),choices.end(),move)!=choices.end(),"Variant replay legality");
        board.makeMove(move);board=projected_board(board);
    }
    require(key(board)==key(loop->root()),"Variant loop endpoint");
    rejects([]{LoopCertificate invalid(State{},{"e2e5"},movement_only);});
    rejects([]{LoopCertificate invalid(State{},{"e2e4"},movement_only);});
    rejects([]{LoopCertificate invalid(State{},{},movement_only);});
    auto other=std::make_shared<LoopCertificate>(State{},std::vector<std::string>{"b1c3","b8c6","c3b1","c6b8"},movement_only);
    rejects([&]{one.then(Word(other,Natural("1")));});
    rejects([&]{extension.repeat(one,Word(other));});
    require(loop->signature()==knight_loop()->signature(),"Certificate reproducibility");
    std::cout<<"PASS: loop certificate, standard/variant separation, 160-ply replay, exact huge naturals, 1000 additive/repetition cases, coding and bounded materialization\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
