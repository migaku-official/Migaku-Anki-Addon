# Architecture

This document describes the major runtime boundaries in the Migaku Anki add-on and how note-type card assets move from this repository into Anki. It focuses on the parts contributors need to understand before changing card presentation or behavior.

## Repository map

| Path | Responsibility |
| --- | --- |
| `src/__init__.py` | Add-on initialization and Anki hook registration |
| `src/migaku_connection/` | HTTP and WebSocket integration with other Migaku clients |
| `src/note_type_mgr.py` | Creates, updates, and identifies Migaku note types |
| `src/languages/` | Language definitions and language-specific card assets |
| `src/editor/` | Anki editor integration |
| `src/menu/` | Add-on menu actions and supporting UI |
| `src/lib/` | Dependencies bundled with the add-on |
| `dev/card-preview/` | Development-only card rendering and live-preview tooling |
| `tests/` | Node-based regression tests for parsers and card tooling |

Production code is loaded directly from `src/` by Anki. The `dev/` and `tests/` directories are development infrastructure and are not part of card execution inside Anki.

## Runtime overview

Anki loads the add-on through `src/__init__.py`. Initialization registers hooks and connects the add-on's feature modules to Anki. The connection layer exposes handlers used by Migaku clients, while feature modules operate on Anki notes, cards, editors, and reviewer state.

The main integration entry point for external Migaku clients is `MigakuConnection` in `src/migaku_connection/__init__.py`. Its handlers include the `/anki-connect` WebSocket endpoint used by the Migaku Extension.

## Note-type asset pipeline

Every supported language owns a card asset directory:

```text
src/languages/<language>/card/
├── front.html
├── back.html
├── styles.css
├── support.html
├── support.css
└── media/
```

The production flow is:

```text
language card source files
          |
          v
src/note_type_mgr.py
          |
          +--> front.html   -> Anki template qfmt
          +--> back.html    -> Anki template afmt
          +--> styles.css   -> Anki note-type CSS
          +--> support.*    -> language support injected into the template/CSS
          +--> media/*      -> Anki collection media
          |
          v
Anki reviewer and previewer
```

`nt_update()` is the main synchronization boundary. For reserved base note types such as `Migaku Japanese`, it ensures required fields exist, resets the standard front/back templates from the repository, replaces the main stylesheet, appends language support, and copies card media into the collection.

Custom note types are cloned from a base note type. Their user-controlled template content is preserved where possible, while language support can still be reapplied. This distinction matters: changing repository card assets immediately changes newly installed or updated base note types, but does not imply that every customized note type will become visually identical.

## Card behavior contract

Card functionality is distributed across several asset types:

| Asset | Intended responsibility | Cosmetic-only policy |
| --- | --- | --- |
| `front.html` | Front-side field selection, conditionals, structure, and classes | Protected; do not change |
| `back.html` | Back-side field selection, conditionals, structure, and classes | Protected; do not change |
| `support.html` | Language-specific browser-side behavior | Protected; do not change |
| `styles.css` | Main layout and visual presentation | Freely editable |
| `support.css` | Presentation required by language support features | Editable with extra care |
| `media/` | Fonts, logos, images, and other referenced card assets | Filenames and references are contractual |

The contract tests hash every shipped `front.html`, `back.html`, and `support.html`. A cosmetic change should never require updating those hashes.

`support.css` is CSS, but some of its selectors may control the presentation of interactive language support such as readings or popups. Treat it as behavior-adjacent: visual changes are allowed, but visibility, hit targets, and state selectors must remain functional.

## Card Front-end Lab

The Card Front-end Lab is an isolated development surface under `dev/card-preview/`. It reads the production card assets directly; there is no copied preview template or generated stylesheet.

```text
production card files
          |
          v
card-document.js ---- fixtures.js
          |                |
          +------> template-engine.js
                           |
                           v
                    preview HTML document
                           |
                           v
                      server.js iframe
```

The components have narrow responsibilities:

| Component | Responsibility |
| --- | --- |
| `template-engine.js` | Resolves Anki-style field substitutions and section conditionals needed by the fixtures |
| `fixtures.js` | Supplies representative sentence, vocabulary, audio, and stress-test field data |
| `card-document.js` | Reads real card assets and produces a standalone preview document |
| `server.js` | Serves the lab UI, preview route, media, and live-reload events |
| `template-contract.js` | Verifies protected template files against approved hashes |
| `template-contract.json` | Stores the language list and approved template hashes |

The preview renderer is intentionally not a complete Anki emulator. It provides the DOM and visual states needed for CSS work, but final validation must still happen in Anki because the reviewer, scheduler, WebView, audio replacement, and platform integrations belong to Anki.

## Development dependency direction

Development tooling may depend on production card files:

```text
dev/card-preview -> src/languages/*/card
tests            -> dev/card-preview
tests            -> src/languages/*/card
```

Production code must not depend on `dev/` or `tests/`. This keeps the preview lab removable and prevents Node-only infrastructure from leaking into the Anki runtime.

## Regression layers

The card workflow is protected at four seams:

1. Template engine behavior: field substitution and nested conditionals.
2. Template contract: all shipped functional HTML files match approved hashes.
3. Document rendering: real front/back files, CSS, support assets, and fixtures compose successfully.
4. HTTP workflow: the lab shell and preview route expose valid development states and errors.

The existing syntax-parser suite remains part of the same top-level test command.

## Architectural rules for cosmetic changes

- Keep production HTML and JavaScript unchanged.
- Use existing card classes as the styling API.
- Make production CSS files the source of truth.
- Do not add a second set of preview-only styles.
- Exercise light, Anki dark, and AnkiDroid dark themes.
- Exercise both normal content and pathological overflow content.
- Keep media references compatible with Anki collection media.
- Run the complete regression suite before committing.
- Validate the final result inside desktop Anki and AnkiDroid.

For the operating workflow, see [Card Front-end Development](CARD_FRONTEND_DEVELOPMENT.md).
