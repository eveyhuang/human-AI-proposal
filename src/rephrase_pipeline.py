"""
Helpers for the redesigned proposal/review rephrasing stage.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from proposal_generation import (
    build_target_proposal_uid,
    ensure_failure_csv,
    find_project_root,
    latest_matching_file,
    now_run_id,
    save_generation_manifest,
)
from rephrase_reviews import (
    ONE_STEP_REVIEW_SYSTEM,
    build_ai_review_text,
    build_human_review_text_sheet1,
    extract_first_json_object,
)


PROPOSAL_REPHRASE_PROMPT_VERSION = 'proposal_semantic_standardization_v1'
REVIEW_REPHRASE_PROMPT_VERSION = 'review_neutralization_v1'
SECTION_HEADERS = [
    'SCIENTIFIC BACKGROUND AND RESEARCH QUESTION',
    'METHODOLOGY AND ANALYTICAL APPROACH',
    'DATA SOURCES AND SYNTHESIS PLAN',
    'FEASIBILITY AND TIMELINE',
    'OPEN SCIENCE AND TEAM COMPOSITION',
]

SUMMARIZE_SYSTEM = """You are a scientific content extractor. Read the research proposal and extract its core semantic content as a compact, neutral summary.

Your ONLY goal is to capture what the proposal says while stripping style, rhetoric, and phrasing.

Extract facts for each of the following categories. Write each as a plain declarative statement in neutral words. If a category is not addressed, write "Not specified."

1. Research domain and specific phenomenon being studied
2. Scientific gap or open question
3. Current state of knowledge and what remains incomplete
4. Primary research question or objective
5. Why the research question is significant or novel
6. Overall study design and analytical strategy
7. Key methods, models, tools, or algorithms
8. How results will be validated or benchmarked
9. Datasets or databases to be used
10. How the datasets will be integrated or synthesized
11. Known data limitations and how they will be addressed
12. Project milestones and timeline
13. Why multi-lab or cross-disciplinary collaboration is needed
14. Open science plans
15. Team composition

Output ONLY the numbered fact statements."""

FILL_SYSTEM = """You are a scientific writer. You will be given a numbered list of semantic facts extracted from a research proposal. Use ONLY these facts to write the standardized template below.

SCIENTIFIC BACKGROUND AND RESEARCH QUESTION
Write exactly 3 sentences.

METHODOLOGY AND ANALYTICAL APPROACH
Write exactly 3 sentences.

DATA SOURCES AND SYNTHESIS PLAN
Write exactly 3 sentences.

FEASIBILITY AND TIMELINE
Write exactly 2 sentences.

OPEN SCIENCE AND TEAM COMPOSITION
Write exactly 2 sentences.

Rules:
- Third-person neutral register only.
- Declarative statements only.
- Preserve scientific meaning.
- If a fact is "Not specified", say the proposal does not specify that information.
- Output ONLY the filled template with the five section headings and their sentences."""

ABSTRACT_SYSTEM = """You will be given extracted scientific facts from a research proposal. Write exactly 5 sentences as a neutral structured abstract in biomedical article style.

Sentence 1: background and domain.
Sentence 2: the scientific gap.
Sentence 3: objective and approach.
Sentence 4: data and integration strategy.
Sentence 5: expected contribution and significance.

