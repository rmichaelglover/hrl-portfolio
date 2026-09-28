#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

#include <zlib.h>

namespace fs = std::filesystem;

// ============================================================
// CONSTANTS
// ============================================================

constexpr int ROWS   = 28;
constexpr int COLS   = 28;
constexpr int PIXELS = 784;
constexpr int DIGITS = 10;
constexpr int BLOCKS = 16;
constexpr int N_COMPONENTS = 5;

constexpr double EPS = 1e-12;

const std::string BASE_URL =
    "https://storage.googleapis.com/cvdf-datasets/mnist/";

const std::array<std::string, 4> MNIST_FILES = {
    "train-images-idx3-ubyte.gz",
    "train-labels-idx1-ubyte.gz",
    "t10k-images-idx3-ubyte.gz",
    "t10k-labels-idx1-ubyte.gz"
};

enum ComponentIndex {
    PROTOTYPE = 0,
    BLOCK_SHAPE,
    MASS,
    CENTER,
    PERSISTENCE
};

const std::array<std::string, N_COMPONENTS> COMPONENT_NAMES = {
    "prototype",
    "block_shape",
    "mass",
    "center",
    "persistence"
};

using Image = std::array<float, PIXELS>;
using State = std::array<double, DIGITS>;
using Components =
    std::array<std::array<double, DIGITS>, N_COMPONENTS>;


// ============================================================
// UTILITIES
// ============================================================

double clamp(double x, double lo = 0.0, double hi = 1.0)
{
    return std::max(lo, std::min(hi, x));
}

uint32_t read_be32(gzFile f)
{
    unsigned char b[4];

    if (gzread(f, b, 4) != 4)
        throw std::runtime_error("Unexpected EOF reading IDX header");

    return
        (uint32_t(b[0]) << 24) |
        (uint32_t(b[1]) << 16) |
        (uint32_t(b[2]) << 8)  |
        uint32_t(b[3]);
}


// ============================================================
// DOWNLOAD
// ============================================================

void download_if_missing(const fs::path& data_dir)
{
    fs::create_directories(data_dir);

    for (const auto& filename : MNIST_FILES)
    {
        fs::path path = data_dir / filename;

        if (fs::exists(path))
            continue;

        std::string url = BASE_URL + filename;

        std::cout << "Downloading " << url << "\n";

        std::string command =
            "curl -L --fail --silent --show-error "
            "-o \"" + path.string() + "\" "
            "\"" + url + "\"";

        int result = std::system(command.c_str());

        if (result != 0)
            throw std::runtime_error(
                "curl failed downloading " + filename
            );
    }
}


// ============================================================
// MNIST LOADING
// ============================================================

std::vector<Image> load_images(const fs::path& path)
{
    gzFile f = gzopen(path.string().c_str(), "rb");

    if (!f)
        throw std::runtime_error(
            "Cannot open " + path.string()
        );

    uint32_t magic = read_be32(f);
    uint32_t n     = read_be32(f);
    uint32_t rows  = read_be32(f);
    uint32_t cols  = read_be32(f);

    if (magic != 2051)
        throw std::runtime_error(
            "Bad MNIST image magic"
        );

    if (rows != ROWS || cols != COLS)
        throw std::runtime_error(
            "Expected 28x28 MNIST images"
        );

    std::vector<Image> images(n);

    std::array<unsigned char, PIXELS> buffer{};

    for (uint32_t i = 0; i < n; ++i)
    {
        int got = gzread(
            f,
            buffer.data(),
            PIXELS
        );

        if (got != PIXELS)
            throw std::runtime_error(
                "Unexpected EOF in MNIST images"
            );

        for (int p = 0; p < PIXELS; ++p)
            images[i][p] =
                static_cast<float>(buffer[p]) / 255.0f;
    }

    gzclose(f);

    return images;
}


std::vector<uint8_t> load_labels(const fs::path& path)
{
    gzFile f = gzopen(path.string().c_str(), "rb");

    if (!f)
        throw std::runtime_error(
            "Cannot open " + path.string()
        );

    uint32_t magic = read_be32(f);
    uint32_t n     = read_be32(f);

    if (magic != 2049)
        throw std::runtime_error(
            "Bad MNIST label magic"
        );

    std::vector<uint8_t> labels(n);

    if (gzread(f, labels.data(), n) != static_cast<int>(n))
        throw std::runtime_error(
            "Unexpected EOF in MNIST labels"
        );

    gzclose(f);

    return labels;
}


