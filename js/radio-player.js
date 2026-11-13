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

  function ensureMiniRadioDrawer() {
    let drawer = document.getElementById('sticky-radio-mini-drawer');
    if (!drawer) {
      drawer = document.createElement('div');
      drawer.id = 'sticky-radio-mini-drawer';
      drawer.className = 'sticky-radio-mini-drawer';
      drawer.setAttribute('aria-label', '김쌤의 영웅 라디오 미니 방송창');
      drawer.innerHTML = `
        <div class="sticky-radio-mini-head">
          <span id="sticky-mini-drawer-label">🔴 김쌤의 영웅 라디오 방송 중</span>
          <button type="button" class="btn-mini-drawer-collapse" id="btn-mini-drawer-collapse">화면 접기 ▾</button>
        </div>
        <div class="sticky-radio-mini-frame">
          <iframe id="sticky-youtube-embed" title="김쌤의 영웅 라디오 실시간 재생기" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
        </div>
      `;
      document.body.appendChild(drawer);

      const collapseBtn = drawer.querySelector('#btn-mini-drawer-collapse');
      if (collapseBtn) {
        collapseBtn.addEventListener('click', () => {
          const minimized = drawer.classList.toggle('minimized');
          collapseBtn.textContent = minimized ? '화면 펴기 ▴' : '화면 접기 ▾';
        });
      }

      const miniIframe = drawer.querySelector('#sticky-youtube-embed');
      if (miniIframe) {
        miniIframe.addEventListener('load', () => {
          subscribeYoutubeEndedEvent(miniIframe);
        });
      }
    }
    return drawer;
  }

  function subscribeYoutubeEndedEvent(iframeEl) {
    try {
      if (!iframeEl || !iframeEl.contentWindow) return;
      iframeEl.contentWindow.postMessage(JSON.stringify({ event: 'listening', id: iframeEl.id || 'yt-radio' }), '*');
      iframeEl.contentWindow.postMessage(JSON.stringify({ event: 'command', func: 'addEventListener', args: ['onStateChange'] }), '*');
    } catch (e) {
      // Ignore cross-origin handshake error
    }
  }

  function buildYoutubeEmbedUrl(videoId, autoplay) {
    const autoFlag = autoplay ? '1' : '0';
    return `https://www.youtube.com/embed/${videoId}?autoplay=${autoFlag}&playsinline=1&rel=0&enablejsapi=1`;
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
        const targetSrc = buildYoutubeEmbedUrl(ep.videoId, true);
        if (mainEmbed.getAttribute('src') !== targetSrc) {
          mainEmbed.setAttribute('src', targetSrc);
        }
      } else if (typeof document !== 'undefined') {
        const drawer = ensureMiniRadioDrawer();
        drawer.classList.add('open');
        const miniLabel = document.getElementById('sticky-mini-drawer-label');
        if (miniLabel) miniLabel.textContent = `🔴 ${ep.id.toUpperCase()} 방송 중`;
        const miniEmbed = document.getElementById('sticky-youtube-embed');
        const targetSrc = buildYoutubeEmbedUrl(ep.videoId, true);
        if (miniEmbed && miniEmbed.getAttribute('src') !== targetSrc) {
          miniEmbed.setAttribute('src', targetSrc);
        }
      }
    } else {
      if (statusEl) statusEl.textContent = '📻 김쌤의 영웅 라디오 (▶ 방송 듣기를 누르세요)';
      if (playIcon) playIcon.textContent = '▶';
      if (playText) playText.textContent = '방송 듣기';
      if (toggleBtn) toggleBtn.classList.remove('playing');
      if (mainEmbed) {
        const idleSrc = buildYoutubeEmbedUrl(ep.videoId, false);
        if (!mainEmbed.getAttribute('src') || (mainEmbed.getAttribute('src') || '').includes('autoplay=1')) {
          mainEmbed.setAttribute('src', idleSrc);
        }
      }
      const drawer = typeof document !== 'undefined' ? document.getElementById('sticky-radio-mini-drawer') : null;
      if (drawer) {
        drawer.classList.remove('open');
        const miniEmbed = document.getElementById('sticky-youtube-embed');
        if (miniEmbed && miniEmbed.getAttribute('src')) {
          miniEmbed.setAttribute('src', 'about:blank');
        }
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
      mainEmbed.setAttribute('src', buildYoutubeEmbedUrl(videoId, true));
      mainEmbed.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (videoId && typeof document !== 'undefined') {
      isPlaying = true;
      const drawer = ensureMiniRadioDrawer();
      drawer.classList.add('open');
      const miniLabel = document.getElementById('sticky-mini-drawer-label');
      if (miniLabel && customTitle) miniLabel.textContent = `🎵 ${customTitle}`;
      const miniEmbed = document.getElementById('sticky-youtube-embed');
      if (miniEmbed) miniEmbed.setAttribute('src', buildYoutubeEmbedUrl(videoId, true));
    }
    if (mainTitle && customTitle) {
      mainTitle.textContent = `🎵 지금 재생 중: ${customTitle}`;
    }
  }

  function initRadioPlayer() {
    loadState();
    const deepLinked = applyQueryDeepLink();
    buildStickyPlayerDOM();
    const mainEmbed = document.getElementById('main-youtube-embed');
    if (mainEmbed) {
      mainEmbed.addEventListener('load', () => subscribeYoutubeEndedEvent(mainEmbed));
    }
    if (typeof window !== 'undefined') {
      window.addEventListener('message', (ev) => {
        try {
          if (!ev || typeof ev.data !== 'string') return;
          if (!ev.origin || !/youtube\.com|youtube-nocookie\.com/i.test(ev.origin)) return;
          const payload = JSON.parse(ev.data);
          if (
            (payload.event === 'onStateChange' && payload.info === 0) ||
            (payload.event === 'infoDelivery' && payload.info && payload.info.playerState === 0)
          ) {
            nextEpisode();
          }
        } catch (e) {
          // Ignore non-JSON messages
        }
      });
    }
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
