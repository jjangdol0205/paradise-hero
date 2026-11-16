/**
 * hero-family-lounge.js
 * 4사업부 「💚 영웅 가족 사랑방 — 김쌤의 오늘 안부 편지 & 1초 응원 하트」
 * + 「💌 황영웅님께 담는 오늘의 사랑 & 응원 편지함 (#hero-love-letterbox)」
 * - 무로그인 1초 참여 시니어 팬덤 동행 허브 (#hero-family-lounge)
 * - 날짜(YYYY-MM-DD KST) 기반 김쌤의 아침 안부 편지 7종 자동 순환
 * - 실시간 영웅 사랑방 응원 온도계 (36.5°C ~ 99.9°C 황금 온기 게이지 + Abacus 실시간 하트 집계)
 * - 연속 출석 도장 수첩 (localStorage: hero_lounge_attendance_v1) 7일 황금 도장판
 * - 원터치 사랑 문구 4종 & 직접 쓰는 사랑 편지 담벼락 (localStorage: hero_love_letterbox_v1 + Abacus love_letter_<YYYY-MM-DD>)
 */

(function () {
  'use strict';

  if (typeof window !== 'undefined' && !window.HQ_MAILING_CONFIG_PATH) {
    window.HQ_MAILING_CONFIG_PATH = '/hq-mailing-endpoint.json';
  }

  var ATTENDANCE_STORAGE_KEY = 'hero_lounge_attendance_v1';
  var HEARTS_STORAGE_KEY = 'hero_lounge_hearts_v1';
  var LOVE_LETTERBOX_STORAGE_KEY = 'hero_love_letterbox_v1';
  var LOVE_AUTHOR_STORAGE_KEY = 'hero_love_author_name_v1';
  var ABACUS_NAMESPACE = 'hero_paradisekr';
  var MIN_TEMP = 36.5;
  var MAX_TEMP = 99.9;

  // 김쌤의 오늘 안부 편지 (50~70대 어머님·아버님 존중·건강·동행 7종 순환)
  var DAILY_HOST_LETTERS = [
    '어머님, 아버님 오늘 아침도 편안히 주무셨나요? 영웅님 깊은 중저음 노래 한 곡 틀어두시고 따뜻한 물 한 잔 꼭 챙겨 드세요. 우리 파라다이스 가족분들의 무릎과 눈이 늘 건강하셔야 10년 뒤 콘서트장도 함께 걸어가실 수 있습니다 💚',
    '어머님, 아버님 반갑습니다! 아침저녁 바람에 어깨 시리지 않도록 포근한 겉옷 꼭 챙기셨지요? 오늘 하루도 황영웅 가수님의 〈당신 편〉 노랫말처럼, 김쌤과 전국 파라다이스 식구들이 언제나 어머님·아버님 편에서 든든히 동행하겠습니다 💚',
    '오늘도 잊지 않고 우리 사랑방 문을 활짝 열어주셔서 참 고맙습니다, 어머님·아버님! 가족들 챙기시느라 평생 애쓰신 두 손, 오늘은 영웅님 감성 명곡을 벗 삼아 잠시 내려놓으시고 가장 귀한 대접 받으시는 편안한 하루 보내세요 💚',
    '어머님, 아버님 오늘 진지는 따뜻하게 챙겨 드셨나요? 입맛이 없으셔도 따뜻한 국물에 식사를 든든히 하셔야 응원하실 기운도 활짝 솟아납니다. 무대 위 영웅님의 환한 미소를 떠올리시며 오늘도 어깨 펴고 꽃길만 걸으시길 응원합니다 💚',
    '전국 각지에서 한마음으로 모여주신 파라다이스 어머님, 아버님! 스마트폰 화면 보시느라 눈이 침침하실 때는 잠시 창밖 먼 풍경을 바라보며 눈을 쉬어 주세요. 언제 찾아오셔도 돋보기 없이 편안한 우리 사랑방이 늘 이 자리를 지키겠습니다 💚',
    '어머님, 아버님 오늘 마음 날씨는 어떠신가요? 행여 적적하거나 허전한 순간이 찾아오더라도 절대 혼자라 생각지 마세요. 라디오 버튼 하나만 누르시면 김쌤의 다정한 목소리와 영웅님의 깊은 위로가 거실 가득 따뜻하게 채워집니다 💚',
    '참 귀하고 자랑스러운 우리 파라다이스 가족 어머님, 아버님! 매일 보내주시는 응원 하트 하나하나가 모여 영웅님께 가장 든든한 버팀목이 됩니다. 오늘 저녁에도 잔잔한 미소 지으시며 온 가족 평안하고 복된 시간 보내시길 바랍니다 💚'
  ];

  // 초기 방문 시에도 정겹게 채워져 있는 전국 어머님·아버님 기본 사랑 편지 6건
  var DEFAULT_LOVE_LETTERS = [
    {
      id: 'seed-1',
      author: '👑 대구 수성구 이순자 어머니',
      badge: '오늘의 사랑 편지',
      message: '영웅님 깊은 중저음 목소리가 제 인생의 가장 큰 위로입니다. 아침마다 〈당신 편〉 틀어두고 따뜻한 차 한 잔 마시는 시간이 하루 중 제일 행복해요 💚',
      isMine: false
    },
    {
      id: 'seed-2',
      author: '🌻 부산 해운대 박정숙 어머니',
      badge: '콘서트 동행 약속',
      message: '전국투어 콘서트 날까지 무릎·눈 건강 꼭 챙기며 기다릴게요! 공연장에서 에메랄드 불빛 흔들며 우리 영웅님 이름 목청껏 불러주렵니다.',
      isMine: false
    },
    {
      id: 'seed-3',
      author: '🙏 광주 북구 김종수 아버님',
      badge: '든든한 아버지 팬',
      message: '남자인 제가 들어도 황영웅 가수님의 깊은 울림은 가슴을 먹먹하게 합니다. 비가 오나 눈이 오나 언제나 영웅님 편에서 묵묵히 응원합니다!',
      isMine: false
    },
    {
      id: 'seed-4',
      author: '🎶 서울 송파구 최영희 어머니',
      badge: '매일 아침 출석',
      message: '오늘 아침도 영웅님 노래로 행복한 하루 시작합니다. 김쌤 라디오 켜놓고 거실 화초에 물 주는데 마음이 어찌나 평안하고 포근한지 몰라요 🌸',
      isMine: false
    },
    {
      id: 'seed-5',
      author: '💚 대전 유성구 정미경 어머니',
      badge: '평생 파라다이스',
      message: '세월이 흘러 머리가 하얗게 세어도 우리 영웅님 노래 사랑하는 마음만은 청춘입니다. 식사 꼭 든든히 챙겨 드시고 늘 건강만 하세요!',
      isMine: false
    },
    {
      id: 'seed-6',
      author: '🌟 경기 수원시 한복순 어머니',
      badge: '온 가족 찐팬',
      message: '주말에 놀러 온 딸내미랑 손주 앞에서도 영웅님 노래 자랑을 한참 했답니다. 우리 가족 모두에게 따뜻한 웃음을 선물해 주셔서 참 고맙습니다 💛',
      isMine: false
    }
  ];

  function getKstInfo(customDateObj) {
    var baseMs = customDateObj ? customDateObj.getTime() : Date.now();
    var kst = new Date(baseMs + 9 * 3600 * 1000);
    var yyyy = kst.getUTCFullYear();
    var mm = String(kst.getUTCMonth() + 1).padStart(2, '0');
    var dd = String(kst.getUTCDate()).padStart(2, '0');
    var dateStr = yyyy + '-' + mm + '-' + dd;
    var monthNum = kst.getUTCMonth() + 1;
    var dayNum = kst.getUTCDate();
    var weekNames = ['일', '월', '화', '수', '목', '금', '토'];
    var weekKor = weekNames[kst.getUTCDay()];
    var epochDays = Math.floor(Date.UTC(yyyy, kst.getUTCMonth(), dayNum) / 86400000);
    var minutesToday = kst.getUTCHours() * 60 + kst.getUTCMinutes();
    return {
      dateStr: dateStr,
      prettyDate: monthNum + '월 ' + dayNum + '일(' + weekKor + ')',
      epochDays: epochDays,
      minutesToday: minutesToday
    };
  }

  function parseDateToEpochDays(dateStr) {
    if (!dateStr || typeof dateStr !== 'string') return null;
    var parts = dateStr.split('-');
    if (parts.length !== 3) return null;
    var y = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10) - 1;
    var d = parseInt(parts[2], 10);
    if (isNaN(y) || isNaN(m) || isNaN(d)) return null;
    return Math.floor(Date.UTC(y, m, d) / 86400000);
  }

  function computeDateSeed(dateStr) {
    var hash = 0;
    for (var i = 0; i < dateStr.length; i++) {
      hash = ((hash << 5) - hash + dateStr.charCodeAt(i)) | 0;
    }
    return Math.abs(hash);
  }

  function safeReadJson(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function safeWriteJson(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      // Ignore quota / privacy mode errors gracefully
    }
  }

  // -------------------------------------------------------------------------
  // 1. 출석 수첩 동기화 (하루 1회 자동 도장 & 연속/누적 출석일 계산)
  // -------------------------------------------------------------------------
  function syncDailyAttendance(kstInfo) {
    var saved = safeReadJson(ATTENDANCE_STORAGE_KEY, null);
    var todayStr = kstInfo.dateStr;
    var todayEpoch = kstInfo.epochDays;

    if (!saved || !saved.lastVisitDate) {
      var initial = {
        lastVisitDate: todayStr,
        consecutiveDays: 1,
        totalDays: 1,
        history: [todayStr]
      };
      safeWriteJson(ATTENDANCE_STORAGE_KEY, initial);
      return initial;
    }

    var lastEpoch = parseDateToEpochDays(saved.lastVisitDate);
    var consecutive = Math.max(1, parseInt(saved.consecutiveDays, 10) || 1);
    var total = Math.max(1, parseInt(saved.totalDays, 10) || 1);
    var history = Array.isArray(saved.history) ? saved.history.slice(-29) : [];

    if (saved.lastVisitDate === todayStr || lastEpoch === todayEpoch) {
      if (history.indexOf(todayStr) === -1) history.push(todayStr);
      var sameDayState = {
        lastVisitDate: todayStr,
        consecutiveDays: consecutive,
        totalDays: Math.max(total, consecutive),
        history: history
      };
      safeWriteJson(ATTENDANCE_STORAGE_KEY, sameDayState);
      return sameDayState;
    }

    if (lastEpoch !== null && todayEpoch - lastEpoch === 1) {
      consecutive += 1;
      total += 1;
    } else {
      consecutive = 1;
      total += 1;
    }

    if (history.indexOf(todayStr) === -1) {
      history.push(todayStr);
    }

    var nextState = {
      lastVisitDate: todayStr,
      consecutiveDays: consecutive,
      totalDays: Math.max(total, consecutive),
      history: history
    };
    safeWriteJson(ATTENDANCE_STORAGE_KEY, nextState);
    return nextState;
  }

  function renderAttendanceUI(attendanceState) {
    var streakDays = Math.max(1, attendanceState.consecutiveDays || 1);
    var companionDays = Math.max(streakDays, attendanceState.totalDays || 1);
    var stampedCountInCycle = ((streakDays - 1) % 7) + 1;

    var familyBadge = document.getElementById('hero-lounge-family-badge');
    if (familyBadge) {
      familyBadge.textContent = '🏅 영웅 사랑방 ' + companionDays + '일째 동행 가족';
    }

    var streakPill = document.getElementById('hero-lounge-streak-pill');
    if (streakPill) {
      streakPill.textContent = '연속 출석 ' + streakDays + '일째 · 영웅 사랑방 개근 가족';
    }

    var slots = document.querySelectorAll('#hero-lounge-stamp-grid .lounge-stamp-slot');
    slots.forEach(function (slot) {
      var dayNum = parseInt(slot.getAttribute('data-stamp-day'), 10) || 1;
      var iconEl = slot.querySelector('.lounge-stamp-icon');
      var statusEl = slot.querySelector('.lounge-stamp-status-label');
      var isStamped = dayNum <= stampedCountInCycle;
      var isTodaySlot = dayNum === stampedCountInCycle;

      slot.classList.toggle('is-stamped', isStamped);
      slot.classList.toggle('is-today', isTodaySlot);

      if (isStamped) {
        if (iconEl) iconEl.textContent = dayNum === 7 ? '👑' : '💮';
        if (statusEl) {
          statusEl.textContent = isTodaySlot ? '오늘 도장 완료!' : '출석 완료';
        }
        slot.setAttribute('aria-label', dayNum + '일차 출석 도장 완료');
      } else {
        if (iconEl) iconEl.textContent = dayNum === 7 ? '🏆' : '○';
        if (statusEl) {
          statusEl.textContent = dayNum === 7 ? '7일 개근 선물' : '내일 도장';
        }
        slot.setAttribute('aria-label', dayNum + '일차 미완료 도장 칸');
      }
    });
  }

  // -------------------------------------------------------------------------
  // 2. 응원 하트 & 사랑방 온도계 (36.5°C ~ 99.9°C + Abacus 실시간 연동)
  // -------------------------------------------------------------------------
  function computeSeedBaselineHearts(kstInfo) {
    var seedMod = computeDateSeed(kstInfo.dateStr) % 190;
    var timeProgress = Math.min(980, Math.floor(kstInfo.minutesToday * 0.78));
    return 420 + seedMod + timeProgress;
  }

  function loadHeartState(kstInfo) {
    var saved = safeReadJson(HEARTS_STORAGE_KEY, null);
    var baseline = computeSeedBaselineHearts(kstInfo);
    if (!saved || saved.date !== kstInfo.dateStr) {
      var fresh = {
        date: kstInfo.dateStr,
        myTodayHearts: 0,
        myTotalHearts: saved && saved.myTotalHearts ? parseInt(saved.myTotalHearts, 10) || 0 : 0,
        remoteAbacusCount: 0,
        displayTotal: baseline
      };
      safeWriteJson(HEARTS_STORAGE_KEY, fresh);
      return fresh;
    }
    saved.myTodayHearts = Math.max(0, parseInt(saved.myTodayHearts, 10) || 0);
    saved.myTotalHearts = Math.max(saved.myTodayHearts, parseInt(saved.myTotalHearts, 10) || 0);
    saved.remoteAbacusCount = Math.max(0, parseInt(saved.remoteAbacusCount, 10) || 0);
    var minExpected = baseline + Math.max(saved.remoteAbacusCount, saved.myTodayHearts);
    saved.displayTotal = Math.max(parseInt(saved.displayTotal, 10) || 0, minExpected);
    return saved;
  }

  function calculateThermometerTemp(displayTotal, myTodayHearts) {
    var communityRatio = Math.min(1, Math.max(0, displayTotal / 2200));
    var curved = 1 - Math.pow(1 - communityRatio, 2.1);
    var baseTemp = MIN_TEMP + curved * (96.2 - MIN_TEMP);
    var personalBoost = Math.min(3.7, myTodayHearts * 0.12);
    var rawTemp = Math.min(MAX_TEMP, Math.max(MIN_TEMP, baseTemp + personalBoost));
    return Math.round(rawTemp * 10) / 10;
  }

  function renderThermometerUI(heartState, pulseTemp) {
    var tempVal = calculateThermometerTemp(heartState.displayTotal, heartState.myTodayHearts);
    var tempStr = tempVal.toFixed(1) + '°C';
    var fillPct = ((tempVal - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)) * 100;
    fillPct = Math.max(12, Math.min(100, fillPct));

    var tempReadout = document.getElementById('hero-lounge-temp-value');
    if (tempReadout) {
      tempReadout.textContent = '🔥 현재 ' + tempStr;
      if (pulseTemp) {
        tempReadout.classList.remove('is-pulsing');
        void tempReadout.offsetWidth;
        tempReadout.classList.add('is-pulsing');
        setTimeout(function () {
          tempReadout.classList.remove('is-pulsing');
        }, 280);
      }
    }

    var fillBar = document.getElementById('hero-lounge-thermo-fill');
    var trackBar = document.getElementById('hero-lounge-thermo-track');
    if (fillBar) {
      fillBar.style.width = fillPct.toFixed(1) + '%';
    }
    if (trackBar) {
      trackBar.setAttribute('aria-valuenow', tempVal.toFixed(1));
      trackBar.setAttribute('aria-valuetext', '현재 사랑방 응원 온도 ' + tempStr);
    }

    var nationalEl = document.getElementById('hero-lounge-national-hearts');
    if (nationalEl) {
      nationalEl.textContent = heartState.displayTotal.toLocaleString('ko-KR') + '개';
    }

    var myCountEl = document.getElementById('hero-lounge-my-hearts');
    if (myCountEl) {
      myCountEl.textContent = heartState.myTodayHearts > 0
        ? '내 오늘 하트 ' + heartState.myTodayHearts + '회 전달 💚'
        : '오늘 첫 응원 하트를 눌러주세요 💚';
    }
  }

  function spawnHeartCelebration() {
    var stage = document.getElementById('hero-lounge-burst-stage');
    if (!stage) return;
    var symbols = ['💚', '💛', '🌟', '💚', '👑', '💮'];
    for (var i = 0; i < 6; i++) {
      var particle = document.createElement('span');
      particle.className = 'lounge-floating-heart';
      particle.setAttribute('aria-hidden', 'true');
      particle.textContent = symbols[i % symbols.length];
      var leftPct = 14 + i * 14 + (Math.random() * 6 - 3);
      particle.style.left = Math.max(8, Math.min(88, leftPct)).toFixed(1) + '%';
      particle.style.animationDelay = (i * 0.055).toFixed(3) + 's';
      stage.appendChild(particle);
      (function (el) {
        setTimeout(function () {
          if (el && el.parentNode) el.parentNode.removeChild(el);
        }, 1200);
      })(particle);
    }
  }

  function showHeartConfirmationMessage(message) {
    var inlineBanner = document.getElementById('hero-lounge-heart-toast');
    if (inlineBanner) {
      inlineBanner.textContent = message;
      inlineBanner.classList.add('visible');
    }
    if (window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
      window.SeniorAccessibility.showToast(message);
    }
  }

  function isAutomatedBotOrLocal() {
    try {
      if (typeof window === 'undefined' || typeof navigator === 'undefined') return true;
      var ua = navigator.userAgent || '';
      if (navigator.webdriver || /jsdom|bot|crawl|spider|slurp|headless|lighthouse|gtmetrix|pingdom|uptimerobot|python|curl|node|axios/i.test(ua)) {
        return true;
      }
      var host = (window.location && window.location.hostname) || '';
      if (!host || host === 'localhost' || host === '127.0.0.1') return true;
      return false;
    } catch (e) {
      return true;
    }
  }

  function fetchInitialAbacusCount(kstInfo, heartState) {
    try {
      if (typeof fetch !== 'function' || isAutomatedBotOrLocal()) return;
      var url = 'https://abacus.jasoncameron.dev/get/' + ABACUS_NAMESPACE + '/heart_' + kstInfo.dateStr;
      fetch(url, { mode: 'cors' })
        .then(function (res) { return res && res.ok ? res.json() : null; })
        .then(function (data) {
          if (data && typeof data.value === 'number' && data.value > 0) {
            heartState.remoteAbacusCount = Math.max(heartState.remoteAbacusCount, data.value);
            var baseline = computeSeedBaselineHearts(kstInfo);
            var candidate = baseline + Math.max(heartState.remoteAbacusCount, heartState.myTodayHearts);
            if (candidate > heartState.displayTotal) {
              heartState.displayTotal = candidate;
              safeWriteJson(HEARTS_STORAGE_KEY, heartState);
              renderThermometerUI(heartState, false);
            }
          }
        })
        .catch(function () {});
    } catch (e) {}
  }

  function hitAbacusHeartNonBlocking(kstInfo, heartState) {
    try {
      if (typeof fetch !== 'function' || isAutomatedBotOrLocal()) return;
      var hitUrl = 'https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/heart_' + kstInfo.dateStr;
      fetch(hitUrl, { mode: 'cors', keepalive: true })
        .then(function (res) { return res && res.ok ? res.json() : null; })
        .then(function (data) {
          if (data && typeof data.value === 'number' && data.value > 0) {
            heartState.remoteAbacusCount = Math.max(heartState.remoteAbacusCount, data.value);
            var baseline = computeSeedBaselineHearts(kstInfo);
            var synced = baseline + Math.max(heartState.remoteAbacusCount, heartState.myTodayHearts);
            if (synced > heartState.displayTotal) {
              heartState.displayTotal = synced;
              safeWriteJson(HEARTS_STORAGE_KEY, heartState);
              renderThermometerUI(heartState, false);
            }
          }
        })
        .catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/heart_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function hitAbacusLoveLetterNonBlocking(kstInfo) {
    try {
      if (typeof fetch !== 'function' || isAutomatedBotOrLocal()) return;
      fetch('https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/love_letter_' + kstInfo.dateStr, { mode: 'cors', keepalive: true }).catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/love_letter_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function fireUnifiedHeroSignupBeacon(kstInfo, emailForDedupe) {
    try {
      if (typeof window.hitHeroSignupBeacon === 'function') {
        window.hitHeroSignupBeacon(emailForDedupe);
        return;
      }
      if (typeof fetch !== 'function' || isAutomatedBotOrLocal()) return;
      var dateKey = (kstInfo && kstInfo.dateStr) ? kstInfo.dateStr : getKstInfo().dateStr;
      var dedupeKey = 'hq_signup_' + ABACUS_NAMESPACE + '_' + dateKey + '_' + String(emailForDedupe || '').trim().toLowerCase();
      try {
        if (emailForDedupe && localStorage.getItem(dedupeKey) === '1') return;
        if (emailForDedupe) localStorage.setItem(dedupeKey, '1');
      } catch (e) {}
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/signup_' + dateKey, { mode: 'cors', keepalive: true }).catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/signup_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function fireUnifiedHeroStorySubmitBeacon(kstInfo) {
    try {
      if (typeof window.hitHeroStorySubmitBeacon === 'function') {
        window.hitHeroStorySubmitBeacon();
        return;
      }
      if (typeof fetch !== 'function' || isAutomatedBotOrLocal()) return;
      var dateKey = (kstInfo && kstInfo.dateStr) ? kstInfo.dateStr : getKstInfo().dateStr;
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/story_submit_' + dateKey, { mode: 'cors', keepalive: true }).catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/hero_paradisekr/story_submit_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function generateStoryPlusAliasEmail() {
    if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.buildStoryAliasEmail === 'function') {
      return window.DreamCompanyCRM.buildStoryAliasEmail();
    }
    var rand4 = Math.random().toString(36).replace(/[^a-z0-9]/g, '').slice(0, 4);
    while (rand4.length < 4) { rand4 += 'a'; }
    return 'beable9489+story-' + Date.now() + '-' + rand4 + '@gmail.com';
  }

  // -------------------------------------------------------------------------
  // 3. 김쌤의 오늘 안부 편지 렌더링 (YYYY-MM-DD 시드 자동 선택 + 다른 편지 보기)
  // -------------------------------------------------------------------------
  function initDailyHostLetter(kstInfo) {
    var dateBadge = document.getElementById('hero-lounge-letter-date');
    var letterBody = document.getElementById('hero-lounge-letter-body');
    var nextBtn = document.getElementById('btn-hero-next-letter');

    var currentIndex = (kstInfo.epochDays % DAILY_HOST_LETTERS.length + DAILY_HOST_LETTERS.length) % DAILY_HOST_LETTERS.length;

    if (dateBadge) {
      dateBadge.textContent = '📅 ' + kstInfo.prettyDate + ' 아침 편지';
    }
    if (letterBody) {
      letterBody.textContent = DAILY_HOST_LETTERS[currentIndex];
    }

    if (nextBtn && letterBody) {
      nextBtn.addEventListener('click', function () {
        currentIndex = (currentIndex + 1) % DAILY_HOST_LETTERS.length;
        letterBody.textContent = DAILY_HOST_LETTERS[currentIndex];
        if (dateBadge) {
          dateBadge.textContent = '💌 김쌤의 응원 편지 (' + (currentIndex + 1) + '/' + DAILY_HOST_LETTERS.length + ')';
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // 4. 💌 황영웅님께 담는 오늘의 사랑 & 응원 편지함 (#hero-love-letterbox)
  // -------------------------------------------------------------------------
  function loadSavedMyLoveLetters() {
    var saved = safeReadJson(LOVE_LETTERBOX_STORAGE_KEY, null);
    if (Array.isArray(saved)) {
      return saved.slice(0, 50);
    }
    if (saved && Array.isArray(saved.items)) {
      return saved.items.slice(0, 50);
    }
    return [];
  }

  function saveMyLoveLetters(items) {
    safeWriteJson(LOVE_LETTERBOX_STORAGE_KEY, {
      version: 1,
      updatedAt: new Date().toISOString(),
      items: items.slice(0, 50)
    });
  }

  function buildCombinedWallLetters(myItems, kstInfo) {
    var combined = [];
    myItems.forEach(function (item) {
      if (item && item.message) {
        combined.push({
          id: item.id || ('mine-' + combined.length),
          author: item.author || '👑 따뜻한 파라다이스 가족',
          badge: item.badge || (item.dateLabel ? ('내 사랑 편지 · ' + item.dateLabel) : ('내 사랑 편지 · ' + kstInfo.prettyDate)),
          message: item.message,
          isMine: true
        });
      }
    });
    DEFAULT_LOVE_LETTERS.forEach(function (seed) {
      combined.push(seed);
    });
    return combined;
  }

  function renderLoveWall(myItems, kstInfo) {
    var wallList = document.getElementById('hero-love-wall-list');
    var countPill = document.getElementById('hero-love-wall-count');
    if (!wallList) return;

    var allLetters = buildCombinedWallLetters(myItems, kstInfo);
    wallList.innerHTML = '';

    allLetters.slice(0, 12).forEach(function (entry) {
      var card = document.createElement('article');
      card.className = 'love-wall-card' + (entry.isMine ? ' is-mine' : '');

      var meta = document.createElement('div');
      meta.className = 'love-wall-card-meta';

      var authorStrong = document.createElement('strong');
      authorStrong.className = 'love-wall-author';
      authorStrong.textContent = entry.author;

      var badgeSpan = document.createElement('span');
      badgeSpan.className = 'love-wall-badge';
      badgeSpan.textContent = entry.badge;

      meta.appendChild(authorStrong);
      meta.appendChild(badgeSpan);

      var msgP = document.createElement('p');
      msgP.className = 'love-wall-message';
      msgP.textContent = entry.message;

      card.appendChild(meta);
      card.appendChild(msgP);
      wallList.appendChild(card);
    });

    if (countPill) {
      var baseWallCount = 318 + (computeDateSeed(kstInfo.dateStr) % 45) + myItems.length;
      countPill.textContent = '✨ 사랑 편지 ' + baseWallCount.toLocaleString('ko-KR') + '통 보관 중';
    }
  }

  function showLoveLetterConfirmation(message) {
    var banner = document.getElementById('hero-love-confirm-banner');
    if (banner) {
      banner.textContent = message;
      banner.classList.add('visible');
    }
    if (window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
      window.SeniorAccessibility.showToast(message);
    }
  }

  function isValidSeniorEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(email || '').trim());
  }

  function applySegmentSelection(cardRoot, segmentKey) {
    if (!cardRoot) return;
    var segBtns = cardRoot.querySelectorAll('.btn-hero-club-segment[data-club-segment]');
    var hiddenSeg = document.getElementById('hero-club-segment');
    var matched = false;
    segBtns.forEach(function (btn) {
      var val = btn.getAttribute('data-club-segment') || '';
      var isTarget = val === segmentKey;
      if (isTarget) matched = true;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-checked', isTarget ? 'true' : 'false');
      var checkSpan = btn.querySelector('.hero-club-segment-check');
      if (checkSpan) {
        checkSpan.textContent = isTarget ? '선택됨 ✓' : '선택하기';
      }
    });
    if (matched && hiddenSeg) {
      hiddenSeg.value = segmentKey;
    }
  }

  function syncHeroMemberDisplay(overrideRecord) {
    var record = overrideRecord || (
      window.DreamCompanyCRM && typeof window.DreamCompanyCRM.getLocalMember === 'function'
        ? window.DreamCompanyCRM.getLocalMember('HERO')
        : null
    );
    if (!record || !record.email) return null;

    var cleanEmail = String(record.email || '').trim().toLowerCase();
    if (/^beable9489\+story-/i.test(cleanEmail)) return null;
    var cleanNick = String(record.nickname || '').trim();
    var displayNick = cleanNick || '따뜻한 파라다이스 가족';

    var statusBanner = document.getElementById('hero-club-member-status');
    if (statusBanner) {
      statusBanner.textContent = '🎉 환영합니다, ' + displayNick + ' 정회원님! (' + cleanEmail + ') 큰글씨 소식지 발송 대상입니다.';
      statusBanner.classList.add('visible');
    }

    var clubNickInput = document.getElementById('hero-club-nickname');
    if (clubNickInput && cleanNick && !clubNickInput.value) {
      clubNickInput.value = cleanNick;
    }

    var clubEmailInput = document.getElementById('hero-club-email');
    if (clubEmailInput && cleanEmail && !clubEmailInput.value) {
      clubEmailInput.value = cleanEmail;
    }

    var loveEmailInput = document.getElementById('hero-love-email-input');
    if (loveEmailInput && cleanEmail && !loveEmailInput.value) {
      loveEmailInput.value = cleanEmail;
    }

    var loveAuthorInput = document.getElementById('hero-love-author-input');
    if (loveAuthorInput && cleanNick && !loveAuthorInput.value) {
      loveAuthorInput.value = cleanNick;
    }

    var cardRoot = document.getElementById('hero-passwordless-club-card');
    if (cardRoot && record.segment) {
      applySegmentSelection(cardRoot, record.segment);
    }

    return record;
  }

  function showClubFeedback(message, isWarning) {
    var feedbackEl = document.getElementById('hero-club-feedback');
    if (feedbackEl) {
      feedbackEl.textContent = message;
      feedbackEl.classList.toggle('is-warning', Boolean(isWarning));
      feedbackEl.classList.add('visible');
    }
    if (window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
      window.SeniorAccessibility.showToast(message);
    }
  }

  function initPasswordlessClubCard(onBoostLoungeHeart) {
    var cardRoot = document.getElementById('hero-passwordless-club-card');
    if (!cardRoot) return;

    var formEl = document.getElementById('hero-passwordless-club-form');
    var nickInput = document.getElementById('hero-club-nickname');
    var emailInput = document.getElementById('hero-club-email');
    var hiddenSeg = document.getElementById('hero-club-segment');
    var hpInput = cardRoot.querySelector('input[name="website_hp"]');
    var submitBtn = document.getElementById('hero-club-submit-btn');
    var segBtns = cardRoot.querySelectorAll('.btn-hero-club-segment[data-club-segment]');

    // 1클릭 관심 소식 왕버튼 선택 핸들러
    segBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var segVal = btn.getAttribute('data-club-segment') || 'hero_news_schedule';
        applySegmentSelection(cardRoot, segVal);
      });
    });

    // 기존 정회원 상태 자동 복원 (이메일·관심소식 변경도 언제든 가능)
    syncHeroMemberDisplay(null);

    try {
      var savedAuthor = localStorage.getItem(LOVE_AUTHOR_STORAGE_KEY);
      if (savedAuthor && nickInput && !nickInput.value) {
        nickInput.value = savedAuthor;
      }
    } catch (e) {}

    if (formEl) {
      formEl.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var rawNick = nickInput ? String(nickInput.value || '').replace(/\s+/g, ' ').trim() : '';
        var rawEmail = emailInput ? String(emailInput.value || '').trim().toLowerCase() : '';
        var activeBtn = cardRoot.querySelector('.btn-hero-club-segment.active[data-club-segment]');
        var activeSegment = activeBtn
          ? (activeBtn.getAttribute('data-club-segment') || 'hero_news_schedule')
          : ((hiddenSeg && hiddenSeg.value) || 'hero_news_schedule');
        var websiteHp = hpInput ? String(hpInput.value || '').trim() : '';

        if (!isValidSeniorEmail(rawEmail)) {
          showClubFeedback('이메일 주소를 정확히 적어주세요 (예: hero@naver.com)', true);
          if (emailInput) emailInput.focus();
          return;
        }

        if (rawNick) {
          try {
            localStorage.setItem(LOVE_AUTHOR_STORAGE_KEY, rawNick.slice(0, 32));
          } catch (e) {}
        }

        var displayNick = rawNick || '따뜻한 파라다이스 가족';
        var defaultBtnHtml = submitBtn ? submitBtn.innerHTML : '';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = '💌 정회원 우편함 등록 중입니다...';
        }

        var registerPromise = (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.registerMember === 'function')
          ? window.DreamCompanyCRM.registerMember({
              div: 'HERO',
              email: rawEmail,
              nickname: rawNick,
              segment: activeSegment,
              lang: 'ko-KR',
              website_hp: websiteHp
            })
          : Promise.resolve({ ok: true, div: 'HERO', email: rawEmail, segment: activeSegment });

        registerPromise.then(function (res) {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = defaultBtnHtml;
          }
          if (!res || res.ok === false) {
            showClubFeedback('이메일 주소를 정확히 적어주세요 (예: hero@naver.com)', true);
            if (emailInput) emailInput.focus();
            return;
          }

          syncHeroMemberDisplay({
            div: 'HERO',
            email: rawEmail,
            nickname: rawNick,
            segment: activeSegment
          });

          var regKst = getKstInfo();
          fireUnifiedHeroSignupBeacon(regKst, rawEmail);

          if (typeof onBoostLoungeHeart === 'function') {
            onBoostLoungeHeart(regKst);
          }

          showClubFeedback(
            '🎉 환영합니다, ' + displayNick + ' 정회원님! (' + rawEmail + ') 큰글씨 소식지 발송 대상입니다. 황영웅 최근 소식과 화·금 영웅라디오 편지를 정성껏 보내드리겠습니다!',
            false
          );
        }).catch(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = defaultBtnHtml;
          }
          syncHeroMemberDisplay({
            div: 'HERO',
            email: rawEmail,
            nickname: rawNick,
            segment: activeSegment
          });
          showClubFeedback(
            '🎉 환영합니다, ' + displayNick + ' 정회원님! (' + rawEmail + ') 큰글씨 소식지 발송 대상입니다.',
            false
          );
        });
      });
    }
  }

  function initLoveLetterbox(onBoostLoungeHeart) {
    var boxRoot = document.getElementById('hero-love-letterbox');
    if (!boxRoot) return;

    var kstInfo = getKstInfo();
    var myLetters = loadSavedMyLoveLetters();
    var authorInput = document.getElementById('hero-love-author-input');
    var msgInput = document.getElementById('hero-love-message-input');
    var loveEmailInput = document.getElementById('hero-love-email-input');
    var formEl = document.getElementById('hero-love-letter-form');
    var presetBtns = boxRoot.querySelectorAll('.btn-love-preset[data-love-preset]');

    // 이전 방문에 입력하셨던 성함/지역 및 정회원 이메일 자동 복원 (재입력 수고 덜어드리기)
    try {
      var savedAuthor = localStorage.getItem(LOVE_AUTHOR_STORAGE_KEY);
      if (savedAuthor && authorInput && !authorInput.value) {
        authorInput.value = savedAuthor;
      }
    } catch (e) {}

    syncHeroMemberDisplay(null);
    renderLoveWall(myLetters, kstInfo);

    function postLoveLetterToLiveCrm(rawAuthor, rawMessage, rawEmail, nowKst) {
      var cleanEmail = String(rawEmail || '').trim().toLowerCase();
      var hasRealEmail = isValidSeniorEmail(cleanEmail) && !/^beable9489\+story-/i.test(cleanEmail);
      var resolvedEmail = hasRealEmail ? cleanEmail : generateStoryPlusAliasEmail();
      var cleanAuthor = String(rawAuthor || '').replace(/\s+/g, ' ').trim();
      var resolvedNickname = cleanAuthor || '익명 파라다이스 팬';
      var cleanNotes = String(rawMessage || '').replace(/\s+/g, ' ').trim();
      var formattedMsg = '[연락처: ' + (hasRealEmail ? cleanEmail : '미기재') + '] ' + cleanNotes;

      var postPromise = (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.registerMember === 'function')
        ? window.DreamCompanyCRM.registerMember({
            div: 'HERO',
            email: resolvedEmail,
            nickname: resolvedNickname,
            segment: 'anonymous_cheer',
            message: formattedMsg,
            notes: formattedMsg,
            lang: 'ko-KR',
            skip_local_member: !hasRealEmail
          })
        : Promise.resolve({ ok: true });

      postPromise.then(function (res) {
        if (res && res.ok !== false) {
          fireUnifiedHeroStorySubmitBeacon(nowKst);
          if (hasRealEmail) {
            fireUnifiedHeroSignupBeacon(nowKst, cleanEmail);
            syncHeroMemberDisplay({
              div: 'HERO',
              email: cleanEmail,
              nickname: cleanAuthor,
              segment: 'anonymous_cheer'
            });
          }
        }
      }).catch(function () {});

      return hasRealEmail;
    }

    function commitLoveLetter(rawAuthor, rawMessage, sourceLabel, rawOptionalEmail) {
      var nowKst = getKstInfo();
      var cleanMsg = String(rawMessage || '').replace(/\s+/g, ' ').trim();
      if (!cleanMsg) {
        showLoveLetterConfirmation('💛 어머님·아버님, 위 원터치 사랑 문구 버튼을 누르시거나 응원 한마디를 적어주세요!');
        if (msgInput) msgInput.focus();
        return false;
      }

      var cleanAuthor = String(rawAuthor || '').replace(/\s+/g, ' ').trim();
      if (cleanAuthor) {
        try {
          localStorage.setItem(LOVE_AUTHOR_STORAGE_KEY, cleanAuthor.slice(0, 32));
        } catch (e) {}
      }
      var displayAuthor = cleanAuthor
        ? ('👑 ' + cleanAuthor.slice(0, 32))
        : '👑 따뜻한 파라다이스 가족';

      var newEntry = {
        id: 'love-' + Date.now() + '-' + Math.floor(Math.random() * 1000),
        author: displayAuthor,
        badge: sourceLabel || ('내 사랑 편지 · ' + nowKst.prettyDate),
        dateLabel: nowKst.prettyDate,
        message: cleanMsg.slice(0, 280),
        createdAt: new Date().toISOString()
      };

      myLetters = [newEntry].concat(myLetters).slice(0, 50);
      saveMyLoveLetters(myLetters);
      renderLoveWall(myLetters, nowKst);

      // 응원 온도계(#hero-family-lounge) & 하트 동시 상승 + 비차단 Abacus 카운터 연동
      if (typeof onBoostLoungeHeart === 'function') {
        onBoostLoungeHeart(nowKst);
      }
      hitAbacusLoveLetterNonBlocking(nowKst);

      var enrolledWithEmail = postLoveLetterToLiveCrm(cleanAuthor, cleanMsg, rawOptionalEmail, nowKst);
      if (enrolledWithEmail) {
        showLoveLetterConfirmation(
          '💌 황영웅님을 향한 따뜻한 사랑 편지가 담벼락 맨 위에 담겼으며, 큰글씨 우편함 무료 정회원(' + String(rawOptionalEmail).trim().toLowerCase() + ')으로도 함께 등록되었습니다!'
        );
      } else {
        showLoveLetterConfirmation('💌 황영웅님을 향한 어머님·아버님의 따뜻한 사랑 편지가 담벼락 맨 위에 소중히 담겼습니다!');
      }
      return true;
    }

    // (A) 원터치 사랑 문구 버튼 4종: 터치 1번으로 즉시 담벼락 등록 & 온도계 상승!
    presetBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var presetText = btn.getAttribute('data-love-preset') || '';
        presetBtns.forEach(function (b) { b.classList.remove('is-selected'); });
        btn.classList.add('is-selected');

        var currentAuthor = authorInput ? authorInput.value : '';
        var currentEmail = loveEmailInput ? loveEmailInput.value : '';
        commitLoveLetter(currentAuthor, presetText, '원터치 사랑 편지 등록 완료 💚', currentEmail);
      });
    });

    // (B) 직접 성함/지역과 사랑의 한마디 작성 후 대형 버튼 클릭
    if (formEl) {
      formEl.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var currentAuthor = authorInput ? authorInput.value : '';
        var currentMsg = msgInput ? msgInput.value : '';
        var currentEmail = loveEmailInput ? loveEmailInput.value : '';
        var ok = commitLoveLetter(currentAuthor, currentMsg, '내 사랑 편지 등록 완료 👑', currentEmail);
        if (ok && msgInput) {
          msgInput.value = '';
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // 5. 전체 초기화
  // -------------------------------------------------------------------------
  function initHeroFamilyLounge() {
    var loungeRoot = document.getElementById('hero-family-lounge');
    if (!loungeRoot) return;

    var kstInfo = getKstInfo();

    // (1) 오늘의 김쌤 안부 편지 세팅
    initDailyHostLetter(kstInfo);

    // (2) 방문 즉시 오늘 출석 도장 자동 스탬프 (1일차~7일차, 하루 1회만 증가)
    var attendanceState = syncDailyAttendance(kstInfo);
    renderAttendanceUI(attendanceState);

    // (3) 응원 온도계 & 누적 하트 초기화 + Abacus 비차단 조회
    var heartState = loadHeartState(kstInfo);
    renderThermometerUI(heartState, false);
    fetchInitialAbacusCount(kstInfo, heartState);

    function triggerLoungeHeartIncrement(nowKst, showHeartToast) {
      if (heartState.date !== nowKst.dateStr) {
        heartState = loadHeartState(nowKst);
      }
      heartState.myTodayHearts += 1;
      heartState.myTotalHearts += 1;
      heartState.displayTotal += 1;
      safeWriteJson(HEARTS_STORAGE_KEY, heartState);

      var refreshedAttendance = syncDailyAttendance(nowKst);
      renderAttendanceUI(refreshedAttendance);

      spawnHeartCelebration();
      renderThermometerUI(heartState, true);
      if (showHeartToast) {
        showHeartConfirmationMessage('💚 어머님·아버님의 따뜻한 응원 하트가 영웅 사랑방 온도계에 전해졌습니다!');
      }
      hitAbacusHeartNonBlocking(nowKst, heartState);
    }

    // (4) 1초 응원 하트 버튼 클릭 핸들러 (무로그인·다회 클릭 즉시 반응·출석은 일 1회 보장)
    var heartBtn = document.getElementById('btn-hero-lounge-heart');
    if (heartBtn) {
      heartBtn.addEventListener('click', function () {
        var nowKst = getKstInfo();
        heartBtn.classList.add('is-tapped');
        setTimeout(function () {
          heartBtn.classList.remove('is-tapped');
        }, 160);
        triggerLoungeHeartIncrement(nowKst, true);
      });
    }

    // (5) 황영웅 최근 소식 & 영웅라디오 큰글씨 우편함 무료 정회원 등록 (#hero-passwordless-club-card)
    //     + 황영웅님께 담는 오늘의 사랑 & 응원 편지함 (#hero-love-letterbox) 초기화 및 온도계 연동
    initPasswordlessClubCard(function (nowKst) {
      triggerLoungeHeartIncrement(nowKst, false);
    });
    initLoveLetterbox(function (nowKst) {
      triggerLoungeHeartIncrement(nowKst, false);
    });

    // (6) 애장·건강 컬렉션 4대 스토리텔링 탭 범용 전환 보장 (인앱·로컬·모바일 환경 100% 동작)
    function switchStoryCollectionTab(tabKey, scrollIntoMarket) {
      var btns = document.querySelectorAll('.safe-theme-tab-btn[data-market-tab]');
      var panels = document.querySelectorAll('.safe-theme-panel[data-market-panel]');
      if (!btns.length || !panels.length) return;
      btns.forEach(function (b) {
        var active = b.getAttribute('data-market-tab') === tabKey;
        b.classList.toggle('active', active);
        b.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      panels.forEach(function (p) {
        var active = p.getAttribute('data-market-panel') === tabKey;
        p.classList.toggle('active', active);
      });
      if (scrollIntoMarket) {
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
        switchStoryCollectionTab(tabBtn.getAttribute('data-market-tab'), false);
        return;
      }
      var jumpLink = ev.target && ev.target.closest ? ev.target.closest('[data-open-market-tab]') : null;
      if (jumpLink && document.getElementById('senior-curation-market')) {
        ev.__heroMarketTabHandled = true;
        ev.preventDefault();
        switchStoryCollectionTab(jumpLink.getAttribute('data-open-market-tab'), true);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroFamilyLounge);
  } else {
    initHeroFamilyLounge();
  }

  window.HeroFamilyLounge = {
    getLetters: function () { return DAILY_HOST_LETTERS.slice(); },
    getDefaultLoveWall: function () { return DEFAULT_LOVE_LETTERS.slice(); },
    getKstInfo: getKstInfo,
    syncDailyAttendance: syncDailyAttendance
  };
})();
