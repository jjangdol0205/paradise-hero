/**
 * radio-player.js
 * @김쌤의영웅라디오 1-클릭 연속 재생 플레이어 & 본문 16:9 유튜브 공식 IFrame API 플레이어 연동 모듈
 * - 모바일(iOS/안드로이드) 무음 차단 문제를 100% 해결하기 위해 본문 상단 16:9 보이는 유튜브 플레이어(#main-youtube-embed)와
 *   화면 하단 고정 바(Sticky Bar)를 동시 연동합니다.
 * - ?ep=1~5 딥링크 파라미터 자동 선택·재생을 지원합니다.
 * - 공식 YouTube IFrame Player API (https://www.youtube.com/iframe_api, enablejsapi=1)를 통해
 *   실제 재생 상태(player.getPlayerState() === 1 / YT.PlayerState.PLAYING)인 동안만 1초 주기로 누적 시청 시간을 계측하여
 *   330초(5분 30초) 도달 시 세션당 1회 hero_paradisekr radio_5m30s 비콘을 전송합니다.
 */

(function () {
  'use strict';

  const RADIO_EPISODES = [
    {
      id: 'ep01',
      title: '1화: [사연라디오] 내 인생의 사계절을 울린 황영웅의 목소리 — 파라다이스에 찾아온 봄',
      song: '당신 편 · 꽃구경',
      duration: '11:45',
      videoId: 'WOPZLb6S1xI'
    },
    {
      id: 'ep02',
      title: '2화: [심야사연극] 앞치마는 잠시 내려놓으세요 — 황영웅이 파라다이스에 보낸 사연 열차',
      song: '해바라기 · 함께해요',
      duration: '12:33',
      videoId: 'M26BNE0bSz8'
    },
    {
      id: 'ep03',
      title: '3화: [감동다큐] 텅 빈 연습실의 눈물과 파라다이스가 함께 만든 두 번째 기적',
      song: '비상 · 인생아 고마웠다',
      duration: '12:27',
      videoId: 'fqYTY_NZ3Uw'
    },
    {
      id: 'ep04',
      title: '4화: [인생사연] 낡은 구두와 초록빛 응원봉 — 황영웅이 전하는 진심의 이야기',
      song: '인사동 찻집 · 당신꽃',
      duration: '14:14',
      videoId: 'wb9IV7eD1p0'
    },
    {
      id: 'ep05',
      title: '5화: [명곡해설] 새벽 4시 녹음실, 모두를 울려버린 황영웅의 진심과 신곡 비하인드',
      song: '당신 편 · 가을, 그리움',
      duration: '16:59',
      videoId: 'nZhCCjhgSIE'
    }
  ];

  const STATE_KEY = 'paradise_radio_state_v3';
  const WATCH_ACCUM_KEY = 'hq_radio_accum_sec';
  const WATCH_BEACON_SENT_KEY = 'hq_radio_5m30s_sent';
  const WATCH_TARGET_SECONDS = 330;

  let currentIndex = 0;
  let isPlaying = false;

  let ytMainPlayer = null;
  let ytMainPlayerReady = false;
  let ytMainLoadedVideoId = '';

  let ytMiniPlayer = null;
  let ytMiniPlayerReady = false;
  let ytMiniLoadedVideoId = '';

  let accumulatedPlaySeconds = 0;
  let watchIntervalId = null;

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
      const savedAccum = parseInt(sessionStorage.getItem(WATCH_ACCUM_KEY) || '0', 10);
      if (!isNaN(savedAccum) && savedAccum > 0) {
        accumulatedPlaySeconds = savedAccum;
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

  function fireRadio5m30sBeaconOnce() {
    try {
      if (typeof sessionStorage !== 'undefined' && sessionStorage.getItem(WATCH_BEACON_SENT_KEY) === '1') {
        return;
      }
      if (typeof sessionStorage !== 'undefined') {
        sessionStorage.setItem(WATCH_BEACON_SENT_KEY, '1');
      }
      if (typeof fetch !== 'function' || typeof navigator === 'undefined') return;
      const ua = navigator.userAgent || '';
      if (navigator.webdriver || /jsdom|bot|crawl|spider|slurp|headless|lighthouse|gtmetrix|pingdom|uptimerobot|python|curl|node|axios/i.test(ua)) {
        return;
      }
      const host = (typeof window !== 'undefined' && window.location && window.location.hostname) || '';
      if (!host || host === 'localhost' || host === '127.0.0.1') return;

      const kstDate = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/radio_5m30s_' + kstDate, { mode: 'cors', keepalive: true }).catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/radio_5m30s_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function isPlayerActivelyPlaying(player) {
    if (!player || typeof player.getPlayerState !== 'function') return false;
    try {
      const playingConst = (typeof window !== 'undefined' && window.YT && window.YT.PlayerState && typeof window.YT.PlayerState.PLAYING === 'number')
        ? window.YT.PlayerState.PLAYING
        : 1;
      return player.getPlayerState() === playingConst;
    } catch (e) {
      return false;
    }
  }

  function ensureRealPlaybackWatchTimer() {
    if (watchIntervalId !== null || typeof window === 'undefined') return;
    watchIntervalId = window.setInterval(function () {
      if (isPlayerActivelyPlaying(ytMainPlayer) || isPlayerActivelyPlaying(ytMiniPlayer)) {
        accumulatedPlaySeconds += 1;
        try {
          sessionStorage.setItem(WATCH_ACCUM_KEY, String(accumulatedPlaySeconds));
        } catch (e) {}
        if (accumulatedPlaySeconds >= WATCH_TARGET_SECONDS) {
          fireRadio5m30sBeaconOnce();
        }
      }
    }, 1000);
  }

  function loadYouTubeIframeApiScript() {
    if (typeof document === 'undefined' || typeof window === 'undefined') return;
    if (window.YT && typeof window.YT.Player === 'function') {
      bindYouTubePlayers();
      return;
    }
    const prevCallback = window.onYouTubeIframeAPIReady;
    if (!window.__paradiseYtCallbackHooked) {
      window.__paradiseYtCallbackHooked = true;
      window.onYouTubeIframeAPIReady = function () {
        if (typeof prevCallback === 'function') {
          try { prevCallback(); } catch (e) {}
        }
        bindYouTubePlayers();
      };
    }
    const existingScript = document.querySelector('script[src*="youtube.com/iframe_api"]');
    if (!existingScript && document.head) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      tag.async = true;
      document.head.appendChild(tag);
    }
  }

  function extractVideoIdFromSrc(src) {
    const m = String(src || '').match(/\/embed\/([a-zA-Z0-9_-]{11})/);
    return m ? m[1] : '';
  }

  function syncUiButtonsOnly(playingState) {
    const statusEl = document.getElementById('radio-status-label');
    const playIcon = document.getElementById('radio-play-icon');
    const playText = document.getElementById('radio-play-text');
    const toggleBtn = document.getElementById('btn-radio-toggle');

    if (playingState) {
      if (statusEl) statusEl.textContent = '🔴 지금 방송 중 — @김쌤의영웅라디오';
      if (playIcon) playIcon.textContent = '⏸';
      if (playText) playText.textContent = '일시정지';
      if (toggleBtn) toggleBtn.classList.add('playing');
    } else {
      if (statusEl) statusEl.textContent = '📻 김쌤의 영웅 라디오 (▶ 방송 듣기를 누르세요)';
      if (playIcon) playIcon.textContent = '▶';
      if (playText) playText.textContent = '방송 듣기';
      if (toggleBtn) toggleBtn.classList.remove('playing');
    }
  }

  function bindYouTubePlayers() {
    if (typeof window === 'undefined' || !window.YT || typeof window.YT.Player !== 'function') return;

    const mainEl = document.getElementById('main-youtube-embed');
    if (mainEl && !ytMainPlayer) {
      ytMainLoadedVideoId = extractVideoIdFromSrc(mainEl.getAttribute('src')) || RADIO_EPISODES[currentIndex].videoId;
      try {
        ytMainPlayer = new window.YT.Player('main-youtube-embed', {
          events: {
            onReady: function () {
              ytMainPlayerReady = true;
              ensureRealPlaybackWatchTimer();
              if (isPlaying) {
                const targetVid = RADIO_EPISODES[currentIndex].videoId;
                if (ytMainLoadedVideoId !== targetVid && typeof ytMainPlayer.loadVideoById === 'function') {
                  ytMainLoadedVideoId = targetVid;
                  ytMainPlayer.loadVideoById(targetVid);
                } else if (typeof ytMainPlayer.playVideo === 'function') {
                  ytMainPlayer.playVideo();
                }
              }
            },
            onStateChange: function (event) {
              const playingState = (window.YT && window.YT.PlayerState) ? window.YT.PlayerState.PLAYING : 1;
              const pausedState = (window.YT && window.YT.PlayerState) ? window.YT.PlayerState.PAUSED : 2;
              const endedState = (window.YT && window.YT.PlayerState) ? window.YT.PlayerState.ENDED : 0;

              if (event.data === playingState) {
                isPlaying = true;
                saveState();
                syncUiButtonsOnly(true);
                ensureRealPlaybackWatchTimer();
              } else if (event.data === pausedState) {
                isPlaying = false;
                saveState();
                syncUiButtonsOnly(false);
              } else if (event.data === endedState) {
                nextEpisode();
              }
            }
          }
        });
      } catch (e) {
        ytMainPlayer = null;
      }
    }

    const miniEl = document.getElementById('sticky-youtube-embed');
    if (miniEl && !ytMiniPlayer && miniEl.getAttribute('src') && miniEl.getAttribute('src') !== 'about:blank') {
      ytMiniLoadedVideoId = extractVideoIdFromSrc(miniEl.getAttribute('src'));
      try {
        ytMiniPlayer = new window.YT.Player('sticky-youtube-embed', {
          events: {
            onReady: function () {
              ytMiniPlayerReady = true;
              ensureRealPlaybackWatchTimer();
            },
            onStateChange: function (event) {
              const playingState = (window.YT && window.YT.PlayerState) ? window.YT.PlayerState.PLAYING : 1;
              const endedState = (window.YT && window.YT.PlayerState) ? window.YT.PlayerState.ENDED : 0;
              if (event.data === playingState) {
                ensureRealPlaybackWatchTimer();
              } else if (event.data === endedState) {
                nextEpisode();
              }
            }
          }
        });
      } catch (e) {
        ytMiniPlayer = null;
      }
    }
  }

  function ensureStickyPlayerCriticalStyles() {
    if (typeof document === 'undefined' || !document.head) return;
    if (document.getElementById('paradise-radio-critical-css')) return;
    const style = document.createElement('style');
    style.id = 'paradise-radio-critical-css';
    style.textContent = `
      .sticky-radio-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; background: #0E2820; color: #FFFFFF; border-top: 3px solid #D4AF37; padding: 10px 16px; box-shadow: 0 -4px 20px rgba(0,0,0,0.35); }
      .btn-radio-play, .btn-radio-secondary, #btn-radio-toggle, #btn-radio-next, #btn-radio-prev, .btn-mini-drawer-collapse, #btn-mini-drawer-collapse {
        min-height: 60px !important; padding: 12px 18px !important; font-size: 20px !important; font-weight: 800 !important; border-radius: 14px !important;
        display: inline-flex !important; align-items: center !important; justify-content: center !important; gap: 8px !important; cursor: pointer !important;
      }
      @media (max-width: 640px) {
        .sticky-radio-bar { padding: 8px 12px 10px; }
        .radio-controls { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; width: 100%; }
        #btn-radio-toggle, #btn-radio-next { width: 100%; min-width: 0; padding: 12px 10px !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function buildStickyPlayerDOM() {
    ensureStickyPlayerCriticalStyles();
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
      if (typeof window !== 'undefined' && window.innerWidth <= 640) {
        drawer.classList.add('minimized');
        if (collapseBtn) collapseBtn.textContent = '화면 펴기 ▴';
      }
      if (collapseBtn) {
        collapseBtn.addEventListener('click', () => {
          const minimized = drawer.classList.toggle('minimized');
          collapseBtn.textContent = minimized ? '화면 펴기 ▴' : '화면 접기 ▾';
        });
      }

      const miniIframe = drawer.querySelector('#sticky-youtube-embed');
      if (miniIframe) {
        miniIframe.addEventListener('load', () => {
          bindYouTubePlayers();
        });
      }
    }
    return drawer;
  }

  function buildYoutubeEmbedUrl(videoId, autoplay) {
    const autoFlag = autoplay ? '1' : '0';
    let originParam = '';
    if (typeof window !== 'undefined' && window.location && /^https?:/i.test(window.location.protocol) && window.location.origin) {
      originParam = '&origin=' + encodeURIComponent(window.location.origin);
    }
    return `https://www.youtube.com/embed/${videoId}?autoplay=${autoFlag}&playsinline=1&rel=0&enablejsapi=1${originParam}`;
  }

  function updatePlayerUI() {
    const ep = RADIO_EPISODES[currentIndex];
    const titleEl = document.getElementById('radio-current-title');
    const mainEmbed = document.getElementById('main-youtube-embed');
    const mainTitle = document.getElementById('main-youtube-title');

    if (titleEl) {
      titleEl.textContent = `${ep.title} (${ep.duration} · 배경곡: ${ep.song})`;
    }
    if (mainTitle) {
      mainTitle.textContent = `📺 현재 선택된 방송: ${ep.title} (${ep.duration})`;
    }

    syncUiButtonsOnly(isPlaying);

    if (isPlaying) {
      if (mainEmbed) {
        if (ytMainPlayerReady && ytMainPlayer && typeof ytMainPlayer.loadVideoById === 'function') {
          if (ytMainLoadedVideoId !== ep.videoId) {
            ytMainLoadedVideoId = ep.videoId;
            ytMainPlayer.loadVideoById(ep.videoId);
          } else if (typeof ytMainPlayer.playVideo === 'function') {
            ytMainPlayer.playVideo();
          }
        } else {
          const targetSrc = buildYoutubeEmbedUrl(ep.videoId, true);
          if (mainEmbed.getAttribute('src') !== targetSrc) {
            ytMainLoadedVideoId = ep.videoId;
            mainEmbed.setAttribute('src', targetSrc);
          }
        }
      } else if (typeof document !== 'undefined') {
        const drawer = ensureMiniRadioDrawer();
        drawer.classList.add('open');
        const miniLabel = document.getElementById('sticky-mini-drawer-label');
        if (miniLabel) miniLabel.textContent = `🔴 ${ep.id.toUpperCase()} 방송 중`;
        const miniEmbed = document.getElementById('sticky-youtube-embed');
        if (ytMiniPlayerReady && ytMiniPlayer && typeof ytMiniPlayer.loadVideoById === 'function') {
          if (ytMiniLoadedVideoId !== ep.videoId) {
            ytMiniLoadedVideoId = ep.videoId;
            ytMiniPlayer.loadVideoById(ep.videoId);
          } else if (typeof ytMiniPlayer.playVideo === 'function') {
            ytMiniPlayer.playVideo();
          }
        } else if (miniEmbed) {
          const targetSrc = buildYoutubeEmbedUrl(ep.videoId, true);
          if (miniEmbed.getAttribute('src') !== targetSrc) {
            ytMiniLoadedVideoId = ep.videoId;
            miniEmbed.setAttribute('src', targetSrc);
          }
        }
      }
    } else {
      if (mainEmbed) {
        if (ytMainPlayerReady && ytMainPlayer && typeof ytMainPlayer.pauseVideo === 'function') {
          ytMainPlayer.pauseVideo();
        } else {
          const idleSrc = buildYoutubeEmbedUrl(ep.videoId, false);
          if (!mainEmbed.getAttribute('src') || (mainEmbed.getAttribute('src') || '').includes('autoplay=1')) {
            ytMainLoadedVideoId = ep.videoId;
            mainEmbed.setAttribute('src', idleSrc);
          }
        }
      }
      const drawer = typeof document !== 'undefined' ? document.getElementById('sticky-radio-mini-drawer') : null;
      if (drawer) {
        drawer.classList.remove('open');
        if (ytMiniPlayerReady && ytMiniPlayer && typeof ytMiniPlayer.pauseVideo === 'function') {
          ytMiniPlayer.pauseVideo();
        } else {
          const miniEmbed = document.getElementById('sticky-youtube-embed');
          if (miniEmbed && miniEmbed.getAttribute('src')) {
            miniEmbed.setAttribute('src', 'about:blank');
          }
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
      isPlaying = true;
      syncUiButtonsOnly(true);
      if (ytMainPlayerReady && ytMainPlayer && typeof ytMainPlayer.loadVideoById === 'function') {
        ytMainLoadedVideoId = videoId;
        ytMainPlayer.loadVideoById(videoId);
      } else {
        ytMainLoadedVideoId = videoId;
        mainEmbed.setAttribute('src', buildYoutubeEmbedUrl(videoId, true));
      }
      mainEmbed.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (videoId && typeof document !== 'undefined') {
      isPlaying = true;
      syncUiButtonsOnly(true);
      const drawer = ensureMiniRadioDrawer();
      drawer.classList.add('open');
      const miniLabel = document.getElementById('sticky-mini-drawer-label');
      if (miniLabel && customTitle) miniLabel.textContent = `🎵 ${customTitle}`;
      const miniEmbed = document.getElementById('sticky-youtube-embed');
      if (ytMiniPlayerReady && ytMiniPlayer && typeof ytMiniPlayer.loadVideoById === 'function') {
        ytMiniLoadedVideoId = videoId;
        ytMiniPlayer.loadVideoById(videoId);
      } else if (miniEmbed) {
        ytMiniLoadedVideoId = videoId;
        miniEmbed.setAttribute('src', buildYoutubeEmbedUrl(videoId, true));
      }
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
    loadYouTubeIframeApiScript();
    ensureRealPlaybackWatchTimer();

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

    const heroRadioCta = document.getElementById('btn-hero-radio-now');
    if (heroRadioCta) {
      heroRadioCta.addEventListener('click', function (e) {
        const radioSection = document.getElementById('hero-radio-section');
        if (radioSection) {
          e.preventDefault();
          playEpisodeByIndex(currentIndex || 0);
          radioSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          radioSection.classList.add('radio-highlight-pulse');
          setTimeout(function () {
            radioSection.classList.remove('radio-highlight-pulse');
          }, 2600);
        }
      });
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
      applyQueryDeepLink: applyQueryDeepLink,
      getAccumulatedPlaySeconds: function () { return accumulatedPlaySeconds; }
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      RADIO_EPISODES
    };
  }
})();
