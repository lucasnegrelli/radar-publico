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
const brlCurto = (v) => v >= 1e9 ? `R$ ${(v / 1e9).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} bi` : v >= 1e6 ? `R$ ${(v / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mi` : v >= 1e3 ? `R$ ${(v / 1e3).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} mil` : brl(v);
const plural = (n, a, b) => `${n} ${n === 1 ? a : b}`;

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
const QUALIF = { "49": "sócio-administrador", "22": "sócio", "05": "administrador", "10": "diretor", "16": "presidente", "65": "titular (empresário individual)", "28": "sócio-gerente", "08": "conselheiro" };
const PORTE = { "00": "não informado", "01": "microempresa", "03": "empresa de pequeno porte", "05": "demais (médio/grande porte)" };

// ---------- textos por regra ----------
function manchete(a) {
  const m = a.manchete, E = `<b>${esc(a.empresa)}</b>`;
  if (m.tipo === "R01") return `${E} recebeu <b>${brl(a.total)}</b> em ${plural(a.n, "pagamento", "pagamentos")} da cota parlamentar ${periodo(a.inicio, a.fim)}, num período em que constava como <b>${situacao(m.sancao)}</b> no ${esc(m.lista)}.`;
  if (m.tipo === "R02") return `${E} assinou ${plural(a.n, "contrato público", "contratos públicos")} somando <b>${brl(a.total)}</b> ${periodo(a.inicio, a.fim)}, num período em que constava como <b>${situacao(m.sancao)}</b> no ${esc(m.lista)}.`;
  if (m.tipo === "R08") return `${E} assinou ${plural(a.n, "contrato", "contratos")} somando <b>${brl(a.total)}</b> com ${esc(a.orgao)}. Tem como sócio <b>${esc(m.socio)}</b> sediado em <b>${esc(m.pais)}</b>, jurisdição de ${m.nivel === 1 ? "sigilo clássico" : "tributação favorecida"} (lista de referência). Ter sócio no exterior é legal; o ponto de atenção é a opacidade de quem recebe dinheiro público.`;
  if (m.tipo === "R06") return `${E} assinou <b>${a.n} contratos</b> com ${esc(a.orgao)} no trimestre ${esc(m.tri)}, cada um entre <b>${brl(m.minimo)}</b> e <b>${brl(m.maximo)}</b>, somando <b>${brl(a.total)}</b>. Todos abaixo da faixa de dispensa de licitação por valor: pode ser uma compra maior dividida em partes.`;
  if (m.tipo === "R07") return `${E} concentra <b>${Math.round(m.share * 100)}%</b> de tudo que ${esc(a.orgao)} contratou em <b>${m.ano}</b> (${brl(a.total)} de ${brl(m.total_orgao)}).`;
  if (m.tipo === "RF01") return m.ref
    ? `${E} foi liquidado pelo Banco Central em nov/2025. Este é o <b>caso de referência</b>: o critério (captação acima de R$ 5 bi, crescimento de 50% ou mais em 12 meses e alavancagem de 10x ou mais) teria acendido por <b>${m.trimestres} trimestres seguidos</b>, desde o 1º trimestre de 2023, mais de dois anos antes da liquidação.`
    : `${E} cresce rápido e alavancado há <b>${m.trimestres} trimestres seguidos</b>: captações de <b>${brlCurto(m.captacao)}</b> (${m.yoy >= 0 ? "+" : ""}${Math.round(m.yoy * 100)}% em 12 meses) com ativo <b>${(m.alav || 0).toFixed(1)} vezes</b> o patrimônio líquido (posição em ${esc(m.ate)}). É uma <b>lista de observação</b>, não um diagnóstico.`;
  if (m.tipo === "R05") return `${E} assinou ${plural(a.n, "contrato", "contratos")} somando <b>${brl(a.total)}</b> com a Prefeitura de ${esc(m.cidade)}/${esc(m.uf)} desde 2025. <b>${esc(m.doador)}</b>, ${esc(QUALIF[m.qualificacao] || "sócio(a)")} da empresa, doou <b>${brl(m.doacao)}</b> à campanha do prefeito eleito <b>${esc(m.prefeito)}</b> (${esc(m.partido)}) em 2024.`;
  if (m.tipo === "R03") return `${E} abriu as portas em <b>${data(m.abertura)}</b> e, <b>${m.dias} dias depois</b>, assinou um contrato de <b>${brl(a.total)}</b> com ${esc(a.orgao)}.`;
  return `${E} tem capital social de <b>${brl(m.capital || 0)}</b> e assinou um contrato de <b>${brl(a.total)}</b> com ${esc(a.orgao)}: <b>${(m.vezes || 0).toLocaleString("pt-BR")} vezes</b> o capital.`;
}
function linhaCard(a) {
  const m = a.manchete;
  if (m.tipo === "R01") return `${situacaoCurta(m.sancao)} quando recebeu da cota parlamentar`;
  if (m.tipo === "R02") return `${situacaoCurta(m.sancao)} quando assinou contrato público`;
  if (m.tipo === "R08") return `Sócio sediado em ${m.pais}, jurisdição de ${m.nivel === 1 ? "sigilo clássico" : "tributação favorecida"}`;
  if (m.tipo === "R06") return `${a.n} contratos pequenos no mesmo trimestre, todos abaixo do limite de dispensa`;
  if (m.tipo === "R07") return `Fica com ${Math.round(m.share * 100)}% do dinheiro contratado pela prefeitura em ${m.ano}`;
  if (m.tipo === "RF01") return m.ref ? `Caso de referência: o critério acenderia ${m.trimestres} trimestres antes da liquidação` : `Crescimento acelerado e alavancado há ${m.trimestres} trimestres`;
  if (m.tipo === "R05") return `Sócio doou ${brlCurto(m.doacao)} ao prefeito e a empresa fechou contrato com a prefeitura`;
  if (m.tipo === "R03") return `Aberta há ${m.dias} dias quando assinou o contrato`;
  return `Contrato ${(m.vezes || 0).toLocaleString("pt-BR")}× maior que o capital da empresa`;
}
function numeros(a) {
  const m = a.manchete, N = (r, v) => `<div><small>${r}</small><b class="num">${v}</b></div>`;
  if (m.tipo === "R01" || m.tipo === "R02") return N("Total recebido", brlCurto(a.total)) + N(m.tipo === "R01" ? "Pagamentos" : "Contratos", a.n) + N("Punição", esc(a.sancao.lista));
  if (m.tipo === "R08") return N("Em contratos", brlCurto(a.total)) + N("Contratos", a.n) + N("País do sócio", esc(m.pais));
  if (m.tipo === "R06") return N("Soma", brlCurto(a.total)) + N("Contratos", a.n) + N("Maior contrato", brlCurto(m.maximo));
  if (m.tipo === "R07") return N("Do fornecedor", brlCurto(a.total)) + N("Do órgão no ano", brlCurto(m.total_orgao)) + N("Participação", Math.round(m.share * 100) + "%");
  if (m.tipo === "RF01") return N("Captações", brlCurto(m.captacao)) + N("Em 12 meses", (m.yoy >= 0 ? "+" : "") + Math.round(m.yoy * 100) + "%") + N("Ativo / patrimônio", (m.alav || 0).toFixed(1) + "x");
  if (m.tipo === "R05") return N("Em contratos", brlCurto(a.total)) + N("Contratos", a.n) + N("Doação ao prefeito", brlCurto(m.doacao));
  if (m.tipo === "R03") return N("Valor do contrato", brlCurto(a.total)) + N("Dias de vida", m.dias) + N("Capital social", m.capital != null ? brlCurto(m.capital) : "–");
  return N("Valor do contrato", brlCurto(a.total)) + N("Vezes o capital", (m.vezes || 0).toLocaleString("pt-BR")) + N("Capital social", brlCurto(m.capital || 0));
}
function checagem(a) {
  const m = a.manchete;
  if (m.tipo === "R01") return ["Abra a nota de cada pagamento e veja o que foi contratado.", `Veja se a punição realmente alcançava a casa legislativa na data do pagamento (o alcance acima diz onde ela valia).`, "Confirme a situação atual da empresa no Portal da Transparência."];
  if (m.tipo === "R02") return ["Abra cada contrato no PNCP e veja quem contratou e o que foi contratado.", "Confira se a punição valia para esse órgão (veja o alcance acima). Punição restrita a outro órgão não impede contratar.", "Procure se o contrato foi suspenso ou anulado depois."];
  if (m.tipo === "R08") return ["Multinacionais legítimas costumam ter sócio em Luxemburgo, Suíça ou Países Baixos. O sinal forte é sócio em jurisdição de sigilo clássico (Panamá, Ilhas Virgens, Cayman) numa empresa pequena.", "Descubra quem está por trás do sócio no exterior: o beneficiário final precisa constar no cadastro da Receita.", "Veja se a empresa tem outros contratos públicos e se foi aberta recentemente."];
  if (m.tipo === "R06") return ["Abra os contratos no PNCP: o objeto é o mesmo ou muito parecido entre eles?", "Some os valores: a compra única passaria do limite de dispensa e exigiria licitação?", "Veja se há justificativa de urgência ou de fornecimento de naturezas diferentes."];
  if (m.tipo === "R07") return ["Em alguns serviços há poucos fornecedores (coleta de lixo, saúde, merenda). Concentração não é irregularidade por si só.", "Confira se houve licitação aberta com mais de um concorrente.", "Compare o preço pago com o de prefeituras de porte parecido."];
  if (m.tipo === "RF01") return ["Alavancagem de 10x a 20x é comum em banco. O sinal relevante é o crescimento sustentado muito acima dos pares.", "Veja quem compra o papel: fundos de previdência de servidores e bancos públicos concentrados num emissor pequeno são o ponto crítico.", "Compare a remuneração oferecida (CDBs, LCIs, LFs) com a taxa de mercado: rendimento muito acima da média exige explicação.", "Consulte o Índice de Basileia e as demonstrações no IF.data do Banco Central."];
  if (m.tipo === "R05") return ["Doar para campanha é legal. Veja se a empresa já era fornecedora da prefeitura antes da eleição.", "Abra cada contrato no PNCP: houve licitação com concorrência ou foi dispensa/inexigibilidade?", "Compare o preço com o que outras prefeituras pagam pelo mesmo objeto.", "Confira a prestação de contas do candidato no site do TSE (DivulgaCandContas)."];
  if (m.tipo === "R03") return ["Empresa nova não é irregular por si só. Veja se tem experiência no objeto contratado (CNAE, sócios).", "Procure o processo de contratação: houve concorrência ou foi dispensa/inexigibilidade?", "Confira quem são os sócios e se têm ligação com o órgão."];
  return ["Confira se o valor está certo: erros de digitação são comuns no PNCP (uma casa decimal a mais vira um contrato de bilhões).", "Capital baixo pode ser normal em empresas de serviço. Veja se há subcontratação ou garantia.", "Abra o contrato no PNCP e confira o objeto e a forma de contratação.", "Confira o histórico da empresa com outros órgãos."];
}

