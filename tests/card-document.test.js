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
assert.doesNotMatch(front, /{{[^{}]+}}/);

assert.match(back, /data-preview-side="back"/);
assert.match(back, /class="card nightMode"/);
assert.match(back, /Eine Sprache zu lernen öffnet ein weiteres Fenster zur Welt\./);
assert.match(back, /\.migaku-card/);
assert.ok(back.includes(previewCommandShim));
assert.ok(back.indexOf(previewCommandShim) < back.indexOf('class="migaku-typeselect"'));
assert.doesNotMatch(back, /{{[^{}]+}}/);

const syntaxCases = {
  de: "(Sprache)[Sprache,nn,f]",
  en: "(language)[language,noun,ˈlæŋɡwɪdʒ]",
  ja: "言語[げんご;h]",
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
