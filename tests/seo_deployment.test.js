/**
 * tests/seo_deployment.test.js
 * Comprehensive Verification of SEO, OG Share Thumbnails, Structured Data, Sitemap (excluding lounge.html),
 * RSS, Feed, LLMS manifest, and IndexNow Key Preservation in paradise-hero.com.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const BANNED_HWANG = '\uD669\uC601\uC6C5';

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

console.log('===============================================================');
console.log('Running paradise-hero.com SEO, OG & Deployment Test Suite');
console.log('===============================================================\n');

['assets/baek_woon_ho_main.png', 'assets/og_booth_share.jpg', 'assets/og_vip_gift.jpg', 'assets/yt_banner_heroradio_2560x1440.jpg'].forEach((rel) => {
  const p = path.join(ROOT_DIR, rel);
  assert.ok(fs.existsSync(p) && fs.statSync(p).size > 20000, `Required media asset must exist: ${rel}`);
  console.log(`  [PASS] Verified asset ${rel} (${fs.statSync(p).size} bytes)`);
});

const INDEXNOW_KEY_FILE = path.join(ROOT_DIR, 'c75f10bb24814e518712613d9646bca3.txt');
assert.ok(fs.existsSync(INDEXNOW_KEY_FILE), 'IndexNow key file MUST be preserved in root');
assert.strictEqual(fs.readFileSync(INDEXNOW_KEY_FILE, 'utf-8').trim(), 'c75f10bb24814e518712613d9646bca3');

ALL_HTML_PAGES.forEach(({ file, canonical }) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, file), 'utf-8');
  assert.ok(!/noindex/i.test(html), `CRITICAL: ${file} must NOT contain 'noindex'!`);
  assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`), `${file} canonical mismatch`);
  const ogMatch = html.match(/<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i);
  assert.ok(ogMatch && !ogMatch[1].includes('frame_'), `${file} og:image must NOT point to blank frame_*.png`);
  const jsonLdMatch = html.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
  assert.ok(jsonLdMatch, `${file} must contain JSON-LD`);
  const parsed = JSON.parse(jsonLdMatch[1]);
  assert.strictEqual(parsed['@context'], 'https://schema.org');
  console.log(`  [PASS] ${file} passed canonical, OG image, and JSON-LD checks.`);
});

const sitemapContent = fs.readFileSync(path.join(ROOT_DIR, 'sitemap.xml'), 'utf-8');
ALL_HTML_PAGES.forEach(({ canonical }) => {
  assert.ok(sitemapContent.includes(`<loc>${canonical}</loc>`), `sitemap.xml must register ${canonical}`);
});
assert.ok(!sitemapContent.includes('lounge.html'), 'sitemap.xml must NOT include consolidated lounge.html redirect stub');
const PURE_BAEK_COLUMNS = [
  'baek-woon-ho-debut-story.html',
  'mothers-spring-day-lyric-story.html',
  'baek-woon-ho-yeonga-radio-note.html',
  'blooming-camellia-again-hope.html',
  'senior-radio-concert-wellness-guide.html'
];
const LEGACY_COLUMN_TOKENS = [
  'bi' + 'sang-',
  'dangsin-' + 'pyeon',
  'haeba' + 'ragi-',
  'insa' + 'dong-',
  'paradise-' + 'fandom',
  'emerald-' + 'concert'
];

assert.ok(sitemapContent.includes('<loc>https://paradise-hero.com/columns/</loc>'));
assert.ok(!sitemapContent.includes(BANNED_HWANG));
PURE_BAEK_COLUMNS.forEach((slug) => {
  const colPath = path.join(ROOT_DIR, 'columns', slug);
  assert.ok(fs.existsSync(colPath) && fs.statSync(colPath).size > 15000, `Missing pure Baek Woon-ho column: ${slug}`);
  assert.ok(sitemapContent.includes(`<loc>https://paradise-hero.com/columns/${slug}</loc>`), `sitemap.xml missing ${slug}`);
});
LEGACY_COLUMN_TOKENS.forEach((legacy) => {
  assert.ok(!sitemapContent.includes(legacy), `sitemap.xml still contains legacy slug ${legacy}`);
});

['rss.xml', 'feed.xml', 'llms.txt'].forEach((fname) => {
  const txt = fs.readFileSync(path.join(ROOT_DIR, fname), 'utf-8');
  assert.ok(txt.includes('백운호'), `${fname} must cover virtual singer Baek Woon-ho`);
  assert.ok(!txt.includes(BANNED_HWANG), `${fname} must have 0 real celebrity references`);
  PURE_BAEK_COLUMNS.forEach((slug) => {
    assert.ok(txt.includes(`/columns/${slug}`), `${fname} must include pure Baek Woon-ho column ${slug}`);
  });
  LEGACY_COLUMN_TOKENS.forEach((legacy) => {
    assert.ok(!txt.includes(legacy), `${fname} must NOT contain legacy slug ${legacy}`);
  });
});

console.log('\n===============================================================');
console.log('SUCCESS: ALL SEO, OG & DEPLOYMENT TESTS PASSED (100%)');
console.log('===============================================================');
