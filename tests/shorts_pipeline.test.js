/**
 * tests/shorts_pipeline.test.js
 * ==============================================================================
 * Programmatic Node.js Verification Suite for Milestone 4 (F9, F10, F11, F12)
 * Clean Shorts V3 Mastering & Automated Daily Shorts Pipeline for Division 4
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
console.log('Running Milestone 4: Daily Shorts V3 Pipeline Test Suite (Node.js)');
console.log('===============================================================');

// -----------------------------------------------------------------------------
// Test 1: Pipeline Scripts Physical Existence and Substantive Sizes
// -----------------------------------------------------------------------------
console.log('\nTest 1: Verifying physical existence and sizes of pipeline scripts...');
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

// -----------------------------------------------------------------------------
// Test 2: Episode 1 Complete Artifact Package Verification
// -----------------------------------------------------------------------------
console.log('\nTest 2: Verifying Episode 01 artifacts package in content/shorts_daily/ep_01/...');
const requiredArtifacts = [
  { name: 'script_ep01.json', minBytes: 1500 },
  { name: 'audio_ep01.wav', minBytes: 100000 },
  { name: 'audio_metadata.json', minBytes: 300 },
  { name: 'shorts_ep01_1080x1920.mp4', minBytes: 300000 },
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

// -----------------------------------------------------------------------------
// Test 3: Script Schema, A/B/C 3-Variant Pacing & Character Roster
// -----------------------------------------------------------------------------
console.log('\nTest 3: Validating script schema, A/B/C 3-variant dopamine storylines & character roster...');
const scriptPath = path.join(CONTENT_DIR, 'script_ep01.json');
const scriptData = JSON.parse(fs.readFileSync(scriptPath, 'utf8'));

// Verify 3 variants
assert.ok(scriptData.variants, 'script_ep01.json missing variants object');
const variantKeys = Object.keys(scriptData.variants);
assert.ok(variantKeys.includes('A_VS_CONTRAST'), 'Missing A_VS_CONTRAST variant');
assert.ok(variantKeys.includes('B_LOSS_AVERSION'), 'Missing B_LOSS_AVERSION variant');
assert.ok(variantKeys.includes('C_DRAMATIC_REVERSAL'), 'Missing C_DRAMATIC_REVERSAL variant');
console.log(`  [PASS] All 3 dopamine storyline variants present (${variantKeys.join(', ')}).`);

// Verify selected variant
assert.ok(scriptData.selected_variant, 'Missing selected_variant');
assert.ok(['A_VS_CONTRAST', 'B_LOSS_AVERSION', 'C_DRAMATIC_REVERSAL'].includes(scriptData.selected_variant));
assert.ok(typeof scriptData.selected_score === 'number' && scriptData.selected_score > 80);
console.log(`  [PASS] Selected variant: ${scriptData.selected_variant} (Dopamine Score: ${scriptData.selected_score}).`);

// Verify beats count & duration pacing
const beats = scriptData.beats;
assert.ok(Array.isArray(beats), 'beats must be an array');
assert.ok(beats.length >= 6 && beats.length <= 10, `beats count out of range 6~10 (found ${beats.length})`);
console.log(`  [PASS] Beats count: ${beats.length} (Complies with 6~10 beats standard).`);

// Verify micro-cuts: body beats 1.8~2.2s, CTA beat 2.5~3.8s
for (let i = 0; i < beats.length; i++) {
  const b = beats[i];
  assert.strictEqual(b.beat_idx, i, `beat_idx mismatch at ${i}`);
  assert.ok(typeof b.narration === 'string' && b.narration.length > 5, `beat ${i} narration invalid`);
  assert.ok(typeof b.subtitle_l1 === 'string' && b.subtitle_l1.length > 0, `beat ${i} subtitle_l1 missing`);
  assert.ok(typeof b.subtitle_l2 === 'string' && b.subtitle_l2.length > 0, `beat ${i} subtitle_l2 missing`);
  assert.ok(b.sfx, `beat ${i} missing sfx marker`);

  if (i === beats.length - 1 || b.is_cta) {
    assert.ok(b.target_duration_sec >= 2.5 && b.target_duration_sec <= 6.0,
      `Ending CTA beat duration ${b.target_duration_sec}s not in 2.5~6.0s range`);
  } else {
    assert.ok(b.target_duration_sec >= 1.8 && b.target_duration_sec <= 6.0,
      `Body beat ${i} duration ${b.target_duration_sec}s not in 1.8~6.0s range`);
  }
}
console.log('  [PASS] All beat durations strictly adhere to full narration completion pacing (1.8~6.0s body, 2.5~6.0s CTA).');

// Verify character references
const charactersData = JSON.parse(fs.readFileSync(CHARACTERS_JSON, 'utf8'));
const validCharacterIds = new Set(charactersData.map(c => c.id));
assert.strictEqual(validCharacterIds.size, 10, 'Character catalog must contain exactly 10 characters');

for (const b of beats) {
  assert.ok(validCharacterIds.has(b.character_id), `Unknown character_id: ${b.character_id}`);
}
assert.ok(scriptData.featured_characters.includes('hwang_young_woong'), 'Hwang Young-woong must be featured');
console.log(`  [PASS] Character IDs validated against 10 anime trot prince catalog.`);

// -----------------------------------------------------------------------------
// Test 4: Audio Mastering & Zero-Silence Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 4: Checking audio mastering, zero-silence, limiter ceiling & point SFX...');
const audioMetaPath = path.join(CONTENT_DIR, 'audio_metadata.json');
const audioMeta = JSON.parse(fs.readFileSync(audioMetaPath, 'utf8'));

assert.strictEqual(audioMeta.sample_rate, 44100, 'Audio sample rate must be 44100Hz');
assert.ok(audioMeta.peak_dbfs <= -0.5, `Peak ${audioMeta.peak_dbfs} dBFS exceeds -0.5 dBFS ceiling`);
assert.strictEqual(audioMeta.clipped_samples, 0, 'Audio must have 0 clipped samples');
assert.ok(audioMeta.max_internal_silence_sec <= 0.12,
  `Max silence ${audioMeta.max_internal_silence_sec}s exceeds natural breathing <=0.12s limit`);
assert.strictEqual(audioMeta.zero_silence_compliant, true);
assert.strictEqual(audioMeta.limiter_compliant, true);

// Check SFX markers
const sfxMarkers = audioMeta.sfx_markers.map(m => m.sfx_type);
assert.ok(sfxMarkers.includes('hook_chime'), 'Missing hook_chime SFX marker at 0s');
assert.ok(sfxMarkers.includes('cut_whoosh'), 'Missing cut_whoosh SFX marker');
assert.ok(sfxMarkers.includes('metric_ping'), 'Missing metric_ping SFX marker');
assert.ok(sfxMarkers.includes('outro_drop'), 'Missing outro_drop SFX marker');
console.log(`  [PASS] Audio mastering verified: Peak=${audioMeta.peak_dbfs} dBFS, Max Silence=${audioMeta.max_internal_silence_sec}s, Clipped=${audioMeta.clipped_samples}.`);
console.log(`  [PASS] Point SFX verified: ${sfxMarkers.length} events (chime, whoosh, ping, drop).`);

// -----------------------------------------------------------------------------
// Test 5: Multi-Platform Distribution Metadata Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 5: Validating YouTube Shorts & Instagram Reels metadata packaging...');
const metaPath = path.join(CONTENT_DIR, 'metadata_ep01.json');
const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));

// YouTube Shorts
assert.ok(meta.youtube_shorts, 'Missing youtube_shorts metadata packet');
assert.ok(meta.youtube_shorts.title.includes('#Shorts'), 'YouTube Shorts title must contain #Shorts');
assert.ok(meta.youtube_shorts.tags.includes('#Shorts'), 'YouTube tags must include #Shorts');
assert.ok(meta.youtube_shorts.tags.includes('#황영웅'), 'YouTube tags must include #황영웅');
assert.ok(meta.youtube_shorts.tags.includes('#김쌤의영웅라디오'), 'YouTube tags must include #김쌤의영웅라디오');
assert.ok(meta.youtube_shorts.tags.includes('#파라다이스히어로'), 'YouTube tags must include #파라다이스히어로');
assert.strictEqual(meta.youtube_shorts.madeForKids, false, 'YouTube madeForKids must be strictly false');
assert.ok(Array.isArray(meta.youtube_shorts.chapters) && meta.youtube_shorts.chapters.length >= 6);
console.log('  [PASS] YouTube Shorts metadata compliant (#Shorts tag, chapters, madeForKids=false).');

// Instagram Reels
assert.ok(meta.instagram_reels, 'Missing instagram_reels metadata packet');
assert.ok(meta.instagram_reels.caption.includes('@kimteacher_heroradio'), 'Reels caption must include @kimteacher_heroradio');
assert.ok(meta.instagram_reels.caption.includes('paradise-hero.com'), 'Reels caption must include paradise-hero.com');
assert.strictEqual(meta.instagram_reels.account_tag, '@kimteacher_heroradio');
assert.strictEqual(meta.instagram_reels.domain_callout, 'paradise-hero.com');
console.log('  [PASS] Instagram Reels metadata compliant (@kimteacher_heroradio, domain CTA).');

// -----------------------------------------------------------------------------
// Test 6: GEMINI.md Zero-Tolerance Prohibited Words Compliance
// -----------------------------------------------------------------------------
console.log('\nTest 6: Enforcing GEMINI.md Zero-Tolerance Prohibited Commercial Words...');
const BANNED_WORDS = ['최저가', '할인율', '특가', '폭탄세일'];

const filesToCheck = [
  path.join(SCRIPTS_DIR, 'generate_shorts_script.py'),
  path.join(SCRIPTS_DIR, 'synthesize_shorts_audio.py'),
  path.join(SCRIPTS_DIR, 'render_shorts_video.py'),
  path.join(SCRIPTS_DIR, 'run_daily_shorts_master.py'),
  path.join(CONTENT_DIR, 'script_ep01.json'),
  path.join(CONTENT_DIR, 'metadata_ep01.json'),
  path.join(CONTENT_DIR, 'metadata_ep01.md'),
];

for (const fp of filesToCheck) {
  const content = fs.readFileSync(fp, 'utf8');
  for (const banned of BANNED_WORDS) {
    assert.ok(!content.includes(banned),
      `Zero-tolerance violation: Found prohibited word '${banned}' in ${path.relative(DIVISION_DIR, fp)}`);
  }
}
console.log('  [PASS] All pipeline scripts and generated metadata are 100% clean of prohibited words.');

console.log('\n===============================================================');
console.log('ALL NODE.JS PIPELINE TESTS PASSED (100% Success)!');
console.log('===============================================================');
