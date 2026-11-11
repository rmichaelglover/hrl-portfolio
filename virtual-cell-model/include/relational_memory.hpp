#pragma once

#include "virtual_cell.hpp"
#include <memory>
#include <optional>

namespace virtual_cell::mind {

using NodeId = std::size_t;

// Michael's NullSet is a container interface, not the mathematical empty set.
class NullSet {
    std::string name_;
public:
    explicit NullSet(std::string name) : name_(std::move(name)) {}
    virtual ~NullSet() = default;
    const std::string& name() const { return name_; }
    virtual std::vector<NodeId> elements() const = 0;
};

template<std::size_t N>
class FixedSet : public NullSet {
    std::array<NodeId, N> elements_;
public:
    FixedSet(std::string name, std::array<NodeId, N> elements)
        : NullSet(std::move(name)), elements_(elements) {
        std::set<NodeId> unique(elements.begin(), elements.end());
        if (unique.size() != N) throw std::invalid_argument("Set members must be distinct");
    }
    std::vector<NodeId> elements() const override {
        return {elements_.begin(), elements_.end()};
    }
};

class One final : public FixedSet<1> { public: using FixedSet<1>::FixedSet; };
class Two final : public FixedSet<2> { public: using FixedSet<2>::FixedSet; };
class Three final : public FixedSet<3> { public: using FixedSet<3>::FixedSet; };

class Root final : public NullSet {
    std::vector<NodeId> elements_;
public:
    explicit Root(std::string name) : NullSet(std::move(name)) {}
    std::vector<NodeId> elements() const override { return elements_; }
    void include(NodeId id) {
        if (std::find(elements_.begin(), elements_.end(), id) == elements_.end())
            elements_.push_back(id);
    }
};

enum class Relation { Supports, Attacks, LeadsTo, Models };
struct Edge { NodeId from, to; Relation relation; };

// Own nodes once; references to them are IDs rather than owning pointers.
class Memory {
    std::vector<std::unique_ptr<NullSet>> nodes_;
    std::vector<Edge> edges_;
public:
    template<class Node, class... Arguments>
    NodeId create(Arguments&&... arguments) {
        auto node = std::make_unique<Node>(std::forward<Arguments>(arguments)...);
        for (auto id : node->elements()) at(id);
        nodes_.push_back(std::move(node));
        return nodes_.size() - 1;
    }
    const NullSet& at(NodeId id) const { return *nodes_.at(id); }
    void include(NodeId root, NodeId child) {
        at(child);
        auto* container = dynamic_cast<Root*>(nodes_.at(root).get());
        if (!container) throw std::invalid_argument("Only Root has variable membership");
        container->include(child);
    }
    void relate(NodeId from, NodeId to, Relation relation) {
        at(from); at(to);
        if (!has_edge(from, to, relation)) edges_.push_back({from, to, relation});
    }
    bool has_edge(NodeId from, NodeId to, Relation relation) const {
        return std::any_of(edges_.begin(), edges_.end(), [&](const Edge& e) {
            return e.from == from && e.to == to && e.relation == relation;
        });
    }
    std::size_t reachable_count(NodeId start) const {
        std::set<NodeId> visited;
        std::vector<NodeId> pending{start};
        while (!pending.empty()) {
            const auto id = pending.back(); pending.pop_back();
            if (!visited.insert(id).second) continue;
            const auto children = at(id).elements();
            pending.insert(pending.end(), children.begin(), children.end());
        }
        return visited.size();
    }
};

// Order belongs to the route, not to the membership of a simplex or set.
class Route {
    std::vector<NodeId> steps_;
public:
    explicit Route(std::vector<NodeId> steps) : steps_(std::move(steps)) {
        if (steps_.empty()) throw std::invalid_argument("Route needs a starting node");
    }
    bool valid_in(const Memory& memory) const {
        for (auto id : steps_) memory.at(id);
        for (std::size_t i = 1; i < steps_.size(); ++i)
            if (!memory.has_edge(steps_[i - 1], steps_[i], Relation::LeadsTo)) return false;
        return true;
    }
    const std::vector<NodeId>& steps() const { return steps_; }
};

// Binary forecasts evaluated against observations, not inferred mental states.
class ForecastRecord {
    std::size_t count_ = 0;
    double squared_error_sum_ = 0.0;
public:
    void observe(double probability, bool occurred) {
        nonnegative(probability);
        if (probability > 1) throw std::invalid_argument("Probability exceeds one");
        const double error = probability - (occurred ? 1.0 : 0.0);
        squared_error_sum_ += error * error;
        ++count_;
    }
    std::size_t count() const { return count_; }
    std::optional<double> brier_score() const {
        if (!count_) return std::nullopt;
        return squared_error_sum_ / static_cast<double>(count_);
    }
};

struct OpponentModel {
    std::string subject;
    ForecastRecord move_forecasts;
};

struct SelfModel {
    ForecastRecord own_move_forecasts;
    // Measures the accuracy of one's estimates about one's opponent model.
    ForecastRecord opponent_model_forecasts;
};

class Brain {
    Memory memory_;
    SelfModel self_;
    std::map<std::string, OpponentModel> opponents_;
public:
    Memory& memory() { return memory_; }
    const Memory& memory() const { return memory_; }
    SelfModel& self_model() { return self_; }
    OpponentModel& model_of(const std::string& name) {
        return opponents_.try_emplace(name, OpponentModel{name, {}}).first->second;
    }
};

} // namespace virtual_cell::mind
