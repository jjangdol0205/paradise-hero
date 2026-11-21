/**
 * trot-news.js
 * Division 4: @김쌤의영웅라디오 화·금 정규 방송 편성표 & 가상 트로트 가수 백운호 신곡·사연 소식란 엔진
 * Target: paradise-hero.com (@김쌤의영웅라디오)
 *
 * - 가짜 신문사 기사 및 2024~2025 구 기사 0건
 * - 6대 정직 카테고리: 전체, 정규방송·편성표, 백운호 대표곡, 사랑방 사연소식, 시니어 건강상식, 라디오 이용안내
 * - 큰글씨 요약 모달(24px -> 28px -> 32px) + 김쌤의 콘서트·응원 안심 준비물관 공정위 문구 준수
 */

(function (global) {
  'use strict';

  const SINGER_LIST = [
    '전체',
    '정규방송·편성표',
    '백운호 대표곡',
    '사랑방 사연소식',
    '시니어 건강상식',
    '라디오 이용안내'
  ];

  const SEED_NEWS = [
    {
      id: 'radio_sched_001',
      title: '[정규 편성 안내] 매주 화요일·금요일 저녁 6시 유튜브 @김쌤의영웅라디오 15분 본방송',
      link: 'https://www.youtube.com/@%EA%B9%80%EC%8C%A4%EC%9D%98%EC%98%81%EC%9B%85%EB%9D%BC%EB%94%94%EC%98%A4',
      pubDate: '2026-11-17T09:00:00Z',
      source: '김쌤의영웅라디오 편성실',
      summary: '매주 화요일과 금요일 저녁 6시, 한 주 동안 접수된 어머님·아버님들의 따뜻한 인생 사연과 전속 가상 트로트 가수 백운호의 중저음 대표곡을 엮은 15분 정규 라디오 방송이 유튜브 채널에 공개됩니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '정규방송·편성표'
    },
    {
      id: 'radio_sched_002',
      title: '[1화 다시듣기] 남편 떠난 빈집을 적신 중저음 위로 · 백운호 〈어머니의 봄날〉 특집 방송',
      link: 'https://paradise-hero.com/radio.html?ep=1',
      pubDate: '2026-11-17T08:00:00Z',
      source: '유튜브 @김쌤의영웅라디오',
      summary: '홀로 맞이하는 계절을 따뜻하게 감싸 안아드리는 1화 사연 방송입니다. 가족을 위해 평생을 바치신 어머님께 바치는 백운호의 타이틀곡 〈어머니의 봄날〉과 함께 깊은 위로를 만나보세요.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '정규방송·편성표'
    },
    {
      id: 'radio_sched_003',
      title: '[2화·3화 다시듣기] 무릎 재활 산책길 동행 사연 & 시집가는 막내딸 축원 라디오 방송',
      link: 'https://paradise-hero.com/radio.html?ep=2',
      pubDate: '2026-11-16T18:00:00Z',
      source: '유튜브 @김쌤의영웅라디오',
      summary: '재활 걷기 운동을 버티게 해준 〈백운호 연가〉 사연(2화)과 막내딸을 시집보낸 저녁의 먹먹한 마음을 달래준 〈다시 피는 동백꽃〉 사연(3화)을 공식 유튜브 영상으로 바로 감상하실 수 있습니다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '정규방송·편성표'
    },
    {
      id: 'radio_sched_004',
      title: '[4화·5화 다시듣기] 칠순에 찾은 새 봄날 & 새벽 첫차 어머님 손길 추억 라디오 방송',
      link: 'https://paradise-hero.com/radio.html?ep=4',
      pubDate: '2026-11-15T18:00:00Z',
      source: '유튜브 @김쌤의영웅라디오',
      summary: '평생 가족 뒷바라지 끝에 맞이한 〈내 인생의 금빛 노을〉(4화)과 새벽 기차역의 추억이 담긴 〈고향역 첫차〉·〈항구의 등불〉(5화) 본방송을 광고 걱정 없이 편안하게 이어 들으실 수 있습니다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '정규방송·편성표'
    },
    {
      id: 'baek_song_001',
      title: '[백운호 탄생 이야기] 세월의 강을 건너온 우리네 어머니·아버지를 위한 중저음 위로',
      link: 'https://paradise-hero.com/columns/baek-woon-ho-debut-story.html',
      pubDate: '2026-11-18T07:30:00Z',
      source: '백운호 사랑방 편집실',
      summary: '실존 연예인이 아닌 오직 5070 시니어 가족분들의 음악 위로와 사연 소통을 위해 탄생한 『김쌤의영웅라디오』 전속 가상 트로트 가수 백운호(白雲湖)의 탄생 배경과 중저음 음악 철학을 큰 글씨로 전해드립니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '백운호 대표곡'
    },
    {
      id: 'baek_song_002',
      title: '[대표곡 가사 해설] 〈어머니의 봄날〉 — 자식 키우느라 잊고 산 봄날을 다시 불러드립니다',
      link: 'https://paradise-hero.com/columns/mothers-spring-day-lyric-story.html',
      pubDate: '2026-11-18T07:00:00Z',
      source: '백운호 음반 제작노트',
      summary: '거친 세월 앞치마에 눈물을 닦으시던 어머님들의 청춘을 따뜻하게 어루만지는 백운호 대표 타이틀곡 〈어머니의 봄날〉 노랫말 해설과 전국 사랑방 가족들의 사연을 담았습니다.',
      image_url: 'assets/characters/thumb_hero_style_01.png',
      singer_tag: '백운호 대표곡'
    },
    {
      id: 'baek_song_003',
      title: '[스튜디오 녹음 노트] 〈백운호 연가〉 — 호숫가 물안개처럼 잔잔히 스며드는 저녁 라디오 편지',
      link: 'https://paradise-hero.com/columns/baek-woon-ho-yeonga-radio-note.html',
      pubDate: '2026-11-17T11:00:00Z',
      source: '백운호 음반 제작노트',
      summary: '공원 산책길 편안한 보폭을 닮은 76 BPM 정통 트롯 왈츠 〈백운호 연가〉의 아날로그 스튜디오 녹음 비화와 저녁 쉼터 청취 사연을 큰 글씨 편지로 만나보세요.',
      image_url: 'assets/characters/thumb_hero_style_03.png',
      singer_tag: '백운호 대표곡'
    },
    {
      id: 'baek_song_004',
      title: '[신곡 응원 사연 모음] 〈다시 피는 동백꽃〉 — 인생 후반전, 오늘이 가장 젊은 날입니다',
      link: 'https://paradise-hero.com/columns/blooming-camellia-again-hope.html',
      pubDate: '2026-11-17T09:00:00Z',
      source: '백운호 음반 제작노트',
      summary: '찬 서리를 견뎌내고 누구보다 붉게 피어나는 동백꽃처럼, 자녀 뒷바라지를 마치고 인생 2막을 여신 어머님·아버님들을 응원하는 신곡 〈다시 피는 동백꽃〉 사연 모음입니다.',
      image_url: 'assets/characters/thumb_hero_style_04.png',
      singer_tag: '백운호 대표곡'
    },
    {
      id: 'lounge_story_001',
      title: '[사연 접수 안내] 이메일·비밀번호 없이도 1분 만에 라디오 사연과 1줄 응원을 남기실 수 있습니다',
      link: 'https://paradise-hero.com/story.html',
      pubDate: '2026-11-17T06:30:00Z',
      source: '김쌤의영웅라디오 작가실',
      summary: '복잡한 회원가입 없이 성함(또는 별명)과 사연만 적어 보내주시면 방송국 서버에 즉시 접수됩니다. 타자 입력이 불편하신 분들을 위해 마이크로 말씀하시면 글자로 적어주는 음성 받아쓰기 기능도 지원합니다.',
      image_url: 'assets/characters/thumb_hero_style_06.png',
      singer_tag: '사랑방 사연소식'
    },
    {
      id: 'lounge_story_002',
      title: '[전국 가족 담벼락] 부산·대구·강릉·익산 전국 사랑방 가족들의 실시간 공감 박수 소통 안내',
      link: 'https://paradise-hero.com/community.html',
      pubDate: '2026-11-16T09:30:00Z',
      source: '김쌤의영웅라디오 사랑방',
      summary: '사랑방 담벼락에 게시된 이웃 사연의 공감 박수 버튼을 누르시면 전국 어디서 접속하든 실시간으로 따뜻한 응원 박수 숫자가 함께 올라갑니다. 새로 보내주신 응원글은 스팸 확인 후 정식 게시됩니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '사랑방 사연소식'
    },
    {
      id: 'lounge_story_003',
      title: '[이달의 사연 주제] 내 인생 가장 고마웠던 한 사람 & 가을 산책길에 떠오르는 추억 모집',
      link: 'https://paradise-hero.com/story.html',
      pubDate: '2026-11-15T09:30:00Z',
      source: '김쌤의영웅라디오 작가실',
      summary: '평생 곁을 지켜준 배우자, 멀리 사는 자녀, 그리운 친정어머니, 혹은 여고 시절 단짝 친구에게 전하고 싶은 짧은 편지를 남겨주세요. 화·금 저녁 6시 정규 방송에서 김쌤이 정성껏 읽어드립니다.',
      image_url: 'assets/characters/thumb_hero_style_02.png',
      singer_tag: '사랑방 사연소식'
    },
    {
      id: 'lounge_story_004',
      title: '[정직 운영 원칙] 본 사랑방은 실존 연예인 팬카페가 아닌 오리지널 가상 가수 백운호 라디오 쉼터입니다',
      link: 'https://paradise-hero.com/index.html',
      pubDate: '2026-11-14T09:30:00Z',
      source: '김쌤의영웅라디오 운영팀',
      summary: '김쌤의영웅라디오의 영웅은 가족을 위해 평생을 바치신 어머님·아버님 여러분을 뜻합니다. 실존 연예인 사칭이나 혼동 없이, 순수 창작 가상 트로트 가수 백운호의 음악과 청취자 사연으로 정직하게 운영합니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '사랑방 사연소식'
    },
    {
      id: 'senior_health_001',
      title: '[환절기 건강 상식] 아침·저녁 기온 차 큰 계절, 시니어 심혈관·혈압 관리 및 산책 수칙',
      link: 'https://www.kdca.go.kr',
      pubDate: '2026-11-16T08:00:00Z',
      source: '질병관리청 건강정보 안내',
      summary: '기온이 급격히 내려가는 이른 새벽 산책보다는 햇살이 퍼지는 오전 10시 이후 얇은 옷을 여러 겹 겹쳐 입고 가벼운 보폭으로 걸으시는 것이 혈관 건강과 체온 유지에 큰 도움이 됩니다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '시니어 건강상식'
    },
    {
      id: 'senior_health_002',
      title: '[청취·눈 건강 가이드] 스마트폰 라디오 시청 시 눈 피로와 귀 피로를 줄이는 생활 습관',
      link: 'https://www.nhis.or.kr',
      pubDate: '2026-11-15T08:00:00Z',
      source: '국민건강보험 건강자료 안내',
      summary: '스마트폰 화면은 눈에서 30cm 이상 띄우고 본 사랑방 상단의 글자 크게 버튼을 활용해 눈의 긴장을 덜어주세요. 이어폰 음량은 최대 볼륨의 60% 이하로 맞추고 50분 청취 후 10분 휴식을 권장합니다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '시니어 건강상식'
    },
    {
      id: 'senior_health_003',
      title: '[목·호흡기 관리] 건조한 실내에서 노래를 따라 부르실 때 미지근한 수분 섭취가 중요한 이유',
      link: 'https://www.nhis.or.kr',
      pubDate: '2026-11-14T08:00:00Z',
      source: '국민건강보험 건강자료 안내',
      summary: '난방이 시작되는 계절에는 성대 점막이 쉽게 마를 수 있습니다. 카페인이 많은 진한 커피 대신 미지근한 물이나 따뜻한 도라지·배차를 조금씩 자주 드시면 목 잠김 예방에 좋습니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '시니어 건강상식'
    },
    {
      id: 'senior_health_004',
      title: '[어르신 문화·복지 정보] 보건복지상담센터(국번없이 129) 및 지역 어르신 문화 프로그램 확인하기',
      link: 'https://www.129.go.kr',
      pubDate: '2026-11-13T08:00:00Z',
      source: '보건복지상담센터 공공안내',
      summary: '우리 동네 노인복지관의 무료 건강교실, 노래교실, 예방접종 일정 및 일상 돌봄 상담이 필요하실 때는 보건복지상담센터 공식 누리집이나 국번 없이 129번을 통해 친절히 안내받으실 수 있습니다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '시니어 건강상식'
    },
    {
      id: 'radio_guide_001',
      title: '[본방송 활용법 & 건강 수칙] 화·금 저녁 6시 김쌤의영웅라디오 100% 즐기는 법 & 눈·목 편안한 청취 수칙',
      link: 'https://paradise-hero.com/columns/senior-radio-concert-wellness-guide.html',
      pubDate: '2026-11-18T06:00:00Z',
      source: '사랑방 도우미 안내',
      summary: '상단 글자 크게 3단계 조절 버튼과 음성 받아쓰기 사연 접수로 화·금 저녁 6시 15분 본방송을 편안하게 즐기시는 법, 그리고 눈·목 피로를 줄이는 청취 건강 수칙을 안내합니다.',
      image_url: 'assets/characters/thumb_hero_style_06.png',
      singer_tag: '라디오 이용안내'
    },
    {
      id: 'radio_guide_002',
      title: '[무료 포토부스 안내] 백운호 6대 무대 의상(에메랄드 정장~한복·DJ룩)과 다정한 기념사진 찍는 법',
      link: 'https://paradise-hero.com/booth.html',
      pubDate: '2026-11-16T06:00:00Z',
      source: '사랑방 도우미 안내',
      summary: '기념 촬영관에서 에메랄드 정장, 화이트 턱시도, 클래식 네이비 수트, 가을 코트, 전통 한복, 라디오 DJ룩 중 마음에 드는 의상을 고르고 내 사진만 올리시면 무료로 고화질 기념사진을 저장하실 수 있습니다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '라디오 이용안내'
    },
    {
      id: 'radio_guide_003',
      title: '[무료 선물관 안내] 카톡 아침 안부카드 · 큰글씨 달력 · 백운호 명곡 가사카드 100% 무료 저장',
      link: 'https://paradise-hero.com/vip.html',
      pubDate: '2026-11-15T06:00:00Z',
      source: '사랑방 도우미 안내',
      summary: '유료 결제나 회원가입 없이 누구나 무료로 이용하실 수 있는 디지털 선물관입니다. 친구와 자녀 단톡방에 보내기 좋은 요일별 꽃 안부카드와 음력 표시 큰글씨 달력을 바로 휴대폰에 담아보세요.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '라디오 이용안내'
    },
    {
      id: 'radio_guide_004',
      title: '[3초 무료 우편함] 비밀번호 없이 이메일만 적으면 화·금 라디오 방송 소식을 편지로 보내드립니다',
      link: 'https://paradise-hero.com/index.html#hero-passwordless-club-card',
      pubDate: '2026-11-14T06:00:00Z',
      source: '사랑방 도우미 안내',
      summary: '아이디나 비밀번호를 외우실 필요 없이 이메일 주소 하나로 무료 우편함 회원이 되실 수 있습니다. 매주 새 라디오 사연 방송 소식과 계절 건강 편지를 큰글씨로 보내드리며 언제든 1클릭 수신거부가 가능합니다.',
      image_url: 'assets/baek_woon_ho_main.png',
      singer_tag: '라디오 이용안내'
    }
  ];

  class TrotNewsEngine {
    constructor(initialArticles = null) {
      this.articles = Array.isArray(initialArticles) ? initialArticles : [];
      this.activeSinger = '전체';
      this.searchQuery = '';
      this.currentModalArticle = null;
      this.modalFontLevel = 'normal';
      this.isModalOpen = false;
    }

    async loadNews(customFetch = null) {
      if (this.articles.length > 0) {
        return this.articles;
      }

      const fetchFn = customFetch || (typeof fetch === 'function' ? fetch : null);

      if (fetchFn) {
        try {
          const res = await fetchFn('data/trot_news.json');
          if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
              this.articles = data;
              return this.articles;
            }
          }
        } catch (e) {
          // Fall back gracefully
        }
      }

      this.articles = SEED_NEWS.slice();
      return this.articles;
    }

    setSingerFilter(singer) {
      if (SINGER_LIST.includes(singer) || singer === '전체') {
        this.activeSinger = singer;
      } else {
        this.activeSinger = '전체';
      }
      return this.getFilteredArticles();
    }

    setSearchQuery(query) {
      this.searchQuery = typeof query === 'string' ? query.trim() : '';
      return this.getFilteredArticles();
    }

    getFilteredArticles() {
      let filtered = this.articles;

      if (this.activeSinger && this.activeSinger !== '전체') {
        filtered = filtered.filter((item) => item.singer_tag === this.activeSinger);
      }

      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter((item) => {
          const t = (item.title || '').toLowerCase();
          const s = (item.summary || '').toLowerCase();
          const src = (item.source || '').toLowerCase();
          const tag = (item.singer_tag || '').toLowerCase();
          return t.includes(q) || s.includes(q) || src.includes(q) || tag.includes(q);
        });
      }

      return filtered;
    }

    getArticleById(id) {
      return this.articles.find((a) => a.id === id) || null;
    }

    openModal(id) {
      const article = this.getArticleById(id);
      if (!article) return null;

      this.currentModalArticle = article;
      this.isModalOpen = true;
      return article;
    }

    closeModal() {
      this.currentModalArticle = null;
      this.isModalOpen = false;
    }

    toggleModalFont() {
      if (this.modalFontLevel === 'normal') {
        this.modalFontLevel = 'large';
      } else if (this.modalFontLevel === 'large') {
        this.modalFontLevel = 'xlarge';
      } else {
        this.modalFontLevel = 'normal';
      }
      return this.modalFontLevel;
    }

    getModalFontSizePx() {
      switch (this.modalFontLevel) {
        case 'large':
          return 28;
        case 'xlarge':
          return 32;
        case 'normal':
        default:
          return 24;
      }
    }
  }

  function initBrowserUI() {
    if (typeof document === 'undefined') return;

    const engine = new TrotNewsEngine();

    const pillsContainer = document.getElementById('singer-pills-container');
    const heroContainer = document.getElementById('news-hero-spotlight');
    const feedContainer = document.getElementById('news-feed-grid');
    const searchInput = document.getElementById('news-search-input');
    const searchClearBtn = document.getElementById('btn-clear-search');
    const resultCountEl = document.getElementById('news-result-count');

    const modalEl = document.getElementById('senior-news-modal');
    const modalCloseBtn = document.getElementById('btn-close-modal');
    const modalFontScalerBtn = document.getElementById('btn-modal-font-scaler');
    const modalBadgeEl = document.getElementById('modal-singer-badge');
    const modalOutletEl = document.getElementById('modal-outlet-name');
    const modalDateEl = document.getElementById('modal-pub-date');
    const modalTitleEl = document.getElementById('modal-news-title');
    const modalBodyEl = document.getElementById('modal-news-body');
    const modalLinkEl = document.getElementById('btn-modal-external-link');
    const modalShareBtn = document.getElementById('btn-modal-share');

    function formatDate(isoStr) {
      if (!isoStr) return '';
      try {
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return isoStr;
        return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
      } catch (e) {
        return isoStr;
      }
    }

    function renderPills() {
      if (!pillsContainer) return;
      pillsContainer.innerHTML = '';

      SINGER_LIST.forEach((category) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pill-btn' + (engine.activeSinger === category ? ' active' : '');
        btn.setAttribute('aria-pressed', engine.activeSinger === category ? 'true' : 'false');
        btn.setAttribute('data-singer', category);
        btn.innerHTML = `<span class="pill-dot" aria-hidden="true"></span><span>${category}</span>`;

        btn.addEventListener('click', () => {
          engine.setSingerFilter(category);
          updateUI();
        });

        pillsContainer.appendChild(btn);
      });
    }

    function renderHero(article) {
      if (!heroContainer) return;
      if (!article) {
        heroContainer.innerHTML = '';
        heroContainer.style.display = 'none';
        return;
      }

      heroContainer.style.display = 'block';
      const formattedDate = formatDate(article.pubDate);

      heroContainer.innerHTML = `
        <article class="hero-spotlight-card senior-card" aria-label="김쌤의영웅라디오 주요 편성 및 소식">
          <div class="hero-badge-row">
            <span class="spotlight-tag">📻 김쌤의영웅라디오 주요 안내</span>
            <span class="singer-tag-badge">${article.singer_tag}</span>
            <span class="outlet-badge">${article.source}</span>
            <span class="date-badge">${formattedDate}</span>
          </div>
          <div class="hero-content-split">
            <div class="hero-thumb-wrapper">
              <img src="${article.image_url}" alt="${article.title} 안내 이미지" class="hero-thumb-img" data-csp-fallback-src="assets/baek_woon_ho_main.png">
            </div>
            <div class="hero-text-col">
              <h2 class="hero-news-title">
                <a href="#view-${article.id}" class="news-title-link" data-id="${article.id}">${article.title}</a>
              </h2>
              <p class="hero-news-summary">${article.summary}</p>
              <div class="hero-action-row">
                <button type="button" class="senior-btn btn-primary btn-read-large" data-id="${article.id}" aria-label="${article.title} 큰 글씨로 편하게 읽기">
                  <span aria-hidden="true">🔍</span> 큰 글씨로 편하게 읽기
                </button>
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="senior-btn btn-outline" aria-label="관련 페이지 바로 열기">
                  <span aria-hidden="true">🌐</span> 바로 이동하기
                </a>
              </div>
            </div>
          </div>
        </article>
      `;
    }

    function createPhotoBoothCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-booth senior-card';
      banner.setAttribute('aria-label', '가상 트로트 가수 백운호 무료 투샷 사진관 바로가기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📸</div>
          <div class="cta-text-col">
            <span class="cta-kicker">회원가입 없는 무료 기념관</span>
            <h3 class="cta-heading">가상 트로트 가수 백운호 6대 무대 의상 투샷 포토부스</h3>
            <p class="cta-description">에메랄드 정장, 화이트 턱시도, 전통 한복, 라디오 DJ룩 등 6가지 의상과 함께 기념사진을 무료로 남겨보세요.</p>
          </div>
          <div class="cta-btn-col">
            <a href="booth.html" class="senior-btn btn-gold cta-action-btn">
              <span>무료 기념사진 찍기 👉</span>
            </a>
          </div>
        </div>
      `;
      return banner;
    }

    function createRadioCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-radio senior-card';
      banner.setAttribute('aria-label', '김쌤의영웅라디오 방송 듣기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📻</div>
          <div class="cta-text-col">
            <span class="cta-kicker">유튜브 @김쌤의영웅라디오</span>
            <h3 class="cta-heading">백운호 〈어머니의 봄날〉과 따뜻한 인생 사연 연속 방송</h3>
            <p class="cta-description">화요일·금요일 저녁 6시 정규 라디오 방송과 지난 1~5화 사연 방송을 지금 바로 편안하게 들어보세요.</p>
          </div>
          <div class="cta-btn-col">
            <a href="radio.html" class="senior-btn btn-primary cta-action-btn">
              <span>라디오 들으러 가기 🎵</span>
            </a>
          </div>
        </div>
      `;
      return banner;
    }

    function getContextShopItems(tag) {
      const t = String(tag || '');
      if (t.indexOf('건강') !== -1) {
        return [
          {
            img: 'assets/shop/item_lutein.svg',
            badge: '청취 건강 케어',
            title: '눈 침침함 케어 루테인 지아잔틴',
            reason: '스마트폰으로 라디오 사연을 읽으실 때 침침한 눈 건강을 챙겨드립니다.',
            url: 'https://cshop.naver.com/paradiseshop',
            bg: '#03C75A',
            cta: '🟢 공식 판매처 보러가기 (네이버페이) 👉'
          },
          {
            img: 'assets/shop/item_doraji.svg',
            badge: '청취 건강 케어',
            title: '목이 편안한 도라지배즙 스틱',
            reason: '트로트 명곡을 따라 부르실 때 칼칼한 목을 촉촉하게 보호해 드립니다.',
            url: 'https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_news&pageKey=%EB%8F%84%EB%9D%BC%EC%A7%80%EB%B0%B0%EC%A6%99+%EC%8A%A4%ED%8B%B1',
            bg: '#B91C1C',
            cta: '🚀 공식 판매처 보러가기 (쿠팡) 👉'
          }
        ];
      }
      return [
        {
          img: 'assets/shop/item_speaker.svg',
          badge: '음반·청취 필수품',
          title: '백운호·정통 트로트 감상용 효도 블루투스 라디오 스피커',
          reason: '큼직한 버튼 하나로 거실 가득 풍성한 중저음 라디오를 들으실 수 있습니다.',
          url: 'https://cshop.naver.com/paradiseshop',
          bg: '#03C75A',
          cta: '🟢 공식 판매처 보러가기 (네이버페이) 👉'
        },
        {
          img: 'assets/shop/item_cushion.svg',
          badge: '공연·나들이 준비물',
          title: '3시간 공연장 푹신 메모리폼 방석',
          reason: '오래 앉아 계셔도 허리와 무릎 부담을 덜어주는 접이식 메모리폼 방석입니다.',
          url: 'https://influencers.coupang.com/s/paradisehero',
          bg: '#B91C1C',
          cta: '🚀 공식 판매처 보러가기 (쿠팡 공식관) 👉'
        }
      ];
    }

    function renderShopCardsInnerHtml(items) {
      return items.map((it) => `
        <div style="background:#FAFAF8;border:2px solid #D1D5DB;border-radius:16px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;gap:14px;">
          <div style="display:flex;gap:14px;align-items:center;">
            <img src="${it.img}" alt="${it.title}" width="88" height="88" style="width:88px;height:88px;flex-shrink:0;border-radius:14px;background:#ECFDF5;border:2px solid #10B981;padding:8px;object-fit:contain;">
            <div>
              <span style="display:inline-block;background:#FEF3C7;color:#92400E;font-size:16px;font-weight:900;padding:3px 10px;border-radius:999px;margin-bottom:4px;">${it.badge}</span>
              <div style="font-size:21px;font-weight:900;color:#111827;line-height:1.35;margin-bottom:4px;">${it.title}</div>
              <div style="font-size:19px;font-weight:700;color:#374151;line-height:1.45;">${it.reason}</div>
            </div>
          </div>
          <a href="${it.url}" target="_blank" rel="noopener noreferrer sponsored" style="display:flex;align-items:center;justify-content:center;text-align:center;min-height:64px;padding:12px 16px;border-radius:14px;background:${it.bg};color:#FFFFFF;font-size:20px;font-weight:900;text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
            ${it.cta}
          </a>
        </div>
      `).join('');
    }

    function createOneTapShopBanner(tag) {
      const items = getContextShopItems(tag);
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta senior-card';
      banner.setAttribute('aria-label', '김쌤의 콘서트·응원 안심 준비물관');
      banner.style.cssText = 'background:#FFFFFF;border:3px solid #D4AF37;border-radius:18px;padding:22px;margin:20px 0;';
      banner.innerHTML = `
        <div style="font-size:23px;font-weight:900;color:#0E2820;margin-bottom:6px;">💚 김쌤의 콘서트·응원 안심 준비물관 추천 2선</div>
        <p style="margin:0 0 14px;font-size:19px;color:#374151;font-weight:700;">라디오 청취와 공연 나들이 때 꼭 필요한 실속 준비물을 에디터 큐레이션으로 모았습니다.</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:14px;">
          ${renderShopCardsInnerHtml(items)}
        </div>
        <p class="ftc-inline-disclosure" style="margin:12px 0 0;">※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다.</p>
      `;
      return banner;
    }

    function renderFeed(articles) {
      if (!feedContainer) return;
      feedContainer.innerHTML = '';

      if (articles.length === 0) {
        feedContainer.innerHTML = `
          <div class="no-results-card senior-card">
            <p class="no-results-icon" aria-hidden="true">🔎</p>
            <h3 class="no-results-title">검색된 라디오·편성 소식이 없습니다</h3>
            <p class="no-results-desc">다른 분야 버튼을 누르시거나 검색어를 지워주세요.</p>
            <button type="button" class="senior-btn btn-gold btn-reset-filters">
              <span>전체 편성·소식 보기</span>
            </button>
          </div>
        `;
        const resetBtn = feedContainer.querySelector('.btn-reset-filters');
        if (resetBtn) {
          resetBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            engine.setSearchQuery('');
            engine.setSingerFilter('전체');
            updateUI();
          });
        }
        return;
      }

      const displayList = articles.length > 1 ? articles.slice(1) : articles;

      displayList.forEach((article, idx) => {
        if (idx === 1) {
          feedContainer.appendChild(createOneTapShopBanner(engine.activeSinger || article.singer_tag));
        }
        if (idx === 3) {
          feedContainer.appendChild(createPhotoBoothCTA());
        }
        if (idx === 6) {
          feedContainer.appendChild(createRadioCTA());
        }

        const card = document.createElement('article');
        card.className = 'news-card senior-card';
        card.setAttribute('aria-label', `${article.singer_tag}: ${article.title}`);

        const formattedDate = formatDate(article.pubDate);

        card.innerHTML = `
          <div class="news-card-inner">
            <div class="news-card-thumb-wrap">
              <img src="${article.image_url}" alt="${article.singer_tag} 안내 이미지" class="news-card-thumb" data-csp-fallback-src="assets/baek_woon_ho_main.png">
              <span class="card-singer-badge">${article.singer_tag}</span>
            </div>
            <div class="news-card-body">
              <div class="news-card-meta">
                <span class="card-outlet">${article.source}</span>
                <span class="card-date">${formattedDate}</span>
              </div>
              <h3 class="news-card-title">
                <a href="#view-${article.id}" class="card-title-link" data-id="${article.id}">${article.title}</a>
              </h3>
              <p class="news-card-excerpt">${article.summary}</p>
              <div class="news-card-actions">
                <button type="button" class="senior-btn btn-gold-outline btn-read-large" data-id="${article.id}" aria-label="${article.title} 큰 글씨로 읽기">
                  <span aria-hidden="true">📖</span> 큰 글씨 요약 보기
                </button>
              </div>
            </div>
          </div>
        `;

        feedContainer.appendChild(card);
      });
    }

    function showModalForArticle(id) {
      const article = engine.openModal(id);
      if (!article || !modalEl) return;

      if (modalBadgeEl) modalBadgeEl.textContent = article.singer_tag;
      if (modalOutletEl) modalOutletEl.textContent = article.source;
      if (modalDateEl) modalDateEl.textContent = formatDate(article.pubDate);
      if (modalTitleEl) modalTitleEl.textContent = article.title;
      if (modalBodyEl) {
        modalBodyEl.textContent = article.summary;
        modalBodyEl.style.fontSize = `${engine.getModalFontSizePx()}px`;
        let shopSlot = document.getElementById('modal-context-shop-slot');
        if (!shopSlot && modalBodyEl.parentNode) {
          shopSlot = document.createElement('div');
          shopSlot.id = 'modal-context-shop-slot';
          shopSlot.style.marginTop = '20px';
          modalBodyEl.parentNode.appendChild(shopSlot);
        }
        if (shopSlot) {
          const items = getContextShopItems(article.singer_tag);
          shopSlot.innerHTML = `
            <div style="background:#FFFFFF;border:2.5px solid #D4AF37;border-radius:16px;padding:18px;">
              <div style="font-size:21px;font-weight:900;color:#0E2820;margin-bottom:10px;">💚 김쌤의 콘서트·응원 안심 준비물관</div>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;">
                ${renderShopCardsInnerHtml(items)}
              </div>
              <p class="ftc-inline-disclosure" style="margin:10px 0 0;">※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다.</p>
            </div>
          `;
        }
      }
      if (modalLinkEl) {
        modalLinkEl.href = article.link;
      }

      modalEl.setAttribute('aria-hidden', 'false');
      modalEl.classList.add('is-open');
      document.body.classList.add('modal-active');

      if (modalCloseBtn) modalCloseBtn.focus();
    }

    function hideModal() {
      engine.closeModal();
      if (!modalEl) return;

      modalEl.setAttribute('aria-hidden', 'true');
      modalEl.classList.remove('is-open');
      document.body.classList.remove('modal-active');
    }

    function updateUI() {
      const filtered = engine.getFilteredArticles();
      renderPills();

      if (resultCountEl) {
        resultCountEl.textContent = `${filtered.length}건`;
      }

      const heroArticle = filtered.length > 0 ? filtered[0] : null;
      renderHero(heroArticle);
      renderFeed(filtered);
    }

    document.addEventListener('click', (e) => {
      const target = e.target;
      const readBtn = target.closest('.btn-read-large, .news-title-link, .card-title-link');
      if (readBtn) {
        e.preventDefault();
        const id = readBtn.getAttribute('data-id');
        if (id) {
          showModalForArticle(id);
        }
      }
    });

    if (modalCloseBtn) {
      modalCloseBtn.addEventListener('click', hideModal);
    }

    if (modalEl) {
      modalEl.addEventListener('click', (e) => {
        if (e.target === modalEl) {
          hideModal();
        }
      });
    }

    if (modalFontScalerBtn) {
      modalFontScalerBtn.addEventListener('click', () => {
        engine.toggleModalFont();
        const sizePx = engine.getModalFontSizePx();
        if (modalBodyEl) {
          modalBodyEl.style.fontSize = `${sizePx}px`;
        }
        modalFontScalerBtn.setAttribute('aria-label', `소식 글자 크기 조절 (현재 ${sizePx}px)`);
        modalFontScalerBtn.innerHTML = `<span aria-hidden="true">🔍</span> 글자 크기: <strong>${sizePx}px</strong>`;
      });
    }

    if (modalShareBtn) {
      modalShareBtn.addEventListener('click', async () => {
        const article = engine.currentModalArticle;
        if (!article) return;

        const shareData = {
          title: `[김쌤의영웅라디오 소식란] ${article.title}`,
          text: `${article.summary}\n\n출처: 김쌤의영웅라디오 가족 사랑방`,
          url: window.location.href
        };

        if (navigator.share) {
          try {
            await navigator.share(shareData);
          } catch (err) {}
        } else if (navigator.clipboard) {
          try {
            await navigator.clipboard.writeText(`${shareData.title}\n${shareData.url}`);
            alert('소식 주소가 복사되었습니다! 카카오톡 대화방에 편하게 붙여넣기 하세요.');
          } catch (err) {
            alert('주소 복사에 실패했습니다.');
          }
        }
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        engine.setSearchQuery(e.target.value);
        updateUI();
      });
    }

    if (searchClearBtn && searchInput) {
      searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        engine.setSearchQuery('');
        updateUI();
        searchInput.focus();
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && engine.isModalOpen) {
        hideModal();
      }
    });

    engine.loadNews().then(() => {
      engine.setSingerFilter('전체');
      updateUI();
    });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initBrowserUI);
    } else {
      initBrowserUI();
    }
  }

  global.TrotNewsEngine = TrotNewsEngine;
  global.SEED_NEWS = SEED_NEWS;
  global.SINGER_LIST = SINGER_LIST;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      TrotNewsEngine,
      SEED_NEWS,
      SINGER_LIST
    };
  }
})(typeof window !== 'undefined' ? window : global);
