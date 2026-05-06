import argparse
import json
from pathlib import Path

import pandas as pd


NCEMS_FIELD_MAP = {
    'Relevance to Emergent Phenomena': 'relevance_to_emergent_phenomena',
    'Novelty & Significance': 'novelty_and_significance',
    'Rigor of Approach': 'rigor_of_approach',
    'Scope & Timeline': 'scope_and_timeline',
    'Synthesis Focus': 'synthesis_focus',
    'Data Identification': 'data_identification',
    'Open Science Commitment': 'open_science_commitment',
}


def build_review_scores(condition: str) -> pd.DataFrame:
    ncems_dir = Path(f'data/reviews/ai_reviews/{condition}/ncems_criteria')
    ncems_files = sorted(ncems_dir.glob('ncems_reviews_*.json'))
    if not ncems_files:
        raise FileNotFoundError(f'No NCEMS review files found in {ncems_dir}')

    with open(ncems_files[-1], 'r') as f:
        payload = json.load(f)

    rows = []
    for review in payload.get('reviews', []):
        evaluation = (review.get('evaluations') or {}).get('evaluation', {})
        if not isinstance(evaluation, dict):
            continue

        row = {
            'title': review.get('title', ''),
            'author': review.get('author', ''),
        }
        for category in evaluation.get('criteria_scores', []) or []:
            for subcriterion in category.get('subcriteria', []) or []:
                field = NCEMS_FIELD_MAP.get(subcriterion.get('criterion'))
                if field:
                    row[field] = subcriterion.get('score')
        rows.append(row)

    df = pd.DataFrame(rows)
    score_cols = ['title', 'author', *NCEMS_FIELD_MAP.values()]
    for col in score_cols:
        if col not in df.columns:
            df[col] = pd.NA

    return (
        df[score_cols]
        .groupby(['title', 'author'], as_index=False)
        .mean(numeric_only=True)
        .sort_values(['title', 'author'])
        .reset_index(drop=True)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Build review_scores_wide.csv from latest NCEMS review JSON.')
    parser.add_argument('--condition', required=True, help='Experimental condition, e.g. minimal')
    args = parser.parse_args()

    df = build_review_scores(args.condition)
    output_dir = Path(f'results/tables/rephrased/{args.condition}')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'review_scores_wide.csv'
    df.to_csv(output_path, index=False)
    print(f'Saved {len(df)} rows to {output_path}')


if __name__ == '__main__':
    main()
