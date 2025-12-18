# Migaku Anki

Note: We renamed the pynput library to magicy in order to avoid Windows Real-time protection

## Docs

Some guidelines to work with this codebase:

For anything that uses the the server created by the Migaku-Anki-Addon, the main entrance can be seen as the MigakuConnection object in `migaku_connection/__init__.py`.
In there is a handlers objects, which has all the endpoints, and which class they call.

The most important one is the ("/anki-connect", MigakuConnector) endpoint, which establishes the WebSocket connection to
the Migaku Extension.

The the Migkau extension sends a card, the `receive_card` endpoint is called.

## Things that often break

- The `src/lib` folder contains dependencies, that are not included in Anki by default.
If the extension suddenly starts failing on newer Anki versions (especially on macOS), you might have to create a new folder like `macos_314`,
and add the new dependencies.

You'll also need to add the appropriate code in `sys_libraries.py` then, to load the new libraries on the right platform and Anki version.

- Support for new languages require adding a new folder in `src/languages` and modifying `src/languages/__init__.py` to include it.
