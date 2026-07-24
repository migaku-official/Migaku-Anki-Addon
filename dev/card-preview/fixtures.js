const image = (label, color) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img" aria-label="${label}"><rect width="640" height="360" fill="${color}"/><circle cx="320" cy="150" r="72" fill="rgba(255,255,255,.72)"/><text x="320" y="274" text-anchor="middle" font-family="sans-serif" font-size="28" fill="white">${label}</text></svg>`;

const dataImage = (label, color) =>
  `data:image/svg+xml,${encodeURIComponent(image(label, color))}`;

const syntaxTranslation = "Learning a language opens another window onto the world.";
const standardFields = [
  "Sentence",
  "Translation",
  "Target Word",
  "Definitions",
  "Screenshot",
  "Sentence Audio",
  "Word Audio",
  "Images",
  "Example Sentences",
  "Notes",
  "Reading",
  "Alternate Sentence",
  "Is Vocabulary Card",
  "Is Audio Card",
];
const toggleFields = standardFields.filter((field) => field !== "Reading");
const fixedMediaFields = {
  Screenshot:
    '<img alt="Vegeta wearing a scouter" src="/fixture-media/vegeta-scouter.png">',
  "Sentence Audio": "[sound:sentence.m4a]",
  "Word Audio": "[sound:target-word.mp3]",
};
const buildFieldFallbacks = (language) => {
  const profile = syntaxProfiles[language];
  return {
    "Alternate Sentence": profile.sentence,
    Definitions: "<p>Fixture definition.</p>",
    "Example Sentences": "<p>Fixture example sentence.</p>",
    Images:
      '<img alt="Vegeta wearing a scouter" src="/fixture-media/vegeta-scouter.png">',
    "Is Audio Card": "1",
    "Is Vocabulary Card": "1",
    Notes: "<p>Fixture note.</p>",
    Reading: "Fixture reading",
    Sentence: profile.sentence,
    "Target Word": profile.targetWord,
    Translation: profile.translation,
    ...fixedMediaFields,
  };
};

