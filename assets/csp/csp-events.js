/* Strict CSP Event Dispatcher (Compile-Time Static Allowlist, Zero eval) */
(function () {
  if (window.__CSP_EVENTS_READY__) return;
  window.__CSP_EVENTS_READY__ = true;
  var STATIC = {
    "click": {
      "h_08b6e8fbd6cb": function (event) {
setFontSize('26px', this)
      },
      "h_09848cee9c78": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.printLyricGuide()
      },
      "h_09f9d7d5b9f4": function (event) {
document.documentElement.style.setProperty('--base-font','22px')
      },
      "h_1b919b9d5bce": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadFanQuizCert()
      },
      "h_1e17f42f3e62": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadWallpaper()
      },
      "h_2211829df45a": function (event) {
setFontSize('30px', this)
      },
      "h_22bbd6d66900": function (event) {
shareSeniorLetter()
      },
      "h_427d8e388bdd": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadWishLantern()
      },
      "h_4d8865c6b9e9": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadFortuneTalisman()
      },
      "h_6372a5def7ec": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadGreetingCard()
      },
      "h_682f985131c7": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadFanIdCard()
      },
      "h_6b7c36502c7a": function (event) {
window.ParadiseStoryHub && window.ParadiseStoryHub.switchTab('browse')
      },
      "h_7d3d925d83c9": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadGoldenTicket()
      },
      "h_8092c3fd1222": function (event) {
window.__dcStampMorningLetter('HERO', 'dc_fandom_letter_streak_hero', '🌺 오늘 사랑방 출석 완료! 연속 동행 기록:', '일째', 'fandom_stamp_hero')
      },
      "h_a97451975e10": function (event) {
document.documentElement.style.setProperty('--base-font','30px')
      },
      "h_d0e1b85321d4": function (event) {
document.documentElement.style.setProperty('--base-font','26px')
      },
      "h_d4a2c996318b": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.playVoiceLetterAloud()
      },
      "h_f09aeffbd1aa": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.downloadFlowerTribute()
      },
      "h_f8f169c87499": function (event) {
setFontSize('22px', this)
      },
      "h_fa3b1eaaff0d": function (event) {
window.VIPDigitalStudio && window.VIPDigitalStudio.shareGreetingCard()
      }
    },
    "submit": {
    },
    "input": {
    },
    "change": {
    },
    "keydown": {
    },
    "keyup": {
    },
    "error": {
    },
    "focus": {
    },
    "blur": {
    }
  };

  var CLICK_ACTIONS = {
    "dc-share-site": function (el) {
      var div = (el && el.getAttribute("data-share-div")) || "TOM";
      var mode = String((el && el.getAttribute("data-share-mode")) || "native_or_copy").toLowerCase();
      var rawUrl = (el && el.getAttribute("data-share-url")) || (window.location ? window.location.origin + window.location.pathname : "");
      var url = (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.buildReferralShareUrl === "function")
        ? window.DreamCompanyCRM.buildReferralShareUrl(rawUrl)
        : rawUrl;
      var title = (el && el.getAttribute("data-share-title")) || document.title || "";
      var text = (el && el.getAttribute("data-share-text")) || title;
      var ownVid = (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.getOrCreateVisitorProfile === "function")
        ? window.DreamCompanyCRM.getOrCreateVisitorProfile().visitor_id
        : "";
      if (window.DreamCompanyCRM && typeof window.DreamCompanyCRM.trackFunnelEvent === "function") {
        try { window.DreamCompanyCRM.trackFunnelEvent(div, "share_click", { ref_code: ownVid, event_meta: mode }); } catch (_) {}
      }
      function flashLabel(msg) {
        if (!el) return;
        var orig = el.getAttribute("data-orig-label") || el.textContent;
        el.setAttribute("data-orig-label", orig);
        el.textContent = msg;
        setTimeout(function () { el.textContent = orig; }, 2200);
      }
      function copyUrl(doneMsg) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () { flashLabel(doneMsg); }).catch(function () {
            try {
              var ta = document.createElement("textarea");
              ta.value = url;
              ta.setAttribute("readonly", "");
              ta.style.position = "fixed";
              ta.style.opacity = "0";
              document.body.appendChild(ta);
              ta.select();
              document.execCommand("copy");
              document.body.removeChild(ta);
              flashLabel(doneMsg);
            } catch (_) {}
          });
        } else {
          try {
            var ta2 = document.createElement("textarea");
            ta2.value = url;
            ta2.setAttribute("readonly", "");
            ta2.style.position = "fixed";
            ta2.style.opacity = "0";
            document.body.appendChild(ta2);
            ta2.select();
            document.execCommand("copy");
            document.body.removeChild(ta2);
            flashLabel(doneMsg);
          } catch (_) {}
        }
      }
      var copiedDefault = div === "GBA"
        ? "\u30ea\u30f3\u30af\u3092\u30b3\u30d4\u30fc\u3057\u307e\u3057\u305f \u2713"
        : ((div === "KFK" || div === "HERO")
          ? "\ub9c1\ud06c\uac00 \ubcf5\uc0ac\ub418\uc5c8\uc2b5\ub2c8\ub2e4 \u2713"
          : "Link Copied \u2014 Ready to Share \u2713");
      if (mode === "line") {
        var lineUrl = "https://social-plugins.line.me/lineit/share?url=" + encodeURIComponent(url);
        window.open(lineUrl, "_blank", "noopener,noreferrer");
        return;
      }
      if (mode === "whatsapp") {
        var waUrl = "https://wa.me/?text=" + encodeURIComponent((text ? text + " " : "") + url);
        window.open(waUrl, "_blank", "noopener,noreferrer");
        return;
      }
      if (mode === "sms") {
        var body = encodeURIComponent((text ? text + " " : "") + url);
        var isIos = /iPad|iPhone|iPod/i.test((navigator && navigator.userAgent) || "");
        var smsHref = isIos ? ("sms:&body=" + body) : ("sms:?body=" + body);
        copyUrl("SMS Ready \u2713");
        try { window.location.href = smsHref; } catch (_) {}
        return;
      }
      if (mode === "copy") {
        copyUrl(copiedDefault);
        return;
      }
      if (mode === "kakao") {
        if (navigator.share) {
          navigator.share({ title: title, text: text, url: url }).catch(function () {
            copyUrl("\uce74\ud1a1 \uacf5\uc720 \ub9c1\ud06c \ubcf5\uc0ac\ub428 \u2713");
          });
          return;
        }
        copyUrl("\uce74\ud1a1 \uacf5\uc720 \ub9c1\ud06c \ubcf5\uc0ac\ub428 \u2713");
        return;
      }
      if (navigator.share) {
        navigator.share({ title: title, text: text, url: url }).catch(function () {});
        return;
      }
      copyUrl(copiedDefault);
    },
    "kfk-open-latpeed": function (el) {
      var tier = (el && el.getAttribute("data-csp-arg")) || "tier1";
      var isNativeAnchor = Boolean(el && el.tagName === "A" && el.getAttribute("href"));
      if (window.KfkAtelierApp && window.KfkAtelierApp.openKfkLatpeedCheckout) {
        window.KfkAtelierApp.openKfkLatpeedCheckout(tier, { skipWindowOpen: isNativeAnchor });
      } else if (window.openKfkLatpeedCheckout) {
        window.openKfkLatpeedCheckout(tier, { skipWindowOpen: isNativeAnchor });
      }
    },
    "gba-whop-tab": function (el) {
      var plan = (el && el.getAttribute("data-csp-arg")) || "monthly";
      if (window.selectGbaWhopPlan) window.selectGbaWhopPlan(plan);
    },
    "remove-parent": function (el) {
      if (el && el.parentNode) el.parentNode.remove();
    },
    "window-print": function () {
      window.print();
    },
    "tom-open-license": function () {
      var b = document.getElementById("btnOpenLicense");
      if (b) { b.click(); }
      else { var m = document.getElementById("licenseModal"); if (m) m.style.display = "flex"; }
    },
    "kfk-reopen-email": function () {
      if (window.KfkAtelierApp && window.KfkAtelierApp.reopenEmailSaveForm) window.KfkAtelierApp.reopenEmailSaveForm();
    },
    "kfk-download-album-pdf": function () {
      if (window.KfkAtelierApp && window.KfkAtelierApp.downloadRealGraduationAlbumPdf) window.KfkAtelierApp.downloadRealGraduationAlbumPdf();
    },
    "kfk-select-inapp-seg": function (el) {
      if (window.selectKidsFitInAppSeg) window.selectKidsFitInAppSeg(el.getAttribute("data-csp-arg") || "");
    },
    "kfg-switch-sibling": function (el) {
      if (window.switchKfgSibling) window.switchKfgSibling(Number(el.getAttribute("data-csp-arg") || 0));
    },
    "kfg-add-sibling": function () {
      if (window.addKfgSiblingProfile) window.addKfgSiblingProfile();
    },
    "kfg-reopen-email": function () {
      if (window.reopenAtelierEmailSaveForm) window.reopenAtelierEmailSaveForm();
    },
    "kfg-open-member-modal": function (el) {
      if (window.openKfgMemberModal) window.openKfgMemberModal(el.getAttribute("data-csp-arg") || "checkin");
    },
    "kfg-start-polar": function (el, ev) {
      if (ev) ev.preventDefault();
      if (window.startAtelierPolarCheckout) window.startAtelierPolarCheckout(el.getAttribute("data-csp-arg") || "pass");
    },
    "kfg-dl-custom-pdf": function () {
      if (window.downloadCustomAtelierPdf) window.downloadCustomAtelierPdf();
    },
    "kfg-dl-guide-pdf": function () {
      if (window.downloadProtectedKfgGuidePdf) window.downloadProtectedKfgGuidePdf();
    },
    "kfg-begin-atelier": function () {
      if (window.beginAtelier) window.beginAtelier();
    },
    "kfg-wl-close": function () {
      if (window.closeKfgVipWaitlistModal) window.closeKfgVipWaitlistModal();
    },
    "kfg-wl-select": function (el) {
      if (window.selectKfgWaitlistPlan) window.selectKfgWaitlistPlan(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-wl-verify": function () {
      if (window.verifyExistingVipLicenseInModal) window.verifyExistingVipLicenseInModal();
    },
    "kfg-velocity-checkout-pass": function () {
      if (window.triggerKfgVelocityEdgeCheckout) window.triggerKfgVelocityEdgeCheckout("pass");
      else if (window.openKfgVipWaitlistModal) window.openKfgVipWaitlistModal("sixMonth");
    },
    "kfg-velocity-checkout": function (el) {
      if (window.triggerKfgVelocityEdgeCheckout) window.triggerKfgVelocityEdgeCheckout(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-unlock-checkin-code": function () {
      if (window.unlockVipCheckinWithCode) window.unlockVipCheckinWithCode();
    },
    "kfg-dl-grad-album": function (el) {
      if (window.KfgPersonalizedPdf && window.KfgPersonalizedPdf.downloadGraduationAlbumPdf) {
        window.KfgPersonalizedPdf.downloadGraduationAlbumPdf(
          el.getAttribute("data-csp-arg") || "Your Child",
          Number(el.getAttribute("data-csp-arg2") || 0),
          Number(el.getAttribute("data-csp-arg3") || 0)
        );
      }
    },
    "kfg-sample-page": function (el) {
      if (window.switchSamplePreviewPage) window.switchSamplePreviewPage(Number(el.getAttribute("data-csp-arg") || 1));
    },
    "kfg-sample-step": function (el) {
      var ind = document.getElementById("sample-active-page-num");
      var cur = parseInt(ind ? ind.textContent : "1", 10) || 1;
      var delta = Number(el.getAttribute("data-csp-arg") || 1);
      if (window.switchSamplePreviewPage) window.switchSamplePreviewPage(cur + delta);
    },
    "kfg-close-sample-open-checkout": function (el) {
      var m = document.getElementById("kidsfit-sample-demo-modal");
      if (m) m.remove();
      if (window.openKidsFitGlobalCheckoutModal) window.openKidsFitGlobalCheckoutModal(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-load-sample": function () {
      if (window.loadSampleDemoProfile) window.loadSampleDemoProfile();
    },
    "kfg-auth-open-admin": function () {
      var m = document.getElementById("kidsfit-auth-modal");
      if (m) m.remove();
      if (window.KidsFitAdminStudio && window.KidsFitAdminStudio.openAdminModal) window.KidsFitAdminStudio.openAdminModal();
    },
    "kfg-verify-member-order": function (el) {
      if (window.verifyKidsFitMemberOrder) window.verifyKidsFitMemberOrder(el.getAttribute("data-csp-arg") || "");
    },
    "kfg-sign-out": function () {
      if (window.signOutKidsFitAccount) window.signOutKidsFitAccount();
    },
    "kfg-submit-auth": function (el) {
      if (window.submitKidsFitAuth) window.submitKidsFitAuth(el.getAttribute("data-csp-arg") || "signup");
    },
    "kfg-global-print": function () {
      if (window.triggerKidsFitGlobalPrint) window.triggerKidsFitGlobalPrint();
      else window.print();
    },
    "kfg-launch-polar": function (el) {
      if (window.launchPolarCheckout) window.launchPolarCheckout(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-launch-polar-prevent": function (el, ev) {
      if (ev) ev.preventDefault();
      if (window.launchPolarCheckout) window.launchPolarCheckout(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-launch-polar-selected": function () {
      if (window.launchPolarCheckout) window.launchPolarCheckout(window.__kfgSelectedPaywallPlan || "single");
    },
    "kfg-print-chrono": function () {
      if (window.printChrononutritionShoppingList) window.printChrononutritionShoppingList();
    },
    "kfg-posture-timer": function (el) {
      if (window.startGlobalPostureTimer) {
        window.startGlobalPostureTimer(Number(el.getAttribute("data-csp-arg") || 30), el.getAttribute("data-csp-arg2") || "");
      }
    },
    "kfg-select-care-month": function (el) {
      if (window.selectKidsFitCareMonth) {
        window.selectKidsFitCareMonth(el.getAttribute("data-csp-arg") || "growth", Number(el.getAttribute("data-csp-arg2") || 1));
      }
    },
    "kfg-open-checkout-modal": function () {
      if (window.openKidsFitGlobalCheckoutModal) window.openKidsFitGlobalCheckoutModal();
    },
    "kfg-open-sample-preview": function () {
      if (window.openSampleReportPreview) window.openSampleReportPreview();
      else if (window.loadSampleDemoProfile) window.loadSampleDemoProfile();
    },
    "kfg-recalc-monthly": function (el) {
      if (!window.recalculateKidsFitMonthlyProgress) return;
      var kind = el.getAttribute("data-csp-arg") || "growth";
      var a2 = Number(el.getAttribute("data-csp-arg2") || 0);
      var a3Raw = el.getAttribute("data-csp-arg3");
      if (a3Raw !== null && a3Raw !== "") {
        window.recalculateKidsFitMonthlyProgress(kind, a2, Number(a3Raw));
      } else {
        window.recalculateKidsFitMonthlyProgress(kind, a2);
      }
    },
    "kfg-close-sample-preview": function () {
      if (window.closeSampleReportPreview) window.closeSampleReportPreview();
    },
    "kfg-sample-start-wizard": function () {
      if (window.closeSampleReportPreview) window.closeSampleReportPreview();
      if (window.KidsFitOnboardingWizard && window.KidsFitOnboardingWizard.openWizard) {
        window.KidsFitOnboardingWizard.openWizard();
      } else {
        var f = document.getElementById("diagnosis-form");
        if (f) f.scrollIntoView({ behavior: "smooth" });
      }
    },
    "kfg-print-doc": function (el) {
      if (window.printKidsFitDocument) window.printKidsFitDocument(el.getAttribute("data-csp-arg") || "doctor-dossier");
    },
    "kfg-scroll-highlight": function (el) {
      var id = el.getAttribute("data-csp-arg") || "";
      var t = id ? document.getElementById(id) : null;
      if (t) {
        t.scrollIntoView({ behavior: "smooth", block: "center" });
        t.style.boxShadow = "0 0 0 4px rgba(37,99,235,0.35)";
        setTimeout(function () { t.style.boxShadow = "none"; }, 2500);
      }
    },
    "kfg-copy-magic-link": function () {
      if (window.copyKidsFitMagicUnlockLink) window.copyKidsFitMagicUnlockLink();
    },
    "kfg-dl-vip-res": function (el) {
      if (window.downloadKidsFitVipResource) window.downloadKidsFitVipResource(el.getAttribute("data-csp-arg") || "all_vip_pack");
    },
    "kfg-sibling-slot": function (el) {
      if (window.saveOrSwitchKidsFitSiblingSlot) window.saveOrSwitchKidsFitSiblingSlot(Number(el.getAttribute("data-csp-arg") || 1));
    },
    "kfg-share-report": function (el) {
      if (window.shareKidsFitGlobalReport) window.shareKidsFitGlobalReport(el.getAttribute("data-csp-arg") || "native");
    },
    "kfg-select-global-plan": function (el) {
      if (window.selectKidsFitGlobalPlan) window.selectKidsFitGlobalPlan(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-restore-inline": function () {
      if (window.restoreKidsFitInlineAccess) window.restoreKidsFitInlineAccess();
    },
    "kfg-switch-modal-plan": function (el) {
      if (window.switchModalPlan) window.switchModalPlan(el.getAttribute("data-csp-arg") || "single");
    },
    "kfg-complete-checkout": function () {
      if (window.completeKidsFitGlobalCheckout) window.completeKidsFitGlobalCheckout();
    }
  };

  var SUBMIT_ACTIONS = {
    "kfk-submit-inapp-email": function (el, ev) {
      if (window.submitKidsFitInAppWorkbookEmail) return window.submitKidsFitInAppWorkbookEmail(ev);
      return false;
    },
    "kfg-wl-submit": function (el, ev) {
      if (window.submitKfgVipWaitlistForm) return window.submitKfgVipWaitlistForm(ev);
      return false;
    }
  };

  var CHANGE_ACTIONS = {
    "kfg-whatif-update": function () {
      if (window.updateKidsFitWhatIfSimulator) window.updateKidsFitWhatIfSimulator();
    },
    "kfg-clinic-q": function (el) {
      if (window.toggleClinicChecklistQuestion) window.toggleClinicChecklistQuestion(Number(el.getAttribute("data-csp-arg") || 1));
    }
  };

  var INPUT_ACTIONS = {
    "kfg-hormone-update": function () {
      if (window.updateGlobalHormoneSimulator) window.updateGlobalHormoneSimulator();
    }
  };

  var KEYDOWN_ACTIONS = {
    "kfg-auth-enter-signup": function (el, ev) {
      if (ev && ev.key === "Enter") {
        ev.preventDefault();
        if (window.submitKidsFitAuth) window.submitKidsFitAuth("signup");
      }
    }
  };

  function runBubbled(event, attrStatic, staticMap, attrAct, actMap, checkRemoveHide) {
    var stopped = false;
    var origStop = event.stopPropagation;
    try {
      event.stopPropagation = function () {
        stopped = true;
        if (origStop) return origStop.call(event);
      };
    } catch (_) {}

    var node = event.target;
    while (node && node.nodeType === 1 && !stopped) {
      var sid = node.getAttribute(attrStatic);
      if (sid && staticMap && Object.prototype.hasOwnProperty.call(staticMap, sid)) {
        var r1 = staticMap[sid].call(node, event);
        if (r1 === false) event.preventDefault();
      }
      if (stopped) break;
      if (attrAct && actMap) {
        var act = node.getAttribute(attrAct);
        if (act && Object.prototype.hasOwnProperty.call(actMap, act)) {
          var r2 = actMap[act].call(node, node, event);
          if (r2 === false) event.preventDefault();
        }
      }
      if (stopped) break;
      if (checkRemoveHide) {
        var remId = node.getAttribute("data-csp-remove");
        if (remId) {
          var remEl = document.getElementById(remId);
          if (remEl) remEl.remove();
        }
        var hideSel = node.getAttribute("data-csp-hide");
        if (hideSel) {
          var target = (hideSel.charAt(0) === "#" ? document.getElementById(hideSel.slice(1)) : null) || (node.closest ? node.closest(hideSel) : null);
          if (target) target.style.display = "none";
        }
      }
      node = node.parentElement;
    }
  }

  document.addEventListener("click", function (event) {
    runBubbled(event, "data-csp-click", STATIC.click, "data-csp-act", CLICK_ACTIONS, true);
  });

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (!form || form.nodeType !== 1) return;
    var sid = form.getAttribute("data-csp-submit");
    if (sid && STATIC.submit && Object.prototype.hasOwnProperty.call(STATIC.submit, sid)) {
      var r1 = STATIC.submit[sid].call(form, event);
      if (r1 === false) event.preventDefault();
    }
    var act = form.getAttribute("data-csp-submit-act");
    if (act && Object.prototype.hasOwnProperty.call(SUBMIT_ACTIONS, act)) {
      var r2 = SUBMIT_ACTIONS[act].call(form, form, event);
      if (r2 === false) event.preventDefault();
    }
  });

  document.addEventListener("input", function (event) {
    runBubbled(event, "data-csp-input", STATIC.input, "data-csp-input-act", INPUT_ACTIONS, false);
  });

  document.addEventListener("change", function (event) {
    runBubbled(event, "data-csp-change", STATIC.change, "data-csp-change-act", CHANGE_ACTIONS, false);
  });

  document.addEventListener("keydown", function (event) {
    runBubbled(event, "data-csp-keydown", STATIC.keydown, "data-csp-keydown-act", KEYDOWN_ACTIONS, false);
  });

  function applyImgFallback(img) {
    if (!img || img.nodeType !== 1) return;
    if (img.getAttribute("data-csp-fb-done") === "1") return;
    var fb = img.getAttribute("data-csp-fallback-src");
    if (fb) {
      img.setAttribute("data-csp-fb-done", "1");
      img.src = fb;
      return;
    }
    var eid = img.getAttribute("data-csp-error");
    if (eid && STATIC.error && Object.prototype.hasOwnProperty.call(STATIC.error, eid)) {
      img.setAttribute("data-csp-fb-done", "1");
      STATIC.error[eid].call(img, new Event("error"));
    }
  }

  document.addEventListener("error", function (event) {
    var el = event.target;
    if (el && el.nodeType === 1) applyImgFallback(el);
  }, true);

  document.addEventListener("DOMContentLoaded", function () {
    var imgs = document.querySelectorAll("img[data-csp-fallback-src], img[data-csp-error]");
    for (var i = 0; i < imgs.length; i++) {
      if (imgs[i].complete && imgs[i].naturalWidth === 0) {
        applyImgFallback(imgs[i]);
      }
    }
  });
})();

