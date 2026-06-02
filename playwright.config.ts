import { randomUUID } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { defineConfig, devices } from "@playwright/test";

const e2eDatabaseUrl = `sqlite+pysqlite:///${join(
  tmpdir(),
  `best-trading-agent-e2e-${randomUUID()}.db`,
)}`;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html", { open: "never" }], ["list"]],
  use: {
    baseURL: "http://127.0.0.1:5174",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: [
    {
      command:
        "uv run uvicorn best_trading_agent.api.main:create_app --factory --host 127.0.0.1 --port 8765",
      env: {
        BEST_TRADING_AGENT_DATA_MODE: "fixture",
        BEST_TRADING_AGENT_DATABASE_URL: e2eDatabaseUrl,
      },
      reuseExistingServer: false,
      timeout: 120_000,
      url: "http://127.0.0.1:8765/api/runs",
    },
    {
      command: "npm --prefix frontend run dev -- --host 127.0.0.1 --port 5174",
      env: {
        BEST_TRADING_AGENT_API_PROXY: "http://127.0.0.1:8765",
      },
      reuseExistingServer: false,
      timeout: 120_000,
      url: "http://127.0.0.1:5174",
    },
  ],
});
