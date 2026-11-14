#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>
namespace fs=std::filesystem;
std::vector<std::string> fields(const std::string& line){std::vector<std::string> out;std::string value;bool quoted=false;for(std::size_t i=0;i<line.size();++i){char c=line[i];if(c=='"'){if(quoted&&i+1<line.size()&&line[i+1]=='"'){value+='"';++i;}else quoted=!quoted;}else if(c==','&&!quoted){out.push_back(value);value.clear();}else value+=c;}out.push_back(value);return out;}
using Row=std::map<std::string,std::string>;using Records=std::map<std::string,Row>;
Records read(const fs::path& file){std::ifstream in(file);if(!in)throw std::runtime_error("Cannot read CSV");std::string line;std::getline(in,line);auto headers=fields(line);Records result;while(std::getline(in,line)){if(line.empty())continue;auto values=fields(line);if(values.size()!=headers.size())throw std::runtime_error("CSV width mismatch");Row r;for(std::size_t i=0;i<headers.size();++i)r[headers[i]]=values[i];const auto id=r["game"]+"/"+r["root_ply"]+"/"+r["depth"]+"/"+r["ordering"];if(!result.emplace(id,r).second)throw std::runtime_error("Duplicate benchmark case");}return result;}
std::string bytes(const fs::path& p){std::ifstream in(p,std::ios::binary);if(!in)throw std::runtime_error("Missing certificate");return {std::istreambuf_iterator<char>(in),{}};}
int main(int argc,char** argv){try{if(argc!=3)throw std::runtime_error("Usage: magnum_compare UNGATED_CSV GATED_CSV");auto old=read(argv[1]),now=read(argv[2]);if(old.size()!=now.size())throw std::runtime_error("Different case counts");std::uint64_t certs=0;double old_probes=0,new_probes=0;
 for(const auto& item:old){auto it=now.find(item.first);if(it==now.end())throw std::runtime_error("Missing paired case");const auto& a=item.second;const auto& b=it->second;for(auto col:{"lower","upper","nodes"})if(a.at(col)!=b.at(col))throw std::runtime_error("Changed proof/search result: "+item.first);
  if(!a.at("certificate").empty()){if(b.at("certificate").empty()||bytes(fs::path(argv[1]).parent_path()/a.at("certificate"))!=bytes(fs::path(argv[2]).parent_path()/b.at("certificate")))throw std::runtime_error("Changed certificate bytes");++certs;}
  old_probes+=std::stod(a.at("claim_probes"));new_probes+=std::stod(b.at("claim_probes"));
 }
 std::cout<<"{\"position_mode_pairs\":"<<old.size()<<",\"identical_intervals_and_search_nodes\":true,\"byte_identical_certificates\":"<<certs<<",\"old_claim_probes\":"<<std::fixed<<std::setprecision(0)<<old_probes<<",\"new_claim_probes\":"<<new_probes<<",\"claim_probe_reduction_percent\":"<<std::setprecision(4)<<100*(1-new_probes/old_probes)<<"}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
