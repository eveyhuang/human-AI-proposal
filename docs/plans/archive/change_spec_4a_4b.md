# Prep Layer — Modifying `4a` / `4b` for the Facet Pipeline

Version: 1.0
Date: 2026-07-15
Status: **Replaces §2's `00_prepare.ipynb` and `01_literature_map.ipynb` in
`diversity_facets_design_spec_v2.md`.** Those notebooks are NOT to be created. `4a` and `4b`
already perform their function and are retained with targeted modifications.

Read with: `diversity_facets_design_spec_v2.md` (the facet spec). This document defines the
**prep → analysis contract** that `02_facets_proposals`, `03_facets_reviews`, and `04_synthesis`
depend on.

---

## 0. Verdict — what already exists

`4a` and `4b` are **not** the messy part of the pipeline. They are already:
- **correctly parameterized** — both loop `for condition in CONDITIONS_TO_PREPARE: for text_version
  in TEXT_VERSIONS:` from a single config cell. The "don't clone a notebook per branch" rule in
  facet-spec §1.10 was aimed at `5a/5b/6a/6b`. **`4a`/`4b` already satisfy it. Do not restructure
  them.**
- **thin** — all logic lives in `src/prepare_proposals_for_analysis.py`,
  `src/prepare_literature_assets.py`, `src/prepare_reviews_for_analysis.py`. Correct architecture.
- **validated** — `validate_proposal_alignment`, `validate_review_alignment`, uid-uniqueness checks,
  row-count assertions, and a written manifest per (condition, branch). Keep all of it.
- **cached** — `REUSE_EXISTING_ARTIFACTS` + corpus hashing. Keep.

Coverage against the retired `00`/`01` design:

| Facet-spec `00`/`01` requirement | Status in `4a`/`4b` | Action |
|---|---|---|
| Roster load + alignment validation | ✅ `4a` cell 3/4, `4b` cell 2/3 | none |
| Proposal embeddings (BioLinkBERT-large) | ✅ `4a` — `full_text` + `abstract_text` | none |
| Review embeddings | ✅ `4b` — `review_text` (+ `strengths`/`weakness`) | none |
| Pairwise cosine matrices | ✅ both | none |
| PubMed corpus → embeddings | ✅ `4a` cell 3 | none |
| BERTopic fitted **once**, frozen | ✅ `4a` cell 3 (`fit_or_load_literature_bertopic`) | **gate failure** (§2.4) |
| Literature UMAP (illustration) | ✅ `4a` cell 3 | none |
| Proposal→literature KNN (for M6) | ✅ `4a` — `k=50`, from `abstract_text` | none (§2.6) |
| Review panel registry / sampling frame | ✅ `4b` cell 3 | none |
| **L2-normalized embeddings** | ❓ **unverified** — inside `build_embedding_bundle` | **§2.1 — CRITICAL** |
| **Pooled-AI subsample index cache** | ❌ **missing** | **§2.2 — must add** |
| **Exact-n review panel enumeration** | ❌ **explicitly not done** ("does not pre-sample exact-n matched AI panels") | **§3.2 — must add** |
| **MeSH index per literature article** | ❓ unverified — may be in `literature_article_index` | **§2.3 — verify/add** |
| **`n_regions_total` exposed for M6** | ❌ missing from manifest | **§2.5 — must add** |

**Five real gaps.** Everything else stays untouched.

---

## 1. Naming reconciliation (do this first — it touches every downstream notebook)

The facet spec used `branch`; `4a`/`4b` use `text_version`. **Adopt `text_version` everywhere.**
It is already written into every manifest and directory path; renaming the data layer to match a
document is backwards.

| Facet-spec v2 said | Use instead | Where |
|---|---|---|
| `branch` | **`text_version`** | CONFIG dicts, results-schema column, all joins |
| `data/cache/{condition}/{branch}/` | **`data/prepared/{condition}/{proposals\|reviews}/{text_version}/`** | all loads |
| `subsample_idx_ai_n23_seed42.npy` | same name, new location (§2.2) | `02` |
| `review_panels_exact_n.pkl` | same name, new location (§3.2) | `03` |

