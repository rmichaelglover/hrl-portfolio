"""Real NLP -> consensus: relax claims from prose to vtrue / ish / vfalse.

Run: ``python examples/paper_consensus_demo.py``    (needs the `nli` extra)

Raw text is split into claims, a real **NLI model** reads every pair to build
the agreement/contradiction web, one trusted observation anchors the field, and
relaxation labeling settles every claim onto a truth value. No hand-authored
agreement matrix — the structure is inferred from language.
"""
import numpy as np

from hrl.consensus import anchor_prior, extract_claims, relax_truth, truth_report, VTRUE
from hrl.nli import NLIAgreement

# A small conflicting-evidence digest (the kind of contradictory claims you'd
# pull across several papers on one question).
DIGEST = """
Compound X significantly reduces patient mortality.
In an independent replication trial, compound X lowered mortality.
Compound X reduces mortality in treated patients.
Compound X has no effect on patient mortality.
Patients treated with compound X showed no survival benefit.
Compound X increases the risk of death in the treatment group.
Compound X was well tolerated, with only mild side effects.
"""

ANCHOR = 1  # trust the independent replication (claim index 1) as vtrue


def main():
    claims = extract_claims(DIGEST)
    print("=" * 72)
    print("Paper consensus — claims relaxed to truth via a real NLI model")
    print("=" * 72)
    print(f"extracted {len(claims)} claims; loading NLI model "
          "(first run downloads weights)...\n")

    agreement = NLIAgreement(threshold=0.15)(claims)

    print("NLI-inferred relations (entail = +, contradict = -):")
    for i in range(len(claims)):
        for k in range(i + 1, len(claims)):
            if agreement[i, k]:
                rel = "agree   " if agreement[i, k] > 0 else "contradict"
                print(f"  c{i} {rel} c{k}   ({agreement[i, k]:+.2f})")

    prior = anchor_prior(len(claims), {ANCHOR: VTRUE}, strength=0.9)
    report = truth_report(relax_truth(agreement, prior, prior_strength=0.4))

    print(f"\nanchored claim c{ANCHOR} as a trusted observation (vtrue):\n")
    for i, (claim, r) in enumerate(zip(claims, report)):
        tag = "  <- anchor" if i == ANCHOR else ""
        print(f"  [{r['truth']:>6} {r['score']:+.2f}]  c{i}: {claim}{tag}")

    print("\nThe NLI model supplied the web; relaxation propagated truth from one")
    print("anchor across it. Swap NLIAgreement for hrl.llm_judge to scale to "
          "whole papers.")


if __name__ == "__main__":
    main()
