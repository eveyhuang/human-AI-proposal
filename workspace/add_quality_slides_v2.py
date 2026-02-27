#!/usr/bin/env python3
"""
Add 13 quality-analysis slides to the diversity presentation,
replacing the existing slides 18-19 (Key Findings / Implications).

Run from the project root:
    python workspace/add_quality_slides_v2.py
"""
import csv, html, os, re, shutil, tempfile, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

PPTX_PATH = Path('results/diversity_analysis_presentation_baseline_updated_20260218.pptx')
FIG_DIR   = Path('results/figures/quality')

# XML namespaces
P_NS  = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A_NS  = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_NS  = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'

ET.register_namespace('p',  P_NS)
ET.register_namespace('a',  A_NS)
ET.register_namespace('r',  R_NS)
ET.register_namespace('',   PR_NS)

# ── Colour palette (matches existing deck) ──────────────────────────────────
NAVY   = '1B2A4A'
WHITE  = 'FFFFFF'
TEXT   = '2C3E50'
ACCENT = 'E8505B'
GRAY   = '5D6D7E'
GREEN  = '27AE60'   # positive / significant
ORANGE = 'E67E22'   # caution / marginal
RED    = 'C0392B'   # warning / limitation


# ── Helpers ──────────────────────────────────────────────────────────────────

def read_csv(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

def find_row(rows, **conds):
    for r in rows:
        if all(str(r.get(k)) == str(v) for k, v in conds.items()):
            return r
    return {}

def fn(x, d=2):
    try:   return f'{float(x):.{d}f}'
    except: return 'NA'

def ppt_esc(s):
    return html.escape(str(s), quote=False)

def font():
    return '<a:latin typeface="Arial"/><a:ea typeface="Arial"/><a:cs typeface="Arial"/>'


# ── XML building blocks ──────────────────────────────────────────────────────

def header_shapes(title, subtitle):
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="HeaderBar"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="9144000" cy="650000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>'

        f'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Title"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="500000" y="170000"/><a:ext cx="8300000" cy="300000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/>'
        f'<a:p><a:pPr algn="l"/><a:r>'
        f'<a:rPr sz="2000" b="1"><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill>{font()}</a:rPr>'
        f'<a:t>{ppt_esc(title)}</a:t></a:r></a:p></p:txBody></p:sp>'

        f'<p:sp><p:nvSpPr><p:cNvPr id="4" name="Subtitle"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="500000" y="760000"/><a:ext cx="8300000" cy="260000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/>'
        f'<a:p><a:pPr algn="l"/><a:r>'
        f'<a:rPr sz="1050" b="1"><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill>{font()}</a:rPr>'
        f'<a:t>{ppt_esc(subtitle)}</a:t></a:r></a:p></p:txBody></p:sp>'

        f'<p:sp><p:nvSpPr><p:cNvPr id="5" name="Accent"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="500000" y="1050000"/><a:ext cx="500000" cy="23000"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:solidFill><a:srgbClr val="{ACCENT}"/></a:solidFill></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody></p:sp>'
    )


def para(text, size=900, color=TEXT, bold=False, italic=False):
    b = ' b="1"' if bold else ''
    i = ' i="1"' if italic else ''
    return (
        f'<a:p><a:pPr algn="l"/><a:r>'
        f'<a:rPr sz="{size}"{b}{i}>'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{font()}</a:rPr>'
        f'<a:t>{ppt_esc(text)}</a:t></a:r></a:p>'
    )


def textbox(sid, x, y, cx, cy, lines, size=900, color=TEXT, bold=False):
    paras = ''.join(para(l, size=size, color=color, bold=bold) for l in lines)
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Txt{sid}"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>'
    )


def mixed_textbox(sid, x, y, cx, cy, items):
    """items: list of (text, size, color, bold) tuples."""
    paras = ''.join(para(t, size=s, color=c, bold=b) for t, s, c, b in items)
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Txt{sid}"/>'
        f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>'
    )


def image_shape(sid, rid, x, y, cx, cy):
    return (
        f'<p:pic><p:nvPicPr><p:cNvPr id="{sid}" name="Pic{sid}"/>'
        f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
    )


def wrap_slide(shapes_xml):
    return (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<p:sld xmlns:a="{A_NS}" xmlns:r="{R_NS}" xmlns:p="{P_NS}">'
        f'<p:cSld><p:bg><p:bgPr>'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/>'
        f'</p:bgPr></p:bg>'
        f'<p:spTree>'
        f'<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        f'<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        f'{shapes_xml}'
        f'</p:spTree></p:cSld>'
        f'<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
        f'</p:sld>'
    )


def rels_xml(image_targets):
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Relationships xmlns="{PR_NS}">',
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>',
    ]
    for i, tgt in enumerate(image_targets, start=2):
        lines.append(
            f'  <Relationship Id="rId{i}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="../media/{tgt}"/>'
        )
    lines.append('</Relationships>')
    return '\n'.join(lines)


# ── Slide builders ────────────────────────────────────────────────────────────
# Layout constants (EMU): slide 9144000 × 5143500
# Content area: y=1200000 to y≈5100000, x=500000 to x≈8644000
# Two-image row: each image 4000000 wide, h=2500000, y=1250000
# Text footer: y=3900000, h=1200000

