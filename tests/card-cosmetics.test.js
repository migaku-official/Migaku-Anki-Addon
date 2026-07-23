const assert = require("assert");
const path = require("path");

const { renderCardDocument } = require("../dev/card-preview/card-document");

const rootDir = path.resolve(__dirname, "..");
const light = renderCardDocument({
  fixtureName: "syntax",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const dark = renderCardDocument({
  fixtureName: "syntax",
  language: "en",
  rootDir,
  side: "back",
  theme: "dark",
});
const ankidroid = renderCardDocument({
  fixtureName: "syntax",
  language: "en",
  rootDir,
  side: "back",
  theme: "ankidroid",
});

assert.match(light, /\.migaku-header\s*\{\s*display: none;/);
assert.match(
  light,
  /main\.container\s*\{[^}]*padding: 80px 16px 120px;[^}]*background: #ede3ff;/s,
);
assert.match(light, /\.card\s*\{[^}]*color: rgb\(0, 0, 90\);/s);
assert.match(
  light,
  /\.migaku-card-translation,\s*\.migaku-card-examples\s*\{[^}]*color: inherit;/s,
);
assert.match(
  light,
  /\.migaku-card,\s*\.migaku-typeselect\s*\{[^}]*width: 100%;[^}]*max-width: 760px;[^}]*background: #fff;[^}]*border-radius: 24px;[^}]*box-shadow: 0 9px 20px rgba\(0 0 90 \/ 14%\)/s,
);
assert.match(
  light,
  /#content\s*\{[^}]*display: flex;[^}]*flex-direction: column;[^}]*height: calc\(100vh - 200px\);/s,
);
assert.match(light, /main\.container \.migaku-card\s*\{[^}]*flex: 1;/s);
assert.match(light, /\.migaku-card\s*\{[^}]*padding: 24px 16px 8px;/s);
assert.match(light, /\.migaku-card-front \.migaku-card-content\s*\{[^}]*font-size: 32px;/s);
assert.match(light, /\.migaku-card-unknown\s*\{[^}]*font-size: 46px;/s);
assert.match(light, /\.migaku-card-sentence\s*\{[^}]*font-size: 32px;/s);
assert.match(light, /\.dict-form\s*\{[^}]*white-space: nowrap;[^}]*word-break: normal;/s);
assert.match(
  light,
  /box-shadow: 0 9px 20px rgba\(0 0 90 \/ 14%\), 0 3\.76px 8\.3555px rgba\(0 0 90 \/ 8\.3%\), 0 2\.0103px 4\.4673px rgba\(0 0 90 \/ 5%\), 0 1\.1269px 2\.5043px rgba\(0 0 90 \/ 2\.6%\), 0 \.5985px 1\.33px rgba\(0 0 90 \/ \.8%\);/,
);

assert.match(dark, /\.nightMode\.card\s*\{[^}]*color: #fff;/s);
assert.match(dark, /\.nightMode main\.container\s*\{[^}]*background: #0a002a;/s);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect\s*\{[^}]*background: #202047;[^}]*box-shadow: 0 9px 20px rgb\(0 0 0 \/ 18%\), 0 3\.76px 8\.3556px rgb\(0 0 0 \/ 14\.4%\), 0 2\.0103px 4\.4673px rgb\(0 0 0 \/ 8\.11%\), 0 1\.127px 2\.5043px rgb\(0 0 0 \/ 3\.63%\), 0 \.5985px 1\.33px rgb\(0 0 0 \/ 2\.8%\);/s,
);

assert.match(ankidroid, /class="card ankidroid_dark_mode"/);
assert.match(
  ankidroid,
  /\.ankidroid_dark_mode\.card,\s*\.nightMode\.card\s*\{[^}]*color: #fff;/s,
);
assert.match(
  ankidroid,
  /\.ankidroid_dark_mode main\.container,\s*\.nightMode main\.container\s*\{[^}]*background: #0a002a;/s,
);
assert.match(
  ankidroid,
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect\s*\{[^}]*background: #202047;[^}]*box-shadow: 0 9px 20px rgb\(0 0 0 \/ 18%\)/s,
);

console.log("✓ card cosmetic contract");
