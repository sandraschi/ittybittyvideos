import { test, expect } from "@playwright/test";

test.describe("ittybitty webapp smoke", () => {
  test("dashboard loads with fleet branding", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.locator("nav").getByText("ittybitty", { exact: true })).toBeVisible();
  });

  test("sidebar navigates to status and shows API health JSON", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Status" }).click();
    await expect(page.getByRole("heading", { name: "Status" })).toBeVisible();
    const pre = page.locator("pre");
    await expect(pre).toBeVisible();
    await expect(pre).toContainText("health");
    await expect(pre).toContainText("ittybitty");
  });

  test("help page overview tab renders", async ({ page }) => {
    await page.goto("/help");
    await expect(page.getByRole("heading", { name: /Help/i })).toBeVisible();
    await expect(page.getByText("What is ittybitty?")).toBeVisible();
  });

  test("help links catalog tab renders", async ({ page }) => {
    await page.goto("/help");
    await page.getByRole("tab", { name: "Links" }).click();
    await expect(page.getByText("Core stack")).toBeVisible();
    await expect(page.getByText("SadTalker")).toBeVisible();
  });

  test("tools page lists MCP tools from backend", async ({ page }) => {
    await page.goto("/tools");
    await expect(page.getByRole("heading", { name: /Tools/i })).toBeVisible();
    await expect(page.getByText("videogen_generate")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("videogen_review")).toBeVisible();
  });
});
