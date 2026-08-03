# Next milestones: Lichess foundation, then generic NLP-GRRLE

## 1. A legally grounded Lichess-derived chess platform

Use the official Lichess source repository and its actual license notices as the
authority. As verified on 2026-08-03, the `lila` server is **AGPL-3.0-or-later**,
Chessground is **GPL-3.0-or-later**, and the current mobile project is GPL-3.0.
Do not assume that one license covers every repository or bundled asset. Preserve
copyright notices, track upstream commits, document every
modification, and keep trademarks, service identity, user data, and third-party assets
separate from source-code licensing. Before public service deployment, review the
current Lichess license, API terms, rate limits, OAuth guidance, privacy obligations,
and asset licenses from official sources.

Official references: [lila](https://github.com/lichess-org/lila),
[Chessground](https://github.com/lichess-org/chessground),
[Lichess API](https://lichess.org/api), and
[Terms of Service](https://lichess.org/terms-of-service).

Architecture milestones:

1. Inventory which Chess Worlds features belong in an upstream-derived client,
   independent package, or optional service.
2. Build a local-first client for PGN/FEN replay, branching, Woodland/classical cast
   policy, narration, and HRL overlays.
3. Keep rules, analysis, and lightweight persistence client-side when trustworthy;
   reserve the server for identity, matchmaking, authoritative clocks/results, study
   collaboration, moderation, and durable storage.
4. Add edge caches/workers for static assets, public study snapshots, bounded API
   mediation, and geographically close read paths. Never place secrets or authoritative
   anti-cheat decisions in an untrusted client.
5. Measure a practical small-server target—CPU, memory, storage, egress, concurrent
   games, and recovery time—without making minimalism the product goal.
6. Establish upstream-sync, security, abuse prevention, backups, observability, and
   license-compliance checks before calling the service production-ready.

## 2. Return to advanced HRL: generic NLP-GRRLE streams

After the chess platform reaches agreed replay/edit, local-server, multiplayer, and
operational milestones, extract the existing text work from corpus-specific theology.
The generic system should accept arbitrary bounded text streams; segment assertions,
entities, events, and relations; propose labels with provenance; relax them under
pairwise and higher-order compatibility; retain a noise/unknown label; and expose
uncertainty, disagreement, temporal drift, and human corrections.

Initial benchmarks should include public-domain prose, technical logs, meeting or chat
streams with consent, news/event streams with licensed text, and synthetic adversarial
contradictions. Success criteria are calibration, provenance fidelity, correction cost,
streaming latency, memory bounds, and performance under topic shift—not agreement with
any religious, political, or philosophical conclusion.
