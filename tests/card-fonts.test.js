const assert = require("assert");
const fs = require("fs");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const expectedFonts = {
  de: { assetCount: 2, fontName: "Inter" },
  en: { assetCount: 2, fontName: "Inter" },
  es: { assetCount: 2, fontName: "Inter" },
  fr: { assetCount: 2, fontName: "Inter" },
  it: { assetCount: 2, fontName: "Inter" },
  ja: { assetCount: 12, fontName: "Noto Sans JP" },
  ko: { assetCount: 2, fontName: "LINE Seed KR" },
  pt: { assetCount: 2, fontName: "Inter" },
  vi: { assetCount: 2, fontName: "Inter" },
  yue: { assetCount: 144, assetPrefix: "_ChironHeiHK-", fontName: "Chiron Hei HK WS" },
  zh_CN: { assetCount: 8, fontName: "Noto Sans SC" },
  zh_TW: { assetCount: 8, fontName: "Noto Sans TC" },
};

Object.entries(expectedFonts).forEach(([language, { assetCount, assetPrefix, fontName }]) => {
  const cardDir = path.join(rootDir, "src", "languages", language, "card");
  const fontsCss = fs.readFileSync(path.join(cardDir, "fonts.css"), "utf8");
  const stylesCss = fs.readFileSync(path.join(cardDir, "styles.css"), "utf8");
  const mediaDir = path.join(cardDir, "media");
  const referencedAssets = Array.from(fontsCss.matchAll(/url\('\/(_[^']+\.woff2)'\)/g), (match) => match[1]);
  const mediaAssets = fs.readdirSync(mediaDir).sort();

  assert.match(fontsCss, new RegExp(`/\\* Migaku UI default: ${fontName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")} \\*/`));
  assert.match(fontsCss, /font-family: cardFont;/);
  assert.ok(referencedAssets.length > 0, `${language} should reference local WOFF2 media`);
  assert.ok(!/https?:\/\//.test(fontsCss), `${language} should work without remote font requests`);
  assert.deepEqual(mediaAssets, Array.from(new Set(referencedAssets)).sort());
  assert.equal(mediaAssets.length, assetCount, `${language} should ship every default font face`);
  assert.ok(mediaAssets.every((asset) => asset.startsWith("_") && asset.endsWith(".woff2")));
  if (assetPrefix) assert.ok(mediaAssets.every((asset) => asset.startsWith(assetPrefix)));
  mediaAssets.forEach((asset) => {
    const signature = fs.readFileSync(path.join(mediaDir, asset)).subarray(0, 4).toString("ascii");
    assert.equal(signature, "wOF2", `${language}/${asset} should be a WOFF2 font`);
  });
  assert.ok(stylesCss.startsWith(fontsCss), `${language} generated styles should include its font imports`);
});

console.log("✓ card fonts match Migaku UI language defaults");
