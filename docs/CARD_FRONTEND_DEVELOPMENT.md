# Card Front-end Development

This guide explains how to make cosmetic changes to Migaku note-type cards while preserving their field logic, conditionals, support JavaScript, and Anki integration.

## Goals

The workflow is designed to support aggressive visual changes with conservative functional boundaries:

- Iterate on the real language-specific CSS with automatic reload.
- Preview the shipped front and back templates.
- Check multiple languages, card types, themes, and viewport widths.
- Detect accidental changes to functional template files.
- Keep the browser preview separate from production runtime code.

It is not intended to reproduce Anki's scheduler, reviewer controls, editor, audio substitution, or every WebView difference.

## Start the lab

From the repository root:

```bash
npm run dev:cards
```

Open [http://127.0.0.1:4173](http://127.0.0.1:4173).

Set a different port when `4173` is already occupied:

```bash
CARD_PREVIEW_PORT=4174 npm run dev:cards
```

The server binds to `127.0.0.1`, so the lab is available only on the local machine.

Starting the lab compiles the shared card stylesheet. While it runs, saving the
shared CSS or a language font source rebuilds the generated language stylesheets
before the preview reloads.

## Controls

The toolbar changes the preview URL and rerenders the iframe:

| Control | States |
| --- | --- |
| Language | Every language listed in `template-contract.json` |
| Side | Front or back |
| Fixture | Sentence, vocabulary, audio, or stress test |
| Theme | Light, Anki dark, or AnkiDroid dark |
| Viewport | Responsive wide view, 768 px tablet, or 390 px mobile |

Control state is stored in the page query string. A particular combination can therefore be bookmarked or shared with another developer running the lab.

## What to edit

Shared card styling lives at:

```text
src/card-styles/global.css
```

For a cosmetic-only change:

- Make global cosmetic changes in `src/card-styles/global.css`.
- Change `src/languages/<language>/card/fonts.css` only for language-specific
  font declarations.
- Treat `src/languages/<language>/card/styles.css` as generated output; do not
  edit it directly.
- Change `support.css` only when the language-support presentation also needs work.
- Add or replace files in `media/` only when the CSS or existing templates reference them correctly.
- Do not change `front.html`, `back.html`, or `support.html`.

The lab watches `src/card-styles/`, every language card directory, and
`dev/card-preview/`. Saving a watched file compiles stale stylesheets, then sends
a server-sent `reload` event to the lab. The current iframe reloads without
restarting the server.

Run the compiler without the lab when needed:

```bash
npm run build:card-styles
```

`src/card-styles/legacy-variants.json` records the small pre-existing differences
required to reproduce the old language stylesheets byte-for-byte. It is a
compatibility input, not the normal place for cosmetic work.

## Production parity

`card-document.js` reads these files on every preview request:

1. The selected language's `front.html`.
2. The selected language's `back.html`.
3. `styles.css`.
4. `support.css`.
5. `support.html`.

The selected fixture supplies note fields. The lightweight renderer resolves the subset of Anki template syntax used by these cards:

- Normal fields such as `{{Sentence}}`.
- Filtered fields such as `{{editable:Sentence}}`.
- Truthy sections such as `{{#Sentence}}...{{/Sentence}}`.
- Inverted sections such as `{{^Is Audio Card}}...{{/Is Audio Card}}`.
- Nested sections.

The rendered card is placed inside a small Anki-like document containing `main.container`, `#qa`, `#content`, and the appropriate body classes for the selected theme.

The document also provides a preview-only no-op `pycmd` bridge. This keeps
Anki-gated presentation such as the back-side card-type switcher visible without
sending commands or changing card data.

## Fixtures

Fixtures are defined in `dev/card-preview/fixtures.js`. Every language supplies
its own annotated sentence, target word, and translation using the formats in
the [Migaku syntax reference guide](https://magenta-dirigible-0d8.notion.site/Syntax-reference-guide-2a55f4eb6327491ca80792e3a935d07a).
Changing the lab language therefore exercises that language's parser, coloring,
and popup metadata rather than reusing English content.

### Sentence

A content-rich sentence card with translation, definitions, examples, notes, audio controls, screenshot, and supporting image.

### Vocabulary

A vocabulary-card state that exercises target-word and word-audio branches.

### Audio

An audio-card state that exercises the audio-first conditional branch with deliberately sparse supporting fields.

### Syntax showcase

A focused annotated sentence and target word for checking dictionary forms,
parts of speech, gender colors, IPA, readings, tones, pitch accents, and popup
layout. Use this fixture first when changing `.word` or `.popup` styles.

### Stress test

Long multilingual text, unbroken strings, repeated definitions, multiple images, and oversized content. Use this fixture to find:

- Horizontal overflow.
- Broken word wrapping.
- Excessive fixed heights.
- Image overflow.
- Poor narrow-screen spacing.
- Dark-mode contrast failures.

When a visual bug depends on a new content shape, add a named fixture rather than embedding preview-only markup into production templates.

## Recommended CSS loop

1. Start the lab and edit `src/card-styles/global.css`.
2. Start with the sentence fixture on the front and back.
3. Check the syntax showcase for coloring and popups.
4. Check the vocabulary and audio branches.
5. Check the stress fixture at 390 px.
6. Check both dark themes.
7. Repeat the matrix for languages with different font assets, especially Japanese, Korean, Simplified Chinese, Traditional Chinese, and Cantonese.
8. Run the complete regression suite.
9. Validate representative cards inside desktop Anki and AnkiDroid.

The lab is optimized for fast discovery. Real Anki validation remains the release gate.

## Regression tests

Run:

```bash
npm test
```

The card-specific suites are:

| Test | Protected behavior |
| --- | --- |
| `tests/card-styles.test.js` | Shared-style compilation, generated output, and freshness detection |
| `node tools/card-styles.js --check` | Every committed language stylesheet matches its compiler inputs |
| `tests/card-preview.test.js` | Template fields and nested section semantics |
| `tests/card-template-contract.test.js` | Approved hashes for all functional card HTML |
| `tests/card-fixtures.test.js` | Language-specific sentence and target-word syntax |
| `tests/card-document.test.js` | Composition of real assets into front/back documents |
| `tests/card-preview-server.test.js` | Lab shell, preview route, state parameters, and invalid-input responses |

`run-tests.sh` invokes the same complete npm test command. The pre-push workflow can therefore continue using the repository's shell runner.

## Template contract policy

The contract covers every language's:

- `front.html`
- `back.html`
- `support.html`

The expected hashes live in `dev/card-preview/template-contract.json`.

For a cosmetic pull request, a contract failure is a hard failure. Revert the functional file instead of updating the hash.

Only update a hash when the task explicitly includes a reviewed behavior change. In that case:

1. Separate the behavior change from cosmetic CSS commits.
2. Explain the changed field, conditional, structure, or JavaScript behavior.
3. Test all affected card branches in the lab.
4. Test the behavior inside Anki.
5. Update only the affected approved hashes.
6. Commit the contract update with the behavior change.

Never regenerate or accept every hash merely to make the suite green.

## Adding a language

When adding a language:

1. Add its production card directory and assets.
2. Add `card/fonts.css` with the language's `@font-face` declarations.
3. Add its language code to `template-contract.json`.
4. Add approved hashes for its functional templates.
5. Run `npm run build:card-styles`.
6. Verify that it appears in the lab language selector.
7. Run the full regression suite.

The preview server derives its language options and watched card directories from the contract language list.

## Troubleshooting

### The preview does not reload

- Confirm the server process is still running.
- Confirm the edited file is under `src/card-styles/`,
  `src/languages/<language>/card/`, or `dev/card-preview/`.
- Refresh the lab page once to recreate the event stream.
- Check whether another process is replacing files through a path outside the watched directory.

### A font or image is missing

- Confirm the asset exists in a language's `card/media/` directory.
- Use the exact filename referenced by the CSS or template.
- Remember that Anki media filenames are effectively global within a collection.
- Verify the same asset inside Anki before release.

### The lab and Anki differ

Check whether the difference comes from:

- Anki reviewer DOM or body classes.
- Desktop Anki versus Android WebView behavior.
- Anki's audio replacement.
- Existing customized note types that were not reset from repository assets.
- Collection media that differs from the repository.

Document intentional platform exceptions in the CSS near the relevant selector.

## Definition of done

A cosmetic card change is complete when:

- Functional template hashes remain unchanged.
- Generated language stylesheets are current.
- Front and back render correctly.
- Sentence, vocabulary, audio, and stress fixtures remain usable.
- Light, Anki dark, and AnkiDroid dark modes have adequate contrast.
- Wide and narrow layouts do not overflow unexpectedly.
- The complete automated suite passes.
- Representative cards are verified in desktop Anki and AnkiDroid.
