import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server on :5173. The `/api` proxy forwards to the FastAPI backend so the
// browser talks to the same origin in dev (no CORS needed). Override the
// backend target with VITE_PROXY_TARGET if it runs elsewhere.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward API calls to the FastAPI backend (same-origin in the browser).
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
