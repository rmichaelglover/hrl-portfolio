# Progression words: addition, repetition, and an expressivity boundary

**Originating proposal and research direction: Michael Emanuel Glover.** Michael proposed constructing a logic from legal chess progressions, investigating arithmetic interpretations, and factoring transformations to reduce repeated work. Cypher contributed this continuation's formal construction, C++ implementation, examples and tests. It extends [the preceding lesson](02-legal-progression-logic.md) and the existing Magnum Chessicus engine.

This lesson introduces a genuinely unbounded mathematical word domain, proves an additive interpretation, identifies an exact first-order limitation, and specifies one sufficient extension for multiplication. The C++ program implements ground operations and checks examples. The general expressivity statements are mathematical arguments; no general arithmetic theorem prover has been implemented.

## Start here: what should the reader take away?

Michael's proposal asks whether legal chess transformations can serve as a language for arithmetic, and whether their structure offers useful compression. We now have a worked example with three distinct results: a reusable movement loop, an exact additive interpretation on words, and an explicit extension for multiplication.

**Picture a short dance.** White's knight goes out, Black's knight goes out, White's knight comes back, and Black's knight comes back. Call the whole dance c. One c is four plies: four individual player moves. The pieces and movement rights return to their starting configuration. The fact that the dance happened is still part of the history.

**Now count dances, not board arrangements.** The empty dance ε represents zero; c represents one; cc represents two. Appending a three-dance history to a four-dance history gives seven dances. That is addition expressed by concatenating the histories themselves:

    ccc ; cccc = ccccccc
    3 + 4 = 7 cycles = 28 plies.

Multiplication asks a different question: take the entire three-dance block and perform it four times. That gives twelve dances, not seven:

    (ccc)(ccc)(ccc)(ccc) = c^12
    3 * 4 = 12 cycles = 48 plies.

A fixed number of copies can always be written as a finite concatenation. Letting another variable word specify how many copies to make is a stronger operation. We call that new operation Repeat. The mathematical result below explains why no first-order formula in the concatenation-only language already defines general multiplication. Our C++ implementation supplies Repeat explicitly; it does not discover multiplication hidden inside ordinary chess moves.

**Why change the rules?** An ordinary game would end in a draw instead of allowing this dance forever. To study unbounded words, we declared a movement-only variant without draw adjudication. We also made entire histories the mathematical objects. We did not turn one ordinary chess board into infinitely many distinct board configurations.

**Why is the huge example useful?** A checked dance and its repetition count can describe an enormous move history exactly. The program adds one to a 41-digit cycle count without writing out the moves. This is compression of a particular repeatable witness family. It is not yet a method for evaluating every opponent reply or solving the initial position.

| Result | What establishes it | What it tells us |
|---|---|---|
| The knight dance can repeat in the variant | One legal period checked in C++, plus induction on the number of periods | Every finite word c^n has a legal movement interpretation |
| Concatenation expresses addition | The bijection c^n ↔ n preserves the operation | A faithful unbounded additive interpretation in the declared first-order word language |
| First-order concatenation cannot define general multiplication | The classical Presburger definability theorem, transferred through that bijection | A precise limitation of this selected language; not a limit on every possible chess-based language |
| Added Repeat expresses multiplication | Its specified meaning Repeat(c^a,c^b)=c^(ab), and the same bijection | One sufficient enrichment for the full arithmetic signature |
| Symbolic words remain exact at large counts | C++ ground examples and tests, including values beyond 64 bits | The representation avoids expanding this witness family |

The contribution here is Michael's chess-progression research direction and this explicit construction, implementation and application of established logic. The Presburger theorems are established results, credited in the references below. Tests check program behavior; they do not replace the general mathematical proofs. Arithmetic expressivity, an effectively axiomatized proof theory, and optimal chess play remain distinct questions.

## 1. Remove a bound explicitly

Choose the generator

    c = g1f3 g8f6 f3g1 f6g8.

From the standard initial position, these four legal plies restore piece placement, side to move, castling rights and effective en-passant possibilities. They do not restore the complete history or move counters.

Ordinary chess therefore does not permit this loop to repeat forever: automatic draw adjudication eventually ends the game. The original `Progression`, `State`, outcome solver and modal checker keep their existing rules.

For this new construction, declare a **movement-only variant without draw adjudication**. It retains orthodox move legality, occupancy, king safety, side to move, castling rights and en-passant constraints. It ignores draw claims, repetition adjudication, move-count adjudication and other draw adjudication. Mate and stalemate still prevent further moves because they have no legal movement successor. The construction is about move words, not a complete competitive scoring system.

