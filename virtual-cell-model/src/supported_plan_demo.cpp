#include "seeing_person.hpp"
#include "supported_plan.hpp"
#include <iostream>

using namespace virtual_cell;
using namespace virtual_cell::mind;

int main() {
    // Reuse the existing embodied Alex: body, eyes, PersonModel and memory.
    auto embodied_alex = vision::make_seeing_alex();
    auto& alex = embodied_alex.alex;
    auto& memory = alex.brain().memory();

    const auto context = alex.add_context("Considering a response to a queen threat");
    const auto evidence = memory.create<Root>("Supplied observation of a counter-threat");
    const auto plan = memory.create<Root>("Consider blocking the attack with a pawn counter-threat");
    const RecordSupportedPlan skill;

    const auto first = skill.apply(memory, context, evidence, plan);
    std::cout << std::boolalpha;
    std::cout << "Without supplied support, plan recorded: "
              << (first == RecordPlanResult::Recorded) << '\n';

    // Authored lesson input. A later lesson can connect an actual chess verifier.
    memory.relate(evidence, plan, Relation::Supports);
    const auto second = skill.apply(memory, context, evidence, plan);
    std::cout << "With supplied support, plan recorded: "
              << (second == RecordPlanResult::Recorded) << '\n';

    const auto third = skill.apply(memory, context, evidence, plan);
    std::cout << "Repeating the task recognizes the existing record: "
              << (third == RecordPlanResult::AlreadyRecorded) << '\n';
    std::cout << "Plans in this context: " << memory.at(context).elements().size() << '\n';
}
