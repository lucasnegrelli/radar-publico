import "@fontsource-variable/inter";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/500.css";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { PathLayer, ScatterplotLayer } from "@deck.gl/layers";
import { HeatmapLayer } from "@deck.gl/aggregation-layers";
import { TripsLayer } from "@deck.gl/geo-layers";

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
const pad = () => ({ top: 24, bottom: 112, left: document.body.classList.contains("sem-painel") ? 24 : 420, right: 24 });
const map = new maplibregl.Map({
  container: "mapa", attributionControl: { compact: true },
  style: { version: 8, glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf", sources: {}, layers: [{ id: "fundo", type: "background", paint: { "background-color": "#05080c" } }] },
  bounds: MAPA_BOUNDS, fitBoundsOptions: { padding: { top: 24, bottom: 112, left: 420, right: 24 } },
  minZoom: 1.5, maxZoom: 10, dragRotate: true, pitchWithRotate: true, maxPitch: 60,
});
const vazio = { type: "FeatureCollection", features: [] };

function curva(a, b, n = 40) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1];
  const c = [mx - dy * 0.22, my + dx * 0.22 * (dx >= 0 ? 1 : -1) + Math.abs(dx) * 0.05];
  return Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t;
    return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]]; });
}

function grade() {
  const f = [];
  for (let x = -75; x <= -30; x += 5) f.push({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [[x, -36], [x, 8]] } });
  for (let y = -35; y <= 7; y += 5) f.push({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [[-76, y], [-28, y]] } });
  return { type: "FeatureCollection", features: f };
}
let alertas = [], visiveis = [], filtroG = "todas", filtroR = "todas", sel = null, nomes = {};
const RGB = { alta: [255, 45, 85], media: [255, 179, 0], baixa: [0, 184, 255] };
const ADITIVO = { blend: true, blendColorOperation: "add", blendColorSrcFactor: "src-alpha", blendColorDstFactor: "one", blendAlphaSrcFactor: "one", blendAlphaDstFactor: "one" };
function corUF(lista) {
  const por = {}; lista.filter((a) => a.local).forEach((a) => { por[a.local.uf] = (por[a.local.uf] || 0) + 1; });
  const casos = ["match", ["get", "uf"]];
  Object.entries(por).forEach(([u, n]) => casos.push(u, n >= 40 ? "#202f40" : n >= 15 ? "#1a2736" : n >= 5 ? "#152030" : "#111a26"));
  casos.push("#0e151d"); return casos;
}

// ----- dados derivados para o deck.gl -----
let trilhas = [], colunas = [], pulsos = [], pontosA = [], rotaSel = null, overlay = null;
const LAY = { calor: true, rotas: true, todas: false, pontos: true };
let janela = null;
const rotasVis = () => (LAY.todas ? trilhas : trilhas.slice(0, 60));
const noJanela = (a) => !janela || ((a.fim || a.inicio || "").slice(0, 7) >= janela[0] && (a.inicio || a.fim || "").slice(0, 7) <= janela[1]);
function derivar() {
  const comRota = visiveis.filter((a) => a.local && a.origem);
  trilhas = comRota.map((a, k) => { const caminho = curva([a.origem.lon, a.origem.lat], [a.local.lon, a.local.lat], 28); const fase = (k * 0.137) % 1;
    return { id: a.id, g: a.gravidade, w: Math.min(2.6, 0.7 + Math.log10(Math.max(a.total, 1000)) * 0.28), path: caminho, ts: caminho.map((_, i) => fase + i / 28 * 0.9) }; });
  const por = new Map();
  visiveis.filter((a) => a.local).forEach((a) => { const k = a.local.cidade + "|" + a.local.uf; let c = por.get(k);
    if (!c) por.set(k, (c = { pos: [a.local.lon, a.local.lat], cidade: a.local.cidade, uf: a.local.uf, n: 0, total: 0, topo: a, alta: 0 }));
    c.n++; c.total += a.total; if (a.gravidade === "alta") c.alta++; if (a.total > c.topo.total) c.topo = a; });
  colunas = [...por.values()].map((c) => ({ ...c, g: c.alta / c.n >= 0.35 ? "alta" : c.alta / c.n > 0 || c.topo.gravidade === "media" ? "media" : "baixa" }));
  pulsos = [...colunas].sort((a, b) => b.total - a.total).slice(0, 6);
  pontosA = visiveis.filter((a) => a.local).map((a) => ({ id: a.id, g: a.gravidade, pos: [a.local.lon, a.local.lat], total: a.total, empresa: a.empresa, cidade: a.local.cidade, uf: a.local.uf }));
}
const altura = (v) => Math.max(8000, (Math.log10(Math.max(v, 1000)) - 2.6) * 95000);
function camadas(tempo) {
  const L = [];
  L.push(new PathLayer({ id: "rotas-base", visible: LAY.rotas, data: rotasVis(), getPath: (d) => d.path, getColor: (d) => [...RGB[d.g], 42], getWidth: (d) => d.w * 0.7, widthUnits: "pixels", capRounded: true, pickable: true, parameters: ADITIVO, onClick: (i) => i.object && abrir(i.object.id) }));
  L.push(new TripsLayer({ id: "pulsos-rota", visible: LAY.rotas, data: rotasVis(), getPath: (d) => d.path, getTimestamps: (d) => d.ts, getColor: (d) => [...RGB[d.g], 255], widthMinPixels: 1.6, capRounded: true, jointRounded: true, trailLength: 0.28, currentTime: tempo, parameters: ADITIVO }));
  L.push(new HeatmapLayer({ id: "calor", visible: LAY.calor, data: pontosA, getPosition: (d) => d.pos, getWeight: (d) => Math.max(0.2, Math.log10(Math.max(d.total, 1000)) - 2.5), radiusPixels: 54, intensity: 3.6, threshold: 0.015, aggregation: "SUM",
    colorRange: [[20, 8, 40, 0], [70, 20, 100, 110], [140, 30, 125, 175], [220, 60, 70, 215], [255, 140, 40, 240], [255, 226, 130, 255]], parameters: ADITIVO }));
  L.push(new ScatterplotLayer({ id: "pontos-a", visible: LAY.pontos, data: pontosA, getPosition: (d) => d.pos, getRadius: 2.5, radiusUnits: "pixels", getFillColor: (d) => [...RGB[d.g], 255], stroked: true, getLineColor: [255, 255, 255, 90], getLineWidth: 0.5, lineWidthUnits: "pixels", pickable: true, onClick: (i) => i.object && abrir(i.object.id) }));
  L.push(new ScatterplotLayer({ id: "anel-pulso", visible: LAY.pontos, data: pulsos, getPosition: (d) => d.pos, getRadius: 1, radiusUnits: "pixels", radiusScale: 6 + 16 * (tempo % 1), stroked: true, filled: false, getLineColor: (d) => [...RGB[d.g], Math.round(200 * (1 - (tempo % 1)))], getLineWidth: 1.5, lineWidthUnits: "pixels", parameters: ADITIVO }));
  if (rotaSel) {
    L.push(new PathLayer({ id: "sel-brilho", data: [rotaSel], getPath: (d) => d.path, getColor: [...RGB[rotaSel.g], 90], getWidth: 14, widthUnits: "pixels", capRounded: true, parameters: ADITIVO }));
    L.push(new PathLayer({ id: "sel", data: [rotaSel], getPath: (d) => d.path, getColor: [255, 255, 255, 255], getWidth: 3, widthUnits: "pixels", capRounded: true }));
  }
  return L;
}
function atualizarMapa() { if (!overlay) return; derivar(); map.setPaintProperty("uf-fill", "fill-color", corUF(visiveis)); }
function mostrarRota(a) {
  const o = a.origem, d = a.local;
  if (!o || !d) { rotaSel = null; return; }
  rotaSel = { g: a.gravidade, path: curva([o.lon, o.lat], [d.lon, d.lat], 60) };
  const b = new maplibregl.LngLatBounds([o.lon, o.lat], [o.lon, o.lat]).extend([d.lon, d.lat]);
  map.fitBounds(b, { padding: { top: 90, bottom: 90, left: 90, right: 560 }, maxZoom: 7, duration: 1100 });
}
const limparRota = () => { rotaSel = null; };

