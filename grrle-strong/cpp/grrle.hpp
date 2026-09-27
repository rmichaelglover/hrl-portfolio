#pragma once
/*
 * GRRLE / HyperObject — Strong C++ Core
 * Action-governed multi-scale recursive relaxation
 * Matching the Python reference architecture.
 */

#include <vector>
#include <unordered_map>
#include <cmath>
#include <random>
#include <algorithm>
#include <iostream>
#include <numeric>
#include <optional>
#include <string>

namespace grrle {

enum class Role { Object, Label };

struct Node {
    int uid = -1;
    int depth = 0;
    std::vector<double> tau;
    Role role = Role::Object;
    std::optional<int> parent_uid;
    std::vector<int> children_uids;
};

class CompatibilitySuperFn {
public:
    double agreement     = 1.15;
    double depth_scale   = 0.40;
    double confidence_mod = 0.30;
    double repulsion     = 0.12;

    double operator()(const Node& ni, int a, const Node& nj, int b,
                      const std::vector<Node>& all) const {
        double score = (a == b) ? agreement : -0.45 * agreement;

        double dd = std::abs(ni.depth - nj.depth);
        score += depth_scale * std::exp(-0.6 * dd);

        double conf = std::abs(ni.tau[a]) * std::abs(nj.tau[b]);
        score += confidence_mod * (2.0 * conf - 1.0);

        if (a == b) {
            int crowd = 0;
            for (const auto& n : all)
                if (n.uid != ni.uid && n.tau[a] > 0.6) ++crowd;
            score -= repulsion * std::log1p(static_cast<double>(crowd));
        }
        return score;
    }
};

class ActionFunctional {
public:
    CompatibilitySuperFn compat;
    double mass = 1.0;
    double w_cross = 0.60;
    double w_within = 1.0;

    std::vector<double> local_support(const Node& node, const std::vector<Node>& nodes) const {
        std::vector<double> Q(node.tau.size(), 0.0);
        for (const auto& other : nodes) {
            if (other.uid == node.uid) continue;
            for (size_t a = 0; a < node.tau.size(); ++a)
                for (size_t b = 0; b < other.tau.size(); ++b)
                    Q[a] += compat(node, static_cast<int>(a), other, static_cast<int>(b), nodes) * other.tau[b];
        }
        return Q;
    }

    std::vector<double> cross_scale_support(const Node& node, const std::vector<Node>& nodes,
                                            const std::unordered_map<int, size_t>& uid2idx) const {
        std::vector<double> Q(node.tau.size(), 0.0);

        if (node.parent_uid) {
            auto it = uid2idx.find(*node.parent_uid);
            if (it != uid2idx.end()) {
                const Node& parent = nodes[it->second];
                for (size_t a = 0; a < node.tau.size(); ++a)
                    for (size_t b = 0; b < parent.tau.size(); ++b)
                        Q[a] += 0.7 * compat(node, static_cast<int>(a), parent, static_cast<int>(b), nodes) * parent.tau[b];
            }
        }
        for (int cuid : node.children_uids) {
            auto it = uid2idx.find(cuid);
            if (it == uid2idx.end()) continue;
            const Node& child = nodes[it->second];
            for (size_t a = 0; a < node.tau.size(); ++a)
                for (size_t b = 0; b < child.tau.size(); ++b)
                    Q[a] += 0.5 * compat(node, static_cast<int>(a), child, static_cast<int>(b), nodes) * child.tau[b];
        }
        return Q;
    }

    std::vector<double> total_support(const Node& node, const std::vector<Node>& nodes,
                                      const std::unordered_map<int, size_t>& uid2idx) const {
        auto Lw = local_support(node, nodes);
        auto Lc = cross_scale_support(node, nodes, uid2idx);
        std::vector<double> Q(Lw.size());
        for (size_t i = 0; i < Q.size(); ++i)
            Q[i] = w_within * Lw[i] + w_cross * Lc[i];
        return Q;
    }

