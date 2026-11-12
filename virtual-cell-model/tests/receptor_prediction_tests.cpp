#include "receptor_prediction.hpp"
#include <iostream>
using namespace virtual_cell::prediction;
void check(bool x){if(!x)throw std::runtime_error("Receptor prediction invariant failed");}
int main(){
 Compartment c;auto x=c.advance(2,.1);
 check(std::abs(x.after-(2-std::exp(-.1)))<1e-12);
 check(std::abs(x.before+x.incoming-x.outgoing-x.after)<1e-12);
 check(x.atp_fmol==x.incoming);
 Observer a(Memory::Instantaneous),b(Memory::Filtered);
 check(a.forecast(1)==1 && b.forecast(1)==1);
 check(a.forecast(2)==2 && b.forecast(2)<2);
 bool bad=false;try{Compartment invalid(-1);}catch(const std::invalid_argument&){bad=true;}check(bad);
 std::cout<<"Exact compartment solution, material/ATP ledger, and causal observer state passed\n";
}
