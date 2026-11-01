import "cesium/Build/Cesium/Widgets/widgets.css";
import * as Cesium from "cesium";

Cesium.Ion.defaultAccessToken = ""; // não usamos Cesium ion: mapa-base gratuito (Esri Dark Gray)

const COR = { alta: "#ff3b3b", media: "#ffb020", baixa: "#4cc9f0" };
const ROTULO = { alta: "alta", media: "média", baixa: "baixa" };
const $ = (id) => document.getElementById(id);
const brl = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });

const viewer = new Cesium.Viewer("globe", {
  baseLayer: new Cesium.ImageryLayer(new Cesium.UrlTemplateImageryProvider({
    url: "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    credit: "Esri, HERE, Garmin, © OpenStreetMap contributors", maximumLevel: 16,
  })),
  baseLayerPicker: false, geocoder: false, homeButton: false, sceneModePicker: false,
  navigationHelpButton: false, animation: false, timeline: false, fullscreenButton: false,
  infoBox: false, selectionIndicator: false, requestRenderMode: false,
});
const sc = viewer.scene;
sc.backgroundColor = Cesium.Color.fromCssColorString("#05080d");
sc.globe.baseColor = Cesium.Color.fromCssColorString("#07101a");
sc.globe.enableLighting = false;
sc.skyAtmosphere.hueShift = -0.05; sc.skyAtmosphere.brightnessShift = -0.3;
sc.globe.atmosphereBrightnessShift = -0.25;
viewer.clock.shouldAnimate = true;

const BR = { lon: -52, lat: -14.5 };
const olharBrasil = (dur = 3) => viewer.camera.flyToBoundingSphere(
  new Cesium.BoundingSphere(Cesium.Cartesian3.fromDegrees(BR.lon, BR.lat, 0), 2400000),
  { offset: new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-62), 7800000), duration: dur });
olharBrasil(0);

// ---------- geometria dos arcos ----------
function arco(o, d, n = 80) {
  const dist = Math.hypot(d.lon - o.lon, d.lat - o.lat);
  const alt = Math.max(60000, dist * 55000);
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n;
    pts.push(Cesium.Cartesian3.fromDegrees(o.lon + (d.lon - o.lon) * t, o.lat + (d.lat - o.lat) * t, Math.sin(Math.PI * t) * alt));
  }
  return pts;
}
const emArco = (pts, t) => pts[Math.min(pts.length - 1, Math.floor(t * (pts.length - 1)))];

// ---------- estado ----------
let alertas = [], filtro = "todas", selecionado = null;
const porId = new Map();

function desenhar() {
  viewer.entities.removeAll(); porId.clear();
  alertas.filter((a) => a.destino).forEach((a, k) => {
    const cor = Cesium.Color.fromCssColorString(COR[a.gravidade]);
    const pts = arco(a.origem, a.destino);
    const fase = (k * 0.173) % 1;
    const larg = Math.min(6, 1.5 + Math.log10(Math.max(a.valor, 10)) * 0.7);
    viewer.entities.add({ id: a.id + "-arco", polyline: { positions: pts, width: larg,
      material: new Cesium.PolylineGlowMaterialProperty({ glowPower: 0.22, color: cor.withAlpha(0.8) }) } });
    viewer.entities.add({ id: a.id + "-cometa", position: new Cesium.CallbackProperty(() =>
      emArco(pts, ((Date.now() / 2800) + fase) % 1), false),
      point: { pixelSize: 6, color: Cesium.Color.WHITE, outlineColor: cor, outlineWidth: 3 } });
    viewer.entities.add({ id: a.id, position: Cesium.Cartesian3.fromDegrees(a.destino.lon, a.destino.lat, 0),
      point: { pixelSize: new Cesium.CallbackProperty(() => 9 + 4 * Math.sin(Date.now() / 380 + k), false),
        color: cor, outlineColor: cor.withAlpha(0.35), outlineWidth: 8, disableDepthTestDistance: Number.POSITIVE_INFINITY },
      label: { text: a.destino.nome, font: "11px monospace", fillColor: Cesium.Color.fromCssColorString("#cfe3f3"),
        pixelOffset: new Cesium.Cartesian2(0, -18), showBackground: true, backgroundColor: Cesium.Color.fromCssColorString("#05080d").withAlpha(0.7),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 2500000), disableDepthTestDistance: Number.POSITIVE_INFINITY } });
    porId.set(a.id, a);
  });
  viewer.entities.add({ position: Cesium.Cartesian3.fromDegrees(-47.8645, -15.7997, 0),
    point: { pixelSize: 10, color: Cesium.Color.fromCssColorString("#35e0a1"), outlineColor: Cesium.Color.fromCssColorString("#35e0a1").withAlpha(0.3), outlineWidth: 8 },
    label: { text: "BRASÍLIA", font: "11px monospace", fillColor: Cesium.Color.fromCssColorString("#35e0a1"), pixelOffset: new Cesium.Cartesian2(0, -18) } });
}

