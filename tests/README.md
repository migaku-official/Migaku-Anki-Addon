# Migaku Anki Add-on Tests

## Overview

This directory contains unit tests for the Migaku Anki Add-on, focusing on syntax parsing functionality across different languages.

## Running Tests

### Prerequisites

- Node.js (v14 or higher)

### Run All Tests

```bash
node tests/syntax-parser.test.js
```

## Test Coverage

### Syntax Parser Tests (`syntax-parser.test.js`)

Tests the card syntax parsing functionality for multiple languages:

#### Italian / European Languages (Italian, French, Spanish, Portuguese, German)
- ✓ New format with parentheses and pipe alternatives: `(word)[lemma,pos,gender|alt1,pos,gender]`
- ✓ Old format without parentheses: `word[lemma,pos,gender]`
- ✓ Contractions with apostrophes: `(d')[di,adp]`
- ✓ Complex sentences with multiple forms and alternatives
- ✓ Mixed old and new format in same sentence
- ✓ Plain text without syntax markers

#### French Specific
- ✓ Elision with apostrophes: `(l')[le,art,m]`
- ✓ Gender markers (masculine/feminine)

#### English / Vietnamese
- ✓ IPA pronunciation data: `(word)[lemma,pos,IPA]`
- ✓ Multiple IPA alternatives separated by semicolons
- ✓ Backward compatibility with old format

#### Edge Cases
- ✓ Empty metadata
- ✓ Partial metadata (missing fields)
- ✓ Malformed alternatives (multiple pipes)
- ✓ Special characters and punctuation in plain text
- ✓ Accented characters (café, naïve, etc.)

## Test Format

Each test validates specific parsing scenarios and ensures:
1. Correct extraction of words (with or without parentheses)
2. Proper handling of metadata (lemma, part of speech, gender/IPA)
3. Support for pipe-separated alternatives (using first option)
4. Backward compatibility with old syntax format
5. Proper handling of apostrophes and contractions
6. Preservation of plain text and spacing

## Adding New Tests

To add new test cases, follow this pattern:

```javascript
if (runTest('Test description', () => {
    const input = 'your test input';
    const result = parseSyntaxEuropeanWithGender(input);
    
    assertEquals(result[0].text, 'expected', 'assertion message');
    assertEquals(result[0].dict_form, 'expected_lemma', 'assertion message');
})) passed++; else failed++;
```

## Continuous Integration

Consider adding these tests to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: node tests/syntax-parser.test.js
```

## Related Files

The syntax parsing logic tested here is implemented in:
- `/src/languages/it/card/support.html` (Italian)
- `/src/languages/fr/card/support.html` (French)
- `/src/languages/es/card/support.html` (Spanish)
- `/src/languages/pt/card/support.html` (Portuguese)
- `/src/languages/de/card/support.html` (German)
- `/src/languages/en/card/support.html` (English)
- `/src/languages/vi/card/support.html` (Vietnamese)
