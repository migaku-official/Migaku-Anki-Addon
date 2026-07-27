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
  /\.migaku-card-back\s*\{[^}]*flex-flow: row wrap;[^}]*justify-content: center;[^}]*column-gap: 16px;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-content\s*\{[^}]*display: contents;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-content > :not\(\.migaku-card-images\)\s*\{[^}]*max-width: calc\(100% - 30px\);/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-content::before,\s*\.migaku-card-back \.migaku-card-content::after\s*\{[^}]*content: "";[^}]*flex: 0 0 100%;[^}]*height: 15px;/s,
);
assert.match(light, /\.migaku-card-back \.migaku-card-content::before\s*\{[^}]*order: 0;/s);
assert.match(light, /\.migaku-card-back \.migaku-card-content::after\s*\{[^}]*order: 13;/s);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-screenshot,\s*\.migaku-card-back \.migaku-card-images\s*\{[^}]*display: contents;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-screenshot img\s*\{[^}]*order: 11;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-images img\s*\{[^}]*order: 12;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-screenshot img,\s*\.migaku-card-back \.migaku-card-images img\s*\{[^}]*flex: 1 1 300px;[^}]*width: 100%;[^}]*max-width: 450px;[^}]*margin-top: 16px;[^}]*border-radius: 16px;/s,
);
assert.match(
  light,
  /\.migaku-translation-toggle,\s*\.migaku-card-back \.migaku-card-translation\s*\{[^}]*order: 5;[^}]*height: 34px;[^}]*min-height: 34px;[^}]*margin: 16px auto;[^}]*padding: 8px 16px;[^}]*font-size: \.875rem;[^}]*line-height: 1\.25;/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-translation\s*\{[^}]*display: flex;[^}]*align-items: center;[^}]*justify-content: center;[^}]*overflow-y: auto;[^}]*color: rgba\(0 0 90 \/ 60%\);/s,
);
assert.match(
  light,
  /\.migaku-card-back \.migaku-card-translation\[hidden\]\s*\{[^}]*display: none;/s,
);
assert.match(
  light,
  /\.sentence-separator\s*\{[^}]*order: 7;[^}]*margin: 8px 0;[^}]*border-color: rgba\(0 0 90 \/ 15%\);/s,
);
assert.match(light, /\.migaku-card-back \.migaku-card-definitions\s*\{[^}]*order: 8;[^}]*width: 100%;/s);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-type-toggle\s*\{[^}]*position: static;[^}]*align-self: center;[^}]*margin: 4px auto 0;[^}]*transform: none;[^}]*color: rgba\(0 0 90 \/ 60%\);[^}]*background: transparent;[^}]*box-shadow: none;[^}]*font-size: 0;[^}]*font-weight: 400;[^}]*opacity: \.5;/s,
);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-type-toggle::after\s*\{[^}]*content: "Customize front of card";[^}]*font-size: 1rem;/s,
);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-type-toggle\[aria-expanded="true"\]::after\s*\{[^}]*content: "Dismiss";/s,
);
assert.match(light, /main\.container \.migaku-card-shell\s*\{[^}]*margin: 0 auto 16px;/s);
assert.match(light, /main\.container\s*\{[^}]*padding: 80px 16px 120px;/s);
assert.match(light, /main\.container #qa\s*\{[^}]*height: 100%;/s);
assert.match(
  light,
  /main\.container \.migaku-card-shell:has\(> \.migaku-type-toggle\)\s*\{[^}]*padding-bottom: 64px;/s,
);
assert.match(light, /#content\s*\{[^}]*height: 100%;/s);
assert.match(light, /\.migaku-type-toggle:hover\s*\{[^}]*opacity: 1;[^}]*text-decoration: underline;/s);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-typeselect\s*\{[^}]*position: static;[^}]*margin: 8px auto 0;[^}]*transform: none;/s,
);
assert.match(
  light,
  /\.migaku-card-shell > \.migaku-typeselect\s*\{[^}]*text-align: left;/s,
);
assert.match(
  light,
  /\.migaku-typeselect form\s*\{[^}]*display: grid;[^}]*"section-subtitle section-subtitle"[^}]*grid-template-columns: auto auto;[^}]*justify-content: flex-start;[^}]*column-gap: 40px;/s,
);
assert.match(
  light,
  /\.migaku-typeselect form::before\s*\{[^}]*grid-area: section-title;[^}]*content: "Customize front of card";[^}]*font-size: 1\.25rem;[^}]*font-weight: 700;[^}]*text-align: left;/s,
);
assert.match(
  light,
  /\.migaku-typeselect form::after\s*\{[^}]*grid-area: section-subtitle;[^}]*content: 'These toggles control the "Is Vocab Card" and "Is Audio Card" fields\. Those values determine what is shown on the front of the card when you are reviewing';[^}]*color: rgba\(0 0 90 \/ 60%\);[^}]*font-size: \.875rem;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control\s*\{[^}]*grid-area: card-mode;[^}]*display: grid;[^}]*grid-template-areas:[^}]*"title title title"[^}]*"sentence toggle vocab";[^}]*align-items: center;[^}]*justify-items: start;[^}]*column-gap: 8px;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control::before\s*\{[^}]*grid-area: title;[^}]*content: "Which field is on the front:";[^}]*font-size: 1rem;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control span\s*\{[^}]*display: flex;[^}]*align-items: center;[^}]*width: 76px;[^}]*color: rgba\(0 0 90 \/ 60%\);[^}]*font-size: \.875rem;[^}]*font-weight: 400;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control span::before\s*\{[^}]*content: "✓";[^}]*width: 16px;[^}]*opacity: 0;/s,
);
assert.match(light, /\.migaku-card-mode-control span:first-child::before\s*\{[^}]*opacity: 1;/s);
assert.match(
  light,
  /\.migaku-card-mode-control:has\(input:checked\) span:first-child::before\s*\{[^}]*opacity: 0;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control input:checked ~ span::before\s*\{[^}]*opacity: 1;/s,
);
assert.match(light, /\.migaku-card-mode-control span:first-child\s*\{[^}]*font-weight: 700;/s);
assert.match(
  light,
  /\.migaku-card-mode-control:has\(input:checked\) span:first-child\s*\{[^}]*font-weight: 400;/s,
);
assert.match(
  light,
  /\.migaku-card-mode-control input:checked ~ span\s*\{[^}]*font-weight: 700;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control\s*\{[^}]*--migaku-selected-tick: url\("data:image\/svg\+xml,[^"]+"\);[^}]*display: grid;[^}]*grid-template-areas:[^}]*"title title title"[^}]*"text toggle audio";[^}]*align-items: center;[^}]*justify-items: start;[^}]*column-gap: 8px;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control > span::after\s*\{[^}]*content: "Text or audio on the front:";[^}]*font-size: 1rem;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control::before,\s*\.migaku-audio-card-control::after\s*\{[^}]*width: 64px;[^}]*padding-left: 16px;[^}]*background-position: left center;[^}]*background-repeat: no-repeat;[^}]*background-size: 14px;[^}]*color: rgba\(0 0 90 \/ 60%\);[^}]*font-size: \.875rem;[^}]*font-weight: 400;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control::before\s*\{[^}]*grid-area: text;[^}]*content: "Text";[^}]*background-image: var\(--migaku-selected-tick\);[^}]*font-weight: 700;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control::after\s*\{[^}]*grid-area: audio;[^}]*content: "Audio";/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control:has\(input:checked\)::before\s*\{[^}]*background-image: none;[^}]*font-weight: 400;/s,
);
assert.match(
  light,
  /\.migaku-audio-card-control:has\(input:checked\)::after\s*\{[^}]*background-image: var\(--migaku-selected-tick\);[^}]*font-weight: 700;/s,
);
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
  /@media only screen and \(max-width: 520px\)\s*\{[\s\S]*?\.migaku-typeselect form\s*\{[^}]*grid-template-columns: 1fr;/,
);
assert.match(
  light,
  /@media only screen and \(max-width: 520px\)\s*\{[\s\S]*?\.migaku-audio-card-control\s*\{[^}]*margin-top: 12px;/,
);
assert.match(
  light,
  /@media only screen and \(max-width: 520px\)\s*\{[\s\S]*?\.migaku-card-front \.migaku-card-unknown,\s*\.migaku-card-back \.migaku-card-unknown\s*\{[^}]*font-size: 40px;[\s\S]*?\.migaku-card-front \.migaku-card-sentence,\s*\.migaku-card-back \.migaku-card-sentence\s*\{[^}]*font-size: 28px;/,
);
assert.match(
  light,
  /@media only screen and \(max-width: 768px\)\s*\{[^}]*main\.container\s*\{[^}]*padding-top: 16px;/s,
);
assert.doesNotMatch(light, /\.migaku-typeselect\s*\{[^}]*border-radius: 10px;/s);
assert.match(light, /\.dict-form\s*\{[^}]*white-space: nowrap;[^}]*word-break: normal;/s);
assert.match(light, /ruby\s*\{[^}]*ruby-align: center;/s);
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
  /\.ankidroid_dark_mode \.migaku-card-shell > \.migaku-type-toggle,\s*\.nightMode \.migaku-card-shell > \.migaku-type-toggle\s*\{[^}]*box-shadow: none;/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card,\s*\.nightMode \.migaku-card,\s*\.ankidroid_dark_mode \.migaku-typeselect,\s*\.nightMode \.migaku-typeselect,\s*\.ankidroid_dark_mode \.UiButton,\s*\.nightMode \.UiButton\s*\{[^}]*box-shadow: 0 9px 20px rgb\(0 0 0 \/ 18%\), 0 3\.76px 8\.3556px rgb\(0 0 0 \/ 14\.4%\), 0 2\.0103px 4\.4673px rgb\(0 0 0 \/ 8\.11%\), 0 1\.127px 2\.5043px rgb\(0 0 0 \/ 3\.63%\), 0 \.5985px 1\.33px rgb\(0 0 0 \/ 2\.8%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-card-translation,[\s\S]*?\.nightMode \.migaku-audio-card-control::after\s*\{[^}]*color: rgba\(255 255 255 \/ 60%\);/s,
);
assert.match(
  dark,
  /\.ankidroid_dark_mode \.migaku-typeselect form::after,\s*\.nightMode \.migaku-typeselect form::after,/s,
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
