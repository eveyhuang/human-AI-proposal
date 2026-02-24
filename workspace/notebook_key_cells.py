
########################################################################################################################
CELL 21
########################################################################################################################
def compute_pairwise_distances(embeddings):
    """
    Compute pairwise cosine distances within a group.
    Returns upper triangle (excluding diagonal) as 1D array.
    """
    # Cosine distance matrix
    dist_matrix = cosine_distances(embeddings)
    
    # Extract upper triangle (excluding diagonal)
    n = len(embeddings)
    indices = np.triu_indices(n, k=1)
    pairwise_dists = dist_matrix[indices]
    
    return pairwise_dists

# Compute pairwise distances for all groups
print("="*85)
print("COMPUTING PAIRWISE DISTANCES FOR ALL GROUPS")
print("="*85)

# Overall groups
ai_pairwise = compute_pairwise_distances(ai_embeddings)
human_pairwise = compute_pairwise_distances(human_embeddings)

# Individual AI models - split by model
ai_models = sorted(ai_df['model'].unique())
model_pairwise = {}
model_embeddings_dict = {}

for model in ai_models:
    model_mask = ai_df['model'] == model
    model_embeds = ai_embeddings[model_mask]
    model_embeddings_dict[model] = model_embeds
    
    if len(model_embeds) > 1:  # Need at least 2 proposals for pairwise comparison
        model_pairwise[model] = compute_pairwise_distances(model_embeds)
    else:
        model_pairwise[model] = np.array([])

# Print statistics table
print(f"\n{'GROUP':<35} {'N':<8} {'Pairs':<10} {'Mean':<10} {'Median':<10} {'Std':<10}")
print("-"*85)

# Human baseline
print(f"{'Human':<35} {len(human_embeddings):<8} {len(human_pairwise):<10} {human_pairwise.mean():<10.4f} {np.median(human_pairwise):<10.4f} {human_pairwise.std():<10.4f}")

print()  # Blank line separator

# Individual AI models
for model in ai_models:
    if len(model_pairwise[model]) > 0:
        n_proposals = len(model_embeddings_dict[model])
        n_pairs = len(model_pairwise[model])
        mean_dist = model_pairwise[model].mean()
        median_dist = np.median(model_pairwise[model])
        std_dist = model_pairwise[model].std()
        print(f"{model:<35} {n_proposals:<8} {n_pairs:<10} {mean_dist:<10.4f} {median_dist:<10.4f} {std_dist:<10.4f}")

print()  # Blank line separator

# All AI combined
print(f"{'All AI (combined)':<35} {len(ai_embeddings):<8} {len(ai_pairwise):<10} {ai_pairwise.mean():<10.4f} {np.median(ai_pairwise):<10.4f} {ai_pairwise.std():<10.4f}")

print("="*85)
print("\n💡 INTERPRETATION:")
print("   - MEAN: Average distance (affected by outliers)")
print("   - MEDIAN: Typical distance (robust to outliers)")
print("   - Higher median = more consistently diverse proposals")
print("   - Mean > Median = distribution has high outliers")
print("\n💡 INTERPRETATION:")
print("   - Higher mean distance = more diverse proposals within group")
print("   - Compare each AI model to Human to see which produces human-like diversity")
print("="*85)
print("\n💡 INTERPRETATION:")
print("   - MEAN: Average distance (affected by outliers)")
print("   - MEDIAN: Typical distance (robust to outliers)")
print("   - Higher median = more consistently diverse proposals")
print("   - Mean > Median = distribution has high outliers")

########################################################################################################################
CELL 22
########################################################################################################################
# DIAGNOSTIC: Verify pairwise distance calculations and Cliff's Delta
print("="*85)
print("DIAGNOSTIC CHECK: Pairwise Distances and Statistical Tests")
print("="*85)

# Show actual mean values
print("\n1. ACTUAL MEAN PAIRWISE DISTANCES:")
print("-"*85)
print(f"Human:                         {human_pairwise.mean():.6f}")
for model in ai_models:
    if model in model_pairwise and len(model_pairwise[model]) > 0:
        print(f"{model:<30} {model_pairwise[model].mean():.6f}")
print(f"All AI (combined):             {ai_pairwise.mean():.6f}")

# Manually verify Cliff's Delta calculation for gemini
print("\n2. MANUAL CLIFF'S DELTA VERIFICATION (gemini vs human):")
print("-"*85)
if 'gemini-3-pro-preview' in model_pairwise:
    gemini_dist = model_pairwise['gemini-3-pro-preview']
    
    # Calculate Cliff's Delta manually
    n1, n2 = len(gemini_dist), len(human_pairwise)
    dominance = 0
    for x in gemini_dist:
        for y in human_pairwise:
            if x > y:
                dominance += 1
            elif x < y:
                dominance -= 1
    
    delta_manual = dominance / (n1 * n2)
    
    print(f"Gemini pairwise distances: n={len(gemini_dist)}, mean={gemini_dist.mean():.6f}")
    print(f"Human pairwise distances:  n={len(human_pairwise)}, mean={human_pairwise.mean():.6f}")
    print(f"\nDifference in means: {gemini_dist.mean() - human_pairwise.mean():.6f}")
    print(f"Cliff's Delta (manual calculation): {delta_manual:.4f}")
    print(f"\nInterpretation:")
    if delta_manual > 0:
        print(f"  → Positive δ means Gemini values tend to be HIGHER than Human")
        print(f"  → Gemini proposals are MORE diverse")
    else:
        print(f"  → Negative δ means Human values tend to be HIGHER than Gemini")
        print(f"  → Human proposals are MORE diverse")
    
    # Show distribution statistics
    print(f"\n3. DISTRIBUTION DETAILS:")
    print("-"*85)
    print(f"Gemini: min={gemini_dist.min():.6f}, max={gemini_dist.max():.6f}, "
          f"q25={np.percentile(gemini_dist, 25):.6f}, q75={np.percentile(gemini_dist, 75):.6f}")
    print(f"Human:  min={human_pairwise.min():.6f}, max={human_pairwise.max():.6f}, "
          f"q25={np.percentile(human_pairwise, 25):.6f}, q75={np.percentile(human_pairwise, 75):.6f}")
    
    # Count how many pairs fall into different ranges
    print(f"\n4. DISTRIBUTION OVERLAP:")
    print("-"*85)
    gemini_above_human_mean = (gemini_dist > human_pairwise.mean()).sum()
    human_above_gemini_mean = (human_pairwise > gemini_dist.mean()).sum()
    print(f"Gemini pairs above human mean: {gemini_above_human_mean}/{len(gemini_dist)} ({gemini_above_human_mean/len(gemini_dist)*100:.1f}%)")
    print(f"Human pairs above gemini mean: {human_above_gemini_mean}/{len(human_pairwise)} ({human_above_gemini_mean/len(human_pairwise)*100:.1f}%)")
    
print("\n" + "="*85)
print("KEY INSIGHT:")
print("Cliff's Delta looks at ALL pairwise comparisons, not just means.")
print("A negative δ means the MAJORITY of individual comparisons favor the second group.")
print("="*85)

print("\n" + "="*85)
print("EXPLANATION OF THE PARADOX:")
print("="*85)
if "gemini-3-pro-preview" in model_pairwise:
    gemini_dist = model_pairwise["gemini-3-pro-preview"]
    print(f"\nGemini mean ({gemini_dist.mean():.4f}) > Human mean ({human_pairwise.mean():.4f})")
    print(f"BUT Gemini median ({np.median(gemini_dist):.4f}) < Human median ({np.median(human_pairwise):.4f})")
    print(f"\nThis means:")
    print(f"  ✓ Gemini has extreme outliers (max={gemini_dist.max():.3f}) pulling mean UP")
    print(f"  ✓ But MOST Gemini pairs have LOW distances (Q75={np.percentile(gemini_dist, 75):.3f})")
    print(f"  ✓ Human pairs are more CONSISTENTLY diverse (Q25-Q75: {np.percentile(human_pairwise, 25):.3f}-{np.percentile(human_pairwise, 75):.3f})")
    print(f"\n  → Cliffs Delta correctly identifies that TYPICAL Gemini pairs are less diverse")
    print(f"  → The few outliers do not represent typical diversity")
print("="*85)

print("\n" + "="*85)
print("EXPLANATION OF THE PARADOX:")
print("="*85)
if "gemini-3-pro-preview" in model_pairwise:
    gemini_dist = model_pairwise["gemini-3-pro-preview"]
    print(f"\nGemini mean ({gemini_dist.mean():.4f}) > Human mean ({human_pairwise.mean():.4f})")
    print(f"BUT Gemini median ({np.median(gemini_dist):.4f}) < Human median ({np.median(human_pairwise):.4f})")
    print(f"\nThis means:")
    print(f"  ✓ Gemini has extreme outliers (max={gemini_dist.max():.3f}) pulling mean UP")
    print(f"  ✓ But MOST Gemini pairs have LOW distances (Q75={np.percentile(gemini_dist, 75):.3f})")
    print(f"  ✓ Human pairs are more CONSISTENTLY diverse (Q25-Q75: {np.percentile(human_pairwise, 25):.3f}-{np.percentile(human_pairwise, 75):.3f})")
    print(f"\n  → Cliffs Delta correctly identifies that TYPICAL Gemini pairs are less diverse")
    print(f"  → The few outliers do not represent typical diversity")
print("="*85)


########################################################################################################################
CELL 23
########################################################################################################################
# Statistical tests - Compare each group to Human
print("\n" + "="*85)
print("STATISTICAL TESTS: Pairwise Diversity (All Groups vs Human)")
print("="*85)

# Store all results
comparison_results = []

# Compare All AI vs Human
print("\n" + "-"*85)
print("Comparison: All AI (combined) vs Human")
print("-"*85)

u_stat, p_value_mw = mannwhitneyu(ai_pairwise, human_pairwise, alternative='two-sided')
delta = cliffs_delta(ai_pairwise, human_pairwise)
delta_interp = interpret_cliffs_delta(delta)
p_value_perm, obs_diff, perm_diffs = permutation_test(ai_pairwise, human_pairwise)

print(f"\nMann-Whitney U Test:")
print(f"  U-statistic: {u_stat:,.0f}, p-value: {p_value_mw:.4e}")
print(f"\nCliff's Delta:")
print(f"  δ = {delta:.4f} ({delta_interp} effect)")
if delta > 0:
    print(f"  → All AI proposals are MORE diverse than human proposals")
else:
    print(f"  → Human proposals are MORE diverse than all AI proposals")
print(f"\nPermutation Test (10,000 permutations):")
print(f"  Observed difference: {obs_diff:.4f}, p-value: {p_value_perm:.4f}")

comparison_results.append({
    'group': 'All AI',
    'u_stat': u_stat,
    'p_value_mw': p_value_mw,
    'delta': delta,
    'delta_interp': delta_interp,
    'p_value_perm': p_value_perm
})

# Compare each individual AI model vs Human
for model in ai_models:
    if len(model_pairwise[model]) > 0:
        print("\n" + "-"*85)
        print(f"Comparison: {model} vs Human")
        print("-"*85)
        
        u_stat_model, p_value_mw_model = mannwhitneyu(model_pairwise[model], human_pairwise, alternative='two-sided')
        delta_model = cliffs_delta(model_pairwise[model], human_pairwise)
        delta_interp_model = interpret_cliffs_delta(delta_model)
        p_value_perm_model, obs_diff_model, _ = permutation_test(model_pairwise[model], human_pairwise)
        
        print(f"\nMann-Whitney U Test:")
        print(f"  U-statistic: {u_stat_model:,.0f}, p-value: {p_value_mw_model:.4e}")
        print(f"\nCliff's Delta:")
        print(f"  δ = {delta_model:.4f} ({delta_interp_model} effect)")
        if delta_model > 0:
            print(f"  → {model} proposals are MORE diverse than human proposals")
        else:
            print(f"  → Human proposals are MORE diverse than {model} proposals")
        print(f"\nPermutation Test (10,000 permutations):")
        print(f"  Observed difference: {obs_diff_model:.4f}, p-value: {p_value_perm_model:.4f}")
        
        comparison_results.append({
            'group': model,
            'u_stat': u_stat_model,
            'p_value_mw': p_value_mw_model,
            'delta': delta_model,
            'delta_interp': delta_interp_model,
            'p_value_perm': p_value_perm_model
        })

# Summary table
print("\n" + "="*85)
print("SUMMARY: Effect Sizes (Cliff's Delta) - All Groups vs Human")
print("="*85)
print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
print("-"*85)
for result in comparison_results:
    print(f"{result['group']:<30} {result['delta']:<12.4f} {result['delta_interp']:<20} {result['p_value_mw']:<15.4e}")
print("="*85)
print("\nIMPORTANT NOTE:")
print("  Cliff's Delta measures TYPICAL diversity (distribution-based), not mean.")
print("  A group can have higher mean due to outliers but lower typical diversity.")
print("  Check both mean AND median in the summary table above.")
print("\nIMPORTANT NOTE:")
print("  Cliffs Delta measures TYPICAL diversity (distribution-based), not mean.")
print("  A group can have higher mean due to outliers but lower typical diversity.")
print("  Check both mean AND median in the summary table above.")

print("\n💡 Positive δ = AI more diverse; Negative δ = Human more diverse")
print("="*85)


########################################################################################################################
CELL 26
########################################################################################################################
def compute_centroid_distances(embeddings):
    """
    Compute distances from each proposal to its group centroid.
    """
    # Compute centroid (mean embedding)
    centroid = embeddings.mean(axis=0, keepdims=True)
    
    # Compute cosine distances to centroid
    distances = cosine_distances(embeddings, centroid).flatten()
    
    return distances, centroid

# Compute centroid distances for all groups
print("="*85)
print("COMPUTING CENTROID DISPERSION FOR ALL GROUPS")
print("="*85)

# Overall groups
ai_centroid_dists, ai_centroid = compute_centroid_distances(ai_embeddings)
human_centroid_dists, human_centroid = compute_centroid_distances(human_embeddings)

# Individual AI models
model_centroid_dists = {}
model_centroids = {}

for model in ai_models:
    if len(model_embeddings_dict[model]) > 0:
        dists, centroid = compute_centroid_distances(model_embeddings_dict[model])
        model_centroid_dists[model] = dists
        model_centroids[model] = centroid

# Print statistics table
print(f"\n{'GROUP':<35} {'N':<8} {'Mean':<10} {'Median':<10} {'Std':<10} {'Variance':<10}")
print("-"*90)

# Human baseline
print(f"{'Human':<35} {len(human_embeddings):<8} {human_centroid_dists.mean():<10.4f} {np.median(human_centroid_dists):<10.4f} {human_centroid_dists.std():<10.4f} {human_centroid_dists.var():<10.4f}")

print()  # Blank line separator

# Individual AI models
for model in ai_models:
    if model in model_centroid_dists:
        dists = model_centroid_dists[model]
        n_proposals = len(model_embeddings_dict[model])
        print(f"{model:<35} {n_proposals:<8} {dists.mean():<10.4f} {np.median(dists):<10.4f} {dists.std():<10.4f} {dists.var():<10.4f}")

print()  # Blank line separator

# All AI combined
print(f"{'All AI (combined)':<35} {len(ai_embeddings):<8} {ai_centroid_dists.mean():<10.4f} {np.median(ai_centroid_dists):<10.4f} {ai_centroid_dists.std():<10.4f} {ai_centroid_dists.var():<10.4f}")

print("="*90)
print("\n💡 INTERPRETATION:")
print("   - Higher variance = more dispersed proposals (higher diversity)")
print("   - Lower variance = proposals cluster tightly around center")
print("="*90)


########################################################################################################################
CELL 27
########################################################################################################################
# Statistical tests - Compare each group to Human
print("\n" + "="*85)
print("STATISTICAL TESTS: Centroid Dispersion (All Groups vs Human)")
print("="*85)

# Store all results
centroid_comparison_results = []

# Compare All AI vs Human
print("\n" + "-"*85)
print("Comparison: All AI (combined) vs Human")
print("-"*85)

u_stat_cent, p_value_cent = mannwhitneyu(ai_centroid_dists, human_centroid_dists, alternative='two-sided')
delta_cent = cliffs_delta(ai_centroid_dists, human_centroid_dists)
delta_cent_interp = interpret_cliffs_delta(delta_cent)
p_value_perm_cent, obs_diff_cent, _ = permutation_test(ai_centroid_dists, human_centroid_dists)

