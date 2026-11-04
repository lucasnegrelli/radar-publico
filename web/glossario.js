// Glossário clicável (termos técnicos ganham explicação em linguagem simples) e boas-vindas no primeiro acesso.
const TERMOS = {
  "emenda parlamentar": "Dinheiro do orçamento federal que um deputado ou senador indica para uma obra, serviço ou entidade. Receber emenda é normal; o Radar mostra para onde foi.",
  "emendas parlamentares": "Dinheiro do orçamento federal que deputados e senadores indicam para obras, serviços ou entidades. Receber emenda é normal; o Radar mostra para onde foi.",
  "emendas": "Dinheiro do orçamento federal indicado por deputados e senadores para obras, serviços ou entidades.",
  "dispensa de licitação": "Contratação sem concorrência, permitida em casos previstos em lei (valor baixo, emergência). É mais fácil de abusar, por isso o Radar olha com cuidado.",
  "dispensa": "Contratação direta, sem licitação, nos casos previstos em lei.",
  "inexigibilidade": "Contratação sem licitação porque só uma empresa ou pessoa poderia fornecer (ex.: artista, serviço singular).",
  "licitação": "Disputa pública em que empresas competem para vender ao governo. A que oferece melhor condição vence.",
  "pregão": "Tipo de licitação em que ganha o menor preço, feita por lances.",
  "CEIS": "Cadastro de Empresas Inidôneas e Suspensas: empresas punidas e impedidas de contratar com o governo.",
  "CNEP": "Cadastro Nacional de Empresas Punidas pela Lei Anticorrupção. Atenção: nem toda punição impede de contratar (multa não impede).",
  "CEPIM": "Cadastro de Entidades Privadas sem Fins Lucrativos Impedidas de receber verba federal.",
  "PNCP": "Portal Nacional de Contratações Públicas: onde órgãos de todo o país registram licitações e contratos.",
  "sócio-administrador": "Sócio que também administra a empresa e responde por ela.",
  "cotista": "Sócio que tem parte da empresa mas não a administra.",
  "RPPS": "Regime Próprio de Previdência dos Servidores: o fundo que paga aposentadoria de servidores de estados e municípios.",
  "FIDC": "Fundo de Investimento em Direitos Creditórios: fundo que compra dívidas e recebíveis de empresas e bancos.",
  "offshore": "Empresa aberta em país de tributação baixa ou sigilo. Ter offshore pode ser legal e declarado; o que importa é o contexto.",
  "liquidação extrajudicial": "Quando o Banco Central encerra as atividades de um banco que não consegue honrar suas dívidas.",
  "indiciamento": "Ato da polícia que aponta alguém como suspeito formal de crime. Não é acusação nem condenação.",
  "denúncia": "Acusação formal feita pelo Ministério Público à Justiça. Ainda não é condenação.",
  "réu": "Pessoa cuja denúncia foi aceita pela Justiça e que passa a responder a uma ação penal. Ainda não é condenada.",
  "cota parlamentar": "Verba mensal que o deputado ou senador usa para gastos do mandato (passagens, escritório, divulgação), com notas publicadas.",
  "empenho": "Reserva de dinheiro que o governo faz para pagar uma despesa. É o primeiro passo antes do pagamento.",
  "favorecido": "Quem recebe o dinheiro público em um pagamento.",
  "capital social": "Valor que os sócios declararam investir na empresa. Capital muito baixo com contrato muito alto chama atenção.",
  "quadro societário": "Lista de sócios e administradores de uma empresa.",
  "prisão preventiva": "Prisão antes da condenação, para proteger a investigação ou a sociedade. Não é pena.",
  "acordo de leniência": "Acordo em que uma empresa admite irregularidades, colabora e paga, em troca de redução de punições.",
  "delação premiada": "Acordo em que um investigado conta o que sabe e recebe benefício. Precisa de provas além da palavra do delator.",
  "inelegível": "Impedido de se candidatar por um período definido pela Justiça Eleitoral.",
  "prescrição": "Perda do prazo do Estado para punir. O caso acaba sem julgar se houve ou não o crime.",
  "homônimo": "Pessoa diferente com o mesmo nome. Por isso o Radar pede confirmação nas ligações feitas só por nome.",
};
const chaves = Object.keys(TERMOS).sort((a, b) => b.length - a.length);
let pop = null;
function mostra(el, txt) {
  pop ||= (() => { const d = document.createElement("div"); d.id = "gl-pop"; document.body.appendChild(d); document.addEventListener("click", (e) => { if (!e.target.closest(".gl")) d.classList.remove("on"); }); return d; })();
  pop.textContent = txt; pop.classList.add("on");
  const r = el.getBoundingClientRect(), w = Math.min(300, window.innerWidth - 20);
  pop.style.width = w + "px"; pop.style.left = Math.max(10, Math.min(window.innerWidth - w - 10, r.left)) + "px"; pop.style.top = Math.min(window.innerHeight - 140, r.bottom + 8) + "px";
}
function anota(raiz) {
  if (!raiz) return;
  const usados = new Set();
  const walker = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, { acceptNode: (n) => (n.parentElement.closest("a,button,.gl,h2,svg,textarea,input,script,style,.fechar,.dos") || !n.nodeValue.trim() ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT) });
  const alvos = []; let n; while ((n = walker.nextNode())) alvos.push(n);
  for (const no of alvos) {
    let txt = no.nodeValue, achou = null;
    for (const k of chaves) { if (usados.has(k)) continue; const i = txt.toLowerCase().indexOf(k.toLowerCase()); if (i >= 0 && !/\p{L}/u.test(txt[i - 1] || " ") && !/\p{L}/u.test(txt[i + k.length] || " ")) { achou = [k, i]; break; } }
    if (!achou) continue;
    const [k, i] = achou; usados.add(k);
    const span = document.createElement("span"); span.className = "gl"; span.textContent = txt.slice(i, i + k.length); span.dataset.t = k;
    span.onclick = (e) => { e.stopPropagation(); mostra(span, TERMOS[k]); };
    const resto = no.splitText(i); resto.nodeValue = resto.nodeValue.slice(k.length); no.parentNode.insertBefore(span, resto);
  }
  raiz.dataset.gl = String(raiz.innerHTML.length);
}
export function iniciaGlossario() {
  // só anota o painel de detalhe; o observador é desligado enquanto anota, para não reagir às próprias mudanças
  const det = document.getElementById("detalhe"); if (!det) return;
  const obs = new MutationObserver(() => { clearTimeout(det._t); det._t = setTimeout(() => { obs.disconnect(); try { anota(det); } finally { obs.observe(det, { childList: true }); } }, 150); });
  obs.observe(det, { childList: true });
}
export const todosTermos = () => Object.entries(TERMOS).sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));

