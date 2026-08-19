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
  const stopAudio = () => {
    audio.pause();
    audio.currentTime = 0;
    button.blur();
  };
  button.addEventListener("click", () => {
    if (!audio.paused) return stopAudio();
    audio.currentTime = 0;
    audio.play();
  });
});
</script>`;

const previewEmptyFrontStyles = `
[data-preview-empty-front] {
  position: absolute;
  z-index: 1;
  top: 50%;
  left: 50%;
  display: grid;
  gap: 8px;
  width: min(calc(100% - 64px), 420px);
  padding: 20px;
  transform: translate(-50%, -50%);
  color: inherit;
  text-align: center;
  pointer-events: none;
}
[data-preview-empty-front] strong {
  font-size: 1.25rem;
  line-height: 1.2;
}
[data-preview-empty-front] span {
  font-size: .875rem;
  line-height: 1.4;
  opacity: .65;
}`;

const getFrontField = (fields) => {
  if (fields["Is Audio Card"])
    return fields["Is Vocabulary Card"] ? "Word Audio" : "Sentence Audio";
  return fields["Is Vocabulary Card"] ? "Target Word" : "Sentence";
};

const renderEmptyFrontNotice = (side, fields) => {
  if (side !== "front") return "";
  const frontField = getFrontField(fields);
  if (fields[frontField]) return "";
  return `<div data-preview-empty-front role="status"><strong>Front of card is blank</strong><span>The ${frontField} field is empty.</span></div>`;
};

const assertOption = (options, value, optionName) => {
  if (!options.includes(value))
    throw new Error(`Unknown ${optionName} "${value}". Expected one of: ${options.join(", ")}`);
};

const renderCardDocument = ({
  audioCard = false,
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
  const fixture = buildLocalizedFixture(language, fixtureName, audioCard);
  if (enabledFields) {
    const enabledFieldSet = new Set(enabledFields);
    const fallbackFields = buildFieldFallbacks(language);
    standardFields.filter((field) => field !== "Is Audio Card").forEach((field) => {
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
  const emptyFrontNotice = renderEmptyFrontNotice(side, fixture.fields);
  const styles = readCardFile(rootDir, language, "styles.css");
  const supportStyles = readCardFile(rootDir, language, "support.css");
  const supportScript = readCardFile(rootDir, language, "support.html");

  return `<!doctype html>
<html lang="${language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script>const pycmd = () => {};</script>
  <style>${styles}\n${supportStyles}\n${previewEmptyFrontStyles}</style>
</head>
<body class="${themes[theme]}" data-preview-audio="${audioCard ? "audio" : "text"}" data-preview-fixture="${fixtureName}" data-preview-side="${side}" data-preview-theme="${theme}">
  <main class="container">
    <div id="qa">
      <div id="content">${card}${emptyFrontNotice}</div>
    </div>
  </main>
  ${supportScript}
  ${previewAudioScript}
</body>
</html>`;
};

module.exports = { renderCardDocument };
