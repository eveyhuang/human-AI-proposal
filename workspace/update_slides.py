#!/usr/bin/env python3
"""Update slides 2, 3 and insert new Novelty definition slide.

1. Slide 2: Broaden research question, add analysis overview
2. Slide 3: Add metric definitions (diversity vs novelty vs thematic)
3. New slide 18: "Defining Novelty & Literature Corpus" inserted before novelty results
"""

import os, shutil

BASE = "/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison"
UNPACKED = os.path.join(BASE, "workspace", "pptx_unpacked")
SLIDES_DIR = os.path.join(UNPACKED, "ppt", "slides")
RELS_DIR = os.path.join(SLIDES_DIR, "_rels")
MEDIA_DIR = os.path.join(UNPACKED, "ppt", "media")
FIGURES_DIR = os.path.join(BASE, "results", "figures")

# Design constants (same as previous script)
NAVY = "1B2A4A"; RED = "E8505B"; BLUE = "2E86AB"; WHITE = "FFFFFF"
BODY_DARK = "2C3E50"; BODY_GRAY = "5D6D7E"; BG_BLUE = "F7F9FC"
BG_PINK = "FDF8F8"; BG_LIGHT = "F0F4F8"; BG_GRAY = "F5F5F5"
PURPLE = "8E44AD"; ORANGE = "E67E22"; GREEN = "27AE60"; TEAL = "16A085"
FB = '''<a:latin typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="0"/>
                <a:ea typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="-122"/>
                <a:cs typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="-120"/>'''


# ─── Reusable shape builders (same helpers as before) ──────────────
def slide_hdr(title):
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Text 0"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="9144000" cy="650677"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Text 1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="507950" y="177701"/><a:ext cx="8290661" cy="295275"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
        <p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0" algn="l"><a:buNone/></a:pPr>
            <a:r><a:rPr lang="en-US" sz="2000" b="1" dirty="0"><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill>{FB}</a:rPr><a:t>{title}</a:t></a:r>
            <a:endParaRPr lang="en-US" sz="2000" dirty="0"/></a:p></p:txBody>
      </p:sp>'''

def tb(id, x, y, cx, cy, text, sz=950, color=BODY_DARK, bold=False, lsp=1285):
    b = ' b="1"' if bold else ''
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id}" name="Text {id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
        <p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPts val="{lsp}"/></a:lnSpc>
            <a:spcAft><a:spcPts val="400"/></a:spcAft><a:buNone/></a:pPr>
            <a:r><a:rPr lang="en-US" sz="{sz}"{b} dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{FB}</a:rPr><a:t>{text}</a:t></a:r>
            <a:endParaRPr lang="en-US" sz="{sz}" dirty="0"/></a:p></p:txBody>
      </p:sp>'''