export function boasVindas() {
  return;   // substituído pelo herói da tela inicial (busca + manchete + atalhos)
  if (localStorage.getItem("radar.visto")) return;
  const d = document.createElement("div"); d.id = "bv";
  d.innerHTML = `<button class="bv-x" aria-label="Fechar">×</button>
    <div class="bv-t">Para onde vai o dinheiro público?</div>
    <p>Cada ponto no mapa é um <u>ponto de atenção</u>, não uma acusação: mostra por que apareceu e o que não prova. Cor = prioridade (<i style="color:#ff2d55">alta</i>, <i style="color:#ffb300">média</i>, <i style="color:#00b8ff">baixa</i>).</p>
    <div class="bv-go"><button data-aba="cidade">🏠 Minha cidade</button><button data-aba="fichas">👤 Um político</button><button data-aba="investigar">🔎 Uma empresa</button><button data-aba="casos">📂 Casos</button></div>`;
  document.getElementById("centro").appendChild(d);
  const fecha = () => { localStorage.setItem("radar.visto", "1"); d.remove(); };
  d.querySelector(".bv-x").onclick = fecha;
  d.querySelectorAll("[data-aba]").forEach((b) => (b.onclick = () => { document.querySelector(`#abas [data-aba="${b.dataset.aba}"]`).click(); fecha(); }));
  setTimeout(() => { if (d.isConnected) d.classList.add("quieto"); }, 12000);
}
