#pragma once

#include "virtual_cell.hpp"
#include <limits>

namespace virtual_cell::mind {

struct CompatibilityEdge {
    std::size_t object, label, neighbor, neighbor_label;
    double weight;
};

struct LabelField {
    std::vector<std::vector<double>> strengths;
    std::size_t iterations = 0;
    bool converged = false;
    double final_delta = 0;
};

// Independently implemented sparse, damped, prior-anchored compatibility field.
// Any finite number of labels; strengths are not calibrated probabilities.
class CompatibilityField {
    std::vector<std::vector<double>> prior_;
    std::vector<CompatibilityEdge> edges_;
public:
    explicit CompatibilityField(std::vector<std::vector<double>> prior)
        : prior_(std::move(prior)) {
        if (prior_.empty() || prior_[0].empty()) throw std::invalid_argument("Empty label field");
        const auto labels = prior_[0].size();
        for (auto& row : prior_) {
            if (row.size() != labels) throw std::invalid_argument("Ragged label field");
            double sum = 0;
            for (double value : row) sum = finite(sum + nonnegative(value));
            if (sum == 0) throw std::invalid_argument("Prior row needs positive mass");
            for (auto& value : row) value /= sum;
        }
    }
    void add(CompatibilityEdge edge) {
        if (edge.object >= prior_.size() || edge.neighbor >= prior_.size() ||
            edge.label >= prior_[0].size() || edge.neighbor_label >= prior_[0].size())
            throw std::out_of_range("Compatibility index");
        finite(edge.weight);
        edges_.push_back(edge);
    }
    LabelField run(std::size_t budget = 100, double damping = 0.5,
                   double coupling = 1.0, double tolerance = 1e-8) const {
        if (!budget || !std::isfinite(damping) || damping <= 0 || damping > 1)
            throw std::invalid_argument("Invalid iteration budget or damping");
        nonnegative(coupling); nonnegative(tolerance);
        LabelField result{prior_};
        for (std::size_t iteration = 0; iteration < budget; ++iteration) {
            auto support = prior_;
            for (auto& row : support) std::fill(row.begin(), row.end(), 0);
            for (const auto& edge : edges_) {
                auto& value = support[edge.object][edge.label];
                value = finite(value + edge.weight * result.strengths[edge.neighbor][edge.neighbor_label]);
            }
            auto next = result.strengths;
            double delta = 0;
            for (std::size_t i = 0; i < prior_.size(); ++i) {
                // Stable softmax(log(prior) + coupling * support).
                std::vector<double> logits(prior_[i].size());
                double maximum = -std::numeric_limits<double>::infinity();
                for (std::size_t a = 0; a < logits.size(); ++a) {
                    logits[a] = prior_[i][a] == 0 ? -std::numeric_limits<double>::infinity()
                        : finite(std::log(prior_[i][a]) + finite(coupling * support[i][a]));
                    maximum = std::max(maximum, logits[a]);
                }
                double sum = 0;
                for (auto& value : logits) { value = std::exp(value - maximum); sum += value; }
                for (std::size_t a = 0; a < logits.size(); ++a) {
                    next[i][a] += damping * (logits[a] / sum - next[i][a]);
                    delta = std::max(delta, std::abs(next[i][a] - result.strengths[i][a]));
                }
            }
            result.strengths = std::move(next);
            result.iterations = iteration + 1;
            result.final_delta = delta;
            if (delta <= tolerance) { result.converged = true; break; }
        }
        return result;
    }
};

} // namespace virtual_cell::mind