function montarMapa() {
  const corG = ["match", ["get", "g"], "alta", COR.alta, "media", COR.media, COR.baixa];
  map.addSource("mundo", { type: "geojson", data: mundoGeo });
  map.addLayer({ id: "mundo-fill", type: "fill", source: "mundo", paint: { "fill-color": "#0c1118" } });
  map.addLayer({ id: "mundo-line", type: "line", source: "mundo", paint: { "line-color": "#19232e", "line-width": 0.6 } });
  map.addSource("grade", { type: "geojson", data: grade() });
  map.addLayer({ id: "grade", type: "line", source: "grade", paint: { "line-color": "#8aa0b5", "line-width": 0.5, "line-opacity": 0.035 } });
  map.addSource("ufs", { type: "geojson", data: ufGeo });
  map.addLayer({ id: "uf-fill", type: "fill", source: "ufs", paint: { "fill-color": corUF(visiveis) } });
  map.addLayer({ id: "uf-line", type: "line", source: "ufs", paint: { "line-color": "#2c3b4c", "line-width": 0.7, "line-opacity": 0.95 } });
  map.addSource("voos", { type: "geojson", data: vazio });
  map.addLayer({ id: "voos-arco", type: "line", source: "voos", filter: ["==", ["geometry-type"], "LineString"], layout: { visibility: "none" }, paint: { "line-color": "#b388ff", "line-width": ["interpolate", ["linear"], ["get", "n"], 1, 1, 100, 4], "line-opacity": 0.75 } });
  map.addLayer({ id: "voos-ponto", type: "circle", source: "voos", filter: ["==", ["geometry-type"], "Point"], layout: { visibility: "none" }, paint: { "circle-color": "#b388ff", "circle-radius": ["interpolate", ["linear"], ["get", "n"], 1, 4, 100, 12], "circle-stroke-color": "#fff", "circle-stroke-width": 1 } });
  map.addLayer({ id: "voos-nome", type: "symbol", source: "voos", filter: ["==", ["geometry-type"], "Point"], layout: { visibility: "none", "text-field": ["concat", ["get", "pais"], " · ", ["to-string", ["get", "n"]]], "text-font": ["Open Sans Regular"], "text-size": 11, "text-offset": [0, 1.2], "text-anchor": "top" }, paint: { "text-color": "#d9c8ff", "text-halo-color": "#04090e", "text-halo-width": 1.5 } });
  const el = document.createElement("div"); el.innerHTML = '<div style="color:#00ffa6;font:700 11px ui-monospace,Consolas,monospace;letter-spacing:.14em;text-shadow:0 0 8px #00ffa6">◉ BRASÍLIA</div>';
  new maplibregl.Marker({ element: el, anchor: "left" }).setLngLat(BRASILIA).addTo(map);

  derivar();
  overlay = new MapboxOverlay({ interleaved: false, layers: camadas(0), getTooltip: ({ object, layer }) => {
    if (!object) return null;
    if (layer.id === "pontos-a") return { className: "deck-tip", html: `<b>${esc(object.empresa)}</b><br>${esc(object.cidade)}/${esc(object.uf)} · ${brlCurto(object.total)}` };
    if (layer.id === "colunas") return { className: "deck-tip", html: `<b>${esc(object.cidade)}/${esc(object.uf)}</b><br>${plural(object.n, "alerta", "alertas")} · ${brlCurto(object.total)}<br><span style="opacity:.7">clique para abrir o maior</span>` };
    if (layer.id === "rotas-base") { const a = alertas.find((x) => x.id === object.id); return a ? { className: "deck-tip", html: `<b>${esc(a.empresa)}</b><br>${brlCurto(a.total)}` } : null; }
    return null; } });
  map.addControl(overlay);
  map.easeTo({ pitch: 0, duration: 800 });

  map.on("click", "voos-ponto", () => {});
  ["voos-ponto"].forEach((l) => { map.on("mouseenter", l, () => (map.getCanvas().style.cursor = "pointer")); map.on("mouseleave", l, () => (map.getCanvas().style.cursor = "")); });
  const dica = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12 });
  map.on("mousemove", "voos-ponto", (e) => dica.setLngLat(e.lngLat).setHTML(`<b>${esc(e.features[0].properties.pais)}</b><br>${e.features[0].properties.n} voos pagos com a cota`).addTo(map));
  map.on("mouseleave", "voos-ponto", () => dica.remove());
  map.on("mousemove", (e) => { $("coords").textContent = `LAT ${e.lngLat.lat.toFixed(2)} · LON ${e.lngLat.lng.toFixed(2)}`; });
  $("tg-voos").onchange = (e) => alternarVoos(e.target.checked);

  const varre = $("varre"), mapaEl = $("mapa");
  const posVarre = () => { const p = map.project(BRASILIA); varre.style.left = p.x + mapaEl.offsetLeft + "px"; varre.style.top = p.y + "px"; };
  map.on("move", posVarre); posVarre();
  const t0 = performance.now(); let q = 0;
  (function quadro(t) {
    if ((q++ & 1) && !map.isMoving()) { requestAnimationFrame(quadro); return; }
    if (!globoAtivo) overlay.setProps({ layers: camadas(((t - t0) / 2600) % 1.5) });
    requestAnimationFrame(quadro);
  })(t0);
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
  visiveis = alertas.filter((a) => noJanela(a) && (filtroG === "todas" || a.gravidade === filtroG) && (filtroR === "todas" || (filtroR === "__comb" ? !!a.correlacao : a.regra === filtroR)));
  lista(); atualizarMapa(); atualizarPanorama();
}
function lista() {
  $("itens").innerHTML = visiveis.slice(0, 200).map((a) => `
    <li class="card ${sel === a.id ? "sel" : ""} ${triagem()[a.id] === "descartado" ? "dim" : ""}" style="--c:${COR[a.gravidade]}" data-id="${esc(a.id)}">
      <div class="topo"><div class="nome">${esc(a.empresa)}</div><div class="valor num">${brlCurto(a.total)}</div></div>
      <div class="sub">${linhaCard(a)}</div>
      <div class="meta">${a.novo ? '<span class="chip" style="--c:#00ffa6">novo</span>' : ""}${a.correlacao ? '<span class="chip" style="--c:#b388ff">combinado</span>' : ""}${triagem()[a.id] && triagem()[a.id] !== "novo" ? `<span class="chip" style="--c:#8aa0b5">${triagem()[a.id]}</span>` : ""}${a.regra} · ${plural(a.n, "registro", "registros")} · ${periodo(a.inicio, a.fim).replace(/^(em|entre) /, "")}${a.local ? " · " + esc(a.local.cidade) + "/" + a.local.uf : ""}</div>
    </li>`).join("") || '<p class="sub2">Nenhum alerta neste filtro.</p>';
  $("itens").querySelectorAll(".card").forEach((c) => (c.onclick = () => abrir(c.dataset.id)));
  $("cont").textContent = `${visiveis.length} alertas${visiveis.length > 200 ? " (mostrando 200)" : ""}`;
}

