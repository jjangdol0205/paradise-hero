# 👑 [4사업부] 파라다이스히어로 · 영웅라디오 — `paradise-hero.com`

- **소속**: 드림컴퍼니 **4사업부 (`D:\드림컴퍼니\4사업부`)**
- **전담 텔레그램 봇**: **`[4사업부] 파라다이스히어로 · 영웅라디오`** (`@inves123_bot`)
- **공식 홈페이지**: **[https://paradise-hero.com](https://paradise-hero.com)**
- **공식 유튜브 채널 (롱폼 라디오)**: **[https://www.youtube.com/@김쌤의영웅라디오](https://www.youtube.com/@%EA%B9%80%EC%8C%A4%EC%9D%98%EC%98%81%EC%9B%85%EB%9D%BC%EB%94%94%EC%98%A4)**

---

## 1. 4대 핵심 수익화 파이프라인 (`docs/PARADISE_HERO_MONETIZATION_BLUEPRINT.md`)
1. **유튜브 15분+ 롱폼 라디오 애드센스 & 슈퍼땡스**: 5070 시니어 완청률 극대화 3막 구조 라디오 방송으로 미드롤 광고 3~4회 삽입 및 고정댓글 `paradise-hero.com` 유입
2. **파라다이스 골드 VIP 멤버십 (`vip.html`)**: 월 9,900원 / 연 99,000원 정기구독 (무광고 연속 청취, 김쌤의 방송 호명, 콘서트 선예매 알림, 고화질 배경화면)
3. **실시간 황금 응원 전광판 & 사연 우선 채택권 (`story.html`, `community.html`)**: 3,000원~50,000원 소액 팬덤 후원 및 상단 황금 배너 노출
4. **5070 시니어 라이프스타일 큐레이션 커머스 (`stream.html`)**: 콘서트 준비물(방석·망원경·보조배터리) 및 프리미엄 효도 건강식품 제휴 큐레이션

---

## 2. 시니어 친화(WCAG AAA) 6대 웹페이지 구성
- [`index.html`](file:///D:/드림컴퍼니/4사업부/index.html): 메인 포털 (오늘의 라디오 방송, 실시간 황금 응원 전광판, 일일 출석 도장판)
- [`radio.html`](file:///D:/드림컴퍼니/4사업부/radio.html): `@김쌤의영웅라디오` 다시듣기 아카이브 & 챕터 점프 플레이어
- [`story.html`](file:///D:/드림컴퍼니/4사업부/story.html): 초간편 3단계 사연 접수 & 음성 녹음 안내
- [`stream.html`](file:///D:/드림컴퍼니/4사업부/stream.html): 원클릭 스트리밍/투표 가이드 & 콘서트 준비물 큐레이션
- [`community.html`](file:///D:/드림컴퍼니/4사업부/community.html): 지역별 팬 사랑방 & 콘서트 동행 찾기
- [`vip.html`](file:///D:/드림컴퍼니/4사업부/vip.html): 파라다이스 골드 VIP 멤버십 가입 & 황금 전광판 후원

---

## 3. `@김쌤의영웅라디오` 롱폼 자동 제작 명령어
```powershell
cd "D:\드림컴퍼니\4사업부"
python scripts/run_daily_radio_master.py --episode 1
node tests/test_paradise_hero_suite.js
```
