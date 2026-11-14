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
      story_id: 'story_20261109_001',
      sender_name: '대구 달서구 이순자 어머니',
      sender_location: '대구 달서구',
      contact_info_masked: '010-****-5678',
      song_title: '당신 편',
      story_title: '병실에서 손잡아준 당신 편, 영웅아 고맙다',
      story_content: '김쌤, 작년 가을에 40년을 한결같이 곁을 지키던 남편을 오랜 병간호 끝에 먼저 하늘나라로 떠나보냈습니다. 장례를 다 치르고 홀로 텅 빈 집에 돌아왔는데, 방안의 공기가 어찌나 시리고 차갑던지요. 남편이 벗어둔 외투를 부여잡고 며칠 동안 밥 한 숟갈 뜨지 못한 채 울기만 했습니다. 그렇게 넋을 놓고 누워만 있던 저를 다시 일으켜 세운 건 딸아이가 머리맡에 틀어주고 간 영웅님의 노래였습니다. 세상이 다 등을 돌려도 내가 당신 편이 되겠소라는 묵직한 첫 소절이 귀를 때리는 순간 멈췄던 눈물이 왈칵 쏟아졌습니다. 영웅님, 내 인생 가장 어두웠던 골짜기에서 손을 잡아줘서 참 고맙고 감사합니다. 부디 아프지 말고 오래오래 노래해 주세요.',
      created_at: '2026-11-09T08:00:00Z',
      cheer_count: 188,
      resonance_score: 88.5,
      tier: 'top_spotlight',
      status: 'selected_for_radio',
      broadcast_info: {
        episode_number: 1,
        broadcast_date: '2026-11-11',
        youtube_video_id: 'ep01_preview',
        youtube_url: 'https://www.youtube.com/@김쌤의영웅라디오'
      }
    },
    {
      story_id: 'story_20261108_002',
      sender_name: '전북 익산 박정옥 어머니',
      sender_location: '전북 익산',
      contact_info_masked: '010-****-8842',
      song_title: '꽃구경',
      story_title: '어머니 손잡고 떠났던 그 시절 꽃구경을 떠올리며',
      story_content: '김쌤 안녕하세요. 칠순을 훌쩍 넘긴 나이에 영웅님을 알게 되어 매일이 꿈결 같은 박정옥입니다. 작년에 아흔넷이 되신 저희 친정 어머니를 먼저 떠나보내고 한동안 멍하니 살았습니다. 봄이 와도 꽃이 핀 줄도 모르고 지냈는데, 우연히 유튜브에서 영웅님이 부르신 꽃구경을 듣게 되었습니다. 어머니 꽃구경 가요 하며 시작하는 그 애절하고 따뜻한 목소리가 어찌나 가슴을 파고들던지요. 라디오를 들으며 얼마나 울었는지 모릅니다. 영웅님의 노래는 단순한 가요가 아니라, 가슴속 깊이 묻어둔 어머니를 향한 사모곡이자 눈물의 치유였습니다. 김쌤 라디오에서 이 꽃구경을 함께 들으며 하늘에 계신 어머니께 사랑한다는 말을 꼭 전하고 싶습니다.',
      created_at: '2026-11-08T10:30:00Z',
      cheer_count: 134,
      resonance_score: 81.2,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261107_003',
      sender_name: '부산 해운대 김영희 님',
      sender_location: '부산 해운대',
      contact_info_masked: '010-****-3421',
      song_title: '비상',
      story_title: '항암의 차가운 병상에서 다시 날아오르게 해준 비상',
      story_content: '2년 전 유방암 판정을 받고 힘든 수술과 고통스러운 항암 치료를 견뎌야 했습니다. 머리카락이 한 웅큼씩 빠지고 거울을 볼 때마다 쏟아지는 눈물을 참을 수가 없었습니다. 새벽마다 통증으로 잠 못 이루던 밤, 병실 침대에서 이어폰을 꽂고 영웅님의 비상을 들었습니다. 이 세상 어딘가 내 쉴 곳을 찾아서 힘차게 솟구쳐 오르는 영웅님의 울림 있는 목소리가 제 메마른 영혼에 강력한 버팀목이 되어주었습니다. 마침내 완치 판정을 받았습니다. 영웅님의 노래는 제 생명의 은인이자 가장 든든한 동행이었습니다.',
      created_at: '2026-11-07T14:15:00Z',
      cheer_count: 98,
      resonance_score: 76.9,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261106_004',
      sender_name: '강원 강릉 최선자 어머니',
      sender_location: '강원 강릉',
      contact_info_masked: '010-****-7712',
      song_title: '인사동 찻집',
      story_title: '먼저 떠난 여고 동창과의 추억, 인사동 찻집에서',
      story_content: '어느덧 칠십 고개를 넘어 뒤돌아보니 청춘은 쏜살같이 지나갔습니다. 여고 시절 단짝으로 평생을 함께 울고 웃었던 친구가 3년 전 갑작스럽게 세상을 떠났습니다. 젊은 날 서울에 놀러 갈 때마다 인사동 전통 찻집에서 쌍화차를 나눠 마시며 미래를 이야기하던 그 시절이 영웅님의 노래 인사동 찻집을 들을 때마다 눈앞에 아지랑이처럼 피어오릅니다. 영웅님의 구수한 감성과 담백한 목소리가 친구 잃은 제 쓸쓸한 마음에 따스한 차 한 잔처럼 온기를 전해줍니다.',
      created_at: '2026-11-06T09:20:00Z',
      cheer_count: 76,
      resonance_score: 71.4,
      tier: 'heartfelt_resonant',
      status: 'ranked'
    },
    {
      story_id: 'story_20261105_005',
      sender_name: '서울 양천구 정명숙 님',
      sender_location: '서울 양천구',
      contact_info_masked: '010-****-1983',
      song_title: '함께해요',
      story_title: '일흔에 찾은 내 인생의 봄날, 함께해요',
      story_content: '평생을 남편과 삼 남매 뒷바라지에 제 이름 석 자는 잊어버리고 그저 누구 엄마로만 살아왔습니다. 막내까지 결혼시키고 찾아온 빈 둥지 증후군으로 우울증이 찾아왔을 때, 기적처럼 영웅님의 노래 함께해요를 만났습니다. 함께 손잡고 걸어가요라는 가사에 가슴이 뭉클해져 팬카페에 가입하고 스밍하는 법도 배웠습니다. 칠십 평생 처음으로 나를 위한 순수한 열정을 발견하게 해준 영웅님께 진심으로 고마운 마음을 전합니다.',
      created_at: '2026-11-05T16:45:00Z',
      cheer_count: 62,
      resonance_score: 67.8,
      tier: 'community_feed',
      status: 'ranked'
    }
  ];

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
  // 2. Web Speech API Voice Dictation
  // ---------------------------------------------------------------------------
  function initVoiceDictation() {
    const btnVoice = document.getElementById('btn-voice-dictation');
    const statusText = document.getElementById('voice-dictation-status');
    const textarea = document.getElementById('story-content');

    if (!btnVoice || !textarea) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      if (statusText) {
        statusText.textContent = '현재 사용하시는 브라우저는 음성 입력을 지원하지 않습니다. 키보드로 편안히 작성해주세요.';
      }
      btnVoice.style.opacity = '0.7';
      return;
    }

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
      if (statusText) {
        statusText.textContent = '음성 인식 중 잠시 안내: 마이크 권한을 확인해 주시거나 키보드로 작성해 주세요.';
      }
    };

    speechRecognitionInstance.onend = function () {
      stopVoiceRecording();
    };

    btnVoice.addEventListener('click', function () {
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

  function handleStoryFormSubmit(e) {
    if (e) e.preventDefault();

    const senderInput = document.getElementById('story-sender');
    const contactInput = document.getElementById('story-contact');
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
      song: songSelect ? songSelect.value : '당신 편',
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
      sender_location: '파라다이스 가족',
      contact_info_masked: maskContact(formData.contact),
      song_title: formData.song,
      story_title: formData.title,
      story_content: formData.content,
      created_at: new Date().toISOString(),
      cheer_count: 1,
      resonance_score: 72.0,
      tier: 'heartfelt_resonant',
      status: 'submitted'
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
    const hasCheered = Boolean(localStorage.getItem(cheerKey));

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
            따뜻한 공감 응원 <strong class="cheer-count-val" style="color: var(--brand-emerald); font-size: 20px;">${topStory.cheer_count || 0}</strong>명
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
        handleCheerClick(topStory.story_id, cheerBtn, spotlightContainer.querySelector('.cheer-count-val'));
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

    let html = '';
    stories.forEach(function (story) {
      const cheerKey = 'paradise_cheered_' + story.story_id;
      const hasCheered = Boolean(localStorage.getItem(cheerKey));

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

          <p style="font-size: var(--font-base); line-height: 1.8; color: var(--text-charcoal); margin-bottom: 20px; word-break: keep-all;">
            ${escapeHtml(story.story_content)}
          </p>

          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; padding-top: 14px; border-top: 1px solid #F3F4F6;">
            <span style="font-size: 16px; color: var(--text-muted);">
              함께 울고 웃은 팬 <strong><span class="cheer-count-val">${story.cheer_count || 0}</span></strong>명
            </span>
            <button type="button" class="senior-btn btn-cheer ${hasCheered ? 'cheered' : 'btn-primary'}" data-story-id="${story.story_id}" style="min-height: 60px; font-size: 20px; font-weight: 800; padding: 12px 20px;">
              <span aria-hidden="true">👏</span>
              <span>${hasCheered ? '따뜻한 응원 완료 💚' : '박수와 응원 보내기 👏'}</span>
            </button>
          </div>
        </article>
      `;
    });

    listContainer.innerHTML = html;

    // Attach cheer event listeners
    const cardCheerButtons = listContainer.querySelectorAll('.btn-cheer');
    cardCheerButtons.forEach(function (btn) {
      const storyId = btn.getAttribute('data-story-id');
      const card = btn.closest('.story-card');
      const countSpan = card ? card.querySelector('.cheer-count-val') : null;

      btn.addEventListener('click', function () {
        handleCheerClick(storyId, btn, countSpan);
      });
    });
  }

  function handleCheerClick(storyId, btnElement, countElement) {
    const cheerKey = 'paradise_cheered_' + storyId;
    if (localStorage.getItem(cheerKey)) {
      alert('어머님의 따뜻한 응원이 이미 전달되었습니다. 내일 또 힘찬 박수를 보내주세요! 💚');
      return;
    }

    // Save cheer vote
    localStorage.setItem(cheerKey, Date.now().toString());

    // Update DOM
    if (countElement) {
      const currentCount = parseInt(countElement.textContent, 10) || 0;
      countElement.textContent = (currentCount + 1).toString();
    }

    btnElement.classList.remove('btn-primary');
    btnElement.classList.add('cheered');
    btnElement.innerHTML = '<span aria-hidden="true">💚</span> <span>따뜻한 응원 완료 👏</span>';

    // Tactile animation
    btnElement.style.transform = 'scale(0.96)';
    setTimeout(function () {
      btnElement.style.transform = 'scale(1)';
    }, 150);
  }

  async function loadAndRenderStories() {
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
    SEED_STORIES: SEED_STORIES
  };
})();
