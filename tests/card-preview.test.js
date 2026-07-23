const assert = require("assert");

const { renderTemplate } = require("../dev/card-preview/template-engine");

const fields = {
  Sentence: "A real sentence",
  Translation: "A real translation",
  Empty: "",
};

assert.strictEqual(
  renderTemplate(
    "{{#Sentence}}<p>{{editable:Sentence}}</p>{{/Sentence}}{{^Empty}}<small>{{Translation}}</small>{{/Empty}}",
    fields,
  ),
  "<p>A real sentence</p><small>A real translation</small>",
);

assert.strictEqual(
  renderTemplate(
    "{{#Empty}}hidden{{/Empty}}{{^Sentence}}hidden{{/Sentence}}{{#Sentence}}{{^Empty}}shown{{/Empty}}{{/Sentence}}",
    fields,
  ),
  "shown",
);

console.log("✓ card preview template renderer");
