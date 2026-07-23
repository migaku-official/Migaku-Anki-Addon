const assert = require("assert");
const path = require("path");

const { verifyTemplateContract } = require("../dev/card-preview/template-contract");

const result = verifyTemplateContract(path.resolve(__dirname, ".."));

assert.deepStrictEqual(result, {
  filesChecked: 36,
  languagesChecked: 12,
});

console.log("✓ card templates match the protected contract");
