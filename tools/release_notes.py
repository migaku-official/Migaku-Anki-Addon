#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = ROOT / "CHANGELOG.md"


def release_notes(version):
    lines = CHANGELOG_PATH.read_text().splitlines()
    heading = f"## {version}"
    try:
        start = lines.index(heading)
    except ValueError as error:
        raise SystemExit(f"Could not find {heading} in CHANGELOG.md") from error

    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    notes = "\n".join(lines[start + 1 : end]).strip()
    if not notes:
        raise SystemExit(f"Release section {heading} is empty")
    return notes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tools/release_notes.py VERSION")
    print(release_notes(sys.argv[1]))
