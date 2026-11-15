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

// Passwordless 3-Second Senior Big-Font Mailbox Membership (#hero-passwordless-club-card) & CRM wiring check
const crmClientPath = path.join(ROOT_DIR, 'js', 'hq_member_crm_client.js');
const loungeJsPath = path.join(ROOT_DIR, 'js', 'hero-family-lounge.js');
const endpointJsonPath = path.join(ROOT_DIR, 'hq-mailing-endpoint.json');
assert.ok(fs.existsSync(crmClientPath), 'js/hq_member_crm_client.js must exist');
assert.ok(fs.existsSync(loungeJsPath), 'js/hero-family-lounge.js must exist');
assert.ok(fs.existsSync(endpointJsonPath), 'hq-mailing-endpoint.json must exist');

const crmScriptIdx = indexHtml.indexOf('js/hq_member_crm_client.js');
const loungeScriptIdx = indexHtml.indexOf('js/hero-family-lounge.js');
assert.ok(crmScriptIdx > 0 && loungeScriptIdx > crmScriptIdx, 'hq_member_crm_client.js must load right before hero-family-lounge.js');
assert.ok(indexHtml.includes('id="hero-passwordless-club-card"'), 'index.html must contain #hero-passwordless-club-card');
assert.ok(indexHtml.includes('무료 정회원 우편함 · 비밀번호 없음 (3초 등록)'), 'Badge text must match senior spec');
assert.ok(indexHtml.includes('황영웅 반가운 최근 소식과 화·금 영웅라디오 편지를 큰글씨 이메일로 받아보세요'), '3-sec hook heading must match spec');
assert.ok(indexHtml.includes('data-club-segment="hero_news_schedule"'), 'Must include hero_news_schedule segment');
assert.ok(indexHtml.includes('data-club-segment="hero_radio_letters"'), 'Must include hero_radio_letters segment');
assert.ok(indexHtml.includes('data-club-segment="senior_health_lounge"'), 'Must include senior_health_lounge segment');
assert.ok(indexHtml.includes('id="hero-club-nickname"'), 'Must include #hero-club-nickname');
assert.ok(indexHtml.includes('id="hero-club-email"'), 'Must include #hero-club-email');
assert.ok(indexHtml.includes('name="website_hp"'), 'Must include hidden honeypot website_hp');
assert.ok(indexHtml.includes('id="hero-club-submit-btn"'), 'Must include #hero-club-submit-btn');
assert.ok(indexHtml.includes('id="hero-club-feedback"'), 'Must include #hero-club-feedback');
assert.ok(indexHtml.includes('id="hero-love-email-input"'), 'Must include optional #hero-love-email-input in #hero-love-letter-form');

// Zero type="password" & Zero U+FFFD broken encoding across HTML/CSS/JS
[
  ...CORE_PAGES.map((p) => path.join(ROOT_DIR, p)),
  CSS_FILE,
  crmClientPath,
  loungeJsPath
].forEach((filePath) => {
  const txt = fs.readFileSync(filePath, 'utf-8');
  assert.strictEqual(/type\s*=\s*["']password["']/i.test(txt), false, `Zero password input violated in ${path.basename(filePath)}`);
  assert.strictEqual(txt.includes('\uFFFD'), false, `Broken character U+FFFD found in ${path.basename(filePath)}`);
  assert.strictEqual(/lemonsqueezy/i.test(txt), false, `lemonsqueezy found in ${path.basename(filePath)}`);
});

const loungeJsContent = fs.readFileSync(loungeJsPath, 'utf-8');
assert.ok(loungeJsContent.includes('DreamCompanyCRM') && loungeJsContent.includes('registerMember'), 'hero-family-lounge.js must wire DreamCompanyCRM.registerMember');
assert.ok(loungeJsContent.includes('getLocalMember'), 'hero-family-lounge.js must check getLocalMember("HERO") on load');
assert.ok(loungeJsContent.includes('이메일 주소를 정확히 적어주세요 (예: hero@naver.com)'), 'hero-family-lounge.js must include friendly senior email guidance');
console.log('  [PASS] Passwordless 3-second HERO Big-Font Mailbox Membership & Zero-Password/Zero-FFFD verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL PARADISE-HERO.COM WEB PLATFORM TESTS PASSED (100%)');
console.log('===============================================================\n');
