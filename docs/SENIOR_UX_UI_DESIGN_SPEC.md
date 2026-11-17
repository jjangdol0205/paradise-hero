# 🎨 4사업부 `paradise-hero.com` 5070 시니어 WCAG 2.1 AAA UX/UI 디자인 명세서

## 1. 디자인 철학 및 브랜드 컬러 시스템
- **핵심 대상**: 50대~70대 어머님·아버님 청취자 (노안 배려, 손떨림 오터치 방지, 인지부하 최소화)
- **브랜드 핵심 컬러 (고대비 AAA 준수)**:
  - 메인 에메랄드 다크 그린: **`#1B4D3E`** 및 딥 포레스트 `#0E2820`
  - 포인트 골드: **`#D4AF37`** (강조 테두리 및 배지)
  - 눈부심 방지 소프트 아이보리 배경: **`#FAFAF8`**
  - 고대비 본문 텍스트: `#111827` / `#1F2937` (명도 대비 12:1 이상 확보, WCAG 2.1 AAA 기준 충족)

---

## 2. 타이포그래피 & 3단계 글자 크기 조절기 (`#btn-font-scaler`)
1. **최소 본문 글자 크기 `20px` 이상 강제**:
   - 기본(`Level 0`): `20px` (`line-height: 1.75`)
   - 크게(`Level 1`, `body.font-lg`): `23px`
   - 아주 크게(`Level 2`, `body.font-xl`): `26px`
2. **비차단 토스트 안내 (`1.8초` 자동 닫힘)**:
   - 글자 크기 변경 토스트(`#senior-accessibility-toast`, `.senior-toast-banner`)는 본문 제목이나 상단 메뉴를 가리지 않도록 **`bottom: 74px; right: 16px; pointer-events: none;`** 위치에 표시되며 `1.8초(1800ms)` 후 자동으로 사라집니다.

---

## 3. 터치 타겟 & 모바일 뷰포트 가림 원천 해소 (`@media (max-width: 768px)`)
1. **본문 버튼·입력창 최소 높이 `60px` 이상**:
   - 모든 주요 CTA 버튼, 사연 입력창, 의상·액자 선택 버튼, 공감 박수 버튼은 `min-height: 60px` 이상으로 설계합니다.
2. **모바일 상·하단 고정 영역 초슬림화 (뷰포트 가림 해소)**:
   - 상단 헤더(`.site-header`): 모바일에서 로고 부제를 숨기고 가로 스크롤 1줄 메뉴로 압축해 시원한 본문 열람 영역을 확보합니다.
   - 하단 고정 라디오 미니바(`.sticky-radio-bar`): 모바일(`<= 768px`)에서 기존 다단 구성을 폐지하고 **`58px`(`56px~60px`) 1줄 컴팩트 바** (`[▶️ 재생/일시정지] · [현재 사연곡 제목 1줄 말줄임] · [위로 열기 ↑]`)로 슬림화합니다.
   - 본문 하단 여백: `body { padding-bottom: 76px !important; }`를 적용하여 페이지 맨 끝 글자나 버튼이 미니바에 가려지지 않습니다.
   - 자판 입력 시 자동 언핀·숨김: `<input>`, `<textarea>`, `<select>`에 포커스(`focusin`)되면 `body.is-keyboard-editing` 클래스가 활성화되어 하단 고정바가 즉시 화면 아래로 숨겨집니다.

---

## 4. 시니어 친화 정보 구조 및 무비밀번호 원칙
1. **비밀번호 입력창 전면 금지 (`type="password"` `0건`)**:
   - 우편함 구독(`#hero-passwordless-club-card`), 1줄 응원(`#hero-love-letterbox`), 라디오 사연 접수(`story.html`) 모두 비밀번호 없이 이용 가능합니다.
2. **글쓰기 동선 2대 행동 단순화 (`lounge.html` ➔ `community.html` 통합)**:
   - 중복되던 `lounge.html`은 `community.html`로 통합 리다이렉트 처리하고, 모든 글쓰기 창구를 **`[① 1줄 응원 남기기]`**와 **`[② 라디오 사연 보내기]`** 2가지로 통일했습니다.
