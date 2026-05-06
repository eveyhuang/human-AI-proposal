import base64
import io
import json
import os
import traceback
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Iterable, List, Optional

from pipeline_config import ConditionConfig, NotebookSpec


class NotebookTemplateError(RuntimeError):
    pass


class NotebookExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class NotebookRenderResult:
    notebook: Dict[str, Any]
    output_path: Path


def _load_notebook(path: Path) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def _write_notebook(path: Path, notebook: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(notebook, f, indent=1)
        f.write('\n')


def _find_code_cell_index(notebook: Dict[str, Any], required_fragments: Iterable[str]) -> int:
    fragments = tuple(required_fragments)
    for idx, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell.get('source', []))
        if all(fragment in source for fragment in fragments):
            return idx
    raise NotebookTemplateError(f'Could not find code cell containing fragments: {fragments}')


def _set_cell_source(notebook: Dict[str, Any], cell_index: int, source: str) -> None:
    notebook['cells'][cell_index]['source'] = source.splitlines(keepends=True)
    notebook['cells'][cell_index]['outputs'] = []
    notebook['cells'][cell_index]['execution_count'] = None


def _render_gen_proposals(notebook: Dict[str, Any], condition: ConditionConfig,
                          generate_new_ideas: bool) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    idx = _find_code_cell_index(rendered, ['# Condition Configuration', 'CONDITION ='])
    source = dedent(f"""\
        # =========================
        # Condition Configuration
        # =========================
        # This cell is auto-managed by src/run_condition.py.
        CONDITION = '{condition.name}'
        GENERATE_NEW_IDEAS = {str(generate_new_ideas)}

        IDEA_PROMPT_TEMPLATE = '{condition.idea_prompt_template}'
        PROPOSAL_PROMPT_TEMPLATE = '{condition.proposal_prompt_template}'

        NUM_IDEAS_PER_MODEL = 23
        IDEAS_FILE_OVERRIDE = None
        IDEAS_GLOB = None

        condition_slug = CONDITION.replace('/', '_').replace(' ', '_')
        ideas_input_dir = Path('data/ai-proposals') / CONDITION
        output_dir = ideas_input_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        MODEL_CANONICAL_MAP = {{
            'gpt-5.2': 'gpt-5.2',
            'gpt5.2': 'gpt-5.2',
            'gpt': 'gpt-5.2',
            'gpt-5': 'gpt-5.2',
            'gemini-3-pro-preview': 'gemini-3-pro-preview',
            'gemini3propreview': 'gemini-3-pro-preview',
            'gemini': 'gemini-3-pro-preview',
            'claude-opus-4-5': 'claude-opus-4-5',
            'claudeopus45': 'claude-opus-4-5',
            'claude': 'claude-opus-4-5',
        }}


        def _normalize_key(s):
            return ''.join(ch for ch in str(s).lower() if ch.isalnum())


        def canonicalize_model(model_value):
            if model_value is None:
                return None
            key = _normalize_key(model_value)
            return MODEL_CANONICAL_MAP.get(key, str(model_value))


        def infer_model_from_filename(path: Path):
            name = path.name.lower()
            if 'claude' in name:
                return 'claude-opus-4-5'
            if 'gemini' in name:
                return 'gemini-3-pro-preview'
            if 'gpt' in name:
                return 'gpt-5.2'
            return None


        def _extract_ideas_from_json_obj(obj):
            if isinstance(obj, list):
                return obj
            if isinstance(obj, dict):
                for k in ['research_ideas', 'ideas', 'records', 'data']:
                    if k in obj and isinstance(obj[k], list):
                        return obj[k]
            return []
    """)
    _set_cell_source(rendered, idx, source)
    return rendered


