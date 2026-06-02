import { expect, test } from "@playwright/test";

test("runs fixture-backed research and opens source evidence", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Research Workbench" })).toBeVisible();
  await page.getByLabel("Ticker").fill("NVDA");
  await page.getByRole("button", { name: "Start research" }).click();

  await expect(page.getByRole("status")).toContainText("Running research...");
  await expect(page.getByRole("region", { name: "Research report" })).toBeVisible();
  await expect(page.getByText("Evidence memo")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Trade ideas" })).toBeVisible();
  await expect(page.getByText("Fixture RSS feed represents partial news coverage")).toBeVisible();

  const sourceDrawer = page.getByRole("complementary", { name: "Source drawer" });
  await expect(sourceDrawer).toBeVisible();
  await expect(sourceDrawer.getByRole("button", { name: /market.*Fixture.*fixture/i })).toBeVisible();

  await sourceDrawer.getByRole("button", { name: /market/i }).click();
  await expect(page.getByRole("article", { name: "Source detail" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "NVDA market snapshot" })).toBeVisible();
  await expect(page.getByText(/"price": 125/)).toBeVisible();

  await expect(page.getByRole("button", { name: /NVDA completed_with_warnings/i })).toBeVisible();
});
