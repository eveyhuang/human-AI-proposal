import umap

print("="*85)
print("VISUALIZING PROPOSALS IN LITERATURE EMBEDDING SPACE (UMAP)")
print("="*85)

# Build aligned AI model labels locally so this cell does not depend on the t-SNE cell
if 'ai_metadata' in globals() and isinstance(ai_metadata, list) and len(ai_metadata) == len(ai_embeddings):
    ai_model_labels = [str(r.get('model', 'AI')) for r in ai_metadata]
elif 'ai_df' in globals() and len(ai_df) == len(ai_embeddings) and 'model' in ai_df.columns:
    print("⚠️ Falling back to ai_df['model'] order.")
    ai_model_labels = [str(x) for x in ai_df['model'].tolist()]
else:
    raise RuntimeError("Cannot infer AI model labels aligned to ai_embeddings.")

ai_models_nov = sorted(list(dict.fromkeys(ai_model_labels)))
ai_model_arr = np.array(ai_model_labels)
n_human_abs = len(human_embeddings)

proposals_stacked = np.vstack([human_embeddings, ai_embeddings])

# Fit UMAP on literature only; project proposals into that space
print("\nFitting UMAP on literature corpus...")
reducer_nov_umap = umap.UMAP(
    n_neighbors=20,
    min_dist=0.1,
    n_components=2,
    metric='cosine',
    random_state=42
)
literature_2d_umap = reducer_nov_umap.fit_transform(literature_embeddings)

print("Projecting proposals into literature UMAP space...")
proposals_2d_umap = reducer_nov_umap.transform(proposals_stacked)

human_2d_umap = proposals_2d_umap[:n_human_abs]
ai_2d_umap    = proposals_2d_umap[n_human_abs:]

print(f"✓ Literature: {len(literature_2d_umap)} points  |  Proposals: {len(proposals_2d_umap)} points")

# ── Shared scatter helper (UMAP version) ─────────────────────────────────────
def _draw_all_umap(ax, legend=False):
    ax.scatter(literature_2d_umap[:, 0], literature_2d_umap[:, 1],
               c='#AAAAAA', s=25, alpha=0.35, linewidths=0,
               label=f'Literature ({len(literature_embeddings)} articles)', zorder=1)

    for model in ai_models_nov:
        mask = ai_model_arr == model
        pts = ai_2d_umap[mask]
        ax.scatter(pts[:, 0], pts[:, 1],
                   c=colors.get(model, '#808080'), label=model,
                   s=100, alpha=0.65, edgecolors='black', linewidth=0.5, zorder=3)

    ax.scatter(human_2d_umap[:, 0], human_2d_umap[:, 1],
               c=colors['Human'], label='Human',
               s=130, alpha=0.9, edgecolors='black', linewidth=0.8,
               marker='o', zorder=5)

    if 'outliers' in globals():
        outlier_coords_umap = proposals_2d_umap[outliers]
        ax.scatter(outlier_coords_umap[:, 0], outlier_coords_umap[:, 1],
                   s=400, facecolors='none', edgecolors='magenta',
                   linewidth=2.5, alpha=0.7,
                   label=f'Outliers (n={outliers.sum()})', zorder=8)

    ax.grid(True, alpha=0.3, linestyle='--')
    if legend:
        ax.legend(loc='best', fontsize=9, framealpha=0.9, edgecolor='black')

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, (ax_lit, ax_prop) = plt.subplots(1, 2, figsize=(18, 8))

_draw_all_umap(ax_lit)
_draw_all_umap(ax_prop, legend=True)

ax_lit.set_xlabel('UMAP Dimension 1', fontsize=12, fontweight='bold')
ax_lit.set_ylabel('UMAP Dimension 2', fontsize=12, fontweight='bold')
ax_lit.set_title('Left half of embedding space (x < midpoint)\n(contains parts of all clusters)',
                 fontsize=13, fontweight='bold')

ax_prop.set_xlabel('UMAP Dimension 1', fontsize=12, fontweight='bold')
ax_prop.set_ylabel('UMAP Dimension 2', fontsize=12, fontweight='bold')
ax_prop.set_title('Right half of embedding space (x ≥ midpoint)\n(contains parts of all clusters)',
                  fontsize=13, fontweight='bold')

fig.suptitle('Proposals in Literature Embedding Space  (UMAP · Magenta = Outliers · Gray = Literature)',
             fontsize=14, fontweight='bold', y=1.01)

plt.tight_layout()

# Split into left vs right halves
all_pts_umap = np.vstack([literature_2d_umap, proposals_2d_umap])
x_all_umap = all_pts_umap[:, 0]

xsplit_umap = (x_all_umap.min() + x_all_umap.max()) / 2

zoom_pad_umap = 0.04

def _zoom_to_umap(ax, mask):
    pts = all_pts_umap[mask]
    if len(pts) == 0:
        return
    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    xp = (xmax - xmin) * zoom_pad_umap
    yp = (ymax - ymin) * zoom_pad_umap
    ax.set_xlim(xmin - xp, xmax + xp)
    ax.set_ylim(ymin - yp, ymax + yp)

left_mask_umap = x_all_umap < xsplit_umap
right_mask_umap = ~left_mask_umap

_zoom_to_umap(ax_lit, left_mask_umap)
_zoom_to_umap(ax_prop, right_mask_umap)

out_path_umap = FIGURES_DIR / 'proposals_in_literature_space_umap.png'
plt.savefig(out_path_umap, dpi=300, bbox_inches='tight')
plt.show()
print(f"\n✓ Figure saved to: {out_path_umap}")
print("="*85)
