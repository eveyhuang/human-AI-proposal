"""
Helpers for the redesigned review-preparation stage.
"""

from __future__ import annotations

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_distances

from prepare_proposals_for_analysis import (
    MODEL_DISPLAY_NAME_MAP,
    PROPOSAL_EMBEDDING_MODEL,
    embed_texts,
    fit_or_load_proposal_umap,
    load_pickle,
    save_pickle,
)
from proposal_generation import build_target_proposal_uid, find_project_root, latest_matching_file
from rephrase_reviews import build_human_review_text_sheet1


AI_REVIEW_EXPECTED_ROWS = 345
AI_REVIEW_EXPECTED_PER_MODEL = 5
AI_REVIEW_EXPECTED_POOLED = 15

AI_CRITERION_SCORE_MAP = {
    'relevance_to_emergent_phenomena_score': 'score_relevance_to_emergent_phenomena',
    'novelty_and_significance_score': 'score_novelty_and_significance',
    'rigor_of_approach_score': 'score_rigor_of_approach',
    'scope_and_timeline_score': 'score_scope_and_timeline',
    'synthesis_focus_score': 'score_synthesis_focus',
    'data_identification_score': 'score_data_identification',
    'open_science_commitment_score': 'score_open_science_commitment',
}
AI_CRITERION_JUSTIFICATION_MAP = {
    'relevance_to_emergent_phenomena_justification': 'justification_relevance_to_emergent_phenomena',
    'novelty_and_significance_justification': 'justification_novelty_and_significance',
    'rigor_of_approach_justification': 'justification_rigor_of_approach',
    'scope_and_timeline_justification': 'justification_scope_and_timeline',
    'synthesis_focus_justification': 'justification_synthesis_focus',
    'data_identification_justification': 'justification_data_identification',
    'open_science_commitment_justification': 'justification_open_science_commitment',
}
HUMAN_CRITERION_SCORE_MAP = {
    'scientific_merit_and_innovation_score': 'score_novelty_and_significance',
    'feasibility_score': 'score_scope_and_timeline',
    'data_sources_and_limitations_score': 'score_data_identification',
    'open_science_compliance_score': 'score_open_science_commitment',
}
HUMAN_CRITERION_JUSTIFICATION_MAP = {
    'scientific_merit_and_innovation_justification': 'justification_novelty_and_significance',
    'feasibility_justification': 'justification_scope_and_timeline',
    'data_sources_and_limitations_justification': 'justification_data_identification',
    'open_science_compliance_justification': 'justification_open_science_commitment',
}
CANONICAL_SCORE_COLUMNS = list(dict.fromkeys(list(AI_CRITERION_SCORE_MAP.values()) + list(HUMAN_CRITERION_SCORE_MAP.values())))
CANONICAL_JUSTIFICATION_COLUMNS = list(dict.fromkeys(list(AI_CRITERION_JUSTIFICATION_MAP.values()) + list(HUMAN_CRITERION_JUSTIFICATION_MAP.values())))


def locate_latest_ai_review_files(project_root: Path, condition: str) -> Dict[str, Path]:
    """Locate the latest original and rephrased AI review files for one condition."""
    original_dir = project_root / 'data' / 'reviews' / 'ai_reviews' / condition
    rephrased_dir = original_dir / 'rephrased'
    original = latest_matching_file(original_dir, f'ai_reviews_{condition}_complete_*.csv')
    rephrased = latest_matching_file(rephrased_dir, f'ai_reviews_{condition}_rephrased_*.csv')
    if original is None:
        raise FileNotFoundError(f'Missing original AI review CSV for {condition} in {original_dir}')
    if rephrased is None:
        raise FileNotFoundError(f'Missing rephrased AI review CSV for {condition} in {rephrased_dir}')
    return {'original': original, 'rephrased': rephrased}


