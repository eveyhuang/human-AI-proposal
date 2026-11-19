# Analysis plan v2

## Overview

**Status date: November 16, 2026.** This is the execution-status and results reference for the current NCEMS double-compression project. It preserves the section order of `analysis_plan.md`, replaces the obsolete notebook descriptions with the nine notebooks currently in `notebooks/`, and separates completed analyses from proposed extensions.

The study asks whether AI narrows collective scientific search at two stages: generation of scientific proposals and review of the same human proposals. The current paper reports four diversity facets (spread, richness, evenness, coverage) plus displacement. The computational pipeline additionally retains dimensionality. The primary text branch is `rephrased`; `original` is a robustness branch.

The main empirical pattern is lower proposal spread and richness under all three conditions on the primary branch, disproportionate omission of peripheral human ideas, and lower within-proposal AI review diversity under the two structured conditions. Numeric AI scores show no detectable funding signal, but the sample does not establish a human-versus-AI accuracy difference. These are findings about this corpus and representation, not direct measurements of scientific value or downstream discovery.

### Evidence and scope

Sources used, in order of role:

| Source | Role |
|---|---|
| `notebooks/*.ipynb` and their imported `src/` modules | Implemented workflow, configuration, contracts, inference, and figure construction |
| `data/NCEMS-data/prepared/` and `results/tables/` | Current stored records, model metadata, manifests, and numerical results |
| `docs/drafts/2026-08-24_facet_diversity_audited_results.md` | Comprehensive results narrative, including August 30 core–edge and August 31 manuscript-scope updates |
| `docs/writing/double compression/human vs AI draft-JMO+BUcomments.docx` | Current paper framing, results, methods, and collaborator revisions |
| `docs/drafts/draft2_aug30.md` | Markdown manuscript counterpart |
| `docs/plans/paper_figure_Build_Specification.md` | Main-paper figure scope and panel arrangement |
| `docs/plans/analysis_plan.md` | Section structure only; its older findings are not inherited as current evidence |

This document records a read-only inspection of source, saved notebook outputs, prepared metadata, and exported tables. No model calls, embedding rebuilds, or full statistical reruns were performed to prepare it. “Completed” means implemented with stored outputs, not freshly reproduced on this date. Tables below identify whether values were read directly from CSVs or summarized from the audited report.

### Current execution status

The NCEMS analysis and production-figure code are implemented and results are stored. **A clean end-to-end rerun is not yet established for the current directory layout.** Data now resides under `data/NCEMS-data/`, while notebooks and several helpers still construct paths under `data/prepared/`, `data/ai-proposals/`, `data/reviews/`, and `data/literature/`. Stored manifests also contain old absolute paths. Resolve the data root and manifest references before rerunning; do not treat a saved success output as proof that the current checkout runs unchanged.

Three additional qualifications affect alignment with the paper:

1. Prepared proposal metadata records different exact model versions at baseline versus the structured conditions. Condition contrasts therefore do not isolate prompting from model version.
2. Pooled-AI proposal inference and plotted uncertainty are based on without-replacement subsamples, whereas the paper and audit sometimes describe all proposal inference as permutation tests with jackknife intervals.
3. The review statistic labeled “Cliff’s δ” is implemented as the balance of positive and negative paired differences. Preserve its stored values, but reconcile the statistical name before publication.

These are documented discrepancies, not changes to the stored results.

## Data Used (Actual)

### Corpus and analysis units

| Data component | Stored or reported scope | Analysis unit and qualification |
|---|---|---|
| Human proposals | 23: 12 in cohort y1, 11 in y2 | Shared human reference across conditions; not 69 independent human observations |
| AI proposals | 23 per model family per condition; 69 per condition | 92 rows including humans in each prepared proposal master; 207 AI proposals across three conditions |
| Human reviews | 85; 2–5 per proposal; mean 3.70 | Within-proposal panels, paired against AI panels |
| AI reviews | 5 per model per human proposal; 345 per condition | 430 rows including humans in each review master; 1,035 AI reviews across conditions |
| Human numeric scores | 14 proposals with at least one score; 13 with at least two | AUC/means use 14; within-panel score variance uses 13; score panels contain 1–4 scored reviews |
| Funding outcomes | 14 funded, 9 not funded, among all 23 proposals | Human scored subset has 8 funded and 6 not funded |
| Reference literature | 39,538 articles in the literature manifest | BioLinkBERT-large reference embeddings; 12 non-outlier BERTopic regions; MeSH index available |
| Text representations | `original`, `rephrased` | Same underlying records, not independent samples |
| Review fields | `whole`, `strengths`, `weakness` | Whole text on both branches; section analyses on rephrased text only |

The manuscript describes human submissions from 2022 and late 2023. This remains a manuscript-level provenance statement; the numerical result tables do not independently establish submission dates, reviewer eminence, consent, or access arrangements. Final data documentation should establish these from the program records.

### Model versions and generation settings

The following version IDs were read from the current prepared masters, rather than inferred from family labels:

| Task and condition | Claude | Gemini | GPT |
|---|---|---|---|
| Proposals, baseline | `claude-opus-4-5` | `gemini-3-pro-preview` | `gpt-5.2` |
| Proposals, one-at-a-time | `claude-sonnet-5` | `gemini-3.1-pro-preview` | `gpt-5.5` |
| Proposals, persona | `claude-sonnet-5` | `gemini-3.1-pro-preview` | `gpt-5.5` |
| Reviews, all three conditions | `claude-sonnet-5` | `gemini-3.1-pro-preview` | `gpt-5.5` |

Proposal versions come from `proposal_master.csv:model`; review versions come from `review_master.csv:evaluator_model`, under `data/NCEMS-data/prepared/{condition}/{task}/rephrased/`. These are recorded metadata identifiers, not independently verified provider histories. They establish that the stored baseline-versus-structured proposal comparison is not a fixed-version prompt intervention.

Current notebook settings use generation temperature 0.9 in both `00a` and `00b`. Proposal token caps are 8,000 for ideas and 16,000 for expansion; reviews use 12,000. `00c` uses `gemini-3.1-pro-preview`, temperature 0, with proposal/review token caps 12,000/4,000. Current settings must not be retroactively attributed to every historical run without checking its logs and metadata.