def slide_18_overview(v):
    """Part IV Quality: Why three linked analyses?"""
    s = header_shapes(
        'Part IV Quality: Why Three Linked Analyses?',
        'Motivation, analytical logic, and how R1, R2, and R3 connect'
    )
    items = [
        ('Motivation:', 950, NAVY, True),
        ('Diversity and novelty analyses (Parts I–III) tell us whether AI proposals explore different intellectual territory.', 880, TEXT, False),
        ('They do not tell us whether those proposals are high-quality, rigorous, or fundable. That requires explicit quality scoring.', 880, TEXT, False),
        ('But quality scoring with AI evaluators introduces new risks: evaluator leniency differences and self-preference bias.', 880, TEXT, False),
        ('', 600, TEXT, False),
        ('Three linked sub-analyses:', 950, NAVY, True),
        ('R1  Proxy Validity: Are AI reviews textually and judgmentally similar to expert human reviews?', 880, TEXT, False),
        ('    Without this, AI-judged quality scores have no established relationship to expert opinion.', 820, GRAY, False),
        ('R2  Proposal Quality: Do AI-generated proposals score higher than human-authored proposals under AI evaluation?', 880, TEXT, False),
        ('    This is the core substantive question—but only interpretable after R1 and R3 are addressed.', 820, GRAY, False),
        ('R3  Evaluator Bias: Do AI evaluators show systematic leniency differences or self-preference?', 880, TEXT, False),
        ('    If yes, R2 conclusions are confounded and must be re-run with bias controls.', 820, GRAY, False),
        ('', 600, TEXT, False),
        ('Analytical sequence: R1 validates the instrument \u2192 R3 diagnoses bias \u2192 bias-controlled R2 enables valid inference.', 870, ACCENT, True),
    ]
    s += mixed_textbox(6, 500000, 1200000, 8400000, 3800000, items)
    return wrap_slide(s), []


def slide_19_r1_method(v):
    """R1 Method: Validating the evaluation instrument."""
    s = header_shapes(
        'R1 Method: Validating the Evaluation Instrument Before Interpreting Scores',
        'Cosine similarity, sentiment alignment, and categorical agreement across review pair types'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4600000, 3100000)
    items = [
        ('Why this analysis:', 900, NAVY, True),
        ('If AI reviewers produce fundamentally different assessments than human experts, using them as a quality proxy', 820, TEXT, False),
        ('is methodologically indefensible. R1 tests whether AI reviews are in the same "critical space" as human reviews.', 820, TEXT, False),
        ('', 500, TEXT, False),
        ('Design:', 900, NAVY, True),
        ('12 Y1 proposals were reviewed by both expert human panels and all 3 AI models, enabling direct pair comparison.', 820, TEXT, False),
        ('Three pair types: Human\u2013Human (HH), Human\u2013AI (HAI), AI\u2013AI (AIAI).', 820, TEXT, False),
        ('Metrics: cosine similarity (sentence-BERT embeddings), sentiment polarity alignment, categorical agreement.', 820, TEXT, False),
        ('', 500, TEXT, False),
        ('Method argument:', 900, NAVY, True),
        ('Scores averaged to proposal level (n=12) before testing, avoiding pairwise pseudo-replication.', 820, TEXT, False),
        ('Paired Wilcoxon signed-rank is the primary test (same 12 proposals in both groups); BH-FDR controls multiplicity.', 820, TEXT, False),
        ('Figure: proposal-level paired slopes show within-proposal changes across pair types.', 820, GRAY, False),
    ]
    s += mixed_textbox(7, 5200000, 1250000, 3400000, 3100000, items)
    return wrap_slide(s), ['quality_similarity_proxy_paired_slopes.png']


def slide_20_r1_results(v):
    """R1 Results: similarity structure."""
    s = header_shapes(
        'R1 Results: AI Reviews Are Aligned With Humans—But AI Judges Cluster Tightly',
        'Human\u2013AI similarity is not significantly lower than human\u2013human; AI\u2013AI similarity is dramatically higher'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 3950000, 2600000)
    s += image_shape(7, 'rId3', 4650000, 1250000, 3950000, 2600000)
    items = [
        (f"Human\u2013AI vs Human\u2013Human cosine: q={v['r1_hai_hh_q']}, \u03b4={v['r1_hai_hh_d']} (small, not significant)", 820, TEXT, False),
        (f"\u2192 AI reviews are not detectably more dissimilar to each other than human reviews are to each other.", 800, GREEN, False),
        ('', 400, TEXT, False),
        (f"AI\u2013AI vs Human\u2013Human cosine: Wilcoxon p=0.016, q={v['r1_aiai_hh_q']}, \u03b4={v['r1_aiai_hh_d']} (large, significant)", 820, TEXT, False),
        (f"AI\u2013AI vs Human\u2013AI cosine: Wilcoxon p=0.00049, q={v['r1_aiai_hai_q']}, \u03b4={v['r1_aiai_hai_d']} (large, highly significant)", 820, TEXT, False),
        (f"\u2192 AI models converge on far more similar review language than humans do, and more than when reviewing the same human-written proposal.", 800, ORANGE, False),
        ('', 400, TEXT, False),
        ('Interpretation: AI reviews are not foreign to human expert assessments in textual content (R1 passes the basic validity bar).', 820, TEXT, False),
        ('However, the AI judge panel lacks the heterogeneity of human expert panels, which may compress the diversity of critical perspectives.', 820, TEXT, False),
        ('Left panel: HAI vs HH by AI model. Right panel: AIAI vs HH by model pair.', 760, GRAY, True),
    ]
    s += mixed_textbox(8, 500000, 3950000, 8400000, 1100000, items)
    return wrap_slide(s), [
        'quality_similarity_human_ai_by_model_proposal_level.png',
        'quality_similarity_ai_ai_by_model_pair_proposal_level.png',
    ]


def slide_21_r2_setup(v):
    """R2 Setup: Y1 vs Y2 comparability."""
    s = header_shapes(
        'R2 Setup: Verifying Human Baseline Comparability (Year 1 vs Year 2)',
        'Before pooling two human cohorts as "human-all," we test whether they are statistically equivalent'
    )
    items = [
        ('Why this matters:', 950, NAVY, True),
        ('Two human cohorts exist: Year 1 (n=12 proposals, evaluated by both human experts and AI) and Year 2 (n=11 proposals, AI-evaluated only).', 870, TEXT, False),
        ('If the cohorts differ substantially in quality, pooling them inflates within-group variance and biases comparisons to AI.', 870, TEXT, False),
        ('', 500, TEXT, False),
        ('Method: Mann\u2013Whitney U + Cliff\u2019s delta + BH-FDR, applied to all 8 scored dimensions.', 870, TEXT, False),
        ('', 500, TEXT, False),
        ('Results across 8 criteria (BH-FDR corrected):', 950, NAVY, True),
        (f"Overall score: Y1 mean={v['y1_overall']}, Y2 mean={v['y2_overall']}, q={v['y1y2_overall_q']} \u2014 NOT significant (\u03b4=-0.42 medium)", 870, GREEN, False),
        ('Relevance, Novelty, Rigor, Scope/Timeline, Synthesis, Open Science: all non-significant (q > 0.05)', 870, GREEN, False),
        (f"EXCEPTION \u2014 Data Identification: Y1={v['y1_dataid']}, Y2={v['y2_dataid']}, q={v['y1y2_dataid_q']}, \u03b4=-0.69 (large, significant)", 870, ORANGE, False),
        ('Y2 proposals include stronger data identification plans, possibly reflecting evolved grant writing norms.', 860, TEXT, False),
        ('', 500, TEXT, False),
        ('Conclusion: the two cohorts are equivalent on 7 of 8 dimensions. Pooling as "human-all" is justified for overall quality comparisons,', 870, TEXT, False),
        ('with the caveat that Data Identification scores in human-all reflect a year-of-submission effect.', 870, TEXT, False),
    ]
    s += mixed_textbox(6, 500000, 1200000, 8400000, 3800000, items)
    return wrap_slide(s), []


