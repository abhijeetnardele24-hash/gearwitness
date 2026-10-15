import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("GearWitness Complete Forensic Operator Journey", () => {
  test("loads application with zero console errors, zero broken images, and complete operator workflow", async ({
    page,
  }) => {
    const consoleErrors: string[] = [];
    const failedRequests: string[] = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    page.on("requestfailed", (req) => {
      // Ignore aborts on navigation
      if (req.failure()?.errorText !== "net::ERR_ABORTED") {
        failedRequests.push(`${req.url()} (${req.failure()?.errorText})`);
      }
    });

    // 1. Application Load
    await page.goto("http://127.0.0.1:8000/");
    await page.waitForSelector("#main-content", { state: "visible" });

    // Verify Brand, Mode, and Identity
    await expect(page.locator(".brand-title")).toHaveText("GearWitness");
    await expect(page.locator(".mode-label")).toContainText("MODE:");
    await expect(page.locator("#asset-title")).toBeVisible();

    // Verify zero console errors & zero failed requests on initial load
    expect(consoleErrors).toEqual([]);
    expect(failedRequests).toEqual([]);

    // 2. Assert every visible image has complete=true and naturalWidth > 0
    await page.waitForLoadState("networkidle");
    const images = await page.locator("img").all();
    expect(images.length).toBeGreaterThan(0);
    for (const img of images) {
      if (await img.isVisible()) {
        await img.evaluate(async (el: HTMLImageElement) => {
          if (!el.complete) {
            await new Promise((resolve) => {
              el.onload = resolve;
              el.onerror = resolve;
            });
          }
        });
        const imgInfo = await img.evaluate((el: HTMLImageElement) => ({
          src: el.src,
          complete: el.complete,
          naturalWidth: el.naturalWidth,
        }));
        expect(imgInfo.complete, `Image ${imgInfo.src} did not complete loading`).toBe(true);
        expect(imgInfo.naturalWidth, `Image ${imgInfo.src} has broken naturalWidth 0`).toBeGreaterThan(0);
      }
    }

    // 3. Compare Canvas Interactions (Reveal Divider & Hotspots)
    const slider = page.locator(".slider-divider");
    await expect(slider).toBeVisible();
    const initialPos = await slider.getAttribute("aria-valuenow");
    expect(initialPos).toBe("50");

    // Keyboard move slider
    await slider.focus();
    await page.keyboard.press("ArrowLeft");
    await expect(slider).toHaveAttribute("aria-valuenow", "45");
    await page.keyboard.press("ArrowRight");
    await expect(slider).toHaveAttribute("aria-valuenow", "50");

    // 4. Change Proposal Decisions: Confirm, Dismiss, and Uncertain
    const confirmBtn = page.locator("#btn-confirm-prop_01_scratch");
    await expect(confirmBtn).toBeVisible();
    await confirmBtn.click();
    await expect(confirmBtn).toHaveClass(/active/);

    const dismissBtn = page.locator("#btn-dismiss-prop_02_glare");
    await expect(dismissBtn).toBeVisible();
    await dismissBtn.click();
    await expect(dismissBtn).toHaveClass(/active/);

    const uncertainBtn = page.locator("#btn-uncertain-prop_03_cable");
    if (await uncertainBtn.isVisible()) {
      await uncertainBtn.click();
      await expect(uncertainBtn).toHaveClass(/active/);
    }

    // 5. Kit Inventory Checklist Updates
    const kitItemToggle = page.locator("#toggle-missing-kit_04");
    if (await kitItemToggle.isVisible()) {
      await kitItemToggle.click();
      await expect(page.locator("#kit-row-kit_04")).toHaveClass(/item-missing/);
    }

    // 6. Guided Capture Modal
    const guidedCaptureBtn = page.locator("#btn-guided-capture");
    await guidedCaptureBtn.click();
    await expect(page.locator(".capture-modal")).toBeVisible();

    // Verify Step Selection
    const backAngleTab = page.locator("#angle-step-back");
    await backAngleTab.click();
    await expect(page.locator(".angle-detail-header h3")).toContainText("Back Display");

    // Close capture modal
    await page.locator("#btn-close-capture-modal").click();
    await expect(page.locator(".capture-modal")).not.toBeVisible();

    // 7. Audit Report & Manifest Workflow
    const exportBtn = page.locator("#btn-export-report");
    await exportBtn.click();
    await expect(page.locator(".report-modal")).toBeVisible();

    // Verify SHA-256 Content Integrity Digest renders
    await expect(page.locator(".hash-badge")).toHaveText("SHA-256 CONTENT INTEGRITY DIGEST");
    await expect(page.locator("#val-manifest-hash")).toBeVisible();

    // Verify Approve and Finalize Manifest
    const approveBtn = page.locator("#btn-approve-signoff");
    if (await approveBtn.isVisible()) {
      await approveBtn.click();
      await expect(page.locator(".modal-footer")).toContainText("Manifest Approved & Finalized");
    }

    // Close modal
    await page.locator("#btn-close-modal").click();
    await expect(page.locator(".report-modal")).not.toBeVisible();

    // 8. Axe Core Accessibility Audit (Zero serious or critical violations)
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    const seriousOrCritical = accessibilityScanResults.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical"
    );
    expect(seriousOrCritical).toEqual([]);
  });

  // 9. Responsive Viewport Tests (360, 768, 1024, 1440, 1920)
  const viewports = [
    { width: 360, height: 740, name: "Mobile (360px)" },
    { width: 768, height: 1024, name: "Tablet (768px)" },
    { width: 1024, height: 768, name: "Small Desktop (1024px)" },
    { width: 1440, height: 900, name: "Standard Desktop (1440px)" },
    { width: 1920, height: 1080, name: "Full HD Studio (1920px)" },
  ];

  for (const vp of viewports) {
    test(`renders without horizontal overflow at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto("http://127.0.0.1:8000/");
      await page.waitForSelector("#main-content", { state: "visible" });

      // Check horizontal overflow
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2); // allow sub-pixel rounding
    });
  }
});
