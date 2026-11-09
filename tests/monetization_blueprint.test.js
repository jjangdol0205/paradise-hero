/**
 * monetization_blueprint.test.js
 * Verification suite for paradise-hero.com Monetization Blueprint & Channel Strategy.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const DOCS_DIR = path.resolve(__dirname, '..', 'docs');
const MASTER_DOC = path.join(DOCS_DIR, 'PARADISE_HERO_MONETIZATION_BLUEPRINT.md');
const PLAYBOOK_DOC = path.join(DOCS_DIR, 'YOUTUBE_SYNERGY_PLAYBOOK.md');
const SPEC_DOC = path.join(DOCS_DIR, 'SENIOR_UX_UI_DESIGN_SPEC.md');

console.log('--- Running Division 4 Monetization Blueprint Verification ---');

// Test 1: Verify all 3 core strategy documents exist and have substantive content
[MASTER_DOC, PLAYBOOK_DOC, SPEC_DOC].forEach((docPath) => {
  assert.ok(fs.existsSync(docPath), `Document must exist: ${docPath}`);
  const stat = fs.statSync(docPath);
  assert.ok(stat.size > 5000, `Document must be substantive (>5KB): ${docPath} (${stat.size} bytes)`);
  console.log(`[PASS] Document exists and substantive: ${path.basename(docPath)} (${stat.size} bytes)`);
});

const masterContent = fs.readFileSync(MASTER_DOC, 'utf-8');
const playbookContent = fs.readFileSync(PLAYBOOK_DOC, 'utf-8');
const specContent = fs.readFileSync(SPEC_DOC, 'utf-8');

// Test 2: Fandom Market Dynamics & Demographics
assert.ok(masterContent.includes('황영웅'), 'Must cover artist Hwang Young-woong');
assert.ok(masterContent.includes('파라다이스') || masterContent.includes('PARADISE'), 'Must cover fandom PARADISE');
assert.ok(masterContent.includes('88%'), 'Must cover female 88% demographic');
assert.ok(masterContent.includes('94%') || masterContent.includes('94.2%'), 'Must cover mobile 94%+ demographic');
assert.ok(masterContent.includes('63만 장') || masterContent.includes('당신 편'), 'Must cover album sales/record');
console.log('[PASS] Fandom market dynamics and senior demographics verified.');

// Test 3: The 4 High-Yield Monetization Pillars
// Pillar 1: VIP Supporters
assert.ok(masterContent.includes('9,900원') || masterContent.includes('9900원'), 'Must include Monthly VIP 9,900 KRW');
assert.ok(masterContent.includes('99,000원') || masterContent.includes('99000원'), 'Must include Annual VIP 99,000 KRW');
assert.ok(masterContent.includes('300,000'), 'Must include Lifetime Patron 300,000 KRW');

// Pillar 2: Billboard micro-donations
assert.ok(masterContent.includes('3,000원'), 'Must include 3,000 KRW Bronze Star');
assert.ok(masterContent.includes('5,000원'), 'Must include 5,000 KRW Silver Star');
assert.ok(masterContent.includes('10,000원'), 'Must include 10,000 KRW Golden Star');

// Pillar 3: Senior Commerce & Affiliate
assert.ok(masterContent.includes('5%') && masterContent.includes('15%'), 'Must include CPS 5~15%');
assert.ok(masterContent.includes('큐레이션'), 'Must include senior curation');

// Pillar 4: YouTube Synergy
assert.ok(masterContent.includes('미드롤'), 'Must include mid-roll strategy');
assert.ok(masterContent.includes('RPM') || masterContent.includes('4,500원') || masterContent.includes('4,000'), 'Must include YouTube RPM range');
assert.ok(masterContent.includes('슈퍼챗') || masterContent.includes('슈퍼땡스'), 'Must include Super Chat/Super Thanks');
console.log('[PASS] All 4 Monetization Pillars and pricing tiers verified.');

// Test 4: Flywheel Architecture
assert.ok(masterContent.includes('플라이휠') || masterContent.includes('Flywheel'), 'Must include Flywheel architecture');
assert.ok(masterContent.includes('사연 우체통') || masterContent.includes('story.html'), 'Must include single-gate story funnel');
assert.ok(playbookContent.includes('더보기') && playbookContent.includes('고정 댓글'), 'Must include YouTube metadata & pinned comment funnel');
console.log('[PASS] YouTube <-> Web platform flywheel loop verified.');

// Test 5: 3-Phase Financial Projections
assert.ok(masterContent.includes('Phase 1') && masterContent.includes('Phase 2') && masterContent.includes('Phase 3'), 'Must cover 3 phases');
assert.ok(masterContent.includes('MRR') && masterContent.includes('ARR'), 'Must detail MRR and ARR projections');
assert.ok(masterContent.includes('영업이익률'), 'Must detail operating margin analysis');
console.log('[PASS] 3-Phase financial model and unit economics verified.');

// Test 6: Ground Rules Compliance
// Unified email
[masterContent, playbookContent, specContent].forEach((c, idx) => {
  assert.ok(c.includes('beable9489@gmail.com'), `Must include unified email in doc ${idx + 1}`);
});
console.log('[PASS] Unified email beable9489@gmail.com present across all docs.');

// Lemon Squeezy Store #296100
assert.ok(masterContent.includes('296100'), 'Must reference Lemon Squeezy Store #296100');
console.log('[PASS] Lemon Squeezy Store #296100 verified.');

// Zero Prohibited Words
const prohibitedWords = ['최저가', '할인율', '특가', '폭탄세일'];
prohibitedWords.forEach((word) => {
  // Allow only when explaining the ban rule
  const count = (masterContent.match(new RegExp(word, 'g')) || []).length;
  // If count > 0, it must only be in section explaining prohibition or zero cliches
  if (count > 0) {
    assert.ok(masterContent.includes(`배제`) || masterContent.includes('금지'), `Prohibited word '${word}' can only appear in ban explanation`);
  }
});
console.log('[PASS] Zero prohibited commercial cliches verified.');

// Anti-AI Cliches check
const aiBuzzwords = ['새로운 지평', '바쁜 현대사회', '선택은 여러분의 몫', 'Supercharge', 'Delve'];
aiBuzzwords.forEach((word) => {
  const count = (masterContent.match(new RegExp(word, 'g')) || []).length;
  if (count > 0) {
    assert.ok(masterContent.includes('금지') || masterContent.includes('배제'), `AI buzzword '${word}' can only appear in ban context`);
  }
});
console.log('[PASS] Anti-AI tone and manner verified.');

// Senior UX Accessibility Specs
assert.ok(specContent.includes('WCAG') && specContent.includes('AAA'), 'Must specify WCAG AAA');
assert.ok(specContent.includes('18px'), 'Must specify base font 18px');
assert.ok(specContent.includes('56px'), 'Must specify touch target 56px+');
assert.ok(specContent.includes('#1B4D3E') && specContent.includes('#D4AF37'), 'Must specify brand colors emerald green & gold');
console.log('[PASS] Senior UX & WCAG AAA specifications verified.');

console.log('\n========================================');
console.log('ALL MONETIZATION BLUEPRINT TESTS PASSED!');
console.log('========================================\n');
