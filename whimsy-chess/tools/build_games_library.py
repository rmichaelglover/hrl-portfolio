#!/usr/bin/env python3
"""
Build whimsy-chess/games-library.js from Lichess PGN exports.

Chess Maestro's 12 hand-written games stay where they are, in maestro.html. This
script produces the *library* — a much larger set pulled straight from Manny's
Lichess accounts — as a separate script file so the page itself stays readable
and the PWA doesn't have to ship it inline.

    # one request at a time; Lichess rate-limits hard
    curl -H "Accept: application/x-chess-pgn" \
      "https://lichess.org/api/games/user/mannyfresher?max=400&opening=true" \
      -o mannyfresher.pgn

    python3 tools/build_games_library.py mannyfresher.pgn pappymagee.pgn \
        --heroes mannyfresher,pappymagee --limit 120 -o games-library.js

Selection is deliberate, not "everything": checkmates first, then decisive games,
then the rest — capped per opening family so the list isn't fifty Kadas Attacks.
Whatever gets dropped is reported, never silently truncated.

By Manny Glover.
"""
import argparse
import json
import re
import sys
from collections import defaultdict

TAG = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
RESULT_TOKEN = re.compile(r'\b(1-0|0-1|1/2-1/2|\*)\s*$')


def split_games(text):
    """Split a multi-game PGN into (headers, movetext) pairs."""
    games, cur_tags, cur_moves, in_moves = [], {}, [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            if in_moves:                      # a new game's tags begin
                games.append((cur_tags, " ".join(cur_moves)))
                cur_tags, cur_moves, in_moves = {}, [], False
            m = TAG.match(s)
            if m:
                cur_tags[m.group(1)] = m.group(2)
        elif s:
            in_moves = True
            cur_moves.append(s)
    if cur_tags or cur_moves:
        games.append((cur_tags, " ".join(cur_moves)))
    return [(t, m) for t, m in games if m.strip()]


def ply_count(movetext):
    """Rough ply count — good enough for length filtering."""
    body = re.sub(r"\{[^}]*\}", " ", movetext)
    body = re.sub(r"\d+\.+", " ", body)
    body = RESULT_TOKEN.sub(" ", body)
    return len([t for t in body.split() if t not in ("", "*")])


def clean_movetext(movetext):
    """Strip move numbers and the trailing result; keep SAN (and any {[%clk]})."""
    s = re.sub(r"\{[^}]*\}", " ", movetext)         # drop comments: they bloat the file
    s = RESULT_TOKEN.sub(" ", s)
    s = re.sub(r"\d+\.+", " ", s)
    s = re.sub(r"\$\d+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Manny's signature flank systems, detected from the opening moves rather than
# trusting the ECO name (Lichess often files these under generic codes).
def family(tags, moves):
    toks = moves.split()
    w1 = toks[0] if toks else ""
    b1 = toks[1] if len(toks) > 1 else ""
    w2 = toks[2] if len(toks) > 2 else ""
    if w1 == "h4":
        return "Kadas Attack (1.h4)"
    if w1 == "h3":
        return "Clemenz / Creepy Crawly (1.h3)"
    if b1 == "h5":
        return "Goldsmith Defence (1…h5)"
    if b1 == "h6":
        return "Carr Defence (1…h6)"
    if w1 == "a4" or (w1 == "h4" and w2 == "a4"):
        return "Ware / flank (1.a4)"
    if w1 == "a3":
        return "Anderssen (1.a3)"
    if b1 == "a5":
        return "Mieses / a-file (1…a5)"
    if b1 == "a6":
        return "St. George (1…a6)"
    op = (tags.get("Opening") or "").strip()
    if op and op != "?":
        return op.split(":")[0].strip()
    return "Other"


def hero_of(tags, heroes):
    w = (tags.get("White") or "").lower()
    b = (tags.get("Black") or "").lower()
    for h in heroes:
        if w == h:
            return "w"
        if b == h:
            return "b"
    return None


def pretty_result(r):
    return {"1-0": "1–0", "0-1": "0–1", "1/2-1/2": "½–½"}.get(r, r or "?")


def slug(s, used):
    base = re.sub(r"[^a-z0-9]+", "", (s or "game").lower())[:22] or "game"
    k, n = base, 2
    while k in used:
        k = f"{base}{n}"
        n += 1
    used.add(k)
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pgn", nargs="+")
    ap.add_argument("--heroes", default="mannyfresher,pappymagee")
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--per-family", type=int, default=14)
    ap.add_argument("--min-ply", type=int, default=16)
    ap.add_argument("--max-ply", type=int, default=140)
    ap.add_argument("--exclude-file", default=None,
                    help="maestro.html — skip games already hand-curated there")
    ap.add_argument("-o", "--out", default="games-library.js")
    args = ap.parse_args()

    heroes = [h.strip().lower() for h in args.heroes.split(",") if h.strip()]

    already = set()
    if args.exclude_file:
        try:
            page = open(args.exclude_file, encoding="utf-8").read()
            for m in re.finditer(r'pgn:"([^"]{40,})"', page):
                toks = clean_movetext(m.group(1)).split()
                already.add(" ".join(toks[:12]))
        except OSError:
            pass

    cands, stats = [], defaultdict(int)
    for path in args.pgn:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"  ! cannot read {path}: {e}", file=sys.stderr)
            continue
        games = split_games(text)
        stats["parsed"] += len(games)
        for tags, movetext in games:
            hero = hero_of(tags, heroes)
            if hero is None:
                stats["dropped_no_hero"] += 1
                continue
            if (tags.get("Variant") or "Standard") != "Standard":
                stats["dropped_variant"] += 1
                continue
            n = ply_count(movetext)
            if not (args.min_ply <= n <= args.max_ply):
                stats["dropped_length"] += 1
                continue
            moves = clean_movetext(movetext)
            if not moves:
                stats["dropped_empty"] += 1
                continue
            if " ".join(moves.split()[:12]) in already:
                stats["dropped_already_curated"] += 1
                continue

            res = tags.get("Result", "*")
            won = (res == "1-0" and hero == "w") or (res == "0-1" and hero == "b")
            mate = moves.rstrip().endswith("#")
            try:
                he = int(tags.get("WhiteElo" if hero == "w" else "BlackElo", 0) or 0)
                oe = int(tags.get("BlackElo" if hero == "w" else "WhiteElo", 0) or 0)
            except ValueError:
                he = oe = 0
            upset = max(0, oe - he) if won else 0

            score = (120 if mate else 0) + (45 if won else 0) + min(upset, 400) / 4.0
            if 24 <= n <= 90:
                score += 12
            cands.append(dict(tags=tags, moves=moves, hero=hero, res=res, mate=mate,
                             won=won, upset=upset, plies=n, score=score,
                             family=family(tags, moves), he=he, oe=oe))

    cands.sort(key=lambda c: -c["score"])
    chosen, per_fam = [], defaultdict(int)
    for c in cands:
        if len(chosen) >= args.limit:
            break
        if per_fam[c["family"]] >= args.per_family:
            stats["dropped_family_cap"] += 1
            continue
        per_fam[c["family"]] += 1
        chosen.append(c)
    stats["dropped_over_limit"] = max(0, len(cands) - len(chosen) - stats["dropped_family_cap"])

    used, entries = set(), []
    for c in chosen:
        t = c["tags"]
        me = (t.get("White") if c["hero"] == "w" else t.get("Black")) or "?"
        opp = (t.get("Black") if c["hero"] == "w" else t.get("White")) or "?"
        op = (t.get("Opening") or "").strip()
        bits = []
        if c["mate"]:
            bits.append("mate")
        if c["upset"] >= 100:
            bits.append(f"+{c['upset']} Elo")
        tail = f" [{', '.join(bits)}]" if bits else ""
        label = f"{op if op and op != '?' else c['family']} · {pretty_result(c['res'])} vs {opp}{tail}"
        entries.append((slug(op or c["family"], used), dict(
            label=label,
            white=f"{t.get('White','?')} ({t.get('WhiteElo','?')})",
            black=f"{t.get('Black','?')} ({t.get('BlackElo','?')})",
            hero=c["hero"], result=pretty_result(c["res"]),
            tc=t.get("TimeControl", "") or "",
            group=c["family"], date=t.get("UTCDate", "") or "",
            eco=t.get("ECO", "") or "", account=me,
            site=t.get("Site", "") or "", pgn=c["moves"])))

    by_fam = defaultdict(int)
    for _, e in entries:
        by_fam[e["group"]] += 1

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("/* games-library.js — Chess Maestro's preloaded game library.\n"
                "   GENERATED by tools/build_games_library.py from Lichess PGN exports.\n"
                "   Do not hand-edit: re-run the script. The 12 hand-written games live in\n"
                "   maestro.html and are merged with these at load time.\n"
                f"   {len(entries)} games from: {', '.join(heroes)}\n"
                "   By Manny Glover. */\n")
        f.write("window.GAMES_LIBRARY = {\n")
        for k, e in entries:
            f.write(f"  {k}: {json.dumps(e, ensure_ascii=False)},\n")
        f.write("};\n")

    print(f"wrote {args.out} — {len(entries)} games")
    print("  by opening family:")
    for fam, n in sorted(by_fam.items(), key=lambda kv: -kv[1]):
        print(f"    {n:4d}  {fam}")
    print("  selection accounting (nothing silently dropped):")
    for k in sorted(stats):
        print(f"    {stats[k]:5d}  {k}")
    print(f"    {sum(1 for c in chosen if c['mate']):5d}  chosen ending in checkmate")


if __name__ == "__main__":
    main()
