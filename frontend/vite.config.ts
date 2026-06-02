import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const apiProxyTarget = process.env.BEST_TRADING_AGENT_API_PROXY ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": apiProxyTarget,
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/testSetup.ts",
  },
});
