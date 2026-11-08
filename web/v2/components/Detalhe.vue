<script setup>
import { computed } from "vue";
import Coincidencia from "./Coincidencia.vue";
import { brl, brlCurto, manchete, bonito, RNOME, periodo } from "../textos.js";
const props = defineProps({ a: Object });
const emit = defineEmits(["voltar"]);
const texto = computed(() => manchete(props.a).replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(props.a.empresa, bonito(props.a.empresa)));
const regra = computed(() => (props.a.manchete && props.a.manchete.tipo) || props.a.regra);
const NAO = {
  R01: ["Que o gasto foi irregular: o serviço pode ter sido prestado de verdade.", "Que o parlamentar sabia da punição: o cadastro nem sempre é consultado."],
  R02: ["Que o contrato é ilegal: a punição pode não alcançar o órgão que contratou.", "Que houve fraude: confira a vigência e o alcance da sanção."],
  R11: ["Que o pagamento seja irregular: pode ser contrato anterior à punição.", "Que a empresa tenha agido de má-fé: a sanção pode estar sob decisão judicial."],
  R09: ["Que a emenda foi mal usada: entidade privada pode receber emenda por lei.", "Que o parlamentar tenha participação nos sinais: ele indica, não executa."],
  R10: ["Que houve favorecimento: ser sócio é legal em muitos casos.", "Que o contrato seja ilegal: confira se foi licitação e se é do mesmo município."],
  R03: ["Que a empresa seja de fachada: empresas novas podem ter experiência dos sócios.", "Que o contrato seja irregular: confira o processo de contratação."],
};
const naoProva = computed(() => NAO[regra.value] || ["Que algo seja ilegal. Este é um ponto de atenção feito de dados públicos, não uma conclusão.", "Pode haver explicação legal. Confira a fonte antes de concluir."]);
const linhas = computed(() => (props.a.tabela?.linhas || []).slice(0, 10).map((l) => l.map((c) => c.t)));
const onde = computed(() => [props.a.local ? `${props.a.local.cidade}/${props.a.local.uf}` : "", periodo(props.a.inicio, props.a.fim).replace(/^(em|entre) /, "")].filter(Boolean).join(" · "));
const zap = computed(() => "https://wa.me/?text=" + encodeURIComponent(`${texto.value.slice(0, 180)} Veja no Radar Público: ${location.origin}/#${encodeURIComponent(props.a.id)}`));
</script>

<template>
  <section class="det">
    <button class="volta" @click="emit('voltar')">← Hoje</button>
    <div class="marca-d"><span class="tipo">{{ RNOME[a.regra] || a.regra }}</span><span class="nivel" :class="a.gravidade">{{ a.gravidade === "alta" ? "CONFERIR JÁ" : "VALE OLHAR" }}</span></div>
    <h1 class="tit">{{ bonito(a.empresa) }}</h1>
    <div class="num-g">R$ {{ brlCurto(a.total).replace("R$ ", "") }}</div>
    <div class="rot">{{ onde }}</div>

    <div class="bloco-d"><div class="rot">A coincidência</div><Coincidencia :a="a" alto /></div>

    <div class="bloco-d"><div class="rot">O que aconteceu</div><p class="corpo">{{ texto }}</p></div>

    <div class="bloco-d" v-if="linhas.length"><div class="rot">Registros ({{ linhas.length }} de {{ a.n }})</div>
      <table class="tb"><tbody><tr v-for="(l, i) in linhas" :key="i"><td class="mono">{{ l[0] }}</td><td>{{ l[1] }}</td><td class="mono d">{{ l[3] }}</td></tr></tbody></table>
    </div>

    <div class="bloco-d nao"><div class="rot">O que isto não prova</div><ul><li v-for="t in naoProva" :key="t">{{ t }}</li></ul></div>

    <div class="acoes">
      <a class="botao" :href="`/#${encodeURIComponent(a.id)}`">Dossiê completo e fontes →</a>
      <a class="botao vazio" :href="zap" target="_blank" rel="noopener">Compartilhar no WhatsApp</a>
    </div>
  </section>
</template>
