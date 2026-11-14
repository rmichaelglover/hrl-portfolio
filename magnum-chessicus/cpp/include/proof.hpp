#pragma once
// Michael Emanuel Glover's Magnum Chessicus: native continuation of sound
// outcome intervals and research-guided bounded proofs. Heuristics only order.
#include "../vendor/chess.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <map>
#include <memory>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <unordered_map>
namespace magnum {
using chess::Board;using chess::Move;using chess::Movelist;using chess::Color;using chess::PieceType;
struct Bounds {int lower=-1,upper=1;bool operator==(Bounds v)const{return lower==v.lower&&upper==v.upper;}};
inline Movelist legal(const Board& b){Movelist m;chess::movegen::legalmoves(m,b);return m;}
inline std::string key(const Board& b){
 std::istringstream in(b.getFen());std::string placement,turn,rights,ep;in>>placement>>turn>>rights>>ep;
 if(ep!="-"){bool possible=false;for(auto m:legal(b))if(m.typeOf()==Move::ENPASSANT)possible=true;if(!possible)ep="-";}
 return placement+" "+turn+" "+rights+" "+ep;
}
inline void validate(const Board& b){
 if(b.pieces(PieceType::KING,Color::WHITE).count()!=1||b.pieces(PieceType::KING,Color::BLACK).count()!=1)throw std::runtime_error("Exactly two kings required");
 if(b.isAttacked(b.kingSq(~b.sideToMove()),b.sideToMove()))throw std::runtime_error("Side that just moved remains in check");
 for(int i=0;i<64;++i){const auto sq=chess::Square(i);if(b.at(sq).type()==PieceType::PAWN&&(i<8||i>=56))throw std::runtime_error("Pawn on promotion rank");}
}
struct State {
 Board board;std::string initial;std::vector<std::string> root_moves,history;
 std::unordered_map<std::string,unsigned> occurrences;unsigned repeated_keys=0;
 explicit State(std::string fen=std::string(chess::constants::STARTPOS)):initial(std::move(fen)){
  if(!board.setFen(initial))throw std::runtime_error("Invalid FEN");
  validate(board);history.push_back(key(board));occurrences[history.back()]=1;
 }
 void push(Move m){board.makeMove(m);history.push_back(key(board));auto& count=occurrences[history.back()];if(count==1)++repeated_keys;++count;}
 void pop(Move m){auto it=occurrences.find(history.back());if(it->second==2)--repeated_keys;if(--it->second==0)occurrences.erase(it);history.pop_back();board.unmakeMove(m);}
 void play(const std::string& uci){auto m=chess::uci::uciToMove(board,uci);auto ls=legal(board);if(std::find(ls.begin(),ls.end(),m)==ls.end())throw std::runtime_error("Illegal root move: "+uci);push(m);root_moves.push_back(uci);}
 int repetitions()const{return static_cast<int>(occurrences.at(history.back()));}
};
inline bool dead_material(const Board& b){
 int minors=0,knights=0,bishop_color=-1;
 for(int i=0;i<64;++i){const auto t=b.at(chess::Square(i)).type();
  if(t==PieceType::NONE||t==PieceType::KING)continue;
  if(t==PieceType::PAWN||t==PieceType::ROOK||t==PieceType::QUEEN)return false;
  ++minors;if(t==PieceType::KNIGHT)++knights;
  else {const int color=((i%8)+(i/8))%2;if(bishop_color<0)bishop_color=color;else if(bishop_color!=color)bishop_color=2;}
 }
 return minors<=1||(knights==0&&bishop_color<2);
}
struct Terminal {bool done=false;Bounds bounds;std::string reason;};
inline Terminal terminal(const State& s,const Movelist& moves){
 if(moves.empty()){
  if(s.board.inCheck()){const int v=s.board.sideToMove()==Color::WHITE?-1:1;return {true,{v,v},"mate"};}
  return {true,{0,0},"stalemate"};
 }
 if(dead_material(s.board))return {true,{0,0},"dead-material"};
 if(s.repetitions()>=5)return {true,{0,0},"fivefold"};
 if(s.board.halfMoveClock()>=150)return {true,{0,0},"75-move"};
 return {};
}
inline bool claim_now(const State& s){return s.repetitions()>=3||s.board.halfMoveClock()>=100;}
inline bool can_claim(State& s,const Movelist& moves,std::uint64_t* probes=nullptr,bool gated=true){
 const auto claim=[&](){return (gated?s.repetitions():static_cast<int>(std::count(s.history.begin(),s.history.end(),s.history.back())))>=3||s.board.halfMoveClock()>=100;};
 if(claim())return true;
 // Necessary conditions: a next quiet move raises the clock by at most one;
 // a third occurrence requires an already twice-recorded destination position.
 if(gated&&s.board.halfMoveClock()<99&&s.repeated_keys==0)return false;
 for(auto m:moves){if(probes)++*probes;s.push(m);bool available=claim();
  if(available){const auto next=legal(s.board);if(next.empty()&&s.board.inCheck())available=false;}
  s.pop(m);if(available)return true;
 }
 return false;
}
struct Proof {char kind='F';Bounds bounds;std::string reason="budget";std::vector<std::pair<std::string,std::shared_ptr<Proof>>> children;};
struct Statistics {std::uint64_t nodes=0,cutoffs=0,ordered=0,ordering_probes=0,ordering_candidates=0,claim_probes=0;bool exhausted=false;double seconds=0;};
struct Config {int depth=3;std::uint64_t max_nodes=1000000;double seconds=30;bool guided=true,prune=true,relax=true,claim_gate=true;};
inline Bounds combine(const Board& b,bool claim,const Movelist& moves,const std::map<std::string,Bounds>& children){
 const bool white=b.sideToMove()==Color::WHITE;
 Bounds r=claim?Bounds{0,0}:white?Bounds{-1,-1}:Bounds{1,1};
 for(auto m:moves){auto it=children.find(chess::uci::moveToUci(m));const Bounds v=it==children.end()?Bounds{}:it->second;
  if(white){r.lower=std::max(r.lower,v.lower);r.upper=std::max(r.upper,v.upper);}
  else{r.lower=std::min(r.lower,v.lower);r.upper=std::min(r.upper,v.upper);}}
 return r;
}
inline bool capture_feature(const Board& b,Move m){return m.typeOf()!=Move::CASTLING&&(b.at(m.to())!=chess::Piece::NONE||m.typeOf()==Move::ENPASSANT);}
// Continuation of chess_logic.py's shared-plan cosine compatibility and
// normalized multiplicative support, using an explicitly documented C++ feature set.
inline std::vector<Move> order(State& s,const Movelist& input,bool relaxation=true,std::uint64_t* probes=nullptr){
 std::vector<Move> moves(input.begin(),input.end());const auto n=moves.size();
 std::vector<std::array<double,6>> plans;std::vector<double> prior(n),p(n),next(n),norms(n);
 const Color us=s.board.sideToMove();
 for(std::size_t i=0;i<n;++i){const auto m=moves[i];const auto from=s.board.at(m.from()).type();const bool capture=capture_feature(s.board,m);
  const bool check=s.board.givesCheck(m)!=chess::CheckType::NO_CHECK;bool mate=false;
  if(check){if(probes)++*probes;s.push(m);mate=legal(s.board).empty();s.pop(m);}
  const auto sq=m.to();const int x=static_cast<int>(sq.file()),y=static_cast<int>(sq.rank());
  const double center=1.-(std::abs(x-3.5)+std::abs(y-3.5))/7.;
  const bool development=(from==PieceType::KNIGHT||from==PieceType::BISHOP)&&static_cast<int>(m.from().rank())==(us==Color::WHITE?0:7);
  plans.push_back({double(check),double(capture),double(m.typeOf()==Move::PROMOTION),double(development),center,double(from==PieceType::QUEEN)});
  double norm=0;for(double v:plans.back())norm+=v*v;norms[i]=std::sqrt(norm);
  prior[i]=std::exp(std::min(20.,12.*mate+3.*check+1.4*capture+2.*(m.typeOf()==Move::PROMOTION)+.3*development+.2*center));
 }
 const double total=std::accumulate(prior.begin(),prior.end(),0.);for(std::size_t i=0;i<n;++i)p[i]=prior[i]/total;
 for(int round=0;round<(relaxation?8:0);++round){double sum=0;
  for(std::size_t i=0;i<n;++i){double support=0;for(std::size_t j=0;j<n;++j)if(i!=j&&norms[i]>0&&norms[j]>0){double dot=0;for(int k=0;k<6;++k)dot+=plans[i][k]*plans[j][k];support+=dot/(norms[i]*norms[j])*p[j];}
   next[i]=p[i]*(1+support);sum+=next[i];}
  for(std::size_t i=0;i<n;++i)p[i]=next[i]/sum;
 }
 std::vector<std::size_t> indices(n);std::iota(indices.begin(),indices.end(),0);
 std::stable_sort(indices.begin(),indices.end(),[&](auto a,auto b){return p[a]>p[b];});
 std::vector<Move> sorted;for(auto i:indices)sorted.push_back(moves[i]);return sorted;
}
class Solver {
 Config config;std::chrono::steady_clock::time_point start;
 bool stop(){if(stats.nodes>=config.max_nodes||std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=config.seconds){stats.exhausted=true;return true;}return false;}
 std::shared_ptr<Proof> visit(State& s,int depth){
  auto proof=std::make_shared<Proof>();if(stop())return proof;++stats.nodes;
  const auto moves=legal(s.board);const auto t=terminal(s,moves);
  if(t.done){proof->kind='T';proof->bounds=t.bounds;proof->reason=t.reason;return proof;}
  const bool claim=can_claim(s,moves,&stats.claim_probes,config.claim_gate);
  if(depth==0){proof->reason="depth";if(claim)proof->bounds=s.board.sideToMove()==Color::WHITE?Bounds{0,1}:Bounds{-1,0};return proof;}
  proof->kind='B';proof->reason="search";std::map<std::string,Bounds> childbounds;
  if(config.guided)stats.ordering_candidates+=moves.size();
  auto sequence=config.guided?order(s,moves,config.relax,&stats.ordering_probes):std::vector<Move>(moves.begin(),moves.end());if(config.guided)++stats.ordered;
  for(auto m:sequence){if(stop())break;const auto name=chess::uci::moveToUci(m);s.push(m);auto child=visit(s,depth-1);s.pop(m);childbounds[name]=child->bounds;proof->children.emplace_back(name,child);
   proof->bounds=combine(s.board,claim,moves,childbounds);
   if(config.prune&&((s.board.sideToMove()==Color::WHITE&&proof->bounds.lower==1)||(s.board.sideToMove()==Color::BLACK&&proof->bounds.upper==-1))){++stats.cutoffs;break;}}
  proof->bounds=combine(s.board,claim,moves,childbounds);return proof;
 }
public:
 Statistics stats;
 explicit Solver(Config c):config(c){if(c.depth<0||c.depth>64||!c.max_nodes||c.seconds<=0||!std::isfinite(c.seconds))throw std::runtime_error("Invalid search budget");}
 std::shared_ptr<Proof> solve(State& s){const auto before=s.board.getFen();const auto history=s.history;start=std::chrono::steady_clock::now();auto p=visit(s,config.depth);stats.seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();if(before!=s.board.getFen()||history!=s.history)throw std::runtime_error("Search mutated root");return p;}
};
// Separate replay; it never calls order(), Solver, or trusts stored node scores.
inline Bounds verify(State& s,const Proof& p,int depth,std::uint64_t& visited){
 if(++visited>10000000)throw std::runtime_error("Certificate too large");
 if(p.bounds.lower< -1||p.bounds.upper>1||p.bounds.lower>p.bounds.upper)throw std::runtime_error("Invalid claimed interval");
 if(p.kind=='F'&&p.reason=="budget"&&p.bounds==Bounds{}){if(!p.children.empty())throw std::runtime_error("Frontier has children");return {};}
 const auto moves=legal(s.board);const auto t=terminal(s,moves);Bounds expected;
 if(p.kind=='T'){if(!t.done||!p.children.empty()||p.reason!=t.reason)throw std::runtime_error("False terminal");expected=t.bounds;}
 else if(p.kind=='F'){if(depth!=0||t.done||!p.children.empty()||p.reason!="depth")throw std::runtime_error("Invalid depth frontier");const bool claim=can_claim(s,moves,nullptr,false);if(claim)expected=s.board.sideToMove()==Color::WHITE?Bounds{0,1}:Bounds{-1,0};}
 else if(p.kind=='B'){
  if(depth<=0||t.done||p.reason!="search")throw std::runtime_error("Invalid branch");
  std::map<std::string,Bounds> children;std::map<std::string,Move> names;for(auto m:moves)names.emplace(chess::uci::moveToUci(m),m);
  for(const auto& edge:p.children){auto it=names.find(edge.first);if(it==names.end()||children.count(edge.first))throw std::runtime_error("Illegal or duplicate certificate edge");s.push(it->second);Bounds child;try{child=verify(s,*edge.second,depth-1,visited);}catch(...){s.pop(it->second);throw;}s.pop(it->second);children.emplace(edge.first,child);}
  expected=combine(s.board,can_claim(s,moves,nullptr,false),moves,children);
 }else throw std::runtime_error("Unknown certificate kind");
 if(!(expected==p.bounds))throw std::runtime_error("Certificate interval not justified by replay");
 return expected;
}
inline std::string certified_action(State& s,const Proof& p){
 if(p.bounds.lower!=p.bounds.upper)return {};
 const auto moves=legal(s.board);if(terminal(s,moves).done)return "terminal";
 if(p.bounds.lower==0){
  if(claim_now(s))return "claim_draw_now";
  for(auto m:moves){s.push(m);bool claim=claim_now(s);if(claim){const auto next=legal(s.board);if(next.empty()&&s.board.inCheck())claim=false;}s.pop(m);if(claim)return "claim_draw_with "+chess::uci::moveToUci(m);}
 }
 const bool white=s.board.sideToMove()==Color::WHITE;
 for(const auto& child:p.children)
  if((white&&child.second->bounds.lower>=p.bounds.lower)||(!white&&child.second->bounds.upper<=p.bounds.upper))return child.first;
 // When every continuation loses, any legal move is outcome-optimal.
 if((white&&p.bounds.upper==-1)||(!white&&p.bounds.lower==1))return chess::uci::moveToUci(moves[0]);
 throw std::runtime_error("Exact interval lacks a certified action");
}

inline void write_node(std::ostream& out,const Proof& p){out<<p.kind<<' '<<p.bounds.lower<<' '<<p.bounds.upper<<' '<<std::quoted(p.reason)<<' '<<p.children.size()<<'\n';for(const auto& e:p.children){out<<std::quoted(e.first)<<'\n';write_node(out,*e.second);}}
inline std::shared_ptr<Proof> read_node(std::istream& in,int nesting,std::uint64_t& count){
 if(nesting>65||++count>10000000)throw std::runtime_error("Certificate size/depth exceeded");
 auto p=std::make_shared<Proof>();std::size_t n;
 if(!(in>>p->kind>>p->bounds.lower>>p->bounds.upper>>std::quoted(p->reason)>>n)||n>256)throw std::runtime_error("Invalid certificate node");
 for(std::size_t i=0;i<n;++i){std::string m;if(!(in>>std::quoted(m)))throw std::runtime_error("Missing move");p->children.emplace_back(m,read_node(in,nesting+1,count));}return p;
}
inline void save_certificate(const std::string& path,const State& root,int depth,const Proof& p){std::ofstream out(path);if(!out)throw std::runtime_error("Cannot write certificate");out<<"MAGNUM_CPP_V1\n"<<std::quoted(root.initial)<<'\n'<<root.root_moves.size()<<'\n';for(auto& m:root.root_moves)out<<std::quoted(m)<<'\n';out<<depth<<'\n';write_node(out,p);}
inline Bounds check_certificate(const std::string& path){
 std::ifstream in(path);std::string magic,fen;std::size_t n;int depth;
 if(!(in>>magic>>std::quoted(fen)>>n)||magic!="MAGNUM_CPP_V1"||n>20000)throw std::runtime_error("Invalid certificate header");
 State root(fen);
 for(std::size_t i=0;i<n;++i){std::string m;if(!(in>>std::quoted(m)))throw std::runtime_error("Missing root history");root.play(m);}
 if(!(in>>depth)||depth<0||depth>64)throw std::runtime_error("Invalid certificate depth");
 std::uint64_t count=0;auto p=read_node(in,0,count);in>>std::ws;if(!in.eof())throw std::runtime_error("Trailing certificate data");std::uint64_t visited=0;return verify(root,*p,depth,visited);
}
} // namespace magnum
