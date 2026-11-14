# Controlled Provocation: A Review of Six Recent Public Chess Studies

**Michael Emanuel Glover’s opening theory · 13 November 2026**

Originating theory, playing style, study curation and games: **Michael Emanuel Glover (mannyfresher)**. Assistant contribution: legal replay, operational definitions, engine screening and rechecks, aggregation, and explanatory writing.

## Finding

Your controlled-provocation idea has concrete tactical realizations in these studies. Its strongest examples do more than survive a queen threat: they answer it with a counter-threat, interposition, material gain, or mating attack. Fermathemate’s 10.Bf3 met …g4 and a mating finish; No_More_Bans_Pls’s later Nd5 allowed …Qxa1; A-Roy2025’s Nh4 allowed a favorable queen liquidation. These are observable commitments and consequences.

The same record also distinguishes productive queen threats from wasted moves. A fresh knight or bishop can develop well while attacking your queen. Repeated-piece moves are not automatically wasted either; their value depends on what they accomplish. The useful test is the position after your answer, including your own queen tempi, king safety, and available tactics.

## Your theory, made testable

> Make the position look inviting to attack, while preparing to exploit the attack’s commitments. Keep a functional structure, introduce deliberate unfamiliarity, and judge the opponent’s response rather than treating an unusual appearance as a defect.

The board-level hypothesis is that selected queen provocations elicit exploitable commitments. The psychological hypothesis is that opponents underestimate an unconventional player. The move records can test tactical consequences, development, and queen displacement; they do not record an opponent’s private beliefs. A successful counterattack is credited without inventing those beliefs.

## Complete inventory

All **77 chapters** in the six recent files were reviewed. They contain **76 unique games**, with **4,856 recorded plies** after deduplication. The unique results are **41 wins, 10 draws, 25 losses** from your side. The duplicate is the Svenjamin94 game `1ET6rM28`, appearing in two study chapters; both chapter locations remain indexed below.

There are **75 standard-rule chapters/games** eligible for standard Stockfish evaluation, including two chapters beginning from supplied positions, and **one Crazyhouse game**. Study membership totals below count the duplicate in each study where it appears.

| Study | Chapters | Wins | Draws | Losses | Queen moved by move 10 |
|---|---:|---:|---:|---:|---:|
| Kings Gambit | 9 | 3 | 1 | 5 | 5 |
| The Queen's Gambit: NETFLIX | 8 | 2 | 2 | 4 | 1 |
| Van Mieses | 1 | 1 | 0 | 0 | 1 |
| Rancid Randi | 18 | 10 | 2 | 6 | 11 |
| Pircerson Parks | 14 | 8 | 1 | 5 | 10 |
| Van't Kruijsing | 27 | 17 | 4 | 6 | 17 |

## What the queen-pressure audit found

An “early queen” means your queen first moved by recorded fullmove 10; **44 games** qualify, including **27 by move 5**. Those 44 games ended **26 wins, 6 draws, 12 losses**. This is a description of your selected studies, not an estimate of what early queen play causes against matched opponents.

After your queen had moved, **43 games** contained a qualifying newly available legal queen-capture threat in the first twenty recorded full moves. **30 of the 44 early-queen games** had such an episode. Across the complete sample there were **93 episodes**:

| Opponent action producing queen pressure | Episodes | Interpretation |
|---|---:|---|
| Repeated move with an already-active piece | 41 | A candidate commitment to examine; not automatically a wasted tempo. |
| First move of a knight or bishop | 22 | Developing with a threat; ordinarily a useful tempo unless concretely refuted. |
| Pawn commitment | 20 | Changes squares, lines or pawn structure; its actual costs require calculation. |
| Other first piece move | 9 | Includes queen/rook/king activity; examine the concrete purpose. |
| Crazyhouse piece drop | 1 | A variant-specific threat, treated separately from ordinary development. |

Of these 93 episodes, **70 were answered by a queen move**; **33 of those queen answers captured or gave check**, while **37 did neither**. There were **7 checking opponent moves** among the queen-pressure episodes. Those can be forks or forcing combinations rather than simple harassment. This ledger makes the cost on both sides visible; it is not a net-tempo or causal-gain calculation.

In **22 games**, you also made a non-castling king move within the first ten recorded full moves. That is another commitment to assess alongside early queen play. Your “one deliberate exception” idea is most demanding when several exceptions accumulate: queen moves, king relocation, pawn commitments, or delayed development. The report identifies those combinations without assuming that every one is unsound.

## Practical conclusions

1. **Best-supported mechanism: a forcing answer to the queen threat.** The clearest case is …g4 against Bf3: it both shields the queen’s line and attacks the threatening bishop. The queen is not just running away.

2. **Count developing threats honestly.** Nc3 and Nf3 against No_More_Bans_Pls were useful development, even though a later knight chase failed tactically. Different episodes in the same game deserve different judgments.

3. **Keep piece safety symmetric.** The opponent’s exposed attacker and your exposed queen obey the same capture geometry. Against pietro_atlas, Qxe4 entered the h7-bishop’s diagonal.

4. **Separate opening success, later recovery, and final result.** The kusal2022 game contains an opening gain and a later comeback. A win on time records successful practical play, but does not establish that the final position or opening was theoretically winning.

5. **Keep the broader theory broader than the queen.** The Justinnn09 win used an unconventional setup and active bishops before your queen first moved on move 19. That supports studying unfamiliar structures, not attributing every success to early queen psychology.

## Method and reading the game notes

Every supplied mainline was replayed with python-chess and the appropriate rules. Standard positions were screened with **Stockfish 14.1, one thread, 64 MB hash, 20,000 nodes per position**. Each eligible game’s largest screened personal setback and opponent concession, plus the strongest screened early queen-pressure episode where present, received a **200,000-node before/after recheck**. Candidate lines are legal continuations generated during those searches. Positions retain their replayed histories.

Engine figures are always **from White’s perspective**, in pawn units. They are finite-search assessments, not proofs of optimal play. Mate-search scores are printed as searched mates rather than being interpreted as ordinary centipawn changes. A changed evaluation can be a search-horizon effect; the notes explicitly flag important screening signals not reproduced by the deeper check.

A queen-pressure episode requires a newly available **legal** capture of your queen after an opposing move and after your queen has already moved. Pinned geometric attacks that cannot legally capture it are excluded. Threats can include checking forks and offers to trade queens. A queen actually captured on that move is separately recorded, rather than counted as an ensuing chase. In Crazyhouse, drops are labeled explicitly. “Repeat-piece” is based on the recorded piece’s prior moves; it is not a claim that its latest move lacked value.

The two “From Position” chapters are evaluated from their supplied FENs. Their numbering describes the supplied record, not unseen earlier play. No opponent intention, preparation, emotional state, or deliberate trap is inferred solely from the result.

## Selected examples in detail

### Fermathemate — Win, you played Black

A particularly clear realization of controlled provocation. Your queen on h5 was attacked by 10.Bf3. Instead of retreating, 10…g4 blocked the bishop’s line and attacked that bishop. After 11.Be4 hxg3 12.fxg3, 12…Qxh2# completed the attack. The observable gain is the counterattack and mating geometry; the opponent’s private impression of you is not recorded.

