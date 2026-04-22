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