### Data locations and provenance

Actual NCEMS storage is `data/NCEMS-data/{ai-proposals,human-proposals,reviews,literature,prepared,embeddings}` with call material at `data/NCEMS-data/call_and_info.json`. `data/NOVO-data/` belongs to the prospective archive extension; its presence does not establish completed analyses.

Saved preparation outputs reference baseline AI proposals with run ID `20260209_205423`, structured-condition proposals with `20260709_095141`, and corrected AI reviews with `20260715_212424`; rephrased review filenames include July 16 timestamps. The audit describes the corrected-review regeneration as July 16. Retain both the actual filenames and that audit history rather than treating a filename date as a complete execution chronology.

## Prepared Data Inventory (`01a` / `01b`)

In this section, **D = `data/NCEMS-data`**, **C = condition**, and **B = text branch**. These are current storage locations. The notebook source still targets the corresponding paths without `NCEMS-data`, which is an outstanding migration issue.

| Prepared artifact | Contents and contract | Producer → consumer |
|---|---|---|
| `D/prepared/C/proposals/B/proposal_master.csv` and JSON companion | Human/AI text and metadata; 92 rows; stable `proposal_uid`, source family, exact model | `01a` → `02`, `04`, figure builders |
| `proposal_embeddings_full.pkl` | Full-proposal, mean-pooled, L2-normalized BioLinkBERT-large embeddings, 1,024 dimensions | `01a` → proposal facets |
| `proposal_embeddings_abstract.pkl` | Abstract/Section-1 representation comparable with literature abstracts | `01a` → literature coverage and mapping |
| `proposal_pairwise_cosine_{full,abstract}.npy` | Pairwise cosine-distance matrices aligned to the master | `01a` → analysis and geometry builders |
| `proposal_to_literature_knn.npz` | Abstract-to-literature nearest-neighbor cache, maximum k=50 | `01a` → M6 domain coverage |
| `proposal_umap_reducer.pkl`, `proposal_umap2d.npy` | Cached proposal-space display coordinates | `01a` → diagnostic plots |
| `subsample_idx_ai_n23_seed42.npy` | 1,000 draws of 23 AI rows without replacement from the 69-row pool | `01a` → pooled-AI inference in `02` |
| `prepare_manifest.json` in each proposal branch | Input files, row order, dimensions, normalization, artifact references, subsample metadata | `01a` → contract assertions in `02` |
| `D/prepared/C/reviews/B/review_master.csv` and JSON companion | 430 reviews, stable `review_uid`, target proposal, reviewer/model, text and scores | `01b` → `03` |
| `review_embeddings_text.pkl`, `review_pairwise_cosine_text.npy` | Whole-review vectors and distances aligned to the master | `01b` → review facets |
| `review_embeddings_{strengths,weakness}.pkl`, corresponding distance matrices | Separate section embeddings; rephrased branch only | `01b` → field-specific review facets |
| `review_panels_exact_n.pkl` | Per-target human indices and same-size pooled/per-model AI panel combinations | `01b` → matched-panel inference in `03` |
| `review_panel_distance_cache.pkl` | Cached within-target review distances | `01b` → review analysis |
| `review_umap_reducer.pkl`, `review_umap2d.npy` | Review display coordinates | `01b` → diagnostic plots |
| Review `prepare_manifest.json` | UID order, normalization, available fields and cache references | `01b` → assertions in `03` |
| `D/prepared/C/reviews/review_panel_registry.csv` | Panel eligibility and target linkage | `01b` → panel checks |
| `review_sampling_frame.csv` | Sampling metadata for target panels | `01b` → matched analyses |
| `proposal_review_scores_summary.csv` | Proposal outcomes/ranking and score summaries | `01b` → decision analysis |
| `D/prepared/literature/literature_corpus_prepared.json`, `literature_article_index.csv` | Frozen reference records and embedding alignment | `01a` → literature analyses |
| `literature_mesh_index.parquet` | Article-to-MeSH mapping | `01a` → M6 MeSH coverage |
| `lit_bertopic_assignments.csv`, `lit_bertopic_topic_info.csv` | Article region assignments and region metadata | `01a` → M6, Figure 3A |
| `literature_prepare_manifest.json` | Corpus hash, 39,538 articles, 12 regions, MeSH availability and map readiness | `01a` → provenance and assertions |
| `D/embeddings/literature/relevant_literature_embeddings.pkl` | Normalized literature vectors | `01a` → abstract-to-literature comparisons |
| `lit_bertopic_model.pkl`, `lit_umap_reducer.pkl`, `lit_umap2d.npy` | Frozen region model and literature display map | `01a` → mapping and visualization |

### Preparation sections replacing the old single notebook

`01a` prepares the shared literature corpus and maps, then processes all condition × branch proposal masters, embeddings, distance matrices, nearest-neighbor caches, manifests, and pooled subsamples. `01b` prepares review masters, whole/section embeddings, exact-n panels, score summaries, and manifests. Neither stage estimates the paper’s headline group contrasts.

Full-proposal embeddings are used for proposal-set diversity. Abstract-only proposal embeddings are used against literature abstracts. Literature regions are defined from the reference corpus, not fitted jointly with proposal groups. Cosine **distance is 0 for identical normalized vectors**; cosine similarity is 1. UMAP is a display representation, not the space in which facet tests are performed.

### Output table inventory

Current results are read from `results/tables/{C}/{task}/{B}/`:

| File | Meaning |
|---|---|
| `facet_diversity_tests.csv` | Facet values, effects, primary flags, inference labels, p-values, uncertainty, sample sizes and parameters |
| `facet_review_paired_long.csv` | Per-proposal human/AI review values and paired differences |
| `facet_diversity_gradient.csv` | Model-ordering tests and direction checks |
| `facet_diversity_curves.parquet` | Curves and subsample distributions for plotting |
| `facet_null_reference.parquet` | Proposal null-reference draws |
| `facet_fingerprint.csv` | Direction-aligned diagnostic summaries |
| `facet_interleaving.csv` | Cross-group nearest-neighbor and exclusive-territory diagnostics |
| `simpson_diversity.csv` | Embedding and, where applicable, categorical diversity outputs |

