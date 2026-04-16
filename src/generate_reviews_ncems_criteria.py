"""
Generate AI reviews (GPT, Gemini, Claude) for all proposals using the NCEMS criteria prompt.

Adapted from eval_proposals_ncems_criteria.ipynb.

Usage (run from project root):
    python src/generate_reviews_ncems_criteria.py --condition minimal

Output:
    data/reviews/ai_reviews/<condition>/ncems_reviews_<timestamp>.json
"""

import argparse
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv(Path('.env'), override=True)
sys.path.insert(0, str(Path(__file__).parent))

from ai_models_interface import AIModelsInterface
from prompt_templates import PromptManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MAX_FULL_TEXT_CHARS = 60_000


# ─── Helpers (mirrors eval_proposals_ncems_criteria.ipynb) ────────────────────

def extract_first_json_object(text: str) -> Tuple[Optional[Dict], Optional[str]]:
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
    depth, end = 0, -1
    for i, ch in enumerate(s[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None, 'unclosed JSON object'
    try:
        return json.loads(s[start:end + 1]), None
    except json.JSONDecodeError as e:
        return None, str(e)


def _infer_human_author(source_file: str) -> str:
    sf = (source_file or '').lower()
    if 'y1' in sf:
        return 'human-y1'
    if 'y2' in sf:
        return 'human-y2'
    return 'human'


AI_SECTION_COLUMNS = [
    ('Abstract', 'abstract'),
    ('Background and Significance', 'background_and_significance'),
    ('Research Questions and Hypotheses', 'research_questions_and_hypotheses'),
    ('Methods and Approach', 'methods_and_approach'),
    ('Expected Outcomes and Impact', 'expected_outcomes_and_impact'),
    ('Budget and Resources', 'budget_and_resources'),
]


def create_full_text_ai(proposal: Dict[str, Any]) -> str:
    """Assemble full text for AI proposals from their individual section columns."""
    parts = []
    for label, col in AI_SECTION_COLUMNS:
        val = str(proposal.get(col, '') or '').strip()
        if val:
            parts.append(f"{label.upper()}:\n{val}")
    return '\n\n'.join(parts)


def create_full_text_human(proposal: Dict[str, Any]) -> str:
    """Assemble full text for human proposals from abstract + full_draft."""
    abstract = str(proposal.get('abstract', '') or '').strip()
    full_draft = str(proposal.get('full_draft', '') or '').strip()
    parts = []
    if abstract:
        parts.append(f"ABSTRACT:\n{abstract}")
    if full_draft:
        parts.append(f"FULL PROPOSAL:\n{full_draft}")
    return '\n\n'.join(parts)


def make_prompt(proposal: Dict[str, Any], research_call: str,
                prompt_manager: PromptManager, template: str = 'eval_ncems_criteria') -> str:
    title = str(proposal.get('title', proposal.get('proposal_title', ''))).strip()
    full_text = str(proposal.get('_full_text', '')).strip()

    if len(full_text) > MAX_FULL_TEXT_CHARS:
        full_text = full_text[:MAX_FULL_TEXT_CHARS] + '\n[... truncated for length ...]'

    return prompt_manager.format_prompt(template, {
        'research_call': research_call,
        'proposal_id': proposal.get('proposal_id', 'N/A'),
        'proposal_title': title,
        'proposal_abstract': '',
        'proposal_full': full_text,
    })


def load_proposals(ai_dir: Path, human_dir: Path) -> List[Dict[str, Any]]:
    """Load all proposals into a flat list."""
    proposals = []

    # AI proposals (proposals only — exclude ai_ideas_*.csv files)
    ai_files = sorted(ai_dir.glob('ai_proposals_*.csv'))
    if not ai_files:
        raise FileNotFoundError(f"No ai_proposals_*.csv found in {ai_dir}")
    ai_df = pd.read_csv(ai_files[-1])
    logger.info(f"Loaded {len(ai_df)} AI proposals from {ai_files[-1].name}")

    for _, row in ai_df.iterrows():
        p = row.to_dict()
        p['author'] = row.get('model', 'ai')
        p['_full_text'] = create_full_text_ai(p)
        proposals.append(p)

    # Human proposals
    for cohort_glob in ['*y1*.json', '*y2*.json']:
        h_files = sorted(human_dir.glob(cohort_glob))
        if not h_files:
            logger.warning(f"No file matching {cohort_glob} in {human_dir}")
            continue
        with open(h_files[-1]) as f:
            data = json.load(f)
        source_file = h_files[-1].name
        for proposal in data.get('proposals', []):
            p = dict(proposal)
            p['title'] = proposal.get('proposal_title', '')
            p['author'] = _infer_human_author(source_file)
            p['_full_text'] = create_full_text_human(p)
            proposals.append(p)

    logger.info(f"Total proposals to review: {len(proposals)}")
    return proposals


def main():
    parser = argparse.ArgumentParser(description='Generate NCEMS-criteria AI reviews for proposals.')
    parser.add_argument('--condition', default='minimal',
                        help='Condition sub-path, e.g. "minimal" (default: minimal)')
    parser.add_argument('--template', default='eval_ncems_criteria',
                        help='Prompt template name to use for evaluation (default: eval_ncems_criteria)')
    args = parser.parse_args()
    condition = args.condition
    template = args.template

    # ── Paths ─────────────────────────────────────────────────────────────────
    ai_dir = Path(f'data/ai-proposals/{condition}')
    human_dir = Path('data/human-proposals')
    output_dir = Path(f'data/reviews/ai_reviews/{condition}/ncems_criteria')
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load research call ────────────────────────────────────────────────────
    with open('data/call_and_info.json') as f:
        call_and_info = json.load(f)
    research_call = call_and_info['call']

    # ── Load proposals ────────────────────────────────────────────────────────
    proposals = load_proposals(ai_dir, human_dir)

    # ── Initialize models ─────────────────────────────────────────────────────
    ai_interface = AIModelsInterface(config_path='.env', override_env=True)
    available_models = ai_interface.get_available_models()
    requested_models = ['gpt-5.2', 'gemini-3-pro-preview', 'claude-opus-4-5']
    evaluator_models = [m for m in requested_models if m in available_models]

    if not evaluator_models:
        logger.error("No evaluator models available. Check API keys.")
        sys.exit(1)
    logger.info(f"Evaluator models: {evaluator_models}")

    prompt_manager = PromptManager()
    _ = prompt_manager.get_template(template)

    # ── Output file ────────────────────────────────────────────────────────────
    run_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'ncems_reviews_{run_ts}.json'

    output_data = {
        'created_at': datetime.now().isoformat(),
        'condition': condition,
        'template': template,
        'research_call_source': 'data/call_and_info.json',
        'human_inputs': [
            'data/human-proposals/human-proposals-y1.json',
            'data/human-proposals/human-proposals-y2.json',
        ],
        'ai_input': f'data/ai-proposals/{condition}/ai_proposals_*.csv',
        'evaluators': evaluator_models,
        'reviews': [],
    }

    # ── Main evaluation loop ───────────────────────────────────────────────────
    total_calls = len(proposals) * len(evaluator_models)
    pbar = tqdm(total=total_calls, desc='Generating reviews')

    for proposal in proposals:
        title = str(proposal.get('title', proposal.get('proposal_title', '')))
        author = proposal.get('author', 'unknown')
        prompt = make_prompt(proposal, research_call, prompt_manager, template)

        for evaluator in evaluator_models:
            pbar.set_description(f"{evaluator} | {title[:40]}")
            try:
                raw = ai_interface.generate_content(prompt, model_name=evaluator,
                                                    temperature=0, max_tokens=4096)
                parsed, err = extract_first_json_object(raw)
                review_entry = {
                    'title': title,
                    'author': author,
                    'evaluator': evaluator,
                    'evaluations': parsed if parsed else {},
                    'raw_response': raw,
                    'parse_error': err,
                }
            except Exception as e:
                logger.error(f"Error evaluating '{title[:40]}' with {evaluator}: {e}")
                review_entry = {
                    'title': title,
                    'author': author,
                    'evaluator': evaluator,
                    'evaluations': {},
                    'raw_response': str(e),
                    'parse_error': str(e),
                }

            output_data['reviews'].append(review_entry)
            pbar.update(1)

            # Save checkpoint after every review
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

    pbar.close()
    logger.info(f"Done. {len(output_data['reviews'])} reviews saved to {output_path}")


if __name__ == '__main__':
    main()
