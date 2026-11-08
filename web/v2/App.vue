<script setup>
import { ref, computed, onMounted } from "vue";
import Anomalia from "./components/Anomalia.vue";
import MapaBR from "./components/MapaBR.vue";
import { brlCurto, pontuar } from "./textos.js";

const dir = ref(new URLSearchParams(location.search).get("d") || "cedula");
const alertas = ref([]), geo = ref(null), gerado = ref(""), busca = ref(""), uf = ref(""), mostrar = ref(3);

onMounted(async () => {
  const j = (u) => fetch(u).then((r) => r.json()).catch(() => null);
  const [a, r, g] = await Promise.all([j("/data/alertas.json"), j("/data/risco.json"), j("/data/uf.geojson")]);
  const L = [...((a && a.alertas) || []), ...((r && r.alertas) || [])].map((x) => ((x.score = pontuar(x)), x));
  const ord = [...L].sort((x, y) => y.score - x.score), nA = Math.max(20, Math.round(ord.length * 0.03)), nM = Math.round(ord.length * 0.18);
  ord.forEach((x, i) => { x.gravidade = i < nA ? "alta" : i < nA + nM ? "media" : "baixa"; });
  alertas.value = ord; geo.value = g; gerado.value = (a && a.gerado) || "";
});
const pesam = computed(() => alertas.value.filter((a) => a.gravidade !== "baixa" && !(a.manchete && a.manchete.ref)));
const total = computed(() => pesam.value.reduce((t, a) => t + (a.total || 0), 0));
const valorTxt = computed(() => brlCurto(total.value));
const porUF = computed(() => { const o = {}; pesam.value.forEach((a) => { const u = (a.local && a.local.uf) || a.orgao_uf; if (u) o[u] = (o[u] || 0) + (a.total || 0); }); return o; });
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const lista = computed(() => {
  const q = norm(busca.value).trim();
  let L = q ? alertas.value.filter((a) => norm([a.empresa, a.cnpj, a.local && a.local.cidade, a.local && a.local.uf].join(" ")).includes(q)) : pesam.value;
  if (uf.value && !q) L = L.filter((a) => ((a.local && a.local.uf) || a.orgao_uf) === uf.value);
  return L;
});
const hoje = computed(() => new Date().toLocaleDateString("pt-BR", { day: "2-digit", month: "short" }).replace(".", ""));
const escolhe = (u) => { uf.value = uf.value === u ? "" : u; mostrar.value = 3; };
const ufs = computed(() => Object.entries(porUF.value).sort((a, b) => b[1] - a[1]).slice(0, 10).map((x) => x[0]));
</script>

<template>
  <div class="app" :data-dir="dir">
    <header class="cab">
      <a class="logo" href="/v2/" @click.prevent>
        <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="16" cy="16" r="13" /><circle cx="16" cy="16" r="7.5" /><circle cx="16" cy="16" r="2.4" fill="var(--signal)" stroke="none" /><path d="M16 16 L25 8" stroke="var(--signal)" /></svg>
        Radar Público
      </a>
      <time>{{ hoje }}</time>
    </header>

    <section class="abre">
      <div class="rot">Hoje no dinheiro público</div>
      <h1><span class="valor">{{ valorTxt }}</span> em {{ pesam.length.toLocaleString("pt-BR") }} sinais que merecem conferência.</h1>
      <p class="sub">Cruzamos contratos, emendas, sanções e empresas com bases oficiais. <b>Alerta não é acusação</b>: é um motivo para conferir, sempre com a fonte.</p>
    </section>

    <label class="busca"><svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6" /><path d="M15 15l6 6" /></svg><input v-model="busca" placeholder="Sua cidade, uma empresa ou um CNPJ" inputmode="search" /></label>
    <div class="chips"><button v-for="u in ufs" :key="u" class="chip" :class="{ on: uf === u }" @click="escolhe(u)">{{ u }}</button></div>

    <section class="bloco">
      <h2>{{ busca ? "Resultados" : uf ? "Em " + uf : "Conferir primeiro" }}</h2>
      <div class="fila">
        <Anomalia v-for="a in lista.slice(0, mostrar)" :key="a.id" :a="a" />
        <div v-if="!lista.length" class="vazio">Nada encontrado. Tente o nome da cidade ou da empresa.</div>
      </div>
      <button v-if="lista.length > mostrar" class="mais" @click="mostrar += 5">Ver mais ({{ lista.length - mostrar }})</button>
    </section>

    <section class="bloco">
      <h2>Onde está</h2>
      <div class="mapa"><MapaBR :geo="geo" :valores="porUF" :selecionada="uf" @escolher="escolhe" /></div>
      <div class="leg"><span>menos</span><span>mais valor em atenção</span></div>
    </section>

    <section class="bloco">
      <h2>Como funciona</h2>
      <div class="como">
        <div><b>Juntamos</b><p>Contratos, emendas, sanções, empresas e doações de bases oficiais e abertas.</p></div>
        <div><b>Cruzamos</b><p>Procuramos o que foge do normal e ordenamos por peso: só uma parte pequena vira prioridade.</p></div>
        <div><b>Mostramos a fonte</b><p>Cada sinal explica o porquê e o que ele não prova. Você confere e decide.</p></div>
      </div>
    </section>

    <footer class="rodape">Fontes: PNCP, Portal da Transparência, Câmara, Senado, TSE, Receita, PGFN e Banco Central. Atualizado em {{ gerado }}. <a href="/">Painel completo</a></footer>

    <nav class="abas">
      <a class="on" href="/v2/"><svg viewBox="0 0 24 24"><path d="M12 3l9.5 17h-19L12 3z" /><path d="M12 10v5M12 18v.5" /></svg>Hoje</a>
      <a href="/"><svg viewBox="0 0 24 24"><path d="M3 21V10l9-6 9 6v11M9 21v-6h6v6" /></svg>Cidade</a>
      <a href="/"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" /></svg>Pessoas</a>
      <a href="/"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 6.5v11M15 9.6c0-1.3-1.3-2-3-2s-3 .7-3 2 1.3 1.8 3 2.4 3 1.1 3 2.4-1.3 2-3 2-3-.7-3-2" /></svg>Dinheiro</a>
      <a href="/"><svg viewBox="0 0 24 24"><path d="M4 4h12l4 4v12H4z" /><path d="M8 12h8M8 16h5" /></svg>Casos</a>
    </nav>
  </div>
</template>