print(f"\nMann-Whitney U Test:")
print(f"  U-statistic: {u_stat_cent:,.0f}, p-value: {p_value_cent:.4e}")
print(f"\nCliff's Delta:")
print(f"  δ = {delta_cent:.4f} ({delta_cent_interp} effect)")
if delta_cent > 0:
    print(f"  → All AI proposals are MORE dispersed from center")
else:
    print(f"  → Human proposals are MORE dispersed from center")
print(f"\nPermutation Test (10,000 permutations):")
print(f"  Observed difference: {obs_diff_cent:.4f}, p-value: {p_value_perm_cent:.4f}")

centroid_comparison_results.append({
    'group': 'All AI',
    'u_stat': u_stat_cent,
    'p_value_mw': p_value_cent,
    'delta': delta_cent,
    'delta_interp': delta_cent_interp,
    'p_value_perm': p_value_perm_cent
})

# Compare each individual AI model vs Human
for model in ai_models:
    if model in model_centroid_dists:
        print("\n" + "-"*85)
        print(f"Comparison: {model} vs Human")
        print("-"*85)
        
        u_stat_model, p_value_mw_model = mannwhitneyu(model_centroid_dists[model], human_centroid_dists, alternative='two-sided')
        delta_model = cliffs_delta(model_centroid_dists[model], human_centroid_dists)
        delta_interp_model = interpret_cliffs_delta(delta_model)
        p_value_perm_model, obs_diff_model, _ = permutation_test(model_centroid_dists[model], human_centroid_dists)
        
        print(f"\nMann-Whitney U Test:")
        print(f"  U-statistic: {u_stat_model:,.0f}, p-value: {p_value_mw_model:.4e}")
        print(f"\nCliff's Delta:")
        print(f"  δ = {delta_model:.4f} ({delta_interp_model} effect)")
        if delta_model > 0:
            print(f"  → {model} proposals are MORE dispersed from center")
        else:
            print(f"  → Human proposals are MORE dispersed from center")
        print(f"\nPermutation Test (10,000 permutations):")
        print(f"  Observed difference: {obs_diff_model:.4f}, p-value: {p_value_perm_model:.4f}")
        
        centroid_comparison_results.append({
            'group': model,
            'u_stat': u_stat_model,
            'p_value_mw': p_value_mw_model,
            'delta': delta_model,
            'delta_interp': delta_interp_model,
            'p_value_perm': p_value_perm_model
        })

# Summary table
print("\n" + "="*85)
print("SUMMARY: Effect Sizes (Cliff's Delta) - Centroid Dispersion")
print("="*85)
print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
print("-"*85)
for result in centroid_comparison_results:
    print(f"{result['group']:<30} {result['delta']:<12.4f} {result['delta_interp']:<20} {result['p_value_mw']:<15.4e}")
print("="*85)
print("\n💡 Positive δ = AI more dispersed; Negative δ = Human more dispersed")
print("="*85)


########################################################################################################################
CELL 30
########################################################################################################################
# Combine all embeddings for global nearest-neighbor analysis
all_embeddings = np.vstack([human_embeddings, ai_embeddings])
n_human = len(human_embeddings)
n_ai = len(ai_embeddings)

# Build per-row labels aligned to embedding order (avoid assuming contiguous blocks by model)
if 'ai_metadata' in globals() and isinstance(ai_metadata, list) and len(ai_metadata) == n_ai:
    ai_model_labels = [str(r.get('model', 'AI')) for r in ai_metadata]
elif 'ai_df' in globals() and len(ai_df) == n_ai and 'model' in ai_df.columns:
    print("⚠️ ai_metadata not available; falling back to ai_df['model'] order (may misalign if embeddings were shuffled).")
    ai_model_labels = [str(x) for x in ai_df['model'].tolist()]
else:
    raise RuntimeError("Cannot infer AI model labels aligned to ai_embeddings. Need ai_metadata (preferred) or ai_df with matching order.")

labels = np.array((['Human'] * n_human) + ai_model_labels)
ai_models_local = [m for m in sorted(list(dict.fromkeys(ai_model_labels))) if m is not None]

# Compute full distance matrix
print("="*85)
print("COMPUTING NEAREST-NEIGHBOR DISTANCES FOR ALL GROUPS")
print("="*85)

all_distances = cosine_distances(all_embeddings)
np.fill_diagonal(all_distances, np.inf)
nn_distances = all_distances.min(axis=1)

# Split by group
human_nn_dists = nn_distances[labels == 'Human']
ai_nn_dists = nn_distances[labels != 'Human']

# Extract per-model NN distances using label masks
model_nn_dists = {m: nn_distances[labels == m] for m in ai_models_local}

# Print statistics table
print(f"\n{'GROUP':<35} {'N':<8} {'Mean':<10} {'Median':<10} {'Min':<10} {'Max':<10}")
print("-"*85)

print(f"{'Human':<35} {len(human_nn_dists):<8} {human_nn_dists.mean():<10.4f} {np.median(human_nn_dists):<10.4f} {human_nn_dists.min():<10.4f} {human_nn_dists.max():<10.4f}")
print()

for model in ai_models_local:
    dists = model_nn_dists[model]
    print(f"{model:<35} {len(dists):<8} {dists.mean():<10.4f} {np.median(dists):<10.4f} {dists.min():<10.4f} {dists.max():<10.4f}")

print()
print(f"{'All AI (combined)':<35} {len(ai_nn_dists):<8} {ai_nn_dists.mean():<10.4f} {np.median(ai_nn_dists):<10.4f} {ai_nn_dists.min():<10.4f} {ai_nn_dists.max():<10.4f}")

print("="*85)
print("\n💡 INTERPRETATION:")
print("   - Higher mean NN distance = more isolated proposals (outliers)")
print("   - Lower mean NN distance = proposals cluster together")
print("="*85)


########################################################################################################################
CELL 31
########################################################################################################################
# Identify outliers (top 10% of NN distances)
threshold = np.percentile(nn_distances, 90)
outliers = nn_distances > threshold

human_outliers = int(outliers[labels == 'Human'].sum())
ai_outliers = int(outliers[labels != 'Human'].sum())

# Per-model outlier detection (do NOT slice by contiguous blocks)
model_outliers = {m: int(outliers[labels == m].sum()) for m in ai_models_local}

print("\n" + "="*85)
print("OUTLIER DETECTION (Top 10% Nearest-Neighbor Distance)")
print("="*85)
print(f"Threshold distance: {threshold:.4f}")
print()

print(f"{'GROUP':<35} {'Outliers':<15} {'Total':<10} {'Percentage':<15}")
print("-"*85)

print(f"{'Human':<35} {human_outliers:<15} {n_human:<10} {human_outliers/n_human*100:<15.1f}%")
print()

for model in ai_models_local:
    n_model = int((labels == model).sum())
    print(f"{model:<35} {model_outliers[model]:<15} {n_model:<10} {model_outliers[model]/n_model*100:<15.1f}%")

print()
print(f"{'All AI (combined)':<35} {ai_outliers:<15} {n_ai:<10} {ai_outliers/n_ai*100:<15.1f}%")

print("="*85)


########################################################################################################################
CELL 32
########################################################################################################################
# Find nearest neighbor's group for each proposal
nn_indices = all_distances.argmin(axis=1)
nn_labels = labels[nn_indices]

# Determine if NN is from same or different group
human_nn_same_group = int((nn_labels[labels == 'Human'] == 'Human').sum())
human_nn_diff_group = int(n_human - human_nn_same_group)

ai_nn_same_group = int((nn_labels[labels != 'Human'] != 'Human').sum())
ai_nn_diff_group = int(n_ai - ai_nn_same_group)

# Per-model nearest neighbor group analysis (mask-based)
model_nn_analysis = {}
for model in ai_models_local:
    mask = labels == model
    total = int(mask.sum())
    nn_from_human = int((nn_labels[mask] == 'Human').sum())
    nn_from_same_model = int((nn_labels[mask] == model).sum())
    nn_from_other_ai = int(total - nn_from_human - nn_from_same_model)

    model_nn_analysis[model] = {
        'from_human': nn_from_human,
        'from_same_model': nn_from_same_model,
        'from_other_ai': nn_from_other_ai,
        'total': total
    }

print("\n" + "="*85)
print("NEAREST NEIGHBOR GROUP ANALYSIS")
print("="*85)

print(f"\n{'Human proposals:':<50}")
print(f"  NN from same group (human): {human_nn_same_group} ({human_nn_same_group/n_human*100:.1f}%)")
print(f"  NN from different group (AI): {human_nn_diff_group} ({human_nn_diff_group/n_human*100:.1f}%)")

print(f"\n{'All AI proposals (combined):':<50}")
print(f"  NN from same group (AI): {ai_nn_same_group} ({ai_nn_same_group/n_ai*100:.1f}%)")
print(f"  NN from different group (human): {ai_nn_diff_group} ({ai_nn_diff_group/n_ai*100:.1f}%)")

print("\n" + "-"*85)
print("Per-Model NN Group Breakdown:")
print("-"*85)

for model in ai_models_local:
    data = model_nn_analysis[model]
    print(f"\n{model}:")
    print(f"  NN from Human: {data['from_human']} ({data['from_human']/data['total']*100:.1f}%)")
    print(f"  NN from same model: {data['from_same_model']} ({data['from_same_model']/data['total']*100:.1f}%)")
    print(f"  NN from other AI models: {data['from_other_ai']} ({data['from_other_ai']/data['total']*100:.1f}%)")

print("\n" + "="*85)
print("\n💡 INTERPRETATION:")
print("   - High 'NN from same model' = model produces similar proposals")
print("   - High 'NN from Human' = model proposals resemble human work")
print("="*85)


########################################################################################################################
CELL 33
########################################################################################################################
# Statistical tests - Compare each group to Human
print("\n" + "="*85)
print("STATISTICAL TESTS: Nearest-Neighbor Distances (All Groups vs Human)")
print("="*85)

# Store all results
nn_comparison_results = []

# Compare All AI vs Human
print("\n" + "-"*85)
print("Comparison: All AI (combined) vs Human")
print("-"*85)

u_stat_nn, p_value_nn = mannwhitneyu(ai_nn_dists, human_nn_dists, alternative='two-sided')
delta_nn = cliffs_delta(ai_nn_dists, human_nn_dists)
delta_nn_interp = interpret_cliffs_delta(delta_nn)
p_value_perm_nn, obs_diff_nn, _ = permutation_test(ai_nn_dists, human_nn_dists)

print(f"\nMann-Whitney U Test:")
print(f"  U-statistic: {u_stat_nn:,.0f}, p-value: {p_value_nn:.4e}")
print(f"\nCliff's Delta:")
print(f"  δ = {delta_nn:.4f} ({delta_nn_interp} effect)")
if delta_nn > 0:
    print(f"  → All AI proposals have MORE unique/outlier ideas")
else:
    print(f"  → Human proposals have MORE unique/outlier ideas")
print(f"\nPermutation Test (10,000 permutations):")
print(f"  Observed difference: {obs_diff_nn:.4f}, p-value: {p_value_perm_nn:.4f}")

nn_comparison_results.append({
    'group': 'All AI',
    'u_stat': u_stat_nn,
    'p_value_mw': p_value_nn,
    'delta': delta_nn,
    'delta_interp': delta_nn_interp,
    'p_value_perm': p_value_perm_nn
})

# Compare each individual AI model vs Human
for model in ai_models:
    if model in model_nn_dists:
        print("\n" + "-"*85)
        print(f"Comparison: {model} vs Human")
        print("-"*85)
        
        u_stat_model, p_value_mw_model = mannwhitneyu(model_nn_dists[model], human_nn_dists, alternative='two-sided')
        delta_model = cliffs_delta(model_nn_dists[model], human_nn_dists)
        delta_interp_model = interpret_cliffs_delta(delta_model)
        p_value_perm_model, obs_diff_model, _ = permutation_test(model_nn_dists[model], human_nn_dists)
        
        print(f"\nMann-Whitney U Test:")
        print(f"  U-statistic: {u_stat_model:,.0f}, p-value: {p_value_mw_model:.4e}")
        print(f"\nCliff's Delta:")
        print(f"  δ = {delta_model:.4f} ({delta_interp_model} effect)")
        if delta_model > 0:
            print(f"  → {model} proposals have MORE unique/outlier ideas")
        else:
            print(f"  → Human proposals have MORE unique/outlier ideas")
        print(f"\nPermutation Test (10,000 permutations):")
        print(f"  Observed difference: {obs_diff_model:.4f}, p-value: {p_value_perm_model:.4f}")
        
        nn_comparison_results.append({
            'group': model,
            'u_stat': u_stat_model,
            'p_value_mw': p_value_mw_model,
            'delta': delta_model,
            'delta_interp': delta_interp_model,
            'p_value_perm': p_value_perm_model
        })

# Summary table
print("\n" + "="*85)
print("SUMMARY: Effect Sizes (Cliff's Delta) - Nearest-Neighbor Distances")
print("="*85)
print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
print("-"*85)
for result in nn_comparison_results:
    print(f"{result['group']:<30} {result['delta']:<12.4f} {result['delta_interp']:<20} {result['p_value_mw']:<15.4e}")
print("="*85)
print("\n💡 Positive δ = AI more outlier-prone; Negative δ = Human more outlier-prone")
print("="*85)


########################################################################################################################
CELL 34
########################################################################################################################
import numpy as np
import pandas as pd

print("\n" + "="*85)
print("UNADJUSTED NN OUTLIERS: TITLES + AUTHOR")
print("="*85)

required = ['outliers', 'threshold', 'n_human']
missing = [v for v in required if v not in globals()]
if missing:
    print(f"⚠️ Missing variables: {missing}")
    print("Run the unadjusted NN + outlier detection cells first.")
else:
    outlier_indices = np.where(outliers)[0]
    n_total = int(len(outliers))
    n_ai = int(n_total - n_human)

    # NN distances (unadjusted)
    nn_d = np.asarray(nn_distances) if 'nn_distances' in globals() else None

    # Prefer metadata saved alongside embeddings (aligned with embedding order)
    use_meta = ('ai_metadata' in globals()) and ('human_metadata' in globals())
    if use_meta:
        if len(human_metadata) != n_human or len(ai_metadata) != n_ai:
            print("⚠️ Metadata lengths do not match embedding counts; falling back to df lookup.")
            use_meta = False

    rows = []
    for idx in outlier_indices:
        if idx < n_human:
            who = 'Human'
            model = 'Human'
            if use_meta:
                rec = human_metadata[idx]
                title = rec.get('proposal_title', rec.get('title', ''))
            else:
                title = human_df.iloc[idx].get('proposal_title', human_df.iloc[idx].get('title', '')) if 'human_df' in globals() else ''
        else:
            ai_idx = int(idx - n_human)
            who = 'AI'
            if use_meta:
                rec = ai_metadata[ai_idx]
                model = str(rec.get('model', 'AI'))
                title = str(rec.get('title', ''))
            else:
                model = str(ai_df.iloc[ai_idx].get('model', 'AI')) if 'ai_df' in globals() else 'AI'
                title = str(ai_df.iloc[ai_idx].get('title', '')) if 'ai_df' in globals() else ''

        rows.append({
            'global_index': int(idx),
            'who': who,
            'model': model,
            'nn_distance': float(nn_d[idx]) if nn_d is not None else np.nan,
            'title': title
        })

    out_df = pd.DataFrame(rows).sort_values('nn_distance', ascending=False)

    print(f"Outlier threshold (90th percentile): {threshold:.4f}")
    print(f"Total outliers: {len(out_df)} / {n_total} ({len(out_df)/n_total*100:.1f}%)")
    print("Outliers by source (model):")
    print(out_df['model'].value_counts().to_string())

    with pd.option_context('display.max_colwidth', 140):
        display(out_df.reset_index(drop=True))


########################################################################################################################
CELL 50
########################################################################################################################
from sklearn.metrics.pairwise import cosine_distances

# Compute novelty scores
print("="*85)
print("COMPUTING NOVELTY SCORES")
print("="*85)
print("Novelty = Mean distance to 10 nearest neighbors in literature corpus")
print("Higher score = farther from existing work = more novel")
print()

k = 10  # Number of nearest neighbors

