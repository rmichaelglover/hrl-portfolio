# A logic built from legal chess progressions

**Originating proposal and research direction: Michael Emanuel Glover.** Michael proposed using legal state transformations, composition and numerical coding to investigate chess's expressive power and opportunities for compression. Cypher contributed this formalization, C++ implementation, examples and checks. The implementation extends Magnum Chessicus's existing legal-move, history and terminal kernel; it does not start a separate chess engine.

This lesson establishes a bounded modal logic, an injective numerical syntax code, and an explicit finite arithmetic construction. It identifies the additional structure required before a claim about interpreting arithmetic or applying incompleteness would follow.

## 1. Objects, legal steps, and their composition

A semantic state contains a board, side to move, rights, counters and local repetition history. Use the existing `magnum::State`. A root supplied as FEN starts a new local history: it does not assert that the position is reachable from the standard starting position.

Write `s —m→ t` when m is legal at s, s is nonterminal in the selected kernel, and applying m yields t. A certified progression is

    p : s —m1→ s1 —m2→ ... —mk→ t.

There is an empty progression `id_s : s→s`. Two progressions compose only when the end of the first is the complete initial state of the second:

    p : s→t    q : t→u
    -----------------  composition
          p;q : s→u

Lengths satisfy `length(p;q)=length(p)+length(q)`. Composition is associative and empty progressions are identities, so complete states and certified progressions form a path category. This is composition of directed paths, not a group: inverse moves need not exist. Captures and history changes make reversibility particularly restrictive.

`Progression` replays the existing kernel, rejects illegal edges and continuation after recognized terminals, and checks intermediate equality using a collision-free serialization. It stores the full move witness rather than merely asserting reachability. Its numerical code includes the supplied root and move sequence.

**Rules scope.** The reused kernel recognizes mate, stalemate, fivefold repetition, 75-move automatic draws, and a sufficient dead-material subset. Its dead-position detector is not a complete implementation of every FIDE dead position. This lesson's movement relation does not include optional draw-claim actions, resignation, agreements, clocks or negotiations. These semantics are a specified Magnum progression model, not a new claim of complete FIDE adjudication. An adversarial query below concerns forcing its stated goal through movement, not every possible off-board action.

## 2. A language whose modalities mean legal progressions

Define formulas by this grammar:

    φ ::= True | WhiteTurn | WhiteMate | Terminal | Position(k)
        | Not φ | (φ And φ) | (φ Or φ) | Some φ | Every φ.

`Position(k)` checks the existing repetition-position key (placement, turn, castling rights and effective en-passant); it deliberately does not assert equality of complete histories. Numerical state identity does retain history. `WhiteMate` means Black to move, in check, with no legal move.

The judgments are `s ⊢ φ : true` and `s ⊢ φ : false`. Atoms are evaluated from the state; the Boolean connectives follow their classical truth tables. The characteristic modal inference rules are:

    s —m→ t    t ⊢ φ : true
    ----------------------  Some-true
        s ⊢ Some φ : true

    for every legal successor t of s: t ⊢ φ : false
    ------------------------------------------------ Some-false
                 s ⊢ Some φ : false

    for every legal successor t of s: t ⊢ φ : true
    ----------------------------------------------- Every-true
                 s ⊢ Every φ : true

    s —m→ t    t ⊢ φ : false
    ----------------------- Every-false
       s ⊢ Every φ : false

At a terminal state there are no movement successors: `Some φ` is false and `Every φ` is true. This is ordinary vacuous universal quantification, not a claim that a player wins by having no move. Negation exchanges true and false; in particular `Every φ ≡ Not Some Not φ`.

`ModelChecker` implements these rules by traversing legal successors. Each recursive evaluation consumes budget. Exhaustion throws `ResourceLimit`, returning **no verdict**, rather than mistaking an unfinished search for false. It does not construct an independent portable proof certificate; the existing outcome solver's certificate system remains separate.

