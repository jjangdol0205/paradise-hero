/**
 * hero-family-lounge.js
 * 4사업부 「💚 영웅 가족 사랑방 — 김쌤의 오늘 안부 편지 & 1초 응원 하트」
 * - 무로그인 1초 참여 시니어 팬덤 동행 허브 (#hero-family-lounge)
 * - 날짜(YYYY-MM-DD KST) 기반 김쌤의 아침 안부 편지 7종 자동 순환
 * - 실시간 영웅 사랑방 응원 온도계 (36.5°C ~ 99.9°C 황금 온기 게이지 + Abacus 실시간 하트 집계)
 * - 연속 출석 도장 수첩 (localStorage: hero_lounge_attendance_v1) 7일 황금 도장판
 */

(function () {
  'use strict';

  var ATTENDANCE_STORAGE_KEY = 'hero_lounge_attendance_v1';
  var HEARTS_STORAGE_KEY = 'hero_lounge_hearts_v1';
  var ABACUS_NAMESPACE = 'hero_paradise';
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
    // 36.5°C 출발 -> 전국 가족 온기 합산 시 84°C~98.5°C 구간 도달 + 내 터치마다 +0.1°C 상승 (최대 99.9°C)
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

  function fetchInitialAbacusCount(kstInfo, heartState) {
    try {
      if (typeof fetch !== 'function') return;
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
      if (typeof fetch !== 'function') return;
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

      if (typeof window.__hitParadiseHeroMetric === 'function') {
        window.__hitParadiseHeroMetric('lounge_heart');
      }
    } catch (e) {}
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
  // 4. 전체 초기화
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

    // (4) 1초 응원 하트 버튼 클릭 핸들러 (무로그인·다회 클릭 즉시 반응·출석은 일 1회 보장)
    var heartBtn = document.getElementById('btn-hero-lounge-heart');
    if (heartBtn) {
      heartBtn.addEventListener('click', function () {
        var nowKst = getKstInfo();
        if (heartState.date !== nowKst.dateStr) {
          heartState = loadHeartState(nowKst);
        }

        heartState.myTodayHearts += 1;
        heartState.myTotalHearts += 1;
        heartState.displayTotal += 1;
        safeWriteJson(HEARTS_STORAGE_KEY, heartState);

        // 일일 출석은 하루 1회만 기록 유지
        var refreshedAttendance = syncDailyAttendance(nowKst);
        renderAttendanceUI(refreshedAttendance);

        // 버튼 터치 피드백 + 하트 축하 파티클 + 온도계 상승 + 안심 확인 토스트
        heartBtn.classList.add('is-tapped');
        setTimeout(function () {
          heartBtn.classList.remove('is-tapped');
        }, 160);

        spawnHeartCelebration();
        renderThermometerUI(heartState, true);
        showHeartConfirmationMessage('💚 어머님·아버님의 따뜻한 응원 하트가 영웅 사랑방 온도계에 전해졌습니다!');

        // 비차단 Abacus 카운터 전송
        hitAbacusHeartNonBlocking(nowKst, heartState);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroFamilyLounge);
  } else {
    initHeroFamilyLounge();
  }

  window.HeroFamilyLounge = {
    getLetters: function () { return DAILY_HOST_LETTERS.slice(); },
    getKstInfo: getKstInfo,
    syncDailyAttendance: syncDailyAttendance
  };
})();
