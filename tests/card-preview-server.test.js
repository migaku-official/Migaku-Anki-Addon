const assert = require("assert");
const fs = require("fs");
const http = require("http");
const os = require("os");
const path = require("path");

const { createPreviewServer } = require("../dev/card-preview/server");
const contract = require("../dev/card-preview/template-contract.json");

const request = (port, requestPath) =>
  new Promise((resolve, reject) => {
    const req = http.get({ host: "127.0.0.1", path: requestPath, port }, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () =>
        resolve({
          body: Buffer.concat(chunks).toString("utf8"),
          statusCode: res.statusCode,
        }),
      );
    });
    req.on("error", reject);
  });
const requestBinary = (port, requestPath) =>
  new Promise((resolve, reject) => {
    const req = http.get({ host: "127.0.0.1", path: requestPath, port }, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () =>
        resolve({
          body: Buffer.concat(chunks),
          contentType: res.headers["content-type"],
          statusCode: res.statusCode,
        }),
      );
    });
    req.on("error", reject);
  });

const waitFor = (predicate, timeoutMs = 2000) =>
  new Promise((resolve, reject) => {
    const startedAt = Date.now();
    const poll = () => {
      if (predicate()) return resolve();
      if (Date.now() - startedAt > timeoutMs) return reject(new Error("Timed out waiting for live style rebuild"));
      setTimeout(poll, 20);
    };
    poll();
  });

const waitForEvent = (port, eventName, trigger, timeoutMs = 2000) =>
  new Promise((resolve, reject) => {
    const state = { body: "", settled: false, triggered: false };
    const timeout = setTimeout(
      () => finish(new Error(`Timed out waiting for ${eventName} event`)),
      timeoutMs,
    );
    const finish = (error) => {
      if (state.settled) return;
      state.settled = true;
      clearTimeout(timeout);
      req.destroy();
      if (error) return reject(error);
      resolve();
    };
    const req = http.get({ host: "127.0.0.1", path: "/events", port }, (res) => {
      res.on("data", (chunk) => {
        state.body += chunk.toString("utf8");
        if (!state.triggered && state.body.includes("event: ready\n")) {
          state.triggered = true;
          setTimeout(trigger, 50);
        }
        if (state.body.includes(`event: ${eventName}\n`)) finish();
      });
    });
    req.on("error", (error) => !state.settled && finish(error));
  });

const testLiveStyleRebuild = async () => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "migaku-card-preview-"));
  const globalStylesDir = path.join(rootDir, "src", "card-styles");
  fs.mkdirSync(path.join(rootDir, "dev", "card-preview"), { recursive: true });
  fs.mkdirSync(globalStylesDir, { recursive: true });
  fs.writeFileSync(path.join(globalStylesDir, "global.css"), ".card {\n  color: red;\n}\n");
  fs.writeFileSync(path.join(globalStylesDir, "legacy-variants.json"), "{}\n");
  contract.languages.forEach((language) => {
    const cardDir = path.join(rootDir, "src", "languages", language, "card");
    fs.mkdirSync(cardDir, { recursive: true });
    fs.writeFileSync(path.join(cardDir, "fonts.css"), `/* ${language} font */\n`);
  });
  const server = createPreviewServer({ rootDir });
  try {
    await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
    await waitForEvent(server.address().port, "reload", () =>
      fs.writeFileSync(
        path.join(globalStylesDir, "global.css"),
        ".card {\n  color: blue;\n}\n",
      ),
    );
    await waitFor(() =>
      fs
        .readFileSync(path.join(rootDir, "src", "languages", "en", "card", "styles.css"), "utf8")
        .includes("color: blue"),
    );
  } finally {
    if (server.listening) await new Promise((resolve) => server.close(resolve));
    fs.rmSync(rootDir, { force: true, recursive: true });
  }
};

