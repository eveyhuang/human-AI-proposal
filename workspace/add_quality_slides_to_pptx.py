#!/usr/bin/env python3
import csv
import html
import os
import re
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

PPTX_PATH = Path('/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/diversity_analysis_presentation_baseline_updated_20260218.pptx')
FIG_DIR = Path('/Users/eveyhuang/Documents/NICO/human-AI-proposal/results/figures/quality')

P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'

ET.register_namespace('p', P_NS)
ET.register_namespace('a', A_NS)
ET.register_namespace('r', R_NS)
ET.register_namespace('', PR_NS)
ET.register_namespace('', CT_NS)

NAVY = '1B2A4A'
WHITE = 'FFFFFF'
TEXT = '2C3E50'
ACCENT = 'E8505B'
GRAY = '5D6D7E'


def read_csv_rows(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def fnum(x, d=2):
    try:
        return f"{float(x):.{d}f}"
    except Exception:
        return 'NA'


def find_row(rows, **conds):
    for r in rows:
        ok = True
        for k, v in conds.items():
            if str(r.get(k)) != str(v):
                ok = False
                break
        if ok:
            return r
    return None


def ppt_escape(s):
    return html.escape(str(s), quote=False)


def font_block():
    return '<a:latin typeface="Arial"/><a:ea typeface="Arial"/><a:cs typeface="Arial"/>'


def header_shapes(title, subtitle):
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="2" name="HeaderBar"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="9144000" cy="650000"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody>
</p:sp>
<p:sp>
  <p:nvSpPr><p:cNvPr id="3" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="500000" y="170000"/><a:ext cx="8300000" cy="300000"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle>
  </a:lstStyle><a:p><a:pPr algn="l"/><a:r><a:rPr sz="2000" b="1"><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill>{font_block()}</a:rPr><a:t>{ppt_escape(title)}</a:t></a:r></a:p></p:txBody>
</p:sp>
<p:sp>
  <p:nvSpPr><p:cNvPr id="4" name="Subtitle"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="500000" y="760000"/><a:ext cx="8300000" cy="260000"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="l"/><a:r><a:rPr sz="1050" b="1"><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill>{font_block()}</a:rPr><a:t>{ppt_escape(subtitle)}</a:t></a:r></a:p></p:txBody>
</p:sp>
<p:sp>
  <p:nvSpPr><p:cNvPr id="5" name="Accent"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="500000" y="1050000"/><a:ext cx="500000" cy="23000"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{ACCENT}"/></a:solidFill></p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr/></a:p></p:txBody>
</p:sp>'''


def textbox(shape_id, x, y, cx, cy, lines, size=900, color=TEXT, bold=False):
    paras = []
    for line in lines:
        line = ppt_escape(line)
        paras.append(
            f'<a:p><a:pPr algn="l"/><a:r><a:rPr sz="{size}"' +
            (' b="1"' if bold else '') +
            f'><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{font_block()}</a:rPr><a:t>{line}</a:t></a:r></a:p>'
        )
    paras_xml = ''.join(paras)
    return f'''<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id}" name="Text{shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
  <p:txBody><a:bodyPr/><a:lstStyle/>{paras_xml}</p:txBody>
</p:sp>'''


def image_shape(shape_id, rid, x, y, cx, cy):
    return f'''<p:pic>
  <p:nvPicPr><p:cNvPr id="{shape_id}" name="Pic{shape_id}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
  <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
</p:pic>'''


def wrap_slide(shapes_xml):
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{A_NS}" xmlns:r="{R_NS}" xmlns:p="{P_NS}">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {shapes_xml}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def rels_xml(image_targets):
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Relationships xmlns="{PR_NS}">',
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>',
    ]
    for i, target in enumerate(image_targets, start=2):
        parts.append(f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{target}"/>')
    parts.append('</Relationships>')
    return '\n'.join(parts)


def make_slide_1(vals):
    s = header_shapes('Part IV Quality: Motivation and Analytical Logic',
                      'Why review-quality analysis is necessary beyond diversity/novelty')
    lines = [
        '• Motivation: Proposal diversity/novelty do not tell us whether ideas are high-quality or fundable.',
        '• Risk: AI-as-judge can be biased (evaluator leniency, self-preference).',
        '• Design choice: three linked analyses to separate quality signal from judging bias.',
        '• R1 Proxy test: Human–AI vs Human–Human review similarity (proposal-level, FDR-corrected).',
        '• R2 Quality test: Human vs AI proposal scores (Mann-Whitney + Cliff\'s delta + robust checks).',
        '• R3 Bias test: evaluator effects + self-preference + bias-controlled reruns.',
        '• Coherence goal: compare baseline findings to sensitivity reruns before drawing conclusions.',
    ]
    s += textbox(6, 500000, 1200000, 8400000, 3200000, lines, size=880)
    s += textbox(7, 500000, 4450000, 8400000, 450000,
                 ['Method rationale: non-parametric tests are appropriate for small n and skewed score distributions.'],
                 size=820, color=GRAY, bold=True)
    return wrap_slide(s), []


def make_slide_2(vals):
    s = header_shapes('R1: Are AI Reviews a Reliable Proxy for Human Expert Reviews?',
                      'Similarity structure across Human–Human, Human–AI, and AI–AI review pairs')
    s += image_shape(6, 'rId2', 500000, 1200000, 5000000, 3000000)
    lines = [
        'Why this analysis: proxy validity requires AI review reasoning to align with human reviewer reasoning.',
        'Method argument: proposal-level aggregation avoids pairwise pseudo-replication; FDR controls multiplicity.',
        f"Result: Human–AI vs Human–Human cosine similarity not significant (q={vals['r1_hai_hh_q']}, Cliff's δ={vals['r1_hai_hh_d']}).",
        f"Result: AI–AI vs Human–Human cosine is significantly higher (q={vals['r1_aiai_hh_q']}, δ={vals['r1_aiai_hh_d']}).",
        f"Result: AI–AI vs Human–AI is also higher (q={vals['r1_aiai_hai_q']}, δ={vals['r1_aiai_hai_d']}).",
        'Interpretation: AI reviews are not clearly less human-like than human-human baseline,',
        'but AI judges are more internally homogeneous, which may compress critique diversity.',
    ]
    s += textbox(7, 5600000, 1250000, 3000000, 2950000, lines, size=760)
    return wrap_slide(s), ['quality_similarity_proxy_boxplots_proposal_level.png']


def make_slide_3(vals):
    s = header_shapes('R2 Baseline: AI-Judged Proposal Quality vs Human Proposals',
                      'Proposal-level scoring (all AI evaluators pooled)')
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2500000)
    s += image_shape(7, 'rId3', 4600000, 1250000, 4000000, 2500000)
    lines = [
        'Why this analysis: tests whether AI-generated proposals are scored as higher quality, and on which criteria.',
        'Method argument: Mann-Whitney + Cliff\'s delta + FDR, with criterion-level decomposition.',
        f"Overall means: Human-all {vals['base_h_mean']}, Claude {vals['base_c_mean']} (q={vals['base_c_q']}),",
        f"Gemini {vals['base_g_mean']} (q={vals['base_g_q']}), GPT-5.2 {vals['base_t_mean']} (q={vals['base_t_q']}).",
        'Interpretation: baseline pooled judges rate Gemini and GPT proposals above human proposals; Claude is not higher overall.',
        'Heatmap shows where effects concentrate by criterion and model (not a uniform pattern across models).',
    ]
    s += textbox(8, 500000, 3900000, 8400000, 1200000, lines, size=760)
    return wrap_slide(s), ['quality_overall_boxplot_proposal_level.png', 'quality_effect_size_heatmap.png']


def make_slide_4(vals):
    s = header_shapes('R3 Bias Diagnostics: Evaluator Effects and Self-Preference',
                      'Testing whether AI models systematically favor their own outputs')
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2500000)
    s += image_shape(7, 'rId3', 4600000, 1250000, 4000000, 2500000)
    lines = [
        'Why this analysis: AI-as-judge claims require explicit bias checks before interpretation.',
        f"Evaluator leniency differs: mean scores Gemini {vals['eval_g_mean']} > Claude {vals['eval_c_mean']} > GPT {vals['eval_t_mean']}.",
        f"Self-preference (overall): GPT strong positive (q={vals['sp_gpt_q']}); Claude shows reverse effect (q={vals['sp_claude_q']}); Gemini not significant.",
        'Criterion heatmap shows bias is criterion-dependent, not constant across rubric dimensions.',
        'Interpretation: pooled quality conclusions are confounded unless self-evaluation pathways are controlled.',
    ]
    s += textbox(8, 500000, 3900000, 8400000, 1200000, lines, size=760)
    return wrap_slide(s), ['self_pref_strip_overall.png', 'self_pref_criterion_heatmap.png']


def make_slide_5(vals):
    s = header_shapes('Bias-Controlled R2 Reruns',
                      'Cross-evaluator-only and Gemini-only sensitivity analyses')
    s += image_shape(6, 'rId2', 500000, 1250000, 4000000, 2500000)
    s += image_shape(7, 'rId3', 4600000, 1250000, 4000000, 2500000)
    lines = [
        'Cross-evaluator-only rule: for AI-authored proposals, remove the score from the model that wrote it.',
        f"Result: Gemini overall advantage attenuates (q={vals['cross_g_q']}, mean {vals['cross_g_mean']} vs human {vals['cross_h_mean']}); GPT remains high (q={vals['cross_t_q']}).",
        'Gemini-only judge rerun (single evaluator for all proposals):',
        f"Claude scores below human (q={vals['gem_c_q']}); Gemini and GPT remain above human (q={vals['gem_g_q']}, {vals['gem_t_q']}).",
        'Interpretation: GPT advantage is robust to bias controls; Gemini/Claude conclusions are judge-configuration sensitive.',
    ]
    s += textbox(8, 500000, 3900000, 8400000, 1200000, lines, size=760)
    return wrap_slide(s), ['quality_effectsize_heatmap_cross_eval_only.png', 'quality_effectsize_heatmap_gemini_only.png']


def make_slide_6(vals):
    s = header_shapes('Integrated Interpretation for a General-Science Audience',
                      'What we can conclude now, and what still needs independent validation')
    lines = [
        'Synthesis across R1–R3:',
        '• R1: AI reviews are not obviously less aligned than human-human baseline, but AI-AI consistency is unusually high.',
        '• R2 baseline: AI-generated proposals (especially GPT, often Gemini) receive higher AI-judge scores than human proposals.',
        '• R3: evaluator identity and self-preference materially affect conclusions; bias controls change some model-level outcomes.',
        'Practical inference:',
        '• Strongest robust signal in current data: GPT-generated proposals remain highly rated under bias controls.',
        '• Model-specific claims for Gemini/Claude should be treated as conditional on evaluator setup.',
        'Important limitation from current notebook outputs:',
        '• Human-panel proxy-calibration metrics are not currently estimable (NaN correlations/ICC in exported tables).',
        '  This prevents a definitive claim that AI judges are valid substitutes for expert human review.',
        'Recommendation:',
        '• Use AI judging as a screening aid, not a standalone decision mechanism, until blinded external human rerating is complete.',
    ]
    s += textbox(6, 500000, 1250000, 8400000, 3300000, lines, size=800)
    return wrap_slide(s), []


def collect_values(fig_dir):
    sim = read_csv_rows(fig_dir / 'quality_similarity_mw_cliffs_overall.csv')
    pairwise = read_csv_rows(fig_dir / 'quality_pairwise_mw_cliffs_all_metrics_proposal_level.csv')
    evals = read_csv_rows(fig_dir / 'quality_evaluator_overall_stats_clean.csv')
    sp = read_csv_rows(fig_dir / 'quality_self_preference_tests_overall.csv')
    cross = read_csv_rows(fig_dir / 'quality_vs_ai_mw_cliffs_cross_eval_only.csv')
    gem = read_csv_rows(fig_dir / 'quality_vs_ai_mw_cliffs_gemini_only.csv')

    r1_hai_hh = find_row(sim, metric='cosine_similarity', group1='human-ai', group2='human-human')
    r1_aiai_hh = find_row(sim, metric='cosine_similarity', group1='ai-ai', group2='human-human')
    r1_aiai_hai = find_row(sim, metric='cosine_similarity', group1='ai-ai', group2='human-ai')

    b_c = find_row(pairwise, metric='overall_score', group1='human-all', group2='claude-opus-4-5')
    b_g = find_row(pairwise, metric='overall_score', group1='human-all', group2='gemini-3-pro-preview')
    b_t = find_row(pairwise, metric='overall_score', group1='human-all', group2='gpt-5.2')

    ev_c = find_row(evals, evaluator='claude-opus-4-5')
    ev_g = find_row(evals, evaluator='gemini-3-pro-preview')
    ev_t = find_row(evals, evaluator='gpt-5.2')

    sp_c = find_row(sp, evaluator='claude-opus-4-5')
    sp_g = find_row(sp, evaluator='gemini-3-pro-preview')
    sp_t = find_row(sp, evaluator='gpt-5.2')

    c_g = find_row(cross, metric='overall_score', group2='gemini-3-pro-preview')
    c_t = find_row(cross, metric='overall_score', group2='gpt-5.2')

    g_c = find_row(gem, metric='overall_score', group2='claude-opus-4-5')
    g_g = find_row(gem, metric='overall_score', group2='gemini-3-pro-preview')
    g_t = find_row(gem, metric='overall_score', group2='gpt-5.2')

    return {
        'r1_hai_hh_q': fnum(r1_hai_hh.get('q_value'), 3),
        'r1_hai_hh_d': fnum(r1_hai_hh.get('cliffs_delta'), 2),
        'r1_aiai_hh_q': fnum(r1_aiai_hh.get('q_value'), 3),
        'r1_aiai_hh_d': fnum(r1_aiai_hh.get('cliffs_delta'), 2),
        'r1_aiai_hai_q': fnum(r1_aiai_hai.get('q_value'), 3),
        'r1_aiai_hai_d': fnum(r1_aiai_hai.get('cliffs_delta'), 2),

        'base_h_mean': fnum(b_c.get('mean_group1'), 2),
        'base_c_mean': fnum(b_c.get('mean_group2'), 2),
        'base_c_q': fnum(b_c.get('q_value'), 3),
        'base_g_mean': fnum(b_g.get('mean_group2'), 2),
        'base_g_q': fnum(b_g.get('q_value'), 3),
        'base_t_mean': fnum(b_t.get('mean_group2'), 2),
        'base_t_q': fnum(b_t.get('q_value'), 3),

        'eval_c_mean': fnum(ev_c.get('mean'), 2),
        'eval_g_mean': fnum(ev_g.get('mean'), 2),
        'eval_t_mean': fnum(ev_t.get('mean'), 2),

        'sp_claude_q': fnum(sp_c.get('q_value'), 3),
        'sp_gem_q': fnum(sp_g.get('q_value'), 3),
        'sp_gpt_q': fnum(sp_t.get('q_value'), 3),

        'cross_h_mean': fnum(c_g.get('mean_group1'), 2),
        'cross_g_mean': fnum(c_g.get('mean_group2'), 2),
        'cross_g_q': fnum(c_g.get('q_value'), 3),
        'cross_t_q': fnum(c_t.get('q_value'), 3),

        'gem_c_q': fnum(g_c.get('q_value'), 3),
        'gem_g_q': fnum(g_g.get('q_value'), 3),
        'gem_t_q': fnum(g_t.get('q_value'), 3),
    }


def add_quality_slides(pptx_path: Path):
    vals = collect_values(FIG_DIR)

    slides_def = [
        make_slide_1,
        make_slide_2,
        make_slide_3,
        make_slide_4,
        make_slide_5,
        make_slide_6,
    ]

    with tempfile.TemporaryDirectory(prefix='pptx_edit_') as td:
        root = Path(td)
        with zipfile.ZipFile(pptx_path, 'r') as zf:
            zf.extractall(root)

        slides_dir = root / 'ppt' / 'slides'
        rels_dir = slides_dir / '_rels'
        media_dir = root / 'ppt' / 'media'

        existing_slide_nums = sorted(int(m.group(1)) for m in [re.match(r'slide(\d+)\.xml$', p.name) for p in slides_dir.glob('slide*.xml')] if m)
        max_slide = max(existing_slide_nums)

        # Parse presentation.xml
        pres_path = root / 'ppt' / 'presentation.xml'
        pres_tree = ET.parse(pres_path)
        pres_root = pres_tree.getroot()
        ns = {'p': P_NS, 'r': R_NS}
        sldIdLst = pres_root.find('p:sldIdLst', ns)
        max_sld_id = max(int(x.attrib['id']) for x in sldIdLst.findall('p:sldId', ns))

        # Parse presentation rels
        pres_rels_path = root / 'ppt' / '_rels' / 'presentation.xml.rels'
        pres_rels_tree = ET.parse(pres_rels_path)
        pres_rels_root = pres_rels_tree.getroot()
        rel_nums = []
        for rel in pres_rels_root.findall(f'{{{PR_NS}}}Relationship'):
            rid = rel.attrib.get('Id', '')
            m = re.match(r'rId(\d+)$', rid)
            if m:
                rel_nums.append(int(m.group(1)))
        max_rel_num = max(rel_nums) if rel_nums else 1

        # Parse content types
        ct_path = root / '[Content_Types].xml'
        ct_tree = ET.parse(ct_path)
        ct_root = ct_tree.getroot()

        new_slide_num = max_slide
        new_sld_id = max_sld_id
        new_rel_num = max_rel_num

        for idx, builder in enumerate(slides_def, start=1):
            slide_xml, img_basenames = builder(vals)
            new_slide_num += 1
            new_sld_id += 1
            new_rel_num += 1
            pres_rid = f'rId{new_rel_num}'

            # copy images and assign slide-local relationship IDs
            copied_names = []
            for img in img_basenames:
                src = FIG_DIR / img
                if not src.exists():
                    raise FileNotFoundError(f'Missing image: {src}')
                dst_name = f'quality_{new_slide_num}_{img}'
                shutil.copy2(src, media_dir / dst_name)
                copied_names.append(dst_name)

            # write slide xml
            slide_path = slides_dir / f'slide{new_slide_num}.xml'
            slide_path.write_text(slide_xml, encoding='utf-8')

            # write slide rels
            rels_path = rels_dir / f'slide{new_slide_num}.xml.rels'
            rels_path.write_text(rels_xml(copied_names), encoding='utf-8')

            # update presentation.xml.rels
            ET.SubElement(
                pres_rels_root,
                f'{{{PR_NS}}}Relationship',
                {
                    'Id': pres_rid,
                    'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide',
                    'Target': f'slides/slide{new_slide_num}.xml',
                },
            )

            # update presentation.xml sldIdLst
            ET.SubElement(
                sldIdLst,
                f'{{{P_NS}}}sldId',
                {
                    'id': str(new_sld_id),
                    f'{{{R_NS}}}id': pres_rid,
                },
            )

            # update [Content_Types].xml
            part_name = f'/ppt/slides/slide{new_slide_num}.xml'
            exists = any(x.attrib.get('PartName') == part_name for x in ct_root.findall(f'{{{CT_NS}}}Override'))
            if not exists:
                ET.SubElement(
                    ct_root,
                    f'{{{CT_NS}}}Override',
                    {
                        'PartName': part_name,
                        'ContentType': 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml',
                    },
                )

        # write updated xml files
        pres_tree.write(pres_path, encoding='utf-8', xml_declaration=True)
        pres_rels_tree.write(pres_rels_path, encoding='utf-8', xml_declaration=True)
        ct_tree.write(ct_path, encoding='utf-8', xml_declaration=True)

        # backup original
        backup = pptx_path.with_suffix('.pptx.bak')
        if not backup.exists():
            shutil.copy2(pptx_path, backup)

        # repack
        tmp_out = pptx_path.with_suffix('.pptx.tmp')
        if tmp_out.exists():
            tmp_out.unlink()
        with zipfile.ZipFile(tmp_out, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in root.rglob('*'):
                if file.is_file():
                    zf.write(file, file.relative_to(root).as_posix())

        tmp_out.replace(pptx_path)
        return len(slides_def), backup


def main():
    n, backup = add_quality_slides(PPTX_PATH)
    print(f'Added {n} slides to {PPTX_PATH}')
    print(f'Backup: {backup}')


if __name__ == '__main__':
    main()
