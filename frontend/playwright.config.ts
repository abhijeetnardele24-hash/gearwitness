import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: false,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000",
    cwd: "../",
    url: "http://127.0.0.1:8000/api/v1/health",
    reuseExistingServer: true,
    timeout: 15000,
  },
});
