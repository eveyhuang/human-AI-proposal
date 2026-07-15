"""
Helpers for pooled proposal comparison notebooks.
"""

from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.stats import chi2_contingency, kruskal

from proposal_generation import find_project_root


PRIMARY_DIVERSITY_METRICS = ['mean_pairwise_distance', 'nearest_neighbor_distance', 'grid_entropy']


@dataclass
class ProposalConditionAnalysis:
    condition: str
    proposal_master: pd.DataFrame
    full_embeddings: Dict[str, Any]
    abstract_embeddings: Dict[str, Any]
    pairwise_full: np.ndarray
    umap2d: np.ndarray
    proposal_to_literature_knn: Dict[str, Any]
    review_scores_summary: pd.DataFrame


def load_pickle(path: Path) -> Any:
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def load_npz(path: Path) -> Dict[str, Any]:
    payload = np.load(path, allow_pickle=True)
    return {key: payload[key] for key in payload.files}


def load_condition_analysis_inputs(project_root: Path, condition: str, text_version: str = 'original') -> ProposalConditionAnalysis:
    """Load all prepared inputs required for one condition analysis run."""
    base_dir = project_root / 'data' / 'prepared' / condition / 'proposals' / text_version
    review_summary_path = project_root / 'data' / 'prepared' / condition / 'reviews' / 'proposal_review_scores_summary.csv'
    proposal_master = pd.read_csv(base_dir / 'proposal_master.csv')
    full_embeddings = load_pickle(base_dir / 'proposal_embeddings_full.pkl')
    abstract_embeddings = load_pickle(base_dir / 'proposal_embeddings_abstract.pkl')
    pairwise_full = np.load(base_dir / 'proposal_pairwise_cosine_full.npy')
    umap2d = np.load(base_dir / 'proposal_umap2d.npy')
    proposal_to_literature_knn = load_npz(base_dir / 'proposal_to_literature_knn.npz')
    review_scores_summary = pd.read_csv(review_summary_path) if review_summary_path.exists() else pd.DataFrame()
    return ProposalConditionAnalysis(
        condition=condition,
        proposal_master=proposal_master,
        full_embeddings=full_embeddings,
        abstract_embeddings=abstract_embeddings,
        pairwise_full=pairwise_full,
        umap2d=umap2d,
        proposal_to_literature_knn=proposal_to_literature_knn,
        review_scores_summary=review_scores_summary,
    )


