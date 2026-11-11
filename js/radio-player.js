/**
 * radio-player.js
 * @김쌤의영웅라디오 1-클릭 연속 재생 플레이어 & 본문 16:9 유튜브 공식 플레이어 연동 모듈
 * - 모바일(iOS/안드로이드) 무음 차단 문제를 100% 해결하기 위해 본문 중앙 16:9 보이는 유튜브 플레이어(#main-youtube-embed)와
 *   화면 하단 고정 바(Sticky Bar)를 동시 연동합니다.
 * - ?ep=1~5 딥링크 파라미터 자동 선택·재생을 지원합니다.
 */

(function () {
  'use strict';

  const RADIO_EPISODES = [
    {
      id: 'ep01',
      title: '1화: [보컬분석] 가수 황영웅, 소리 전문가들이 극찬한 명품 중저음의 비밀',
      song: '당신 편 (정규 1집 타이틀곡)',
      duration: '15:20',
      videoId: 'lGkMncY4u1o'
    },
    {
      id: 'ep02',
      title: '2화: 황영웅, 아무도 몰랐던 침묵의 시간들... 빛과 그림자 8부작 풀스토리',
      song: '꽃구경 · 황영웅 인생다큐',
      duration: '16:45',
      videoId: 'QcrBg7UWg3k'
    },
    {
      id: 'ep03',
      title: '3화: 소리 전문가가 분석한 황영웅의 압도적 감성 이유 (김쌤의 영웅 라디오)',
      song: '인사동 찻집 · 비나리',
      duration: '17:10',
      videoId: 'kgkUqsI5d2k'
    },
    {
      id: 'ep04',
      title: '4화: 황영웅 운명이 뒤바뀐 8주간의 기록 (오디오북 특집)',
      song: '당신꽃 · 황금빛 인생',
      duration: '15:50',
      videoId: 'NArJ2CH2IAw'
    },
    {
      id: 'ep05',
      title: '5화: 황영웅 귀환 확정 & 파라다이스 총공 특집 브리핑',
      song: '함께해요 · 비상',
      duration: '0:45 (특집 속보 브리핑)',
      videoId: 'GwJBs6kouow'
    }
  ];

  const STATE_KEY = 'paradise_radio_state_v2';

  let currentIndex = 0;
  let isPlaying = false;

  function loadState() {
    try {
      const saved = sessionStorage.getItem(STATE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.index === 'number' && parsed.index >= 0 && parsed.index < RADIO_EPISODES.length) {
          currentIndex = parsed.index;
        }
        isPlaying = Boolean(parsed.isPlaying);
      }
    } catch (e) {
      currentIndex = 0;
      isPlaying = false;
    }
  }

  function applyQueryDeepLink() {
    try {
      if (typeof window === 'undefined' || !window.location) return false;
      const params = new URLSearchParams(window.location.search || '');
      const epParam = params.get('ep');
      if (epParam) {
        const epNum = parseInt(epParam, 10);
        if (!isNaN(epNum) && epNum >= 1 && epNum <= RADIO_EPISODES.length) {
          currentIndex = epNum - 1;
          isPlaying = true;
          saveState();
          return true;
        }
      }
    } catch (e) {
      // Ignore malformed query
    }
    return false;
  }

  function saveState() {
    try {
      sessionStorage.setItem(
        STATE_KEY,
        JSON.stringify({
          index: currentIndex,
          isPlaying: isPlaying
        })
      );
    } catch (e) {
      // Storage unavailable
    }
  }

  function buildStickyPlayerDOM() {
    if (document.getElementById('sticky-radio-player')) return;

    const ep = RADIO_EPISODES[currentIndex];
    const bar = document.createElement('aside');
    bar.id = 'sticky-radio-player';
    bar.className = 'sticky-radio-bar';
    bar.setAttribute('aria-label', '김쌤의 영웅 라디오 고정 재생기');

    bar.innerHTML = `
      <div class="radio-bar-inner">
        <div class="radio-info">
          <div class="radio-live-badge">
            <span class="radio-live-dot" id="radio-live-dot"></span>
            <span id="radio-status-label">📻 김쌤의 영웅 라디오 (화면의 ▶ 버튼을 누르면 바로 소리가 납니다)</span>
          </div>
          <div class="radio-track-title" id="radio-current-title">${ep.title}</div>
          <div class="radio-wifi-notice">💡 Wi-Fi(와이파이) 환경에서 들으시면 데이터 요금이 전혀 나가지 않습니다.</div>
        </div>
        <div class="radio-controls">
          <button type="button" class="btn-radio-play" id="btn-radio-toggle" aria-label="라디오 방송 재생 및 일시정지">
            <span aria-hidden="true" id="radio-play-icon">▶</span>
            <span id="radio-play-text">방송 듣기</span>
          </button>
          <button type="button" class="btn-radio-secondary" id="btn-radio-next" aria-label="다음 라디오 사연 듣기">
            <span>다음 편 ⏭</span>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(bar);
  }

  function updatePlayerUI() {
    const ep = RADIO_EPISODES[currentIndex];
    const titleEl = document.getElementById('radio-current-title');
    const statusEl = document.getElementById('radio-status-label');
    const playIcon = document.getElementById('radio-play-icon');
    const playText = document.getElementById('radio-play-text');
    const toggleBtn = document.getElementById('btn-radio-toggle');
    const mainEmbed = document.getElementById('main-youtube-embed');
    const mainTitle = document.getElementById('main-youtube-title');

    if (titleEl) {
      titleEl.textContent = `${ep.title} (${ep.duration} · 배경곡: ${ep.song})`;
    }
    if (mainTitle) {
      mainTitle.textContent = `📺 현재 선택된 방송: ${ep.title} (${ep.duration})`;
    }

    if (isPlaying) {
      if (statusEl) statusEl.textContent = '🔴 지금 방송 중 — @김쌤의영웅라디오';
      if (playIcon) playIcon.textContent = '⏸';
      if (playText) playText.textContent = '일시정지';
      if (toggleBtn) toggleBtn.classList.add('playing');
      if (mainEmbed) {
        const targetSrc = `https://www.youtube.com/embed/${ep.videoId}?autoplay=1&playsinline=1&rel=0`;
        if (mainEmbed.getAttribute('src') !== targetSrc) {
          mainEmbed.setAttribute('src', targetSrc);
        }
      }
    } else {
      if (statusEl) statusEl.textContent = '📻 김쌤의 영웅 라디오 (▶ 방송 듣기를 누르세요)';
      if (playIcon) playIcon.textContent = '▶';
      if (playText) playText.textContent = '방송 듣기';
      if (toggleBtn) toggleBtn.classList.remove('playing');
      if (mainEmbed && !mainEmbed.getAttribute('src')) {
        mainEmbed.setAttribute('src', `https://www.youtube.com/embed/${ep.videoId}?playsinline=1&rel=0`);
      }
    }
  }

  function focusVisibleEmbed() {
    const mainEmbed = document.getElementById('main-youtube-embed');
    if (mainEmbed) {
      mainEmbed.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function togglePlay() {
    isPlaying = !isPlaying;
    saveState();
    updatePlayerUI();
    if (isPlaying) {
      focusVisibleEmbed();
    }
  }

  function nextEpisode() {
    currentIndex = (currentIndex + 1) % RADIO_EPISODES.length;
    isPlaying = true;
    saveState();
    updatePlayerUI();
    focusVisibleEmbed();
  }

  function playEpisodeByIndex(idx) {
    if (idx >= 0 && idx < RADIO_EPISODES.length) {
      currentIndex = idx;
      isPlaying = true;
      saveState();
      updatePlayerUI();
      focusVisibleEmbed();
    }
  }

  function playVideoById(videoId, customTitle) {
    const mainEmbed = document.getElementById('main-youtube-embed');
    const mainTitle = document.getElementById('main-youtube-title');
    if (mainEmbed && videoId) {
      mainEmbed.setAttribute('src', `https://www.youtube.com/embed/${videoId}?autoplay=1&playsinline=1&rel=0`);
      mainEmbed.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    if (mainTitle && customTitle) {
      mainTitle.textContent = `🎵 지금 재생 중: ${customTitle}`;
    }
  }

  function initRadioPlayer() {
    loadState();
    const deepLinked = applyQueryDeepLink();
    buildStickyPlayerDOM();
    updatePlayerUI();
    if (deepLinked) {
      focusVisibleEmbed();
    }

    const toggleBtn = document.getElementById('btn-radio-toggle');
    const nextBtn = document.getElementById('btn-radio-next');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', togglePlay);
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', nextEpisode);
    }

    const episodeButtons = document.querySelectorAll('[data-play-episode]');
    episodeButtons.forEach((btn) => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const epIdx = parseInt(this.getAttribute('data-play-episode'), 10);
        if (!isNaN(epIdx)) {
          playEpisodeByIndex(epIdx);
        }
      });
    });

    const videoButtons = document.querySelectorAll('[data-play-videoid]');
    videoButtons.forEach((btn) => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const vid = this.getAttribute('data-play-videoid');
        const vtitle = this.getAttribute('data-play-title') || '';
        if (vid) {
          playVideoById(vid, vtitle);
        }
      });
    });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initRadioPlayer);
    } else {
      initRadioPlayer();
    }
  }

  if (typeof window !== 'undefined') {
    window.ParadiseRadio = {
      episodes: RADIO_EPISODES,
      togglePlay: togglePlay,
      nextEpisode: nextEpisode,
      playEpisode: playEpisodeByIndex,
      playVideoById: playVideoById,
      applyQueryDeepLink: applyQueryDeepLink
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      RADIO_EPISODES
    };
  }
})();
