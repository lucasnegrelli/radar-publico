// Textos e regras de leitura dos alertas, extraídos do painel original (main.js) para a nova interface.
const COR = { alta: "#ff2d55", media: "#ffb300", baixa: "#00b8ff" };
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));


// ---------- formatação ----------
const MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const dt = (s) => { const [a, m, d] = s.split("-").map(Number); return { a, m, d }; };
const data = (s) => { if (!s) return "data não informada"; const x = dt(s); return `${x.d} ${MES[x.m - 1]} ${x.a}`; };
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

// etiqueta de confiança do R11 (contrato novo assinado durante a punição?)
function chipContrato(a) {
  const c = a.contratos; if (!c) return "";
  const t = c.sinal === "contrato_novo" ? ["contrato novo", "#ff2d55", "Há contrato assinado depois do início da punição"]
    : c.sinal === "so_contrato_anterior" ? ["contrato antigo", "#8aa0b5", "Só há contratos anteriores à punição: provável pagamento de contrato antigo"]
    : ["origem incerta", "#8aa0b5", "Nenhum contrato dessa empresa no PNCP"];
  return `<span class="chip" style="--c:${t[1]}" title="${t[2]}">${t[0]}</span>`;
}
// ---------- textos por regra ----------
function fraseContratoR11(m) {
  const c = m.contratos; if (!c) return "";
  if (c.sinal === "contrato_novo") return ` Assinou <b>${plural(c.novos, "contrato novo", "contratos novos")}</b> (${brl(c.valor_novos)}) já durante a punição.`;
  if (c.sinal === "so_contrato_anterior") return " Só achamos contratos <b>anteriores</b> à punição: pode ser pagamento de contrato antigo.";
  return " Não achamos contrato dessa empresa no PNCP: não dá para saber de onde veio o pagamento.";
}
function manchete(a) {
  const m = a.manchete, E = `<b>${esc(a.empresa)}</b>`;
  if (m.tipo === "R01") return `${E} recebeu <b>${brl(a.total)}</b> em ${plural(a.n, "pagamento", "pagamentos")} da cota parlamentar ${periodo(a.inicio, a.fim)}, num período em que constava como <b>${situacao(m.sancao)}</b> no ${esc(m.lista)}.`;
  if (m.tipo === "R02") return `${E} assinou ${plural(a.n, "contrato público", "contratos públicos")} somando <b>${brl(a.total)}</b> ${periodo(a.inicio, a.fim)}, num período em que constava como <b>${situacao(m.sancao)}</b> no ${esc(m.lista)}.`;
  if (m.tipo === "R12") return `${E} vendeu <b>${brl(a.total)}</b> ao governo federal ${periodo(a.inicio, a.fim)} (${plural(a.n, "contrato", "contratos")}, ${esc(a.orgao)}). Entre os sócios há <b>${plural(m.n_servidores, "servidor federal ativo", "servidores federais ativos")}</b>${m.administradores ? ", dos quais <b>" + m.administradores + " na administração da empresa</b>" : " (como cotistas)"}.`;
  if (m.tipo === "R11") return `${E} recebeu <b>${brl(a.total)}</b> do governo federal ${periodo(a.inicio, a.fim)} (${plural(a.n, "pagamento mensal", "pagamentos mensais")}), em meses em que constava como <b>${esc(situacaoCurta(m.sancao))}</b> com punição que alcança a União. Quem mais pagou: ${m.orgaos.map(esc).join(", ")}.${fraseContratoR11(m)}`;
  if (m.tipo === "R10") return `${E} vendeu <b>${brl(a.total)}</b> a ${esc(a.orgao)}${m.orgaos.length > 1 ? " e outros órgãos" : ""} ${periodo(a.inicio, a.fim)}. Consta como sócio(a) <b>${esc(m.politico)}</b>, ${esc(m.cargo.toLowerCase())} eleito(a) em ${m.ano} (${esc(m.partido)}/${esc(m.uf)}).${m.mesmo_municipio ? " O contrato é com o próprio município onde exerce o mandato." : ""}${m.apos_posse ? "" : " Os contratos são anteriores à posse."}`;
  if (m.tipo === "R09") return `${E} recebeu <b>${brl(a.total)}</b> em ${plural(a.n, "pagamento", "pagamentos")} de emendas parlamentares ${periodo(a.inicio, a.fim)}. Autor${m.autores.length > 1 ? "es principais" : ""}: <b>${m.autores.map((x) => esc(x.nome)).join(", ")}</b>.${m.sancao ? " A empresa constava em lista de sancionadas no período." : ""}${m.cepim ? " A entidade consta no CEPIM (impedida de receber transferências federais): " + esc(String(m.cepim).toLowerCase()) + "." : ""}${m.nova ? " Foi aberta menos de um ano antes do primeiro pagamento." : ""}${m.capital_peq ? " O valor recebido é muito maior que o capital social." : ""}`;
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
  if (m.tipo === "R12") return `${plural(m.n_servidores, "servidor federal", "servidores federais")} entre os sócios${m.administradores ? ", " + m.administradores + " administrando" : ""}`;
  if (m.tipo === "R11") return `${situacaoCurta(m.sancao)} nos meses em que recebeu verba federal`;
  if (m.tipo === "R10") return `Sócio: ${m.politico} (${m.cargo.toLowerCase()}, ${m.partido}/${m.uf})`;
  if (m.tipo === "R09") return `Recebeu verba de emenda de ${m.autores[0] ? m.autores[0].nome : "parlamentar"}${m.n_autores > 1 ? " e mais " + (m.n_autores - 1) : ""}: ${[m.cepim && "impedida (CEPIM)", m.sancao && "sancionada", m.nova && "empresa nova", m.capital_peq && "capital pequeno"].filter(Boolean).join(", ")}`;
  if (m.tipo === "R08") return `Sócio sediado em ${m.pais}, jurisdição de ${m.nivel === 1 ? "sigilo clássico" : "tributação favorecida"}`;
  if (m.tipo === "R06") return `${a.n} contratos pequenos no mesmo trimestre, todos abaixo do limite de dispensa`;
  if (m.tipo === "R07") return `Fica com ${Math.round(m.share * 100)}% do dinheiro contratado pela prefeitura em ${m.ano}`;
  if (m.tipo === "RF01") return m.ref ? `Caso de referência: o critério acenderia ${m.trimestres} trimestres antes da liquidação` : `Crescimento acelerado e alavancado há ${m.trimestres} trimestres`;
  if (m.tipo === "R05") return `Sócio doou ${brlCurto(m.doacao)} ao prefeito e a empresa fechou contrato com a prefeitura`;
  if (m.tipo === "R03") return `Aberta há ${m.dias} dias quando assinou o contrato`;
  return `Contrato ${(m.vezes || 0).toLocaleString("pt-BR")}× maior que o capital da empresa`;
}

