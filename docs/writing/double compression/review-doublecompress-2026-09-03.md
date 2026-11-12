# Review: "Double compression: AI narrows both the generation and the gatekeeping of scientific ideas"

**Target venue:** PNAS · **Mode:** Draft Mode for Lab · **Lab paper** · **Reviewed:** 2026-09-03

---

## 1. Steel Man Summary

The central contribution: using 23 confidential proposals and 85 expert reviews from a real NSF bioscience competition (NCEMS) as a ground-truth corpus that cannot be in any model's training data, the paper shows that frontier LLMs compress scientific search at both stages of grant review — generating proposal sets with 25–36% fewer distinct ideas that reproduce the dense core of human idea space while missing 69% of its distinctive edge, and producing review panels whose judgments converge on one another (Cliff's δ down to −0.91) and carry no detectable funding signal — and that persona prompting, the strongest documented anti-homogenization intervention, fixes the wording but not the ideas.

Additional contributions: (a) a four-facet diversity decomposition (spread, richness, evenness, coverage) with style-normalization to separate idea-level from wording-level effects; (b) the core-vs-edge geometry result (distinctiveness almost deterministically predicts AI miss-rate, ρ = +0.86); (c) the strengths-vs-weaknesses decomposition showing criticism homogenizes hardest; (d) the argument that AI-for-science should be evaluated on set-level diversity, not item-level quality. Four contributions — at the ceiling but not over it.

## 1b. Most Extreme Critical Take

**Prior art.** Qian, Wen, Furnas, Bai, Shao & Wang, "The rise of large language models and the direction and impact of US federal research funding," *PNAS* (August 2026), already used *5,700 confidential grant proposals and 131,000 awards* to show that greater LLM involvement makes proposals less semantically distinctive and positions them closer to recently funded work — at the same target venue, with 250× the sample, on real submissions rather than model-generated simulacra. Wenger & Kenett (*PNAS Nexus*, March 2026) already showed LLM outputs are more similar to each other than human outputs are, across 22 models. A hostile reviewer will say: "AI homogenizes proposals" is established at this venue, "LLMs are homogeneously creative" is established at this venue's sibling, and reviewer-score convergence from repeated sampling of one model is close to a statistical tautology — so the paper's advance reduces to running known effects on a smaller dataset. The paper currently cites none of this work, which makes the attack look like an omission rather than a differentiation. The answer exists — controlled generation vs. observational assistance, the review stage, the core/edge geometry, and the two-stage compounding are all genuinely new — but the paper must make that answer explicit, because at least one likely reviewer pool (the Wang group is at Kellogg) will make the attack.

## 2. Venue Context & Literature Search

### 2a. Field-wide search — queries used

`R3 automated reviewer LLM peer review system 2026` · `"Reviewer3" OR "r3" AI reviewer tool scientific papers startup` · `Refine Ben Golub AI economics peer review referee reports` · `Chenhao Tan LLM peer review hypothesis generation AI for science 2025 2026` · `Diyi Yang AI research ideas Agents4Science automated science LLM ideation 2025 2026` · `Liang Zou "monitoring AI-modified content" ICLR reviews` · `Emily Wenger LLM creativity homogenization 22 models 102 humans` · `Sourati "McDonaldization" AI homogenization 2026` · `Agents4Science conference AI-written AI-reviewed papers James Zou results` · `study 400,000 scientific articles similarity increased after ChatGPT` · `Pier "low agreement" NIH grant applications PNAS` · `Hao et al AI expands scientists impact contracts science focus` · `LLM grant proposal review NIH NSF 2025` · `"algorithmic monoculture" Kleinberg Raghavan Bommasani` · `Liang "can large language models provide useful feedback on research papers" NEJM AI` · `AI exposure lasting creativity homogenization "two months"`

### Key citations to add, mapped to the draft's [CITE] slots

**Automated reviewing — systems and deployments** (intro ¶2 "issue evaluative judgments," and the Result C framing):

