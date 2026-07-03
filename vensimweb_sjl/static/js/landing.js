/* Landing — Residuos Sólidos SJL
   Partículas del hero, revelados por scroll, contadores, sparklines vivas y tilt 3D. */
(function () {
  "use strict";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 1. Campo de partículas del hero ---------- */
  function particles() {
    const canvas = document.getElementById("flow-canvas");
    if (!canvas || reduced) return;
    const ctx = canvas.getContext("2d");
    const COLORS = ["47,122,110", "70,194,169", "201,138,31", "246,239,227"];
    let W, H, pts = [], raf;

    function resize() {
      W = canvas.width = canvas.offsetWidth * devicePixelRatio;
      H = canvas.height = canvas.offsetHeight * devicePixelRatio;
    }
    function spawn(n) {
      pts = [];
      for (let i = 0; i < n; i++) {
        pts.push({
          x: Math.random() * W, y: Math.random() * H,
          r: (Math.random() * 1.8 + 0.6) * devicePixelRatio,
          sp: (Math.random() * 0.35 + 0.12) * devicePixelRatio,
          ph: Math.random() * Math.PI * 2,
          c: COLORS[(Math.random() * COLORS.length) | 0],
          a: Math.random() * 0.35 + 0.12,
        });
      }
    }
    let t = 0;
    function tick() {
      t += 0.004;
      ctx.clearRect(0, 0, W, H);
      for (const p of pts) {
        // deriva ascendente siguiendo un campo sinusoidal suave
        p.y -= p.sp;
        p.x += Math.sin(t * 2 + p.ph + p.y * 0.0016) * 0.45 * devicePixelRatio;
        if (p.y < -8) { p.y = H + 8; p.x = Math.random() * W; }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.c},${p.a})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(tick);
    }
    resize(); spawn(Math.min(110, (innerWidth / 12) | 0)); tick();
    addEventListener("resize", () => { resize(); spawn(Math.min(110, (innerWidth / 12) | 0)); });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) cancelAnimationFrame(raf); else tick();
    });
  }

  /* ---------- 2. Revelado por scroll ---------- */
  function reveals() {
    const els = document.querySelectorAll(".io-reveal");
    if (!("IntersectionObserver" in window) || reduced) {
      els.forEach((e) => e.classList.add("in"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.18 });
    els.forEach((e) => io.observe(e));
  }

  /* ---------- 3. Contadores ---------- */
  function counters() {
    const els = document.querySelectorAll(".counter");
    const run = (el) => {
      const target = +el.dataset.target, suffix = el.dataset.suffix || "";
      const t0 = performance.now(), dur = 1400;
      (function step(now) {
        const k = Math.min((now - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - k, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    };
    if (reduced || !("IntersectionObserver" in window)) {
      els.forEach((el) => (el.textContent = el.dataset.target + (el.dataset.suffix || "")));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { run(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    els.forEach((e) => io.observe(e));
  }

  /* ---------- 4. Sparklines vivas (datos del modelo) ---------- */
  const SPARK = {
    generacion: "entrada generacion bruta",
    recoleccion: "cobertura recoleccion",
    disposicion: "vida util remanente",
    valorizacion: "tasa reciclaje",
    financiamiento: "presupuesto per capita",
  };
  async function sparklines() {
    const cards = document.querySelectorAll("[data-spark]");
    if (!cards.length) return;
    try {
      const niveles = [...new Set([...cards].map((c) => SPARK[c.dataset.spark]).filter(Boolean))];
      const r = await fetch("/api/series?niveles=" + encodeURIComponent(niveles.join(",")));
      const data = await r.json();
      if (!r.ok || data.error) throw new Error();
      cards.forEach((card) => {
        const serie = data.series[SPARK[card.dataset.spark]];
        const poly = card.querySelector("polyline");
        if (!serie || !poly) return;
        const vals = serie.valores.filter((v) => v !== null);
        const min = Math.min(...vals), max = Math.max(...vals), rng = max - min || 1;
        const pts = serie.valores.map((v, i) => {
          const x = (i / (serie.valores.length - 1)) * 120;
          const y = v === null ? 18 : 33 - ((v - min) / rng) * 30;
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(" ");
        poly.setAttribute("points", pts);
        poly.style.stroke = serie.color || "";
        // dibujo animado al entrar en pantalla
        requestAnimationFrame(() => {
          const len = poly.getTotalLength();
          poly.style.setProperty("--len", len);
          if (!reduced) poly.classList.add("draw");
        });
      });
    } catch (e) {
      // sin backend disponible: degradar con elegancia
      document.querySelectorAll(".lcard-spark").forEach((s) => (s.style.display = "none"));
    }
  }

  /* ---------- 5. Tilt 3D en tarjetas ---------- */
  function tilt() {
    if (reduced || matchMedia("(hover: none)").matches) return;
    document.querySelectorAll(".tilt").forEach((card) => {
      card.addEventListener("mousemove", (e) => {
        const b = card.getBoundingClientRect();
        const rx = ((e.clientY - b.top) / b.height - 0.5) * -7;
        const ry = ((e.clientX - b.left) / b.width - 0.5) * 7;
        card.style.transform = `rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg) translateY(-3px)`;
      });
      card.addEventListener("mouseleave", () => (card.style.transform = ""));
    });
  }

  /* ---------- 6. Scroll suave para anclas ---------- */
  function anchors() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const target = document.querySelector(a.getAttribute("href"));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: reduced ? "auto" : "smooth" }); }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    particles(); reveals(); counters(); sparklines(); tilt(); anchors();
  });
})();
