"""
Collect relevant PubMed articles based on keywords derived from the NCEMS call for proposals.

Searches PubMed using multiple keyword queries capturing the call's key themes:
emergent properties, mesoscale biology, data synthesis, multi-omics integration,
and AI/ML for molecular and cellular biology.

Retrieves up to 350 unique articles and saves keywords, titles, and abstracts
to data/literature/call-relevant-corpus.json.
"""

import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "literature" / "call-relevant-corpus.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

TARGET_ARTICLES = 350
DELAY = 0.4  # NCBI rate limit: ~3 requests/sec without API key

# ---------------------------------------------------------------------------
# Search queries derived from the NCEMS call for proposals.
#
# The call focuses on:
#   - Emergence phenomena in molecular and cellular biosciences
#   - Mesoscale biology (between biomolecules and organelles)
#   - Community-scale synthesis of publicly available molecular/cellular data
#   - AI and data science for molecular/cellular biology
#   - Multi-omics data integration
#   - Transdisciplinary / computational approaches
#
# Each query targets a facet of the call. We retrieve more candidates per
# query than needed and deduplicate by PMID to reach 350 unique articles.
# ---------------------------------------------------------------------------

SEARCH_QUERIES = [
    # Core: emergent properties at molecular/cellular scales
    {
        "label": "emergent properties molecular cellular biology",
        "query": '("emergent properties" OR "emergence") AND ("molecular biology" OR "cellular biology" OR "cell biology")',
        "max": 60,
    },
    # Mesoscale biology
    {
        "label": "mesoscale biology biomolecular organization",
        "query": '("mesoscale" OR "mesoscopic") AND ("protein" OR "biomolecular" OR "cellular" OR "organelle")',
        "max": 50,
    },
    # Phase separation and biomolecular condensates (key mesoscale phenomenon)
    {
        "label": "biomolecular condensates phase separation",
        "query": '("biomolecular condensates" OR "phase separation") AND ("cell biology" OR "molecular biology")',
        "max": 50,
    },
    # Multi-omics data integration
    {
        "label": "multi-omics data integration molecular cellular",
        "query": '("multi-omics" OR "multiomics" OR "integrative omics") AND ("data integration" OR "data synthesis") AND ("molecular" OR "cellular")',
        "max": 50,
    },
    # AI / machine learning for molecular and cellular biology
    {
        "label": "AI machine learning molecular cellular biology",
        "query": '("machine learning" OR "artificial intelligence" OR "deep learning") AND ("molecular biology" OR "cell biology" OR "proteomics" OR "genomics")',
        "max": 60,
    },
    # Systems biology and network analysis
    {
        "label": "systems biology network analysis cellular",
        "query": '("systems biology" OR "biological networks") AND ("data synthesis" OR "data integration") AND ("molecular" OR "cellular")',
        "max": 50,
    },
    # Protein structure-function and self-assembly
    {
        "label": "protein self-assembly supramolecular organization",
        "query": '("protein self-assembly" OR "supramolecular" OR "macromolecular complex") AND ("emergent" OR "organization" OR "cellular function")',
        "max": 40,
    },
    # Computational biology synthesis of public data
    {
        "label": "computational biology public data synthesis",
        "query": '("computational biology" OR "bioinformatics") AND ("publicly available data" OR "public databases" OR "data synthesis") AND ("molecular" OR "cellular")',
        "max": 50,
    },
    # Gene regulation and epigenomics at scale
    {
        "label": "gene regulatory networks single-cell omics",
        "query": '("gene regulatory network" OR "single-cell omics" OR "single-cell transcriptomics") AND ("data integration" OR "computational" OR "systems")',
        "max": 50,
    },
    # Cytoskeletal dynamics and cellular organization
    {
        "label": "cytoskeletal dynamics cellular organization",
        "query": '("cytoskeletal dynamics" OR "cytoskeleton") AND ("self-organization" OR "emergent" OR "cellular organization")',
        "max": 40,
    },
]


def search_pubmed(query: str, max_results: int) -> list[str]:
    """Search PubMed and return PMIDs sorted by relevance."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "relevance",
        "retmode": "json",
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_article_details(pmids: list[str]) -> list[dict]:
    """Fetch title and abstract for a batch of PMIDs (max ~200 at a time)."""
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    resp = requests.get(EFETCH_URL, params=params, timeout=60)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    articles = []
    for article_elem in root.findall(".//PubmedArticle"):
        pmid_elem = article_elem.find(".//PMID")
        title_elem = article_elem.find(".//ArticleTitle")
        abstract_parts = article_elem.findall(".//AbstractText")

        pmid = pmid_elem.text if pmid_elem is not None else ""
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""

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
    seen_pmids: set[str] = set()
    all_articles: list[dict] = []
    query_log: list[dict] = []

    print(f"Target: {TARGET_ARTICLES} unique articles\n")
    print("Search queries derived from the NCEMS call for proposals:")
    print("=" * 60)

    for i, q in enumerate(SEARCH_QUERIES, 1):
        if len(all_articles) >= TARGET_ARTICLES:
            print(f"\nReached {TARGET_ARTICLES} articles. Stopping early.")
            break

        label = q["label"]
        query = q["query"]
        max_results = q["max"]

        print(f"\n[{i}/{len(SEARCH_QUERIES)}] {label}")
        print(f"  Query: {query}")

        pmids = search_pubmed(query, max_results)
        time.sleep(DELAY)

        # Filter out duplicates
        new_pmids = [p for p in pmids if p not in seen_pmids]

        # Only fetch as many as we still need
        remaining = TARGET_ARTICLES - len(all_articles)
        new_pmids = new_pmids[:remaining]

        if new_pmids:
            articles = fetch_article_details(new_pmids)
            time.sleep(DELAY)

            for article in articles:
                if article["pmid"] not in seen_pmids:
                    seen_pmids.add(article["pmid"])
                    all_articles.append(article)
        else:
            articles = []

        query_log.append({
            "label": label,
            "query": query,
            "total_results_returned": len(pmids),
            "new_unique_added": len(articles),
        })

        print(f"  Retrieved: {len(pmids)}, New unique: {len(articles)}, "
              f"Running total: {len(all_articles)}")

    # Trim to exactly TARGET_ARTICLES if we went over
    all_articles = all_articles[:TARGET_ARTICLES]

    # Build output
    output = {
        "description": "PubMed articles relevant to the NCEMS call for proposals, "
                       "retrieved using keyword queries derived from the call's key themes.",
        "total_articles": len(all_articles),
        "search_queries": query_log,
        "articles": all_articles,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Done! Saved {len(all_articles)} unique articles.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
