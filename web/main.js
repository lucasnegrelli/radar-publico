import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";

const COR = { alta: "#ff2d55", media: "#ffb300", baixa: "#00b8ff" };
const NOME_G = { alta: "Prioridade alta", media: "Prioridade média", baixa: "Prioridade baixa" };
const UF_COD = { 11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF" };
const BRASILIA = [-47.8645, -15.7997];
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------- formatação ----------
const MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const dt = (s) => { const [a, m, d] = s.split("-").map(Number); return { a, m, d }; };
const data = (s) => { const x = dt(s); return `${x.d} ${MES[x.m - 1]} ${x.a}`; };
function periodo(a, b) {
  const x = dt(a), y = dt(b);
  if (a === b) return `em ${data(a)}`;
  if (x.a === y.a && x.m === y.m) return `em ${MES[x.m - 1]} de ${x.a}`;
  if (x.a === y.a) return `entre ${MES[x.m - 1]} e ${MES[y.m - 1]} de ${x.a}`;
  return `entre ${MES[x.m - 1]} de ${x.a} e ${MES[y.m - 1]} de ${y.a}`;
}
const brl = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: v < 1000 ? 2 : 0 });
const brlCurto = (v) => v >= 1e6 ? `R$ ${(v / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi` : v >= 1e3 ? `R$ ${(v / 1e3).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mil` : brl(v);

function situacao(tipo) {
  if (/inidone/i.test(tipo)) return "declarada inidônea (impedida de contratar com o poder público)";
  if (/impedimento|proibi/i.test(tipo)) return "impedida de contratar com o poder público";
  if (/suspens/i.test(tipo)) return "suspensa de contratar com o poder público";
  return "com sanção registrada";
}
const situacaoCurta = (t) => /inidone/i.test(t) ? "Declarada inidônea" : /impedimento|proibi/i.test(t) ? "Impedida de contratar" : /suspens/i.test(t) ? "Suspensa de contratar" : "Com sanção";
function alcance(txt) {
  const t = txt.toLowerCase();
  if (t.includes("todas as esferas")) return "vale para União, estados e municípios, em qualquer Poder";
  if (t.includes("em todos os poderes")) return "vale para todos os Poderes da mesma esfera do órgão que puniu";
  if (t.includes("na esfera e no poder")) return "vale só no mesmo Poder e esfera do órgão que puniu";
  if (/^no .*rg.o/.test(t)) return "vale só no órgão que aplicou a punição";
  return "o órgão sancionador não informou o alcance";
}
const listaNome = { CEIS: "CEIS (Cadastro de Empresas Inidôneas e Suspensas)", CNEP: "CNEP (Cadastro Nacional de Empresas Punidas)" };

// ---------- mapa ----------
const map = new maplibregl.Map({
  container: "mapa", attributionControl: { compact: true },
  style: { version: 8, sources: {}, layers: [{ id: "fundo", type: "background", paint: { "background-color": "#02060a" } }] },
  bounds: [[-74, -34], [-34, 5.5]], fitBoundsOptions: { padding: { left: 60, right: 40, top: 30, bottom: 70 } },
  minZoom: 3, maxZoom: 9, dragRotate: false, pitchWithRotate: false,
});
map.touchZoomRotate.disableRotation();
const vazio = { type: "FeatureCollection", features: [] };

function curva(a, b, n = 36) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
  const c = [mx - dy * 0.22, my + dx * 0.22 * (dx >= 0 ? 1 : -1) + Math.abs(dx) * 0.05];
  return Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t;
    return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]]; });
}

let alertas = [], filtro = "todas", sel = null, rotas = [];

