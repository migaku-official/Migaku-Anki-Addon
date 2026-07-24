const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");

const {
  checkCardStyles,
  compileCardStyles,
  writeCardStyles,
} = require("../tools/card-styles");

const sandbox = fs.mkdtempSync(path.join(os.tmpdir(), "migaku-card-styles-"));
const cardStylesDir = path.join(sandbox, "src", "card-styles");
const languageCardDir = path.join(sandbox, "src", "languages", "en", "card");

fs.mkdirSync(cardStylesDir, { recursive: true });
fs.mkdirSync(languageCardDir, { recursive: true });
fs.writeFileSync(
  path.join(cardStylesDir, "global.css"),
  [
    ".migaku-card-front .migaku-card-unknown {",
    "  color: var(--card-color);",
    "}",
    "",
    "t {",
    "  font-style: bold;",
    "}",
    "",
    "@media only screen and (max-width: 450px) {",
    "  /* For mobile phones: */",
    "  .migaku-card {",
    "    width: 100%;",
    "  }",
    "}",
    "",
  ].join("\n"),
);
fs.writeFileSync(
  path.join(cardStylesDir, "legacy-variants.json"),
  `${JSON.stringify({ en: { alternateSentence: true, mobileCommentGap: true, textStyle: "bold" } }, null, 2)}\n`,
);
fs.writeFileSync(
  path.join(languageCardDir, "fonts.css"),
  "@font-face {\n  font-family: cardFont;\n  src: url('/font.ttf');\n}\n",
);
fs.writeFileSync(path.join(languageCardDir, "styles.css"), "stale\n");

const expected = [
  "@font-face {",
  "  font-family: cardFont;",
  "  src: url('/font.ttf');",
  "}",
  "",
  ".migaku-card-sentence-alternate {",
  "  text-align: center;",
  "  width: 100%;",
  "  font-size: 20px;",
  "  margin-top: 10px;",
  "  color: rgb(180, 180, 180);",
  "}",
  "",
  ".migaku-card-front .migaku-card-unknown {",
  "  color: var(--card-color);",
  "}",
  "",
  "t {",
  "  font-weight: bold;",
  "}",
  "",
  "@media only screen and (max-width: 450px) {",
  "  /* For mobile phones: */",
  "",
  "  .migaku-card {",
  "    width: 100%;",
  "  }",
  "}",
  "",
].join("\n");

assert.strictEqual(compileCardStyles(sandbox, "en"), expected);
assert.deepStrictEqual(checkCardStyles(sandbox), {
  languages: ["en"],
  stale: ["en"],
});
assert.deepStrictEqual(writeCardStyles(sandbox), {
  languages: ["en"],
  written: ["en"],
});
assert.strictEqual(fs.readFileSync(path.join(languageCardDir, "styles.css"), "utf8"), expected);
assert.deepStrictEqual(checkCardStyles(sandbox), {
  languages: ["en"],
  stale: [],
});

fs.writeFileSync(path.join(cardStylesDir, "global.css"), ".redesign {\n  color: blue;\n}\n");
assert.strictEqual(
  compileCardStyles(sandbox, "en"),
  "@font-face {\n  font-family: cardFont;\n  src: url('/font.ttf');\n}\n\n.redesign {\n  color: blue;\n}\n",
);

fs.writeFileSync(
  path.join(cardStylesDir, "legacy-variants.json"),
  `${JSON.stringify({ en: { textStyle: "typo" } }, null, 2)}\n`,
);
assert.throws(() => compileCardStyles(sandbox, "en"), /Unknown text style variant/);
fs.writeFileSync(path.join(cardStylesDir, "legacy-variants.json"), "{}\n");

const missingFontsDir = path.join(sandbox, "src", "languages", "fr", "card");
fs.mkdirSync(missingFontsDir, { recursive: true });
fs.writeFileSync(path.join(missingFontsDir, "styles.css"), "stale\n");
assert.throws(() => checkCardStyles(sandbox), /fonts\.css/);

fs.rmSync(sandbox, { force: true, recursive: true });

console.log("✓ card styles compile from global and language sources");
