#pragma once
#include "compatibility.hpp"
#include <chrono>
namespace virtual_cell::mind::comparison {
using Vector = std::vector<double>;
struct Sample { std::size_t iteration, evaluations; double residual; };
struct Result {
    Vector state;
    std::vector<Sample> trace;
    std::size_t evaluations = 0, linear_solves = 0, fallbacks = 0;
    bool converged = false;
};
// Binary categorical fields: x_i is label zero; label one is exactly 1-x_i.
class BinarySystem {
    const CompatibilityField& field_;
    double coupling_;
public:
    BinarySystem(const CompatibilityField& field, double coupling):field_(field),coupling_(coupling) {
        nonnegative(coupling);
        for (const auto& row : field.prior())
            if (row.size()!=2 || row[0]<=0 || row[1]<=0)
                throw std::invalid_argument("Comparison requires positive binary priors");
    }
    Vector initial() const { Vector x; for(const auto& r:field_.prior()) x.push_back(r[0]); return x; }
    Vector residual(const Vector& x, Result& result) const {
        std::vector<Vector> state; for(double v:x) state.push_back({v,1-v});
        auto t=field_.target(state,coupling_); ++result.evaluations;
        Vector f(x.size()); for(std::size_t i=0;i<x.size();++i) f[i]=t[i][0]-x[i]; return f;
    }
};
inline double norm(const Vector& x) { double v=0; for(double a:x) v=std::max(v,std::abs(a)); return v; }
// Partial-pivot dense elimination; failure leaves the caller a safe fallback.
inline bool solve(std::vector<Vector> a, Vector b, Vector& x) {
    const auto n=b.size();
    for(std::size_t k=0;k<n;++k) {
        std::size_t pivot=k;
        for(std::size_t i=k+1;i<n;++i) if(std::abs(a[i][k])>std::abs(a[pivot][k])) pivot=i;
        if(std::abs(a[pivot][k])<1e-12) return false;
        std::swap(a[pivot],a[k]); std::swap(b[pivot],b[k]);
        for(std::size_t i=k+1;i<n;++i) {
            double r=a[i][k]/a[k][k];
            for(std::size_t j=k;j<n;++j) a[i][j]-=r*a[k][j];
            b[i]-=r*b[k];
        }
    }
    x.assign(n,0);
    for(std::size_t ii=n;ii-->0;) { double v=b[ii]; for(std::size_t j=ii+1;j<n;++j) v-=a[ii][j]*x[j]; x[ii]=v/a[ii][ii]; }
    return true;
}
class Solver {
public:
    virtual ~Solver()=default;
    virtual Result run(const BinarySystem&,std::size_t budget=500,double tolerance=1e-10) const=0;
};
class RelaxationSolver final:public Solver {
    double damping_;
public:
    explicit RelaxationSolver(double damping):damping_(damping) {
        if(!std::isfinite(damping)||damping<=0||damping>1) throw std::invalid_argument("Damping");
    }
    Result run(const BinarySystem& system,std::size_t budget=500,double tolerance=1e-10) const override {
        Result r; r.state=system.initial();
        for(std::size_t k=0;k<=budget;++k) {
            auto f=system.residual(r.state,r); double error=norm(f);
            r.trace.push_back({k,r.evaluations,error});
            if(error<=tolerance) {r.converged=true;break;} if(k==budget) break;
            for(std::size_t i=0;i<f.size();++i) r.state[i]+=damping_*f[i];
        } return r;
    }
};
class NewtonSolver final:public Solver {
public:
    Result run(const BinarySystem& system,std::size_t budget=500,double tolerance=1e-10) const override {
        Result r; r.state=system.initial();
        for(std::size_t k=0;k<=budget;++k) {
            auto f=system.residual(r.state,r); const double error=norm(f);
            r.trace.push_back({k,r.evaluations,error});
            if(error<=tolerance) {r.converged=true;break;} if(k==budget) break;
            const auto n=f.size(); std::vector<Vector> jac(n,Vector(n));
            // One-sided finite differences stay inside the simplex. Cost is counted.
            for(std::size_t j=0;j<n;++j) {
                auto y=r.state; double h=y[j]<.5 ? 1e-6 : -1e-6;
                y[j]+=h; auto g=system.residual(y,r);
                for(std::size_t i=0;i<n;++i) jac[i][j]=(g[i]-f[i])/h;
            }
            Vector rhs=f,step; for(auto& v:rhs) v=-v;
            ++r.linear_solves; bool accepted=false;
            if(solve(jac,rhs,step)) {
                double alpha=1;
                for(std::size_t i=0;i<n;++i) {
                    if(step[i]>0) alpha=std::min(alpha,.99*(1-r.state[i])/step[i]);
                    if(step[i]<0) alpha=std::min(alpha,-.99*r.state[i]/step[i]);
                }
                for(int trial=0;trial<24;++trial,alpha*=.5) {
                    auto y=r.state; for(std::size_t i=0;i<n;++i) y[i]+=alpha*step[i];
                    if(norm(system.residual(y,r))<=(1-1e-4*alpha)*error) {r.state=std::move(y);accepted=true;break;}
                }
            }
            if(!accepted) {++r.fallbacks; for(std::size_t i=0;i<n;++i) r.state[i]+=.5*f[i];}
        } return r;
    }
};
} // namespace
