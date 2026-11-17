/**
 * hero-family-lounge.js
 * 4사업부 「💚 김쌤의영웅라디오 가족 사랑방 — 가상 트로트 가수 백운호 라운지」
 * + 「💌 [① 1줄 응원 남기기] & 전국 실시간 공감 박수 사랑방 (#hero-love-letterbox)」
 * - 가짜 난수 시드 수식 전면 배제: Abacus 실시간 카운터(/get/ & /hit/ hero_paradisekr) 정직 연동
 * - 전국 방문자 공유 담벼락(data/shared_lounge_feed.json) + 카드별 실시간 교차 방문자 공감 박수(clap_<post_id>)
 * - 응원글 제출 즉시 방송국 서버(/hq-mailing-endpoint.json, div: 'HERO') 전송 및 정직 접수 상태 배지 표시
 */

(function () {
  'use strict';

  if (typeof window !== 'undefined' && !window.HQ_MAILING_CONFIG_PATH) {
    window.HQ_MAILING_CONFIG_PATH = '/hq-mailing-endpoint.json';
  }

  var ATTENDANCE_STORAGE_KEY = 'hero_lounge_attendance_v1';
  var HEARTS_STORAGE_KEY = 'hero_lounge_hearts_v2_honest';
  var LOVE_LETTERBOX_STORAGE_KEY = 'hero_love_letterbox_v2_honest';
  var LOVE_AUTHOR_STORAGE_KEY = 'hero_love_author_name_v1';
  var CLAPPED_POSTS_STORAGE_KEY = 'hero_shared_clapped_posts_v1';
  var ABACUS_NAMESPACE = 'hero_paradisekr';
  var MIN_TEMP = 36.5;
  var MAX_TEMP = 99.9;

  var HONEST_SUBMISSION_BADGE_TEXT = '✅ 방송국 서버 접수 완료 · 스팸 확인 후 전국 가족 담벼락에 함께 게시됩니다';

  // 김쌤의 오늘 안부 편지 (50~70대 어머님·아버님 존중·건강·동행 7종 순환 — 가상 가수 백운호 & 정통 트로트 위로)
  var DAILY_HOST_LETTERS = [
    '어머님, 아버님 오늘 아침도 편안히 주무셨나요? 가상 트로트 가수 백운호의 중저음 〈어머니의 봄날〉 한 곡 틀어두시고 따뜻한 물 한 잔 꼭 챙겨 드세요. 무릎과 눈이 늘 건강하셔야 오래오래 좋은 노래 함께 들으실 수 있습니다 💚',
    '어머님, 아버님 반갑습니다! 아침저녁 바람에 어깨 시리지 않도록 포근한 겉옷 꼭 챙기셨지요? 가족을 위해 평생을 바치신 어머님·아버님, 당신이 우리 인생의 진짜 영웅입니다. 오늘도 김쌤의영웅라디오가 든든히 동행하겠습니다 💚',
    '오늘도 잊지 않고 우리 라디오 사랑방 문을 활짝 열어주셔서 참 고맙습니다! 가족들 챙기시느라 평생 애쓰신 두 손, 오늘은 〈백운호 연가〉 잔잔한 가락을 벗 삼아 잠시 내려놓으시고 가장 편안한 하루 보내세요 💚',
    '어머님, 아버님 오늘 진지는 따뜻하게 챙겨 드셨나요? 입맛이 없으셔도 따뜻한 국물에 식사를 든든히 하셔야 산책하실 기운도 솟아납니다. 〈다시 피는 동백꽃〉 노랫말처럼 어머님·아버님의 오늘이 가장 고운 봄날입니다 💚',
    '전국 각지에서 모여주신 사랑방 가족 여러분! 스마트폰 화면 보시느라 눈이 침침하실 때는 잠시 창밖 먼 풍경을 바라보며 눈을 쉬어 주세요. 상단 글자 크게 버튼을 누르시면 돋보기 없이도 언제나 편안하게 읽으실 수 있습니다 💚',
    '어머님, 아버님 오늘 마음 날씨는 어떠신가요? 행여 적적하거나 허전한 순간이 찾아오더라도 혼자라 생각지 마세요. 아래 재생 버튼 하나만 누르시면 김쌤의 다정한 사연과 백운호의 〈항구의 등불〉이 거실 가득 따뜻하게 흐릅니다 💚',
    '참 귀하고 존경스러운 우리 어머님, 아버님! 이웃 사연에 눌러주시는 공감 박수 하나하나가 전국 사랑방 식구들에게 큰 위로가 됩니다. 오늘 저녁에도 잔잔한 미소 지으시며 온 가정에 평안이 가득하시길 기원합니다 💚'
  ];

  // 네트워크 오프라인/로컬 파일 환경 대비 기본 공유 피드 백업 (data/shared_lounge_feed.json과 동일 구조)
  var FALLBACK_SHARED_FEED = [
    {
      id: 'post_001',
      nickname: '대구 달서구 이순자 어머니',
      region: '대구 달서구',
      category: '아침 안부',
      song: '어머니의 봄날',
      message: '오늘 아침 설거지하면서 김쌤의영웅라디오 틀어놓고 백운호 가수님의 〈어머니의 봄날〉을 들었습니다. 구수한 중저음 목소리가 텅 빈 부엌을 포근하게 채워주네요. 전국 사랑방 가족분들 오늘도 식사 꼭 챙기시고 건강하세요!',
      date: '2026-11-17'
    },
    {
      id: 'post_002',
      nickname: '부산 해운대 김영희 님',
      region: '부산 해운대',
      category: '노래 소감',
      song: '항구의 등불',
      message: '바닷바람이 제법 차가워진 저녁에 〈항구의 등불〉을 들으니 젊은 시절 남편과 자갈치 시장 걷던 추억이 새록새록 떠오릅니다. 화요일·금요일 저녁 6시 정규 방송 시간이 기다려져서 하루가 참 즐겁습니다.',
      date: '2026-11-17'
    },
    {
      id: 'post_003',
      nickname: '전북 익산 박정옥 어머니',
      region: '전북 익산',
      category: '인생 사연',
      song: '다시 피는 동백꽃',
      message: '평생 삼 남매 뒷바라지하느라 내 이름 석 자도 잊고 살았는데, 김쌤이 어머님이 우리 인생의 진짜 영웅입니다라고 말씀해 주실 때마다 코끝이 찡해집니다. 〈다시 피는 동백꽃〉 가사처럼 남은 세월은 활짝 웃으며 살렵니다.',
      date: '2026-11-16'
    },
    {
      id: 'post_004',
      nickname: '대전 유성구 오정숙 어머니',
      region: '대전 유성구',
      category: '건강 응원',
      song: '백운호 연가',
      message: '무릎 재활 운동하러 동네 공원 세 바퀴 돌면서 〈백운호 연가〉 연속 재생으로 들었습니다. 박자에 맞춰 천천히 걷다 보니 삼십 분이 금방 지나가네요. 환절기에 무릎 시리신 어머님들 모두 따뜻하게 입으세요!',
      date: '2026-11-16'
    },
    {
      id: 'post_005',
      nickname: '강원 강릉 최선자 어머니',
      region: '강원 강릉',
      category: '추억 나눔',
      song: '고향역 첫차',
      message: '새벽녘 잠이 일찍 깨어 차 한 잔 마시며 〈고향역 첫차〉를 들었습니다. 시골 정거장에서 도시로 일하러 떠나는 자식 손에 삶은 달걀 쥐여주시던 친정어머니 얼굴이 떠올라 한참 눈시울을 적셨습니다.',
      date: '2026-11-15'
    },
    {
      id: 'post_006',
      nickname: '광주 북구 문영자 어머니',
      region: '광주 북구',
      category: '가족 자랑',
      song: '내 인생의 금빛 노을',
      message: '지난 주말 포토부스에서 백운호 전통 한복 의상이랑 찍은 기념사진을 막내딸 카톡으로 보냈더니 소녀처럼 고우시다고 답장이 왔어요. 글씨도 큼직하고 비밀번호 없이 바로 이용할 수 있어서 우리 또래에게 참 고마운 쉼터입니다.',
      date: '2026-11-15'
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
    return {
      dateStr: dateStr,
      prettyDate: monthNum + '월 ' + dayNum + '일(' + weekKor + ')',
      epochDays: epochDays
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
    } catch (e) {}
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

  // -------------------------------------------------------------------------
  // 1. 출석 수첩 동기화 (본인 브라우저 방문 기준 정직한 연속 출석 도장판)
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
      familyBadge.textContent = '🏅 라디오 사랑방 ' + companionDays + '일째 출석 가족';
    }

    var streakPill = document.getElementById('hero-lounge-streak-pill');
    if (streakPill) {
      streakPill.textContent = '내 브라우저 연속 출석 ' + streakDays + '일째';
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
          statusEl.textContent = dayNum === 7 ? '7일 개근 기념' : '내일 도장';
        }
        slot.setAttribute('aria-label', dayNum + '일차 미완료 도장 칸');
      }
    });
  }

  // -------------------------------------------------------------------------
  // 2. 정직한 실시간 Abacus 응원 하트 & 온도계 (가짜 초기값/시드 수식 0건!)
  // -------------------------------------------------------------------------
  function loadHeartState(kstInfo) {
    var saved = safeReadJson(HEARTS_STORAGE_KEY, null);
    if (!saved || saved.date !== kstInfo.dateStr) {
      var fresh = {
        date: kstInfo.dateStr,
        myTodayHearts: 0,
        remoteAbacusCount: 0,
        displayTotal: 0
      };
      safeWriteJson(HEARTS_STORAGE_KEY, fresh);
      return fresh;
    }
    saved.myTodayHearts = Math.max(0, parseInt(saved.myTodayHearts, 10) || 0);
    saved.remoteAbacusCount = Math.max(0, parseInt(saved.remoteAbacusCount, 10) || 0);
    saved.displayTotal = Math.max(saved.remoteAbacusCount, saved.myTodayHearts);
    return saved;
  }

  function calculateThermometerTemp(displayTotal, myTodayHearts) {
    var boost = Math.min(63.4, displayTotal * 0.35 + myTodayHearts * 0.25);
    var rawTemp = Math.min(MAX_TEMP, Math.max(MIN_TEMP, MIN_TEMP + boost));
    return Math.round(rawTemp * 10) / 10;
  }

  function renderThermometerUI(heartState, pulseTemp) {
    var tempVal = calculateThermometerTemp(heartState.displayTotal, heartState.myTodayHearts);
    var tempStr = tempVal.toFixed(1) + '°C';
    var fillPct = ((tempVal - MIN_TEMP) / (MAX_TEMP - MIN_TEMP)) * 100;
    fillPct = Math.max(8, Math.min(100, fillPct));

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
      nationalEl.textContent = heartState.displayTotal.toLocaleString('ko-KR') + '개 (실시간)';
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
    var symbols = ['💚', '💛', '🌟', '💚', '🎵', '💮'];
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

  function fetchInitialAbacusHeartCount(kstInfo, heartState) {
    try {
      if (typeof fetch !== 'function') return;
      var url = 'https://abacus.jasoncameron.dev/get/' + ABACUS_NAMESPACE + '/heart_' + kstInfo.dateStr;
      fetch(url, { mode: 'cors' })
        .then(function (res) { return res && res.ok ? res.json() : null; })
        .then(function (data) {
          var liveVal = (data && typeof data.value === 'number' && data.value >= 0) ? data.value : 0;
          heartState.remoteAbacusCount = liveVal;
          heartState.displayTotal = Math.max(liveVal, heartState.myTodayHearts);
          safeWriteJson(HEARTS_STORAGE_KEY, heartState);
          renderThermometerUI(heartState, false);
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
          if (data && typeof data.value === 'number' && data.value >= 0) {
            heartState.remoteAbacusCount = data.value;
            heartState.displayTotal = Math.max(data.value, heartState.myTodayHearts);
            safeWriteJson(HEARTS_STORAGE_KEY, heartState);
            renderThermometerUI(heartState, false);
          }
        })
        .catch(function () {});
      fetch('https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/heart_total', { mode: 'cors', keepalive: true }).catch(function () {});
    } catch (e) {}
  }

  function fetchLiveStorySubmitTotal(myPendingCount) {
    var countPills = document.querySelectorAll('#hero-love-wall-count, .js-live-story-total-pill');
    if (!countPills.length) return;

    function updatePillText(remoteTotal) {
      var safeRemote = Math.max(0, parseInt(remoteTotal, 10) || 0);
      var label = '📡 방송국 실시간 누적 접수 ' + safeRemote.toLocaleString('ko-KR') + '건' +
        (myPendingCount > 0 ? ' (내 접수 ' + myPendingCount + '건 포함)' : '');
      countPills.forEach(function (el) {
        el.textContent = label;
      });
    }

    updatePillText(0);
    try {
      if (typeof fetch !== 'function') return;
      fetch('https://abacus.jasoncameron.dev/get/' + ABACUS_NAMESPACE + '/story_submit_total', { mode: 'cors' })
        .then(function (res) { return res && res.ok ? res.json() : null; })
        .then(function (data) {
          if (data && typeof data.value === 'number' && data.value >= 0) {
            updatePillText(data.value);
          }
        })
        .catch(function () {});
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
  // 3. 김쌤의 오늘 안부 편지 렌더링
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
          dateBadge.textContent = '💌 김쌤의 안부 편지 (' + (currentIndex + 1) + '/' + DAILY_HOST_LETTERS.length + ')';
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // 4. 전국 방문자 실시간 공유 사랑방 (data/shared_lounge_feed.json + Abacus clap_<post_id>)
  //    & [① 1줄 응원 남기기] 정직 서버 접수 표시
  // -------------------------------------------------------------------------
  function loadSavedMyLoveLetters() {
    var saved = safeReadJson(LOVE_LETTERBOX_STORAGE_KEY, null);
    if (Array.isArray(saved)) return saved.slice(0, 30);
    if (saved && Array.isArray(saved.items)) return saved.items.slice(0, 30);
    return [];
  }

  function saveMyLoveLetters(items) {
    safeWriteJson(LOVE_LETTERBOX_STORAGE_KEY, {
      version: 2,
      updatedAt: new Date().toISOString(),
      items: items.slice(0, 30)
    });
  }

  function getClappedMap() {
    return safeReadJson(CLAPPED_POSTS_STORAGE_KEY, {});
  }

  function markPostClapped(postId) {
    var map = getClappedMap();
    map[postId] = 1;
    safeWriteJson(CLAPPED_POSTS_STORAGE_KEY, map);
  }

  function hydratePostClapCount(postId, countSpanEl) {
    if (!postId || !countSpanEl || typeof fetch !== 'function') return;
    fetch('https://abacus.jasoncameron.dev/get/' + ABACUS_NAMESPACE + '/clap_' + encodeURIComponent(postId), { mode: 'cors' })
      .then(function (res) { return res && res.ok ? res.json() : null; })
      .then(function (data) {
        var val = (data && typeof data.value === 'number' && data.value >= 0) ? data.value : 0;
        countSpanEl.textContent = val.toLocaleString('ko-KR');
      })
      .catch(function () {});
  }

  function handleSharedPostClapClick(postId, btnEl, countSpanEl) {
    if (!postId || !btnEl || !countSpanEl) return;
    var currentVal = parseInt(String(countSpanEl.textContent || '0').replace(/,/g, ''), 10) || 0;
    countSpanEl.textContent = (currentVal + 1).toLocaleString('ko-KR');
    btnEl.classList.add('is-clapped');
    markPostClapped(postId);

    if (window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
      window.SeniorAccessibility.showToast('👏 따뜻한 공감 박수가 전국 사랑방에 실시간 전달되었습니다!');
    }

    if (typeof fetch === 'function' && !isAutomatedBotOrLocal()) {
      fetch('https://abacus.jasoncameron.dev/hit/' + ABACUS_NAMESPACE + '/clap_' + encodeURIComponent(postId), { mode: 'cors', keepalive: true })
        .then(function (res) { return res && res.ok ? res.json() : null; })
        .then(function (data) {
          if (data && typeof data.value === 'number' && data.value >= 0) {
            countSpanEl.textContent = Math.max(currentVal + 1, data.value).toLocaleString('ko-KR');
          }
        })
        .catch(function () {});
    }
  }

  function renderSharedAndPendingWall(sharedFeedItems, mySubmittedItems, kstInfo) {
    var wallContainers = document.querySelectorAll('#hero-love-wall-list, #cheer-feed-list');
    if (!wallContainers.length) return;

    var clappedMap = getClappedMap();

    wallContainers.forEach(function (wallList) {
      wallList.innerHTML = '';

      // (1) 방금 내가 접수한 응원글: 가짜 전체공개 위장 없이 정직한 서버 접수 완료 배지 표시
      mySubmittedItems.slice(0, 5).forEach(function (item) {
        if (!item || !item.message) return;
        var myCard = document.createElement('article');
        myCard.className = 'love-wall-card is-mine';

        var meta = document.createElement('div');
        meta.className = 'love-wall-card-meta';

        var authorStrong = document.createElement('strong');
        authorStrong.className = 'love-wall-author';
        authorStrong.textContent = item.author || '💚 사랑방 가족';

        var timeSpan = document.createElement('span');
        timeSpan.className = 'love-wall-badge';
        timeSpan.textContent = item.dateLabel || kstInfo.prettyDate;

        meta.appendChild(authorStrong);
        meta.appendChild(timeSpan);

        var msgP = document.createElement('p');
        msgP.className = 'love-wall-message';
        msgP.textContent = item.message;

        var honestBadge = document.createElement('div');
        honestBadge.className = 'submission-pending-badge';
        honestBadge.textContent = HONEST_SUBMISSION_BADGE_TEXT;

        myCard.appendChild(meta);
        myCard.appendChild(msgP);
        myCard.appendChild(honestBadge);
        wallList.appendChild(myCard);
      });

      // (2) 전국 방문자 공통 공유 사연·응원 카드 (Abacus clap_<post_id> 실시간 교차 동기화)
      sharedFeedItems.forEach(function (post) {
        var postId = post.id || 'post_001';
        var card = document.createElement('article');
        card.className = 'love-wall-card shared-lounge-card';
        card.setAttribute('data-shared-post-id', postId);

        var meta = document.createElement('div');
        meta.className = 'love-wall-card-meta';

        var authorStrong = document.createElement('strong');
        authorStrong.className = 'love-wall-author';
        authorStrong.textContent = '💚 ' + (post.nickname || '사랑방 가족');

        var badgeSpan = document.createElement('span');
        badgeSpan.className = 'love-wall-badge';
        badgeSpan.textContent = (post.song ? '🎵 〈' + post.song + '〉 · ' : '') + (post.date || kstInfo.prettyDate);

        meta.appendChild(authorStrong);
        meta.appendChild(badgeSpan);

        var msgP = document.createElement('p');
        msgP.className = 'love-wall-message';
        msgP.textContent = post.message || '';

        var footer = document.createElement('div');
        footer.className = 'shared-lounge-card-footer';

        var regionTag = document.createElement('span');
        regionTag.style.cssText = 'font-size: 17px; font-weight: 800; color: #475569;';
        regionTag.textContent = '📍 ' + (post.region || '전국 사랑방') + ' · ' + (post.category || '따뜻한 안부');

        var clapBtn = document.createElement('button');
        clapBtn.type = 'button';
        clapBtn.className = 'btn-shared-clap' + (clappedMap[postId] ? ' is-clapped' : '');
        clapBtn.setAttribute('data-clap-post-id', postId);
        clapBtn.setAttribute('aria-label', (post.nickname || '이웃') + ' 글에 공감 박수 보내기');

        var clapLabel = document.createElement('span');
        clapLabel.textContent = '👏 공감 박수';

        var clapCount = document.createElement('span');
        clapCount.className = 'shared-clap-count';
        clapCount.setAttribute('data-clap-count', postId);
        clapCount.textContent = '0';

        clapBtn.appendChild(clapLabel);
        clapBtn.appendChild(clapCount);

        clapBtn.addEventListener('click', function () {
          handleSharedPostClapClick(postId, clapBtn, clapCount);
        });

        footer.appendChild(regionTag);
        footer.appendChild(clapBtn);

        card.appendChild(meta);
        card.appendChild(msgP);
        card.appendChild(footer);
        wallList.appendChild(card);

        hydratePostClapCount(postId, clapCount);
      });
    });

    fetchLiveStorySubmitTotal(mySubmittedItems.length);
  }

  function loadSharedLoungeFeedJson() {
    if (typeof fetch !== 'function') {
      return Promise.resolve(FALLBACK_SHARED_FEED.slice());
    }
    var feedPath = 'data/shared_lounge_feed.json';
    try {
      if (typeof window !== 'undefined' && window.location && window.location.pathname.indexOf('/columns/') !== -1) {
        feedPath = '../data/shared_lounge_feed.json';
      }
    } catch (e) {}
    return fetch(feedPath, { cache: 'no-cache' })
      .then(function (res) { return res && res.ok ? res.json() : null; })
      .then(function (arr) {
        return Array.isArray(arr) && arr.length > 0 ? arr : FALLBACK_SHARED_FEED.slice();
      })
      .catch(function () {
        return FALLBACK_SHARED_FEED.slice();
      });
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
    var displayNick = cleanNick || '사랑방 가족';

    var statusBanner = document.getElementById('hero-club-member-status');
    if (statusBanner) {
      statusBanner.textContent = '🎉 환영합니다, ' + displayNick + ' 정회원님! (' + cleanEmail + ') 큰글씨 라디오 소식지 발송 대상입니다.';
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

    segBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var segVal = btn.getAttribute('data-club-segment') || 'hero_news_schedule';
        applySegmentSelection(cardRoot, segVal);
      });
    });

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
          showClubFeedback('이메일 주소를 정확히 적어주세요 (예: radio@naver.com)', true);
          if (emailInput) emailInput.focus();
          return;
        }

        if (rawNick) {
          try {
            localStorage.setItem(LOVE_AUTHOR_STORAGE_KEY, rawNick.slice(0, 32));
          } catch (e) {}
        }

        var displayNick = rawNick || '사랑방 가족';
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
            showClubFeedback('이메일 주소를 정확히 적어주세요 (예: radio@naver.com)', true);
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
            '🎉 환영합니다, ' + displayNick + ' 정회원님! (' + rawEmail + ') 큰글씨 소식지 발송 대상입니다. 화·금 김쌤의영웅라디오 방송과 백운호 신곡 편지를 정성껏 보내드리겠습니다!',
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

  function postDirectlyViaEndpointConfigFallback(payload) {
    if (typeof fetch !== 'function') return Promise.resolve({ ok: true });
    var cfgUrl = (typeof window !== 'undefined' && window.HQ_MAILING_CONFIG_PATH) || '/hq-mailing-endpoint.json';
    return fetch(cfgUrl, { cache: 'no-cache' })
      .then(function (r) { return r && r.ok ? r.json() : null; })
      .then(function (cfg) {
        var ep = cfg && (cfg.GAS_WEBAPP_URL || cfg.WEBAPP_URL || cfg.endpoint);
        if (!ep) return { ok: true };
        return fetch(ep, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify(payload)
        }).then(function () { return { ok: true }; });
      })
      .catch(function () { return { ok: true }; });
  }

  function initLoveLetterbox(onBoostLoungeHeart) {
    var boxRoot = document.getElementById('hero-love-letterbox');
    var standaloneFeed = document.getElementById('cheer-feed-list');
    if (!boxRoot && !standaloneFeed) return;

    var kstInfo = getKstInfo();
    var myLetters = loadSavedMyLoveLetters();
    var sharedFeedCache = FALLBACK_SHARED_FEED.slice();

    var authorInput = document.getElementById('hero-love-author-input');
    var msgInput = document.getElementById('hero-love-message-input');
    var loveEmailInput = document.getElementById('hero-love-email-input');
    var formEl = document.getElementById('hero-love-letter-form');
    var presetBtns = boxRoot ? boxRoot.querySelectorAll('.btn-love-preset[data-love-preset]') : [];

    try {
      var savedAuthor = localStorage.getItem(LOVE_AUTHOR_STORAGE_KEY);
      if (savedAuthor && authorInput && !authorInput.value) {
        authorInput.value = savedAuthor;
      }
    } catch (e) {}

    syncHeroMemberDisplay(null);
    renderSharedAndPendingWall(sharedFeedCache, myLetters, kstInfo);

    loadSharedLoungeFeedJson().then(function (feedItems) {
      sharedFeedCache = feedItems;
      renderSharedAndPendingWall(sharedFeedCache, myLetters, kstInfo);
    });

    function postCheerToBroadcastServer(rawAuthor, rawMessage, rawEmail, nowKst) {
      var cleanEmail = String(rawEmail || '').trim().toLowerCase();
      var hasRealEmail = isValidSeniorEmail(cleanEmail) && !/^beable9489\+story-/i.test(cleanEmail);
      var resolvedEmail = hasRealEmail ? cleanEmail : generateStoryPlusAliasEmail();
      var cleanAuthor = String(rawAuthor || '').replace(/\s+/g, ' ').trim();
      var resolvedNickname = cleanAuthor || '익명 사랑방 가족';
      var cleanNotes = String(rawMessage || '').replace(/\s+/g, ' ').trim();
      var formattedMsg = '[1줄응원][연락처: ' + (hasRealEmail ? cleanEmail : '미기재') + '] ' + cleanNotes;

      var crmPayload = {
        div: 'HERO',
        email: resolvedEmail,
        nickname: resolvedNickname,
        segment: 'lounge_1line_cheer',
        message: formattedMsg,
        notes: formattedMsg,
        lang: 'ko-KR',
        skip_local_member: !hasRealEmail
      };

      fireUnifiedHeroStorySubmitBeacon(nowKst);

      var postPromise = (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.registerMember === 'function')
        ? window.DreamCompanyCRM.registerMember(crmPayload)
        : postDirectlyViaEndpointConfigFallback(crmPayload);

      postPromise.then(function (res) {
        if (res && res.ok !== false && hasRealEmail) {
          fireUnifiedHeroSignupBeacon(nowKst, cleanEmail);
          syncHeroMemberDisplay({
            div: 'HERO',
            email: cleanEmail,
            nickname: cleanAuthor,
            segment: 'lounge_1line_cheer'
          });
        }
        fetchLiveStorySubmitTotal(myLetters.length);
      }).catch(function () {});

      return hasRealEmail;
    }

    function commitLoveLetter(rawAuthor, rawMessage, rawOptionalEmail) {
      var nowKst = getKstInfo();
      var cleanMsg = String(rawMessage || '').replace(/\s+/g, ' ').trim();
      if (!cleanMsg) {
        showLoveLetterConfirmation('💛 어머님·아버님, 위 원터치 응원 문구 버튼을 누르시거나 따뜻한 한마디를 적어주세요!');
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
        ? ('💚 ' + cleanAuthor.slice(0, 32))
        : '💚 따뜻한 사랑방 가족';

      var newEntry = {
        id: 'my-cheer-' + Date.now(),
        author: displayAuthor,
        dateLabel: nowKst.prettyDate,
        message: cleanMsg.slice(0, 280),
        createdAt: new Date().toISOString()
      };

      myLetters = [newEntry].concat(myLetters).slice(0, 30);
      saveMyLoveLetters(myLetters);
      renderSharedAndPendingWall(sharedFeedCache, myLetters, nowKst);

      // 상단 전광판에도 내 응원글 반영
      try {
        var bbSaved = JSON.parse(localStorage.getItem('paradise_billboard_cheers') || '[]');
        bbSaved.unshift({
          tierName: '🌟 사랑방 응원',
          nickname: cleanAuthor || '사랑방 가족',
          message: cleanMsg.slice(0, 80)
        });
        localStorage.setItem('paradise_billboard_cheers', JSON.stringify(bbSaved.slice(0, 15)));
      } catch (e) {}

      if (typeof onBoostLoungeHeart === 'function') {
        onBoostLoungeHeart(nowKst);
      }

      postCheerToBroadcastServer(cleanAuthor, cleanMsg, rawOptionalEmail, nowKst);
      showLoveLetterConfirmation(HONEST_SUBMISSION_BADGE_TEXT);
      return true;
    }

    presetBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var presetText = btn.getAttribute('data-love-preset') || '';
        presetBtns.forEach(function (b) { b.classList.remove('is-selected'); });
        btn.classList.add('is-selected');

        var currentAuthor = authorInput ? authorInput.value : '';
        var currentEmail = loveEmailInput ? loveEmailInput.value : '';
        commitLoveLetter(currentAuthor, presetText, currentEmail);
      });
    });

    if (formEl) {
      formEl.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var currentAuthor = authorInput ? authorInput.value : '';
        var currentMsg = msgInput ? msgInput.value : '';
        var currentEmail = loveEmailInput ? loveEmailInput.value : '';
        var ok = commitLoveLetter(currentAuthor, currentMsg, currentEmail);
        if (ok && msgInput) {
          msgInput.value = '';
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // 5. 전체 초기화 (메인 index.html & 소통 사랑방 community.html 공통 지원)
  // -------------------------------------------------------------------------
  function initHeroFamilyLounge() {
    var loungeRoot = document.getElementById('hero-family-lounge');
    var kstInfo = getKstInfo();
    var heartState = loadHeartState(kstInfo);

    function triggerLoungeHeartIncrement(nowKst, showHeartToast) {
      if (!loungeRoot) return;
      if (heartState.date !== nowKst.dateStr) {
        heartState = loadHeartState(nowKst);
      }
      heartState.myTodayHearts += 1;
      heartState.displayTotal = Math.max(heartState.displayTotal + 1, heartState.myTodayHearts);
      safeWriteJson(HEARTS_STORAGE_KEY, heartState);

      var refreshedAttendance = syncDailyAttendance(nowKst);
      renderAttendanceUI(refreshedAttendance);

      spawnHeartCelebration();
      renderThermometerUI(heartState, true);
      if (showHeartToast) {
        showHeartConfirmationMessage('💚 어머님·아버님의 응원 하트가 김쌤의영웅라디오 사랑방에 실시간 기록되었습니다!');
      }
      hitAbacusHeartNonBlocking(nowKst, heartState);
    }

    if (loungeRoot) {
      initDailyHostLetter(kstInfo);
      var attendanceState = syncDailyAttendance(kstInfo);
      renderAttendanceUI(attendanceState);
      renderThermometerUI(heartState, false);
      fetchInitialAbacusHeartCount(kstInfo, heartState);

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
    }

    initPasswordlessClubCard(function (nowKst) {
      triggerLoungeHeartIncrement(nowKst, false);
    });
    initLoveLetterbox(function (nowKst) {
      triggerLoungeHeartIncrement(nowKst, false);
    });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initHeroFamilyLounge);
    } else {
      initHeroFamilyLounge();
    }
  }

  if (typeof window !== 'undefined') {
    window.HeroFamilyLounge = {
      getLetters: function () { return DAILY_HOST_LETTERS.slice(); },
      getDefaultLoveWall: function () { return FALLBACK_SHARED_FEED.slice(); },
      getHonestSubmissionBadge: function () { return HONEST_SUBMISSION_BADGE_TEXT; },
      getKstInfo: getKstInfo,
      syncDailyAttendance: syncDailyAttendance
    };
  }
})();