def _render_compare_proposals_rephrased(notebook: Dict[str, Any],
                                        condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)

    setup_idx = _find_code_cell_index(rendered, ['PROPOSAL_EMBEDDINGS_FILE', "condition = 'rephrased/minimal'"])
    setup_source = dedent(f"""\
        import sys
        import os
        import json
        import numpy as np
        import pandas as pd
        from pathlib import Path
        import pickle
        from datetime import datetime
        import warnings
        warnings.filterwarnings('ignore')

        # Plotting
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # NLP and embeddings
        from transformers import AutoTokenizer, AutoModel
        import torch
        from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
        from scipy.spatial.distance import cdist
        from tqdm import tqdm

        # Statistics
        from scipy import stats
        from scipy.stats import mannwhitneyu
        import itertools

        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11

        print("✓ Imports successful")
        print(f"✓ Working directory: {{os.getcwd()}}")
        print(f"✓ PyTorch version: {{torch.__version__}}")
        print(f"✓ CUDA available: {{torch.cuda.is_available()}}")

        try:
            import umap
        except ImportError:
            import subprocess
            subprocess.check_call(['pip', 'install', 'umap-learn'])
            import umap

        CONDITION_NAME = '{condition.name}'
        condition = f'rephrased/{{CONDITION_NAME}}'
        AI_REPHRASED_GLOB = f'ai_proposals_{{CONDITION_NAME}}_rephrased_*.csv'
        AI_ORIGINAL_GLOB = f'ai_proposals_{{CONDITION_NAME}}_complete_*.csv'

        AI_PROPOSALS_PATH = Path(f'../data/ai-proposals/{{condition}}')
        HUMAN_PROPOSALS_PATH = Path(f'../data/human-proposals/{{condition}}')
        RESULTS_DIR = Path('../results')
        FIGURES_DIR = RESULTS_DIR / 'figures' / condition
        TABLES_DIR = RESULTS_DIR / 'tables' / condition
        PROPOSAL_EMBEDDINGS_FILE = Path(f'../data/embeddings/{{condition}}/proposal_embeddings_human_ai_rephrased.pkl')
        ABSTRACT_EMBEDDINGS_FILE = Path(f'../data/embeddings/{{condition}}/proposal_embeddings_section1_only.pkl')
        MAIN_IDEA_EMBEDDINGS_FILE = Path(f'../data/embeddings/{{condition}}/proposal_embeddings_main_idea_only.pkl')
        LITERATURE_EMBEDDINGS_FILE = Path('../data/embeddings/literature/relevant_literature_embeddings.pkl')
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
        PROPOSAL_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ABSTRACT_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        LITERATURE_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        MAIN_IDEA_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    """)
    _set_cell_source(rendered, setup_idx, setup_source)

    load_idx = _find_code_cell_index(rendered, ['# Load AI proposals', 'ai_proposals_minimal_rephrased_*.csv'])
    load_source = dedent("""\
        # Load AI proposals
        ai_files = sorted(AI_PROPOSALS_PATH.glob(AI_REPHRASED_GLOB))
        if not ai_files:
            ai_files = sorted(AI_PROPOSALS_PATH.glob('ai_proposals_*_rephrased_*.csv'))

        if not ai_files:
            raise FileNotFoundError("No rephrased AI proposal files found. Run src/rephrase_proposals.py first.")

        ai_df = pd.read_csv(ai_files[-1])
        print(f"✓ Loaded AI proposals from: {ai_files[-1].name}")
        print(f"  Shape: {ai_df.shape}")
        print(f"  Models: {ai_df['model'].value_counts().to_dict()}")

        human_files = list(HUMAN_PROPOSALS_PATH.glob('*.json'))
        human_proposals = []
        for file in human_files:
            with open(file, 'r') as f:
                data = json.load(f)

                if isinstance(data, list):
                    for proposal in data:
                        proposal['source_file'] = file.name
                        human_proposals.append(proposal)
                elif 'proposals' in data:
                    for proposal in data['proposals']:
                        proposal['source_file'] = file.name
                        human_proposals.append(proposal)
                else:
                    data['source_file'] = file.name
                    human_proposals.append(data)

        human_df = pd.DataFrame(human_proposals)
        print(f"\\n✓ Loaded human proposals from {len(human_files)} files")
        print(f"  Total proposals: {len(human_df)}")
        print(f"  Source files: {human_df['source_file'].unique().tolist()}")
    """)
    _set_cell_source(rendered, load_idx, load_source)

    mi_idx = _find_code_cell_index(rendered, ['proposal_embeddings_main_idea_minimal.pkl', "'main_idea' column missing"])
    mi_source = dedent("""\
        # ── Load main_idea texts and define embedding cache path ────────────────────
        MI_EMBEDDINGS_FILE = MAIN_IDEA_EMBEDDINGS_FILE
        MI_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        for _df_name, _df in [('ai_df', ai_df), ('human_df', human_df)]:
            if 'main_idea' not in _df.columns:
                raise RuntimeError(
                    f"'main_idea' column missing from {_df_name}. "
                    "Re-run rephrase_proposals.py to regenerate the rephrased files."
                )

        mi_ai_texts = ai_df['main_idea'].fillna('').astype(str).tolist()
        mi_human_texts = human_df['main_idea'].fillna('').astype(str).tolist()

        print(f'AI main ideas:    {len(mi_ai_texts)}')
        print(f'Human main ideas: {len(mi_human_texts)}')
        print()
        print('── Sample AI main idea ──')
        print(mi_ai_texts[0][:500])
        print()
        print('── Sample Human main idea ──')
        print(mi_human_texts[0][:500])
    """)
    _set_cell_source(rendered, mi_idx, mi_source)

    export_idx = _find_code_cell_index(rendered, ["_AI_BASE / 'minimal'", 'all_proposals.json'])
    export_source = dedent("""\
        import json as _json
        import pandas as pd
        import numpy as np
        from pathlib import Path

        def _norm(s): return str(s).strip().lower()

        def _load(fname):
            df = pd.read_csv(TABLES_DIR / fname)
            df['_key'] = df['title'].map(_norm)
            return df

        def _load_optional(fname):
            p = TABLES_DIR / fname
            if p.exists():
                df = pd.read_csv(p)
                if 'title' in df.columns:
                    df['_key'] = df['title'].map(_norm)
                return df
            return None

        cent_df = _load('centroid_distances.csv')
        nn_df = _load('nn_distances.csv')
        nov_df = _load('novelty_scores_from_literature.csv')
        style_metrics_df = _load('style_features.csv')
        scores_df = _load_optional('review_scores_wide.csv')

        lit_out_df = _load_optional('literature_space_outliers_mean_knn_k10.csv')
        if lit_out_df is None:
            lit_out_df = _load_optional('literature_space_outliers_mean_knn_k5.csv')

        score_cols = [] if scores_df is None else [c for c in scores_df.columns if c not in {'title', 'author', '_key'}]

        def _to_dict(df, cols):
            return {row['_key']: {c: row[c] for c in cols} for _, row in df.iterrows()}

        cent_lut = _to_dict(cent_df, ['centroid_dist'])
        nn_lut = _to_dict(nn_df, ['nn_dist', 'is_outlier', 'threshold'])
        nov_lut = _to_dict(
            nov_df,
            ['raw_novelty', 'novelty_z', 'novelty_ratio',
             'is_most_novel_raw', 'is_most_novel_z', 'is_most_novel_ratio'],
        )
        style_feat_cols = [c for c in style_metrics_df.columns if c not in {'title', 'group', 'is_ai', '_key'}]
        style_lut = _to_dict(style_metrics_df, style_feat_cols)
        scores_lut = {} if scores_df is None else _to_dict(scores_df, score_cols)

        lit_out_lut = {}
        _lit_dist_col = None
        if lit_out_df is not None and len(lit_out_df):
            for cand in [c for c in lit_out_df.columns if c.startswith('mean_lit_nn_dist_k')]:
                _lit_dist_col = cand
                break
            if '_key' not in lit_out_df.columns and 'title' in lit_out_df.columns:
                lit_out_df['_key'] = lit_out_df['title'].map(_norm)

            if _lit_dist_col is not None and 'is_outlier_literature_space' in lit_out_df.columns:
                for _, row in lit_out_df.iterrows():
                    key = row.get('_key')
                    if key is None:
                        continue
                    raw_flag = row.get('is_outlier_literature_space', 0)
                    flag = 0 if pd.isna(raw_flag) else int(bool(raw_flag))
                    lit_out_lut[key] = {
                        'is_literature_outlier': flag,
                        _lit_dist_col: row.get(_lit_dist_col),
                        'threshold_literature_space': row.get('threshold_literature_space', None),
                    }

        if not lit_out_lut and all(v in globals() for v in ['titles_ls', 'lit_space_outliers_mknn']):
            _dist = globals().get('mean_lit_knn_dist', None)
            _thr = globals().get('lit_mknn_threshold', None)
            for i, t in enumerate(titles_ls):
                key = _norm(t)
                flag = int(bool(lit_space_outliers_mknn[i]))
                rec = {'is_literature_outlier': flag, 'threshold_literature_space': _thr}
                if _dist is not None:
                    rec[f"mean_lit_nn_dist_k{globals().get('k_lit_out', 10)}"] = _dist[i]
                lit_out_lut[key] = rec

        _pairwise_map, _mi_cd_map, _mi_nn_map, _mi_pm_map = {}, {}, {}, {}
        if 'human_pairwise_proposal_means' in globals() and 'human_df' in globals():
            for _i, (_, _r) in enumerate(human_df.iterrows()):
                _t = _norm(_r.get('proposal_title', _r.get('title', '')))
                _pairwise_map[_t] = float(human_pairwise_proposal_means[_i])
        if 'ai_pairwise_proposal_means' in globals() and 'ai_df' in globals():
            for _i, (_, _r) in enumerate(ai_df.iterrows()):
                _t = _norm(_r.get('title', _r.get('proposal_title', '')))
                _pairwise_map[_t] = float(ai_pairwise_proposal_means[_i])
        if 'mi_human_cd' in globals() and 'human_df' in globals():
            for _i, (_, _r) in enumerate(human_df.iterrows()):
                _t = _norm(_r.get('proposal_title', _r.get('title', '')))
                _mi_cd_map[_t] = float(mi_human_cd[_i])
                if 'mi_human_nn' in globals():
                    _mi_nn_map[_t] = float(mi_human_nn[_i])
                if 'mi_human_pm' in globals():
                    _mi_pm_map[_t] = float(mi_human_pm[_i])
        if 'mi_ai_cd' in globals() and 'ai_df' in globals():
            for _i, (_, _r) in enumerate(ai_df.iterrows()):
                _t = _norm(_r.get('title', _r.get('proposal_title', '')))
                _mi_cd_map[_t] = float(mi_ai_cd[_i])
                if 'mi_ai_nn' in globals():
                    _mi_nn_map[_t] = float(mi_ai_nn[_i])
                if 'mi_ai_pm' in globals():
                    _mi_pm_map[_t] = float(mi_ai_pm[_i])

        def _get_metrics(key):
            m = {}
            m.update(cent_lut.get(key, {'centroid_dist': None}))
            m.update(nn_lut.get(key, {'nn_dist': None, 'is_outlier': None, 'threshold': None}))
            m.update(
                nov_lut.get(
                    key,
                    {c: None for c in ['raw_novelty', 'novelty_z', 'novelty_ratio',
                                       'is_most_novel_raw', 'is_most_novel_z', 'is_most_novel_ratio']},
                )
            )
            m.update(style_lut.get(key, {c: None for c in style_feat_cols}))
            m.update({'is_literature_outlier': 0, 'threshold_literature_space': None})
            m.update(lit_out_lut.get(key, {}))

            review = scores_lut.get(key, {c: None for c in score_cols})
            review['review_score_mean'] = (
                np.nanmean([v for v in review.values() if v is not None])
                if any(v is not None for v in review.values()) else None
            )
            m.update(review)

            m['pairwise_mean_dist'] = _pairwise_map.get(key)
            m['mi_centroid_dist'] = _mi_cd_map.get(key)
            m['mi_nn_dist'] = _mi_nn_map.get(key)
            m['mi_pairwise_mean_dist'] = _mi_pm_map.get(key)

            raw_lit_flag = m.get('is_literature_outlier', 0)
            if pd.isna(raw_lit_flag):
                raw_lit_flag = 0
            m['is_literature_outlier'] = int(bool(raw_lit_flag))
            return {k: (v.item() if hasattr(v, 'item') else v) for k, v in m.items()}

        _AI_BASE = AI_PROPOSALS_PATH.parent.parent
        _orig_ai = pd.read_csv(sorted((_AI_BASE / CONDITION_NAME).glob(AI_ORIGINAL_GLOB))[-1])
        _rep_ai = pd.read_csv(sorted(AI_PROPOSALS_PATH.glob('ai_proposals_*.csv'))[-1])
        _rep_ai_lut = {_norm(r['title']): r for _, r in _rep_ai.iterrows()}

        _AI_ORIG_SECTIONS = [
            'abstract',
            'background_and_significance',
            'research_questions_and_hypotheses',
            'methods_and_approach',
            'expected_outcomes_and_impact',
            'budget_and_resources',
        ]

        records = []
        for _, row in _orig_ai.iterrows():
            title = row['title']
            key = _norm(title)
            rep = _rep_ai_lut.get(key, {})
            rec = {
                'title': title,
                'group': row.get('model', 'AI'),
                'is_ai': True,
                'model': row.get('model'),
                'cohort': None,
                'original': {s: row.get(s) for s in _AI_ORIG_SECTIONS},
                'rephrased': {
                    'standardized_text': rep.get('standardized_text'),
                    'main_idea': rep.get('main_idea'),
                },
                'metrics': _get_metrics(key),
            }
            records.append(rec)

        _HUM_BASE = HUMAN_PROPOSALS_PATH.parent.parent

        def _load_human_cohort(cohort):
            with open(_HUM_BASE / f'human-proposals-{cohort}.json') as fh:
                orig_props = _json.load(fh)['proposals']
            rep_paths = sorted(HUMAN_PROPOSALS_PATH.glob(f'human_proposals_rephrased_{cohort}_*.json'))
            rep_lut = {}
            if rep_paths:
                with open(rep_paths[-1]) as fh:
                    for p in _json.load(fh)['proposals']:
                        t = p.get('proposal_title', p.get('title', ''))
                        rep_lut[_norm(t)] = p
            for prop in orig_props:
                title = prop.get('proposal_title', prop.get('title', ''))
                key = _norm(title)
                rep = rep_lut.get(key, {})
                rec = {
                    'title': title,
                    'group': 'Human',
                    'is_ai': False,
                    'model': None,
                    'cohort': cohort,
                    'original': {
                        'abstract': prop.get('abstract'),
                        'full_draft': prop.get('full_draft'),
                    },
                    'rephrased': {
                        'standardized_text': rep.get('standardized_text'),
                        'main_idea': rep.get('main_idea'),
                    },
                    'metrics': _get_metrics(key),
                }
                records.append(rec)

        _load_human_cohort('y1')
        _load_human_cohort('y2')

        out_path = TABLES_DIR / 'all_proposals.json'
        with open(out_path, 'w') as fh:
            _json.dump(records, fh, indent=2, default=str)

        _metric_keys = list(records[0]['metrics'].keys()) if records else []
        _filled = lambda k: sum(1 for r in records if r['metrics'].get(k) is not None)

        print(f'Saved all_proposals.json ({len(records)} proposals)')
        print(f'Path: {out_path}')
        print()
        print('Metrics coverage:')
        for k in _metric_keys:
            print(f'  {k:<35} {_filled(k):>3}/{len(records)}')

        n_lit_out = sum(int(r['metrics'].get('is_literature_outlier', 0)) for r in records)
        print()
        print(
            f"Literature-space outlier flag coverage: {len(records)}/{len(records)} "
            f"(binary), positives={n_lit_out}"
        )
    """)
    _set_cell_source(rendered, export_idx, export_source)
    return rendered


