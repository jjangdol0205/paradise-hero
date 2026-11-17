/**
 * tests/trot_news.test.js
 * Verification Suite for Honest @김쌤의영웅라디오 Tue/Fri Schedule & Virtual Singer Baek Woon-ho News Portal.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execFileSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const NEWS_HTML = path.join(ROOT_DIR, 'news.html');
const TROT_NEWS_JS = path.join(ROOT_DIR, 'js', 'trot-news.js');
const TROT_NEWS_JSON = path.join(ROOT_DIR, 'data', 'trot_news.json');

const EXPECTED_CATEGORIES = [
  '전체',
  '정규방송·편성표',
  '백운호 대표곡',
  '사랑방 사연소식',
  '시니어 건강상식',
  '라디오 이용안내'
];

const BANNED_CELEBS = [
  '\uD669\uC601\uC6C5', '\uC784\uC601\uC6C5', '\uC774\uCC2C\uC6D0', '\uC601\uD0C1',
  '\uC815\uB3D9\uC6D0', '\uAE40\uD638\uC911', '\uC7A5\uBBFC\uD638', '\uBC15\uC11C\uC9C4',
  '\uC190\uD0DC\uC9C4', '\uC548\uC131\uD6C8', '\uC9C4\uD574\uC131'
];

console.log('===============================================================');
console.log('Running Honest @김쌤의영웅라디오 Schedule & Baek Woon-ho News Suite');
console.log('===============================================================\n');

const newsJsonRaw = fs.readFileSync(TROT_NEWS_JSON, 'utf-8');
const newsData = JSON.parse(newsJsonRaw);
assert.ok(Array.isArray(newsData) && newsData.length >= 20, `Expected >=20 items, got ${newsData.length}`);

newsData.forEach((item, idx) => {
  ['id', 'title', 'link', 'pubDate', 'source', 'summary', 'image_url', 'singer_tag'].forEach((f) => {
    assert.ok(typeof item[f] === 'string' && item[f].trim().length > 0, `Item ${idx} missing ${f}`);
  });
  assert.ok(EXPECTED_CATEGORIES.slice(1).includes(item.singer_tag), `Invalid tag ${item.singer_tag}`);
  assert.ok(fs.existsSync(path.join(ROOT_DIR, item.image_url)), `Missing image: ${item.image_url}`);
});

[NEWS_HTML, TROT_NEWS_JS, TROT_NEWS_JSON].forEach((fp) => {
  const txt = fs.readFileSync(fp, 'utf-8');
  BANNED_CELEBS.forEach((s) => {
    assert.ok(!txt.includes(s), `Banned celebrity '${s}' found in ${path.basename(fp)}`);
  });
});

const output = execFileSync('python', ['scripts/fetch_trot_news.py', '--seed-only', '--verify'], {
  cwd: ROOT_DIR,
  encoding: 'utf-8',
  timeout: 60000
});
assert.ok(output.includes('PASSED'), 'fetch_trot_news.py --seed-only --verify must pass');

const { TrotNewsEngine, SEED_NEWS, SINGER_LIST } = require(TROT_NEWS_JS);
assert.deepStrictEqual(SINGER_LIST, EXPECTED_CATEGORIES);
const engine = new TrotNewsEngine(SEED_NEWS);
assert.strictEqual(engine.activeSinger, '전체');
assert.strictEqual(engine.getFilteredArticles().length, SEED_NEWS.length);

EXPECTED_CATEGORIES.slice(1).forEach((cat) => {
  const filtered = engine.setSingerFilter(cat);
  assert.ok(filtered.length >= 4, `Category '${cat}' must have >= 4 notices`);
});
engine.setSingerFilter('전체');

const opened = engine.openModal(SEED_NEWS[0].id);
assert.strictEqual(opened.id, SEED_NEWS[0].id);
assert.strictEqual(engine.getModalFontSizePx(), 24);
engine.toggleModalFont();
assert.strictEqual(engine.getModalFontSizePx(), 28);
engine.closeModal();
assert.strictEqual(engine.isModalOpen, false);
console.log('  [PASS] Honest 6-category radio schedule & Baek Woon-ho notice engine verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL HONEST NEWS & SCHEDULE TESTS PASSED (100%)');
console.log('===============================================================');
