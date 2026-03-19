"""
Summarize all AI and human proposals into a fixed evaluation-aligned template,
neutralizing stylistic and structural differences while preserving scientific content.

Uses a two-step pipeline to maximize style removal:
  Step 1 (SUMMARIZE): Extract core semantic facts from the original text,
          stripping all stylistic patterns (sentence rhythms, punctuation habits,
          vocabulary choices, rhetorical framing) into a compact neutral summary.
  Step 2 (FILL): Generate the standardized template from the summary only,
          so template prose is driven by formatting rules rather than source style.

The template mirrors the NCEMS call for proposals and evaluation criteria:
  Section 1 – Scientific Background & Research Question  
  Section 2 – Methodology & Analytical Approach          
  Section 3 – Data Sources & Synthesis Plan              
  Section 4 – Feasibility & Timeline                     
  Section 5 – Open Science & Team Composition            
  
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

# ─── Two-step summarize → fill pipeline ───────────────────────────────────────
# Step 1: Extract semantic facts from the original, stripping all style.
# Step 2: Fill the fixed template from the summary only, so output prose is
#         governed by formatting rules rather than the source's stylistic patterns.

SUMMARIZE_SYSTEM = """You are a scientific content extractor. Read the research proposal and extract its core semantic content as a compact, neutral summary.

Your ONLY goal is to capture what the proposal says — its scientific facts, methods, data, and plans — while stripping every stylistic element: sentence rhythms, punctuation habits, vocabulary preferences, hedging patterns, rhetorical framing, and evaluative language.

Extract facts for each of the following categories. Write each as a plain declarative statement in your own neutral words — do not quote or echo the source phrasing. If a category is not addressed, write "Not specified."

CATEGORIES:
1. Research domain and the specific phenomenon or system being studied
2. The scientific gap or open question being addressed
3. Current state of knowledge: what is known and where understanding is incomplete
4. Primary research question or objective
5. Why this research question is significant or novel for the field
6. Overall study design and analytical strategy
7. Key methods, models, tools, or algorithms to be used
8. How results will be validated or benchmarked
9. Datasets or databases to be used (include names if mentioned)
10. How the datasets will be integrated or synthesized
11. Known data limitations and how they will be addressed
12. Project milestones and overall timeline
13. Why multi-lab or cross-disciplinary collaboration is needed
14. Plans for open science: sharing of data, code, and findings
15. Team composition: disciplines, career stages, training opportunities

Output ONLY the numbered fact statements. No preamble, no commentary, no section headers."""


FILL_SYSTEM = """You are a scientific writer. You will be given a numbered list of semantic facts extracted from a research proposal. Use ONLY these facts to write the standardized template below.

Your task is to compose fresh, uniform prose from the facts — do not echo the wording of the facts themselves. The output style must follow the rules below exactly, regardless of how the facts are phrased.

TEMPLATE:

SCIENTIFIC BACKGROUND AND RESEARCH QUESTION
(Write exactly 3 sentences.)
Sentence 1: State the research domain, the specific phenomenon being studied, and the key scientific gap or open question. (Draw from facts 1, 2.)
Sentence 2: Describe current state of knowledge — what is known and where understanding is incomplete. (Draw from fact 3.)
Sentence 3: State the primary research question and explain why it is significant or novel. (Draw from facts 4, 5.)

METHODOLOGY AND ANALYTICAL APPROACH
(Write exactly 3 sentences.)
Sentence 1: Describe the overall study design and core analytical strategy. (Draw from fact 6.)
Sentence 2: Specify the key methods, models, tools, or algorithms to be applied. (Draw from fact 7.)
Sentence 3: Explain how results will be validated or benchmarked. (Draw from fact 8.)

DATA SOURCES AND SYNTHESIS PLAN
(Write exactly 3 sentences.)
Sentence 1: Identify the datasets or databases to be used, including names and sources where available. (Draw from fact 9.)
Sentence 2: Describe how distinct datasets will be integrated to address the research question. (Draw from fact 10.)
Sentence 3: Acknowledge known data limitations and explain how they will be mitigated. (Draw from fact 11.)

FEASIBILITY AND TIMELINE
(Write exactly 2 sentences.)
Sentence 1: Summarize the proposed milestones and overall timeline. (Draw from fact 12.)
Sentence 2: Explain why the project scope requires multi-lab or cross-disciplinary collaboration. (Draw from fact 13.)

OPEN SCIENCE AND TEAM COMPOSITION
(Write exactly 2 sentences.)
Sentence 1: Describe plans for making findings, code, and data publicly available. (Draw from fact 14.)
Sentence 2: Characterize the team composition, including disciplines, career stages, and training opportunities. (Draw from fact 15.)