- **Reviewer3 / "r3"** (reviewer3.ai, Khalil & Reed) — commercial AI peer review; >30,000 manuscripts reviewed for >10,000 researchers; claims a "full panel" review in under 10 minutes. The "full panel from one model" framing is exactly what Result C undercuts: your data show that panel is one voice sampled five times.
- **Refine.ink** (Ben Golub & Yann Calvó) — AI referee reports for economics; now formally partnered with the **American Economic Association and the Econometric Society** for AI-assisted technical verification; wins ~90% of head-to-head matches against human-preferred baselines on their benchmark. This is the strongest evidence that automated review is entering *institutional* gatekeeping, not just author-side self-checking — it converts your "if selection is also automated" conditional from hypothetical to current events.
- **OpenAIReview** (Chenhao Tan's Chicago Human+AI lab) — open-source AI-assisted reviewing tool positioned as democratizing access to feedback.
- **Liang et al., NEJM AI 2024**, "Can large language models provide useful feedback on research papers?" — the canonical item-level-quality evaluation your collective-level argument is defined against; explicitly cite it as what current evaluations measure.
- **Liang et al., ICML 2024**, "Monitoring AI-modified content at scale" — 6.5–16.9% of ICLR/NeurIPS reviews already LLM-modified; AI review isn't a future scenario inside peer review either.
- **NeurIPS 2026 AI-assisted reviewing experiment** and **Baumann et al. 2026, "Stop automating peer review without rigorous evaluation"** (arXiv:2605.03202) — the policy debate your evaluation criterion (diversity per unit of scale) speaks to.
- Human baseline for review disagreement: **Pier et al., PNAS 2018**, "Low agreement among reviewers evaluating the same NIH grant applications" (IRR ≈ 0 across 43 reviewers) — essential: human panels *maximally* disagree, which is the diversity AI panels erase, and it's at your venue.

**Automated science / generation side** (intro ¶2 "produce research ideas… run experiments," discussion "efforts to automate science at scale"):

- **Si, Yang & Hashimoto** — already cited as Si et al. 2024; add the follow-up **"The ideation–execution gap"** (2025): LLM ideas rated more novel ex ante performed *worse* when executed — pairs perfectly with your edge-thinning result.
- **Chenhao Tan's hypothesis-generation line**: HypoGeniC ("Hypothesis generation with large language models," NLP4Science 2024) and **Li, Li & Tan, ACL 2025**, "Literature meets data" — the constructive program your diagnosis applies to.
- **Lu et al. 2024, "The AI Scientist"** (Sakana) and **AI Scientist-v2 (2025)** — for "research articles written and reviewed entirely by AI agents."
- **Agents4Science 2025** (Zou et al.; report at arXiv:2511.15534) — 315 AI-authored submissions reviewed by GPT-5, Gemini 2.5 Pro, and Claude Sonnet 4 with scores *averaged* across the three models; 48 accepted. This is a real venue already running the end-to-end pipeline you warn about, and averaging correlated AI judgments is precisely the failure mode Result C documents. Also **aiXiv** (arXiv:2508.15126).

**Homogenization / diversity** (intro ¶3, persona-motivation [CITE]s, discussion):

- **Wenger & Kenett, PNAS Nexus 2026**, "Large language models are homogeneously creative" — 22 LLMs vs. 102 humans; LLM outputs slightly more original but far more similar to each other. Your model-level convergence result generalizes theirs to real scientific content; being in the PNAS family, it must be cited.
- **Qian et al., PNAS 2026** (see 1b) — cite and differentiate in the introduction, not the discussion.
- **Hao, Xu, Li & Evans** — cited as "Hao et al., 2024" (arXiv); now published as "Artificial intelligence tools expand scientists' impact but contract science's focus," ***Nature* 2026** (s41586-025-09922-y). Update the citation — 41.3M papers, AI users publish 3.02× more but collectively narrow.
- **Padmakumar & He, ICLR 2024**, "Does writing with language models reduce content diversity?"; **Anderson et al., C&C 2024**, "Homogenization effects of LLMs on human creative ideation"; **Ashkinaze et al.**, "How AI ideas affect the creativity, diversity, and evolution of human ideas" — with Doshi & Hauser (cited), these are the individual-output homogenization base.
- **Sourati, Ziabari & Dehghani, *Trends in Cognitive Sciences* 2026** ("McDonaldization") and **Daryani, Sourati & Dehghani 2026** (policy) — the theoretical/cultural framing.
- **"The shrinking landscape of linguistic diversity in the age of large language models," *Nature Human Behaviour* 2026** — corpus-scale evidence (80k arXiv papers among ~460k documents) that variance shrank after ChatGPT. Useful in the intro's stakes paragraph.
- **Moon et al.'s "creative scar" result** (AI exposure leaves outputs more homogeneous two months later, no AI present) — optional discussion cite: compression may persist even after AI is removed.

**Monoculture, ensembles, juries** (discussion's [CITE] cluster "ensemble decision making [CITE], jury models [CITE], algorithmic monoculture [CITE], deliberative disagreement [CITE]"):

- **Kleinberg & Raghavan, PNAS 2021**, "Algorithmic monoculture and social welfare" — the formal result that shared algorithms degrade collective outcomes even when individually more accurate. Your paper is the empirical instantiation of this theorem in science funding; it's also a venue-fit anchor.
- **Bommasani et al., NeurIPS 2022**, "Picking on the same person" — outcome homogenization from shared foundation models.
- **Hong & Page, PNAS 2004** (diversity trumps ability) and **Lorenz et al., PNAS 2011** (social influence undermines wisdom of crowds) — the aggregation-value citations, both at PNAS.

### The homogenization news context (nature.com/articles/d41586-026-02682-3)

The September 1, 2026 Nature feature "Bland new world: is AI making us all think the same?" synthesizes exactly this literature — Wenger's homogeneous creativity, Sourati's McDonaldization, Naaman's "mind hijacking," corpus-level convergence of scientific writing. Position the paper as the next step in that arc: everything in that feature measures homogenization of *individual outputs* (essays, ideas, wording) or *corpus-level style*. Double compression moves the question to where homogenization has institutional teeth — **the two-stage pipeline that decides which science gets resourced** — with real stakes, expert humans, and leakage-proof data, and shows the two stages fail differently (coverage loss in generation, independence loss in review). That framing does three things: (1) it gives PNAS editors a live news hook; (2) it inoculates against "homogenization is already known" by conceding the individual-level results and claiming the collective-institutional level; (3) it explains why persona prompting — the fix the individual-level literature offers — doesn't transfer. Consider citing the feature itself in the discussion's zeitgeist sentence; PNAS allows it.

### 2b. Venue-specific analysis

Queries: `PNAS large language models grant proposals 2026` · `PNAS algorithmic monoculture` · `Pier PNAS grant review agreement`. Comparison papers: **Qian et al. 2026 (PNAS)**, **Kleinberg & Raghavan 2021 (PNAS)**, **Pier et al. 2018 (PNAS)**, **Wenger & Kenett 2026 (PNAS Nexus)**, Doshi & Hauser 2024 (Sci. Adv., structural analog).

- **Contribution bar**: cleared on novelty of design (confidential corpus, matched task environment, both stages), *provided* the Qian et al. differentiation is explicit. Without it, this reads as a smaller replication and the bar is not cleared. The n=23 scale is unusual for PNAS social science, but Pier et al. published at n=25 proposals because the corpus was similarly irreplaceable — cite it partly for that precedent.
- **Introduction tone**: matches PNAS (problem → tension → "Here/We study") but the current opening paragraph is flatter than the venue norm; PNAS intros of this type open with a sharper real-world development (see lab-voice notes).
- **Contribution articulation**: PNAS wants the narrative form you use; the final intro paragraph ("We therefore argue…") is appropriately synthetic.
- **Results presentation**: figure-driven with statistics inline — matches. But PNAS expects tight figure captions; current bracketed captions run long (Fig. 3's caption is ~200 words of methods; move to SI or Methods).
- **Methods depth**: main-text Materials and Methods with SI appendix — correct for PNAS.
- **Abstract/Significance**: PNAS caps abstracts at 250 words and Significance at 120 — both are at or over the limit; trim.

### 2c. Lab voice analysis

- **Opening puzzle/tension**: ✗ weakest part of the draft. "Scientific grants are the primary mechanism that links new ideas to the resources needed to pursue them" is a textbook opener, not a puzzle. No vivid concrete example, no signature "remains an open question." A ready-made vignette exists in the current news: *in September 2025 the NIH declared substantially AI-developed applications a violation of its originality expectations, while the same year a Stanford conference accepted 48 papers generated and reviewed entirely by AI, scored by averaging three models' judgments* — that's the tension (institutions simultaneously banning and institutionalizing AI at both stages) in two sentences, and both facts are load-bearing citations anyway.
- **Narrowing pivot**: ✓ "We study double compression with data that carries the stakes and expertise of real grant funding" is a clean lab-style pivot.
- **Empirical specificity in abstract**: ✓ strong — 23 proposals, three models, three conditions, effect ranges all present.
- **Nuance, hedged with "but/however"**: ✓ excellent throughout ("AlphaFold transformed… Yet this efficiency may carry a collective cost"; Gemini exceptions reported honestly).
- **"Together, these results…" synthesis**: ✗ absent. The discussion opens with "We compared…" and never lands the synthesizing sentence. Add one at the start of the discussion or end of results: "Together, these results show that AI narrows scientific search twice: …"
- **Limitations stated plainly**: ✓ the limitations paragraph is genuinely good — direct, specific, non-perfunctory.
- Divergence verdict: the voice is 80% there; the opening and the missing "Together" move are the two real gaps.

## 3. Lynchpin Evidence Analysis

The lynchpin is **Result A's matched-size diversity ratio** (pooled AI holds 64–70% of human spread and 66–75% of human richness, significant in all conditions, surviving persona and style normalization). If that ratio were an artifact, Results B–D would be reinterpretations of noise.

- **Rigor**: The design is unusually careful — matched sample sizes, 1,000 subsample draws, jackknife CIs, label-permutation tests, no resampling with replacement, raw-text robustness branch, and persona as a prespecified stress test. This is the best-controlled comparison of its kind I've seen.
- **The central confound — input-information asymmetry**: Human applicants bring labs, preliminary data, collaborators, funding history, and career incentives to differentiate (the draft itself notes "applicants have every reason to differentiate… a model asked for 23 proposals in a single pass has none" — for baseline, but the deeper asymmetry applies to *all* conditions). The persona condition conditions on 5 titles+abstracts — a thin proxy for a scientist's generative context. A hostile reviewer will say the paper measures what models do with *impoverished input*, not a property of models. The honest defense: (a) one-at-a-time removes the single-pass incentive problem and compression persists; (b) the claim should be explicitly scoped to "AI as currently deployable from a call + public record," which is exactly how automated pipelines would run. Say this in limitations or reframe the claim; don't leave it for reviewers.
- **Ecological validity**: high on the human side (real stakes, real experts — the paper's whole selling point) but note the AI side is zero-stakes by construction; that asymmetry is part of what's being measured and should be named.
- **Effect size**: large and practically framed (one human proposal in five with no AI counterpart; 69% of the distinctive edge missed). Good.
- **Result C's convergence has a rigor gap of its own**: five reviews sampled from one model at fixed decoding parameters *should* correlate; δ = −0.91 may partly measure temperature, not judgment. Decoding parameters are relegated to SI. Report temperature in the main text and, ideally, add a high-temperature robustness condition — otherwise a reviewer can dismiss Result C as "sampling variance is smaller than reviewer variance, as expected."

## 4. Dataset Evaluation

| Attribute | Details |
|---|---|
| Name & source | NCEMS (NSF National Synthesis Center for Emergence in the Molecular and Cellular Sciences) inaugural competition, 2 cohorts |
| Publicly accessible? | No — confidential; de-identified derived data (embeddings, facet values) by agreement; **repository/DOI still a placeholder** |
| N observations | 23 proposals; 85 expert reviews; +69 AI proposals; 345 AI reviews |
| N unique individuals | Not reported — add N of distinct human applicants and reviewers |
| Study design | Matched observational comparison with experimental prompting conditions on the AI side |
| Demographic diversity | Not reported; at minimum report applicant institutional/geographic spread ("faculty at top universities around the world" is currently a claim without numbers) |
| Temporal coverage | Two competition years (which years? "two seperate years" — unspecified and misspelled) |

The confidentiality is the dataset's superpower (leakage-proof) and its transparency weakness; the paper handles the tradeoff about as well as possible, but the derived-data repository must actually exist at submission. Comparable corpora: Pier et al.'s 25 replicated NIH applications; Qian et al.'s 5,700 confidential proposals (observational LLM use, no reviews); no public corpus pairs confidential proposals *with their reviews* — make that uniqueness claim explicitly, it strengthens the Qian differentiation.

## 5. Reproducibility Check

Code is "[repository]" and data is confidential → no reproduction attempted (per protocol, code was not inspected). **Flags**: (1) analysis code not yet public — must be at submission; (2) the de-identified derived data (embeddings + per-item facet values) would allow full reproduction of every statistic in the paper without exposing proposal text — release it, don't just describe access terms; (3) the Gemini style-normalization step is itself irreproducible unless the exact model version, prompt, and normalized outputs' embeddings are archived.

## 6. Statistical Rigor

- **Absence of evidence ≠ evidence of absence** — mostly exemplary ("no detectable association," "not detectably less likely," the explicit "absence of a detectable funding signal… is not evidence of a true null"). Three violations to fix: **Fig. 3 caption**: "The ideas AI misses are unrelated to the competition's funding or ranking" → "not detectably associated with"; **Results heading**: "Scores from AI panel do not predict funding outcome" → "carry no detectable funding signal" (the paragraph's own phrasing); **Discussion**: "the lack of an association" → "the lack of a detectable association" (the sentence's second half already gets it right).
- **Multiple testing**: 5 prespecified primary comparisons at face value, BH within task × branch × stratum for the rest — well designed. State the *total* number of BH-corrected tests somewhere in SI.
- **Power**: n=23 limits are acknowledged and pooling is justified; good. But the strengths-vs-weaknesses analysis is candidly flagged as a decomposition, not independent replication — keep that sentence, reviewers will respect it.
- **No power analysis** for the AUC contrast; the paper correctly downgrades it to exploratory. Keep the human-panel comparison out of the abstract (it currently is — good).
- **Watch**: "almost deterministically" (ρ = +0.86, n=23) overshoots; ρ = −0.99 for local density is the near-deterministic one. Attach each adverb to its statistic.

## 7. Pre-registration

Not pre-registered (no registry named). The draft claims prespecification twice ("Five comparisons were designated primary in advance"; "the prespecified ordering test") with no documentation. For confirmatory-flavored claims at PNAS this will draw a question: either produce a timestamped analysis plan (OSF, even retroactively dated honestly as an internal plan) or soften "prespecified" to "designated primary before unblinding to outcomes" and say where that designation lives. The inferential risk is real: four facets × three conditions × three models × two branches × three field strata is a large garden of forking paths, and the paper's defense is currently a sentence, not a document.

## 8. Audience

- **Metascience / science policy** — direct evidence for how AI adoption changes funding pipelines; speaks to NIH/ARPA-H policy divergence.
- **AI-for-science / NLP** — a new evaluation axis (set-level diversity, judgment independence) for systems like AI Scientist, Refine, Reviewer3.
- **Computational social scientists / science of science** — the monoculture-made-empirical result; natural companions to Qian et al. and Hao et al.
- **HCI / human-AI collaboration** — the persona-fails result contradicts the field's favorite intervention.

PNAS is the right venue: the two closest neighbors (Qian et al.; Kleinberg & Raghavan) are both there, the paper's form (short, figure-driven, Significance-statement-friendly) fits, and being the controlled, two-stage complement to Qian et al. at the same venue is a strength if framed as such. Nature Human Behaviour is the alternative if PNAS balks at n=23.

## 9. Editorial Opportunities & Problems

### Opportunities (by impact)

1. **Own the Qian et al. adjacency.** One intro sentence — "Observational evidence shows LLM-assisted proposals drift toward recently funded work (Qian et al. 2026); whether this reflects the models or their users, and whether it extends to the judgments applied to proposals, requires controlled comparison" — converts the biggest threat into the motivation. Also worth a hallway conversation with the Wang group before submission.
2. **Rewrite the opening with the NIH-ban / Agents4Science tension** (see 2c) — it supplies the lab-signature vivid opening and two needed citations in one move.
3. **Add the "Together, these results…" synthesis sentence** at the discussion's start.
4. **Elevate the Agents4Science score-averaging detail** — a real venue averaging three models' scores is the perfect concrete instance of "correlated judgments masquerading as a panel."
5. **Release the derived-data + code repositories** — this paper's credibility rests on confidential data; maximal transparency on everything derivable is the compensating move.

### Problems

**Critical**

- **C1 — Missing prior art at the target venue.** Qian et al. (PNAS 2026) and Wenger & Kenett (PNAS Nexus 2026) are uncited. Resolution: cite, differentiate (controlled generation; review stage; core/edge geometry; two-stage compounding), reframe novelty claims accordingly.
- **C2 — Input-information asymmetry is treated as a model property.** Resolution: scope the claim ("AI as deployable from the call and public record"), strengthen the limitation, or add a context-enriched condition; at minimum, one honest paragraph.
- **C3 — Review convergence may be a decoding artifact.** Resolution: decoding parameters in main text; temperature-sensitivity robustness (even for one model) in SI.

**Major**

- **M1 — Gemini is both a studied model and the style normalizer.** Normalizing all text through one of the three systems under evaluation risks importing its homogeneity into the primary branch (and Gemini is the model that behaves differently in several results). Resolution: normalize with a held-out model, or show facet ratios are invariant to the choice of normalizer.
- **M2 — Prespecification is claimed but undocumented** (Section 7). Resolution: post the plan or soften the language.
- **M3 — Every [CITE], the IRB number, and both repository placeholders are unfilled.** Gating for any submission; this review's Section 2a supplies most of the [CITE] targets.
- **M4 — Per-model heterogeneity cuts against the pooled claim.** Gemini sits at parity on review spread at baseline and is the only displaced model in generation. The paper discloses this honestly but the abstract speaks of "AI" monolithically. Resolution: one abstract-safe hedge ("consistent across models, with one partial exception in each stage, detailed in results") or surface per-model panels in a main figure.

**Minor**

- Absence-of-evidence phrasing: Fig. 3 caption, Result C heading, one discussion sentence (Section 6).
- Update Hao et al. 2024 arXiv → *Nature* 2026 published version.
- Typos: "two seperate years," "indepdently," "AI, especially, Large language models are now entering…" (garbled), "gate-keeping"/"gatekeeping" inconsistency, missing period after "already produced" in Methods.
- Fig. 3 caption is a methods section; trim to ~80 words, move mechanics to Methods/SI.
- Abstract ≈ over PNAS's 250-word cap; Significance likely over 120 — trim both. In the Significance statement, "biomedical competition" vs. "molecular and cellular bioscience" — pick one descriptor and use it everywhere.
- "Almost deterministically" → attach to the ρ = −0.99 statistic, not ρ = +0.86.
- Report N unique applicants, N unique reviewers, and the two competition years in Methods.

---
