/* Student Recommendation - shared shell behaviour (themes, nav, filters) */

(function () {
  "use strict";

  /* ---------- theme ---------- */
  var THEMES = ["aurora", "candy", "mint", "sky", "paper"];
  var LABEL = { aurora: "Aurora", candy: "Candy", mint: "Mint", sky: "Sky", paper: "Paper" };
  var KEY = "sr-theme";
  var DEFAULT_THEME = "aurora";

  function apply(name) {
    if (THEMES.indexOf(name) === -1) name = DEFAULT_THEME;
    document.documentElement.setAttribute("data-theme", name);
    try { localStorage.setItem(KEY, name); } catch (e) {}
    var label = document.getElementById("theme-label");
    if (label) label.textContent = LABEL[name];
    document.querySelectorAll("[data-set-theme]").forEach(function (b) {
      b.classList.toggle("on", b.dataset.setTheme === name);
    });
    document.dispatchEvent(new CustomEvent("themechange", { detail: { theme: name } }));
  }

  var stored = DEFAULT_THEME;
  try { stored = localStorage.getItem(KEY) || DEFAULT_THEME; } catch (e) {}
  apply(stored);

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-set-theme]");
    if (btn) { apply(btn.dataset.setTheme); return; }
  });

  var themeWrap = document.getElementById("themes");
  var themeBtn = document.getElementById("themes-btn");
  if (themeBtn && themeWrap) {
    themeBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = themeWrap.classList.toggle("open");
      themeBtn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", function () {
      themeWrap.classList.remove("open");
      themeBtn.setAttribute("aria-expanded", "false");
    });
  }

  /* ---------- mobile menu ---------- */
  var burger = document.getElementById("burger");
  var menu = document.getElementById("mobile-menu");
  if (burger && menu) {
    burger.addEventListener("click", function () { menu.classList.toggle("open"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") menu.classList.remove("open"); });
  }

  /* ---------- generic client-side filtering ----------
     One controller per [data-filter-group]. The search input and the category
     chips are combined with AND: a card is shown only when its [data-search]
     text matches the query *and* its [data-cat] equals the selected chip
     ("all" means no category constraint). Both controls drive the same
     render(), so neither can clobber the other's result.                  */
  document.querySelectorAll("[data-filter-group]").forEach(function (group) {
    var target = document.querySelector(group.dataset.filterGroup);
    if (!target) return;

    var input = group.querySelector("[data-filter]");
    var chips = Array.prototype.slice.call(group.querySelectorAll("[data-filter-chip]"));
    var items = Array.prototype.slice.call(target.querySelectorAll("[data-search], [data-cat]"));
    var emptyMsg = document.querySelector(group.dataset.filterGroupEmpty || "[data-empty]");
    var countEl = document.querySelector(group.dataset.filterGroupCount || "");
    var active = "all";

    function render() {
      var q = input ? input.value.trim().toLowerCase() : "";
      var shown = 0;
      items.forEach(function (el) {
        var text = (el.dataset.search || "").toLowerCase();
        var cat = el.dataset.cat;
        var hitText = !q || text.indexOf(q) !== -1;
        var hitCat = active === "all" || !cat || cat === active;
        var hit = hitText && hitCat;
        el.classList.toggle("hide", !hit);
        if (hit) shown++;
      });
      if (emptyMsg) emptyMsg.classList.toggle("hide", shown !== 0);
      if (countEl) countEl.textContent = shown;
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.classList.remove("on"); });
        chip.classList.add("on");
        active = chip.dataset.filterChip || "all";
        render();
      });
    });

    if (input) input.addEventListener("input", render);
    render();
  });

  /* ---------- count-up on stat elements ---------- */
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var target = parseFloat(el.dataset.count) || 0;
    var suffix = el.dataset.suffix || "";
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.textContent = target + suffix;
      return;
    }
    var started = false;
    var run = function () {
      if (started) return;
      started = true;
      var t0 = performance.now(), dur = 1100;
      var tick = function (t) {
        var p = Math.min((t - t0) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if (target > 0) { new IntersectionObserver(function (e, o) { if (e[0].isIntersecting) { run(); o.disconnect(); } }).observe(el); }
    else run();
  });

  /* ---------- reveal on scroll ---------- */
  var revealables = document.querySelectorAll("[data-reveal]");
  if (revealables.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("rise"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("rise"); });
  }

  /* ---------- duration formatting ----------
     Roadmaps are planned in weeks internally, but students think in weeks,
     months and years. One formatter keeps every screen consistent. */
  function duration(weeks) {
    weeks = Number(weeks) || 0;
    if (weeks >= 52) {
      var y = Math.round((weeks / 52) * 10) / 10;
      return y + (y === 1 ? " year" : " years");
    }
    if (weeks >= 4) {
      var m = Math.round((weeks / 4) * 10) / 10;
      return m + (m === 1 ? " month" : " months");
    }
    return weeks + (weeks === 1 ? " week" : " weeks");
  }

  window.CL = { applyTheme: apply, THEMES: THEMES, duration: duration };
})();
