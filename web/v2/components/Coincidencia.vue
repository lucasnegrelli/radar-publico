<script setup>
// O gesto de assinatura do Radar: dois períodos de tempo que se sobrepõem.
// Faixa hachurada = o que restringia (sanção, mandato, empresa recém-aberta); traços = pagamentos/contratos; a parte que cai dentro da faixa fica preta.
import { computed, useId } from "vue";
const props = defineProps({ a: Object, alto: { type: Boolean, default: false } });
const uid = useId().replace(/[^a-z0-9]/gi, "");

const dia = (s) => { if (!s) return null; const t = /^\d{4}-\d{2}$/.test(s) ? s + "-15" : s; const d = new Date(t + "T12:00:00"); return isNaN(d) ? null : d.getTime(); };
const brl = (t) => { const n = parseFloat(String(t || "").replace(/[^\d,]/g, "").replace(",", ".")); return isNaN(n) ? 0 : n; };
const MS = 86400000;

const modelo = computed(() => {
  const a = props.a, m = a.manchete || {}, hoje = Date.now();
  const pays = (a.tabela?.linhas || []).map((l) => ({ t: dia(l[0]?.t), v: brl(l[3]?.t) })).filter((p) => p.t);
  let banda = null, rotuloBanda = "";
  if (a.sancao && a.sancao.inicio) { banda = [dia(a.sancao.inicio), a.sancao.fim ? dia(a.sancao.fim) : null]; rotuloBanda = "SANÇÃO"; }
  else if (m.tipo === "R10" && m.posse) { banda = [dia(m.posse), null]; rotuloBanda = "MANDATO"; }
  else if (m.tipo === "R03" && m.abertura) { banda = [dia(m.abertura), null]; rotuloBanda = "EMPRESA ABERTA"; }
  const p0 = pays.length ? Math.min(...pays.map((p) => p.t)) : dia(a.inicio), p1 = pays.length ? Math.max(...pays.map((p) => p.t)) : dia(a.fim);
  if (!p0) return null;
  let ini = Math.min(p0, banda ? banda[0] : p0) - 60 * MS, fim = Math.max(p1, banda && banda[0] > p1 ? banda[0] : p1) + 60 * MS;
  const aberta = banda && (banda[1] === null || banda[1] > fim), bandaFim = banda ? (aberta ? fim : Math.min(banda[1], fim)) : null;
  if (banda && banda[0] > ini + (fim - ini)) banda = null;
  const dentro = banda ? pays.filter((p) => p.t >= banda[0] && (banda[1] === null || p.t <= banda[1])) : [];
  const W = 600, x = (t) => ((t - ini) / Math.max(fim - ini, MS)) * W;
  const anos = []; for (let y = new Date(ini).getFullYear() + 1; y <= new Date(fim).getFullYear(); y++) anos.push({ y, x: x(new Date(y, 0, 1).getTime()) });
  return {
    W, pays: pays.map((p) => ({ x: x(p.t), dentro: banda ? p.t >= banda[0] && (banda[1] === null || p.t <= banda[1]) : false, v: p.v })),
    banda: banda ? { x0: Math.max(0, x(banda[0])), x1: Math.min(W, x(bandaFim)), aberta, rotulo: rotuloBanda, fimTxt: banda[1] ? new Date(banda[1]).getFullYear() : null } : null,
    anos, nDentro: dentro.length, nTotal: pays.length, vDentro: dentro.reduce((t, p) => t + p.v, 0),
    gap: m.tipo === "R03" && m.dias != null ? m.dias : null,
  };
});
const H = computed(() => (props.alto ? 92 : 64));
</script>

<template>
  <figure v-if="modelo" class="coin" :class="{ alto }">
    <svg :viewBox="`0 0 ${modelo.W} ${H}`" preserveAspectRatio="none" role="img" :aria-label="modelo.banda ? 'Linha do tempo: pagamentos dentro do período de ' + modelo.banda.rotulo.toLowerCase() : 'Linha do tempo dos pagamentos'">
      <defs>
        <pattern :id="'h' + uid" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="currentColor" stroke-width="1" opacity=".38" /></pattern>
      </defs>
      <g v-if="modelo.banda">
        <rect :x="modelo.banda.x0" :y="alto ? 22 : 14" :width="Math.max(1, modelo.banda.x1 - modelo.banda.x0)" :height="alto ? 40 : 28" :fill="`url(#h${uid})`" />
        <rect :x="modelo.banda.x0" :y="alto ? 22 : 14" :width="Math.max(1, modelo.banda.x1 - modelo.banda.x0)" :height="alto ? 40 : 28" fill="none" stroke="currentColor" stroke-width="1" vector-effect="non-scaling-stroke" />
      </g>
      <g>
        <line v-for="(p, i) in modelo.pays" :key="i" :x1="p.x" :x2="p.x" :y1="alto ? 12 : 8" :y2="alto ? 72 : 50" :stroke="p.dentro ? '#000' : '#8a8a8a'" :stroke-width="p.dentro ? 2.4 : 1.6" vector-effect="non-scaling-stroke" />
      </g>
      <line x1="0" :x2="modelo.W" :y1="H - 14" :y2="H - 14" stroke="currentColor" stroke-width="1" vector-effect="non-scaling-stroke" />
      <g v-for="an in modelo.anos" :key="an.y"><line :x1="an.x" :x2="an.x" :y1="H - 14" :y2="H - 9" stroke="currentColor" stroke-width="1" vector-effect="non-scaling-stroke" /></g>
    </svg>
    <div class="eixo"><span v-for="an in modelo.anos" :key="an.y" :style="{ left: (an.x / modelo.W) * 100 + '%' }">{{ an.y }}</span></div>
    <figcaption>
      <template v-if="modelo.banda && modelo.nTotal">
        <b>{{ modelo.nDentro }} de {{ modelo.nTotal }}</b> {{ modelo.nTotal === 1 ? "pagamento caiu" : "pagamentos caíram" }} dentro do período de {{ modelo.banda.rotulo.toLowerCase() }}<template v-if="modelo.banda.aberta"> (sem data final)</template><template v-else-if="modelo.banda.fimTxt"> (até {{ modelo.banda.fimTxt }})</template>.
      </template>
      <template v-else-if="modelo.gap !== null">Contrato assinado <b>{{ modelo.gap }} {{ modelo.gap === 1 ? "dia" : "dias" }}</b> depois da abertura da empresa.</template>
      <template v-else>Período dos pagamentos, mês a mês.</template>
    </figcaption>
  </figure>
</template>

<style scoped>
.coin{margin:0;position:relative;color:var(--ink)}
.coin svg{display:block;width:100%;height:64px}
.coin.alto svg{height:92px}
.eixo{position:relative;height:14px;margin-top:-13px;pointer-events:none}
.eixo span{position:absolute;transform:translateX(-50%);font:500 9.5px var(--mono);color:var(--mid);top:0}
figcaption{margin-top:8px;font-size:13px;line-height:1.35;color:var(--mid)}
figcaption b{color:var(--ink);font-weight:600}
</style>
