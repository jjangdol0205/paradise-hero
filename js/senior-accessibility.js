/**
 * senior-accessibility.js
 * 5070 시니어 전용 3단계 [글자크게 가+] 반응형 접근성 위젯 & 카카오톡 응원방 저장 / 인앱 사진 저장 도우미
 * - 1단계: 기본 (20px)
 * - 2단계: 크게 (23px - body.font-lg)
 * - 3단계: 아주 크게 (26px - body.font-xl)
 * - 브라우저 localStorage 자동 저장 및 다음 방문 시 영속성 유지
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'paradise_senior_font_level';

  // 3단계 폰트 레벨 정의 (기본 20px 이상)
  const FONT_LEVELS = [
    { level: 0, className: '', label: '글자크게 가+', toast: '글자 크기: 기본 (20px)' },
    { level: 1, className: 'font-lg', label: '더 크게 가++', toast: '글자 크기: 크게 (23px)' },
    { level: 2, className: 'font-xl', label: '보통으로 가', toast: '글자 크기: 아주 크게 (26px)' }
  ];

  let currentLevelIndex = 0;

  function loadSavedLevel() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== null) {
        const parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed >= 0 && parsed < FONT_LEVELS.length) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('localStorage 접근 불가:', e);
    }
    return 0;
  }

  function applyLevel(index, showToast = false) {
    currentLevelIndex = index % FONT_LEVELS.length;
    const current = FONT_LEVELS[currentLevelIndex];

    document.body.classList.remove('font-lg', 'font-xl');
    if (current.className) {
      document.body.classList.add(current.className);
    }

    const buttons = document.querySelectorAll('#btn-font-scaler, button.btn-font-scaler');
    buttons.forEach((btn) => {
      btn.innerHTML = `<span aria-hidden="true">🔍</span> ${current.label}`;
      btn.setAttribute('aria-label', `화면 글자 크기 조절 (현재: ${current.toast})`);
    });

    try {
      localStorage.setItem(STORAGE_KEY, currentLevelIndex.toString());
    } catch (e) {
      console.warn('localStorage 저장 실패:', e);
    }

    if (showToast) {
      displayToast(current.toast);
    }
  }

  function toggleNextLevel() {
    const nextIndex = (currentLevelIndex + 1) % FONT_LEVELS.length;
    applyLevel(nextIndex, true);
  }

  function displayToast(message) {
    let toast = document.getElementById('senior-accessibility-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'senior-accessibility-toast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.style.cssText = `
        position: fixed;
        bottom: 74px;
        right: 16px;
        background-color: #1B4D3E;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 12px 20px;
        border-radius: 24px;
        font-size: 19px;
        font-weight: 800;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        z-index: 99999;
        pointer-events: none;
        transition: opacity 0.25s ease;
      `;
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.opacity = '1';

    if (toast._timer) clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
    }, 1800);
  }

  // ---------------------------------------------------------------------------
  // 카카오톡 응원방 보내두기 (Web Share API + 주소 복사 왕글씨 안내 모달)
  // ---------------------------------------------------------------------------
  function copyTextToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(() => legacyCopy(text));
    }
    return Promise.resolve(legacyCopy(text));
  }

  function legacyCopy(text) {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return true;
    } catch (err) {
      return false;
    }
  }

  function openKakaoBookmarkGuideModal(shareUrl) {
    let modal = document.getElementById('kakao-bookmark-guide-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'kakao-bookmark-guide-modal';
      modal.className = 'kakao-king-modal-backdrop';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-label', '카카오톡 응원방 주소 복사 완료 안내');
      modal.innerHTML = `
        <div class="kakao-king-modal-card">
          <div style="font-size: 28px; font-weight: 900; color: #0E2820; margin-bottom: 12px;">
            💛 응원방 주소가 복사되었습니다!
          </div>
          <div class="kakao-king-modal-guide">
            📱 지금 <strong>카카오톡</strong>을 여신 뒤<br>
            <strong>[나와의 채팅]</strong>이나 <strong>[팬 친구 대화방]</strong> 글씨 입력창을<br>
            <strong style="color:#B91C1C; text-decoration:underline;">2초간 꾹~ 눌러 [붙여넣기]</strong> 후 전송해 두세요!
          </div>
          <p style="font-size: 20px; color: #374151; font-weight: 700; margin-bottom: 18px; line-height: 1.55;">
            한 번만 보내두시면 앞으로 검색할 필요 없이<br>
            카톡방에서 1초 만에 김쌤의영웅라디오 가족 사랑방으로 바로 오실 수 있습니다.
          </p>
          <div style="background:#FFFFFF; border:2px solid #D1D5DB; border-radius:12px; padding:12px 16px; font-size:20px; font-weight:800; color:#1B4D3E; margin-bottom:18px; word-break:break-all;" id="kakao-bookmark-copied-url"></div>
          <button type="button" id="btn-close-kakao-bookmark-modal" class="btn btn-emerald btn-full" style="min-height: 64px; font-size: 22px; font-weight: 900;">
            ✅ 네, 확인했습니다! (창 닫기)
          </button>
        </div>
      `;
      document.body.appendChild(modal);

      modal.addEventListener('click', (ev) => {
        if (ev.target === modal || ev.target.closest('#btn-close-kakao-bookmark-modal')) {
          modal.classList.remove('open');
        }
      });
    }

    const urlBox = modal.querySelector('#kakao-bookmark-copied-url');
    if (urlBox) urlBox.textContent = shareUrl;
    modal.classList.add('open');
  }

  function showSeniorToast(message, durationMs) {
    if (typeof document === 'undefined' || !document.body) return;
    let toast = document.getElementById('senior-global-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'senior-global-toast';
      toast.className = 'senior-toast-banner';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.display = 'block';
    if (toast.__hideTimer) clearTimeout(toast.__hideTimer);
    toast.__hideTimer = setTimeout(() => {
      toast.style.display = 'none';
    }, durationMs || 1800);
  }

  async function shareOrBookmarkRoom(customUrl) {
    const targetUrl = customUrl || window.location.href.split('#')[0] || 'https://paradise-hero.com/';
    const shareData = {
      title: '💚 유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지',
      text: '어머님·아버님, 가상 트로트 가수 백운호의 중저음 노래와 인생 사연이 흐르는 김쌤의영웅라디오 사랑방입니다! 카톡에 저장해 두세요 💚',
      url: targetUrl
    };

    await copyTextToClipboard(targetUrl);

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {
        if (err && err.name === 'AbortError') {
          showSeniorToast('✅ 주소가 복사되었습니다! 카카오톡 대화창에 붙여넣기 해주세요 💚');
          openKakaoBookmarkGuideModal(targetUrl);
          return;
        }
      }
    }
    showSeniorToast('✅ 주소가 복사되었습니다! 카카오톡 대화창에 붙여넣기 해주세요 💚');
    openKakaoBookmarkGuideModal(targetUrl);
  }

  // ---------------------------------------------------------------------------
  // 카카오톡 인앱 브라우저(KAKAOTALK UA) & 모바일 2초 꾹 사진 저장 왕글씨 모달
  // ---------------------------------------------------------------------------
  function isKakaoInAppOrMobile() {
    const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    return /KAKAOTALK|NAVER|Instagram|FBAN|FBAV|Line|Android|iPhone|iPad|iPod/i.test(ua);
  }

  let latestModalDataUrl = '';
  let latestModalTitle = '백운호 기념 선물';

  function dataUrlToPngFile(dataUrl, filename) {
    try {
      const parts = (dataUrl || '').split(',');
      if (parts.length < 2) return null;
      const mimeMatch = parts[0].match(/:(.*?);/);
      const mime = (mimeMatch && mimeMatch[1]) || 'image/png';
      const bstr = atob(parts[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, { type: mime });
    } catch (e) {
      return null;
    }
  }

  async function shareDataUrlViaKakaoOrSystem(dataUrl, titleText) {
    const file = dataUrlToPngFile(dataUrl, `백운호_기념선물_${Date.now()}.png`);
    if (file && navigator.canShare && navigator.share) {
      try {
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: titleText || '백운호 무료 기념선물',
            text: '김쌤의영웅라디오 가족 사랑방에서 만든 무료 카톡 안부선물입니다 💚 https://paradise-hero.com/vip.html'
          });
          return true;
        }
      } catch (err) {
        if (err && err.name === 'AbortError') return false;
      }
    }
    await shareOrBookmarkRoom('https://paradise-hero.com/vip.html');
    return false;
  }

  function escapeBillboardHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function hydrateGlobalBillboardTicker() {
    try {
      const tickers = document.querySelectorAll('.billboard-text');
      if (!tickers.length) return;
      const existing = JSON.parse(localStorage.getItem('paradise_billboard_cheers') || '[]');
      const prependText = Array.isArray(existing) && existing.length > 0
        ? existing.slice(0, 5).map((item) => {
            const tName = escapeBillboardHtml(item.tierName || '🌟 사랑방');
            const nick = escapeBillboardHtml(item.nickname || '사랑방 가족');
            const msg = escapeBillboardHtml(item.message || '오늘도 건강하고 평안한 하루 보내세요!');
            return `[${tName} ${nick}] "${msg}" 🌟`;
          }).join(' \u00A0\u00A0\u00A0\u00A0 ') + ' \u00A0\u00A0\u00A0\u00A0 '
        : '';

      tickers.forEach((ticker) => {
        if (ticker.getAttribute('data-seamless-hydrated') === '1') return;
        const baseText = (ticker.textContent || '').replace(/\s+/g, ' ').trim();
        const combined = prependText + escapeBillboardHtml(baseText);
        ticker.innerHTML = `${combined} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${combined}`;
        ticker.setAttribute('data-seamless-hydrated', '1');
      });
    } catch (e) {
      // Ignore storage error
    }
  }

  function openLongPressPhotoSaveModal(dataUrl, titleText) {
    latestModalDataUrl = dataUrl || '';
    latestModalTitle = titleText || '📸 백운호 기념 선물 완성!';

    let modal = document.getElementById('kakao-photo-longpress-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'kakao-photo-longpress-modal';
      modal.className = 'kakao-king-modal-backdrop';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-label', '휴대폰 사진첩 저장 안내');
      modal.innerHTML = `
        <div class="kakao-king-modal-card">
          <div id="kakao-longpress-title" style="font-size: 26px; font-weight: 900; color: #0E2820; margin-bottom: 12px;">
            📸 백운호 기념 선물 완성!
          </div>
          <div class="kakao-king-modal-guide" style="font-size: 23px;">
            📱 손가락으로 아래 그림을 <strong>2초간 꾹~ 눌러</strong><br>
            <strong style="color:#B91C1C; text-decoration:underline;">[사진 저장]</strong> 또는 <strong style="color:#B91C1C; text-decoration:underline;">[이미지 저장]</strong>을 누르세요!
          </div>
          <img id="kakao-longpress-img" src="" alt="길게 눌러 저장할 완성 이미지" style="width:100%; max-width:380px; margin:0 auto 14px; border-radius:16px; border:4px solid #D4AF37; box-shadow:0 10px 26px rgba(0,0,0,0.22); -webkit-touch-callout:default !important; user-select:auto !important;">
          <button type="button" id="btn-kakao-direct-file-share" style="display:flex; align-items:center; justify-content:center; width:100%; min-height:64px; margin-bottom:10px; padding:12px 16px; border-radius:14px; background:#FEE500; color:#191919; border:3px solid #D97706; font-size:20px; font-weight:900; cursor:pointer;">
            💬 카카오톡 단톡방·친구에게 이 사진 바로 보내기 👉
          </button>
          <a href="https://cshop.naver.com/paradiseshop" target="_blank" rel="noopener noreferrer sponsored" style="display:flex; align-items:center; justify-content:center; min-height:64px; margin-bottom:8px; padding:12px 16px; border-radius:14px; background:#03C75A; color:#FFFFFF; border:2px solid #065F46; font-size:20px; font-weight:900; text-decoration:none; text-align:center;">
            💚 김쌤의 콘서트·응원 안심 준비물관 (네이버페이 공식관) 👉
          </a>
          <a href="https://influencers.coupang.com/s/paradisehero" target="_blank" rel="noopener noreferrer sponsored" style="display:flex; align-items:center; justify-content:center; min-height:64px; margin-bottom:8px; padding:12px 16px; border-radius:14px; background:#B91C1C; color:#FFFFFF; border:2px solid #FDE68A; font-size:20px; font-weight:900; text-decoration:none; text-align:center;">
            📻 라디오 스피커·방석·청취 건강 준비물관 (쿠팡 공식관) 👉
          </a>
          <p style="font-size:16px; color:#475569; font-weight:700; margin:0 0 10px; line-height:1.45;">
            ※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다.
          </p>
          <button type="button" id="btn-close-kakao-longpress-modal" class="btn btn-emerald btn-full" style="min-height: 64px; font-size: 22px; font-weight: 900;">
            ✅ 사진 저장 완료! (창 닫기)
          </button>
        </div>
      `;
      document.body.appendChild(modal);

      modal.addEventListener('click', (ev) => {
        if (ev.target.closest('#btn-kakao-direct-file-share')) {
          ev.preventDefault();
          shareDataUrlViaKakaoOrSystem(latestModalDataUrl, latestModalTitle);
          return;
        }
        if (ev.target === modal || ev.target.closest('#btn-close-kakao-longpress-modal')) {
          modal.classList.remove('open');
        }
      });
    }

    const titleEl = modal.querySelector('#kakao-longpress-title');
    const imgEl = modal.querySelector('#kakao-longpress-img');
    if (titleEl && titleText) titleEl.textContent = titleText;
    if (imgEl && dataUrl) imgEl.src = dataUrl;
    modal.classList.add('open');
  }

  function isInAppVoiceBlockedWebView() {
    const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    return /Instagram|FBAN|FBAV|KAKAOTALK/i.test(ua);
  }

  function buildChromeExternalIntentUrl() {
    const loc = (typeof window !== 'undefined' && window.location) ? window.location : null;
    const host = (loc && loc.host) ? loc.host : 'paradise-hero.com';
    const path = (loc && loc.pathname) ? loc.pathname : '/story.html';
    const search = (loc && loc.search) ? loc.search : '';
    return 'intent://' + host + path + search + '#Intent;scheme=https;package=com.android.chrome;end';
  }

  function openInAppVoiceBrowserModal(focusTargetId) {
    let modal = document.getElementById('inapp-voice-browser-modal');
    const currentUrl = (typeof window !== 'undefined' && window.location && window.location.href)
      ? window.location.href
      : 'https://paradise-hero.com/story.html';
    const chromeIntentUrl = buildChromeExternalIntentUrl();

    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'inapp-voice-browser-modal';
      modal.className = 'kakao-king-modal-backdrop';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-label', '외부 인터넷 창으로 열기 안내');
      modal.innerHTML = `
        <div class="kakao-king-modal-card" style="max-width: 560px; text-align: left;">
          <div style="font-size: 25px; font-weight: 900; color: #0E2820; margin-bottom: 12px; text-align: center; line-height: 1.4;">
            🎙️ 마이크 음성 입력을 쓰시려면<br>외부 인터넷 창으로 열어주세요!
          </div>
          <p style="font-size: 20px; color: #1F2937; font-weight: 700; line-height: 1.65; margin: 0 0 16px;">
            현재 보고 계신 <strong>카카오톡 · 인스타그램 앱 안의 임시 창</strong>에서는 보안 정책 때문에 휴대폰 마이크(음성 받아쓰기)가 작동하지 않습니다.
          </p>
          <a id="btn-inapp-open-chrome" href="${chromeIntentUrl}" style="display: flex; align-items: center; justify-content: center; width: 100%; min-height: 64px; padding: 14px 18px; margin-bottom: 14px; border-radius: 14px; background: #1B4D3E; color: #FFFFFF; border: 3px solid #D4AF37; font-size: 20px; font-weight: 900; text-decoration: none; text-align: center; line-height: 1.4;">
            🌐 삼성·안드로이드폰: 크롬(Chrome) 창으로 1초 열기 👉
          </a>
          <div style="background: #FFFBEB; border: 2px solid #F59E0B; border-radius: 14px; padding: 16px; margin-bottom: 14px; font-size: 20px; color: #1F2937; line-height: 1.65;">
            <strong style="color: #92400E; display: block; margin-bottom: 6px;">🍎 아이폰(iOS)에서 여시는 방법:</strong>
            화면 <strong>우측 하단 ⋯ 또는 공유 버튼 ➜ Safari로 열기</strong>를 누르시거나, 아래 <strong>주소 복사하기</strong> 버튼을 눌러 사파리 주소창에 붙여넣어 주세요!
          </div>
          <button type="button" id="btn-inapp-copy-url" style="display: flex; align-items: center; justify-content: center; width: 100%; min-height: 64px; padding: 14px 18px; margin-bottom: 10px; border-radius: 14px; background: #FEE500; color: #191919; border: 2px solid #D97706; font-size: 20px; font-weight: 900; cursor: pointer;">
            📋 주소 복사하기
          </button>
          <button type="button" id="btn-inapp-use-keyboard" style="display: flex; align-items: center; justify-content: center; width: 100%; min-height: 64px; padding: 14px 18px; border-radius: 14px; background: #F3F4F6; color: #1F2937; border: 2px solid #9CA3AF; font-size: 20px; font-weight: 900; cursor: pointer;">
            ⌨️ 그냥 키보드로 편하게 적기
          </button>
        </div>
      `;
      document.body.appendChild(modal);
    }

    const chromeLink = modal.querySelector('#btn-inapp-open-chrome');
    if (chromeLink) {
      chromeLink.setAttribute('href', chromeIntentUrl);
    }

    if (!modal.getAttribute('data-bound')) {
      modal.setAttribute('data-bound', '1');
      modal.addEventListener('click', function (ev) {
        if (ev.target.closest('#btn-inapp-copy-url')) {
          ev.preventDefault();
          copyTextToClipboard(currentUrl).then(function () {
            showSeniorToast('✅ 사연장 주소가 복사되었습니다! 크롬이나 Safari 주소창에 붙여넣어 주세요 💚');
          });
          return;
        }
        if (ev.target === modal || ev.target.closest('#btn-inapp-use-keyboard')) {
          ev.preventDefault();
          modal.classList.remove('open');
          modal.style.display = '';
          const targetEl = focusTargetId ? document.getElementById(focusTargetId) : document.getElementById('story-content');
          if (targetEl && typeof targetEl.focus === 'function') {
            targetEl.focus();
          }
        }
      });
    }

    modal.style.display = 'flex';
    modal.classList.add('open');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const initialIndex = loadSavedLevel();
    applyLevel(initialIndex, false);
    hydrateGlobalBillboardTicker();

    // 입력창(input / textarea / select) 포커스 시 하단 고정 미니바 자동 숨김 (모바일 자판 가림 원천 차단)
    document.addEventListener('focusin', (ev) => {
      const t = ev.target;
      if (t && t.matches && t.matches('input:not([type="checkbox"]):not([type="radio"]):not([type="file"]), textarea, select, [contenteditable="true"]')) {
        document.body.classList.add('is-keyboard-editing');
      }
    });
    document.addEventListener('focusout', () => {
      setTimeout(() => {
        const active = document.activeElement;
        if (!active || !active.matches || !active.matches('input:not([type="checkbox"]):not([type="radio"]):not([type="file"]), textarea, select, [contenteditable="true"]')) {
          document.body.classList.remove('is-keyboard-editing');
        }
      }, 120);
    });

    document.addEventListener('click', (e) => {
      const fontBtn = e.target.closest('#btn-font-scaler, button.btn-font-scaler');
      if (fontBtn) {
        e.preventDefault();
        toggleNextLevel();
        return;
      }

      const kakaoBtn = e.target.closest('.js-kakao-bookmark-btn');
      if (kakaoBtn) {
        e.preventDefault();
        const customUrl = kakaoBtn.getAttribute('data-share-url') || '';
        shareOrBookmarkRoom(customUrl);
      }
    });
  });

  window.SeniorAccessibility = {
    getCurrentLevel: () => currentLevelIndex,
    setLevel: (idx) => applyLevel(idx, false),
    toggleNext: toggleNextLevel,
    showToast: showSeniorToast,
    isInAppVoiceBlockedWebView: isInAppVoiceBlockedWebView,
    buildChromeExternalIntentUrl: buildChromeExternalIntentUrl,
    openInAppVoiceBrowserModal: openInAppVoiceBrowserModal
  };

  window.ParadiseKakaoBookmark = {
    shareRoom: shareOrBookmarkRoom,
    shareDataUrl: shareDataUrlViaKakaoOrSystem,
    showToast: showSeniorToast,
    escapeHtml: escapeBillboardHtml,
    isKakaoInAppOrMobile: isKakaoInAppOrMobile,
    openLongPressPhotoSaveModal: function (dataUrl, titleText) {
      if (typeof window.__hitParadiseHeroMetric === 'function') {
        window.__hitParadiseHeroMetric('gift_download');
      }
      return openLongPressPhotoSaveModal(dataUrl, titleText);
    }
  };
})();

/* === HQ Edge Real-Human Visitor & Conversion KPI Tracker (GAS no-cors + Safe Local Persistence) === */
(function () {
  'use strict';
  try {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') return;
    if (window.__HQ_BEACON_SENT_hero_paradisekr__) return;
    window.__HQ_BEACON_SENT_hero_paradisekr__ = true;

    var ns = 'hero_paradisekr';
    var LOCAL_METRICS_KEY = 'hq_local_metrics_hero_v1';
    var cachedGasUrl = '';

    function getKstDateStr() {
      return new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
    }
    window.getHeroKstDate = getKstDateStr;

    var ua = navigator.userAgent || '';
    var isAutomatedOrLocal = Boolean(
      navigator.webdriver ||
      /jsdom|bot|crawl|spider|slurp|headless|lighthouse|gtmetrix|pingdom|uptimerobot|python|curl|node|axios/i.test(ua) ||
      !location ||
      !location.hostname ||
      location.hostname === 'localhost' ||
      location.hostname === '127.0.0.1'
    );

    function bumpLocalCounter(metricKey) {
      try {
        var map = JSON.parse(localStorage.getItem(LOCAL_METRICS_KEY) || '{}');
        map[metricKey] = (parseInt(map[metricKey], 10) || 0) + 1;
        localStorage.setItem(LOCAL_METRICS_KEY, JSON.stringify(map));
      } catch (e) {}
    }

    function sendGasNoCorsPing(eventType, counterKey) {
      try {
        if (isAutomatedOrLocal || typeof fetch !== 'function') return;
        if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.recordCommunityEvent === 'function') {
          window.DreamCompanyCRM.recordCommunityEvent(eventType, counterKey);
          return;
        }
        var firePost = function (execUrl) {
          if (!execUrl) return;
          fetch(execUrl, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify({
              action: 'community_counter_hit',
              div: 'HERO',
              event_type: eventType,
              counter_key: counterKey,
              source_url: (location && location.href) ? location.href : '',
              client_ts: new Date().toISOString()
            }),
            keepalive: true
          }).catch(function () {});
        };
        if (cachedGasUrl) {
          firePost(cachedGasUrl);
          return;
        }
        var cfgPath = window.HQ_MAILING_CONFIG_PATH || '/hq-mailing-endpoint.json';
        fetch(cfgPath, { cache: 'force-cache' })
          .then(function (r) { return r && r.ok ? r.json() : null; })
          .then(function (cfg) {
            if (cfg && cfg.webapp_exec_url && String(cfg.webapp_exec_url).indexOf('https://script.google.com/macros/s/') === 0) {
              cachedGasUrl = String(cfg.webapp_exec_url).trim();
              firePost(cachedGasUrl);
            }
          })
          .catch(function () {});
      } catch (e) {}
    }

    function hitMetric(key) {
      if (!key) return;
      var kstNow = getKstDateStr();
      bumpLocalCounter(key + '_' + kstNow);
      bumpLocalCounter(key + '_total');
      if (isAutomatedOrLocal) return;
      sendGasNoCorsPing(key, ns + ':' + key + '_' + kstNow);
    }
    window.__hitParadiseHeroMetric = hitMetric;
    window.hitHeroBeacon = hitMetric;

    function hitSignupMetric(emailForDedupe) {
      var kstNow = getKstDateStr();
      var dedupeKey = 'hq_signup_' + ns + '_' + kstNow + '_' + String(emailForDedupe || '').trim().toLowerCase();
      try {
        if (emailForDedupe && localStorage.getItem(dedupeKey) === '1') return;
        if (emailForDedupe) localStorage.setItem(dedupeKey, '1');
      } catch (e) {}
      bumpLocalCounter('signup_' + kstNow);
      bumpLocalCounter('signup_total');
      if (isAutomatedOrLocal) return;
      sendGasNoCorsPing('signup', ns + ':signup_' + kstNow);
    }
    window.hitHeroSignupBeacon = hitSignupMetric;

    function hitStorySubmitMetric() {
      var kstNow = getKstDateStr();
      bumpLocalCounter('story_submit_' + kstNow);
      bumpLocalCounter('story_submit_total');
      if (isAutomatedOrLocal) return;
      sendGasNoCorsPing('story_submit', ns + ':story_submit_' + kstNow);
    }
    window.hitHeroStorySubmitBeacon = hitStorySubmitMetric;

    // Normalize any legacy direct www.coupang.com search links to official AFFSRP redirect
    // + Hydrate Morning Briefing KST Date & 4-Theme Safe Market Tabs (runs even on localhost)
    document.addEventListener('DOMContentLoaded', function () {
      var links = document.querySelectorAll('a[href*="coupang.com/np/search"]');
      links.forEach(function (a) {
        var raw = a.getAttribute('href') || '';
        var qm = raw.replace(/&amp;/g, '&').match(/[?&]q=([^&]+)/i);
        if (qm) {
          a.setAttribute('href', 'https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero&pageKey=' + qm[1]);
        }
      });

      var dateBadges = document.querySelectorAll('.js-kst-today-label');
      if (dateBadges.length) {
        var dNow = new Date(Date.now() + 9 * 3600 * 1000);
        var mNum = dNow.getUTCMonth() + 1;
        var dNum = dNow.getUTCDate();
        var wkNames = ['일', '월', '화', '수', '목', '금', '토'];
        var wk = wkNames[dNow.getUTCDay()];
        dateBadges.forEach(function (el) {
          el.textContent = mNum + '월 ' + dNum + '일(' + wk + ') 오늘의 브리핑';
        });
      }

      function activateSafeMarketTab(tabKey, scrollToMarket) {
        var btns = document.querySelectorAll('.safe-theme-tab-btn[data-market-tab]');
        var panels = document.querySelectorAll('.safe-theme-panel[data-market-panel]');
        if (!btns.length || !panels.length) return;
        btns.forEach(function (b) {
          var isAct = b.getAttribute('data-market-tab') === tabKey;
          b.classList.toggle('active', isAct);
          b.setAttribute('aria-selected', isAct ? 'true' : 'false');
        });
        panels.forEach(function (p) {
          var isAct = p.getAttribute('data-market-panel') === tabKey;
          p.classList.toggle('active', isAct);
        });
        if (scrollToMarket) {
          var sec = document.getElementById('senior-curation-market');
          if (sec && sec.scrollIntoView) {
            sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      }

      document.addEventListener('click', function (ev) {
        if (ev.__heroMarketTabHandled) return;
        var tabBtn = ev.target && ev.target.closest ? ev.target.closest('.safe-theme-tab-btn[data-market-tab]') : null;
        if (tabBtn) {
          ev.__heroMarketTabHandled = true;
          ev.preventDefault();
          activateSafeMarketTab(tabBtn.getAttribute('data-market-tab'), false);
          return;
        }
        var jumpBtn = ev.target && ev.target.closest ? ev.target.closest('[data-open-market-tab]') : null;
        if (jumpBtn) {
          var targetTab = jumpBtn.getAttribute('data-open-market-tab');
          if (document.getElementById('senior-curation-market')) {
            ev.__heroMarketTabHandled = true;
            ev.preventDefault();
            activateSafeMarketTab(targetTab, true);
          }
        }
      });
    });

    if (isAutomatedOrLocal) return;

    var kst = getKstDateStr();
    bumpLocalCounter('pv_' + kst);
    try {
      if (localStorage.getItem('hq_uv_' + ns + '_' + kst) !== '1') {
        localStorage.setItem('hq_uv_' + ns + '_' + kst, '1');
        bumpLocalCounter('uv_' + kst);
        sendGasNoCorsPing('daily_uv', ns + ':uv_' + kst);
      }
      if (localStorage.getItem('hq_uv_ever_' + ns) !== '1') {
        localStorage.setItem('hq_uv_ever_' + ns, '1');
        bumpLocalCounter('uv_total');
      }
    } catch (e) {}

    function hitShopAndReferral(extraKey) {
      hitMetric('ref_click');
      hitMetric('shop_click');
      if (extraKey) hitMetric(extraKey);
    }

    var lastBeaconClickTs = 0;
    var lastBeaconEl = null;

    document.addEventListener('click', function (e) {
      var el = e.target && e.target.closest ? e.target.closest('a, button, [role="button"]') : null;
      if (!el) return;
      var nowTs = Date.now();
      if (lastBeaconEl === el && nowTs - lastBeaconClickTs < 400) return;
      lastBeaconClickTs = nowTs;
      lastBeaconEl = el;

      var href = (el.getAttribute('href') || '').toLowerCase();
      var onclick = (el.getAttribute('onclick') || '').toLowerCase();
      if (href.indexOf('cshop.naver.com/paradiseshop') !== -1 || href.indexOf('brandconnect.naver.com/affiliates/') !== -1) {
        hitShopAndReferral('aff_naver_cshop');
      } else if (href.indexOf('influencers.coupang.com/s/paradisehero') !== -1) {
        hitShopAndReferral('aff_coupang_influencer');
      } else if (href.indexOf('coupang.com') !== -1) {
        hitShopAndReferral('aff_coupang');
      } else if (href.indexOf('linkprice.com') !== -1 || href.indexOf('kr.iherb.com') !== -1 || href.indexOf('myrealt.rip') !== -1 || href.indexOf('naver.me/') !== -1) {
        hitShopAndReferral('aff_partner_store');
      } else if (onclick.indexOf('vipdigitalstudio.download') !== -1) {
        hitMetric('gift_download');
      }
    }, true);

    document.addEventListener('submit', function (e) {
      var fid = e.target && e.target.id ? e.target.id : '';
      if (fid === 'auto-billboard-form' || fid === 'cheer-form') {
        hitMetric('billboard_cheer');
      }
    }, true);
  } catch (err) {}
})();
