"""
Generate novelty-focused AI reviews for all rephrased proposals.

Uses the 'eval_novelty' prompt template, which scores proposals on six
novelty dimensions and supplies each proposal with abstracts of its three
closest literature neighbors (from proposal_lit_neighbors.json) as context.

Usage (run from project root):
    python src/generate_reviews_novelty.py --condition rephrased/minimal

Output:
    data/reviews/ai_reviews/<condition>/novelty_reviews_<timestamp>.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(Path('.env'), override=True)
sys.path.insert(0, str(Path(__file__).parent))

from ai_models_interface import AIModelsInterface
from prompt_templates import PromptManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MAX_FULL_TEXT_CHARS = 60_000


# ─── Helpers ──────────────────────────────────────────────────────────────────

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


def format_lit_neighbors(neighbors: List[Dict[str, Any]]) -> str:
    """Format the three literature neighbors into a readable block for the prompt."""
    lines = []
    for n in neighbors:
        rank = n.get('rank', '?')
        title = n.get('title', 'Unknown title')
        abstract = n.get('abstract', '').strip()
        pub_date = n.get('publication_date', '')
        pmid = n.get('pmid', '')
        lines.append(
            f"[{rank}] {title} (PMID: {pmid}, {pub_date})\n"
            f"Abstract: {abstract}"
        )
    return '\n\n'.join(lines)


def load_lit_neighbors(condition: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load proposal_lit_neighbors.json for the given condition and return a
    flat title → lit_neighbors mapping (covers both human and AI proposals).
    """
    neighbors_path = Path(f'results/tables/rephrased/{condition}/proposal_lit_neighbors.json')
    if not neighbors_path.exists():
        raise FileNotFoundError(f"Lit-neighbors file not found: {neighbors_path}")
    with open(neighbors_path) as f:
        data = json.load(f)

    title_to_neighbors: Dict[str, List[Dict[str, Any]]] = {}
    for group_entries in data.values():
        for title, entry in group_entries.items():
            title_to_neighbors[title] = entry.get('lit_neighbors', [])

    logger.info(f"Loaded lit-neighbors for {len(title_to_neighbors)} proposals")
    return title_to_neighbors


def load_proposals(ai_rephrased_dir: Path,
                   human_rephrased_dir: Path) -> List[Dict[str, Any]]:
    """Load all rephrased proposals into a flat list."""
    proposals = []

    # AI proposals (proposals only — exclude ai_ideas_*.csv files)
    ai_files = sorted(ai_rephrased_dir.glob('ai_proposals_*.csv'))
    if not ai_files:
        raise FileNotFoundError(f"No ai_proposals_*.csv found in {ai_rephrased_dir}")
    ai_df = pd.read_csv(ai_files[-1])
    logger.info(f"Loaded {len(ai_df)} AI proposals from {ai_files[-1].name}")

    for _, row in ai_df.iterrows():
        p = row.to_dict()
        p['author'] = row.get('model', 'ai')
        p['_full_text'] = create_full_text_ai(p)
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
            p['_full_text'] = create_full_text_human(p)
            proposals.append(p)

    logger.info(f"Total proposals to review: {len(proposals)}")
    return proposals


def make_prompt(proposal: Dict[str, Any],
                title_to_neighbors: Dict[str, List[Dict[str, Any]]],
                prompt_manager: PromptManager) -> str:
    title = str(proposal.get('title', proposal.get('proposal_title', ''))).strip()
    full_text = str(proposal.get('_full_text', '')).strip()

    if len(full_text) > MAX_FULL_TEXT_CHARS:
        full_text = full_text[:MAX_FULL_TEXT_CHARS] + '\n[... truncated for length ...]'

    neighbors = title_to_neighbors.get(title, [])
    if not neighbors:
        logger.warning(f"No lit-neighbors found for: {title[:60]!r}")
    lit_neighbors_text = format_lit_neighbors(neighbors) if neighbors else (
        "No literature neighbors available for this proposal."
    )

    return prompt_manager.format_prompt('eval_novelty', {
        'proposal_id': proposal.get('proposal_id', 'N/A'),
        'proposal_title': title,
        'proposal_full': full_text,
        'lit_neighbors': lit_neighbors_text,
    })


def main():
    parser = argparse.ArgumentParser(
        description='Generate novelty-focused AI reviews for rephrased proposals.'
    )
    parser.add_argument('--condition', default='minimal',
                        help='Condition sub-path, e.g. "minimal" (default: minimal)')
    args = parser.parse_args()
    condition = args.condition

    # ── Paths ─────────────────────────────────────────────────────────────────
    ai_proposal_dir = Path(f'data/ai-proposals/{condition}')
    human_proposal_dir = Path(f'data/human-proposals/')
    output_dir = Path(f'data/reviews/ai_reviews/{condition}/novelty') 
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load lit-neighbors lookup ─────────────────────────────────────────────
    title_to_neighbors = load_lit_neighbors(condition)

    # ── Load proposals ────────────────────────────────────────────────────────
    proposals = load_proposals(ai_proposal_dir, human_proposal_dir)

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
    _ = prompt_manager.get_template('eval_novelty')  # validate template exists

    # ── Output file ────────────────────────────────────────────────────────────
    run_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f'novelty_reviews_{run_ts}.json'

    output_data = {
        'created_at': datetime.now().isoformat(),
        'condition': condition,
        'template': 'eval_novelty',
        'lit_neighbors_source': f'results/tables/{condition}/proposal_lit_neighbors.json',
        'human_inputs': [
            f'data/human-proposals/{condition}/human_proposals_rephrased_y1_*.json',
            f'data/human-proposals/{condition}/human_proposals_rephrased_y2_*.json',
        ],
        'ai_input': f'data/ai-proposals/{condition}/*.csv',
        'evaluators': evaluator_models,
        'rephrased': True,
        'reviews': [],
    }

    # ── Main evaluation loop ───────────────────────────────────────────────────
    total_calls = len(proposals) * len(evaluator_models)
    pbar = tqdm(total=total_calls, desc='Generating novelty reviews')

    for proposal in proposals:
        title = str(proposal.get('title', proposal.get('proposal_title', '')))
        author = proposal.get('author', 'unknown')
        prompt = make_prompt(proposal, title_to_neighbors, prompt_manager)

        for evaluator in evaluator_models:
            pbar.set_description(f"{evaluator} | {title[:40]}")
            try:
                raw = ai_interface.generate_content(prompt, model_name=evaluator,
                                                    temperature=0, max_tokens=4096,
                                                    use_web_search=True)
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
