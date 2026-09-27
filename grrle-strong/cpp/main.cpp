#include "grrle.hpp"
#include <iostream>

int main() {
    std::cout << "GRRLE Strong C++ Core — Demo\n";
    std::cout << "==============================\n";

    grrle::RelaxSuperTree tree(-2, 2, 5, 4, 42);
    std::cout << "Nodes: " << tree.nodes.size() << "\n";

    tree.relax(100, 0.10, 0.85);

    double mean_str = 0.0;
    for (size_t i = 0; i < tree.nodes.size(); ++i)
        mean_str += tree.strength(i);
    mean_str /= tree.nodes.size();
    std::cout << "Mean strength: " << mean_str << "\n";

    return 0;
}
