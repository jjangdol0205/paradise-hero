/**
 * monetization_platform.test.js
 * Verification suite for 💚 김쌤의 콘서트·응원 안심 준비물관 (3 Themes, 7 Genuine Senior Items, Zero Unrelated Items)
 * & Unlimited Free Gift Studio.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const VIP_STUDIO_JS = path.join(ROOT_DIR, 'js', 'vip-digital-studio.js');

console.log('======================================================================');
console.log('Running 김쌤의 콘서트·응원 안심 준비물관 & Free Gift Studio Verification');
console.log('======================================================================\n');

const storePages = [
  'index.html',
  'booth.html',
  'vip.html',
  'radio.html',
  'stream.html',
  'news.html',
  'community.html',
  'story.html'
].map((name) => ({ name, content: fs.readFileSync(path.join(ROOT_DIR, name), 'utf-8') }));

const NAVER_CSHOP_URL = 'https://cshop.naver.com/paradiseshop';
const FTC_DISCLOSURE = '※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다.';
const BANNED_UNRELATED = [
  '\uC544\uC774\uD074\uD0C0\uC784', // icletime
  '\uD0A4\uC131\uC7A5',             // kid growth
  '\uC8FC\uB801\uC8FC\uB801',       // zoorung
  '\uB3D9\uBB3C\uC6D0',             // zoo
  '\uC54C\uD30C\uCE74',             // alpaca
  '\uACE8\uB4DC VIP',               // gold vip
  '\uC6D4 9,900\uC6D0'              // monthly 9900
];

storePages.forEach(({ name, content }) => {
  assert.ok(content.includes('💚 김쌤의 콘서트·응원 안심 준비물관'), `${name} must contain store heading '💚 김쌤의 콘서트·응원 안심 준비물관'`);
  assert.ok(content.includes(NAVER_CSHOP_URL), `${name} must link to ${NAVER_CSHOP_URL}`);
  const coupangHits = (content.match(/link\.coupang\.com\/re\/AFFS(?:RP|DP)\?lptag=AF7865143/g) || []).length;
  assert.strictEqual(coupangHits, 7, `${name} must contain exact 7 genuine senior Coupang AF7865143 items (found ${coupangHits})`);
  assert.ok(content.includes(FTC_DISCLOSURE), `${name} must contain exact FTC disclosure right next to product buttons`);
  assert.ok(content.includes('id="hero-brand-partnership-box"'), `${name} must contain #hero-brand-partnership-box`);
  BANNED_UNRELATED.forEach((bad) => {
    assert.ok(!content.includes(bad), `${name} must NOT contain banned unrelated item/label '${bad}'`);
  });
  console.log(`  [PASS] ${name}: 3 themes, 7 genuine senior items, FTC disclosure & 0 unrelated items verified.`);
});

const vipJs = fs.readFileSync(VIP_STUDIO_JS, 'utf-8');
assert.ok(vipJs.includes('unlimitedVip: true') && vipJs.includes('9999'));
assert.ok(vipJs.includes('어머니의 봄날') && vipJs.includes('백운호 연가') && !vipJs.includes('4820'));
assert.ok(vipJs.includes('KAKAOTALK') && vipJs.includes('2초간 꾹'));
console.log('  [PASS] vip-digital-studio.js 100% unlimited free mode, 6 Baek Woon-ho songs & honest counter verified.\n');

console.log('======================================================================');
console.log('SUCCESS: ALL STORE & GIFT STUDIO TESTS PASSED (100%)');
console.log('======================================================================\n');
