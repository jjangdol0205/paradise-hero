/**
 * character-catalog.js
 * 오리지널 가상 트로트 가수 『백운호 (Baek Woon-ho)』 6대 무대 의상 카탈로그 모듈 (paradise-hero.com)
 *
 * - 실존 연예인 성명/파일명 0건 원칙 엄수
 * - assets/characters/hero_style_01.png ~ hero_style_06.png 및 thumb_hero_style_01.png ~ 06.png 일대일 매핑
 * - UMD 호환: 브라우저 전역(window.CHARACTER_CARDS) 및 Node.js(module.exports) 동시 지원
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    const exported = factory();
    root.CHARACTER_CARDS = exported.CHARACTER_CARDS;
    root.CharacterCatalog = exported;
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const CHARACTER_CARDS = [
    {
      id: 'hero_style_01',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '① 에메랄드 정장',
      theme_color: '#1B4D3E',
      accent_color: '#D4AF37',
      badge_emoji: '💚',
      catchphrase: '흰 구름 머무는 호수처럼 어머님·아버님 곁을 따뜻하게 지키겠습니다 💚',
      signature_visual: '에메랄드 벨벳 무대 정장, 황금 브로치, 다정한 미소 인사',
      thumb_path: 'assets/characters/thumb_hero_style_01.png',
      sprite_path: 'assets/characters/hero_style_01.png'
    },
    {
      id: 'hero_style_02',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '② 화이트 콘서트 턱시도',
      theme_color: '#38BDF8',
      accent_color: '#F0F9FF',
      badge_emoji: '🤍',
      catchphrase: '어머니의 봄날처럼 늘 건강하고 환한 꽃길만 걸으세요 🤍',
      signature_visual: '순백의 콘서트 턱시도, 실크 보타이, 환한 눈웃음 인사',
      thumb_path: 'assets/characters/thumb_hero_style_02.png',
      sprite_path: 'assets/characters/hero_style_02.png'
    },
    {
      id: 'hero_style_03',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '③ 클래식 네이비 수트',
      theme_color: '#1E3A8A',
      accent_color: '#EFF6FF',
      badge_emoji: '💙',
      catchphrase: '항구의 등불처럼 지친 하루 끝에 든든한 위로가 되어드릴게요 💙',
      signature_visual: '클래식 네이비 정통 수트, 단정한 행커치프, 든든한 응원 포즈',
      thumb_path: 'assets/characters/thumb_hero_style_03.png',
      sprite_path: 'assets/characters/hero_style_03.png'
    },
    {
      id: 'hero_style_04',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '④ 따뜻한 가을 코트',
      theme_color: '#D97706',
      accent_color: '#FFFBEB',
      badge_emoji: '🍂',
      catchphrase: '백운호 연가 흥얼거리며 도란도란 가을 산책길 함께 걸어요 🍂',
      signature_visual: '포근한 베이지 가을 코트, 따뜻한 머플러, 다정한 에스코트',
      thumb_path: 'assets/characters/thumb_hero_style_04.png',
      sprite_path: 'assets/characters/hero_style_04.png'
    },
    {
      id: 'hero_style_05',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '⑤ 전통 한복 자락',
      theme_color: '#CA8A04',
      accent_color: '#FEFCE8',
      badge_emoji: '🌕',
      catchphrase: '어머님·아버님 가정에 늘 만복과 평안이 가득하시길 기원합니다 🌕',
      signature_visual: '고운 금빛 전통 한복 두루마기, 정갈한 큰절 효도 인사',
      thumb_path: 'assets/characters/thumb_hero_style_05.png',
      sprite_path: 'assets/characters/hero_style_05.png'
    },
    {
      id: 'hero_style_06',
      name_ko: '백운호',
      name_en: 'Baek Woon-ho',
      title: '⑥ 라디오 DJ 스튜디오룩',
      theme_color: '#9A3412',
      accent_color: '#FFF7ED',
      badge_emoji: '🎙️',
      catchphrase: '김쌤의영웅라디오 부스에서 어머님·아버님 사연을 기다립니다 🎙️',
      signature_visual: '라디오 DJ 스튜디오 니트와 안경, 빈티지 마이크 앞 다정한 눈맞춤',
      thumb_path: 'assets/characters/thumb_hero_style_06.png',
      sprite_path: 'assets/characters/hero_style_06.png'
    }
  ];

  function getCharacterById(id) {
    if (!id) return null;
    const found = CHARACTER_CARDS.find((c) => c.id === id);
    return found || null;
  }

  function getAllCharacters() {
    return CHARACTER_CARDS.map((c) => Object.assign({}, c));
  }

  function getCharacterThemeColor(id, fallbackColor = '#1B4D3E') {
    const char = getCharacterById(id);
    return char && char.theme_color ? char.theme_color : fallbackColor;
  }

  return {
    CHARACTER_CARDS,
    getCharacterById,
    getAllCharacters,
    getCharacterThemeColor
  };
});
