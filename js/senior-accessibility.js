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

    const buttons = document.querySelectorAll('.btn-font-scaler');
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
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #1B4D3E;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 14px 26px;
        border-radius: 30px;
        font-size: 20px;
        font-weight: 800;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        z-index: 99999;
        pointer-events: none;
        transition: opacity 0.3s ease;
      `;
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.opacity = '1';

    if (toast._timer) clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
    }, 2200);
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
            카톡방에서 1초 만에 황영웅 응원방으로 바로 오실 수 있습니다.
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

  async function shareOrBookmarkRoom(customUrl) {
    const targetUrl = customUrl || window.location.href.split('#')[0] || 'https://paradise-hero.com/';
    const shareData = {
      title: '💚 가수 황영웅 공식 팬 쉼터 — 파라다이스 히어로',
      text: '어머님, 황영웅님과 무료 기념사진도 찍고 김쌤의 영웅라디오도 바로 들으실 수 있는 응원방입니다! 카톡에 저장해 두세요 💚',
      url: targetUrl
    };

    await copyTextToClipboard(targetUrl);

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {
        if (err && err.name === 'AbortError') {
          openKakaoBookmarkGuideModal(targetUrl);
          return;
        }
      }
    }
    openKakaoBookmarkGuideModal(targetUrl);
  }

  // ---------------------------------------------------------------------------
  // 카카오톡 인앱 브라우저(KAKAOTALK UA) & 모바일 2초 꾹 사진 저장 왕글씨 모달
  // ---------------------------------------------------------------------------
  function isKakaoInAppOrMobile() {
    const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    return /KAKAOTALK|NAVER|Instagram|FBAN|FBAV|Line|Android|iPhone|iPad|iPod/i.test(ua);
  }

  function openLongPressPhotoSaveModal(dataUrl, titleText) {
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
            📸 황영웅 기념 선물 완성!
          </div>
          <div class="kakao-king-modal-guide" style="font-size: 23px;">
            📱 손가락으로 아래 그림을 <strong>2초간 꾹~ 눌러</strong><br>
            <strong style="color:#B91C1C; text-decoration:underline;">[사진 저장]</strong> 또는 <strong style="color:#B91C1C; text-decoration:underline;">[이미지 저장]</strong>을 누르세요!
          </div>
          <img id="kakao-longpress-img" src="" alt="길게 눌러 저장할 완성 이미지" style="width:100%; max-width:380px; margin:0 auto 18px; border-radius:16px; border:4px solid #D4AF37; box-shadow:0 10px 26px rgba(0,0,0,0.22); -webkit-touch-callout:default !important; user-select:auto !important;">
          <button type="button" id="btn-close-kakao-longpress-modal" class="btn btn-emerald btn-full" style="min-height: 64px; font-size: 22px; font-weight: 900;">
            ✅ 사진 저장 완료! (창 닫기)
          </button>
        </div>
      `;
      document.body.appendChild(modal);

      modal.addEventListener('click', (ev) => {
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

  document.addEventListener('DOMContentLoaded', () => {
    const initialIndex = loadSavedLevel();
    applyLevel(initialIndex, false);

    document.addEventListener('click', (e) => {
      const fontBtn = e.target.closest('.btn-font-scaler');
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
    toggleNext: toggleNextLevel
  };

  window.ParadiseKakaoBookmark = {
    shareRoom: shareOrBookmarkRoom,
    isKakaoInAppOrMobile: isKakaoInAppOrMobile,
    openLongPressPhotoSaveModal: openLongPressPhotoSaveModal
  };
})();
