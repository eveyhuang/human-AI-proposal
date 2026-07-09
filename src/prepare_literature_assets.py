"""
Helpers for shared literature assets used in proposal analyses.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from prepare_proposals_for_analysis import (
    PROPOSAL_EMBEDDING_MODEL,
    build_embedding_bundle,
    embed_texts,
    load_pickle,
    save_pickle,
)


def load_literature_corpus(path: Path) -> Dict[str, Any]:
    """Load the raw literature corpus JSON payload."""
    return json.loads(path.read_text())


def compute_corpus_hash(payload: Dict[str, Any]) -> str:
    """Compute a stable hash for the normalized literature payload."""
    serial = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(serial).hexdigest()


def normalize_literature_articles(payload: Dict[str, Any]) -> pd.DataFrame:
    """Flatten literature articles into a stable article index."""
    records: List[Dict[str, Any]] = []
    for idx, article in enumerate(payload.get('articles', [])):
        publication_date = str(article.get('publication_date', '') or '')
        publication_year = None
        if publication_date[:4].isdigit():
            publication_year = int(publication_date[:4])
        records.append(
            {
                'article_idx': idx,
                'pmid': article.get('pmid'),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'publication_date': publication_date,
                'publication_year': publication_year,
                'mesh_terms': article.get('mesh_terms', []),
                'journal': article.get('journal'),
                'authors': article.get('authors', []),
            }
        )
    return pd.DataFrame(records)


def build_or_load_literature_embeddings(
    article_index: pd.DataFrame,
    *,
    output_path: Path,
    corpus_hash: str,
    model_name: str = PROPOSAL_EMBEDDING_MODEL,
    reuse_if_exists: bool = True,
) -> Dict[str, Any]:
    """Build or load the shared literature embedding payload."""
    texts = [
        f"Title: {row['title']}\n\nAbstract: {row['abstract']}"
        for _, row in article_index.fillna('').iterrows()
    ]
    if reuse_if_exists and output_path.exists():
        payload = load_pickle(output_path)
        if payload.get('corpus_hash') == corpus_hash and payload.get('model_name') == model_name:
            return payload
    payload = {
        'embeddings': embed_texts(texts, model_name=model_name, pooling='cls'),
        'texts': texts,
        'article_index': article_index.copy(),
        'model_name': model_name,
        'corpus_hash': corpus_hash,
        'timestamp': datetime.now().isoformat(),
    }
    save_pickle(output_path, payload)
    return payload


def fit_or_load_literature_bertopic(
    article_index: pd.DataFrame,
    embedding_payload: Dict[str, Any],
    *,
    model_path: Path,
    assignments_path: Path,
    topic_info_path: Path,
    reuse_if_exists: bool = True,
) -> Tuple[Any, pd.DataFrame, pd.DataFrame]:
    """Fit or load BERTopic region assignments on literature embeddings only."""
    if reuse_if_exists and model_path.exists() and assignments_path.exists() and topic_info_path.exists():
        model = load_pickle(model_path)
        return model, pd.read_csv(assignments_path), pd.read_csv(topic_info_path)

    from bertopic import BERTopic
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.feature_extraction.text import CountVectorizer
    import umap as umap_lib

    embeddings = np.asarray(embedding_payload['embeddings'], dtype=np.float32)
    texts = embedding_payload['texts']
    umap_model = umap_lib.UMAP(
        n_neighbors=20,
        min_dist=0.0,
        n_components=5,
        metric='cosine',
        random_state=42,
        low_memory=True,
    )
    cluster_model = MiniBatchKMeans(n_clusters=12, random_state=42, batch_size=1024)
    vectorizer_model = CountVectorizer(stop_words='english', min_df=8, max_df=0.60, ngram_range=(1, 2), max_features=50000)
    topic_model = BERTopic(
        embedding_model=None,
        umap_model=umap_model,
        hdbscan_model=cluster_model,
        vectorizer_model=vectorizer_model,
        calculate_probabilities=False,
        verbose=True,
    )
    topics, _ = topic_model.fit_transform(texts, embeddings=embeddings)
    topic_info = topic_model.get_topic_info().copy()
    if 'Name' in topic_info.columns and 'display_label' not in topic_info.columns:
        topic_info['display_label'] = topic_info['Name']
    assignments = article_index[['article_idx', 'pmid', 'title']].copy()
    assignments['bertopic_topic'] = np.asarray(topics, dtype=int)
    assignments['display_label'] = assignments['bertopic_topic'].map(
        topic_info.set_index('Topic')['display_label'].to_dict()
    )

    save_pickle(model_path, topic_model)
    assignments.to_csv(assignments_path, index=False)
    topic_info.to_csv(topic_info_path, index=False)
    return topic_model, assignments, topic_info


def fit_or_load_literature_umap(
    embedding_payload: Dict[str, Any],
    *,
    reducer_path: Path,
    coords_path: Path,
    reuse_if_exists: bool = True,
) -> Tuple[Any, np.ndarray]:
    """Fit or load the shared literature-only UMAP reducer and coordinates."""
    if reuse_if_exists and reducer_path.exists() and coords_path.exists():
        return load_pickle(reducer_path), np.load(coords_path)
    import umap as umap_lib

    embeddings = np.asarray(embedding_payload['embeddings'], dtype=np.float32)
    reducer = umap_lib.UMAP(
        n_neighbors=20,
        min_dist=0.1,
        n_components=2,
        metric='cosine',
        random_state=42,
        low_memory=True,
    )
    coords = reducer.fit_transform(embeddings)
    save_pickle(reducer_path, reducer)
    np.save(coords_path, coords)
    return reducer, coords


def write_literature_manifest(path: Path, payload: Dict[str, Any]) -> None:
    """Write the shared literature preparation manifest."""
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


__all__ = [
    'build_or_load_literature_embeddings',
    'compute_corpus_hash',
    'fit_or_load_literature_bertopic',
    'fit_or_load_literature_umap',
    'load_literature_corpus',
    'normalize_literature_articles',
    'write_literature_manifest',
]
