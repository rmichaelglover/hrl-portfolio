#!/usr/bin/env python3
"""Compile every local PGN into the Relaxed Chess Brain's learned graph.

No chess package is required.  The model learns from SAN tokens: local move
contexts become objects, candidate continuations become labels, and observed
frequency supplies the prior/compatibility field used by the browser's
relaxation loop.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

TAG = re.compile(r'^\[([^ ]+)\s+"(.*)"\]$')
COMMENTS = re.compile(r"\{[^}]*\}|;[^\n]*")
MOVE_NO = re.compile(r"^\d+\.(?:\.\.)?")
RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}


def games_in(text: str):
    """Yield (headers, SAN tokens), discarding comments and side variations."""
    chunks = re.split(r"\n\s*\n(?=\[Event\s)", text.replace("\r", ""))
    for chunk in chunks:
        headers, body = {}, []
        for line in chunk.splitlines():
            match = TAG.match(line.strip())
            if match:
                headers[match.group(1)] = match.group(2)
            else:
                body.append(line)
        movetext = COMMENTS.sub(" ", " ".join(body))
        # Remove recursive annotation variations without trying to interpret them.
        while "(" in movetext:
            reduced = re.sub(r"\([^()]*\)", " ", movetext)
            if reduced == movetext:
                break
            movetext = reduced
        moves = []
        for raw in movetext.split():
            token = MOVE_NO.sub("", raw).strip()
            if not token or token in RESULTS or token.startswith("$") or token == "...":
                continue
            token = re.sub(r"[!?]+$", "", token)
            if token and not token[0].isdigit():
                moves.append(token)
        if moves:
            yield headers, moves


def motif(move: str) -> str:
    if move in {"O-O", "O-O-O"}: return "king safety"
    if "=" in move: return "promotion"
    if "#" in move: return "mate"
    if "+" in move: return "check"
    if "x" in move: return "capture"
    if move.startswith("Q"): return "queen activity"
    if move.startswith(("N", "B")): return "development"
    if move.startswith("R"): return "rook activity"
    if move.startswith("K"): return "king activity"
    if move[:1] in "abcdefgh": return "pawn structure"
    return "other"


def compile_brain(root: Path, max_contexts: int = 180):
    files = sorted(root.rglob("*.pgn"))
    seen, games, transitions = set(), [], defaultdict(Counter)
    transition_evidence = defaultdict(list)
    move_counts, motif_counts, opening_counts = Counter(), Counter(), Counter()
    results, plies = Counter(), 0
    for path in files:
        try:
            parsed = games_in(path.read_text(encoding="utf-8", errors="replace"))
            for headers, moves in parsed:
                signature = " ".join(moves) + "|" + headers.get("White", "") + "|" + headers.get("Black", "")
                digest = hashlib.sha256(signature.encode()).hexdigest()
                if digest in seen:
                    continue
                seen.add(digest)
                games.append((headers, moves, str(path)))
                results[headers.get("Result", "*")] += 1
                plies += len(moves)
                move_counts.update(moves)
                motif_counts.update(map(motif, moves))
                opening_counts[" ".join(moves[:4])] += 1
                for i, move in enumerate(moves):
                    for width in (0, 1, 2, 3):
                        context = tuple(moves[max(0, i-width):i])
                        if len(context) == width:
                            transitions[context][move] += 1
                            key = (context, move)
                            if len(transition_evidence[key]) < 4:
                                transition_evidence[key].append({
                                    "white": headers.get("White", "?"),
                                    "black": headers.get("Black", "?"),
                                    "result": headers.get("Result", "*"),
                                    "site": headers.get("Site", ""),
                                    "event": headers.get("Event", "Game"),
                                    "ply": i + 1,
                                })
        except OSError:
            continue

    ranked_contexts = sorted(
        (c for c in transitions if c),
        key=lambda c: (-sum(transitions[c].values()), -len(c), c),
    )[:max_contexts]
    contexts = []
    for context in ranked_contexts:
        counts = transitions[context]
        total = sum(counts.values())
        candidates = [
            {"move": m, "count": n, "prior": round(n / total, 6), "motif": motif(m),
             "evidence": transition_evidence[(context, m)]}
            for m, n in counts.most_common(8)
        ]
        contexts.append({"key": " ".join(context), "count": total, "next": candidates})

    # A compact learned hierarchy for display: corpus -> openings -> motifs -> moves.
    nodes = [{"id": "corpus", "label": "PGN memory", "layer": 0, "weight": len(games)}]
    links = []
    for i, (name, count) in enumerate(opening_counts.most_common(14)):
        oid = f"o{i}"; nodes.append({"id": oid, "label": name, "layer": 1, "weight": count})
        links.append({"source": "corpus", "target": oid, "weight": count})
    for i, (name, count) in enumerate(motif_counts.most_common()):
        mid = f"p{i}"; nodes.append({"id": mid, "label": name, "layer": 2, "weight": count})
        links.append({"source": "corpus", "target": mid, "weight": count})
    top_moves = move_counts.most_common(28)
    motif_ids = {n["label"]: n["id"] for n in nodes if n["layer"] == 2}
    for i, (name, count) in enumerate(top_moves):
        mid = f"m{i}"; nodes.append({"id": mid, "label": name, "layer": 3, "weight": count})
        links.append({"source": motif_ids[motif(name)], "target": mid, "weight": count})

    # Exact empirical one-ply compatibility.  Entry [i][j] is the observed
    # conditional frequency P(next move j | move i), with no smoothing,
    # motif bonus, or relaxation-derived adjustment.
    auto_names = [name for name, _ in top_moves]
    auto_matrix = []
    for source in auto_names:
        row_counts = transitions.get((source,), Counter())
        denominator = sum(row_counts.values())
        auto_matrix.append([
            round(row_counts[target] / denominator, 8) if denominator else 0.0
            for target in auto_names
        ])

    return {
        "meta": {"files": len(files), "unique_games": len(games), "plies": plies,
                 "unique_moves": len(move_counts), "results": results,
                 "model": "hierarchical probabilistic relaxation labeling",
                 "noise_label": True, "context_depth": 3},
        "global": [{"move": m, "count": n, "motif": motif(m)} for m, n in move_counts.most_common(60)],
        "contexts": contexts, "nodes": nodes, "links": links,
        "automata": {"moves": auto_names, "compatibility": auto_matrix,
                     "definition": "exact empirical P(next | current), unsmoothed"},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pgn-root", type=Path, default=Path.home())
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("brain.json"))
    args = parser.parse_args()
    brain = compile_brain(args.pgn_root)
    args.output.write_text(json.dumps(brain, separators=(",", ":")), encoding="utf-8")
    print(f"learned {brain['meta']['unique_games']} unique games / {brain['meta']['plies']} plies from {brain['meta']['files']} PGNs")


if __name__ == "__main__":
    main()
