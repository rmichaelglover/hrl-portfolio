#include "proof.hpp"
#include <iostream>
#include <random>
using namespace magnum;
void check(bool c,const std::string& why){if(!c)throw std::runtime_error(why);}
std::uint64_t perft(Board& b,int depth){if(!depth)return 1;std::uint64_t n=0;for(auto m:legal(b)){b.makeMove(m);n+=perft(b,depth-1);b.unmakeMove(m);}return n;}
Bounds run(State& s,int depth,bool guided=true,bool prune=true){Config c;c.depth=depth;c.guided=guided;c.prune=prune;Solver solver(c);auto p=solver.solve(s);std::uint64_t visited=0;return verify(s,*p,depth,visited);}
int main(){try{
 State initial;const auto saved=initial.board.getFen();const std::array<std::uint64_t,4> totals={20,400,8902,197281};
 for(int d=1;d<=4;++d)check(perft(initial.board,d)==totals[d-1],"Initial perft mismatch");
 check(initial.board.getFen()==saved,"Perft mutated root");
 State kiwi("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1");check(perft(kiwi.board,3)==97862,"Castling-rich perft mismatch");check(!capture_feature(kiwi.board,chess::uci::uciToMove(kiwi.board,"e1g1")),"Castling treated as capture");
 State mate("7k/8/5KQ1/8/8/8/8/8 w - - 0 1");check(run(mate,1)==Bounds{1,1},"Mate missing");check(run(mate,1,false,false)==Bounds{1,1},"Exhaustive disagreement");
 State stale("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1");check(run(stale,0)==Bounds{0,0},"Stalemate missing");
 State dead("7k/8/5K2/8/8/8/8/8 w - - 0 1");check(run(dead,0)==Bounds{0,0},"Dead material missing");
 State repeat;for(int i=0;i<7;++i)repeat.play(std::array<std::string,4>{"g1f3","g8f6","f3g1","f6g8"}[i%4]);
 check(repeat.repetitions()==2,"Wrong pre-claim count");check(can_claim(repeat,legal(repeat.board)),"Intended-move threefold claim missing");
 repeat.play("f6g8");check(repeat.repetitions()==3,"Wrong threefold count");check(!terminal(repeat,legal(repeat.board)).done,"Optional claim made automatic");check(run(repeat,0)==Bounds{0,1},"White claim bound missing");
 for(int i=0;i<8;++i)repeat.play(std::array<std::string,4>{"g1f3","g8f6","f3g1","f6g8"}[i%4]);
 check(run(repeat,0)==Bounds{0,0},"Fivefold missing");State samefen(repeat.board.getFen());check(samefen.repetitions()==1,"Invented FEN history");check(run(samefen,0)==Bounds{},"FEN-only invented a repetition draw");
 State fifty("7k/8/5KQ1/8/8/8/8/8 w - - 99 1");check(can_claim(fifty,legal(fifty.board)),"Intended fifty-move claim missing");check(run(fifty,0)==Bounds{0,1},"Fifty-move claim clamp missing");
 State seventyfive("7k/8/5KQ1/8/8/8/8/8 w - - 150 1");check(run(seventyfive,0)==Bounds{0,0},"75-move automatic draw missing");
 State lastmate("7k/8/5KQ1/8/8/8/8/8 w - - 149 1");lastmate.play("g6g7");check(run(lastmate,0)==Bounds{1,1},"Mate lost priority over 75 moves");
 State pinnedep("k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"),noep("k3r3/8/8/3pP3/8/8/8/4K3 w - - 0 1");check(key(pinnedep.board)==key(noep.board),"Pinned EP changed repetition identity");
 State promotion("k7/6P1/8/8/8/8/8/7K w - - 0 1");int promotions=0;for(auto m:legal(promotion.board))promotions+=m.typeOf()==Move::PROMOTION;check(promotions==4,"Underpromotions excluded");
 Config tiny;tiny.depth=5;tiny.max_nodes=1;Solver limited(tiny);auto truncated=limited.solve(initial);std::uint64_t count=0;check(verify(initial,*truncated,5,count)==Bounds{},"Budget became a proof");check(limited.stats.exhausted,"Budget not reported");
 Config c;c.depth=1;Solver solver(c);auto proof=solver.solve(mate);check(certified_action(mate,*proof)=="g6g7","Certified winning action missing");save_certificate("/tmp/magnum-test.cert",mate,1,*proof);check(check_certificate("/tmp/magnum-test.cert")==Bounds{1,1},"Disk certificate failed");
 auto corrupt=*proof;corrupt.bounds={0,0};bool rejected=false;count=0;try{verify(mate,corrupt,1,count);}catch(...){rejected=true;}check(rejected,"Forged bound accepted");
 corrupt=*proof;corrupt.children.clear();rejected=false;count=0;try{verify(mate,corrupt,1,count);}catch(...){rejected=true;}check(rejected,"Missing winning witness accepted");
 corrupt=*proof;corrupt.children.push_back(corrupt.children[0]);rejected=false;count=0;try{verify(mate,corrupt,1,count);}catch(...){rejected=true;}check(rejected,"Duplicate move accepted");
 corrupt=*proof;corrupt.children[0].first="a1a8";rejected=false;count=0;try{verify(mate,corrupt,1,count);}catch(...){rejected=true;}check(rejected,"Illegal edge accepted");
 State defense("8/1k6/p7/P3Q3/3pPB2/1P1P4/5PB1/4K3 b - - 2 40");Config dc;dc.depth=2;Solver ds(dc);auto dp=ds.solve(defense);
 check(dp->bounds==Bounds{1,1}&&dp->children.size()>1,"Universal-defense fixture did not prove");
 auto missing=*dp;missing.children.pop_back();rejected=false;count=0;try{verify(defense,missing,2,count);}catch(...){rejected=true;}check(rejected,"Missing defensive reply accepted");
 std::mt19937 random(20261113);State walk;
 for(int step=0;step<1000;++step){auto ls=legal(walk.board);if(step%80==0||terminal(walk,ls).done){walk=State{};ls=legal(walk.board);}
  check(walk.repetitions()==static_cast<int>(std::count(walk.history.begin(),walk.history.end(),walk.history.back())),"Occurrence cache drift");
  check(can_claim(walk,ls,nullptr,true)==can_claim(walk,ls,nullptr,false),"Necessary-condition gate disagrees with full claim scan");
  const auto before=walk.history;const auto counts=walk.occurrences;const auto twice=walk.repeated_keys;auto m=ls[random()%ls.size()];walk.push(m);walk.pop(m);check(walk.history==before&&walk.occurrences==counts&&walk.repeated_keys==twice,"Occurrence make/unmake drift");walk.push(m);
 }
 check(run(initial,3,true)==Bounds{}&&run(initial,3,false)==Bounds{},"Initial enclosure changed");
 std::cout<<"PASS: perft, castling, promotions, mate/stalemate/dead material, exact history, intended/current claims, 75-move priority, pinned EP identity, budget bounds and corrupted-certificate rejection\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
