const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const contract = require("./template-contract.json");

const getExpectedHash = (fileName, language) => {
  const fileContract = contract.hashes[fileName];
  return (fileContract.overrides && fileContract.overrides[language]) || fileContract.default;
};

const hashFile = (filePath) =>
  crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");

const getTemplateHashes = (rootDir) =>
  Object.fromEntries(
    contract.languages.map((language) => [
      language,
      Object.fromEntries(
        Object.keys(contract.hashes).map((fileName) => [
          fileName,
          hashFile(path.join(rootDir, "src", "languages", language, "card", fileName)),
        ]),
      ),
    ]),
  );

const verifyTemplateContract = (rootDir) => {
  const fileNames = Object.keys(contract.hashes);
  const files = contract.languages.flatMap((language) =>
    fileNames.map((fileName) => ({ fileName, language })),
  );
  const hashes = getTemplateHashes(rootDir);

  files.forEach(({ fileName, language }) => {
    const relativePath = path.join("src", "languages", language, "card", fileName);
    const actualHash = hashes[language][fileName];
    const expectedHash = getExpectedHash(fileName, language);
    if (actualHash !== expectedHash)
      throw new Error(
        `${relativePath} changed outside the protected card template contract.\nExpected: ${expectedHash}\nActual:   ${actualHash}`,
      );
  });

  return {
    filesChecked: files.length,
    languagesChecked: contract.languages.length,
  };
};

module.exports = { getTemplateHashes, verifyTemplateContract };
