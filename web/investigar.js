// Bancada de investigação: busca uma empresa ou pessoa, abre a ficha com os cruzamentos e deixa o usuário montar, anotar e compartilhar a própria investigação.
const lotes = {};
async function lote(cnpj) {
  const k = cnpj.slice(6, 8);
  lotes[k] ||= fetch(`/data/empresas/e${k}.json`).then((r) => r.json()).catch(() => ({}));
  return (await lotes[k])[cnpj];
}

const KEY = "radar.invest";
export const carregaInv = () => { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch { return []; } };
const salvaInv = (v) => localStorage.setItem(KEY, JSON.stringify(v));
export function adicionaInv(item) {
  const v = carregaInv();
  if (!v.find((x) => x.t === item.t && x.id === item.id)) { v.push({ ...item, nota: "" }); salvaInv(v); }
  return v.length;
}
const b64 = (o) => btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const deb64 = (s) => JSON.parse(decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/")))));
export function importaDoHash() {
  const m = location.hash.match(/^#inv=(.+)$/);
  if (!m) return false;
  try { const v = deb64(m[1]); if (Array.isArray(v)) { salvaInv(v); return true; } } catch {}
  return false;
}
const SIT = { ativa: "Ativa", baixada: "Baixada", inapta: "Inapta", suspensa: "Suspensa", nula: "Nula" };

export async function abrirEmpresa(cnpj, ctx) {
  const { $, esc, brlCurto, alertas, abrir, abrirPessoa, onInv } = ctx;
  const el = $("detalhe"); el.hidden = false; el.style.setProperty("--c", "#4cc9f0");
  el.innerHTML = '<button class="fechar" aria-label="Fechar">×</button><p class="sub2" style="margin-top:40px">Carregando empresa...</p>';
  el.querySelector(".fechar").onclick = () => { el.hidden = true; history.replaceState(null, "", location.pathname); };
  const f = await lote(cnpj);
  if (!f) { el.innerHTML = '<button class="fechar">×</button><p class="aviso">Empresa fora da base de investigação (só entram empresas com alerta, contrato, emenda ou doação relevantes).</p>'; el.querySelector(".fechar").onclick = () => (el.hidden = true); return; }
  history.replaceState(null, "", "#e-" + cnpj);
  const fmt = (d) => `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`;
  const alv = (id) => alertas.find((a) => a.id === id);
  const chips = (arr) => (arr || []).map((a) => { const x = alv(a.id); return x ? `<a href="#" class="chip-al" data-id="${esc(a.id)}">${esc(x.empresa)} · ${brlCurto(x.total)}</a>` : ""; }).join(" ");
  const ab = f.abertura ? `${String(f.abertura).slice(0, 4)}` : "";
  const sinais = [];
  if (f.sancoes) sinais.push(["Consta em lista de sancionadas", f.sancoes.map((s) => `${s.lista}: ${s.tipo}`).join(" · ")]);
  if (f.politicos && f.politicos.length) sinais.push(["Tem político eleito entre os sócios", f.politicos.map((p) => p.nome).join(", ")]);
  if (f.emendas && f.emendas.total >= 100000) sinais.push(["Recebeu emendas parlamentares", brlCurto(f.emendas.total)]);
  if (f.doacoes && f.doacoes.total >= 50000) sinais.push(["Doou a campanhas eleitorais", brlCurto(f.doacoes.total)]);
  if (f.contratos && f.emendas) sinais.push(["Tem contrato com governo e também recebe emenda", brlCurto(f.contratos.total) + " em contratos"]);
  if (f.abertura && f.contratos && f.contratos.total > 1e6 && new Date().getFullYear() - Number(String(f.abertura).slice(0, 4)) <= 1) sinais.push(["Empresa com menos de 1 ano e contratos acima de R$ 1 mi", ab]);
  el.innerHTML = `<button class="fechar" aria-label="Fechar">×</button>
    <div class="dos" style="--c:#4cc9f0"><span>FICHA · EMPRESA</span><span class="carimbo">DADOS ABERTOS</span></div>
    <h2 style="--c:#4cc9f0">${esc(f.nome)}</h2>
    <div class="sub2 mono">CNPJ ${fmt(f.cnpj)} · ${esc(SIT[f.situacao] || f.situacao || "")}${ab ? " · aberta em " + ab : ""}${f.uf ? " · " + esc(f.uf) : ""}${f.capital != null ? " · capital " + brlCurto(Number(f.capital)) : ""}</div>
    <div class="acoes" style="margin:10px 0"><button class="botao" id="b-inv">+ Minha investigação</button></div>
    ${sinais.length ? `<h4>Cruzamentos que chamam atenção</h4><ul class="check pessoa-pontos">${sinais.map((s) => `<li><b>${esc(s[0])}</b><br><span class="sub2">${esc(s[1])}</span></li>`).join("")}</ul>` : ""}
    ${(f.alertas || []).length ? `<h4>Alertas do Radar</h4><div class="chips">${chips(f.alertas)}</div>` : ""}
    ${f.contratos ? `<h4>Contratos com o governo (desde 2025)</h4><div class="kp2"><div><b>${brlCurto(f.contratos.total)}</b><span>${f.contratos.n} contrato(s)</span></div></div><table class="tbl"><tbody>${(f.contratos.orgaos || []).map((o) => `<tr><td>${esc(o[0])}</td><td class="num" style="text-align:right">${brlCurto(o[1])}</td></tr>`).join("")}</tbody></table>` : ""}
    ${f.emendas ? `<h4>Emendas parlamentares recebidas</h4><div class="kp2"><div><b>${brlCurto(f.emendas.total)}</b><span>no total (todos os anos)</span></div></div><table class="tbl"><tbody>${f.emendas.autores.map((a) => `<tr><td>${esc(a[0])}</td><td class="num" style="text-align:right">${brlCurto(a[1] || 0)}</td></tr>`).join("")}</tbody></table>` : ""}
    ${f.doacoes ? `<h4>Doações a campanhas</h4><div class="kp2"><div><b>${brlCurto(f.doacoes.total)}</b><span>doados a candidatos</span></div></div><table class="tbl"><tbody>${f.doacoes.para.map((d) => `<tr><td>${esc(d[0])} <span class="sub2">${d[1]}</span></td><td class="num" style="text-align:right">${brlCurto(d[2])}</td></tr>`).join("")}</tbody></table>` : ""}
    ${(f.sancoes || []).length ? `<h4>Sanções</h4><table class="tbl"><tbody>${f.sancoes.map((s) => `<tr><td><b>${esc(s.lista)}</b> · ${esc(s.tipo)}<br><span class="sub2">${esc(s.orgao || "")}${s.ini ? " · " + esc(s.ini) : ""}${s.fim ? " a " + esc(s.fim) : ""}</span></td></tr>`).join("")}</tbody></table>` : ""}
    <h4>Sócios e administradores</h4><p class="sub2">Quadro atual (Receita). Pessoas físicas aparecem com nome abreviado; políticos eleitos aparecem completos, com link.</p>
    <table class="tbl"><tbody>${(f.socios || []).map((s) => `<tr><td>${s.politico ? `<b>${esc(s.nome)}</b> <span class="tag-s" style="background:rgba(255,122,217,.15);color:#ff7ad9">político</span>` : esc(s.nome)}</td><td class="sub2" style="text-align:right">${esc(s.qual || "")}</td></tr>`).join("") || '<tr><td class="sub2">Sem sócios listados.</td></tr>'}</tbody></table>
    ${(f.politicos || []).length ? `<div class="chips">${f.politicos.map((p) => `<a href="#" class="chip-al" data-p="${esc(p.id)}" style="color:#ff9ee5">${esc(p.nome)} · ficha</a>`).join(" ")}</div>` : ""}
    <p class="aviso">Cruzamento de bases públicas. Ligação entre bases não é prova de irregularidade: confira os documentos de origem antes de concluir qualquer coisa.</p>`;
  el.querySelector(".fechar").onclick = () => { el.hidden = true; history.replaceState(null, "", location.pathname); };
  el.querySelectorAll("a[data-id]").forEach((x) => (x.onclick = (e) => { e.preventDefault(); abrir(x.dataset.id); }));
  el.querySelectorAll("a[data-p]").forEach((x) => (x.onclick = (e) => { e.preventDefault(); abrirPessoa(x.dataset.p); }));
  $("b-inv").onclick = () => { adicionaInv({ t: "e", id: f.cnpj, nome: f.nome }); $("b-inv").textContent = "Adicionada ✓"; if (onInv) onInv(); };
  el.scrollTop = 0;
}

export function montarInvestigar(ctx) {
  const { $, esc, brlCurto, abrirPessoa } = ctx;
  const el = $("aba-investigar");
  let idxE = null, idxP = null;
  const desenhaTrilha = () => {
    const v = carregaInv();
    $("inv-trilha").innerHTML = v.length ? v.map((x, i) => `<div class="inv-it"><div class="inv-h"><a href="#" data-i="${i}">${x.t === "e" ? "🏢" : "👤"} ${esc(x.nome)}</a><button data-del="${i}" title="Tirar">×</button></div><textarea data-nota="${i}" placeholder="Anotação: o que você achou aqui?">${esc(x.nota || "")}</textarea></div>`).join("") : '<p class="sub2">Vazia. Abra uma empresa ou pessoa e toque em "+ Minha investigação".</p>';
    $("inv-trilha").querySelectorAll("a[data-i]").forEach((a) => (a.onclick = (e) => { e.preventDefault(); const x = carregaInv()[Number(a.dataset.i)]; x.t === "e" ? abrirEmpresa(x.id, ctx) : abrirPessoa(x.id); }));
    $("inv-trilha").querySelectorAll("[data-del]").forEach((b) => (b.onclick = () => { const w = carregaInv(); w.splice(Number(b.dataset.del), 1); salvaInv(w); desenhaTrilha(); }));
    $("inv-trilha").querySelectorAll("textarea").forEach((t) => (t.oninput = () => { const w = carregaInv(); w[Number(t.dataset.nota)].nota = t.value; salvaInv(w); }));
  };
  ctx.onInv = desenhaTrilha;
  el.innerHTML = `<h3>Investigar</h3><p class="sub2">Pesquise qualquer empresa (nome ou CNPJ) ou político e siga as ligações: sócios, contratos, emendas, doações, sanções. Monte sua investigação, anote e compartilhe o link.</p>
    <input id="inv-q" type="search" placeholder="Nome da empresa, CNPJ ou político..." autocomplete="off"><div id="inv-res"></div>
    <h4 style="margin-top:18px">Minha investigação</h4><div id="inv-trilha"></div>
    <div class="acoes"><button class="botao" id="inv-link">Copiar link para compartilhar</button> <button class="botao" id="inv-md">Copiar como texto</button> <button class="botao" id="inv-limpa">Limpar</button></div>
    <p class="sub2" id="inv-msg"></p>`;
  desenhaTrilha();
  const busca = async () => {
    const q = $("inv-q").value.trim(); const nq = q.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    if (nq.length < 3) { $("inv-res").innerHTML = '<div class="rot">// digite pelo menos 3 letras ou o CNPJ</div>'; return; }
    idxE ||= (await fetch("/data/empresas/idx.json").then((r) => r.json()).catch(() => ({ e: [] }))).e;
    idxP ||= (await fetch("/data/pessoas/idx.json").then((r) => r.json()).catch(() => ({ p: [] }))).p;
    const dig = q.replace(/\D/g, ""), ts = nq.split(/\s+/);
    const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
    const E = (dig.length >= 6 ? idxE.filter((r) => r[0].includes(dig)) : idxE.filter((r) => { const k = norm(r[1]); return ts.every((t) => k.includes(t)); })).slice(0, 12);
    const P = dig.length >= 6 ? [] : idxP.filter((r) => { const k = norm(r[1] + " " + r[2]); return ts.every((t) => k.includes(t)); }).slice(0, 8);
    $("inv-res").innerHTML = (E.length ? '<div class="rot">// empresas</div>' + E.map((r) => `<div class="card" style="--c:#4cc9f0" data-e="${r[0]}"><div class="topo"><div class="nome">${esc(r[1])}</div><div class="valor num">${r[3] ? brlCurto(r[3]) : ""}</div></div><div class="sub">${r[2] || ""}${r[4] ? " · " + r[4] + " alerta(s)" : ""}${r[5] ? " · tem político entre os sócios" : ""}</div></div>`).join("") : "")
      + (P.length ? '<div class="rot">// pessoas</div>' + P.map((r) => `<div class="card" style="--c:#00ffa6" data-p="${r[0]}"><div class="topo"><div class="nome">${esc(r[1])}</div></div><div class="sub">${esc(r[5])} · ${esc(r[3] || "")}${r[4] && r[4] !== "BR" ? "/" + esc(r[4]) : ""} · ${r[6]}</div></div>`).join("") : "") || '<p class="sub2">Nada encontrado. A base cobre empresas com alerta, contrato, emenda ou doação relevantes.</p>';
    $("inv-res").querySelectorAll("[data-e]").forEach((c) => (c.onclick = () => abrirEmpresa(c.dataset.e, ctx)));
    $("inv-res").querySelectorAll("[data-p]").forEach((c) => (c.onclick = () => abrirPessoa(c.dataset.p)));
  };
  let t0; $("inv-q").oninput = () => { clearTimeout(t0); t0 = setTimeout(busca, 250); };
  $("inv-link").onclick = () => { const url = location.origin + "/#inv=" + b64(carregaInv()); navigator.clipboard && navigator.clipboard.writeText(url); $("inv-msg").textContent = "Link copiado. Quem abrir verá a sua investigação com as anotações."; };
  $("inv-md").onclick = () => { const md = "# Minha investigação (Radar Público)\n\n" + carregaInv().map((x) => `- **${x.nome}** (${x.t === "e" ? "empresa " + x.id : "pessoa"})${x.nota ? "\n  - " + x.nota.replace(/\n/g, " ") : ""}`).join("\n") + "\n\nFonte: " + location.origin; navigator.clipboard && navigator.clipboard.writeText(md); $("inv-msg").textContent = "Texto copiado."; };
  $("inv-limpa").onclick = () => { salvaInv([]); desenhaTrilha(); };
}
