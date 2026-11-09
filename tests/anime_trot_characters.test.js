/**
 * anime_trot_characters.test.js
 * Automated verification test suite for Milestone 2 (F4, F5):
 * 10 Anime Prince Trot Singer Characters Data, Pillow Procedural Illustrations,
 * 20 RGBA PNG Assets, and Universal Character Catalog on paradise-hero.com
 *
 * Test Sections:
 * 1. Physical file existence and non-trivial sizes (>1KB for JSON, >2KB for JS, >3KB for Python script).
 * 2. characters.json JSON schema integrity, complete 10-character array, and unique ID validation.
 * 3. js/character-catalog.js UMD module exports, helper methods (getCharacterById, getAllCharacters, getCharacterThemeColor).
 * 4. Strict parity between data/characters.json and js/character-catalog.js.
 * 5. Physical existence and sizes of all 20 image assets in assets/characters/.
 * 6. Programmatic PNG binary header validation:
 *    - All 10 sprites: exactly 1080x1440 resolution, ColorType 6 (RGBA transparency).
 *    - All 10 thumbnails: exactly 160x160 resolution, ColorType 6 (RGBA transparency).
 * 7. Zero Prohibited Commercial Words (최저가, 할인율, 특가, 폭탄세일) compliance across all M2 files.
 * 8. Fandom representation and emotional catchphrase completeness for all 10 male trot princes.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const DATA_CHARACTERS_JSON = path.join(ROOT_DIR, 'data', 'characters.json');
const JS_CATALOG = path.join(ROOT_DIR, 'js', 'character-catalog.js');
const PY_GEN_SCRIPT = path.join(ROOT_DIR, 'scripts', 'generate_characters.py');
const CHARACTERS_DIR = path.join(ROOT_DIR, 'assets', 'characters');

const EXPECTED_IDS = [
  'hwang_young_woong',
  'lim_young_woong',
  'lee_chan_won',
  'young_tak',
  'jeong_dong_won',
  'kim_ho_joong',
  'jang_min_ho',
  'park_seo_jin',
  'son_tae_jin',
  'ahn_sung_hoon_jin_hae_seong'
];

const PROHIBITED_WORDS = ['최저가', '할인율', '특가', '폭탄세일'];

/**
 * Parses binary PNG IHDR chunk from file buffer
 * Returns { width, height, bitDepth, colorType }
 */
function readPngMetadata(filePath) {
  const fd = fs.openSync(filePath, 'r');
  const buffer = Buffer.alloc(29);
  fs.readSync(fd, buffer, 0, 29, 0);
  fs.closeSync(fd);

  // PNG magic header: 89 50 4E 47 0D 0A 1A 0A
  const isPng = buffer[0] === 0x89 &&
                buffer[1] === 0x50 &&
                buffer[2] === 0x4E &&
                buffer[3] === 0x47 &&
                buffer[4] === 0x0D &&
                buffer[5] === 0x0A &&
                buffer[6] === 0x1A &&
                buffer[7] === 0x0A;
  assert.ok(isPng, `File ${path.basename(filePath)} must have valid PNG magic signature`);

  // IHDR chunk: width (16..19), height (20..23), bitDepth (24), colorType (25)
  const width = buffer.readUInt32BE(16);
  const height = buffer.readUInt32BE(20);
  const bitDepth = buffer.readUInt8(24);
  const colorType = buffer.readUInt8(25); // 6 = RGBA

  return { width, height, bitDepth, colorType };
}

console.log('===============================================================');
console.log('Running Milestone 2: 10 Anime Prince Trot Characters Test Suite');
console.log('===============================================================\n');

// -----------------------------------------------------------------------------
// Test 1: Physical File Existence & Non-trivial Sizes
// -----------------------------------------------------------------------------
console.log('Test 1: Verifying physical file existence and substantive sizes...');

assert.ok(fs.existsSync(DATA_CHARACTERS_JSON), 'data/characters.json must exist');
const jsonStat = fs.statSync(DATA_CHARACTERS_JSON);
assert.ok(jsonStat.size > 1000, `data/characters.json must be >1KB, got ${jsonStat.size} bytes`);
console.log(`  [PASS] data/characters.json verified (${jsonStat.size} bytes).`);

