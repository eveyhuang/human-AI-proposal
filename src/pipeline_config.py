import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class ConditionConfig:
    name: str
    executed_notebook_dir: Path
    idea_prompt_template: str
    proposal_prompt_template: str


@dataclass(frozen=True)
class NotebookSpec:
    key: str
    template: Path
    output_name: str


@dataclass(frozen=True)
class PipelineConfig:
    conditions: Dict[str, ConditionConfig]
    generation_notebook: NotebookSpec
    analysis_notebooks: List[NotebookSpec]


def load_pipeline_config(config_path: Path = Path('configs/pipeline_conditions.json')) -> PipelineConfig:
    with open(config_path, 'r') as f:
        raw = json.load(f)

    conditions = {
        name: ConditionConfig(
            name=name,
            executed_notebook_dir=Path(payload['executed_notebook_dir']),
            idea_prompt_template=payload['idea_prompt_template'],
            proposal_prompt_template=payload['proposal_prompt_template'],
        )
        for name, payload in raw['conditions'].items()
    }

    generation = raw['notebooks']['generation']
    generation_notebook = NotebookSpec(
        key='gen_proposals',
        template=Path(generation['template']),
        output_name=generation['output_name'],
    )

    analysis_notebooks = [
        NotebookSpec(
            key=item['key'],
            template=Path(item['template']),
            output_name=item['output_name'],
        )
        for item in raw['notebooks']['analysis']
    ]

    return PipelineConfig(
        conditions=conditions,
        generation_notebook=generation_notebook,
        analysis_notebooks=analysis_notebooks,
    )