def _render_compare_reviews(notebook: Dict[str, Any], condition: ConditionConfig,
                            review_kind: str) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    idx = _find_code_cell_index(rendered, ["condition='minimal'", 'REVIEW_EMBEDDINGS_FILE'])
    if review_kind == 'ncems_criteria':
        source = dedent(f"""\
            import json
            import re
            import itertools
            import pickle
            from pathlib import Path
            from difflib import SequenceMatcher

            import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            from scipy.stats import mannwhitneyu, kruskal, wilcoxon, spearmanr, kendalltau, linregress
            from sklearn.metrics.pairwise import cosine_similarity
            from textblob import TextBlob

            import torch
            from transformers import AutoTokenizer, AutoModel

            sns.set_theme(style='whitegrid', context='talk')

            condition = '{condition.name}'
            AI_REVIEWS_PATH = sorted(
                Path(f'../data/reviews/ai_reviews/{{condition}}/ncems_criteria').glob('ncems_reviews_*.json')
            )[-1]
            HUMAN_Y1_REVIEWS_PATH = Path('../data/reviews/human_reviews/human_reviews_human-y1.xlsx')
            FIGURES_DIR = Path(f'../results/figures/quality/{{condition}}/ncems_criteria')
            TABLES_DIR = Path(f'../results/tables/quality/{{condition}}/ncems_criteria')
            REVIEW_EMBEDDINGS_FILE = Path(
                f'../data/embeddings/reviews/{{condition}}/ncems_criteria/review_embeddings_{{condition}}.pkl'
            )
            OUTPUT_DIR = FIGURES_DIR
            FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            TABLES_DIR.mkdir(parents=True, exist_ok=True)
            REVIEW_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            colors = {{
                'Human': '#DC143C',
                'claude-opus-4-5': '#4A90E2',
                'gemini-3-pro-preview': '#7B68EE',
                'gpt-5.2': '#FF8C00',
            }}

            CRITERIA_ORDER = [
                'Relevance_to_Emergent_Phenomena',
                'Novelty_and_Significance',
                'Rigor_of_Approach',
                'Scope_and_Timeline',
                'Synthesis_Focus',
                'Data_Identification',
                'Open_Science_Commitment',
            ]
    """)
    else:
        source = dedent(f"""\
            import json
            import re
            import itertools
            import pickle
            from pathlib import Path
            from difflib import SequenceMatcher

            import numpy as np
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt

            from scipy.stats import mannwhitneyu, kruskal, wilcoxon, spearmanr, kendalltau, linregress
            from sklearn.metrics.pairwise import cosine_similarity
            from textblob import TextBlob

            import torch
            from transformers import AutoTokenizer, AutoModel

            sns.set_theme(style='whitegrid', context='talk')

            condition = '{condition.name}'
            AI_REVIEWS_PATH = sorted(
                Path(f'../data/reviews/ai_reviews/{{condition}}/novelty').glob('novelty_reviews_*.json')
            )[-1]
            FIGURES_DIR = Path(f'../results/figures/quality/{{condition}}/novelty')
            TABLES_DIR = Path(f'../results/tables/quality/{{condition}}/novelty')
            REVIEW_EMBEDDINGS_FILE = Path(
                f'../data/embeddings/reviews/{{condition}}/novelty/review_embeddings_{{condition}}.pkl'
            )
            OUTPUT_DIR = FIGURES_DIR
            FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            TABLES_DIR.mkdir(parents=True, exist_ok=True)
            REVIEW_EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

            colors = {{
                'Human': '#DC143C',
                'claude-opus-4-5': '#4A90E2',
                'gemini-3-pro-preview': '#7B68EE',
                'gpt-5.2': '#FF8C00',
            }}

            CRITERIA_ORDER = [
                'new_question_topic_or_framing',
                'new_theory_concept_method_dataset_or_design',
                'unusual_combination_of_existing_ideas',
                'beyond_state_of_the_art',
                'credible_high_risk_high_gain',
                'unique_knowledge_generation',
            ]
    """)
    _set_cell_source(rendered, idx, source)
    return rendered