def slide_22_r2_baseline(v):
    """R2 Baseline: quality comparison."""
    s = header_shapes(
        'R2 Baseline: AI-Generated Proposals Score Higher Under AI Evaluation',
        'All evaluators pooled; 23 AI proposals vs 23 human proposals per group'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2600000)
    s += image_shape(7, 'rId3', 4650000, 1250000, 4000000, 2600000)
    items = [
        ('Method: proposal-level means (averaged across all AI evaluators), Mann\u2013Whitney + Cliff\u2019s \u03b4 + BH-FDR + bootstrap CI.', 820, TEXT, False),
        ('', 300, TEXT, False),
        (f"Human-all: mean={v['base_h_mean']} \u2502 Claude: {v['base_c_mean']} (q={v['base_c_q']}, ns) \u2502 Gemini: {v['base_g_mean']} (q={v['base_g_q']}***) \u2502 GPT-5.2: {v['base_t_mean']} (q={v['base_t_q']}***)", 820, TEXT, False),
        (f"Robust bootstrap (human\u2212AI): Claude +0.15 [95% CI: \u22120.11, +0.43] ns \u2502 Gemini \u22120.47 [\u22120.68, \u22120.23] sig \u2502 GPT \u22120.74 [\u22120.91, \u22120.57] sig", 820, TEXT, False),
        ('', 300, TEXT, False),
        ('Interpretation: Gemini and GPT proposals receive substantially higher scores than human proposals under pooled AI evaluation.', 820, TEXT, False),
        ('Claude proposals are statistically indistinguishable from human proposals (both on the 1\u20135 scale near 3.5).', 820, TEXT, False),
        ('IMPORTANT CAVEAT: these pooled scores include self-evaluations (AI evaluating its own proposals). R3 quantifies this bias.', 820, RED, True),
        ('Left: overall score distributions by author group. Right: radar chart of 7 criteria reveals pattern heterogeneity.', 780, GRAY, False),
    ]
    s += mixed_textbox(8, 500000, 3950000, 8400000, 1150000, items)
    return wrap_slide(s), [
        'quality_overall_boxplot_proposal_level.png',
        'quality_radar_criteria_proposal_level.png',
    ]


def slide_23_r2_criteria(v):
    """R2 criterion-level effects."""
    s = header_shapes(
        'R2 Criterion Decomposition: The AI Advantage Is Model- and Dimension-Specific',
        'Effect-size heatmap and dot plot across 7 rubric criteria'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4200000, 3000000)
    s += image_shape(7, 'rId3', 4800000, 1250000, 3800000, 3000000)
    items = [
        ('Key patterns (human-all vs each AI author group):', 900, NAVY, True),
        ('Relevance: all three AI models score near ceiling (5.0) vs human mean \u22483.75 \u2014 \u03b4 \u2248 \u22120.87 large for all models.', 830, TEXT, False),
        ('Rigor: humans score significantly HIGHER than Claude proposals (\u03b4=+0.48, large) but lower than GPT (\u03b4=\u22120.92, large).', 830, TEXT, False),
        ('Scope/Timeline: humans score higher than Claude (\u03b4=+0.58 large) but lower than GPT (\u03b4=\u22120.50 large).', 830, TEXT, False),
        ('Open Science: GPT proposals score far higher than humans (\u03b4=\u22120.92 large); Gemini also higher (\u03b4=\u22120.53 large).', 830, TEXT, False),
        ('Data Identification: GPT dramatically higher (\u03b4=\u22120.70 large); Gemini not significantly different from humans.', 830, TEXT, False),
        ('', 300, TEXT, False),
        ('Interpretation: "AI proposals score higher" is not uniform\u2014models and criteria show opposite patterns.', 830, TEXT, False),
        ('Claude underperforms humans on Rigor and Scope/Timeline while exceeding them on Relevance alone.', 830, TEXT, False),
        ('Heatmap: blue=human higher, red=AI higher; gray=non-significant. Dot plot: filled=significant, hollow=ns.', 780, GRAY, False),
    ]
    s += mixed_textbox(8, 500000, 4350000, 8400000, 750000, items)
    return wrap_slide(s), [
        'quality_effect_size_heatmap.png',
        'quality_effect_size_dotplot.png',
    ]


