"""
Core diversity-facet metrics for proposal and review embedding analyses.

All public functions operate on row-wise L2-normalized embedding matrices in the
original embedding space. Plotting coordinates such as UMAP/PCA should not be
passed here.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np
from scipy.spatial.distance import cdist
from scipy.sparse.csgraph import minimum_spanning_tree


EPS = 1e-12


def l2_normalize(X: np.ndarray) -> np.ndarray:
    """Return a float array with rows normalized to unit length."""
    arr = np.asarray(X, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms < EPS] = 1.0
    return arr / norms


def cosine_dist(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Cosine distance for already-normalized rows, clipped for stability."""
    Xn = l2_normalize(X)
    Yn = Xn if Y is None else l2_normalize(Y)
    return 1.0 - np.clip(Xn @ Yn.T, -1.0, 1.0)


def pairwise_sq_euclidean(X: np.ndarray, Y: np.ndarray | None = None) -> np.ndarray:
    """Squared Euclidean distance; equals 2 - 2*cos for normalized rows."""
    Xn = l2_normalize(X)
    Yn = Xn if Y is None else l2_normalize(Y)
    D2 = np.sum(Xn * Xn, axis=1)[:, None] + np.sum(Yn * Yn, axis=1)[None, :] - 2.0 * (Xn @ Yn.T)
    return np.maximum(D2, 0.0)


def median_pairwise_distance(X: np.ndarray) -> float:
    """Median nonzero pairwise Euclidean distance."""
    D2 = pairwise_sq_euclidean(X)
    tri = D2[np.triu_indices(D2.shape[0], k=1)]
    tri = tri[np.isfinite(tri) & (tri > EPS)]
    if tri.size == 0:
        return 1.0
    return float(np.sqrt(np.median(tri)))


def mean_pairwise(X: np.ndarray, metric: str = "cosine") -> float:
    """Mean upper-triangle pairwise distance."""
    D = cosine_dist(X) if metric == "cosine" else cdist(np.asarray(X, dtype=float), np.asarray(X, dtype=float), metric=metric)
    tri = D[np.triu_indices(D.shape[0], k=1)]
    return float(np.nanmean(tri)) if tri.size else np.nan


def centroid_dispersion_loo(X: np.ndarray) -> float:
    """Mean Euclidean distance to the leave-one-out centroid."""
    Xn = l2_normalize(X)
    if Xn.shape[0] < 2:
        return np.nan
    vals = []
    for i in range(Xn.shape[0]):
        centroid = np.delete(Xn, i, axis=0).mean(axis=0)
        vals.append(np.linalg.norm(Xn[i] - centroid))
    return float(np.nanmean(vals))


def mst_dispersion(X: np.ndarray) -> float:
    """Mean edge length of the cosine-distance minimum spanning tree."""
    D = cosine_dist(X)
    tree = minimum_spanning_tree(D)
    return float(np.nanmean(tree.data)) if tree.data.size else np.nan


def sparseness(X: np.ndarray) -> float:
    """Mean cosine distance from each point to the group's medoid."""
    D = cosine_dist(X)
    if D.shape[0] < 2:
        return np.nan
    medoid = int(np.argmin(D.sum(axis=1)))
    return float(np.delete(D[medoid], medoid).mean())


def nn_isolation(X: np.ndarray) -> float:
    """Mean nearest-neighbor cosine distance."""
    return float(np.nanmean(nn_distances(X)))


def spherical_variance(X: np.ndarray) -> float:
    """Directional-statistics dispersion: 1 - norm of mean resultant vector."""
    Xn = l2_normalize(X)
    if Xn.shape[0] == 0:
        return np.nan
    return float(1.0 - np.linalg.norm(Xn.mean(axis=0)))


def vendi_scores(
    X: np.ndarray,
    qs: Iterable[float] = (0, 0.5, 1, 2, 4, np.inf),
    *,
    kernel: str = "cosine",
    sigma: float | None = None,
) -> Dict[float, float]:
    """Similarity-sensitive Hill-number / Vendi diversity profile."""
    Xn = l2_normalize(X)
    n = Xn.shape[0]
    if n == 0:
        return {float(q): np.nan for q in qs}
    if kernel == "cosine":
        K = Xn @ Xn.T
    elif kernel == "rbf":
        if sigma is None:
            sigma = median_pairwise_distance(Xn)
        K = np.exp(-pairwise_sq_euclidean(Xn) / (2.0 * sigma**2))
    else:
        raise ValueError(f"Unsupported kernel: {kernel}")

    Kn = K / float(n)
    w = np.linalg.eigvalsh(Kn)
    w = np.clip(w, 0.0, None)
    w = w[w > EPS]
    if w.size == 0:
        return {float(q): np.nan for q in qs}

    out: Dict[float, float] = {}
    for q_raw in qs:
        q = float(q_raw)
        if np.isclose(q, 1.0):
            out[q_raw] = float(np.exp(-np.sum(w * np.log(w))))
        elif np.isinf(q):
            out[q_raw] = float(1.0 / np.max(w))
        else:
            out[q_raw] = float(np.sum(w**q) ** (1.0 / (1.0 - q)))
    return out


