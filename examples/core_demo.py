"""A 60-second tour of the relaxation-labeling core.

Run: ``python examples/core_demo.py``

Shows the three things the core gives you:
  1. correspondence  — recover which measured point is which model marker,
  2. the noise label — quarantine an outlier instead of mislabeling it,
  3. respected priors — let a weak prior settle an otherwise-tied field.
"""
import numpy as np

from hrl import RelaxationLabeler, pairwise_distance_compatibility

MODEL = np.array([[0.0, 0.0], [3.0, 0.0], [0.0, 1.0], [1.0, 2.0]])
NAMES = ["head", "l-shoulder", "r-shoulder", "pelvis"]


def _rotate(points, degrees):
    t = np.radians(degrees)
    r = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return points @ r.T


def demo_correspondence():
    print("\n1) MARKER CORRESPONDENCE  (motion-capture flavor)")
    perm = np.array([2, 0, 3, 1])
    rng = np.random.default_rng(0)
    objects = _rotate(MODEL, 37.0)[perm] + np.array([5.0, -2.0])
    objects += rng.normal(scale=0.01, size=objects.shape)

    compat = pairwise_distance_compatibility(objects, MODEL, sigma=0.05)
    result = RelaxationLabeler(compat, max_iterations=100).run()

    print(f"   converged in {result.iterations} iterations")
    for i, (label, conf) in enumerate(zip(result.assignments, result.confidence)):
        truth = "OK" if label == perm[i] else "WRONG"
        print(f"   measured point {i} -> {NAMES[label]:<11} ({conf:.2f})  [{truth}]")


def demo_noise():
    print("\n2) NOISE LABEL  (an outlier is quarantined, not mislabeled)")
    perm = np.array([2, 0, 3, 1])
    rng = np.random.default_rng(1)
    real = _rotate(MODEL, 37.0)[perm] + np.array([5.0, -2.0])
    real += rng.normal(scale=0.01, size=real.shape)
    objects = np.vstack([real, [[42.0, 17.0]]])  # a spurious 5th detection

    compat = pairwise_distance_compatibility(objects, MODEL, sigma=0.05)
    result = RelaxationLabeler(compat, noise=True, max_iterations=100).run()

    for i, label in enumerate(result.assignments):
        name = "** NOISE / unlabeled **" if label == -1 else NAMES[label]
        print(f"   measured point {i} -> {name}")


def demo_prior():
    print("\n3) RESPECTED PRIOR  (a weak nudge settles a perfect tie)")
    compat = np.zeros((2, 2, 2, 2))
    for i in range(2):
        for k in range(2):
            if i != k:
                for j in range(2):
                    for l in range(2):
                        compat[i, j, k, l] = 1.0 if j != l else 0.0

    for nudge, prior in (("toward label 0", [[0.9, 0.1], [0.5, 0.5]]),
                         ("toward label 1", [[0.1, 0.9], [0.5, 0.5]])):
        result = RelaxationLabeler(compat, np.array(prior), prior_strength=0.7).run()
        print(f"   prior nudges object 0 {nudge:<15} -> assignment {result.assignments.tolist()}")


if __name__ == "__main__":
    print("=" * 60)
    print("Hierarchical Relaxation Labeling — core demo")
    print("=" * 60)
    demo_correspondence()
    demo_noise()
    demo_prior()
    print("\nSame engine, three behaviors. Swap the kernel, change the world.\n")
