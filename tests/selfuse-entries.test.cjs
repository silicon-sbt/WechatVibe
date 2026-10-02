const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const path = require("node:path");
const { it } = require("node:test");

const root = path.join(__dirname, "..");
const html = readFileSync(path.join(root, "chatui/index.html"), "utf8");
const app = readFileSync(path.join(root, "chatui/app.js"), "utf8");

it("ships every self-use entry point in the sidebar and settings modal", () => {
  for (const id of ["btnAddAllConversations", "btnToggleBackgroundAnalyze", "sweepProgress",
                    "sweepProgressLabel", "sweepProgressValue", "sweepProgressFill",
                    "btnWorkerMinus", "btnWorkerPlus", "btnToggleElasticWorkers",
                    "workerLimitValue", "workerLimitHint"]) {
    assert.ok(html.includes(`id="${id}"`), `index.html must ship #${id}`);
  }
  for (const name of ["addAllConversations", "trackNewConversations", "backgroundAnalyzeAll",
                      "loadAnalysisOverview", "loadWorkerSettings", "changeWorkerSettings"]) {
    assert.match(app, new RegExp(`(?:async )?function ${name}\\(`), `app.js must define ${name}`);
  }
});

it("renders image messages from the local bridge with a zoom and retry path", () => {
  const css = readFileSync(path.join(root, "chatui/style.css"), "utf8");
  assert.ok(app.includes('image.className = "msg-image"'));
  assert.ok(app.includes('"/api/media?user="'));
  assert.ok(app.includes('image.classList.toggle("zoomed")'));
  assert.ok(app.includes('&retry=" + attempts'));
  assert.ok(app.includes('element("div", "msg-bubble", "[图片]")'));
  assert.ok(css.includes(".msg-image {"));
  assert.ok(css.includes(".msg-image.zoomed {"));
});

it("keeps the self-use calls on the documented bridge endpoints", () => {
  assert.ok(app.includes('"/api/conversation-selection"'));
  assert.ok(app.includes('"/api/analysis-overview"'));
  assert.ok(app.includes('"/api/analysis-workers"'));
  assert.ok(app.includes('"/api/analyze"'));
  // The sweep is gated by the local model, not by how many conversations are selected.
  const sweep = app.slice(app.indexOf("async function backgroundAnalyzeAll("));
  assert.ok(sweep.includes("canAnalyzeLocal()"), "the sweep must require the local model");
  assert.ok(sweep.includes("settingsState.settings.backgroundAnalyze"),
    "the sweep must honour the background-analysis switch");
});