def slide_24_r3_leniency(v):
    """R3 Step 1: evaluator leniency differences."""
    s = header_shapes(
        'R3 Step 1: AI Evaluators Differ Substantially in Scoring Leniency',
        'Kruskal\u2013Wallis test across all 276 AI reviews; evaluator identity predicts score independently of proposal quality'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4600000, 2900000)
    items = [
        ('Why diagnose evaluator leniency first:', 900, NAVY, True),
        ('If one evaluator systematically assigns higher scores, comparing author groups across a pooled panel', 850, TEXT, False),
        ('confounds proposal quality with evaluator severity\u2014an evaluator effect, not a quality effect.', 850, TEXT, False),
        ('', 400, TEXT, False),
        ('Result:', 900, NAVY, True),
        (f"Kruskal\u2013Wallis H = 70.034, p = 6.2 \u00d7 10\u207b\u00b9\u2076 \u2014 evaluator identity is a highly significant predictor of score.", 850, TEXT, False),
        (f"Gemini evaluator: mean = {v['eval_g_mean']} (most lenient) \u2502 Claude: {v['eval_c_mean']} \u2502 GPT: {v['eval_t_mean']} (most strict)", 850, TEXT, False),
        ('The 0.71-point spread between Gemini and GPT evaluator means is larger than the human\u2013GPT author group difference.', 850, ORANGE, True),
        ('', 400, TEXT, False),
        ('Consequence:', 900, NAVY, True),
        ('Pooled-evaluator R2 results are a mixture of proposal quality and evaluator severity.', 850, TEXT, False),
        ('Before accepting the R2 baseline, we must check (a) self-preference bias (R3 Step 2) and', 850, TEXT, False),
        ('(b) whether findings replicate with evaluator configuration controlled (sensitivity analyses).', 850, TEXT, False),
    ]
    s += mixed_textbox(7, 5200000, 1250000, 3400000, 2900000, items)
    return wrap_slide(s), ['quality_overall_by_evaluator_clean.png']


def slide_25_r3_selfpref(v):
    """R3 Step 2: self-preference bias."""
    s = header_shapes(
        'R3 Step 2: Self-Preference Is Large in Magnitude and Model-Divergent',
        'GPT strongly self-inflates; Claude self-deprecates; Gemini is neutral\u2014all three effects are large or negligible'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2600000)
    s += image_shape(7, 'rId3', 4650000, 1250000, 3950000, 2600000)
    items = [
        ('Method: for each AI evaluator, compare scores assigned to its own proposals (self) vs other models\' proposals (other).', 820, TEXT, False),
        ('Mann\u2013Whitney U + Cliff\u2019s \u03b4 + BH-FDR, then criterion-level decomposition.', 820, TEXT, False),
        ('', 300, TEXT, False),
        (f"GPT evaluator \u2192 strong self-INFLATION: \u03b4=+0.987 large (q={v['sp_gpt_q']}); own mean={v['sp_gpt_self']} vs others mean={v['sp_gpt_other']}", 820, RED, True),
        (f"Claude evaluator \u2192 strong self-DEPRECATION: \u03b4=\u22120.581 large (q={v['sp_claude_q']}); own mean={v['sp_claude_self']} vs others mean={v['sp_claude_other']}", 820, ORANGE, True),
        (f"Gemini evaluator \u2192 NO significant self-preference: \u03b4=+0.128 negligible (q={v['sp_gem_q']})", 820, GREEN, True),
        ('', 300, TEXT, False),
        ('Criterion detail: GPT self-inflation concentrates in Rigor (+1.33), Data Identification (+0.93), Open Science (+0.80).', 820, TEXT, False),
        ('Claude self-deprecation concentrates in Rigor (\u22120.98), Scope/Timeline (\u22120.67); Relevance scores are floor-capped (all=5.0).', 820, TEXT, False),
        ('Implication: GPT baseline R2 advantage is at least partly a self-evaluation artifact, not objective quality difference.', 820, RED, False),
        ('Left: strip/box plot of self vs other by evaluator. Right: criterion-level heatmap of self\u2212other mean differences.', 760, GRAY, False),
    ]
    s += mixed_textbox(8, 500000, 3950000, 8400000, 1150000, items)
    return wrap_slide(s), [
        'self_pref_strip_overall.png',
        'self_pref_criterion_heatmap.png',
    ]


def slide_26_r3_regression(v):
    """R3 Step 3: regression control for proposal quality."""
    s = header_shapes(
        'R3 Step 3: Self-Preference Survives Proposal-Quality Controls',
        'Fixed-effects regression isolates self-preference net of proposal identity, evaluator severity, and author group'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4600000, 3000000)
    items = [
        ('Why a regression?', 900, NAVY, True),
        ('The self vs other comparison conflates two mechanisms: (1) genuine self-preference bias and (2) AI models may simply', 840, TEXT, False),
        ('produce higher-quality proposals that any evaluator would rate higher.', 840, TEXT, False),
        ('The regression removes the second explanation by adding proposal fixed effects.', 840, TEXT, False),
        ('', 400, TEXT, False),
        ('Model: score ~ is_self * criterion + evaluator + author + proposal_uid (HC3-robust SEs)', 840, TEXT, False),
        ('Proposal fixed effects absorb all between-proposal quality variation.', 840, TEXT, False),
        ('', 400, TEXT, False),
        ('Key findings:', 900, NAVY, True),
        ('Net self-preference (Data_ID reference criterion): +0.33 points persists after all controls.', 840, RED, True),
        ('Evaluator effects confirmed: Gemini +0.40 above Claude baseline; GPT \u22120.20 below.', 840, TEXT, False),
        ('GPT-authored proposals receive ~+1.25 more points than the baseline, net of evaluator severity.', 840, TEXT, False),
        ('', 400, TEXT, False),
        ('Conclusion: self-preference is a real evaluator bias, not a proxy for objective quality differences.', 840, ACCENT, True),
        ('Forest plot shows per-criterion self-preference coefficients (\u03b2 \u00b1 95% CI) and evaluator severity panel.', 800, GRAY, False),
    ]
    s += mixed_textbox(7, 5200000, 1250000, 3400000, 3000000, items)
    return wrap_slide(s), ['self_pref_regression_forest.png']


