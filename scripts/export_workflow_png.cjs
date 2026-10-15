const { chromium } = require("../frontend/node_modules/playwright");
const path = require("path");
const fs = require("fs");

async function renderSvgToPng() {
  const svgPath = path.resolve(__dirname, "../docs/assets/forensic_operator_workflow.svg");
  const pngPath = path.resolve(__dirname, "../docs/assets/forensic_operator_workflow.png");

  if (!fs.existsSync(svgPath)) {
    throw new Error(`SVG file not found at ${svgPath}`);
  }

  const svgContent = fs.readFileSync(svgPath, "utf8");

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1600, height: 440 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  // Load clean HTML document containing the SVG
  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { background: transparent; overflow: hidden; }
          svg { display: block; width: 1600px; height: 440px; }
        </style>
      </head>
      <body>
        ${svgContent}
      </body>
    </html>
  `;

  await page.setContent(htmlContent, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);

  await page.screenshot({
    path: pngPath,
    omitBackground: true,
  });

  await browser.close();
  console.log(`Successfully exported crisp PNG to ${pngPath}`);
}

renderSvgToPng().catch((err) => {
  console.error("Failed to render SVG to PNG:", err);
  process.exit(1);
});
