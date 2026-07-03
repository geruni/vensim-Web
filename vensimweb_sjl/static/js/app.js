/* Panel de análisis - Residuos Sólidos SJL
   Controla selección de niveles, superposición, comparación real vs simulado,
   ratios, KPIs, exportación CSV y escenarios guardados. Gráficos con Plotly. */
(function () {
  "use strict";
  const CFG = window.__CFG__;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  const PLOT_FONT = { family: "-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif", color: "#241D14" };
  const GRID = "#EDE4D3";
  let ultimoDataset = null; // para exportar CSV
  let PALANCAS = [];        // definición de sliders what-if (desde /api/palancas)

  // ---------- palancas what-if ----------
  const fmtPalanca = (p, v) => {
    if (p.max >= 1e6) return (v / 1e6).toFixed(0) + " M";
    if (p.paso < 1) return (+v).toFixed(String(p.paso).split(".")[1]?.length || 2);
    return String(v);
  };

  function paramsActuales() {
    const out = {};
    $$("#lista-palancas input[type=range]").forEach((s) => {
      const p = PALANCAS.find((x) => x.nombre === s.dataset.nombre);
      if (p && +s.value !== p.defecto) out[p.nombre] = +s.value;
    });
    return out;
  }
  const hayWhatIf = () => Object.keys(paramsActuales()).length > 0;
  const paramsQS = () => {
    const p = paramsActuales();
    return Object.keys(p).length ? "&params=" + encodeURIComponent(JSON.stringify(p)) : "";
  };

  function actualizarBadgeWhatIf() {
    $("#whatif-badge").classList.toggle("hidden", !hayWhatIf());
  }

  let debounceTimer;
  function construirPalancas() {
    const cont = $("#lista-palancas");
    api("/api/palancas").then((defs) => {
      PALANCAS = defs;
      cont.innerHTML = "";
      defs.forEach((p) => {
        const row = document.createElement("div");
        row.className = "palanca";
        row.innerHTML =
          `<div class="palanca-head"><span class="palanca-nombre">${p.etiqueta}</span>` +
          `<span class="palanca-valor" id="pv-${p.nombre.replace(/\s+/g, "_")}">${fmtPalanca(p, p.defecto)}</span></div>` +
          `<input type="range" min="${p.min}" max="${p.max}" step="${p.paso}" value="${p.defecto}" data-nombre="${p.nombre}">` +
          `<div class="palanca-meta"><span>${p.subsistema}</span><span>${p.unidad}</span></div>`;
        cont.appendChild(row);
        const slider = $("input", row);
        slider.addEventListener("input", () => {
          $(`#pv-${p.nombre.replace(/\s+/g, "_")}`).textContent = fmtPalanca(p, slider.value);
          row.classList.toggle("modificada", +slider.value !== p.defecto);
          actualizarBadgeWhatIf();
          clearTimeout(debounceTimer);
          debounceTimer = setTimeout(render, 420);
        });
      });
    }).catch(() => {
      cont.innerHTML = '<p class="muted">No se pudieron cargar las palancas.</p>';
    });
    $("#palancas-reset").addEventListener("click", () => {
      $$("#lista-palancas input[type=range]").forEach((s) => {
        const p = PALANCAS.find((x) => x.nombre === s.dataset.nombre);
        if (!p) return;
        s.value = p.defecto;
        $(`#pv-${p.nombre.replace(/\s+/g, "_")}`).textContent = fmtPalanca(p, p.defecto);
        s.closest(".palanca").classList.remove("modificada");
      });
      actualizarBadgeWhatIf();
      render();
    });
    $("#ver-base").addEventListener("change", () => hayWhatIf() && render());
  }

  // ---------- utilidades ----------
  const fmt = (v) => {
    if (v === null || v === undefined || Number.isNaN(v)) return "—";
    const a = Math.abs(v);
    if (a !== 0 && a < 0.01) return v.toExponential(2);
    if (a >= 1e6) return (v / 1e6).toFixed(2) + " M";
    if (a >= 1e3) return v.toLocaleString("es-PE", { maximumFractionDigits: 0 });
    return v.toLocaleString("es-PE", { maximumFractionDigits: 2 });
  };

  function toast(msg, tipo) {
    const t = $("#toast");
    t.textContent = msg;
    t.className = "toast " + (tipo || "");
    setTimeout(() => (t.className = "toast hidden"), 3200);
  }

  async function api(url, opts) {
    const r = await fetch(url, opts);
    const j = await r.json().catch(() => ({ error: "Respuesta no válida del servidor." }));
    if (!r.ok || j.error) throw new Error(j.error || "Error " + r.status);
    return j;
  }

  // ---------- construir sidebar ----------
  function construirNiveles() {
    const cont = $("#lista-niveles");
    const grupos = {};
    CFG.niveles.forEach((n) => {
      (grupos[n.grupo || "Otros"] = grupos[n.grupo || "Otros"] || []).push(n);
    });
    cont.innerHTML = "";
    Object.keys(grupos).forEach((g) => {
      const h = document.createElement("div");
      h.className = "nivel-grupo";
      h.textContent = g;
      cont.appendChild(h);
      grupos[g].forEach((n, i) => {
        const id = "niv-" + n.nivel.replace(/\s+/g, "_");
        const row = document.createElement("label");
        row.className = "nivel-item";
        row.innerHTML =
          `<input type="checkbox" value="${n.nivel}" id="${id}">` +
          `<span class="dot" style="background:${n.color}"></span>` +
          `<span class="nivel-nombre">${n.titulo}</span>` +
          `<span class="nivel-unidad">${n.unidad || ""}</span>`;
        cont.appendChild(row);
      });
    });
    // Seleccionar el primer nivel (indicador) por defecto
    const first = $('input[type=checkbox]', cont);
    if (first) first.checked = true;
  }

  function construirRatioSelects() {
    const a = $("#ratio-a"), b = $("#ratio-b");
    CFG.catalogo
      .sort((x, y) => x.titulo.localeCompare(y.titulo))
      .forEach((c) => {
        const label = `${c.titulo} (${c.unidad || "—"})`;
        a.appendChild(new Option(label, c.nivel));
        b.appendChild(new Option(label, c.nivel));
      });
    // Defecto sugerido: un flujo sobre población
    const flota = CFG.catalogo.find((c) => c.nivel === "Flota operativa");
    const pob = CFG.catalogo.find((c) => c.nivel === "Poblacion");
    if (flota) a.value = flota.nivel;
    if (pob) b.value = pob.nivel;
  }

  const nivelesSeleccionados = () =>
    $$("#lista-niveles input:checked").map((c) => c.value);

  const metaDe = (nivel) => CFG.niveles.find((n) => n.nivel === nivel) || {};

  // ---------- KPIs ----------
  function pintarKPIs(years, series) {
    const cont = $("#kpis");
    cont.innerHTML = "";
    const claves = Object.keys(series).slice(0, 4);
    if (!claves.length) return;
    claves.forEach((nivel) => {
      const vals = series[nivel].valores || series[nivel].simulado || series[nivel];
      const meta = metaDe(nivel);
      const ini = vals[0], fin = vals[vals.length - 1];
      const cambio = ini ? ((fin - ini) / Math.abs(ini)) * 100 : null;
      const signo = cambio === null ? "" : cambio >= 0 ? "up" : "down";
      const flecha = cambio === null ? "" : cambio >= 0 ? "▲" : "▼";
      const card = document.createElement("div");
      card.className = "kpi";
      card.innerHTML =
        `<div class="kpi-top"><span class="dot" style="background:${meta.color || "#2F7A6E"}"></span>` +
        `<span class="kpi-name">${(series[nivel].titulo) || meta.titulo || nivel}</span></div>` +
        `<div class="kpi-val">${fmt(fin)} <span class="kpi-unit">${meta.unidad || ""}</span></div>` +
        `<div class="kpi-foot ${signo}">${flecha} ${cambio === null ? "—" : Math.abs(cambio).toFixed(1) + "% vs 2019"}</div>`;
      cont.appendChild(card);
    });
  }

  // ---------- render: SUPERPONER ----------
  const normalizar = (vals) => {
    const base = vals.find((v) => v !== null && v !== 0);
    return vals.map((v) => (v === null || !base ? null : (v / base) * 100));
  };

  async function renderSuperponer() {
    const niveles = nivelesSeleccionados();
    if (!niveles.length) { toast("Selecciona al menos un nivel.", "warn"); return; }
    const norm = $("#normalizar").checked;
    const whatif = hayWhatIf();
    const q = encodeURIComponent(niveles.join(","));
    const data = await api("/api/series?niveles=" + q + paramsQS());
    ultimoDataset = { tipo: "series", years: data.years, series: data.series };

    const traces = Object.keys(data.series).map((nivel) => {
      const s = data.series[nivel];
      const y = norm ? normalizar(s.valores) : s.valores;
      return {
        x: data.years, y, name: s.titulo + (whatif ? " (what-if)" : ""), mode: "lines",
        line: { color: s.color, width: 2.5, shape: "spline" },
        hovertemplate: `<b>${s.titulo}</b><br>%{x}: %{y:.2f} ${norm ? "" : s.unidad}<extra></extra>`,
      };
    });

    // corrida base punteada para dimensionar el efecto de las palancas
    if (whatif && $("#ver-base").checked) {
      const base = await api("/api/series?niveles=" + q);
      Object.keys(base.series).forEach((nivel) => {
        const s = base.series[nivel];
        traces.push({
          x: base.years, y: norm ? normalizar(s.valores) : s.valores,
          name: s.titulo + " (base)", mode: "lines",
          line: { color: s.color, width: 1.6, dash: "dot" }, opacity: 0.55,
          hovertemplate: `%{x}: %{y:.2f}<extra>${s.titulo} base</extra>`,
        });
      });
    }

    const yTitle = norm ? "Índice (2019 = 100)" : unidadComun(data.series);
    dibujar(traces, `Evolución — ${CFG.subsistemaNombre}`, yTitle);
    pintarKPIs(data.years, data.series);
    ocultarTabla();
    $("#chart-hint").textContent = whatif ? "Escenario what-if activo" : (norm ? "Normalizado base 100" : "Valores absolutos");
    await superponerEscenarioActivo(traces, norm);
  }

  function unidadComun(series) {
    const us = [...new Set(Object.values(series).map((s) => s.unidad))];
    return us.length === 1 ? us[0] : "Valor (unidades mixtas)";
  }

  // ---------- render: COMPARAR real vs simulado ----------
  async function renderComparar() {
    const niveles = nivelesSeleccionados();
    if (!niveles.length) { toast("Selecciona al menos un nivel.", "warn"); return; }
    const data = await api(`/api/comparar?subsistema=${CFG.subsistema}&niveles=${encodeURIComponent(niveles.join(","))}` + paramsQS());
    ultimoDataset = { tipo: "comparar", years: data.years, series: data.series };

    const traces = [];
    Object.keys(data.series).forEach((nivel) => {
      const s = data.series[nivel];
      traces.push({
        x: data.years, y: s.simulado, name: s.titulo + " (sim.)", mode: "lines",
        line: { color: s.color, width: 2.5 },
        hovertemplate: `%{x}: %{y:.2f} ${s.unidad}<extra>${s.titulo} sim.</extra>`,
      });
      traces.push({
        x: data.years, y: s.real, name: s.titulo + " (real)", mode: "markers",
        marker: { color: s.color, size: 9, symbol: "circle-open", line: { width: 2.5 } },
        hovertemplate: `%{x}: %{y:.2f} ${s.unidad}<extra>${s.titulo} real</extra>`,
      });
    });
    dibujar(traces, `Real vs Simulado — ${CFG.subsistemaNombre}`, unidadComun(data.series));
    pintarKPIs(data.years, data.series);
    tablaComparacion(data);
    $("#chart-hint").textContent = "Puntos = dato real observado";
  }

  function tablaComparacion(data) {
    const card = $("#tabla-card"); card.classList.remove("hidden");
    const t = $("#tabla-comp");
    const niveles = Object.keys(data.series);
    // años con al menos un real
    const anios = data.years.filter((y, i) => niveles.some((n) => data.series[n].real[i] !== null));
    let html = "<thead><tr><th>Nivel</th>";
    anios.forEach((y) => (html += `<th colspan="3">${y}</th>`));
    html += "<th>MAPE</th></tr><tr><th></th>";
    anios.forEach(() => (html += "<th>real</th><th>sim</th><th>Δ%</th>"));
    html += "<th></th></tr></thead><tbody>";
    niveles.forEach((n) => {
      const s = data.series[n];
      html += `<tr><td class="td-nivel"><span class="dot" style="background:${s.color}"></span>${s.titulo}</td>`;
      anios.forEach((y) => {
        const i = data.years.indexOf(y);
        const r = s.real[i], sim = s.simulado[i];
        const dpct = (r !== null && sim !== null && r !== 0) ? ((sim - r) / Math.abs(r)) * 100 : null;
        const cls = dpct === null ? "" : Math.abs(dpct) <= 10 ? "ok" : Math.abs(dpct) <= 25 ? "warn" : "bad";
        html += `<td>${fmt(r)}</td><td>${fmt(sim)}</td><td class="${cls}">${dpct === null ? "—" : (dpct >= 0 ? "+" : "") + dpct.toFixed(1)}</td>`;
      });
      const mapeCls = s.mape === null ? "" : s.mape <= 10 ? "ok" : s.mape <= 25 ? "warn" : "bad";
      html += `<td class="mape ${mapeCls}">${s.mape === null ? "—" : s.mape + "%"}</td></tr>`;
    });
    html += "</tbody>";
    t.innerHTML = html;
  }

  // ---------- render: RATIO ----------
  async function renderRatio() {
    const a = $("#ratio-a").value, b = $("#ratio-b").value;
    if (a === b) { toast("Elige dos variables distintas.", "warn"); return; }
    const data = await api(`/api/ratio?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}` + paramsQS());
    ultimoDataset = { tipo: "ratio", years: data.years, valores: data.valores, etiqueta: data.etiqueta };
    const trace = {
      x: data.years, y: data.valores, name: data.etiqueta, mode: "lines",
      line: { color: "#6F5BA8", width: 3, shape: "spline" }, fill: "tozeroy",
      fillcolor: "rgba(111,91,168,0.08)",
      hovertemplate: `%{x}: %{y:.4f}<extra></extra>`,
    };
    dibujar([trace], "Ratio en el tiempo", `${data.unidad_a || ""} / ${data.unidad_b || ""}`);
    const vals = data.valores.filter((v) => v !== null);
    pintarKPIsRatio(data);
    ocultarTabla();
    $("#chart-hint").textContent = data.etiqueta;
  }

  function pintarKPIsRatio(data) {
    const cont = $("#kpis"); cont.innerHTML = "";
    const vals = data.valores.filter((v) => v !== null);
    const ini = vals[0], fin = vals[vals.length - 1];
    const max = Math.max(...vals), min = Math.min(...vals);
    const tarjetas = [
      ["Ratio 2019", ini], ["Ratio 2040", fin], ["Máximo", max], ["Mínimo", min],
    ];
    tarjetas.forEach(([t, v]) => {
      const c = document.createElement("div");
      c.className = "kpi";
      c.innerHTML = `<div class="kpi-top"><span class="kpi-name">${t}</span></div><div class="kpi-val">${fmt(v)}</div>`;
      cont.appendChild(c);
    });
  }

  // ---------- Plotly ----------
  function dibujar(traces, titulo, yTitle) {
    $("#chart-title").textContent = titulo;
    const layout = {
      margin: { l: 64, r: 24, t: 12, b: 48 },
      font: PLOT_FONT,
      paper_bgcolor: "white",
      plot_bgcolor: "white",
      hovermode: "x unified",
      legend: { orientation: "h", y: -0.2, font: { size: 11 } },
      xaxis: { title: "Año", gridcolor: GRID, zeroline: false, dtick: 2 },
      yaxis: { title: yTitle, gridcolor: GRID, zeroline: false },
    };
    Plotly.react("chart", traces, layout, {
      responsive: true, displaylogo: false,
      modeBarButtonsToRemove: ["lasso2d", "select2d"],
      toImageButtonOptions: { format: "png", filename: "residuos_sjl_" + CFG.subsistema, scale: 2 },
    });
  }

  const ocultarTabla = () => $("#tabla-card").classList.add("hidden");

  // ---------- escenarios guardados ----------
  let escenarioActivo = null;
  async function cargarEscenarios() {
    const cont = $("#lista-escenarios");
    try {
      const lista = await api("/api/escenarios");
      if (!lista.length) { cont.innerHTML = '<p class="muted">Aún no hay escenarios guardados.</p>'; return; }
      cont.innerHTML = "";
      lista.forEach((e) => {
        const el = document.createElement("div");
        el.className = "escenario";
        const gear = e.parametros ? ' <span class="esc-gear" title="Escenario con palancas modificadas">⚙</span>' : "";
        el.innerHTML =
          `<button class="esc-load" data-id="${e.id}">${e.nombre}${gear}</button>` +
          `<span class="esc-fecha">${(e.creado || "").slice(0, 10)}</span>`;
        cont.appendChild(el);
      });
      $$(".esc-load", cont).forEach((b) =>
        b.addEventListener("click", () => activarEscenario(b.dataset.id, b.textContent)));
    } catch (e) {
      cont.innerHTML = '<p class="muted">No se pudieron cargar los escenarios.</p>';
    }
  }

  async function activarEscenario(id, nombre) {
    try {
      const data = await api("/api/escenario/" + id);
      escenarioActivo = { id, nombre, data };
      toast(`Escenario "${nombre}" superpuesto (línea punteada).`, "ok");
      render();
    } catch (e) { toast(e.message, "warn"); }
  }

  async function superponerEscenarioActivo(traces, norm) {
    if (!escenarioActivo) return;
    const d = escenarioActivo.data;
    const extra = [];
    Object.keys(d.series).forEach((nivel) => {
      if (!nivelesSeleccionados().includes(nivel)) return;
      let y = d.series[nivel];
      if (norm) { const base = y.find((v) => v); y = y.map((v) => (v && base ? (v / base) * 100 : null)); }
      extra.push({
        x: d.years, y, name: (metaDe(nivel).titulo || nivel) + " · " + escenarioActivo.nombre,
        mode: "lines", line: { color: "#9C9181", width: 2, dash: "dot" },
        hovertemplate: `%{x}: %{y:.2f}<extra>${escenarioActivo.nombre}</extra>`,
      });
    });
    if (extra.length) Plotly.addTraces("chart", extra);
  }

  // ---------- guardar / exportar ----------
  async function guardarEscenario() {
    const niveles = nivelesSeleccionados();
    if (!niveles.length) { toast("Selecciona niveles para guardar.", "warn"); return; }
    const sugerido = (hayWhatIf() ? "What-if " : "Escenario base ") + CFG.subsistemaNombre;
    const nombre = prompt("Nombre del escenario:", sugerido);
    if (!nombre) return;
    try {
      await api("/api/guardar", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre, descripcion: "Subsistema " + CFG.subsistemaNombre,
          niveles, params: paramsActuales(),
        }),
      });
      toast("Escenario guardado en la base de datos.", "ok");
      cargarEscenarios();
    } catch (e) { toast(e.message, "warn"); }
  }

  function exportarCSV() {
    if (!ultimoDataset) { toast("Primero genera un gráfico.", "warn"); return; }
    const d = ultimoDataset;
    let filas = [];
    if (d.tipo === "ratio") {
      filas.push(["anio", "ratio"]);
      d.years.forEach((y, i) => filas.push([y, d.valores[i]]));
    } else {
      const niveles = Object.keys(d.series);
      const cols = ["anio"];
      niveles.forEach((n) => {
        cols.push(d.series[n].titulo + " (sim)");
        if (d.tipo === "comparar") cols.push(d.series[n].titulo + " (real)");
      });
      filas.push(cols);
      d.years.forEach((y, i) => {
        const row = [y];
        niveles.forEach((n) => {
          row.push(d.series[n].simulado ? d.series[n].simulado[i] : d.series[n].valores[i]);
          if (d.tipo === "comparar") row.push(d.series[n].real[i]);
        });
        filas.push(row);
      });
    }
    const csv = filas.map((r) => r.map((c) => (c === null || c === undefined ? "" : c)).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `residuos_sjl_${CFG.subsistema}_${d.tipo}.csv`;
    a.click();
    toast("CSV descargado.", "ok");
  }

  // ---------- modos ----------
  function modoActual() { return $('input[name=modo]:checked').value; }
  function aplicarModo() {
    const m = modoActual();
    $("#bloque-niveles").classList.toggle("hidden", m === "ratio");
    $("#bloque-ratio").classList.toggle("hidden", m !== "ratio");
  }

  async function render() {
    const btn = $("#btn-graficar");
    btn.disabled = true; btn.textContent = "Calculando…";
    try {
      const m = modoActual();
      if (m === "superponer") await renderSuperponer();
      else if (m === "comparar") await renderComparar();
      else await renderRatio();
    } catch (e) {
      toast(e.message || "Error al generar el gráfico.", "warn");
    } finally {
      btn.disabled = false; btn.textContent = "Actualizar gráfico";
    }
  }

  // ---------- init ----------
  function init() {
    construirNiveles();
    construirRatioSelects();
    construirPalancas();
    aplicarModo();
    $$('input[name=modo]').forEach((r) => r.addEventListener("change", () => { aplicarModo(); render(); }));
    $("#btn-graficar").addEventListener("click", render);
    $("#btn-csv").addEventListener("click", exportarCSV);
    $("#btn-guardar").addEventListener("click", guardarEscenario);
    $("#normalizar").addEventListener("change", () => modoActual() === "superponer" && render());
    $("#sel-todos").addEventListener("click", () => { $$("#lista-niveles input").forEach((c) => (c.checked = true)); render(); });
    $("#sel-ninguno").addEventListener("click", () => { $$("#lista-niveles input").forEach((c) => (c.checked = false)); });
    $("#ratio-a").addEventListener("change", () => modoActual() === "ratio" && render());
    $("#ratio-b").addEventListener("change", () => modoActual() === "ratio" && render());
    cargarEscenarios();
    render();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