// ---------- dossiê ----------
function abrir(id) {
  const a = alertas.find((x) => x.id === id); if (!a) return;
  sel = id; lista(); history.replaceState(null, "", "#" + encodeURIComponent(id));
  const c = COR[a.gravidade], t = a.tabela, s = a.sancao;
  const cab = t.cols.map((h, i) => `<th${i === 3 ? ' style="text-align:right"' : ""}>${h}</th>`).join("");
  const linhas = t.linhas.map((l) => "<tr>" + l.map((x) => `<td${x.v ? ' class="v num"' : ""}>${x.u ? `<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)}</a>` : x.s ? `<b>${esc(x.t)}</b><br><span class="sub2">${esc(x.s)}</span>` : esc(x.t)}</td>`).join("") + "</tr>").join("");
  const blocoSancao = s ? `<h4>A punição</h4><dl class="kv"><dt>Cadastro</dt><dd>${esc(listaNome[s.lista] || s.lista)}</dd><dt>Tipo</dt><dd>${esc(s.tipo)}</dd><dt>Aplicada por</dt><dd>${esc(s.orgao)}</dd><dt>Vigência</dt><dd>${s.fim ? `de ${data(s.inicio)} até ${data(s.fim)}` : `desde ${data(s.inicio)}, sem data final`}</dd><dt>Alcance</dt><dd>${alcance(s.alcance)}</dd></dl>` : "";
  const m = a.manchete;
  const blocoEmpresa = (m.tipo === "R03" || m.tipo === "R04") ? `<h4>A empresa</h4><dl class="kv">${m.abertura ? `<dt>Abertura</dt><dd>${data(m.abertura)}</dd>` : ""}<dt>Capital social</dt><dd>${m.capital != null ? brl(m.capital) : "não informado"}</dd><dt>Porte</dt><dd>${esc(PORTE[m.porte] || m.porte || "não informado")}</dd><dt>Contratante</dt><dd>${esc(a.orgao || "")}${a.orgao_municipio ? " · " + esc(a.orgao_municipio) + "/" + esc(a.orgao_uf) : ""}</dd></dl>` : "";
  const blocoVinculo = m.tipo === "R05" ? `<h4>O vínculo</h4><dl class="kv"><dt>Prefeito eleito</dt><dd>${esc(m.prefeito)} (${esc(m.partido)}) · ${esc(m.cidade)}/${esc(m.uf)}</dd><dt>Doador</dt><dd>${esc(m.doador)}, ${esc(QUALIF[m.qualificacao] || "sócio(a)")} da empresa</dd><dt>Doou</dt><dd>${brl(m.doacao)} na campanha de 2024</dd><dt>Fonte</dt><dd><a href="https://divulgacandcontas.tse.jus.br" target="_blank" rel="noopener">TSE · DivulgaCandContas</a></dd></dl>` : "";
  const meta = META[a.regra] || { conf: "média", fp: [] }, est = triagem()[a.id];
  const blocoCorr = a.correlacao ? `<h4>Sinais combinados</h4><p class="sub2" style="margin-bottom:6px">A mesma empresa aparece em mais de uma regra, o que pesa mais que um alerta isolado.</p><ul class="check">${a.correlacao.map((x) => { const o = alertas.find((z) => z.id === x.id); return `<li><a href="#" data-id="${esc(x.id)}">${esc(nomes[x.regra] || x.regra)}</a>${o ? ` <span class="sub2">· ${brlCurto(o.total)}</span>` : ""}</li>`; }).join("")}</ul>` : "";
  const blocoAcoes = `<h4>Análise</h4><div class="acoes">${[["visto", "Visto", ""], ["analise", "Em análise", "sx"], ["descartado", "Descartar", "sd"]].map(([k, l, cl]) => `<button class="botao ${cl} ${est === k ? "on" : ""}" data-st="${k}">${l}</button>`).join("")}</div>
    <p class="sub2">Confiança do dado: <b style="color:#fff">${esc(meta.conf)}</b>. Falsos positivos comuns: ${esc(meta.fp.join("; ") || "nenhum conhecido")}.</p>
    <div class="acoes" style="margin-top:6px"><a class="botao sx" href="${issueUrl(a)}" target="_blank" rel="noopener">Sinalizar erro nos dados</a><button class="botao" id="b-link">Copiar link</button></div>`;
  $("detalhe").hidden = false; $("detalhe").style.setProperty("--c", c);
  $("detalhe").innerHTML = `
    <button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:${c}"><span>DOSSIÊ · ${a.regra} · ${esc(nomes[a.regra] || "")}</span><span class="carimbo">PONTO DE ATENÇÃO</span></div>
    <h2 style="--c:${c}">${esc(a.empresa)}</h2>
    <div class="sub2 mono">CNPJ ${esc(a.cnpj)}${a.local ? " · " + esc(a.local.cidade) + "/" + esc(a.local.uf) : ""}</div>
    <div class="manchete" style="--c:${c}">${manchete(a)}</div>
    <div class="numeros" style="--c:${c}">${numeros(a)}</div>
    <h4>Rede de ligações</h4>${grafoSVG(a)}${linhaSVG(a) ? `<h4>Linha do tempo</h4>${linhaSVG(a)}` : ""}${blocoCorr}
    <h4>${esc(t.titulo)}</h4>
    <table style="--c:${c}"><thead><tr>${cab}</tr></thead><tbody>${linhas}</tbody></table>
    ${a.n > t.linhas.length ? `<p class="sub2" style="margin-top:6px">Mostrando ${t.linhas.length} de ${a.n} registros.</p>` : ""}
    ${blocoSancao}${blocoEmpresa}${blocoVinculo}${(dDiarios[a.id] || []).length ? `<h4>Diários oficiais</h4>${dDiarios[a.id].map((x) => `<div class="diario"><small>${esc(x.cidade)}/${esc(x.uf)} · ${esc(x.data)}</small>${esc(x.trecho)} <a href="${esc(x.url)}" target="_blank" rel="noopener">abrir diário</a></div>`).join("")}<p class="sub2">Menções ao nome da empresa em diários oficiais municipais (Querido Diário). Podem ser homônimos.</p>` : ""}${(a.secoes || []).map((x) => `<h4>${esc(x.titulo)}</h4><dl class="kv">${x.kv.map((k) => `<dt>${esc(k[0])}</dt><dd>${esc(k[1])}</dd>`).join("")}</dl>`).join("")}
    <h4>Checagem</h4><ul class="check">${checagem(a).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    ${blocoAcoes}
    <p class="aviso">Isto é um ponto de atenção feito a partir de dados públicos, não uma conclusão. Pode haver explicação legal.</p>
    <div class="links" style="margin-top:12px;font-size:12.5px">Fontes: <a href="https://www3.bcb.gov.br/ifdata" target="_blank" rel="noopener">Banco Central (IF.data)</a> · <a href="https://dados.cvm.gov.br" target="_blank" rel="noopener">CVM</a> · <a href="https://pncp.gov.br" target="_blank" rel="noopener">PNCP</a> · <a href="https://portaldatransparencia.gov.br/sancoes/consulta" target="_blank" rel="noopener">Portal da Transparência</a> · <a href="https://dadosabertos.camara.leg.br" target="_blank" rel="noopener">Câmara</a> · <a href="https://www12.senado.leg.br/transparencia/dados-abertos-transparencia/dados-abertos-ceaps" target="_blank" rel="noopener">Senado</a> · <a href="https://dadosabertos.rfb.gov.br" target="_blank" rel="noopener">Receita (CNPJ)</a></div>`;
  $("detalhe").querySelector(".fechar").onclick = fechar;
  $("detalhe").querySelectorAll("a[data-id]").forEach((x) => (x.onclick = (e) => { e.preventDefault(); abrir(x.dataset.id); }));
  $("detalhe").querySelectorAll("[data-st]").forEach((b) => (b.onclick = () => { const m2 = triagem(); if (m2[a.id] === b.dataset.st) delete m2[a.id]; else m2[a.id] = b.dataset.st; localStorage.setItem("radar.triagem", JSON.stringify(m2)); abrir(a.id); }));
  $("b-link").onclick = () => { navigator.clipboard && navigator.clipboard.writeText(location.origin + "/#" + encodeURIComponent(a.id)); $("b-link").textContent = "Link copiado"; };
  mostrarRota(a);
}
function fechar() { $("detalhe").hidden = true; sel = null; history.replaceState(null, "", location.pathname); lista(); limparRota(); map.fitBounds(MAPA_BOUNDS, { padding: pad(), duration: 900 }); }

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
    <div class="caixa"><b>${d.voos.length}</b> voos para <b>${d.paises.length}</b> países, somando <b>${brlCurto(tot)}</b>.</div><button class="botao" id="b-globo">Ver em globo 3D</button><span class="sub2"> mostra também os sócios em jurisdições de sigilo (R08)</span>
    <div class="rot">// por país</div><table class="tbl"><tbody>${d.paises.map((p) => `<tr><td>${esc(p.pais)}</td><td class="num" style="text-align:right">${p.n} voos</td><td class="num" style="text-align:right">${brlCurto(p.v)}</td></tr>`).join("")}</tbody></table>
    <div class="rot" style="margin-top:14px">// quem mais voou ao exterior com a cota</div>
    <table class="tbl"><tbody>${d.deputados.slice(0, 15).map((p) => `<tr><td><b>${esc(p.p)}</b><br><span class="sub2">${esc(p.pt || "")}${p.uf ? "/" + esc(p.uf) : ""} · ${Object.entries(p.paises).map(([k, v]) => k + " " + v).join(", ")}</span></td><td class="num" style="text-align:right">${p.n}</td><td class="num" style="text-align:right">${brlCurto(p.v)}</td></tr>`).join("")}</tbody></table>
    <p class="aviso">Voo ao exterior pago pela cota não é irregularidade por si só (há regras próprias de uso). Veja o trecho e o passageiro na nota da Câmara.</p>`;
  $("tg-voos").checked = true; alternarVoos(true);
  $("b-globo").onclick = () => { modoGlobo(!globoAtivo); $("b-globo").textContent = globoAtivo ? "Voltar ao mapa do Brasil" : "Ver em globo 3D"; };
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

// ---------- ferramentas de análise ----------
let globoAtivo = false;
const triagem = () => { try { return JSON.parse(localStorage.getItem("radar.triagem") || "{}"); } catch { return {}; } };
const META = {
  R01: { conf: "alta", fp: ["punição restrita a outro órgão", "empresa homônima"] },
  R02: { conf: "média", fp: ["punição que não alcança o órgão contratante", "contrato anterior à punição só republicado"] },
  R03: { conf: "média", fp: ["empresa criada para uma obra específica", "reorganização societária"] },
  R04: { conf: "baixa", fp: ["valor digitado errado no PNCP (escala por mil)", "contrato plurianual com valor global"] },
  R05: { conf: "média", fp: ["doação legal de quem já era fornecedor antes da eleição", "empresa única da cidade"] },
  R06: { conf: "média", fp: ["compras de naturezas diferentes", "fornecimento contínuo em ata"] },
  R07: { conf: "média", fp: ["mercado local com poucos fornecedores", "serviço contínuo como coleta de lixo ou saúde"] },
  R08: { conf: "média", fp: ["multinacional legítima com holding no exterior", "sócio estrangeiro de boa-fé"] },
  RF01: { conf: "média", fp: ["banco grande e legítimo em expansão", "instituição de pagamento mal classificada"] },
};
const issueUrl = (a) => "https://github.com/lucasnegrelli/radar-publico/issues/new?labels=dados&title=" + encodeURIComponent(`Dado suspeito: ${a.empresa} (${a.id})`) + "&body=" + encodeURIComponent(`Alerta: ${a.id}\nEmpresa: ${a.empresa}\n\nO que está errado ou como você verificou:\n\nLink da fonte conferida:\n`);
function exportarCSV() {
  const L = [["id", "regra", "prioridade", "empresa", "cnpj", "total_reais", "registros", "inicio", "fim", "cidade", "uf"]];
  visiveis.forEach((a) => L.push([a.id, a.regra, a.gravidade, a.empresa, a.cnpj, Math.round(a.total), a.n, a.inicio, a.fim, a.local ? a.local.cidade : "", a.local ? a.local.uf : ""]));
  const csv = L.map((r) => r.map((x) => `"${String(x ?? "").replace(/"/g, '""')}"`).join(";")).join("\n");
  const u = URL.createObjectURL(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" })); const l = document.createElement("a"); l.href = u; l.download = "radar-publico-alertas.csv"; l.click(); URL.revokeObjectURL(u);
}
const CORK = { org: "#00ffa6", pessoa: "#00b8ff", sancao: "#ff2d55", pais: "#b388ff", doador: "#ffb300", obra: "#8aa0b5" };
function grafoSVG(a) {
  const m = a.manchete, N = []; const org = a.orgao || (a.tabela.linhas[0] && a.tabela.linhas[0][1] && a.tabela.linhas[0][1].t) || "órgão contratante";
  if (m.tipo === "R01") { [...new Set(a.tabela.linhas.map((l) => l[1].t))].slice(0, 3).forEach((n) => N.push({ l: n, k: "pessoa", e: "cota" })); if (a.sancao) N.push({ l: `${a.sancao.lista}: ${situacaoCurta(a.sancao.tipo)}`, k: "sancao", e: "punida" }); }
  else if (m.tipo === "R05") { N.push({ l: `Prefeitura de ${m.cidade}`, k: "org", e: "contrata" }); N.push({ l: m.prefeito, k: "pessoa", e: "eleito", liga: 0 }); N.push({ l: m.doador, k: "doador", e: "sócio", liga: -1 }); N.push({ l: m.doador, k: "doador", e: "doou", liga: 1, so: 1 }); }
  else if (m.tipo === "R08") { N.push({ l: org, k: "org", e: "contrata" }); N.push({ l: `${m.pais}`, k: "pais", e: "sócio" }); }
  else if (m.tipo === "RF01") { N.push({ l: "Banco Central", k: "org", e: "supervisiona" }); N.push({ l: "Fundos (CVM)", k: "doador", e: "compram papel" }); }
  else { N.push({ l: org, k: "org", e: "contrata" }); if (a.sancao) N.push({ l: `${a.sancao.lista}: ${situacaoCurta(a.sancao.tipo)}`, k: "sancao", e: "punida" }); if (m.abertura) N.push({ l: `Aberta em ${data(m.abertura)}`, k: "obra", e: "abertura" }); }
  const nos = N.filter((n) => !n.so), cx = 220, cy = 92, W = 440, H = 184;
  nos.forEach((n, i) => { const ang = (-Math.PI / 2) + (i + 0.5) * (2 * Math.PI / nos.length) + (nos.length === 1 ? Math.PI / 2 : 0); n.x = cx + 160 * Math.cos(ang); n.y = cy + 66 * Math.sin(ang); });
  const cut = (x, n) => (x.length > n ? x.slice(0, n - 1) + "…" : x);
  const linhas = nos.map((n) => { const alvo = n.liga != null && n.liga >= 0 && nos[n.liga] ? nos[n.liga] : { x: cx, y: cy }; return `<line x1="${n.x}" y1="${n.y}" x2="${alvo.x}" y2="${alvo.y}" stroke="${CORK[n.k]}" stroke-opacity=".55" stroke-width="1.4"/><text x="${(n.x + alvo.x) / 2}" y="${(n.y + alvo.y) / 2 - 3}" text-anchor="middle" style="fill:#6f8aa3">${esc(n.e)}</text>`; }).join("");
  const bolas = nos.map((n) => `<circle cx="${n.x}" cy="${n.y}" r="9" fill="${CORK[n.k]}" fill-opacity=".25" stroke="${CORK[n.k]}"/><text x="${n.x}" y="${n.y + 21}" text-anchor="middle">${esc(cut(n.l, 24))}</text>`).join("");
  return `<svg class="viz" viewBox="0 0 ${W} ${H}">${linhas}<circle cx="${cx}" cy="${cy}" r="13" fill="#fff" fill-opacity=".9"/><text x="${cx}" y="${cy + 26}" text-anchor="middle" style="fill:#fff;font-weight:700">${esc(cut(a.empresa, 30))}</text>${bolas}</svg>`;
}
function linhaSVG(a) {
  const m = a.manchete, ev = []; const add = (d, l, k) => { if (d && /^\d{4}-\d{2}-\d{2}/.test(String(d))) ev.push({ d: String(d).slice(0, 10), l, k }); };
  add(m.abertura, "Empresa aberta", "#8aa0b5");
  if (a.sancao) { add(a.sancao.inicio, "Início da punição", "#ff2d55"); add(a.sancao.fim, "Fim da punição", "#ff2d55"); }
  if (m.tipo === "R05") { add("2024-10-06", "Eleição", "#ffb300"); add("2025-01-01", "Posse", "#ffb300"); }
  const ds = a.tabela.linhas.map((l) => l[0].t).filter((x) => /^\d{4}-\d{2}-\d{2}$/.test(x)).sort();
  if (ds.length) { add(ds[0], a.tabela.titulo === "Contratos" ? "1º contrato" : "1º pagamento", "#00ffa6"); if (ds.length > 1 && ds[ds.length - 1] !== ds[0]) add(ds[ds.length - 1], "Último", "#00ffa6"); }
  if (ev.length < 2) return "";
  ev.sort((x, y) => x.d.localeCompare(y.d)); const t0 = new Date(ev[0].d).getTime(), t1 = new Date(ev[ev.length - 1].d).getTime(), span = Math.max(1, t1 - t0);
  const mm = (d) => { const x = dt(d); return `${MES[x.m - 1]}/${String(x.a).slice(2)}`; };
  const pts = ev.map((e, i) => { const x = 30 + 380 * ((new Date(e.d).getTime() - t0) / span), up = i % 2 === 0; return `<line x1="${x}" y1="46" x2="${x}" y2="${up ? 30 : 62}" stroke="${e.k}"/><circle cx="${x}" cy="46" r="4.5" fill="${e.k}"/><text x="${x}" y="${up ? 22 : 74}" text-anchor="middle">${esc(e.l)}</text><text x="${x}" y="${up ? 12 : 85}" text-anchor="middle" style="fill:#6f8aa3">${mm(e.d)}</text>`; }).join("");
  return `<svg class="viz" viewBox="0 0 440 92"><line x1="20" y1="46" x2="420" y2="46" stroke="#1f3044" stroke-width="2"/>${pts}</svg>`;
}

