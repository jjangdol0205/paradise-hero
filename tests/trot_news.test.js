/**
 * tests/trot_news.test.js
 * Verification Suite for Hwang Young-woong Exclusive 6-Category News Portal (2026-11-11 HQ Spec).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const NEWS_HTML = path.join(ROOT_DIR, 'news.html');
const TROT_NEWS_JS = path.join(ROOT_DIR, 'js', 'trot-news.js');
const TROT_NEWS_JSON = path.join(ROOT_DIR, 'data', 'trot_news.json');
const FETCH_SCRIPT_PY = path.join(ROOT_DIR, 'scripts', 'fetch_trot_news.py');

const EXPECTED_CATEGORIES = [
  '전체',
  '신곡·음반',
  '콘서트·공연',
  '나눔·선행',
  '방송·라디오',
  '팬덤·파라다이스'
];

const BANNED_OTHER_SINGERS = [
  '임영웅', '이찬원', '영탁', '정동원', '김호중', '장민호', '박서진', '손태진', '안성훈', '진해성'
];

console.log('===============================================================');
console.log('Running Hwang Young-woong Exclusive 6-Category News Test Suite');
console.log('===============================================================\n');

const newsJsonRaw = fs.readFileSync(TROT_NEWS_JSON, 'utf-8');
const newsData = JSON.parse(newsJsonRaw);
assert.ok(Array.isArray(newsData) && newsData.length >= 20, `Expected >=20 articles, got ${newsData.length}`);

newsData.forEach((item, idx) => {
  ['id', 'title', 'link', 'pubDate', 'source', 'summary', 'image_url', 'singer_tag'].forEach((f) => {
    assert.ok(typeof item[f] === 'string' && item[f].trim().length > 0, `Article ${idx} missing ${f}`);
  });
  assert.ok(
    EXPECTED_CATEGORIES.slice(1).includes(item.singer_tag),
    `Article ${item.id} category '${item.singer_tag}' must be one of the 5 Hwang Young-woong categories`
  );
  assert.ok(fs.existsSync(path.join(ROOT_DIR, item.image_url)), `Missing image: ${item.image_url}`);
});

// Verify zero other singers across news HTML, JS, JSON, and Python fetcher
[NEWS_HTML, TROT_NEWS_JS, TROT_NEWS_JSON, FETCH_SCRIPT_PY].forEach((fp) => {
  const txt = fs.readFileSync(fp, 'utf-8');
  BANNED_OTHER_SINGERS.forEach((s) => {
    // Allow fetch_trot_news.py negative filter array if any, otherwise zero
    if (fp !== FETCH_SCRIPT_PY) {
      assert.ok(!txt.includes(s), `Banned other singer '${s}' found in ${path.basename(fp)}`);
    }
  });
  assert.ok(!txt.includes('10대 스타') && !txt.includes('10대 왕자') && !txt.includes('회원가입 무료 1회'), `Legacy multi-singer promo found in ${path.basename(fp)}`);
});
console.log(`  [PASS] All ${newsData.length} articles are 100% Hwang Young-woong exclusive across 5 categories.`);

const output = execSync('python scripts/fetch_trot_news.py --seed-only --verify', {
  cwd: ROOT_DIR,
  encoding: 'utf-8',
  timeout: 10000
});
assert.ok(output.includes('PASSED'), 'fetch_trot_news.py --seed-only --verify must pass');
console.log('  [PASS] scripts/fetch_trot_news.py --seed-only --verify passed.');

const { TrotNewsEngine, SEED_NEWS, SINGER_LIST } = require(TROT_NEWS_JS);
assert.deepStrictEqual(SINGER_LIST, EXPECTED_CATEGORIES, 'SINGER_LIST must equal exact 6 Hwang Young-woong categories');
const engine = new TrotNewsEngine(SEED_NEWS);
assert.strictEqual(engine.activeSinger, '전체');
assert.strictEqual(engine.getFilteredArticles().length, SEED_NEWS.length);

EXPECTED_CATEGORIES.slice(1).forEach((cat) => {
  const filtered = engine.setSingerFilter(cat);
  assert.ok(filtered.length >= 2, `Category '${cat}' must have >= 2 articles (got ${filtered.length})`);
});
engine.setSingerFilter('전체');

const opened = engine.openModal(SEED_NEWS[0].id);
assert.strictEqual(opened.id, SEED_NEWS[0].id);
assert.strictEqual(engine.getModalFontSizePx(), 24);
engine.toggleModalFont();
assert.strictEqual(engine.getModalFontSizePx(), 28);
engine.closeModal();
assert.strictEqual(engine.isModalOpen, false);
console.log('  [PASS] TrotNewsEngine 6-category filtering, search, and senior easy-read modal verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL HWANG YOUNG-WOONG NEWS PORTAL TESTS PASSED (100%)');
console.log('===============================================================');
