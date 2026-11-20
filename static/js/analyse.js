/* CareerLens — analysis tool page */

(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var pct = function (v) { return Math.round((v || 0) * 100) + "%"; };

  var meta = null;
  var picked = {};
  var cat = "All";
  var q = "";
  var open = { 0: true };

  var SAMPLE = [
    "SKILLS",
    "Python, SQL, Pandas, Excel, Power BI, Statistics, Git",
    "",
    "PROJECTS",
    "Built a sales performance dashboard using Python, pandas and PostgreSQL with automated weekly refresh.",
    "Created a sentiment analysis notebook on customer reviews using scikit-learn and Matplotlib.",
    "",
    "EXPERIENCE",
    "Data analyst intern at a retail company - built weekly KPI reports and automated data cleaning with Python.",
    "Presented insights to non-technical stakeholders using Power BI dashboards.",
    "",
    "INTERESTS",
    "I enjoy visualising data, working with SQL databases and machine learning problems."
  ].join("\n");

  /* ---------- init ---------- */
  function init() {
    $("form").addEventListener("submit", run);
    $("resume").addEventListener("input", function (e) { $("count").textContent = e.target.value.length + " characters"; });
    $("sample").addEventListener("click", function () {
      $("resume").value = SAMPLE;
      $("resume").dispatchEvent(new Event("input"));
      $("interests").value = "data visualisation, machine learning, SQL";
    });
    $("cats").addEventListener("click", function (e) {
      var b = e.target.closest("[data-cat-btn]");
      if (!b) return;
      cat = b.dataset.catBtn;
      renderCats(); renderChips();
    });
    $("chips").addEventListener("click", function (e) {
      var c = e.target.closest("[data-skill]");
      if (!c) return;
      if (picked[c.dataset.skill]) delete picked[c.dataset.skill]; else picked[c.dataset.skill] = 1;
      renderChips();
    });
    $("skill-search").addEventListener("input", function (e) { q = e.target.value; renderChips(); });
    $("matches").addEventListener("click", function (e) {
      var h = e.target.closest(".match-head");
      if (!h) return;
      var i = h.dataset.i;
      if (open[i]) delete open[i]; else open[i] = true;
      renderMatches(lastData);
    });

    fetch("/api/meta").then(function (r) { return r.json(); }).then(function (m) {
      meta = m;
      fillSelects();
      renderCats();
      renderChips();
    }).catch(function () { fail("Could not load the knowledge base."); });
  }

  function fillSelects() {
    var sel = $("career");
    var cats = Object.keys(meta.careers.reduce(function (a, c) { a[c.category] = 1; return a; }, {})).sort();
    cats.forEach(function (name) {
      var g = document.createElement("optgroup");
      g.label = name;
      meta.careers.filter(function (c) { return c.category === name; }).forEach(function (c) {
        var o = document.createElement("option");
        o.value = c.id; o.textContent = c.title;
        g.appendChild(o);
      });
      sel.appendChild(g);
    });
    var cs = $("company");
    meta.companies.forEach(function (co) {
      var o = document.createElement("option");
      o.value = co.id; o.textContent = co.name;
      cs.appendChild(o);
    });

    /* deep links: /analyse?career=data-scientist&company=razorpay */
    var params = new URLSearchParams(location.search);
    var c = params.get("career");
    var co2 = params.get("company");
    if (c && $("career").querySelector('option[value="' + c.replace(/"/g, "") + '"]')) $("career").value = c;
    if (co2 && $("company").querySelector('option[value="' + co2.replace(/"/g, "") + '"]')) $("company").value = co2;
  }

  function renderCats() {
    var names = ["All"].concat(Object.keys(meta.skills.reduce(function (a, s) { a[s.category] = 1; return a; }, {})).sort());
    $("cats").innerHTML = names.map(function (n) {
      return '<button type="button" class="chip ' + (n === cat ? "on" : "") + '" data-cat-btn="' + esc(n) + '">' + esc(n) + "</button>";
    }).join("");
  }

  function renderChips() {
    var list = meta.skills.slice();
    if (cat !== "All") list = list.filter(function (s) { return s.category === cat; });
    var needle = q.trim().toLowerCase();
    if (needle) list = list.filter(function (s) {
      return s.name.toLowerCase().indexOf(needle) !== -1 || s.aliases.some(function (a) { return a.toLowerCase().indexOf(needle) !== -1; });
    });
    $("chips").innerHTML = list.slice(0, 90).map(function (s) {
      return '<span class="chip ' + (picked[s.id] ? "on" : "") + '" data-skill="' + esc(s.id) + '">' + esc(s.name) + "</span>";
    }).join("");
  }

  function fail(msg) { $("err").textContent = msg; $("err").hidden = false; }

  /* ---------- request ---------- */
  var lastData = null;

  function run(e) {
    e.preventDefault();
    $("err").hidden = true;
    var btn = $("go");
    btn.disabled = true;
    $("go-label").textContent = "Analysing…";

    fetch("/api/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: $("resume").value,
        interests_text: $("interests").value,
        manual_skills: Object.keys(picked),
        target_career: $("career").value || null,
        target_company: $("company").value || null,
        horizon_weeks: (function () {
          var amount = Number($("amount").value) || 4;
          var unit = $("unit").value;
          var weeks = unit === "year" ? amount * 52 : unit === "month" ? amount * 4 : amount;
          return Math.max(4, Math.min(52, Math.round(weeks)));
        })(),
        top_n: 6
      })
    })
      .then(function (r) {
        return r.json().then(function (b) { if (!r.ok) throw new Error(b.detail || "Failed"); return b; });
      })
      .then(function (data) {
        open = { 0: true };
        render(data);
        $("out").scrollIntoView({ behavior: "smooth", block: "start" });
      })
      .catch(function (err) { fail(err.message); })
      .then(function () {
        btn.disabled = false;
        $("go-label").textContent = "Run analysis";
      });
  }

  /* ---------- render ---------- */
  function render(d) {
    lastData = d;
    $("idle").hidden = true;
    $("out").hidden = false;
    renderHead();

    var top = d.matches[0];
    var gaps = (d.focus && d.focus.gaps) || [];
    var crit = gaps.filter(function (g) { return g.priority === "critical"; }).length;
    var rm = (d.focus && d.focus.roadmap) || { total_weeks: 0, estimated_total_hours: 0 };

    var tiles = [
      ["Top match", top ? pct(top.score) : "—", top ? top.title : ""],
      ["Skills found", d.profile.skills_detected, d.profile.skills_proficient + " above threshold"],
      ["Readiness", d.focus ? pct(d.focus.readiness) : "—", d.focus ? d.focus.readiness_label : ""],
      ["Critical gaps", crit, crit ? "close these first" : "nothing blocking"],
      ["Roadmap", CL.duration(rm.total_weeks), "personalised plan"],
      ["Input signal", pct(d.profile.input_strength), "profile detail"]
    ];
    $("summary").innerHTML = tiles.map(function (t) {
      return '<div class="card card-tight"><div class="eyebrow" style="font-size:.6rem">' + esc(t[0]) + '</div>' +
        '<div style="font-size:1.5rem;font-weight:800;letter-spacing:-.03em;margin:2px 0">' + esc(t[1]) + '</div>' +
        '<div class="dim" style="font-size:var(--t-xs)">' + esc(t[2]) + "</div></div>";
    }).join("");

    $("skill-count").textContent = d.skills.length + " found";
    $("skills").innerHTML = d.skills.length
      ? d.skills.slice(0, 44).map(function (s) {
          return '<span class="chip static" style="' + (s.self_reported ? "border-color:var(--accent);color:var(--accent)" : "") + '">' +
            esc(s.name) + '<span class="pct">' + pct(s.proficiency) + "</span></span>";
        }).join("")
      : '<span class="dim">Nothing detected — add skills manually on the left.</span>';

    var ev = d.skills.filter(function (s) { return s.evidence && s.evidence.length; }).slice(0, 8);
    $("evidence").innerHTML = ev.length
      ? ev.map(function (s) {
          return '<div style="border-left:2px solid var(--accent);padding-left:var(--s-3);margin-bottom:var(--s-3)">' +
            '<div style="font-size:var(--t-sm)"><strong>' + esc(s.name) + "</strong> · " + pct(s.proficiency) + " · " + s.mentions + " mentions</div>" +
            s.evidence.map(function (t) { return '<div class="mono dim" style="font-size:var(--t-xs);margin-top:4px">…' + esc(t) + "…</div>"; }).join("") +
            "</div>";
        }).join("")
      : '<div class="dim">No textual evidence — these were self-reported by you.</div>';

    renderMatches(d);
    renderFocus(d);
    renderAdjacent(d.adjacent_skills);
    renderSimilar(d.similar_careers);
  }

  function renderMatches(d) {
    $("match-count").textContent = d.matches.length + " roles";
    $("matches").innerHTML = d.matches.map(function (m, i) {
      var isOpen = !!open[i];
      var gapsHtml = m.gaps.slice(0, 5).map(function (g) {
        return '<div class="kv"><span class="k">' + esc(g.name) + '</span><span class="v">' + pct(g.current) + " / " + pct(g.target) + "</span></div>";
      }).join("") || '<div class="dim" style="font-size:var(--t-sm)">No gaps — fully covered.</div>';
      var strHtml = m.strengths.slice(0, 5).map(function (s) {
        return '<div class="kv"><span class="k">' + esc(s.name) + '</span><span class="v">' + pct(s.current) + "</span></div>";
      }).join("") || '<div class="dim" style="font-size:var(--t-sm)">Nothing evidenced yet.</div>';

      return '<div class="match ' + (i === 0 ? "top" : "") + '">' +
        '<button class="match-head" data-i="' + i + '">' +
          '<span class="match-rank">#' + (i + 1) + "</span>" +
          "<span><span class='match-title'>" + esc(m.title) + "</span>" +
          "<span class='match-meta'>" +
            '<span class="badge">' + esc(m.category) + "</span>" +
            '<span class="badge">' + m.demand + "/5 demand</span>" +
            '<span class="badge badge-accent">' + esc(m.readiness_label) + "</span>" +
          "</span>" +
          '<span class="meter" style="margin-top:8px"><i style="width:' + pct(m.score) + '"></i></span>' +
          "</span>" +
          '<span class="match-score"><span class="num">' + pct(m.score) + '</span><span class="lbl">match</span></span>' +
        "</button>" +
        (isOpen ? '<div class="match-body"><p class="explain">' + esc(m.explanation) + "</p>" +
          '<div class="grid" style="grid-template-columns:1fr 1fr;gap:var(--s-4)">' +
            "<div><span class='eyebrow' style='font-size:.6rem'>Your strengths</span>" + strHtml + "</div>" +
            "<div><span class='eyebrow' style='font-size:.6rem'>Skill gaps</span>" + gapsHtml + "</div>" +
          "</div>" +
          '<div class="grid" style="grid-template-columns:1fr 1fr;gap:var(--s-4);margin-top:var(--s-4)">' +
            "<div><span class='eyebrow' style='font-size:.6rem'>Responsibilities</span>" +
              m.responsibilities.map(function (r) { return '<div class="kv"><span class="k">' + esc(r) + "</span></div>"; }).join("") + "</div>" +
            "<div><span class='eyebrow' style='font-size:.6rem'>Companies hiring</span>" +
              ((m.hiring_companies || []).map(function (c) { return '<div class="kv"><span class="k">' + esc(c) + "</span></div>"; }).join("") ||
               '<div class="dim" style="font-size:var(--t-sm)">Not listed.</div>') +
            "</div>" +
          "</div>" +
          '<div class="row gap-2" style="margin-top:var(--s-4)"><a class="btn btn-ghost btn-sm" href="/careers/' + esc(m.id) + '">Open career page →</a></div>' +
        "</div>" : "") +
      "</div>";
    }).join("");
  }

  function renderFocus(d) {
    var f = d.focus;
    var host = $("focus");
    if (!f) { host.innerHTML = ""; return; }

    var C = 2 * Math.PI * 44;
    var off = C * (1 - f.readiness);

    var gapHtml = f.gaps.slice(0, 8).map(function (g) {
      var cls = g.priority === "critical" ? "crit" : g.priority === "high" ? "high" : "";
      return '<div class="kv"><span class="k">' + esc(g.name) + '</span><span class="v ' + cls + '">' + g.priority + " · " + pct(g.current) + "→" + pct(g.target) + "</span></div>" +
        '<div class="note">' + esc(g.rationale) + "</div>";
    }).join("") || '<div class="dim">You cover every requirement for this role.</div>';

    var phases = f.roadmap.phases.map(function (p) {
      var weeks = [];
      for (var i = 0; i < Math.min(p.weeks, 8); i++) weeks.push('<span class="week">W' + (i + 1) + " " + esc(p.skills[i % p.skills.length].name) + "</span>");
      return '<div class="phase">' +
        '<div class="phase-head"><span class="phase-name">' + esc(p.name) + '</span><span class="phase-meta">' + CL.duration(p.weeks) + "</span></div>" +
        '<div class="milestone">' + esc(p.milestone) + "</div>" +
        '<div class="row gap-1 wrapf">' + p.skills.map(function (s) {
          return '<span class="chip static">' + esc(s.name) + '<span class="pct">' + pct(s.current) + "</span></span>";
        }).join("") + "</div>" +
        '<div class="weeks">' + weeks.join("") + "</div></div>";
    }).join("") || '<div class="dim">No roadmap needed — you are already ready.</div>';

    var res = f.roadmap.resources.slice(0, 8).map(function (r) {
      return '<div class="res"><span class="res-kind">' + esc(r.kind) + "</span><span>" +
        '<div class="res-title">' + esc(r.title) + "</div>" +
        '<div class="res-sub">' + esc(r.provider) + " · " + CL.duration(Math.max(1, Math.round(r.hours / 8))) + " · closes " + esc(r.skill_name) +
        (r.url ? ' · <a href="' + esc(r.url) + '" target="_blank" rel="noopener">open</a>' : "") + "</div></span></div>";
    }).join("");

    var projs = f.projects.map(function (p) {
      var closeSet = {};
      (p.closes || []).forEach(function (c) { closeSet[c.skill_id] = 1; });
      var tags = p.skill_ids.map(function (sid, i) {
        return '<span class="chip static ' + (closeSet[sid] ? "on" : "") + '">' + esc(p.skills[i]) + "</span>";
      }).join("");
      return '<div class="card proj"><h4>' + esc(p.title) + "</h4><p>" + esc(p.summary) + "</p>" +
        '<div class="row gap-1 wrapf">' + tags + "</div>" +
        '<div class="proj-foot"><span class="diff diff-' + esc(p.difficulty) + '">' + esc(p.difficulty) + '</span><span class="mono dim" style="font-size:var(--t-xs)">~' + p.estimated_hours + "h</span></div></div>";
    }).join("") || '<div class="dim">No projects needed.</div>';

    var cf = f.company_fit;
    var cfHtml = "";
    if (cf) {
      cfHtml = '<section class="card" style="border-color:var(--accent-3)">' +
        "<h3>" + esc(cf.name) + " <span class='dim' style='font-weight:400'>· " + esc(cf.industry) + "</span></h3>" +
        '<div class="dim" style="font-size:var(--t-sm);margin:2px 0 var(--s-3)">' + esc(cf.location) + " · " + esc(cf.size) + " employees</div>" +
        "<p style='font-size:var(--t-sm)'>" + esc(cf.description) + "</p>" +
        '<div class="row gap-1 wrapf" style="margin-top:var(--s-3)">' +
          cf.hiring_titles.map(function (t) { return '<span class="chip static">' + esc(t) + "</span>"; }).join("") +
        "</div>" +
        '<div class="row gap-1 wrapf" style="margin-top:var(--s-2)">' +
          cf.extra_skills.map(function (s) {
            return '<span class="badge ' + (s.covered ? "badge-ok" : "badge-warn") + '">' + (s.covered ? "✓" : "○") + " " + esc(s.name) + "</span>";
          }).join("") +
        "</div></section>";
    }

    host.innerHTML =
      cfHtml +
      '<section class="card"><div class="row gap-5 wrapf" style="align-items:center">' +
        '<div class="ring" style="width:104px;height:104px">' +
          '<svg width="104" height="104" viewBox="0 0 104 104">' +
          '<circle class="track" cx="52" cy="52" r="44" />' +
          '<circle class="prog" cx="52" cy="52" r="44" stroke-dasharray="' + C + '" stroke-dashoffset="' + off + '" />' +
          "</svg>" +
          '<span class="ring-label" style="font-size:1.3rem">' + pct(f.readiness) + "</span>" +
        "</div>" +
        '<div class="grow" style="min-width:220px">' +
          "<h3>" + esc(f.career_title) + " readiness</h3>" +
          '<div style="margin:6px 0"><span class="badge badge-ok">' + esc(f.readiness_label) + "</span></div>" +
          '<p class="dim" style="font-size:var(--t-sm)">Weighted coverage of every skill this role asks for, where each skill\'s importance weight decides how much a gap costs you.</p>' +
        "</div></div></section>" +

      '<section class="card"><div class="row between wrapf gap-2" style="margin-bottom:var(--s-4)">' +
        "<h3>Skill gap analysis</h3><span class='badge'>" + f.gaps.length + " gaps</span></div>" + gapHtml + "</section>" +

      '<section class="card"><div class="row between wrapf gap-2" style="margin-bottom:var(--s-4)">' +
        "<h3>Learning roadmap</h3><span class='badge'>" + CL.duration(f.roadmap.total_weeks) + "</span></div>" + phases + "</section>" +

      (res ? '<section class="card"><h3 style="margin-bottom:var(--s-4)">Recommended resources</h3>' + res + "</section>" : "") +

      '<section class="card"><div class="row between wrapf gap-2" style="margin-bottom:var(--s-4)">' +
        "<h3>Projects that close your gaps</h3><span class='dim mono' style='font-size:var(--t-xs)'>portfolio evidence</span></div>" +
        '<div class="grid g-3">' + projs + "</div></section>";
  }

  function renderAdjacent(items) {
    var host = $("adjacent");
    if (!items || !items.length) { host.innerHTML = '<div class="dim">Add skills to see adjacent recommendations.</div>'; return; }
    var max = Math.max.apply(null, items.map(function (i) { return i.affinity; })) || 1;
    host.innerHTML = items.map(function (i) {
      return '<div class="card card-tight">' +
        '<div style="font-weight:600;font-size:var(--t-sm)">' + esc(i.name) + "</div>" +
        '<div class="mono dim" style="font-size:var(--t-xs)">affinity ' + i.affinity.toFixed(2) + "</div>" +
        '<div class="meter" style="margin-top:7px"><i style="width:' + Math.round((i.affinity / max) * 100) + '%"></i></div></div>';
    }).join("");
  }

  function renderSimilar(items) {
    var host = $("similar");
    if (!items || !items.length) { host.innerHTML = '<div class="dim">No similar roles.</div>'; return; }
    host.innerHTML = items.map(function (i) {
      return '<a class="chip" href="/careers/' + esc(i.id) + '">' + esc(i.title) + '<span class="pct">' + i.similarity.toFixed(2) + "</span></a>";
    }).join("");
  }

  init();
})();
