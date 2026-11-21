function setFontSize(sz, btn) {
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    function shareSeniorLetter() {
      var msg = "🌺 찬 서리 견뎌내고 활짝 피어나는 백운호 신곡 〈다시 피는 동백꽃〉, 인생 후반전 응원 편지입니다.\n👉 큰 글씨로 바로 읽기: https://paradise-hero.com/columns/blooming-camellia-again-hope.html";
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