3. **정직 고지 배지 & 공정위 문구 가독성**:
   - 가상 트로트 가수 『백운호』 정직 안내 배지(`.honesty-virtual-singer-notice`)와 `💚 김쌤의 콘서트·응원 안심 준비물관` 공정위 대가성 문구(`.ftc-inline-disclosure`)를 `18px~20px` 고대비 박스로 선명하게 노출합니다.
4. **공식 접근성·이용 지원 창구**: `beable9489@gmail.com`

---

## 부록: 페이지별 핵심 DOM ID 및 품질 보증 체크표

| 페이지 | 핵심 역할 | 필수 보존 DOM ID / 데이터 연동 | 검증 기준 |
| :--- | :--- | :--- | :--- |
| `index.html` | 순수 라디오·위로 메인 사랑방 | `#hero-radio-section`, `#main-youtube-embed`, `#hero-family-lounge`, `#hero-love-letterbox`, `#hero-passwordless-club-card`, `#senior-curation-market`, `#hero-brand-partnership-box` | `<h1>` 15단어 이내, 정직 배지 노출 |
| `community.html` | 통합 소통 사랑방 (`lounge.html` 통합) | `#hero-love-letterbox`, `#hero-love-wall-list`, `data/shared_lounge_feed.json`, Abacus `clap_<post_id>` | 전국 방문자 실시간 박수 동기화 |
| `story.html` | `[② 라디오 사연 보내기]` | `#story-submission-form`, `#btn-voice-dictation`, `#story-success-box`, `/hq-mailing-endpoint.json` | 음성 받아쓰기 & 정직 접수 배지 |
| `news.html` | 화·금 정규 편성표 & 백운호 소식란 | `#singer-pills-container`, `#news-feed-grid`, `data/trot_news.json` | 가공 신문기사 `0건`, 공공 건강정보 연결 |
| `booth.html` | 백운호 6벌 의상 무료 촬영관 | `#booth-canvas`, `#character-tray` (`hero_style_01`~`06`), `#save-celebration-modal` | `1080x1440` 클라이언트 합성, 2초 꾹 저장 |
| `vip.html` | 백운호 10대 무료 디지털 선물관 | `#vip-digital-studio`, `#gc-canvas`, `#wp-canvas`, `#lb-song-select` | 전 아이템 무제한 무료, 가짜 카운터 `0건` |

---

## 부록: 페이지별 핵심 DOM ID 및 품질 보증 체크표

| 페이지 | 핵심 역할 | 필수 보존 DOM ID / 데이터 연동 | 검증 기준 |
| :--- | :--- | :--- | :--- |
| `index.html` | 순수 라디오·위로 메인 사랑방 | `#hero-radio-section`, `#main-youtube-embed`, `#hero-family-lounge`, `#hero-love-letterbox`, `#hero-passwordless-club-card`, `#senior-curation-market`, `#hero-brand-partnership-box` | `<h1>` 15단어 이내, 정직 배지 노출 |
| `community.html` | 통합 소통 사랑방 (`lounge.html` 통합) | `#hero-love-letterbox`, `#hero-love-wall-list`, `data/shared_lounge_feed.json`, Abacus `clap_<post_id>` | 전국 방문자 실시간 박수 동기화 |
| `story.html` | `[② 라디오 사연 보내기]` | `#story-submission-form`, `#btn-voice-dictation`, `#story-success-box`, `/hq-mailing-endpoint.json` | 음성 받아쓰기 & 정직 접수 배지 |
| `news.html` | 화·금 정규 편성표 & 백운호 소식란 | `#singer-pills-container`, `#news-feed-grid`, `data/trot_news.json` | 가공 신문기사 `0건`, 공공 건강정보 연결 |
| `booth.html` | 백운호 6벌 의상 무료 촬영관 | `#booth-canvas`, `#character-tray` (`hero_style_01`~`06`), `#save-celebration-modal` | `1080x1440` 클라이언트 합성, 2초 꾹 저장 |
| `vip.html` | 백운호 10대 무료 디지털 선물관 | `#vip-digital-studio`, `#gc-canvas`, `#wp-canvas`, `#lb-song-select` | 전 아이템 무제한 무료, 가짜 카운터 `0건` |
