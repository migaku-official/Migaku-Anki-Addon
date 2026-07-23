const fs = require("fs");
const http = require("http");
const path = require("path");

const { renderCardDocument } = require("./card-document");
const contract = require("./template-contract.json");
const { fixtures } = require("./fixtures");
const { writeCardStyles } = require("../../tools/card-styles");

const contentTypes = {
  ".gif": "image/gif",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".mp3": "audio/mpeg",
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
    body { min-height: 100vh; margin: 0; background: #111318; }
    .app { display: grid; grid-template-rows: auto minmax(0, 1fr); min-height: 100vh; }
    .toolbar {
      position: relative;
      z-index: 1;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: end;
      padding: 14px 18px;
      border-bottom: 1px solid #30343d;
      background: #1a1d24;
      box-shadow: 0 10px 30px rgb(0 0 0 / 25%);
    }
    .brand { align-self: center; margin-right: auto; }
    .brand strong { display: block; font-size: 15px; }
    .brand span, .status { color: #9da3b1; font-size: 12px; }
    label { display: grid; gap: 5px; color: #afb5c2; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
    select, button {
      min-height: 36px;
      border: 1px solid #3b404b;
      border-radius: 8px;
      background: #242832;
      color: #f6f7fb;
      font: inherit;
    }
    select { min-width: 132px; padding: 0 32px 0 10px; }
    button { padding: 0 12px; cursor: pointer; }
    button:hover, button[aria-pressed="true"] { border-color: #6d8dff; background: #31416f; }
    .viewport-picker { display: flex; gap: 5px; }
    .viewport-picker button { min-width: 40px; }
    .workspace { min-height: 0; overflow: auto; padding: 24px; background-color: #111318; background-image: radial-gradient(#2d323d 1px, transparent 1px); background-size: 18px 18px; }
    .device {
      width: min(100%, var(--preview-width, 100%));
      min-height: calc(100vh - 120px);
      margin: 0 auto;
      overflow: hidden;
      border: 1px solid #3b404b;
      border-radius: 14px;
      background: white;
      box-shadow: 0 18px 60px rgb(0 0 0 / 35%);
      transition: width 180ms ease;
    }
    iframe { display: block; width: 100%; height: calc(100vh - 122px); min-height: 640px; border: 0; background: white; }
    @media (max-width: 760px) {
      .toolbar { align-items: stretch; }
      .brand { flex-basis: 100%; }
      label { flex: 1 1 120px; }
      select { width: 100%; min-width: 0; }
      .workspace { padding: 10px; }
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
      <label>Theme
        <select id="theme"><option value="light">Light</option><option value="dark">Anki dark</option><option value="ankidroid">AnkiDroid dark</option></select>
      </label>
      <label>Viewport
        <span class="viewport-picker">
          <button type="button" data-viewport="100%" aria-label="Responsive desktop" aria-pressed="true">Wide</button>
          <button type="button" data-viewport="768px" aria-label="Tablet">768</button>
          <button type="button" data-viewport="390px" aria-label="Mobile">390</button>
        </span>
      </label>
    </header>
    <main class="workspace">
      <div class="device" id="device">
        <iframe id="preview" title="Card preview"></iframe>
      </div>
    </main>
  </div>
  <script>
    const controls = ["language", "side", "fixture", "theme"].map((id) => document.getElementById(id));
    const device = document.getElementById("device");
    const frame = document.getElementById("preview");
    const status = document.getElementById("status");
    const viewportButtons = Array.from(document.querySelectorAll("[data-viewport]"));
    const query = new URLSearchParams(window.location.search);
    const applyQuery = () => controls.forEach((control) => {
      const value = query.get(control.id);
      if (value && Array.from(control.options).some((option) => option.value === value)) control.value = value;
    });
    const getParams = () => new URLSearchParams(Object.fromEntries(controls.map((control) => [control.id, control.value])));
    const render = () => {
      const params = getParams();
      window.history.replaceState(null, "", "?" + params.toString());
      params.set("_reload", Date.now().toString());
      frame.src = "/preview?" + params.toString();
    };
    const setViewport = (button) => {
      viewportButtons.forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      device.style.setProperty("--preview-width", button.dataset.viewport);
    };
    applyQuery();
    controls.forEach((control) => control.addEventListener("change", render));
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
  return directories.map((directory) =>
    fs.watch(directory, () => {
      if (debounce.timeout) clearTimeout(debounce.timeout);
      debounce.timeout = setTimeout(refresh, 80);
    }),
  );
};

const createPreviewServer = ({ rootDir, watch = true }) => {
  writeCardStyles(rootDir);
  const clients = new Set();
  const notify = () =>
    clients.forEach((client) => client.write(`event: reload\ndata: ${Date.now()}\n\n`));
  const watchers = watch ? createWatchers(rootDir, notify) : [];
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname === "/") return send(res, 200, "text/html", renderAppShell());
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
    if (url.pathname.startsWith("/media/") || url.pathname.startsWith("/_")) {
      if (serveMedia(rootDir, decodeURIComponent(url.pathname), res)) return;
    }
    send(res, 404, "text/plain", "Not found");
  });
  server.on("close", () => {
    watchers.forEach((watcher) => watcher.close());
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