def slide_27_bridge(v):
    """Bridge: connecting R3 to R2 re-runs."""
    s = header_shapes(
        'R3 \u2192 R2: Why Bias-Controlled Reruns Are Necessary Before Drawing Conclusions',
        'Two sources of confound identified; two sensitivity analyses designed to address them'
    )
    items = [
        ('Summary of R3 findings and their implications for R2:', 950, NAVY, True),
        ('', 400, TEXT, False),
        ('Confound 1 \u2014 Evaluator self-preference:', 900, RED, True),
        ('GPT evaluator strongly inflates own proposals (+0.99\u03b4 large). Including GPT self-evaluations in the pooled baseline', 860, TEXT, False),
        ('artificially elevates GPT-authored proposal scores.', 860, TEXT, False),
        ('Fix: Sensitivity 1 removes self-evaluations for AI authors (cross-evaluator-only).', 860, GREEN, False),
        ('', 400, TEXT, False),
        ('Confound 2 \u2014 Evaluator leniency heterogeneity:', 900, ORANGE, True),
        ('Gemini evaluator is 0.71 points more lenient than GPT evaluator. Pooling evaluators weights', 860, TEXT, False),
        ('proposal group comparisons by the leniency of whichever evaluator happened to review more of one group.', 860, TEXT, False),
        ('Fix: Sensitivity 2 uses Gemini-only as a single, uniform evaluator for all proposals.', 860, GREEN, False),
        ('', 400, TEXT, False),
        ('Interpretation framework for the two reruns:', 950, NAVY, True),
        ('\u2022 Findings that hold under both controls are robust and interpretable.', 860, TEXT, False),
        ('\u2022 Findings that disappear or reverse under one control are evaluator-configuration sensitive.', 860, TEXT, False),
        ('\u2022 GPT\u2019s elevated scores must survive cross-evaluator removal to be credible.', 860, TEXT, False),
    ]
    s += mixed_textbox(6, 500000, 1200000, 8400000, 3800000, items)
    return wrap_slide(s), []


def slide_28_sensitivity1(v):
    """Sensitivity 1: cross-evaluator only."""
    s = header_shapes(
        'Sensitivity 1 \u2014 Cross-Evaluator Only: GPT Advantage Is Robust; Gemini Attenuates',
        'Removing self-evaluations: each AI proposal scored only by the 2 models that did not write it'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2600000)
    s += image_shape(7, 'rId3', 4650000, 1250000, 3950000, 2600000)
    items = [
        ('Design: for Claude-, Gemini-, and GPT-authored proposals, remove the 69 rows where evaluator==author (23 per model).', 820, TEXT, False),
        ('Human proposals are unaffected (all 3 AI models review them). This controls for self-preference without losing proposals.', 820, TEXT, False),
        ('', 300, TEXT, False),
        (f"Means (cross-eval only): Human {v['cx_h_mean']} \u2502 Claude {v['cx_c_mean']} (q={v['cx_c_q']}, ns) \u2502 Gemini {v['cx_g_mean']} (q={v['cx_g_q']}, marginal) \u2502 GPT {v['cx_t_mean']} (q={v['cx_t_q']}***)", 810, TEXT, False),
        (f"Robust bootstrap: Claude +0.17 [\u22120.11, +0.47] ns \u2502 Gemini \u22120.19 [\u22120.40, +0.02] ns \u2502 GPT \u22120.89 [\u22121.06, \u22120.73] sig", 810, TEXT, False),
        ('', 300, TEXT, False),
        ('Key changes from baseline:', 870, NAVY, True),
        ('Gemini advantage: baseline q=1.4\u00d710\u207b\u2075 (large sig) \u2192 q=0.070 (marginal, non-significant after self-removal)', 810, ORANGE, False),
        ('  \u2192 Gemini\u2019s elevated baseline score was substantially driven by self-evaluation inflation.', 800, ORANGE, False),
        ('GPT advantage: remains highly significant (q=1.5\u00d710\u207b\u2078, \u03b4=\u22121.00 large); robust to self-removal.', 810, GREEN, False),
        ('  \u2192 GPT proposals are rated higher even by models that did not write them\u2014a more credible quality signal.', 800, GREEN, False),
        ('Claude: unchanged (never significant), confirming Claude proposals are similar to human quality under fair evaluation.', 810, TEXT, False),
    ]
    s += mixed_textbox(8, 500000, 3950000, 8400000, 1150000, items)
    return wrap_slide(s), [
        'quality_overall_boxplot_proposal_level_cross_eval_only.png',
        'quality_effectsize_heatmap_cross_eval_only.png',
    ]


def slide_29_sensitivity2(v):
    """Sensitivity 2: Gemini-only evaluator."""
    s = header_shapes(
        'Sensitivity 2 \u2014 Gemini-Only Evaluator: Claude Falls Below Human Baseline',
        'Single-evaluator control: all proposals evaluated by Gemini, eliminating leniency-mix confound'
    )
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2600000)
    s += image_shape(7, 'rId3', 4650000, 1250000, 3950000, 2600000)
    items = [
        ('Design: restrict to Gemini-only reviews (92 rows). All 5 author groups evaluated by the same single evaluator.', 820, TEXT, False),
        ('This eliminates leniency-mix bias, at the cost of reduced power (n=23 per group, single evaluator).', 820, TEXT, False),
        ('Note: Gemini evaluates its own proposals (self-preference not removed here), making Gemini results still potentially inflated.', 820, ORANGE, False),
        ('', 300, TEXT, False),
        (f"Means (Gemini-only): Human {v['go_h_mean']} \u2502 Claude {v['go_c_mean']} (q={v['go_c_q']}***) \u2502 Gemini {v['go_g_mean']} (q={v['go_g_q']}***) \u2502 GPT {v['go_t_mean']} (q={v['go_t_q']}***)", 810, TEXT, False),
        (f"Robust bootstrap: Claude +0.65 [+0.27, +1.03] sig \u2502 Gemini \u22120.43 [\u22120.69, \u22120.14] sig \u2502 GPT \u22120.60 [\u22120.78, \u22120.43] sig", 810, TEXT, False),
        ('', 300, TEXT, False),
        ('Key changes from baseline:', 870, NAVY, True),
        (f"Claude reversal: baseline q=0.358 (ns, Claude \u2248 human) \u2192 Gemini-only q={v['go_c_q']} (humans score significantly HIGHER than Claude).", 810, ORANGE, False),
        ('  \u2192 Under a strict single evaluator, Claude proposals fall below human quality. The baseline equivalence was partly an artifact of mixed leniency.', 800, ORANGE, False),
        ('GPT: still elevated above humans, robust across evaluator configurations.', 810, GREEN, False),
        ('Gemini: elevated above humans (but Gemini evaluates own proposals\u2014self-preference likely inflating this result).', 810, ORANGE, False),
    ]
    s += mixed_textbox(8, 500000, 3950000, 8400000, 1150000, items)
    return wrap_slide(s), [
        'quality_overall_boxplot_proposal_level_gemini_only.png',
        'quality_effectsize_heatmap_gemini_only.png',
    ]


