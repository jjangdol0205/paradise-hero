/**
 * story_hub.test.js
 * Verification Suite for Senior Fan Story Hub ("사연 복덕방") & Radio Bridge (2026-11-11 HQ Spec).
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

const requiredFiles = [
  { p: path.join(ROOT_DIR, 'story.html'), minSize: 5000, label: 'story.html' },
  { p: path.join(JS_DIR, 'story-hub.js'), minSize: 3000, label: 'js/story-hub.js' },
  { p: path.join(DATA_DIR, 'stories.json'), minSize: 1500, label: 'data/stories.json' },
  { p: path.join(SCRIPTS_DIR, 'select_top_story.py'), minSize: 3000, label: 'scripts/select_top_story.py' },
  { p: path.join(SCRIPTS_DIR, 'generate_radio_script.py'), minSize: 15000, label: 'scripts/generate_radio_script.py' }
];

requiredFiles.forEach(({ p, minSize, label }) => {
  assert.ok(fs.existsSync(p), `File must exist: ${label}`);
  const stat = fs.statSync(p);
  assert.ok(stat.size >= minSize, `File must be substantive (>=${minSize} bytes): ${label} (${stat.size} bytes)`);
});

const rawStories = fs.readFileSync(path.join(DATA_DIR, 'stories.json'), 'utf-8');
const stories = JSON.parse(rawStories);
assert.ok(Array.isArray(stories) && stories.length >= 5);
assert.ok(!rawStories.includes('건행'), 'stories.json must NOT contain 건행');

const storyHubJs = fs.readFileSync(path.join(JS_DIR, 'story-hub.js'), 'utf-8');
const mockSandbox = {
  window: {},
  document: { addEventListener: () => {} },
  localStorage: { getItem: () => null, setItem: () => {} },
  console: { warn: () => {}, error: () => {} }
};
new Function('window', 'document', 'localStorage', 'console', storyHubJs)(
  mockSandbox.window, mockSandbox.document, mockSandbox.localStorage, mockSandbox.console
);
const hub = mockSandbox.window.ParadiseStoryHub;
assert.ok(hub);
assert.strictEqual(hub.maskContact('010-1234-5678'), '010-****-5678');

const testSelectedJsonPath = path.join(ROOT_DIR, 'content', 'test_selected_story.json');
const testOutputDir = path.join(ROOT_DIR, 'content', 'test_ep_bridge');
try {
  execSync(`python "${path.join(SCRIPTS_DIR, 'select_top_story.py')}" --output "${testSelectedJsonPath}" --min-score 50`, { encoding: 'utf-8' });
  const selectedStory = JSON.parse(fs.readFileSync(testSelectedJsonPath, 'utf-8'));
  execSync(`python "${path.join(SCRIPTS_DIR, 'generate_radio_script.py')}" --episode 2 --story-file "${testSelectedJsonPath}" --output-dir "${testOutputDir}"`, { encoding: 'utf-8' });
  const generatedScript = JSON.parse(fs.readFileSync(path.join(testOutputDir, 'script_ep02.json'), 'utf-8'));
  assert.strictEqual(generatedScript.total_chapters, 6);
  const ch4 = generatedScript.chapters.find(c => c.chapter_id === 'ch4_fan_letter');
  assert.ok(ch4 && ch4.title.includes(selectedStory.sender_name));
  console.log(`  [PASS] Story Hub ranking & Radio 3-story bridge verified (${selectedStory.sender_name})`);
} finally {
  try {
    if (fs.existsSync(testSelectedJsonPath)) fs.unlinkSync(testSelectedJsonPath);
    if (fs.existsSync(testOutputDir)) fs.rmSync(testOutputDir, { recursive: true, force: true });
  } catch (e) {}
}

const storyHtml = fs.readFileSync(path.join(ROOT_DIR, 'story.html'), 'utf-8');
assert.ok(storyHtml.includes('id="tab-btn-write"') && storyHtml.includes('id="tab-btn-browse"'));
assert.ok(storyHtml.includes('booth.html') && storyHtml.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').includes('🎁 무료 선물제작소'));
assert.ok(storyHtml.includes('beable9489@gmail.com'));
assert.ok(!storyHtml.includes('296100') && !/lemonsqueezy/i.test(storyHtml));

console.log('\n===============================================================');
console.log('SUCCESS: ALL SENIOR STORY HUB TESTS PASSED (100%)');
console.log('===============================================================\n');
