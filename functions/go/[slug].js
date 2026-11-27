/**
 * Cloudflare Pages Function: /go/[slug] (HERO — https://paradise-hero.com)
 * 1) Immediate 302 redirect (0ms blocking latency) to fixed same-origin destination with clean internal GA4 UTM.
 * 2) Non-blocking async telemetry via context.waitUntil -> https://api.truthofmarket.com/api/track-go
 *    with explicit `is_test` guard (?internal_test=1 or X-Internal-Test: 1) & `utm_content` passthrough.
 * Security: Strict same-origin allowlist (zero open redirect).
 */
const SITE_KEY = "HERO";
const SLUG_MAP = {
  "yt": "https://paradise-hero.com/?utm_source=youtube&utm_medium=video&utm_campaign=go_yt",
  "yt-a": "https://paradise-hero.com/?utm_source=youtube&utm_medium=video&utm_campaign=go_yt&utm_content=slot_a_realui",
  "yt-b": "https://paradise-hero.com/?utm_source=youtube&utm_medium=video&utm_campaign=go_yt&utm_content=slot_b_flowchar",
  "yt-radio": "https://paradise-hero.com/radio.html?utm_source=youtube&utm_medium=video&utm_campaign=go_yt_radio",
  "yt-card": "https://paradise-hero.com/vip.html?utm_source=youtube&utm_medium=video&utm_campaign=go_yt_card",
  "yt-stream": "https://paradise-hero.com/stream?utm_source=youtube&utm_medium=video&utm_campaign=go_yt_stream",
  "ig": "https://paradise-hero.com/?utm_source=instagram&utm_medium=social&utm_campaign=go_ig",
  "ig-b": "https://paradise-hero.com/?utm_source=instagram&utm_medium=social&utm_campaign=go_ig&utm_content=slot_b_flowchar",
  "share": "https://paradise-hero.com/vip.html?utm_source=share_card&utm_medium=referral&utm_campaign=go_share"
};
const DEFAULT_PREFIX = "https://paradise-hero.com/?utm_source=go_link&utm_medium=referral&utm_campaign=";

export async function onRequestGet(context) {
  const raw = String((context.params && context.params.slug) || 'yt').toLowerCase().trim();
  const slug = /^[a-z0-9_-]{1,32}$/.test(raw) ? raw : 'yt';
  const dest = Object.prototype.hasOwnProperty.call(SLUG_MAP, slug)
    ? SLUG_MAP[slug]
    : (DEFAULT_PREFIX + encodeURIComponent(slug));

  const reqUrl = new URL(context.request.url);
  const isTest = reqUrl.searchParams.get('internal_test') === '1'
    || String(context.request.headers.get('x-internal-test') || '').trim() === '1';
  let utmContent = '';
  try {
    utmContent = new URL(dest).searchParams.get('utm_content') || '';
  } catch (_) {}

  const ref = String(context.request.headers.get('referer') || '').slice(0, 240);
  const ua = String(context.request.headers.get('user-agent') || '').slice(0, 140);

  if (typeof context.waitUntil === 'function') {
    const trackHeaders = { 'Content-Type': 'application/json' };
    if (isTest) trackHeaders['X-Internal-Test'] = '1';
    context.waitUntil(
      fetch('https://api.truthofmarket.com/api/track-go', {
        method: 'POST',
        headers: trackHeaders,
        body: JSON.stringify({
          site: SITE_KEY,
          slug: slug,
          utm_content: utmContent,
          is_test: isTest,
          ref: ref,
          ua: ua,
          ts: new Date().toISOString()
        })
      }).catch(() => {})
    );
  }

  return new Response(null, {
    status: 302,
    headers: {
      'Location': dest,
      'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      'X-Robots-Tag': 'noindex, nofollow',
      'X-Content-Type-Options': 'nosniff'
    }
  });
}
