#pragma once
#include "bioelectric.hpp"
#include <random>

namespace virtual_cell::learning {
using Vector = std::vector<double>;
using Matrix = std::vector<Vector>;
struct Neighbor {std::size_t index; double weight;};
struct Example {
    Matrix features;
    std::vector<int> labels; // -1 means unlabelled; never an input feature.
    std::vector<std::vector<Neighbor>> neighbors;
};
struct Forward {
    std::vector<Matrix> states;
    std::vector<Matrix> proposals;
    double last_delta=0;
};
struct LossGradient {double loss; Vector gradient;};

inline Vector softmax(const Vector& logits) {
    const double maximum=*std::max_element(logits.begin(),logits.end());
    Vector result(logits.size()); double sum=0;
    for(std::size_t k=0;k<logits.size();++k){result[k]=std::exp(logits[k]-maximum);sum+=result[k];}
    for(auto& value:result)value/=sum;
    return result;
}
inline Vector softmax_backward(const Vector& probability,const Vector& adjoint) {
    double dot=0;
    for(std::size_t k=0;k<probability.size();++k)dot+=probability[k]*adjoint[k];
    Vector result(probability.size());
    for(std::size_t k=0;k<result.size();++k)result[k]=probability[k]*(adjoint[k]-dot);
    return result;
}

// Finite-depth, prior-anchored categorical relaxation. Same update form as the
// existing CompatibilityField; shared compatibility coefficients are trainable.
// Manual reverse mode includes both initialization and repeated unary injection.
class RelaxationMachine {
    std::size_t feature_count_,label_count_,steps_;
    double mixing_;
    Vector parameters_;
    std::size_t unary(std::size_t feature,std::size_t label) const {return feature*label_count_+label;}
    std::size_t bias(std::size_t label) const {return feature_count_*label_count_+label;}
    std::size_t compatibility(std::size_t a,std::size_t b) const {
        return (feature_count_+1)*label_count_+a*label_count_+b;
    }
    void validate(const Example& e) const {
        if(e.features.empty() || e.features.size()!=e.labels.size() || e.neighbors.size()!=e.features.size())
            throw std::invalid_argument("Invalid graph example dimensions");
        for(std::size_t i=0;i<e.features.size();++i){
            if(e.features[i].size()!=feature_count_)throw std::invalid_argument("Feature count mismatch");
            for(double value:e.features[i]){
                electric::detail::checked(value);
                if(std::abs(value)>6)throw std::invalid_argument("Standardized feature outside [-6,6]");
            }
            if(e.labels[i]<-1 || e.labels[i]>=static_cast<int>(label_count_))throw std::invalid_argument("Invalid reference label");
            double sum=0;
            for(const auto& edge:e.neighbors[i]){
                if(edge.index>=e.features.size())throw std::invalid_argument("Unknown neighbor");
                sum+=electric::detail::nonnegative(edge.weight);
            }
            if(sum>1+1e-12)throw std::invalid_argument("Neighbor weights exceed one");
        }
    }
    Matrix aggregate(const Matrix& states,const Example& e) const {
        Matrix result(states.size(),Vector(label_count_,0));
        for(std::size_t i=0;i<states.size();++i)
            for(const auto& edge:e.neighbors[i])
                for(std::size_t b=0;b<label_count_;++b)result[i][b]+=edge.weight*states[edge.index][b];
        return result;
    }
public:
    RelaxationMachine(std::size_t features,std::size_t labels,std::size_t steps=6,double mixing=.5,unsigned seed=73)
        :feature_count_(features),label_count_(labels),steps_(steps),mixing_(mixing),
         parameters_((features+1)*labels+labels*labels,0) {
        if(!features || labels<2 || steps>100 || !std::isfinite(mixing) || mixing<=0 || mixing>1)
            throw std::invalid_argument("Invalid relaxation machine configuration");
        std::mt19937 generator(seed);std::normal_distribution<double> initial(0,.02);
        for(std::size_t k=0;k<features*labels;++k)parameters_[k]=initial(generator);
    }
    const Vector& parameters() const {return parameters_;}
    std::size_t features() const {return feature_count_;}
    std::size_t labels() const {return label_count_;}
    std::size_t steps() const {return steps_;}
    double mixing() const {return mixing_;}
    std::size_t compatibility_offset() const {return (feature_count_+1)*label_count_;}
    void set_parameters(Vector values) {
        if(values.size()!=parameters_.size())throw std::invalid_argument("Parameter count mismatch");
        for(std::size_t k=0;k<values.size();++k){
            electric::detail::checked(values[k]);
            const double limit=k<compatibility_offset()?5.0:1.5/static_cast<double>(label_count_);
            if(std::abs(values[k])>limit+1e-12)throw std::invalid_argument("Parameter outside projected bounds");
        }
        parameters_=std::move(values);
    }
    void project_and_set(Vector values) {
        if(values.size()!=parameters_.size())throw std::invalid_argument("Parameter count mismatch");
        for(std::size_t k=0;k<values.size();++k){
            electric::detail::checked(values[k]);
            const double limit=k<compatibility_offset()?5.0:1.5/static_cast<double>(label_count_);
            values[k]=std::clamp(values[k],-limit,limit);
        }
        set_parameters(std::move(values));
    }
    double contraction_bound() const {
        double norm=0;
        for(std::size_t a=0;a<label_count_;++a){double sum=0;
            for(std::size_t b=0;b<label_count_;++b)sum+=std::abs(parameters_[compatibility(a,b)]);
            norm=std::max(norm,sum);
        }
        return 1-mixing_+mixing_*.5*norm;
    }
    Forward forward(const Example& e) const {
        validate(e);const auto n=e.features.size();
        Matrix logits(n,Vector(label_count_)),initial(n,Vector(label_count_));
        for(std::size_t i=0;i<n;++i){
            for(std::size_t a=0;a<label_count_;++a){
                logits[i][a]=parameters_[bias(a)];
                for(std::size_t f=0;f<feature_count_;++f)logits[i][a]+=e.features[i][f]*parameters_[unary(f,a)];
            }
            initial[i]=softmax(logits[i]);
        }
        Forward cache;cache.states.push_back(std::move(initial));
        for(std::size_t t=0;t<steps_;++t){
            const auto neighbors=aggregate(cache.states.back(),e);
            Matrix next=cache.states.back(),proposal(n,Vector(label_count_));double delta=0;
            for(std::size_t i=0;i<n;++i){
                Vector z=logits[i];
                for(std::size_t a=0;a<label_count_;++a)
                    for(std::size_t b=0;b<label_count_;++b)z[a]+=parameters_[compatibility(a,b)]*neighbors[i][b];
                proposal[i]=softmax(z);
                for(std::size_t a=0;a<label_count_;++a){
                    next[i][a]=(1-mixing_)*next[i][a]+mixing_*proposal[i][a];
                    delta=std::max(delta,std::abs(next[i][a]-cache.states.back()[i][a]));
                }
            }
            cache.proposals.push_back(std::move(proposal));cache.states.push_back(std::move(next));cache.last_delta=delta;
        }
        return cache;
    }
    LossGradient loss_gradient(const Example& e) const {
        const auto cache=forward(e);const auto n=e.features.size();
        std::size_t labelled=0;for(int label:e.labels)labelled+=label>=0;
        if(!labelled)throw std::invalid_argument("Loss needs a reference label");
        Vector gradient(parameters_.size(),0);Matrix adjoint(n,Vector(label_count_,0)),unary_adjoint=adjoint;
        double loss=0;
        for(std::size_t i=0;i<n;++i)if(e.labels[i]>=0){
            const auto label=static_cast<std::size_t>(e.labels[i]);const double p=cache.states.back()[i][label];
            loss-=std::log(p)/labelled;adjoint[i][label]=-1.0/(labelled*p);
        }
        for(std::size_t t=steps_;t-->0;){
            const auto neighbors=aggregate(cache.states[t],e);
            Matrix previous(n,Vector(label_count_,0));
            for(std::size_t i=0;i<n;++i){
                Vector message=adjoint[i];for(auto& value:message)value*=mixing_;
                const auto dz=softmax_backward(cache.proposals[t][i],message);
                for(std::size_t a=0;a<label_count_;++a){
                    previous[i][a]+=(1-mixing_)*adjoint[i][a];unary_adjoint[i][a]+=dz[a];
                    for(std::size_t b=0;b<label_count_;++b){
                        gradient[compatibility(a,b)]+=dz[a]*neighbors[i][b];
                        for(const auto& edge:e.neighbors[i])previous[edge.index][b]+=edge.weight*parameters_[compatibility(a,b)]*dz[a];
                    }
                }
            }
            adjoint=std::move(previous);
        }
        for(std::size_t i=0;i<n;++i){
            const auto initialization=softmax_backward(cache.states[0][i],adjoint[i]);
            for(std::size_t a=0;a<label_count_;++a){
                const double dz=unary_adjoint[i][a]+initialization[a];gradient[bias(a)]+=dz;
                for(std::size_t f=0;f<feature_count_;++f)gradient[unary(f,a)]+=e.features[i][f]*dz;
            }
        }
        return {loss,std::move(gradient)};
    }
};
class Adam {
    Vector first_,second_;
    std::size_t step_=0;
public:
    explicit Adam(std::size_t parameters):first_(parameters,0),second_(parameters,0) {}
    void update(RelaxationMachine& model,const Vector& gradient,double rate=.02) {
        if(gradient.size()!=first_.size() || model.parameters().size()!=first_.size())throw std::invalid_argument("Optimizer dimensions");
        electric::detail::positive(rate);auto next=model.parameters();++step_;
        for(std::size_t k=0;k<next.size();++k){
            const double g=electric::detail::checked(gradient[k]);
            first_[k]=.9*first_[k]+.1*g;second_[k]=.999*second_[k]+.001*g*g;
            next[k]-=rate*(first_[k]/(1-std::pow(.9,step_)))/(std::sqrt(second_[k]/(1-std::pow(.999,step_)))+1e-8);
        }
        model.project_and_set(std::move(next));
    }
};
} // namespace virtual_cell::learning
