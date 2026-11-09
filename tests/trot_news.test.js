/**
 * tests/trot_news.test.js
 * =======================
 * Automated Verification Test Suite for Milestone 1 (F1, F2, F3):
 * Trot RSS News Traffic Portal, News Ingestion Pipeline, Naver News Layout,
 * Senior WCAG AAA Ergonomics, SEO Metadata, and Zero Prohibited Words.
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
const THIS_TEST_FILE = path.join(ROOT_DIR, 'tests', 'trot_news.test.js');

// Prohibited Commercial Words (assembled to prevent static false alarms)
const PROHIBITED_WORDS = [
  '최' + '저가',
  '할' + '인율',
  '특' + '가',
  '폭' + '탄세일'
];

const REQUIRED_10_SINGERS = [
  '황영웅',
  '임영웅',
  '이찬원',
  '영탁',
  '정동원',
  '김호중',
  '장민호',
  '박서진',
  '손태진',
  '안성훈/진해성'
];

console.log('===============================================================');
console.log('Running paradise-hero.com Milestone 1: Trot News Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Physical File Existence & Substantive Sizes
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence and substantive sizes...');

const ownedFiles = [
  { file: 'news.html', path: NEWS_HTML, minSize: 3000 },
  { file: 'js/trot-news.js', path: TROT_NEWS_JS, minSize: 3000 },
  { file: 'data/trot_news.json', path: TROT_NEWS_JSON, minSize: 2000 },
  { file: 'scripts/fetch_trot_news.py', path: FETCH_SCRIPT_PY, minSize: 2000 },
  { file: 'tests/trot_news.test.js', path: THIS_TEST_FILE, minSize: 1500 }
];

ownedFiles.forEach(({ file, path: filePath, minSize }) => {
  assert.ok(fs.existsSync(filePath), `Required owned file missing: ${file}`);
  const stat = fs.statSync(filePath);
  assert.ok(stat.size >= minSize, `${file} must be substantive (>=${minSize} bytes, got ${stat.size})`);
  console.log(`  [PASS] Verified ${file} (${stat.size} bytes)`);
});

// -----------------------------------------------------------------------------
// Test 2: Data Integrity in data/trot_news.json
// -----------------------------------------------------------------------------
console.log('\nTest 2: Verifying data/trot_news.json schema and 10-singer coverage...');

const newsJsonRaw = fs.readFileSync(TROT_NEWS_JSON, 'utf-8');
let newsData = null;
assert.doesNotThrow(() => {
  newsData = JSON.parse(newsJsonRaw);
}, 'data/trot_news.json must be valid JSON');

assert.ok(Array.isArray(newsData), 'data/trot_news.json must be an array');
assert.ok(newsData.length >= 20, `Expected at least 20 articles, found ${newsData.length}`);

// Verify required fields
const requiredFields = ['id', 'title', 'link', 'pubDate', 'source', 'summary', 'image_url', 'singer_tag'];
newsData.forEach((item, idx) => {
  requiredFields.forEach((field) => {
    assert.ok(
      typeof item[field] === 'string' && item[field].trim().length > 0,
      `Article at index ${idx} missing or invalid field '${field}'`
    );
  });
  // Check valid date format
  const parsedDate = new Date(item.pubDate);
  assert.ok(!isNaN(parsedDate.getTime()), `Article ${item.id} has invalid pubDate: ${item.pubDate}`);
});

// Physical file existence assertion for all news article images
newsData.forEach((item) => {
  const imgFullPath = path.join(ROOT_DIR, item.image_url);
  assert.ok(
    fs.existsSync(imgFullPath),
    `News image file must physically exist on disk: ${item.image_url} (Article ${item.id})`
  );
});
console.log(`  [PASS] All ${newsData.length} news article images physically verified on disk.`);

// Verify coverage of all 10 singers
const representedSingers = new Set(newsData.map(item => item.singer_tag));
REQUIRED_10_SINGERS.forEach((singer) => {
  const covered = Array.from(representedSingers).some(tag => 
    tag === singer || (singer === '안성훈/진해성' && (tag === '안성훈' || tag === '진해성' || tag === '안성훈/진해성'))
  );
  assert.ok(covered, `Missing article coverage for required singer: ${singer}`);
  console.log(`  [PASS] Verified coverage for singer: ${singer}`);
});

// -----------------------------------------------------------------------------
// Test 3: Python RSS Ingestion Script (scripts/fetch_trot_news.py)
// -----------------------------------------------------------------------------
console.log('\nTest 3: Verifying scripts/fetch_trot_news.py script execution and offline mode...');

const pyContent = fs.readFileSync(FETCH_SCRIPT_PY, 'utf-8');
assert.ok(pyContent.includes('--offline') || pyContent.includes('--seed-only'), 'Script must support offline seed generation');
assert.ok(pyContent.includes('sanitize_and_deduplicate') || pyContent.includes('deduplicate'), 'Script must have deduplication');
assert.ok(pyContent.includes('TROT_SINGERS'), 'Script must configure 10 trot singers');

// Run deterministic seed test command
try {
  const output = execSync('python scripts/fetch_trot_news.py --seed-only --verify', {
    cwd: ROOT_DIR,
    encoding: 'utf-8',
    timeout: 10000
  });
  assert.ok(output.includes('PASSED'), 'fetch_trot_news.py output must indicate integrity pass');
  console.log('  [PASS] fetch_trot_news.py executed and passed verification successfully.');
} catch (err) {
  assert.fail(`fetch_trot_news.py execution failed: ${err.message}`);
}

// -----------------------------------------------------------------------------
// Test 4: Client JS Engine (js/trot-news.js)
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying js/trot-news.js client controller and state machine...');

const { TrotNewsEngine, SEED_NEWS, SINGER_LIST } = require(TROT_NEWS_JS);

assert.ok(typeof TrotNewsEngine === 'function', 'TrotNewsEngine class must be exported');
assert.ok(Array.isArray(SEED_NEWS) && SEED_NEWS.length >= 20, 'SEED_NEWS must contain at least 20 items');
assert.ok(Array.isArray(SINGER_LIST) && SINGER_LIST.length === 11, 'SINGER_LIST must contain 11 options (전체 + 10 singers)');

REQUIRED_10_SINGERS.forEach(singer => {
  assert.ok(SINGER_LIST.includes(singer), `SINGER_LIST must include ${singer}`);
});

// Physical file existence assertion for SEED_NEWS items
SEED_NEWS.forEach((item) => {
  const imgFullPath = path.join(ROOT_DIR, item.image_url);
  assert.ok(
    fs.existsSync(imgFullPath),
    `SEED_NEWS image file must physically exist on disk: ${item.image_url} (Article ${item.id})`
  );
});
console.log(`  [PASS] All ${SEED_NEWS.length} SEED_NEWS article images physically verified on disk.`);

// Instantiate engine with SEED_NEWS
const engine = new TrotNewsEngine(SEED_NEWS);

// Test 4.1: Initial State
assert.strictEqual(engine.activeSinger, '전체');
assert.strictEqual(engine.getFilteredArticles().length, SEED_NEWS.length);

// Test 4.2: Singer Filtering
const hywArticles = engine.setSingerFilter('황영웅');
assert.ok(hywArticles.length >= 2, 'Should find at least 2 Hwang Young-woong articles');
hywArticles.forEach(a => assert.strictEqual(a.singer_tag, '황영웅'));

const ashJhsArticles = engine.setSingerFilter('안성훈/진해성');
assert.ok(ashJhsArticles.length >= 2, 'Should find at least 2 articles for Ahn Sung-hoon / Jin Hae-seong');
ashJhsArticles.forEach(a => {
  assert.ok(
    a.singer_tag === '안성훈/진해성' || a.singer_tag === '안성훈' || a.singer_tag === '진해성',
    `Unexpected tag in filtered result: ${a.singer_tag}`
  );
});

// Reset to 전체
engine.setSingerFilter('전체');
assert.strictEqual(engine.getFilteredArticles().length, SEED_NEWS.length);

// Test 4.3: Keyword Search
const searchResult = engine.setSearchQuery('당신 편');
assert.ok(searchResult.length >= 1, "Search for '당신 편' should yield results");
searchResult.forEach(a => {
  const match = (a.title + a.summary).includes('당신 편');
  assert.ok(match, "Searched article must contain '당신 편'");
});
engine.setSearchQuery(''); // reset

// Test 4.4: Modal Viewer Lifecycle & Font Scaling
const targetArticle = SEED_NEWS[0];
const opened = engine.openModal(targetArticle.id);
assert.strictEqual(opened.id, targetArticle.id);
assert.strictEqual(engine.isModalOpen, true);
assert.strictEqual(engine.getModalFontSizePx(), 24); // Base 24px+

engine.toggleModalFont(); // large
assert.strictEqual(engine.getModalFontSizePx(), 28);

engine.toggleModalFont(); // xlarge
assert.strictEqual(engine.getModalFontSizePx(), 32);

engine.toggleModalFont(); // back to normal
assert.strictEqual(engine.getModalFontSizePx(), 24);

engine.closeModal();
assert.strictEqual(engine.isModalOpen, false);
assert.strictEqual(engine.currentModalArticle, null);

console.log('  [PASS] js/trot-news.js engine filtering, search, and modal lifecycle verified.');

// -----------------------------------------------------------------------------
// Test 5: Semantic HTML5, Naver News Layout & WCAG AAA Ergonomics (news.html)
// -----------------------------------------------------------------------------
console.log('\nTest 5: Verifying news.html semantics, Naver News layout, and WCAG AAA ergonomics...');

const newsHtml = fs.readFileSync(NEWS_HTML, 'utf-8');

// HTML5 Basics
assert.ok(newsHtml.includes('<!DOCTYPE html>'), 'news.html must declare HTML5 doctype');
assert.ok(newsHtml.includes('<html lang="ko">'), 'news.html must have lang="ko"');
assert.ok(newsHtml.includes('<meta charset="UTF-8">'), 'news.html must have charset UTF-8');
assert.ok(newsHtml.includes('name="viewport"'), 'news.html must have viewport meta');

// Skip navigation link
assert.ok(newsHtml.includes('class="skip-link"'), 'news.html must have accessible skip link');
assert.ok(newsHtml.includes('id="main-content"'), 'news.html must have #main-content');

// Portal Layout Components
assert.ok(newsHtml.includes('id="news-search-input"'), 'news.html must have search input');
assert.ok(newsHtml.includes('id="singer-pills-container"'), 'news.html must have 10-singer pills container');
assert.ok(newsHtml.includes('id="news-hero-spotlight"'), 'news.html must have hero breaking spotlight section');
assert.ok(newsHtml.includes('id="news-feed-grid"'), 'news.html must have news feed grid');

// Senior Easy-Read Modal
assert.ok(newsHtml.includes('id="senior-news-modal"'), 'news.html must have senior easy-read modal viewer');
assert.ok(newsHtml.includes('role="dialog"'), 'modal must have role="dialog"');
assert.ok(newsHtml.includes('aria-modal="true"'), 'modal must have aria-modal="true"');
assert.ok(newsHtml.includes('id="btn-close-modal"'), 'modal must have close button');
assert.ok(newsHtml.includes('id="btn-modal-font-scaler"'), 'modal must have font size scaler');
assert.ok(newsHtml.includes('id="btn-modal-external-link"'), 'modal must have external news link');
assert.ok(newsHtml.includes('id="btn-modal-share"'), 'modal must have share button');

// Ergonomics & Styles
assert.ok(newsHtml.includes('--touch-min-height: 56px') || newsHtml.includes('56px'), 'Touch targets must be min 56px');
assert.ok(newsHtml.includes('#FAFAF8') || newsHtml.includes('var(--bg-canvas)'), 'High contrast soft ivory background required');
assert.ok(newsHtml.includes('24px'), 'Modal viewer must support 24px+ base font');

// Required Scripts
assert.ok(newsHtml.includes('src="js/senior-accessibility.js"'), 'Must load senior-accessibility.js');
assert.ok(newsHtml.includes('src="js/radio-player.js"'), 'Must load radio-player.js');
assert.ok(newsHtml.includes('src="js/trot-news.js"'), 'Must load trot-news.js');
console.log('  [PASS] news.html passed semantic HTML5, Naver News layout, and ergonomics audits.');

// -----------------------------------------------------------------------------
// Test 6: Contextual CTA Cards Linking to Photo Booth and Radio
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying contextual CTA cards linking to Photo Booth and Radio...');

const trotNewsJsContent = fs.readFileSync(TROT_NEWS_JS, 'utf-8');

assert.ok(
  trotNewsJsContent.includes('booth.html'),
  'js/trot-news.js must contain contextual CTA link to booth.html'
);
assert.ok(
  trotNewsJsContent.includes('radio.html'),
  'js/trot-news.js must contain contextual CTA link to radio.html'
);
assert.ok(
  newsHtml.includes('booth.html'),
  'news.html navigation must link to booth.html'
);
assert.ok(
  newsHtml.includes('radio.html'),
  'news.html navigation must link to radio.html'
);
console.log('  [PASS] Contextual CTA cards and navigation links verified.');

// Verify all onerror fallbacks in js/trot-news.js physically exist
const onerrorMatches = Array.from(trotNewsJsContent.matchAll(/this\.src='([^']+)'/g));
assert.ok(onerrorMatches.length > 0, 'Expected at least one onerror fallback in js/trot-news.js');
onerrorMatches.forEach((m) => {
  const fallbackPath = path.join(ROOT_DIR, m[1]);
  assert.ok(
    fs.existsSync(fallbackPath),
    `Onerror fallback image must physically exist on disk: ${m[1]}`
  );
  console.log(`  [PASS] Verified onerror fallback image exists: ${m[1]}`);
});

// -----------------------------------------------------------------------------
// Test 7: Standard SEO Meta Tags & STRICT ZERO noindex
// -----------------------------------------------------------------------------
console.log('\nTest 7: Verifying standard SEO meta tags and STRICT ZERO noindex...');

// STRICT ZERO noindex
assert.ok(!/noindex/i.test(newsHtml), "CRITICAL: news.html must NOT contain 'noindex'!");

// Standard robots & googlebot
assert.ok(
  newsHtml.includes('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'),
  'news.html must contain standardized <meta name="robots">'
);
assert.ok(
  newsHtml.includes('<meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'),
  'news.html must contain standardized <meta name="googlebot">'
);

// Canonical link
assert.ok(
  newsHtml.includes('<link rel="canonical" href="https://paradise-hero.com/news.html">'),
  'news.html must contain canonical link to https://paradise-hero.com/news.html'
);

// OpenGraph & Twitter
assert.ok(newsHtml.includes('property="og:site_name"'), 'news.html must have og:site_name');
assert.ok(newsHtml.includes('property="og:title"'), 'news.html must have og:title');
assert.ok(newsHtml.includes('property="og:url"'), 'news.html must have og:url');
assert.ok(newsHtml.includes('name="twitter:card"'), 'news.html must have twitter:card');

// Verify OpenGraph and Twitter images physically exist on disk
const metaImages = Array.from(newsHtml.matchAll(/<meta\s+(?:property="og:image"|name="twitter:image")\s+content="https:\/\/paradise-hero\.com\/([^"]+)"/g));
assert.ok(metaImages.length >= 2, 'Expected og:image and twitter:image in news.html');
metaImages.forEach((m) => {
  const metaImgPath = path.join(ROOT_DIR, m[1]);
  assert.ok(
    fs.existsSync(metaImgPath),
    `Social meta tag image must physically exist on disk: ${m[1]}`
  );
  console.log(`  [PASS] Verified meta tag image exists: ${m[1]}`);
});

// JSON-LD structured data
const jsonLdMatch = newsHtml.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
assert.ok(jsonLdMatch, 'news.html must contain JSON-LD script block');
let parsedLd = null;
assert.doesNotThrow(() => {
  parsedLd = JSON.parse(jsonLdMatch[1]);
}, 'JSON-LD must be valid JSON');
assert.strictEqual(parsedLd['@context'], 'https://schema.org', 'JSON-LD must have @context https://schema.org');
assert.ok(Array.isArray(parsedLd['@graph']), 'JSON-LD must have @graph array');

const graphTypes = parsedLd['@graph'].map(g => g['@type']);
assert.ok(graphTypes.includes('WebSite') || graphTypes.includes('CollectionPage'), 'JSON-LD graph must include WebSite or CollectionPage');
assert.ok(graphTypes.includes('ItemList'), 'JSON-LD graph must include ItemList of news articles');
console.log('  [PASS] news.html passed robots, googlebot, canonical, OG, Twitter, and JSON-LD audits.');

// -----------------------------------------------------------------------------
// Test 8: STRICT ZERO Prohibited Commercial Words Audit
// -----------------------------------------------------------------------------
console.log('\nTest 8: Auditing STRICT ZERO prohibited words (' + PROHIBITED_WORDS.join(', ') + ')...');

ownedFiles.forEach(({ file, path: filePath }) => {
  const content = fs.readFileSync(filePath, 'utf-8');
  PROHIBITED_WORDS.forEach((banned) => {
    // If the file is the test file itself, ignore definition line
    if (file === 'tests/trot_news.test.js') {
      const lines = content.split('\n');
      lines.forEach((line, lineNo) => {
        if (!line.includes('const PROHIBITED_WORDS') && !line.includes("'최' + '저가'")) {
          assert.ok(
            !line.includes(banned),
            `VIOLATION: Prohibited word '${banned}' found in ${file}:${lineNo + 1}`
          );
        }
      });
    } else {
      assert.ok(
        !content.includes(banned),
        `VIOLATION: Prohibited word '${banned}' found in ${file}`
      );
    }
  });
  console.log(`  [PASS] 0 prohibited words found in ${file}`);
});

// -----------------------------------------------------------------------------
// Test 9: Contact Email & Store #296100 Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 9: Verifying unified contact email and Store #296100 compliance...');

assert.ok(newsHtml.includes('beable9489@gmail.com'), 'news.html must feature unified contact email beable9489@gmail.com');
assert.ok(newsHtml.includes('Store #296100') || newsHtml.includes('296100'), 'news.html must mention Lemon Squeezy Store #296100');
console.log('  [PASS] Unified email and Store #296100 verified.');

console.log('\n===============================================================');
console.log('SUCCESS: ALL MILESTONE 1 TROT NEWS TESTS PASSED (100%)');
console.log('===============================================================');
