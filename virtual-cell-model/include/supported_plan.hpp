#pragma once
#include "relational_memory.hpp"

namespace virtual_cell::mind {

enum class RecordPlanResult {
    NoSupportingEvidence,
    AlreadyRecorded,
    Recorded
};

// A small constructor-like capability: retain the ability to perform the task
// while transforming a person's memory context. Support is supplied evidence;
// this class does not determine chess legality or establish that evidence is true.
class RecordSupportedPlan {
public:
    [[nodiscard]] RecordPlanResult apply(
        Memory& memory, NodeId context, NodeId evidence, NodeId plan) const {
        // Validate every supplied identity before inspecting or changing memory.
        const auto& context_node = memory.at(context);
        memory.at(evidence);
        memory.at(plan);
        if (dynamic_cast<const Root*>(&context_node) == nullptr)
            throw std::invalid_argument("A plan context must be a Root");

        if (!memory.has_edge(evidence, plan, Relation::Supports))
            return RecordPlanResult::NoSupportingEvidence;

        const auto members = context_node.elements();
        if (std::find(members.begin(), members.end(), plan) != members.end())
            return RecordPlanResult::AlreadyRecorded;

        memory.include(context, plan);
        return RecordPlanResult::Recorded;
    }
};

} // namespace virtual_cell::mind
