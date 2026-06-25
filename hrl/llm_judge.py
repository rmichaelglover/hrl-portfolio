"""Claude LLM-judge — the high-capability NLP front-end for consensus.

An NLI model (:mod:`hrl.nli`) judges *textual* inference between short claims.
For abstract, world-knowledge agreement — and for pulling atomic claims out of
a whole paper in the first place — a frontier LLM is far stronger. This module
uses the Claude API for both:

* :func:`extract_claims_llm` — turn raw paper text into a list of atomic claims,
* :class:`LLMAgreement` — judge every related pair as entail / contradict with a
  strength, assembled into the same signed agreement matrix the consensus
  engine consumes.

Opt-in: requires the ``anthropic`` package and credentials (``ANTHROPIC_API_KEY``
or an ``ant auth login`` profile). The engine itself stays numpy-only; this is
imported only when you choose the LLM backend.
"""
from __future__ import annotations

import json

import numpy as np

__all__ = ["LLMAgreement", "extract_claims_llm", "DEFAULT_MODEL"]

DEFAULT_MODEL = "claude-opus-4-8"

_CLAIMS_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["claims"],
    "additionalProperties": False,
}

_RELATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                    "relation": {"type": "string", "enum": ["entail", "contradict"]},
                    "strength": {"type": "number"},
                },
                "required": ["a", "b", "relation", "strength"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["relations"],
    "additionalProperties": False,
}


def _client(client=None):
    if client is not None:
        return client
    import anthropic  # imported lazily so the package is an optional dependency
    return anthropic.Anthropic()


def _json_response(client, model, prompt, schema, max_tokens=4096):
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def extract_claims_llm(paper_text: str, *, model: str = DEFAULT_MODEL, client=None) -> list[str]:
    """Extract atomic, individually-checkable claims from a paper / abstract."""
    prompt = (
        "Extract the distinct, atomic factual claims asserted in the text below. "
        "Each claim should be a single self-contained statement that could be "
        "independently judged true or false. Do not include hedges, citations, "
        "or methodology — just the substantive claims.\n\n"
        f"TEXT:\n{paper_text}"
    )
    return _json_response(_client(client), model, prompt, _CLAIMS_SCHEMA)["claims"]


class LLMAgreement:
    """Callable that turns claims into a signed agreement matrix via Claude.

    ``agreement[i, k] = +strength`` if i and k entail each other, ``-strength``
    if they contradict, ``0`` if unrelated — the same convention as
    :class:`hrl.nli.NLIAgreement`, so it drops straight into ``relax_truth``.
    """

    def __init__(self, *, model: str = DEFAULT_MODEL, client=None) -> None:
        self.model = model
        self._client = client

    def __call__(self, claims: list[str]) -> np.ndarray:
        n = len(claims)
        agreement = np.zeros((n, n))
        if n < 2:
            return agreement

        listing = "\n".join(f"{i}: {c}" for i, c in enumerate(claims))
        prompt = (
            "Below are numbered claims. For every PAIR of claims that are "
            "logically related, decide whether one entails/supports the other "
            "(`entail`) or they contradict (`contradict`), with a strength in "
            "0..1. Omit pairs that are unrelated. Use each claim's index.\n\n"
            f"CLAIMS:\n{listing}"
        )
        data = _json_response(_client(self._client), self.model, prompt, _RELATIONS_SCHEMA)

        for rel in data["relations"]:
            i, k = int(rel["a"]), int(rel["b"])
            if i == k or not (0 <= i < n and 0 <= k < n):
                continue
            s = float(np.clip(rel["strength"], 0.0, 1.0))
            value = s if rel["relation"] == "entail" else -s
            agreement[i, k] = agreement[k, i] = value
        return agreement