Rules:
- Use only the provided facts.
- Third-person neutral register.
- No team, timeline, budget, or open-science details.
- Output only the 5-sentence paragraph."""


def strip_section_headers(text: str) -> str:
    """Remove the standardized section headers from generated proposal text."""
    import re

    cleaned = str(text or '')
    for header in SECTION_HEADERS:
        cleaned = re.sub(rf'^\s*{re.escape(header)}\s*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    return re.sub(r'\n{3,}', '\n\n', cleaned).strip()


def build_ai_full_text(row: pd.Series) -> str:
    """Concatenate AI proposal sections into a single extraction source text."""
    parts: List[str] = []
    field_labels = [
        ('abstract', 'Abstract'),
        ('background_and_significance', 'Background and Significance'),
        ('research_questions_and_hypotheses', 'Research Questions and Hypotheses'),
        ('methods_and_approach', 'Methods and Approach'),
        ('expected_outcomes_and_impact', 'Expected Outcomes and Impact'),
        ('open_science_and_reproducibility', 'Open Science and Reproducibility'),
        ('budget_and_resources', 'Budget and Resources'),
    ]
    for field, label in field_labels:
        text = str(row.get(field, '') or '').strip()
        if text and text.lower() not in {'nan', 'none'}:
            parts.append(f'[{label}]\n{text}')
    return '\n\n'.join(parts)


def build_human_full_text(proposal: Dict[str, Any]) -> str:
    """Concatenate human proposal fields into a single extraction source text."""
    parts: List[str] = []
    abstract = str(proposal.get('abstract', '') or '').strip()
    full_draft = str(proposal.get('full_draft', '') or '').strip()
    if abstract and abstract.lower() not in {'nan', 'none'}:
        parts.append(f'[Abstract]\n{abstract}')
    if full_draft and full_draft.lower() not in {'nan', 'none'}:
        parts.append(f'[Full Proposal]\n{full_draft}')
    return '\n\n'.join(parts)


def locate_latest_ai_proposal_files(
    project_root: Path, conditions: List[str], require_all: bool = True
) -> Dict[str, Path]:
    """Locate the latest complete AI proposal file for each condition.

    With require_all=True (default) a missing complete file raises. With
    require_all=False, conditions without a complete file are skipped, so a
    stage can proceed on whatever is ready (e.g. rephrasing finished conditions
    while others are still generating).
    """
    files: Dict[str, Path] = {}
    for condition in conditions:
        directory = project_root / 'data' / 'ai-proposals' / condition
        path = latest_matching_file(directory, f'ai_proposals_{condition}_complete_*.csv')
        if path is None:
            if require_all:
                raise FileNotFoundError(f'No complete AI proposal CSV found for condition {condition} in {directory}')
            continue
        files[condition] = path
    return files


def locate_latest_ai_review_files(
    project_root: Path, conditions: List[str], require_all: bool = True
) -> Dict[str, Path]:
    """Locate the latest complete AI review file for each condition.

    See locate_latest_ai_proposal_files for the require_all semantics.
    """
    files: Dict[str, Path] = {}
    for condition in conditions:
        directory = project_root / 'data' / 'reviews' / 'ai_reviews' / condition
        path = latest_matching_file(directory, f'ai_reviews_{condition}_complete_*.csv')
        if path is None:
            if require_all:
                raise FileNotFoundError(f'No complete AI review CSV found for condition {condition} in {directory}')
            continue
        files[condition] = path
    return files


def load_human_proposal_sources(project_root: Path) -> Dict[str, Path]:
    """Return the shared human proposal source files keyed by cohort."""
    sources = {
        'y1': project_root / 'data' / 'human-proposals' / 'human-proposals-y1.json',
        'y2': project_root / 'data' / 'human-proposals' / 'human-proposals-y2.json',
    }
    for cohort, path in sources.items():
        if not path.exists():
            raise FileNotFoundError(f'Missing human proposal source for {cohort}: {path}')
    return sources


def load_human_review_sources(project_root: Path) -> Dict[str, Path]:
    """Return the shared human review workbooks keyed by cohort label."""
    sources = {
        'human-y1': project_root / 'data' / 'reviews' / 'human_reviews' / 'human_reviews_human-y1.xlsx',
        'human-y2': project_root / 'data' / 'reviews' / 'human_reviews' / 'human_reviews_human-y2.xlsx',
    }
    for cohort, path in sources.items():
        if not path.exists():
            raise FileNotFoundError(f'Missing human review source for {cohort}: {path}')
    return sources


def build_rephrase_job_registry(
    *,
    ai_proposal_sources: Dict[str, Path],
    ai_review_sources: Dict[str, Path],
    human_proposal_sources: Dict[str, Path],
    human_review_sources: Dict[str, Path],
    rephrase_model: str,
    rephrase_temperature: float,
    run_id: str,
) -> Dict[str, Any]:
    """Build one explicit job registry for the full notebook run."""
    ai_proposal_jobs = []
    for condition, source_path in ai_proposal_sources.items():
        ai_proposal_jobs.append(
            {
                'artifact_family': 'ai_proposals',
                'condition': condition,
                'source_path': source_path,
                'output_dir': source_path.parent / 'rephrased',
            }
        )

    ai_review_jobs = []
    for condition, source_path in ai_review_sources.items():
        ai_review_jobs.append(
            {
                'artifact_family': 'ai_reviews',
                'condition': condition,
                'source_path': source_path,
                'output_dir': source_path.parent / 'rephrased',
            }
        )

    human_proposal_jobs = []
    for cohort, source_path in human_proposal_sources.items():
        human_proposal_jobs.append(
            {
                'artifact_family': 'human_proposals',
                'cohort': cohort,
                'source_path': source_path,
                'output_dir': source_path.parent / 'rephrased',
            }
        )

    human_review_jobs = []
    for cohort, source_path in human_review_sources.items():
        human_review_jobs.append(
            {
                'artifact_family': 'human_reviews',
                'cohort': cohort,
                'source_path': source_path,
                'output_dir': source_path.parent / 'rephrased',
            }
        )

    return {
        'run_id': run_id,
        'rephrase_model': rephrase_model,
        'rephrase_temperature': rephrase_temperature,
        'proposal_prompt_version': PROPOSAL_REPHRASE_PROMPT_VERSION,
        'review_prompt_version': REVIEW_REPHRASE_PROMPT_VERSION,
        'ai_proposal_rephrase_jobs': ai_proposal_jobs,
        'ai_review_rephrase_jobs': ai_review_jobs,
        'human_proposal_rephrase_jobs': human_proposal_jobs,
        'human_review_rephrase_jobs': human_review_jobs,
    }


def append_rephrase_failure_log(failures: List[Dict[str, Any]], **record: Any) -> None:
    """Append one failure record in a stable format."""
    failures.append({'failed_at': datetime.now().isoformat(), **record})


def _call_model(
    *,
    ai_interface: Any,
    prompt: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
    retry_delays: List[int],
) -> Dict[str, Any]:
    return ai_interface.generate_content_with_metadata(
        prompt,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_delays=retry_delays,
    )


def _proposal_prompts(full_text: str) -> Dict[str, str]:
    return {
        'summary': f"{SUMMARIZE_SYSTEM}\n\n---\nPROPOSAL TEXT:\n{full_text.strip()}\n---\nEXTRACTED FACTS:",
        'fill': None,
        'abstract': None,
    }


def _review_prompt(review_text: str) -> str:
    return f"{ONE_STEP_REVIEW_SYSTEM}\n\n---\nREVIEW TEXT:\n{review_text.strip()}\n---\nJSON:"


def _coerce_ai_proposal_schema(df: pd.DataFrame, condition: str) -> pd.DataFrame:
    out = df.copy()
    if 'condition' not in out.columns:
        out['condition'] = condition
    if 'proposal_uid' not in out.columns:
        generated_uids: List[str] = []
        for model_name, group in out.groupby(out.get('model', pd.Series(['unknown'] * len(out))), sort=False):
            for idx, original_index in enumerate(group.index, start=1):
                generated_uids.append((original_index, f'{condition}::{model_name}::{idx:02d}'))
        if generated_uids:
            uid_series = pd.Series({idx: uid for idx, uid in generated_uids})
            out['proposal_uid'] = out.index.to_series().map(uid_series)
    if 'model' not in out.columns and 'author' in out.columns:
        out['model'] = out['author']
    if 'author' not in out.columns and 'model' in out.columns:
        out['author'] = out['model']
    return out


def _coerce_ai_review_schema(df: pd.DataFrame, condition: str) -> pd.DataFrame:
    out = df.copy()
    if 'condition' not in out.columns:
        out['condition'] = condition
    if 'review_uid' not in out.columns:
        ids: List[Tuple[Any, str]] = []
        for idx, row in out.iterrows():
            evaluator_model = str(row.get('evaluator_model') or row.get('model') or 'unknown')
            target_uid = str(row.get('target_proposal_uid') or f"unknown_target_{idx}")
            draw_index = int(row.get('review_draw_index') or idx + 1)
            ids.append((idx, f'{condition}::{evaluator_model}::{target_uid}::{draw_index:02d}'))
        out['review_uid'] = out.index.to_series().map(pd.Series(dict(ids)))
    return out


def _rephrase_proposal_text(
    *,
    ai_interface: Any,
    full_text: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
    retry_delays: List[int],
) -> Dict[str, Any]:
    """Run summarize -> fill -> abstract on one proposal text."""
    result = {
        'standardized_text': '',
        'rephrased_abstract': '',
        'proposal_rephrased_at': '',
        'proposal_rephrase_retry_count': 0,
        'proposal_rephrase_status': 'failed',
        'proposal_rephrase_error': '',
    }
    prompts = _proposal_prompts(full_text)
    summary_call = _call_model(
        ai_interface=ai_interface,
        prompt=prompts['summary'],
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_delays=retry_delays,
    )
    result['proposal_rephrase_retry_count'] += max(summary_call['attempt_count'] - 1, 0)
    if summary_call['error']:
        result['proposal_rephrase_error'] = f"summary: {summary_call['error']}"
        result['proposal_rephrased_at'] = summary_call['timestamp']
        return result

    summary_text = str(summary_call['raw_response'] or '').strip()
    fill_prompt = f"{FILL_SYSTEM}\n\n---\nEXTRACTED FACTS:\n{summary_text}\n---\nFILLED TEMPLATE:"
    fill_call = _call_model(
        ai_interface=ai_interface,
        prompt=fill_prompt,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_delays=retry_delays,
    )
    result['proposal_rephrase_retry_count'] += max(fill_call['attempt_count'] - 1, 0)
    if fill_call['error']:
        result['proposal_rephrase_error'] = f"fill: {fill_call['error']}"
        result['proposal_rephrased_at'] = fill_call['timestamp']
        return result

    abstract_prompt = f"{ABSTRACT_SYSTEM}\n\n---\nEXTRACTED FACTS:\n{summary_text}\n---\nABSTRACT:"
    abstract_call = _call_model(
        ai_interface=ai_interface,
        prompt=abstract_prompt,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_delays=retry_delays,
    )
    result['proposal_rephrase_retry_count'] += max(abstract_call['attempt_count'] - 1, 0)
    result['proposal_rephrased_at'] = abstract_call['timestamp']
    if abstract_call['error']:
        result['proposal_rephrase_error'] = f"abstract: {abstract_call['error']}"
        return result

    standardized_text = strip_section_headers(str(fill_call['raw_response'] or '').strip())
    rephrased_abstract = str(abstract_call['raw_response'] or '').strip()
    result['standardized_text'] = standardized_text
    result['rephrased_abstract'] = rephrased_abstract
    if standardized_text and rephrased_abstract:
        result['proposal_rephrase_status'] = 'success'
    else:
        result['proposal_rephrase_error'] = 'missing standardized_text or rephrased_abstract'
    return result


def _extract_review_source_text(row: Dict[str, Any]) -> str:
    review_text = str(row.get('review_text', '') or '').strip()
    strengths = str(row.get('strengths', '') or '').strip()
    weakness = str(row.get('weakness', '') or '').strip()
    if review_text and strengths and weakness:
        return (
            f"[Overall Review]\n{review_text}\n\n"
            f"[Strengths]\n{strengths}\n\n"
            f"[Weakness]\n{weakness}"
        )
    if review_text:
        return review_text
    return build_ai_review_text(row)


def _rephrase_review_text(
    *,
    ai_interface: Any,
    review_text: str,
    model_name: str,
    temperature: float,
    max_tokens: int,
    retry_delays: List[int],
) -> Dict[str, Any]:
    result = {
        'rephrased_review': '',
        'rephrased_strengths': '',
        'rephrased_weakness': '',
        'review_rephrased_at': '',
        'review_rephrase_retry_count': 0,
        'review_rephrase_status': 'failed',
        'review_rephrase_error': '',
    }
    call = _call_model(
        ai_interface=ai_interface,
        prompt=_review_prompt(review_text),
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        retry_delays=retry_delays,
    )
    result['review_rephrase_retry_count'] = max(call['attempt_count'] - 1, 0)
    result['review_rephrased_at'] = call['timestamp']
    if call['error']:
        result['review_rephrase_error'] = call['error']
        return result

    payload, parse_error = extract_first_json_object(str(call['raw_response'] or ''))
    if parse_error or not isinstance(payload, dict):
        result['review_rephrase_error'] = parse_error or 'invalid JSON response'
        return result

    result['rephrased_review'] = str(payload.get('rephrased_review', '') or '').strip()
    result['rephrased_strengths'] = str(payload.get('strengths', '') or '').strip()
    result['rephrased_weakness'] = str(payload.get('weakness', '') or '').strip()
    if result['rephrased_review'] and result['rephrased_strengths'] and result['rephrased_weakness']:
        result['review_rephrase_status'] = 'success'
    else:
        result['review_rephrase_error'] = 'missing one or more rephrased review fields'
    return result


def _proposal_rephrase_manifest(
    *,
    source_path: Path,
    output_path: Path,
    condition_or_cohort: str,
    run_id: str,
    rephrase_model: str,
    rephrase_temperature: float,
    row_count: int,
    success_count: int,
    failure_count: int,
    prompt_version: str,
) -> Dict[str, Any]:
    return {
        'run_id': run_id,
        'scope': condition_or_cohort,
        'source_file': str(source_path),
        'output_file': str(output_path),
        'row_count': row_count,
        'success_count': success_count,
        'failure_count': failure_count,
        'rephrase_model': rephrase_model,
        'temperature': rephrase_temperature,
        'prompt_version': prompt_version,
        'started_at': datetime.now().isoformat(),
    }


def _review_rephrase_manifest(
    *,
    source_path: Path,
    output_path: Path,
    condition_or_cohort: str,
    run_id: str,
    rephrase_model: str,
    rephrase_temperature: float,
    row_count: int,
    success_count: int,
    failure_count: int,
    prompt_version: str,
) -> Dict[str, Any]:
    return {
        'run_id': run_id,
        'scope': condition_or_cohort,
        'source_file': str(source_path),
        'output_file': str(output_path),
        'row_count': row_count,
        'success_count': success_count,
        'failure_count': failure_count,
        'rephrase_model': rephrase_model,
        'temperature': rephrase_temperature,
        'prompt_version': prompt_version,
        'started_at': datetime.now().isoformat(),
    }


def _proposal_rephrase_complete(df: pd.DataFrame, source_df: pd.DataFrame) -> bool:
    if len(df) != len(source_df):
        return False
    required = ['proposal_uid', 'standardized_text', 'rephrased_abstract', 'proposal_rephrase_status']
    if any(col not in df.columns for col in required):
        return False
    if df['proposal_uid'].fillna('').astype(str).str.strip().eq('').any():
        return False
    return df['proposal_rephrase_status'].fillna('').astype(str).eq('success').all()


def _review_rephrase_complete(df: pd.DataFrame, source_df: pd.DataFrame) -> bool:
    if len(df) != len(source_df):
        return False
    required = ['review_uid', 'rephrased_review', 'rephrased_strengths', 'rephrased_weakness', 'review_rephrase_status']
    if any(col not in df.columns for col in required):
        return False
    if df['review_uid'].fillna('').astype(str).str.strip().eq('').any():
        return False
    return df['review_rephrase_status'].fillna('').astype(str).eq('success').all()


def _latest_completed_output(output_dir: Path, pattern: str) -> Optional[Path]:
    """Latest file matching pattern, excluding *_failures.csv.

    The '*' in these rephrase-output globs also matches the sibling failures CSV,
    and since '.' < '_' it sorts last, so a naive latest-match would wrongly pick
    the failures file as the prior output.
    """
    matches = [
        p for p in sorted(output_dir.glob(pattern))
        if not p.name.endswith('_failures.csv')
    ]
    return matches[-1] if matches else None


def _carry_over_successful_rows(
    out_df: pd.DataFrame,
    partial_df: Optional[pd.DataFrame],
    *,
    key_col: str,
    status_col: str,
    columns: List[str],
) -> None:
    """Copy already-successful rows from a prior partial output into out_df.

    Enables per-row resume: rows carried over here are skipped in the rephrase
    loop, so only failed/missing rows are re-sent to the model. Matches on key_col.
    """
    if partial_df is None or key_col not in partial_df.columns or status_col not in partial_df.columns:
        return
    prior = (
        partial_df[partial_df[status_col].fillna('').astype(str).eq('success')]
        .drop_duplicates(subset=[key_col], keep='last')
        .set_index(key_col)
    )
    for row_idx, row in out_df.iterrows():
        key = row.get(key_col)
        if key in prior.index:
            for col in columns:
                if col in prior.columns:
                    out_df.at[row_idx, col] = prior.at[key, col]


def rephrase_ai_proposals_for_condition(
    *,
    project_root: Path,
    ai_interface: Any,
    condition: str,
    source_path: Path,
    rephrase_model: str,
    rephrase_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_every_n_rows: int,
    resume_ok: bool,
    run_id: str,
) -> Dict[str, Any]:
    """Rephrase one condition's AI proposal CSV into a condition-local CSV."""
    source_df = _coerce_ai_proposal_schema(pd.read_csv(source_path), condition)
    output_dir = project_root / 'data' / 'ai-proposals' / condition / 'rephrased'
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_output = _latest_completed_output(output_dir, f'ai_proposals_{condition}_rephrased_*.csv')
    resume_partial_df = None
    if resume_ok and latest_output is not None:
        existing_df = pd.read_csv(latest_output)
        if _proposal_rephrase_complete(existing_df, source_df):
            return {
                'condition': condition,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else run_id,
                'rephrased_df': existing_df,
                'output_path': latest_output,
                'failures_path': latest_matching_file(output_dir, f'ai_proposals_{condition}_rephrased_*_failures.csv'),
                'manifest_path': latest_matching_file(output_dir, f'proposal_rephrase_manifest_{condition}_*.json'),
                'qa_issues': [],
                'reused_existing': True,
            }
        resume_partial_df = existing_df
        if 'run_id' in existing_df.columns and not existing_df.empty and str(existing_df['run_id'].iloc[0]).strip():
            run_id = str(existing_df['run_id'].iloc[0])

    out_path = output_dir / f'ai_proposals_{condition}_rephrased_{run_id}.csv'
    tmp_path = out_path.with_suffix('.csv.tmp')
    failures_path = output_dir / f'ai_proposals_{condition}_rephrased_{run_id}_failures.csv'
    manifest_path = output_dir / f'proposal_rephrase_manifest_{condition}_{run_id}.json'

    out_df = source_df.copy()
    new_columns = [
        'run_id',
        'rephrase_source_file',
        'proposal_rephrase_model',
        'proposal_rephrase_temperature',
        'proposal_rephrase_prompt_version',
        'proposal_rephrased_at',
        'proposal_rephrase_retry_count',
        'proposal_rephrase_status',
        'proposal_rephrase_error',
        'standardized_text',
        'rephrased_abstract',
    ]
    for col in new_columns:
        if col not in out_df.columns:
            out_df[col] = ''
    _carry_over_successful_rows(
        out_df, resume_partial_df,
        key_col='proposal_uid', status_col='proposal_rephrase_status', columns=new_columns,
    )

    failures: List[Dict[str, Any]] = []
    for row_idx, row in out_df.iterrows():
        if str(out_df.at[row_idx, 'proposal_rephrase_status']).strip() == 'success':
            continue  # carried over from a prior run; do not re-call the model
        full_text = build_ai_full_text(row)
        if not full_text.strip():
            append_rephrase_failure_log(
                failures,
                scope=condition,
                artifact_family='ai_proposals',
                row_id=row.get('proposal_uid', row_idx),
                error='empty AI proposal text',
            )
            continue

        result = _rephrase_proposal_text(
            ai_interface=ai_interface,
            full_text=full_text,
            model_name=rephrase_model,
            temperature=rephrase_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        out_df.at[row_idx, 'run_id'] = run_id
        out_df.at[row_idx, 'rephrase_source_file'] = str(source_path)
        out_df.at[row_idx, 'proposal_rephrase_model'] = rephrase_model
        out_df.at[row_idx, 'proposal_rephrase_temperature'] = rephrase_temperature
        out_df.at[row_idx, 'proposal_rephrase_prompt_version'] = PROPOSAL_REPHRASE_PROMPT_VERSION
        for key, value in result.items():
            out_df.at[row_idx, key] = value
        if result['proposal_rephrase_status'] != 'success':
            append_rephrase_failure_log(
                failures,
                scope=condition,
                artifact_family='ai_proposals',
                row_id=row.get('proposal_uid', row_idx),
                error=result['proposal_rephrase_error'],
            )
        if (row_idx + 1) % save_every_n_rows == 0:
            out_df.to_csv(tmp_path, index=False)
            ensure_failure_csv(failures_path, failures)

    out_df.to_csv(out_path, index=False)
    ensure_failure_csv(failures_path, failures)
    if tmp_path.exists():
        tmp_path.unlink()

    qa_issues: List[str] = []
    if len(out_df) != len(source_df):
        qa_issues.append(f'{condition}: row count mismatch between source and rephrased proposals')
    if out_df['proposal_uid'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing proposal_uid in rephrased proposals')
    if out_df['standardized_text'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing standardized_text in one or more rows')
    if out_df['rephrased_abstract'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing rephrased_abstract in one or more rows')

    success_count = int(out_df['proposal_rephrase_status'].fillna('').astype(str).eq('success').sum())
    manifest = _proposal_rephrase_manifest(
        source_path=source_path,
        output_path=out_path,
        condition_or_cohort=condition,
        run_id=run_id,
        rephrase_model=rephrase_model,
        rephrase_temperature=rephrase_temperature,
        row_count=len(out_df),
        success_count=success_count,
        failure_count=len(out_df) - success_count,
        prompt_version=PROPOSAL_REPHRASE_PROMPT_VERSION,
    )
    manifest['ended_at'] = datetime.now().isoformat()
    manifest['qa_issues'] = qa_issues
    manifest['completed_cleanly'] = not qa_issues and success_count == len(out_df)
    save_generation_manifest(manifest_path, manifest)

    return {
        'condition': condition,
        'run_id': run_id,
        'rephrased_df': out_df,
        'output_path': out_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'manifest': manifest,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


def rephrase_ai_reviews_for_condition(
    *,
    project_root: Path,
    ai_interface: Any,
    condition: str,
    source_path: Path,
    rephrase_model: str,
    rephrase_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_every_n_rows: int,
    resume_ok: bool,
    run_id: str,
) -> Dict[str, Any]:
    """Rephrase one condition's AI review CSV into a condition-local CSV."""
    source_df = _coerce_ai_review_schema(pd.read_csv(source_path), condition)
    output_dir = project_root / 'data' / 'reviews' / 'ai_reviews' / condition / 'rephrased'
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_output = _latest_completed_output(output_dir, f'ai_reviews_{condition}_rephrased_*.csv')
    resume_partial_df = None
    if resume_ok and latest_output is not None:
        existing_df = pd.read_csv(latest_output)
        if _review_rephrase_complete(existing_df, source_df):
            return {
                'condition': condition,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else run_id,
                'rephrased_df': existing_df,
                'output_path': latest_output,
                'failures_path': latest_matching_file(output_dir, f'ai_reviews_{condition}_rephrased_*_failures.csv'),
                'manifest_path': latest_matching_file(output_dir, f'review_rephrase_manifest_{condition}_*.json'),
                'qa_issues': [],
                'reused_existing': True,
            }
        resume_partial_df = existing_df
        if 'run_id' in existing_df.columns and not existing_df.empty and str(existing_df['run_id'].iloc[0]).strip():
            run_id = str(existing_df['run_id'].iloc[0])

    out_path = output_dir / f'ai_reviews_{condition}_rephrased_{run_id}.csv'
    tmp_path = out_path.with_suffix('.csv.tmp')
    failures_path = output_dir / f'ai_reviews_{condition}_rephrased_{run_id}_failures.csv'
    manifest_path = output_dir / f'review_rephrase_manifest_{condition}_{run_id}.json'

    out_df = source_df.copy()
    new_columns = [
        'run_id',
        'rephrase_source_file',
        'review_rephrase_model',
        'review_rephrase_temperature',
        'review_rephrase_prompt_version',
        'review_rephrased_at',
        'review_rephrase_retry_count',
        'review_rephrase_status',
        'review_rephrase_error',
        'rephrased_review',
        'rephrased_strengths',
        'rephrased_weakness',
    ]
    for col in new_columns:
        if col not in out_df.columns:
            out_df[col] = ''
    _carry_over_successful_rows(
        out_df, resume_partial_df,
        key_col='review_uid', status_col='review_rephrase_status', columns=new_columns,
    )

    failures: List[Dict[str, Any]] = []
    for row_idx, row in out_df.iterrows():
        if str(out_df.at[row_idx, 'review_rephrase_status']).strip() == 'success':
            continue  # carried over from a prior run; do not re-call the model
        source_text = _extract_review_source_text(row.to_dict())
        if not source_text.strip():
            append_rephrase_failure_log(
                failures,
                scope=condition,
                artifact_family='ai_reviews',
                row_id=row.get('review_uid', row_idx),
                error='empty AI review text',
            )
            continue

        result = _rephrase_review_text(
            ai_interface=ai_interface,
            review_text=source_text,
            model_name=rephrase_model,
            temperature=rephrase_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        out_df.at[row_idx, 'run_id'] = run_id
        out_df.at[row_idx, 'rephrase_source_file'] = str(source_path)
        out_df.at[row_idx, 'review_rephrase_model'] = rephrase_model
        out_df.at[row_idx, 'review_rephrase_temperature'] = rephrase_temperature
        out_df.at[row_idx, 'review_rephrase_prompt_version'] = REVIEW_REPHRASE_PROMPT_VERSION
        for key, value in result.items():
            out_df.at[row_idx, key] = value
        if result['review_rephrase_status'] != 'success':
            append_rephrase_failure_log(
                failures,
                scope=condition,
                artifact_family='ai_reviews',
                row_id=row.get('review_uid', row_idx),
                error=result['review_rephrase_error'],
            )
        if (row_idx + 1) % save_every_n_rows == 0:
            out_df.to_csv(tmp_path, index=False)
            ensure_failure_csv(failures_path, failures)

    out_df.to_csv(out_path, index=False)
    ensure_failure_csv(failures_path, failures)
    if tmp_path.exists():
        tmp_path.unlink()

    qa_issues: List[str] = []
    if len(out_df) != len(source_df):
        qa_issues.append(f'{condition}: row count mismatch between source and rephrased reviews')
    if out_df['review_uid'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing review_uid in rephrased reviews')
    if out_df['rephrased_review'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing rephrased_review in one or more rows')
    if out_df['rephrased_strengths'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing rephrased_strengths in one or more rows')
    if out_df['rephrased_weakness'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{condition}: missing rephrased_weakness in one or more rows')

    success_count = int(out_df['review_rephrase_status'].fillna('').astype(str).eq('success').sum())
    manifest = _review_rephrase_manifest(
        source_path=source_path,
        output_path=out_path,
        condition_or_cohort=condition,
        run_id=run_id,
        rephrase_model=rephrase_model,
        rephrase_temperature=rephrase_temperature,
        row_count=len(out_df),
        success_count=success_count,
        failure_count=len(out_df) - success_count,
        prompt_version=REVIEW_REPHRASE_PROMPT_VERSION,
    )
    manifest['ended_at'] = datetime.now().isoformat()
    manifest['qa_issues'] = qa_issues
    manifest['completed_cleanly'] = not qa_issues and success_count == len(out_df)
    save_generation_manifest(manifest_path, manifest)

    return {
        'condition': condition,
        'run_id': run_id,
        'rephrased_df': out_df,
        'output_path': out_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'manifest': manifest,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


def _load_human_proposal_payload(source_path: Path, cohort: str) -> List[Dict[str, Any]]:
    payload = json.loads(source_path.read_text())
    proposals = payload.get('proposals', [])
    records: List[Dict[str, Any]] = []
    for proposal in proposals:
        proposal_id = proposal.get('proposal_id')
        records.append(
            {
                **proposal,
                'cohort': cohort,
                'proposal_uid': build_target_proposal_uid(cohort, proposal_id),
            }
        )
    return records


def rephrase_shared_human_proposals(
    *,
    project_root: Path,
    ai_interface: Any,
    source_path: Path,
    cohort: str,
    rephrase_model: str,
    rephrase_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_every_n_rows: int,
    resume_ok: bool,
    run_id: str,
) -> Dict[str, Any]:
    """Rephrase one human proposal cohort into shared JSON and CSV artifacts."""
    records = _load_human_proposal_payload(source_path, cohort)
    source_df = pd.DataFrame(records)
    output_dir = project_root / 'data' / 'human-proposals' / 'rephrased'
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_csv = _latest_completed_output(output_dir, f'human_proposals_rephrased_{cohort}_*.csv')
    resume_partial_df = None
    if resume_ok and latest_csv is not None:
        existing_df = pd.read_csv(latest_csv)
        if _proposal_rephrase_complete(existing_df, source_df):
            latest_json = latest_matching_file(output_dir, f'human_proposals_rephrased_{cohort}_*.json')
            return {
                'cohort': cohort,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else run_id,
                'rephrased_df': existing_df,
                'csv_path': latest_csv,
                'json_path': latest_json,
                'failures_path': latest_matching_file(output_dir, f'human_proposals_rephrased_{cohort}_*_failures.csv'),
                'manifest_path': latest_matching_file(output_dir, f'human_proposal_rephrase_manifest_{cohort}_*.json'),
                'qa_issues': [],
                'reused_existing': True,
            }
        resume_partial_df = existing_df
        if 'run_id' in existing_df.columns and not existing_df.empty and str(existing_df['run_id'].iloc[0]).strip():
            run_id = str(existing_df['run_id'].iloc[0])

    csv_path = output_dir / f'human_proposals_rephrased_{cohort}_{run_id}.csv'
    json_path = output_dir / f'human_proposals_rephrased_{cohort}_{run_id}.json'
    tmp_path = csv_path.with_suffix('.csv.tmp')
    failures_path = output_dir / f'human_proposals_rephrased_{cohort}_{run_id}_failures.csv'
    manifest_path = output_dir / f'human_proposal_rephrase_manifest_{cohort}_{run_id}.json'

    out_df = source_df.copy()
    new_columns = [
        'run_id',
        'rephrase_source_file',
        'proposal_rephrase_model',
        'proposal_rephrase_temperature',
        'proposal_rephrase_prompt_version',
        'proposal_rephrased_at',
        'proposal_rephrase_retry_count',
        'proposal_rephrase_status',
        'proposal_rephrase_error',
        'standardized_text',
        'rephrased_abstract',
    ]
    for col in new_columns:
        if col not in out_df.columns:
            out_df[col] = ''
    _carry_over_successful_rows(
        out_df, resume_partial_df,
        key_col='proposal_uid', status_col='proposal_rephrase_status', columns=new_columns,
    )

    failures: List[Dict[str, Any]] = []
    for row_idx, row in out_df.iterrows():
        if str(out_df.at[row_idx, 'proposal_rephrase_status']).strip() == 'success':
            continue  # carried over from a prior run; do not re-call the model
        full_text = build_human_full_text(row.to_dict())
        if not full_text.strip():
            append_rephrase_failure_log(
                failures,
                scope=cohort,
                artifact_family='human_proposals',
                row_id=row.get('proposal_uid', row_idx),
                error='empty human proposal text',
            )
            continue

        result = _rephrase_proposal_text(
            ai_interface=ai_interface,
            full_text=full_text,
            model_name=rephrase_model,
            temperature=rephrase_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        out_df.at[row_idx, 'run_id'] = run_id
        out_df.at[row_idx, 'rephrase_source_file'] = str(source_path)
        out_df.at[row_idx, 'proposal_rephrase_model'] = rephrase_model
        out_df.at[row_idx, 'proposal_rephrase_temperature'] = rephrase_temperature
        out_df.at[row_idx, 'proposal_rephrase_prompt_version'] = PROPOSAL_REPHRASE_PROMPT_VERSION
        for key, value in result.items():
            out_df.at[row_idx, key] = value
        if result['proposal_rephrase_status'] != 'success':
            append_rephrase_failure_log(
                failures,
                scope=cohort,
                artifact_family='human_proposals',
                row_id=row.get('proposal_uid', row_idx),
                error=result['proposal_rephrase_error'],
            )
        if (row_idx + 1) % save_every_n_rows == 0:
            out_df.to_csv(tmp_path, index=False)
            ensure_failure_csv(failures_path, failures)

    out_df.to_csv(csv_path, index=False)
    if tmp_path.exists():
        tmp_path.unlink()
    ensure_failure_csv(failures_path, failures)
    json_payload = {'cohort': cohort, 'source_file': str(source_path), 'proposals': out_df.to_dict('records')}
    json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False))

    qa_issues: List[str] = []
    if len(out_df) != len(source_df):
        qa_issues.append(f'{cohort}: row count mismatch between source and rephrased human proposals')
    if out_df['proposal_uid'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing proposal_uid in rephrased human proposals')
    if out_df['standardized_text'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing standardized_text in one or more rows')
    if out_df['rephrased_abstract'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing rephrased_abstract in one or more rows')

    success_count = int(out_df['proposal_rephrase_status'].fillna('').astype(str).eq('success').sum())
    manifest = _proposal_rephrase_manifest(
        source_path=source_path,
        output_path=csv_path,
        condition_or_cohort=cohort,
        run_id=run_id,
        rephrase_model=rephrase_model,
        rephrase_temperature=rephrase_temperature,
        row_count=len(out_df),
        success_count=success_count,
        failure_count=len(out_df) - success_count,
        prompt_version=PROPOSAL_REPHRASE_PROMPT_VERSION,
    )
    manifest['json_output_file'] = str(json_path)
    manifest['ended_at'] = datetime.now().isoformat()
    manifest['qa_issues'] = qa_issues
    manifest['completed_cleanly'] = not qa_issues and success_count == len(out_df)
    save_generation_manifest(manifest_path, manifest)

    return {
        'cohort': cohort,
        'run_id': run_id,
        'rephrased_df': out_df,
        'csv_path': csv_path,
        'json_path': json_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'manifest': manifest,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


def _deterministic_human_review_uid(cohort: str, proposal_id: Any, reviewer_id: Any, row_index: int) -> str:
    reviewer = str(reviewer_id).strip() if pd.notna(reviewer_id) else ''
    if not reviewer:
        reviewer = f'row{row_index}'
    return f'{cohort}::{proposal_id}::{reviewer}'


def _load_human_review_rows(source_path: Path, cohort: str) -> pd.DataFrame:
    df = pd.read_excel(source_path, sheet_name='Sheet1')
    df = df.copy()
    df['target_cohort'] = 'y1' if cohort == 'human-y1' else 'y2'
    df['target_proposal_id'] = df['id']
    df['target_proposal_uid'] = df.apply(
        lambda row: build_target_proposal_uid(df.at[row.name, 'target_cohort'], row['id']),
        axis=1,
    )
    df['review_uid'] = [
        _deterministic_human_review_uid(df.at[idx, 'target_cohort'], row['id'], row.get('reviewer_id'), idx)
        for idx, row in df.iterrows()
    ]
    df['_raw_review_text'] = df.apply(build_human_review_text_sheet1, axis=1)
    df['rephrase_source_file'] = str(source_path)
    return df


def rephrase_shared_human_reviews(
    *,
    project_root: Path,
    ai_interface: Any,
    source_path: Path,
    cohort: str,
    rephrase_model: str,
    rephrase_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_every_n_rows: int,
    resume_ok: bool,
    run_id: str,
) -> Dict[str, Any]:
    """Rephrase one shared human review workbook into a timestamped CSV."""
    source_df = _load_human_review_rows(source_path, cohort)
    output_dir = project_root / 'data' / 'reviews' / 'human_reviews' / 'rephrased'
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_csv = _latest_completed_output(output_dir, f'human_reviews_{cohort}_rephrased_*.csv')
    resume_partial_df = None
    if resume_ok and latest_csv is not None:
        existing_df = pd.read_csv(latest_csv)
        if _review_rephrase_complete(existing_df, source_df):
            return {
                'cohort': cohort,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else run_id,
                'rephrased_df': existing_df,
                'csv_path': latest_csv,
                'failures_path': latest_matching_file(output_dir, f'human_reviews_{cohort}_rephrased_*_failures.csv'),
                'manifest_path': latest_matching_file(output_dir, f'human_review_rephrase_manifest_{cohort}_*.json'),
                'qa_issues': [],
                'reused_existing': True,
            }
        # Not complete: keep already-successful rows and re-call only the rest.
        resume_partial_df = existing_df
        if 'run_id' in existing_df.columns and not existing_df.empty and str(existing_df['run_id'].iloc[0]).strip():
            run_id = str(existing_df['run_id'].iloc[0])

    csv_path = output_dir / f'human_reviews_{cohort}_rephrased_{run_id}.csv'
    tmp_path = csv_path.with_suffix('.csv.tmp')
    failures_path = output_dir / f'human_reviews_{cohort}_rephrased_{run_id}_failures.csv'
    manifest_path = output_dir / f'human_review_rephrase_manifest_{cohort}_{run_id}.json'

    rephrase_cols = [
        'run_id',
        'review_rephrase_model',
        'review_rephrase_temperature',
        'review_rephrase_prompt_version',
        'review_rephrased_at',
        'review_rephrase_retry_count',
        'review_rephrase_status',
        'review_rephrase_error',
        'rephrased_review',
        'rephrased_strengths',
        'rephrased_weakness',
    ]
    out_df = source_df.copy()
    for col in rephrase_cols:
        if col not in out_df.columns:
            out_df[col] = ''
    _carry_over_successful_rows(
        out_df, resume_partial_df,
        key_col='review_uid', status_col='review_rephrase_status', columns=rephrase_cols,
    )

    failures: List[Dict[str, Any]] = []
    for row_idx, row in out_df.iterrows():
        if str(out_df.at[row_idx, 'review_rephrase_status']).strip() == 'success':
            continue  # carried over from a prior run; do not re-call the model
        source_text = str(row.get('_raw_review_text', '') or '').strip()
        if not source_text:
            append_rephrase_failure_log(
                failures,
                scope=cohort,
                artifact_family='human_reviews',
                row_id=row.get('review_uid', row_idx),
                error='empty human review text',
            )
            continue

        result = _rephrase_review_text(
            ai_interface=ai_interface,
            review_text=source_text,
            model_name=rephrase_model,
            temperature=rephrase_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        out_df.at[row_idx, 'run_id'] = run_id
        out_df.at[row_idx, 'review_rephrase_model'] = rephrase_model
        out_df.at[row_idx, 'review_rephrase_temperature'] = rephrase_temperature
        out_df.at[row_idx, 'review_rephrase_prompt_version'] = REVIEW_REPHRASE_PROMPT_VERSION
        for key, value in result.items():
            out_df.at[row_idx, key] = value
        if result['review_rephrase_status'] != 'success':
            append_rephrase_failure_log(
                failures,
                scope=cohort,
                artifact_family='human_reviews',
                row_id=row.get('review_uid', row_idx),
                error=result['review_rephrase_error'],
            )
        if (row_idx + 1) % save_every_n_rows == 0:
            out_df.to_csv(tmp_path, index=False)
            ensure_failure_csv(failures_path, failures)

    out_df.to_csv(csv_path, index=False)
    ensure_failure_csv(failures_path, failures)
    if tmp_path.exists():
        tmp_path.unlink()

    qa_issues: List[str] = []
    if len(out_df) != len(source_df):
        qa_issues.append(f'{cohort}: row count mismatch between source and rephrased human reviews')
    if out_df['review_uid'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing review_uid in rephrased human reviews')
    if out_df['rephrased_review'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing rephrased_review in one or more rows')
    if out_df['rephrased_strengths'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing rephrased_strengths in one or more rows')
    if out_df['rephrased_weakness'].fillna('').astype(str).str.strip().eq('').any():
        qa_issues.append(f'{cohort}: missing rephrased_weakness in one or more rows')

    success_count = int(out_df['review_rephrase_status'].fillna('').astype(str).eq('success').sum())
    manifest = _review_rephrase_manifest(
        source_path=source_path,
        output_path=csv_path,
        condition_or_cohort=cohort,
        run_id=run_id,
        rephrase_model=rephrase_model,
        rephrase_temperature=rephrase_temperature,
        row_count=len(out_df),
        success_count=success_count,
        failure_count=len(out_df) - success_count,
        prompt_version=REVIEW_REPHRASE_PROMPT_VERSION,
    )
    manifest['ended_at'] = datetime.now().isoformat()
    manifest['qa_issues'] = qa_issues
    manifest['completed_cleanly'] = not qa_issues and success_count == len(out_df)
    save_generation_manifest(manifest_path, manifest)

    return {
        'cohort': cohort,
        'run_id': run_id,
        'rephrased_df': out_df,
        'csv_path': csv_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'manifest': manifest,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


__all__ = [
    'PROPOSAL_REPHRASE_PROMPT_VERSION',
    'REVIEW_REPHRASE_PROMPT_VERSION',
    'append_rephrase_failure_log',
    'build_rephrase_job_registry',
    'find_project_root',
    'load_human_proposal_sources',
    'load_human_review_sources',
    'locate_latest_ai_proposal_files',
    'locate_latest_ai_review_files',
    'now_run_id',
    'rephrase_ai_proposals_for_condition',
    'rephrase_ai_reviews_for_condition',
    'rephrase_shared_human_proposals',
    'rephrase_shared_human_reviews',
]
