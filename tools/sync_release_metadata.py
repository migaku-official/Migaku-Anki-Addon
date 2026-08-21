#!/usr/bin/env python3

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = ROOT / "package.json"
ANKIWEB_PATH = ROOT / "ankiweb.html"
ASSET_URL_PATTERN = re.compile(
    r"(https://raw\.githubusercontent\.com/migaku-official/"
    r"Migaku-Anki-Addon/)[^/]+(/docs/assets/)"
)


def main():
    package = json.loads(PACKAGE_PATH.read_text())
    version = package["version"]
    description = ANKIWEB_PATH.read_text()
    updated_description, replacements = ASSET_URL_PATTERN.subn(
        rf"\g<1>{version}\g<2>",
        description,
    )

    if replacements == 0:
        raise SystemExit("No release asset URLs found in ankiweb.html")

    ANKIWEB_PATH.write_text(updated_description)
    print(f"Updated {replacements} AnkiWeb asset URLs to {version}")


if __name__ == "__main__":
    main()
