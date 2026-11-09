/**
 * senior-accessibility.js
 * 5070 시니어 전용 3단계 [글자크게 가+] 반응형 접근성 위젯
 * - 1단계: 기본 (18px)
 * - 2단계: 크게 (21px - body.font-lg)
 * - 3단계: 아주 크게 (24px - body.font-xl)
 * - 브라우저 localStorage 자동 저장 및 다음 방문 시 영속성 유지
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'paradise_senior_font_level';

  // 3단계 폰트 레벨 정의
  const FONT_LEVELS = [
    { level: 0, className: '', label: '글자크게 가+', toast: '글자 크기: 기본 (18px)' },
    { level: 1, className: 'font-lg', label: '더 크게 가++', toast: '글자 크기: 크게 (21px)' },
    { level: 2, className: 'font-xl', label: '보통으로 가', toast: '글자 크기: 아주 크게 (24px)' }
  ];

  let currentLevelIndex = 0;

  /**
   * 로컬 스토리지에서 저장된 폰트 크기 불러오기
   */
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
    return 0; // 기본값
  }

  /**
   * 폰트 레벨 적용 및 클래스 갱신
   */
  function applyLevel(index, showToast = false) {
    currentLevelIndex = index % FONT_LEVELS.length;
    const current = FONT_LEVELS[currentLevelIndex];

    // body 클래스 초기화 후 새 클래스 부여
    document.body.classList.remove('font-lg', 'font-xl');
    if (current.className) {
      document.body.classList.add(current.className);
    }

    // 모든 글자 크기 조절 버튼 텍스트/접근성 라벨 동기화
    const buttons = document.querySelectorAll('.btn-font-scaler');
    buttons.forEach((btn) => {
      btn.innerHTML = `<span aria-hidden="true">🔍</span> ${current.label}`;
      btn.setAttribute('aria-label', `화면 글자 크기 조절 (현재: ${current.toast})`);
    });

    // 로컬 스토리지에 영구 저장
    try {
      localStorage.setItem(STORAGE_KEY, currentLevelIndex.toString());
    } catch (e) {
      console.warn('localStorage 저장 실패:', e);
    }

    if (showToast) {
      displayToast(current.toast);
    }
  }

  /**
   * 다음 레벨로 토글 (0 -> 1 -> 2 -> 0)
   */
  function toggleNextLevel() {
    const nextIndex = (currentLevelIndex + 1) % FONT_LEVELS.length;
    applyLevel(nextIndex, true);
  }

  /**
   * 시니어 안심 토스트 알림 (2초간 안내)
   */
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
        padding: 12px 24px;
        border-radius: 30px;
        font-size: 18px;
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
    }, 2000);
  }

  // 초기화 실행
  document.addEventListener('DOMContentLoaded', () => {
    const initialIndex = loadSavedLevel();
    applyLevel(initialIndex, false);

    // 이벤트 위임 또는 버튼 직접 바인딩
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-font-scaler');
      if (btn) {
        e.preventDefault();
        toggleNextLevel();
      }
    });
  });

  // 전역 객체 노출 (테스트 및 디버깅용)
  window.SeniorAccessibility = {
    getCurrentLevel: () => currentLevelIndex,
    setLevel: (idx) => applyLevel(idx, false),
    toggleNext: toggleNextLevel
  };
})();
