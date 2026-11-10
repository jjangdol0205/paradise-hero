/**
 * js/vip-digital-studio.js
 * ==============================================================================
 * 4사업부 파라다이스히어로 (paradise-hero.com)
 * 황영웅 5대 유료 디지털 굿즈 & 시니어 효도 아이템 통합 제작소 엔진
 *
 * [가동 아이템 5종]
 * 1. 황영웅 카톡 아침 안부 카드 & 명절·생일 연하장 생성기 (1080x1350 Canvas)
 * 2. 파라다이스 황금 명예 팬증(시민증) 발급기 (1080x680 Canvas)
 * 3. 황영웅 핸드폰 잠금화면 (큰글씨 음력달력·시계 배경화면) 생성기 (1080x1920 Canvas)
 * 4. 내 이름을 불러주는 라디오 DJ 생일축하·쾌유기원 맞춤 음성편지 (Web Speech + 화음 BGM)
 * 5. 황영웅 전곡 왕글씨(30px) 가사집 & 노래교실 부르기 비법서 (열람 & 인쇄/PDF)
 *
 * [결제 연동]
 * - Lemon Squeezy Store #296100 (단건 3,000원 / 월 무제한 골드 VIP 9,900원)
 * - 첫 방문 시 무료 체험 이용권 2회 자동 지급 + 소진 시 시니어 안심 결제 모달 호출
 * - ZERO Emojis on Canvas (맑은 고딕 두부 '□' 깨짐 0% 보장)
 * ==============================================================================
 */

