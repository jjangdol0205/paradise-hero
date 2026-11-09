# 👑 4사업부 (`paradise-hero.com` & `@김쌤의영웅라디오`) 10대 트로트 왕자 데일리 쇼츠 스토리라인 & Google Flow (`Veo 3.1 Fast`) 마스터 프롬프트 팩

이 문서는 사장님께서 기상 직후 **Google Flow (`Veo 3.1 Fast`, 9:16 세로형)**에 그대로 복사·붙여넣기하여 생성하거나, 로컬 원클릭 마스터 파이프라인(`python scripts/run_daily_shorts_master.py --episode 1~10`)으로 즉시 렌더링해 **`@김쌤의영웅라디오` 유튜브 쇼츠 & 인스타그램 릴스(`@kimteacher_heroradio`)**에 매일 업로드할 수 있도록 설계된 **10인 트로트 왕자 세계관(황실 파라다이스 연대기) 10부작 마스터 패키지**입니다.

---

## 🚀 기상 후 1분 실행 가이드

1. **이미 렌더링 완료된 제1화 즉시 업로드 파일**:
   - **완성 본편 영상 (`1080×1920`, 30fps, 1.2배속 무공백 TTS + 효과음 + 세이프존 자막)**: `D:\드림컴퍼니\4사업부\content\shorts_daily\ep_01\shorts_ep01_1080x1920.mp4`
   - **유튜브 쇼츠 / 인스타 릴스 복붙용 제목·설명·해시태그**: `D:\드림컴퍼니\4사업부\content\shorts_daily\ep_01\metadata_ep01.md`
2. **제2화 ~ 제10화 원클릭 자동 생성 명령어**:
   ```powershell
   cd D:\드림컴퍼니\4사업부
   python scripts/run_daily_shorts_master.py --episode 2
   ```
3. **Google Flow (`Veo 3.1 Fast`) 고화질 배경 클립 생성 시**:
   - 아래 **Day 1 ~ Day 10 캐릭터별 `Veo 3.1 Fast` 전용 영문 프롬프트**를 복사해 Flow에서 `9:16 Vertical`로 생성하신 뒤, 포토부스 및 쇼츠 배경 리소스로 활용하실 수 있습니다.

---

## 🌟 10대 트로트 왕자 데일리 스토리라인 & Flow (`Veo 3.1 Fast`) 프롬프트 (Day 1 ~ Day 10)

