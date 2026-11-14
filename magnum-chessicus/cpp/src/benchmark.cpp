#include "proof.hpp"
#include <filesystem>
#include <cstdlib>
#include <iostream>
namespace fs=std::filesystem;
using namespace magnum;
struct Game {std::map<std::string,std::string> headers;std::string initial;std::vector<std::string> moves;};
class Reader:public chess::pgn::Visitor {
 Game current;Board board;bool omitted=false;
public:
 std::vector<Game> games;int chapters=0,variants=0;
 void startPgn()override{current=Game{};omitted=false;}
 void header(std::string_view k,std::string_view v)override{current.headers[std::string(k)]=std::string(v);}
 void startMoves()override{
  ++chapters;const auto v=current.headers["Variant"];
  if(!v.empty()&&v!="Standard"&&v!="From Position"){omitted=true;++variants;skipPgn(true);return;}
  current.initial=current.headers.count("FEN")?current.headers["FEN"]:std::string(chess::constants::STARTPOS);
  if(!board.setFen(current.initial))throw std::runtime_error("Invalid PGN FEN");
  validate(board);
 }
 void move(std::string_view san,std::string_view)override{if(omitted)return;
  const auto m=chess::uci::parseSan(board,san);const auto ls=legal(board);if(std::find(ls.begin(),ls.end(),m)==ls.end())throw std::runtime_error("Illegal PGN move");
  current.moves.push_back(chess::uci::moveToUci(m));board.makeMove(m);
 }
 void endPgn()override{if(!omitted)games.push_back(current);}
};
std::string quote(const std::string& text){std::string s="\"";for(char c:text){if(c=='"')s+="\"\"";else s+=c;}return s+'"';}
struct Total{std::uint64_t nodes=0,proven=0,exhausted=0,ordering_probes=0,ordering_candidates=0,claim_probes=0;double seconds=0;};
int main(int argc,char** argv){try{
 if(argc<3)throw std::runtime_error("Usage: magnum_benchmark OUTPUT_DIRECTORY PGN...");
 const bool reverse=std::getenv("MAGNUM_REVERSE_ORDER")!=nullptr;
 const bool claim_gate=std::getenv("MAGNUM_UNGATED_CLAIMS")==nullptr;
 const bool noarchive=std::getenv("MAGNUM_NO_CERTIFICATES")!=nullptr;
 const fs::path out=argv[1];fs::create_directories(out/"certificates");Reader reader;
 for(int i=2;i<argc;++i){std::ifstream input(argv[i]);if(!input)throw std::runtime_error("Cannot open PGN");chess::pgn::StreamParser<> parser(input);const auto error=parser.readGames(reader);if(error)throw std::runtime_error(error.message());}
 std::set<std::string> seen;std::vector<Game> games;std::uint64_t plies=0;
 for(auto& g:reader.games){std::string id=g.headers.count("GameId")?g.headers["GameId"]:g.headers["Site"];std::string identity=id+g.initial;for(auto& m:g.moves)identity+=' '+m;if(seen.insert(identity).second){plies+=g.moves.size();games.push_back(std::move(g));}}
 std::ofstream csv(out/"benchmark.csv");csv<<"game,root_ply,depth,ordering,lower,upper,nodes,seconds,exhausted,ordering_probes,claim_probes,ordering_candidates,certificate,root_fen,played_move\n";
 Total totals[3];int cases=0,mating_games=0;double pair_node_ratio_sum=0;int improved=0,worse=0,equal=0,clock_faster=0,relax_better=0,relax_worse=0,relax_equal=0;
 for(auto& g:games){State end(g.initial);for(auto& m:g.moves)end.play(m);const auto ending=terminal(end,legal(end.board));if(!ending.done||ending.reason!="mate")continue;++mating_games;
  const auto id=g.headers.count("GameId")?g.headers["GameId"]:g.headers["Site"].substr(g.headers["Site"].find_last_of('/')+1);
  for(int depth:{1,3,5}){if(g.moves.size()<static_cast<std::size_t>(depth))continue;const auto ply=g.moves.size()-depth;State root(g.initial);for(std::size_t j=0;j<ply;++j)root.play(g.moves[j]);++cases;Bounds pair[3];Statistics stats[3];
   for(int trial=0;trial<3;++trial){const int mode=reverse?2-trial:trial;const std::string label=mode==0?"legal":mode==1?"prior":"relaxed";Config c;c.depth=depth;c.guided=mode!=0;c.relax=mode==2;c.claim_gate=claim_gate;c.max_nodes=20000;c.seconds=10;Solver solver(c);auto proof=solver.solve(root);std::uint64_t checked=0;const auto bound=verify(root,*proof,depth,checked);pair[mode]=bound;stats[mode]=solver.stats;auto& t=totals[mode];t.nodes+=solver.stats.nodes;t.seconds+=solver.stats.seconds;t.exhausted+=solver.stats.exhausted;t.ordering_probes+=solver.stats.ordering_probes;t.ordering_candidates+=solver.stats.ordering_candidates;t.claim_probes+=solver.stats.claim_probes;
    std::string cert;if(bound.lower==bound.upper){++t.proven;if(!noarchive){cert="certificates/"+id+"-"+std::to_string(ply)+("-"+label+".cert");save_certificate((out/cert).string(),root,depth,*proof);if(!(check_certificate((out/cert).string())==bound))throw std::runtime_error("Disk replay disagreement");}}
    csv<<id<<','<<ply<<','<<depth<<','<<label<<','<<bound.lower<<','<<bound.upper<<','<<solver.stats.nodes<<','<<std::setprecision(10)<<solver.stats.seconds<<','<<solver.stats.exhausted<<','<<solver.stats.ordering_probes<<','<<solver.stats.claim_probes<<','<<solver.stats.ordering_candidates<<','<<cert<<','<<quote(root.board.getFen())<<','<<g.moves[ply]<<'\n';
   }
   for(int a=0;a<3;++a)for(int b=0;b<a;++b)if(pair[a].lower>pair[b].upper||pair[b].lower>pair[a].upper)throw std::runtime_error("Contradictory paired proofs");
   if(stats[2].nodes<stats[0].nodes)++improved;else if(stats[2].nodes>stats[0].nodes)++worse;else ++equal;
   if(stats[2].seconds<stats[0].seconds)++clock_faster;
   if(stats[2].nodes<stats[1].nodes)++relax_better;else if(stats[2].nodes>stats[1].nodes)++relax_worse;else ++relax_equal;
   pair_node_ratio_sum+=double(stats[0].nodes)/std::max<std::uint64_t>(1,stats[2].nodes);
  }
  std::cout<<id<<": "<<cases<<" cases; legal proven "<<totals[0].proven<<", guided "<<totals[2].proven<<'\n';
 }
 std::ofstream report(out/"results.json");report<<"{\"execution_order\":\""<<(reverse?"relaxed-prior-legal":"legal-prior-relaxed")<<"\",\"claim_gate\":"<<(claim_gate?"true":"false")<<",\"source_chapters\":"<<reader.chapters<<",\"excluded_variant_chapters\":"<<reader.variants<<",\"unique_standard_games\":"<<games.size()<<",\"standard_plies_replayed\":"<<plies<<",\"checkmate_games\":"<<mating_games<<",\"paired_positions\":"<<cases<<",\"nodes_per_search\":20000,\"guided_fewer_nodes\":"<<improved<<",\"guided_more_nodes\":"<<worse<<",\"equal_nodes\":"<<equal<<",\"guided_faster_cases\":"<<clock_faster<<",\"mean_paired_node_ratio\":"<<pair_node_ratio_sum/std::max(1,cases)<<",\"relaxation_fewer_nodes_than_prior\":"<<relax_better<<",\"relaxation_more_nodes_than_prior\":"<<relax_worse<<",\"relaxation_equal_nodes_to_prior\":"<<relax_equal<<",\"modes\":[";
 for(int i=0;i<3;++i){if(i)report<<',';report<<"{\"ordering\":\""<<(i==0?"legal":i==1?"prior":"relaxed")<<"\",\"nodes\":"<<totals[i].nodes<<",\"seconds\":"<<totals[i].seconds<<",\"proven\":"<<totals[i].proven<<",\"budget_exhausted\":"<<totals[i].exhausted<<",\"ordering_probes\":"<<totals[i].ordering_probes<<",\"ordering_candidates\":"<<totals[i].ordering_candidates<<",\"claim_probes\":"<<totals[i].claim_probes<<'}';}report<<"]}\n";
 std::cout<<"BENCHMARK COMPLETE\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
