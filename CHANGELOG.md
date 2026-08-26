## 0.6.5

### Patch Changes

- e72989f: Release downloads now use a stable version-only filename while local builds keep their date and time suffix for easy identification.

## 0.6.4

### Patch Changes

- 9e59465: Clear existing distribution artifacts before creating a new add-on build, and include the UTC build time in archive filenames.
- 9e59465: Release builds now use versioned, dated filenames so downloaded add-on archives are easy to identify.
- 9af73aa: Prevent intermittent Card Creator audio failures by isolating concurrent media conversions and recovering when the operating system removes temporary storage during a long-running Anki session.
- 9e59465: Keep English readings attached to their complete words when card text wraps.
- 9e59465: Keep the card customization controls from resizing when hovered in desktop Anki.
- 9e59465: Keep the card customization link visually stable when its hover emphasis appears.

## 0.6.3

### Patch Changes

- c6fd75e: Keep the See Translation control working when moving between review cards.

## 0.6.2

### Patch Changes

- eada272: Improve the See Translation control on AnkiDroid and other legacy card WebViews by using a more compatible show-and-remove interaction.
- 2d9f75a: Keep the audio button icons and playback indicator aligned in AnkiDroid and other legacy card WebViews.
- 1a5d510: Restrict the front-of-card customization control to desktop Anki; it is now hidden in AnkiDroid and AnkiMobile.
- 9c04491: Allow revealed translations to grow with multi-line content instead of clipping or scrolling inside a fixed-height slot.

## 0.6.1

### Patch Changes

- 436d005: Improve the Notes field presentation across supported card languages, including clearer spacing, alignment, contrast, and conditional rendering.

## 0.6.0

- [FEATURE] Redesign Migaku card visuals across supported languages
- [FEATURE] Add bundled offline fonts and refreshed media, audio, and card customization presentation
- [FEATURE] Improve light, dark, mobile, and AnkiDroid card layouts
- [FEATURE] Refresh the AnkiWeb add-on description and setup guide

## 0.5.2

- [FIX] Add spacing above new Notes field
- [FIX] Expose new Reading field in Field Maps

## 0.5.1

- [FEATURE] Save Migaku-generated Notes into the Notes field
- [FEATURE] Add Reading field for pronunciation guidance, pre-populated for CN, JA, EN, and a few other languages
- [FIX] Stop duplicating CN Sentence into Alternate Sentence field

## 0.5.0

- [FEATURE] Export detailed Anki card types and intervals to support KnownStatus mapping
- [FIX] Un-skip and export User Buried and Sched Buried cards to preserve word learning progress

## 0.4.0

- [FEATURE] Add Migaku > Export Debug Logs menu item
- [FIX] Add error popup on port connection issues
- [FIX] Fail gracefully when certain initialization errors occur
- [FIX] European language syntax parsing fixes
- [UPDATE] Support for Anki 25.09

## 0.3.5

- [FIX] Increase Qt6 compatibility
- [FIX] Use updated Anki methods
- [FIX] Send to Anki functionality from legacy extension

## 0.3.4

- [FIX] Increase timeout of generating descriptions request to 60s
- [FIX] Leaked file descriptors
- [FIX] Use SO_REUSEPORT if available
- [FEATURE] Add Migaku items to context menu for notes in browser

## 0.2.4

- [FEATURE] Endpoint for searching

## 0.2.3

- [FIX] Condensed audio error
- [FIX] Improved vacation group selector
- [FIX] Checkbox toggles on certain Qt versions
- [FEATURE] Option to remove/replace line breaks from sentences of new cards
- [FEATURE] Option to apply regex replacement for new cards
- [FEATURE] Card promotion interval factor

## 0.2.2

- [FEATURE] Support for native Apple silicon (M1) Anki versions

## 0.2.1

- [FIX] Allow incremental sync for balance scheduler card modifications
- [FIX] Syntax tools in card adding dialog

## 0.2.0

- [FEATURE] Support for Anki 2.1.50
- [FEATURE] Review balancing
- [FEATURE] Weekly schedule
- [FEATURE] Vacations
- [FEATURE] Audio normalizing
- [FEATURE] Advanced settings toggle
- [FIX] Consider nsbp in Japanese syntax parsing
- [FIX] Handle error when no field is associated to specific data type
