"""
Prompt templates for study generation and evaluation workflows.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """Container for prompt template information"""
    name: str
    description: str
    template: str
    parameters: List[str] = None
    version: str = "v1"

class PromptManager:
    """Manager for different prompt templates"""
    
    def __init__(self):
        """Initialize with default prompt templates"""
        self.templates = self._create_default_templates()

    def _create_default_templates(self) -> Dict[str, PromptTemplate]:
        """Create default prompt templates"""
        templates = {}


        templates['generate_ideas_minimal_batch'] = PromptTemplate(
            name="Generate Research Ideas (minimal batch)",
            description="Generate a batch of diverse research ideas without persona grounding",
            
            template="""
            You are generating research ideas that will most likely be accepted by
            the competitive funding call from NCEMS (National Synthesis Center for
            Emergence in Molecular and Cellular Sciences).

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            TASK:
            Generate exactly {num} research ideas that are aligned with the
            research call and are clearly different from each other.

            For each idea, provide:
            - **Title**: Clear, specific, and scientifically precise
            - **Abstract** (400-600 words) 

            IMPORTANT: Format your response as a valid JSON object:
            {{
              "research_ideas": [
                {{
                  "title": "Specific Research Title Here",
                  "abstract": "Detailed 400-600 word abstract addressing all requirements above..."
                }},
                {{
                  "title": "Another Specific Research Title",
                  "abstract": "Detailed 400-600 word abstract addressing all requirements above..."
                }}
              ]
            }}

            Ensure the JSON is properly formatted and valid.
            """,
            parameters=['research_call', 'information_about_ncems', 'num'],
            version='v2'
        )

        templates['generate_ideas_minimal_single'] = PromptTemplate(
            name="Generate Research Ideas (minimal single)",
            description="Generate exactly one research idea without persona grounding",

            template="""
            You are generating one research idea that will most likely be
            accepted by the competitive funding call from NCEMS (National
            Synthesis Center for Emergence in Molecular and Cellular Sciences).

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            TASK:
            Generate exactly one research idea aligned with the research call.
            This call should be treated as one independent draw, not as part of a
            list that must be diversified relative to other unseen ideas.

            Provide:
            - **Title**: Clear, specific, and scientifically precise
            - **Abstract**: 400-600 words

            IMPORTANT: Format your response as a valid JSON object:
            {{
              "research_ideas": [
                {{
                  "title": "Specific Research Title Here",
                  "abstract": "Detailed 400-600 word abstract addressing all requirements above..."
                }}
              ]
            }}

            Ensure the JSON is properly formatted and valid.
            """,
            parameters=['research_call', 'information_about_ncems'],
            version='v1'
        )

        templates['generate_ideas_persona_single'] = PromptTemplate(
            name="Generate Research Ideas (persona single)",
            description="Generate exactly one research idea while drawing on the factual scientific perspective of a human author team",

            template="""
            You are generating one research idea that will most likely be
            accepted by the competitive funding call from NCEMS (National
            Synthesis Center for Emergence in Molecular and Cellular Sciences).

            For this task, adopt the scientific perspective of the human
            research team described below.
            This means you should let the team's publication record shape:
            - what problems seem important
            - what biological systems, scales, or phenomena stand out
            - what kinds of methods, data, and synthesis approaches feel natural
            - what kinds of cross-domain connections this team would be well positioned to notice

            Adopt the team's scientific perspective, but NOT their writing
            style, tone, or personal biography.

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            INFORMATION ABOUT THE MEMBERS IN THE TEAM:
            {persona_card_json}

            TASK:
            Generate exactly one new research idea aligned with the research
            call.

            IMPORTANT INSTRUCTIONS:
            - Use the persona card as factual scientific grounding for the
              team's domains, systems, methods, data types, and recurring
              research questions.
            - Adopt only the scientific perspective implied by the publication
              record, not the authors' prose style or personal voice.
            - Do not copy titles, phrases, hypotheses, or paper-specific claims
              from the persona card.
            - Do not simply restate an existing paper topic.
            - Generate a NEW idea that is plausible for a team with these
              scientific backgrounds.
            - The idea should clearly reflect the perspective in the persona
              card.
            - Whenever possible, integrate signals from multiple team members
              rather than defaulting to only one author.
            - Ground the idea in at least two concrete elements from the
              persona card, such as domains, biological systems, methods, data
              types, or recurring scientific questions.
            - Preserve the NCEMS requirement that the project must be synthesis
              research using existing publicly available data.

            Provide:
            - **Title**: Clear, specific, and scientifically precise
            - **Abstract** (400-600 words)

            IMPORTANT: Format your response as a valid JSON object:
            {{
              "research_ideas": [
                {{
                  "title": "Specific Research Title Here",
                  "abstract": "Detailed 400-600 word abstract addressing all requirements above..."
                }}
              ]
            }}

            Ensure the JSON is properly formatted and valid.
            """,
            parameters=['research_call', 'information_about_ncems', 'team_members', 'persona_card_json'],
            version='v1'
        )

        templates['generate_ideas_minimal'] = templates['generate_ideas_minimal_batch']
        templates['generate_ideas_persona'] = templates['generate_ideas_persona_single']

        templates['generate_proposals_minimal'] = PromptTemplate(
            name="Generate Research Proposals Minimal",
            description="Generate comprehensive research proposals based on title and abstract",
            template="""
            Write a comprehensive research proposal based on the provided title
            and abstract, ensuring it aligns with NCEMS funding requirements.

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            RESEARCH IDEA TO EXPAND:
            Title: {title}
            Abstract: {abstract}

            Create a proposal meeting the highest standards for scientific rigor, clarity, and feasibility. Include these sections with specified word counts:

            1. BACKGROUND AND SIGNIFICANCE (500 words)

            2. RESEARCH QUESTIONS AND HYPOTHESES (500 words)

            3. METHODS AND APPROACH (500 words)

            4. EXPECTED OUTCOMES AND IMPACT (300 words)

            5. OPEN SCIENCE AND REPRODUCIBILITY (300 words)

            6. BUDGET AND RESOURCES (300 words)

            RESPONSE FORMAT: Return ONLY valid JSON:
            {{
              "proposal": {{
                "title": "{title}",
                "abstract": "{abstract}",
                "background_and_significance": "...",
                "research_questions_and_hypotheses": "...",
                "methods_and_approach": "...",
                "expected_outcomes_and_impact": "...",
                "open_science_and_reproducibility": "...",
                "budget_and_resources": "..."
              }}
            }}

            IMPORTANT:
            - Each section must be substantive, detailed, and meet word counts
            - Ensure the JSON is properly formatted and valid
            """,
            parameters=['title', 'abstract', 'research_call', 'information_about_ncems'],
            version='v2'
        )

        templates['generate_proposals_persona_minimal'] = PromptTemplate(
            name="Generate Research Proposals Persona Minimal",
            description="Generate comprehensive research proposals while preserving persona-grounded scientific perspective",
            template="""
            Write a comprehensive research proposal based on the provided title
            and abstract, ensuring it aligns with NCEMS funding requirements.

            Preserve the scientific perspective implied by the human research
            team described below, but do NOT imitate their personal prose style,
            biography, or idiosyncratic phrasing.

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            PERSONA CONTEXT:
            {persona_card_json}

            RESEARCH IDEA TO EXPAND:
            Title: {title}
            Abstract: {abstract}

            Create a proposal meeting the highest standards for scientific
            rigor, clarity, and feasibility. Include these sections with
            specified word counts:

            1. BACKGROUND AND SIGNIFICANCE (500 words)
            2. RESEARCH QUESTIONS AND HYPOTHESES (500 words)
            3. METHODS AND APPROACH (500 words)
            4. EXPECTED OUTCOMES AND IMPACT (300 words)
            5. OPEN SCIENCE AND REPRODUCIBILITY (300 words)
            6. BUDGET AND RESOURCES (300 words)

            IMPORTANT INSTRUCTIONS:
            - Use the persona card only as factual scientific grounding for
              domains, systems, methods, data types, and recurring research
              questions.
            - Do not copy language from the persona card.
            - Keep the proposal clearly centered on synthesis research using
              existing publicly available data.

            RESPONSE FORMAT: Return ONLY valid JSON:
            {{
              "proposal": {{
                "title": "{title}",
                "abstract": "{abstract}",
                "background_and_significance": "...",
                "research_questions_and_hypotheses": "...",
                "methods_and_approach": "...",
                "expected_outcomes_and_impact": "...",
                "open_science_and_reproducibility": "...",
                "budget_and_resources": "..."
              }}
            }}

            IMPORTANT:
            - Each section must be substantive, detailed, and meet word counts
            - Ensure the JSON is properly formatted and valid
            """,
            parameters=['title', 'abstract', 'research_call', 'information_about_ncems', 'persona_card_json'],
            version='v1'
        )

        templates['eval_ncems_criteria_batch5'] = PromptTemplate(
            name="NCEMS Criteria Evaluation Batch 5",
            description="Generate five structured NCEMS reviews for one proposal in a single response",
            template="""
            You are an expert scientific reviewer evaluating a research proposal
            for the following funding call:

            {research_call}

            PROPOSAL TO EVALUATE:
            ID: {proposal_id}
            Title: {proposal_title}
            Abstract: {proposal_abstract}
            Full Proposal: {proposal_full}

            TASK:
            Generate exactly 5 independent reviews of this proposal. Each review
            should read like it was written by a distinct reviewer, but all five
            must still be grounded in the proposal text and NCEMS evaluation
            criteria.

            For each review, provide:
            - review_text
            - strengths
            - weakness
            - overall_numeric_score (1-5)
            - overall_summary
            - relevance_to_emergent_phenomena_score and justification
            - novelty_and_significance_score and justification
            - rigor_of_approach_score and justification
            - scope_and_timeline_score and justification
            - synthesis_focus_score and justification
            - data_identification_score and justification
            - open_science_commitment_score and justification

            IMPORTANT:
            - Return valid JSON only.
            - Return exactly 5 review objects.
            - Do not wrap the response in markdown.

            RESPONSE FORMAT:
            {{
              "reviews": [
                {{
                  "review_text": "...",
                  "strengths": "...",
                  "weakness": "...",
                  "overall_numeric_score": 4,
                  "overall_summary": "...",
                  "relevance_to_emergent_phenomena_score": 4,
                  "relevance_to_emergent_phenomena_justification": "...",
                  "novelty_and_significance_score": 4,
                  "novelty_and_significance_justification": "...",
                  "rigor_of_approach_score": 4,
                  "rigor_of_approach_justification": "...",
                  "scope_and_timeline_score": 4,
                  "scope_and_timeline_justification": "...",
                  "synthesis_focus_score": 4,
                  "synthesis_focus_justification": "...",
                  "data_identification_score": 4,
                  "data_identification_justification": "...",
                  "open_science_commitment_score": 4,
                  "open_science_commitment_justification": "..."
                }}
              ]
            }}
            """,
            parameters=['research_call', 'proposal_id', 'proposal_title', 'proposal_abstract', 'proposal_full'],
            version='v1'
        )

        templates['eval_ncems_criteria_single'] = PromptTemplate(
            name="NCEMS Criteria Evaluation Single",
            description="Generate one structured NCEMS review for one proposal",
            template="""
            You are an expert scientific reviewer evaluating a research proposal
            for the following funding call:

            {research_call}

            PROPOSAL TO EVALUATE:
            ID: {proposal_id}
            Title: {proposal_title}
            Abstract: {proposal_abstract}
            Full Proposal: {proposal_full}

            TASK:
            Generate exactly 1 independent review of this proposal.

            Provide:
            - review_text
            - strengths
            - weakness
            - overall_numeric_score (1-5)
            - overall_summary
            - relevance_to_emergent_phenomena_score and justification
            - novelty_and_significance_score and justification
            - rigor_of_approach_score and justification
            - scope_and_timeline_score and justification
            - synthesis_focus_score and justification
            - data_identification_score and justification
            - open_science_commitment_score and justification

            IMPORTANT:
            - Return valid JSON only.
            - Return exactly 1 review object.
            - Do not wrap the response in markdown.

            RESPONSE FORMAT:
            {{
              "reviews": [
                {{
                  "review_text": "...",
                  "strengths": "...",
                  "weakness": "...",
                  "overall_numeric_score": 4,
                  "overall_summary": "...",
                  "relevance_to_emergent_phenomena_score": 4,
                  "relevance_to_emergent_phenomena_justification": "...",
                  "novelty_and_significance_score": 4,
                  "novelty_and_significance_justification": "...",
                  "rigor_of_approach_score": 4,
                  "rigor_of_approach_justification": "...",
                  "scope_and_timeline_score": 4,
                  "scope_and_timeline_justification": "...",
                  "synthesis_focus_score": 4,
                  "synthesis_focus_justification": "...",
                  "data_identification_score": 4,
                  "data_identification_justification": "...",
                  "open_science_commitment_score": 4,
                  "open_science_commitment_justification": "..."
                }}
              ]
            }}
            """,
            parameters=['research_call', 'proposal_id', 'proposal_title', 'proposal_abstract', 'proposal_full'],
            version='v1'
        )

        templates['eval_ncems_criteria_persona_single'] = PromptTemplate(
            name="NCEMS Criteria Evaluation Persona Single",
            description="Generate one structured NCEMS review while adopting a reviewer persona card",
            template="""
            You are an expert scientific reviewer evaluating a research proposal
            for the following funding call:

            {research_call}

            Adopt the scientific review perspective implied by the reviewer
            persona card below, but do not imitate a personal writing style or
            biography.

            REVIEWER PERSONA:
            {reviewer_persona_card_json}

            PROPOSAL TO EVALUATE:
            ID: {proposal_id}
            Title: {proposal_title}
            Abstract: {proposal_abstract}
            Full Proposal: {proposal_full}

            TASK:
            Generate exactly 1 independent review of this proposal from the
            scientific perspective implied by the reviewer persona.

            Provide:
            - review_text
            - strengths
            - weakness
            - overall_numeric_score (1-5)
            - overall_summary
            - relevance_to_emergent_phenomena_score and justification
            - novelty_and_significance_score and justification
            - rigor_of_approach_score and justification
            - scope_and_timeline_score and justification
            - synthesis_focus_score and justification
            - data_identification_score and justification
            - open_science_commitment_score and justification

            IMPORTANT:
            - Return valid JSON only.
            - Return exactly 1 review object.
            - Do not wrap the response in markdown.

            RESPONSE FORMAT:
            {{
              "reviews": [
                {{
                  "review_text": "...",
                  "strengths": "...",
                  "weakness": "...",
                  "overall_numeric_score": 4,
                  "overall_summary": "...",
                  "relevance_to_emergent_phenomena_score": 4,
                  "relevance_to_emergent_phenomena_justification": "...",
                  "novelty_and_significance_score": 4,
                  "novelty_and_significance_justification": "...",
                  "rigor_of_approach_score": 4,
                  "rigor_of_approach_justification": "...",
                  "scope_and_timeline_score": 4,
                  "scope_and_timeline_justification": "...",
                  "synthesis_focus_score": 4,
                  "synthesis_focus_justification": "...",
                  "data_identification_score": 4,
                  "data_identification_justification": "...",
                  "open_science_commitment_score": 4,
                  "open_science_commitment_justification": "..."
                }}
              ]
            }}
            """,
            parameters=['research_call', 'proposal_id', 'proposal_title', 'proposal_abstract', 'proposal_full', 'reviewer_persona_card_json'],
            version='v1'
        )
        

        # Human Criteria Evaluation
        templates['eval_ncems_criteria'] = PromptTemplate(
            name="NCEMS Criteria Evaluation",
            description="Evaluate proposal based on human reviewer criteria with detailed scoring",
            template="""You are an expert scientific reviewer evaluating a research proposal for the following funding call:

            {research_call}

            You have been asked to evaluate the following research proposal submitted in response to this call.

            **PROPOSAL TO EVALUATE:**
            ID: {proposal_id}
            Title: {proposal_title}
            Abstract: {proposal_abstract}
            Full Proposal: {proposal_full}

            Your task is to provide a detailed evaluation of this proposal based on the following criteria:

            **EVALUATION CRITERIA:**

            **1. Scientific Merit and Innovation**

            **1a. Relevance to Emergent Phenomena**
            Does the research explicitly address emergent phenomena at the mesoscale in molecular/cellular biosciences?
            - 1 = Not relevant; does not address emergent phenomena
            - 2 = Minimally relevant; tangential connection to emergent phenomena
            - 3 = Moderately relevant; addresses emergent phenomena but not as central focus
            - 4 = Highly relevant; emergent phenomena is a key focus
            - 5 = Exceptionally relevant; directly and explicitly addresses mesoscale emergent phenomena

            **1b. Novelty & Significance**
            Are the questions and approaches innovative? Do they have potential to advance knowledge?
            - 1 = Not novel; incremental work with limited significance
            - 2 = Somewhat novel; modest advancement expected
            - 3 = Novel; clear advancement in the field
            - 4 = Highly novel; significant potential to advance knowledge
            - 5 = Groundbreaking; transformative potential for the field

            **1c. Rigor of Approach**
            Is the proposed methodology clear, logical, and grounded in established or emerging research practices?
            - 1 = Poor; unclear or illogical methodology
            - 2 = Fair; methodology has significant gaps or concerns
            - 3 = Good; solid methodology with minor concerns
            - 4 = Very good; clear, logical, and well-grounded methodology
            - 5 = Excellent; exceptionally rigorous and well-justified approach

            **2. Feasibility**

            **2a. Scope & Timeline**
            Are the goals and milestones realistic for the proposed time frame and planned approach?
            - 1 = Unrealistic; goals are unattainable within proposed timeline
            - 2 = Questionable; significant concerns about feasibility
            - 3 = Reasonable; achievable with noted challenges
            - 4 = Realistic; well-planned scope and timeline
            - 5 = Highly feasible; excellent planning with contingencies

            **3. Data Sources and Limitations**

            **3a. Synthesis Focus**
            Does the proposal clearly demonstrate a synthesis project?
            - 1 = No synthesis; appears to be primarily generating new data
            - 2 = Minimal synthesis; mostly new data generation with some integration
            - 3 = Moderate synthesis; balanced between existing and new data
            - 4 = Strong synthesis; primarily uses existing data with clear integration plan
            - 5 = Exemplary synthesis; exclusively uses existing data with comprehensive integration

            **3b. Data Identification**
            Are the data sources explicitly identified, and are limitations appropriately acknowledged?
            - 1 = Poor; data sources vague and limitations not addressed
            - 2 = Fair; some data sources identified but incomplete or limitations ignored
            - 3 = Good; data sources identified and basic limitations acknowledged
            - 4 = Very good; clear data sources with thoughtful discussion of limitations
            - 5 = Excellent; comprehensive data source specification with thorough limitation analysis

            **4. Open Science Compliance**

            **4a. Open Science Commitment**
            Does the proposal demonstrate a commitment to open, team, and reproducible science principles?
            - 1 = No commitment; does not address open science
            - 2 = Minimal commitment; vague statements without concrete plans
            - 3 = Moderate commitment; some open science practices mentioned
            - 4 = Strong commitment; clear plans for open and reproducible science
            - 5 = Exemplary commitment; comprehensive open science framework with detailed implementation

            IMPORTANT: Return your evaluation as a valid JSON object with the following structure:

            {{
            "evaluation": {{
                "proposal_id": "{proposal_id}",
                "criteria_scores": [
                {{
                    "category": "Scientific Merit and Innovation",
                    "subcriteria": [
                    {{
                        "criterion": "Relevance to Emergent Phenomena",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }},
                    {{
                        "criterion": "Novelty & Significance",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }},
                    {{
                        "criterion": "Rigor of Approach",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }}
                    ],
                    "category_average": <average of subcriteria scores, rounded to 1 decimal>
                }},
                {{
                    "category": "Feasibility",
                    "subcriteria": [
                    {{
                        "criterion": "Scope & Timeline",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }}
                    ],
                    "category_average": <score from subcriterion>
                }},
                {{
                    "category": "Data Sources and Limitations",
                    "subcriteria": [
                    {{
                        "criterion": "Synthesis Focus",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }},
                    {{
                        "criterion": "Data Identification",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }}
                    ],
                    "category_average": <average of subcriteria scores, rounded to 1 decimal>
                }},
                {{
                    "category": "Open Science Compliance",
                    "subcriteria": [
                    {{
                        "criterion": "Open Science Commitment",
                        "score": <1-5>,
                        "justification": "<1-2 sentence explanation for this score>"
                    }}
                    ],
                    "category_average": <score from subcriterion>
                }}
                ],
                "overall_rating": {{
                    "final_numeric_score": <average of all category averages, rounded to 1 decimal>,
                    "narrative_summary": "<One or two paragraphs explaining key strengths and areas for improvement>"
                }}
            }}
            }}

            Provide ONLY the JSON output above with no additional text before or after.""",
            parameters=['research_call', 'proposal_id', 'proposal_title', 'proposal_abstract', 
                       'proposal_full']
        )

        # Novelty-only Evaluation (with literature context and web search)
        templates['eval_novelty'] = PromptTemplate(
            name="Novelty Evaluation",
            description="Evaluate proposal novelty across six dimensions grounded in prior research, using relevant literature abstracts as context and web search when needed",
            template="""You are an expert research evaluator. Evaluate the NOVELTY of the following research proposal using six dimensions grounded in prior research on originality and proposal review.