const run = async () => {
  const server = createPreviewServer({
    rootDir: path.resolve(__dirname, ".."),
    watch: false,
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = server.address().port;

  const app = await request(port, "/");
  assert.strictEqual(app.statusCode, 200);
  assert.match(app.body, /Card Front-end Lab/);
  assert.match(app.body, /id="language"/);
  assert.match(
    app.body,
    /id="theme-toggle"[^>]*aria-label="Switch to dark mode"[^>]*><i data-lucide="moon"><\/i><\/button>/,
  );
  assert.match(
    app.body,
    /<div class="toolbar-actions">[\s\S]*<summary aria-label="Choose populated fields" title="Fields"><i data-lucide="list"><\/i><\/summary>[\s\S]*id="theme-toggle"/,
  );
  assert.match(app.body, /<script src="\/vendor\/lucide\.js"><\/script>/);
  assert.match(app.body, /lucide\.createIcons\(\)/);
  assert.match(app.body, /\.toolbar-actions\s*\{[^}]*margin-left: auto;[^}]*display: flex;/s);
  assert.match(app.body, /\.field-menu summary\s*\{[^}]*display: grid;[^}]*width: 28px;[^}]*padding: 0;/s);
  assert.match(app.body, /#theme-toggle\s*\{[^}]*margin-left: 0;[^}]*width: 28px;/s);
  assert.match(app.body, />Syntax showcase<\/option>/);
  assert.match(app.body, /new EventSource\("\/events"\)/);
  assert.match(app.body, /html, body\s*\{[^}]*height: 100%;[^}]*overflow: hidden;/s);
  assert.match(app.body, /\.app\s*\{[^}]*height: 100vh;[^}]*overflow: hidden;/s);
  assert.match(app.body, /\.toolbar\s*\{[^}]*flex-wrap: nowrap;[^}]*padding: 4px 8px;/s);
  assert.match(app.body, /\.brand\s*\{[^}]*display: none;/s);
  assert.match(app.body, /select\s*\{[^}]*min-width: 96px;/s);
  assert.match(app.body, /\.workspace\s*\{[^}]*overflow: hidden;/s);
  assert.match(app.body, /\.device\s*\{[^}]*height: 100%;[^}]*min-height: 0;/s);
  assert.match(app.body, /iframe\s*\{[^}]*height: 100%;[^}]*min-height: 0;/s);
  assert.match(app.body, /frame\.addEventListener\("load",/);
  assert.match(app.body, /side\.value = side\.value === "front" \? "back" : "front"/);
  assert.match(app.body, /theme\.value = theme\.value === "light" \? "dark" : "light"/);
  assert.match(app.body, /themeToggle\.addEventListener\("click", toggleTheme\)/);
  [
    "Sentence",
    "Translation",
    "Target Word",
    "Definitions",
    "Screenshot",
    "Sentence Audio",
    "Word Audio",
    "Images",
    "Example Sentences",
    "Notes",
    "Alternate Sentence",
    "Is Vocabulary Card",
    "Is Audio Card",
  ].forEach((field) => assert.match(app.body, new RegExp(`data-field="${field}"`)));
  assert.doesNotMatch(app.body, /data-field="Reading"/);

  const preview = await request(
    port,
    "/preview?language=en&side=back&theme=dark&fixture=sentence",
  );
  assert.strictEqual(preview.statusCode, 200);
  assert.match(preview.body, /data-preview-side="back"/);
  assert.match(preview.body, /Eine Sprache zu lernen/);

  const conditionalPreview = await request(
    port,
    "/preview?language=en&side=back&theme=dark&fixture=sentence&field=Target%20Word",
  );
  assert.match(conditionalPreview.body, /\(language\)\[language,noun/);
  assert.doesNotMatch(conditionalPreview.body, /\(Learning\)\[learn,verb/);

  const emptyPreview = await request(
    port,
    "/preview?language=en&side=back&theme=dark&fixture=sentence&fields=configured",
  );
  assert.doesNotMatch(emptyPreview.body, /\(language\)\[language,noun/);
  assert.doesNotMatch(emptyPreview.body, /\(Learning\)\[learn,verb/);
  assert.doesNotMatch(emptyPreview.body, /fixture-media/);

  for (const [asset, contentType] of [
    ["target-word.mp3", "audio/mpeg"],
    ["sentence.m4a", "audio/mp4"],
    ["vegeta-scouter.png", "image/png"],
  ]) {
    const media = await requestBinary(port, `/fixture-media/${asset}`);
    assert.strictEqual(media.statusCode, 200);
    assert.strictEqual(media.contentType, contentType);
    assert.ok(media.body.length > 1000);
  }

  const lucide = await request(port, "/vendor/lucide.js");
  assert.strictEqual(lucide.statusCode, 200);
  assert.match(lucide.body, /createIcons/);

  const invalid = await request(
    port,
    "/preview?language=en&side=middle&theme=dark&fixture=sentence",
  );
  assert.strictEqual(invalid.statusCode, 400);
  assert.match(invalid.body, /Unknown side/);

  await new Promise((resolve) => server.close(resolve));
  await testLiveStyleRebuild();
  console.log("✓ card preview server exposes the live development workflow");
};

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
