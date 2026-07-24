const assert = require("assert");
const fs = require("fs");
const path = require("path");

const { renderCardDocument } = require("../dev/card-preview/card-document");
const contract = require("../dev/card-preview/template-contract.json");
const { buildLocalizedFixture } = require("../dev/card-preview/fixtures");
const { renderTemplate } = require("../dev/card-preview/template-engine");

const rootDir = path.resolve(__dirname, "..");
const front = renderCardDocument({
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const vocabularyFront = renderCardDocument({
  fixtureName: "vocabulary",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const audioFront = renderCardDocument({
  fixtureName: "audio",
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
assert.match(front, /class="migaku-logo"/);
assert.match(
  front,
  /class="migaku-card migaku-card-front">[\s\S]*class="migaku-card-content">[\s\S]*class="field migaku-card-sentence" data-popup="yes"/,
);
assert.doesNotMatch(front, /class="field migaku-card-unknown"/);
assert.match(front, /\(language\)\[language,noun,ˈlæŋɡwɪdʒ\]/);
assert.doesNotMatch(front, /{{[^{}]+}}/);
assert.match(
  vocabularyFront,
  /class="migaku-card migaku-card-front">[\s\S]*class="migaku-card-content">[\s\S]*class="field migaku-card-unknown" data-popup="yes"/,
);
assert.doesNotMatch(vocabularyFront, /class="field migaku-card-sentence"/);
assert.match(
  audioFront,
  /class="migaku-card migaku-card-front">[\s\S]*class="migaku-card-content">[\s\S]*<audio controls/,
);

contract.languages.forEach((language) => {
  const template = fs.readFileSync(
    path.join(rootDir, "src", "languages", language, "card", "front.html"),
    "utf8",
  );
  const sentenceFields = buildLocalizedFixture(language, "sentence").fields;
  const vocabularyFields = buildLocalizedFixture(language, "vocabulary").fields;
  const sentence = renderTemplate(template, sentenceFields);
  const vocabulary = renderTemplate(template, vocabularyFields);
  const emptySentence = renderTemplate(template, { ...sentenceFields, Sentence: "" });
  const emptyTargetWord = renderTemplate(template, { ...vocabularyFields, "Target Word": "" });

  assert.match(sentence, /class="field migaku-card-sentence"/);
  assert.doesNotMatch(sentence, /class="field migaku-card-unknown"/);
  assert.match(vocabulary, /class="field migaku-card-unknown"/);
  assert.doesNotMatch(vocabulary, /class="field migaku-card-sentence"/);
  assert.doesNotMatch(emptySentence, /class="field migaku-card-sentence"/);
  assert.doesNotMatch(emptyTargetWord, /class="field migaku-card-unknown"/);
});

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
