// Dossiê de pessoa: reúne só dado aberto (TSE, Câmara, Senado) e mostra "pontos de atenção", nunca veredito.
const lotes = {};
async function carregarLote(id) {
  const k = id.slice(0, 2);
  lotes[k] ||= fetch(`/data/pessoas/s${k}.json`).then((r) => r.json()).catch(() => ({}));
  return (await lotes[k])[id];
}
let _extras = null;
const extras = async () => (_extras ||= fetch("/data/pessoas/extras.json").then((r) => r.json()).catch(() => ({})));
const vo_n = (v) => v.n.toLocaleString("pt-BR");
const SIT = (s, seg) => {
  const x = (s || "").toLowerCase();
  if (x.startsWith("eleito")) return "Eleito(a)";
  if (seg || x.startsWith("2")) return "Foi ao 2º turno";
  if (x.includes("não eleito") || x.includes("nao eleito")) return "Não eleito(a)";
  if (x.includes("suplente")) return "Suplente";
  if (x.includes("nulo") || !x) return "Resultado não informado";
  return s;
};
const ORIGEM = (o) => (o || "").replace(/^Recursos de /i, "").replace(/^Recursos /i, "").replace(/^\w/, (c) => c.toUpperCase());

export async function abrirPessoa(id, { $, esc, brlCurto, alertas, nomes, abrir, fechar }) {
  const el = $("detalhe");
  el.hidden = false;
  el.style.setProperty("--c", "#00ffa6");
  el.innerHTML = '<button class="fechar" aria-label="Fechar">×</button><p class="sub2" style="margin-top:40px">Carregando ficha...</p>';
  el.querySelector(".fechar").onclick = () => { el.hidden = true; history.replaceState(null, "", location.pathname); };
  const p = await carregarLote(id);
  if (!p) { el.innerHTML = '<button class="fechar">×</button><p class="aviso">Ficha não encontrada.</p>'; el.querySelector(".fechar").onclick = () => (el.hidden = true); return; }
  history.replaceState(null, "", "#p-" + id);
  const ex = (await extras())[id] || {};
  const c = "#00ffa6";
  const nomeBusca = encodeURIComponent('"' + p.n + '"');
  const alvo = (aid) => alertas.find((z) => z.id === aid);
  const ligaAlertas = (ids) => (ids || []).map((x) => { const a = alvo(x); return a ? `<a href="#" class="chip-al" data-id="${esc(x)}">${esc(a.empresa)} · ${brlCurto(a.total)}</a>` : ""; }).join(" ");

  const pontos = (p.pontos || []).map((x) => `<li><b>${esc(x.t)}</b><br><span class="sub2">${esc(x.d)}</span>${x.alertas ? `<div class="chips">${ligaAlertas(x.alertas)}</div>` : ""}</li>`).join("");

  const cand = (p.cand || []).map((k) => `<tr><td class="num">${k.ano}</td><td><b>${esc(k.cargo)}</b><br><span class="sub2">${esc(k.ue || (k.uf === "BR" ? "Brasil" : k.uf))}</span></td><td>${esc(k.partido)}</td><td>${esc(SIT(k.sit, k.segundo))}</td></tr>`).join("");

  const bensAnos = Object.entries(p.bens || {}).sort();
  const maxB = Math.max(1, ...bensAnos.map(([, v]) => v.total));
  const bens = bensAnos.map(([a, v]) => `<div class="barra-l"><span class="num">${a}</span><div class="trilho"><i style="width:${Math.max(2, Math.round(100 * v.total / maxB))}%"></i></div><b class="num">${brlCurto(v.total)}</b></div>`).join("");
  const ultB = bensAnos.length ? bensAnos[bensAnos.length - 1] : null;
  const topB = ultB && ultB[1].top ? `<table class="tbl"><tbody>${ultB[1].top.map((b) => `<tr><td><b>${esc(b[0])}</b><br><span class="sub2">${esc(b[1])}</span></td><td class="num" style="text-align:right">${brlCurto(b[2])}</td></tr>`).join("")}</tbody></table>` : "";

  const campAnos = Object.entries(p.camp || {}).sort().reverse();
  const camp = campAnos.map(([ano, k]) => {
    const maxO = Math.max(1, ...(k.origens || []).map((o) => o[1]));
    const orig = (k.origens || []).slice(0, 5).map((o) => `<div class="barra-l"><span style="font-size:11.5px">${esc(ORIGEM(o[0]))}</span><div class="trilho"><i style="width:${Math.max(2, Math.round(100 * o[1] / maxO))}%"></i></div><b class="num">${brlCurto(o[1])}</b></div>`).join("");
    const parte = (arr) => (arr || []).map((d) => `<tr><td><b>${esc(d.nome)}</b>${d.pj ? "" : ' <span class="sub2">(pessoa física)</span>'}${d.sanc ? ' <span class="tag-s">sancionada</span>' : ""}${d.alertas ? `<div class="chips">${ligaAlertas(d.alertas)}</div>` : ""}</td><td class="num" style="text-align:right">${brlCurto(d.v)}</td></tr>`).join("");
    return `<div class="bloco-camp"><h5>${ano}</h5>
      <div class="kp2"><div><b>${brlCurto(k.receita || 0)}</b><span>arrecadado</span></div><div><b>${brlCurto(k.despesa || 0)}</b><span>contratado em despesas</span></div></div>
      ${orig ? `<div class="sub2" style="margin:8px 0 2px">De onde veio o dinheiro</div>${orig}` : ""}
      ${(k.doadores || []).length ? `<div class="sub2" style="margin:10px 0 2px">Maiores doadores (sem partido e sem recurso próprio)</div><table class="tbl"><tbody>${parte(k.doadores)}</tbody></table>` : ""}
      ${(k.gastos || []).length ? `<div class="sub2" style="margin:10px 0 2px">Onde gastou</div><table class="tbl"><tbody>${k.gastos.map((g) => `<tr><td>${esc(g[0])}</td><td class="num" style="text-align:right">${brlCurto(g[1])}</td></tr>`).join("")}</tbody></table>` : ""}
      ${(k.fornecedores || []).length ? `<div class="sub2" style="margin:10px 0 2px">Maiores fornecedores da campanha</div><table class="tbl"><tbody>${parte(k.fornecedores)}</tbody></table>` : ""}</div>`;
  }).join("");

  const m = p.mandato;
  let mand = "";
  if (m) {
    const anos = Object.entries(m.anos || {});
    const mx = Math.max(1, ...anos.map(([, v]) => v));
    mand = `<h4>Cota parlamentar · ${esc(m.tipo)}</h4>${anos.map(([a, v]) => `<div class="barra-l"><span class="num">${a}</span><div class="trilho"><i style="width:${Math.max(2, Math.round(100 * v / mx))}%"></i></div><b class="num">${brlCurto(v)}</b></div>`).join("")}
      ${m.pct25 ? `<p class="sub2">Em 2025, gastou mais que ${m.pct25}% dos deputados.</p>` : ""}
      ${(m.forn || []).length ? `<table class="tbl"><tbody>${m.forn.map((f) => `<tr><td>${esc(f[0])}</td><td class="num" style="text-align:right">${brlCurto(f[1])}</td></tr>`).join("")}</tbody></table>` : ""}`;
  }
  const em = p.emendas;
  let emd = "";
  if (em) {
    const anos = Object.entries(em.anos).sort(); const mx = Math.max(1, ...anos.map(([, v]) => v));
    emd = `<h4>Emendas parlamentares (autor)</h4>${anos.slice(-8).map(([a, v]) => `<div class="barra-l"><span class="num">${a}</span><div class="trilho"><i style="width:${Math.max(2, Math.round(100 * v / mx))}%"></i></div><b class="num">${brlCurto(v)}</b></div>`).join("")}
      <div class="sub2" style="margin:8px 0 2px">Quem mais recebeu</div><table class="tbl"><tbody>${em.top.map((t) => `<tr><td>${esc(t[0])}</td><td class="num" style="text-align:right">${brlCurto(t[2])}</td></tr>`).join("")}</tbody></table>
      ${(em.alertas || []).length ? `<div class="sub2">Favorecidas com alerta:</div><div class="chips">${ligaAlertas(em.alertas)}</div>` : ""}`;
  }
  const vo = p.voos
    ? `<h4>Voos internacionais pagos com a cota</h4><div class="kp2"><div><b>${vo_n(p.voos)}</b><span>voos desde 2023</span></div><div><b>${brlCurto(p.voos.v)}</b><span>em passagens</span></div></div><p class="sub2">${Object.entries(p.voos.paises).map(([k, v]) => esc(k) + " " + v).join(" · ")}. A data é a de emissão da passagem; voo pago pela cota não é irregular por si só.</p>`
    : "";
  const emps = (p.empresas || []).length
    ? `<h4>Empresas em que consta como sócio(a)</h4><p class="sub2">Receita Federal: nome completo e 6 dígitos centrais do CPF coincidem. A base mostra o quadro atual, sem data de saída.</p>${p.empresas.map((e) => `<div class="emp"><div class="emp-t"><b>${esc(e.nome)}</b>${e.sanc ? ' <span class="tag-s">sancionada</span>' : ""}</div><div class="sub2">${esc(e.qual)} · ${esc(e.situacao || "")}${e.abertura ? " · aberta em " + esc(String(e.abertura).slice(0, 4)) : ""}${e.uf ? " · " + esc(e.uf) : ""}${e.capital != null ? " · capital " + brlCurto(Number(e.capital)) : ""}</div>${e.alertas ? `<div class="chips">${ligaAlertas(e.alertas)}</div>` : ""}</div>`).join("")}`
    : "";
  const off = (p.offshore || []).length
    ? `<h4>Possível ligação com empresas no exterior</h4><p class="sub2">Base pública do ICIJ (Offshore Leaks). O nome completo coincide, mas pode ser outra pessoa: confirme antes de concluir qualquer coisa.</p>${p.offshore.map((o) => `<div class="bloco-camp"><h5>${esc(o.nome)} · ${esc(o.fonte)}</h5>${(o.entidades || []).map((e) => `<div class="sub2">${esc(e.nome)} · ${esc(e.jurisdicao || "")}${e.inicio ? " · aberta em " + esc(e.inicio) : ""}${e.status ? " · " + esc(e.status) : ""}</div>`).join("") || '<div class="sub2">Sem empresa ligada nos dados.</div>'}<a href="https://offshoreleaks.icij.org/nodes/${esc(o.id)}" target="_blank" rel="noopener">ver no ICIJ</a></div>`).join("")}`
    : "";
  const ult = (p.cand || [])[0];
  const alvoTitulo = ult ? `${ult.cargo}${ult.ue ? " de " + ult.ue : ""}${ult.uf && ult.uf !== "BR" ? "/" + ult.uf : ""} · ${ult.partido} · ${ult.ano}` : (m ? m.tipo : "");
  el.innerHTML = `
    <button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:${c}"><span>FICHA · PESSOA</span><span class="carimbo">DADOS ABERTOS</span></div>
    <h2 style="--c:${c}">${esc(p.n)}</h2>
    <div class="sub2 mono">${p.u && p.u !== p.n ? "“" + esc(p.u) + "” · " : ""}${esc(alvoTitulo)}${p.nasc ? " · nasc. " + esc(p.nasc) : ""}${p.ocup ? " · " + esc(p.ocup.toLowerCase()) : ""}</div>
    ${ex.w ? `<div class="quem"><b>Quem é</b> ${esc(ex.w.x)} <a href="${esc(ex.w.u)}" target="_blank" rel="noopener">Wikipédia</a> <span class="sub2">(CC BY-SA)</span></div>` : ""}
    ${pontos ? `<h4>Pontos de atenção</h4><ul class="check pessoa-pontos">${pontos}</ul>` : '<div class="manchete" style="--c:' + c + '">Nenhum ponto de atenção apareceu nos cruzamentos feitos. Isso não significa que não exista; significa que estes dados abertos não mostram.</div>'}
    <h4>Candidaturas</h4><table class="tbl"><tbody>${cand || '<tr><td class="sub2">Sem candidatura nos dados de 2018, 2022 e 2024.</td></tr>'}</tbody></table>
    ${emps}
    ${bens ? `<h4>Patrimônio declarado à Justiça Eleitoral</h4>${bens}${topB}` : ""}
    ${camp ? `<h4>Campanhas</h4>${camp}` : ""}
    ${mand}
    ${emd}
    ${vo}
    ${off}
    ${(ex.n || []).length ? `<h4>Na imprensa</h4><ul class="check">${ex.n.map((n) => `<li><a href="${esc(n[3])}" target="_blank" rel="noopener">${esc(n[2])}</a><br><span class="sub2">${esc(n[1])}${n[0] ? " · " + esc(n[0]) : ""}</span></li>`).join("")}</ul><p class="sub2">Manchetes automáticas do Google Notícias que citam o nome. Podem tratar de pessoas homônimas.</p>` : ""}
    <h4>Ver mais</h4>
    <div class="links" style="font-size:12.5px"><a href="https://news.google.com/search?q=${nomeBusca}&hl=pt-BR&gl=BR&ceid=BR:pt-419" target="_blank" rel="noopener">notícias</a> · <a href="https://queridodiario.ok.org.br/pesquisa?term=${nomeBusca}" target="_blank" rel="noopener">diários oficiais</a> · <a href="https://divulgacandcontas.tse.jus.br/divulga/" target="_blank" rel="noopener">DivulgaCand (TSE)</a> · <a href="https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?termo=${encodeURIComponent(p.n)}" target="_blank" rel="noopener">Portal da Transparência</a></div>
    <p class="aviso">Ficha montada só com dados abertos, sem avaliação de conduta. Doar, receber doação, ter patrimônio e contratar fornecedores é normal em campanha; o Radar só mostra onde vale olhar. Pessoa física aparece com nome abreviado. Pessoas com o mesmo nome podem ser confundidas: confira a data de nascimento.</p>`;
  el.querySelector(".fechar").onclick = () => { el.hidden = true; history.replaceState(null, "", location.pathname); };
  el.querySelectorAll("a[data-id]").forEach((x) => (x.onclick = (e) => { e.preventDefault(); abrir(x.dataset.id); }));
  el.scrollTop = 0;
}
