# Experimental protocol for scientific proposal coverage and review

Working design, November 12, 2026. This specifies proposed work; no new-agency files have been analyzed and no proposal or review generation has been run for this protocol. The archive is described by the researcher as approximately 14,000 submissions, their reviews and recorded funding outcomes, and 600 calls with evaluation criteria from 2019–2026. Access to numeric scores, reviewer identities, historical document versions, and resource information still requires verification.

The study consists of two linked experiments. In the generation experiment, AI receives a call and permitted scientific background, then produces proposals that are compared with submitted proposals. In the review experiment, AI assesses the same submitted proposals that received historical expert reviews. A separately validated representation of each proposal's scientific contributions connects the experiments. The main review comparison does not compare human reviews of human proposals with AI reviews of different AI proposals.

## Study scope and workload

Use the full archive to describe submission patterns, call characteristics, scientific content, and review availability. Use sampled calls for controlled generation and intensive review comparisons. The call count below is a planning example, not a power calculation or evidence that the archive contains enough eligible calls.

| Stage | Planning specification | Output |
|---|---|---|
| Archive audit | All available calls, proposals, and reviews | Linked records, document versions, completeness and eligibility table |
| Development | Approximately 10 call families | Frozen extraction instructions, matching rules, generation procedures, and annotation guide |
| Generation confirmation | 60 eligible held-out calls × 3 model versions × 3 conditions × 20 outputs | 10,800 final scientific proposal narratives, plus all intermediate drafts and logs |
| Standard review comparison | 6 submitted proposals per call × 60 calls × 3 models × 3 reviews | 3,240 AI reviews paired with existing expert reviews |
| Structured review intervention | Prespecified subset of 120 of those proposals × 3 models × 3 reviews | 1,080 additional AI reviews |
| Expert validation | Development and separate held-out samples | Adjudicated contribution records, proposal matches, review claims, and quality judgments |

The planning total is 4,320 AI reviews. Each final proposal involves multiple model requests, so 10,800 proposals is not 10,800 requests. A pilot must measure tokens, failure rates, annotation time, and costs before deciding the final scale. A smaller call sample with rigorous validation is preferable to losing validation to fund more generation.

Retain NCEMS as the exploratory case and a bridge to the original paper. Re-annotate its 23 proposals and 85 reviews using the same scientific-contribution scheme, and rerun a prespecified subset of the new generation/review conditions there. Agreement across the small, scientifically interpretable case and held-out new-agency calls would establish the scope of replication. Disagreement is informative about domain or call conditions. NCEMS must not become a second confirmation sample after being used to develop the hypotheses.

Select confirmation calls by prespecified strata such as broad field, year, call scope, and novelty emphasis. Hold out related call families from development wherever feasible. Define a generation-eligible population based on documented scientific tasks and adequate submitted content. Report exclusions, including calls whose requirements cannot be realistically simulated without unavailable preliminary evidence. Generalization is to the sampled eligible population, not automatically all 600 calls.

For the proposed three-way human comparison, calls with at least 21 usable submissions permit a calibration set of 10, a human reference set of 10, and at least one held-out target. Smaller calls can support other descriptive and review analyses. Revisit the eligibility threshold after auditing the actual call-size distribution; do not select calls based on the magnitude of an AI deficit.

## 1 Build the linked archive

Create stable identifiers for calls, proposal versions, applicants or teams when available, reviews, and reviewers when available. Retain original documents and preserve page, section, paragraph, and table locations during text extraction. Record parsing failures and unreadable content instead of silently dropping them.

Distinguish submission date from award date, and pending from rejected outcomes. Identify initial independent reviews, panel summaries, applicant responses, and revised reviews where the archive permits it. Use the proposal version actually reviewed. Treat post-discussion reviews as a different assessment setting from independent initial critiques.

Separate administrative material, scientific narrative, references, and supporting evidence. Preserve scientific figures or tables when they carry the hypothesis or design; exclude or separately analyze cases where the model input omits material that historical reviewers saw. Use the same scientific content in AI review as was available in the archived version, while documenting unobserved historical context.

