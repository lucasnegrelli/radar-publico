<script setup>
import { computed } from "vue";
import Coincidencia from "./Coincidencia.vue";
import { brlCurto, curta, bonito, RNOME, periodo } from "../textos.js";
const props = defineProps({ a: Object, n: Number });
const emit = defineEmits(["abrir"]);
const frase = computed(() => curta(props.a).replace(props.a.empresa, bonito(props.a.empresa)));
const onde = computed(() => [props.a.local ? `${props.a.local.cidade}/${props.a.local.uf}` : "", periodo(props.a.inicio, props.a.fim).replace(/^(em|entre) /, "")].filter(Boolean).join(" · "));
const valor = computed(() => brlCurto(props.a.total).replace("R$ ", ""));
const nivel = computed(() => (props.a.gravidade === "alta" ? "CONFERIR JÁ" : "VALE OLHAR"));
</script>

<template>
  <article class="item" @click="emit('abrir', a.id)" tabindex="0" @keydown.enter="emit('abrir', a.id)">
    <header>
      <span class="idx">{{ String(n).padStart(2, "0") }}</span>
      <span class="tipo">{{ RNOME[a.regra] || a.regra }}</span>
      <span class="nivel" :class="a.gravidade">{{ nivel }}</span>
    </header>
    <Coincidencia :a="a" />
    <p class="fr">{{ frase }}</p>
    <footer>
      <span class="v">R$ {{ valor }}</span>
      <span class="onde">{{ onde }}</span>
      <span class="abrir">Abrir →</span>
    </footer>
  </article>
</template>