const syntaxProfiles = {
  de: {
    sentence:
      "(Eine)[ein,art,f] (Sprache)[Sprache,nn,f] (zu)[zu,zu,x] (lernen)[lernen,v,x] (öffnet)[öffnen,v,x] (ein)[ein,art,n] (weiteres)[weit,adj,n] (Fenster)[Fenster,nn,n] (zur)[zu,prepart,f] (Welt)[Welt,nn,f].",
    targetWord: "(Sprache)[Sprache,nn,f]",
    translation: syntaxTranslation,
  },
  en: {
    sentence:
      "(Learning)[learn,verb,ˈlɜːnɪŋ] (a)[a,article,ə] (language)[language,noun,ˈlæŋɡwɪdʒ] (opens)[open,verb,ˈoʊpənz] (another)[another,det,əˈnʌðər] (window)[window,noun,ˈwɪndoʊ] (onto)[onto,prep,ˈɒntuː] (the)[the,article,ðə] (world)[world,noun,wɜːrld].",
    targetWord: "(language)[language,noun,ˈlæŋɡwɪdʒ]",
    translation: "Eine Sprache zu lernen öffnet ein weiteres Fenster zur Welt.",
  },
  es: {
    sentence:
      "(Aprender)[aprender,verb] (un)[uno,article,m] (idioma)[idioma,noun,m] (abre)[abrir,verb] (otra)[otro,adj,f] (ventana)[ventana,noun,f] (al)[al,article,m] (mundo)[mundo,noun,m].",
    targetWord: "(idioma)[idioma,noun,m]",
    translation: syntaxTranslation,
  },
  fr: {
    sentence:
      "(Apprendre)[apprendre,verb] (une)[un,article,f] (langue)[langue,noun,f] (ouvre)[ouvrir,verb] (une)[un,article,f] (autre)[autre,adj,f] (fenêtre)[fenêtre,noun,f] (sur)[sur,prep] (le)[le,article,m] (monde)[monde,noun,m].",
    targetWord: "(langue)[langue,noun,f]",
    translation: syntaxTranslation,
  },
  it: {
    sentence:
      "(Imparare)[imparare,verb] (una)[uno,article,f] (lingua)[lingua,noun,f] (apre)[aprire,verb] (una)[uno,article,f] (nuova)[nuovo,adj,f] (finestra)[finestra,noun,f] (sul)[su,prep,m] (mondo)[mondo,noun,m].",
    targetWord: "(lingua)[lingua,noun,f]",
    translation: syntaxTranslation,
  },
  ja: {
    sentence:
      "言語[げんご;h]を 学[まな,まなぶ;n2]ぶと、世界[せかい;h]への 窓[まど;a]が 開[ひら,ひらく;n2]きます。",
    targetWord: "言語[げんご;h]",
    translation: syntaxTranslation,
  },
  ko: {
    sentence:
      "언어[언어$:nng]를 배우면[배우다$:v] 세상[세상$:nng]을 보는[보다$:v] 또 다른[다르다$:a] 창문[창문$:nng]이 열립니다[열리다$:v].",
    targetWord: "언어[언어$:nng]",
    translation: syntaxTranslation,
  },
  pt: {
    sentence:
      "(Aprender)[aprender,verb] (uma)[um,article,f] (língua)[língua,noun,f] (abre)[abrir,verb] (outra)[outro,adj,f] (janela)[janela,noun,f] (para)[para,prep] (o)[o,article,m] (mundo)[mundo,noun,m].",
    targetWord: "(língua)[língua,noun,f]",
    translation: syntaxTranslation,
  },
  vi: {
    sentence:
      "Học một (ngôn)[ngôn,noun,ŋoːn˧] ngữ mở (ra)[ra,part,zaː˧] một cửa sổ khác nhìn (ra)[ra,part,zaː˧] thế giới.",
    targetWord: "(ngôn)[ngôn,noun,ŋoːn˧]",
    translation: syntaxTranslation,
  },
  yue: {
    sentence:
      "學習[hok6 zaap6;v]一門[jat1 mun4;q]語言[jyu5 jin4;n]，就會打開[daa2 hoi1;v]另一扇[ling6 jat1 sin3;q]望向[mong6 hoeng3;v]世界[sai3 gaai3;n]嘅窗[coeng1;n]。",
    targetWord: "語言[jyu5 jin4;n]",
    translation: syntaxTranslation,
  },
  zh_CN: {
    sentence:
      "学习[xue2 xi2;v]一门[yi1 men2;q]语言[yu3 yan2;n]，就会打开[da3 kai1;v]另一扇[ling4 yi1 shan4;q]看向[kan4 xiang4;v]世界[shi4 jie4;n]的窗户[chuang1 hu5;n]。",
    targetWord: "语言[yu3 yan2;n]",
    translation: syntaxTranslation,
  },
  zh_TW: {
    sentence:
      "學習[xue2 xi2;v]一門[yi1 men2;q]語言[yu3 yan2;n]，就會打開[da3 kai1;v]另一扇[ling4 yi1 shan4;q]看向[kan4 xiang4;v]世界[shi4 jie4;n]的窗戶[chuang1 hu5;n]。",
    targetWord: "語言[yu3 yan2;n]",
    translation: syntaxTranslation,
  },
};