assert.ok(fs.existsSync(JS_CATALOG), 'js/character-catalog.js must exist');
const jsStat = fs.statSync(JS_CATALOG);
assert.ok(jsStat.size > 2000, `js/character-catalog.js must be >2KB, got ${jsStat.size} bytes`);
console.log(`  [PASS] js/character-catalog.js verified (${jsStat.size} bytes).`);

assert.ok(fs.existsSync(PY_GEN_SCRIPT), 'scripts/generate_characters.py must exist');
const pyStat = fs.statSync(PY_GEN_SCRIPT);
assert.ok(pyStat.size > 3000, `scripts/generate_characters.py must be >3KB, got ${pyStat.size} bytes`);
console.log(`  [PASS] scripts/generate_characters.py verified (${pyStat.size} bytes).`);

assert.ok(fs.existsSync(CHARACTERS_DIR), 'assets/characters/ directory must exist');
const assetFiles = fs.readdirSync(CHARACTERS_DIR);
assert.ok(assetFiles.length >= 20, `assets/characters must contain at least 20 PNG files, found ${assetFiles.length}`);
console.log(`  [PASS] assets/characters/ directory verified (${assetFiles.length} files found).\n`);

// -----------------------------------------------------------------------------
// Test 2: JSON Schema Validation & Required Fields
// -----------------------------------------------------------------------------
console.log('Test 2: Validating data/characters.json schema and required fields...');

const rawData = fs.readFileSync(DATA_CHARACTERS_JSON, 'utf-8');
const characters = JSON.parse(rawData);

assert.ok(Array.isArray(characters), 'data/characters.json must be a JSON array');
assert.strictEqual(characters.length, 10, 'Must contain exactly 10 characters');

const foundIds = new Set();
const hexColorRegex = /^#[0-9A-Fa-f]{6}$/;

characters.forEach((char, index) => {
  const prefix = `Character #${index + 1} (${char.id || 'unknown'}):`;
  
  assert.ok(char.id && typeof char.id === 'string', `${prefix} id must be non-empty string`);
  assert.ok(!foundIds.has(char.id), `${prefix} id '${char.id}' must be unique`);
  foundIds.add(char.id);

  assert.ok(char.name_ko && typeof char.name_ko === 'string', `${prefix} name_ko must be non-empty string`);
  assert.ok(char.name_en && typeof char.name_en === 'string', `${prefix} name_en must be non-empty string`);
  assert.ok(char.title && typeof char.title === 'string', `${prefix} title must be non-empty string`);
  
  assert.ok(hexColorRegex.test(char.theme_color), `${prefix} theme_color '${char.theme_color}' must be valid 6-char hex`);
  assert.ok(hexColorRegex.test(char.accent_color), `${prefix} accent_color '${char.accent_color}' must be valid 6-char hex`);
  
  assert.ok(char.badge_emoji && typeof char.badge_emoji === 'string', `${prefix} badge_emoji must be non-empty string`);
  assert.ok(char.catchphrase && typeof char.catchphrase === 'string', `${prefix} catchphrase must be non-empty string`);
  assert.ok(char.signature_visual && typeof char.signature_visual === 'string', `${prefix} signature_visual must be non-empty string`);
  
  assert.strictEqual(char.thumb_path, `assets/characters/thumb_${char.id}.png`, `${prefix} thumb_path must match standard pattern`);
  assert.strictEqual(char.sprite_path, `assets/characters/sprite_${char.id}.png`, `${prefix} sprite_path must match standard pattern`);
});

EXPECTED_IDS.forEach(expectedId => {
  assert.ok(foundIds.has(expectedId), `Must include expected character '${expectedId}'`);
});
console.log('  [PASS] All 10 characters verified with complete required schema fields.\n');

// -----------------------------------------------------------------------------
// Test 3: js/character-catalog.js UMD Module Exports & Helper Methods
// -----------------------------------------------------------------------------
console.log('Test 3: Testing js/character-catalog.js module exports & helper methods...');