// ============================================================
// FEATURE EXTRACTION
// ============================================================

std::array<double, BLOCKS>
block_features(const Image& image)
{
    std::array<double, BLOCKS> out{};
    out.fill(0.0);

    // 28x28 -> 4x4
    // Each block is 7x7.

    for (int br = 0; br < 4; ++br)
    {
        for (int bc = 0; bc < 4; ++bc)
        {
            double sum = 0.0;

            for (int r = 0; r < 7; ++r)
            {
                for (int c = 0; c < 7; ++c)
                {
                    int y = br * 7 + r;
                    int x = bc * 7 + c;

                    sum += image[y * COLS + x];
                }
            }

            out[br * 4 + bc] = sum / 49.0;
        }
    }

    return out;
}


double image_mass(const Image& image)
{
    double s = 0.0;

    for (float v : image)
        s += v;

    return s / 784.0;
}


std::array<double, 2>
center_of_mass(const Image& image)
{
    double mass = 0.0;
    double sx = 0.0;
    double sy = 0.0;

    for (int y = 0; y < ROWS; ++y)
    {
        for (int x = 0; x < COLS; ++x)
        {
            double v = image[y * COLS + x];

            mass += v;
            sx += v * x;
            sy += v * y;
        }
    }

    mass += EPS;

    return {
        (sx / mass) / 27.0,
        (sy / mass) / 27.0
    };
}


// ============================================================
// OPERATOR
// ============================================================

struct Operator
{
    double prototype   = 0.40;
    double block_shape = 0.25;
    double mass        = 0.10;
    double center      = 0.10;
    double persistence = 0.15;

    double exploration = 0.00;

    std::array<double, N_COMPONENTS>
    normalized() const
    {
        std::array<double, N_COMPONENTS> w = {
            std::max(prototype,   1e-6),
            std::max(block_shape, 1e-6),
            std::max(mass,        1e-6),
            std::max(center,      1e-6),
            std::max(persistence, 1e-6)
        };

        double sum =
            std::accumulate(
                w.begin(),
                w.end(),
                0.0
            );

        for (double& x : w)
            x /= sum;

        return w;
    }

    void assign(
        const std::array<double, N_COMPONENTS>& w
    )
    {
        prototype   = w[PROTOTYPE];
        block_shape = w[BLOCK_SHAPE];
        mass        = w[MASS];
        center      = w[CENTER];
        persistence = w[PERSISTENCE];
    }
};


// ============================================================
// CLASSIFICATION RESULT
// ============================================================

struct Classification
{
    int pred = 0;
    Components components{};
    State state{};
};


// ============================================================
// RELAX MNIST
// ============================================================

class RelaxMNIST
{
public:

    RelaxMNIST(
        double state_lr_    = 0.45,
        double goal_lr_     = 0.08,
        double operator_lr_ = 0.02,
        int iterations_     = 4,
        uint64_t seed       = 7
    )
        :
        state_lr(state_lr_),
        goal_lr(goal_lr_),
        operator_lr(operator_lr_),
        iterations(iterations_),
        rng(seed)
    {
        state.fill(0.1);

        long_accuracy   = 1.0;
        medium_shape    = 0.8;
        medium_geometry = 0.7;
        short_current   = 1.0;

        for (auto& p : prototypes)
            p.fill(0.0);

        for (auto& p : block_prototypes)
            p.fill(0.0);

        mass_prototypes.fill(0.0);

        for (auto& p : center_prototypes)
            p.fill(0.0);
    }


    // ========================================================
    // PROTOTYPE FITTING
    // ========================================================

