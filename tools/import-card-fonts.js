const fs = require("fs");
const path = require("path");

const addonRoot = path.resolve(__dirname, "..");
const frontEndRoot = path.resolve(process.argv[2] || path.join(addonRoot, "..", "migaku-front-end"));
const fontSourceDir = path.join(frontEndRoot, "packages", "ui", "src", "styles", "scss", "fonts");
const languagesRoot = path.join(addonRoot, "src", "languages");
const fontGroups = [
  { fontName: "Inter", languages: ["de", "en", "es", "fr", "it", "pt", "vi"], source: "inter.scss", family: "InterVariable" },
  { fontName: "Noto Sans JP", languages: ["ja"], source: "noto-sans-jp.scss" },
  { fontName: "LINE Seed KR", languages: ["ko"], source: "line-seed-kr.scss" },
  { fontName: "Noto Sans SC", languages: ["zh_CN"], source: "noto-sans-sc.scss" },
  { fontName: "Noto Sans TC", languages: ["zh_TW"], source: "noto-sans-tc.scss" },
  { assetPrefix: "ChironHeiHK-", fontName: "Chiron Hei HK WS", languages: ["yue"], source: "chiron-hei-hk.scss" },
];

const stripComments = (source) => source.replace(/\/\*[\s\S]*?\*\//g, "");
const getReferencedAssets = (css) => Array.from(css.matchAll(/url\(['"]\/([^'"]+)['"]\)/g), (match) => path.basename(match[1]));
const getFontFaces = ({ assetPrefix = "", family, source }) => {
  const sourcePath = path.join(fontSourceDir, source);
  const faces = stripComments(fs.readFileSync(sourcePath, "utf8")).match(/@font-face\s*\{[\s\S]*?\}/g) || [];
  const selectedFaces = family ? faces.filter((face) => face.includes(`font-family: ${family};`)) : faces;
  return selectedFaces.map((face) => {
    const sourceUrl = face.match(/https:\/\/migaku-public-data\.migaku\.com\/[^'")?]+\.woff2(?:\?[^'")]+)?/)?.[0];
    if (!sourceUrl) throw new Error(`Missing hosted WOFF2 source in ${source}`);
    const assetName = `_${assetPrefix}${path.basename(new URL(sourceUrl).pathname)}`;
    const css = face
      .replace(/font-family:\s*[^;]+;/, "font-family: cardFont;")
      .replace(/\s*src:\s*url\([\s\S]*?;/g, "")
      .replace(/\}$/, `  src: url('/${assetName}') format('woff2');\n}`)
      .trim();
    return { assetName, css, sourceUrl };
  });
};
const downloadFont = async (sourceUrl) => {
  const response = await fetch(sourceUrl);
  if (!response.ok) throw new Error(`Unable to download ${sourceUrl}: ${response.status}`);
  const data = Buffer.from(await response.arrayBuffer());
  if (data.subarray(0, 4).toString("ascii") !== "wOF2") throw new Error(`Invalid WOFF2 response from ${sourceUrl}`);
  return data;
};
const downloadFonts = async (sourceUrls) => {
  const pending = Array.from(sourceUrls);
  const downloads = new Map();
  const worker = async () => {
    while (pending.length) {
      const sourceUrl = pending.shift();
      downloads.set(sourceUrl, await downloadFont(sourceUrl));
    }
  };
  await Promise.all(Array.from({ length: Math.min(8, pending.length) }, worker));
  return downloads;
};
const importFonts = async () => {
  const preparedGroups = fontGroups.map((group) => ({ ...group, faces: getFontFaces(group) }));
  const sourceUrls = new Set(preparedGroups.flatMap(({ faces }) => faces.map(({ sourceUrl }) => sourceUrl)));
  const downloads = await downloadFonts(sourceUrls);

  preparedGroups.forEach(({ faces, fontName, languages, source }) => {
    const css = [
      `/* Migaku UI default: ${fontName} */`,
      `/* Imported from packages/ui/src/styles/scss/fonts/${source}. */`,
      "",
      ...faces.flatMap(({ css: faceCss }) => [faceCss, ""]),
    ].join("\n");
    languages.forEach((language) => {
      const cardDir = path.join(languagesRoot, language, "card");
      const fontsPath = path.join(cardDir, "fonts.css");
      const mediaDir = path.join(cardDir, "media");
      fs.mkdirSync(mediaDir, { recursive: true });
      if (fs.existsSync(fontsPath)) {
        getReferencedAssets(fs.readFileSync(fontsPath, "utf8")).forEach((asset) =>
          fs.rmSync(path.join(mediaDir, asset), { force: true }),
        );
      }
      fs.writeFileSync(fontsPath, css);
      new Map(faces.map((face) => [face.assetName, face.sourceUrl])).forEach((sourceUrl, assetName) =>
        fs.writeFileSync(path.join(mediaDir, assetName), downloads.get(sourceUrl)),
      );
    });
  });
  console.log(`✓ imported ${sourceUrls.size} Migaku UI font assets`);
};

importFonts().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
