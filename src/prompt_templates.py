"""
Prompt templates for research idea generation and proposal evaluation.
Includes: Generate Research Ideas (baseline), generate full proposals, Human Criteria Evaluation.
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

class PromptManager:
    """Manager for different prompt templates"""
    
    def __init__(self):
        """Initialize with default prompt templates"""
        self.templates = self._create_default_templates()

    def _create_default_templates(self) -> Dict[str, PromptTemplate]:
        """Create default prompt templates"""
        templates = {}

        # Generate Research Ideas (baseline)
        templates['generate_ideas_baseline'] = PromptTemplate(
            name="Generate Research Ideas (baseline)",
            description="Generate innovative research ideas without any special prompting",
            
            template="""
            You are generating research ideas for a competitive funding call from NCEMS (National Synthesis Center for Emergence in Molecular and Cellular Sciences).

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            CRITICAL REQUIREMENTS (your ideas MUST satisfy these):
            1. **SYNTHESIS RESEARCH ONLY**: Ideas must use ONLY existing publicly available data. DO NOT propose generating new experimental data, conducting new experiments, or collecting new samples. Your research must synthesize and integrate existing datasets.

            2. **EMERGENT PHENOMENA FOCUS**: Research must explicitly address emergent phenomena at the MESOSCALE (the scale between individual biomolecules and organelles, ~10-1000 nm). Focus on how unexpected properties arise from molecular/cellular organization.

            3. **COLLABORATIVE & TRANSDISCIPLINARY**: Research requires expertise from multiple disciplines and goes beyond what a single lab can accomplish.

            4. **OPEN SCIENCE**: Commit to making all analyses, code, and results publicly available.

            TASK:
            Generate {num} innovative and DIVERSE research ideas that address the goals above. 

            DIVERSITY REQUIREMENTS:
            - Cover different biological systems, scales, or phenomena
            - Use varied analytical/computational approaches
            - Address different aspects of emergent phenomena
            - Ensure minimal overlap between ideas

            For each idea, provide:
            - **Title**: Clear, specific, and scientifically precise
            - **Abstract** (400-600 words) that includes:
              * The specific emergent phenomenon being studied
              * What existing data sources will be synthesized (be specific: e.g., "PDB structural data", "Cancer Genome Atlas", "single-cell RNA-seq from Human Cell Atlas")
              * The novel scientific question or hypothesis
              * The computational/analytical approach
              * Expected insights about mesoscale emergent phenomena
              * Why this requires team science and synthesis

            QUALITY BAR - Each idea should aim for:
            - High novelty: Not incremental; transformative questions
            - High rigor: Clear, logical methodology
            - High feasibility: Realistic with existing data and methods
            - High impact: Potential to advance fundamental understanding

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
            parameters=['research_call', 'information_about_ncems', 'num']
        )

        # Generate Research Ideas (baseline)
        templates['generate_ideas_minimal'] = PromptTemplate(
            name="Generate Research Ideas (minimal)",
            description="Generate innovative research ideas without any special prompting",
            
            template="""
            You are generating research ideas that will most likely be accepted by the competitive funding call from NCEMS (National Synthesis Center for Emergence in Molecular and Cellular Sciences).

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            TASK:
            Generate {num} research ideas that are aglined with the research call and are all different from each other. 

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
            parameters=['research_call', 'information_about_ncems', 'num']
        )


        # generate full proposals from ideas
        templates['generate_proposals'] = PromptTemplate(
            name="Generate Research Proposals",
            description="Generate comprehensive research proposals based on title and abstract",
            template="""
            Write a comprehensive research proposal based on the provided title and abstract, ensuring it aligns with NCEMS funding requirements.

            RESEARCH CALL:
            {research_call}

            INFORMATION ABOUT NCEMS:
            {information_about_ncems}

            RESEARCH IDEA TO EXPAND:
            Title: {title}
            Abstract: {abstract}

            CRITICAL CONSTRAINTS:
            1. **NO NEW DATA GENERATION**: This must be synthesis research using ONLY existing publicly available data. Do not propose experiments, data collection, or generating new samples.
            2. **MESOSCALE EMERGENT PHENOMENA**: Keep focus on emergent properties at the mesoscale (between molecules and organelles).
            3. **COLLABORATIVE TEAM SCIENCE**: Emphasize how this requires multiple labs/disciplines.
            4. **OPEN SCIENCE**: Detail plans for open code, data, and reproducible workflows.

            Create a proposal meeting the highest standards for scientific rigor, clarity, and feasibility. Include these sections with specified word counts:

            1. BACKGROUND AND SIGNIFICANCE (600-800 words)
               - Current understanding of the mesoscale phenomenon
               - Literature review showing what's known from existing data
               - Specific gaps that synthesis research can address
               - Why emergent phenomena at this scale are important
               - How existing data sources enable new insights

            2. RESEARCH QUESTIONS AND HYPOTHESES (600-800 words)
               - Precise, testable research questions about emergent phenomena
               - Clear hypotheses with measurable predictions
               - How hypotheses will be validated using existing data
               - Expected mechanistic insights about mesoscale organization

            3. METHODS AND APPROACH (800-1000 words)
               - **Specific data sources**: Name actual databases/repositories (e.g., "Protein Data Bank", "Human Cell Atlas scRNA-seq", "ENCODE ChIP-seq")
               - Data integration/harmonization strategy
               - Computational/analytical methods (algorithms, statistical approaches, AI/ML if applicable)
               - **Synthesis approach**: How you'll integrate heterogeneous datasets
               - Validation strategies (cross-dataset validation, known positive controls)
               - Timeline with milestones (realistic for 2-3 year project)
               - Team composition: what expertise is needed
               - **NO experimental validation** - all validation must use existing data

            4. EXPECTED OUTCOMES AND IMPACT (600-800 words)
               - Specific deliverables (integrated datasets, computational tools, mechanistic models)
               - Contribution to understanding mesoscale emergent phenomena
               - Broader impacts on molecular/cellular biology
               - How results enable future research
               - Plans for dissemination (publications, workshops, databases)
               - Long-term sustainability of data/tools

            5. OPEN SCIENCE AND REPRODUCIBILITY (300-500 words)
               - Code sharing plan (GitHub/GitLab with open license)
               - Data sharing plan (which repositories, when)
               - Reproducible workflows (Docker containers, Jupyter notebooks, workflow management)
               - Documentation standards
               - Community engagement and training plans

            6. BUDGET AND RESOURCES (400-600 words)
               - Personnel (postdocs, graduate students, programmer)
               - Computing resources (cloud computing, HPC time)
               - Travel for collaboration and dissemination
               - Workshops/training events
               - Open science infrastructure costs
               - Justify each budget item relative to synthesis goals

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
            - Emphasize SYNTHESIS throughout - no new data generation
            - Be specific about data sources (don't say "publicly available data", name them)
            - Maintain focus on mesoscale emergent phenomena
            - Ensure the JSON is properly formatted and valid
            """,
            parameters=['title', 'abstract', 'research_call', 'information_about_ncems']
        )

         # generate full proposals from ideas
        templates['generate_proposals_minimal'] = PromptTemplate(
            name="Generate Research Proposals Minimal",
            description="Generate comprehensive research proposals based on title and abstract",
            template="""
            Write a comprehensive research proposal based on the provided title and abstract, ensuring it aligns with NCEMS funding requirements.

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
            parameters=['title', 'abstract', 'research_call', 'information_about_ncems']
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
                'parameters': template.parameters
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
