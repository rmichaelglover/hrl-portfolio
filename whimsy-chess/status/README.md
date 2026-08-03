# Whimsy Chess — Project Status

Updated August 3, 2026. This is the wide-angle map; component READMEs remain the
authority for installation and detailed use.

## Current state

Chess Maestro is the flagship browser application and the canonical code lives in
this repository. The curated public copy lives in `hrl-portfolio/whimsy-chess`.
Both copies currently contain the same released Maestro, WorldKit, novella, and
archived-game material.

What works now:

- a self-contained chessboard with 25 hand-narrated games and PGN import;
- HRL piece-role analysis and white/contested/black board coloration;
- musical playback, inferred meter, MIDI, WAV, and prompt export;
- stateful HydroGRRLE terrain whose earth, water, ice, and sky evolve by ply;
- compatible World JSON, Minecraft datapack, and Roblox exports;
- installable/offline PWA behavior and a Pythonista wrapper;
- a Vim-native emoji study tool with the same 25-game teaching shelf;
- linear tween, classroom, and advanced novella paths;
- an optional ten-door Master Board adventure, beginning with CoachZ Crossing;
- an expanding source-game archive, including annotated study PGNs.

The current browser and export harness passes 26 checks. CoachZ Crossing is a
separate archive/adventure addition; it does not silently change the main linear
novella's 25-game structure.

## Current project frontier

The strongest completed integration is the loop from chess position to HRL roles,
coloration, evolving terrain, music, narration, and portable voxel-world exports.
Each representation derives from the same ply instead of behaving like an unrelated
visual effect.

The next useful frontier is explanation and comparison: show what an authored study
expected, what a chess engine recommends at a declared depth, what the player chose,
and how the recorded game actually ended. The proposed Engine & Study Coach is
specified in `engine-coach/README.md`; it is recorded for future work, not presented
as a finished feature.

## Near-term polish

- catalogue the recently audited study and chapter PGNs without duplicating exports;
- choose only distinct games for future linear or adventure narration;
- keep wins, losses, and draws so the archive teaches decisions rather than mythology;
- preserve PG/tween boundaries in the public story paths;
- keep the canonical and publication repositories synchronized and tested.

## August 3 work summary

Today's completed work joined three layers without starting another application:

- published the exact CoachZ Crossing PGN and its optional Master Board chapter;
- audited recent study exports, separating duplicates and already-narrated games from
  uncatalogued candidates;
- preserved the linear tween novella as its existing 25-game edition;
- recorded the future Engine & Study Coach, including played/study/engine overlays,
  outcome-balanced wins and losses, draws, and the **Avoid the Inaccuracy** exercise;
- archived the newer a6699–mannyfresher Checkers study and added both a rigorous
  examination and a separate Woodland narration in `games/README.md`.

The latest-game synthesis is brief: Black needed `3...e6` against the queen-and-bishop
battery, not `3...f6??`; both sides then missed decisive continuations; and late in the
game Black had the repeated defensive pattern `...Qxa6` before White's two queens built
the final mating net. The loss is valuable because the same avoidable idea appears at
multiple trainable checkpoints.

## Preview

A future learner pauses at a study position. One arrow shows the study author's
intended continuation; another shows the engine's current top move. When they agree,
the arrows become one. When they differ, the learner predicts why before revealing
the evaluation. In **Avoid the Inaccuracy** mode, the current chapter stops just before
the first meaningful inaccuracy by the learner's chosen side and asks for a better
continuation. The lesson may come from an exact recorded win or loss—and sometimes a
draw—because the result is evidence about the whole game, not a moral grade for one move.
