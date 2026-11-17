/**
 * tests/shorts_pipeline.test.js
 * Verification Suite for 6070 Senior Shorts & Naver Clip Pipeline Artifacts.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const DIVISION_DIR = path.resolve(__dirname, '..');
const CONTENT_DIR = path.join(DIVISION_DIR, 'content', 'shorts_daily', 'ep_01');

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
  assert.ok(fs.existsSync(fullPath) && fs.statSync(fullPath).size >= sc.minBytes);
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
  assert.ok(fs.existsSync(fullPath) && fs.statSync(fullPath).size >= art.minBytes);
}

const scriptData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'script_ep01.json'), 'utf8'));
assert.ok(scriptData.title.length <= 50);
assert.ok(Array.isArray(scriptData.beats) && scriptData.beats.length >= 6);

const audioMeta = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'audio_metadata.json'), 'utf8'));
assert.strictEqual(audioMeta.sample_rate, 44100);
assert.ok(audioMeta.peak_dbfs <= -0.5);
assert.strictEqual(audioMeta.clipped_samples, 0);
assert.strictEqual(audioMeta.full_narration_completion_compliant, true);

const meta = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'metadata_ep01.json'), 'utf8'));
assert.ok(meta.youtube_shorts && Array.isArray(meta.youtube_shorts.tags) && meta.youtube_shorts.tags.length === 5);
assert.strictEqual(meta.youtube_shorts.madeForKids, false);
assert.ok(meta.naver_clip && meta.naver_clip.clean_video_file.includes('naver_clip_clean.mp4'));
console.log('  [PASS] Shorts pipeline scripts, audio mastering, and metadata schema verified.');

console.log('\n===============================================================');
console.log('ALL NODE.JS 6070 SENIOR SHORTS PIPELINE TESTS PASSED (100%)!');
console.log('===============================================================');
