const fs = require("fs");
const path = require("path");

const alternateSentenceStyles = [
  ".migaku-card-sentence-alternate {",
  "  text-align: center;",
  "  width: 100%;",
  "  font-size: 20px;",
  "  margin-top: 10px;",
  "  color: rgb(180, 180, 180);",
  "}",
  "",
].join("\n");
const canonicalTextStyles = "t {\n  font-style: bold;\n}";
const textStyleVariants = {
  bold: "t {\n  font-weight: bold;\n}",
  heavyItalic: "t {\n  font-weight: 900;\n  font-style: italic;\n}",
};

const getCardStylePaths = (rootDir, language) => ({
  card: path.join(rootDir, "src", "languages", language, "card"),
  fonts: path.join(rootDir, "src", "languages", language, "card", "fonts.css"),
  global: path.join(rootDir, "src", "card-styles", "global.css"),
  legacyVariants: path.join(rootDir, "src", "card-styles", "legacy-variants.json"),
  output: path.join(rootDir, "src", "languages", language, "card", "styles.css"),
});

const getCardStyleLanguages = (rootDir) => {
  const languagesDir = path.join(rootDir, "src", "languages");
  return fs
    .readdirSync(languagesDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((language) => fs.existsSync(getCardStylePaths(rootDir, language).card))
    .sort();
};

const readStyleSource = (filePath) =>
  fs.readFileSync(filePath, "utf8").replace(/\r\n/g, "\n").trim();

const replaceLegacyFragment = (source, search, replacement) =>
  source.includes(search) ? source.replace(search, replacement) : source;

const getTextStyleVariant = (name) => {
  if (!Object.hasOwn(textStyleVariants, name)) throw new Error(`Unknown text style variant: ${name}`);
  return textStyleVariants[name];
};

const getLegacyVariant = (paths, language) =>
  fs.existsSync(paths.legacyVariants)
    ? JSON.parse(fs.readFileSync(paths.legacyVariants, "utf8"))[language] || {}
    : {};

const applyLegacyVariant = (source, variant) => {
  const withAlternateSentence = variant.alternateSentence
    ? replaceLegacyFragment(
        source,
        ".migaku-card-unknown {",
        `${alternateSentenceStyles}\n.migaku-card-unknown {`,
      )
    : source;
  const withTextStyle = variant.textStyle
    ? replaceLegacyFragment(
        withAlternateSentence,
        canonicalTextStyles,
        getTextStyleVariant(variant.textStyle),
      )
    : withAlternateSentence;
  return variant.mobileCommentGap
    ? replaceLegacyFragment(
        withTextStyle,
        "  /* For mobile phones: */\n",
        "  /* For mobile phones: */\n\n",
      )
    : withTextStyle;
};

const compileCardStyles = (rootDir, language) => {
  const paths = getCardStylePaths(rootDir, language);
  const globalStyles = applyLegacyVariant(readStyleSource(paths.global), getLegacyVariant(paths, language));
  return `${readStyleSource(paths.fonts)}\n\n${globalStyles}\n`;
};

const inspectCardStyles = (rootDir) => {
  const languages = getCardStyleLanguages(rootDir);
  const compiled = Object.fromEntries(
    languages.map((language) => [language, compileCardStyles(rootDir, language)]),
  );
  const stale = languages.filter((language) => {
    const paths = getCardStylePaths(rootDir, language);
    const actual = fs.existsSync(paths.output) ? fs.readFileSync(paths.output, "utf8") : "";
    return actual !== compiled[language];
  });
  return { compiled, languages, stale };
};

const checkCardStyles = (rootDir) => {
  const { languages, stale } = inspectCardStyles(rootDir);
  return { languages, stale };
};

const writeCardStyles = (rootDir) => {
  const { compiled, languages, stale } = inspectCardStyles(rootDir);
  stale.forEach((language) => {
    const paths = getCardStylePaths(rootDir, language);
    fs.writeFileSync(paths.output, compiled[language]);
  });
  return { languages, written: stale };
};

const run = () => {
  const rootDir = path.resolve(__dirname, "..");
  const checkOnly = process.argv.includes("--check");
  const result = checkOnly ? checkCardStyles(rootDir) : writeCardStyles(rootDir);
  const changed = checkOnly ? result.stale : result.written;
  if (checkOnly && changed.length > 0) {
    console.error(`Generated card styles are stale: ${changed.join(", ")}`);
    process.exitCode = 1;
    return;
  }
  console.log(
    checkOnly
      ? `✓ ${result.languages.length} generated card styles are current`
      : `✓ generated card styles (${changed.length} written)`,
  );
};

if (require.main === module) run();

module.exports = {
  checkCardStyles,
  compileCardStyles,
  getCardStyleLanguages,
  writeCardStyles,
};
