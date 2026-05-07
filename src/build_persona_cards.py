import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_models_interface import AIModelsInterface


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

RETRY_DELAYS = [5, 15, 30]


PERSONA_CARD_PROMPT = """You are building a factual scientific persona card for a research team.

You will be given:
1. A team of authors
2. A set of publications for each author

Your job is to summarize only what is supported by the publications. Focus on scientific content and perspectives, not personality.

REQUIREMENTS:
- Be expansive and faithful to the publication contents.
- Do not propose research ideas.
- Do not suggest future directions.
- Do not infer personal traits, motivations, or writing style.
- Do not mention funding fit or likely proposal strategies.
- Stay close to the actual topics, systems, methods, and data in the papers.
- If methods or data are not clearly described in a paper, say "Not clearly specified in abstract."

For each author:
- Infer 2 to 6 possible research domains from the publications only.
- For each paper, write a factual 2 to 4 sentence summary covering:
  - what the paper studies
  - the biological or computational system
  - methods, assays, models, datasets, or data types if mentioned
  - the main factual contribution

Return ONLY valid JSON with this structure:
{
  "team_id": "...",
  "cohort": "...",
  "human_proposal_id": ...,
  "human_proposal_title": "...",
  "team_members": ["..."],
  "team_member_profiles": [
    {
      "author_name": "...",
      "domains": ["...", "..."],
      "paper_summaries": [
        {
          "pmid": "...",
          "title": "...",
          "summary": "...",
          "methods_or_data": ["...", "..."]
        }
      ]
    }
  ]
}

TEAM PUBLICATION CONTEXT:
__TEAM_CONTEXT_JSON__
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build factual persona cards from human author publication corpora.')
    parser.add_argument('--output', default='data/literature/persona_cards.json', help='Output JSON path')
    parser.add_argument('--model', default='gemini-3-pro-preview', help='Model to use for card synthesis')
    parser.add_argument('--force', action='store_true', help='Rebuild cards even if the output file already exists')
    return parser.parse_args()


def normalize_author_name(name: str) -> str:
    s = str(name or '').strip()
    s = re.sub(r'[\s,;:]+$', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s


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

    depth = 0
    end = -1
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
    except json.JSONDecodeError as exc:
        return None, str(exc)


def load_human_teams() -> List[Dict[str, Any]]:
    teams: List[Dict[str, Any]] = []
    for cohort in ['y1', 'y2']:
        path = Path(f'data/human-proposals/human-proposals-{cohort}.json')
        with open(path, 'r') as f:
            payload = json.load(f)
        proposals = payload['proposals'] if isinstance(payload, dict) else payload
        for idx, proposal in enumerate(proposals, start=1):
            proposal_id = proposal.get('proposal_id', idx)
            teams.append({
                'team_id': f'{cohort}_{int(proposal_id):02d}',
                'cohort': cohort,
                'human_proposal_id': proposal_id,
                'human_proposal_title': proposal.get('proposal_title', proposal.get('title', '')),
                'team_members': [normalize_author_name(a) for a in proposal.get('authors', []) if normalize_author_name(a)],
            })
    return teams


def load_corpus() -> Dict[str, Dict[str, Any]]:
    path = Path('data/literature/human-scientists-corpus.json')
    with open(path, 'r') as f:
        corpus = json.load(f)

    normalized: Dict[str, Dict[str, Any]] = {}
    for author_name, record in corpus.items():
        normalized[normalize_author_name(author_name)] = record
    return normalized


def build_team_context(team: Dict[str, Any], corpus: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    authors_context = []
    missing_authors = []
    for author_name in team['team_members']:
        record = corpus.get(normalize_author_name(author_name))
        if record is None:
            missing_authors.append(author_name)
            authors_context.append({
                'author_name': author_name,
                'num_articles_found': 0,
                'articles': [],
            })
            continue

        articles = []
        for article in record.get('articles', []):
            articles.append({
                'pmid': str(article.get('pmid', '')),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
            })

        authors_context.append({
            'author_name': author_name,
            'num_articles_found': int(record.get('num_articles_found', len(articles))),
            'articles': articles,
        })

    return {
        'team_id': team['team_id'],
        'cohort': team['cohort'],
        'human_proposal_id': team['human_proposal_id'],
        'human_proposal_title': team['human_proposal_title'],
        'team_members': team['team_members'],
        'missing_from_corpus': missing_authors,
        'authors_publication_context': authors_context,
    }


def choose_model(ai_interface: AIModelsInterface, requested_model: str) -> str:
    available_models = ai_interface.get_available_models()
    if requested_model in available_models:
        return requested_model

    for fallback in ['gemini-3-pro-preview', 'gpt-5.2', 'claude-opus-4-5']:
        if fallback in available_models:
            logger.warning(f'Requested model {requested_model} unavailable; falling back to {fallback}')
            return fallback

    raise RuntimeError('No supported model available for persona card generation. Check API keys in .env.')


def generate_persona_card(ai_interface: AIModelsInterface, model_name: str,
                          team_context: Dict[str, Any]) -> Dict[str, Any]:
    prompt = PERSONA_CARD_PROMPT.replace(
        '__TEAM_CONTEXT_JSON__',
        json.dumps(team_context, indent=2, ensure_ascii=False),
    )

    for attempt, delay in enumerate([0] + RETRY_DELAYS, start=1):
        if delay:
            logger.info(f'Retrying persona card for {team_context["team_id"]} in {delay}s')
            time.sleep(delay)

        response = ai_interface.generate_content(
            prompt=prompt,
            model_name=model_name,
            temperature=0,
            max_completion_tokens=16000,
            max_tokens=16000,
        )

        if response.startswith('Error:'):
            logger.warning(f'Persona card generation error for {team_context["team_id"]}: {response}')
            continue

        parsed, err = extract_first_json_object(response)
        if parsed is not None:
            return parsed

        logger.warning(f'Failed to parse persona card JSON for {team_context["team_id"]}: {err}')

    raise RuntimeError(f'All retries failed while building persona card for {team_context["team_id"]}')


def main() -> None:
    args = parse_args()

    output_path = Path(args.output)
    teams = load_human_teams()
    if output_path.exists() and not args.force:
        with open(output_path, 'r') as f:
            existing = json.load(f)
        existing_cards = existing.get('cards', []) if isinstance(existing, dict) else existing
        if len(existing_cards) == len(teams):
            logger.info(f'Persona cards already exist at {output_path}. Use --force to rebuild.')
            return
        logger.info(
            f'Existing persona card file at {output_path} is incomplete '
            f'({len(existing_cards)}/{len(teams)} cards). Rebuilding.'
        )

    ai_interface = AIModelsInterface(config_path='.env', override_env=True)
    model_name = choose_model(ai_interface, args.model)
    corpus = load_corpus()

    cards = []
    for team in teams:
        logger.info(f'Building persona card for {team["team_id"]}: {team["human_proposal_title"][:80]}')
        team_context = build_team_context(team, corpus)
        card = generate_persona_card(ai_interface, model_name, team_context)
        card['missing_from_corpus'] = team_context.get('missing_from_corpus', [])
        cards.append(card)

    output_payload = {
        'created_at': datetime.now().isoformat(),
        'model_used': model_name,
        'source_human_proposals': [
            'data/human-proposals/human-proposals-y1.json',
            'data/human-proposals/human-proposals-y2.json',
        ],
        'source_corpus': 'data/literature/human-scientists-corpus.json',
        'cards': cards,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
    logger.info(f'Saved {len(cards)} persona cards to {output_path}')


if __name__ == '__main__':
    main()
