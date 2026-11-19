# NOVO analysis plan

## Overview

**Draft date:** November 18, 2026. **Last revised:** November 19, 2026. **Status:** proposed implementation and analysis protocol; no NOVO AI generation, component extraction, embedding analysis, or hypothesis tests were run to create this plan.

This study tests whether the NCEMS double-compression findings generalize across funding calls: whether AI produces less diverse scientific proposals and whether AI reviews of the same applicant proposals provide less diverse scientific appraisals. The extension locates compression in research questions, hypotheses, methods, data, contributions, and their scientific connections, and separately tests the quality of reviewer recognition.

**The call is the replication unit.** Within a call, compare each model's proposal set with the equally sized eligible applicant set. For reviews, compare each model's panel with the eligible human panel of the same applicant proposal, then summarize proposal-level effects within the call. Call families and repeated reviewers introduce dependence that must be represented in inference.

This plan follows the broad section sequence of `analysis_plan_v2.md` and adds explicit research questions, hypotheses, schemas, prompt specifications, and implementation gates. It supersedes the illustrative NOVO workloads in the November 12 experimental protocol for this study. It does not replace the historical NCEMS results record.

**Reading guide:** [Questions and hypotheses](#research-questions-and-hypotheses) · [Current data](#data-used-actual) · [Study conditions](#experiment-conditions) · [Code changes](#concrete-code-changes) · [Prompts](#prompt-specifications) · [Execution order](#next-priority-execution-order).

### Decisions established in the discussion

- Generate each complete proposal in one pass. There is no preliminary idea/plan, expansion, critique/revision, or two-stage comparison in the current study.
- Proposal and review generation both use `gpt-6.2-astra`, `gemini-4-carbon`, and `claude-fable-5-2`, with each model analyzed separately.
- Each model generates **N_c proposals per call per condition**, where N_c is the eligible applicant proposal count for call c. There is no universal target of ten or twenty proposals.
- Each model generates **R_ci reviews of applicant proposal i**, where R_ci is the number of eligible distinct human assessors with an admissible assessment of that proposal.
- Three model families therefore contribute 3N_c proposals and 3 × sum_i(R_ci) reviews per condition. These are three matched comparisons, not one 3N_c-versus-N_c comparison.
- Exactly three proposal conditions (G-independent, G-persona, G-sequential-different) and three review conditions (R-independent, R-persona, R-focus-diverse) are specified.
- Independent call-only generation and independent review are the primary NOVO conditions. Persona conditions test expertise conditioning. Sequential differentiated generation (P03) and varied review-focus panels (P13) provide prespecified secondary tests designed to encourage diversity.
- Preserve whole-proposal analyses and add scientific-component analyses. Retain extracted components before any style rewrite.
- Apply the same new measurement pipeline to NCEMS and NOVO, while preserving the original NCEMS outputs as a legacy branch.
- Core–edge analysis must include an equal-size human-reference omission baseline.

### Evidence sources and status vocabulary

| Source | Use in this plan |
|---|---|
| `data/NOVO-data/included-research_projects_investigator/` | Current selected call JSON files and inventory, inspected November 18 |
| `data/NOVO-data/original/reviews_extended.csv` | Source assessment types, statuses, reviewer IDs, and versions |
| `src/rebuild_novo_reviews.py` | Existing lossless grouping of assessments and recommendations |
| `src/select_novo_calls.py` | Existing selection rules and their limitations |
| `docs/plans/analysis_plan_v2.md` | NCEMS workflow, outcomes and unresolved statistical issues |
| `src/rephrase_pipeline.py`, `src/prepare_proposals_for_analysis.py`, `src/prepare_reviews_for_analysis.py` | Current text extraction, pooling and preparation behavior |
| `docs/writing/double compression/new_agency_experimental_protocol.md` | Earlier proposed contribution-level validation and calibrated coverage design |

“Observed” below means checked in current local records or code. “Proposed” means specified here but not implemented. “To freeze” identifies a decision requiring pilot evidence or verified archival metadata before confirmation. Proposed paths and module names are not claims that those files already exist.

## Research questions and hypotheses

### Questions, estimands and tests

Conditions are defined under Experiment Conditions. Each hypothesis is evaluated per exact model version; pooled-model results are secondary.

| ID | Research question and proposed hypothesis | Endpoint and comparison | Status |
|---|---|---|---|
| RQ1 / H1 | Does proposal compression replicate across calls? **H1:** Under independent call-only generation, AI has lower whole-proposal spread and effective richness than applicants. | Within-call log AI/applicant mean-pairwise-distance and Vendi q=1 ratios, summarized equally across calls; predicted aggregate effect <0. | Confirmatory core |
| RQ2 / H2 | Where in scientific content does compression occur? **H2:** Compression differs across questions, hypotheses, methods, datasets and contributions. No component ordering is assumed. | Within-call differences between component-specific log ratios; omnibus component interaction before pairwise contrasts. | Prespecified secondary; two-sided heterogeneity |
| RQ3 / H3 | Does AI disproportionately omit distinctive scientific ideas? **H3:** Excess AI omission over an equal-size human reference increases with independently defined call-local peripherality. | Per-call slope/contrast of AI-minus-human omission against peripherality; whole, component and linked-contribution endpoints. | Key secondary, dependent on matching validation |
| RQ4 / H4 | Do AI reviewers converge more than human reviewers? **H4:** Independent AI panels have lower within-proposal whole-review spread. | Matched R_ci panels; proposal-level differences or log ratios aggregated within call, then across calls. | Confirmatory core |
| RQ5 / H5 | Is review convergence concentrated in particular judgments? **H5:** Weakness appraisals show a larger AI/human spread reduction than strengths. Component-specific differences are tested without an assumed ordering. | Paired weakness-versus-strength effect contrast on a common eligible set; separate component-attention and appraisal-diversity endpoints. | Prespecified secondary |
| RQ6 / H6 | Does expertise conditioning change compression? **H6a:** Persona changes proposal/review semantic diversity; **H6b:** persona improves lexical diversity. Semantic improvement and residual deficit are separate tests. | Persona-minus-independent effects on the same calls, model versions and records; lexical controls and semantic endpoints. | Prespecified secondary; H6a two-sided, H6b directional |
| RQ7 | Do AI reviewers identify valid scientific strengths and weaknesses better or worse? | Expert-adjudicated precision, recall and unsupported-critique rates by component; matched human/AI comparison on the same validation proposals. | Exploratory comparative accuracy; no assumed winner |
| RQ8 | Do compressed judgments predict different funding outcomes or rankings? | Assessment-only within-call AUC, paired human/AI AUC differences, score spread, rank agreement and aggregation curves. | Exploratory; funding is an institutional outcome, not independent scientific truth |
| RQ9 | How robust is measured compression to text representation, and how does it vary by call? | Original-versus-verified-neutral representation sensitivity; heterogeneity by instrument, field, year, call size, evidence requirements and family. | Exploratory measurement robustness and generalization; no generation-stage mechanism claim |
| RQ10 / H10 | Does sequential differentiation reduce proposal compression? **H10:** G-sequential-different increases within-call spread/richness relative to G-independent. | Paired call effects at N_c, same model/settings/format; separate residual gap to applicants and quality checks. | Prespecified secondary; two-sided tests with directional prediction |
| RQ11 / H11 | Do varied evaluation priorities reduce review compression? **H11:** R-focus-diverse increases substantive appraisal diversity relative to R-independent. | Matched R_ci, component/stance spread, validated issue coverage, unsupported-critique rate. | Prespecified secondary; increased diversity alone is not improved reviewing |
| RQ12 | How many coded scientific ideas recur or remain exclusive to each sampled source, and how does their number scale with generation volume? | Adjudicated idea incidence and frequency spectra; accumulation and Vendi curves; finite-budget crossing of human targets and calibrated coverage. | Secondary descriptive/scaling; thresholds and coding validated before confirmation |
| RQ13 | How good are AI proposals, and are distinctive human proposals highly rated? | Blinded contemporary expert ratings of matched applicant/AI subsets; within-call peripherality–quality associations and missed-edge analyses. | Exploratory quality and association; no assumed superiority or causal effect |

H1 and H4 test the core replication; H2/H3/H5 explain its location. RQ7 is needed before describing reviewers as better or worse at scientific recognition. Lower semantic diversity alone does not establish inferior judgment.

### Multiplicity and interpretation

Proposed confirmatory family: three fixed model versions × three endpoints (whole-proposal spread, whole-proposal Vendi q=1, whole-review spread) under the independent condition, for **nine tests**, controlled by Holm at family-wise alpha 0.05. Use two-sided inference with directional hypotheses: a significant effect in the opposite direction contradicts the prediction. Report unadjusted and adjusted p-values and effect intervals.

The primary representation is the verified component-based whole scientific narrative with no fixed compression budget, described below. Original-text and legacy-style branches are sensitivity analyses, not additional primary opportunities. H1 and H4 may use different eligibility populations; both must be displayed.

For secondary endpoints, define families before confirmation: component contrasts; calibrated omission; persona contrasts; review-field contrasts. Add named secondary families for sequential-generation contrasts and review-focus contrasts across their declared endpoints and all three models; keep residual AI/applicant gaps distinct from intervention improvements. Apply BH FDR within each named family across the models, conditions and components actually tested. Do not create a separate family for every call. Report all planned endpoints, not only significant ones. Exploratory outcomes remain labeled exploratory.

Do not infer a difference from “significant here, nonsignificant there.” Test the paired difference between component/condition effects. A nonsignificant persona improvement does not prove no improvement; claims that recovery is negligible require a prespecified equivalence margin and sufficient precision. Negative findings, invalid assumptions and failed extraction validation remain reportable.

## Data Used (Actual)

### Current selected archive

The previously discussed `included-round1` directory is no longer present. The current selected directory is `data/NOVO-data/included-research_projects_investigator/`. This plan treats it as the current working cohort; selection provenance must be frozen before analysis.

| Item | November 18 observation |
|---|---|
| Selected calls | 57 |
| Applicant proposals | 2,112; call sizes 10–194, median 26 |
| Proposal text and brief | Both nonblank for all 2,112 records |
| Median main-text length | Approximately 19,980 characters |
| Assessment reviewer groups | 6,721 proposal × reviewer groups |
| Assessment records/versions | 6,753; 32 groups have multiple versions, affecting four proposals |
| Reviewers per proposal | 2–8 groups, median 3; 45 proposals have >5 |
| Distinct assessor IDs | 132 across the selected archive |
| Recommendation records | 2,072 in the separate recommendation collections |
| Funding outcomes | 337 `True`, 1,775 `False`; verify analytic mapping from source status |
| Observed assessment scores | Values 1–6; numeric meaning/direction must be verified by call rubric |
| Grant years | 2019–2024, with three calls missing the recorded grant year |
| Missing applicant research summaries | 678 |
| Applicant CV and literature reference fields | Empty in all 2,112 records |
| Missing call fields | Purpose 3 calls; scope 4; eligibility 7; call description 52 |

These supersede the previous discussion's 2,169-proposal/9,832-flat-review snapshot. Existing audit JSON files can describe earlier preprocessing states; regenerate a manifest of the current snapshot instead of assuming their old totals remain current.

The selected folder contains mixed instrument labels despite its name: research projects, investigator grants, postdoctoral fellowships, and smaller numbers of innovation, education and conference records; 257 proposal records have a missing instrument type. Define scientific-task eligibility from the call and proposal content, not solely the directory name.

### Existing review format

The current schema already separates activities and preserves versions:

```json
{
  "reviews": [
    {
      "reviewer_id": "stable-source-id",
      "reviewer_full_name": "source name",
      "assessments": [
        {
          "review_id": "stable-assessment-id",
          "activity_type": "Assessment",
          "activity_status": "source-status",
          "assessment_score": "source-string",
          "assessor_comment": "source-text"
        }
      ]
    }
  ],
  "recommendation": [
    {
      "reviewer_id": "stable-source-id",
      "recommendations": []
    }
  ]
}
```

Nested assessment records retain additional source metadata. A group is a reviewer, not another independent reviewer for each version. `mean_score` and `within_call_pct` were preserved by rebuilding; they are not certified assessment-only aggregates.

### Eligibility and version policy

1. Build separate `generation_eligible`, `review_text_eligible`, `score_eligible`, `persona_eligible`, `coverage_calibration_eligible` and `recognition_validation_eligible` flags with reasons. A proposal excluded from one endpoint is not automatically excluded everywhere.
2. Identify the intended assessment stage. Do not infer chronology from CSV order, IDs, `Historic` versus `Complete`, or the old folder name. With one admissible assessment per assessor, use it; where versions differ and chronology is unavailable, obtain provenance or exclude that unresolved assessor from the primary panel. Retain all versions for explicitly labeled sensitivity analyses. Never average versions and call them independent reviews.
3. Recompute R_ci after version/stage and substantive-assessment eligibility. At least two eligible assessors are required for within-panel diversity; single-score records can still contribute to carefully labeled score analyses.
4. Exclude administrative decisions from scientific-review embeddings. Do not impose a text-length-only rule: a short specific criticism may be substantive. Annotate content suitability using an origin-independent rule fixed before AI comparisons.
5. Audit stage, conflicts of interest, missing context, attachments, and proposal version actually reviewed. Missing CVs and private preliminary evidence limit historical review comparability. Restrict primary review claims to information actually provided to both sides, or label information asymmetry explicitly.
6. Calls need sufficient verified scientific instructions, format and rubric for their intended experiment. Missing structured fields may be recovered from checked historical call material; missing rubric weights must not be invented. `guideline_length_chars` is not assumed to be a proposal word limit.
7. Do not invent missing hypotheses or treat legitimate descriptive projects as extraction failures. Instrument-specific applicability is distinct from absent information.

The current `select_novo_calls.py` excludes calls with identical comments across distinct assessors. That conditions human-panel selection on agreement, a quantity related to the outcome. Preserve its inventory as historical selection, but define confirmation eligibility without excluding genuine identical judgments. Either rebuild a broader eligible population from the parent archive under a content/provenance rule, or explicitly restrict inference to this selected cohort and report selection sensitivity. Changing the cohort requires a new manifest, not silent directory replacement.

Before splitting related annual calls, identify repeated applicants and near-duplicate/resubmitted proposal text across calls. Preserve these records in the archive, prevent resubmission leakage between development and confirmation where feasible, and add applicant/proposal-lineage sensitivity analyses; do not deduplicate genuine within-call scientific similarity out of the outcome.

Call the observational texts **applicant-submitted**, not proven unaided human writing, especially in later years. Current-model generation is retrospective: pre-deadline retrieval restrictions do not recreate historical model knowledge.

## Prepared Data Inventory

### Proposed normalized tables

All identifiers are namespaced by dataset; the call-year is metadata, not the sole identity key. Preserve source IDs and hashes without exposing outcome-linked IDs to generators.

| Artifact | Key columns and role |
|---|---|
| `call_manifest.parquet` | dataset, call_id, call_family_id, year, instrument, scope, deadline, verified format/rubric, score direction, eligibility, source hash, split |
| `proposal_manifest.parquet` | proposal_uid, call_id, source ID/version, language, scientific text references, source section IDs, eligibility and missingness |
| `assessment_versions.parquet` | proposal_uid, reviewer_uid, review_uid, type, status, version evidence, raw comment/score, source hash; every version retained |
| `assessment_selection.parquet` | One selected assessment or explicit unresolved reason per proposal × assessor for each declared stage policy |
| `review_panel_manifest.parquet` | proposal_uid, stage_policy_id, eligible reviewer IDs, R_ci_text, R_ci_score, matching choices |
| `outcomes.parquet` | Funding, amounts and institutional ranking; analysis-only inputs, unavailable to generation/extraction |
| `persona_cards.jsonl` | Sanitized model-visible expertise with dated publication evidence |
| `persona_assignments.parquet` | Administrative applicant/reviewer linkage, call IDs and schedules; never serialized wholesale into prompts |
| `generation_schedule.parquet` | call_id, exact model/version, condition, replicate/chain_id, slot_id/order, persona_id/focus_id, seed if supported, stage, expected counts |
| `generation_records.jsonl` | Raw responses, parsed complete proposals/reviews, prompt/input/history hashes, parent proposal IDs, request IDs, usage, timing, retries and status |
| `proposal_components.jsonl` | Multiple aims, component items, explicit missingness, source evidence and links |
| `component_verification.jsonl` | Unsupported items, missing aims, scientific alterations and resolution history |
| `review_claims.jsonl` | Source-grounded appraisals with component targets, stance and independent mapping validation |
| `embeddings/` and `embedding_manifest.json` | Whole/component/chunk vectors with encoder revision, pooling, chunking, token coverage and content hashes |
| `call_effects.parquet` | One declared call/model/condition/metric/component effect, uncertainty, sample sizes and validity flags |
| `proposal_panel_effects.parquet` | Review effects per target proposal; preserves call and reviewer clustering |
| `coverage_targets.parquet` | Held-out target, calibration split, peripherality, human/AI omission and matched reference size |
| `recognition_validation.parquet` | Expert reference issues, admissible opportunities, detected/missed/unsupported claims and adjudication |

Additional proposed artifacts, following the same NOVO roots:

| Artifact | Purpose |
|---|---|
| `idea_codebook.json`, `proposal_idea_incidence.parquet` | Expert-validated definitions, source passages, ambiguity and binary proposal/type membership |
| `idea_frequency_spectra.parquet` | D_g, F_g(k), source-exclusive/shared counts and matched-size denominators |
| `vendi_trace/` | Selected texts, representation metadata, vectors, kernels, eigenvalues and arithmetic |
| `generation_volume_curves.parquet` | m, chain/prefix or subsample ID, counts, Vendi, coverage, crossing and budget flags |
| `review_focus_assignments.parquet` | Target/panel, eligible lens catalog, assigned focus, seed/order and rubric version |
| `proposal_quality_ratings.parquet` | Blinded proposal ID, rater, dimension scores, uncertainty, evidence and sample weight |

Prepared codebooks/assignments/ratings go under `data/NOVO-data/prepared/{analysis_version}/`; derived counts, curves and Vendi traces go under `results-NOVO/{analysis_version}/tables/` or `audits/` as appropriate. Raw generation histories remain with their run records.

### Storage and reproducibility

Proposed paths:

```text
configs/novo/analysis_v1.yaml
prompts/novo/v1/
src/NOVO/
notebooks-NOVO/
data/NOVO-data/prepared/{analysis_version}/
data/NOVO-data/generated/{run_id}/{call_id}/{condition}/{model_key}/
results-NOVO/{analysis_version}/tables/
results-NOVO/{analysis_version}/figures/
```

Resolve every configured path from `PROJECT_ROOT`, the repository root containing `notebooks-NOVO/`, `src/NOVO/`, and `results-NOVO/`, regardless of the notebook working directory. Centralize these roots in `configs/novo/analysis_v1.yaml`; validate them before any read/write. The three NOVO directories already exist, while the configuration and implementation files listed here remain proposed.

Use `src/NOVO/` as a package with an `__init__.py`; after adding `PROJECT_ROOT / "src"` to the import path, use explicit `NOVO.*` imports for NOVO modules. Avoid unqualified imports such as `from proposal_generation import ...`, which could load the existing NCEMS module. Place the NOVO prompt loader at `src/NOVO/prompt_templates.py` and load versioned prompt text from `PROJECT_ROOT / "prompts/novo/v1"`.

Prepared records, component/embedding caches and generated text remain under `data/NOVO-data/` as specified above. Save all NOVO analysis tables, figures, audit reports and analysis logs under `results-NOVO/{analysis_version}/` (with `tables/`, `figures/`, `audits/`, and `logs/` subdirectories). Generation request logs remain with their generated records. Production builders must receive this output root explicitly. Check path resolution from both the repository root and `notebooks-NOVO/`, and reject writes to NCEMS result directories.

Keep raw selected/source files unchanged. No writes to existing NCEMS result directories. Pin source manifests rather than selecting the latest filename implicitly. A cache key must include input hashes, schema/prompt versions, encoder revision, pooling, chunking, text branch, call and component. Changing pooling or prompts must invalidate the appropriate cache.

### Scientific-component contract

The five primary content components are `research_question`, `hypothesis`, `methods`, `datasets`, and `contribution`. Additional context types are `system_scope`, `validation`, `preliminary_evidence`, `feasibility`, and `resources`. `whole` remains an analysis level; `linked_contribution` is a relationship endpoint, not simply another bag of words.

```json
{
  "schema_version": "novo_components_v1",
  "proposal_uid": "novo:call-id:proposal-id",
  "source_hash": "sha256",
  "aims": [{"aim_id": "a1", "source_section_ids": ["s1"]}],
  "components": {
    "research_question": {
      "status": "present",
      "items": [{
        "item_id": "q1",
        "aim_ids": ["a1"],
        "scientific_text": "Source-faithful statement of the question.",
        "knowledge_status": "proposed_work",
        "evidence": [{"section_id": "s1", "quote": "Exact source passage"}]
      }]
    },
    "hypothesis": {"status": "not_stated", "items": []},
    "methods": {"status": "not_stated", "items": []},
    "datasets": {"status": "not_stated", "items": []},
    "contribution": {"status": "not_stated", "items": []},
    "system_scope": {"status": "not_stated", "items": []},
    "validation": {"status": "not_stated", "items": []},
    "preliminary_evidence": {"status": "not_stated", "items": []},
    "feasibility": {"status": "not_stated", "items": []},
    "resources": {"status": "not_stated", "items": []}
  },
  "links": [],
  "unresolved": []
}
```

The example is a schema illustration, not extracted data. Status vocabulary: `present`, `not_stated`, `explicitly_absent`, `not_applicable`, `unresolved`. `not_applicable` needs an explicit source or a predeclared instrument-level rule; it is not a synonym for missing. Mixed cases retain items and unresolved flags. Item knowledge statuses distinguish background, preliminary result, proposed work, prediction and intended contribution. Links have `source_item_id`, `relation`, `target_item_id`, `aim_id`, and evidence; permitted relations include `tests`, `addresses`, `uses_data`, `validates`, and `supports_intended_contribution`.

Use immutable normalized source sections. Deterministically locate exact evidence quotes and add zero-based Unicode code-point start/end offsets, end exclusive, to the stored record. Do not trust model-generated offsets without checking them. Preserve the normalization-to-raw-source mapping. Null/missing items are never embedded as the phrase “Not specified.”

## Experiment Conditions

### Selected proposal and review generation models

The following model IDs are fixed for both NOVO proposal generation and NOVO review generation:

```python
GENERATION_MODELS = ["gpt-6.2-astra", "gemini-4-carbon", "claude-fable-5-2"]
```

Use this same list in the proposed NOVO `00a_gen_proposals.ipynb` and `00b_gen_reviews.ipynb`, supplied by the shared study configuration. Each model generates its own N_c-proposal set and matched R_ci-review panels under every enabled condition. Generate each complete proposal directly in a single request; no expansion request is scheduled. Keep model-specific results separate; do not pool the three generated sets into a single comparison with applicants.

Freeze supported decoding/reasoning settings during development and record the requested model ID, returned model identifier when available, settings, and generation date for every attempt. Validate access and request compatibility before confirmation; a failed or unavailable model must not silently fall back to another version. Extraction, rephrasing, verification, and embedding model choices remain separate measurement decisions; this selection applies to proposal and review generation.

### Core conditions and diversity interventions

| Task / condition | Input and execution | Interpretation |
|---|---|---|
| G-independent | Verified call packet; fresh request returning one complete proposal | Primary call-only generation at native call size |
| G-persona | Same procedure plus sanitized prior expertise; one profile per applicant slot, reused across models | Expertise-conditioned generation; prompt conditioning, not fine-tuning |
| G-sequential-different | N_c single-proposal requests; each request after the first receives all previous complete proposals from its chain and explicitly seeks a different scientific contribution | Secondary diversity intervention relative to G-independent; proposals within a chain are dependent |
| R-independent | Same eligible applicant proposal and rubric; R_ci fresh review requests per model | Primary review comparison |
| R-persona | Same proposal and rubric plus matched reviewer expertise | Scientific-perspective intervention; historical-reviewer reconstruction only if evidence supports it |
| R-focus-diverse | R_ci independent requests with deliberately varied, call-applicable scientific evaluation priorities | Secondary diversity intervention; synthetic evaluation roles, distinct from biographical expertise personas |

Use exact fixed versions for all conditions within a model family; do not repeat the NCEMS baseline-version confound. Generation condition and review condition are separate axes: the main AI-review experiment targets applicant proposals, not proposals generated under a corresponding G condition. There is no required G×R factorial of AI-proposal reviews. The separate RQ13 quality-validation subset includes both applicant and AI proposals, primarily rated by blinded human experts; supplementary AI quality ratings must be labeled separately.

The core design uses one full-proposal generation request per slot, with no external drafting, expansion, critique, revision, candidate ranking or novelty-based selection. “One pass” describes the API workflow; it makes no claim about the provider’s internal reasoning. Technical retries follow the declared failure policy and are logged. No two-stage comparison or funding-oriented prompt bridge is scheduled. P03 adds previous complete outputs as context for the next complete proposal, without revising any previous proposal. Literature retrieval/revision agents remain outside the current study. A future NCEMS rerun can use the same one-pass protocol and selected models with the NCEMS call packet; preserve and label its historical results separately. Current NOVO inference concerns this declared generation protocol, not all possible uses of an LLM.

### Why three review conditions

| Review condition | Manipulation | Question answered |
|---|---|---|
| R-independent / P08 | No expertise profile or assigned evaluation focus | How diverse and accurate are ordinary independent AI appraisals? |
| R-persona / P09 | Distinct, evidence-grounded scientific expertise profiles; each reviewer assesses the whole proposal | Does background expertise change appraisal diversity and recognition? |
| R-focus-diverse / P13 | Distinct call-applicable evaluation priorities, such as novelty, feasibility or measurement validity | Does deliberately distributing attention reduce review compression while preserving valid judgments? |

These parallel proposal generation at the level of baseline, expertise conditioning and deliberate diversification. The third mechanism differs by task: proposal P03 uses cumulative-history differentiation, while review P13 assigns priorities without showing other reviews. Do not describe the third arms as the same intervention or treat the design as a matched mechanism factorial. There is no sequential “disagree with previous reviews” condition.

All three review conditions target the same eligible applicant proposal and supply exactly R_ci separate reviews per model. Hold the rubric, admissible dossier, length policy and supported decoding settings fixed. Keep profile/focus assignments fixed across models; profile availability may restrict R-persona, so condition contrasts use common eligible targets and report missingness. R-persona receives no assigned focus; R-focus-diverse receives no biographical persona. This keeps the interventions interpretable. Preserve H6's review-persona contrast and H11's focus-diversity contrast against R-independent; any persona-versus-focus comparison is separately labeled secondary. Evaluate substantive appraisal diversity and recognition quality in every condition.

### Sample counts and independence

For call c, freeze N_c from scientific-text eligibility before AI generation. Record membership and exclusion counts against the original call inventory: a selected subset is not necessarily the complete historical applicant population. Under each G condition and exact model, schedule N_c final proposal slots. Under each R condition, schedule R_ci reviews for each review-eligible applicant proposal i. A generation replicate is a fresh complete N_c-proposal set or a fresh complete collection of matched review panels; seed/subsample draws are not replicate calls.

For three models and K_G generation conditions, final proposal slots = `3 × K_G × sum_c N_c` per generation replicate. For K_R review conditions, review slots = `3 × K_R × sum_c sum_i R_ci` per review replicate. The design now specifies K_G = K_R = 3. If every current raw record qualified for every condition, that would imply 19,008 proposal slots and 60,489 review slots per replicate, using 2,112 proposals and 6,721 assessor groups. Actual counts must be computed from condition-specific eligibility, including persona availability and sequential context feasibility; these are workload illustrations, not executed counts or a power calculation. Every final proposal slot corresponds to one planned full-proposal generation request. Extraction, verification and technical retries add requests; no idea-generation or expansion requests are budgeted.

Start development on a small, prespecified set of call families. Measure cost and between-run variability there before fixing the number of confirmation replicates. Every replicate preserves the native N_c and R_ci matching. If resources require fewer calls, choose them by predeclared strata, not observed compression, and preserve within-call matching.

P03 requires enough input context for the complete cumulative proposal history plus the call/prompt and reserved output. Preflight all N_c steps. Do not silently truncate history, replace it with titles, summarize it, or reset the chain. If full-history generation is infeasible, exclude that call/model cell from this secondary contrast, report the feasibility selection, and retain its independent/persona results. A summarized-history variant would require its own protocol. No review-batch or all-component-checklist generation condition is scheduled.

Keep scientific duplicates and scientifically weak proposals, including failed differentiation in P03. Fixed technical retries repair transport or parsing failures, not low novelty or unfavorable scores. Retain failed slots and all attempts. If N_c usable texts are not obtained, flag the cell incomplete; report failure/yield and a declared matched-available sensitivity analysis rather than presenting it as the complete primary cell. Meaningful but invalid scientific outputs remain in the record and in validity/yield analyses.

### Persona requirements

For a call-level G-persona comparison, require N_c admissible profiles built from pre-deadline, author-disambiguated sources. Give the same profile multiset to each model. Do not claim a fully applicant-matched persona condition if profiles exist for only a subset. For incomplete calls, keep G-independent eligible and exclude the call from the primary matched-persona contrast, or preregister a separately named partial-profile experiment.

Store model-visible profile JSON separately from assignments. Fields: `persona_id`, `knowledge_cutoff`, domains, systems, methods, data experience, and publications with stable source ID, date, title, abstract and supported expertise. Publication titles are allowed; submitted proposal titles are not. Do not infer private resources, personalities, reviewer decisions or unpublished findings. No fixed requirement of five papers is imposed here; the evidence-selection and maximum-budget rule is frozen during development.

For R-persona, use distinct reviewer-expertise profiles where available and preserve reviewer reuse across proposals through a stable assignment table. Same profiles across models, no target-derived hints. If applicant-team profiles are used instead, label the condition synthetic scientific perspectives; it cannot answer whether AI reproduces the actual reviewers.

## Completed Analyses and Results

Only archive structure, counts, code behavior and existing preparation work are established. NOVO compression, component differences, core–edge omission and review recognition results are **not yet known**. No NCEMS effect size is copied into a NOVO results cell.

### Implemented foundations and remaining work

| Capability | Current status | Required change |
|---|---|---|
| Assessment/recommendation separation | Implemented in `rebuild_novo_reviews.py`; current JSON uses grouped schema | Select admissible versions and recompute scores; preserve separation |
| Call inventory/selection | Implemented in `select_novo_calls.py` | Parameterize current selected root; remove agreement-based eligibility for confirmation or quantify selection limitation |
| Existing NCEMS extracted facts | Stored for 23 applicant and 207 AI proposals in earlier inspected CSVs and summary JSON | Re-extract against current source hashes into the richer schema; do not treat old summaries as complete evidence |
| Proposal embedding | BioLinkBERT-large, CLS pooling in current notebook/caches; 512-token truncation | Chunk complete text; explicit representation/version contract |
| Review embedding | Mean pooling, also bounded by tokenization | Chunk complete eligible reviews and component claims |
| Facet functions | Existing NCEMS metric library | Reuse metric math after contract tests; replace fixed counts, paths and inference orchestration |
| Core–edge builder | Single-corpus geometry, fixed n23 cache | Call-local calibrated human-reference comparison |
| Score/outcome analysis | NCEMS scoring and sample assumptions | Call-native scoring, selected assessments, within-call outcomes and clustered summaries |

The earlier v2 description of proposal embeddings as mean-pooled is incorrect for the inspected notebook and caches. Record the legacy as CLS; harmonized mean-pooled chunk embeddings constitute a new measurement version, not a reinterpretation of the old stored results.

### Proposed measurements

For whole proposals and each primary component, compute applicable spread, richness, evenness, geometric coverage and displacement. Dimensionality remains diagnostic. Domain/literature coverage needs an appropriate reference and is secondary; do not reuse the fixed NCEMS 12-region map for every NOVO call or for every component.

Primary component-set unit: **one representation per proposal per component**, built from all verified items for that component. Multiple aims are retained for linked matching but do not multiply a proposal's statistical weight. Component-specific diversity is conditional on having substantive content; also report absence/applicability rates across the full matched cohort.

For component j, match size within each call/model/condition using `n_cj = min(number of applicant representations present, number of AI representations present)`, sampling without replacement as needed. Report both original presence counts and matched n_cj. This measurement subsetting does not change the N_c generation target. Do not silently impute absent hypotheses or treat universal absence as complete semantic compression. Compare component effects on a common-support set as a sensitivity analysis to presence-based selection.

Metric support gates: pairwise spread and Vendi need at least two substantive representations; a k=3 neighborhood needs at least four; geometric nulls and evenness require additional stability checks. Freeze metric-specific minimum support and stability rules in development. Insufficient cells are reported, not filled with zeros.

### Collaborator feedback: gaps addressed by the revised design

| Feedback | What the prior draft covered | Added requirement |
|---|---|---|
| Literal counts and repeats of ideas | Embedding richness and component matching, not an adjudicated idea census | Idea codebook, source-linked incidence, repetition spectra and source-exclusive counts |
| Explain Vendi concretely | Metric named without a worked trace | Toy calculation below plus an auditable real-proposal text-to-matrix example |
| How many generated proposals recover human breadth? | Equal-size comparisons only | Separate volume experiment with accumulation, effective-richness and target-coverage curves |
| Are AI proposals good? | AI reviewed applicant proposals; no comparable human/AI proposal quality panel | Blinded contemporary expert ratings of both origins on a matched validation subset |
| Are human edges highly scored? | Peripherality and omission, but no independent quality endpoint | Edge–quality association using new ratings, with archival scores as a separate analysis |
| Strongest plausible reviewer prompting | Expertise profiles and an all-component checklist | R-focus-diverse: deliberately varied scientific evaluation priorities at the same R_ci |

These are prospective additions, not completed results. Fig. 3's unmatched points are not a literal idea census: a projection cannot establish equivalence or uniqueness. The v2 reconciliation register already cautions against turning spread or a Vendi ratio into a literal percentage fewer ideas, and records no detected historical funding/ranking difference for missed proposals. The new analyses must not presuppose a positive quality result.

### Literal idea counts and repetition spectra

Define the coding unit before seeing source labels: a substantive linked contribution consisting of question/objective, relevant scope/system, approach/evidence, and intended contribution. The same topic alone does not imply the same idea. Freeze an expert-developed equivalence codebook on development calls. For whole-proposal redundancy, separately code equivalence of the central contribution; for multi-aim proposals, retain all distinct linked contributions and their links. Do not mix the two units in one count.

Build a joint, source-blinded codebook within each call over applicant and AI proposals. Experts validate proposed matches and unmatched/rare items using source passages; audit missed matches as well as false matches. Do not create idea types from single-link connected components whose endpoints may be scientifically different. Keep unresolved cases and report conservative/liberal coding sensitivity. No fixed embedding threshold or LLM label is a verified idea count by itself.

Store binary incidence A_ij: proposal i contains idea type j. Count a repeated idea once within a proposal. For source/model/condition g, let f_gj = sum_i A_ij, D_g = number of j with f_gj > 0, and F_g(k) = number of idea types with f_gj = k. Report D_g, F_g(1), F_g(2), F_g(3), ... and shared/exclusive types: applicant-only means f_Hj > 0 and f_Aj = 0 in this sampled comparison, not novel to science. Use the phrase “present in k proposals,” not k independent people, unless authorship independence is established. Multiple ideas per proposal allow D_g to exceed proposal count.

For NCEMS, report actual counts for each model's 23 proposals against the 23 applicants when those sets are complete. A 69-proposal union across three models is a separate, larger mixed-model portfolio; label it and also show matched-size 23-proposal subsamples under a frozen model-mixture rule. Never attribute a union advantage to a single model or compare 69 versus 23 as if sample sizes were equal. NOVO uses each call's N_c. Apply whole and component-level coding consistently, retaining human-adjudicated examples of agreement, difference and ambiguity.

### Worked richness example and auditable calculation

Vendi is a property of a set, not a quality or uniqueness score assigned to one proposal. With unit-normalized embedding rows X, the current helper `src/diversity_facets.py::vendi_scores` uses K = XX^T, normalizes by n, obtains eigenvalues lambda, and computes `VS_1 = exp(-sum(lambda * log(lambda)))`, taking 0 log 0 as zero. This is effective richness under a declared similarity representation, not a thresholded count. See [Friedman & Dieng (2023), The Vendi Score](https://arxiv.org/abs/2210.02410).

**Author-constructed illustration, not observed proposal embeddings:** proposals A and B express the same contribution; C and D express two other mutually distinct contributions. Give them idealized vectors A=B=(1,0,0), C=(0,1,0), D=(0,0,1). The similarity matrix and normalized eigenvalues are:

```text
K = [[1, 1, 0, 0],
     [1, 1, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 1]]
lambda(K/4) = [0.50, 0.25, 0.25, 0]
VS_1 = exp(-(0.50 ln 0.50 + 0.25 ln 0.25 + 0.25 ln 0.25))
     = 2.8284
```

There are four proposals, three literal coded idea types, and 2.83 effective types because one type is repeated. Four identical vectors yield 1; four mutually orthogonal vectors yield 4. Actual similarities are graded, not these idealized zeros and ones. Adding repetitive proposals can reduce effective richness by increasing imbalance; Vendi is not necessarily monotone with sample size.

Produce a real, source-linked audit example for a prespecified small set once extraction is validated: proposal passage → extracted contribution/component → verified neutral text → exact tokenizer/chunks and encoder revision → pooled normalized vector → pairwise similarities → full eigenvalue spectrum → entropy → Vendi. Save the matrices and settings with the figure/table, compare original and neutral text, and include a scientifically close pair and a contrasting pair. Check symmetry, unit diagonal, trace and positive semidefiniteness; permit only numerical-tolerance eigenvalue clipping. Report alternative-encoder/kernel sensitivity. The real example is required for manuscript delivery; the toy arithmetic does not validate embedding semantics.

### Generation-volume and human-target curves

Keep first-N_c equal-size results as the primary experiment. On a prespecified subset of development/confirmation call families, extend separate generation streams to a fixed budget beyond N_c. A starting grid for budgeting is N_c, 2N_c and 4N_c, frozen after cost/context preflight and before confirmation effects. This is a labeled secondary volume experiment, not a change to native-size matching or permission to stop upon a favorable crossing. Freeze included conditions and any persona-profile reuse policy before extending persona streams; default volume contrasts are P01 and P03 per model.

At each m report: (a) adjudicated observed idea count D_A(m); (b) Vendi at m; (c) coverage of held-out applicant idea targets under the established calibration scheme; (d) yield and cumulative tokens/cost. Show the applicant D_H(N_c) and Vendi_H(N_c) as separate targets, with human accumulation curves only up to N_c. Matching a number of types does not mean recovering the same human ideas or their quality.

Use repeated without-replacement subsamples/orderings for independent pools and actual chronological prefixes for sequential chains; shuffle-based rarefaction of a P03 final pool is descriptive only and cannot stand in for its deployment trajectory. Report independent-chain variability and call-family uncertainty without treating subsamples as extra calls. Freeze the idea codebook/version before plotting so that cluster merging does not create spurious gains/losses; audit this codebook as new outputs are assigned.

Define the observed crossing m* separately for literal count and Vendi. Report the first measured checkpoint meeting its human target, and whether later checkpoints remain above it; do not force Vendi to be monotone. If the target is not reached, report “not reached by B_c proposals,” not an extrapolated answer or proof of impossibility. Include target uncertainty and between-chain variability. Coverage gets its own prespecified target and may remain incomplete even after richness crosses. Keep mixed-model portfolios secondary and explicitly budgeted.

### Comparable proposal quality and the value of human edges

Select a stratified random validation subset across calls, applicant/AI origins, all three models and declared generation conditions. Within eligible calls use equal origin sample sizes; determine sample size and ratings per proposal by pilot precision/cost, then freeze before seeing quality scores. Oversample peripheral/missed proposals only through predeclared strata with recorded inclusion probabilities and weighting for population summaries. Do not select impressive AI examples. The subset can be small, but uncertainty must reflect its actual size.

Obtain contemporary domain-expert ratings on both applicant and AI proposals, blinded to origin/model/condition, funding and historical reviews. Randomize order, use an equal admissible dossier and standardized display, balance raters across origins, and record conflicts, confidence and optional guesses of origin. Blinding reduces cues but cannot guarantee raters cannot infer origin. Apply the same verified call rubric, with prespecified anchors for scientific validity, feasibility, significance, novelty relative to known literature, and overall merit where applicable; missing evidence is flagged, not invented. Use at least two independent ratings per selected proposal as a development minimum, then freeze the panel size; report disagreement and rater/call effects. Provide the rating form in P14. AI-only ratings are supplementary, not an independent validation of AI quality; any AI panel should cross generator/reviewer families and expose same-family effects.

Define peripherality and AI-miss labels before examining scores. Compare continuous peripherality with contemporary expert quality within call; also report calibrated AI-missed versus covered human proposals and prespecified edge/core summaries. Repeated partitions of the same proposal do not multiply observations. Adjust for call/rater and predeclared instrument/length factors, report selection weights, and retain the precision limits of the subset. Archival human scores/funding are a separate historical association because raters, evidence and institutional selection differ. Do not equate a null difference with equivalence or infer that distinctive means valuable.

Report a diversity–quality profile: total diversity, quality distribution, and count/coverage of distinct ideas in proposals meeting an independently prespecified quality standard, with denominators and uncertainty. Quality-filtered results are secondary and must not replace the unselected generation comparison. Do not construct an unvalidated combined “diversity × quality” score.

### Review attention, diversity and recognition

For every component, distinguish:

1. **Attention:** fraction of reviews/panels with an explicit appraisal of that component; absence is an outcome here.
2. **Appraisal diversity:** semantic spread/richness of substantive appraisals conditional on enough panel members addressing it; match contributing-review counts and disclose them.
3. **Stance:** strengths, weaknesses, neutral descriptions or mixed judgments; preserve severity and uncertainty without inventing numeric scales.
4. **Recognition:** detection of independently validated scientific strengths/weaknesses, false positives and omissions.

Generate reviews before component annotation. Apply the same downstream component extraction and recognition analysis to all three review conditions. No all-component checklist is added to R-independent or R-persona; component-level analysis does not require a component-guided generation condition.

A valid reference for RQ7 requires expert assessment of the proposal independent of the AI/human reviews where feasible, supplemented by blinded adjudication of proposed issues from both sources. This avoids treating historical human critiques as the complete truth. Define an opportunity set, issue equivalence, acceptable partial matches and adjudication rules before confirmation. Audit precision/recall by origin, component and rarity. Include short comments and apparent misses in validation, not only easy semantic matches.

### Core–edge calibration

Preserve full-size N_c comparisons for primary diversity. The calibrated omission analysis is a different endpoint and requires disjoint human sets within a call:

- C: human calibration proposals define peripherality.
- H: human reference proposals supply a finite-sample comparison pool.
- T: held-out target proposals, absent from C and H.
- A: AI subset of size |H|, drawn from the generated N_c pool.

Compare the same T against A and H. Define peripherality using distances to C, not to H and not to AI. Matching thresholds are learned/validated on development calls, independently of confirmation effects. A linked idea is covered only if a single candidate preserves its defining relationships; question in candidate A plus method in candidate B is component availability, not linked recovery.

For target i, `excess_omission_i = AI_miss_i − human_reference_miss_i`. Estimate its relationship with continuous peripherality within call, then aggregate call-level slopes. Rotate partitions under a frozen scheme; repeated partitions do not enlarge the independent sample.

Partition proportions, minimum stable calibration/reference sizes and equivalence thresholds are to be frozen after the pilot. Ten is not a required common size. Calls too small for a stable three-way split remain eligible for primary diversity and reviews but not this calibrated endpoint. Density-tertile graphics are descriptive; do not select a partition or threshold because it produces a strong edge effect.

### Inference and effect reporting

Use positive-metric log ratios `log(D_AI / D_applicant)` for proposal spread/richness. Within review target i, compute `log(D_AI_ci / D_human_ci)` where defined; average equally over eligible proposals within a call. Aggregate call effects equally across eligible calls. Zero/undefined values receive explicit flags and predeclared difference-based sensitivity analyses, not arbitrary epsilons.

Evenness uses signed excess relative to a declared reference; coverage is a proportion or human-calibrated difference; displacement has its own units. Do not relabel all metrics as ratios. Report effect size, uncertainty, N_c/R_ci, component availability, model/condition and inference method for every result.

Proposed primary uncertainty: bootstrap call-family clusters over the already computed call effects, retaining all calls in a sampled family and the equal-call estimand. Average repeated AI replicates within call before the main summary, and estimate between-run variability separately. Resampling effect records across clusters is permissible; resampling documents with replacement inside a Vendi/coverage calculation would inject duplicates and is not the same procedure. For a scalar endpoint, implement a two-sided null-centered cluster-bootstrap test of the equal-call mean effect against zero and percentile bootstrap confidence intervals; document the centering and Monte Carlo convention in the inference helper. Joint component tests require the corresponding multivariate contrast and family-resampled null distribution, not a count of significant component tests. Cluster-bootstrap settings, including 10,000 draws as a starting configuration, are frozen before confirmation; few-family uncertainty must be acknowledged.

Repeated reviewers can cross calls/families. Add a reviewer-aware sensitivity model for review-level outcomes with crossed reviewer effects or another validated dependence treatment. Report family and reviewer counts; do not claim the nominal number of calls is the effective independent sample size.

Per-call permutation diagnostics must respect source-generation batches and matched proposals; they are not a replacement for across-call replication inference. Do not reuse the old pooled-subsample tail proportion and call it a label-permutation p-value. If preserving the old paired sign-balance measure, name it accurately; do not call it standard Cliff's delta or rank-biserial correlation.

For persona comparisons, pair effects within the same call/model/representation on the intersection of eligible calls. For whole/component comparisons, report direct contrasts and support-set sensitivity. Secondary proposal-weighted summaries answer a different population question and are labeled accordingly.

### Funding and score analyses

Recompute numeric scores from the selected assessment versions. Keep the raw scale, verified favorable direction, criterion definitions and any genuine published weights. Do not infer score direction by maximizing observed AUC, normalize scores across calls as if rubrics were identical, or reuse stored `mean_score` without reconciliation.

Compute AUC and ranking agreement within calls on the same scored proposals and matched scored panel sizes. Both funding classes are required for a call-specific AUC; report inadequate-class cells. Summarize within-call discrimination and paired human/AI differences, with call-family uncertainty. Rank aggregation uses the same proposal support at different panel sizes where feasible; changing support is disclosed. Recommendations, official ranking and funding never enter predictor generation or component extraction.

The human scores contributed to funding, so human-outcome agreement has institutional dependence. Funding outcomes reflect budgets and fit as well as scientific merit. Better AUC is not proof of better independent scientific recognition. Large overall N does not remove these limitations.

## Data Visualization Guide

Use stable source/model colors and explicit condition/representation labels. Main displays should show call-level effects rather than only one pooled effect. Every plot identifies whether a point is a call, proposal, reviewer, AI replicate or subsample.

Proposed figures:

1. **Design and eligibility:** archive → scientific calls → generation/review/persona/coverage populations; show N_c and R_ci distributions and exclusions.
2. **Across-call replication:** model-specific call-effect distributions and aggregate intervals for whole-proposal spread/richness and within-proposal review spread.
3. **Where compression occurs:** component × facet effect matrix with call support and uncertainty; direct contrasts alongside absolute absence rates.
4. **Distinctive scientific content:** calibrated excess omission versus peripherality; component and linked-idea recovery, with adjudicated examples.
5. **Review behavior:** component attention, strengths/weakness diversity and independently validated recognition side by side.
6. **Conditions and robustness:** persona, sequential-generation and review-focus contrasts, raw/normalized representations and call-family heterogeneity.
7. **Concrete ideas and scaling:** adjudicated frequency spectra, human/AI-exclusive examples, Vendi trace and count/coverage-versus-budget curves.
8. **Quality and edges:** blinded quality distributions and peripherality–quality relationships with uncertainty.

Supplementary score/funding panels report call-level sample sizes and class balance. UMAP remains descriptive; it does not supply the distances for inference. Do not compare raw distance magnitudes across components with different length/content distributions. Keep NCEMS legacy figures separate from harmonized NCEMS/NOVO figures.

## Notebooks and analyses

### Proposed end-to-end layout

Keep the current NCEMS notebooks intact. Place NOVO notebooks in the existing `notebooks-NOVO/` directory and NOVO-specific modules in the existing `src/NOVO/` directory. Reuse suitable shared pure functions through explicit imports; put NOVO orchestration, adapters and output routing in `src/NOVO/` rather than copying large analysis cells or changing NCEMS defaults. All entries in the layout below are relative to `notebooks-NOVO/`.

```text
00_ingest_validate.ipynb
    → call/proposal manifests, assessment selection, splits, persona evidence
00a_gen_proposals.ipynb → complete proposals in one pass
00b_gen_reviews.ipynb   → ordinary and focus-diverse matched review panels
00c_extract_rephrase.ipynb
    → source-linked proposal components + verification + optional neutral prose
    → review claims + component mapping + optional neutral prose
01a_prepare_proposals.ipynb → whole/component chunk embeddings and call caches
01b_prepare_reviews.ipynb   → matched review/component panels and score tables
02_facets_proposals.ipynb  → within-call whole/component effects
03_facets_reviews.ipynb    → within-target effects, attention, claims and scores
04_synthesis.ipynb         → across-call inference, calibrated omission, validation
04a_idea_counts_scaling.ipynb → coded counts, repetition, Vendi trace, volume curves
04b_proposal_quality.ipynb  → blinded quality ratings, peripherality and missed edges
05_build_production_figures.ipynb → manuscript/SI figures
```

### Concrete code changes

The first column identifies existing code to inspect/reuse, or a proposed new module. The second column gives the NOVO implementation destination; it does not claim these files already exist. Existing `src/*.py` evidence references elsewhere in this plan retain their actual locations. NOVO adapters may call shared pure functions, but their default inputs, generation configuration and outputs must follow the NOVO path contract above.

| Existing module / behavior | NOVO implementation path | Proposed implementation change | Acceptance condition |
|---|---|---|---|
| `rebuild_novo_reviews.py` | `src/NOVO/rebuild_novo_reviews.py` | Reuse lossless grouped schema; do not rerun destructive flattening | Every source version preserved, activities separated, IDs unique |
| `select_novo_calls.py` | `src/NOVO/select_novo_calls.py` | Accept configurable roots including current folder; add stage/text/task eligibility; separate historical duplicate-comment flag from confirmation eligibility | Inventory totals reconcile; identical genuine assessments do not automatically exclude calls |
| New `novo_ingest.py`, `novo_contracts.py` | `src/NOVO/novo_ingest.py`, `src/NOVO/novo_contracts.py` | Normalize call/proposal/reviewer/assessment tables, hashes, flags and metadata | Every derived row links to immutable source |
| `ai_models_interface.py` and proposed NOVO generation notebook configuration | `src/NOVO/ai_models_interface.py` | Register the three selected generation IDs exactly; load the same model list for proposals and reviews; preserve historical NCEMS configuration separately | Requests use `gpt-6.2-astra`, `gemini-4-carbon`, or `claude-fable-5-2` as selected; no alias substitution or fallback to another model; requested/returned identity and settings logged |
| `proposal_generation.py` | `src/NOVO/proposal_generation.py` | Replace NCEMS idea/expansion passes with one complete-proposal request per slot; use call records and N_c, call-native sections, and condition/model/replicate/slot IDs | Exact N_c scheduled slots per eligible model/condition/call; no idea/expansion stages or cross-call context |
| `build_persona_cards.py` and persona loaders | `src/NOVO/build_persona_cards.py` | Separate prompt payload from target linkage; preserve publication dates/evidence; enforce deadline filter | No submitted title/text or outcomes in prompt hash input; same profiles across models |
| `review_generation.py` | `src/NOVO/review_generation.py` | Replace five-review registry/schedule with R_ci; read each call's rubric; keep applicant target IDs; eliminate prefix-only character truncation | Exactly R_ci review slots per model/condition/target; complete admissible input tracked |
| `rephrase_pipeline.py` | `src/NOVO/rephrase_pipeline.py` | Replace 15 numbered facts as analytic endpoint with verified component JSON; retain old facts and optional legacy prose | All five components, evidence and links persisted; no silent absent-field deletion in records |
| `rephrase_reviews.py` | `src/NOVO/rephrase_reviews.py` | Separate appraisal extraction from neutral rewriting; annotate existing judgments only | No invented strengths/weaknesses; empty appraisal remains empty |
| `prepare_proposals_for_analysis.py` | `src/NOVO/prepare_proposals_for_analysis.py` | Configurable dataset root and call keys; whole/component chunk pooling; explicit representation manifest | Every token-covered chunk traceable; no hidden 512-token-prefix representation |
| `prepare_reviews_for_analysis.py` | `src/NOVO/prepare_reviews_for_analysis.py` | Consume selected versions, distinct reviewer IDs and variable panels; whole/component/stance fields | Text and score panel counts independently verified |
| New `scientific_components.py`, `review_components.py` | `src/NOVO/scientific_components.py`, `src/NOVO/review_components.py` | Schema validation, source evidence checking, link mapping, content-preservation QA | Invalid quotes/IDs fail validation; missing content is not invented |
| New `component_embeddings.py` | `src/NOVO/component_embeddings.py` | Shared chunking/aggregation and versioned cache contract for both datasets | Model/pooling/prompt changes invalidate cache |
| `diversity_inference.py` | `src/NOVO/diversity_inference.py` | Reuse metric functions; parameterize call/component and n; replace NCEMS-specific effect aggregation | Matched n, correct effect direction and declared null per metric |
| `core_edge_analysis.py` | `src/NOVO/core_edge_analysis.py` | Refactor fixed n23/baseline references to call-local C/H/T/A partitions | Held-out targets excluded from references; AI and human references equal-sized |
| `claim_uniqueness.py` | `src/NOVO/claim_uniqueness.py` | Retain semantic screening; add source-linked component mapping and adjudicated issue matching | Claim similarity is not labeled scientific correctness |
| `decision_outcome.py` | `src/NOVO/decision_outcome.py` | Call-native score direction, selected-assessment scores and within-call AUC | No recommendations/outcomes leak into predictors |
| New `idea_census.py`, `generation_scaling.py` | `src/NOVO/idea_census.py`, `src/NOVO/generation_scaling.py` | Validated incidence counts, chain-aware curves and finite-budget crossing | No counts inferred from UMAP or rounded Vendi; no shuffled sequential deployment curves |
| New `review_focus.py`, `proposal_quality.py` | `src/NOVO/review_focus.py`, `src/NOVO/proposal_quality.py` | Matched focus-panel assignments and blinded rating exports/analysis | Exact R_ci, same lens assignment across models, source-blind ratings and weighting |
| New `novo_synthesis.py` | `src/NOVO/novo_synthesis.py` | Equal-call summaries, family resampling, paired condition/component tests and multiplicity | Replicates/subsamples do not inflate call count |
| Production builders | `src/NOVO/build_production_figures.py` | Dataset/version-specific output root; call-level figures and eligibility flow | Existing NCEMS outputs unchanged |

### Representation and chunking specification

Preserve three branches: `original_scientific`, `verified_neutral`, and `legacy_ncems_style` (bridge only). The proposed primary is `verified_neutral`: component-item text verified against source, assembled without forced sentence limits. Whole scientific text contains all retained scientific items and their relationships, excluding administrative biography unless the endpoint explicitly concerns resources/feasibility. Check it against original scientific sections for omitted principal content.

For the BioLinkBERT bridge, use tokenizer-aware chunks with a starting development setting of 448 content tokens and 64-token overlap, leaving room for model special tokens. These are pilot settings, frozen before confirmation. Assign each source token position to one chunk for pooling; overlap supplies context but its repeated positions are masked out of that chunk's pooling contribution. Mean-pool the assigned non-padding, non-special-token representations within each chunk, aggregate weighted by assigned-token count, then L2-normalize the document/component vector. Store every chunk, source-position assignment and coverage map. Do not count overlapping tokens repeatedly as extra evidence. Compare against the legacy CLS-prefix representation on NCEMS explicitly.

Use the same encoder/aggregation policy within an analysis stratum and across origins. Validate language and domain suitability. If a different scientific or multilingual encoder is needed, freeze its exact revision and rerun the common NCEMS bridge; do not compare one model's vectors with another's in a shared distance matrix. Compare a separately selected alternative encoder as sensitivity, not by choosing whichever maximizes the human–AI gap.

Chunk pooling can still lose question–method relationships; source-linked contribution matching supplements rather than duplicates it. No projection-based distances enter the facet tests. Full proposal review inputs also require complete context coverage: if a model cannot read an admissible dossier in context, use a separately defined, equally applied evidence-summary condition or exclude that cell. Never silently send only the opening characters.

## Prompt specifications

The following are proposed v1 templates, not prompts already used to produce NOVO results. Implement them as versioned files under `prompts/novo/v1/`. Braced uppercase names below are host-filled variables. Validate input/output schemas in code; do not rely on the prompt alone. Save the exact rendered prompt, model version, response and hashes for every attempt.

### Comparison with the existing proposal-generation prompts

The current NCEMS `notebooks/00a_gen_proposals.ipynb` uses `src/prompt_templates.py` and the registry in `src/proposal_generation.py`. Its idea-then-expansion implementation is historical context, not the NOVO design. NOVO P01 replaces both `generate_ideas_minimal_single` and `generate_proposals_minimal` with one complete-proposal request; P02 is the persona variant. P04 is retired, and no generation-stage comparison is planned.

| Dimension | Current NCEMS implementation | Current NOVO specification |
|---|---|---|
| Generation workflow | Idea abstract, then expansion | One complete proposal per request under independent/persona conditions |
| Objective | Funding-success wording | Scientifically meaningful contribution and call compliance; no instruction to maximize distance or novelty scores |
| Scientific content | Scientific detail requested mainly during expansion | Coherent question–approach–evidence relationships within the complete proposal |
| Format | 400–600-word idea abstract, followed by six sections totaling 2,400 words with abstract retained | Call-native headings and length rules; include an abstract only if the call format requires one |
| Evidence | No equivalent explicit fabrication restrictions in the independent templates | Distinguish planned work, established evidence, unavailable information and resource assumptions |
| Persona | Publication-grounded expertise used during both stages | Sanitized pre-deadline expertise used in the single request |
| Output and analysis | Intermediate ideas and expanded narratives | Complete proposal sections; whole/component extraction occurs afterward and is identical across origins |

The contemplated NCEMS rerun can adopt this same generation protocol, substituting its verified call and matching its eligible sample size. Keep historical and rerun results separately versioned; a change in model, prompt, source data or representation cannot be attributed to just one factor. No claim about where compression enters an idea-to-expansion sequence is made in this design.

### Research-informed prompt choices and attribution

The following decisions use a selected, checked subset of the supplied literature review, consulted November 19, 2026. They do not adopt every technique or numerical claim in that review. Prompt wording below is our adaptation, not a quotation or a validated optimum. Studies of products, word associations and creative writing motivate hypotheses; their effects are not assumed to transfer to full scientific proposals or peer review.

| Evidence and source | Decision for the current study | Scope and limitation |
|---|---|---|
| Heterogeneous personas and constraints improved product-idea diversity in [Terwiesch et al. (2026)](https://journals.sagepub.com/doi/10.1177/10591478261474243). | Retain G-persona and use distinct, evidence-grounded scientific profiles across applicant slots. P02 asks how supported expertise informs questions, methods and evidence. | Adapt heterogeneous starting contexts, not random demographic characters or constraints. Our matched publication profiles differ from their intervention. H6a remains two-sided. |
| Genius/demographic role prompts had bounded effects and engineered prompts had mixed/negative effects in [Wang, Huang, Shen & Uzzi (2026; online 2025)](https://doi.org/10.1038/s41562-025-02331-1); see also the [authors’ institutional account](https://english.amss.cas.cn/ae/rp/202605/t20260521_1159685.html). | No “genius,” prestige, eccentricity, or demographic stereotypes in persona instructions; do not assume elaborate prompts improve diversity. | Divergent-association evidence does not establish the effect of scientific-expertise profiles. Treat the latter as a testable intervention. |
| [ResearchAgent (Baek et al., 2025)](https://aclanthology.org/2025.naacl-long.342/) explicitly develops problems, methods and experiments within a retrieval/revision system. | Borrow only the organizing principle: P01 links the research question to methods and evidential tests in a single complete narrative. | This is a limited adaptation; the system’s results do not validate our isolated wording. Do not borrow its agents or iterative revisions. |
| Selected AI research ideas were judged more novel while generation diversity remained problematic in [Si, Yang & Hashimoto (2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ea94957d81b1c1caf87ef5319fa6b467-Abstract-Conference.html). | Separate set diversity, literature-relative novelty and scientific quality. Keep every scheduled scientific output; do not rank, deduplicate or shortlist to improve the primary result. | Our retention policy is a methodological inference from the distinction between generator output and selected output, not a reproduction of their selection pipeline. |
| Differentiated sequential search improved creative solutions in [Boussioux et al. (2024)](https://doi.org/10.1287/orsc.2023.18430). | Keep cross-output differentiation out of G-independent/G-persona. P03 now implements sequential differentiated generation with cumulative prior proposals. | Adapt their differentiated-search principle to full proposals, without claiming the same effect. Independent/persona requests still have no previous outputs. |
| [Verbalized Sampling (Zhang et al., 2026)](https://proceedings.mlr.press/v306/zhang26hy.html) elicits multiple candidate responses with probabilities. | Defer this technique; P01 returns exactly one complete proposal, with no candidate sampling/selection or probability field. | Probabilities are not scientific truth, novelty or success probabilities. Evidence from creative text does not establish gains for this study. |
| [SciMON (Wang et al., 2024)](https://aclanthology.org/2024.acl-long.18/) compares ideas with retrieved literature and iteratively revises them. | Keep a frozen, source-identified background policy; do not ask an ungrounded model to certify novelty. Defer retrieval/revision and facet-recombination workflows. | Evidence and source bookkeeping are study controls, not a claim to implement or obtain SciMON’s effects. No two-stage or revision condition is scheduled. |

**Condition-specific implementation.** P01 uses the same scientific coherence, evidence and format instructions across all three models. P02 adds only the supported expertise block, with the same profile assignments across models and a frozen profile-length policy; this estimates the expertise-context package, not an isolated “persona label” effect. Neither condition requests alternatives, hidden candidate lists, a diversity-maximizing score, or a self-critique stage. Independent sessions define the estimand; they are not chosen because they are known to maximize diversity. P03 instead generates one complete proposal per request while supplying all earlier proposals in its chain and requesting substantive differentiation. This is a prespecified secondary comparison against P01, with decoding settings held fixed.

**Review prompts.** Ideation studies do not establish that forcing disagreement improves peer review. P08/P09 ask for evidence-grounded scientific judgments under a common rubric. P13 adds deliberately different scientific evaluation priorities across a panel, without predetermined positive/negative verdicts or fabricated disagreements. Expertise may change attention but must not change evidentiary standards. P11 is retired: no separate all-component-checklist generation condition is retained. Recognition quality is validated for the three retained conditions. These are our study controls, not borrowed efficacy claims from the ideation papers.

**Extraction and analysis.** Scientific components are extracted after generation from both applicant and AI texts. No recombined component menu is supplied to generators. H1/H4 remain the nine-test confirmatory family; H2/H3/H5 and H6 retain their existing roles. RQ9 concerns representation robustness and call heterogeneity; RQ10–13 add the collaborator-requested secondary tests. The blinded proposal-quality subset reports literature-relative novelty and other quality dimensions separately from embedding diversity and funding outcomes; no embedding distance is treated as quality. Pilot prompts for format, fidelity and feasibility, not for maximizing or eliminating the observed human–AI gap. Freeze every adopted adaptation and its citations with the prompt version.

### P00 — Build the call packet

```text
ROLE: Extract the requirements of a funding call from its supplied historical
materials. Preserve its scientific scope and actual review criteria.

SOURCE MATERIALS WITH SECTION IDS:
{CALL_SOURCE_SECTIONS}

Return a JSON call packet with:
call_id; source_hashes; deadline; language; scientific_scope;
permitted_project_types; eligibility; required_sections;
length_limits (value, unit, applicable section);
evaluation_criteria (criterion_id, wording, weight if explicitly supplied);
score_scale (allowed_values, anchors, favorable_direction);
resource_or_preliminary_evidence_requirements; unresolved_fields.

Every substantive field must include exact source quotes and section IDs.
Do not convert source-document character counts into application limits.
Do not infer weights, score meanings or missing eligibility rules. Distinguish
mandatory requirements from examples and advice. Mark missing facts unresolved.
```

A checked call packet, not unchecked model extraction, enters generation. If a required scientific field is missing, the call is not ready for its affected condition.

### P01 — Independent full-proposal generation in one pass

This original study template incorporates the limited problem–method–evidence organizing principle attributed above to ResearchAgent; it does not implement that system’s retrieval or revision workflow.

```text
ROLE: Write one complete scientific research proposal responding to the
supplied call, in this response.

VERIFIED CALL PACKET:
{CALL_PACKET}
PERMITTED BACKGROUND:
{BACKGROUND_PACKET_OR_EMPTY}
OUTPUT LANGUAGE:
{OUTPUT_LANGUAGE}
REQUIRED SCIENTIFIC SECTIONS AND LENGTH LIMITS:
{PROPOSAL_FORMAT_AND_LENGTH_RULES}

Generate exactly one complete proposal. Follow the call's objectives,
permitted project types, required headings and length limits. Develop a
scientifically meaningful question or objective and explain the intended
contribution. Explain how the proposed methods, data or materials, and
analysis or evaluation will address the question and support the conclusions.
State a hypothesis only when appropriate to the project. Do not force an
experimental or causal hypothesis onto a descriptive or theoretical task.

Describe proposed work in enough detail to assess its scientific rationale
and feasibility. Future experiments or data collection are allowed only if
this call permits them. Distinguish established evidence from proposed work
and assumptions. Do not invent completed preliminary results, access to
facilities or private data, collaborators, credentials or citations.
Describe essential resource assumptions and material evidence gaps honestly.
A claim of novelty must not be presented as verified merely because it is
generated here. Do not imitate an applicant or claim their credentials.

Return the complete proposal, not an outline, a list of alternative ideas,
or an intermediate draft awaiting expansion. Include an abstract if required
by the call. Keep scientific content in the required proposal sections;
completion flags are administrative metadata, not a substitute for the text.

Return only JSON:
{
  "title": "...",
  "sections": [{"section_id": "...", "heading": "...", "text": "..."}],
  "completion_flags": [],
  "resource_assumptions": [],
  "cited_source_ids": []
}
```

The host supplies the allowed section IDs, headings, lengths and scientific dossier scope. It validates schema, complete output and truncation without selecting for novelty or quality. The generator receives no applicant submission/title, target components, historical reviews, funding outcomes, or previous generated proposals. Freeze the background packet policy and source registry before generation; use the same call-level packet across models and core conditions, with persona evidence as the explicit P02 addition. An empty packet is permitted and does not erase pretrained knowledge. Do not invent bibliographic metadata; cited source IDs must resolve to supplied sources. No online retrieval or invented claim of a comprehensive literature search is allowed in this generation workflow.

Generate N_c independent complete proposals per model/condition/call, one per fresh request. Do not refill scientific duplicates or weak outputs with better candidates. Store metadata separately from scientific sections used for embeddings, and extract components independently afterward using P05/P06. A technical retry is another logged attempt for the same slot, not an extra scientific candidate to rank.

### P02 — Persona full-proposal generation in one pass

Use P01 unchanged except for adding this instruction and data block. The varied-starting-context principle is adapted from [Terwiesch et al. (2026)](https://journals.sagepub.com/doi/10.1177/10591478261474243); scientific publication grounding is our study-specific implementation.

```text
SCIENTIFIC EXPERTISE PROFILE:
{SANITIZED_PERSONA_PROFILE}

Use this profile as evidence of scientific experience available before the
call deadline. Let its supported domains, methods, data experience and
research questions inform the problem you address and the approach you use.
Where justified by the evidence, connect complementary areas of expertise;
do not force an unrelated combination or merely substitute terminology.

Do not copy a prior paper's proposal, invent resources, or impersonate the
person. Publication facts are background, not proof that proposed work has
already been done. Do not infer the submitted proposal or funding history.
Do not assume excellence, risk preference or a favored conclusion from a
name, affiliation or demographic characteristic. Produce one complete
proposal under the same call, format, length and evidence rules as P01.
Return exactly the same JSON schema.
```

Only the expertise context changes. Reuse the same admissible profile multiset and slot assignments across models; do not choose profiles for observed diversity. Strip administrative mapping fields before rendering. There is no persona idea-generation or expansion pass.

### P03 — Sequential differentiated full-proposal generation

Replace the former optional proposal batch condition with `G-sequential-different`. This adapts differentiated sequential search from [Boussioux et al. (2024)](https://doi.org/10.1287/orsc.2023.18430) to complete scientific proposals. It is a stronger diversity-seeking intervention than P01, not a claim to maximize every possible diversity measure.

For each call/model/independent chain, request proposal 1 with P01. For positions 2 through N_c, use P01's call, evidence, final format and output schema plus this block:

```text
PREVIOUS COMPLETE PROPOSALS IN THIS GENERATION CHAIN:
{ORDERED_PREVIOUS_PROPOSALS}

Write exactly one new complete proposal for the same call. Seek a substantive
scientific contribution different from those already proposed above. Consider
differences in the research question, hypothesis where applicable, explanatory
mechanism, approach, data/materials, or their meaningful scientific combination.
A change of wording, title or labels alone is not a new contribution. Sharing
a method or dataset is acceptable when the scientific question or combination
is substantively different. Preserve scientific coherence, feasibility and
call compliance; do not create arbitrary differences merely for variety.

The previous proposals are comparison material, not verified evidence. Do not
copy their unsupported assumptions or treat their planned findings as facts.
Do not revise or rank them. Return only the new complete proposal using the
same JSON schema, section requirements and length limits as P01.
```

At step t, supply all t−1 previous full scientific proposals from the same call/model/condition/chain in generation order. Exclude applicant proposals, human reviews/outcomes, other models' outputs and analysis scores. Save history IDs, exact content hashes, input/output token counts and chain position. Reconstruct a fresh API request with the full declared history; do not rely on undocumented provider session state. The first step is not labeled as already receiving differentiation context.

Hold model version, supported temperature/reasoning settings, background, final length and technical-retry policy fixed relative to P01. Temperature controls sampling; one-at-a-time versus sequential-history generation controls context and instructions. They are different experimental factors. Do not describe P01 as a high-temperature condition. P03 tests the combined history-plus-differentiation intervention, not the isolated effect of either. It adds input tokens and is not compute-matched; report that cost explicitly. For approximately L tokens per proposal, repeated history alone contributes about L × N_c(N_c−1)/2 input tokens across a chain, before call/prompt tokens and caching effects.

Every successful slot produces one complete proposal in one pass, with no concept-expansion stage or rejection for weak novelty. Include scientifically repetitive outputs in both history and analysis. On a terminal technical failure stop/flag the incomplete chain; do not renumber it as a complete N_c set. Resume only from the exact validated chain history. Within-chain proposals are dependent; independent full chains, not shuffled prefixes, estimate generation variability. Average chain effects within calls, then use call-family inference. Freeze the number of chains from the development cost/precision audit. Compare P03 and P01 on the same eligible calls at N_c; report both improvement over P01 and any residual applicant gap. Any equivalence claim requires a separate prespecified margin.

### P04 — Retired expansion prompt

Retired November 19, 2026. No template, request or comparison is scheduled for P04. Its identifier is reserved to preserve references to P05–P12; extraction and review prompts keep their existing IDs.

### P05 — Source-grounded proposal-component extraction

```text
ROLE: Extract scientific content from the supplied proposal without improving,
reviewing or rewriting its science. Origin and funding outcome are withheld.

IMMUTABLE SOURCE SECTIONS:
{PROPOSAL_SECTIONS_WITH_IDS}
COMPONENT SCHEMA:
{COMPONENT_SCHEMA}

Identify all substantive aims. For each, extract the stated research
questions/objectives, hypotheses if present, methods/design, datasets or
materials, intended contributions, system/scope, validation, preliminary
evidence, feasibility and resources. Retain minority aims and unusual details.
Split distinct claims into separate items and preserve which method/data
addresses which question or tests which hypothesis.

Use short source-faithful scientific statements without a fixed item or
sentence quota. Preserve direction, negation, uncertainty, conditions and
important qualifiers. Distinguish background knowledge, preliminary results,
proposed work, predictions and intended contributions. Do not turn intentions
into achieved discoveries or infer a missing hypothesis.

For every item and relationship, include exact source quotes and section IDs.
Use present/not_stated/explicitly_absent/not_applicable/unresolved according
to the supplied schema. Mark not_applicable only with source support or a
supplied instrument rule. Retain empty arrays for absent components. Do not
use reviews, outcomes or assumptions about what a good proposal should say.

Return only JSON conforming to COMPONENT_SCHEMA, including unresolved items.
```

For long proposals, apply extraction by source section/chunk, then reconcile duplicate mentions across the entire document. Reconciliation may merge repeated expressions of one item, not distinct aims sharing vocabulary. Preserve original item IDs and merge provenance. The verification pass reads all original scientific sections, including those producing no extracted items.

### P06 — Verify extraction and reconcile components

```text
ROLE: Audit whether the extracted record faithfully covers the source proposal.
Do not evaluate scientific merit or add scientifically plausible missing ideas.

SOURCE SECTIONS:
{PROPOSAL_SECTIONS_WITH_IDS}
CANDIDATE COMPONENT RECORD:
{COMPONENT_RECORD}

Check each item's quotes, factual support, uncertainty, negation and knowledge
status. Check links between questions, hypotheses, methods and data. Inspect
the source independently for omitted substantive aims or distinctive details.
Identify duplicated mentions without merging different scientific claims.

Return JSON:
{
  "item_checks": [{"item_id": "...", "status": "supported|unsupported|altered|unresolved",
                   "reason": "...", "evidence": []}],
  "link_checks": [],
  "omitted_source_content": [{"section_id": "...", "quote": "...", "reason": "..."}],
  "suggested_source_supported_corrections": [],
  "needs_human_resolution": false
}
```

Code verifies quote matches and valid IDs. Corrections create a new record version and are rechecked. Verifier agreement does not substitute for expert validation of recall, rare-content preservation and linked meaning. An unresolved extraction is not silently scored as absence.

### P07 — Neutral rephrasing of verified components

```text
ROLE: Express verified scientific content in a consistent neutral register
without compressing away distinctions. Do not create new content.

VERIFIED COMPONENT RECORD AND SUPPORTING PASSAGES:
{VERIFIED_COMPONENT_RECORD}
REQUESTED OUTPUT:
{COMPONENT_OR_WHOLE}

Preserve every substantive item, its uncertainty, negation, scientific scope,
knowledge status and links. Use consistent terminology. Do not impose a fixed
sentence count, erase qualifiers to shorten sentences, or add a generic
hypothesis/method/contribution. Avoid promotional language without weakening
or strengthening the scientific claim.

For component output, retain item boundaries and source item IDs. For whole
output, organize the verified scientific items coherently and preserve their
relationships; do not add administrative material. Missing components remain
empty in structured data and are not replaced by repeated placeholder prose.

Return JSON:
{
  "items": [{"source_item_ids": [], "neutral_text": "..."}],
  "whole_scientific_text": null,
  "unresolved": []
}
```

Set `whole_scientific_text` when requested. Validate that every substantive source item is represented and no unsupported item is introduced. For the primary verified-neutral branch, verified component statements can be used directly; this additional stylistic rewrite is optional and independently versioned. Retain original quotations as a sensitivity representation. The legacy 13-sentence/5-sentence-abstract NCEMS style remains a separately labeled bridge.

### P08 — Independent review generation

```text
ROLE: Provide one scientific assessment of this proposal under the supplied
call's actual evaluation rubric. Make your own assessment from the supplied
information; no other reviews or funding decision are available.

VERIFIED CALL AND SCORING PACKET:
{CALL_PACKET}
COMPLETE ADMISSIBLE PROPOSAL DOSSIER:
{PROPOSAL_DOSSIER}
REVIEW FORMAT AND LENGTH GUIDANCE:
{REVIEW_FORMAT_POLICY}

Evaluate the scientific case using the call criteria. Identify the strengths,
limitations and uncertainties you judge material. Support specific appraisals
with proposal section references where possible. Distinguish a weakness in
the science from information unavailable in this dossier. Do not assume that
missing attachments, a CV or private evidence prove the underlying weakness.

Do not fabricate claims, references or completed experiments. Do not use an
NCEMS rubric or a 1-to-5 scale unless this call actually specifies them. Apply
only verified score anchors and weights. If a numeric criterion cannot be
scored from the supplied rubric, return null with a reason. Do not predict or
reproduce an actual historical funding decision.

Return JSON:
{
  "assessment_text": "...",
  "criterion_scores": [{"criterion_id": "...", "score": null, "rationale": "..."}],
  "overall_score": null,
  "score_unavailable_reason": null,
  "dossier_limitations": []
}
```

Do not require a comment on every scientific component here. Apply the actual review form when known; if unavailable, use a declared neutral review-format policy fixed across AI conditions. Do not force AI reviews to match each historical review's exact length or reveal human criticism to determine their content. Model score rationale can be stored separately from the primary narrative endpoint; make the text-selection rule symmetric with available human fields.

### P09 — Expertise-persona review generation

R-persona uses P08 plus:

```text
REVIEWER SCIENTIFIC EXPERTISE:
{SANITIZED_REVIEWER_PROFILE}

Apply the supported scientific expertise as a perspective on this proposal.
Do not imitate the person's language or infer their historical opinion. Do not
claim that this profile supplies private knowledge or unavailable evidence.
Use the same rubric, format and scoring rules as the independent condition.
Do not manufacture disagreement or adopt a predetermined positive or negative
verdict because of this expertise profile.
```

Each R-persona review is a separate request with a supported expertise profile. Use fresh contexts with no access to previous generated reviews. Match R_ci, call rubric, dossier, output-length policy and model settings to R-independent; scientific expertise is the condition-specific input. No batch variant is scheduled.

### P10 — Extract and map review appraisals

```text
ROLE: Extract what this reviewer actually says; do not conduct a new review.

REVIEW WITH IMMUTABLE SECTION IDS:
{REVIEW_SECTIONS}
PROPOSAL COMPONENT RECORD AND SOURCE SECTIONS, FOR MAPPING ONLY:
{PROPOSAL_RECORD_AND_SOURCE}

Split substantive scientific appraisals into atomic claims. Preserve stance,
severity, uncertainty and reasoning. Map each to one or more scientific
components and, where possible, item/aim IDs. The proposal helps identify the
target; it must not supply an appraisal absent from the review.

A criticism of a missing hypothesis or validation plan can target a missing
component. Distinguish that from no reviewer mention. Treat administrative
recommendations and pure score restatements separately. Allow neutral,
mixed and unmapped claims. Do not manufacture a strength to balance a weakness.

Return JSON:
{
  "claims": [{
    "claim_id": "...",
    "appraisal_text": "...",
    "stance": "strength|weakness|neutral|mixed",
    "component_types": [],
    "target_item_ids": [],
    "target_is_missing_component": false,
    "review_evidence": [{"section_id": "...", "quote": "..."}],
    "proposal_evidence": [],
    "mapping_status": "mapped|ambiguous|unmapped"
  }],
  "administrative_content": [],
  "unresolved": []
}
```

Check exact review quotes separately from proposal mapping. Review claims are not marked true just because their subject can be located. Create whole/strength/weakness/component texts from verified claims while preserving reviewer identity and empty fields. Optional neutral rewriting follows P07's preservation rules, applied to appraisals; no new evaluation is allowed.

### P11 — Retired component-guided generation prompt

Retired November 19, 2026 to keep exactly three review-generation conditions. No separate all-component checklist is scheduled. P10 still extracts component-specific appraisals from every condition; P13 remains the distinct review-focus intervention. Preserve this identifier so existing references to P12–P14 remain stable.

### P12 — Scientific matching for coverage screening

```text
ROLE: Compare scientific content, not writing similarity or author identity.

TARGET COMPONENTS AND SUPPORTING PASSAGES:
{TARGET_RECORD}
CANDIDATE COMPONENTS AND SUPPORTING PASSAGES:
{CANDIDATE_RECORD}

Judge research question, hypothesis if present, methods, datasets/materials,
contribution and their defining relationships separately. Use equivalent,
partially_overlapping, different or insufficient_information. Shared topic
words are not sufficient; paraphrases can be equivalent. Preserve differences
in direction, conditions, target system and the question-method connection.

Give a linked-contribution match only when this single candidate preserves
the target's defining scientific relationship. Do not combine parts of other
candidates. Explain each judgment with the supplied evidence. Do not infer
missing facts or rank quality.

Return JSON with per-component judgments, evidence, linked-contribution
judgment, and unresolved issues under the supplied matching schema.
```

This is an automated screening/matching instrument requiring expert calibration. Neither a model-generated match label nor a cosine threshold is scientific ground truth. Freeze retrieval recall checks and matching thresholds on development data before confirmation.

### P13 — Deliberately varied review-focus panels

`R-focus-diverse` is a collaborator-proposed intervention, not a claim that ideation papers validate review quality. It differs from R-persona: expertise profiles describe a scientist’s supported background, whereas focus assignments explicitly direct attention to a particular evaluation dimension. P11 is retired. Each reviewer receives one main scientific evaluation priority; all receive the same proposal and common rubric.

Candidate focus catalog: novelty; feasibility; a call-specific domain concern; relevance to emerging scientific directions; generalizability; clinical/translational relevance; mechanistic insight; reproducibility; risk–benefit; and measurement validity. Define “call-specific concern” in advance from the call, not a deliberately bizarre request. Clinical, mechanistic or other inapplicable priorities are excluded by a rule frozen before outcomes. Emerging-topic relevance is scientific timeliness, not a reward for fashionable labels.

For proposal i, assign exactly R_ci focuses from the call-applicable catalog, without replacement when possible, balancing assignments across the call with a stored random seed. If R_ci exceeds applicable focuses, preregister repeats and report them; never invent irrelevant lenses to force diversity. Use identical focus assignments across all three models and the same length/output-token policy as R-independent. A panel of three gets three focuses, not ten reviews; across proposals, balanced assignments cover the available catalog. Separate requests do not see one another's reviews or human appraisals.

Use P08 plus:

```text
PRIMARY SCIENTIFIC EVALUATION FOCUS:
{FOCUS_NAME_AND_OPERATIONAL_DEFINITION}

Prioritize this dimension in your assessment and provide specific, supported
strengths, limitations and uncertainties relevant to it. Explain why those
observations matter for this proposal. Do not insert the focus label as filler
or substitute a generic checklist for a scientific appraisal.

Use the common call rubric and evidence standards. Your assigned focus is
not a predetermined verdict. Do not manufacture objections, praise, unusual
claims or disagreement. Where the dimension is inapplicable or evidence is
insufficient, say so. Do not treat popularity as scientific merit. Mention a
critical issue outside your focus if necessary. Assign numerical scores only
when justified by the supplied rubric and evidence; otherwise return null
with a reason. Return the same JSON schema as P08.
```

Measure whole-review diversity and, crucially, extracted substantive-claim diversity, validated distinct-issue coverage, precision/recall and unsupported appraisals. Keep assigned labels/administrative metadata out of embeddings and audit focus-word sensitivity. Compare within-component diversity where enough reviewers address the same component; increased between-component attention alone is not diverse judgment about the same issue. Preserve R_ci matching and identical analysis support. Compare quality and score calibration separately: a reviewer focusing on one dimension may have insufficient evidence for an overall score, and artificial differences in scores are not a success criterion. An all-ten-focus enlarged panel, if ever added, would be a separate panel-size experiment.

### P14 — Blinded human proposal-quality rating form

This is an expert rating form, not another generation stage. The assignment packet includes a masked proposal, the same call and admissible evidence, verified rubric anchors and rating instructions; it excludes source, model, generation condition, peripherality, funding and previous reviews.

```text
Evaluate this proposal under the supplied call using only the admissible
information. For each applicable rubric dimension, provide its anchored
score, a short evidence-based reason, and confidence. Distinguish scientific
weakness from unavailable dossier information. Mark inapplicable or unrateable
dimensions explicitly rather than assigning a default middle score.
Evaluate novelty relative to relevant prior knowledge, explaining the basis
and limits of that judgment. Do not infer quality from writing polish alone.
Provide overall merit only if the supplied rubric supports it, and disclose
any conflict or prior familiarity. Complete the rating independently.
```

Record blinded proposal ID, rater ID, criterion ID, score/null reason, justification, confidence, conflict/familiarity and rubric version. Keep a separate restricted linkage table for origin/model/condition. Expert recruitment and collection are required work; no quality results exist until ratings are obtained.

## Updated Overall Story

The proposed study tests whether within-call compression generalizes, where it occurs in scientific content, and whether reduced appraisal diversity coincides with missed or unsupported scientific judgments. It does not presuppose that every model compresses every component, that unusual ideas are superior, or that diversity loss necessarily changes funding accuracy.

If compression appears mainly in datasets/methods but not questions, the interpretation differs from compression of question–method combinations. If AI recognizes valid issues while using more homogeneous wording, the gate-keeping claim must narrow accordingly. If humans and AI miss peripheral contributions equally at matched size, the original core–edge relationship is insufficient evidence of AI-specific omission. All are informative possible outcomes.

## UPDATE LOGS

### November 18, 2026 — Initial NOVO plan

Recorded the current selected directory and grouped-assessment schema, replacing the previous round1 counts. Incorporated native-size per-model matching, source-linked scientific components, sanitized personas, call-family inference, calibrated omission, recognition validation and thirteen proposed prompt specifications. Existing pipeline files and data are unchanged by this document.

### November 18, 2026 — Generation model selection

Selected `gpt-6.2-astra`, `gemini-4-carbon`, and `claude-fable-5-2` for both proposal and review generation across enabled NOVO conditions. Added the shared configuration and model-identity requirements to the planned implementation. This is a plan update; runtime code and notebooks have not been changed.

### November 18, 2026 — NOVO paths and prompt comparison

Aligned notebook, implementation and result destinations with the existing `notebooks-NOVO/`, `src/NOVO/`, and `results-NOVO/` directories. Added explicit package imports, repository-root path resolution and per-module destinations. Compared P01/P04 with the current idea/expansion templates and recorded the scientific interpretation of the changed objectives, constraints, schemas and length policies. No generation code was run or modified.

### November 19, 2026 — One-pass proposals and cited prompt rationale

Replaced initial concepts plus expansion with one-pass complete proposals in G-independent/G-persona and the optional G-batch. Removed the generation-stage comparison, retired P04, revised RQ9, request budgets, schemas, notebook flow and implementation checks. Added verified primary-source links and explicit adoption/deferment decisions for the supplied prompt-design literature. Updated persona and review instructions while keeping measurement separate from generation. The earlier November 18 descriptions of P01/P04 and the count of thirteen active prompts are superseded; P00–P12 now contain twelve active specifications and the retired P04 placeholder. No runtime pipeline, existing NCEMS plan/results, or data were changed.

### November 19, 2026 — Collaborator-requested diversity and quality tests

Replaced proposal batch P03 with sequential cumulative-history differentiation; retained one-pass full proposals. Added R-focus-diverse/P13 and the human quality form P14, RQ10–13, literal idea-count and frequency definitions, an illustrative Vendi calculation and required real audit trace, finite-budget scaling, and blinded quality/edge analyses. Updated manifests and NOVO module/notebook destinations. Earlier statements deferring sequential generation or describing P03 as a single-response batch are superseded. The runtime directories are currently empty: these remain protocol specifications, not executed API runs or empirical results.

### November 19, 2026 — Exactly three review conditions

Retained R-independent/P08, R-persona/P09 and R-focus-diverse/P13. Removed R-batch and retired the P11 component-guided generation condition. Component extraction and recognition analysis remain common downstream measurements. Updated request-count illustrations for three proposal and three review conditions, distinguished expertise from evaluation focus, and retained H6/H11 as separate secondary comparisons.

### Relationship to prior plans

`analysis_plan_v2.md` remains the NCEMS status reference. The November 12 protocol remains a source of proposed scientific-component validation ideas, but its fixed illustrative call/output counts and G0/G1/G2 labels are not adopted here. Prior audit records describe their own snapshots. NCEMS source proposals have recently changed in the workspace; record current hashes before any extraction bridge and do not silently reuse summaries from earlier source versions.

## Analyses From Original Plan Not Yet Done (Moved Here)

All new NOVO scientific endpoints remain prospective. The following decisions must be frozen before confirmation:

| Decision | Evidence needed | Conservative default until resolved |
|---|---|---|
| Confirmation population | Selection provenance, scientific-task/rubric completeness and agreement-selection sensitivity | Describe current cohort only; do not generalize to all 596 calls |
| Assessment versions/stage | Verified chronology or archival process documentation | Unresolved assessor versions excluded from primary panels, retained for sensitivity |
| Generation model access and decoding | Validate the three selected IDs, supported settings and pilot reliability; freeze settings before confirmation | Keep the selected generation list fixed; no silent model substitution mid-experiment |
| Persona source budget/coverage | Author disambiguation, dates, evidence quality | No target-informed or invented profiles |
| Number of independent replicates | Pilot between-run variability, costs and precision simulations | No fixed large-scale run count claimed by this draft |
| Encoder/chunk policy | Full-text coverage and domain/language validation | No prefix-only representation labeled full text |
| Extraction/matching thresholds | Blinded expert validation across origins, rare content and domains | No unvalidated scientific-accuracy claim |
| Family splits and uncertainty | Recurring-call mapping and number of independent families | Family-held-out development and confirmation; explicit small-family caveats |
| Core–edge partitions | Stability and enough disjoint human references | Omit unstable cells from that endpoint, not from every analysis |
| Smallest meaningful differences | Substantive interpretation and precision analysis | Do not claim equivalence or “no recovery” from nonsignificance |

## Next Priority Execution Order

1. **Freeze an archive snapshot and audit eligibility.** Record current roots/hashes, restore selection provenance, retain assessment versions, resolve the four affected proposals, check rubric/format availability and recompute analysis-only scores.
2. **Build normalized contracts and family splits.** Produce manifests, N_c/R_ci schedules, current scientific-task eligibility and outcome-isolated prompt inputs. Keep historical selection flags for sensitivity.
3. **Pilot extraction before generation at scale.** Apply P05/P06 to current NCEMS and diverse NOVO development proposals, validate all five components and links, then test chunk representations and raw-versus-neutral sensitivity. Check omissions, not only extraction precision.
4. **Validate prompts and personas.** Pilot one-pass P01/P02/P03 and P08/P09/P13 at native size on development calls; check format, token coverage, unsupported evidence, source leakage, retries and review-panel counts. Keep all outputs and measure yield/cost, including cumulative-history token growth. Prepare blinded P14 packets and validate the idea codebook before count/quality claims.
5. **Freeze confirmation design.** Register population, calls/families, hypotheses, primary representation, model versions, budgets, independent replicate count, inference/multiplicity rules and validation thresholds before examining confirmation AI effects. Use pilot simulations for precision rather than copying illustrative sample sizes.
6. **Run confirmation generation/review and blinded measurement.** Persist complete logs and versioned components; do not adapt prompts to apparent model deficits on held-out calls.
7. **Run facets, coded idea counts/scaling, calibrated omission and recognition/quality validation.** Produce all planned call effects, missingness/validity summaries and reviewer-aware sensitivities before selecting manuscript examples.
8. **Build figures and update the manuscript.** Report NCEMS legacy, harmonized NCEMS and NOVO findings distinctly, with actual eligibility, source information, effect uncertainty and limitations.

### Implementation acceptance checks

Before treating the pipeline as ready, require meaningful tests for: source row conservation and activity separation; one selected assessment per reviewer/stage; no outcome or target-title leakage; exact native-size generation schedules; one-pass proposal requests with no expansion or selection stage; different counts for text and scored panels; component evidence/ID validity; preserved uncertainty and absent hypotheses; no duplicate-content deletion; complete token coverage; cache invalidation; correct AI/human effect direction; no cross-call nearest neighbors; disjoint coverage partitions; equal-size human/AI references; correct score direction; reviewer/family clustering; complete sequential histories and deterministic resume; balanced focus assignments at exactly R_ci; validated idea incidence and traceable Vendi arithmetic; chronological scaling prefixes; blinded quality linkage and sample weights; and stable output paths that cannot overwrite NCEMS results.

The deliverable of implementation is a reproducible analysis with explicit unsupported or unresolved cells, not a pipeline forced to reproduce the original result.