def build_human_target_proposal_lookup(project_root: Path) -> pd.DataFrame:
    """Build pooled human proposal metadata used to attach target-proposal fields to reviews."""
    rows: List[Dict[str, Any]] = []
    for cohort, filename in [('y1', 'human-proposals-y1.json'), ('y2', 'human-proposals-y2.json')]:
        payload = json.loads((project_root / 'data' / 'human-proposals' / filename).read_text())
        for proposal in payload.get('proposals', []):
            status = proposal.get('proposal_status', '')
            rows.append(
                {
                    'target_proposal_uid': build_target_proposal_uid(cohort, proposal.get('proposal_id')),
                    'target_cohort': cohort,
                    'target_proposal_id': str(proposal.get('proposal_id')),
                    'target_proposal_title': proposal.get('proposal_title', ''),
                    'target_proposal_status': status,
                    'target_authors': '; '.join(proposal.get('authors', []) or []),
                    'target_ranking': proposal.get('ranking'),
                    'target_funding': any(token in str(status).lower() for token in ['fund', 'selected', 'award']),
                }
            )
    df = pd.DataFrame(rows).sort_values(['target_cohort', 'target_proposal_id']).reset_index(drop=True)
    return df


def build_deterministic_human_review_uid(row: pd.Series) -> str:
    """Build a stable review_uid for human reviews."""
    return f"{row['target_cohort']}::{str(row['target_proposal_id'])}::{row['reviewer_id']}::{int(row['review_occurrence']):02d}"


