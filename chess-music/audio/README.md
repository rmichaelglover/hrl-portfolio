# Van’t Kruijsing — Head-Nod Chess

A first original synthesized draft for Manny Glover: 85 BPM, swung drums, warm bass, soft chords, and chess-derived melodies. Approximately 93 seconds, 44.1 kHz stereo WAV. There are no third-party audio samples.

Source: https://lichess.org/study/7hLlnCHF
Chapter: https://lichess.org/study/7hLlnCHF/wHZor7mJ
Game: mannyfresher vs sidpadhi, September 8, 2026, 1–0, ending Rh8#.

## Open in Audacity

1. In Audacity choose **File → Open**, select **List of files in basic text format** if needed, and open `Open-in-Audacity.lof`. All five lossless FLAC stems import into the same project at time zero.
2. Press Space to listen. Solo the drum track, then bring in bass, chords, and the White/Black move melodies.
3. Optionally choose **File → Import → Labels** and import `Audacity-labels.txt`. Labels mark each half-move, including the final checkmate.
4. Choose **File → Save Project** to preserve your arrangement and edits. Your installed Audacity 2.4.2 uses `.aup` plus a companion data folder; keep both together. Newer Audacity versions use `.aup3`. Export audio when ready to share it.

`Listen.mp3` is the reference mix. Do not import it alongside the five stems unless you mute it; otherwise you will double the music.

FLAC stems decode to the same samples as the original WAVs. The five stems share one gain so their sum reproduces the reference mix, which peaks at −3 dBFS. Keep track gains at zero to start. Lower the master level if your edits create clipping.

White is a higher-register melody panned slightly left; Black answers lower and slightly right. Destination files choose scale degrees, upper destination ranks raise an octave, captures are louder, and checks add a fifth. Mainline moves only; engine variations are excluded. The synthesized backing is an artistic arrangement, not a claim that chess inherently determines a unique composition.

`moves.csv` provides the exact move/time/note mapping; `study.pgn` preserves all 21 downloaded chapters; `track.json` gives metadata. Run `python3 make_track.py` to rebuild (requires NumPy and python-chess, already available on this machine).

Audacity LOF documentation: https://manual.audacityteam.org/man/lof_files.html