**Edit `diversity_facets_design_spec_v2.md`:** global replace `branch` → `text_version` in §1.9,
§1.10, §2, §10.3, §11.4, §12.1–12.5, §15. The `results/tables/.../{text_version}/...` layout in
§12.5 stays otherwise unchanged.

**One value-level note:** `TEXT_VERSIONS = ['original', 'rephrased']` in `4a`/`4b`. The manuscript
designates **`rephrased` as primary** (style-controlled) and `original` as the robustness check.
That ordering is a *reporting* convention, not a prep concern — no change to `4a`/`4b`.

---

## 2. `4a_prepare_proposal_for_analysis.ipynb` — modifications

### 2.1 CRITICAL — guarantee L2-normalized embeddings
Every facet metric assumes L2-normalized vectors (facet-spec §1.1/§1.2). `compute_pairwise_cosine_matrix`
is normalization-invariant, so **the cached pairwise matrices are fine either way** — but M1 (kernel),
M3 (covariance), and M5 (MMD/OT) consume **raw vectors**, where it matters. Whether
`build_embedding_bundle` normalizes is not visible from the notebook.

**Agent instructions:**
1. Inspect `src/prepare_proposals_for_analysis.py::build_embedding_bundle` and
   `src/prepare_literature_assets.py::build_or_load_literature_embeddings`.
2. If they do **not** L2-normalize, add a finalization step that normalizes **in place and re-saves**,
   then records the fact in the manifest. Do **not** rely on downstream normalization — a single
   choke point at write time is safer than trusting four consumers to remember.

```python
# add to src/prepare_proposals_for_analysis.py
def finalize_embedding_bundle(bundle, atol=1e-5):
    """Ensure bundle['embeddings'] is L2-normalized. Idempotent. Records provenance."""
    X = np.asarray(bundle['embeddings'], dtype=np.float64)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    if np.allclose(norms, 1.0, atol=atol):
        bundle['l2_normalized'] = True
        return bundle
    if (norms == 0).any():
        raise ValueError('zero-norm embedding row — cannot normalize')
    bundle['embeddings'] = X / norms
    bundle['l2_normalized'] = True
    bundle['normalization'] = 'l2_post_hoc'
    return bundle
```
3. Call it on **every** bundle in `4a` (`full_bundle`, `abstract_bundle`, `literature_bundle`) and in
   `4b` (`text_bundle`, `strengths_bundle`, `weakness_bundle`) immediately after construction, before
   `compute_pairwise_cosine_matrix`.
4. Add `'embeddings_l2_normalized': True` to every manifest.
5. **Cache invalidation:** normalizing is a cheap pass over existing vectors — it does **not** require
   re-embedding. Do not force `REUSE_EXISTING_ARTIFACTS = False`; that would re-embed 39,538 PubMed
   abstracts for no reason. Load → normalize → re-save.
6. Downstream (`02`/`03`) asserts `manifest['embeddings_l2_normalized'] is True` on load and raises
   otherwise.

> **Why this is #1:** if the vectors aren't normalized, M1's Gram matrix has `K_ii ≠ 1`, the Vendi
> eigen-spectrum is no longer a probability vector, and `VS_q` is silently wrong — no error, just a
> wrong number. Same class of failure for M5's median-heuristic bandwidth. This is the one gap that
> produces plausible-looking garbage rather than a crash.

### 2.2 Add the pooled-AI subsample index cache
Facet-spec §1.5 requires a frozen, without-replacement subsample cache. It does not exist.

