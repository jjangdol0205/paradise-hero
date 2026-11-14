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

    const buttons = document.querySelectorAll('button.btn-font-scaler');
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
    }, durationMs || 3800);
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
  let latestModalTitle = '황영웅 기념 선물';

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
    const file = dataUrlToPngFile(dataUrl, `황영웅_기념선물_${Date.now()}.png`);
    if (file && navigator.canShare && navigator.share) {
      try {
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: titleText || '황영웅 무료 기념선물',
            text: '어머님, 황영웅 무료 선물제작소에서 만든 카톡 선물입니다 💚 https://paradise-hero.com/vip.html'
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
            const tName = escapeBillboardHtml(item.tierName || '🌟 황금빛');
            const nick = escapeBillboardHtml(item.nickname || '파라다이스 팬');
            const msg = escapeBillboardHtml(item.message || '영웅님 응원합니다!');
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
    latestModalTitle = titleText || '📸 황영웅 기념 선물 완성!';

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
          <img id="kakao-longpress-img" src="" alt="길게 눌러 저장할 완성 이미지" style="width:100%; max-width:380px; margin:0 auto 14px; border-radius:16px; border:4px solid #D4AF37; box-shadow:0 10px 26px rgba(0,0,0,0.22); -webkit-touch-callout:default !important; user-select:auto !important;">
          <button type="button" id="btn-kakao-direct-file-share" style="display:flex; align-items:center; justify-content:center; width:100%; min-height:64px; margin-bottom:10px; padding:12px 16px; border-radius:14px; background:#FEE500; color:#191919; border:3px solid #D97706; font-size:20px; font-weight:900; cursor:pointer;">
            💬 카카오톡 단톡방·친구에게 이 사진 바로 보내기 👉
          </button>
          <a href="https://cshop.naver.com/paradiseshop" target="_blank" rel="noopener noreferrer sponsored" style="display:flex; align-items:center; justify-content:center; min-height:64px; margin-bottom:10px; padding:12px 16px; border-radius:14px; background:#03C75A; color:#FFFFFF; border:2px solid #065F46; font-size:20px; font-weight:900; text-decoration:none; text-align:center;">
            🟢 네이버페이(Npay) 원탭 구매 — 콘서트·건강선물 &amp; 골드VIP 응원템 보기 👉
          </a>
          <a href="https://influencers.coupang.com/s/paradisehero" target="_blank" rel="noopener noreferrer sponsored" style="display:flex; align-items:center; justify-content:center; min-height:64px; margin-bottom:10px; padding:12px 16px; border-radius:14px; background:#B91C1C; color:#FFFFFF; border:2px solid #FDE68A; font-size:20px; font-weight:900; text-decoration:none; text-align:center;">
            💿 황영웅 정품 음반·효도USB·응원굿즈 쿠팡 공식관 보기 👉
          </a>
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

  document.addEventListener('DOMContentLoaded', () => {
    const initialIndex = loadSavedLevel();
    applyLevel(initialIndex, false);
    hydrateGlobalBillboardTicker();

    document.addEventListener('click', (e) => {
      const fontBtn = e.target.closest('button.btn-font-scaler');
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
    showToast: showSeniorToast
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

/* === HQ Edge Real-Human Visitor & Conversion KPI Tracker (hero_paradisekr) === */
(function () {
  'use strict';
  try {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') return;
    if (window.__HQ_BEACON_SENT_hero_paradisekr__) return;
    window.__HQ_BEACON_SENT_hero_paradisekr__ = true;
    var ua = navigator.userAgent || '';
    if (navigator.webdriver || /jsdom|bot|crawl|spider|slurp|headless|lighthouse|gtmetrix|pingdom|uptimerobot|python|curl|node|axios/i.test(ua)) return;
    var host = (location && location.hostname) || '';
    if (!host || host === 'localhost' || host === '127.0.0.1') return;
    var kst = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
    var ns = 'hero_paradisekr';
    function hitMetric(key) {
      fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/' + key + '_' + kst, { mode: 'cors', keepalive: true }).catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/' + key + '_total', { mode: 'cors', keepalive: true }).catch(function () {});
    }
    window.__hitParadiseHeroMetric = hitMetric;

    fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/pv_' + kst, { mode: 'cors', keepalive: true }).catch(function () {});
    fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/pv_total', { mode: 'cors', keepalive: true }).catch(function () {});
    if (localStorage.getItem('hq_uv_' + ns + '_' + kst) !== '1') {
      localStorage.setItem('hq_uv_' + ns + '_' + kst, '1');
      fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/uv_' + kst, { mode: 'cors', keepalive: true }).catch(function () {});
    }
    if (localStorage.getItem('hq_uv_ever_' + ns) !== '1') {
      localStorage.setItem('hq_uv_ever_' + ns, '1');
      fetch('https://abacus.jasoncameron.dev/hit/' + ns + '/uv_total', { mode: 'cors', keepalive: true }).catch(function () {});
    }

    // Normalize any legacy direct www.coupang.com search links to official AFFSRP redirect
    document.addEventListener('DOMContentLoaded', function () {
      var links = document.querySelectorAll('a[href*="coupang.com/np/search"]');
      links.forEach(function (a) {
        var raw = a.getAttribute('href') || '';
        var qm = raw.replace(/&amp;/g, '&').match(/[?&]q=([^&]+)/i);
        if (qm) {
          a.setAttribute('href', 'https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero&pageKey=' + qm[1]);
        }
      });
    });

    document.addEventListener('click', function (e) {
      var el = e.target && e.target.closest ? e.target.closest('a, button, [role="button"]') : null;
      if (!el) return;
      var href = (el.getAttribute('href') || '').toLowerCase();
      var onclick = (el.getAttribute('onclick') || '').toLowerCase();
      if (href.indexOf('cshop.naver.com/paradiseshop') !== -1 || href.indexOf('brandconnect.naver.com/affiliates/') !== -1) {
        hitMetric('ref_click');
        hitMetric('aff_naver_cshop');
      } else if (href.indexOf('influencers.coupang.com/s/paradisehero') !== -1) {
        hitMetric('ref_click');
        hitMetric('aff_coupang');
        hitMetric('aff_coupang_influencer');
      } else if (href.indexOf('coupang.com') !== -1) {
        hitMetric('ref_click');
        hitMetric('aff_coupang');
      } else if (href.indexOf('#gold-vip-membership') !== -1 || (href.indexOf('mailto:beable9489@gmail.com') !== -1 && href.indexOf('vip') !== -1)) {
        hitMetric('vip_supporter_click');
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
