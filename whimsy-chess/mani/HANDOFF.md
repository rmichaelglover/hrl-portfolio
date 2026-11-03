# Maestro / Mani — project handoff

Updated 3 November 2026. Originating architecture and mission: **Michael Glover**. Implementation: Cypher / ChatGPT / Codex.

## Where we are

The published prototype is a complete demonstration of the current execution and accounting scope. It can remain available without a running backend, paid infrastructure, scheduled jobs, or token-market operations. Browser records remain on the device that created them; export any receipts worth retaining.

Implemented:

- Browser research challenges, relaxation labeling, hypothesis inspection, and replay-verifiable local receipts.
- Demonstration 80/10/10 accounting and a separate realized-revenue Sanctuary calculator.
- PoDD v0 fixed-point execution, Merkle trace commitments, complete replay, selected-transition openings, and schema validation rules.
- Browser export/import, headless CLI, and a loopback JSON-RPC verifier.
- Regression tests including a forged-prefix counterexample, tamper rejection, and transport behavior.

The floating-point research view and integer PoDD profile are explicitly distinct. PoDD reports what it checked. Scientific utility, signed identities, peer networking, shared finality, and funded settlement remain separate milestones.

## Restart in five minutes

From the repository root:

```sh
cd whimsy-chess/mani
npm test
```

Requires Node 20 or later. No dependency installation is needed. HTTP tests bind a temporary loopback port and close it afterward; environments that restrict local sockets must allow that test to bind.

To run the local verifier:

```sh
npm start
```

It listens on `127.0.0.1:8891` until stopped with Ctrl+C. The static website does not start or contact it automatically.

For the browser interface, use the [published workspace](https://rmichaelglover.github.io/hrl-portfolio/whimsy-chess/mani/) or serve the repository root over localhost. The [PoDD specification](PODD.md) includes the complete CLI example and JSON-RPC methods. The [README](README.md) describes the original scientific view and accounting.

## One next milestone

**Two separately running processes exchange one authorized task and produce independently verifiable signed reports.**

Acceptance criteria:

1. A proposer publishes its challenge commitment and trace before the validator selects an audit seed.
2. A validator checks a correct submission and produces a signed report binding the task ID, receipt ID, arithmetic profile, verification mode, selected steps if applicable, and result.
3. A deliberately corrupted submission produces reproducible invalid-transition evidence. A sample that misses the bad step remains explicitly a sample, never full verification.
4. A durable task registry retains claims and reports across restarts and rejects duplicate credit for the same authorized task.
5. A demonstration ledger allocates 80/10/10 only under a documented acceptance policy. No transferable MNI or real treasury balance is inferred from those records.

The milestone does not require public deployment of a validator, token issuance, staking, or a supplier integration. Those can follow after the exchange and registry work reliably.

## Keeping the project ready

If the project rests: leave the site online, retain this handoff, and export valuable local receipts. There is no obligation to keep a verifier running.

If work continues: implement the single milestone above before expanding scope. A regular, bounded working session is sufficient; the project does not need to occupy every available hour.

Do not change an existing numerical profile or commitment format silently. A change must have a new version and regression vector. Check licensing and data provenance when introducing a scientific dataset. Preserve Michael’s originating credit and distinguish implementation contributions.
