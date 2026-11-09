/**
 * radio-player.js
 * 5070 시니어 전용 하단 상시 고정 [김쌤의 영웅 라디오] 연속 재생 플레이어
 * - 1-클릭 대형 재생/일시정지 버튼 (직경 58px+)
 * - 유튜브 공식 영상/오디오 스트림 연동 (Zero Raw MP3 저작권 100% 준수)
 * - 음량 조절 및 무음(Mute) 토글
 * - 와이파이(Wi-Fi) 권장 안심 툴팁
 */

(function () {
  'use strict';

  // 김쌤의 영웅 라디오 에피소드 카탈로그 (공식 유튜브 연동 메타데이터)
  const EPISODES = [
    {
      id: 1,
      title: '1화: 어머니, 제가 당신의 편이 되어드릴게요 (대표곡: 당신 편)',
      youtubeId: 'qN4q0M-rRnk', // 공식 대표 스트림 임베드 ID
      duration: '15:20',
      date: '2026-11-09'
    },
    {
      id: 2,
      title: '2화: 가을 바람 타고 온 꽃구경의 추억 (대표곡: 꽃구경)',
      youtubeId: 'X7kU8p_09aE',
      duration: '16:45',
      date: '2026-11-05'
    },
    {
      id: 3,
      title: '3화: 인사동 찻집에서 나눈 어머니의 눈물과 위로',
      youtubeId: 'L8pQ1k_54aB',
      duration: '17:10',
      date: '2026-11-02'
    },
    {
      id: 4,
      title: '4화: 당신꽃으로 활짝 피어난 우리들의 황금빛 인생',
      youtubeId: 'P3oW7m_89cD',
      duration: '15:50',
      date: '2026-10-28'
    }
  ];

  let currentEpisodeIndex = 0;
  let isPlaying = false;
  let isMuted = false;
  let currentVolume = 80;
  let youtubePlayerIframe = null;

  /**
   * 플레이어 UI 렌더링 및 DOM 준비
   */
  function initPlayerUI() {
    let playerContainer = document.getElementById('sticky-radio-player');
    if (!playerContainer) {
      playerContainer = document.createElement('div');
      playerContainer.id = 'sticky-radio-player';
      playerContainer.className = 'sticky-radio-player';
      playerContainer.setAttribute('role', 'region');
      playerContainer.setAttribute('aria-label', '김쌤의 영웅 라디오 하단 오디오 플레이어');

      playerContainer.innerHTML = `
        <div class="player-inner">
          <div class="player-info">
            <div class="player-album-art" aria-hidden="true">📻</div>
            <div class="player-text-wrap">
              <div class="player-show-title">👑 김쌤의 영웅 라디오</div>
              <div class="player-episode-title" id="player-current-title">1화: 어머니, 제가 당신의 편이 되어드릴게요</div>
            </div>
          </div>

          <div class="player-controls">
            <!-- 58px 대형 재생/일시정지 버튼 -->
            <button type="button" class="btn-player-play" id="btn-player-toggle" aria-label="라디오 재생 시작">
              <span id="player-icon" aria-hidden="true">▶</span>
            </button>
            <span class="player-wifi-pill">📶 Wi-Fi 권장</span>
          </div>

          <div class="player-volume-wrap">
            <button type="button" class="btn-mute-toggle" id="btn-player-mute" aria-label="음소거 토글">
              <span id="mute-icon" aria-hidden="true">🔊</span>
            </button>
            <input type="range" class="volume-slider" id="player-volume-slider" min="0" max="100" value="80" aria-label="라디오 음량 조절">
          </div>
        </div>
        <!-- 유튜브 백그라운드 IFrame 컨테이너 (비노출 안전 스트리밍) -->
        <div id="youtube-audio-host" style="position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none;"></div>
      `;

      document.body.appendChild(playerContainer);
    }

    bindPlayerEvents();
    updatePlayerDisplay();
  }

  /**
   * 플레이어 이벤트 바인딩
   */
  function bindPlayerEvents() {
    const playBtn = document.getElementById('btn-player-toggle');
    const muteBtn = document.getElementById('btn-player-mute');
    const volumeSlider = document.getElementById('player-volume-slider');

    if (playBtn) {
      playBtn.addEventListener('click', togglePlay);
    }

    if (muteBtn) {
      muteBtn.addEventListener('click', toggleMute);
    }

    if (volumeSlider) {
      volumeSlider.addEventListener('input', (e) => {
        setVolume(parseInt(e.target.value, 10));
      });
    }

    // 외부 에피소드 재생 버튼 연동 (예: .btn-play-episode)
    document.addEventListener('click', (e) => {
      const target = e.target.closest('[data-play-episode]');
      if (target) {
        e.preventDefault();
        const epIndex = parseInt(target.getAttribute('data-play-episode'), 10);
        if (!isNaN(epIndex)) {
          playEpisode(epIndex);
        }
      }
    });
  }

  /**
   * 화면 표시 업데이트
   */
  function updatePlayerDisplay() {
    const titleEl = document.getElementById('player-current-title');
    const iconEl = document.getElementById('player-icon');
    const playBtn = document.getElementById('btn-player-toggle');

    if (titleEl && EPISODES[currentEpisodeIndex]) {
      titleEl.textContent = EPISODES[currentEpisodeIndex].title;
    }

    if (iconEl && playBtn) {
      if (isPlaying) {
        iconEl.textContent = '⏸';
        playBtn.setAttribute('aria-label', '라디오 일시정지');
        playBtn.style.backgroundColor = '#1B4D3E';
        playBtn.style.color = '#FFFFFF';
      } else {
        iconEl.textContent = '▶';
        playBtn.setAttribute('aria-label', '라디오 연속 재생 시작');
        playBtn.style.backgroundColor = '#D4AF37';
        playBtn.style.color = '#0E2820';
      }
    }
  }

  /**
   * 1-클릭 재생/일시정지 토글
   */
  function togglePlay() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  /**
   * 재생 실행
   */
  function play() {
    isPlaying = true;
    updatePlayerDisplay();
    ensureIframeLoaded(true);
    console.log(`[RadioPlayer] 재생 중: ${EPISODES[currentEpisodeIndex].title}`);
  }

  /**
   * 일시정지
   */
  function pause() {
    isPlaying = false;
    updatePlayerDisplay();
    if (youtubePlayerIframe && youtubePlayerIframe.contentWindow) {
      youtubePlayerIframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
    }
    console.log('[RadioPlayer] 일시정지됨');
  }

  /**
   * 특정 에피소드 선택 재생
   */
  function playEpisode(index) {
    if (index >= 0 && index < EPISODES.length) {
      currentEpisodeIndex = index;
      if (youtubePlayerIframe) {
        youtubePlayerIframe.remove();
        youtubePlayerIframe = null;
      }
      play();
    }
  }

  /**
   * 음소거 토글
   */
  function toggleMute() {
    isMuted = !isMuted;
    const muteIcon = document.getElementById('mute-icon');
    const muteBtn = document.getElementById('btn-player-mute');

    if (muteIcon && muteBtn) {
      if (isMuted) {
        muteIcon.textContent = '🔇';
        muteBtn.setAttribute('aria-label', '소리 켜기');
      } else {
        muteIcon.textContent = '🔊';
        muteBtn.setAttribute('aria-label', '소리 끄기');
      }
    }

    if (youtubePlayerIframe && youtubePlayerIframe.contentWindow) {
      const cmd = isMuted ? 'mute' : 'unMute';
      youtubePlayerIframe.contentWindow.postMessage(`{"event":"command","func":"${cmd}","args":""}`, '*');
    }
  }

  /**
   * 볼륨 조절
   */
  function setVolume(vol) {
    currentVolume = Math.max(0, Math.min(100, vol));
    if (youtubePlayerIframe && youtubePlayerIframe.contentWindow) {
      youtubePlayerIframe.contentWindow.postMessage(`{"event":"command","func":"setVolume","args":[${currentVolume}]}`, '*');
    }
  }

  /**
   * 유튜브 공식 영상 백그라운드 IFrame 로드
   */
  function ensureIframeLoaded(autoPlay = false) {
    const host = document.getElementById('youtube-audio-host');
    if (!host) return;

    const ep = EPISODES[currentEpisodeIndex];
    if (!youtubePlayerIframe) {
      youtubePlayerIframe = document.createElement('iframe');
      youtubePlayerIframe.id = 'yt-radio-iframe';
      youtubePlayerIframe.src = `https://www.youtube-nocookie.com/embed/${ep.youtubeId}?enablejsapi=1&autoplay=${autoPlay ? 1 : 0}&playsinline=1&rel=0`;
      youtubePlayerIframe.title = '김쌤의 영웅 라디오 오디오 스트림';
      youtubePlayerIframe.allow = 'autoplay; encrypted-media';
      youtubePlayerIframe.style.width = '1px';
      youtubePlayerIframe.style.height = '1px';
      host.appendChild(youtubePlayerIframe);
    } else if (autoPlay && youtubePlayerIframe.contentWindow) {
      youtubePlayerIframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
    }
  }

  // 초기화
  document.addEventListener('DOMContentLoaded', initPlayerUI);

  // 전역 API 노출
  window.RadioPlayer = {
    play: play,
    pause: pause,
    togglePlay: togglePlay,
    playEpisode: playEpisode,
    toggleMute: toggleMute,
    setVolume: setVolume,
    getEpisodes: () => EPISODES.slice(),
    getCurrentEpisode: () => EPISODES[currentEpisodeIndex],
    isPlaying: () => isPlaying
  };
})();
