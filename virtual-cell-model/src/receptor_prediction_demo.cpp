#include "receptor_prediction.hpp"
#include <iostream>
#include <iomanip>
int main(){
 using namespace virtual_cell::prediction;
 Observer a(Memory::Instantaneous),b(Memory::Filtered),c(Memory::Predictive);Compartment cell;
 std::cout<<std::setprecision(17);
 for(double sensed:{1.,1.2,.8,1.5}){
  const auto x=cell.advance(sensed,.1);
  std::cout<<a.forecast(sensed)<<','<<b.forecast(sensed)<<','<<c.forecast(sensed)<<','<<x.after<<'\n';
 }
}
