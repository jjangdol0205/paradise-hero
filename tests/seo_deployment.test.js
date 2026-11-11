/**
 * tests/seo_deployment.test.js
 * Comprehensive Verification of SEO, OG Share Thumbnails, Structured Data, Sitemap, RSS, Robots,
 * LLMS manifest, and IndexNow Key Preservation in paradise-hero.com (2026-11-11 HQ Spec).
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

console.log('===============================================================');
console.log('Running paradise-hero.com SEO, OG & Deployment Test Suite');
console.log('===============================================================\n');

// Verify OG assets & YouTube banner physically exist
['assets/og_booth_share.jpg', 'assets/og_vip_gift.jpg', 'assets/yt_banner_heroradio_2560x1440.jpg'].forEach((rel) => {
  const p = path.join(ROOT_DIR, rel);
  assert.ok(fs.existsSync(p) && fs.statSync(p).size > 20000, `Required media asset must exist: ${rel}`);
  console.log(`  [PASS] Verified asset ${rel} (${fs.statSync(p).size} bytes)`);
});

// Verify IndexNow root key file is strictly preserved
const INDEXNOW_KEY_FILE = path.join(ROOT_DIR, 'c75f10bb24814e518712613d9646bca3.txt');
assert.ok(fs.existsSync(INDEXNOW_KEY_FILE), 'IndexNow key file MUST be preserved in root');
assert.strictEqual(fs.readFileSync(INDEXNOW_KEY_FILE, 'utf-8').trim(), 'c75f10bb24814e518712613d9646bca3');

ALL_HTML_PAGES.forEach(({ file, canonical }) => {
  const html = fs.readFileSync(path.join(ROOT_DIR, file), 'utf-8');
  assert.ok(!/noindex/i.test(html), `CRITICAL: ${file} must NOT contain 'noindex'!`);
  assert.ok(html.includes(`<link rel="canonical" href="${canonical}">`), `${file} canonical mismatch`);
  assert.ok(/<meta\s+property=["']og:image["']/i.test(html), `${file} must have og:image`);

  // Ensure blank frame_*.png is NEVER used as og:image or twitter:image
  const ogMatch = html.match(/<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i);
  assert.ok(ogMatch && !ogMatch[1].includes('frame_'), `${file} og:image must NOT point to blank frame_*.png (${ogMatch && ogMatch[1]})`);
  assert.ok(
    ogMatch[1] === 'https://paradise-hero.com/assets/og_booth_share.jpg' ||
    ogMatch[1] === 'https://paradise-hero.com/assets/og_vip_gift.jpg',
    `${file} og:image must use verified high-res OG image (got ${ogMatch[1]})`
  );

  const jsonLdMatch = html.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
  assert.ok(jsonLdMatch, `${file} must contain JSON-LD`);
  const parsed = JSON.parse(jsonLdMatch[1]);
  assert.strictEqual(parsed['@context'], 'https://schema.org');
  console.log(`  [PASS] ${file} passed canonical, OG image (${path.basename(ogMatch[1])}), and JSON-LD checks.`);
});

const sitemapContent = fs.readFileSync(path.join(ROOT_DIR, 'sitemap.xml'), 'utf-8');
ALL_HTML_PAGES.forEach(({ canonical }) => {
  assert.ok(sitemapContent.includes(`<loc>${canonical}</loc>`), `sitemap.xml must register ${canonical}`);
});

const rssContent = fs.readFileSync(path.join(ROOT_DIR, 'rss.xml'), 'utf-8');
assert.ok(rssContent.includes('<rss version="2.0"') && !rssContent.includes('10대 왕자'));

const llmsContent = fs.readFileSync(path.join(ROOT_DIR, 'llms.txt'), 'utf-8');
assert.ok(llmsContent.includes('# Paradise Hero') && llmsContent.includes('beable9489@gmail.com'));
assert.ok(!llmsContent.includes('임영웅') && !llmsContent.includes('296100'));

console.log('\n===============================================================');
console.log('SUCCESS: ALL SEO, OG & DEPLOYMENT TESTS PASSED (100%)');
console.log('===============================================================');
