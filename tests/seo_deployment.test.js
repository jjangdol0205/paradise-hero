/**
 * tests/seo_deployment.test.js
 * =============================
 * Milestone 4 Automated Test Suite:
 * Comprehensive Verification of SEO, Structured Data, Sitemap, RSS, Robots,
 * LLMS manifest, IndexNow Submission, and Zero Prohibited Words in paradise-hero.com.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');

const ALL_HTML_PAGES = [
  { file: 'index.html', canonical: 'https://paradise-hero.com/' },
  { file: 'story.html', canonical: 'https://paradise-hero.com/story.html' },
  { file: 'booth.html', canonical: 'https://paradise-hero.com/booth.html' },
  { file: 'photobooth.html', canonical: 'https://paradise-hero.com/photobooth.html' },
  { file: 'radio.html', canonical: 'https://paradise-hero.com/radio.html' },
  { file: 'community.html', canonical: 'https://paradise-hero.com/community.html' },
  { file: 'stream.html', canonical: 'https://paradise-hero.com/stream.html' },
  { file: 'vip.html', canonical: 'https://paradise-hero.com/vip.html' },
  { file: 'news.html', canonical: 'https://paradise-hero.com/news.html' }
];

const PROHIBITED_WORDS = ['최저가', '할인율', '특가', '폭탄세일'];

console.log('===============================================================');
console.log('Running paradise-hero.com Milestone 4 SEO & Deployment Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Physical File Existence
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence of all deployment assets...');

ALL_HTML_PAGES.forEach(({ file }) => {
  const p = path.join(ROOT_DIR, file);
  assert.ok(fs.existsSync(p), `Required HTML file missing: ${file}`);
  const s = fs.statSync(p).size;
  assert.ok(s > 2000, `${file} must be substantive (>2KB, got ${s} bytes)`);
  console.log(`  [PASS] Verified ${file} (${s} bytes)`);
});

const SITEMAP_FILE = path.join(ROOT_DIR, 'sitemap.xml');
const RSS_FILE = path.join(ROOT_DIR, 'rss.xml');
const ROBOTS_FILE = path.join(ROOT_DIR, 'robots.txt');
const LLMS_FILE = path.join(ROOT_DIR, 'llms.txt');
const INDEXNOW_SCRIPT = path.join(ROOT_DIR, 'scripts', 'submit_indexnow.py');
const INDEXNOW_KEY_FILE = path.join(ROOT_DIR, 'c75f10bb24814e518712613d9646bca3.txt');

assert.ok(fs.existsSync(SITEMAP_FILE), 'sitemap.xml must exist');
assert.ok(fs.existsSync(RSS_FILE), 'rss.xml must exist');
assert.ok(fs.existsSync(ROBOTS_FILE), 'robots.txt must exist');
assert.ok(fs.existsSync(LLMS_FILE), 'llms.txt must exist');
assert.ok(fs.existsSync(INDEXNOW_SCRIPT), 'scripts/submit_indexnow.py must exist');
assert.ok(fs.existsSync(INDEXNOW_KEY_FILE), 'IndexNow key file must exist in root');
console.log('  [PASS] All metadata, feeds, manifests, and deployment scripts exist.');

// -----------------------------------------------------------------------------
// Test 2: SEO Meta Tags & STRICT ZERO noindex across ALL 8 HTML Pages
// -----------------------------------------------------------------------------
console.log(`\nTest 2: Verifying SEO meta tags, Googlebot, and STRICT ZERO noindex across all ${ALL_HTML_PAGES.length} HTML pages...`);

ALL_HTML_PAGES.forEach(({ file, canonical }) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, file), 'utf-8');

  // STRICT ZERO noindex
  assert.ok(!/noindex/i.test(html), `CRITICAL: ${file} must NOT contain 'noindex'!`);

  // Robots meta
  assert.ok(
    html.includes('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'),
    `${file} must contain full standardized <meta name="robots"> tag`
  );

  // Googlebot meta
  assert.ok(
    html.includes('<meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'),
    `${file} must contain full standardized <meta name="googlebot"> tag`
  );

  // Canonical URL
  const canonicalExpected = `<link rel="canonical" href="${canonical}">`;
  assert.ok(html.includes(canonicalExpected), `${file} must contain exact canonical tag: ${canonicalExpected}`);

  // OpenGraph tags
  assert.ok(/<meta\s+property=["']og:site_name["']/i.test(html), `${file} must have og:site_name`);
  assert.ok(/<meta\s+property=["']og:type["']/i.test(html), `${file} must have og:type`);
  assert.ok(/<meta\s+property=["']og:title["']/i.test(html), `${file} must have og:title`);
  assert.ok(/<meta\s+property=["']og:description["']/i.test(html), `${file} must have og:description`);
  assert.ok(/<meta\s+property=["']og:url["']/i.test(html), `${file} must have og:url`);
  assert.ok(/<meta\s+property=["']og:image["']/i.test(html), `${file} must have og:image`);

  // JSON-LD structured data
  const jsonLdMatch = html.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
  assert.ok(jsonLdMatch, `${file} must contain <script type="application/ld+json">`);
  let parsed = null;
  assert.doesNotThrow(() => {
    parsed = JSON.parse(jsonLdMatch[1]);
  }, `${file} JSON-LD content must be valid JSON`);
  assert.ok(parsed && parsed['@context'] === 'https://schema.org', `${file} JSON-LD must use @context https://schema.org`);
  assert.ok(Array.isArray(parsed['@graph']) && parsed['@graph'].length >= 1, `${file} JSON-LD must contain @graph array`);

  console.log(`  [PASS] ${file} passed robots, googlebot, canonical, OG, and JSON-LD audits.`);
});

// -----------------------------------------------------------------------------
// Test 3: Sitemap.xml Completeness & lastmod 2026-11-09
// -----------------------------------------------------------------------------
console.log('\nTest 3: Verifying sitemap.xml coverage, lastmod dates, changefreq, and priorities...');

const sitemapContent = fs.readFileSync(SITEMAP_FILE, 'utf-8');
assert.ok(sitemapContent.startsWith('<?xml'), 'sitemap.xml must be valid XML declaration');

ALL_HTML_PAGES.forEach(({ canonical }) => {
  assert.ok(sitemapContent.includes(`<loc>${canonical}</loc>`), `sitemap.xml must register ${canonical}`);
});

const lastmodCount = (sitemapContent.match(/<lastmod>2026-11-09<\/lastmod>/g) || []).length;
assert.strictEqual(lastmodCount, ALL_HTML_PAGES.length, `All ${ALL_HTML_PAGES.length} entries must have <lastmod>2026-11-09</lastmod>`);

const changefreqCount = (sitemapContent.match(/<changefreq>(daily|weekly)<\/changefreq>/g) || []).length;
assert.strictEqual(changefreqCount, ALL_HTML_PAGES.length, 'All entries in sitemap must define changefreq');

const priorityCount = (sitemapContent.match(/<priority>[0-1]\.[0-9]<\/priority>/g) || []).length;
assert.strictEqual(priorityCount, ALL_HTML_PAGES.length, 'All entries in sitemap must define priority');
console.log(`  [PASS] sitemap.xml verified (${ALL_HTML_PAGES.length} URLs registered, 100% lastmod 2026-11-09, valid priority & changefreq)`);

// -----------------------------------------------------------------------------
// Test 4: RSS 2.0 Feed Validity & Channel Items
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying rss.xml 2.0 schema, channels, and multi-channel items...');

const rssContent = fs.readFileSync(RSS_FILE, 'utf-8');
assert.ok(rssContent.includes('<rss version="2.0"'), 'rss.xml must be RSS 2.0');
assert.ok(rssContent.includes('<channel>'), 'rss.xml must have <channel>');
assert.ok(rssContent.includes('<title>'), 'rss.xml must have channel title');
assert.ok(rssContent.includes('<link>https://paradise-hero.com/</link>'), 'rss.xml must link to domain');
assert.ok(rssContent.includes('2026'), 'rss.xml must contain 2026 dates');

const itemCount = (rssContent.match(/<item>/g) || []).length;
assert.ok(itemCount >= 4, `rss.xml must contain at least 4 items, got ${itemCount}`);
assert.ok(rssContent.includes('story.html'), 'rss.xml must feature story hub');
assert.ok(rssContent.includes('booth.html'), 'rss.xml must feature photo booth');
assert.ok(rssContent.includes('radio.html'), 'rss.xml must feature radio episodes');
assert.ok(rssContent.includes('news.html'), 'rss.xml must feature trot news portal');
console.log(`  [PASS] rss.xml verified (${itemCount} items, dated 2026-11-09, covering story hub, photo booth, and trot news)`);

// -----------------------------------------------------------------------------
// Test 5: Robots.txt Specification
// -----------------------------------------------------------------------------
console.log('\nTest 5: Verifying robots.txt directives and sitemap declaration...');

const robotsContent = fs.readFileSync(ROBOTS_FILE, 'utf-8');
assert.ok(robotsContent.includes('User-agent: *'), 'robots.txt must set User-agent: *');
assert.ok(robotsContent.includes('Allow: /'), 'robots.txt must set Allow: /');
assert.ok(robotsContent.includes('Sitemap: https://paradise-hero.com/sitemap.xml'), 'robots.txt must declare sitemap location');
assert.ok(!robotsContent.includes('Disallow: /'), 'robots.txt must not disallow root');
console.log('  [PASS] robots.txt verified (open crawling allowed, sitemap linked)');

// -----------------------------------------------------------------------------
// Test 6: LLMS.txt AI Manifest
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying llms.txt AI search manifest...');

const llmsContent = fs.readFileSync(LLMS_FILE, 'utf-8');
assert.ok(llmsContent.includes('# Paradise Hero'), 'llms.txt must have title');
assert.ok(llmsContent.includes('beable9489@gmail.com'), 'llms.txt must list unified contact email');
ALL_HTML_PAGES.forEach(({ file }) => {
  const check = file === 'index.html' ? 'https://paradise-hero.com/' : file;
  assert.ok(llmsContent.includes(check), `llms.txt must index endpoint: ${check}`);
});
assert.ok(llmsContent.includes('WCAG AAA'), 'llms.txt must describe WCAG AAA accessibility standard');
console.log(`  [PASS] llms.txt verified (${llmsContent.length} chars, indexing all ${ALL_HTML_PAGES.length} endpoints)`);

// -----------------------------------------------------------------------------
// Test 7: IndexNow Submission Script & Key Verification
// -----------------------------------------------------------------------------
console.log('\nTest 7: Verifying IndexNow Python submission script and verification key...');

const indexNowScriptContent = fs.readFileSync(INDEXNOW_SCRIPT, 'utf-8');
assert.ok(indexNowScriptContent.includes('api.indexnow.org'), 'submit_indexnow.py must target api.indexnow.org');
assert.ok(indexNowScriptContent.includes('bing.com/indexnow'), 'submit_indexnow.py must target bing.com/indexnow');
assert.ok(indexNowScriptContent.includes('c75f10bb24814e518712613d9646bca3'), 'submit_indexnow.py must contain key');

const keyFileContent = fs.readFileSync(INDEXNOW_KEY_FILE, 'utf-8').trim();
assert.strictEqual(keyFileContent, 'c75f10bb24814e518712613d9646bca3', 'Key file content must match KEY');
console.log('  [PASS] IndexNow script and key file verified.');

// -----------------------------------------------------------------------------
// Test 8: STRICT ZERO Prohibited Commercial Words Audit
// -----------------------------------------------------------------------------
console.log('\nTest 8: Verifying STRICT ZERO prohibited words (최저가, 할인율, 특가, 폭탄세일)...');

const filesToAudit = [
  ...ALL_HTML_PAGES.map(p => p.file),
  'sitemap.xml',
  'rss.xml',
  'robots.txt',
  'llms.txt',
  path.join('scripts', 'submit_indexnow.py')
];

filesToAudit.forEach((relPath) => {
  const content = fs.readFileSync(path.join(ROOT_DIR, relPath), 'utf-8');
  PROHIBITED_WORDS.forEach((word) => {
    assert.ok(
      !content.includes(word),
      `VIOLATION: Prohibited word '${word}' found in ${relPath}`
    );
  });
});
console.log(`  [PASS] 0 prohibited words found across all ${filesToAudit.length} deployment files.`);

console.log('\n===============================================================');
console.log('SUCCESS: ALL MILESTONE 4 SEO & DEPLOYMENT TESTS PASSED (100%)');
console.log('===============================================================');