    void fit_prototypes(
        const std::vector<Image>& images,
        const std::vector<uint8_t>& labels,
        const std::vector<size_t>& indices
    )
    {
        std::array<size_t, DIGITS> counts{};
        counts.fill(0);

        for (size_t idx : indices)
        {
            int digit = labels[idx];

            counts[digit]++;

            const Image& image = images[idx];

            auto blocks = block_features(image);
            double mass = image_mass(image);
            auto center = center_of_mass(image);

            for (int p = 0; p < PIXELS; ++p)
                prototypes[digit][p] += image[p];

            for (int b = 0; b < BLOCKS; ++b)
                block_prototypes[digit][b] += blocks[b];

            mass_prototypes[digit] += mass;

            center_prototypes[digit][0] += center[0];
            center_prototypes[digit][1] += center[1];
        }

        for (int d = 0; d < DIGITS; ++d)
        {
            if (counts[d] == 0)
                throw std::runtime_error(
                    "No prototype samples for digit " +
                    std::to_string(d)
                );

            double n =
                static_cast<double>(counts[d]);

            for (double& v : prototypes[d])
                v /= n;

            for (double& v : block_prototypes[d])
                v /= n;

            mass_prototypes[d] /= n;

            center_prototypes[d][0] /= n;
            center_prototypes[d][1] /= n;
        }

        // Cache norms.
        for (int d = 0; d < DIGITS; ++d)
        {
            prototype_norm[d] =
                vector_norm(prototypes[d]);

            block_norm[d] =
                vector_norm(block_prototypes[d]);
        }

        // Same mass scale idea as NumPy std().
        double mean =
            std::accumulate(
                mass_prototypes.begin(),
                mass_prototypes.end(),
                0.0
            ) / DIGITS;

        double variance = 0.0;

        for (double v : mass_prototypes)
        {
            double dv = v - mean;
            variance += dv * dv;
        }

        variance /= DIGITS;

        mass_scale =
            std::sqrt(variance) + 1e-3;
    }


    // ========================================================
    // SUPPORT COMPONENTS
    // ========================================================

    Components support_components(
        const Image& image
    )
    {
        Components c{};

        auto block = block_features(image);
        double mass = image_mass(image);
        auto center = center_of_mass(image);

        double xnorm = image_norm(image);
        double bnorm = vector_norm(block);

        for (int d = 0; d < DIGITS; ++d)
        {
            // ------------------------------------------------
            // prototype cosine
            // ------------------------------------------------

            double proto_dot = 0.0;

            for (int p = 0; p < PIXELS; ++p)
                proto_dot +=
                    prototypes[d][p] *
                    image[p];

            double proto_sim =
                proto_dot /
                (
                    prototype_norm[d] *
                    xnorm + EPS
                );

            // ------------------------------------------------
            // block-shape cosine
            // ------------------------------------------------

            double block_dot = 0.0;

            for (int b = 0; b < BLOCKS; ++b)
                block_dot +=
                    block_prototypes[d][b] *
                    block[b];

            double block_sim =
                block_dot /
                (
                    block_norm[d] *
                    bnorm + EPS
                );

            // ------------------------------------------------
            // mass similarity
            // ------------------------------------------------

            double mass_sim =
                std::exp(
                    -std::abs(
                        mass_prototypes[d] -
                        mass
                    ) / mass_scale
                );

            // ------------------------------------------------
            // center similarity
            // ------------------------------------------------

            double dx =
                center_prototypes[d][0] -
                center[0];

            double dy =
                center_prototypes[d][1] -
                center[1];

            double center_dist =
                std::sqrt(dx * dx + dy * dy);

            double center_sim =
                std::exp(
                    -center_dist / 0.15
                );

            c[PROTOTYPE][d] =
                clamp(proto_sim);

            c[BLOCK_SHAPE][d] =
                clamp(block_sim);

            c[MASS][d] =
                clamp(mass_sim);

            c[CENTER][d] =
                clamp(center_sim);

            c[PERSISTENCE][d] =
                clamp(state[d]);
        }

        return c;
    }


    // ========================================================
    // COMBINED SUPPORT
    // ========================================================

    State combined_support(
        const Components& c
    )
    {
        auto w = op.normalized();

        State support{};

        for (int d = 0; d < DIGITS; ++d)
        {
            support[d] =
                w[PROTOTYPE] *
                    c[PROTOTYPE][d] *
                    medium_shape

                +

                w[BLOCK_SHAPE] *
                    c[BLOCK_SHAPE][d] *
                    medium_shape

                +

                w[MASS] *
                    c[MASS][d] *
                    medium_geometry

                +

                w[CENTER] *
                    c[CENTER][d] *
                    medium_geometry

                +

                w[PERSISTENCE] *
                    c[PERSISTENCE][d] *
                    short_current;
        }

        if (op.exploration > 0.0)
        {
            std::normal_distribution<double>
                noise(0.0, op.exploration);

            for (double& v : support)
                v += noise(rng);
        }

        return support;
    }