STYLE RULES — follow these exactly:
- Third-person neutral register: "This project...", "The proposed study...", "The team...". No first person ("I", "we").
- Declarative statements only. Do not add hedging ("may", "suggests", "is expected to") unless a fact explicitly states uncertainty.
- Average sentence length of 18–22 words. One main clause with at most one subordinate clause. No stacked qualifications.
- Use the same term for the same concept throughout. Do not introduce synonyms for technical terms.
- Full prepositional phrases, not noun stacks: "analysis of protein dynamics" not "protein dynamics analysis". Include articles and prepositions naturally.
- Minimize commas. No serial/Oxford commas — restructure as prose with "and" or write separate sentences. Use a comma only to separate a subordinate clause from a main clause.
- Use parentheses for acronym definitions on first use and brief examples where natural (e.g., "machine learning (ML)").
- No bullet points, numbered lists, colons introducing items, or extra line breaks within a section. Flowing prose only.
- Adhere strictly to the sentence count for each section. Do not add, split, or merge sentences.
- If a fact is "Not specified", write one sentence stating that the proposal does not address this information.
- Output ONLY the filled template with the five section headings and their sentences. No preamble, no commentary."""


TITLE_SYSTEM = """You are a scientific editor. Rephrase this research proposal title into standard academic title format. Rules:
1. Preserve ALL scientific content and meaning.
2. Use noun-phrase format (no verbs like "investigating" at the start unless natural).
3. Title Case capitalization.
4. No colons unless truly needed for subtitle.
5. 8–15 words preferred.
6. Return ONLY the rephrased title with no preamble."""


def _call_gemini(client: genai.Client, prompt: str,
                 label: str, max_retries: int = 3) -> Optional[str]:
    """Shared Gemini call with retry logic. Returns stripped text or None on failure."""
    for attempt, delay in enumerate([0] + RETRY_DELAYS[:max_retries - 1]):
        if delay:
            logger.info(f"Retrying {label} in {delay}s (attempt {attempt + 1}/{max_retries})")
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
            logger.warning(f"{label} error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"{label}: all retries failed")
                return None
    return None


def summarize_proposal(client: genai.Client, full_text: str,
                       max_retries: int = 3) -> Optional[str]:
    """Step 1: Extract semantic facts from the original text, stripping all style."""
    if not full_text or not full_text.strip():
        return None
    prompt = (f"{SUMMARIZE_SYSTEM}\n\n"
              f"---\nPROPOSAL TEXT:\n{full_text.strip()}\n---\nEXTRACTED FACTS:")
    return _call_gemini(client, prompt, label="summarize", max_retries=max_retries)


def fill_template(client: genai.Client, summary: str,
                  max_retries: int = 3) -> Optional[str]:
    """Step 2: Generate the standardized template from the style-free summary."""
    if not summary or not summary.strip():
        return None
    prompt = (f"{FILL_SYSTEM}\n\n"
              f"---\nEXTRACTED FACTS:\n{summary.strip()}\n---\nFILLED TEMPLATE:")
    return _call_gemini(client, prompt, label="fill_template", max_retries=max_retries)


def extract_proposal(client: genai.Client, full_text: str,
                     max_retries: int = 3) -> Optional[str]:
    """Two-step pipeline: summarize to strip style, then fill the fixed template."""
    summary = summarize_proposal(client, full_text, max_retries=max_retries)
    if not summary:
        logger.warning("Summarization step returned None; skipping template fill.")
        return None
    return fill_template(client, summary, max_retries=max_retries)


def rephrase_title(client: genai.Client, title: str,
                   max_retries: int = 3) -> str:
    """Rephrase a proposal title. Returns original on failure."""
    if not title or not title.strip():
        return title
    prompt = f"{TITLE_SYSTEM}\n\n---\nORIGINAL TITLE:\n{title.strip()}\n---\nREPHRASED TITLE:"
    result = _call_gemini(client, prompt, label="rephrase_title", max_retries=max_retries)
    return result if result else title


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
    ai_baseline_dir = Path('data/ai-proposals/minimal')
    ai_csv_files = sorted(ai_baseline_dir.glob('ai_proposals_minimal_complete_*.csv'))
    if not ai_csv_files:
        logger.error("No AI proposal CSV found in data/ai-proposals/baseline/")
        sys.exit(1)

    ai_csv_path = ai_csv_files[-1]  # most recent
    ai_out_path = Path('data/ai-proposals/rephrased/v3-minimal') / f'ai_proposals_minimal_rephrased_{timestamp}.csv'
    checkpoint_path = ai_out_path.with_suffix('.csv.tmp')
    rephrased_ai_df = rephrase_ai_proposals(client, ai_csv_path,
                                            checkpoint_path=checkpoint_path)

    ai_out_path.parent.mkdir(parents=True, exist_ok=True)
    rephrased_ai_df.to_csv(ai_out_path, index=False)
    logger.info(f"Saved extracted AI proposals -> {ai_out_path}")
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    # ── Extract human proposals ───────────────────────────────────────────────
    # for cohort in ['y1', 'y2']:
    #     human_path = Path(f'data/human-proposals/human-proposals-{cohort}.json')
    #     if not human_path.exists():
    #         logger.warning(f"Not found: {human_path}, skipping.")
    #         continue

    #     rephrased_data = rephrase_human_proposals(client, human_path)
    #     out_path = (Path('data/human-proposals/rephrased') /
    #                 f'human_proposals_rephrased_{cohort}_{timestamp}.json')
    #     out_path.parent.mkdir(parents=True, exist_ok=True)
    #     with open(out_path, 'w') as f:
    #         json.dump(rephrased_data, f, indent=2, ensure_ascii=False)
    #     logger.info(f"Saved extracted human proposals -> {out_path}")

    # logger.info("Done. All proposals extracted into standardized template.")


if __name__ == '__main__':
    main()