The movement position is a projection of a game state, not a full game state. `projected_board` resets the library's counters after each step to prevent finite-counter overflow. It does not silently make a standard game's history cyclic. Chess960 is rejected explicitly.

`LoopCertificate` checks one nonempty period using the existing legal move generator and checks equality of the projected starting and ending position keys. The explicit `movement_only` tag is required when constructing a certificate. It does not certify reachability of an arbitrary supplied root from the normal initial position.

**Repeatability lemma.** Move legality in the selected variant depends on the projected movement position, not on the discarded adjudication data. If every move in c is legal and c returns to its starting projected position, then c^n is a legal movement word for every natural number n. Proof: the empty word is legal. If c^n is legal and ends at the starting projected position, the same checked period c can be appended, establishing c^(n+1). This is a mathematical induction argument over a finite, checkable loop certificate.

The supplied generator is jointly performed by White and Black. Its repeatability proves the existence of a cooperative progression. It does not prove that White can force Black to keep participating.

## 2. An infinite domain from finite descriptions

Let

    D = {ε, c, cc, ccc, ...} = {c^n : n ∈ N}.

Objects are finite move words, rather than just their terminal board positions. Different exponents denote different words even though their projected endpoints agree. Because c is nonempty, words with different exponents have different lengths. We do not identify all returning words with a single board state.

Define the structure

    W_add = (D; ε, c, ;),

where `;` is concatenation. Every pair of words in D can compose because each whole period returns to the same projected position. This is a one-generator free monoid. The general category of chess progressions has partial composition; this chosen loop family has total composition. Powers of this single generator also commute under concatenation. That does not mean distinct chess moves or unrelated loop families commute.

**Encoding implementation.** `Word` stores a shared checked generator and an exact canonical decimal exponent. `Natural` uses a dynamically sized digit string, rather than a uint64 counter. It can represent, for example, c^(10^40) and its successor without expanding the moves. Every actual object and allocation is finite; the mathematical family has no fixed maximum exponent. Available memory remains a physical bound on implementation, not a new mathematical largest natural number.

Words from different declared generator families cannot be concatenated by this API. Generator identity includes its projected starting position, explicit movement policy, and ordered moves. Two families may have related expansions, but no cross-family equivalence theorem or quotient is claimed.

`Word::materialize(max_plies)` is a separate bounded request. If the expansion would exceed the allowance, it throws `ResourceLimit`; it neither truncates nor changes the exact symbolic word. The earlier natural-number byte codec can encode this compressed representation. That code is not the same number as a code of the fully expanded history.

## 3. Addition is now intrinsic to the word operation

Define

    ν : D → N,     ν(c^n)=n.

This is a bijection, and

    ν(ε)=0,
    ν(c)=1,
    ν(x;y)=ν(x)+ν(y).

Consequently W_add is isomorphic to (N;0,1,+). This is stronger than the previous lesson's externally supplied finite arithmetic table: addition is exactly the existing concatenation operation on the chosen domain.

A first-order word language has variables ranging over D, constants ε and c, equality, concatenation, ordinary Boolean connectives and quantifiers over D. In that language:

    Zero(x)       := x=ε
    Succ(x,y)     := x;c=y
    Add(x,y,z)    := x;y=z
    Leq(x,y)      := ∃z (x;z=y).

To translate an additive arithmetic formula, replace 0 with ε, 1 with c, and + with `;`, leaving equality and logical structure intact; quantify over D. Structural induction on terms and formulas proves that the translation preserves truth under the bijection ν. Thus the construction faithfully interprets unbounded additive arithmetic in this specified word language.

This is an added first-order word structure. The previous state-modal language did not already quantify over all histories, and has not silently acquired those quantifiers.

