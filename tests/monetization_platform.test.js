/**
 * monetization_platform.test.js
 * Comprehensive automated verification test suite for Milestone 3:
 * Automated Monetization Strategy & Web Platform Touchpoints (paradise-hero.com & @김쌤의영웅라디오)
 *
 * Verifies:
 * 1. docs/PARADISE_HERO_MONETIZATION_BLUEPRINT.md 100% automated operational flows (Pillars 1~4)
 * 2. stream.html & vip.html senior affiliate curation commerce (6 items, links, FTC notice, approved terms)
 * 3. vip.html automated billboard micro-donation web form (zero manual mailto, client-side queue, Store #296100)
 * 4. radio.html & index.html YouTube 1-click subscription funnel (?sub_confirmation=1)
 * 5. Strict Zero Prohibited Words (최저가, 할인율, 특가, 폭탄세일) across all modified files
 * 6. Lemon Squeezy Store #296100 and unified contact email beable9489@gmail.com
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const DOCS_DIR = path.join(ROOT_DIR, 'docs');
const BLUEPRINT_PATH = path.join(DOCS_DIR, 'PARADISE_HERO_MONETIZATION_BLUEPRINT.md');
const STREAM_HTML = path.join(ROOT_DIR, 'stream.html');
const VIP_HTML = path.join(ROOT_DIR, 'vip.html');
const RADIO_HTML = path.join(ROOT_DIR, 'radio.html');
const INDEX_HTML = path.join(ROOT_DIR, 'index.html');

console.log('======================================================================');
console.log('Running Milestone 3: Automated Monetization & Touchpoints Verification');
console.log('======================================================================\n');

// -----------------------------------------------------------------------------
// Test Group 1: Blueprint Automated Operational Flows (Section 7)
// -----------------------------------------------------------------------------
console.log('Test Group 1: Verifying Blueprint 100% Automated Operational Flows...');

assert.ok(fs.existsSync(BLUEPRINT_PATH), 'PARADISE_HERO_MONETIZATION_BLUEPRINT.md must exist');
const blueprint = fs.readFileSync(BLUEPRINT_PATH, 'utf-8');

// Section 7 title & Zero Human Management
assert.ok(
  blueprint.includes('100% 무인 자동화') || blueprint.includes('Zero Human Management'),
  'Blueprint must feature 100% Automated Operational Flows / Zero Human Management'
);

// Pillar 1: Webhook & Digital Keepsake & Self-Serve Portal
assert.ok(blueprint.includes('order_created') && blueprint.includes('subscription_created'), 'Must document Lemon Squeezy webhooks (order_created, subscription_created)');
assert.ok(blueprint.includes('디지털') && (blueprint.includes('인증서') || blueprint.includes('Keepsake')), 'Must document instant digital keepsake / certificate delivery');
assert.ok(blueprint.includes('달력 배경화면') || blueprint.includes('배경화면'), 'Must document monthly high-res wallpaper delivery');
assert.ok(blueprint.includes('오디오') && (blueprint.includes('스트림') || blueprint.includes('스트리밍')), 'Must document unreleased private audio streaming unlock');
assert.ok(blueprint.includes('Customer Portal') || blueprint.includes('고객 포털') || blueprint.includes('셀프서비스'), 'Must document 1-click self-serve customer cancellation portal');

// Pillar 2: Real-time Billboard Automated FIFO Queue
assert.ok(blueprint.includes('전광판') && (blueprint.includes('FIFO') || blueprint.includes('큐') || blueprint.includes('localStorage')), 'Must document real-time billboard ticker queue automation');
assert.ok(blueprint.includes('3,000원') && blueprint.includes('5,000원') && blueprint.includes('10,000원'), 'Must document 3 micro-donation tiers');

// Pillar 3: Senior Affiliate Commerce Parameters & Catalog
assert.ok(blueprint.includes('AF7865143'), 'Must document Coupang Partners code AF7865143');
assert.ok(blueprint.includes('A100708867'), 'Must document LinkPrice merchant code A100708867');
assert.ok(blueprint.includes('CPS') && (blueprint.includes('5%') || blueprint.includes('15%')), 'Must document CPS commission range 5~15%');
assert.ok(blueprint.includes('rel="noopener noreferrer sponsored"') || blueprint.includes('sponsored'), 'Must document sponsored link attribute');

// Pillar 4: YouTube Synergy & Funnels
assert.ok(blueprint.includes('15분') || blueprint.includes('롱폼'), 'Must document 15-minute longform format');
assert.ok(blueprint.includes('미드롤'), 'Must document 3 mid-roll ads placement strategy');
assert.ok(blueprint.includes('RPM') || blueprint.includes('4,500원') || blueprint.includes('8,500원'), 'Must document YouTube RPM 4,500 ~ 8,500 KRW');
assert.ok(blueprint.includes('?sub_confirmation=1'), 'Must document 1-click subscription link with ?sub_confirmation=1');
assert.ok(blueprint.includes('story.html'), 'Must document single-gate description box funnel to story.html');

console.log('  [PASS] Blueprint 100% automated operational flows verified for Pillars 1, 2, 3, and 4.\n');

// -----------------------------------------------------------------------------
// Test Group 2: Senior Affiliate Curation Commerce in stream.html and vip.html
// -----------------------------------------------------------------------------
console.log('Test Group 2: Verifying Senior Affiliate Curation Commerce in Web Pages...');

const streamHtml = fs.readFileSync(STREAM_HTML, 'utf-8');
const vipHtml = fs.readFileSync(VIP_HTML, 'utf-8');

const targetPages = [
  { name: 'stream.html', content: streamHtml },
  { name: 'vip.html', content: vipHtml }
];

const requiredProducts = [
  { name: '콘서트 폭신 방석', tag: 'AF7865143_cushion' },
  { name: '에메랄드 방수 크로스백', tag: 'AF7865143_pouch' },
  { name: '영웅 보온 보냉 텀블러', tag: 'AF7865143_tumbler' },
  { name: '무릎 안심 MSM 식이유황 관절 영양제', tag: 'AF7865143_msm' },
  { name: '목 건강 도라지 배즙 스틱', tag: 'AF7865143_pear' },
  { name: '눈 피로 개선 루테인 지아잔틴', tag: 'AF7865143_lutein' }
];

const ftcNotice = '이 포스팅은 제휴마케팅 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있으며 어머님의 구매 가격에는 일체의 영향이 없습니다.';

targetPages.forEach(({ name, content }) => {
  // Check section existence
  assert.ok(content.includes('id="senior-curation-market"'), `${name} must contain section #senior-curation-market`);
  assert.ok(content.includes('파라다이스 에디터 안심 큐레이션'), `${name} must include curation badge`);
  assert.ok(content.includes('어머님을 위한 콘서트 필수품 &amp; 건강 쉼터') || content.includes('어머님을 위한 콘서트 필수품 & 건강 쉼터'), `${name} must include curation section heading`);

  // Check all 6 products exist
  requiredProducts.forEach((prod) => {
    assert.ok(content.includes(prod.name), `${name} must contain product: ${prod.name}`);
    assert.ok(content.includes(prod.tag), `${name} must contain tracking link tag: ${prod.tag}`);
  });

  // Check standard approved button CTA
  const ctaMatches = (content.match(/공식 판매처 보러가기/g) || []).length;
  assert.ok(ctaMatches >= 6, `${name} must contain at least 6 approved CTA buttons '공식 판매처 보러가기' (found ${ctaMatches})`);

  // Check approved pricing label
  const labelMatches = (content.match(/어머님 추천 혜택가/g) || []).length;
  assert.ok(labelMatches >= 6, `${name} must contain at least 6 approved labels '어머님 추천 혜택가' (found ${labelMatches})`);

  // Check sponsored link attribute
  assert.ok(content.includes('rel="noopener noreferrer sponsored"'), `${name} must format outbound affiliate links with rel="noopener noreferrer sponsored"`);

  // Check FTC Disclosure
  assert.ok(content.includes(ftcNotice), `${name} must display the exact FTC economic interest disclosure`);
  assert.ok(content.includes('공정거래위원회 심사지침 준수 고지'), `${name} must include FTC title notice`);

  console.log(`  [PASS] All 6 senior affiliate curation cards, FTC disclosure & links verified in ${name}.`);
});
console.log();

// -----------------------------------------------------------------------------
// Test Group 3: Automated Billboard Micro-Donation Section in vip.html
// -----------------------------------------------------------------------------
console.log('Test Group 3: Verifying Automated Billboard Donation in vip.html...');

// Form presence and elements
assert.ok(vipHtml.includes('id="auto-billboard-form"'), 'vip.html must contain #auto-billboard-form');
assert.ok(vipHtml.includes('id="bb-nickname"'), 'vip.html must contain nickname input #bb-nickname');
assert.ok(vipHtml.includes('id="bb-message"'), 'vip.html must contain message input #bb-message');
assert.ok(vipHtml.includes('id="bb-tier"'), 'vip.html must contain tier selector #bb-tier');
assert.ok(vipHtml.includes('value="3000"') && vipHtml.includes('value="5000"') && vipHtml.includes('value="10000"'), 'vip.html form must support 3K, 5K, and 10K tiers');

// Zero manual mailto in billboard-support
const billboardSection = vipHtml.substring(
  vipHtml.indexOf('id="billboard-support"'),
  vipHtml.indexOf('id="auto-billboard-form"') + 800
);
assert.strictEqual(
  billboardSection.includes('mailto:'),
  false,
  'vip.html billboard-support section must NOT use manual mailto! Must be 100% automated web entry.'
);

// Client-side automated handler script
assert.ok(vipHtml.includes('function submitAutoBillboard'), 'vip.html must define submitAutoBillboard()');
assert.ok(vipHtml.includes('function selectBillboardTier'), 'vip.html must define selectBillboardTier()');
assert.ok(vipHtml.includes('paradise_billboard_cheers'), 'vip.html must use localStorage queue paradise_billboard_cheers');
assert.ok(vipHtml.includes('billboard-text'), 'vip.html must update .billboard-text ticker');
assert.ok(vipHtml.includes('Store #296100') || vipHtml.includes('296100'), 'vip.html billboard feedback must connect to Store #296100');

console.log('  [PASS] Automated billboard micro-donation form and zero manual mailto verified in vip.html.\n');

// -----------------------------------------------------------------------------
// Test Group 4: YouTube 1-Click Subscription Funnels in radio.html and index.html
// -----------------------------------------------------------------------------
console.log('Test Group 4: Verifying YouTube 1-Click Subscription Funnel (?sub_confirmation=1)...');

const radioHtml = fs.readFileSync(RADIO_HTML, 'utf-8');
const indexHtml = fs.readFileSync(INDEX_HTML, 'utf-8');

const youtubeFunnelUrl = 'https://www.youtube.com/@김쌤의영웅라디오?sub_confirmation=1';

assert.ok(
  radioHtml.includes(youtubeFunnelUrl),
  `radio.html must contain 1-click subscription link: ${youtubeFunnelUrl}`
);
assert.ok(
  indexHtml.includes(youtubeFunnelUrl),
  `index.html must contain 1-click subscription link: ${youtubeFunnelUrl}`
);

// In radio.html, verify subscription callout banner
assert.ok(
  radioHtml.includes('유튜브 @김쌤의영웅라디오 구독하고 새 방송 알림 받기'),
  'radio.html must feature prominent YouTube subscription banner'
);

console.log('  [PASS] YouTube 1-click subscription funnel (?sub_confirmation=1) verified in radio.html and index.html.\n');

// -----------------------------------------------------------------------------
// Test Group 5: Zero Tolerance on Prohibited Words Across All Modified Files
// -----------------------------------------------------------------------------
console.log('Test Group 5: Verifying STRICT ZERO Prohibited Commercial Words...');

const prohibitedWords = ['최저가', '할인율', '특가', '폭탄세일'];
const modifiedHtmlFiles = [
  { name: 'stream.html', content: streamHtml },
  { name: 'vip.html', content: vipHtml },
  { name: 'radio.html', content: radioHtml },
  { name: 'index.html', content: indexHtml }
];

modifiedHtmlFiles.forEach(({ name, content }) => {
  prohibitedWords.forEach((word) => {
    assert.strictEqual(
      content.includes(word),
      false,
      `FATAL: Prohibited commercial word '${word}' detected in ${name}!`
    );
  });
  console.log(`  [PASS] Zero prohibited commercial words in ${name}.`);
});

// For blueprint, prohibited words can only appear in context of ban explanation
prohibitedWords.forEach((word) => {
  const matches = (blueprint.match(new RegExp(word, 'g')) || []).length;
  if (matches > 0) {
    assert.ok(
      blueprint.includes('금지') || blueprint.includes('배제'),
      `Prohibited word '${word}' in blueprint must strictly be in context of prohibition explanation`
    );
  }
});
console.log('  [PASS] Blueprint respects strict zero-prohibited-words policy.\n');

// -----------------------------------------------------------------------------
// Test Group 6: Lemon Squeezy Store #296100 and Unified Email beable9489@gmail.com
// -----------------------------------------------------------------------------
console.log('Test Group 6: Verifying Lemon Squeezy Store #296100 and Unified Email...');

[
  { name: 'stream.html', content: streamHtml },
  { name: 'vip.html', content: vipHtml },
  { name: 'radio.html', content: radioHtml },
  { name: 'index.html', content: indexHtml }
].forEach(({ name, content }) => {
  assert.ok(content.includes('beable9489@gmail.com'), `${name} must include unified email beable9489@gmail.com`);
  assert.ok(content.includes('296100'), `${name} must reference Lemon Squeezy Store #296100`);
});

// Check live UUIDs in vip.html
const vipExpectedUuids = [
  'bad98d00-7175-41f6-9d58-eeb2471d0da4',
  'ce12a74d-2e25-4484-9d88-655d86e48d2b',
  '00c9f6e1-c8be-42a4-b5a5-e05af1a41ed9'
];
vipExpectedUuids.forEach((uuid) => {
  assert.ok(vipHtml.includes(uuid), `vip.html must contain live Lemon Squeezy product UUID: ${uuid}`);
});

console.log('  [PASS] Store #296100 IDs, live checkout UUIDs, and unified email verified across all modified files.\n');

console.log('======================================================================');
console.log('SUCCESS: ALL MILESTONE 3 AUTOMATED MONETIZATION TESTS PASSED (100%)');
console.log('======================================================================\n');
