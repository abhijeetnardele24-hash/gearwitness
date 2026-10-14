const { chromium } = require("../frontend/node_modules/playwright");
const path = require("path");
const fs = require("fs");

async function run() {
  const assetsDir = path.resolve(__dirname, "../docs/assets");
  const screenshotsDir = path.resolve(__dirname, "../docs/screenshots");
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });
  if (!fs.existsSync(screenshotsDir)) fs.mkdirSync(screenshotsDir, { recursive: true });

  const browser = await chromium.launch();

  // 1. Desktop Workstation (1440x900)
  {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();
    await page.goto("http://127.0.0.1:8000/", { waitUntil: "networkidle" });
    await page.waitForSelector("#main-content");
    await page.waitForTimeout(500);

    const desktopPath = path.join(assetsDir, "desktop_workstation.png");
    const workspaceHeroPath = path.join(screenshotsDir, "workspace_hero.png");
    await page.screenshot({ path: desktopPath, fullPage: false });
    await page.screenshot({ path: workspaceHeroPath, fullPage: false });
    console.log("Captured desktop_workstation.png & workspace_hero.png");

    // 2. Guided Capture Assistant Modal
    const guidedBtn = page.locator("#btn-guided-capture");
    await guidedBtn.click();
    await page.waitForSelector(".modal-backdrop");
    await page.waitForTimeout(400);

    const guidedPath = path.join(assetsDir, "guided_capture_modal.png");
    const guidedScreenPath = path.join(screenshotsDir, "guided_capture_assistant.png");
    await page.screenshot({ path: guidedPath });
    await page.screenshot({ path: guidedScreenPath });
    console.log("Captured guided_capture_modal.png & guided_capture_assistant.png");

    // Close guided modal
    await page.locator("#btn-close-capture-modal").click();
    await page.waitForTimeout(400);

    // 3. Complete Proposals & Capture Report Modal
    const exportBtn = page.locator("#btn-export-report");
    await exportBtn.click();
    await page.waitForSelector(".report-modal", { timeout: 3000 });
    await page.waitForTimeout(500);

    const reportPath = path.join(assetsDir, "audit_report_manifest.png");
    const reportScreenPath = path.join(screenshotsDir, "audit_report_manifest.png");
    await page.screenshot({ path: reportPath });
    await page.screenshot({ path: reportScreenPath });
    console.log("Captured audit_report_manifest.png");

    await context.close();
  }

  // 4. Mobile Responsive View (390x844)
  {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();
    await page.goto("http://127.0.0.1:8000/", { waitUntil: "networkidle" });
    await page.waitForSelector("#main-content");
    await page.waitForTimeout(500);

    const mobilePath = path.join(assetsDir, "mobile_workflow.png");
    await page.screenshot({ path: mobilePath, fullPage: true });
    console.log("Captured mobile_workflow.png");
    await context.close();
  }

  // 5. Hero Banner (1280x600)
  {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 600 },
      deviceScaleFactor: 2,
    });
    const page = await context.newPage();
    await page.goto("http://127.0.0.1:8000/", { waitUntil: "networkidle" });
    await page.waitForSelector("#main-content");
    await page.waitForTimeout(500);

    const heroPath = path.join(assetsDir, "hero_banner.png");
    const coverPath = path.join(assetsDir, "cover_image.png");
    await page.screenshot({ path: heroPath, fullPage: false });
    await page.screenshot({ path: coverPath, fullPage: false });
    console.log("Captured hero_banner.png & cover_image.png");
    await context.close();
  }

  await browser.close();
  console.log("All authentic application screenshots captured successfully!");
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
