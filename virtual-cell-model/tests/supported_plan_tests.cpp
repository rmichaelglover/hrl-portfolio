#include "seeing_person.hpp"
#include "supported_plan.hpp"
#include <iostream>
using namespace virtual_cell;
using namespace virtual_cell::mind;
void check(bool value,const char* reason) {
    if (!value) throw std::runtime_error(reason);
}
int main() {
    auto embodied = vision::make_seeing_alex();
    auto& alex = embodied.alex;
    auto& memory = alex.brain().memory();
    const auto context = alex.add_context("A tactical question");
    const auto evidence = memory.create<Root>("An observation");
    const auto plan = memory.create<Root>("A candidate plan");
    const RecordSupportedPlan skill;
    check(skill.apply(memory,context,evidence,plan)==RecordPlanResult::NoSupportingEvidence,
          "Absent support was invented");
    check(memory.at(context).elements().empty(),"Unsupported plan changed memory");
    memory.relate(plan,evidence,Relation::Supports);
    check(skill.apply(memory,context,evidence,plan)==RecordPlanResult::NoSupportingEvidence,
          "Support direction was ignored");
    memory.relate(evidence,plan,Relation::Supports);
    check(skill.apply(memory,context,evidence,plan)==RecordPlanResult::Recorded,
          "Supported plan was not recorded");
    check(skill.apply(memory,context,evidence,plan)==RecordPlanResult::AlreadyRecorded,
          "Repeated application was not distinguished");
    check(memory.at(context).elements().size()==1,"Repeated application duplicated the plan");
    const auto another_context=alex.add_context("Another consideration of the plan");
    check(skill.apply(memory,another_context,evidence,plan)==RecordPlanResult::Recorded,
          "Capability could not be reused");
    const auto singleton=memory.create<One>("A single observation",std::array<NodeId,1>{evidence});
    bool rejected=false;
    try { static_cast<void>(skill.apply(memory,singleton,evidence,plan)); }
    catch(const std::invalid_argument&) { rejected=true; }
    check(rejected,"Invalid context type accepted");
    rejected=false;
    try { static_cast<void>(skill.apply(memory,context,evidence,1000000)); }
    catch(const std::out_of_range&) { rejected=true; }
    check(rejected,"Invalid identity accepted");
    check(alex.human().has_organ(OrganKind::Eye),"Existing embodied model lost its eyes");
    std::cout << "Supported-plan task checks passed\n";
}