const catalog = require(JS_CATALOG);

assert.ok(Array.isArray(catalog.CHARACTER_CARDS), 'catalog.CHARACTER_CARDS must be an array');
assert.strictEqual(catalog.CHARACTER_CARDS.length, 10, 'CHARACTER_CARDS must have exactly 10 items');

assert.strictEqual(typeof catalog.getCharacterById, 'function', 'catalog.getCharacterById must be a function');
assert.strictEqual(typeof catalog.getAllCharacters, 'function', 'catalog.getAllCharacters must be a function');
assert.strictEqual(typeof catalog.getCharacterThemeColor, 'function', 'catalog.getCharacterThemeColor must be a function');

// Test getCharacterById
const hwang = catalog.getCharacterById('hwang_young_woong');
assert.ok(hwang, "getCharacterById('hwang_young_woong') must return character object");
assert.strictEqual(hwang.name_ko, '황영웅');
assert.strictEqual(hwang.title, '감성 황태자');
assert.strictEqual(hwang.theme_color, '#1B4D3E');

const nonExistent = catalog.getCharacterById('non_existent_singer');
assert.strictEqual(nonExistent, null, 'getCharacterById on unknown id must return null');

// Test getAllCharacters immutability / copy
const allChars = catalog.getAllCharacters();
assert.strictEqual(allChars.length, 10);

// Test getCharacterThemeColor
const limColor = catalog.getCharacterThemeColor('lim_young_woong');
assert.strictEqual(limColor, '#38BDF8');
const fallbackColor = catalog.getCharacterThemeColor('invalid_id', '#123456');
assert.strictEqual(fallbackColor, '#123456');

console.log('  [PASS] js/character-catalog.js API functions verified.\n');

// -----------------------------------------------------------------------------
// Test 4: Strict Parity between JSON and JS
// -----------------------------------------------------------------------------
console.log('Test 4: Checking strict parity between characters.json and character-catalog.js...');

assert.strictEqual(characters.length, catalog.CHARACTER_CARDS.length, 'JSON and JS catalog lengths must match');
for (let i = 0; i < characters.length; i++) {
  const jsonChar = characters[i];
  const jsChar = catalog.CHARACTER_CARDS[i];
  assert.strictEqual(jsonChar.id, jsChar.id, `ID mismatch at index ${i}`);
  assert.strictEqual(jsonChar.name_ko, jsChar.name_ko, `name_ko mismatch for ${jsonChar.id}`);
  assert.strictEqual(jsonChar.title, jsChar.title, `title mismatch for ${jsonChar.id}`);
  assert.strictEqual(jsonChar.theme_color, jsChar.theme_color, `theme_color mismatch for ${jsonChar.id}`);
  assert.strictEqual(jsonChar.thumb_path, jsChar.thumb_path, `thumb_path mismatch for ${jsonChar.id}`);
  assert.strictEqual(jsonChar.sprite_path, jsChar.sprite_path, `sprite_path mismatch for ${jsonChar.id}`);
}
console.log('  [PASS] Strict 1:1 parity confirmed between JSON and JS catalog.\n');

// -----------------------------------------------------------------------------
// Test 5 & 6: Programmatic PNG Binary Header & RGBA Transparency Validation
// -----------------------------------------------------------------------------
console.log('Test 5 & 6: Validating 20 PNG assets physical presence, dimensions, and RGBA...');

let checkedSprites = 0;
let checkedThumbs = 0;

