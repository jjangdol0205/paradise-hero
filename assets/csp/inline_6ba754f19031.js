document.addEventListener('DOMContentLoaded', function () {
      const canvas = document.getElementById('booth-canvas');
      const video = document.getElementById('booth-video');
      const fileInput = document.getElementById('booth-file-input');
      const engine = new PhotoBoothEngine({ canvas, video, fileInput });
      engine.init();
      window.photoBoothEngine = engine;

      const charBtns = document.querySelectorAll('.character-select-btn');
      charBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          charBtns.forEach(function (b) { b.classList.remove('active'); b.setAttribute('aria-checked', 'false'); });
          btn.classList.add('active');
          btn.setAttribute('aria-checked', 'true');
          engine.selectCharacter(btn.getAttribute('data-character-id'));
        });
      });

      const btnCamera = document.getElementById('btn-camera');
      const btnCameraText = document.getElementById('btn-camera-text');
      btnCamera.addEventListener('click', async function () {
        if (!engine.isCameraStreaming) {
          const started = await engine.startCamera();
          if (started) {
            btnCameraText.textContent = '📸 찰칵! 셔터 누르기';
            btnCamera.style.background = 'linear-gradient(135deg, #DC2626 0%, #991B1B 100%)';
          }
        } else {
          engine.captureSnapshot();
          btnCameraText.textContent = '내 사진 다시 찍기 (카메라)';
          btnCamera.style.background = '';
        }
      });

      document.getElementById('btn-album').addEventListener('click', function () { fileInput.click(); });

      const frameBtns = document.querySelectorAll('.frame-select-btn');
      frameBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          frameBtns.forEach(function (b) { b.classList.remove('active'); b.setAttribute('aria-checked', 'false'); });
          btn.classList.add('active');
          btn.setAttribute('aria-checked', 'true');
          engine.selectFrame(parseInt(btn.getAttribute('data-frame-index'), 10));
        });
      });

      document.getElementById('btn-zoom-in').addEventListener('click', function () { engine.zoomIn(0.1); });
      document.getElementById('btn-zoom-out').addEventListener('click', function () { engine.zoomOut(0.1); });
      document.getElementById('btn-flip').addEventListener('click', function () { engine.flipHorizontal(); });
      document.getElementById('btn-rotate').addEventListener('click', function () { engine.rotateClockwise(); });
      document.getElementById('btn-pan-up').addEventListener('click', function () { engine.pan(0, -30); });
      document.getElementById('btn-pan-down').addEventListener('click', function () { engine.pan(0, 30); });
      document.getElementById('btn-pan-left').addEventListener('click', function () { engine.pan(-30, 0); });
      document.getElementById('btn-pan-right').addEventListener('click', function () { engine.pan(30, 0); });
      document.getElementById('btn-reset').addEventListener('click', function () { engine.resetTransform(); });

      let lastExportedBlob = null;
      let lastExportedFilename = '';
      const celebModal = document.getElementById('save-celebration-modal');
      const modalPreviewImg = document.getElementById('modal-preview-img');

      document.getElementById('btn-save-photo').addEventListener('click', async function () {
        try {
          const result = await engine.exportPhoto();
          lastExportedBlob = result.blob;
          lastExportedFilename = result.filename;
          modalPreviewImg.src = result.dataUrl || result.url;
          celebModal.style.display = 'flex';
        } catch (err) {
          alert('사진 저장 중 오류가 발생했습니다. 다시 시도해 주세요.');
        }
      });

      const triggerShare = async function () {
        if (!lastExportedBlob) {
          try {
            const result = await engine.exportPhoto();
            lastExportedBlob = result.blob;
            lastExportedFilename = result.filename;
            modalPreviewImg.src = result.dataUrl || result.url;
          } catch (e) { return; }
        }
        const shared = await engine.sharePhoto(lastExportedBlob, lastExportedFilename);
        if (!shared) celebModal.style.display = 'flex';
      };

      document.getElementById('btn-share-photo').addEventListener('click', triggerShare);
      document.getElementById('btn-modal-share').addEventListener('click', triggerShare);
      document.getElementById('btn-modal-close').addEventListener('click', function () { celebModal.style.display = 'none'; });

      const camModal = document.getElementById('camera-fallback-modal');
      document.getElementById('btn-fallback-album').addEventListener('click', function () { camModal.style.display = 'none'; fileInput.click(); });
      document.getElementById('btn-fallback-close').addEventListener('click', function () { camModal.style.display = 'none'; });
    });