// ---------- investigações (casos) ----------
let _casos = null;
async function montarCasos() {
  const d = (_casos ||= await fetch("/data/casos.json").then((r) => r.json()).catch(() => ({ casos: [] })));
  $("aba-casos").innerHTML = `<h3>Investigações</h3><p class="sub2">Dossiês de casos montados só com dados abertos: o que se consegue levantar, o que falta e quais são os próximos passos.</p>` +
    d.casos.map((c, i) => `<div class="card" style="--c:#00ffa6" data-i="${i}"><div class="topo"><div class="nome">${esc(c.titulo)}</div></div><div class="sub">${esc(c.resumo)}</div><div class="meta">${c.serie.length} trimestres · ${c.noticias.length} manchetes · ${c.achados.length} achados</div></div>`).join("") || '<p class="sub2">Nenhuma investigação cadastrada.</p>';
  $("aba-casos").querySelectorAll(".card").forEach((e) => (e.onclick = () => abrirCaso(d.casos[Number(e.dataset.i)])));
}
function serieSVG(s) {
  const W = 440, H = 190, px = 34, py = 14, n = s.length, mx = Math.max(...s.map((x) => x.ativo || 0)), X = (i) => px + (W - px - 12) * i / Math.max(1, n - 1), Y = (v) => H - 26 - (H - 26 - py) * (v / mx);
  const linha = (k, cor) => `<polyline fill="none" stroke="${cor}" stroke-width="2" points="${s.map((x, i) => (x[k] != null ? X(i) + "," + Y(x[k]) : "")).filter(Boolean).join(" ")}"/>`;
  const eixo = [0, 0.5, 1].map((f) => `<text x="2" y="${Y(mx * f) + 3}">${(mx * f / 1e9).toFixed(0)}</text><line x1="${px}" x2="${W - 8}" y1="${Y(mx * f)}" y2="${Y(mx * f)}" stroke="#1f3044"/>`).join("");
  const rot = [0, Math.floor(n / 2), n - 1].map((i) => `<text x="${X(i)}" y="${H - 8}" text-anchor="middle">${esc(s[i].tri)}</text>`).join("");
  return `<svg class="viz" viewBox="0 0 ${W} ${H}">${eixo}${linha("ativo", "#00ffa6")}${linha("captacao", "#ffb300")}${linha("pl", "#00b8ff")}${rot}</svg><div class="leg"><span><i style="background:#00ffa6"></i>Ativo</span><span><i style="background:#ffb300"></i>Captações</span><span><i style="background:#00b8ff"></i>Patrimônio líquido</span><span>R$ bilhões</span></div>`;
}
async function abrirCaso(c) {
  const dd = await fetch("/data/caso_" + c.id + "_diarios.json").then((r) => r.json()).catch(() => ({ diarios: [] }));
  const porCid = {}; dd.diarios.forEach((x) => { const k = x.cidade + "/" + x.uf; (porCid[k] ||= []).push(x); });
  const cidades = Object.entries(porCid).sort((a, b) => b[1].length - a[1].length);
  const ev = [...c.noticias.map((n) => ({ d: n.data, t: n.titulo, f: n.fonte, u: n.url }))].sort((a, b) => a.d.localeCompare(b.d));
  const ad = c.cadastro;
  $("detalhe").hidden = false; $("detalhe").style.setProperty("--c", "#00ffa6");
  $("detalhe").innerHTML = `<button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:#00ffa6"><span>INVESTIGAÇÃO · ${esc(c.id.toUpperCase())}</span><span class="carimbo">DADOS ABERTOS</span></div>
    <h2 style="--c:#00ffa6">${esc(c.titulo)}</h2><div class="sub2 mono">${esc(ad.razao_social)} · CNPJ base ${esc(ad.cnpj_basico)}</div>
    <h4>O que os dados mostram</h4>${c.achados.map((x) => `<div class="achado">${esc(x)}</div>`).join("")}
    ${c.serie.length ? `<h4>Balanço trimestral (Banco Central)</h4>${serieSVG(c.serie)}` : ""}
    ${c.exposicao_fundos.length ? `<h4>Fundos abertos com papel do banco (CVM)</h4><table class="tbl"><tbody>${c.exposicao_fundos.map((e) => `<tr><td>${esc(e.mes)}</td><td class="num">${e.fundos} fundos</td><td class="num" style="text-align:right">${brlCurto(e.valor)}</td></tr>`).join("")}</tbody></table>` : ""}
    <h4>Municípios que citam o banco nos diários oficiais</h4>${cidades.length ? `<p class="sub2">${dd.diarios.length} diários em ${cidades.length} municípios. Atos de comitês de investimento de institutos de previdência costumam citar aplicações. Cada menção precisa ser lida: pode ser aplicação, resgate ou só notícia.</p>
      ${cidades.slice(0, 40).map(([k, v]) => `<div class="diario"><small>${esc(k)} · ${v.length} diário${v.length > 1 ? "s" : ""} · mais recente ${esc(v[0].data)}</small>${esc((v[0].trechos[0] || "").slice(0, 300))} <a href="${esc(v[0].url)}" target="_blank" rel="noopener">abrir diário</a></div>`).join("")}` : '<p class="sub2">Busca nos diários ainda em andamento (roda no GitHub, pode levar um tempo).</p>'}
    <h4>Linha do tempo de manchetes</h4><table class="tbl"><tbody>${ev.slice(-25).map((e) => `<tr><td class="num sx" style="white-space:nowrap">${esc(e.d)}</td><td><a href="${esc(e.u)}" target="_blank" rel="noopener" style="color:#c9f3ea;text-decoration:none">${esc(e.t)}</a><br><span class="sub2">${esc(e.f)}</span></td></tr>`).join("")}</tbody></table>
    <h4>Cadastro (Receita Federal)</h4><dl class="kv"><dt>Capital social</dt><dd>${ad.capital_social != null ? brl(ad.capital_social) : "–"}</dd>${ad.estabelecimentos.slice(0, 4).map((e) => `<dt>${esc(e.tipo)}</dt><dd>${esc(e.cnpj)} · ${esc(e.uf)} · ${esc(e.situacao)}${e.situacao_desde ? " desde " + esc(e.situacao_desde) : ""}</dd>`).join("")}
      ${ad.administradores.map((x) => `<dt>${esc(x.cargo)}</dt><dd>${esc(x.nome)}${x.desde ? " · desde " + esc(x.desde) : ""}</dd>`).join("")}</dl>
    <h4>O que não dá para ver em dado aberto</h4><ul class="check">${c.lacunas.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    <h4>Próximos passos</h4><ul class="check">${c.proximos_passos.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    <p class="aviso">Dossiê montado só com dados públicos e manchetes de imprensa. Não faz acusação: organiza o que está disponível e aponta o que falta verificar.</p>
    <div class="links" style="margin-top:10px;font-size:12.5px">Fontes: ${c.fontes.map(esc).join(" · ")}</div>`;
  $("detalhe").querySelector(".fechar").onclick = () => { $("detalhe").hidden = true; };
}

