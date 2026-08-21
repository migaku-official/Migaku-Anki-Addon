const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const packageJson = JSON.parse(fs.readFileSync(path.join(repoRoot, "package.json"), "utf8"));
const description = fs.readFileSync(path.join(repoRoot, "ankiweb.html"), "utf8");
const releaseAssetUrls = description.match(
  /https:\/\/raw\.githubusercontent\.com\/migaku-official\/Migaku-Anki-Addon\/[^/]+\/docs\/assets\//g,
) || [];

assert.match(packageJson.version, /^\d+\.\d+\.\d+$/);
assert.ok(releaseAssetUrls.length > 0);
assert.ok(releaseAssetUrls.every((url) => url.endsWith(`/${packageJson.version}/docs/assets/`)));

console.log("✓ release metadata uses one package version across AnkiWeb asset URLs");
