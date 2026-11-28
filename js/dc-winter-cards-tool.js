(function () {
  'use strict';

  function buildCleanShareUrl(rawUrl, extraParams) {
    var base = String(rawUrl || (window.location.origin + window.location.pathname));
    var u = new URL(base);
    ['internal_check', 'owner_device', 'internal_test', 'smoke_test', 'nocache'].forEach(function (k) {
      u.searchParams.delete(k);
    });
    if (extraParams && typeof extraParams === 'object') {
      Object.keys(extraParams).forEach(function (k) {
        if (extraParams[k] !== undefined && extraParams[k] !== null && extraParams[k] !== '') {
          u.searchParams.set(k, String(extraParams[k]));
        }
      });
    }
    var vid = '';
    try {
      if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.getOrCreateVisitorProfile === 'function') {
        vid = window.DreamCompanyCRM.getOrCreateVisitorProfile().visitor_id || '';
      } else {
        vid = localStorage.getItem('dc_visitor_id') || '';
        if (!vid) {
          vid = 'v_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
          localStorage.setItem('dc_visitor_id', vid);
        }
      }
    } catch (_) {}
    if (vid) u.searchParams.set('ref', vid);
    if (!u.searchParams.get('utm_source')) u.searchParams.set('utm_source', 'referral');
    if (!u.searchParams.get('utm_medium')) u.searchParams.set('utm_medium', 'share');
    return u.toString();
  }
  window.__dcBuildCleanShareUrl = buildCleanShareUrl;

  function triggerOneTouchShare(div, title, text, shareUrl, toastEl, copiedMsg) {
    var cleanUrl = buildCleanShareUrl(shareUrl);
    if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.trackFunnelEvent === 'function') {
      window.DreamCompanyCRM.trackFunnelEvent(div, 'share_click', { event_meta: 'seasonal_share_card' });
    }
    function showToast(msg) {
      if (!toastEl) return;
      toastEl.textContent = msg;
      toastEl.style.display = 'block';
    }
    if (navigator.share) {
      navigator.share({ title: title, text: text, url: cleanUrl }).then(function () {
        showToast(copiedMsg);
      }).catch(function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(cleanUrl).then(function () { showToast(copiedMsg); }).catch(function () { showToast(cleanUrl); });
        } else {
          showToast(cleanUrl);
        }
      });
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(cleanUrl).then(function () { showToast(copiedMsg); }).catch(function () { showToast(cleanUrl); });
    } else {
      showToast(cleanUrl);
    }
    return cleanUrl;
  }

  var PRESETS = {
    cold: {
      badge: '12월 한파 안부',
      title: '찬 바람 부는 겨울 아침, 따뜻하게 입으세요',
      msg: '날씨가 부쩍 차가워졌습니다. 외출하실 때 목도리 꼭 두르시고, 오늘도 따뜻한 차 한 잔과 함께 평안한 하루 보내시길 바랍니다.',
      bg1: '#0E2820', bg2: '#1E4638', accent: '#FDE68A',
      song: '/assets/audio/baek_woonho_01_mothers_spring.mp3',
      songTitle: '백운호 — 어머니의 봄날'
    },
    dongji: {
      badge: '12월 22일 동지(冬至)',
      title: '동지 팥죽 한 그릇에 액운은 멀리, 복은 가까이',
      msg: '일 년 중 밤이 가장 긴 동짓날입니다. 따뜻한 팥죽 맛있게 드시고, 다가오는 새해에는 온 가족 모두 건강과 웃음만 가득하시길 기원합니다.',
      bg1: '#4A1822', bg2: '#7C2D36', accent: '#FDE68A',
      song: '/assets/audio/baek_woonho_04_camellia.mp3',
      songTitle: '백운호 — 다시 피는 동백꽃'
    },
    christmas: {
      badge: '성탄절 평안 인사',
      title: '사랑과 온기가 가득한 성탄절 되세요',
      msg: '올 한 해도 참 수고 많으셨습니다. 눈꽃처럼 포근한 성탄 연휴, 소중한 가족과 함께 웃음꽃 피우는 따뜻한 시간 보내세요.',
      bg1: '#143628', bg2: '#235340', accent: '#FCD34D',
      song: '/assets/audio/baek_woonho_02_yeonga.mp3',
      songTitle: '백운호 — 백운호 연가'
    },
    yearend: {
      badge: '연말 감사 인사',
      title: '올 한 해 함께해 주셔서 진심으로 고맙습니다',
      msg: '지나온 2026년, 곁에서 힘이 되어 주신 덕분에 참 든든했습니다. 남은 연말 편안히 마무리하시고 늘 강녕하시길 두 손 모아 빕니다.',
      bg1: '#1E293B', bg2: '#334155', accent: '#FDE68A',
      song: '/assets/audio/baek_woonho_03_harbor_light.mp3',
      songTitle: '백운호 — 항구의 등불'
    },
    newyear2027: {
      badge: '2027년 정미년(丁未年) 새해',
      title: '2027년 정미년 새해 복 많이 받으세요',
      msg: '밝아오는 2027년 정미년 새해에는 아픈 곳 없이 늘 건강한 발걸음으로, 매일 아침 좋은 노래와 함께 행복한 날들만 가득하시길 기원합니다.',
      bg1: '#3B1E12', bg2: '#7C2D12', accent: '#FDE68A',
      song: '/assets/audio/baek_woonho_06_golden_sunset.mp3',
      songTitle: '백운호 — 내 인생의 금빛 노을'
    }
  };

  var currentKey = 'dongji';

  function wrapLines(ctx, text, maxW) {
    var words = String(text || '').split(' ');
    var lines = [];
    var cur = '';
    for (var i = 0; i < words.length; i++) {
      var test = cur ? (cur + ' ' + words[i]) : words[i];
      if (ctx.measureText(test).width > maxW && cur) {
        lines.push(cur);
        cur = words[i];
      } else {
        cur = test;
      }
    }
    if (cur) lines.push(cur);
    return lines;
  }

  function renderCard() {
    var p = PRESETS[currentKey] || PRESETS.dongji;
    var canvas = document.getElementById('heroWinterCanvas');
    if (!canvas || !canvas.getContext) return;
    var ctx = canvas.getContext('2d');
    var W = canvas.width, H = canvas.height;

    var grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, p.bg1);
    grad.addColorStop(1, p.bg2);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Decorative gold border + gentle winter snow dots
    ctx.strokeStyle = p.accent;
    ctx.lineWidth = 8;
    ctx.strokeRect(28, 28, W - 56, H - 56);
    ctx.fillStyle = 'rgba(255,255,255,0.22)';
    for (var s = 0; s < 28; s++) {
      var sx = ((s * 97 + 41) % (W - 100)) + 50;
      var sy = ((s * 67 + 29) % 240) + 44;
      ctx.beginPath();
      ctx.arc(sx, sy, (s % 4) + 2, 0, Math.PI * 2);
      ctx.fill();
    }

    var toName = (document.getElementById('heroCardTo').value || '').trim();
    var fromName = (document.getElementById('heroCardFrom').value || '').trim();
    var customMsg = (document.getElementById('heroCardMsg').value || '').trim() || p.msg;

    ctx.textAlign = 'center';
    ctx.fillStyle = p.accent;
    ctx.font = 'bold 30px "Malgun Gothic", sans-serif';
    ctx.fillText('✦  ' + p.badge + '  ✦', W / 2, 118);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 46px "Malgun Gothic", sans-serif';
    var tLines = wrapLines(ctx, p.title, W - 130);
    var ty = 196;
    tLines.forEach(function (ln) { ctx.fillText(ln, W / 2, ty); ty += 60; });

    ctx.fillStyle = p.accent;
    ctx.fillRect(W / 2 - 90, ty + 6, 180, 4);

    if (toName) {
      ctx.fillStyle = '#FEF3C7';
      ctx.font = 'bold 34px "Malgun Gothic", sans-serif';
      ctx.fillText(toName + ' 님께', W / 2, ty + 68);
      ty += 62;
    }

    ctx.fillStyle = '#F8FAFC';
    ctx.font = '600 32px "Malgun Gothic", sans-serif';
    var mLines = wrapLines(ctx, customMsg, W - 140);
    var my = ty + 68;
    mLines.slice(0, 6).forEach(function (ln) { ctx.fillText(ln, W / 2, my); my += 50; });

    ctx.fillStyle = p.accent;
    ctx.font = 'bold 32px "Malgun Gothic", sans-serif';
    if (fromName) {
      ctx.fillText('— ' + fromName + ' 드림 —', W / 2, H - 122);
    }
    ctx.fillStyle = 'rgba(255,255,255,0.82)';
    ctx.font = '600 24px "Malgun Gothic", sans-serif';
    ctx.fillText('🎵 ' + p.songTitle + '  ·  김쌤의영웅라디오 (paradise-hero.com)', W / 2, H - 64);
  }

  function selectPreset(key, autoFocusPlayer) {
    if (!PRESETS[key]) key = 'dongji';
    currentKey = key;
    var p = PRESETS[key];
    var msgEl = document.getElementById('heroCardMsg');
    if (msgEl) msgEl.value = p.msg;

    var btns = document.querySelectorAll('[data-winter-preset]');
    for (var i = 0; i < btns.length; i++) {
      var active = btns[i].getAttribute('data-winter-preset') === key;
      btns[i].setAttribute('aria-pressed', active ? 'true' : 'false');
      btns[i].style.background = active ? '#D4AF37' : '#FFFFFF';
      btns[i].style.color = active ? '#0E2820' : '#0E2820';
    }

    var audio = document.getElementById('heroWinterAudio');
    var titleEl = document.getElementById('heroWinterSongTitle');
    if (titleEl) titleEl.textContent = p.songTitle;
    if (audio && audio.getAttribute('data-src') !== p.song) {
      audio.setAttribute('data-src', p.song);
      audio.src = p.song;
    }
    if (autoFocusPlayer) {
      var pBox = document.getElementById('heroWinterPlayerBox');
      if (pBox) pBox.style.boxShadow = '0 0 0 4px #D4AF37';
    }
    renderCard();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var sp = new URLSearchParams(window.location.search || '');
    var initKey = sp.get('card') || 'dongji';
    var isPlayParam = sp.get('play') === '1';

    var btns = document.querySelectorAll('[data-winter-preset]');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function () {
        selectPreset(this.getAttribute('data-winter-preset'), false);
      });
    }
    ['heroCardTo', 'heroCardFrom', 'heroCardMsg'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('input', renderCard);
    });

    var playBtn = document.getElementById('btnHeroWinterPlay');
    var audio = document.getElementById('heroWinterAudio');
    if (playBtn && audio) {
      playBtn.addEventListener('click', function () {
        if (audio.paused) {
          audio.play().catch(function () {});
          playBtn.textContent = '⏸ 노래 잠시 멈추기';
          if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.trackFunnelEvent === 'function') {
            window.DreamCompanyCRM.trackFunnelEvent('HERO', 'audio_play', { event_meta: 'winter_cards_' + currentKey });
          }
        } else {
          audio.pause();
          playBtn.textContent = '▶ 백운호 노래 바로 듣기';
        }
      });
    }

    var dlBtn = document.getElementById('btnHeroWinterDownload');
    if (dlBtn) {
      dlBtn.addEventListener('click', function () {
        var c = document.getElementById('heroWinterCanvas');
        if (!c) return;
        var a = document.createElement('a');
        a.download = 'baek_woonho_winter_card_' + currentKey + '.png';
        a.href = c.toDataURL('image/png');
        a.click();
        if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.trackFunnelEvent === 'function') {
          window.DreamCompanyCRM.trackFunnelEvent('HERO', 'gift_download', { event_meta: 'winter_card_' + currentKey });
        }
      });
    }

    var shareBtn = document.getElementById('btnHeroWinterShare');
    if (shareBtn) {
      shareBtn.addEventListener('click', function () {
        var p = PRESETS[currentKey] || PRESETS.dongji;
        var shareUrl = buildCleanShareUrl('https://paradise-hero.com/winter-cards', { card: currentKey, play: '1' });
        triggerOneTouchShare(
          'HERO',
          p.badge + ' 꽃카드 & ' + p.songTitle + ' | 김쌤의영웅라디오',
          p.title + ' — 아래 링크를 누르시면 백운호 노래와 겨울 꽃카드가 바로 열립니다:',
          shareUrl,
          document.getElementById('heroWinterShareToast'),
          '노래+꽃카드 공유 링크가 복사되었습니다! 카카오톡이나 문자에 바로 붙여넣어 보내세요.'
        );
      });
    }

    selectPreset(initKey, isPlayParam);
  });
})();