def rrect(id, x, y, cx, cy, color=BG_BLUE, adj=3645):
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id}" name="Text {id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>
          <a:solidFill><a:srgbClr val="{color}"/></a:solidFill></p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
      </p:sp>'''

def hline(id, x, y, cx, color=BLUE):
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id}" name="Shape {id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="0"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>
          <a:ln w="38100"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:prstDash val="solid"/></a:ln></p:spPr>
      </p:sp>'''

def vline(id, x, y, cy, color=BLUE):
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id}" name="Shape {id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="0" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>
          <a:ln w="38100"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:prstDash val="solid"/></a:ln></p:spPr>
      </p:sp>'''

def accent(id, x, y, color=RED, cx=507950):
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id}" name="Text {id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="25301"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p></p:txBody>
      </p:sp>'''

def img(id, rid, x, y, cx, cy):
    return f'''<p:pic>
        <p:nvPicPr><p:cNvPr id="{id}" name="Picture {id}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
        <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
        <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:pic>'''

def wrap(shapes):
    return f'''<?xml version="1.0" encoding="ascii"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {shapes}
    </p:spTree>
  </p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


# ═══════════════════════════════════════════════════════════════════
# 1. UPDATE SLIDE 2: Study Design
# ═══════════════════════════════════════════════════════════════════
def update_slide2():
    """Edit slide2.xml in-place: broaden research question, update approach text."""
    path = os.path.join(SLIDES_DIR, "slide2.xml")
    with open(path, "r") as f:
        xml = f.read()

    # Update research question
    xml = xml.replace(
        "Do AI-generated research proposals exhibit less diversity than human-written proposals when responding to the same funding call?",
        "How do AI-generated research proposals compare to human-written proposals in diversity, novelty, and thematic content when responding to the same funding call?"
    )

    # Update approach description
    xml = xml.replace(
        "We compare proposals written by humans and three frontier AI models for the NSF NCEMS call on emergence in molecular and cellular biosciences.",
        "We compare 23 human proposals and 69 AI proposals (from three frontier models) for the NSF NCEMS call, using embedding-based analyses across three dimensions: internal diversity, novelty relative to published literature, and thematic/cluster composition."
    )

    # Update the last approach line (about diversity measurement)
    xml = xml.replace(
        "Diversity is measured via three complementary embedding-space analyses with non-parametric statistical tests.",
        "Analysis spans three parts: (1) within-group diversity via pairwise, centroid, and nearest-neighbor metrics; "
        "(2) novelty via distance to a PubMed literature corpus; (3) thematic separation via topic modeling and cluster analysis."
    )

    # Update the approach context line
    xml = xml.replace(
        "All models received the same funding call, background literature, and evaluation criteria that the human applicants had.",
        "All models received the same funding call and evaluation criteria. All analyses use BioLinkBERT embeddings with non-parametric statistical tests."
    )

    with open(path, "w") as f:
        f.write(xml)
    print("  Updated slide2.xml")


# ═══════════════════════════════════════════════════════════════════
# 2. REBUILD SLIDE 3: Methodology (expanded with metric definitions)
# ═══════════════════════════════════════════════════════════════════
def rebuild_slide3():
    s = slide_hdr("Methodology")

    # ── LEFT COLUMN: Embedding Pipeline (compact) ──
    left_x = 507950
    s += tb(4, left_x, 853827, 3951021, 200025,
        "Embedding Pipeline", sz=1300, color=NAVY, bold=True)
    s += accent(5, left_x, 1100000, RED)

    # Pipeline steps - compact
    s += rrect(6, left_x, 1180000, 3951021, 340000, BG_LIGHT, 3000)
    s += vline(7, left_x + 19050, 1180000, 340000, BLUE)
    s += tb(8, left_x + 190500, 1200000, 3700000, 130000,
        "BioLinkBERT-large", sz=1050, color=NAVY, bold=True, lsp=1400)
    s += tb(9, left_x + 190500, 1340000, 3700000, 150000,
        "340M-param biomedical model pretrained on PubMed with citation links. Encodes each proposal as a 1024-dim vector (400-word overlapping chunks, averaged).",
        sz=800, color=BODY_GRAY, lsp=1050)

    s += rrect(10, left_x, 1580000, 3951021, 240000, BG_LIGHT, 3000)
    s += vline(11, left_x + 19050, 1580000, 240000, BLUE)
    s += tb(12, left_x + 190500, 1600000, 3700000, 130000,
        "Cosine distance in 1024-dim space for all metrics. Mann-Whitney U, Cliff&#8217;s delta, and permutation tests (10K iterations) for all comparisons.",
        sz=800, color=BODY_GRAY, lsp=1050)

    # ── LEFT COLUMN: Key Definitions ──
    s += tb(13, left_x, 1920000, 3951021, 200025,
        "Key Metric Definitions", sz=1300, color=NAVY, bold=True)
    s += accent(14, left_x, 2170000, BLUE, 507950)

    # Definition: Diversity
    s += rrect(15, left_x, 2260000, 3951021, 580000, BG_PINK, 3000)
    s += hline(16, left_x, 2279050, 3951021, RED)
    s += tb(17, left_x + 152400, 2310000, 3700000, 150000,
        "Diversity (within-group)", sz=1050, color=RED, bold=True, lsp=1400)
    s += tb(18, left_x + 152400, 2470000, 3700000, 340000,
        "How different are proposals from each other within the same group? "
        "Measured by cosine distances between proposal embeddings. "
        "Three complementary lenses: pairwise distances (all pairs), centroid dispersion (distance to group center), "
        "and nearest-neighbor analysis (closest proposal in the combined space). "
        "Answers: &#8220;Is this group producing varied ideas?&#8221;",
        sz=800, color=BODY_DARK, lsp=1050)

    # Definition: Novelty
    s += rrect(19, left_x, 2920000, 3951021, 580000, BG_BLUE, 3000)
    s += hline(20, left_x, 2939050, 3951021, BLUE)
    s += tb(21, left_x + 152400, 2970000, 3700000, 150000,
        "Novelty (vs. published literature)", sz=1050, color=BLUE, bold=True, lsp=1400)
    s += tb(22, left_x + 152400, 3130000, 3700000, 340000,
        "How far are proposals from what already exists in the scientific literature? "
        "Measured as mean cosine distance from each proposal to its 10 nearest neighbors in a corpus of 350 PubMed articles. "
        "Higher = more novel. Crucially different from diversity: a group can be internally diverse but still close to published work, "
        "or internally homogeneous but exploring genuinely new territory.",
        sz=800, color=BODY_DARK, lsp=1050)

    # Definition: Thematic
    s += rrect(23, left_x, 3580000, 3951021, 480000, BG_GRAY, 3000)
    s += hline(24, left_x, 3599050, 3951021, TEAL)
    s += tb(25, left_x + 152400, 3630000, 3700000, 150000,
        "Thematic Separation (topic &#38; cluster)", sz=1050, color=TEAL, bold=True, lsp=1400)
    s += tb(26, left_x + 152400, 3790000, 3700000, 240000,
        "Do human and AI proposals occupy the same conceptual regions? LDA topic modeling identifies latent themes; "
        "Gaussian Mixture Model clustering groups proposals by embedding similarity. Tests whether sources are segregated or intermingled.",
        sz=800, color=BODY_DARK, lsp=1050)

    # ── RIGHT COLUMN: Analysis Overview ──
    right_x = 4762500
    s += tb(27, right_x, 853827, 3951021, 200025,
        "Analysis Overview", sz=1300, color=NAVY, bold=True)
    s += accent(28, right_x, 1100000, BLUE, 507950)

    # Part I
    s += rrect(29, right_x, 1180000, 3873550, 720000, BG_LIGHT, 3000)
    s += vline(30, right_x + 19050, 1180000, 720000, RED)
    s += tb(31, right_x + 190500, 1210000, 3600000, 150000,
        "Part I: Diversity Analysis (Slides 4&#8211;7)", sz=1000, color=NAVY, bold=True, lsp=1400)
    s += tb(32, right_x + 190500, 1380000, 3600000, 460000,
        "&#8226; Pairwise distances &#8212; all n(n&#8722;1)/2 pairs within each group\n"
        "&#8226; Centroid dispersion &#8212; distance from each proposal to group mean\n"
        "&#8226; Nearest-neighbor &#8212; closest proposal in combined 92-proposal space\n"
        "&#8226; Embedding visualization &#8212; UMAP 2D projection",
        sz=800, color=BODY_DARK, lsp=1050)

    # Part II
    s += rrect(33, right_x, 1980000, 3873550, 650000, BG_LIGHT, 3000)
    s += vline(34, right_x + 19050, 1980000, 650000, BLUE)
    s += tb(35, right_x + 190500, 2010000, 3600000, 150000,
        "Part II: Novelty Analysis (Slides 8&#8211;9)", sz=1000, color=NAVY, bold=True, lsp=1400)
    s += tb(36, right_x + 190500, 2180000, 3600000, 400000,
        "&#8226; Literature corpus: 350 PubMed articles from 7 search queries\n"
        "&#8226; Novelty score: mean distance to k=10 nearest neighbors in literature\n"
        "&#8226; Compares title+abstract embeddings (fair comparison with abstracts)\n"
        "&#8226; Statistical tests: same non-parametric framework as Part I",
        sz=800, color=BODY_DARK, lsp=1050)

    # Part III
    s += rrect(37, right_x, 2710000, 3873550, 680000, BG_LIGHT, 3000)
    s += vline(38, right_x + 19050, 2710000, 680000, TEAL)
    s += tb(39, right_x + 190500, 2740000, 3600000, 150000,
        "Part III: Thematic &#38; Cluster Analysis (Slides 10&#8211;11)", sz=1000, color=NAVY, bold=True, lsp=1400)
    s += tb(40, right_x + 190500, 2910000, 3600000, 430000,
        "&#8226; LDA topic modeling (k=5, strong priors, stability-validated)\n"
        "&#8226; Topic distribution: Fisher&#8217;s exact tests with FDR correction\n"
        "&#8226; GMM clustering (k=3, selected by BIC)\n"
        "&#8226; Segregation metrics: NMI, ARI, between/within distance ratio",
        sz=800, color=BODY_DARK, lsp=1050)

    # Bottom: key distinction callout
    s += rrect(41, right_x, 3490000, 3873550, 580000, NAVY, 3000)
    s += tb(42, right_x + 152400, 3530000, 3600000, 150000,
        "Why three separate analyses?", sz=1050, color=WHITE, bold=True, lsp=1400)
    s += tb(43, right_x + 152400, 3700000, 3600000, 320000,
        "Diversity asks: &#8220;Are the ideas varied?&#8221; Novelty asks: &#8220;Are they new relative to the field?&#8221; "
        "Thematic analysis asks: &#8220;Are they about the same things?&#8221; A model can score high on one and low on another &#8212; "
        "these dimensions are complementary, not redundant.",
        sz=850, color="B0C4DE", lsp=1100)

    return s


# ═══════════════════════════════════════════════════════════════════
# 3. NEW SLIDE 18: Defining Novelty & Literature Corpus
# ═══════════════════════════════════════════════════════════════════
def build_novelty_definition_slide():
    s = slide_hdr("Defining Novelty &#38; the Literature Corpus")

    # ── Left column: definitions ──
    left_x = 507950

    s += tb(4, left_x, 853827, 3951021, 200025,
        "How is novelty measured?", sz=1300, color=NAVY, bold=True)
    s += accent(5, left_x, 1100000, RED)

    # What novelty measures
    s += rrect(6, left_x, 1180000, 3951021, 700000, BG_BLUE, 3000)
    s += hline(7, left_x, 1199050, 3951021, BLUE)
    s += tb(8, left_x + 152400, 1240000, 3700000, 620000,
        "For each proposal, we find its k=10 nearest neighbors in a reference corpus of published PubMed articles "
        "and compute the mean cosine distance. A higher score means the proposal is further from anything "
        "previously published &#8212; it explores territory that the existing literature does not cover. "
        "We embed only the title + abstract of each proposal (not the full text) to ensure a fair comparison "
        "with the PubMed abstracts.",
        sz=900, color=BODY_DARK, lsp=1150)

    # How novelty differs from diversity
    s += tb(9, left_x, 1980000, 3951021, 200025,
        "How does novelty differ from diversity?", sz=1200, color=NAVY, bold=True)
    s += accent(10, left_x, 2230000, TEAL, 507950)

    s += rrect(11, left_x, 2310000, 1900000, 630000, BG_PINK, 3000)
    s += hline(12, left_x, 2329050, 1900000, RED)
    s += tb(13, left_x + 114300, 2370000, 1700000, 150000,
        "Diversity", sz=1050, color=RED, bold=True, lsp=1400)
    s += tb(14, left_x + 114300, 2520000, 1700000, 380000,
        "Compares proposals to each other within a group. "
        "A diverse group produces varied ideas, but those ideas may all be well-known in the literature. "
        "Reference: internal (proposals vs. proposals).",
        sz=800, color=BODY_DARK, lsp=1050)

    s += rrect(15, left_x + 2050000, 2310000, 1900000, 630000, BG_BLUE, 3000)
    s += hline(16, left_x + 2050000, 2329050, 1900000, BLUE)
    s += tb(17, left_x + 2050000 + 114300, 2370000, 1700000, 150000,
        "Novelty", sz=1050, color=BLUE, bold=True, lsp=1400)
    s += tb(18, left_x + 2050000 + 114300, 2520000, 1700000, 380000,
        "Compares proposals to published literature. "
        "A novel proposal explores territory that no published paper covers, regardless of how similar it is to other proposals. "
        "Reference: external (proposals vs. PubMed).",
        sz=800, color=BODY_DARK, lsp=1050)

    # Key implication
    s += rrect(19, left_x, 3040000, 3951021, 350000, NAVY, 3000)
    s += tb(20, left_x + 152400, 3080000, 3700000, 280000,
        "Implication: A model can be highly diverse (varied output) but low novelty (ideas the field already knows), "
        "or low diversity (repetitive) but high novelty (repetitively novel). These are independent dimensions.",
        sz=850, color=WHITE, bold=True, lsp=1100)

    # ── Right column: Literature corpus stats + image ──
    right_x = 4762500

    s += tb(21, right_x, 853827, 3873550, 200025,
        "Reference Literature Corpus", sz=1300, color=NAVY, bold=True)
    s += accent(22, right_x, 1100000, BLUE, 507950)

    # Image
    s += img(23, "rId2", right_x, 1180000, 3873550, 2000000)

    # Stats below image
    s += rrect(24, right_x, 3280000, 3873550, 1120000, BG_LIGHT, 3000)
    s += vline(25, right_x + 19050, 3280000, 1120000, BLUE)
    s += tb(26, right_x + 190500, 3320000, 3600000, 150000,
        "350 PubMed articles from 7 targeted queries", sz=1000, color=NAVY, bold=True, lsp=1400)
    s += tb(27, right_x + 190500, 3490000, 3600000, 860000,
        "&#8226; Emergent properties in molecular/cellular biology (59 articles)\n"
        "&#8226; Mesoscale biology &#38; biomolecular organization (49)\n"
        "&#8226; Biomolecular condensates &#38; phase separation (49)\n"
        "&#8226; Multi-omics data integration (50)\n"
        "&#8226; AI/ML in molecular &#38; cellular biology (59)\n"
        "&#8226; Systems biology &#38; network analysis (44)\n"
        "&#8226; Protein self-assembly &#38; supramolecular organization (40)\n"
        "Mean abstract length: 1,351 characters. Embedded with BioLinkBERT using same pipeline as proposals.",
        sz=780, color=BODY_DARK, lsp=1000)

    return s


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════
def main():
    # 1. Update slide 2
    update_slide2()

    # 2. Rebuild slide 3
    path3 = os.path.join(SLIDES_DIR, "slide3.xml")
    with open(path3, "w", encoding="ascii", errors="xmlcharrefreplace") as f:
        f.write(wrap(rebuild_slide3()))
    print("  Rebuilt slide3.xml")

    # 3. Copy literature_corpus_overview.png
    src = os.path.join(FIGURES_DIR, "literature_corpus_overview.png")
    dst = os.path.join(MEDIA_DIR, "image8.png")
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print("  Copied literature_corpus_overview.png -> image8.png")
    else:
        print(f"  WARNING: {src} not found!")

    # 4. Write new slide 18
    path18 = os.path.join(SLIDES_DIR, "slide18.xml")
    with open(path18, "w", encoding="ascii", errors="xmlcharrefreplace") as f:
        f.write(wrap(build_novelty_definition_slide()))
    print("  Wrote slide18.xml")

    # 5. Write rels for slide 18
    rels18 = '''<?xml version="1.0" encoding="ascii"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image8.png"/>
</Relationships>'''
    with open(os.path.join(RELS_DIR, "slide18.xml.rels"), "w") as f:
        f.write(rels18)
    print("  Wrote _rels/slide18.xml.rels")

    # 6. Update presentation.xml - insert slide18 between slide7 and slide11
    pres_path = os.path.join(UNPACKED, "ppt", "presentation.xml")
    pres = '''<?xml version="1.0" encoding="ascii"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" autoCompressPictures="0">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:notesMasterIdLst><p:notesMasterId r:id="rId4"/></p:notesMasterIdLst>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId3"/>
    <p:sldId id="257" r:id="rId5"/>
    <p:sldId id="258" r:id="rId6"/>
    <p:sldId id="259" r:id="rId7"/>
    <p:sldId id="260" r:id="rId8"/>
    <p:sldId id="261" r:id="rId9"/>
    <p:sldId id="262" r:id="rId10"/>
    <p:sldId id="273" r:id="rId24"/>
    <p:sldId id="266" r:id="rId17"/>
    <p:sldId id="267" r:id="rId18"/>
    <p:sldId id="268" r:id="rId19"/>
    <p:sldId id="269" r:id="rId20"/>
    <p:sldId id="270" r:id="rId21"/>
    <p:sldId id="271" r:id="rId22"/>
    <p:sldId id="272" r:id="rId23"/>
  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="5143500"/>
  <p:notesSz cx="5143500" cy="9144000"/>
  <p:defaultTextStyle>
    <a:lvl1pPr marL="0" algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1">
      <a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr>
    </a:lvl1pPr>
  </p:defaultTextStyle>
</p:presentation>'''
    with open(pres_path, "w") as f:
        f.write(pres)
    print("  Updated presentation.xml (15 slides)")

    # 7. Update presentation.xml.rels - add rId24 for slide18
    pres_rels_path = os.path.join(UNPACKED, "ppt", "_rels", "presentation.xml.rels")
    with open(pres_rels_path, "r") as f:
        rels = f.read()
    new_rel = '  <Relationship Id="rId24" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide18.xml"/>\n'
    if "rId24" not in rels:
        rels = rels.replace("</Relationships>", new_rel + "</Relationships>")
    with open(pres_rels_path, "w") as f:
        f.write(rels)
    print("  Updated presentation.xml.rels")

    # 8. Update [Content_Types].xml
    ct_path = os.path.join(UNPACKED, "[Content_Types].xml")
    with open(ct_path, "r") as f:
        ct = f.read()
    entry18 = '  <Override PartName="/ppt/slides/slide18.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
    if "slide18.xml" not in ct:
        ct = ct.replace("</Types>", entry18 + "</Types>")
    with open(ct_path, "w") as f:
        f.write(ct)
    print("  Updated [Content_Types].xml")

    print("\n  Done! Ready to repack.")


if __name__ == "__main__":
    main()
