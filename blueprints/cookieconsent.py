# blueprints/cookieconsent.py  – korrigierte CookieConsent v3-Bar-Konfiguration mit snake_case guiOptions
from flask import Blueprint, current_app, make_response, render_template_string

bp_cookie = Blueprint(
    'cookieconsent',
    __name__
)

# Dynamische JS-Konfiguration für CookieConsent v3
_TEMPLATE = r"""
// 1) Bibliothek laden
(function(){
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/gh/orestbida/cookieconsent@3.1.0/dist/cookieconsent.umd.js';
  script.async = true;
  script.onload = () => {
    // 2) Basis + Debug
    const LANG      = navigator.language.startsWith('de') ? 'de' : 'en';
    const RECAP_ON  = {{ RECAPTCHA_ENABLED | tojson }};
    const RECAP_KEY = {{ RECAPTCHA_SITE_KEY | tojson }};
    const ENV       = {{ ENV | tojson }};
    const DBG       = ENV === 'dev';
    const log       = (...m) => DBG && console.log('[CC]', ...m);

    // 3) Übersetzungen
    const I18N = {
      de: {
        consent_modal: {
          title: 'Cookies',
          description: 'Wir verwenden Cookies für Statistik (GA4) und Sicherheit (reCAPTCHA).',
          primary_btn:    { text: 'Alle akzeptieren', role: 'accept_all' },
          secondary_btn:  { text: 'Alle ablehnen',    role: 'reject_all' },
          learn_more_btn: { text: 'Einstellungen verwalten', role: 'settings' }
        },
        settings_modal: {
          title: 'Cookie-Einstellungen',
          save_settings_btn: 'Einstellungen speichern',
          accept_all_btn:    'Alle akzeptieren',
          reject_all_btn:    'Alle ablehnen',
          close_btn_label:   'Schließen',
          blocks: [
            { title: 'Notwendig',           type: 'toggle', label: 'Notwendig',   linked_categories: ['necessary'], read_only: true },
            { title: 'Statistik',           type: 'toggle', label: 'Statistik',   linked_categories: ['statistics'] },
            { title: 'Marketing',           type: 'toggle', label: 'Marketing',   linked_categories: ['marketing'] },
            { title: 'Sicherheit',          type: 'toggle', label: 'Sicherheit',  linked_categories: ['security'] }
          ]
        }
      },
      en: {
        consent_modal: {
          title: 'Cookies',
          description: 'We use cookies for analytics (GA4) and security (reCAPTCHA).',
          primary_btn:    { text: 'Accept all', role: 'accept_all' },
          secondary_btn:  { text: 'Reject all', role: 'reject_all' },
          learn_more_btn: { text: 'Manage settings', role: 'settings' }
        },
        settings_modal: {
          title: 'Cookie Preferences',
          save_settings_btn: 'Save preferences',
          accept_all_btn:    'Accept all',
          reject_all_btn:    'Reject all',
          close_btn_label:   'Close',
          blocks: [
            { title: 'Necessary',    type: 'toggle', label: 'Necessary',    linked_categories: ['necessary'], read_only: true },
            { title: 'Statistics',   type: 'toggle', label: 'Statistics',   linked_categories: ['statistics'] },
            { title: 'Marketing',    type: 'toggle', label: 'Marketing',    linked_categories: ['marketing'] },
            { title: 'Security',     type: 'toggle', label: 'Security',     linked_categories: ['security'] }
          ]
        }
      }
    };
    log('I18N geladen:', I18N);

    // 4) Dienste
    const Services = {
      ga() {
        if (window.__ga_loaded) return;
        const s2 = document.createElement('script'); s2.async = true;
        s2.src = 'https://www.googletagmanager.com/gtag/js?id=G-HP7N4LH3RN';
        document.head.appendChild(s2);
        s2.onload = () => {
          window.dataLayer = window.dataLayer || [];
          window.gtag = (...args) => window.dataLayer.push(args);
          gtag('js', new Date());
          gtag('config', 'G-HP7N4LH3RN');
          window.__ga_loaded = true;
        };
      },
      clearGA() { document.cookie.split(';').forEach(c=>document.cookie=c.replace(/=.*/, '=;expires='+new Date().toUTCString()+';path=/')); },
      map() {},
      recaptcha() { if (RECAP_ON && RECAP_KEY && !window.__rc_loaded) window.__rc_loaded = true; }
    };

    // 5) Handler
    function handle(cats) {
      const has = c => cats.includes(c);
      has('statistics')? Services.ga() : Services.clearGA();
      if (has('marketing')) Services.map();
      if (has('security'))  Services.recaptcha();
    }

    // 6) Init CookieConsent
    CookieConsent.run({
      categories:      { necessary:{readOnly:true}, statistics:{}, marketing:{}, ...(RECAP_ON?{security:{}}:{}) },
      language:        { default: LANG, translations: I18N },
      guiOptions:      { consent_modal:{ layout:'bar', position:'bottom', flipButtons:false }, settings_modal:{ layout:'box', position:'bottom center' } },
      palette:         { popup:{ background:'#202124', text:'#e8eaed' }, button:{ background:'#8ab4f8', text:'#000' } },
      autoShow:        true,
      forceShow:       DBG,
      onReady:         ({cookie}) => handle(cookie.acceptedCategories),
      onFirstAction:   ({cookie}) => handle(cookie.acceptedCategories),
      onAccept:        ({acceptedCategories}) => handle(acceptedCategories),
      onChange:        ({acceptedCategories}) => handle(acceptedCategories)
    });
  };
  document.head.appendChild(script);
})();
"""

@bp_cookie.route('/static/assets/js/cookieconsent-config.js')
def cookieconsent_config():
    env = 'dev' if current_app.debug else 'prod'
    js = render_template_string(
        _TEMPLATE,
        RECAPTCHA_ENABLED=current_app.config.get('RECAPTCHA_ENABLED', False),
        RECAPTCHA_SITE_KEY=current_app.config.get('RECAPTCHA_SITE_KEY'),
        ENV=env
    )
    resp = make_response(js)
    resp.mimetype = 'application/javascript'
    resp.headers['Cache-Control'] = 'no-store' if current_app.debug else 'public, max-age=1800'
    return resp
