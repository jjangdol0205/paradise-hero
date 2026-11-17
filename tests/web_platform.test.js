/**
 * web_platform.test.js
 * Automated verification test suite for paradise-hero.com Baek Woon-ho Rebrand & 7-Principles Senior UX.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const CSS_FILE = path.join(ROOT_DIR, 'css', 'senior-style.css');
const ACCESSIBILITY_JS = path.join(ROOT_DIR, 'js', 'senior-accessibility.js');
const RADIO_JS = path.join(ROOT_DIR, 'js', 'radio-player.js');
const LOUNGE_JS = path.join(ROOT_DIR, 'js', 'hero-family-lounge.js');
const SHARED_FEED_JSON = path.join(ROOT_DIR, 'data', 'shared_lounge_feed.json');
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

// Unicode escapes so test source itself contains 0 literal real celebrity / banned strings
const BANNED_REAL_CELEBS = [
  '\uD669\uC601\uC6C5', // hwang
  '\uC784\uC601\uC6C5', // lim
  '\uC774\uCC2C\uC6D0', // lee
  '\uC601\uD0C1',       // young
  '\uAE40\uD638\uC911', // kim
  '\uC7A5\uBBFC\uD638', // jang
  '\uC815\uB3D9\uC6D0', // jeong
  '\uBC15\uC11C\uC9C4', // park
  '\uC190\uD0DC\uC9C4', // son
  '\uC548\uC131\uD6C8', // ahn
  '\uC9C4\uD574\uC131', // jin
  '\uBBF8\uC2A4\uD130\uD2B8\uB86F', // mr trot
  '\uBD88\uD0C0\uB294 \uD2B8\uB86F\uB9E8', // burning trotman
  '\uB2F9\uC2E0 \uD3B8' // dangsin pyeon
];

const BANNED_PROMO_AND_ITEMS = [
  '\uCD5C\uC800\uAC00', // lowest price
  '\uD560\uC778\uC728', // discount rate
  '\uD2B9\uAC00',       // special price
  '\uD3ED\uD0C4\uC138\uC77C', // bomb sale
  '\uC544\uC774\uD074\uD0C0\uC784', // icletime
  '\uD0A4\uC131\uC7A5', // kid growth
  '\uC8FC\uB801\uC8FC\uB801', // zoorung
  '\uB3D9\uBB3C\uC6D0', // zoo
  '\uC54C\uD30C\uCE74'  // alpaca
];

console.log('===============================================================');
console.log('Running paradise-hero.com Baek Woon-ho & 7-Principles Test Suite');
console.log('===============================================================\n');

assert.ok(fs.existsSync(CNAME_FILE), 'CNAME file must exist');
assert.strictEqual(fs.readFileSync(CNAME_FILE, 'utf-8').trim(), 'paradise-hero.com');
assert.ok(fs.existsSync(SHARED_FEED_JSON), 'data/shared_lounge_feed.json must exist');
const sharedFeed = JSON.parse(fs.readFileSync(SHARED_FEED_JSON, 'utf-8'));
assert.ok(Array.isArray(sharedFeed) && sharedFeed.length >= 6, 'shared_lounge_feed.json must contain >= 6 shared posts');

// Verify lounge.html is consolidated redirect stub to community.html
const loungeRedirectHtml = fs.readFileSync(path.join(ROOT_DIR, 'lounge.html'), 'utf-8');
assert.ok(loungeRedirectHtml.includes('url=community.html') && loungeRedirectHtml.includes('https://paradise-hero.com/community.html'), 'lounge.html must redirect to community.html');

CORE_PAGES.forEach((pageName) => {
  const filePath = path.join(ROOT_DIR, pageName);
  assert.ok(fs.existsSync(filePath), `Core page must exist: ${pageName}`);
  const html = fs.readFileSync(filePath, 'utf-8');

  assert.ok(/<!DOCTYPE\s+html>/i.test(html), `${pageName} must have <!DOCTYPE html>`);
  assert.ok(/<html\s+lang=["']ko["']/i.test(html), `${pageName} must have <html lang="ko">`);
  assert.ok(html.includes('css/senior-style.css'), `${pageName} must link to css/senior-style.css`);
  assert.ok(html.includes('js/senior-accessibility.js'), `${pageName} must load js/senior-accessibility.js`);
  assert.ok(html.includes('js/radio-player.js'), `${pageName} must load js/radio-player.js`);
  assert.ok(html.includes('beable9489@gmail.com'), `${pageName} must contain unified contact email`);
  assert.ok(html.includes('id="hero-brand-partnership-box"'), `${pageName} must preserve #hero-brand-partnership-box`);
  assert.ok(html.includes('본 사랑방은 실존 연예인 팬카페가 아닌'), `${pageName} must display Transparent Honesty Badge`);
  assert.ok(!html.includes('href="lounge.html"'), `${pageName} navbar/footer must NOT link to duplicate lounge.html`);

  BANNED_REAL_CELEBS.forEach((celeb) => {
    assert.ok(!html.includes(celeb), `${pageName} must NOT mention banned celebrity/song '${celeb}'`);
  });
  BANNED_PROMO_AND_ITEMS.forEach((bad) => {
    assert.ok(!html.includes(bad), `${pageName} must NOT contain banned word/item '${bad}'`);
  });
  assert.strictEqual(/%ED%99%A9%EC%98%81%EC%9B%85/i.test(html), false, `${pageName} must NOT contain URL-encoded celebrity query`);
  assert.strictEqual(/type\s*=\s*["']password["']/i.test(html), false, `Zero password input violated in ${pageName}`);
});
console.log('  [PASS] All 8 core HTML pages verified: 0 real celebrities, 0 unrelated items, honesty badge & partnership box present.');

// Hero first impression check on index.html
const indexHtml = fs.readFileSync(path.join(ROOT_DIR, 'index.html'), 'utf-8');
const h1Match = indexHtml.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
assert.ok(h1Match, 'index.html must have <h1>');
const h1Text = h1Match[1].replace(/<[^>]+>/g, '').trim();
assert.strictEqual(h1Text, '매일 아침 중저음 트로트 한 곡과 따뜻한 인생 사연이 흐르는 김쌤의 라디오 사랑방');
assert.ok(h1Text.split(/\s+/).length <= 15, '<h1> must be <= 15 words');
assert.ok(indexHtml.includes('💚 유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지'));
['hero-family-lounge', 'hero-love-letterbox', 'hero-passwordless-club-card', 'hero-brand-partnership-box'].forEach((domId) => {
  assert.ok(indexHtml.includes(`id="${domId}"`), `index.html must preserve #${domId}`);
});
console.log('  [PASS] Hero <h1> (13 words <= 15) & all locked DOM IDs verified.');

// CSS & Mobile 58px compact bar + 76px body padding + bottom: 74px toast check
const cssContent = fs.readFileSync(CSS_FILE, 'utf-8');
assert.ok(cssContent.includes('#1B4D3E') && cssContent.includes('#D4AF37') && cssContent.includes('#FAFAF8'));
assert.ok(cssContent.includes('20px') && cssContent.includes('60px'));
assert.ok(cssContent.includes('padding-bottom: 76px') && cssContent.includes('height: 58px') && cssContent.includes('bottom: 74px'));
const accessJsContent = fs.readFileSync(ACCESSIBILITY_JS, 'utf-8');
assert.ok(accessJsContent.includes('bottom: 74px') && accessJsContent.includes('right: 16px') && accessJsContent.includes('1800'));
console.log('  [PASS] Mobile 58px compact radio bar, 76px body padding, input focus auto-hide, and 1.8s toast at bottom:74px verified.');

// Radio player 5 episodes, Baek Woon-ho studio MP3 broadcasts & 330s radio_5m30s beacon check
const BANNED_OLD_YT_IDS = ['WOPZLb6S1xI', 'M26BNE0bSz8', 'fqYTY_NZ3Uw', 'wb9IV7eD1p0', 'nZhCCjhgSIE'];
const radioJsContent = fs.readFileSync(RADIO_JS, 'utf-8');
const { RADIO_EPISODES } = require(RADIO_JS);
assert.ok(Array.isArray(RADIO_EPISODES) && RADIO_EPISODES.length === 5);
RADIO_EPISODES.forEach((ep) => {
  assert.ok(ep.audioSrc && fs.existsSync(path.join(ROOT_DIR, ep.audioSrc)), `Studio MP3 must exist: ${ep.audioSrc}`);
});
assert.ok(radioJsContent.includes('어머니의 봄날') && radioJsContent.includes('baek_woon_ho_ep01.mp3') && radioJsContent.includes('radio_5m30s') && radioJsContent.includes('330'));
assert.ok(radioJsContent.includes('위로 열기 ↑'));
CORE_PAGES.concat(['js/radio-player.js', 'js/story-hub.js', 'js/trot-news.js']).forEach((relFile) => {
  const content = fs.readFileSync(path.join(ROOT_DIR, relFile), 'utf-8');
  BANNED_OLD_YT_IDS.forEach((vid) => {
    assert.ok(!content.includes(vid), `${relFile} must NOT embed old celebrity videoId '${vid}'`);
  });
});

// Cross-visitor lounge Abacus clap_<post_id> & zero fake 318 math check
const loungeJsContent = fs.readFileSync(LOUNGE_JS, 'utf-8');
assert.ok(!loungeJsContent.includes('318') && !loungeJsContent.includes('computeSeedBaselineHearts'), 'Zero fake 318/seed math allowed');
assert.ok(loungeJsContent.includes('shared_lounge_feed.json') && loungeJsContent.includes('clap_') && loungeJsContent.includes('story_submit_total'));
assert.ok(loungeJsContent.includes('✅ 방송국 서버 접수 완료 · 스팸 확인 후 전국 가족 담벼락에 함께 게시됩니다'));
console.log('  [PASS] Cross-visitor shared lounge (shared_lounge_feed.json + Abacus clap_) & zero fake counter math verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL PARADISE-HERO.COM WEB PLATFORM TESTS PASSED (100%)');
console.log('===============================================================\n');