def compute_novelty_scores(proposal_embeddings, literature_embeddings, k=10):
    """
    Compute novelty score for each proposal as mean distance to k-NN in literature.
    
    Args:
        proposal_embeddings: Embeddings of proposals (n_proposals, embedding_dim)
        literature_embeddings: Embeddings of literature corpus (n_articles, embedding_dim)
        k: Number of nearest neighbors
        
    Returns:
        novelty_scores: Array of novelty scores (n_proposals,)
        nearest_neighbor_indices: Array of k-NN indices for each proposal (n_proposals, k)
    """
    # Compute distances from each proposal to all literature articles
    distances = cosine_distances(proposal_embeddings, literature_embeddings)
    
    # For each proposal, find k nearest neighbors
    nearest_neighbor_indices = np.argsort(distances, axis=1)[:, :k]
    
    # Novelty score = mean distance to k-NN
    novelty_scores = np.array([
        distances[i, nearest_neighbor_indices[i]].mean()
        for i in range(len(proposal_embeddings))
    ])
    
    return novelty_scores, nearest_neighbor_indices

# Compute novelty for AI proposals
print("Computing novelty scores for AI proposals...")
ai_novelty_scores, ai_nn_indices = compute_novelty_scores(
    ai_embeddings_abstract, literature_embeddings, k=k
)

# Compute novelty for Human proposals
print("Computing novelty scores for human proposals...")
human_novelty_scores, human_nn_indices = compute_novelty_scores(
    human_embeddings_abstract, literature_embeddings, k=k
)

# Split AI novelty by model (mask-based; do NOT assume contiguous blocks)
if 'ai_df' not in globals() or 'model' not in ai_df.columns:
    raise RuntimeError("ai_df with a 'model' column is required to split AI novelty scores by model")

ai_models = sorted(ai_df['model'].astype(str).unique().tolist())
ai_model_series = ai_df['model'].astype(str).values

model_novelty_scores = {m: ai_novelty_scores[ai_model_series == m] for m in ai_models}

# Display statistics
print(f"\n{'='*85}")
print("NOVELTY SCORE STATISTICS")
print(f"{'='*85}")
print(f"\n{'GROUP':<35} {'N':<8} {'Mean':<10} {'Median':<10} {'Min':<10} {'Max':<10}")
print("-"*85)

# Human
print(f"{'Human':<35} {len(human_novelty_scores):<8} {human_novelty_scores.mean():<10.4f} {np.median(human_novelty_scores):<10.4f} {human_novelty_scores.min():<10.4f} {human_novelty_scores.max():<10.4f}")

print()  # Blank line

# Individual AI models
for model in ai_models:
    if model in model_novelty_scores:
        scores = model_novelty_scores[model]
        print(f"{model:<35} {len(scores):<8} {scores.mean():<10.4f} {np.median(scores):<10.4f} {scores.min():<10.4f} {scores.max():<10.4f}")

print()  # Blank line

# All AI combined
print(f"{'All AI (combined)':<35} {len(ai_novelty_scores):<8} {ai_novelty_scores.mean():<10.4f} {np.median(ai_novelty_scores):<10.4f} {ai_novelty_scores.min():<10.4f} {ai_novelty_scores.max():<10.4f}")

print("="*85)
print("\n💡 INTERPRETATION:")
print("   - Higher novelty score = more distant from existing literature")
print("   - Lower novelty score = more similar to published work")
print("="*85)

########################################################################################################################
CELL 52
########################################################################################################################
# Statistical tests - Compare each group to Human
print("="*85)
print("STATISTICAL TESTS: Novelty Scores (All Groups vs Human)")
print("="*85)

# Store all results
novelty_comparison_results = []

# Compare All AI vs Human
print("\n" + "-"*85)
print("Comparison: All AI (combined) vs Human")
print("-"*85)

u_stat_nov, p_value_nov = mannwhitneyu(ai_novelty_scores, human_novelty_scores, alternative='two-sided')
delta_nov = cliffs_delta(ai_novelty_scores, human_novelty_scores)
delta_interp_nov = interpret_cliffs_delta(delta_nov)
p_value_perm_nov, obs_diff_nov, _ = permutation_test(ai_novelty_scores, human_novelty_scores)

print(f"\nMann-Whitney U Test:")
print(f"  U-statistic: {u_stat_nov:,.0f}, p-value: {p_value_nov:.4e}")
print(f"\nCliff's Delta:")
print(f"  δ = {delta_nov:.4f} ({delta_interp_nov} effect)")
if delta_nov > 0:
    print(f"  → All AI proposals are MORE novel than human proposals")
else:
    print(f"  → Human proposals are MORE novel than all AI proposals")
print(f"\nPermutation Test (10,000 permutations):")
print(f"  Observed difference: {obs_diff_nov:.4f}, p-value: {p_value_perm_nov:.4f}")

novelty_comparison_results.append({
    'group': 'All AI',
    'u_stat': u_stat_nov,
    'p_value_mw': p_value_nov,
    'delta': delta_nov,
    'delta_interp': delta_interp_nov,
    'p_value_perm': p_value_perm_nov
})

# Compare each individual AI model vs Human
for model in ai_models:
    if model in model_novelty_scores:
        print("\n" + "-"*85)
        print(f"Comparison: {model} vs Human")
        print("-"*85)
        
        u_stat_model, p_value_mw_model = mannwhitneyu(model_novelty_scores[model], human_novelty_scores, alternative='two-sided')
        delta_model = cliffs_delta(model_novelty_scores[model], human_novelty_scores)
        delta_interp_model = interpret_cliffs_delta(delta_model)
        p_value_perm_model, obs_diff_model, _ = permutation_test(model_novelty_scores[model], human_novelty_scores)
        
        print(f"\nMann-Whitney U Test:")
        print(f"  U-statistic: {u_stat_model:,.0f}, p-value: {p_value_mw_model:.4e}")
        print(f"\nCliff's Delta:")
        print(f"  δ = {delta_model:.4f} ({delta_interp_model} effect)")
        if delta_model > 0:
            print(f"  → {model} proposals are MORE novel than human proposals")
        else:
            print(f"  → Human proposals are MORE novel than {model} proposals")
        print(f"\nPermutation Test (10,000 permutations):")
        print(f"  Observed difference: {obs_diff_model:.4f}, p-value: {p_value_perm_model:.4f}")
        
        novelty_comparison_results.append({
            'group': model,
            'u_stat': u_stat_model,
            'p_value_mw': p_value_mw_model,
            'delta': delta_model,
            'delta_interp': delta_interp_model,
            'p_value_perm': p_value_perm_model
        })

# Summary table
print("\n" + "="*85)
print("SUMMARY: Effect Sizes (Cliff's Delta) - Novelty Scores")
print("="*85)
print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
print("-"*85)
for result in novelty_comparison_results:
    print(f"{result['group']:<30} {result['delta']:<12.4f} {result['delta_interp']:<20} {result['p_value_mw']:<15.4e}")
print("="*85)
print("\n💡 Positive δ = AI more novel; Negative δ = Human more novel")
print("="*85)

########################################################################################################################
CELL 58
########################################################################################################################
# Examine most and least novel proposals
print("="*85)
print("EXAMINING MOST AND LEAST NOVEL PROPOSALS")
print("="*85)

# Find most novel human proposal
most_novel_human_idx = human_novelty_scores.argmax()
most_novel_human_score = human_novelty_scores[most_novel_human_idx]
most_novel_human_title = human_df.iloc[most_novel_human_idx]['proposal_title']

print(f"\n🏆 MOST NOVEL HUMAN PROPOSAL:")
print(f"  Title: {most_novel_human_title}")
print(f"  Novelty Score: {most_novel_human_score:.4f}")
print(f"  Nearest neighbors in literature:")
for j, lit_idx in enumerate(human_nn_indices[most_novel_human_idx][:5]):
    lit_article = articles[lit_idx]
    dist = cosine_distances([human_embeddings_abstract[most_novel_human_idx]], [literature_embeddings[lit_idx]])[0][0]
    print(f"    {j+1}. [{lit_article['pmid']}] {lit_article['title'][:80]}...")
    print(f"       Distance: {dist:.4f}, Published: {lit_article['publication_date']}")

# Find least novel human proposal
least_novel_human_idx = human_novelty_scores.argmin()
least_novel_human_score = human_novelty_scores[least_novel_human_idx]
least_novel_human_title = human_df.iloc[least_novel_human_idx]['proposal_title']

print(f"\n📚 LEAST NOVEL HUMAN PROPOSAL:")
print(f"  Title: {least_novel_human_title}")
print(f"  Novelty Score: {least_novel_human_score:.4f}")
print(f"  Nearest neighbors in literature:")
for j, lit_idx in enumerate(human_nn_indices[least_novel_human_idx][:5]):
    lit_article = articles[lit_idx]
    dist = cosine_distances([human_embeddings_abstract[least_novel_human_idx]], [literature_embeddings[lit_idx]])[0][0]
    print(f"    {j+1}. [{lit_article['pmid']}] {lit_article['title'][:80]}...")
    print(f"       Distance: {dist:.4f}, Published: {lit_article['publication_date']}")

# Find most novel AI proposal
most_novel_ai_idx = ai_novelty_scores.argmax()
most_novel_ai_score = ai_novelty_scores[most_novel_ai_idx]
most_novel_ai_title = ai_df.iloc[most_novel_ai_idx]['title']
most_novel_ai_model = ai_df.iloc[most_novel_ai_idx]['model']

print(f"\n🏆 MOST NOVEL AI PROPOSAL:")
print(f"  Model: {most_novel_ai_model}")
print(f"  Title: {most_novel_ai_title}")
print(f"  Novelty Score: {most_novel_ai_score:.4f}")
print(f"  Nearest neighbors in literature:")
for j, lit_idx in enumerate(ai_nn_indices[most_novel_ai_idx][:5]):
    lit_article = articles[lit_idx]
    dist = cosine_distances([ai_embeddings_abstract[most_novel_ai_idx]], [literature_embeddings[lit_idx]])[0][0]
    print(f"    {j+1}. [{lit_article['pmid']}] {lit_article['title'][:80]}...")
    print(f"       Distance: {dist:.4f}, Published: {lit_article['publication_date']}")

# Find least novel AI proposal
least_novel_ai_idx = ai_novelty_scores.argmin()
least_novel_ai_score = ai_novelty_scores[least_novel_ai_idx]
least_novel_ai_title = ai_df.iloc[least_novel_ai_idx]['title']
least_novel_ai_model = ai_df.iloc[least_novel_ai_idx]['model']

print(f"\n📚 LEAST NOVEL AI PROPOSAL:")
print(f"  Model: {least_novel_ai_model}")
print(f"  Title: {least_novel_ai_title}")
print(f"  Novelty Score: {least_novel_ai_score:.4f}")
print(f"  Nearest neighbors in literature:")
for j, lit_idx in enumerate(ai_nn_indices[least_novel_ai_idx][:5]):
    lit_article = articles[lit_idx]
    dist = cosine_distances([ai_embeddings_abstract[least_novel_ai_idx]], [literature_embeddings[lit_idx]])[0][0]
    print(f"    {j+1}. [{lit_article['pmid']}] {lit_article['title'][:80]}...")
    print(f"       Distance: {dist:.4f}, Published: {lit_article['publication_date']}")

print("="*85)

########################################################################################################################
CELL 62
########################################################################################################################
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*85)
print("TOPIC MODELING WITH LDA (EXPLORATORY)")
print("="*85)

# Prepare FULL DRAFT for topic modeling
ai_abstracts = ai_df['full_text'].fillna('').tolist()
human_abstracts = human_df['full_text'].fillna('').tolist()
all_abstracts = human_abstracts + ai_abstracts

# Create source labels
source_labels = ['Human'] * len(human_abstracts) + ['AI'] * len(ai_abstracts)
model_labels = ['Human'] * len(human_abstracts) + ai_df['model'].tolist()

print(f"\n✓ Prepared {len(all_abstracts)} abstracts")
print(f"  Human: {len(human_abstracts)}, AI: {len(ai_abstracts)}")

# Create document-term matrix with CountVectorizer (LDA requires counts, not TF-IDF)
#
# NOTE: In biology abstracts, very common background words (e.g., "cell") often
# appear in many topics and reduce interpretability. To improve topic specificity,
# we (1) detect corpus-specific high document-frequency UNIGRAMS and (2) drop only
# those UNIGRAM features while keeping informative BIGRAMS like "single cell".

# 1) Detect high document-frequency unigrams in THIS corpus
_unigram_probe = CountVectorizer(
    stop_words='english',
    ngram_range=(1, 1),
    min_df=2,
    max_df=1.0,
    max_features=5000
)
_unigram_X = _unigram_probe.fit_transform(all_abstracts)
_unigram_terms = _unigram_probe.get_feature_names_out()
_unigram_df = np.asarray((_unigram_X > 0).mean(axis=0)).ravel()  # fraction of docs containing term

# Auto-stopwords: appear in >= 50% of documents (tune threshold if needed)
auto_domain_unigram_stopwords = set(_unigram_terms[_unigram_df >= 0.50])

# Manual additions (keep small; auto list usually does most of the work)
manual_domain_unigram_stopwords = {
    'cell', 'cells',
    'protein', 'proteins',
    'project', 'using', 'nup', '000', 'nan', 'fg', 'npc', 'ii', 'et'
}

domain_unigram_stopwords = auto_domain_unigram_stopwords | manual_domain_unigram_stopwords

_top_common_idx = np.argsort(_unigram_df)[-20:][::-1]
print("\nMost common unigrams in corpus (doc frequency):")
for i in _top_common_idx:
    print(f"  {_unigram_terms[i]}: {_unigram_df[i]:.2f}")
print(f"\n✓ Domain unigram stopwords (auto+manual): {len(domain_unigram_stopwords)}")

# 2) Build unigram+bigram counts, then remove only stopword UNIGRAM features
print("\nCreating document-term matrix...")
vectorizer = CountVectorizer(
    max_features=2000,
    min_df=2,  # Minimum 2 documents
    max_df=0.7,  # Maximum 70% of documents
    stop_words='english',
    ngram_range=(1, 2)  # Unigrams and bigrams
)

_doc_term_matrix_full = vectorizer.fit_transform(all_abstracts)
_feature_names_full = np.array(vectorizer.get_feature_names_out())

_unigram_mask = np.array([' ' not in t for t in _feature_names_full])
_drop_mask = _unigram_mask & np.isin(_feature_names_full, list(domain_unigram_stopwords))
_keep_mask = ~_drop_mask

doc_term_matrix = _doc_term_matrix_full[:, _keep_mask]
feature_names = _feature_names_full[_keep_mask]

print(f"✓ Document-term matrix: {doc_term_matrix.shape}")
print(f"  Documents: {doc_term_matrix.shape[0]}, Vocabulary: {doc_term_matrix.shape[1]}")
print(f"  Dropped domain unigrams: {_drop_mask.sum()} (kept bigrams intact)")

# Fit LDA with strong priors for stability
print("\nFitting LDA with conservative parameters...")
print("  n_topics=5, alpha=0.5, beta=0.5 (strong regularization)")

n_topics = 5
lda_model = LatentDirichletAllocation(
    n_components=n_topics,
    doc_topic_prior=0.5,  # alpha - stronger prior for document regularization
    topic_word_prior=0.5,  # beta - stronger prior for topic regularization
    max_iter=100,
    learning_method='batch',
    random_state=42,
    n_jobs=-1
)

doc_topic_dist = lda_model.fit_transform(doc_term_matrix)

print(f"✓ LDA fitted")
print(f"  Perplexity: {lda_model.perplexity(doc_term_matrix):.2f}")
print(f"  Log-likelihood: {lda_model.score(doc_term_matrix):.2f}")

# Extract top words per topic
def display_topics(model, feature_names, n_top_words=10):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics.append(top_words)
    return topics

topics = display_topics(lda_model, feature_names, n_top_words=10)

print("\n" + "="*85)
print("TOP 10 WORDS PER TOPIC")
print("="*85)
for i, topic_words in enumerate(topics):
    print(f"\nTopic {i+1}: {', '.join(topic_words)}")

# Store document-topic distributions
doc_topic_df = pd.DataFrame(doc_topic_dist, columns=[f'Topic_{i+1}' for i in range(n_topics)])
doc_topic_df['source'] = source_labels
doc_topic_df['model'] = model_labels
doc_topic_df['group'] = ['Human' if s == 'Human' else 'AI' for s in source_labels]

