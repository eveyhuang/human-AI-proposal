# Compare Proposals Analysis Guide

## Overview

`compare_proposals.ipynb` implements comprehensive diversity analysis comparing AI-generated proposals against human-written proposals using biomedical embeddings and statistical tests.

## What This Notebook Does

### 1. **Data Loading & Embedding**
- Loads AI proposals from `data/ai-proposals/baseline/`
- Loads human proposals from `data/human-proposals/`
- Uses **PubMedBERT** (biomedical domain-specific) to embed all proposals
- Saves embeddings to `data/embeddings/` for reuse

### 2. **Three Diversity Analyses**

#### **Analysis 2.1.1: Within-Group Pairwise Diversity**
- **What**: Compares average pairwise distances within each group
- **Metric**: Cosine distance between all proposal pairs
- **Tests**: Mann-Whitney U, Cliff's delta, permutation test (10k iterations)
- **Output**: Distribution plots, box plots with statistical annotations

#### **Analysis 2.1.2: Centroid Dispersion**
- **What**: Measures how scattered proposals are from their group center
- **Metric**: Distance from each proposal to group centroid
- **Tests**: Mann-Whitney U, Cliff's delta, permutation test
- **Output**: Violin plots, scatter plots with means

#### **Analysis 2.1.3: Nearest-Neighbor Outlier Detection**
- **What**: Identifies "lone wolf" ideas far from all others
- **Metric**: Distance to nearest neighbor (across all proposals)
- **Tests**: Mann-Whitney U, Cliff's delta
- **Outputs**: 
  - NN distance distributions
  - Outlier counts (top 10%)
  - NN group membership analysis

### 3. **Statistical Rigor**
All analyses include:
- ✅ **Mann-Whitney U test** (non-parametric, robust to non-normal distributions)
- ✅ **Cliff's Delta effect size** (interpretable: negligible/small/medium/large)
- ✅ **Permutation tests** (10,000 iterations for robust p-values)
- ✅ **Multiple visualizations** (distributions, box plots, violin plots)

### 4. **Output Files**

```
results/
├── figures/
│   ├── pairwise_diversity.png
│   ├── centroid_dispersion.png
│   └── nearest_neighbor_analysis.png
└── diversity_analysis_summary_YYYYMMDD_HHMMSS.json

data/embeddings/
└── proposal_embeddings_YYYYMMDD_HHMMSS.pkl
```

---

## How to Run

### Prerequisites

1. **Install dependencies** (if not already installed):
```bash
pip install transformers torch scikit-learn scipy matplotlib seaborn plotly pandas
```

2. **Generate AI proposals first**:
   - Run `gen_proposals.ipynb` to create AI proposals
   - Ensure `data/ai-proposals/baseline/ai_proposals_baseline_complete_*.csv` exists

3. **Have human proposals ready**:
   - Place in `data/human-proposals/*.json`
   - Expected structure: JSON files with `title`, `abstract`, `full_text` fields

### Running the Analysis

1. Open `compare_proposals.ipynb` in Jupyter
2. Run all cells sequentially (Kernel → Run All)
3. Expected runtime:
   - Embedding generation: ~2-5 minutes (GPU) or ~10-20 minutes (CPU)
   - Statistical analyses: ~1-2 minutes
   - Total: ~15-25 minutes

### GPU Acceleration

The notebook automatically uses GPU if available:
- With GPU: Much faster embedding generation
- Without GPU: Works fine, just slower

Check GPU status in first cell output:
```
✓ CUDA available: True  # or False
```

---

## Interpreting Results

### Cliff's Delta Effect Size

| |δ| Range | Interpretation |
|-----------|----------------|
| < 0.147 | Negligible |
| 0.147 - 0.33 | Small |
| 0.33 - 0.474 | Medium |
| ≥ 0.474 | Large |

**Sign interpretation:**
- δ > 0: AI group has higher values (more diverse)
- δ < 0: Human group has higher values (more diverse)

