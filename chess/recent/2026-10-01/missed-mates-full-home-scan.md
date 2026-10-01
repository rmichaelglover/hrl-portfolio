# Full-drive missed-mate scan — mannyfresher

Scanned all 332 `.pgn` files under `/home/rmichaelglover` on 2026-10-01. After deduplication, this covered 686 standard-chess games and 39,129 positions. The exact search examined queen-first checking lines in mate in one through three and tested every legal defense in each returned line. It found 913 candidate positions overall, including 54 unique games where Mannyfresher was the side to move.

## Six distinct lessons

| Game | Position | Verified line | Move actually played |
|---|---:|---|---|
| [DHXB0n44](https://lichess.org/DHXB0n44) vs samurai2113 | 23. — M2 | `Qd7+ Kf8 Nxg6#` | `Nxe6` |
| [biu2zGAr](https://lichess.org/biu2zGAr) vs matisanchez76 | 25... — M3 | `Qa6+ Kb2 Qa3#` | `a5` |
| [2jid8qJX](https://lichess.org/2jid8qJX) vs chrkoll | 27. — M1 | `Qh8#` | `Qh7+` |
| [I0HkZs9T](https://lichess.org/I0HkZs9T) vs KelsoPresto | 20. — M2 | `Qh6+ Qg7 Qxg7#` | `Nxa8` |
| [Ti5XC3Lp](https://lichess.org/Ti5XC3Lp) vs Jane_jo | 23. — M2 | `Qc7+ Ke8 Qxe7#` | `Qxe7+` |
| [C2qo5zsO](https://lichess.org/C2qo5zsO) vs Edupuicon_utp | 20... — M3 | `Qa6+ Kd2 Qd3+ Kc1 Qc2#` | `Qxb2+` |

The complete original games remain in their source PGNs and the linked Lichess records. The JSON file stores every candidate returned by the scan, including opponent-to-move positions for comparison.
