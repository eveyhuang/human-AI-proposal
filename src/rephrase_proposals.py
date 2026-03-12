"""
Rephrase all AI and human proposals field-by-field into a neutral academic style
using gemini-2.0-flash, removing stylistic differences while preserving content.

Usage (run from project root):
    python src/rephrase_proposals.py

Outputs:
    data/ai-proposals/rephrased/ai_proposals_rephrased_<timestamp>.csv
    data/human-proposals/rephrased/human_proposals_rephrased_y1_<timestamp>.json
    data/human-proposals/rephrased/human_proposals_rephrased_y2_<timestamp>.json
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from google import genai

# ─── Setup ────────────────────────────────────────────────────────────────────
load_dotenv(Path('.env'), override=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

GEMINI_MODEL = 'gemini-2.0-flash'
RETRY_DELAYS = [5, 15, 30]   # seconds between retries on API errors

# ─── Rephrasing prompt ────────────────────────────────────────────────────────
REPHRASE_SYSTEM = """You are a scientific editor. Your task is to rephrase text into a standardized neutral academic style. Rules:
1. Preserve ALL scientific content exactly: hypotheses, methods, data sources, expected outcomes, findings.
2. Use neutral, formal academic register (similar to Nature Methods).
3. Write in third person ("This project...", "The study...") — no "I will" or "we propose to".
4. Use consistent hedging: prefer "may", "suggests", "is expected to", "will be investigated".
5. Use standard paragraph structure: topic sentence followed by supporting details.
6. Avoid bullet lists; write in prose.
7. Avoid redundant phrases like "cutting-edge", "groundbreaking", "revolutionary", "novel approach".
8. Keep sentence length 18–28 words on average.
9. Return ONLY the rephrased text with no preamble, explanation, or quotes."""

TITLE_SYSTEM = """You are a scientific editor. Rephrase this research proposal title into standard academic title format. Rules:
1. Preserve ALL scientific content and meaning.
2. Use noun-phrase format (no verbs like "investigating" at the start unless natural).
3. Title Case capitalization.
4. No colons unless truly needed for subtitle.
5. 8–15 words preferred.
6. Return ONLY the rephrased title with no preamble."""


def rephrase_field(client: genai.Client, text: str, is_title: bool = False,
                   max_retries: int = 3) -> Optional[str]:
    """Call gemini-2.0-flash to rephrase a single text field. Returns None on failure."""
    if not text or not str(text).strip():
        return text

    system_prompt = TITLE_SYSTEM if is_title else REPHRASE_SYSTEM
    prompt = f"{system_prompt}\n\n---\nORIGINAL TEXT:\n{str(text).strip()}\n---\nREPHRASED:"

    for attempt, delay in enumerate([0] + RETRY_DELAYS[:max_retries - 1]):
        if delay:
            logger.info(f"Retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config={'temperature': 0}
            )
            result = response.text.strip()
            # Strip surrounding quotes if model added them
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1].strip()
            return result
        except Exception as e:
            logger.warning(f"Gemini error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"All retries failed; keeping original text")
                return text  # fallback: keep original

    return text


def rephrase_ai_proposals(client: genai.Client, ai_csv_path: Path,
                          checkpoint_path: Path = None) -> pd.DataFrame:
    """Rephrase all AI proposal fields. Returns modified DataFrame."""
    df = pd.read_csv(ai_csv_path)
    logger.info(f"Loaded {len(df)} AI proposals from {ai_csv_path.name}")

    # Fields to rephrase — order matters for tqdm display
    text_fields = [
        'abstract',
        'background_and_significance',
        'research_questions_and_hypotheses',
        'methods_and_approach',
        'expected_outcomes_and_impact',
        'budget_and_resources',
    ]

    rephrased_df = df.copy()

    for row_num, (idx, row) in enumerate(tqdm(df.iterrows(), total=len(df),
                         desc="Rephrasing AI proposals"), start=1):
        model_label = row.get('model', 'unknown')
        title_orig = str(row.get('title', ''))

        # Rephrase title
        rephrased_df.at[idx, 'title'] = rephrase_field(
            client, title_orig, is_title=True)

        # Rephrase all text fields
        for field in text_fields:
            orig = str(row.get(field, ''))
            rephrased_df.at[idx, field] = rephrase_field(client, orig)

        logger.info(f"  [{row_num}/{len(df)}] {model_label}: {title_orig[:60]}...")
        if checkpoint_path is not None:
            rephrased_df.to_csv(checkpoint_path, index=False)

    return rephrased_df


def rephrase_human_proposals(client: genai.Client,
                              json_path: Path) -> Dict[str, Any]:
    """Rephrase all human proposal fields. Returns modified data dict."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    proposals = data.get('proposals', [])
    logger.info(f"Loaded {len(proposals)} human proposals from {json_path.name}")

    rephrased_proposals = []
    for i, proposal in enumerate(tqdm(proposals, desc=f"Rephrasing {json_path.name}")):
        p = dict(proposal)  # copy

        # Rephrase title
        p['proposal_title'] = rephrase_field(
            client, proposal.get('proposal_title', ''), is_title=True)

        # Rephrase abstract
        p['abstract'] = rephrase_field(
            client, proposal.get('abstract', ''))

        # Rephrase full_draft (may be long — send as-is, model handles length)
        p['full_draft'] = rephrase_field(
            client, proposal.get('full_draft', ''))

        logger.info(f"  [{i+1}/{len(proposals)}] {proposal.get('proposal_title', '')[:60]}...")
        rephrased_proposals.append(p)

    return {**data, 'proposals': rephrased_proposals}


def main():
    # ── Validate API key ──────────────────────────────────────────────────────
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY not set. Check your .env file.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # ── Rephrase AI proposals ─────────────────────────────────────────────────
    ai_baseline_dir = Path('data/ai-proposals/baseline')
    ai_csv_files = sorted(ai_baseline_dir.glob('ai_proposals_baseline_complete_*.csv'))
    if not ai_csv_files:
        logger.error("No AI proposal CSV found in data/ai-proposals/baseline/")
        sys.exit(1)

    ai_csv_path = ai_csv_files[-1]  # most recent
    ai_out_path = Path('data/ai-proposals/rephrased') / f'ai_proposals_rephrased_{timestamp}.csv'
    checkpoint_path = ai_out_path.with_suffix('.csv.tmp')
    rephrased_ai_df = rephrase_ai_proposals(client, ai_csv_path,
                                            checkpoint_path=checkpoint_path)

    ai_out_path.parent.mkdir(parents=True, exist_ok=True)
    rephrased_ai_df.to_csv(ai_out_path, index=False)
    logger.info(f"Saved rephrased AI proposals -> {ai_out_path}")
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    # ── Rephrase human proposals ──────────────────────────────────────────────
    for cohort in ['y1', 'y2']:
        human_path = Path(f'data/human-proposals/human-proposals-{cohort}.json')
        if not human_path.exists():
            logger.warning(f"Not found: {human_path}, skipping.")
            continue

        rephrased_data = rephrase_human_proposals(client, human_path)
        out_path = (Path('data/human-proposals/rephrased') /
                    f'human_proposals_rephrased_{cohort}_{timestamp}.json')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump(rephrased_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved rephrased human proposals -> {out_path}")

    logger.info("Done. All rephrased proposals saved.")


if __name__ == '__main__':
    main()
