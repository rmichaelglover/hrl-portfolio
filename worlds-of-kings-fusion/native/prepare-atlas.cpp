// Native build-time preprocessing; no compiler or native executable is required by visitors.
#include <jsoncpp/json/json.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <set>
#include <vector>
int main(int argc,char**argv){
 if(argc!=3){std::cerr<<"usage: prepare-atlas input.json output.json\n";return 2;}
 auto start=std::chrono::steady_clock::now();Json::Value data;std::ifstream input(argv[1]);if(!input||!(input>>data)){std::cerr<<"Invalid atlas\n";return 1;}
 auto &regions=data["regions"];int n=regions.size();std::vector<int> colors(n,-1);std::vector<std::vector<int>> borders(n);std::set<int> pending;
 for(int i=0;i<n;i++)if(!regions[i]["country"].isNull()){pending.insert(i);for(auto &v:regions[i]["neighbors"]){int j=v.asInt();if(j<0||j>=n)return 1;if(!regions[j]["country"].isNull())borders[i].push_back(j);}}
 const std::array<const char*,4> palette={"#bed4aa","#f1dfa0","#cbd0d2","#477553"};std::array<int,4> counts{};
 while(!pending.empty()){int chosen=-1,bestSat=-1,bestDegree=-1;for(int i:pending){unsigned used=0;for(int j:borders[i])if(colors[j]>=0)used|=1u<<colors[j];int sat=__builtin_popcount(used),degree=borders[i].size();if(sat>bestSat||(sat==bestSat&&degree>bestDegree)){chosen=i;bestSat=sat;bestDegree=degree;}}std::array<int,4> used{};for(int j:borders[chosen])if(colors[j]>=0)used[colors[j]]++;int color=0;while(color<4&&used[color])color++;if(color==4)color=std::min_element(used.begin(),used.end())-used.begin();colors[chosen]=color;counts[color]++;regions[chosen]["mapColor"]=palette[color];pending.erase(chosen);}
 // 10-degree bins prune polygon hit tests; the precise spherical test remains in the browser.
 Json::Value bins(Json::objectValue);for(int i=0;i<n;i++){auto e=regions[i]["extent"];int x0=std::clamp(int(std::floor((e[0].asDouble()+180)/10)),0,35),x1=std::clamp(int(std::floor((e[2].asDouble()+180)/10)),0,35),y0=std::clamp(int(std::floor((e[1].asDouble()+90)/10)),0,17),y1=std::clamp(int(std::floor((e[3].asDouble()+90)/10)),0,17);for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)bins[std::to_string(y*36+x)].append(i);}
 data["hitBins"]=bins;data["optimization"]["native_preprocessor"]="C++17";data["optimization"]["polygon_simplification_degrees"]=0.1;int conflicts=0;for(int i=0;i<n;i++)for(int j:borders[i])if(j>i&&colors[i]==colors[j])conflicts++;data["optimization"]["same_color_source_connections"]=conflicts;
 Json::StreamWriterBuilder writer;writer["indentation"]="";writer["precision"]=5;writer["precisionType"]="decimal";std::ofstream output(argv[2]);if(!output)return 1;output<<Json::writeString(writer,data);output.close();if(!output)return 1;
 std::cout<<"Prepared "<<n<<" regions, "<<bins.size()<<" spatial bins; palette counts ";for(int v:counts)std::cout<<v<<' ';std::cout<<"; "<<conflicts<<" same-color tolerance links; "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<" seconds\n";
}
