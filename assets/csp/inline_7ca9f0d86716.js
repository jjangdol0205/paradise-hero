(function(){
        window.__dcStampMorningLetter = window.__dcStampMorningLetter || function(div, key, donePrefix, unit, beaconPrefix) {
          try {
            var today = new Date().toISOString().slice(0, 10);
            var raw = JSON.parse(localStorage.getItem(key) || '{}');
            if (raw.lastDate !== today) {
              var yest = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
              raw.streak = (raw.lastDate === yest) ? ((raw.streak || 0) + 1) : 1;
              raw.lastDate = today;
              localStorage.setItem(key, JSON.stringify(raw));
              if (typeof fetch === 'function' && !navigator.webdriver) {
                if (window.hitHeroBeacon) { window.hitHeroBeacon(beaconPrefix); }
              }
            }
            var btn = document.getElementById('fandom-stamp-btn-' + div.toLowerCase());
            if (btn) {
              btn.textContent = donePrefix + ' ' + (raw.streak || 1) + ' ' + unit;
            }
          } catch (e) {}
        };
        try {
          var saved = JSON.parse(localStorage.getItem('dc_fandom_letter_streak_hero') || '{}');
          var todayInit = new Date().toISOString().slice(0, 10);
          if (saved.lastDate === todayInit && saved.streak) {
            var b = document.getElementById('fandom-stamp-btn-hero');
            if (b) b.textContent = '🌺 오늘 사랑방 출석 완료! 연속 동행 기록: ' + saved.streak + ' 일째';
          }
        } catch (e) {}
      })();
