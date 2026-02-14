const pptxgen = require('pptxgenjs');
const path = require('path');
const html2pptx = require('/Users/eveyhuang/.claude/plugins/cache/anthropic-agent-skills/document-skills/69c0b1a06741/skills/pptx/scripts/html2pptx');

const SLIDES_DIR = path.join(__dirname, 'slides');
const FIGURES_DIR = path.join(__dirname, '..', 'results', 'figures');
const OUTPUT = path.join(__dirname, '..', 'results', 'diversity_analysis_presentation.pptx');

async function build() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'Diversity Analysis';
  pptx.title = 'AI vs Human Research Proposal Diversity Analysis';

  // Slide 1: Title
  await html2pptx(path.join(SLIDES_DIR, 'slide01-title.html'), pptx);
  console.log('Slide 1: Title done');

  // Slide 2: Study Design
  await html2pptx(path.join(SLIDES_DIR, 'slide02-overview.html'), pptx);
  console.log('Slide 2: Study Design done');

  // Slide 3: Methodology
  await html2pptx(path.join(SLIDES_DIR, 'slide03-methods.html'), pptx);
  console.log('Slide 3: Methodology done');

  // Slide 4: Pairwise Diversity with chart
  {
    const { slide, placeholders } = await html2pptx(path.join(SLIDES_DIR, 'slide04-pairwise.html'), pptx);
    if (placeholders.length > 0) {
      const p = placeholders[0];
      slide.addChart(pptx.charts.BAR, [{
        name: "Cliff's Delta",
        labels: ["All AI", "Claude", "Gemini", "GPT-5.2"],
        values: [-0.290, 0.248, -0.726, -1.000]
      }], {
        x: p.x, y: p.y, w: p.w, h: p.h,
        barDir: 'col',
        showTitle: false,
        showLegend: false,
        showCatAxisTitle: false,
        showValAxisTitle: true,
        valAxisTitle: "Cliff's Delta",
        valAxisMinVal: -1.1,
        valAxisMaxVal: 0.4,
        valAxisMajorUnit: 0.25,
        catAxisLabelFontSize: 8,
        valAxisLabelFontSize: 8,
        valAxisTitleFontSize: 8,
        chartColors: ["1B2A4A", "5D6D7E", "8E44AD", "E67E22"],
        dataLabelPosition: 'outEnd',
        dataLabelFontSize: 7,
        showValue: true,
        dataLabelColor: '2C3E50'
      });
    }
    console.log('Slide 4: Pairwise done');
  }

  // Slide 5: Centroid Dispersion with chart
  {
    const { slide, placeholders } = await html2pptx(path.join(SLIDES_DIR, 'slide05-centroid.html'), pptx);
    if (placeholders.length > 0) {
      const p = placeholders[0];
      slide.addChart(pptx.charts.BAR, [{
        name: 'Mean Distance to Centroid',
        labels: ["Human", "Claude", "Gemini", "GPT-5.2"],
        values: [0.032, 0.179, 0.047, 0.010]
      }], {
        x: p.x, y: p.y, w: p.w, h: p.h,
        barDir: 'col',
        showTitle: false,
        showLegend: false,
        showCatAxisTitle: false,
        showValAxisTitle: true,
        valAxisTitle: 'Mean Cosine Distance',
        valAxisMinVal: 0,
        valAxisMaxVal: 0.2,
        valAxisMajorUnit: 0.05,
        catAxisLabelFontSize: 8,
        valAxisLabelFontSize: 8,
        valAxisTitleFontSize: 8,
        chartColors: ["E74C3C", "5D6D7E", "8E44AD", "E67E22"],
        dataLabelPosition: 'outEnd',
        dataLabelFontSize: 7,
        showValue: true,
        dataLabelColor: '2C3E50'
      });
    }
    console.log('Slide 5: Centroid done');
  }

  // Slide 6: Nearest-Neighbor with chart
  {
    const { slide, placeholders } = await html2pptx(path.join(SLIDES_DIR, 'slide06-nn.html'), pptx);
    if (placeholders.length > 0) {
      const p = placeholders[0];
      // Stacked bar chart for NN origins
      slide.addChart(pptx.charts.BAR, [
        {
          name: 'Same Group',
          labels: ["Human", "Claude", "Gemini", "GPT-5.2"],
          values: [43.5, 95.7, 69.6, 69.6]
        },
        {
          name: 'Other AI Model',
          labels: ["Human", "Claude", "Gemini", "GPT-5.2"],
          values: [0, 4.3, 30.4, 30.4]
        },
        {
          name: 'Different Group Type',
          labels: ["Human", "Claude", "Gemini", "GPT-5.2"],
          values: [56.5, 0, 0, 0]
        }
      ], {
        x: p.x, y: p.y, w: p.w, h: p.h,
        barDir: 'bar',
        barGrouping: 'stacked',
        showTitle: false,
        showLegend: true,
        legendPos: 'b',
        legendFontSize: 6,
        showCatAxisTitle: false,
        showValAxisTitle: true,
        valAxisTitle: '% of Proposals',
        valAxisMinVal: 0,
        valAxisMaxVal: 100,
        catAxisLabelFontSize: 7,
        valAxisLabelFontSize: 7,
        valAxisTitleFontSize: 7,
        chartColors: ["2E86AB", "B0C4DE", "E8505B"]
      });
    }
    console.log('Slide 6: NN done');
  }

  // Slide 7: UMAP with image
  {
    const { slide, placeholders } = await html2pptx(path.join(SLIDES_DIR, 'slide07-umap.html'), pptx);
    if (placeholders.length > 0) {
      const p = placeholders[0];
      slide.addImage({
        path: path.join(FIGURES_DIR, 'embedding_space_2d.png'),
        x: p.x, y: p.y, w: p.w, h: p.h
      });
    }
    console.log('Slide 7: UMAP done');
  }

  // Slide 8: Summary table
  {
    const { slide, placeholders } = await html2pptx(path.join(SLIDES_DIR, 'slide08-summary.html'), pptx);
    if (placeholders.length > 0) {
      const p = placeholders[0];
      const headerStyle = { fill: { color: "1B2A4A" }, color: "FFFFFF", bold: true, fontSize: 9, align: 'center', valign: 'middle' };
      const cellStyle = { fontSize: 9, align: 'center', valign: 'middle', border: { pt: 0.5, color: "CCCCCC" } };
      const humanRow = { fill: { color: "FDF0F0" }, fontSize: 9, align: 'center', valign: 'middle', border: { pt: 0.5, color: "CCCCCC" } };
      const altRow = { fill: { color: "F0F4F8" }, fontSize: 9, align: 'center', valign: 'middle', border: { pt: 0.5, color: "CCCCCC" } };

      slide.addTable([
        [
          { text: "Group", options: headerStyle },
          { text: "Pairwise Diversity", options: headerStyle },
          { text: "Centroid Dispersion", options: headerStyle },
          { text: "NN Distance", options: headerStyle },
          { text: "Outlier Rate", options: headerStyle },
          { text: "Overall Pattern", options: headerStyle }
        ],
        [
          { text: "Human (baseline)", options: { ...humanRow, bold: true } },
          { text: "---", options: humanRow },
          { text: "---", options: humanRow },
          { text: "---", options: humanRow },
          { text: "13.0%", options: humanRow },
          { text: "Moderate diversity, genuine outliers", options: { ...humanRow, align: 'left', fontSize: 8 } }
        ],
        [
          { text: "Claude Opus 4.5", options: { ...altRow, bold: true } },
          { text: "+0.25 (small) ***", options: altRow },
          { text: "+0.99 (large) ***", options: altRow },
          { text: "-1.00 (large) ***", options: altRow },
          { text: "0.0%", options: altRow },
          { text: "High spread, subcluster pattern", options: { ...altRow, align: 'left', fontSize: 8 } }
        ],
        [
          { text: "Gemini 3 Pro", options: { ...cellStyle, bold: true } },
          { text: "-0.73 (large) ***", options: cellStyle },
          { text: "-0.82 (large) ***", options: cellStyle },
          { text: "-0.76 (large) ***", options: cellStyle },
          { text: "4.3%", options: cellStyle },
          { text: "Low diversity, moderate clustering", options: { ...cellStyle, align: 'left', fontSize: 8 } }
        ],
        [
          { text: "GPT-5.2", options: { ...altRow, bold: true } },
          { text: "-1.00 (large) ***", options: altRow },
          { text: "-1.00 (large) ***", options: altRow },
          { text: "+0.06 (negl.) ns", options: altRow },
          { text: "26.1%", options: altRow },
          { text: "Near-identical, isolated cluster", options: { ...altRow, align: 'left', fontSize: 8 } }
        ]
      ], {
        x: p.x, y: p.y, w: p.w,
        colW: [1.2, 1.3, 1.3, 1.3, 0.8, 2.2],
        rowH: [0.35, 0.35, 0.35, 0.35, 0.35],
        border: { pt: 0.5, color: "CCCCCC" }
      });
    }
    console.log('Slide 8: Summary table done');
  }

  // Slide 9: Key Findings
  await html2pptx(path.join(SLIDES_DIR, 'slide09-findings.html'), pptx);
  console.log('Slide 9: Key Findings done');

  // Slide 10: Implications
  await html2pptx(path.join(SLIDES_DIR, 'slide10-implications.html'), pptx);
  console.log('Slide 10: Implications done');

  // Save
  await pptx.writeFile({ fileName: OUTPUT });
  console.log(`\nPresentation saved to: ${OUTPUT}`);
}

build().catch(err => {
  console.error('Build failed:', err);
  process.exit(1);
});
