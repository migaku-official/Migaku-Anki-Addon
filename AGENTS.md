- When giving the user commands to copy/paste, use the `scratchpad` skill to put them in a root session file.

## Documentation

- Read `docs/ARCHITECTURE.md` before changing runtime boundaries, note-type installation, card asset delivery, or dependencies between production and development code.
- Read `docs/CARD_FRONTEND_DEVELOPMENT.md` before changing note-type card HTML, CSS, support assets, preview tooling, fixtures, or card regression tests.
- Keep those documents synchronized when the corresponding architecture or workflow changes.

## Card front-end safety contract

- Treat `src/languages/<language>/card/` as the production source of truth. Do not create or maintain preview-only copies of production templates or styles.
- For cosmetic-only work, do not change `front.html`, `back.html`, or `support.html`.
- `styles.css` is the primary cosmetic surface. Treat `support.css` as behavior-adjacent because its selectors may affect readings, popups, visibility, or hit targets.
- Preserve existing classes, field expressions, conditionals, data attributes, media filenames, and JavaScript behavior unless the task explicitly includes a functional change.
- Use the Card Front-end Lab through the `dev:cards` npm script to exercise front/back, languages, fixtures, themes, and viewport widths.
- Run the complete npm test suite before committing card-related work.
- A card template contract failure is a hard failure for cosmetic work. Revert the functional template change; do not update approved hashes.
- Update `dev/card-preview/template-contract.json` only for an explicitly authorized functional change that has been reviewed and verified inside Anki.
- Browser previews are not a substitute for final validation in desktop Anki and AnkiDroid.
