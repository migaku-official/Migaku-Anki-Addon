const fs = require("fs");
const path = require("path");

const contract = require("./template-contract.json");
const { fixtures } = require("./fixtures");
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

const assertOption = (options, value, optionName) => {
  if (!options.includes(value))
    throw new Error(`Unknown ${optionName} "${value}". Expected one of: ${options.join(", ")}`);
};

const renderCardDocument = ({
  fixtureName,
  language,
  rootDir,
  side,
  theme,
}) => {
  assertOption(contract.languages, language, "language");
  assertOption(["front", "back"], side, "side");
  assertOption(Object.keys(themes), theme, "theme");
  assertOption(Object.keys(fixtures), fixtureName, "fixture");

  const fixture = fixtures[fixtureName];
  const frontTemplate = readCardFile(rootDir, language, "front.html");
  const frontSide = renderTemplate(frontTemplate, fixture.fields);
  const fields = { ...fixture.fields, FrontSide: frontSide };
  const template = readCardFile(rootDir, language, `${side}.html`);
  const card = renderTemplate(template, fields);
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
</body>
</html>`;
};

module.exports = { renderCardDocument };
