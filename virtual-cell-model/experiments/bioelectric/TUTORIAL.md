# Small C++ lessons: ownership before electricity

These examples use the implementation in `include/bioelectric.hpp`,
`include/virtual_cell.hpp` and `include/bioelectric_body.hpp`.
Each step can be discussed on its own. Building the project need not mean
learning every part in one sitting.

## 1. Owning a value

```cpp
class Brain {
    Organ organ_{"Brain", OrganKind::Brain};
    // public methods follow in the complete class
};
```

A Brain contains an Organ value. There is no separately allocated Organ to
remember to delete. The members are constructed in declaration order and
destroyed in reverse order.

## 2. Optional ownership is still ownership

```cpp
std::optional<Brain> brain_;
std::vector<Organ> organs_;
electric::NervousSystem nervous_system_;
```

These are members of our Body. The optional wrapper starts empty in a partial
body; `add_brain()` constructs its owned Brain. A full example supplies the
Brain, Heart, Lungs, Skin and Mouth. The vector owns its organ values.
The NervousSystem owns its connections and event queue.

Each member manages its own resources. The Body needs no handwritten destructor:
this is the Rule of Zero. Constructing a valid object and immediately leaving
its scope is safe. Destruction of a C++ model is a lifetime operation; a separate
biological process would be needed to model cell death.

## 3. Build a complete example

```cpp
#include "bioelectric_body.hpp"

int main() {
    auto model = virtual_cell::electric::make_body_example("Alex");
}
```

The returned object owns a HomoSapiens, whose Body owns the components.
Its storage is released when `model` leaves scope. Return by value and ordinary
copy/move semantics work without a model-level owning pointer.

## 4. Borrow briefly to inspect

```cpp
const auto& brain = model.person.body().brain();
const auto count = brain.tissue(0).cell_count(); // 2
```

This reference borrows the existing Brain; it does not take ownership.
It must not outlive `model`. Avoiding owning pointers does not require avoiding
all references. We use references for temporary access, not persistent wiring.

## 5. A Cell may own an electrical aspect

```cpp
virtual_cell::Cell cell;
cell.attach_membrane(virtual_cell::electric::Membrane{});

const double voltage = cell.membrane().voltage_mv(); // -65
```

The existing Cell owns its molecular collection and optional Membrane.
Reading the voltage is const; advancing physical time changes the voltage.
No governor's permission is needed for a physical membrane current.

## 6. One membrane, one measured quantity

```cpp
virtual_cell::electric::Membrane membrane({100, 5, -65});
membrane.advance(20, 100);
```

The parameters are 100 pF capacitance, 5 nS leak, and -65 mV leak reversal.
The call applies a 100 pA inward current for 20 ms. The voltage approaches
-45 mV with a 20 ms time constant. The implementation uses the analytical RC
solution; the tests compare it to that independent formula.

## 7. Connections name cells without owning them

```cpp
auto& body = model.person.body();
const auto sensor = model.skin_sensor;

body.advance_electrical(10, {{sensor, 350}});
```

The Body resolves its local CellId into one owned cell. Connections do not hold
pointers into another object's storage. A copied model gets independent cells
and independent queued events, and its graph resolves within that copy.

## 8. Preserve what a result actually means

A threshold event is a reduced spike, not a full action-potential waveform.
A Heart-labelled membrane voltage is not a heartbeat. A higher-leak experiment
is a circuit perturbation, not a diagnosis. These distinctions tell us which
additional measurements and mechanisms should enter the next increment.
