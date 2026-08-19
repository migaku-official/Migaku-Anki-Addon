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
  audioCard: true,
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const audioVocabularyFront = renderCardDocument({
  audioCard: true,
  fixtureName: "vocabulary",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const emptyAudioFront = renderCardDocument({
  audioCard: true,
  enabledFields: ["Sentence"],
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const emptySentenceFront = renderCardDocument({
  enabledFields: [],
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const emptyVocabularyFront = renderCardDocument({
  enabledFields: ["Is Vocabulary Card"],
  fixtureName: "vocabulary",
  language: "en",
  rootDir,
  side: "front",
  theme: "light",
});
const emptyAudioVocabularyFront = renderCardDocument({
  audioCard: true,
  enabledFields: ["Is Vocabulary Card"],
  fixtureName: "vocabulary",
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
const imagesOnlyBack = renderCardDocument({
  enabledFields: ["Images"],
  fixtureName: "sentence",
  language: "en",
  rootDir,
  side: "back",
  theme: "light",
});
const previewCommandShim = "<script>const pycmd = () => {};</script>";
const previewAudioScript = [...back.matchAll(/<script>([\s\S]*?)<\/script>/g)]
  .map((match) => match[1])
  .find((script) => script.includes("data-preview-audio-button"));
const previewAudio = {
  currentTime: 9,
  pauseCalls: 0,
  paused: true,
  playCalls: 0,
  pause: () => {
    previewAudio.pauseCalls += 1;
    previewAudio.paused = true;
  },
  play: () => {
    previewAudio.playCalls += 1;
    previewAudio.paused = false;
  },
};
const previewAudioButton = {
  blurCalls: 0,
  nextElementSibling: previewAudio,
  addEventListener: (_, listener) => previewAudioButton.click = listener,
  blur: () => previewAudioButton.blurCalls += 1,
};

assert.ok(previewAudioScript);
vm.runInNewContext(previewAudioScript, {
  document: { querySelectorAll: () => [previewAudioButton] },
});
previewAudioButton.click();
assert.strictEqual(previewAudio.currentTime, 0);
assert.strictEqual(previewAudio.playCalls, 1);
previewAudio.currentTime = 3;
previewAudioButton.click();
assert.strictEqual(previewAudio.currentTime, 0);
assert.strictEqual(previewAudio.pauseCalls, 1);
assert.strictEqual(previewAudio.playCalls, 1);
assert.strictEqual(previewAudioButton.blurCalls, 1);

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
  /class="migaku-card migaku-card-front">[\s\S]*class="migaku-card-content">[\s\S]*class="replay-button soundLink"/,
);
assert.match(audioFront, /src="\/fixture-media\/sentence\.m4a"/);
assert.doesNotMatch(audioFront, /target-word\.mp3/);
assert.match(audioVocabularyFront, /src="\/fixture-media\/target-word\.mp3"/);
assert.doesNotMatch(audioVocabularyFront, /sentence\.m4a/);
assert.match(emptyAudioFront, /<div data-preview-empty-front/);
assert.match(emptyAudioFront, /Front of card is blank/);
assert.match(emptyAudioFront, /text-wrap: balance;/);
assert.match(
  emptyAudioFront,
  /class="migaku-card-content">\s*<div data-preview-empty-front role="status">/,
);
assert.match(
  emptyAudioFront,
  /This is a Sentence Audio card, but the Sentence Audio field is empty\./,
);
assert.match(
  emptySentenceFront,
  /This is a Sentence card, but the Sentence field is empty\./,
);
assert.match(
  emptyVocabularyFront,
  /This is a Vocab card, but the Target Word field is empty\./,
);
assert.match(
  emptyAudioVocabularyFront,
  /This is a Vocab Audio card, but the Word Audio field is empty\./,
);
assert.doesNotMatch(front, /<div data-preview-empty-front/);
assert.doesNotMatch(vocabularyFront, /<div data-preview-empty-front/);
assert.doesNotMatch(audioFront, /<div data-preview-empty-front/);
assert.doesNotMatch(audioVocabularyFront, /<div data-preview-empty-front/);
assert.doesNotMatch(front, /class="replay-button soundLink" data-preview-audio-button/);
assert.doesNotMatch(
  vocabularyFront,
  /class="replay-button soundLink" data-preview-audio-button/,
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
  /<button type="button" class="replay-button soundLink" data-preview-audio-button aria-label="Play audio"><\/button><audio hidden preload="none" src="\/fixture-media\/sentence\.m4a"><\/audio>/,
);
assert.match(back, /src="\/fixture-media\/target-word\.mp3"/);
assert.doesNotMatch(back, /<audio controls/);
assert.doesNotMatch(back, /\[sound:/);
assert.match(
  back,
  /class="migaku-card-mode-control">[\s\S]*<span>Sentence<\/span>[\s\S]*type="checkbox" name="vocabulary" role="switch"[\s\S]*<span>Vocab<\/span>/,
);
assert.doesNotMatch(back, /migaku-card-type-title/);
assert.match(
  back,
  /class="migaku-audio-card-control">[\s\S]*<span>Audio card<\/span>[\s\S]*type="checkbox" name="audio" role="switch"/,
);
assert.ok(back.indexOf(previewCommandShim) < back.indexOf('class="migaku-typeselect"'));
assert.doesNotMatch(back, /{{[^{}]+}}/);
assert.strictEqual((imagesOnlyBack.match(/<img /g) || []).length, 3);
[
  "storybook-square.png",
  "storybook-portrait.png",
  "storybook-landscape.png",
].forEach((image) => assert.match(imagesOnlyBack, new RegExp(`/fixture-media/${image}`)));

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
  const audioFields = buildLocalizedFixture(language, "sentence", true).fields;
  const audioInteractions = executeBackInteractions(template, audioFields);
  const audioVocabularyInteractions = executeBackInteractions(
    template,
    buildLocalizedFixture(language, "vocabulary", true).fields,
  );
  const noPycmdInteractions = executeBackInteractions(template, fields, false);
  const localizedBack = renderCardDocument({
    fixtureName: "sentence",
    language,
    rootDir,
    side: "back",
    theme: "light",
  });
  const audioBack = renderCardDocument({
    audioCard: true,
    fixtureName: "sentence",
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
  assert.deepStrictEqual(interactions.commands, ["update_card_type|s"]);
  assert.deepStrictEqual(vocabularyInteractions.initialState, { audio: false, vocabulary: true });
  assert.deepStrictEqual(vocabularyInteractions.commands, ["update_card_type|v"]);
  assert.deepStrictEqual(audioInteractions.initialState, { audio: true, vocabulary: false });
  assert.deepStrictEqual(audioInteractions.commands, ["update_card_type|as"]);
  assert.deepStrictEqual(audioVocabularyInteractions.initialState, { audio: true, vocabulary: true });
  assert.deepStrictEqual(audioVocabularyInteractions.commands, ["update_card_type|av"]);
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