// ---------- mapa ----------
const MAPA_BOUNDS = [[-75, -34.5], [-33, 5.6]];
const map = new maplibregl.Map({
  container: "mapa", attributionControl: { compact: true },
  style: { version: 8, glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf", sources: {}, layers: [{ id: "fundo", type: "background", paint: { "background-color": "#04090e" } }] },
  bounds: MAPA_BOUNDS, fitBoundsOptions: { padding: 8 },
  minZoom: 1.5, maxZoom: 10, dragRotate: false, pitchWithRotate: false,
});
map.touchZoomRotate.disableRotation();
const vazio = { type: "FeatureCollection", features: [] };

function curva(a, b, n = 40) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
  const c = [mx - dy * 0.22, my + dx * 0.22 * (dx >= 0 ? 1 : -1) + Math.abs(dx) * 0.05];
  return Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t;
    return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]]; });
}

let alertas = [], visiveis = [], filtroG = "todas", filtroR = "todas", sel = null, nomes = {};
const ptsGeo = (lista) => ({ type: "FeatureCollection", features: lista.filter((a) => a.local).map((a) => ({ type: "Feature", properties: { id: a.id, g: a.gravidade, t: Math.log10(Math.max(a.total, 1000)) }, geometry: { type: "Point", coordinates: [a.local.lon, a.local.lat] } })) });
function corUF(lista) {
  const por = {}; lista.filter((a) => a.local).forEach((a) => { por[a.local.uf] = (por[a.local.uf] || 0) + 1; });
  const casos = ["match", ["get", "uf"]];
  Object.entries(por).forEach(([u, n]) => casos.push(u, n >= 40 ? "#244a5e" : n >= 15 ? "#1d3d50" : n >= 5 ? "#18323f" : "#132a36"));
  casos.push("#0f212b"); return casos;
}
function atualizarMapa() {
  if (!map.getSource("pontos")) return;
  map.getSource("pontos").setData(ptsGeo(visiveis));
  map.setPaintProperty("uf-fill", "fill-color", corUF(visiveis));
}
function mostrarRota(a) {
  if (!map.getSource("rota")) return;
  const o = a.origem, d = a.local;
  if (!o || !d) { map.getSource("rota").setData(vazio); return; }
  map.getSource("rota").setData({ type: "Feature", properties: { g: a.gravidade }, geometry: { type: "LineString", coordinates: curva([o.lon, o.lat], [d.lon, d.lat]) } });
  const b = new maplibregl.LngLatBounds([o.lon, o.lat], [o.lon, o.lat]).extend([d.lon, d.lat]);
  map.fitBounds(b, { padding: { top: 90, bottom: 90, left: 90, right: 560 }, maxZoom: 7, duration: 1100 });
}
const limparRota = () => map.getSource("rota") && map.getSource("rota").setData(vazio);

