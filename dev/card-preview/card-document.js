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
  display: grid;
  gap: 8px;
  width: min(100%, 420px);
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
  text-wrap: balance;
}`;

const getFrontField = (fields) => {
  if (fields["Is Audio Card"])
    return fields["Is Vocabulary Card"] ? "Word Audio" : "Sentence Audio";
  return fields["Is Vocabulary Card"] ? "Target Word" : "Sentence";
};
const getFrontCardType = (fields) =>
  `${fields["Is Vocabulary Card"] ? "Vocab" : "Sentence"}${fields["Is Audio Card"] ? " Audio" : ""}`;

const renderEmptyFrontNotice = (side, fields) => {
  if (side !== "front") return "";
  const frontField = getFrontField(fields);
  if (fields[frontField]) return "";
  return `<div data-preview-empty-front role="status"><strong>Front of card is blank</strong><span>This is a ${getFrontCardType(fields)} card, but the ${frontField} field is empty.</span></div>`;
};
const injectEmptyFrontNotice = (card, notice) => {
  if (!notice) return card;
  const frontContentMarker = '<div class="migaku-card-content">';
  if (!card.includes(frontContentMarker))
    throw new Error("Cannot render the empty-front diagnostic without the front content container.");
  return card.replace(
    frontContentMarker,
    `${frontContentMarker}\n        ${notice}`,
  );
};

const assertOption = (options, value, optionName) => {
  if (!options.includes(value))
    throw new Error(`Unknown ${optionName} "${value}". Expected one of: ${options.join(", ")}`);
};

const assertAudioCount = (count, fieldName) => {
  if (!Number.isSafeInteger(count) || count < 0)
    throw new Error(`${fieldName} count must be a non-negative integer.`);
};

const repeatAudio = (value, count) => value ? Array.from({ length: count }, () => value).join("<br>") : "";

const renderCardDocument = ({
  audioCard = false,
  commandBridge = true,
  enabledFields,
  fixtureName,
  language,
  rootDir,
  sentenceAudioCount = 1,
  side,
  theme,
  wordAudioCount = 1,
}) => {
  assertOption(contract.languages, language, "language");
  assertOption(["front", "back"], side, "side");
  assertOption(Object.keys(themes), theme, "theme");
  assertAudioCount(sentenceAudioCount, "Sentence audio");
  assertAudioCount(wordAudioCount, "Word audio");
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
  fixture.fields["Sentence Audio"] = repeatAudio(fixture.fields["Sentence Audio"], sentenceAudioCount);
  fixture.fields["Word Audio"] = repeatAudio(fixture.fields["Word Audio"], wordAudioCount);
  const frontTemplate = readCardFile(rootDir, language, "front.html");
  const frontSide = renderTemplate(frontTemplate, fixture.fields);
  const fields = { ...fixture.fields, FrontSide: frontSide };
  const template = readCardFile(rootDir, language, `${side}.html`);
  const card = renderPreviewAudio(renderTemplate(template, fields));
  const emptyFrontNotice = renderEmptyFrontNotice(side, fixture.fields);
  const cardWithEmptyFrontNotice = injectEmptyFrontNotice(card, emptyFrontNotice);
  const styles = readCardFile(rootDir, language, "styles.css");
  const supportStyles = readCardFile(rootDir, language, "support.css");
  const supportScript = readCardFile(rootDir, language, "support.html");

  return `<!doctype html>
<html lang="${language}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  ${commandBridge ? "<script>const pycmd = () => {};</script>" : ""}
  <style>${styles}\n${supportStyles}\n${previewEmptyFrontStyles}</style>
</head>
<body class="${themes[theme]}" data-preview-audio="${audioCard ? "audio" : "text"}" data-preview-fixture="${fixtureName}" data-preview-side="${side}" data-preview-theme="${theme}">
  <main class="container">
    <div id="qa">
      <div id="content">${cardWithEmptyFrontNotice}</div>
    </div>
  </main>
  ${supportScript}
  ${previewAudioScript}
</body>
</html>`;
};

module.exports = { renderCardDocument };
