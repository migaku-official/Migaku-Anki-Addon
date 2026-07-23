const assert = require("assert");
const path = require("path");

const { renderCardDocument } = require("../dev/card-preview/card-document");

const rootDir = path.resolve(__dirname, "..");
const front = renderCardDocument({
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const back = renderCardDocument({
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "back",
  theme: "dark",
});
const previewCommandShim = "<script>const pycmd = () => {};</script>";

assert.match(front, /^<!doctype html>/);
assert.match(front, /data-preview-side="front"/);
assert.match(front, /\(language\)\[language,noun,ˈlæŋɡwɪdʒ\]/);
assert.match(front, /\.migaku-header\s*\{\s*display: none;/);
assert.match(
  front,
  /main\.container\s*\{[^}]*padding: 120px 16px 160px;[^}]*background: #ede3ff;/s,
);
assert.match(front, /\.card\s*\{[^}]*color: rgb\(0, 0, 90\);/s);
assert.match(
  front,
  /\.migaku-card,\s*\.migaku-typeselect\s*\{[^}]*width: 100%;[^}]*max-width: 760px;/s,
);
assert.match(
  front,
  /#content\s*\{[^}]*display: flex;[^}]*flex-direction: column;[^}]*min-height: calc\(100vh - 280px\);/s,
);
assert.match(front, /main\.container \.migaku-card\s*\{[^}]*flex: 1;/s);
assert.match(front, /\.migaku-card\s*\{[^}]*background: #fff;[^}]*border-radius: 24px;/s);
assert.match(
  front,
  /box-shadow: 0 9px 20px rgba\(0 0 90 \/ 14%\), 0 3\.76px 8\.3555px rgba\(0 0 90 \/ 8\.3%\), 0 2\.0103px 4\.4673px rgba\(0 0 90 \/ 5%\), 0 1\.1269px 2\.5043px rgba\(0 0 90 \/ 2\.6%\), 0 \.5985px 1\.33px rgba\(0 0 90 \/ \.8%\);/,
);
assert.doesNotMatch(front, /{{[^{}]+}}/);

assert.match(back, /data-preview-side="back"/);
assert.match(back, /class="card nightMode"/);
assert.match(back, /\.nightMode\.card\s*\{[^}]*color: #fff;/s);
assert.match(back, /\.nightMode main\.container\s*\{[^}]*background: #0a002a;/s);
assert.match(
  back,
  /\.nightMode \.migaku-card\s*\{[^}]*background: #202047;[^}]*box-shadow: 0 9px 20px rgb\(0 0 0 \/ 18%\), 0 3\.76px 8\.3556px rgb\(0 0 0 \/ 14\.4%\), 0 2\.0103px 4\.4673px rgb\(0 0 0 \/ 8\.11%\), 0 1\.127px 2\.5043px rgb\(0 0 0 \/ 3\.63%\), 0 \.5985px 1\.33px rgb\(0 0 0 \/ 2\.8%\);/s,
);
assert.match(back, /Eine Sprache zu lernen öffnet ein weiteres Fenster zur Welt\./);
assert.match(back, /\.migaku-card/);
assert.ok(back.includes(previewCommandShim));
assert.ok(back.indexOf(previewCommandShim) < back.indexOf('class="migaku-typeselect"'));
assert.doesNotMatch(back, /{{[^{}]+}}/);

const syntaxCases = {
  de: "(Sprache)[Sprache,nn,f]",
  en: "(language)[language,noun,ˈlæŋɡwɪdʒ]",
  ja: "言語[げんご,げんご;h]",
  ko: "언어[언어$:nng]",
  yue: "語言[jyu5 jin4;n]",
};

Object.entries(syntaxCases).forEach(([language, targetWord]) => {
  const syntaxDocument = renderCardDocument({
    fixtureName: "syntax",
    language,
    rootDir,
    side: "back",
    theme: "light",
  });
  assert.ok(syntaxDocument.includes(targetWord));
});

console.log("✓ card preview renders the shipped front and back");
