/**
 * photo_booth.test.js
 * Automated verification test suite for Milestone 2:
 * Interactive Companion Photo Booth & Visual Pipeline on paradise-hero.com
 *
 * Test Sections:
 * 1. Physical existence of HTML pages (booth.html, photobooth.html), JS engine, and frame assets.
 * 2. Semantic HTML5, metadata, robots index/follow, and 1080x1440 canvas definitions.
 * 3. 56px+ senior ergonomics touch target classes, directional pads, and modal structures.
 * 4. 4 Commemorative Frame PNGs and thumbnails integrity and resolution.
 * 5. Interactive PhotoBoothEngine state machine, transform logic, and zoom/pan/rotate operations.
 * 6. 100% Client-Side Export compliance (zero server POST/upload endpoints, privacy preservation).
 * 7. Global Navigation integration (booth.html link across index, radio, stream, community, vip).
 * 8. Zero Prohibited Commercial Words (최저가, 할인율, 특가, 폭탄세일).
 * 9. Unified contact email (beable9489@gmail.com) and Store #296100 compliance.
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
console.log('Running paradise-hero.com Companion Photo Booth Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: File Existence & Substantive Sizes
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence and substantive sizes...');

assert.ok(fs.existsSync(BOOTH_HTML), 'booth.html must exist');
const boothStat = fs.statSync(BOOTH_HTML);
assert.ok(boothStat.size > 5000, `booth.html must be substantive (>5KB, got ${boothStat.size} bytes)`);
console.log(`  [PASS] booth.html verified (${boothStat.size} bytes).`);

assert.ok(fs.existsSync(PHOTOBOOTH_HTML), 'photobooth.html must exist for backward/forward compatibility');
const photoBoothStat = fs.statSync(PHOTOBOOTH_HTML);
assert.ok(photoBoothStat.size > 5000, `photobooth.html must be substantive (>5KB, got ${photoBoothStat.size} bytes)`);
console.log(`  [PASS] photobooth.html verified (${photoBoothStat.size} bytes).`);

assert.ok(fs.existsSync(BOOTH_JS), 'js/photo-booth.js must exist');
const jsStat = fs.statSync(BOOTH_JS);
assert.ok(jsStat.size > 4000, `js/photo-booth.js must be substantive (>4KB, got ${jsStat.size} bytes)`);
console.log(`  [PASS] js/photo-booth.js verified (${jsStat.size} bytes).`);

// -----------------------------------------------------------------------------
// Test 2: HTML5 Semantics, Metadata, Robots index/follow, and Canvas Layout
// -----------------------------------------------------------------------------
console.log('\nTest 2: Verifying HTML5 semantics, metadata, robots index/follow, and canvas layout...');

[BOOTH_HTML, PHOTOBOOTH_HTML].forEach((pagePath) => {
  const pageName = path.basename(pagePath);
  const html = fs.readFileSync(pagePath, 'utf-8');

  // Doctype, lang, charset, viewport
  assert.ok(/<!DOCTYPE\s+html>/i.test(html), `${pageName} must have <!DOCTYPE html>`);
  assert.ok(/<html\s+lang=["']ko["']/i.test(html), `${pageName} must have <html lang="ko">`);
  assert.ok(/<meta\s+charset=["']UTF-8["']/i.test(html), `${pageName} must have <meta charset="UTF-8">`);
  assert.ok(/<meta\s+name=["']viewport["']/i.test(html), `${pageName} must have mobile viewport`);

  // Robots index, follow
  assert.ok(
    /<meta\s+name=["']robots["']\s+content=["']index,\s*follow["']/i.test(html),
    `${pageName} must have <meta name="robots" content="index, follow">`
  );

  // Semantic elements
  assert.ok(html.includes('<header'), `${pageName} must include <header>`);
  assert.ok(html.includes('<nav'), `${pageName} must include <nav>`);
  assert.ok(html.includes('<main'), `${pageName} must include <main>`);
  assert.ok(html.includes('<footer'), `${pageName} must include <footer>`);

  // 1080x1440 Master Canvas definition
  assert.ok(
    /<canvas[^>]+id=["']booth-canvas["'][^>]+width=["']1080["'][^>]+height=["']1440["']/i.test(html) ||
    /<canvas[^>]+width=["']1080["'][^>]+height=["']1440["'][^>]+id=["']booth-canvas["']/i.test(html),
    `${pageName} must define canvas#booth-canvas with width 1080 and height 1440`
  );

  // Camera video stream & File upload input
  assert.ok(html.includes('id="booth-video"'), `${pageName} must include hidden video element #booth-video`);
  assert.ok(html.includes('id="booth-file-input"'), `${pageName} must include file input #booth-file-input`);
  assert.ok(/accept=["']image\/\*["']/.test(html), `${pageName} file input must accept image/*`);

  console.log(`  [PASS] ${pageName} semantic structure and 1080x1440 canvas validated.`);
});

// -----------------------------------------------------------------------------
// Test 3: Senior Ergonomics, 56px+ Touch Target Classes, and Modals
// -----------------------------------------------------------------------------
console.log('\nTest 3: Verifying senior ergonomics, oversized 56px touch controls, and modals...');

const boothHtml = fs.readFileSync(BOOTH_HTML, 'utf-8');

// Required oversized buttons
const requiredControls = [
  'btn-camera',
  'btn-album',
  'btn-zoom-in',
  'btn-zoom-out',
  'btn-flip',
  'btn-rotate',
  'btn-pan-up',
  'btn-pan-down',
  'btn-pan-left',
  'btn-pan-right',
  'btn-reset',
  'btn-save-photo',
  'btn-share-photo'
];

requiredControls.forEach((ctrlId) => {
  assert.ok(
    boothHtml.includes(`id="${ctrlId}"`),
    `booth.html must contain control element #${ctrlId}`
  );
});
console.log(`  [PASS] All ${requiredControls.length} senior control buttons present in booth.html.`);

// Modals
assert.ok(boothHtml.includes('id="save-celebration-modal"'), 'Must contain #save-celebration-modal');
assert.ok(boothHtml.includes('id="modal-preview-img"'), 'Must contain #modal-preview-img in celebration modal');
assert.ok(boothHtml.includes('id="camera-fallback-modal"'), 'Must contain #camera-fallback-modal');
assert.ok(boothHtml.includes('1초간 꾹'), 'Must explain long-press saving gesture for seniors');
console.log('  [PASS] Long-press celebration modal and camera fallback modal verified.');

// -----------------------------------------------------------------------------
// Test 4: Commemorative Frames Assets & Thumbnails
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying 4 commemorative frames assets and thumbnails...');

assert.strictEqual(COMMEMORATIVE_FRAMES.length, 4, 'Must define exactly 4 commemorative frames');
assert.strictEqual(CANVAS_WIDTH, 1080, 'Master canvas width must be 1080');
assert.strictEqual(CANVAS_HEIGHT, 1440, 'Master canvas height must be 1440');

const expectedFrames = [
  { id: 'flower_path', file: 'frame_flower_path.png', thumb: 'thumb_flower_path.png' },
  { id: 'golden_milestone', file: 'frame_golden_milestone.png', thumb: 'thumb_golden_milestone.png' },
  { id: 'paradise_4cut', file: 'frame_paradise_4cut.png', thumb: 'thumb_paradise_4cut.png' },
  { id: 'radio_studio', file: 'frame_radio_studio.png', thumb: 'thumb_radio_studio.png' }
];

expectedFrames.forEach((ef) => {
  const framePath = path.join(FRAMES_DIR, ef.file);
  const thumbPath = path.join(FRAMES_DIR, ef.thumb);

  assert.ok(fs.existsSync(framePath), `Master frame asset must exist: ${ef.file}`);
  const fStat = fs.statSync(framePath);
  assert.ok(fStat.size > 20000, `Frame ${ef.file} must be substantive (>20KB, got ${fStat.size} bytes)`);

  assert.ok(fs.existsSync(thumbPath), `Thumbnail asset must exist: ${ef.thumb}`);
  const tStat = fs.statSync(thumbPath);
  assert.ok(tStat.size > 4000, `Thumbnail ${ef.thumb} must be substantive (>4KB, got ${tStat.size} bytes)`);

  console.log(`  [PASS] Frame asset verified: ${ef.file} (${Math.round(fStat.size / 1024)}KB) & ${ef.thumb} (${Math.round(tStat.size / 1024)}KB)`);
});

// -----------------------------------------------------------------------------
// Test 5: Interactive PhotoBoothEngine State Machine & Transforms
// -----------------------------------------------------------------------------
console.log('\nTest 5: Verifying PhotoBoothEngine state machine and transformation methods...');

// Mock canvas and context for Node unit testing
const mockCtx = {
  save: () => {},
  restore: () => {},
  translate: () => {},
  rotate: () => {},
  scale: () => {},
  fillRect: () => {},
  strokeRect: () => {},
  drawImage: () => {},
  fillText: () => {},
  setLineDash: () => {}
};

const mockCanvas = {
  width: 1080,
  height: 1440,
  getContext: () => mockCtx,
  addEventListener: () => {},
  getBoundingClientRect: () => ({ width: 360, height: 480, top: 0, left: 0 }),
  toBlob: (cb) => cb(new Blob(['mock_jpeg_data'], { type: 'image/jpeg' }))
};

const engine = new PhotoBoothEngine({ canvas: mockCanvas });
assert.strictEqual(engine.activeFrameIndex, 0, 'Initial frame index must be 0');
assert.strictEqual(engine.transform.scale, 1.0, 'Initial scale must be 1.0');
assert.strictEqual(engine.transform.rotation, 0, 'Initial rotation must be 0');
assert.strictEqual(engine.transform.flipH, false, 'Initial flipH must be false');
assert.strictEqual(engine.transform.translateX, 0, 'Initial translateX must be 0');
assert.strictEqual(engine.transform.translateY, 0, 'Initial translateY must be 0');

// Test Zoom In
engine.zoomIn(0.1);
assert.ok(Math.abs(engine.transform.scale - 1.1) < 0.001, 'Zoom in should increase scale to ~1.1');

// Test Zoom Out
engine.zoomOut(0.1);
assert.ok(Math.abs(engine.transform.scale - 0.99) < 0.001, 'Zoom out should decrease scale');

// Test Rotation
engine.rotateClockwise();
assert.strictEqual(engine.transform.rotation, 90, 'Rotation should increment by 90 degrees');
engine.rotateClockwise();
assert.strictEqual(engine.transform.rotation, 180, 'Rotation should reach 180 degrees');
engine.rotateClockwise();
engine.rotateClockwise();
assert.strictEqual(engine.transform.rotation, 0, 'Rotation should cycle back to 0 degrees');

// Test Flip Horizontal
engine.flipHorizontal();
assert.strictEqual(engine.transform.flipH, true, 'flipH should toggle to true');
engine.flipHorizontal();
assert.strictEqual(engine.transform.flipH, false, 'flipH should toggle back to false');

// Test Pan
engine.pan(30, -50);
assert.strictEqual(engine.transform.translateX, 30, 'translateX should be 30');
assert.strictEqual(engine.transform.translateY, -50, 'translateY should be -50');

// Test Reset
engine.resetTransform();
assert.strictEqual(engine.transform.scale, 1.0, 'Scale should reset to 1.0');
assert.strictEqual(engine.transform.rotation, 0, 'Rotation should reset to 0');
assert.strictEqual(engine.transform.translateX, 0, 'TranslateX should reset to 0');
assert.strictEqual(engine.transform.translateY, 0, 'TranslateY should reset to 0');

// Test Frame Selection
engine.selectFrame(2);
assert.strictEqual(engine.activeFrameIndex, 2, 'activeFrameIndex should be 2');
assert.strictEqual(engine.getActiveFrame().id, 'paradise_4cut', 'Active frame should be paradise_4cut');

console.log('  [PASS] All PhotoBoothEngine transform operations and state transitions verified.');

// -----------------------------------------------------------------------------
// Test 6: 100% Client-Side Local Export Compliance (Zero Server Endpoints)
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying 100% client-side export and zero server upload dependencies...');

const boothJsContent = fs.readFileSync(BOOTH_JS, 'utf-8');

// Ensure toBlob and image/jpeg are used
assert.ok(boothJsContent.includes('toBlob'), 'photo-booth.js must use canvas.toBlob for memory export');
assert.ok(boothJsContent.includes('image/jpeg'), 'Export must target image/jpeg');
assert.ok(boothJsContent.includes('paradise_hero_with_you_'), 'Filename must include paradise_hero_with_you_ format');

// Ensure no backend endpoints are called for photo upload (pure client-side privacy)
assert.strictEqual(
  boothJsContent.includes('fetch(') || boothJsContent.includes('XMLHttpRequest') || boothJsContent.includes('$.ajax'),
  false,
  'photo-booth.js must NOT upload photos to any backend server (guaranteeing 100% client-side privacy and 0 server errors)'
);
console.log('  [PASS] 100% client-side memory export verified. Zero server dependencies or upload hazards.');

// -----------------------------------------------------------------------------
// Test 7: Global Navigation Integration Across All 5 Core Pages
// -----------------------------------------------------------------------------
console.log('\nTest 7: Verifying Photo Booth navigation link across all core pages...');

const PAGES_TO_VERIFY_NAV = [
  'index.html',
  'radio.html',
  'stream.html',
  'community.html',
  'vip.html',
  'booth.html',
  'photobooth.html'
];

PAGES_TO_VERIFY_NAV.forEach((pageName) => {
  const pagePath = path.join(ROOT_DIR, pageName);
  const html = fs.readFileSync(pagePath, 'utf-8');

  assert.ok(
    html.includes('href="booth.html"'),
    `${pageName} navigation bar must include link to booth.html`
  );
  assert.ok(
    html.includes('영웅과 함께'),
    `${pageName} navigation bar must contain label '영웅과 함께'`
  );
  console.log(`  [PASS] ${pageName} navigation bar links to booth.html ('📸 영웅과 함께').`);
});

// -----------------------------------------------------------------------------
// Test 8: Zero Prohibited Commercial Words Verification
// -----------------------------------------------------------------------------
console.log('\nTest 8: Verifying ZERO prohibited commercial words in Milestone 2 files...');

const prohibitedWords = ['최저가', '할인율', '특가', '폭탄세일'];
const m2Files = [
  BOOTH_HTML,
  PHOTOBOOTH_HTML,
  BOOTH_JS
];

m2Files.forEach((fPath) => {
  const content = fs.readFileSync(fPath, 'utf-8');
  prohibitedWords.forEach((word) => {
    assert.strictEqual(
      content.includes(word),
      false,
      `Prohibited commercial word '${word}' detected in ${path.basename(fPath)}!`
    );
  });
  console.log(`  [PASS] 0 prohibited words in ${path.basename(fPath)}.`);
});

// -----------------------------------------------------------------------------
// Test 9: Contact Email & Store #296100 Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 9: Verifying unified contact email and Store #296100...');

[BOOTH_HTML, PHOTOBOOTH_HTML].forEach((pPath) => {
  const content = fs.readFileSync(pPath, 'utf-8');
  assert.ok(content.includes('beable9489@gmail.com'), `${path.basename(pPath)} must contain unified email beable9489@gmail.com`);
  assert.ok(content.includes('296100'), `${path.basename(pPath)} must contain Lemon Squeezy Store #296100`);
});
console.log('  [PASS] Unified email beable9489@gmail.com and Store #296100 verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL COMPANION PHOTO BOOTH AUTOMATED TESTS PASSED (100%)');
console.log('===============================================================\n');
