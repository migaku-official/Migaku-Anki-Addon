## Documentation

- Read `docs/ARCHITECTURE.md` before changing runtime boundaries, note-type installation, card asset delivery, or dependencies between production and development code.
- Read `docs/CARD_FRONTEND_DEVELOPMENT.md` before changing note-type card HTML, CSS, support assets, preview tooling, fixtures, or card regression tests.
- Keep those documents synchronized when the corresponding architecture or workflow changes.

## Card front-end safety contract

- Treat `src/card-styles/global.css`, language `card/fonts.css` files, and
  `src/languages/<language>/card/` as production sources. Do not create or
  maintain preview-only copies of production templates or styles.
- For cosmetic-only work, do not change `front.html`, `back.html`, or `support.html`.
- `src/card-styles/global.css` is the primary cosmetic surface.
  Per-language `styles.css` files are generated; never edit them directly.
  Treat `support.css` as behavior-adjacent because its selectors may affect
  readings, popups, visibility, or hit targets.
- Preserve existing classes, field expressions, conditionals, data attributes, media filenames, and JavaScript behavior unless the task explicitly includes a functional change.
- Use the Card Front-end Lab through the `dev:cards` npm script to exercise front/back, languages, fixtures, themes, and viewport widths.
- Run `npm run build:card-styles` when working without the lab. The lab rebuilds
  stale styles automatically.
- Run the complete npm test suite before committing card-related work.
- A card template contract failure is a hard failure for cosmetic work. Revert the functional template change; do not update approved hashes.
- Update `dev/card-preview/template-contract.json` only for an explicitly authorized functional change that has been reviewed and verified inside Anki.
- Browser previews are not a substitute for final validation in desktop Anki and AnkiDroid.
