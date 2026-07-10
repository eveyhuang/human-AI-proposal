"""
Helpers for the redesigned proposal-preparation stage.
"""

from __future__ import annotations

import json
import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_distances

from proposal_generation import build_target_proposal_uid, find_project_root, latest_matching_file


PROPOSAL_EMBEDDING_MODEL = 'michiyasunaga/BioLinkBERT-large'
PROPOSAL_TO_LITERATURE_K = 50
MODEL_DISPLAY_NAME_MAP = {
    'claude-sonnet-5': 'Claude',
    'claude-opus-4-5': 'Claude',
    'gemini-3.1-pro-preview': 'Gemini',
    'gemini-3-pro-preview': 'Gemini',
    'gpt-5.5': 'GPT',
    'gpt-5.2': 'GPT',
    'human': 'Human',
}


def _latest_non_failures_csv(directory: Path, pattern: str) -> Optional[Path]:
    """Latest CSV matching pattern, excluding *_failures.csv.

    The '*' in these rephrased-output globs also matches the sibling failures
    CSV, and since '.' < '_' it sorts last, so a naive latest-match would pick
    the failures file (which lacks the expected proposal columns).
    """
    matches = [
        p for p in sorted(directory.glob(pattern))
        if not p.name.endswith('_failures.csv')
    ]
    return matches[-1] if matches else None


def normalize_title(title: Any) -> str:
    """Create a lightweight normalized title string for QA checks."""
    if pd.isna(title):
        return ''
    normalized = str(title).strip().lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    return re.sub(r'[^a-z0-9 ]', '', normalized)