Cross-condition exports are under `results/tables/cross_condition/`. Review-specific files include `score_decision_analysis.csv`, `claim_uniqueness.csv`, `claim_uniqueness_examples.csv`, `decision_outcome_{proposal_scores,curves,summary}.csv`, and `decision_outcome_matched_auc.csv`. Synthesis writes `results/tables/synthesis/{B}/double_compression_summary.csv` and `results/tables/synthesis/core_edge_{B}.csv`.

Do not substitute old `.../{B}/facet/` tables or legacy `rephrased/minimal/` outputs for the current tables. Retained files are not proof that the current workflow still writes them.

## Experiment Conditions

| Condition | Proposal elicitation | Review elicitation |
|---|---|---|
| `baseline` | A batch of 23 ideas in one model call, followed by the proposal-expansion stage | Five reviews of a target proposal in one call per model |
| `one_at_a_time` | Independent idea calls, then expansion into full proposals | Five independent review calls per model per target |
| `persona` | Independent calls grounded in scientist-team persona cards, then expansion with persona context where configured | Independent review calls using the reviewer-persona schedule |

All conditions use the same task-level call or review criteria, but this does not imply equal background information, incentives, or exact model versions. The generator explicitly separates **Pass A: ideas** from **Pass B: full proposals**. The paper’s “one request generates 23 proposals” is a shorthand for the batch condition, not a literal description of the full two-pass implementation.

Personas provide scientific context from publication records. They are prompt conditioning, not demonstrated model fine-tuning or training. The manuscript’s “top five cited papers” wording requires reconciliation with the actual card construction and retrieval records; do not infer citation-ranked selection from the existence of publication-based cards. Reviewer personas and applicant-team personas have separate rosters.

The human set is fixed across conditions. Each condition’s pooled AI comparison draws 23 from 69 proposals without replacement. Reviews compare panels within the same human proposal, matching the number of textual human reviews. Score-based analyses instead match available **scored** human reviews where required.

### Cross-condition comparison plan

The three conditions have stored results and are no longer “not yet executed,” as in the old plan. Compare their effects within each task and branch, preserving the shared human reference. Do not pool repeated human rows as additional independent observations. Do not treat changes between baseline and structured proposal conditions as a causal prompting gradient until the version mismatch is resolved.

`facet_diversity_gradient.csv` includes the prespecified model-ordering check; that is distinct from a causal test of condition effects. The audit reports no stable Claude < Gemini < GPT ordering. Descriptive changes across conditions and model-ordering tests answer different questions.

Current execution selections are narrower than supported scope: `00a` selects only `one_at_a_time` and `persona`; `00b` selects all three; `00c` currently selects no proposal conditions and all three review conditions. `01a`, `01b`, `02`, and `03` select all three conditions and both text branches. A “Run All” action does not automatically regenerate every historical input.

## Completed Analyses and Results

### Facet definitions and reference values

| Facet/check | Primary operational measure | Reference and interpretation |
|---|---|---|
| Spread | Mean pairwise cosine distance within a set/panel | Larger values mean more dispersed representations |
| Richness | Vendi score at q=1 from the similarity spectrum | Effective diversity, not a manually counted set of distinct scientific contributions |
| Evenness | Integrated close-neighbor excess relative to same-size pooled draws | Positive means excess clumping; negative means more regular spacing |
| Geometric coverage | Neighborhood coverage of human representations by AI | Proposal human split-half reference; review human leave-one-out self-coverage reference, reported near 0.83 |
| Domain coverage | Literature region and MeSH breadth; effective region occupancy | Proposal abstracts mapped to literature; breadth and even occupancy are separate quantities |
| Dimensionality | Participation ratio; effective rank as an alternative | Number of effective variation directions; retained in computation, omitted from main paper |
| Displacement | Kernel MMD², cross-checked by optimal-transport distance | Separate cloud-position check, not another diversity facet; pooled reference differs from per-model permutation inference |

### Statistical reading conventions

The computational primary set is spread/mean pairwise, richness/Vendi q=1, evenness/Ripley excess, dimensionality/participation ratio, geometric coverage, and displacement/MMD². The paper omits dimensionality and presents five primary comparisons across four facets plus displacement. Primary rows use `p_raw`; secondary rows use Benjamini–Hochberg correction within task × branch × field, pooling the relevant condition/model rows. These are pipeline-designated primaries; the repository designation alone does not establish an external preregistration.

For spread and richness, manuscript effects are **AI ÷ human**. The raw proposal table’s `effect_size` often stores the inverse **human ÷ AI**. Compute the manuscript ratio from `ai_value / human_value`; never copy the raw column without checking `effect_type` and metric. Coverage, clumping, and displacement have their own units and reference values.

Review δ is oriented AI minus human: negative means lower AI diversity for spread/richness. Positive evenness δ means more clumping; positive coverage δ means more human-review span covered. In `src/diversity_inference.py:paired_wilcoxon`, the implemented effect is `(number of positive differences − number of negative differences) / number of nonzero differences`, with orientation reversed for the AI comparison. It is a paired sign-balance effect, despite the “Cliff’s δ” table label and a rank-biserial helper docstring. Wilcoxon uses `mode="auto"`, not an unconditional exact-test setting.

Individual-model proposal facet comparisons generally use label permutations and jackknife estimates. **Pooled proposal spread/richness use 1,000 without-replacement subsamples**, an empirical directional tail proportion, and percentile limits of the subsample values. Pooled displacement is referenced against a human split-half floor. `B_perm=10,000` in notebook configuration does not mean every row used 10,000 label permutations. The exported `inference` field and source helper identify the procedure for each row.

AUC uncertainty is different: a stratified bootstrap resamples proposals **with replacement**, and label permutations test funding discrimination. The no-replacement rule for diversity sets must not be stated as a universal ban on bootstrap resampling throughout the project.

### Compact Results Table

The following headline tables are transcribed programmatically from current per-condition CSVs. Values are rounded; p-values are the exported raw primary p-values. They reproduce the main audited/paper pattern without relabeling the implemented tests.

#### Generation primary results