The relevant classical setting is Presburger arithmetic, with a decidable first-order theory; see the [logic course's Presburger treatment](https://cvc4.cs.stanford.edu/logic/slides/lec10.pdf). The C++ code here implements exact ground concatenation and equality, not a quantifier-elimination algorithm or decision procedure for arbitrary first-order formulas. Infinite domain and unbounded syntax therefore need not imply undecidability.

## 4. Multiplication is not hidden in first-order concatenation

Fixed repetition is available: for any fixed natural k, concatenating x with itself k times expresses multiplication by that fixed constant. Each k gives a finite term. There is no single first-order formula in W_add defining general multiplication of two variable exponents.

For the precise scope, assume a formula in the first-order concatenation language defined M(x,y,z) exactly when ν(z)=ν(x)ν(y). Translating through ν would define multiplication in Presburger arithmetic. The classical definability theorem says each unary Presburger-definable set is ultimately periodic; its modern formalization also explicitly establishes that multiplication is not definable. See the [Mathlib definability results](https://leanprover.github.io/hex/docs/Mathlib/ModelTheory/Arithmetic/Presburger/Definability.html).

Here is the obstruction using squares. If multiplication were definable, so would be

    Square(z) := ∃x M(x,x,z).

Suppose the squares were periodic beyond N with positive period p. Choose n with n²>N and 2n+1>p. Periodicity would make n²+p a square, yet

    n² < n²+p < (n+1)²,

which is impossible. Thus squares are not ultimately periodic, contradicting the definability theorem.

The conclusion is specific to first-order W_add. It does not prohibit C++ loops, richer sequence languages, second-order quantifiers, newly added predicates, or a different multi-generator word construction from expressing more. Finite ground tests cannot establish this nondefinability theorem; the theorem and the isomorphism do that work.

## 5. One sufficient extension: variable-count block repetition

Add a new binary operation on word objects:

    Repeat(c^a,c^b) = (c^a) repeated b times = c^(a*b).

The second argument is another word in D, interpreted as a counter by its cycle length. This is well-defined for every pair, with Repeat(x,ε)=ε and Repeat(x,c)=x. It satisfies the recursion

    Repeat(x,y;c) = Repeat(x,y);x.

**Repeat is explicitly new vocabulary.** It is not claimed to be first-order definable from concatenation. Writing the recursion is not a proof that a formula in the old language can express arbitrary iterations. The `RepeatExtension` C++ class implements the intended operation by exact decimal multiplication; that algorithm computes the new interpretation rather than deriving it from the old language.

For the expanded structure

    W_arith = (D; ε, c, ;, Repeat),

the same ν gives an isomorphism to (N;0,1,+,*). Extend the translation with x*y mapped to Repeat(x,y). Structural induction now proves truth preservation for the full first-order arithmetic signature. This supplies a specific sufficient extension for an arithmetic interpretation; it is not a proof that Repeat is the only possible route or that standard chess already contains it.

A useful difference in the example:

    c^3 ; c^4             = c^7
    Repeat(c^3,c^4)        = c^12.

Both produce legal words in the variant, but only the second uses the added variable-count operation.

## 6. What this does and does not imply about Gödel

The intended W_arith structure satisfies translated arithmetic truths, including the PA axioms and each translated induction instance, by its isomorphism with the standard natural numbers. That is a semantic statement in the surrounding mathematics.

A proof system is a separate object. One can choose translated PA as an effectively axiomatized theory in this expanded word language. Conditional on its consistency, the usual incompleteness results apply to that theory. The set of *all* truths of W_arith is complete by its definition but is not an effective axiomatization; these are different theories.

We have not implemented PA proof syntax, proof checking, internal arithmetization of those proofs, or a Gödel sentence. We have not shown that the standard finite chess game is undecidable, inconsistent, or a draw. We have established where an additive word structure stops and what one explicit extension contributes.

## 7. Compression with a precise scope

A checked loop and a 41-digit exponent represent 4×10^40 individual plies. Concatenating c^a and c^b costs work proportional to exponent-digit lengths for this implementation, rather than work proportional to the expanded histories. The period is certified once; its legality for all repetitions follows from the repeatability lemma.

This is exact compression of a selected cooperative witness family. It does not compress all possible legal games, retain all adversarial branches, or improve a worst-case chess-solving bound. We have changed both the rule policy and the domain to study expressivity. A search-compression experiment must separately preserve the original rules and strategic quantifiers.

## 8. Read, run, and inspect

The existing C++17 project now contains:

- [`include/progression_words.hpp`](../include/progression_words.hpp): Natural, LoopCertificate, Word, RepeatExtension.
- [`src/word_demo.cpp`](../src/word_demo.cpp): the small worked example.
- [`tests/word_tests.cpp`](../tests/word_tests.cpp): exact arithmetic, loop checks, policy separation, coding and bounded expansion checks.
- [`data/progression-words/demo.txt`](../data/progression-words/demo.txt): captured output.

```sh
cmake -S . -B /tmp/magnum-progression-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/magnum-progression-build -j 2
ctest --test-dir /tmp/magnum-progression-build --output-on-failure
/tmp/magnum-progression-build/word_demo
```

No new runtime dependencies. Both the original outcome tests and the earlier bounded-logic tests remain in CTest. The new suite checks 1,000 deterministic arithmetic/law cases, large carries beyond machine-word sizes, a 160-ply movement-only replay, refusal of the same kind of continuation under standard adjudication, and explicit expansion-budget refusal. Those checks validate implementation instances; the all-natural-number claims rest on the mathematical proofs above.

Next didactic step: specify a small proof language for this expanded arithmetic structure and verify proof objects, keeping that separate from the ordinary chess solver. A separate empirical track can test safe compression of standard-game witnesses.
