/**
 * monetization_platform.test.js
 * Verification suite for Dual Safe Special Store (Naver Creator Shop + Coupang AF7865143)
 * & Unlimited Free Gift Studio (2026-11-11 HQ Spec).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const INDEX_HTML = path.join(ROOT_DIR, 'index.html');
const BOOTH_HTML = path.join(ROOT_DIR, 'booth.html');
const VIP_HTML = path.join(ROOT_DIR, 'vip.html');
const RADIO_HTML = path.join(ROOT_DIR, 'radio.html');
const STREAM_HTML = path.join(ROOT_DIR, 'stream.html');
const VIP_STUDIO_JS = path.join(ROOT_DIR, 'js', 'vip-digital-studio.js');

console.log('======================================================================');
console.log('Running Dual Safe Special Store & Free Gift Studio Verification');
console.log('======================================================================\n');

const storePages = [
  { name: 'index.html', content: fs.readFileSync(INDEX_HTML, 'utf-8') },
  { name: 'booth.html', content: fs.readFileSync(BOOTH_HTML, 'utf-8') },
  { name: 'vip.html', content: fs.readFileSync(VIP_HTML, 'utf-8') },
  { name: 'radio.html', content: fs.readFileSync(RADIO_HTML, 'utf-8') },
  { name: 'stream.html', content: fs.readFileSync(STREAM_HTML, 'utf-8') }
];

const NAVER_CSHOP_URL = 'https://cshop.naver.com/paradiseshop';
const FTC_DISCLOSURE = '본 특가관은 네이버 쇼핑 커넥트 및 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.';

storePages.forEach(({ name, content }) => {
  assert.ok(
    content.includes('김쌤이 직접 고른 어머님 콘서트·응원·건강 안심 특가관'),
    `${name} must contain Dual Safe Special Store heading`
  );
  assert.ok(
    content.includes(NAVER_CSHOP_URL),
    `${name} must contain top green king-button to ${NAVER_CSHOP_URL}`
  );
  assert.ok(
    content.includes('https://www.coupang.com/np/search?q=') && content.includes('lptag=AF7865143&subid=paradisehero') ||
    content.includes('lptag=AF7865143&amp;subid=paradisehero'),
    `${name} must contain working Coupang search URLs with lptag=AF7865143&subid=paradisehero`
  );
  const coupangHits = (content.match(/www\.coupang\.com\/np\/search\?q=/g) || []).length;
  assert.ok(coupangHits >= 6, `${name} must contain all 6 Coupang items (found ${coupangHits})`);

  assert.ok(!content.includes('link.coupang.com'), `${name} must NOT contain broken fake shortlinks link.coupang.com`);
  assert.ok(!/lemonsqueezy/i.test(content), `${name} must NOT contain broken lemonsqueezy links`);
  assert.ok(!content.includes('296100'), `${name} must NOT contain Store #296100`);
  assert.ok(content.includes(FTC_DISCLOSURE), `${name} must contain exact FTC disclosure`);
  assert.ok(content.includes('beable9489@gmail.com'), `${name} must include unified support email`);
  console.log(`  [PASS] ${name}: Naver Creator Shop + 6 Coupang AF7865143 items + FTC disclosure verified.`);
});

const vipHtml = fs.readFileSync(VIP_HTML, 'utf-8');
const vipJs = fs.readFileSync(VIP_STUDIO_JS, 'utf-8');
assert.ok(vipHtml.includes('id="auto-billboard-form"'), 'vip.html must preserve free fan billboard ticker form');
assert.ok(vipJs.includes('unlimitedVip: true') && vipJs.includes('9999'), 'vip-digital-studio.js must unlock unlimited free access');
assert.ok(vipJs.includes('KAKAOTALK') && vipJs.includes('2초간 꾹'), 'vip-digital-studio.js must support KakaoTalk 2s long-press save modal');
assert.ok(!/lemonsqueezy/i.test(vipJs) && !vipJs.includes('296100'), 'vip-digital-studio.js must NOT reference Lemon Squeezy');
console.log('  [PASS] vip.html & vip-digital-studio.js 100% unlimited free mode + Kakao long-press modal verified.\n');

console.log('======================================================================');
console.log('SUCCESS: ALL DUAL SAFE SPECIAL STORE & GIFT STUDIO TESTS PASSED (100%)');
console.log('======================================================================\n');
