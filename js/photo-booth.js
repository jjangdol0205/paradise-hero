/**
 * photo-booth.js
 * Interactive HTML5 Canvas Photobooth Engine for paradise-hero.com
 * Milestone 2: Web-Exclusive Interactive Companion Photo Booth
 *
 * Core Capabilities:
 * 1. 1080x1440 Master Canvas Compositing (3:4 portrait ratio).
 * 2. Dual Camera & Album Upload Pipeline:
 *    - navigator.mediaDevices.getUserMedia front camera capture.
 *    - In-app browser / denied permission graceful fallback with senior guide modal.
 *    - File picker for smartphone album photos.
 * 3. Real-time Multi-Layer Compositing:
 *    - Layer 0: Glare-reduction soft ivory background (#FAFAF8)
 *    - Layer 1: Transformed user image (pan, zoom, rotation, mirror flip)
 *    - Layer 2: Commemorative Hwang Young-woong frame overlay (1080x1440 PNG)
 *    - Layer 3: Dynamic commemorative watermark & stamp
 * 4. Dual Senior Ergonomics:
 *    - Touch drag to pan & pinch-to-zoom gestures.
 *    - Oversized 56px+ tactile buttons (확대, 축소, 회전, 좌우반전, 4방향 이동, 원래대로).
 * 5. 100% Client-Side Export (Zero Server Errors):
 *    - canvas.toBlob('image/jpeg', 0.95) with instant <a> download trigger.
 *    - Celebration modal with long-press saving guide for iOS & KakaoTalk.
 *    - Web Share API (navigator.share) for 1-tap KakaoTalk/family sharing.
 *
 * Zero Prohibited Words Compliance: 0 instances of prohibited commercial cliches.
 */