function montarMapa() {
  const corG = ["match", ["get", "g"], "alta", COR.alta, "media", COR.media, COR.baixa];
  // mundo ao fundo, discreto
  map.addSource("mundo", { type: "geojson", data: mundoGeo });
  map.addLayer({ id: "mundo-fill", type: "fill", source: "mundo", paint: { "fill-color": "#0a151d" } });
  map.addLayer({ id: "mundo-line", type: "line", source: "mundo", paint: { "line-color": "#16303d", "line-width": 0.6 } });
  // Brasil em destaque
  map.addSource("ufs", { type: "geojson", data: ufGeo });
  map.addLayer({ id: "uf-fill", type: "fill", source: "ufs", paint: { "fill-color": corUF(visiveis) } });
  map.addLayer({ id: "uf-line", type: "line", source: "ufs", paint: { "line-color": "#2d7f78", "line-width": 0.9, "line-opacity": 0.8 } });
  // voos internacionais (opcional)
  map.addSource("voos", { type: "geojson", data: vazio });
  map.addLayer({ id: "voos-arco", type: "line", source: "voos", filter: ["==", ["geometry-type"], "LineString"], layout: { visibility: "none" }, paint: { "line-color": "#b388ff", "line-width": ["interpolate", ["linear"], ["get", "n"], 1, 1, 100, 4], "line-opacity": 0.7 } });
  map.addLayer({ id: "voos-ponto", type: "circle", source: "voos", filter: ["==", ["geometry-type"], "Point"], layout: { visibility: "none" }, paint: { "circle-color": "#b388ff", "circle-radius": ["interpolate", ["linear"], ["get", "n"], 1, 4, 100, 12], "circle-stroke-color": "#fff", "circle-stroke-width": 1 } });
  map.addLayer({ id: "voos-nome", type: "symbol", source: "voos", filter: ["==", ["geometry-type"], "Point"], layout: { visibility: "none", "text-field": ["concat", ["get", "pais"], " · ", ["to-string", ["get", "n"]]], "text-font": ["Open Sans Regular"], "text-size": 11, "text-offset": [0, 1.2], "text-anchor": "top" }, paint: { "text-color": "#d9c8ff", "text-halo-color": "#04090e", "text-halo-width": 1.5 } });
  // rota do alerta selecionado
  map.addSource("rota", { type: "geojson", data: vazio });
  map.addLayer({ id: "rota-brilho", type: "line", source: "rota", paint: { "line-color": corG, "line-width": 8, "line-blur": 6, "line-opacity": 0.35 } });
  map.addLayer({ id: "rota", type: "line", source: "rota", layout: { "line-cap": "round" }, paint: { "line-color": "#ffffff", "line-width": 2.4 } });
  // alertas agrupados
  map.addSource("pontos", { type: "geojson", data: ptsGeo(visiveis), cluster: true, clusterRadius: 42, clusterMaxZoom: 8,
    clusterProperties: { alta: ["+", ["case", ["==", ["get", "g"], "alta"], 1, 0]], media: ["+", ["case", ["==", ["get", "g"], "media"], 1, 0]] } });
  const corC = ["case", [">=", ["/", ["get", "alta"], ["get", "point_count"]], 0.35], COR.alta, [">=", ["/", ["+", ["get", "alta"], ["get", "media"]], ["get", "point_count"]], 0.35], COR.media, COR.baixa];
  map.addLayer({ id: "cluster", type: "circle", source: "pontos", filter: ["has", "point_count"], paint: { "circle-color": corC, "circle-opacity": 0.85, "circle-radius": ["step", ["get", "point_count"], 14, 5, 18, 20, 23, 60, 29], "circle-stroke-color": "#04090e", "circle-stroke-width": 2 } });
  map.addLayer({ id: "cluster-n", type: "symbol", source: "pontos", filter: ["has", "point_count"], layout: { "text-field": ["get", "point_count_abbreviated"], "text-font": ["Open Sans Regular"], "text-size": 12 }, paint: { "text-color": "#04090e" } });
  map.addLayer({ id: "pontos", type: "circle", source: "pontos", filter: ["!", ["has", "point_count"]], paint: { "circle-color": corG, "circle-radius": ["interpolate", ["linear"], ["get", "t"], 3, 4, 5, 7, 7, 11], "circle-stroke-color": "#04090e", "circle-stroke-width": 1.5 } });
  const el = document.createElement("div"); el.innerHTML = '<div style="color:#00ffa6;font:700 11px ui-monospace,Consolas,monospace;letter-spacing:.1em;text-shadow:0 0 6px #000">◉ BRASÍLIA</div>';
  new maplibregl.Marker({ element: el, anchor: "left" }).setLngLat(BRASILIA).addTo(map);

  map.on("click", "cluster", async (e) => {
    const f = e.features[0]; const z = await map.getSource("pontos").getClusterExpansionZoom(f.properties.cluster_id);
    map.easeTo({ center: f.geometry.coordinates, zoom: z + 0.3 });
  });
  map.on("click", "pontos", (e) => abrir(e.features[0].properties.id));
  ["pontos", "cluster", "voos-ponto"].forEach((l) => { map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer")); map.on("mouseleave", l, () => (map.getCanvas().style.cursor = "")); });
  const dica = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12 });
  map.on("mousemove", "pontos", (e) => { const a = alertas.find((x) => x.id === e.features[0].properties.id); if (a) dica.setLngLat(e.lngLat).setHTML(`<b>${esc(a.empresa)}</b><br>${esc(a.local.cidade)}/${esc(a.local.uf)} · ${brlCurto(a.total)}`).addTo(map); });
  map.on("mouseleave", "pontos", () => dica.remove());
  map.on("mousemove", "voos-ponto", (e) => dica.setLngLat(e.lngLat).setHTML(`<b>${esc(e.features[0].properties.pais)}</b><br>${e.features[0].properties.n} voos pagos com a cota`).addTo(map));
  map.on("mouseleave", "voos-ponto", () => dica.remove());
  map.on("mousemove", (e) => { $("coords").textContent = `LAT ${e.lngLat.lat.toFixed(2)} · LON ${e.lngLat.lng.toFixed(2)}`; });
  $("tg-voos").onchange = (e) => alternarVoos(e.target.checked);
}
async function alternarVoos(on) {
  const v = on ? "visible" : "none";
  ["voos-arco", "voos-ponto", "voos-nome"].forEach((l) => map.setLayoutProperty(l, "visibility", v));
  if (!on) return;
  const d = await dadosViagens();
  const fs = [];
  d.paises.forEach((p) => {
    fs.push({ type: "Feature", properties: { pais: p.pais, n: p.n }, geometry: { type: "LineString", coordinates: curva(BRASILIA, [p.lon, p.lat], 50) } });
    fs.push({ type: "Feature", properties: { pais: p.pais, n: p.n }, geometry: { type: "Point", coordinates: [p.lon, p.lat] } });
  });
  map.getSource("voos").setData({ type: "FeatureCollection", features: fs });
  map.fitBounds([[-80, -40], [10, 45]], { padding: 40, duration: 1200 });
}
let _viagens = null;
const dadosViagens = async () => (_viagens ||= await fetch("/data/viagens.json").then((r) => r.json()).catch(() => ({ voos: [], deputados: [], paises: [] })));

