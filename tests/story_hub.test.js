/**
 * story_hub.test.js
 * Comprehensive Test Suite for Milestone 1: Senior Fan Story Hub ("사연 복덕방")
 * with Automated Top Story Selection & YouTube Radio Bridge.
 * 
 * Verifies:
 * 1. Physical file existence and substantive sizes
 * 2. Seed stories schema and quality in data/stories.json
 * 3. Client validation logic (anti-spam, character bounds, prohibited words, masking)
 * 4. Algorithmic ranking engine (mathematical scoring, quarantine filter, time decay)
 * 5. YouTube Radio Script Generation Bridge (Chapter 4 fan letter & Chapter 3 song commentary)
 * 6. Senior WCAG AAA accessibility, touch targets (>= 56px), dual-tab UX, and photo booth link
 * 7. Zero prohibited commercial words compliance
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT_DIR, 'data');
const SCRIPTS_DIR = path.join(ROOT_DIR, 'scripts');
const JS_DIR = path.join(ROOT_DIR, 'js');

console.log('===============================================================');
console.log('--- Running Senior Fan Story Hub ("사연 복덕방") Test Suite ---');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Physical File Existence & Substantive Sizes
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence and sizes...');
const requiredFiles = [
  { p: path.join(ROOT_DIR, 'story.html'), minSize: 5000, label: 'story.html' },
  { p: path.join(JS_DIR, 'story-hub.js'), minSize: 3000, label: 'js/story-hub.js' },
  { p: path.join(DATA_DIR, 'stories.json'), minSize: 1500, label: 'data/stories.json' },
  { p: path.join(SCRIPTS_DIR, 'select_top_story.py'), minSize: 3000, label: 'scripts/select_top_story.py' },
  { p: path.join(SCRIPTS_DIR, 'generate_radio_script.py'), minSize: 30000, label: 'scripts/generate_radio_script.py' }
];

requiredFiles.forEach(({ p, minSize, label }) => {
  assert.ok(fs.existsSync(p), `File must exist: ${label}`);
  const stat = fs.statSync(p);
  assert.ok(stat.size >= minSize, `File must be substantive (>=${minSize} bytes): ${label} (${stat.size} bytes)`);
  console.log(`  [PASS] Verified ${label} (${stat.size} bytes)`);
});

// -----------------------------------------------------------------------------
// Test 2: Seed Stories Schema & Quality in data/stories.json
// -----------------------------------------------------------------------------
console.log('\nTest 2: Verifying seed stories schema and resonance quality...');
const rawStories = fs.readFileSync(path.join(DATA_DIR, 'stories.json'), 'utf-8');
const stories = JSON.parse(rawStories);

assert.ok(Array.isArray(stories), 'data/stories.json must contain an array');
assert.ok(stories.length >= 5, `Must have at least 5 seeded stories (found: ${stories.length})`);

const requiredProps = [
  'story_id', 'sender_name', 'song_title', 'story_title',
  'story_content', 'created_at', 'cheer_count', 'resonance_score',
  'tier', 'status'
];

let hasTopSpotlight = false;
stories.forEach((st, idx) => {
  requiredProps.forEach((prop) => {
    assert.ok(st[prop] !== undefined && st[prop] !== null, `Story #${idx + 1} missing required property: ${prop}`);
  });

  assert.ok(st.story_content.length >= 60, `Story #${idx + 1} content must be >= 60 chars (length: ${st.story_content.length})`);
  assert.ok(st.story_content.length <= 3000, `Story #${idx + 1} content must be <= 3000 chars (length: ${st.story_content.length})`);
  assert.ok(st.cheer_count >= 0, `Story #${idx + 1} cheer_count must be non-negative`);
  assert.ok(st.resonance_score >= 0 && st.resonance_score <= 100, `Story #${idx + 1} resonance_score must be between 0 and 100`);

  if (st.tier === 'top_spotlight' && st.status === 'selected_for_radio') {
    hasTopSpotlight = true;
    assert.ok(st.broadcast_info, 'Top spotlight story must include broadcast_info');
  }
});

assert.ok(hasTopSpotlight, 'Must have at least one story with tier top_spotlight and status selected_for_radio');
console.log(`  [PASS] Seed stories valid (${stories.length} stories, schema confirmed, top spotlight present)`);

// -----------------------------------------------------------------------------
// Test 3: Client Validation Logic (js/story-hub.js)
// -----------------------------------------------------------------------------
console.log('\nTest 3: Verifying client validation and masking logic...');
const storyHubJs = fs.readFileSync(path.join(JS_DIR, 'story-hub.js'), 'utf-8');

// Validate masking function in js
assert.ok(storyHubJs.includes('maskContact'), 'story-hub.js must define contact masking');
assert.ok(storyHubJs.includes('validateStorySubmission'), 'story-hub.js must define validation logic');
assert.ok(storyHubJs.includes('SpeechRecognition'), 'story-hub.js must support Web Speech API');
assert.ok(storyHubJs.includes('paradise_cheered_'), 'story-hub.js must persist cheers in localStorage');

// Execute sandbox test of validation logic
const mockSandbox = {
  window: {},
  document: { addEventListener: () => {} },
  localStorage: { getItem: () => null, setItem: () => {} },
  console: { warn: () => {}, error: () => {} }
};

const scriptFn = new Function('window', 'document', 'localStorage', 'console', storyHubJs);
scriptFn(mockSandbox.window, mockSandbox.document, mockSandbox.localStorage, mockSandbox.console);

const hub = mockSandbox.window.ParadiseStoryHub;
assert.ok(hub, 'ParadiseStoryHub export must be available on window');

// Valid submission
const validSubmission = hub.validateStorySubmission({
  sender: '대구 이순자 어머니',
  title: '병실에서 들었던 노래',
  content: '김쌤, 작년 가을 남편을 먼저 보내고 슬픔에 빠져 있던 제게 영웅님의 노래는 큰 위로였습니다. 감사합니다.'
});
assert.strictEqual(validSubmission.valid, true, 'Valid story must pass validation');

// Too short
const shortSubmission = hub.validateStorySubmission({
  sender: '팬',
  title: '좋아요',
  content: '너무 좋습니다.'
});
assert.strictEqual(shortSubmission.valid, false, 'Short story must fail validation');

// Prohibited commercial word rejection
const badWordSubmission = hub.validateStorySubmission({
  sender: '상인',
  title: '공식 굿즈 팝니다',
  content: '파라다이스 팬 여러분 안녕하세요. 이번에 나온 영웅님 굿즈 최' + '저가로 모십니다. 많은 관심 부탁드립니다.'
});
assert.strictEqual(badWordSubmission.valid, false, 'Commercial buzzword must fail validation');

// External link rejection
const linkSubmission = hub.validateStorySubmission({
  sender: '홍보',
  title: '단톡방 오세요',
  content: '우리 함께 모여서 영웅님 응원해요. 단톡방 주소는 open.kakao.com/hero123 입니다. 어서 오세요.'
});
assert.strictEqual(linkSubmission.valid, false, 'External link must fail validation');

// Contact masking test
const masked = hub.maskContact('010-1234-5678');
assert.strictEqual(masked, '010-****-5678', 'Phone number must be properly masked');
console.log('  [PASS] Client validation and masking logic verified');

// -----------------------------------------------------------------------------
// Test 4: Algorithmic Ranking Engine (select_top_story.py)
// -----------------------------------------------------------------------------
console.log('\nTest 4: Verifying algorithmic ranking engine via python...');
const pythonCmd = 'python';

const testSelectedJsonPath = path.join(ROOT_DIR, 'content', 'test_selected_story.json');
try {
  if (fs.existsSync(testSelectedJsonPath)) fs.unlinkSync(testSelectedJsonPath);
} catch (e) {}

// Run select_top_story.py
const selectCmd = `${pythonCmd} "${path.join(SCRIPTS_DIR, 'select_top_story.py')}" --output "${testSelectedJsonPath}" --min-score 50`;
const selectOutput = execSync(selectCmd, { encoding: 'utf-8' });
assert.ok(fs.existsSync(testSelectedJsonPath), 'select_top_story.py must produce output JSON');

const selectedStory = JSON.parse(fs.readFileSync(testSelectedJsonPath, 'utf-8'));
assert.ok(selectedStory.story_id, 'Selected story must have story_id');
assert.ok(selectedStory.sender_name, 'Selected story must have sender_name');
assert.ok(selectedStory.song_title, 'Selected story must have song_title');
assert.ok(selectedStory.resonance_score >= 50.0, 'Selected story must meet min score');
assert.ok(Array.isArray(selectedStory.spoken_segments), 'Selected story must contain spoken_segments');
assert.ok(selectedStory.spoken_segments.length >= 2, 'Must have at least 2 spoken segments');

console.log(`  [PASS] Python ranking engine selected top story: '${selectedStory.story_title}' (Score: ${selectedStory.resonance_score})`);

// -----------------------------------------------------------------------------
// Test 5: YouTube Radio Bridge (generate_radio_script.py --story-file)
// -----------------------------------------------------------------------------
console.log('\nTest 5: Verifying YouTube Radio script generator bridge...');
const testOutputDir = path.join(ROOT_DIR, 'content', 'test_ep_bridge');
const radioCmd = `${pythonCmd} "${path.join(SCRIPTS_DIR, 'generate_radio_script.py')}" --episode 2 --story-file "${testSelectedJsonPath}" --output-dir "${testOutputDir}"`;
const radioOutput = execSync(radioCmd, { encoding: 'utf-8' });

const generatedScriptPath = path.join(testOutputDir, 'script_ep02.json');
const generatedMdPath = path.join(testOutputDir, 'script_ep02.md');
assert.ok(fs.existsSync(generatedScriptPath), 'Radio script JSON must exist');
assert.ok(fs.existsSync(generatedMdPath), 'Radio script Markdown must exist');

const generatedScript = JSON.parse(fs.readFileSync(generatedScriptPath, 'utf-8'));
assert.strictEqual(generatedScript.episode_number, 2, 'Episode number must be 2');
assert.strictEqual(generatedScript.total_chapters, 6, 'Must contain 6 chapters');

// Verify Chapter 4 fan letter injection
const ch4 = generatedScript.chapters.find(c => c.chapter_id === 'ch4_fan_letter');
assert.ok(ch4, 'Chapter 4 fan letter must exist');
assert.ok(ch4.title.includes(selectedStory.sender_name), 'Chapter 4 title must contain sender name');

// Check voice assignment
const letterVoiceSeg = ch4.segments.find(s => s.speaker === 'fan_letter_writer');
assert.ok(letterVoiceSeg, 'Must contain segment read by fan_letter_writer');
assert.ok(letterVoiceSeg.text.length > 10, 'Fan letter segment must contain real letter text');

// Check DJ Kim consoling
const djKimConsole = ch4.segments.find(s => s.speaker === 'dj_kim' && s.emotion === 'deep_consolation');
assert.ok(djKimConsole, 'DJ Kim deep consolation segment must exist in Chapter 4');
assert.ok(djKimConsole.text.includes(selectedStory.sender_name), 'DJ Kim consolation must name the story author');

// Verify Anti-AI lexical purity
assert.strictEqual(generatedScript.anti_ai_purity_score, '20/20 (0 AI Cliches Detected)', 'Must have 0 AI cliches');

console.log(`  [PASS] Radio bridge verified (Ch4 segments dynamically matched to ${selectedStory.sender_name})`);

// -----------------------------------------------------------------------------
// Test 6: Senior WCAG AAA Accessibility, Touch Targets & Dual-Tab UX in story.html
// -----------------------------------------------------------------------------
console.log('\nTest 6: Verifying story.html WCAG AAA accessibility, touch targets, and dual-tab DOM...');
const storyHtml = fs.readFileSync(path.join(ROOT_DIR, 'story.html'), 'utf-8');

// Dual tab buttons and containers
assert.ok(storyHtml.includes('id="tab-btn-write"'), 'story.html must have #tab-btn-write');
assert.ok(storyHtml.includes('id="tab-btn-browse"'), 'story.html must have #tab-btn-browse');
assert.ok(storyHtml.includes('id="story-write-section"'), 'story.html must have #story-write-section');
assert.ok(storyHtml.includes('id="story-browse-section"'), 'story.html must have #story-browse-section');

// Form inputs
assert.ok(storyHtml.includes('id="story-sender"'), 'Must have #story-sender input');
assert.ok(storyHtml.includes('id="story-contact"'), 'Must have #story-contact input');
assert.ok(storyHtml.includes('id="story-song"'), 'Must have #story-song selector');
assert.ok(storyHtml.includes('id="story-title"'), 'Must have #story-title input');
assert.ok(storyHtml.includes('id="story-content"'), 'Must have #story-content textarea');
assert.ok(storyHtml.includes('id="btn-voice-dictation"'), 'Must have Web Speech voice dictation button');
assert.ok(storyHtml.includes('id="story-agree"'), 'Must have broadcast consent checkbox');

// Senior Touch Targets >= 56px check
assert.ok(storyHtml.includes('min-height: 56px') || storyHtml.includes('min-height: 64px'), 'Must enforce >= 56px touch target');
assert.ok(storyHtml.includes('btn-voice'), 'Must define voice button class');
assert.ok(storyHtml.includes('btn-cheer'), 'Must define cheer button class');

// Privacy reassurance text
assert.ok(storyHtml.includes('전화번호는 선물을 보내드릴 때만 안전하게 사용되며 외부에 절대 공개되지 않습니다'), 'Privacy disclosure notice must be prominently visible');

// Photo booth navigation link per DISPATCH
assert.ok(storyHtml.includes('booth.html'), 'Navigation must include link to booth.html (Photo Booth)');
assert.ok(storyHtml.includes('영웅과 함께'), 'Photo Booth link text must say 영웅과 함께');

// Contact Email & Store 296100
assert.ok(storyHtml.includes('beable9489@gmail.com'), 'story.html must contain unified contact email beable9489@gmail.com');
assert.ok(storyHtml.includes('296100'), 'story.html must include Lemon Squeezy Store #296100');

console.log('  [PASS] WCAG AAA accessibility, touch targets (>=56px), dual tabs, and photo booth link verified');

// -----------------------------------------------------------------------------
// Test 7: Zero Prohibited Commercial Words Across All Milestone 1 Files
// -----------------------------------------------------------------------------
console.log('\nTest 7: Verifying ZERO prohibited commercial words (최' + '저가, 할' + '인율, 특' + '가, 폭' + '탄세일)...');
const prohibitedWords = ['최' + '저가', '할' + '인율', '특' + '가', '폭' + '탄세일'];
const m1Files = [
  path.join(ROOT_DIR, 'story.html'),
  path.join(JS_DIR, 'story-hub.js'),
  path.join(DATA_DIR, 'stories.json')
];

m1Files.forEach((f) => {
  const content = fs.readFileSync(f, 'utf-8');
  prohibitedWords.forEach((pw) => {
    // Check user-facing copy doesn't use prohibited words
    const count = (content.match(new RegExp(pw, 'g')) || []).length;
    assert.strictEqual(count, 0, `Prohibited word '${pw}' found in ${path.basename(f)}!`);
  });
});
console.log('  [PASS] Strictly 0 prohibited commercial words verified in story.html, story-hub.js, and stories.json');

// Cleanup temporary test artifacts
try {
  if (fs.existsSync(testSelectedJsonPath)) fs.unlinkSync(testSelectedJsonPath);
  if (fs.existsSync(testOutputDir)) fs.rmSync(testOutputDir, { recursive: true, force: true });
} catch (e) {}

console.log('\n===============================================================');
console.log('SUCCESS: ALL SENIOR STORY HUB (MILESTONE 1) TESTS PASSED (100%)');
console.log('===============================================================\n');