    // ========================================================
    // STATE RELAXATION
    // ========================================================

    void relax_state(const State& support)
    {
        double minv =
            *std::min_element(
                support.begin(),
                support.end()
            );

        State target{};

        double sum = 0.0;

        for (int d = 0; d < DIGITS; ++d)
        {
            target[d] =
                support[d] - minv;

            sum += target[d];
        }

        if (sum < EPS)
        {
            target.fill(0.1);
        }
        else
        {
            for (double& v : target)
                v /= sum;
        }

        double state_sum = 0.0;

        for (int d = 0; d < DIGITS; ++d)
        {
            state[d] =
                (1.0 - state_lr) *
                    state[d]

                +

                state_lr *
                    target[d];

            state[d] =
                std::max(0.0, state[d]);

            state_sum += state[d];
        }

        state_sum += EPS;

        for (double& v : state)
            v /= state_sum;
    }


    // ========================================================
    // CLASSIFICATION
    // ========================================================

    Classification classify(
        const Image& image,
        bool reset_state = true
    )
    {
        if (reset_state)
            state.fill(0.1);

        Components components{};

        for (int i = 0; i < iterations; ++i)
        {
            components =
                support_components(image);

            State support =
                combined_support(components);

            relax_state(support);
        }

        int pred =
            static_cast<int>(
                std::distance(
                    state.begin(),
                    std::max_element(
                        state.begin(),
                        state.end()
                    )
                )
            );

        return {
            pred,
            components,
            state
        };
    }


    // ========================================================
    // GOAL RELAXATION
    // ========================================================

    void relax_goals(bool correct)
    {
        double reward =
            correct ? 1.0 : 0.0;

        short_current +=
            goal_lr *
            (
                reward -
                short_current
            );

        double medium_lr =
            goal_lr * 0.4;

        medium_shape +=
            medium_lr *
            (
                reward -
                medium_shape
            );

        medium_geometry +=
            medium_lr *
            (
                reward -
                medium_geometry
            );

        double long_lr =
            goal_lr * 0.1;

        long_accuracy +=
            long_lr *
            (
                reward -
                long_accuracy
            );
    }


    // ========================================================
    // OPERATOR RELAXATION
    // ========================================================

    void relax_operator(
        const Components& components,
        int pred,
        int truth
    )
    {
        auto current =
            op.normalized();

        auto updated =
            current;

        for (
            int component = 0;
            component < N_COMPONENTS;
            ++component
        )
        {
            double truth_support =
                components[component][truth];

            double competitor =
                -1e100;

            for (int d = 0; d < DIGITS; ++d)
            {
                if (d == truth)
                    continue;

                competitor =
                    std::max(
                        competitor,
                        components[component][d]
                    );
            }

            double margin =
                clamp(
                    truth_support -
                    competitor,
                    -1.0,
                    1.0
                );

            updated[component] =
                std::max(
                    1e-5,
                    current[component]
                    +
                    operator_lr *
                    margin
                );
        }

        double total =
            std::accumulate(
                updated.begin(),
                updated.end(),
                0.0
            );

        for (double& v : updated)
            v /= total;

        op.assign(updated);

        if (pred != truth)
        {
            op.exploration =
                std::min(
                    0.08,
                    op.exploration +
                    operator_lr * 0.02
                );
        }
        else
        {
            op.exploration =
                std::max(
                    0.0,
                    op.exploration -
                    operator_lr * 0.005
                );
        }
    }


    // ========================================================
    // CALIBRATION
    // ========================================================

