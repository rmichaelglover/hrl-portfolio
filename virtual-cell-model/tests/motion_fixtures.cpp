#include "peaceful_motion.hpp"
#include <iostream>
using namespace virtual_cell::motion;
int main(){
 std::cout<<'[';
 for(int f=0;f<32;++f){
  Agent a[2];a[0].from={0,0};a[1].from={1+.1*(f%3),0};
  for(int i=0;i<2;++i)a[i].count=3;
  a[0].choices[0]={{.6,0},2+f*.001,true};a[0].choices[1]={{0,0},0,true};a[0].choices[2]={{0,.2},-.1,true};
  a[1].choices[0]={{a[1].from.x-.6,0},2,true};a[1].choices[1]={a[1].from,0,true};a[1].choices[2]={{a[1].from.x,-.2},-.1,true};
  Neighbor frog{{.4,.5},{.4,-.5},.3};const auto d=coordinate(a,2,&frog,f%2,f);
  if(f)std::cout<<',';
  std::cout<<"{\"feasible\":"<<(d.feasible?"true":"false")<<",\"chosen\":["<<d.chosen[0]<<','<<d.chosen[1]<<"]}";
 }
 std::cout<<"]\n";
}