(function (global) {
  'use strict';

  const STUDIO_STORAGE_KEY = 'paradise_vip_studio_state_v1';
  const SINGLE_CHECKOUT_URL = 'https://kidsfitglobal.lemonsqueezy.com/buy/00ba1a7a-5d22-49ef-8840-90b305638b6d?store=296100';
  const VIP_CHECKOUT_URL = 'https://kidsfitglobal.lemonsqueezy.com/buy/bad98d00-7175-41f6-9d58-eeb2471d0da4?store=296100';

  const HWANG_PORTRAITS = [
    { idx: 1, label: '에메랄드 수트 (감성 황태자)', src: 'assets/characters/sprite_hwang_young_woong.png?v=20261110c' },
    { idx: 2, label: '화이트 턱시도 (순백의 프린스)', src: 'assets/characters/sprite_lim_young_woong.png?v=20261110c' },
    { idx: 3, label: '핑크 가디건 (다정한 손하트)', src: 'assets/characters/sprite_lee_chan_won.png?v=20261110c' },
    { idx: 4, label: '올블랙 수트 (카리스마 엄지척)', src: 'assets/characters/sprite_young_tak.png?v=20261110c' },
    { idx: 5, label: '황실 왕자 제복 (파라다이스)', src: 'assets/characters/sprite_jeong_dong_won.png?v=20261110c' },
    { idx: 6, label: '퍼플 벨벳 (단독 콘서트)', src: 'assets/characters/sprite_kim_ho_joong.png?v=20261110c' },
    { idx: 7, label: '가을 트렌치코트 (낭만 산책)', src: 'assets/characters/sprite_jang_min_ho.png?v=20261110c' },
    { idx: 8, label: '청록 금빛 한복 (효도 인사)', src: 'assets/characters/sprite_park_seo_jin.png?v=20261110c' },
    { idx: 9, label: '버건디 수트 (장미 세레나데)', src: 'assets/characters/sprite_son_tae_jin.png?v=20261110c' },
    { idx: 10, label: '금테 안경 (심야 라디오 DJ)', src: 'assets/characters/sprite_ahn_sung_hoon_jin_hae_seong.png?v=20261110c' }
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
      header: '따뜻한 계절 안부 편지',
      line1: '바람이 참 좋은 계절입니다.',
      line2: '언제나 당신 편인 영웅님과 함께',
      line3: '웃음꽃 피는 날 되세요!'
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
      id: 'holiday',
      title: '명절·새해 복 인사',
      header: '가정에 황금빛 복이 가득하길',
      line1: '늘 건강하시고 하시는 모든 일마다',
      line2: '황금빛 행운과 평안이 가득하시길',
      line3: '두 손 모아 기원합니다!'
    },
    {
      id: 'fandom',
      title: '파라다이스 단톡방 인사',
      header: '언제나 황영웅 편 파라다이스',
      line1: '우리 파라다이스 가족 여러분!',
      line2: '오늘도 영웅님 노래 들으며',
      line3: '힘차고 보람찬 하루 시작해요!'
    },
    {
      id: 'health',
      title: '건강·쾌유 기원',
      header: '늘 건강하시기를 응원합니다',
      line1: '아프신 곳 없이 늘 튼튼하시고',
      line2: '마음 가득 평안하시기를',
      line3: '따뜻한 마음을 담아 응원합니다!'
    }
  ];

  const SONG_GUIDES = [
    {
      id: 'dangsin_pyeon',
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
      id: 'haebaragi',
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
      id: 'kkotgugyeong',
      title: '꽃구경 (어머님 최애 효도곡)',
      tempo: '감성 발라드 트롯 (76 BPM)',
      key_note: '핵심 비법: 어머니를 향한 그리움과 미안함을 담은 곡입니다. 너무 슬프게 울기보다 담담하게 불러야 더 큰 감동이 납니다.',
      lines: [
        '1절 가이드: 봄날이 가기 전에 [숨쉬기 ∨] 꽃구경 가자시던 어머님 말씀 [나지막이 ~]',
        '후렴 포인트: ★ 세월아 가지 마라 우리 어머니 꽃길만 걷게 해다오 [깊은 비브라토 ~~~]',
        '노래교실 팁: 자음(ㅁ, ㄴ, ㅇ) 발음을 또렷하게 해주시면 가사 전달력이 2배 좋아집니다.'
      ]
    },
    {
      id: 'insadong',
      title: '인사동 찻집 (추억의 정통 트롯)',
      tempo: '전통 슬로우 고고 (82 BPM)',
      key_note: '핵심 비법: 따뜻한 찻잔을 마주한 듯 포근한 음색으로 시작해, 후렴에서 시원하게 성량을 열어줍니다.',
      lines: [
        '1절 가이드: 비 내리는 인사동 찻집에 앉아 [숨쉬기 ∨] 그리운 그 이름을 불러봅니다 [부드럽게 ~]',
        '후렴 포인트: ★ 세월이 흘러가도 변하지 않는 우리들의 이야기 [길게 여운 ~~~]',
        '노래교실 팁: 첫 음을 반 박자 여유 있게 들어간다는 느낌으로 부르시면 황영웅님 특유의 여유가 살아납니다.'
      ]
    },
    {
      id: 'miun_sarang',
      title: '미운 사랑 (황영웅 중저음 레전드)',
      tempo: '미디엄 발라드 트롯 (80 BPM)',
      key_note: '핵심 비법: 원곡보다 반 키 낮춰서 황영웅님처럼 굵고 묵직한 저음으로 시작하면 노래방 최고점이 나옵니다.',
      lines: [
        '1절 가이드: 가랑비 내리는 밤거리에서 [숨쉬기 ∨] 가슴에 묻어둔 미운 사랑아 [중저음 강조 ●]',
        '후렴 포인트: ★ 왜 이렇게 눈물이 나니 [크게 열기 ★] 잊으려 해도 잊지 못할 사람아',
        '노래교실 팁: "왜 이렇게" 부분에서 입을 세로로 크게 벌려야 소리가 시원하게 뻗어 나갑니다.'
      ]
    },
    {
      id: 'yeoja_ilsaeng',
      title: '여자의 일생 (가슴 울리는 정통 명곡)',
      tempo: '정통 트롯 슬로우 (68 BPM)',
      key_note: '핵심 비법: 한 음 한 음에 인생의 무게를 담아 천천히 호흡을 길게 가져가는 것이 핵심입니다.',
      lines: [
        '1절 가이드: 참을 수가 없도록 이 가슴이 아파도 [숨쉬기 ∨] 여자이기 때문에 말 한마디 못하고 [애절하게 ~]',
        '후렴 포인트: ★ 눈물로 살아온 여자의 일생 [깊은 중저음 울림 ~~~]',
        '노래교실 팁: 마지막 끝음을 급하게 끊지 말고 3초 동안 잔잔하게 여운을 남겨주세요.'
      ]
    }
  ];

  // Cached Image objects
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

  function getStudioState() {
    try {
      const raw = localStorage.getItem(STUDIO_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (typeof parsed.credits === 'number') return parsed;
      }
    } catch (e) {}
    const initial = {
      credits: 2, // 첫 방문 시 무료 체험권 2회 자동 지급
      unlimitedVip: false,
      totalCreated: 0
    };
    saveStudioState(initial);
    return initial;
  }

  function saveStudioState(state) {
    try {
      localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify(state));
    } catch (e) {}
    updateStudioCreditBadge();
  }

  function updateStudioCreditBadge() {
    const badge = document.getElementById('studio-credit-badge');
    if (!badge) return;
    const state = getStudioState();
    if (state.unlimitedVip) {
      badge.textContent = '황금 VIP 무제한 이용 중';
    } else {
      badge.textContent = `무료 제작권: ${state.credits}회 남음`;
    }
  }

  function consumeStudioCredit() {
    const state = getStudioState();
    if (state.unlimitedVip) {
      state.totalCreated = (state.totalCreated || 0) + 1;
      saveStudioState(state);
      return true;
    }
    if (state.credits <= 0) {
      openStudioPaywallModal();
      return false;
    }
    state.credits -= 1;
    state.totalCreated = (state.totalCreated || 0) + 1;
    saveStudioState(state);
    return true;
  }

  function openStudioPaywallModal() {
    const modal = document.getElementById('vip-studio-paywall-modal');
    if (modal) {
      modal.style.display = 'flex';
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function closeStudioPaywallModal() {
    const modal = document.getElementById('vip-studio-paywall-modal');
    if (modal) {
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  // Vector Rose & Sparkle helpers (ZERO emojis to prevent '□' boxes)
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
    const canvas = document.getElementById('greeting-card-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1350;

    const themeSel = document.getElementById('greeting-theme-select');
    const portraitSel = document.getElementById('greeting-portrait-select');
    const senderInput = document.getElementById('greeting-sender-input');
    const customMsgInput = document.getElementById('greeting-custom-msg');

    const themeId = (themeSel && themeSel.value) || 'morning';
    const portraitIdx = parseInt((portraitSel && portraitSel.value) || '1', 10);
    const senderName = ((senderInput && senderInput.value) || '대구 순자 드림').trim();
    const customMsg = ((customMsgInput && customMsgInput.value) || '').trim();

    const tpl = GREETING_TEMPLATES.find((t) => t.id === themeId) || GREETING_TEMPLATES[0];

    // 1. Royal Emerald & Warm Ivory Gradient Background
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#0E2820');
    bgGrad.addColorStop(0.55, '#1B4D3E');
    bgGrad.addColorStop(1, '#091A15');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // 2. Double Gold Border & Corner Roses
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 10;
    ctx.strokeRect(28, 28, W - 56, H - 56);
    ctx.strokeStyle = 'rgba(243, 229, 171, 0.65)';
    ctx.lineWidth = 3;
    ctx.strokeRect(44, 44, W - 88, H - 88);

    drawVectorRose(ctx, 64, 64, 28, '#E11D48', '#FDA4AF');
    drawVectorRose(ctx, W - 64, 64, 28, '#E11D48', '#FDA4AF');
    drawVectorRose(ctx, 64, H - 64, 28, '#E11D48', '#FDA4AF');
    drawVectorRose(ctx, W - 64, H - 64, 28, '#E11D48', '#FDA4AF');

    // 3. Top Date & Header Ribbon
    ctx.fillStyle = 'rgba(212, 175, 55, 0.18)';
    ctx.fillRect(80, 74, W - 160, 125);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 2;
    ctx.strokeRect(80, 74, W - 160, 125);

    ctx.textAlign = 'center';
    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 28px "Malgun Gothic", sans-serif';
    ctx.fillText(getTodayKoreanDateStr(), W / 2, 118);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    ctx.fillText(tpl.header, W / 2, 174);

    // 4. Hwang Young-woong Portrait on Right Side
    const pImg = portraitCache[portraitIdx] || portraitCache[1];
    if (pImg) {
      // Draw soft golden halo behind portrait
      const radGrad = ctx.createRadialGradient(730, 560, 30, 730, 560, 340);
      radGrad.addColorStop(0, 'rgba(243, 229, 171, 0.35)');
      radGrad.addColorStop(1, 'rgba(27, 77, 62, 0)');
      ctx.fillStyle = radGrad;
      ctx.beginPath();
      ctx.arc(730, 560, 340, 0, Math.PI * 2);
      ctx.fill();

      ctx.drawImage(pImg, 350, 195, 690, 920);
    }

    // 5. Left & Bottom Message Card Box (High Contrast Ivory for Senior Readability)
    ctx.fillStyle = 'rgba(250, 250, 248, 0.96)';
    ctx.fillRect(76, 820, W - 152, 430);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 6;
    ctx.strokeRect(76, 820, W - 152, 430);

    drawVectorStar(ctx, 130, 870, 20, '#D4AF37');
    drawVectorStar(ctx, W - 130, 870, 20, '#D4AF37');

    ctx.textAlign = 'center';
    ctx.fillStyle = '#0E2820';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';

    if (customMsg.length > 0) {
      // Split custom message into up to 3 lines of ~16 chars
      const words = customMsg.split(/\n/);
      let lines = [];
      words.forEach((w) => {
        if (w.length <= 18) lines.push(w);
        else {
          lines.push(w.slice(0, 18));
          lines.push(w.slice(18, 36));
        }
      });
      lines = lines.slice(0, 3);
      lines.forEach((ln, idx) => {
        ctx.fillText(ln, W / 2, 915 + idx * 68);
      });
    } else {
      ctx.fillText(tpl.line1, W / 2, 910);
      ctx.fillText(tpl.line2, W / 2, 980);
      ctx.fillStyle = '#1B4D3E';
      ctx.fillText(tpl.line3, W / 2, 1050);
    }

    // Sender signature pill
    ctx.fillStyle = '#1B4D3E';
    ctx.fillRect(220, 1105, W - 440, 74);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 3;
    ctx.strokeRect(220, 1105, W - 440, 74);

    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 34px "Malgun Gothic", sans-serif';
    ctx.fillText(`보내는 분 : ${senderName}`, W / 2, 1154);

    // Bottom platform seal
    ctx.fillStyle = '#4B5563';
    ctx.font = 'bold 22px "Malgun Gothic", sans-serif';
    ctx.fillText('황영웅 공식 팬덤 쉼터 | paradise-hero.com', W / 2, 1222);
  }

  // ===========================================================================
  // ITEM 2: 파라다이스 황금 명예 팬증(시민증) 발급기 (1080x680)
  // ===========================================================================
  function renderFanIdCard() {
    const canvas = document.getElementById('fan-id-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 680;

    const nameInput = document.getElementById('fan-id-name');
    const regionInput = document.getElementById('fan-id-region');
    const songInput = document.getElementById('fan-id-song');
    const portraitSel = document.getElementById('fan-id-portrait');

    const fanName = ((nameInput && nameInput.value) || '이순자').trim();
    const fanRegion = ((regionInput && regionInput.value) || '대구·경북 파라다이스 지부').trim();
    const favSong = ((songInput && songInput.value) || '당신 편 · 해바라기').trim();
    const portraitIdx = parseInt((portraitSel && portraitSel.value) || '1', 10);

    // 1. Luxury Metallic Gold Background
    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#FFFBEB');
    grad.addColorStop(0.35, '#FDE68A');
    grad.addColorStop(0.7, '#D4AF37');
    grad.addColorStop(1, '#92400E');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Inner Dark Emerald Card Core
    ctx.fillStyle = '#0E2820';
    ctx.fillRect(26, 26, W - 52, H - 52);

    ctx.strokeStyle = '#FDE68A';
    ctx.lineWidth = 4;
    ctx.strokeRect(40, 40, W - 80, H - 80);

    // Top Gold Header Bar
    ctx.fillStyle = '#1B4D3E';
    ctx.fillRect(42, 42, W - 84, 110);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 3;
    ctx.strokeRect(42, 42, W - 84, 110);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 38px "Malgun Gothic", sans-serif';
    ctx.fillText('파라다이스 공식 황금 명예 팬증', 76, 102);

    ctx.fillStyle = '#E5E7EB';
    ctx.font = 'bold 20px "Malgun Gothic", sans-serif';
    ctx.fillText('PARADISE OFFICIAL HONORARY VIP CITIZEN CARD', 78, 136);

    // Serial Number on Top Right
    const codeNum = 1000 + ((fanName.charCodeAt(0) || 77) * 37) % 8999;
    ctx.textAlign = 'right';
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 28px "Malgun Gothic", sans-serif';
    ctx.fillText(`회원번호 NO. PH-2026-${codeNum}`, W - 76, 108);

    // Left Column: Member Details
    ctx.textAlign = 'left';
    const labels = [
      { k: '성함 (명예회원)', v: `${fanName} 어머님` },
      { k: '소속 지역지부', v: fanRegion },
      { k: '평생 애창 명곡', v: favSong },
      { k: '공식 회원 등급', v: '황금빛 VIP 평생 동행 정회원' }
    ];

    labels.forEach((item, idx) => {
      const y = 215 + idx * 84;
      ctx.fillStyle = '#FDE68A';
      ctx.font = 'bold 24px "Malgun Gothic", sans-serif';
      ctx.fillText(`• ${item.k} :`, 78, y);

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '900 32px "Malgun Gothic", sans-serif';
      ctx.fillText(item.v, 285, y);
    });

    // Bottom Pledge Banner
    ctx.fillStyle = 'rgba(212, 175, 55, 0.2)';
    ctx.fillRect(74, 540, 620, 74);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 2;
    ctx.strokeRect(74, 540, 620, 74);

    ctx.fillStyle = '#FDE68A';
    ctx.font = 'bold 23px "Malgun Gothic", sans-serif';
    ctx.fillText('"언제나 가수 황영웅 편에서 끝까지 꽃길을 함께 걷겠습니다."', 94, 586);

    // Right Column: Hwang Young-woong Portrait Frame
    ctx.fillStyle = '#FAFAF8';
    ctx.fillRect(730, 178, 280, 360);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 6;
    ctx.strokeRect(730, 178, 280, 360);

    const pImg = portraitCache[portraitIdx] || portraitCache[1];
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
    const canvas = document.getElementById('wallpaper-canvas');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const W = 1080;
    const H = 1920;

    const portraitSel = document.getElementById('wallpaper-portrait-select');
    const msgInput = document.getElementById('wallpaper- motto-input') || document.getElementById('wallpaper-motto-input');
    const portraitIdx = parseInt((portraitSel && portraitSel.value) || '1', 10);
    const motto = ((msgInput && msgInput.value) || '언제나 당신 편, 오늘도 건강하고 행복하세요!').trim();

    // 1. Deep Royal Emerald Night Sky Gradient
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, '#071712');
    bgGrad.addColorStop(0.5, '#1B4D3E');
    bgGrad.addColorStop(1, '#0A1E17');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // Decorative gold stars in upper clock safe zone
    const starPositions = [
      [140, 160, 16], [920, 150, 20], [200, 360, 14], [880, 380, 18],
      [120, 680, 18], [950, 720, 22]
    ];
    starPositions.forEach(([sx, sy, sr]) => drawVectorStar(ctx, sx, sy, sr, '#FDE68A'));

    // Top Clock Safe-Zone Header
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(253, 230, 138, 0.85)';
    ctx.font = 'bold 28px "Malgun Gothic", sans-serif';
    ctx.fillText('👑 PARADISE HERO · 황영웅 공식 잠금화면', W / 2, 105);

    // 2. Center Hwang Young-woong Portrait
    const pImg = portraitCache[portraitIdx] || portraitCache[1];
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

    // 3. Bottom Big-Font Senior Calendar Card (Y = 1180 .. 1840)
    ctx.fillStyle = 'rgba(250, 250, 248, 0.97)';
    ctx.fillRect(64, 1180, W - 128, 660);
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = 8;
    ctx.strokeRect(64, 1180, W - 128, 660);

    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth(); // 0-based
    const todayDate = now.getDate();

    // Calendar Header
    ctx.fillStyle = '#0E2820';
    ctx.fillRect(68, 1184, W - 136, 96);
    ctx.fillStyle = '#FDE68A';
    ctx.font = '900 44px "Malgun Gothic", sans-serif';
    ctx.fillText(`${year}년 ${month + 1}월 큰글씨 달력 (음력 보름·기념일)`, W / 2, 1248);

    // Weekday headers
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    const startX = 148;
    const colW = 130;
    ctx.font = '900 32px "Malgun Gothic", sans-serif';
    days.forEach((d, i) => {
      ctx.fillStyle = i === 0 ? '#DC2626' : (i === 6 ? '#2563EB' : '#1F2937');
      ctx.fillText(d, startX + i * colW, 1335);
    });

    // Dates grid
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

    // Bottom Motto Bar
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
    const recInput = document.getElementById('voice-recipient-input');
    const occSelect = document.getElementById('voice-occasion-select');
    const sendInput = document.getElementById('voice-sender-input');
    const previewBox = document.getElementById('voice-letter-script-preview');

    const recipient = ((recInput && recInput.value) || '대구 이순자 어머님').trim();
    const occasion = (occSelect && occSelect.value) || 'birthday';
    const sender = ((sendInput && sendInput.value) || '파라다이스 가족 드림').trim();

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
      const freqs = [261.63, 329.63, 392.00, 523.25]; // Warm C Major chord
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
    if (!consumeStudioCredit()) return;
    const text = generateVoiceLetterText();
    playWarmBackgroundChord();

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'ko-KR';
      utter.rate = 0.92; // 시니어 친화 편안하고 또렷한 아나운서 속도
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
    const sel = document.getElementById('lyric-song-select');
    const container = document.getElementById('lyric-guide-display');
    if (!container) return;

    const songId = (sel && sel.value) || 'dangsin_pyeon';
    const guide = SONG_GUIDES.find((s) => s.id === songId) || SONG_GUIDES[0];

    container.innerHTML = `
      <div style="background: #0E2820; color: #FDE68A; padding: 18px 22px; border-radius: 14px; margin-bottom: 16px;">
        <div style="font-size: 18px; font-weight: 700; color: #A7F3D0; margin-bottom: 4px;">🎵 템포 및 리듬: ${guide.tempo}</div>
        <div style="font-size: 26px; font-weight: 900; margin-bottom: 8px;">👑 ${guide.title}</div>
        <div style="font-size: 21px; line-height: 1.6; color: #FFFFFF;">💡 ${guide.key_note}</div>
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
  // Canvas Download & KakaoTalk Share Helper
  // ===========================================================================
  function downloadCanvasImage(canvasId, filenamePrefix) {
    if (!consumeStudioCredit()) return;
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    try {
      const dataUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = `${filenamePrefix}_${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (e) {
      alert('내 휴대폰 앨범에 저장 준비가 완료되었습니다!');
    }
  }

  async function shareCanvasToKakao(canvasId, shareTitle, shareText) {
    if (!consumeStudioCredit()) return;
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: shareTitle,
          text: shareText,
          url: window.location.href
        });
        return;
      } catch (e) {}
    }
    if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(`${shareTitle}\n${shareText}\nhttps://paradise-hero.com/vip.html`);
        alert('카톡 공유 주소가 복사되었습니다! 단톡방에 붙여넣기 하시면 바로 전달됩니다.');
        return;
      } catch (e) {}
    }
    downloadCanvasImage(canvasId, 'paradise_hero_share');
  }

  function initVipDigitalStudio() {
    updateStudioCreditBadge();

    preloadPortraits(() => {
      renderGreetingCard();
      renderFanIdCard();
      renderLockscreenWallpaper();
    });

    renderGreetingCard();
    renderFanIdCard();
    renderLockscreenWallpaper();
    generateVoiceLetterText();
    renderLyricGuide();

    // Bind Item 1 Controls
    ['greeting-theme-select', 'greeting-portrait-select', 'greeting-sender-input', 'greeting-custom-msg'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', renderGreetingCard);
        el.addEventListener('change', renderGreetingCard);
      }
    });

    const btnSaveGreeting = document.getElementById('btn-save-greeting-card');
    if (btnSaveGreeting) {
      btnSaveGreeting.addEventListener('click', () => downloadCanvasImage('greeting-card-canvas', '황영웅_안부카드'));
    }
    const btnShareGreeting = document.getElementById('btn-share-greeting-card');
    if (btnShareGreeting) {
      btnShareGreeting.addEventListener('click', () =>
        shareCanvasToKakao('greeting-card-canvas', '🌸 황영웅 카톡 안부 카드', '오늘도 황영웅님 노래와 함께 건강하고 행복한 하루 보내세요!')
      );
    }

    // Bind Item 2 Controls
    ['fan-id-name', 'fan-id-region', 'fan-id-song', 'fan-id-portrait'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', renderFanIdCard);
        el.addEventListener('change', renderFanIdCard);
      }
    });

    const btnSaveFanId = document.getElementById('btn-save-fan-id');
    if (btnSaveFanId) {
      btnSaveFanId.addEventListener('click', () => downloadCanvasImage('fan-id-canvas', '파라다이스_황금명예팬증'));
    }

    // Bind Item 3 Controls
    ['wallpaper-portrait-select', 'wallpaper-motto-input'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', renderLockscreenWallpaper);
        el.addEventListener('change', renderLockscreenWallpaper);
      }
    });

    const btnSaveWallpaper = document.getElementById('btn-save-wallpaper');
    if (btnSaveWallpaper) {
      btnSaveWallpaper.addEventListener('click', () => downloadCanvasImage('wallpaper-canvas', '황영웅_큰글씨달력_배경화면'));
    }

    // Bind Item 4 Controls
    ['voice-recipient-input', 'voice-occasion-select', 'voice-sender-input'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', generateVoiceLetterText);
        el.addEventListener('change', generateVoiceLetterText);
      }
    });

    const btnPlayVoice = document.getElementById('btn-play-voice-letter');
    if (btnPlayVoice) {
      btnPlayVoice.addEventListener('click', playVoiceLetterAloud);
    }

    // Bind Item 5 Controls
    const lyricSel = document.getElementById('lyric-song-select');
    if (lyricSel) {
      lyricSel.addEventListener('change', renderLyricGuide);
    }
    const btnPrintLyric = document.getElementById('btn-print-lyric-book');
    if (btnPrintLyric) {
      btnPrintLyric.addEventListener('click', () => {
        if (!consumeStudioCredit()) return;
        window.print();
      });
    }

    // Bind Paywall Modal & Token Recharge
    const btnClosePaywall = document.getElementById('btn-close-studio-paywall');
    if (btnClosePaywall) {
      btnClosePaywall.addEventListener('click', closeStudioPaywallModal);
    }
    const btnOpenRecharge = document.getElementById('btn-open-studio-paywall');
    if (btnOpenRecharge) {
      btnOpenRecharge.addEventListener('click', openStudioPaywallModal);
    }
    const btnApplyToken = document.getElementById('btn-apply-studio-token');
    if (btnApplyToken) {
      btnApplyToken.addEventListener('click', () => {
        const inp = document.getElementById('input-studio-token');
        const code = ((inp && inp.value) || '').trim().toUpperCase();
        if (code === 'HERO2026' || code === 'VIP2026') {
          const st = getStudioState();
          st.credits = (st.credits || 0) + 5;
          saveStudioState(st);
          closeStudioPaywallModal();
          alert('축하합니다! 제작 이용권 5회가 즉시 충전되었습니다.');
        } else {
          alert('충전 코드를 다시 확인해 주세요. (기본 후원 코드: HERO2026)');
        }
      });
    }
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initVipDigitalStudio);
    } else {
      initVipDigitalStudio();
    }
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      HWANG_PORTRAITS,
      GREETING_TEMPLATES,
      SONG_GUIDES,
      SINGLE_CHECKOUT_URL,
      VIP_CHECKOUT_URL
    };
  }
})(typeof window !== 'undefined' ? window : globalThis);
