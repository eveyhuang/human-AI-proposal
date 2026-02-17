#!/usr/bin/env python3
"""Build new slides for the diversity analysis presentation.

Adds 5 new slides for Part II (Novelty) and Part III (Thematic/Cluster),
updates Cross-Analysis Consistency + Key Findings + Implications slides,
copies images, and updates all OOXML registration files.
"""

import os
import shutil
import xml.etree.ElementTree as ET

BASE = "/Users/eveyhuang/Documents/NICO/human-AI-proposal-comparison"
UNPACKED = os.path.join(BASE, "workspace", "pptx_unpacked")
SLIDES_DIR = os.path.join(UNPACKED, "ppt", "slides")
RELS_DIR = os.path.join(SLIDES_DIR, "_rels")
MEDIA_DIR = os.path.join(UNPACKED, "ppt", "media")
FIGURES_DIR = os.path.join(BASE, "results", "figures")

# ─── Design system constants ───────────────────────────────────────
NAVY = "1B2A4A"
RED = "E8505B"
BLUE = "2E86AB"
WHITE = "FFFFFF"
BODY_DARK = "2C3E50"
BODY_GRAY = "5D6D7E"
BG_BLUE = "F7F9FC"
BG_PINK = "FDF8F8"
BG_LIGHT = "F0F4F8"
BG_GRAY = "F5F5F5"
PURPLE = "8E44AD"
ORANGE = "E67E22"
GREEN = "27AE60"
TEAL = "16A085"

FONT_BLOCK = '''<a:latin typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="0"/>
                <a:ea typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="-122"/>
                <a:cs typeface="Arial" panose="020B0604020202090204" pitchFamily="34" charset="-120"/>'''


def slide_header(title):
    """Return the standard header bar + title text (navy bar with white text)."""
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Text 0"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="0" y="0"/><a:ext cx="9144000" cy="650677"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill>
        </p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Text 1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="507950" y="177701"/><a:ext cx="8290661" cy="295275"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"/>
          <a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0" algn="l"><a:buNone/></a:pPr>
            <a:r><a:rPr lang="en-US" sz="2000" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill>{FONT_BLOCK}
            </a:rPr><a:t>{title}</a:t></a:r>
            <a:endParaRPr lang="en-US" sz="2000" dirty="0"/>
          </a:p>
        </p:txBody>
      </p:sp>'''


def subtitle_text(id_num, y, text, color=NAVY):
    """A bold subtitle below the header."""
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id_num}" name="Text {id_num-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="507950" y="{y}"/><a:ext cx="8290661" cy="171450"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0" algn="l"><a:spcAft><a:spcPts val="600"/></a:spcAft><a:buNone/></a:pPr>
            <a:r><a:rPr lang="en-US" sz="1200" b="1" dirty="0">
              <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{FONT_BLOCK}
            </a:rPr><a:t>{text}</a:t></a:r>
            <a:endParaRPr lang="en-US" sz="1200" dirty="0"/>
          </a:p>
        </p:txBody>
      </p:sp>'''