You have access to a web search tool. Use it when you need to verify specific factual claims about the state of the art, check whether a method or dataset already exists, or assess how established a particular approach is—but only when the proposal text alone is insufficient to make an informed judgment.

**RELEVANT LITERATURE CONTEXT:**
The following three papers are the closest literature neighbors to this proposal (retrieved by semantic similarity). Use them as evidence of what is already known in this area when judging novelty.

{lit_neighbors}

**Important evaluation rules:**
1. Evaluate only based on the information in the proposal text provided below. Do not use outside knowledge about the field unless explicitly included in the proposal or retrieved via web search.
2. Judge how strongly the proposal MAKES A CASE for novelty, not whether the proposal is definitely novel in the real world.
3. For each dimension, assign a score from 1–5 and provide concise reasoning grounded in specific evidence from the proposal.
4. When possible, cite short phrases or paraphrase concrete evidence from the proposal.
5. If the proposal does not provide enough information for a dimension, say so explicitly and assign a conservative middle score unless the absence of evidence clearly weakens the case.
6. Be analytically strict. Do not reward vague claims such as "this is novel" unless the proposal explains why.

**Scoring scale for each dimension:**
1 = Very weak evidence
2 = Weak evidence
3 = Moderate / mixed evidence
4 = Strong evidence
5 = Very strong evidence

