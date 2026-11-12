# Observe Alex without owning Alex

```cpp
study::PassiveTracker tracker;
tracker.observe(study::PoseSample{
    "synthetic-room-1", "room", 1.0, 2.0, 1.0, 0.0, .01
});
```

The tracker owns an observation: session, frame, source time, position, and a
variance. It does not own or borrow Alex. It cannot change Alex's Body or Will.
An external tracker and Alex's subjective self-location are different objects.

```cpp
std::optional<PoseSample> pose;
```

An empty optional means no pose measurement. It does not mean Alex is located
at the origin. Similarly, a stale observation does not become current by being
remembered.

The sleep observation is another value:

```cpp
study::SleepEpoch epoch{
    "sleep-recording", 0, 30, study::SleepStage::REM, 12, 15
};
epoch.validate();
```

These sample numbers illustrate the type; they are not measured patient data.
A scored REM label is not an eyeball angle. EOG microvolts need their own
calibration before they can imply physical eye rotation.

Alex owns a separate reflective practice:

```cpp
alex.reflection().say(mind::flowers_mantra());
alex.reflection().count(mind::ReflectiveReward::Happiness); // 1
```

This increments a named reward in the model. It does not edit an observed EOG
sample or establish a biological health effect.

Run `./build/observation_demo` for a complete small example.
