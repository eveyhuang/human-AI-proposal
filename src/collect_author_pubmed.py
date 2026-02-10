"""
Collect top PubMed articles for each author from human proposals.

For each author listed in data/human-proposals/, searches PubMed for their
most relevant articles (sorted by relevance, which factors in citation metrics)
and saves titles + abstracts to data/literature/human-scientists-corpus.json.
"""

import json
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = BASE_DIR / "data" / "human-proposals"
OUTPUT_PATH = BASE_DIR / "data" / "literature" / "human-scientists-corpus.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

ARTICLES_PER_AUTHOR = 5
DELAY_BETWEEN_REQUESTS = 0.4  # NCBI rate limit: 3 requests/sec without API key


def extract_authors(proposals_dir: Path) -> list[str]:
    """Extract unique author names from all proposal JSON files."""
    authors = []
    for filepath in sorted(proposals_dir.glob("*.json")):
        with open(filepath) as f:
            data = json.load(f)
        for proposal in data.get("proposals", []):
            for name in proposal.get("authors", []):
                name = name.strip().rstrip(",")
                if name and name not in authors:
                    authors.append(name)
    return authors


def search_pubmed(author_name: str, max_results: int = 5) -> list[str]:
    """Search PubMed for articles by an author, sorted by relevance. Returns PMIDs."""
    params = {
        "db": "pubmed",
        "term": f"{author_name}[Author]",
        "retmax": max_results,
        "sort": "relevance",
        "retmode": "json",
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_article_details(pmids: list[str]) -> list[dict]:
    """Fetch title and abstract for a list of PMIDs."""
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    resp = requests.get(EFETCH_URL, params=params, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    articles = []
    for article_elem in root.findall(".//PubmedArticle"):
        pmid_elem = article_elem.find(".//PMID")
        title_elem = article_elem.find(".//ArticleTitle")
        abstract_parts = article_elem.findall(".//AbstractText")

        pmid = pmid_elem.text if pmid_elem is not None else ""
        title = title_elem.text if title_elem is not None else ""

        # Some abstracts have multiple sections (structured abstracts)
        abstract_texts = []
        for part in abstract_parts:
            label = part.get("Label", "")
            text = "".join(part.itertext()).strip()
            if label:
                abstract_texts.append(f"{label}: {text}")
            else:
                abstract_texts.append(text)
        abstract = " ".join(abstract_texts)

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
        })
    return articles


def main():
    print("Extracting author names from proposals...")
    authors = extract_authors(PROPOSALS_DIR)
    print(f"Found {len(authors)} unique authors:\n")
    for i, name in enumerate(authors, 1):
        print(f"  {i}. {name}")
    print()

    corpus = {}
    for i, author in enumerate(authors, 1):
        print(f"[{i}/{len(authors)}] Searching PubMed for: {author}...")
        try:
            pmids = search_pubmed(author, max_results=ARTICLES_PER_AUTHOR)
            time.sleep(DELAY_BETWEEN_REQUESTS)

            if pmids:
                articles = fetch_article_details(pmids)
                time.sleep(DELAY_BETWEEN_REQUESTS)
            else:
                articles = []
                print(f"  WARNING: No articles found for {author}")

            corpus[author] = {
                "author_name": author,
                "num_articles_found": len(articles),
                "articles": articles,
            }
            print(f"  Found {len(articles)} articles")
        except Exception as e:
            print(f"  ERROR for {author}: {e}")
            corpus[author] = {
                "author_name": author,
                "num_articles_found": 0,
                "articles": [],
                "error": str(e),
            }
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    total_articles = sum(entry["num_articles_found"] for entry in corpus.values())
    print(f"\nDone! Saved {total_articles} articles for {len(corpus)} authors")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