def vendi_evenness_slope(scores: Dict[Any, float], q_low: float = 0, q_high: float = 2) -> float:
    """Log-profile slope; more negative values indicate lower evenness."""
    if q_low not in scores or q_high not in scores:
        return np.nan
    low = float(scores[q_low])
    high = float(scores[q_high])
    if low <= 0 or high <= 0:
        return np.nan
    return float((np.log(high) - np.log(low)) / (q_high - q_low))


def vendi_slope(scores: Dict[Any, float]) -> float:
    """Relative q=0 to q=2 Vendi-profile drop; larger means lower evenness."""
    if 0 not in scores or 2 not in scores:
        return np.nan
    low = float(scores[0])
    high = float(scores[2])
    if low <= 0:
        return np.nan
    return float((low - high) / low)


def _centered_spectrum(X: np.ndarray) -> np.ndarray:
    Xn = l2_normalize(X)
    if Xn.shape[0] < 2:
        return np.array([], dtype=float)
    Xc = Xn - Xn.mean(axis=0, keepdims=True)
    w = np.linalg.eigvalsh(Xc @ Xc.T)
    w = np.clip(w, 0.0, None)
    return w[w > EPS]


def participation_ratio(X: np.ndarray) -> float:
    """Effective dimensionality via participation ratio."""
    w = _centered_spectrum(X)
    if w.size == 0:
        return np.nan
    return float((w.sum() ** 2) / np.sum(w**2))


def effective_rank(X: np.ndarray) -> float:
    """Entropy effective rank of the centered covariance spectrum."""
    w = _centered_spectrum(X)
    if w.size == 0:
        return np.nan
    p = w / w.sum()
    return float(np.exp(-np.sum(p * np.log(p))))


def coverage_density(X_ref: np.ndarray, X_gen: np.ndarray, k: int = 3) -> Dict[str, float]:
    """Density-and-coverage estimator against a reference manifold."""
    Xr = l2_normalize(X_ref)
    Xg = l2_normalize(X_gen)
    if Xr.shape[0] < 2 or Xg.shape[0] == 0:
        return {"coverage": np.nan, "density": np.nan, "k": float(k)}
    k_eff = int(max(1, min(k, Xr.shape[0] - 1)))
    Dref = cosine_dist(Xr)
    np.fill_diagonal(Dref, np.inf)
    radius = np.sort(Dref, axis=1)[:, k_eff - 1]
    Dcross = cosine_dist(Xr, Xg)
    inside = Dcross < radius[:, None]
    coverage = float(np.mean(inside.any(axis=1)))
    density = float(inside.sum() / (k_eff * Xg.shape[0]))
    return {"coverage": coverage, "density": density, "k": float(k_eff)}


def loo_self_coverage(X: np.ndarray, k: int = 3) -> float:
    """Leave-one-out self-coverage of a small panel.

    Finite-sample human reference for review-panel coverage (spec 11.2): each point
    is held out and counted as covered iff it falls within the k'-NN radius of any
    remaining point, with k' = min(k, m - 2). Undefined (NaN) for m < 3.
    """
    Xn = l2_normalize(X)
    m = Xn.shape[0]
    if m < 3:
        return np.nan
    k_eff = int(max(1, min(k, m - 2)))
    covered = []
    for i in range(m):
        ref = np.delete(Xn, i, axis=0)
        Dref = cosine_dist(ref)
        np.fill_diagonal(Dref, np.inf)
        radius = np.sort(Dref, axis=1)[:, k_eff - 1]
        d_i = cosine_dist(ref, Xn[i : i + 1]).ravel()
        covered.append(bool(np.any(d_i < radius)))
    return float(np.mean(covered))