EXPECTED_IDS.forEach(id => {
  const spriteRel = `assets/characters/sprite_${id}.png`;
  const thumbRel = `assets/characters/thumb_${id}.png`;
  const spriteFull = path.join(ROOT_DIR, spriteRel);
  const thumbFull = path.join(ROOT_DIR, thumbRel);

  // 1. Physical presence & size
  assert.ok(fs.existsSync(spriteFull), `Master sprite missing: ${spriteRel}`);
  const sStat = fs.statSync(spriteFull);
  assert.ok(sStat.size > 10000, `Master sprite ${spriteRel} too small (<10KB: got ${sStat.size} bytes)`);

  assert.ok(fs.existsSync(thumbFull), `Selector thumbnail missing: ${thumbRel}`);
  const tStat = fs.statSync(thumbFull);
  assert.ok(tStat.size > 5000, `Thumbnail ${thumbRel} too small (<5KB: got ${tStat.size} bytes)`);

  // 2. Binary PNG Header Inspection
  const sMeta = readPngMetadata(spriteFull);
  assert.strictEqual(sMeta.width, 1080, `Sprite ${id} width must be 1080, got ${sMeta.width}`);
  assert.strictEqual(sMeta.height, 1440, `Sprite ${id} height must be 1440, got ${sMeta.height}`);
  assert.strictEqual(sMeta.colorType, 6, `Sprite ${id} must be RGBA (ColorType 6), got ${sMeta.colorType}`);
  checkedSprites++;

  const tMeta = readPngMetadata(thumbFull);
  assert.strictEqual(tMeta.width, 160, `Thumbnail ${id} width must be 160, got ${tMeta.width}`);
  assert.strictEqual(tMeta.height, 160, `Thumbnail ${id} height must be 160, got ${tMeta.height}`);
  assert.strictEqual(tMeta.colorType, 6, `Thumbnail ${id} must be RGBA (ColorType 6), got ${tMeta.colorType}`);
  checkedThumbs++;

  console.log(`  [PASS] ${id}: Sprite (1080x1440 RGBA, ${(sStat.size / 1024).toFixed(1)} KB) | Thumb (160x160 RGBA, ${(tStat.size / 1024).toFixed(1)} KB)`);
});

assert.strictEqual(checkedSprites, 10, 'Must have verified exactly 10 master sprites');
assert.strictEqual(checkedThumbs, 10, 'Must have verified exactly 10 selector thumbnails');
console.log('  [PASS] All 20 PNG images physically confirmed with genuine RGBA 1080x1440 and 160x160 dimensions.\n');

// -----------------------------------------------------------------------------
// Test 7: Zero Prohibited Commercial Words Compliance
// -----------------------------------------------------------------------------
console.log('Test 7: Enforcing GEMINI.md Zero-Tolerance Prohibited Commercial Words...');

const filesToScan = [
  { path: DATA_CHARACTERS_JSON, name: 'data/characters.json' },
  { path: JS_CATALOG, name: 'js/character-catalog.js' },
  { path: PY_GEN_SCRIPT, name: 'scripts/generate_characters.py' }
];

filesToScan.forEach(fileInfo => {
  const content = fs.readFileSync(fileInfo.path, 'utf-8');
  PROHIBITED_WORDS.forEach(badWord => {
    const hasBadWord = content.includes(badWord);
    assert.strictEqual(hasBadWord, false, `Prohibited word '${badWord}' detected in ${fileInfo.name}!`);
  });
  console.log(`  [PASS] ${fileInfo.name} is 100% clean of prohibited words.`);
});
console.log('  [PASS] Zero prohibited commercial words compliance verified.\n');

// -----------------------------------------------------------------------------
// Test 8: Fandom Representation & Emotional Catchphrases
// -----------------------------------------------------------------------------
console.log('Test 8: Verifying emotional catchphrases & fandom representation...');

const hwangProfile = catalog.getCharacterById('hwang_young_woong');
assert.ok(hwangProfile.catchphrase.includes('어머님'), 'Hwang Young-woong catchphrase must honor mothers');
assert.ok(hwangProfile.signature_visual.includes('에메랄드'), 'Hwang Young-woong must have emerald visual motif');

const limProfile = catalog.getCharacterById('lim_young_woong');
assert.ok(limProfile.catchphrase.includes('건행'), 'Lim Young-woong catchphrase must include gun-haeng');

const chanwonProfile = catalog.getCharacterById('lee_chan_won');
assert.ok(chanwonProfile.title.includes('찬또'), 'Lee Chan-won must carry Chan-tto title');

console.log('  [PASS] Fandom resonance and emotional catchphrases validated.\n');

console.log('===============================================================');
console.log('ALL TESTS PASSED (100% Success) — Milestone 2 Complete!');
console.log('===============================================================');
