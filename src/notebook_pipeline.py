import base64
import io
import json
import os
import traceback
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Iterable, List, Optional

from pipeline_config import ConditionConfig, NotebookSpec


class NotebookTemplateError(RuntimeError):
    pass


class NotebookExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class NotebookRenderResult:
    notebook: Dict[str, Any]
    output_path: Path


def _load_notebook(path: Path) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def _write_notebook(path: Path, notebook: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(notebook, f, indent=1)
        f.write('\n')


def _find_code_cell_index(notebook: Dict[str, Any], required_fragments: Iterable[str]) -> int:
    fragments = tuple(required_fragments)
    for idx, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell.get('source', []))
        if all(fragment in source for fragment in fragments):
            return idx
    raise NotebookTemplateError(f'Could not find code cell containing fragments: {fragments}')


def _set_cell_source(notebook: Dict[str, Any], cell_index: int, source: str) -> None:
    notebook['cells'][cell_index]['source'] = source.splitlines(keepends=True)
    notebook['cells'][cell_index]['outputs'] = []
    notebook['cells'][cell_index]['execution_count'] = None


def _prepend_cells(notebook: Dict[str, Any], cells: List[Dict[str, Any]]) -> None:
    notebook['cells'] = cells + notebook.get('cells', [])


def _render_gen_proposals(notebook: Dict[str, Any], condition: ConditionConfig,
                          generate_new_ideas: bool) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                'Set the condition and the main execution flags here before running the notebook.\n',
                '\n',
                '- `CONDITION`: experimental condition folder under `data/ai-proposals/`.\n',
                '- `GENERATE_NEW_IDEAS`: `True` to call the models for fresh ideas, `False` to load existing idea files.\n',
                '- `SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS`: `True` to reuse the latest complete proposal CSV if one already exists.\n',
                '- `RUN_REPHRASE_AT_END`: `True` to run `src/rephrase_proposals.py` after proposal generation finishes.\n',
                '- `GENERATION_TEMPERATURE`: sampling temperature used for AI idea and proposal generation.\n',
                '- `IDEAS_FILE_OVERRIDE` / `IDEAS_GLOB`: optional controls for selecting an existing ideas file when not generating new ideas.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
                GENERATE_NEW_IDEAS = {str(generate_new_ideas)}
                SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS = True
                RUN_REPHRASE_AT_END = True
                GENERATION_TEMPERATURE = {condition.generation_temperature}
                IDEAS_FILE_OVERRIDE = None
                IDEAS_GLOB = None
            """).splitlines(keepends=True),
        },
    ])
    setup_idx = _find_code_cell_index(
        rendered,
        ['# Option B: Just install requirements from src/requirements.txt', 'REQUIREMENTS_PATH']
    )
    _set_cell_source(rendered, setup_idx, dedent("""\
        # Option 1: Run setup.py (recommended - also creates .env config file)
        # This uses the setup script from src/setup.py which installs from src/requirements.txt
        import subprocess
        import sys
        from pathlib import Path

        def find_project_root():
            candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
            for candidate in candidates:
                if (candidate / 'src').exists() and (candidate / 'data').exists():
                    return candidate.resolve()
            raise RuntimeError('Could not find project root containing src/ and data/.')

        PROJECT_ROOT = find_project_root()
        REQUIREMENTS_PATH = PROJECT_ROOT / 'src' / 'requirements.txt'
        SETUP_SCRIPT_PATH = PROJECT_ROOT / 'src' / 'setup.py'

        # Uncomment ONE of the following options:

        # Option A: Run the full setup script (installs dependencies + creates .env file)
        # subprocess.check_call([sys.executable, str(SETUP_SCRIPT_PATH)], cwd=PROJECT_ROOT)

        # Option B: Just install requirements from src/requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)], cwd=PROJECT_ROOT)

        print("ℹ️  To install dependencies, uncomment one of the options above and run this cell")
        print(f"✓ Dependencies defined in: {REQUIREMENTS_PATH}")
        print(f"✓ Setup script available at: {SETUP_SCRIPT_PATH}")
    """))

    imports_idx = _find_code_cell_index(rendered, ['# Add src to path to import custom modules', 'from ai_models_interface import AIModelsInterface'])
    _set_cell_source(rendered, imports_idx, dedent("""\
        import sys
        import os
        import json
        import pandas as pd
        from pathlib import Path
        from datetime import datetime
        import logging

        def find_project_root():
            candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
            for candidate in candidates:
                if (candidate / 'src').exists() and (candidate / 'data').exists():
                    return candidate.resolve()
            raise RuntimeError('Could not find project root containing src/ and data/.')

        PROJECT_ROOT = find_project_root()

        # Add src to path to import custom modules
        src_path = str(PROJECT_ROOT / 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        # Import custom modules from src/
        from ai_models_interface import AIModelsInterface
        from prompt_templates import PromptManager

        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)

        print("✓ Imports successful")
        print(f"✓ Working directory: {os.getcwd()}")
        print(f"✓ Project root: {PROJECT_ROOT}")
        print(f"✓ Python path includes: {src_path}")
    """))

    idx = _find_code_cell_index(rendered, ['# Condition Configuration', 'CONDITION ='])
    source = dedent(f"""\
        # =========================
        # Condition Configuration
        # =========================
        # This cell is auto-managed by src/run_condition.py.
        CONDITION = '{condition.name}'
        GENERATE_NEW_IDEAS = {str(generate_new_ideas)}
        SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS = globals().get('SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS', True)
        RUN_REPHRASE_AT_END = globals().get('RUN_REPHRASE_AT_END', True)

        IDEA_PROMPT_TEMPLATE = '{condition.idea_prompt_template}'
        PROPOSAL_PROMPT_TEMPLATE = '{condition.proposal_prompt_template}'
        GENERATION_TEMPERATURE = {condition.generation_temperature}

        NUM_IDEAS_PER_MODEL = 23
        IDEAS_FILE_OVERRIDE = globals().get('IDEAS_FILE_OVERRIDE', None)
        IDEAS_GLOB = globals().get('IDEAS_GLOB', None)
        IS_PERSONA_CONDITION = CONDITION == 'persona'
        PERSONA_CARDS_PATH = PROJECT_ROOT / 'data' / 'literature' / 'persona_cards.json'
        REPHRASE_SCRIPT_PATH = PROJECT_ROOT / 'src' / 'rephrase_proposals.py'

        condition_slug = CONDITION.replace('/', '_').replace(' ', '_')
        ideas_input_dir = PROJECT_ROOT / 'data' / 'ai-proposals' / CONDITION
        output_dir = ideas_input_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        MODEL_CANONICAL_MAP = {{
            'gpt-5.2': 'gpt-5.2',
            'gpt5.2': 'gpt-5.2',
            'gpt': 'gpt-5.2',
            'gpt-5': 'gpt-5.2',
            'gemini-3-pro-preview': 'gemini-3-pro-preview',
            'gemini3propreview': 'gemini-3-pro-preview',
            'gemini': 'gemini-3-pro-preview',
            'claude-opus-4-5': 'claude-opus-4-5',
            'claudeopus45': 'claude-opus-4-5',
            'claude': 'claude-opus-4-5',
        }}


        def _normalize_key(s):
            return ''.join(ch for ch in str(s).lower() if ch.isalnum())


        def canonicalize_model(model_value):
            if model_value is None:
                return None
            key = _normalize_key(model_value)
            return MODEL_CANONICAL_MAP.get(key, str(model_value))


        def infer_model_from_filename(path: Path):
            name = path.name.lower()
            if 'claude' in name:
                return 'claude-opus-4-5'
            if 'gemini' in name:
                return 'gemini-3-pro-preview'
            if 'gpt' in name:
                return 'gpt-5.2'
            return None


        def _extract_ideas_from_json_obj(obj):
            if isinstance(obj, list):
                return obj
            if isinstance(obj, dict):
                for k in ['research_ideas', 'ideas', 'records', 'data']:
                    if k in obj and isinstance(obj[k], list):
                        return obj[k]
                if any(k in obj for k in ['title', 'abstract']):
                    return [obj]
            return []


        def load_persona_cards():
            if not PERSONA_CARDS_PATH.exists():
                raise FileNotFoundError(
                    f'Persona cards not found: {{PERSONA_CARDS_PATH}}. '
                    'Run src/build_persona_cards.py first.'
                )
            with open(PERSONA_CARDS_PATH, 'r') as f:
                payload = json.load(f)
            cards = payload.get('cards', []) if isinstance(payload, dict) else payload
            if not cards:
                raise RuntimeError(f'No persona cards found in {{PERSONA_CARDS_PATH}}')
            return cards


        def persona_prompt_payload(card):
            return {{
                'team_id': card.get('team_id'),
                'cohort': card.get('cohort'),
                'team_members': card.get('team_members', []),
                'team_member_profiles': card.get('team_member_profiles', []),
                'missing_from_corpus': card.get('missing_from_corpus', []),
            }}


        def persona_author_label(card):
            proposal_id = card.get('human_proposal_id')
            cohort = card.get('cohort', '')
            if proposal_id is not None and cohort:
                return f'persona-{{cohort}}-{{proposal_id}}'
            return card.get('team_id', 'persona-team')


        def parse_generated_ideas_response(response_text):
            response_text = response_text.strip()
            start_idx = response_text.find('{{')
            end_idx = response_text.rfind('}}') + 1

            if start_idx == -1 or end_idx <= start_idx:
                return []

            try:
                payload = json.loads(response_text[start_idx:end_idx])
            except json.JSONDecodeError:
                return []

            return _extract_ideas_from_json_obj(payload)


        def _load_records_from_file(path: Path):
            suffix = path.suffix.lower()
            if suffix == '.csv':
                return pd.read_csv(path).to_dict('records')
            if suffix in ('.xlsx', '.xls'):
                return pd.read_excel(path).to_dict('records')
            if suffix == '.json':
                with open(path, 'r') as f:
                    obj = json.load(f)
                return _extract_ideas_from_json_obj(obj)
            return []


        def _pick_value(rec, candidates):
            for c in candidates:
                if c in rec and pd.notna(rec[c]):
                    val = rec[c]
                    if str(val).strip() != '':
                        return val

            norm = {{_normalize_key(k): k for k in rec.keys()}}
            for c in candidates:
                ck = _normalize_key(c)
                if ck in norm:
                    v = rec[norm[ck]]
                    if pd.notna(v) and str(v).strip() != '':
                        return v
            return None


        def normalize_idea_records(records, source_file: Path):
            out = []
            model_from_file = infer_model_from_filename(source_file)
            for rec in records:
                if not isinstance(rec, dict):
                    continue

                title = _pick_value(rec, ['title', 'idea_title', 'proposal_title', 'research_title'])
                abstract = _pick_value(rec, ['abstract', 'summary', 'description'])
                author = _pick_value(rec, ['author', 'persona_author', 'scientist_author', 'author_name', 'target_author'])
                model_raw = _pick_value(rec, ['model', 'llm_model', 'generator_model', 'ai_model'])

                model = canonicalize_model(model_raw) if model_raw is not None else model_from_file
                if model is None:
                    model = ''

                if title is None or abstract is None:
                    continue

                normalized = {{
                    'model': model,
                    'author': author if author is not None else model,
                    'title': str(title).strip(),
                    'abstract': str(abstract).strip(),
                    'generated_at': _pick_value(rec, ['generated_at', 'created_at', 'timestamp']),
                    'source_file': source_file.name,
                }}

                for key, value in rec.items():
                    if key not in normalized:
                        normalized[key] = value

                out.append(normalized)
            return out


        def get_condition_idea_files():
            if IDEAS_FILE_OVERRIDE:
                file_path = Path(IDEAS_FILE_OVERRIDE)
                if not file_path.exists():
                    raise FileNotFoundError(f'IDEAS_FILE_OVERRIDE not found: {{file_path}}')
                return [file_path]

            if not ideas_input_dir.exists():
                raise FileNotFoundError(f'Condition folder not found: {{ideas_input_dir}}')

            if IDEAS_GLOB:
                files = sorted(ideas_input_dir.glob(IDEAS_GLOB))
            else:
                files = [
                    f for f in sorted(ideas_input_dir.iterdir())
                    if f.suffix.lower() in ('.csv', '.json', '.xlsx', '.xls')
                    and not f.name.startswith('ai_proposals_')
                ]

            if not files:
                raise FileNotFoundError(
                    f'No idea files found in {{ideas_input_dir}}. '
                    'Either enable GENERATE_NEW_IDEAS or place idea files in the condition folder.'
                )
            return files


        def load_ideas_for_condition():
            all_rows = []
            for file_path in get_condition_idea_files():
                records = _load_records_from_file(file_path)
                rows = normalize_idea_records(records, file_path)
                logger.info(f"Loaded {{len(rows)}} idea rows from {{file_path.name}}")
                all_rows.extend(rows)

            if not all_rows:
                raise RuntimeError(f'No usable idea rows found for condition {{CONDITION}}')

            return pd.DataFrame(all_rows)
    """)
    _set_cell_source(rendered, idx, source)

    prompt_idx = _find_code_cell_index(rendered, ['# Initialize prompt manager', 'ideas_prompt_template = prompt_manager.get_template'])
    prompt_source = dedent("""\
        # Initialize prompt manager
        prompt_manager = PromptManager()
        ideas_prompt_template = prompt_manager.get_template(IDEA_PROMPT_TEMPLATE)

        if GENERATE_NEW_IDEAS:
            if IS_PERSONA_CONDITION:
                persona_cards = load_persona_cards()
                print('✓ Persona idea prompt template prepared')
                print(f'✓ Loaded {len(persona_cards)} persona cards from: {PERSONA_CARDS_PATH}')
                print(f'✓ Configured to generate 1 idea per persona card per model')
            else:
                ideas_prompt = ideas_prompt_template.template.format(
                    research_call=research_call,
                    information_about_ncems=ncems_info,
                    num=NUM_IDEAS_PER_MODEL,
                )
                print('✓ Idea prompt template prepared')
                print(f'✓ Configured to generate {NUM_IDEAS_PER_MODEL} ideas per model')
                print(f'\\nPrompt preview (first 500 chars):\\n{ideas_prompt[:500]}...')
        else:
            print('Skipping idea generation prompt setup (GENERATE_NEW_IDEAS=False).')
    """)
    _set_cell_source(rendered, prompt_idx, prompt_source)

    generate_idx = _find_code_cell_index(rendered, ['# Generate ideas from each model', 'all_ideas = []'])
    generate_source = dedent("""\
        if GENERATE_NEW_IDEAS:
            all_ideas = []

            if IS_PERSONA_CONDITION:
                for model_name in models_to_use:
                    logger.info(f"\\n{'='*60}")
                    logger.info(f"Generating persona-conditioned ideas using {model_name}...")
                    logger.info(f"{'='*60}")

                    for card_idx, card in enumerate(persona_cards, start=1):
                        team_members = card.get('team_members', [])
                        team_members_text = ', '.join(team_members)
                        persona_payload = persona_prompt_payload(card)
                        prompt = ideas_prompt_template.template.format(
                            research_call=research_call,
                            information_about_ncems=ncems_info,
                            team_members=team_members_text,
                            persona_card_json=json.dumps(persona_payload, indent=2, ensure_ascii=False),
                            num=1,
                        )

                        logger.info(
                            f"[{card_idx}/{len(persona_cards)}] {model_name} persona team "
                            f"{card.get('team_id', 'unknown')}: {card.get('human_proposal_title', '')[:80]}"
                        )

                        try:
                            response = ai_interface.generate_content(
                                prompt=prompt,
                                model_name=model_name,
                                temperature=GENERATION_TEMPERATURE,
                                max_completion_tokens=16000,
                            )
                            research_ideas = parse_generated_ideas_response(response)
                            if not research_ideas:
                                logger.error(
                                    f"No valid research ideas found for {model_name} / "
                                    f"{card.get('team_id', 'unknown')}"
                                )
                                continue

                            for idea in research_ideas[:1]:
                                idea['model'] = model_name
                                idea['author'] = persona_author_label(card)
                                idea['generated_at'] = datetime.now().isoformat()
                                idea['generation_temperature'] = GENERATION_TEMPERATURE
                                idea['persona_team_id'] = card.get('team_id')
                                idea['persona_team_authors'] = '; '.join(team_members)
                                idea['source_human_proposal_id'] = card.get('human_proposal_id')
                                idea['source_human_proposal_title'] = card.get('human_proposal_title')
                                idea['cohort'] = card.get('cohort')
                                all_ideas.append(idea)
                        except Exception as e:
                            logger.error(
                                f"Error generating persona-conditioned idea with {model_name} "
                                f"for {card.get('team_id', 'unknown')}: {e}"
                            )
            else:
                for model_name in models_to_use:
                    logger.info(f"\\n{'='*60}")
                    logger.info(f"Generating {NUM_IDEAS_PER_MODEL} research ideas using {model_name}...")
                    logger.info(f"{'='*60}")

                    try:
                        response = ai_interface.generate_content(
                            prompt=ideas_prompt,
                            model_name=model_name,
                            temperature=GENERATION_TEMPERATURE,
                            max_completion_tokens=16000,
                        )
                        research_ideas = parse_generated_ideas_response(response)
                        if not research_ideas:
                            logger.error(f"No valid research ideas found for {model_name}")
                            continue

                        logger.info(f"✓ Generated {len(research_ideas)} ideas from {model_name}")
                        for idea in research_ideas:
                            idea['model'] = model_name
                            idea['author'] = model_name
                            idea['generated_at'] = datetime.now().isoformat()
                            idea['generation_temperature'] = GENERATION_TEMPERATURE
                            all_ideas.append(idea)
                    except Exception as e:
                        logger.error(f"Error generating ideas with {model_name}: {e}")

            print(f"\\n{'='*60}")
            print(f"✓ Total ideas generated: {len(all_ideas)}")
            print(f"{'='*60}")
        else:
            ideas_df = load_ideas_for_condition()
    """)
    _set_cell_source(rendered, generate_idx, generate_source)
    proposal_idx = _find_code_cell_index(rendered, ['progress_files = sorted(output_dir.glob', 'for idx, row in ideas_df.iterrows():'])
    proposal_source = dedent("""\
        section_cols = [
            'background_and_significance',
            'research_questions_and_hypotheses',
            'methods_and_approach',
            'expected_outcomes_and_impact',
            'open_science_and_reproducibility',
            'budget_and_resources',
        ]

        complete_files = sorted(output_dir.glob(f'ai_proposals_{condition_slug}_complete_*.csv'))
        progress_files = sorted(output_dir.glob(f'ai_proposals_{condition_slug}_progress_*.csv'))
        skip_proposal_generation = False

        if complete_files and SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS:
            latest_complete = complete_files[-1]
            ideas_df = pd.read_csv(latest_complete)
            skip_proposal_generation = True
            print(f"Found complete proposal file: {latest_complete.name}")
            print("SKIP_PROPOSAL_GENERATION_IF_COMPLETE_EXISTS=True, so proposal generation will be skipped.")
        elif progress_files:
            latest = progress_files[-1]
            ideas_df = pd.read_csv(latest)
            print(f"Loaded progress file: {latest.name}  ({len(ideas_df)} rows)")
        elif 'ideas_df' not in globals():
            raise RuntimeError(
                'No progress files found and ideas_df is not defined. '
                'Run earlier cells to prepare ideas_df first.'
            )
        else:
            print(f"No progress file found — using ideas_df from memory ({len(ideas_df)} rows).")

        for col in section_cols:
            if col not in ideas_df.columns:
                ideas_df[col] = ''
        if 'proposal_generated_at' not in ideas_df.columns:
            ideas_df['proposal_generated_at'] = ''


        def _is_complete(row):
            model_val = row.get('model', '')
            if pd.isna(model_val) or str(model_val).strip() == '':
                return True  # skip malformed rows
            for c in section_cols:
                val = row.get(c, '')
                if pd.isna(val) or str(val).strip() == '':
                    return False
            return True

        already_done = sum(_is_complete(r) for _, r in ideas_df.iterrows())
        print(f"Proposals already complete : {already_done} / {len(ideas_df)}")
        print(f"Remaining to generate      : {len(ideas_df) - already_done}\\n")

        if not skip_proposal_generation:
            for idx, row in ideas_df.iterrows():
                if _is_complete(row):
                    logger.info(f"Skipping {idx+1}/{len(ideas_df)} — already complete: {str(row.get('title',''))[:60]}")
                    continue

                model_name = canonicalize_model(row.get('model', ''))
                title = str(row.get('title', '')).strip()
                abstract = str(row.get('abstract', '')).strip()
                author = str(row.get('author', row.get('model', '')))

                if not model_name or model_name not in available_models:
                    logger.error(f"Skipping row {idx}: unavailable model '{model_name}'.")
                    continue

                logger.info(f"\\n{'='*60}")
                logger.info(f"Generating proposal {idx+1}/{len(ideas_df)} using {model_name}")
                logger.info(f"Author label: {author}")
                logger.info(f"Title: {title[:100]}...")
                logger.info(f"{'='*60}")

                try:
                    proposal_prompt = proposals_template.template.format(
                        research_call=research_call,
                        information_about_ncems=ncems_info,
                        title=title,
                        abstract=abstract,
                    )

                    response = ai_interface.generate_content(
                        prompt=proposal_prompt,
                        model_name=model_name,
                        temperature=GENERATION_TEMPERATURE,
                        max_completion_tokens=16000,
                    )

                    try:
                        response_text = response.strip()
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}') + 1

                        if start_idx != -1 and end_idx > start_idx:
                            json_str = response_text[start_idx:end_idx]
                            proposal_data = json.loads(json_str)
                            proposal = proposal_data['proposal'] if 'proposal' in proposal_data else proposal_data

                            ideas_df.at[idx, 'background_and_significance'] = proposal.get('background_and_significance', '')
                            ideas_df.at[idx, 'research_questions_and_hypotheses'] = proposal.get('research_questions_and_hypotheses', '')
                            ideas_df.at[idx, 'methods_and_approach'] = proposal.get('methods_and_approach', '')
                            ideas_df.at[idx, 'expected_outcomes_and_impact'] = proposal.get('expected_outcomes_and_impact', '')
                            ideas_df.at[idx, 'open_science_and_reproducibility'] = proposal.get('open_science_and_reproducibility', '')
                            ideas_df.at[idx, 'budget_and_resources'] = proposal.get('budget_and_resources', '')
                            ideas_df.at[idx, 'proposal_generated_at'] = datetime.now().isoformat()
                            ideas_df.at[idx, 'generation_temperature'] = GENERATION_TEMPERATURE

                            progress_file = output_dir / f'ai_proposals_{condition_slug}_progress_{timestamp}.csv'
                            ideas_df.to_csv(progress_file, index=False)

                            logger.info(f"✓ Successfully generated proposal for: {title[:60]}...")
                        else:
                            logger.error(f"Could not extract JSON from response for row {idx}")
                    except Exception as parse_error:
                        logger.error(f"Error parsing proposal JSON for row {idx}: {parse_error}")
                except Exception as e:
                    logger.error(f"Error generating proposal for row {idx}: {e}")
        else:
            print("Skipping proposal generation because a complete proposal file already exists for this condition.")
    """)
    _set_cell_source(rendered, proposal_idx, proposal_source)
    rendered['cells'].append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '## Rephrase Proposals\n',
            '\n',
            'Run the standardized rephrasing step for the current condition so the next notebook can use the rephrased AI and human proposal files.'
        ],
    })
    rendered['cells'].append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': dedent("""\
            import subprocess
            import sys

            complete_files = sorted(output_dir.glob(f'ai_proposals_{condition_slug}_complete_*.csv'))
            if not complete_files:
                raise FileNotFoundError(
                    f'No complete proposal CSV found in {output_dir}. '
                    'Run the proposal-generation cells above first.'
                )

            latest_complete = complete_files[-1]
            print(f'Using latest complete proposal file: {latest_complete}')

            if RUN_REPHRASE_AT_END:
                subprocess.check_call(
                    [sys.executable, str(REPHRASE_SCRIPT_PATH), '--condition', CONDITION],
                    cwd=PROJECT_ROOT,
                )
            else:
                print('RUN_REPHRASE_AT_END=False, so the rephrasing script was not executed.')

            ai_rephrased_dir = PROJECT_ROOT / 'data' / 'ai-proposals' / 'rephrased' / CONDITION
            human_rephrased_dir = PROJECT_ROOT / 'data' / 'human-proposals' / 'rephrased' / CONDITION
            print(f'✓ Rephrased AI proposals available in: {ai_rephrased_dir}')
            print(f'✓ Rephrased human proposals available in: {human_rephrased_dir}')
        """).splitlines(keepends=True),
    })
    return rendered


def _render_compare_proposals_rephrased(notebook: Dict[str, Any],
                                        condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                'Run this notebook after the rephrasing section in `gen_proposals.ipynb`.\n',
                '\n',
                '- `CONDITION`: condition name whose rephrased proposal files should be analyzed.\n',
                '- `REUSE_CACHED_PROPOSAL_EMBEDDINGS`: load proposal embeddings if they already exist.\n',
                '- `REUSE_CACHED_MAIN_IDEA_EMBEDDINGS`: load main-idea embeddings if they already exist.\n',
                '- `REUSE_CACHED_LITERATURE_EMBEDDINGS`: load literature embeddings if they already exist.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
                REUSE_CACHED_PROPOSAL_EMBEDDINGS = True
                REUSE_CACHED_MAIN_IDEA_EMBEDDINGS = True
                REUSE_CACHED_LITERATURE_EMBEDDINGS = True
            """).splitlines(keepends=True),
        },
    ])

    setup_idx = _find_code_cell_index(rendered, ['PROPOSAL_EMBEDDINGS_FILE', "condition = 'rephrased/minimal'"])

    setup_existing = ''.join(rendered['cells'][setup_idx].get('source', []))
    if 'PREPARED_ALL_PROPOSALS_PATH' in setup_existing:
        setup_source = setup_existing.replace(
            "condition = 'rephrased/minimal'",
            f"condition = 'rephrased/{condition.name}'",
        )
        setup_source = setup_source.replace(
            "AI_PROPOSALS_PATH = PROJECT_ROOT / 'data' / 'ai-proposals' / condition",
            "AI_PROPOSALS_PATH = PROJECT_ROOT / 'data' / 'ai-proposals' / condition",
        )
        _set_cell_source(rendered, setup_idx, setup_source)

        try:
            export_idx = _find_code_cell_index(rendered, ["_AI_BASE / 'minimal'", 'all_proposals.json'])
            export_source = ''.join(rendered['cells'][export_idx].get('source', []))
            export_source = export_source.replace(
                "_orig_ai = pd.read_csv(sorted((_AI_BASE / 'minimal').glob('ai_proposals_minimal_complete_*.csv'))[-1])",
                (
                    f"_orig_ai = pd.read_csv(sorted((_AI_BASE / '{condition.name}').glob("
                    f"'ai_proposals_{condition.name}_complete_*.csv'))[-1])"
                ),
            )
            _set_cell_source(rendered, export_idx, export_source)
        except NotebookTemplateError:
            pass
        return rendered

    setup_source = dedent(f"""\
        import sys
        import os
        import json
        import numpy as np
        import pandas as pd
        from pathlib import Path
        import pickle
        from datetime import datetime
        import warnings
        warnings.filterwarnings('ignore')

        # Plotting
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # NLP and embeddings
        from transformers import AutoTokenizer, AutoModel
        import torch
        from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
        from scipy.spatial.distance import cdist
        from tqdm import tqdm

        # Statistics
        from scipy import stats
        from scipy.stats import mannwhitneyu
        import itertools

        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11

        def find_project_root():
            candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
            for candidate in candidates:
                if (candidate / 'src').exists() and (candidate / 'data').exists():
                    return candidate.resolve()
            raise RuntimeError('Could not find project root containing src/ and data/.')

        PROJECT_ROOT = find_project_root()

        print("✓ Imports successful")
        print(f"✓ Working directory: {{os.getcwd()}}")
        print(f"✓ Project root: {{PROJECT_ROOT}}")
        print(f"✓ PyTorch version: {{torch.__version__}}")
        print(f"✓ CUDA available: {{torch.cuda.is_available()}}")

        try:
            import umap
        except ImportError:
            import subprocess
            subprocess.check_call(['pip', 'install', 'umap-learn'])
            import umap

        CONDITION_NAME = CONDITION
        condition = f'rephrased/{{CONDITION_NAME}}'
        AI_REPHRASED_GLOB = f'ai_proposals_{{CONDITION_NAME}}_rephrased_*.csv'
        AI_ORIGINAL_GLOB = f'ai_proposals_{{CONDITION_NAME}}_complete_*.csv'

        AI_PROPOSALS_PATH = PROJECT_ROOT / 'data' / 'ai-proposals' / condition
        HUMAN_PROPOSALS_PATH = PROJECT_ROOT / 'data' / 'human-proposals' / condition
        RESULTS_DIR = PROJECT_ROOT / 'results'
        FIGURES_DIR = RESULTS_DIR / 'figures' / condition
        TABLES_DIR = RESULTS_DIR / 'tables' / condition
        PROPOSAL_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / condition / 'proposal_embeddings_human_ai_rephrased.pkl'
        ABSTRACT_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / condition / 'proposal_embeddings_section1_only.pkl'
        MAIN_IDEA_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / condition / 'proposal_embeddings_main_idea_only.pkl'
        LITERATURE_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / 'literature' / 'relevant_literature_embeddings.pkl'
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        PROPOSAL_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ABSTRACT_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LITERATURE_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        MAIN_IDEA_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    """)
    _set_cell_source(rendered, setup_idx, setup_source)

    load_idx = _find_code_cell_index(rendered, ['# Load AI proposals', 'ai_proposals_minimal_rephrased_*.csv'])
    load_source = dedent("""\
        # Load AI proposals
        ai_files = sorted(AI_PROPOSALS_PATH.glob(AI_REPHRASED_GLOB))
        if not ai_files:
            ai_files = sorted(AI_PROPOSALS_PATH.glob('ai_proposals_*_rephrased_*.csv'))

        if not ai_files:
            raise FileNotFoundError("No rephrased AI proposal files found. Run the final rephrasing section in gen_proposals.ipynb first.")

        ai_df = pd.read_csv(ai_files[-1])
        print(f"✓ Loaded AI proposals from: {ai_files[-1].name}")
        print(f"  Shape: {ai_df.shape}")
        print(f"  Models: {ai_df['model'].value_counts().to_dict()}")

        human_files = list(HUMAN_PROPOSALS_PATH.glob('*.json'))
        human_proposals = []
        for file in human_files:
            with open(file, 'r') as f:
                data = json.load(f)

                if isinstance(data, list):
                    for proposal in data:
                        proposal['source_file'] = file.name
                        human_proposals.append(proposal)
                elif 'proposals' in data:
                    for proposal in data['proposals']:
                        proposal['source_file'] = file.name
                        human_proposals.append(proposal)
                else:
                    data['source_file'] = file.name
                    human_proposals.append(data)

        human_df = pd.DataFrame(human_proposals)
        print(f"\\n✓ Loaded human proposals from {len(human_files)} files")
        print(f"  Total proposals: {len(human_df)}")
        print(f"  Source files: {human_df['source_file'].unique().tolist()}")
    """)
    _set_cell_source(rendered, load_idx, load_source)

    emb_idx = _find_code_cell_index(rendered, ['embeddings_file = PROPOSAL_EMBEDDINGS_FILE', 'legacy_embedding_files = sorted'])
    emb_source = dedent("""\
        # Generate embeddings (or load an existing cache if already saved)
        embeddings_file = PROPOSAL_EMBEDDINGS_FILE
        legacy_embedding_files = sorted(embeddings_file.parent.glob('proposal_embeddings_[0-9]*.pkl'))
        rephrased_embeddings_were_generated = False

        if REUSE_CACHED_PROPOSAL_EMBEDDINGS:
            if embeddings_file.exists():
                embeddings_to_load = embeddings_file
            elif legacy_embedding_files:
                embeddings_to_load = legacy_embedding_files[-1]
            else:
                embeddings_to_load = None
        else:
            embeddings_to_load = None

        if embeddings_to_load is not None:
            print(f"✓ Loading cached embeddings from: {embeddings_to_load}")
            embeddings_data = retrieve_embeddings(str(embeddings_to_load))
            ai_embeddings = embeddings_data['ai_embeddings']
            human_embeddings = embeddings_data['human_embeddings']
            ai_metadata = embeddings_data.get('ai_metadata', ai_df[['model', 'title', 'group']].to_dict('records'))
            human_metadata = embeddings_data.get('human_metadata', human_df[['proposal_title', 'group', 'source_file']].to_dict('records'))
            print(f"  AI:    {ai_embeddings.shape}")
            print(f"  Human: {human_embeddings.shape}")

            if embeddings_to_load != embeddings_file:
                canonical_payload = {
                    'ai_embeddings': ai_embeddings,
                    'human_embeddings': human_embeddings,
                    'ai_metadata': ai_metadata,
                    'human_metadata': human_metadata,
                    'model_name': embeddings_data.get('model_name', model_name),
                    'timestamp': embeddings_data.get('timestamp', datetime.now().isoformat()),
                }
                with open(embeddings_file, 'wb') as f:
                    pickle.dump(canonical_payload, f)
                print(f"✓ Canonicalized embeddings cache to: {embeddings_file}")
        else:
            print("No cached proposal embeddings found or cache reuse disabled — generating now (this takes a few minutes)...")

            print("Embedding AI proposals...")
            ai_embeddings = get_embeddings(ai_df['full_text'].tolist())
            print(f"✓ AI embeddings shape: {ai_embeddings.shape}")

            print("\\nEmbedding human proposals...")
            human_embeddings = get_embeddings(human_df['full_text'].tolist())
            print(f"✓ Human embeddings shape: {human_embeddings.shape}")

            ai_metadata = ai_df[['model', 'title', 'group']].to_dict('records')
            human_metadata = human_df[['proposal_title', 'group', 'source_file']].to_dict('records')
            rephrased_embeddings_were_generated = True

            embeddings_data = {
                'ai_embeddings': ai_embeddings,
                'human_embeddings': human_embeddings,
                'ai_metadata': ai_metadata,
                'human_metadata': human_metadata,
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
            }

            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings_data, f)
            print(f"✓ Saved proposal embeddings to: {embeddings_file}")
    """)
    _set_cell_source(rendered, emb_idx, emb_source)

    mi_idx = _find_code_cell_index(rendered, ['MI_EMBEDDINGS_FILE', "'main_idea' column missing"])
    mi_source = dedent("""\
        # ── Load main_idea texts and define embedding cache path ────────────────────
        MI_EMBEDDINGS_FILE = MAIN_IDEA_EMBEDDINGS_FILE
        MI_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        for _df_name, _df in [('ai_df', ai_df), ('human_df', human_df)]:
            if 'main_idea' not in _df.columns:
                raise RuntimeError(
                    f"'main_idea' column missing from {_df_name}. "
                    "Re-run the final rephrasing section in gen_proposals.ipynb to regenerate the rephrased files."
                )

        mi_ai_texts = ai_df['main_idea'].fillna('').astype(str).tolist()
        mi_human_texts = human_df['main_idea'].fillna('').astype(str).tolist()

        print(f'AI main ideas:    {len(mi_ai_texts)}')
        print(f'Human main ideas: {len(mi_human_texts)}')
        print()
        print('── Sample AI main idea ──')
        print(mi_ai_texts[0][:500])
        print()
        print('── Sample Human main idea ──')
        print(mi_human_texts[0][:500])
    """)
    _set_cell_source(rendered, mi_idx, mi_source)

    mi_embed_idx = _find_code_cell_index(rendered, ['if MI_EMBEDDINGS_FILE.exists():', "print('No cache found — embedding main ideas now"])
    mi_embed_source = dedent("""\
        # ── Embed main ideas (or load cached embeddings) ────────────────────────────
        if REUSE_CACHED_MAIN_IDEA_EMBEDDINGS and MI_EMBEDDINGS_FILE.exists():
            print(f'Loading cached main-idea embeddings: {MI_EMBEDDINGS_FILE.name}')
            _mi_cache    = retrieve_embeddings(str(MI_EMBEDDINGS_FILE))
            mi_ai_emb    = _mi_cache['ai_embeddings']
            mi_human_emb = _mi_cache['human_embeddings']
            print(f'  AI:    {mi_ai_emb.shape}')
            print(f'  Human: {mi_human_emb.shape}')
        else:
            print('No main-idea cache found or cache reuse disabled — embedding main ideas now...')
            if 'get_embeddings' not in globals():
                raise RuntimeError('get_embeddings() not defined. Run the BioLinkBERT loading cells first.')
            print('Embedding AI main ideas...')
            mi_ai_emb = get_embeddings(mi_ai_texts)
            print(f'✓ AI shape: {mi_ai_emb.shape}')
            print('Embedding human main ideas...')
            mi_human_emb = get_embeddings(mi_human_texts)
            print(f'✓ Human shape: {mi_human_emb.shape}')
            with open(MI_EMBEDDINGS_FILE, 'wb') as _f:
                pickle.dump({
                    'ai_embeddings':    mi_ai_emb,
                    'human_embeddings': mi_human_emb,
                    'model_name':       model_name if 'model_name' in globals() else 'BioLinkBERT-large',
                    'timestamp':        datetime.now().isoformat(),
                }, _f)
            print(f'✓ Saved to {MI_EMBEDDINGS_FILE}  ({MI_EMBEDDINGS_FILE.stat().st_size/1024/1024:.2f} MB)')

        # Per-model embedding slices (aligned to ai_df row order)
        mi_model_emb_dict = {}
        for _m in ai_models:
            _mask = (ai_df['model'] == _m).values
            mi_model_emb_dict[_m] = mi_ai_emb[_mask]

        print()
        print('Per-model main-idea embedding shapes:')
        for _m, _e in mi_model_emb_dict.items():
            print(f'  {_m}: {_e.shape}')
    """)
    _set_cell_source(rendered, mi_embed_idx, mi_embed_source)

    lit_idx = _find_code_cell_index(rendered, ['literature_embeddings_file = LITERATURE_EMBEDDINGS_FILE', 'Embedding literature corpus'])
    lit_source = dedent("""\
        # Embed literature corpus using the same approach (truncated to 512 tokens)
        print("="*85)
        print("EMBEDDING LITERATURE CORPUS")
        print("="*85)
        print("Using BioLinkBERT-Large (same as proposals, truncated to 512 tokens)")
        print()

        literature_embeddings_file = LITERATURE_EMBEDDINGS_FILE

        if REUSE_CACHED_LITERATURE_EMBEDDINGS and literature_embeddings_file.exists():
            print(f"✓ Loading cached literature embeddings from {literature_embeddings_file}")
            with open(literature_embeddings_file, 'rb') as f:
                literature_data = pickle.load(f)
                literature_embeddings = literature_data['embeddings']
            print(f"✓ Loaded {len(literature_embeddings)} embeddings")
        else:
            print("Embedding literature corpus (this will take a few minutes)...")
            literature_embeddings = get_embeddings(corpus_texts)
            print(f"✓ Literature embeddings shape: {literature_embeddings.shape}")

            literature_embeddings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(literature_embeddings_file, 'wb') as f:
                pickle.dump({
                    'embeddings': literature_embeddings,
                    'model_name': model_name,
                    'timestamp': datetime.now().isoformat()
                }, f)
            print(f"✓ Cached embeddings to: {literature_embeddings_file}")

        print("="*85)
    """)
    _set_cell_source(rendered, lit_idx, lit_source)

    export_idx = _find_code_cell_index(rendered, ["_AI_BASE / 'minimal'", 'all_proposals.json'])
    export_source = dedent("""\
        import json as _json
        import pandas as pd
        import numpy as np
        from pathlib import Path

        def _norm(s): return str(s).strip().lower()

        def _load(fname):
            df = pd.read_csv(TABLES_DIR / fname)
            df['_key'] = df['title'].map(_norm)
            return df

        def _load_optional(fname):
            p = TABLES_DIR / fname
            if p.exists():
                df = pd.read_csv(p)
                if 'title' in df.columns:
                    df['_key'] = df['title'].map(_norm)
                return df
            return None

        cent_df = _load('centroid_distances.csv')
        nn_df = _load('nn_distances.csv')
        nov_df = _load('novelty_scores_from_literature.csv')
        style_metrics_df = _load('style_features.csv')
        scores_df = _load_optional('review_scores_wide.csv')

        lit_out_df = _load_optional('literature_space_outliers_mean_knn_k10.csv')
        if lit_out_df is None:
            lit_out_df = _load_optional('literature_space_outliers_mean_knn_k5.csv')

        score_cols = [] if scores_df is None else [c for c in scores_df.columns if c not in {'title', 'author', '_key'}]

        def _to_dict(df, cols):
            return {row['_key']: {c: row[c] for c in cols} for _, row in df.iterrows()}

        cent_lut = _to_dict(cent_df, ['centroid_dist'])
        nn_lut = _to_dict(nn_df, ['nn_dist', 'is_outlier', 'threshold'])
        nov_lut = _to_dict(
            nov_df,
            ['raw_novelty', 'novelty_z', 'novelty_ratio',
             'is_most_novel_raw', 'is_most_novel_z', 'is_most_novel_ratio'],
        )
        style_feat_cols = [c for c in style_metrics_df.columns if c not in {'title', 'group', 'is_ai', '_key'}]
        style_lut = _to_dict(style_metrics_df, style_feat_cols)
        scores_lut = {} if scores_df is None else _to_dict(scores_df, score_cols)

        lit_out_lut = {}
        _lit_dist_col = None
        if lit_out_df is not None and len(lit_out_df):
            for cand in [c for c in lit_out_df.columns if c.startswith('mean_lit_nn_dist_k')]:
                _lit_dist_col = cand
                break
            if '_key' not in lit_out_df.columns and 'title' in lit_out_df.columns:
                lit_out_df['_key'] = lit_out_df['title'].map(_norm)

            if _lit_dist_col is not None and 'is_outlier_literature_space' in lit_out_df.columns:
                for _, row in lit_out_df.iterrows():
                    key = row.get('_key')
                    if key is None:
                        continue
                    raw_flag = row.get('is_outlier_literature_space', 0)
                    flag = 0 if pd.isna(raw_flag) else int(bool(raw_flag))
                    lit_out_lut[key] = {
                        'is_literature_outlier': flag,
                        _lit_dist_col: row.get(_lit_dist_col),
                        'threshold_literature_space': row.get('threshold_literature_space', None),
                    }

        if not lit_out_lut and all(v in globals() for v in ['titles_ls', 'lit_space_outliers_mknn']):
            _dist = globals().get('mean_lit_knn_dist', None)
            _thr = globals().get('lit_mknn_threshold', None)
            for i, t in enumerate(titles_ls):
                key = _norm(t)
                flag = int(bool(lit_space_outliers_mknn[i]))
                rec = {'is_literature_outlier': flag, 'threshold_literature_space': _thr}
                if _dist is not None:
                    rec[f"mean_lit_nn_dist_k{globals().get('k_lit_out', 10)}"] = _dist[i]
                lit_out_lut[key] = rec

        _pairwise_map, _mi_cd_map, _mi_nn_map, _mi_pm_map = {}, {}, {}, {}
        if 'human_pairwise_proposal_means' in globals() and 'human_df' in globals():
            for _i, (_, _r) in enumerate(human_df.iterrows()):
                _t = _norm(_r.get('proposal_title', _r.get('title', '')))
                _pairwise_map[_t] = float(human_pairwise_proposal_means[_i])
        if 'ai_pairwise_proposal_means' in globals() and 'ai_df' in globals():
            for _i, (_, _r) in enumerate(ai_df.iterrows()):
                _t = _norm(_r.get('title', _r.get('proposal_title', '')))
                _pairwise_map[_t] = float(ai_pairwise_proposal_means[_i])
        if 'mi_human_cd' in globals() and 'human_df' in globals():
            for _i, (_, _r) in enumerate(human_df.iterrows()):
                _t = _norm(_r.get('proposal_title', _r.get('title', '')))
                _mi_cd_map[_t] = float(mi_human_cd[_i])
                if 'mi_human_nn' in globals():
                    _mi_nn_map[_t] = float(mi_human_nn[_i])
                if 'mi_human_pm' in globals():
                    _mi_pm_map[_t] = float(mi_human_pm[_i])
        if 'mi_ai_cd' in globals() and 'ai_df' in globals():
            for _i, (_, _r) in enumerate(ai_df.iterrows()):
                _t = _norm(_r.get('title', _r.get('proposal_title', '')))
                _mi_cd_map[_t] = float(mi_ai_cd[_i])
                if 'mi_ai_nn' in globals():
                    _mi_nn_map[_t] = float(mi_ai_nn[_i])
                if 'mi_ai_pm' in globals():
                    _mi_pm_map[_t] = float(mi_ai_pm[_i])

        def _get_metrics(key):
            m = {}
            m.update(cent_lut.get(key, {'centroid_dist': None}))
            m.update(nn_lut.get(key, {'nn_dist': None, 'is_outlier': None, 'threshold': None}))
            m.update(
                nov_lut.get(
                    key,
                    {c: None for c in ['raw_novelty', 'novelty_z', 'novelty_ratio',
                                       'is_most_novel_raw', 'is_most_novel_z', 'is_most_novel_ratio']},
                )
            )
            m.update(style_lut.get(key, {c: None for c in style_feat_cols}))
            m.update({'is_literature_outlier': 0, 'threshold_literature_space': None})
            m.update(lit_out_lut.get(key, {}))

            review = scores_lut.get(key, {c: None for c in score_cols})
            review['review_score_mean'] = (
                np.nanmean([v for v in review.values() if v is not None])
                if any(v is not None for v in review.values()) else None
            )
            m.update(review)

            m['pairwise_mean_dist'] = _pairwise_map.get(key)
            m['mi_centroid_dist'] = _mi_cd_map.get(key)
            m['mi_nn_dist'] = _mi_nn_map.get(key)
            m['mi_pairwise_mean_dist'] = _mi_pm_map.get(key)

            raw_lit_flag = m.get('is_literature_outlier', 0)
            if pd.isna(raw_lit_flag):
                raw_lit_flag = 0
            m['is_literature_outlier'] = int(bool(raw_lit_flag))
            return {k: (v.item() if hasattr(v, 'item') else v) for k, v in m.items()}

        _AI_BASE = AI_PROPOSALS_PATH.parent.parent
        _orig_ai = pd.read_csv(sorted((_AI_BASE / CONDITION_NAME).glob(AI_ORIGINAL_GLOB))[-1])
        _rep_ai = pd.read_csv(sorted(AI_PROPOSALS_PATH.glob('ai_proposals_*.csv'))[-1])
        _rep_ai_lut = {_norm(r['title']): r for _, r in _rep_ai.iterrows()}

        _AI_ORIG_SECTIONS = [
            'abstract',
            'background_and_significance',
            'research_questions_and_hypotheses',
            'methods_and_approach',
            'expected_outcomes_and_impact',
            'budget_and_resources',
        ]

        records = []
        for _, row in _orig_ai.iterrows():
            title = row['title']
            key = _norm(title)
            rep = _rep_ai_lut.get(key, {})
            rec = {
                'title': title,
                'group': row.get('model', 'AI'),
                'is_ai': True,
                'model': row.get('model'),
                'cohort': None,
                'original': {s: row.get(s) for s in _AI_ORIG_SECTIONS},
                'rephrased': {
                    'standardized_text': rep.get('standardized_text'),
                    'main_idea': rep.get('main_idea'),
                },
                'metrics': _get_metrics(key),
            }
            records.append(rec)

        _HUM_BASE = HUMAN_PROPOSALS_PATH.parent.parent

        def _load_human_cohort(cohort):
            with open(_HUM_BASE / f'human-proposals-{cohort}.json') as fh:
                orig_props = _json.load(fh)['proposals']
            rep_paths = sorted(HUMAN_PROPOSALS_PATH.glob(f'human_proposals_rephrased_{cohort}_*.json'))
            rep_lut = {}
            if rep_paths:
                with open(rep_paths[-1]) as fh:
                    for p in _json.load(fh)['proposals']:
                        t = p.get('proposal_title', p.get('title', ''))
                        rep_lut[_norm(t)] = p
            for prop in orig_props:
                title = prop.get('proposal_title', prop.get('title', ''))
                key = _norm(title)
                rep = rep_lut.get(key, {})
                rec = {
                    'title': title,
                    'group': 'Human',
                    'is_ai': False,
                    'model': None,
                    'cohort': cohort,
                    'original': {
                        'abstract': prop.get('abstract'),
                        'full_draft': prop.get('full_draft'),
                    },
                    'rephrased': {
                        'standardized_text': rep.get('standardized_text'),
                        'main_idea': rep.get('main_idea'),
                    },
                    'metrics': _get_metrics(key),
                }
                records.append(rec)

        _load_human_cohort('y1')
        _load_human_cohort('y2')

        out_path = TABLES_DIR / 'all_proposals.json'
        with open(out_path, 'w') as fh:
            _json.dump(records, fh, indent=2, default=str)

        _metric_keys = list(records[0]['metrics'].keys()) if records else []
        _filled = lambda k: sum(1 for r in records if r['metrics'].get(k) is not None)

        print(f'Saved all_proposals.json ({len(records)} proposals)')
        print(f'Path: {out_path}')
        print()
        print('Metrics coverage:')
        for k in _metric_keys:
            print(f'  {k:<35} {_filled(k):>3}/{len(records)}')

        n_lit_out = sum(int(r['metrics'].get('is_literature_outlier', 0)) for r in records)
        print()
        print(
            f"Literature-space outlier flag coverage: {len(records)}/{len(records)} "
            f"(binary), positives={n_lit_out}"
        )
    """)
    _set_cell_source(rendered, export_idx, export_source)
    return rendered