    double calibrate(
        const std::vector<Image>& images,
        const std::vector<uint8_t>& labels,
        const std::vector<size_t>& calibration_indices,
        int epochs,
        int report_every = 1000,
        bool shuffle = true
    )
    {
        double final_accuracy = 0.0;

        std::vector<size_t> order =
            calibration_indices;

        for (
            int epoch = 1;
            epoch <= epochs;
            ++epoch
        )
        {
            if (shuffle)
                std::shuffle(
                    order.begin(),
                    order.end(),
                    rng
                );

            size_t correct = 0;

            std::cout
                << "\n--- calibration epoch "
                << epoch
                << "/"
                << epochs
                << " ---\n";

            for (
                size_t step = 0;
                step < order.size();
                ++step
            )
            {
                size_t idx =
                    order[step];

                int truth =
                    labels[idx];

                Classification result =
                    classify(
                        images[idx],
                        true
                    );

                bool is_correct =
                    result.pred == truth;

                if (is_correct)
                    ++correct;

                relax_goals(is_correct);

                relax_operator(
                    result.components,
                    result.pred,
                    truth
                );

                if (
                    report_every > 0 &&
                    (step + 1) %
                        static_cast<size_t>(
                            report_every
                        )
                    == 0
                )
                {
                    double running_accuracy =
                        static_cast<double>(
                            correct
                        ) /
                        static_cast<double>(
                            step + 1
                        );

                    std::cout
                        << "epoch "
                        << std::setw(2)
                        << epoch
                        << " sample "
                        << std::setw(6)
                        << step + 1
                        << ": accuracy="
                        << std::fixed
                        << std::setprecision(4)
                        << running_accuracy
                        << " operator=";

                    print_operator_inline();
                }
            }

            final_accuracy =
                static_cast<double>(
                    correct
                ) /
                static_cast<double>(
                    order.size()
                );

            std::cout
                << "epoch "
                << epoch
                << " complete: accuracy="
                << std::fixed
                << std::setprecision(4)
                << final_accuracy * 100.0
                << "%\n";

            print_operator();
        }

        return final_accuracy;
    }


    // ========================================================
    // EVALUATE
    // ========================================================

    double evaluate(
        const std::vector<Image>& images,
        const std::vector<uint8_t>& labels,
        size_t limit,
        std::array<
            std::array<uint64_t, DIGITS>,
            DIGITS
        >& confusion,
        bool deterministic = true
    )
    {
        for (auto& row : confusion)
            row.fill(0);

        double old_exploration =
            op.exploration;

        if (deterministic)
            op.exploration = 0.0;

        size_t correct = 0;

        limit =
            std::min(
                limit,
                images.size()
            );

        for (size_t i = 0; i < limit; ++i)
        {
            int truth =
                labels[i];

            int pred =
                classify(
                    images[i],
                    true
                ).pred;

            if (pred == truth)
                ++correct;

            confusion[truth][pred]++;
        }

        if (deterministic)
            op.exploration =
                old_exploration;

        return
            static_cast<double>(correct) /
            static_cast<double>(limit);
    }


    // ========================================================
    // BASELINE
    // ========================================================

    double prototype_baseline(
        const std::vector<Image>& images,
        const std::vector<uint8_t>& labels,
        size_t limit
    ) const
    {
        limit =
            std::min(
                limit,
                images.size()
            );

        size_t correct = 0;

        for (size_t i = 0; i < limit; ++i)
        {
            const auto& image =
                images[i];

            double xnorm =
                image_norm(image);

            int best_digit = 0;
            double best_score = -1e100;

            for (int d = 0; d < DIGITS; ++d)
            {
                double dot = 0.0;

                for (int p = 0; p < PIXELS; ++p)
                    dot +=
                        prototypes[d][p] *
                        image[p];

                double score =
                    dot /
                    (
                        prototype_norm[d] *
                        xnorm + EPS
                    );

                if (score > best_score)
                {
                    best_score =
                        score;

                    best_digit =
                        d;
                }
            }

            if (
                best_digit ==
                labels[i]
            )
                ++correct;
        }

        return
            static_cast<double>(correct) /
            static_cast<double>(limit);
    }


    // ========================================================
    // REPORTING
    // ========================================================

    void print_operator_inline() const
    {
        auto w =
            op.normalized();

        std::cout << "{ ";

        for (
            int i = 0;
            i < N_COMPONENTS;
            ++i
        )
        {
            std::cout
                << COMPONENT_NAMES[i]
                << "="
                << std::setprecision(4)
                << w[i];

            if (i + 1 < N_COMPONENTS)
                std::cout << ", ";
        }

        std::cout << " }\n";
    }