function montarMapa() {
  const comLocal = alertas.filter((a) => a.local);
  rotas = comLocal.map((a, k) => ({ id: a.id, g: a.gravidade, linha: curva(BRASILIA, [a.local.lon, a.local.lat]), fase: (k * 0.211) % 1 }));
  const porUF = {}; comLocal.forEach((a) => { porUF[a.local.uf] = (porUF[a.local.uf] || 0) + 1; });
  const casos = ["match", ["get", "uf"]]; Object.entries(porUF).forEach(([u, n]) => casos.push(u, n >= 3 ? "#26425e" : n === 2 ? "#1f364d" : "#192d41")); casos.push("#101a26");
  map.addSource("grade", { type: "geojson", data: grade() });
  map.addLayer({ id: "grade", type: "line", source: "grade", paint: { "line-color": "#00ffa6", "line-width": 0.5, "line-opacity": 0.09 } });
  map.addSource("ufs", { type: "geojson", data: ufGeo });
  map.addLayer({ id: "uf-fill", type: "fill", source: "ufs", paint: { "fill-color": casos } });
  map.addLayer({ id: "uf-glow", type: "line", source: "ufs", paint: { "line-color": "#00ffa6", "line-width": 5, "line-blur": 5, "line-opacity": 0.16 } });
  map.addLayer({ id: "uf-line", type: "line", source: "ufs", paint: { "line-color": "#19f0b4", "line-width": 0.9, "line-opacity": 0.55 } });
  map.addSource("rotas", { type: "geojson", data: { type: "FeatureCollection", features: rotas.map((r) => ({ type: "Feature", properties: { id: r.id, g: r.g }, geometry: { type: "LineString", coordinates: r.linha } })) } });
  const corG = ["match", ["get", "g"], "alta", COR.alta, "media", COR.media, COR.baixa];
  map.addLayer({ id: "rotas-glow", type: "line", source: "rotas", paint: { "line-color": corG, "line-width": 8, "line-blur": 7, "line-opacity": 0.45 } });
  map.addLayer({ id: "rotas", type: "line", source: "rotas", layout: { "line-cap": "round" }, paint: { "line-color": corG, "line-width": 1.8, "line-opacity": 0.9 } });
  map.addLayer({ id: "rotas-sel", type: "line", source: "rotas", filter: ["==", ["get", "id"], ""], paint: { "line-color": "#ffffff", "line-width": 3.2, "line-opacity": 1 } });
  map.addSource("pontos", { type: "geojson", data: { type: "FeatureCollection", features: comLocal.map((a) => ({ type: "Feature", properties: { id: a.id, g: a.gravidade, t: Math.min(a.total, 60000) }, geometry: { type: "Point", coordinates: [a.local.lon, a.local.lat] } })) } });
  map.addLayer({ id: "anel1", type: "circle", source: "pontos", paint: { "circle-color": "rgba(0,0,0,0)", "circle-radius": 10, "circle-stroke-color": corG, "circle-stroke-width": 1.6, "circle-stroke-opacity": 0.8 } });
  map.addLayer({ id: "anel2", type: "circle", source: "pontos", paint: { "circle-color": "rgba(0,0,0,0)", "circle-radius": 10, "circle-stroke-color": corG, "circle-stroke-width": 1.2, "circle-stroke-opacity": 0.6 } });
  map.addLayer({ id: "pulso", type: "circle", source: "pontos", paint: { "circle-color": corG, "circle-radius": 16, "circle-opacity": 0.3, "circle-blur": 0.9 } });
  map.addLayer({ id: "pontos", type: "circle", source: "pontos", paint: { "circle-color": corG, "circle-radius": ["interpolate", ["linear"], ["get", "t"], 0, 5, 60000, 12], "circle-stroke-color": "#ffffff", "circle-stroke-width": 1.4 } });
  map.addSource("cometas", { type: "geojson", data: vazio });
  map.addLayer({ id: "cometas", type: "circle", source: "cometas", paint: { "circle-color": ["case", ["==", ["get", "r"], 3.4], "#ffffff", corG], "circle-radius": ["get", "r"], "circle-opacity": ["get", "o"], "circle-blur": 0.3 } });
  const el = document.createElement("div"); el.innerHTML = '<div style="color:#00ffa6;font:700 11px ui-monospace,Consolas,monospace;letter-spacing:.14em;text-shadow:0 0 8px #00ffa6">◉ BRASÍLIA · ORIGEM</div>';
  new maplibregl.Marker({ element: el, anchor: "left" }).setLngLat(BRASILIA).addTo(map);

  map.on("click", "pontos", (e) => abrir(e.features[0].properties.id));
  map.on("click", "rotas", (e) => abrir(e.features[0].properties.id));
  ["pontos", "rotas"].forEach((l) => { map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer")); map.on("mouseleave", l, () => (map.getCanvas().style.cursor = "")); });
  const nome = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: "dica" });
  map.on("mousemove", "pontos", (e) => { const a = alertas.find((x) => x.id === e.features[0].properties.id); nome.setLngLat(e.lngLat).setHTML(`<b>${esc(a.empresa)}</b><br>${esc(a.local.cidade)}/${esc(a.local.uf)} · ${brlCurto(a.total)}`).addTo(map); });
  map.on("mouseleave", "pontos", () => nome.remove());

  const t0 = performance.now();
  const varre = $("varre"), mapaEl = $("mapa");
  const posVarre = () => { const p = map.project(BRASILIA); varre.style.left = p.x + mapaEl.offsetLeft + "px"; varre.style.top = p.y + "px"; };
  map.on("move", posVarre); posVarre();
  map.on("mousemove", (e) => { $("coords").textContent = `LAT ${e.lngLat.lat.toFixed(2)} · LON ${e.lngLat.lng.toFixed(2)}`; });
  (function quadro(t) {
    const s = (t - t0) / 1000;
    map.setPaintProperty("pulso", "circle-radius", 15 + 6 * Math.sin(s * 2.4));
    const f1 = (s / 2.4) % 1, f2 = (s / 2.4 + 0.5) % 1;
    map.setPaintProperty("anel1", "circle-radius", 8 + 34 * f1); map.setPaintProperty("anel1", "circle-stroke-opacity", 0.9 * (1 - f1));
    map.setPaintProperty("anel2", "circle-radius", 8 + 34 * f2); map.setPaintProperty("anel2", "circle-stroke-opacity", 0.9 * (1 - f2));
    const fs = [];
    rotas.forEach((r) => {
      const p = ((s / 3.2) + r.fase) % 1, n = r.linha.length - 1;
      for (let k = 0; k < 9; k++) {
        const q = p - k * 0.012; if (q < 0) continue;
        fs.push({ type: "Feature", properties: { g: r.g, r: k === 0 ? 3.4 : 2.6 - k * 0.2, o: k === 0 ? 1 : 0.65 - k * 0.07 }, geometry: { type: "Point", coordinates: r.linha[Math.floor(q * n)] } });
      }
    });
    map.getSource("cometas").setData({ type: "FeatureCollection", features: fs });
    requestAnimationFrame(quadro);
  })(t0);
}

