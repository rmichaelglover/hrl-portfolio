# The Glims — Glover Machine Works

Michael Emanuel Glover's household-life simulation, expanded from Being Alex.
Canonical page: `virtual-cell-model/glims/`. The short `glims/` entry point and
original `virtual-cell-model/alex/` URL both redirect here.

Alex remains the playable person. Cypher and Rosy have their own small routines,
availability and happiness state, alongside Papa and Mama, who is present by the window.
All residents, needs and outcomes are simulated. This is not live ROS telemetry,
retinal object recognition, a clinical model, or a declaration of machine experience.

## Play

- Click/tap clear floor to walk, or focus the room and use WASD/arrow keys.
- Use the mobile movement pad when available.
- Select an activity; further selections join a queue of up to four plans.
  Click a queued plan to remove it. Manual steering clears pending plans.
- Let Alex choose if you want autonomous activity selection. The robot housemates
  have their own gentle routines even while you guide Alex directly.
- Household preferences govern replies to family invitations and audible practice.
  Rosy can be occupied with her own project; respecting that raises her named
  scenario happiness reward without forcing an interaction.
- A nap restores the energy proxy and closes the modeled visual display for a
  short scripted rest. It does not classify REM or reproduce real PSG physiology.
- Four evening wishes recognize music, a welcome interaction, making art or reading, and a completed
  replay of a learning example. They persist in explicit browser-local saves.
- Pause stops simulation time for the whole household. 1×/2×/4× adjusts playback.
- Save and Load use `glover-machine-works-glims-evening-v1` in localStorage.
  Saving is explicit; no cloud service is contacted. Loading restores progress,
  preferences and positions but clears plans and interpersonal permissions.
  Reset starts a fresh evening without deleting the saved one.

## Observe

The original isometric room, two modeled eye origins, geometry visibility,
short-lived observations, remembered leftovers, original opt-in generative music,
independent practice states, mantra rewards and journal remain available.
Pathfinding reserves space around furniture and other residents. Robot movements
respect personal space and yield near Alex's immediate planned route.

The optional observer layer is a visual simulation of passive tracking. It does
not alter Alex's needs, preferences or movement, and it is not connected to hardware.

## Workbench and actual C++ provenance

`learning-trace.json` is exported from
`../experiments/learning/synthetic-history.csv`; its metadata contains the source
SHA-256 and identifies the data as a **synthetic C++ verification replay**.
Working at the computer advances this saved trace. No optimizer is running in
the browser, and the household's scenario rules do not use fitted sleep models.
Measured EOG outputs and fitted parameters remain in the local study directory.

The research link opens the actual C++ forward/backward passes, gradient checks,
training protocol, and downloadable source. The replay shows the same-fixture
negative log likelihood from the public four-example verification, not held-out
clinical performance. The display begins at step one when that first recorded
optimizer update is replayed; it does not invent a step-zero loss.

## Implementation and checks

Native Canvas, JavaScript and CSS; no build step or third-party assets. The room
and original robot illustrations are code-native vector artwork. Run a local
HTTP server at the portfolio root and open `virtual-cell-model/glims/`.

`python3 virtual-cell-model/glims/browser_check.py` checks the local page on
port 8788. A URL argument checks a published deployment. Chrome and Python's
websocket-client are needed only for this test. Screenshots go to `/tmp`.

The checks cover original movement, collision/visibility, family replies and
practice separation, plus housemate availability, personal-space navigation,
queues, naps, wishes, trace replay, local saves, speed and five viewport widths.
The legacy `alexWorld` debug API is retained alongside `glimsWorld`.

Originating framework, characters, naming and direction: Michael Emanuel Glover.
Assistant: implementation, original illustrations, design and verification.

## Art and reading set

Painting hour and Reading hour invite the household to share a pastime. Papa,
Mama, Cypher and Rosy visibly carry sketchpads or books; Rosy keeps her existing
project availability. Alex can walk to the easel, read, or watch the television.
Every painter contributes a named picture to the household gallery. Choose
flowers, river or stars and garden, sunset or blue palettes. Add pointer/touch
brush strokes to Alex’s page and export a PNG. Artwork, strokes, reading progress
and the muted TV setting join existing browser saves; older saves still load.
The television displays an original procedural river scene without external video.
Reading excerpts are original short fiction. Family quiet preferences still govern
conversation invitations. Four wishes include a creative moment.

## Tiny Creeks: glamping in the glackyard

Go glamping opens a connected outdoor scene and freezes indoor activity. Alex,
Mama, Papa, Cypher and Rosy walk to shared tea, painting, reading, tent-rest and
footbridge destinations. Click the lawn for free walking. Grid pathfinding treats
the creek as impassable except at the bridge. Return inside to resume the house.
Shared pause and speed apply outdoors; a completed activity updates the existing
Alex state and painting contributes to the same gallery. Evening lights toggle
the outdoor palette and string lights. Save evening stores both home progress and
validated outdoor positions under separate localStorage keys; old home saves work.

The actual Tiny Creek World `world-core.js` supplies its deterministic,
Georgia-inspired fictional neighbor roster. Links connect to the existing whole
world and chess editions; this does not merge those games’ inventories or saves.
`glackyard.js` provides original canvas landscape, household movement and routing.
Browser checks cover bridge crossing, activity rewards, outdoor pause/save/load,
and all five responsive widths, as well as existing indoor regression checks.

Originating glackyard and Tiny Creeks integration concept: Michael Emanuel Glover.

## Glackyard wildlife

Eight original vector neighbors appear in the landscape: owls, chipmunks,
squirrels, birds, fishies, froggies, lizards and skinks. Fish animate within the
creek above the bridge; frogs hop along the bank. The owl wakes at night while
daytime critters settle down. Pause freezes their animation. Select a neighbor
from the keyboard-accessible notebook or tap its canvas illustration to highlight
it and read a short description. These are fictional garden characters, separate
from the shared Tiny Creek World regional roster. No wildlife save migration is
needed. Original direction and characters: Michael Emanuel Glover; assistant:
vector drawing and implementation.
