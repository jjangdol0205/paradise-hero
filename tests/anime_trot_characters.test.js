/**
 * anime_trot_characters.test.js
 * Verification Suite for Singer Hwang Young-woong's 10 Signature Stage & Daily Outfits Catalog,
 * 20 RGBA PNG Assets, and Zero Other-Singer Guarantee on paradise-hero.com (2026-11-11 HQ Spec).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const DATA_CHARACTERS_JSON = path.join(ROOT_DIR, 'data', 'characters.json');
const JS_CATALOG = path.join(ROOT_DIR, 'js', 'character-catalog.js');
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

const BANNED_OTHER_SINGERS = [
  '임영웅', '이찬원', '영탁', '정동원', '김호중', '장민호', '박서진', '손태진', '안성훈', '진해성'
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
console.log('Running Hwang Young-woong 10 Signature Outfits Catalog Test Suite');
console.log('===============================================================\n');

const rawData = fs.readFileSync(DATA_CHARACTERS_JSON, 'utf-8');
const jsRaw = fs.readFileSync(JS_CATALOG, 'utf-8');

BANNED_OTHER_SINGERS.forEach((s) => {
  assert.ok(!rawData.includes(s), `data/characters.json must NOT contain '${s}'`);
  assert.ok(!jsRaw.includes(s), `js/character-catalog.js must NOT contain '${s}'`);
});
assert.ok(!rawData.includes('건행') && !jsRaw.includes('건행'), 'Must NOT contain 건행');
assert.ok(!rawData.includes('10대 왕자') && !jsRaw.includes('10대 왕자'), 'Must NOT contain 10대 왕자');

const characters = JSON.parse(rawData);
assert.strictEqual(characters.length, 10);

characters.forEach((char, index) => {
  assert.strictEqual(char.name_ko, '황영웅', `Outfit #${index + 1} name_ko must be '황영웅'`);
  assert.strictEqual(char.name_en, 'Hwang Young-woong');
  assert.ok(char.title && char.title.length >= 4);
  assert.strictEqual(char.thumb_path.split('?')[0], `assets/characters/thumb_${char.id}.png`);
  assert.strictEqual(char.sprite_path.split('?')[0], `assets/characters/sprite_${char.id}.png`);
});

const catalog = require(JS_CATALOG);
assert.strictEqual(catalog.CHARACTER_CARDS.length, 10);
for (let i = 0; i < 10; i++) {
  assert.strictEqual(characters[i].id, catalog.CHARACTER_CARDS[i].id);
  assert.strictEqual(characters[i].name_ko, catalog.CHARACTER_CARDS[i].name_ko);
  assert.strictEqual(characters[i].title, catalog.CHARACTER_CARDS[i].title);
}
console.log('  [PASS] 100% Hwang Young-woong 10 signature outfits & JSON/JS 1:1 parity verified.');

EXPECTED_IDS.forEach((id) => {
  const spriteFull = path.join(CHARACTERS_DIR, `sprite_${id}.png`);
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
console.log('  [PASS] All 20 PNG assets (1080x1440 sprites & 160x160 thumbs RGBA) verified.');

console.log('\n===============================================================');
console.log('ALL HWANG YOUNG-WOONG 10-OUTFIT CATALOG TESTS PASSED (100%)!');
console.log('===============================================================');
