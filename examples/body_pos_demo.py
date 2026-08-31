"""Body-position labeling from a wearable accelerometer — a night of sleep.

Run: ``python examples/body_pos_demo.py``

A torso-worn accelerometer reports the gravity vector as the sleeper holds a
posture, rolls over, holds the next. Relaxation labeling assigns each reading a
canonical body position; the absolute-fit *prior* pins the posture, relative
geometry + temporal smoothing keep a stretch self-consistent, and the *noise
label* quarantines the roll-over movements. Saves ``body_pos_session.png`` if
matplotlib is present.
"""
import numpy as np

from hrl import classify_session, synthetic_session, POSITION_NAMES


def main():
    readings, times, truth = synthetic_session(seed=3)
    result = classify_session(readings, times=times)
    asg = result.assignments

    real = truth >= 0
    real_ok = int(np.sum(asg[real] == truth[real]))
    real_total = int(np.sum(real))
    move = ~real
    move_ok = int(np.sum(asg[move] == -1))
    move_total = int(np.sum(move))

    name = lambda j: "— movement → noise" if j < 0 else POSITION_NAMES[j]

    print("=" * 62)
    print("Body-position labeling — relaxation labeling over a night")
    print("=" * 62)
    print(f"readings              : {len(readings)}")
    print(f"posture accuracy      : {real_ok}/{real_total} correct "
          f"({100 * real_ok / real_total:.1f}%)")
    print(f"roll-overs -> noise   : {move_ok}/{move_total} quarantined")
    print(f"converged             : {result.converged} in {result.iterations} iterations")
    print("\n  t   truth        assigned        confidence")
    print("  " + "-" * 50)
    for t in range(len(readings)):
        flag = "" if (asg[t] == truth[t] or (truth[t] < 0 and asg[t] < 0)) else "  <-- miss"
        print(f"  {int(times[t]):>2}  {name(truth[t]):<12} {name(asg[t]):<16}"
              f"{result.confidence[t]:.2f}{flag}")
    print("\nThe prior is absolute fit (which direction is gravity?), geometry +")
    print("time keep each stretch consistent, and the noise label eats the rolls.")

    _maybe_plot(times, truth, asg, result.confidence)


def _maybe_plot(times, truth, asg, confidence):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("\n(matplotlib not installed — skipping the timeline plot)")
        return

    n_lab = len(POSITION_NAMES)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    colors = plt.cm.tab10(np.linspace(0, 1, n_lab))

    for t, (a, c) in enumerate(zip(asg, confidence)):
        if a < 0:
            ax.scatter(times[t], n_lab, marker="x", c="0.55", s=60, zorder=3)
        else:
            ax.scatter(times[t], a, c=[colors[a]], s=80 * (0.4 + 0.6 * c),
                       edgecolors="white", linewidths=0.8, zorder=3)
    # faint truth track
    for t, tr in enumerate(truth):
        if tr >= 0:
            ax.scatter(times[t], tr, facecolors="none", edgecolors="0.7", s=130, zorder=1)

    ax.set_yticks(list(range(n_lab)) + [n_lab])
    ax.set_yticklabels(POSITION_NAMES + ["noise"])
    ax.set_xlabel("time (samples)")
    ax.set_title("Sleep posture, labeled by relaxation (rings = truth)")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "body_pos_session.png")
    fig.savefig(out, dpi=120)
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
