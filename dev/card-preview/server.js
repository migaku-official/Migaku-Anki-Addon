const fs = require("fs");
const http = require("http");
const path = require("path");

const { renderCardDocument } = require("./card-document");
const contract = require("./template-contract.json");
const {
  buildLocalizedFixture,
  fixtures,
  toggleFields,
} = require("./fixtures");
const { writeCardStyles } = require("../../tools/card-styles");

const lucidePath = require.resolve("lucide/dist/umd/lucide.js");

const contentTypes = {
  ".gif": "image/gif",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".mp3": "audio/mpeg",
  ".m4a": "audio/mp4",
  ".ogg": "audio/ogg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ttf": "font/ttf",
  ".wav": "audio/wav",
  ".webp": "image/webp",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

const renderOptions = (items, getLabel = (item) => item) =>
  items.map((item) => `<option value="${item}">${getLabel(item)}</option>`).join("");
const renderFieldToggles = () =>
  toggleFields
    .map((field) => `<label class="field-toggle"><input type="checkbox" data-field="${field}">${field}</label>`)
    .join("");

const renderAppShell = () => `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Card Front-end Lab</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      background: #111318;
      color: #f6f7fb;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; overflow: hidden; }
    body { margin: 0; background: #111318; }
    .app { display: grid; grid-template-rows: auto minmax(0, 1fr); height: 100vh; overflow: hidden; }
    .toolbar {
      position: relative;
      z-index: 1;
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
      align-items: flex-end;
      padding: 8px 12px;
      border-bottom: 1px solid #30343d;
      background: #1a1d24;
      box-shadow: 0 10px 30px rgb(0 0 0 / 25%);
    }
    .brand { display: none; }
    .brand span, .status { display: none; }
    label { display: grid; flex: 0 1 auto; min-width: 0; gap: 4px; color: #afb5c2; font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
    select, button {
      min-height: 38px;
      border: 1px solid #3b404b;
      border-radius: 8px;
      background: #242832;
      color: #f6f7fb;
      font: inherit;
    }
    select { min-width: 112px; padding: 0 30px 0 10px; }
    #fixture { min-width: 160px; }
    .audio-choice { display: flex; align-items: center; min-height: 38px; gap: 8px; padding: 0 10px; border: 1px solid #3b404b; border-radius: 8px; background: #242832; color: #f6f7fb; font-size: 12px; letter-spacing: 0; text-transform: none; }
    .audio-choice input { width: 16px; height: 16px; margin: 0; }
    #theme-toggle {
      display: grid;
      flex: 0 0 auto;
      place-items: center;
      margin-left: 0;
      width: 40px;
      min-width: 40px;
      padding: 0;
    }
    #theme-toggle svg { width: 20px; height: 20px; }
    button { padding: 0 12px; cursor: pointer; }
    button:hover, button[aria-pressed="true"] { border-color: #6d8dff; background: #31416f; }
    .viewport-picker { display: flex; flex-wrap: wrap; gap: 4px; }
    .viewport-picker button { min-width: 44px; }
    .toolbar-actions { margin-left: auto; display: flex; flex: 0 1 auto; flex-wrap: wrap; justify-content: flex-end; align-items: center; gap: 8px; }
    .field-menu { position: relative; flex: 0 0 auto; }
    .field-menu summary { display: grid; grid-auto-flow: column; place-items: center; width: auto; min-height: 38px; gap: 8px; padding: 0 12px; border: 1px solid #3b404b; border-radius: 8px; background: #242832; cursor: pointer; font-size: 12px; font-weight: 700; list-style: none; }
    .field-menu summary svg { width: 20px; height: 20px; }
    .field-menu-content { position: absolute; z-index: 2; top: calc(100% + 8px); right: 0; display: grid; width: min(360px, calc(100vw - 24px)); grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 16px; padding: 12px; border: 1px solid #3b404b; border-radius: 10px; background: #1a1d24; box-shadow: 0 12px 32px rgb(0 0 0 / 40%); }
    .field-toggle { display: flex; align-items: center; gap: 8px; font-size: 12px; letter-spacing: 0; text-transform: none; }
    .workspace { min-height: 0; overflow: hidden; padding: 8px; background-color: #111318; background-image: radial-gradient(#2d323d 1px, transparent 1px); background-size: 18px 18px; }
    .device {
      width: min(100%, var(--preview-width, 100%));
      height: 100%;
      min-height: 0;
      margin: 0 auto;
      overflow: hidden;
      border: 1px solid #3b404b;
      border-radius: 14px;
      background: white;
      box-shadow: 0 18px 60px rgb(0 0 0 / 35%);
      transition: width 180ms ease;
    }
    iframe { display: block; width: 100%; height: 100%; min-height: 0; border: 0; background: white; }
    @media (max-width: 760px) {
      .workspace { padding: 8px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <header class="toolbar">
      <div class="brand">
        <strong>Card Front-end Lab</strong>
        <span id="status">Watching shipped card files</span>
      </div>
      <label>Language
        <select id="language">${renderOptions(contract.languages)}</select>
      </label>
      <label>Side
        <select id="side"><option value="front">Front</option><option value="back">Back</option></select>
      </label>
      <label>Fixture
        <select id="fixture">${renderOptions(
          Object.keys(fixtures),
          (name) => fixtures[name].label,
        )}</select>
      </label>
      <label>Front content
        <span class="audio-choice"><input type="checkbox" id="audio-card">Audio</span>
      </label>
      <label>Viewport
        <span class="viewport-picker">
          <button type="button" data-viewport="100%" aria-label="Responsive desktop" aria-pressed="true">Wide</button>
          <button type="button" data-viewport="768px" aria-label="Tablet">768</button>
          <button type="button" data-viewport="390px" aria-label="Mobile">390</button>
        </span>
      </label>
      <div class="toolbar-actions">
        <details class="field-menu">
          <summary aria-label="Choose populated fields" title="Fields"><span>Fields</span><i data-lucide="list"></i></summary>
          <div class="field-menu-content">${renderFieldToggles()}</div>
        </details>
        <button type="button" id="theme-toggle" aria-label="Switch to dark mode" aria-pressed="false"><i data-lucide="moon"></i></button>
      </div>
    </header>
    <main class="workspace">
      <div class="device" id="device">
        <iframe id="preview" title="Card preview"></iframe>
      </div>
    </main>
  </div>
  <script src="/vendor/lucide.js"></script>
  <script>
    const controls = ["language", "side", "fixture"].map((id) => document.getElementById(id));
    const audioCard = document.getElementById("audio-card");
    const side = document.getElementById("side");
    const themeToggle = document.getElementById("theme-toggle");
    const device = document.getElementById("device");
    const frame = document.getElementById("preview");
    const status = document.getElementById("status");
    const viewportButtons = Array.from(document.querySelectorAll("[data-viewport]"));
    const fieldToggles = Array.from(document.querySelectorAll("[data-field]"));
    const interactivePreviewSelector = "a, audio, button, input, label, select, textarea, .word, .popup";
    const fixtureFieldPresence = ${JSON.stringify(
      Object.fromEntries(
        Object.keys(fixtures).map((fixtureName) => [
          fixtureName,
          toggleFields.filter(
            (field) => buildLocalizedFixture("en", fixtureName).fields[field],
          ),
        ]),
      ),
    )};
    const query = new URLSearchParams(window.location.search);
    const themeState = { value: ["light", "dark", "ankidroid"].includes(query.get("theme")) ? query.get("theme") : "light" };
    const applyQuery = () => {
      controls.forEach((control) => {
        const value = query.get(control.id);
        if (value && Array.from(control.options).some((option) => option.value === value)) control.value = value;
      });
      audioCard.checked = query.get("audio") === "1";
    };
    const enabledQueryFields = query.getAll("field");
    const syncFixtureFields = () => fieldToggles.forEach((toggle) => toggle.checked = fixtureFieldPresence[document.getElementById("fixture").value].includes(toggle.dataset.field));
    if (enabledQueryFields.length) fieldToggles.forEach((toggle) => toggle.checked = enabledQueryFields.includes(toggle.dataset.field));
    else syncFixtureFields();
    const getParams = () => {
      const params = new URLSearchParams(Object.fromEntries(controls.map((control) => [control.id, control.value])));
      params.set("audio", audioCard.checked ? "1" : "0");
      params.set("theme", themeState.value);
      params.set("fields", "configured");
      fieldToggles.filter((toggle) => toggle.checked).forEach((toggle) => params.append("field", toggle.dataset.field));
      return params;
    };
    const render = () => {
      const params = getParams();
      window.history.replaceState(null, "", "?" + params.toString());
      params.set("_reload", Date.now().toString());
      frame.src = "/preview?" + params.toString();
    };
    const toggleSide = () => {
      side.value = side.value === "front" ? "back" : "front";
      render();
    };
    const syncThemeToggle = () => {
      const isDark = themeState.value !== "light";
      themeToggle.setAttribute("aria-label", "Switch to " + (isDark ? "light" : "dark") + " mode");
      themeToggle.setAttribute("aria-pressed", String(isDark));
      themeToggle.innerHTML = '<i data-lucide="' + (isDark ? "sun" : "moon") + '"></i>';
      lucide.createIcons();
    };
    const toggleTheme = () => {
      themeState.value = themeState.value === "light" ? "dark" : "light";
      syncThemeToggle();
      render();
    };
    const setViewport = (button) => {
      viewportButtons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      device.style.setProperty("--preview-width", button.dataset.viewport);
    };
    applyQuery();
    syncThemeToggle();
    controls.forEach((control) => control.addEventListener("change", () => {
      if (control.id === "fixture") syncFixtureFields();
      render();
    }));
    fieldToggles.forEach((toggle) => toggle.addEventListener("change", render));
    audioCard.addEventListener("change", render);
    themeToggle.addEventListener("click", toggleTheme);
    frame.addEventListener("load", () =>
      frame.contentDocument?.addEventListener("click", (event) => {
        if (event.target.closest(interactivePreviewSelector)) return;
        toggleSide();
      }),
    );
    viewportButtons.forEach((button) => button.addEventListener("click", () => setViewport(button)));
    const events = new EventSource("/events");
    events.addEventListener("reload", () => {
      status.textContent = "Reloaded " + new Date().toLocaleTimeString();
      render();
    });
    events.addEventListener("error", () => status.textContent = "Live reload disconnected");
    render();
  </script>
</body>
</html>`;

const send = (res, statusCode, contentType, body) => {
  res.writeHead(statusCode, {
    "Cache-Control": "no-store",
    "Content-Type": `${contentType}; charset=utf-8`,
  });
  res.end(body);
};

const findMediaFile = (rootDir, requestedLanguage, assetName) => {
  const languages = requestedLanguage
    ? [requestedLanguage, ...contract.languages.filter((item) => item !== requestedLanguage)]
    : contract.languages;
  return languages
    .map((language) =>
      path.join(rootDir, "src", "languages", language, "card", "media", assetName),
    )
    .find((candidate) => fs.existsSync(candidate));
};

const serveMedia = (rootDir, pathname, res) => {
  const mediaMatch = pathname.match(/^\/media\/([^/]+)\/([^/]+)$/);
  const requestedLanguage = mediaMatch ? mediaMatch[1] : "";
  const assetName = path.basename(mediaMatch ? mediaMatch[2] : pathname);
  const filePath = findMediaFile(rootDir, requestedLanguage, assetName);
  if (!filePath) return false;
  const contentType = contentTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream";
  res.writeHead(200, { "Cache-Control": "no-store", "Content-Type": contentType });
  fs.createReadStream(filePath).pipe(res);
  return true;
};

const serveFixtureMedia = (rootDir, pathname, res) => {
  const filePath = path.join(
    rootDir,
    "dev",
    "card-preview",
    "media",
    path.basename(pathname),
  );
  if (!fs.existsSync(filePath)) return false;
  const contentType =
    contentTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream";
  res.writeHead(200, { "Cache-Control": "no-store", "Content-Type": contentType });
  fs.createReadStream(filePath).pipe(res);
  return true;
};

const createWatchers = (rootDir, notify) => {
  const directories = [
    path.join(rootDir, "dev", "card-preview"),
    path.join(rootDir, "src", "card-styles"),
    ...contract.languages.map((language) =>
      path.join(rootDir, "src", "languages", language, "card"),
    ),
  ];
  const debounce = { timeout: null };
  const refresh = () => {
    writeCardStyles(rootDir);
    notify();
  };
  const watchers = directories.map((directory) =>
    fs.watch(directory, (eventType, filename) => {
      if (filename && filename.toString() === "styles.css") return;
      if (debounce.timeout) clearTimeout(debounce.timeout);
      debounce.timeout = setTimeout(refresh, 80);
    }),
  );
  return () => {
    if (debounce.timeout) clearTimeout(debounce.timeout);
    watchers.forEach((watcher) => watcher.close());
  };
};

const createPreviewServer = ({ rootDir, watch = true }) => {
  writeCardStyles(rootDir);
  const clients = new Set();
  const notify = () =>
    clients.forEach((client) => client.write(`event: reload\ndata: ${Date.now()}\n\n`));
  const closeWatchers = watch ? createWatchers(rootDir, notify) : () => {};
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname === "/") return send(res, 200, "text/html", renderAppShell());
    if (url.pathname === "/vendor/lucide.js") return send(res, 200, "text/javascript", fs.readFileSync(lucidePath));
    if (url.pathname === "/events") {
      res.writeHead(200, {
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "Content-Type": "text/event-stream",
      });
      res.write("event: ready\ndata: connected\n\n");
      clients.add(res);
      req.on("close", () => clients.delete(res));
      return;
    }
    if (url.pathname === "/preview") {
      try {
        const document = renderCardDocument({
          audioCard: url.searchParams.get("audio") === "1",
          enabledFields: url.searchParams.has("fields") || url.searchParams.has("field")
            ? url.searchParams.getAll("field")
            : undefined,
          fixtureName: url.searchParams.get("fixture") || "sentence",
          language: url.searchParams.get("language") || "en",
          rootDir,
          side: url.searchParams.get("side") || "front",
          theme: url.searchParams.get("theme") || "light",
        });
        return send(res, 200, "text/html", document);
      } catch (error) {
        return send(res, 400, "text/plain", error.message);
      }
    }
    if (url.pathname.startsWith("/fixture-media/")) {
      if (serveFixtureMedia(rootDir, decodeURIComponent(url.pathname), res)) return;
    }
    if (url.pathname.startsWith("/media/") || url.pathname.startsWith("/_")) {
      if (serveMedia(rootDir, decodeURIComponent(url.pathname), res)) return;
    }
    send(res, 404, "text/plain", "Not found");
  });
  server.on("close", () => {
    closeWatchers();
    clients.forEach((client) => client.end());
  });
  return server;
};

const start = () => {
  const rootDir = path.resolve(__dirname, "..", "..");
  const port = Number(process.env.CARD_PREVIEW_PORT) || 4173;
  const server = createPreviewServer({ rootDir });
  server.listen(port, "127.0.0.1", () =>
    console.log(`Card Front-end Lab running at http://127.0.0.1:${port}`),
  );
};

if (require.main === module) start();

module.exports = { createPreviewServer };
