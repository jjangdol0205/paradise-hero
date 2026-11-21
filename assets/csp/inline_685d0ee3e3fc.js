function setFontSize(sz, btn) {
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    function shareSeniorLetter() {
      var msg = "📻 화·금 저녁 6시 김쌤의영웅라디오 100% 즐기는 법과 눈·목 편안한 청취 건강 수칙입니다.\n👉 큰 글씨로 바로 읽기: https://paradise-hero.com/columns/senior-radio-concert-wellness-guide.html";
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
