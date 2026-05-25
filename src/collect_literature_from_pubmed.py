"""
Collect a broad PubMed corpus aligned to NCEMS call key areas.

This script uses query themes derived from data/call_and_info.json only
(and intentionally does not use proposal-specific topic terms).

For each key-area query, it retrieves all matching PubMed records from
2010-01-01 through today, deduplicates PMIDs across queries, fetches article
metadata, and stores article MeSH terms alongside title/abstract/date fields.
"""

from __future__ import annotations

import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CALL_INFO_PATH = BASE_DIR / "data" / "call_and_info.json"
OUTPUT_PATH = BASE_DIR / "data" / "literature" / "relevant-corpus-from-pubmed.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# User-provided key (can be overridden with NCBI_API_KEY env var).
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "6cad3f28a364436623653bbe5c69d95d6408")

START_DATE = date(2010, 1, 1)
END_DATE = date.today()

# ESearch can only return up to 10,000 PMIDs per query window for PubMed.
MAX_ESEARCH_WINDOW = 10_000
SEARCH_BATCH_SIZE = 1_000
EFETCH_BATCH_SIZE = 200
DELAY = 0.12 if NCBI_API_KEY else 0.4

# Key areas strictly derived from NCEMS call text in data/call_and_info.json.
KEY_AREA_QUERIES = [
    {
        "label": "emergence in molecular and cellular biosciences",
        "query": '(("emergent properties" OR emergence) AND ("molecular biosciences" OR "cellular biosciences" OR "molecular biology" OR "cell biology"))',
    },
    
]


def _api_params() -> dict[str, str]:
    """Return shared API params, including key when available."""
    params: dict[str, str] = {}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    return params


def _search_request(
    query: str,
    start: date,
    end: date,
    retmax: int,
    retstart: int,
) -> dict:
    """Run ESearch request with publication-date filters."""
    params: dict[str, str | int] = {
        "db": "pubmed",
        "term": query,
        "datetype": "pdat",
        "mindate": start.strftime("%Y/%m/%d"),
        "maxdate": end.strftime("%Y/%m/%d"),
        "retmode": "json",
        "retmax": retmax,
        "retstart": retstart,
        "sort": "pub_date",
        **_api_params(),
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=60)
    resp.raise_for_status()
    time.sleep(DELAY)
    return resp.json().get("esearchresult", {})


def _window_count(query: str, start: date, end: date) -> int:
    """Return total PubMed result count for query in date window."""
    data = _search_request(query=query, start=start, end=end, retmax=0, retstart=0)
    return int(data.get("count", "0"))


def _fetch_window_pmids(query: str, start: date, end: date, count: int) -> list[str]:
    """Fetch PMIDs for a query/date window where count <= MAX_ESEARCH_WINDOW."""
    pmids: list[str] = []
    for retstart in range(0, count, SEARCH_BATCH_SIZE):
        batch = _search_request(
            query=query,
            start=start,
            end=end,
            retmax=min(SEARCH_BATCH_SIZE, count - retstart),
            retstart=retstart,
        )
        pmids.extend(batch.get("idlist", []))
    return pmids


