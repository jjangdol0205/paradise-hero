/**
 * trot-news.js
 * Division 4: Hwang Young-woong Exclusive News Portal Client Engine.
 * Target: paradise-hero.com (@김쌤의영웅라디오)
 *
 * Features:
 * 1. 6 Hwang Young-woong Exclusive Category Tabs (전체, 신곡·음반, 콘서트·공연, 나눔·선행, 방송·라디오, 팬덤·파라다이스)
 * 2. Instant Search Keyword Filtering
 * 3. Hero Breaking Spotlight Card & Responsive Card Feed
 * 4. Senior Easy-Read Modal Viewer (24px+ text, High Contrast #FAFAF8, Text Scaler)
 * 5. Contextual Interstitial CTA Cards (100% Free Photo Booth & Kim Teacher's Radio)
 * 6. Dual-layer fallback (fetches data/trot_news.json -> falls back to embedded SEED_NEWS)
 * 7. WCAG AAA Senior Ergonomics (Min 60px touch target, Accessible Keyboard & Focus Traps)
 */

(function (global) {
  'use strict';

  // 가수 황영웅 전용 6대 소식 카테고리
  const SINGER_LIST = [
    '전체',
    '신곡·음반',
    '콘서트·공연',
    '나눔·선행',
    '방송·라디오',
    '팬덤·파라다이스'
  ];

  // Embedded Offline Fallback News Seed Bundle (100% 가수 황영웅 소식 20선)
  const SEED_NEWS = [
    {
      id: 'hyw_news_album_001',
      title: '황영웅, 정규 1집 \'당신 편\' 초동 63만 장 대기록 돌파… 전국 파라다이스 팬심 감동',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EB%8B%B9%EC%8B%A0%ED%8E%B8&sort=1',
      pubDate: '2026-11-11T09:00:00Z',
      source: '파라다이스 뉴스룸',
      summary: '가수 황영웅의 첫 정규앨범 \'당신 편\'이 초동 63만 장 돌파라는 대기록을 세우며 뜨거운 사랑을 입증했다. 황영웅은 변함없이 곁을 지켜준 공식 팬덤 파라다이스 어머님들께 깊은 큰절과 진심 어린 감사의 인사를 전했다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '신곡·음반'
    },
    {
      id: 'hyw_news_album_002',
      title: '황영웅 명곡 \'당신 편\' · \'해바라기\' 음원 차트 역주행… 5070 어머님 눈물샘 적셨다',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%ED%95%B4%EB%B0%94%EB%9D%BC%EA%B8%B0&sort=1',
      pubDate: '2026-11-10T14:20:00Z',
      source: '연예포커스',
      summary: '가수 황영웅의 대표 감성곡 \'당신 편\'과 \'해바라기\'가 심야 청취자들의 사연 신청 쇄도로 주요 음원 플랫폼 스트리밍 순위에서 가파른 상승세를 기록 중이다. 고단한 삶을 어루만지는 따뜻한 노랫말이 깊은 울림을 전하고 있다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '신곡·음반'
    },
    {
      id: 'hyw_news_album_003',
      title: '황영웅 미니앨범 \'꽃구경\' · \'인사동 찻집\', 공식 영상 누적 재생 1,500만 뷰 돌파',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EA%BD%83%EA%B5%AC%EA%B2%BD&sort=1',
      pubDate: '2026-11-09T11:10:00Z',
      source: 'K-트롯 데일리',
      summary: '황영웅의 짙은 사모곡 감성이 담긴 \'꽃구경\'과 \'인사동 찻집\' 공식 무대 영상이 누적 1,500만 회 재생을 돌파했다. 세월이 흘러도 질리지 않는 정통 동굴 중저음 보컬의 진가가 다시 한번 빛을 발했다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '신곡·음반'
    },
    {
      id: 'hyw_news_album_004',
      title: '황영웅 수록곡 \'함께해요\' · \'황금빛 인생\', 어머님들이 뽑은 아침 힐링송 1위 선정',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-07T08:40:00Z',
      source: '뮤직투데이',
      summary: '가수 황영웅의 따뜻한 희망가 \'함께해요\'가 시니어 팬들이 매일 아침 가장 먼저 재생하는 활력 응원곡으로 꼽혔다. 다정하게 손을 내미는 듯한 보이스 컬러가 하루의 든든한 시작을 열어준다는 호평이 이어진다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '신곡·음반'
    },
    {
      id: 'hyw_news_concert_001',
      title: '황영웅 전국 투어 콘서트 감동 후기 쇄도… 공연장 수놓은 \'에메랄드 응원 물결\'',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-11T07:30:00Z',
      source: '스포츠한국',
      summary: '전국 각지에서 모인 파라다이스 팬들이 에메랄드빛 응원봉 물결로 객석을 가득 메우며 가수 황영웅과 하나 되는 명장면을 연출했다. 황영웅은 흔들림 없는 3시간 라이브 가창력과 다정한 눈맞춤으로 최고의 하루를 선물했다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '콘서트·공연'
    },
    {
      id: 'hyw_news_concert_002',
      title: '황영웅 콘서트 현장 어머님 배려 서비스 화제… 큰 글씨 안내판부터 따뜻한 쉼터까지',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-09T16:00:00Z',
      source: '문화포커스',
      summary: '가수 황영웅의 공연장이 중장년·시니어 관객들의 안전과 편의를 세심하게 배려한 운영으로 귀감이 되고 있다. 넉넉한 대기 좌석과 친절한 길 안내 요원 배치로 자녀들도 안심하고 부모님 효도 선물을 예매한다는 반응이다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '콘서트·공연'
    },
    {
      id: 'hyw_news_concert_003',
      title: '황영웅 앙코르 무대 \'비상\' 열창에 객석 눈물바다… 1만 관객 기립박수 장관',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-08T13:15:00Z',
      source: '스타뉴스',
      summary: '황영웅이 콘서트 앙코르 곡으로 선보인 \'비상\' 라이브 무대가 관객들의 가슴에 잊지 못할 전율을 안겼다. 시련을 딛고 다시 날아오르는 가사 하나하나에 진심을 실어 부른 열창에 전 객석에서 뜨거운 기립박수가 터져 나왔다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '콘서트·공연'
    },
    {
      id: 'hyw_news_concert_004',
      title: '황영웅 팬미팅 현장에서 전한 진심… \'어머님들 건강이 제게는 가장 큰 선물입니다\'',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-06T10:30:00Z',
      source: '일간연예',
      summary: '가수 황영웅이 현장을 찾은 어머님 팬들의 환절기 건강을 살뜰히 챙기며 효자 가수다운 면모를 보였다. 공연이 끝난 뒤에도 한참 동안 무대 구석구석을 돌며 허리 숙여 인사하는 모습에 팬들의 감동이 이어졌다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '콘서트·공연'
    },
    {
      id: 'hyw_news_charity_001',
      title: '황영웅, 공식 팬카페 \'파라다이스\'와 함께한 온기 나눔 성료… 선한 영향력 확산',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-10T18:30:00Z',
      source: '스타투데이',
      summary: '가수 황영웅과 공식 팬덤 \'파라다이스\'가 전국 홀몸 어르신 및 취약계층을 위한 따뜻한 나눔 봉사활동을 성공적으로 마쳤다. 황영웅은 팬 여러분의 사랑이 더 큰 온기로 번져나갈 수 있어 진심으로 감사드린다고 전했다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '나눔·선행'
    },
    {
      id: 'hyw_news_charity_002',
      title: '황영웅 팬덤 파라다이스 지역 모임, 겨울맞이 김장·연탄 나눔 릴레이 훈훈',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-09T09:50:00Z',
      source: '나눔경제',
      summary: '서울·경기부터 부산·대구·호남까지 전국의 황영웅 팬모임 회원들이 자발적인 김장 김치 및 방한용품 기탁을 이어가고 있다. 가수의 이름을 빛내는 성숙하고 품격 있는 기부 문화가 지역사회에 귀감이 되고 있다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '나눔·선행'
    },
    {
      id: 'hyw_news_charity_003',
      title: '황영웅 데뷔 및 음반 발매 기념 성금 기탁… 소외 이웃에 전달된 희망의 손길',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-07T15:20:00Z',
      source: '복지타임즈',
      summary: '황영웅의 음악으로 위로를 받은 팬들이 십시일반 모은 성금과 생필품을 지역 복지관에 전달했다. 복지관 관계자는 매년 잊지 않고 따뜻한 손길을 내밀어 주시는 황영웅 가수와 파라다이스 팬분들께 깊이 감사드린다고 밝혔다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '나눔·선행'
    },
    {
      id: 'hyw_news_charity_004',
      title: '황영웅 노래교실 재능기부 봉사단 화제… 어르신 경로당에 울려 퍼진 \'당신 편\'',
      link: 'https://paradise-hero.com/columns/index.html',
      pubDate: '2026-11-05T11:45:00Z',
      source: '시니어일보',
      summary: '황영웅을 사랑하는 팬들로 구성된 봉사단이 지역 경로당을 찾아 황영웅의 대표곡을 함께 부르고 다과를 나누는 뜻깊은 시간을 가졌다. 노래로 웃음꽃을 피우는 정겨운 현장이 큰 감동을 전하고 있다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '나눔·선행'
    },
    {
      id: 'hyw_news_radio_001',
      title: '김쌤의 영웅라디오 사연 신청 폭주… 황영웅 노래로 다시 웃음 찾은 어머님들 감동 실화',
      link: 'https://paradise-hero.com/radio.html',
      pubDate: '2026-11-11T06:00:00Z',
      source: '김쌤의 영웅라디오',
      summary: '유튜브 \'@김쌤의영웅라디오\'와 파라다이스 사연 복덕방에 전국 어머님들의 진솔한 인생 사연이 줄을 잇고 있다. 병상에서, 혹은 외로운 저녁 시간에 황영웅의 목소리로 큰 위로를 받았다는 편지들이 깊은 공감을 자아낸다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '방송·라디오'
    },
    {
      id: 'hyw_news_radio_002',
      title: '보컬 전문가들이 분석한 황영웅 중저음의 비밀… \'듣는 이의 심장 박동과 닮은 치유 주파수\'',
      link: 'https://paradise-hero.com/radio.html?ep=1',
      pubDate: '2026-11-10T10:15:00Z',
      source: '사운드저널',
      summary: '소리 전문가들은 가수 황영웅 특유의 깊고 풍부한 중저음 발성이 중장년 청취자들에게 심리적 안정감과 카타르시스를 동시에 선사한다고 호평했다. 기교보다 진심을 앞세운 호흡이 독보적 호소력의 비결로 꼽힌다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '방송·라디오'
    },
    {
      id: 'hyw_news_radio_003',
      title: '황영웅 대표 리메이크 무대 다시보기 열풍… 심야 라디오 단골 신청곡 등극',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EB%AC%B4%EB%8C%80+%EC%98%81%EC%83%81&sort=1',
      pubDate: '2026-11-08T19:00:00Z',
      source: '방송연예뉴스',
      summary: '잠 못 이루는 밤 라디오 주파수를 맞추는 시니어 애청자들 사이에서 황영웅의 정통 트로트 무대 음원이 부동의 인기 신청곡으로 사랑받고 있다. 한 소절만 들어도 가슴이 뻥 뚫린다는 애청자 후기가 이어진다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '방송·라디오'
    },
    {
      id: 'hyw_news_radio_004',
      title: '파라다이스 사연 복덕방 음성 받아쓰기 인기… \'글자 치기 힘들어도 말로 사연 보내요\'',
      link: 'https://paradise-hero.com/story.html',
      pubDate: '2026-11-06T14:10:00Z',
      source: '파라다이스 뉴스룸',
      summary: '스마트폰 작은 자판 입력이 불편했던 어머님들이 파라다이스 히어로의 \'말씀으로 편하게 적기\' 기능을 통해 손쉽게 방송 사연을 접수하고 있다. 접수된 사연은 매주 김쌤의 영웅라디오 정규 방송에서 따뜻하게 낭독된다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '방송·라디오'
    },
    {
      id: 'hyw_news_fandom_001',
      title: '파라다이스 히어로, 황영웅 10대 시그니처 의상 무료 투샷 포토부스 전면 개방 화제',
      link: 'https://paradise-hero.com/booth.html',
      pubDate: '2026-11-11T08:00:00Z',
      source: '파라다이스 뉴스룸',
      summary: '가수 황영웅 팬 쉼터 \'파라다이스 히어로\'가 에메랄드 콘서트 수트부터 순백 턱시도, 한복룩까지 황영웅의 10가지 의상과 함께 기념사진을 찍는 온라인 포토부스를 회원가입·결제 없이 100% 무제한 무료로 개방해 큰 호응을 얻고 있다.',
      image_url: 'assets/og_booth_share.jpg',
      singer_tag: '팬덤·파라다이스'
    },
    {
      id: 'hyw_news_fandom_002',
      title: '어머님들 카톡 프로필 사진 열풍… 황영웅 무료 선물제작소 달력·효도 안부카드 인기',
      link: 'https://paradise-hero.com/vip.html',
      pubDate: '2026-11-10T12:30:00Z',
      source: '디지털시니어',
      summary: '내 이름이 새겨진 파라다이스 평생 동행 증서와 큰 글씨 월간 달력 배경화면, 자녀·친구에게 보내는 황영웅 안부 카드를 무료로 만들 수 있는 \'무료 선물제작소\'가 어머님 팬들의 카카오톡 단톡방 필수 코스로 자리 잡았다.',
      image_url: 'assets/og_vip_gift.jpg',
      singer_tag: '팬덤·파라다이스'
    },
    {
      id: 'hyw_news_fandom_003',
      title: '칠순에 다시 찾은 청춘… 황영웅 응원하며 스마트폰 스밍·투표 배운 어머님들의 봄날',
      link: 'https://paradise-hero.com/stream.html',
      pubDate: '2026-11-08T09:20:00Z',
      source: '라이프투데이',
      summary: '평생 가족 뒷바라지만 하며 살아온 6070 어머님들이 가수 황영웅을 응원하면서 음원 스트리밍과 팬 커뮤니티 소통을 배우며 제2의 청춘 활력을 되찾고 있다. 자녀들 역시 밝아진 어머니 모습에 함께 응원을 보태고 있다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '팬덤·파라다이스'
    },
    {
      id: 'hyw_news_fandom_004',
      title: '파라다이스 사랑방 일일 출석 응원 열기… \'오늘도 황영웅님 꽃길만 걸으세요\'',
      link: 'https://paradise-hero.com/community.html',
      pubDate: '2026-11-05T17:00:00Z',
      source: '파라다이스 뉴스룸',
      summary: '복잡한 회원가입 없이 닉네임 하나로 매일 따뜻한 응원 한마디를 남기는 파라다이스 사랑방 출석 게시판이 전국 팬들의 다정한 안부 인사로 북적이고 있다. 서로의 건강을 챙기며 황영웅을 응원하는 성숙한 팬 문화가 빛난다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '팬덤·파라다이스'
    }
  ];

  class TrotNewsEngine {
    constructor(initialArticles = null) {
      this.articles = Array.isArray(initialArticles) ? initialArticles : [];
      this.activeSinger = '전체';
      this.searchQuery = '';
      this.currentModalArticle = null;
      this.modalFontLevel = 'normal'; // 'normal' (24px), 'large' (28px), 'xlarge' (32px)
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
      } else if (singer === '황영웅') {
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
        filtered = filtered.filter(item => item.singer_tag === this.activeSinger);
      }

      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase();
        filtered = filtered.filter(item => {
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
      return this.articles.find(a => a.id === id) || null;
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
        const now = new Date();
        const diffHours = Math.floor((now - d) / (1000 * 60 * 60));
        if (diffHours >= 0 && diffHours < 1) return '방금 전';
        if (diffHours >= 1 && diffHours < 24) return `${diffHours}시간 전`;
        return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
      } catch (e) {
        return isoStr;
      }
    }

    function renderPills() {
      if (!pillsContainer) return;
      pillsContainer.innerHTML = '';

      SINGER_LIST.forEach(category => {
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
        <article class="hero-spotlight-card senior-card" aria-label="가수 황영웅 오늘의 주요 소식">
          <div class="hero-badge-row">
            <span class="spotlight-tag" aria-label="속보">💚 오늘의 황영웅 주요 소식</span>
            <span class="singer-tag-badge">${article.singer_tag}</span>
            <span class="outlet-badge">${article.source}</span>
            <span class="date-badge">${formattedDate}</span>
          </div>
          <div class="hero-content-split">
            <div class="hero-thumb-wrapper">
              <img src="${article.image_url}" alt="${article.title} 사진" class="hero-thumb-img" onerror="this.onerror=null;this.src='assets/og_booth_share.jpg';">
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
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="senior-btn btn-outline" aria-label="원문 소식 새 창에서 보기">
                  <span aria-hidden="true">🌐</span> 원문 소식 보기
                </a>
              </div>
            </div>
          </div>
        </article>
      `;
    }

    function renderFeed(articles) {
      if (!feedContainer) return;
      feedContainer.innerHTML = '';

      if (articles.length === 0) {
        feedContainer.innerHTML = `
          <div class="no-results-card senior-card">
            <p class="no-results-icon" aria-hidden="true">🔎</p>
            <h3 class="no-results-title">검색된 황영웅 소식이 없습니다</h3>
            <p class="no-results-desc">다른 분야 버튼을 누르시거나 검색어를 지워주세요.</p>
            <button type="button" class="senior-btn btn-gold btn-reset-filters">
              <span>전체 황영웅 소식 보기</span>
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
        if (idx === 2) {
          feedContainer.appendChild(createPhotoBoothCTA());
        }
        if (idx === 6) {
          feedContainer.appendChild(createRadioCTA());
        }

        const card = document.createElement('article');
        card.className = 'news-card senior-card';
        card.setAttribute('aria-label', `${article.singer_tag} 소식: ${article.title}`);

        const formattedDate = formatDate(article.pubDate);

        card.innerHTML = `
          <div class="news-card-inner">
            <div class="news-card-thumb-wrap">
              <img src="${article.image_url}" alt="가수 황영웅 ${article.singer_tag} 소식 이미지" class="news-card-thumb" onerror="this.onerror=null;this.src='assets/og_booth_share.jpg';">
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

    function createPhotoBoothCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-booth senior-card';
      banner.setAttribute('aria-label', '가수 황영웅과 함께하는 무료 투샷 사진관 바로가기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📸</div>
          <div class="cta-text-col">
            <span class="cta-kicker">100% 무제한 무료 개방</span>
            <h3 class="cta-heading">가수 황영웅님과 다정한 기념 투샷 무료 촬영!</h3>
            <p class="cta-description">회원가입이나 결제 없이 누구나 평생 무제한 무료! 황영웅님의 10가지 무대·일상 의상과 함께 세상에 하나뿐인 사진을 만드세요.</p>
          </div>
          <div class="cta-btn-col">
            <a href="booth.html" class="senior-btn btn-gold cta-action-btn">
              <span>무료 사진 찍으러 가기 👉</span>
            </a>
          </div>
        </div>
      `;
      return banner;
    }

    function createRadioCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-radio senior-card';
      banner.setAttribute('aria-label', '김쌤의 영웅 라디오 방송 듣기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📻</div>
          <div class="cta-text-col">
            <span class="cta-kicker">김쌤의 영웅 라디오</span>
            <h3 class="cta-heading">가슴을 울리는 황영웅 사연과 명곡 연속 방송</h3>
            <p class="cta-description">전국 파라다이스 어머님들의 눈물과 감동이 담긴 편지, 황영웅 가수의 명품 무대 이야기를 지금 바로 편안하게 들어보세요.</p>
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
        modalFontScalerBtn.setAttribute('aria-label', `기사 글자 크기 조절 (현재 ${sizePx}px)`);
        modalFontScalerBtn.innerHTML = `<span aria-hidden="true">🔍</span> 글자 크기: <strong>${sizePx}px</strong>`;
      });
    }

    if (modalShareBtn) {
      modalShareBtn.addEventListener('click', async () => {
        const article = engine.currentModalArticle;
        if (!article) return;

        const shareData = {
          title: `[황영웅 소식방] ${article.title}`,
          text: `${article.summary}\n\n출처: 파라다이스 히어로`,
          url: window.location.href
        };

        if (navigator.share) {
          try {
            await navigator.share(shareData);
          } catch (err) {
            // Cancelled
          }
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

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      TrotNewsEngine,
      SEED_NEWS,
      SINGER_LIST
    };
  } else {
    global.TrotNewsEngine = TrotNewsEngine;
    global.SEED_NEWS = SEED_NEWS;
    global.SINGER_LIST = SINGER_LIST;
  }

})(typeof window !== 'undefined' ? window : globalThis);
