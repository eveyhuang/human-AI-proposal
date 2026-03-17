"""
Re-generate AI reviews (GPT, Gemini, Claude) for all rephrased proposals.

Adapted from eval_proposals_ncems_criteria.ipynb.

Usage (run from project root):
    python src/generate_reviews_rephrased.py

Output:
    data/reviews/ai_reviews/ai_reviews_rephrased_<timestamp>.json
    (same structure as ai_reviews_ncems_criteria_20260223_153411.json)
"""

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


def create_full_text(proposal: Dict[str, Any]) -> str:
    """Return the standardized_text produced by the two-step summarize→fill pipeline."""
    return str(proposal.get('standardized_text', '') or '').strip()


def make_prompt(proposal: Dict[str, Any], research_call: str,
                prompt_manager: PromptManager) -> str:
    title = str(proposal.get('title', proposal.get('proposal_title', ''))).strip()
    full_text = str(proposal.get('_full_text', '')).strip()

    if len(full_text) > MAX_FULL_TEXT_CHARS:
        full_text = full_text[:MAX_FULL_TEXT_CHARS] + '\n[... truncated for length ...]'

    # All content is now in standardized_text (5 template sections).
    # proposal_abstract is left empty — the template parameter is still required
    # by the prompt template but there is no separate abstract after rephrasing.
    return prompt_manager.format_prompt('eval_ncems_criteria', {
        'research_call': research_call,
        'proposal_id': proposal.get('proposal_id', 'N/A'),
        'proposal_title': title,
        'proposal_abstract': '',
        'proposal_full': full_text,
    })


def load_proposals(ai_rephrased_dir: Path,
                   human_rephrased_dir: Path) -> List[Dict[str, Any]]:
    """Load all rephrased proposals into a flat list."""
    proposals = []

    # AI proposals
    ai_files = sorted(ai_rephrased_dir.glob('ai_proposals_rephrased_*.csv'))
    if not ai_files:
        raise FileNotFoundError(f"No rephrased AI CSV in {ai_rephrased_dir}")
    ai_df = pd.read_csv(ai_files[-1])
    logger.info(f"Loaded {len(ai_df)} AI proposals from {ai_files[-1].name}")

    for _, row in ai_df.iterrows():
        p = row.to_dict()
        p['author'] = row.get('model', 'ai')
        p['_full_text'] = create_full_text(p)
        proposals.append(p)

    # Human proposals
    for cohort_glob in ['*y1*.json', '*y2*.json']:
        h_files = sorted(human_rephrased_dir.glob(cohort_glob))
        if not h_files:
            logger.warning(f"No file matching {cohort_glob} in {human_rephrased_dir}")
            continue
        with open(h_files[-1]) as f:
            data = json.load(f)
        source_file = h_files[-1].name
        for proposal in data.get('proposals', []):
            p = dict(proposal)
            p['title'] = proposal.get('proposal_title', '')
            p['author'] = _infer_human_author(source_file)
            p['_full_text'] = create_full_text(p)
            proposals.append(p)

    logger.info(f"Total proposals to review: {len(proposals)}")
    return proposals


def main():
    # ── Paths ─────────────────────────────────────────────────────────────────
    ai_rephrased_dir = Path('data/ai-proposals/rephrased')
    human_rephrased_dir = Path('data/human-proposals/rephrased')
    output_dir = Path('data/reviews/ai_reviews')
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load research call ────────────────────────────────────────────────────
    with open('data/call_and_info.json') as f:
        call_and_info = json.load(f)
    research_call = call_and_info['call']

    # ── Load proposals ────────────────────────────────────────────────────────
    proposals = load_proposals(ai_rephrased_dir, human_rephrased_dir)

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
    _ = prompt_manager.get_template('eval_ncems_criteria')

    # ── Output file ────────────────────────────────────────────────────────────
    run_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'ai_reviews_rephrased_{run_ts}.json'

    output_data = {
        'created_at': datetime.now().isoformat(),
        'research_call_source': 'data/call_and_info.json',
        'human_inputs': [
            'data/human-proposals/rephrased/human_proposals_rephrased_y1_*.json',
            'data/human-proposals/rephrased/human_proposals_rephrased_y2_*.json',
        ],
        'ai_input': 'data/ai-proposals/rephrased/ai_proposals_rephrased_*.csv',
        'evaluators': evaluator_models,
        'rephrased': True,
        'reviews': [],
    }

    # ── Main evaluation loop ───────────────────────────────────────────────────
    total_calls = len(proposals) * len(evaluator_models)
    pbar = tqdm(total=total_calls, desc='Generating reviews')

    for proposal in proposals:
        title = str(proposal.get('title', proposal.get('proposal_title', '')))
        author = proposal.get('author', 'unknown')
        prompt = make_prompt(proposal, research_call, prompt_manager)

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