function grade() {
  const f = [];
  for (let x = -75; x <= -30; x += 5) f.push({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [[x, -36], [x, 8]] } });
  for (let y = -35; y <= 7; y += 5) f.push({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [[-76, y], [-28, y]] } });
  return { type: "FeatureCollection", features: f };
}

// ---------- lista ----------
function lista() {
  const vis = alertas.filter((a) => filtro === "todas" || a.gravidade === filtro);
  $("itens").innerHTML = vis.map((a) => `
    <li class="card ${sel === a.id ? "sel" : ""}" style="--c:${COR[a.gravidade]}" data-id="${a.id}">
      <div class="topo"><div class="nome">${esc(a.empresa)}</div><div class="valor num">${brlCurto(a.total)}</div></div>
      <div class="sub">${situacaoCurta(a.sancao.tipo)} quando recebeu da cota parlamentar</div>
      <div class="meta"><span class="chip">${NOME_G[a.gravidade].replace("Prioridade ", "")}</span>${a.n} pagamento${a.n > 1 ? "s" : ""} · ${periodo(a.primeiro, a.ultimo).replace(/^(em|entre) /, "")}${a.local ? " · " + esc(a.local.cidade) + "/" + a.local.uf : ""}</div>
    </li>`).join("") || '<p class="sub2">Nenhum alerta neste filtro.</p>';
  $("itens").querySelectorAll(".card").forEach((c) => (c.onclick = () => abrir(c.dataset.id)));
}

