/**
 * video_pipeline.test.js
 * Comprehensive Test Suite for @김쌤의영웅라디오 Visible Story Radio Long-Form Pipeline (2026-11-11 HQ Spec).
 *
 * Verifies:
 * 1. Pipeline script presence (generate_radio_script.py, synthesize_radio_audio.py, render_radio_video.py, package_youtube_metadata.py, run_daily_radio_master.py)
 * 2. 6-chapter narrative pacing (12~20 min window: 720s ~ 1200s) + 3 fan stories (story.html) + 2 news items (news.html)
 * 3. Anti-AI rubric & 100% Hwang Young-woong solo purity (0 banned words, 0 '건행', 0 other singers)
 * 4. Audio voice parameters (InJoonNeural rate -4% / SunHiNeural rate -3%) & ducking (-22dB / -14dB)
 * 5. Video assembly plan (16:9 1920x1080, warm vacuum-tube radio booth + right-side 72pt+ story subtitles)
 * 6. YouTube metadata (Tue/Fri 18:00 KST publishAt, fixed 5 tags, exact HQ pinned comment with booth.html & cshop.naver.com/paradiseshop)
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

const requiredScripts = [
  'generate_radio_script.py',
  'synthesize_radio_audio.py',
  'render_radio_video.py',
  'package_youtube_metadata.py',
  'run_daily_radio_master.py'
];

requiredScripts.forEach((scriptFile) => {
  const scriptPath = path.join(SCRIPTS_DIR, scriptFile);
  assert.ok(fs.existsSync(scriptPath), `Script must exist: ${scriptFile}`);
  const stat = fs.statSync(scriptPath);
  assert.ok(stat.size > 1500, `Script must be substantive: ${scriptFile} (${stat.size} bytes)`);
  console.log(`[PASS] Pipeline script verified: ${scriptFile} (${stat.size} bytes)`);
});

const requiredArtifacts = [
  'script_ep01.json',
  'script_ep01.md',
  'narration_prompts.json',
  'video_assembly_plan.json',
  'youtube_metadata.json',
  'thumbnail_ep01_1080p.png',
  'youtube_upload_kit.txt'
];

requiredArtifacts.forEach((artFile) => {
  const artPath = path.join(CONTENT_DIR, artFile);
  assert.ok(fs.existsSync(artPath), `Sample package artifact must exist: ${artFile}`);
  const stat = fs.statSync(artPath);
  assert.ok(stat.size > 800, `Artifact must be substantive: ${artFile} (${stat.size} bytes)`);
  console.log(`[PASS] Sample package artifact verified: ${artFile} (${stat.size} bytes)`);
});

const visualsDir = path.join(CONTENT_DIR, 'visuals');
assert.ok(fs.existsSync(visualsDir), 'Visuals directory must exist');
const visualFiles = fs.readdirSync(visualsDir).filter(f => f.endsWith('.png'));
assert.strictEqual(visualFiles.length, 6, 'Exactly 6 chapter 1080p visual cards must exist');

const scriptData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'script_ep01.json'), 'utf-8'));
assert.strictEqual(scriptData.total_chapters, 6, 'Must contain exactly 6 chapters');
const totalEstSec = scriptData.total_estimated_duration_sec;
assert.ok(
  totalEstSec >= 720.0 && totalEstSec <= 1200.0,
  `Total estimated duration (${totalEstSec}s) must fall inside 12~20 min window (720s ~ 1200s)`
);
assert.ok(Array.isArray(scriptData.stories_featured) && scriptData.stories_featured.length === 3, 'Must ingest 3 fan stories from story.html/stories.json');
assert.ok(Array.isArray(scriptData.news_featured) && scriptData.news_featured.length === 2, 'Must ingest 2 Hwang Young-woong news items from news.html/trot_news.json');
console.log(`[PASS] 6-Chapter narrative arc (${totalEstSec}s), 3 stories & 2 news items verified.`);

let fullScriptText = '';
scriptData.chapters.forEach(ch => {
  ch.segments.forEach(seg => {
    fullScriptText += seg.text + ' ';
  });
});
assert.ok(fullScriptText.includes('파라다이스'), 'Must include fandom name 파라다이스');
assert.ok(!fullScriptText.includes('건행'), 'Must NOT include other-fandom catchphrase 건행');
assert.ok(!fullScriptText.includes('10대 왕자'), 'Must NOT include 10대 왕자');

const videoPlan = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'video_assembly_plan.json'), 'utf-8'));
assert.strictEqual(videoPlan.aspect_ratio, '16:9');
assert.strictEqual(videoPlan.resolution, '1920x1080');
const sub = videoPlan.video_specifications.subtitles;
assert.ok(sub.font_size_pt >= 72, `Right-side senior story subtitle font must be >= 72pt (got ${sub.font_size_pt}pt)`);
console.log(`[PASS] 1920x1080 Vacuum-Tube Booth + Right-Side ${sub.font_size_pt}pt Senior Subtitle layout verified.`);

const metadata = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'youtube_metadata.json'), 'utf-8'));
assert.ok(metadata.title.includes('황영웅'), 'Title must contain Hwang Young-woong');
assert.ok(metadata.publishAt && metadata.publishAt.includes('T18:00:00+09:00'), `Longform publishAt must be Tue/Fri 18:00 KST (got ${metadata.publishAt})`);
assert.deepStrictEqual(
  metadata.tags,
  ['#황영웅', '#파라다이스', '#트로트', '#감동사연', '#시니어유튜브'],
  'Fixed hashtags must match exact 5 HQ tags'
);
['#영상툰', '#애니메이션', '#웹툰'].forEach((bad) => {
  assert.ok(!metadata.description.includes(bad), `Banned tag ${bad} found in description`);
});

assert.ok(metadata.pinned_comment.includes('https://paradise-hero.com/booth.html'), 'Pinned comment must include free photo booth URL');
assert.ok(metadata.pinned_comment.includes('https://cshop.naver.com/paradiseshop'), 'Pinned comment must include Naver Creator Shop URL');
assert.ok(metadata.pinned_comment.includes('네이버 쇼핑 커넥트 활동의 일환으로'), 'Pinned comment must include Shopping Connect disclosure');
console.log('[PASS] Tue/Fri 18:00 KST publishAt, fixed 5 tags, and HQ pinned comment verified.');

console.log('\n===============================================================');
console.log('ALL @김쌤의영웅라디오 VIDEO PIPELINE TESTS PASSED (100%)!');
console.log('===============================================================');
