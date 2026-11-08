<script setup>
import { ref, computed, onMounted } from "vue";
import Anomalia from "./components/Anomalia.vue";
import MapaBR from "./components/MapaBR.vue";
import { brlCurto, pontuar } from "./textos.js";

const alertas = ref([]), geo = ref(null), esc_ = ref(null), meta = ref({}), casos = ref(null);
const busca = ref(""), uf = ref(""), nivel = ref("alta"), mostrar = ref(6), tema = ref(document.documentElement.dataset.tema);

onMounted(async () => {
  const j = (u) => fetch(u).then((r) => r.json()).catch(() => null);
  const [a, r, g, e, c] = await Promise.all([j("/data/alertas.json"), j("/data/risco.json"), j("/data/uf.geojson"), j("/data/escala.json"), j("/data/casos_noticias.json")]);
  const L = [...((a && a.alertas) || []), ...((r && r.alertas) || [])].map((x) => ((x.score = pontuar(x)), x));
  const ord = [...L].sort((x, y) => y.score - x.score), nA = Math.max(20, Math.round(ord.length * 0.03)), nM = Math.round(ord.length * 0.18);
  ord.forEach((x, i) => { x.gravidade_regra = x.gravidade; x.gravidade = i < nA ? "alta" : i < nA + nM ? "media" : "baixa"; });
  alertas.value = ord; geo.value = g; esc_.value = e; meta.value = { gerado: a && a.gerado }; casos.value = c;
});

const pesam = computed(() => alertas.value.filter((a) => a.gravidade !== "baixa" && !(a.manchete && a.manchete.ref)));
const total = computed(() => pesam.value.reduce((t, a) => t + (a.total || 0), 0));
const partes = computed(() => { const t = brlCurto(total.value).replace("R$ ", "").split(" "); return { n: t[0] || "–", u: t[1] === "bi" ? "bilhões" : t[1] === "mi" ? "milhões" : t[1] || "" }; });
const pct = computed(() => (esc_.value && esc_.value.pncp_bi ? (100 * total.value / 1e9 / esc_.value.pncp_bi).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) : null));
const nMax = computed(() => alertas.value.filter((a) => a.gravidade === "alta").length), nRel = computed(() => alertas.value.filter((a) => a.gravidade === "media").length);
const nNovos = computed(() => pesam.value.filter((a) => a.novo).length), nComb = computed(() => pesam.value.filter((a) => a.correlacao).length);
const porUF = computed(() => { const o = {}; pesam.value.forEach((a) => { const u = (a.local && a.local.uf) || a.orgao_uf; if (u) o[u] = (o[u] || 0) + (a.total || 0); }); return o; });
const ranking = computed(() => Object.entries(porUF.value).sort((x, y) => y[1] - x[1]).slice(0, 8));
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const lista = computed(() => {
  const q = norm(busca.value).trim();
  let L = q ? alertas.value.filter((a) => norm([a.empresa, a.cnpj, a.local && a.local.cidade, a.local && a.local.uf].join(" ")).includes(q)) : pesam.value.filter((a) => nivel.value === "todos" || (nivel.value === "alta" ? a.gravidade === "alta" : a.gravidade === "media"));
  if (uf.value && !q) L = L.filter((a) => ((a.local && a.local.uf) || a.orgao_uf) === uf.value);
  return L;
});
const trocaTema = () => { tema.value = tema.value === "claro" ? "escuro" : "claro"; document.documentElement.dataset.tema = tema.value; localStorage.setItem("radar.tema", tema.value); };
const zap = computed(() => "https://wa.me/?text=" + encodeURIComponent(`Radar Público: ${brlCurto(total.value)} em ${pesam.value.length} sinais que merecem uma segunda olhada no gasto público. ${location.origin}/v2/`));
const maxUF = computed(() => (ranking.value[0] ? ranking.value[0][1] : 1));
const escolhe = (u) => { uf.value = uf.value === u ? "" : u; mostrar.value = 6; };
</script>

