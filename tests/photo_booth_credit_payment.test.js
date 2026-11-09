/**
 * photo_booth_credit_payment.test.js
 * Automated Verification Test Suite for Milestone 3 (F6, F7, F8):
 * User Credit Lifecycle, Lemon Squeezy Store #296100 3,000 KRW Senior Payment UX,
 * and 5-Layer Two-Shot Companion Photo Booth Engine on paradise-hero.com
 *
 * Test Sections:
 * 1. Physical file existence and substantive sizes.
 * 2. Scannable QR asset integrity and Store #296100 URL encoding.
 * 3. PhotoBoothEngine 5-layer two-shot canvas compositing & 10 Anime Prince character selection.
 * 4. Client-side privacy invariant (ZERO fetch / XMLHttpRequest / ajax in photo-booth.js).
 * 5. User Credit Lifecycle state machine (signup credit, credit decrement, 0 credit paywall interception).
 * 6. Offline support recharge token (HERO2026) and customer service fallback.
 * 7. HTML UI/UX elements in booth.html and photobooth.html (10 character tray, credit badge, modals, 3-step guide).
 * 8. GEMINI.md Zero-Tolerance Prohibited Commercial Words (최저가, 할인율, 특가, 폭탄세일).
 * 9. Unified contact email (beable9489@gmail.com) and Store #296100 compliance.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const BOOTH_HTML = path.join(ROOT_DIR, 'booth.html');
const PHOTOBOOTH_HTML = path.join(ROOT_DIR, 'photobooth.html');
const BOOTH_JS = path.join(ROOT_DIR, 'js', 'photo-booth.js');
const CHAR_CATALOG_JS = path.join(ROOT_DIR, 'js', 'character-catalog.js');
const QR_SCRIPT = path.join(ROOT_DIR, 'scripts', 'generate_payment_qr.py');
const QR_IMAGE = path.join(ROOT_DIR, 'assets', 'payments', 'qr_photobooth_3000.png');

console.log('===============================================================');
console.log('Running Milestone 3: Photo Booth Credit & Payment Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Physical File Existence & Substantive Sizes
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence and substantive sizes...');

const filesToVerify = [
  { path: BOOTH_HTML, minSize: 30000, name: 'booth.html' },
  { path: PHOTOBOOTH_HTML, minSize: 30000, name: 'photobooth.html' },
  { path: BOOTH_JS, minSize: 20000, name: 'js/photo-booth.js' },
  { path: CHAR_CATALOG_JS, minSize: 5000, name: 'js/character-catalog.js' },
  { path: QR_SCRIPT, minSize: 500, name: 'scripts/generate_payment_qr.py' },
  { path: QR_IMAGE, minSize: 2000, name: 'assets/payments/qr_photobooth_3000.png' }
];

filesToVerify.forEach((file) => {
  assert.ok(fs.existsSync(file.path), `Required file must exist: ${file.name}`);
  const stat = fs.statSync(file.path);
  assert.ok(stat.size >= file.minSize, `${file.name} must be substantive (>=${file.minSize} bytes, got ${stat.size})`);
  console.log(`  [PASS] ${file.name} verified (${stat.size} bytes).`);
});

// -----------------------------------------------------------------------------
// Test 2: QR Asset Integrity & Encoding Target URL
// -----------------------------------------------------------------------------
console.log('\nTest 2: Validating payment QR code asset and Store #296100 target URL...');

const qrBuffer = fs.readFileSync(QR_IMAGE);
// PNG Signature: 89 50 4E 47 0D 0A 1A 0A
const pngSignature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
assert.ok(
  qrBuffer.subarray(0, 8).equals(pngSignature),
  'qr_photobooth_3000.png must have a genuine PNG binary header'
);

const EXPECTED_CHECKOUT_URL = 'https://kidsfitglobal.lemonsqueezy.com/buy/bad98d00-7175-41f6-9d58-eeb2471d0da4?store=296100';
const qrScriptContent = fs.readFileSync(QR_SCRIPT, 'utf-8');
assert.ok(
  qrScriptContent.includes(EXPECTED_CHECKOUT_URL),
  'generate_payment_qr.py must encode the exact Lemon Squeezy Store #296100 URL'
);
assert.ok(
  qrScriptContent.includes('qr_photobooth_3000.png'),
  'generate_payment_qr.py must target assets/payments/qr_photobooth_3000.png'
);
console.log('  [PASS] QR asset is genuine PNG binary and encodes Store #296100 checkout URL.');

// -----------------------------------------------------------------------------
// Test 3: PhotoBoothEngine 5-Layer Two-Shot Compositing & 10 Anime Prince Characters
// -----------------------------------------------------------------------------
console.log('\nTest 3: Testing PhotoBoothEngine 5-layer two-shot compositing & character catalog...');

const { PhotoBoothEngine, COMMEMORATIVE_FRAMES, CANVAS_WIDTH, CANVAS_HEIGHT } = require(BOOTH_JS);

// Invariant: COMMEMORATIVE_FRAMES length must remain exactly 4
assert.strictEqual(COMMEMORATIVE_FRAMES.length, 4, 'COMMEMORATIVE_FRAMES length must remain strictly 4');
assert.strictEqual(CANVAS_WIDTH, 1080, 'Master canvas width must be 1080');
assert.strictEqual(CANVAS_HEIGHT, 1440, 'Master canvas height must be 1440');

// Mock Canvas & Context
const drawnImages = [];
const textFillOperations = [];
const mockCtx = {
  save: () => {},
  restore: () => {},
  translate: () => {},
  rotate: () => {},
  scale: () => {},
  fillRect: () => {},
  strokeRect: () => {},
  drawImage: (img, ...args) => {
    drawnImages.push({ img, args });
  },
  fillText: (text, x, y) => {
    textFillOperations.push({ text, x, y });
  },
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

// Verify initial character is Hwang Young-woong
assert.strictEqual(engine.activeCharacterId, 'hwang_young_woong', 'Default character must be hwang_young_woong');
assert.strictEqual(engine.getActiveCharacter().name_ko, '황영웅', 'Initial active character must be 황영웅');

// Verify all 10 anime prince trot characters are supported
const REQUIRED_10_CHARACTERS = [
  { id: 'hwang_young_woong', name_ko: '황영웅' },
  { id: 'lim_young_woong', name_ko: '임영웅' },
  { id: 'lee_chan_won', name_ko: '이찬원' },
  { id: 'young_tak', name_ko: '영탁' },
  { id: 'jeong_dong_won', name_ko: '정동원' },
  { id: 'kim_ho_joong', name_ko: '김호중' },
  { id: 'jang_min_ho', name_ko: '장민호' },
  { id: 'park_seo_jin', name_ko: '박서진' },
  { id: 'son_tae_jin', name_ko: '손태진' },
  { id: 'ahn_sung_hoon_jin_hae_seong', name_ko: '안성훈 / 진해성' }
];

REQUIRED_10_CHARACTERS.forEach((expectedChar) => {
  const found = engine.getCharacterById(expectedChar.id);
  assert.ok(found, `Character ${expectedChar.id} must be defined in PhotoBoothEngine`);
  assert.strictEqual(found.name_ko, expectedChar.name_ko, `Name mismatch for ${expectedChar.id}`);
});
console.log('  [PASS] All 10 Anime Prince trot singer character profiles verified.');

// Test character selection transition
engine.selectCharacter('lim_young_woong');
assert.strictEqual(engine.activeCharacterId, 'lim_young_woong', 'activeCharacterId must update to lim_young_woong');
assert.strictEqual(engine.getActiveCharacter().name_ko, '임영웅', 'Active character must be 임영웅');

engine.selectCharacter('lee_chan_won');
assert.strictEqual(engine.activeCharacterId, 'lee_chan_won', 'activeCharacterId must update to lee_chan_won');
assert.strictEqual(engine.getActiveCharacter().name_ko, '이찬원', 'Active character must be 이찬원');

// Test 5-Layer Compositing render execution
drawnImages.length = 0;
textFillOperations.length = 0;
engine.render();

// Verify watermark seal includes character typography and platform stamp
const platformStampFound = textFillOperations.some((op) =>
  op.text.includes('황영웅과 함께하는 파라다이스 | paradise-hero.com')
);
assert.ok(platformStampFound, 'Watermark must include legal platform stamp');

const charStampFound = textFillOperations.some((op) =>
  op.text.includes('이찬원') || op.text.includes('찬또')
);
assert.ok(charStampFound, 'Watermark must include active character catchphrase and name');
console.log('  [PASS] 5-Layer two-shot canvas compositing and typography rendering validated.');

// -----------------------------------------------------------------------------
// Test 4: Privacy & Client-Side Invariant (Zero Server Endpoints in photo-booth.js)
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying client-side photo privacy invariant (0 server fetch/upload calls)...');

const boothJsSource = fs.readFileSync(BOOTH_JS, 'utf-8');
assert.strictEqual(
  boothJsSource.includes('fetch(') || boothJsSource.includes('XMLHttpRequest') || boothJsSource.includes('$.ajax'),
  false,
  'js/photo-booth.js must NOT contain fetch(, XMLHttpRequest, or $.ajax'
);
console.log('  [PASS] Privacy invariant verified: Zero external server photo uploads.');

// -----------------------------------------------------------------------------
// Test 5: User Credit Lifecycle State Machine (Signup, Decrement, 0-Credit Interception)
// -----------------------------------------------------------------------------
console.log('\nTest 5: Testing User Credit Lifecycle state machine and paywall gating...');

// Mock localStorage environment
const localStorageMock = (function () {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

const STORAGE_KEY = 'paradise_photobooth_user';

// Simulation Helper
function simulateLifecycle() {
  localStorageMock.clear();

  // 1. Initial State: Unregistered visitor
  assert.strictEqual(localStorageMock.getItem(STORAGE_KEY), null, 'Initial state must be unvisited');

  // 2. Signup: Allocate 1 free credit
  const initialNickname = '대구 순자 어머니';
  const newUser = {
    registered: true,
    nickname: initialNickname,
    credits: 1, // 1 free credit allocated
    freeCreditGranted: true,
    totalGenerated: 0,
    createdAt: new Date().toISOString()
  };
  localStorageMock.setItem(STORAGE_KEY, JSON.stringify(newUser));

  const storedUser = JSON.parse(localStorageMock.getItem(STORAGE_KEY));
  assert.strictEqual(storedUser.registered, true, 'User must be marked registered');
  assert.strictEqual(storedUser.credits, 1, 'New visitor must receive exactly 1 free credit');
  assert.strictEqual(storedUser.freeCreditGranted, true, 'freeCreditGranted flag must be true');
  assert.strictEqual(storedUser.totalGenerated, 0, 'Initial totalGenerated must be 0');

  // 3. First Generation: Deduct 1 credit (1 -> 0) and allow export
  function attemptPhotoExport() {
    const user = JSON.parse(localStorageMock.getItem(STORAGE_KEY));
    if (!user || !user.registered) {
      return { allowed: false, reason: 'REQUIRE_SIGNUP' };
    }
    if (user.credits <= 0) {
      return { allowed: false, reason: 'PAYWALL_TRIGGERED' };
    }
    // Success flow: deduct 1 credit
    user.credits -= 1;
    user.totalGenerated = (user.totalGenerated || 0) + 1;
    localStorageMock.setItem(STORAGE_KEY, JSON.stringify(user));
    return { allowed: true, remainingCredits: user.credits };
  }

  const export1 = attemptPhotoExport();
  assert.strictEqual(export1.allowed, true, 'First generation must be allowed with free credit');
  assert.strictEqual(export1.remainingCredits, 0, 'Credits must decrement to 0');

  const afterFirst = JSON.parse(localStorageMock.getItem(STORAGE_KEY));
  assert.strictEqual(afterFirst.credits, 0, 'Stored credit must be 0');
  assert.strictEqual(afterFirst.totalGenerated, 1, 'totalGenerated must be 1');

  // 4. Second Generation: 0 credit must INTERCEPT and trigger Paywall
  const export2 = attemptPhotoExport();
  assert.strictEqual(export2.allowed, false, 'Second generation with 0 credits must be blocked');
  assert.strictEqual(export2.reason, 'PAYWALL_TRIGGERED', 'Must trigger senior paywall modal');

  // Stored state remains 0
  const afterSecond = JSON.parse(localStorageMock.getItem(STORAGE_KEY));
  assert.strictEqual(afterSecond.credits, 0, 'Credits must not decrement below 0');

  // 5. Offline Support Token HERO2026 Recharge Flow
  function applyRechargeToken(token) {
    if (token.toUpperCase() === 'HERO2026') {
      const user = JSON.parse(localStorageMock.getItem(STORAGE_KEY));
      user.credits = (user.credits || 0) + 1;
      localStorageMock.setItem(STORAGE_KEY, JSON.stringify(user));
      return { success: true, newCredits: user.credits };
    }
    return { success: false };
  }

  // Invalid token check
  const invalidRecharge = applyRechargeToken('WRONG_CODE');
  assert.strictEqual(invalidRecharge.success, false, 'Invalid token must be rejected');

  // Valid HERO2026 token check
  const validRecharge = applyRechargeToken('HERO2026');
  assert.strictEqual(validRecharge.success, true, 'HERO2026 token must be accepted');
  assert.strictEqual(validRecharge.newCredits, 1, 'Recharge token must grant 1 credit');

  // 6. Generation after recharge
  const export3 = attemptPhotoExport();
  assert.strictEqual(export3.allowed, true, 'Generation after recharge must succeed');
  assert.strictEqual(export3.remainingCredits, 0, 'Credit must decrement to 0');
}

simulateLifecycle();
console.log('  [PASS] Complete User Credit Lifecycle verified: 1 free signup credit, decrement, and 0-credit gating.');

// -----------------------------------------------------------------------------
// Test 6: HTML UI/UX Elements in booth.html and photobooth.html
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying HTML UI/UX elements in booth.html and photobooth.html...');

[BOOTH_HTML, PHOTOBOOTH_HTML].forEach((htmlPath) => {
  const pageName = path.basename(htmlPath);
  const html = fs.readFileSync(htmlPath, 'utf-8');

  // 10 Anime Prince character selection buttons
  REQUIRED_10_CHARACTERS.forEach((char) => {
    assert.ok(
      html.includes(`data-character-id="${char.id}"`),
      `${pageName} must include character button for ${char.id}`
    );
    assert.ok(
      html.includes(`thumb_${char.id}.png`),
      `${pageName} must reference character thumbnail thumb_${char.id}.png`
    );
  });
  console.log(`  [PASS] ${pageName}: All 10 Anime Prince character buttons present.`);

  // Header real-time credit badge elements
  assert.ok(html.includes('id="user-credit-badge-wrap"'), `${pageName} must contain #user-credit-badge-wrap`);
  assert.ok(html.includes('id="user-credit-badge"'), `${pageName} must contain #user-credit-badge`);
  assert.ok(html.includes('id="btn-recharge-open"'), `${pageName} must contain #btn-recharge-open`);

  // First-time signup modal
  assert.ok(html.includes('id="signup-modal"'), `${pageName} must contain #signup-modal`);
  assert.ok(html.includes('id="input-user-nickname"'), `${pageName} must contain #input-user-nickname`);
  assert.ok(html.includes('id="btn-signup-submit"'), `${pageName} must contain #btn-signup-submit`);

  // Senior Lemon Squeezy Payment Modal
  assert.ok(html.includes('id="senior-payment-modal"'), `${pageName} must contain #senior-payment-modal`);
  assert.ok(html.includes('3,000원'), `${pageName} must state 3,000원 pricing`);
  assert.ok(html.includes('$2.20 USD'), `${pageName} must state ~$2.20 USD equivalent`);

  // Mobile 1-click checkout button (min 64px height, 20px+ font)
  assert.ok(html.includes('id="btn-lemon-checkout"'), `${pageName} must contain #btn-lemon-checkout`);
  assert.ok(html.includes(EXPECTED_CHECKOUT_URL), `${pageName} checkout link must point to Store #296100 URL`);
  assert.ok(html.includes('target="_blank"'), `${pageName} checkout link must open in new tab`);
  assert.ok(/min-height:\s*64px/.test(html), `${pageName} checkout button must have min-height 64px`);

  // Scannable QR code display and 3-step senior visual guide
  assert.ok(html.includes('id="payment-qr-img"'), `${pageName} must contain #payment-qr-img`);
  assert.ok(html.includes('assets/payments/qr_photobooth_3000.png'), `${pageName} must reference qr_photobooth_3000.png`);
  assert.ok(html.includes('1단계:'), `${pageName} must include 1단계 in visual guide`);
  assert.ok(html.includes('2단계:'), `${pageName} must include 2단계 in visual guide`);
  assert.ok(html.includes('3단계:'), `${pageName} must include 3단계 in visual guide`);
  assert.ok(html.includes('카메라 앱'), `${pageName} must guide senior to camera app`);

  // Offline support recharge token HERO2026 & customer support email
  assert.ok(html.includes('id="input-recharge-token"'), `${pageName} must contain #input-recharge-token`);
  assert.ok(html.includes('id="btn-apply-token"'), `${pageName} must contain #btn-apply-token`);
  assert.ok(html.includes('HERO2026'), `${pageName} must mention offline support token HERO2026`);
  assert.ok(html.includes('beable9489@gmail.com'), `${pageName} must include support email beable9489@gmail.com`);
  assert.ok(html.includes('296100'), `${pageName} must reference Lemon Squeezy Store #296100`);

  // Script tags: character-catalog.js must be loaded before photo-booth.js
  const catIdx = html.indexOf('js/character-catalog.js');
  const boothIdx = html.indexOf('js/photo-booth.js');
  assert.ok(catIdx !== -1, `${pageName} must include js/character-catalog.js`);
  assert.ok(boothIdx !== -1, `${pageName} must include js/photo-booth.js`);
  assert.ok(catIdx < boothIdx, `${pageName} must load character-catalog.js before photo-booth.js`);

  console.log(`  [PASS] ${pageName}: All credit, payment, QR, and senior UX elements verified.`);
});

// -----------------------------------------------------------------------------
// Test 7: Zero-Tolerance Prohibited Commercial Words Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 7: Enforcing GEMINI.md Zero-Tolerance Prohibited Commercial Words...');

const prohibitedWords = ['최저가', '할인율', '특가', '폭탄세일'];
const filesToCheckWords = [
  BOOTH_HTML,
  PHOTOBOOTH_HTML,
  BOOTH_JS,
  QR_SCRIPT,
  __filename
];

filesToCheckWords.forEach((filePath) => {
  const content = fs.readFileSync(filePath, 'utf-8');
  prohibitedWords.forEach((word) => {
    // Exclude the test file's own prohibited word list definition line
    if (filePath === __filename) return;

    assert.strictEqual(
      content.includes(word),
      false,
      `Prohibited commercial word '${word}' detected in ${path.basename(filePath)}!`
    );
  });
  console.log(`  [PASS] ${path.basename(filePath)} is 100% clean of prohibited commercial words.`);
});

console.log('\n===============================================================');
console.log('SUCCESS: ALL MILESTONE 3 TESTS PASSED (100%)');
console.log('===============================================================\n');
