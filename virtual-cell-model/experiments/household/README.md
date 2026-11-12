# Alex at home: situated activity and subjective mapping

Originating scenario, framework, and direction: **Michael Emanuel Glover**.
Assistant contribution: C++ implementation, explicit assumptions, and verification.

Alex wants to listen to *Yesterday* by The Beatles, improve singing and lyric
recall, maintain an already practiced guitar part, enjoy food, relate to Papa
and Mama, and make progress toward autonomy and financial independence.
The model keeps these desires simultaneous rather than treating one as his
complete objective.

## Run and read

```sh
cmake -S . -B build
cmake --build build -j 2
ctest --test-dir build --output-on-failure
./build/household_demo
```

See [example output](example-output.txt), [C++ model](../../include/household.hpp),
[scenario](../../src/household_demo.cpp), and [tests](../../tests/household_tests.cpp).
All new components own their state by value; there are no new owning pointers,
manual allocations, or destructor requirements.

## World, experience, and memory

The existing Body still owns both Eyes and their retinal cells. Moving the
observer changes both optical frames with their 64-mm separation retained.
An idealized room-light emitter feeds the existing photon/transduction pipeline;
retinal counts feed the existing `PersonModel::boundary_evidence()` interface.
This is not a new visual system replacing the old one.

Our current scalar rod pathways do not infer object identity, stereo disparity,
or image features. The semantic frontend is therefore an explicit fixture
supplying identified range/bearing measurements for guitar, computer, Papa,
visible food, and refrigerator. That fixture is distinct from retinal evidence;
no object-recognition performance is inferred from light responses.

The remembered Singaporean noodles are stored at the remembered refrigerator
location with uncertain coordinates and an episodic source. Remembering them
is not seeing through the closed refrigerator. Mama has no current visual
observation; the map makes no inference that she does not exist or has left home.
Visible food is a separate observation from the remembered leftovers.

`SubjectiveMap` contains estimated position, yaw, an accumulating pose-variance
proxy, and landmark records with variance, source, and last-seen time. Forward
odometry and turning transform egocentric observations into an estimated map:

```
x_landmark = x_self + range * sin(yaw_self + bearing)
z_landmark = z_self + range * cos(yaw_self + bearing)
```

Repeated observations conservatively replace a landmark estimate instead of
pretending correlated pose errors are independent measurements. Landmarks do
not magically remain visible after moving; observations expire by age.
The shortest grid route uses only explicitly known free cells. Unknown cells
are not silently traversable. The example plans a three-step refrigerator route
and demonstrates a one-meter motion with the corresponding optical-frame change.
Actual and estimated motion coincide in this initial ideal-odometry example;
the stored variance expresses estimated uncertainty, not sampled physical error.

This is a first subjective localization-and-mapping scaffold: it does not yet
solve joint pose/landmark inference, loop closure, occlusion, collision-aware
execution, semantic tracking, or stereo geometry. Those can be added behind the
observation and movement interfaces without changing Person ownership.

## Parents have their own objectives

`HouseholdPerson` owns preferences for conversation, quiet, music, meals, sweets,
and drinks, plus an occupied state. Meal appetite is low after breakfast and
late lunch while a cinnamon roll or drink can remain appealing. Preferences
are scenario values, not estimates of Michael's actual parents.

`OtherModel` is what Alex knows: visibility and optional replies. Unknown is
represented by an empty `std::optional<bool>`, distinct from refusal. Alex may
invite or contact someone without presuming availability. In this first policy,
audible practice requires affirmative household agreement; headphone listening
and quiet recall remain available. Papa's willingness to converse does not imply
permission for audible music. Mama's absence from view does not imply that she
will want a call or that her quiet preference is irrelevant. The example leaves
her availability unknown and offers an availability inquiry.

The scenario obtains Papa's explicit replies. It does not inspect Mama's private
preferences when making Alex's choices. This is the self/other-model distinction
made operational.

## Several kinds of value

Activities retain the existing five goal proxies: health, security,
relationships, learning, and resources. Additional reported dimensions are joy,
peace, stimulation, and autonomy. `HouseholdGovernor` combines these only under
explicit supplied weights; these weights are inspectable scenario policy.
Financial preparation is a prospective resource score, not actual income.
Self-actualization is represented provisionally by learning and autonomy, not
collapsed into money. Future income and long-horizon scheduling are not simulated.

Hunger affects the eating health proxy, pleasure affects the joy proxy, and effort
affects action cost and enjoyment. Thus satiation does not erase appetitive desire.
There is no claim that tastier food is inherently healthier. Need values can be
varied to probe uncertainty about hunger; this version does not diagnose hunger
from a physiological sensor.

The scenario prints all options, their permissions, and their component scores.
Two policies illustrate how prioritizing relationships can change the selected
activity. Selection is a decision point, not automatic execution of a meal,
conversation, employment task, or audio playback. Speech replies are explicit
inputs, not outputs of an auditory-language recognizer.

## Music, concentration, and relaxation

`MusicPractice` names the song and artist and stores independent proficiency
variables: guitar starts at .85, voice at .3, and lyric recall at .1. No recording
or lyric text is embedded. The lyric-recall scalar is a first learning-state
proxy; actual verse sequencing, word-level recall, pitch, breath, and motor
control remain separate future mechanisms.

An independent ten-minute quiet-recall probe follows the activity comparison.
Only the rehearsed lyric state improves in that probe; it does not silently
train guitar or voice. Concentration increases the explicit-rehearsal rate:

```
k_explicit = .01 + .04 * concentration
skill_after = 1 - (1 - skill_before) * exp(-minutes * k_explicit)
```

Incidental-learning accumulation remains positive in both modes. A separate
procedural-consolidation proxy increases with relaxation. These rates implement
Michael's proposed distinction as a testable modeling assumption; they are not
fitted neurobiology or evidence for a literal transfer of learning from Mind to
Body. Physical neural and bodily mechanisms remain within the composed Body.
The separate state variables let future data test and revise that hypothesis.

## Next small mechanisms

1. Replace supplied semantic detections with image/feature observations and
   uncertainty-aware association; preserve the raw retinal pathway.
2. Add uncertain hunger evidence, meal portions, food inventory, and stateful
   responses to invitations rather than assuming activity outcomes.
3. Add timed action execution, movement/collision feedback, changing parental
   availability, and a scheduler that revisits tradeoffs after each response.
4. Connect proposed contextual relations to the existing HRL/GRRLE evidence
   adapters. A relationship rule must remain distinct from an observed reply.
5. Fit learning and observation parameters on development data, then test on
   separate sessions. Current household parameters are transparent assumptions.

The earlier biochemical, bioelectric, statistical, and relational models remain
available. This module supplies situated decision inputs, not a replacement for
those mechanisms.