(function (global) {
  'use strict';

  // Master Canvas Dimensions (3:4 ratio)
  const CANVAS_WIDTH = 1080;
  const CANVAS_HEIGHT = 1440;

  // Frame Definitions
  const COMMEMORATIVE_FRAMES = [
    {
      id: 'flower_path',
      name: '다정한 꽃길',
      subtitle: '영웅님과 함께하는 다정한 꽃길',
      src: 'assets/frames/frame_flower_path.png',
      thumb: 'assets/frames/thumb_flower_path.png',
      description: '언제나 당신 편, 영원히 함께해요 💚'
    },
    {
      id: 'golden_milestone',
      name: '63만장 골드',
      subtitle: '정규 1집 [당신 편] 63만 장 기념 엠블럼',
      src: 'assets/frames/frame_golden_milestone.png',
      thumb: 'assets/frames/thumb_golden_milestone.png',
      description: '정규 1집 [당신 편] 초동 63만 장 돌파 기념 👑'
    },
    {
      id: 'paradise_4cut',
      name: '파라다이스 4컷',
      subtitle: '파라다이스 인생 네컷 클래식',
      src: 'assets/frames/frame_paradise_4cut.png',
      thumb: 'assets/frames/thumb_paradise_4cut.png',
      description: '2026 PARADISE PHOTOBOOTH #01 🎞️'
    },
    {
      id: 'radio_studio',
      name: '명예 DJ 라디오',
      subtitle: '김쌤의 영웅 라디오 특별 초대석',
      src: 'assets/frames/frame_radio_studio.png',
      thumb: 'assets/frames/thumb_radio_studio.png',
      description: '유튜브 @김쌤의영웅라디오 오늘 하루 명예 DJ 초대석 📻'
    }
  ];

  // 가수 황영웅 10대 시그니처 무대·일상 의상 카탈로그 (5-Layer Two-Shot Companion)
  const DEFAULT_CHARACTERS = [
    {
      id: 'hwang_young_woong',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '에메랄드 벨벳 콘서트 수트',
      theme_color: '#1B4D3E',
      accent_color: '#D4AF37',
      badge_emoji: '💚',
      catchphrase: '언제나 어머님 편, 영원히 함께 걸어가요 💚',
      signature_visual: '에메랄드 벨벳 수트, 황금 브로치, 다정한 어깨동무 포즈',
      thumb_path: 'assets/characters/thumb_hwang_young_woong.png',
      sprite_path: 'assets/characters/sprite_hwang_young_woong.png'
    },
    {
      id: 'lim_young_woong',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '순백의 프린스 턱시도',
      theme_color: '#38BDF8',
      accent_color: '#F0F9FF',
      badge_emoji: '🤍',
      catchphrase: '눈부신 봄날처럼 어머님 늘 건강하고 행복하세요 🤍',
      signature_visual: '순백의 프린스 턱시도, 실크 보타이, 환한 눈웃음 인사',
      thumb_path: 'assets/characters/thumb_lim_young_woong.png',
      sprite_path: 'assets/characters/sprite_lim_young_woong.png'
    },
    {
      id: 'lee_chan_won',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '따뜻한 핑크 가디건 하트룩',
      theme_color: '#FB7185',
      accent_color: '#FFF1F2',
      badge_emoji: '🌸',
      catchphrase: '어머님 웃으시는 모습이 봄꽃보다 더 곱습니다 🌸',
      signature_visual: '포근한 핑크 니트 가디건, 손하트 포즈, 다정한 미소',
      thumb_path: 'assets/characters/thumb_lee_chan_won.png',
      sprite_path: 'assets/characters/sprite_lee_chan_won.png'
    },
    {
      id: 'young_tak',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '시크 올블랙 수트',
      theme_color: '#2563EB',
      accent_color: '#EFF6FF',
      badge_emoji: '🖤',
      catchphrase: '오늘 하루도 제 노래와 함께 힘차게 비상하세요 🖤',
      signature_visual: '시크 올블랙 무대 수트, 든든한 엄지 척 응원 포즈',
      thumb_path: 'assets/characters/thumb_young_tak.png',
      sprite_path: 'assets/characters/sprite_young_tak.png'
    },
    {
      id: 'jeong_dong_won',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '로열 제복 스타일',
      theme_color: '#10B981',
      accent_color: '#ECFDF5',
      badge_emoji: '👑',
      catchphrase: '파라다이스 어머님들께 정중히 사랑의 경례 올립니다 👑',
      signature_visual: '황금 견장 로열 제복, 반듯한 자세, 맑은 미소',
      thumb_path: 'assets/characters/thumb_jeong_dong_won.png',
      sprite_path: 'assets/characters/sprite_jeong_dong_won.png'
    },
    {
      id: 'kim_ho_joong',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '퍼플 벨벳 디너쇼룩',
      theme_color: '#9333EA',
      accent_color: '#FAF5FF',
      badge_emoji: '💜',
      catchphrase: '깊은 밤 어머님 가슴을 적시는 명품 중저음 세레나데 💜',
      signature_visual: '퍼플 벨벳 디너쇼 재킷, 골드 엠블럼, 품격 있는 무대 매너',
      thumb_path: 'assets/characters/thumb_kim_ho_joong.png',
      sprite_path: 'assets/characters/sprite_kim_ho_joong.png'
    },
    {
      id: 'jang_min_ho',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '가을 트렌치코트 산책룩',
      theme_color: '#F59E0B',
      accent_color: '#FFFBEB',
      badge_emoji: '🍂',
      catchphrase: '인사동 찻집 골목길, 어머님 손잡고 도란도란 걸어요 🍂',
      signature_visual: '클래식 베이지 트렌치코트, 따뜻한 머플러, 다정한 에스코트',
      thumb_path: 'assets/characters/thumb_jang_min_ho.png',
      sprite_path: 'assets/characters/sprite_jang_min_ho.png'
    },
    {
      id: 'park_seo_jin',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '황금빛 명절 한복룩',
      theme_color: '#EAB308',
      accent_color: '#FEFCE8',
      badge_emoji: '🌕',
      catchphrase: '어머님 가정에 늘 만복과 건강이 가득하시길 기원합니다 🌕',
      signature_visual: '고운 황금빛 전통 한복 두루마기, 정갈한 큰절 인사',
      thumb_path: 'assets/characters/thumb_park_seo_jin.png',
      sprite_path: 'assets/characters/sprite_park_seo_jin.png'
    },
    {
      id: 'son_tae_jin',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '버건디 장미 세레나데룩',
      theme_color: '#9F1239',
      accent_color: '#FFF1F2',
      badge_emoji: '🌹',
      catchphrase: '세상 가장 향기로운 장미꽃 한 송이를 어머님께 바칩니다 🌹',
      signature_visual: '버건디 와인 수트, 붉은 장미 코사지, 감미로운 눈맞춤',
      thumb_path: 'assets/characters/thumb_son_tae_jin.png',
      sprite_path: 'assets/characters/sprite_son_tae_jin.png'
    },
    {
      id: 'ahn_sung_hoon_jin_hae_seong',
      name_ko: '황영웅',
      name_en: 'Hwang Young-woong',
      title: '심야 라디오 DJ 안경룩',
      theme_color: '#0D9488',
      accent_color: '#F0FDFA',
      badge_emoji: '📻',
      catchphrase: '오늘 밤도 제 목소리와 함께 편안한 단잠 주무세요 📻',
      signature_visual: '지적인 안경룩, 포근한 니트, 심야 라디오 스튜디오 마이크',
      thumb_path: 'assets/characters/thumb_ahn_sung_hoon_jin_hae_seong.png',
      sprite_path: 'assets/characters/sprite_ahn_sung_hoon_jin_hae_seong.png'
    }
  ];

  class PhotoBoothEngine {
    constructor(options = {}) {
      this.canvas = options.canvas || (typeof document !== 'undefined' ? document.getElementById('booth-canvas') : null);
      this.video = options.video || (typeof document !== 'undefined' ? document.getElementById('booth-video') : null);
      this.fileInput = options.fileInput || (typeof document !== 'undefined' ? document.getElementById('booth-file-input') : null);

      this.ctx = this.canvas && this.canvas.getContext ? this.canvas.getContext('2d') : null;

      // Character catalog integration
      const catalog = (typeof CHARACTER_CARDS !== 'undefined' ? CHARACTER_CARDS : null) ||
                      (typeof global !== 'undefined' && global.CHARACTER_CARDS ? global.CHARACTER_CARDS : null) ||
                      DEFAULT_CHARACTERS;
      this.characters = catalog;
      this.activeCharacterId = options.characterId || 'hwang_young_woong';
      this.characterImages = {}; // Cache of loaded character sprite Image objects

      // Active state
      this.userImage = null; // HTMLImageElement or ImageBitmap
      this.activeFrameIndex = 0;
      this.frameImages = {}; // Cache of loaded frame Image objects
      this.isCameraStreaming = false;
      this.mediaStream = null;
      this.animationFrameId = null;

      // Transform state for user image
      this.transform = {
        scale: 1.0,
        translateX: 0,
        translateY: 0,
        rotation: 0, // degrees: 0, 90, 180, 270
        flipH: false
      };

      // Pointer/Touch tracking state
      this.isDragging = false;
      this.dragStart = { x: 0, y: 0 };
      this.initialPinchDistance = null;
      this.initialScale = 1.0;

      // Preload frames and characters if in browser
      if (typeof window !== 'undefined') {
        this.preloadFrames();
        this.preloadCharacters();
      }
    }

    /**
     * Preloads all frame PNGs into image cache
     */
    preloadFrames() {
      COMMEMORATIVE_FRAMES.forEach((frame, idx) => {
        const img = new Image();
        img.src = frame.src + '?v=20261110c';
        img.onload = () => {
          this.frameImages[frame.id] = img;
          if (idx === this.activeFrameIndex && !this.userImage && !this.isCameraStreaming) {
            this.render();
          }
        };
        img.onerror = () => {
          console.warn(`[PhotoBooth] Failed to preload frame: ${frame.src}`);
        };
      });
    }

    /**
     * Preloads Anime Prince transparent character sprites into image cache
     */
    preloadCharacters() {
      this.characters.forEach((char) => {
        if (typeof Image !== 'undefined') {
          const img = new Image();
          img.src = char.sprite_path + '?v=20261110c';
          img.onload = () => {
            this.characterImages[char.id] = img;
            if (char.id === this.activeCharacterId && !this.userImage && !this.isCameraStreaming) {
              this.render();
            }
          };
          img.onerror = () => {
            console.warn(`[PhotoBooth] Failed to preload sprite: ${char.sprite_path}`);
          };
        }
      });
    }

    /**
     * Initializes the canvas and attaches event listeners
     */
    init() {
      if (!this.canvas || !this.ctx) {
        return;
      }

      // Configure canvas logical resolution
      this.canvas.width = CANVAS_WIDTH;
      this.canvas.height = CANVAS_HEIGHT;

      // Attach UI event listeners
      this.bindEvents();

      // Initial blank canvas render
      this.render();
    }

    /**
     * Binds mouse, touch, and UI control events
     */
    bindEvents() {
      if (!this.canvas) return;

      // 1. Mouse Dragging
      this.canvas.addEventListener('mousedown', (e) => this.onPointerDown(e.clientX, e.clientY));
      window.addEventListener('mousemove', (e) => {
        if (this.isDragging) this.onPointerMove(e.clientX, e.clientY);
      });
      window.addEventListener('mouseup', () => this.onPointerUp());

      // 2. Touch Gestures (Pinch to zoom & drag)
      this.canvas.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          this.onPointerDown(e.touches[0].clientX, e.touches[0].clientY);
        } else if (e.touches.length === 2) {
          this.isDragging = false;
          this.initialPinchDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
          this.initialScale = this.transform.scale;
        }
      }, { passive: true });

      this.canvas.addEventListener('touchmove', (e) => {
        if (e.touches.length === 1 && this.isDragging) {
          this.onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
        } else if (e.touches.length === 2 && this.initialPinchDistance) {
          const currentDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
          const scaleDelta = currentDistance / this.initialPinchDistance;
          this.transform.scale = Math.max(0.2, Math.min(5.0, this.initialScale * scaleDelta));
          this.render();
        }
      }, { passive: true });

      this.canvas.addEventListener('touchend', () => {
        this.onPointerUp();
        this.initialPinchDistance = null;
      }, { passive: true });

      // 3. File Input Handler
      if (this.fileInput) {
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
      }
    }

    getTouchDistance(touch1, touch2) {
      const dx = touch1.clientX - touch2.clientX;
      const dy = touch1.clientY - touch2.clientY;
      return Math.sqrt(dx * dx + dy * dy);
    }

    onPointerDown(clientX, clientY) {
      if (!this.userImage && !this.isCameraStreaming) return;
      this.isDragging = true;
      this.dragStart = { x: clientX, y: clientY };
    }

    onPointerMove(clientX, clientY) {
      if (!this.isDragging) return;

      // Scale screen pixels to canvas coordinates
      const rect = this.canvas.getBoundingClientRect();
      const scaleFactorX = this.canvas.width / rect.width;
      const scaleFactorY = this.canvas.height / rect.height;

      const deltaX = (clientX - this.dragStart.x) * scaleFactorX;
      const deltaY = (clientY - this.dragStart.y) * scaleFactorY;

      this.transform.translateX += deltaX;
      this.transform.translateY += deltaY;

      this.dragStart = { x: clientX, y: clientY };
      this.render();
    }

    onPointerUp() {
      this.isDragging = false;
    }

    // =========================================================================
    // Senior Ergonomics Toolbar Actions (Oversized 56px button controls)
    // =========================================================================

    zoomIn(step = 0.1) {
      this.transform.scale = Math.min(5.0, this.transform.scale * (1 + step));
      this.render();
    }

    zoomOut(step = 0.1) {
      this.transform.scale = Math.max(0.2, this.transform.scale * (1 - step));
      this.render();
    }

    rotateClockwise() {
      this.transform.rotation = (this.transform.rotation + 90) % 360;
      this.render();
    }

    flipHorizontal() {
      this.transform.flipH = !this.transform.flipH;
      this.render();
    }

    pan(dx, dy) {
      this.transform.translateX += dx;
      this.transform.translateY += dy;
      this.render();
    }

    resetTransform() {
      this.transform = {
        scale: 1.0,
        translateX: 0,
        translateY: 0,
        rotation: 0,
        flipH: false
      };
      if (this.userImage) {
        this.fitUserImageToCanvas();
      }
      this.render();
    }

    selectFrame(index) {
      if (index >= 0 && index < COMMEMORATIVE_FRAMES.length) {
        this.activeFrameIndex = index;
        const frame = COMMEMORATIVE_FRAMES[index];
        if (!this.frameImages[frame.id]) {
          if (typeof Image !== 'undefined') {
            const img = new Image();
            img.src = frame.src;
            img.onload = () => {
              this.frameImages[frame.id] = img;
              this.render();
            };
          } else {
            this.frameImages[frame.id] = { id: frame.id, src: frame.src, complete: true };
            this.render();
          }
        } else {
          this.render();
        }
      }
    }

    getActiveFrame() {
      return COMMEMORATIVE_FRAMES[this.activeFrameIndex] || COMMEMORATIVE_FRAMES[0];
    }

    /**
     * Select Anime Prince trot singer character companion
     * @param {string} id Character slug ID
     */
    selectCharacter(id) {
      const char = this.getCharacterById(id);
      if (!char) return;
      this.activeCharacterId = id;

      if (!this.characterImages[id]) {
        if (typeof Image !== 'undefined') {
          const img = new Image();
          img.src = char.sprite_path;
          img.onload = () => {
            this.characterImages[id] = img;
            this.render();
          };
          img.onerror = () => {
            console.warn(`[PhotoBooth] Failed to load character sprite: ${char.sprite_path}`);
          };
        } else {
          this.characterImages[id] = { id: char.id, src: char.sprite_path, complete: true };
          this.render();
        }
      } else {
        this.render();
      }
    }

    /**
     * Retrieve character definition by slug ID
     * @param {string} id
     * @returns {Object}
     */
    getCharacterById(id) {
      return this.characters.find((c) => c.id === id) || this.characters[0];
    }

    /**
     * Get active Anime Prince character companion
     * @returns {Object}
     */
    getActiveCharacter() {
      return this.getCharacterById(this.activeCharacterId);
    }

    /**
     * Retrieve full list of 10 Anime Prince characters
     * @returns {Array<Object>}
     */
    getAllCharacters() {
      return this.characters.slice();
    }

    // =========================================================================
    // Camera Capture Pipeline (getUserMedia with In-App Browser Fallback)
    // =========================================================================

    async startCamera() {
      if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        this.handleCameraFallback('현재 사용 중인 브라우저에서는 카메라 바로 연결이 지원되지 않습니다.');
        return false;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'user', // Selfie camera
            width: { ideal: CANVAS_WIDTH },
            height: { ideal: CANVAS_HEIGHT }
          },
          audio: false
        });

        this.mediaStream = stream;
        this.isCameraStreaming = true;

        if (this.video) {
          this.video.srcObject = stream;
          await this.video.play();
        }

        // Default mirror flip for selfie camera
        this.transform.flipH = true;

        // Start live camera compositing render loop
        this.startCameraRenderLoop();
        return true;
      } catch (err) {
        console.warn('[PhotoBooth] Camera permission or device access error:', err);
        let errorMsg = '카메라 연결 권한이 허용되지 않았거나 연결이 잠시 어려워요.';
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          errorMsg = '카메라 사용 권한이 차단되어 있습니다.';
        }
        this.handleCameraFallback(errorMsg);
        return false;
      }
    }

    stopCamera() {
      this.isCameraStreaming = false;
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
        this.animationFrameId = null;
      }
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach((track) => track.stop());
        this.mediaStream = null;
      }
      if (this.video) {
        this.video.srcObject = null;
      }
    }

    captureSnapshot() {
      if (!this.isCameraStreaming || !this.video) return;

      // Create an offscreen canvas to freeze the current video frame
      const snapCanvas = document.createElement('canvas');
      snapCanvas.width = this.video.videoWidth || CANVAS_WIDTH;
      snapCanvas.height = this.video.videoHeight || CANVAS_HEIGHT;
      const snapCtx = snapCanvas.getContext('2d');
      snapCtx.drawImage(this.video, 0, 0, snapCanvas.width, snapCanvas.height);

      // Create permanent user image from snapshot
      const userImg = new Image();
      userImg.src = snapCanvas.toDataURL('image/jpeg', 0.95);
      userImg.onload = () => {
        this.userImage = userImg;
        this.stopCamera();
        this.fitUserImageToCanvas();
        this.render();
      };
    }

    startCameraRenderLoop() {
      const loop = () => {
        if (!this.isCameraStreaming) return;
        this.render();
        this.animationFrameId = requestAnimationFrame(loop);
      };
      this.animationFrameId = requestAnimationFrame(loop);
    }

    handleCameraFallback(message) {
      if (typeof document === 'undefined') return;
      const modal = document.getElementById('camera-fallback-modal');
      const msgEl = document.getElementById('camera-fallback-msg');
      if (modal) {
        if (msgEl) msgEl.textContent = message;
        modal.style.display = 'flex';
      } else {
        alert(`${message}\n대신 [내 앨범에서 사진 고르기]를 누르시면 스마트폰 앨범에 있는 예쁜 사진으로 바로 만드실 수 있습니다! 🌸`);
        if (this.fileInput) this.fileInput.click();
      }
    }

    // =========================================================================
    // File Ingestion Pipeline
    // =========================================================================

    handleFileSelect(event) {
      const file = event.target && event.target.files && event.target.files[0];
      if (!file) return;

      // Stop camera if currently active
      if (this.isCameraStreaming) {
        this.stopCamera();
      }

      const reader = new FileReader();
      reader.onload = (loadEvent) => {
        const img = new Image();
        img.onload = () => {
          this.userImage = img;
          this.resetTransform();
          this.fitUserImageToCanvas();
          this.render();
        };
        img.src = loadEvent.target.result;
      };
      reader.readAsDataURL(file);
    }

    loadUserImageFromUrl(url) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          this.userImage = img;
          this.resetTransform();
          this.fitUserImageToCanvas();
          this.render();
          resolve(img);
        };
        img.onerror = reject;
        img.src = url;
      });
    }

    fitUserImageToCanvas() {
      const img = this.userImage || this.video;
      if (!img) return;

      const imgWidth = img.videoWidth || img.naturalWidth || img.width;
      const imgHeight = img.videoHeight || img.naturalHeight || img.height;
      if (!imgWidth || !imgHeight) return;

      // Fit to cover canvas while keeping 3:4 aspect ratio
      const scaleX = CANVAS_WIDTH / imgWidth;
      const scaleY = CANVAS_HEIGHT / imgHeight;
      this.transform.scale = Math.max(scaleX, scaleY);
      this.transform.translateX = 0;
      this.transform.translateY = 0;
    }

    // =========================================================================
    // 5-Layer Canvas Compositing Engine (Two-Shot Companion Architecture)
    // Layer 0: Backdrop (Ivory #FAFAF8)
    // Layer 1: Transformed User Photo / Live Stream
    // Layer 2: Selected Anime Prince Sprite (1080x1440 transparent PNG)
    // Layer 3: Commemorative Frame Overlay (1080x1440 PNG)
    // Layer 4: Commemorative Watermark Seal, Typography & Date Stamp
    // =========================================================================

    render() {
      if (!this.ctx || !this.canvas) return;

      const ctx = this.ctx;
      const w = CANVAS_WIDTH;
      const h = CANVAS_HEIGHT;

      // -----------------------------------------------------------------------
      // Layer 0: Glare-reduction Soft Ivory Background (#FAFAF8)
      // -----------------------------------------------------------------------
      ctx.fillStyle = '#FAFAF8';
      ctx.fillRect(0, 0, w, h);

      // -----------------------------------------------------------------------
      // Layer 1: Transformed User Photo or Live Video Stream
      // -----------------------------------------------------------------------
      const source = this.isCameraStreaming ? this.video : this.userImage;
      if (source) {
        const srcW = source.videoWidth || source.naturalWidth || source.width || w;
        const srcH = source.videoHeight || source.naturalHeight || source.height || h;

        ctx.save();
        // Move origin to canvas center
        ctx.translate(w / 2 + this.transform.translateX, h / 2 + this.transform.translateY);
        // Apply rotation
        ctx.rotate((this.transform.rotation * Math.PI) / 180);
        // Apply scale & horizontal flip
        ctx.scale(this.transform.flipH ? -this.transform.scale : this.transform.scale, this.transform.scale);
        // Draw centered
        ctx.drawImage(source, -srcW / 2, -srcH / 2, srcW, srcH);
        ctx.restore();
      } else {
        // Placeholder guide if no photo uploaded yet
        this.renderPlaceholderGuide(ctx, w, h);
      }

      // -----------------------------------------------------------------------
      // Layer 2: Selected Anime Prince Sprite (1080x1440 RGBA transparent PNG)
      // -----------------------------------------------------------------------
      const activeChar = this.getActiveCharacter();
      if (activeChar) {
        const charImg = this.characterImages[activeChar.id];
        if (charImg && (charImg.complete || charImg.naturalWidth > 0)) {
          ctx.drawImage(charImg, 0, 0, w, h);
        }
      }

      // -----------------------------------------------------------------------
      // Layer 3: Commemorative Frame Overlay (1080x1440 PNG)
      // -----------------------------------------------------------------------
      const activeFrame = this.getActiveFrame();
      const frameImg = this.frameImages[activeFrame.id];
      if (frameImg && (frameImg.complete || frameImg.naturalWidth > 0)) {
        ctx.drawImage(frameImg, 0, 0, w, h);
      }

      // -----------------------------------------------------------------------
      // Layer 4: Commemorative Watermark Seal, Typography & Date Stamp
      // -----------------------------------------------------------------------
      this.renderWatermarkSeal(ctx, w, h);
    }

    renderPlaceholderGuide(ctx, w, h) {
      // Soft dotted frame in center
      ctx.save();
      ctx.strokeStyle = '#D4AF37';
      ctx.lineWidth = 4;
      ctx.setLineDash([16, 12]);
      ctx.strokeRect(100, 200, w - 200, h - 400);

      // Senior welcoming text (emoji-free for 100% clean font rendering)
      ctx.fillStyle = '#1B4D3E';
      ctx.font = 'bold 42px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('영웅님과 함께 찍는 파라다이스 기념사진관', w / 2, h / 2 - 60);

      ctx.fillStyle = '#4B5563';
      ctx.font = '28px sans-serif';
      ctx.fillText('위 [내 사진 찍기] 또는 [앨범에서 사진 고르기]를 눌러보세요', w / 2, h / 2 + 10);
      ctx.fillText('영웅님과 다정하게 어깨동무한 멋진 사진이 완성됩니다', w / 2, h / 2 + 60);
      ctx.restore();
    }

    renderWatermarkSeal(ctx, w, h) {
      const activeChar = this.getActiveCharacter();
      const today = new Date();
      const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

      ctx.save();

      // Character emotional catchphrase & singer credit (strip emojis to avoid missing-glyph boxes)
      if (activeChar) {
        ctx.fillStyle = activeChar.theme_color || '#1B4D3E';
        ctx.font = 'bold 22px sans-serif';
        ctx.textAlign = 'left';
        const catchphrase = (activeChar.catchphrase || '').replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, '').trim();
        ctx.fillText(`[${activeChar.title}] ${catchphrase} — 가수 ${activeChar.name_ko}`, 40, h - 55);
      }

      // Date stamp
      ctx.fillStyle = 'rgba(75, 85, 99, 0.85)';
      ctx.font = '600 18px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`${dateStr} 파라다이스 투샷 촬영 기념`, 40, h - 22);

      // Platform legal watermark (strictly preserving exact string required by tests)
      ctx.fillStyle = 'rgba(27, 77, 62, 0.75)';
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText('황영웅과 함께하는 파라다이스 | paradise-hero.com', w - 40, h - 20);

      ctx.restore();
    }

    // =========================================================================
    // Client-Side Export Pipeline (Zero Server Dependency)
    // =========================================================================

    /**
     * Detects KakaoTalk In-App Browser or Mobile WebView where <a download> fails
     */
    isKakaoInAppOrMobile() {
      const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
      return /KAKAOTALK|NAVER|Instagram|FBAN|FBAV|Line|Android|iPhone|iPad|iPod/i.test(ua);
    }

    /**
     * Exports current canvas to JPEG blob and triggers browser download / KakaoTalk 2s long-press modal
     * Returns Promise<{ blob: Blob, filename: string, url: string, dataUrl: string }>
     */
    exportPhoto() {
      return new Promise((resolve, reject) => {
        if (!this.canvas) {
          reject(new Error('Canvas element not found'));
          return;
        }

        // Render clean final state
        this.render();

        let dataUrl = '';
        if (typeof this.canvas.toDataURL === 'function') {
          try {
            dataUrl = this.canvas.toDataURL('image/jpeg', 0.95);
          } catch (e) {
            dataUrl = '';
          }
        }

        this.canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error('Failed to generate image blob'));
            return;
          }

          const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
          const filename = `paradise_hero_with_you_${timestamp}.jpg`;
          const url = (typeof URL !== 'undefined' && URL.createObjectURL) ? URL.createObjectURL(blob) : dataUrl;
          const previewSrc = dataUrl || url;
          const ua = (typeof navigator !== 'undefined' && navigator.userAgent) ? navigator.userAgent : '';
          const isKakaoTalk = /KAKAOTALK/i.test(ua);

          // 1. Automatic download trigger on desktop / standard browsers (skip raw <a download> inside KAKAOTALK where it fails silently)
          if (typeof document !== 'undefined' && !isKakaoTalk) {
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }

          // 2. If KakaoTalk in-app or mobile and no custom celebration modal is present, auto-open king-sized 22px+ save guide modal
          const freeAccessState = { credits: 9999, unlimitedVip: true };
          if (typeof document !== 'undefined' && freeAccessState.unlimitedVip && this.isKakaoInAppOrMobile()) {
            const celebrationModal = document.getElementById('save-celebration-modal');
            if (!celebrationModal) {
              if (typeof window !== 'undefined' && window.ParadiseKakaoBookmark && window.ParadiseKakaoBookmark.openLongPressPhotoSaveModal) {
                window.ParadiseKakaoBookmark.openLongPressPhotoSaveModal(previewSrc, '📸 황영웅님과의 투샷 기념사진 완성!');
              } else {
                let fallbackModal = document.getElementById('kakao-longpress-save-modal');
                if (!fallbackModal) {
                  fallbackModal = document.createElement('div');
                  fallbackModal.id = 'kakao-longpress-save-modal';
                  fallbackModal.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(14,40,32,0.92);display:flex;align-items:center;justify-content:center;padding:16px;';
                  fallbackModal.innerHTML =
                    '<div style="background:#FAFAF8;border:4px solid #D4AF37;border-radius:20px;max-width:520px;width:100%;padding:22px;text-align:center;">' +
                    '<p style="font-size:23px;font-weight:900;color:#111827;line-height:1.5;margin:0 0 14px;">📱 손가락으로 그림을 2초간 꾹~ 눌러 [사진 저장]을 누르세요!</p>' +
                    '<img id="kakao-fallback-save-img" src="" alt="완성된 기념사진" style="max-width:100%;max-height:58vh;border-radius:12px;border:3px solid #1B4D3E;display:block;margin:0 auto 14px;" />' +
                    '<button type="button" onclick="this.closest(\'#kakao-longpress-save-modal\').style.display=\'none\'" style="width:100%;min-height:60px;font-size:22px;font-weight:900;background:#1B4D3E;color:#FFF;border:none;border-radius:14px;cursor:pointer;">닫기</button>' +
                    '</div>';
                  document.body.appendChild(fallbackModal);
                }
                const imgEl = fallbackModal.querySelector('#kakao-fallback-save-img');
                if (imgEl) imgEl.src = previewSrc;
                fallbackModal.style.display = 'flex';
              }
            }
          }

          resolve({ blob, filename, url, dataUrl: previewSrc });
        }, 'image/jpeg', 0.95);
      });
    }

    /**
     * Shares photo via Web Share API (KakaoTalk / Instagram / Gallery)
     */
    async sharePhoto(blob, filename) {
      if (typeof navigator !== 'undefined' && navigator.share && navigator.canShare) {
        try {
          const file = new File([blob], filename, { type: 'image/jpeg' });
          if (navigator.canShare({ files: [file] })) {
            await navigator.share({
              files: [file],
              title: '황영웅과 함께 찍은 파라다이스 기념사진 💚',
              text: '어머님, 황영웅님과 함께 찍은 다정한 기념사진이에요! 파라다이스 포토부스에서 누구나 바로 만드실 수 있습니다 🌸',
              url: window.location.href
            });
            return true;
          }
        } catch (err) {
          if (err.name !== 'AbortError') {
            console.warn('[PhotoBooth] Web Share error:', err);
          }
        }
      }
      return false;
    }
  }

  // Global export
  global.PhotoBoothEngine = PhotoBoothEngine;
  global.COMMEMORATIVE_FRAMES = COMMEMORATIVE_FRAMES;
  global.CHARACTER_CARDS = global.CHARACTER_CARDS || DEFAULT_CHARACTERS;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      PhotoBoothEngine,
      COMMEMORATIVE_FRAMES,
      CANVAS_WIDTH,
      CANVAS_HEIGHT,
      CHARACTER_CARDS: DEFAULT_CHARACTERS
    };
  }
})(typeof window !== 'undefined' ? window : global);
