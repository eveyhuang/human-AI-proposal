from sklearn.manifold import TSNE

print("="*85)
print("VISUALIZING PROPOSALS IN LITERATURE EMBEDDING SPACE (t-SNE)")
print("="*85)

# Build aligned AI model labels
if 'ai_metadata' in globals() and isinstance(ai_metadata, list) and len(ai_metadata) == len(ai_embeddings):
    ai_model_labels = [str(r.get('model', 'AI')) for r in ai_metadata]
elif 'ai_df' in globals() and len(ai_df) == len(ai_embeddings) and 'model' in ai_df.columns:
    print("⚠️ Falling back to ai_df['model'] order.")
    ai_model_labels = [str(x) for x in ai_df['model'].tolist()]
else:
    raise RuntimeError("Cannot infer AI model labels aligned to ai_embeddings.")

ai_models_nov = sorted(list(dict.fromkeys(ai_model_labels)))
n_human_abs   = len(human_embeddings)
n_ai_abs      = len(ai_embeddings)

# t-SNE must be fit on ALL data jointly (no .transform() like UMAP)
print("\nFitting t-SNE on literature + proposals jointly...")
print("(This may take a minute...)")

proposals_stacked = np.vstack([human_embeddings, ai_embeddings])
all_embeddings_lit = np.vstack([literature_embeddings, proposals_stacked])

reducer_nov = TSNE(
    n_components=2,
    perplexity=30,
    metric='cosine',
    random_state=42,
    n_iter=1000,
    verbose=0
)
all_2d_nov = reducer_nov.fit_transform(all_embeddings_lit)

# Split back into literature vs proposals
n_lit = len(literature_embeddings)
literature_2d_nov = all_2d_nov[:n_lit]
proposals_2d_nov  = all_2d_nov[n_lit:]

human_2d_nov = proposals_2d_nov[:n_human_abs]
ai_2d_nov    = proposals_2d_nov[n_human_abs:]
ai_model_arr = np.array(ai_model_labels)

print(f"✓ Literature: {len(literature_2d_nov)} points  |  Proposals: {len(proposals_2d_nov)} points")

# ── Compute tight bounding boxes for each cluster ────────────────────────────
pad = 0.08  # 8% padding around each cluster

def _bounds(pts, pad_frac):
    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    xp = (xmax - xmin) * pad_frac
    yp = (ymax - ymin) * pad_frac
    return xmin - xp, xmax + xp, ymin - yp, ymax + yp

lit_bounds  = _bounds(literature_2d_nov, pad)
prop_bounds = _bounds(proposals_2d_nov,  pad)

# ── Shared scatter helper ─────────────────────────────────────────────────────
def _draw_all(ax, legend=False):
    ax.scatter(literature_2d_nov[:, 0], literature_2d_nov[:, 1],
               c='#AAAAAA', s=25, alpha=0.35, linewidths=0,
               label=f'Literature ({len(literature_embeddings)} articles)', zorder=1)

    for model in ai_models_nov:
        mask = ai_model_arr == model
        pts  = ai_2d_nov[mask]
        ax.scatter(pts[:, 0], pts[:, 1],
                   c=colors.get(model, '#808080'), label=model,
                   s=100, alpha=0.65, edgecolors='black', linewidth=0.5, zorder=3)

    ax.scatter(human_2d_nov[:, 0], human_2d_nov[:, 1],
               c=colors['Human'], label='Human',
               s=130, alpha=0.9, edgecolors='black', linewidth=0.8,
               marker='o', zorder=5)

    if 'outliers' in globals():
        outlier_coords_nov = proposals_2d_nov[outliers]
        ax.scatter(outlier_coords_nov[:, 0], outlier_coords_nov[:, 1],
                   s=400, facecolors='none', edgecolors='magenta',
                   linewidth=2.5, alpha=0.7,
                   label=f'Outliers (n={outliers.sum()})', zorder=8)

    ax.grid(True, alpha=0.3, linestyle='--')
    if legend:
        ax.legend(loc='best', fontsize=9, framealpha=0.9, edgecolor='black')

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, (ax_lit, ax_prop) = plt.subplots(1, 2, figsize=(18, 8))

_draw_all(ax_lit)
_draw_all(ax_prop, legend=True)

ax_lit.set_xlabel('t-SNE Dimension 1', fontsize=12, fontweight='bold')
ax_lit.set_ylabel('t-SNE Dimension 2', fontsize=12, fontweight='bold')
ax_lit.set_title('Left half of embedding space (x < midpoint)\n(contains parts of all clusters)',
                 fontsize=13, fontweight='bold')

ax_prop.set_xlabel('t-SNE Dimension 1', fontsize=12, fontweight='bold')
ax_prop.set_ylabel('t-SNE Dimension 2', fontsize=12, fontweight='bold')
ax_prop.set_title('Right half of embedding space (x ≥ midpoint)\n(contains parts of all clusters)',
                  fontsize=13, fontweight='bold')

fig.suptitle('Proposals in Literature Embedding Space  (t-SNE · Magenta = Outliers · Gray = Literature)',
             fontsize=14, fontweight='bold', y=1.01)

# tight_layout first, THEN set limits — so layout engine cannot override them
plt.tight_layout()

# Split the SAME embedding canvas into left vs right halves
all_pts = np.vstack([literature_2d_nov, proposals_2d_nov])
x_all = all_pts[:, 0]
y_all = all_pts[:, 1]

# Midpoint split (keeps left vs right halves of the canvas)
xsplit = (x_all.min() + x_all.max()) / 2

# Zoom each panel to the points that fall into its half (plus padding)
zoom_pad = 0.04  # smaller = tighter zoom

def _zoom_to(ax, mask):
    pts = all_pts[mask]
    if len(pts) == 0:
        return
    xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
    ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
    xp = (xmax - xmin) * zoom_pad
    yp = (ymax - ymin) * zoom_pad
    ax.set_xlim(xmin - xp, xmax + xp)
    ax.set_ylim(ymin - yp, ymax + yp)

left_mask  = x_all < xsplit
right_mask = ~left_mask

_zoom_to(ax_lit, left_mask)
_zoom_to(ax_prop, right_mask)

out_path = FIGURES_DIR / 'proposals_in_literature_space_tsne.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.show()
print(f"\n✓ Figure saved to: {out_path}")
print("="*85)