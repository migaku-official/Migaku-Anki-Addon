const fs = require("fs");
const path = require("path");

const contract = require("./template-contract.json");
const {
  buildFieldFallbacks,
  buildLocalizedFixture,
  standardFields,
} = require("./fixtures");
const { renderTemplate } = require("./template-engine");

const themes = {
  ankidroid: "card ankidroid_dark_mode",
  dark: "card nightMode",
  light: "card",
};

const readCardFile = (rootDir, language, fileName) =>
  fs.readFileSync(
    path.join(rootDir, "src", "languages", language, "card", fileName),
    "utf8",
  );

const renderPreviewAudio = (html) =>
  html.replace(
    /\[sound:([^\]]+)]/g,
    (_, fileName) =>
      `<button type="button" class="replay-button soundLink" data-preview-audio-button aria-label="Play audio"></button><audio hidden preload="none" src="/fixture-media/${encodeURIComponent(fileName)}"></audio>`,
  );

const previewAudioScript = `<script>
document.querySelectorAll("[data-preview-audio-button]").forEach((button) => {
  const audio = button.nextElementSibling;
  button.addEventListener("click", () => {
    audio.currentTime = 0;
    audio.play();
  });
});
</script>`;

const assertOption = (options, value, optionName) => {
  if (!options.includes(value))
    throw new Error(`Unknown ${optionName} "${value}". Expected one of: ${options.join(", ")}`);
};

const renderCardDocument = ({
  enabledFields,
  fixtureName,
  language,
  rootDir,
  side,
  theme,
}) => {
  assertOption(contract.languages, language, "language");
  assertOption(["front", "back"], side, "side");
  assertOption(Object.keys(themes), theme, "theme");
  const fixture = buildLocalizedFixture(language, fixtureName);
  if (enabledFields) {
    const enabledFieldSet = new Set(enabledFields);
    const fallbackFields = buildFieldFallbacks(language);
    standardFields.forEach((field) => {
      fixture.fields[field] = enabledFieldSet.has(field)
        ? fixture.fields[field] || fallbackFields[field]
        : "";
    });
  }
  const frontTemplate = readCardFile(rootDir, language, "front.html");
  const frontSide = renderTemplate(frontTemplate, fixture.fields);
  const fields = { ...fixture.fields, FrontSide: frontSide };
  const template = readCardFile(rootDir, language, `${side}.html`);
  const card = renderPreviewAudio(renderTemplate(template, fields));
  const styles = readCardFile(rootDir, language, "styles.css");
  const supportStyles = readCardFile(rootDir, language, "support.css");
  const supportScript = readCardFile(rootDir, language, "support.html");

  return `<!doctype html>
<html lang="${language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script>const pycmd = () => {};</script>
  <style>${styles}\n${supportStyles}</style>
</head>
<body class="${themes[theme]}" data-preview-fixture="${fixtureName}" data-preview-side="${side}" data-preview-theme="${theme}">
  <main class="container">
    <div id="qa">
      <div id="content">${card}</div>
    </div>
  </main>
  ${supportScript}
  ${previewAudioScript}
</body>
</html>`;
};

module.exports = { renderCardDocument };