# Assign dominant topic to each document
doc_topic_df['dominant_topic'] = doc_topic_df[[f'Topic_{i+1}' for i in range(n_topics)]].idxmax(axis=1)
doc_topic_df['dominant_topic_prob'] = doc_topic_df[[f'Topic_{i+1}' for i in range(n_topics)]].max(axis=1)

print("\n" + "="*85)
print("DOCUMENT-TOPIC DISTRIBUTION SUMMARY")
print("="*85)
print(f"\nMean topic probabilities per document:")
for i in range(n_topics):
    print(f"  Topic {i+1}: {doc_topic_df[f'Topic_{i+1}'].mean():.3f} ± {doc_topic_df[f'Topic_{i+1}'].std():.3f}")

print(f"\nDominant topic assignment:")
print(doc_topic_df['dominant_topic'].value_counts().sort_index())

print("\n⚠️ LABEL AS EXPLORATORY - Small sample size limits topic stability")
print("="*85)

########################################################################################################################
CELL 63
########################################################################################################################
# Stability check: Run LDA with multiple random seeds
# IMPORTANT: LDA topics can permute across random seeds ("label switching").
# This version ALIGNs topics to a reference run before computing stability.

from scipy.optimize import linear_sum_assignment

print("="*85)
print("TOPIC STABILITY VALIDATION")
print("="*85)
print("Running LDA with 10 different random seeds to assess stability (with topic alignment)...")

n_stability_runs = 10
n_top_words = 10

stability_topics = []      # list[run] -> list[topic] -> list[str]
stability_topic_dists = [] # list[run] -> ndarray (n_topics, vocab)

for seed in range(n_stability_runs):
    lda_temp = LatentDirichletAllocation(
        n_components=n_topics,
        doc_topic_prior=0.5,
        topic_word_prior=0.5,
        max_iter=100,
        learning_method='batch',
        random_state=seed,
        n_jobs=-1
    )
    lda_temp.fit(doc_term_matrix)

    # Normalize to topic-word probabilities for similarity comparisons
    topic_word = lda_temp.components_.astype(float)
    topic_word = topic_word / topic_word.sum(axis=1, keepdims=True)

    topics_temp = display_topics(lda_temp, feature_names, n_top_words=n_top_words)
    stability_topics.append(topics_temp)
    stability_topic_dists.append(topic_word)

print(f"✓ Completed {n_stability_runs} stability runs")

# Reference run (seed=0)
ref_words_by_topic = [set(ws) for ws in stability_topics[0]]
ref_dist = stability_topic_dists[0]

def _cosine_sim_matrix(A, B, eps=1e-12):
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + eps)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + eps)
    return A @ B.T

# Collect aligned stability metrics
per_topic_overlap_all = [[] for _ in range(n_topics)]
per_topic_cos_all = [[] for _ in range(n_topics)]

print("\nTopic stability (aligned to reference run):")
for run_idx in range(1, n_stability_runs):
    run_dist = stability_topic_dists[run_idx]
    sim = _cosine_sim_matrix(run_dist, ref_dist)  # (run_topic, ref_topic)

    # Hungarian assignment to maximize total similarity
    row_ind, col_ind = linear_sum_assignment(-sim)

    # Build aligned words and aligned cosine per reference topic
    aligned_words = [None] * n_topics
    aligned_cos = np.zeros(n_topics, dtype=float)
    for r_topic, ref_topic in zip(row_ind, col_ind):
        aligned_words[ref_topic] = set(stability_topics[run_idx][r_topic])
        aligned_cos[ref_topic] = sim[r_topic, ref_topic]

    # Per-topic overlap (top words) + cosine similarity (full distributions)
    overlaps = []
    for k in range(n_topics):
        overlap = len(ref_words_by_topic[k] & aligned_words[k]) / max(1, len(ref_words_by_topic[k]))
        overlaps.append(overlap)
        per_topic_overlap_all[k].append(overlap)
        per_topic_cos_all[k].append(aligned_cos[k])

    print(
        f"  Run {run_idx}: "
        f"mean top-{n_top_words} overlap={np.mean(overlaps):.1%}, "
        f"mean cosine={np.mean(aligned_cos):.3f}"
    )

print("\nPer-topic stability (mean across aligned runs):")
for k in range(n_topics):
    print(
        f"  Topic {k+1}: "
        f"{np.mean(per_topic_overlap_all[k]):.1%} ± {np.std(per_topic_overlap_all[k]):.1%} top-{n_top_words} overlap, "
        f"{np.mean(per_topic_cos_all[k]):.3f} ± {np.std(per_topic_cos_all[k]):.3f} cosine"
    )

print("\n💡 If overlap/cosine are still very low AFTER alignment, that reflects true instability.")
print("="*85)


########################################################################################################################
CELL 65
########################################################################################################################
from scipy.stats import fisher_exact, chi2_contingency
from statsmodels.stats.multitest import multipletests

print("="*85)
print("TOPIC DISTRIBUTION COMPARISON")
print("="*85)

# Create contingency table: topics × source
contingency_table = pd.crosstab(doc_topic_df['dominant_topic'], doc_topic_df['group'])
print("\nContingency table (dominant topic × source):")
print(contingency_table)
print(f"\nRow percentages:")
print(pd.crosstab(doc_topic_df['dominant_topic'], doc_topic_df['group'], normalize='index').round(3))

# Permutation test for overall distribution difference
print("\n" + "-"*85)
print("PERMUTATION TEST: Overall topic distribution difference")
print("-"*85)

def compute_chi_square_stat(contingency):
    """Compute chi-square statistic from contingency table"""
    return chi2_contingency(contingency)[0]

observed_chi2 = compute_chi_square_stat(contingency_table)
print(f"Observed chi-square statistic: {observed_chi2:.4f}")

# Permutation test
n_permutations = 10000
perm_chi2_stats = []

for _ in range(n_permutations):
    # Shuffle source labels
    shuffled_labels = np.random.permutation(doc_topic_df['group'].values)
    perm_contingency = pd.crosstab(doc_topic_df['dominant_topic'], shuffled_labels)
    perm_chi2 = compute_chi_square_stat(perm_contingency)
    perm_chi2_stats.append(perm_chi2)

perm_chi2_stats = np.array(perm_chi2_stats)
p_value_perm = np.mean(perm_chi2_stats >= observed_chi2)

print(f"\nPermutation test results ({n_permutations:,} permutations):")
print(f"  Null mean chi-square: {perm_chi2_stats.mean():.4f} ± {perm_chi2_stats.std():.4f}")
print(f"  Observed chi-square: {observed_chi2:.4f}")
print(f"  p-value: {p_value_perm:.4f}")

if p_value_perm < 0.05:
    print(f"  → Significant difference in topic distributions (p < 0.05)")
else:
    print(f"  → No significant difference in topic distributions (p ≥ 0.05)")

# Per-topic Fisher's exact tests
print("\n" + "-"*85)
print("PER-TOPIC TESTS: Fisher's Exact (Human vs. All AI)")
print("-"*85)

fisher_results = []

for topic in contingency_table.index:
    # Create 2×2 table for this topic
    topic_yes = contingency_table.loc[topic, :]
    topic_no = contingency_table.drop(topic).sum(axis=0)
    
    table_2x2 = np.array([
        [topic_yes['Human'], topic_yes['AI']],
        [topic_no['Human'], topic_no['AI']]
    ])
    
    odds_ratio, p_value = fisher_exact(table_2x2)
    
    # Calculate percentages
    human_pct = topic_yes['Human'] / contingency_table['Human'].sum() * 100
    ai_pct = topic_yes['AI'] / contingency_table['AI'].sum() * 100
    
    fisher_results.append({
        'topic': topic,
        'human_count': topic_yes['Human'],
        'ai_count': topic_yes['AI'],
        'human_pct': human_pct,
        'ai_pct': ai_pct,
        'odds_ratio': odds_ratio,
        'p_value': p_value
    })

fisher_df = pd.DataFrame(fisher_results)

# Apply FDR correction (Benjamini-Hochberg at q=0.10 for exploratory)
fisher_df['p_value_fdr'] = multipletests(fisher_df['p_value'], method='fdr_bh', alpha=0.10)[1]

print(f"\n{'Topic':<12} {'Human %':<10} {'AI %':<10} {'OR':<8} {'p-value':<10} {'FDR q':<10} {'Result'}")
print("-"*85)

for _, row in fisher_df.iterrows():
    sig_mark = '***' if row['p_value_fdr'] < 0.01 else '**' if row['p_value_fdr'] < 0.05 else '*' if row['p_value_fdr'] < 0.10 else ''
    direction = 'Human↑' if row['odds_ratio'] > 1 else 'AI↑' if row['odds_ratio'] < 1 else 'Equal'
    
    print(f"{row['topic']:<12} {row['human_pct']:<10.1f} {row['ai_pct']:<10.1f} {row['odds_ratio']:<8.2f} "
          f"{row['p_value']:<10.4f} {row['p_value_fdr']:<10.4f} {direction} {sig_mark}")

print("\n*** p<0.01, ** p<0.05, * p<0.10 (FDR-corrected)")
print("OR > 1 = over-represented in human; OR < 1 = over-represented in AI")

print("="*85)

########################################################################################################################
CELL 67
########################################################################################################################
# Subsample validation to account for group size imbalance (23 human vs 69 AI)
print("="*85)
print("SUBSAMPLE VALIDATION (Accounting for 3:1 group size imbalance)")
print("="*85)
print("Subsampling AI to n=23, repeating 1000 times...")

n_subsamples = 1000
subsample_results = {topic: [] for topic in contingency_table.index}

for _ in range(n_subsamples):
    # Subsample AI to match human sample size
    ai_indices = doc_topic_df[doc_topic_df['group'] == 'AI'].index
    sampled_indices = np.random.choice(ai_indices, size=len(human_abstracts), replace=False)
    
    # Create balanced dataset
    balanced_df = pd.concat([
        doc_topic_df[doc_topic_df['group'] == 'Human'],
        doc_topic_df.loc[sampled_indices]
    ])
    
    # Test each topic
    for topic in contingency_table.index:
        human_has_topic = (balanced_df[balanced_df['group'] == 'Human']['dominant_topic'] == topic).sum()
        ai_has_topic = (balanced_df[balanced_df['group'] == 'AI']['dominant_topic'] == topic).sum()
        
        # 2×2 table
        table = np.array([
            [human_has_topic, len(human_abstracts) - human_has_topic],
            [ai_has_topic, len(human_abstracts) - ai_has_topic]
        ])
        
        _, p_val = fisher_exact(table)
        subsample_results[topic].append(p_val)

print("\nSubsample validation results:")
print(f"{'Topic':<12} {'Sig. in N subsamples':<25} {'Proportion':<12} {'Interpretation'}")
print("-"*85)

for topic in contingency_table.index:
    p_values = subsample_results[topic]
    n_significant = sum(np.array(p_values) < 0.05)
    proportion = n_significant / n_subsamples
    
    interpretation = "Robust" if proportion > 0.8 else "Moderate" if proportion > 0.5 else "Weak"
    print(f"{topic:<12} {n_significant}/{n_subsamples:<20} {proportion:<12.2%} {interpretation}")

print("\n💡 Proportion >80% = robust difference even with balanced sample sizes")
print("="*85)

########################################################################################################################
CELL 70
########################################################################################################################
from scipy.stats import entropy

print("="*85)
print("TOPIC COVERAGE AND ENTROPY ANALYSIS")
print("="*85)

# Topic coverage: count unique topics per group (threshold: topic probability > 0.20)
threshold = 0.20

def count_topics_covered(doc_topic_probs, threshold=0.20):
    """Count how many topics are represented above threshold"""
    topic_cols = [col for col in doc_topic_probs.columns if col.startswith('Topic_')]
    topics_above_threshold = set()
    for col in topic_cols:
        if (doc_topic_probs[col] > threshold).any():
            topics_above_threshold.add(col)
    return len(topics_above_threshold)

human_doc_topics = doc_topic_df[doc_topic_df['group'] == 'Human']
ai_doc_topics = doc_topic_df[doc_topic_df['group'] == 'AI']

human_coverage = count_topics_covered(human_doc_topics, threshold)
ai_coverage = count_topics_covered(ai_doc_topics, threshold)

print(f"\n1. TOPIC COVERAGE (topics with at least one proposal >{threshold*100:.0f}% probability):")
print(f"  Human: {human_coverage}/{n_topics} topics")
print(f"  AI: {ai_coverage}/{n_topics} topics")

# Exclusive topics
print(f"\n2. EXCLUSIVE TOPICS:")

def get_exclusive_topics(group_df, other_df, threshold=0.20, min_count=5):
    """Find topics exclusive to one group (with minimum count)"""
    topic_cols = [col for col in group_df.columns if col.startswith('Topic_')]
    exclusive = []
    
    for col in topic_cols:
        # Check if topic appears in group with sufficient frequency
        group_has = (group_df[col] > threshold).sum()
        other_has = (other_df[col] > threshold).sum()
        
        if group_has >= min_count and other_has == 0:
            exclusive.append(col)
    
    return exclusive

human_exclusive = get_exclusive_topics(human_doc_topics, ai_doc_topics, threshold, min_count=5)
ai_exclusive = get_exclusive_topics(ai_doc_topics, human_doc_topics, threshold, min_count=5)

print(f"  Human-exclusive topics (≥5 proposals, 0 in AI): {len(human_exclusive)}")
if human_exclusive:
    print(f"    {', '.join(human_exclusive)}")
print(f"  AI-exclusive topics (≥5 proposals, 0 in Human): {len(ai_exclusive)}")
if ai_exclusive:
    print(f"    {', '.join(ai_exclusive)}")

# Permutation test for exclusive topics
print(f"\n  Permutation test for exclusive topics:")
n_perm = 10000
perm_human_exclusive_counts = []
perm_ai_exclusive_counts = []

for _ in range(n_perm):
    # Shuffle group labels
    shuffled = doc_topic_df.copy()
    shuffled['group'] = np.random.permutation(shuffled['group'].values)
    
    human_perm = shuffled[shuffled['group'] == 'Human']
    ai_perm = shuffled[shuffled['group'] == 'AI']
    
    h_excl = len(get_exclusive_topics(human_perm, ai_perm, threshold, min_count=5))
    a_excl = len(get_exclusive_topics(ai_perm, human_perm, threshold, min_count=5))
    
    perm_human_exclusive_counts.append(h_excl)
    perm_ai_exclusive_counts.append(a_excl)

perm_human_exclusive_counts = np.array(perm_human_exclusive_counts)
perm_ai_exclusive_counts = np.array(perm_ai_exclusive_counts)

p_human = np.mean(perm_human_exclusive_counts >= len(human_exclusive))
p_ai = np.mean(perm_ai_exclusive_counts >= len(ai_exclusive))

print(f"    Human: {len(human_exclusive)} observed vs. {perm_human_exclusive_counts.mean():.2f} ± {perm_human_exclusive_counts.std():.2f} expected, p={p_human:.4f}")
print(f"    AI: {len(ai_exclusive)} observed vs. {perm_ai_exclusive_counts.mean():.2f} ± {perm_ai_exclusive_counts.std():.2f} expected, p={p_ai:.4f}")

# Shannon entropy with Miller-Madow correction
print(f"\n3. SHANNON ENTROPY (with Miller-Madow bias correction):")

def calculate_entropy_corrected(topic_distribution, n_topics):
    """Calculate Shannon entropy with Miller-Madow correction"""
    # Get topic counts
    topic_counts = topic_distribution.value_counts()
    
    # Shannon entropy
    h = entropy(topic_counts, base=2)
    
    # Miller-Madow correction: H_corrected = H + (K-1)/(2*N)
    # K = number of categories with non-zero count, N = sample size
    k = len(topic_counts)
    n = topic_counts.sum()
    h_corrected = h + (k - 1) / (2 * n)
    
    # Normalized entropy
    h_max = np.log2(k) if k > 1 else 1
    h_normalized = h_corrected / h_max if h_max > 0 else 0
    
    return h_corrected, h_normalized

human_entropy, human_norm_entropy = calculate_entropy_corrected(
    human_doc_topics['dominant_topic'], n_topics
)
ai_entropy, ai_norm_entropy = calculate_entropy_corrected(
    ai_doc_topics['dominant_topic'], n_topics
)

