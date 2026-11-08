import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "node:path";
export default defineConfig({
  plugins: [vue()],
  build: { target: "es2022", rollupOptions: { input: { main: resolve(__dirname, "index.html"), v2: resolve(__dirname, "v2/index.html") } } },
  esbuild: { target: "es2022" },
});
