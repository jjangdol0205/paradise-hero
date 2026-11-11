/**
 * js/vip-digital-studio.js
 * ==============================================================================
 * 4사업부 파라다이스히어로 (paradise-hero.com)
 * 황영웅 10대 유료 디지털 굿즈 & 어머님 초밀착 참여형 효도 아이템 제작소 엔진
 *
 * [전격 가동 10대 유료 참여 아이템]
 * 1. 황영웅 카톡 아침 안부 카드 & 명절·생일 연하장 생성기 (1080x1350 Canvas)
 * 2. 파라다이스 공식 황금 명예 팬증(시민증) 발급기 (1080x680 Canvas)
 * 3. 황영웅 핸드폰 잠금화면 (큰글씨 달력·시계 배경화면) 생성기 (1080x1920 Canvas)
 * 4. 내 이름을 불러주는 라디오 DJ 생일축하·쾌유기원 맞춤 음성편지 (Web Speech + 화음 BGM)
 * 5. 황영웅 전곡 왕글씨(30px) 가사집 & 노래교실 부르기 비법서 (열람 & 인쇄/PDF)
 * 6. 오늘의 황영웅 황금 행운 부적 & 생년(띠)별 대박 운세 뽑기 (1080x1350 Canvas)
 * 7. 우리 가족 소원 등불(연등) 달기 & 황영웅 대박 기원탑 인증서 (1080x1350 Canvas + 실시간 등불 전광판)
 * 8. 황영웅에게 바치는 가상 황금 꽃다발 & 효자가수 대상 상장 수여식 (1080x1080 Canvas)
 * 9. 내 이름이 찍힌 황영웅 VIP 골든 콘서트 소장용 기념 티켓 발급기 (1080x560 Canvas)
 * 10. 치매 예방 & 팬심 테스트 '황영웅 찐팬 골든벨 퀴즈' & 장원급제 수료증 (1080x800 Canvas)
 *
 * [100% 무제한 무료 개방]
 * - 회원가입·결제 없이 전 아이템 평생 무제한 무료 (credits: 9999, unlimitedVip: true)
 * - 카카오톡 인앱 브라우저(KAKAOTALK UA) 및 모바일 2초 꾹 저장 왕글씨(22px+) 안내 모달 자동 탑재
 * - ZERO Emojis on Canvas (맑은 고딕 두부 '□' 깨짐 0% 보장)
 * ==============================================================================
 */