    void print_operator() const
    {
        auto w =
            op.normalized();

        std::cout
            << "operator:\n";

        for (
            int i = 0;
            i < N_COMPONENTS;
            ++i
        )
        {
            std::cout
                << "  "
                << std::setw(14)
                << std::left
                << COMPONENT_NAMES[i]
                << ": "
                << std::fixed
                << std::setprecision(6)
                << w[i]
                << "\n";
        }

        std::cout
            << "  "
            << std::setw(14)
            << std::left
            << "exploration"
            << ": "
            << op.exploration
            << "\n";
    }


    void print_goals() const
    {
        std::cout
            << "\nGoal strengths:\n";

        std::cout
            << "  long_accuracy   : "
            << long_accuracy
            << "\n";

        std::cout
            << "  medium_shape    : "
            << medium_shape
            << "\n";

        std::cout
            << "  medium_geometry : "
            << medium_geometry
            << "\n";

        std::cout
            << "  short_current   : "
            << short_current
            << "\n";
    }


    void print_sample_guts(
        const Image& image,
        int truth
    )
    {
        Classification result =
            classify(image, true);

        static const std::string chars =
            " .:-=+*#%@";

        std::cout
            << "\n============================================================\n"
            << "SAMPLE GUTS truth="
            << truth
            << " prediction="
            << result.pred
            << "\n"
            << "============================================================\n";

        std::cout
            << "\nInput digit:\n";

        for (int y = 0; y < ROWS; ++y)
        {
            std::cout << "  ";

            for (int x = 0; x < COLS; ++x)
            {
                double v =
                    image[y * COLS + x];

                int idx =
                    static_cast<int>(
                        std::round(
                            clamp(v) *
                            (chars.size() - 1)
                        )
                    );

                std::cout << chars[idx];
            }

            std::cout << "\n";
        }

        std::vector<int> order(DIGITS);

        std::iota(
            order.begin(),
            order.end(),
            0
        );

        std::sort(
            order.begin(),
            order.end(),
            [&](int a, int b)
            {
                return
                    result.state[a] >
                    result.state[b];
            }
        );

        std::cout
            << "\nFinal label-assignment strengths:\n";

        for (int d : order)
        {
            std::cout
                << "  "
                << d
                << ": "
                << std::fixed
                << std::setprecision(6)
                << result.state[d]
                << "\n";
        }

        std::cout
            << "\nSupport-component winners:\n";

        for (
            int c = 0;
            c < N_COMPONENTS;
            ++c
        )
        {
            std::vector<int> digit_order(DIGITS);

            std::iota(
                digit_order.begin(),
                digit_order.end(),
                0
            );

            std::sort(
                digit_order.begin(),
                digit_order.end(),
                [&](int a, int b)
                {
                    return
                        result.components[c][a] >
                        result.components[c][b];
                }
            );

            std::cout
                << "  "
                << std::setw(14)
                << std::left
                << COMPONENT_NAMES[c]
                << ": ";

            for (int k = 0; k < 3; ++k)
            {
                int d =
                    digit_order[k];

                std::cout
                    << d
                    << "="
                    << std::fixed
                    << std::setprecision(3)
                    << result.components[c][d]
                    << "  ";
            }

            std::cout << "\n";
        }
    }


    const Operator& get_operator() const
    {
        return op;
    }


private:

    double state_lr;
    double goal_lr;
    double operator_lr;

    int iterations;

    std::mt19937_64 rng;

    State state{};

    double long_accuracy;
    double medium_shape;
    double medium_geometry;
    double short_current;

    Operator op;

    std::array<
        std::array<double, PIXELS>,
        DIGITS
    > prototypes{};

    std::array<
        std::array<double, BLOCKS>,
        DIGITS
    > block_prototypes{};

    std::array<double, DIGITS>
        mass_prototypes{};

    std::array<
        std::array<double, 2>,
        DIGITS
    > center_prototypes{};

    std::array<double, DIGITS>
        prototype_norm{};

    std::array<double, DIGITS>
        block_norm{};

    double mass_scale = 1.0;


