"""
Helpers for the redesigned multi-condition proposal generation stage.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


PROPOSAL_SECTION_COLUMNS = [
    'background_and_significance',
    'research_questions_and_hypotheses',
    'methods_and_approach',
    'expected_outcomes_and_impact',
    'open_science_and_reproducibility',
    'budget_and_resources',
]


def _is_blank_value(value: Any) -> bool:
    """Return True when a scalar should count as missing text/content."""
    if value is None or pd.isna(value):
        return True
    return not str(value).strip()


def find_project_root(start: Optional[Path] = None) -> Path:
    """Find the project root from a notebook or script working directory."""
    base = (start or Path.cwd()).resolve()
    for candidate in [base, *base.parents]:
        if (candidate / 'src').exists() and (candidate / 'data').exists():
            return candidate
    raise RuntimeError('Could not locate project root containing src/ and data/.')


def now_run_id() -> str:
    """Create a compact timestamp-based run id."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def build_target_proposal_uid(cohort: str, proposal_id: Any) -> str:
    """Build a stable pooled human proposal id."""
    return f"{str(cohort).strip().lower()}::{str(proposal_id).strip()}"


def load_shared_call_context(project_root: Path) -> Dict[str, str]:
    """Load the shared NCEMS call text and supporting context."""
    payload = json.loads((project_root / 'data' / 'call_and_info.json').read_text())
    return {
        'research_call': payload['call'],
        'information_about_ncems': payload['info'],
    }


def load_target_proposal_count(project_root: Path) -> int:
    """Count the human comparison proposals across cohorts."""
    roster = load_human_target_roster(project_root)
    return len(roster)


def load_human_target_roster(project_root: Path) -> pd.DataFrame:
    """Build the pooled human proposal roster used for target-count checks."""
    records: List[Dict[str, Any]] = []
    for cohort, filename in [('y1', 'human-proposals-y1.json'), ('y2', 'human-proposals-y2.json')]:
        payload = json.loads((project_root / 'data' / 'human-proposals' / filename).read_text())
        for proposal in payload.get('proposals', []):
            proposal_id = proposal['proposal_id']
            records.append(
                {
                    'target_cohort': cohort,
                    'target_proposal_id': proposal_id,
                    'target_proposal_uid': build_target_proposal_uid(cohort, proposal_id),
                    'target_proposal_title': proposal.get('proposal_title', ''),
                    'target_proposal_status': proposal.get('proposal_status', ''),
                    'target_authors': '; '.join(proposal.get('authors', []) or []),
                }
            )
    df = pd.DataFrame(records)
    if df.empty:
        raise RuntimeError('No human target proposals were loaded.')
    return df.sort_values(['target_cohort', 'target_proposal_id']).reset_index(drop=True)


def load_persona_cards(project_root: Path, human_target_roster: pd.DataFrame) -> pd.DataFrame:
    """Load persona cards and attach stable source proposal ids."""
    payload = json.loads((project_root / 'data' / 'literature' / 'persona_cards.json').read_text())
    cards = payload.get('cards', [])
    if not cards:
        raise RuntimeError('No persona cards found in data/literature/persona_cards.json.')

    title_to_uid = {
        row.target_proposal_title.strip().lower(): row.target_proposal_uid
        for row in human_target_roster.itertuples(index=False)
    }
    id_to_uid = {
        (row.target_cohort, str(row.target_proposal_id)): row.target_proposal_uid
        for row in human_target_roster.itertuples(index=False)
    }

    records: List[Dict[str, Any]] = []
    for idx, card in enumerate(cards, start=1):
        cohort = str(card.get('cohort', '')).strip().lower()
        proposal_id = str(card.get('human_proposal_id') or card.get('source_human_proposal_id') or '').strip()
        proposal_title = str(card.get('human_proposal_title') or card.get('source_human_proposal_title') or '').strip()
        matched_uid = id_to_uid.get((cohort, proposal_id)) or title_to_uid.get(proposal_title.lower())
        records.append(
            {
                'persona_card_id': card.get('team_id', f'persona-{idx:02d}'),
                'persona_team_id': card.get('team_id', f'persona-{idx:02d}'),
                'persona_team_authors': '; '.join(card.get('team_members', []) or []),
                'source_human_proposal_id': proposal_id or None,
                'source_human_proposal_title': proposal_title or None,
                'matched_human_proposal_uid': matched_uid,
                'cohort': cohort,
                'team_members': card.get('team_members', []) or [],
                'persona_card_json': json.dumps(card, indent=2, ensure_ascii=False),
            }
        )

    df = pd.DataFrame(records).sort_values(['cohort', 'persona_card_id']).reset_index(drop=True)
    return df