// ---------- lista e filtros ----------
function aplicarFiltro() {
  visiveis = alertas.filter((a) => (filtroG === "todas" || a.gravidade === filtroG) && (filtroR === "todas" || a.regra === filtroR));
  lista(); atualizarMapa();
}
function lista() {
  $("itens").innerHTML = visiveis.slice(0, 200).map((a) => `
    <li class="card ${sel === a.id ? "sel" : ""}" style="--c:${COR[a.gravidade]}" data-id="${esc(a.id)}">
      <div class="topo"><div class="nome">${esc(a.empresa)}</div><div class="valor num">${brlCurto(a.total)}</div></div>
      <div class="sub">${linhaCard(a)}</div>
      <div class="meta"><span class="chip">${NOME_G[a.gravidade].replace("Prioridade ", "")}</span>${a.regra} · ${plural(a.n, "registro", "registros")} · ${periodo(a.inicio, a.fim).replace(/^(em|entre) /, "")}${a.local ? " · " + esc(a.local.cidade) + "/" + a.local.uf : ""}</div>
    </li>`).join("") || '<p class="sub2">Nenhum alerta neste filtro.</p>';
  $("itens").querySelectorAll(".card").forEach((c) => (c.onclick = () => abrir(c.dataset.id)));
  $("cont").textContent = `${visiveis.length} alertas${visiveis.length > 200 ? " (mostrando 200)" : ""}`;
}

