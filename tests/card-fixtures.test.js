const assert = require("assert");

const { buildLocalizedFixture } = require("../dev/card-preview/fixtures");

const english = buildLocalizedFixture("en", "syntax");

assert.strictEqual(english.label, "Syntax showcase");
assert.strictEqual(
  english.fields["Target Word"],
  "(language)[language,noun,ˈlæŋɡwɪdʒ]",
);
assert.strictEqual(
  english.fields.Sentence,
  "(Learning)[learn,verb,ˈlɜːnɪŋ] (a)[a,article,ə] (language)[language,noun,ˈlæŋɡwɪdʒ] (opens)[open,verb,ˈoʊpənz] (another)[another,det,əˈnʌðər] (window)[window,noun,ˈwɪndoʊ] (onto)[onto,prep,ˈɒntuː] (the)[the,article,ðə] (world)[world,noun,wɜːrld].",
);

const expectedTargetWords = {
  de: "(Sprache)[Sprache,nn,f]",
  en: "(language)[language,noun,ˈlæŋɡwɪdʒ]",
  es: "(idioma)[idioma,noun,m]",
  fr: "(langue)[langue,noun,f]",
  it: "(lingua)[lingua,noun,f]",
  ja: "言語[げんご;h]",
  ko: "언어[언어$:nng]",
  pt: "(língua)[língua,noun,f]",
  vi: "(ngôn)[ngôn,noun,ŋoːn˧]",
  yue: "語言[jyu5 jin4;n]",
  zh_CN: "语言[yu3 yan2;n]",
  zh_TW: "語言[yu3 yan2;n]",
};

Object.entries(expectedTargetWords).forEach(([language, targetWord]) => {
  const fixture = buildLocalizedFixture(language, "syntax");
  assert.strictEqual(fixture.fields["Target Word"], targetWord);
  assert.ok(fixture.fields.Sentence.includes(targetWord));
  assert.ok(fixture.fields.Translation);
});
const japanese = buildLocalizedFixture("ja", "syntax");
assert.ok(japanese.fields.Sentence.includes("世界[せかい;h]"));
assert.ok(japanese.fields.Sentence.includes("窓[まど;a]"));

["sentence", "vocabulary"].forEach((fixtureName) => {
  const fixture = buildLocalizedFixture("ja", fixtureName);
  assert.strictEqual(fixture.fields["Target Word"], expectedTargetWords.ja);
  assert.ok(fixture.fields.Sentence.includes(expectedTargetWords.ja));
});

const audio = buildLocalizedFixture("zh_CN", "audio");
assert.ok(audio.fields.Sentence.includes(expectedTargetWords.zh_CN));
assert.strictEqual(audio.fields["Target Word"], "");

const stress = buildLocalizedFixture("ja", "stress");
assert.ok(stress.fields.Sentence.includes(expectedTargetWords.ja));
assert.ok(stress.fields.Sentence.includes("verylongunbrokencontentthatmustwrap"));
assert.ok(stress.fields["Target Word"].includes("非常に長い対象語句"));
assert.ok(stress.fields.Translation.includes("intentionally long translation"));

["de", "en", "es", "fr", "it", "pt", "vi"].forEach((language) => {
  const sentence = buildLocalizedFixture(language, "syntax").fields.Sentence;
  const annotations = [...sentence.matchAll(/\(([^)]+)\)\[([^\]]+)\]/g)];
  assert.ok(annotations.length > 0);
  assert.ok(annotations.every(([, word]) => /^[a-zA-Z\u00C0-\u024F]+$/u.test(word)));
  assert.ok(annotations.every(([, , metadata]) => [2, 3].includes(metadata.split(",").length)));
});

["de", "es", "fr", "it", "pt"].forEach((language) => {
  const annotations = [
    ...buildLocalizedFixture(language, "syntax").fields.Sentence.matchAll(/\([^)]+\)\[([^\]]+)\]/g),
  ];
  assert.ok(
    annotations.every(([, metadata]) => {
      const gender = metadata.split(",")[2];
      return !gender || /^[fmnx]$/u.test(gender);
    }),
  );
});

["en", "vi"].forEach((language) => {
  const annotations = [
    ...buildLocalizedFixture(language, "syntax").fields.Sentence.matchAll(/\([^)]+\)\[([^\]]+)\]/g),
  ];
  assert.ok(annotations.every(([, metadata]) => metadata.split(",")[2]));
});

["yue", "zh_CN", "zh_TW"].forEach((language) => {
  const sentence = buildLocalizedFixture(language, "syntax").fields.Sentence;
  assert.doesNotMatch(sentence, /;\s/u);
  assert.ok([...sentence.matchAll(/[\u3400-\u9fff]+\[[^;\]]+;[a-z]+\]/gu)].length > 2);
});

const japaneseAnnotations = [
  ...buildLocalizedFixture("ja", "syntax").fields.Sentence.matchAll(
    /[\u3400-\u9fff]+\[([^\]]+)\]/gu,
  ),
];
assert.ok(japaneseAnnotations.length > 4);
assert.ok(
  japaneseAnnotations.every(([, metadata]) =>
    /^(?:[^,;\]]+|[^,;\]]+,[^,;\]]+);[hanok]\d*$/u.test(metadata),
  ),
);
assert.ok(japaneseAnnotations.some(([, metadata]) => !metadata.includes(",")));
assert.ok(japaneseAnnotations.some(([, metadata]) => metadata.includes(",")));
assert.ok(
  [
    ...buildLocalizedFixture("ko", "syntax").fields.Sentence.matchAll(
      /[\uac00-\ud7af]+\[[^\]$]+\$:[a-z]+\]/gu,
    ),
  ].length > 2,
);

console.log("✓ card fixtures provide language syntax showcases");
