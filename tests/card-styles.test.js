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
  ".card {\n  color: var(--card-color);\n}\n",
);
fs.writeFileSync(
  path.join(languageCardDir, "fonts.css"),
  "@font-face {\n  font-family: cardFont;\n  src: url('/font.ttf');\n}\n",
);
fs.writeFileSync(path.join(languageCardDir, "styles.css"), "stale\n");

const expected =
  "@font-face {\n  font-family: cardFont;\n  src: url('/font.ttf');\n}\n\n.card {\n  color: var(--card-color);\n}\n";

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

fs.rmSync(sandbox, { force: true, recursive: true });

console.log("✓ card styles compile from global and language sources");
