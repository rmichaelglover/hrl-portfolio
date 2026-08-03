# Vim Chess Tutor — deferred companion to Ella the Wise One

Status: **recorded for future work; not an active implementation task.**

The Vim Chess Tutor should be a keyboard-first teaching companion inside Vim
Chess, related to but distinct from Ella the Wise One. It should preserve the
quiet terminal board, avoid showing legal-move hints unless requested, and
teach by questions rather than by taking control of the game.

Possible future shape:

- `:ChessTutor` opens a narrow lesson/review pane beside the current board;
- the tutor asks one position-specific question at a time and accepts ordinary
  language, SAN, or square-based answers;
- hints progress from strategic purpose, to candidate pieces, to candidate
  moves, with the complete answer last;
- explanations contrast good human reasoning with engine verification and
  clearly distinguish forced tactics from judgment calls;
- an end-of-session multiple-choice analogy links the chess concept to another
  domain, with Ella offering elaboration or a graceful stopping point;
- all core lessons, question data, and inference run locally without accounts,
  advertising, telemetry, or paid APIs;
- accessibility includes classic pieces, text-only mode, stable-width Unicode,
  screen-reader-friendly narration, adjustable verbosity, and no timed pressure;
- saved progress belongs to the learner and uses an inspectable local format.

An initial implementation should reuse Vim Chess's position/move model, expose
a small lesson protocol, and connect to NLP-HRL through an optional local
process. Chess remains deterministic; language interpretation may express
uncertainty and ask for clarification.

Licensing goal: FOSS—**free and open-source software**. Educational datasets
need their own compatible licenses and provenance; “free of charge” alone does
not make a dataset open source.

## Keyboard musicianship branch

Record a second, optional tutor that grows beyond Vim and beyond ordinary typing.
The home row becomes both an editor posture and a musical rest position; motions teach
intervals, rhythm, chord function, voice leading, and fingering without making either
Vim or a physical instrument mandatory. Lessons should support standard keyboards,
Vim notation, MIDI-capable devices, accessible one-hand mappings, and silent visual
practice. This is a future design note, not an active implementation task.