| Metric | Baseline | One-at-a-time | Persona |
|---|---|---|---|
| Spread: AI/human ratio | 0.704 (p=0.010) | 0.644 (p=0.000999) | 0.682 (p=0.003) |
| Richness: AI/human ratio | 0.742 (p=0.005) | 0.664 (p=0.000999) | 0.751 (p=0.004) |
| Clumping: human → AI excess | -0.141 → +0.077 (p=0.000999) | -0.234 → +0.142 (p=0.000999) | -0.115 → +0.062 (p=0.000999) |
| Geometric coverage: AI value | 0.850 (p=0.038) | 0.863 (p=0.082) | 0.805 (p=0.000999) |
| Displacement: pooled MMD² | 0.037 (p=0.122) | 0.062 (p=0.122) | 0.032 (p=0.122) |

Human spread is approximately 0.41557; AI spread is 0.29257 / 0.26771 / 0.28360. Human Vendi q=1 is approximately 3.14893; pooled AI is 2.33554 / 2.09224 / 2.36475. These effective counts depend on the embedding/kernel; emphasize relative richness rather than literal counts of scientific ideas. Geometric coverage is the exported coverage value, tested against the human split-half benchmark; it is not a generic AI/human ratio.

#### Review primary results

| Whole-review facet | Baseline δ (p) | One-at-a-time δ (p) | Persona δ (p) |
|---|---|---|---|
| Spread | -0.391 (0.070) | -0.913 (7.15e-07) | -0.739 (1.03e-05) |
| Richness | -0.304 (0.092) | -0.826 (1.19e-06) | -0.739 (1.03e-05) |
| Clumping | +0.217 (0.111) | +0.913 (1.19e-06) | +0.739 (7.87e-06) |
| Coverage | +0.368 (0.004) | +0.444 (0.002) | +0.368 (0.003) |

#### Field-specific spread

| Field | Baseline δ (p) | One-at-a-time δ (p) | Persona δ (p) |
|---|---|---|---|
| whole | -0.391 (0.070) | -0.913 (7.15e-07) | -0.739 (1.03e-05) |
| strengths | +0.043 (0.777) | -0.652 (0.000408) | -0.565 (0.003) |
| weakness | -0.043 (0.286) | -0.913 (1.67e-06) | -0.913 (5.96e-06) |

#### Model-level spread and richness

The cells below show the current rephrased results as `effect (raw p)`. Proposal effects are AI/human ratios; review effects are paired δ. These are descriptive family comparisons, not a stable ranking of model capabilities.

| Task / metric | Condition | Claude | Gemini | GPT |
|---|---|---|---|---|
| proposals / spread | baseline | 0.614 (0.079) | 0.734 (0.255) | 0.775 (0.213) |
| proposals / spread | one_at_a_time | 0.814 (0.332) | 0.451 (0.020) | 0.640 (0.103) |
| proposals / spread | persona | 0.692 (0.114) | 0.503 (0.024) | 0.859 (0.385) |
| proposals / richness | baseline | 0.677 (0.056) | 0.773 (0.212) | 0.755 (0.144) |
| proposals / richness | one_at_a_time | 0.740 (0.094) | 0.563 (0.017) | 0.651 (0.031) |
| proposals / richness | persona | 0.767 (0.202) | 0.632 (0.025) | 0.856 (0.400) |
| reviews / spread | baseline | -0.739 (1.31e-05) | 0.043 (1.000) | -0.913 (1.03e-05) |
| reviews / spread | one_at_a_time | -1.000 (2.38e-07) | -1.000 (2.38e-07) | -0.913 (1.19e-06) |
| reviews / spread | persona | -0.913 (2.38e-06) | -0.739 (4.94e-05) | -1.000 (2.38e-07) |
| reviews / richness | baseline | -0.739 (1.31e-05) | 0.043 (0.917) | -0.913 (1.67e-05) |
| reviews / richness | one_at_a_time | -1.000 (2.38e-07) | -1.000 (2.38e-07) | -0.913 (1.19e-06) |
| reviews / richness | persona | -0.826 (3.34e-06) | -0.739 (3.27e-05) | -1.000 (2.38e-07) |

### Additional generation findings and literature grounding

The following supplementary findings summarize the audited report (§2, SI-1, SI-2 and SI-5), with corresponding outputs in the inventory above:

| Finding | Reported values | Interpretation |
|---|---|---|
| Effective literature regions | Human 4.94; pooled AI/human ratios 0.78 / 0.62 / 0.73 | Uneven occupancy within broadly shared topical territory |
| Region breadth | Sets touch roughly 5–8 of 12 regions; pooled one-at-a-time 5.9 versus human 7, FDR p≈0.008 | Most breadth contrasts do not survive correction |
| MeSH breadth | AI 571–598 unique terms versus human 504; reported nonsignificant | More raw terms is not evidence of broader effective conceptual diversity |
| Human-only fringe | 18–26%, versus a roughly 10% human-spacing reference | Some human proposals lack nearby AI counterparts |
| AI-only fringe | 4–9% | Asymmetry in coverage, not proof that AI has no novel ideas |
| Core–edge association | Miss-rate versus centroid distance Spearman ρ≈0.86; versus local density ≈−0.99 | Peripheral human proposals are missed more often |
| Miss-rate by density tertile | Rephrased: core 0%, middle 4%, edge 69%; original: 0%, 13%, 58% | Descriptive pattern replicated across branches |
| Funding quality guard | Funded/rejected miss-rate 0.20/0.26; Mann–Whitney p≈0.77 | No detected funding association; does not prove equal scientific quality |
| Embedding inverse Simpson | Pooled/human ratios ≈0.76 / 0.73 / 0.76 | Converges with Vendi richness; distinct from categorical region Simpson |
| Lexical controls | Persona brings wording closer to parity; semantic gaps remain | Wording and embedding diversity are different measurements |

Order throughout is baseline / one-at-a-time / persona. Core–edge outputs are in `results/tables/synthesis/core_edge_{B}.csv`, produced by the builder invoked from `04`.

Non-significant displacement does not prove equivalence, concentricity, or identical radial extent. Likewise, human-only and human–AI distance calculations share the human representation and geometric yardstick: the paper/audit phrase “share no inputs” is too strong. The core–edge association remains an observed relationship, but its construction alone does not establish independence or eliminate geometric coupling.

