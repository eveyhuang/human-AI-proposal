# Style-Controlled Rephrasing Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rephrase all proposals (AI + human) field-by-field into a neutral academic style using `gemini-2.0-flash`, then re-generate AI reviews and rerun all analyses in a parallel `style-controlled comparison/` folder.

**Architecture:** Three phases — (1) `src/rephrase_proposals.py` rephrases raw proposals and saves to `data/*/rephrased/`, (2) `src/generate_reviews_rephrased.py` generates AI reviews for rephrased proposals, (3) two mirrored notebooks in `style-controlled comparison/` rerun all analyses on the rephrased data.

**Tech Stack:** Python 3, `google-genai` SDK (same client as `ai_models_interface.py`), pandas, json, tqdm. Notebooks mirror `compare_proposals_baseline.ipynb` and `compare_reviews.ipynb` with path changes only.

---

## Context: Key File Paths

- **AI proposals (baseline):** `data/ai-proposals/baseline/ai_proposals_baseline_complete_20260209_205423.csv`
  - Columns: `model, title, abstract, generated_at, background_and_significance, research_questions_and_hypotheses, methods_and_approach, expected_outcomes_and_impact, budget_and_resources, proposal_generated_at`
  - 69 rows: 23 each for `gpt-5.2`, `gemini-3-pro-preview`, `claude-opus-4-5`
- **Human proposals Y1:** `data/human-proposals/human-proposals-y1.json` — 12 proposals
  - Keys: `proposal_id, proposal_title, authors, authors_departments, abstract, full_draft, proposal_status, ranking`
- **Human proposals Y2:** `data/human-proposals/human-proposals-y2.json` — 11 proposals (same keys)
- **API config:** `.env` file at project root
- **Model client:** `src/ai_models_interface.py` — use `self.gemini_client.models.generate_content(model='gemini-2.0-flash', ...)` for rephrasing
- **Existing review gen logic:** `eval_proposals_ncems_criteria.ipynb` (cells 4–16)
- **Existing AI reviews:** `data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json`
  - Top-level keys: `created_at, research_call_source, human_inputs, ai_input, evaluators, reviews`
- **Prompt templates:** `src/prompt_templates.py` — `PromptManager` class with `eval_ncems_criteria` template

---

## Task 1: Create rephrased data directories and verify API access

**Files:**
- No new files yet — just shell commands and a quick API check

**Step 1: Create output directories**

```bash
mkdir -p data/ai-proposals/rephrased
mkdir -p data/human-proposals/rephrased
mkdir -p data/embeddings/rephrased
mkdir -p data/reviews/ai_reviews
```

**Step 2: Verify Gemini API key is set**

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env', override=True)
key = os.getenv('GOOGLE_API_KEY')
print('GOOGLE_API_KEY set:', bool(key))
"
```
Expected: `GOOGLE_API_KEY set: True`

---

## Task 2: Write `src/rephrase_proposals.py`

**Files:**
- Create: `src/rephrase_proposals.py`

This script rephrases all proposals field-by-field using `gemini-2.0-flash`. Run from the **project root** directory.

**Step 1: Write the script**

```python
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


