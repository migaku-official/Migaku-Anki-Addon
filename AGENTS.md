## Documentation

- Read `docs/ARCHITECTURE.md` before changing runtime boundaries, note-type installation, card asset delivery, or dependencies between production and development code.
- Read `docs/CARD_FRONTEND_DEVELOPMENT.md` before changing note-type card HTML, CSS, support assets, preview tooling, fixtures, or card regression tests.
- Keep those documents synchronized when the corresponding architecture or workflow changes.

## AnkiWeb description preview

- Treat `ankiweb.html` as the canonical AnkiWeb add-on description. Make all published description content changes there.
- `ankiweb-realistic-preview.html` is an adjacent development-only shell that approximates the AnkiWeb add-on page and fetches `ankiweb.html` at runtime. It must consume the canonical file; never copy the description markup into the preview.
- Serve the repository over HTTP and open `ankiweb-realistic-preview.html` to review description changes. Opening the preview directly from the filesystem will prevent it from fetching `ankiweb.html`.
- Change `ankiweb-realistic-preview.html` only when the preview shell itself needs to better match AnkiWeb.

## Card front-end safety contract

- Treat `src/card-styles/global.css`, language `card/fonts.css` files, and
  `src/languages/<language>/card/` as production sources. Do not create or
  maintain preview-only copies of production templates or styles.
- For cosmetic-only work, do not change `front.html`, `back.html`, or `support.html`.
- A cosmetic-first release may include explicitly reviewed functional template or
  media migrations. Keep each accepted behavior change documented in
  `docs/ARCHITECTURE.md`, cover it with focused regression tests, and update only
  the affected template hashes. The accepted result becomes the protected
  baseline for subsequent cosmetic-only work.
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