def accent_line(id_num, y, color=RED, width=444401):
    """Horizontal accent line."""
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id_num}" name="Text {id_num-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="507950" y="{y}"/><a:ext cx="{width}" cy="25301"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
        </p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p>
        </p:txBody>
      </p:sp>'''


def text_box(id_num, x, y, cx, cy, text, sz=950, color=BODY_DARK, bold=False, line_sp=1285):
    """General text box."""
    b_attr = ' b="1"' if bold else ''
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id_num}" name="Text {id_num-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0" algn="l">
            <a:lnSpc><a:spcPts val="{line_sp}"/></a:lnSpc>
            <a:spcAft><a:spcPts val="400"/></a:spcAft><a:buNone/></a:pPr>
            <a:r><a:rPr lang="en-US" sz="{sz}"{b_attr} dirty="0">
              <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{FONT_BLOCK}
            </a:rPr><a:t>{text}</a:t></a:r>
            <a:endParaRPr lang="en-US" sz="{sz}" dirty="0"/>
          </a:p>
        </p:txBody>
      </p:sp>'''


def rounded_rect_bg(id_num, x, y, cx, cy, color=BG_BLUE, adj=3645):
    """Background rounded rectangle."""
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id_num}" name="Text {id_num-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>
          <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
        </p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p>
        </p:txBody>
      </p:sp>'''


def horiz_line_shape(id_num, x, y, cx, color=BLUE, width=38100):
    """Horizontal accent line using line shape."""
    return f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{id_num}" name="Shape {id_num-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="0"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>
          <a:ln w="{width}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:prstDash val="solid"/></a:ln>
        </p:spPr>
      </p:sp>'''


def image_shape(id_num, rid, x, y, cx, cy):
    """Embedded image shape."""
    return f'''<p:pic>
        <p:nvPicPr>
          <p:cNvPr id="{id_num}" name="Picture {id_num}"/>
          <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="{rid}"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>'''


def finding_card(base_id, x, y, num, num_color, title, body, bg_color=BG_BLUE, line_color=BLUE):
    """A numbered finding card (used on Key Findings slide)."""
    card_cx = 3937099
    card_cy = 1050000
    return (
        rounded_rect_bg(base_id, x, y, card_cx, card_cy, bg_color) +
        horiz_line_shape(base_id+1, x, y + 19050, card_cx, line_color) +
        text_box(base_id+2, x + 152400, y + 146050, card_cx - 230000, 308521,
                 num, sz=1800, color=num_color, bold=True, line_sp=2430) +
        text_box(base_id+3, x + 152400, y + 400000, card_cx - 230000, 152400,
                 title, sz=1050, color=NAVY, bold=True) +
        text_box(base_id+4, x + 152400, y + 580000, card_cx - 230000, 420000,
                 body, sz=900, color=BODY_DARK)
    )


def impl_card(base_id, x, y, title, body, line_color=BLUE, bg_color=BG_BLUE):
    """Implication card for final slide."""
    cx = 3962400
    cy = 900000
    return (
        f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{base_id}" name="Text {base_id-2}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="{bg_color}"/></a:solidFill>
        </p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p>
        </p:txBody>
      </p:sp>''' +
        f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="{base_id+1}" name="Shape {base_id-1}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x + 19050}" y="{y}"/><a:ext cx="0" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>
          <a:ln w="38100"><a:solidFill><a:srgbClr val="{line_color}"/></a:solidFill><a:prstDash val="solid"/></a:ln>
        </p:spPr>
      </p:sp>''' +
        text_box(base_id+2, x + 190500, y + 76200, cx - 280000, 171301,
                 title, sz=1000, color=BODY_DARK, bold=True, line_sp=1350) +
        text_box(base_id+3, x + 190500, y + 290000, cx - 280000, cy - 350000,
                 body, sz=850, color=BODY_GRAY, line_sp=1150)
    )


def wrap_slide(shapes_xml):
    """Wrap shapes in a complete slide XML."""
    return f'''<?xml version="1.0" encoding="ascii"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {shapes_xml}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def rels_with_layout_and_images(image_list):
    """Create a slide .rels file with slideLayout and optional images."""
    rels = ['<?xml version="1.0" encoding="ascii"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>']
    for i, img in enumerate(image_list, 2):
        rels.append(f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{img}"/>')
    rels.append('</Relationships>')
    return '\n'.join(rels)


# ─── Slide 11: Novelty Analysis ────────────────────────────────────
def build_slide11():
    shapes = slide_header("Novelty Analysis: Distance from Existing Literature")
    shapes += subtitle_text(4, 853827,
        "Novelty = mean cosine distance to 10 nearest neighbors in a corpus of 350 PubMed articles")
    shapes += accent_line(5, 1101477, RED)

    # Left side: image
    shapes += image_shape(6, "rId2", 507950, 1253728, 4200000, 3150000)

    # Right side: findings
    shapes += rounded_rect_bg(7, 4850000, 1253728, 3937099, 1050000, BG_PINK)
    shapes += horiz_line_shape(8, 4850000, 1272778, 3937099, RED)
    shapes += text_box(9, 5002400, 1380679, 3704945, 152400,
        "Human proposals are more novel than AI", sz=1100, color=NAVY, bold=True)
    shapes += text_box(10, 5002400, 1581299, 3704945, 570000,
        "Human mean novelty: 0.151 vs AI combined: 0.117 (Cliff&#8217;s d = &#8722;0.34, medium effect, p = 0.014). "
        "Human proposals sit further from published literature, suggesting they draw on less well-trodden ideas.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(11, 4850000, 2430000, 3937099, 760000, BG_BLUE)
    shapes += horiz_line_shape(12, 4850000, 2449050, 3937099, BLUE)
    shapes += text_box(13, 5002400, 2556272, 3704945, 152400,
        "Claude is closest to human novelty", sz=1100, color=NAVY, bold=True)
    shapes += text_box(14, 5002400, 2730000, 3704945, 400000,
        "Claude: d = &#8722;0.21 (small, p = 0.22, not significant). "
        "Gemini: d = &#8722;0.42 (medium, p = 0.016). "
        "GPT-5.2: d = &#8722;0.40 (medium, p = 0.020). "
        "The same model that shows greatest internal diversity also produces the most novel output.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(15, 4850000, 3310000, 3937099, 760000, BG_LIGHT)
    shapes += horiz_line_shape(16, 4850000, 3329050, 3937099, TEAL)
    shapes += text_box(17, 5002400, 3436272, 3704945, 152400,
        "Most vs. least novel proposals", sz=1100, color=NAVY, bold=True)
    shapes += text_box(18, 5002400, 3610000, 3704945, 400000,
        "Most novel human: &#8220;Cytokinetic Bottlenecks of Heat Waves&#8221; (0.260). "
        "Least novel AI: a Gemini antibiotic resistance proposal (0.059), nearly overlapping published work. "
        "AI&#8217;s lower novelty may reflect reliance on training-data-dominant framings.",
        sz=900, color=BODY_DARK)

    return shapes


# ─── Slide 12: Novelty Embedding Space ─────────────────────────────
def build_slide12():
    shapes = slide_header("Novelty in Embedding Space")
    shapes += subtitle_text(4, 853827,
        "Proposals (colored) projected alongside 350 PubMed articles (gray) via UMAP")
    shapes += accent_line(5, 1101477, RED)

    # Large image
    shapes += image_shape(6, "rId2", 507950, 1253728, 4200000, 3400000)

    # Right side interpretation
    shapes += text_box(7, 4850000, 1253728, 3937099, 200000,
        "Key observations", sz=1200, color=NAVY, bold=True, line_sp=1600)

    shapes += text_box(8, 4850000, 1530000, 3937099, 420000,
        "Human proposals (gray markers) sit at the periphery of the literature cluster, "
        "occupying regions where fewer published articles exist. This is consistent with the "
        "novelty scores: humans venture further from the established literature.",
        sz=900, color=BODY_DARK)

    shapes += text_box(9, 4850000, 2050000, 3937099, 420000,
        "AI proposals (colored markers) tend to concentrate closer to dense literature regions, "
        "particularly GPT-5.2 and Gemini. Claude proposals show more scatter, with some overlapping "
        "human territory, consistent with its non-significant novelty difference.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(10, 4850000, 2600000, 3937099, 500000, BG_PINK)
    shapes += text_box(11, 5002400, 2680000, 3704945, 380000,
        "Linking diversity and novelty: GPT-5.2&#8217;s tight internal cluster maps onto well-published "
        "territory. High internal similarity + low novelty = AI re-deriving the same ideas from training data. "
        "Claude&#8217;s spread extends into less-charted space, mirroring its higher novelty scores.",
        sz=900, color=RED, bold=False)

    shapes += text_box(12, 4850000, 3250000, 3937099, 550000,
        "Interpretation caveat: UMAP projections can distort distances. The quantitative novelty scores "
        "(slide 8) are the primary evidence; this visualization serves as a qualitative consistency check. "
        "Proposals near literature &#8800; low quality, and distance from literature could also indicate incoherence.",
        sz=850, color=BODY_GRAY)

    return shapes


# ─── Slide 13: Topic Modeling ──────────────────────────────────────
def build_slide13():
    shapes = slide_header("Thematic Analysis: Topic Distribution")
    shapes += subtitle_text(4, 853827,
        "LDA topic modeling (k=5, strong priors) with Fisher&#8217;s exact tests and FDR correction")
    shapes += accent_line(5, 1101477, RED)

    # Left: image
    shapes += image_shape(6, "rId2", 507950, 1253728, 4200000, 3400000)

    # Right: results
    shapes += rounded_rect_bg(7, 4850000, 1253728, 3937099, 900000, BG_PINK)
    shapes += horiz_line_shape(8, 4850000, 1272778, 3937099, RED)
    shapes += text_box(9, 5002400, 1350000, 3704945, 152400,
        "Complete thematic separation", sz=1100, color=NAVY, bold=True)
    shapes += text_box(10, 5002400, 1530000, 3704945, 570000,
        "All 23 human proposals map to a single dominant topic (Topic 3: evolutionary/species-level biology). "
        "All 69 AI proposals distribute across the other 4 topics (mechanical/structural, transport/diffusion, "
        "imaging/perturbation, splicing/allosteric). Overall chi-square permutation test: p &lt; 0.0001.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(11, 4850000, 2280000, 3937099, 700000, BG_BLUE)
    shapes += horiz_line_shape(12, 4850000, 2299050, 3937099, BLUE)
    shapes += text_box(13, 5002400, 2380000, 3704945, 152400,
        "Per-topic Fisher&#8217;s exact tests (FDR-corrected)", sz=1050, color=NAVY, bold=True)
    shapes += text_box(14, 5002400, 2550000, 3704945, 380000,
        "Topic 3 (human-exclusive): p &lt; 0.0001. "
        "Topics 1, 4, 5 (AI-overrepresented): p &lt; 0.05. "
        "Topic 2 (AI-leaning): p = 0.061 (marginal). "
        "Subsample validation (n=23 each, 1000 iter): Topics 1 and 3 robust (&gt;98%); Topic 2 weak (18.5%).",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(15, 4850000, 3100000, 3937099, 600000, BG_GRAY)
    shapes += text_box(16, 5002400, 3180000, 3704945, 152400,
        "Critical caveat", sz=1050, color=RED, bold=True)
    shapes += text_box(17, 5002400, 3350000, 3704945, 310000,
        "Perfect separation is a red flag: LDA may be capturing systematic stylistic or templating artifacts "
        "rather than genuine scientific themes. Human entropy = 0 (all in one topic) is suspicious. "
        "These results are exploratory and require validation with expert coding.",
        sz=850, color=BODY_GRAY)

    return shapes


# ─── Slide 14: Cluster Segregation ─────────────────────────────────
def build_slide14():
    shapes = slide_header("Cluster Segregation Analysis")
    shapes += subtitle_text(4, 853827,
        "Gaussian Mixture Model clustering (k=3, selected by BIC) with segregation metrics")
    shapes += accent_line(5, 1101477, RED)

    # Left: image
    shapes += image_shape(6, "rId2", 507950, 1253728, 4200000, 3400000)

    # Right: results
    shapes += rounded_rect_bg(7, 4850000, 1253728, 3937099, 850000, BG_BLUE)
    shapes += horiz_line_shape(8, 4850000, 1272778, 3937099, BLUE)
    shapes += text_box(9, 5002400, 1350000, 3704945, 152400,
        "Cluster composition reveals asymmetric segregation", sz=1050, color=NAVY, bold=True)
    shapes += text_box(10, 5002400, 1530000, 3704945, 500000,
        "Cluster 0 (n=27): 100% AI. Cluster 1 (n=7): 100% AI. Cluster 2 (n=58): 40% human, 60% AI. "
        "Two clusters are entirely AI-dominated. All 23 human proposals land in a single mixed cluster, "
        "while AI proposals spread across all three, suggesting AI occupies distinct conceptual regions "
        "that humans do not enter.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(11, 4850000, 2230000, 3937099, 700000, BG_PINK)
    shapes += horiz_line_shape(12, 4850000, 2249050, 3937099, RED)
    shapes += text_box(13, 5002400, 2330000, 3704945, 152400,
        "Segregation metrics", sz=1050, color=NAVY, bold=True)
    shapes += text_box(14, 5002400, 2510000, 3704945, 380000,
        "NMI = 0.197 (p &lt; 0.0001): clusters predict human/AI source better than chance. "
        "ARI = &#8722;0.035 (p = 0.86): no agreement beyond chance (expected given unbalanced groups). "
        "Between/within distance ratio = 1.085 (p = 0.004): human and AI proposals are measurably "
        "more distant from each other than from their own group.",
        sz=900, color=BODY_DARK)

    shapes += rounded_rect_bg(15, 4850000, 3050000, 3937099, 650000, BG_LIGHT)
    shapes += horiz_line_shape(16, 4850000, 3069050, 3937099, TEAL)
    shapes += text_box(17, 5002400, 3150000, 3704945, 152400,
        "Connecting the evidence", sz=1050, color=NAVY, bold=True)
    shapes += text_box(18, 5002400, 3330000, 3704945, 330000,
        "Cluster segregation corroborates the nearest-neighbor finding (100% AI-AI nearest neighbors) "
        "and the topic separation. Across three independent methods &#8212; NN analysis, LDA topic modeling, "
        "and GMM clustering &#8212; humans and AI occupy different semantic territories.",
        sz=900, color=BODY_DARK)

    return shapes


# ─── Updated Slide 15: Integrated Findings ─────────────────────────
def build_slide15():
    """Replaces the old Cross-Analysis Consistency (slide 8)."""
    shapes = slide_header("Integrated Findings Across All Analyses")
    shapes += subtitle_text(4, 853827,
        "Convergent evidence from diversity, novelty, thematic, and cluster analyses")
    shapes += accent_line(5, 1101477, RED)

    # 2x3 grid of findings
    left_x = 507950
    right_x = 4698950
    row1_y = 1253728
    row2_y = 2500000
    row3_y = 3746272

    card_cx = 3937099
    card_cy = 1120000

    # Card 1: Diversity ranking
    shapes += rounded_rect_bg(6, left_x, row1_y, card_cx, card_cy, BG_PINK)
    shapes += horiz_line_shape(7, left_x, row1_y + 19050, card_cx, RED)
    shapes += text_box(8, left_x + 152400, row1_y + 100000, 3700000, 152400,
        "Diversity ranking is consistent", sz=1050, color=NAVY, bold=True)
    shapes += text_box(9, left_x + 152400, row1_y + 280000, 3700000, 780000,
        "Claude &gt; Human &gt; Gemini &gt; GPT-5.2, confirmed by pairwise, centroid, and NN analyses. "
        "All three metrics agree: same ranking, consistent effect sizes, robust under permutation.",
        sz=900, color=BODY_DARK)

    # Card 2: Novelty follows diversity
    shapes += rounded_rect_bg(10, right_x, row1_y, card_cx, card_cy, BG_BLUE)
    shapes += horiz_line_shape(11, right_x, row1_y + 19050, card_cx, BLUE)
    shapes += text_box(12, right_x + 152400, row1_y + 100000, 3700000, 152400,
        "Novelty tracks a different dimension", sz=1050, color=NAVY, bold=True)
    shapes += text_box(13, right_x + 152400, row1_y + 280000, 3700000, 780000,
        "Human &gt; Claude &gt; GPT-5.2 &#8776; Gemini for novelty. Humans are both moderately diverse AND more novel. "
        "Claude is most diverse but only moderately novel, suggesting its spread is within AI-typical territory. "
        "Diversity &#8800; novelty.",
        sz=900, color=BODY_DARK)

    # Card 3: Semantic segregation
    shapes += rounded_rect_bg(14, left_x, row2_y, card_cx, card_cy, BG_BLUE)
    shapes += horiz_line_shape(15, left_x, row2_y + 19050, card_cx, TEAL)
    shapes += text_box(16, left_x + 152400, row2_y + 100000, 3700000, 152400,
        "Semantic segregation confirmed 3 ways", sz=1050, color=NAVY, bold=True)
    shapes += text_box(17, left_x + 152400, row2_y + 280000, 3700000, 780000,
        "100% AI-AI nearest neighbors (NN analysis). Complete topic separation (LDA). "
        "Two AI-only clusters (GMM, NMI p &lt; 0.0001). Human and AI proposals occupy different "
        "semantic regions, even when AI shows high internal diversity.",
        sz=900, color=BODY_DARK)

    # Card 4: Aggregation misleads
    shapes += rounded_rect_bg(18, right_x, row2_y, card_cx, card_cy, BG_LIGHT)
    shapes += horiz_line_shape(19, right_x, row2_y + 19050, card_cx, PURPLE)
    shapes += text_box(20, right_x + 152400, row2_y + 100000, 3700000, 152400,
        "Aggregation masks real differences", sz=1050, color=NAVY, bold=True)
    shapes += text_box(21, right_x + 152400, row2_y + 280000, 3700000, 780000,
        "&#8220;AI vs Human&#8221; centroid dispersion: non-significant (p = 0.22). "
        "But per-model: Claude d = +0.99, GPT-5.2 d = &#8722;1.00. "
        "Similarly, topic entropy (AI = 1.94, Human = 0.00) hides that humans produce truly distinctive ideas "
        "rather than a single narrow theme.",
        sz=900, color=BODY_DARK)

    # Bottom bar: key takeaway
    shapes += rounded_rect_bg(22, 507950, row3_y, 8128099, 500000, NAVY, adj=3000)
    shapes += text_box(23, 660350, row3_y + 100000, 7900000, 350000,
        "Bottom line: AI models generate systematically different kinds of ideas than humans, and "
        "they differ dramatically from each other. Human proposals are more novel relative to existing literature "
        "and occupy unique conceptual territory that no AI model fully reaches.",
        sz=1000, color=WHITE, bold=True, line_sp=1400)

    return shapes


# ─── Updated Slide 16: Key Findings ───────────────────────────────
def build_slide16():
    """Replaces the old Key Findings (slide 9)."""
    shapes = slide_header("Key Findings")

    left_x = 507950
    right_x = 4698950
    row1_y = 853827
    row2_y = 2050000
    row3_y = 3300000

    # Card 1
    shapes += finding_card(4, left_x, row1_y, "1", RED,
        "Model-specific diversity varies dramatically",
        "Claude is more diverse than humans (d = +0.25, pairwise). "
        "GPT-5.2 shows mode collapse (d = &#8722;1.00). Gemini is intermediate (d = &#8722;0.73). "
        "There is no single &#8220;AI diversity&#8221; story.",
        BG_PINK, RED)

    # Card 2
    shapes += finding_card(9, right_x, row1_y, "2", BLUE,
        "Human proposals are more novel than AI",
        "Human mean novelty 0.151 vs AI 0.117 (d = &#8722;0.34, medium). "
        "Claude&#8217;s novelty is closest to human (not significant), while GPT-5.2 and Gemini "
        "are significantly less novel &#8212; their output stays close to published literature.",
        BG_BLUE, BLUE)

    # Card 3
    shapes += finding_card(14, left_x, row2_y, "3", BLUE,
        "Human and AI occupy different semantic territory",
        "100% of AI nearest neighbors are other AI proposals. GMM clustering: 2 of 3 clusters are "
        "AI-only (NMI = 0.20, p &lt; 0.0001). LDA: complete topic separation. "
        "Humans and AI generate fundamentally different kinds of ideas.",
        BG_BLUE, BLUE)

    # Card 4
    shapes += finding_card(19, right_x, row2_y, "4", TEAL,
        "Diversity does not equal novelty",
        "Claude produces the most diverse proposals, but they are only moderately novel. "
        "Human proposals are moderately diverse but most novel. High diversity within AI space may "
        "reflect variation among training-data-typical framings, not genuinely new ideas.",
        BG_LIGHT, TEAL)

    # Bottom key takeaway
    shapes += rounded_rect_bg(24, 507950, row3_y, 8128099, 650000, BG_GRAY, adj=5000)
    shapes += text_box(25, 660350, row3_y + 80000, 7900000, 200000,
        "Overarching narrative", sz=1100, color=NAVY, bold=True)
    shapes += text_box(26, 660350, row3_y + 310000, 7900000, 300000,
        "AI models can produce diverse proposals on paper, but that diversity operates within a different "
        "conceptual space than humans. Human scientists bring genuinely novel perspectives &#8212; ideas "
        "further from published literature and outside the semantic territory AI models inhabit. "
        "This suggests AI is better positioned as an ideation complement to, rather than replacement for, human researchers.",
        sz=900, color=BODY_DARK)

    return shapes


# ─── Updated Slide 17: Implications & Limitations ──────────────────
def build_slide17():
    """Replaces the old Implications slide (slide 10)."""
    shapes = slide_header("Implications &#38; Limitations")
    shapes += subtitle_text(4, 853827, "What This Means", NAVY)
    shapes += accent_line(5, 1101477, RED)

    left_x = 507950
    right_x = 4673501

    # Left column: 3 implication cards
    shapes += impl_card(6, left_x, 1253728,
        "AI models are not interchangeable for scientific ideation",
        "GPT-5.2&#8217;s mode collapse vs Claude&#8217;s subcluster diversity means model "
        "choice drastically affects the space of ideas. Researchers should test multiple models "
        "and evaluate outputs comparatively, not assume one model represents &#8220;AI.&#8221;",
        BLUE, BG_BLUE)

    shapes += impl_card(10, left_x, 2270000,
        "Human novelty advantage suggests complementary roles",
        "Human proposals venture further from published literature, indicating that human scientists "
        "bring perspectives not derivable from training data alone. AI may be most valuable for "
        "extending existing lines of inquiry, while humans contribute genuinely novel framings.",
        TEAL, BG_BLUE)

    shapes += impl_card(14, left_x, 3290000,
        "Semantic segregation raises questions about AI&#8217;s &#8220;idea space&#8221;",
        "The consistent finding that AI and human proposals occupy distinct territories &#8212; confirmed "
        "by NN, LDA, and GMM analyses &#8212; suggests systematic differences in how AI frames research. "
        "This may limit AI&#8217;s ability to surface truly unconventional ideas.",
        PURPLE, BG_LIGHT)

    # Right column: limitations
    shapes += f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="18" name="Text 16"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{right_x}" y="1253728"/><a:ext cx="3962549" cy="2800000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="{BG_PINK}"/></a:solidFill>
        </p:spPr>
        <p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"/><a:lstStyle/>
          <a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr><a:endParaRPr lang="en-US" dirty="0"/></a:p>
        </p:txBody>
      </p:sp>'''
    shapes += f'''<p:sp>
        <p:nvSpPr><p:cNvPr id="19" name="Shape 17"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{right_x + 19050}" y="1253728"/><a:ext cx="0" cy="2800000"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:noFill/>
          <a:ln w="38100"><a:solidFill><a:srgbClr val="{RED}"/></a:solidFill><a:prstDash val="solid"/></a:ln>
        </p:spPr>
      </p:sp>'''
    shapes += text_box(20, right_x + 190500, 1350000, 3600000, 200000,
        "Limitations", sz=1200, color=RED, bold=True, line_sp=1600)

    lim_items = [
        "Single funding call (NCEMS) &#8212; generalizability is unknown.",
        "Small, unbalanced sample (23 human vs. 69 AI). Power is limited for subtle effects.",
        "Embedding distance &#8800; conceptual diversity. BioLinkBERT may conflate stylistic "
        "with semantic differences. Expert validation is needed.",
        "Novelty score conflates novelty with incoherence. High distance from literature "
        "could mean a genuinely new idea OR a poorly formulated one.",
        "Topic separation may be an artifact of writing style or prompt templating, not "
        "genuine thematic differences. LDA results are exploratory.",
        "Population mismatch: humans wrote under real funding stakes; AI under zero stakes. "
        "This confounds any comparison of quality or effort.",
        "No quality evaluation yet &#8212; diversity and novelty do not imply good science. "
        "Human expert review (planned) is the critical missing piece.",
    ]
    y_pos = 1600000
    for item in lim_items:
        shapes += text_box(21, right_x + 190500, y_pos, 3600000, 200000,
            "&#8226; " + item, sz=800, color=BODY_DARK, line_sp=1050)
        y_pos += 270000

    # Bottom: next steps
    shapes += rounded_rect_bg(30, 507950, 4200000, 8128099, 380000, NAVY, adj=3000)
    shapes += text_box(31, 660350, 4260000, 7900000, 260000,
        "Next steps: (1) Human expert evaluation of proposal quality; (2) Augmented conditions "
        "(literature-enriched, persona-based prompts); (3) Construct validation of embedding metrics; "
        "(4) Larger sample sizes across multiple funding calls.",
        sz=900, color=WHITE, bold=True, line_sp=1200)

    return shapes


# ─── Main: build everything ────────────────────────────────────────
def main():
    # 1. Copy images to media folder
    image_map = {
        "image4.png": "novelty_analysis.png",
        "image5.png": "novelty_embedding_space.png",
        "image6.png": "topic_distribution_comparison.png",
        "image7.png": "cluster_analysis_visualization.png",
    }
    for dest, src in image_map.items():
        src_path = os.path.join(FIGURES_DIR, src)
        dst_path = os.path.join(MEDIA_DIR, dest)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"  Copied {src} -> {dest}")
        else:
            print(f"  WARNING: {src_path} not found!")

    # 2. Write new slide XMLs
    slides = {
        "slide11.xml": wrap_slide(build_slide11()),
        "slide12.xml": wrap_slide(build_slide12()),
        "slide13.xml": wrap_slide(build_slide13()),
        "slide14.xml": wrap_slide(build_slide14()),
    }
    # Overwrite slides 8, 9, 10 -> become slides 15, 16, 17
    slides["slide15.xml"] = wrap_slide(build_slide15())
    slides["slide16.xml"] = wrap_slide(build_slide16())
    slides["slide17.xml"] = wrap_slide(build_slide17())

    for name, content in slides.items():
        path = os.path.join(SLIDES_DIR, name)
        with open(path, "w", encoding="ascii", errors="xmlcharrefreplace") as f:
            f.write(content)
        print(f"  Wrote {name}")

    # 3. Write slide rels files
    new_rels = {
        "slide11.xml.rels": rels_with_layout_and_images(["image4.png"]),
        "slide12.xml.rels": rels_with_layout_and_images(["image5.png"]),
        "slide13.xml.rels": rels_with_layout_and_images(["image6.png"]),
        "slide14.xml.rels": rels_with_layout_and_images(["image7.png"]),
        "slide15.xml.rels": rels_with_layout_and_images([]),
        "slide16.xml.rels": rels_with_layout_and_images([]),
        "slide17.xml.rels": rels_with_layout_and_images([]),
    }
    for name, content in new_rels.items():
        path = os.path.join(RELS_DIR, name)
        with open(path, "w") as f:
            f.write(content)
        print(f"  Wrote _rels/{name}")

    # 4. Update presentation.xml - add new slide entries and reorder
    pres_path = os.path.join(UNPACKED, "ppt", "presentation.xml")
    # New slide order: 1-7 (unchanged), 11-14 (new), 15-17 (updated summaries)
    # We keep rId3-rId10 for slides 1-7, plus old rId11-13 for slides 8-10
    # Add rId17-rId23 for slides 11-17
    pres_xml = '''<?xml version="1.0" encoding="ascii"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" autoCompressPictures="0">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:notesMasterIdLst>
    <p:notesMasterId r:id="rId4"/>
  </p:notesMasterIdLst>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId3"/>
    <p:sldId id="257" r:id="rId5"/>
    <p:sldId id="258" r:id="rId6"/>
    <p:sldId id="259" r:id="rId7"/>
    <p:sldId id="260" r:id="rId8"/>
    <p:sldId id="261" r:id="rId9"/>
    <p:sldId id="262" r:id="rId10"/>
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
        f.write(pres_xml)
    print("  Updated presentation.xml")

    # 5. Update presentation.xml.rels
    pres_rels_path = os.path.join(UNPACKED, "ppt", "_rels", "presentation.xml.rels")
    pres_rels = '''<?xml version="1.0" encoding="ascii"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide3.xml"/>
  <Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide4.xml"/>
  <Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide5.xml"/>
  <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide6.xml"/>
  <Relationship Id="rId10" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide7.xml"/>
  <Relationship Id="rId14" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>
  <Relationship Id="rId15" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps" Target="viewProps.xml"/>
  <Relationship Id="rId16" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles" Target="tableStyles.xml"/>
  <Relationship Id="rId17" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide11.xml"/>
  <Relationship Id="rId18" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide12.xml"/>
  <Relationship Id="rId19" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide13.xml"/>
  <Relationship Id="rId20" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide14.xml"/>
  <Relationship Id="rId21" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide15.xml"/>
  <Relationship Id="rId22" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide16.xml"/>
  <Relationship Id="rId23" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide17.xml"/>
</Relationships>'''
    with open(pres_rels_path, "w") as f:
        f.write(pres_rels)
    print("  Updated presentation.xml.rels")

    # 6. Update [Content_Types].xml
    ct_path = os.path.join(UNPACKED, "[Content_Types].xml")
    with open(ct_path, "r") as f:
        ct = f.read()

    # Add new slide entries before closing </Types>
    new_entries = ""
    for i in range(11, 18):
        entry = f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
        if entry.strip() not in ct:
            new_entries += entry

    if new_entries:
        ct = ct.replace("</Types>", new_entries + "</Types>")

    with open(ct_path, "w") as f:
        f.write(ct)
    print("  Updated [Content_Types].xml")

    # 7. Remove old slides 8-10 from the slide order (they're replaced by 15-17)
    # The old slide8-10 files stay on disk but are no longer referenced
    # Actually we should remove old rId11-13 references since we replaced them
    # The old slide8.xml, slide9.xml, slide10.xml files are no longer in the sldIdLst
    print("\n  Old slides 8-10 are no longer referenced (replaced by slides 15-17).")
    print("  Done! Ready to validate and pack.")


if __name__ == "__main__":
    main()
