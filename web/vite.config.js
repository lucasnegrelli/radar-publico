import { defineConfig } from "vite";
import cesium from "vite-plugin-cesium";
export default defineConfig({
  plugins: [cesium()],
  build: { target: "es2022", chunkSizeWarningLimit: 6000 },
  esbuild: { target: "es2022" },
});
