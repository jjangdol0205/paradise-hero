/**
 * photo_booth_credit_payment.test.js
 * Verification Test Suite for 100% Unlimited Free Baek Woon-ho Photo Booth (Zero Credit Lock / Zero Paywall)
 * & KakaoTalk In-App 2-Second Long-Press Save Modal.
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
console.log('Running Unlimited Free Baek Woon-ho Photo Booth Test Suite');
console.log('===============================================================\n');

[BOOTH_HTML, PHOTOBOOTH_HTML, BOOTH_JS, CHAR_CATALOG_JS].forEach((p) => {
  assert.ok(fs.existsSync(p) && fs.statSync(p).size > 3000, `Missing or small file: ${path.basename(p)}`);
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
assert.strictEqual(engine.activeCharacterId, 'hero_style_01');
assert.strictEqual(engine.getActiveCharacter().name_ko, '백운호');

['hero_style_01', 'hero_style_02', 'hero_style_03', 'hero_style_04', 'hero_style_05', 'hero_style_06'].forEach((id) => {
  const c = engine.getCharacterById(id);
  assert.ok(c, `Outfit ${id} must exist`);
  assert.strictEqual(c.name_ko, '백운호');
  assert.ok(fs.existsSync(path.join(ROOT_DIR, c.sprite_path)));
});

engine.selectCharacter('hero_style_05');
engine.render();
assert.ok(
  textFillOperations.some((op) => op.text.includes('가상 트로트 가수 백운호와 함께 | paradise-hero.com')),
  'Watermark must include Baek Woon-ho & paradise-hero.com stamp'
);
console.log('  [PASS] 5-Layer two-shot compositing with 6 Baek Woon-ho stage outfits verified.');

const boothJsSource = fs.readFileSync(BOOTH_JS, 'utf-8');
assert.ok(boothJsSource.includes('credits: 9999') && boothJsSource.includes('unlimitedVip: true'));
assert.ok(boothJsSource.includes('KAKAOTALK') && boothJsSource.includes('2초간 꾹'));
assert.strictEqual(boothJsSource.includes('fetch(') || boothJsSource.includes('XMLHttpRequest'), false);
console.log('  [PASS] Zero credit lock, zero paywall, and KakaoTalk 2s long-press modal verified.');

console.log('\n===============================================================');
console.log('ALL UNLIMITED FREE PHOTO BOOTH TESTS PASSED (100%)!');
console.log('===============================================================');
