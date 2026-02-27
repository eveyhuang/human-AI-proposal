# Quality Analysis Slides Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace slides 18–19 of the existing PPTX with a 13-slide quality analysis section covering R1 (proxy validity), R2 (proposal quality), R3 (self-preference bias), two sensitivity analyses, and a final summary.

**Architecture:** Direct PPTX ZIP manipulation using Python stdlib (zipfile + xml.etree). No python-pptx dependency. Build on existing `workspace/add_quality_slides_to_pptx.py` patterns. Script at `workspace/add_quality_slides_v2.py`.

**Tech Stack:** Python 3, zipfile, xml.etree.ElementTree, csv, shutil, tempfile

---

## Slide Structure (13 new slides, replacing slides 18–19)

| New # | Title |
|-------|-------|
| 18 | Part IV Quality: Why Three Linked Analyses? |
| 19 | R1 Method: Validating the Evaluation Instrument Before Interpreting Scores |
| 20 | R1 Results: AI Reviews Align With Humans—But AI Judges Are Unusually Homogeneous |
| 21 | R2 Setup: Verifying Human Baseline Comparability (Y1 vs Y2) |
| 22 | R2 Baseline: AI-Generated Proposals Score Higher Under AI Evaluation |
| 23 | R2 Criterion Decomposition: The AI Advantage Is Model- and Dimension-Specific |
| 24 | R3 Step 1: AI Evaluators Differ Substantially in Scoring Leniency |
| 25 | R3 Step 2: Self-Preference Is Large in Magnitude and Model-Divergent |
| 26 | R3 Step 3: Self-Preference Survives Proposal-Quality Controls |
| 27 | R3→R2: Why Bias-Controlled Reruns Are Necessary Before Drawing Conclusions |
| 28 | Sensitivity 1 — Cross-Evaluator Only: GPT Advantage Robust, Gemini Attenuates |
| 29 | Sensitivity 2 — Gemini-Only Evaluator: Claude Falls Below Human Baseline |
| 30 | Summary: Big Picture, Key Takeaways, and Next Steps |

## Figures Used

All from `results/figures/quality/`:
- Slide 19: `quality_similarity_proxy_paired_slopes.png`
- Slide 20: `quality_similarity_human_ai_by_model_proposal_level.png` + `quality_similarity_ai_ai_by_model_pair_proposal_level.png`
- Slide 22: `quality_overall_boxplot_proposal_level.png` + `quality_radar_criteria_proposal_level.png`
- Slide 23: `quality_effect_size_heatmap.png` + `quality_effect_size_dotplot.png`
- Slide 24: `quality_overall_by_evaluator_clean.png`
- Slide 25: `self_pref_strip_overall.png` + `self_pref_criterion_heatmap.png`
- Slide 26: `self_pref_regression_forest.png`
- Slide 28: `quality_overall_boxplot_proposal_level_cross_eval_only.png` + `quality_effectsize_heatmap_cross_eval_only.png`
- Slide 29: `quality_overall_boxplot_proposal_level_gemini_only.png` + `quality_effectsize_heatmap_gemini_only.png`

## CSVs Read for Statistics

All from `results/figures/quality/`:
- `quality_similarity_mw_cliffs_overall.csv`
- `quality_summary_overall_by_author_group.csv`
- `quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv`
- `quality_robust_bootstrap_permutation_key_comparisons.csv`
- `quality_evaluator_overall_stats_clean.csv`
- `quality_self_preference_tests_overall.csv`
- `quality_vs_ai_mw_cliffs_cross_eval_only.csv`
- `quality_robust_bootstrap_permutation_cross_eval_only.csv`
- `quality_summary_overall_by_author_group_cross_eval_only.csv`
- `quality_vs_ai_mw_cliffs_gemini_only.csv`
- `quality_robust_bootstrap_permutation_gemini_only.csv`
- `quality_summary_overall_by_author_group_gemini_only.csv`
- `quality_human_cohort_mw_cliffs_cross_eval_only.csv` (Y1 vs Y2)

## Key Operations

1. Extract PPTX to temp dir
2. Delete slides 18 and 19: remove slide XML files, slide rels files, entries from sldIdLst, presentation.xml.rels, and [Content_Types].xml
3. Read all CSVs and populate `vals` dict with formatted statistics
4. Generate 13 slide XMLs + copy images
5. Register each slide in presentation.xml, presentation.xml.rels, [Content_Types].xml
6. Backup original PPTX, repack as new PPTX

---

### Task 1: Write workspace/add_quality_slides_v2.py

**File:** `workspace/add_quality_slides_v2.py`

**Step 1:** Write the complete Python script (see implementation below)

**Step 2:** Run the script:
```bash
cd /Users/eveyhuang/Documents/NICO/human-AI-proposal
python workspace/add_quality_slides_v2.py
```
Expected output: `Added 13 slides to .../diversity_analysis_presentation_baseline_updated_20260218.pptx` and `Backup: ...pptx.bak`

**Step 3:** Verify slide count:
```bash
python3 -c "
import zipfile, re
with zipfile.ZipFile('results/diversity_analysis_presentation_baseline_updated_20260218.pptx') as zf:
    slides = [n for n in zf.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]
    print(f'Total slides: {len(slides)}')
"
```
Expected: `Total slides: 30`
