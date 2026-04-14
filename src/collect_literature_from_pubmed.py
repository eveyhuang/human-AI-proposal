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
OUTPUT_PATH = BASE_DIR / "data" / "literature" / "relevant-corpus-from-pubmed.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

TARGET_ARTICLES = 1050
DELAY = 0.4  # NCBI rate limit: ~3 requests/sec without API key

# ---------------------------------------------------------------------------
# Search queries derived from the NCEMS call for proposals AND topic coverage
# for all human and AI-generated proposals.
#
# The call focuses on:
#   - Emergence phenomena in molecular and cellular biosciences
#   - Mesoscale biology (between biomolecules and organelles)
#   - Community-scale synthesis of publicly available molecular/cellular data
#   - AI and data science for molecular/cellular biology
#   - Multi-omics data integration
#   - Transdisciplinary / computational approaches
#
# Proposal topics additionally span protein biophysics (disorder, allostery,
# topology, PPIs, turnover), chromatin and gene regulation, organelle dynamics
# (mitochondria, ER, Golgi, peroxisomes, contacts), membrane trafficking and
# vesicles, signaling and PTMs, bacterial/microbial biology, plant biology,
# spatial omics, ribosome heterogeneity, and systems physiology, among others.
#
# Similar topics are grouped into combined queries. Each query retrieves 30
# articles sorted by relevance; duplicates are removed by PMID.
# ---------------------------------------------------------------------------