    static double image_norm(
        const Image& image
    )
    {
        double s = 0.0;

        for (float v : image)
            s += double(v) * double(v);

        return std::sqrt(s) + EPS;
    }


    template <size_t N>
    static double vector_norm(
        const std::array<double, N>& v
    )
    {
        double s = 0.0;

        for (double x : v)
            s += x * x;

        return std::sqrt(s) + EPS;
    }
};


// ============================================================
// CONFUSION REPORT
// ============================================================

void print_confusion(
    const std::array<
        std::array<uint64_t, DIGITS>,
        DIGITS
    >& confusion
)
{
    std::cout
        << "\nConfusion matrix: rows=true, columns=predicted\n\n"
        << "     ";

    for (int d = 0; d < DIGITS; ++d)
        std::cout
            << std::setw(6)
            << d;

    std::cout << "\n";

    for (int truth = 0; truth < DIGITS; ++truth)
    {
        std::cout
            << "  "
            << truth
            << " |";

        for (int pred = 0; pred < DIGITS; ++pred)
        {
            std::cout
                << std::setw(6)
                << confusion[truth][pred];
        }

        std::cout << "\n";
    }

    std::cout
        << "\nPer-digit recall:\n";

    for (int truth = 0; truth < DIGITS; ++truth)
    {
        uint64_t total = 0;

        for (int pred = 0; pred < DIGITS; ++pred)
            total += confusion[truth][pred];

        double recall =
            total
            ?
            double(
                confusion[truth][truth]
            ) / double(total)
            :
            0.0;

        std::cout
            << "  "
            << truth
            << ": "
            << std::fixed
            << std::setprecision(2)
            << recall * 100.0
            << "%\n";
    }
}


// ============================================================
// COMMAND LINE OPTIONS
// ============================================================

struct Options
{
    std::string data_dir =
        "./mnist_data";

    size_t prototype_count =
        10000;

    size_t calibrate_count =
        5000;

    size_t test_limit =
        10000;

    int iterations =
        4;

    double state_lr =
        0.45;

    double goal_lr =
        0.08;

    double operator_lr =
        0.02;

    uint64_t seed =
        7;

    int epochs =
        5;

    int report_every =
        1000;

    int guts_samples =
        3;

    bool stochastic_test =
        false;
};


Options parse_args(
    int argc,
    char** argv
)
{
    Options o;

    for (int i = 1; i < argc; ++i)
    {
        std::string a =
            argv[i];

        auto need_value =
            [&](const std::string& name)
            {
                if (i + 1 >= argc)
                    throw std::runtime_error(
                        "Missing value for " +
                        name
                    );

                return std::string(
                    argv[++i]
                );
            };

        if (a == "--data-dir")
            o.data_dir =
                need_value(a);

        else if (a == "--prototype-count")
            o.prototype_count =
                std::stoull(
                    need_value(a)
                );

        else if (a == "--calibrate-count")
            o.calibrate_count =
                std::stoull(
                    need_value(a)
                );

        else if (a == "--test-limit")
            o.test_limit =
                std::stoull(
                    need_value(a)
                );

        else if (a == "--iterations")
            o.iterations =
                std::stoi(
                    need_value(a)
                );

        else if (a == "--state-lr")
            o.state_lr =
                std::stod(
                    need_value(a)
                );

        else if (a == "--goal-lr")
            o.goal_lr =
                std::stod(
                    need_value(a)
                );

        else if (a == "--operator-lr")
            o.operator_lr =
                std::stod(
                    need_value(a)
                );

        else if (a == "--seed")
            o.seed =
                std::stoull(
                    need_value(a)
                );

        else if (a == "--epochs")
            o.epochs =
                std::stoi(
                    need_value(a)
                );

        else if (a == "--report-every")
            o.report_every =
                std::stoi(
                    need_value(a)
                );

        else if (a == "--guts-samples")
            o.guts_samples =
                std::stoi(
                    need_value(a)
                );

        else if (a == "--stochastic-test")
            o.stochastic_test =
                true;

        else
            throw std::runtime_error(
                "Unknown argument: " + a
            );
    }

    return o;
}


// ============================================================
// MAIN
// ============================================================

