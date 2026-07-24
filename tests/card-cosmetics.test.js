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
  /main\.container\s*\{[^}]*padding: 80px 16px 200px;[^}]*background: #ede3ff;/s,
);
assert.match(light, /\.card\s*\{[^}]*color: rgb\(0, 0, 90\);/s);
assert.match(
  light,
  /\.migaku-card-examples\s*\{[^}]*color: inherit;/s,
);
assert.match(
  light,
  /\.migaku-card,\s*\.migaku-typeselect\s*\{[^}]*width: 100%;[^}]*max-width: 760px;[^}]*background: #fff;[^}]*border-radius: 24px;/s,
);
assert.match(
  light,
  /\.migaku-card,\s*\.migaku-typeselect,\s*\.UiButton\s*\{[^}]*box-shadow: 0 9px 20px rgba\(0 0 90 \/ 14%\), 0 3\.76px 8\.3555px rgba\(0 0 90 \/ 8\.3%\), 0 2\.0103px 4\.4673px rgba\(0 0 90 \/ 5%\), 0 1\.1269px 2\.5043px rgba\(0 0 90 \/ 2\.6%\), 0 \.5985px 1\.33px rgba\(0 0 90 \/ \.8%\);/s,
);
assert.match(
  light,
  /#content\s*\{[^}]*display: flex;[^}]*flex-direction: column;[^}]*height: 100%;/s,
);
assert.match(light, /main\.container \.migaku-card\s*\{[^}]*flex: 1;/s);
assert.match(
  light,
  /main\.container \.migaku-card-shell\s*\{[^}]*position: relative;[^}]*flex: 1;[^}]*max-width: 760px;/s,
);
assert.match(light, /\.migaku-card\s*\{[^}]*padding: 24px 16px 8px;/s);
assert.match(light, /\.migaku-card-front \.migaku-card-content\s*\{[^}]*font-size: 32px;/s);
assert.match(light, /\.migaku-card-front \.migaku-card-content\s*\{[^}]*gap: 8px;/s);
assert.match(light, /\.migaku-card-front \.migaku-card-unknown\s*\{[^}]*font-size: 46px;/s);
assert.match(light, /\.migaku-card-front \.migaku-card-sentence\s*\{[^}]*font-size: 32px;/s);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-unknown\s*\{[^}]*order: 1;[^}]*font-size: 46px;[^}]*text-align: center;[^}]*width: 100%;[^}]*margin: 0 0 8px;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-sentence\s*\{[^}]*order: 2;[^}]*font-size: 32px;[^}]*text-align: center;[^}]*width: 100%;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-audio-row\s*\{[^}]*order: 4;[^}]*display: flex;[^}]*width: 100%;/s,
);
assert.match(
  light,
  /\.UiButton\s*\{[^}]*appearance: none;[^}]*display: inline-flex;[^}]*min-height: 34px;[^}]*padding: 8px 16px;[^}]*border-radius: 20px;/s,
);
assert.match(
  light,
  /\.migaku-card-screenshot img,\s*\.migaku-card-images img\s*\{[^}]*max-width: min\(100%, 450px\);[^}]*border-radius: 16px;/s,
);
assert.match(light, /\.migaku-translation-toggle\s*\{[^}]*order: 5;[^}]*background: #fff;/s);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-translation\s*\{[^}]*order: 6;[^}]*font-size: 0\.875rem;[^}]*color: rgba\(0 0 90 \/ 60%\);/s,
);
assert.match(
  light,
  /\.sentence-separator\s*\{[^}]*order: 7;[^}]*margin: 8px 0;[^}]*border-color: rgba\(0 0 90 \/ 15%\);/s,
);
assert.match(light, /\.migaku-card-back \.migaku-card-definitions\s*\{[^}]*order: 8;[^}]*width: 100%;/s);
assert.match(light, /\.migaku-card-back \.migaku-card-images\s*\{[^}]*order: 11;[^}]*width: 100%;/s);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-type-toggle\s*\{[^}]*position: absolute;[^}]*top: calc\(100% \+ 4px\);[^}]*color: rgba\(0 0 90 \/ 60%\);[^}]*background: transparent;[^}]*font-weight: 400;[^}]*opacity: \.5;/s,
);
assert.match(light, /main\.container \.migaku-card-shell\s*\{[^}]*margin: 0 auto 16px;/s);
assert.match(light, /main\.container\s*\{[^}]*padding: 80px 16px 200px;/s);
assert.match(light, /main\.container #qa\s*\{[^}]*height: 100%;/s);
assert.match(
  light,
  /main\.container \.migaku-card-shell:has\(> \.migaku-type-toggle\)\s*\{[^}]*margin-bottom: 96px;/s,
);
assert.match(light, /#content\s*\{[^}]*height: 100%;/s);
assert.match(light, /\.migaku-type-toggle:hover\s*\{[^}]*opacity: 1;[^}]*text-decoration: underline;/s);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-typeselect\s*\{[^}]*top: calc\(100% \+ 38px\);/s,
);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-typeselect\s*\{[^}]*text-align: left;/s,
);
assert.match(
  light,
  /\.migaku-typeselect form\s*\{[^}]*display: grid;[^}]*grid-template-columns: auto auto;[^}]*justify-content: flex-start;[^}]*column-gap: 24px;/s,
);
assert.match(
  light,
  /\.migaku-typeselect form::before\s*\{[^}]*content: "Card type";[^}]*font-size: 1rem;[^}]*text-align: left;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control\s*\{[^}]*display: flex;[^}]*align-items: center;[^}]*gap: 8px;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control span\s*\{[^}]*display: flex;[^}]*align-items: center;[^}]*font-size: \.875rem;/s,
);
assert.match(light, /\.migaku-audio-card-control\s*\{[^}]*display: grid;[^}]*justify-items: start;/s);
assert.match(
  light,
  /\.migaku-typeselect input\[type="checkbox"\]\s*\{[^}]*appearance: none;[^}]*width: 44px;[^}]*height: 24px;[^}]*border-radius: 999px;/s,
);
assert.match(
  light,
  /\.migaku-typeselect input\[type="checkbox"\]:checked::before\s*\{[^}]*transform: translateX\(20px\);/s,
);
assert.match(
  light,
  /@media only screen and \(max-width: 520px\)\s*\{[^}]*\.migaku-typeselect form\s*\{[^}]*grid-template-columns: 1fr;/s,
);
assert.doesNotMatch(light, /\.migaku-typeselect\s*\{[^}]*border-radius: 10px;/s);
assert.match(light, /\.dict-form\s*\{[^}]*white-space: nowrap;[^}]*word-break: normal;/s);
assert.match(
  light,
  /box-shadow: 0 9px 20px rgba\(0 0 90 \/ 14%\), 0 3\.76px 8\.3555px rgba\(0 0 90 \/ 8\.3%\), 0 2\.0103px 4\.4673px rgba\(0 0 90 \/ 5%\), 0 1\.1269px 2\.5043px rgba\(0 0 90 \/ 2\.6%\), 0 \.5985px 1\.33px rgba\(0 0 90 \/ \.8%\);/,
);

