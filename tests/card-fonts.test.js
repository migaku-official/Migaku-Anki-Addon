const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { languages } = require("../dev/card-preview/template-contract.json");

const rootDir = path.resolve(__dirname, "..");
const expectedAssetCounts = {
  de: 2,
  en: 2,
  es: 2,
  fr: 2,
  it: 2,
  ja: 12,
  ko: 2,
  pt: 2,
  vi: 2,
  yue: 144,
  zh_CN: 8,
  zh_TW: 8,
};
assert.deepEqual(Object.keys(expectedAssetCounts).sort(), languages.slice().sort(), "every supported language should have a font contract");

Object.entries(expectedAssetCounts).forEach(([language, assetCount]) => {
  const cardDir = path.join(rootDir, "src", "languages", language, "card");
  const fontsCss = fs.readFileSync(path.join(cardDir, "fonts.css"), "utf8");
  const stylesCss = fs.readFileSync(path.join(cardDir, "styles.css"), "utf8");
  const mediaDir = path.join(cardDir, "media");
  const referencedAssets = Array.from(fontsCss.matchAll(/url\('\/(_[^']+\.woff2)'\)/g), (match) => match[1]);
  const mediaEntries = fs.readdirSync(mediaDir).sort();
  const mediaAssets = mediaEntries.filter((asset) => asset.endsWith(".woff2"));

  assert.match(fontsCss, /^\/\* Migaku UI default: [^*]+ \*\//);
  assert.match(fontsCss, /\/\* Canonical variable: \$font-[\w-]+ in packages\/ui\/src\/styles\/scss\/_variables\.scss\. \*\//);
  assert.match(fontsCss, /font-family: cardFont;/);
  assert.ok(referencedAssets.length > 0, `${language} should reference local WOFF2 media`);
  assert.ok(!/https?:\/\//.test(fontsCss), `${language} should work without remote font requests`);
  assert.deepEqual(mediaAssets, Array.from(new Set(referencedAssets)).sort());
  assert.ok(!mediaEntries.some((asset) => asset.startsWith("_NotoSerif")), `${language} should not retain legacy Noto Serif media`);
  assert.equal(mediaAssets.length, assetCount, `${language} should ship every default font face`);
  assert.ok(mediaAssets.every((asset) => asset.startsWith("_migaku-card-") && asset.endsWith(".woff2")));
  mediaAssets.forEach((asset) => {
    const data = fs.readFileSync(path.join(mediaDir, asset));
    assert.equal(data.subarray(0, 4).toString("ascii"), "wOF2", `${language}/${asset} should be a WOFF2 font`);
    assert.equal(data.readUInt32BE(8), data.length, `${language}/${asset} should have a valid declared length`);
    assert.ok(data.readUInt16BE(12) > 0, `${language}/${asset} should contain font tables`);
    assert.equal(data.readUInt16BE(14), 0, `${language}/${asset} should have a valid reserved header field`);
    assert.ok(data.readUInt32BE(20) <= data.length - 48, `${language}/${asset} should have valid compressed data bounds`);
  });
  assert.ok(stylesCss.startsWith(fontsCss), `${language} generated styles should include its font imports`);
});

console.log("✓ card fonts match Migaku UI language defaults");