int main(
    int argc,
    char** argv
)
{
    try
    {
        Options args =
            parse_args(
                argc,
                argv
            );

        fs::path data_dir =
            args.data_dir;

        download_if_missing(
            data_dir
        );

        std::cout
            << "\nLoading MNIST...\n";

        auto train_images =
            load_images(
                data_dir /
                MNIST_FILES[0]
            );

        auto train_labels =
            load_labels(
                data_dir /
                MNIST_FILES[1]
            );

        auto test_images =
            load_images(
                data_dir /
                MNIST_FILES[2]
            );

        auto test_labels =
            load_labels(
                data_dir /
                MNIST_FILES[3]
            );

        // ----------------------------------------------------
        // Random train partition:
        //
        // prototype set followed by calibration set.
        // ----------------------------------------------------

        std::mt19937_64 rng(
            args.seed
        );

        std::vector<size_t> idx(
            train_images.size()
        );

        std::iota(
            idx.begin(),
            idx.end(),
            0
        );

        std::shuffle(
            idx.begin(),
            idx.end(),
            rng
        );

        size_t prototype_count =
            std::min(
                args.prototype_count,
                idx.size()
            );

        size_t remaining =
            idx.size() -
            prototype_count;

        size_t calibrate_count =
            std::min(
                args.calibrate_count,
                remaining
            );

        std::vector<size_t> proto_idx(
            idx.begin(),
            idx.begin() +
            prototype_count
        );

        std::vector<size_t> cal_idx(
            idx.begin() +
            prototype_count,
            idx.begin() +
            prototype_count +
            calibrate_count
        );

        size_t test_n =
            std::min(
                args.test_limit,
                test_images.size()
            );

        RelaxMNIST engine(
            args.state_lr,
            args.goal_lr,
            args.operator_lr,
            args.iterations,
            args.seed
        );

        std::cout
            << "\nBuilding digit prototypes...\n";

        engine.fit_prototypes(
            train_images,
            train_labels,
            proto_idx
        );

        std::cout
            << "\nBaseline: mean-image prototype cosine classifier\n";

        double baseline =
            engine.prototype_baseline(
                test_images,
                test_labels,
                test_n
            );

        std::cout
            << "baseline test accuracy: "
            << std::fixed
            << std::setprecision(4)
            << baseline * 100.0
            << "%\n";

        if (!cal_idx.empty())
        {
            std::cout
                << "\nRELAX calibration...\n";

            double cal_acc =
                engine.calibrate(
                    train_images,
                    train_labels,
                    cal_idx,
                    args.epochs,
                    args.report_every,
                    true
                );

            std::cout
                << "\ncalibration accuracy: "
                << std::fixed
                << std::setprecision(4)
                << cal_acc * 100.0
                << "%\n";
        }

        std::cout
            << "\nLearned operator weights:\n";

        engine.print_operator();

        engine.print_goals();

        std::array<
            std::array<uint64_t, DIGITS>,
            DIGITS
        > confusion{};

        std::cout
            << "\nFrozen RELAX test...\n";

        double test_acc =
            engine.evaluate(
                test_images,
                test_labels,
                test_n,
                confusion,
                !args.stochastic_test
            );

        std::cout
            << "\nRELAX test accuracy:    "
            << std::fixed
            << std::setprecision(4)
            << test_acc * 100.0
            << "%\n";

        std::cout
            << "baseline test accuracy: "
            << baseline * 100.0
            << "%\n";

        std::cout
            << "difference:             "
            << std::showpos
            << (test_acc - baseline) * 100.0
            << "%"
            << std::noshowpos
            << "\n";

        std::cout
            << "evaluation mode:        "
            << (
                args.stochastic_test
                ?
                "stochastic"
                :
                "deterministic"
            )
            << "\n";

        print_confusion(
            confusion
        );

        // ----------------------------------------------------
        // Detailed sample guts.
        // ----------------------------------------------------

        int n_guts =
            std::min<int>(
                args.guts_samples,
                test_n
            );

        for (
            int i = 0;
            i < n_guts;
            ++i
        )
        {
            engine.print_sample_guts(
                test_images[i],
                test_labels[i]
            );
        }

        return 0;
    }

    catch (
        const std::exception& e
    )
    {
        std::cerr
            << "\nERROR: "
            << e.what()
            << "\n";

        return 1;
    }
}