// ---------- dossiê ----------
function abrir(id) {
  const a = alertas.find((x) => x.id === id); if (!a) return;
  sel = id; lista();
  const c = COR[a.gravidade], t = a.tabela, s = a.sancao;
  const cab = t.cols.map((h, i) => `<th${i === 3 ? ' style="text-align:right"' : ""}>${h}</th>`).join("");
  const linhas = t.linhas.map((l) => "<tr>" + l.map((x) => `<td${x.v ? ' class="v num"' : ""}>${x.u ? `<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)}</a>` : x.s ? `<b>${esc(x.t)}</b><br><span class="sub2">${esc(x.s)}</span>` : esc(x.t)}</td>`).join("") + "</tr>").join("");
  const blocoSancao = s ? `<h4>A punição</h4><dl class="kv"><dt>Cadastro</dt><dd>${esc(listaNome[s.lista] || s.lista)}</dd><dt>Tipo</dt><dd>${esc(s.tipo)}</dd><dt>Aplicada por</dt><dd>${esc(s.orgao)}</dd><dt>Vigência</dt><dd>${s.fim ? `de ${data(s.inicio)} até ${data(s.fim)}` : `desde ${data(s.inicio)}, sem data final`}</dd><dt>Alcance</dt><dd>${alcance(s.alcance)}</dd></dl>` : "";
  const m = a.manchete;
  const blocoEmpresa = (m.tipo === "R03" || m.tipo === "R04") ? `<h4>A empresa</h4><dl class="kv">${m.abertura ? `<dt>Abertura</dt><dd>${data(m.abertura)}</dd>` : ""}<dt>Capital social</dt><dd>${m.capital != null ? brl(m.capital) : "não informado"}</dd><dt>Porte</dt><dd>${esc(PORTE[m.porte] || m.porte || "não informado")}</dd><dt>Contratante</dt><dd>${esc(a.orgao || "")}${a.orgao_municipio ? " · " + esc(a.orgao_municipio) + "/" + esc(a.orgao_uf) : ""}</dd></dl>` : "";
  const blocoVinculo = m.tipo === "R05" ? `<h4>O vínculo</h4><dl class="kv"><dt>Prefeito eleito</dt><dd>${esc(m.prefeito)} (${esc(m.partido)}) · ${esc(m.cidade)}/${esc(m.uf)}</dd><dt>Doador</dt><dd>${esc(m.doador)}, ${esc(QUALIF[m.qualificacao] || "sócio(a)")} da empresa</dd><dt>Doou</dt><dd>${brl(m.doacao)} na campanha de 2024</dd><dt>Fonte</dt><dd><a href="https://divulgacandcontas.tse.jus.br" target="_blank" rel="noopener">TSE · DivulgaCandContas</a></dd></dl>` : "";
  $("detalhe").hidden = false; $("detalhe").style.setProperty("--c", c);
  $("detalhe").innerHTML = `
    <button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:${c}"><span>DOSSIÊ · ${a.regra} · ${esc(nomes[a.regra] || "")}</span><span class="carimbo">PONTO DE ATENÇÃO</span></div>
    <h2 style="--c:${c}">${esc(a.empresa)}</h2>
    <div class="sub2 mono">CNPJ ${esc(a.cnpj)}${a.local ? " · " + esc(a.local.cidade) + "/" + esc(a.local.uf) : ""}</div>
    <div class="manchete" style="--c:${c}">${manchete(a)}</div>
    <div class="numeros" style="--c:${c}">${numeros(a)}</div>
    <h4>${esc(t.titulo)}</h4>
    <table style="--c:${c}"><thead><tr>${cab}</tr></thead><tbody>${linhas}</tbody></table>
    ${a.n > t.linhas.length ? `<p class="sub2" style="margin-top:6px">Mostrando ${t.linhas.length} de ${a.n} registros.</p>` : ""}
    ${blocoSancao}${blocoEmpresa}${blocoVinculo}${(dDiarios[a.id] || []).length ? `<h4>Diários oficiais</h4>${dDiarios[a.id].map((x) => `<div class="diario"><small>${esc(x.cidade)}/${esc(x.uf)} · ${esc(x.data)}</small>${esc(x.trecho)} <a href="${esc(x.url)}" target="_blank" rel="noopener">abrir diário</a></div>`).join("")}<p class="sub2">Menções ao nome da empresa em diários oficiais municipais (Querido Diário). Podem ser homônimos.</p>` : ""}${(a.secoes || []).map((x) => `<h4>${esc(x.titulo)}</h4><dl class="kv">${x.kv.map((k) => `<dt>${esc(k[0])}</dt><dd>${esc(k[1])}</dd>`).join("")}</dl>`).join("")}
    <h4>Checagem</h4><ul class="check">${checagem(a).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    <p class="aviso">Isto é um ponto de atenção feito a partir de dados públicos, não uma conclusão. Pode haver explicação legal.</p>
    <div class="links" style="margin-top:12px;font-size:12.5px">Fontes: <a href="https://www3.bcb.gov.br/ifdata" target="_blank" rel="noopener">Banco Central (IF.data)</a> · <a href="https://dados.cvm.gov.br" target="_blank" rel="noopener">CVM</a> · <a href="https://pncp.gov.br" target="_blank" rel="noopener">PNCP</a> · <a href="https://portaldatransparencia.gov.br/sancoes/consulta" target="_blank" rel="noopener">Portal da Transparência</a> · <a href="https://dadosabertos.camara.leg.br" target="_blank" rel="noopener">Câmara</a> · <a href="https://www12.senado.leg.br/transparencia/dados-abertos-transparencia/dados-abertos-ceaps" target="_blank" rel="noopener">Senado</a> · <a href="https://dadosabertos.rfb.gov.br" target="_blank" rel="noopener">Receita (CNPJ)</a></div>`;
  $("detalhe").querySelector(".fechar").onclick = fechar;
  mostrarRota(a);
}
function fechar() { $("detalhe").hidden = true; sel = null; lista(); limparRota(); map.fitBounds(MAPA_BOUNDS, { padding: 8, duration: 900 }); }