print(f"  Human: H = {human_entropy:.4f}, H_normalized = {human_norm_entropy:.4f}")
print(f"  AI: H = {ai_entropy:.4f}, H_normalized = {ai_norm_entropy:.4f}")

# Subsample AI to n=23 to account for sample size
print(f"\n  Subsample validation (AI subsampled to n={len(human_abstracts)}, 1000 iterations):")
subsample_entropies = []
subsample_norm_entropies = []

for _ in range(1000):
    ai_indices = ai_doc_topics.index
    sampled = ai_doc_topics.loc[np.random.choice(ai_indices, size=len(human_abstracts), replace=False)]
    h, h_norm = calculate_entropy_corrected(sampled['dominant_topic'], n_topics)
    subsample_entropies.append(h)
    subsample_norm_entropies.append(h_norm)

subsample_entropies = np.array(subsample_entropies)
subsample_norm_entropies = np.array(subsample_norm_entropies)

print(f"    AI (subsampled): H = {subsample_entropies.mean():.4f} ± {subsample_entropies.std():.4f}")
print(f"    AI (subsampled): H_normalized = {subsample_norm_entropies.mean():.4f} ± {subsample_norm_entropies.std():.4f}")

# Compare (subsample/permutation style test)
# We compare Human entropy to the distribution of AI entropies under subsampling.
# NOTE: If Human entropy is *lower* than typical AI, the one-sided p-value is
# P(AI_subsample_entropy <= Human_entropy), not >=.

ai_sub_mean = subsample_entropies.mean()
diff = human_entropy - ai_sub_mean

p_lower = np.mean(subsample_entropies <= human_entropy)  # AI as low-or-lower than Human
p_upper = np.mean(subsample_entropies >= human_entropy)  # AI as high-or-higher than Human
p_two_sided = min(1.0, 2 * min(p_lower, p_upper))

# One-sided in the observed direction
p_one_sided = p_lower if human_entropy < ai_sub_mean else p_upper

print(f"\n  Comparison (subsample test):")
print(f"    Difference (Human - AI_subsample_mean): {diff:.4f}")
print(f"    p_one_sided (observed direction): {p_one_sided:.4f}")
print(f"    p_two_sided: {p_two_sided:.4f}")

if p_two_sided < 0.05:
    if human_entropy > ai_sub_mean:
        print(f"    → Human proposals have significantly HIGHER entropy (more even dominant-topic distribution)")
    else:
        print(f"    → AI proposals have significantly HIGHER entropy (more even dominant-topic distribution)")
else:
    print(f"    → No significant difference in entropy")

print("\n💡 Higher entropy = more even spread across topics = higher thematic diversity")
print("="*85)

########################################################################################################################
CELL 73
########################################################################################################################
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, normalized_mutual_info_score, adjusted_rand_score

print("="*85)
print("CLUSTER ANALYSIS: STEP 1 - OPTIMAL k SELECTION")
print("="*85)

# Use embeddings from diversity analysis (already computed)
all_embeddings_cluster = np.vstack([human_embeddings, ai_embeddings])
source_labels_cluster = np.array(['Human'] * len(human_embeddings) + ['AI'] * len(ai_embeddings))

print(f"\nUsing embeddings: {all_embeddings_cluster.shape}")
print(f"  Human: {len(human_embeddings)}, AI: {len(ai_embeddings)}")

# Test different values of k
k_values = [3, 4, 5, 6, 7, 8]
metrics_results = []

print(f"\nTesting k = {k_values}...")
print(f"\n{'k':<5} {'Silhouette':<12} {'Davies-Bouldin':<16} {'BIC':<12}")
print("-"*50)

for k in k_values:
    # Fit GMM
    gmm = GaussianMixture(
        n_components=k,
        covariance_type='full',
        random_state=42,
        n_init=10
    )
    cluster_labels = gmm.fit_predict(all_embeddings_cluster)
    
    # Compute metrics
    silhouette = silhouette_score(all_embeddings_cluster, cluster_labels)
    davies_bouldin = davies_bouldin_score(all_embeddings_cluster, cluster_labels)
    bic = gmm.bic(all_embeddings_cluster)
    
    metrics_results.append({
        'k': k,
        'silhouette': silhouette,
        'davies_bouldin': davies_bouldin,
        'bic': bic
    })
    
    print(f"{k:<5} {silhouette:<12.4f} {davies_bouldin:<16.4f} {bic:<12.2f}")

metrics_df = pd.DataFrame(metrics_results)

# Select best k using BIC (lower is better)
best_k_bic = metrics_df.loc[metrics_df['bic'].idxmin(), 'k']
best_k_silhouette = metrics_df.loc[metrics_df['silhouette'].idxmax(), 'k']

print(f"\n✓ Best k by BIC (elbow method): {best_k_bic}")
print(f"✓ Best k by Silhouette score: {best_k_silhouette}")

# Use BIC as primary criterion
best_k = int(best_k_bic)
print(f"\n→ Selected k = {best_k} (using BIC)")

# Visualize selection metrics
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Panel 1: BIC
ax1 = axes[0]
ax1.plot(metrics_df['k'], metrics_df['bic'], 'o-', linewidth=2, markersize=8, color='steelblue')
ax1.axvline(best_k, color='red', linestyle='--', alpha=0.7, label=f'Selected k={best_k}')
ax1.set_xlabel('Number of clusters (k)', fontsize=12, fontweight='bold')
ax1.set_ylabel('BIC (lower = better)', fontsize=12, fontweight='bold')
ax1.set_title('BIC vs. k (Elbow Method)', fontsize=14, fontweight='bold')
ax1.grid(alpha=0.3)
ax1.legend()

# Panel 2: Silhouette
ax2 = axes[1]
ax2.plot(metrics_df['k'], metrics_df['silhouette'], 'o-', linewidth=2, markersize=8, color='darkorange')
ax2.axvline(best_k, color='red', linestyle='--', alpha=0.7, label=f'Selected k={best_k}')
ax2.set_xlabel('Number of clusters (k)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Silhouette Score (higher = better)', fontsize=12, fontweight='bold')
ax2.set_title('Silhouette Score vs. k', fontsize=14, fontweight='bold')
ax2.grid(alpha=0.3)
ax2.legend()

# Panel 3: Davies-Bouldin
ax3 = axes[2]
ax3.plot(metrics_df['k'], metrics_df['davies_bouldin'], 'o-', linewidth=2, markersize=8, color='darkgreen')
ax3.axvline(best_k, color='red', linestyle='--', alpha=0.7, label=f'Selected k={best_k}')
ax3.set_xlabel('Number of clusters (k)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Davies-Bouldin Index (lower = better)', fontsize=12, fontweight='bold')
ax3.set_title('Davies-Bouldin Index vs. k', fontsize=14, fontweight='bold')
ax3.grid(alpha=0.3)
ax3.legend()

plt.tight_layout()
plt.savefig('results/figures/cluster_k_selection.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Figure saved to: results/figures/cluster_k_selection.png")
print("="*85)

########################################################################################################################
CELL 74
########################################################################################################################
print("="*85)
print(f"CLUSTER ANALYSIS: STEP 2 - CLUSTERING WITH k={best_k}")
print("="*85)

# Fit final GMM with best k
gmm_final = GaussianMixture(
    n_components=best_k,
    covariance_type='full',
    random_state=42,
    n_init=10
)

cluster_labels_final = gmm_final.fit_predict(all_embeddings_cluster)
cluster_probs_final = gmm_final.predict_proba(all_embeddings_cluster)

print(f"\n✓ Clustered {len(all_embeddings_cluster)} proposals into {best_k} clusters")
print(f"  Cluster sizes: {np.bincount(cluster_labels_final)}")

# Cluster composition analysis
print(f"\n" + "-"*85)
print("CLUSTER COMPOSITION ANALYSIS")
print("-"*85)

cluster_composition = []

for cluster_id in range(best_k):
    cluster_mask = cluster_labels_final == cluster_id
    cluster_sources = source_labels_cluster[cluster_mask]
    
    n_total = len(cluster_sources)
    n_human = (cluster_sources == 'Human').sum()
    n_ai = (cluster_sources == 'AI').sum()
    
    pct_human = n_human / n_total * 100 if n_total > 0 else 0
    pct_ai = n_ai / n_total * 100 if n_total > 0 else 0
    
    # Classify cluster dominance (baseline: 25% human, 75% AI)
    if pct_human > 60:
        dominance = 'Human-dominated'
    elif pct_human < 15:  # Less than expected given 25% baseline
        dominance = 'AI-dominated'
    else:
        dominance = 'Mixed'
    
    cluster_composition.append({
        'cluster': cluster_id,
        'total': n_total,
        'human': n_human,
        'ai': n_ai,
        'pct_human': pct_human,
        'pct_ai': pct_ai,
        'dominance': dominance
    })

composition_df = pd.DataFrame(cluster_composition)

print(f"\n{'Cluster':<10} {'Total':<8} {'Human':<8} {'AI':<8} {'%Human':<10} {'%AI':<10} {'Dominance'}")
print("-"*85)

for _, row in composition_df.iterrows():
    print(f"{row['cluster']:<10} {row['total']:<8} {row['human']:<8} {row['ai']:<8} "
          f"{row['pct_human']:<10.1f} {row['pct_ai']:<10.1f} {row['dominance']}")

print(f"\n{'Dominance':<20} {'Count'}")
print("-"*30)
dominance_counts = composition_df['dominance'].value_counts()
for dom, count in dominance_counts.items():
    print(f"{dom:<20} {count}")

print(f"\n💡 Baseline: 25% human, 75% AI")
print(f"   Human-dominated: >60% human")
print(f"   AI-dominated: <15% human")
print(f"   Mixed: 15-60% human")
print("="*85)

########################################################################################################################
CELL 75
########################################################################################################################
print("="*85)
print("CLUSTER ANALYSIS: STEP 3 - SEGREGATION METRICS (with Permutation Tests)")
print("="*85)

# Convert source labels to binary (0 = Human, 1 = AI)
source_binary = (source_labels_cluster == 'AI').astype(int)

# 1. Normalized Mutual Information (NMI)
nmi_observed = normalized_mutual_info_score(cluster_labels_final, source_binary)

print(f"\n1. NORMALIZED MUTUAL INFORMATION (NMI):")
print(f"   Observed NMI: {nmi_observed:.4f}")

# Permutation test for NMI
n_perm_seg = 10000
nmi_null = []

for _ in range(n_perm_seg):
    shuffled_sources = np.random.permutation(source_binary)
    nmi_perm = normalized_mutual_info_score(cluster_labels_final, shuffled_sources)
    nmi_null.append(nmi_perm)

nmi_null = np.array(nmi_null)
p_nmi = np.mean(nmi_null >= nmi_observed)

print(f"   Null distribution: {nmi_null.mean():.4f} ± {nmi_null.std():.4f}")
print(f"   p-value: {p_nmi:.4f}")

if p_nmi < 0.05:
    print(f"   → Significant segregation: clusters predict source better than chance")
else:
    print(f"   → No significant segregation: clustering independent of source")

# 2. Adjusted Rand Index (ARI)
ari_observed = adjusted_rand_score(cluster_labels_final, source_binary)

print(f"\n2. ADJUSTED RAND INDEX (ARI):")
print(f"   Observed ARI: {ari_observed:.4f}")

# Permutation test for ARI
ari_null = []

for _ in range(n_perm_seg):
    shuffled_sources = np.random.permutation(source_binary)
    ari_perm = adjusted_rand_score(cluster_labels_final, shuffled_sources)
    ari_null.append(ari_perm)

ari_null = np.array(ari_null)
p_ari = np.mean(ari_null >= ari_observed)

print(f"   Null distribution: {ari_null.mean():.4f} ± {ari_null.std():.4f}")
print(f"   p-value: {p_ari:.4f}")

if p_ari < 0.05:
    print(f"   → Significant agreement: cluster assignments correlate with source")
else:
    print(f"   → No significant agreement: random overlap")

# 3. Within-group vs. Between-group distances
print(f"\n3. WITHIN-GROUP VS. BETWEEN-GROUP DISTANCES:")

# Calculate pairwise distances
from sklearn.metrics.pairwise import cosine_distances

distances_all = cosine_distances(all_embeddings_cluster)

# Within-human distances
human_mask = source_labels_cluster == 'Human'
within_human_dists = distances_all[np.ix_(human_mask, human_mask)]
within_human_dists = within_human_dists[np.triu_indices_from(within_human_dists, k=1)]

# Within-AI distances
ai_mask = source_labels_cluster == 'AI'
within_ai_dists = distances_all[np.ix_(ai_mask, ai_mask)]
within_ai_dists = within_ai_dists[np.triu_indices_from(within_ai_dists, k=1)]

# Between human-AI distances
between_dists = distances_all[np.ix_(human_mask, ai_mask)].flatten()

print(f"   Within-human mean distance: {within_human_dists.mean():.4f} ± {within_human_dists.std():.4f}")
print(f"   Within-AI mean distance: {within_ai_dists.mean():.4f} ± {within_ai_dists.std():.4f}")
print(f"   Between human-AI mean distance: {between_dists.mean():.4f} ± {between_dists.std():.4f}")

# Ratio of between to within
within_mean = np.mean([within_human_dists.mean(), within_ai_dists.mean()])
between_within_ratio = between_dists.mean() / within_mean

print(f"\n   Between/Within ratio: {between_within_ratio:.4f}")

# Permutation test for between/within ratio
ratio_null = []

for _ in range(n_perm_seg):
    shuffled = np.random.permutation(source_labels_cluster)
    h_mask = shuffled == 'Human'
    a_mask = shuffled == 'AI'
    
    within_h = distances_all[np.ix_(h_mask, h_mask)]
    within_h = within_h[np.triu_indices_from(within_h, k=1)]
    
    within_a = distances_all[np.ix_(a_mask, a_mask)]
    within_a = within_a[np.triu_indices_from(within_a, k=1)]
    
    between = distances_all[np.ix_(h_mask, a_mask)].flatten()
    
    within_m = np.mean([within_h.mean(), within_a.mean()])
    ratio_perm = between.mean() / within_m
    ratio_null.append(ratio_perm)

ratio_null = np.array(ratio_null)
p_ratio = np.mean(ratio_null >= between_within_ratio)

print(f"   Null distribution: {ratio_null.mean():.4f} ± {ratio_null.std():.4f}")
print(f"   p-value: {p_ratio:.4f}")

if p_ratio < 0.05:
    if between_within_ratio > 1:
        print(f"   → Human and AI proposals are significantly MORE distant from each other than within groups")
    else:
        print(f"   → Human and AI proposals are significantly CLOSER to each other than within groups")
else:
    print(f"   → No significant difference in between vs. within-group distances")

print("\n" + "="*85)
print("INTERPRETATION SUMMARY")
print("="*85)

if p_nmi < 0.05 or p_ari < 0.05:
    print("✓ SEGREGATION: Human and AI proposals cluster in distinct semantic regions")
    print("  → They generate different KINDS of ideas")
elif p_nmi > 0.10 and p_ari > 0.10:
    print("✓ INTEGRATION: Human and AI proposals intermixed in embedding space")
    print("  → Ideas are similar regardless of source")
else:
    print("✓ INTERMEDIATE: Some thematic clustering but not strictly by source")

print("="*85)

########################################################################################################################
CELL 78
########################################################################################################################
print("="*85)
print("ANALYSIS 2.3: THEMATIC AND CLUSTER ANALYSIS - COMPREHENSIVE SUMMARY")
print("="*85)

print("\n" + "="*85)
print("1. TOPIC MODELING (LDA with n=5 topics)")
print("="*85)
print(f"  Model: Latent Dirichlet Allocation")
print(f"  Parameters: alpha=0.5, beta=0.5 (strong regularization)")
print(f"  Perplexity: {lda_model.perplexity(doc_term_matrix):.2f}")
print(f"\n  Topics identified:")
for i, topic_words in enumerate(topics):
    print(f"    Topic {i+1}: {', '.join(topic_words[:5])}...")

print("\n" + "="*85)
print("2. TOPIC DISTRIBUTION COMPARISON")
print("="*85)
print(f"  Overall distribution test (permutation):")
print(f"    Chi-square: {observed_chi2:.4f}, p={p_value_perm:.4f}")
if p_value_perm < 0.05:
    print(f"    → Significant difference in topic distributions")
else:
    print(f"    → No significant difference in topic distributions")

print(f"\n  Per-topic tests (Fisher's exact with FDR correction):")
significant_topics = fisher_df[fisher_df['p_value_fdr'] < 0.10]
if len(significant_topics) > 0:
    print(f"    {len(significant_topics)} topics show significant over/under-representation:")
    for _, row in significant_topics.iterrows():
        direction = 'Human' if row['odds_ratio'] > 1 else 'AI'
        print(f"      {row['topic']}: OR={row['odds_ratio']:.2f}, p_fdr={row['p_value_fdr']:.4f} ({direction}↑)")
else:
    print(f"    No topics show significant over/under-representation (FDR q=0.10)")

print("\n" + "="*85)
print("3. TOPIC COVERAGE AND ENTROPY")
print("="*85)
print(f"  Coverage (topics with >20% probability):")
print(f"    Human: {human_coverage}/{n_topics} topics")
print(f"    AI: {ai_coverage}/{n_topics} topics")

print(f"\n  Exclusive topics (≥5 proposals):")
print(f"    Human-exclusive: {len(human_exclusive)} (p={p_human:.4f})")
print(f"    AI-exclusive: {len(ai_exclusive)} (p={p_ai:.4f})")

print(f"\n  Shannon entropy (Miller-Madow corrected):")
print(f"    Human: H={human_entropy:.4f}, H_norm={human_norm_entropy:.4f}")
print(f"    AI (subsampled): H={subsample_entropies.mean():.4f}±{subsample_entropies.std():.4f}")
print(f"    Difference: p={p_entropy:.4f}")

print("\n" + "="*85)
print(f"4. CLUSTER ANALYSIS (GMM with k={best_k})")
print("="*85)
print(f"  Model selection:")
print(f"    Best k by BIC: {best_k}")
print(f"    Silhouette score: {metrics_df.loc[metrics_df['k']==best_k, 'silhouette'].values[0]:.4f}")

print(f"\n  Cluster composition:")
print(f"    Human-dominated clusters: {(composition_df['dominance']=='Human-dominated').sum()}")
print(f"    AI-dominated clusters: {(composition_df['dominance']=='AI-dominated').sum()}")
print(f"    Mixed clusters: {(composition_df['dominance']=='Mixed').sum()}")

print(f"\n  Segregation metrics:")
print(f"    NMI: {nmi_observed:.4f} (null: {nmi_null.mean():.4f}±{nmi_null.std():.4f}, p={p_nmi:.4f})")
print(f"    ARI: {ari_observed:.4f} (null: {ari_null.mean():.4f}±{ari_null.std():.4f}, p={p_ari:.4f})")
print(f"    Between/Within distance ratio: {between_within_ratio:.4f} (p={p_ratio:.4f})")

print("\n" + "="*85)
print("OVERALL INTERPRETATION")
print("="*85)

# Topic distribution
if p_value_perm < 0.05:
    print("✓ Topics: Human and AI differ in topic distributions")
else:
    print("✓ Topics: No significant difference in topic distributions")

# Entropy
if p_entropy < 0.05:
    if diff > 0:
        print("✓ Entropy: Human proposals show higher thematic diversity")
    else:
        print("✓ Entropy: AI proposals show higher thematic diversity")
else:
    print("✓ Entropy: Similar thematic diversity between groups")

# Clustering
if p_nmi < 0.05 or p_ari < 0.05:
    print("✓ Clustering: SEGREGATION - Human and AI occupy distinct semantic regions")
    print("  → Generate different KINDS of ideas")
elif p_nmi > 0.10 and p_ari > 0.10:
    print("✓ Clustering: INTEGRATION - Human and AI ideas are intermixed")
    print("  → Similar ideas regardless of source")
else:
    print("✓ Clustering: INTERMEDIATE - Some thematic patterns but not strict segregation")

print("\n⚠️  LIMITATIONS:")
print("  • Small sample size (n=23 human, n=69 AI)")
print("  • Topic modeling labeled as EXPLORATORY")
print("  • Results should be validated with larger samples")
print("  • Segregation may reflect prompt differences, not inherent ideation differences")

print("\n" + "="*85)
print("📊 FIGURES GENERATED:")
print("="*85)
print("  1. results/figures/cluster_k_selection.png")
print("  2. results/figures/topic_distribution_comparison.png")
print("  3. results/figures/cluster_analysis_visualization.png")
print("="*85)

########################################################################################################################
CELL 81
########################################################################################################################
# =============================================================================
# ANALYSIS 2.3.5–2.3.6: STYLE VS CONTENT (Baseline + Style-Controlled Sensitivity)
# Text scope: full proposals (full_text)
# =============================================================================

import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ----------------------------
# Style feature extraction
# ----------------------------

_HEDGE_WORDS = {
    'may','might','could','can','suggest','suggests','suggested','potential','potentially',
    'likely','unlikely','possibly','possible','approximately','estimate','estimated',
    'hypothesize','hypothesis','we propose','we aim','we will','we plan'
}

def _tokenize_words(text: str):
    return re.findall(r"[A-Za-z']+", text.lower())

def _split_sentences(text: str):
    # lightweight sentence split for readability/stylistic counts
    sents = re.split(r"[.!?]+\s+|\n+", text.strip())
    return [s for s in (sent.strip() for sent in sents) if s]

def _count_syllables(word: str) -> int:
    # heuristic syllable counter (good enough for comparative readability proxies)
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    w = re.sub(r"e$", "", w)  # silent e
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))