def nn_distances(X: np.ndarray, metric: str = "cosine") -> np.ndarray:
    """Per-point nearest-neighbor distance."""
    if metric != "cosine":
        D = cdist(np.asarray(X, dtype=float), np.asarray(X, dtype=float), metric=metric)
    else:
        D = cosine_dist(X)
    if D.shape[0] < 2:
        return np.full(D.shape[0], np.nan)
    np.fill_diagonal(D, np.inf)
    return D.min(axis=1)


def g_function(X: np.ndarray, radii: Iterable[float], metric: str = "cosine") -> np.ndarray:
    """Nearest-neighbor CDF evaluated at each radius."""
    nnd = nn_distances(X, metric=metric)
    return np.asarray([(nnd <= r).mean() for r in radii], dtype=float)


def ripley_K(X: np.ndarray, radii: Iterable[float], metric: str = "cosine") -> np.ndarray:
    """Mean neighbor count within each radius."""
    if metric != "cosine":
        D = cdist(np.asarray(X, dtype=float), np.asarray(X, dtype=float), metric=metric)
    else:
        D = cosine_dist(X)
    if D.shape[0] < 2:
        return np.full(len(list(radii)), np.nan)
    np.fill_diagonal(D, np.inf)
    return np.asarray([(D < r).sum(axis=1).mean() for r in radii], dtype=float)


def ripley_excess_area(X: np.ndarray, radii: Iterable[float], null_mean: np.ndarray | None = None) -> float:
    """Area under the observed K curve, optionally centered by a null mean."""
    radii_arr = np.asarray(list(radii), dtype=float)
    curve = ripley_K(X, radii_arr)
    y = curve if null_mean is None else curve - np.asarray(null_mean, dtype=float)
    if radii_arr.size < 2:
        return float(np.nanmean(y))
    return float(np.trapz(y, radii_arr))


def _rbf_kernel(X: np.ndarray, Y: np.ndarray, sigma: float) -> np.ndarray:
    return np.exp(-pairwise_sq_euclidean(X, Y) / (2.0 * sigma**2))


def mmd2_rbf(X: np.ndarray, Y: np.ndarray, sigma: float | None = None) -> float:
    """Unbiased two-sample MMD^2 with an RBF kernel."""
    Xn = l2_normalize(X)
    Yn = l2_normalize(Y)
    m, n = Xn.shape[0], Yn.shape[0]
    if m < 2 or n < 2:
        return np.nan
    if sigma is None:
        sigma = median_pairwise_distance(np.vstack([Xn, Yn]))
    sigma = float(max(sigma, EPS))
    Kxx = _rbf_kernel(Xn, Xn, sigma)
    Kyy = _rbf_kernel(Yn, Yn, sigma)
    Kxy = _rbf_kernel(Xn, Yn, sigma)
    sxx = (Kxx.sum() - np.trace(Kxx)) / (m * (m - 1))
    syy = (Kyy.sum() - np.trace(Kyy)) / (n * (n - 1))
    return float(max(0.0, sxx + syy - 2.0 * Kxy.mean()))


def wasserstein_ot(X: np.ndarray, Y: np.ndarray, metric: str = "cosine") -> float:
    """Empirical optimal-transport distance between two equally weighted clouds."""
    try:
        import ot
    except ImportError as exc:  # pragma: no cover - installation is environment-specific.
        raise ImportError("POT is required for wasserstein_ot; install with `pip install pot`.") from exc

    Xn = l2_normalize(X)
    Yn = l2_normalize(Y)
    if Xn.shape[0] == 0 or Yn.shape[0] == 0:
        return np.nan
    C = cosine_dist(Xn, Yn) if metric == "cosine" else cdist(Xn, Yn, metric=metric)
    a = np.ones(Xn.shape[0], dtype=float) / Xn.shape[0]
    b = np.ones(Yn.shape[0], dtype=float) / Yn.shape[0]
    return float(ot.emd2(a, b, C))


def region_coverage(topic_ids: Iterable[Any], n_regions_total: int) -> Dict[str, float]:
    """Coverage of BERTopic regions, excluding the -1 outlier/no-topic bin."""
    clean = {int(t) for t in topic_ids if int(t) != -1}
    denom = int(n_regions_total)
    return {
        "n_regions": int(len(clean)),
        "frac_regions": float(len(clean) / denom) if denom else np.nan,
    }


def mesh_coverage(mesh_sets: Iterable[Iterable[str]]) -> Dict[str, int]:
    """Union size of MeSH descriptors across a proposal group."""
    union = set()
    for terms in mesh_sets:
        union.update(str(term) for term in terms if str(term).strip())
    return {"n_mesh": int(len(union))}