[Public study chapter](https://lichess.org/study/y98nnAdG/KPNfbnIQ)

### No_More_Bans_Pls — Win, you played Black

A mixed but instructive test. 3.Nc3 and 4.Nf3 developed fresh knights with threats against your queen, so those were productive development tempi. Later, 10.Nd5 attacked the queen on f6 but allowed 10…Qxa1. The deeper check confirms a major tactical concession there. The practical lesson is to distinguish sound developing threats from a later overextension.

[Public study chapter](https://lichess.org/study/2nJl10wd/DF5ruzYx)

### A-Roy2025 — Win, you played Black

White’s 7.Bg5 developed a bishop while threatening your queen. The later 9.Nh4 moved an already-active knight to attack the queen on f5. Your 9…Qxg5 10.Qxg5 fxg5 traded queens and removed White’s bishop. The distinction between a sound first developing threat and an exploitable follow-up is central to your thesis.

[Public study chapter](https://lichess.org/study/QLTafcOT/VNvrJfzC)

### kusal2022 — Win, you played White

Your 2.Qd2 and unusual setup met Black’s queen-and-bishop pressure. 5.e3 Qxe3+ 6.Qxe3 Bxe3 7.Bxe3 left you a bishop ahead for a pawn. That is an opening tactical payoff. The later game was a separate comeback: your first c-pawn eliminated a rook, the second promoted, and after the opponent’s responses you captured both their queens. 85.Qg2# converted the final queen ending. The opening payoff and the eventual win should be credited separately.

[Public study chapter](https://lichess.org/study/da9uLoen/JLwbFtbu)

### AndriyMAY — Loss, you played White

A counterexample to treating unfamiliarity as sufficient protection. 2.Qd2, 3.Kd1 and 4.Qe1 combined early queen play with an uncastled king relocation. Black’s central invasion culminated in 18…Qxd2#. The practical checkpoint is whether your king and defenders remain coordinated while you introduce the unusual feature.

[Public study chapter](https://lichess.org/study/y98nnAdG/GjzR5jsO)

### pietro_atlas — Loss, you played White

The clearest local piece-safety issue is 17.Qxe4 Bxe4: the bishop on h7 defended e4 along the diagonal. Your queen was lost when it captured the knight there. There was no qualifying early queen-chase episode in this chapter. This is a calculation/safety lesson rather than evidence that the provocation mechanism failed merely because an opening was unusual.

[Public study chapter](https://lichess.org/study/7hLlnCHF/dlVgbw2v)

### Justinnn09 — Win, you played White

A successful unconventional opening without an early queen outing: your queen first moved on move 19. The early story is pawn commitments and bishop activity, including Bxc7 and Bxb8. This belongs to the broader controlled-unfamiliarity programme, but should not be counted as evidence for a specifically early-queen psychological mechanism.

[Public study chapter](https://lichess.org/study/7hLlnCHF/1j1079eC)

## All 77 chapter locations

The index includes every chapter. Repeated game IDs link to the single deduplicated analysis.

| Study | Chapter | Opponent | Your side | Result | Game |
|---|---:|---|---|---|---|
| Kings Gambit | 1 | Chungkheu | White | Loss | [UttLxPKo](#game-uttlxpko) |
| Kings Gambit | 2 | amirof_99 | Black | Loss | [e5Jt4Pgw](#game-e5jt4pgw) |
| Kings Gambit | 3 | adechess | Black | Win | [CfGIc0tx](#game-cfgic0tx) |
| Kings Gambit | 4 | gamlet12345 | Black | Loss | [J3IcMnZK](#game-j3icmnzk) |
| Kings Gambit | 5 | Joslugal | Black | Win | [dKgQcSKp](#game-dkgqcskp) |
| Kings Gambit | 6 | Fermathemate | Black | Win | [df4AKckV](#game-df4akckv) |
| Kings Gambit | 7 | AndriyMAY | White | Loss | [AOYgpFzW](#game-aoygpfzw) |
| Kings Gambit | 8 | Svenjamin94 | White | Loss | [1ET6rM28](#game-1et6rm28) |
| Kings Gambit | 9 | tahan10 | Black | Draw | [LL67ubcC](#game-ll67ubcc) |
| The Queen's Gambit: NETFLIX | 1 | Greggorr | Black | Win | [F7VWRiUN](#game-f7vwriun) |
| The Queen's Gambit: NETFLIX | 2 | Ernestino_13 | Black | Win | [oDPwg4ID](#game-odpwg4id) |
| The Queen's Gambit: NETFLIX | 3 | kingEnteng | Black | Loss | [KU50IW6W](#game-ku50iw6w) |
| The Queen's Gambit: NETFLIX | 4 | daniel_dgm | Black | Draw | [q45ZUO6W](#game-q45zuo6w) |
| The Queen's Gambit: NETFLIX | 5 | endri_abazi_albania | White | Loss | [eYgsUU8Z](#game-eygsuu8z) |
| The Queen's Gambit: NETFLIX | 6 | ElJuliCC | Black | Loss | [LseqYWyF](#game-lseqywyf) |
| The Queen's Gambit: NETFLIX | 7 | fchfan | Black | Draw | [7BUj2Rvv](#game-7buj2rvv) |
| The Queen's Gambit: NETFLIX | 8 | EminBurak2018 | Black | Loss | [PCUmbC2N](#game-pcumbc2n) |
| Van Mieses | 1 | kusal2022 | White | Win | [i0W1q3IX](#game-i0w1q3ix) |
| Rancid Randi | 1 | YouddaVonBlbackoff | Black | Loss | [4182Oyps](#game-4182oyps) |
| Rancid Randi | 2 | Bntimane | Black | Win | [POY7Vryc](#game-poy7vryc) |
| Rancid Randi | 3 | Audvik_Acharya | Black | Win | [cwGjSsEN](#game-cwgjssen) |
| Rancid Randi | 4 | Legoboost | Black | Loss | [kzbSo2vU](#game-kzbso2vu) |
| Rancid Randi | 5 | MOREbming498 | Black | Win | [Ep2VxHEC](#game-ep2vxhec) |
| Rancid Randi | 6 | Carpena1980 | Black | Loss | [e9dop6g7](#game-e9dop6g7) |
| Rancid Randi | 7 | Ahmedadilzumrawi | Black | Draw | [JhxEruTO](#game-jhxeruto) |
| Rancid Randi | 8 | No_More_Bans_Pls | Black | Win | [2nJxcpYA](#game-2njxcpya) |
| Rancid Randi | 9 | sonsnare | Black | Loss | [ziNJzlZm](#game-zinjzlzm) |
| Rancid Randi | 10 | dragonakm | Black | Win | [Yez6uJVF](#game-yez6ujvf) |
| Rancid Randi | 11 | geogektor291 | Black | Win | [P1ARyfX7](#game-p1aryfx7) |
| Rancid Randi | 12 | clavenera | Black | Loss | [RICo4AbD](#game-rico4abd) |
| Rancid Randi | 13 | Succot | Black | Loss | [iXhLee7j](#game-ixhlee7j) |
| Rancid Randi | 14 | tucz1n | Black | Win | [VC5MszyS](#game-vc5mszys) |
| Rancid Randi | 15 | Aarkom | Black | Win | [cjAUBAG5](#game-cjaubag5) |
| Rancid Randi | 16 | bujurest | Black | Win | [Pe8OcQiJ](#game-pe8ocqij) |
| Rancid Randi | 17 | olk | Black | Draw | [g3J5EH39](#game-g3j5eh39) |
| Rancid Randi | 18 | carla227 | Black | Win | [UYo057a7](#game-uyo057a7) |
| Pircerson Parks | 1 | LeaderAswa | Black | Loss | [RPqJPm8K](#game-rpqjpm8k) |
| Pircerson Parks | 2 | Posseidon1977 | Black | Loss | [bEU6Bd9W](#game-beu6bd9w) |
| Pircerson Parks | 3 | GreyWizard-108 | Black | Loss | [cXjNygRo](#game-cxjnygro) |
| Pircerson Parks | 4 | Skn_wittur | Black | Loss | [4u6HwGxw](#game-4u6hwgxw) |
| Pircerson Parks | 5 | hopydopy | Black | Win | [475976ig](#game-475976ig) |
| Pircerson Parks | 6 | Azsch | Black | Loss | [YLjcKPXi](#game-yljckpxi) |
| Pircerson Parks | 7 | A-Roy2025 | Black | Win | [TaC6RghC](#game-tac6rghc) |
| Pircerson Parks | 8 | Ishanth14 | Black | Draw | [6BAtOdha](#game-6batodha) |
| Pircerson Parks | 9 | DmitriySvr | Black | Win | [NupgaHtz](#game-nupgahtz) |
| Pircerson Parks | 10 | trostyanko-13 | Black | Win | [rmMa0yGW](#game-rmma0ygw) |
| Pircerson Parks | 11 | Ttedv | Black | Win | [uwIkaXdf](#game-uwikaxdf) |
| Pircerson Parks | 12 | Raymond_Juma | Black | Win | [BJzsFoag](#game-bjzsfoag) |
| Pircerson Parks | 13 | Emanuel_pro | Black | Win | [jwTAjfrm](#game-jwtajfrm) |
| Pircerson Parks | 14 | WARIK_12364764-E | Black | Win | [tSUtX3fq](#game-tsutx3fq) |
| Van't Kruijsing | 1 | Genose | Black | Win | [DlsWV4m5](#game-dlswv4m5) |
| Van't Kruijsing | 2 | sidpadhi | White | Win | [LULfIsiU](#game-lulfisiu) |
| Van't Kruijsing | 3 | Svenjamin94 | White | Loss | [1ET6rM28](#game-1et6rm28) |
| Van't Kruijsing | 4 | franck_tp | White | Draw | [ZGcMZHLX](#game-zgcmzhlx) |
| Van't Kruijsing | 5 | chess06sisi | White | Win | [bFKICDGR](#game-bfkicdgr) |
| Van't Kruijsing | 6 | PamukSeker | White | Loss | [0Ot0AVBp](#game-0ot0avbp) |
| Van't Kruijsing | 7 | Afiyet2016 | White | Draw | [YUlGIZqU](#game-yulgizqu) |
| Van't Kruijsing | 8 | AbilashNelapati | Black | Win | [yHDp9B7U](#game-yhdp9b7u) |
| Van't Kruijsing | 9 | Stickity | White | Win | [zFiz2FiO](#game-zfiz2fio) |
| Van't Kruijsing | 10 | RogueDoc007 | White | Win | [l6XkdB9K](#game-l6xkdb9k) |
| Van't Kruijsing | 11 | tixupixu | White | Win | [pjvMqQeJ](#game-pjvmqqej) |
| Van't Kruijsing | 12 | JaydenMogorosii | White | Win | [OGrU8gpH](#game-ogru8gph) |
| Van't Kruijsing | 13 | pavelbraginskiy | White | Win | [P5Kc7JsX](#game-p5kc7jsx) |
| Van't Kruijsing | 14 | Beckerhecht | Black | Loss | [cimlkC2j](#game-cimlkc2j) |
| Van't Kruijsing | 15 | mogdalyan | White | Win | [gWIkn4LS](#game-gwikn4ls) |
| Van't Kruijsing | 16 | agenT007_xx2 | White | Win | [E4gJBzYS](#game-e4gjbzys) |
| Van't Kruijsing | 17 | cata1983 | Black | Win | [gzr8DmHy](#game-gzr8dmhy) |
| Van't Kruijsing | 18 | ximenacaicedoluna | White | Win | [Ok27NG4F](#game-ok27ng4f) |
| Van't Kruijsing | 19 | Rathiem888 | Black | Draw | [XMZxmF9X](#game-xmzxmf9x) |
| Van't Kruijsing | 20 | Sungirl20 | White | Loss | [2edLyNmz](#game-2edlynmz) |
| Van't Kruijsing | 21 | TheNorth87 | White | Win | [FnXnKKR3](#game-fnxnkkr3) |
| Van't Kruijsing | 22 | zxcvbnmasfesgjejwj | White | Win | [DItWyjG9](#game-ditwyjg9) |
| Van't Kruijsing | 23 | Dmiiitr | White | Draw | [yFUi7qS7](#game-yfui7qs7) |
| Van't Kruijsing | 24 | Arisotocrata | White | Win | [15QVQJQZ](#game-15qvqjqz) |
| Van't Kruijsing | 25 | AOK_Koliberda | Black | Loss | [BQVwXNN0](#game-bqvwxnn0) |
| Van't Kruijsing | 26 | pietro_atlas | White | Loss | [fjFuElbw](#game-fjfuelbw) |
| Van't Kruijsing | 27 | Justinnn09 | White | Win | [zoMm9deu](#game-zomm9deu) |

## Individual game reviews

<a id="game-uttlxpko"></a>

### 01. Chungkheu — Loss as White

**2026.08.03 · mannyfresher–Chungkheu · 0-1 · 52 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/A5hrlMxp) · [Game](https://lichess.org/UttLxPKo).

**Supplied-position chapter:** review begins from its PGN FEN, not an assumed standard initial position.

**Queen plan:** first queen move `11.Qe2+`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19...g6` (pawn commitment) → `20.Qxg6+`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `4.Be2, 5.Na3`; opponent: `1...Nc6, 8...Bb4+`. No non-castling early king move is recorded.

**Your screened critical decision: 23.h4.** 200,000-node recheck: Black searched mate in 6 → Black searched mate in 4. Pre-move candidate line: `23.Rd1 23...Qe2 24.Kb2 24...Qxd1 25.Bxe3`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 18...Nxb4+.** 200,000-node recheck: White -22.69 → White -14.84. Pre-move candidate line: `18...Nxe5 19.Re1`.

**Recorded finish:** `24.Kb3 24...Qxd3+ 25.Ka4 25...b5+ 26.axb6 26...axb6#`. The final position is checkmate.

**Opening record:** `1.fxe5 1...Nc6 2.exd5 2...Qxd5 3.e6 3...Qxe6+ 4.Be2 4...Qd5 5.Na3 5...Qxg2 6.Nc4 6...Qxh1 7.d3 7...Qxg1+ 8.Bf1 8...Bb4+ 9.c3 9...Ba5 10.b4 10...Bb6`.

<a id="game-e5jt4pgw"></a>

### 02. amirof_99 — Loss as Black

**2026.08.04 · amirof_99–mannyfresher · 1-0 · 49 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/Mr8XqeGX) · [Game](https://lichess.org/e5Jt4Pgw).

**Supplied-position chapter:** review begins from its PGN FEN, not an assumed standard initial position.

**Queen plan:** first queen move `17...Qb6`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Bxb7`; opponent: `6.Nf3, 8.Bxf4, 9.Nd2`. No non-castling early king move is recorded.

**Your screened critical decision: 24...Kb5.** 200,000-node recheck: White +3.23 → White searched mate in 1. Pre-move candidate line: `24...Bxb4 25.cxb4 25...Nh6 26.Bf4 26...Ng4`.

**Opponent’s screened critical decision: 17.Qa6.** 200,000-node recheck: White +14.30 → White +1.85. Pre-move candidate line: `17.Ne5+ 17...Ke6 18.Qxc6+ 18...Qd6 19.Qxa8`.

**Recorded finish:** `22...Ka6 23.Nxc6 23...Rc8 24.Nb4+ 24...Kb5 25.a4#`. The final position is checkmate.

**Opening record:** `1.exd5 1...c6 2.c3 2...f5 3.d4 3...g5 4.dxc6 4...h5 5.cxb7 5...Bxb7 6.Nf3 6...e4 7.Ne5 7...gxf4 8.Bxf4 8...h4 9.Nd2 9...h3 10.g3 10...e3`.

<a id="game-cfgic0tx"></a>

### 03. adechess — Win as Black

**2026.09.01 · adechess–mannyfresher · 0-1 · 76 plies · Time forfeit. [Study chapter](https://lichess.org/study/y98nnAdG/NkWt8i0H) · [Game](https://lichess.org/CfGIc0tx).

**Queen plan:** first queen move `2...Qd7`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `8...Bg4`; opponent: `2.Nf3, 3.Bc4, 7.Nc3`. Your non-castling early king moves: `6...Kxf7`.

**Your screened critical decision: 37...Kg2.** 200,000-node recheck: White searched mate in 4 → White searched mate in 3. Pre-move candidate line: `37...Na6 38.Ne4+ 38...Kh2 39.Rh8+ 39...Kg2`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 17.Qd5+.** 200,000-node recheck: White +12.92 → White +3.81. Pre-move candidate line: `17.c3 17...Nbc6 18.Qb3+ 18...Kg6 19.Qxb7`.

**Recorded finish:** `36.d7 36...Kg3 37.d8=Q 37...Kg2 38.Qd4 38...Kg3`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.Nf3 2...Qd7 3.Bc4 3...e5 4.Ng5 4...f6 5.Nf7 5...Qxf7 6.Bxf7+ 6...Kxf7 7.Nc3 7...h5 8.d4 8...Bg4 9.f3 9...Bxf3 10.gxf3 10...h4`.

<a id="game-j3icmnzk"></a>

### 04. gamlet12345 — Loss as Black

**2026.09.09 · gamlet12345–mannyfresher · 1-0 · 99 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/2GBr87NF) · [Game](https://lichess.org/J3IcMnZK).

**Queen plan:** first queen move `14...Qe7`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `1...Nh6, 4...Bh6`; opponent: `2.Bxh6, 7.Nc3`. Your non-castling early king moves: `6...Kf7, 9...Ke6, 10...Kd6`.

**Your screened critical decision: 29...a5.** 200,000-node recheck: White +63.68 → White +71.11. Pre-move candidate line: `29...Kb7 30.Nxb5`.

**Opponent’s screened critical decision: 14.Bxb8.** 200,000-node recheck: White +20.29 → White +6.63. Pre-move candidate line: `14.Qh7+`.

**Recorded finish:** `47...Kd3 48.Qd4+ 48...Ke2 49.Rf2+ 49...Ke1 50.Qd2#`. The final position is checkmate.

**Opening record:** `1.d4 1...Nh6 2.Bxh6 2...g5 3.Bxg5 3...f6 4.Bd2 4...Bh6 5.Bxh6 5...Rg8 6.Be3 6...Kf7 7.Nc3 7...Re8 8.Qd3 8...c6 9.Qxh7+ 9...Ke6 10.d5+ 10...Kd6`.

<a id="game-dkgqcskp"></a>

### 05. Joslugal — Win as Black

**2026.09.09 · Joslugal–mannyfresher · 0-1 · 88 plies · Time forfeit. [Study chapter](https://lichess.org/study/y98nnAdG/PzOR1RdH) · [Game](https://lichess.org/dKgQcSKp).

**Queen plan:** first queen move `3...Qe7`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `12.c3` (pawn commitment) → `12...Qxe4+`; `13.Qe2` (other piece move) → `13...Qxe2+`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `1...Nf6, 6...Be7, 9...Nxd7`; opponent: `2.Nc3, 5.Nf3, 6.Bg5, 7.Bb5`. Your non-castling early king moves: `4...Kd8`.

**Your screened critical decision: 42...g2.** 200,000-node recheck: White +11.38 → White searched mate in 5. Pre-move candidate line: `42...Kg2 43.hxg3`.

**Opponent’s screened critical decision: 44.Qd8.** 200,000-node recheck: White searched mate in 3 → White -6.07. Pre-move candidate line: `44.Qa8+ 44...Kf2 45.Rf4+ 45...Ke1 46.Qa1#`.

**Recorded finish:** `42.b7 42...g2 43.b8=Q 43...g1=Q 44.Qd8 44...Qd1+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...Nf6 2.Nc3 2...e5 3.d4 3...Qe7 4.d5 4...Kd8 5.Nf3 5...Qe8 6.Bg5 6...Be7 7.Bb5 7...c6 8.dxc6 8...Nxe4 9.cxd7 9...Nxd7 10.Bxe7+ 10...Qxe7`.

<a id="game-df4akckv"></a>

### 06. Fermathemate — Win as Black

**2026.09.09 · Fermathemate–mannyfresher · 0-1 · 24 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/KPNfbnIQ) · [Game](https://lichess.org/df4AKckV).

A particularly clear realization of controlled provocation. Your queen on h5 was attacked by 10.Bf3. Instead of retreating, 10…g4 blocked the bishop’s line and attacked that bishop. After 11.Be4 hxg3 12.fxg3, 12…Qxh2# completed the attack. The observable gain is the counterattack and mating geometry; the opponent’s private impression of you is not recorded.

**Queen plan:** first queen move `2...Qd7`; 3 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `10.Bf3` (repeat-piece move) → `10...g4`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `none recorded`; opponent: `1.Nf3, 3.Bg2`. Your non-castling early king moves: `3...Kd8`.

**Your screened critical decision: 3...Kd8.** 200,000-node recheck: White +0.86 → White +2.69. Pre-move candidate line: `3...c5 4.e3`.

**Opponent’s screened critical decision: 11.Be4.** 200,000-node recheck: White -2.57 → Black searched mate in 4. Pre-move candidate line: `11.Bg2`.

**Recorded finish:** `10.Bf3 10...g4 11.Be4 11...hxg3 12.fxg3 12...Qxh2#`. The final position is checkmate.

**Opening record:** `1.Nf3 1...d6 2.g3 2...Qd7 3.Bg2 3...Kd8 4.O-O 4...Qe8 5.d4 5...f6 6.c3 6...h5 7.Nh4 7...g5 8.Nf3 8...h4 9.Nfd2 9...Qh5 10.Bf3 10...g4`.

<a id="game-aoygpfzw"></a>

### 07. AndriyMAY — Loss as White

**2026.09.09 · mannyfresher–AndriyMAY · 0-1 · 36 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/GjzR5jsO) · [Game](https://lichess.org/AOYgpFzW).

A counterexample to treating unfamiliarity as sufficient protection. 2.Qd2, 3.Kd1 and 4.Qe1 combined early queen play with an uncastled king relocation. Black’s central invasion culminated in 18…Qxd2#. The practical checkpoint is whether your king and defenders remain coordinated while you introduce the unusual feature.

**Queen plan:** first queen move `2.Qd2`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `14...Bxd2` (repeat-piece move) → `15.Bxd2`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `7.Bxd3, 9.Nd2`; opponent: `2...Nf6, 3...Nc6, 4...Bf5`. Your non-castling early king moves: `3.Kd1`.

**Your screened critical decision: 16.Qe2.** 200,000-node recheck: White -8.79 → Black searched mate in 1. Pre-move candidate line: `16.Kc1 16...Nd4`.

**Opponent’s screened critical decision: 16...Qd5.** 200,000-node recheck: Black searched mate in 1 → White -6.10. Pre-move candidate line: `16...Qb1#`.

**Recorded finish:** `16.Qe2 16...Qd5 17.Qa6+ 17...Kb8 18.fxe4 18...Qxd2#`. The final position is checkmate.

**Opening record:** `1.d3 1...d5 2.Qd2 2...Nf6 3.Kd1 3...Nc6 4.Qe1 4...Bf5 5.e4 5...dxe4 6.f3 6...exd3 7.Bxd3 7...Bxd3 8.cxd3 8...Qxd3+ 9.Nd2 9...O-O-O 10.a4 10...e5`.

<a id="game-1et6rm28"></a>

### 08. Svenjamin94 — Loss as White

**2026.09.09 · mannyfresher–Svenjamin94 · 0-1 · 44 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/zPcFbWuf) · [Game](https://lichess.org/1ET6rM28).

**Queen plan:** first queen move `3.Qe1`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `12...Be7` (minor-piece development) → `13.Qxe7+`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `7.Be2, 9.Nf3`; opponent: `2...Nc6, 4...Bf5`. Your non-castling early king moves: `2.Ke2, 4.Kd1`.

**Your screened critical decision: 20.Bb2.** 200,000-node recheck: White +4.66 → Black searched mate in 4. Pre-move candidate line: `20.Bxb5 20...cxb4 21.Ke2 21...exd2 22.Bxd2`.

**Opponent’s screened critical decision: 20...cxb4.** 200,000-node recheck: Black searched mate in 4 → White -1.50. Pre-move candidate line: `20...Rxd2+ 21.Kc1 21...Qxe2 22.Ba3 22...Qd3`.

**Recorded finish:** `20.Bb2 20...cxb4 21.cxb4 21...Qxb4 22.Rb1 22...Qxd2#`. The final position is checkmate.

**Opening record:** `1.e3 1...c5 2.Ke2 2...Nc6 3.Qe1 3...d5 4.Kd1 4...Bf5 5.f4 5...Qd6 6.g4 6...Bxg4+ 7.Be2 7...f5 8.Qh4 8...d4 9.Nf3 9...dxe3 10.h3 10...Qxf4`.

**Duplicate preserved:** Kings Gambit chapter 8; Van't Kruijsing chapter 3.

<a id="game-ll67ubcc"></a>

### 09. tahan10 — Draw as Black

**2026.11.12 · tahan10–mannyfresher · 1/2-1/2 · 19 plies · Normal. [Study chapter](https://lichess.org/study/y98nnAdG/J4fx1nMj) · [Game](https://lichess.org/game/LL67ubcC).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `none recorded`; opponent: `2.Nf3`. Your non-castling early king moves: `5...Kxf7, 6...Ke6, 7...Kf7, 8...Kg7, 9...Kf7`.

**Your screened critical decision: 4...f6.** 200,000-node recheck: White +5.37 → White searched mate in 1. Pre-move candidate line: `4...d5 5.c3`.

**Opponent’s screened critical decision: 5.Nf7.** 200,000-node recheck: White searched mate in 1 → White +1.05. Pre-move candidate line: `5.Qh5#`.

**Recorded finish:** `7...Kf7 8.Qh5+ 8...Kg7 9.Qg4+ 9...Kf7 10.Qh5+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...b5 2.Nf3 2...g5 3.d4 3...c6 4.Nxg5 4...f6 5.Nf7 5...Kxf7 6.Qh5+ 6...Ke6 7.Qh3+ 7...Kf7 8.Qh5+ 8...Kg7 9.Qg4+ 9...Kf7 10.Qh5+`.

<a id="game-f7vwriun"></a>

### 10. Greggorr — Win as Black

**2026.10.05 · Greggorr–mannyfresher · 0-1 · 44 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/pgOaAEPX) · [Game](https://lichess.org/F7VWRiUN).

**Queen plan:** first queen move `14...Qb8`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nc6, 5...Nf6`; opponent: `6.Be3, 7.Nd2`. No non-castling early king move is recorded.

**Your screened critical decision: 18...Ke7.** 200,000-node recheck: White -10.31 → White -0.60. Pre-move candidate line: `18...Bxc8`.

**Opponent’s screened critical decision: 22.Bxe2.** 200,000-node recheck: White -10.96 → Black searched mate in 1. Pre-move candidate line: `22.gxf6+ 22...Kxf6 23.Rh2 23...Qxc3+ 24.Bd2`.

**Recorded finish:** `20.h4 20...Ba6 21.hxg5 21...Bxe2 22.Bxe2 22...Qxe2#`. The final position is checkmate.

**Opening record:** `1.d4 1...a6 2.e4 2...d6 3.c3 3...Nc6 4.f3 4...b5 5.Qe2 5...Nf6 6.Be3 6...h6 7.Nd2 7...g5 8.g4 8...e5 9.d5 9...Na5 10.b4 10...Nc4`.

<a id="game-odpwg4id"></a>

### 11. Ernestino_13 — Win as Black

**2026.10.05 · Ernestino_13–mannyfresher · 0-1 · 62 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/NvLHGgKw) · [Game](https://lichess.org/oDPwg4ID).

**Queen plan:** first queen move `13...Qf6`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Nc6, 4...Be6, 5...Nf6`; opponent: `5.Bh3, 10.Ne2`. No non-castling early king move is recorded.

**Your screened critical decision: 24...Rd4.** 200,000-node recheck: White -6.10 → White +0.86. Pre-move candidate line: `24...Rxf2+ 25.Kxf2`.

**Opponent’s screened critical decision: 28.fxg4.** 200,000-node recheck: White -8.31 → Black searched mate in 2. Pre-move candidate line: `28.Kf1 28...Rc4`.

**Recorded finish:** `29.Kf3 29...Rf4+ 30.Ke3 30...Qxf2+ 31.Kd3 31...Rh3#`. The final position is checkmate.

**Opening record:** `1.d4 1...a6 2.Qd3 2...Nc6 3.c3 3...d6 4.g3 4...Be6 5.Bh3 5...Nf6 6.Bxe6 6...fxe6 7.f3 7...e5 8.e3 8...exd4 9.exd4 9...d5 10.Ne2 10...e6`.

<a id="game-ku50iw6w"></a>

### 12. kingEnteng — Loss as Black

**2026.11.02 · kingEnteng–mannyfresher · 1-0 · 65 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/3bMq8LjT) · [Game](https://lichess.org/game/KU50IW6W).

**Queen plan:** first queen move `26...Qa5`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nc6, 4...Bf5, 9...Nge7`; opponent: `2.Bf4, 5.Bd3`. No non-castling early king move is recorded.

**Your screened critical decision: 26...Qa5.** 200,000-node recheck: White +20.35 → White searched mate in 3. Pre-move candidate line: `26...Qf8 27.Qb7+ 27...Qf7 28.Qxa8 28...Kh6`.

**Opponent’s screened critical decision: 23.Bg3.** 200,000-node recheck: White searched mate in 6 → White +14.84. Pre-move candidate line: `23.Nxg5 23...Rf8 24.Nf7+ 24...Kg7 25.Bh6+`.

**Recorded finish:** `30...a5 31.Qe6 31...a4 32.Qxf6+ 32...Kh5 33.Qxg5#`. The final position is checkmate.

**Opening record:** `1.d4 1...d6 2.Bf4 2...c5 3.c3 3...Nc6 4.e3 4...Bf5 5.Bd3 5...e5 6.Bxf5 6...f6 7.Bg3 7...exd4 8.exd4 8...cxd4 9.cxd4 9...Nge7 10.Bh3 10...Nd5`.

<a id="game-q45zuo6w"></a>

### 13. daniel_dgm — Draw as Black

**2026.11.10 · daniel_dgm–mannyfresher · 1/2-1/2 · 81 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/v3cUJAB4) · [Game](https://lichess.org/game/q45ZUO6W).

**Queen plan:** first queen move `11...Qxd1`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nf6, 5...Bg4, 8...Nxc6`; opponent: `5.Bc4, 7.Nxf3`. No non-castling early king move is recorded.

**Your screened critical decision: 35...Ke6.** 200,000-node recheck: White searched mate in 5 → White searched mate in 5. Pre-move candidate line: `35...Ke6 36.Bg4+ 36...Kf6 37.h8=Q+ 37...Kf7`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 41.g4.** 200,000-node recheck: White searched mate in 1 → terminal outcome. Pre-move candidate line: `41.Bc2#`.

**Recorded finish:** `38...Kf6 39.Qxa4 39...Kf5 40.Qxb3 40...Ke4 41.g4`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.d4 1...d5 2.e3 2...h6 3.c4 3...Nf6 4.cxd5 4...h5 5.Bc4 5...Bg4 6.f3 6...Bxf3 7.Nxf3 7...c6 8.dxc6 8...Nxc6 9.O-O 9...e6 10.Ne5 10...Nxe5`.

<a id="game-eygsuu8z"></a>

### 14. endri_abazi_albania — Loss as White

**2026.11.10 · mannyfresher–endri_abazi_albania · 0-1 · 62 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/XakVukqt) · [Game](https://lichess.org/game/eYgsUU8Z).

**Queen plan:** first queen move `14.Qb3`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `15...Nd4` (repeat-piece move) → `16.Bxd7+`; `16...Qxd7` (other piece move) → `17.Qg3`; `20...Nxe2` (repeat-piece move) → `21.Kxe2`.

**Theory assessment:** 0 developing minor-piece threat(s), 2 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `none recorded`; opponent: `6...Bd7`. No non-castling early king move is recorded.

**Your screened critical decision: 30.Ke5.** 200,000-node recheck: Black searched mate in 8 → Black searched mate in 2. Pre-move candidate line: `30.Bb4 30...Qxb4+ 31.Ke3 31...Re8+ 32.Kd3`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 28...g6.** 200,000-node recheck: White -12.79 → White -9.89. Pre-move candidate line: `28...Qd3 29.Ke5 29...Qxd2 30.Rc6 30...Qe2+`.

**Recorded finish:** `29.Rc7 29...Qa4+ 30.Ke5 30...Re8+ 31.Kf6 31...Qd4#`. The final position is checkmate.

**Opening record:** `1.d4 1...a6 2.e4 2...h6 3.d5 3...d6 4.e5 4...dxe5 5.d6 5...cxd6 6.b4 6...Bd7 7.a4 7...e6 8.b5 8...axb5 9.a5 9...b6 10.a6 10...Rxa6`.

<a id="game-lseqywyf"></a>

### 15. ElJuliCC — Loss as Black

**2026.11.10 · ElJuliCC–mannyfresher · 1-0 · 41 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/4gwsrGK2) · [Game](https://lichess.org/game/LseqYWyF).

**Queen plan:** first queen move `13...Qf8`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `14.Bh6` (minor-piece development) → `14...Qf6`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `6...Nf6, 10...Bf5`; opponent: `5.Nc3`. No non-castling early king move is recorded.

**Your screened critical decision: 17...b6.** 200,000-node recheck: White searched mate in 5 → White searched mate in 3. Pre-move candidate line: `17...b5 18.cxb6 18...Kd6 19.Qxe7+ 19...Kd5`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 9.e3.** 200,000-node recheck: White +7.45 → White -0.55. Pre-move candidate line: `9.Qxe5+ 9...Qe7`.

**Recorded finish:** `18...Kc8 19.Qd8+ 19...Kb7 20.Ne6 20...bxc5 21.Qc7#`. The final position is checkmate.

**Opening record:** `1.d4 1...d5 2.c4 2...f6 3.c5 3...e5 4.dxe5 4...fxe5 5.Nc3 5...d4 6.Ne4 6...Nf6 7.Qc2 7...Nxe4 8.Qxe4 8...g6 9.e3 9...c6 10.exd4 10...Bf5`.

<a id="game-7buj2rvv"></a>

### 16. fchfan — Draw as Black

**2026.11.10 · fchfan–mannyfresher · 1/2-1/2 · 133 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/YNlrJNPi) · [Game](https://lichess.org/game/7BUj2Rvv).

**Queen plan:** first queen move `2...Qd6`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `3.c5` (pawn commitment) → `3...Qg6`; `12.Bxe4` (repeat-piece move) → `12...Nxe4`; `18.Neg5` (repeat-piece move) → `18...Qg4`; `20.Bd2` (minor-piece development) → `20...Qb2`.

**Theory assessment:** 1 developing minor-piece threat(s), 2 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Bf5, 10...Nf6`; opponent: `4.Nc3`. No non-castling early king move is recorded.

**Your screened critical decision: 61...Kh3.** 200,000-node recheck: White +10.56 → White searched mate in 2. Pre-move candidate line: `61...Kg5`.

**Opponent’s screened critical decision: 67.Qf5+.** 200,000-node recheck: White searched mate in 3 → White +0.00. Pre-move candidate line: `67.Kf4 67...g1=Q 68.Qh5+ 68...Kg2 69.Qf3#`.

**Recorded finish:** `64...Kh3 65.Qf5+ 65...Kg3 66.Qg5+ 66...Kh3 67.Qf5+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.d4 1...d5 2.c4 2...Qd6 3.c5 3...Qg6 4.Nc3 4...Bf5 5.f3 5...Bc2 6.Qd2 6...a6 7.e4 7...Bxe4 8.fxe4 8...dxe4 9.Qe2 9...f5 10.g4 10...Nf6`.

<a id="game-pcumbc2n"></a>

### 17. EminBurak2018 — Loss as Black

**2026.11.12 · EminBurak2018–mannyfresher · 1-0 · 61 plies · Normal. [Study chapter](https://lichess.org/study/nErRsOiw/HqWDhHRd) · [Game](https://lichess.org/game/PCUmbC2N).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Bh3, 10...Nd7`; opponent: `2.Nf3, 6.Bxh3`. No non-castling early king move is recorded.

**Your screened critical decision: 27...Rc7.** 200,000-node recheck: White +12.63 → White searched mate in 2. Pre-move candidate line: `27...Rc6 28.Rg8+ 28...Kd7 29.Rxd8+ 29...Bxd8`.

**Opponent’s screened critical decision: 28.Rg8+.** 200,000-node recheck: White searched mate in 2 → White +12.78. Pre-move candidate line: `28.Qe6 28...Rxc3 29.Rg8#`.

**Recorded finish:** `28...Kd7 29.Qd5+ 29...Bd6 30.Rg7+ 30...Kc8 31.Qa8#`. The final position is checkmate.

**Opening record:** `1.d4 1...h5 2.Nf3 2...h4 3.g4 3...hxg3 4.fxg3 4...d5 5.c3 5...Bh3 6.Bxh3 6...Rxh3 7.Qa4+ 7...c6 8.Qb3 8...b5 9.Qa3 9...a5 10.Qc5 10...Nd7`.

<a id="game-i0w1q3ix"></a>

### 18. kusal2022 — Win as White

**2026.11.12 · mannyfresher–kusal2022 · 1-0 · 169 plies · Normal. [Study chapter](https://lichess.org/study/da9uLoen/JLwbFtbu) · [Game](https://lichess.org/game/i0W1q3IX).

Your 2.Qd2 and unusual setup met Black’s queen-and-bishop pressure. 5.e3 Qxe3+ 6.Qxe3 Bxe3 7.Bxe3 left you a bishop ahead for a pawn. That is an opening tactical payoff. The later game was a separate comeback: your first c-pawn eliminated a rook, the second promoted, and after the opponent’s responses you captured both their queens. 85.Qg2# converted the final queen ending. The opening payoff and the eventual win should be credited separately.

**Queen plan:** first queen move `2.Qd2`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `5...Qxe3+` (repeat-piece move; also check) → `6.Qxe3`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4.Nh3, 7.Bxe3, 8.Nc3`; opponent: `3...Bc5, 7...Nf6, 9...Nc6`. No non-castling early king move is recorded.

**Your screened critical decision: 73.Qe1.** 200,000-node recheck: White searched mate in 7 → White searched mate in 5. Pre-move candidate line: `73.Qe2 73...Kg5 74.Ke5 74...Kg6 75.Qf3`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 62...Ke6.** 200,000-node recheck: Black searched mate in 8 → White +55.36. Pre-move candidate line: `62...Qxc7+ 63.Kxc7 63...a1=Q 64.Kb6 64...Qe5`.

**Recorded finish:** `82...Kh2 83.Qg4 83...Kh1 84.Kf2 84...Kh2 85.Qg2#`. The final position is checkmate.

**Opening record:** `1.d3 1...e6 2.Qd2 2...Qf6 3.f3 3...Bc5 4.Nh3 4...Qd4 5.e3 5...Qxe3+ 6.Qxe3 6...Bxe3 7.Bxe3 7...Nf6 8.Nc3 8...O-O 9.O-O-O 9...Nc6 10.d4 10...Re8`.

<a id="game-4182oyps"></a>

### 19. YouddaVonBlbackoff — Loss as Black

**2026.09.09 · YouddaVonBlbackoff–mannyfresher · 1-0 · 89 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/JfbUggCa) · [Game](https://lichess.org/4182Oyps).

**Queen plan:** first queen move `3...Qe8`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Nxc6, 9...Bg4`; opponent: `3.Nc3, 4.Bb5+, 9.Ne2`. Your non-castling early king moves: `2...Kd7, 6...Kd6, 10...Kc5`.

**Your screened critical decision: 11...Nd4.** 200,000-node recheck: White +1.20 → White searched mate in 3. Pre-move candidate line: `11...Bxe2 12.Bxe2`.

**Opponent’s screened critical decision: 44.Rb1+.** 200,000-node recheck: White searched mate in 4 → White +5.40. Pre-move candidate line: `44.Rxa2 44...a5 45.Rb2+ 45...Ka6 46.Qc6+`.

**Recorded finish:** `42...f5 43.Qc3+ 43...Kb5 44.Rb1+ 44...Ka4 45.Qb4#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.exd5 2...Kd7 3.Nc3 3...Qe8 4.Bb5+ 4...c6 5.dxc6+ 5...Nxc6 6.Nd5 6...Kd6 7.Qf3 7...e6 8.Qd3 8...exd5+ 9.Ne2 9...Bg4 10.Qg3+ 10...Kc5`.

<a id="game-poy7vryc"></a>

### 20. Bntimane — Win as Black

**2026.09.28 · Bntimane–mannyfresher · 0-1 · 44 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/jCJfv4yw) · [Game](https://lichess.org/POY7Vryc).

**Queen plan:** first queen move `7...Qh4`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `8.Nf3` (minor-piece development) → `8...Qb4`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Bg4`; opponent: `4.Be2, 5.Nc3, 6.Be3, 8.Nf3`. Your non-castling early king moves: `10...Kd8`.

**Your screened critical decision: 11...Bd6.** 200,000-node recheck: White -10.94 → White -0.76. Pre-move candidate line: `11...Bg6 12.d6`.

**Opponent’s screened critical decision: 22.Bxg7.** 200,000-node recheck: White -13.07 → Black searched mate in 1. Pre-move candidate line: `22.f3 22...Nb3 23.Be5 23...Nxa1 24.h3`.

**Recorded finish:** `20.Kh1 20...Nxc1 21.Bd4 21...Qxc2 22.Bxg7 22...Qd1#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.exd5 2...Bg4 3.d4 3...Bxd1 4.Be2 4...Bxc2 5.Nc3 5...c5 6.Be3 6...e5 7.dxe5 7...Qh4 8.Nf3 8...Qb4 9.O-O 9...Qxb2 10.Nb5 10...Kd8`.

<a id="game-cwgjssen"></a>

### 21. Audvik_Acharya — Win as Black

**2026.10.03 · Audvik_Acharya–mannyfresher · 0-1 · 26 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/uYBFkaJt) · [Game](https://lichess.org/cwGjSsEN).

**Queen plan:** first queen move `7...Qa5`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Bxf5, 6...Nxc6, 8...Bxd6`; opponent: `2.Nc3, 3.Nf3, 5.Bb5+`. No non-castling early king move is recorded.

**Your screened critical decision: 12...Nf6.** 200,000-node recheck: White -16.08 → White -12.33. Pre-move candidate line: `12...Nxc2+`.

**Opponent’s screened critical decision: 6.Bxc6+.** 200,000-node recheck: White -1.23 → White -6.75. Pre-move candidate line: `6.Be2 6...Nd7 7.O-O 7...Bd6 8.d4`.

**Recorded finish:** `11.Qd1 11...Nd4 12.Nh3 12...Nf6 13.g4 13...Bxg4`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.Nc3 2...e5 3.Nf3 3...f5 4.exf5 4...Bxf5 5.Bb5+ 5...c6 6.Bxc6+ 6...Nxc6 7.Nb5 7...Qa5 8.Nd6+ 8...Bxd6 9.Ng5 9...h6 10.Qh5+ 10...g6`.

<a id="game-kzbso2vu"></a>

### 22. Legoboost — Loss as Black

**2026.10.03 · Legoboost–mannyfresher · 1-0 · 85 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/ThPXDbER) · [Game](https://lichess.org/kzbSo2vU).

**Queen plan:** first queen move `12...Qe7`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `14.a3` (pawn commitment) → `14...Qa5`; `16.b4` (pawn commitment) → `16...Qa6`; `19.Nxc5+` (repeat-piece move; also check) → `19...Kc6`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `6...Bd7, 7...Nc6, 8...Bb4+`; opponent: `8.Bb5`. Your non-castling early king moves: `10...Kxd7`.

**Your screened critical decision: 39...Kb4.** 200,000-node recheck: White +18.76 → White searched mate in 3. Pre-move candidate line: `39...Ka4 40.Nd5 40...a5 41.Rb1 41...Rb3`.

**Opponent’s screened critical decision: 37.Bd4+.** 200,000-node recheck: White searched mate in 5 → White +17.76. Pre-move candidate line: `37.Rd6+ 37...Kb7 38.Rd7+ 38...Ka6 39.Rc6+`.

**Recorded finish:** `40...Ka4 41.Rc4+ 41...Ka5 42.Bc3+ 42...Ka6 43.Rc6#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.Qf3 2...dxe4 3.Qf4 3...e3 4.dxe3 4...e5 5.Qa4+ 5...b5 6.Qxb5+ 6...Bd7 7.Qb7 7...Nc6 8.Bb5 8...Bb4+ 9.c3 9...Na5 10.Bxd7+ 10...Kxd7`.

<a id="game-ep2vxhec"></a>

### 23. MOREbming498 — Win as Black

**2026.10.05 · MOREbming498–mannyfresher · 0-1 · 50 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/30nRNN6I) · [Game](https://lichess.org/Ep2VxHEC).

**Queen plan:** first queen move `14...Qxd5`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Bg4, 7...Nc6`; opponent: `2.Nc3, 4.Bxd3, 5.Nf3`. No non-castling early king move is recorded.

**Your screened critical decision: 21...Qf2+.** 200,000-node recheck: Black searched mate in 1 → White +0.00. Pre-move candidate line: `21...Rf1#`.

**Opponent’s screened critical decision: 21.Bh3.** 200,000-node recheck: White +10.73 → Black searched mate in 1. Pre-move candidate line: `21.Rf3 21...Qxf3 22.Qxf3 22...Rxf3 23.Bxg8`.

**Recorded finish:** `23.Ke2 23...Qf2+ 24.Kd1 24...Qg1+ 25.Bf1 25...Qxf1#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.Nc3 2...d4 3.Nd5 3...d3 4.Bxd3 4...h5 5.Nf3 5...Bg4 6.h3 6...Be6 7.Ne5 7...Nc6 8.f4 8...Nd4 9.g4 9...f6 10.gxh5 10...fxe5`.

<a id="game-e9dop6g7"></a>

### 24. Carpena1980 — Loss as Black

**2026.10.05 · Carpena1980–mannyfresher · 1-0 · 93 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/4bnTbmNa) · [Game](https://lichess.org/e9dop6g7).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Nc6, 3...Nf6`; opponent: `5.Nf3, 6.Be2`. Your non-castling early king moves: `9...Kxd8, 10...Ke8`.

**Your screened critical decision: 14...Rd8.** 200,000-node recheck: White +8.58 → White searched mate in 1. Pre-move candidate line: `14...Nxc3`.

**Opponent’s screened critical decision: 15.Be3.** 200,000-node recheck: White searched mate in 1 → White +8.53. Pre-move candidate line: `15.Bxf7#`.

**Recorded finish:** `44...b3 45.Re2 45...b2 46.Qc3+ 46...Ka2 47.Qxb2#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.Qh5 2...Nc6 3.d3 3...Nf6 4.Qd1 4...g6 5.Nf3 5...h5 6.Be2 6...dxe4 7.dxe4 7...Ne5 8.Nxe5 8...Nxe4 9.Qxd8+ 9...Kxd8 10.O-O 10...Ke8`.

<a id="game-jhxeruto"></a>

### 25. Ahmedadilzumrawi — Draw as Black

**2026.10.06 · Ahmedadilzumrawi–mannyfresher · 1/2-1/2 · 83 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/jp5QW8xt) · [Game](https://lichess.org/JhxEruTO).

**Queen plan:** first queen move `2...Qxd5`; 6 queen moves in the first ten recorded full moves, 3 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `3.Nc3` (minor-piece development) → `3...Qd4`; `4.Nf3` (minor-piece development) → `4...Qf4`; `5.d3` (pawn commitment) → `5...Qf6`; `9.Ng5` (repeat-piece move) → `9...Qxe2+`.

**Theory assessment:** 2 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `6...Bg4, 8...Nc6`; opponent: `3.Nc3, 4.Nf3, 7.Bg2`. No non-castling early king move is recorded.

**Your screened critical decision: 21...g5.** 200,000-node recheck: White +12.75 → White +19.79. Pre-move candidate line: `21...gxf6 22.Kxf6`.

**Opponent’s screened critical decision: 42.Qh4.** 200,000-node recheck: White searched mate in 1 → terminal outcome. Pre-move candidate line: `42.Qf4#`.

**Recorded finish:** `39...Kd2 40.Qxb4+ 40...Ke3 41.Rhe1+ 41...Kf2 42.Qh4`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.exd5 2...Qxd5 3.Nc3 3...Qd4 4.Nf3 4...Qf4 5.d3 5...Qf6 6.g3 6...Bg4 7.Bg2 7...Qe6+ 8.Ne2 8...Nc6 9.Ng5 9...Qxe2+ 10.Qxe2 10...Bxe2`.

<a id="game-2njxcpya"></a>

### 26. No_More_Bans_Pls — Win as Black

**2026.10.08 · No_More_Bans_Pls–mannyfresher · 0-1 · 22 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/DF5ruzYx) · [Game](https://lichess.org/2nJxcpYA).

A mixed but instructive test. 3.Nc3 and 4.Nf3 developed fresh knights with threats against your queen, so those were productive development tempi. Later, 10.Nd5 attacked the queen on f6 but allowed 10…Qxa1. The deeper check confirms a major tactical concession there. The practical lesson is to distinguish sound developing threats from a later overextension.

**Queen plan:** first queen move `2...Qxd5`; 4 queen moves in the first ten recorded full moves, 2 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `3.Nc3` (minor-piece development) → `3...Qd4`; `4.Nf3` (minor-piece development) → `4...Qf6`; `10.Nd5` (repeat-piece move) → `10...Qxa1`.

**Theory assessment:** 2 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `none recorded`; opponent: `3.Nc3, 4.Nf3`. No non-castling early king move is recorded.

**Your screened critical decision: 9...Rf5.** 200,000-node recheck: White -4.13 → White +2.85. Pre-move candidate line: `9...Qxc3+ 10.Bd2`.

**Opponent’s screened critical decision: 10.Nd5.** 200,000-node recheck: White +2.78 → White -4.67. Pre-move candidate line: `10.Bb2`.

**Recorded finish:** `9.b4 9...Rf5 10.Nd5 10...Qxa1 11.Nc7+ 11...Kd8`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.exd5 2...Qxd5 3.Nc3 3...Qd4 4.Nf3 4...Qf6 5.d4 5...a5 6.d5 6...a4 7.d6 7...cxd6 8.a3 8...Ra5 9.b4 9...Rf5 10.Nd5 10...Qxa1`.

<a id="game-zinjzlzm"></a>

### 27. sonsnare — Loss as Black

**2026.10.15 · sonsnare–mannyfresher · 1-0 · 99 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/rwt9tgbC) · [Game](https://lichess.org/ziNJzlZm).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nd7, 4...Ngf6, 7...Bh6`; opponent: `4.Bc4, 5.Nc3, 6.Nf3, 9.Bxg5`. No non-castling early king move is recorded.

**Your screened critical decision: 14...Nxb2.** 200,000-node recheck: White -4.24 → White +8.03. Pre-move candidate line: `14...exf6`.

**Opponent’s screened critical decision: 14.Bxf6.** 200,000-node recheck: White +5.44 → White -4.10. Pre-move candidate line: `14.Nxf6 14...Nb6`.

**Recorded finish:** `47...Kf6 48.Qcc6+ 48...Ke7 49.Qdd7+ 49...Kf8 50.Qcc8#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.d3 2...dxe4 3.dxe4 3...Nd7 4.Bc4 4...Ngf6 5.Nc3 5...g6 6.Nf3 6...h5 7.O-O 7...Bh6 8.Ng5 8...Bxg5 9.Bxg5 9...h4 10.h3 10...Ne5`.

<a id="game-yez6ujvf"></a>

### 28. dragonakm — Win as Black

**2026.10.15 · dragonakm–mannyfresher · 0-1 · 58 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/w9J9Iuxp) · [Game](https://lichess.org/Yez6uJVF).

**Queen plan:** first queen move `13...Qxc8`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Ne7, 10...Bb7`; opponent: `10.Bb2`. No non-castling early king move is recorded.

**Your screened critical decision: 22...Qa1+.** 200,000-node recheck: Black searched mate in 1 → White -13.64. Pre-move candidate line: `22...Qf2#`.

**Opponent’s screened critical decision: 22.Ngf3.** 200,000-node recheck: White -12.84 → Black searched mate in 1. Pre-move candidate line: `22.Ke1 22...dxc4`.

**Recorded finish:** `27.d6 27...Rae8 28.Bxb5 28...Bxe1 29.Nxe1 29...Qxe1#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.Qh5 2...e6 3.exd5 3...exd5 4.Qe5+ 4...Ne7 5.d3 5...f6 6.Qg3 6...g5 7.Qf3 7...c5 8.Qh5+ 8...Ng6 9.b3 9...b5 10.Bb2 10...Bb7`.

<a id="game-p1aryfx7"></a>

### 29. geogektor291 — Win as Black

**2026.10.22 · geogektor291–mannyfresher · 0-1 · 36 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/F8N0EcWp) · [Game](https://lichess.org/game/P1ARyfX7).

**Queen plan:** first queen move `4...Qd7`; 3 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nxc6, 9...Be7, 10...Nf6`; opponent: `4.Nc3, 6.Bb2, 8.Bc4`. No non-castling early king move is recorded.

**Your screened critical decision: 12...Bd7.** 200,000-node recheck: White +1.65 → White +6.77. Pre-move candidate line: `12...e5 13.Nc3 13...Bf5 14.Nd5 14...Nxd5`.

**Opponent’s screened critical decision: 18.c3.** 200,000-node recheck: White +6.56 → Black searched mate in 1. Pre-move candidate line: `18.Qb2`.

**Recorded finish:** `16.Re3 16...Qxa2 17.Re4 17...Nb4 18.c3 18...Qc2#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.exd5 2...c6 3.dxc6 3...Nxc6 4.Nc3 4...Qd7 5.b3 5...Qc7 6.Bb2 6...Qb8 7.Qf3 7...e6 8.Bc4 8...g6 9.O-O-O 9...Be7 10.Re1 10...Nf6`.

<a id="game-rico4abd"></a>

### 30. clavenera — Loss as Black

**2026.11.01 · clavenera–mannyfresher · 1-0 · 67 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/hzcJ6F21) · [Game](https://lichess.org/game/RICo4AbD).

**Queen plan:** first queen move `9...Qb6`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `10.Na4` (repeat-piece move) → `10...Qb4+`; `16.a3` (pawn commitment) → `16...Nf5`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nxc6, 4...Bg4, 8...Bc5`; opponent: `4.Nf3, 8.Nc3, 9.Be3`. No non-castling early king move is recorded.

**Your screened critical decision: 21...f6.** 200,000-node recheck: White +12.01 → White searched mate in 3. Pre-move candidate line: `21...h5`.

**Opponent’s screened critical decision: 22.Qxb7.** 200,000-node recheck: White searched mate in 3 → White searched mate in 6. Pre-move candidate line: `22.Qd5+ 22...Rf7 23.Qd8+ 23...Rf8 24.Bc4#`. The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.

**Recorded finish:** `31...Kh4 32.g3+ 32...Kh3 33.Rf2 33...f4 34.Rh2#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.exd5 2...c6 3.dxc6 3...Nxc6 4.Nf3 4...Bg4 5.d4 5...Bxf3 6.Qxf3 6...Nxd4 7.Qd3 7...e5 8.Nc3 8...Bc5 9.Be3 9...Qb6 10.Na4 10...Qb4+`.

<a id="game-ixhlee7j"></a>

### 31. Succot — Loss as Black

**2026.11.01 · Succot–mannyfresher · 1-0 · 69 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/5nLiZH4K) · [Game](https://lichess.org/game/iXhLee7j).

**Queen plan:** first queen move `2...Qxd5`; 4 queen moves in the first ten recorded full moves, 2 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `3.Nc3` (minor-piece development) → `3...Qd4`; `4.Nf3` (minor-piece development) → `4...Qf6`; `19.Ne4+` (repeat-piece move; also check) → `19...Qxe4`.

**Theory assessment:** 2 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Bg4, 8...Nf6, 9...Nc6`; opponent: `3.Nc3, 4.Nf3, 6.Be2, 8.Be3`. No non-castling early king move is recorded.

**Your screened critical decision: 34...f5.** 200,000-node recheck: White +58.31 → White searched mate in 1. Pre-move candidate line: `34...h4 35.gxh4`.

**Opponent’s screened critical decision: 14.Bf3.** 200,000-node recheck: White searched mate in 4 → White +12.12. Pre-move candidate line: `14.O-O-O+ 14...Qd6 15.Qxa7 15...Kc8 16.Qb7+`.

**Recorded finish:** `32...h5 33.g3+ 33...Kg4 34.Kg2 34...f5 35.h3#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.exd5 2...Qxd5 3.Nc3 3...Qd4 4.Nf3 4...Qf6 5.d4 5...Bg4 6.Be2 6...Bxf3 7.Bxf3 7...Qe6+ 8.Be3 8...Nf6 9.Bxb7 9...Nc6 10.Bxa8 10...Nxd4`.

<a id="game-vc5mszys"></a>

### 32. tucz1n — Win as Black

**2026.11.01 · tucz1n–mannyfresher · 0-1 · 26 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/skhS7jNc) · [Game](https://lichess.org/game/VC5MszyS).

**Queen plan:** first queen move `6...Qxd4`; 3 queen moves in the first ten recorded full moves, 3 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `9.Be3` (minor-piece development) → `9...Qxb2`; `11.Bd4` (repeat-piece move) → `11...Qxd4+`.

**Theory assessment:** 1 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Bg4, 8...Nf6`; opponent: `4.Nxf3, 7.Bb5+, 9.Be3`. No non-castling early king move is recorded.

**Your screened critical decision: 6...Qxd4.** 200,000-node recheck: White -0.10 → White +7.90. Pre-move candidate line: `6...c6 7.Be3`.

**Opponent’s screened critical decision: 13.Qb3.** 200,000-node recheck: White -13.61 → White -25.53. Pre-move candidate line: `13.Qxf7+ 13...Kd8 14.Qf4 14...e5 15.c3`.

**Recorded finish:** `11.Bd4 11...Qxd4+ 12.Rf2 12...Ne4 13.Qb3 13...Qxf2+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.f3 2...dxe4 3.d4 3...exf3 4.Nxf3 4...Bg4 5.h3 5...Bxf3 6.Qxf3 6...Qxd4 7.Bb5+ 7...c6 8.Be2 8...Nf6 9.Be3 9...Qxb2 10.O-O 10...Qxa1`.

<a id="game-cjaubag5"></a>

### 33. Aarkom — Win as Black

**2026.11.02 · Aarkom–mannyfresher · 0-1 · 52 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/5HVlZPFo) · [Game](https://lichess.org/game/cjAUBAG5).

**Queen plan:** first queen move `2...Qxd5`; 5 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `3.Nc3` (minor-piece development) → `3...Qd4`; `4.Nce2` (repeat-piece move) → `4...Qe4`; `5.d3` (pawn commitment) → `5...Qe5`; `6.d4` (pawn commitment) → `6...Qe4`; `12.Qxc2` (other piece move) → `12...Qxc2`; `13.Nd4` (repeat-piece move) → `13...Qe4+`; `16.Rb1` (other piece move) → `16...Qe6`.

**Theory assessment:** 1 developing minor-piece threat(s), 2 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `7...Bf5, 8...Nd7`; opponent: `3.Nc3`. No non-castling early king move is recorded.

**Your screened critical decision: 16...Qe6.** 200,000-node recheck: White -21.09 → White -11.88. Pre-move candidate line: `16...Qxb1`.

**Opponent’s screened critical decision: 25.g4.** 200,000-node recheck: Black searched mate in 7 → Black searched mate in 4. Pre-move candidate line: `25.Kg3 25...Ngf6 26.h4 26...Qe4 27.h5`. The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.

**Recorded finish:** `24.f4 24...Qf5 25.g4 25...Qxf4+ 26.Kg1 26...e5`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.exd5 2...Qxd5 3.Nc3 3...Qd4 4.Nce2 4...Qe4 5.d3 5...Qe5 6.d4 6...Qe4 7.d5 7...Bf5 8.d6 8...Nd7 9.dxc7 9...Rc8 10.b4 10...Rxc7`.

<a id="game-pe8ocqij"></a>

### 34. bujurest — Win as Black

**2026.11.02 · bujurest–mannyfresher · 0-1 · 82 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/SxobnIT4) · [Game](https://lichess.org/game/Pe8OcQiJ).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Nc6, 3...Be6, 10...Nf6`; opponent: `5.Bb5, 8.Nf3, 9.Nc3`. No non-castling early king move is recorded.

**Your screened critical decision: 38...Rf3.** 200,000-node recheck: Black searched mate in 5 → White -66.84. Pre-move candidate line: `38...Bf3 39.Rxf3+ 39...Rxf3 40.a3 40...h3`.

**Opponent’s screened critical decision: 37.b4.** 200,000-node recheck: White -11.02 → Black searched mate in 7. Pre-move candidate line: `37.b4 37...Rg2+`.

**Recorded finish:** `39.Rxf3+ 39...Bxf3 40.a4 40...h3 41.b5 41...h2+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.Qh5 2...Nc6 3.Qxd5 3...Be6 4.Qxd8+ 4...Rxd8 5.Bb5 5...Rd6 6.e5 6...Rd5 7.Bxc6+ 7...bxc6 8.Nf3 8...Bg4 9.Nc3 9...Rc5 10.e6 10...Nf6`.

<a id="game-g3j5eh39"></a>

### 35. olk — Draw as Black

**2026.11.07 · olk–mannyfresher · 1/2-1/2 · 53 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/2vQTrkgq) · [Game](https://lichess.org/game/g3J5EH39).

**Queen plan:** first queen move `9...Qxd3`; 1 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `8...Bh3`; opponent: `2.Nc3, 5.Bxd3, 7.Nf3`. No non-castling early king move is recorded.

**Your screened critical decision: 19...Kc2.** 200,000-node recheck: White +41.44 → White searched mate in 2. Pre-move candidate line: `19...f6 20.Qxc7`.

**Opponent’s screened critical decision: 27.Qxf3.** 200,000-node recheck: White searched mate in 2 → terminal outcome. Pre-move candidate line: `27.Kxf3 27...Kd3 28.Qc4#`.

**Recorded finish:** `24...Bf3 25.Qf7 25...Be4 26.Ke2 26...Bf3+ 27.Qxf3`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d5 2.Nc3 2...d4 3.Nce2 3...d3 4.Ng3 4...h5 5.Bxd3 5...h4 6.Nf1 6...h3 7.Nf3 7...hxg2 8.Rg1 8...Bh3 9.Ng3 9...Qxd3 10.cxd3 10...e5`.

<a id="game-uyo057a7"></a>

### 36. carla227 — Win as Black

**2026.11.11 · carla227–mannyfresher · 0-1 · 40 plies · Normal. [Study chapter](https://lichess.org/study/2nJl10wd/YIqsmqAS) · [Game](https://lichess.org/game/UYo057a7).

**Queen plan:** first queen move `13...Qxd4`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `17.Bxf6` (repeat-piece move) → `17...gxf6`; `18.Qxf6+` (repeat-piece move; also check) → `18...Qxf6`.

**Theory assessment:** 0 developing minor-piece threat(s), 2 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Bg4, 7...Nxf6, 8...Bd6, 9...Nc6`; opponent: `4.Nf3, 5.Be2, 8.Bg5`. No non-castling early king move is recorded.

**Your screened critical decision: 19...Qxf2.** 200,000-node recheck: Black searched mate in 3 → White -8.27. Pre-move candidate line: `19...Qh4+ 20.Kg1 20...Qxf2+ 21.Kh1 21...Qxg2#`.

**Opponent’s screened critical decision: 19.Rfd1.** 200,000-node recheck: White -7.54 → Black searched mate in 3. Pre-move candidate line: `19.Ne4 19...Qf4+`.

**Recorded finish:** `18.Qxf6+ 18...Qxf6 19.Rfd1 19...Qxf2 20.Rac1 20...Qxg2#`. The final position is checkmate.

**Opening record:** `1.e4 1...d5 2.e5 2...d4 3.d3 3...h5 4.Nf3 4...Bg4 5.Be2 5...e6 6.O-O 6...f6 7.exf6 7...Nxf6 8.Bg5 8...Bd6 9.c3 9...Nc6 10.cxd4 10...Nxd4`.

<a id="game-rpqjpm8k"></a>

### 37. LeaderAswa — Loss as Black

**2026.09.09 · LeaderAswa–mannyfresher · 1-0 · 61 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/U2WQabYo) · [Game](https://lichess.org/RPqJPm8K).

**Queen plan:** first queen move `2...Qd7`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `7.Bxd7` (repeat-piece move) → `7...Qxd7`; `14.cxb4` (pawn commitment) → `14...Qxb4+`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Nd7, 8...Ne7`; opponent: `2.Nf3, 3.Nc3, 5.Bf4, 6.Bb5`. Your non-castling early king moves: `3...Kd8, 10...Ke8`.

**Your screened critical decision: 27...Kxa6.** 200,000-node recheck: White +11.02 → White searched mate in 5. Pre-move candidate line: `27...Rxc7 28.d8=Q`.

**Opponent’s screened critical decision: 22.Rxc8.** 200,000-node recheck: White +15.37 → White +11.04. Pre-move candidate line: `22.d6+ 22...Kd7 23.Ne5+ 23...Kxd6 24.Nxf7+`.

**Recorded finish:** `28...Kb5 29.Qb7+ 29...Kc5 30.c8=Q+ 30...Kd6 31.Qbd7#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.Nf3 2...Qd7 3.Nc3 3...Kd8 4.d4 4...Qe8 5.Bf4 5...Nd7 6.Bb5 6...e6 7.Bxd7 7...Qxd7 8.e5 8...Ne7 9.exd6 9...Nd5 10.dxc7+ 10...Ke8`.

<a id="game-beu6bd9w"></a>

### 38. Posseidon1977 — Loss as Black

**2026.09.10 · Posseidon1977–mannyfresher · 1-0 · 37 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/sb7Gu17i) · [Game](https://lichess.org/bEU6Bd9W).

**Queen plan:** first queen move `2...Qd7`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Nd7, 7...Ne7`; opponent: `4.Nc3, 5.Bd2, 6.Bd3, 7.Nge2`. Your non-castling early king moves: `3...Kd8`.

**Your screened critical decision: 18...Kd6.** 200,000-node recheck: White +8.84 → White searched mate in 1. Pre-move candidate line: `18...Kc8 19.Bb3`.

**Opponent’s screened critical decision: 12.Bc4.** 200,000-node recheck: White +10.61 → White +7.79. Pre-move candidate line: `12.exf7`.

**Recorded finish:** `16...Qxf7 17.Ne6+ 17...Kd7 18.Nc5+ 18...Kd6 19.Bf4#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.f3 2...Qd7 3.d4 3...Kd8 4.Nc3 4...Qe8 5.Bd2 5...Nd7 6.Bd3 6...e6 7.Nge2 7...Ne7 8.O-O 8...h6 9.f4 9...a6 10.f5 10...g6`.

<a id="game-cxjnygro"></a>

### 39. GreyWizard-108 — Loss as Black

**2026.09.10 · GreyWizard-108–mannyfresher · 1-0 · 43 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/tziqO3c1) · [Game](https://lichess.org/cXjNygRo).

**Queen plan:** first queen move `2...Qd7`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `18.e8=Q+` (pawn commitment; also check) → `18...Qxe8`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `7...Bxe6, 10...Nf6`; opponent: `5.Nf3, 6.Bd3, 9.Nc3`. Your non-castling early king moves: `3...Kd8`.

**Your screened critical decision: 17...Kc6.** 200,000-node recheck: White +14.99 → White searched mate in 5. Pre-move candidate line: `17...Nc6 18.Rxg6`.

**Opponent’s screened critical decision: 20.h3.** 200,000-node recheck: White searched mate in 3 → White +22.70. Pre-move candidate line: `20.b4+ 20...Kc6 21.Nd4+ 21...Kd7 22.Qe6#`.

**Recorded finish:** `19...Kc5 20.h3 20...c6 21.hxg4 21...hxg4 22.Qe3#`. The final position is checkmate.

**Opening record:** `1.d4 1...d6 2.e4 2...Qd7 3.d5 3...Kd8 4.c4 4...Qe8 5.Nf3 5...h5 6.Bd3 6...e5 7.dxe6 7...Bxe6 8.O-O 8...g6 9.Nc3 9...f5 10.exf5 10...Nf6`.

<a id="game-4u6hwgxw"></a>

### 40. Skn_wittur — Loss as Black

**2026.09.10 · Skn_wittur–mannyfresher · 1-0 · 53 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/YhQJkSnz) · [Game](https://lichess.org/4u6HwGxw).

**Queen plan:** first queen move `2...Qd7`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `6...Nc6, 7...Nh6`; opponent: `3.Bc4, 6.Nc3, 7.Nge2`. Your non-castling early king moves: `3...Kd8`.

**Your screened critical decision: 22...Qh4.** 200,000-node recheck: White +12.86 → White searched mate in 4. Pre-move candidate line: `22...Qxa7 23.Qxa7 23...Rf6 24.Qb8 24...Rf7`.

**Opponent’s screened critical decision: 16.Nb5.** 200,000-node recheck: White -2.68 → White -7.89. Pre-move candidate line: `16.Rae1 16...Rf8 17.Nf4 17...Qd6 18.Ne4`.

**Recorded finish:** `24...Kd8 25.Qd6+ 25...Ke8 26.Re1+ 26...Qe7 27.Rexe7#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.Qf3 2...Qd7 3.Bc4 3...Kd8 4.h3 4...e6 5.d3 5...f6 6.Nc3 6...Nc6 7.Nge2 7...Nh6 8.O-O 8...f5 9.exf5 9...Nxf5 10.a3 10...g6`.

<a id="game-475976ig"></a>

### 41. hopydopy — Win as Black

**2026.09.26 · hopydopy–mannyfresher · 0-1 · 38 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/lHlqOGGd) · [Game](https://lichess.org/475976ig).

A queen-to-queen confrontation rather than simply a development race. After …Qg4 and …Qxg2, White tried 8.Qf3 and 9.Qg2. Your 9…Qxg2 won their queen. This supports readiness to exploit a mistaken attack; it does not by itself show that you induced underestimation.

**Queen plan:** first queen move `2...Qd7`; 6 queen moves in the first ten recorded full moves, 3 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `8.Qf3` (repeat-piece move) → `8...Qg4`; `9.Qg2` (repeat-piece move) → `9...Qxg2`; `13.Bd3` (repeat-piece move) → `13...Qb4+`; `14.c3` (pawn commitment) → `14...Qg4`.

**Theory assessment:** 0 developing minor-piece threat(s), 3 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Nf6`; opponent: `3.Bc4, 6.Nc3, 10.Nge2`. No non-castling early king move is recorded.

**Your screened critical decision: 5...e5.** 200,000-node recheck: White -0.18 → White +0.95. Pre-move candidate line: `5...exd5 6.Bxd5 6...Nxd5 7.exd5 7...Be7`.

**Opponent’s screened critical decision: 9.Qg2.** 200,000-node recheck: White -1.28 → White -18.89. Pre-move candidate line: `9.Be3 9...Qxf3 10.Nxf3 10...a6 11.a4`.

**Recorded finish:** `17.Bxc6+ 17...Nxc6 18.b4 18...Ba6 19.b5 19...Bxb5`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.Qf3 2...Qd7 3.Bc4 3...e6 4.d4 4...Nf6 5.d5 5...e5 6.Nc3 6...Qg4 7.Qd3 7...Qxg2 8.Qf3 8...Qg4 9.Qg2 9...Qxg2 10.Nge2 10...Qxh1+`.

<a id="game-yljckpxi"></a>

### 42. Azsch — Loss as Black

**2026.09.26 · Azsch–mannyfresher · 1-0 · 81 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/fB8YsmfB) · [Game](https://lichess.org/YLjcKPXi).

**Queen plan:** first queen move `15...Qh4`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19.Bg5` (repeat-piece move) → `19...Re3+`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Bg4, 6...Nc6`; opponent: `2.Nc3, 3.Nf3, 9.Bd3`. No non-castling early king move is recorded.

**Your screened critical decision: 35...Qxc7.** 200,000-node recheck: White searched mate in 5 → White searched mate in 5. Pre-move candidate line: `35...Qxc7 36.bxc7 36...Kxc7 37.Bh3 37...Kc6`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 35.Rc7+.** 200,000-node recheck: White searched mate in 1 → White searched mate in 6. Pre-move candidate line: `35.Qc8#`. The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.

**Recorded finish:** `38...a6 39.Qxe5 39...Kb7 40.Bd8 40...Kc6 41.Qd5#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.Nc3 2...h5 3.Nf3 3...Bg4 4.h3 4...Bxf3 5.gxf3 5...e5 6.Nd5 6...Nc6 7.c4 7...Nd4 8.Rg1 8...g6 9.Bd3 9...g5 10.b3 10...g4`.

<a id="game-tac6rghc"></a>

### 43. A-Roy2025 — Win as Black

**2026.09.27 · A-Roy2025–mannyfresher · 0-1 · 52 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/VNvrJfzC) · [Game](https://lichess.org/TaC6RghC).

White’s 7.Bg5 developed a bishop while threatening your queen. The later 9.Nh4 moved an already-active knight to attack the queen on f5. Your 9…Qxg5 10.Qxg5 fxg5 traded queens and removed White’s bishop. The distinction between a sound first developing threat and an exploitable follow-up is central to your thesis.

**Queen plan:** first queen move `6...Qf6`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `7.Bg5` (minor-piece development) → `7...Qf5`; `9.Nh4` (repeat-piece move) → `9...Qxg5`.

**Theory assessment:** 1 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Nd7`; opponent: `2.Bc4, 3.Nf3, 4.Nc3, 7.Bg5`. No non-castling early king move is recorded.

**Your screened critical decision: 6...Qf6.** 200,000-node recheck: White +2.50 → White +6.94. Pre-move candidate line: `6...Bd6`.

**Opponent’s screened critical decision: 9.Nh4.** 200,000-node recheck: White +3.14 → White -5.34. Pre-move candidate line: `9.Be3 9...Bb4 10.a3 10...Bxc3 11.Qxc3`.

**Recorded finish:** `24.bxc4 24...Rxc4+ 25.Kb3 25...Nb6 26.Rb5 26...O-O`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.Bc4 2...Nd7 3.Nf3 3...e6 4.Nc3 4...d5 5.exd5 5...e5 6.d3 6...Qf6 7.Bg5 7...Qf5 8.Qd2 8...f6 9.Nh4 9...Qxg5 10.Qxg5 10...fxg5`.

<a id="game-6batodha"></a>

### 44. Ishanth14 — Draw as Black

**2026.09.28 · Ishanth14–mannyfresher · 1/2-1/2 · 99 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/GkZZ3GMP) · [Game](https://lichess.org/6BAtOdha).

**Queen plan:** first queen move `2...Qd7`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `11.c3` (pawn commitment) → `11...Nd3+`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4...Nc6, 9...Bxd6`; opponent: `7.Bg5+, 10.Nf3`. Your non-castling early king moves: `3...Kd8, 6...Kxe7, 8...Ke6`.

**Your screened critical decision: 42...gxf3.** 200,000-node recheck: White +15.88 → White +63.75. Pre-move candidate line: `42...Kd3 43.Rg6`.

**Opponent’s screened critical decision: 50.Qf2.** 200,000-node recheck: White searched mate in 2 → terminal outcome. Pre-move candidate line: `50.Ke2+ 50...Kxh2 51.Qh6#`.

**Recorded finish:** `47...a5 48.f7 48...a4 49.f8=Q 49...a3 50.Qf2`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.d4 2...Qd7 3.e5 3...Kd8 4.exd6 4...Nc6 5.d5 5...Ne5 6.dxe7+ 6...Kxe7 7.Bg5+ 7...f6 8.d6+ 8...Ke6 9.Bc1 9...Bxd6 10.Nf3 10...Bb4+`.

<a id="game-nupgahtz"></a>

### 45. DmitriySvr — Win as Black

**2026.09.30 · DmitriySvr–mannyfresher · 0-1 · 74 plies · Time forfeit. [Study chapter](https://lichess.org/study/QLTafcOT/6uE67M6i) · [Game](https://lichess.org/NupgaHtz).

**Queen plan:** first queen move `4...Qd4`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `7.Bd2` (minor-piece development) → `7...Bxf2+`; `8.Nxf2` (repeat-piece move) → `8...Qc5`; `12.Bb4` (repeat-piece move) → `12...Qd4`; `13.c3` (pawn commitment) → `13...Qe3`; `14.Qd2` (other piece move) → `14...Qg3`; `15.Nh1` (repeat-piece move) → `15...Qh4`; `16.Qf2` (repeat-piece move) → `16...f5`.

**Theory assessment:** 1 developing minor-piece threat(s), 4 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Bc5`; opponent: `2.Bc4, 6.Nh3, 7.Bd2`. No non-castling early king move is recorded.

**Your screened critical decision: 21...Nc6.** 200,000-node recheck: White +11.87 → White +21.41. Pre-move candidate line: `21...Nd7 22.Ng5`.

**Opponent’s screened critical decision: 22.Re1.** 200,000-node recheck: White +21.77 → White +11.46. Pre-move candidate line: `22.Rf8+ 22...Kd7 23.Rxa8 23...Nce7 24.Bxe7`.

**Recorded finish:** `35.Na4 35...bxa3 36.bxa3 36...Rxa3 37.Nxc5 37...a4`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.Bc4 2...d5 3.Bxd5 3...e6 4.Bb3 4...Qd4 5.d3 5...Bc5 6.Nh3 6...Qb4+ 7.Bd2 7...Bxf2+ 8.Nxf2 8...Qc5 9.O-O 9...h5 10.h3 10...f6`.

<a id="game-rmma0ygw"></a>

### 46. trostyanko-13 — Win as Black

**2026.09.30 · trostyanko-13–mannyfresher · 0-1 · 52 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/5DJOGmw5) · [Game](https://lichess.org/rmMa0yGW).

**Queen plan:** first queen move `18...Qg5`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `6...Be7, 7...Nc6, 8...Bd7`; opponent: `2.Nc3, 4.Bd3, 5.Be3, 6.Nf3`. No non-castling early king move is recorded.

**Your screened critical decision: 22...Qd2.** 200,000-node recheck: White +0.06 → White searched mate in 5. Pre-move candidate line: `22...Qxg3+ 23.hxg3 23...Nxd4 24.Rf4 24...h2+`.

**Opponent’s screened critical decision: 24.Bb5.** 200,000-node recheck: White searched mate in 4 → Black searched mate in 1. Pre-move candidate line: `24.Rxe6+ 24...Kxe6 25.Bc4+ 25...Ke7 26.Rf7+`.

**Recorded finish:** `24.Bb5 24...Nf6 25.Qxb7 25...Rg8+ 26.Kh1 26...Qg2#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.Nc3 2...e6 3.d4 3...f6 4.Bd3 4...g5 5.Be3 5...h5 6.Nf3 6...Be7 7.O-O 7...Nc6 8.Qd2 8...Bd7 9.a3 9...g4 10.Nh4 10...f5`.

<a id="game-uwikaxdf"></a>

### 47. Ttedv — Win as Black

**2026.10.01 · Ttedv–mannyfresher · 0-1 · 106 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/WSIKeZn0) · [Game](https://lichess.org/uwIkaXdf).

**Queen plan:** first queen move `18...Qxa8`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19.Qa3` (repeat-piece move) → `19...Qd8`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `9...Bg4`; opponent: `2.Nf3, 4.Bb5+, 10.Nbd2`. No non-castling early king move is recorded.

**Your screened critical decision: 20...Ke7.** 200,000-node recheck: White +8.38 → White +20.30. Pre-move candidate line: `20...Bxc5 21.Qa8`.

**Opponent’s screened critical decision: 51.Rd5+.** 200,000-node recheck: White -0.03 → Black searched mate in 12. Pre-move candidate line: `51.Rf3+ 51...Ke4 52.Rxf6 52...Ke3 53.Re6+`.

**Recorded finish:** `51.Rd5+ 51...Ke3 52.h5 52...Rc1+ 53.Rd1 53...exd1=Q#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.Nf3 2...a5 3.d4 3...a4 4.Bb5+ 4...c6 5.Bd3 5...b5 6.c4 6...b4 7.b3 7...axb3 8.Qxb3 8...c5 9.a3 9...Bg4 10.Nbd2 10...e6`.

<a id="game-bjzsfoag"></a>

### 48. Raymond_Juma — Win as Black

**2026.10.15 · Raymond_Juma–mannyfresher · 0-1 · 60 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/RRstcV0k) · [Game](https://lichess.org/BJzsFoag).

**Queen plan:** first queen move `2...Qd7`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `6.Nxe5` (repeat-piece move) → `6...dxe5`; `7.Bb5` (minor-piece development) → `7...c6`; `8.dxc6` (pawn commitment) → `8...bxc6`.

**Theory assessment:** 1 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nf6, 4...Nc6, 9...Bxd7`; opponent: `3.Nf3, 4.Nc3, 7.Bb5`. No non-castling early king move is recorded.

**Your screened critical decision: 12...Nxf2.** 200,000-node recheck: White +2.00 → White +8.82. Pre-move candidate line: `12...Nf6 13.Be3`.

**Opponent’s screened critical decision: 30.Kf5.** 200,000-node recheck: White +7.97 → Black searched mate in 1. Pre-move candidate line: `30.Rg3 30...Rc2`.

**Recorded finish:** `28.Kh4 28...Rh2+ 29.Kg4 29...Rcg2+ 30.Kf5 30...Rg5#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.d4 2...Qd7 3.Nf3 3...Nf6 4.Nc3 4...Nc6 5.d5 5...Ne5 6.Nxe5 6...dxe5 7.Bb5 7...c6 8.dxc6 8...bxc6 9.Qxd7+ 9...Bxd7 10.Ba4 10...O-O-O`.

<a id="game-jwtajfrm"></a>

### 49. Emanuel_pro — Win as Black

**2026.10.21 · Emanuel_pro–mannyfresher · 0-1 · 66 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/U2jkVAt2) · [Game](https://lichess.org/jwTAjfrm).

**Queen plan:** first queen move `12...Qe7+`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `15.Qxe2` (other piece move) → `15...Qxe2`; `16.Rfe1` (other piece move) → `16...Qxe1+`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Nxf6`; opponent: `2.Nf3, 8.Nc3, 10.Bg5`. No non-castling early king move is recorded.

**Your screened critical decision: 10...a5.** 200,000-node recheck: White +5.83 → White +9.20. Pre-move candidate line: `10...Bg7 11.Bb5+ 11...Bd7 12.Bc4 12...Nc6`.

**Opponent’s screened critical decision: 16.Rfe1.** 200,000-node recheck: White +2.82 → White -6.45. Pre-move candidate line: `16.Nxe2 16...Nc6 17.Rfd1 17...Rd8 18.Nf4`.

**Recorded finish:** `31.Ne7+ 31...Kb5 32.Ng6 32...Rh6 33.Ne7 33...Ne3+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e4 1...d6 2.Nf3 2...f6 3.d4 3...b6 4.e5 4...g5 5.exf6 5...Nxf6 6.Nxg5 6...h6 7.Nf3 7...h5 8.Nc3 8...c5 9.dxc5 9...bxc5 10.Bg5 10...a5`.

<a id="game-tsutx3fq"></a>

### 50. WARIK_12364764-E — Win as Black

**2026.11.10 · WARIK_12364764-E–mannyfresher · 0-1 · 66 plies · Normal. [Study chapter](https://lichess.org/study/QLTafcOT/9Fl4YmqK) · [Game](https://lichess.org/game/tSUtX3fq).

**Queen plan:** first queen move `6...Qa5+`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `13.Bxf6` (repeat-piece move) → `13...Qxf6`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Nf6, 4...Nc6, 10...Bh3`; opponent: `4.Bg2, 5.Nf3, 6.Bg5, 7.Nbd2`. No non-castling early king move is recorded.

**Your screened critical decision: 30...Rd8.** 200,000-node recheck: White +0.87 → White +6.55. Pre-move candidate line: `30...Qf7 31.Rd7 31...c4 32.Rc7 32...a5`.

**Opponent’s screened critical decision: 33.Kh3.** 200,000-node recheck: White -7.71 → Black searched mate in 1. Pre-move candidate line: `33.Qf3 33...Qxf3+`.

**Recorded finish:** `31.Rxd8+ 31...Bxd8 32.f4 32...Qxe4+ 33.Kh3 33...Qh1#`. The final position is checkmate.

**Opening record:** `1.e4 1...d6 2.d3 2...c5 3.g3 3...Nf6 4.Bg2 4...Nc6 5.Nf3 5...e5 6.Bg5 6...Qa5+ 7.Nbd2 7...Nd4 8.O-O 8...Nxf3+ 9.Bxf3 9...Qd8 10.c4 10...Bh3`.

<a id="game-dlswv4m5"></a>

### 51. Genose — Win as Black

**2026.09.08 · Genose–mannyfresher · 0-1 · 42 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/MhOWgUk4) · [Game](https://lichess.org/DlsWV4m5).

**Queen plan:** first queen move `11...Qh4+`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `9...Bd7, 10...Bxc5`; opponent: `6.Nh3`. No non-castling early king move is recorded.

**Your screened critical decision: 14...Nxf2.** 200,000-node recheck: White -1.70 → White +8.68. Pre-move candidate line: `14...Ra7 15.Ba3`.

**Opponent’s screened critical decision: 17.Qxb8.** 200,000-node recheck: White +9.90 → White -1.27. Pre-move candidate line: `17.Qxa5 17...Rc8`.

**Recorded finish:** `19.Nb5 19...Ne4+ 20.Kc2 20...Bxb5 21.Qf3 21...Qf2+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...d6 2.d3 2...c5 3.c3 3...b6 4.f4 4...a5 5.Qe2 5...e6 6.Nh3 6...d5 7.d4 7...b5 8.b3 8...f5 9.dxc5 9...Bd7 10.c4 10...Bxc5`.

<a id="game-lulfisiu"></a>

### 52. sidpadhi — Win as White

**2026.09.08 · mannyfresher–sidpadhi · 1-0 · 75 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/wHZor7mJ) · [Game](https://lichess.org/LULfIsiU).

**Queen plan:** first queen move `3.Qe1`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5.Be2, 6.Nf3`; opponent: `6...Nc6, 7...Nh6`. Your non-castling early king moves: `2.Ke2, 4.Kd1`.

**Your screened critical decision: 18.Bh5.** 200,000-node recheck: White -18.38 → Black searched mate in 7. Pre-move candidate line: `18.f3 18...Qh4 19.Bf1 19...d5 20.c3`.

**Opponent’s screened critical decision: 37...Qxd3.** 200,000-node recheck: White -13.00 → White searched mate in 1. Pre-move candidate line: `37...e4 38.a3`.

**Recorded finish:** `35...Rd7+ 36.Kxc8 36...Qxc3 37.Rxh7 37...Qxd3 38.Rh8#`. The final position is checkmate.

**Opening record:** `1.e3 1...e5 2.Ke2 2...b6 3.Qe1 3...Qg5 4.Kd1 4...Qg4+ 5.Be2 5...Qxg2 6.Nf3 6...Nc6 7.h4 7...Nh6 8.Ng5 8...Rg8 9.Rg1 9...Qh2 10.Nf3 10...Qh3`.

<a id="game-zgcmzhlx"></a>

### 53. franck_tp — Draw as White

**2026.09.11 · mannyfresher–franck_tp · 1/2-1/2 · 116 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/tgfU7d9I) · [Game](https://lichess.org/ZGcMZHLX).

**Queen plan:** first queen move `22.Qb3`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5.Nf3, 6.Nbxd2, 10.Be2`; opponent: `1...Nc6, 6...Bb4`. No non-castling early king move is recorded.

**Your screened critical decision: 51.Kb5.** 200,000-node recheck: White -63.02 → White -76.82. Pre-move candidate line: `51.Kd4 51...Ne7`.

**Opponent’s screened critical decision: 58...g1=Q.** 200,000-node recheck: Black searched mate in 1 → terminal outcome. Pre-move candidate line: `58...Qa1#`.

**Recorded finish:** `56.Ka8 56...f1=Q 57.Ka7 57...g2 58.Ka8 58...g1=Q`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...Nc6 2.f4 2...e5 3.g4 3...exf4 4.h4 4...fxe3 5.Nf3 5...exd2+ 6.Nbxd2 6...Bb4 7.c3 7...Ba5 8.b4 8...Bb6 9.a4 9...Qe7+ 10.Be2 10...Be3`.

<a id="game-bfkicdgr"></a>

### 54. chess06sisi — Win as White

**2026.09.13 · mannyfresher–chess06sisi · 1-0 · 99 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/TPg2Z63q) · [Game](https://lichess.org/bFKICDGR).

**Queen plan:** first queen move `7.Qe1`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 4.Nd2`; opponent: `2...Nc6, 3...Nf6, 4...Bb4, 8...Bg4+`. Your non-castling early king moves: `6.Ke2, 10.Kf2`.

**Your screened critical decision: 36.Bxg7+.** 200,000-node recheck: White +0.66 → White -6.09. Pre-move candidate line: `36.Bg5`.

**Opponent’s screened critical decision: 44...Qg7.** 200,000-node recheck: White +9.14 → White searched mate in 2. Pre-move candidate line: `44...Qxh5`.

**Recorded finish:** `47...Kg6 48.Qe6+ 48...Kg5 49.Rg7+ 49...Kh4 50.Qh6#`. The final position is checkmate.

**Opening record:** `1.e3 1...e5 2.Ne2 2...Nc6 3.d3 3...Nf6 4.Nd2 4...Bb4 5.Ng3 5...d5 6.Ke2 6...d4 7.Qe1 7...O-O 8.e4 8...Bg4+ 9.f3 9...Be6 10.Kf2 10...Qd7`.

<a id="game-0ot0avbp"></a>

### 55. PamukSeker — Loss as White

**2026.09.17 · mannyfresher–PamukSeker · 0-1 · 48 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/747H95OW) · [Game](https://lichess.org/0Ot0AVBp).

**Queen plan:** first queen move `8.Qa4+`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `8...Bd7` (minor-piece development) → `9.Qd4`; `10...Nc6` (minor-piece development) → `11.Bxc6`; `11...Bxc6` (repeat-piece move) → `12.Qxd8+`.

**Theory assessment:** 2 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 4.Bg2`; opponent: `8...Bd7, 10...Nc6`. No non-castling early king move is recorded.

**Your screened critical decision: 18.Kh4.** 200,000-node recheck: Black searched mate in 4 → Black searched mate in 3. Pre-move candidate line: `18.Na3 18...h4 19.Nc4 19...hxg3+ 20.Kg4`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 18...Be7+.** 200,000-node recheck: Black searched mate in 3 → Black searched mate in 3. Pre-move candidate line: `18...Bg2 19.Kg5 19...Be7+ 20.Kf5 20...Rd5#`. The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.

**Recorded finish:** `22.Na3 22...g1=Q+ 23.Kf5 23...Qc5+ 24.Kg4 24...Qh5#`. The final position is checkmate.

**Opening record:** `1.e3 1...d5 2.Ne2 2...e5 3.g3 3...d4 4.Bg2 4...e4 5.Bxe4 5...c5 6.exd4 6...cxd4 7.c3 7...d3 8.Qa4+ 8...Bd7 9.Qd4 9...dxe2 10.Bxb7 10...Nc6`.

<a id="game-yulgizqu"></a>

### 56. Afiyet2016 — Draw as White

**2026.09.19 · mannyfresher–Afiyet2016 · 1/2-1/2 · 59 plies · Time forfeit. [Study chapter](https://lichess.org/study/7hLlnCHF/ydDbTU1X) · [Game](https://lichess.org/YUlGIZqU).

**Queen plan:** first queen move `11.Qxc2`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `12...Bd7` (minor-piece development) → `13.Qe4+`; `13...Qe7` (other piece move) → `14.Qxe3`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 6.Nd2, 8.Bg2`; opponent: `3...Nc6`. No non-castling early king move is recorded.

**Your screened critical decision: 30.Nc4+.** 200,000-node recheck: White searched mate in 1 → White +3.42. Pre-move candidate line: `30.Bb2#`.

**Opponent’s screened critical decision: 25...Ke6.** 200,000-node recheck: White -1.06 → White searched mate in 8. Pre-move candidate line: `25...Bxd1 26.Nf7`.

**Recorded finish:** `27...Kd4 28.Rbd1+ 28...Bxd1 29.Rxd1+ 29...Ke5 30.Nc4+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...e5 2.Ne2 2...d5 3.a3 3...Nc6 4.h3 4...b5 5.d3 5...f5 6.Nd2 6...f4 7.g3 7...e4 8.Bg2 8...d4 9.b3 9...exd3 10.Nxf4 10...dxc2`.

<a id="game-yhdp9b7u"></a>

### 57. AbilashNelapati — Win as Black

**2026.09.26 · AbilashNelapati–mannyfresher · 0-1 · 70 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/KJc3rKFD) · [Game](https://lichess.org/yHDp9B7U).

**Queen plan:** first queen move `17...Qf6+`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19.Qxf5` (repeat-piece move) → `19...Qxf5+`; `20.Bd3` (minor-piece development) → `20...Qc5+`.

**Theory assessment:** 1 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `2...Nf6, 6...Be7`; opponent: `none recorded`. Your non-castling early king moves: `7...Kd7`.

**Your screened critical decision: 29...Qxd2.** 200,000-node recheck: Black searched mate in 1 → White -12.18. Pre-move candidate line: `29...Qe6#`.

**Opponent’s screened critical decision: 27.Kc4.** 200,000-node recheck: White -9.61 → Black searched mate in 4. Pre-move candidate line: `27.h5 27...Qxe2 28.Rh4 28...Qxd2 29.Rc4+`.

**Recorded finish:** `33.Rd1 33...Nc2+ 34.Kb3 34...Kc5+ 35.Nb5 35...Rxb5#`. The final position is checkmate.

**Opening record:** `1.e3 1...d5 2.Qh5 2...Nf6 3.Qe5 3...Ng4 4.Qg3 4...e5 5.f3 5...Nh6 6.Qxe5+ 6...Be7 7.Qxg7 7...Kd7 8.Qxh6 8...Bh4+ 9.g3 9...Bg5 10.Qh3+ 10...f5`.

<a id="game-zfiz2fio"></a>

### 58. Stickity — Win as White

**2026.09.26 · mannyfresher–Stickity · 1-0 · 65 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/hJUTprSN) · [Game](https://lichess.org/zFiz2FiO).

**Queen plan:** first queen move `6.Qf3`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `12...dxe4` (pawn commitment) → `13.dxe4`; `15...Qxf6` (other piece move) → `16.Qb3`; `18...a4` (pawn commitment) → `19.Qc4`; `20...Bd7` (minor-piece development) → `21.Qxa8+`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4.Bb5`; opponent: `2...Nf6, 3...Nc6`. No non-castling early king move is recorded.

**Your screened critical decision: 32.Qg6+.** 200,000-node recheck: White searched mate in 5 → White searched mate in 4. Pre-move candidate line: `32.Rd7+ 32...Be7 33.Qg6+ 33...Kf8 34.Qe6`. The deeper check does not reproduce a substantial adverse swing; do not label this move a demonstrated blunder from the initial screen alone.

**Opponent’s screened critical decision: 31...Kf7.** 200,000-node recheck: White +23.21 → White searched mate in 5. Pre-move candidate line: `31...Be7 32.Nc4`.

**Recorded finish:** `30...Qg4+ 31.Qxg4 31...Kf7 32.Qg6+ 32...Kg8 33.Rxd8#`. The final position is checkmate.

**Opening record:** `1.e3 1...d5 2.h3 2...Nf6 3.g4 3...Nc6 4.Bb5 4...a6 5.Bxc6+ 5...bxc6 6.Qf3 6...e6 7.h4 7...Ne4 8.g5 8...a5 9.g6 9...fxg6 10.h5 10...g5`.

<a id="game-l6xkdb9k"></a>

### 59. RogueDoc007 — Win as White

**2026.09.26 · mannyfresher–RogueDoc007 · 1-0 · 37 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/tOWMQmei) · [Game](https://lichess.org/l6XkdB9K).

**Queen plan:** first queen move `2.Qf3`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `11...Nf4` (repeat-piece move) → `12.Qg3`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4.Bh3, 10.Nd2`; opponent: `1...Nf6, 3...Bg7, 10...Bxh3`. No non-castling early king move is recorded.

**Your screened critical decision: 15.c3.** 200,000-node recheck: White -6.61 → White -7.85. Pre-move candidate line: `15.Qc3 15...Qa6 16.Qf3 16...d5 17.Nf6+`.

**Opponent’s screened critical decision: 18...Bxf6.** 200,000-node recheck: White +2.88 → White +13.53. Pre-move candidate line: `18...Nxc1 19.Rxc1 19...Qd3+ 20.Ke1 20...d5`.

**Recorded finish:** `16...Nd3+ 17.Kf1 17...f5 18.gxf6 18...Bxf6 19.Nxf6+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...Nf6 2.Qf3 2...g6 3.g3 3...Bg7 4.Bh3 4...O-O 5.d4 5...Re8 6.e4 6...e5 7.d5 7...d6 8.g4 8...c6 9.g5 9...Nh5 10.Nd2 10...Bxh3`.

<a id="game-pjvmqqej"></a>

### 60. tixupixu — Win as White

**2026.09.27 · mannyfresher–tixupixu · 1-0 · 51 plies · Time forfeit. [Study chapter](https://lichess.org/study/7hLlnCHF/CdApVQI0) · [Game](https://lichess.org/pjvMqQeJ).

**Crazyhouse:** drop-aware legal replay; no standard-chess engine assessment.

This is Crazyhouse, won on time against tixupixu. Captured pieces can return as drops: 17…B@e6 is a drop-based queen threat, not ordinary bishop development. Its subsequent tactics are legally replayed under Crazyhouse rules. Standard Stockfish scores are deliberately absent, so this chapter is kept separate from standard-chess evaluation claims.

**Queen plan:** first queen move `12.Qb3`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `17...B@e6` (piece drop) → `18.Bxf7+`; `18...Bxf7` (repeat-piece move) → `19.@c4`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 5.Nd2`; opponent: `2...Nc6, 4...Nf6, 5...Be7`. No non-castling early king move is recorded.

**Recorded finish:** `23...Be6 24.c4 24...Na5 25.Qc3 25...dxc5 26.Rxg7+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...e5 2.Ne2 2...Nc6 3.f3 3...d6 4.d3 4...Nf6 5.Nd2 5...Be7 6.c3 6...O-O 7.g4 7...a6 8.h4 8...h6 9.h5 9...Nh7 10.f4 10...Bg5`.

<a id="game-ogru8gph"></a>

### 61. JaydenMogorosii — Win as White

**2026.09.30 · mannyfresher–JaydenMogorosii · 1-0 · 1 plies · Abandoned. [Study chapter](https://lichess.org/study/7hLlnCHF/R1rIL7wF) · [Game](https://lichess.org/OGrU8gpH).

Only one ply is recorded. The result is a White win, but the chapter contains no developed queen-chase or tactical sequence with which to test the theory. It belongs in the inventory, not among substantive supporting examples.

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `none recorded`; opponent: `none recorded`. No non-castling early king move is recorded.

**Recorded finish:** `1.e3`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3`.

<a id="game-p5kc7jsx"></a>

### 62. pavelbraginskiy — Win as White

**2026.09.30 · mannyfresher–pavelbraginskiy · 1-0 · 24 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/wzjaCzx5) · [Game](https://lichess.org/P5Kc7JsX).

**Queen plan:** first queen move `10.Qe2`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Nc3, 9.Bf4`; opponent: `5...Bf5, 6...Nf6, 7...Nc6`. No non-castling early king move is recorded.

**Your screened critical decision: 12.O-O-O.** 200,000-node recheck: White -3.25 → White -8.64. Pre-move candidate line: `12.Qf2 12...h4 13.Ne2 13...Be6 14.Kd1`.

**Opponent’s screened critical decision: 12...Rd6.** 200,000-node recheck: White -8.68 → White -5.50. Pre-move candidate line: `12...Qa2 13.h4`.

**Recorded finish:** `10.Qe2 10...O-O-O 11.Nxf6 11...gxf6 12.O-O-O 12...Rd6`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...e5 2.Nc3 2...d5 3.a3 3...d4 4.exd4 4...exd4 5.Ne4 5...Bf5 6.d3 6...Nf6 7.f3 7...Nc6 8.h3 8...h5 9.Bf4 9...Qd5 10.Qe2 10...O-O-O`.

<a id="game-cimlkc2j"></a>

### 63. Beckerhecht — Loss as Black

**2026.09.30 · Beckerhecht–mannyfresher · 1-0 · 95 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/s4gFN1l8) · [Game](https://lichess.org/cimlkC2j).

**Queen plan:** first queen move `11...Qg5`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `17.f4` (pawn commitment) → `17...exf4`; `18.exf4` (pawn commitment) → `18...Qg4`; `19.Be2` (repeat-piece move) → `19...Qg6`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `3...Bd7, 5...Nc6, 8...Be7`; opponent: `8.Bc4`. No non-castling early king move is recorded.

**Your screened critical decision: 46...Kd7.** 200,000-node recheck: White +6.83 → White searched mate in 3. Pre-move candidate line: `46...gxh6 47.Qf6+`.

**Opponent’s screened critical decision: 46.Qg6.** 200,000-node recheck: White searched mate in 5 → White +6.08. Pre-move candidate line: `46.Re6+ 46...Kd7 47.Qe8+ 47...Kc7 48.Rc6+`.

**Recorded finish:** `45...Ke7 46.Qg6 46...Kd7 47.Qxg7+ 47...Ke8 48.Rh8#`. The final position is checkmate.

**Opening record:** `1.e3 1...d6 2.c3 2...c5 3.Qa4+ 3...Bd7 4.Qb3 4...a6 5.Qxb7 5...Nc6 6.Qb3 6...Rb8 7.Qc2 7...e5 8.Bc4 8...Be7 9.a3 9...Bh4 10.g3 10...Bxg3`.

<a id="game-gwikn4ls"></a>

### 64. mogdalyan — Win as White

**2026.10.01 · mannyfresher–mogdalyan · 1-0 · 51 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/BLNVYTVP) · [Game](https://lichess.org/gWIkn4LS).

**Queen plan:** first queen move `22.Qe2`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5.Be2, 6.Bd2, 7.Nc3, 8.Nf3`; opponent: `1...Nc6, 2...Nf6, 7...Ba6, 8...Bh6`. No non-castling early king move is recorded.

**Your screened critical decision: 10.Rg1.** 200,000-node recheck: White +7.51 → White -0.08. Pre-move candidate line: `10.b4 10...Qe7`.

**Opponent’s screened critical decision: 25...Kb8.** 200,000-node recheck: White searched mate in 7 → White searched mate in 1. Pre-move candidate line: `25...Kd7 26.Bf6 26...Qxg2+ 27.Kxg2 27...Rxa8`. The deeper check does not confirm a substantial concession; the initial screening signal is not treated as a proven opportunity.

**Recorded finish:** `23...Rg8 24.Bxa8 24...Re8 25.Qa6+ 25...Kb8 26.Qb7#`. The final position is checkmate.

**Opening record:** `1.e3 1...Nc6 2.d3 2...Nf6 3.h3 3...e6 4.a3 4...Qe7 5.Be2 5...g6 6.Bd2 6...b6 7.Nc3 7...Ba6 8.Nf3 8...Bh6 9.Rb1 9...Qc5 10.Rg1 10...Bg5`.

<a id="game-e4gjbzys"></a>

### 65. agenT007_xx2 — Win as White

**2026.10.01 · mannyfresher–agenT007_xx2 · 1-0 · 61 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/VlclqMn0) · [Game](https://lichess.org/E4gJBzYS).

**Queen plan:** first queen move `6.Qd3`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19...Nf4+` (repeat-piece move; also check) → `20.Bxf4`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `3.Nf3, 8.Bd2`; opponent: `3...Bg4, 6...Bb4, 8...Nd7`. Your non-castling early king moves: `2.Ke2`.

**Your screened critical decision: 26.Rgh2.** 200,000-node recheck: White searched mate in 3 → White -12.67. Pre-move candidate line: `26.Rxh7+ 26...Kxh7 27.Qxg6+ 27...Kh8 28.Qh5#`.

**Opponent’s screened critical decision: 30...Bg5.** 200,000-node recheck: White -5.54 → White searched mate in 1. Pre-move candidate line: `30...h5`.

**Recorded finish:** `28...Bxh2+ 29.Kg2 29...Bf4 30.Qh3 30...Bg5 31.Qxh7#`. The final position is checkmate.

**Opening record:** `1.e3 1...c6 2.Ke2 2...d5 3.Nf3 3...Bg4 4.d4 4...Bxf3+ 5.gxf3 5...e6 6.Qd3 6...Bb4 7.c3 7...Ba5 8.Bd2 8...Nd7 9.b4 9...Bb6 10.a4 10...a5`.

<a id="game-gzr8dmhy"></a>

### 66. cata1983 — Win as Black

**2026.10.02 · cata1983–mannyfresher · 0-1 · 68 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/49C14q1i) · [Game](https://lichess.org/gzr8DmHy).

**Queen plan:** first queen move `7...Qa5+`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `8.Bd2` (minor-piece development) → `8...Qb6`.

**Theory assessment:** 1 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `9...Nc6, 10...Nf6`; opponent: `6.Bd3, 8.Bd2`. No non-castling early king move is recorded.

**Your screened critical decision: 26...Bf7.** 200,000-node recheck: White -17.76 → White -10.30. Pre-move candidate line: `26...Bxb2 27.Qf6+ 27...Kd7 28.Nc5+ 28...Nxc5`.

**Opponent’s screened critical decision: 32.Nxb4.** 200,000-node recheck: White -18.67 → Black searched mate in 5. Pre-move candidate line: `32.a3 32...Qxd4`.

**Recorded finish:** `32.Nxb4 32...Rxb2+ 33.Kc1 33...Rxb4 34.Rhf1 34...Qc6#`. The final position is checkmate.

**Opening record:** `1.e3 1...h6 2.d4 2...d5 3.h3 3...e5 4.c3 4...exd4 5.exd4 5...c5 6.Bd3 6...cxd4 7.cxd4 7...Qa5+ 8.Bd2 8...Qb6 9.Qc2 9...Nc6 10.Bh7 10...Nf6`.

<a id="game-ok27ng4f"></a>

### 67. ximenacaicedoluna — Win as White

**2026.10.04 · mannyfresher–ximenacaicedoluna · 1-0 · 13 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/6qsVKEfV) · [Game](https://lichess.org/Ok27NG4F).

**Queen plan:** first queen move `2.Qe2`; 3 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3.Nf3`; opponent: `3...Nc6, 4...Nf6, 5...Bc5, 6...Bf5`. No non-castling early king move is recorded.

**Your screened critical decision: 7.Qxb7.** 200,000-node recheck: White +4.84 → White -3.69. Pre-move candidate line: `7.Qxc5 7...h6 8.Nf3 8...Nd7 9.Qa3`.

**Opponent’s screened critical decision: 6...Bf5.** 200,000-node recheck: White -5.14 → White +4.58. Pre-move candidate line: `6...Qe7`.

**Recorded finish:** `4...Nf6 5.Ng5 5...Bc5 6.Qb5 6...Bf5 7.Qxb7`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...e5 2.Qe2 2...d5 3.Nf3 3...Nc6 4.h4 4...Nf6 5.Ng5 5...Bc5 6.Qb5 6...Bf5 7.Qxb7`.

<a id="game-xmzxmf9x"></a>

### 68. Rathiem888 — Draw as Black

**2026.10.04 · Rathiem888–mannyfresher · 1/2-1/2 · 127 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/5zprCskL) · [Game](https://lichess.org/XMZxmF9X).

**Queen plan:** first queen move `3...Qe8`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `11.Nxc8` (repeat-piece move) → `11...Rxc8`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `5...Nf6, 8...Nxc6, 10...Be7`; opponent: `1.Nc3`. Your non-castling early king moves: `2...Kd7, 4...Kd8`.

**Your screened critical decision: 43...Kg4.** 200,000-node recheck: White +7.53 → White searched mate in 1. Pre-move candidate line: `43...Ke6 44.Nb8`.

**Opponent’s screened critical decision: 64.Kf2.** 200,000-node recheck: White searched mate in 3 → terminal outcome. Pre-move candidate line: `64.Bb7 64...a6 65.bxa6 65...b5 66.Qxb5#`.

**Recorded finish:** `61...Ka5 62.g8=Q 62...Ka4 63.Qc4+ 63...Ka5 64.Kf2`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.Nc3 1...d6 2.Nb5 2...Kd7 3.d4 3...Qe8 4.Nc3 4...Kd8 5.e4 5...Nf6 6.f3 6...c6 7.d5 7...e6 8.dxc6 8...Nxc6 9.Nb5 9...Qd7 10.Nxd6 10...Be7`.

<a id="game-2edlynmz"></a>

### 69. Sungirl20 — Loss as White

**2026.10.05 · mannyfresher–Sungirl20 · 0-1 · 66 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/1V4k2rEf) · [Game](https://lichess.org/2edLyNmz).

**Queen plan:** first queen move `2.Qe2`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `5.Ne2, 6.Nbc3, 8.Bg2`; opponent: `none recorded`. Your non-castling early king moves: `3.Kd1`.

**Your screened critical decision: 32.Nxd2.** 200,000-node recheck: White +6.91 → Black searched mate in 2. Pre-move candidate line: `32.Nxg5 32...fxg5`.

**Opponent’s screened critical decision: 28...Kb8.** 200,000-node recheck: White -6.99 → White +8.00. Pre-move candidate line: `28...Nxf5 29.Rxf5`.

**Recorded finish:** `31.Qa6 31...g5 32.Nxd2 32...g4+ 33.Kh4 33...Ng6#`. The final position is checkmate.

**Opening record:** `1.e3 1...e5 2.Qe2 2...Qe7 3.Kd1 3...d6 4.Qe1 4...f6 5.Ne2 5...c5 6.Nbc3 6...b6 7.g3 7...d5 8.Bg2 8...d4 9.Ne4 9...dxe3 10.d3 10...exf2`.

<a id="game-fnxnkkr3"></a>

### 70. TheNorth87 — Win as White

**2026.10.05 · mannyfresher–TheNorth87 · 1-0 · 45 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/wJ6KyuWg) · [Game](https://lichess.org/FnXnKKR3).

**Queen plan:** first queen move `7.Qd2`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `12...Bxf4` (repeat-piece move) → `13.Qxf4`; `20...Qf4+` (repeat-piece move; also check) → `21.Qxf4`.

**Theory assessment:** 0 developing minor-piece threat(s), 2 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 4.Bg2, 6.Nbc3, 9.Bb2`; opponent: `3...Bf5, 5...Bd6, 6...Nf6, 8...Nbd7`. No non-castling early king move is recorded.

**Your screened critical decision: 12.Nf4.** 200,000-node recheck: White +8.46 → White -2.68. Pre-move candidate line: `12.dxe4 12...Bg4`.

**Opponent’s screened critical decision: 22...hxg5.** 200,000-node recheck: White +14.48 → White searched mate in 1. Pre-move candidate line: `22...Ng4 23.gxh6`.

**Recorded finish:** `20...Qf4+ 21.Qxf4 21...cxd3 22.hxg5 22...hxg5 23.Qxg5#`. The final position is checkmate.

**Opening record:** `1.e3 1...c6 2.Ne2 2...d5 3.g3 3...Bf5 4.Bg2 4...e6 5.d3 5...Bd6 6.Nbc3 6...Nf6 7.Qd2 7...O-O 8.b3 8...Nbd7 9.Bb2 9...c5 10.O-O-O 10...Qb6`.

<a id="game-ditwyjg9"></a>

### 71. zxcvbnmasfesgjejwj — Win as White

**2026.10.27 · mannyfresher–zxcvbnmasfesgjejwj · 1-0 · 51 plies · Time forfeit. [Study chapter](https://lichess.org/study/7hLlnCHF/dn9ni27j) · [Game](https://lichess.org/game/DItWyjG9).

Your Qb1–Qb2 arrangement was unconventional, but there was no qualifying queen-chase episode in the first twenty moves. The recorded result is a win on time after 26.Rg6+. The engine screen flags substantial tactical difficulties along the way. The win is real; a clock result and an objectively established opening advantage are different measurements.

**Queen plan:** first queen move `7.Qb1`; 2 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3.Nc3, 4.Be2, 5.Bd2, 6.Nf3`; opponent: `3...Nf6, 4...Bf5, 5...Nc6, 6...Bd6`. No non-castling early king move is recorded.

**Your screened critical decision: 25.Qb3.** 200,000-node recheck: White -14.31 → Black searched mate in 1. Pre-move candidate line: `25.Qa1 25...Qf3`.

**Opponent’s screened critical decision: 25...Qf3.** 200,000-node recheck: Black searched mate in 1 → White -17.77. Pre-move candidate line: `25...Qc1#`.

**Recorded finish:** `23...Kxh6 24.h5 24...Nh8 25.Qb3 25...Qf3 26.Rg6+`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...e5 2.d3 2...d5 3.Nc3 3...Nf6 4.Be2 4...Bf5 5.Bd2 5...Nc6 6.Nf3 6...Bd6 7.Qb1 7...h6 8.a3 8...Bh7 9.b4 9...a6 10.Qb2 10...O-O`.

<a id="game-yfui7qs7"></a>

### 72. Dmiiitr — Draw as White

**2026.10.31 · mannyfresher–Dmiiitr · 1/2-1/2 · 136 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/3qbrIJIN) · [Game](https://lichess.org/game/yFUi7qS7).

**Queen plan:** first queen move `9.Qd3`; 2 queen moves in the first ten recorded full moves, 1 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `10...Bd7` (minor-piece development) → `11.Qxb7`; `14...Qxe5` (repeat-piece move) → `15.Bg5`.

**Theory assessment:** 1 developing minor-piece threat(s), 1 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `4.Nf3`; opponent: `2...Nc6, 6...Bg7, 10...Bd7`. No non-castling early king move is recorded.

**Your screened critical decision: 26.c4.** 200,000-node recheck: White -71.35 → Black searched mate in 6. Pre-move candidate line: `26.Kg4 26...Rxh2`.

**Opponent’s screened critical decision: 68...Re8.** 200,000-node recheck: Black searched mate in 2 → terminal outcome. Pre-move candidate line: `68...Rh5+ 69.Ke6 69...Re5#`.

**Recorded finish:** `66.Kd3 66...Rc8 67.Ke4 67...Rd8 68.Kf5 68...Re8`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...c5 2.f4 2...Nc6 3.g3 3...e6 4.Nf3 4...g6 5.Ne5 5...Nxe5 6.fxe5 6...Bg7 7.d4 7...cxd4 8.exd4 8...d6 9.Qd3 9...dxe5 10.Qb5+ 10...Bd7`.

<a id="game-15qvqjqz"></a>

### 73. Arisotocrata — Win as White

**2026.11.02 · mannyfresher–Arisotocrata · 1-0 · 89 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/tevZBnTE) · [Game](https://lichess.org/game/15QVQJQZ).

**Queen plan:** first queen move `6.Qe2`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19...d3` (pawn commitment) → `20.Qe3`.

**Theory assessment:** 0 developing minor-piece threat(s), 0 repeated-piece threat(s). The record directly tests your response to queen pressure. Judge each episode by its concrete follow-up; neither the threat count nor the final result identifies wasted tempi by itself.

**Development and king commitments:** your first minor-piece moves through move 10: `3.Nf3, 5.Bg2, 7.Nc3`; opponent: `1...Nf6, 4...Bf5, 5...Nc6, 6...Be7`. No non-castling early king move is recorded.

**Your screened critical decision: 18.b3.** 200,000-node recheck: White +6.43 → Black searched mate in 5. Pre-move candidate line: `18.e5 18...Nxe5`.

**Opponent’s screened critical decision: 18...d4.** 200,000-node recheck: Black searched mate in 5 → White -2.76. Pre-move candidate line: `18...Qa3+ 19.Kc2 19...Nb4+ 20.cxb4 20...Qxa2+`.

**Recorded finish:** `42...Re2 43.Bd5+ 43...Kh8 44.Rxe2 44...a5 45.e8=N`. The supplied record does not end in a checkmated position; its header result and termination are retained.

**Opening record:** `1.e3 1...Nf6 2.h3 2...e5 3.Nf3 3...d6 4.g3 4...Bf5 5.Bg2 5...Nc6 6.Qe2 6...Be7 7.Nc3 7...O-O 8.d3 8...e4 9.Nxe4 9...Bxe4 10.dxe4 10...Nxe4`.

<a id="game-bqvwxnn0"></a>

### 74. AOK_Koliberda — Loss as Black

**2026.11.07 · AOK_Koliberda–mannyfresher · 1-0 · 33 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/GaAy4q7S) · [Game](https://lichess.org/game/BQVwXNN0).

**Queen plan:** your queen did not move in the supplied mainline; this is not a test of your early-queen mechanism.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `1...Nf6, 10...Bb7`; opponent: `7.Bd3, 10.Ne2`. No non-castling early king move is recorded.

**Your screened critical decision: 16...Be7.** 200,000-node recheck: White +2.05 → White searched mate in 1. Pre-move candidate line: `16...Nh4`.

**Opponent’s screened critical decision: 13.h4.** 200,000-node recheck: White +17.33 → White +3.02. Pre-move candidate line: `13.Qh5+`.

**Recorded finish:** `14...h6 15.Nh5 15...hxg5 16.fxg5 16...Be7 17.Nxg7#`. The final position is checkmate.

**Opening record:** `1.e3 1...Nf6 2.f4 2...Nd5 3.d4 3...Nb4 4.c3 4...N4c6 5.e4 5...e6 6.e5 6...Ne7 7.Bd3 7...Ng6 8.g4 8...Nh4 9.g5 9...b6 10.Ne2 10...Bb7`.

<a id="game-fjfuelbw"></a>

### 75. pietro_atlas — Loss as White

**2026.11.10 · mannyfresher–pietro_atlas · 0-1 · 72 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/dlVgbw2v) · [Game](https://lichess.org/game/fjFuElbw).

The clearest local piece-safety issue is 17.Qxe4 Bxe4: the bishop on h7 defended e4 along the diagonal. Your queen was lost when it captured the knight there. There was no qualifying early queen-chase episode in this chapter. This is a calculation/safety lesson rather than evidence that the provocation mechanism failed merely because an opening was unusual.

**Queen plan:** first queen move `5.Qe2`; 1 queen moves in the first ten recorded full moves, 0 capturing or checking. This is an early-queen test under the stated definition.

**Theory assessment:** no qualifying queen-pressure episode after your queen moved and within the first twenty recorded full moves. This game can illuminate your setup and tactics, but supplies no direct opening chase episode under this definition.

**Development and king commitments:** your first minor-piece moves through move 10: `3.Nc3, 4.Nf3, 6.Bd2`; opponent: `2...Bf5, 4...Nf6, 5...Bd6, 7...Nbd7`. No non-castling early king move is recorded.

**Your screened critical decision: 27.Re6.** 200,000-node recheck: White -15.61 → Black searched mate in 2. Pre-move candidate line: `27.a4 27...Qd4`.

**Opponent’s screened critical decision: 27...Kh7.** 200,000-node recheck: Black searched mate in 2 → White -16.39. Pre-move candidate line: `27...Rf1+ 28.Re1 28...Rxe1#`.

**Recorded finish:** `34.Kb3 34...Rb1+ 35.Ka3 35...Qxc3+ 36.Ka2 36...Qb3#`. The final position is checkmate.

**Opening record:** `1.e3 1...d5 2.d3 2...Bf5 3.Nc3 3...e6 4.Nf3 4...Nf6 5.Qe2 5...Bd6 6.Bd2 6...c6 7.O-O-O 7...Nbd7 8.g3 8...O-O 9.h3 9...h6 10.g4 10...Bh7`.

<a id="game-zomm9deu"></a>

### 76. Justinnn09 — Win as White

**2026.11.10 · mannyfresher–Justinnn09 · 1-0 · 95 plies · Normal. [Study chapter](https://lichess.org/study/7hLlnCHF/1j1079eC) · [Game](https://lichess.org/game/zoMm9deu).

A successful unconventional opening without an early queen outing: your queen first moved on move 19. The early story is pawn commitments and bishop activity, including Bxc7 and Bxb8. This belongs to the broader controlled-unfamiliarity programme, but should not be counted as evidence for a specifically early-queen psychological mechanism.

**Queen plan:** first queen move `19.Qxd4`; 0 queen moves in the first ten recorded full moves, 0 capturing or checking. This is not an early-queen test under the stated definition.

**Queen-pressure ledger, through move 20:** `19...Qb6` (repeat-piece move) → `20.Qxb6`.

**Theory assessment:** 0 developing minor-piece threat(s), 1 repeated-piece threat(s). The threats occurred after a later queen move, so they illuminate queen handling without directly testing early deployment.

**Development and king commitments:** your first minor-piece moves through move 10: `2.Ne2, 3.Nbc3, 5.Bg2`; opponent: `2...Nc6, 3...Nf6`. No non-castling early king move is recorded.

**Your screened critical decision: 32.Rb6.** 200,000-node recheck: White searched mate in 8 → White +13.30. Pre-move candidate line: `32.Rxf5+ 32...Ke8 33.Rxb5 33...Bd8 34.Rb7`.

**Opponent’s screened critical decision: 39...Bd6.** 200,000-node recheck: White +11.30 → White searched mate in 11. Pre-move candidate line: `39...Ke6 40.g4 40...Nd4 41.g5 41...Nb3`.

**Recorded finish:** `45...Kg4 46.h3+ 46...Kg5 47.Qg7+ 47...Kh5 48.Qg4#`. The final position is checkmate.

**Opening record:** `1.e3 1...e5 2.Ne2 2...Nc6 3.Nbc3 3...Nf6 4.g3 4...g5 5.Bg2 5...h5 6.O-O 6...g4 7.Bxc6 7...bxc6 8.d4 8...Rb8 9.dxe5 9...Ng8 10.e4 10...Qe7`.
