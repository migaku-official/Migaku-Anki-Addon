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
| Fixture | Sentence, vocabulary, audio, syntax showcase, or stress test |
| Theme | Light, Anki dark, or AnkiDroid dark |
| Theme toggle | Right-aligned moon/sun icon that switches directly between Light and Anki dark |
| Viewport | Responsive wide view, 768 px tablet, or 390 px mobile |
| Fields | Right-aligned list icon that opens a checklist for every standard note field |

Control state is stored in the page query string. A particular combination can therefore be bookmarked or shared with another developer running the lab. The icon-only Fields and theme controls use the locally installed Lucide package and stay grouped at the right edge of the toolbar. The theme button updates the same Theme control and query parameter, while the Theme select retains direct access to AnkiDroid dark mode.

Click non-interactive space inside the rendered card to toggle between front and back. The lab updates the Side control and query string. Links, audio, form controls, syntax words, and popups remain interactive without changing sides.

The toolbar and preview fill the browser viewport without page scrolling. The toolbar stays compact so the card receives the remaining height.

The Fields menu writes a `fields=configured` marker and one repeated `field`
query parameter per enabled field. The marker preserves the all-fields-off state.
Unchecking a field supplies an empty value to the shipped template, so real
Anki conditional rendering can be inspected without editing a fixture.

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

### Font defaults

Card fonts follow the component library defaults:

| Languages | Default |
| --- | --- |
| German, English, Spanish, French, Italian, Portuguese, Vietnamese | Inter |
| Japanese | Noto Sans JP |
| Korean | LINE Seed KR |
| Simplified Chinese | Noto Sans SC |
| Traditional Chinese | Noto Sans TC |
| Cantonese | Chiron Hei HK WS |

The committed `fonts.css` and `media/*.woff2` files are offline card artifacts. Refresh them from an adjacent component-library checkout with `node tools/import-card-fonts.js ../migaku-front-end`, then run `npm run build:card-styles`. The importer reads the canonical defaults from the component library's `_variables.scss`, selects the matching WOFF2 faces, validates their headers and bounds, rewrites them to the `cardFont` family, and gives every Anki media file a collision-resistant `_migaku-card-<font-source>-` prefix.

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

Audio fixture fields use Anki-style `[sound:filename]` values. The document
renderer converts those values into `.replay-button` controls backed by hidden
fixture audio and preview-only playback wiring. Clicking a replay button starts
its audio from the beginning; clicking the same button while it is playing
pauses and resets it. The lab therefore exercises the same audio-button selectors
as Anki without changing production templates.

On the back, Target Word and Sentence retain distinct semantic containers and
render at 46 px and 32 px respectively. The visual order is Target Word,
Sentence, a dedicated row containing both audio controls, translation, divider, definitions and supporting
content, then images and screenshot. The divider remains present when Sentence
is empty so vocabulary and audio-vocabulary backs keep the same section boundary.
Inline `<t>` elements supplied by Anki fields render with bold font weight so
target-word emphasis survives inside sentences.

Translation starts hidden behind a `See Translation` button. Activating it
reveals the translation and removes the one-time button. The card-type controls
also start hidden. The half-opacity `Change card type` button remains in place,
changes its text to `Dismiss`, and reveals a panel beneath it. The panel contains
two left-aligned on/off controls beneath a `Card type` heading: Sentence/Vocab
selects the card content and Audio card selects its audio variant. The controls
share one row when space permits and stack on narrow cards. Together they
preserve the four existing `s`, `v`, `as`, and `av` states. Switch changes
continue to send the existing
`update_card_type` command through `pycmd`. The production script hides that
entry point when `pycmd` is absent.
Both card-type controls are anchored to the production card shell, so their
absolute position follows the actual card height rather than the preview viewport.
The layout retains extra bottom padding beyond the card-height calculation so
both the collapsed Change card type button and the expanded switch panel always
have comfortable scroll runway beneath them.

## Fixtures

Fixtures are defined in `dev/card-preview/fixtures.js`. Every language supplies
its own annotated sentence, target word, and translation using the formats in
the [Migaku syntax reference guide](https://magenta-dirigible-0d8.notion.site/Syntax-reference-guide-2a55f4eb6327491ca80792e3a935d07a).
Changing the lab language therefore exercises that language's parser, coloring,
and popup metadata rather than reusing English content.

Every fixture also receives the same lab-only target-word audio, sentence audio,
and Vegeta screenshot from `dev/card-preview/media/`. The preview server exposes
these through `/fixture-media/`; they are regression assets and are not installed
as production note-type media.

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
| `tests/card-fonts.test.js` | Component-library font mapping, offline WOFF2 completeness, media naming, and generated-style parity |
| `node tools/card-styles.js --check` | Every committed language stylesheet matches its compiler inputs |
| `tests/card-preview.test.js` | Template fields and nested section semantics |
| `tests/card-template-contract.test.js` | Approved hashes for all functional card HTML |
| `tests/card-fixtures.test.js` | Language-specific sentence and target-word syntax |
| `tests/card-document.test.js` | Composition of real assets into front/back documents |
| `tests/card-cosmetics.test.js` | Shared light/dark surface and layout tokens in rendered cards |
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

1. Add its production card directory, templates, and supporting assets.
2. Add its component-library font mapping to `fontGroups` in
   `tools/import-card-fonts.js`.
3. Add its expected asset count to `expectedAssetCounts` in
   `tests/card-fonts.test.js`.
4. Run `node tools/import-card-fonts.js ../migaku-front-end`.
5. Add its language code to `template-contract.json`.
6. Add its annotated sentence, target word, and translation to `syntaxProfiles`
   in `dev/card-preview/fixtures.js`.
7. Add approved hashes for its functional templates.
8. Run `npm run build:card-styles`.
9. Verify that it appears in the lab language selector and that the syntax
   showcase renders its word coloring and popup metadata.
10. Run the full regression suite.

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
- Run `node tests/card-fonts.test.js` to catch missing, remote, stale, or invalid font media.
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
