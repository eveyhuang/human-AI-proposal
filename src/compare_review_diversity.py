"""
Helpers for exact-n matched review-diversity comparison notebooks.
"""

from __future__ import annotations

import itertools
import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.stats import spearmanr, wilcoxon

from proposal_generation import find_project_root


COMPARISON_LABELS = {
    'all_ai': 'All AI',
    'claude': 'Claude',
    'gemini': 'Gemini',
    'gpt': 'GPT',
}

CONFIRMATORY_REVIEW_METRICS = ['mean_pairwise', 'nn']
EXPLORATORY_REVIEW_METRICS = [
    'centroid_loo',
    'global_centroid_dist',
    'medoid_dist',
    'span90',
    'mst_dispersion',
    'sparseness',
]
COMPATIBILITY_REVIEW_METRICS = ['remote_clique']
ALL_REVIEW_DIVERSITY_METRICS = (
    CONFIRMATORY_REVIEW_METRICS
    + EXPLORATORY_REVIEW_METRICS
    + COMPATIBILITY_REVIEW_METRICS
)

@dataclass
class ReviewConditionAnalysis:
    condition: str
    text_version: str
    panel_registry: pd.DataFrame
    sampling_frame: pd.DataFrame
    proposal_score_summary: pd.DataFrame
    review_master: pd.DataFrame
    review_embeddings: Dict[str, Any]
    review_pairwise: np.ndarray
    review_umap2d: np.ndarray
    review_panel_distance_cache: Dict[str, Any]