**Evaluate these six dimensions:**

**1. New question, topic, or problem framing**
Definition: Does the proposal introduce a new question, topic, or way of framing the problem? This dimension is grounded in definitions of originality that include studying a new topic or an understudied area (Guetzkow et al., 2004).

**2. New theory, concept, method, dataset, or design**
Definition: Does the proposal use or develop a new theory, concept, method, dataset, or research design? This dimension is grounded in definitions of originality as involving a new approach, theory, method, or data, and in proposal-review criteria emphasizing novel concepts and methods (Guetzkow et al., 2004; European Research Council, 2021).

**3. Unusual combination of existing ideas**
Definition: Does the proposal combine existing ideas, methods, datasets, or perspectives in an unusual or atypical way? This dimension is grounded in the recombination view of novelty (Uzzi et al., 2013).

**4. Beyond the state of the art rather than incremental**
Definition: Is the proposal ambitious and beyond the current state of the art, rather than merely extending prior work incrementally? This dimension is grounded in major proposal-review criteria (European Research Council, 2021).

**5. Credible high-risk / high-gain potential**
Definition: Does the proposal contain a credible high-risk, high-gain element, where the potential payoff is substantial if the work succeeds? This dimension is grounded in ERC review criteria (European Research Council, 2021).

**6. Potential to generate unique knowledge not obtainable from prior work alone**
Definition: Could the proposal generate knowledge that would be difficult to obtain from prior work alone? This dimension is grounded in the definition of originality as generating unique knowledge not available from previous studies (Shibayama & Wang, 2020).

