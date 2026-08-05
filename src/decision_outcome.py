"""
Decision-outcome analysis for the gate-keeping side: can a review panel reproduce the
competition's ACTUAL funding decisions?

Every other gate-keeping metric measures review *text* or within-panel score spread. This
one uses the real outcome — the funding ranking / fund-or-not decision for all proposals —
as ground truth, and asks whether a panel's mean score reproduces it, and whether adding
reviewers helps (the error-cancellation / Condorcet question).

The mechanism it exposes: AI panel scores barely vary *across* proposals (the "central
blanket" / score-convergence finding, in the currency of the decision), so an AI panel
cannot discriminate proposals — it rates everything ~4 and lands at chance.

**Honest caveat, baked into every consumer:** the funding ranking was set by the human
review process, so the human curve has a built-in advantage. The load-bearing result is
therefore the AI side alone — *an AI panel cannot reproduce the decisions* — not a
human-vs-AI accuracy gap.

All functions are pure (operate on DataFrames / arrays); no I/O.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

import numpy as np
import pandas as pd


def _scores(master: pd.DataFrame, uid: str, source: str) -> np.ndarray:
    g = master[master["target_proposal_uid"].astype(str).eq(uid)]
    return g[g["review_source"].eq(source)]["overall_score"].dropna().to_numpy(float)


def panel_means(master: pd.DataFrame, source: str, uids: Sequence[str]) -> Dict[str, float]:
    """Per-proposal mean score for one source (NaN if that proposal has no such reviews)."""
    out = {}
    for u in uids:
        s = _scores(master, u, source)
        out[u] = float(np.mean(s)) if len(s) else np.nan
    return out


def between_proposal_sd(means: Mapping[str, float]) -> float:
    """SD of the per-proposal mean scores — how much the panel discriminates proposals.

    Small = the panel rates every proposal about the same (cannot rank).
    """
    v = np.asarray([x for x in means.values() if np.isfinite(x)], dtype=float)
    return float(np.std(v, ddof=1)) if v.size >= 2 else np.nan


def funding_auc(means: Mapping[str, float], funded: Mapping[str, bool]) -> float:
    """AUC for predicting funded vs not from the panel mean (0.5 = chance)."""
    us = [u for u in means if np.isfinite(means[u]) and u in funded]
    y = np.asarray([bool(funded[u]) for u in us])
    s = np.asarray([means[u] for u in us], dtype=float)
    pos, neg = s[y], s[~y]
    if not len(pos) or not len(neg):
        return np.nan
    return float(np.mean([(p > n) + 0.5 * (p == n) for p in pos for n in neg]))


def _spearman(a: Sequence[float], b: Sequence[float]) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.std(ra) == 0 or np.std(rb) == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def rank_corr_vs_k(master: pd.DataFrame, source: str, uids: Sequence[str],
                   rank: Mapping[str, float], *, kmax: int, n_boot: int = 400,
                   seed: int = 3, min_props: int = 6) -> List[Dict[str, Any]]:
    """Spearman(panel-mean, −true-rank) as a function of panel size k.

    At each k, only proposals with >= k reviews of `source` are eligible; the panel mean is
    the mean of k reviewers drawn without replacement, averaged over `n_boot` draws. Higher
    score should track a better (smaller) rank, hence −rank.
    """
    rng = np.random.default_rng(seed)
    rows: List[Dict[str, Any]] = []
    for k in range(1, kmax + 1):
        elig = [u for u in uids if len(_scores(master, u, source)) >= k and np.isfinite(rank.get(u, np.nan))]
        if len(elig) < min_props:
            break
        neg_rank = [-rank[u] for u in elig]
        rhos = []
        for _ in range(n_boot):
            means = [float(np.mean(rng.choice(_scores(master, u, source), k, replace=False))) for u in elig]
            r = _spearman(means, neg_rank)
            if np.isfinite(r):
                rhos.append(r)
        if rhos:
            rows.append({"k": k, "rho": float(np.mean(rhos)),
                         "se": float(np.std(rhos) / np.sqrt(len(rhos))), "n_props": len(elig)})
    return rows


def build_decision_outcome(ai_masters: Mapping[str, pd.DataFrame], human_master: pd.DataFrame,
                           summary: pd.DataFrame, *, kmax_ai: int = 12, kmax_human: int = 4,
                           seed: int = 3):
    """Assemble the three tidy tables for the decision-outcome analysis.

    ai_masters: {condition -> review_master} (AI scores are condition-specific).
    human_master: any condition's review_master (human scores are condition-invariant).
    summary: proposal_review_scores_summary with target_funding / target_ranking.

    Returns (proposal_scores_df, curves_df, summary_df).
    """
    s = summary.copy()
    s["uid"] = s["target_proposal_uid"].astype(str)
    rank = s.set_index("uid")["target_ranking"].to_dict()
    funded = {u: bool(v) for u, v in s.set_index("uid")["target_funding"].items()}
    uids = [u for u in s["uid"] if np.isfinite(rank.get(u, np.nan))]

    prop_rows, curve_rows, summ_rows = [], [], []

    def _emit(group, condition, master, source, kmax):
        means = panel_means(master, source, uids)
        for u in uids:
            prop_rows.append({"group": group, "condition": condition, "uid": u,
                              "panel_mean": means[u], "funded": funded.get(u, np.nan),
                              "rank": rank.get(u, np.nan)})
        for r in rank_corr_vs_k(master, source, uids, rank, kmax=kmax, seed=seed):
            curve_rows.append({"group": group, "condition": condition, **r})
        full = {u: means[u] for u in uids if np.isfinite(means[u])}
        summ_rows.append({"group": group, "condition": condition,
                          "funding_auc": funding_auc(means, funded),
                          "between_proposal_sd": between_proposal_sd(means),
                          "n_props": int(len(full))})

    _emit("Human", "all", human_master, "human", kmax_human)
    for cond, master in ai_masters.items():
        _emit("AI", cond, master, "ai", kmax_ai)

    return (pd.DataFrame(prop_rows), pd.DataFrame(curve_rows), pd.DataFrame(summ_rows))


__all__ = ["panel_means", "between_proposal_sd", "funding_auc", "rank_corr_vs_k",
           "build_decision_outcome"]
