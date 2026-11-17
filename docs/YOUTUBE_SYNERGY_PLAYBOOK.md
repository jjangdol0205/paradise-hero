# 📺 유튜브 `@김쌤의영웅라디오` & `paradise-hero.com` 시너지 운영 플레이북

## 1. 채널 및 사랑방 핵심 정체성
- **채널명**: 유튜브 **`@김쌤의영웅라디오`**
- **공식 웹 사랑방**: **`https://paradise-hero.com`** (PARADISE HERO · 김쌤의영웅라디오 가족 사랑방)
- **전속 오리지널 가상 트로트 가수**: **『백운호 (Baek Woon-ho)』**
  - 타이틀곡 **〈어머니의 봄날〉** 외 **〈백운호 연가〉**, **〈항구의 등불〉**, **〈다시 피는 동백꽃〉**, **〈고향역 첫차〉**, **〈내 인생의 금빛 노을〉**
  - 실존 연예인 성명·초상·곡명 사용 `0건` 원칙을 엄격히 준수합니다.

---

## 2. 정규 편성 및 무타자(Zero-Typing) 웹 유입 동선

### ① 화요일·금요일 저녁 18:00 KST 15분 롱폼 사연 라디오
1. **본문 80% 순수 청취자 인생 사연 & 중저음 트로트 위로**:
   - `story.html` (`[② 라디오 사연 보내기]`)과 `community.html` (`[① 1줄 응원 남기기]`)을 통해 접수된 5070 시니어 가족분들의 실제 사연을 김쌤 DJ가 따뜻한 호흡으로 낭독하고 백운호의 오리지널 트로트를 함께 들려드립니다.
2. **설명란 첫 줄 & 고정댓글 원터치 연결 표준**:
   - 시니어 시청자분들이 영문 주소를 외워 치실 필요 없이 터치 한 번으로 이동하실 수 있도록 고정댓글에 아래 링크를 명확히 안내합니다:
   ```text
   💚 어머님·아버님, 당신이 우리 인생의 진짜 영웅입니다!
   📸 백운호 6벌 의상 무료 기념사진 찍기 👉 https://paradise-hero.com/booth.html
   💌 다음 라디오 방송에 내 사연 보내기 👉 https://paradise-hero.com/story.html
   🛍️ 김쌤의 콘서트·응원 안심 준비물관 (네이버페이 공식관) 👉 https://cshop.naver.com/paradiseshop
   ※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다.
   ```

### ② 일일 쇼츠 하이라이트 (`1080x1920`) 무타자 2터치 연결
- 쇼츠 본문(`Cut 0~3`)에서는 상업 배너 없이 100% 공감 사연과 노래 감동에만 집중합니다.
- 종료 3초(`Cut 4`)에서는 **① 하단 채널 프로필 터치 안내** 및 **② 쇼츠 `▶ 관련 동영상(Related Video)` 1터치 연결(최신 15분 롱폼 본방송 ➔ 고정댓글 파란 링크)**로 자연스럽게 `https://paradise-hero.com` 사랑방과 연결합니다.

---

## 3. 웹 유입 후 가치 사다리 & 커뮤니티 정착 루프
1. **무료 라디오 & 백운호 대표곡 청취 (`index.html`, `radio.html`, `stream.html`)**:
   - 본문 16:9 유튜브 공식 IFrame API 플레이어(`enablejsapi=1`)와 모바일 `58px` 1줄 컴팩트 하단 바를 통해 끊김 없는 청취 경험을 제공하며, 실재생 `330초(5분 30초)` 도달 시 `radio_5m30s` 비콘을 계측합니다.
2. **실시간 교차 방문자 공감 박수 & 출석 루프 (`community.html`, `#hero-family-lounge`)**:
   - `data/shared_lounge_feed.json`과 Abacus `clap_<post_id>` API로 전국 청취자 간 실시간 박수 응원을 연결하고, 비밀번호 없는 3초 무료 우편함(`#hero-passwordless-club-card`)으로 화·금 방송 알림을 발송합니다.
3. **무료 디지털 선물 & 건전한 실물 준비물관 (`booth.html`, `vip.html`, `#senior-curation-market`)**:
   - 무료 기념사진·안부카드 저장 후 자연스럽게 `💚 김쌤의 콘서트·응원 안심 준비물관`(블루투스 스피커·보조배터리·이어폰·방석·보온숄·루테인·도라지배즙 7종) 및 브랜드 협찬 창구(`beable9489@gmail.com`)로 이어집니다.

---

## 4. 운영 안전 가드레일 체크리스트
- 실존 연예인 성명·영문 슬러그·초상 파일 혼입: **절대 금지 (`0건`)**
- 가짜 신문사 기사 및 가짜 난수 카운터(`318 + ...` 등): **절대 금지 (`0건`)**
- 시니어 무관 제휴 품목 및 과장 상업 문구(`최저가` 등): **절대 금지 (`0건`)**
- 공식 지원 및 제휴 이메일: **`beable9489@gmail.com`**

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
