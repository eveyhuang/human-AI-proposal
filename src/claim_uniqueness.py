"""
Claim-level uniqueness analysis for reviews.

The facet battery measures whole-review geometry: it can show that AI reviews are
*positioned* near every human review, but not whether every *point* a human reviewer
makes also appears somewhere in the AI panel. A review is 90% standard assessment
plus, occasionally, one decisive catch ("the sample in Aim 2 cannot power the subgroup
analysis"); whole-document embeddings average that catch away.

This module decomposes reviews into atomic claims (sentences of `strengths_text` /
`weakness_text`), embeds each claim with the SAME encoder and pooling as the prep layer
(BioLinkBERT-large, mean pooling, L2-normalized), and asks, per target proposal and
polarity: is each human claim matched by some claim in the AI panel, and vice versa?

The match threshold is not chosen by hand. It is calibrated on HUMAN-to-HUMAN claim
matching within the same proposal: the distance at which a human claim typically finds
its nearest counterpart in a *different human reviewer's* review of the same proposal.
"Unique" therefore means "farther from the other group than human reviewers typically
are from each other" — the same yardstick logic as the interleaving statistics.

All functions are pure except `embed_claims`, which delegates to the prep layer's
`embed_texts` so the encoder, pooling, batching and truncation are identical by
construction.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd


# Sentence boundary: terminator + space + capital/digit, protecting common abbreviations
# and decimals ("e.g.", "i.e.", "Fig. 2", "vs.", "p = 0.03", "Aim 1.").
# The lookbehinds must include the terminating period, since they are evaluated at the
# position after it (e.g. "Fig." -> the three characters before the split point are "ig.").
_ABBREV = (r"(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bvs\.)(?<!\bcf\.)(?<!\bFig\.)(?<!\bDr\.)"
           r"(?<!\bal\.)(?<!\bAim\.)(?<!\bNo\.)(?<!\bapprox\.)(?<!\bTable\.)(?<!\bRef\.)")
_SPLIT_RE = re.compile(rf"{_ABBREV}(?<=[.!?])\s+(?=[A-Z0-9])")
_BULLET_RE = re.compile(r"^\s*(?:[-•*•]|\(?\d{1,2}[.)])\s+")

MIN_CLAIM_WORDS = 4


def atomize(text: str, *, min_words: int = MIN_CLAIM_WORDS) -> List[str]:
    """Split one review field into atomic claims (sentences / bullet items).

    Bullet and numbered-list markers are stripped; fragments shorter than
    `min_words` are dropped (headers, "Strengths:", stray tokens).
    """
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return []
    raw = str(text).replace("\r", "\n")
    pieces: List[str] = []
    for line in raw.split("\n"):
        line = _BULLET_RE.sub("", line).strip()
        if not line:
            continue
        pieces.extend(p.strip() for p in _SPLIT_RE.split(line))
    return [p for p in pieces if len(p.split()) >= min_words]


def build_claim_frame(
    master: pd.DataFrame,
    *,
    fields: Sequence[str] = ("strengths_text", "weakness_text"),
    min_words: int = MIN_CLAIM_WORDS,
) -> pd.DataFrame:
    """Long frame of atomic claims: one row per (review, field, claim index)."""
    rows: List[Dict[str, Any]] = []
    for _, r in master.iterrows():
        for field in fields:
            if field not in master.columns:
                continue
            for j, claim in enumerate(atomize(r[field], min_words=min_words)):
                rows.append({
                    "review_uid": str(r["review_uid"]),
                    "target_proposal_uid": str(r["target_proposal_uid"]),
                    "review_source": r["review_source"],
                    "source_family": r.get("source_family", ""),
                    "polarity": "strength" if field.startswith("strength") else "weakness",
                    "field": field,
                    "claim_idx": j,
                    "claim_text": claim,
                    "n_words": len(claim.split()),
                })
    return pd.DataFrame(rows)


def embed_claims(texts: Sequence[str], *, batch_size: int = 16) -> np.ndarray:
    """Embed claims with the prep layer's encoder (BioLinkBERT-large, mean pooling).

    Delegates to `prepare_proposals_for_analysis.embed_texts` so the model, pooling,
    truncation and batching match the review bundles exactly; rows are L2-normalized
    afterwards, as the prep layer does for its stored bundles.
    """
    from prepare_proposals_for_analysis import embed_texts

    emb = embed_texts(list(texts), pooling="mean", batch_size=batch_size)
    arr = np.asarray(emb, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1.0
    return arr / norms


def _cos_dist(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    return 1.0 - np.clip(np.asarray(A) @ np.asarray(B).T, -1.0, 1.0)


def human_human_reference(
    claims: pd.DataFrame,
    X: np.ndarray,
    *,
    polarity: str | None = None,
) -> np.ndarray:
    """Nearest-claim distances between DIFFERENT human reviewers of the same proposal.

    This is the calibration set: how far a human claim typically sits from the closest
    claim made by another human reviewing the same proposal.
    """
    out: List[float] = []
    sub = claims if polarity is None else claims[claims["polarity"].eq(polarity)]
    hum = sub[sub["review_source"].eq("human")]
    for uid, grp in hum.groupby("target_proposal_uid"):
        uids = grp["review_uid"].unique()
        if len(uids) < 2:
            continue
        for ru in uids:
            mine = grp.index[grp["review_uid"].eq(ru)].to_numpy()
            others = grp.index[grp["review_uid"].ne(ru)].to_numpy()
            if not len(mine) or not len(others):
                continue
            D = _cos_dist(X[mine], X[others])
            out.extend(D.min(axis=1).tolist())
    return np.asarray(out, dtype=float)


def coverage_rates(
    claims: pd.DataFrame,
    X: np.ndarray,
    *,
    threshold: float,
    ai_family: str | None = None,
    polarity: str | None = None,
) -> Dict[str, float]:
    """Per-side claim coverage between the human panel and an AI panel of the same proposal.

    Returns the share of human claims with no AI claim within `threshold`
    ("human-unique"), the mirror share for AI claims, the median nearest-claim
    distances in both directions, and the claim counts.
    """
    sub = claims if polarity is None else claims[claims["polarity"].eq(polarity)]
    h_un, a_un, d_ha, d_ah = [], [], [], []
    n_h = n_a = 0
    for uid, grp in sub.groupby("target_proposal_uid"):
        hi = grp.index[grp["review_source"].eq("human")].to_numpy()
        ai_mask = grp["review_source"].eq("ai")
        if ai_family:
            ai_mask &= grp["source_family"].eq(ai_family)
        ai = grp.index[ai_mask].to_numpy()
        if not len(hi) or not len(ai):
            continue
        D = _cos_dist(X[hi], X[ai])          # (human claims, AI claims)
        nn_h = D.min(axis=1)                 # each human claim -> nearest AI claim
        nn_a = D.min(axis=0)                 # each AI claim -> nearest human claim
        h_un.append(nn_h > threshold)
        a_un.append(nn_a > threshold)
        d_ha.append(nn_h)
        d_ah.append(nn_a)
        n_h += len(hi)
        n_a += len(ai)
    if not h_un:
        return {"human_unique_rate": np.nan, "ai_unique_rate": np.nan,
                "human_to_ai_median": np.nan, "ai_to_human_median": np.nan,
                "n_human_claims": 0, "n_ai_claims": 0}
    h_un = np.concatenate(h_un); a_un = np.concatenate(a_un)
    return {
        "human_unique_rate": float(h_un.mean()),
        "ai_unique_rate": float(a_un.mean()),
        "human_to_ai_median": float(np.median(np.concatenate(d_ha))),
        "ai_to_human_median": float(np.median(np.concatenate(d_ah))),
        "n_human_claims": int(n_h),
        "n_ai_claims": int(n_a),
    }


def coverage_rates_exact_n(
    claims: pd.DataFrame,
    X: np.ndarray,
    *,
    threshold: float,
    panels: Dict[str, Dict[str, Any]],
    review_uids: Sequence[str],
    ai_key: str = "pooled",
    model: str | None = None,
    polarity: str | None = None,
    max_panels: int = 200,
    seed: int = 42,
) -> Dict[str, float]:
    """Claim coverage at EXACT-N matched panel size (spec 11.1).

    `coverage_rates` compares the human panel against every AI review of a proposal
    (m human reviews vs 15 AI reviews), which biases both rates: more AI claims give
    each human claim more chances to be matched (human-unique understated) while
    forcing more AI claims to go unmatched (AI-unique overstated). This version draws
    the AI side from the SAME enumerated exact-n panels used by every facet metric —
    m AI reviews for a proposal with m human reviews — and averages the rates over
    panels, so the two sides are compared at equal panel size.

    `panels` is the `review_panels_exact_n.pkl` payload; `review_uids` is the review
    master's uid order (the panel indices are positional against it).
    """
    sub = claims if polarity is None else claims[claims["polarity"].eq(polarity)]
    rng = np.random.default_rng(seed)
    uid_of = {i: str(u) for i, u in enumerate(review_uids)}
    h_rates, a_rates, d_ha, d_ah, n_h_all, n_a_all, n_panels = [], [], [], [], [], [], 0

    for uid, grp in sub.groupby("target_proposal_uid"):
        payload = panels.get(str(uid))
        if payload is None:
            continue
        combos = payload["pooled"] if ai_key == "pooled" else payload["per_model"].get(str(model), [])
        if not combos:
            continue
        if len(combos) > max_panels:
            pick = rng.choice(len(combos), size=max_panels, replace=False)
            combos = [combos[i] for i in pick]
        hi = grp.index[grp["review_source"].eq("human")].to_numpy()
        if not len(hi):
            continue
        by_uid = {u: g.index.to_numpy() for u, g in grp.groupby("review_uid")}
        for combo in combos:
            ai = np.concatenate([by_uid.get(uid_of[int(i)], np.array([], dtype=int)) for i in combo]) \
                 if len(combo) else np.array([], dtype=int)
            ai = ai.astype(int)
            if not len(ai):
                continue
            D = _cos_dist(X[hi], X[ai])
            nn_h = D.min(axis=1)
            nn_a = D.min(axis=0)
            h_rates.append(float((nn_h > threshold).mean()))
            a_rates.append(float((nn_a > threshold).mean()))
            d_ha.append(float(np.median(nn_h)))
            d_ah.append(float(np.median(nn_a)))
            n_h_all.append(len(hi))
            n_a_all.append(len(ai))
            n_panels += 1

    if not h_rates:
        return {"human_unique_rate": np.nan, "ai_unique_rate": np.nan,
                "human_to_ai_median": np.nan, "ai_to_human_median": np.nan,
                "n_human_claims": 0, "n_ai_claims": 0, "n_panels": 0}
    return {
        "human_unique_rate": float(np.mean(h_rates)),
        "ai_unique_rate": float(np.mean(a_rates)),
        "human_to_ai_median": float(np.mean(d_ha)),
        "ai_to_human_median": float(np.mean(d_ah)),
        "n_human_claims": float(np.mean(n_h_all)),
        "n_ai_claims": float(np.mean(n_a_all)),
        "n_panels": int(n_panels),
    }


def unique_claim_examples(
    claims: pd.DataFrame,
    X: np.ndarray,
    *,
    threshold: float,
    side: str = "human",
    top_k: int = 12,
    polarity: str | None = None,
) -> pd.DataFrame:
    """The most distant unmatched claims — the qualitative check on the numbers.

    Embedding-based matching has its own errors, so any published uniqueness rate
    should be accompanied by a hand-read sample; this returns the candidates.
    """
    sub = claims if polarity is None else claims[claims["polarity"].eq(polarity)]
    recs: List[Dict[str, Any]] = []
    for uid, grp in sub.groupby("target_proposal_uid"):
        hi = grp.index[grp["review_source"].eq("human")].to_numpy()
        ai = grp.index[grp["review_source"].eq("ai")].to_numpy()
        if not len(hi) or not len(ai):
            continue
        D = _cos_dist(X[hi], X[ai])
        if side == "human":
            src_idx, nn = hi, D.min(axis=1)
        else:
            src_idx, nn = ai, D.min(axis=0)
        for k, d in zip(src_idx, nn):
            if d > threshold:
                recs.append({"target_proposal_uid": uid, "nn_distance": float(d),
                             "polarity": claims.at[k, "polarity"],
                             "review_uid": claims.at[k, "review_uid"],
                             "source": claims.at[k, "review_source"],
                             "family": claims.at[k, "source_family"],
                             "claim_text": claims.at[k, "claim_text"]})
    if not recs:
        return pd.DataFrame(columns=["target_proposal_uid", "nn_distance", "polarity",
                                     "review_uid", "source", "family", "claim_text"])
    return pd.DataFrame(recs).sort_values("nn_distance", ascending=False).head(top_k).reset_index(drop=True)


__all__ = ["atomize", "build_claim_frame", "embed_claims", "human_human_reference",
           "coverage_rates", "unique_claim_examples", "MIN_CLAIM_WORDS"]