For each call, produce a checked call record containing the scientific scope, original wording, eligibility, required sections, length limits, evaluation criteria and weights where supplied, permitted data/resources, and deadline. Do not invent missing weights or impose the NCEMS evaluation rubric on another agency.

Call the observational corpus human-submitted or applicant-submitted. Later submissions may incorporate AI assistance. Before/after dates and estimated writing modification are descriptors, not verified authorship labels.

## 2 Extract contribution records from proposal text

The unit is a substantive aim or contribution, not a paragraph, keyword, or entire proposal. Multiple aims can produce multiple linked records. Preserve all explicit aims; use a fixed annotation rule to identify principal contributions from objectives and the scientific case, independently of reviews and outcomes. Do not infer centrality from novelty language alone.

Each record contains:

| Field | Required content |
|---|---|
| Question or objective | The specific uncertainty or goal |
| System and scope | Organism, population, setting, scale, and material conditions |
| Hypothesis or explanation | Proposed relationship, direction, conditions, and uncertainty; missing when not applicable |
| Approach | Method, intervention, data, model, comparison, or analytical strategy |
| Discriminating evidence | What evidence would address the uncertainty or separate explanations |
| Intended contribution | What would become known or possible, stated as an intention |
| Relationships | Which approach addresses which question or tests which explanation |
| Provenance | Exact supporting passages and their original locations |
| Knowledge status | Prior finding, proposed investigation, prediction, or established preliminary evidence |

