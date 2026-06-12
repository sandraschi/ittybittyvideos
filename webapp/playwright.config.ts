import { defineConfig } from "@playwright/test";

/** Dev UI with API proxy (default). Override with ITTYBITTY_E2E_BASE_URL for built-in dist on :11054. */
const baseURL = process.env.ITTYBITTY_E2E_BASE_URL ?? "http://127.0.0.1:11055";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  timeout: 30_000,
});
