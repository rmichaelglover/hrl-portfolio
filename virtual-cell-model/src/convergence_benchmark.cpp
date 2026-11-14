#include "fixed_point_comparison.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace virtual_cell::mind;
using namespace virtual_cell::mind::comparison;
int main(int argc,char** argv) {
    if(argc!=2) {std::cerr<<"Usage: convergence_benchmark output_directory\n";return 1;}
    const std::string dir=argv[1];
    std::ofstream traces(dir+"/traces.csv"),summary(dir+"/summary.csv"),maps(dir+"/compatibility.csv"),states(dir+"/states.csv");
    if(!traces||!summary||!maps||!states) return 2;
    traces<<"case,solver,iteration,evaluations,residual\n";
    summary<<"case,n,coupling,solver,converged,iterations,evaluations,linear_solves,fallbacks,residual,median_us,min_us,max_us\n";
    maps<<"case,row,column,weight\n"; states<<"case,solver,object,label0\n";
    traces<<std::setprecision(17); summary<<std::setprecision(17); states<<std::setprecision(17);
    for(int c=0;c<5;++c) {
        const std::string name=std::vector<std::string>{"gentle-8","gentle-32","near-critical","strong-agreement","conflicting-ring"}[c];
        const std::size_t n=c==1?32:8;
        const double beta=std::vector<double>{.4,.4, .98,4,6}[c];
        std::vector<Vector> priors; for(std::size_t i=0;i<n;++i) {double p=c==2 ? .50001+.000001*std::sin(double(i)+.3) : .52+.015*std::sin(double(i)+.3); priors.push_back({p,1-p});}
        CompatibilityField field(priors);
        for(std::size_t i=0;i<n;++i) for(auto j:{(i+1)%n,(i+n-1)%n})
            for(std::size_t a=0;a<2;++a) for(std::size_t b=0;b<2;++b) {
                double w=(a==b?.5:-.5)*(c==4?-1:1);
                field.add({i,a,j,b,w}); maps<<name<<','<<2*i+a<<','<<2*j+b<<','<<w<<'\n';
            }
        BinarySystem system(field,beta); RelaxationSolver half(.5),full(1); NewtonSolver newton;
        const Solver* solvers[]={&half,&full,&newton}; const char* names[]={"relax-0.5","relax-1.0","newton"};
        std::vector<double> times[3]; Result results[3];
        // Warmup, then alternate forward/reverse method order over 21 repetitions.
        for(int repetition=-1;repetition<21;++repetition) for(int order=0;order<3;++order) {
            int s=(repetition>=0 && repetition%2)?2-order:order;
            auto start=std::chrono::steady_clock::now(); auto r=solvers[s]->run(system);
            double us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-start).count();
            if(repetition>=0) times[s].push_back(us);
            results[s]=std::move(r);
        }
        for(int s=0;s<3;++s) {
            auto& r=results[s]; auto t=times[s]; std::sort(t.begin(),t.end());
            summary<<name<<','<<n<<','<<beta<<','<<names[s]<<','<<r.converged<<','<<r.trace.back().iteration<<','<<r.evaluations<<','<<r.linear_solves<<','<<r.fallbacks<<','<<r.trace.back().residual<<','<<t[10]<<','<<t.front()<<','<<t.back()<<'\n';
            for(auto v:r.trace) traces<<name<<','<<names[s]<<','<<v.iteration<<','<<v.evaluations<<','<<v.residual<<'\n';
            for(std::size_t i=0;i<n;++i) states<<name<<','<<names[s]<<','<<i<<','<<r.state[i]<<'\n';
        }
    }
}