**Add a new cell to `4a`, after the per-condition loop** (or inside it, per condition):
```python
import numpy as np

SUBSAMPLE_B = 1000
SUBSAMPLE_SEED = 42
SUBSAMPLE_N = 23                      # = human n; keep tied to the human roster, not hard-coded blind

for condition, branch_outputs in condition_prepare_outputs.items():
    for text_version, result in branch_outputs.items():
        master_df = result['master_df']
        ai_pos = np.flatnonzero((master_df['source_type'] == 'ai').to_numpy())
        n_human = int((master_df['source_type'] == 'human').sum())
        if n_human != SUBSAMPLE_N:
            raise RuntimeError(f'{condition}/{text_version}: human n={n_human}, expected {SUBSAMPLE_N}')

        rng = np.random.default_rng(SUBSAMPLE_SEED)
        idx = np.stack([rng.choice(ai_pos, size=SUBSAMPLE_N, replace=False)
                        for _ in range(SUBSAMPLE_B)])          # (1000, 23)

        out = (PROJECT_ROOT / 'data' / 'prepared' / condition / 'proposals' / text_version
               / 'subsample_idx_ai_n23_seed42.npy')
        np.save(out, idx)
        print(f'  {condition}/{text_version}: subsample cache {idx.shape} -> {out}')
```
**Notes for the agent:**
- Indices are **positional rows into `master_df` / the embedding bundle**, not `proposal_uid`s — so
  `X[idx[b]]` works directly. The row order is already frozen by
  `manifest['proposal_uid_order']`; downstream must assert that order matches before using the cache.
- `replace=False` — **without replacement**. Never change this. Facet-spec §1.4 forbids
  with-replacement resampling for every metric in the battery (duplicates deflate diversity).
- Record in the manifest: `'subsample_idx_file'`, `'subsample_B': 1000`, `'subsample_seed': 42`,
  `'subsample_n': 23`, `'subsample_replace': False`.

### 2.3 Verify / add the MeSH index (M6 dependency)
M6 (`coverage_mesh_terms`) needs MeSH descriptors per literature article.
`normalize_literature_articles` produces `literature_article_index` → `literature_article_index.csv`,
but whether it carries MeSH is unverified.

**Agent instructions:**
1. Inspect `src/prepare_literature_assets.py::normalize_literature_articles` and the columns of
   `data/prepared/literature/literature_article_index.csv`.
2. If a MeSH column exists (any of `mesh_terms`, `mesh_headings`, `descriptors`), ensure it is stored
   as a **list-valued** column, not a raw delimited string. Persist as parquet, or write a companion
   `literature_mesh_index.parquet` with schema `article_row_idx:int, mesh_terms:list[str]`.
3. If MeSH is **not** present, check the raw `relevant-corpus-from-pubmed.json` payload for a MeSH
   field and extract it. If the corpus has no MeSH at all, **stop and report** — do not silently
   proceed; `coverage_mesh_terms` must then be dropped from M6 and the facet spec's §9 amended to
   region-coverage only.
4. Row order of the MeSH index **must** match `literature_article_index` and `literature_bundle`
   row-for-row. Assert `len(mesh_index) == len(literature_article_index) == len(literature_bundle['embeddings'])`.
5. Manifest: `'mesh_index_file'`, `'mesh_available': bool`, `'mesh_n_unique_total': int`.

### 2.4 Gate the BERTopic failure — do not swallow it
`4a` cell 3 wraps BERTopic in `try/except`, sets `bertopic_status='failed'`, and **continues**. That
is right for a prep notebook whose other outputs are independent — but M6 then has no data, and the
failure is only visible in a manifest field nobody reads.

