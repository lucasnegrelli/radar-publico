<script setup>
import { computed } from "vue";
import { brlCurto, curta, linhaCard, bonito, RNOME, periodo } from "../textos.js";
const props = defineProps({ a: Object });
const cores = { alta: "var(--sinal)", media: "var(--ambar)", baixa: "var(--mudo)" };
const rot = { alta: "Prioridade máxima", media: "Relevante", baixa: "Contexto" };
const frase = computed(() => curta(props.a).replace(props.a.empresa, bonito(props.a.empresa)));
const onde = computed(() => [props.a.local ? `${props.a.local.cidade}/${props.a.local.uf}` : "", periodo(props.a.inicio, props.a.fim).replace(/^(em|entre) /, "")].filter(Boolean).join(" · "));
const valor = computed(() => { const t = brlCurto(props.a.total); const m = t.replace("R$ ", "").split(" "); return { n: m[0], u: m[1] || "" }; });
</script>

<template>
  <article class="card" :style="{ '--c': cores[a.gravidade] }">
    <div class="tipo">
      <span>{{ rot[a.gravidade] }} · {{ RNOME[a.regra] || a.regra }}</span>
      <span v-if="a.novo" class="tag nv">novo</span>
      <span v-if="a.correlacao" class="tag cb">sinais combinados</span>
    </div>
    <p class="frase">{{ frase }}</p>
    <p class="por"><b>Por que importa:</b> {{ linhaCard(a) }}.</p>
    <div class="rod">
      <div>
        <div class="num v">{{ valor.n }} <small style="display:inline;font-size:.4em;font-family:Inter Variable,sans-serif;font-weight:500">{{ valor.u }}</small></div>
        <small>{{ onde }}</small>
      </div>
      <a class="btn" :href="`/#${encodeURIComponent(a.id)}`">Ver a ficha completa →</a>
    </div>
  </article>
</template>
