# GEMINI.md — 4사업부 파라다이스히어로 · 김쌤의영웅라디오 (`paradise-hero.com`) 절대 규칙 (Ground Rules)

이 문서는 `D:\드림컴퍼니\4사업부` 작업 시 루트 `D:\드림컴퍼니\GEMINI.md`와 100% 일관되게 적용되는 하위 규칙입니다. 모든 대화방(`텔레그램`, `hq_main`, `sns_video`, `seo_monetize`, `payment_pg`)은 반드시 루트 `D:\드림컴퍼니\GEMINI.md` 및 `D:\드림컴퍼니\data\hq_ssot_state.json`과 동일한 기준만 답변·수행합니다.

---

## 1. 법인 정체성 · 전담 CEO 봇 · 호스팅 (SSOT)
- **법인명 / 도메인 / 채널**: 4사업부 (`HERO` 법인) — **`https://paradise-hero.com`** (**GitHub Pages**, `jjangdol0205/paradise-hero.git` `main`) & 유튜브 **`@김쌤의영웅라디오`**
- **전담 CEO 봇**: **`@inves123_bot`** (`4사업부/.env`의 `TELEGRAM_BOT_TOKEN`) / 그룹 비서실장·감사관: **`@Allcompany1_bot`**
- **오리지널 가상(버추얼) 트로트가수 『백운호』 세계관 전환 (실존 연예인 `0건`)**:
  - 초상권·성명권·음성권 리스크를 원천 제거하기 위해 **`황영웅` 등 실존 트로트 가수 성명·초상·파일명을 모든 웹·영상·칼럼·메일링에서 `0건`으로 배제**하고, 자체 오리지널 가상 트로트가수 **『백운호 (Baek Woon-ho, 대표곡 〈어머니의 봄날〉·〈백운호 연가〉)』** 및 **`유튜브 @김쌤의영웅라디오 따뜻한 가족 사랑방`**으로 운영합니다 (대문 H1 내 `'안심 장터'` 및 `'공식 팬 쉼터'` 사칭 오해 문구 금지).
  - **시니어 사랑방 진정성 & 실시간 공유 담벼락**: `localStorage` 전용 가짜 담벼락·가짜 난수 카운터·가공 기사를 금지하고, Google Apps Script 공유 피드로 전국 애청자 응원글·박수가 실시간 공유되게 운영합니다 (`lounge.html`은 `community.html`로 단일 통합).
  - **건전한 국내 실물 준비물관 & 브랜드 협찬 (해외 PG `0건`)**: 무관 상품(`아이클타임 키성장`, `실내동물원`, `알파카월드`) 및 오해 소지 명칭(`골드 VIP 월 9,900원`)을 폐지하고, **`[💚 김쌤의 콘서트·응원 안심 준비물관]`**(응원 보온/방석/보조배터리·목 도라지배즙·눈 루테인 6~8선, 공정위 제휴 고지 명시)과 하단 공식 브랜드 협찬 창구(`#hero-brand-partnership-box`)만 운영합니다.

---

## 2. 시니어 WCAG AAA 접근성 · 고정 배너 가림 해소 · 잠근 DOM 보호
- **상·하단 고정 배너 화면 가림 원천 차단**: 시니어 가독성을 해치는 상·하단 과대 고정(sticky/fixed) 배너를 제거·슬림화하여 깨끗한 본문 열람 뷰포트를 보장합니다 (모바일 라디오 플레이어는 `<=60px` 초슬림 바 또는 비고정 플레이어로 정리, 입력창/메뉴 가림 `0건`).
- **최소 본문 폰트 `20px` 이상**, **터치 타겟 높이 `60px` 이상**, **글자 크기 3단계 조절기**를 항상 유지합니다.
- 잠근 핵심 DOM(`#hero-family-lounge`, `#hero-love-letterbox`, `#hero-passwordless-club-card`, `#hero-brand-partnership-box`)을 항상 보존합니다.

---

## 3. 실서버 배포 및 `/live-audit` 출구 잠금
- 웹 수정 시 원본 수정 및 빌드 갱신 ➜ `git commit & push` (`jjangdol0205/paradise-hero.git` `main`) ➜ CDN 전파 대기 후 `python "C:\Users\jjang\.gemini\config\skills\live-audit\run_live_audit.py" paradise-hero.com` `ALL PASS` 확인 후 보고합니다.
