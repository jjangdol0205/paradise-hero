/**
 * radio-player.js
 * @김쌤의영웅라디오 & 전속 가상 트로트 가수 『백운호 (白雲湖)』 100% 오리지널 스튜디오 라디오 플레이어
 * - 실존 연예인 영상/음원 혼입 0건: 자체 제작된 백운호·김쌤 스튜디오 MP3 방송(assets/audio/baek_woon_ho_ep01~05.mp3)을
 *   광고 0초·인앱 브라우저 차단 0건으로 즉시 연속 재생합니다.
 * - 본문 상단 16:9 보이는 라디오 스튜디오(#main-youtube-embed)와 하단 58px 슬림 고정 바(#sticky-radio-player)를 1:1 동기화합니다.
 * - ?ep=1~5 딥링크 자동 선택 및 실제 오디오 재생 중(!audio.paused)일 때만 1초 주기로 누적 청취 시간을 계측하여
 *   330초(5분 30초) 도달 시 세션당 1회 hero_paradisekr radio_5m30s 비콘을 전송합니다.
 */

(function () {
  'use strict';

  const RADIO_EPISODES = [
    {
      id: 'ep01',
      title: '1곡 [완곡 02:45]: 백운호 타이틀곡 — 〈어머니의 봄날〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '어머니의 봄날 (완곡 02:45)',
      duration: '02:45',
      audioSrc: 'assets/audio/baek_woonho_01_mothers_spring.mp3',
      poster: 'assets/baek_woon_ho_main.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 타이틀곡 〈어머니의 봄날〉 — 찬 서리 내리던 새벽 부엌에, 보리차 끓이시던 고운 그 손길' },
        { at: 42, text: '🎶 어머니 내 어머니 이제 울지 마세요 · 모진 겨울 다 지나고 꽃이 핍니다' },
        { at: 90, text: '🎵 장터 길 찬 바람에 옷깃 여미며 내 이름 석 자조차 잊고 산 세월, 오늘 밤 내 가슴을 적시네' },
        { at: 120, text: '🎶 주름진 두 손 잡고 함께 걸어갈 어머니의 봄날이 오늘 피어납니다' }
      ]
    },
    {
      id: 'ep02',
      title: '2곡 [완곡 02:45]: 백운호 산책길 애창곡 — 〈백운호 연가〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '백운호 연가 (완곡 02:45)',
      duration: '02:45',
      audioSrc: 'assets/audio/baek_woonho_02_yeonga.mp3',
      poster: 'assets/characters/hero_style_02.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 대표곡 〈백운호 연가〉 — 흰 구름 쉬어 가는 고요한 호수에 노을빛 물결 따라 세월이 흐르네' },
        { at: 42, text: '🎶 쉬어 가세요 내 사람아 넓은 품 안에서 · 거친 바람 지나는 날 내가 막아 드리리' },
        { at: 90, text: '🎵 표현은 서툴러도 마음만은 진국인 무뚝뚝한 그대 손이 내 평생 버팀목' },
        { at: 120, text: '🎶 한낮보다 아름다운 우리의 금빛 노을 · 두 손 꼭 잡고 걷는 호숫가 연가여라' }
      ]
    },
    {
      id: 'ep03',
      title: '3곡 [완곡 02:47]: 백운호 저녁 위로곡 — 〈항구의 등불〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '항구의 등불 (완곡 02:47)',
      duration: '02:47',
      audioSrc: 'assets/audio/baek_woonho_03_harbor_light.mp3',
      poster: 'assets/characters/hero_style_03.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 저녁 위로곡 〈항구의 등불〉 — 밤안개 내려앉은 부둣가에 거친 파도 헤쳐 온 연락선이 쉬어가네' },
        { at: 42, text: '🎶 불을 켜라 항구의 등불 어두운 밤바다에 · 지친 어선 길 비추는 따뜻한 등대처럼' },
        { at: 90, text: '🎵 새벽 별 보며 나가 달빛 안고 돌아오던 굳은살 박인 손에 들려 있던 작은 봉투' },
        { at: 120, text: '🎶 이제는 닻을 내리고 편안히 쉬어 가세요 · 당신이 우리 집의 꺼지지 않는 등불이라' }
      ]
    },
    {
      id: 'ep04',
      title: '4곡 [완곡 02:46]: 백운호 희망 응원곡 — 〈다시 피는 동백꽃〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '다시 피는 동백꽃 (완곡 02:46)',
      duration: '02:46',
      audioSrc: 'assets/audio/baek_woonho_04_camellia.mp3',
      poster: 'assets/characters/hero_style_04.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 희망 응원곡 〈다시 피는 동백꽃〉 — 매서운 겨울바람 스쳐 가도 가지 끝에 붉게 맺힌 동백 꽃망울' },
        { at: 42, text: '🎶 활짝 피어나세요 다시 피는 동백꽃 · 당신의 인생 이 막 지금이 청춘입니다' },
        { at: 90, text: '🎵 지나온 모진 세월 훈장처럼 빛나고 웃음꽃 피어나는 오늘이 선물이라' },
        { at: 120, text: '🎶 고운 스카프 두르고 봄바람 마주하며 가벼운 발걸음으로 꽃길을 걸어가네' }
      ]
    },
    {
      id: 'ep05',
      title: '5곡 [완곡 02:46]: 백운호 향수 사모곡 — 〈고향역 첫차〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '고향역 첫차 (완곡 02:46)',
      duration: '02:46',
      audioSrc: 'assets/audio/baek_woonho_05_hometown_train.mp3',
      poster: 'assets/characters/hero_style_03.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 향수 사모곡 〈고향역 첫차〉 — 희미한 가로등 불 새벽 안개 정거장에 보리차 따뜻한 병 안겨 주시던 손' },
        { at: 42, text: '🎶 기적 소리 울리며 달려가는 고향역 첫차 · 차창 밖에 스쳐 가는 그리운 고향 산천아' },
        { at: 90, text: '🎵 삶은 달걀 두 알에 소금 종이 접어 넣고 막차 타면 추울세라 목도리 여며 주셨지' },
        { at: 120, text: '🎶 세월 지나 백발 되어 그 정거장 다시 서니 따스하던 어머니 손길 가슴 시리게 그립네' }
      ]
    },
    {
      id: 'ep06',
      title: '6곡 [완곡 02:49]: 백운호 황혼 세레나데 — 〈내 인생의 금빛 노을〉 (Lyria 3.5 스튜디오 정규 음원)',
      song: '내 인생의 금빛 노을 (완곡 02:49)',
      duration: '02:49',
      audioSrc: 'assets/audio/baek_woonho_06_golden_sunset.mp3',
      poster: 'assets/characters/hero_style_05.png',
      captions: [
        { at: 0, text: '🎙️ 백운호 황혼 세레나데 〈내 인생의 금빛 노을〉 — 한낮의 뜨거운 해 서산 너머 기울어 갈 때 온 하늘 물들이는 금빛 노을아' },
        { at: 42, text: '🎶 아름다워라 내 인생의 눈부신 금빛 노을 · 수고했다 내 어깨야 참 잘 살아왔구나' },
        { at: 90, text: '🎵 은빛 머리칼 위에 저녁 햇살 내려앉으면 주름진 눈가에도 따뜻한 미소 번지네' },
        { at: 120, text: '🎶 나란히 발맞추어 저녁 산책 걸어가는 오늘 이 시간들이 하늘이 준 축복이라' }
      ]
    }
  ];

  const STATE_KEY = 'paradise_radio_state_v4';
  const WATCH_ACCUM_KEY = 'hq_radio_accum_sec';
  const WATCH_BEACON_SENT_KEY = 'hq_radio_5m30s_sent';
  const WATCH_TARGET_SECONDS = 330;

  // 정식 대표 롱폼 [1화] (18분 풀버전 — 유튜브 @김쌤의영웅라디오 업로드 즉시 youtubeVideoId 입력 시 자동 전환, 빈 값일 때는 깨진 iframe 0건 + 무광고 연속 스튜디오 스트림 즉시 재생)
  const FLAGSHIP_EP1_CONFIG = {
    title: '[1부·2부 연속 인생 사연 극장] 어머님 감동 사연 & 백운호 대표곡 연속 듣기 (다음 화 결말 예고 포함)',
    youtubeVideoId: 'O2_HvEfJoTw',
    channelUrl: 'https://www.youtube.com/@%EA%B9%80%EC%8C%A4%EC%9D%98%EC%98%81%EC%9B%85%EB%9D%BC%EB%94%94%EC%98%A4',
    poster: 'assets/ep1_flagship_thumb_1280x720.png',
    continuousTracks: [
      {
        label: '[1화 · 사연 1편] 대구 달서구 이순자 어머님의 봄날 편지',
        audioSrc: 'assets/audio/baek_woon_ho_ep01.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '💌 [사연 1편] 자식들 다 키워 보내고 텅 빈 새벽 부엌에서 맞이한 어머님의 봄날 편지가 흐르고 있습니다.'
      },
      {
        label: '[1화 · 대표곡 1곡 풀버전] 백운호 — 〈어머니의 봄날〉',
        audioSrc: 'assets/audio/baek_woonho_debut_sample.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '🎵 [대표곡 1곡 풀버전] 백운호 — 〈어머니의 봄날〉 (찬 서리 내리던 새벽 부엌에, 보리차 끓이시던 고운 그 손길)'
      },
      {
        label: '[1화 · 사연 2편] 아버님이 챙겨두신 약봉지와 황혼의 산책',
        audioSrc: 'assets/audio/baek_woon_ho_ep02.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '💌 [사연 2편] 무뚝뚝하던 아버님이 어머님 건강을 챙기며 함께 걷는 따뜻한 저녁 사연입니다.'
      },
      {
        label: '[1화 · 대표곡 2곡 풀버전] 백운호 — 〈백운호 연가〉',
        audioSrc: 'assets/audio/baek_woonho_yeonga_full.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '🎵 [대표곡 2곡 풀버전] 백운호 — 〈백운호 연가〉 (흰 구름 쉬어 가는 고요한 백운호에, 노을빛 물결 따라)'
      },
      {
        label: '[1화 · 건강 안부 쉼표] 나들이 무릎·목 보온 & 세월의 응원',
        audioSrc: 'assets/audio/baek_woon_ho_ep03.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '💚 [김쌤의 건강 쉼표] 외출·공연 시 스카프 보온과 발목 10번 당기기로 무릎 건강을 꼭 챙기세요.'
      },
      {
        label: '[1화 · 대표곡 3곡 풀버전] 백운호 — 〈다시 피는 동백꽃〉',
        audioSrc: 'assets/audio/baek_woonho_camellia_full.mp3',
        poster: 'assets/ep1_flagship_thumb_1280x720.png',
        caption: '🎵 [대표곡 3곡 풀버전] 백운호 — 〈다시 피는 동백꽃〉 (매서운 겨울바람 이겨내고 활짝 피어나는 인생 2막)'
      }
    ]
  };

  let currentIndex = 0;
  let isPlaying = false;
  let customBannerTitle = '';
  let flagshipQueueActive = false;
  let flagshipQueueIdx = 0;
  let accumulatedPlaySeconds = 0;
  let watchIntervalId = null;

  function formatSec(sec) {
    if (!isFinite(sec) || sec < 0) return '00:00';
    const total = Math.floor(sec);
    const m = String(Math.floor(total / 60)).padStart(2, '0');
    const s = String(total % 60).padStart(2, '0');
    return m + ':' + s;
  }

  function loadState() {
    try {
      const saved = sessionStorage.getItem(STATE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.index === 'number' && parsed.index >= 0 && parsed.index < RADIO_EPISODES.length) {
          currentIndex = parsed.index;
        }
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
          saveState();
          return true;
        }
      }
    } catch (e) {}
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
    } catch (e) {}
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
      if (typeof window !== 'undefined' && typeof window.hitHeroBeacon === 'function') {
        window.hitHeroBeacon('radio_5m30s_' + kstDate);
      } else if (typeof window !== 'undefined' && window.DreamCompanyCRM && typeof window.DreamCompanyCRM.recordCommunityEvent === 'function') {
        window.DreamCompanyCRM.recordCommunityEvent('radio_5m30s', 'radio_5m30s_' + kstDate);
      }
    } catch (e) {}
  }

  function ensureStudioAudioElement() {
    if (typeof document === 'undefined') return null;
    let audio = document.getElementById('baek-studio-audio');
    if (!audio && document.body) {
      audio = document.createElement('audio');
      audio.id = 'baek-studio-audio';
      audio.preload = 'metadata';
      audio.src = RADIO_EPISODES[currentIndex].audioSrc;
      audio.style.display = 'none';
      document.body.appendChild(audio);
    }
    if (audio && !audio.__baekEventsBound) {
      audio.__baekEventsBound = true;
      audio.addEventListener('play', function () {
        isPlaying = true;
        saveState();
        syncUiState(true);
      });
      audio.addEventListener('pause', function () {
        if (!audio.ended) {
          isPlaying = false;
          saveState();
          syncUiState(false);
        }
      });
      audio.addEventListener('ended', function () {
        if (flagshipQueueActive) {
          advanceFlagshipEp1Queue();
        } else {
          nextEpisode();
        }
      });
      audio.addEventListener('timeupdate', function () {
        syncProgressAndCaptions(audio);
      });
      audio.addEventListener('loadedmetadata', function () {
        syncProgressAndCaptions(audio);
      });
    }
    return audio;
  }

  function syncProgressAndCaptions(audio) {
    if (!audio || typeof document === 'undefined') return;
    const ep = RADIO_EPISODES[currentIndex];
    const cur = audio.currentTime || 0;
    const dur = isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 166;

    const timeEl = document.getElementById('studio-time-readout');
    if (timeEl) {
      timeEl.textContent = formatSec(cur) + ' / ' + formatSec(dur);
    }
    const scrubber = document.getElementById('studio-audio-scrubber');
    if (scrubber && !scrubber.__isDragging) {
      scrubber.value = String(Math.min(1000, Math.round((cur / dur) * 1000)));
    }
    const capEl = document.getElementById('studio-live-caption');
    if (flagshipQueueActive) {
      const fTrack = FLAGSHIP_EP1_CONFIG.continuousTracks[flagshipQueueIdx];
      if (capEl && fTrack && capEl.textContent !== fTrack.caption) {
        capEl.textContent = fTrack.caption;
      }
      return;
    }
    if (capEl && Array.isArray(ep.captions) && ep.captions.length > 0) {
      let activeText = ep.captions[0].text;
      for (let i = 0; i < ep.captions.length; i += 1) {
        if (cur >= ep.captions[i].at) {
          activeText = ep.captions[i].text;
        }
      }
      if (capEl.textContent !== activeText) {
        capEl.textContent = activeText;
      }
    }
  }

  function ensureRealPlaybackWatchTimer() {
    if (watchIntervalId !== null || typeof window === 'undefined') return;
    watchIntervalId = window.setInterval(function () {
      const audio = typeof document !== 'undefined' ? document.getElementById('baek-studio-audio') : null;
      if (audio && !audio.paused && !audio.ended && audio.currentTime > 0) {
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

  function ensureStudioAndStickyStyles() {
    if (typeof document === 'undefined' || !document.head) return;
    if (document.getElementById('paradise-radio-critical-css')) return;
    const style = document.createElement('style');
    style.id = 'paradise-radio-critical-css';
    style.textContent = `
      .baek-studio-stage {
        background: linear-gradient(135deg, #0E2820 0%, #163B2F 55%, #1E293B 100%);
        border: 3px solid #D4AF37;
        border-radius: 18px;
        padding: 20px;
        color: #FFFFFF;
        box-shadow: 0 12px 28px rgba(14, 40, 32, 0.25);
        margin-bottom: 18px;
      }
      .baek-studio-grid {
        display: grid;
        grid-template-columns: minmax(180px, 240px) 1fr;
        gap: 20px;
        align-items: center;
      }
      .baek-studio-portrait-wrap {
        text-align: center;
      }
      .baek-studio-portrait {
        width: 100%;
        max-width: 220px;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        object-position: top center;
        border-radius: 16px;
        border: 3px solid #D4AF37;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
        background: #0E2820;
      }
      .baek-studio-top-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
      }
      .baek-studio-onair-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(212, 175, 55, 0.18);
        border: 1.5px solid #D4AF37;
        color: #FEF08A;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 16px;
        font-weight: 800;
      }
      .baek-studio-onair-pill.is-live {
        background: #991B1B;
        border-color: #FCA5A5;
        color: #FFFFFF;
      }
      .baek-studio-time-pill {
        font-size: 17px;
        font-weight: 800;
        color: #FDE68A;
        font-variant-numeric: tabular-nums;
      }
      .baek-studio-big-play-btn {
        width: 100%;
        min-height: 66px;
        padding: 12px 20px;
        border-radius: 14px;
        background: #D4AF37;
        color: #0E2820;
        border: 2px solid #FEF08A;
        font-size: 22px;
        font-weight: 900;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
      }
      .baek-studio-big-play-btn.playing {
        background: #FEF08A;
        color: #0E2820;
      }
      .baek-studio-caption {
        background: rgba(255, 255, 255, 0.1);
        border-left: 4px solid #D4AF37;
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 20px;
        line-height: 1.6;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0 0 12px;
        min-height: 68px;
      }
      .baek-studio-scrubber {
        width: 100%;
        height: 12px;
        accent-color: #D4AF37;
        cursor: pointer;
      }
      @media (max-width: 680px) {
        .baek-studio-grid {
          grid-template-columns: 1fr;
        }
        .baek-studio-portrait {
          max-width: 160px;
        }
      }
      .sticky-radio-bar { position: fixed; bottom: 0; left: 0; right: 0; z-index: 1000; background: #0E2820; color: #FFFFFF; border-top: 3px solid #D4AF37; padding: 10px 16px; box-shadow: 0 -4px 20px rgba(0,0,0,0.35); transition: transform 0.2s ease, opacity 0.2s ease; }
      .btn-radio-play, .btn-radio-secondary, .btn-radio-expand-up, #btn-radio-toggle, #btn-radio-next, #btn-radio-prev {
        min-height: 60px; padding: 12px 18px; font-size: 20px; font-weight: 800; border-radius: 14px;
        display: inline-flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer;
      }
      .btn-radio-expand-up { background: rgba(255,255,255,0.14); color: #FEF08A; border: 2px solid #D4AF37; }
      body.is-keyboard-editing .sticky-radio-bar { transform: translateY(120%) !important; opacity: 0 !important; pointer-events: none !important; }
      @media (max-width: 768px) {
        body { padding-bottom: 76px !important; }
        .sticky-radio-bar { height: 58px !important; min-height: 56px !important; max-height: 60px !important; padding: 5px 10px !important; display: flex !important; align-items: center !important; }
        .sticky-radio-bar .radio-bar-inner { width: 100% !important; display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: space-between !important; gap: 8px !important; }
        .sticky-radio-bar .radio-live-badge, .sticky-radio-bar .radio-wifi-notice, .sticky-radio-bar #btn-radio-next { display: none !important; }
        .sticky-radio-bar .radio-info { order: 2; flex: 1 1 auto !important; min-width: 0 !important; width: auto !important; }
        .sticky-radio-bar .radio-track-title { font-size: 15px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
        .sticky-radio-bar .radio-controls { display: contents !important; }
        .sticky-radio-bar #btn-radio-toggle { order: 1; width: auto !important; min-width: 84px !important; min-height: 44px !important; max-height: 46px !important; padding: 6px 10px !important; font-size: 15px !important; border-radius: 10px !important; flex-shrink: 0 !important; }
        .sticky-radio-bar #btn-radio-expand-up { order: 3; width: auto !important; min-height: 44px !important; max-height: 46px !important; padding: 6px 10px !important; font-size: 14px !important; border-radius: 10px !important; flex-shrink: 0 !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function syncUiState(playingState) {
    if (typeof document === 'undefined') return;
    const ep = RADIO_EPISODES[currentIndex];
    const statusEl = document.getElementById('radio-status-label');
    const playIcon = document.getElementById('radio-play-icon');
    const playText = document.getElementById('radio-play-text');
    const toggleBtn = document.getElementById('btn-radio-toggle');
    const titleEl = document.getElementById('radio-current-title');
    const mainTitle = document.getElementById('main-youtube-title');
    const posterEl = document.getElementById('studio-stage-poster');
    const onairEl = document.getElementById('studio-onair-pill');
    const stagePlayBtn = document.getElementById('btn-studio-stage-play');
    const stagePlayIcon = document.getElementById('studio-stage-play-icon');
    const stagePlayLabel = document.getElementById('studio-stage-play-label');

    if (titleEl) {
      titleEl.textContent = customBannerTitle || `${ep.title} (${ep.song})`;
    }
    if (mainTitle) {
      mainTitle.textContent = customBannerTitle
        ? `🎵 지금 선택된 방송: ${customBannerTitle}`
        : `📻 현재 선택된 방송: ${ep.title} (수록곡: ${ep.song})`;
    }
    if (posterEl && ep.poster && posterEl.getAttribute('src') !== ep.poster) {
      posterEl.setAttribute('src', ep.poster);
    }

    if (playingState) {
      if (statusEl) statusEl.textContent = '🔴 지금 방송 중 — @김쌤의영웅라디오 · 백운호 스튜디오';
      if (playIcon) playIcon.textContent = '⏸';
      if (playText) playText.textContent = '일시정지';
      if (toggleBtn) toggleBtn.classList.add('playing');
      if (onairEl) {
        onairEl.textContent = '🔴 ON AIR · 백운호 사연 라디오 방송 중';
        onairEl.classList.add('is-live');
      }
      if (stagePlayBtn) stagePlayBtn.classList.add('playing');
      if (stagePlayIcon) stagePlayIcon.textContent = '⏸';
      if (stagePlayLabel) stagePlayLabel.textContent = '방송 일시정지 (다시 누르면 계속 재생)';
    } else {
      if (statusEl) statusEl.textContent = '📻 김쌤의 영웅 라디오 (▶ 방송 듣기를 누르세요)';
      if (playIcon) playIcon.textContent = '▶';
      if (playText) playText.textContent = '방송 듣기';
      if (toggleBtn) toggleBtn.classList.remove('playing');
      if (onairEl) {
        onairEl.textContent = '📻 스튜디오 대기 중 · 광고 0초 즉시 재생';
        onairEl.classList.remove('is-live');
      }
      if (stagePlayBtn) stagePlayBtn.classList.remove('playing');
      if (stagePlayIcon) stagePlayIcon.textContent = '▶';
      if (stagePlayLabel) stagePlayLabel.textContent = '지금 사연·노래 방송 바로 듣기';
    }

    document.querySelectorAll('[data-play-episode]').forEach(function (btn) {
      const idx = parseInt(btn.getAttribute('data-play-episode'), 10);
      if (idx === currentIndex) {
        btn.classList.add('btn-primary');
        btn.classList.remove('btn-outline');
      } else {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline');
      }
    });
  }

  function buildStickyPlayerDOM() {
    ensureStudioAndStickyStyles();
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
            <span id="radio-status-label">📻 김쌤의 영웅 라디오 (▶ 방송 듣기를 누르면 바로 소리가 납니다)</span>
          </div>
          <div class="radio-track-title" id="radio-current-title">${ep.title}</div>
          <div class="radio-wifi-notice">💡 광고 없이 백운호의 오리지널 사연 방송이 연속 재생됩니다.</div>
        </div>
        <div class="radio-controls">
          <button type="button" class="btn-radio-play" id="btn-radio-toggle" aria-label="라디오 방송 재생 및 일시정지">
            <span aria-hidden="true" id="radio-play-icon">▶</span>
            <span id="radio-play-text">방송 듣기</span>
          </button>
          <button type="button" class="btn-radio-secondary" id="btn-radio-next" aria-label="다음 라디오 사연 듣기">
            <span>다음 편 ⏭</span>
          </button>
          <button type="button" class="btn-radio-expand-up" id="btn-radio-expand-up" aria-label="라디오 방송 화면 위로 열기">
            <span>위로 열기 ↑</span>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(bar);
  }

  function loadAndPlayCurrentEpisode(shouldPlay) {
    const ep = RADIO_EPISODES[currentIndex];
    const audio = ensureStudioAudioElement();
    if (!audio) return;

    const currentAttr = audio.getAttribute('src') || '';
    if (currentAttr !== ep.audioSrc) {
      audio.setAttribute('src', ep.audioSrc);
      try { audio.load(); } catch (e) {}
    }

    const capEl = typeof document !== 'undefined' ? document.getElementById('studio-live-caption') : null;
    if (capEl && Array.isArray(ep.captions) && ep.captions[0]) {
      capEl.textContent = ep.captions[0].text;
    }

    if (shouldPlay) {
      isPlaying = true;
      saveState();
      syncUiState(true);
      const p = audio.play();
      if (p && typeof p.catch === 'function') {
        p.catch(function () {
          isPlaying = false;
          syncUiState(false);
        });
      }
    } else {
      try { audio.pause(); } catch (e) {}
      isPlaying = false;
      saveState();
      syncUiState(false);
    }
  }

  function focusStudioSection() {
    if (typeof document === 'undefined') return;
    const sec = document.getElementById('hero-radio-section') || document.getElementById('main-youtube-embed');
    if (sec && typeof sec.scrollIntoView === 'function') {
      sec.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function togglePlay() {
    const audio = ensureStudioAudioElement();
    if (!audio) return;
    if (audio.paused) {
      loadAndPlayCurrentEpisode(true);
    } else {
      loadAndPlayCurrentEpisode(false);
    }
  }

  function nextEpisode() {
    flagshipQueueActive = false;
    customBannerTitle = '';
    currentIndex = (currentIndex + 1) % RADIO_EPISODES.length;
    loadAndPlayCurrentEpisode(true);
  }

  function playEpisodeByIndex(idx, optionalCustomTitle) {
    if (idx >= 0 && idx < RADIO_EPISODES.length) {
      flagshipQueueActive = false;
      customBannerTitle = optionalCustomTitle || '';
      currentIndex = idx;
      loadAndPlayCurrentEpisode(true);
      focusStudioSection();
    }
  }

  function playFlagshipTrackAtIndex(qIdx) {
    const tracks = FLAGSHIP_EP1_CONFIG.continuousTracks;
    if (!Array.isArray(tracks) || tracks.length === 0) return;
    flagshipQueueActive = true;
    flagshipQueueIdx = ((qIdx % tracks.length) + tracks.length) % tracks.length;
    const tr = tracks[flagshipQueueIdx];
    customBannerTitle = tr.label;

    const audio = ensureStudioAudioElement();
    if (!audio) return;
    audio.setAttribute('src', tr.audioSrc);
    try { audio.load(); } catch (e) {}

    const posterEl = typeof document !== 'undefined' ? document.getElementById('studio-stage-poster') : null;
    if (posterEl && tr.poster) {
      posterEl.setAttribute('src', tr.poster);
    }
    const capEl = typeof document !== 'undefined' ? document.getElementById('studio-live-caption') : null;
    if (capEl) {
      capEl.textContent = tr.caption;
    }
    const statusBadge = typeof document !== 'undefined' ? document.getElementById('hero-ep1-showcase-status') : null;
    if (statusBadge) {
      statusBadge.textContent = '🔴 지금 재생 중 (' + String(flagshipQueueIdx + 1) + '/' + String(tracks.length) + ') · ' + tr.label;
    }

    isPlaying = true;
    saveState();
    syncUiState(true);
    const p = audio.play();
    if (p && typeof p.catch === 'function') {
      p.catch(function () {
        isPlaying = false;
        syncUiState(false);
      });
    }
  }

  function advanceFlagshipEp1Queue() {
    const nextIdx = (flagshipQueueIdx + 1) % FLAGSHIP_EP1_CONFIG.continuousTracks.length;
    playFlagshipTrackAtIndex(nextIdx);
  }

  function activateFlagshipEpisode1() {
    if (typeof document === 'undefined') return;
    const vid = (FLAGSHIP_EP1_CONFIG.youtubeVideoId || '').trim();
    const mount = document.getElementById('hero-ep1-video-mount');
    if (vid && /^[A-Za-z0-9_-]{11}$/.test(vid) && mount) {
      try {
        const audio = document.getElementById('baek-studio-audio');
        if (audio && !audio.paused) audio.pause();
      } catch (e) {}
      mount.innerHTML =
        '<div style="position:relative;width:100%;aspect-ratio:16/9;margin-bottom:22px;border-radius:14px;overflow:hidden;border:3px solid #D4AF37;background:#000;z-index:1;">' +
        '<iframe src="https://www.youtube-nocookie.com/embed/' + vid + '?autoplay=1&rel=0" ' +
        'title="' + FLAGSHIP_EP1_CONFIG.title.replace(/"/g, '&quot;') + '" ' +
        'style="position:absolute;inset:0;width:100%;height:100%;border:0;" ' +
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>';
      return;
    }
    playFlagshipTrackAtIndex(0);
    focusStudioSection();
  }

  function initRadioPlayer() {
    loadState();
    const deepLinked = applyQueryDeepLink();
    buildStickyPlayerDOM();
    ensureStudioAudioElement();
    syncUiState(false);
    ensureRealPlaybackWatchTimer();

    if (deepLinked) {
      loadAndPlayCurrentEpisode(false);
      focusStudioSection();
    }

    const toggleBtn = document.getElementById('btn-radio-toggle');
    const nextBtn = document.getElementById('btn-radio-next');
    const expandUpBtn = document.getElementById('btn-radio-expand-up');
    const stagePlayBtn = document.getElementById('btn-studio-stage-play');
    const scrubber = document.getElementById('studio-audio-scrubber');

    if (toggleBtn) toggleBtn.addEventListener('click', togglePlay);
    if (stagePlayBtn) stagePlayBtn.addEventListener('click', togglePlay);
    if (nextBtn) nextBtn.addEventListener('click', nextEpisode);

    if (scrubber) {
      scrubber.addEventListener('input', function () {
        scrubber.__isDragging = true;
      });
      scrubber.addEventListener('change', function () {
        const audio = ensureStudioAudioElement();
        if (audio && isFinite(audio.duration) && audio.duration > 0) {
          const ratio = Math.max(0, Math.min(1, parseInt(scrubber.value || '0', 10) / 1000));
          audio.currentTime = ratio * audio.duration;
        }
        scrubber.__isDragging = false;
      });
    }

    if (expandUpBtn) {
      expandUpBtn.addEventListener('click', function () {
        const radioSec = document.getElementById('hero-radio-section') || document.getElementById('main-youtube-embed');
        if (radioSec && typeof radioSec.scrollIntoView === 'function') {
          radioSec.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }
        if (typeof window !== 'undefined' && window.location) {
          window.location.href = 'radio.html?ep=' + String(currentIndex + 1);
        }
      });
    }

    document.addEventListener('focusin', function (ev) {
      const t = ev.target;
      if (t && t.matches && t.matches('input:not([type="checkbox"]):not([type="radio"]):not([type="file"]):not([type="range"]), textarea, select, [contenteditable="true"]')) {
        document.body.classList.add('is-keyboard-editing');
      }
    });
    document.addEventListener('focusout', function () {
      setTimeout(function () {
        const active = document.activeElement;
        if (!active || !active.matches || !active.matches('input:not([type="checkbox"]):not([type="radio"]):not([type="file"]):not([type="range"]), textarea, select, [contenteditable="true"]')) {
          document.body.classList.remove('is-keyboard-editing');
        }
      }, 120);
    });

    const heroRadioCta = document.getElementById('btn-hero-radio-now');
    if (heroRadioCta) {
      heroRadioCta.addEventListener('click', function (e) {
        const radioSection = document.getElementById('hero-radio-section');
        if (radioSection) {
          e.preventDefault();
          playEpisodeByIndex(currentIndex || 0);
        }
      });
    }

    document.querySelectorAll('[data-play-episode]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const epIdx = parseInt(this.getAttribute('data-play-episode'), 10);
        const customTitle = this.getAttribute('data-play-title') || '';
        if (!isNaN(epIdx)) {
          playEpisodeByIndex(epIdx, customTitle);
        }
      });
    });
    document.querySelectorAll('[data-play-flagship-ep1]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        activateFlagshipEpisode1();
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
    window.HERO_FLAGSHIP_EP1_CONFIG = FLAGSHIP_EP1_CONFIG;
    window.ParadiseRadio = {
      episodes: RADIO_EPISODES,
      flagshipEp1: FLAGSHIP_EP1_CONFIG,
      togglePlay: togglePlay,
      nextEpisode: nextEpisode,
      playEpisode: playEpisodeByIndex,
      playFlagshipEp1: activateFlagshipEpisode1,
      applyQueryDeepLink: applyQueryDeepLink,
      getAccumulatedPlaySeconds: function () { return accumulatedPlaySeconds; }
    };
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      RADIO_EPISODES,
      FLAGSHIP_EP1_CONFIG
    };
  }
})();
