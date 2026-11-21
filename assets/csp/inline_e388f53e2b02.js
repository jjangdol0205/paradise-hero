function setFontSize(sz, btn) {
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    function shareSeniorLetter() {
      var msg = "🌸 자식 키우느라 잊고 산 봄날을 다시 불러드리는 백운호 대표곡 〈어머니의 봄날〉 가사 해설 편지입니다.\n👉 큰 글씨로 바로 읽기: https://paradise-hero.com/columns/mothers-spring-day-lyric-story.html";
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
