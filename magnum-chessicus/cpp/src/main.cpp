#include "proof.hpp"
#include <iostream>
int main(int argc,char** argv){try{
 magnum::Config cfg;std::string fen=std::string(chess::constants::STARTPOS),moves,certificate;
 for(int i=1;i<argc;++i){const std::string a=argv[i];auto arg=[&](){if(++i>=argc)throw std::runtime_error("Missing argument");return std::string(argv[i]);};
  if(a=="--verify"){auto b=magnum::check_certificate(arg());std::cout<<"verified ["<<b.lower<<','<<b.upper<<"]\n";return 0;}
  if(a=="--fen")fen=arg();else if(a=="--moves")moves=arg();else if(a=="--depth")cfg.depth=std::stoi(arg());else if(a=="--nodes")cfg.max_nodes=std::stoull(arg());else if(a=="--seconds")cfg.seconds=std::stod(arg());else if(a=="--certificate")certificate=arg();else if(a=="--unguided")cfg.guided=false;else if(a=="--prior-only")cfg.relax=false;else if(a=="--exhaustive")cfg.prune=false;else if(a=="--ungated-claims")cfg.claim_gate=false;else throw std::runtime_error("Unknown option: "+a);}
 magnum::State state(fen);std::istringstream input(moves);std::string m;while(input>>m)state.play(m);
 magnum::Solver solver(cfg);auto p=solver.solve(state);std::uint64_t replayed=0;auto b=magnum::verify(state,*p,cfg.depth,replayed);
 if(!certificate.empty())magnum::save_certificate(certificate,state,cfg.depth,*p);
 const auto action=magnum::certified_action(state,*p);
 std::cout<<"{\"claim_gate\":"<<(cfg.claim_gate?"true":"false")<<",\"certified_action\":\""<<action<<"\",\"ordering_probes\":"<<solver.stats.ordering_probes<<",\"claim_probes\":"<<solver.stats.claim_probes<<",\"status\":\""<<(b.lower==b.upper?"proven":"unresolved")<<"\",\"lower\":"<<b.lower<<",\"upper\":"<<b.upper<<",\"perspective\":\"White\",\"depth\":"<<cfg.depth<<",\"nodes\":"<<solver.stats.nodes<<",\"seconds\":"<<solver.stats.seconds<<",\"cutoffs\":"<<solver.stats.cutoffs<<",\"budget_exhausted\":"<<(solver.stats.exhausted?"true":"false")<<",\"certificate_nodes_checked\":"<<replayed<<"}\n";
 return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
