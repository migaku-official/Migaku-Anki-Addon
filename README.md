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

## Release Process

### Creating a New Release

1. **Update version and changelog:**
   - Update `CHANGELOG.md` with the new version number and changes
   - Commit the changes to your feature branch

2. **Merge to master:**
   ```bash
   git checkout master
   git pull origin master
   git merge your-feature-branch
   git push origin master
   ```

3. **Create and push a tag:**
   ```bash
   git tag 0.4.0  # Use the new version number
   git push origin 0.4.0
   ```

4. **GitHub Actions will automatically:**
   - Build the `.ankiaddon` file
   - Set the version in `src/version.py`
   - Create a GitHub release
   - Attach the built file to the release

### QA Testing a Release Candidate

**Step 1: Download the Test Build**
1. Go to https://github.com/migaku-official/Migaku-Anki-Addon/releases
2. Find the release version (e.g., 0.4.0)
3. Download `Migaku.ankiaddon`

**Step 2: Backup Current Production Version**

⚠️ **Important: Close Anki first before proceeding!**

**Mac:**
```bash
cd ~/Library/Application\ Support/Anki2/addons21/
mv 1846879528 ~/Desktop/1846879528.backup
```

**Windows:**
```cmd
cd %APPDATA%\Anki2\addons21\
move 1846879528 %USERPROFILE%\Desktop\1846879528.backup
```

**Linux:**
```bash
cd ~/.local/share/Anki2/addons21/
mv 1846879528 ~/Desktop/1846879528.backup
```

**Step 3: Install Test Version**
1. Open Anki
2. Go to **Tools → Add-ons**
3. Click **Install from file...**
4. Select the downloaded `Migaku.ankiaddon` file
5. Restart Anki

**Step 4: Test the Add-on**
- Verify all functionality works as expected
- Test new features mentioned in the changelog
- Check compatibility with current Anki version
- Test connection to Migaku Browser Extension

**Step 5: Restore Production Version (After Testing)**
```bash
# Close Anki first
cd [addons folder path from Step 2]
rm -rf 1846879528
mv ~/Desktop/1846879528.backup 1846879528
```
Then restart Anki.

### Publishing to AnkiWeb

After QA approval:
1. Go to https://ankiweb.net/shared/upload
2. Sign in with your AnkiWeb account
3. Update addon **1846879528**
4. Upload the `Migaku.ankiaddon` file from the GitHub release
5. Update the description if needed (using `ankiweb.html`)

## Things that often break

- The `src/lib` folder contains dependencies, that are not included in Anki by default.
  If the extension suddenly starts failing on newer Anki versions (especially on macOS), you might have to create a new folder like `macos_314`,
  and add the new dependencies.

You'll also need to add the appropriate code in `sys_libraries.py` then, to load the new libraries on the right platform and Anki version.

- Support for new languages require adding a new folder in `src/languages` and modifying `src/languages/__init__.py` to include it.

## Ankiweb User Guide

Check out [here](./ankiweb.html).
