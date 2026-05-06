import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from notebook_pipeline import execute_notebook, render_notebook
from pipeline_config import ConditionConfig, load_pipeline_config


STEP_DESCRIPTIONS = {
    1: 'Generate proposals notebook',
    2: 'Rephrase proposals',
    3: 'Compare proposals rephrased notebook',
    4: 'Generate NCEMS reviews',
    5: 'Generate novelty reviews',
    6: 'Build review_scores_wide.csv',
    7: 'Compare NCEMS reviews notebook',
    8: 'Compare novelty reviews notebook',
    9: 'Metric-score relationship notebook',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run the condition-specific generation, rephrasing, review, and analysis pipeline.'
    )
    parser.add_argument('--condition', required=True, help='Condition name, e.g. minimal, how_to_think, persona')
    parser.add_argument('--force', action='store_true', help='Re-run expensive API-backed steps even if outputs exist')
    parser.add_argument('--render-only', action='store_true', help='Render notebooks but do not execute them')
    parser.add_argument('--generate-new-ideas', action='store_true', help='Force idea generation inside gen_proposals.ipynb')
    parser.add_argument('--reuse-existing-ideas', action='store_true', help='Force reuse of existing idea snapshots')
    parser.add_argument('--steps', help='Comma-separated step numbers to run, e.g. 1,2,7,9')
    parser.add_argument('--from-step', type=int, default=1, help='First pipeline step to run (default: 1)')
    parser.add_argument('--to-step', type=int, default=9, help='Last pipeline step to run (default: 9)')
    return parser.parse_args()


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    matches = sorted(directory.glob(pattern))
    return matches[-1] if matches else None


def run_command(args: list[str]) -> None:
    print(f"\n$ {' '.join(args)}")
    subprocess.run(args, check=True)


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


def should_skip_generation(condition: str, force: bool) -> bool:
    if force:
        return False
    complete_dir = Path('data/ai-proposals') / condition
    return latest_file(complete_dir, f'ai_proposals_{condition}_complete_*.csv') is not None


def should_skip_rephrase(condition: str, force: bool) -> bool:
    if force:
        return False
    ai_dir = Path('data/ai-proposals/rephrased') / condition
    human_dir = Path('data/human-proposals/rephrased') / condition
    return all([
        latest_file(ai_dir, f'ai_proposals_{condition}_rephrased_*.csv') is not None,
        latest_file(human_dir, 'human_proposals_rephrased_y1_*.json') is not None,
        latest_file(human_dir, 'human_proposals_rephrased_y2_*.json') is not None,
    ])


def should_skip_ncems_reviews(condition: str, force: bool) -> bool:
    if force:
        return False
    ncems_dir = Path('data/reviews/ai_reviews') / condition / 'ncems_criteria'
    return latest_file(ncems_dir, 'ncems_reviews_*.json') is not None


def should_skip_novelty_reviews(condition: str, force: bool) -> bool:
    if force:
        return False
    novelty_dir = Path('data/reviews/ai_reviews') / condition / 'novelty'
    return latest_file(novelty_dir, 'novelty_reviews_*.json') is not None


def render_and_execute_notebook(spec, condition_cfg: ConditionConfig,
                                render_only: bool, generate_new_ideas: bool = False) -> None:
    output_path = condition_cfg.executed_notebook_dir / spec.output_name
    render_notebook(spec, condition_cfg, output_path, generate_new_ideas=generate_new_ideas)
    print(f'Rendered notebook -> {output_path}')
    if not render_only:
        execute_notebook(output_path)
        print(f'Executed notebook -> {output_path}')


def validate_step_range(from_step: int, to_step: int) -> None:
    valid_steps = set(STEP_DESCRIPTIONS)
    if from_step not in valid_steps or to_step not in valid_steps:
        valid = f'{min(valid_steps)}-{max(valid_steps)}'
        raise SystemExit(f'Invalid step range. Valid step numbers are {valid}.')
    if from_step > to_step:
        raise SystemExit('--from-step cannot be greater than --to-step.')


