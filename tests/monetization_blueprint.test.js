/**
 * monetization_blueprint.test.js
 * Verification suite for paradise-hero.com Baek Woon-ho Virtual Singer & 7-Principles Blueprint.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const DOCS_DIR = path.resolve(__dirname, '..', 'docs');
const MASTER_DOC = path.join(DOCS_DIR, 'PARADISE_HERO_MONETIZATION_BLUEPRINT.md');
const PLAYBOOK_DOC = path.join(DOCS_DIR, 'YOUTUBE_SYNERGY_PLAYBOOK.md');
const SPEC_DOC = path.join(DOCS_DIR, 'SENIOR_UX_UI_DESIGN_SPEC.md');

const BANNED_HWANG = '\uD669\uC601\uC6C5';

console.log('--- Running Division 4 Baek Woon-ho Blueprint Verification ---');

[MASTER_DOC, PLAYBOOK_DOC, SPEC_DOC].forEach((docPath) => {
  assert.ok(fs.existsSync(docPath), `Document must exist: ${docPath}`);
  const stat = fs.statSync(docPath);
  assert.ok(stat.size > 5000, `Document must be substantive (>5KB): ${docPath} (${stat.size} bytes)`);
  console.log(`[PASS] Document exists and substantive: ${path.basename(docPath)} (${stat.size} bytes)`);
});

const masterContent = fs.readFileSync(MASTER_DOC, 'utf-8');
const playbookContent = fs.readFileSync(PLAYBOOK_DOC, 'utf-8');
const specContent = fs.readFileSync(SPEC_DOC, 'utf-8');

assert.ok(masterContent.includes('백운호'), 'Must cover virtual trot singer Baek Woon-ho');
assert.ok(masterContent.includes('어머니의 봄날'), 'Must cover title song 어머니의 봄날');
assert.ok(!masterContent.includes(BANNED_HWANG), 'Must NOT contain real celebrity name');
assert.ok(masterContent.includes('https://cshop.naver.com/paradiseshop'), 'Must document Naver Creator Shop URL');
assert.ok(masterContent.includes('AF7865143'), 'Must document Coupang Partners ID AF7865143');
assert.ok(!masterContent.includes('296' + '100'), 'Must NOT contain retired overseas Store');
assert.ok(playbookContent.includes('https://paradise-hero.com/booth.html'), 'Playbook pinned comment must include booth.html');
assert.ok(playbookContent.includes('https://cshop.naver.com/paradiseshop'), 'Playbook pinned comment must include cshop.naver.com/paradiseshop');

[masterContent, playbookContent, specContent].forEach((c, idx) => {
  assert.ok(c.includes('beable9489@gmail.com'), `Must include unified email in doc ${idx + 1}`);
  assert.ok(!c.includes(BANNED_HWANG), `Doc ${idx + 1} must have 0 real celebrity references`);
});

assert.ok(specContent.includes('WCAG') && specContent.includes('AAA'), 'Must specify WCAG AAA');
assert.ok(specContent.includes('#1B4D3E') && specContent.includes('#D4AF37'), 'Must specify brand colors emerald green & gold');

console.log('\n========================================');
console.log('ALL MONETIZATION BLUEPRINT TESTS PASSED!');
console.log('========================================\n');