def _render_prepare_data_for_analysis(notebook: Dict[str, Any],
                                      condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                'This notebook prepares reusable data artifacts for the selected condition.\n',
                '\n',
                '- `CONDITION`: condition name under `data/ai-proposals/` and `data/ai-proposals/rephrased/`.\n',
                '- `BASE_CONDITION`: raw proposal/review condition name before adding the `rephrased/` prefix.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
                BASE_CONDITION = '{condition.name}'
            """).splitlines(keepends=True),
        },
    ])

    setup_idx = _find_code_cell_index(rendered, ["condition = 'rephrased/minimal'", "base_condition = 'minimal'"])
    setup_source = ''.join(rendered['cells'][setup_idx].get('source', []))
    setup_source = setup_source.replace(
        "condition = 'rephrased/minimal'",
        "condition = f'rephrased/{CONDITION}'",
    )
    setup_source = setup_source.replace(
        "base_condition = 'minimal'",
        "base_condition = BASE_CONDITION",
    )
    _set_cell_source(rendered, setup_idx, setup_source)
    return rendered


def _render_generate_reviews(notebook: Dict[str, Any], condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                '- `CONDITION`: condition name whose rephrased proposals should be reviewed.\n',
                '- `SKIP_NCEMS_IF_EXISTS`: reuse the latest NCEMS review JSON if it already exists.\n',
                '- `SKIP_NOVELTY_IF_EXISTS`: reuse the latest novelty review JSON if it already exists.\n',
                '- `REBUILD_REVIEW_SCORES`: rebuild `review_scores_wide.csv` from the latest NCEMS review file.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
                SKIP_NCEMS_IF_EXISTS = True
                SKIP_NOVELTY_IF_EXISTS = True
                REBUILD_REVIEW_SCORES = True
            """).splitlines(keepends=True),
        },
    ])
    idx = _find_code_cell_index(rendered, ["CONDITION = 'minimal'"])
    _set_cell_source(rendered, idx, dedent(f"""\
        # Auto-managed by src/run_condition.py
        CONDITION = '{condition.name}'
        SKIP_NCEMS_IF_EXISTS = True
        SKIP_NOVELTY_IF_EXISTS = True
        REBUILD_REVIEW_SCORES = True
    """))
    ncems_idx = _find_code_cell_index(rendered, ["str(SCRIPTS_DIR / 'generate_reviews_ncems_criteria.py')", 'latest_ncems = sorted'])
    _set_cell_source(rendered, ncems_idx, dedent("""\
        existing_ncems = sorted(NCEMS_REVIEWS_DIR.glob('ncems_reviews_*.json'))
        if existing_ncems and SKIP_NCEMS_IF_EXISTS:
            latest_ncems = existing_ncems[-1]
            print(f'✓ Reusing existing NCEMS reviews: {latest_ncems}')
        else:
            subprocess.check_call([
                sys.executable,
                str(SCRIPTS_DIR / 'generate_reviews_ncems_criteria.py'),
                '--condition',
                CONDITION,
            ], cwd=PROJECT_ROOT)

            latest_ncems = sorted(NCEMS_REVIEWS_DIR.glob('ncems_reviews_*.json'))[-1]
            print(f'✓ NCEMS reviews written to: {latest_ncems}')
    """))
    novelty_idx = _find_code_cell_index(rendered, ["str(SCRIPTS_DIR / 'generate_reviews_novelty.py')", 'latest_novelty = sorted'])
    _set_cell_source(rendered, novelty_idx, dedent("""\
        existing_novelty = sorted(NOVELTY_REVIEWS_DIR.glob('novelty_reviews_*.json'))
        if existing_novelty and SKIP_NOVELTY_IF_EXISTS:
            latest_novelty = existing_novelty[-1]
            print(f'✓ Reusing existing novelty reviews: {latest_novelty}')
        else:
            subprocess.check_call([
                sys.executable,
                str(SCRIPTS_DIR / 'generate_reviews_novelty.py'),
                '--condition',
                CONDITION,
            ], cwd=PROJECT_ROOT)

            latest_novelty = sorted(NOVELTY_REVIEWS_DIR.glob('novelty_reviews_*.json'))[-1]
            print(f'✓ Novelty reviews written to: {latest_novelty}')
    """))
    scores_idx = _find_code_cell_index(rendered, ["str(SCRIPTS_DIR / 'build_review_scores_wide.py')", "print(f'✓ Review score table written to: {REVIEW_SCORES_PATH}')"])
    _set_cell_source(rendered, scores_idx, dedent("""\
        if REBUILD_REVIEW_SCORES or not REVIEW_SCORES_PATH.exists():
            subprocess.check_call([
                sys.executable,
                str(SCRIPTS_DIR / 'build_review_scores_wide.py'),
                '--condition',
                CONDITION,
            ], cwd=PROJECT_ROOT)
            print(f'✓ Review score table written to: {REVIEW_SCORES_PATH}')
        else:
            print(f'✓ Reusing existing review score table: {REVIEW_SCORES_PATH}')
    """))
    return rendered