// ---------- fontes (saúde dos dados) ----------
async function montarFontes() {
  const d = await fetch("/data/meta.json").then((r) => r.json()).catch(() => null);
  $("aba-fontes").innerHTML = d ? `<h3>Fontes e cobertura</h3><p class="sub2">O que cada base cobre, até quando, e o que ainda não vê. Um painel só é confiável se mostra seus próprios pontos cegos.</p>` +
    d.fontes.map((f) => `<div class="caixa"><b>${esc(f.fonte)}</b><br><span class="sub2">${esc(f.cobertura)}${f.linhas ? " · " + Number(f.linhas).toLocaleString("pt-BR") + " linhas" : ""} · atualizado ${esc(f.atualizado)}</span><p style="margin:6px 0 0;font-size:12.5px;color:var(--media)">Lacuna: ${esc(f.lacuna)}</p></div>`).join("") : '<p class="sub2">Metadados indisponíveis.</p>';
}

// ---------- globo 3D (vínculos com o exterior) ----------
function modoGlobo(on) {
  globoAtivo = on; map.setProjection({ type: on ? "globe" : "mercator" });
  if (on) {
    overlay.setProps({ layers: [] });
    if (!map.getSource("vinc-ext")) {
      const fs = alertas.filter((a) => a.regra === "R08" && a.local && a.manchete.pais_xy).map((a) => ({ type: "Feature", properties: { n: a.manchete.nivel }, geometry: { type: "LineString", coordinates: curva([a.manchete.pais_xy.lon, a.manchete.pais_xy.lat], [a.local.lon, a.local.lat], 50) } }));
      map.addSource("vinc-ext", { type: "geojson", data: { type: "FeatureCollection", features: fs } });
      map.addLayer({ id: "vinc-ext-brilho", type: "line", source: "vinc-ext", paint: { "line-color": "#b388ff", "line-width": 7, "line-blur": 6, "line-opacity": 0.35 } });
      map.addLayer({ id: "vinc-ext", type: "line", source: "vinc-ext", paint: { "line-color": ["case", ["==", ["get", "n"], 1], "#ff2d55", "#b388ff"], "line-width": 1.6, "line-opacity": 0.9 } });
    }
    map.setLayoutProperty("vinc-ext", "visibility", "visible"); map.setLayoutProperty("vinc-ext-brilho", "visibility", "visible");
    map.easeTo({ center: [-30, 15], zoom: 1.7, pitch: 0, duration: 1600 });
  } else {
    if (map.getLayer("vinc-ext")) { map.setLayoutProperty("vinc-ext", "visibility", "none"); map.setLayoutProperty("vinc-ext-brilho", "visibility", "none"); }
    map.easeTo({ pitch: 0, duration: 800 }); map.fitBounds(MAPA_BOUNDS, { padding: pad(), duration: 1200 });
  }
}