def strip_section_headers(text: Any) -> str:
    """Remove known section headers from rephrased proposal text."""
    cleaned = '' if pd.isna(text) else str(text)
    headers = [
        'SCIENTIFIC BACKGROUND AND RESEARCH QUESTION',
        'METHODOLOGY AND ANALYTICAL APPROACH',
        'DATA SOURCES AND SYNTHESIS PLAN',
        'FEASIBILITY AND TIMELINE',
        'OPEN SCIENCE AND TEAM COMPOSITION',
    ]
    for header in headers:
        cleaned = re.sub(rf'^\s*{re.escape(header)}\s*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    return re.sub(r'\n{3,}', '\n\n', cleaned).strip()


def locate_latest_proposal_files(project_root: Path, condition: str) -> Dict[str, Path]:
    """Locate the latest original and rephrased AI proposal files for one condition."""
    original_dir = project_root / 'data' / 'ai-proposals' / condition
    rephrased_dir = original_dir / 'rephrased'
    original = latest_matching_file(original_dir, f'ai_proposals_{condition}_complete_*.csv')
    rephrased = _latest_non_failures_csv(rephrased_dir, f'ai_proposals_{condition}_rephrased_*.csv')
    if original is None:
        raise FileNotFoundError(f'Missing original AI proposal CSV for {condition} in {original_dir}')
    if rephrased is None:
        raise FileNotFoundError(f'Missing rephrased AI proposal CSV for {condition} in {rephrased_dir}')
    return {'original': original, 'rephrased': rephrased}


def load_ai_original_proposals(path: Path, condition: str) -> pd.DataFrame:
    """Load original AI proposals and coerce required canonical columns."""
    df = pd.read_csv(path).copy()
    if 'condition' not in df.columns:
        df['condition'] = condition
    if 'model' not in df.columns and 'author' in df.columns:
        df['model'] = df['author']
    if 'author' not in df.columns and 'model' in df.columns:
        df['author'] = df['model']
    if 'proposal_uid' not in df.columns:
        generated: List[str] = []
        for model_name, group in df.groupby('model', sort=False):
            for draw_index, idx in enumerate(group.index, start=1):
                generated.append((idx, f'{condition}::{model_name}::{draw_index:02d}'))
        df['proposal_uid'] = df.index.to_series().map(pd.Series(dict(generated)))
    if 'idea_uid' not in df.columns:
        df['idea_uid'] = df['proposal_uid']
    if 'idea_index' not in df.columns:
        df['idea_index'] = df.groupby('model').cumcount() + 1
    if 'generation_mode' not in df.columns:
        df['generation_mode'] = condition if condition != 'baseline' else 'batch'
    if 'temperature' not in df.columns:
        df['temperature'] = np.nan
    if 'prompt_template' not in df.columns:
        df['prompt_template'] = ''
    if 'open_science_and_reproducibility' not in df.columns:
        df['open_science_and_reproducibility'] = ''
    for col in ['persona_card_id', 'matched_human_proposal_uid', 'proposal_generated_at']:
        if col not in df.columns:
            df[col] = ''
    return df


def load_ai_rephrased_proposals(path: Path, condition: str) -> pd.DataFrame:
    """Load rephrased AI proposals and coerce required canonical columns."""
    df = pd.read_csv(path).copy()
    if 'condition' not in df.columns:
        df['condition'] = condition
    if 'proposal_uid' not in df.columns:
        df = load_ai_original_proposals(path, condition)
    if 'standardized_text' not in df.columns:
        df['standardized_text'] = ''
    if 'rephrased_abstract' not in df.columns:
        df['rephrased_abstract'] = ''
    if 'proposal_rephrased_at' not in df.columns:
        df['proposal_rephrased_at'] = ''
    return df


def load_human_original_proposals(project_root: Path) -> pd.DataFrame:
    """Load pooled original human proposals with stable proposal_uid values."""
    records: List[Dict[str, Any]] = []
    for cohort, filename in [('y1', 'human-proposals-y1.json'), ('y2', 'human-proposals-y2.json')]:
        payload = json.loads((project_root / 'data' / 'human-proposals' / filename).read_text())
        for proposal in payload.get('proposals', []):
            records.append(
                {
                    'proposal_uid': build_target_proposal_uid(cohort, proposal.get('proposal_id')),
                    'cohort': cohort,
                    'proposal_id': proposal.get('proposal_id'),
                    'proposal_title': proposal.get('proposal_title', ''),
                    'abstract': proposal.get('abstract', ''),
                    'full_draft': proposal.get('full_draft', ''),
                    'proposal_status': proposal.get('proposal_status', ''),
                    'ranking': proposal.get('ranking'),
                    'authors': '; '.join(proposal.get('authors', []) or []),
                    'source_file': filename,
                }
            )
    return pd.DataFrame(records).sort_values(['cohort', 'proposal_id']).reset_index(drop=True)


def load_human_rephrased_proposals(project_root: Path) -> pd.DataFrame:
    """Load pooled rephrased human proposals from the latest cohort files."""
    out_frames: List[pd.DataFrame] = []
    base_dir = project_root / 'data' / 'human-proposals' / 'rephrased'
    for cohort in ['y1', 'y2']:
        latest_json = latest_matching_file(base_dir, f'human_proposals_rephrased_{cohort}_*.json')
        latest_csv = _latest_non_failures_csv(base_dir, f'human_proposals_rephrased_{cohort}_*.csv')
        if latest_csv is not None:
            df = pd.read_csv(latest_csv)
        elif latest_json is not None:
            payload = json.loads(latest_json.read_text())
            df = pd.DataFrame(payload.get('proposals', []))
        else:
            raise FileNotFoundError(f'Missing rephrased human proposal artifacts for {cohort} in {base_dir}')
        if 'proposal_uid' not in df.columns:
            df['proposal_uid'] = df.apply(
                lambda row: build_target_proposal_uid(cohort, row.get('proposal_id')),
                axis=1,
            )
        if 'standardized_text' not in df.columns:
            df['standardized_text'] = ''
        if 'rephrased_abstract' not in df.columns:
            df['rephrased_abstract'] = ''
        if 'proposal_rephrased_at' not in df.columns:
            df['proposal_rephrased_at'] = ''
        out_frames.append(df)
    return pd.concat(out_frames, ignore_index=True, sort=False)


def validate_proposal_alignment(original_df: pd.DataFrame, rephrased_df: pd.DataFrame, scope: str) -> List[str]:
    """Validate proposal alignment between original and rephrased datasets."""
    issues: List[str] = []
    if original_df['proposal_uid'].duplicated().any():
        issues.append(f'{scope}: duplicate proposal_uid values in original data')
    if rephrased_df['proposal_uid'].duplicated().any():
        issues.append(f'{scope}: duplicate proposal_uid values in rephrased data')

    orig_ids = list(original_df['proposal_uid'].astype(str))
    repr_ids = list(rephrased_df['proposal_uid'].astype(str))
    if sorted(orig_ids) != sorted(repr_ids):
        issues.append(f'{scope}: original and rephrased proposal_uid sets do not match')

    merged = original_df[['proposal_uid', 'title']].merge(
        rephrased_df[['proposal_uid', 'title']],
        on='proposal_uid',
        how='inner',
        suffixes=('_orig', '_repr'),
    )
    if not merged.empty:
        mismatched = (
            merged['title_orig'].fillna('').map(normalize_title)
            != merged['title_repr'].fillna('').map(normalize_title)
        )
        if mismatched.any():
            # Title drift is a warning, not a fatal error. Proposals are paired by
            # proposal_uid (validated above via the uid-set and duplicate checks),
            # so a rewritten title does not break the pairing. Legacy rephrase runs
            # (e.g. the original baseline) rewrote titles wholesale; newer runs
            # preserve them, so drift there would be 0.
            print(
                f'  WARNING {scope}: title normalization drift on '
                f'{int(mismatched.sum())}/{len(merged)} matched proposals '
                f'(pairing is by proposal_uid, not title).'
            )
    return issues


def assemble_full_text(row: pd.Series, text_version: str) -> str:
    """Assemble the proposal full text for the selected branch."""
    if text_version == 'rephrased':
        return strip_section_headers(row.get('standardized_text', ''))
    parts: List[str] = []
    section_map = [
        ('abstract', 'Abstract'),
        ('background_and_significance', 'Background and Significance'),
        ('research_questions_and_hypotheses', 'Research Questions and Hypotheses'),
        ('methods_and_approach', 'Methods and Approach'),
        ('expected_outcomes_and_impact', 'Expected Outcomes and Impact'),
        ('open_science_and_reproducibility', 'Open Science and Reproducibility'),
        ('budget_and_resources', 'Budget and Resources'),
        ('full_draft', 'Full Proposal'),
    ]
    for field, label in section_map:
        value = str(row.get(field, '') or '').strip()
        if value and value.lower() not in {'nan', 'none'}:
            parts.append(f'[{label}]\n{value}')
    return '\n\n'.join(parts)


def _display_group(model_name: Any, source_type: str) -> str:
    if source_type == 'human':
        return 'Human'
    return MODEL_DISPLAY_NAME_MAP.get(str(model_name), str(model_name))


def _is_funded(status: Any) -> Optional[bool]:
    if pd.isna(status):
        return None
    lowered = str(status).strip().lower()
    if lowered == '':
        return None
    return any(token in lowered for token in ['fund', 'selected', 'awarded'])


def _is_top5(rank: Any) -> Optional[bool]:
    try:
        if pd.isna(rank):
            return None
        return float(rank) <= 5
    except Exception:
        return None


def build_proposal_master_table(
    *,
    condition: str,
    text_version: str,
    ai_original_df: pd.DataFrame,
    ai_rephrased_df: pd.DataFrame,
    human_original_df: pd.DataFrame,
    human_rephrased_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build the canonical proposal master table for one condition and branch."""
    ai_alignment = validate_proposal_alignment(ai_original_df, ai_rephrased_df, f'ai::{condition}')
    human_alignment = validate_proposal_alignment(human_original_df.rename(columns={'proposal_title': 'title'}), human_rephrased_df.rename(columns={'proposal_title': 'title'}), 'human')
    if ai_alignment or human_alignment:
        raise RuntimeError('Proposal alignment failed: ' + '; '.join(ai_alignment + human_alignment))

    ai_join = ai_original_df.merge(
        ai_rephrased_df[['proposal_uid', 'standardized_text', 'rephrased_abstract', 'proposal_rephrased_at']],
        on='proposal_uid',
        how='left',
        validate='one_to_one',
    )
    human_join = human_original_df.merge(
        human_rephrased_df[['proposal_uid', 'standardized_text', 'rephrased_abstract', 'proposal_rephrased_at']],
        on='proposal_uid',
        how='left',
        validate='one_to_one',
    )

    ai_rows: List[Dict[str, Any]] = []
    for row in ai_join.to_dict('records'):
        ai_rows.append(
            {
                'proposal_uid': row['proposal_uid'],
                'condition': condition,
                'text_version': text_version,
                'source_type': 'ai',
                'source_group': _display_group(row.get('model'), 'ai'),
                'model': row.get('model', ''),
                'cohort': 'ai',
                'proposal_id': None,
                'title': row.get('title', ''),
                'title_norm': normalize_title(row.get('title', '')),
                'abstract_text': row.get('rephrased_abstract', '') if text_version == 'rephrased' else row.get('abstract', ''),
                'full_text': assemble_full_text(pd.Series(row), text_version),
                'proposal_status': None,
                'ranking': None,
                'is_funded_human': None,
                'is_top5_ranked_human': None,
                'authors': '',
                'idea_uid': row.get('idea_uid', row['proposal_uid']),
                'idea_index': row.get('idea_index'),
                'generation_mode': row.get('generation_mode', ''),
                'temperature': row.get('temperature'),
                'prompt_template': row.get('prompt_template', ''),
                'persona_card_id': row.get('persona_card_id', ''),
                'matched_human_proposal_uid': row.get('matched_human_proposal_uid', ''),
                'proposal_generated_at': row.get('proposal_generated_at', row.get('generated_at', '')),
                'rephrased_at': row.get('proposal_rephrased_at', ''),
                'standardized_text': row.get('standardized_text', ''),
                'rephrased_abstract': row.get('rephrased_abstract', ''),
                'abstract_original': row.get('abstract', ''),
            }
        )

    human_rows: List[Dict[str, Any]] = []
    for row in human_join.to_dict('records'):
        human_rows.append(
            {
                'proposal_uid': row['proposal_uid'],
                'condition': condition,
                'text_version': text_version,
                'source_type': 'human',
                'source_group': 'Human',
                'model': 'human',
                'cohort': row.get('cohort', ''),
                'proposal_id': row.get('proposal_id'),
                'title': row.get('proposal_title', row.get('title', '')),
                'title_norm': normalize_title(row.get('proposal_title', row.get('title', ''))),
                'abstract_text': row.get('rephrased_abstract', '') if text_version == 'rephrased' else row.get('abstract', ''),
                'full_text': assemble_full_text(pd.Series(row), text_version),
                'proposal_status': row.get('proposal_status', ''),
                'ranking': row.get('ranking'),
                'is_funded_human': _is_funded(row.get('proposal_status')),
                'is_top5_ranked_human': _is_top5(row.get('ranking')),
                'authors': row.get('authors', ''),
                'idea_uid': None,
                'idea_index': None,
                'generation_mode': None,
                'temperature': None,
                'prompt_template': None,
                'persona_card_id': None,
                'matched_human_proposal_uid': None,
                'proposal_generated_at': None,
                'rephrased_at': row.get('proposal_rephrased_at', ''),
                'standardized_text': row.get('standardized_text', ''),
                'rephrased_abstract': row.get('rephrased_abstract', ''),
                'abstract_original': row.get('abstract', ''),
            }
        )

    master_df = pd.DataFrame(human_rows + ai_rows)
    source_order = {'human': 0, 'ai': 1}
    master_df['_source_order'] = master_df['source_type'].map(source_order)
    master_df = master_df.sort_values(['_source_order', 'source_group', 'proposal_uid']).drop(columns=['_source_order']).reset_index(drop=True)
    return master_df


def save_pickle(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as handle:
        pickle.dump(payload, handle)


def load_pickle(path: Path) -> Any:
    with open(path, 'rb') as handle:
        return pickle.load(handle)


tokenizer = None
embedding_model = None
embedding_device = None


def ensure_embedding_model_loaded(model_name: str = PROPOSAL_EMBEDDING_MODEL):
    """Lazily load the transformer embedding model."""
    global tokenizer, embedding_model, embedding_device
    if tokenizer is not None and embedding_model is not None:
        return tokenizer, embedding_model, embedding_device
    import torch
    from transformers import AutoModel, AutoTokenizer

    embedding_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    embedding_model = AutoModel.from_pretrained(model_name).to(embedding_device)
    embedding_model.eval()
    return tokenizer, embedding_model, embedding_device


def embed_texts(
    texts: List[str],
    *,
    model_name: str = PROPOSAL_EMBEDDING_MODEL,
    batch_size: int = 8,
    max_len: int = 512,
    pooling: str = 'cls',
) -> np.ndarray:
    """Embed texts with BioLinkBERT using cls or mean pooling."""
    import torch
    from tqdm import tqdm

    tokenizer_obj, model_obj, device = ensure_embedding_model_loaded(model_name)
    clean_texts = ['' if pd.isna(text) else str(text) for text in texts]
    all_embeddings: List[np.ndarray] = []
    with torch.no_grad():
        for i in tqdm(range(0, len(clean_texts), batch_size), desc='Embedding texts'):
            batch = clean_texts[i:i + batch_size]
            encoded = tokenizer_obj(
                batch,
                padding=True,
                truncation=True,
                max_length=max_len,
                return_tensors='pt',
            ).to(device)
            outputs = model_obj(**encoded)
            if pooling == 'mean':
                attn = encoded['attention_mask'].unsqueeze(-1)
                masked = outputs.last_hidden_state * attn
                denom = attn.sum(dim=1).clamp(min=1)
                emb = masked.sum(dim=1) / denom
                emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            else:
                emb = outputs.last_hidden_state[:, 0, :]
            all_embeddings.append(emb.cpu().numpy())
    return np.vstack(all_embeddings)


def build_embedding_bundle(
    df: pd.DataFrame,
    *,
    text_field: str,
    output_path: Path,
    model_name: str = PROPOSAL_EMBEDDING_MODEL,
    pooling: str = 'cls',
    reuse_if_exists: bool = True,
) -> Dict[str, Any]:
    """Build or load one aligned embedding bundle for a proposal master table."""
    proposal_uids = df['proposal_uid'].astype(str).tolist()
    texts = df[text_field].fillna('').astype(str).tolist()
    metadata = df[['proposal_uid', 'source_type', 'source_group', 'model', 'title', 'cohort', 'condition', 'text_version']].to_dict('records')
    if reuse_if_exists and output_path.exists():
        payload = load_pickle(output_path)
        if payload.get('proposal_uids') == proposal_uids and payload.get('text_field') == text_field:
            return payload
    payload = {
        'embeddings': embed_texts(texts, model_name=model_name, pooling=pooling),
        'proposal_uids': proposal_uids,
        'texts': texts,
        'metadata': metadata,
        'model_name': model_name,
        'text_field': text_field,
        'pooling': pooling,
        'timestamp': datetime.now().isoformat(),
    }
    save_pickle(output_path, payload)
    return payload


def compute_pairwise_cosine_matrix(embedding_bundle: Dict[str, Any], output_path: Path) -> np.ndarray:
    """Compute and save one square pairwise cosine-distance matrix."""
    embeddings = np.asarray(embedding_bundle['embeddings'], dtype=np.float32)
    pairwise = cosine_distances(embeddings)
    np.save(output_path, pairwise)
    return pairwise


def fit_or_load_proposal_umap(
    embedding_bundle: Dict[str, Any],
    *,
    reducer_path: Path,
    coords_path: Path,
    reuse_if_exists: bool = True,
) -> Tuple[Any, np.ndarray]:
    """Fit or load a proposal-space UMAP reducer and coordinates."""
    if reuse_if_exists and reducer_path.exists() and coords_path.exists():
        return load_pickle(reducer_path), np.load(coords_path)
    import umap as umap_lib

    embeddings = np.asarray(embedding_bundle['embeddings'], dtype=np.float32)
    reducer = umap_lib.UMAP(
        n_neighbors=15,
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


def compute_or_load_proposal_to_literature_knn(
    proposal_embedding_bundle: Dict[str, Any],
    literature_embedding_bundle: Dict[str, Any],
    *,
    output_path: Path,
    k: int = PROPOSAL_TO_LITERATURE_K,
    reuse_if_exists: bool = True,
) -> Dict[str, Any]:
    """Compute or load proposal-to-literature nearest-neighbor caches."""
    proposal_uids = proposal_embedding_bundle['proposal_uids']
    literature_indices = literature_embedding_bundle['article_index']['article_idx'].astype(int).tolist()
    if reuse_if_exists and output_path.exists():
        payload = np.load(output_path, allow_pickle=True)
        if payload['proposal_uids'].tolist() == proposal_uids and payload['article_idx'].tolist() == literature_indices:
            return {key: payload[key] for key in payload.files}

    prop = np.asarray(proposal_embedding_bundle['embeddings'], dtype=np.float32)
    lit = np.asarray(literature_embedding_bundle['embeddings'], dtype=np.float32)
    distances = cosine_distances(prop, lit)
    nn_idx = np.argsort(distances, axis=1)[:, :k]
    nn_dist = np.take_along_axis(distances, nn_idx, axis=1)
    payload = {
        'proposal_uids': np.array(proposal_uids, dtype=object),
        'article_idx': np.array(literature_indices, dtype=int),
        'neighbor_idx': nn_idx.astype(np.int32),
        'neighbor_distance': nn_dist.astype(np.float32),
        'k': np.array(k, dtype=np.int32),
        'text_field': np.array(proposal_embedding_bundle['text_field'], dtype=object),
        'built_from': np.array('abstract_text', dtype=object),
        'timestamp': np.array(datetime.now().isoformat(), dtype=object),
    }
    np.savez(output_path, **payload)
    return payload


def write_prepare_manifest(path: Path, payload: Dict[str, Any]) -> None:
    """Write the proposal-preparation manifest."""
    # default=str keeps the writer robust to Path (and other non-JSON) values.
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


__all__ = [
    'PROPOSAL_EMBEDDING_MODEL',
    'PROPOSAL_TO_LITERATURE_K',
    'assemble_full_text',
    'build_embedding_bundle',
    'build_proposal_master_table',
    'compute_or_load_proposal_to_literature_knn',
    'compute_pairwise_cosine_matrix',
    'find_project_root',
    'fit_or_load_proposal_umap',
    'load_ai_original_proposals',
    'load_ai_rephrased_proposals',
    'load_human_original_proposals',
    'load_human_rephrased_proposals',
    'locate_latest_proposal_files',
    'normalize_title',
    'save_pickle',
    'load_pickle',
    'validate_proposal_alignment',
    'write_prepare_manifest',
]
