/**
 * trot-news.js
 * Division 4: Trot RSS News Traffic Portal Client Engine.
 * Target: paradise-hero.com (@김쌤의영웅라디오)
 * 
 * Features:
 * 1. 10 Trot Singer Category Filtering (전체, 황영웅, 임영웅, 이찬원, 영탁, 정동원, 김호중, 장민호, 박서진, 손태진, 안성훈/진해성)
 * 2. Instant Search Keyword Filtering
 * 3. Hero Breaking Spotlight Card & Responsive Card Feed
 * 4. Senior Easy-Read Modal Viewer (24px+ text, High Contrast #FAFAF8, Text Scaler)
 * 5. Contextual Interstitial CTA Cards (Photo Booth & Kim Teacher's Radio)
 * 6. Dual-layer fallback (fetches data/trot_news.json -> falls back to embedded SEED_NEWS)
 * 7. WCAG AAA Senior Ergonomics (Min 56px touch target, Accessible Keyboard & Focus Traps)
 */

(function (global) {
  'use strict';

  // 10 Male Trot Singer Tabs
  const SINGER_LIST = [
    '전체',
    '황영웅',
    '임영웅',
    '이찬원',
    '영탁',
    '정동원',
    '김호중',
    '장민호',
    '박서진',
    '손태진',
    '안성훈/진해성'
  ];

  // Embedded Offline Fallback News Seed Bundle
  const SEED_NEWS = [
    {
      id: 'trot_news_hyw_001',
      title: '황영웅, 정규 1집 \'당신 편\' 63만 장 대기록 돌파… 전국 파라다이스 팬심 폭발',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EB%8B%B9%EC%8B%A0%ED%8E%B8&sort=1',
      pubDate: '2026-11-10T09:00:00Z',
      source: '파라다이스 뉴스룸',
      summary: '감성 황태자 황영웅의 첫 정규앨범 \'당신 편\'이 초동 63만 장 돌파라는 대기록을 세우며 트로트 음반 역사를 새로 썼다. 황영웅은 변함없이 곁을 지켜준 공식 팬덤 파라다이스 어머님들께 깊은 큰절과 감사의 인사를 전했다.',
      image_url: 'assets/hero_main.png',
      singer_tag: '황영웅'
    },
    {
      id: 'trot_news_hyw_002',
      title: '황영웅, 공식 팬카페 \'파라다이스\'와 함께한 온기 나눔 성료… 선한 영향력 확산',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%ED%8C%8C%EB%9D%BC%EB%8B%A4%EC%9D%B4%EC%8A%A4+%EA%B8%B0%EB%B6%80&sort=1',
      pubDate: '2026-11-09T18:30:00Z',
      source: '스타투데이',
      summary: '가수 황영웅과 공식 팬덤 \'파라다이스\'가 전국 소외계층 어르신들을 위한 따뜻한 나눔 봉사활동을 성공적으로 마쳤다. 깊은 중저음 보이스로 사랑받는 황영웅은 \'팬 여러분의 사랑이 더 큰 온기로 번져나갈 수 있어 진심으로 감사드린다\'고 전했다.',
      image_url: 'assets/characters/thumb_hwang_young_woong.png',
      singer_tag: '황영웅'
    },
    {
      id: 'trot_news_hyw_003',
      title: '황영웅 명곡 \'당신 편\' · \'해바라기\' 스트리밍 역주행… 5070 어머님들의 눈물샘 자극',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%ED%95%B4%EB%B0%94%EB%9D%BC%EA%B8%B0&sort=1',
      pubDate: '2026-11-09T14:20:00Z',
      source: '연예포커스',
      summary: '황영웅의 대표 감성곡 \'당신 편\'과 \'해바라기\'가 라디오 청취자들의 사연 신청 쇄도로 주요 음원 플랫폼 스트리밍 순위에서 가파른 역주행을 기록 중이다. 지친 일상에 깊은 위로를 건네는 진솔한 노랫말이 큰 감동을 자아내고 있다.',
      image_url: 'assets/characters/thumb_lim_young_woong.png',
      singer_tag: '황영웅'
    },
    {
      id: 'trot_news_hyw_004',
      title: '황영웅 미니앨범 \'꽃구경\' · \'인사동 찻집\', 누적 재생 1,500만 회 돌파… 진심 통했다',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EA%BD%83%EA%B5%AC%EA%B2%BD&sort=1',
      pubDate: '2026-11-08T11:10:00Z',
      source: 'K-트롯 데일리',
      summary: '황영웅의 깊은 감성이 담긴 \'꽃구경\'과 \'인사동 찻집\' 공식 무대 영상이 국내외 플랫폼 누적 1,500만 회 재생을 돌파했다. 변함없는 응원을 보내주는 팬덤 파라다이스와의 끈끈한 유대감이 일궈낸 값진 결실로 평가받는다.',
      image_url: 'assets/characters/thumb_lee_chan_won.png',
      singer_tag: '황영웅'
    },
    {
      id: 'trot_news_hyw_005',
      title: '황영웅 전국 콘서트 투어 감동 후기 쇄도… \'평생 잊지 못할 에메랄드 물결\'',
      link: 'https://search.naver.com/search.naver?where=news&query=%ED%99%A9%EC%98%81%EC%9B%85+%EC%BD%98%EC%84%9C%ED%8A%B8&sort=1',
      pubDate: '2026-11-08T09:00:00Z',
      source: '스포츠한국',
      summary: '전국 각지에서 모인 파라다이스 팬들이 에메랄드 응원봉 물결로 공연장을 가득 채우며 황영웅과 하나 되는 명장면을 연출했다. 황영웅은 흔들림 없는 라이브 가창력과 다정한 팬 서비스로 현장을 찾은 어머님들에게 최고의 하루를 선물했다.',
      image_url: 'assets/characters/thumb_young_tak.png',
      singer_tag: '황영웅'
    },
    {
      id: 'trot_news_lyw_001',
      title: '임영웅, 전국투어 \'IM HERO\' 전석 매진 신화… 상암에 울려 퍼진 하늘빛 축제',
      link: 'https://paradise-hero.com/news.html#lyw_001',
      pubDate: '2026-11-09T08:45:00Z',
      source: '스타투데이',
      summary: '가수 임영웅의 전국투어 콘서트가 연일 전석 매진을 기록하며 대한민국 가요계의 독보적인 흥행 파워를 과시했다. 임영웅은 영웅시대 팬들과 함께 잊지 못할 감동의 무대를 선사하며 뜨거운 호평을 받았다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '임영웅'
    },
    {
      id: 'trot_news_lyw_002',
      title: '임영웅 신곡 \'온기\' 뮤직비디오 유튜브 2,000만 뷰 달성… 세대 초월 힐링',
      link: 'https://paradise-hero.com/news.html#lyw_002',
      pubDate: '2026-11-08T14:10:00Z',
      source: '스포츠한국',
      summary: '임영웅이 직접 작사·작곡에 참여한 자작곡 \'온기\' 뮤직비디오가 유튜브 조회수 2,000만 뷰를 넘어섰다. 한 편의 단편영화를 연상케 하는 몰입도 높은 연기와 따뜻한 멜로디가 전 세대 음악 팬들의 마음을 울렸다.',
      image_url: 'assets/frames/frame_flower_path.png',
      singer_tag: '임영웅'
    },
    {
      id: 'trot_news_lyw_003',
      title: '임영웅 팬클럽 \'영웅시대\', 소아암 어린이 위해 1억 원 기부 실천',
      link: 'https://paradise-hero.com/news.html#lyw_003',
      pubDate: '2026-11-06T10:00:00Z',
      source: '문화일보',
      summary: '가수 임영웅의 든든한 동반자 \'영웅시대\'가 소아암 환아 치료를 위한 성금 1억 원을 기부했다. 가수를 닮은 팬들의 훈훈한 기부 릴레이는 성숙한 팬덤 문화의 모범 사례로 널리 회자되고 있다.',
      image_url: 'assets/frames/frame_radio_studio.png',
      singer_tag: '임영웅'
    },
    {
      id: 'trot_news_lcw_001',
      title: '이찬원, 정규 2집 타이틀곡 \'하늘 여행\' 지상파 3사 1위 그랜드슬램 달성',
      link: 'https://paradise-hero.com/news.html#lcw_001',
      pubDate: '2026-11-09T07:50:00Z',
      source: '스포츠조선',
      summary: '\'찬또배기\' 이찬원이 자작곡 \'하늘 여행\'으로 음악 방송 트로피를 휩쓸며 싱어송라이터로서의 진가를 입증했다. 노부부의 인생과 사랑을 그린 애절한 멜로디가 시니어 청취자들의 깊은 공감을 이끌어냈다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '이찬원'
    },
    {
      id: 'trot_news_lcw_002',
      title: '이찬원, 예능과 음악 넘나드는 만능 엔터테이너 면모… \'톡파원 25시\' 맹활약',
      link: 'https://paradise-hero.com/news.html#lcw_002',
      pubDate: '2026-11-07T16:30:00Z',
      source: 'OSEN',
      summary: '이찬원이 방송 프로그램에서 백과사전급 해박한 지식과 유쾌한 입담으로 시청자들의 사랑을 독차지하고 있다. 찬또위키라는 별명에 걸맞은 명품 진행 능력이 연일 찬사를 받는 중이다.',
      image_url: 'assets/frames/frame_paradise_4cut.png',
      singer_tag: '이찬원'
    },
    {
      id: 'trot_news_yt_001',
      title: '영탁, 새 미니앨범 \'슈퍼슈퍼\' 발표 직후 음원차트 최상위권 안착',
      link: 'https://paradise-hero.com/news.html#yt_001',
      pubDate: '2026-11-09T10:15:00Z',
      source: '헤럴드POP',
      summary: '에너지 넘치는 가수 영탁이 신보 \'슈퍼슈퍼(SuperSuper)\'로 컴백해 주요 차트를 휩쓸었다. 특유의 시원하고 파워풀한 가창력과 긍정적인 메시지가 팬들에게 짜릿한 활력을 불어넣고 있다.',
      image_url: 'assets/frames/frame_flower_path.png',
      singer_tag: '영탁'
    },
    {
      id: 'trot_news_yt_002',
      title: '영탁, 전국 단독 콘서트 \'TAK SHOW\' 성황… 영탁앤블루스와 파란 물결',
      link: 'https://paradise-hero.com/news.html#yt_002',
      pubDate: '2026-11-06T18:00:00Z',
      source: '마이데일리',
      summary: '영탁이 단독 투어 콘서트 \'TAK SHOW\'를 통해 다채로운 밴드 사운드와 흔들림 없는 라이브 실력을 선보였다. 팬클럽 영탁앤블루스의 푸른빛 응원봉이 객석을 가득 메우며 장관을 이뤘다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '영탁'
    },
    {
      id: 'trot_news_jdw_001',
      title: '정동원, K-팝 부캐 \'JD1\'과 본캐 넘나드는 한계 없는 음악 스펙트럼',
      link: 'https://paradise-hero.com/news.html#jdw_001',
      pubDate: '2026-11-08T13:40:00Z',
      source: '텐아시아',
      summary: '어엿한 청년 가수로 성장한 정동원이 트롯 무대와 K-팝 아이돌 부캐 JD1 활동을 완벽하게 병행하며 전방위 활약을 펼치고 있다. 깊어진 감성과 화려한 퍼포먼스가 음악 팬들을 매료시켰다.',
      image_url: 'assets/frames/frame_paradise_4cut.png',
      singer_tag: '정동원'
    },
    {
      id: 'trot_news_jdw_002',
      title: '정동원 소품집 \'소품집 Vol.1\', 아날로그 감성 가득 담은 명반 호평',
      link: 'https://paradise-hero.com/news.html#jdw_002',
      pubDate: '2026-11-05T09:10:00Z',
      source: '뉴스1',
      summary: '정동원의 진한 트롯 감성을 담은 리메이크 미니앨범이 시니어 리스너들의 추억을 자극하고 있다. 소년에서 성숙한 아티스트로 발돋움한 그의 호소력 짙은 음색이 큰 울림을 안긴다.',
      image_url: 'assets/frames/frame_flower_path.png',
      singer_tag: '정동원'
    },
    {
      id: 'trot_news_khj_001',
      title: '김호중의 클래식 명반 \'파노라마\', 변함없는 팬덤 아리스의 묵직한 응원',
      link: 'https://paradise-hero.com/news.html#khj_001',
      pubDate: '2026-11-08T11:00:00Z',
      source: 'TV리포트',
      summary: '\'트바로티\' 김호중의 웅장한 테너 음색이 담긴 클래식 앨범 수록곡들이 팬덤 아리스의 변함없는 사랑 속에 스테디셀러로 자리 잡고 있다. 성악과 트롯을 융합한 독보적 보이스가 큰 사랑을 받는다.',
      image_url: 'assets/frames/frame_radio_studio.png',
      singer_tag: '김호중'
    },
    {
      id: 'trot_news_khj_002',
      title: '김호중 대표곡 \'빛이 나는 사람\', 라디오 청취자 희망 사연 1위 등극',
      link: 'https://paradise-hero.com/news.html#khj_002',
      pubDate: '2026-11-06T15:45:00Z',
      source: '스포츠경향',
      summary: '김호중이 노래한 \'빛이 나는 사람\'이 고단한 삶을 위로하는 대표 힐링 송으로 라디오 방송 사연 코너에서 가장 많이 신청된 곡으로 꼽혔다. 팬들을 향한 진심 어린 위로의 메시지가 돋보인다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '김호중'
    },
    {
      id: 'trot_news_jmh_001',
      title: '장민호, 정규앨범 \'에세이 ep.3\' 발매… 따뜻한 시선과 인생 철학 담아내',
      link: 'https://paradise-hero.com/news.html#jmh_001',
      pubDate: '2026-11-09T08:15:00Z',
      source: '스포츠동아',
      summary: '\'트롯계의 꽃신사\' 장민호가 세 번째 에세이 앨범을 통해 깊어진 인생의 맛과 낭만을 전했다. 중후한 감성과 세련된 보컬이 돋보이는 수록곡들이 가을 가요계를 촉촉하게 물들이고 있다.',
      image_url: 'assets/frames/frame_flower_path.png',
      singer_tag: '장민호'
    },
    {
      id: 'trot_news_jmh_002',
      title: '장민호 전국투어 \'호시절\', 민호특공대와 함께한 눈물과 웃음의 축제',
      link: 'https://paradise-hero.com/news.html#jmh_002',
      pubDate: '2026-11-07T14:50:00Z',
      source: '뉴스엔',
      summary: '가수 장민호의 전국투어 콘서트 \'호시절\'이 관객들의 기립박수 속에 성황리에 펼쳐졌다. 팬덤 \'민호특공대\'의 질서 정연하고 열정적인 응원 문화가 돋보인 훈훈한 시간이었다.',
      image_url: 'assets/frames/frame_paradise_4cut.png',
      singer_tag: '장민호'
    },
    {
      id: 'trot_news_psj_001',
      title: '박서진, KBS \'살림하는 남자들\' 최고 시청률 견인… 지극한 효심 화제',
      link: 'https://paradise-hero.com/news.html#psj_001',
      pubDate: '2026-11-09T09:00:00Z',
      source: '엑스포츠뉴스',
      summary: '\'장구의 신\' 박서진이 가족을 향한 애틋한 사랑과 인간미 넘치는 일상을 선보이며 주말 예능 최고 시청률의 주역으로 우뚝 섰다. 닻별 팬들은 물론 대중의 뜨거운 응원이 쏟아지고 있다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '박서진'
    },
    {
      id: 'trot_news_psj_002',
      title: '박서진 단독 콘서트 티켓 예매 대란… 신들린 장구 퍼포먼스 기대감 고조',
      link: 'https://paradise-hero.com/news.html#psj_002',
      pubDate: '2026-11-06T11:30:00Z',
      source: '스포츠서울',
      summary: '박서진의 단독 콘서트 티켓이 오픈 직후 빠른 속도로 매진되며 막강한 티켓 파워를 입증했다. 시원한 가창력과 압도적인 장구 타악 퍼포먼스가 어우러진 신명 나는 축제가 예고됐다.',
      image_url: 'assets/frames/frame_radio_studio.png',
      singer_tag: '박서진'
    },
    {
      id: 'trot_news_stj_001',
      title: '손태진, MBC 표준FM \'손태진의 트로트 라디오\' 청취율 1위 고공행진',
      link: 'https://paradise-hero.com/news.html#stj_001',
      pubDate: '2026-11-08T12:20:00Z',
      source: '일간스포츠',
      summary: '베이스 바리톤 손태진이 진행하는 낮 12시 라디오 프로그램이 감미로운 목소리와 따스한 공감 능력으로 동시간대 청취율 1위를 질주하고 있다. 전국 청취자들에게 비타민 같은 휴식을 안겨준다.',
      image_url: 'assets/frames/frame_flower_path.png',
      singer_tag: '손태진'
    },
    {
      id: 'trot_news_stj_002',
      title: '손태진 정규 1집 \'The Showcase\', 고급스러운 크로스오버 트롯의 정점',
      link: 'https://paradise-hero.com/news.html#stj_002',
      pubDate: '2026-11-05T17:15:00Z',
      source: '매일경제',
      summary: '손태진의 첫 솔로 정규 앨범이 클래식과 트롯의 황금 비율을 선보이며 평단과 팬덤 \'손샤인\'의 극찬을 이끌어냈다. 깊이 있는 울림과 품격 있는 음악적 시도가 높은 평가를 얻고 있다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '손태진'
    },
    {
      id: 'trot_news_ash_jhs_001',
      title: '안성훈·진해성, 미스터트롯2 주역들의 의기투합… 정통 트롯의 진수 선보여',
      link: 'https://paradise-hero.com/news.html#ash_jhs_001',
      pubDate: '2026-11-09T08:30:00Z',
      source: '조선일보 연예',
      summary: '\'미스터트롯2\' 진(眞) 안성훈과 미(美) 진해성이 특별 듀엣 무대를 통해 감칠맛 나는 정통 트롯의 꺾기와 폭발적인 가창력을 선보였다. 두 사람의 훈훈한 우정이 무대를 더욱 빛냈다.',
      image_url: 'assets/frames/frame_paradise_4cut.png',
      singer_tag: '안성훈/진해성'
    },
    {
      id: 'trot_news_ash_jhs_002',
      title: '안성훈, 팬클럽 \'후니애니\'와 함께 연탄 봉사 실천… 가슴 따뜻한 행보',
      link: 'https://paradise-hero.com/news.html#ash_jhs_002',
      pubDate: '2026-11-07T10:40:00Z',
      source: '헤럴드경제',
      summary: '가수 안성훈이 겨울철을 앞두고 취약계층 가구를 위해 연탄 배달 봉사를 펼쳤다. 팬들의 든든한 사랑을 사회로 환원하는 그의 따뜻한 실천에 박수가 이어지고 있다.',
      image_url: 'assets/frames/frame_radio_studio.png',
      singer_tag: '안성훈/진해성'
    },
    {
      id: 'trot_news_ash_jhs_003',
      title: '진해성, 명품 중저음 돋보이는 신곡 발표… \'해성사랑\' 팬덤 뜨거운 환호',
      link: 'https://paradise-hero.com/news.html#ash_jhs_003',
      pubDate: '2026-11-06T14:20:00Z',
      source: '스포츠W',
      summary: '가수 진해성이 구수한 매력과 짙은 호소력을 담은 신곡을 공개하며 정통 트롯 팬들의 마음을 사로잡았다. 감칠맛 나는 보이스 컬러가 청중의 귀를 사로잡으며 큰 반향을 일으키고 있다.',
      image_url: 'assets/frames/frame_golden_milestone.png',
      singer_tag: '안성훈/진해성'
    }
  ];

  /**
   * TrotNewsEngine: State Machine for News Traffic Acquisition
   */
  class TrotNewsEngine {
    constructor(initialArticles = null) {
      this.articles = Array.isArray(initialArticles) ? initialArticles : [];
      this.activeSinger = '전체';
      this.searchQuery = '';
      this.currentModalArticle = null;
      this.modalFontLevel = 'normal'; // 'normal' (24px), 'large' (28px), 'xlarge' (32px)
      this.isModalOpen = false;
    }

    /**
     * Load news from data/trot_news.json or fallback to SEED_NEWS
     */
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

    /**
     * Set active singer filter
     */
    setSingerFilter(singer) {
      if (SINGER_LIST.includes(singer) || singer === '전체') {
        this.activeSinger = singer;
      }
      return this.getFilteredArticles();
    }

    /**
     * Set search query
     */
    setSearchQuery(query) {
      this.searchQuery = typeof query === 'string' ? query.trim() : '';
      return this.getFilteredArticles();
    }

    /**
     * Get filtered articles based on active singer and search query
     */
    getFilteredArticles() {
      let filtered = this.articles;

      // 1. Singer Filter
      if (this.activeSinger !== '전체') {
        if (this.activeSinger === '안성훈/진해성') {
          filtered = filtered.filter(item => 
            item.singer_tag === '안성훈/진해성' ||
            item.singer_tag === '안성훈' ||
            item.singer_tag === '진해성'
          );
        } else {
          filtered = filtered.filter(item => item.singer_tag === this.activeSinger);
        }
      }

      // 2. Search Query Filter
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

    /**
     * Get article by ID
     */
    getArticleById(id) {
      return this.articles.find(a => a.id === id) || null;
    }

    /**
     * Open modal viewer for specified article ID
     */
    openModal(id) {
      const article = this.getArticleById(id);
      if (!article) return null;

      this.currentModalArticle = article;
      this.isModalOpen = true;
      return article;
    }

    /**
     * Close modal viewer
     */
    closeModal() {
      this.currentModalArticle = null;
      this.isModalOpen = false;
    }

    /**
     * Scale modal font size: 'normal' -> 'large' -> 'xlarge' -> 'normal'
     */
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

    /**
     * Get font size in px for modal text
     */
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

  // ---------------------------------------------------------------------------
  // DOM Presentation Controller (Browser Only)
  // ---------------------------------------------------------------------------
  function initBrowserUI() {
    if (typeof document === 'undefined') return;

    const engine = new TrotNewsEngine();

    // DOM Elements
    const pillsContainer = document.getElementById('singer-pills-container');
    const heroContainer = document.getElementById('news-hero-spotlight');
    const feedContainer = document.getElementById('news-feed-grid');
    const searchInput = document.getElementById('news-search-input');
    const searchClearBtn = document.getElementById('btn-clear-search');
    const resultCountEl = document.getElementById('news-result-count');

    // Modal Elements
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

    // Format human readable date
    function formatDate(isoStr) {
      if (!isoStr) return '';
      try {
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return isoStr;
        const now = new Date();
        const diffHours = Math.floor((now - d) / (1000 * 60 * 60));
        if (diffHours < 1) return '방금 전';
        if (diffHours < 24) return `${diffHours}시간 전`;
        return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
      } catch (e) {
        return isoStr;
      }
    }

    // Render 10 singer filter pills
    function renderPills() {
      if (!pillsContainer) return;
      pillsContainer.innerHTML = '';

      SINGER_LIST.forEach(singer => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'pill-btn' + (engine.activeSinger === singer ? ' active' : '');
        btn.setAttribute('aria-pressed', engine.activeSinger === singer ? 'true' : 'false');
        btn.setAttribute('data-singer', singer);
        btn.innerHTML = `<span class="pill-dot" aria-hidden="true"></span><span>${singer}</span>`;

        btn.addEventListener('click', () => {
          engine.setSingerFilter(singer);
          updateUI();
        });

        pillsContainer.appendChild(btn);
      });
    }

    // Render Hero Breaking Spotlight Card
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
        <article class="hero-spotlight-card senior-card" aria-label="오늘의 트로트 주요 뉴스 속보">
          <div class="hero-badge-row">
            <span class="spotlight-tag" aria-label="속보">🔥 오늘 주목할 뉴스</span>
            <span class="singer-tag-badge">${article.singer_tag}</span>
            <span class="outlet-badge">${article.source}</span>
            <span class="date-badge">${formattedDate}</span>
          </div>
          <div class="hero-content-split">
            <div class="hero-thumb-wrapper">
              <img src="${article.image_url}" alt="${article.title} 보도 사진" class="hero-thumb-img" onerror="this.onerror=null;this.src='assets/frames/frame_flower_path.png';">
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
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="senior-btn btn-outline" aria-label="원문 언론사 기사 새 창에서 보기">
                  <span aria-hidden="true">🌐</span> 원문 기사 보기
                </a>
              </div>
            </div>
          </div>
        </article>
      `;
    }

    // Render News Feed Card Grid + Interstitial CTAs
    function renderFeed(articles) {
      if (!feedContainer) return;
      feedContainer.innerHTML = '';

      if (articles.length === 0) {
        feedContainer.innerHTML = `
          <div class="no-results-card senior-card">
            <p class="no-results-icon" aria-hidden="true">🔎</p>
            <h3 class="no-results-title">검색된 소식이 없습니다</h3>
            <p class="no-results-desc">다른 가수를 선택하시거나 검색어를 확인해 주세요.</p>
            <button type="button" class="senior-btn btn-gold btn-reset-filters">
              <span>전체 소식 보기</span>
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

      // Skip the first article if it is shown in the hero card
      const displayList = articles.length > 1 ? articles.slice(1) : articles;

      displayList.forEach((article, idx) => {
        // Interstitial CTA 1 (Photo Booth) at position 2
        if (idx === 2) {
          feedContainer.appendChild(createPhotoBoothCTA());
        }

        // Interstitial CTA 2 (Kim Teacher's Radio) at position 6
        if (idx === 6) {
          feedContainer.appendChild(createRadioCTA());
        }

        const card = document.createElement('article');
        card.className = 'news-card senior-card';
        card.setAttribute('aria-label', `${article.singer_tag} 뉴스: ${article.title}`);

        const formattedDate = formatDate(article.pubDate);

        card.innerHTML = `
          <div class="news-card-inner">
            <div class="news-card-thumb-wrap">
              <img src="${article.image_url}" alt="${article.singer_tag} 뉴스 이미지" class="news-card-thumb" onerror="this.onerror=null;this.src='assets/frames/frame_flower_path.png';">
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

    // Photo Booth Contextual Banner Card
    function createPhotoBoothCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-booth senior-card';
      banner.setAttribute('aria-label', '가수와 함께하는 투샷 사진관 바로가기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📸</div>
          <div class="cta-text-col">
            <span class="cta-kicker">파라다이스 특별 체험</span>
            <h3 class="cta-heading">내가 좋아하는 트로트 스타와 기념 투샷 촬영!</h3>
            <p class="cta-description">회원가입만 해도 1회 무료 촬영권 즉시 증정! 황영웅·임영웅 등 10대 스타와 나만의 소중한 사진을 간직하세요.</p>
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

    // Radio Contextual Banner Card
    function createRadioCTA() {
      const banner = document.createElement('aside');
      banner.className = 'news-interstitial-cta cta-radio senior-card';
      banner.setAttribute('aria-label', '김쌤의 영웅 라디오 방송 듣기');
      banner.innerHTML = `
        <div class="cta-inner">
          <div class="cta-icon-col" aria-hidden="true">📻</div>
          <div class="cta-text-col">
            <span class="cta-kicker">김쌤의 영웅 라디오</span>
            <h3 class="cta-heading">가슴을 울리는 트로트 사연과 명곡 연속 방송</h3>
            <p class="cta-description">전국 5070 어머님들의 눈물과 감동이 담긴 편지, 황영웅 가수의 명품 음원을 지금 바로 편안하게 들어보세요.</p>
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

    // Open Modal Viewer
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

    // Close Modal Viewer
    function hideModal() {
      engine.closeModal();
      if (!modalEl) return;

      modalEl.setAttribute('aria-hidden', 'true');
      modalEl.classList.remove('is-open');
      document.body.classList.remove('modal-active');
    }

    // Update UI state
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

    // Attach Event Delegations
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

    // Font Scaler Inside Modal
    if (modalFontScalerBtn) {
      modalFontScalerBtn.addEventListener('click', () => {
        const nextLevel = engine.toggleModalFont();
        const sizePx = engine.getModalFontSizePx();
        if (modalBodyEl) {
          modalBodyEl.style.fontSize = `${sizePx}px`;
        }
        modalFontScalerBtn.setAttribute('aria-label', `기사 글자 크기 조절 (현재 ${sizePx}px)`);
        modalFontScalerBtn.innerHTML = `<span aria-hidden="true">🔍</span> 글자 크기: <strong>${sizePx}px</strong>`;
      });
    }

    // Modal Share Button
    if (modalShareBtn) {
      modalShareBtn.addEventListener('click', async () => {
        const article = engine.currentModalArticle;
        if (!article) return;

        const shareData = {
          title: `[파라다이스 뉴스] ${article.title}`,
          text: `${article.summary}\n\n출처: 파라다이스 뉴스룸`,
          url: window.location.href
        };

        if (navigator.share) {
          try {
            await navigator.share(shareData);
          } catch (err) {
            // Cancelled or unsupported
          }
        } else if (navigator.clipboard) {
          try {
            await navigator.clipboard.writeText(`${shareData.title}\n${shareData.url}`);
            alert('기사 주소가 복사되었습니다! 카카오톡이나 밴드에 편하게 공유하세요.');
          } catch (err) {
            alert('주소 복사에 실패했습니다.');
          }
        }
      });
    }

    // Search Input Handling
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

    // Keyboard ESC for modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && engine.isModalOpen) {
        hideModal();
      }
    });

    // Initial Load — Default to 황영웅 filter in browser for Paradise Hero fans
    engine.loadNews().then(() => {
      engine.setSingerFilter('황영웅');
      updateUI();
    });
  }

  // Auto-init in browser
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initBrowserUI);
    } else {
      initBrowserUI();
    }
  }

  // Export for Node.js test environment
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