const fixtures = {
  sentence: {
    label: "Sentence card",
    fields: {
      Definitions:
        "<ol><li>A system of communication used by a community.</li><li>The style of a piece of writing or speech.</li></ol>",
      "Example Sentences":
        "<p>Language connects people across cultures.</p><p>Her use of language is precise and warm.</p>",
      Images: `<img alt="A second fixture" src="${dataImage("Supporting image", "#f59e0b")}">`,
      "Is Audio Card": "",
      "Is Vocabulary Card": "",
      Notes:
        "<p>Fixture note: this content intentionally includes <strong>rich text</strong> and punctuation.</p>",
      Screenshot: `<img alt="A preview fixture" src="${dataImage("Screenshot fixture", "#2563eb")}">`,
      Sentence: "Learning a language opens another window onto the world.",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "<span class=\"word\">language</span>",
      Translation:
        "Eine Sprache zu lernen öffnet ein weiteres Fenster zur Welt.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
  vocabulary: {
    label: "Vocabulary card",
    fields: {
      Definitions:
        "<ol><li>A word or phrase used in a particular language.</li></ol>",
      "Example Sentences": "<p>This expression appears in everyday conversation.</p>",
      Images: "",
      "Is Audio Card": "",
      "Is Vocabulary Card": "1",
      Notes: "<p>Vocabulary fixture with a deliberately concise definition.</p>",
      Screenshot: "",
      Sentence: "The expression sounds natural in this context.",
      "Sentence Audio": "",
      "Target Word": "<span class=\"word\">expression</span>",
      Translation: "Der Ausdruck klingt in diesem Kontext natürlich.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
  audio: {
    label: "Audio card",
    fields: {
      Definitions: "",
      "Example Sentences": "",
      Images: "",
      "Is Audio Card": "1",
      "Is Vocabulary Card": "",
      Notes: "",
      Screenshot: "",
      Sentence: "Can you understand this sentence from audio alone?",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "",
      Translation: "Kannst du diesen Satz allein durch den Ton verstehen?",
      "Word Audio": "",
    },
  },
  stress: {
    label: "Stress test",
    fields: {
      Definitions: `<ol>${Array.from(
        { length: 8 },
        (_, index) =>
          `<li>Definition ${index + 1}: a deliberately long explanation that exercises wrapping, vertical rhythm, and overflow behavior across narrow and wide screens.</li>`,
      ).join("")}</ol>`,
      "Example Sentences": `<p>${"A long example sentence with mixed punctuation — commas, dashes, parentheses, and emphasis. ".repeat(
        5,
      )}</p>`,
      Images: Array.from(
        { length: 4 },
        (_, index) =>
          `<img alt="Stress fixture ${index + 1}" src="${dataImage(`Image ${index + 1}`, "#7c3aed")}">`,
      ).join(""),
      "Is Audio Card": "",
      "Is Vocabulary Card": "",
      Notes: `<p>${"UnbrokenContent".repeat(24)}</p>`,
      Screenshot: `<img alt="Wide stress fixture" src="${dataImage("Wide screenshot", "#0f766e")}">`,
      Sentence:
        "これは非常に長い文章です。它包含多种文字、verylongunbrokencontentthatmustwrapwithoutbreakingthelayout、そして複数の句読点。",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "<span class=\"word\">非常に長い対象語句</span>",
      Translation:
        "This intentionally long translation verifies that the card remains readable when content grows far beyond the happy path.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
  syntax: {
    label: "Syntax showcase",
    fields: {
      Definitions:
        "<ol><li>Hover or tap annotated words to inspect their syntax metadata.</li></ol>",
      "Example Sentences": "<p>The sentence and target word both use Migaku syntax.</p>",
      Images: "",
      "Is Audio Card": "",
      "Is Vocabulary Card": "",
      Notes: "<p>Language-specific syntax fixture for coloring and popup checks.</p>",
      Screenshot: "",
      Sentence: "",
      "Sentence Audio": "",
      "Target Word": "",
      Translation: "",
      "Word Audio": "",
    },
  },
};

const buildLocalizedFixture = (language, fixtureName) => {
  const fixture = fixtures[fixtureName];
  if (!fixture) throw new Error(`Unknown fixture: ${fixtureName}`);
  const profile = syntaxProfiles[language];
  if (!profile) throw new Error(`Missing syntax fixture for language: ${language}`);
  const mergeStressContent = (localizedValue, fixtureValue) =>
    fixtureName === "stress" ? `${localizedValue} ${fixtureValue}` : localizedValue;
  return {
    ...fixture,
    fields: {
      ...fixture.fields,
      ...fixedMediaFields,
      Sentence: mergeStressContent(profile.sentence, fixture.fields.Sentence),
      "Target Word": mergeStressContent(
        fixtureName === "audio" ? fixture.fields["Target Word"] : profile.targetWord,
        fixture.fields["Target Word"],
      ),
      Translation: mergeStressContent(profile.translation, fixture.fields.Translation),
    },
  };
};

module.exports = {
  buildFieldFallbacks,
  buildLocalizedFixture,
  fixtures,
  standardFields,
  toggleFields,
};