def load_pickle(path: Path) -> Any:
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def save_pickle(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as handle:
        pickle.dump(payload, handle)


def load_review_analysis_inputs(project_root: Path, condition: str, text_version: str = 'original') -> ReviewConditionAnalysis:
    """Load the prepared review inputs for one condition and branch."""
    prepared_root = project_root / 'data' / 'prepared' / condition
    reviews_root = prepared_root / 'reviews'
    branch_root = reviews_root / text_version
    required_paths = {
        'panel_registry': reviews_root / 'review_panel_registry.csv',
        'sampling_frame': reviews_root / 'review_sampling_frame.csv',
        'review_master': branch_root / 'review_master.csv',
        'review_embeddings': branch_root / 'review_embeddings_text.pkl',
        'review_pairwise': branch_root / 'review_pairwise_cosine_text.npy',
        'review_umap2d': branch_root / 'review_umap2d.npy',
        'review_panel_distance_cache': branch_root / 'review_panel_distance_cache.pkl',
    }
    missing = [str(path) for path in required_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            'Missing prepared review inputs for '
            f'{condition}/{text_version}: ' + ', '.join(missing)
        )
    proposal_score_summary_path = reviews_root / 'proposal_review_scores_summary.csv'
    proposal_score_summary = (
        pd.read_csv(proposal_score_summary_path)
        if proposal_score_summary_path.exists()
        else pd.DataFrame()
    )
    return ReviewConditionAnalysis(
        condition=condition,
        text_version=text_version,
        panel_registry=pd.read_csv(required_paths['panel_registry']),
        sampling_frame=pd.read_csv(required_paths['sampling_frame']),
        proposal_score_summary=proposal_score_summary,
        review_master=pd.read_csv(required_paths['review_master']),
        review_embeddings=load_pickle(required_paths['review_embeddings']),
        review_pairwise=np.load(required_paths['review_pairwise']),
        review_umap2d=np.load(required_paths['review_umap2d']),
        review_panel_distance_cache=load_pickle(required_paths['review_panel_distance_cache']),
    )


def _parse_uid_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if pd.isna(value):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        except json.JSONDecodeError:
            return [text]
    return [str(value)]


def build_exact_n_panel_combinations(
    panel_registry_df: pd.DataFrame,
    comparison: str,
) -> Dict[str, Dict[str, Any]]:
    """Enumerate all exact-n AI review panels per target proposal."""
    if comparison not in COMPARISON_LABELS:
        raise ValueError(f'Unsupported comparison: {comparison}')
    source_col = {
        'all_ai': 'ai_review_uids_pooled',
        'claude': 'ai_review_uids_claude',
        'gemini': 'ai_review_uids_gemini',
        'gpt': 'ai_review_uids_gpt',
    }[comparison]
    eligible_col = {
        'all_ai': 'eligible_exact_match_pooled',
        'claude': 'eligible_exact_match_claude',
        'gemini': 'eligible_exact_match_gemini',
        'gpt': 'eligible_exact_match_gpt',
    }[comparison]

    output: Dict[str, Dict[str, Any]] = {}
    for row in panel_registry_df.to_dict('records'):
        target_uid = str(row['target_proposal_uid'])
        n_human = int(row['target_human_n_reviews'])
        human_uids = _parse_uid_list(row.get('human_review_uids'))
        ai_uids = _parse_uid_list(row.get(source_col))
        eligible = bool(row.get(eligible_col, False)) and len(human_uids) == n_human and len(ai_uids) >= n_human
        combos = list(itertools.combinations(ai_uids, n_human)) if eligible else []
        output[target_uid] = {
            'condition': row.get('condition'),
            'comparison': comparison,
            'comparison_label': COMPARISON_LABELS[comparison],
            'target_proposal_uid': target_uid,
            'target_cohort': row.get('target_cohort'),
            'target_proposal_id': row.get('target_proposal_id'),
            'target_proposal_title': row.get('target_proposal_title'),
            'target_human_n_reviews': n_human,
            'human_review_uids': human_uids,
            'ai_review_uids_available': ai_uids,
            'eligible': eligible,
            'n_ai_reviews_available': len(ai_uids),
            'ai_panel_combinations': combos,
            'n_ai_panels_enumerated': len(combos),
        }
    return output


def compute_review_panel_metrics_from_distance_submatrix(
    distance_submatrix: np.ndarray,
    embeddings: np.ndarray | None = None,
) -> Dict[str, float]:
    """Compute one panel's diversity metrics."""
    D = np.asarray(distance_submatrix, dtype=float)
    out = {metric: np.nan for metric in ALL_REVIEW_DIVERSITY_METRICS}
    if D.shape[0] < 2:
        return out

    tri = D[np.triu_indices(D.shape[0], k=1)]
    if tri.size:
        out['mean_pairwise'] = float(np.nanmean(tri))
        out['remote_clique'] = float(np.nanmean(tri))

    nn_arr = D.copy()
    np.fill_diagonal(nn_arr, np.inf)
    out['nn'] = float(np.mean(np.min(nn_arr, axis=1)))

    medoid_idx = int(np.argmin(D.sum(axis=1)))
    out['medoid_dist'] = float(np.mean(D[:, medoid_idx]))

    try:
        mst = minimum_spanning_tree(D)
        mst_vals = np.asarray(mst.data, dtype=float)
        if mst_vals.size:
            out['mst_dispersion'] = float(np.mean(mst_vals))
    except Exception:
        out['mst_dispersion'] = np.nan

    if embeddings is not None:
        X = np.asarray(embeddings, dtype=float)
        if X.ndim == 2 and X.shape[0] == D.shape[0]:
            norms = np.linalg.norm(X, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            X = X / norms
            centroid = X.mean(axis=0)
            centroid_norm = np.linalg.norm(centroid)
            if centroid_norm > 0:
                centroid = centroid / centroid_norm
                dist_to_centroid = 1.0 - np.clip(X @ centroid, -1.0, 1.0)
                out['span90'] = float(np.nanpercentile(dist_to_centroid, 90))
                out['sparseness'] = float(np.nanmean(dist_to_centroid))
                out['global_centroid_dist'] = float(np.nanmean(dist_to_centroid))

            loo_vals = []
            for idx in range(X.shape[0]):
                others = np.delete(X, idx, axis=0)
                if others.shape[0] == 0:
                    continue
                loo_centroid = others.mean(axis=0)
                loo_norm = np.linalg.norm(loo_centroid)
                if loo_norm == 0:
                    continue
                loo_centroid = loo_centroid / loo_norm
                loo_vals.append(1.0 - float(np.clip(X[idx] @ loo_centroid, -1.0, 1.0)))
            if loo_vals:
                out['centroid_loo'] = float(np.mean(loo_vals))

    return out


def summarize_exact_n_panel_metrics(panel_metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize one proposal-comparison's panel metrics over all exact-n AI panels."""
    if panel_metrics_df.empty:
        return pd.DataFrame(
            columns=[
                'metric',
                'ai_metric_panel_mean',
                'ai_metric_panel_median',
                'ai_metric_panel_std',
                'ai_metric_panel_q10',
                'ai_metric_panel_q25',
                'ai_metric_panel_q75',
                'ai_metric_panel_q90',
                'n_ai_panels_enumerated',
            ]
        )
    rows: List[Dict[str, Any]] = []
    for metric, group in panel_metrics_df.groupby('metric', sort=True):
        values = pd.to_numeric(group['ai_metric_value'], errors='coerce').dropna().to_numpy(dtype=float)
        if values.size == 0:
            continue
        rows.append(
            {
                'metric': metric,
                'ai_metric_panel_mean': float(np.mean(values)),
                'ai_metric_panel_median': float(np.median(values)),
                'ai_metric_panel_std': float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
                'ai_metric_panel_q10': float(np.quantile(values, 0.10)),
                'ai_metric_panel_q25': float(np.quantile(values, 0.25)),
                'ai_metric_panel_q75': float(np.quantile(values, 0.75)),
                'ai_metric_panel_q90': float(np.quantile(values, 0.90)),
                'n_ai_panels_enumerated': int(values.size),
            }
        )
    return pd.DataFrame(rows)


def build_review_diversity_proposal_master(
    analysis: ReviewConditionAnalysis,
    combination_cache: Mapping[str, Mapping[str, Dict[str, Any]]],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build proposal-level exact-n matched review-diversity tables."""
    review_master = analysis.review_master.copy()
    review_uid_to_idx = {
        str(uid): idx
        for idx, uid in enumerate(review_master['review_uid'].astype(str).tolist())
    }
    embedding_array = np.asarray(analysis.review_embeddings['embeddings'], dtype=float)

    proposal_rows: List[Dict[str, Any]] = []
    panel_rows: List[Dict[str, Any]] = []
    proposal_score_lookup = (
        analysis.proposal_score_summary.set_index('target_proposal_uid').to_dict('index')
        if not analysis.proposal_score_summary.empty and 'target_proposal_uid' in analysis.proposal_score_summary.columns
        else {}
    )

    for comparison, combo_map in combination_cache.items():
        comparison_label = COMPARISON_LABELS[comparison]
        for target_uid, combo_info in combo_map.items():
            if not combo_info.get('eligible', False):
                continue
            panel_cache = analysis.review_panel_distance_cache['panels'].get(str(target_uid))
            if panel_cache is None:
                raise KeyError(f'Missing panel cache for target_proposal_uid={target_uid}')

            human_uids = [str(uid) for uid in combo_info['human_review_uids']]
            human_idx = [review_uid_to_idx[uid] for uid in human_uids]
            human_D = analysis.review_pairwise[np.ix_(human_idx, human_idx)]
            human_X = embedding_array[human_idx]
            human_metrics = compute_review_panel_metrics_from_distance_submatrix(human_D, human_X)

            per_panel_metric_rows: List[Dict[str, Any]] = []
            for panel_id, ai_uids in enumerate(combo_info['ai_panel_combinations']):
                ai_idx = [review_uid_to_idx[str(uid)] for uid in ai_uids]
                ai_D = analysis.review_pairwise[np.ix_(ai_idx, ai_idx)]
                ai_X = embedding_array[ai_idx]
                ai_metrics = compute_review_panel_metrics_from_distance_submatrix(ai_D, ai_X)
                for metric, ai_value in ai_metrics.items():
                    rec = {
                        'condition': analysis.condition,
                        'text_version': analysis.text_version,
                        'comparison': comparison,
                        'comparison_label': comparison_label,
                        'target_proposal_uid': str(target_uid),
                        'target_cohort': combo_info.get('target_cohort'),
                        'target_proposal_id': combo_info.get('target_proposal_id'),
                        'target_proposal_title': combo_info.get('target_proposal_title'),
                        'target_human_n_reviews': combo_info.get('target_human_n_reviews'),
                        'ai_panel_id': f'{comparison}_{target_uid}_{panel_id:04d}',
                        'ai_panel_size': len(ai_uids),
                        'ai_panel_review_uids': json.dumps([str(uid) for uid in ai_uids]),
                        'metric': metric,
                        'human_metric_value': human_metrics.get(metric),
                        'ai_metric_value': ai_value,
                    }
                    panel_rows.append(rec)
                    per_panel_metric_rows.append(rec)

            panel_metrics_df = pd.DataFrame(per_panel_metric_rows)
            summary_df = summarize_exact_n_panel_metrics(panel_metrics_df)
            score_overlay = proposal_score_lookup.get(str(target_uid), {})
            for row in summary_df.to_dict('records'):
                metric = row['metric']
                proposal_rows.append(
                    {
                        'condition': analysis.condition,
                        'text_version': analysis.text_version,
                        'comparison': comparison,
                        'comparison_label': comparison_label,
                        'target_proposal_uid': str(target_uid),
                        'target_cohort': combo_info.get('target_cohort'),
                        'target_proposal_id': combo_info.get('target_proposal_id'),
                        'target_proposal_title': combo_info.get('target_proposal_title'),
                        'target_human_n_reviews': combo_info.get('target_human_n_reviews'),
                        'metric': metric,
                        'metric_class': (
                            'confirmatory'
                            if metric in CONFIRMATORY_REVIEW_METRICS
                            else 'compatibility'
                            if metric in COMPATIBILITY_REVIEW_METRICS
                            else 'exploratory'
                        ),
                        'human_metric_value': human_metrics.get(metric),
                        **row,
                        'paired_difference_human_minus_ai': (
                            float(human_metrics.get(metric)) - float(row['ai_metric_panel_mean'])
                            if pd.notna(human_metrics.get(metric)) and pd.notna(row['ai_metric_panel_mean'])
                            else np.nan
                        ),
                        'ai_to_human_ratio': (
                            float(row['ai_metric_panel_mean']) / float(human_metrics.get(metric))
                            if pd.notna(human_metrics.get(metric)) and float(human_metrics.get(metric)) != 0.0
                            else np.nan
                        ),
                        **score_overlay,
                    }
                )

    proposal_master_df = pd.DataFrame(proposal_rows)
    panel_long_df = pd.DataFrame(panel_rows)
    return proposal_master_df, panel_long_df


def _paired_rank_biserial(differences: np.ndarray) -> float:
    nonzero = differences[np.abs(differences) > 0]
    if nonzero.size == 0:
        return 0.0
    n_pos = int(np.sum(nonzero > 0))
    n_neg = int(np.sum(nonzero < 0))
    return float((n_pos - n_neg) / (n_pos + n_neg))


def paired_review_diversity_tests(
    proposal_master_df: pd.DataFrame,
    comparison: str | None = None,
    subset_label: str = 'all_proposals',
) -> pd.DataFrame:
    """Run paired Wilcoxon tests across target proposals."""
    df = proposal_master_df.copy()
    if comparison is not None:
        df = df[df['comparison'] == comparison].copy()
    rows: List[Dict[str, Any]] = []
    for (comp, metric), group in df.groupby(['comparison', 'metric'], sort=True):
        sub = group[['target_proposal_uid', 'human_metric_value', 'ai_metric_panel_mean', 'paired_difference_human_minus_ai']].dropna()
        if sub.empty:
            continue
        x = sub['human_metric_value'].to_numpy(dtype=float)
        y = sub['ai_metric_panel_mean'].to_numpy(dtype=float)
        diff = sub['paired_difference_human_minus_ai'].to_numpy(dtype=float)
        if np.allclose(diff, 0):
            stat = 0.0
            p_value = 1.0
        else:
            test = wilcoxon(x, y, zero_method='wilcox', alternative='two-sided', mode='auto')
            stat = float(test.statistic)
            p_value = float(test.pvalue)
        rows.append(
            {
                'comparison': comp,
                'comparison_label': COMPARISON_LABELS.get(comp, comp),
                'metric': metric,
                'metric_class': (
                    'confirmatory'
                    if metric in CONFIRMATORY_REVIEW_METRICS
                    else 'compatibility'
                    if metric in COMPATIBILITY_REVIEW_METRICS
                    else 'exploratory'
                ),
                'subset_label': subset_label,
                'n_proposals': int(len(sub)),
                'human_metric_mean': float(np.mean(x)),
                'ai_metric_mean': float(np.mean(y)),
                'effect_human_minus_ai_mean': float(np.mean(diff)),
                'effect_human_minus_ai_median': float(np.median(diff)),
                'ai_to_human_ratio_mean': float(np.mean(y) / np.mean(x)) if np.mean(x) != 0 else np.nan,
                'wilcoxon_statistic': stat,
                'p_value': p_value,
                'paired_rank_biserial': _paired_rank_biserial(diff),
            }
        )
    return pd.DataFrame(rows).sort_values(['comparison', 'metric']).reset_index(drop=True)


def compute_review_metric_correlation_table(proposal_master_df: pd.DataFrame) -> pd.DataFrame:
    """Correlate metric-wise paired differences within each comparison."""
    rows: List[Dict[str, Any]] = []
    for comparison, comp_df in proposal_master_df.groupby('comparison', sort=True):
        pivot = comp_df.pivot_table(
            index='target_proposal_uid',
            columns='metric',
            values='paired_difference_human_minus_ai',
            aggfunc='mean',
        )
        metrics = [m for m in ALL_REVIEW_DIVERSITY_METRICS if m in pivot.columns]
        for metric_a, metric_b in itertools.combinations(metrics, 2):
            pair = pivot[[metric_a, metric_b]].dropna()
            if len(pair) < 3:
                rho = np.nan
                p_value = np.nan
            else:
                rho, p_value = spearmanr(pair[metric_a], pair[metric_b])
            rows.append(
                {
                    'comparison': comparison,
                    'comparison_label': COMPARISON_LABELS.get(comparison, comparison),
                    'metric_a': metric_a,
                    'metric_b': metric_b,
                    'spearman_rho': rho,
                    'p_value': p_value,
                    'n_proposals': int(len(pair)),
                }
            )
    return pd.DataFrame(rows).sort_values(['comparison', 'metric_a', 'metric_b']).reset_index(drop=True)


def plot_review_diversity_paired_slopes(
    proposal_master_df: pd.DataFrame,
    *,
    comparison: str,
    metrics: Sequence[str],
    output_path: Path,
    title: str,
) -> None:
    """Plot proposal-level paired Human vs AI panel-mean values."""
    df = proposal_master_df[proposal_master_df['comparison'] == comparison].copy()
    metrics = [metric for metric in metrics if metric in df['metric'].unique()]
    if not metrics:
        return
    fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 5), sharey=False)
    if len(metrics) == 1:
        axes = [axes]
    for ax, metric in zip(axes, metrics):
        sub = df[df['metric'] == metric].sort_values('target_proposal_uid')
        for _, row in sub.iterrows():
            ax.plot(
                ['Human', COMPARISON_LABELS.get(comparison, comparison)],
                [row['human_metric_value'], row['ai_metric_panel_mean']],
                color='#999999',
                alpha=0.45,
                linewidth=1.0,
            )
        ax.scatter(np.repeat('Human', len(sub)), sub['human_metric_value'], color='#C62828', s=28, zorder=3)
        ax.scatter(
            np.repeat(COMPARISON_LABELS.get(comparison, comparison), len(sub)),
            sub['ai_metric_panel_mean'],
            color='#1565C0',
            s=28,
            zorder=3,
        )
        ax.set_title(metric)
        ax.set_xlabel('')
        ax.set_ylabel('Diversity metric value')
    fig.suptitle(title)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def plot_review_diversity_effects(
    tests_df: pd.DataFrame,
    *,
    output_path: Path,
    title: str,
    metric_class: str | None = None,
) -> None:
    """Plot paired effect summaries."""
    plot_df = tests_df.copy()
    if metric_class is not None:
        plot_df = plot_df[plot_df['metric_class'] == metric_class].copy()
    if plot_df.empty:
        return
    fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(plot_df))))
    sns.barplot(
        data=plot_df,
        x='effect_human_minus_ai_mean',
        y='metric',
        hue='comparison_label',
        ax=ax,
    )
    ax.axvline(0.0, color='black', linewidth=1.0)
    ax.set_xlabel('Mean paired difference (Human - AI)')
    ax.set_ylabel('')
    ax.set_title(title)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def plot_review_embedding_space(
    analysis: ReviewConditionAnalysis,
    *,
    output_path: Path,
    title: str,
) -> None:
    """Plot prepared review-space UMAP coordinates."""
    coords = np.asarray(analysis.review_umap2d, dtype=float)
    df = analysis.review_master.copy()
    if coords.shape[0] != len(df):
        raise ValueError('UMAP coordinates do not align with review_master rows')
    plot_df = df[['review_source', 'source_family', 'target_cohort']].copy()
    plot_df['umap_x'] = coords[:, 0]
    plot_df['umap_y'] = coords[:, 1]
    plot_df['group_label'] = np.where(
        plot_df['review_source'] == 'human',
        'Human',
        plot_df['source_family'].str.title(),
    )
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.scatterplot(
        data=plot_df,
        x='umap_x',
        y='umap_y',
        hue='group_label',
        style='target_cohort',
        alpha=0.7,
        s=40,
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def cross_condition_summary_table(test_frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate per-condition test summaries."""
    frames = [frame.copy() for frame in test_frames if frame is not None and not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


__all__ = [
    'ALL_REVIEW_DIVERSITY_METRICS',
    'COMPARISON_LABELS',
    'COMPATIBILITY_REVIEW_METRICS',
    'CONFIRMATORY_REVIEW_METRICS',
    'EXPLORATORY_REVIEW_METRICS',
    'ReviewConditionAnalysis',
    'build_exact_n_panel_combinations',
    'build_review_diversity_proposal_master',
    'compute_review_metric_correlation_table',
    'compute_review_panel_metrics_from_distance_submatrix',
    'cross_condition_summary_table',
    'find_project_root',
    'load_review_analysis_inputs',
    'load_pickle',
    'paired_review_diversity_tests',
    'plot_review_diversity_effects',
    'plot_review_diversity_paired_slopes',
    'plot_review_embedding_space',
    'save_pickle',
    'summarize_exact_n_panel_metrics',
]
