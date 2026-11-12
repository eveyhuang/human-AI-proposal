# Double compression feedback by concern

This compilation groups the feedback by the concern it raises while retaining each reviewer’s original wording, including typos, proposed rewrites, praise, and repeated recommendations. The recurring concerns are clearer explanations of diversity and results, stronger prompting comparisons, additional quality and scaling analyses, qualified statistical claims, transparent data and methods, and engagement with related literature.

## Sources and location conventions

- **Word draft:** `human vs AI draft-JMO+BUcomments.docx` — all 40 comments: 19 by Brian Uzzi and 21 by Julio M Ottino. No tracked insertions or deletions were present. Eight explicit editorial notes/placeholders in ordinary body text are also included, without assigning an author.
- **Matt:** `matt_feedback.md` — all 16 nonblank text blocks, including 12 numbered requests, two opening paragraphs, and two short labels.
- **Automated review:** `review-doublecompress-2026-09-03.md` — all 87 nonheading text blocks. Matt describes an attached automated review; this file itself does not identify an individual reviewer or model. Its comments are not attributed to Matt.
- The `.~man vs AI draft-JMO+BUcomments.docx` file is a Word lock file, not another draft. The Pangram report mentioned by Matt and an SI document are not present in this folder.

**Locations:** Word entries give the actual section and anchor plus a document paragraph number (counting all `w:p` elements, including empty paragraphs). These are paragraph locators, not page numbers. Standalone feedback gives original source line numbers and a manuscript section mapping; that mapping is inferred unless the reviewer names the section/figure. Page numbers have not been inferred. The automated review sometimes refers to an earlier version; its wording is retained even when the current draft differs. In particular, Matt’s “Fig 3C” corresponds to the unmatched-idea inset called Fig. 3B in the current caption.

**Reading the entries:** W = Word comment, M = Matt, R = automated review, B = draft-body editorial note. Each entry appears once under its primary concern; compound comments are kept intact. Blockquotes reproduce source wording. Labels and location descriptions outside blockquotes are organizational additions. See [the reference list](recommended_references.md) for citation details and unresolved leads.

## Areas at a glance

