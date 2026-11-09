/**
 * video_pipeline.test.js
 * Comprehensive Test Suite for @김쌤의영웅라디오 Long-Form Video Production Pipeline & Sample Package.
 *
 * Verifies:
 * 1. Pipeline script presence and structure
 * 2. 6-chapter narrative pacing (12~18 min window: 720s ~ 1080s)
 * 3. Anti-AI rubric compliance (0 blacklist cliches)
 * 4. Audio voice parameters (InJoonNeural rate -4% / SunHiNeural rate -3%) & ducking (-22dB / -14dB)
 * 5. Video assembly plan (16:9 1920x1080, 30s Ken Burns, 52~56pt high-contrast subtitles)
 * 6. YouTube metadata (high-CTR title, timestamps, single-gate funnel, email, pinned comment URL-free)
 * 7. Sample package integrity (audio files, visuals, metadata)
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const SCRIPTS_DIR = path.join(ROOT_DIR, 'scripts');
const CONTENT_DIR = path.join(ROOT_DIR, 'content', 'episode_01');

console.log('===============================================================');
console.log('--- Running @김쌤의영웅라디오 Video Pipeline Verification ---');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Pipeline Scripts Existence & Executability
// -----------------------------------------------------------------------------
const requiredScripts = [
  'generate_radio_script.py',
  'synthesize_radio_audio.py',
  'render_radio_video.py',
  'package_youtube_metadata.py'
];

requiredScripts.forEach((scriptFile) => {
  const scriptPath = path.join(SCRIPTS_DIR, scriptFile);
  assert.ok(fs.existsSync(scriptPath), `Script must exist: ${scriptFile}`);
  const stat = fs.statSync(scriptPath);
  assert.ok(stat.size > 2000, `Script must be substantive (>2KB): ${scriptFile} (${stat.size} bytes)`);
  console.log(`[PASS] Pipeline script verified: ${scriptFile} (${stat.size} bytes)`);
});

// -----------------------------------------------------------------------------
// Test 2: Episode 1 Sample Package Artifacts Existence
// -----------------------------------------------------------------------------
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
  assert.ok(stat.size > 1000, `Artifact must be substantive (>1KB): ${artFile} (${stat.size} bytes)`);
  console.log(`[PASS] Sample package artifact verified: ${artFile} (${stat.size} bytes)`);
});

// Verify audio assets and visual cards
const audioDir = path.join(CONTENT_DIR, 'audio');
assert.ok(fs.existsSync(audioDir), 'Audio directory must exist');
const audioFiles = fs.readdirSync(audioDir).filter(f => f.endsWith('.mp3'));
assert.ok(audioFiles.length >= 4, `At least 4 synthesized audio segments must exist (found ${audioFiles.length})`);
audioFiles.forEach(f => {
  const fSize = fs.statSync(path.join(audioDir, f)).size;
  assert.ok(fSize > 5000, `Audio file ${f} must be valid audio (>5KB, found ${fSize})`);
});
console.log(`[PASS] Real synthesized audio files verified (${audioFiles.length} files in audio/)`);

const visualsDir = path.join(CONTENT_DIR, 'visuals');
assert.ok(fs.existsSync(visualsDir), 'Visuals directory must exist');
const visualFiles = fs.readdirSync(visualsDir).filter(f => f.endsWith('.png'));
assert.strictEqual(visualFiles.length, 6, 'Exactly 6 chapter 1080p visual cards must exist');
visualFiles.forEach(f => {
  const fSize = fs.statSync(path.join(visualsDir, f)).size;
  assert.ok(fSize > 10000, `Visual card ${f} must be a valid 1080p render (>10KB, found ${fSize})`);
});
console.log(`[PASS] Real 1080p chapter visual cards verified (6/6 files in visuals/)`);

// -----------------------------------------------------------------------------
// Test 3: Script Pacing & 6-Chapter Narrative Arc
// -----------------------------------------------------------------------------
const scriptData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'script_ep01.json'), 'utf-8'));

assert.strictEqual(scriptData.total_chapters, 6, 'Must contain exactly 6 chapters');
assert.strictEqual(scriptData.chapters.length, 6, 'Chapters array length must be 6');

const expectedChapterIds = [
  'ch1_opening',
  'ch2_hero_story',
  'ch3_song_commentary',
  'ch4_fan_letter',
  'ch5_fandom_cheer',
  'ch6_closing_cta'
];

expectedChapterIds.forEach((chId, idx) => {
  const ch = scriptData.chapters[idx];
  assert.strictEqual(ch.chapter_id, chId, `Chapter ${idx + 1} ID must match ${chId}`);
  assert.ok(ch.segments && ch.segments.length > 0, `Chapter ${chId} must contain segments`);
  assert.ok(ch.title, `Chapter ${chId} must have a title`);
});

// Pacing duration check: 12~18 min (720s ~ 1080s)
const totalEstSec = scriptData.total_estimated_duration_sec;
assert.ok(
  totalEstSec >= 720.0 && totalEstSec <= 1080.0,
  `Total estimated duration (${totalEstSec}s) must fall inside 12~18 min window (720s ~ 1080s)`
);
console.log(`[PASS] 6-Chapter narrative arc & pacing verified: ${totalEstSec}s (${(totalEstSec / 60).toFixed(1)} min)`);

// Speaker roles check
const speakers = new Set();
scriptData.chapters.forEach(ch => {
  ch.segments.forEach(seg => {
    speakers.add(seg.speaker);
  });
});
assert.ok(speakers.has('dj_kim'), 'Script must feature DJ 김쌤');
assert.ok(speakers.has('fan_letter_writer'), 'Script must feature fan letter reader');
console.log(`[PASS] Speaker role diversification verified: ${Array.from(speakers).join(', ')}`);

// -----------------------------------------------------------------------------
// Test 4: Anti-AI Lexical Purity (0 Forbidden Cliches)
// -----------------------------------------------------------------------------
const AI_BLACKLIST = [
  '혁신적인', '궁극의', '새로운 지평', '바쁜 현대사회', '알아보겠습니다',
  '도움이 되셨나요', '선택은 여러분의 몫', '여정을 떠나보세요', '함께 성장해요',
  '마법 같은', '기적의', '완벽한 솔루션', '놀라운 경험', '주목받고 있는'
];

let fullScriptText = '';
scriptData.chapters.forEach(ch => {
  ch.segments.forEach(seg => {
    fullScriptText += seg.text + ' ';
    AI_BLACKLIST.forEach(badWord => {
      assert.ok(
        !seg.text.includes(badWord),
        `AI Blacklist cliche '${badWord}' detected in segment ${seg.segment_id}`
      );
    });
  });
});

assert.ok(fullScriptText.includes('파라다이스'), 'Must include fandom name 파라다이스');
assert.ok(fullScriptText.includes('건행'), 'Must include signature signoff 건행');
console.log(`[PASS] Anti-AI lexical purity verified: 0 forbidden words across ${fullScriptText.length} characters`);

// -----------------------------------------------------------------------------
// Test 5: Audio Engine, Voice Models & Ducking Specification
// -----------------------------------------------------------------------------
const narrationData = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'narration_prompts.json'), 'utf-8'));

// Voice verification
const voices = narrationData.voice_specifications;
assert.ok(voices.dj_kim, 'DJ 김쌤 voice spec must exist');
assert.strictEqual(voices.dj_kim.voice, 'ko-KR-InJoonNeural', 'DJ 김쌤 voice must be ko-KR-InJoonNeural');
assert.strictEqual(voices.dj_kim.rate, '-4%', 'DJ 김쌤 rate must be -4%');
assert.strictEqual(voices.dj_kim.pitch, '-2Hz', 'DJ 김쌤 pitch must be -2Hz');

assert.ok(voices.fan_letter_writer, 'Fan letter voice spec must exist');
assert.strictEqual(voices.fan_letter_writer.voice, 'ko-KR-SunHiNeural', 'Fan letter voice must be ko-KR-SunHiNeural');
assert.strictEqual(voices.fan_letter_writer.rate, '-3%', 'Fan letter rate must be -3%');
assert.strictEqual(voices.fan_letter_writer.pitch, '-1Hz', 'Fan letter pitch must be -1Hz');

// Ducking verification
const ducking = narrationData.ducking_specifications;
assert.strictEqual(ducking.speech_active_bgm_db, -22.0, 'Speech active ducking must be -22 dBFS');
assert.strictEqual(ducking.speech_pause_bgm_db, -14.0, 'Speech pause ducking must be -14 dBFS');
assert.strictEqual(ducking.master_integrated_lufs, -16.0, 'Master integrated loudness must be -16 LUFS');
assert.strictEqual(ducking.true_peak_limit_db, -1.0, 'True peak limit must be -1.0 dBTP');
assert.ok(narrationData.ffmpeg_ducking_recipe.includes('sidechaincompress'), 'Must include sidechaincompress recipe');

console.log('[PASS] Audio voices (InJoonNeural -4% / SunHiNeural -3%) and ducking (-22dB / -14dB) verified.');

// -----------------------------------------------------------------------------
// Test 6: 16:9 Landscape Video Assembly Plan
// -----------------------------------------------------------------------------
const videoPlan = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'video_assembly_plan.json'), 'utf-8'));

assert.strictEqual(videoPlan.aspect_ratio, '16:9', 'Video must be 16:9 Landscape');
assert.strictEqual(videoPlan.resolution, '1920x1080', 'Video resolution must be 1920x1080');

const kb = videoPlan.video_specifications.ken_burns;
assert.strictEqual(kb.cycle_duration_sec, 30.0, 'Ken Burns cycle must be 30 seconds');
assert.strictEqual(kb.zoom_start, 1.00, 'Ken Burns zoom start must be 1.00');
assert.strictEqual(kb.zoom_end, 1.05, 'Ken Burns zoom end must be 1.05');

const sub = videoPlan.video_specifications.subtitles;
assert.ok(
  sub.font_size_pt >= 52 && sub.font_size_pt <= 56,
  `Subtitle font size must be within 52~56pt (got ${sub.font_size_pt}pt)`
);
assert.strictEqual(sub.text_color, '#FFFFFF', 'Subtitle text color must be #FFFFFF');
assert.ok(sub.outline_width_px >= 8, 'Subtitle outline must be >= 8px for senior readability');
assert.ok(sub.vertical_align_y >= 880, 'Subtitle vertical position must be in bottom safe area');

assert.strictEqual(videoPlan.chapters.length, 6, 'Video plan must have 6 chapters with scene prompts');
videoPlan.chapters.forEach(ch => {
  assert.ok(ch.art_prompt && ch.art_prompt.length > 50, `Chapter ${ch.chapter_index} must have detailed art prompt`);
  assert.ok(ch.subtitles && ch.subtitles.length > 0, `Chapter ${ch.chapter_index} must have subtitle cues`);
});

console.log('[PASS] 16:9 Landscape (1920x1080), 30s Ken Burns and 54pt senior subtitle specs verified.');

// -----------------------------------------------------------------------------
// Test 7: YouTube Metadata & Funnel Conversion Kit
// -----------------------------------------------------------------------------
const metadata = JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'youtube_metadata.json'), 'utf-8'));

// Title
assert.ok(metadata.title.includes('황영웅'), 'Title must contain Hwang Young-woong');
assert.ok(metadata.title.includes('당신 편'), 'Title must contain featured song 당신 편');
assert.ok(metadata.title.includes('제1화') || metadata.title.includes('1화'), 'Title must contain episode number');

// Description
assert.ok(metadata.description.includes('https://paradise-hero.com/story.html'), 'Description must contain single-gate story funnel URL');
assert.ok(
  metadata.description.includes('김쌤의 영웅 라디오 사연 신청 및 황금빛 VIP 혜택은 공식 커뮤니티 https://paradise-hero.com 에서 확인하세요'),
  'Description must contain standard VIP community funnel callout'
);
assert.ok(metadata.description.includes('beable9489@gmail.com'), 'Description must contain unified support email beable9489@gmail.com');

// Timestamps
assert.strictEqual(metadata.timestamps.length, 6, 'Metadata must contain exactly 6 chapter timestamps');
assert.ok(metadata.description.includes('00:00'), 'Description must list 00:00 timestamp');

// Pinned Comment Safety: STRICT ZERO RAW URLS
assert.strictEqual(
  metadata.pinned_comment_has_raw_url,
  false,
  'Pinned comment MUST NOT contain raw URLs (to prevent YouTube spam filter penalties)'
);
assert.ok(!metadata.pinned_comment.includes('http://'), 'Pinned comment must not contain http://');
assert.ok(!metadata.pinned_comment.includes('https://'), 'Pinned comment must not contain https://');
assert.ok(metadata.pinned_comment.includes('더보기'), 'Pinned comment must guide users to [더보기] description');
assert.ok(metadata.pinned_comment.includes('paradise-hero.com'), 'Pinned comment can mention domain text without http protocol');

// Thumbnail specification
const thumbSpec = metadata.thumbnail_specification;
assert.ok(thumbSpec.layout_formula.includes('55%') && thumbSpec.layout_formula.includes('45%'), 'Thumbnail formula must use 55/45 split');
assert.ok(thumbSpec.top_amber_badge.includes('1화'), 'Thumbnail badge must show episode 1');
assert.strictEqual(thumbSpec.main_headline, '어머니, 이젠 울지 마세요', 'Main headline must match emotional hook');

console.log('[PASS] YouTube metadata, 6 timestamps, story funnel, email, and URL-free pinned comment verified.');

// -----------------------------------------------------------------------------
// Test 8: End-to-End Package Consistency
// -----------------------------------------------------------------------------
assert.strictEqual(scriptData.total_chapters, videoPlan.total_chapters);
assert.strictEqual(scriptData.chapters.length, metadata.timestamps.length);
assert.strictEqual(narrationData.total_segments, scriptData.total_segments);

console.log('[PASS] Cross-artifact structural consistency verified.');

console.log('\n===============================================================');
console.log('ALL @김쌤의영웅라디오 VIDEO PIPELINE TESTS PASSED (100%)!');
console.log('===============================================================');