def get_group_indices(master_df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """Build reusable row-index slices for Human vs pooled AI."""
    human_idx = master_df.index[master_df['source_type'] == 'human'].to_numpy()
    ai_idx = master_df.index[master_df['source_type'] == 'ai'].to_numpy()
    by_model = {}
    for group in sorted(master_df.loc[master_df['source_type'] == 'ai', 'source_group'].dropna().unique().tolist()):
        by_model[group] = master_df.index[master_df['source_group'] == group].to_numpy()
    return {'Human': human_idx, 'All AI': ai_idx, **by_model}


def generate_or_load_bootstrap_samples(
    ai_idx: np.ndarray,
    *,
    output_path: Path,
    n_boot: int = 1000,
    n_subsample: int = 23,
    seed: int = 42,
) -> np.ndarray:
    """Create or load pooled AI bootstrap subsamples of size 23."""
    if output_path.exists():
        cached = np.load(output_path)
        if cached.shape == (n_boot, n_subsample):
            return cached
    rng = np.random.default_rng(seed)
    samples = np.vstack([
        rng.choice(ai_idx, size=n_subsample, replace=False)
        for _ in range(n_boot)
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, samples)
    return samples


def mean_pairwise_distance(D_sub: np.ndarray) -> float:
    arr = np.asarray(D_sub, dtype=float).copy()
    np.fill_diagonal(arr, np.nan)
    return float(np.nanmean(arr))


def nearest_neighbor_distance(D_sub: np.ndarray) -> float:
    arr = np.asarray(D_sub, dtype=float).copy()
    np.fill_diagonal(arr, np.inf)
    return float(np.mean(np.min(arr, axis=1)))


def mst_dispersion(D_sub: np.ndarray) -> float:
    mst = minimum_spanning_tree(np.asarray(D_sub, dtype=float))
    data = mst.data
    if data.size == 0:
        return float('nan')
    return float(np.mean(data))


def chamfer_distance(D: np.ndarray, idx_a: np.ndarray, idx_b: np.ndarray) -> float:
    """Symmetric nearest-neighbor cross-group distance."""
    cross = D[np.ix_(idx_a, idx_b)]
    return float(0.5 * (np.mean(np.min(cross, axis=1)) + np.mean(np.min(cross, axis=0))))


def fixed_coordinate_range(coords: np.ndarray) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Return a stable 2D histogram range for comparable grid metrics."""
    arr = np.asarray(coords, dtype=float)
    x_min, x_max = float(np.nanmin(arr[:, 0])), float(np.nanmax(arr[:, 0]))
    y_min, y_max = float(np.nanmin(arr[:, 1])), float(np.nanmax(arr[:, 1]))
    if x_min == x_max:
        x_min -= 0.5
        x_max += 0.5
    if y_min == y_max:
        y_min -= 0.5
        y_max += 0.5
    return ((x_min, x_max), (y_min, y_max))


def grid_entropy(
    coords: np.ndarray,
    idx: np.ndarray,
    bins: int = 8,
    coord_range: Tuple[Tuple[float, float], Tuple[float, float]] | None = None,
) -> float:
    """Discrete occupied-area metric on 2D coordinates.

    Pass a fixed coord_range when comparing groups so each group is binned on
    the same map rather than on its own local bounding box.
    """
    pts = np.asarray(coords[idx], dtype=float)
    if pts.size == 0:
        return float('nan')
    hist_range = coord_range if coord_range is not None else fixed_coordinate_range(pts)
    hist, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=bins, range=hist_range)
    p = hist.ravel()
    p = p[p > 0]
    p = p / p.sum()
    return float(-(p * np.log2(p)).sum())


def per_proposal_diversity_metrics(master_df: pd.DataFrame, D: np.ndarray) -> pd.DataFrame:
    """Compute per-proposal local redundancy metrics used downstream."""
    rows: List[Dict[str, Any]] = []
    group_idx = get_group_indices(master_df)
    for label in ['Human', 'All AI']:
        idx = group_idx[label]
        D_sub = D[np.ix_(idx, idx)].copy()
        np.fill_diagonal(D_sub, np.nan)
        nn_sub = D[np.ix_(idx, idx)].copy()
        np.fill_diagonal(nn_sub, np.inf)
        for local_pos, global_idx in enumerate(idx):
            rows.append(
                {
                    'proposal_uid': master_df.iloc[global_idx]['proposal_uid'],
                    'source_group_binary': label,
                    'mean_pairwise_distance': float(np.nanmean(D_sub[local_pos])),
                    'nearest_neighbor_distance': float(np.min(nn_sub[local_pos])),
                }
            )
    return pd.DataFrame(rows)


def permutation_test_group_metric(
    D: np.ndarray,
    human_idx: np.ndarray,
    ai_idx: np.ndarray,
    *,
    metric_name: str,
    n_perm: int = 10000,
    seed: int = 42,
    coords: np.ndarray | None = None,
    coord_range: Tuple[Tuple[float, float], Tuple[float, float]] | None = None,
) -> Dict[str, Any]:
    """Permutation-primary inference for pooled Human vs All-AI matrix-derived metrics."""
    metric_fns = {
        'mean_pairwise_distance': lambda idx: mean_pairwise_distance(D[np.ix_(idx, idx)]),
        'nearest_neighbor_distance': lambda idx: nearest_neighbor_distance(D[np.ix_(idx, idx)]),
        'mst_dispersion': lambda idx: mst_dispersion(D[np.ix_(idx, idx)]),
        'grid_entropy': lambda idx: grid_entropy(coords, idx, coord_range=coord_range) if coords is not None else np.nan,
    }
    if metric_name not in metric_fns:
        raise ValueError(f'Unsupported metric_name: {metric_name}')
    metric_fn = metric_fns[metric_name]
    observed = float(metric_fn(human_idx) - metric_fn(ai_idx))
    combined = np.concatenate([human_idx, ai_idx])
    n_h = len(human_idx)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        perm = rng.permutation(combined)
        null[i] = metric_fn(perm[:n_h]) - metric_fn(perm[n_h:])
    p_value = float((np.sum(np.abs(null) >= abs(observed)) + 1) / (n_perm + 1))
    return {
        'metric': metric_name,
        'observed_difference_human_minus_ai': observed,
        'permutation_p_value': p_value,
        'n_perm': n_perm,
    }


def pooled_bootstrap_metric_distribution(
    D: np.ndarray,
    human_idx: np.ndarray,
    boot_ai_idx_samples: np.ndarray,
    *,
    metric_name: str,
    coords: np.ndarray | None = None,
    coord_range: Tuple[Tuple[float, float], Tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Compute matched-size bootstrap distributions for Human vs pooled AI."""
    metric_fns = {
        'mean_pairwise_distance': lambda idx: mean_pairwise_distance(D[np.ix_(idx, idx)]),
        'nearest_neighbor_distance': lambda idx: nearest_neighbor_distance(D[np.ix_(idx, idx)]),
        'mst_dispersion': lambda idx: mst_dispersion(D[np.ix_(idx, idx)]),
        'grid_entropy': lambda idx: grid_entropy(coords, idx, coord_range=coord_range) if coords is not None else np.nan,
    }
    metric_fn = metric_fns[metric_name]
    human_value = float(metric_fn(human_idx))
    rows = []
    for i, sample in enumerate(boot_ai_idx_samples):
        rows.append(
            {
                'sample_index': i,
                'human_value': human_value,
                'ai_value': float(metric_fn(sample)),
                'metric': metric_name,
            }
        )
    return pd.DataFrame(rows)


def compare_human_vs_group_metrics(
    D: np.ndarray,
    human_idx: np.ndarray,
    comparison_idx: np.ndarray,
    *,
    coords: np.ndarray | None = None,
    coord_range: Tuple[Tuple[float, float], Tuple[float, float]] | None = None,
    metric_names: List[str] | None = None,
    n_perm: int = 10000,
    seed: int = 42,
) -> pd.DataFrame:
    """Run the standard matrix-derived metric comparison for one Human-vs-group contrast."""
    metric_names = metric_names or (PRIMARY_DIVERSITY_METRICS + ['mst_dispersion'])
    rows = []
    for metric_name in metric_names:
        perm = permutation_test_group_metric(
            D,
            human_idx,
            comparison_idx,
            metric_name=metric_name,
            n_perm=n_perm,
            seed=seed,
            coords=coords,
            coord_range=coord_range,
        )
        rows.append(
            {
                'metric': metric_name,
                'effect_human_minus_group': perm['observed_difference_human_minus_ai'],
                'permutation_p_value': perm['permutation_p_value'],
                'inference_primary': 'permutation',
            }
        )
    return pd.DataFrame(rows)


def build_proposal_metrics_master(
    analysis: ProposalConditionAnalysis,
    lit_self_knn_mean10: np.ndarray | None = None,
) -> pd.DataFrame:
    """Build one proposal-level master table used by summary exports."""
    master = analysis.proposal_master.copy()
    D = np.asarray(analysis.pairwise_full, dtype=float)
    per_prop = per_proposal_diversity_metrics(master, D)
    master = master.merge(per_prop, on='proposal_uid', how='left', validate='one_to_one')

    knn = analysis.proposal_to_literature_knn
    neighbor_distance = np.asarray(knn['neighbor_distance'], dtype=float)
    master['literature_element_novelty_k1'] = neighbor_distance[:, 0]
    k10 = min(10, neighbor_distance.shape[1])
    master['literature_mean_knn_novelty_k10'] = neighbor_distance[:, :k10].mean(axis=1)
    if lit_self_knn_mean10 is not None:
        master['literature_local_density_normalized_novelty'] = (
            master['literature_mean_knn_novelty_k10'].to_numpy() - np.mean(lit_self_knn_mean10)
        ) / np.std(lit_self_knn_mean10)
    else:
        master['literature_local_density_normalized_novelty'] = np.nan
    if not analysis.review_scores_summary.empty:
        master = master.merge(
            analysis.review_scores_summary,
            left_on='proposal_uid',
            right_on='target_proposal_uid',
            how='left',
        )
    return master


def compute_literature_self_knn_cache(
    literature_embeddings_path: Path,
    *,
    output_path: Path,
    k: int = 50,
) -> np.ndarray:
    """Compute or load literature self-kNN distances for local-density normalization."""
    if output_path.exists():
        return np.load(output_path)
    payload = load_pickle(literature_embeddings_path)
    X = np.asarray(payload['embeddings'], dtype=np.float32)
    nn = NearestNeighbors(n_neighbors=k + 1, metric='cosine')
    nn.fit(X)
    distances, _ = nn.kneighbors(X)
    distances = distances[:, 1:]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, distances)
    return distances


def simple_style_features(texts: pd.Series) -> pd.DataFrame:
    """Build lightweight stylistic feature vectors."""
    rows = []
    for text in texts.fillna('').astype(str):
        words = re.findall(r'\b\w+\b', text)
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        unique_words = set(w.lower() for w in words)
        rows.append(
            {
                'char_len': len(text),
                'word_count': len(words),
                'sentence_count': max(len(sentences), 1),
                'avg_sentence_len': len(words) / max(len(sentences), 1),
                'type_token_ratio': len(unique_words) / max(len(words), 1),
                'comma_rate': text.count(',') / max(len(words), 1),
                'digit_rate': sum(ch.isdigit() for ch in text) / max(len(text), 1),
                'uppercase_rate': sum(ch.isupper() for ch in text) / max(len(text), 1),
            }
        )
    return pd.DataFrame(rows)


def style_classifier_permutation(
    X: pd.DataFrame,
    y: np.ndarray,
    *,
    n_perm: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Train a style-only classifier and estimate a permutation p-value."""
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
    class_counts = np.bincount(np.asarray(y, dtype=int))
    min_class = int(class_counts.min()) if class_counts.size else 2
    n_splits = max(2, min(5, min_class))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    pred = cross_val_predict(clf, X, y, cv=cv, method='predict_proba')[:, 1]
    observed_auc = float(roc_auc_score(y, pred))
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        pred_perm = cross_val_predict(clf, X, y_perm, cv=cv, method='predict_proba')[:, 1]
        null[i] = roc_auc_score(y_perm, pred_perm)
    p_value = float((np.sum(null >= observed_auc) + 1) / (n_perm + 1))
    return {'observed_auc': observed_auc, 'permutation_p_value': p_value, 'n_perm': n_perm}


def run_simple_topic_analysis(master_df: pd.DataFrame, *, n_topics: int = 5, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Run a lightweight LDA topic-distribution comparison on abstract texts."""
    text_col = 'abstract_text'
    texts = master_df[text_col].fillna('').astype(str).tolist()
    vectorizer = CountVectorizer(stop_words='english', min_df=2)
    X = vectorizer.fit_transform(texts)
    n_topics = max(2, min(n_topics, max(2, X.shape[0] - 1)))
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=seed)
    topic_probs = lda.fit_transform(X)
    topic_label = topic_probs.argmax(axis=1)
    topic_df = master_df[['proposal_uid', 'source_type', 'source_group']].copy()
    topic_df['lda_topic'] = topic_label
    contingency = pd.crosstab(topic_df['source_type'], topic_df['lda_topic'])
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    summary = {'chi2': float(chi2), 'p_value': float(p_value), 'dof': int(dof), 'n_topics': int(n_topics)}
    return topic_df, summary


def run_simple_cluster_analysis(embeddings: np.ndarray, master_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Run a lightweight embedding-based cluster segregation analysis."""
    clusterer = AgglomerativeClustering(n_clusters=2, metric='euclidean', linkage='ward')
    labels = clusterer.fit_predict(np.asarray(embeddings, dtype=float))
    cluster_df = master_df[['proposal_uid', 'source_type', 'source_group']].copy()
    cluster_df['cluster_label'] = labels
    contingency = pd.crosstab(cluster_df['source_type'], cluster_df['cluster_label'])
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    return cluster_df, {'chi2': float(chi2), 'p_value': float(p_value), 'dof': int(dof), 'n_clusters': 2}


def cross_condition_summary_table(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


__all__ = [
    'PRIMARY_DIVERSITY_METRICS',
    'ProposalConditionAnalysis',
    'build_proposal_metrics_master',
    'chamfer_distance',
    'compute_literature_self_knn_cache',
    'cross_condition_summary_table',
    'generate_or_load_bootstrap_samples',
    'get_group_indices',
    'grid_entropy',
    'load_condition_analysis_inputs',
    'mean_pairwise_distance',
    'mst_dispersion',
    'nearest_neighbor_distance',
    'per_proposal_diversity_metrics',
    'permutation_test_group_metric',
    'pooled_bootstrap_metric_distribution',
    'run_simple_cluster_analysis',
    'run_simple_topic_analysis',
    'simple_style_features',
    'style_classifier_permutation',
]