def _render_metric_score_relationship(notebook: Dict[str, Any],
                                      condition: ConditionConfig) -> Dict[str, Any]:
    rendered = deepcopy(notebook)
    idx = _find_code_cell_index(rendered, ['ALL_PROPOSALS_PATH', "condition = 'rephrased/minimal'"])
    source = dedent(f"""\
        import sys
        import os
        import json
        import numpy as np
        import pandas as pd
        from pathlib import Path
        import pickle
        from datetime import datetime
        import warnings
        warnings.filterwarnings('ignore')

        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        from transformers import AutoTokenizer, AutoModel
        import torch
        from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
        from scipy.spatial.distance import cdist
        from tqdm import tqdm

        from scipy import stats
        from scipy.stats import mannwhitneyu
        import itertools

        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11

        print("✓ Imports successful")
        print(f"✓ Working directory: {{os.getcwd()}}")
        print(f"✓ PyTorch version: {{torch.__version__}}")
        print(f"✓ CUDA available: {{torch.cuda.is_available()}}")

        try:
            import umap
        except ImportError:
            import subprocess
            subprocess.check_call(['pip', 'install', 'umap-learn'])
            import umap

        ANALYSIS_CONDITION = '{condition.name}'
        condition = f'rephrased/{{ANALYSIS_CONDITION}}'

        ALL_PROPOSALS_PATH = Path(f'../results/tables/rephrased/{{ANALYSIS_CONDITION}}/all_proposals.json')
        NCEMS_REVIEWS_PATH = sorted(
            Path(f'../data/reviews/ai_reviews/{{ANALYSIS_CONDITION}}/ncems_criteria').glob('ncems_reviews_*.json')
        )[-1]
        NOVELTY_REVIEWS_PATH = sorted(
            Path(f'../data/reviews/ai_reviews/{{ANALYSIS_CONDITION}}/novelty').glob('novelty_reviews_*.json')
        )[-1]

        RESULTS_DIR = Path('../results')
        FIGURES_DIR = RESULTS_DIR / 'figures' / condition / 'metric-score'
        TABLES_DIR = RESULTS_DIR / 'tables' / condition / 'metric-score'
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        TABLES_DIR.mkdir(parents=True, exist_ok=True)
    """)
    _set_cell_source(rendered, idx, source)
    return rendered


