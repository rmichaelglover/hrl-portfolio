#include "impase_assay.hpp"
#include <iomanip>
#include <iostream>
#include <sstream>

using namespace virtual_cell::bio::assay;
int main() {
    // Batch protocol for comparing the fitted Python and C++ implementations.
    // model,V,half,hill,inhibition,Kis,Kii,substrate,Mg,Li -> Delta A360/min
    try {
        std::string line;
        while (std::getline(std::cin,line)) {
            if (line.empty()) continue;
            std::replace(line.begin(),line.end(),',',' ');
            std::istringstream input(line);
            int model;
            Parameters p; double substrate,magnesium,lithium;
            if (!(input>>model>>p.maximum>>p.half_mm>>p.hill>>p.inhibition_mm
                    >>p.lithium_slope_mm>>p.lithium_intercept_mm>>substrate>>magnesium>>lithium)
                || model<0 || model>6)
                throw std::invalid_argument("Invalid batch assay row");
            const Conditions conditions{model<3?Substrate::Inositol1Phosphate:Substrate::Ribose5Phosphate,
                                         substrate,magnesium,lithium};
            std::cout<<std::setprecision(17)<<InitialRateModel(static_cast<Mechanism>(model),p)
                .rate_abs_per_min(conditions)<<'\n';
        }
    } catch (const std::exception& error) {
        std::cerr<<error.what()<<'\n'; return 1;
    }
}