**Soundness and local completeness theorem.** Relative to a fixed, correctly computed transition relation and atomic valuation, these judgment rules derive exactly the semantic truth value of every finite formula at every state. Proof: structural induction on the formula. Atoms are their defining valuations; the induction hypothesis establishes the Boolean cases. The finitely many successors and induction hypothesis establish the existential and universal cases, including empty successor sets. Each modal step reduces formula depth, so a finite derivation exists even if the underlying graph has cycles. A sufficient evaluation budget therefore decides each query. It also follows that no state has derivations of both truth values for the same formula under these rules. This is consistency of the specified semantic judgment system; it is not an arithmetic theory proving its own consistency. This theorem is about these semantic judgments, not an implemented Hilbert calculus or a proof of every assertion about chess.

The family relationship to modal/dynamic logic is intentional. Sequential progression is already available through composition and nested modalities; full program syntax for choice, tests and Kleene iteration is not implemented in this first lesson. See the primary course handout on [propositional dynamic logic](https://www.cs.cornell.edu/courses/cs6860/2010fa/Handouts/HKT4-10.pdf).

## 3. Two agents: cooperation differs from forcing

For any goal g, define bounded cooperative reachability:

    R_0(g) = g
    R_(d+1)(g) = g Or (Not Terminal And Some R_d(g)).

Define White's bounded adversarial forcing:

    F_0(g) = g
    F_(d+1)(g) = g Or (Not Terminal And
        ((WhiteTurn And Some F_d(g)) Or
         (Not WhiteTurn And Every F_d(g)))).

The terminal guard prevents vacuous `Every` from inventing a win at a terminal position where g is false. The existential and universal branches implement the two players' different control of moves. If both players share a single objective, R is the appropriate existence query for a coordinated plan. It establishes possibility, not that independently acting agents will coordinate. A negotiation protocol would need explicit actions and preferences, and is outside this first model.

Executable example: after `1. e4`, reaching the position after `1... e5` is possible, but White cannot force Black to choose that particular reply. The checker returns true for R and false for F. A separate queen-and-king fixture establishes a White mate in one ply.

## 4. Numbering without smuggling in arithmetic

For a finite byte string b1...bk, define its code as

    G(bytes) = 1000^k + Σ(i=1..k) bi * 1000^(k-i),   0 ≤ bi ≤ 255.

Its decimal representation is a leading `1` followed by k three-digit byte blocks. Empty text encodes as `1`. The leading base-1000 digit and fixed-width blocks give a unique inverse. Thus distinct serialized objects have distinct positive-integer codes, without relying on hashes or prime factorization. The C++ implementation handles these integers as exact decimal strings, avoiding machine-integer overflow.

State fields and progression fields have explicit length delimiters. Formula text has fixed operator tokens and length-delimited subexpressions. `number` and `unnumber` provide exact byte roundtrips. This first implementation does not parse serialized formula text back into an AST, arithmetize a proof-checking predicate within the object language, or establish internal self-reference.

This is a Gödel-style coding *ingredient*. The arithmetic in the coding algorithm is in the surrounding implementation/metatheory. Giving an expression a number does not make addition, multiplication or statements about proofs expressible inside the modal language.

## 5. Precisely what bounded arithmetic we have built

Choose a certified eight-ply progression, consisting of two legal knight-return cycles from the initial position:

    g1f3 g8f6 f3g1 f6g8 g1f3 g8f6 f3g1 f6g8.

Its nine prefixes form distinguished objects v0,...,v8. Number n denotes the prefix of length n. The full histories distinguish these objects even when their board-position keys agree.

Extend the structure with the following explicit finite relations:

    Zero(v0)
    Succ(vi,vj)       iff j=i+1 ≤ 8
    Add(vi,vj,vk)     iff i+j=k ≤ 8
    Mul(vi,vj,vk)     iff i*j=k ≤ 8.

`PrefixArithmetic` constructs the corresponding partial operations on prefix indices. The tables agree exactly with natural-number arithmetic wherever all inputs and the result are in the stated domain. Every pair of indices 0..8 is checked in the tests. Addition also reflects concatenation of the corresponding consecutive path segments. Multiplication is the externally supplied bounded repeated-addition table; no intrinsic multiplication operation on boards has been proved.

**Status of this construction:** a faithful finite arithmetic expansion on certified prefix objects. These relations are NOT proved definable in the bare modal language of Section 2. They are additional structure. In first-order logic with a name for each vi, each table can trivially be defined by a finite disjunction of matching triples, but that imports enumeration and gives no compression theorem.

The boundary is visible: `2*4=8`, while `3*3` has no value in this domain, and `Succ(v8, x)` holds for no x. This is neither arithmetic modulo 9 nor a model of PA or Robinson Q.

**Finite-domain obstruction.** Suppose a nonempty finite domain D had a total injective successor S with no x satisfying S(x)=0. Any injective self-map of a finite set is surjective, so some x must satisfy S(x)=0: contradiction. These are already requirements of Q. Consequently no finite-domain structure can satisfy them all. Moreover, any ordinary first-order interpretation using a fixed finite tuple dimension and a definable quotient inside a finite structure still has a finite domain. It therefore cannot interpret a model of Q. This covers ordinary finite-state relational interpretations; it does not cover adding an unbounded sort of syntax, sets or histories from outside.

This proof identifies the limitation rather than inferring it merely from the experiments. It also explains why internally interpreting full arithmetic is different from externally encoding a finite chess structure in arithmetic.

## 6. Which bounds to remove, and what that buys

1. **Retain ordinary bounded play.** Formula syntax can be arbitrarily long in principle, but each semantic state domain is finite. Longer formulas do not by themselves add an infinite object-level number domain. The present checker decides individual finite formulas, subject to budget.
2. **Remove draw termination and allow unbounded recorded play, in an explicit variant.** Repeating the four-ply knight macro c then yields distinct history words ε,c,cc,... even though placements recur. This is a mathematical extension, not legal infinite play under standard automatic draw rules. If the domain includes those words and concatenation is made available, length yields an unbounded additive structure: c^a;c^b=c^(a+b). First-order addition alone is not sufficient for Gödel incompleteness. The extension and its operations must be specified, not silently added to the existing kernel.
3. **Provide genuinely unbounded memory or workspace.** Candidates include an unbounded history/syntax sort, an expanding board family, or external writable memory. Each changes the object being studied. They supply potential capacity; they do not by themselves prove universal computation, definability of multiplication or interpretation of Q.
4. **Prove an arithmetic interpretation.** Give a uniform domain formula, equality relation, Zero, Succ, Add and Mul definitions; specify quantifier translation; and prove the translated axioms of the chosen arithmetic theory. A separate universal-computation construction would need its own encoding and simulation proof.
5. **Specify a proof theory before invoking incompleteness.** A consistent, effectively axiomatized theory interpreting sufficient arithmetic is the relevant setting. Syntax numbering and unbounded capacity alone do not establish all those hypotheses. Neither undecidability nor inconsistency of standard chess follows from this lesson.

The next research target is a precisely specified unbounded progression-word extension and its definable operations, alongside experiments on compressing the bounded logic. A compression result must preserve the distinction between Some and Every and account for the cost of building the representation. Nothing in this first milestone establishes that matrix factorization reduces total search cost.

## Run and read

From `magnum-chessicus/cpp`:

```sh
cmake -S . -B /tmp/magnum-progression-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/magnum-progression-build -j 2
ctest --test-dir /tmp/magnum-progression-build --output-on-failure
/tmp/magnum-progression-build/progression_demo
```

Read [`include/progression_logic.hpp`](../include/progression_logic.hpp), then [`src/progression_demo.cpp`](../src/progression_demo.cpp), then [`tests/progression_tests.cpp`](../tests/progression_tests.cpp). C++17; no new runtime dependencies. The pinned MIT-licensed chess library and its provenance remain those of the existing project.

Further reference: [Gödel's incompleteness theorems](https://plato.stanford.edu/archives/spr2026/entries/goedel-incompleteness/index.html). This lesson distinguishes model checking, finite arithmetic tables, arithmetic interpretation and proof-theoretic completeness throughout.
