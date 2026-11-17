/**
 * anime_trot_characters.test.js
 * Verification Suite for Virtual Trot Singer Baek Woon-ho (백운호) 6 Stage Outfits Catalog,
 * 12 RGBA PNG Assets (hero_style_01~06), and Zero Real-Celebrity File/Name Guarantee.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const DATA_CHARACTERS_JSON = path.join(ROOT_DIR, 'data', 'characters.json');
const JS_CATALOG = path.join(ROOT_DIR, 'js', 'character-catalog.js');
const CHARACTERS_DIR = path.join(ROOT_DIR, 'assets', 'characters');

const EXPECTED_IDS = [
  'hero_style_01',
  'hero_style_02',
  'hero_style_03',
  'hero_style_04',
  'hero_style_05',
  'hero_style_06'
];

const BANNED_SLUGS = [
  'hwang_young_woong', 'lim_young_woong', 'lee_chan_won', 'young_tak',
  'kim_ho_joong', 'jang_min_ho', 'jeong_dong_won', 'park_seo_jin',
  'son_tae_jin', 'ahn_sung_hoon', 'jin_hae_seong'
];

function readPngMetadata(filePath) {
  const fd = fs.openSync(filePath, 'r');
  const buffer = Buffer.alloc(29);
  fs.readSync(fd, buffer, 0, 29, 0);
  fs.closeSync(fd);

  const isPng = buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4E && buffer[3] === 0x47;
  assert.ok(isPng, `File ${path.basename(filePath)} must have valid PNG magic signature`);
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
    bitDepth: buffer.readUInt8(24),
    colorType: buffer.readUInt8(25)
  };
}

console.log('===============================================================');
console.log('Running Virtual Singer Baek Woon-ho 6 Outfits Catalog Test Suite');
console.log('===============================================================\n');

// Verify zero real-singer filenames exist in assets/characters/
const dirFiles = fs.readdirSync(CHARACTERS_DIR);
dirFiles.forEach((fname) => {
  const low = fname.toLowerCase();
  BANNED_SLUGS.forEach((slug) => {
    assert.ok(!low.includes(slug), `Banned real-celebrity filename '${fname}' still exists in assets/characters/`);
  });
});

const rawData = fs.readFileSync(DATA_CHARACTERS_JSON, 'utf-8');
const jsRaw = fs.readFileSync(JS_CATALOG, 'utf-8');
const characters = JSON.parse(rawData);
assert.strictEqual(characters.length, 6);

characters.forEach((char, index) => {
  assert.strictEqual(char.id, EXPECTED_IDS[index]);
  assert.strictEqual(char.name_ko, '백운호', `Outfit #${index + 1} name_ko must be '백운호'`);
  assert.strictEqual(char.name_en, 'Baek Woon-ho');
  assert.strictEqual(char.thumb_path, `assets/characters/thumb_${char.id}.png`);
  assert.strictEqual(char.sprite_path, `assets/characters/${char.id}.png`);
});

const catalog = require(JS_CATALOG);
assert.strictEqual(catalog.CHARACTER_CARDS.length, 6);
for (let i = 0; i < 6; i++) {
  assert.strictEqual(characters[i].id, catalog.CHARACTER_CARDS[i].id);
  assert.strictEqual(characters[i].name_ko, catalog.CHARACTER_CARDS[i].name_ko);
  assert.strictEqual(characters[i].title, catalog.CHARACTER_CARDS[i].title);
}
console.log('  [PASS] Baek Woon-ho 6 stage outfits & JSON/JS 1:1 parity verified.');

EXPECTED_IDS.forEach((id) => {
  const spriteFull = path.join(CHARACTERS_DIR, `${id}.png`);
  const thumbFull = path.join(CHARACTERS_DIR, `thumb_${id}.png`);
  assert.ok(fs.existsSync(spriteFull) && fs.statSync(spriteFull).size > 10000);
  assert.ok(fs.existsSync(thumbFull) && fs.statSync(thumbFull).size > 5000);

  const sMeta = readPngMetadata(spriteFull);
  assert.strictEqual(sMeta.width, 1080);
  assert.strictEqual(sMeta.height, 1440);
  assert.strictEqual(sMeta.colorType, 6);

  const tMeta = readPngMetadata(thumbFull);
  assert.strictEqual(tMeta.width, 160);
  assert.strictEqual(tMeta.height, 160);
  assert.strictEqual(tMeta.colorType, 6);
});
console.log('  [PASS] All 12 PNG assets (hero_style_01~06 1080x1440 & thumb_hero_style_01~06 160x160 RGBA) verified.');

console.log('\n===============================================================');
console.log('ALL BAEK WOON-HO 6-OUTFIT CATALOG TESTS PASSED (100%)!');
console.log('===============================================================');
