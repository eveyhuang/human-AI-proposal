"""
Lexical-diversity robustness controls (spec 1.9): distinct-n and self-BLEU.

Pure-python implementations with no dependencies beyond numpy, so the lexical
control cannot be blocked by an NLTK install. Inputs are pre-tokenized texts
(lists of lowercase tokens).
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Tuple

import numpy as np


def _ngrams(tokens: Sequence[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def distinct_n(token_lists: Sequence[Sequence[str]], n: int) -> float:
    """Group-level distinct-n: unique n-grams / total n-grams across the group (Li et al. 2016)."""
    total = 0
    unique = set()
    for tokens in token_lists:
        grams = _ngrams(tokens, n)
        total += len(grams)
        unique.update(grams)
    if total == 0:
        return np.nan
    return float(len(unique) / total)


def _bleu_against_refs(cand: Sequence[str], ref_counts: Dict[int, Counter], max_n: int = 4) -> float:
    """Corpus-style BLEU of one candidate against pooled reference n-gram counts."""
    log_precisions = []
    for n in range(1, max_n + 1):
        cand_grams = Counter(_ngrams(cand, n))
        if not cand_grams:
            continue  # text shorter than n: skip this order rather than zeroing BLEU
        refs = ref_counts.get(n, Counter())
        clipped = sum(min(c, refs.get(g, 0)) for g, c in cand_grams.items())
        total = sum(cand_grams.values())
        precision = clipped / total if total else 0.0
        if precision == 0.0:
            precision = 1.0 / (2.0 * total)  # standard smoothing for zero counts
        log_precisions.append(np.log(precision))
    bleu = float(np.exp(np.mean(log_precisions)))
    return bleu


def self_bleu(token_lists: Sequence[Sequence[str]], max_n: int = 4) -> float:
    """Self-BLEU (Zhu et al. 2018): mean BLEU of each text against all other texts in the group.

    Higher = texts repeat each other's phrasing = lower lexical diversity. No brevity
    penalty is applied (texts within a group are comparable in length; the statistic
    is used only as a within-study contrast).
    """
    if len(token_lists) < 2:
        return np.nan
    per_text_counts = [
        {n: Counter(_ngrams(tokens, n)) for n in range(1, max_n + 1)} for tokens in token_lists
    ]
    totals = {n: Counter() for n in range(1, max_n + 1)}
    for counts in per_text_counts:
        for n in range(1, max_n + 1):
            totals[n].update(counts[n])
    scores = []
    for i, tokens in enumerate(token_lists):
        refs = {}
        for n in range(1, max_n + 1):
            rc = totals[n].copy()
            rc.subtract(per_text_counts[i][n])
            refs[n] = +rc  # drop non-positive counts
        scores.append(_bleu_against_refs(tokens, refs, max_n=max_n))
    return float(np.mean(scores))


__all__ = ["distinct_n", "self_bleu"]
