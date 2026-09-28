#!/usr/bin/env python3
"""
Chess Time Machine v0.1
-----------------------
A zero-dependency research prototype for estimating cross-era chess strength.

Important:
- Glicko-2 ratings are relative to the pool in which they are computed.
- This prototype separates:
    1) within-pool Glicko-2 estimation
    2) cross-era alignment via explicit era offsets / bridge assumptions
- The bundled demo data are SYNTHETIC and are NOT historical claims.

CSV format:
date,white,black,result,era
1858-01-01,Paul Morphy,Adolf Anderssen,1-0,1850s
...
result must be one of: 1-0, 0-1, 1/2-1/2
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# ----------------------------
# Glicko-2 constants / helpers
# ----------------------------

GLICKO2_SCALE = 173.7178
DEFAULT_RATING = 1500.0
DEFAULT_RD = 350.0
DEFAULT_VOL = 0.06
TAU = 0.5
EPSILON = 1e-6


def rating_to_mu(rating: float) -> float:
    return (rating - 1500.0) / GLICKO2_SCALE


def rd_to_phi(rd: float) -> float:
    return rd / GLICKO2_SCALE


def mu_to_rating(mu: float) -> float:
    return 1500.0 + GLICKO2_SCALE * mu


def phi_to_rd(phi: float) -> float:
    return GLICKO2_SCALE * phi


def g(phi: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))


def E(mu: float, mu_j: float, phi_j: float) -> float:
    return 1.0 / (1.0 + math.exp(-g(phi_j) * (mu - mu_j)))


@dataclass
class Player:
    name: str
    rating: float = DEFAULT_RATING
    rd: float = DEFAULT_RD
    vol: float = DEFAULT_VOL
    era: str = "unknown"

    @property
    def mu(self) -> float:
        return rating_to_mu(self.rating)

    @property
    def phi(self) -> float:
        return rd_to_phi(self.rd)


@dataclass
class Game:
    white: str
    black: str
    score_white: float
    era: str = "unknown"
    date: str = ""


def parse_result(result: str) -> float:
    r = result.strip()
    if r == "1-0":
        return 1.0
    if r == "0-1":
        return 0.0
    if r in ("1/2-1/2", "½-½"):
        return 0.5
    raise ValueError(f"Unsupported result: {result!r}")


def load_games_csv(path: Path) -> List[Game]:
    games = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"white", "black", "result"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing columns: {sorted(missing)}")

        for row in reader:
            games.append(
                Game(
                    white=row["white"].strip(),
                    black=row["black"].strip(),
                    score_white=parse_result(row["result"]),
                    era=(row.get("era") or "unknown").strip(),
                    date=(row.get("date") or "").strip(),
                )
            )
    return games


def _new_volatility(phi: float, sigma: float, delta: float, v: float, tau: float = TAU) -> float:
    """
    Glicko-2 volatility update from Mark Glickman's published algorithm.
    """
    a = math.log(sigma * sigma)

    def f(x: float) -> float:
        ex = math.exp(x)
        num = ex * (delta * delta - phi * phi - v - ex)
        den = 2.0 * (phi * phi + v + ex) ** 2
        return num / den - (x - a) / (tau * tau)

    A = a

    if delta * delta > phi * phi + v:
        B = math.log(delta * delta - phi * phi - v)
    else:
        k = 1
        B = a - k * tau
        while f(B) < 0:
            k += 1
            B = a - k * tau

    fA = f(A)
    fB = f(B)

    while abs(B - A) > EPSILON:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)
        if fC * fB <= 0:
            A = B
            fA = fB
        else:
            fA /= 2.0
        B = C
        fB = fC

    return math.exp(A / 2.0)


def update_player(player: Player, results: List[Tuple[Player, float]]) -> Player:
    """
    Update one player for one rating period.
    results = [(opponent, score), ...]
    """
    mu = player.mu
    phi = player.phi
    sigma = player.vol

    if not results:
        phi_star = math.sqrt(phi * phi + sigma * sigma)
        return Player(player.name, player.rating, phi_to_rd(phi_star), sigma, player.era)

    inv_v = 0.0
    delta_sum = 0.0

    for opp, score in results:
        gj = g(opp.phi)
        ej = E(mu, opp.mu, opp.phi)
        inv_v += gj * gj * ej * (1.0 - ej)
        delta_sum += gj * (score - ej)

    v = 1.0 / inv_v
    delta = v * delta_sum
    sigma_prime = _new_volatility(phi, sigma, delta, v)

    phi_star = math.sqrt(phi * phi + sigma_prime * sigma_prime)
    phi_prime = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / v)

    sum_term = 0.0
    for opp, score in results:
        sum_term += g(opp.phi) * (score - E(mu, opp.mu, opp.phi))

    mu_prime = mu + phi_prime * phi_prime * sum_term

    return Player(
        name=player.name,
        rating=mu_to_rating(mu_prime),
        rd=phi_to_rd(phi_prime),
        vol=sigma_prime,
        era=player.era,
    )


def fit_glicko2(games: List[Game], periods: int = 12) -> Dict[str, Player]:
    """
    Repeated batch fitting for a compact research prototype.

    This is not a substitute for historically faithful rating periods.
    For production work, games should be grouped by real dates/rating periods.
    """
    eras = {}
    names = set()
    for gm in games:
        names.add(gm.white)
        names.add(gm.black)
        eras.setdefault(gm.white, gm.era)
        eras.setdefault(gm.black, gm.era)

    players = {
        n: Player(n, era=eras.get(n, "unknown"))
        for n in names
    }

    for _ in range(periods):
        buckets = defaultdict(list)

        # Snapshot opponents so all updates are simultaneous.
        snapshot = {
            n: Player(p.name, p.rating, p.rd, p.vol, p.era)
            for n, p in players.items()
        }

        for gm in games:
            w = snapshot[gm.white]
            b = snapshot[gm.black]
            buckets[gm.white].append((b, gm.score_white))
            buckets[gm.black].append((w, 1.0 - gm.score_white))

        players = {
            n: update_player(snapshot[n], buckets[n])
            for n in snapshot
        }

    return players


# ----------------------------
# Cross-era alignment
# ----------------------------

def align_to_modern(
    players: Dict[str, Player],
    era_offsets: Dict[str, float],
    modern_center: float = 2100.0,
) -> Dict[str, Tuple[float, float]]:
    """
    Convert within-pool ratings to a toy modern-equivalent scale.

    modern_equivalent = modern_center + (within_pool_rating - 1500) + era_offset

    The era_offset is intentionally explicit. In a serious project it should be
    inferred from bridge evidence: overlapping careers, engine move quality,
    opening/endgame knowledge adjustments, time controls, etc.
    """
    out = {}
    for name, p in players.items():
        offset = era_offsets.get(p.era, 0.0)
        modern_equiv = modern_center + (p.rating - 1500.0) + offset
        out[name] = (modern_equiv, p.rd)
    return out


def expected_score(r_a: float, r_b: float) -> float:
    """
    Elo-style expected score for an intuitive head-to-head display.
    """
    return 1.0 / (1.0 + 10.0 ** ((r_b - r_a) / 400.0))


# ----------------------------
# Demo
# ----------------------------

def synthetic_demo_games() -> List[Game]:
    """
    Deliberately fictional data used only to prove the pipeline works.
    """
    rows = [
        ("Paul Morphy", "Adolf Anderssen", 1.0, "1850s"),
        ("Paul Morphy", "Adolf Anderssen", 1.0, "1850s"),
        ("Paul Morphy", "Adolf Anderssen", 0.5, "1850s"),
        ("Paul Morphy", "Louis Paulsen", 1.0, "1850s"),
        ("Paul Morphy", "Louis Paulsen", 1.0, "1850s"),
        ("Adolf Anderssen", "Louis Paulsen", 0.5, "1850s"),

        ("Wilhelm Steinitz", "Johannes Zukertort", 1.0, "1880s"),
        ("Wilhelm Steinitz", "Johannes Zukertort", 1.0, "1880s"),
        ("Wilhelm Steinitz", "Johannes Zukertort", 0.5, "1880s"),

        ("Emanuel Lasker", "Wilhelm Steinitz", 1.0, "1890s"),
        ("Emanuel Lasker", "Wilhelm Steinitz", 1.0, "1890s"),
        ("Emanuel Lasker", "Wilhelm Steinitz", 0.5, "1890s"),

        ("Jose Capablanca", "Emanuel Lasker", 1.0, "1920s"),
        ("Jose Capablanca", "Emanuel Lasker", 0.5, "1920s"),
        ("Jose Capablanca", "Emanuel Lasker", 1.0, "1920s"),

        ("Bobby Fischer", "Boris Spassky", 1.0, "1970s"),
        ("Bobby Fischer", "Boris Spassky", 1.0, "1970s"),
        ("Bobby Fischer", "Boris Spassky", 0.5, "1970s"),

        ("Garry Kasparov", "Anatoly Karpov", 1.0, "1980s"),
        ("Garry Kasparov", "Anatoly Karpov", 0.5, "1980s"),
        ("Garry Kasparov", "Anatoly Karpov", 1.0, "1980s"),

        ("Magnus Carlsen", "Modern GM Sample", 1.0, "modern"),
        ("Magnus Carlsen", "Modern GM Sample", 1.0, "modern"),
        ("Magnus Carlsen", "Modern GM Sample", 0.5, "modern"),
    ]
    return [Game(a, b, s, e) for a, b, s, e in rows]


def print_report(players: Dict[str, Player], aligned, compare_rating: float = 2100.0):
    ranked = sorted(
        players,
        key=lambda n: aligned[n][0],
        reverse=True
    )

    print("\nCHESS TIME MACHINE v0.1")
    print("Synthetic demonstration only — not historical estimates.\n")
    print(f"{'Player':24s} {'Era':8s} {'Pool':>8s} {'RD':>7s} {'ModernEq':>10s} {'vs 2100':>9s}")
    print("-" * 76)

    for name in ranked:
        p = players[name]
        modern, rd = aligned[name]
        exp = expected_score(compare_rating, modern)
        print(
            f"{name:24s} {p.era:8s} "
            f"{p.rating:8.1f} {rd:7.1f} {modern:10.1f} {exp:9.3f}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="Historical game CSV")
    parser.add_argument("--periods", type=int, default=12)
    parser.add_argument("--compare", type=float, default=2100.0)
    args = parser.parse_args()

    games = load_games_csv(args.csv) if args.csv else synthetic_demo_games()
    players = fit_glicko2(games, periods=args.periods)

    # Toy offsets, explicitly NOT empirical.
    # A real project should estimate these from bridge evidence.
    toy_offsets = {
        "1850s": -120.0,
        "1880s": -100.0,
        "1890s": -85.0,
        "1920s": -60.0,
        "1970s": -25.0,
        "1980s": -10.0,
        "modern": 0.0,
    }

    aligned = align_to_modern(players, toy_offsets)
    print_report(players, aligned, args.compare)

    print("\nInterpretation:")
    print("  Pool      = within-dataset Glicko-2 estimate")
    print("  RD        = rating deviation / uncertainty")
    print("  ModernEq  = toy modern-equivalent rating after explicit era offset")
    print("  vs 2100   = expected score of a 2100 player against that estimate")
    print("\nNext research step: replace toy era offsets with evidence-based bridges.")


if __name__ == "__main__":
    main()
