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
    generation_temperature: float = 0.7


@dataclass(frozen=True)
class NotebookSpec:
    step: int
    key: str
    description: str
    template: Path
    output_name: str


@dataclass(frozen=True)
class PipelineConfig:
    conditions: Dict[str, ConditionConfig]
    pipeline_notebooks: List[NotebookSpec]


def load_pipeline_config(config_path: Path = Path('configs/pipeline_conditions.json')) -> PipelineConfig:
    with open(config_path, 'r') as f:
        raw = json.load(f)

    conditions = {
        name: ConditionConfig(
            name=name,
            executed_notebook_dir=Path(payload['executed_notebook_dir']),
            idea_prompt_template=payload['idea_prompt_template'],
            proposal_prompt_template=payload['proposal_prompt_template'],
            generation_temperature=float(payload.get('generation_temperature', 0.7)),
        )
        for name, payload in raw['conditions'].items()
    }

    pipeline_notebooks = [
        NotebookSpec(
            step=int(item['step']),
            key=item['key'],
            description=item['description'],
            template=Path(item['template']),
            output_name=item['output_name'],
        )
        for item in raw['notebooks']
    ]
    pipeline_notebooks.sort(key=lambda item: item.step)

    return PipelineConfig(
        conditions=conditions,
        pipeline_notebooks=pipeline_notebooks,
    )
