#include "person_model.hpp"
#include <iostream>
#include <iomanip>

using namespace virtual_cell;
int main() {
    std::cout << "# Synthetic parameters; response_proxy is not mood or treatment efficacy.\n";
    std::cout << "profile,external_initial_li_mm,time_s,free_li_inside_mm,productive_fraction,impase_mm_per_s,inositol_mm,response_proxy\n";
    for (const auto& profile: {"coupled", "uncoupled"}) {
        for (double lithium: {0.0,0.5,1.0,2.0}) {
            bio::PhysiologyParameters p;
            if (std::string(profile)=="uncoupled") { p.kinase_gain=0; p.inositol_gain=0; }
            mind::PersonModel person("Synthetic person",3,{1,1,1,1,1});
            person.attach_physiology(bio::illustrative_physiology(bio::Millimolar(lithium),p));
            for (int second=0;second<=60;++second) {
                const auto s=person.physiology().snapshot();
                std::cout << std::setprecision(12) << profile << ',' << lithium << ',' << s.time_seconds
                    << ',' << s.lithium_inside_mm << ',' << s.productive_site_fraction
                    << ',' << s.impase_flux_mm_per_second << ',' << s.inositol_mm
                    << ',' << s.response_proxy << '\n';
                if (second<60) person.advance_physiology(bio::Seconds(1));
            }
        }
    }
}
