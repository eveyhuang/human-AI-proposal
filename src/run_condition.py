import argparse
from pathlib import Path
from typing import Optional

from notebook_pipeline import render_notebook
from pipeline_config import load_pipeline_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Render the condition-specific notebook pipeline without executing it.'
    )
    parser.add_argument('--condition', required=True, help='Condition name, e.g. minimal, how_to_think, persona')
    parser.add_argument('--generate-new-ideas', action='store_true', help='Set gen_proposals.ipynb to generate fresh ideas')
    parser.add_argument('--reuse-existing-ideas', action='store_true', help='Set gen_proposals.ipynb to reuse existing idea snapshots')
    parser.add_argument('--steps', help='Comma-separated step numbers to render, e.g. 1,2,4,6')
    parser.add_argument('--from-step', type=int, help='First pipeline step to render')
    parser.add_argument('--to-step', type=int, help='Last pipeline step to render')
    return parser.parse_args()


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    matches = sorted(directory.glob(pattern))
    return matches[-1] if matches else None


def detect_generate_new_ideas(condition: str, args: argparse.Namespace) -> bool:
    if args.generate_new_ideas and args.reuse_existing_ideas:
        raise ValueError('Use only one of --generate-new-ideas or --reuse-existing-ideas.')
    if args.generate_new_ideas:
        return True
    if args.reuse_existing_ideas:
        return False

    ideas_dir = Path('data/ai-proposals') / condition
    existing_ideas = latest_file(ideas_dir, f'ai_ideas_{condition}_*.csv')
    return existing_ideas is None


def parse_selected_steps(steps_arg: Optional[str], step_numbers: list[int],
                         from_step: Optional[int], to_step: Optional[int]) -> list[int]:
    valid_steps = set(step_numbers)
    if steps_arg:
        selected_steps = set()
        for token in steps_arg.split(','):
            token = token.strip()
            if not token:
                continue
            try:
                step = int(token)
            except ValueError as exc:
                raise SystemExit(f'Invalid step "{token}" in --steps. Use comma-separated integers like 1,2,4,6.') from exc
            if step not in valid_steps:
                valid = ', '.join(str(s) for s in step_numbers)
                raise SystemExit(f'Invalid step "{step}" in --steps. Valid step numbers are: {valid}.')
            selected_steps.add(step)
        if not selected_steps:
            raise SystemExit('--steps was provided but no valid step numbers were found.')
        return sorted(selected_steps)

    start = from_step if from_step is not None else min(step_numbers)
    end = to_step if to_step is not None else max(step_numbers)
    if start not in valid_steps or end not in valid_steps:
        valid = f'{min(step_numbers)}-{max(step_numbers)}'
        raise SystemExit(f'Invalid step range. Valid step numbers are {valid}.')
    if start > end:
        raise SystemExit('--from-step cannot be greater than --to-step.')
    return [step for step in step_numbers if start <= step <= end]


def main() -> None:
    args = parse_args()
    config = load_pipeline_config()

    if args.condition not in config.conditions:
        valid = ', '.join(sorted(config.conditions))
        raise SystemExit(f'Unknown condition "{args.condition}". Valid conditions: {valid}')

    condition_cfg = config.conditions[args.condition]
    generate_new_ideas = detect_generate_new_ideas(args.condition, args)
    step_numbers = [spec.step for spec in config.pipeline_notebooks]
    selected_steps = parse_selected_steps(args.steps, step_numbers, args.from_step, args.to_step)

    selected_specs = [spec for spec in config.pipeline_notebooks if spec.step in selected_steps]
    step_label = ','.join(str(spec.step) for spec in selected_specs)
    print(f'Rendering steps {step_label} for condition "{args.condition}"')
    print(f'Output notebook folder: {condition_cfg.executed_notebook_dir}')

    for spec in selected_specs:
        output_path = condition_cfg.executed_notebook_dir / spec.output_name
        render_notebook(spec, condition_cfg, output_path, generate_new_ideas=generate_new_ideas)
        print(f'[{spec.step}] Rendered {output_path}  ({spec.description})')


if __name__ == '__main__':
    main()