| Area | Entries | Main concerns |
|---|---:|---|
| [Writing and structure](#writing-and-structure) | 30 | Simplify prose; define the argument earlier; reorganize Methods and SI; strengthen opening and synthesis |
| [Definitions and measurement](#definitions-and-measurement) | 12 | Explain distinct ideas, Vendi, spread, near-clones, MeSH, and embedding validity |
| [Methods and prompting](#methods-and-prompting) | 13 | Strengthen diversity prompts; report personas, context, temperature, and normalization; test asymmetries |
| [Analysis and additional experiments](#analysis-and-additional-experiments) | 8 | Count unique ideas and overlaps; assess scaling, quality, human edges, geometry, and criticism |
| [Statistical interpretation and limitations](#statistical-interpretation-and-limitations) | 18 | Qualify null results and generalizability; clarify AUC, power, multiple testing, and prespecification |
| [Data and reproducibility](#data-and-reproducibility) | 13 | Describe corpus, access, years, people, review procedures, SI, code, and derived data |
| [Literature and contribution](#literature-and-contribution) | 39 | Differentiate prior art; add automated-science/review, diversity, and collective-judgment references |
| [Figures and captions](#figures-and-captions) | 3 | Make captions concise and self-contained; clarify figure mappings |
| [Venue and audience](#venue-and-audience) | 7 | Resolve venue assumptions; align framing and audience |
| [Source context](#source-context) | 8 | Retain source labels, severity labels, and search metadata for completeness |

## Differences to reconcile

- **Venue:** Brian’s W38 says Nature and Science first; the automated review assumes PNAS. Its format and length advice is therefore venue-dependent.
- **Captions:** Brian’s W17 asks captions to tell the whole story, including methods and interpretation; R36/R84 asks for much shorter captions and moving mechanics to Methods/SI.
- **Prompting:** Matt’s M09/M12 requests stronger diversity-inducing conditions; R48/R51/R73/R74 questions context and decoding confounds. Preserve these alongside the draft’s claim that prompting does not remove compression.
- **Data dates:** M11 and R87 request years; the current Abstract says “2022 and late 2023,” while Corpus still says two separate years. The feedback remains useful for consistent reporting.
- **Literature accuracy:** The bibliography separates confirmed identities from incomplete leads and flags the Ashkinaze interpretation and “Li, Li & Tan” attribution. Original review text below is unchanged.

## Writing and structure

### W01 Julio M Ottino

**Referenced location:** Abstract.

**Source:** Word comment ID 1; document paragraph 4.

**Exact draft anchor:**

> Persona conditioning

**Original feedback:**

> Make stand out more? Italics? 

### W03 Julio M Ottino

**Referenced location:** Introduction, paragraph 1.

**Source:** Word comment ID 3; document paragraph 8.

**Exact draft anchor:**

> Scientific grants link new ideas to the resources needed to pursue them.  While grants are a gateway to resources that support research, grant writing is one of a scientist’s most time-consuming efforts.  Annually, scientists spend 66 of their 260 working days on funding acquisition. The coveted RO1 grant (a.k.a. the “tenure award” grant), for example, typically consumes millions of hours of researchers’ and reviewers’ time each year (5, 6).   Grant review is a two-stage process of investigators generating candidate ideas, and peer reviewers select which ideas are novel, feasible, and worth funding.

**Original feedback:**

> Paragraph 1

### W04 Brian Uzzi

**Referenced location:** Introduction, paragraph 1.

**Source:** Word comment ID 4; document paragraph 8.

**Exact draft anchor:**

> Scientific grants link new ideas to the resources needed to pursue them.  While grants are a gateway to resources that support research, grant writing is one of a scientist’s most time-consuming efforts.  Annually, scientists spend 66 of their 260 working days on funding acquisition. The coveted RO1 grant (a.k.a. the “tenure award” grant), for example, typically consumes millions of hours of researchers’ and reviewers’ time each year (5, 6).   Grant review is a two-stage process of investigators generating candidate ideas, and peer reviewers select which ideas are novel, feasible, and worth funding.

**Original feedback:**

> Modify language and tighten to this article.  This is a crib of ideas from the Pword paper.

### W07 Julio M Ottino

**Referenced location:** Introduction, final paragraph.

**Source:** Word comment ID 7; document paragraph 13.

**Exact draft anchor:**

> the NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences (NCEMS), 

**Original feedback:**

> Rewrite? CAREER awards...does this refer to NSF, Faculty Early Career Development? Or awards in general?

### W08 Brian Uzzi

**Referenced location:** Introduction, final paragraph.

**Source:** Word comment ID 8; document paragraph 13.

**Exact draft anchor:**

> Maybe add this overview of findings here if it can be condensed.

**Original feedback:**

> 
> AI reduces diversity at both stages, the two effects differ, and prompting for more diversity removes neither. In generation, AI proposes fewer distinct ideas, drawn from the same topics and the same region of idea space as human proposals rather than a separate one, and it reproduces the dense core of human ideas while under-representing their distinctive edges. In review, each AI review sits close to the human reviews, yet the AI reviews of a proposal resemble one another and their scores barely differ, whereas human reviews of the same proposal diverge. Prompting for more diversity changes the wording but not the ideas or judgments. We therefore argue that AI for science should be evaluated by its effect on the range of ideas and judgments across proposals and reviews, not only by the quality of individual ones, and we show that better prompting does not remove the effect.

### W11 Brian Uzzi

**Referenced location:** Blank paragraph immediately before Fig. 1 (empty comment anchor).

**Source:** Word comment ID 11; document paragraph 21.

**Exact draft anchor:**

*No selected text; anchored to a blank paragraph before Fig. 1.*

**Original feedback:**

> Evey this is methods

### W13 Brian Uzzi

**Referenced location:** Methods overview, four diversity facets.

**Source:** Word comment ID 13; document paragraph 24.

**Exact draft anchor:**

> We measured variability through four facets

**Original feedback:**

> Yes, this needs to be stated above but in a very concise way.  This much detail needs to go in the methods section.

### W16 Julio M Ottino

**Referenced location:** Result B heading.

**Source:** Word comment ID 16; document paragraph 31.

**Exact draft anchor:**

> edges

**Original feedback:**

> Or “AI reproduces the core, misses the edges or Humans capture AI, AI does not capture humans”?

### W22 Brian Uzzi

**Referenced location:** AI gate-keeping compresses idea selection / Result C, Low spread and richness but high coverage.

**Source:** Word comment ID 22; document paragraph 42.

**Exact draft anchor:**

> the floor the exact paired test can express at this sample size; persona is similar (δ = −0.74).  At baseline the pattern holds for Claude and GPT (δ = −0.74 to −0.91), but Gemini sits at parity (δ = +0.04, not significant), which dilutes the pooled contrast to marginal (δ ≈ −0.3 to −0.4, P = 0.07 to 0.09).

**Original feedback:**

> Good results but it needs to be made simpler and setup before you get to the results.  What is the measure and why is it important.  This is a good time remind the readers about double compression.  Ideas are narrowed in the generative stage and then in the gate-keeping stage.  

### W26 Julio M Ottino

**Referenced location:** Discussion, opening paragraph.

**Source:** Word comment ID 26; document paragraph 53.

**Exact draft anchor:**

> Both stages compressed, but in different ways

**Original feedback:**

> I understand what is trying to be said, but...better phrasing?

### W28 Julio M Ottino

**Referenced location:** Discussion, generation versus review asymmetry.

**Source:** Word comment ID 28; document paragraph 55.

**Exact draft anchor:**

> The asymmetry matters more than the general conclusion that AI is less diverse because the two losses have different consequences

**Original feedback:**

> This is not clear

### W32 Julio M Ottino

**Referenced location:** Discussion, limitations.

**Source:** Word comment ID 32; document paragraph 63.

**Exact draft anchor:**

> Several limitations bound these conclusions. 

**Original feedback:**

> Other ways to phrase this? For example These conclusions are subject to several limitations / Several factors limit the generalizability of these conclusions  / These conclusions are inherently limited by several factors.

### W38 Brian Uzzi

**Referenced location:** Materials and methods, Style normalization through Data, Materials, and Software Availability.

**Source:** Word comment ID 38; document paragraph 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85.

**Exact draft anchor:**

> Style normalization. Because differences in writing style can make two texts appear dissimilar when their content is the same, every proposal and review, human and AI, was rewritten into a single neutral format and style by Gemini before embedding; this style-normalized text (the *rephrased* branch) is primary throughout. The unedited text (the original branch) was analyzed in parallel and is reported as a robustness check (SI Appendix). The gap between the two branches is itself a measurement to test whether an effect present on both lives in the ideas, whereas an effect present only on raw text lives in the prose.Embedding and distance. Each document was embedded with BioLinkBERT-large, a biomedical language model, using mean pooling followed by L2 normalization, yielding one 1,024-dimensional vector per document; dissimilarity is cosine distance throughout. For the field analysis of reviews, the strengths and weakness sections were embedded separately (rephrased branch only).Diversity facets. We decomposed set diversity into four facets, each posing a different question of a set of proposals (or of a review panel). Spread is measured by the mean pairwise cosine distance within a set (CITE). Richness is measured by the Vendi score at order 1, the effective number of distinct items implied by the set's similarity structure (CITE). Evenness is the excess close-neighbor mass relative to a same-size random draw from the pooled items, positive values indicating near-duplicate clumping and negative values indicating more regular spacing than chance (CITE). Coverage is measured two ways: geometrically, as the fraction of human items with an AI item in their local neighborhood, benchmarked against how well one random half of the human set covers the other; and by literature region (below). To confirm that each facet reflects the data rather than one formula, every facet was additionally computed with several alternative estimators (for example, spread six ways, coverage two ways) for robustness, which agree with each other(SI Appendix).Literature grounding. To test whether AI engages in the same areas of biomedical science, we assembled a reference corpus of approximately 39,500 PubMed abstracts retrieved with search terms taken from the call, embedded them in the same space, and clustered them into 12 topic regions with BERTopic (the outlier bin was dropped). Each proposal was assigned to its nearest region and to its 10 nearest abstracts, from which we counted the literature regions engaged and the unique MeSH subject headings touched. Treating the regions as categories, we report the categorical inverse-Simpson effective number of regions occupied, which captures how evenly a set spreads across the literature rather than how many regions it reaches.Core versus edge. To ask whether the human proposals AI fails to reproduce are specifically the distinctive ones, we measured, for each of the 23 human proposals, its peripherality in human idea space using human-to-human distances only (distance from the human centroid, mean distance to its three nearest human neighbors, and local density within the human 90th-percentile nearest-neighbor distance) and, separately, its miss-rate: the fraction of equal-sized (n = 23) AI pools, across conditions and subsamples, whose nearest proposal to that human idea falls beyond the same 90th-percentile yardstick. Peripherality is defined from human geometry alone and miss-rate from human-to-AI distances, so the two share no inputs. We summarized their relationship with Spearman correlation and, as a quality guard, tested whether miss-rate was associated with the program's funding decision or ranking (Mann-Whitney and Spearman; SI Appendix).Gate-keeping design. Because reviews of different proposals differ for reasons unrelated to reviewer independence, every review facet is computed within a proposal: the 2 to 5 human reviews of a proposal against equal-sized panels drawn from that proposal's AI reviews, matched to the human panel size for that proposal. The spread, richness, evenness, and coverage measures are as above, with two review-specific benchmarks stated on every figure: panel coverage is judged against leave-one-out self-coverage (how well each human review is covered by the rest of its own panel, 0.83 on average), and panel clumping against random same-size draws from that condition's review pool. The full battery was run three times over a field axis, the whole review, its strengths section alone, and its weakness section alone (rephrased branch only), to locate where the compression concentrates.Score and decision analyses. Using the reviewers' numeric overall scores and the program's real outcomes, we compared human and AI panels on within-panel score spread, on rank agreement with the funding ranking as a function of panel size, and on the separation of funded from not-funded proposals by panel mean score (area under the ROC curve). Each AUC carries a stratified bootstrap 95% confidence interval and a two-sided label-permutation p-value (10,000 draws each). Because human scores cover only part of the set and the funding ranking was itself produced by human review, the human-versus-AI contrast is exploratory and is reported as such; a size- and proposal-matched decomposition, which leaves the AI-side conclusion unchanged, is given in SI Appendix.Wording controls. To confirm that the semantic results are not an artifact of the embedding model, we measured two text-only quantities that never touch the embedding, distinct-2gram (the share of unique adjacent word pairs) and self-BLEU (self-repetition), for humans and for each model on both text branches.Statistical inference. Every comparison is made at matched sample size. Generation contrasts compare whole sets at 23 versus 23; pooled AI is the three models' 69 proposals subsampled to 23 without replacement, averaged over 1,000 draws, and reported as an AI-to-human ratio in which 1.0 is human parity. Group differences use label-permutation tests (10,000 shuffles) and confidence intervals use the jackknife; we never resample with replacement, which would inject duplicates into metrics that are sensitive to them. Gate-keeping is a paired design and is reported as Cliff's δ, the consistency with which the AI panel falls below the human panel across the 23 proposals, with p-values from the exact paired Wilcoxon test. Five comparisons were designated primary in advance, one headline metric for each of the four facets (spread, richness, evenness, and geometric coverage) plus a whole-cloud displacement check, and are read at face value; all other p-values are corrected for multiple comparisons with the Benjamini-Hochberg false-discovery-rate procedure applied within each task, text branch, and field stratum. Displacement between two clouds was tested with the kernel two-sample statistic MMD² against a shuffle null and cross-checked with an optimal-transport (Wasserstein) distance.Data, Materials, and Software Availability. The proposal and review texts are confidential to the NCEMS competition and cannot be released publicly; de-identified derived data (embeddings and per-item facet values) and access terms are described in SI Appendix and are available from the authors under agreement with the program [repository/DOI]. Analysis code for the facet pipeline is available at [repository]. The embedding model, BioLinkBERT-large, is publicly available [CITE].

**Original feedback:**

> This is a lot of detail for the M&M section.  The trick here is to give the reader enough info without overwhemling and distracting them.  So, we need to decide what we want to put in the SI.  Also, since we are going to try Nature and Science first, this PNAS format won’t work for those submissions.  These ideas must go in theSI

### W39 Julio M Ottino

**Referenced location:** Materials and methods, Literature grounding.

**Source:** Word comment ID 39; document paragraph 73.

**Exact draft anchor:**

> the

**Original feedback:**

> in? with?

### M01 Matt (name supplied by filename)

**Referenced location:** Whole manuscript; literature engagement in Introduction and Discussion.

**Source:** matt_feedback.md, lines 1–1.

**Original feedback:**

> I read the NCEMS draft. I think it's heading in the right direction. From a writing perspective, the two biggest problems I currently see is (1) it looks like AI-writing (and the Pangram report puts it at 78% AI writing) (2) it lacks engagement with the emerging field of papers on automated science and automated review. I've attached the PanGram report and another automated review showing the key citations to add (including Dashun's latest PNAS paper) plus rhetorical approaches you may want to consider. Fwiw, I think the AI-like writing obscures the analysis and it's not as sharp, simple, and straightforward as the results could be.

### R34 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction opening.

**Source:** review-doublecompress-2026-09-03.md, lines 67–67; 2b. Venue-specific analysis.

**Original feedback:**

> - **Introduction tone**: matches PNAS (problem → tension → "Here/We study") but the current opening paragraph is flatter than the venue norm; PNAS intros of this type open with a sharper real-world development (see lab-voice notes).

### R35 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction final paragraph in reviewed version.

**Source:** review-doublecompress-2026-09-03.md, lines 68–68; 2b. Venue-specific analysis.

**Original feedback:**

> - **Contribution articulation**: PNAS wants the narrative form you use; the final intro paragraph ("We therefore argue…") is appropriately synthetic.

### R38 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Abstract and Significance statement.

**Source:** review-doublecompress-2026-09-03.md, lines 71–71; 2b. Venue-specific analysis.

**Original feedback:**

> - **Abstract/Significance**: PNAS caps abstracts at 250 words and Significance at 120 — both are at or over the limit; trim.

### R39 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction opening.

**Source:** review-doublecompress-2026-09-03.md, lines 75–75; 2c. Lab voice analysis.

**Original feedback:**

> - **Opening puzzle/tension**: ✗ weakest part of the draft. "Scientific grants are the primary mechanism that links new ideas to the resources needed to pursue them" is a textbook opener, not a puzzle. No vivid concrete example, no signature "remains an open question." A ready-made vignette exists in the current news: *in September 2025 the NIH declared substantially AI-developed applications a violation of its originality expectations, while the same year a Stanford conference accepted 48 papers generated and reviewed entirely by AI, scored by averaging three models' judgments* — that's the tension (institutions simultaneously banning and institutionalizing AI at both stages) in two sentences, and both facts are load-bearing citations anyway.

### R40 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, study pivot.

**Source:** review-doublecompress-2026-09-03.md, lines 76–76; 2c. Lab voice analysis.

**Original feedback:**

> - **Narrowing pivot**: ✓ "We study double compression with data that carries the stakes and expertise of real grant funding" is a clean lab-style pivot.

### R41 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Abstract.

**Source:** review-doublecompress-2026-09-03.md, lines 77–77; 2c. Lab voice analysis.

**Original feedback:**

> - **Empirical specificity in abstract**: ✓ strong — 23 proposals, three models, three conditions, effect ranges all present.

### R42 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction and Results, model exceptions.

**Source:** review-doublecompress-2026-09-03.md, lines 78–78; 2c. Lab voice analysis.

**Original feedback:**

> - **Nuance, hedged with "but/however"**: ✓ excellent throughout ("AlphaFold transformed… Yet this efficiency may carry a collective cost"; Gemini exceptions reported honestly).

### R43 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion opening or end of Results.

**Source:** review-doublecompress-2026-09-03.md, lines 79–79; 2c. Lab voice analysis.

**Original feedback:**

> - **"Together, these results…" synthesis**: ✗ absent. The discussion opens with "We compared…" and never lands the synthesizing sentence. Add one at the start of the discussion or end of results: "Together, these results show that AI narrows scientific search twice: …"

### R44 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 80–80; 2c. Lab voice analysis.

**Original feedback:**

> - **Limitations stated plainly**: ✓ the limitations paragraph is genuinely good — direct, specific, non-perfunctory.

### R45 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction opening and Discussion synthesis.

**Source:** review-doublecompress-2026-09-03.md, lines 81–81; 2c. Lab voice analysis.

**Original feedback:**

> - Divergence verdict: the voice is 80% there; the opening and the missing "Together" move are the two real gaps.

### R67 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction opening.

**Source:** review-doublecompress-2026-09-03.md, lines 137–137; Opportunities (by impact).

**Original feedback:**

> 2. **Rewrite the opening with the NIH-ban / Agents4Science tension** (see 2c) — it supplies the lab-signature vivid opening and two needed citations in one move.

### R68 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion opening.

**Source:** review-doublecompress-2026-09-03.md, lines 138–138; Opportunities (by impact).

**Original feedback:**

> 3. **Add the "Together, these results…" synthesis sentence** at the discussion's start.

### R83 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction and Methods; terminology throughout.

**Source:** review-doublecompress-2026-09-03.md, lines 161–161; Problems.

**Original feedback:**

> - Typos: "two seperate years," "indepdently," "AI, especially, Large language models are now entering…" (garbled), "gate-keeping"/"gatekeeping" inconsistency, missing period after "already produced" in Methods.

### R85 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Abstract and Significance statement.

**Source:** review-doublecompress-2026-09-03.md, lines 163–163; Problems.

**Original feedback:**

> - Abstract ≈ over PNAS's 250-word cap; Significance likely over 120 — trim both. In the Significance statement, "biomedical competition" vs. "molecular and cellular bioscience" — pick one descriptor and use it everywhere.

### B04 Unattributed editorial note in draft body

**Referenced location:** Introduction, final paragraph.

**Source:** Word draft body, paragraph 13; ordinary text, not a Word comment.

**Original feedback:**

> Maybe add this overview of findings here if it can be condensed.

## Definitions and measurement

### W02 Julio M Ottino

**Referenced location:** Significance statement.

**Source:** Word comment ID 2; document paragraph 5.

**Exact draft anchor:**

> distinct

**Original feedback:**

> Not for here, but hint how you will quantify “distinct”?

### W10 Brian Uzzi

**Referenced location:** Methods overview, prompting conditions.

**Source:** Word comment ID 10; document paragraph 18.

**Exact draft anchor:**

> whether AI panels review a given proposal as diversely as human panels.th

**Original feedback:**

> Evey, I don’t understand this.

### W12 Julio M Ottino

**Referenced location:** Methods overview, four diversity facets.

**Source:** Word comment ID 12; document paragraph 24.

**Exact draft anchor:**

> We measured variability through four facets

**Original feedback:**

> This is key...should be foreshowed earlier

### W14 Julio M Ottino

**Referenced location:** Methods overview, four diversity facets.

**Source:** Word comment ID 14; document paragraph 24.

**Exact draft anchor:**

> spread

**Original feedback:**

> Fist time “diversity” is defined?

### W15 Brian Uzzi

**Referenced location:** Generation results / Result A, Evenness.

**Source:** Word comment ID 15; document paragraph 29.

**Exact draft anchor:**

> near-clone duplicates

**Original feedback:**

> Need to define this clearly.

### W18 Julio M Ottino

**Referenced location:** Result B, Topical coverage.

**Source:** Word comment ID 18; document paragraph 34.

**Exact draft anchor:**

> MeSH 

**Original feedback:**

> Glossary needed?

### W19 Brian Uzzi

**Referenced location:** Result B, Topical coverage.

**Source:** Word comment ID 19; document paragraph 34.

**Exact draft anchor:**

> The generation narrowing (Result A) is therefore within topics, not avoidance of them. Occupancy of those topics is uneven, however. Treating each region as a category, the inverse-Simpson effective number of regions occupied is 4.94 for human proposals against 3.1 to 3.9 for pooled AI at matched sample size (ratios 0.78, 0.62, 0.73), so AI spreads across fewer regions in every condition, most severely under one-at-a-time (Fig. 3A).

**Original feedback:**

> Unclear but sounds important less discuss.

### W30 Julio M Ottino

**Referenced location:** Discussion, implications beyond grant review.

**Source:** Word comment ID 30; document paragraph 61.

**Exact draft anchor:**

> Automation in these settings is usually evaluated one output or one decision at a time, yet neither the range of candidates considered nor the independence of the judgments applied to them is a property of any single output

**Original feedback:**

> Not sure I get the “property of any single output”

### M05 Matt (name supplied by filename)

**Referenced location:** Methods overview / Diversity facets; Result A, richness.

**Source:** matt_feedback.md, lines 8–8.

**Original feedback:**

> 2. Richness is measured via Vendi, which is implied for set's similarity structure but it's opaque... can you offer a concrete example showing how a proposal is transformed into a richness score? This feels like it's not grounded and the analysis is AI-generated (I'm not claiming it is, but that's my feeling as a reader)

### M15 Matt (name supplied by filename)

**Referenced location:** Materials and methods, Embedding and distance.

**Source:** matt_feedback.md, lines 22–22.

**Original feedback:**

> 5. Is BioLinkBERT the right model here? Should we be using a commercial embedding or BioClinicalModernBert

### R46 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result A, matched-size spread and richness.

**Source:** review-doublecompress-2026-09-03.md, lines 85–85; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> The lynchpin is **Result A's matched-size diversity ratio** (pooled AI holds 64–70% of human spread and 66–75% of human richness, significant in all conditions, surviving persona and style normalization). If that ratio were an artifact, Results B–D would be reinterpretations of noise.

### B06 Unattributed editorial note in draft body

**Referenced location:** Generation results / Result A, Evenness.

**Source:** Word draft body, paragraph 29; ordinary text, not a Word comment.

**Original feedback:**

> Using our measure ________, where positive values mean clumping and vice versa for negative numbers

## Methods and prompting

### W00 Brian Uzzi

**Referenced location:** Abstract.

**Source:** Word comment ID 0; document paragraph 4.

**Exact draft anchor:**

> Finally, having LLMs  Persona conditioning, the strongest documented intervention against model homogeneity, removes the difference in wording but not the difference in ideas or judgments.

**Original feedback:**

> I need to learn more about this finding.

### W37 Julio M Ottino

**Referenced location:** Materials and methods, AI generation and review.

**Source:** Word comment ID 37; document paragraph 67.

**Exact draft anchor:**

> Holding the call, the proposals under review, and the criteria fixed across humans and models leaves the source of the text as the only varying factor.

**Original feedback:**

> Rewrite?

### M09 Matt (name supplied by filename)

**Referenced location:** Materials and methods, AI generation and review / Generation conditions; Result C.

**Source:** matt_feedback.md, lines 12–12.

**Original feedback:**

> 6. What is the reviewer prompt? This matters a ton for the expected diversity of the response. For example, what if you had AI personas focus only only (a) novelty (b) feasibility (c) some weird particularity (d) engagement with the most hyped topics (e) generalizability (f) clinical relevant (g) mechanistic insight (h) reproducibility (i) risk-benefit profile (j) validity of measurement then if each persona focused on those things independently we should expect diversity. My point here is the outcome depends on how you choose to generate reviews with AI, so you need to steelman this by giving the most diversity expecting prompt you can come up with

### M12 Matt (name supplied by filename)

**Referenced location:** Methods overview; Materials and methods, Generation conditions.

**Source:** matt_feedback.md, lines 19–19.

**Original feedback:**

> 2. Can you give more details on the one-at-a-time condition? Is it like high temperature? I think this isn't as much of a steelman as giving a generated proposal and saying be different, then givngn 2 generated proposals and saying be different all the way up to 23. Can you run that?

### M13 Matt (name supplied by filename)

**Referenced location:** Materials and methods, Generation conditions / persona.

**Source:** matt_feedback.md, lines 20–20.

**Original feedback:**

> 3. More details on persona conditions -- how are the 5 titles and abstracts chosen?

### M14 Matt (name supplied by filename)

**Referenced location:** Materials and methods, Style normalization.

**Source:** matt_feedback.md, lines 21–21.

**Original feedback:**

> 4. What's the prompt for style normalization? That should be included here for transparency. When style normalizing how many characters are these proposals?

### R47 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, resampling and robustness.

**Source:** review-doublecompress-2026-09-03.md, lines 87–87; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> - **Rigor**: The design is unusually careful — matched sample sizes, 1,000 subsample draws, jackknife CIs, label-permutation tests, no resampling with replacement, raw-text robustness branch, and persona as a prespecified stress test. This is the best-controlled comparison of its kind I've seen.

### R48 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, Generation conditions; Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 88–88; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> - **The central confound — input-information asymmetry**: Human applicants bring labs, preliminary data, collaborators, funding history, and career incentives to differentiate (the draft itself notes "applicants have every reason to differentiate… a model asked for 23 proposals in a single pass has none" — for baseline, but the deeper asymmetry applies to *all* conditions). The persona condition conditions on 5 titles+abstracts — a thin proxy for a scientist's generative context. A hostile reviewer will say the paper measures what models do with *impoverished input*, not a property of models. The honest defense: (a) one-at-a-time removes the single-pass incentive problem and compression persists; (b) the claim should be explicitly scoped to "AI as currently deployable from a call + public record," which is exactly how automated pipelines would run. Say this in limitations or reframe the claim; don't leave it for reviewers.

### R49 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, human versus AI task context; Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 89–89; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> - **Ecological validity**: high on the human side (real stakes, real experts — the paper's whole selling point) but note the AI side is zero-stakes by construction; that asymmetry is part of what's being measured and should be named.

### R51 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result C; Methods, decoding parameters; SI.

**Source:** review-doublecompress-2026-09-03.md, lines 91–91; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> - **Result C's convergence has a rigor gap of its own**: five reviews sampled from one model at fixed decoding parameters *should* correlate; δ = −0.91 may partly measure temperature, not judgment. Decoding parameters are relegated to SI. Report temperature in the main text and, ideally, add a high-temperature robustness condition — otherwise a reviewer can dismiss Result C as "sampling variance is smaller than reviewer variance, as expected."

### R73 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, Generation conditions; Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 147–147; Problems.

**Original feedback:**

> - **C2 — Input-information asymmetry is treated as a model property.** Resolution: scope the claim ("AI as deployable from the call and public record"), strengthen the limitation, or add a context-enriched condition; at minimum, one honest paragraph.

### R74 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result C; Methods, decoding parameters; SI.

**Source:** review-doublecompress-2026-09-03.md, lines 148–148; Problems.

**Original feedback:**

> - **C3 — Review convergence may be a decoding artifact.** Resolution: decoding parameters in main text; temperature-sensitivity robustness (even for one model) in SI.

### R76 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, Style normalization; robustness analysis.

**Source:** review-doublecompress-2026-09-03.md, lines 152–152; Problems.

**Original feedback:**

> - **M1 — Gemini is both a studied model and the style normalizer.** Normalizing all text through one of the three systems under evaluation risks importing its homogeneity into the primary branch (and Gemini is the model that behaves differently in several results). Resolution: normalize with a held-out model, or show facet ratios are invariant to the choice of normalizer.

## Analysis and additional experiments

### W20 Brian Uzzi

**Referenced location:** Result B, Geometry.

**Source:** Word comment ID 20; document paragraph 35.

**Exact draft anchor:**

> Geometry. The two sets are not separated. A two-sample distance test cannot distinguish them in any condition (MMD² = 0.037, 0.062, 0.032, all not significant), benchmarked against a calibration in which two halves of the human sample differ by approximately 0, and an independent optimal-transport distance agrees. Gemini is the one partial exception, significantly displaced under one-at-a-time and persona, whereas GPT is essentially undisplaced (persona MMD² = 0.000). The AI cloud is thus concentric with the human cloud and shares its radial extent; what differs is how evenly it fills that space (Result A).

**Original feedback:**

> Do we need this measure if it is ns?  Maybe drop if unnecessary for less -is-more reasons.

### W24 Brian Uzzi

**Referenced location:** Result C, Compression is concentrated in the criticism.

**Source:** Word comment ID 24; document paragraph 44.

**Exact draft anchor:**

> Compression is concentrated in the criticism. The compression effect is strongest when we split each review into its strengths and its weaknesses and compare them separately (Fig. 4B). Weakness panels compress at the design ceiling (δ = −0.91 for both spread and richness, narrower for 22 of 23 proposals), while strengths compress substantially less (δ = −0.57 to −0.65). Weaknesses are also where human panels have the most variability to lose: human within-panel spread is 0.084 for weaknesses against 0.069 for strengths and 0.044 for whole reviews.  The section that carries the decision is the section AI homogenizes hardest. The generation-side signature reappears here in miniature, inside a single proposal's criticism: human weakness panels are even than chance (excess −0.006, −0.003) while pooled AI runs +0.026, and weaknesses are the only field where clumping is already significant at baseline (δ = +0.48).

**Original feedback:**

> I need you to explain this to me

### M02 Matt (name supplied by filename)

**Referenced location:** Discussion, implications beyond grant review (P61); Fig. 3A.

**Source:** matt_feedback.md, lines 3–3.

**Original feedback:**

> I really like this idea which I find central to the paper: "AI can remain within the same broad scientific domains as humans while undersampling the distinctive edges of their idea space, and AI reviewers can cover much of the semantic territory of human review while supplying less independent judgment" and I think Figure 3 A is rocking showing the human coverage is higher than AI coverage (but I do worry that this may be a sample size effect here and a different 23 human submissions would not be 4.94)

### M04 Matt (name supplied by filename)

**Referenced location:** Fig. 3C as named by Matt (bottom-right unmatched-idea inset; current caption calls this Fig. 3B inset); Result A.

**Source:** matt_feedback.md, lines 7–7.

**Original feedback:**

> 1. Fig 3C in bottom right suggests there are 4-5 human ideas with no AI match and 2 AI ideas with no human match. Likewise Result A claims: AI generated fewer distinct ideas. If you can make this claim, then I assume you can make a claim: There are X unique human ideas among the 23 proposals and Y unique AI ideas among the 23 (X among the 69) AI proposals. Likewise, there are N ideas proposed by 2 humans, 3 humans, 4 humans etc. and M ideas proposed by 2 AI, 3 AI etc.

### M06 Matt (name supplied by filename)

**Referenced location:** Result A, richness; Discussion, automation at scale.

**Source:** matt_feedback.md, lines 9–9.

**Original feedback:**

> 3. I'd like to know how number of distinct ideas (related to the Vendi score) scales with number of proposals generated? How many proposals do you have to generative to have hit the same amount of ideas as humans.

### M07 Matt (name supplied by filename)

**Referenced location:** Generation results; proposal quality comparison (new analysis).

**Source:** matt_feedback.md, lines 10–10.

**Original feedback:**

> 4. How good are AI ideas? Can we get review scores for a subset so we can compare quality?

### M08 Matt (name supplied by filename)

**Referenced location:** Result B, distinctive edges and funding/ranking.

**Source:** matt_feedback.md, lines 11–11.

**Original feedback:**

> 5. Are the distinctive human edges highly scored?

### R50 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result B, unmatched proposals and distinctive edges.

**Source:** review-doublecompress-2026-09-03.md, lines 90–90; 3. Lynchpin Evidence Analysis.

**Original feedback:**

> - **Effect size**: large and practically framed (one human proposal in five with no AI counterpart; 69% of the distinctive edge missed). Good.

## Statistical interpretation and limitations

### W21 Brian Uzzi

**Referenced location:** Result B, unmatched proposals and funding outcomes.

**Source:** Word comment ID 21; document paragraph 37.

**Exact draft anchor:**

> Those  human proposal areas unexplored by AI are statistically indistinguishable from the reproduced ones in the competition's funding and ranking (funded versus rejected miss-rate 0.20 versus 0.26, Mann-Whitney P = 0.77; all P > 0.3), so the gap is not AI skipping the ideas that human reviewers themselves rejected. Generation therefore loses territory specifically at its distinctive edges. 

**Original feedback:**

> Mixing ideas here.  Please clarify?  Generative compression vs gate-keeping compression

### W23 Brian Uzzi

**Referenced location:** Result C, panel independence.

**Source:** Word comment ID 23; document paragraph 43.

**Exact draft anchor:**

> What gate-keeping loses is not the quality of any single judgment but the independence of judgments across the panel.

**Original feedback:**

> Brilliant deduction!

### W25 Brian Uzzi

**Referenced location:** Result C, Scores from AI panel do not predict funding outcome.

**Source:** Word comment ID 25; document paragraph 45.

**Exact draft anchor:**

> Scores from AI panel do not predict funding outcome.  Human ranking and a favorable funding decisions were available fro 13 of 23 proposals, which makes strong relative conclusion exploratory.  Nevertheless, across all three conditions, AI reviewers display no detectable funding signal relative to eminent human reviewers.  On the competition's 1-to-5 scoring scale, the human panel's scores vary more across reviewers of a proposal (standard deviation 0.74) than the AI panels' scores do in any condition (0.51 at baseline, 0.34 at one-at-a-time, 0.29 at persona). AI scores also vary less across proposals than human scores (between-proposal standard deviation 0.36, 0.54, and 0.52 against 0.62).  Importantly, this suggests that AI gate-keeping compression also leaves less signal with which to separate proposals. Against the competition's actual outcomes (14 funded, 9 not), AI panel scores carry no detectable funding signal: the area under the ROC curve is 0.50, 0.47, and 0.50 across conditions (label-permutation P = 0.99, 0.84, 0.99), compared with 0.77 for the human panel. 

**Original feedback:**

> I’m guessing here aas to what you want to say.  Please review carefully.

### W27 Julio M Ottino

**Referenced location:** Discussion, opening paragraph.

**Source:** Word comment ID 27; document paragraph 53.

**Exact draft anchor:**

> A pipeline that automated both stages would therefore narrow scientific search twice: first by reducing the range of distinctive possibilities considered, and then by evaluating those possibilities with a more correlated set of judgments.

**Original feedback:**

> This is good

### W29 Julio M Ottino

**Referenced location:** Discussion, automation at scale.

**Source:** Word comment ID 29; document paragraph 59.

**Exact draft anchor:**

> Our

**Original feedback:**

> At some point defensively say our analysis based on ...limited...suggests that...rather than results show 

### W31 Julio M Ottino

**Referenced location:** Discussion, implications beyond grant review.

**Source:** Word comment ID 31; document paragraph 61.

**Exact draft anchor:**

> Our results make the distinction concrete: 

**Original feedback:**

> Strong stand...hedge?

### W33 Julio M Ottino

**Referenced location:** Discussion, limitations.

**Source:** Word comment ID 33; document paragraph 63.

**Exact draft anchor:**

> confidence intervals are wide

**Original feedback:**

> Make more precise?

### W34 Julio M Ottino

**Referenced location:** Discussion, limitations.

**Source:** Word comment ID 34; document paragraph 63.

**Exact draft anchor:**

> Finally, the study concerns one competition, one proposal format, one scientific domain, three models, and one period in a rapidly changing technology. The next questions are whether core-edge compression persists across models and domains, whether heterogeneous model ensembles or deliberately atypical conditioning can recover the missing edge, and whether reduced reviewer independence ultimately changes allocation decisions. 

**Original feedback:**

> Should this be more upfront rather than “finally…”

### R55 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Fig. 3 caption; Result C funding heading; Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 113–113; 6. Statistical Rigor.

**Original feedback:**

> - **Absence of evidence ≠ evidence of absence** — mostly exemplary ("no detectable association," "not detectably less likely," the explicit "absence of a detectable funding signal… is not evidence of a true null"). Three violations to fix: **Fig. 3 caption**: "The ideas AI misses are unrelated to the competition's funding or ranking" → "not detectably associated with"; **Results heading**: "Scores from AI panel do not predict funding outcome" → "carry no detectable funding signal" (the paragraph's own phrasing); **Discussion**: "the lack of an association" → "the lack of a detectable association" (the sentence's second half already gets it right).

### R56 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Materials and methods, Statistical inference; SI.

**Source:** review-doublecompress-2026-09-03.md, lines 114–114; 6. Statistical Rigor.

**Original feedback:**

> - **Multiple testing**: 5 prespecified primary comparisons at face value, BH within task × branch × stratum for the rest — well designed. State the *total* number of BH-corrected tests somewhere in SI.

### R57 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, limitations; Result C strengths versus weaknesses.

**Source:** review-doublecompress-2026-09-03.md, lines 115–115; 6. Statistical Rigor.

**Original feedback:**

> - **Power**: n=23 limits are acknowledged and pooling is justified; good. But the strengths-vs-weaknesses analysis is candidly flagged as a decomposition, not independent replication — keep that sentence, reviewers will respect it.

### R58 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result C AUC; Discussion limitations; Abstract.

**Source:** review-doublecompress-2026-09-03.md, lines 116–116; 6. Statistical Rigor.

**Original feedback:**

> - **No power analysis** for the AUC contrast; the paper correctly downgrades it to exploratory. Keep the human-panel comparison out of the abstract (it currently is — good).

### R59 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result B, Distinctive edges.

**Source:** review-doublecompress-2026-09-03.md, lines 117–117; 6. Statistical Rigor.

**Original feedback:**

> - **Watch**: "almost deterministically" (ρ = +0.86, n=23) overshoots; ρ = −0.99 for local density is the near-deterministic one. Attach each adverb to its statistic.

### R60 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Materials and methods, Statistical inference; Discussion, limitations.

**Source:** review-doublecompress-2026-09-03.md, lines 121–121; 7. Pre-registration.

**Original feedback:**

> Not pre-registered (no registry named). The draft claims prespecification twice ("Five comparisons were designated primary in advance"; "the prespecified ordering test") with no documentation. For confirmatory-flavored claims at PNAS this will draw a question: either produce a timestamped analysis plan (OSF, even retroactively dated honestly as an internal plan) or soften "prespecified" to "designated primary before unblinding to outcomes" and say where that designation lives. The inferential risk is real: four facets × three conditions × three models × two branches × three field strata is a large garden of forking paths, and the paper's defense is currently a sentence, not a document.

### R77 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods, Statistical inference; prespecification documentation.

**Source:** review-doublecompress-2026-09-03.md, lines 153–153; Problems.

**Original feedback:**

> - **M2 — Prespecification is claimed but undocumented** (Section 7). Resolution: post the plan or soften the language.

### R79 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Abstract; Results A–C per-model exceptions; main figures.

**Source:** review-doublecompress-2026-09-03.md, lines 155–155; Problems.

**Original feedback:**

> - **M4 — Per-model heterogeneity cuts against the pooled claim.** Gemini sits at parity on review spread at baseline and is the only displaced model in generation. The paper discloses this honestly but the abstract speaks of "AI" monolithically. Resolution: one abstract-safe hedge ("consistent across models, with one partial exception in each stage, detailed in results") or surface per-model panels in a main figure.

### R81 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Fig. 3 caption; Result C funding heading; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 159–159; Problems.

**Original feedback:**

> - Absence-of-evidence phrasing: Fig. 3 caption, Result C heading, one discussion sentence (Section 6).

### R86 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Result B, Distinctive edges.

**Source:** review-doublecompress-2026-09-03.md, lines 164–164; Problems.

**Original feedback:**

> - "Almost deterministically" → attach to the ρ = −0.99 statistic, not ρ = +0.86.

## Data and reproducibility

### W06 Julio M Ottino

**Referenced location:** Introduction, final paragraph.

**Source:** Word comment ID 6; document paragraph 13.

**Exact draft anchor:**

> the NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences (NCEMS), 

**Original feedback:**

> Say something here…”we were given access to…”

### W09 Brian Uzzi

**Referenced location:** Data, editorial placeholder.

**Source:** Word comment ID 9; document paragraph 16.

**Exact draft anchor:**

> Evey add data section.

**Original feedback:**

> This has to be a strong section.  This is a data driven process.

### W35 Brian Uzzi

**Referenced location:** Materials and methods, Corpus.

**Source:** Word comment ID 35; document paragraph 66.

**Exact draft anchor:**

> Corpus: The human corpus is the complete set of 23 proposals submitted to the inaugural competition of the NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences (NCEMS) from two separate years and two applicant cohorts, together with the 85 expert reviews they received (2 to 5 reviewers per proposal, mean 3.70) and the program's own outcomes for each proposal: a binary funding decision (14 funded, 9 not) and a numeric ranking. Reviewers also recorded an overall score on the program's 1-to-5 scale, available for 13 to 14 of the 23 proposals. The proposals, reviews, and outcomes are confidential to the program and were never publicly released, so they are absent from any model's training corpus; this is the property that lets us treat the AI outputs as generated rather than recalled. Use of the de-identified corpus was covered under [IRB xxxx; SI Appendix].

**Original feedback:**

> Should go in data section.  Because the data is so important in this paper and unique, we need to front it in the main text.  

### W36 Julio M Ottino

**Referenced location:** Materials and methods, Corpus.

**Source:** Word comment ID 36; document paragraph 66.

**Exact draft anchor:**

> : The human corpus is the complete set of 23 proposals submitted to the inaugural competition of the NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences (NCEMS) 

**Original feedback:**

> Should you say how you got access to this? Can anybody get access?

### M11 Matt (name supplied by filename)

**Referenced location:** Data; Materials and methods, Corpus.

**Source:** matt_feedback.md, lines 18–18.

**Original feedback:**

> 1. What year are the NCEMs proposals from?

### M16 Matt (name supplied by filename)

**Referenced location:** SI Appendix, referenced throughout.

**Source:** matt_feedback.md, lines 23–23.

**Original feedback:**

> 6. Is there an SI, I see it referenced but do not see it.

### R52 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Data; Materials and methods, Corpus; data availability.

**Source:** review-doublecompress-2026-09-03.md, lines 95–103; 4. Dataset Evaluation.

**Original feedback:**

> | Attribute | Details |
> |---|---|
> | Name & source | NCEMS (NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences) inaugural competition, 2 cohorts |
> | Publicly accessible? | No — confidential; de-identified derived data (embeddings, facet values) by agreement; **repository/DOI still a placeholder** |
> | N observations | 23 proposals; 85 expert reviews; +69 AI proposals; 345 AI reviews |
> | N unique individuals | Not reported — add N of distinct human applicants and reviewers |
> | Study design | Matched observational comparison with experimental prompting conditions on the AI side |
> | Demographic diversity | Not reported; at minimum report applicant institutional/geographic spread ("faculty at top universities around the world" is currently a claim without numbers) |
> | Temporal coverage | Two competition years (which years? "two seperate years" — unspecified and misspelled) |

### R53 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, corpus contribution; data availability.

**Source:** review-doublecompress-2026-09-03.md, lines 105–105; 4. Dataset Evaluation.

**Original feedback:**

> The confidentiality is the dataset's superpower (leakage-proof) and its transparency weakness; the paper handles the tradeoff about as well as possible, but the derived-data repository must actually exist at submission. Comparable corpora: Pier et al.'s 25 replicated NIH applications; Qian et al.'s 5,700 confidential proposals (observational LLM use, no reviews); no public corpus pairs confidential proposals *with their reviews* — make that uniqueness claim explicitly, it strengthens the Qian differentiation.

### R54 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Data availability; Style normalization; SI.

**Source:** review-doublecompress-2026-09-03.md, lines 109–109; 5. Reproducibility Check.

**Original feedback:**

> Code is "[repository]" and data is confidential → no reproduction attempted (per protocol, code was not inspected). **Flags**: (1) analysis code not yet public — must be at submission; (2) the de-identified derived data (embeddings + per-item facet values) would allow full reproduction of every statistic in the paper without exposing proposal text — release it, don't just describe access terms; (3) the Gemini style-normalization step is itself irreproducible unless the exact model version, prompt, and normalized outputs' embeddings are archived.

### R70 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Data, Materials, and Software Availability.

**Source:** review-doublecompress-2026-09-03.md, lines 140–140; Opportunities (by impact).

**Original feedback:**

> 5. **Release the derived-data + code repositories** — this paper's credibility rests on confidential data; maximal transparency on everything derivable is the compensating move.

### R78 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** All citation placeholders; Corpus IRB placeholder; data/code availability.

**Source:** review-doublecompress-2026-09-03.md, lines 154–154; Problems.

**Original feedback:**

> - **M3 — Every [CITE], the IRB number, and both repository placeholders are unfilled.** Gating for any submission; this review's Section 2a supplies most of the [CITE] targets.

### R87 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Data; Materials and methods, Corpus.

**Source:** review-doublecompress-2026-09-03.md, lines 165–165; Problems.

**Original feedback:**

> - Report N unique applicants, N unique reviewers, and the two competition years in Methods.

### B05 Unattributed editorial note in draft body

**Referenced location:** Data, editorial placeholder.

**Source:** Word draft body, paragraph 16; ordinary text, not a Word comment.

**Original feedback:**

> Evey add data section.  Time frame, stats on the PIs, name of NSF Competion and its ground-breaking purpose, eminence of human reviewers, length of proposals, and the human review process and ranking procedure.  Also, add data on the embedding map of molecular biology, include embedding model (e.g., glove, etc) and stats on the embeddings Nodes, path length, clustering, and construct validity.

## Literature and contribution

### W05 Brian Uzzi

**Referenced location:** Introduction, paragraph 3.

**Source:** Word comment ID 5; document paragraph 10.

**Exact draft anchor:**

> Hao et al., 2024

**Original feedback:**

> What is this citation?

### R02 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Abstract; whole manuscript contribution.

**Source:** review-doublecompress-2026-09-03.md, lines 9–9; 1. Steel Man Summary.

**Original feedback:**

> The central contribution: using 23 confidential proposals and 85 expert reviews from a real NSF bioscience competition (NCEMS) as a ground-truth corpus that cannot be in any model's training data, the paper shows that frontier LLMs compress scientific search at both stages of grant review — generating proposal sets with 25–36% fewer distinct ideas that reproduce the dense core of human idea space while missing 69% of its distinctive edge, and producing review panels whose judgments converge on one another (Cliff's δ down to −0.91) and carry no detectable funding signal — and that persona prompting, the strongest documented anti-homogenization intervention, fixes the wording but not the ideas.

### R03 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Whole manuscript; diversity facets; Results B and C; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 11–11; 1. Steel Man Summary.

**Original feedback:**

> Additional contributions: (a) a four-facet diversity decomposition (spread, richness, evenness, coverage) with style-normalization to separate idea-level from wording-level effects; (b) the core-vs-edge geometry result (distinctiveness almost deterministically predicts AI miss-rate, ρ = +0.86); (c) the strengths-vs-weaknesses decomposition showing criticism homogenizes hardest; (d) the argument that AI-for-science should be evaluated on set-level diversity, not item-level quality. Four contributions — at the ceiling but not over it.

### R04 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, prior art and novelty claims.

**Source:** review-doublecompress-2026-09-03.md, lines 15–15; 1b. Most Extreme Critical Take.

**Original feedback:**

> **Prior art.** Qian, Wen, Furnas, Bai, Shao & Wang, "The rise of large language models and the direction and impact of US federal research funding," *PNAS* (August 2026), already used *5,700 confidential grant proposals and 131,000 awards* to show that greater LLM involvement makes proposals less semantically distinctive and positions them closer to recently funded work — at the same target venue, with 250× the sample, on real submissions rather than model-generated simulacra. Wenger & Kenett (*PNAS Nexus*, March 2026) already showed LLM outputs are more similar to each other than human outputs are, across 22 models. A hostile reviewer will say: "AI homogenizes proposals" is established at this venue, "LLMs are homogeneously creative" is established at this venue's sibling, and reviewer-score convergence from repeated sampling of one model is close to a statistical tautology — so the paper's advance reduces to running known effects on a smaller dataset. The paper currently cites none of this work, which makes the attack look like an omission rather than a differentiation. The answer exists — controlled generation vs. observational assistance, the review stage, the core/edge geometry, and the two-stage compounding are all genuinely new — but the paper must make that answer explicit, because at least one likely reviewer pool (the Wang group is at Kellogg) will make the attack.

### R06 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 25–25; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> **Automated reviewing — systems and deployments** (intro ¶2 "issue evaluative judgments," and the Result C framing):

### R07 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 27–27; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Reviewer3 / "r3"** (reviewer3.ai, Khalil & Reed) — commercial AI peer review; >30,000 manuscripts reviewed for >10,000 researchers; claims a "full panel" review in under 10 minutes. The "full panel from one model" framing is exactly what Result C undercuts: your data show that panel is one voice sampled five times.

### R08 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 28–28; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Refine.ink** (Ben Golub & Yann Calvó) — AI referee reports for economics; now formally partnered with the **American Economic Association and the Econometric Society** for AI-assisted technical verification; wins ~90% of head-to-head matches against human-preferred baselines on their benchmark. This is the strongest evidence that automated review is entering *institutional* gatekeeping, not just author-side self-checking — it converts your "if selection is also automated" conditional from hypothetical to current events.

### R09 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 29–29; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **OpenAIReview** (Chenhao Tan's Chicago Human+AI lab) — open-source AI-assisted reviewing tool positioned as democratizing access to feedback.

### R10 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 30–30; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Liang et al., NEJM AI 2024**, "Can large language models provide useful feedback on research papers?" — the canonical item-level-quality evaluation your collective-level argument is defined against; explicitly cite it as what current evaluations measure.

### R11 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 31–31; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Liang et al., ICML 2024**, "Monitoring AI-modified content at scale" — 6.5–16.9% of ICLR/NeurIPS reviews already LLM-modified; AI review isn't a future scenario inside peer review either.

### R12 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 32–32; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **NeurIPS 2026 AI-assisted reviewing experiment** and **Baumann et al. 2026, "Stop automating peer review without rigorous evaluation"** (arXiv:2605.03202) — the policy debate your evaluation criterion (diversity per unit of scale) speaks to.

### R13 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Result C framing.

**Source:** review-doublecompress-2026-09-03.md, lines 33–33; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - Human baseline for review disagreement: **Pier et al., PNAS 2018**, "Low agreement among reviewers evaluating the same NIH grant applications" (IRR ≈ 0 across 43 reviewers) — essential: human panels *maximally* disagree, which is the diversity AI panels erase, and it's at your venue.

### R14 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Discussion, automation at scale.

**Source:** review-doublecompress-2026-09-03.md, lines 35–35; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> **Automated science / generation side** (intro ¶2 "produce research ideas… run experiments," discussion "efforts to automate science at scale"):

### R15 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Discussion, automation at scale.

**Source:** review-doublecompress-2026-09-03.md, lines 37–37; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Si, Yang & Hashimoto** — already cited as Si et al. 2024; add the follow-up **"The ideation–execution gap"** (2025): LLM ideas rated more novel ex ante performed *worse* when executed — pairs perfectly with your edge-thinning result.

### R16 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Discussion, automation at scale.

**Source:** review-doublecompress-2026-09-03.md, lines 38–38; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Chenhao Tan's hypothesis-generation line**: HypoGeniC ("Hypothesis generation with large language models," NLP4Science 2024) and **Li, Li & Tan, ACL 2025**, "Literature meets data" — the constructive program your diagnosis applies to.

### R17 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Discussion, automation at scale.

**Source:** review-doublecompress-2026-09-03.md, lines 39–39; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Lu et al. 2024, "The AI Scientist"** (Sakana) and **AI Scientist-v2 (2025)** — for "research articles written and reviewed entirely by AI agents."

### R18 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 2; Discussion, automation at scale.

**Source:** review-doublecompress-2026-09-03.md, lines 40–40; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Agents4Science 2025** (Zou et al.; report at arXiv:2511.15534) — 315 AI-authored submissions reviewed by GPT-5, Gemini 2.5 Pro, and Claude Sonnet 4 with scores *averaged* across the three models; 48 accepted. This is a real venue already running the end-to-end pipeline you warn about, and averaging correlated AI judgments is precisely the failure mode Result C documents. Also **aiXiv** (arXiv:2508.15126).

### R19 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 42–42; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> **Homogenization / diversity** (intro ¶3, persona-motivation [CITE]s, discussion):

### R20 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 44–44; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Wenger & Kenett, PNAS Nexus 2026**, "Large language models are homogeneously creative" — 22 LLMs vs. 102 humans; LLM outputs slightly more original but far more similar to each other. Your model-level convergence result generalizes theirs to real scientific content; being in the PNAS family, it must be cited.

### R21 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 45–45; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Qian et al., PNAS 2026** (see 1b) — cite and differentiate in the introduction, not the discussion.

### R22 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 46–46; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Hao, Xu, Li & Evans** — cited as "Hao et al., 2024" (arXiv); now published as "Artificial intelligence tools expand scientists' impact but contract science's focus," ***Nature* 2026** (s41586-025-09922-y). Update the citation — 41.3M papers, AI users publish 3.02× more but collectively narrow.

### R23 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 47–47; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Padmakumar & He, ICLR 2024**, "Does writing with language models reduce content diversity?"; **Anderson et al., C&C 2024**, "Homogenization effects of LLMs on human creative ideation"; **Ashkinaze et al.**, "How AI ideas affect the creativity, diversity, and evolution of human ideas" — with Doshi & Hauser (cited), these are the individual-output homogenization base.

### R24 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 48–48; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Sourati, Ziabari & Dehghani, *Trends in Cognitive Sciences* 2026** ("McDonaldization") and **Daryani, Sourati & Dehghani 2026** (policy) — the theoretical/cultural framing.

### R25 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 49–49; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **"The shrinking landscape of linguistic diversity in the age of large language models," *Nature Human Behaviour* 2026** — corpus-scale evidence (80k arXiv papers among ~460k documents) that variance shrank after ChatGPT. Useful in the intro's stakes paragraph.

### R26 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction paragraph 3; persona motivation; Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 50–50; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Moon et al.'s "creative scar" result** (AI exposure leaves outputs more homogeneous two months later, no AI present) — optional discussion cite: compression may persist even after AI is removed.

### R27 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, aggregation / ensembles / juries / monoculture citation cluster.

**Source:** review-doublecompress-2026-09-03.md, lines 52–52; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> **Monoculture, ensembles, juries** (discussion's [CITE] cluster "ensemble decision making [CITE], jury models [CITE], algorithmic monoculture [CITE], deliberative disagreement [CITE]"):

### R28 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, aggregation / ensembles / juries / monoculture citation cluster.

**Source:** review-doublecompress-2026-09-03.md, lines 54–54; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Kleinberg & Raghavan, PNAS 2021**, "Algorithmic monoculture and social welfare" — the formal result that shared algorithms degrade collective outcomes even when individually more accurate. Your paper is the empirical instantiation of this theorem in science funding; it's also a venue-fit anchor.

### R29 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, aggregation / ensembles / juries / monoculture citation cluster.

**Source:** review-doublecompress-2026-09-03.md, lines 55–55; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Bommasani et al., NeurIPS 2022**, "Picking on the same person" — outcome homogenization from shared foundation models.

### R30 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, aggregation / ensembles / juries / monoculture citation cluster.

**Source:** review-doublecompress-2026-09-03.md, lines 56–56; Key citations to add, mapped to the draft's [CITE] slots.

**Original feedback:**

> - **Hong & Page, PNAS 2004** (diversity trumps ability) and **Lorenz et al., PNAS 2011** (social influence undermines wisdom of crowds) — the aggregation-value citations, both at PNAS.

### R31 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction framing; Discussion context.

**Source:** review-doublecompress-2026-09-03.md, lines 60–60; The homogenization news context (nature.com/articles/d41586-026-02682-3).

**Original feedback:**

> The September 1, 2026 Nature feature "Bland new world: is AI making us all think the same?" synthesizes exactly this literature — Wenger's homogeneous creativity, Sourati's McDonaldization, Naaman's "mind hijacking," corpus-level convergence of scientific writing. Position the paper as the next step in that arc: everything in that feature measures homogenization of *individual outputs* (essays, ideas, wording) or *corpus-level style*. Double compression moves the question to where homogenization has institutional teeth — **the two-stage pipeline that decides which science gets resourced** — with real stakes, expert humans, and leakage-proof data, and shows the two stages fail differently (coverage loss in generation, independence loss in review). That framing does three things: (1) it gives PNAS editors a live news hook; (2) it inoculates against "homogenization is already known" by conceding the individual-level results and claiming the collective-institutional level; (3) it explains why persona prompting — the fix the individual-level literature offers — doesn't transfer. Consider citing the feature itself in the discussion's zeitgeist sentence; PNAS allows it.

### R66 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, Qian comparison.

**Source:** review-doublecompress-2026-09-03.md, lines 136–136; Opportunities (by impact).

**Original feedback:**

> 1. **Own the Qian et al. adjacency.** One intro sentence — "Observational evidence shows LLM-assisted proposals drift toward recently funded work (Qian et al. 2026); whether this reflects the models or their users, and whether it extends to the judgments applied to proposals, requires controlled comparison" — converts the biggest threat into the motivation. Also worth a hallway conversation with the Wang group before submission.

### R69 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, automated review; Discussion, correlated panels.

**Source:** review-doublecompress-2026-09-03.md, lines 139–139; Opportunities (by impact).

**Original feedback:**

> 4. **Elevate the Agents4Science score-averaging detail** — a real venue averaging three models' scores is the perfect concrete instance of "correlated judgments masquerading as a panel."

### R72 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, Qian and Wenger citations and novelty claims.

**Source:** review-doublecompress-2026-09-03.md, lines 146–146; Problems.

**Original feedback:**

> - **C1 — Missing prior art at the target venue.** Qian et al. (PNAS 2026) and Wenger & Kenett (PNAS Nexus 2026) are uncited. Resolution: cite, differentiate (controlled generation; review stage; core/edge geometry; two-stage compounding), reframe novelty claims accordingly.

### R82 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction, Hao citation.

**Source:** review-doublecompress-2026-09-03.md, lines 160–160; Problems.

**Original feedback:**

> - Update Hao et al. 2024 arXiv → *Nature* 2026 published version.

### B01 Unattributed editorial note in draft body

**Referenced location:** Introduction, paragraph 1.

**Source:** Word draft body, paragraph 8; ordinary text, not a Word comment.

**Original feedback:**

> (citations)

### B02 Unattributed editorial note in draft body

**Referenced location:** Introduction, paragraph 2.

**Source:** Word draft body, paragraph 9; ordinary text, not a Word comment.

**Original feedback:**

> (Cite end-to-end science pieces by Julio and Brian and other works)

### B03 Unattributed editorial note in draft body

**Referenced location:** Introduction, paragraph 3.

**Source:** Word draft body, paragraph 10; ordinary text, not a Word comment.

**Original feedback:**

> (I would cite Science editorial here)

### B07 Unattributed editorial note in draft body

**Referenced location:** Result B, Distinctive edges.

**Source:** Word draft body, paragraph 36; ordinary text, not a Word comment.

**Original feedback:**

> (Uzzi et al. 2Ottino 20XX)

### B08 Unattributed editorial note in draft body

**Referenced location:** Robustness checks, Style and embedding.

**Source:** Word draft body, paragraph 49; ordinary text, not a Word comment.

**Original feedback:**

> (NEED CITATION HERE)

## Figures and captions

### W17 Brian Uzzi

**Referenced location:** Fig. 3 caption.

**Source:** Word comment ID 17; document paragraph 33.

**Exact draft anchor:**

> Fig. 3. AI engages the same biomedical territory as human proposals but occupies it less evenly, and the ideas it fails to reproduce are specifically the most distinctive. (A) Effective number of literature regions occupied (inverse Simpson, of 12) for the human set (fixed at 4.94) and for AI subsampled to matched size (n = 23, drawn 1,000 times without replacement; box = median and interquartile range, points = subsample draws), in each condition. AI concentrates in fewer regions in every condition (ratio AI ÷ human 0.78, 0.62, 0.73), most under one-at-a-time. Both groups touch the same regions (5 to 8 of 12) and similar numbers of MeSH terms; what differs is how evenly those regions are occupied. (B) For each of the 23 human proposals, how distinctive it is (distance from the center of human idea space) against how often an equal-sized AI pool fails to reproduce it (its nearest AI proposal falls beyond the spacing that separates two human proposals); miss-rate rises with distinctiveness (Spearman ρ = +0.86, P < 0.001). Top inset: mean miss-rate by density tertile, where AI misses 0% of core ideas, 4% of the middle, and 69% of the distinctive edge. Bottom inset: human proposals with no AI counterpart (18% to 26%) versus AI proposals with no human counterpart (4% to 9%, near the ~10% chance reference). The ideas AI misses are unrelated to the competition's funding or ranking (funded vs rejected miss-rate 0.20 vs 0.26, Mann-Whitney P = 0.77; all P > 0.3). Displacement between the two proposal clouds, reported in the text and not shown here, is not significant (MMD² = 0.032 to 0.062, against a human split-half floor ≈ 0).]

**Original feedback:**

> Evey, I am not copyediting the captions.  We fix them once we have the results in the text fixed.  The captions need to tell the WHOLE story of the paper in the most concise way possible but still include methods, tests, interpretations, and a walk through of each plot and its meaning for the readers who only read the captions.

### R36 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Results figures, especially Fig. 3 caption.

**Source:** review-doublecompress-2026-09-03.md, lines 69–69; 2b. Venue-specific analysis.

**Original feedback:**

> - **Results presentation**: figure-driven with statistics inline — matches. But PNAS expects tight figure captions; current bracketed captions run long (Fig. 3's caption is ~200 words of methods; move to SI or Methods).

### R84 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Fig. 3 caption; Methods/SI.

**Source:** review-doublecompress-2026-09-03.md, lines 162–162; Problems.

**Original feedback:**

> - Fig. 3 caption is a methods section; trim to ~80 words, move mechanics to Methods/SI.

## Venue and audience

### R33 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction contribution; overall venue fit.

**Source:** review-doublecompress-2026-09-03.md, lines 66–66; 2b. Venue-specific analysis.

**Original feedback:**

> - **Contribution bar**: cleared on novelty of design (confidential corpus, matched task environment, both stages), *provided* the Qian et al. differentiation is explicit. Without it, this reads as a smaller replication and the bar is not cleared. The n=23 scale is unusual for PNAS social science, but Pier et al. published at n=25 proposals because the corpus was similarly irreplaceable — cite it partly for that precedent.

### R37 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Materials and methods; SI Appendix.

**Source:** review-doublecompress-2026-09-03.md, lines 70–70; 2b. Venue-specific analysis.

**Original feedback:**

> - **Methods depth**: main-text Materials and Methods with SI appendix — correct for PNAS.

### R61 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Whole manuscript framing and audience.

**Source:** review-doublecompress-2026-09-03.md, lines 125–125; 8. Audience.

**Original feedback:**

> - **Metascience / science policy** — direct evidence for how AI adoption changes funding pipelines; speaks to NIH/ARPA-H policy divergence.

### R62 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Discussion, scientific AI evaluation.

**Source:** review-doublecompress-2026-09-03.md, lines 126–126; 8. Audience.

**Original feedback:**

> - **AI-for-science / NLP** — a new evaluation axis (set-level diversity, judgment independence) for systems like AI Scientist, Refine, Reviewer3.

### R63 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Introduction and Discussion, science of science.

**Source:** review-doublecompress-2026-09-03.md, lines 127–127; 8. Audience.

**Original feedback:**

> - **Computational social scientists / science of science** — the monoculture-made-empirical result; natural companions to Qian et al. and Hao et al.

### R64 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Methods/persona result and Discussion.

**Source:** review-doublecompress-2026-09-03.md, lines 128–128; 8. Audience.

**Original feedback:**

> - **HCI / human-AI collaboration** — the persona-fails result contradicts the field's favorite intervention.

### R65 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Whole manuscript, venue choice.

**Source:** review-doublecompress-2026-09-03.md, lines 130–130; 8. Audience.

**Original feedback:**

> PNAS is the right venue: the two closest neighbors (Qian et al.; Kleinberg & Raghavan) are both there, the paper's form (short, figure-driven, Significance-statement-friendly) fits, and being the controlled, two-stage complement to Qian et al. at the same venue is a strength if framed as such. Nature Human Behaviour is the alternative if PNAS balks at n=23.

## Source context

### M03 Matt (name supplied by filename)

**Referenced location:** Analysis feedback preamble.

**Source:** matt_feedback.md, lines 5–5.

**Original feedback:**

> From an analysis perspective, here's my human (non-AI) feedback:

### M10 Matt (name supplied by filename)

**Referenced location:** Methods and documentation feedback preamble.

**Source:** matt_feedback.md, lines 16–16.

**Original feedback:**

> Other details:

### R01 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 3–3; Review: "Double compression: AI narrows both the generation and the gatekeeping of scientific ideas".

**Original feedback:**

> **Target venue:** PNAS · **Mode:** Draft Mode for Lab · **Lab paper** · **Reviewed:** 2026-09-03

### R05 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 21–21; 2a. Field-wide search — queries used.

**Original feedback:**

> `R3 automated reviewer LLM peer review system 2026` · `"Reviewer3" OR "r3" AI reviewer tool scientific papers startup` · `Refine Ben Golub AI economics peer review referee reports` · `Chenhao Tan LLM peer review hypothesis generation AI for science 2025 2026` · `Diyi Yang AI research ideas Agents4Science automated science LLM ideation 2025 2026` · `Liang Zou "monitoring AI-modified content" ICLR reviews` · `Emily Wenger LLM creativity homogenization 22 models 102 humans` · `Sourati "McDonaldization" AI homogenization 2026` · `Agents4Science conference AI-written AI-reviewed papers James Zou results` · `study 400,000 scientific articles similarity increased after ChatGPT` · `Pier "low agreement" NIH grant applications PNAS` · `Hao et al AI expands scientists impact contracts science focus` · `LLM grant proposal review NIH NSF 2025` · `"algorithmic monoculture" Kleinberg Raghavan Bommasani` · `Liang "can large language models provide useful feedback on research papers" NEJM AI` · `AI exposure lasting creativity homogenization "two months"`

### R32 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 64–64; 2b. Venue-specific analysis.

**Original feedback:**

> Queries: `PNAS large language models grant proposals 2026` · `PNAS algorithmic monoculture` · `Pier PNAS grant review agreement`. Comparison papers: **Qian et al. 2026 (PNAS)**, **Kleinberg & Raghavan 2021 (PNAS)**, **Pier et al. 2018 (PNAS)**, **Wenger & Kenett 2026 (PNAS Nexus)**, Doshi & Hauser 2024 (Sci. Adv., structural analog).

### R71 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 144–144; Problems.

**Original feedback:**

> **Critical**

### R75 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 150–150; Problems.

**Original feedback:**

> **Major**

### R80 Automated review dated 2026-09-03 (author/model not identified)

**Referenced location:** Review metadata or search context; no specific manuscript section.

**Source:** review-doublecompress-2026-09-03.md, lines 157–157; Problems.

**Original feedback:**

> **Minor**