### Day 1. 황영웅 — 「감성 황태자의 에메랄드빛 약속」 (Episode 01 메인)
- **캐릭터 컨셉**: 감성 황태자 (`#1B4D3E` 에메랄드 & `#D4AF37` 골드 제복, 수호 브로치, 골드 마이크)
- **스토리라인 요약**: 어두운 밤 홀로 눈물짓던 어머님들의 손을 잡아주며, 에메랄드빛 황실 무대 위에서 묵직한 중저음 사모곡으로 기적의 위로를 건네는 서막.
- **내레이션 훅 (0~2초)**: *"심금을 울리는 중저음 보이스! 어머님들이 이 목소리에 눈물 흘리는 진짜 이유!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 nostalgic 90s shoujo manga royal anime style, ultra-detailed cel-shaded animation. A handsome Korean trot crown prince with gentle warm eyes and a charismatic smile, wearing a deep emerald green and gold-trimmed royal uniform with an emerald guardian brooch, holding a vintage golden microphone on a grand palace stage. Sparkling golden rose petals and warm emerald starlight floating in the air, emotional cinematic lighting, smooth slow-motion camera push-in, clean fullscreen, no text, no watermark.
  ```

### Day 2. 임영웅 — 「별빛 황제 왕자의 건행 세레나데」 (Episode 02)
- **캐릭터 컨셉**: 별빛 황제 왕자 (`#38BDF8` 스카이블루 & 순백 연미복, 별빛 후광, 건행 손인사)
- **스토리라인 요약**: 밤하늘의 은하수가 쏟아지는 유리 궁전 테라스에서 어머님들의 건강과 행복('건행')을 기원하며 황영웅 황태자와 뜨거운 우정의 축배를 나누는 이야기.
- **내레이션 훅 (0~2초)**: *"하늘에서 내려온 별빛 고음! 온 세상을 푸른 감동으로 물들인 건행의 기적!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 nostalgic classic shoujo anime prince aesthetic. A noble Korean anime prince with a refined gentle smile, dressed in an immaculate white royal tailcoat with a sky-blue silk cravat and silver starlight shoulder epaulets, giving a warm respectful hand salute under a glowing galaxy night sky. Shimmering blue stardust particles and crystal chandelier reflections, cinematic lens flare, clean fullscreen, no text, no watermark.
  ```

### Day 3. 이찬원 — 「찬또 브레인 왕자의 백합꽃 효도 편지」 (Episode 03)
- **캐릭터 컨셉**: 찬또 브레인 왕자 (`#FB7185` 로즈골드 & 브리티시 황실 제복, 앤틱 금테 안경, 백합꽃)
- **스토리라인 요약**: 황실 대도서관에서 어머님들이 보내주신 구구절절한 사연 복덕방 편지를 한 글자씩 소중히 읽으며 눈시울을 붉히고 답가를 바치는 감동 에피소드.
- **내레이션 훅 (0~2초)**: *"천재 브레인 왕자가 어머님 편지를 읽다가 끝내 눈물 쏟은 사연은?"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 romantic shoujo anime illustration in motion. A bright and intelligent young royal prince wearing antique gold-rimmed glasses and a rose-pink and cream British royal dress uniform, holding a bouquet of glowing white lilies in a sunlit grand royal library. Warm golden dust motes, gentle eye-smile, fluttering flower petals, clean fullscreen, no text, no watermark.
  ```

### Day 4. 영탁 — 「청량 에너지 왕자의 사파이어 축포」 (Episode 04)
- **캐릭터 컨셉**: 청량 에너지 왕자 (`#2563EB` 코발트 블루 사파이어 재킷, 엄지 척 포즈)
- **스토리라인 요약**: 지치고 우울했던 어머님들의 일상에 짜릿한 청량 에너지와 '진짜배기' 웃음꽃을 터뜨리며 황실 무대를 축제의 장으로 바꾸는 반전 에피소드.
- **내레이션 훅 (0~2초)**: *"단 2초 만에 어머님들 어깨를 들썩이게 만든 진짜배기 사파이어 왕자님!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 vibrant shoujo-manhwa prince animation. An energetic charismatic Korean anime prince in a dazzling cobalt-blue sapphire royal jacket with silver embroidery, giving a confident thumbs-up and a radiant refreshing smile on a festival palace balcony. Dynamic blue light ribbons and sparkling confetti in the air, high-energy camera movement, clean fullscreen, no text, no watermark.
  ```

### Day 5. 정동원 — 「음악 신동 소년왕자의 황금 색소폰 선율」 (Episode 05)
- **캐릭터 컨셉**: 음악 신동 소년왕자 (`#10B981` 민트 왕자 케이프, 골든 색소폰/바이올린, 요정 눈웃음)
- **스토리라인 요약**: 할머니·어머님들의 영원한 손자이자 비타민 소년왕자가 황금 색소폰 연주로 형님 왕자들과 할머니들의 마음을 하나로 이어주는 따뜻한 가족 서사.
- **내레이션 훅 (0~2초)**: *"어머님들의 영원한 비타민! 소년왕자의 황금 색소폰이 울려 퍼지는 순간!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 enchanting shoujo anime style. A cheerful young royal boy prince wearing a mint-emerald velvet cape with gold trim, holding a gleaming golden saxophone in a magical royal garden filled with glowing fireflies and musical notes floating in mid-air. Warm heartwarming expression, soft pastel lighting, clean fullscreen, no text, no watermark.
  ```

### Day 6. 김호중 — 「트바로티 고결 왕자의 오페라 대성당」 (Episode 06)
- **캐릭터 컨셉**: 트바로티 고결 왕자 (`#9333EA` 로열 퍼플 오페라 망토, 황금 엠블럼)
- **스토리라인 요약**: 웅장한 황실 오페라 하우스의 스테인드글라스 빛 아래에서 천상을 울리는 성량으로 어머님들의 한(恨)을 씻어주는 전율의 무대.
- **내레이션 훅 (0~2초)**: *"성악과 트롯이 만난 세기의 성량! 천장을 뚫는 고결 왕자의 전율 보이스!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 majestic shoujo anime royal opera aesthetic. A dignified Korean prince with a powerful presence, wearing a royal purple velvet opera cape with golden crest over a double-breasted tuxedo, singing passionately beneath illuminated cathedral stained-glass windows. Dramatic volumetric purple and gold light rays, swirling golden sparkles, clean fullscreen, no text, no watermark.
  ```

### Day 7. 장민호 — 「로맨틱 신사 왕자의 샴페인 골드 에스코트」 (Episode 07)
- **캐릭터 컨셉**: 로맨틱 신사 왕자 (`#F59E0B` 샴페인 골드 턱시도, 조각 같은 비주얼, 젠틀한 에스코트 손길)
- **스토리라인 요약**: 황실 무도회장 입구에서 어머님 한 분 한 분께 정중히 손을 내밀며 소녀 시절의 설렘을 되찾아 주는 로맨틱 신사 왕자의 에스코트.
- **내레이션 훅 (0~2초)**: *"어머님들을 단숨에 열여덟 소녀로 되돌려 놓은 조각 같은 신사 왕자님의 손길!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 classic romantic shoujo manga prince style. A tall, handsomely sculpted gentleman prince with warm crinkled eyes, dressed in a champagne-gold royal tuxedo with a white silk pocket square, extending a gloved hand graciously on a grand marble staircase. Warm chandelier glow, floating golden sparkles and white rose petals, clean fullscreen, no text, no watermark.
  ```

### Day 8. 박서진 — 「열정의 장구 왕자와 닻별의 축제」 (Episode 08)
- **캐릭터 컨셉**: 열정의 장구 왕자 (`#EAB308` 골든 옐로우 제복, 황금 장구채, 닻별 엠블럼, 흩날리는 꽃잎)
- **스토리라인 요약**: 효심 가득한 미소년 장구 왕자가 황금 장구채를 휘두르며 묵은 체증과 시름을 단번에 날려버리는 신명 나는 황실 연회.
- **내레이션 훅 (0~2초)**: *"황금 장구채가 춤추는 순간, 어머님들의 모든 시름이 눈 녹듯 사라집니다!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 dynamic shoujo anime royal festival aesthetic. A youthful handsome prince in a radiant golden-yellow royal uniform adorned with a star-anchor emblem, dynamically wielding twin golden drum sticks surrounded by swirling cherry blossom petals and golden lightning sparks. Vibrant celebratory atmosphere, crisp cel-shaded animation, clean fullscreen, no text, no watermark.
  ```

### Day 9. 손태진 — 「크로스오버 클래식 왕자의 와인빛 로즈 세레나데」 (Episode 09)
- **캐릭터 컨셉**: 크로스오버 클래식 왕자 (`#9F1239` 버건디 와인 벨벳 수트, 붉은 장미, 그랜드 피아노)
- **스토리라인 요약**: 달빛이 비치는 황실 온실의 그랜드 피아노 앞에서 붉은 장미 한 송이와 감미로운 바리톤 세레나데로 깊은 밤의 평안을 선물하는 이야기.
- **내레이션 훅 (0~2초)**: *"깊은 밤 귓가에 속삭이는 와인빛 바리톤, 어머님들의 마음을 녹이는 세레나데!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 aristocratic shoujo anime romance style. A tall refined baritone prince in a burgundy wine velvet royal suit, holding a deep crimson rose beside a gleaming black grand piano in a moonlit crystal conservatory. Soft crimson and silver moonlight reflections, drifting rose petals, clean fullscreen, no text, no watermark.
  ```

### Day 10. 안성훈 · 진해성 — 「정통 감성 마스터 왕자와 10대 왕자 대합창 피날레」 (Episode 10)
- **캐릭터 컨셉**: 정통 감성 마스터 왕자 (`#0D9488` 비취 틸 & 전통 자개 문양 황실 예복) + **황영웅 포함 10대 왕자 전원 집결**
- **스토리라인 요약**: 정통 트롯의 깊은 뿌리를 지키는 마스터 왕자와 감성 황태자 황영웅을 필두로 10대 왕자 전원이 황금 무대에 모여 영원한 동행을 맹세하고 `paradise-hero.com` 포토부스로 어머님들을 초대하는 대단원.
- **내레이션 훅 (0~2초)**: *"가슴 깊은 곳을 울리는 정통 트롯의 진수! 마침내 10대 왕자가 하나로 모였습니다!"*
- **Google Flow (`Veo 3.1 Fast`) 9:16 프롬프트**:
  ```text
  Vertical 9:16 grand finale shoujo anime royal ensemble scene. Ten handsome Korean royal trot princes in distinct jewel-toned royal uniforms—led by the emerald-and-gold crown prince at the center alongside teal mother-of-pearl, sky-blue, rose-pink, cobalt, mint, purple, champagne-gold, yellow, and burgundy princes—standing together on a magnificent golden palace stage under a shower of golden starlight. Epic uplifting camera crane shot, clean fullscreen, no text, no watermark.
  ```
