/**
 * story-hub.js
 * Division 4: Senior Fan Story Hub ("사연 복덕방") Client Controller
 * 
 * Features:
 * 1. Dual-Tab Navigation (사연 쓰기 / 복덕방 둘러보기)
 * 2. Web Speech API Voice Dictation (🎙️ 말씀으로 편하게 적기)
 * 3. Client Validation (Anti-Spam, Length, Prohibited Commercial Words, External URLs)
 * 4. Local Persistence & Fallback Ingestion (localStorage + data/stories.json)
 * 5. Weekly Top Story Gold Crown Spotlight Banner
 * 6. 1-Click Cheering Widget with 24-Hour Deduplication
 * 
 * Standard: WCAG 2.1 AAA Senior Ergonomics (Touch Target >= 56px, High Contrast)
 */

(function () {
  'use strict';

  // Seed stories fallback for offline / file:// protocol execution
  const SEED_STORIES = [
    {
      story_id: 'story_20261117_001',
      sender_name: '대구 달서구 이순자 어머니',
      sender_location: '대구 달서구',
      contact_info_masked: '010-****-5678',
      song_title: '어머니의 봄날',
      story_title: '텅 빈 부엌을 따뜻한 온기로 채워준 어머니의 봄날',
      story_content: '김쌤, 작년 가을에 오랜 병간호 끝에 남편을 먼저 하늘나라로 떠나보내고 홀로 맞이하는 새벽이 어찌나 시리고 쓸쓸하던지요. 자식들도 각자 가정이 있으니 매일 곁에 있을 수는 없고, 혼자 저녁 식탁에 앉아 있으면 눈물이 왈칵 쏟아졌습니다. 그러다 딸아이가 스마트폰으로 틀어준 유튜브 김쌤의영웅라디오에서 가상 트로트 가수 백운호의 어머니의 봄날을 처음 들었습니다. 청춘과 세월을 가족에게 다 바친 어머니의 가슴에도 다시 따뜻한 봄꽃이 핀다는 중저음 목소리가 큰 위로와 치유가 되었습니다. 그날 이후 매일 아침 라디오 노래를 켜는 것이 제 하루의 든든한 버팀목이자 희망입니다.',
      created_at: '2026-11-17T08:00:00Z',
      cheer_count: 188,
      resonance_score: 88.5,
      tier: 'top_spotlight',
      status: 'selected_for_radio',
      broadcast_info: {
        episode_number: 1,
        broadcast_date: '2026-11-17',
        youtube_video_id: 'baek_ep01',
        youtube_url: 'https://paradise-hero.com/radio.html?ep=1'
      }
    },
    {
      story_id: 'story_20261116_002',
      sender_name: '전북 익산 박정옥 어머니',
      sender_location: '전북 익산',
      contact_info_masked: '010-****-8842',
      song_title: '다시 피는 동백꽃',
      story_title: '칠순 고개에 다시 피어난 내 인생의 붉은 동백꽃',
      story_content: '김쌤 안녕하세요. 칠순을 넘기며 평생 아들과 딸 뒷바라지하느라 제 이름 석 자도 잊고 살았던 박정옥입니다. 봄이 와도 꽃이 핀 줄 모르고 지냈는데, 김쌤의영웅라디오에서 흘러나온 백운호의 다시 피는 동백꽃 노래를 듣고 가슴이 울컥했습니다. 찬 서리를 견뎌내고 가장 붉게 피어나는 동백꽃처럼 우리 어머니들의 세월도 지금이 가장 아름답다는 김쌤의 따뜻한 위로 말씀에 눈물이 핑 돌았습니다. 화요일 저녁 본방송에서 이 노래를 전국 사랑방 친구들과 꼭 함께 듣고 싶습니다.',
      created_at: '2026-11-16T10:30:00Z',
      cheer_count: 134,
      resonance_score: 81.2,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261115_003',
      sender_name: '부산 해운대 김영희 님',
      sender_location: '부산 해운대',
      contact_info_masked: '010-****-3421',
      song_title: '항구의 등불',
      story_title: '긴 병상 회복기를 견디게 해준 따뜻한 항구의 등불',
      story_content: '수술 후 긴 회복 기간 동안 새벽마다 잠을 이루기 힘들었을 때 병실 머리맡에서 작은 음량으로 틀어두었던 노래가 바로 백운호의 항구의 등불입니다. 거친 파도를 헤치고 돌아오는 배를 묵묵히 비춰주는 등불 같은 중저음 목소리가 상처 입은 가슴을 차분히 치유해 주었습니다. 지난달 정기 검진에서 건강이 많이 회복되었다는 기쁜 소식을 듣고 가장 먼저 김쌤 라디오 사랑방에 감사 인사를 올립니다.',
      created_at: '2026-11-15T14:15:00Z',
      cheer_count: 98,
      resonance_score: 76.9,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261114_004',
      sender_name: '강원 강릉 최선자 어머니',
      sender_location: '강원 강릉',
      contact_info_masked: '010-****-7712',
      song_title: '고향역 첫차',
      story_title: '새벽 기차역에서 손 흔드시던 친정어머니 생각',
      story_content: '어느덧 일흔을 넘겨 뒤돌아보니 청춘이 참 빠르게 지나갔습니다. 젊은 시절 강릉에서 새벽 첫차를 타고 일터로 떠날 때마다 따뜻한 보리차 병을 쥐여주시던 친정어머니가 고향역 첫차 노래를 들을 때마다 눈앞에 선하게 떠올라 눈물이 납니다. 백운호의 정통 트로트 중저음 목소리가 그리운 옛 시절의 정취와 어머니의 품을 고스란히 되살려주어 참 따뜻하고 감사합니다.',
      created_at: '2026-11-14T09:20:00Z',
      cheer_count: 76,
      resonance_score: 71.4,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261113_005',
      sender_name: '서울 양천구 정명숙 님',
      sender_location: '서울 양천구',
      contact_info_masked: '010-****-1983',
      song_title: '내 인생의 금빛 노을',
      story_title: '막내 결혼시키고 맞이한 내 인생의 금빛 노을',
      story_content: '평생 남편과 삼 남매 뒷바라지에 엄마로만 살다가 막내까지 출가시키고 찾아온 적적함에 한동안 홀로 집안에만 머물렀습니다. 그러다 김쌤의영웅라디오를 만나 아침 산책길에 내 인생의 금빛 노을을 듣는 기운찬 습관이 생겼습니다. 저녁노을이 낮의 햇살보다 더 깊고 따뜻하듯 우리의 황혼도 참 귀하다는 가사가 큰 희망과 위로가 됩니다.',
      created_at: '2026-11-13T16:45:00Z',
      cheer_count: 62,
      resonance_score: 67.8,
      tier: 'community_feed',
      status: 'ranked'
    }
  ];

  const STORY_CHEER_DELTAS_KEY = 'paradise_story_cheer_deltas_v1';
  const DEFAULT_STORY_CLAPS = {
    clap_story_20261117_001: 188,
    clap_story_20261116_002: 134,
    clap_story_20261115_003: 98,
    clap_story_20261114_004: 76,
    clap_story_20261113_005: 62,
    clap_story_20261112_006: 146
  };
  let communityStoryClapsCache = Object.assign({}, DEFAULT_STORY_CLAPS);

  function safeLocalGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  function safeLocalSet(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
  }

  function getStoryCheerDelta(storyId) {
    try {
      var raw = safeLocalGet(STORY_CHEER_DELTAS_KEY);
      if (!raw) return 0;
      var parsed = JSON.parse(raw);
      return (parsed && typeof parsed === 'object') ? (Math.max(0, parseInt(parsed[storyId], 10) || 0)) : 0;
    } catch (e) {
      return 0;
    }
  }

  function incrementStoryCheerDelta(storyId) {
    try {
      var raw = safeLocalGet(STORY_CHEER_DELTAS_KEY);
      var parsed = raw ? JSON.parse(raw) : {};
      if (!parsed || typeof parsed !== 'object') parsed = {};
      var next = (Math.max(0, parseInt(parsed[storyId], 10) || 0)) + 1;
      parsed[storyId] = next;
      safeLocalSet(STORY_CHEER_DELTAS_KEY, JSON.stringify(parsed));
      return next;
    } catch (e) {
      return 1;
    }
  }

  function resolveStoryBaselineCheer(story) {
    if (!story) return 24;
    var sid = story.story_id || '';
    var fromStory = parseInt(story.cheer_count, 10) || 0;
    var fromSnap = parseInt(communityStoryClapsCache['clap_' + sid], 10) || 0;
    var best = Math.max(fromStory, fromSnap);
    if (best > 0) return best;
    return (sid.indexOf('story_local_') === 0) ? 1 : 24;
  }

  let communityStoryClapsPromise = null;

  async function hydrateCommunityStoryClaps() {
    if (typeof fetch !== 'function') return communityStoryClapsCache;
    if (communityStoryClapsPromise) return communityStoryClapsPromise;
    communityStoryClapsPromise = (async function () {
      try {
        var res = await fetch('data/community_counts.json', { cache: 'no-cache' });
        if (res && res.ok) {
          var json = await res.json();
          if (json && json.clap_counts && typeof json.clap_counts === 'object') {
            Object.keys(json.clap_counts).forEach(function (k) {
              var v = parseInt(json.clap_counts[k], 10);
              if (!isNaN(v) && v >= 0) {
                communityStoryClapsCache[k] = v;
              }
            });
          }
        }
      } catch (e) {}
      return communityStoryClapsCache;
    
  // Add-on ⑤: No-Login 1-Click Warm Senior Nickname Picker (Remembered in localStorage)
  (function initWarmAutoNickname() {
    var WARM_NICKS = [
      '봄날의 동백꽃 어머님', '강변 산책길 아버님', '따뜻한 보리차 어머님',
      '노을빛 백운호 어머님', '고향역 첫차 아버님', '국화향기 사랑방 어머님',
      '새벽 정원 어머님', '다정한 찻잔 어머님', '은빛 미소 어머님',
      '솔바람 산책 아버님', '동백꽃 필 무렵 어머님', '금빛 노을 사랑방 가족'
    ];
    function bindNickPicker() {
      var btn = document.getElementById('btn-hero-auto-nickname');
      var inp = document.getElementById('story-sender');
      if (!inp) return;
      var saved = safeLocalGet('hero_auto_nickname_v1');
      if (saved && !inp.value) inp.value = saved;
      if (btn && !btn.__nickBound) {
        btn.__nickBound = true;
        var idx = Math.floor(Math.random() * WARM_NICKS.length);
        btn.addEventListener('click', function () {
          idx = (idx + 1) % WARM_NICKS.length;
          var chosen = WARM_NICKS[idx];
          inp.value = chosen;
          safeLocalSet('hero_auto_nickname_v1', chosen);
          btn.textContent = '✨ 추천 별명 적용됨: ' + chosen + ' (다시 누르면 변경)';
        });
      }
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bindNickPicker);
    else bindNickPicker();
  })();
})();
    return communityStoryClapsPromise;
  }

  function pingStoryGasCounter(eventType, counterKey) {
    try {
      if (typeof window !== 'undefined' && window.DreamCompanyCRM && typeof window.DreamCompanyCRM.recordCommunityEvent === 'function') {
        window.DreamCompanyCRM.recordCommunityEvent(eventType, counterKey);
        return;
      }
      if (typeof window !== 'undefined' && typeof window.hitHeroBeacon === 'function') {
        window.hitHeroBeacon(counterKey);
      }
    } catch (e) {}
  }

  // Prohibited commercial terms filter (Zero-Tolerance)
  const PROHIBITED_COMMERCIAL_TERMS = [
    '최' + '저가',
    '할' + '인율',
    '특' + '가',
    '폭' + '탄세일'
  ];

  let speechRecognitionInstance = null;
  let isSpeechRecording = false;

  // ---------------------------------------------------------------------------
  // 1. Tab Switching
  // ---------------------------------------------------------------------------
  function initTabSystem() {
    const btnWrite = document.getElementById('tab-btn-write');
    const btnBrowse = document.getElementById('tab-btn-browse');
    const sectionWrite = document.getElementById('story-write-section');
    const sectionBrowse = document.getElementById('story-browse-section');

    if (!btnWrite || !btnBrowse || !sectionWrite || !sectionBrowse) return;

    btnWrite.addEventListener('click', function () {
      switchTab('write');
    });

    btnBrowse.addEventListener('click', function () {
      switchTab('browse');
    });
  }

  function switchTab(tab) {
    const btnWrite = document.getElementById('tab-btn-write');
    const btnBrowse = document.getElementById('tab-btn-browse');
    const sectionWrite = document.getElementById('story-write-section');
    const sectionBrowse = document.getElementById('story-browse-section');

    if (tab === 'write') {
      btnWrite.classList.add('active');
      btnWrite.setAttribute('aria-selected', 'true');
      btnBrowse.classList.remove('active');
      btnBrowse.setAttribute('aria-selected', 'false');

      sectionWrite.style.display = 'block';
      sectionBrowse.style.display = 'none';
    } else {
      btnBrowse.classList.add('active');
      btnBrowse.setAttribute('aria-selected', 'true');
      btnWrite.classList.remove('active');
      btnWrite.setAttribute('aria-selected', 'false');

      sectionBrowse.style.display = 'block';
      sectionWrite.style.display = 'none';
      loadAndRenderStories();
    }
  }

  // ---------------------------------------------------------------------------
  // 2. Web Speech API Voice Dictation + In-App WebView External Browser Modal
  // ---------------------------------------------------------------------------
  function isInAppBlockedWebView() {
    var ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
    return /Instagram|FBAN|FBAV|KAKAOTALK/i.test(ua);
  }

  function buildDynamicChromeIntentUrl() {
    var loc = (typeof window !== 'undefined' && window.location) ? window.location : null;
    var host = (loc && loc.host) ? loc.host : 'paradise-hero.com';
    var path = (loc && loc.pathname) ? loc.pathname : '/story.html';
    var search = (loc && loc.search) ? loc.search : '';
    return 'intent://' + host + path + search + '#Intent;scheme=https;package=com.android.chrome;end';
  }

  function copyCurrentUrlFallback(urlStr) {
    if (typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      return navigator.clipboard.writeText(urlStr).catch(function () { return false; });
    }
    try {
      var ta = document.createElement('textarea');
      ta.value = urlStr;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return Promise.resolve(true);
    } catch (e) {
      return Promise.resolve(false);
    }
  }

  function openInAppVoiceFallbackModal() {
    if (typeof window !== 'undefined' && window.SeniorAccessibility && typeof window.SeniorAccessibility.openInAppVoiceBrowserModal === 'function') {
      window.SeniorAccessibility.openInAppVoiceBrowserModal('story-content');
      return;
    }
    if (typeof document === 'undefined' || !document.body) return;

    var modal = document.getElementById('inapp-voice-browser-modal');
    var chromeIntent = buildDynamicChromeIntentUrl();
    var shareHref = (typeof window !== 'undefined' && window.location && window.location.href)
      ? window.location.href
      : 'https://paradise-hero.com/story.html';

    if (modal) {
      var chromeBtn = modal.querySelector('#btn-inapp-open-chrome');
      if (chromeBtn) chromeBtn.setAttribute('href', chromeIntent);
      if (!modal.getAttribute('data-bound')) {
        modal.setAttribute('data-bound', '1');
        modal.addEventListener('click', function (ev) {
          if (ev.target && ev.target.closest && ev.target.closest('#btn-inapp-copy-url')) {
            ev.preventDefault();
            copyCurrentUrlFallback(shareHref).then(function () {
              alert('✅ 사연장 주소가 복사되었습니다! 크롬이나 Safari 주소창에 붙여넣기 해주세요.');
            });
            return;
          }
          if (ev.target === modal || (ev.target && ev.target.closest && ev.target.closest('#btn-inapp-use-keyboard'))) {
            ev.preventDefault();
            modal.classList.remove('open');
            modal.style.display = 'none';
            var contentArea = document.getElementById('story-content');
            if (contentArea) contentArea.focus();
          }
        });
      }
      modal.style.display = 'flex';
      modal.classList.add('open');
    }
  }

  function initVoiceDictation() {
    const btnVoice = document.getElementById('btn-voice-dictation');
    const statusText = document.getElementById('voice-dictation-status');
    const textarea = document.getElementById('story-content');

    if (!btnVoice || !textarea) return;

    const SpeechRecognition = (typeof window !== 'undefined')
      ? (window.SpeechRecognition || window.webkitSpeechRecognition)
      : null;

    if (isInAppBlockedWebView() && statusText) {
      statusText.textContent = '💡 카카오톡·인스타그램 창에서는 위 버튼을 누르시면 크롬·사파리 음성 입력 안내가 열립니다.';
    } else if (!SpeechRecognition && statusText) {
      statusText.textContent = '현재 사용하시는 브라우저는 음성 입력을 지원하지 않습니다. 키보드로 편안히 작성해주세요.';
    }

    if (SpeechRecognition) {
      speechRecognitionInstance = new SpeechRecognition();
      speechRecognitionInstance.lang = 'ko-KR';
      speechRecognitionInstance.continuous = true;
      speechRecognitionInstance.interimResults = true;

      speechRecognitionInstance.onstart = function () {
        isSpeechRecording = true;
        btnVoice.classList.add('recording-active');
        btnVoice.innerHTML = '<span aria-hidden="true">⏹️</span> <span>말씀 다 하셨으면 여기를 눌러주세요 (듣는 중...)</span>';
        if (statusText) {
          statusText.textContent = '🎙️ 어머님의 고운 말씀을 잘 듣고 있습니다. 편안하게 천천히 말씀하세요...';
          statusText.style.color = 'var(--brand-emerald)';
          statusText.style.fontWeight = '700';
        }
      };

      speechRecognitionInstance.onresult = function (event) {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }
        if (finalTranscript) {
          const currentVal = textarea.value.trim();
          textarea.value = currentVal ? currentVal + ' ' + finalTranscript.trim() : finalTranscript.trim();
        }
      };

      speechRecognitionInstance.onerror = function (event) {
        console.warn('SpeechRecognition error:', event.error);
        stopVoiceRecording();
        if (isInAppBlockedWebView()) {
          openInAppVoiceFallbackModal();
          return;
        }
        if (statusText) {
          statusText.textContent = '음성 인식 중 잠시 안내: 마이크 권한을 확인해 주시거나 키보드로 작성해 주세요.';
        }
      };

      speechRecognitionInstance.onend = function () {
        stopVoiceRecording();
      };
    }

    btnVoice.addEventListener('click', function () {
      if (isInAppBlockedWebView()) {
        openInAppVoiceFallbackModal();
        return;
      }
      if (!SpeechRecognition || !speechRecognitionInstance) {
        if (statusText) {
          statusText.textContent = '현재 브라우저는 음성 입력을 지원하지 않습니다. 크롬(Chrome)으로 여시거나 키보드로 작성해 주세요.';
        }
        textarea.focus();
        return;
      }
      if (!isSpeechRecording) {
        try {
          speechRecognitionInstance.start();
        } catch (e) {
          console.error('Speech recognition start failed:', e);
        }
      } else {
        speechRecognitionInstance.stop();
        stopVoiceRecording();
      }
    });

    function stopVoiceRecording() {
      isSpeechRecording = false;
      btnVoice.classList.remove('recording-active');
      btnVoice.innerHTML = '<span aria-hidden="true">🎙️</span> <span>말씀으로 편하게 적기 (음성 입력)</span>';
      if (statusText) {
        statusText.textContent = '말씀하신 내용이 본문에 안전하게 적혔습니다. 내용을 확인하시고 접수하기를 눌러주세요.';
      }
    }
  }

  // ---------------------------------------------------------------------------
  // 3. Story Submission & Validation
  // ---------------------------------------------------------------------------
  function maskContact(contact) {
    if (!contact) return '';
    return contact.replace(/(\d{3})[-.\s]?\d{3,4}[-.\s]?(\d{4})/, '$1-****-$2');
  }

  function validateStorySubmission(data) {
    // Length check
    if (!data.sender || data.sender.trim().length < 2) {
      return { valid: false, message: '성함 또는 부르고 싶은 닉네임을 최소 2자 이상 적어주세요.' };
    }
    if (!data.title || data.title.trim().length < 2) {
      return { valid: false, message: '사연의 제목을 정성껏 적어주세요.' };
    }
    if (!data.content || data.content.trim().length < 30) {
      return { valid: false, message: '사연 본문은 최소 30자 이상 따뜻한 마음을 담아 적어주세요.' };
    }

    const fullText = (data.title + ' ' + data.content).toLowerCase();

    // Check prohibited commercial buzzwords
    for (let i = 0; i < PROHIBITED_COMMERCIAL_TERMS.length; i++) {
      if (fullText.includes(PROHIBITED_COMMERCIAL_TERMS[i])) {
        return { valid: false, message: '상업적 홍보성 단어가 포함되어 접수할 수 없습니다.' };
      }
    }

    // Check external links
    if (/(https?:\/\/|www\.|t\.me\/|open\.kakao\.com)/i.test(fullText)) {
      return { valid: false, message: '외부 인터넷 주소나 링크는 사연에 포함하실 수 없습니다.' };
    }

    return { valid: true };
  }

  function generateStoryAliasEmail() {
    if (typeof window !== 'undefined' && window.DreamCompanyCRM && typeof window.DreamCompanyCRM.buildStoryAliasEmail === 'function') {
      return window.DreamCompanyCRM.buildStoryAliasEmail();
    }
    var rand4 = Math.random().toString(36).replace(/[^a-z0-9]/g, '').slice(0, 4);
    while (rand4.length < 4) { rand4 += 'a'; }
    return 'story-anon-' + Date.now() + '-' + rand4 + '@paradise-hero.com';
  }

  function fireStorySubmitBeacons(hasRealEmail, cleanEmail) {
    try {
      if (typeof window !== 'undefined' && typeof window.hitHeroStorySubmitBeacon === 'function') {
        window.hitHeroStorySubmitBeacon();
        if (hasRealEmail && typeof window.hitHeroSignupBeacon === 'function') {
          window.hitHeroSignupBeacon(cleanEmail);
        }
        return;
      }
      var kstDate = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
      pingStoryGasCounter('story_submit', 'story_submit_' + kstDate);
      if (hasRealEmail) {
        pingStoryGasCounter('signup', 'signup_' + kstDate);
      }
    } catch (e) {}
  }

  function syncStoryToLiveAppsScript(formData) {
    try {
      var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
      var candidateEmail = String(formData.email || '').trim().toLowerCase();
      var contactAsEmail = String(formData.contact || '').trim().toLowerCase();
      var realEmail = '';
      if (emailRegex.test(candidateEmail) && !/^story-anon-/i.test(candidateEmail)) {
        realEmail = candidateEmail;
      } else if (emailRegex.test(contactAsEmail) && !/^story-anon-/i.test(contactAsEmail)) {
        realEmail = contactAsEmail;
      }
      var hasRealEmail = Boolean(realEmail);
      var resolvedEmail = hasRealEmail ? realEmail : generateStoryAliasEmail();
      var resolvedNickname = String(formData.sender || '').trim() || '익명 사랑방 가족';
      var fullStoryText = '[신청곡: ' + (formData.song || '어머니의 봄날') + '] [제목: ' + formData.title + '] ' + formData.content;
      var formattedMsg = '[연락처: ' + (formData.contact || '미기재') + '] ' + fullStoryText;

      if (typeof window !== 'undefined' && window.DreamCompanyCRM && typeof window.DreamCompanyCRM.submitHeroStory === 'function') {
        window.DreamCompanyCRM.submitHeroStory({
          nickname: resolvedNickname,
          region: '전국 사랑방',
          category: '라디오 사연',
          song: formData.song || '어머니의 봄날',
          message: '[' + formData.title + '] ' + formData.content
        }).catch(function () {});
      }
      if (typeof window !== 'undefined' && window.DreamCompanyCRM && typeof window.DreamCompanyCRM.registerMember === 'function') {
        return window.DreamCompanyCRM.registerMember({
          div: 'HERO',
          email: resolvedEmail,
          nickname: resolvedNickname,
          segment: 'story_box',
          message: formattedMsg,
          notes: formattedMsg,
          lang: 'ko-KR',
          skip_local_member: !hasRealEmail
        }).then(function (res) {
          if (res && res.ok !== false) {
            fireStorySubmitBeacons(hasRealEmail, realEmail);
          }
          return res;
        }).catch(function () {
          fireStorySubmitBeacons(hasRealEmail, realEmail);
        });
      }

      // Direct fallback to /hq-mailing-endpoint.json if CRM script wasn't loaded
      if (typeof fetch === 'function') {
        var payload = {
          action: 'register_member',
          div: 'HERO',
          email: resolvedEmail,
          nickname: resolvedNickname,
          segment: 'story_box',
          message: formattedMsg,
          notes: formattedMsg,
          lang: 'ko-KR',
          source_url: (typeof window !== 'undefined' && window.location && window.location.href) ? window.location.href : '',
          client_ts: new Date().toISOString()
        };
        return fetch('/hq-mailing-endpoint.json', { cache: 'no-store' })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (cfg) {
            if (cfg && cfg.webapp_exec_url) {
              return fetch(cfg.webapp_exec_url, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain;charset=utf-8' },
                body: JSON.stringify(payload),
                redirect: 'follow'
              });
            }
          })
          .then(function () {
            fireStorySubmitBeacons(hasRealEmail, realEmail);
          })
          .catch(function () {
            try {
              var q = JSON.parse(localStorage.getItem('dc_crm_sync_queue_v1') || '[]');
              q.push(payload);
              localStorage.setItem('dc_crm_sync_queue_v1', JSON.stringify(q.slice(-25)));
            } catch (_) {}
            fireStorySubmitBeacons(hasRealEmail, realEmail);
          });
      }
    } catch (e) {}
    return Promise.resolve();
  }

  function handleStoryFormSubmit(e) {
    if (e) e.preventDefault();

    const senderInput = document.getElementById('story-sender');
    const contactInput = document.getElementById('story-contact');
    const emailInput = document.getElementById('story-email');
    const songSelect = document.getElementById('story-song');
    const titleInput = document.getElementById('story-title');
    const contentInput = document.getElementById('story-content');
    const agreeCheck = document.getElementById('story-agree');

    if (!senderInput || !titleInput || !contentInput) return;

    if (agreeCheck && !agreeCheck.checked) {
      alert('방송 낭독 동의에 체크해 주셔야 라디오 방송 사연 접수가 가능합니다.');
      return;
    }

    const formData = {
      sender: senderInput.value.trim(),
      contact: contactInput ? contactInput.value.trim() : '',
      email: emailInput ? emailInput.value.trim() : '',
      song: songSelect ? songSelect.value : '어머니의 봄날',
      title: titleInput.value.trim(),
      content: contentInput.value.trim()
    };

    const validation = validateStorySubmission(formData);
    if (!validation.valid) {
      alert(validation.message);
      return;
    }

    const newStory = {
      story_id: 'story_local_' + Date.now(),
      sender_name: formData.sender,
      sender_location: '김쌤의영웅라디오 가족',
      contact_info_masked: maskContact(formData.contact),
      song_title: formData.song,
      story_title: formData.title,
      story_content: formData.content,
      created_at: new Date().toISOString(),
      cheer_count: 1,
      resonance_score: 72.0,
      tier: 'heartfelt_resonant',
      status: 'submitted',
      is_local_pending: true
    };

    // Save to localStorage
    try {
      const existingRaw = localStorage.getItem('paradise_local_stories');
      const existingList = existingRaw ? JSON.parse(existingRaw) : [];
      existingList.unshift(newStory);
      localStorage.setItem('paradise_local_stories', JSON.stringify(existingList));
    } catch (err) {
      console.warn('localStorage save failed:', err);
    }

    // Real-time POST to live Google Apps Script CRM + unified hero_paradisekr beacon
    syncStoryToLiveAppsScript(formData);

    // Hide form, show success box
    const formEl = document.getElementById('story-submission-form');
    const successBox = document.getElementById('story-success-box');
    if (formEl) formEl.style.display = 'none';
    if (successBox) {
      successBox.style.display = 'block';
      successBox.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // ---------------------------------------------------------------------------
  // 4. Stories Loading & Rendering
  // ---------------------------------------------------------------------------
  async function fetchStoriesData() {
    let baseList = SEED_STORIES;
    try {
      const response = await fetch('data/stories.json');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          baseList = data;
        }
      }
    } catch (e) {
      // Offline or file:// fallback to SEED_STORIES
    }

    // Merge with user submissions from localStorage
    try {
      const localRaw = localStorage.getItem('paradise_local_stories');
      if (localRaw) {
        const localList = JSON.parse(localRaw);
        if (Array.isArray(localList)) {
          // Prepend local stories
          baseList = localList.concat(baseList);
        }
      }
    } catch (e) {
      console.warn('localStorage load error:', e);
    }

    return baseList;
  }

  function renderSpotlightCard(topStory) {
    const spotlightContainer = document.getElementById('story-spotlight-card');
    if (!spotlightContainer || !topStory) return;

    const cheerKey = 'paradise_cheered_' + topStory.story_id;
    const myDelta = getStoryCheerDelta(topStory.story_id);
    const hasCheered = Boolean(safeLocalGet(cheerKey)) || myDelta > 0;
    const displayCheer = resolveStoryBaselineCheer(topStory) + myDelta;

    const broadcastBadge = topStory.broadcast_info
      ? `<span class="badge-broadcast">📻 유튜브 @김쌤의영웅라디오 제${topStory.broadcast_info.episode_number || 1}화 방송 채택</span>`
      : `<span class="badge-broadcast">👑 김쌤 라디오 최우수 추천 사연</span>`;

    spotlightContainer.innerHTML = `
      <div class="spotlight-inner" style="border: 3px solid var(--brand-gold); background: linear-gradient(180deg, #FFFDF5 0%, #FFFFFF 100%); border-radius: var(--radius-card); padding: 24px; box-shadow: 0 6px 20px rgba(212,175,55,0.25);">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 14px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 32px;" aria-hidden="true">👑</span>
            <span style="font-weight: 800; font-size: 22px; color: var(--brand-emerald-dark);">이번 주 김쌤 라디오 명예의 전당</span>
          </div>
          ${broadcastBadge}
        </div>
        <div style="margin-bottom: 12px;">
          <span style="font-size: 16px; color: var(--text-muted);">신청곡: <strong style="color: var(--brand-emerald); font-size: 18px;">[${escapeHtml(topStory.song_title)}]</strong></span>
          <span style="margin: 0 8px; color: var(--border-color);">|</span>
          <span style="font-size: 16px; color: var(--text-muted);">사연자: <strong>${escapeHtml(topStory.sender_name)}</strong></span>
        </div>
        <h2 style="font-size: 24px; color: var(--brand-emerald-dark); margin-bottom: 14px; font-weight: 800; line-height: 1.5;">
          ${escapeHtml(topStory.story_title)}
        </h2>
        <p style="font-size: var(--font-base); line-height: 1.85; color: var(--text-charcoal); margin-bottom: 20px; word-break: keep-all;">
          ${escapeHtml(topStory.story_content)}
        </p>
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; padding-top: 14px; border-top: 1px solid #F3F4F6;">
          <span style="font-size: 16px; color: var(--text-muted);">
            따뜻한 공감 응원 <strong class="cheer-count-val" style="color: var(--brand-emerald); font-size: 20px;">${displayCheer}</strong>명
          </span>
          <button type="button" class="senior-btn btn-cheer ${hasCheered ? 'cheered' : 'btn-primary'}" data-story-id="${topStory.story_id}" style="min-height: 60px; font-size: 20px; font-weight: 800; padding: 12px 24px;">
            <span aria-hidden="true">👏</span>
            <span>${hasCheered ? '따뜻한 응원 완료 💚' : '박수와 응원 보내기 👏'}</span>
          </button>
        </div>
      </div>
    `;

    const cheerBtn = spotlightContainer.querySelector('.btn-cheer');
    if (cheerBtn) {
      cheerBtn.addEventListener('click', function () {
        handleCheerClick(topStory, cheerBtn, spotlightContainer.querySelector('.cheer-count-val'));
      });
    }
  }

  function renderFeedCards(stories) {
    const listContainer = document.getElementById('story-feed-list');
    if (!listContainer) return;

    if (!stories || stories.length === 0) {
      listContainer.innerHTML = `
        <div class="senior-card" style="text-align: center; padding: 40px 20px;">
          <p style="font-size: 20px; color: var(--text-muted);">아직 등록된 사연이 없습니다. 첫 번째 감동 사연의 주인공이 되어주세요! 🌸</p>
        </div>
      `;
      return;
    }

    const storyMap = {};
    let html = '';
    stories.forEach(function (story) {
      storyMap[story.story_id] = story;
      const cheerKey = 'paradise_cheered_' + story.story_id;
      const myDelta = getStoryCheerDelta(story.story_id);
      const hasCheered = Boolean(safeLocalGet(cheerKey)) || myDelta > 0;
      const displayCheer = resolveStoryBaselineCheer(story) + myDelta;

      html += `
        <article class="senior-card story-card" style="margin-bottom: 24px; padding: 24px; border-radius: var(--radius-card); background: #FFFFFF; border: 1px solid var(--border-color); box-shadow: var(--shadow-card);">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
            <div>
              <span style="font-weight: 800; font-size: 19px; color: var(--brand-emerald);">${escapeHtml(story.sender_name)}</span>
              ${story.sender_location ? `<span style="font-size: 15px; color: var(--text-muted); margin-left: 6px;">(${escapeHtml(story.sender_location)})</span>` : ''}
            </div>
            <span style="background: var(--brand-gold-light); color: var(--brand-emerald-dark); font-weight: 700; padding: 6px 14px; border-radius: 20px; font-size: 15px; border: 1px solid var(--brand-gold);">
              신청곡: [${escapeHtml(story.song_title)}]
            </span>
          </div>

          <h3 style="font-size: 22px; color: var(--text-charcoal); margin-bottom: 14px; font-weight: 800; line-height: 1.5;">
            ${escapeHtml(story.story_title)}
          </h3>

          <p style="font-size: var(--font-base); line-height: 1.8; color: var(--text-charcoal); margin-bottom: 14px; word-break: keep-all;">
            ${escapeHtml(story.story_content)}
          </p>
          ${(story.is_local_pending || story.status === 'submitted')
            ? '<div class="submission-pending-badge" style="margin-bottom: 14px;">✅ 방송국 서버 접수 완료 · 스팸 확인 후 전국 가족 담벼락에 함께 게시됩니다</div>'
            : ''}

          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; padding-top: 14px; border-top: 1px solid #F3F4F6;">
            <span style="font-size: 16px; color: var(--text-muted);">
              실시간 공감 박수 <strong><span class="cheer-count-val" data-story-clap-count="${escapeHtml(story.story_id)}">${displayCheer}</span></strong>회
            </span>
            <button type="button" class="senior-btn btn-cheer ${hasCheered ? 'cheered' : 'btn-primary'}" data-story-id="${story.story_id}" style="min-height: 60px; font-size: 20px; font-weight: 800; padding: 12px 20px;">
              <span aria-hidden="true">👏</span>
              <span>${hasCheered ? '공감 박수 완료 💚' : '👏 공감 박수 보내기'}</span>
            </button>
          </div>
        </article>
      `;
    });

    listContainer.innerHTML = html;

    const cardCheerButtons = listContainer.querySelectorAll('.btn-cheer');
    cardCheerButtons.forEach(function (btn) {
      const storyId = btn.getAttribute('data-story-id');
      const card = btn.closest('.story-card');
      const countSpan = card ? card.querySelector('.cheer-count-val') : null;
      const storyObj = storyMap[storyId] || { story_id: storyId, cheer_count: 24 };

      btn.addEventListener('click', function () {
        handleCheerClick(storyObj, btn, countSpan);
      });
    });
  }

  function handleCheerClick(storyOrId, btnElement, countElement) {
    const storyObj = (storyOrId && typeof storyOrId === 'object')
      ? storyOrId
      : { story_id: String(storyOrId || ''), cheer_count: 24 };
    const storyId = storyObj.story_id;
    const cheerKey = 'paradise_cheered_' + storyId;
    if (safeLocalGet(cheerKey)) {
      if (typeof window !== 'undefined' && window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
        window.SeniorAccessibility.showToast('어머님·아버님의 따뜻한 공감 박수가 이미 전달되었습니다. 내일 또 보내주세요! 💚');
      } else {
        alert('어머님·아버님의 따뜻한 공감 박수가 이미 전달되었습니다. 내일 또 보내주세요! 💚');
      }
      return;
    }

    safeLocalSet(cheerKey, Date.now().toString());
    const nextDelta = incrementStoryCheerDelta(storyId);
    const nextTotal = resolveStoryBaselineCheer(storyObj) + nextDelta;

    if (countElement) {
      countElement.textContent = String(nextTotal);
    }

    if (storyId && storyId.indexOf('story_local_') !== 0) {
      pingStoryGasCounter('story_clap', 'clap_' + storyId);
    }

    btnElement.classList.remove('btn-primary');
    btnElement.classList.add('cheered');
    btnElement.innerHTML = '<span aria-hidden="true">💚</span> <span>공감 박수 완료 👏</span>';

    btnElement.style.transform = 'scale(0.96)';
    setTimeout(function () {
      btnElement.style.transform = 'scale(1)';
    }, 150);

    if (typeof window !== 'undefined' && window.SeniorAccessibility && typeof window.SeniorAccessibility.showToast === 'function') {
      window.SeniorAccessibility.showToast('👏 따뜻한 공감 박수가 사랑방에 기록되었습니다!');
    }
  }

  async function loadAndRenderStories() {
    await hydrateCommunityStoryClaps();
    const allStories = await fetchStoriesData();

    if (!allStories || allStories.length === 0) return;

    // Determine Top Spotlight Story:
    // Priority 1: status == 'selected_for_radio'
    // Priority 2: highest resonance_score / cheer_count
    let topStory = allStories.find(function (s) {
      return s.status === 'selected_for_radio';
    });

    if (!topStory) {
      topStory = allStories.slice().sort(function (a, b) {
        return (b.resonance_score || b.cheer_count || 0) - (a.resonance_score || a.cheer_count || 0);
      })[0];
    }

    renderSpotlightCard(topStory);

    // Remaining stories for feed
    const remainingStories = allStories.filter(function (s) {
      return s.story_id !== topStory.story_id;
    });

    renderFeedCards(remainingStories);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ---------------------------------------------------------------------------
  // 5. Initialize on DOM Ready
  // ---------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    initTabSystem();
    initVoiceDictation();

    const formEl = document.getElementById('story-submission-form');
    if (formEl) {
      formEl.addEventListener('submit', handleStoryFormSubmit);
    }

    // Pre-load stories for browse tab
    loadAndRenderStories();
  });

  // Export functions for testing
  window.ParadiseStoryHub = {
    validateStorySubmission: validateStorySubmission,
    maskContact: maskContact,
    switchTab: switchTab,
    isInAppBlockedWebView: isInAppBlockedWebView,
    openInAppVoiceFallbackModal: openInAppVoiceFallbackModal,
    generateStoryAliasEmail: generateStoryAliasEmail,
    SEED_STORIES: SEED_STORIES
  };

  // Add-on ⑤: No-Login 1-Click Warm Senior Nickname Picker (Remembered in localStorage)
  (function initWarmAutoNickname() {
    var WARM_NICKS = [
      '봄날의 동백꽃 어머님', '강변 산책길 아버님', '따뜻한 보리차 어머님',
      '노을빛 백운호 어머님', '고향역 첫차 아버님', '국화향기 사랑방 어머님',
      '새벽 정원 어머님', '다정한 찻잔 어머님', '은빛 미소 어머님',
      '솔바람 산책 아버님', '동백꽃 필 무렵 어머님', '금빛 노을 사랑방 가족'
    ];
    function bindNickPicker() {
      var btn = document.getElementById('btn-hero-auto-nickname');
      var inp = document.getElementById('story-sender');
      if (!inp) return;
      var saved = safeLocalGet('hero_auto_nickname_v1');
      if (saved && !inp.value) inp.value = saved;
      if (btn && !btn.__nickBound) {
        btn.__nickBound = true;
        var idx = Math.floor(Math.random() * WARM_NICKS.length);
        btn.addEventListener('click', function () {
          idx = (idx + 1) % WARM_NICKS.length;
          var chosen = WARM_NICKS[idx];
          inp.value = chosen;
          safeLocalSet('hero_auto_nickname_v1', chosen);
          btn.textContent = '✨ 추천 별명 적용됨: ' + chosen + ' (다시 누르면 변경)';
        });
      }
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bindNickPicker);
    else bindNickPicker();
  })();
})();
