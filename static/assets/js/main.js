(function () {
  "use strict";

  /* ========= Helper ========= */
  const select = (el, all = false) => {
    el = el.trim();
    return all ? [...document.querySelectorAll(el)] : document.querySelector(el);
  };

  const on = (type, el, listener, all = false) => {
    const sel = select(el, all);
    if (!sel) return;
    (all ? sel : [sel]).forEach(e => e.addEventListener(type, listener));
  };

  const onscroll = (el, listener) => el.addEventListener("scroll", listener);

  /* ========= Navbar active ========= */
  const navbarlinks = select("#navbar .scrollto", true);
  const navbarlinksActive = () => {
    const pos = window.scrollY + 200;
    navbarlinks.forEach(link => {
      if (!link.hash) return;
      const section = select(link.hash);
      if (!section) return;
      link.classList.toggle("active",
        pos >= section.offsetTop &&
        pos <= section.offsetTop + section.offsetHeight
      );
    });
  };
  window.addEventListener("load", navbarlinksActive);
  onscroll(document, navbarlinksActive);

  /* ========= Smooth scroll ========= */
  const scrollto = (el) => {
    const header = select("#header");
    const offset = header ? header.offsetHeight : 0;
    window.scrollTo({
      top: select(el).offsetTop - offset,
      behavior: "smooth"
    });
  };

  /* ========= Header shadow ========= */
  const header = select("#header");
  if (header) {
    const headerScrolled = () =>
      header.classList.toggle("header-scrolled", window.scrollY > 100);
    window.addEventListener("load", headerScrolled);
    onscroll(document, headerScrolled);
  }

  /* ========= Back-to-top ========= */
  const backtotop = select(".back-to-top");
  if (backtotop) {
    const toggle = () =>
      backtotop.classList.toggle("active", window.scrollY > 100);
    window.addEventListener("load", toggle);
    onscroll(document, toggle);
  }

  /* ========= Mobile nav ========= */
  on("click", ".mobile-nav-toggle", function () {
    select("#navbar").classList.toggle("navbar-mobile");
    this.classList.toggle("bi-list");
    this.classList.toggle("bi-x");
  });

  on("click", ".navbar .dropdown > a", function (e) {
    if (select("#navbar").classList.contains("navbar-mobile")) {
      e.preventDefault();
      this.nextElementSibling.classList.toggle("dropdown-active");
    }
  }, true);

  on("click", ".scrollto", function (e) {
    if (select(this.hash)) {
      e.preventDefault();
      const navbar = select("#navbar");
      if (navbar.classList.contains("navbar-mobile")) {
        navbar.classList.remove("navbar-mobile");
        select(".mobile-nav-toggle").classList.toggle("bi-list");
        select(".mobile-nav-toggle").classList.toggle("bi-x");
      }
      scrollto(this.hash);
    }
  }, true);

  window.addEventListener("load", () => {
    if (window.location.hash && select(window.location.hash))
      scrollto(window.location.hash);
  });

  /* ========= Preloader ========= */
  window.addEventListener("load", () => {
    const pre = document.getElementById("preloader");
    if (!pre) return;
    pre.style.transition = "opacity .5s";
    pre.style.opacity = 0;
    setTimeout(() => pre.remove(), 500);
  });

  /* ========= Skills bar ========= */
  const skills = select(".skills-content");
  if (skills) {
    new Waypoint({
      element: skills,
      offset: "80%",
      handler: () =>
        select(".progress .progress-bar", true).forEach(el => {
          el.style.width = `${el.getAttribute("aria-valuenow")}%`;
        })
    });
  }

  /* ========= Portfolio (Tabs / Isotope) ========= */
  window.addEventListener("DOMContentLoaded", () => {
    const container = select('.portfolio-container');
    if (!container) return;

    // Isotope initialisieren
    const iso = new Isotope(container, {
      itemSelector: '.portfolio-item',
      layoutMode: 'fitRows',
      filter: '.filter-description'
    });
    iso.on('arrangeComplete', () => AOS.refresh());

    // Pill-Buttons unten
    const buttons = select('#portfolio-flters [data-filter]', true);
    const setFilter = btn => {
      buttons.forEach(b => b.classList.toggle('active', b === btn));
      iso.arrange({ filter: btn.dataset.filter });
    };
    // Erstes Tab vorselektieren
    setFilter(buttons[0]);

    // Klick auf Pill-Buttons
    buttons.forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        setFilter(btn);
      });
    });

    // Dropdown-Links oben in der Navbar
    const ddLinks = select('.dropdown-item[data-filter]', true);
    if (ddLinks) {
      ddLinks.forEach(link => {
        link.addEventListener('click', e => {
          e.preventDefault();
          const filter = link.dataset.filter;

          // 1) Smooth scroll zum Portfolio-Bereich
          if (select('#portfolio')) scrollto('#portfolio');

          // 2) Entsprechende Pill unten aktivieren
          const target = buttons.find(b => b.dataset.filter === filter);
          if (target) setFilter(target);
        });
      });
    }
  });

  /* ========= Swiper ========= */
  new Swiper(".portfolio-details-slider", {
    speed: 400,
    loop: true,
    autoplay: { delay: 5000, disableOnInteraction: false },
    pagination: { el: ".swiper-pagination", type: "bullets", clickable: true }
  });

  /* ========= AOS ========= */
  window.addEventListener("load", () =>
    AOS.init({ duration: 1000, easing: "ease-in-out", once: true, mirror: false })
  );

  /* ========= Flash fade ========= */
  setTimeout(() =>
    $("#flash-alert").fadeTo(500, 0).slideUp(500, function () {
      $(this).remove();
    }), 5000
  );

  /* ========= Typewriter ========= */
  window.addEventListener("DOMContentLoaded", () => {
    const lang = document.getElementById("selected-language")?.dataset.lang;
    if (!lang) return;
    fetch(`static/assets/json/${lang}.json`)
      .then(r => r.json())
      .then(t => {
        const phrases = t.hero_section.future_science;
        const ph = document.querySelector(".dynamic-placeholder");
        const txt = document.getElementById("dynamic-text");
        ph.textContent = phrases.reduce((a, b) => a.length > b.length ? a : b, "");
        let p = 0, c = 0;
        const type = () => {
          const cur = phrases[p];
          txt.textContent = cur.slice(0, c++);
          if (c <= cur.length) return setTimeout(type, 80);
          c = 0; p = (p + 1) % phrases.length; setTimeout(type, 1500);
        };
        type();
      });
  });

  /* ========= Timeline ========= */
  (() => {
    const items = document.querySelectorAll(".timeline li");
    const inView = el => {
      const r = el.getBoundingClientRect();
      return (
        r.top >= 0 && r.left >= 0 &&
        r.bottom <= (innerHeight || document.documentElement.clientHeight) &&
        r.right <= (innerWidth || document.documentElement.clientWidth)
      );
    };
    const cb = () => items.forEach(i => inView(i) && i.classList.add("in-view"));
    ["load", "resize", "scroll"].forEach(ev => window.addEventListener(ev, cb));
  })();

  /* ========= GLB tweak ========= */
  document.querySelector("model-viewer")?.addEventListener("load", e => {
    e.target.model.materials.forEach(mat => {
      const pbr = mat.pbrMetallicRoughness;
      pbr.setBaseColorFactor([0.2, 0.2, 0.2, 1]);
      pbr.setMetallicFactor(0.9);
      pbr.setRoughnessFactor(0.2);
    });
  });
})(); // <-- Hier war vorher eine überzählige schließende Klammer