def render_notebook(spec: NotebookSpec, condition: ConditionConfig, output_path: Path,
                    generate_new_ideas: bool = False) -> NotebookRenderResult:
    notebook = _load_notebook(spec.template)

    if spec.key == 'gen_proposals':
        notebook = _render_gen_proposals(notebook, condition, generate_new_ideas)
    elif spec.key == 'compare_proposals_rephrased':
        notebook = _render_compare_proposals_rephrased(notebook, condition)
    elif spec.key == 'compare_reviews_ncems_criteria':
        notebook = _render_compare_reviews(notebook, condition, 'ncems_criteria')
    elif spec.key == 'compare_reviews_novelty':
        notebook = _render_compare_reviews(notebook, condition, 'novelty')
    elif spec.key == 'metric_score_relationship':
        notebook = _render_metric_score_relationship(notebook, condition)
    else:
        raise NotebookTemplateError(f'Unsupported notebook key: {spec.key}')

    _write_notebook(output_path, notebook)
    return NotebookRenderResult(notebook=notebook, output_path=output_path)


def _serialize_display_output(output: Any) -> Dict[str, Any]:
    data = {}
    for mime, value in getattr(output, 'data', {}).items():
        if isinstance(value, bytes):
            data[mime] = base64.b64encode(value).decode('ascii')
        else:
            data[mime] = value
    return {
        'output_type': 'display_data',
        'data': data,
        'metadata': getattr(output, 'metadata', {}) or {},
    }


