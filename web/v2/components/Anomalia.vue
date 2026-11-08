<script setup>
import { computed } from "vue";
import { brlCurto, curta, linhaCard, bonito, RNOME, periodo } from "../textos.js";
const props = defineProps({ a: Object });
const rot = { alta: "Conferir já", media: "Vale olhar" };
const frase = computed(() => curta(props.a).replace(props.a.empresa, bonito(props.a.empresa)));
const onde = computed(() => [props.a.local ? `${props.a.local.cidade}/${props.a.local.uf}` : "", periodo(props.a.inicio, props.a.fim).replace(/^(em|entre) /, "")].filter(Boolean).join(" · "));
const valor = computed(() => { const m = brlCurto(props.a.total).replace("R$ ", "").split(" "); return { n: m[0], u: m[1] || "" }; });
</script>

<template>
  <article class="item">
    <span class="sel" :class="a.gravidade">{{ rot[a.gravidade] }}</span><span class="tp">{{ RNOME[a.regra] || a.regra }}</span>
    <p class="fr">{{ frase }}</p>
    <p class="por"><b>Por que importa:</b> {{ linhaCard(a) }}.</p>
    <div class="rod">
      <div><div class="v">R$ {{ valor.n }}<small>{{ valor.u }}</small></div><span class="onde">{{ onde }}</span></div>
      <a class="ir" :href="`/#${encodeURIComponent(a.id)}`">Ver a ficha →</a>
    </div>
  </article>
</template>
