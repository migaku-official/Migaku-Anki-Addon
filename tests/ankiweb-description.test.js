const assert = require("assert");
const fs = require("fs");
const path = require("path");

const description = fs.readFileSync(path.join(__dirname, "..", "ankiweb.html"), "utf8");
const imageTags = description.match(/<img\b[^>]*>/g) || [];
const releaseAssetUrl = /^https:\/\/raw\.githubusercontent\.com\/migaku-official\/Migaku-Anki-Addon\/[^/]+\/docs\/assets\//;

assert.ok(imageTags.length > 0, "AnkiWeb description should contain images");
imageTags.forEach((tag) => {
  const source = tag.match(/\bsrc="([^"]+)"/);
  const width = tag.match(/\bwidth="([1-9]\d*)"/);
  assert.ok(source, `AnkiWeb image is missing src: ${tag}`);
  assert.ok(width, `AnkiWeb image needs an intrinsic width because style attributes are stripped: ${source[1]}`);
  assert.match(source[1], releaseAssetUrl, `AnkiWeb image must use an absolute release asset URL: ${source[1]}`);
});
assert.doesNotMatch(description, /\bsrc="docs\/assets\//, "AnkiWeb cannot resolve repository-relative image URLs");
assert.doesNotMatch(description, /\s(?:class|id|style)="/, "AnkiWeb strips class, id, and style attributes");
assert.doesNotMatch(description, /<(?:script|style)\b/i, "AnkiWeb descriptions cannot depend on scripts or style blocks");

console.log("✓ AnkiWeb description uses sanitizer-safe HTML and public release image URLs");