def build_condition_registry(target_n: int) -> Dict[str, Dict[str, Any]]:
    """Return explicit study condition configs."""
    return {
        'baseline': {
            'condition': 'baseline',
            'idea_prompt_template': 'generate_ideas_minimal_batch',
            'proposal_prompt_template': 'generate_proposals_minimal',
            'idea_generation_mode': 'batch',
            'uses_persona_cards': False,
            'reuse_persona_in_proposal': False,
            'expected_rows_per_model': target_n,
        },
        'one_at_a_time': {
            'condition': 'one_at_a_time',
            'idea_prompt_template': 'generate_ideas_minimal_single',
            'proposal_prompt_template': 'generate_proposals_minimal',
            'idea_generation_mode': 'independent_single',
            'uses_persona_cards': False,
            'reuse_persona_in_proposal': False,
            'expected_rows_per_model': target_n,
        },
        'persona': {
            'condition': 'persona',
            'idea_prompt_template': 'generate_ideas_persona_single',
            'proposal_prompt_template': 'generate_proposals_persona_minimal',
            'idea_generation_mode': 'independent_single',
            'uses_persona_cards': True,
            'reuse_persona_in_proposal': True,
            'expected_rows_per_model': target_n,
        },
    }


def extract_first_json_object(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Extract the first JSON object from a model response."""
    if not text or not text.strip():
        return None, 'empty response'
    s = text.strip()
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


def parse_generated_ideas_response(raw_text: str, expected_count: int, mode: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Parse idea-generation JSON and validate the expected number of records."""
    payload, parse_error = extract_first_json_object(raw_text)
    if payload is None:
        return [], parse_error

    raw_ideas = payload.get('research_ideas')
    if isinstance(raw_ideas, dict):
        raw_ideas = [raw_ideas]
    if not isinstance(raw_ideas, list):
        return [], 'missing research_ideas list'

    ideas: List[Dict[str, Any]] = []
    for item in raw_ideas:
        title = str((item or {}).get('title', '')).strip()
        abstract = str((item or {}).get('abstract', '')).strip()
        ideas.append({'title': title, 'abstract': abstract})

    if len(ideas) != expected_count:
        return [], f'expected {expected_count} idea(s), parsed {len(ideas)}'

    if mode == 'independent_single' and len(ideas) != 1:
        return [], f'independent_single expected 1 idea, parsed {len(ideas)}'

    return ideas, None


def parse_generated_proposal_response(raw_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse proposal-generation JSON and validate required sections."""
    payload, parse_error = extract_first_json_object(raw_text)
    if payload is None:
        return None, parse_error
    proposal = payload.get('proposal')
    if not isinstance(proposal, dict):
        return None, 'missing proposal object'
    missing = [col for col in PROPOSAL_SECTION_COLUMNS if not str(proposal.get(col, '')).strip()]
    if missing:
        return None, f'missing proposal section(s): {", ".join(missing)}'
    return proposal, None


def validate_idea_records(df: pd.DataFrame, expected_rows_per_model: int, condition: str) -> List[str]:
    """Return QA messages for the generated ideas table."""
    issues: List[str] = []
    if df.empty:
        return ['ideas dataframe is empty']

    for col in ['title', 'abstract', 'model', 'idea_call_id']:
        if col not in df.columns or df[col].map(_is_blank_value).any():
            issues.append(f'missing values found in {col}')

    counts = df.groupby('model').size().to_dict()
    for model_name, count in counts.items():
        if count != expected_rows_per_model:
            issues.append(
                f'{condition}: model {model_name} has {count} ideas; expected {expected_rows_per_model}'
            )

    if condition == 'baseline':
        call_counts = df.groupby('model')['idea_call_id'].nunique().to_dict()
        for model_name, count in call_counts.items():
            if count != 1:
                issues.append(f'baseline: model {model_name} has {count} idea calls; expected 1')

    if condition in {'one_at_a_time', 'persona'}:
        call_counts = df.groupby('model')['idea_call_id'].nunique().to_dict()
        for model_name, count in call_counts.items():
            if count != expected_rows_per_model:
                issues.append(
                    f'{condition}: model {model_name} has {count} idea calls; expected {expected_rows_per_model}'
                )

    return issues


def validate_proposal_record(row: Dict[str, Any]) -> List[str]:
    """Return missing proposal-section issues for one row."""
    issues: List[str] = []
    for col in PROPOSAL_SECTION_COLUMNS:
        if _is_blank_value(row.get(col, '')):
            issues.append(f'missing {col}')
    return issues


def append_failure_log(failures: List[Dict[str, Any]], **record: Any) -> None:
    """Append one failure record in a stable format."""
    failures.append(
        {
            'failed_at': datetime.now().isoformat(),
            **record,
        }
    )


def save_generation_manifest(path: Path, payload: Dict[str, Any]) -> None:
    """Write a machine-readable generation manifest."""
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def latest_matching_file(directory: Path, pattern: str) -> Optional[Path]:
    """Return the latest file matching a glob pattern."""
    matches = sorted(directory.glob(pattern))
    return matches[-1] if matches else None


def extract_run_id_from_path(path: Optional[Path], prefix: str) -> Optional[str]:
    """Extract the run id suffix from a generated artifact path."""
    if path is None:
        return None
    stem = path.stem
    if stem.startswith(prefix):
        return stem[len(prefix):]
    return None


def load_failures_csv(path: Optional[Path]) -> List[Dict[str, Any]]:
    """Load a prior failures CSV if present."""
    if path is None or not path.exists():
        return []
    df = pd.read_csv(path)
    if df.empty:
        return []
    return df.to_dict('records')


def _idea_call_is_complete(rows: pd.DataFrame, schedule_row: Dict[str, Any]) -> bool:
    """Return whether one idea-generation call is already complete in a partial CSV."""
    subset = rows[rows['idea_call_id'] == schedule_row['idea_call_id']].copy()
    expected = int(schedule_row['expected_idea_count'])
    if len(subset) != expected:
        return False
    required_cols = ['title', 'abstract', 'proposal_uid', 'idea_draw_index']
    for col in required_cols:
        if col not in subset.columns:
            return False
        if subset[col].fillna('').astype(str).str.strip().eq('').any():
            return False
    if subset['proposal_uid'].astype(str).duplicated().any():
        return False
    if condition := schedule_row.get('condition'):
        if condition == 'baseline':
            expected_draws = list(range(1, expected + 1))
            observed = sorted(pd.to_numeric(subset['idea_draw_index'], errors='coerce').dropna().astype(int).tolist())
            return observed == expected_draws
    return True


def _deduplicate_idea_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one stable row per proposal_uid in resumed idea outputs."""
    if df.empty or 'proposal_uid' not in df.columns:
        return df
    return df.drop_duplicates(subset=['proposal_uid'], keep='last').copy()


def _proposal_row_is_complete(row: Dict[str, Any]) -> bool:
    """Return whether one proposal row has all required expanded sections."""
    return len(validate_proposal_record(row)) == 0


def build_proposal_uid(condition: str, model_name: str, idea_draw_index: int) -> str:
    """Create a stable AI proposal id within a condition."""
    return f"{condition}::{model_name}::{idea_draw_index:02d}"


def idea_schedule_rows(condition_config: Dict[str, Any], model_name: str, target_n: int, persona_roster: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
    """Create the idea-generation schedule for one condition-model pair."""
    condition = condition_config['condition']
    rows: List[Dict[str, Any]] = []
    if condition == 'baseline':
        call_id = f'{condition}::{model_name}::idea_call_001'
        rows.append(
            {
                'condition': condition,
                'model': model_name,
                'idea_call_id': call_id,
                'expected_idea_count': target_n,
                'idea_generation_mode': 'batch',
                'idea_draw_index': None,
                'idea_position_in_call': None,
                'persona_payload': None,
            }
        )
        return rows

    persona_records = []
    if condition == 'persona':
        if persona_roster is None or len(persona_roster) != target_n:
            raise RuntimeError('Persona condition requires one persona card per human target proposal.')
        persona_records = persona_roster.to_dict('records')

    for draw_index in range(1, target_n + 1):
        payload = persona_records[draw_index - 1] if condition == 'persona' else None
        rows.append(
            {
                'condition': condition,
                'model': model_name,
                'idea_call_id': f'{condition}::{model_name}::idea_call_{draw_index:03d}',
                'expected_idea_count': 1,
                'idea_generation_mode': 'independent_single',
                'idea_draw_index': draw_index,
                'idea_position_in_call': 1,
                'persona_payload': payload,
            }
        )
    return rows


def normalize_idea_row(
    *,
    condition: str,
    run_id: str,
    model_name: str,
    idea: Dict[str, Any],
    idea_generation_mode: str,
    idea_call_id: str,
    idea_position_in_call: int,
    idea_draw_index: int,
    prompt_template_name: str,
    prompt_template_version: str,
    provider_model_id: str,
    temperature: float,
    generated_at: str,
    persona_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build one canonical idea/proposal row before proposal expansion."""
    persona_payload = persona_payload or {}
    proposal_uid = build_proposal_uid(condition, model_name, idea_draw_index)
    return {
        'proposal_uid': proposal_uid,
        'run_id': run_id,
        'condition': condition,
        'model': model_name,
        'author': model_name,
        'title': idea['title'],
        'abstract': idea['abstract'],
        'background_and_significance': '',
        'research_questions_and_hypotheses': '',
        'methods_and_approach': '',
        'expected_outcomes_and_impact': '',
        'open_science_and_reproducibility': '',
        'budget_and_resources': '',
        'idea_uid': proposal_uid,
        'idea_index': idea_draw_index,
        'generation_mode': idea_generation_mode,
        'temperature': temperature,
        'prompt_template': prompt_template_name,
        'idea_generation_mode': idea_generation_mode,
        'idea_call_id': idea_call_id,
        'idea_position_in_call': idea_position_in_call,
        'idea_draw_index': idea_draw_index,
        'idea_prompt_template': prompt_template_name,
        'idea_prompt_version': prompt_template_version,
        'idea_provider_model_id': provider_model_id,
        'idea_temperature': temperature,
        'idea_generated_at': generated_at,
        'proposal_call_id': '',
        'proposal_prompt_template': '',
        'proposal_prompt_version': '',
        'proposal_provider_model_id': '',
        'proposal_temperature': temperature,
        'proposal_generated_at': '',
        'persona_card_id': persona_payload.get('persona_card_id'),
        'persona_team_id': persona_payload.get('persona_team_id'),
        'persona_team_authors': persona_payload.get('persona_team_authors'),
        'source_human_proposal_id': persona_payload.get('source_human_proposal_id'),
        'source_human_proposal_title': persona_payload.get('source_human_proposal_title'),
        'matched_human_proposal_uid': persona_payload.get('matched_human_proposal_uid'),
        'persona_card_json': persona_payload.get('persona_card_json'),
    }


def manifest_base(
    *,
    condition: str,
    run_id: str,
    target_n: int,
    models: List[str],
    idea_prompt_template: str,
    proposal_prompt_template: str,
    idea_prompt_version: str,
    proposal_prompt_version: str,
    temperature: float,
) -> Dict[str, Any]:
    """Create the shared manifest structure for one condition run."""
    return {
        'condition': condition,
        'run_id': run_id,
        'target_n': target_n,
        'models_run': models,
        'idea_prompt_template': idea_prompt_template,
        'idea_prompt_version': idea_prompt_version,
        'proposal_prompt_template': proposal_prompt_template,
        'proposal_prompt_version': proposal_prompt_version,
        'temperature': temperature,
        'started_at': datetime.now().isoformat(),
    }


def ensure_failure_csv(path: Path, failures: List[Dict[str, Any]]) -> None:
    """Write failures to CSV even when the list is empty."""
    df = pd.DataFrame(failures)
    if df.empty:
        df = pd.DataFrame(columns=['failed_at', 'condition', 'stage', 'model', 'call_id', 'error'])
    df.to_csv(path, index=False)


def build_idea_prompt_kwargs(
    shared_call_context: Dict[str, str],
    condition_config: Dict[str, Any],
    target_n: int,
    schedule_row: Dict[str, Any],
) -> Dict[str, Any]:
    """Build prompt kwargs for one idea-generation call."""
    kwargs = dict(shared_call_context)
    if condition_config['idea_generation_mode'] == 'batch':
        kwargs['num'] = target_n
    if condition_config['condition'] == 'persona':
        persona_payload = schedule_row['persona_payload'] or {}
        kwargs['team_members'] = '; '.join(persona_payload.get('team_members', []))
        kwargs['persona_card_json'] = persona_payload.get('persona_card_json', '{}')
    return kwargs


def run_idea_generation_for_condition(
    *,
    project_root: Path,
    ai_interface: Any,
    prompt_manager: Any,
    shared_call_context: Dict[str, str],
    condition_config: Dict[str, Any],
    models_to_use: List[str],
    target_n: int,
    persona_roster: Optional[pd.DataFrame],
    generation_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_progress_every_n_calls: int,
    resume_ok: bool,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate ideas for one condition and save the canonical idea CSV."""
    condition = condition_config['condition']
    output_dir = project_root / 'data' / 'ai-proposals' / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_ideas = latest_matching_file(output_dir, f'ai_ideas_{condition}_*.csv')
    latest_failures = latest_matching_file(output_dir, f'ai_ideas_{condition}_*_failures.csv')
    latest_manifest = latest_matching_file(output_dir, f'generation_manifest_{condition}_*.json')
    if resume_ok and latest_ideas is not None:
        existing_df = pd.read_csv(latest_ideas)
        issues = validate_idea_records(existing_df, condition_config['expected_rows_per_model'], condition)
        if not issues:
            existing_run_id = str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else latest_ideas.stem.split('_')[-1]
            return {
                'condition': condition,
                'run_id': existing_run_id,
                'ideas_df': existing_df,
                'ideas_path': latest_ideas,
                'failures_path': latest_failures,
                'manifest_path': latest_manifest,
                'manifest': {'condition': condition, 'run_id': existing_run_id, 'reused_existing_ideas': True},
                'qa_issues': [],
                'reused_existing': True,
            }

    resolved_models = [ai_interface.resolve_model_name(model_name) for model_name in models_to_use]
    existing_partial_df = pd.DataFrame()
    resumed_from_partial = False
    if resume_ok and latest_ideas is not None:
        existing_partial_df = _deduplicate_idea_rows(pd.read_csv(latest_ideas))
        partial_run_id = (
            str(existing_partial_df['run_id'].iloc[0])
            if 'run_id' in existing_partial_df.columns and not existing_partial_df.empty
            else extract_run_id_from_path(latest_ideas, f'ai_ideas_{condition}_')
        )
        if partial_run_id:
            run_id = partial_run_id
            resumed_from_partial = not existing_partial_df.empty
    run_id = run_id or now_run_id()
    idea_template = prompt_manager.get_template(condition_config['idea_prompt_template'])
    proposal_template = prompt_manager.get_template(condition_config['proposal_prompt_template'])
    ideas_path = output_dir / f'ai_ideas_{condition}_{run_id}.csv'
    failures_path = output_dir / f'ai_ideas_{condition}_{run_id}_failures.csv'
    manifest_path = output_dir / f'generation_manifest_{condition}_{run_id}.json'

    manifest = manifest_base(
        condition=condition,
        run_id=run_id,
        target_n=target_n,
        models=resolved_models,
        idea_prompt_template=condition_config['idea_prompt_template'],
        proposal_prompt_template=condition_config['proposal_prompt_template'],
        idea_prompt_version=idea_template.version,
        proposal_prompt_version=proposal_template.version,
        temperature=generation_temperature,
    )

    all_rows: List[Dict[str, Any]] = existing_partial_df.to_dict('records') if not existing_partial_df.empty else []
    failures: List[Dict[str, Any]] = load_failures_csv(failures_path if failures_path.exists() else latest_failures)
    calls_completed = 0

    for model_name in resolved_models:
        schedule = idea_schedule_rows(
            condition_config=condition_config,
            model_name=model_name,
            target_n=target_n,
            persona_roster=persona_roster,
        )
        for schedule_row in schedule:
            current_df = _deduplicate_idea_rows(pd.DataFrame(all_rows))
            if not current_df.empty and _idea_call_is_complete(current_df, schedule_row):
                continue
            prompt_kwargs = build_idea_prompt_kwargs(
                shared_call_context=shared_call_context,
                condition_config=condition_config,
                target_n=target_n,
                schedule_row=schedule_row,
            )
            prompt = prompt_manager.format_prompt(
                condition_config['idea_prompt_template'],
                prompt_kwargs,
            )
            result = ai_interface.generate_content_with_metadata(
                prompt,
                model_name=model_name,
                temperature=generation_temperature,
                max_tokens=max_tokens,
                retry_delays=retry_delays,
            )
            calls_completed += 1

            if result['error']:
                append_failure_log(
                    failures,
                    condition=condition,
                    stage='idea_generation',
                    model=model_name,
                    call_id=schedule_row['idea_call_id'],
                    error=result['error'],
                )
            else:
                ideas, parse_error = parse_generated_ideas_response(
                    result['raw_response'],
                    expected_count=schedule_row['expected_idea_count'],
                    mode=condition_config['idea_generation_mode'],
                )
                if parse_error:
                    append_failure_log(
                        failures,
                        condition=condition,
                        stage='idea_generation',
                        model=model_name,
                        call_id=schedule_row['idea_call_id'],
                        error=parse_error,
                    )
                else:
                    for idx, idea in enumerate(ideas, start=1):
                        persona_payload = schedule_row['persona_payload']
                        position_in_call = idx if condition == 'baseline' else 1
                        draw_index = idx if condition == 'baseline' else int(schedule_row['idea_draw_index'])
                        all_rows.append(
                            normalize_idea_row(
                                condition=condition,
                                run_id=run_id,
                                model_name=model_name,
                                idea=idea,
                                idea_generation_mode=condition_config['idea_generation_mode'],
                                idea_call_id=schedule_row['idea_call_id'],
                                idea_position_in_call=position_in_call,
                                idea_draw_index=draw_index,
                                prompt_template_name=condition_config['idea_prompt_template'],
                                prompt_template_version=idea_template.version,
                                provider_model_id=result['provider_model_id'],
                                temperature=generation_temperature,
                                generated_at=result['timestamp'],
                                persona_payload=persona_payload,
                            )
                        )

            if calls_completed % save_progress_every_n_calls == 0 and all_rows:
                partial_df = _deduplicate_idea_rows(pd.DataFrame(all_rows))
                partial_df.sort_values(['model', 'idea_draw_index']).to_csv(ideas_path, index=False)
                ensure_failure_csv(failures_path, failures)

    ideas_df = _deduplicate_idea_rows(pd.DataFrame(all_rows))
    if not ideas_df.empty:
        ideas_df = ideas_df.sort_values(['model', 'idea_draw_index']).reset_index(drop=True)
        ideas_df.to_csv(ideas_path, index=False)
    ensure_failure_csv(failures_path, failures)

    qa_issues = validate_idea_records(ideas_df, condition_config['expected_rows_per_model'], condition)
    manifest.update(
        {
            'idea_calls_completed': calls_completed,
            'idea_rows_completed': len(ideas_df),
            'idea_failures': len(failures),
            'idea_qa_issues': qa_issues,
            'resumed_from_partial': resumed_from_partial,
            'completed_cleanly': not qa_issues and not failures,
            'ended_at': datetime.now().isoformat(),
        }
    )
    save_generation_manifest(manifest_path, manifest)

    return {
        'condition': condition,
        'run_id': run_id,
        'ideas_df': ideas_df,
        'ideas_path': ideas_path,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'manifest': manifest,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }


def run_proposal_expansion_for_condition(
    *,
    project_root: Path,
    ai_interface: Any,
    prompt_manager: Any,
    shared_call_context: Dict[str, str],
    condition_config: Dict[str, Any],
    ideas_df: pd.DataFrame,
    generation_temperature: float,
    max_tokens: int,
    retry_delays: List[int],
    save_progress_every_n_calls: int,
    resume_ok: bool,
    run_id: str,
) -> Dict[str, Any]:
    """Expand generated ideas into full proposals for one condition."""
    condition = condition_config['condition']
    output_dir = project_root / 'data' / 'ai-proposals' / condition
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_complete = latest_matching_file(output_dir, f'ai_proposals_{condition}_complete_*.csv')
    latest_progress = latest_matching_file(output_dir, f'ai_proposals_{condition}_progress_*.csv')
    latest_failures = latest_matching_file(output_dir, f'ai_proposals_{condition}_*_failures.csv')
    if resume_ok and latest_complete is not None:
        existing_df = pd.read_csv(latest_complete)
        proposal_issues = []
        for row in existing_df.to_dict('records'):
            proposal_issues.extend(validate_proposal_record(row))
        if not proposal_issues and len(existing_df) == len(ideas_df):
            return {
                'condition': condition,
                'run_id': str(existing_df['run_id'].iloc[0]) if 'run_id' in existing_df.columns and not existing_df.empty else run_id,
                'proposals_df': existing_df,
                'progress_path': latest_progress,
                'complete_path': latest_complete,
                'failures_path': latest_failures,
                'qa_issues': [],
                'reused_existing': True,
            }

    existing_progress_df = pd.DataFrame()
    resumed_from_partial = False
    if resume_ok and latest_progress is not None:
        existing_progress_df = pd.read_csv(latest_progress)
        partial_run_id = (
            str(existing_progress_df['run_id'].iloc[0])
            if 'run_id' in existing_progress_df.columns and not existing_progress_df.empty
            else extract_run_id_from_path(latest_progress, f'ai_proposals_{condition}_progress_')
        )
        if partial_run_id:
            run_id = partial_run_id
            resumed_from_partial = not existing_progress_df.empty

    run_id = run_id or now_run_id()
    proposal_template = prompt_manager.get_template(condition_config['proposal_prompt_template'])
    progress_path = output_dir / f'ai_proposals_{condition}_progress_{run_id}.csv'
    complete_path = output_dir / f'ai_proposals_{condition}_complete_{run_id}.csv'
    failures_path = output_dir / f'ai_proposals_{condition}_{run_id}_failures.csv'
    manifest_path = output_dir / f'generation_manifest_{condition}_{run_id}.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'condition': condition, 'run_id': run_id}

    proposals_df = ideas_df.copy()
    for col in PROPOSAL_SECTION_COLUMNS + ['proposal_call_id', 'proposal_prompt_template', 'proposal_prompt_version', 'proposal_temperature', 'proposal_generated_at']:
        if col not in proposals_df.columns:
            proposals_df[col] = ''
    if 'proposal_provider_model_id' not in proposals_df.columns:
        proposals_df['proposal_provider_model_id'] = ''

    if not existing_progress_df.empty and 'proposal_uid' in existing_progress_df.columns:
        progress_lookup = existing_progress_df.drop_duplicates(subset=['proposal_uid'], keep='last').set_index('proposal_uid')
        for idx, row in proposals_df.iterrows():
            uid = row.get('proposal_uid')
            if uid in progress_lookup.index:
                for col in proposals_df.columns:
                    if col in progress_lookup.columns:
                        proposals_df.at[idx, col] = progress_lookup.at[uid, col]

    failures: List[Dict[str, Any]] = load_failures_csv(failures_path if failures_path.exists() else latest_failures)
    calls_completed = 0

    for row_idx, row in proposals_df.iterrows():
        if _proposal_row_is_complete(row.to_dict()):
            continue

        model_name = row['model']
        prompt_kwargs = {
            **shared_call_context,
            'title': row['title'],
            'abstract': row['abstract'],
        }
        if condition_config['reuse_persona_in_proposal']:
            prompt_kwargs['persona_card_json'] = row.get('persona_card_json', '') or '{}'
        prompt = prompt_manager.format_prompt(
            condition_config['proposal_prompt_template'],
            prompt_kwargs,
        )
        result = ai_interface.generate_content_with_metadata(
            prompt,
            model_name=model_name,
            temperature=generation_temperature,
            max_tokens=max_tokens,
            retry_delays=retry_delays,
        )
        calls_completed += 1

        if result['error']:
            append_failure_log(
                failures,
                condition=condition,
                stage='proposal_expansion',
                model=model_name,
                call_id=f"{condition}::{model_name}::proposal_call_{int(row['idea_draw_index']):03d}",
                error=result['error'],
            )
        else:
            proposal, parse_error = parse_generated_proposal_response(result['raw_response'])
            if parse_error:
                append_failure_log(
                    failures,
                    condition=condition,
                    stage='proposal_expansion',
                    model=model_name,
                    call_id=f"{condition}::{model_name}::proposal_call_{int(row['idea_draw_index']):03d}",
                    error=parse_error,
                )
            else:
                for col in PROPOSAL_SECTION_COLUMNS:
                    proposals_df.at[row_idx, col] = proposal[col]
                proposals_df.at[row_idx, 'proposal_call_id'] = f"{condition}::{model_name}::proposal_call_{int(row['idea_draw_index']):03d}"
                proposals_df.at[row_idx, 'proposal_prompt_template'] = condition_config['proposal_prompt_template']
                proposals_df.at[row_idx, 'proposal_prompt_version'] = proposal_template.version
                proposals_df.at[row_idx, 'proposal_provider_model_id'] = result['provider_model_id']
                proposals_df.at[row_idx, 'proposal_temperature'] = generation_temperature
                proposals_df.at[row_idx, 'proposal_generated_at'] = result['timestamp']

        if calls_completed % save_progress_every_n_calls == 0:
            proposals_df.to_csv(progress_path, index=False)
            ensure_failure_csv(failures_path, failures)

    proposals_df.to_csv(progress_path, index=False)
    ensure_failure_csv(failures_path, failures)

    qa_issues: List[str] = []
    for row in proposals_df.to_dict('records'):
        qa_issues.extend(validate_proposal_record(row))
    if not qa_issues:
        proposals_df.to_csv(complete_path, index=False)

    manifest.update(
        {
            'proposal_prompt_template': condition_config['proposal_prompt_template'],
            'proposal_prompt_version': proposal_template.version,
            'proposal_expansions_completed': calls_completed,
            'proposal_failures': len(failures),
            'proposal_qa_issues': qa_issues,
            'resumed_from_partial': resumed_from_partial,
            'completed_cleanly': manifest.get('completed_cleanly', True) and not qa_issues and not failures,
            'ended_at': datetime.now().isoformat(),
        }
    )
    save_generation_manifest(manifest_path, manifest)

    return {
        'condition': condition,
        'run_id': run_id,
        'proposals_df': proposals_df,
        'progress_path': progress_path,
        'complete_path': complete_path if not qa_issues else None,
        'failures_path': failures_path,
        'manifest_path': manifest_path,
        'qa_issues': qa_issues,
        'reused_existing': False,
    }
