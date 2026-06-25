"""Natural-language-inference agreement — a real NLP front-end for consensus.

The consensus engine (:mod:`hrl.consensus`) turns an agreement matrix into a
truth labeling. The *only* model-dependent part is producing that matrix from
text. This module does it with a real **NLI** model: for each ordered pair of
claims it reads the entailment / neutral / contradiction distribution and
collapses it to a signed agreement score

    agree(a, b) = P(entail | a, b) - P(contradict | a, b)   in [-1, +1]

averaged over both directions for symmetry. Entailing claims push toward the
same truth value, contradicting claims toward opposite ones — exactly what the
relaxation kernel consumes.

NLI judges *textual* inference, so it is strongest when claims share vocabulary
and differ on a key assertion — the way sentences in one paper relate. For
abstract, world-knowledge equivalences, use the Claude LLM-judge backend in
:mod:`hrl.llm_judge` instead. The model loads lazily, so importing ``hrl`` stays
numpy-only; ``transformers`` + ``torch`` are needed only when you actually run
this.
"""
from __future__ import annotations

import numpy as np

__all__ = ["NLIAgreement"]

DEFAULT_MODEL = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"


class NLIAgreement:
    """Callable that turns a list of claims into a signed agreement matrix.

    Parameters
    ----------
    model:
        Any HuggingFace 3-way (entailment/neutral/contradiction) NLI model.
    threshold:
        Agreement scores with magnitude below this are zeroed (dropped as
        too weak/uncertain to be an edge). Default ``0.15``.
    device:
        Passed to the transformers pipeline (e.g. ``0`` for the first GPU,
        ``-1`` for CPU). ``None`` lets transformers choose.
    batch_size:
        Pipeline batch size for the pairwise inferences.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        threshold: float = 0.15,
        device: int | None = None,
        batch_size: int = 16,
    ) -> None:
        self.model_name = model
        self.threshold = float(threshold)
        self.device = device
        self.batch_size = int(batch_size)
        self._pipe = None  # lazy

    def _pipeline(self):
        if self._pipe is None:
            from transformers import pipeline  # imported lazily on first use
            kwargs = {"model": self.model_name, "top_k": None}
            if self.device is not None:
                kwargs["device"] = self.device
            self._pipe = pipeline("text-classification", **kwargs)
        return self._pipe

    @staticmethod
    def _signed(scores: dict) -> float:
        s = {k.lower(): v for k, v in scores.items()}
        return float(s.get("entailment", 0.0) - s.get("contradiction", 0.0))

    def __call__(self, claims: list[str]) -> np.ndarray:
        """Return the ``[n, n]`` symmetric agreement matrix for ``claims``."""
        n = len(claims)
        if n < 2:
            return np.zeros((n, n))

        # every ordered pair (premise -> hypothesis), i != k
        pairs, index = [], []
        for i in range(n):
            for k in range(n):
                if i != k:
                    pairs.append({"text": claims[i], "text_pair": claims[k]})
                    index.append((i, k))

        outputs = self._pipeline()(pairs, batch_size=self.batch_size)

        directed = np.zeros((n, n))
        for (i, k), scores in zip(index, outputs):
            directed[i, k] = self._signed({d["label"]: d["score"] for d in scores})

        # symmetrize (average a->b and b->a) and threshold
        agreement = np.zeros((n, n))
        for i in range(n):
            for k in range(i + 1, n):
                a = 0.5 * (directed[i, k] + directed[k, i])
                if abs(a) >= self.threshold:
                    agreement[i, k] = agreement[k, i] = a
        return agreement
