"""
Helpers for the redesigned multi-condition review generation stage.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from proposal_generation import (
    append_failure_log,
    build_target_proposal_uid,
    ensure_failure_csv,
    extract_run_id_from_path,
    find_project_root,
    load_failures_csv,
    load_shared_call_context,
    now_run_id,
    save_generation_manifest,
)


MAX_FULL_TEXT_CHARS = 60_000

REVIEW_SCORE_FIELDS = [
    'relevance_to_emergent_phenomena_score',
    'relevance_to_emergent_phenomena_justification',
    'novelty_and_significance_score',
    'novelty_and_significance_justification',
    'rigor_of_approach_score',
    'rigor_of_approach_justification',
    'scope_and_timeline_score',
    'scope_and_timeline_justification',
    'synthesis_focus_score',
    'synthesis_focus_justification',
    'data_identification_score',
    'data_identification_justification',
    'open_science_commitment_score',
    'open_science_commitment_justification',
]


def _is_blank_value(value: Any) -> bool:
    """Return True when a scalar should count as missing text/content."""
    if value is None or pd.isna(value):
        return True
    return not str(value).strip()


def load_human_proposal_roster(project_root: Path) -> pd.DataFrame:
    """Load original human proposals and build the review target roster."""
    records: List[Dict[str, Any]] = []
    for cohort, filename in [('y1', 'human-proposals-y1.json'), ('y2', 'human-proposals-y2.json')]:
        path = project_root / 'data' / 'human-proposals' / filename
        payload = json.loads(path.read_text())
        for proposal in payload.get('proposals', []):
            proposal_id = proposal['proposal_id']
            abstract = str(proposal.get('abstract', '') or '').strip()
            full_draft = str(proposal.get('full_draft', '') or '').strip()
            full_text = '\n\n'.join(
                part for part in [
                    f"ABSTRACT:\n{abstract}" if abstract else '',
                    f"FULL PROPOSAL:\n{full_draft}" if full_draft else '',
                ] if part
            )
            records.append(
                {
                    'target_cohort': cohort,
                    'target_proposal_id': str(proposal_id),
                    'target_proposal_uid': build_target_proposal_uid(cohort, proposal_id),
                    'target_proposal_title': proposal.get('proposal_title', ''),
                    'target_proposal_status': proposal.get('proposal_status', ''),
                    'target_authors': '; '.join(proposal.get('authors', []) or []),
                    'target_source_file': str(path),
                    'target_abstract': abstract,
                    'target_full_text': full_text,
                }
            )
    df = pd.DataFrame(records).sort_values(['target_cohort', 'target_proposal_id']).reset_index(drop=True)
    if len(df) != 23:
        raise RuntimeError(f'Expected 23 human target proposals, found {len(df)}.')
    return df


def load_human_review_counts(project_root: Path) -> pd.DataFrame:
    """Load human review workbooks and compute observed reviews per proposal."""
    frames: List[pd.DataFrame] = []
    for filename in ['human_reviews_human-y1.xlsx', 'human_reviews_human-y2.xlsx']:
        path = project_root / 'data' / 'reviews' / 'human_reviews' / filename
        df = pd.read_excel(path)
        frames.append(df)
    reviews_df = pd.concat(frames, ignore_index=True)
    counts = (
        reviews_df.groupby(['year', 'id'], dropna=False)
        .size()
        .reset_index(name='target_human_n_reviews')
        .rename(columns={'year': 'target_cohort', 'id': 'target_proposal_id'})
    )
    counts['target_cohort'] = counts['target_cohort'].astype(str).str.lower()
    # proposal_id comes from JSON as a string but from Excel as int64; normalize
    # to str so the two frames merge on a matching key dtype.
    counts['target_proposal_id'] = counts['target_proposal_id'].astype(str)
    counts['target_proposal_uid'] = counts.apply(
        lambda row: build_target_proposal_uid(row['target_cohort'], row['target_proposal_id']),
        axis=1,
    )
    return counts[['target_cohort', 'target_proposal_id', 'target_proposal_uid', 'target_human_n_reviews']]


def load_reviewer_persona_roster(project_root: Path, target_roster: pd.DataFrame) -> pd.DataFrame:
    """Load persona cards and align them to target proposals."""
    payload = json.loads((project_root / 'data' / 'literature' / 'persona_cards.json').read_text())
    cards = payload.get('cards', [])
    records: List[Dict[str, Any]] = []
    title_to_uid = {
        row.target_proposal_title.strip().lower(): row.target_proposal_uid
        for row in target_roster.itertuples(index=False)
    }
    for card in cards:
        cohort = str(card.get('cohort', '')).strip().lower()
        proposal_id = str(card.get('human_proposal_id', '')).strip()
        proposal_uid = build_target_proposal_uid(cohort, proposal_id) if cohort and proposal_id else title_to_uid.get(str(card.get('human_proposal_title', '')).strip().lower())
        records.append(
            {
                'reviewer_persona_card_id': card.get('team_id'),
                'reviewer_persona_team_id': card.get('team_id'),
                'reviewer_persona_team_authors': '; '.join(card.get('team_members', []) or []),
                'reviewer_persona_source_human_proposal_id': card.get('human_proposal_id'),
                'reviewer_persona_source_human_proposal_title': card.get('human_proposal_title'),
                'reviewer_persona_source_human_proposal_uid': proposal_uid,
                'reviewer_persona_card_json': json.dumps(card, indent=2, ensure_ascii=False),
            }
        )
    df = pd.DataFrame(records).sort_values('reviewer_persona_card_id').reset_index(drop=True)
    if len(df) != len(target_roster):
        raise RuntimeError('Reviewer persona roster must contain one card per human target proposal.')
    return df


def build_review_condition_registry() -> Dict[str, Dict[str, Any]]:
    """Return explicit study review condition configs."""
    return {
        'baseline': {
            'condition': 'baseline',
            'review_prompt_template': 'eval_ncems_criteria_batch5',
            'review_generation_mode': 'batch5',
            'uses_reviewer_persona': False,
            'reviews_per_model_per_proposal': 5,
        },
        'one_at_a_time': {
            'condition': 'one_at_a_time',
            'review_prompt_template': 'eval_ncems_criteria_single',
            'review_generation_mode': 'independent_single',
            'uses_reviewer_persona': False,
            'reviews_per_model_per_proposal': 5,
        },
        'persona': {
            'condition': 'persona',
            'review_prompt_template': 'eval_ncems_criteria_persona_single',
            'review_generation_mode': 'independent_single',
            'uses_reviewer_persona': True,
            'reviews_per_model_per_proposal': 5,
        },
    }


def build_persona_review_schedule(
    target_roster: pd.DataFrame,
    reviewer_persona_roster: pd.DataFrame,
) -> Dict[str, List[Dict[str, Any]]]:
    """Build one fixed 5-persona schedule per target proposal."""
    persona_records = reviewer_persona_roster.to_dict('records')
    schedule: Dict[str, List[Dict[str, Any]]] = {}
    for target_idx, row in enumerate(target_roster.itertuples(index=False)):
        eligible = [
            rec for rec in persona_records
            if rec['reviewer_persona_source_human_proposal_uid'] != row.target_proposal_uid
        ]
        if len(eligible) < 5:
            raise RuntimeError(f'Not enough eligible reviewer personas for {row.target_proposal_uid}.')
        rotated = eligible[target_idx % len(eligible):] + eligible[:target_idx % len(eligible)]
        schedule[row.target_proposal_uid] = rotated[:5]
    return schedule


def build_review_schedule(
    *,
    target_roster: pd.DataFrame,
    condition_config: Dict[str, Any],
    models_to_use: List[str],
    reviewer_persona_schedule: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> pd.DataFrame:
    """Build the frozen review call schedule for one condition."""
    rows: List[Dict[str, Any]] = []
    for target in target_roster.to_dict('records'):
        for model_name in models_to_use:
            if condition_config['review_generation_mode'] == 'batch5':
                rows.append(
                    {
                        **target,
                        'condition': condition_config['condition'],
                        'evaluator_model': model_name,
                        'review_call_id': f"{condition_config['condition']}::{target['target_proposal_uid']}::{model_name}::review_call_001",
                        'review_generation_mode': 'batch5',
                        'expected_review_count': 5,
                        'review_draw_index': None,
                        'review_prompt_template': condition_config['review_prompt_template'],
                        'reviewer_persona_card_id': None,
                        'reviewer_persona_team_id': None,
                        'reviewer_persona_team_authors': None,
                        'reviewer_persona_source_human_proposal_id': None,
                        'reviewer_persona_source_human_proposal_title': None,
                        'reviewer_persona_card_json': None,
                    }
                )
            else:
                persona_panel = reviewer_persona_schedule.get(target['target_proposal_uid'], []) if reviewer_persona_schedule else []
                for draw_index in range(1, 6):
                    persona_payload = persona_panel[draw_index - 1] if condition_config['uses_reviewer_persona'] else {}
                    rows.append(
                        {
                            **target,
                            'condition': condition_config['condition'],
                            'evaluator_model': model_name,
                            'review_call_id': f"{condition_config['condition']}::{target['target_proposal_uid']}::{model_name}::review_call_{draw_index:03d}",
                            'review_generation_mode': 'independent_single',
                            'expected_review_count': 1,
                            'review_draw_index': draw_index,
                            'review_prompt_template': condition_config['review_prompt_template'],
                            'reviewer_persona_card_id': persona_payload.get('reviewer_persona_card_id'),
                            'reviewer_persona_team_id': persona_payload.get('reviewer_persona_team_id'),
                            'reviewer_persona_team_authors': persona_payload.get('reviewer_persona_team_authors'),
                            'reviewer_persona_source_human_proposal_id': persona_payload.get('reviewer_persona_source_human_proposal_id'),
                            'reviewer_persona_source_human_proposal_title': persona_payload.get('reviewer_persona_source_human_proposal_title'),
                            'reviewer_persona_card_json': persona_payload.get('reviewer_persona_card_json'),
                        }
                    )
    return pd.DataFrame(rows)


def truncate_target_full_text(full_text: str) -> Tuple[str, bool]:
    """Truncate proposal text to the configured model input bound."""
    if len(full_text) <= MAX_FULL_TEXT_CHARS:
        return full_text, False
    return full_text[:MAX_FULL_TEXT_CHARS] + '\n[... truncated for length ...]', True


def make_review_prompt(
    *,
    prompt_manager: Any,
    schedule_row: Dict[str, Any],
    shared_review_context: Dict[str, str],
) -> Tuple[str, bool]:
    """Format one review-generation prompt."""
    truncated_text, was_truncated = truncate_target_full_text(str(schedule_row['target_full_text']))
    payload = {
        'research_call': shared_review_context['research_call'],
        'proposal_id': schedule_row['target_proposal_id'],
        'proposal_title': schedule_row['target_proposal_title'],
        'proposal_abstract': schedule_row.get('target_abstract', ''),
        'proposal_full': truncated_text,
    }
    if schedule_row['review_prompt_template'] == 'eval_ncems_criteria_persona_single':
        payload['reviewer_persona_card_json'] = schedule_row['reviewer_persona_card_json']
    return prompt_manager.format_prompt(schedule_row['review_prompt_template'], payload), was_truncated


def extract_first_json_object(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Extract the first JSON object from a model response."""
    if not text or not str(text).strip():
        return None, 'empty response'
    s = str(text).strip()
    if s.startswith('{') and s.endswith('}'):
        try:
            return json.loads(s), None
        except json.JSONDecodeError:
            pass
    start = s.find('{')
    if start == -1:
        return None, 'no JSON object found'
    depth = 0
    end = -1
    for idx, char in enumerate(s[start:], start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = idx
                break
    if end == -1:
        return None, 'unclosed JSON object'
    try:
        return json.loads(s[start:end + 1]), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def parse_review_response(raw_text: str, expected_count: int) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Parse one model response into one or five review objects."""
    payload, parse_error = extract_first_json_object(raw_text)
    if payload is None:
        return [], parse_error
    reviews = payload.get('reviews')
    if isinstance(reviews, dict):
        reviews = [reviews]
    if not isinstance(reviews, list):
        return [], 'missing reviews list'
    if len(reviews) != expected_count:
        return [], f'expected {expected_count} review(s), parsed {len(reviews)}'
    return reviews, None


def flatten_review_response(
    *,
    schedule_row: Dict[str, Any],
    review_obj: Dict[str, Any],
    review_draw_index: int,
    run_id: str,
    prompt_version: str,
    provider_model_id: str,
    raw_response: str,
    generated_at: str,
    temperature: float,
    retry_count: int,
    target_text_truncated: bool,
) -> Dict[str, Any]:
    """Flatten one review object into the canonical output row."""
    row = {
        'review_uid': f"{schedule_row['condition']}::{schedule_row['target_proposal_uid']}::{schedule_row['evaluator_model']}::{review_draw_index:03d}",
        'run_id': run_id,
        'condition': schedule_row['condition'],
        'evaluator_model': schedule_row['evaluator_model'],
        'review_generation_mode': schedule_row['review_generation_mode'],
        'review_draw_index': review_draw_index,
        'review_call_id': schedule_row['review_call_id'],
        'review_prompt_template': schedule_row['review_prompt_template'],
        'review_prompt_version': prompt_version,
        'review_provider_model_id': provider_model_id,
        'review_temperature': temperature,
        'review_generated_at': generated_at,
        'parse_success': True,
        'parse_error': '',
        'raw_response': raw_response,
        'retry_count': retry_count,
        'target_proposal_uid': schedule_row['target_proposal_uid'],
        'target_cohort': schedule_row['target_cohort'],
        'target_proposal_id': schedule_row['target_proposal_id'],
        'target_proposal_title': schedule_row['target_proposal_title'],
        'target_proposal_status': schedule_row['target_proposal_status'],
        'target_authors': schedule_row['target_authors'],
        'target_human_n_reviews': schedule_row['target_human_n_reviews'],
        'target_source_file': schedule_row['target_source_file'],
        'target_text_truncated': target_text_truncated,
        'reviewer_persona_card_id': schedule_row.get('reviewer_persona_card_id'),
        'reviewer_persona_team_id': schedule_row.get('reviewer_persona_team_id'),
        'reviewer_persona_team_authors': schedule_row.get('reviewer_persona_team_authors'),
        'reviewer_persona_source_human_proposal_id': schedule_row.get('reviewer_persona_source_human_proposal_id'),
        'reviewer_persona_source_human_proposal_title': schedule_row.get('reviewer_persona_source_human_proposal_title'),
        'review_text': str(review_obj.get('review_text', '') or '').strip(),
        'strengths': str(review_obj.get('strengths', '') or '').strip(),
        'weakness': str(review_obj.get('weakness', '') or '').strip(),
        'overall_numeric_score': review_obj.get('overall_numeric_score'),
        'overall_summary': str(review_obj.get('overall_summary', '') or '').strip(),
    }
    for field in REVIEW_SCORE_FIELDS:
        row[field] = review_obj.get(field)
    return row


def validate_review_row(row: Dict[str, Any]) -> List[str]:
    """Validate the required output fields for a flattened review row."""
    issues: List[str] = []
    for field in [
        'review_uid',
        'target_proposal_uid',
        'review_text',
        'strengths',
        'weakness',
        'overall_summary',
    ]:
        if _is_blank_value(row.get(field, '')):
            issues.append(f'missing {field}')
    for field in REVIEW_SCORE_FIELDS:
        if _is_blank_value(row.get(field)):
            issues.append(f'missing {field}')
    return issues


def review_manifest_base(
    *,
    condition: str,
    run_id: str,
    models: List[str],
    prompt_template: str,
    prompt_version: str,
    temperature: float,
    target_n: int,
) -> Dict[str, Any]:
    """Create the shared manifest scaffold for one review condition."""
    return {
        'condition': condition,
        'run_id': run_id,
        'models_run': models,
        'review_prompt_template': prompt_template,
        'review_prompt_version': prompt_version,
        'temperature': temperature,
        'target_n': target_n,
        'started_at': datetime.now().isoformat(),
    }


def _review_call_is_complete(rows: pd.DataFrame, schedule_row: Dict[str, Any]) -> bool:
    """Return whether one review-generation call is already complete in a partial CSV."""
    subset = rows[rows['review_call_id'] == schedule_row['review_call_id']].copy()
    expected = int(schedule_row['expected_review_count'])
    if len(subset) != expected:
        return False
    required_cols = ['review_uid', 'review_text', 'strengths', 'weakness', 'overall_summary']
    for col in required_cols:
        if col not in subset.columns:
            return False
        if subset[col].fillna('').astype(str).str.strip().eq('').any():
            return False
    for field in REVIEW_SCORE_FIELDS:
        if field not in subset.columns:
            return False
        if subset[field].isna().any() or subset[field].astype(str).str.strip().eq('').any():
            return False
    if schedule_row['review_generation_mode'] == 'batch5':
        observed = sorted(pd.to_numeric(subset['review_draw_index'], errors='coerce').dropna().astype(int).tolist())
        return observed == list(range(1, expected + 1))
    return True


def _deduplicate_review_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one stable row per review_uid in resumed review outputs."""
    if df.empty or 'review_uid' not in df.columns:
        return df
    return df.drop_duplicates(subset=['review_uid'], keep='last').copy()


def run_review_generation_for_condition(
    *,
    project_root: Path,
    ai_interface: Any,
    prompt_manager: Any,
    shared_review_context: Dict[str, str],
    condition_config: Dict[str, Any],
    schedule_df: pd.DataFrame,
    generation_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_progress_every_n_calls: int,
    resume_ok: bool,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate reviews for one condition and save the canonical flat CSV."""
    condition = condition_config['condition']
    output_dir = project_root / 'data' / 'reviews' / 'ai_reviews' / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_complete = sorted(output_dir.glob(f'ai_reviews_{condition}_complete_*.csv'))
    latest_complete_path = latest_complete[-1] if latest_complete else None
    latest_progress_path = sorted(output_dir.glob(f'ai_reviews_{condition}_progress_*.csv'))
    latest_progress_path = latest_progress_path[-1] if latest_progress_path else None
    latest_schedule_path = sorted(output_dir.glob(f'review_schedule_{condition}_*.csv'))
    latest_schedule_path = latest_schedule_path[-1] if latest_schedule_path else None
    latest_failures_path = sorted(output_dir.glob(f'ai_reviews_{condition}_*_failures.csv'))
    latest_failures_path = latest_failures_path[-1] if latest_failures_path else None
    latest_manifest_path = sorted(output_dir.glob(f'generation_manifest_{condition}_*.json'))
    latest_manifest_path = latest_manifest_path[-1] if latest_manifest_path else None

    if resume_ok and latest_complete_path:
        existing_df = pd.read_csv(latest_complete_path)
        if len(existing_df) == 345:
            return {
                'condition': condition,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else latest_complete_path.stem.split('_')[-1],
                'reviews_df': existing_df,
                'complete_path': latest_complete_path,
                'progress_path': latest_progress_path,
                'schedule_path': latest_schedule_path,
                'failures_path': latest_failures_path,
                'manifest_path': latest_manifest_path,
                'qa_issues': [],
                'reused_existing': True,
            }

    existing_progress_df = pd.DataFrame()
    resumed_from_partial = False
    if resume_ok and latest_progress_path is not None:
        existing_progress_df = _deduplicate_review_rows(pd.read_csv(latest_progress_path))
        partial_run_id = (
            str(existing_progress_df['run_id'].iloc[0])
            if 'run_id' in existing_progress_df.columns and not existing_progress_df.empty
            else extract_run_id_from_path(latest_progress_path, f'ai_reviews_{condition}_progress_')
        )
        if partial_run_id:
            run_id = partial_run_id
            resumed_from_partial = not existing_progress_df.empty

    run_id = run_id or now_run_id()
    schedule_path = output_dir / f'review_schedule_{condition}_{run_id}.csv'
    progress_path = output_dir / f'ai_reviews_{condition}_progress_{run_id}.csv'
    complete_path = output_dir / f'ai_reviews_{condition}_complete_{run_id}.csv'
    failures_path = output_dir / f'ai_reviews_{condition}_{run_id}_failures.csv'
    manifest_path = output_dir / f'generation_manifest_{condition}_{run_id}.json'

    schedule_df.to_csv(schedule_path, index=False)
    prompt_template = prompt_manager.get_template(condition_config['review_prompt_template'])
    manifest = review_manifest_base(
        condition=condition,
        run_id=run_id,
        models=sorted(schedule_df['evaluator_model'].unique()),
        prompt_template=condition_config['review_prompt_template'],
        prompt_version=prompt_template.version,
        temperature=generation_temperature,
        target_n=schedule_df['target_proposal_uid'].nunique(),
    )

    rows: List[Dict[str, Any]] = existing_progress_df.to_dict('records') if not existing_progress_df.empty else []
    failures: List[Dict[str, Any]] = load_failures_csv(failures_path if failures_path.exists() else latest_failures_path)
    calls_completed = 0

    for schedule_row in schedule_df.to_dict('records'):
        current_df = _deduplicate_review_rows(pd.DataFrame(rows))
        if not current_df.empty and _review_call_is_complete(current_df, schedule_row):
            continue
        prompt, target_text_truncated = make_review_prompt(
            prompt_manager=prompt_manager,
            schedule_row=schedule_row,
            shared_review_context=shared_review_context,
        )
        result = ai_interface.generate_content_with_metadata(
            prompt,
            model_name=schedule_row['evaluator_model'],
            temperature=generation_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        calls_completed += 1

        if result['error']:
            append_failure_log(
                failures,
                condition=condition,
                stage='review_generation',
                model=schedule_row['evaluator_model'],
                call_id=schedule_row['review_call_id'],
                error=result['error'],
            )
        else:
            reviews, parse_error = parse_review_response(
                result['raw_response'],
                expected_count=int(schedule_row['expected_review_count']),
            )
            if parse_error:
                append_failure_log(
                    failures,
                    condition=condition,
                    stage='review_generation',
                    model=schedule_row['evaluator_model'],
                    call_id=schedule_row['review_call_id'],
                    error=parse_error,
                )
            else:
                for idx, review_obj in enumerate(reviews, start=1):
                    draw_index = idx if schedule_row['review_generation_mode'] == 'batch5' else int(schedule_row['review_draw_index'])
                    row = flatten_review_response(
                        schedule_row=schedule_row,
                        review_obj=review_obj,
                        review_draw_index=draw_index,
                        run_id=run_id,
                        prompt_version=prompt_template.version,
                        provider_model_id=result['provider_model_id'],
                        raw_response=result['raw_response'],
                        generated_at=result['timestamp'],
                        temperature=generation_temperature,
                        retry_count=max(result['attempt_count'] - 1, 0),
                        target_text_truncated=target_text_truncated,
                    )
                    issues = validate_review_row(row)
                    if issues:
                        append_failure_log(
                            failures,
                            condition=condition,
                            stage='review_generation',
                            model=schedule_row['evaluator_model'],
                            call_id=schedule_row['review_call_id'],
                            error='; '.join(issues),
                        )
                    else:
                        rows.append(row)

        if calls_completed % save_progress_every_n_calls == 0 and rows:
            partial_df = _deduplicate_review_rows(pd.DataFrame(rows))
            partial_df.sort_values(['target_proposal_uid', 'evaluator_model', 'review_draw_index']).to_csv(progress_path, index=False)
            ensure_failure_csv(failures_path, failures)

    reviews_df = _deduplicate_review_rows(pd.DataFrame(rows))
    if not reviews_df.empty:
        reviews_df = reviews_df.sort_values(['target_proposal_uid', 'evaluator_model', 'review_draw_index']).reset_index(drop=True)
        reviews_df.to_csv(progress_path, index=False)
        reviews_df.to_csv(complete_path, index=False)
    ensure_failure_csv(failures_path, failures)

    qa_issues = validate_review_outputs(reviews_df, condition)
    manifest.update(
        {
            'total_planned_api_calls': len(schedule_df),
            'total_completed_api_calls': calls_completed,
            'total_completed_review_rows': len(reviews_df),
            'failed_calls': len(failures),
            'qa_issues': qa_issues,
            'resumed_from_partial': resumed_from_partial,
            'completed_cleanly': not qa_issues and not failures,
            'ended_at': datetime.now().isoformat(),
        }
    )
    save_generation_manifest(manifest_path, manifest)

    return {
        'condition': condition,
        'run_id': run_id,
        'reviews_df': reviews_df,
        'complete_path': complete_path,
        'progress_path': progress_path,
        'schedule_path': schedule_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


def validate_review_outputs(reviews_df: pd.DataFrame, condition: str) -> List[str]:
    """Run the condition-level QA checks required by the redesign spec."""
    issues: List[str] = []
    if len(reviews_df) != 345:
        issues.append(f'{condition}: expected 345 completed review rows, found {len(reviews_df)}')
    if reviews_df.empty:
        return issues

    counts = reviews_df.groupby(['target_proposal_uid', 'evaluator_model']).size()
    for (target_uid, model_name), count in counts.items():
        if count != 5:
            issues.append(f'{condition}: {target_uid} x {model_name} has {count} review rows; expected 5')

    if condition == 'baseline':
        call_counts = reviews_df.groupby(['target_proposal_uid', 'evaluator_model'])['review_call_id'].nunique()
        for (target_uid, model_name), count in call_counts.items():
            if count != 1:
                issues.append(f'baseline: {target_uid} x {model_name} has {count} call ids; expected 1')

    if condition in {'one_at_a_time', 'persona'}:
        call_counts = reviews_df.groupby(['target_proposal_uid', 'evaluator_model'])['review_call_id'].nunique()
        for (target_uid, model_name), count in call_counts.items():
            if count != 5:
                issues.append(f'{condition}: {target_uid} x {model_name} has {count} call ids; expected 5')

    if condition == 'persona':
        if reviews_df['reviewer_persona_card_id'].isna().any():
            issues.append('persona: found missing reviewer_persona_card_id values')
    return issues


__all__ = [
    'build_persona_review_schedule',
    'build_review_condition_registry',
    'build_review_schedule',
    'find_project_root',
    'load_human_proposal_roster',
    'load_human_review_counts',
    'load_reviewer_persona_roster',
    'load_shared_call_context',
    'run_review_generation_for_condition',
]
