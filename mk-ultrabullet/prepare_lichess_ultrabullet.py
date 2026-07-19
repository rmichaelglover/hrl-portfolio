#!/usr/bin/env python3
"""Extract anonymous musical features from Lichess PGN exports.

Accepts plain PGN or .zst (when the optional zstandard package is installed).
Only games with zero increment and <= 30 seconds initial time are retained.
Player names, ratings, links, and dates are intentionally omitted.
"""
from __future__ import annotations

import argparse
import io
import json
import re
from pathlib import Path

HEADER = re.compile(r'^\[([A-Za-z0-9_]+)\s+"(.*)"\]$')
CLOCK = re.compile(r'\[%clk\s+(\d+):(\d+):([\d.]+)\]')
MOVE = re.compile(r'(?<!\S)(?:\d+\.(?:\.\.)?)?\s*([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|O-O(?:-O)?[+#]?)')


def _seconds(value: str) -> float:
    h, m, s = CLOCK.search(value).groups()  # type: ignore[union-attr]
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_game(text: str) -> dict | None:
    headers = {}
    body = []
    for line in text.splitlines():
        m = HEADER.match(line.strip())
        if m:
            headers[m.group(1)] = m.group(2)
        elif line.strip():
            body.append(line.strip())
    tc = headers.get("TimeControl", "")
    m = re.fullmatch(r'(\d+)\+(\d+)', tc)
    if not m or int(m.group(1)) > 30 or int(m.group(2)) != 0:
        return None
    movetext = " ".join(body)
    sans = MOVE.findall(re.sub(r'\([^)]*\)', ' ', movetext))
    clocks = [_seconds(x.group(0)) for x in CLOCK.finditer(movetext)]
    spent = []
    last = {0: float(m.group(1)), 1: float(m.group(1))}
    for i, remaining in enumerate(clocks):
        side = i % 2
        spent.append(max(0.01, last[side] - remaining))
        last[side] = remaining
    if not spent:
        spent = [0.18] * len(sans)
    return {
        "time_control": tc,
        "plies": len(sans),
        "spent": [round(x, 3) for x in spent[: len(sans)]],
        "captures": [i for i, san in enumerate(sans) if "x" in san],
        "checks": [i for i, san in enumerate(sans) if "+" in san or "#" in san],
        "castles": [i for i, san in enumerate(sans) if san.startswith("O-O")],
        "promotions": [i for i, san in enumerate(sans) if "=" in san],
        "result": headers.get("Result", "*"),
    }


def iter_games(stream):
    block = []
    for line in stream:
        if line.startswith("[Event ") and block:
            yield "".join(block)
            block = []
        block.append(line)
    if block:
        yield "".join(block)


def open_text(path: Path):
    if path.suffix != ".zst":
        return path.open(encoding="utf-8", errors="replace")
    try:
        import zstandard
    except ImportError as exc:
        raise SystemExit("For .zst input: python3 -m pip install zstandard") from exc
    raw = path.open("rb")
    reader = zstandard.ZstdDecompressor().stream_reader(raw)
    return io.TextIOWrapper(reader, encoding="utf-8", errors="replace")


def extract(path: Path, limit: int = 5000) -> dict:
    games = []
    with open_text(path) as stream:
        for block in iter_games(stream):
            game = parse_game(block)
            if game:
                games.append(game)
                if len(games) >= limit:
                    break
    return {"schema": "mk-ultrabullet-v1", "source": "Lichess CC0 PGN export", "games": games}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--limit", type=int, default=5000)
    args = ap.parse_args()
    data = extract(args.input, args.limit)
    args.output.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(data['games'])} anonymous ultrabullet games to {args.output}")


if __name__ == "__main__":
    main()
