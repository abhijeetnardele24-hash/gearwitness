const { chromium } = require("../frontend/node_modules/playwright");
const path = require("path");
const fs = require("fs");

async function previewReadmeWorkflow() {
  const svgPath = path.resolve(__dirname, "../docs/assets/forensic_operator_workflow.svg");
  const svgContent = fs.readFileSync(svgPath, "utf8");

  const browser = await chromium.launch();
  // Standard GitHub desktop article width (~980px)
  const context = await browser.newContext({
    viewport: { width: 1012, height: 700 },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>GitHub README Preview</title>
      <style>
        body {
          background-color: #0d1117;
          color: #c9d1d9;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          margin: 0;
          padding: 24px;
          display: flex;
          justify-content: center;
        }
        .markdown-body {
          max-width: 980px;
          width: 100%;
        }
        .markdown-body h2 {
          font-size: 24px;
          border-bottom: 1px solid #21262d;
          padding-bottom: 8px;
          margin-bottom: 16px;
        }
        .workflow-img {
          width: 100%;
          height: auto;
          display: block;
          border-radius: 8px;
          margin: 16px 0;
        }
      </style>
    </head>
    <body>
      <div class="markdown-body">
        <h2>🔄 Forensic Operator Workflow</h2>
        <img class="workflow-img" src="data:image/svg+xml;utf8,${encodeURIComponent(svgContent)}" alt="Forensic Operator Workflow: Five-Stage Inspection Pipeline" />
      </div>
    </body>
    </html>
  `;

  await page.setContent(html, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);

  const previewPath = path.resolve(__dirname, "../docs/assets/github_readme_preview.png");
  await page.screenshot({ path: previewPath });
  console.log(`Saved GitHub width preview to ${previewPath}`);

  await browser.close();
}

previewReadmeWorkflow().catch((err) => {
  console.error(err);
  process.exit(1);
});
