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
    _latest_non_failures_csv,
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
    rephrased = _latest_non_failures_csv(rephrased_dir, f'ai_reviews_{condition}_rephrased_*.csv')
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
                    'target_funding': is_accepted_or_funded(status),
                }
            )
    df = pd.DataFrame(rows).sort_values(['target_cohort', 'target_proposal_id']).reset_index(drop=True)
    return df


def is_accepted_or_funded(status: Any) -> Optional[bool]:
    if pd.isna(status):
        return None
    lowered = str(status).strip().lower()
    if lowered == '':
        return None
    return lowered in {'accepted', 'accept'} or any(token in lowered for token in ['fund', 'selected', 'awarded', 'award'])


def add_review_score_ranks(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Add AI/human reviewer-derived ranks for the human target proposals.

    Original target_ranking comes from the source human proposal JSON files
    where lower is better. These derived ranks use reviewer mean scores, where
    higher scores are treated as better.
    """
    if summary_df.empty:
        return summary_df
    out = summary_df.copy()
    score_sources = ['human', 'ai_pooled', 'claude', 'gemini', 'gpt']
    for source in score_sources:
        score_col = f'{source}_mean_overall_score'
        if score_col not in out.columns:
            continue
        values = pd.to_numeric(out[score_col], errors='coerce')
        out[f'{source}_review_score_rank'] = (
            values.groupby(out['condition']).rank(method='min', ascending=False, na_option='bottom')
        )
        out[f'{source}_review_score_rank_within_cohort'] = (
            values.groupby([out['condition'], out['target_cohort']]).rank(method='min', ascending=False, na_option='bottom')
        )
    return out


def _top_n_flag(values: pd.Series, *, n: int = 5) -> pd.Series:
    """Return a strict top-n boolean flag with deterministic tie-breaking."""
    proposal_uids = values.index.astype(str)
    score_df = pd.DataFrame({
        'proposal_uid': proposal_uids.to_numpy(),
        'score': pd.to_numeric(values, errors='coerce').to_numpy(),
    })
    score_df = score_df.dropna(subset=['score']).sort_values(
        ['score', 'proposal_uid'],
        ascending=[False, True],
        kind='mergesort',
    )
    selected = set(score_df.head(n)['proposal_uid'])
    return pd.Series(proposal_uids.isin(selected), index=values.index)


def build_ai_review_score_annotations(
    proposal_scores_by_condition: Dict[str, pd.DataFrame],
    *,
    top_n: int = 5,
) -> pd.DataFrame:
    """Build proposal-level AI review score annotations across review conditions."""
    annotation: pd.DataFrame | None = None
    weighted_score_cols = []
    weighted_count_cols = []

    for condition, scores_df in proposal_scores_by_condition.items():
        if scores_df is None or scores_df.empty:
            continue
        required = {'target_proposal_uid', 'ai_pooled_mean_overall_score'}
        missing = required.difference(scores_df.columns)
        if missing:
            raise ValueError(f'{condition}: missing proposal score columns: {sorted(missing)}')

        score_col = f'average_score_AI_{condition}'
        count_col = f'_n_AI_reviews_{condition}'
        cond = scores_df[['target_proposal_uid', 'ai_pooled_mean_overall_score']].copy()
        cond = cond.rename(columns={'target_proposal_uid': 'proposal_uid', 'ai_pooled_mean_overall_score': score_col})
        cond[score_col] = pd.to_numeric(cond[score_col], errors='coerce')
        if 'ai_pooled_n_reviews' in scores_df.columns:
            cond[count_col] = pd.to_numeric(scores_df['ai_pooled_n_reviews'], errors='coerce').fillna(0).to_numpy()
        else:
            cond[count_col] = 1

        cond[f'is_top5_AI-ranked_{condition}'] = _top_n_flag(cond.set_index('proposal_uid')[score_col], n=top_n).to_numpy()
        cond[f'average_score_AI_rank_{condition}'] = cond[score_col].rank(method='first', ascending=False, na_option='bottom')
        cond[f'_weighted_score_AI_{condition}'] = cond[score_col] * cond[count_col]
        weighted_score_cols.append(f'_weighted_score_AI_{condition}')
        weighted_count_cols.append(count_col)

        if annotation is None:
            annotation = cond
        else:
            annotation = annotation.merge(cond, on='proposal_uid', how='outer', validate='one_to_one')

    if annotation is None:
        return pd.DataFrame()

    weighted_scores = annotation[weighted_score_cols].sum(axis=1, min_count=1)
    weighted_counts = annotation[weighted_count_cols].sum(axis=1, min_count=1).replace(0, np.nan)
    annotation['average_score_AI'] = weighted_scores / weighted_counts
    annotation['is_top5_AI-ranked'] = _top_n_flag(annotation.set_index('proposal_uid')['average_score_AI'], n=top_n).to_numpy()
    annotation['average_score_AI_rank'] = annotation['average_score_AI'].rank(method='first', ascending=False, na_option='bottom')

    drop_cols = [c for c in annotation.columns if c.startswith('_weighted_score_AI_') or c.startswith('_n_AI_reviews_')]
    return annotation.drop(columns=drop_cols).sort_values('proposal_uid').reset_index(drop=True)


def annotate_prepared_proposal_masters_with_ai_scores(
    project_root: Path,
    proposal_scores_by_condition: Dict[str, pd.DataFrame],
    *,
    proposal_conditions: List[str],
    text_versions: List[str],
    top_n: int = 5,
    write_json_companions: bool = True,
) -> pd.DataFrame:
    """Append AI review-score annotations to prepared proposal_master files."""
    annotations = build_ai_review_score_annotations(proposal_scores_by_condition, top_n=top_n)
    if annotations.empty:
        return pd.DataFrame()

    written_rows: List[Dict[str, Any]] = []
    annotation_cols = [c for c in annotations.columns if c != 'proposal_uid']
    flag_cols = [c for c in annotation_cols if c.startswith('is_top5_AI-ranked')]

    score_annotations = annotations.rename(columns={'proposal_uid': 'target_proposal_uid'})
    for condition in proposal_conditions:
        score_summary_path = project_root / 'data' / 'prepared' / condition / 'reviews' / 'proposal_review_scores_summary.csv'
        if not score_summary_path.exists():
            continue
        score_summary = pd.read_csv(score_summary_path)
        if 'target_proposal_uid' not in score_summary.columns:
            continue
        score_summary = score_summary.drop(columns=[c for c in annotation_cols if c in score_summary.columns], errors='ignore')
        score_summary = score_summary.merge(score_annotations, on='target_proposal_uid', how='left', validate='one_to_one')
        for col in flag_cols:
            if col in score_summary.columns:
                score_summary[col] = score_summary[col].fillna(False).astype(bool)
        score_summary.to_csv(score_summary_path, index=False)
        written_rows.append({
            'condition': condition,
            'text_version': 'reviews',
            'proposal_master_path': str(score_summary_path),
            'json_path': '',
            'rows': int(len(score_summary)),
            'human_rows': int(len(score_summary)),
            'top_ai_ranked_rows': int(score_summary['is_top5_AI-ranked'].sum()) if 'is_top5_AI-ranked' in score_summary.columns else np.nan,
        })

    for condition in proposal_conditions:
        for text_version in text_versions:
            master_path = project_root / 'data' / 'prepared' / condition / 'proposals' / text_version / 'proposal_master.csv'
            if not master_path.exists():
                continue
            master = pd.read_csv(master_path)
            master = master.drop(columns=[c for c in annotation_cols if c in master.columns], errors='ignore')
            master = master.merge(annotations, on='proposal_uid', how='left', validate='many_to_one')
            if 'source_type' in master.columns:
                non_human = master['source_type'] != 'human'
                for col in annotation_cols:
                    if col in flag_cols:
                        master.loc[non_human, col] = False
                    else:
                        master.loc[non_human, col] = np.nan
            for col in flag_cols:
                master[col] = master[col].fillna(False).astype(bool)
            master.to_csv(master_path, index=False)

            json_path = master_path.with_suffix('.json')
            if write_json_companions:
                json_path.write_text(json.dumps(master.to_dict('records'), indent=2, ensure_ascii=False, default=str))

            top_ai_ranked_rows = (
                int(master.loc[master['source_type'] == 'human', 'is_top5_AI-ranked'].sum())
                if 'is_top5_AI-ranked' in master.columns and 'source_type' in master.columns
                else np.nan
            )
            written_rows.append({
                'condition': condition,
                'text_version': text_version,
                'proposal_master_path': str(master_path),
                'json_path': str(json_path) if write_json_companions else '',
                'rows': int(len(master)),
                'human_rows': int((master['source_type'] == 'human').sum()) if 'source_type' in master.columns else np.nan,
                'top_ai_ranked_rows': top_ai_ranked_rows,
            })

    return pd.DataFrame(written_rows)


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
        latest = _latest_non_failures_csv(base_dir, f'human_reviews_{cohort_label}_rephrased_*.csv')
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
    if 'target_proposal_id' in df.columns:
        # Match load_ai_original_reviews / the proposal lookup (str) so the
        # downstream merge on target_proposal_id doesn't hit an int64-vs-object
        # dtype mismatch.
        df['target_proposal_id'] = df['target_proposal_id'].astype(str)
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
            human_rephrased_df[['review_uid', 'rephrased_review', 'rephrased_strengths', 'rephrased_weakness', 'review_rephrased_at', 'review_rephrase_status']],
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
    out = pd.DataFrame(rows).sort_values(['condition', 'target_cohort', 'target_proposal_id']).reset_index(drop=True)
    return add_review_score_ranks(out)


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
    # default=str keeps the writer robust to Path (and other non-JSON) values so
    # a stray unstringified path in the manifest doesn't blow up the whole run.
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


__all__ = [
    'AI_REVIEW_EXPECTED_PER_MODEL',
    'AI_REVIEW_EXPECTED_POOLED',
    'AI_REVIEW_EXPECTED_ROWS',
    'CANONICAL_JUSTIFICATION_COLUMNS',
    'CANONICAL_SCORE_COLUMNS',
    'add_review_score_ranks',
    'annotate_prepared_proposal_masters_with_ai_scores',
    'build_ai_review_score_annotations',
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