    double tree_support_scalar(const std::vector<Node>& nodes,
                               const std::unordered_map<int, size_t>& uid2idx) const {
        double total = 0.0;
        for (const auto& n : nodes) {
            auto Q = total_support(n, nodes, uid2idx);
            for (size_t i = 0; i < Q.size(); ++i)
                total += Q[i] * n.tau[i];
        }
        return total;
    }
};

class RelaxSuperTree {
public:
    std::vector<Node> nodes;
    std::unordered_map<int, size_t> uid2idx;
    ActionFunctional action;
    std::mt19937_64 rng;

    RelaxSuperTree(int d_min, int d_max, int n_labels = 5, int nodes_per_depth = 4, uint64_t seed = 42)
        : rng(seed)
    {
        action.compat = CompatibilitySuperFn{};
        int uid = 0;
        std::uniform_real_distribution<double> dist(-0.4, 0.4);

        std::unordered_map<int, std::vector<size_t>> depth_nodes;
        for (int d = d_min; d <= d_max; ++d) {
            for (int i = 0; i < nodes_per_depth; ++i) {
                Node n;
                n.uid = uid++;
                n.depth = d;
                n.tau.resize(n_labels);
                for (auto& v : n.tau) v = dist(rng);
                n.role = Role::Object;
                uid2idx[n.uid] = nodes.size();
                depth_nodes[d].push_back(nodes.size());
                nodes.push_back(std::move(n));
            }
        }

        // Wire hierarchy
        for (int d = d_min; d < d_max; ++d) {
            auto& children = depth_nodes[d];
            auto& parents  = depth_nodes[d + 1];
            for (size_t i = 0; i < children.size(); ++i) {
                size_t pidx = parents[i % parents.size()];
                nodes[children[i]].parent_uid = nodes[pidx].uid;
                nodes[pidx].children_uids.push_back(nodes[children[i]].uid);
                nodes[children[i]].role = Role::Label;
            }
        }
    }

    void rebuild_index() {
        uid2idx.clear();
        for (size_t i = 0; i < nodes.size(); ++i)
            uid2idx[nodes[i].uid] = i;
    }

    void relax(int steps = 100, double eta = 0.10, double momentum = 0.85, double tol = 1e-5) {
        std::vector<std::vector<double>> velocity(nodes.size());
        for (size_t i = 0; i < nodes.size(); ++i)
            velocity[i].assign(nodes[i].tau.size(), 0.0);

        for (int step = 0; step < steps; ++step) {
            std::vector<std::vector<double>> grads(nodes.size());
            for (size_t i = 0; i < nodes.size(); ++i)
                grads[i] = action.total_support(nodes[i], nodes, uid2idx);

            double max_change = 0.0;
            for (size_t i = 0; i < nodes.size(); ++i) {
                for (size_t k = 0; k < nodes[i].tau.size(); ++k) {
                    velocity[i][k] = momentum * velocity[i][k] + eta * grads[i][k];
                    double newv = nodes[i].tau[k] + velocity[i][k];
                    newv = std::clamp(newv, -1.0, 1.0);
                    max_change = std::max(max_change, std::abs(newv - nodes[i].tau[k]));
                    nodes[i].tau[k] = newv;
                }
            }
            if (step % 25 == 0 || step == steps - 1) {
                double S = action.tree_support_scalar(nodes, uid2idx);
                std::cout << "step " << step << " | support=" << S << " | Δ=" << max_change << "\n";
            }
            if (max_change < tol) {
                std::cout << "Converged at step " << step << "\n";
                break;
            }
        }
    }

    double strength(size_t idx, double eps = 3e-3, int trials = 5) {
        auto base = action.total_support(nodes[idx], nodes, uid2idx);
        std::vector<double> original = nodes[idx].tau;
        std::normal_distribution<double> noise(0.0, eps);
        double sum = 0.0;
        for (int t = 0; t < trials; ++t) {
            for (auto& v : nodes[idx].tau) v = original[&v - &nodes[idx].tau[0]] + noise(rng);
            for (auto& v : nodes[idx].tau) v = std::clamp(v, -1.0, 1.0);
            auto Q = action.total_support(nodes[idx], nodes, uid2idx);
            double diff = 0.0;
            for (size_t k = 0; k < Q.size(); ++k) diff += (Q[k] - base[k]) * (Q[k] - base[k]);
            sum += std::sqrt(diff);
        }
        nodes[idx].tau = original;
        return -sum / trials;
    }
};

} // namespace grrle
