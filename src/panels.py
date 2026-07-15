"""Exact-n review panel enumeration utilities."""

from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable

import numpy as np
import pandas as pd


MAX_PANELS_PER_MODEL = 5000


def enumerate_exact_n_panels(
    master_df: pd.DataFrame,
    models: Iterable[str] = ('claude', 'gemini', 'gpt'),
    rng_seed: int = 42,
) -> Dict[str, Dict[str, Any]]:
    """Enumerate exact-n matched AI panels by target proposal.

    Returned indices are positional rows into master_df and its aligned embedding
    bundle, so downstream callers can slice raw vectors directly.
    """
    rng = np.random.default_rng(rng_seed)
    pos = np.arange(len(master_df))
    out: Dict[str, Dict[str, Any]] = {}
    target_values = master_df['target_proposal_uid'].astype(str)
    source_values = master_df['review_source'].astype(str)
    family_values = master_df['source_family'].astype(str)

    for uid in sorted(target_values.unique()):
        target_mask = (target_values == uid).to_numpy()
        human_rows = pos[target_mask & (source_values == 'human').to_numpy()]
        m = int(len(human_rows))
        if m < 2:
            raise RuntimeError(f'{uid}: human panel size {m} < 2 - cannot measure within-panel spread')

        per_model = {}
        for model in models:
            model_rows = pos[
                target_mask
                & (source_values == 'ai').to_numpy()
                & (family_values == model).to_numpy()
            ]
            if len(model_rows) < m:
                raise RuntimeError(f'{uid}/{model}: {len(model_rows)} AI reviews < human panel size {m}')
            per_model[str(model)] = [
                np.asarray(combo, dtype=int)
                for combo in combinations(model_rows, m)
            ]

        pooled_rows = pos[target_mask & (source_values == 'ai').to_numpy()]
        pooled_all = list(combinations(pooled_rows, m))
        if len(pooled_all) > MAX_PANELS_PER_MODEL:
            pick = rng.choice(len(pooled_all), size=MAX_PANELS_PER_MODEL, replace=False)
            pooled_all = [pooled_all[i] for i in pick]
        pooled = [np.asarray(combo, dtype=int) for combo in pooled_all]

        out[str(uid)] = {
            'm': m,
            'human_idx': human_rows.astype(int),
            'per_model': per_model,
            'pooled': pooled,
        }
    return out


__all__ = ['MAX_PANELS_PER_MODEL', 'enumerate_exact_n_panels']