### P-value Interpretation

- p < 0.001: *** (highly significant)
- p < 0.01: ** (very significant)
- p < 0.05: * (significant)
- p ≥ 0.05: ns (not significant)

### What Each Metric Tells You

1. **Pairwise Diversity**
   - Higher = proposals are more different from each other
   - Captures overall within-group heterogeneity

2. **Centroid Dispersion**
   - Higher = proposals scattered further from center
   - Can reveal if diversity comes from subclusters vs uniform spread

3. **Nearest-Neighbor Distance**
   - Higher = more "lone wolf" ideas
   - Outlier count = how many truly unique ideas
   - NN group membership = are proposals more similar to own group or other group?

---

## Customization Options

### Change Embedding Model

Replace PubMedBERT with another model:

```python
# In the "Generate Embeddings" cell, change:
model_name = "allenai/scibert_scivocab_uncased"  # General science
# or
model_name = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"  # Biomedical
```

### Adjust Outlier Threshold

Change from top 10% to top 5%:

```python
# In "Nearest-Neighbor Outlier Detection" section:
threshold = np.percentile(nn_distances, 95)  # was 90
```

### Modify Statistical Tests

Add more permutations for higher precision:

```python
p_value_perm, obs_diff, perm_diffs = permutation_test(
    ai_pairwise, 
    human_pairwise,
    n_permutations=50000  # was 10000
)
```

---

## Troubleshooting

### "No AI proposal files found"
**Solution**: Run `gen_proposals.ipynb` first to generate AI proposals.

### "ModuleNotFoundError: No module named 'transformers'"
**Solution**: Install required packages:
```bash
pip install transformers torch
```

### Out of Memory (OOM) Error
**Solutions**:
1. Reduce batch size:
   ```python
   embeddings = get_embeddings(texts, batch_size=4)  # was 8
   ```
2. Reduce max_length:
   ```python
   embeddings = get_embeddings(texts, max_length=256)  # was 512
   ```
3. Use CPU instead of GPU (automatically falls back)

### Slow Embedding Generation
**Solutions**:
1. Use GPU if available
2. Reduce max_length (proposals are truncated anyway)
3. Cache embeddings (notebook does this automatically in `data/embeddings/`)

---

## Expected Output Example

```
📊 SAMPLE SIZES:
  Human proposals: 23
  AI proposals: 69
    - gpt-5.2: 23
    - gemini-3-pro-preview: 23
    - claude-opus-4-6: 23

📏 PAIRWISE DIVERSITY:
  Human mean distance: 0.3245
  AI mean distance: 0.3789
  Cliff's δ: 0.2145 (small)
  p-value: 0.0234

🎯 CENTROID DISPERSION:
  Human mean distance: 0.2891
  AI mean distance: 0.3156
  Cliff's δ: 0.1876 (small)
  p-value: 0.0456

🔍 NEAREST NEIGHBOR:
  Human mean NN distance: 0.1234
  AI mean NN distance: 0.1567
  Human outliers: 2 / 23
  AI outliers: 9 / 69
  Cliff's δ: 0.3012 (small)
  p-value: 0.0123
```

---

## Next Steps

After running this analysis:

1. **Examine figures** in `results/figures/`
2. **Review JSON summary** in `results/diversity_analysis_summary_*.json`
3. **Compare across AI models** (add per-model analysis)
4. **Validate findings** (check if outliers make sense)
5. **Write up results** for your paper

---

## Citation

If you use this analysis approach, consider citing:

- **PubMedBERT**: Gu et al. (2021). Domain-Specific Language Model Pretraining for Biomedical Natural Language Processing
- **Cliff's Delta**: Cliff (1993). Dominance statistics: Ordinal analyses to answer ordinal questions
- **Cosine Distance**: Standard metric in NLP/embedding similarity

---

## Questions?

See the main analysis plan: `docs/analysis_plan.md`

For implementation details, check the notebook cells with detailed comments.
