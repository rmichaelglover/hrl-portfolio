# One small step: an Eye can own a window

In the complete model, our Eye owns an Organ containing retinal cells. It also
owns an optical window and a reduced phototransduction state. Ownership is by
value, so no manual `delete` is needed.

```cpp
auto model = virtual_cell::vision::make_seeing_alex();
auto& body = model.alex.human().body();
```

`model` owns Alex and his Body. `body` is a temporary borrowed reference to that
same Body, not another owner.

```cpp
body.eye(0).window().set_open(false);
body.eye(1).window().set_open(true);
```

We have closed the left window and kept the right one open. Closing a window
changes what external light enters; it does not abolish internal retinal activity.

```cpp
virtual_cell::vision::Environment scene;
scene.add({"lamp", {0, 0, 1}, 1e-10, 500});
body.advance_in_environment(scene, 100);
```

The lamp is at (0,0,1) metres, emits isotropically at 1e-10 watts and has a
500 nm wavelength. The last call advances 100 milliseconds. These are explicit
model units, not defaults guessed from the word “lamp.”

A const accessor can inspect a result:

```cpp
const auto& right = body.eye(1);
const double voltage = right.cell(0, 0).membrane().voltage_mv();
```

Light decreases the rod-like cell's inward CNG current, making its voltage more
negative. Later cells in the retinal pathway can produce spikes. We can study
that sign change separately from constructing the Eye.

A different choice concerns a representation:

```cpp
model.alex.will().intend(1.0, virtual_cell::mind::Integration::Decline);
```

This sets an explicit integration policy. It does not close either window or
stop receptor chemistry.

Finally, an active concept can be retired:

```cpp
model.alex.retire_representation("light_activity");
```

Its definition remains available; a later permitted observation can create a
fresh active representation. Ending an instance and retaining a reusable
definition are distinct operations.
