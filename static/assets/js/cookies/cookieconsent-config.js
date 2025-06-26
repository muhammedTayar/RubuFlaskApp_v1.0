/* cookieconsent-config.js · v1.0  --------------------------------------
 * · Dark-Mode-Banner  (bar-inline)
 * · GA, reCAPTCHA, Google-Maps – alles über CookieConsent gesteuert
 * · Umfangreiche 📌-Debug-Logs  (DEBUG_CC = true)
 * --------------------------------------------------------------------*/
(() => {
  "use strict";

  /* ---------- 0) Globals & Debug flag -------------------------------- */
  const DEBUG_CC = true;                         // <- hier ausschalten, wenn Ruhe gewünscht
  const log = (...a) => DEBUG_CC && console.log("📌", ...a);

  /* ---------- 1) Sofortiges Dark-Theme --------------------------------*/
  document.documentElement.classList.add("cc--darkmode");

  /* ---------- 2) Service Helpers --------------------------------------*/
  const S = {                   // wird unten in den Callbacks benutzt
    analytics() {
      if (S.analytics.done) return;
      S.analytics.done = true;
      log("[GA] consent granted – initialisiere GA");
      if (!window.gtag || !window.CONFIG?.GA_ID) return log("[GA] fehlt GA_ID oder gtag()");
      gtag("consent", "update", { analytics_storage: "granted", ad_storage: "granted" });
      gtag("config", window.CONFIG.GA_ID, { send_page_view: true, debug_mode: DEBUG_CC });
    },

    maps() {
      const wrap = document.getElementById("map-wrapper");
      if (!wrap || wrap.dataset.loaded) return;

      /* ► NUR die URL zwischen den Anführungszeichen lassen! */
      let src = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2626.887391795017!2d10.059395076971292!3d48.822209971327304!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47991b130e78570f%3A0x86f70f0fa52d4c54!2sFelix-Wankel-Stra%C3%9Fe%201%2C%2073431%20Aalen!5e0!3m2!1sde!2sde!4v1750791273215!5m2!1sde!2sde";

      /* Sicherheitshalber säubern */
      src = src
            .replace(/\s+/g, '')        // Zeilenumbrüche/Spaces killen
            .replace(/&amp;/g, '&')     // doppelt ge-escapte &
            .replace(/&#(\d+);/g, (_,d)=>'%'+(+d).toString(16)); // Entities → %xx

      wrap.dataset.loaded = "1";
      wrap.innerHTML = `
        <iframe width="100%" height="290" loading="lazy"
                style="border:0" allowfullscreen
                referrerpolicy="no-referrer-when-downgrade"
                src="${src}">
        </iframe>`;
    },

    recaptcha: (() => {
      /* alle reCAPTCHA-Details inc. Lazy-Loader */
      const SITE_KEY = window.RECAPTCHA_SITE_KEY || "";
      const SCRIPT_SRC = "https://www.google.com/recaptcha/api.js";
      const QUERY = "?onload=recaptchaLoaded&render=explicit";
      let scriptTag = null, widgetId = null;

      function inject() {
        if (!SITE_KEY) return log("⚠️  kein SITE_KEY – überspringe");
        if (scriptTag) return;
        log("[reCAPTCHA] inject Script…");
        scriptTag = document.createElement("script");
        scriptTag.src = SCRIPT_SRC + QUERY;
        scriptTag.async = true;
        scriptTag.defer = true;
        scriptTag.onload = () => log("[reCAPTCHA] Script geladen");
        scriptTag.onerror = () => log("❌ [reCAPTCHA] Script-Fehler");
        document.head.appendChild(scriptTag);
      }

      window.recaptchaLoaded = () => {
        log("[reCAPTCHA] API geladen");
        attempt();
      };

      function attempt(attempts = 0) {
        const BOX = document.getElementById("recaptcha-box");
        if (!BOX) return attempts < 15
          ? setTimeout(() => attempt(attempts + 1), 100)
          : log("❌ [reCAPTCHA] Kein Platzhalter gefunden");
        if (widgetId !== null) return log("[reCAPTCHA] schon gerendert");
        if (!window.grecaptcha) return log("[reCAPTCHA] grecaptcha fehlt");
        try {
          widgetId = grecaptcha.render(BOX, { sitekey: SITE_KEY, callback: t => log("[reCAPTCHA] Token", t.slice(0,8)+"…") });
          log("[reCAPTCHA] Widget-ID", widgetId);
        } catch (e) {
          log("❌ [reCAPTCHA] Render-Fehler", e);
        }
      }

      function init() {
        inject();
        attempt();
      }

      return {
        init,
        done: false
      };
    })(),

    clearGA() {
      ["_ga", "_gid", "_gat", "_gcl_au"].forEach(name =>
        (document.cookie = `${name}=;path=/;expires=Thu, 01 Jan 1970 00:00:00 GMT`));
      log("[GA] GA-Cookies gelöscht (Consent entzogen)");
    }
  };

  /* ---------- 3) Übersetzungen ---------------------------------------*/
  const t = {
    de: {
      consentModal: {
        title: "Cookies & Dienste",
        description:
          'Wir nutzen Cookies & externe Dienste. Du entscheidest. <a href="/datenschutz" target="_blank">Mehr erfahren</a>.',
        acceptAllBtn: "Alle akzeptieren",
        acceptNecessaryBtn: "Nur notwendige",
        showPreferencesBtn: "Auswahl erlauben"
      },
      preferencesModal: {
        title: "Datenschutzeinstellungen",
        acceptAllBtn: "Alle akzeptieren",
        acceptNecessaryBtn: "Nur notwendige",
        savePreferencesBtn: "Speichern",
        closeIconLabel: "Schließen",
        sections: [
          { linkedCategory: "necessary",
            title: '<span class="pm__badge">Immer aktiv</span>',
            description: "Für den technischen Betrieb erforderlich." },
          { linkedCategory: "statistics",
            title: "Statistik",
            description: "Hilft uns zu verstehen, wie unsere Seite genutzt wird." },
          { linkedCategory: "marketing",
            title: "Marketing",
            description: "Ermöglicht personalisierte Inhalte & Werbung." },
          { linkedCategory: "security",
            title: "reCAPTCHA",
            description: "Schützt Formulare vor Spam und Bots." }
        ]
      }
    }
  };

  /* ---------- 4) Services -------------------------------------------*/
  const services = [
    { name: "CookieConsent", category: "necessary", uri: "" },
    { name: "Google Analytics", category: "statistics",
      uri: "https://developers.google.com/analytics/devguides/collection/gtagjs" },
    { name: "Google Maps", category: "marketing",
      uri: "https://policies.google.com/technologies/cookies" },
    { name: "reCAPTCHA", category: "security",
      uri: "https://developers.google.com/recaptcha/docs/privacy" }
  ];

  /* ---------- 5) Initialisierung -------------------------------------*/
  CookieConsent.run({
    disablePageInteraction: true,
    language: { default: "de", translations: t },
    services,
    guiOptions: {
      consentModal    : { layout: "bar inline", position: "bottom", flipButtons: true },
      preferencesModal: { layout: "bar wide",  position: "right",  flipButtons: true }
    },
    palette: {
      popup : { background: "#1d1f20", text: "#ffffff" },
      button: { background: "#47b2e4", text: "#ffffff" }
    },
    categories: { necessary: {readOnly:true}, statistics:{}, marketing:{}, security:{} },

    onReady({ cookie }) {
      log("[CC] onReady", cookie);
      if (cookie.acceptedCategories.includes("statistics")) S.analytics();
      if (cookie.acceptedCategories.includes("marketing"))  S.maps();
      if (cookie.acceptedCategories.includes("security"))   S.recaptcha.init();
    },

    onAccept({ cookie }) {
      log("[CC] onAccept", cookie.acceptedCategories);
      const has = c => cookie.acceptedCategories.includes(c);
      if (has("statistics")) S.analytics();
      if (has("marketing"))   S.maps();
      if (has("security"))    S.recaptcha.init();
    }
  });

  /* ---------- 6) Maps-Button (Lazy-Load) ------------------------------*/
  document.getElementById("map-load")?.addEventListener("click", () => {
    if (CookieConsent.acceptedCategory("marketing")) S.maps();
    else alert("Bitte zuerst Marketing-Cookies akzeptieren, um die Karte zu laden.");
  });

  /* ---------- 7) Debug-Hilfen im Global Scope -------------------------*/
  window.CCdebug = { S, CookieConsent };
  log("[CC] Konfiguration fertig initialisiert");
})();