### Review fields, scores, claims, and decisions

The structured-condition review result is strongest in criticism: reported weakness spread δ≈−0.91 in both conditions, versus strengths −0.65 and −0.57. Human mean within-panel distances are approximately 0.044 whole, 0.069 strengths, and 0.084 weaknesses. Baseline pooled whole/section spread and richness are not significant; Gemini at baseline offsets the compression of other model families. Do not claim every model/condition cell is significant.

The audit’s score analysis reports human panel score SD≈0.74, versus pooled AI 0.51 / 0.34 / 0.29. Paired effects are approximately −0.23 (baseline p≈0.09), −0.85, and −0.85. Only 13 proposals support score-variance comparisons. Human–AI panel-mean rank agreement is approximately 0.46 / 0.44 / 0.43, against a noisy human split-half reference near 0.40; this does not demonstrate harmful ranking divergence.

Claim uniqueness is computed separately for strengths and weaknesses at matched panel size. Human unmatched claims are approximately 40–58%; AI unmatched claims 41–58%. Against the full 15-review AI reservoir, human unmatched claims fall to 16–32%. These are different panel-size questions. Nearest-claim semantic matching is not an expert validation of claim truth, importance, or whether a decisive scientific flaw was recognized.

| Panel | AUC | 95% stratified-bootstrap interval | Permutation p | Scored proposals |
|---|---|---|---|---|
| Human / all | 0.771 | [0.479, 1.000] | 0.089 | 14 |
| AI / baseline | 0.504 | [0.246, 0.746] | 0.990 | 23 |
| AI / one_at_a_time | 0.472 | [0.218, 0.722] | 0.839 | 23 |
| AI / persona | 0.504 | [0.246, 0.762] | 0.988 | 23 |

Source: `results/tables/cross_condition/reviews/decision_outcome_summary.csv`. These headline AUC panels are unmatched: AI uses 15 reviews over all 23 proposals; humans use their available scores over 14. The matched decomposition reports pooled AI AUC approximately 0.50 / 0.45 / 0.50 when both the proposal set and scored panel sizes are matched, with wide intervals spanning chance. All A/B/C and per-model estimates remain in `decision_outcome_matched_auc.csv`.

The reported AI rank-aggregation curve rises initially and reaches approximately ρ=0.41–0.43 by eight reviews. It does **not** “plateau at chance.” Human agreement rises over the available range, but the human sample shrinks from 14 proposals at k=1 to 6 at k=4, and the target ranking arose from human review. These curves cannot establish a clean causal effect of independent judgment on decision accuracy.

### Robustness and secondary analyses

Original-text results are a robustness comparison, not an independent replication. The audit reports pooled original-text proposal spread ratios 1.02 / 0.28 / 0.69 and richness ratios 0.96 / 0.69 / 0.86. Baseline spread/richness are nonsignificant on raw text, unlike rephrased text. Original review spread δ is approximately +0.04 / −0.91 / −0.91. Thus structured-condition compression and core–edge geometry recur, but the claim that every generation effect is invariant to normalization is unsupported.

Dimensionality remains computed and should remain in the reproducibility record. It is not uniformly null across all cells: the audited pooled rephrased proposal ratio is 0.85 under one-at-a-time and significant, while baseline/persona are nonsignificant; review whole-field dimensionality is near zero. Its exclusion from the main paper is a reporting-scope decision, not grounds to erase its results.

Other completed diagnostics include alternative spread estimators, Vendi orders and slope, kernel/neighborhood sensitivity, coverage/density, MMD² and optimal transport, interleaving, lexical diversity/self-BLEU, convergence plots, and model-ordering tests. The audit reports generation ordering direction correct in only 3 of 36 cells and no significant review ordering in 15 cells. Do not rank the three families as a stable performance hierarchy.

### Paper alignment and reconciliation register

| Topic | Supported account for this plan | Paper/audit wording requiring reconciliation |
|---|---|---|
| Overall result | Lower spread/richness; sparse-edge coverage loss; structured review convergence | Do not equate embedding spread with a literal count of scientific discoveries |
| Richness reduction | Roughly 25–34% lower Vendi richness; spread roughly 30–36% lower | “25–36% fewer distinct ideas” combines two different measures |
| Review target | Current `00b` reviews human proposals only | Abstract claims about ranking own AI proposals highest are not supported by this current review workflow |
| Calls | Baseline batch elicitation; structured independent calls; two-pass proposals | “All prompting was independent” and a single-call account of the full proposal pipeline are inaccurate |
| Model versions | Baseline proposal versions differ from the structured versions | Prompt-only causal language requires fixed-version evidence |
| Persona | Publication-grounded prompt context | “Trained beforehand” and “top cited” need separate evidence |
| Primary inference | Row-specific methods, including pooled subsample tail proportions | Blanket “10,000 permutations” is inaccurate for pooled headline rows |
| Figure 2 intervals | Exported pooled subsample percentile limits divided by the human value | Blanket “jackknife 95% intervals” does not describe current pooled production bars |
| Review effect | Stored paired sign-balance statistic | Reconcile “Cliff’s δ,” rank-biserial, and exact-Wilcoxon labels |
| Core–edge | Association in shared embedding geometry | “No shared inputs” and “not circular by construction” overstate independence |
| Missed proposals | No detected funding/ranking difference | “Highly ranked” as a selective enrichment claim is not established; the DOCX limitation saying “detectably less successful” contradicts the null result |
| Funding | No detectable AI signal; broad intervals; human superiority unresolved | “Cannot identify funded proposals” or claims of worse accuracy are too strong |
| Rank aggregation | Positive agreement that flattens early | “Leveled off to chance” contradicts the positive correlation values |
| Synthesis | Reuses facet tables and derives additional core–edge/region summaries | “04 adds no statistics” is no longer a complete description |
| Confidentiality | Restricted corpus and low apparent leakage risk | Confidentiality alone does not prove absence from every training corpus |

This register preserves alignment with the paper’s numerical findings while making disagreements visible. It does not silently endorse conflicting wording or change the manuscript.

## Data Visualization Guide

### Color Scheme and Metadata Encoding

