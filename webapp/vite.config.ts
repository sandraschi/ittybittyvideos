import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const BACKEND = "http://127.0.0.1:11054";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    port: 11055,
    host: "127.0.0.1",
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
      "/health": { target: BACKEND, changeOrigin: true },
      "/docs": { target: BACKEND, changeOrigin: true },
      "/docs/": { target: BACKEND, changeOrigin: true },
      "/openapi.json": { target: BACKEND, changeOrigin: true },
      "/redoc": { target: BACKEND, changeOrigin: true },
      "/mcp": { target: BACKEND, changeOrigin: true },
    },
  },
});