(function (global) {
  'use strict';

  const STUDIO_STORAGE_KEY = 'paradise_vip_studio_state_free_v3';
  const LANTERN_STORAGE_KEY = 'paradise_wish_lanterns_v1';

  const HWANG_PORTRAITS = [
    { idx: 1, label: '에메랄드 벨벳 콘서트 수트', src: 'assets/characters/sprite_hwang_young_woong.png?v=20261110c' },
    { idx: 2, label: '순백의 프린스 턱시도', src: 'assets/characters/sprite_lim_young_woong.png?v=20261110c' },
    { idx: 3, label: '따뜻한 핑크 가디건 하트룩', src: 'assets/characters/sprite_lee_chan_won.png?v=20261110c' },
    { idx: 4, label: '시크 올블랙 수트', src: 'assets/characters/sprite_young_tak.png?v=20261110c' },
    { idx: 5, label: '로열 제복 스타일', src: 'assets/characters/sprite_jeong_dong_won.png?v=20261110c' },
    { idx: 6, label: '퍼플 벨벳 디너쇼룩', src: 'assets/characters/sprite_kim_ho_joong.png?v=20261110c' },
    { idx: 7, label: '가을 트렌치코트 산책룩', src: 'assets/characters/sprite_jang_min_ho.png?v=20261110c' },
    { idx: 8, label: '황금빛 명절 한복룩', src: 'assets/characters/sprite_park_seo_jin.png?v=20261110c' },
    { idx: 9, label: '버건디 장미 세레나데룩', src: 'assets/characters/sprite_son_tae_jin.png?v=20261110c' },
    { idx: 10, label: '심야 라디오 DJ 안경룩', src: 'assets/characters/sprite_ahn_sung_hoon_jin_hae_seong.png?v=20261110c' }
  ];

  const GREETING_TEMPLATES = [
    {
      id: 'morning',
      title: '아침 문안 인사',
      header: '행복한 아침 문안 인사',
      line1: '오늘도 황영웅님 노래처럼',
      line2: '건강하고 꽃길만 걸으시는',
      line3: '행복한 하루 보내세요!'
    },
    {
      id: 'weekend',
      title: '주말·계절 안부',
      header: '따뜻한 주말 안부 편지',
      line1: '바람이 참 좋은 계절입니다.',
      line2: '언제나 당신 편인 영웅님과 함께',
      line3: '웃음꽃 피는 주말 되세요!'
    },
    {
      id: 'birthday',
      title: '생신 축하 연하장',
      header: '생신을 진심으로 축하드립니다',
      line1: '세상에서 가장 소중하고 귀한 날,',
      line2: '황영웅님의 따뜻한 노래와 함께',
      line3: '백세까지 만수무강하세요!'
    },
    {
      id: 'health',
      title: '환절기 건강 인사',
      header: '늘 건강하시기를 응원합니다',
      line1: '아프신 곳 없이 늘 튼튼하시고',
      line2: '마음 가득 평안하시기를',
      line3: '따뜻한 마음을 담아 응원합니다!'
    },
    {
      id: 'holiday',
      title: '명절·새해 복 인사',
      header: '가정에 황금빛 복이 가득하길',
      line1: '늘 건강하시고 하시는 모든 일마다',
      line2: '황금빛 행운과 평안이 가득하시길',
      line3: '두 손 모아 기원합니다!'
    },
    {
      id: 'thankyou',
      title: '감사·사랑 인사',
      header: '늘 고맙고 사랑합니다',
      line1: '소중한 인연에 깊이 감사드리며',
      line2: '황영웅님 목소리처럼 포근한',
      line3: '축복이 늘 함께하시길 바랍니다!'
    }
  ];

  const SONG_GUIDES = [
    {
      id: '당신 편',
      title: '당신 편 (정규 1집 타이틀)',
      tempo: '느린 트롯 발라드 (72 BPM)',
      key_note: '핵심 비법: 첫 소절은 말하듯 나지막이 시작하고, 후렴구 "내가 당신 편이 되어줄게요"에서 가슴 깊은 중저음 울림을 실어주세요.',
      lines: [
        '1절 가이드: 세상이 등을 돌려도 [숨쉬기 ∨] 눈물이 앞을 가려도 [부드럽게 ~]',
        '후렴 포인트: ★ 내가 당신 편이 되어줄게요 [길게 울림 ~~~] 언제까지나 영원히 ★',
        '노래교실 팁: 고음에서 목을 조이지 말고 어머님 한숨 쉬듯 편안하게 배에서 소리를 밀어 올리세요.'
      ]
    },
    {
      id: '비상',
      title: '비상 (가슴 뭉클한 역전 명곡)',
      tempo: '락 발라드 트롯 (74 BPM)',
      key_note: '핵심 비법: 1절은 독백처럼 낮게 읊조리고, 후렴 "나 이제 날아오른다"에서 양팔을 벌리듯 성량을 폭발시키세요.',
      lines: [
        '1절 가이드: 그토록 오랫동안 움츠렸던 날개를 [숨쉬기 ∨] 이제는 활짝 펴고 [감정 고조 ▲]',
        '후렴 포인트: ★ 하늘 높이 날아오른다 [길게 호흡 유지 ~~~] 거친 바람을 가르며 ★',
        '노래교실 팁: 후렴 들어가기 직전 코와 입으로 깊게 숨을 들이마셔야 끝음이 흔들리지 않습니다.'
      ]
    },
    {
      id: '인생아 고마웠다',
      title: '인생아 고마웠다 (어머님 애창 1위)',
      tempo: '정통 트롯 슬로우 (76 BPM)',
      key_note: '핵심 비법: 지나온 세월을 쓰다듬듯 따뜻한 미소를 머금고 부르시면 듣는 분들의 눈시울이 붉어집니다.',
      lines: [
        '1절 가이드: 미운 정 고운 정 다 품고 살아온 [숨쉬기 ∨] 내 인생아 참 고마웠다 [꺾기 ♪]',
        '후렴 포인트: ★ 눈물도 웃음도 다 내 보석이었네 [깊은 비브라토 ~~~] ★',
        '노래교실 팁: "고마웠다"의 "다" 발음을 급하게 닫지 말고 2초간 여운을 남겨주세요.'
      ]
    },
    {
      id: '해바라기',
      title: '해바라기 (정규 1집 수록곡)',
      tempo: '미디엄 템포 정통 트롯 (88 BPM)',
      key_note: '핵심 비법: 경쾌하면서도 애절한 리듬감이 생명입니다. 박자 끝음마다 살짝 들어 올리는 트롯 꺾기를 넣어보세요.',
      lines: [
        '1절 가이드: 오직 한 사람만 바라보는 [숨쉬기 ∨] 해바라기 같은 내 사랑 [박자 정박 ●]',
        '후렴 포인트: ★ 비가 오나 눈이 오나 당신만을 기다립니다 [감정 강조 ★]',
        '노래교실 팁: 어깨에 힘을 빼고 무릎으로 살짝 리듬을 타면서 부르시면 박자가 흔들리지 않습니다.'
      ]
    },
    {
      id: '안 볼 때 없을 때',
      title: '안 볼 때 없을 때 (경쾌한 리듬)',
      tempo: '네오 트롯 미디엄 (104 BPM)',
      key_note: '핵심 비법: 박수 치며 부르기 가장 좋은 흥겨운 곡입니다! 첫 박에 강세를 주어 신나게 리듬을 타세요.',
      lines: [
        '1절 가이드: 있을 때 잘해 후회하지 말고 [숨쉬기 ∨] 안 볼 때 없을 때 더 생각나는 사람 [경쾌하게 ●]',
        '후렴 포인트: ★ 바로 지금 내 옆에 있는 당신이 최고야 [밝은 미소로 ~~~] ★',
        '노래교실 팁: 노래교실 박수 짝-짝 리듬에 맞춰 끝음을 짧고 통통 튀게 끊어 불러보세요.'
      ]
    },
    {
      id: '미운 사랑',
      title: '미운 사랑 (황영웅 중저음 레전드)',
      tempo: '미디엄 발라드 트롯 (80 BPM)',
      key_note: '핵심 비법: 원곡보다 반 키 낮춰서 황영웅님처럼 굵고 묵직한 저음으로 시작하면 노래방 최고점이 나옵니다.',
      lines: [
        '1절 가이드: 가랑비 내리는 밤거리에서 [숨쉬기 ∨] 가슴에 묻어둔 미운 사랑아 [중저음 강조 ●]',
        '후렴 포인트: ★ 왜 이렇게 눈물이 나니 [크게 열기 ★] 잊으려 해도 잊지 못할 사람아',
        '노래교실 팁: "왜 이렇게" 부분에서 입을 세로로 크게 벌려야 소리가 시원하게 뻗어 나갑니다.'
      ]
    }
  ];

  const FORTUNE_MESSAGES = {
    health: {
      title: '무병장수 · 백세건강 황금대길 부적',
      fortune: '막혔던 기운이 풀리고 몸과 마음에 활력이 솟아나는 대길(大吉)의 날입니다!',
      luckySong: '행운의 명곡: 당신 편 (아침·저녁 1회 청취 시 복 배가)',
      luckyItem: '행운의 색깔: 에메랄드 그린 & 황금색'
    },
    wealth: {
      title: '가정만복 · 재물운 대박 황금 부적',
      fortune: '생각지 못한 반가운 소식과 재물복이 대문을 두드리는 황금빛 운세입니다!',
      luckySong: '행운의 명곡: 해바라기 (밝은 미소로 흥얼거리면 재물운 상승)',
      luckyItem: '행운의 숫자: 7, 10, 88'
    },
    children: {
      title: '자녀성공 · 손주건강 만사형통 부적',
      fortune: '자녀와 손주들에게 귀인이 나타나 하는 일마다 술술 풀리는 축복의 운세입니다!',
      luckySong: '행운의 명곡: 비상 (자녀들을 떠올리며 들으시면 만사형통)',
      luckyItem: '행운의 방향: 동남쪽 (따뜻한 차 한 잔의 여유)'
    }
  };

  const portraitCache = {};

  function preloadPortraits(callback) {
    let loaded = 0;
    HWANG_PORTRAITS.forEach((p) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = p.src;
      img.onload = () => {
        portraitCache[p.idx] = img;
        loaded++;
        if (loaded === 1 && typeof callback === 'function') callback();
      };
      img.onerror = () => {
        loaded++;
      };
    });
  }

  function resolvePortraitFromValue(val) {
    if (!val) return portraitCache[1];
    const num = parseInt(val, 10);
    if (!isNaN(num) && portraitCache[num]) return portraitCache[num];
    if (String(val).includes('2_') || String(val).includes('lim')) return portraitCache[2] || portraitCache[1];
    if (String(val).includes('3_') || String(val).includes('lee')) return portraitCache[3] || portraitCache[1];
    if (String(val).includes('4_') || String(val).includes('young_tak')) return portraitCache[4] || portraitCache[1];
    if (String(val).includes('5_') || String(val).includes('jeong')) return portraitCache[5] || portraitCache[1];
    if (String(val).includes('6_') || String(val).includes('jin_haesung') || String(val).includes('kim_ho')) return portraitCache[6] || portraitCache[1];
    if (String(val).includes('7_') || String(val).includes('jang')) return portraitCache[7] || portraitCache[1];
    if (String(val).includes('8_') || String(val).includes('park')) return portraitCache[8] || portraitCache[1];
    if (String(val).includes('9_') || String(val).includes('son')) return portraitCache[9] || portraitCache[1];
    if (String(val).includes('10_') || String(val).includes('ahn')) return portraitCache[10] || portraitCache[1];
    return portraitCache[1];
  }

  function getStudioState() {
    let totalCreated = 0;
    try {
      const raw = localStorage.getItem(STUDIO_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        totalCreated = Number(parsed.totalCreated) || 0;
      }
    } catch (e) {}
    return {
      credits: 9999,
      unlimitedVip: true,
      totalCreated: totalCreated
    };
  }

  function saveStudioState(state) {
    const normalized = {
      credits: 9999,
      unlimitedVip: true,
      totalCreated: Number(state && state.totalCreated) || 0
    };
    try {
      localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify(normalized));
    } catch (e) {}
    updateStudioCreditBadge();
  }

  function updateStudioCreditBadge() {
    const text = '🎁 100% 평생 무제한 무료 개방';
    ['vip-studio-credit-count', 'studio-credit-badge'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    });
  }

  function consumeStudioCredit(itemLabel) {
    const state = getStudioState();
    incrementParticipationTicker(itemLabel || '디지털 선물 발급');
    state.credits = 9999;
    state.unlimitedVip = true;
    state.totalCreated = (state.totalCreated || 0) + 1;
    saveStudioState(state);
    return true;
  }

  function openStudioPaywallModal() {
    // 100% 무료 전환 완료 — 결제 모달 미노출
  }

  function closeStudioPaywallModal() {
    const modal = document.getElementById('vip-studio-paywall-modal');
    if (modal) {
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  function redeemStudioToken() {
    const st = getStudioState();
    saveStudioState(st);
  }

  function incrementParticipationTicker(actionLabel) {
    const countEl = document.getElementById('live-today-participation-count');
    if (countEl) {
      const current = parseInt(String(countEl.textContent).replace(/[^0-9]/g, ''), 10) || 4820;
      countEl.textContent = (current + 1).toLocaleString('ko-KR');
    }
    const feedEl = document.getElementById('live-participation-feed');
    if (feedEl && actionLabel) {
      const item = document.createElement('span');
      item.style.cssText = 'display:inline-block; background:#FEF3C7; color:#92400E; font-weight:800; padding:4px 12px; border-radius:999px; margin-right:8px; font-size:16px;';
      item.textContent = `방금 전 [${actionLabel}] 참여 완료!`;
      feedEl.prepend(item);
    }
  }

  function drawVectorStar(ctx, cx, cy, r, color) {
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const angle = (i * Math.PI) / 4 - Math.PI / 2;
      const rad = i % 2 === 0 ? r : r * 0.25;
      const x = cx + Math.cos(angle) * rad;
      const y = cy + Math.sin(angle) * rad;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function drawVectorRose(ctx, cx, cy, r, mainColor, coreColor) {
    ctx.save();
    ctx.fillStyle = mainColor;
    for (let i = 0; i < 6; i++) {
      const a = (i * Math.PI) / 3;
      ctx.beginPath();
      ctx.arc(cx + Math.cos(a) * (r * 0.42), cy + Math.sin(a) * (r * 0.42), r * 0.55, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = coreColor;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.45, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function getTodayKoreanDateStr() {
    const now = new Date();
    const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
    return `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${now.getDate()}일 ${days[now.getDay()]}`;
  }

  // ===========================================================================
  // ITEM 1: 황영웅 카톡 아침 안부 카드 & 연하장 생성기 (1080x1350)
  // ===========================================================================
  function renderGreetingCard() {
    const canvas = document.getElementById('gc-canvas') || document.getElementById('greeting-card-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1350;

    const themeSel = document.getElementById('gc-template') || document.getElementById('greeting-theme-select');
    const portraitSel = document.getElementById('gc-look') || document.getElementById('greeting-portrait-select');
    const senderInput = document.getElementById('gc-sender') || document.getElementById('greeting-sender-input');
    const customInput = document.getElementById('gc-custom-msg') || document.getElementById('greeting-custom-msg');

    const themeId = (themeSel && themeSel.value) || 'morning';
    const senderName = ((senderInput && senderInput.value) || '파라다이스 팬 드림').trim();
    const customMsg = ((customInput && customInput.value) || '').trim();
    const tpl = GREETING_TEMPLATES.find((t) => t.id === themeId) || GREETING_TEMPLATES[0];

    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#0E2820');
    bgGrad.addColorStop(0.55, '#1B4D3E');
    bgGrad.addColorStop(1, '#091A14');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 14;
    ctx.strokeRect(32, 32, W - 64, H - 64);
    ctx.strokeStyle = '#FDE68A';
    ctx.lineWidth = 4;
    ctx.strokeRect(52, 52, W - 104, H - 104);

    drawVectorRose(ctx, 110, 110, 28, '#E11D48', '#FDE047');
    drawVectorRose(ctx, W - 110, 110, 28, '#E11D48', '#FDE047');
    drawVectorStar(ctx, 180, 180, 18, '#FDE68A');
    drawVectorStar(ctx, W - 180, 180, 18, '#FDE68A');

    ctx.fillStyle = '#D4AF37';
    ctx.fillRect(140, 86, W - 280, 74);
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 38px "Malgun Gothic", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(tpl.header, W / 2, 136);

    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 28px "Malgun Gothic", sans-serif';
    ctx.fillText(getTodayKoreanDateStr(), W / 2, 206);

    const pImg = resolvePortraitFromValue(portraitSel && portraitSel.value);
    if (pImg) {
      const halo = ctx.createRadialGradient(W / 2, 540, 40, W / 2, 540, 340);
      halo.addColorStop(0, 'rgba(253, 230, 138, 0.42)');
      halo.addColorStop(1, 'rgba(27, 77, 62, 0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(W / 2, 540, 340, 0, Math.PI * 2);
      ctx.fill();
      ctx.drawImage(pImg, 220, 220, 640, 850);
    }

    ctx.fillStyle = 'rgba(250, 250, 248, 0.96)';
    ctx.fillRect(76, 860, W - 152, 390);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 6;
    ctx.strokeRect(76, 860, W - 152, 390);

    ctx.fillStyle = '#111827';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    if (customMsg.length > 0) {
      const l1 = customMsg.slice(0, 18);
      const l2 = customMsg.slice(18, 36);
      const l3 = customMsg.slice(36, 54);
      ctx.fillText(l1, W / 2, 955);
      if (l2) ctx.fillText(l2, W / 2, 1020);
      if (l3) ctx.fillText(l3, W / 2, 1085);
    } else {
      ctx.fillText(tpl.line1, W / 2, 950);
      ctx.fillText(tpl.line2, W / 2, 1018);
      ctx.fillStyle = '#1B4D3E';
      ctx.fillText(tpl.line3, W / 2, 1086);
    }

    ctx.fillStyle = '#0E2820';
    ctx.fillRect(180, 1140, W - 360, 76);
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 36px "Malgun Gothic", sans-serif';
    ctx.fillText(`보내는 이: ${senderName}`, W / 2, 1190);

    ctx.fillStyle = '#A7F3D0';
    ctx.font = 'bold 24px "Malgun Gothic", sans-serif';
    ctx.fillText('황영웅 공식 팬덤 플랫폼 PARADISE-HERO.COM', W / 2, 1290);
  }

  // ===========================================================================
  // ITEM 2: 파라다이스 황금 명예 팬증(시민증) 발급기 (1080x680)
  // ===========================================================================
  function renderFanIdCard() {
    const canvas = document.getElementById('fid-canvas') || document.getElementById('fan-id-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 680;

    const nameInput = document.getElementById('fid-name') || document.getElementById('fan-id-name');
    const regionInput = document.getElementById('fid-region') || document.getElementById('fan-id-region');
    const songInput = document.getElementById('fid-song') || document.getElementById('fan-id-song');
    const portraitSel = document.getElementById('fid-look') || document.getElementById('fan-id-portrait');

    const fanName = ((nameInput && nameInput.value) || '이순자 어머니').trim();
    const region = ((regionInput && regionInput.value) || '대구·경북 본부').trim();
    const favSong = ((songInput && songInput.value) || '당신 편').trim();

    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#0F2E24');
    grad.addColorStop(0.5, '#1B4D3E');
    grad.addColorStop(1, '#091914');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 14;
    ctx.strokeRect(24, 24, W - 48, H - 48);
    ctx.strokeStyle = '#FDE68A';
    ctx.lineWidth = 3;
    ctx.strokeRect(40, 40, W - 80, H - 80);

    ctx.fillStyle = '#D4AF37';
    ctx.fillRect(40, 40, W - 80, 105);
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 42px "Malgun Gothic", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('PARADISE GOLDEN VIP CITIZEN ID', 75, 106);

    let hash = 2026;
    for (let i = 0; i < fanName.length; i++) {
      hash = (hash * 31 + fanName.charCodeAt(i)) % 9000 + 1000;
    }
    const serialNo = `NO. PH-2026-${hash}`;

    ctx.textAlign = 'left';
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 32px "Malgun Gothic", sans-serif';
    ctx.fillText(`회원번호: ${serialNo}`, 75, 210);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 50px "Malgun Gothic", sans-serif';
    ctx.fillText(`성 함 : ${fanName}`, 75, 295);

    ctx.fillStyle = '#D1FAE5';
    ctx.font = 'bold 34px "Malgun Gothic", sans-serif';
    ctx.fillText(`소속 지부 : ${region}`, 75, 368);
    ctx.fillText(`평생 애창곡 : ${favSong}`, 75, 430);
    ctx.fillText(`회원 등급 : 황금 VIP 정회원 (평생 당신 편)`, 75, 492);

    ctx.fillStyle = '#D4AF37';
    ctx.fillRect(75, 535, 580, 68);
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 28px "Malgun Gothic", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('위 분을 가수 황영웅 평생 명예 후원회원으로 인증함', 365, 579);

    ctx.fillStyle = '#FAFAF8';
    ctx.fillRect(730, 178, 280, 360);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 6;
    ctx.strokeRect(730, 178, 280, 360);

    const pImg = resolvePortraitFromValue(portraitSel && portraitSel.value);
    if (pImg) {
      ctx.save();
      ctx.beginPath();
      ctx.rect(734, 182, 272, 352);
      ctx.clip();
      ctx.drawImage(pImg, 630, 155, 420, 560);
      ctx.restore();
    }

    ctx.textAlign = 'center';
    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 22px "Malgun Gothic", sans-serif';
    ctx.fillText('파라다이스 총괄본부 공인 | paradise-hero.com', 870, 585);
  }

  // ===========================================================================
  // ITEM 3: 황영웅 핸드폰 잠금화면 (큰글씨 달력·시계 배경화면) (1080x1920)
  // ===========================================================================
  function renderLockscreenWallpaper() {
    const canvas = document.getElementById('wp-canvas') || document.getElementById('wallpaper-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1920;

    const portraitSel = document.getElementById('wp-look') || document.getElementById('wallpaper-portrait-select');
    const msgInput = document.getElementById('wp-motto') || document.getElementById('wallpaper-motto-input');
    const motto = ((msgInput && msgInput.value) || '영웅님과 함께 오늘도 건강하고 행복하게!').trim();

    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#071712');
    bgGrad.addColorStop(0.5, '#1B4D3E');
    bgGrad.addColorStop(1, '#0A1E17');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    const starPositions = [
      [140, 160, 16], [920, 150, 20], [200, 360, 14], [880, 380, 18],
      [120, 680, 18], [950, 720, 22]
    ];
    starPositions.forEach(([sx, sy, sr]) => drawVectorStar(ctx, sx, sy, sr, '#FDE68A'));

    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(253, 230, 138, 0.85)';
    ctx.font = 'bold 28px "Malgun Gothic", sans-serif';
    ctx.fillText('PARADISE HERO · 황영웅 공식 잠금화면', W / 2, 105);

    const pImg = resolvePortraitFromValue(portraitSel && portraitSel.value);
    if (pImg) {
      const halo = ctx.createRadialGradient(W / 2, 740, 40, W / 2, 740, 440);
      halo.addColorStop(0, 'rgba(243, 229, 171, 0.35)');
      halo.addColorStop(1, 'rgba(27, 77, 62, 0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(W / 2, 740, 440, 0, Math.PI * 2);
      ctx.fill();
      ctx.drawImage(pImg, 130, 220, 820, 1090);
    }

    ctx.fillStyle = 'rgba(250, 250, 248, 0.97)';
    ctx.fillRect(64, 1180, W - 128, 660);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 8;
    ctx.strokeRect(64, 1180, W - 128, 660);

    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const todayDate = now.getDate();

    ctx.fillStyle = '#0E2820';
    ctx.fillRect(68, 1184, W - 136, 96);
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    ctx.fillText(`${year}년 ${month + 1}월 큰글씨 달력 (음력 보름·기념일)`, W / 2, 1248);

    const days = ['일', '월', '화', '수', '목', '금', '토'];
    const startX = 148;
    const colW = 130;
    ctx.font = '900 32px "Malgun Gothic", sans-serif';
    days.forEach((d, i) => {
      ctx.fillStyle = i === 0 ? '#DC2626' : (i === 6 ? '#2563EB' : '#1F2937');
      ctx.fillText(d, startX + i * colW, 1335);
    });

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    let row = 0;
    let col = firstDay;

    ctx.font = '900 34px "Malgun Gothic", sans-serif';
    for (let d = 1; d <= daysInMonth; d++) {
      const x = startX + col * colW;
      const y = 1400 + row * 66;

      if (d === todayDate) {
        ctx.fillStyle = '#1B4D3E';
        ctx.beginPath();
        ctx.arc(x, y - 12, 28, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#FDE68A';
      } else if (col === 0) {
        ctx.fillStyle = '#DC2626';
      } else if (col === 6) {
        ctx.fillStyle = '#2563EB';
      } else {
        ctx.fillStyle = '#111827';
      }
      ctx.fillText(String(d), x, y);

      col++;
      if (col > 6) {
        col = 0;
        row++;
      }
    }

    ctx.fillStyle = '#1B4D3E';
    ctx.fillRect(96, 1742, W - 192, 72);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 28px "Malgun Gothic", sans-serif';
    ctx.fillText(motto.slice(0, 28), W / 2, 1788);
  }

  // ===========================================================================
  // ITEM 4: 내 이름을 불러주는 라디오 DJ 맞춤 음성편지 생성 & 재생
  // ===========================================================================
  function generateVoiceLetterText() {
    const recInput = document.getElementById('vl-name') || document.getElementById('voice-recipient-input');
    const occSelect = document.getElementById('vl-occasion') || document.getElementById('voice-occasion-select');
    const sendInput = document.getElementById('vl-sender') || document.getElementById('voice-sender-input');
    const previewBox = document.getElementById('vl-script-preview') || document.getElementById('voice-letter-script-preview');

    const recipient = ((recInput && recInput.value) || '이순자 어머니').trim();
    const occasion = (occSelect && occSelect.value) || 'birthday';
    const sender = ((sendInput && sendInput.value) || '사랑하는 가족 & 김쌤 라디오').trim();

    let body = '';
    if (occasion === 'birthday') {
      body = `안녕하세요, 김쌤의 영웅라디오입니다. 오늘 세상에서 가장 귀하고 아름다운 날을 맞이하신 ${recipient}! 생신을 진심으로 축하드립니다. 그동안 가족을 위해 묵묵히 걸어오신 어머님의 고운 손길에 깊은 감사와 존경을 올립니다. 언제나 어머님 편인 가수 황영웅님의 따뜻한 노래 들으시면서, 올 한 해도 아프신 곳 없이 백세까지 만수무강하시고 꽃길만 걸으시길 진심으로 기원합니다. (${sender})`;
    } else if (occasion === 'health') {
      body = `안녕하세요, 김쌤의 영웅라디오입니다. ${recipient}, 요즘 환절기에 몸은 좀 어떠신가요? 어머님께서 늘 건강하시고 웃음 가득하시기를 바라는 마음으로 특별 음성편지를 전해드립니다. 황영웅님의 깊은 중저음 목소리가 어머님의 지친 마음을 포근히 안아드릴 거예요. 오늘도 식사 꼭 잘 챙겨 드시고 늘 힘내세요! (${sender})`;
    } else {
      body = `안녕하세요, 김쌤의 영웅라디오입니다. 언제나 가수 황영웅님의 든든한 버팀목이 되어주시는 ${recipient}! 어머님의 따뜻한 응원과 사랑 덕분에 오늘도 파라다이스는 봄날처럼 빛납니다. 오늘 하루도 황영웅님의 명곡 '당신 편'과 함께 가장 행복하고 보람찬 시간 보내시길 응원합니다! (${sender})`;
    }

    if (previewBox) {
      previewBox.textContent = body;
    }
    return body;
  }

  function playWarmBackgroundChord() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const freqs = [261.63, 329.63, 392.00, 523.25];
      freqs.forEach((f) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = f;
        gain.gain.setValueAtTime(0.001, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.035, ctx.currentTime + 0.8);
        gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 5.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 5.6);
      });
    } catch (e) {}
  }

  function playVoiceLetterAloud() {
    if (!consumeStudioCredit('라디오 맞춤 음성편지')) return;
    const text = generateVoiceLetterText();
    playWarmBackgroundChord();

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'ko-KR';
      utter.rate = 0.92;
      utter.pitch = 1.0;
      window.speechSynthesis.speak(utter);
    } else {
      alert('음성 편지 대본이 생성되었습니다:\n\n' + text);
    }
  }

  // ===========================================================================
  // ITEM 5: 황영웅 전곡 왕글씨(30px) 가사집 & 노래교실 부르기 비법서
  // ===========================================================================
  function renderLyricGuide() {
    const sel = document.getElementById('lb-song-select') || document.getElementById('lyric-song-select');
    const container = document.getElementById('lb-guide-box') || document.getElementById('lyric-guide-display');
    if (!container) return;

    const songVal = (sel && sel.value) || '당신 편';
    const guide = SONG_GUIDES.find((s) => s.id === songVal || s.title.includes(songVal)) || SONG_GUIDES[0];

    container.innerHTML = `
      <div style="background: #0E2820; color: #FDE68A; padding: 18px 22px; border-radius: 14px; margin-bottom: 16px;">
        <div style="font-size: 18px; font-weight: 700; color: #A7F3D0; margin-bottom: 4px;">템포 및 리듬: ${guide.tempo}</div>
        <div style="font-size: 26px; font-weight: 900; margin-bottom: 8px;">${guide.title}</div>
        <div style="font-size: 21px; line-height: 1.6; color: #FFFFFF;">${guide.key_note}</div>
      </div>
      <div style="background: #FAFAF8; border: 3px solid #D4AF37; border-radius: 14px; padding: 22px;">
        ${guide.lines
          .map(
            (ln) =>
              `<p style="font-size: 30px; font-weight: 900; color: #111827; line-height: 1.75; margin-bottom: 16px; border-bottom: 1px dashed #D1D5DB; padding-bottom: 12px;">${ln}</p>`
          )
          .join('')}
      </div>
    `;
  }

  // ===========================================================================
  // ITEM 6: 오늘의 황영웅 황금 행운 부적 & 띠별·생년별 대박 운세 뽑기 (1080x1350)
  // ===========================================================================
  function renderFortuneTalisman() {
    const canvas = document.getElementById('ft-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1350;

    const nameEl = document.getElementById('ft-name');
    const yearEl = document.getElementById('ft-birth-year');
    const wishEl = document.getElementById('ft-wish-type');

    const fanName = ((nameEl && nameEl.value) || '이순자 어머니').trim();
    const birthYear = (yearEl && yearEl.value) || '1958년생 (황금 개띠)';
    const wishType = (wishEl && wishEl.value) || 'health';
    const info = FORTUNE_MESSAGES[wishType] || FORTUNE_MESSAGES.health;

    // Gold & Imperial Vermilion Talisman Gradient
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#451A03');
    grad.addColorStop(0.5, '#78350F');
    grad.addColorStop(1, '#1C1917');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Double Ornate Gold Talisman Border
    ctx.strokeStyle = '#FACC15';
    ctx.lineWidth = 18;
    ctx.strokeRect(36, 36, W - 72, H - 72);
    ctx.strokeStyle = '#FEF08A';
    ctx.lineWidth = 5;
    ctx.strokeRect(60, 60, W - 120, H - 120);

    // Top Red-Gold Seal Banner
    ctx.fillStyle = '#B91C1C';
    ctx.fillRect(100, 90, W - 200, 92);
    ctx.strokeStyle = '#FACC15';
    ctx.lineWidth = 4;
    ctx.strokeRect(100, 90, W - 200, 92);

    ctx.textAlign = 'center';
    ctx.fillStyle = '#FEF08A';
    ctx.font = '900 42px "Malgun Gothic", sans-serif';
    ctx.fillText(info.title, W / 2, 150);

    // Portrait Halo & Golden Hanbok/Prince Hwang Young-woong
    const pImg = portraitCache[8] || portraitCache[1];
    if (pImg) {
      const halo = ctx.createRadialGradient(W / 2, 520, 50, W / 2, 520, 340);
      halo.addColorStop(0, 'rgba(250, 204, 21, 0.55)');
      halo.addColorStop(1, 'rgba(120, 53, 15, 0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(W / 2, 520, 340, 0, Math.PI * 2);
      ctx.fill();
      ctx.drawImage(pImg, 240, 210, 600, 800);
    }

    // Fortune Scroll Box
    ctx.fillStyle = '#FFFBEB';
    ctx.fillRect(80, 820, W - 160, 430);
    ctx.strokeStyle = '#D97706';
    ctx.lineWidth = 8;
    ctx.strokeRect(80, 820, W - 160, 430);

    ctx.fillStyle = '#991B1B';
    ctx.font = '900 40px "Malgun Gothic", sans-serif';
    ctx.fillText(`${fanName} (${birthYear}) 오늘의 대길 운세`, W / 2, 895);

    ctx.fillStyle = '#111827';
    ctx.font = '900 34px "Malgun Gothic", sans-serif';
    const f1 = info.fortune.slice(0, 22);
    const f2 = info.fortune.slice(22, 48);
    ctx.fillText(f1, W / 2, 975);
    if (f2) ctx.fillText(f2, W / 2, 1030);

    ctx.fillStyle = '#065F46';
    ctx.font = 'bold 30px "Malgun Gothic", sans-serif';
    ctx.fillText(info.luckySong, W / 2, 1110);
    ctx.fillStyle = '#92400E';
    ctx.fillText(info.luckyItem, W / 2, 1165);

    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 26px "Malgun Gothic", sans-serif';
    ctx.fillText(`${getTodayKoreanDateStr()} · 황영웅 파라다이스 황금부적`, W / 2, 1295);
  }

  // ===========================================================================
  // ITEM 7: 우리 가족 소원 등불(연등) 달기 & 대박 기원탑 인증서 (1080x1350)
  // ===========================================================================
  function renderWishLantern() {
    const canvas = document.getElementById('wl-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1350;

    const nameEl = document.getElementById('wl-name');
    const wishEl = document.getElementById('wl-wish');
    const colorEl = document.getElementById('wl-color');

    const fanName = ((nameEl && nameEl.value) || '대구 이순자 어머니').trim();
    const wishText = ((wishEl && wishEl.value) || '우리 가족 모두 아프지 말고 황영웅 콘서트 대박나게 해주세요!').trim();
    const lanternType = (colorEl && colorEl.value) || 'gold';

    // Night Sky Gradient
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#040D1A');
    bgGrad.addColorStop(0.55, '#0F2922');
    bgGrad.addColorStop(1, '#071410');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 12;
    ctx.strokeRect(32, 32, W - 64, H - 64);

    // Draw glowing Lantern in Upper Center
    const lanternColors = {
      gold: ['#FDE047', '#CA8A04'],
      emerald: ['#6EE7B7', '#059669'],
      pink: ['#F9A8D4', '#DB2777']
    };
    const [cLight, cDark] = lanternColors[lanternType] || lanternColors.gold;

    const glow = ctx.createRadialGradient(W / 2, 360, 30, W / 2, 360, 290);
    glow.addColorStop(0, cLight);
    glow.addColorStop(0.5, 'rgba(250, 204, 21, 0.25)');
    glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(W / 2, 360, 290, 0, Math.PI * 2);
    ctx.fill();

    // Lantern Body
    ctx.fillStyle = cDark;
    ctx.beginPath();
    ctx.ellipse(W / 2, 360, 175, 145, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#FEF08A';
    ctx.lineWidth = 6;
    ctx.stroke();

    // Lantern Cap & Tassel
    ctx.fillStyle = '#78350F';
    ctx.fillRect(W / 2 - 90, 195, 180, 32);
    ctx.fillRect(W / 2 - 80, 495, 160, 28);

    ctx.textAlign = 'center';
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    ctx.fillText('소 원 성 취', W / 2, 375);

    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 40px "Malgun Gothic", sans-serif';
    ctx.fillText('파라다이스 황금 소원 등불 점등 인증서', W / 2, 130);

    // Wish Plaque
    ctx.fillStyle = 'rgba(255, 251, 235, 0.96)';
    ctx.fillRect(84, 620, W - 168, 560);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 8;
    ctx.strokeRect(84, 620, W - 168, 560);

    ctx.fillStyle = '#0E2820';
    ctx.font = '900 42px "Malgun Gothic", sans-serif';
    ctx.fillText(`점등인: ${fanName}`, W / 2, 710);

    ctx.fillStyle = '#1F2937';
    ctx.font = '900 36px "Malgun Gothic", sans-serif';
    const w1 = wishText.slice(0, 20);
    const w2 = wishText.slice(20, 40);
    const w3 = wishText.slice(40, 60);
    ctx.fillText(`"${w1}`, W / 2, 820);
    if (w2) ctx.fillText(w2, W / 2, 880);
    if (w3) ctx.fillText(`${w3}"`, W / 2, 940);
    else ctx.fillText('"', W / 2, 880);

    ctx.fillStyle = '#065F46';
    ctx.font = 'bold 30px "Malgun Gothic", sans-serif';
    ctx.fillText('어머님의 간절한 기도가 황영웅님의 노래와 함께', W / 2, 1045);
    ctx.fillText('반드시 이루어지기를 파라다이스가 함께 기원합니다.', W / 2, 1095);

    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 26px "Malgun Gothic", sans-serif';
    ctx.fillText(`${getTodayKoreanDateStr()} · PARADISE-HERO.COM`, W / 2, 1265);
  }

  function lightUpWishLanternAndDownload() {
    if (!consumeStudioCredit('가족 소원 등불 점등')) return;
    const nameEl = document.getElementById('wl-name');
    const wishEl = document.getElementById('wl-wish');
    const fanName = ((nameEl && nameEl.value) || '대구 이순자 어머니').trim();
    const wishText = ((wishEl && wishEl.value) || '우리 가족 건강과 황영웅 대박 기원!').trim();

    try {
      const list = JSON.parse(localStorage.getItem(LANTERN_STORAGE_KEY) || '[]');
      list.unshift({ name: fanName, wish: wishText, date: getTodayKoreanDateStr() });
      localStorage.setItem(LANTERN_STORAGE_KEY, JSON.stringify(list.slice(0, 12)));
    } catch (e) {}

    renderLiveLanternWall();
    triggerDirectDownload('wl-canvas', '황영웅_소원성취_등불인증서');
  }

  function renderLiveLanternWall() {
    const wall = document.getElementById('wl-live-list');
    if (!wall) return;
    let saved = [];
    try {
      saved = JSON.parse(localStorage.getItem(LANTERN_STORAGE_KEY) || '[]');
    } catch (e) {}
    const defaults = [
      { name: '대구 이순자 어머니', wish: '우리 아들 딸 손주들 올 한 해 아프지 않고 만사형통하길 기원합니다!' },
      { name: '부산 해운대 박정숙님', wish: '황영웅 정규앨범 대박나고 전국투어 전석 매진되기를 두 손 모아 빕니다!' },
      { name: '서울 송파 김영희맘', wish: '남편 무릎 통증 깨끗이 낫고 영웅님 콘서트 부부 동반으로 꼭 가고 싶어요!' }
    ];
    const merged = saved.concat(defaults).slice(0, 6);
    wall.innerHTML = merged
      .map(
        (item) => `
        <div style="background:#0E2820; color:#FFFFFF; border:2px solid #D4AF37; border-radius:12px; padding:12px 16px;">
          <strong style="color:#FDE68A; font-size:18px;">🕯️ [${item.name}]</strong>
          <p style="font-size:18px; color:#ECFDF5; margin-top:4px;">"${item.wish}"</p>
        </div>`
      )
      .join('');
  }

  // ===========================================================================
  // ITEM 8: 황영웅에게 바치는 가상 황금 꽃다발 & 사랑의 상장 수여식 (1080x1080)
  // ===========================================================================
  function renderFlowerTribute() {
    const canvas = document.getElementById('fl-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1080;

    const nameEl = document.getElementById('fl-name');
    const titleEl = document.getElementById('fl-award-title');
    const bouquetEl = document.getElementById('fl-bouquet');

    const fanName = ((nameEl && nameEl.value) || '이순자 어머니').trim();
    const awardTitle = (titleEl && titleEl.value) || '대한민국 최고 효자가수 대상';
    const bouquetName = (bouquetEl && bouquetEl.value) || '황금 장미 100송이 대왕 꽃다발';

    // Cream & Gold Certificate Background
    ctx.fillStyle = '#FFFDF5';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 22;
    ctx.strokeRect(36, 36, W - 72, H - 72);
    ctx.strokeStyle = '#0E2820';
    ctx.lineWidth = 6;
    ctx.strokeRect(62, 62, W - 124, H - 124);

    // Corner Roses
    drawVectorRose(ctx, 115, 115, 34, '#E11D48', '#FACC15');
    drawVectorRose(ctx, W - 115, 115, 34, '#E11D48', '#FACC15');
    drawVectorRose(ctx, 115, H - 115, 34, '#E11D48', '#FACC15');
    drawVectorRose(ctx, W - 115, H - 115, 34, '#E11D48', '#FACC15');

    ctx.textAlign = 'center';
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 54px "Malgun Gothic", sans-serif';
    ctx.fillText('황 금 사 랑 상 장', W / 2, 165);

    ctx.fillStyle = '#92400E';
    ctx.font = '900 38px "Malgun Gothic", sans-serif';
    ctx.fillText(`부문: ${awardTitle}`, W / 2, 240);
    ctx.fillStyle = '#BE123C';
    ctx.font = 'bold 32px "Malgun Gothic", sans-serif';
    ctx.fillText(`헌정 꽃다발: ${bouquetName}`, W / 2, 295);

    const pImg = portraitCache[9] || portraitCache[1];
    if (pImg) {
      ctx.save();
      ctx.beginPath();
      ctx.arc(W / 2, 500, 165, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(pImg, W / 2 - 190, 320, 380, 480);
      ctx.restore();
      ctx.strokeStyle = '#D4AF37';
      ctx.lineWidth = 8;
      ctx.beginPath();
      ctx.arc(W / 2, 500, 165, 0, Math.PI * 2);
      ctx.stroke();
    }

    ctx.fillStyle = '#111827';
    ctx.font = 'bold 32px "Malgun Gothic", sans-serif';
    ctx.fillText('위 가수는 천상의 중저음 목소리로 전국 어머님들의', W / 2, 735);
    ctx.fillText('가슴에 깊은 위로와 기쁨을 선물하였기에,', W / 2, 785);
    ctx.fillText('온 마음을 담아 이 꽃다발과 황금 상장을 수여합니다.', W / 2, 835);

    ctx.fillStyle = '#0E2820';
    ctx.font = '900 40px "Malgun Gothic", sans-serif';
    ctx.fillText(`수여인 : 평생 당신 편 ${fanName} 올림`, W / 2, 925);

    ctx.fillStyle = '#6B7280';
    ctx.font = 'bold 24px "Malgun Gothic", sans-serif';
    ctx.fillText(`${getTodayKoreanDateStr()} · PARADISE-HERO.COM`, W / 2, 985);
  }

  // ===========================================================================
  // ITEM 9: 내 이름이 찍힌 황영웅 VIP 골든 콘서트 소장용 기념 티켓 (1080x560)
  // ===========================================================================
  function renderGoldenTicket() {
    const canvas = document.getElementById('gt-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 560;

    const nameEl = document.getElementById('gt-name');
    const cityEl = document.getElementById('gt-city');
    const seatEl = document.getElementById('gt-seat');

    const fanName = ((nameEl && nameEl.value) || '이순자 어머니').trim();
    const city = (cityEl && cityEl.value) || '서울 올림픽체조경기장 (KSPO DOME)';
    const seat = (seatEl && seatEl.value) || 'VIP 황금 R석 1열 1번 (영웅님 정면 명당)';

    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#B45309');
    grad.addColorStop(0.35, '#FDE047');
    grad.addColorStop(0.7, '#D97706');
    grad.addColorStop(1, '#78350F');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    ctx.fillStyle = '#0E2820';
    ctx.fillRect(28, 28, W - 56, H - 56);
    ctx.strokeStyle = '#FDE047';
    ctx.lineWidth = 6;
    ctx.strokeRect(40, 40, W - 80, H - 80);

    // Ticket Stub Divider Line
    ctx.setLineDash([14, 10]);
    ctx.strokeStyle = '#FDE047';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(760, 40);
    ctx.lineTo(760, H - 40);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#FDE047';
    ctx.font = '900 34px "Malgun Gothic", sans-serif';
    ctx.fillText('HWANG YOUNG WOONG GOLDEN VIP CONCERT TICKET', 70, 105);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 46px "Malgun Gothic", sans-serif';
    ctx.fillText(`초대석 성함 : ${fanName}`, 70, 195);

    ctx.fillStyle = '#A7F3D0';
    ctx.font = 'bold 30px "Malgun Gothic", sans-serif';
    ctx.fillText(`공연장 : ${city}`, 70, 270);
    ctx.fillStyle = '#FDE68A';
    ctx.fillText(`좌석 등급 : ${seat}`, 70, 330);
    ctx.fillStyle = '#E5E7EB';
    ctx.fillText(`발권 일자 : ${getTodayKoreanDateStr()}`, 70, 390);

    ctx.fillStyle = '#D4AF37';
    ctx.fillRect(70, 425, 640, 62);
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 28px "Malgun Gothic", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('평생 소장용 황금 VIP 기념 티켓 · PARADISE-HERO.COM', 390, 466);

    const pImg = portraitCache[6] || portraitCache[1];
    if (pImg) {
      ctx.save();
      ctx.beginPath();
      ctx.rect(790, 65, 230, 340);
      ctx.clip();
      ctx.drawImage(pImg, 710, 45, 380, 480);
      ctx.restore();
    }
    ctx.fillStyle = '#FDE047';
    ctx.font = '900 26px "Malgun Gothic", sans-serif';
    ctx.fillText('VIP ADMIT ONE', 905, 455);
  }

  // ===========================================================================
  // ITEM 10: 치매 예방 & 팬심 테스트 '황영웅 찐팬 골든벨 퀴즈' & 수료증 (1080x800)
  // ===========================================================================
  function renderFanQuizCert() {
    const canvas = document.getElementById('fq-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 800;

    const nameEl = document.getElementById('fq-name');
    const q1 = document.getElementById('fq-q1');
    const q2 = document.getElementById('fq-q2');
    const q3 = document.getElementById('fq-q3');

    const fanName = ((nameEl && nameEl.value) || '이순자 어머니').trim();
    let score = 0;
    if (!q1 || q1.value === 'correct') score += 34;
    if (!q2 || q2.value === 'correct') score += 33;
    if (!q3 || q3.value === 'correct') score += 33;

    ctx.fillStyle = '#0E2820';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#FFFDF5';
    ctx.fillRect(36, 36, W - 72, H - 72);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 14;
    ctx.strokeRect(48, 48, W - 96, H - 96);

    ctx.textAlign = 'center';
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 48px "Malgun Gothic", sans-serif';
    ctx.fillText('파라다이스 황영웅 팬심 골든벨 장원급제 증서', W / 2, 145);

    ctx.fillStyle = '#B91C1C';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    ctx.fillText(`성 함 : ${fanName}   |   점 수 : ${score}점 (1등급 찐팬)`, W / 2, 245);

    ctx.fillStyle = '#1F2937';
    ctx.font = 'bold 32px "Malgun Gothic", sans-serif';
    ctx.fillText('위 어머님께서는 가수 황영웅의 대표 명곡과 활동 역사를', W / 2, 345);
    ctx.fillText('완벽히 기억하시는 대한민국 상위 1% 명예 찐팬이시기에', W / 2, 405);
    ctx.fillText('파라다이스 골든벨 1등급 장원급제 수료증을 수여합니다!', W / 2, 465);

    ctx.fillStyle = '#0E2820';
    ctx.fillRect(220, 535, W - 440, 86);
    ctx.fillStyle = '#FDE047';
    ctx.font = '900 36px "Malgun Gothic", sans-serif';
    ctx.fillText('황영웅 팬덤 골든벨 위원회 공인 인증', W / 2, 590);

    ctx.fillStyle = '#4B5563';
    ctx.font = 'bold 26px "Malgun Gothic", sans-serif';
    ctx.fillText(`${getTodayKoreanDateStr()} · PARADISE-HERO.COM`, W / 2, 695);
  }

  function isKakaoInAppOrMobile() {
    const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    return /KAKAOTALK|NAVER|Instagram|FBAN|FBAV|Line|Android|iPhone|iPad|iPod/i.test(ua);
  }

  function openStudioLongPressSaveModal(dataUrl, itemLabel) {
    if (typeof document === 'undefined') return;
    if (typeof window !== 'undefined' && window.ParadiseKakaoBookmark && window.ParadiseKakaoBookmark.openLongPressPhotoSaveModal) {
      window.ParadiseKakaoBookmark.openLongPressPhotoSaveModal(dataUrl, `🎁 [${itemLabel || '황영웅 기념 선물'}] 완성!`);
      return;
    }

    let modal = document.getElementById('vip-kakao-longpress-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'vip-kakao-longpress-modal';
      modal.style.cssText = 'display:flex; position:fixed; inset:0; background:rgba(14,40,32,0.88); z-index:10050; align-items:center; justify-content:center; padding:18px; overflow-y:auto;';
      modal.innerHTML = `
        <div style="background:#FAFAF8; border:4px solid #D4AF37; border-radius:24px; max-width:580px; width:100%; padding:26px 20px; text-align:center;">
          <div id="vip-longpress-heading" style="font-size:26px; font-weight:900; color:#0E2820; margin-bottom:12px;">🎁 황영웅 기념 선물 완성!</div>
          <div style="background:#FFFBEB; border:3px solid #F59E0B; border-radius:16px; padding:18px; font-size:23px; font-weight:900; color:#92400E; line-height:1.55; margin-bottom:16px;">
            📱 손가락으로 그림을 <strong>2초간 꾹~ 눌러</strong><br>
            <strong style="color:#B91C1C; text-decoration:underline;">[사진 저장]</strong>을 누르세요!
          </div>
          <img id="vip-longpress-preview-img" src="" alt="길게 눌러 저장할 완성 선물" style="width:100%; max-width:380px; margin:0 auto 16px; border-radius:14px; border:4px solid #D4AF37;">
          <button type="button" id="btn-close-vip-longpress" class="btn btn-emerald btn-full" style="min-height:64px; font-size:22px; font-weight:900;">✅ 사진 저장 완료! (창 닫기)</button>
        </div>
      `;
      document.body.appendChild(modal);
      modal.addEventListener('click', (ev) => {
        if (ev.target === modal || ev.target.closest('#btn-close-vip-longpress')) {
          modal.style.display = 'none';
        }
      });
    }
    const hEl = modal.querySelector('#vip-longpress-heading');
    const imgEl = modal.querySelector('#vip-longpress-preview-img');
    if (hEl) hEl.textContent = `🎁 [${itemLabel || '황영웅 기념 선물'}] 완성!`;
    if (imgEl) imgEl.src = dataUrl;
    modal.style.display = 'flex';
  }

  function triggerDirectDownload(canvasId, filenamePrefix, itemLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    try {
      const dataUrl = canvas.toDataURL('image/png');
      const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
      const isKakaoTalk = /KAKAOTALK/i.test(ua);

      if (!isKakaoTalk) {
        const a = document.createElement('a');
        a.href = dataUrl;
        a.download = `${filenamePrefix}_${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }

      // 카카오톡 인앱 브라우저 및 모바일(또는 저장 완료 안내용)에서 왕글씨 2초 꾹 저장 모달 자동 호출
      if (isKakaoInAppOrMobile() || isKakaoTalk) {
        openStudioLongPressSaveModal(dataUrl, itemLabel || filenamePrefix);
      } else {
        openStudioLongPressSaveModal(dataUrl, itemLabel || filenamePrefix);
      }
    } catch (e) {
      alert('📱 완성된 그림을 2초간 꾹~ 눌러 [사진 저장]을 누르시면 내 사진첩에 바로 저장됩니다!');
    }
  }

  function downloadCanvasImage(canvasId, filenamePrefix, itemLabel) {
    if (!consumeStudioCredit(itemLabel || filenamePrefix)) return;
    triggerDirectDownload(canvasId, filenamePrefix, itemLabel);
  }

  function initVipDigitalStudio() {
    updateStudioCreditBadge();
    renderLiveLanternWall();

    const renderAll = () => {
      renderGreetingCard();
      renderFanIdCard();
      renderLockscreenWallpaper();
      generateVoiceLetterText();
      renderLyricGuide();
      renderFortuneTalisman();
      renderWishLantern();
      renderFlowerTribute();
      renderGoldenTicket();
      renderFanQuizCert();
    };

    preloadPortraits(renderAll);
    renderAll();

    const bindInputs = (ids, fn) => {
      ids.forEach((id) => {
        const el = document.getElementById(id);
        if (el) {
          el.addEventListener('input', fn);
          el.addEventListener('change', fn);
        }
      });
    };

    bindInputs(['gc-template', 'gc-look', 'gc-sender', 'gc-custom-msg', 'greeting-theme-select', 'greeting-portrait-select', 'greeting-sender-input', 'greeting-custom-msg'], renderGreetingCard);
    bindInputs(['fid-name', 'fid-region', 'fid-song', 'fid-look', 'fan-id-name', 'fan-id-region', 'fan-id-song', 'fan-id-portrait'], renderFanIdCard);
    bindInputs(['wp-look', 'wp-motto', 'wallpaper-portrait-select', 'wallpaper-motto-input'], renderLockscreenWallpaper);
    bindInputs(['vl-name', 'vl-occasion', 'vl-sender', 'voice-recipient-input', 'voice-occasion-select', 'voice-sender-input'], generateVoiceLetterText);
    bindInputs(['lb-song-select', 'lyric-song-select'], renderLyricGuide);
    bindInputs(['ft-name', 'ft-birth-year', 'ft-wish-type'], renderFortuneTalisman);
    bindInputs(['wl-name', 'wl-wish', 'wl-color'], renderWishLantern);
    bindInputs(['fl-name', 'fl-award-title', 'fl-bouquet'], renderFlowerTribute);
    bindInputs(['gt-name', 'gt-city', 'gt-seat'], renderGoldenTicket);
    bindInputs(['fq-name', 'fq-q1', 'fq-q2', 'fq-q3'], renderFanQuizCert);
  }

  const publicApi = {
    downloadGreetingCard: () => downloadCanvasImage('gc-canvas', '황영웅_카톡안부카드', '카톡 아침 안부카드'),
    downloadFanIdCard: () => downloadCanvasImage('fid-canvas', '파라다이스_황금명예팬증', '황금 명예 팬증 발급'),
    downloadWallpaper: () => downloadCanvasImage('wp-canvas', '황영웅_큰글씨달력_배경화면', '큰글씨 달력 잠금화면'),
    playVoiceLetterAloud,
    printLyricGuide: () => {
      if (!consumeStudioCredit('왕글씨 노래교실 비법서')) return;
      window.print();
    },
    downloadFortuneTalisman: () => downloadCanvasImage('ft-canvas', '황영웅_황금행운부적', '황영웅 행운 부적 뽑기'),
    downloadWishLantern: lightUpWishLanternAndDownload,
    downloadFlowerTribute: () => downloadCanvasImage('fl-canvas', '황영웅_황금꽃다발_사랑상장', '황금 꽃다발 & 상장 수여'),
    downloadGoldenTicket: () => downloadCanvasImage('gt-canvas', '황영웅_VIP콘서트_골든티켓', 'VIP 골든 콘서트 티켓'),
    downloadFanQuizCert: () => downloadCanvasImage('fq-canvas', '황영웅_찐팬골든벨_장원급제증서', '황영웅 팬심 골든벨 퀴즈'),
    openStudioPaywall: openStudioPaywallModal,
    closeStudioPaywall: closeStudioPaywallModal,
    redeemStudioToken
  };

  if (typeof window !== 'undefined') {
    window.VIPDigitalStudio = publicApi;
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initVipDigitalStudio);
    } else {
      initVipDigitalStudio();
    }
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = Object.assign(
      {
        HWANG_PORTRAITS,
        GREETING_TEMPLATES,
        SONG_GUIDES,
        getStudioState,
        isKakaoInAppOrMobile
      },
      publicApi
    );
  }
})(typeof window !== 'undefined' ? window : globalThis);