Use the shared `src/plotting.py` palette for diagnostics and the production helpers for main figures. Human is red; pooled AI is blue. Production spread/richness use `#08519c` and `#6baed6`. Conditions retain baseline → one-at-a-time → persona order. Family-specific colors are appropriate for supplements, but pooled effects lead the main paper.

Funding/top-rank outlines require explicit legends and should only appear on actual proposal-level points. Do not transfer funding rings to pairwise distances or subsample draws. A fringe outline marks geometric unmatchedness, not funding status or quality.

### Standard Boxplot Grammar

Boxes show median/IQR and the stated whisker rule; jittered points show the unit named in the caption. In Figure 3A, points are matched-n subsample draws. In Figure 4A, points represent proposals. These are different sampling units and must not be described interchangeably. State whether an overlaid marker shows mean ± SD, percentile limits, or another interval.

The old plan’s default “bootstrapped mean diamond” is not universal. In particular, do not bootstrap diversity sets with replacement, and do not label the current pooled proposal percentile bars as jackknife intervals.

### Violin, Ridge, and Histogram Views

Use distribution plots for descriptive diagnostics. Pairwise distances are dependent observations; a ridge plot’s many pairs are not an enlarged inferential sample size. Keep consistent scales/binning when comparing groups and label the unit.

### UMAP and Embedding-Space Projections

Use cached coordinates and a frozen literature map. Literature overlays use abstract-only proposal vectors; proposal-only geometry uses full proposals. Compute inference in the original embedding space. Neither apparent UMAP overlap nor separated islands is itself evidence of equality or statistical displacement. The main Figure 3 is effective-region occupancy plus core–edge geometry; projection plots are supplementary.

### Effect-Size and Significance Panels

Proposal spread/richness use AI/human ratios with parity 1. Review spread/richness use paired δ with parity 0. Do not put these on one undifferentiated numerical axis. Explicitly state clumping and coverage direction. Primary versus FDR-corrected p-values must follow the source row. A null result is not an equivalence test.

### Labels, Legends, and Export Standards

Use descriptive axes and captions stating sample size, unit, branch, condition, uncertainty, and test. Keep main-paper numbering separate from diagnostic filenames beginning `fig1`, `fig2`, etc. Main outputs are `results/figures/production/Fig1.png` through `Fig4.png`, plus individual panels. Branch-specific diagnostics and supplements are under `results/figures/synthesis/{B}/` and condition/task/branch directories. `05` defaults to rephrased; its production directory is not branch-scoped, so switching branches can overwrite main outputs.

| Main figure | Current panel content | Source/build route |
|---|---|---|
| Figure 1 | Design, corpus, conditions, matched comparisons | `fig1_design_schematic` via `05` |
| Figure 2A | Pooled spread and richness ratios | Facet CSVs → `production_figures._draw_spread_richness` |
| Figure 2B | Human/AI close-neighbor excess | Facet CSVs → evenness helper |
| Figure 2C | Wording versus idea diversity | Production wording helper |
| Figure 3A | Effective literature regions at matched n | `figure3_regions.build_panel_a` |
| Figure 3B | Core–edge miss-rate, tertiles and asymmetry | `core_edge_analysis.build_panel_b` |
| Figure 4A | Within-proposal review spread across conditions | Paired review outputs → production helper |
| Figure 4B | Whole/strengths/weakness effects | Field-specific facet rows |
| Figure 4C | Funding AUC and uncertainty | `decision_outcome_summary.csv` |

The near-duplicate curve is retained as an optional alternate, not a fourth main Figure 2 panel. Claim uniqueness and rank aggregation belong in SI. Notebook `05` still contains a stale markdown description of four Figure 2 panels; its code/output filenames and the revised figure spec describe the implemented three-panel figure.

## Notebooks and analyses

### End-to-end dependency map

```text
Human proposals + call + applicant personas ──> 00a: AI ideas → full proposals
Human proposals + criteria + reviewer personas ──> 00b: AI reviews
Human originals + AI originals ──> 00c: rephrased text

Proposal originals/rephrases + literature ──> 01a: proposal/literature preparation
Review originals/rephrases + target metadata ──> 01b: review/panel preparation

01a ──> 02: proposal facets and supplementary statistics
01b ──> 03: review facets, scores, claims and outcomes
02 + 03 + prepared geometry ──> 04: synthesis, core–edge and region summaries
02 + 03 outputs + prepared artifacts/builders ──> 05: production Figures 1–4
```

Run preparation before analyses, and `04` before the final production build so the synthesis records are current. `00a` and `00b` are separate generation branches; `00b` evaluates human proposals and does not require AI proposals from `00a`. `01b` also uses proposal metadata to link targets/outcomes. Existing validated generated text can be reused without new paid generation calls.

### `00a_gen_proposals.ipynb`

**Purpose:** Generate original AI ideas, then expand each into a full proposal with the same model. Imports `proposal_generation` helpers and persona/call data. It does not normalize style, embed, or analyze.

**Stages:** Load human target roster and call; validate persona count against 23 targets; resolve model IDs; optionally test calls; complete Pass A for selected conditions; persist ideas; run Pass B expansion; validate counts and save progress/completion summaries. Preserve idea-call and proposal-call identifiers, persona IDs, and model version metadata.

**Current selection:** one-at-a-time and persona, three newer model IDs, temperature 0.9, resumable execution, tests disabled. Baseline is supported by helpers but is not selected in this saved configuration.

**Outputs:** Condition-specific `ai_ideas_*`, proposal progress and complete files under the AI-proposal data tree. Consumers are `00c` and `01a`. Stored baseline proposals originate from an earlier run and older versions. Do not overwrite them without defining a new analysis version.

### `00b_gen_reviews.ipynb`

**Purpose:** Generate original NCEMS-criteria reviews of the 23 human proposals. It does not run the old novelty-review framework or review all 92 human/AI proposals.

**Stages:** Load human target roster and review criteria; load reviewer personas and schedule; resolve models; optionally test; generate five reviews per model per target according to condition; validate/persist schedules, progress, and complete review records.

**Current selection:** all three conditions; temperature 0.9; five reviews; same three newer model IDs. Consumers are `00c` and `01b`. Expect 345 AI reviews per condition. The corrected-prompt review corpus, rather than earlier review outputs, is the basis of current results.