function lista() {
  const ul = $("itens"); ul.innerHTML = "";
  const vis = alertas.filter((a) => filtro === "todas" || a.gravidade === filtro);
  $("contagem").textContent = `(${vis.length})`;
  vis.forEach((a) => {
    const li = document.createElement("li");
    li.style.setProperty("--c", COR[a.gravidade]);
    if (selecionado === a.id) li.classList.add("sel");
    li.innerHTML = `<div class="t">${a.titulo}</div><div class="m">${ROTULO[a.gravidade].toUpperCase()} · ${brl(a.valor)}${a.destino ? " · " + a.destino.nome + "/" + a.destino.uf : ""}</div>`;
    li.onclick = () => abrir(a.id);
    ul.appendChild(li);
  });
}

function abrir(id) {
  const a = alertas.find((x) => x.id === id); if (!a) return;
  selecionado = id; lista();
  const c = COR[a.gravidade];
  $("detalhe").style.setProperty("--c", c); $("detalhe").hidden = false;
  $("d-grav").textContent = "gravidade " + ROTULO[a.gravidade];
  $("d-titulo").textContent = a.titulo; $("d-texto").textContent = a.explicacao;
  $("d-valor").textContent = brl(a.valor);
  $("d-periodo").textContent = a.inicio === a.fim ? a.inicio : `${a.inicio} a ${a.fim}`;
  $("d-destino").textContent = a.destino ? `${a.destino.nome}/${a.destino.uf}` : "não localizado";
  $("d-fonte").textContent = a.fonte;
  if (a.destino) viewer.camera.flyTo({ destination: Cesium.Cartesian3.fromDegrees(a.destino.lon, a.destino.lat - 3.2, 900000),
    orientation: { heading: 0, pitch: Cesium.Math.toRadians(-40), roll: 0 }, duration: 2 });
}
$("fechar").onclick = () => { $("detalhe").hidden = true; selecionado = null; lista(); olharBrasil(2); };
$("filtros").onclick = (e) => { const b = e.target.closest("button"); if (!b) return;
  filtro = b.dataset.g; [...$("filtros").children].forEach((x) => x.classList.toggle("on", x === b)); lista(); };

new Cesium.ScreenSpaceEventHandler(viewer.canvas).setInputAction((m) => {
  const p = sc.pick(m.position);
  if (p && p.id && p.id.id) { const id = String(p.id.id).replace(/-(arco|cometa)$/, ""); if (porId.has(id)) abrir(id); }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

// ---------- nível de atenção (estilo DEFCON, 5 calmo ... 1 crítico) ----------
function nivel() {
  const altas = alertas.filter((a) => a.gravidade === "alta").length;
  const n = altas === 0 ? 5 : altas < 5 ? 4 : altas < 15 ? 3 : altas < 40 ? 2 : 1;
  const cores = { 5: "#35e0a1", 4: "#4cc9f0", 3: "#ffb020", 2: "#ff7a1a", 1: "#ff3b3b" };
  const txt = { 5: "NORMAL", 4: "ATENÇÃO", 3: "ELEVADO", 2: "ALTO", 1: "CRÍTICO" };
  $("nivel").style.setProperty("--c", cores[n]); $("nivel-n").textContent = n; $("nivel-t").textContent = txt[n];
}

setInterval(() => { $("relogio").textContent = new Date().toLocaleTimeString("pt-BR", { timeZone: "America/Sao_Paulo" }); }, 1000);

// ---------- carga ----------
const [dadosA, dadosN] = await Promise.all([
  fetch("/data/alertas.json").then((r) => r.json()).catch(() => ({ alertas: [] })),
  fetch("/data/noticias.json").then((r) => r.json()).catch(() => ({ itens: [] })),
]);
alertas = dadosA.alertas.sort((a, b) => ({ alta: 0, media: 1, baixa: 2 }[a.gravidade] - { alta: 0, media: 1, baixa: 2 }[b.gravidade]) || b.valor - a.valor);
desenhar(); lista(); nivel(); olharBrasil(3);
$("faixa-txt").innerHTML = (dadosN.itens.length
  ? dadosN.itens.map((n) => `<span>◆ <a href="${n.url}" target="_blank" rel="noopener">${n.titulo}</a> <i>(${n.fonte})</i></span>`).join("")
  : "<span>◆ Sem notícias carregadas. Rode ingestao/noticias.py</span>");
