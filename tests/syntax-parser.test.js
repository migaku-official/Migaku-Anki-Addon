/**
 * Unit tests for syntax parsing across different languages
 * Run with: node tests/syntax-parser.test.js
 */

// Test utilities
function assertEquals(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  if (actualStr !== expectedStr) {
    throw new Error(
      `${message}\nExpected: ${expectedStr}\nActual: ${actualStr}`,
    );
  }
}

function runTest(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    return true;
  } catch (error) {
    console.error(`✗ ${name}`);
    console.error(`  ${error.message}`);
    return false;
  }
}

// Parser implementations for European languages (Italian, French, Spanish, Portuguese, German)
function parseSyntaxEuropeanWithGender(text) {
  let ret = [];
  const syntax_re =
    /(?:\(([a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F']+?)\)|([a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F']+?))\[(.*?)\]/gm;
  let last_idx = 0;
  let match;

  do {
    match = syntax_re.exec(text);

    if (match) {
      if (match.index > last_idx) {
        ret.push({
          type: "plain",
          text: text.substring(last_idx, match.index),
        });
      }

      // Handle pipe-separated alternatives - use only the first one
      const metadata = match[3].split("|")[0];
      const args = metadata.split(",");
      const dict_form = args[0] || "";
      const word_pos = args[1] || "";
      const gender = args[2] || "x";

      ret.push({
        type: "syntax",
        text: match[1] || match[2], // match[1] for (word), match[2] for word
        dict_form: dict_form,
        word_pos: word_pos,
        gender: gender,
      });

      last_idx = match.index + match[0].length;
    }
  } while (match);

  if (last_idx < text.length) {
    ret.push({
      type: "plain",
      text: text.substr(last_idx),
    });
  }

  return ret;
}

// Parser for English and Vietnamese (with IPA instead of gender)
function parseSyntaxWithIPA(text) {
  let ret = [];
  const syntax_re =
    /(?:\(([a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F']+?)\)|([a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u024F']+?))\[(.*?)\]/gm;
  let last_idx = 0;
  let match;

  do {
    match = syntax_re.exec(text);

    if (match) {
      if (match.index > last_idx) {
        ret.push({
          type: "plain",
          text: text.substring(last_idx, match.index),
        });
      }

      // Handle pipe-separated alternatives - use only the first one
      const metadata = match[3].split("|")[0];
      const args = metadata.split(",");
      const dict_form = args[0] || "";
      const word_pos = args[1] || "";
      const ipa = (args[2] || "").split(";");
      if (ipa.length == 1 && ipa[0] == "") {
        ipa.pop();
      }

      ret.push({
        type: "syntax",
        text: match[1] || match[2], // match[1] for (word), match[2] for word
        dict_form: dict_form,
        word_pos: word_pos,
        ipa: ipa,
      });

      last_idx = match.index + match[0].length;
    }
  } while (match);

  if (last_idx < text.length) {
    ret.push({
      type: "plain",
      text: text.substr(last_idx),
    });
  }

  return ret;
}

// Test suite
console.log("Running syntax parser tests...\n");
let passed = 0;
let failed = 0;

// Italian tests
console.log("=== Italian / European Language Tests ===");

if (
  runTest("Italian: New format with parentheses and pipe alternatives", () => {
    const input =
      "(Ho)[avere,verb,m|havere,verb,m] (salutato)[salutare,verb,m]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result.length, 3, "Should parse into 3 elements");
    assertEquals(result[0].type, "syntax", "First element should be syntax");
    assertEquals(result[0].text, "Ho", "Should extract word from parentheses");
    assertEquals(result[0].dict_form, "avere", "Should use first alternative");
    assertEquals(result[0].word_pos, "verb", "Should extract POS");
    assertEquals(result[0].gender, "m", "Should extract gender");

    assertEquals(result[1].type, "plain", "Should have space between words");
    assertEquals(result[1].text, " ", "Should preserve space");

    assertEquals(result[2].text, "salutato", "Should extract second word");
  })
)
  passed++;
else failed++;

if (
  runTest("Italian: Old format without parentheses", () => {
    const input = "Ho[avere,verb,m] salutato[salutare,verb,m]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result.length, 3, "Should parse into 3 elements");
    assertEquals(
      result[0].text,
      "Ho",
      "Should extract word without parentheses",
    );
    assertEquals(result[0].dict_form, "avere", "Should extract lemma");
  })
)
  passed++;
else failed++;

if (
  runTest("Italian: Contractions with apostrophes", () => {
    const input = "(d')[di,adp]acqua";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result.length, 2, "Should parse into 2 elements");
    assertEquals(
      result[0].text,
      "d'",
      "Should handle apostrophe in contraction",
    );
    assertEquals(result[0].dict_form, "di", "Should extract preposition");
    assertEquals(result[0].word_pos, "adp", "Should identify as adposition");
    assertEquals(result[1].text, "acqua", "Should handle plain text after");
  })
)
  passed++;
else failed++;

if (
  runTest("Italian: Complex sentence with multiple forms", () => {
    const input =
      "(il)[il,art,m] (mio)[mio,det,m|mio,pron,m] (amico)[amico,noun,m|amico,adj,m|amicare,verb]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].text, "il", "Should parse article");
    assertEquals(result[2].text, "mio", "Should parse determiner");
    assertEquals(
      result[2].dict_form,
      "mio",
      "Should use first alternative for mio",
    );
    assertEquals(result[2].word_pos, "det", "Should use first POS");
    assertEquals(result[4].text, "amico", "Should parse noun");
    assertEquals(
      result[4].word_pos,
      "noun",
      "Should prefer noun over adjective/verb",
    );
  })
)
  passed++;
else failed++;

if (
  runTest("Italian: Mixed old and new format", () => {
    const input =
      "(Ho)[avere,verb] mangiato[mangiare,verb] (la)[il,art,f] pasta";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].text, "Ho", "Should parse new format");
    assertEquals(result[2].text, "mangiato", "Should parse old format");
    assertEquals(result[4].text, "la", "Should parse new format again");
    assertEquals(result[5].text, " pasta", "Should have plain text");
  })
)
  passed++;
