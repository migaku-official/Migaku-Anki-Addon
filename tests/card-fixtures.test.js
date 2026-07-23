const assert = require("assert");

const { getFixture } = require("../dev/card-preview/fixtures");

const english = getFixture("en", "syntax");

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
  ja: "言語[げんご,げんご;h]",
  ko: "언어[언어$:nng]",
  pt: "(língua)[língua,noun,f]",
  vi: "(ngôn)[ngôn,noun,ŋoːn˧]",
  yue: "語言[jyu5 jin4;n]",
  zh_CN: "语言[yu3 yan2;n]",
  zh_TW: "語言[yu3 yan2;n]",
};

Object.entries(expectedTargetWords).forEach(([language, targetWord]) => {
  const fixture = getFixture(language, "syntax");
  assert.strictEqual(fixture.fields["Target Word"], targetWord);
  assert.ok(fixture.fields.Sentence.includes(targetWord));
  assert.ok(fixture.fields.Translation);
});

["sentence", "vocabulary", "stress"].forEach((fixtureName) => {
  const fixture = getFixture("ja", fixtureName);
  assert.strictEqual(fixture.fields["Target Word"], expectedTargetWords.ja);
  assert.ok(fixture.fields.Sentence.includes(expectedTargetWords.ja));
});

const audio = getFixture("zh_CN", "audio");
assert.ok(audio.fields.Sentence.includes(expectedTargetWords.zh_CN));
assert.strictEqual(audio.fields["Target Word"], "");

["de", "en", "es", "fr", "it", "pt", "vi"].forEach((language) => {
  const sentence = getFixture(language, "syntax").fields.Sentence;
  const annotatedWords = [...sentence.matchAll(/\(([^)]+)\)\[/g)].map((match) => match[1]);
  assert.ok(annotatedWords.length > 0);
  assert.ok(annotatedWords.every((word) => /^[a-zA-Z\u00C0-\u024F]+$/u.test(word)));
});

["yue", "zh_CN", "zh_TW"].forEach((language) =>
  assert.doesNotMatch(getFixture(language, "syntax").fields.Sentence, /;\s/u),
);

console.log("✓ card fixtures provide language syntax showcases");