// ---------- abas ----------
$("abas").onclick = (e) => { const b = e.target.closest("button"); if (!b) return;
  [...$("abas").children].forEach((x) => x.classList.toggle("on", x === b));
  document.querySelectorAll(".aba").forEach((x) => x.classList.toggle("on", x.id === "aba-" + b.dataset.aba));
  if (b.dataset.aba === "fichas") carregarFichas();
  if (b.dataset.aba === "exterior") montarExterior();
  if (b.dataset.aba === "justica") montarJustica();
  if (b.dataset.aba === "casos") montarCasos();
  if (b.dataset.aba === "fontes") montarFontes(); };
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
const nComb = alertas.filter((a) => a.correlacao).length;
const selTipo = document.createElement("select"); selTipo.id = "tipo";
selTipo.innerHTML = `<option value="todas">Todos os tipos (${alertas.length})</option><option value="__comb">★ Sinais combinados (${nComb})</option>` + Object.keys(nomes).filter((r) => cont[r]).map((r) => `<option value="${r}">${esc(nomes[r])} (${cont[r]})</option>`).join("");
selTipo.onchange = () => { filtroR = selTipo.value; aplicarFiltro(); };
$("filtros").before(selTipo);
const contEl = document.createElement("div"); contEl.id = "cont"; contEl.className = "sub2"; contEl.style.margin = "0 0 10px"; $("itens").before(contEl);
const bCsv = document.createElement("button"); bCsv.className = "botao"; bCsv.textContent = "Exportar CSV"; bCsv.style.margin = "0 0 10px"; bCsv.onclick = () => exportarCSV(); $("itens").before(bCsv);

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

