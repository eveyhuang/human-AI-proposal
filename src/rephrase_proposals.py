"""
Extract all AI and human proposals into a fixed evaluation-aligned template,
neutralizing stylistic and structural differences while preserving scientific content.

The template mirrors the NCEMS call for proposals and evaluation criteria:
  Section 1 – Scientific Background & Research Question  → criteria 1a (emergent phenomena), 1b (novelty)
  Section 2 – Methodology & Analytical Approach          → criterion  1c (rigor)
  Section 3 – Data Sources & Synthesis Plan              → criteria 3a (synthesis focus), 3b (data ID)
  Section 4 – Feasibility & Timeline                     → criterion  2a (scope/timeline)
  Section 5 – Open Science & Team Composition            → criterion  4a (open science) + call requirement

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

GEMINI_MODEL = 'gemini-3.1-flash-lite-preview'
RETRY_DELAYS = [5, 15, 30]   # seconds between retries on API errors

# ─── Fixed extraction template ────────────────────────────────────────────────
# Each section maps directly to NCEMS evaluation criteria and call requirements.
# Both human and AI proposals are extracted into this identical skeleton so that
# the classifier cannot exploit source-structure differences.

EXTRACTION_SYSTEM = """You are a scientific editor standardizing research proposals for blind review.
Extract the proposal content into the EXACT fixed template below.
Follow the section headings, sentence counts, and guidance precisely.

TEMPLATE:

SCIENTIFIC BACKGROUND AND RESEARCH QUESTION
(Write exactly 3 sentences.)
Sentence 1: State the research domain, the specific emergent or mesoscale phenomenon being studied, and the key scientific gap or open question.
Sentence 2: Describe current state of knowledge — what is known, what data exist, and where understanding is incomplete.
Sentence 3: State the primary research question or objective, and explain why it is novel or significant for the field.

METHODOLOGY AND ANALYTICAL APPROACH
(Write exactly 3 sentences.)
Sentence 1: Describe the overall study design and the core analytical or computational strategy.
Sentence 2: Specify the key methods, models, tools, or algorithms to be applied.
Sentence 3: Explain how results will be validated, benchmarked, or compared.

DATA SOURCES AND SYNTHESIS PLAN
(Write exactly 3 sentences.)
Sentence 1: Identify the publicly available datasets or databases to be used (include names and sources if mentioned).
Sentence 2: Describe how distinct datasets will be integrated or synthesized to address the research question.
Sentence 3: Acknowledge known data limitations and explain how they will be mitigated.

FEASIBILITY AND TIMELINE
(Write exactly 2 sentences.)
Sentence 1: Summarize the proposed milestones and overall timeline for the project.
Sentence 2: Explain why the project scope requires multi-lab or cross-disciplinary collaboration beyond the capacity of a single research group.

OPEN SCIENCE AND TEAM COMPOSITION
(Write exactly 2 sentences.)
Sentence 1: Describe plans for making findings, analytical code, and processed data publicly available in accordance with open and reproducible science principles.
Sentence 2: Characterize the composition of the proposed team, including scientific disciplines, career stages, and any training opportunities for students or postdocs.

