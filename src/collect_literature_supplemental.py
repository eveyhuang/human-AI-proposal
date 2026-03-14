"""
Extend the existing call-relevant literature corpus with supplemental PubMed queries
targeting topics under-represented in the original 350-article corpus.

Under-represented topics were identified by inspecting proposals that clustered
far from the existing literature in the UMAP novelty visualization:
  - Bacterial cell division / divisome machinery
  - Bacterial organelles and microcompartments
  - Chromatin / genome 3D organization
  - Proteostasis and chaperone networks
  - Synaptic molecular organization (nanocolumns, PSD)
  - Cryo-electron tomography / in-situ structural biology
  - Protein interactomics and PPI networks
  - Cellular bioenergetics and metabolic networks

Loads the existing corpus, appends new unique articles (up to SUPPLEMENTAL_TARGET),
and overwrites the JSON in place.

Usage (run from project root):
    python src/collect_literature_supplemental.py
"""

import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE_DIR / "data" / "literature" / "call-relevant-corpus.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

SUPPLEMENTAL_TARGET = 250   # max new articles to add (on top of existing 350)
DELAY = 0.4                 # NCBI rate limit: ~3 requests/sec without API key

SUPPLEMENTAL_QUERIES = [
    # Bacterial cell division machinery
    {
        "label": "bacterial cell division divisome machinery",
        "query": '("bacterial cell division" OR "FtsZ" OR "divisome" OR "Z-ring" OR "cell division machinery") AND ("organization" OR "dynamics" OR "emergent" OR "assembly")',
        "max": 40,
    },
    # Bacterial organelles and microcompartments
    {
        "label": "bacterial organelles microcompartments",
        "query": '("bacterial organelle" OR "carboxysome" OR "metabolosome" OR "bacterial microcompartment" OR "encapsulin") AND ("assembly" OR "function" OR "organization")',
        "max": 35,
    },
    # Chromatin / 3D genome organization
    {
        "label": "chromatin 3D genome organization structure-function",
        "query": '("chromatin organization" OR "genome folding" OR "topologically associating domain" OR "Hi-C" OR "chromatin loop") AND ("gene regulation" OR "structure-function" OR "3D genome")',
        "max": 40,
    },
    # Proteostasis and chaperone networks
    {
        "label": "proteostasis chaperone network protein quality control",
        "query": '("proteostasis" OR "protein homeostasis" OR "chaperone network" OR "protein quality control" OR "unfolded protein response") AND ("network" OR "systems" OR "cellular")',
        "max": 40,
    },
    # Synaptic molecular organization
    {
        "label": "synaptic organization postsynaptic density nanocolumn",
        "query": '("postsynaptic density" OR "synaptic scaffold" OR "synaptic organization" OR "nanocolumn" OR "synapse organization") AND ("molecular" OR "organization" OR "emergent" OR "structure")',
        "max": 35,
    },
    # Cryo-ET and in-situ structural biology
    {
        "label": "cryo-ET in-situ structural biology cellular architecture",
        "query": '("cryo-electron tomography" OR "cryo-ET" OR "subtomogram averaging" OR "in situ structural biology") AND ("cellular architecture" OR "molecular" OR "in situ")',
        "max": 40,
    },
    # Protein-protein interaction networks / interactomics
    {
        "label": "protein interactome PPI network cellular function",
        "query": '("protein interactome" OR "protein-protein interaction network" OR "interactome" OR "PPI network") AND ("systems" OR "cellular" OR "functional" OR "network analysis")',
        "max": 40,
    },
    # Cellular bioenergetics and metabolic networks
    {
        "label": "cellular bioenergetics metabolic network organization",
        "query": '("bioenergetics" OR "cellular metabolism" OR "metabolic network" OR "metabolon") AND ("emergent" OR "organization" OR "systems" OR "molecular mechanism")',
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
    return resp.json().get("esearchresult", {}).get("idlist", [])


def fetch_article_details(pmids: list[str]) -> list[dict]:
    """Fetch title, abstract, and publication date for a batch of PMIDs."""
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
    for elem in root.findall(".//PubmedArticle"):
        pmid_e    = elem.find(".//PMID")
        title_e   = elem.find(".//ArticleTitle")
        abs_parts = elem.findall(".//AbstractText")
        year_e    = elem.find(".//PubDate/Year")

        pmid  = pmid_e.text if pmid_e is not None else ""
        title = "".join(title_e.itertext()).strip() if title_e is not None else ""
        year  = year_e.text if year_e is not None else ""

        abstract_texts = []
        for part in abs_parts:
            label = part.get("Label", "")
            text  = "".join(part.itertext()).strip()
            abstract_texts.append(f"{label}: {text}" if label else text)
        abstract = " ".join(abstract_texts)

        articles.append({"pmid": pmid, "title": title, "abstract": abstract,
                          "publication_date": year})
    return articles


def main():
    # ── Load existing corpus ──────────────────────────────────────────────────
    with open(CORPUS_PATH) as f:
        corpus = json.load(f)

    existing_articles: list[dict] = corpus["articles"]
    existing_query_log: list[dict] = corpus["search_queries"]
    seen_pmids: set[str] = {a["pmid"] for a in existing_articles}
    new_articles: list[dict] = []

    print(f"Existing corpus: {len(existing_articles)} articles")
    print(f"Supplemental target: up to {SUPPLEMENTAL_TARGET} additional articles\n")
    print("=" * 65)

    for i, q in enumerate(SUPPLEMENTAL_QUERIES, 1):
        if len(new_articles) >= SUPPLEMENTAL_TARGET:
            print(f"\nReached supplemental target of {SUPPLEMENTAL_TARGET}. Stopping.")
            break

        print(f"\n[{i}/{len(SUPPLEMENTAL_QUERIES)}] {q['label']}")
        print(f"  Query: {q['query']}")

        pmids = search_pubmed(q["query"], q["max"])
        time.sleep(DELAY)

        new_pmids = [p for p in pmids if p not in seen_pmids]
        remaining = SUPPLEMENTAL_TARGET - len(new_articles)
        new_pmids = new_pmids[:remaining]

        fetched = []
        if new_pmids:
            fetched = fetch_article_details(new_pmids)
            time.sleep(DELAY)
            for art in fetched:
                if art["pmid"] not in seen_pmids:
                    seen_pmids.add(art["pmid"])
                    new_articles.append(art)

        existing_query_log.append({
            "label": q["label"],
            "query": q["query"],
            "total_results_returned": len(pmids),
            "new_unique_added": len(fetched),
        })

        print(f"  Retrieved: {len(pmids)}, New unique: {len(fetched)}, "
              f"Running new total: {len(new_articles)}")

    # ── Merge and save ────────────────────────────────────────────────────────
    all_articles = existing_articles + new_articles
    corpus["articles"] = all_articles
    corpus["total_articles"] = len(all_articles)
    corpus["search_queries"] = existing_query_log

    with open(CORPUS_PATH, "w") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 65}")
    print(f"Done! Added {len(new_articles)} new articles.")
    print(f"Total corpus: {len(all_articles)} articles.")
    print(f"Saved to: {CORPUS_PATH}")
    print()
    print("Next step: delete the cached literature embeddings so they are")
    print("re-computed on the next notebook run:")
    print(f"  rm data/embeddings/literature/relevant_literature_embeddings.pkl")


if __name__ == "__main__":
    main()