def parse_selected_steps(steps_arg: Optional[str], from_step: int, to_step: int) -> set[int]:
    valid_steps = set(STEP_DESCRIPTIONS)
    if steps_arg:
        selected_steps = set()
        for token in steps_arg.split(','):
            token = token.strip()
            if not token:
                continue
            try:
                step = int(token)
            except ValueError as exc:
                raise SystemExit(f'Invalid step "{token}" in --steps. Use comma-separated integers like 1,2,7,9.') from exc
            if step not in valid_steps:
                valid = ', '.join(str(s) for s in sorted(valid_steps))
                raise SystemExit(f'Invalid step "{step}" in --steps. Valid step numbers are: {valid}.')
            selected_steps.add(step)
        if not selected_steps:
            raise SystemExit('--steps was provided but no valid step numbers were found.')
        return selected_steps

    validate_step_range(from_step, to_step)
    return set(range(from_step, to_step + 1))


def should_run_step(step_num: int, selected_steps: set[int]) -> bool:
    return step_num in selected_steps


def main() -> None:
    args = parse_args()
    config = load_pipeline_config()

    if args.condition not in config.conditions:
        valid = ', '.join(sorted(config.conditions))
        raise SystemExit(f'Unknown condition "{args.condition}". Valid conditions: {valid}')

    condition_cfg = config.conditions[args.condition]
    python_executable = sys.executable
    generate_new_ideas = detect_generate_new_ideas(args.condition, args)
    selected_steps = parse_selected_steps(args.steps, args.from_step, args.to_step)
    step_label = ','.join(str(step) for step in sorted(selected_steps))
    print(f'Running steps {step_label} for condition "{args.condition}"')

    if should_run_step(1, selected_steps):
        if should_skip_generation(args.condition, args.force):
            print(f'Skipping step 1: {STEP_DESCRIPTIONS[1]} because a complete proposals CSV already exists.')
        else:
            render_and_execute_notebook(
                config.generation_notebook,
                condition_cfg,
                render_only=args.render_only,
                generate_new_ideas=generate_new_ideas,
            )

    if should_run_step(2, selected_steps):
        if should_skip_rephrase(args.condition, args.force):
            print(f'Skipping step 2: {STEP_DESCRIPTIONS[2]} because rephrased outputs already exist.')
        else:
            run_command([python_executable, 'src/rephrase_proposals.py', '--condition', args.condition])

    proposal_analysis_spec = next(spec for spec in config.analysis_notebooks if spec.key == 'compare_proposals_rephrased')
    if should_run_step(3, selected_steps):
        render_and_execute_notebook(
            proposal_analysis_spec,
            condition_cfg,
            render_only=args.render_only,
        )

    if should_run_step(4, selected_steps):
        if should_skip_ncems_reviews(args.condition, args.force):
            print(f'Skipping step 4: {STEP_DESCRIPTIONS[4]} because NCEMS review outputs already exist.')
        else:
            run_command([python_executable, 'src/generate_reviews_ncems_criteria.py', '--condition', args.condition])

    if should_run_step(5, selected_steps):
        if should_skip_novelty_reviews(args.condition, args.force):
            print(f'Skipping step 5: {STEP_DESCRIPTIONS[5]} because novelty review outputs already exist.')
        else:
            run_command([python_executable, 'src/generate_reviews_novelty.py', '--condition', args.condition])

    if should_run_step(6, selected_steps):
        run_command([python_executable, 'src/build_review_scores_wide.py', '--condition', args.condition])

    remaining_notebooks = {
        'compare_reviews_ncems_criteria': 7,
        'compare_reviews_novelty': 8,
        'metric_score_relationship': 9,
    }
    for notebook_spec in config.analysis_notebooks:
        step_num = remaining_notebooks.get(notebook_spec.key)
        if step_num is None:
            continue
        if should_run_step(step_num, selected_steps):
            render_and_execute_notebook(
                notebook_spec,
                condition_cfg,
                render_only=args.render_only,
            )


if __name__ == '__main__':
    main()