### `00c_rephrase.ipynb`

**Purpose:** Build the standardized text branch while retaining original records. Handles AI proposals, AI reviews, shared human proposals, and shared human reviews.

**Stages:** Resolve source files; normalize selected corpora with Gemini; save rephrased records, progress/failure information and alignment fields. Preserve scores and target/record identities through rewriting; rephrasing does not create independent observations.

**Current selection:** AI proposal conditions `[]`, AI review conditions all three; Gemini version and temperature as documented above. Consumers are both preparation notebooks. Rephrasing is a measurement control, not proof that content is unaffected or that all embedding bias has been removed.

### `01a_prepare_proposal_for_analysis.ipynb`

**Purpose:** Prepare reusable proposal and literature artifacts for all three conditions and both branches.

**Stages:** Load and align original/rephrased human and AI proposals; prepare literature records and normalized embeddings; build MeSH and frozen BERTopic/UMAP artifacts; assemble 92-row masters; compute full and abstract embeddings and pairwise distances; cache abstract-to-literature neighbors (k=50); write manifests and 1,000 pooled-AI subsample indices.

**Checks:** Original/rephrased identity alignment, required metadata, normalized embeddings, stable row order, 23 proposals per AI family, correct subsample shape. Failures in literature preparation must be resolved before M6 is interpreted.

**Consumers:** `02`, `04`, and geometry/production helpers. The notebook title still says “4a”; the current filename is `01a`. Cached absolute paths need migration with the data root.

### `01b_prepare_review_for_analysis.ipynb`

**Purpose:** Prepare matched target panels, whole and section representations, and score/outcome linkage.

**Stages:** Load original/rephrased human reviews and condition-specific AI reviews; validate alignment; merge target metadata; build 430-row masters; embed whole reviews; embed strengths/weakness on rephrased text; calculate distance matrices; enumerate exact-n panels; save manifests, registry, sampling frame and proposal score summaries.

**Checks:** Stable `review_uid` order, target linkage, field availability, normalized vectors, consistent originals/rephrases. Exact-n textual panels and scored panels differ where human numeric scores are missing.

**Consumer:** `03`. The notebook title and some downstream messages still say “4b.”

### `02_facets_proposals.ipynb`

**Purpose:** Estimate generation-side facets in full embedding space and domain coverage against literature. Loops over three conditions × two branches; field is `whole`.

**Sections and outputs:**

1. **Load:** Check manifests, row order, normalization, model counts, and 1,000×23 subsample indices.
2. **M0–M5:** Spread, Vendi richness, geometric coverage/density, dimensionality, evenness, displacement; retain primary and secondary estimators.
3. **M6:** Literature region/MeSH coverage using abstract-to-literature cache, with k=5,10,20 sensitivity.
4. **Interleaving:** Human/AI nearest-neighbor and fringe diagnostics.
5. **FDR and convergence:** Apply secondary-family corrections, compare estimators, retain model-ordering/direction checks.
6. **Simpson:** Embedding diversity and categorical domain counterparts.
7. **Export and figures:** Tidy tables, distributions, fingerprints, diagnostic figures and cross-condition summaries.

`RUN_OT=True`, `WRITE_FIGURES=True`, seed 42, configured `B_perm=10,000`, `B_sub=1,000`; individual procedures can use different draw counts. Main helper: `src/diversity_inference.py`, with facet and plotting helpers. The notebook does not estimate the funding-outcome analysis.

### `03_facets_reviews.ipynb`

**Purpose:** Compute within-target review diversity and supplementary score/claim/outcome analyses. Loops over condition × branch × available field; no literature M6 for reviews.

**Sections and outputs:**

1. **Load/panels:** Assert prep contract; convert row-index panels into UID combinations; compute per-target human and equal-size AI facets, then paired effects.
2. **Interleaving:** Review-cloud geometric overlap and exclusive territory.
3. **Score-level decision analysis:** Matched score SD, human–AI ranking agreement, human split-half reference, disagreement/divergence checks.
4. **Decision outcome:** Mean scores versus funding AUC, stratified-bootstrap intervals, label-permutation p-values, rank curves and between-proposal score variation.
5. **Matched outcome decomposition:** A = all 23 proposals/full AI reservoir; B = 14 human-scored proposals/full reservoir; C = same 14 proposals/exact scored human panel sizes, 2,000 draws.
6. **Claim uniqueness:** Sentence-level strengths/weakness matching, human-calibrated thresholds, exact-n and full-reservoir comparisons.
7. **Simpson, exports, figures, cross-condition summaries:** Preserve full field axis and paired-long tables.

Score/outcome data are branch-invariant; these analyses are stored once through the rephrased workflow. Section/claim analyses depend on rephrased fields. Main helpers include `diversity_inference`, `decision_outcome`, and `claim_uniqueness`. Numeric-score sample sizes must be displayed separately from the 23-proposal semantic sample.

### `04_synthesis.ipynb`

**Purpose:** Integrate proposal/review tables into readable summaries, diagnostic figures and supplements. It does not rerun the M0–M6 facet battery.

**Stages:** Read tidy tables and optional claim/decision/Simpson outputs; construct direction-aware ratio/effect summaries; build synthesis and robustness figures; generate proposal-geometry and within-target review views; invoke `core_edge_analysis.build_panel_b` and `figure3_regions.build_panel_a` per branch; export the synthesis summary.

**Important distinction:** Most operations are display/aggregation, but core–edge and effective-region builders derive additional summaries from prepared geometry and records. Thus “display only, adds no statistics” is outdated. Data-root migration affects these builders too.

**Outputs:** `results/tables/synthesis/{B}/double_compression_summary.csv`, `core_edge_{B}.csv`, and `results/figures/synthesis/{B}/` figure families. These include diagnostic figure numbers that are not the main-paper numbering.

### `05_build_production_figures.ipynb`

**Purpose:** Build main Figures 1–4 and their individual panels using `production_figures`, `figure3_regions`, and `core_edge_analysis`.