def _append_text_stream(outputs: List[Dict[str, Any]], name: str, text: str) -> None:
    if not text:
        return
    outputs.append({
        'output_type': 'stream',
        'name': name,
        'text': text,
    })


def execute_notebook(notebook_path: Path) -> None:
    try:
        from IPython.core.interactiveshell import InteractiveShell
        from IPython.utils.capture import capture_output
    except ImportError as exc:
        raise NotebookExecutionError(
            'Notebook execution requires IPython. Run this pipeline with the project notebook environment.'
        ) from exc

    notebook = _load_notebook(notebook_path)
    shell = InteractiveShell()
    shell.run_line_magic('matplotlib', 'inline')

    old_cwd = Path.cwd()
    os.chdir(notebook_path.parent)
    try:
        exec_count = 1
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') != 'code':
                continue

            source = ''.join(cell.get('source', []))
            cell['outputs'] = []
            if not source.strip():
                cell['execution_count'] = None
                continue

            with capture_output(display=True) as captured:
                result = shell.run_cell(source)

            outputs: List[Dict[str, Any]] = []
            _append_text_stream(outputs, 'stdout', captured.stdout)
            _append_text_stream(outputs, 'stderr', captured.stderr)
            outputs.extend(_serialize_display_output(output) for output in captured.outputs)

            if result.error_before_exec or result.error_in_exec:
                err = result.error_before_exec or result.error_in_exec
                tb = traceback.format_exception(type(err), err, err.__traceback__)
                outputs.append({
                    'output_type': 'error',
                    'ename': type(err).__name__,
                    'evalue': str(err),
                    'traceback': tb,
                })
                cell['outputs'] = outputs
                cell['execution_count'] = exec_count
                _write_notebook(notebook_path, notebook)
                raise NotebookExecutionError(f'Notebook execution failed in {notebook_path.name}: {err}')

            if result.result is not None:
                outputs.append({
                    'output_type': 'execute_result',
                    'data': {'text/plain': repr(result.result)},
                    'metadata': {},
                    'execution_count': exec_count,
                })

            cell['outputs'] = outputs
            cell['execution_count'] = exec_count
            exec_count += 1

        _write_notebook(notebook_path, notebook)
    finally:
        os.chdir(old_cwd)