def rephrase_ai_proposals(client: genai.Client, ai_csv_path: Path) -> pd.DataFrame:
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

    for idx, row in tqdm(df.iterrows(), total=len(df),
                         desc="Rephrasing AI proposals"):
        model_label = row.get('model', 'unknown')
        title_orig = str(row.get('title', ''))

        # Rephrase title
        rephrased_df.at[idx, 'title'] = rephrase_field(
            client, title_orig, is_title=True)

        # Rephrase all text fields
        for field in text_fields:
            orig = str(row.get(field, ''))
            rephrased_df.at[idx, field] = rephrase_field(client, orig)

        logger.info(f"  [{idx+1}/{len(df)}] {model_label}: {title_orig[:60]}...")

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
    rephrased_ai_df = rephrase_ai_proposals(client, ai_csv_path)

    ai_out_path = Path('data/ai-proposals/rephrased') / f'ai_proposals_rephrased_{timestamp}.csv'
    rephrased_ai_df.to_csv(ai_out_path, index=False)
    logger.info(f"Saved rephrased AI proposals -> {ai_out_path}")

    # ── Rephrase human proposals ──────────────────────────────────────────────
    for cohort in ['y1', 'y2']:
        human_path = Path(f'data/human-proposals/human-proposals-{cohort}.json')
        if not human_path.exists():
            logger.warning(f"Not found: {human_path}, skipping.")
            continue

        rephrased_data = rephrase_human_proposals(client, human_path)
        out_path = (Path('data/human-proposals/rephrased') /
                    f'human_proposals_rephrased_{cohort}_{timestamp}.json')
        with open(out_path, 'w') as f:
            json.dump(rephrased_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved rephrased human proposals -> {out_path}")

    logger.info("Done. All rephrased proposals saved.")


if __name__ == '__main__':
    main()
```

**Step 2: Run a quick smoke test (rephrase first 2 AI proposals only)**

```bash
cd /path/to/project
python3 -c "
import os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('.env', override=True)
sys.path.insert(0, 'src')

from rephrase_proposals import rephrase_field
from google import genai

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

sample = 'We propose to study biomolecular condensates using cutting-edge ML to revolutionize our understanding.'
result = rephrase_field(client, sample)
print('Original:', sample)
print('Rephrased:', result)
assert len(result) > 10, 'Empty result'
print('SMOKE TEST PASSED')
"
```
Expected: a rephrased version in neutral academic style, no errors.

**Step 3: Commit**

```bash
git add src/rephrase_proposals.py
git commit -m "feat: add rephrase_proposals.py to standardize proposal writing style using gemini-2.0-flash"
```

---

## Task 3: Run rephrasing on all proposals

**Step 1: Run the script (takes ~15-30 min for 92 proposals × 7 fields)**

```bash
cd /path/to/project
python3 src/rephrase_proposals.py
```

Expected output ends with:
```
Saved rephrased AI proposals -> data/ai-proposals/rephrased/ai_proposals_rephrased_<timestamp>.csv
Saved rephrased human proposals -> data/human-proposals/rephrased/human_proposals_rephrased_y1_<timestamp>.json
Saved rephrased human proposals -> data/human-proposals/rephrased/human_proposals_rephrased_y2_<timestamp>.json
Done. All rephrased proposals saved.
```

**Step 2: Verify output**

```bash
python3 -c "
import json, pandas as pd
from pathlib import Path

# Check AI
ai_files = sorted(Path('data/ai-proposals/rephrased').glob('*.csv'))
df = pd.read_csv(ai_files[-1])
print('AI rephrased shape:', df.shape)
print('Models:', df['model'].value_counts().to_dict())
print('Sample title:', df.iloc[0]['title'])

# Check human Y1
h_files = sorted(Path('data/human-proposals/rephrased').glob('*y1*.json'))
with open(h_files[-1]) as f:
    data = json.load(f)
print('Human Y1 count:', len(data['proposals']))
print('Sample title:', data['proposals'][0]['proposal_title'])
"
```
Expected: 69 AI rows, 12 Y1 proposals, 11 Y2 proposals, all with rephrased titles visible.

---

## Task 4: Write `src/generate_reviews_rephrased.py`

**Files:**
- Create: `src/generate_reviews_rephrased.py`

This script is adapted from `eval_proposals_ncems_criteria.ipynb` (cells 4–16) but loads from `data/*/rephrased/`.

**Step 1: Write the script**

```python
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
import re
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
    # Find first { ... } block
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


def create_full_text_ai(row: Dict[str, Any]) -> str:
    sections = [
        ('Background and Significance', row.get('background_and_significance', '')),
        ('Research Questions and Hypotheses', row.get('research_questions_and_hypotheses', '')),
        ('Methods and Approach', row.get('methods_and_approach', '')),
        ('Expected Outcomes and Impact', row.get('expected_outcomes_and_impact', '')),
        ('Budget and Resources', row.get('budget_and_resources', '')),
    ]
    parts = []
    for header, content in sections:
        content = str(content or '').strip()
        if content:
            parts.append(f"## {header}\n{content}")
    return '\n\n'.join(parts)


def create_full_text_human(proposal: Dict[str, Any]) -> str:
    return str(proposal.get('full_draft', '') or '').strip()


def make_prompt(proposal: Dict[str, Any], research_call: str,
                prompt_manager: PromptManager) -> str:
    title = str(proposal.get('title', proposal.get('proposal_title', ''))).strip()
    abstract = str(proposal.get('abstract', '')).strip()
    full_text = str(proposal.get('_full_text', '')).strip()

    if len(full_text) > MAX_FULL_TEXT_CHARS:
        full_text = full_text[:MAX_FULL_TEXT_CHARS] + '\n[... truncated for length ...]'

    return prompt_manager.format_prompt('eval_ncems_criteria', {
        'research_call': research_call,
        'title': title,
        'abstract': abstract,
        'full_proposal': full_text,
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
            p['_full_text'] = create_full_text_human(proposal)
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
```

**Step 2: Verify script loads without import errors**

```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
import generate_reviews_rephrased
print('Import OK')
"
```
Expected: `Import OK`

**Step 3: Commit**

```bash
git add src/generate_reviews_rephrased.py
git commit -m "feat: add generate_reviews_rephrased.py to re-evaluate rephrased proposals"
```

---

## Task 5: Run review generation for rephrased proposals

**Step 1: Run the script (takes ~30–60 min for 92 proposals × 3 models)**

```bash
python3 src/generate_reviews_rephrased.py
```

Expected final line:
```
Done. 276 reviews saved to data/reviews/ai_reviews/ai_reviews_rephrased_<timestamp>.json
```
(92 proposals × 3 evaluator models = 276 reviews)

**Step 2: Verify output**

```bash
python3 -c "
import json
from pathlib import Path

files = sorted(Path('data/reviews/ai_reviews').glob('ai_reviews_rephrased_*.json'))
with open(files[-1]) as f:
    data = json.load(f)

reviews = data['reviews']
print('Total reviews:', len(reviews))

import pandas as pd
df = pd.DataFrame(reviews)
print('By evaluator:', df['evaluator'].value_counts().to_dict())
print('By author:', df['author'].value_counts().to_dict())
print('Parse errors:', df['parse_error'].notna().sum())
"
```
Expected: 276 total reviews, ~92 per evaluator, parse errors < 5%.

---

## Task 6: Create `style-controlled comparison/compare_proposals_rephrased.ipynb`

**Files:**
- Create: `style-controlled comparison/compare_proposals_rephrased.ipynb`

This notebook is a copy of `compare_proposals_baseline.ipynb` with the following changes:
1. Title changed to "Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)"
2. Data loading cell (Cell 8) updated to load from `data/*/rephrased/`
3. Embeddings save/load path updated to `data/embeddings/rephrased/`
4. All other analysis cells are identical

**Step 1: Copy and patch the notebook**

```python
# Run this as a Python script or in a terminal Python session
import json
from pathlib import Path
import copy

# Load baseline notebook
with open('compare_proposals_baseline.ipynb') as f:
    nb = json.load(f)

new_nb = copy.deepcopy(nb)

# 1. Update title cell (Cell 0)
new_nb['cells'][0]['source'] = [
    "# Compare AI vs Human Research Proposals — Style-Controlled (Rephrased)\n",
    "\n",
    "This notebook mirrors `compare_proposals_baseline.ipynb` but uses proposals rephrased by `gemini-2.0-flash` into a standardized neutral academic style, removing stylistic fingerprints before analysis.\n",
    "\n",
    "**Data sources:**\n",
    "- `data/ai-proposals/rephrased/ai_proposals_rephrased_*.csv`\n",
    "- `data/human-proposals/rephrased/human_proposals_rephrased_y*.json`\n",
    "\n",
    "All analyses (diversity, novelty, thematic, style baseline) are identical to the baseline notebook."
]

# 2. Update data loading cell (Cell 8) — load from rephrased directories
for i, cell in enumerate(new_nb['cells']):
    src = ''.join(cell['source'])
    if 'data/ai-proposals/baseline' in src and 'ai_proposals_baseline_complete' in src:
        new_src = src.replace(
            "ai_proposals_path = Path('data/ai-proposals/baseline')",
            "ai_proposals_path = Path('data/ai-proposals/rephrased')"
        ).replace(
            "ai_files = sorted(ai_proposals_path.glob('ai_proposals_baseline_complete_*.csv'))",
            "ai_files = sorted(ai_proposals_path.glob('ai_proposals_rephrased_*.csv'))"
        ).replace(
            "ai_proposals_path = Path('data/human-proposals')",
            "ai_proposals_path = Path('data/human-proposals/rephrased')"
        )
        # Also update human proposals path
        new_src = new_src.replace(
            "human_proposals_path = Path('data/human-proposals')",
            "human_proposals_path = Path('data/human-proposals/rephrased')"
        )
        new_nb['cells'][i]['source'] = [new_src]
        print(f"Updated data loading cell {i}")

# 3. Update embeddings save/load path
for i, cell in enumerate(new_nb['cells']):
    src = ''.join(cell['source'])
    if 'data/embeddings' in src and 'embeddings_dir' in src:
        new_src = src.replace(
            "embeddings_dir = Path('data/embeddings')",
            "embeddings_dir = Path('data/embeddings/rephrased')"
        )
        new_nb['cells'][i]['source'] = [new_src]
        print(f"Updated embeddings dir cell {i}")

# 4. Update any hardcoded embedding file paths
for i, cell in enumerate(new_nb['cells']):
    src = ''.join(cell['source'])
    if "'data/embeddings'" in src and 'rephrased' not in src:
        new_src = src.replace("'data/embeddings'", "'data/embeddings/rephrased'")
        new_nb['cells'][i]['source'] = [new_src]
        print(f"Updated hardcoded embeddings path in cell {i}")

# Clear all outputs
for cell in new_nb['cells']:
    if cell['cell_type'] == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None

# Save
out_path = Path('style-controlled comparison/compare_proposals_rephrased.ipynb')
with open(out_path, 'w') as f:
    json.dump(new_nb, f, indent=1)

print(f"\nSaved to {out_path}")
```

Save this script as `src/create_rephrased_notebooks.py` and run it:

```bash
python3 src/create_rephrased_notebooks.py
```

**Step 2: Manually verify the notebook opened correctly**

Open `style-controlled comparison/compare_proposals_rephrased.ipynb` in Jupyter and confirm:
- Title mentions "Rephrased"
- Cell 8 loads from `data/ai-proposals/rephrased/`
- Embeddings path is `data/embeddings/rephrased`

**Step 3: Commit**

```bash
git add "style-controlled comparison/compare_proposals_rephrased.ipynb" src/create_rephrased_notebooks.py
git commit -m "feat: add compare_proposals_rephrased.ipynb for style-controlled analysis"
```

---

## Task 7: Create `style-controlled comparison/compare_reviews_rephrased.ipynb`

**Files:**
- Create: `style-controlled comparison/compare_reviews_rephrased.ipynb`

This notebook is a copy of `compare_reviews.ipynb` with the review JSON path updated to load from `data/reviews/ai_reviews/ai_reviews_rephrased_*.json`.

**Step 1: Add review notebook creation to `src/create_rephrased_notebooks.py`**

Append to the script:

```python
# ── compare_reviews_rephrased.ipynb ───────────────────────────────────────────
with open('compare_reviews.ipynb') as f:
    nb_reviews = json.load(f)

new_nb_reviews = copy.deepcopy(nb_reviews)

# Update title
new_nb_reviews['cells'][0]['source'] = [
    "# PART IV QUALITY — Compare Human and AI Reviews (Style-Controlled / Rephrased)\n",
    "\n",
    "This notebook mirrors `compare_reviews.ipynb` but uses AI reviews generated on rephrased proposals.\n",
    "\n",
    "**Review data:** `data/reviews/ai_reviews/ai_reviews_rephrased_*.json`\n",
    "**Proposal data:** `data/*/rephrased/`"
]

# Update review file path reference
for i, cell in enumerate(new_nb_reviews['cells']):
    src = ''.join(cell['source'])
    if 'ai_reviews_ncems_criteria' in src:
        new_src = src.replace(
            'ai_reviews_ncems_criteria_20260223_153411.json',
            'REPHRASED_REVIEWS_PLACEHOLDER'
        )
        # Use glob to find the most recent rephrased review
        new_src = new_src.replace(
            'REPHRASED_REVIEWS_PLACEHOLDER',
            "ai_reviews_rephrased_*.json'\n# (uses most recent rephrased review file)"
        )
        # Simpler: replace hardcoded path with glob pattern
        new_src = src.replace(
            "Path('data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json')",
            "sorted(Path('data/reviews/ai_reviews').glob('ai_reviews_rephrased_*.json'))[-1]"
        ).replace(
            "'data/reviews/ai_reviews/ai_reviews_ncems_criteria_20260223_153411.json'",
            "str(sorted(Path('data/reviews/ai_reviews').glob('ai_reviews_rephrased_*.json'))[-1])"
        )
        new_nb_reviews['cells'][i]['source'] = [new_src]
        print(f"Updated reviews path in cell {i}")

# Clear outputs
for cell in new_nb_reviews['cells']:
    if cell['cell_type'] == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None

out_reviews_path = Path('style-controlled comparison/compare_reviews_rephrased.ipynb')
with open(out_reviews_path, 'w') as f:
    json.dump(new_nb_reviews, f, indent=1)

print(f"Saved to {out_reviews_path}")
```

**Step 2: Re-run the full script**

```bash
python3 src/create_rephrased_notebooks.py
```

**Step 3: Verify the compare_reviews notebook**

Open `style-controlled comparison/compare_reviews_rephrased.ipynb`. Confirm:
- Title mentions "Rephrased"
- Review loading cell uses `ai_reviews_rephrased_*.json`

**Step 4: Commit**

```bash
git add "style-controlled comparison/compare_reviews_rephrased.ipynb" src/create_rephrased_notebooks.py
git commit -m "feat: add compare_reviews_rephrased.ipynb for style-controlled review analysis"
```

---

## Task 8: Run the analysis notebooks

**Step 1: Run compare_proposals_rephrased.ipynb**

Open in Jupyter and run all cells. Confirm:
- Embeddings generate without errors
- All diversity/novelty/cluster/style analyses run
- Figures render correctly

**Step 2: Run compare_reviews_rephrased.ipynb**

Open in Jupyter and run all cells. Confirm:
- Reviews load correctly
- All quality comparison analyses run

**Step 3: Final commit**

```bash
git add data/embeddings/rephrased/ "style-controlled comparison/"
git commit -m "results: run style-controlled analyses on rephrased proposals"
```

---

## Summary of New Files

| Path | Purpose |
|------|---------|
| `src/rephrase_proposals.py` | Rephrase all proposals using gemini-2.0-flash |
| `src/generate_reviews_rephrased.py` | Re-generate AI reviews for rephrased proposals |
| `src/create_rephrased_notebooks.py` | Script to generate the two analysis notebooks |
| `style-controlled comparison/compare_proposals_rephrased.ipynb` | Diversity/novelty/cluster analysis on rephrased proposals |
| `style-controlled comparison/compare_reviews_rephrased.ipynb` | Quality/review analysis on rephrased proposals |
| `data/ai-proposals/rephrased/ai_proposals_rephrased_<ts>.csv` | Rephrased AI proposals |
| `data/human-proposals/rephrased/human_proposals_rephrased_y1_<ts>.json` | Rephrased human Y1 |
| `data/human-proposals/rephrased/human_proposals_rephrased_y2_<ts>.json` | Rephrased human Y2 |
| `data/reviews/ai_reviews/ai_reviews_rephrased_<ts>.json` | Reviews for rephrased proposals |
| `data/embeddings/rephrased/` | BioLinkBERT embeddings of rephrased proposals |