def _flesch_kincaid(text: str):
    words = _tokenize_words(text)
    n_words = len(words)
    sents = _split_sentences(text)
    n_sents = len(sents)
    if n_words == 0 or n_sents == 0:
        return np.nan, np.nan
    syllables = sum(_count_syllables(w) for w in words)

    # Flesch Reading Ease & FK Grade Level (English)
    fre = 206.835 - 1.015 * (n_words / n_sents) - 84.6 * (syllables / n_words)
    fkgl = 0.39 * (n_words / n_sents) + 11.8 * (syllables / n_words) - 15.59
    return fre, fkgl

def extract_style_features(text: str) -> dict:
    text = text or ""
    words = _tokenize_words(text)
    n_words = len(words)
    n_chars = len(text)
    sents = _split_sentences(text)
    n_sents = len(sents)

    uniq = len(set(words)) if n_words else 0
    ttr = (uniq / n_words) if n_words else 0.0

    stop_ct = sum(1 for w in words if w in ENGLISH_STOP_WORDS)
    stop_rate = (stop_ct / n_words) if n_words else 0.0

    avg_word_len = (np.mean([len(w) for w in words]) if n_words else 0.0)
    avg_sent_len = (n_words / n_sents) if n_sents else 0.0

    # punctuation / formatting (normalized)
    punct = {
        'comma': text.count(','),
        'semicolon': text.count(';'),
        'colon': text.count(':'),
        'dash': text.count('-') + text.count('–') + text.count('—'),
        'paren': text.count('(') + text.count(')'),
        'quote': text.count('"') + text.count("'"),
        'newline': text.count('\n'),
        'bullet': len(re.findall(r"(^|\n)\s*[-*•]\s+", text))
    }
    punct_rate = {f"{k}_per_1k_chars": (v / max(1, n_chars)) * 1000.0 for k, v in punct.items()}

    # hedging / stance
    low = text.lower()
    hedge_hits = 0
    # count single-token hedges
    hedge_hits += sum(1 for w in words if w in _HEDGE_WORDS)
    # count a few multiword patterns
    hedge_hits += len(re.findall(r"\bwe\s+(propose|aim|plan|will)\b", low))
    hedge_rate = (hedge_hits / n_words) if n_words else 0.0

    # simple headers / sectioning markers (your full_text includes e.g., "Title:", "Abstract:")
    header_lines = 0
    for line in (ln.strip() for ln in text.splitlines()):
        if re.match(r"^[A-Z][A-Za-z0-9 /-]{1,40}:\s+", line):
            header_lines += 1
    header_rate = header_lines

    fre, fkgl = _flesch_kincaid(text)

    feats = {
        'n_words': n_words,
        'n_chars': n_chars,
        'n_sents': n_sents,
        'avg_word_len': avg_word_len,
        'avg_sent_len_words': avg_sent_len,
        'type_token_ratio': ttr,
        'stopword_rate': stop_rate,
        'hedge_rate': hedge_rate,
        'flesch_reading_ease': fre,
        'fk_grade_level': fkgl,
    }
    feats.update(punct_rate)
    return feats

# Build style feature table (full proposals)
human_texts_style = human_df['full_text'].fillna('').tolist()
ai_texts_style = ai_df['full_text'].fillna('').tolist()
all_texts_style = human_texts_style + ai_texts_style

style_rows = [extract_style_features(t) for t in all_texts_style]
style_df = pd.DataFrame(style_rows)
style_df['group'] = (['Human'] * len(human_texts_style)) + (['AI'] * len(ai_texts_style))
style_df['is_ai'] = (style_df['group'] == 'AI').astype(int)

print("="*85)
print("STYLE FEATURES: EXTRACTED")
print("="*85)
print(f"✓ Built style feature table: {style_df.shape[0]} docs × {style_df.shape[1]-2} features")
print(style_df.groupby('group')[['avg_sent_len_words','stopword_rate','hedge_rate','fk_grade_level']].mean().round(3))


########################################################################################################################
CELL 85
########################################################################################################################
from sklearn.model_selection import StratifiedKFold, cross_val_score, permutation_test_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

print("="*85)
print("STYLE-ONLY BASELINE: HUMAN VS AI")
print("="*85)

# Use all numeric style features
feature_cols = [c for c in style_df.columns if c not in {'group','is_ai'}]
X = style_df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(style_df[feature_cols].median()).values
y = style_df['is_ai'].values

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
clf = make_pipeline(
    StandardScaler(),
    LogisticRegression(
        max_iter=5000,
        class_weight='balanced',
        solver='liblinear',
        random_state=42
    )
)

auc_scores = cross_val_score(clf, X, y, cv=cv, scoring='roc_auc')
bal_scores = cross_val_score(clf, X, y, cv=cv, scoring='balanced_accuracy')

print(f"CV AUROC: {auc_scores.mean():.3f} ± {auc_scores.std():.3f}")
print(f"CV balanced accuracy: {bal_scores.mean():.3f} ± {bal_scores.std():.3f}")

# Permutation test for AUROC (style-only)
# (Keep permutations moderate for notebook runtime; increase if needed.)
obs_score, perm_scores, p_value = permutation_test_score(
    clf, X, y,
    cv=cv,
    scoring='roc_auc',
    n_permutations=1000,
    n_jobs=-1,
    random_state=42
)

print("\nPermutation test (AUROC, 1,000 label shuffles):")
print(f"  Observed AUROC: {obs_score:.3f}")
print(f"  Null mean AUROC: {perm_scores.mean():.3f} ± {perm_scores.std():.3f}")
print(f"  p-value: {p_value:.4f}")

if obs_score >= 0.80:
    print("  → Strong evidence that style alone separates Human vs AI.")
elif obs_score >= 0.60:
    print("  → Moderate evidence that style contributes to separation.")
else:
    print("  → Style-only separation is weak; downstream separation is less likely to be purely stylistic.")


########################################################################################################################
CELL 89
########################################################################################################################
from sklearn.metrics.pairwise import cosine_distances

print("="*85)
print("STYLE-CONTROLLED EMBEDDING OUTCOMES (RESIDUALIZATION)")
print("="*85)

if 'human_embeddings' not in globals() or 'ai_embeddings' not in globals():
    print("⚠️ Embeddings not found in workspace variables (expected `human_embeddings` and `ai_embeddings`).")
else:
    # Align document order: Human first, then AI (matches style_df build above)
    E_h = np.asarray(human_embeddings)
    E_a = np.asarray(ai_embeddings)
    E = np.vstack([E_h, E_a])
    group = np.array([0] * len(E_h) + [1] * len(E_a))  # 0=Human, 1=AI

    # Style covariates (compact set)
    cov_cols = ['n_words','avg_sent_len_words','type_token_ratio','hedge_rate','fk_grade_level']
    cov = style_df[cov_cols].replace([np.inf, -np.inf], np.nan).fillna(style_df[cov_cols].median()).values
    cov = StandardScaler().fit_transform(cov)

    # Outcomes from embeddings
    centroid_all = E.mean(axis=0, keepdims=True)
    dist_to_all = cosine_distances(E, centroid_all).ravel()

    centroid_h = E_h.mean(axis=0, keepdims=True)
    centroid_a = E_a.mean(axis=0, keepdims=True)
    dist_to_group = np.where(group == 0,
                             cosine_distances(E, centroid_h).ravel(),
                             cosine_distances(E, centroid_a).ravel())

    def _ols_group_coef(y, g, covariates):
        X = np.column_stack([np.ones(len(y)), g.astype(float), covariates])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        return beta[1], beta

    def perm_test_group_coef(y, g, covariates, n_perm=5000, seed=42):
        rng = np.random.default_rng(seed)
        obs_coef, _ = _ols_group_coef(y, g, covariates)
        null = np.zeros(n_perm, dtype=float)
        for i in range(n_perm):
            g_perm = rng.permutation(g)
            null[i], _ = _ols_group_coef(y, g_perm, covariates)
        p_two = (np.mean(np.abs(null) >= abs(obs_coef)) + 1) / (n_perm + 1)
        return obs_coef, null, p_two

    def summarize_outcome(name, y):
        mean_h = float(np.mean(y[group == 0]))
        mean_a = float(np.mean(y[group == 1]))
        print(f"\nOutcome: {name}")
        print(f"  Unadjusted means: Human={mean_h:.4f}, AI={mean_a:.4f}, (AI-Human)={mean_a-mean_h:+.4f}")
        coef, null, p = perm_test_group_coef(y, group, cov, n_perm=5000, seed=42)
        print(f"  Style-adjusted group coef (AI indicator): {coef:+.6f}")
        print(f"  Permutation p (two-sided, 5,000 shuffles): {p:.4f}")

    summarize_outcome('Cosine distance to overall centroid', dist_to_all)
    summarize_outcome('Cosine distance to own-group centroid', dist_to_group)


########################################################################################################################
CELL 92
########################################################################################################################
import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler
from scipy.stats import mannwhitneyu

print("\n" + "="*85)
print("STATISTICAL TESTS: Style-adjusted Centroid Dispersion (All Groups vs Human)")
print("="*85)

# ---- helpers (define if not already in notebook) ----
if 'cliffs_delta' not in globals():
    def cliffs_delta(x, y):
        """Cliff's delta: P(x>y) - P(x<y)."""
        x = np.asarray(x)
        y = np.asarray(y)
        gt = 0
        lt = 0
        for xi in x:
            gt += np.sum(xi > y)
            lt += np.sum(xi < y)
        return (gt - lt) / (len(x) * len(y))

if 'interpret_cliffs_delta' not in globals():
    def interpret_cliffs_delta(d):
        ad = abs(d)
        if ad < 0.147:
            return 'negligible'
        if ad < 0.33:
            return 'small'
        if ad < 0.474:
            return 'medium'
        return 'large'

