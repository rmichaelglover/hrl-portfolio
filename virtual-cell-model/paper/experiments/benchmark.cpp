#include "person_model.hpp"
#include <fstream>
#include <iomanip>
#include <random>
#include <chrono>
using namespace virtual_cell;
using namespace virtual_cell::mind;

struct Metrics { double accuracy, brier, entropy; };
Metrics measure(const std::vector<std::vector<double>>& p, const std::vector<int>& truth) {
    Metrics m{};
    for (std::size_t i=0;i<p.size();++i) {
        m.accuracy += (p[i][1]>p[i][0]) == truth[i];
        m.brier += (p[i][1]-truth[i])*(p[i][1]-truth[i]);
        for (double x:p[i]) if(x>0) m.entropy -= x*std::log(x);
    }
    m.accuracy/=p.size();m.brier/=p.size();m.entropy/=p.size();return m;
}
struct Synthetic {
    std::vector<int> truth;
    std::vector<std::vector<double>> prior;
    std::vector<std::vector<int>> graph;
};
Synthetic generate(unsigned seed) {
    std::mt19937 rng(seed);std::normal_distribution<double> normal(0,1);
    std::uniform_real_distribution<double> uniform(0,1);
    constexpr int n=64;
    Synthetic s; s.truth.resize(n);s.graph.resize(n);
    for(int i=0;i<n;++i)s.truth[i]=i>=n/2;
    std::shuffle(s.truth.begin(),s.truth.end(),rng);
    for(int y:s.truth){double z=(y?1:-1)*0.65+normal(rng)*1.2;
        double p=1/(1+std::exp(-z));s.prior.push_back({1-p,p});}
    for(int i=0;i<n;++i)for(int j=i+1;j<n;++j)
        if(uniform(rng)<(s.truth[i]==s.truth[j]?0.20:0.02)){
            s.graph[i].push_back(j);s.graph[j].push_back(i);}
    return s;
}
LabelField infer(const Synthetic& s,const std::string& mode,double coupling,double damping,std::size_t budget=200) {
    auto prior=s.prior;auto graph=s.graph;
    if(mode=="shared_wrong")for(auto& row:prior)std::swap(row[0],row[1]);
    if(mode=="shuffled"){
        std::mt19937 rng(123456);std::vector<int> perm(s.truth.size());
        for(std::size_t i=0;i<perm.size();++i)perm[i]=static_cast<int>(i);
        std::shuffle(perm.begin(),perm.end(),rng);
        std::vector<std::vector<int>> shuffled(graph.size());
        for(std::size_t i=0;i<graph.size();++i)for(int j:graph[i])shuffled[perm[i]].push_back(perm[j]);
        graph=std::move(shuffled);
    }
    CompatibilityField field(prior);
    for(std::size_t i=0;i<graph.size();++i)for(int j:graph[i])for(std::size_t a=0;a<2;++a)
        field.add({i,a,static_cast<std::size_t>(j),a,1.0/graph[i].size()});
    return field.run(budget,damping,coupling,1e-8);
}
int main(int argc,char**argv){
    if(argc!=2) return 2;
    std::string dir=argv[1];
    std::ofstream out(dir+"/compatibility.csv");out<<std::setprecision(17);
    out<<"seed,condition,accuracy,brier,entropy,iterations,converged,delta\n";
    for(unsigned seed=0;seed<200;++seed){auto s=generate(1000+seed);
        for(const std::string mode:{"prior","valid","shuffled","shared_wrong"}){
            auto r=infer(s,mode,mode=="prior"?0:1.5,0.5);auto m=measure(r.strengths,s.truth);
            out<<seed<<','<<mode<<','<<m.accuracy<<','<<m.brier<<','<<m.entropy<<','<<r.iterations<<','<<r.converged<<','<<r.final_delta<<'\n';
        }}
    std::ofstream grid(dir+"/convergence.csv");grid<<std::setprecision(17);
    grid<<"seed,coupling,damping,accuracy,iterations,converged,delta\n";
    for(unsigned seed=0;seed<20;++seed){auto s=generate(5000+seed);
        for(double coupling:{0.0,0.5,1.5,3.0,6.0})for(double damping:{0.2,0.5,0.8,1.0}){
            auto r=infer(s,"valid",coupling,damping);auto m=measure(r.strengths,s.truth);
            grid<<seed<<','<<coupling<<','<<damping<<','<<m.accuracy<<','<<r.iterations<<','<<r.converged<<','<<r.final_delta<<'\n';}}
    std::ofstream weights(dir+"/policies.csv");weights<<std::setprecision(17);weights<<"health,relationships,resources,selection,c_score,d_score\n";
    std::vector<Candidate> actions{{"C",ObjectiveVector({8,0,7,0,3}),2,true},{"D",ObjectiveVector({6,0,5,0,9}),2,true},
                                 {"dominated",ObjectiveVector({5,0,4,0,2}),2,true},
                                 {"unaffordable",ObjectiveVector({10,10,10,10,10}),20,true}};
    for(int h=0;h<=100;++h)for(int r=0;r<=100-h;++r){int money=100-h-r;
        MultiObjectiveGovernor governor({double(h),0,double(r),0,double(money)});
        auto selected=governor.choose(actions,5);
        weights<<h<<','<<r<<','<<money<<','<<*selected<<','<<governor.score(actions[0].outcomes)<<','<<governor.score(actions[1].outcomes)<<'\n';}
    std::ofstream forecast(dir+"/forecasts.csv");forecast<<std::setprecision(17);
    forecast<<"seed,event,truth_probability,outcome,calibrated,overconfident,underconfident\n";
    for(unsigned seed=0;seed<100;++seed){std::mt19937 rng(8000+seed);std::uniform_real_distribution<double> u(0,1);
        for(int i=0;i<200;++i){double p=0.05+0.9*u(rng);bool y=u(rng)<p;double logit=std::log(p/(1-p));
            forecast<<seed<<','<<i<<','<<p<<','<<y<<','<<p<<','<<1/(1+std::exp(-2*logit))<<','<<1/(1+std::exp(-0.5*logit))<<'\n';}}
    std::ofstream summary(dir+"/summaries.csv");summary<<std::setprecision(17);
    summary<<"branches,true_observations,computed_observations,naive_path_observations,mean_health,visited_nodes\n";
    for(std::size_t branches:{1,2,4,8,16,32}){
        Memory memory;auto root=memory.create<Root>("root");auto shared=memory.create<Root>("shared");
        SummaryStore store;store.record(memory,shared,{ObjectiveVector({8,1,1,1,1}),0.5,"shared observation"});
        for(std::size_t b=0;b<branches;++b){auto child=memory.create<Root>("branch");memory.include(root,child);memory.include(child,shared);
            store.record(memory,child,{ObjectiveVector({2,1,1,1,1}),0.5,"local observation"});}
        memory.include(shared,root);auto result=store.summarize(memory,root);
        summary<<branches<<','<<branches+1<<','<<result.observation_count<<','<<2*branches<<','<<result.mean_outcomes.at(Objective::Health)<<','<<result.visited_nodes<<'\n';}
    std::ofstream safety(dir+"/invariants.csv");safety<<"case,checks,failures\n";
    int transfer_fail=0,energy_fail=0,permission_fail=0;
    const Molecule glycine("glycine",{2,5,1,2});
    for(int n=0;n<1000;++n){Cell a,b;for(int i=0;i<n%20;++i)a.add_molecule(glycine);
        const auto total=a.molecule_count();for(int i=0;i<25;++i)a.transfer_molecule_to(b);
        transfer_fail+=(a.molecule_count()+b.molecule_count()!=total);
        Cell c(5);TransitionProposal proposal(3);ActionEstimate estimate(.8,10,2);
        c.deliberate_and_execute(proposal,estimate,{true,0,0},0);
        c.deliberate_and_execute(proposal,estimate,{true,0,0},0);
        energy_fail+=(c.available_energy()+c.transition_energy()!=5||c.available_energy()!=2);
        Cell d;d.deliberate_and_execute(proposal,estimate,{false,100,100},0);
        permission_fail+=(d.available_energy()!=5||d.state()!=CellState::Undifferentiated);
    }
    safety<<"molecule_transfer,1000,"<<transfer_fail<<"\nenergy_ledger,1000,"<<energy_fail<<"\npermission_gate,1000,"<<permission_fail<<'\n';
    // A deliberately noncontractive inhibitory self-loop: finite budget must report failure.
    std::ofstream stress(dir+"/oscillation.csv");stress<<std::setprecision(17)<<"budget,damping,strength,converged,delta\n";
    for(double damping:{0.2,1.0})for(std::size_t budget=1;budget<=60;++budget){
        CompatibilityField field({{0.51,0.49}});field.add({0,0,0,0,-8});field.add({0,1,0,1,-8});
        auto r=field.run(budget,damping,1,1e-8);stress<<budget<<','<<damping<<','<<r.strengths[0][0]<<','<<r.converged<<','<<r.final_delta<<'\n';}
}
