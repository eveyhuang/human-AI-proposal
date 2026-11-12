# Scientific idea measurement and generation methods

Research checked November 12, 2026. This focused review addresses two decisions for Double compression: how to compare the scientific content of proposals below the whole-document level, and which generation strategies provide a credible test of the current core-and-edge finding. It contains 20 references, distinguishing published work from preprints. The proposed adaptations below are study-design recommendations, not results from the new agency data.

The recommended combination is **a proposal representation that retains scientific components, their relationships, and source passages; separate measures of component and combination coverage; and a literature-grounded generation comparison that explicitly tests recombination and novelty checking**. Citation-based novelty should provide an additional perspective, rather than define the idea or serve as its quality score.

## Decisions supported by the literature

| Decision | Recommended starting point | Why it fits this project |
|---|---|---|
| Represent scientific content | CoreSC and SciClaim, with a proposal-specific extension | Separate scientific roles and preserve claims, qualifications, and proposed versus established knowledge |
| Compare particular components | ASPIRE-style aspect matching, validated on proposals | Distinguish shared questions from shared methods without requiring a whole-document match |
| Identify combinations | Luo et al.; document-level relations illustrated by SciREX | Test whether familiar components are present but their scientific connections are missing |
| Strengthen generation | Scideator-inspired recombination plus bounded SciMON-style novelty checking | Directly challenges the possibility that current generation fails to search for alternative scientific combinations |
| Add bibliometric evidence | Uzzi et al.; Wang et al.; Shi and Evans | Distinguish unusual knowledge combinations, disciplinary breadth, and content novelty |
| Preserve a useful control | Literature-grounded ordinary generation with the same source packet | Separate benefits of added information from benefits of the recombination procedure |

## What the Gu and Krenn paper establishes

