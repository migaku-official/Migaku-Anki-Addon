const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const { renderCardDocument } = require("../dev/card-preview/card-document");
const contract = require("../dev/card-preview/template-contract.json");
const { buildLocalizedFixture } = require("../dev/card-preview/fixtures");
const { renderTemplate } = require("../dev/card-preview/template-engine");

const rootDir = path.resolve(__dirname, "..");
const createInteractiveElement = (hidden) => {
  const listeners = {};
  const element = {
    hidden,
    removed: false,
    attributes: {},
    textContent: "",
    addEventListener: (event, listener) => listeners[event] = listener,
    click: () => listeners.click(),
    remove: () => element.removed = true,
    setAttribute: (name, value) => element.attributes[name] = value,
  };
  return element;
};
const executeBackInteractions = (template, fields, hasPycmd = true) => {
  const rendered = renderTemplate(template, fields);
  const scripts = [...rendered.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  const translationToggle = createInteractiveElement(false);
  const translation = createInteractiveElement(true);
  const typeToggle = createInteractiveElement(false);
  typeToggle.textContent = "Change card type";
  const typeSelector = createInteractiveElement(true);
  const form = {
    elements: {
      audio: { checked: false },
      vocabulary: { checked: false },
    },
    onchange: undefined,
  };
  const elements = {
    ".migaku-card-translation": translation,
    ".migaku-translation-toggle": translationToggle,
    ".migaku-type-toggle": typeToggle,
    ".migaku-typeselect": typeSelector,
    ".migaku-typeselect form": form,
  };
  const commands = [];

  const context = {
    document: { querySelector: (selector) => elements[selector] },
  };
  if (hasPycmd) context.pycmd = (command) => commands.push(command);
  vm.runInNewContext(scripts[scripts.length - 1][1], context);
  const initialState = {
    audio: form.elements.audio.checked,
    vocabulary: form.elements.vocabulary.checked,
  };
  translationToggle.click();
  if (hasPycmd) {
    typeToggle.click();
    const typeSelectorAfterOpen = typeSelector.hidden;
    const typeToggleTextAfterOpen = typeToggle.textContent;
    form.elements.audio.checked = true;
    form.elements.vocabulary.checked = true;
    form.onchange();
    typeToggle.click();
    return {
      commands,
      initialState,
      translation,
      translationToggle,
      typeSelector,
      typeSelectorAfterOpen,
      typeToggle,
      typeToggleTextAfterOpen,
    };
  }

  return { commands, initialState, translation, translationToggle, typeSelector, typeToggle };
};
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
assert.match(back, /class="migaku-card-unknown migaku-indented"/);
assert.match(back, /class="migaku-card-sentence"/);
assert.match(
  back,
  /<button class="UiButton migaku-translation-toggle" type="button" aria-expanded="false" aria-controls="migaku-card-translation">See Translation<\/button>/,
);
assert.match(back, /id="migaku-card-translation" class="migaku-card-translation" hidden>/);
assert.match(back, /<hr class="sentence-separator">/);
assert.match(
  back,
  /<button class="UiButton migaku-type-toggle" type="button" aria-expanded="false" aria-controls="migaku-typeselect">Change card type<\/button>/,
);
assert.match(back, /id="migaku-typeselect" class="migaku-typeselect" hidden>/);
assert.doesNotMatch(back, /<h2>/);
assert.doesNotMatch(back, /migaku-type-close/);
assert.match(back, /class="migaku-card-audio-row"/);
assert.match(
  back,
  /class="migaku-card-mode-control">[\s\S]*<span>Sentence<\/span>[\s\S]*type="checkbox" name="vocabulary" role="switch"[\s\S]*<span>Vocab<\/span>/,
);
assert.match(
  back,
  /class="migaku-audio-card-control">[\s\S]*<span>Audio card<\/span>[\s\S]*type="checkbox" name="audio" role="switch"/,
);
assert.ok(back.indexOf(previewCommandShim) < back.indexOf('class="migaku-typeselect"'));
assert.doesNotMatch(back, /{{[^{}]+}}/);

contract.languages.forEach((language) => {
  const template = fs.readFileSync(
    path.join(rootDir, "src", "languages", language, "card", "back.html"),
    "utf8",
  );
  const fields = buildLocalizedFixture(language, "sentence").fields;
  const interactions = executeBackInteractions(template, fields);
  const vocabularyInteractions = executeBackInteractions(
    template,
    buildLocalizedFixture(language, "vocabulary").fields,
  );
  const audioFields = buildLocalizedFixture(language, "audio").fields;
  const audioInteractions = executeBackInteractions(template, audioFields);
  const audioVocabularyInteractions = executeBackInteractions(template, {
    ...audioFields,
    "Is Vocabulary Card": "1",
  });
  const noPycmdInteractions = executeBackInteractions(template, fields, false);
  const localizedBack = renderCardDocument({
    fixtureName: "sentence",
    language,
    rootDir,
    side: "back",
    theme: "light",
  });
  const audioBack = renderCardDocument({
    fixtureName: "audio",
    language,
    rootDir,
    side: "back",
    theme: "light",
  });
  const emptyTranslation = renderTemplate(template, { ...fields, Translation: "" });
  const emptySentenceVocabulary = renderTemplate(template, {
    ...buildLocalizedFixture(language, "vocabulary").fields,
    Sentence: "",
  });

  assert.match(localizedBack, /class="migaku-card-shell"/);
  assert.match(localizedBack, /class="UiButton migaku-translation-toggle"/);
  assert.match(localizedBack, /id="migaku-card-translation" class="migaku-card-translation" hidden/);
  assert.match(localizedBack, /class="UiButton migaku-type-toggle"/);
  assert.match(localizedBack, /id="migaku-typeselect" class="migaku-typeselect" hidden/);
  assert.match(localizedBack, /name="vocabulary" role="switch"/);
  assert.match(localizedBack, /name="audio" role="switch"/);
  assert.match(localizedBack, /translation\.hidden = false/);
  assert.match(localizedBack, /translationToggle\.remove\(\)/);
  assert.match(localizedBack, /pycmd\('update_card_type\|'/);
  assert.match(audioBack, /class="sentence-separator"/);
  assert.doesNotMatch(emptyTranslation, /class="UiButton migaku-translation-toggle"/);
  assert.doesNotMatch(emptyTranslation, /id="migaku-card-translation"/);
  assert.match(emptySentenceVocabulary, /class="sentence-separator"/);
  assert.strictEqual(interactions.translation.hidden, false);
  assert.strictEqual(interactions.translationToggle.removed, true);
  assert.strictEqual(interactions.typeSelectorAfterOpen, false);
  assert.strictEqual(interactions.typeToggleTextAfterOpen, "Dismiss");
  assert.strictEqual(interactions.typeSelector.hidden, true);
  assert.strictEqual(interactions.typeToggle.hidden, false);
  assert.strictEqual(interactions.typeToggle.textContent, "Change card type");
  assert.deepStrictEqual(interactions.initialState, { audio: false, vocabulary: false });
  assert.deepStrictEqual(interactions.commands, ["update_card_type|av"]);
  assert.deepStrictEqual(vocabularyInteractions.initialState, { audio: false, vocabulary: true });
  assert.deepStrictEqual(audioInteractions.initialState, { audio: true, vocabulary: false });
  assert.deepStrictEqual(audioVocabularyInteractions.initialState, { audio: true, vocabulary: true });
  assert.strictEqual(noPycmdInteractions.typeToggle.hidden, true);
  assert.strictEqual(noPycmdInteractions.typeSelector.hidden, true);
  assert.deepStrictEqual(noPycmdInteractions.commands, []);
});

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
