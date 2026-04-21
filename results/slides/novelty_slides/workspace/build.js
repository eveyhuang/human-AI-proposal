const pptxgen = require('/opt/homebrew/lib/node_modules/pptxgenjs');
const html2pptx = require('/Users/eveyhuang/.claude/plugins/marketplaces/anthropic-agent-skills/skills/pptx/scripts/html2pptx');
const path = require('path');

const WORKSPACE = path.resolve(__dirname);

async function build() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.title = 'Novelty Reviews of AI vs. Human Research Proposals';
    pptx.subject = 'Part IV Quality Analysis — Style-Controlled Condition';

    const slides = [
        'slide01.html',
        'slide02.html',
        'slide03.html',
        'slide04.html',
        'slide05.html',
        'slide06.html',
        'slide07.html',
        'slide08.html',
        'slide09.html',
        'slide10.html',
        'slide11.html',
    ];

    for (const fname of slides) {
        const fpath = path.join(WORKSPACE, fname);
        console.log(`Processing ${fname}...`);
        try {
            await html2pptx(fpath, pptx);
        } catch (err) {
            console.error(`ERROR on ${fname}:`, err.message);
            process.exit(1);
        }
    }

    const outPath = path.join(WORKSPACE, '..', 'novelty_review_analysis.pptx');
    await pptx.writeFile({ fileName: outPath });
    console.log(`\nSaved: ${outPath}`);
}

build().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
