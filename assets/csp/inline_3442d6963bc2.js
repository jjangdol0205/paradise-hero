function setFontSize(sz, btn) {
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    function shareSeniorLetter() {
      var msg = "💚 세월의 강을 건너온 우리 어머님·아버지를 위해 탄생한 가상 트로트 가수 『백운호』 이야기입니다.\n👉 큰 글씨로 바로 읽기: https://paradise-hero.com/columns/baek-woon-ho-debut-story.html";
      if (navigator.share) {
        navigator.share({ title: document.title, text: msg, url: location.href }).catch(function(){});
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(msg).then(function() {
          document.getElementById('share-toast').style.display = 'block';
        });
      }
    }
