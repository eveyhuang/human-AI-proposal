"""
Decision-outcome analysis for the gate-keeping side: can a review panel reproduce the
competition's ACTUAL funding decisions?

Every other gate-keeping metric measures review *text* or within-panel score spread. This
one uses the real outcome — the funding ranking / fund-or-not decision for all proposals —
as ground truth, and asks whether a panel's mean score reproduces it, and whether adding
reviewers helps (the error-cancellation / Condorcet question).

The mechanism it exposes: AI panel scores barely vary *across* proposals (the "central
blanket" / score-convergence finding, in the currency of the decision), so an AI panel has
no measurable ability to discriminate proposals — it rates everything ~4 and lands at chance.

**Precision, not just direction.** `funding_auc_inference` attaches a stratified bootstrap
95% CI and a label-permutation p to every AUC, because "AUC = 0.50" at n = 23 is ambiguous
between a demonstrated null and an underpowered one. On this data the intervals run ~+/-0.25,
so the honest reading is *absence of evidence* (no funding signal detectable, permutation
p = .84-.99) rather than a proven null; the Human AUC is likewise not separable from chance
(0.77, CI 0.48-1.00, p = .09). Consumers should quote the interval alongside the point.

**Honest caveat, baked into every consumer:** the funding ranking was set by the human
review process, so the human curve has a built-in advantage. The load-bearing result is
therefore the AI side alone — *an AI panel's scores show no funding signal* — not a
human-vs-AI accuracy gap, which these intervals do not establish.

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


def funding_auc_inference(means: Mapping[str, float], funded: Mapping[str, bool], *,
                          n_boot: int = 10_000, n_perm: int = 10_000,
                          seed: int = 3) -> Dict[str, Any]:
    """Point estimate, bootstrap CI, and permutation p-value for the funding AUC.

    The AUC alone cannot say whether "0.50" means "demonstrably at chance" or "too few
    proposals to tell" — with 23 proposals both readings are live. Two devices separate
    them, and neither assumes a distribution:

    * **Stratified bootstrap CI.** Funded and not-funded proposals are resampled *within
      class* with replacement, holding both class sizes fixed, so every draw keeps a
      computable AUC (an unstratified draw can empty a class). The 2.5/97.5 percentiles
      of the resulting AUCs are the interval. It answers "how much would this AUC move
      with a different sample of proposals?"
    * **Label permutation.** The funded/not-funded labels are shuffled across the scored
      proposals, holding the scores fixed, and the AUC recomputed. The two-sided p-value
      is the share of shuffles whose |AUC - 0.5| is at least the observed |AUC - 0.5|.
      It answers "could this AUC have arisen from scores carrying no outcome signal?"

    Returns point/ci_lo/ci_hi/p_perm/n_funded/n_not_funded (all NaN-safe: if either class
    is empty the AUC is undefined and every field comes back NaN / 0).
    """
    us = [u for u in means if np.isfinite(means[u]) and u in funded]
    y = np.asarray([bool(funded[u]) for u in us])
    s = np.asarray([means[u] for u in us], dtype=float)
    pos_idx, neg_idx = np.flatnonzero(y), np.flatnonzero(~y)
    n_pos, n_neg = len(pos_idx), len(neg_idx)
    out: Dict[str, Any] = {"point": np.nan, "ci_lo": np.nan, "ci_hi": np.nan,
                           "p_perm": np.nan, "n_funded": n_pos, "n_not_funded": n_neg}
    if not n_pos or not n_neg:
        return out

    def _auc(scores: np.ndarray, labels: np.ndarray) -> float:
        # Vectorized twin of funding_auc() above (same tie handling, 0.5 credit); the
        # resampling loops call this ~20,000 times per group, so it broadcasts instead
        # of iterating over the pos x neg pairs.
        pos, neg = scores[labels], scores[~labels]
        d = pos[:, None] - neg[None, :]
        return float((np.count_nonzero(d > 0) + 0.5 * np.count_nonzero(d == 0)) / d.size)

    out["point"] = _auc(s, y)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        take = np.concatenate([rng.choice(pos_idx, n_pos, replace=True),
                               rng.choice(neg_idx, n_neg, replace=True)])
        boot[b] = _auc(s[take], y[take])
    out["ci_lo"], out["ci_hi"] = (float(x) for x in np.percentile(boot, [2.5, 97.5]))

    obs_dev = abs(out["point"] - 0.5)
    hits = 0
    for _ in range(n_perm):
        hits += abs(_auc(s, rng.permutation(y)) - 0.5) >= obs_dev - 1e-12
    out["p_perm"] = float((hits + 1) / (n_perm + 1))
    return out


def _auc_arrays(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUC from parallel score/label arrays; ties get 0.5 credit (as funding_auc)."""
    pos, neg = scores[labels], scores[~labels]
    if not pos.size or not neg.size:
        return np.nan
    d = pos[:, None] - neg[None, :]
    return float((np.count_nonzero(d > 0) + 0.5 * np.count_nonzero(d == 0)) / d.size)