For each dimension output: score, reasoning, evidence_from_proposal, uncertainties_or_limitations.
Then provide: overall_novelty_score, overall_summary, strongest_dimensions, weakest_dimensions, major_uncertainties.

Use the following JSON format exactly:

{{
  "proposal_id": "{proposal_id}",
  "new_question_topic_or_framing": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "new_theory_concept_method_dataset_or_design": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "unusual_combination_of_existing_ideas": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "beyond_state_of_the_art": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "credible_high_risk_high_gain": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "unique_knowledge_generation": {{
    "score": ,
    "reasoning": "",
    "evidence_from_proposal": "",
    "uncertainties_or_limitations": ""
  }},
  "overall_novelty_score": ,
  "overall_summary": "",
  "strongest_dimensions": [],
  "weakest_dimensions": [],
  "major_uncertainties": []
}}

**Research proposal:**
ID: {proposal_id}
Title: {proposal_title}
{proposal_full}""",
            parameters=['proposal_id', 'proposal_title', 'proposal_full', 'lit_neighbors']
        )

        return templates

    def get_template(self, template_name: str) -> PromptTemplate:
        """Get a specific template by name"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.templates.keys())}")
        return self.templates[template_name]
    
    def get_all_templates(self) -> Dict[str, PromptTemplate]:
        """Get all available templates"""
        return self.templates
    
    def list_templates(self) -> List[Dict[str, str]]:
        """Get a list of all templates with their names and descriptions"""
        return [
            {
                'name': name,
                'description': template.description,
                'parameters': template.parameters,
                'version': template.version,
            }
            for name, template in self.templates.items()
        ]
    
    def create_custom_template(self, name: str, description: str, template: str, parameters: List[str] = None):
        """Create a custom template"""
        self.templates[name] = PromptTemplate(
            name=name,
            description=description,
            template=template,
            parameters=parameters or []
        )
    
    def format_prompt(self, template_name: str, data: Dict[str, Any], role: str = None) -> str:
        """Format a prompt using a specific template and data"""
        template = self.get_template(template_name)
        format_data = {param: data.get(param, 'N/A') for param in template.parameters}
        try:
            return template.template.format(**format_data)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for template '{template_name}': {e}")
    



# Example usage and testing
if __name__ == "__main__":
    manager = PromptManager()
    print("Available templates:")
    for template_info in manager.list_templates():
        print(f"- {template_info['name']}: {template_info['description']}")
