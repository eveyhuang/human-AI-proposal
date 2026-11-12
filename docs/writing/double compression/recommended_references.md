# Double compression references and how to cite them

References and citation leads raised in the collaborators’ feedback, grouped by the manuscript area they support. Source IDs refer to [Feedback by concern](feedback_by_concern.md), which preserves the original recommendations verbatim. Bibliographic corrections below do not alter those quotations. Identified works have source links; incomplete leads remain separate so they are not mistaken for finished citations. Bibliographic and citation-use checks were made on November 10, 2026.

Each entry explains the supported argument or method, the specific gap relevant to this manuscript, a possible sentence or transition, and limits on the inference. Suggested wording is newly drafted prose, not a quotation from the cited author. Proposed extensions distinguish what the current study addresses from experiments it has not performed. The linked sources support the literature descriptions; the bridges to our study are proposed interpretations.

The strongest positioning is a study of proposal coverage and assessment variation in the same confidential grant setting. It should not claim the first demonstration of AI homogenization, AI-review convergence, or controlled AI reviewing. Nor should it claim that separately observed narrowing compounds in an end-to-end pipeline: that interaction has not been tested.

## Scientific funding and collective diversity

### 1 Qian and colleagues

**Qian, Y., Wen, Z., Furnas, A. C., Bai, Y., Shao, E., & Wang, D. (2026).** The rise of large language models and the direction and impact of US federal research funding. *PNAS, 123*(33), e2601439123. [Author preprint and journal reference](https://arxiv.org/abs/2601.15485). **Recommended by:** automated review R04/R21/R66/R72; Matt M01 calls for Dashun’s latest PNAS paper. **Placement:** Introduction, prior art and contribution; distinguish observational assistance from controlled generation and review.

**What it establishes:** Detected LLM involvement in real submissions is associated with proximity to previously funded work. This supports the funding-specific motivation, not a causal claim that models alone produce narrowing.

**Gap and our contribution:** Adoption is not randomly assigned; author choices, drafting assistance, and model generation remain entangled. We elicit proposals directly under a common call and vary prompting, then compare matched-size sets and reviews of the same human proposals. This removes uncertainty about AI-output provenance, but does not equalize human expertise or establish the causal effect of adopting AI. Our human-relative coverage measure also differs from distance to historical awards.

**Suggested use:** After describing funding homogenization: “Observational evidence links LLM involvement to lower proposal distinctiveness (Qian et al., 2026). We ask whether directly generated proposal sets cover the range of human submissions under the same call, and whether model-generated reviews preserve the diversity of human assessments.”

**Method connection:** Qian already tests style sensitivity by rewriting earlier abstracts and recomputing distinctiveness. Style control is therefore a shared concern, not our novel contribution. See [the detailed contribution assessment](qian_comparison_and_contribution_strategy.md) for a comparison and prioritized analyses. Consult their stylistic robustness analyses when defending our normalization choices. [Evidence: main text and SI](https://arxiv.org/html/2601.15485v3).


### 2 Wenger and Kenett

**Wenger, E., & Kenett, Y. N. (2026).** Large language models are homogeneously creative. *PNAS Nexus, 5*(3), pgag042. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13010328). **Source:** R04/R20/R72. **Placement:** Introduction, cross-model homogenization and novelty positioning.

**What it supports:** Across standardized creativity tasks, outputs from different LLMs resemble one another more than human responses do. This makes using several models an empirical test of diversity, rather than a guarantee of independent ideas.

**Gap and our contribution:** The scientific question is whether this pattern extends to domain-specific proposals and expert evaluation, and where coverage is lost. Our contribution is the grant setting, human-relative core/edge geometry, and examination of both stages—not discovery of cross-model homogeneity itself.

**Suggested use:** In the Introduction, before the study question: “Cross-model homogeneity has been observed in creativity tasks (Wenger and Kenett, 2026); whether model-generated proposals omit particular parts of expert scientific idea space requires a domain-specific comparison.” In Discussion, connect model similarity to the need to test heterogeneous ensembles rather than assume they solve the problem.

**Limit:** Task similarity does not establish shared training data as the cause.


### 3 Hao and colleagues

**Hao, Q., Xu, F., Li, Y., & Evans, J. (2026).** Artificial intelligence tools expand scientists’ impact but contract science’s focus. *Nature, 649*, 1237–1243. [Published article](https://www.nature.com/articles/s41586-025-09922-y). **Source:** Brian W05 asks what “Hao et al., 2024” is; R22/R82 recommends updating it. **Placement:** Introduction, individual productivity versus collective breadth. **Scope:** this concerns AI-augmented research across eras of AI, not solely LLM assistance in manuscript writing.

**What it supports:** Individual scientific productivity and impact can coexist with collective narrowing of research topics. This supplies the conceptual tension in the Introduction: greater output is not the same as broader scientific exploration.

**Gap and our contribution:** Their publication-scale analysis concerns AI-augmented research broadly. We examine the upstream proposal and review stages within one competition. This offers evidence about a possible institutional point of narrowing, not proof that our measured process caused their aggregate pattern.

**Suggested use:** “AI-augmented research has been associated with individual advantages alongside a narrower collective focus (Hao et al., 2026). We examine whether comparable concentration appears before research is undertaken, in the proposals considered and the reviews applied to them.”

**Limit:** Do not describe this as a study showing that scientists used LLMs to write papers; do not equate topic breadth with innovation quality.


### 4 Padmakumar and He

**Padmakumar, V., & He, H. (2024).** Does writing with language models reduce content diversity? *ICLR*. [Proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/02dec8877fb7c6aa9a79f81661baca7c-Abstract-Conference.html). **Source:** R23. **Placement:** Introduction, content diversity under writing assistance.

**What it supports and qualifies:** A controlled essay-writing experiment finds reduced diversity with InstructGPT but not base GPT-3, with the reduction concentrated in model-contributed text. This supports separating lexical from content diversity and taking model differences seriously.

**Gap and our contribution:** We compare directly generated scientific proposals with human proposals, rather than co-written essays. Our raw versus normalized branches ask whether results survive a change in presentation; they do not reproduce this paper’s identification of human- versus model-authored segments.

**Suggested use:** “Homogenization depends on the system and contribution being measured: feedback-tuned assistance reduced essay diversity where base-model assistance did not (Padmakumar and He, 2024). We therefore report model-specific results and distinguish wording from semantic variation.”

**Limit:** The contrast motivates post-training as a possible mechanism; our design does not isolate that mechanism. [Evidence](https://arxiv.org/abs/2309.05196).


### 5 Anderson and colleagues

**Anderson, B. R., Shah, J. H., & Kreminski, M. (2024).** Homogenization effects of large language models on human creative ideation. *Creativity and Cognition*. [Author manuscript](https://arxiv.org/abs/2402.01536). **Source:** R23. **Placement:** Introduction, creative ideation and group-level diversity.

**What it supports:** ChatGPT-supported participants generated more detailed ideas but less semantically distinct ideas across users than participants using another creativity support tool. This supports distinguishing output quantity from collective breadth.

**Gap and our contribution:** Their user study does not establish coverage of expert scientific proposals or diversity in review. Our matched-size comparisons ask whether concentration persists after controlling the number of outputs being compared.

**Suggested use:** “Tools can increase the number of ideas produced while reducing their distinctiveness across users (Anderson et al., 2024). Accordingly, we compare proposal diversity at equal set size rather than treating proposal count as a measure of exploration.”

**Further analysis:** Matt’s proposed diversity-versus-set-size curve would extend this logic by estimating the additional generation needed to match human coverage; the existing fixed-size results do not answer that question.


### 6 Ashkinaze and colleagues

**Ashkinaze, J., Mendelsohn, J., Li, Q., Budak, C., & Gilbert, E. (2025).** How AI ideas affect the creativity, diversity, and evolution of human ideas: Evidence from a large, dynamic experiment. *ACM Collective Intelligence*; preprint first posted 2024. [Author manuscript](https://arxiv.org/abs/2401.13481). **Source:** R23. **Placement:** Introduction or Discussion, boundary conditions and contrasting evidence. **Interpretation correction:** the abstract reports that high AI exposure increased collective idea diversity. Do not treat this as straightforward evidence that AI reduces diversity, despite its grouping in the automated review.

**What it challenges:** High exposure to AI ideas increased collective diversity in a dynamic experiment. This challenges an unconditional claim that introducing AI necessarily homogenizes human ideas.

**Gap and our contribution:** Human participants could reinterpret AI examples and build on earlier participants’ ideas. Our direct-generation comparison evaluates a different configuration. The difference is a boundary condition, not evidence that the earlier result is wrong.

**Suggested use:** In Discussion: “AI exposure can also increase collective diversity when people build on circulating examples (Ashkinaze et al., 2025). Our findings concern directly generated proposal sets and reviews, leaving open whether iterative human–AI collaboration can recover or expand the missing territory.”

**Further analysis:** Test human-only, AI-only, and iterative mixed teams under the same call. That would distinguish replacement from augmentation; the current study cannot.


### 7 Doshi and Hauser

**Doshi, A. R., & Hauser, O. P. (2024).** Generative AI enhances individual creativity but reduces the collective diversity of novel content. *Science Advances, 10*(28), eadn5290. [Article](https://doi.org/10.1126/sciadv.adn5290). **Source:** R23/R32; already cited in the draft. **Placement:** Introduction, individual versus collective outcomes. Included as a reference the feedback explicitly recommends situating alongside the new additions.

**What it supports:** AI-assisted stories can receive better individual evaluations while becoming more similar across writers. Use this to justify evaluating a collection as well as its individual members.

**Gap and our contribution:** We extend that evaluation question to proposals and review panels. The grant corpus also permits asking which human ideas remain unmatched. We do not demonstrate the same quality–diversity tradeoff unless AI proposals receive comparable quality evaluations.

**Suggested use:** “Evidence that AI assistance improves individual creative outputs while reducing their collective diversity (Doshi and Hauser, 2024) suggests that scientific AI should also be assessed at the set level. We measure the range of proposals and assessments produced under a common funding task.”

**Limit:** A higher Vendi score is not evidence of better ideas; human funding outcomes are not direct evaluations of AI proposal quality.


### 8 Sourati and colleagues on expression and thought

**Sourati, Z., Ziabari, A. S., & Dehghani, M. (2026).** The homogenizing effect of large language models on human expression and thought. *Trends in Cognitive Sciences*. [Author manuscript](https://arxiv.org/abs/2508.01491); [published DOI](https://doi.org/10.1016/j.tics.2026.01.003). **Source:** R24, described there as “McDonaldization”; that is a framing term, not the paper title. **Placement:** Introduction/Discussion, cognitive and cultural homogenization. Preprint first posted in 2025.

**What it supports:** This synthesis connects linguistic and cognitive homogenization to common model use and dominant patterns in training and deployment. Use it to frame the broader concern and motivate distinguishing language convergence from convergence of scientific content.

**Gap and our contribution:** Our grant comparison supplies a domain-specific empirical case and operational measures of coverage and within-panel variation. It does not establish society-wide cognitive convergence or identify a training mechanism.

**Suggested use:** “Concern about convergence in expression and thought (Sourati et al., 2026) raises an institutional question: does AI preserve the range of ideas and assessments entering scientific funding?”

**Discussion use:** Present training priors and post-training as possible explanations requiring intervention studies, not causes demonstrated by this citation plus our correlations.


### 9 Daryani and colleagues

**Daryani, Y., Sourati, Z., & Dehghani, M. (2026).** The homogenizing engine: AI’s role in standardizing culture and the path to policy. *Policy Insights from the Behavioral and Brain Sciences, 13*(1). [Publisher record](https://journals.sagepub.com/doi/10.1177/23727322251406591). **Source:** R24. **Placement:** Discussion, cultural and policy implications. First published online December 29, 2025; issue year 2026.

**What it supports:** The policy article argues for cultural-diversity evaluation and interventions across the AI development process. Use it to explain why aggregate diversity should be an explicit evaluation objective.

**Gap and our contribution:** Our analysis offers a narrower operational example: compare human-relative coverage, within-panel variation, and their response to prompting. It does not measure cultural representation or demographic equity.

**Suggested use:** “Calls to evaluate the diversity preserved by AI systems (Daryani et al., 2026) can be made concrete in scientific funding by measuring both proposal coverage and variation among assessments.”

**Further analysis:** Applicant/reviewer demographic or institutional data would be required to test whether particular groups’ ideas are disproportionately lost. Current geometric edges should not be labeled marginalized social groups.


### 10 Sourati and colleagues on linguistic diversity

**Sourati, Z., Karimi-Malekabadi, F., Ozcan, M., McDaniel, C., Ziabari, A., Trager, J., Tak, A. N., Chen, M., Morstatter, F., & Dehghani, M. (2026).** The shrinking landscape of linguistic diversity in the age of large language models. *Nature Human Behaviour, 10*, 1925–1942. Published online August 24, 2026. [Published article](https://doi.org/10.1038/s41562-026-02550-0). [Local full paper](<../literature/sourati-linguistic diversity.pdf>). **Source:** R25 and the user-supplied full PDF. This updates the existing reference, rather than counting the same study twice.

**What it supports:** Across observational and rewriting studies, LLM assistance is associated with reduced linguistic variation; rewriting can also distort author-trait signals. This directly motivates distinguishing style, scientific content, and inferences drawn from text. It does not by itself show that scientific hypotheses become less diverse.

**Where and how to use it:** In the Introduction, move from established convergence in expression to the question of coverage of scientific possibilities. In Methods, use it to explain why both raw and normalized texts are necessary. In Discussion, acknowledge that the normalizer itself can suppress variation.

**Gap and our contribution:** This study concerns expression and information recoverable about authors. Our scientific question is whether candidate sets preserve distinct hypotheses and approaches, and whether reviews contain distinct evaluative concerns. That distinction requires validation of scientific content, not just a new embedding statistic.

**Suggested wording:** “LLM-assisted rewriting can reduce linguistic variation even when broad meaning is retained (Sourati et al., 2026). We ask whether narrowing also appears in the scientific proposals and assessments represented by these texts, comparing original and normalized versions.”

**Specific method connection:** PDF page 4 (journal p. 1928) reports the rewriting comparison. PDF page 11 (journal p. 1935), “Evaluating semantic preservation,” uses original–rewrite embedding similarity and an internal four-author check of 20 Reddit text pairs. Adapt the validation idea to domain experts checking hypotheses, mechanisms, methods, and review qualifications. Their broad semantic-preservation check does not establish preservation of biomedical distinctions in our corpus, and high original–rewrite cosine similarity does not guarantee unchanged pairwise geometry.

**Analysis to add:** Compare raw and normalized pairwise distances, neighborhood identities, coverage classifications, and edge membership; repeat with another normalizer. Manually audit cases whose classifications change. This would show what normalization preserves and removes in our actual measures.

**Relationship to reference 38:** Reference 38 is the research briefing for this paper, not an independent replication. Prefer this primary article for findings and methods.

## Automated science and hypothesis generation

### 11 Si and colleagues

**Si, C., Hashimoto, T., & Yang, D. (2025).** The ideation-execution gap: Execution outcomes of LLM-generated versus human research ideas. arXiv:2506.20803. [Author manuscript](https://arxiv.org/abs/2506.20803). **Source:** R15. **Placement:** Introduction or Discussion, idea ratings versus execution outcomes. This is the follow-up recommended in addition to the draft’s existing Si et al. 2024 citation; author order follows the manuscript record.

**What it challenges:** Favorable ratings of LLM-generated ideas before execution did not reliably translate into superior evaluations after execution. This challenges treating apparent novelty as validated scientific value.

**Gap and our contribution:** We measure the diversity of proposals available for selection, not their realized experimental success. Our contribution is complementary: even a useful idea generator may leave parts of the candidate space unexplored.

**Suggested use:** “Execution studies show that favorable ex ante idea ratings need not persist after implementation (Si et al., 2025). We therefore interpret semantic diversity as a property of the search space, rather than evidence of downstream scientific quality.”

**Further analysis:** Blind quality reviews would address Matt’s immediate request; executing proposals would address the stronger quality question. Neither is supplied by a null association between human miss-rate and funding.


### 12 Zhou and colleagues

**Zhou, Y., Liu, H., Srivastava, T., Mei, H., & Tan, C. (2024).** Hypothesis generation with large language models. *NLP4Science*. [Author manuscript](https://arxiv.org/abs/2404.04326); [proceedings paper](https://aclanthology.org/anthology-files/pdf/nlp4science/2024.nlp4science-1.10.pdf). **Source:** R16, HypoGeniC. **Placement:** Introduction, automated hypothesis generation.

**What it supports:** HypoGeniC iteratively generates and updates hypotheses from labeled examples, evaluated through predictive performance. It establishes a concrete data-informed approach to automated hypothesis generation.

**Gap and our contribution:** Predictive usefulness and coverage of plausible scientific proposals are different outcomes. Our measures could complement performance evaluation, but we have not evaluated HypoGeniC itself.

**Suggested use:** “Data-driven systems can generate hypotheses that improve prediction (Zhou et al., 2024). Such performance tests leave a separate question about the breadth of candidate explanations, which motivates our set-level evaluation.”

**Method implication:** A data-enriched generation condition would test whether narrowing persists when models receive evidence beyond a call and publication summaries. Current results cannot be generalized to iterative evidence-updating systems without that comparison.


### 13 Liu and colleagues

**Liu, H., Zhou, Y., Li, M., Yuan, C., & Tan, C. (2025).** Literature meets data: A synergistic approach to hypothesis generation. *Proceedings of ACL, Volume 1: Long Papers*, 245–281. [ACL record](https://aclanthology.org/2025.acl-long.12/). **Source:** R16. **Placement:** Introduction, literature- and data-informed hypothesis generation. **Correction:** the review’s “Li, Li & Tan” is not the author list of this paper.

**What it supports:** Integrating literature and data improves hypothesis generation relative to the evaluated baselines and can help people on the tested decision tasks. It supports richer grounding as a substantive design choice.

**Gap and our contribution:** Our study asks about set coverage, but its prompting conditions do not implement this literature-plus-data system. This paper therefore also strengthens the reviewer’s input-information-asymmetry objection.

**Suggested use:** In Discussion/limitations: “Literature- and data-grounded generation can improve hypothesis usefulness (Liu et al., 2025). Our results apply to the elicitation conditions tested here; whether richer evidence recovers underrepresented ideas remains open.”

**Further analysis:** Add a grounded condition with matched literature/data access and evaluate both quality and diversity. Do not describe persona publication abstracts as equivalent to this method.


### 14 The AI Scientist

**Lu, C., Lu, C., Lange, R. T., Foerster, J., Clune, J., & Ha, D. (2024).** The AI Scientist: Towards fully automated open-ended scientific discovery. arXiv:2408.06292. [Author manuscript](https://arxiv.org/abs/2408.06292). **Source:** R17. **Placement:** Introduction, end-to-end automated science. The two first authors are Chris Lu and Cong Lu.

**What it supports:** The AI Scientist implements a pipeline from ideation through experiments, manuscript preparation, and simulated review. This makes the generation-plus-evaluation question concrete.

**Gap and our contribution:** Producing viable individual papers does not by itself establish breadth across the generated portfolio. Our measures suggest additional evaluation dimensions, not a direct assessment of this system’s performance.

**Suggested use:** “Systems that automate both research production and review (Lu et al., 2024) make the diversity of candidate ideas and assessments jointly relevant. We examine these two stages in a common grant setting.”

**Limit:** Our study evaluates stages separately and reviews human proposals; it does not estimate compounding losses in an actual end-to-end pipeline or show that this particular system narrows science.


### 15 The AI Scientist v2

**Yamada, Y., Lange, R. T., Lu, C., Hu, S., Lu, C., Foerster, J., Clune, J., & Ha, D. (2025).** The AI Scientist-v2: Workshop-level automated scientific discovery via agentic tree search. arXiv:2504.08066. [Author manuscript](https://arxiv.org/abs/2504.08066). **Source:** R17. **Placement:** Introduction and Discussion, automation at scale. Here the two Lu authors are Cong Lu and Chris Lu, in that order.

**What it supports:** Agentic tree search and iterative experimentation provide a more adaptive automation architecture than independent prompting, with demonstrated workshop-level output. This supports the practical stakes of automated discovery and a meaningful alternative to the current design.

**Gap and our contribution:** Our coverage metrics could evaluate whether branching search produces distinct directions, but independent calls and persona prompts do not test tree search.

**Suggested use:** “Adaptive systems already explore research through branching experiments (Yamada et al., 2025). Whether that exploration expands the effective diversity of ideas is a separate evaluation question from whether an individual paper clears a review threshold.”

**Further analysis:** Compare diversity at matched proposal count and computational budget across independent generation and adaptive search. Treat this as future work, not a result of the present study.


### 16 Agents4Science

**Bianchi, F., Queen, O., Thakkar, N., Sun, E., & Zou, J. (2025).** Exploring the use of AI authors and reviewers at Agents4Science. arXiv:2511.15534. [Author manuscript](https://arxiv.org/abs/2511.15534). **Source:** R18/R39/R67/R69. **Placement:** Introduction opening and Discussion, generation and review in one pipeline. **Attribution clarification:** the review calls this “Zou et al.”; Bianchi is first author. The source describes humans as co-authors and co-reviewers, so “entirely AI” needs qualification.

**What it supports:** Agents4Science provides an actual setting with AI as primary authors and reviewers and humans as co-authors/co-reviewers. It motivates examining generation and evaluation together.

**Gap and our contribution:** Our comparison supplies an expert human grant baseline and coverage/variation measures for both stages. It does not establish how decisions at Agents4Science would change under a different review panel.

**Suggested use:** In the Introduction: “Venues involving AI in both authorship and reviewing make diversity at both stages an immediate evaluation concern (Bianchi et al., 2025).” In Discussion, propose comparing marginal information from additional model reviews before interpreting a larger panel as more independent evidence.

**Limit:** Do not call the event entirely autonomous or claim its averaging procedure failed on the strength of our separate grant experiment.


### 17 aiXiv

**Zhang, P., et al. (2025).** aiXiv: A next-generation open access ecosystem for scientific discovery generated by AI scientists. arXiv:2508.15126. [Author manuscript and full author list](https://arxiv.org/abs/2508.15126). **Source:** R18. **Placement:** Introduction, publication and review infrastructure for automated science.

**What it supports:** aiXiv proposes infrastructure for submission, review, and iterative refinement by human and AI scientists. Cite it as an example of mechanisms that could scale production and evaluation together.

**Gap and our contribution:** Improvement of individual submissions through iteration does not answer whether the resulting portfolio covers diverse directions. Our proposed evaluation adds breadth and reviewer redundancy to item-level assessments.

**Suggested use:** “Infrastructure for iterative AI-supported submission and review (Zhang et al., 2025) makes it possible to scale scientific feedback; evaluating that scale also requires asking what additional ideas and assessments it contributes.”

**Limit:** We have not run this platform, evaluated its users, or tested its iterative refinement architecture. Avoid presenting the paper as evidence that aiXiv exhibits double compression.


## Automated review and human review baselines

### 18 Liang and colleagues on useful feedback

**Liang, W., et al. (2024).** Can large language models provide useful feedback on research papers? A large-scale empirical analysis. *NEJM AI, 1*(8), AIoa2400196. [Author manuscript](https://arxiv.org/abs/2310.01783); [published DOI](https://doi.org/10.1056/AIoa2400196). **Source:** R10. **Placement:** Introduction/Result C, individual review usefulness versus panel independence.

**What it supports:** GPT-4 feedback overlaps with human reviewers’ points and is perceived as useful by many researchers. This supports a positive role for author-facing assistance, rather than a blanket dismissal of AI review.

**Gap and our contribution:** Useful feedback from one model output and useful diversity across a panel are different questions. Our within-proposal comparisons ask whether several model reviews supply distinct assessments, even if they collectively resemble human review content.

**Suggested use:** “AI feedback can raise points found in human reviews and be useful to authors (Liang et al., 2024). We ask a complementary question: when multiple AI reviews are assembled into a panel, how much variation do additional reviews contribute?”

**Limit:** Semantic redundancy is a proxy for reduced informational diversity, not proof of statistical dependence of errors or reduced decision accuracy. [Evidence](https://arxiv.org/abs/2310.01783).


### 19 Liang and colleagues on review text

**Liang, W., et al. (2024).** Monitoring AI-modified content at scale: A case study on the impact of ChatGPT on AI conference peer reviews. *ICML*. [Author manuscript and full author list](https://arxiv.org/abs/2403.07183). **Source:** R11. **Placement:** Introduction, existing AI involvement in peer review.

**What it supports:** Corpus-level estimation finds substantial LLM modification of review text. Use it to establish that AI already participates in the review process, not just in speculative future deployments.

**Gap and our contribution:** Detecting textual involvement does not reveal whether judgments were delegated to models or whether panel diversity changed. Our known-provenance generated reviews permit a direct output comparison under specified prompts.

**Suggested use:** “LLM-modified language is already detectable in conference reviewing (Liang et al., 2024), but prevalence alone does not reveal what happens when models supply the assessments themselves. We compare model-generated and human reviews of the same proposals.”

**Limit:** The reported percentages estimate modified text at corpus level; do not translate them into a verified percentage of fully automated reviewers. Our grant study does not estimate adoption prevalence.


### 20 Baumann and colleagues

**Baumann, J., Pei, J., Koyejo, S., & Hovy, D. (2026).** Position: Stop automating peer review without rigorous evaluation. *Proceedings of the 43rd International Conference on Machine Learning, PMLR 306*, 169349–169380. [Proceedings](https://proceedings.mlr.press/v306/baumann26a.html). **Source:** R12. **Placement:** Introduction/Discussion, evaluation criteria for automated review. This updates the review’s arXiv-only citation to the proceedings version.

**What it establishes:** This is direct empirical prior art: it compares human and AI paper reviews, includes controlled reviewer simulations, and documents excessive similarity and vulnerability to rewriting. It also examines criticism-focused sections and score behavior.

**Gap and our contribution:** Claiming that review convergence or controlled AI review is new would be untenable. Our defensible extension is confidential grant proposals, matched human panels, and a common framework connecting review variation to proposal-set coverage. Criticism concentration should be presented as related evidence, not automatically a first finding.

**Suggested use:** “AI review homogenization has been documented in conference reviewing (Baumann et al., 2026). We examine its expression in grant assessment alongside a distinct question: which parts of the human proposal space AI generation covers.”

**Method connection:** Compare their intra-paper similarity metric with our spread measure. Our normalized/raw comparison addresses presentation sensitivity but does not test adversarial robustness. [Evidence: §§3–4 and appendices](https://arxiv.org/html/2605.03202v2).


### 21 Pier and colleagues

**Pier, E. L., et al. (2018).** Low agreement among reviewers evaluating the same NIH grant applications. *PNAS, 115*(12), 2952–2957. [Article and full author list](https://pmc.ncbi.nlm.nih.gov/articles/PMC5866547). **Source:** R13/R33/R53. **Placement:** Introduction/Result C, human review disagreement; dataset positioning. The study supports discussion of low agreement, rather than an unrestricted claim that human panels “maximally” disagree.

**What it supports and complicates:** Human reviewers can disagree substantially about the same grant. This establishes an empirical baseline, but disagreement can reflect unreliability as well as complementary expertise.

**Gap and our contribution:** We compare semantic variation and scores within proposals. We cannot infer that all additional human variation improves selection.

**Suggested use:** Before Result C or in Discussion: “Low agreement is a documented feature of grant review (Pier et al., 2018). Our comparison asks how AI changes the variation among assessments, while leaving open which disagreements are informative rather than noise.”

**Further analysis:** Code whether unique criticisms identify valid flaws, obtain independent adjudication, or evaluate downstream outcomes. Those tests would connect diversity to useful judgment. Avoid using this citation to claim that maximal disagreement is desirable or that human decisions are ground truth.


## Collective judgment and algorithmic monoculture

### 22 Kleinberg and Raghavan

**Kleinberg, J., & Raghavan, M. (2021).** Algorithmic monoculture and social welfare. *PNAS*. [Published article](https://doi.org/10.1073/pnas.2018340118); [author manuscript](https://arxiv.org/abs/2101.05853). **Source:** R28/R65. **Placement:** Discussion, correlated decision systems and collective outcomes.

**What it supports:** The formal model shows that shared algorithms can reduce collective welfare even when individually more accurate. This justifies separating individual accuracy from system-level performance.

**Gap and our contribution:** We observe concentration and review similarity in science funding, but do not estimate the theorem’s welfare outcome or establish its assumptions in this setting.

**Suggested use:** “Theoretical work shows that individually accurate algorithms need not yield better collective outcomes when decision-makers rely on the same system (Kleinberg and Raghavan, 2021). Our results motivate evaluating a related risk in scientific funding: whether scale preserves distinct candidates and assessments.”

**Limit:** Describe our study as evidence relevant to the theory, not a direct empirical verification of its theorem. A funding-allocation experiment with outcome measures would be needed for the stronger claim.


### 23 Bommasani and colleagues

**Bommasani, R., Creel, K. A., Kumar, A., Jurafsky, D., & Liang, P. (2022).** Picking on the same person: Does algorithmic monoculture lead to outcome homogenization? *NeurIPS*. [Author manuscript](https://arxiv.org/abs/2211.13972). **Source:** R29. **Placement:** Discussion, shared models and outcome homogenization.

**What it supports:** Shared components can homogenize which people receive adverse outcomes; effects depend on how foundation models are adapted. This motivates examining both common model infrastructure and intervention-specific differences.

**Gap and our contribution:** Their outcome homogenization concerns shared decisions; our main evidence concerns text/idea variation. Similar reviews do not automatically imply identical errors or exclusions.

**Suggested use:** “Shared AI components can align downstream outcomes, although adaptation choices matter (Bommasani et al., 2022). We assess an earlier manifestation of convergence: how much variation models provide in proposals and reviews.”

**Further analysis:** Compare which proposals are rejected across models and against independently assessed merit. This would test whether semantic convergence corresponds to systematic exclusion. It is not established by pooling reviews or reporting their average distance.


### 24 Hong and Page

**Hong, L., & Page, S. E. (2004).** Groups of diverse problem solvers can outperform groups of high-ability problem solvers. *PNAS, 101*(46), 16385–16389. [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC528939/). **Source:** R30. **Placement:** Discussion, collective benefits of diversity.

**What it supports:** Under specified conditions, diversity in problem-solving approaches can outweigh superior individual ability. This supports considering complementarity alongside item quality.

**Gap and our contribution:** Our embedding-based measures quantify difference in outputs, not the functional heuristic diversity in their model. We do not show that our more diverse proposal set solves problems better.

**Suggested use:** “Models of collective problem solving explain why diverse approaches can contribute value beyond individual ability (Hong and Page, 2004). This motivates measuring the range of scientific candidates rather than ranking each proposal in isolation.”

**Limit:** Cite in Discussion as theoretical motivation. To claim a performance benefit here, link proposal diversity to independently measured scientific outcomes; the theorem does not validate Vendi as a measure of scientific value.


### 25 Lorenz and colleagues

**Lorenz, J., Rauhut, H., Schweitzer, F., & Helbing, D. (2011).** How social influence can undermine the wisdom of crowd effect. *PNAS, 108*, 9020–9025. [Author-hosted published paper](https://www.sg.ethz.ch/publications/2011/lorenz2011how-social-influence/PNAS-2011-Lorenz-9020-5.pdf). **Source:** R30. **Placement:** Discussion, aggregation and nonindependent judgments.

**What it supports:** In an estimation experiment, social influence reduced opinion diversity and could undermine the wisdom-of-crowds benefit. This supplies an analogy for why many judgments may add less information when they converge.

**Gap and our contribution:** Repeated model sampling is not human social influence, and our reviewers were not experimentally induced to influence one another. Our study measures a different source of convergence.

**Suggested use:** “The benefit of aggregating judgments depends on how they are generated: social influence can erode crowd diversity (Lorenz et al., 2011). Analogously, larger AI panels should be evaluated for the additional information their reviews supply.”

**Limit:** Use “analogously,” not a causal transfer. Testing panel-size gains against independently assessed outcomes would be stronger than equating semantic similarity with correlated errors.


## Systems and contextual sources

These are systems, institutional documentation, or news, rather than research-paper citations. Access date for checked sites: November 10, 2026. Their presence does not independently verify every usage statistic or performance claim in the original review.

### 26 Refine

**Refine.** AI verification platform. [Official site](https://www.refine.ink/). **Source:** R08. **Placement:** Introduction, institutional use of AI-assisted technical review. The current site identifies use by journals including those of the AEA and Econometric Society; the review’s benchmark win rate and founder details require their own supporting source if used.

**What it supports:** The service documents practical deployment of AI technical checking. This makes an opening claim about review assistance concrete.

**Gap and our contribution:** A tool finding technical errors differs from a committee allocating funding. Our review findings motivate asking which tasks can be assisted without replacing complementary expert judgments.

**Suggested use:** “AI tools are being deployed for technical verification of manuscripts (Refine). Their usefulness for specific checks leaves open how best to preserve the diversity of judgments involved in selecting research.”

**Limit:** Treat the website as deployment documentation, not independent evidence of accuracy, fairness, or superiority. Our study does not evaluate Refine. In Discussion, distinguish scalable verification from autonomous selection rather than treating all uses as interchangeable.


### 27 OpenAIReview

**OpenAIReview.** Open AI-assisted reviewing project. [Project site](https://openaireview.org/); [project statement](https://openaireview.org/blog.html). **Source:** R09. **Placement:** Introduction, tools for accessible feedback. **Status update:** the linked March 2026 project statement is signed Chenhao Tan. Cite that statement for its argument and authorship; a formal lab affiliation is not needed for the proposed use below.

**What it supports:** Chenhao Tan’s project statement argues for accessible, customizable AI review and emphasizes improved review precision under submission growth. It supplies a constructive alternative viewpoint, not just another tool name.

**Gap and our contribution:** Our set-level evaluation asks what scaling review adds beyond throughput and individual usefulness. It does not refute the case for open, author-facing assistance.

**Suggested use:** “Open review tools seek to broaden access to feedback and make review assistance customizable (Tan, 2026). Our results suggest that such systems should also be evaluated for complementary assessments across repeated reviews.”

**Method implication:** Open prompts enable testing Matt’s proposal for reviewers with distinct evaluation criteria. This is a proposed intervention, not evidence that OpenAIReview fails. [Project statement, March 2026, signed Chenhao Tan](https://openaireview.org/blog.html).


### 28 NeurIPS reviewing experiment

**NeurIPS (2026).** AI-assisted reviewing experiment. [Official experiment page](https://nips.cc/Conferences/2026/ai-reviewing-experiment). **Source:** R12. **Placement:** Introduction/Discussion, current review evaluation practice. This is an experiment announcement, not evidence of completed experimental outcomes.

**What it supports:** An official experiment studies how human reviewers interact with AI assistance. This establishes active institutional experimentation and distinguishes assistance from substitution.

**Gap and our contribution:** Our AI-generated panels do not measure how human reviewers use, reject, or revise AI suggestions. We can propose diversity and redundancy as additional outcomes for human–AI experiments.

**Suggested use:** “Institutional experiments in AI-assisted reviewing are underway (NeurIPS, 2026). Alongside review quality, evaluations should examine whether assistance changes the range of concerns expressed across reviewers.”

**Limit:** The announcement supplies no completed result. Do not cite it as showing harm or benefit, and do not claim our fully generated reviews predict effects on assisted human reviewers.


### 29 Hutson news feature

**Hutson, M. (2026, September 1).** Bland new world: Is AI making us all think the same? *Nature, 657*, 22–24. [News feature](https://www.nature.com/articles/d41586-026-02682-3). **Source:** R31. **Placement:** Optional Introduction/Discussion context. Cite underlying research for empirical claims.

**What it supports:** The feature establishes a public scientific debate about homogenization across expression and cognition. It is useful for a short opening motivation or an optional Discussion bridge to broader stakes.

**Gap and our contribution:** Move from a general concern to a concrete question about the distribution of proposals and assessments entering funding. This is a framing move, not an empirical gap proven by a news feature.

**Suggested use:** “Concern that generative AI may homogenize expression extends to scientific practice (Hutson, 2026). Grantmaking offers a setting in which to examine the range of ideas proposed and the assessments applied to them.”

**Limit:** Cite original studies for findings and methods; do not use the feature to establish priority or novelty. It may be omitted if the research citations already make the opening clear.


## Citation leads and resolved policy source

### 30 Reviewer3

**Reviewer3 / r3.** R07 names “reviewer3.ai, Khalil & Reed.” **Placement:** Introduction and Result C framing. [Site supplied by the reviewer](https://reviewer3.ai). The site could not be retrieved during checking. Preserve this as a system lead; confirm the creators, exact source, and claimed usage numbers before citing.

**Potential use once verified:** A service advertising a review panel could illustrate why panel size must be distinguished from distinct evaluative contributions. Insert it in the Introduction only after establishing precisely how the service generates its reviews.

**Gap and possible contribution:** Our data motivate measuring marginal information from additional AI reviews, but do not establish whether this service uses a single model, multiple models, specialists, or human checks.

**Conditional wording:** “Services offering multiple AI reviews raise a practical evaluation question: how much distinct information does each additional review contribute?” Add a verified service citation before use.

**Limit:** No validated empirical claim or manuscript-ready factual citation can be assigned to this unresolved lead. Avoid the automated review’s assertion that this particular panel is one voice sampled five times.


### 31 Creative scar lead

**Moon et al., “creative scar.”** R26 supplies no title, year, or identifier and describes persistence two months after AI exposure. **Placement:** Optional Discussion, persistent homogenization. A search returned a paper titled *Creative scar without generative AI: Individual creativity fails to sustain while homogeneity keeps climbing*, but the match to Moon and the particular two-month claim was not confirmed from a primary source. Do not assign that paper to Moon without checking.

**Potential use once identified:** A verified longitudinal study could motivate concern that effects persist after AI assistance ends. That would belong in the Discussion, after reporting the immediate output comparison.

**Gap and our contribution:** Our one-period generated-output study cannot fill the persistence gap. It can motivate a follow-up in which scientists generate ideas before exposure, during assistance, and after withdrawal.

**Conditional wording:** “Whether exposure produces lasting changes in scientists’ subsequent idea generation remains an important question.” This can stand as a future-work question without a citation; attach the intended study only after its identity and follow-up interval are confirmed.

**Limit:** Do not state that our effects persist, or that Moon established the quoted two-month effect, from the available lead.


### 32 NIH originality notice

**National Institutes of Health (2025).** Supporting fairness and originality in NIH research applications. NOT-OD-25-132. [Official notice](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-132.html). **Source:** R39/R67. **Placement:** Introduction opening, potentially paired with Agents4Science. **Status update:** identified and verified; released July 17, 2025, effective for applications submitted to the September 25, 2025 receipt date and beyond.

**What it supports:** NIH’s notice explicitly addresses originality and the burden of AI-enabled application volume. This supplies a documented institutional reason to examine more than production speed. [Official notice NOT-OD-25-132](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-132.html).

**Gap and our contribution:** The policy sets expectations; it is not evidence that AI proposals are scientifically inferior. Our study examines diversity under specified generation conditions without evaluating the policy’s effectiveness.

**Suggested use:** “NIH has raised concerns about originality and the review burden associated with AI-enabled application production (NIH, 2025). These concerns motivate asking whether greater proposal volume expands the range of ideas available for selection.”

**Limit:** This is a source for a historical policy statement, not legal advice or a claim about current compliance. The notice was released July 17, 2025; distinguish that from its September 25, 2025 effective date.


### 33 Julio and Brian science pieces

**“end-to-end science pieces by Julio and Brian and other works.”** Draft-body note B02, Introduction paragraph 2. **Original wording:** “(Cite end-to-end science pieces by Julio and Brian and other works)”. No title/year is supplied; the intended pieces cannot be uniquely identified from this folder.

**Potential use:** These pieces would support the Introduction’s description of which scientific stages can be automated, or a Discussion account of how stages interact. The exact works are needed before assigning findings to them.

**Gap and our contribution:** If they describe end-to-end capability, the bridge is from demonstrated throughput to unmeasured portfolio breadth and distinct assessment. Do not assume they omit diversity before reading them.

**Conditional wording:** “As automation connects idea generation with evaluation, performance at each stage must be assessed both individually and collectively.” Attach the intended pieces only after identification.

**Limit:** Lu, Yamada, and Bianchi provide identified alternatives for specific claims, but should not silently replace the collaborators’ intended works.


### 34 Science editorial lead

**Unspecified Science editorial.** Draft-body note B03, Introduction paragraph 3. **Original wording:** “(I would cite Science editorial here)”. No title, author, or date is supplied. Do not assume it is Hao et al., which is a Nature research article.

**Potential use:** An editorial can frame the stakes of scientific productivity, originality, or AI governance. It cannot substitute for the underlying empirical study of output or topic breadth.

**Gap and our contribution:** Once identified, separate its argument from its cited evidence. Our contribution would be an empirical comparison of candidate sets and assessments, rather than proof of an editorial’s broader diagnosis.

**Conditional wording:** “Debate about AI’s role in science raises questions about what increased production preserves or loses.” Use only if the editorial actually makes this argument.

**Limit:** The specific source remains unidentified. Do not attach quantitative productivity claims or the Hao findings to a guessed Science editorial.


### 35 Ottino and Uzzi placeholder

**Ottino and Uzzi placeholder.** Draft-body note B07, Result B, Distinctive edges. **Original wording:** “(Uzzi et al. 2Ottino 20XX)”. This appears to be a corrupted or unfinished citation; title and year need clarification. The adjacent “Uzzi et al. 2013; Tian et al. 2025” are existing draft citations, not unambiguous new recommendations.

**Potential use:** An identified study of unconventional combinations or breakthrough ideas could motivate asking whether AI misses unusual directions, after the geometry result in Result B or in Discussion.

**Gap and our contribution:** We establish relative position in one embedding and proposal set. We do not establish that peripheral proposals are unconventional in the cited work’s sense, or that they will yield breakthroughs.

**Conditional wording:** “The loss of distinctive proposals raises a question about which opportunities are excluded; distinctiveness here should not be equated with future scientific impact.”

**Further analysis:** Connect human-edge status to expert novelty ratings, combinations of prior literature, and subsequent outcomes. Until the corrupted citation is resolved, do not use it to label the center incremental and the edge revolutionary.


### 36 Style and semantic measurement

**Style and semantic measurement citation.** Draft-body B08, Robustness checks, Style and embedding: “(NEED CITATION HERE)”. The note supplies no specific reference. It seeks support for distinguishing idea effects from style effects; the general linguistic homogenization literature does not automatically validate the particular normalization procedure.

**Method argument needing support:** Raw and rewritten texts provide a sensitivity comparison, not a clean experimental separation of wording and ideas unless rewriting preserves the relevant content.

**How to use the identified literature:** Cite reference 10 to motivate presentation sensitivity, then describe our normalization procedure and audit it empirically. Cite the actual metric/model papers separately for the mathematical and embedding choices.

**Suggested wording:** “We compare original and normalized texts to assess sensitivity to presentation; agreement across branches increases confidence that results are not specific to the original wording.”

**Gap to fill:** Validate retention of hypotheses, methods, caveats, and reviewer concerns; test another normalizer and embedding. Avoid saying that persistence after rewriting proves a purely idea-level effect. This is a validation task as well as a citation gap.


### 37 Grant system citations

**Unspecified grant-system citations.** Draft-body B01, Introduction paragraph 1: “(citations)”. Supports the claim about grants shaping discoveries, beneficiaries, and scientists’ careers; no specific reference is named.

**Argument needing support:** Grants influence which projects can proceed, but effects on discoveries, beneficiaries, and careers are separate claims requiring suitable evidence.

**How to use it:** Narrow the opening to the selection mechanism, then add specific studies if retaining claims about downstream outcomes. Qian provides funding-specific context, but should not bear every causal claim about science and careers.

**Suggested wording:** “Grant competitions select which proposed projects receive resources. We study how AI changes the range of proposals and assessments available to that selection process.”

**Gap and our contribution:** Our outputs characterize the candidate and assessment stages, not the eventual causal effects of awards. Linking these changes to resource allocation or discoveries requires a downstream study; the current paper should identify that question rather than claim to resolve it.


## Research briefing accompanying the linguistic diversity study

### 38 Sourati and Dehghani research briefing

**Sourati, Z., & Dehghani, M. (2026).** AI writing assistants shrink linguistic diversity and blur personal identity. *Nature Human Behaviour, 10*, 1869–1870. Research briefing; published online August 24, 2026. [Local briefing](<../literature/ai shrinks liguistic diversity.pdf>). **Source:** user-supplied PDF. This is a two-page summary of reference 10, with author commentary and an editorial note.

**What it supports:** An accessible account of why stylistic variance matters for interpreting texts and recovering author attributes. It summarizes the observational trends, rewriting experiment, and trait-inference analyses of the primary study.

**Where and how to use it:** Optional Introduction or Discussion framing of the stakes of linguistic homogenization. Use the full paper for numerical claims, methods, and evidentiary support. There is generally no need to cite both for the same empirical sentence.

**Gap and our contribution:** The briefing raises broader concerns about thought and reasoning; it does not separately test scientific idea generation or grant selection. Our paper can ask whether narrowing extends to candidate scientific content and assessment diversity. It should not treat a concern expressed in the briefing as proof of cognitive or scientific harm.

**Suggested wording:** “The implications of homogenized expression extend to how information is inferred from text (Sourati and Dehghani, 2026). In grant assessment, this motivates checking whether apparent similarity reflects shared prose, shared scientific content, or shared evaluative concerns.”

**Limit:** Its account of retained meaning does not validate our Gemini normalization. Its observational account explicitly acknowledges concurrent changes and its experiments focus on polishing. Do not count the briefing and full paper as two studies supporting the same claim.

## Citation gaps without named recommendations

R78 asks to fill every citation placeholder. The draft also has unresolved method citations for mean pairwise distance, Vendi, Simpson, close-neighbor evenness, style normalization, BioLinkBERT, and persona conditioning, plus Discussion placeholders for ensemble decision making, jury models, monoculture, and deliberative disagreement. The named collective-judgment references above address some of the latter cluster. The methods placeholders remain literature-selection tasks; no new methods paper has been silently substituted for a reviewer’s recommendation.

The draft already names Meincke et al. 2024 and De Freitas et al. 2025 in its persona overview, and Si et al. 2024 in its Introduction. These are existing incomplete author–year citations, not additional works uniquely specified by the feedback. They should be reconciled with the eventual bibliography when the citation placeholders are resolved.

## Suggested sequence for the literature argument

1. Establish the practical setting with a small number of concrete systems or deployments: Lu/Yamada for research production and Bianchi or the NeurIPS experiment for review. These establish relevance, not harms.
2. Introduce the individual-versus-collective evaluation problem with Doshi and Hao. Acknowledge Ashkinaze and the model-dependent result in Padmakumar so the argument is conditional rather than universal.
3. Specify the closest prior art separately for each stage: Qian for proposal positioning, Wenger for cross-model homogeneity, and Baumann for review convergence. State what each already establishes before introducing the grant-specific question.
4. Present the study’s contribution as a comparison of human-relative proposal coverage and assessment variation under a common funding task. Explain the core/edge measure, matched set sizes, and within-proposal review comparison. Do not portray human-versus-AI source as the only difference in access to information or incentives.
5. Interpret the results with Liang’s useful-feedback finding and Pier’s disagreement finding: useful reviews can be redundant, but varied reviews can also be noisy. Diversity is an evaluation dimension, not a substitute for quality.
6. Use Kleinberg, Bommasani, Hong, and Lorenz selectively to explain why collective evaluation matters. Close with the tests needed to connect coverage and variation to quality, allocation, and executed science. The theory motivates these tests; it does not supply their missing outcomes.