def matched_funding_auc(master: pd.DataFrame, funded: Mapping[str, bool],
                        *, source: str = "ai", model: str = None,
                        panel_sizes: Mapping[str, int] = None, uids: Sequence[str] = None,
                        n_draws: int = 2_000, n_boot: int = 2_000, n_perm: int = 2_000,
                        seed: int = 3) -> Dict[str, Any]:
    """Funding AUC for AI panels drawn at the HUMAN panel size, on the HUMAN proposal set.

    `build_decision_outcome`'s headline AUC pools all 15 AI reviews over all 23 proposals,
    while the human AUC uses 1-4 scored reviews over the 14 proposals that have any. That
    asymmetry is fine for the AI-side-alone question ("do AI scores carry funding signal?")
    but it is NOT a fair human-vs-AI contrast: the panels differ in size, the proposal sets
    differ, and the human set is 11/14 cohort y2. This function removes all three, matching
    the exact-n convention used everywhere else in notebook 03 (spec 11.1).

    For each proposal in `uids`, an AI panel of exactly `panel_sizes[uid]` reviews is drawn
    without replacement from that proposal's AI reviews (pooled, or one `model`), the panel
    mean is taken, and the AUC is computed across proposals. That repeats `n_draws` times;
    the point estimate is the mean AUC over draws. The CI resamples proposals within class
    (stratified bootstrap) *and* redraws panels, so it carries both sources of uncertainty;
    the permutation p shuffles the funded labels with the scores held fixed.

    Returns point / draw_lo / draw_hi (panel-draw spread only) / ci_lo / ci_hi (proposals +
    draws) / p_perm / n_props / n_funded / n_not_funded / mean_panel_size.
    """
    sub = master[master["review_source"].eq(source)]
    if model is not None:
        sub = sub[sub["source_family"].eq(model)]
    pool = {u: g["overall_score"].dropna().to_numpy(float)
            for u, g in sub.groupby(master["target_proposal_uid"].astype(str))}
    us = [u for u in uids if u in funded and panel_sizes.get(u, 0) >= 1
          and len(pool.get(u, [])) >= panel_sizes[u]]
    y = np.asarray([bool(funded[u]) for u in us])
    sizes = np.asarray([panel_sizes[u] for u in us])
    out: Dict[str, Any] = {"point": np.nan, "draw_lo": np.nan, "draw_hi": np.nan,
                           "ci_lo": np.nan, "ci_hi": np.nan, "p_perm": np.nan,
                           "n_props": len(us), "n_funded": int(y.sum()),
                           "n_not_funded": int((~y).sum()),
                           "mean_panel_size": float(np.mean(sizes)) if len(sizes) else np.nan}
    if not y.any() or y.all():
        return out
    rng = np.random.default_rng(seed)

    def _draw() -> np.ndarray:
        return np.asarray([float(np.mean(rng.choice(pool[u], m, replace=False)))
                           for u, m in zip(us, sizes)])

    draws = np.asarray([_auc_arrays(_draw(), y) for _ in range(n_draws)])
    out["point"] = float(np.nanmean(draws))
    out["draw_lo"], out["draw_hi"] = (float(x) for x in np.nanpercentile(draws, [2.5, 97.5]))

    pos_idx, neg_idx = np.flatnonzero(y), np.flatnonzero(~y)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        take = np.concatenate([rng.choice(pos_idx, len(pos_idx), replace=True),
                               rng.choice(neg_idx, len(neg_idx), replace=True)])
        s = _draw()
        boot[b] = _auc_arrays(s[take], y[take])
    out["ci_lo"], out["ci_hi"] = (float(x) for x in np.nanpercentile(boot, [2.5, 97.5]))

    obs_dev = abs(out["point"] - 0.5)
    hits = sum(abs(_auc_arrays(_draw(), rng.permutation(y)) - 0.5) >= obs_dev - 1e-12
               for _ in range(n_perm))
    out["p_perm"] = float((hits + 1) / (n_perm + 1))
    return out


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
                           seed: int = 3, n_boot_auc: int = 10_000, n_perm_auc: int = 10_000):
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
        auc = funding_auc_inference(means, funded, n_boot=n_boot_auc, n_perm=n_perm_auc, seed=seed)
        summ_rows.append({"group": group, "condition": condition,
                          "funding_auc": funding_auc(means, funded),
                          "funding_auc_ci_lo": auc["ci_lo"], "funding_auc_ci_hi": auc["ci_hi"],
                          "funding_auc_p_perm": auc["p_perm"],
                          "n_funded": auc["n_funded"], "n_not_funded": auc["n_not_funded"],
                          "between_proposal_sd": between_proposal_sd(means),
                          "n_props": int(len(full))})

    _emit("Human", "all", human_master, "human", kmax_human)
    for cond, master in ai_masters.items():
        _emit("AI", cond, master, "ai", kmax_ai)

    return (pd.DataFrame(prop_rows), pd.DataFrame(curve_rows), pd.DataFrame(summ_rows))


__all__ = ["panel_means", "between_proposal_sd", "funding_auc", "funding_auc_inference",
           "matched_funding_auc", "rank_corr_vs_k", "build_decision_outcome"]