def slide_30_summary(v):
    """Final summary slide."""
    s = header_shapes(
        'Summary: Key Findings, Big Picture, and Next Steps',
        'Integrating R1\u2013R3 and the sensitivity analyses into actionable conclusions'
    )
    items = [
        ('What we found:', 950, NAVY, True),
        ('R1: AI reviews are not detectably dissimilar to human expert reviews in text content (proxy validity holds at the bar tested).', 850, TEXT, False),
        ('   However, AI reviewers converge far more tightly with each other than human experts do\u2014homogeneous critique is a limitation.', 840, GRAY, False),
        ('R2 (baseline): AI proposals\u2014especially GPT and Gemini\u2014score substantially higher than human proposals under pooled AI evaluation.', 850, TEXT, False),
        ('R3: Self-preference biases are large (GPT: +0.99\u03b4; Claude: \u22120.58\u03b4) and evaluator leniency varies by 0.71 points across models.', 850, TEXT, False),
        ('After controls: GPT advantage is robust (\u03b4=\u22121.00, sig across both sensitivity analyses). Gemini advantage disappears after self-removal.', 850, TEXT, False),
        ('Claude equivalence to humans flips to deficit under strict single-evaluator assessment.', 850, TEXT, False),
        ('', 400, TEXT, False),
        ('Big picture:', 950, NAVY, True),
        ('AI language models\u2014particularly GPT-5.2\u2014generate grant proposals that are consistently rated more highly than human proposals', 850, TEXT, False),
        ('even by other AI models that did not write them. This is not merely an artifact of self-preference.', 850, TEXT, False),
        ('The pattern varies by model: Claude does not outperform humans; Gemini only does so under conditions that inflate its own score.', 850, TEXT, False),
        ('AI evaluators can serve as a scalable screening proxy, but they systematically compress critique diversity compared to human panels.', 850, TEXT, False),
        ('', 400, TEXT, False),
        ('Limitations to address next:', 950, RED, True),
        ('1. Proxy validity beyond text similarity: ICC and rank-correlation with human panel are NaN\u2014harmonization must be fixed.', 840, TEXT, False),
        ('2. Small n for human expert reviews (n=12 proposals, 47 reviews)\u2014statistical power for human-AI calibration is limited.', 840, TEXT, False),
        ('3. Blinded external re-review: human raters have not scored AI proposals; the inverse direction (human rates AI) is untested.', 840, TEXT, False),
        ('4. GPT-5.2 near-zero variance in quality scores (SD=0.05) warrants investigation\u2014are prompts saturating the rubric?', 840, TEXT, False),
        ('', 400, TEXT, False),
        ('Recommended next steps: (a) repair proxy-validity harmonization; (b) recruit blinded human reviewers to rate AI proposals;', 840, ACCENT, True),
        ('(c) test whether AI\u2013AI homogeneity in reviews leads to worse ranking discrimination than human review panels.', 840, ACCENT, False),
    ]
    s += mixed_textbox(6, 500000, 1200000, 8400000, 3800000, items)
    return wrap_slide(s), []


# ── Statistics collection ─────────────────────────────────────────────────────