<template>
  <header class="topo">
    <div class="wrap">
      <a class="marca" href="/v2/">
        <svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="13" /><circle cx="16" cy="16" r="8" /><circle class="nuc" cx="16" cy="16" r="3" /><path d="M16 16 L26 8" /></svg>
        <b>Radar Público</b><small>para onde vai o dinheiro público</small>
      </a>
      <nav>
        <a class="on" href="#anomalias">Anomalias</a><a href="#mapa">Mapa</a><a href="#como">Como funciona</a><a href="/">Painel completo</a>
      </nav>
      <div class="ac">
        <a class="ic" :href="zap" target="_blank" rel="noopener" title="Compartilhar no WhatsApp"><svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 10-16.6 4.7L3 21l4.4-1.4A9 9 0 0021 12z" /></svg></a>
        <button class="ic" @click="trocaTema" :title="tema === 'claro' ? 'Tema escuro' : 'Tema claro'"><svg viewBox="0 0 24 24"><template v-if="tema === 'claro'"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" /></template><template v-else><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></template></svg></button>
      </div>
    </div>
  </header>

  <main class="wrap">
    <section class="heroi">
      <div class="sel"><i></i> Dados oficiais · atualizado em {{ meta.gerado ? new Date(meta.gerado + 'T12:00').toLocaleDateString('pt-BR') : '…' }}</div>
      <div class="gigante display"><span>{{ partes.n }}</span><small>{{ partes.u }} de reais</small></div>
      <h1>em {{ pesam.length.toLocaleString("pt-BR") }} sinais que merecem uma segunda olhada no dinheiro público.</h1>
      <p class="sub">Cruzamos contratos, emendas, sanções, empresas e doações. {{ pct ? `É ${pct}% das compras públicas que analisamos. ` : "" }}<b>Alerta não é acusação</b>: é um motivo para conferir, sempre com a fonte à mostra.</p>

      <div class="faixa">
        <div class="s"><b class="num">{{ nMax }}</b><span>prioridade máxima</span></div>
        <div class="a"><b class="num">{{ nRel }}</b><span>relevantes</span></div>
        <div><b class="num">{{ nNovos }}</b><span>novos nas últimas semanas</span></div>
        <div><b class="num">{{ nComb }}</b><span>com sinais combinados</span></div>
      </div>

      <label class="busca"><svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6" /><path d="M15 15l6 6" /></svg><input v-model="busca" placeholder="Digite sua cidade, um estado, uma empresa ou um CNPJ" /></label>
      <div class="atalhos"><button class="pill" @click="busca = 'São Paulo'">São Paulo</button><button class="pill" @click="busca = 'Rio de Janeiro'">Rio de Janeiro</button><button class="pill" @click="busca = 'Belo Horizonte'">Belo Horizonte</button><button class="pill" @click="busca = 'Recife'">Recife</button><a class="pill" href="/" style="display:inline-flex;align-items:center;text-decoration:none">Pessoas e casos →</a></div>
    </section>

    <section id="anomalias" class="sec">
      <h2>{{ busca ? "Resultados" : "O que mais pesa hoje" }}</h2>
      <p v-if="!busca" class="lead">Poucos sinais, bem explicados.</p>
      <p v-if="!busca" class="nota">Ordenamos tudo por peso (valor, tipo e combinação com outros sinais). Só cerca de 3% viram prioridade máxima; o resto é contexto.</p>
      <div v-if="!busca" class="atalhos" style="margin-top:14px">
        <button class="pill" :class="{ on: nivel === 'alta' }" @click="nivel = 'alta'; mostrar = 6">Prioridade máxima ({{ nMax }})</button>
        <button class="pill" :class="{ on: nivel === 'media' }" @click="nivel = 'media'; mostrar = 6">Relevantes ({{ nRel }})</button>
        <button v-if="uf" class="pill on" @click="uf = ''">{{ uf }} ×</button>
      </div>
      <div class="lista">
        <Anomalia v-for="a in lista.slice(0, mostrar)" :key="a.id" :a="a" />
        <div v-if="!lista.length" class="vazio">Nada encontrado. Tente o nome da cidade ou da empresa.</div>
      </div>
      <div v-if="lista.length > mostrar" class="mais"><button class="btn vazio" @click="mostrar += 6">Ver mais ({{ lista.length - mostrar }})</button></div>
    </section>

    <section id="mapa" class="sec">
      <h2>Onde está</h2>
      <p class="lead">Toque num estado para ver só os sinais dele.</p>
      <div class="mapa">
        <div><MapaBR :geo="geo" :valores="porUF" :selecionada="uf" @escolher="escolhe" /><div class="leg"><span>menos</span><i></i><span>mais valor em atenção</span></div></div>
        <div class="ufs">
          <button v-for="[u, v] in ranking" :key="u" :class="{ on: uf === u }" @click="escolhe(u)">
            <span class="sg">{{ u }}</span><span class="bar"><i :style="{ width: Math.max(4, Math.round(100 * v / maxUF)) + '%' }"></i></span><span class="num vl">{{ brlCurto(v).replace('R$ ', '') }}</span>
          </button>
        </div>
      </div>
    </section>

    <section id="como" class="sec">
      <h2>Como funciona</h2>
      <div class="passos">
        <div><b class="display">1 · Juntamos</b><p>Contratos, emendas, sanções, empresas, doações e salários, todos de bases oficiais e abertas.</p></div>
        <div><b class="display">2 · Cruzamos</b><p>Procuramos o que foge do normal: empresa punida que recebe, doador que vira fornecedor, contrato gigante para empresa pequena.</p></div>
        <div><b class="display">3 · Mostramos a fonte</b><p>Cada sinal traz o porquê, o que descartamos e o que ele não prova. Você confere e decide.</p></div>
      </div>
    </section>

    <footer class="rodape">
      Fontes: PNCP, Portal da Transparência, Câmara, Senado, TSE, Receita, PGFN, Banco Central e outras bases abertas. · <a href="/">Abrir o painel completo</a> · Esta é a nova cara do Radar (versão em teste).
    </footer>
  </main>
</template>
