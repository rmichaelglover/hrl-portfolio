# Being Alex

An interactive browser interpretation of Michael Emanuel Glover's virtual
Person framework. Original room artwork, first-person view, movement and
scenario logic use native Canvas, JavaScript and CSS. No build step, remote
assets, browser permissions or backend are required.

Open `index.html` from a local HTTP server or the published GitHub Pages site.

- Click clear floor to walk; pathfinding respects furniture clearance.
- Focus the room, then use W/S to move and A/D to turn (arrow keys also work).
- Mobile has touch movement buttons and tap-to-walk.
- Select an activity or let Alex choose from competing scenario scores.
- Change the household's preference, then ask about audible practice.
- Sound is opt-in and uses an original generated melody, not Beatles audio.
- The observer layer is a passive visual illustration; it is not live ROS.
- Pause and reset remain available. Reset starts a fresh evening.

The two modeled eye origins are 64 mm apart. Each eye has a field of view,
distance limit, and geometry-based occlusion; their union supplies a combined
first-person illustration. This is not retinal object recognition. The external
room view can show things outside Alex's current visual field.

The room scene uses A*'s simpler unweighted counterpart, breadth-first search,
on a 25 cm grid with obstacle clearance. Rendering uses isometric projection;
movement is checked continuously against the same collision rectangles.
Landmark identities and room geometry are supplied scenario knowledge, not
learned SLAM. Observation memory retains last-seen positions and timestamps;
current visibility is recomputed rather than inferred from memory.

The browser has its own transparent illustrative state, not compiled C++ or
live HRL/GRRLE inference. It links the executable C++ model and research modules.
Hunger, pleasant food, family availability, practice, rest, and long-term progress
have separate roles. Musical/lyric practice changes only the relevant skill
variables. Named mantra rewards are explicit scenario increments. Meters are
bounded scenario proxies, not clinical measurements or calibrated probabilities.

`browser_check.py` requires Python's websocket-client and an installed Chrome.
Run it with a local portfolio HTTP server on port 8788, or pass another URL as
its first argument. It checks navigation, collisions, changing visibility,
practice separation, family replies, permission, autonomous choices, pause,
reset and responsive layouts. Screenshots go to `/tmp`.

Originating ideas and project direction: Michael Emanuel Glover.
Assistant: implementation, original vector artwork, design and verification.