// ---------- fichas de agente público ----------
let fichas = null;
const norm = (x) => String(x || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const CARGO = { dep: "Deputado(a) federal", sen: "Senador(a)", pref: "Prefeito(a) eleito(a) em 2024" };
$("aba-fichas").innerHTML = `<h3>Fichas de agentes públicos</h3><p class="sub2">Busque um deputado, senador ou prefeito. A ficha reúne só dados abertos (gastos, fornecedores, alertas ligados). Não é avaliação de conduta.</p>
  <input id="busca" type="search" placeholder="Nome, cidade ou UF..." autocomplete="off" style="width:100%;padding:10px 12px;margin:6px 0 12px;background:#06141a;border:1px solid var(--neon);color:#fff;font:14px ui-monospace,Consolas,monospace;outline:none"><div id="res"></div>`;
async function carregarFichas() {
  if (fichas) return;
  $("res").innerHTML = '<p class="sub2">Carregando fichas...</p>';
  fichas = (await fetch("/data/fichas.json").then((r) => r.json()).catch(() => ({ fichas: [] }))).fichas;
  fichas.forEach((f) => { f._k = norm([f.n, f.c, f.u, f.p].join(" ")); });
  buscarFichas();
}
function buscarFichas() {
  const q = norm($("busca").value).trim();
  const lista = (q ? fichas.filter((f) => q.split(/\s+/).every((w) => f._k.includes(w))) : fichas.filter((f) => f.n_alertas > 0).sort((a, b) => b.n_alertas - a.n_alertas)).slice(0, 40);
  $("res").innerHTML = (q ? "" : '<div class="rot">// com alertas ligados</div>') + (lista.map((f, i) => `<div class="card" style="--c:#00ffa6" data-i="${fichas.indexOf(f)}"><div class="topo"><div class="nome">${esc(f.n)}</div>${f.n_alertas ? `<div class="valor num" style="color:var(--media)">${f.n_alertas} alerta${f.n_alertas > 1 ? "s" : ""}</div>` : ""}</div><div class="meta">${CARGO[f.t]}${f.c ? " · " + esc(f.c) : ""}${f.p ? " · " + esc(f.p) : ""}${f.u ? "/" + esc(f.u) : ""}</div></div>`).join("") || '<p class="sub2">Nenhuma ficha encontrada.</p>');
  $("res").querySelectorAll(".card").forEach((c) => (c.onclick = () => abrirFicha(fichas[Number(c.dataset.i)])));
}
$("busca").addEventListener("input", () => fichas && buscarFichas());
function abrirFicha(f) {
  sel = null; const c = "#00ffa6";
  const anos = Object.entries(f.anos || {}); const max = Math.max(1, ...anos.map(([, v]) => v));
  const barras = anos.map(([a, v]) => `<div style="display:grid;grid-template-columns:44px 1fr 92px;gap:8px;align-items:center;margin:4px 0;font-size:12.5px"><span class="sub2">${a}</span><div style="background:#0b2a2c;height:10px"><div style="width:${Math.round(100 * v / max)}%;height:10px;background:var(--neon);box-shadow:0 0 8px var(--neon)"></div></div><span class="num" style="text-align:right">${brlCurto(v)}</span></div>`).join("");
  const forn = (f.forn || []).map((x) => `<tr><td>${esc(x[0])}</td><td class="v num" style="color:var(--forte)">${brlCurto(x[1])}</td></tr>`).join("");
  const al = (f.alertas || []).map((id) => { const a = alertas.find((z) => z.id === id); return a ? `<li><a href="#" data-id="${esc(id)}">${esc(a.empresa)}</a> <span class="sub2">· ${esc(nomes[a.regra] || a.regra)} · ${brlCurto(a.total)}</span></li>` : ""; }).join("");
  const r = f.r05;
  $("detalhe").hidden = false; $("detalhe").style.setProperty("--c", c);
  $("detalhe").innerHTML = `
    <button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:${c}"><span>FICHA · ${CARGO[f.t].toUpperCase()}</span><span class="carimbo">DADOS ABERTOS</span></div>
    <h2 style="--c:${c}">${esc(f.n)}</h2>
    <div class="sub2 mono">${f.c ? esc(f.c) + "/" : ""}${esc(f.u || "")}${f.p ? " · " + esc(f.p) : ""}</div>
    ${f.t === "pref" ? `<div class="manchete" style="--c:${c}">${r ? `Entre os contratos da prefeitura desde 2025, <b>${r.n} empresa${r.n > 1 ? "s" : ""}</b> têm sócio que doou à campanha de 2024, somando <b>${brl(r.v)}</b> em contratos. Doar é legal; o ponto de atenção é o vínculo.` : "Nenhum cruzamento entre doadores da campanha e fornecedores da prefeitura foi encontrado nos dados analisados."}</div>` : `<div class="manchete" style="--c:${c}">${f.pct25 != null ? `Em 2025, o gasto de cota foi maior que o de <b>${f.pct25}%</b> dos deputados.` : "Sem gasto de cota registrado em 2025."} ${f.n_alertas ? `Aparece em <b>${f.n_alertas}</b> alerta${f.n_alertas > 1 ? "s" : ""} (empresa punida paga com a cota).` : "Não aparece em nenhum alerta."}</div>`}
    ${barras ? `<h4>Gasto da cota por ano</h4>${barras}` : ""}
    ${forn ? `<h4>Maiores fornecedores (2023 a 2026)</h4><table><tbody>${forn}</tbody></table>` : ""}
    ${al ? `<h4>Alertas ligados</h4><ul class="check">${al}</ul>` : ""}
    <p class="aviso">Ficha montada só com dados abertos e sem avaliação de conduta. Gasto alto de cota não indica irregularidade por si só: depende de estado, estrutura de gabinete e uso legítimo.</p>`;
  $("detalhe").querySelector(".fechar").onclick = () => { $("detalhe").hidden = true; };
  $("detalhe").querySelectorAll("a[data-id]").forEach((x) => (x.onclick = (e) => { e.preventDefault(); abrir(x.dataset.id); }));
}

// ---------- exterior (voos da cota) e judiciário (DataJud) ----------
async function montarExterior() {
  const d = await dadosViagens(), el = $("aba-exterior");
  const tot = d.voos.reduce((s, x) => s + x.v, 0);
  el.innerHTML = `<h3>Exterior</h3><p class="sub2">Voos internacionais pagos com a cota parlamentar da Câmara (2023 a 2026). A data é a da <b>emissão</b> da passagem, não do voo. Não é rastreamento de ninguém: é o que a Câmara publica.</p>
    <div class="caixa"><b>${d.voos.length}</b> voos para <b>${d.paises.length}</b> países, somando <b>${brlCurto(tot)}</b>.</div>
    <div class="rot">// por país</div><table class="tbl"><tbody>${d.paises.map((p) => `<tr><td>${esc(p.pais)}</td><td class="num" style="text-align:right">${p.n} voos</td><td class="num" style="text-align:right">${brlCurto(p.v)}</td></tr>`).join("")}</tbody></table>
    <div class="rot" style="margin-top:14px">// quem mais voou ao exterior com a cota</div>
    <table class="tbl"><tbody>${d.deputados.slice(0, 15).map((p) => `<tr><td><b>${esc(p.p)}</b><br><span class="sub2">${esc(p.pt || "")}${p.uf ? "/" + esc(p.uf) : ""} · ${Object.entries(p.paises).map(([k, v]) => k + " " + v).join(", ")}</span></td><td class="num" style="text-align:right">${p.n}</td><td class="num" style="text-align:right">${brlCurto(p.v)}</td></tr>`).join("")}</tbody></table>
    <p class="aviso">Voo ao exterior pago pela cota não é irregularidade por si só (há regras próprias de uso). Veja o trecho e o passageiro na nota da Câmara.</p>`;
  $("tg-voos").checked = true; alternarVoos(true);
}
async function montarJustica() {
  const el = $("aba-justica");
  const d = await fetch("/data/judiciario.json").then((r) => r.json()).catch(() => null);
  if (!d || !d.tribunais.length) { el.innerHTML = '<h3>Judiciário</h3><p class="sub2">Dados do DataJud ainda não carregados.</p>'; return; }
  const max = Math.max(...d.tribunais.map((t) => t.total));
  el.innerHTML = `<h3>Judiciário</h3><p class="sub2">${esc(d.classe)} por tribunal (DataJud, CNJ). Mostra quanto chega à Justiça, não a conduta de ninguém. Estados maiores têm mais processos.</p>
    <table class="tbl"><tbody>${d.tribunais.sort((a, b) => b.total - a.total).map((t) => {
      const anos = Object.entries(t.anos).slice(-8), m = Math.max(1, ...anos.map(([, v]) => v));
      const spark = anos.map(([a, v]) => `<i title="${a}: ${v}" style="display:inline-block;width:5px;margin-right:1px;height:${Math.max(2, Math.round(16 * v / m))}px;background:var(--neon);vertical-align:bottom"></i>`).join("");
      return `<tr><td>${esc(t.sigla)}</td><td style="width:90px"><div class="barra"><i style="width:${Math.round(100 * t.total / max)}%"></i></div></td><td class="num" style="text-align:right">${t.total.toLocaleString("pt-BR")}</td><td>${spark}</td></tr>`; }).join("")}</tbody></table>
    <p class="aviso">As barras pequenas mostram as ações ajuizadas por ano (últimos 8 anos). O DataJud não informa as partes, então não dá para ligar processo a político.</p>`;
}

// ---------- abas ----------
$("abas").onclick = (e) => { const b = e.target.closest("button"); if (!b) return;
  [...$("abas").children].forEach((x) => x.classList.toggle("on", x === b));
  document.querySelectorAll(".aba").forEach((x) => x.classList.toggle("on", x.id === "aba-" + b.dataset.aba));
  if (b.dataset.aba === "fichas") carregarFichas();
  if (b.dataset.aba === "exterior") montarExterior();
  if (b.dataset.aba === "justica") montarJustica(); };
$("filtros").onclick = (e) => { const b = e.target.closest("button"); if (!b) return; filtroG = b.dataset.g;
  [...$("filtros").children].forEach((x) => x.classList.toggle("on", x === b)); aplicarFiltro(); };

$("aba-risco").innerHTML = `
  <h3>Risco financeiro <span class="tag">em construção</span></h3>
  <p>Este módulo procura o que não aparece em contratos: dinheiro público e de aposentados concentrado em poucos emissores, bancos crescendo rápido demais e fundos que se pagam entre si. É o tipo de sinal que antecede um colapso como o do Banco Master.</p>
  <div class="caixa"><b>1. Previdência de servidores concentrada</b><p>Quanto da carteira de cada fundo de previdência municipal ou estadual (RPPS) está num único emissor.</p></div>
  <div class="caixa"><b>2. Banco crescendo fora da curva</b><p>Captação e ativos que dobram em poucos trimestres, com rendimento muito acima do mercado. Fonte: Banco Central.</p></div>
  <div class="caixa"><b>3. Rede de fundos e empresas</b><p>Fundos que investem uns nos outros e terminam numa empresa recém-criada. Fonte: CVM e CNPJ da Receita.</p></div>`;
$("aba-sobre").innerHTML = `
  <h3>Como ler este painel</h3>
  <div class="caixa"><b>O que é um alerta</b><p>Um cruzamento automático de bases públicas que encontrou algo fora do esperado. É um ponto de atenção para conferir, não uma acusação.</p></div>
  <div class="caixa"><b>Prioridade</b><p><span class="chip" style="--c:${COR.alta}">alta</span> sinal forte (ex.: punição que valia em todo o governo, empresa com menos de 90 dias e contrato acima de R$ 1 mi). <span class="chip" style="--c:${COR.media}">média</span> sinal relevante com alguma dúvida. <span class="chip" style="--c:${COR.baixa}">baixa</span> sinal fraco ou restrito a um órgão.</p></div>
  <div class="caixa"><b>De onde vêm os dados</b><p>PNCP, Portal da Transparência, Câmara, Senado, TSE e Receita Federal. Tudo aberto e público. Cada alerta traz o link da fonte.</p></div>
  <div class="caixa"><b>Inspiração e créditos</b><p>Operação Serenata de Amor e Querido Diário (Open Knowledge Brasil), ambos de código aberto.</p></div>`;

// ---------- carga ----------
const [dA, dN, ufGeo, dR, mundoGeo, dDiarios] = await Promise.all([
  fetch("/data/alertas.json").then((r) => r.json()).catch(() => ({ alertas: [] })),
  fetch("/data/noticias.json").then((r) => r.json()).catch(() => ({ itens: [] })),
  fetch("/data/uf.geojson").then((r) => r.json()),
  fetch("/data/risco.json").then((r) => r.json()).catch(() => ({ alertas: [] })),
  fetch("/data/mundo.geojson").then((r) => r.json()),
  fetch("/data/diarios.json").then((r) => r.json()).catch(() => ({})),
]);
ufGeo.features.forEach((f) => { f.properties.uf = UF_COD[Number(f.properties.codarea)]; });
nomes = { ...(dA.regras || {}), RF01: "Risco financeiro: banco em crescimento acelerado" };
const ord = { alta: 0, media: 1, baixa: 2 };
alertas = [...dA.alertas, ...(dR.alertas || [])].sort((a, b) => ord[a.gravidade] - ord[b.gravidade] || b.total - a.total);
visiveis = alertas;

// filtro por tipo de alerta
const cont = {}; alertas.forEach((a) => (cont[a.regra] = (cont[a.regra] || 0) + 1));
const barra = document.createElement("div"); barra.className = "filtros"; barra.id = "regras";
barra.innerHTML = `<button data-r="todas" class="on">Todos os tipos</button>` + Object.keys(nomes).filter((r) => cont[r]).map((r) => `<button data-r="${r}" title="${esc(nomes[r])}">${esc(nomes[r])} (${cont[r]})</button>`).join("");
barra.onclick = (e) => { const b = e.target.closest("button"); if (!b) return; filtroR = b.dataset.r; [...barra.children].forEach((x) => x.classList.toggle("on", x === b)); aplicarFiltro(); };
$("filtros").before(barra);
const contEl = document.createElement("div"); contEl.id = "cont"; contEl.className = "sub2"; contEl.style.margin = "0 0 10px"; $("itens").before(contEl);

const total = alertas.filter((a) => !(a.manchete && a.manchete.ref)).reduce((s, a) => s + a.total, 0);  // o caso de referência (Master) é histórico e não entra na soma
$("resumo").innerHTML = `<span><b class="num">${alertas.length}</b>alertas</span><span><b class="num">${brlCurto(total)}</b>envolvidos</span><span><b class="num">${dA.gerado ? data(dA.gerado) : "–"}</b>atualizado</span>`;
{
  const altaR = alertas.filter((a) => a.gravidade === "alta" && !(a.manchete && a.manchete.ref)).reduce((s, a) => s + (a.total || 0), 0);
  const n = altaR < 2e9 ? 4 : altaR < 25e9 ? 3 : altaR < 100e9 ? 2 : 1;
  const cor = { 5: "#00ffa6", 4: "#00b8ff", 3: "#ffb300", 2: "#ff7a1a", 1: "#ff2d55" }[n];
  const txt = { 5: "NORMAL", 4: "ATENÇÃO", 3: "ELEVADO", 2: "ALTO", 1: "CRÍTICO" }[n];
  $("ameaca").style.setProperty("--c", cor); $("ameaca").title = `Nível calculado pelo valor total dos alertas de prioridade alta: ${brlCurto(altaR)}`;
  $("ameaca").innerHTML = `<div><small>Nível de ameaça</small><span>${txt}</span></div><b>${n}</b>`;
}
lista();
$("aba-noticias").innerHTML = `<h3>Notícias</h3><p class="sub2">Manchetes recentes sobre gasto público, fraude e fiscalização.</p><ul class="news">${dN.itens.map((n) => `<li><a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.titulo)}</a><small>${esc(n.fonte)}</small></li>`).join("") || "<li class='sub2'>Sem notícias carregadas.</li>"}</ul>`;
if (map.loaded()) montarMapa(); else map.on("load", montarMapa);