assert.match(dark, /\.nightMode\.card\s*\{[^}]*color: #fff;/s);
assert.match(dark, /\.nightMode main\.container\s*\{[^}]*background: #0a002a;/s);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-translation-toggle,\s*\.nightMode \.migaku-translation-toggle\s*\{[^}]*background: #2b2b60;/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect,\s*\.ankidroid_dark_mode \.UiButton,\s*\.nightMode \.UiButton\s*\{[^}]*box-shadow: 0 9px 20px rgb\(0 0 0 \/ 18%\), 0 3\.76px 8\.3556px rgb\(0 0 0 \/ 14\.4%\), 0 2\.0103px 4\.4673px rgb\(0 0 0 \/ 8\.11%\), 0 1\.127px 2\.5043px rgb\(0 0 0 \/ 3\.63%\), 0 \.5985px 1\.33px rgb\(0 0 0 \/ 2\.8%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card-translation,\s*\.nightMode \.migaku-card-translation,\s*\.ankidroid_dark_mode \.migaku-type-toggle,\s*\.nightMode \.migaku-type-toggle\s*\{[^}]*color: rgba\(255 255 255 \/ 60%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-typeselect input\[type="checkbox"\],\s*\.nightMode \.migaku-typeselect input\[type="checkbox"\]\s*\{[^}]*background: rgba\(255 255 255 \/ 19%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.sentence-separator,\s*\.nightMode \.sentence-separator\s*\{[^}]*border-color: rgba\(255 255 255 \/ 19%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect\s*\{[^}]*background: #202047;/s,
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
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect\s*\{[^}]*background: #202047;/s,
);

console.log("✓ card cosmetic contract");
