# Save: NN distances + outlier flags
import pandas as pd, numpy as np; from pathlib import Path
out_dir = TABLES_DIR; out_dir.mkdir(parents=True, exist_ok=True)
rows = [{'title': r.get('proposal_title', r.get('title','')), 'group': 'Human',
         'nn_dist': human_nn_dists[i], 'is_outlier': bool(outliers[i])}
        for i, r in enumerate(human_metadata)]
mc = {m: 0 for m in ai_models_local}
for j, r in enumerate(ai_metadata):
    m = r.get('model','AI'); k = mc.get(m,0)
    rows.append({'title': r.get('title', r.get('proposal_title','')), 'group': m,
                 'nn_dist': model_nn_dists[m][k] if m in model_nn_dists and k < len(model_nn_dists[m]) else np.nan,
                 'is_outlier': bool(outliers[len(human_metadata)+j])})
    mc[m] = k+1
df = pd.DataFrame(rows); df['threshold'] = threshold
df.to_csv(out_dir/'nn_distances.csv', index=False)
print(f"Saved nn_distances.csv  ({len(df)} rows, threshold={threshold:.4f})")
print(df.groupby('group')[['nn_dist','is_outlier']].agg({'nn_dist':'mean','is_outlier':'sum'}))
