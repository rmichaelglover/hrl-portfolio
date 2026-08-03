# Chess Maestro in Pythonista on iOS

This is the first native iOS-compatible host for the existing browser Maestro.
It deliberately embeds the canonical `maestro.html` rather than creating a
second chess engine that would drift away from the web version.

## Transfer while internet is available

Copy the complete `whimsy-chess` directory to iCloud Drive or **On My iPhone /
Pythonista 3**. These files must remain together:

```text
whimsy-chess/
  maestro.html
  worldkit.js
  games-library.js
  pythonista/
    maestro_pythonista.py
```

Open `pythonista/maestro_pythonista.py` in Pythonista and press Run. The script:

1. starts a private server bound only to `127.0.0.1`;
2. displays Maestro in Pythonista's WebKit view;
3. provides a native **Import PGN** button using the iOS document picker;
4. sends every Maestro export to the iOS share sheet; and
5. runs without an internet connection after the folder has been transferred.

The PGN is placed in Maestro's existing Load panel. Review it, then press the
existing **Load game** button in the page.

## Compatibility boundary

Expected to work:

- embedded study library and move playback;
- board themes and character modes;
- narration, terrain, and HRL role overlays;
- local preferences;
- Web Audio after a user tap;
- PGN paste and native PGN import.

Needs a later native bridge:

- opening external portfolio links inside Pythonista;
- PWA installation and service workers (unnecessary inside Pythonista).

MIDI, WAV, Suno text, World JSON, Minecraft ZIP, and Roblox Lua exports are sent
from JavaScript to Python in ordered 12 KiB chunks. Python reconstructs the
file, verifies its byte count, gives duplicate names a numeric suffix, and opens
Pythonista's native iOS share sheet. Large WAV files are never placed into one
custom URL, avoiding WebKit/iOS URL-length limits.