RULES:
- Use ONLY information present in the original proposal text. Do not invent or infer facts.
- Write in third-person neutral academic register ("This project...", "The proposed study...").
- Do not use first person ("I", "we").
- Avoid evaluative language ("cutting-edge", "groundbreaking", "novel approach", "revolutionary").
- Use declarative academic style with minimal hedging. Write outcomes and methods as direct statements ("This project will...", "The study examines...", "Results will be validated..."). Reserve hedging words ("may", "suggests", "is expected to") only when the original proposal itself expresses explicit uncertainty — do not add hedging that is not in the source.
- Maintain average sentence length of 18–22 words. Prefer simple clause structure: one main clause with at most one subordinate clause per sentence. Avoid stacking multiple conditions or qualifications.
- VOCABULARY CONSISTENCY: Use the same term for the same concept throughout — do not introduce synonyms or paraphrases for technical terms. Prefer common academic vocabulary over rare or specialized alternatives.
- FUNCTION WORDS: Write using full prepositional phrases rather than noun stacks. For example, use "the analysis of protein dynamics" not "protein dynamics analysis"; use "a model for predicting X" not "an X prediction model". Include articles ("the", "a", "an") and prepositions naturally — do not compress phrases.
- READING LEVEL: Keep sentence structure simple and avoid long chains of embedded clauses.
- SENTENCE COUNT: Adhere strictly to the sentence count specified for each section. Do not add extra sentences, do not split any specified sentence into two, and do not merge two specified sentences into one.
- COMMA USE: Minimize commas. Do not use serial/Oxford commas in lists — instead restructure as prose using "and" without a preceding comma, or write separate sentences. Use a comma only when grammatically required to separate a subordinate clause from a main clause.
- PARENTHESES: Use parentheses for brief inline clarifications, acronym definitions on first use, and examples — for example "(e.g., satellite imagery)" or "machine learning (ML)". This matches standard academic prose and should appear naturally where appropriate.
- NO LISTS OR COLONS: Do not use bullet points, numbered lists, or colons to introduce enumerated items. Write all content as flowing prose sentences. Do not add extra line breaks within a section.
- If the proposal does not address a sentence's topic, write one sentence stating that the proposal does not specify this information.
- Output ONLY the filled template with the five section headings and their sentences. No preamble, no commentary."""


TITLE_SYSTEM = """You are a scientific editor. Rephrase this research proposal title into standard academic title format. Rules:
1. Preserve ALL scientific content and meaning.
2. Use noun-phrase format (no verbs like "investigating" at the start unless natural).
3. Title Case capitalization.
4. No colons unless truly needed for subtitle.
5. 8–15 words preferred.
6. Return ONLY the rephrased title with no preamble."""


def extract_proposal(client: genai.Client, full_text: str,
                     max_retries: int = 3) -> Optional[str]:
    """Call Gemini to extract a proposal into the fixed template. Returns None on failure."""
    if not full_text or not full_text.strip():
        return None

    prompt = f"{EXTRACTION_SYSTEM}\n\n---\nPROPOSAL TEXT:\n{full_text.strip()}\n---\nEXTRACTED TEMPLATE:"

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
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1].strip()
            return result
        except Exception as e:
            logger.warning(f"Gemini error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error("All retries failed; keeping None")
                return None

    return None


def rephrase_title(client: genai.Client, title: str,
                   max_retries: int = 3) -> str:
    """Rephrase a proposal title. Returns original on failure."""
    if not title or not title.strip():
        return title

    prompt = f"{TITLE_SYSTEM}\n\n---\nORIGINAL TITLE:\n{title.strip()}\n---\nREPHRASED TITLE:"

    for attempt, delay in enumerate([0] + RETRY_DELAYS[:max_retries - 1]):
        if delay:
            time.sleep(delay)
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt],
                config={'temperature': 0}
            )
            result = response.text.strip()
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1].strip()
            return result
        except Exception as e:
            logger.warning(f"Title rephrase error (attempt {attempt + 1}): {e}")

    return title  # fallback


def build_ai_full_text(row: pd.Series) -> str:
    """Concatenate all AI proposal fields into a single text block for extraction."""
    parts = []
    field_labels = [
        ('abstract',                        'Abstract'),
        ('background_and_significance',     'Background and Significance'),
        ('research_questions_and_hypotheses','Research Questions and Hypotheses'),
        ('methods_and_approach',            'Methods and Approach'),
        ('expected_outcomes_and_impact',    'Expected Outcomes and Impact'),
        ('budget_and_resources',            'Budget and Resources'),
    ]
    for field, label in field_labels:
        text = str(row.get(field, '')).strip()
        if text and text.lower() not in ('nan', 'none', ''):
            parts.append(f"[{label}]\n{text}")
    return '\n\n'.join(parts)


def build_human_full_text(proposal: dict) -> str:
    """Concatenate human proposal fields into a single text block for extraction."""
    parts = []
    abstract = str(proposal.get('abstract', '')).strip()
    full_draft = str(proposal.get('full_draft', '')).strip()
    if abstract and abstract.lower() not in ('nan', 'none', ''):
        parts.append(f"[Abstract]\n{abstract}")
    if full_draft and full_draft.lower() not in ('nan', 'none', ''):
        parts.append(f"[Full Proposal]\n{full_draft}")
    return '\n\n'.join(parts)


def rephrase_ai_proposals(client: genai.Client, ai_csv_path: Path,
                          checkpoint_path: Path = None) -> pd.DataFrame:
    """Extract all AI proposals into the fixed template. Returns modified DataFrame."""
    df = pd.read_csv(ai_csv_path)
    logger.info(f"Loaded {len(df)} AI proposals from {ai_csv_path.name}")

    rephrased_df = df.copy()

    for row_num, (idx, row) in enumerate(tqdm(df.iterrows(), total=len(df),
                                              desc="Extracting AI proposals"), start=1):
        model_label = row.get('model', 'unknown')
        title_orig = str(row.get('title', ''))

        rephrased_df.at[idx, 'title'] = rephrase_title(client, title_orig)

        full_text = build_ai_full_text(row)
        standardized = extract_proposal(client, full_text)
        rephrased_df.at[idx, 'standardized_text'] = standardized if standardized else ''

        logger.info(f"  [{row_num}/{len(df)}] {model_label}: {title_orig[:60]}...")

        if checkpoint_path is not None:
            rephrased_df.to_csv(checkpoint_path, index=False)

    return rephrased_df


def rephrase_human_proposals(client: genai.Client,
                              json_path: Path) -> Dict[str, Any]:
    """Extract all human proposals into the fixed template. Returns modified data dict."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    proposals = data.get('proposals', [])
    logger.info(f"Loaded {len(proposals)} human proposals from {json_path.name}")

    rephrased_proposals = []
    for i, proposal in enumerate(tqdm(proposals, desc=f"Extracting {json_path.name}")):
        p = dict(proposal)

        p['proposal_title'] = rephrase_title(
            client, proposal.get('proposal_title', ''))

        full_text = build_human_full_text(proposal)
        standardized = extract_proposal(client, full_text)
        p['standardized_text'] = standardized if standardized else ''

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

    # ── Extract AI proposals ──────────────────────────────────────────────────
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
    logger.info(f"Saved extracted AI proposals -> {ai_out_path}")
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    # ── Extract human proposals ───────────────────────────────────────────────
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
        logger.info(f"Saved extracted human proposals -> {out_path}")

    logger.info("Done. All proposals extracted into standardized template.")


if __name__ == '__main__':
    main()
