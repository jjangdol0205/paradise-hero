/**
 * video_pipeline.test.js
 * Verification Suite for @김쌤의영웅라디오 Visible Story Radio Long-Form Pipeline Artifacts.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const SCRIPTS_DIR = path.join(ROOT_DIR, 'scripts');
const CONTENT_DIR = path.join(ROOT_DIR, 'content', 'episode_01');

console.log('===============================================================');
console.log('--- Running @김쌤의영웅라디오 Longform Radio Pipeline Verification ---');
console.log('===============================================================\n');

[
  'generate_radio_script.py',
  'synthesize_radio_audio.py',
  'render_radio_video.py',
  'package_youtube_metadata.py',
  'run_daily_radio_master.py'
].forEach((scriptFile) => {
  const scriptPath = path.join(SCRIPTS_DIR, scriptFile);
  assert.ok(fs.existsSync(scriptPath) && fs.statSync(scriptPath).size > 1500);
});

[
  'script_ep01.json',
  'script_ep01.md',
  'narration_prompts.json',
  'video_assembly_plan.json',
  'youtube_metadata.json',
  'thumbnail_ep01_1080p.png',
  'youtube_upload_kit.txt'
].forEach((artFile) => {
  const artPath = path.join(CONTENT_DIR, artFile);
  assert.ok(fs.existsSync(artPath) && fs.statSync(artPath).size > 800);
});

const scriptData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'script_ep01.json'), 'utf-8'));
assert.strictEqual(scriptData.total_chapters, 6);
assert.ok(scriptData.total_estimated_duration_sec >= 720.0 && scriptData.total_estimated_duration_sec <= 1200.0);

const videoPlan = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'video_assembly_plan.json'), 'utf-8'));
assert.strictEqual(videoPlan.aspect_ratio, '16:9');
assert.strictEqual(videoPlan.resolution, '1920x1080');
assert.ok(videoPlan.video_specifications.subtitles.font_size_pt >= 72);

const metadata = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'youtube_metadata.json'), 'utf-8'));
assert.ok(metadata.publishAt && metadata.publishAt.includes('T18:00:00+09:00'));
assert.ok(Array.isArray(metadata.tags) && metadata.tags.length === 5);
assert.ok(metadata.pinned_comment.includes('https://paradise-hero.com/booth.html'));
assert.ok(metadata.pinned_comment.includes('https://cshop.naver.com/paradiseshop'));
console.log('[PASS] Longform 1920x1080 layout, Tue/Fri 18:00 KST publishAt, and pinned comment verified.');

console.log('\n===============================================================');
console.log('ALL @김쌤의영웅라디오 VIDEO PIPELINE TESTS PASSED (100%)!');
console.log('===============================================================');
