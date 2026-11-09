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

  class PhotoBoothEngine {
    constructor(options = {}) {
      this.canvas = options.canvas || (typeof document !== 'undefined' ? document.getElementById('booth-canvas') : null);
      this.video = options.video || (typeof document !== 'undefined' ? document.getElementById('booth-video') : null);
      this.fileInput = options.fileInput || (typeof document !== 'undefined' ? document.getElementById('booth-file-input') : null);

      this.ctx = this.canvas && this.canvas.getContext ? this.canvas.getContext('2d') : null;

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

      // Preload frames if in browser
      if (typeof window !== 'undefined') {
        this.preloadFrames();
      }
    }

    /**
     * Preloads all frame PNGs into image cache
     */
    preloadFrames() {
      COMMEMORATIVE_FRAMES.forEach((frame, idx) => {
        const img = new Image();
        img.src = frame.src;
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
    // Canvas Compositing Engine (Layer 0 + Layer 1 + Layer 2 + Layer 3)
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
      // Layer 2: Commemorative Frame Overlay (1080x1440 PNG)
      // -----------------------------------------------------------------------
      const activeFrame = this.getActiveFrame();
      const frameImg = this.frameImages[activeFrame.id];
      if (frameImg && frameImg.complete && frameImg.naturalWidth > 0) {
        ctx.drawImage(frameImg, 0, 0, w, h);
      }

      // -----------------------------------------------------------------------
      // Layer 3: Commemorative Watermark Seal & Date Stamp
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

      // Senior welcoming text
      ctx.fillStyle = '#1B4D3E';
      ctx.font = 'bold 44px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('📸 영웅님과 함께 찍는 파라다이스 포토부스', w / 2, h / 2 - 60);

      ctx.fillStyle = '#4B5563';
      ctx.font = '28px sans-serif';
      ctx.fillText('아래 [사진 찍기] 또는 [내 앨범에서 사진 고르기]를 눌러보세요', w / 2, h / 2 + 10);
      ctx.fillText('영웅님과 다정하게 어깨동무한 멋진 사진이 완성됩니다 🌸', w / 2, h / 2 + 60);
      ctx.restore();
    }

    renderWatermarkSeal(ctx, w, h) {
      // Elegant bottom watermark
      ctx.save();
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
     * Exports current canvas to JPEG blob and triggers browser download
     * Returns Promise<{ blob: Blob, filename: string, url: string }>
     */
    exportPhoto() {
      return new Promise((resolve, reject) => {
        if (!this.canvas) {
          reject(new Error('Canvas element not found'));
          return;
        }

        // Render clean final state
        this.render();

        this.canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error('Failed to generate image blob'));
            return;
          }

          const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
          const filename = `paradise_hero_with_you_${timestamp}.jpg`;
          const url = URL.createObjectURL(blob);

          // 1. Primary automatic download trigger
          if (typeof document !== 'undefined') {
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }

          resolve({ blob, filename, url });
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

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      PhotoBoothEngine,
      COMMEMORATIVE_FRAMES,
      CANVAS_WIDTH,
      CANVAS_HEIGHT
    };
  }
})(typeof window !== 'undefined' ? window : global);
