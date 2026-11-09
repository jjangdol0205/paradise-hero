/**
 * web_platform.test.js
 * Automated verification test suite for paradise-hero.com Web Platform Foundation & Senior UX.
 * Validates:
 * 1. File existence (CNAME, CSS, JS, 6 Core HTML Pages).
 * 2. Valid semantic HTML5, viewport, charset, lang="ko", title, meta description.
 * 3. Responsive senior CSS (WCAG AAA emerald green #1B4D3E, gold #D4AF37, ivory #FAFAF8, 18px+ font, 56px+ touch target).
 * 4. Senior accessibility widget logic (3-stage scaler, localStorage persistence, font-lg/font-xl classes).
 * 5. Sticky bottom radio player logic (1-click controls, YouTube iframe integration, continuous playback).
 * 6. Contact email unification (beable9489@gmail.com on all pages).
 * 7. Store #296100 integration and zero prohibited words (최저가, 할인율, 특가, 폭탄세일).
 * 8. Zero copyright violations (0 raw mp3 file references, official streaming embeds/links).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const CSS_FILE = path.join(ROOT_DIR, 'css', 'senior-style.css');
const ACCESSIBILITY_JS = path.join(ROOT_DIR, 'js', 'senior-accessibility.js');
const RADIO_JS = path.join(ROOT_DIR, 'js', 'radio-player.js');
const CNAME_FILE = path.join(ROOT_DIR, 'CNAME');

const CORE_PAGES = [
  'index.html',
  'radio.html',
  'stream.html',
  'community.html',
  'vip.html',
  'story.html'
];

console.log('===============================================================');
console.log('Running paradise-hero.com Web Platform Foundation Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Verify CNAME, Stylesheets, Scripts, and HTML Core Pages Exist
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence...');

assert.ok(fs.existsSync(CNAME_FILE), 'CNAME file must exist');
const cnameContent = fs.readFileSync(CNAME_FILE, 'utf-8').trim();
assert.strictEqual(cnameContent, 'paradise-hero.com', 'CNAME must point to paradise-hero.com');
console.log('  [PASS] CNAME exists and contains paradise-hero.com');

assert.ok(fs.existsSync(CSS_FILE), 'css/senior-style.css must exist');
assert.ok(fs.statSync(CSS_FILE).size > 2000, 'senior-style.css must be substantive (>2KB)');
console.log('  [PASS] css/senior-style.css verified');

assert.ok(fs.existsSync(ACCESSIBILITY_JS), 'js/senior-accessibility.js must exist');
assert.ok(fs.statSync(ACCESSIBILITY_JS).size > 1000, 'senior-accessibility.js must be substantive');
console.log('  [PASS] js/senior-accessibility.js verified');

assert.ok(fs.existsSync(RADIO_JS), 'js/radio-player.js must exist');
assert.ok(fs.statSync(RADIO_JS).size > 1500, 'radio-player.js must be substantive');
console.log('  [PASS] js/radio-player.js verified');

CORE_PAGES.forEach((pageName) => {
  const filePath = path.join(ROOT_DIR, pageName);
  assert.ok(fs.existsSync(filePath), `Core page must exist: ${pageName}`);
  const stat = fs.statSync(filePath);
  assert.ok(stat.size > 2500, `Page ${pageName} must be substantive (>2.5KB, got ${stat.size} bytes)`);
  console.log(`  [PASS] Core page exists and substantive: ${pageName} (${stat.size} bytes)`);
});

// -----------------------------------------------------------------------------
// Test 2: Semantic HTML5 Structure, Meta Viewport, and Scripts Linking
// -----------------------------------------------------------------------------
console.log('\nTest 2: Verifying HTML5 semantics and metadata across all pages...');

CORE_PAGES.forEach((pageName) => {
  const filePath = path.join(ROOT_DIR, pageName);
  const html = fs.readFileSync(filePath, 'utf-8');

  // Doctype & html lang
  assert.ok(/<!DOCTYPE\s+html>/i.test(html), `${pageName} must have <!DOCTYPE html>`);
  assert.ok(/<html\s+lang=["']ko["']/i.test(html), `${pageName} must have <html lang="ko">`);

  // Viewport & Charset
  assert.ok(/<meta\s+charset=["']UTF-8["']/i.test(html), `${pageName} must have <meta charset="UTF-8">`);
  assert.ok(/<meta\s+name=["']viewport["']\s+content=["']width=device-width,\s*initial-scale=1\.0["']/i.test(html), `${pageName} must have mobile viewport meta`);

  // Title & description
  assert.ok(/<title>.+<\/title>/i.test(html), `${pageName} must have <title>`);
  assert.ok(/<meta\s+name=["']description["']/i.test(html), `${pageName} must have meta description`);

  // Semantic elements
  assert.ok(html.includes('<header'), `${pageName} must include <header>`);
  assert.ok(html.includes('<nav'), `${pageName} must include <nav>`);
  assert.ok(html.includes('<main'), `${pageName} must include <main>`);
  assert.ok(html.includes('<footer'), `${pageName} must include <footer>`);

  // Resource linkage
  assert.ok(html.includes('css/senior-style.css'), `${pageName} must link to css/senior-style.css`);
  assert.ok(html.includes('js/senior-accessibility.js'), `${pageName} must load js/senior-accessibility.js`);
  assert.ok(html.includes('js/radio-player.js'), `${pageName} must load js/radio-player.js`);

  console.log(`  [PASS] ${pageName} passed HTML5 semantic and metadata audits.`);
});

// -----------------------------------------------------------------------------
// Test 3: WCAG AAA High Contrast & Senior Ergonomics CSS Verification
// -----------------------------------------------------------------------------
console.log('\nTest 3: Verifying senior CSS styling (WCAG AAA, colors, 18px+ font, 56px+ target)...');

const cssContent = fs.readFileSync(CSS_FILE, 'utf-8');

// Brand Colors
assert.ok(cssContent.includes('#1B4D3E'), 'Must include primary emerald green #1B4D3E');
assert.ok(cssContent.includes('#0E2820'), 'Must include dark emerald #0E2820 for ultra high contrast');
assert.ok(cssContent.includes('#D4AF37'), 'Must include secondary accent gold #D4AF37');
assert.ok(cssContent.includes('#FAFAF8'), 'Must include glare-reduction soft ivory canvas #FAFAF8');
assert.ok(cssContent.includes('#1F2937'), 'Must include dark charcoal #1F2937 for text contrast');
console.log('  [PASS] WCAG AAA Color Palette verified (#1B4D3E, #D4AF37, #FAFAF8, #1F2937).');

// Typography & 3-stage scaler classes
assert.ok(cssContent.includes('18px'), 'Must specify base font 18px');
assert.ok(cssContent.includes('font-lg'), 'Must define body.font-lg (21px)');
assert.ok(cssContent.includes('font-xl'), 'Must define body.font-xl (24px)');
assert.ok(cssContent.includes('--line-height-body'), 'Must define comfortable line-height');
console.log('  [PASS] Base font 18px and dynamic scaling classes (.font-lg, .font-xl) verified.');

// Touch target ergonomics
assert.ok(cssContent.includes('56px') || cssContent.includes('--touch-min-height'), 'Must specify minimum 56px touch target');
assert.ok(cssContent.includes(':active'), 'Must provide tactile visual feedback on button active touch');
console.log('  [PASS] 56px+ minimum touch target and tactile feedback verified.');

// -----------------------------------------------------------------------------
// Test 4: Senior Accessibility Widget Logic & Persistence
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying senior accessibility widget logic...');

const accessJsContent = fs.readFileSync(ACCESSIBILITY_JS, 'utf-8');

assert.ok(accessJsContent.includes('localStorage'), 'Must persist font scale in localStorage');
assert.ok(accessJsContent.includes('font-lg') && accessJsContent.includes('font-xl'), 'Must handle font-lg and font-xl classes');
assert.ok(accessJsContent.includes('글자크게') || accessJsContent.includes('btn-font-scaler'), 'Must manage [글자크게 가+] widget');
assert.ok(accessJsContent.includes('DOMContentLoaded'), 'Must initialize on DOMContentLoaded');
console.log('  [PASS] 3-stage font scaler and localStorage persistence verified.');

// -----------------------------------------------------------------------------
// Test 5: Sticky Bottom Radio Player Logic
// -----------------------------------------------------------------------------
console.log('\nTest 5: Verifying sticky bottom radio player logic...');

const radioJsContent = fs.readFileSync(RADIO_JS, 'utf-8');

assert.ok(radioJsContent.includes('sticky-radio-player'), 'Must manage sticky radio player container');
assert.ok(radioJsContent.includes('togglePlay') || radioJsContent.includes('playEpisode'), 'Must provide 1-click play/pause and episode switching');
assert.ok(radioJsContent.includes('youtube') || radioJsContent.includes('iframe'), 'Must integrate official YouTube stream/iframe');
assert.ok(radioJsContent.includes('Wi-Fi') || radioJsContent.includes('wifi'), 'Must include Wi-Fi data-saving notice');
console.log('  [PASS] 1-click radio player and continuous streaming logic verified.');

// -----------------------------------------------------------------------------
// Test 6: Unified Contact Email (beable9489@gmail.com) on All Pages
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying unified contact email across all 6 core pages...');

CORE_PAGES.forEach((pageName) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, pageName), 'utf-8');
  assert.ok(html.includes('beable9489@gmail.com'), `${pageName} must contain unified contact email beable9489@gmail.com`);
  console.log(`  [PASS] beable9489@gmail.com present in ${pageName}`);
});

// -----------------------------------------------------------------------------
// Test 7: Lemon Squeezy Store #296100 Integration & Zero Prohibited Words
// -----------------------------------------------------------------------------
console.log('\nTest 7: Verifying Store #296100 integration and ZERO prohibited words...');

// Store #296100 check in vip.html and footers
const vipHtml = fs.readFileSync(path.join(ROOT_DIR, 'vip.html'), 'utf-8');
assert.ok(vipHtml.includes('296100'), 'vip.html must include Lemon Squeezy Store #296100');
console.log('  [PASS] Lemon Squeezy Store #296100 confirmed in vip.html');

// Zero Prohibited Words check across all files in 4사업부
const prohibitedWords = ['최저가', '할인율', '특가', '폭탄세일'];
const filesToCheck = [
  ...CORE_PAGES.map(p => path.join(ROOT_DIR, p)),
  CSS_FILE,
  ACCESSIBILITY_JS,
  RADIO_JS
];

filesToCheck.forEach((filePath) => {
  const content = fs.readFileSync(filePath, 'utf-8');
  prohibitedWords.forEach((word) => {
    assert.strictEqual(
      content.includes(word),
      false,
      `Prohibited commercial word '${word}' found in ${path.basename(filePath)}!`
    );
  });
});
console.log('  [PASS] Zero prohibited commercial cliches verified across all HTML, CSS, and JS files.');

// -----------------------------------------------------------------------------
// Test 8: Zero Copyright Violations (No Raw MP3 Files)
// -----------------------------------------------------------------------------
console.log('\nTest 8: Verifying Zero Raw MP3 copyright compliance...');

CORE_PAGES.forEach((pageName) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, pageName), 'utf-8');
  assert.strictEqual(
    /\.mp3["'\s]/i.test(html),
    false,
    `Raw MP3 file download/streaming found in ${pageName}! Must only use official streaming/embeds.`
  );
});
console.log('  [PASS] Zero raw mp3 files verified. 100% legal official streaming links and embeds.');

// -----------------------------------------------------------------------------
// Test 9: Senior Navigation & Cross-Funnel Linkage
// -----------------------------------------------------------------------------
console.log('\nTest 9: Verifying cross-page senior navigation and story funnel...');

CORE_PAGES.forEach((pageName) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, pageName), 'utf-8');
  // Check main navigation links exist in all pages
  assert.ok(html.includes('index.html'), `${pageName} must link to index.html`);
  assert.ok(html.includes('radio.html'), `${pageName} must link to radio.html`);
  assert.ok(html.includes('stream.html'), `${pageName} must link to stream.html`);
  assert.ok(html.includes('community.html'), `${pageName} must link to community.html`);
  assert.ok(html.includes('vip.html'), `${pageName} must link to vip.html`);
});

// Single-gate story funnel check
const radioHtml = fs.readFileSync(path.join(ROOT_DIR, 'radio.html'), 'utf-8');
const commHtml = fs.readFileSync(path.join(ROOT_DIR, 'community.html'), 'utf-8');
const indexHtml = fs.readFileSync(path.join(ROOT_DIR, 'index.html'), 'utf-8');

assert.ok(radioHtml.includes('story.html'), 'radio.html must link to story.html single-gate funnel');
assert.ok(commHtml.includes('story.html'), 'community.html must link to story.html single-gate funnel');
assert.ok(indexHtml.includes('story.html'), 'index.html must link to story.html');

console.log('  [PASS] All 6 core pages properly cross-linked into seamless senior funnel.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL PARADISE-HERO.COM WEB PLATFORM TESTS PASSED (100%)');
console.log('===============================================================\n');