def _coerce_human_occurrence(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out['review_occurrence'] = (
        out.groupby(['target_cohort', 'target_proposal_id', 'reviewer_id']).cumcount() + 1
    )
    return out


def load_human_original_reviews(project_root: Path) -> pd.DataFrame:
    """Load pooled original human reviews with deterministic review_uid values."""
    lookup = build_human_target_proposal_lookup(project_root)
    frames: List[pd.DataFrame] = []
    for cohort_label, workbook_name in [('human-y1', 'human_reviews_human-y1.xlsx'), ('human-y2', 'human_reviews_human-y2.xlsx')]:
        source_path = project_root / 'data' / 'reviews' / 'human_reviews' / workbook_name
        df = pd.read_excel(source_path, sheet_name='Sheet1')
        df = df.copy()
        df['target_cohort'] = 'y1' if cohort_label == 'human-y1' else 'y2'
        df['target_proposal_id'] = df['id'].astype(str)
        df['target_proposal_uid'] = df.apply(
            lambda row: build_target_proposal_uid(df.at[row.name, 'target_cohort'], row['id']),
            axis=1,
        )
        df['_source_file'] = workbook_name
        df['_source_sheet'] = 'Sheet1'
        df['_row_index'] = df.index.astype(int)
        df['_raw_review_text'] = df.apply(build_human_review_text_sheet1, axis=1)
        df = _coerce_human_occurrence(df)
        df['review_uid'] = df.apply(build_deterministic_human_review_uid, axis=1)
        df['review_family'] = 'ncems_criteria'
        df['review_source'] = 'human'
        df['source_group'] = 'Human'
        df['source_family'] = 'human'
        df['evaluator_model'] = cohort_label
        df['review_draw_index'] = pd.NA
        df['review_generated_at'] = pd.NA
        df['review_prompt_template'] = pd.NA
        df['review_prompt_version'] = pd.NA
        df['review_temperature'] = pd.NA
        df['parse_success'] = True
        df['parse_error'] = ''
        df['retry_count'] = 0
        df['raw_response'] = ''
        df['overall_score'] = pd.to_numeric(df.get('overall_rating_score'), errors='coerce')
        df['original_review_text'] = df['_raw_review_text']
        df['review_text'] = df['_raw_review_text']
        df['strengths'] = pd.NA
        df['weakness'] = pd.NA
        df['overall_summary'] = df.get('overall_rating_summary', '')
        for source_col, target_col in HUMAN_CRITERION_SCORE_MAP.items():
            df[target_col] = pd.to_numeric(df.get(source_col), errors='coerce')
        for source_col, target_col in HUMAN_CRITERION_JUSTIFICATION_MAP.items():
            df[target_col] = df.get(source_col, '')
        frames.append(df)
    human_df = pd.concat(frames, ignore_index=True, sort=False)
    counts = human_df.groupby('target_proposal_uid').size().rename('target_human_n_reviews').reset_index()
    human_df = human_df.merge(counts, on='target_proposal_uid', how='left', validate='many_to_one')
    human_df = human_df.merge(lookup, on=['target_proposal_uid', 'target_cohort', 'target_proposal_id'], how='left', validate='many_to_one')
    return human_df


def load_human_rephrased_reviews(project_root: Path) -> pd.DataFrame:
    """Load pooled rephrased human reviews and rebuild deterministic review_uid values."""
    frames: List[pd.DataFrame] = []
    base_dir = project_root / 'data' / 'reviews' / 'human_reviews' / 'rephrased'
    for cohort_label in ['human-y1', 'human-y2']:
        latest = latest_matching_file(base_dir, f'human_reviews_{cohort_label}_rephrased_*.csv')
        if latest is None:
            legacy = base_dir / f'human_reviews_{cohort_label}_rephrased.csv'
            if legacy.exists():
                latest = legacy
        if latest is None:
            raise FileNotFoundError(f'Missing rephrased human reviews for {cohort_label} in {base_dir}')
        df = pd.read_csv(latest)
        df = df.copy()
        df['target_cohort'] = 'y1' if cohort_label == 'human-y1' else 'y2'
        df['target_proposal_id'] = df['id'].astype(str)
        df = _coerce_human_occurrence(df)
        df['review_uid'] = df.apply(build_deterministic_human_review_uid, axis=1)
        df['target_proposal_uid'] = df.apply(
            lambda row: build_target_proposal_uid(df.at[row.name, 'target_cohort'], row['id']),
            axis=1,
        )
        if 'review_rephrased_at' not in df.columns:
            df['review_rephrased_at'] = pd.NA
        if 'review_rephrase_status' not in df.columns:
            df['review_rephrase_status'] = 'success'
        frames.append(df)
    return pd.concat(frames, ignore_index=True, sort=False)


def load_ai_original_reviews(path: Path, condition: str) -> pd.DataFrame:
    """Load original AI reviews and coerce the canonical schema."""
    df = pd.read_csv(path).copy()
    if 'condition' not in df.columns:
        df['condition'] = condition
    if 'review_uid' not in df.columns:
        df['review_uid'] = [
            f"{condition}::{row.get('target_proposal_uid', 'unknown')}::{row.get('evaluator_model', row.get('model', 'unknown'))}::{int(row.get('review_draw_index', i + 1)):03d}"
            for i, row in df.iterrows()
        ]
    if 'target_proposal_id' in df.columns:
        df['target_proposal_id'] = df['target_proposal_id'].astype(str)
    if 'evaluator_model' not in df.columns and 'model' in df.columns:
        df['evaluator_model'] = df['model']
    if 'review_source' not in df.columns:
        df['review_source'] = 'ai'
    if 'source_group' not in df.columns:
        df['source_group'] = df['evaluator_model'].map(lambda x: MODEL_DISPLAY_NAME_MAP.get(str(x), str(x)))
    if 'source_family' not in df.columns:
        df['source_family'] = df['source_group'].str.lower().replace({'gpt': 'gpt', 'gemini': 'gemini', 'claude': 'claude'})
    if 'overall_score' not in df.columns:
        df['overall_score'] = pd.to_numeric(df.get('overall_numeric_score'), errors='coerce')
    if 'original_review_text' not in df.columns:
        df['original_review_text'] = df.get('review_text', '')
    if 'review_family' not in df.columns:
        df['review_family'] = 'ncems_criteria'
    if 'review_source' not in df.columns:
        df['review_source'] = 'ai'
    if 'reviewer_id' not in df.columns:
        df['reviewer_id'] = pd.NA
    for col in ['reviewer_persona_card_id', 'reviewer_persona_team_id', 'reviewer_persona_team_authors', 'reviewer_persona_source_human_proposal_id', 'reviewer_persona_source_human_proposal_title']:
        if col not in df.columns:
            df[col] = pd.NA
    for source_col, target_col in AI_CRITERION_SCORE_MAP.items():
        df[target_col] = pd.to_numeric(df.get(source_col), errors='coerce')
    for source_col, target_col in AI_CRITERION_JUSTIFICATION_MAP.items():
        df[target_col] = df.get(source_col, '')
    return df


def load_ai_rephrased_reviews(path: Path, condition: str) -> pd.DataFrame:
    """Load rephrased AI reviews and coerce the canonical schema."""
    df = pd.read_csv(path).copy()
    if 'condition' not in df.columns:
        df['condition'] = condition
    if 'review_uid' not in df.columns:
        raise RuntimeError(f'Rephrased AI review file is missing review_uid: {path}')
    for col in ['rephrased_review', 'rephrased_strengths', 'rephrased_weakness', 'review_rephrased_at', 'review_rephrase_status']:
        if col not in df.columns:
            df[col] = pd.NA
    return df


def validate_review_alignment(original_df: pd.DataFrame, rephrased_df: pd.DataFrame, scope: str) -> List[str]:
    """Validate review alignment between original and rephrased data."""
    issues: List[str] = []
    if original_df['review_uid'].duplicated().any():
        issues.append(f'{scope}: duplicate review_uid values in original data')
    if rephrased_df['review_uid'].duplicated().any():
        issues.append(f'{scope}: duplicate review_uid values in rephrased data')
    if sorted(original_df['review_uid'].astype(str).tolist()) != sorted(rephrased_df['review_uid'].astype(str).tolist()):
        issues.append(f'{scope}: original and rephrased review_uid sets do not match')
    return issues


def harmonize_ncems_review_schema(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """Ensure every review table carries the canonical NCEMS schema."""
    out = df.copy()
    for col in CANONICAL_SCORE_COLUMNS + CANONICAL_JUSTIFICATION_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    if 'overall_score' not in out.columns:
        out['overall_score'] = pd.NA
    if source_type == 'human':
        out['review_source'] = 'human'
        out['source_group'] = 'Human'
        out['source_family'] = 'human'
    else:
        out['review_source'] = 'ai'
        if 'source_group' not in out.columns:
            out['source_group'] = out['evaluator_model'].map(lambda x: MODEL_DISPLAY_NAME_MAP.get(str(x), str(x)))
        if 'source_family' not in out.columns:
            out['source_family'] = out['source_group'].str.lower()
    return out


def build_review_master_table(
    *,
    condition: str,
    text_version: str,
    ai_original_df: pd.DataFrame,
    ai_rephrased_df: pd.DataFrame,
    human_original_df: pd.DataFrame,
    human_rephrased_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build the canonical review master table for one condition and branch."""
    ai_issues = validate_review_alignment(ai_original_df, ai_rephrased_df, f'ai::{condition}')
    human_issues = validate_review_alignment(human_original_df, human_rephrased_df, 'human')
    if ai_issues or human_issues:
        raise RuntimeError('Review alignment failed: ' + '; '.join(ai_issues + human_issues))

    ai_df = harmonize_ncems_review_schema(
        ai_original_df.merge(
            ai_rephrased_df[['review_uid', 'rephrased_review', 'rephrased_strengths', 'rephrased_weakness', 'review_rephrased_at', 'review_rephrase_status']],
            on='review_uid',
            how='left',
            validate='one_to_one',
        ),
        'ai',
    )
    human_df = harmonize_ncems_review_schema(
        human_original_df.merge(
            human_rephrased_df[['review_uid', 'rephrased_review', 'strengths', 'weakness', 'review_rephrased_at', 'review_rephrase_status']].rename(
                columns={'strengths': 'rephrased_strengths', 'weakness': 'rephrased_weakness'}
            ),
            on='review_uid',
            how='left',
            validate='one_to_one',
        ),
        'human',
    )

    ai_rows: List[Dict[str, Any]] = []
    for row in ai_df.to_dict('records'):
        active_text = row.get('rephrased_review', '') if text_version == 'rephrased' else row.get('original_review_text', row.get('review_text', ''))
        strengths_text = row.get('rephrased_strengths', '') if text_version == 'rephrased' else row.get('strengths', '')
        weakness_text = row.get('rephrased_weakness', '') if text_version == 'rephrased' else row.get('weakness', '')
        ai_rows.append(
            {
                **{col: row.get(col) for col in CANONICAL_SCORE_COLUMNS + CANONICAL_JUSTIFICATION_COLUMNS},
                'review_uid': row['review_uid'],
                'condition': condition,
                'text_version': text_version,
                'review_family': 'ncems_criteria',
                'review_source': 'ai',
                'source_group': row.get('source_group'),
                'source_family': row.get('source_family'),
                'evaluator_model': row.get('evaluator_model'),
                'reviewer_id': row.get('reviewer_id'),
                'review_draw_index': row.get('review_draw_index'),
                'target_proposal_uid': row.get('target_proposal_uid'),
                'target_cohort': row.get('target_cohort'),
                'target_proposal_id': row.get('target_proposal_id'),
                'target_proposal_title': row.get('target_proposal_title'),
                'target_proposal_status': row.get('target_proposal_status'),
                'target_authors': row.get('target_authors'),
                'target_ranking': row.get('target_ranking'),
                'target_funding': row.get('target_funding'),
                'target_human_n_reviews': row.get('target_human_n_reviews'),
                'review_text': active_text,
                'strengths_text': strengths_text,
                'weakness_text': weakness_text,
                'original_review_text': row.get('original_review_text', row.get('review_text', '')),
                'rephrased_review': row.get('rephrased_review'),
                'rephrased_strengths': row.get('rephrased_strengths'),
                'rephrased_weakness': row.get('rephrased_weakness'),
                'overall_score': row.get('overall_score'),
                'review_generated_at': row.get('review_generated_at'),
                'review_rephrased_at': row.get('review_rephrased_at'),
                'review_prompt_template': row.get('review_prompt_template'),
                'review_prompt_version': row.get('review_prompt_version'),
                'review_temperature': row.get('review_temperature'),
                'review_rephrase_status': row.get('review_rephrase_status'),
                'parse_success': row.get('parse_success'),
                'parse_error': row.get('parse_error'),
                'retry_count': row.get('retry_count'),
                'reviewer_persona_card_id': row.get('reviewer_persona_card_id'),
                'reviewer_persona_team_id': row.get('reviewer_persona_team_id'),
                'reviewer_persona_team_authors': row.get('reviewer_persona_team_authors'),
                'reviewer_persona_source_human_proposal_id': row.get('reviewer_persona_source_human_proposal_id'),
                'reviewer_persona_source_human_proposal_title': row.get('reviewer_persona_source_human_proposal_title'),
            }
        )

    human_rows: List[Dict[str, Any]] = []
    for row in human_df.to_dict('records'):
        active_text = row.get('rephrased_review', '') if text_version == 'rephrased' else row.get('original_review_text', row.get('review_text', ''))
        strengths_text = row.get('rephrased_strengths', '') if text_version == 'rephrased' else pd.NA
        weakness_text = row.get('rephrased_weakness', '') if text_version == 'rephrased' else pd.NA
        human_rows.append(
            {
                **{col: row.get(col) for col in CANONICAL_SCORE_COLUMNS + CANONICAL_JUSTIFICATION_COLUMNS},
                'review_uid': row['review_uid'],
                'condition': condition,
                'text_version': text_version,
                'review_family': 'ncems_criteria',
                'review_source': 'human',
                'source_group': 'Human',
                'source_family': 'human',
                'evaluator_model': row.get('evaluator_model'),
                'reviewer_id': row.get('reviewer_id'),
                'review_draw_index': pd.NA,
                'target_proposal_uid': row.get('target_proposal_uid'),
                'target_cohort': row.get('target_cohort'),
                'target_proposal_id': row.get('target_proposal_id'),
                'target_proposal_title': row.get('target_proposal_title'),
                'target_proposal_status': row.get('target_proposal_status'),
                'target_authors': row.get('target_authors'),
                'target_ranking': row.get('target_ranking'),
                'target_funding': row.get('target_funding'),
                'target_human_n_reviews': row.get('target_human_n_reviews'),
                'review_text': active_text,
                'strengths_text': strengths_text,
                'weakness_text': weakness_text,
                'original_review_text': row.get('original_review_text', row.get('_raw_review_text')),
                'rephrased_review': row.get('rephrased_review'),
                'rephrased_strengths': row.get('rephrased_strengths'),
                'rephrased_weakness': row.get('rephrased_weakness'),
                'overall_score': row.get('overall_score'),
                'review_generated_at': pd.NA,
                'review_rephrased_at': row.get('review_rephrased_at'),
                'review_prompt_template': pd.NA,
                'review_prompt_version': pd.NA,
                'review_temperature': pd.NA,
                'review_rephrase_status': row.get('review_rephrase_status'),
                'parse_success': True,
                'parse_error': '',
                'retry_count': 0,
                'reviewer_persona_card_id': pd.NA,
                'reviewer_persona_team_id': pd.NA,
                'reviewer_persona_team_authors': pd.NA,
                'reviewer_persona_source_human_proposal_id': pd.NA,
                'reviewer_persona_source_human_proposal_title': pd.NA,
            }
        )
    master_df = pd.DataFrame(human_rows + ai_rows)
    source_order = {'human': 0, 'ai': 1}
    master_df['_source_order'] = master_df['review_source'].map(source_order)
    master_df = master_df.sort_values(['target_proposal_uid', '_source_order', 'source_group', 'review_uid']).drop(columns=['_source_order']).reset_index(drop=True)
    return master_df


def build_review_panel_registry(review_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build one row per target proposal summarizing review-panel availability."""
    rows: List[Dict[str, Any]] = []
    for (condition, target_uid), group in review_master_df.groupby(['condition', 'target_proposal_uid'], sort=True):
        human = group[group['review_source'] == 'human']
        ai = group[group['review_source'] == 'ai']
        counts_by_family = ai.groupby('source_family').size().to_dict()
        target_meta = group.iloc[0]
        target_human_n_reviews = int(target_meta['target_human_n_reviews'])
        rows.append(
            {
                'condition': condition,
                'target_proposal_uid': target_uid,
                'target_cohort': target_meta['target_cohort'],
                'target_proposal_id': target_meta['target_proposal_id'],
                'target_proposal_title': target_meta['target_proposal_title'],
                'target_human_n_reviews': target_human_n_reviews,
                'n_human_reviews_available': int(len(human)),
                'n_ai_reviews_claude': int(counts_by_family.get('claude', 0)),
                'n_ai_reviews_gemini': int(counts_by_family.get('gemini', 0)),
                'n_ai_reviews_gpt': int(counts_by_family.get('gpt', 0)),
                'n_ai_reviews_pooled': int(len(ai)),
                'eligible_exact_match_claude': target_human_n_reviews <= int(counts_by_family.get('claude', 0)),
                'eligible_exact_match_gemini': target_human_n_reviews <= int(counts_by_family.get('gemini', 0)),
                'eligible_exact_match_gpt': target_human_n_reviews <= int(counts_by_family.get('gpt', 0)),
                'eligible_exact_match_pooled': target_human_n_reviews <= int(len(ai)),
                'human_review_uids': json.dumps(human['review_uid'].astype(str).tolist()),
                'ai_review_uids_claude': json.dumps(ai.loc[ai['source_family'] == 'claude', 'review_uid'].astype(str).tolist()),
                'ai_review_uids_gemini': json.dumps(ai.loc[ai['source_family'] == 'gemini', 'review_uid'].astype(str).tolist()),
                'ai_review_uids_gpt': json.dumps(ai.loc[ai['source_family'] == 'gpt', 'review_uid'].astype(str).tolist()),
                'ai_review_uids_pooled': json.dumps(ai['review_uid'].astype(str).tolist()),
            }
        )
    return pd.DataFrame(rows).sort_values(['condition', 'target_cohort', 'target_proposal_id']).reset_index(drop=True)


def build_review_sampling_frame(review_master_df: pd.DataFrame, panel_registry_df: pd.DataFrame) -> pd.DataFrame:
    """Build one row per review carrying exact-n panel-membership metadata."""
    counts_map = panel_registry_df.set_index(['condition', 'target_proposal_uid'])['target_human_n_reviews'].to_dict()
    out = review_master_df[['condition', 'review_uid', 'target_proposal_uid', 'review_source', 'source_family', 'evaluator_model', 'review_draw_index']].copy()
    out['text_versions_available'] = 'original,rephrased'
    out['target_human_n_reviews'] = out.apply(lambda row: counts_map[(row['condition'], row['target_proposal_uid'])], axis=1)
    out['is_human_panel_member'] = out['review_source'] == 'human'
    out['is_ai_pool_member'] = out['review_source'] == 'ai'
    out['is_ai_claude_member'] = out['source_family'] == 'claude'
    out['is_ai_gemini_member'] = out['source_family'] == 'gemini'
    out['is_ai_gpt_member'] = out['source_family'] == 'gpt'
    return out


def build_proposal_review_scores_summary(review_master_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate one proposal-level score summary table per condition."""
    original_df = review_master_df[review_master_df['text_version'] == 'original'].copy()
    rows: List[Dict[str, Any]] = []
    for (condition, target_uid), group in original_df.groupby(['condition', 'target_proposal_uid'], sort=True):
        human = group[group['review_source'] == 'human']
        ai = group[group['review_source'] == 'ai']
        meta = group.iloc[0]
        row: Dict[str, Any] = {
            'condition': condition,
            'target_proposal_uid': target_uid,
            'target_cohort': meta['target_cohort'],
            'target_proposal_id': meta['target_proposal_id'],
            'target_proposal_title': meta['target_proposal_title'],
            'target_proposal_status': meta['target_proposal_status'],
            'target_ranking': meta['target_ranking'],
            'target_funding': meta['target_funding'],
            'target_human_n_reviews': meta['target_human_n_reviews'],
            'human_n_reviews': int(len(human)),
            'human_mean_overall_score': pd.to_numeric(human['overall_score'], errors='coerce').mean(),
            'ai_pooled_n_reviews': int(len(ai)),
            'ai_pooled_mean_overall_score': pd.to_numeric(ai['overall_score'], errors='coerce').mean(),
        }
        for col in CANONICAL_SCORE_COLUMNS:
            row[f'human_mean_{col}'] = pd.to_numeric(human[col], errors='coerce').mean() if col in human.columns else np.nan
            row[f'ai_pooled_mean_{col}'] = pd.to_numeric(ai[col], errors='coerce').mean() if col in ai.columns else np.nan
        for family in ['claude', 'gemini', 'gpt']:
            sub = ai[ai['source_family'] == family]
            row[f'{family}_n_reviews'] = int(len(sub))
            row[f'{family}_mean_overall_score'] = pd.to_numeric(sub['overall_score'], errors='coerce').mean()
            for col in CANONICAL_SCORE_COLUMNS:
                row[f'{family}_mean_{col}'] = pd.to_numeric(sub[col], errors='coerce').mean() if col in sub.columns else np.nan
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(['condition', 'target_cohort', 'target_proposal_id']).reset_index(drop=True)


def build_review_embedding_bundle(
    df: pd.DataFrame,
    *,
    text_field: str,
    output_path: Path,
    model_name: str = PROPOSAL_EMBEDDING_MODEL,
    pooling: str = 'mean',
    reuse_if_exists: bool = True,
) -> Dict[str, Any]:
    """Build or load one aligned review embedding bundle."""
    review_uids = df['review_uid'].astype(str).tolist()
    texts = df[text_field].fillna('').astype(str).tolist()
    metadata = df[['review_uid', 'review_source', 'source_group', 'source_family', 'target_proposal_uid', 'condition', 'text_version']].to_dict('records')
    if reuse_if_exists and output_path.exists():
        payload = load_pickle(output_path)
        if payload.get('review_uids') == review_uids and payload.get('text_field') == text_field:
            return payload
    payload = {
        'embeddings': embed_texts(texts, model_name=model_name, pooling=pooling),
        'review_uids': review_uids,
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
    """Compute and save a square pairwise cosine-distance matrix."""
    embeddings = np.asarray(embedding_bundle['embeddings'], dtype=np.float32)
    pairwise = cosine_distances(embeddings)
    np.save(output_path, pairwise)
    return pairwise


def fit_or_load_review_umap(
    embedding_bundle: Dict[str, Any],
    *,
    reducer_path: Path,
    coords_path: Path,
    reuse_if_exists: bool = True,
) -> Tuple[Any, np.ndarray]:
    """Fit or load a review-space UMAP reducer and coordinates."""
    return fit_or_load_proposal_umap(
        embedding_bundle,
        reducer_path=reducer_path,
        coords_path=coords_path,
        reuse_if_exists=reuse_if_exists,
    )


def build_review_panel_distance_cache(review_master_df: pd.DataFrame, distance_matrix: np.ndarray, output_path: Path) -> Dict[str, Any]:
    """Build and save the per-proposal review-panel distance cache."""
    uid_to_idx = {uid: idx for idx, uid in enumerate(review_master_df['review_uid'].astype(str).tolist())}
    cache: Dict[str, Any] = {'review_uid_order': review_master_df['review_uid'].astype(str).tolist(), 'panels': {}}
    for target_uid, group in review_master_df.groupby('target_proposal_uid', sort=True):
        ordered_uids = group['review_uid'].astype(str).tolist()
        idx = [uid_to_idx[uid] for uid in ordered_uids]
        cache['panels'][str(target_uid)] = {
            'ordered_review_uids': ordered_uids,
            'human_review_uids': group.loc[group['review_source'] == 'human', 'review_uid'].astype(str).tolist(),
            'ai_pooled_review_uids': group.loc[group['review_source'] == 'ai', 'review_uid'].astype(str).tolist(),
            'ai_claude_review_uids': group.loc[group['source_family'] == 'claude', 'review_uid'].astype(str).tolist(),
            'ai_gemini_review_uids': group.loc[group['source_family'] == 'gemini', 'review_uid'].astype(str).tolist(),
            'ai_gpt_review_uids': group.loc[group['source_family'] == 'gpt', 'review_uid'].astype(str).tolist(),
            'distance_submatrix': distance_matrix[np.ix_(idx, idx)],
        }
    save_pickle(output_path, cache)
    return cache


def write_review_prepare_manifest(path: Path, payload: Dict[str, Any]) -> None:
    """Write the review-preparation manifest."""
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


__all__ = [
    'AI_REVIEW_EXPECTED_PER_MODEL',
    'AI_REVIEW_EXPECTED_POOLED',
    'AI_REVIEW_EXPECTED_ROWS',
    'CANONICAL_JUSTIFICATION_COLUMNS',
    'CANONICAL_SCORE_COLUMNS',
    'build_deterministic_human_review_uid',
    'build_human_target_proposal_lookup',
    'build_proposal_review_scores_summary',
    'build_review_embedding_bundle',
    'build_review_master_table',
    'build_review_panel_distance_cache',
    'build_review_panel_registry',
    'build_review_sampling_frame',
    'compute_pairwise_cosine_matrix',
    'find_project_root',
    'fit_or_load_review_umap',
    'load_ai_original_reviews',
    'load_ai_rephrased_reviews',
    'load_human_original_reviews',
    'load_human_rephrased_reviews',
    'locate_latest_ai_review_files',
    'validate_review_alignment',
    'write_review_prepare_manifest',
]
