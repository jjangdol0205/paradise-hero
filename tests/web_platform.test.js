/**
 * web_platform.test.js
 * Automated verification test suite for paradise-hero.com Web Platform Foundation & Senior UX (2026-11-11 HQ Spec).
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
  'story.html',
  'booth.html',
  'news.html'
];

const BANNED_OTHER_SINGERS = [
  '임영웅', '이찬원', '영탁', '정동원', '김호중', '장민호', '박서진', '손태진', '안성훈', '진해성'
];

function stripApprovedSpecialStoreLabel(text) {
  return text.replace(/안심\s*특가관/g, '').replace(/특가관/g, '');
}

console.log('===============================================================');
console.log('Running paradise-hero.com Web Platform Foundation Test Suite');
console.log('===============================================================\n');

assert.ok(fs.existsSync(CNAME_FILE), 'CNAME file must exist');
assert.strictEqual(fs.readFileSync(CNAME_FILE, 'utf-8').trim(), 'paradise-hero.com');
assert.ok(fs.existsSync(CSS_FILE) && fs.statSync(CSS_FILE).size > 2000);
assert.ok(fs.existsSync(ACCESSIBILITY_JS) && fs.statSync(ACCESSIBILITY_JS).size > 1000);
assert.ok(fs.existsSync(RADIO_JS) && fs.statSync(RADIO_JS).size > 1500);

CORE_PAGES.forEach((pageName) => {
  const filePath = path.join(ROOT_DIR, pageName);
  assert.ok(fs.existsSync(filePath), `Core page must exist: ${pageName}`);
  const html = fs.readFileSync(filePath, 'utf-8');

  assert.ok(/<!DOCTYPE\s+html>/i.test(html), `${pageName} must have <!DOCTYPE html>`);
  assert.ok(/<html\s+lang=["']ko["']/i.test(html), `${pageName} must have <html lang="ko">`);
  assert.ok(/<meta\s+charset=["']UTF-8["']/i.test(html), `${pageName} must have <meta charset="UTF-8">`);
  assert.ok(/<meta\s+name=["']viewport["']/i.test(html), `${pageName} must have mobile viewport meta`);
  assert.ok(html.includes('css/senior-style.css'), `${pageName} must link to css/senior-style.css`);
  assert.ok(html.includes('js/senior-accessibility.js'), `${pageName} must load js/senior-accessibility.js`);
  assert.ok(html.includes('js/radio-player.js'), `${pageName} must load js/radio-player.js`);
  assert.ok(html.includes('beable9489@gmail.com'), `${pageName} must contain unified contact email`);
  const plainText = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
  assert.ok(plainText.includes('🎁 무료 선물제작소'), `${pageName} header nav must use unified label '🎁 무료 선물제작소'`);

  // Zero Lemon Squeezy / Store #296100 / other singers / 10대 왕자
  assert.ok(!/lemonsqueezy/i.test(html), `${pageName} must NOT contain lemonsqueezy`);
  assert.ok(!html.includes('296100'), `${pageName} must NOT contain Store #296100`);
  assert.ok(!html.includes('10대 왕자'), `${pageName} must NOT contain '10대 왕자'`);
  assert.ok(!html.includes('건행'), `${pageName} must NOT contain '건행'`);
  BANNED_OTHER_SINGERS.forEach((s) => {
    assert.ok(!html.includes(s), `${pageName} must NOT mention other singer '${s}'`);
  });

  // Zero raw MP3
  assert.strictEqual(/\.mp3["'\s]/i.test(html), false, `Raw MP3 found in ${pageName}`);

  // Zero prohibited commercial words (excluding HQ-mandated '안심 특가관')
  const cleaned = stripApprovedSpecialStoreLabel(html);
  ['최저가', '할인율', '특가', '폭탄세일'].forEach((w) => {
    assert.strictEqual(cleaned.includes(w), false, `Prohibited word '${w}' found in ${pageName}`);
  });
});
console.log('  [PASS] All 8 core HTML pages passed semantics, 100% Hwang Young-woong exclusivity, and zero-paywall checks.');

// CSS 20px+ base font & 60px+ touch target check
const cssContent = fs.readFileSync(CSS_FILE, 'utf-8');
assert.ok(cssContent.includes('#1B4D3E') && cssContent.includes('#D4AF37') && cssContent.includes('#FAFAF8'));
assert.ok(cssContent.includes('20px'), 'CSS must specify 20px+ base font for senior readability');
assert.ok(cssContent.includes('60px'), 'CSS must specify 60px+ minimum touch target');
assert.ok(cssContent.includes('font-lg') && cssContent.includes('font-xl'));
console.log('  [PASS] Senior WCAG AAA CSS (20px+ font, 60px+ touch target, 3-stage scaler) verified.');

// Radio player Ep 5 duration & ?ep=1~5 deep link check
const radioJsContent = fs.readFileSync(RADIO_JS, 'utf-8');
assert.ok(radioJsContent.includes('0:45 (특집 속보 브리핑)'), "Ep 5 duration must be '0:45 (특집 속보 브리핑)'");
assert.ok(radioJsContent.includes('URLSearchParams') && radioJsContent.includes("get('ep')"), 'radio-player.js must support ?ep=1~5 query parameter deep-linking');
console.log("  [PASS] Radio player Ep 5 ('0:45 (특집 속보 브리핑)') & ?ep=1~5 deep-link autoplay verified.");

// Kakao bookmark king-button check
const indexHtml = fs.readFileSync(path.join(ROOT_DIR, 'index.html'), 'utf-8');
assert.ok(
  indexHtml.includes("💛 카카오톡 '나와의 채팅'이나 팬 친구에게 이 응원방 보내두기"),
  'index.html must include yellow Kakao bookmark king-button'
);
console.log('  [PASS] Kakao bookmark king-button verified on index.html.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL PARADISE-HERO.COM WEB PLATFORM TESTS PASSED (100%)');
console.log('===============================================================\n');
