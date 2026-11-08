import "@fontsource-variable/inter";
import "@fontsource/barlow-condensed/500.css";
import "@fontsource/barlow-condensed/700.css";
import "./style.css";
import { createApp } from "vue";
import App from "./App.vue";

const salvo = localStorage.getItem("radar.tema");
const escuro = salvo ? salvo === "escuro" : window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
document.documentElement.dataset.tema = escuro ? "escuro" : "claro";
createApp(App).mount("#app");