else failed++;

if (
  runTest("Italian: Plain text without syntax", () => {
    const input = "Ciao mondo";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result.length, 1, "Should have single plain element");
    assertEquals(result[0].type, "plain", "Should be plain text");
    assertEquals(result[0].text, "Ciao mondo", "Should preserve text");
  })
)
  passed++;
else failed++;

// French tests
console.log("\n=== French Tests ===");

if (
  runTest("French: Contractions with apostrophes", () => {
    const input = "(l')[le,art,m]eau";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].text, "l'", "Should handle French elision");
    assertEquals(result[0].dict_form, "le", "Should extract article");
  })
)
  passed++;
else failed++;

if (
  runTest("French: Gender markers", () => {
    const input =
      "(le)[le,art,m] (chat)[chat,noun,m] (et)[et,conj] (la)[le,art,f] (maison)[maison,noun,f]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].gender, "m", "Should mark masculine article");
    assertEquals(result[6].gender, "f", "Should mark feminine article");
  })
)
  passed++;
else failed++;

// English tests
console.log("\n=== English Tests ===");

if (
  runTest("English: With IPA pronunciation", () => {
    const input = "(hello)[hello,intj,həˈloʊ] (world)[world,noun,wɜːld]";
    const result = parseSyntaxWithIPA(input);

    assertEquals(result[0].text, "hello", "Should extract word");
    assertEquals(result[0].ipa, ["həˈloʊ"], "Should extract IPA");
    assertEquals(result[2].ipa, ["wɜːld"], "Should extract second IPA");
  })
)
  passed++;
else failed++;

if (
  runTest("English: Multiple IPA alternatives", () => {
    const input = "(either)[either,det,ˈiːðə;ˈaɪðə]";
    const result = parseSyntaxWithIPA(input);

    assertEquals(result[0].ipa.length, 2, "Should have two IPA variants");
    assertEquals(result[0].ipa[0], "ˈiːðə", "First pronunciation");
    assertEquals(result[0].ipa[1], "ˈaɪðə", "Second pronunciation");
  })
)
  passed++;
else failed++;

if (
  runTest("English: Old format backward compatibility", () => {
    const input = "I[I,pron] am[be,verb]";
    const result = parseSyntaxWithIPA(input);

    assertEquals(result[0].text, "I", "Should parse old format");
    assertEquals(result[0].dict_form, "I", "Should extract pronoun");
    assertEquals(result[2].text, "am", "Should parse verb");
    assertEquals(result[2].dict_form, "be", "Should get infinitive");
  })
)
  passed++;
else failed++;

// Edge cases
console.log("\n=== Edge Cases ===");

if (
  runTest("Empty metadata", () => {
    const input = "(word)[]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].text, "word", "Should extract word");
    assertEquals(result[0].dict_form, "", "Should handle empty metadata");
    assertEquals(result[0].word_pos, "", "Should have empty POS");
    assertEquals(result[0].gender, "x", "Should default to x gender");
  })
)
  passed++;
else failed++;

if (
  runTest("Partial metadata", () => {
    const input = "(word)[lemma]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].dict_form, "lemma", "Should extract lemma");
    assertEquals(result[0].word_pos, "", "Should handle missing POS");
    assertEquals(result[0].gender, "x", "Should default gender");
  })
)
  passed++;
else failed++;

if (
  runTest("Only pipes (malformed alternatives)", () => {
    const input = "(word)[|||]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result[0].dict_form, "", "Should handle multiple pipes");
  })
)
  passed++;
else failed++;

if (
  runTest("Special characters in plain text", () => {
    const input = "Hello, world! How are you?";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(result.length, 1, "Should treat as plain text");
    assertEquals(
      result[0].text,
      "Hello, world! How are you?",
      "Should preserve punctuation",
    );
  })
)
  passed++;
else failed++;

if (
  runTest("Accented characters", () => {
    const input = "(café)[café,noun,m] (naïve)[naïve,adj]";
    const result = parseSyntaxEuropeanWithGender(input);

    assertEquals(
      result[0].text,
      "café",
      "Should handle accented chars in word",
    );
    assertEquals(
      result[0].dict_form,
      "café",
      "Should handle accented chars in metadata",
    );
    assertEquals(result[2].text, "naïve", "Should handle diaeresis");
  })
)
  passed++;
else failed++;

// Summary
console.log("\n" + "=".repeat(50));
console.log(`Tests completed: ${passed + failed}`);
console.log(`✓ Passed: ${passed}`);
console.log(`✗ Failed: ${failed}`);
console.log("=".repeat(50));

process.exit(failed > 0 ? 1 : 0);
