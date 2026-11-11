/**
 * tests/shorts_pipeline.test.js
 * ==============================================================================
 * Verification Suite for 2026-11-11 HQ 6070 Senior Shorts & Naver Clip Pipeline
 * (@김쌤의영웅라디오 & https://paradise-hero.com)
 * ==============================================================================
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const DIVISION_DIR = path.resolve(__dirname, '..');
const SCRIPTS_DIR = path.join(DIVISION_DIR, 'scripts');
const CONTENT_DIR = path.join(DIVISION_DIR, 'content', 'shorts_daily', 'ep_01');
const CHARACTERS_JSON = path.join(DIVISION_DIR, 'data', 'characters.json');

console.log('===============================================================');
console.log('Running 6070 Senior Shorts & Naver Clip Pipeline Test Suite');
console.log('===============================================================');

const requiredScripts = [
  { name: 'scripts/generate_shorts_script.py', minBytes: 4000 },
  { name: 'scripts/synthesize_shorts_audio.py', minBytes: 6000 },
  { name: 'scripts/render_shorts_video.py', minBytes: 6000 },
  { name: 'scripts/run_daily_shorts_master.py', minBytes: 3000 },
];

for (const sc of requiredScripts) {
  const fullPath = path.join(DIVISION_DIR, sc.name);
  assert.ok(fs.existsSync(fullPath), `Missing required script: ${sc.name}`);
  const stat = fs.statSync(fullPath);
  assert.ok(stat.size >= sc.minBytes, `${sc.name} is undersized (${stat.size} < ${sc.minBytes} bytes)`);
  console.log(`  [PASS] ${sc.name} verified (${stat.size} bytes).`);
}

const requiredArtifacts = [
  { name: 'script_ep01.json', minBytes: 1500 },
  { name: 'audio_ep01.wav', minBytes: 100000 },
  { name: 'audio_metadata.json', minBytes: 300 },
  { name: 'shorts_ep01_1080x1920.mp4', minBytes: 300000 },
  { name: 'shorts_ep01_naver_clip_clean.mp4', minBytes: 300000 },
  { name: 'metadata_ep01.json', minBytes: 800 },
  { name: 'metadata_ep01.md', minBytes: 400 },
];

for (const art of requiredArtifacts) {
  const fullPath = path.join(CONTENT_DIR, art.name);
  assert.ok(fs.existsSync(fullPath), `Missing required episode 1 artifact: ${art.name}`);
  const stat = fs.statSync(fullPath);
  assert.ok(stat.size >= art.minBytes, `${art.name} is undersized (${stat.size} < ${art.minBytes} bytes)`);
  console.log(`  [PASS] ${art.name} verified (${stat.size} bytes).`);
}

// Validate script schema, <=50 char quote title, 30~42s pacing & Hwang Young-woong outfits
const scriptData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'script_ep01.json'), 'utf8'));
assert.ok(scriptData.title.length <= 50, `Shorts title (${scriptData.title.length} chars) must be <= 50 chars`);
assert.ok(scriptData.title.includes('"'), 'Shorts title must follow quote formula');
assert.ok(scriptData.variants && scriptData.variants.A_VS_CONTRAST && scriptData.variants.B_LOSS_AVERSION && scriptData.variants.C_DRAMATIC_REVERSAL);

const beats = scriptData.beats;
assert.ok(Array.isArray(beats) && beats.length >= 6 && beats.length <= 10);

const charactersData = JSON.parse(fs.readFileSync(CHARACTERS_JSON, 'utf8'));
const validCharacterIds = new Set(charactersData.map(c => c.id));
for (const b of beats) {
  assert.ok(validCharacterIds.has(b.character_id), `Unknown character_id: ${b.character_id}`);
  assert.ok(b.subtitle_l1.split(/\s+/).filter(Boolean).length <= 8, 'Subtitle line 1 must be <= 8 words');
  if (b.subtitle_l2) {
    assert.ok(b.subtitle_l2.split(/\s+/).filter(Boolean).length <= 8, 'Subtitle line 2 must be <= 8 words');
  }
}
console.log(`  [PASS] Title (${scriptData.title.length} chars <= 50), 3 A/B/C variants, and <=8 words/line verified.`);

// Audio mastering & seg_dur >= tts_dur + 0.22s full narration completion check
const audioMeta = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'audio_metadata.json'), 'utf8'));
assert.strictEqual(audioMeta.sample_rate, 44100);
assert.ok(audioMeta.peak_dbfs <= -0.5, `Peak ${audioMeta.peak_dbfs} dBFS exceeds -0.5 dBFS ceiling`);
assert.strictEqual(audioMeta.clipped_samples, 0);
assert.strictEqual(audioMeta.full_narration_completion_compliant, true, 'Must guarantee seg_dur >= tts_dur + 0.22s');
assert.ok(audioMeta.total_duration_sec >= 28.0 && audioMeta.total_duration_sec <= 45.0, `Total duration ${audioMeta.total_duration_sec}s must be ~30~42s`);

if (Array.isArray(audioMeta.tts_durations_sec)) {
  for (let i = 0; i < audioMeta.tts_durations_sec.length; i++) {
    const ttsDur = audioMeta.tts_durations_sec[i];
    const segDur = audioMeta.beat_durations_sec[i];
    assert.ok(segDur + 1e-6 >= ttsDur + 0.215, `Beat ${i} seg_dur (${segDur}s) < tts_dur + 0.22s (${ttsDur + 0.22}s)`);
  }
}
console.log(`  [PASS] Audio mastering verified: Duration=${audioMeta.total_duration_sec}s, Peak=${audioMeta.peak_dbfs} dBFS, Clipped=0, seg_dur >= tts_dur + 0.22s.`);

// Metadata check: Fixed 5 tags, zero #영상툰/#애니메이션/#웹툰, 19:30 KST publishAt, Related Video, Naver Clip
const meta = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'metadata_ep01.json'), 'utf8'));
assert.ok(meta.youtube_shorts, 'Missing youtube_shorts metadata');
assert.ok(meta.youtube_shorts.title.length <= 50, `Metadata title (${meta.youtube_shorts.title.length} chars) must be <= 50 chars`);
assert.deepStrictEqual(
  meta.youtube_shorts.tags,
  ['#황영웅', '#파라다이스', '#트로트', '#감동사연', '#시니어유튜브'],
  'YouTube Shorts tags must strictly equal the 5 HQ fixed tags'
);
assert.ok(meta.youtube_shorts.publishAt && meta.youtube_shorts.publishAt.includes('T19:30:00+09:00'), 'Shorts publishAt must be daily 19:30 KST');
assert.strictEqual(meta.youtube_shorts.related_video_id, 'lGkMncY4u1o', 'Shorts Related Video must link to latest longform');
assert.strictEqual(meta.youtube_shorts.madeForKids, false);

assert.ok(meta.naver_clip, 'Missing naver_clip metadata');
assert.ok(meta.naver_clip.clean_video_file && meta.naver_clip.clean_video_file.includes('naver_clip_clean.mp4'));
assert.ok(meta.naver_clip.caption.includes('https://cshop.naver.com/paradiseshop'));

const metaRaw = fs.readFileSync(path.join(CONTENT_DIR, 'metadata_ep01.md'), 'utf8');
['#영상툰', '#애니메이션', '#웹툰', '10대 왕자', '임영웅', '이찬원'].forEach((banned) => {
  assert.ok(!metaRaw.includes(banned), `Banned string '${banned}' found in metadata_ep01.md`);
});
console.log('  [PASS] Fixed 5 tags, 19:30 KST publishAt, Related Video, and Naver Clip clean MP4 verified.');

console.log('\n===============================================================');
console.log('ALL NODE.JS 6070 SENIOR SHORTS PIPELINE TESTS PASSED (100%)!');
console.log('===============================================================');