**Stages:** Set branch (default rephrased); build design schematic; call `fig2a`, `fig2b`, `fig2c` and compose Figure 2; build region/core–edge panels and compose Figure 3; build convergence/field/AUC panels and compose Figure 4; list exported PNGs. The core–edge production call sets `write_table=False`.

**Outputs:** `results/figures/production/` with composed figures and panel PNGs, including `Fig2C_wording.png`. The saved output still mentions an old checkout named `human-AI-proposal-comparison`; that is historical execution output, not the present root. Some panels require prepared data, so the existence of results CSVs alone is insufficient for a clean rebuild.

## Updated Overall Story

The current NCEMS results support a bounded double-compression account. After style normalization, AI proposal sets have less spread and effective richness at matched size. They broadly engage the same literature regions but distribute their proposals less evenly and disproportionately miss peripheral human proposals. Independent and persona-conditioned generation do not eliminate the observed gaps, although the baseline comparison also differs in exact model versions.

For reviews of the same human proposal, structured AI panels are more homogeneous in text and scores, especially in weaknesses. Broad geometric coverage does not imply that AI includes every human critique: matched claim analysis finds unmatched content in both directions. The result concerns the variety of judgments supplied to deliberation, not a demonstrated loss of funding accuracy.

AI score AUC estimates are near 0.5, with wide intervals, and remain near that level after matching. Human superiority is unresolved. Neither unmatched proposals nor semantic distinctiveness is independently validated as scientific merit, novelty, or downstream impact. These limitations are part of the current conclusion, not merely future work.

## UPDATE LOGS

### November 16, 2026 — Current-state plan v2

Preserved the original plan’s top-level sequence and visualization subheadings; replaced obsolete notebook subsections with the complete `00a`–`05` workflow. Added current data storage and path-migration status, exact version metadata, condition selectors, per-condition corpus totals, primary/secondary scope, field analyses, production figures, and the paper-alignment register. Headline facet and funding tables were read from current CSVs. No source analyses or manuscript files were modified.

### August 30–31, 2026 — Updates recorded in the audit and figure specification

Core–edge and effective-region analyses entered the current narrative and Figure 3. Figure 2 became spread/richness, evenness, and wording panels. Rank aggregation and claim uniqueness moved to SI. Dimensionality was removed from manuscript scope while retained computationally.

### August 24, 2026 — Prior results re-audit

The audited report records rechecking numerical tables, correcting primary-count descriptions, adding the review-field axis, updating ranges and figure inventories, and adding AUC uncertainty and the matched decomposition. Those historical audit statements are not a claim that this document repeated every earlier audit test.

### July 2026 — Facet rebuild and corrected reviews

The project moved from older novelty/quality notebooks to the shared facet pipeline with matched sample sizes, original/rephrased branches, and three elicitation conditions. Corrected AI review prompts replaced earlier outputs; the earlier claim of generally more diverse baseline AI panels is superseded. Baseline pooled review spread remains nonsignificant in the corrected corpus.

## Analyses From Original Plan Not Yet Done (Moved Here)

### A) Generation-condition analyses

**Completed in the current stored workflow:** all three conditions, both text branches, matched-size proposal and review facets. Remove the old blanket “not executed” label.

**Still unresolved:** a fixed-exact-model-version comparison spanning all three proposal conditions; a fully pinned source-to-result provenance manifest; and a clean rerun after the data relocation. Additional diversity-oriented prompts, retrieval/search, or higher-temperature robustness are proposed tests, not completed results of this pipeline.

### B) Novelty robustness items

Literature region/MeSH coverage, displacement, and core–edge analysis are completed. They do not subsume every legacy novelty task. The current nine notebooks do not restore the old novelty-framework review notebook as an active analysis stage. New embedding encoders, expert validation of semantic matching, and scientific-component-level novelty/quality assessment remain extensions unless separately supported by outputs.

### C) External human-review validation

The available expert corpus supports the within-proposal comparisons. Independent expert adjudication of unmatched claims, causal effects on actual allocation, multi-competition validation, and stronger accuracy comparisons remain unestablished. Existing funding labels do not make ranking correlations independent of the human process that created those labels.

### D) Planned modeling and expanded archive

The old metric-score and self-preference results should be treated as historical analyses unless explicitly rebuilt with the corrected current corpus and documented in this workflow. Current `00b` reviews human proposals, so evaluator self-preference over AI-authored proposals is not a current end-to-end result.

The November 12 new-agency protocol describes proposed work involving approximately 14,000 submissions and 600 calls (2019–2026), contribution-record extraction, stronger generation conditions, and review-recognition/appraisal analyses. Its introduction and literature review are planning material. No such new-agency findings are included here; the existence of `NOVO-data` is not evidence of execution.

## Next Priority Execution Order

1. **Reconcile the NCEMS data root and stored references.** Update path configuration consistently across notebooks and helpers, including absolute manifest/cache paths, then validate expected artifacts and UID order. This is a prerequisite to any clean rerun.
2. **Freeze the manuscript analysis provenance.** Record input file hashes, exact versions, generation/rephrasing settings, condition definitions and output linkage. Resolve or explicitly disclose baseline version differences; a new fixed-version experiment should have a distinct run namespace.
3. **Reconcile statistical and manuscript descriptions.** Correct pooled inference/interval language, the paired-effect name, all-independent-call wording, persona training/citation claims, and unsupported self-preference/funding statements. Preserve reported values unless a separately documented analysis change is made.
4. **Run preparation contract checks and rebuild dependent results as needed.** Reuse validated generated text; verify 92 proposal/430 review rows per condition, branch alignment, fields, embeddings and panels before running `02` and `03`. Compare regenerated tables against the stored reference before accepting changes.
5. **Regenerate `04` and `05` after dependencies are valid.** Confirm core–edge outputs, field labels, interval sources, main/SI numbering and branch-safe output handling; visually inspect the final figures against manuscript captions.
6. **Finalize data/methods documentation and SI.** Resolve provenance, score missingness, reviewer/process descriptions, confidential-data access, placeholders, and quantitative limitations. Keep the main conclusion scoped to the observed corpus and implemented measurements.
7. **Pursue extensions under a separate protocol.** Prioritize independent scientific-content validation and fixed-version generation tests before generalizing to the new agency archive. Report new results only after their workflow and provenance are established.
