/**
 * photo_booth_credit_payment.test.js
 * Verification Test Suite for 100% Unlimited Free Photo Booth (Zero Credit Lock / Zero Paywall)
 * & KakaoTalk In-App 2-Second Long-Press Save Modal (2026-11-11 HQ Spec).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const BOOTH_HTML = path.join(ROOT_DIR, 'booth.html');
const PHOTOBOOTH_HTML = path.join(ROOT_DIR, 'photobooth.html');
const BOOTH_JS = path.join(ROOT_DIR, 'js', 'photo-booth.js');
const CHAR_CATALOG_JS = path.join(ROOT_DIR, 'js', 'character-catalog.js');

console.log('===============================================================');
console.log('Running Unlimited Free Photo Booth & Kakao Save UX Test Suite');
console.log('===============================================================\n');

[BOOTH_HTML, PHOTOBOOTH_HTML, BOOTH_JS, CHAR_CATALOG_JS].forEach((p) => {
  assert.ok(fs.existsSync(p) && fs.statSync(p).size > 4000, `Missing or small file: ${path.basename(p)}`);
});

const { PhotoBoothEngine, COMMEMORATIVE_FRAMES, CANVAS_WIDTH, CANVAS_HEIGHT } = require(BOOTH_JS);
assert.strictEqual(COMMEMORATIVE_FRAMES.length, 4);
assert.strictEqual(CANVAS_WIDTH, 1080);
assert.strictEqual(CANVAS_HEIGHT, 1440);

const textFillOperations = [];
const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, rotate: () => {},
  scale: () => {}, fillRect: () => {}, strokeRect: () => {}, drawImage: () => {},
  fillText: (text, x, y) => { textFillOperations.push({ text, x, y }); },
  setLineDash: () => {}
};
const mockCanvas = {
  width: 1080, height: 1440, getContext: () => mockCtx, addEventListener: () => {},
  getBoundingClientRect: () => ({ width: 360, height: 480, top: 0, left: 0 }),
  toBlob: (cb) => cb(new Blob(['mock_jpeg_data'], { type: 'image/jpeg' }))
};

const engine = new PhotoBoothEngine({ canvas: mockCanvas });
assert.strictEqual(engine.activeCharacterId, 'hwang_young_woong');
assert.strictEqual(engine.getActiveCharacter().name_ko, '황영웅');

// All 10 outfits belong exclusively to singer Hwang Young-woong
[
  'hwang_young_woong', 'lim_young_woong', 'lee_chan_won', 'young_tak', 'jeong_dong_won',
  'kim_ho_joong', 'jang_min_ho', 'park_seo_jin', 'son_tae_jin', 'ahn_sung_hoon_jin_hae_seong'
].forEach((id) => {
  const c = engine.getCharacterById(id);
  assert.ok(c, `Outfit ${id} must exist`);
  assert.strictEqual(c.name_ko, '황영웅', `Outfit ${id} must belong to 황영웅`);
  assert.ok(c.sprite_path.includes('?v=20261110c') || fs.existsSync(path.join(ROOT_DIR, c.sprite_path.split('?')[0])));
});

engine.selectCharacter('lee_chan_won');
engine.render();
assert.ok(
  textFillOperations.some((op) => op.text.includes('황영웅과 함께하는 파라다이스 | paradise-hero.com')),
  'Watermark must include paradise-hero.com stamp'
);
console.log('  [PASS] 5-Layer two-shot compositing with 10 Hwang Young-woong signature outfits verified.');

// Verify 100% removal of signup popup, 3,000 KRW paywall, and Lemon Squeezy
[BOOTH_HTML, PHOTOBOOTH_HTML].forEach((p) => {
  const html = fs.readFileSync(p, 'utf-8');
  assert.ok(!html.includes('id="signup-modal"'), `${path.basename(p)} must NOT have #signup-modal`);
  assert.ok(!html.includes('id="senior-payment-modal"'), `${path.basename(p)} must NOT have #senior-payment-modal`);
  assert.ok(!/lemonsqueezy/i.test(html), `${path.basename(p)} must NOT have lemonsqueezy`);
  assert.ok(!html.includes('296100'), `${path.basename(p)} must NOT have Store #296100`);
  assert.ok(html.includes('무제한 무료'), `${path.basename(p)} must clearly state unlimited free access`);
  assert.ok(html.includes('beable9489@gmail.com'), `${path.basename(p)} must include unified email`);
});

const boothJsSource = fs.readFileSync(BOOTH_JS, 'utf-8');
assert.ok(boothJsSource.includes('credits: 9999') && boothJsSource.includes('unlimitedVip: true'));
assert.ok(boothJsSource.includes('KAKAOTALK') && boothJsSource.includes('손가락으로 그림을 2초간 꾹~ 눌러 [사진 저장]을 누르세요'));
assert.strictEqual(
  boothJsSource.includes('fetch(') || boothJsSource.includes('XMLHttpRequest') || boothJsSource.includes('$.ajax'),
  false
);
console.log('  [PASS] Zero credit lock, zero Lemon Squeezy paywall, and KakaoTalk 2s long-press modal verified.');

console.log('\n===============================================================');
console.log('ALL UNLIMITED FREE PHOTO BOOTH TESTS PASSED (100%)!');
console.log('===============================================================');