def collect_values():
    q = FIG_DIR
    sim      = read_csv(q / 'quality_similarity_mw_cliffs_overall.csv')
    summary  = read_csv(q / 'quality_summary_overall_by_author_group.csv')
    pw       = read_csv(q / 'quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv')
    boot     = read_csv(q / 'quality_robust_bootstrap_permutation_key_comparisons.csv')
    evals    = read_csv(q / 'quality_evaluator_overall_stats_clean.csv')
    sp       = read_csv(q / 'quality_self_preference_tests_overall.csv')
    cx_mw    = read_csv(q / 'quality_vs_ai_mw_cliffs_cross_eval_only.csv')
    cx_boot  = read_csv(q / 'quality_robust_bootstrap_permutation_cross_eval_only.csv')
    cx_sum   = read_csv(q / 'quality_summary_overall_by_author_group_cross_eval_only.csv')
    go_mw    = read_csv(q / 'quality_vs_ai_mw_cliffs_gemini_only.csv')
    go_boot  = read_csv(q / 'quality_robust_bootstrap_permutation_gemini_only.csv')
    go_sum   = read_csv(q / 'quality_summary_overall_by_author_group_gemini_only.csv')
    cohort   = read_csv(q / 'quality_human_cohort_mw_cliffs_cross_eval_only.csv')

    def grp(rows, g):
        return find_row(rows, group=g)

    r1_hai_hh   = find_row(sim, metric='cosine_similarity', group1='human-ai',  group2='human-human')
    r1_aiai_hh  = find_row(sim, metric='cosine_similarity', group1='ai-ai',     group2='human-human')
    r1_aiai_hai = find_row(sim, metric='cosine_similarity', group1='ai-ai',     group2='human-ai')

    b_h = find_row(summary, group='human-all')
    b_c = find_row(pw,  metric='overall_score', group1='human-all', group2='claude-opus-4-5')
    b_g = find_row(pw,  metric='overall_score', group1='human-all', group2='gemini-3-pro-preview')
    b_t = find_row(pw,  metric='overall_score', group1='human-all', group2='gpt-5.2')

    ec = find_row(evals, evaluator='claude-opus-4-5')
    eg = find_row(evals, evaluator='gemini-3-pro-preview')
    et = find_row(evals, evaluator='gpt-5.2')

    spc = find_row(sp, evaluator='claude-opus-4-5')
    spg = find_row(sp, evaluator='gemini-3-pro-preview')
    spt = find_row(sp, evaluator='gpt-5.2')

    cx_c = find_row(cx_mw, metric='overall_score', group2='claude-opus-4-5')
    cx_g = find_row(cx_mw, metric='overall_score', group2='gemini-3-pro-preview')
    cx_t = find_row(cx_mw, metric='overall_score', group2='gpt-5.2')
    cx_h_row = find_row(cx_sum, group='human-all')
    cx_c_sum = find_row(cx_sum, group='claude-opus-4-5')
    cx_g_sum = find_row(cx_sum, group='gemini-3-pro-preview')
    cx_t_sum = find_row(cx_sum, group='gpt-5.2')

    go_c = find_row(go_mw, metric='overall_score', group2='claude-opus-4-5')
    go_g = find_row(go_mw, metric='overall_score', group2='gemini-3-pro-preview')
    go_t = find_row(go_mw, metric='overall_score', group2='gpt-5.2')
    go_h_row = find_row(go_sum, group='human-all')
    go_c_sum = find_row(go_sum, group='claude-opus-4-5')
    go_g_sum = find_row(go_sum, group='gemini-3-pro-preview')
    go_t_sum = find_row(go_sum, group='gpt-5.2')

    y1y2_overall = find_row(cohort, metric='overall_score')
    y1y2_dataid  = find_row(cohort, metric='Data_Identification')
    y1_sum = find_row(summary, group='human-y1')
    y2_sum = find_row(summary, group='human-y2')

    def fmt_q(r, key='q_value', d=3):
        try:
            v = float(r.get(key, 'nan'))
            if v < 0.001: return '<0.001'
            return f'{v:.{d}f}'
        except: return 'NA'

    return {
        # R1
        'r1_hai_hh_q':   fmt_q(r1_hai_hh),
        'r1_hai_hh_d':   fn(r1_hai_hh.get('cliffs_delta',''), 2),
        'r1_aiai_hh_q':  fmt_q(r1_aiai_hh),
        'r1_aiai_hh_d':  fn(r1_aiai_hh.get('cliffs_delta',''), 2),
        'r1_aiai_hai_q': fmt_q(r1_aiai_hai),
        'r1_aiai_hai_d': fn(r1_aiai_hai.get('cliffs_delta',''), 2),

        # Y1 vs Y2
        'y1_overall':    fn(y1_sum.get('overall_mean',''), 2),
        'y2_overall':    fn(y2_sum.get('overall_mean',''), 2),
        'y1y2_overall_q': fmt_q(y1y2_overall),
        'y1_dataid':     fn(find_row(cohort, metric='Data_Identification').get('mean_group1',''), 2),
        'y2_dataid':     fn(find_row(cohort, metric='Data_Identification').get('mean_group2',''), 2),
        'y1y2_dataid_q': fmt_q(y1y2_dataid),

        # R2 baseline
        'base_h_mean':  fn(b_h.get('overall_mean',''), 2),
        'base_c_mean':  fn(b_c.get('mean_group2',''), 2),
        'base_c_q':     fmt_q(b_c),
        'base_g_mean':  fn(b_g.get('mean_group2',''), 2),
        'base_g_q':     fmt_q(b_g),
        'base_t_mean':  fn(b_t.get('mean_group2',''), 2),
        'base_t_q':     fmt_q(b_t),

        # R3 evaluator leniency
        'eval_g_mean':  fn(eg.get('mean',''), 2),
        'eval_c_mean':  fn(ec.get('mean',''), 2),
        'eval_t_mean':  fn(et.get('mean',''), 2),

        # R3 self-preference
        'sp_claude_q':   fmt_q(spc),
        'sp_claude_self': fn(spc.get('mean_self',''), 2),
        'sp_claude_other': fn(spc.get('mean_other',''), 2),
        'sp_gem_q':      fmt_q(spg),
        'sp_gpt_q':      fmt_q(spt),
        'sp_gpt_self':   fn(spt.get('mean_self',''), 2),
        'sp_gpt_other':  fn(spt.get('mean_other',''), 2),

        # Cross-eval only
        'cx_h_mean':  fn(cx_h_row.get('overall_mean',''), 2),
        'cx_c_mean':  fn(cx_c_sum.get('overall_mean',''), 2),
        'cx_c_q':     fmt_q(cx_c),
        'cx_g_mean':  fn(cx_g_sum.get('overall_mean',''), 2),
        'cx_g_q':     fmt_q(cx_g),
        'cx_t_mean':  fn(cx_t_sum.get('overall_mean',''), 2),
        'cx_t_q':     fmt_q(cx_t),

        # Gemini-only
        'go_h_mean':  fn(go_h_row.get('overall_mean',''), 2),
        'go_c_mean':  fn(go_c_sum.get('overall_mean',''), 2),
        'go_c_q':     fmt_q(go_c),
        'go_g_mean':  fn(go_g_sum.get('overall_mean',''), 2),
        'go_g_q':     fmt_q(go_g),
        'go_t_mean':  fn(go_t_sum.get('overall_mean',''), 2),
        'go_t_q':     fmt_q(go_t),
    }


# ── Main PPTX manipulation ────────────────────────────────────────────────────

SLIDES_TO_DELETE = [18, 19]

SLIDE_BUILDERS = [
    slide_18_overview,
    slide_19_r1_method,
    slide_20_r1_results,
    slide_21_r2_setup,
    slide_22_r2_baseline,
    slide_23_r2_criteria,
    slide_24_r3_leniency,
    slide_25_r3_selfpref,
    slide_26_r3_regression,
    slide_27_bridge,
    slide_28_sensitivity1,
    slide_29_sensitivity2,
    slide_30_summary,
]


