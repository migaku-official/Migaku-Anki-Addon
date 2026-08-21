#!/usr/bin/env python3

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGESET_DIR = ROOT / ".changeset"


def pending_changesets():
    return sorted(
        path
        for path in CHANGESET_DIR.glob("*.md")
        if path.name != "README.md"
    )


def run(command):
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    changesets = pending_changesets()
    if not changesets:
        print("No pending changesets; release preparation is a no-op")
        return

    run(["npx", "changeset", "version"])
    run(["python3", "tools/sync_release_metadata.py"])
    print(f"Consumed {len(changesets)} changeset(s)")


if __name__ == "__main__":
    main()