def _fetch_pmids_recursive(query: str, start: date, end: date) -> list[str]:
    """Fetch all PMIDs by splitting date windows when counts exceed 10k."""
    count = _window_count(query=query, start=start, end=end)

    if count == 0:
        return []

    if count <= MAX_ESEARCH_WINDOW:
        return _fetch_window_pmids(query=query, start=start, end=end, count=count)

    if start >= end:
        print(
            "  Warning: single-day window exceeds PubMed 10k cap; "
            f"retrieving first {MAX_ESEARCH_WINDOW} only for {start.isoformat()}."
        )
        return _fetch_window_pmids(
            query=query,
            start=start,
            end=end,
            count=MAX_ESEARCH_WINDOW,
        )

    midpoint = start + timedelta(days=(end - start).days // 2)
    left = _fetch_pmids_recursive(query=query, start=start, end=midpoint)
    right = _fetch_pmids_recursive(query=query, start=midpoint + timedelta(days=1), end=end)
    return list(dict.fromkeys(left + right))


def fetch_article_details(pmids: list[str]) -> list[dict]:
    """Fetch PubMed metadata and include article MeSH terms."""
    if not pmids:
        return []

    params: dict[str, str] = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        **_api_params(),
    }
    resp = requests.get(EFETCH_URL, params=params, timeout=120)
    resp.raise_for_status()
    time.sleep(DELAY)

    root = ET.fromstring(resp.text)
    articles: list[dict] = []

    for article_elem in root.findall(".//PubmedArticle"):
        pmid_elem = article_elem.find(".//PMID")
        title_elem = article_elem.find(".//ArticleTitle")
        abstract_parts = article_elem.findall(".//AbstractText")

        pub_date_parts = [
            article_elem.find(".//ArticleDate"),
            article_elem.find(".//JournalIssue/PubDate"),
            article_elem.find(".//PubDate"),
        ]

        pmid = pmid_elem.text.strip() if pmid_elem is not None and pmid_elem.text else ""
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""

        abstract_chunks: list[str] = []
        for part in abstract_parts:
            text = "".join(part.itertext()).strip()
            label = (part.get("Label") or "").strip()
            if not text:
                continue
            if label:
                abstract_chunks.append(f"{label}: {text}")
            else:
                abstract_chunks.append(text)
        abstract = " ".join(abstract_chunks)

        publication_date = ""
        for date_node in pub_date_parts:
            if date_node is None:
                continue
            y = date_node.findtext("Year", default="").strip()
            m = date_node.findtext("Month", default="").strip()
            d = date_node.findtext("Day", default="").strip()
            if y:
                pieces = [y] + [p for p in [m, d] if p]
                publication_date = "-".join(pieces)
                break

        mesh_terms: list[str] = []
        for descriptor in article_elem.findall(".//MeshHeadingList/MeshHeading/DescriptorName"):
            term = "".join(descriptor.itertext()).strip()
            if term:
                mesh_terms.append(term)

        articles.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "publication_date": publication_date,
                "mesh_terms": sorted(set(mesh_terms)),
            }
        )

    return articles


def _load_call_info() -> dict:
    with open(CALL_INFO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    call_info = _load_call_info()

    seen_pmids: set[str] = set()
    all_articles: list[dict] = []
    query_log: list[dict] = []

    print(f"Date range: {START_DATE.isoformat()} to {END_DATE.isoformat()}")
    print("NCEMS key-area queries derived from data/call_and_info.json")
    print("=" * 70)

    for i, q in enumerate(KEY_AREA_QUERIES, 1):
        label = q["label"]
        query = q["query"]

        print(f"\n[{i}/{len(KEY_AREA_QUERIES)}] {label}")
        print(f"  Query: {query}")

        pmids = _fetch_pmids_recursive(query=query, start=START_DATE, end=END_DATE)

        unique_query_pmids = [pmid for pmid in pmids if pmid not in seen_pmids]
        print(
            f"  Retrieved PMIDs: {len(pmids)} "
            f"(new after dedup: {len(unique_query_pmids)})"
        )

        query_added = 0
        for start_idx in range(0, len(unique_query_pmids), EFETCH_BATCH_SIZE):
            batch_pmids = unique_query_pmids[start_idx : start_idx + EFETCH_BATCH_SIZE]
            batch_articles = fetch_article_details(batch_pmids)
            for article in batch_articles:
                pmid = article.get("pmid", "")
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    all_articles.append(article)
                    query_added += 1

        query_log.append(
            {
                "label": label,
                "query": query,
                "total_results_returned": len(pmids),
                "new_unique_added": query_added,
            }
        )
        print(f"  Added articles this query: {query_added}")
        print(f"  Running total unique articles: {len(all_articles)}")

    output = {
        "description": (
            "PubMed articles aligned with NCEMS call key areas from "
            "data/call_and_info.json (proposal-informed topic queries removed)."
        ),
        "date_range": {
            "start": START_DATE.isoformat(),
            "end": END_DATE.isoformat(),
            "datetype": "pdat",
        },
        "source": {
            "call_excerpt": call_info.get("call", ""),
            "info_excerpt": call_info.get("info", ""),
        },
        "total_articles": len(all_articles),
        "search_queries": query_log,
        "articles": all_articles,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"Done! Saved {len(all_articles)} unique articles.")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