if (location.hash.length > 1) setTimeout(() => abrir(decodeURIComponent(location.hash.slice(1))), 1800);


// =====================================================================
// UX v5: indicadores, linha do tempo, camadas, busca global, dossiê em abas
// =====================================================================
{ // indicadores
  const emAtencao = alertas.filter((a) => a.gravidade !== "baixa").reduce((s, a) => s + (a.total || 0), 0);
  $("resumo").innerHTML = `<div class="kpi"><b>${alertas.length.toLocaleString("pt-BR")}</b><span>alertas</span></div><div class="kpi"><b>${brlCurto(emAtencao)}</b><span>em atenção</span></div><div class="kpi n"><b>${alertas.filter((a) => a.novo).length}</b><span>novos (14 dias)</span></div><div class="kpi c"><b>${alertas.filter((a) => a.correlacao).length}</b><span>combinados</span></div>`;
}

// ----- camadas -----
[["l-calor", "calor"], ["l-rotas", "rotas"], ["l-todas", "todas"], ["l-pontos", "pontos"]].forEach(([id, k]) => { $(id).onchange = (e) => { LAY[k] = e.target.checked; }; });

// ----- linha do tempo (arraste para filtrar por período) -----
function montarTimeline() {
  const por = {}; alertas.forEach((a) => { const m = (a.fim || a.inicio || "").slice(0, 7); if (!m || m < "2023-01") return; (por[m] ||= { alta: 0, media: 0, baixa: 0 })[a.gravidade]++; });
  const ks = Object.keys(por).sort(); if (ks.length < 2) { $("timeline").style.display = "none"; return; }
  const meses = []; let [y, m] = ks[0].split("-").map(Number); const [yf, mf] = ks[ks.length - 1].split("-").map(Number);
  while (y < yf || (y === yf && m <= mf)) { meses.push(`${y}-${String(m).padStart(2, "0")}`); if (++m > 12) { m = 1; y++; } }
  const n = meses.length, W = 1000, bw = W / n, max = Math.max(1, ...meses.map((k) => { const p = por[k] || {}; return (p.alta || 0) + (p.media || 0) + (p.baixa || 0); }));
  const barras = meses.map((k, i) => { const p = por[k] || { alta: 0, media: 0, baixa: 0 }; let y0 = 50; return ["baixa", "media", "alta"].map((g) => { const h = 46 * (p[g] || 0) / max; y0 -= h; return h > 0 ? `<rect x="${i * bw + 1}" y="${y0}" width="${Math.max(1, bw - 2)}" height="${h}" fill="${COR[g]}" opacity=".85"/>` : ""; }).join(""); }).join("");
  const rotulos = [0, Math.floor(n / 2), n - 1].map((i) => `<text x="${Math.min(W - 30, Math.max(2, i * bw))}" y="49" style="font:10px ui-monospace,monospace;fill:#7a8da3">${meses[i]}</text>`).join("");
  $("timeline").innerHTML = `<div class="tl-h"><span>Linha do tempo · alertas por mês de atividade</span><span id="tl-sel"></span><button id="tl-reset" hidden>limpar período</button></div><svg id="tl-svg" viewBox="0 0 ${W} 52" preserveAspectRatio="none"><rect id="tl-brush" y="0" height="52" fill="#22d3b6" opacity=".18" width="0"/>${barras}</svg>`;
  const svg = $("tl-svg"), br = $("tl-brush"); let ini = null;
  const idx = (e) => { const r = svg.getBoundingClientRect(); return Math.max(0, Math.min(n - 1, Math.floor(((e.clientX - r.left) / r.width) * n))); };
  const pinta = (a, b) => { const lo = Math.min(a, b), hi = Math.max(a, b); br.setAttribute("x", lo * bw); br.setAttribute("width", (hi - lo + 1) * bw); };
  svg.onpointerdown = (e) => { ini = idx(e); svg.setPointerCapture(e.pointerId); pinta(ini, ini); };
  svg.onpointermove = (e) => { if (ini != null) pinta(ini, idx(e)); };
  svg.onpointerup = (e) => { if (ini == null) return; const f = idx(e), lo = Math.min(ini, f), hi = Math.max(ini, f); ini = null;
    janela = [meses[lo], meses[hi]]; $("tl-sel").textContent = lo === hi ? meses[lo] : `${meses[lo]} a ${meses[hi]}`; $("tl-reset").hidden = false; aplicarFiltro(); };
  $("tl-reset").onclick = () => { janela = null; br.setAttribute("width", 0); $("tl-sel").textContent = ""; $("tl-reset").hidden = true; aplicarFiltro(); };
}
montarTimeline();

// ----- dossiê em abas -----
function tabificar() {
  const d = $("detalhe"); if (d.hidden) return; const num = d.querySelector(".numeros"); if (!num) return;
  const resto = []; for (let k = num.nextElementSibling; k; k = k.nextElementSibling) resto.push(k);
  const grupo = (t) => (/^(Rede de ligações|Linha do tempo|Sinais combinados)$/.test(t) ? "Rede e tempo" : /^(Análise|Checagem)$/.test(t) ? "Análise" : "Dados");
  const G = { "Dados": [], "Rede e tempo": [], "Análise": [] }; let atual = "Dados";
  resto.forEach((k) => { if (k.tagName === "H4") atual = grupo(k.textContent.trim()); G[atual].push(k); });
  const tabs = document.createElement("div"); tabs.className = "dtabs"; const panes = {};
  Object.entries(G).forEach(([nome, nos], i) => { if (!nos.length) return;
    const b = document.createElement("button"); b.textContent = nome; if (!panes.__p) b.classList.add("on"); tabs.appendChild(b);
    const p = document.createElement("div"); p.className = "dpane" + (!panes.__p ? " on" : ""); panes.__p = panes.__p || p; nos.forEach((n) => p.appendChild(n)); panes[nome] = p;
    b.onclick = () => { tabs.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b)); Object.entries(panes).forEach(([kk, pp]) => { if (kk !== "__p") pp.classList.toggle("on", pp === p); }); }; });
  num.after(tabs); let ult = tabs; Object.entries(panes).forEach(([kk, pp]) => { if (kk !== "__p") { ult.after(pp); ult = pp; } });
}
{ const _abrir = abrir; abrir = function (id) { _abrir(id); tabificar(); }; }