**1. Gu, X., & Krenn, M. (2026). Generating interesting scientific ideas using knowledge graphs and LLMs: Evaluations with 100 research group leaders. PNAS, 123(46), e2611349123.** [Journal DOI](https://doi.org/10.1073/pnas.2611349123). Published November 9, 2026. Relevant locations in the supplied PDF: pp. 2–4, graph and generation design; pp. 6–7, expert ratings and graph-feature associations.

SciMuse constructs a concept co-occurrence graph from titles and abstracts, augmented with citation and temporal information. Personalized research context supplies candidate combinations for staged generation and self-critique. The study recorded 4,451 ratings from 110 research group leaders. Crucially, supplying graph-selected concept pairs did not improve expert-rated interest over the titles-only GPT baseline. Interest, predicted citation impact, feasibility, and novelty are distinct targets.

**Use in this paper:** motivate controlled changes in the concepts offered to a generator, and analysis of the properties of generated combinations. Do not cite it as establishing that knowledge graphs necessarily improve ideas or as a method that already extracts hypotheses and contribution arguments. Its graph connections represent co-occurrence, not typed scientific relationships such as a method testing a hypothesis.

Two adaptations are especially important. First, its frequency filtering can exclude rare or emerging concepts; an edge study should preserve such terms and audit their extraction. Second, its titles-only condition still uses a structured critique-and-revision procedure. It should not be described as an entirely unstructured one-shot comparison. A call-specific, modest literature collection is sufficient for our pilot; reproducing a graph covering tens of millions of papers is unnecessary.

## Extracting and comparing scientific components

**2. Liakata, M., Teufel, S., Siddharthan, A., & Batchelor, C. (2010). Corpora for the Conceptualisation and Zoning of Scientific Papers. LREC 2010.** [Paper and metadata](https://aclanthology.org/L10-1440/). Published conference paper; see Table 1 for CoreSC and Table 2 for AZ-II.

CoreSC distinguishes scientific roles including motivation, goal, hypothesis, method, model, observation, result, and conclusion; AZ-II captures rhetorical relationships to other work. **Adopt:** a distinction between background, proposed work, and intended contribution. **Adapt:** proposals contain plans and expected outcomes, so an anticipated finding must not become an established result. Sentence labels locate relevant passages but do not by themselves identify unique ideas or establish novelty.

**3. Luan, Y., He, L., Ostendorf, M., & Hajishirzi, H. (2018). Multi-Task Identification of Entities, Relations, and Coreference for Scientific Knowledge Graph Construction. EMNLP, 3219–3232.** [Paper](https://aclanthology.org/D18-1360/). Published; §3 describes SciERC.

SciERC/SciIE combines entity typing, relationships, and coreference: a method can be linked to the task for which it is used. **Adopt:** preserve typed connections and resolve repeated mentions, rather than count keywords. **Adapt:** its computer-science-oriented categories require testing in agency domains. Its graph aggregation also illustrates a danger for this project: frequency filtering and keeping only a dominant relation can erase precisely the rare scientific distinctions under investigation.

**4. Jain, S., van Zuylen, M., Hajishirzi, H., & Beltagy, I. (2020). SciREX: A Challenge Dataset for Document-Level Information Extraction. ACL, 7506–7516.** [Paper](https://aclanthology.org/2020.acl-main.670/). Published; §3.1 and Fig. 1.

SciREX extracts linked dataset–metric–task–method tuples across sections and distinguishes salient contributions from incidental mentions. **Adopt:** relations can span a proposal, and the components of one aim must stay linked. **Adapt:** a tuple designed around machine-learning results is not a general proposal ontology. For multiple aims, do not form every possible question–method pairing: that would invent scientific combinations unsupported by the text.

**5. Magnusson, I., & Friedman, S. (2021). Extracting Fine-Grained Knowledge Graphs of Scientific Claims: Dataset and Transformer-Based Results. EMNLP, 4651–4658.** [Paper](https://aclanthology.org/2021.emnlp-main.381/). Published; schema and examples in the main paper.

SciClaim represents causal, comparative, predictive, statistical, and proportional associations, including qualifications and evidence. **Adopt:** preserve direction, uncertainty, conditions, and the difference between association and causation. These distinctions can separate ideas that share all their major nouns. **Adapt:** extracting a claimed association neither verifies its truth nor establishes that it is new. Proposed hypotheses need an explicit status distinguishing them from the paper's reported findings.

**6. Mysore, S., Cohan, A., & Hope, T. (2022). Multi-Vector Models with Textual Guidance for Fine-Grained Scientific Document Similarity. NAACL, 4453–4470.** [Paper](https://aclanthology.org/2022.naacl-main.331/). Published; ASPIRE, especially §§2–3.

ASPIRE represents sentence-level aspects and learns aspect matching using co-citation contexts; it includes single-match and multiple-match approaches. **Adopt:** compare particular scientific aspects as a complement to whole-document embeddings. **Adapt:** matching any one aspect can overstate equivalence of complete proposals. Validate question, hypothesis, and approach matches separately, then require compatible relationships for an idea-level match. A published paper-similarity benchmark does not validate performance on these grant proposals.

## Characterizing novelty and the shape of the edge

**7. Luo, Z., Lu, W., He, J., & Wang, Y. (2022). Combination of research questions and methods: A new measurement of scientific novelty. Journal of Informetrics, 16(2), 101282.** [Publisher](https://www.sciencedirect.com/science/article/pii/S1751157722000347); [DOI](https://doi.org/10.1016/j.joi.2022.101282). Published. Publisher abstract and indexed methodological passages were accessible; a complete full-text methodological audit remains necessary before reproducing its formulas.

This work measures question novelty, method novelty, and question–method combinations using temporal, frequency, and semantic information. **Adopt:** distinguish a new question, a new approach, and a new pairing. **Adapt:** its term-based measures should be supplemented with proposal-level meaning and expert validation. This is a direct precedent for decomposing the edge; the contribution here must be what the decomposition reveals about generation and expert assessment.

**8. Uzzi, B., Mukherjee, S., Stringer, M., & Jones, B. (2013). Atypical combinations and scientific impact. Science, 342(6157), 468–472.** [Author-hosted article](https://www.kellogg.northwestern.edu/faculty/uzzi/htm/papers/Science-2013-Uzzi-468-72.pdf); [DOI](https://doi.org/10.1126/science.1240474). Published; journal pp. 469–470.

Referenced-journal pair atypicality separates a paper's conventional foundation from its unusual combinations. **Adopt:** examine whether proposals retain common scientific ingredients while introducing a small number of unusual connections. **Adapt:** journal combinations are coarse proxies for intellectual combinations. They do not show that a cited method is actually used or that a hypothesis is original. The association with later impact does not establish the value of an individual omitted proposal.

**9. Wang, J., Veugelers, R., & Stephan, P. (2017). Bias against novelty in science: A cautionary tale for users of bibliometric indicators. Research Policy, 46(8), 1416–1436.** [Journal DOI](https://doi.org/10.1016/j.respol.2017.06.006); [author working paper](https://www.nber.org/papers/w22180). Published journal version; the NBER version is dated 2016.

The measure concerns first-time referenced-journal combinations and the difficulty of those combinations. **Adopt:** distinguish previously unseen combinations from merely uncommon ones. **Adapt:** absence from an incomplete reference corpus means “not observed in this corpus,” not new to science. The study also motivates separating short-run recognition from novelty; eventual citations should not be used as though they were available to applicants at the deadline.

**10. Shi, F., & Evans, J. (2023). Surprising combinations of research contents and contexts are related to impact and emerge with scientific outsiders from distant disciplines. Nature Communications, 14, 1641.** [Article](https://www.nature.com/articles/s41467-023-36741-4). Published; model and methods sections.

This work distinguishes unexpected combinations of scientific contents from combinations of contexts, using a hypergraph model. **Adopt:** separately examine what scientific concepts are connected and which disciplinary communities are drawn together. **Adapt:** content novelty and disciplinary distance need not coincide. A within-field mechanism can be unusual, while a broadly interdisciplinary bibliography can support a conventional proposal. A large hypergraph model is an optional later extension, not a prerequisite for the pilot.

**11. Stirling, A. (2007). A general framework for analysing diversity in science, technology and society. Journal of the Royal Society Interface, 4(15), 707–719.** [Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC2373389/); [DOI](https://doi.org/10.1098/rsif.2007.0213). Published.

The framework separates variety, balance, and disparity. **Adopt:** distinguish missing kinds of ideas, unequal representation of existing kinds, and reduced differences among them. **Adapt:** diversity among cited fields is not automatically novelty, coherence, or scientific value. Treat this as a conceptual foundation for decomposing shrinkage, not as a single score that resolves all three properties.

**12. Arts, S., Melluso, N., & Veugelers, R. (2025). Beyond Citations: Measuring Novel Scientific Ideas and their Impact in Publication Text. The Review of Economics and Statistics, advance publication, 1–33.** [Journal DOI](https://doi.org/10.1162/rest_a_01561); [author manuscript](https://arxiv.org/abs/2309.16437). Journal status reported in the author record; the accessible manuscript is v4, December 2024.

The approach tracks new words, noun phrases, and combinations, separately from their subsequent reuse. **Adopt:** separate novelty at submission from later uptake and compare content-based signals with citation-based ones. **Adapt:** lexical emergence can reflect new naming rather than a new scientific argument. Use this as a complementary historical signal; preserve scientific equivalence across synonymous terms and control for text length.

## Generating stronger scientific ideas

**13. Wang, Q., Downey, D., Ji, H., & Hope, T. (2024). SciMON: Scientific Inspiration Machines Optimized for Novelty. ACL, 279–299.** [Paper](https://aclanthology.org/2024.acl-long.18/). Published; framework and retrieval/iteration sections.

SciMON retrieves scientific inspirations and revises suggestions against prior literature to improve novelty. **Adopt:** a bounded novelty-checking stage with an explicit comparison to the closest prior work. **Adapt:** its task supplies a background problem; a funding call may leave the problem itself open. Include variation in the research question, not only alternative solutions to a fixed question. Novelty relative to retrieved literature remains conditional on retrieval coverage.

**14. Baek, J., Jauhar, S. K., Cucerzan, S., & Hwang, S. J. (2025). ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models. NAACL, 6709–6738.** [Paper](https://aclanthology.org/2025.naacl-long.342/). Published; method and prompt appendices, especially Tables 6–8.

ResearchAgent separates problem identification, method development, and experiment design, with literature grounding and iterative reviewing agents. **Adopt:** retain intermediate scientific content and locate where narrowing appears. **Adapt:** agent critique is a generation mechanism, not an independent scientific evaluator. Assess the resulting ideas using held-out human judgments and measures that were not the agent's optimization target.

**15. Radensky, M., Shahid, S., Fok, R., Siangliulue, P., Hope, T., & Weld, D. S. (2026). Scideator: Human-LLM Compound System for Scientific Ideation through Facet Recombination and Novelty Evaluation. ACM CAIS, 348–374.** [Published DOI](https://doi.org/10.1145/3786335.3813161); [author version](https://arxiv.org/html/2409.14634). Published; the older 2024 preprint has a different title. See §2 and Appendix H.

Scideator uses purpose, mechanism, and evaluation facets, controlled-distance retrieval, and novelty verification. **Adopt:** deliberate combinations of scientific roles. **Adapt:** its evidence concerns human–AI interaction; an autonomous adaptation is a new condition, not a replication of that result. Its short facet labels are useful for navigation but insufficient as the sole record of a nuanced grant hypothesis. Retain supporting passages and richer descriptions for measurement.

**16. Pu, K., Feng, K. J. K., Grossman, T., Hope, T., Dalvi Mishra, B., Latzke, M., Bragg, J., Chang, J. C., & Siangliulue, P. (2025). IdeaSynth: Iterative Research Idea Development Through Evolving and Composing Idea Facets with Literature-Grounded Feedback. CHI, Article 145.** [DOI](https://doi.org/10.1145/3706598.3714057); [author version](https://arxiv.org/html/2410.04025). Published; §4 and Appendix I.

IdeaSynth supports iterative development of problem, solution, evaluation, and contribution facets. **Adopt:** assess whether an initially distinctive idea survives elaboration into a detailed proposal. **Adapt:** its user studies concern assisted human ideation, not autonomous substitution for applicant populations. It is especially relevant to the existing idea-to-full-proposal expansion stage, where a generic template could flatten specificity.

**17. Si, C., Yang, D., & Hashimoto, T. (2025). Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers. ICLR.** [Published proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ea94957d81b1c1caf87ef5319fa6b467-Abstract-Conference.html); [author manuscript](https://arxiv.org/abs/2409.04109). Published; idea-generation and diversity analyses.

The study reports higher expert-rated novelty for generated ideas in its comparison while identifying limited generation diversity and unreliable model self-evaluation. **Adopt:** separate the novelty of a selected idea from coverage of a portfolio. **Adapt:** archive the raw generation pool as well as selected outputs; deduplication and ranking change the distribution being evaluated. This paper is evidence against treating individual novelty and collective diversity as interchangeable.

**18. Yang, Z., Du, X., Li, J., Zheng, J., Poria, S., & Cambria, E. (2024). Large Language Models for Automated Open-domain Scientific Hypotheses Discovery. Findings of ACL, 13545–13565.** [Paper](https://aclanthology.org/2024.findings-acl.804/). Published; MOOSE framework.

MOOSE develops open-domain hypothesis generation with multiple feedback mechanisms, evaluated in a social-science setting. **Adopt:** generate explicit explanatory propositions and revise them using relevant evidence. **Adapt:** expert judgments of plausibility or usefulness are not experimental confirmation. The domain and task differ from complete agency proposals, making this a secondary comparator rather than the first system to implement.

**19. Wang, W., Gu, L., Zhang, L., Luo, Y., Dai, Y., Shen, C., Xie, L., Lin, B., He, X., & Ye, J. (2024; revised 2025). SciPIP: An LLM-based Scientific Paper Idea Proposer. arXiv:2410.23166.** [Author paper](https://arxiv.org/html/2410.23166). Preprint status used here; conference acceptance was not verified. See §§3.1–3.3.

SciPIP combines semantic, keyword, and citation-related retrieval with brainstorming and literature-based generation paths. **Adopt:** combine independently motivated ideas with literature-grounded inspirations. **Adapt:** search quality and source coverage become part of the intervention. Citation recovery or agreement with existing papers does not establish broad coverage of valuable alternatives. A small controlled retrieval comparison is more informative here than reproducing its entire infrastructure.

## A close new comparison for positioning

**20. Tang, Y., & Yang, Y. (2026). AI Research Agents Narrow Scientific Exploration. arXiv:2605.27905v2, July 11.** [Version inspected](https://arxiv.org/html/2605.27905v2). Preprint; a peer-reviewed venue was not verified. Relevant sections: §§2–4, particularly §4.6 and SI §S2.4.

This is a close comparison: it studies concentration across generation frameworks and separates research questions from methods relative to seed papers. **Implication:** neither agent-based concentration nor question/method decomposition should be claimed as unique. Its annotation validation uses agreement among LLMs; novelty relative to a small seed set also differs from novelty relative to the literature. Our proposed advance is validated omissions in real call-matched applicant populations, connected to specific expert judgments. Distinguish the updated version from earlier search summaries.

## Proposed representation for the proposal study

Use a flexible record for each substantive aim, retaining the original wording and its section or page. Multiple aims should produce multiple linked records. This is our proposed synthesis, not a schema already validated by the cited papers.

| Field | What to preserve | Important distinction |
|---|---|---|
| Research question or objective | The specific uncertainty or goal | Broad topic versus actual question |
| System and scope | Organism, population, setting, scale, boundary conditions | Same question in a materially different setting |
| Hypothesis or proposed explanation | Claimed relationship, mechanism, direction, qualifications | Optional for descriptive, theoretical, or design work |
| Proposed approach | Method, intervention, comparison, data, model | Mentioning a method versus using it to answer this question |
| Discriminating evidence | What observation, analysis, or evaluation would resolve the uncertainty | A proposed test versus an asserted future finding |
| Intended contribution | What would become known or possible | Author's novelty claim versus independently assessed novelty |
| Relationships | Which method addresses which question or tests which explanation | Preserve linked aims rather than invent all pairwise combinations |
| Provenance and status | Exact supporting passage; location; proposed, prior, or demonstrated | Unsupported extraction must remain missing or uncertain |

Do not enforce a hypothesis on every proposal. Do not infer a missing mechanism to make an incomplete proposal appear coherent. Preserve uncommon terms rather than forcing everything into a vocabulary learned from frequent concepts. Store canonical labels alongside the original phrases, so scientific distinctions can be recovered when normalization over-merges them.

The same extraction process should operate on human and AI proposals. Generated structured fields are useful process records but cannot automatically serve as ground truth while human texts undergo a noisy extractor. Compare both origins through the same blinded measurement procedure; separately examine agreement with the generator's planned structure.

## Three measurements to prioritize

### Component coverage

For held-out human proposals, measure whether an equally sized AI pool covers their questions, approaches, and hypotheses separately. Compare with a human reference pool on those same targets. Calibrate semantic equivalence through expert judgments rather than exact wording. Track misses in rare terminology to detect extractor-induced compression.

### Combination coverage

Ask whether at least one candidate preserves the relevant scientific connection: for example, this hypothesis tested by this approach in this system. Finding the question in one AI proposal and the method in another establishes component availability, not recovery of the linked idea. Compare combinations among proposals whose components are individually represented, while reporting the size and selection of this conditional subset.

This yields a testable possibility: AI covers many scientific ingredients but less often connects them in the ways represented by human applicants. A negative result is also informative: the edge may instead arise from missing questions, specialized evidence, or different scientific exploration.

### Historical atypicality and expert meaning

Use a dated external literature reference to describe whether the missing connection is unusual historically. Separately use call-local rarity to describe whether it is unusual among that call's applicants. These are different reference populations and should not share the label “novel” without qualification.

Then link the omitted feature to expert assessments: whether it was recognized, judged original, considered promising, or criticized for feasibility or validity. Annotate contribution features independently of the reviews before measuring reviewer recognition. A funded proposal is institutionally selected, not automatically scientifically superior; a rare proposal may be weak or out of scope.

When estimating excess AI omission at edges, define rarity independently of the match being tested and compare equal-sized AI and human sets. Repeated splits improve stability but do not create independent observations. Calls and call families, rather than every pairwise distance, should structure uncertainty. Evaluate valid AI-only directions as well as human-relative omissions.

## How to use citations without confusing the constructs

Three distinct objects are often called a knowledge graph: a network of papers linked by citations, a network of concepts linked by co-occurrence, and a graph of typed scientific claims. The first two provide history and retrieval; the third describes what a proposal actually argues. They can complement each other without being interchangeable.

For proposals with reliable bibliographies, resolve references to real publications and date them. Compute bibliographic atypicality using only historical information. A literature corpus with restricted coverage cannot establish an absolute first-ever combination. Report unresolved references and corpus limitations rather than assigning missing records a novelty score of zero.

Do not equate citing distant fields with integrating their knowledge. Link important citations to the scientific role they play: background, adopted method, motivating limitation, or competing explanation. Bibliographic diversity and content novelty should remain separate variables. Bibliography length and field-specific citation practice also require attention.

For AI outputs, fabricated or irrelevant citations must never count as distant scientific connections. Prefer citations to identifiable items in the provided literature collection, and validate that they support the claimed role. Keep generated bibliographic behavior as a separate outcome from scientific-content coverage.

Citations received by a paper are an impact-related quantity; references made by a proposal describe its intellectual inputs. Future citations and future uptake cannot enter an ex ante novelty score or a historical generation packet. Later outcomes may support a separately labeled retrospective analysis.

## A defensible generation comparison

The present batch, independent-request, and persona conditions test meaningful variations, but do not exhaust published approaches to scientific ideation. The draft's inference that persistence under persona implies the result is unlikely to be a prompting artifact is too strong. The supported statement is that narrowing persists under those tested conditions.

Use the following four conditions on development calls before selecting the confirmatory comparison:

| Condition | Inputs and process | Question answered |
|---|---|---|
| G0 Current independent baseline | Original call, criteria, and existing idea-to-proposal workflow, with input leakage removed | How does the original result reproduce? |
| G1 Literature-grounded control | Same generation steps as G0, plus a fixed, documented literature packet | How much does additional relevant information help? |
| G2 Structured recombination | Same packet; explicit alternative questions and approaches; controlled combinations; bounded novelty checking | Does directed scientific exploration improve coverage beyond ordinary use of the information? |
| G3 Strong alternative workflow | Same initial packet and search permissions; staged problem, method, and experiment development with critique | Does the conclusion survive another credible published design family? |

G2 is a proposed adaptation of published components. G3 can draw on ResearchAgent. They should be described as adaptations unless the actual published implementation and settings are reproduced. Scideator and IdeaSynth include human interaction; removing it creates an autonomous condition and does not inherit their user-study results.

For G1 versus G2, equalize the initial source packet, permitted retrieval, output length, revision opportunities, and inference budget as closely as possible. Include a budget-matched version of G1 with generic revision when G2 uses additional revision calls. One clean small experiment changes only generic critique versus explicit recombination/novelty critique. A separate comparison changes the retrieval strategy. If several components change together, interpret the effect as that of the whole procedure.

Construct literature packets from the public call and documented field searches, with team publications added only in a separately identified expertise condition. Do not derive generation inputs from held-out proposal text, target titles, their private reference lists, expert reviews, or funding outcomes. A target-informed task is possible, but would answer a different question. The existing persona-card title leakage should be removed before reuse, and publication eligibility verified against the call deadline.

Preserve near and more distant relevant sources, and test retrieval distance as a design choice. Broadening inputs need not monotonically improve relevance or scientific value. A historical cutoff on explicit retrieval cannot remove later knowledge already encoded in model weights; these remain retrospective current-model comparisons.

Archive every candidate, revision, rejection, and selection. Do not discard duplicates from the main diversity analysis. Report both raw-pool and selected-portfolio behavior if the method ranks or deduplicates ideas. Equal final output counts can hide very different search budgets, so also report coverage against total generated candidates and cost.

The generator's novelty checker must not be the sole final evaluator, and evaluation cannot consist only of the score optimized during generation. Use independent experts and an alternative representation. Test scientific coherence, feasibility, and call relevance alongside coverage so incoherent combinations do not count as successful recovery. No finite set of prompts proves a universal model limitation; it can establish robustness across explicit, credible procedures and information conditions.

## A pilot that narrows the next decision

An illustrative development pilot would use 10–15 calls spanning several scientific areas and call types. Approximately 100–150 human and generated proposals, plus sampled matched and unmatched pairs, could support an initial annotation exercise; these are workload examples, not a power calculation. Reserve other call families for confirmation.

1. **Validate extraction first.** Have two appropriately qualified annotators mark substantive aims, supporting passages, and scientific relationships on an overlapping sample. Measure missing content, unsupported additions, and agreement separately for human versus AI texts and common versus rare features.
2. **Validate equivalence.** Compare judgments on paraphrases and scientifically changed examples. A good measure should tolerate stylistic changes while detecting a changed hypothesis, causal direction, method, or scope. Use naturally occurring pairs as well as audited perturbations.
3. **Test G0–G2 before committing to G3 at scale.** Use the same calls and models. Diagnose whether extra information, explicit recombination, or later expansion changes coverage. Keep intervention tuning away from the confirmation calls.
4. **Inspect the apparent edge scientifically.** Sample omissions and matches across rarity levels, including possible AI-only contributions. Link independently identified features to review passages and their reasoning.
5. **Choose the claim from the outcome.** Recovery with G1 implicates information access; additional recovery with G2 implicates the search procedure; poor extraction of rare features implicates measurement. Persistent validated combination omissions under stronger procedures support the narrower scientific-coverage claim.

Prioritize the annotation guide and the common-information G1–G2 comparison. Defer a global knowledge graph, a large autonomous-agent implementation, and a single composite novelty index until the pilot shows that they resolve a specific uncertainty. The most useful next result would explain **which scientific distinctions are missing, which generation changes recover them, and how experts understood their significance**.
