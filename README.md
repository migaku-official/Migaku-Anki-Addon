# Migaku Anki

Note: We renamed the pynput library to magicy in order to avoid Windows Real-time protection

## Docs

Some guidelines to work with this codebase:

For anything that uses the server created by the Migaku-Anki-Addon, the main entrance can be seen as the MigakuConnection object in `migaku_connection/__init__.py`.
In there is a handlers objects, which has all the endpoints, and which class they call.

The most important one is the ("/anki-connect", MigakuConnector) endpoint, which establishes the WebSocket connection to
the Migaku Extension.

The the Migkau extension sends a card, the `receive_card` endpoint is called.

## Development Setup

### Running the Add-on in Development Mode

To develop and test changes to the add-on locally, you can create a symlink to avoid copying files repeatedly.

#### Find Your Anki Add-ons Folder

**Mac:**

```bash
~/Library/Application Support/Anki2/addons21/
```

**Windows:**

```bash
%APPDATA%\Anki2\addons21\
```

**Linux:**

```bash
~/.local/share/Anki2/addons21/
```

#### Create a Development Symlink

**Important:** Remove the production add-on folder entirely (don't just rename it). Anki will process any folder in the addons directory, including backups.

**Mac/Linux:**

```bash
# Navigate to the addons folder
cd ~/Library/Application\ Support/Anki2/addons21/  # Mac
# or
cd ~/.local/share/Anki2/addons21/  # Linux

# Move the production add-on OUT of the addons folder entirely
mv 1846879528 ~/Desktop/1846879528.backup

# Create a symlink using the addon ID
# Replace /path/to/your/repo with your actual repo location
ln -s /path/to/your/repo/Migaku-Anki-Addon/src 1846879528
```

**Windows (Command Prompt as Administrator):**

```cmd
# Navigate to the addons folder
cd %APPDATA%\Anki2\addons21\

# Move the production add-on OUT of the addons folder entirely
move 1846879528 %USERPROFILE%\Desktop\1846879528.backup

# Create a symlink using the addon ID
# Replace C:\path\to\your\repo with your actual repo location
mklink /D 1846879528 C:\path\to\your\repo\Migaku-Anki-Addon\src
```

#### Enable Debug Logging

For better error visibility during development, you can run Anki from the terminal:

**Mac:**

```bash
/Applications/Anki.app/Contents/MacOS/launcher
```

**Windows:**

```cmd
# If Anki is in Program Files
"C:\Program Files\Anki\anki.exe"
```

**Linux:**

```bash
anki
```

**Logging**
You can also enable more verbose logging by adding this to the top of `src/__init__.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will output debug messages to the console when running Anki from the terminal.

#### Testing Changes

1. Make your code changes in the repository
2. Restart Anki to load the changes (no build step required)
3. Check the console output for logs and errors
4. Verify the add-on functionality

**Note:** Python changes are loaded directly by Anki - no compilation or build step is needed.

## Things that often break

- The `src/lib` folder contains dependencies, that are not included in Anki by default.
  If the extension suddenly starts failing on newer Anki versions (especially on macOS), you might have to create a new folder like `macos_314`,
  and add the new dependencies.

You'll also need to add the appropriate code in `sys_libraries.py` then, to load the new libraries on the right platform and Anki version.

- Support for new languages require adding a new folder in `src/languages` and modifying `src/languages/__init__.py` to include it.

## Ankiweb User Guide

Check out [here](./ankiweb.html).