def modify_pptx(pptx_path: Path):
    vals = collect_values()

    with tempfile.TemporaryDirectory(prefix='pptx_v2_') as td:
        root = Path(td)
        with zipfile.ZipFile(pptx_path, 'r') as zf:
            zf.extractall(root)

        slides_dir = root / 'ppt' / 'slides'
        rels_dir   = slides_dir / '_rels'
        media_dir  = root / 'ppt' / 'media'
        pres_path  = root / 'ppt' / 'presentation.xml'
        pres_rels_path = root / 'ppt' / '_rels' / 'presentation.xml.rels'
        ct_path    = root / '[Content_Types].xml'

        pres_tree  = ET.parse(pres_path)
        pres_root  = pres_tree.getroot()
        pres_ns    = {'p': P_NS, 'r': R_NS}
        sldIdLst   = pres_root.find('p:sldIdLst', pres_ns)

        pres_rels_tree = ET.parse(pres_rels_path)
        pres_rels_root = pres_rels_tree.getroot()

        ct_tree = ET.parse(ct_path)
        ct_root = ct_tree.getroot()

        # ── Step 1: find rIds for slides to delete ───────────────────────────
        # Build map: Target basename -> rId
        target_to_rid = {}
        for rel in pres_rels_root.findall(f'{{{PR_NS}}}Relationship'):
            tgt = rel.attrib.get('Target', '')
            rid = rel.attrib.get('Id', '')
            # tgt is like "slides/slide18.xml"
            target_to_rid[tgt] = rid

        delete_rids = set()
        for n in SLIDES_TO_DELETE:
            tgt = f'slides/slide{n}.xml'
            if tgt in target_to_rid:
                delete_rids.add(target_to_rid[tgt])

        # ── Step 2: remove from sldIdLst ────────────────────────────────────
        for sldId in list(sldIdLst.findall('p:sldId', pres_ns)):
            rid = sldId.attrib.get(f'{{{R_NS}}}id', '')
            if rid in delete_rids:
                sldIdLst.remove(sldId)

        # ── Step 3: remove from presentation.xml.rels ───────────────────────
        for rel in list(pres_rels_root.findall(f'{{{PR_NS}}}Relationship')):
            if rel.attrib.get('Id', '') in delete_rids:
                pres_rels_root.remove(rel)

        # ── Step 4: remove from [Content_Types].xml ─────────────────────────
        for n in SLIDES_TO_DELETE:
            part_name = f'/ppt/slides/slide{n}.xml'
            for ov in list(ct_root.findall(f'{{{CT_NS}}}Override')):
                if ov.attrib.get('PartName') == part_name:
                    ct_root.remove(ov)

        # ── Step 5: delete slide files ───────────────────────────────────────
        for n in SLIDES_TO_DELETE:
            slide_file = slides_dir / f'slide{n}.xml'
            rels_file  = rels_dir   / f'slide{n}.xml.rels'
            if slide_file.exists(): slide_file.unlink()
            if rels_file.exists():  rels_file.unlink()

        # ── Step 6: determine new slide numbers and IDs ──────────────────────
        existing_nums = sorted(
            int(m.group(1))
            for p in slides_dir.glob('slide*.xml')
            for m in [re.match(r'slide(\d+)\.xml$', p.name)] if m
        )
        max_slide = max(existing_nums) if existing_nums else 0

        max_sld_id = max(
            int(x.attrib['id'])
            for x in sldIdLst.findall('p:sldId', pres_ns)
        )

        rel_nums = [
            int(m.group(1))
            for rel in pres_rels_root.findall(f'{{{PR_NS}}}Relationship')
            for m in [re.match(r'rId(\d+)$', rel.attrib.get('Id', ''))] if m
        ]
        max_rel_num = max(rel_nums) if rel_nums else 1

        # ── Step 7: add new slides ───────────────────────────────────────────
        new_slide_num = max_slide
        new_sld_id    = max_sld_id
        new_rel_num   = max_rel_num

        for builder in SLIDE_BUILDERS:
            slide_xml, img_basenames = builder(vals)
            new_slide_num += 1
            new_sld_id    += 1
            new_rel_num   += 1
            pres_rid = f'rId{new_rel_num}'

            # copy images
            copied_names = []
            for img in img_basenames:
                src = FIG_DIR / img
                if not src.exists():
                    raise FileNotFoundError(f'Missing figure: {src}')
                dst_name = f'q2_{new_slide_num}_{img}'
                shutil.copy2(src, media_dir / dst_name)
                copied_names.append(dst_name)

            # write slide XML
            (slides_dir / f'slide{new_slide_num}.xml').write_text(slide_xml, encoding='utf-8')

            # write slide rels
            (rels_dir / f'slide{new_slide_num}.xml.rels').write_text(
                rels_xml(copied_names), encoding='utf-8'
            )

            # register in presentation.xml
            ET.SubElement(sldIdLst, f'{{{P_NS}}}sldId', {
                'id': str(new_sld_id),
                f'{{{R_NS}}}id': pres_rid,
            })

            # register in presentation.xml.rels
            ET.SubElement(pres_rels_root, f'{{{PR_NS}}}Relationship', {
                'Id': pres_rid,
                'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide',
                'Target': f'slides/slide{new_slide_num}.xml',
            })

            # register in [Content_Types].xml
            part = f'/ppt/slides/slide{new_slide_num}.xml'
            if not any(x.attrib.get('PartName') == part
                       for x in ct_root.findall(f'{{{CT_NS}}}Override')):
                ET.SubElement(ct_root, f'{{{CT_NS}}}Override', {
                    'PartName': part,
                    'ContentType': (
                        'application/vnd.openxmlformats-officedocument'
                        '.presentationml.slide+xml'
                    ),
                })

        # ── Step 8: write updated XML files ─────────────────────────────────
        pres_tree.write(pres_path,       encoding='utf-8', xml_declaration=True)
        pres_rels_tree.write(pres_rels_path, encoding='utf-8', xml_declaration=True)
        ct_tree.write(ct_path,           encoding='utf-8', xml_declaration=True)

        # ── Step 9: backup + repack ──────────────────────────────────────────
        backup = pptx_path.with_suffix('.pptx.bak')
        if not backup.exists():
            shutil.copy2(pptx_path, backup)

        tmp_out = pptx_path.with_suffix('.pptx.tmp')
        if tmp_out.exists():
            tmp_out.unlink()
        with zipfile.ZipFile(tmp_out, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in root.rglob('*'):
                if f.is_file():
                    zf.write(f, f.relative_to(root).as_posix())

        tmp_out.replace(pptx_path)
        return len(SLIDE_BUILDERS), backup


def main():
    os.chdir(Path(__file__).parent.parent)
    n, bak = modify_pptx(PPTX_PATH)
    print(f'Added {n} slides (replaced slides 18-19) in {PPTX_PATH}')
    print(f'Backup: {bak}')


if __name__ == '__main__':
    main()