The representation adapts scientific-claim extraction and scientific-facet approaches; it is not itself an already validated published instrument. Relevant precedents are [SciClaim](https://aclanthology.org/2021.emnlp-main.381/), [SciREX](https://aclanthology.org/2020.acl-main.670/), and [Scideator](https://arxiv.org/html/2409.14634).

### Extraction procedure

First, parse and label source passages without changing their prose. For long documents, extract candidate records by section and reconcile them across the document. Use explicit coreference links to combine repeated mentions. Do not merge distinct hypotheses merely because they use the same entities.

Second, use an LLM to produce structured contribution records. A verification pass checks every scientific field against the cited passages and flags unsupported additions, missing principal aims, changed direction, and altered certainty. It should not repair a weak proposal by inventing content. An additional model can help identify disagreements, but agreement between models is not a substitute for expert validation.

Third, retain both the source wording and any canonical label used to match synonyms. Keep rare concepts even when they appear only once. Uncertain or absent fields stay uncertain or absent; missing hypotheses are legitimate for some descriptive, theoretical, and design proposals.

Apply the same extraction procedure to final human-submitted and AI-generated narratives. An AI generator's structured plan is useful for tracking development, but it does not receive a privileged error-free measurement status.

### Draft extraction instruction

> Identify the research aims explicitly advanced in this proposal. For each aim, extract the question, system, proposed explanation if present, approach, discriminating evidence, and intended contribution. Preserve the links between these elements. Cite exact source passages and their locations. Distinguish background findings from proposed work and predicted outcomes. Preserve conditions, negation, and uncertainty. Do not assess novelty, use reviewer comments, fill gaps, or infer an explanation the proposal does not state. Mark missing information explicitly.

### Expert validation

Start with approximately 120 development records spanning fields, document lengths, common and unusual content, and both submitted and generated origins. Two appropriately qualified annotators independently assess an overlapping sample; a third adjudicates substantive disagreements. Inspect the original scientific text rather than only the extractor's candidate fields, so omissions can be detected.

Measure unsupported additions and recall of principal contributions separately. Audit question–approach links, causal direction, uncertainty, and rare terminology. Examine errors by origin and rarity: an extractor that misses uncommon human contributions more often can manufacture the result of interest. Choose acceptable error levels based on the sensitivity of the final comparisons during development, then lock them. If a domain fails validation, route it to manual annotation or narrow the study's scope.

Reserve a distinct validation sample from confirmation calls. Proposed starting workloads for calibration are roughly 400 proposal-pair judgments and 600 review-claim judgments, each double-coded where resources permit. These are budgeting examples; use observed disagreement and desired precision to set final samples. Reuse expert work carefully, but never call examples used to tune a rule an independent validation of that rule.

## 3 Generate proposals under controlled information conditions

### What the model receives

Every request receives the checked original call and the relevant proposal format and evaluation criteria. Literature-grounded conditions also receive a fixed call-specific collection assembled from public call material and documented field searches, with availability restricted to the original deadline. A development starting point is 15–25 short source records per call, including nearby and more distant relevant work; pilot token use and scientific adequacy before fixing this number. Keep source identifiers, dates, abstracts, and important methodological passages.

Do not build the generation collection from held-out submission text, target titles, their private reference lists, historical reviews, or awards. Prior team publications can be supplied in a separately labeled expertise condition, after verifying dates and removing target-derived material. A deliberately target-informed task would answer a different research question.

Model knowledge can still include post-deadline science. Restricting explicit retrieval does not recreate a historical model or establish training nonexposure. Document model snapshots and public-exposure indicators where available; describe the experiment as retrospective generation by current models.

The supplied source collection is itself a possible restriction on exploration. Audit its topical and methodological breadth independently of target coverage. On a prespecified subset, vary source collections or allow a larger, equally budgeted retrieval space in G1 and G2. A persistent deficit under one narrow source packet alone cannot establish a general limit on AI exploration.

### Three principal conditions

| Condition | Information | Generation procedure |
|---|---|---|
| G0 Call only | Call and rubric | One independently generated scientific plan, ordinary critique/revision, then expansion |
| G1 Literature grounded | Same call plus fixed literature collection | Same stages as G0 |
| G2 Explicit recombination | Same information and search permissions as G1 | One plan built through explicit scientific-component recombination, novelty-oriented critique/revision, then the same expansion stage |

This G0 is a budget-matched call-only control. A separate exact rerun of the original two-stage NCEMS procedure can bridge to the existing paper. Do not describe the new matched control as an exact replication if critique steps are added.

Each run uses a fresh context. A practical matched architecture has four requests: draft a scientific plan; critique it; revise it; expand it into the call-native scientific narrative. G0 and G1 use ordinary scientific critique under the call rubric. G2 explicitly compares the proposed question–approach connection with the supplied literature and checks whether the combination is meaningful. Keep model versions, token ceilings, revision limits, and output requirements comparable. Randomize condition scheduling within calls to reduce run-time confounds.

For G2, controlled sampling of literature anchors can distribute starts across nearby and more distant connections. Define those sampling rules before seeing target coverage. Let the model reject an incoherent combination, but log the rejection and any replacement against its generation budget. Anchors are inspirations, not a closed vocabulary: justified departures remain possible and are recorded.

The procedure draws on [Scideator](https://arxiv.org/html/2409.14634), [SciMON](https://aclanthology.org/2024.acl-long.18/), and staged ideation in [ResearchAgent](https://aclanthology.org/2025.naacl-long.342/). It is a proposed autonomous adaptation, not a replication of their complete systems or human–AI studies.

### Draft G2 instruction

> Using the call and supplied literature, propose one coherent scientific investigation. Identify its specific question, proposed explanation when applicable, approach, and the evidence that would resolve the question. Explain which ideas from the supplied sources inform the proposal and why their connection is scientifically meaningful. Identify the closest supplied prior work and the substantive difference. Avoid combinations whose only justification is that their terminology is unusual. Do not claim completed experiments, fabricate preliminary data, or invent citations. Preserve uncertainty and state necessary resource assumptions.

For its critique stage, ask whether the scientific relationship is supported, whether the proposed test can distinguish the explanation, and whether the claimed departure is already present in the accessible literature. A bounded check cannot certify absolute novelty.

### Comparable outputs and preserved drafts

Generate the scientific sections required by each call, respecting its actual format and limits. Do not compare full human narratives with short AI abstracts and call that a full-proposal comparison. If cost requires a shorter scientific-brief study, restrict both sides to comparable original scientific sections and describe that narrower endpoint explicitly.

Unavailable private preliminary evidence is a real information asymmetry. Do not fabricate model-owned laboratory results, facilities, or team resources. Either provide legitimate common resource information, focus on eligible calls that permit a meaningful comparison, or stratify interpretations by evidence requirements. Call-only capability is not intrinsic scientific creativity under equal human expertise.

Save the initial plan, revised plan, final narrative, citations, and resource assumptions. Extract content at all stages on a subset to locate any change during expansion. Preserve duplicate and invalid outputs; scientific failures count against operational generation yield. Technical retries follow a fixed policy with logged attempts. Scientific success must not determine which outputs are silently replaced.

## 4 Measure what generation covers

### Pairwise scientific matching

Compare submitted target contributions with candidate contributions in the AI pool and human reference pool. Initially examine all candidate pairs in modest within-call sets. If retrieval later reduces the number of pairs, measure retrieval recall on a fully adjudicated subset so retrieval omissions do not become apparent model omissions.

Assign separate judgments for question, hypothesis where present, approach, and linked scientific contribution. Suggested component labels are equivalent, partially overlapping, different, and insufficient information. The linked-contribution judgment asks whether one candidate preserves the material relationship that defines the target idea; shared topic words are insufficient.

Aspect matching has precedent in [ASPIRE](https://aclanthology.org/2022.naacl-main.331/), but the proposal-specific equivalence rules need expert calibration. Automated scores should identify plausible pairs and scale a validated classification, not define scientific truth by themselves. Include both apparent matches and misses in validation, with source identity hidden where feasible.

### Draft matching instruction

> Compare the two contribution records using their supporting passages. Judge the question, explanation, approach, and their connection separately. Identify precisely what is shared and what materially differs. Shared vocabulary or field membership is not sufficient. A paraphrase can be equivalent. Changed causal direction, changed scope, or a different question–method relationship can be substantively different. Do not infer missing content. Give a linked-contribution match only when a single candidate preserves the defining scientific relationship.

If the target question appears in AI proposal A and its method in AI proposal B, that counts toward component availability but not recovery of the linked idea. Average principal-contribution coverage within each proposal before averaging across proposals, preventing proposals with many annotated aims from automatically dominating the result.

### Human sampling reference and edge definition

Within each eligible call, use repeated prespecified partitions into calibration proposals C, reference proposals H, and held-out targets T. One feasible starting configuration is 10 in C, 10 in H, and the remainder in T. For the same targets, compare H with 10 AI outputs. Rotate partitions so targets are not limited to a few arbitrary proposals; repeated partitions do not enlarge the independent sample.

Define call-local peripherality from C alone, using validated scientific-content representations. Matching thresholds are learned on development calls, not adjusted to produce a desired human coverage rate. Do not use distance to H both to define the edge and to declare a human miss. With small calibration sets, report instability of edge assignments and supplement the analysis with independently assessed historical rarity or larger-call subsets.

Primary generation endpoint: excess AI omission of linked contributions over omission by an equal-sized human reference. A central prespecified hypothesis is whether this excess increases with independently defined peripherality. Report continuous rarity analyses as well as easily interpreted core/edge summaries.

For a target group g:

    Excess omission(g) = AI miss rate(g) − human-reference miss rate(g)

An illustrative result would be AI missing 70% of edge contributions while the human reference misses 45%, producing 25 percentage points of excess omission. These numbers are hypothetical. The comparison would be much less compelling if both missed 70%.

Secondary endpoints distinguish missing questions, explanations, methods, and combinations. Historical novelty and citation atypicality use only a documented prior literature reference and remain separate from call-local rarity. Evaluate AI-only contributions for validity to avoid equating human-relative coverage with the entire universe of worthwhile ideas.

### Describe the scientific form of the edge

For validated omissions and an independently sampled set of covered contributions, code nonexclusive categories: an uncommon question; an alternative or opposing explanation; an unusual approach; a neglected system, population, scale, or boundary condition; and an uncommon connection between otherwise familiar components. Require a source passage and a concrete description of what differs. Category definitions are developed without inspecting confirmation-condition differences. Combine frequency estimates with adjudicated examples; preserve cases that do not fit the initial categories rather than forcing them into a taxonomy.

Separately link these contributions to review claims about originality, significance, evidence, feasibility, and fit. This distinguishes, for example, a departure praised as consequential but considered difficult from one criticized as unsupported. Rarity, originality, and favorable appraisal remain different variables. A review can support several judgments about the same contribution.

During the pilot, check that linked-contribution matching has a usable resolution. If almost every human and AI comparison is a nonmatch, exact recovery is too sparse to be the sole endpoint. Prespecify graded scientific overlap and component-level results alongside the strict match, without loosening thresholds after seeing which definition favors the hypothesis. Local coverage also does not measure all worthwhile ideas outside the submitted pool.

With 20 AI outputs per condition, estimate coverage at smaller budgets and compare 20 AI outputs with the 10-human reference. Do not extrapolate a human curve beyond observed reference sizes. Larger-budget experiments can be reserved for a prespecified subset, selected independently of observed deficits.

## 5 Generate AI reviews of the same submitted proposals

The standard review input is the original reviewed scientific document, the original call, and its evaluation rubric. Use all available scientific material that the historical reviewers could see, subject to documented input limitations. Exclude historical reviews, funding outcomes, extracted human judgments, edge labels, and the expert-adjudicated contribution map.

Use three fresh review requests per model and proposal for the planning design. A single response asked for several reviews is not several independently sampled responses. Separate requests still share model assumptions; the purpose is to measure their redundancy, not presume independent expertise.

Select review targets using contribution features defined without AI review outcomes. For example, select three edge and three central proposals per call. This balanced design estimates an edge–core contrast; it is not automatically representative of all submissions. Use known sampling weights for population estimates, and include a separate random sample if that broader estimand becomes primary. If labels are unstable or calls lack enough eligible cases, use a locked continuous-rarity sampling rule and report the change.

### R0 Ordinary criterion-based review

> Review this proposal under the supplied call and evaluation criteria. Identify its principal scientific contributions, strengths, limitations, and important uncertainties. Explain the reasons for each substantive judgment and refer to the relevant proposal content. Use the original scoring scheme only where one is supplied. Do not infer missing preliminary results or treat an asserted expected outcome as an established finding.

Use a review-length range calibrated to the archive, with a sensitivity analysis for length. Human critiques may be shorter, differently structured, or informed by panel discussion; record those differences. Do not impose a rich new rubric on AI and compare it with human reviews written to a narrower task without acknowledging the mismatch.

For the planning counts above, implement R0 as a general review-planning request followed by the final criterion-based review for every target. R1 uses the same two-request budget, replacing general planning with explicit contribution extraction and appraisal. Thus the 1,080 extra R1 outputs have matched R0 controls within the original 3,240; they do not require an uncounted extra control group. One-shot R0 can instead be a separate sensitivity condition with its additional cost reported.

### R1 Extract then appraise

On a prespecified subset, ask the model first to identify the proposal's contributions from the document itself, then produce its review. Give it no expert map. Ask the ordinary-review control to use a comparable two-stage general planning/revision process and budget, so an intervention effect is not simply an extra request.

> Before writing the review, identify the proposal's principal scientific contributions and locate the supporting passages. For each, distinguish what is being proposed from what is already established. Assess the originality claim, the ability of the approach to answer the question, and the principal sources of uncertainty. Then write the criterion-based review, preserving both justified strengths and justified criticisms.

If this improves recognition, the intervention supports an attention or representation explanation under the tested procedure. It does not by itself establish that all remaining disagreements are errors.

## 6 Measure recognition and appraisal in review text

Create atomic review claims, each retaining the original wording and location. Map claims to independently identified proposal contributions. Allow claims about general feasibility, missing evidence, and off-target issues without forcing them onto a contribution.

Do not compare review vectors as the sole evidence of understanding. Code the following separately:

| Dimension | Coding question |
|---|---|
| Recognition | Does the claim identify the specific scientific contribution rather than only its topic or technique? |
| Fidelity | Does it represent the question, relationship, scope, and uncertainty accurately? |
| Appraisal criterion | Does the judgment concern originality, significance, validity, feasibility, fit, or another call criterion? |
| Valence | Is it favorable, critical, mixed, neutral, or unclear? |
| Reasoning specificity | Does it provide a proposal-specific reason, rather than generic praise or criticism? |
| Evidential support | Is the reasoning supported by the proposal or an independently checked scientific fact, unsupported, or unresolved? |
| Additional information | Does it add a distinct valid concern or strength to those already in the panel? |

Accurate recognition can accompany a negative appraisal. Praise does not establish recognition. Silence is lack of recorded recognition, not proof that the reviewer failed to understand; the denominator should emphasize principal, call-relevant contributions that a review could reasonably address.

A measurement model can propose these labels. Expert annotators adjudicate a stratified sample, with reviews de-identified and origin hidden as far as prose permits. Include random claims, apparent errors, model–human disagreements, and rare contributions. Use a union of human and AI claims for validity assessment, rather than declaring all human claims correct and all unmatched AI claims wrong. Preserve legitimate differences of judgment as unresolved or competing appraisals.

Keep selection probabilities for oversampled disagreements and suspected errors. Report error estimates within strata or weight them appropriately; a deliberately difficult validation sample does not directly estimate archive-wide error. Hide outcomes and provisional core/edge labels from adjudicators. Where possible, avoid using the generating model as the only judge of its own scientific overlap or review quality; evaluator separation supplements, rather than replaces, expert validation.

Primary review endpoint: the proportion of principal contributions accurately recognized in review text, reported at individual-review and matched-panel levels. Secondary outcomes include grounded positive and negative appraisals, unsupported claims, and distinct valid information accumulated as reviews are added. A panel can be highly redundant while still recognizing every contribution, or diverse in wording while making repeated errors.

Compare panels at sizes supported by the actual human reviews. If a proposal has two human reviews, compare with two AI reviews for a matched-panel result; a three-AI curve is an additional scale analysis. Where reviewer identifiers exist, account for repeated reviewers. Unknown identities limit claims about independent human judgment.

## 7 A worked example

The following proposal and review excerpts are fictional and demonstrate coding only.

An applicant proposes that variation among cells, rather than their average response, drives abrupt failure to recover from stress. The approach combines time-resolved single-cell measurements with a model comparison designed to separate effects of the mean and the variation.

| Observed text | Interpretation |
|---|---|
| AI proposal predicts average stress recovery from bulk measurements | Same broad topic; does not recover the stated explanatory relationship |
| AI proposal describes cellular heterogeneity but does not test its role in recovery | Partial component coverage; linked contribution remains incomplete |
| Review: “The use of single-cell data is innovative.” | Method noticed; central explanation not explicitly recognized; originality assertion requires support |
| Review: “The study separates the effect of cell-to-cell variation from the mean, but the proposed analysis may not distinguish their causal roles.” | Specific contribution recognized; critical methodological appraisal; validity requires checking the actual design |
| Review claims that the proposal contains no analysis of heterogeneity | Potential factual misreading; inspect the original passages before judging it an error |

If G2 recovers this relationship more often than G1 while maintaining scientific validity, that supports the value of the structured generation procedure. If R1 improves recognition over R0, structured reading helps assessment. If neither occurs, the null remains informative. None of these outcomes is assumed in advance.

## 8 Connect generation and review without overstating causality

For each submitted proposal or contribution, retain its excess generation-omission estimate and its review recognition/appraisal measurements. Ask whether features difficult to recover through generation are also less frequently recognized or accurately assessed. Adjust or stratify for scientific field, call, document length, information requirements, and independently assessed clarity where feasible. This association does not prove a shared internal mechanism.

Use human reviews to distinguish originality praised with feasibility concerns, originality disputed, ordinary but feasible plans, and unsupported departures. Use actual awards as institutional outcomes, not a validity label. Human scores helped determine those awards, so stronger agreement with funding is not independent evidence of superior human accuracy.

For completed decisions, first report within-call funding rates across continuous peripherality and prespecified review-appraisal categories. A secondary association model can include call effects, measured peripherality, and human-review assessments of originality and feasibility. Report models with and without review variables because reviews are part of the selection process, not ordinary pretreatment controls. Use only confirmed available covariates, include the sampling design if working with the review subsample, and separate calls without within-call outcome variation. This analysis asks which kinds of departures the institution funds, not whether AI would have caused different awards. Inspect both funded and unfunded edge cases; do not define important ideas only by acceptance.

The two main experiments support linked evidence about generation and assessment. They do not demonstrate that AI selects its own generated proposals over human proposals or that the two effects compound in a funding pipeline. That stronger claim needs contemporary human and AI evaluations of both origins, under comparable information and selection rules.

## 9 Optional diagnostic experiment

On approximately 30–40 well-understood proposals, commission expert-checked variants: one stylistic paraphrase preserving the scientific contribution, and one minimal substantive change to the hypothesis or question–approach connection. Ensure each version remains coherent and scientifically interpretable. Randomize AI review assignments with no access to other versions.

The outcome is whether review recognition and reasoning track the scientific change while remaining reasonably stable under paraphrase. Do not assume that removing a sentence changes only one concept; experts must check downstream consistency. The randomized contrast identifies effects of the textual variants on the tested AI reviewers, not the causal effect of automating agency decisions.

A smaller diagnostic can supply an expert contribution map to an AI reviewer. This deliberately cues the contribution, so it is not the main independent-recognition condition. Improved appraisal under that cue helps distinguish failure to locate the idea from failure to reason about it.

If the main generation finding persists, a useful generation stress test is portfolio-aware search on a prespecified subset: each successive generation can see the previous generated scientific plans and is explicitly asked to explore a coherent alternative. It still receives no held-out human proposal. Match the overall token/search budget against an independent-generation condition, preserve all rejected candidates, and analyze the generated collection as the unit. This tests a stronger diversity strategy while acknowledging dependent outputs; the principal three conditions do not exhaust plausible prompting methods.

## 10 Analysis and reporting rules

- Estimate paired effects within calls. Report model-specific results and a prespecified equal-model summary; three selected models do not constitute a random sample of all AI systems.
- Use call or related-call-family clustering for generation uncertainty. For review analyses, retain proposal pairing and reviewer dependence where identifiers allow it. Resampling candidates or repeating partitions does not create independent calls or proposals.
- Predefine the principal generation contrast, the edge interaction, and the review-recognition contrast; treat detailed novelty categories and moderator searches as secondary and account for multiplicity.
- Distinguish equal-output comparisons from equal-cost comparisons. Report technical failures, invalid science, missing inputs, duplicates, and intermediate candidate counts.
- Inspect both raw scientific text and audited representations. A shared normalizer can erase meaningful differences from both sides. Annotation uncertainty and sensitivity of match thresholds belong in the result, not only an appendix.
- Model and prompt interventions are randomized within the experimental setting. Historical human versus AI contrasts remain conditional on unequal expertise and potentially different information histories.
- Estimate LLM-associated writing modification and linguistic trends separately. Calibrate on historical texts and synthetic edits, avoid classifying individual applicants as certainly AI-assisted, and do not interpret temporal correlations as adoption effects. This is a supporting characterization of the archive.

## First deliverables

An initial end-to-end pilot can use three development calls, two model versions, three generation conditions, and five outputs per condition: 90 final narratives. Reviewing six submitted targets per call, with two models, three review requests per model, and both review strategies produces 216 final reviews. These small counts test the workflow and annotation burden; they cannot establish cross-field effects. Select pilot calls for scientific interpretability and usable records, then use the broader development sample to check transfer before freezing the confirmation design.

Before scaling, produce a checked archive inventory; checked call records for development calls; an annotation guide with source-grounded examples; an expert-adjudicated development set; fixed G0–G2 and R0–R1 procedures; pilot cost and failure estimates; and a frozen analysis plan with held-out call families.

The first empirical checkpoint is whether scientific contributions can be extracted and matched reliably, particularly at the proposed edges. The second is whether the information and generation interventions change coverage. The third is whether review recognition and reasoning engage those same contributions. These checkpoints determine what the expanded introduction can eventually state as a finding.