// ----- busca global (Ctrl+K) -----
const paleta = document.createElement("div"); paleta.id = "paleta";
paleta.innerHTML = '<div class="caixa-p"><input id="pal-in" placeholder="Buscar empresa, CNPJ, político, cidade ou caso..." autocomplete="off"><div class="res" id="pal-res"></div></div>';
document.body.appendChild(paleta);
let _indice = null, _sel = 0, _itens = [];
async function indice() {
  if (_indice) return _indice;
  await carregarFichas(); const dc = await fetch("/data/casos.json").then((r) => r.json()).catch(() => ({ casos: [] }));
  const L = [];
  alertas.forEach((a) => L.push({ g: "Alertas", t: a.empresa, s: `${nomes[a.regra] || a.regra}${a.local ? " · " + a.local.cidade + "/" + a.local.uf : ""}`, v: brlCurto(a.total), k: norm([a.empresa, a.cnpj, a.local && a.local.cidade, a.local && a.local.uf].join(" ")), go: () => abrir(a.id) }));
  fichas.forEach((f) => L.push({ g: "Agentes públicos", t: f.n, s: `${CARGO[f.t]}${f.c ? " · " + f.c : ""}${f.p ? " · " + f.p : ""}${f.u ? "/" + f.u : ""}`, v: f.n_alertas ? f.n_alertas + " alerta(s)" : "", k: f._k, go: () => abrirFicha(f) }));
  dc.casos.forEach((c) => L.push({ g: "Investigações", t: c.titulo, s: c.resumo, v: "", k: norm(c.titulo + " " + c.resumo), go: () => abrirCaso(c) }));
  return (_indice = L);
}
function pintaPaleta(lista) {
  _itens = lista; _sel = 0; const por = {}; lista.forEach((x) => (por[x.g] ||= []).push(x)); let i = 0;
  $("pal-res").innerHTML = lista.length ? Object.entries(por).map(([g, xs]) => `<div class="grp">${esc(g)}</div>${xs.map((x) => `<div class="it ${i++ === 0 ? "on" : ""}" data-i="${_itens.indexOf(x)}"><div><b>${esc(x.t)}</b><small>${esc(x.s)}</small></div><span class="v">${esc(x.v)}</span></div>`).join("")}`).join("") : '<div class="vazio">Nada encontrado. Tente o nome da empresa, o CNPJ ou a cidade.</div>';
  $("pal-res").querySelectorAll(".it").forEach((e) => { e.onclick = () => escolhe(Number(e.dataset.i)); e.onmousemove = () => { _sel = Number(e.dataset.i); marca(); }; });
}
const marca = () => $("pal-res").querySelectorAll(".it").forEach((e) => { const on = Number(e.dataset.i) === _sel; e.classList.toggle("on", on); if (on) e.scrollIntoView({ block: "nearest" }); });
function escolhe(i) { const x = _itens[i]; if (!x) return; fechaPaleta(); x.go(); }
async function buscaPaleta() {
  const q = norm($("pal-in").value).trim(); const L = await indice();
  if (!q) { pintaPaleta([...L.filter((x) => x.g === "Investigações"), ...alertas.filter((a) => a.gravidade === "alta").slice(0, 6).map((a) => L.find((x) => x.t === a.empresa && x.g === "Alertas")).filter(Boolean)]); return; }
  const ts = q.split(/\s+/); const hit = L.filter((x) => ts.every((t) => x.k.includes(t)));
  const ord = (x) => (norm(x.t).startsWith(q) ? 0 : norm(x.t).includes(q) ? 1 : 2);
  const por = {}; hit.sort((a, b) => ord(a) - ord(b)).forEach((x) => { const arr = (por[x.g] ||= []); if (arr.length < 6) arr.push(x); });
  pintaPaleta(["Alertas", "Agentes públicos", "Investigações"].flatMap((g) => por[g] || []));
}
function abrePaleta() { paleta.classList.add("on"); $("pal-in").value = ""; $("pal-in").focus(); buscaPaleta(); }
function fechaPaleta() { paleta.classList.remove("on"); }
$("b-busca").onclick = abrePaleta; paleta.onclick = (e) => { if (e.target === paleta) fechaPaleta(); };
$("pal-in").oninput = buscaPaleta;
document.addEventListener("keydown", (e) => {
  const tag = (document.activeElement && document.activeElement.tagName) || "";
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); abrePaleta(); return; }
  if (e.key === "/" && tag !== "INPUT" && tag !== "SELECT") { e.preventDefault(); abrePaleta(); return; }
  if (!paleta.classList.contains("on")) { if (e.key === "Escape" && !$("detalhe").hidden) $("detalhe").querySelector(".fechar").click(); return; }
  if (e.key === "Escape") fechaPaleta();
  else if (e.key === "ArrowDown") { e.preventDefault(); _sel = Math.min(_itens.length - 1, _sel + 1); marca(); }
  else if (e.key === "ArrowUp") { e.preventDefault(); _sel = Math.max(0, _sel - 1); marca(); }
  else if (e.key === "Enter") { e.preventDefault(); escolhe(_sel); }
});


// =====================================================================
// v6: panorama (rankings), painel recolhível
// =====================================================================
const pan = document.createElement("div"); pan.id = "panorama"; $("centro").appendChild(pan);
function atualizarPanorama() {
  const L = visiveis; if (!L.length) { pan.innerHTML = '<div class="pan-t">Panorama</div><div class="sub2">Nenhum alerta neste filtro.</div>'; return; }
  const soma = (f) => { const m = {}; L.forEach((a) => { const k = f(a); if (!k) return; const o = (m[k] ||= { n: 0, v: 0 }); o.n++; o.v += a.total || 0; }); return Object.entries(m).sort((x, y) => y[1].v - x[1].v); };
  const ufs = soma((a) => a.local && a.local.uf).slice(0, 6), tipos = soma((a) => nomes[a.regra] || a.regra).slice(0, 5);
  const c = { alta: 0, media: 0, baixa: 0 }; L.forEach((a) => c[a.gravidade]++); const tot = L.length;
  const barras = (arr) => { const mx = Math.max(1, ...arr.map((x) => x[1].v)); return arr.map(([k, o]) => `<div class="pan-l"><span>${esc(k)}</span><div class="barra"><i style="width:${Math.round(100 * o.v / mx)}%"></i></div><b class="num">${brlCurto(o.v)}</b></div>`).join(""); };
  pan.innerHTML = `<div class="pan-t">Panorama <span>${L.length.toLocaleString("pt-BR")} alertas${janela ? " · período filtrado" : ""}</span></div>
    <div class="pan-sev"><i style="width:${100 * c.alta / tot}%;background:${COR.alta}"></i><i style="width:${100 * c.media / tot}%;background:${COR.media}"></i><i style="width:${100 * c.baixa / tot}%;background:${COR.baixa}"></i></div>
    <div class="pan-leg"><span style="color:${COR.alta}">${c.alta} alta</span><span style="color:${COR.media}">${c.media} média</span><span style="color:${COR.baixa}">${c.baixa} baixa</span></div>
    <div class="pan-h">Estados com mais valor em atenção</div>${barras(ufs)}
    <div class="pan-h">Por tipo de alerta</div>${barras(tipos)}`;
}
atualizarPanorama();
const bPainel = document.createElement("button"); bPainel.id = "b-painel"; bPainel.title = "Recolher ou abrir a lista"; bPainel.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14"><path d="M15 6l-6 6 6 6"/></svg>'; $("app").appendChild(bPainel);
bPainel.onclick = () => { document.body.classList.toggle("sem-painel"); map.fitBounds(MAPA_BOUNDS, { padding: pad(), duration: 600 }); };