def _perm_test_mean_diff(x, y, n_perm=10000, seed=42):
    """Two-sided permutation test on mean difference: mean(x)-mean(y).

    Named uniquely to avoid conflicts with any earlier `permutation_test()` defined elsewhere in the notebook.
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    y = np.asarray(y)
    obs = float(np.mean(x) - np.mean(y))
    pooled = np.concatenate([x, y])
    n_x = len(x)
    null = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        perm = rng.permutation(pooled)
        null[i] = float(np.mean(perm[:n_x]) - np.mean(perm[n_x:]))
    p = (np.mean(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)
    return p, obs, null

# ---- compute y_adj robustly (don’t assume previous cell variables exist) ----
if 'style_df' not in globals():
    print("⚠️ style_df not found. Run the style feature extraction cell first.")
elif 'human_embeddings' not in globals() or 'ai_embeddings' not in globals():
    print("⚠️ Embeddings not found (`human_embeddings`, `ai_embeddings`). Run embedding generation first.")
elif 'ai_df' not in globals() or 'model_embeddings_dict' not in globals():
    print("⚠️ ai_df/model_embeddings_dict not found. Run the proposal loading/embedding setup cells first.")
else:
    # Align document order: Human first, then AI (matches style_df build above)
    E_h = np.asarray(human_embeddings)
    E_a = np.asarray(ai_embeddings)
    E = np.vstack([E_h, E_a])
    n_h, n_a = len(E_h), len(E_a)

    # Labels (Human first, then AI per-model)
    ai_model_labels = ai_df['model'].tolist()
    assert len(ai_model_labels) == n_a, "ai_df['model'] length must match ai_embeddings"
    labels = np.array((['Human'] * n_h) + ai_model_labels)

    # Group order consistent with earlier analyses
    if 'ai_models' in globals():
        ai_models_local = list(ai_models)
    else:
        ai_models_local = sorted(ai_df['model'].dropna().unique().tolist())
    group_order = ['Human'] + [m for m in ai_models_local if m in set(ai_model_labels)]

    # Raw distance-to-own-group-centroid
    y_raw = np.zeros(len(labels), dtype=float)
    for g in group_order:
        idx = np.where(labels == g)[0]
        if len(idx) == 0:
            continue
        centroid = E[idx].mean(axis=0, keepdims=True)
        y_raw[idx] = cosine_distances(E[idx], centroid).ravel()

    # Style residualization on y_raw
    cov_cols = ['n_words','avg_sent_len_words','type_token_ratio','hedge_rate','fk_grade_level']
    X_cov = style_df[cov_cols].replace([np.inf, -np.inf], np.nan).fillna(style_df[cov_cols].median()).values
    X_cov = StandardScaler().fit_transform(X_cov)
    X = np.column_stack([np.ones(len(y_raw)), X_cov])
    beta, *_ = np.linalg.lstsq(X, y_raw, rcond=None)
    y_pred = X @ beta
    y_adj = (y_raw - y_pred) + y_raw.mean()

    # Split adjusted distances
    human_adj = y_adj[labels == 'Human']
    ai_adj = y_adj[labels != 'Human']

    model_adj = {m: y_adj[labels == m] for m in group_order if m != 'Human'}

    # ---- tests ----
    adj_comparison_results = []

    print("\n" + "-"*85)
    print("Comparison: All AI (combined) vs Human [STYLE-ADJUSTED]")
    print("-"*85)

    u_stat, p_mw = mannwhitneyu(ai_adj, human_adj, alternative='two-sided')
    d = cliffs_delta(ai_adj, human_adj)
    d_interp = interpret_cliffs_delta(d)
    p_perm, obs_diff, _ = _perm_test_mean_diff(ai_adj, human_adj, n_perm=10000, seed=42)

    print("\nMann-Whitney U Test:")
    print(f"  U-statistic: {u_stat:,.0f}, p-value: {p_mw:.4e}")
    print("\nCliff's Delta:")
    print(f"  δ = {d:.4f} ({d_interp} effect)")
    if d > 0:
        print("  → All AI proposals are MORE dispersed from center (after style adjustment)")
    else:
        print("  → Human proposals are MORE dispersed from center (after style adjustment)")
    print("\nPermutation Test (10,000 permutations):")
    print(f"  Observed difference (mean AI - mean Human): {obs_diff:.4f}, p-value: {p_perm:.4f}")

    adj_comparison_results.append({
        'group': 'All AI',
        'u_stat': u_stat,
        'p_value_mw': p_mw,
        'delta': d,
        'delta_interp': d_interp,
        'p_value_perm': p_perm
    })

    for model in group_order:
        if model == 'Human':
            continue
        vals = model_adj.get(model)
        if vals is None or len(vals) == 0:
            continue

        print("\n" + "-"*85)
        print(f"Comparison: {model} vs Human [STYLE-ADJUSTED]")
        print("-"*85)

        u_stat_m, p_mw_m = mannwhitneyu(vals, human_adj, alternative='two-sided')
        d_m = cliffs_delta(vals, human_adj)
        d_interp_m = interpret_cliffs_delta(d_m)
        p_perm_m, obs_diff_m, _ = _perm_test_mean_diff(vals, human_adj, n_perm=10000, seed=42)

        print("\nMann-Whitney U Test:")
        print(f"  U-statistic: {u_stat_m:,.0f}, p-value: {p_mw_m:.4e}")
        print("\nCliff's Delta:")
        print(f"  δ = {d_m:.4f} ({d_interp_m} effect)")
        if d_m > 0:
            print(f"  → {model} proposals are MORE dispersed from center (after style adjustment)")
        else:
            print("  → Human proposals are MORE dispersed from center (after style adjustment)")
        print("\nPermutation Test (10,000 permutations):")
        print(f"  Observed difference (mean {model} - mean Human): {obs_diff_m:.4f}, p-value: {p_perm_m:.4f}")

        adj_comparison_results.append({
            'group': model,
            'u_stat': u_stat_m,
            'p_value_mw': p_mw_m,
            'delta': d_m,
            'delta_interp': d_interp_m,
            'p_value_perm': p_perm_m
        })

    # Summary table
    print("\n" + "="*85)
    print("SUMMARY: Effect Sizes (Cliff's Delta) - Style-adjusted Centroid Dispersion")
    print("="*85)
    print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
    print("-"*85)
    for r in adj_comparison_results:
        print(f"{r['group']:<30} {r['delta']:<12.4f} {r['delta_interp']:<20} {r['p_value_mw']:<15.4e}")
    print("="*85)
    print("\n💡 Positive δ = AI more dispersed; Negative δ = Human more dispersed (style-adjusted)")
    print("="*85)


########################################################################################################################
CELL 95
########################################################################################################################
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler
from scipy.stats import mannwhitneyu

print("="*85)
print("STYLE-ADJUSTED NEAREST-NEIGHBOR (NN) ANALYSIS (Metadata-aligned)")
print("="*85)

if 'style_df' not in globals():
    print("⚠️ style_df not found. Run the style feature extraction cell first.")
elif 'human_embeddings' not in globals() or 'ai_embeddings' not in globals():
    print("⚠️ Embeddings not found (`human_embeddings`, `ai_embeddings`). Run embedding generation first.")
else:
    # ----------------------------
    # 0) Build per-row labels that match embedding order
    # ----------------------------
    n_human = len(human_embeddings)
    n_ai = len(ai_embeddings)

    if 'ai_metadata' in globals() and isinstance(ai_metadata, list) and len(ai_metadata) == n_ai:
        ai_model_labels = [str(r.get('model', 'AI')) for r in ai_metadata]
    elif 'ai_df' in globals() and len(ai_df) == n_ai and 'model' in ai_df.columns:
        print("⚠️ ai_metadata not available; falling back to ai_df['model'] order (may misalign if embeddings were shuffled).")
        ai_model_labels = [str(x) for x in ai_df['model'].tolist()]
    else:
        raise RuntimeError("Cannot infer AI model labels aligned to ai_embeddings. Need ai_metadata (preferred) or ai_df with matching order.")

    labels = np.array((['Human'] * n_human) + ai_model_labels)

    # Stable group order
    if 'ai_models' in globals():
        ai_models_local = [m for m in list(ai_models) if m in set(ai_model_labels)]
    else:
        ai_models_local = sorted(list(dict.fromkeys(ai_model_labels)))

    group_order = ['Human'] + ai_models_local

    # ----------------------------
    # 1) Build embedding matrix (Human first, then AI) and residualize on style
    # ----------------------------
    all_embeddings = np.vstack([np.asarray(human_embeddings), np.asarray(ai_embeddings)])

    cov_cols = ['n_words','avg_sent_len_words','type_token_ratio','hedge_rate','fk_grade_level']
    X_cov = style_df[cov_cols].replace([np.inf, -np.inf], np.nan).fillna(style_df[cov_cols].median()).values
    X_cov = StandardScaler().fit_transform(X_cov)
    X = np.column_stack([np.ones(len(X_cov)), X_cov])

    B, *_ = np.linalg.lstsq(X, all_embeddings, rcond=None)
    all_embeddings_resid = all_embeddings - (X @ B)
    all_embeddings_resid = all_embeddings_resid / (np.linalg.norm(all_embeddings_resid, axis=1, keepdims=True) + 1e-12)

    # ----------------------------
    # 2) Compute full distance matrix + NN distances (STYLE-ADJUSTED)
    # ----------------------------
    print("\n" + "="*85)
    print("COMPUTING STYLE-ADJUSTED NEAREST-NEIGHBOR DISTANCES FOR ALL GROUPS")
    print("="*85)

    all_distances_adj = cosine_distances(all_embeddings_resid)
    np.fill_diagonal(all_distances_adj, np.inf)
    nn_distances_adj = all_distances_adj.min(axis=1)

    # Group-wise NN distances
    human_nn_dists_adj = nn_distances_adj[labels == 'Human']
    ai_nn_dists_adj = nn_distances_adj[labels != 'Human']

    model_nn_dists_adj = {g: nn_distances_adj[labels == g] for g in ai_models_local}

    # Print statistics table
    print(f"\n{'GROUP':<35} {'N':<8} {'Mean':<10} {'Median':<10} {'Min':<10} {'Max':<10}")
    print("-"*85)
    print(f"{'Human':<35} {len(human_nn_dists_adj):<8} {human_nn_dists_adj.mean():<10.4f} {np.median(human_nn_dists_adj):<10.4f} {human_nn_dists_adj.min():<10.4f} {human_nn_dists_adj.max():<10.4f}")
    print()
    for model in ai_models_local:
        dists = model_nn_dists_adj[model]
        print(f"{model:<35} {len(dists):<8} {dists.mean():<10.4f} {np.median(dists):<10.4f} {dists.min():<10.4f} {dists.max():<10.4f}")
    print()
    print(f"{'All AI (combined)':<35} {len(ai_nn_dists_adj):<8} {ai_nn_dists_adj.mean():<10.4f} {np.median(ai_nn_dists_adj):<10.4f} {ai_nn_dists_adj.min():<10.4f} {ai_nn_dists_adj.max():<10.4f}")

    print("="*85)
    print("\n💡 INTERPRETATION:")
    print("   - Higher mean NN distance = more isolated proposals (outliers)")
    print("   - Lower mean NN distance = proposals cluster together")
    print("   - Distances are computed AFTER removing linear embedding variation explained by style covariates")
    print("="*85)

    # ----------------------------
    # 3) Outlier detection (top 10% NN distances) - STYLE-ADJUSTED
    # ----------------------------
    threshold_adj = np.percentile(nn_distances_adj, 90)
    outliers_adj = nn_distances_adj > threshold_adj

    human_outliers_adj = int(outliers_adj[labels == 'Human'].sum())
    ai_outliers_adj = int(outliers_adj[labels != 'Human'].sum())
    model_outliers_adj = {g: int(outliers_adj[labels == g].sum()) for g in ai_models_local}

    print("\n" + "="*85)
    print("OUTLIER DETECTION (Top 10% NN distance) — STYLE-ADJUSTED")
    print("="*85)
    print(f"Threshold distance: {threshold_adj:.4f}")
    print()
    print(f"{'GROUP':<35} {'Outliers':<15} {'Total':<10} {'Percentage':<15}")
    print("-"*85)
    print(f"{'Human':<35} {human_outliers_adj:<15} {n_human:<10} {human_outliers_adj/n_human*100:<15.1f}%")
    print()
    for model in ai_models_local:
        n_model = int((labels == model).sum())
        print(f"{model:<35} {model_outliers_adj[model]:<15} {n_model:<10} {model_outliers_adj[model]/n_model*100:<15.1f}%")
    print()
    print(f"{'All AI (combined)':<35} {ai_outliers_adj:<15} {n_ai:<10} {ai_outliers_adj/n_ai*100:<15.1f}%")
    print("="*85)

    # ----------------------------
    # 4) Nearest-neighbor origin analysis — STYLE-ADJUSTED
    # ----------------------------
    nn_indices_adj = all_distances_adj.argmin(axis=1)
    nn_labels_adj = labels[nn_indices_adj]

    human_nn_same_group_adj = int((nn_labels_adj[labels == 'Human'] == 'Human').sum())
    human_nn_diff_group_adj = int(n_human - human_nn_same_group_adj)

    ai_nn_same_group_adj = int((nn_labels_adj[labels != 'Human'] != 'Human').sum())
    ai_nn_diff_group_adj = int(n_ai - ai_nn_same_group_adj)

    model_nn_analysis_adj = {}
    for model in ai_models_local:
        mask = labels == model
        total = int(mask.sum())
        nn_from_human = int((nn_labels_adj[mask] == 'Human').sum())
        nn_from_same_model = int((nn_labels_adj[mask] == model).sum())
        nn_from_other_ai = int(total - nn_from_human - nn_from_same_model)
        model_nn_analysis_adj[model] = {
            'from_human': nn_from_human,
            'from_same_model': nn_from_same_model,
            'from_other_ai': nn_from_other_ai,
            'total': total
        }

    print("\n" + "="*85)
    print("NEAREST NEIGHBOR GROUP ANALYSIS — STYLE-ADJUSTED")
    print("="*85)

    print(f"\n{'Human proposals:':<50}")
    print(f"  NN from same group (human): {human_nn_same_group_adj} ({human_nn_same_group_adj/n_human*100:.1f}%)")
    print(f"  NN from different group (AI): {human_nn_diff_group_adj} ({human_nn_diff_group_adj/n_human*100:.1f}%)")

    print(f"\n{'All AI proposals (combined):':<50}")
    print(f"  NN from same group (AI): {ai_nn_same_group_adj} ({ai_nn_same_group_adj/n_ai*100:.1f}%)")
    print(f"  NN from different group (human): {ai_nn_diff_group_adj} ({ai_nn_diff_group_adj/n_ai*100:.1f}%)")

    print("\n" + "-"*85)
    print("Per-Model NN Group Breakdown:")
    print("-"*85)

    for model in ai_models_local:
        data = model_nn_analysis_adj[model]
        print(f"\n{model}:")
        print(f"  NN from Human: {data['from_human']} ({data['from_human']/data['total']*100:.1f}%)")
        print(f"  NN from same model: {data['from_same_model']} ({data['from_same_model']/data['total']*100:.1f}%)")
        print(f"  NN from other AI models: {data['from_other_ai']} ({data['from_other_ai']/data['total']*100:.1f}%)")

    print("\n" + "="*85)
    print("\n💡 INTERPRETATION:")
    print("   - High 'NN from same model' = model produces similar proposals")
    print("   - High 'NN from Human' = model proposals resemble human work")
    print("   - All computed in style-adjusted residual embedding space")
    print("="*85)

    # ----------------------------
    # 5) Statistical tests vs Human (same tests) — STYLE-ADJUSTED
    # ----------------------------
    print("\n" + "="*85)
    print("STATISTICAL TESTS: NN Distances (All Groups vs Human) — STYLE-ADJUSTED")
    print("="*85)

    nn_comparison_results_adj = []

    print("\n" + "-"*85)
    print("Comparison: All AI (combined) vs Human")
    print("-"*85)

    u_stat_nn, p_value_nn = mannwhitneyu(ai_nn_dists_adj, human_nn_dists_adj, alternative='two-sided')
    delta_nn = cliffs_delta(ai_nn_dists_adj, human_nn_dists_adj)
    delta_nn_interp = interpret_cliffs_delta(delta_nn)
    p_value_perm_nn, obs_diff_nn, _ = permutation_test(ai_nn_dists_adj, human_nn_dists_adj)

    print(f"\nMann-Whitney U Test:")
    print(f"  U-statistic: {u_stat_nn:,.0f}, p-value: {p_value_nn:.4e}")
    print(f"\nCliff's Delta:")
    print(f"  δ = {delta_nn:.4f} ({delta_nn_interp} effect)")
    if delta_nn > 0:
        print(f"  → All AI proposals have MORE unique/outlier ideas (style-adjusted)")
    else:
        print(f"  → Human proposals have MORE unique/outlier ideas (style-adjusted)")
    print(f"\nPermutation Test (10,000 permutations):")
    print(f"  Observed difference: {obs_diff_nn:.4f}, p-value: {p_value_perm_nn:.4f}")

    nn_comparison_results_adj.append({
        'group': 'All AI',
        'u_stat': u_stat_nn,
        'p_value_mw': p_value_nn,
        'delta': delta_nn,
        'delta_interp': delta_nn_interp,
        'p_value_perm': p_value_perm_nn
    })

    for model in ai_models_local:
        if model in model_nn_dists_adj:
            print("\n" + "-"*85)
            print(f"Comparison: {model} vs Human")
            print("-"*85)

            u_stat_model, p_value_mw_model = mannwhitneyu(model_nn_dists_adj[model], human_nn_dists_adj, alternative='two-sided')
            delta_model = cliffs_delta(model_nn_dists_adj[model], human_nn_dists_adj)
            delta_interp_model = interpret_cliffs_delta(delta_model)
            p_value_perm_model, obs_diff_model, _ = permutation_test(model_nn_dists_adj[model], human_nn_dists_adj)

            print(f"\nMann-Whitney U Test:")
            print(f"  U-statistic: {u_stat_model:,.0f}, p-value: {p_value_mw_model:.4e}")
            print(f"\nCliff's Delta:")
            print(f"  δ = {delta_model:.4f} ({delta_interp_model} effect)")
            if delta_model > 0:
                print(f"  → {model} proposals have MORE unique/outlier ideas (style-adjusted)")
            else:
                print(f"  → Human proposals have MORE unique/outlier ideas (style-adjusted)")
            print(f"\nPermutation Test (10,000 permutations):")
            print(f"  Observed difference: {obs_diff_model:.4f}, p-value: {p_value_perm_model:.4f}")

            nn_comparison_results_adj.append({
                'group': model,
                'u_stat': u_stat_model,
                'p_value_mw': p_value_mw_model,
                'delta': delta_model,
                'delta_interp': delta_interp_model,
                'p_value_perm': p_value_perm_model
            })

    print("\n" + "="*85)
    print("SUMMARY: Effect Sizes (Cliff's Delta) - NN Distances (Style-adjusted)")
    print("="*85)
    print(f"{'Group':<30} {'δ':<12} {'Effect Size':<20} {'p-value (MW)':<15}")
    print("-"*85)
    for result in nn_comparison_results_adj:
        print(f"{result['group']:<30} {result['delta']:<12.4f} {result['delta_interp']:<20} {result['p_value_mw']:<15.4e}")
    print("="*85)
    print("\n💡 Positive δ = AI more outlier-prone; Negative δ = Human more outlier-prone (style-adjusted)")
    print("="*85)

    # ----------------------------
    # 6) Visualization (same 3-panel layout) — STYLE-ADJUSTED
    # ----------------------------
    fig = plt.figure(figsize=(18, 5))
    gs = fig.add_gridspec(1, 3, hspace=0.3, wspace=0.3)

    # Colors (reuse global mapping)
    if 'colors' in globals() and isinstance(colors, dict):
        colors_local = dict(colors)
    else:
        colors_local = {'Human': 'steelblue'}

    # 1. NN distance distributions by group
    ax1 = fig.add_subplot(gs[0, 0])
    nn_data = []
    for dist, label in [(human_nn_dists_adj, 'Human')] + [(model_nn_dists_adj[m], m) for m in ai_models_local if m in model_nn_dists_adj]:
        for val in dist:
            nn_data.append({'NN Distance': val, 'Group': label})

    nn_df = pd.DataFrame(nn_data)
    group_order_viz = ['Human'] + [m for m in ai_models_local if m in model_nn_dists_adj]
    palette_list = [colors_local.get(g, 'gray') for g in group_order_viz]

    sns.violinplot(data=nn_df, x='Group', y='NN Distance', ax=ax1, palette=palette_list, order=group_order_viz)
    ax1.axhline(threshold_adj, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Outlier threshold (90%): {threshold_adj:.3f}')
    ax1.set_ylabel('Nearest-Neighbor Distance', fontsize=11)
    ax1.set_xlabel('Group', fontsize=11)
    ax1.set_title('NN Distance Distributions (Style-adjusted)', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=20)
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3, axis='y')

    # 2. Outlier counts by group
    ax2 = fig.add_subplot(gs[0, 1])
    outlier_data = []
    outlier_data.append({'Group': 'Human', 'Outliers': human_outliers_adj, 'Total': n_human, 'Percentage': human_outliers_adj/n_human*100})
    for model in ai_models_local:
        if model in model_outliers_adj:
            n_model = len(model_embeddings_dict.get(model, []))
            outlier_data.append({'Group': model, 'Outliers': model_outliers_adj[model], 'Total': n_model, 'Percentage': model_outliers_adj[model]/n_model*100})

    outlier_df = pd.DataFrame(outlier_data)
    bars = ax2.bar(outlier_df['Group'], outlier_df['Percentage'], color=[colors_local.get(g, 'gray') for g in outlier_df['Group']], edgecolor='black', linewidth=1)
    ax2.axhline(10, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Expected 10%')
    ax2.set_ylabel('Outliers (%)', fontsize=11)
    ax2.set_xlabel('Group', fontsize=11)
    ax2.set_title('Outlier Percentages by Group (Style-adjusted)', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=20)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, axis='y')

    for bar, pct in zip(bars, outlier_df['Percentage']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)

    # 3. NN origins (stacked bar)
    ax3 = fig.add_subplot(gs[0, 2])

    groups = ['Human'] + [m for m in ai_models_local if m in model_nn_analysis_adj]
    nn_from_human_pcts = [human_nn_diff_group_adj/n_human*100]
    nn_from_same_pcts = [human_nn_same_group_adj/n_human*100]
    nn_from_other_ai_pcts = [0]

    for model in [m for m in ai_models_local if m in model_nn_analysis_adj]:
        data = model_nn_analysis_adj[model]
        nn_from_human_pcts.append(data['from_human']/data['total']*100)
        nn_from_same_pcts.append(data['from_same_model']/data['total']*100)
        nn_from_other_ai_pcts.append(data['from_other_ai']/data['total']*100)

    x_pos = np.arange(len(groups))
    width = 0.6

    p1 = ax3.bar(x_pos, nn_from_same_pcts, width, label='NN from same group', color='#3498db', edgecolor='black', linewidth=0.5)
    p2 = ax3.bar(x_pos, nn_from_other_ai_pcts, width, bottom=nn_from_same_pcts, label='NN from other AI', color='#95a5a6', edgecolor='black', linewidth=0.5)
    bottom = np.array(nn_from_same_pcts) + np.array(nn_from_other_ai_pcts)
    p3 = ax3.bar(x_pos, nn_from_human_pcts, width, bottom=bottom, label='NN from different group', color='#e74c3c', edgecolor='black', linewidth=0.5)

    ax3.set_ylabel('Percentage (%)', fontsize=11)
    ax3.set_xlabel('Group', fontsize=11)
    ax3.set_title('Nearest Neighbor Origins (Style-adjusted)', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(groups, rotation=20, fontsize=9)
    ax3.legend(fontsize=8, loc='upper right')
    ax3.grid(alpha=0.3, axis='y')
    ax3.set_ylim([0, 100])

    plt.tight_layout()
    out_fig = 'results/figures/nearest_neighbor_by_model_style_adjusted.png'
    plt.savefig(out_fig, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"\n✓ Figure saved to: {out_fig}")
    print("\nNote: This mirrors the unadjusted NN pipeline, but all distances are computed in residual (style-adjusted) embedding space.")

########################################################################################################################
CELL 97
########################################################################################################################
import umap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

print("\n" + "="*85)
print("STYLE-ADJUSTED: UMAP PROJECTION FOR NN/OUTLIER ANALYSIS")
print("="*85)

# This cell expects you to have run the style-adjusted NN analysis cell above.
required_vars = ['all_embeddings_resid', 'outliers_adj', 'threshold_adj', 'n_human', 'n_ai', 'ai_models_local', 'model_embeddings_dict']
missing = [v for v in required_vars if v not in globals()]
if missing:
    print(f"⚠️ Missing variables from prior style-adjusted NN cell: {missing}")
    print("Run the 'STYLE-ADJUSTED NEAREST-NEIGHBOR (NN) ANALYSIS' cell first.")
else:
    # ----------------------------
    # Sanity check: style signal reduction in embeddings (linear association)
    # ----------------------------
    try:
        cov_cols = ['n_words','avg_sent_len_words','type_token_ratio','hedge_rate','fk_grade_level']
        X_cov = style_df[cov_cols].replace([np.inf, -np.inf], np.nan).fillna(style_df[cov_cols].median()).values
        X_cov = StandardScaler().fit_transform(X_cov)

        E_raw = np.vstack([np.asarray(human_embeddings), np.asarray(ai_embeddings)])
        E_raw = E_raw / (np.linalg.norm(E_raw, axis=1, keepdims=True) + 1e-12)
        E_adj = np.asarray(all_embeddings_resid)  # already normalized in the NN cell

        pca = PCA(n_components=10, random_state=42)
        Z_raw = pca.fit_transform(E_raw)
        Z_adj = pca.fit_transform(E_adj)

        def _mean_abs_corr(Z, X):
            # mean absolute correlation across PCs × covariates
            corrs = []
            for i in range(Z.shape[1]):
                zi = Z[:, i]
                for j in range(X.shape[1]):
                    xj = X[:, j]
                    c = np.corrcoef(zi, xj)[0, 1]
                    if np.isfinite(c):
                        corrs.append(abs(c))
            return float(np.mean(corrs)) if corrs else np.nan

        raw_corr = _mean_abs_corr(Z_raw, X_cov)
        adj_corr = _mean_abs_corr(Z_adj, X_cov)

        print("\nStyle-adjustment diagnostic (lower is better):")
        print(f"  Mean |corr(style covariate, PC score)| (raw embeddings):  {raw_corr:.4f}")
        print(f"  Mean |corr(style covariate, PC score)| (residual embeddings): {adj_corr:.4f}")
    except Exception as e:
        print(f"\n⚠️ Diagnostic skipped due to error: {e}")

    # ----------------------------
    # UMAP on residual embeddings
    # ----------------------------
    print("\nReducing residual embeddings to 2D using UMAP...")
    reducer_adj = umap.UMAP(
        n_neighbors=15,
        min_dist=0.1,
        n_components=2,
        metric='cosine',
        random_state=42
    )

    embeddings_2d_adj = reducer_adj.fit_transform(all_embeddings_resid)

    # Split back into groups
    human_2d_adj = embeddings_2d_adj[:n_human]
    ai_2d_adj = embeddings_2d_adj[n_human:]

    print(f"✓ UMAP completed: {len(embeddings_2d_adj)} proposals reduced to 2D")

    # Outlier coords
    outlier_indices_adj = np.where(outliers_adj)[0]
    outlier_coords_adj = embeddings_2d_adj[outlier_indices_adj]

    # Colors
    if 'colors' in globals() and isinstance(colors, dict):
        colors_local = dict(colors)
    else:
        colors_local = {'Human': '#DC143C'}

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # AI first (use labels from the NN cell; do NOT assume contiguous model blocks)
    for model in ai_models_local:
        mask = labels == model
        if mask.any():
            pts = embeddings_2d_adj[mask]
            ax.scatter(
                pts[:, 0], pts[:, 1],
                c=colors_local.get(model, '#808080'),
                label=model,
                s=100,
                alpha=0.55,
                edgecolors='black',
                linewidth=0.5
            )

    # Human on top
    ax.scatter(
        human_2d_adj[:, 0], human_2d_adj[:, 1],
        c=colors_local.get('Human', '#DC143C'),
        label='Human',
        s=120,
        alpha=0.85,
        edgecolors='black',
        linewidth=1.0,
        marker='o',
        zorder=10
    )

    # Outliers
    ax.scatter(
        outlier_coords_adj[:, 0], outlier_coords_adj[:, 1],
        s=420,
        facecolors='none',
        edgecolors='magenta',
        linewidth=2.5,
        alpha=0.75,
        label=f'Outliers (top 10% NN dist; thr={threshold_adj:.3f})',
        zorder=12
    )

    # Centroids (in 2D)
    human_centroid_2d = human_2d_adj.mean(axis=0)
    ax.scatter(
        human_centroid_2d[0], human_centroid_2d[1],
        c=colors_local.get('Human', '#DC143C'),
        s=420,
        marker='X',
        edgecolors='black',
        linewidth=2,
        alpha=1.0,
        zorder=15,
        label='Human centroid'
    )

    for model in ai_models_local:
        if model in model_2d_adj:
            c2d = model_2d_adj[model].mean(axis=0)
            ax.scatter(
                c2d[0], c2d[1],
                c=colors_local.get(model, '#808080'),
                s=380,
                marker='X',
                edgecolors='black',
                linewidth=1.5,
                alpha=0.9,
                zorder=14
            )

    ax.set_xlabel('UMAP Dimension 1', fontsize=13, fontweight='bold')
    ax.set_ylabel('UMAP Dimension 2', fontsize=13, fontweight='bold')
    ax.set_title('Style-adjusted Proposal Embedding Space (Residual embeddings)\n(UMAP 2D; magenta rings = outliers; X = centroids)',
                 fontsize=15, fontweight='bold', pad=20)

    ax.legend(loc='best', fontsize=9, framealpha=0.9, edgecolor='black')
    ax.grid(True, alpha=0.3, linestyle='--')

    # Annotation
    textstr = f'Total: {len(embeddings_2d_adj)} proposals\n'
    textstr += f'Human: {n_human} | AI: {n_ai}\n'
    textstr += f'Outliers: {len(outlier_indices_adj)} (top 10%)'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=props)

    plt.tight_layout()
    out_path = 'results/figures/embedding_space_2d_style_adjusted.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"\n✓ Figure saved to: {out_path}")
    print("\n💡 INTERPRETATION:")
    print("   - Clusters = similar proposals in style-adjusted residual space")
    print("   - Magenta rings = outliers by NN distance in residual space")
    print("   - X markers = group centroids in residual space")
    print("="*85)

########################################################################################################################
CELL 99
########################################################################################################################
import pandas as pd
import numpy as np

print("\n" + "="*85)
print("STYLE-ADJUSTED NN OUTLIERS: TITLES + AUTHOR")
print("="*85)

required = ['outliers_adj', 'threshold_adj', 'n_human']
missing = [v for v in required if v not in globals()]
if missing:
    print(f"⚠️ Missing variables: {missing}")
    print("Run the style-adjusted NN analysis cell first.")
else:
    outlier_indices = np.where(outliers_adj)[0]
    n_total = int(len(outliers_adj))
    n_ai = int(n_total - n_human)

    # Get style-adjusted NN distances if available; otherwise recompute quickly
    if 'nn_distances_adj' in globals():
        nn_d = np.asarray(nn_distances_adj)
    elif 'all_distances_adj' in globals():
        nn_d = np.min(np.asarray(all_distances_adj), axis=1)
    elif 'all_embeddings_resid' in globals():
        from sklearn.metrics.pairwise import cosine_distances
        D = cosine_distances(np.asarray(all_embeddings_resid))
        np.fill_diagonal(D, np.inf)
        nn_d = D.min(axis=1)
    else:
        nn_d = None

    # Prefer metadata saved alongside embeddings (guaranteed to match embedding order)
    use_metadata = ('ai_metadata' in globals()) and ('human_metadata' in globals())
    if use_metadata:
        if len(human_metadata) != n_human or len(ai_metadata) != n_ai:
            print("⚠️ Metadata lengths do not match embedding counts; falling back to df-based lookup.")
            use_metadata = False

    rows = []
    for idx in outlier_indices:
        if idx < n_human:
            who = 'Human'
            model = 'Human'
            if use_metadata:
                rec = human_metadata[idx]
                title = rec.get('proposal_title', rec.get('title', ''))
            else:
                title = human_df.iloc[idx].get('proposal_title', human_df.iloc[idx].get('title', '')) if 'human_df' in globals() else ''
        else:
            ai_idx = idx - n_human
            who = 'AI'
            if use_metadata:
                rec = ai_metadata[ai_idx]
                model = str(rec.get('model', 'AI'))
                title = str(rec.get('title', ''))
            else:
                model = str(ai_df.iloc[ai_idx].get('model', '')) if 'ai_df' in globals() else 'AI'
                title = str(ai_df.iloc[ai_idx].get('title', '')) if 'ai_df' in globals() else ''

        rows.append({
            'global_index': int(idx),
            'who': who,
            'model': model,
            'nn_distance_style_adj': float(nn_d[idx]) if nn_d is not None else np.nan,
            'title': title
        })

    out_df = pd.DataFrame(rows).sort_values('nn_distance_style_adj', ascending=False)

    print(f"Outlier threshold (90th percentile): {threshold_adj:.4f}")
    print(f"Total outliers: {len(out_df)} / {n_total} ({len(out_df)/n_total*100:.1f}%)")
    print("Outliers by source (model):")
    print(out_df['model'].value_counts().to_string())

    with pd.option_context('display.max_colwidth', 140):
        display(out_df.reset_index(drop=True))

