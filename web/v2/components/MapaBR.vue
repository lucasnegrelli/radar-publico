<script setup>
import { computed } from "vue";
const props = defineProps({ geo: Object, valores: Object, selecionada: String });
const emit = defineEmits(["escolher"]);
const UF_COD = { 11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF" };
// projeção simples (equirretangular corrigida pela latitude média): suficiente para o mapa do Brasil
const X0 = -74.2, X1 = -33.6, Y0 = 5.5, Y1 = -34, K = Math.cos((-14 * Math.PI) / 180), W = 520;
const H = Math.round(((Y0 - Y1) / ((X1 - X0) * K)) * W);
const px = (lon) => ((lon - X0) / (X1 - X0)) * W, py = (lat) => ((Y0 - lat) / (Y0 - Y1)) * H;
const anel = (r) => r.map((c, i) => (i ? "L" : "M") + px(c[0]).toFixed(1) + " " + py(c[1]).toFixed(1)).join("") + "Z";
const d = (g) => (g.type === "Polygon" ? g.coordinates.map(anel).join("") : g.coordinates.map((p) => p.map(anel).join("")).join(""));
const centro = (g) => { let a = 0, b = 0, n = 0; const rec = (k) => { if (typeof k[0] === "number") { a += k[0]; b += k[1]; n++; } else k.forEach(rec); }; rec(g.coordinates); return [px(a / n), py(b / n)]; };
const max = computed(() => Math.max(1, ...Object.values(props.valores || {})));
const ufs = computed(() => (props.geo ? props.geo.features.map((f) => ({ uf: UF_COD[Number(f.properties.codarea)], d: d(f.geometry), c: centro(f.geometry) })).filter((x) => x.uf) : []));
const cor = (uf) => { const v = (props.valores || {})[uf] || 0, t = Math.sqrt(v / max.value); return v ? `color-mix(in srgb, var(--sinal) ${Math.round(12 + 78 * t)}%, var(--suave))` : "var(--suave)"; };
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" role="img" aria-label="Mapa do Brasil por estado, colorido pelo valor em alertas">
    <path v-for="u in ufs" :key="u.uf" :d="u.d" :fill="cor(u.uf)" :class="{ sel: selecionada === u.uf }" @click="emit('escolher', u.uf)"><title>{{ u.uf }}</title></path>
    <text v-for="u in ufs" :key="'t' + u.uf" :x="u.c[0]" :y="u.c[1]" text-anchor="middle">{{ u.uf }}</text>
  </svg>
</template>
