/**
 * photo_booth.test.js
 * Verification suite for Baek Woon-ho 6-Outfit Free Photo Booth & Kakao Long-Press Save UX.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const BOOTH_HTML = path.join(ROOT_DIR, 'booth.html');
const PHOTOBOOTH_HTML = path.join(ROOT_DIR, 'photobooth.html');
const BOOTH_JS = path.join(ROOT_DIR, 'js', 'photo-booth.js');
const FRAMES_DIR = path.join(ROOT_DIR, 'assets', 'frames');

const { PhotoBoothEngine, COMMEMORATIVE_FRAMES, CANVAS_WIDTH, CANVAS_HEIGHT } = require(BOOTH_JS);

console.log('===============================================================');
console.log('Running Baek Woon-ho 6-Outfit Photo Booth Test Suite');
console.log('===============================================================\n');

[BOOTH_HTML, PHOTOBOOTH_HTML].forEach((pagePath) => {
  const pageName = path.basename(pagePath);
  const html = fs.readFileSync(pagePath, 'utf-8');
  assert.ok(/<!DOCTYPE\s+html>/i.test(html) && /<html\s+lang=["']ko["']/i.test(html));
  assert.ok(html.includes('id="booth-canvas"') && html.includes('1080') && html.includes('1440'));
  assert.ok(html.includes('id="booth-video"') && html.includes('id="booth-file-input"'));
  assert.ok(html.includes('https://paradise-hero.com/assets/og_booth_share.jpg'), `${pageName} must use og_booth_share.jpg OG thumbnail`);
  assert.ok(html.includes('hero_style_01') && html.includes('hero_style_06'), `${pageName} must include hero_style_01~06`);
});

const boothHtml = fs.readFileSync(BOOTH_HTML, 'utf-8');
const requiredControls = [
  'btn-camera', 'btn-album', 'btn-zoom-in', 'btn-zoom-out', 'btn-flip',
  'btn-rotate', 'btn-pan-up', 'btn-pan-down', 'btn-pan-left', 'btn-pan-right',
  'btn-reset', 'btn-save-photo', 'btn-share-photo'
];
requiredControls.forEach((ctrlId) => {
  assert.ok(boothHtml.includes(`id="${ctrlId}"`), `booth.html must contain #${ctrlId}`);
});

assert.ok(boothHtml.includes('id="save-celebration-modal"') && boothHtml.includes('2초간 꾹'));
assert.strictEqual(COMMEMORATIVE_FRAMES.length, 4);
assert.strictEqual(CANVAS_WIDTH, 1080);
assert.strictEqual(CANVAS_HEIGHT, 1440);
['frame_flower_path.png', 'frame_golden_milestone.png', 'frame_paradise_4cut.png', 'frame_radio_studio.png'].forEach((f) => {
  assert.ok(fs.existsSync(path.join(FRAMES_DIR, f)) && fs.statSync(path.join(FRAMES_DIR, f)).size > 20000);
});

const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, rotate: () => {},
  scale: () => {}, fillRect: () => {}, strokeRect: () => {}, drawImage: () => {},
  fillText: () => {}, setLineDash: () => {}
};
const mockCanvas = {
  width: 1080, height: 1440, getContext: () => mockCtx, addEventListener: () => {},
  getBoundingClientRect: () => ({ width: 360, height: 480, top: 0, left: 0 }),
  toBlob: (cb) => cb(new Blob(['mock_jpeg_data'], { type: 'image/jpeg' }))
};
const engine = new PhotoBoothEngine({ canvas: mockCanvas });
engine.zoomIn(0.1);
assert.ok(Math.abs(engine.transform.scale - 1.1) < 0.001);
engine.rotateClockwise();
assert.strictEqual(engine.transform.rotation, 90);
engine.flipHorizontal();
assert.strictEqual(engine.transform.flipH, true);
engine.pan(30, -50);
assert.strictEqual(engine.transform.translateX, 30);
engine.resetTransform();
assert.strictEqual(engine.transform.scale, 1.0);

const boothJsContent = fs.readFileSync(BOOTH_JS, 'utf-8');
assert.ok(boothJsContent.includes('toBlob') && boothJsContent.includes('image/jpeg') && boothJsContent.includes('KAKAOTALK'));
assert.strictEqual(
  boothJsContent.includes('fetch(') || boothJsContent.includes('XMLHttpRequest') || boothJsContent.includes('$.ajax'),
  false,
  'photo-booth.js must NOT upload photos to any backend server'
);
console.log('  [PASS] PhotoBoothEngine transforms, client-side privacy, and 6-outfit Baek Woon-ho tray verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL PHOTO BOOTH TESTS PASSED (100%)');
console.log('===============================================================\n');
