<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import Item from "./components/Item.vue";
import Detalhe from "./components/Detalhe.vue";
import { brlCurto, pontuar } from "./textos.js";

const alertas = ref([]), gerado = ref(""), busca = ref(""), mostrar = ref(4), aberto = ref(null), como = ref(false);
const lerHash = () => { const h = decodeURIComponent(location.hash.replace(/^#\/?/, "")); aberto.value = h || null; window.scrollTo(0, 0); };

onMounted(async () => {
  const j = (u) => fetch(u).then((r) => r.json()).catch(() => null);
  const [a, r] = await Promise.all([j("/data/alertas.json"), j("/data/risco.json")]);
  const L = [...((a && a.alertas) || []), ...((r && r.alertas) || [])].map((x) => ((x.score = pontuar(x)), x));
  const ord = [...L].sort((x, y) => y.score - x.score), nA = Math.max(20, Math.round(ord.length * 0.03)), nM = Math.round(ord.length * 0.18);
  ord.forEach((x, i) => { x.gravidade = i < nA ? "alta" : i < nA + nM ? "media" : "baixa"; });
  alertas.value = ord; gerado.value = (a && a.gerado) || "";
  lerHash(); window.addEventListener("hashchange", lerHash);
});
onBeforeUnmount(() => window.removeEventListener("hashchange", lerHash));

const pesam = computed(() => alertas.value.filter((a) => a.gravidade !== "baixa" && !(a.manchete && a.manchete.ref)));
const total = computed(() => pesam.value.reduce((t, a) => t + (a.total || 0), 0));
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const lista = computed(() => {
  const q = norm(busca.value).trim();
  if (q) return alertas.value.filter((a) => norm([a.empresa, a.cnpj, a.local && a.local.cidade, a.local && a.local.uf].join(" ")).includes(q));
  // intercala os tipos (um de cada, pelo peso) para a primeira tela mostrar a variedade do que o Radar enxerga
  const grupos = {}; pesam.value.forEach((a) => (grupos[a.regra] ||= []).push(a));
  const fila = Object.values(grupos).sort((x, y) => y[0].score - x[0].score), out = [];
  for (let i = 0; out.length < pesam.value.length; i++) { let algum = false; fila.forEach((g) => { if (g[i]) { out.push(g[i]); algum = true; } }); if (!algum) break; }
  return out;
});
const atual = computed(() => alertas.value.find((a) => a.id === aberto.value));
const hoje = new Date().toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" }).replace(/\//g, ".");
const abrir = (id) => { location.hash = "/" + encodeURIComponent(id); };
const voltar = () => { history.pushState("", document.title, location.pathname + location.search); aberto.value = null; window.scrollTo(0, 0); };
const valorTxt = computed(() => brlCurto(total.value));
</script>

<template>
  <div class="app">
    <header class="cab">
      <a class="logo" href="/v2/" @click.prevent="voltar"><i></i>RADAR PÚBLICO</a>
      <time>{{ hoje }}</time>
    </header>

    <template v-if="!atual">
      <section class="abre">
        <div class="rot">Hoje</div>
        <h1><span class="n">{{ pesam.length.toLocaleString("pt-BR") }}</span> coincidências para conferir.</h1>
        <p class="mono vl">{{ valorTxt }} de dinheiro público envolvido</p>
        <p class="sub">Pagamentos e contratos que caíram onde, ou quando, não deviam. Alerta não é acusação: cada um mostra a fonte e o que não prova.</p>
        <button class="txt" @click="como = !como">{{ como ? "Fechar" : "Como lemos isto" }}</button>
        <div v-if="como" class="como"><p>Cruzamos contratos, emendas, sanções, empresas e doações de bases oficiais. Ordenamos tudo por peso. Só cerca de 3% viram <b>conferir já</b> e 18% <b>vale olhar</b>; o resto é contexto e não aparece como alerta.</p></div>
      </section>

      <label class="busca"><input v-model="busca" placeholder="Sua cidade, uma empresa ou um CNPJ" inputmode="search" /><span>→</span></label>

      <section class="lista">
        <div class="sec"><span class="rot">{{ busca ? "Resultados" : "Conferir primeiro" }}</span><span class="rot">{{ lista.length.toLocaleString("pt-BR") }}</span></div>
        <Item v-for="(a, i) in lista.slice(0, mostrar)" :key="a.id" :a="a" :n="i + 1" @abrir="abrir" />
        <div v-if="!lista.length" class="vazio">Nada encontrado.</div>
        <button v-if="lista.length > mostrar" class="botao vazio cheio" @click="mostrar += 6">Ver mais {{ Math.min(6, lista.length - mostrar) }}</button>
      </section>

      <footer class="rodape">Fontes: PNCP, Portal da Transparência, Câmara, Senado, TSE, Receita, PGFN, Banco Central. Atualizado em {{ gerado }}. <a href="/">Painel completo</a></footer>
    </template>

    <Detalhe v-else :a="atual" @voltar="voltar" />

    <nav class="abas"><a class="on" href="/v2/" @click.prevent="voltar">Hoje</a><a href="/">Cidade</a><a href="/">Pessoas</a><a href="/">Dinheiro</a><a href="/">Casos</a></nav>
  </div>
</template>