def _render_compare_reviews(notebook: Dict[str, Any], condition: ConditionConfig,
                            review_kind: str) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                '- `CONDITION`: condition name whose AI review outputs should be analyzed.\n',
                '- `REUSE_REVIEW_EMBEDDINGS`: `True` to load cached review embeddings when the cache matches the current reviews.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
                REUSE_REVIEW_EMBEDDINGS = True
            """).splitlines(keepends=True),
        },
    ])
    idx = _find_code_cell_index(rendered, ["condition='minimal'", 'REVIEW_EMBEDDINGS_FILE'])
    existing_source = ''.join(rendered['cells'][idx].get('source', []))
    if 'NCEMS_ALL_REVIEWS_PATH' in existing_source or 'NOVELTY_ALL_REVIEWS_PATH' in existing_source:
        source = existing_source.replace("condition='minimal'", f"condition='{condition.name}'")
        _set_cell_source(rendered, idx, source)
        return rendered

    if review_kind == 'ncems_criteria':
        source = dedent(f"""\
            import json
            import re
            import itertools
            import pickle
            from pathlib import Path
            from difflib import SequenceMatcher

            import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            from scipy.stats import mannwhitneyu, kruskal, wilcoxon, spearmanr, kendalltau, linregress
            from sklearn.metrics.pairwise import cosine_similarity
            from textblob import TextBlob

            import torch
            from transformers import AutoTokenizer, AutoModel

            sns.set_theme(style='whitegrid', context='talk')

            def find_project_root():
                candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
                for candidate in candidates:
                    if (candidate / 'src').exists() and (candidate / 'data').exists():
                        return candidate.resolve()
                raise RuntimeError('Could not find project root containing src/ and data/.')

            PROJECT_ROOT = find_project_root()

            condition = CONDITION
            AI_REVIEWS_PATH = sorted(
                (PROJECT_ROOT / 'data' / 'reviews' / 'ai_reviews' / condition / 'ncems_criteria').glob('ncems_reviews_*.json')
            )[-1]
            HUMAN_Y1_REVIEWS_PATH = PROJECT_ROOT / 'data' / 'reviews' / 'human_reviews' / 'human_reviews_human-y1.xlsx'
            FIGURES_DIR = PROJECT_ROOT / 'results' / 'figures' / 'quality' / condition / 'ncems_criteria'
            TABLES_DIR = PROJECT_ROOT / 'results' / 'tables' / 'quality' / condition / 'ncems_criteria'
            REVIEW_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / 'reviews' / condition / 'ncems_criteria' / f'review_embeddings_{{condition}}.pkl'
            OUTPUT_DIR = FIGURES_DIR
            FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            TABLES_DIR.mkdir(parents=True, exist_ok=True)
            REVIEW_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            colors = {{
                'Human': '#DC143C',
                'claude-opus-4-5': '#4A90E2',
                'gemini-3-pro-preview': '#7B68EE',
                'gpt-5.2': '#FF8C00',
            }}

            CRITERIA_ORDER = [
                'Relevance_to_Emergent_Phenomena',
                'Novelty_and_Significance',
                'Rigor_of_Approach',
                'Scope_and_Timeline',
                'Synthesis_Focus',
                'Data_Identification',
                'Open_Science_Commitment',
            ]
    """)
    else:
        source = dedent(f"""\
            import json
            import re
            import itertools
            import pickle
            from pathlib import Path
            from difflib import SequenceMatcher

            import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            from scipy.stats import mannwhitneyu, kruskal, wilcoxon, spearmanr, kendalltau, linregress
            from sklearn.metrics.pairwise import cosine_similarity
            from textblob import TextBlob

            import torch
            from transformers import AutoTokenizer, AutoModel

            sns.set_theme(style='whitegrid', context='talk')

            def find_project_root():
                candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
                for candidate in candidates:
                    if (candidate / 'src').exists() and (candidate / 'data').exists():
                        return candidate.resolve()
                raise RuntimeError('Could not find project root containing src/ and data/.')

            PROJECT_ROOT = find_project_root()

            condition = CONDITION
            AI_REVIEWS_PATH = sorted(
                (PROJECT_ROOT / 'data' / 'reviews' / 'ai_reviews' / condition / 'novelty').glob('novelty_reviews_*.json')
            )[-1]
            FIGURES_DIR = PROJECT_ROOT / 'results' / 'figures' / 'quality' / condition / 'novelty'
            TABLES_DIR = PROJECT_ROOT / 'results' / 'tables' / 'quality' / condition / 'novelty'
            REVIEW_EMBEDDINGS_FILE = PROJECT_ROOT / 'data' / 'embeddings' / 'reviews' / condition / 'novelty' / f'review_embeddings_{{condition}}.pkl'
            OUTPUT_DIR = FIGURES_DIR
            FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            TABLES_DIR.mkdir(parents=True, exist_ok=True)
            REVIEW_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            colors = {{
                'Human': '#DC143C',
                'claude-opus-4-5': '#4A90E2',
                'gemini-3-pro-preview': '#7B68EE',
                'gpt-5.2': '#FF8C00',
            }}

            CRITERIA_ORDER = [
                'new_question_topic_or_framing',
                'new_theory_concept_method_dataset_or_design',
                'unusual_combination_of_existing_ideas',
                'beyond_state_of_the_art',
                'credible_high_risk_high_gain',
                'unique_knowledge_generation',
            ]
    """)
    _set_cell_source(rendered, idx, source)
    try:
        cache_idx = _find_code_cell_index(rendered, ['review_embeddings_loaded_from_cache = False', 'if REVIEW_EMBEDDINGS_FILE.exists():'])
        cache_src = ''.join(rendered['cells'][cache_idx]['source'])
        cache_src = cache_src.replace('if REVIEW_EMBEDDINGS_FILE.exists():', 'if REUSE_REVIEW_EMBEDDINGS and REVIEW_EMBEDDINGS_FILE.exists():')
        _set_cell_source(rendered, cache_idx, cache_src)
    except NotebookTemplateError:
        pass
    return rendered


def _render_metric_score_relationship(notebook: Dict[str, Any],
                                      condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    _prepend_cells(rendered, [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '## Condition Configuration\n',
                '\n',
                '- `CONDITION`: condition name whose `all_proposals.json` and review outputs should be linked here.\n',
                '- This notebook expects step 2 and step 3 outputs to already exist.\n',
            ],
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': dedent(f"""\
                CONDITION = '{condition.name}'
            """).splitlines(keepends=True),
        },
    ])
    idx = _find_code_cell_index(rendered, ['ALL_PROPOSALS_PATH', "condition = 'rephrased/minimal'"])
    existing_source = ''.join(rendered['cells'][idx].get('source', []))
    if 'NCEMS_ALL_REVIEWS_PATH' in existing_source and 'NOVELTY_ALL_REVIEWS_PATH' in existing_source:
        source = existing_source.replace(
            "condition = 'rephrased/minimal'",
            f"condition = 'rephrased/{condition.name}'",
        )
        source = source.replace(
            "ALL_PROPOSALS_PATH = PROJECT_ROOT / 'results' / 'tables' / 'rephrased' / 'minimal' / 'all_proposals.json'",
            f"ALL_PROPOSALS_PATH = PROJECT_ROOT / 'results' / 'tables' / 'rephrased' / '{condition.name}' / 'all_proposals.json'",
        )
        source = source.replace(
            "PREPARED_DIR = PROJECT_ROOT / 'results' / 'tables' / 'rephrased' / 'minimal' / 'prepared'",
            f"PREPARED_DIR = PROJECT_ROOT / 'results' / 'tables' / 'rephrased' / '{condition.name}' / 'prepared'",
        )
        _set_cell_source(rendered, idx, source)
        return rendered

    source = dedent(f"""\
        import sys
        import os
        import json
        import numpy as np
        import pandas as pd
        from pathlib import Path
        import pickle
        from datetime import datetime
        import warnings
        warnings.filterwarnings('ignore')

        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        from transformers import AutoTokenizer, AutoModel
        import torch
        from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
        from scipy.spatial.distance import cdist
        from tqdm import tqdm

        from scipy import stats
        from scipy.stats import mannwhitneyu
        import itertools

        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11

        def find_project_root():
            candidates = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]
            for candidate in candidates:
                if (candidate / 'src').exists() and (candidate / 'data').exists():
                    return candidate.resolve()
            raise RuntimeError('Could not find project root containing src/ and data/.')

        PROJECT_ROOT = find_project_root()

        print("✓ Imports successful")
        print(f"✓ Working directory: {{os.getcwd()}}")
        print(f"✓ Project root: {{PROJECT_ROOT}}")
        print(f"✓ PyTorch version: {{torch.__version__}}")
        print(f"✓ CUDA available: {{torch.cuda.is_available()}}")

        try:
            import umap
        except ImportError:
            import subprocess
            subprocess.check_call(['pip', 'install', 'umap-learn'])
            import umap

        ANALYSIS_CONDITION = CONDITION
        condition = f'rephrased/{{ANALYSIS_CONDITION}}'

        ALL_PROPOSALS_PATH = PROJECT_ROOT / 'results' / 'tables' / 'rephrased' / ANALYSIS_CONDITION / 'all_proposals.json'
        NCEMS_REVIEWS_PATH = sorted(
            (PROJECT_ROOT / 'data' / 'reviews' / 'ai_reviews' / ANALYSIS_CONDITION / 'ncems_criteria').glob('ncems_reviews_*.json')
        )[-1]
        NOVELTY_REVIEWS_PATH = sorted(
            (PROJECT_ROOT / 'data' / 'reviews' / 'ai_reviews' / ANALYSIS_CONDITION / 'novelty').glob('novelty_reviews_*.json')
        )[-1]

        RESULTS_DIR = PROJECT_ROOT / 'results'
        FIGURES_DIR = RESULTS_DIR / 'figures' / condition / 'metric-score'
        TABLES_DIR = RESULTS_DIR / 'tables' / condition / 'metric-score'
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
    """)
    _set_cell_source(rendered, idx, source)
    return rendered


def render_notebook(spec: NotebookSpec, condition: ConditionConfig, output_path: Path,
                    generate_new_ideas: bool = False) -> NotebookRenderResult:
    notebook = _load_notebook(spec.template)

    if spec.key == 'gen_proposals':
        notebook = _render_gen_proposals(notebook, condition, generate_new_ideas)
    elif spec.key == 'compare_proposals_rephrased':
        notebook = _render_compare_proposals_rephrased(notebook, condition)
    elif spec.key == 'generate_reviews':
        notebook = _render_generate_reviews(notebook, condition)
    elif spec.key == 'prepare_data_for_analysis':
        notebook = _render_prepare_data_for_analysis(notebook, condition)
    elif spec.key == 'compare_reviews_ncems_criteria':
        notebook = _render_compare_reviews(notebook, condition, 'ncems_criteria')
    elif spec.key == 'compare_reviews_novelty':
        notebook = _render_compare_reviews(notebook, condition, 'novelty')
    elif spec.key == 'metric_score_relationship':
        notebook = _render_metric_score_relationship(notebook, condition)
    else:
        raise NotebookTemplateError(f'Unsupported notebook key: {spec.key}')

    _write_notebook(output_path, notebook)
    return NotebookRenderResult(notebook=notebook, output_path=output_path)


def _serialize_display_output(output: Any) -> Dict[str, Any]:
    data = {}
    for mime, value in getattr(output, 'data', {}).items():
        if isinstance(value, bytes):
            data[mime] = base64.b64encode(value).decode('ascii')
        else:
            data[mime] = value
    return {
        'output_type': 'display_data',
        'data': data,
        'metadata': getattr(output, 'metadata', {}) or {},
    }


def _append_text_stream(outputs: List[Dict[str, Any]], name: str, text: str) -> None:
    if not text:
        return
    outputs.append({
        'output_type': 'stream',
        'name': name,
        'text': text,
    })


def execute_notebook(notebook_path: Path) -> None:
    try:
        from IPython.core.interactiveshell import InteractiveShell
        from IPython.utils.capture import capture_output
    except ImportError as exc:
        raise NotebookExecutionError(
            'Notebook execution requires IPython. Run this pipeline with the project notebook environment.'
        ) from exc

    notebook = _load_notebook(notebook_path)
    shell = InteractiveShell()
    try:
        shell.run_line_magic('matplotlib', 'inline')
    except NotImplementedError:
        # When running outside a full notebook shell, fall back to a
        # non-interactive backend so plotting cells can still execute.
        import matplotlib
        matplotlib.use('Agg')

    repo_root = Path(__file__).resolve().parent.parent
    old_cwd = Path.cwd()
    os.chdir(repo_root)
    try:
        exec_count = 1
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') != 'code':
                continue

            source = ''.join(cell.get('source', []))
            cell['outputs'] = []
            if not source.strip():
                cell['execution_count'] = None
                continue

            with capture_output(display=True) as captured:
                result = shell.run_cell(source)

            outputs: List[Dict[str, Any]] = []
            _append_text_stream(outputs, 'stdout', captured.stdout)
            _append_text_stream(outputs, 'stderr', captured.stderr)
            outputs.extend(_serialize_display_output(output) for output in captured.outputs)

            if result.error_before_exec or result.error_in_exec:
                err = result.error_before_exec or result.error_in_exec
                tb = traceback.format_exception(type(err), err, err.__traceback__)
                outputs.append({
                    'output_type': 'error',
                    'ename': type(err).__name__,
                    'evalue': str(err),
                    'traceback': tb,
                })
                cell['outputs'] = outputs
                cell['execution_count'] = exec_count
                _write_notebook(notebook_path, notebook)
                raise NotebookExecutionError(f'Notebook execution failed in {notebook_path.name}: {err}')

            if result.result is not None:
                outputs.append({
                    'output_type': 'execute_result',
                    'data': {'text/plain': repr(result.result)},
                    'metadata': {},
                    'execution_count': exec_count,
                })

            cell['outputs'] = outputs
            cell['execution_count'] = exec_count
            exec_count += 1

        _write_notebook(notebook_path, notebook)
    finally:
        os.chdir(old_cwd)
