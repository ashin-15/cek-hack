import { test, expect } from "@playwright/test";
test("full demo journey, estimator isolation, safety provenance, chat and evidence", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "A clearer picture of your home." }),
  ).toBeVisible();
  await expect(page.locator(".chart svg").first()).toBeVisible();
  await page.getByRole("button", { name: "Re-run saved model" }).click();
  await expect(
    page.getByText(/Live inference from saved artifact/),
  ).toBeVisible();
  await page.getByRole("button", { name: "15 min", exact: true }).click();
  await page.getByRole("button", { name: "Review event", exact: true }).click();
  await page.getByRole("link", { name: "Appliances", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Likely appliance events" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Power quality", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Power quality, made visible." }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Safety", exact: true }).click();
  await expect(page.locator(".badge").first()).toHaveText("Simulated");
  await expect(
    page.getByText("Confidence: Not calibrated").first(),
  ).toBeVisible();
  await page.getByRole("link", { name: "Cost & savings", exact: true }).click();
  await page.getByLabel("Monthly power usage").fill("100");
  await page.getByRole("button", { name: "Calculate what-if" }).click();
  await expect(page.locator(".estimate-result")).toContainText("₹465.00");
  await page.getByRole("link", { name: "Ask Paranova", exact: true }).click();
  await page
    .getByLabel("Ask about household energy")
    .fill("Why is my bill higher?");
  await page.getByRole("button", { name: "Send question" }).click();
  await expect(page.locator(".answer")).toContainText("no prior bill");
  await page.getByRole("button", { name: "Evidence", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("Forecast bake-off");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
  await page.goto("/consumption");
  await expect(
    page.getByRole("heading", { name: "A clearer picture of your home." }),
  ).toBeVisible();
  await page.screenshot({
    path: "/tmp/paranova-desktop.png",
    fullPage: true,
    animations: "disabled",
  });
});
test("mobile navigation and layout", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "A clearer picture of your home." }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page.getByRole("link", { name: "Safety", exact: true }).click();
  await expect(page.locator(".badge").first()).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "/tmp/paranova-mobile.png",
    fullPage: true,
    animations: "disabled",
  });
});