const MIN = new Set(["DE", "DA", "DO", "DAS", "DOS", "E", "EM", "NA", "NO"]), SIGLA = /^(LTDA|EIRELI|ME|EPP|SA|S\/A|CIA|MEI|SPE|ONG|CNPJ|UFRJ|USP|II|III|IV|TI)$/;
const bonito = (n) => { const t = String(n || ""); if (t !== t.toUpperCase()) return t; return t.toLowerCase().split(/(\s+)/).map((w, i) => { const u = w.toUpperCase(); return /\d/.test(u) || (u.length <= 3 && !/[AEIOU]/.test(u)) ? u : SIGLA.test(u) ? (u === "SA" ? "S.A." : u === "LTDA" ? "Ltda." : u) : MIN.has(u) && i > 0 ? w : w.charAt(0).toUpperCase() + w.slice(1); }).join(""); };
let listaTodos = false;

const curta = (a) => { const s = manchete(a).replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').trim(); const p = s.split(/(?<=\.)\s/)[0]; return p.length > 175 ? p.slice(0, 172) + "…" : p; };

const RCOR = { R01: "#ff6b81", R02: "#ff2d55", R03: "#ffb300", R04: "#ff8a3d", R05: "#f7d046", R06: "#7cf5de", R07: "#22d3b6", R08: "#b388ff", R09: "#4cc9f0", R10: "#ff7ad9", R11: "#6ea8ff", RF01: "#ffcc00" };
const RNOME = { R01: "Cota × punida", R02: "Contrato × punida", R03: "Empresa nova", R04: "Capital pequeno", R05: "Doador → fornecedor", R06: "Fracionamento", R07: "Concentração", R08: "Sócio no exterior", R09: "Emenda", R10: "Político sócio", R11: "Pgto federal × punida", RF01: "Banco" };

const PESO_R = { R11: 30, R10: 40, R09: 25, R01: 30, R02: 25, R08: -5, R05: 15, R03: 0, R04: -25, R06: -20, R07: -30, RF01: 30 };
function pontuar(a) {
  const m = a.manchete || {};
  return (a.gravidade === "alta" ? 100 : a.gravidade === "media" ? 40 : 0) + 14 * Math.log10(Math.max(a.total || 0, 1e4)) + (a.correlacao ? 45 : 0) + (PESO_R[a.regra] || 0)
    + (a.novo ? 10 : 0) + (m.politico ? 15 : 0) + ((m.autores || []).length ? 10 : 0) + (m.cepim || m.sancao ? 20 : 0);
}

export { esc, brl, brlCurto, plural, manchete, linhaCard, curta, bonito, RNOME, RCOR, pontuar, periodo, data };
