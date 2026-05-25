"""
Rephrase human and AI proposal reviews into a consistent style using a single API call per review.

This script extracts three fields for each review:
  - rephrased_review
  - strengths
  - weakness

Usage (run from project root):
    python src/rephrase_reviews.py

Inputs (default):
    data/reviews/human_reviews/human_reviews_human-y2.xlsx
    data/reviews/human_reviews/human_reviews_human-y1.xlsx
    data/reviews/ai_reviews/minimal/ncems_criteria

Outputs (overwritten each run, no timestamp files):
    data/reviews/human_reviews/rephrased/human_reviews_human-y2_rephrased.csv
    data/reviews/human_reviews/rephrased/human_reviews_human-y1_rephrased.csv
    data/reviews/ai_reviews/minimal/ncems_criteria/rephrased/ncems_reviews_rephrased.json
"""

import argparse
import json
import logging
import os
import requests
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

try:
    from google import genai
    HAS_GOOGLE_GENAI = True
except ImportError:
    import google.generativeai as genai
    HAS_GOOGLE_GENAI = False

# ─── Setup ────────────────────────────────────────────────────────────────────
load_dotenv(Path('.env'), override=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

GEMINI_MODEL = 'gemini-2.5-flash-lite'
RETRY_DELAYS = [5, 15, 30]
REST_MODEL_FALLBACKS = ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-flash-preview']

ONE_STEP_REVIEW_SYSTEM = """You are a scientific review editor.

You will receive one proposal review text. Rewrite it in neutral, consistent style and extract strengths and weaknesses.

Return ONLY a valid JSON object with exactly these keys:
{
  "rephrased_review": "...",
  "strengths": "...",
  "weakness": "..."
}

Rules:
- Keep scientific meaning unchanged.
- Use concise, neutral language.
- `rephrased_review`: 2-4 sentences summarizing the review's overall evaluation.
- `strengths`: 1-3 sentences listing key positive points.
- `weakness`: 1-3 sentences listing key concerns/limitations.
- If strengths or weaknesses are missing, write "Not specified." for that field.
- Output JSON only. No markdown, no prose outside JSON.
"""


# ─── Shared helpers ───────────────────────────────────────────────────────────
def _build_client(api_key: str) -> Any:
    if HAS_GOOGLE_GENAI:
        return genai.Client(api_key=api_key)
    return {'api_key': api_key}


def _call_gemini(client: Any, prompt: str,
                 label: str, model: str,
                 max_retries: int = 3) -> Optional[str]:
    for attempt, delay in enumerate([0] + RETRY_DELAYS[:max_retries - 1]):
        if delay:
            logger.info(f"Retrying {label} in {delay}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        try:
            if HAS_GOOGLE_GENAI:
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    config={'temperature': 0}
                )
                result = (response.text or '').strip()
            else:
                api_key = client['api_key']
                primary = str(model).replace('models/', '')
                model_candidates = [primary] + [m for m in REST_MODEL_FALLBACKS if m != primary]
                result = ''

                payload = {
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {'temperature': 0},
                }

                last_err: Optional[Exception] = None
                for model_name in model_candidates:
                    url = (
                        f"https://generativelanguage.googleapis.com/v1beta/models/"
                        f"{model_name}:generateContent?key={api_key}"
                    )
                    try:
                        response = requests.post(url, json=payload, timeout=120)
                        response.raise_for_status()
                        data = response.json()
                        candidates = data.get('candidates', [])
                        if candidates:
                            content = candidates[0].get('content', {})
                            parts = content.get('parts', [])
                            texts = [p.get('text', '') for p in parts if isinstance(p, dict)]
                            result = '\n'.join([t for t in texts if t]).strip()
                        if result:
                            if model_name != primary:
                                logger.info(f"{label}: used fallback REST model '{model_name}'")
                            break
                    except Exception as model_err:
                        last_err = model_err
                        continue

                if not result and last_err is not None:
                    raise last_err

            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1].strip()
            return result if result else None
        except Exception as e:
            logger.warning(f"{label} error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"{label}: all retries failed")
                return None
    return None


def extract_first_json_object(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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


def _is_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and pd.isna(v):
        return True
    s = str(v).strip()
    return s == '' or s.lower() in {'nan', 'none', 'null'}


def _clean(v: Any) -> str:
    return '' if _is_missing(v) else str(v).strip()


def rephrase_review(client: Any, review_text: str,
                    model: str, max_retries: int = 3) -> Dict[str, str]:
    out = {
        'rephrased_review': '',
        'strengths': '',
        'weakness': '',
    }

    if not review_text or not review_text.strip():
        return out

    prompt = (
        f"{ONE_STEP_REVIEW_SYSTEM}\n\n"
        f"---\nREVIEW TEXT:\n{review_text.strip()}\n---\nJSON:"
    )

    response_text = _call_gemini(
        client,
        prompt,
        label='rephrase_review',
        model=model,
        max_retries=max_retries,
    )
    if not response_text:
        return out

    parsed, err = extract_first_json_object(response_text)
    if err or not isinstance(parsed, dict):
        logger.warning(f"Failed to parse review JSON output: {err}")
        return out

    out['rephrased_review'] = _clean(parsed.get('rephrased_review', ''))
    out['strengths'] = _clean(parsed.get('strengths', ''))
    out['weakness'] = _clean(parsed.get('weakness', ''))
    return out


# ─── Human review extraction ──────────────────────────────────────────────────
def build_human_review_text_sheet1(row: pd.Series) -> str:
    parts: List[str] = []

    merit_j = _clean(row.get('scientific_merit_and_innovation_justification', ''))
    merit_s = _clean(row.get('scientific_merit_and_innovation_score', ''))
    feas_j = _clean(row.get('feasibility_justification', ''))
    feas_s = _clean(row.get('feasibility_score', ''))
    data_j = _clean(row.get('data_sources_and_limitations_justification', ''))
    data_s = _clean(row.get('data_sources_and_limitations_score', ''))
    open_j = _clean(row.get('open_science_compliance_justification', ''))
    open_s = _clean(row.get('open_science_compliance_score', ''))
    overall_j = _clean(row.get('overall_rating_summary', ''))
    overall_s = _clean(row.get('overall_rating_score', ''))

    if merit_j:
        parts.append(f"[Scientific Merit and Innovation | Score: {merit_s or 'Not provided'}]\n{merit_j}")
    if feas_j:
        parts.append(f"[Feasibility | Score: {feas_s or 'Not provided'}]\n{feas_j}")
    if data_j:
        parts.append(f"[Data Sources and Limitations | Score: {data_s or 'Not provided'}]\n{data_j}")
    if open_j:
        parts.append(f"[Open Science Compliance | Score: {open_s or 'Not provided'}]\n{open_j}")
    if overall_j:
        parts.append(f"[Overall Rating | Score: {overall_s or 'Not provided'}]\n{overall_j}")

    return '\n\n'.join(parts)


def build_human_review_text_generic(row: pd.Series, columns: List[str]) -> str:
    parts: List[str] = []
    for c in columns:
        v = _clean(row.get(c, ''))
        if v:
            parts.append(f"[{c}]\n{v}")
    return '\n\n'.join(parts)


def rephrase_human_workbook(client: Any, workbook_path: Path,
                            model: str,
                            max_retries: int = 3,
                            limit: Optional[int] = None) -> pd.DataFrame:
    xls = pd.ExcelFile(workbook_path)
    all_rows: List[Dict[str, Any]] = []

    if 'Sheet1' in xls.sheet_names:
        df1 = xls.parse('Sheet1')
        logger.info(f"Loaded {len(df1)} rows from {workbook_path.name} [Sheet1]")
        for idx, row in df1.iterrows():
            review_text = build_human_review_text_sheet1(row)
            if not review_text:
                continue
            rec = row.to_dict()
            rec['_source_file'] = workbook_path.name
            rec['_source_sheet'] = 'Sheet1'
            rec['_row_index'] = int(idx)
            rec['_raw_review_text'] = review_text
            all_rows.append(rec)

    for sheet in xls.sheet_names:
        if sheet == 'Sheet1':
            continue
        df = xls.parse(sheet)
        review_cols = [c for c in df.columns if 'review' in str(c).lower()]
        if not review_cols:
            continue

        logger.info(f"Loaded {len(df)} rows from {workbook_path.name} [{sheet}] with review columns: {review_cols}")
        for idx, row in df.iterrows():
            review_text = build_human_review_text_generic(row, review_cols)
            if not review_text:
                continue
            rec = row.to_dict()
            rec['_source_file'] = workbook_path.name
            rec['_source_sheet'] = sheet
            rec['_row_index'] = int(idx)
            rec['_raw_review_text'] = review_text
            all_rows.append(rec)

    if limit is not None:
        all_rows = all_rows[:limit]

    out_rows: List[Dict[str, Any]] = []
    for row in tqdm(all_rows, desc=f"Rephrasing human reviews: {workbook_path.name}"):
        r = rephrase_review(
            client,
            review_text=row.get('_raw_review_text', ''),
            model=model,
            max_retries=max_retries,
        )
        merged = dict(row)
        merged.update(r)
        out_rows.append(merged)

    return pd.DataFrame(out_rows)


# ─── AI review extraction ─────────────────────────────────────────────────────
def _safe_score(val: Any) -> str:
    s = _clean(val)
    return s if s else 'Not provided'


def _get_ai_eval_obj(review: Dict[str, Any]) -> Dict[str, Any]:
    ev = review.get('evaluations', {})
    if isinstance(ev, dict) and 'evaluation' in ev and isinstance(ev['evaluation'], dict):
        return ev['evaluation']

    raw = _clean(review.get('raw_response', ''))
    parsed, _ = extract_first_json_object(raw)
    if isinstance(parsed, dict):
        maybe = parsed.get('evaluation', parsed)
        if isinstance(maybe, dict):
            return maybe

    return {}


def build_ai_review_text(review: Dict[str, Any]) -> str:
    ev = _get_ai_eval_obj(review)
    parts: List[str] = []

    criteria = ev.get('criteria_scores', []) if isinstance(ev, dict) else []
    if isinstance(criteria, list):
        for cat in criteria:
            if not isinstance(cat, dict):
                continue
            cat_name = _clean(cat.get('category', 'Unnamed category'))
            cat_avg = _safe_score(cat.get('category_average', ''))
            parts.append(f"[Category: {cat_name} | Average: {cat_avg}]")
            subcriteria = cat.get('subcriteria', [])
            if isinstance(subcriteria, list):
                for sc in subcriteria:
                    if not isinstance(sc, dict):
                        continue
                    crit = _clean(sc.get('criterion', 'Unnamed criterion'))
                    score = _safe_score(sc.get('score', ''))
                    just = _clean(sc.get('justification', ''))
                    if just:
                        parts.append(f"- {crit} | Score: {score}\n{just}")

    overall = ev.get('overall_rating', {}) if isinstance(ev, dict) else {}
    if isinstance(overall, dict):
        num = _safe_score(overall.get('final_numeric_score', ''))
        narrative = _clean(overall.get('narrative_summary', ''))
        if narrative:
            parts.append(f"[Overall Rating | Score: {num}]\n{narrative}")

    if not parts:
        fallback = _clean(review.get('raw_response', ''))
        if fallback:
            parts.append(f"[Raw Review Text]\n{fallback}")

    return '\n\n'.join(parts)


def _latest_json_in_dir(path: Path) -> Path:
    json_files = sorted(path.glob('*.json'))
    if not json_files:
        raise FileNotFoundError(f'No JSON files found in {path}')
    return json_files[-1]


def rephrase_ai_reviews(client: Any, ai_json_path_or_dir: Path,
                       model: str,
                       max_retries: int = 3,
                       limit: Optional[int] = None) -> Dict[str, Any]:
    json_path = ai_json_path_or_dir
    if ai_json_path_or_dir.is_dir():
        json_path = _latest_json_in_dir(ai_json_path_or_dir)

    with open(json_path, 'r') as f:
        data = json.load(f)

    reviews = data.get('reviews', []) if isinstance(data, dict) else []
    if limit is not None:
        reviews = reviews[:limit]

    logger.info(f"Loaded {len(reviews)} AI reviews from {json_path}")

    out_reviews: List[Dict[str, Any]] = []
    for review in tqdm(reviews, desc='Rephrasing AI reviews'):
        r = dict(review)
        raw_text = build_ai_review_text(r)
        r.update(rephrase_review(client, raw_text, model=model, max_retries=max_retries))
        out_reviews.append(r)

    out_data = dict(data)
    out_data['source_file'] = str(json_path)
    out_data['rephrasing_model'] = model
    out_data['reviews'] = out_reviews
    return out_data


# ─── CLI ──────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Rephrase human and AI reviews into consistent style with one API call per review.'
    )
    parser.add_argument(
        '--human-files',
        nargs='*',
        default=[
            'data/reviews/human_reviews/human_reviews_human-y2.xlsx',
            'data/reviews/human_reviews/human_reviews_human-y1.xlsx',
        ],
        help='Human review workbook paths (.xlsx).',
    )
    parser.add_argument(
        '--ai-reviews-path',
        default='data/reviews/ai_reviews/minimal/ncems_criteria',
        help='Path to AI review JSON file or directory containing JSON files.',
    )
    parser.add_argument('--model', default=GEMINI_MODEL, help='Gemini model name to use.')
    parser.add_argument('--max-retries', type=int, default=3, help='LLM call retries on transient errors.')
    parser.add_argument('--limit', type=int, default=None,
                        help='Optional row limit per source for quick testing.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error('GOOGLE_API_KEY not set. Check your .env file.')
        sys.exit(1)

    client = _build_client(api_key)

    # Human reviews: one stable output file per workbook.
    human_out_dir = Path('data/reviews/human_reviews/rephrased')
    human_out_dir.mkdir(parents=True, exist_ok=True)

    for human_file in args.human_files:
        path = Path(human_file)
        if not path.exists():
            logger.warning(f'Human file not found, skipping: {path}')
            continue

        rephrased_df = rephrase_human_workbook(
            client=client,
            workbook_path=path,
            model=args.model,
            max_retries=args.max_retries,
            limit=args.limit,
        )

        out_name = f"{path.stem}_rephrased.csv"
        out_path = human_out_dir / out_name
        rephrased_df.to_csv(out_path, index=False)
        logger.info(f'Saved rephrased human reviews -> {out_path}')

    # AI reviews: one stable output JSON.
    ai_path = Path(args.ai_reviews_path)
    if not ai_path.exists():
        logger.warning(f'AI reviews path not found, skipping: {ai_path}')
    else:
        rephrased_ai = rephrase_ai_reviews(
            client=client,
            ai_json_path_or_dir=ai_path,
            model=args.model,
            max_retries=args.max_retries,
            limit=args.limit,
        )

        ai_out_dir = Path('data/reviews/ai_reviews/minimal/ncems_criteria/rephrased')
        ai_out_dir.mkdir(parents=True, exist_ok=True)
        ai_out_path = ai_out_dir / 'ncems_reviews_rephrased.json'
        with open(ai_out_path, 'w') as f:
            json.dump(rephrased_ai, f, indent=2, ensure_ascii=False)
        logger.info(f'Saved rephrased AI reviews -> {ai_out_path}')

    logger.info('Done. Reviews rephrased using one-step extraction.')


if __name__ == '__main__':
    main()
