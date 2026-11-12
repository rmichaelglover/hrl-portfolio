#include "trainable_relaxation.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace virtual_cell::learning;
struct Dataset {std::vector<Example> examples;std::size_t features=0;};
Dataset read_data(const std::string& path){
    std::ifstream stream(path);std::size_t n=0,f=0;
    if(!(stream>>n>>f) || !n || !f || n>1000000 || f>64)throw std::invalid_argument("Invalid dataset header");
    Dataset result;result.features=f;long previous_group=-1;std::vector<long> epochs;
    auto finish=[&](){if(result.examples.empty())return;auto& e=result.examples.back();e.neighbors.resize(e.features.size());
        for(std::size_t i=0;i<epochs.size();++i){
            if(i && epochs[i]==epochs[i-1]+1)e.neighbors[i].push_back({i-1,1});
            if(i+1<epochs.size() && epochs[i+1]==epochs[i]+1)e.neighbors[i].push_back({i+1,1});
            for(auto& edge:e.neighbors[i])edge.weight/=e.neighbors[i].size();
        }
    };
    for(std::size_t i=0;i<n;++i){long group,epoch;int label;
        if(!(stream>>group>>epoch>>label) || group<0 || epoch<0)throw std::invalid_argument("Invalid dataset row");
        if(group!=previous_group){if(previous_group>=0 && group<=previous_group)throw std::invalid_argument("Groups must increase");finish();result.examples.push_back({});epochs.clear();previous_group=group;}
        if(!epochs.empty() && epoch<=epochs.back())throw std::invalid_argument("Epochs must increase");
        Vector row(f);for(auto& value:row)if(!(stream>>value))throw std::invalid_argument("Missing feature");
        result.examples.back().features.push_back(std::move(row));result.examples.back().labels.push_back(label);epochs.push_back(epoch);
    }
    finish();std::string extra;if(stream>>extra)throw std::invalid_argument("Trailing dataset fields");return result;
}
std::size_t count(const Example& e){std::size_t n=0;for(int label:e.labels)n+=label>=0;return n;}
LossGradient evaluate(const RelaxationMachine& model,const Dataset& data,bool gradient){
    LossGradient result{0,Vector(model.parameters().size(),0)};double total=0;
    for(const auto& e:data.examples){const double n=count(e);if(!n)continue;const auto value=model.loss_gradient(e);total+=n;result.loss+=n*value.loss;
        if(gradient)for(std::size_t k=0;k<result.gradient.size();++k)result.gradient[k]+=n*value.gradient[k];
    }
    if(total==0)throw std::invalid_argument("Dataset has no labels");
    result.loss/=total;
    if(gradient)for(auto& value:result.gradient)value/=total;
    return result;
}
void save(const RelaxationMachine& model,const std::string& path){
    std::ofstream out(path);if(!out)throw std::runtime_error("Cannot save model");out<<std::setprecision(17);
    out<<model.features()<<' '<<model.labels()<<' '<<model.steps()<<' '<<model.mixing()<<'\n';
    for(double value:model.parameters())out<<value<<' ';
    out<<'\n';
}
RelaxationMachine load(const std::string& path){
    std::ifstream in(path);std::size_t f,c,t;double a;if(!(in>>f>>c>>t>>a)||!f||f>64||c<2||c>16)throw std::invalid_argument("Invalid model file");
    RelaxationMachine model(f,c,t,a);auto p=model.parameters();for(auto& value:p)if(!(in>>value))throw std::invalid_argument("Truncated model");
    std::string extra;if(in>>extra)throw std::invalid_argument("Trailing model fields");model.set_parameters(std::move(p));return model;
}
void print_vector(const Vector& v){std::cout<<'[';for(std::size_t i=0;i<v.size();++i){if(i)std::cout<<',';std::cout<<v[i];}std::cout<<']';}
int main(int argc,char** argv){try{
    std::cout<<std::setprecision(17);
    if(argc==2 && std::string(argv[1])=="probe"){
        Example e{{{-.8,.3},{.5,.8},{.1,-.6},{.9,-.2}},{0,1,-1,1},{{{1,.7},{2,.3}},{{0,1}},{},{{3,1}}}};
        RelaxationMachine model(2,2,3,.5);auto p=model.parameters();for(std::size_t k=0;k<p.size();++k)p[k]=.2*std::sin(k+.2);model.set_parameters(p);
        const auto gradient=model.loss_gradient(e);const auto forward=model.forward(e);
        std::cout<<"{\"loss\":"<<gradient.loss<<",\"parameters\":";print_vector(p);std::cout<<",\"gradient\":";print_vector(gradient.gradient);
        std::cout<<",\"strengths\":[";for(std::size_t i=0;i<4;++i){if(i)std::cout<<',';print_vector(forward.states.back()[i]);}std::cout<<"]}\n";return 0;
    }
    if(argc==10 && std::string(argv[1])=="train"){
        const auto train=read_data(argv[2]),validation=read_data(argv[3]);if(train.features!=validation.features)throw std::invalid_argument("Train/validation feature mismatch");
        const auto steps=static_cast<std::size_t>(std::stoul(argv[6]));const int epochs=std::stoi(argv[7]);const unsigned seed=std::stoul(argv[8]);const double rate=std::stod(argv[9]);
        if(epochs<1 || epochs>2000)throw std::invalid_argument("Epoch budget outside [1,2000]");
        RelaxationMachine model(train.features,2,steps,.5,seed);Adam optimizer(model.parameters().size());auto best=model.parameters();double best_loss=evaluate(model,validation,false).loss;int best_epoch=0;
        std::ofstream history(argv[5]);history<<"epoch,train_nll,validation_nll,gradient_norm,contraction_bound\n";
        constexpr double l2=.001;
        for(int epoch=1;epoch<=epochs;++epoch){
            auto value=evaluate(model,train,true);double norm=0;
            for(std::size_t k=0;k<value.gradient.size();++k){value.gradient[k]+=l2*model.parameters()[k];norm+=value.gradient[k]*value.gradient[k];}
            optimizer.update(model,value.gradient,rate);const double held=evaluate(model,validation,false).loss;
            history<<std::setprecision(17)<<epoch<<','<<value.loss<<','<<held<<','<<std::sqrt(norm)<<','<<model.contraction_bound()<<'\n';
            if(held<best_loss){best_loss=held;best=model.parameters();best_epoch=epoch;}
            if(epoch-best_epoch>=35)break;
        }
        model.set_parameters(best);save(model,argv[4]);
        std::cout<<"{\"best_epoch\":"<<best_epoch<<",\"validation_nll\":"<<best_loss<<",\"training_nll\":"<<evaluate(model,train,false).loss<<",\"contraction_bound\":"<<model.contraction_bound()<<"}\n";return 0;
    }
    if(argc==4 && std::string(argv[1])=="predict"){
        const auto model=load(argv[2]);const auto data=read_data(argv[3]);std::cout<<"sequence,node,label,p_nonrem,p_rem,last_delta\n";
        for(std::size_t k=0;k<data.examples.size();++k){const auto& e=data.examples[k];const auto result=model.forward(e);
            for(std::size_t i=0;i<e.features.size();++i)std::cout<<k<<','<<i<<','<<e.labels[i]<<','<<result.states.back()[i][0]<<','<<result.states.back()[i][1]<<','<<result.last_delta<<'\n';
        }return 0;
    }
    std::cerr<<"Usage: probe | train train.txt validation.txt model.txt history.csv steps epochs seed rate | predict model.txt data.txt\n";return 2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
