# Mutual-best early finalization and Relaxed Communications

Michael Emanuel Glover's proposal: examine both the best label for each object and the best object for each label. When a sufficiently strong mutual match persists for three fresh iterations, consider finalizing it early to avoid repeating settled work.

The original C++ `assign()` postpass in `Code/relaxation-labeling/cpp/source/relax/relax.cpp` (approximately lines 218–278) selects row winners and resolves competing ordinary-label assignments by strength. The implementation here moves mutual-support eligibility into the iteration loop. The original three-iteration mechanism has not been located in the inspected source; this is a new implementation of the described idea.

## Read the work

- [Relaxed Communications: theory note](RELAXED-COMMUNICATIONS.md): countably many messages, convergence under explicit assumptions, finite approximations, and the possibility that an infinite candidate set has no best object.
- [Measured finite pilot](REPORT.md): 36 synthetic instances, three policies, three timing repetitions.
- [Larger exploratory probe](LARGE-PROBE.md): one seed at each of 48 and 64 objects, including an explicit aggressive preset.
- [`hrl/finalization.py`](../hrl/finalization.py): opt-in implementation.
- [`tests/test_finalization.py`](../tests/test_finalization.py): trajectory equivalence, ties, cached influence, delayed reversal, reopening, and result semantics.

## Use

```python
from hrl import MutualBestLabeler, FinalizationPolicy

# C and prior describe a fixed one-to-one correspondence problem.
result = MutualBestLabeler(
    C, prior, one_to_one=True,
    policy=FinalizationPolicy.aggressive(),
).run()

settled_pairs = [(i, result.assignments[i])
                 for i in range(len(result.assignments)) if result.finalized[i]]
print(result.stop_reason, result.full_update_residual)
```

Use ordinary relaxation labeling for many-to-one classes or meanings. Label reservation is appropriate to identities, not a general semantic vocabulary. The compatibility tensor is copied and made read-only: new evidence requires a new instance. Call `run()` once per instance.

## Eligibility and commitment

A candidate must be the unique raw-support winner both across its object's labels and across the active objects competing for its unreserved label. It must also win in updated strength and pass strength, strength-gap, normalized support-gap, and row-change gates. Three consecutive eligible sweeps are required by default; a broken condition resets persistence. Ties are rejected. Noise never finalizes or reserves a label.

The default audited policy requires strength ≥ .45, strength gap ≥ .05, row and column support margins ≥ .05, and maximum row change ≤ .03. Audits occur every six sweeps; a one-step change above .06 can release a lock. The aggressive preset lowers these gates, retaining three sweeps and strict tie rejection; it audits every eight sweeps. Neither preset supplies a calibrated error guarantee.

Finalization freezes the whole soft row. Its influence on active objects is cached, rather than removed or rounded to a one-hot assignment. Full audits can reopen locks when fresh support invalidates eligibility or indicates excessive change. Audits can still miss later reversals. Permanent mode is useful as an experimental comparison and demonstrably fails on the delayed-reversal fixture.

`assignments` includes provisional argmax labels for unfinalized rows, including tied rows. Inspect `finalized` before treating a pair as settled. Finalized ordinary labels are unique; provisional labels need not be.

`converged` means the full unfrozen one-step residual is below tolerance. `assignment_converged` means every row has finalized. Stopping because active rows have reached a fixed point conditional on frozen rows is reported separately as `active_fixed_point_with_finalized_assignments`. These conditions are not interchangeable, and none certifies ground-truth correctness.

## Reproduce

From the repository root, run these commands sequentially to avoid contaminating timings:

```sh
python3 -m pytest tests -q
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 mutual-finalization/experiment.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 mutual-finalization/large_experiment.py
```

Reduced arithmetic need not improve time: cache packing, audits, and bookkeeping can dominate smaller problems. The implementation retains the dense compatibility tensor and can allocate an additional packed active matrix; it does not solve dense storage or input-construction costs. The finite experiments evaluate this scheduler, not the distinct contraction operator proposed in the communication theory note.