**Agent instructions:**
- Keep the `try/except` (don't let a BERTopic failure block proposal embeddings).
- Add an explicit gate at the **end** of `4a`:
```python
M6_REQUIRED = True     # set False if the domain-coverage facet (M6) is out of scope

if M6_REQUIRED and bertopic_status != 'ready':
    raise RuntimeError(
        f'M6 (domain coverage) requires BERTopic, but status={bertopic_status!r}: {bertopic_error}\n'
        'Either fix the BERTopic step or set M6_REQUIRED=False and drop §9 from the facet spec.'
    )
```
- Same treatment for `lit_umap_status`: it is **illustration-only** (facet-spec §1.1), so a failure
  must **not** raise — it only costs you Figure 4. Print a warning and continue. Do not conflate the
  two: BERTopic feeds a metric; the UMAP feeds a picture.

### 2.5 Expose `n_regions_total` for M6
`region_coverage(topic_ids, n_regions_total)` needs the denominator. Add to the literature manifest:
```python
n_regions_total = int(bertopic_topic_info_df['Topic'].nunique()) if bertopic_status == 'ready' else 0
n_regions_excl_outlier = int((bertopic_topic_info_df['Topic'] != -1).sum()) if bertopic_status == 'ready' else 0
literature_manifest['n_regions_total'] = n_regions_total
literature_manifest['n_regions_excl_outlier'] = n_regions_excl_outlier
```
> **[DECISION — the agent must not guess]** BERTopic assigns `Topic = -1` to outliers. Is `-1` a
> "region" for coverage purposes? **Recommendation: exclude it.** `-1` is "no topic," so counting it
> would credit a group for landing in the unassigned bin — which is the opposite of topical coverage.
> Use `n_regions_excl_outlier` as the M6 denominator and **filter `-1` out of the numerator too**.
> Record the choice in the manifest and state it in Methods. Whichever you pick, apply it identically
> to every group or the comparison is invalid.

### 2.6 Keep `PROPOSAL_TO_LITERATURE_K = 50` — no change
Facet-spec §9.2 specified `k=10` with a `{5, 10, 20}` sweep. `4a` already stores `k=50`. **This is
strictly better** — a `k=50` neighbor list is a superset; `02` slices `[:, :k]` for any `k ≤ 50` with
zero recomputation. Leave it. Facet-spec §9.2's "k=10 default, sweep {5,10,20}" becomes a *downstream
slicing* parameter, not a prep parameter.

**One thing to document, not change:** the KNN is built from **`abstract_text`** embeddings while
M0–M5 run on **`full_text`**. That is defensible — proposal abstracts are the right comparand for
PubMed abstracts, and matching full grant text against abstracts would be a register mismatch. But it
means Facet 5's two halves rest on different text fields. State it in Methods; do not "fix" it.

---

## 3. `4b_prepare_review_for_analysis.ipynb` — modifications

### 3.1 CRITICAL — L2-normalize
Identical to §2.1. Apply `finalize_embedding_bundle` to `text_bundle`, `strengths_bundle`,
`weakness_bundle`. Add `'embeddings_l2_normalized': True` to the review manifests.

> **Pooling inconsistency — flag, don't fix.** `4a` uses `pooling='cls'` for proposals; `4b` uses
> `pooling='mean'` for reviews. Same encoder, different pooling ⇒ proposal-space and review-space
> geometries are **not** directly comparable. This is *fine* for the analysis as designed, because
> `04_synthesis` compares only **AI÷Human ratios within each task** (facet-spec §15.2), never raw
> values across tasks. But it is exactly the kind of thing a reviewer asks about. Record both pooling
> choices in the manifests and state the ratio-only comparison in Methods. **Do not harmonize
> pooling** without re-running everything.

### 3.2 Add exact-n panel enumeration (M0–M2 reviews depend on it)
`4b`'s markdown states: *"It keeps the full repeated-review reservoir intact and does not pre-sample
exact-n matched AI panels."* The registry (`review_panel_registry.csv`) and sampling frame exist, but
the **enumerated panels** do not.

`build_review_panel_distance_cache` caches per-proposal panel **distances** — that is insufficient:
M1 needs the kernel and M3 needs the covariance, both of which require **raw vectors**, not a
distance matrix. So the enumeration must yield **row indices**, from which `03` slices embeddings.

**Add `src/panels.py`:**
```python
from itertools import combinations
import numpy as np

MAX_PANELS_PER_MODEL = 5000     # C(5,m) is tiny; C(15,m) can reach 6435 at m=7 — cap defensively

def enumerate_exact_n_panels(master_df, models=('claude', 'gemini', 'gpt'), rng_seed=42):
    """For each target proposal, enumerate exact-n matched AI panels.

    Returns {target_proposal_uid: {
        'm': int,                       # human panel size for this proposal
        'human_idx': np.ndarray,        # (m,) positional rows into the embedding bundle
        'per_model': {model: [np.ndarray(m), ...]},   # all C(5,m) panels
        'pooled':    [np.ndarray(m), ...],            # C(15,m) panels, capped by sampling
    }}
    """
    rng = np.random.default_rng(rng_seed)
    pos = np.arange(len(master_df))
    out = {}
    for uid, grp in master_df.groupby('target_proposal_uid', sort=True):
        human_rows = pos[(master_df['target_proposal_uid'] == uid).to_numpy()
                         & (master_df['review_source'] == 'human').to_numpy()]
        m = len(human_rows)
        if m < 2:
            raise RuntimeError(f'{uid}: human panel size {m} < 2 — cannot measure within-panel spread')

        per_model = {}
        for model in models:
            rows = pos[(master_df['target_proposal_uid'] == uid).to_numpy()
                       & (master_df['review_source'] == 'ai').to_numpy()
                       & (master_df['review_model'] == model).to_numpy()]
            if len(rows) < m:
                raise RuntimeError(f'{uid}/{model}: {len(rows)} AI reviews < human panel size {m}')
            per_model[model] = [np.array(c) for c in combinations(rows, m)]

        pooled_rows = pos[(master_df['target_proposal_uid'] == uid).to_numpy()
                          & (master_df['review_source'] == 'ai').to_numpy()]
        pooled_all = list(combinations(pooled_rows, m))
        if len(pooled_all) > MAX_PANELS_PER_MODEL:
            pick = rng.choice(len(pooled_all), size=MAX_PANELS_PER_MODEL, replace=False)
            pooled_all = [pooled_all[i] for i in pick]
        pooled = [np.array(c) for c in pooled_all]

        out[str(uid)] = {'m': m, 'human_idx': human_rows, 'per_model': per_model, 'pooled': pooled}
    return out
```
**Add a cell to `4b`**, inside the condition loop, after `panel_cache`:
```python
from panels import enumerate_exact_n_panels
import pickle

panels = enumerate_exact_n_panels(master_df)
panels_path = output_dir / 'review_panels_exact_n.pkl'
with open(panels_path, 'wb') as fh:
    pickle.dump(panels, fh)
manifest['review_panels_exact_n_file'] = str(panels_path)
manifest['panel_sizes'] = {uid: p['m'] for uid, p in panels.items()}
print(f'  {text_version}: enumerated panels for {len(panels)} target proposals')
```
**Notes for the agent:**
- Column names above (`review_source`, `review_model`, `target_proposal_uid`) are inferred from `4b`'s
  existing usage. **Verify against `review_master.csv` and correct if they differ** — do not assume.
- Enumerate **per text_version**, because positional rows index that branch's bundle. The *panel
  composition* is identical across branches (same roster, guaranteed by `validate_review_alignment`),
  but the row indices must match the bundle they'll be used against.
- Enumerated AI panels are **computational artifacts, not inferential n** (facet-spec §11.1). `03`
  averages the metric over panels per proposal; the inferential n is 23 proposals.

### 3.3 Document the strengths/weakness asymmetry
`4b` builds `strengths_bundle` / `weakness_bundle` **only when `text_version == 'rephrased'`**. That
is a deliberate, sensible choice (the field split is a product of the rephrasing step). But
facet-spec §11.4 presents `field ∈ {whole, strengths, weakness}` as a free config parameter.

**Do not change `4b`.** Instead, constrain downstream: **`field ∈ {strengths, weakness}` is valid only
for `text_version == 'rephrased'`.** `03` must skip those cells rather than crash. Add to the manifest:
```python
manifest['fields_available'] = ['whole'] + (['strengths', 'weakness'] if text_version == 'rephrased' else [])
```
and have `03` read `fields_available` instead of assuming.

### 3.4 Panel registry is built from `original` only — verify, don't change
`4b` builds `panel_registry_df` / `sampling_frame_df` from `branch_masters['original']` and writes
them to the shared `reviews_root` (not per-branch). This is correct **iff** the `review_uid` roster is
identical across branches — which `validate_review_alignment` already enforces. Add one assertion to
make the dependency explicit rather than implicit:
```python
assert set(branch_masters['original']['review_uid']) == set(branch_masters['rephrased']['review_uid']), \
    'panel registry is branch-shared but rosters diverge'
```

---

## 4. The prep → analysis contract

`02`, `03`, `04` may read **only** these. Everything else is prep-internal.

### 4.1 Proposals — `data/prepared/{condition}/proposals/{text_version}/`
| File | Consumed by | Notes |
|---|---|---|
| `proposal_master.csv` | 02 | `proposal_uid`, `source_type` (human/ai), model, cohort, `persona_card_id` |
| `proposal_embeddings_full.pkl` | 02 — **M0, M1, M3, M4, M5** | **primary**; L2-normalized (§2.1) |
| `proposal_embeddings_abstract.pkl` | 02 — robustness | secondary |
| `proposal_pairwise_cosine_full.npy` | 02 — M0, M2, M4 fast paths | (92, 92) |
| `proposal_to_literature_knn.npz` | 02 — **M6** | k=50; slice `[:, :k]` |
| `subsample_idx_ai_n23_seed42.npy` | 02 — pooled comparisons | **NEW** (§2.2) |
| `proposal_umap2d.npy` | 04 — Figure 4 only | **never a metric input** |
| `prepare_manifest.json` | 02 — assertions | `proposal_uid_order`, `embeddings_l2_normalized` |

### 4.2 Literature (shared, once) — `data/prepared/literature/` + `data/embeddings/literature/`
| File | Consumed by | Notes |
|---|---|---|
| `lit_bertopic_assignments.csv` | 02 — M6 | topic id per article |
| `lit_bertopic_topic_info.csv` | 02 — M6 | `n_regions_total` (§2.5) |
| `literature_mesh_index.parquet` | 02 — M6 | **NEW/verify** (§2.3) |
| `literature_prepare_manifest.json` | 02 — assertions | `corpus_hash`, `bertopic_status`, `n_regions_excl_outlier` |
| `lit_umap2d.npy` | 04 — Figure 4 only | **never a metric input** |

### 4.3 Reviews — `data/prepared/{condition}/reviews/{text_version}/`
| File | Consumed by | Notes |
|---|---|---|
| `review_master.csv` | 03 | `review_uid`, `target_proposal_uid`, `review_source`, `review_model` |
| `review_embeddings_text.pkl` | 03 — **M0–M2 (whole)** | L2-normalized (§3.1) |
| `review_embeddings_{strengths,weakness}.pkl` | 03 — field-specific | **rephrased only** (§3.3) |
| `review_pairwise_cosine_text.npy` | 03 — fast paths | |
| `review_panels_exact_n.pkl` | 03 — **all paired metrics** | **NEW** (§3.2) |
| `review_umap2d.npy` | 04 — Figure 4 only | **never a metric input** |
| `prepare_manifest.json` | 03 — assertions | `review_uid_order`, `fields_available`, `panel_sizes` |
| `../review_panel_registry.csv` | 03 — reference | branch-shared |

### 4.4 Load-time assertions `02`/`03` must make
```python
man = json.loads((prep_dir / 'prepare_manifest.json').read_text())
assert man['embeddings_l2_normalized'] is True,        'run modified 4a/4b first (§2.1)'
assert man['proposal_uid_order'] == master_df['proposal_uid'].astype(str).tolist(), \
       'row order drift — subsample/panel indices are positional and would be silently wrong'
assert man['embedding_model_name'] == EXPECTED_ENCODER
# M6 only:
assert lit_man['bertopic_status'] == 'ready', 'M6 requires BERTopic (§2.4)'
```
The `proposal_uid_order` assertion is not ceremony: `subsample_idx_ai_n23_seed42.npy` and
`review_panels_exact_n.pkl` store **positional** indices. If prep is re-run and row order changes,
every index silently points at the wrong row and the analysis produces plausible, wrong numbers.

---

## 5. Amendments to `diversity_facets_design_spec_v2.md`

| § | Change |
|---|---|
| §2.1 layout | Delete `00_prepare.ipynb` and `01_literature_map.ipynb`. Replace with `4a_prepare_proposal_for_analysis.ipynb` (proposals **+ literature**) and `4b_prepare_review_for_analysis.ipynb`. Pipeline: `4a → 4b → 02 → 03 → 04`. |
| §2.4 caches | Replace the whole path block with §4 of this document. |
| §1.5 | Subsample cache is built by **`4a`** (§2.2 here), not `00`. Path: `data/prepared/{condition}/proposals/{text_version}/subsample_idx_ai_n23_seed42.npy`. |
| §1.9, §1.10, §10.3, §11.4, §12, §15 | `branch` → **`text_version`** globally. |
| §9.1 (M6 prep) | Delete "`01_literature_map.ipynb` runs once." The literature map is built by `4a` cell 3. Keep the **fit-once-and-freeze** rule — `fit_or_load_literature_bertopic` already enforces it. |
| §9.2 | `k=10` default + `{5,10,20}` sweep is a **downstream slice** of the cached `k=50` list, not a prep parameter (§2.6). |
| §11.1 | Panel enumeration is built by **`4b`** (§3.2 here) into `review_panels_exact_n.pkl`, not by `00`. |
| §11.4 | `field` is constrained by `manifest['fields_available']` — strengths/weakness are **rephrased-only** (§3.3). |
| §13 build order | Becomes: (1) `src/diversity_facets.py` + tests → (2) `src/diversity_inference.py` → (3) `src/panels.py` → (4) **modify `4a`** (§2) → (5) **modify `4b`** (§3) → (6) `02` → (7) `03` → (8) `04`. |
| §14 sanity checks | Add: "assert `embeddings_l2_normalized`"; "assert `proposal_uid_order` matches before using positional caches"; "BERTopic `-1` outlier handling is identical across all groups." |

---

## 6. Execution order & one-time migration

```
1. Inspect src/prepare_*.py for L2 normalization          (§2.1)
2. Inspect literature_article_index.csv for MeSH          (§2.3)
   → if absent, STOP and report before writing any code
3. Add finalize_embedding_bundle + manifest flags         (§2.1, §3.1)
4. Add src/panels.py                                      (§3.2)
5. Modify 4a: normalize, subsample cache, BERTopic gate,
   n_regions_total, MeSH index                            (§2)
6. Modify 4b: normalize, panel enumeration, assertions    (§3)
7. Re-run 4a then 4b with REUSE_EXISTING_ARTIFACTS = True
   (normalization is a re-save, not a re-embed — do NOT
    force a rebuild of the 39,538-abstract corpus)
8. Verify every file in §4 exists for all 3 conditions
   × 2 text_versions before starting 02
```

**Do not restructure `4a`/`4b`.** They are already condition × text_version parameterized, thin,
validated, cached, and manifest-writing. The five gaps above are additive. The mess that motivated
the rebuild lives in `5a/5b/6a/6b`, which `02`/`03`/`04` replace.
