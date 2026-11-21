function setFontSize(sz, btn) {
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    function shareSeniorLetter() {
      var msg = "🍂 호숫가 물안개처럼 저녁 산책길과 쉼터를 적시는 〈백운호 연가〉 스튜디오 녹음 편지입니다.\n👉 큰 글씨로 바로 읽기: https://paradise-hero.com/columns/baek-woon-ho-yeonga-radio-note.html";
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