SEARCH_QUERIES = [
    # 1. Emergent properties at molecular/cellular scales
    # Covers: NCEMS call core theme
    {
        "label": "emergent properties molecular cellular biology",
        "query": '("emergent properties" OR "emergence") AND ("molecular biology" OR "cellular biology" OR "cell biology")',
        "max": 30,
    },
    # 2. Mesoscale biology + macromolecular crowding
    # Covers: NCEMS call; AI #50
    {
        "label": "mesoscale biology macromolecular crowding",
        "query": '("mesoscale" OR "mesoscopic" OR "macromolecular crowding" OR "cellular crowding") AND ("protein" OR "biomolecular" OR "cellular" OR "organelle" OR "diffusion")',
        "max": 30,
    },
    # 3. Biomolecular condensates + stress granules + viral inclusion bodies
    # Covers: NCEMS call; AI #32,#36,#55
    {
        "label": "condensates stress granules phase separation",
        "query": '("biomolecular condensates" OR "phase separation" OR "stress granule" OR "viral inclusion body" OR "viral factory") AND ("cell biology" OR "molecular biology" OR "assembly" OR "RNA")',
        "max": 30,
    },
    # 4. Multi-omics data integration
    # Covers: NCEMS call; Human Y1 #8; Human Y2 #3
    {
        "label": "multi-omics data integration synthesis",
        "query": '("multi-omics" OR "multiomics" OR "integrative omics") AND ("data integration" OR "data synthesis") AND ("molecular" OR "cellular")',
        "max": 30,
    },
    # 5. AI / machine learning for molecular and cellular biology
    # Covers: NCEMS call; Human Y1 #2; Human Y2 #10
    {
        "label": "AI machine learning molecular cellular biology",
        "query": '("machine learning" OR "artificial intelligence" OR "deep learning") AND ("molecular biology" OR "cell biology" OR "proteomics" OR "genomics")',
        "max": 30,
    },
    # 6. Systems biology and network analysis
    # Covers: NCEMS call
    {
        "label": "systems biology network analysis cellular",
        "query": '("systems biology" OR "biological networks") AND ("data synthesis" OR "data integration") AND ("molecular" OR "cellular")',
        "max": 30,
    },
    # 7. Protein complex assembly + self-assembly + stoichiometry
    # Covers: NCEMS call; AI #5
    {
        "label": "protein complex assembly stoichiometry self-organization",
        "query": '("protein self-assembly" OR "macromolecular complex" OR "protein complex") AND ("stoichiometry" OR "assembly pathway" OR "emergent" OR "organization" OR "structural proteomics")',
        "max": 30,
    },
    # 8. Computational biology data synthesis + proteomics metadata standards
    # Covers: NCEMS call; Human Y1 #12
    {
        "label": "data synthesis reusability standards computational biology",
        "query": '("computational biology" OR "bioinformatics" OR "mass spectrometry" OR "proteomics") AND ("publicly available data" OR "data synthesis" OR "metadata" OR "FAIR" OR "data reusability")',
        "max": 30,
    },
    # 9. Gene regulatory networks + transposable elements
    # Covers: NCEMS call; Human Y1 #10
    {
        "label": "gene regulatory networks transposable elements",
        "query": '("gene regulatory network" OR "single-cell transcriptomics" OR "transposable element" OR "transposon") AND ("data integration" OR "gene regulation" OR "chromatin" OR "computational")',
        "max": 30,
    },
    # 10. Cytoskeletal dynamics and cellular organization
    # Covers: NCEMS call; AI #3,#25,#44,#53
    {
        "label": "cytoskeletal dynamics cellular self-organization",
        "query": '("cytoskeletal dynamics" OR "cytoskeleton" OR "actin" OR "myosin") AND ("self-organization" OR "emergent" OR "cellular organization" OR "assembly")',
        "max": 30,
    },
    # 11. Intrinsically disordered regions / proteins
    # Covers: Human Y1 #5,#7; Human Y2 #4; AI #52
    {
        "label": "intrinsically disordered regions protein function evolution",
        "query": '("intrinsically disordered" OR "disordered protein" OR "disordered regions") AND ("function" OR "evolution" OR "conformational ensemble" OR "adaptation")',
        "max": 30,
    },
    # 12. Protein allostery + protein knots / complex topologies
    # Covers: Human Y2 #1,#2,#6; AI #23
    {
        "label": "protein allostery knots topologies regulation",
        "query": '("allostery" OR "allosteric regulation" OR "protein knot" OR "knotted protein" OR "pierced lasso" OR "protein topology") AND ("computational" OR "evolution" OR "molecular dynamics" OR "folding")',
        "max": 30,
    },
    # 13. Protein interaction networks + crosslinking mass spectrometry
    # Covers: Human Y1 #5,#11; AI #48
    {
        "label": "protein interaction networks structural proteomics XL-MS",
        "query": '("protein-protein interaction" OR "interactome" OR "crosslinking mass spectrometry" OR "XL-MS") AND ("network" OR "structural proteomics" OR "biophysics" OR "stability")',
        "max": 30,
    },
    # 14. mRNP / RNA-protein interactions / RNA localization
    # Covers: Human Y1 #6; AI #19,#64
    {
        "label": "RNA-protein interaction mRNP localization",
        "query": '("mRNP" OR "RNA-protein interaction" OR "RNA-binding protein" OR "ribonucleoprotein" OR "RNA localization") AND ("cellular" OR "transcriptome" OR "condensate" OR "subcellular")',
        "max": 30,
    },
    # 15. Protein turnover + proteasome degradation + proteostasis
    # Covers: Human Y2 #8; AI #8,#45,#60
    {
        "label": "protein turnover degradation proteasome proteostasis",
        "query": '("protein turnover" OR "protein half-life" OR "protein degradation" OR "proteasome" OR "proteostasis") AND ("computational" OR "systems" OR "proteome" OR "cross-species" OR "spatial")',
        "max": 30,
    },
    # 16. 3D chromatin + enhancer-promoter + epigenetic memory
    # Covers: Human Y1 #2; AI #4,#26,#59,#67
    {
        "label": "chromatin architecture enhancer-promoter epigenetic memory",
        "query": '("3D genome" OR "chromatin architecture" OR "Hi-C" OR "enhancer-promoter" OR "epigenetic memory" OR "transcriptional memory") AND ("gene regulation" OR "single-cell" OR "computational" OR "heritable")',
        "max": 30,
    },
    # 17. Organelle contact sites + mitochondrial dynamics
    # Covers: AI #2,#10,#27,#34,#49
    {
        "label": "organelle contact sites mitochondrial dynamics",
        "query": '("organelle contact site" OR "membrane contact site" OR "ER-mitochondria" OR "mitochondrial dynamics" OR "mitochondrial fission" OR "mitochondrial fusion") AND ("proteomics" OR "imaging" OR "bioenergetics" OR "lipid transfer")',
        "max": 30,
    },
    # 18. Nuclear bodies + nuclear pore complex + nuclear lamina
    # Covers: AI #16,#21,#33,#46,#58
    {
        "label": "nuclear bodies pore complex lamina organization",
        "query": '("nuclear body" OR "nuclear speckle" OR "nucleolus" OR "nuclear pore complex" OR "nuclear lamina" OR "PML body") AND ("assembly" OR "organization" OR "emergent" OR "proteomics")',
        "max": 30,
    },
    # 19. Ribosome heterogeneity and specialized translation
    # Covers: AI #12,#29,#57
    {
        "label": "ribosome heterogeneity specialized translation",
        "query": '("ribosome heterogeneity" OR "specialized ribosome" OR "ribosome composition" OR "ribosome biogenesis") AND ("translation" OR "tissue" OR "regulation" OR "proteomics")',
        "max": 30,
    },
    # 20. Membrane microdomains / lipid rafts + glycocalyx / cell surface
    # Covers: AI #13,#28,#43,#66
    {
        "label": "membrane microdomains lipid rafts glycocalyx cell surface",
        "query": '("lipid raft" OR "membrane microdomain" OR "lipid domain" OR "glycocalyx" OR "cell surface glycan") AND ("signaling" OR "organization" OR "proteomics" OR "lipidomics" OR "glycomics")',
        "max": 30,
    },
    # 21. Endocytic trafficking + ESCRT / extracellular vesicles / exosomes
    # Covers: AI #14,#20,#35,#42
    {
        "label": "membrane trafficking endocytosis ESCRT vesicle sorting",
        "query": '("endocytic trafficking" OR "endosome" OR "ESCRT" OR "extracellular vesicle" OR "exosome biogenesis" OR "multivesicular body") AND ("sorting" OR "biogenesis" OR "membrane scission" OR "proteomics")',
        "max": 30,
    },
    # 22. Autophagosome biogenesis / selective autophagy
    # Covers: AI #18,#34,#63
    {
        "label": "autophagosome biogenesis selective autophagy",
        "query": '("autophagosome" OR "autophagy" OR "selective autophagy") AND ("biogenesis" OR "receptor" OR "membrane" OR "proteomics" OR "computational")',
        "max": 30,
    },
    # 23. Cell polarity
    # Covers: AI #9,#51
    {
        "label": "cell polarity spatial organization self-organization",
        "query": '("cell polarity" OR "cellular polarity" OR "asymmetric distribution") AND ("spatial" OR "proteomics" OR "transcriptomics" OR "emergent" OR "self-organization")',
        "max": 30,
    },
    # 24. Cell cycle + centrosome / spindle assembly
    # Covers: AI #15,#37,#62
    {
        "label": "cell cycle centrosome spindle division",
        "query": '("cell cycle transition" OR "mitotic entry" OR "centrosome" OR "spindle assembly" OR "microtubule organizing") AND ("single-cell" OR "proteomics" OR "self-organization" OR "bipolarity")',
        "max": 30,
    },
    # 25. Metabolic channeling and metabolon organization
    # Covers: AI #6,#56
    {
        "label": "metabolic channeling metabolon enzyme complex",
        "query": '("metabolic channeling" OR "metabolon" OR "enzyme complex") AND ("spatial proteomics" OR "metabolomics" OR "flux" OR "organization")',
        "max": 30,
    },
    # 26. Signaling specificity + PTM crosstalk + phospho-proteomics
    # Covers: AI #11,#54,#61
    {
        "label": "signaling specificity PTM crosstalk phosphoproteomics",
        "query": '("signaling specificity" OR "phosphoproteomics" OR "kinase network" OR "PTM crosstalk" OR "post-translational modification crosstalk") AND ("single-cell" OR "pathway" OR "computational" OR "systems")',
        "max": 30,
    },
    # 27. Bacterial / microbial biology (cell states + microcompartments + microbiome)
    # Covers: Human Y1 #3,#4; Human Y2 #11; AI #17,#40
    {
        "label": "bacterial microbial cell states microcompartments microbiome",
        "query": '("bacterial gene expression" OR "bacterial cell state" OR "bacterial microcompartment" OR "encapsulin" OR "microbiome" OR "metagenomics") AND ("atlas" OR "machine learning" OR "assembly" OR "computational" OR "data integration")',
        "max": 30,
    },
    # 28. Plant cell biology (cytokinesis + cell wall)
    # Covers: Human Y1 #1; AI #39
    {
        "label": "plant cell biology cytokinesis cell wall",
        "query": '("plant cytokinesis" OR "plant cell division" OR "cellulose synthase" OR "plant cell wall") AND ("heat stress" OR "assembly" OR "genetic network" OR "robustness" OR "organization")',
        "max": 30,
    },
    # 29. Systems physiology (mammalian hibernation + inter-organ communication)
    # Covers: Human Y2 #3,#5
    {
        "label": "systems physiology hibernation inter-organ communication",
        "query": '("hibernation" OR "torpor" OR "metabolic suppression" OR "inter-organ communication" OR "organ crosstalk") AND ("transcriptomics" OR "multi-omics" OR "comparative" OR "network" OR "molecular mechanism")',
        "max": 30,
    },
    # 30. Spatial transcriptomics and proteomics integration
    # Covers: Human Y2 #9
    {
        "label": "spatial transcriptomics proteomics cell state",
        "query": '("spatial transcriptomics" OR "spatial proteomics" OR "spatial omics") AND ("cell state" OR "tissue" OR "integration" OR "computational")',
        "max": 30,
    },
    # 31. Enzyme function prediction / molecular dynamics
    # Covers: Human Y2 #10
    {
        "label": "enzyme function prediction molecular dynamics AI",
        "query": '("enzyme function" OR "enzyme catalysis") AND ("molecular dynamics" OR "machine learning" OR "deep learning" OR "prediction")',
        "max": 30,
    },
    # 32. Synaptic organization + immune synapse
    # Covers: AI #22,#30,#65
    {
        "label": "synapse organization synaptic immune signaling",
        "query": '("synaptic organization" OR "synaptic vesicle" OR "postsynaptic density" OR "immune synapse" OR "immunological synapse") AND ("proteomics" OR "structure" OR "assembly" OR "spatial organization")',
        "max": 30,
    },
    # 33. ER + Golgi + peroxisome organelle dynamics
    # Covers: AI #38,#41,#68
    {
        "label": "ER Golgi peroxisome organelle dynamics secretory",
        "query": '("endoplasmic reticulum" OR "ER dynamics" OR "Golgi apparatus" OR "secretory pathway" OR "peroxisome biogenesis" OR "peroxisomal") AND ("organization" OR "dynamics" OR "trafficking" OR "morphology")',
        "max": 30,
    },
    # 34. Mechanotransduction and focal adhesion
    # Covers: AI #31,#69
    {
        "label": "mechanotransduction focal adhesion cellular force",
        "query": '("mechanotransduction" OR "focal adhesion" OR "mechanical force") AND ("signaling" OR "maturation" OR "cellular" OR "structure")',
        "max": 30,
    },
    # 35. Molecular evolution / cross-species regulatory modules
    # Covers: Human Y2 #7
    {
        "label": "molecular evolution cross-species regulatory modules",
        "query": '("molecular evolution" OR "cross-species" OR "evolutionary conservation") AND ("regulatory module" OR "metabolic network" OR "gene network" OR "data synthesis")',
        "max": 30,
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
        year_e    = article_elem.find(".//PubDate/Year")

        pmid = pmid_elem.text if pmid_elem is not None else ""
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""
        year  = year_e.text if year_e is not None else ""
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
            "publication_date": year
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