// ---------- detalhe ----------
function abrir(id) {
  const a = alertas.find((x) => x.id === id); if (!a) return;
  sel = id; lista();
  if (map.getLayer("rotas-sel")) map.setFilter("rotas-sel", ["==", ["get", "id"], id]);
  const s = a.sancao, c = COR[a.gravidade];
  const linhas = a.pagamentos.map((p) => `<tr><td>${data(p.data)}</td><td><b>${esc(p.parlamentar)}</b><br><span class="sub2">${esc(p.casa)}${p.partido ? " · " + esc(p.partido) : ""}${p.uf ? "/" + esc(p.uf) : ""}</span></td><td>${esc(p.tipo.slice(0, 70))}</td><td class="v num">${brl(p.valor)}</td><td>${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">ver nota</a>` : "–"}</td></tr>`).join("");
  const vigencia = s.fim ? `de ${data(s.inicio)} até ${data(s.fim)}` : `desde ${data(s.inicio)}, sem data final`;
  $("detalhe").hidden = false; $("detalhe").style.setProperty("--c", c);
  $("detalhe").innerHTML = `
    <button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:${c}"><span>DOSSIÊ · ALVO ${esc(a.id)}</span><span class="carimbo">PONTO DE ATENÇÃO</span></div>
    <h2 style="--c:${c}">${esc(a.empresa)}</h2>
    <div class="sub2 mono">CNPJ ${esc(a.cnpj)}${a.local ? " · " + esc(a.local.cidade) + "/" + esc(a.local.uf) : ""}</div>
    <div class="manchete" style="--c:${c}"><b>${esc(a.empresa)}</b> recebeu <b>${brl(a.total)}</b> em ${a.n} pagamento${a.n > 1 ? "s" : ""} da cota parlamentar ${periodo(a.primeiro, a.ultimo)}, num período em que constava como <b>${situacao(s.tipo)}</b> no ${esc(s.lista)}.</div>
    <div class="numeros" style="--c:${c}"><div><small>Total recebido</small><b class="num">${brlCurto(a.total)}</b></div><div><small>Pagamentos</small><b class="num">${a.n}</b></div><div><small>Punição</small><b>${esc(s.lista)}</b></div></div>
    <h4>Rastro do dinheiro</h4>
    <table style="--c:${c}"><thead><tr><th>Data</th><th>Parlamentar</th><th>Gasto</th><th style="text-align:right">Valor</th><th></th></tr></thead><tbody>${linhas}</tbody></table>
    <h4>A punição</h4>
    <dl class="kv"><dt>Cadastro</dt><dd>${esc(listaNome[s.lista] || s.lista)}</dd><dt>Tipo</dt><dd>${esc(s.tipo)}</dd><dt>Aplicada por</dt><dd>${esc(s.orgao)}</dd><dt>Vigência</dt><dd>${vigencia}</dd><dt>Alcance</dt><dd>${alcance(s.alcance)}</dd></dl>
    <h4>Checagem</h4>
    <ul class="check"><li>Abra a nota de cada pagamento e veja o que foi contratado.</li><li>Veja se a punição realmente alcançava a ${esc(a.pagamentos[0].casa)} na data do pagamento (o alcance acima diz onde ela valia).</li><li>Confirme a situação atual da empresa no Portal da Transparência.</li></ul>
    <p class="aviso">Isto é um ponto de atenção feito a partir de dados públicos, não uma conclusão. Pode haver explicação legal.</p>
    <div class="links" style="margin-top:12px;font-size:12.5px">Fontes: <a href="https://portaldatransparencia.gov.br/sancoes/consulta" target="_blank" rel="noopener">Portal da Transparência (CEIS/CNEP)</a> · <a href="https://dadosabertos.camara.leg.br" target="_blank" rel="noopener">Dados Abertos da Câmara</a> · <a href="https://www12.senado.leg.br/transparencia/dados-abertos-transparencia/dados-abertos-ceaps" target="_blank" rel="noopener">Senado (CEAPS)</a></div>`;
  $("detalhe").querySelector(".fechar").onclick = fechar;
  if (a.local) map.flyTo({ center: [a.local.lon + 1.6, a.local.lat], zoom: 5.4, duration: 1200 });
}
function fechar() { $("detalhe").hidden = true; sel = null; lista(); map.setFilter("rotas-sel", ["==", ["get", "id"], ""]); map.fitBounds([[-74, -34], [-34, 5.5]], { padding: { left: 60, right: 40, top: 30, bottom: 70 }, duration: 900 }); }

// ---------- abas ----------
$("abas").onclick = (e) => { const b = e.target.closest("button"); if (!b) return;
  [...$("abas").children].forEach((x) => x.classList.toggle("on", x === b));
  document.querySelectorAll(".aba").forEach((x) => x.classList.toggle("on", x.id === "aba-" + b.dataset.aba)); };
$("filtros").onclick = (e) => { const b = e.target.closest("button"); if (!b) return; filtro = b.dataset.g;
  [...$("filtros").children].forEach((x) => x.classList.toggle("on", x === b)); lista(); };

$("aba-risco").innerHTML = `
  <h3>Risco financeiro <span class="tag">em construção</span></h3>
  <p>Este módulo procura o que não aparece em contratos: dinheiro público e de aposentados concentrado em poucos emissores, bancos crescendo rápido demais e fundos que se pagam entre si. É o tipo de sinal que antecede um colapso como o do Banco Master.</p>
  <div class="caixa"><b>1. Previdência de servidores concentrada</b><p>Quanto da carteira de cada fundo de previdência municipal ou estadual (RPPS) está num único emissor. Fonte: CADPREV / Previdência.</p></div>
  <div class="caixa"><b>2. Banco crescendo fora da curva</b><p>Captação e ativos que dobram em poucos trimestres, com rendimento muito acima do mercado. Fonte: Banco Central (IF.data).</p></div>
  <div class="caixa"><b>3. Rede de fundos e empresas</b><p>Fundos que investem uns nos outros e terminam numa empresa recém-criada. Fonte: CVM e CNPJ da Receita.</p></div>`;
$("aba-sobre").innerHTML = `
  <h3>Como ler este painel</h3>
  <div class="caixa"><b>O que é um alerta</b><p>Um cruzamento automático de bases públicas que encontrou algo fora do esperado. É um ponto de atenção para conferir, não uma acusação.</p></div>
  <div class="caixa"><b>Prioridade</b><p><span class="chip" style="--c:${COR.alta}">alta</span> a punição valia em todo o governo. <span class="chip" style="--c:${COR.media}">média</span> o alcance da punição não foi informado. <span class="chip" style="--c:${COR.baixa}">baixa</span> a punição valia só no órgão que a aplicou.</p></div>
  <div class="caixa"><b>De onde vêm os dados</b><p>Portal da Transparência, Câmara, Senado, TSE, Receita Federal e PNCP. Tudo aberto e público. Cada alerta traz o link da fonte.</p></div>
  <div class="caixa"><b>Inspiração e créditos</b><p>Operação Serenata de Amor e Querido Diário (Open Knowledge Brasil), ambos de código aberto.</p></div>`;

// ---------- carga ----------
const [dA, dN, ufGeo] = await Promise.all([
  fetch("/data/alertas.json").then((r) => r.json()).catch(() => ({ alertas: [] })),
  fetch("/data/noticias.json").then((r) => r.json()).catch(() => ({ itens: [] })),
  fetch("/data/uf.geojson").then((r) => r.json()),
]);
ufGeo.features.forEach((f) => { f.properties.uf = UF_COD[Number(f.properties.codarea)]; });
const ord = { alta: 0, media: 1, baixa: 2 };
alertas = dA.alertas.sort((a, b) => ord[a.gravidade] - ord[b.gravidade] || b.total - a.total);
const total = alertas.reduce((s, a) => s + a.total, 0);
$("resumo").innerHTML = `<span><b class="num">${alertas.length}</b>alertas</span><span><b class="num">${brlCurto(total)}</b>envolvidos</span><span><b class="num">${dA.gerado ? data(dA.gerado) : "–"}</b>atualizado</span>`;
lista();
{
  const altas = alertas.filter((a) => a.gravidade === "alta").length;
  const n = altas === 0 ? 5 : altas < 5 ? 4 : altas < 15 ? 3 : altas < 40 ? 2 : 1;
  const cor = { 5: "#00ffa6", 4: "#00b8ff", 3: "#ffb300", 2: "#ff7a1a", 1: "#ff2d55" }[n];
  const txt = { 5: "NORMAL", 4: "ATENÇÃO", 3: "ELEVADO", 2: "ALTO", 1: "CRÍTICO" }[n];
  $("ameaca").style.setProperty("--c", cor);
  $("ameaca").innerHTML = `<div><small>Nível de ameaça</small><span>${txt}</span></div><b>${n}</b>`;
}
$("aba-noticias").innerHTML = `<h3>Notícias</h3><p class="sub2">Manchetes recentes sobre gasto público, fraude e fiscalização.</p><ul class="news">${dN.itens.map((n) => `<li><a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.titulo)}</a><small>${esc(n.fonte)}</small></li>`).join("") || "<li class='sub2'>Sem notícias carregadas.</li>"}</ul>`;
if (map.loaded()) montarMapa(); else map.on("load", montarMapa);
