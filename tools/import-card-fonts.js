const fs = require("fs");
const https = require("https");
const path = require("path");

const addonRoot = path.resolve(__dirname, "..");
const frontEndRoot = path.resolve(process.argv[2] || path.join(addonRoot, "..", "migaku-front-end"));
const fontSourceDir = path.join(frontEndRoot, "packages", "ui", "src", "styles", "scss", "fonts");
const fontVariablesPath = path.join(fontSourceDir, "..", "_variables.scss");
const languagesRoot = path.join(addonRoot, "src", "languages");
const fontGroups = [
  { fontVariable: "font-latin", familyVariable: "font-latin-variable", languages: ["de", "en", "es", "fr", "it", "pt", "vi"], source: "inter.scss" },
  { fontVariable: "font-ja", languages: ["ja"], source: "noto-sans-jp.scss" },
  { fontVariable: "font-ko", languages: ["ko"], source: "line-seed-kr.scss" },
  { fontVariable: "font-zh-cn", languages: ["zh_CN"], source: "noto-sans-sc.scss" },
  { fontVariable: "font-zh-tw", languages: ["zh_TW"], source: "noto-sans-tc.scss" },
  { fontVariable: "font-yue", languages: ["yue"], source: "chiron-hei-hk.scss" },
];

const stripComments = (source) => source.replace(/\/\*[\s\S]*?\*\//g, "");
const getReferencedAssets = (css) => Array.from(css.matchAll(/url\(['"]\/([^'"]+)['"]\)/g), (match) => path.basename(match[1]));
const getCanonicalFonts = () =>
  new Map(Array.from(stripComments(fs.readFileSync(fontVariablesPath, "utf8")).matchAll(/^\$(font-[\w-]+):\s*['"]([^'"]+)['"];/gm), (match) => [match[1], match[2]]));
const resolveFontGroup = (canonicalFonts, group) => {
  const fontName = canonicalFonts.get(group.fontVariable);
  const family = canonicalFonts.get(group.familyVariable || group.fontVariable);
  if (!fontName || !family) throw new Error(`Missing canonical font variable for ${group.languages.join(", ")}`);
  return { ...group, family, fontName };
};
const getFontFaces = ({ family, source }) => {
  const sourcePath = path.join(fontSourceDir, source);
  const faces = stripComments(fs.readFileSync(sourcePath, "utf8")).match(/@font-face\s*\{[\s\S]*?\}/g) || [];
  const selectedFaces = faces.filter((face) => face.match(/font-family:\s*['"]?([^;'"]+)['"]?\s*;/)?.[1] === family);
  if (!selectedFaces.length) throw new Error(`No font faces selected from ${source}`);
  const preparedFaces = selectedFaces.map((face) => {
    const sourceUrl = face.match(/https:\/\/migaku-public-data\.migaku\.com\/[^'")?]+\.woff2(?:\?[^'")]+)?/)?.[0];
    if (!sourceUrl) throw new Error(`Missing hosted WOFF2 source in ${source}`);
    const assetName = `_migaku-card-${path.basename(source, ".scss")}-${path.basename(new URL(sourceUrl).pathname)}`;
    const css = face
      .replace(/font-family:\s*[^;]+;/, "font-family: cardFont;")
      .replace(/font-display:\s*[^;]+;/, "font-display: block;")
      .replace(/(@font-face\s*\{)(?![\s\S]*font-display:)/, "$1\n  font-display: block;")
      .replace(/\s*src:\s*url\([\s\S]*?;/g, "")
      .replace(/\}$/, `  src: url('/${assetName}') format('woff2');\n}`)
      .trim();
    return { assetName, css, sourceUrl };
  });
  const sourceUrlsByAsset = new Map();
  preparedFaces.forEach(({ assetName, sourceUrl }) => {
    if (sourceUrlsByAsset.has(assetName) && sourceUrlsByAsset.get(assetName) !== sourceUrl) throw new Error(`Conflicting font asset name ${assetName} in ${source}`);
    sourceUrlsByAsset.set(assetName, sourceUrl);
  });
  return preparedFaces;
};
const validateWoff2 = (data, sourceUrl) => {
  if (data.length < 48 || data.subarray(0, 4).toString("ascii") !== "wOF2") throw new Error(`Invalid WOFF2 header from ${sourceUrl}`);
  if (data.readUInt32BE(8) !== data.length) throw new Error(`Invalid WOFF2 length from ${sourceUrl}`);
  if (!data.readUInt16BE(12) || data.readUInt16BE(14)) throw new Error(`Invalid WOFF2 table directory from ${sourceUrl}`);
  if (data.readUInt32BE(20) > data.length - 48) throw new Error(`Invalid WOFF2 compressed size from ${sourceUrl}`);
  [
    [data.readUInt32BE(28), data.readUInt32BE(32), "metadata"],
    [data.readUInt32BE(40), data.readUInt32BE(44), "private data"],
  ].forEach(([offset, length, label]) => {
    if ((offset && offset + length > data.length) || (!offset && length)) throw new Error(`Invalid WOFF2 ${label} bounds from ${sourceUrl}`);
  });
};
const downloadFont = (sourceUrl, redirectCount = 0) =>
  new Promise((resolve, reject) => {
    const request = https.get(sourceUrl, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        response.resume();
        if (redirectCount >= 5) return reject(new Error(`Too many redirects for ${sourceUrl}`));
        downloadFont(new URL(response.headers.location, sourceUrl).toString(), redirectCount + 1).then(resolve, reject);
        return;
      }
      if (response.statusCode !== 200) {
        response.resume();
        reject(new Error(`Unable to download ${sourceUrl}: ${response.statusCode}`));
        return;
      }
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => {
        const data = Buffer.concat(chunks);
        try {
          validateWoff2(data, sourceUrl);
        } catch (error) {
          reject(error);
          return;
        }
        resolve(data);
      });
    });
    request.on("error", reject);
  });
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
  const canonicalFonts = getCanonicalFonts();
  const preparedGroups = fontGroups.map((group) => resolveFontGroup(canonicalFonts, group)).map((group) => ({ ...group, faces: getFontFaces(group) }));
  const sourceUrls = new Set(preparedGroups.flatMap(({ faces }) => faces.map(({ sourceUrl }) => sourceUrl)));
  const downloads = await downloadFonts(sourceUrls);

  preparedGroups.forEach(({ faces, fontName, fontVariable, languages, source }) => {
    const css = [
      `/* Migaku UI default: ${fontName} */`,
      `/* Canonical variable: $${fontVariable} in packages/ui/src/styles/scss/_variables.scss. */`,
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
        getReferencedAssets(fs.readFileSync(fontsPath, "utf8")).forEach((asset) => {
          const assetPath = path.join(mediaDir, asset);
          if (fs.existsSync(assetPath)) fs.unlinkSync(assetPath);
        });
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
