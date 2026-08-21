#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
DEFAULT_OUTPUT = ROOT / "dist" / "Migaku.ankiaddon"
VERSION_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*\Z")


def get_version():
    configured_version = os.environ.get("MIGAKU_VERSION", "").strip()
    if configured_version:
        version = configured_version
    else:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=ROOT,
            text=True,
        ).strip()

    if version == "git" or not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid add-on version: {version!r}")

    return version


def should_skip(path):
    relative_path = path.relative_to(SOURCE_ROOT)
    return (
        "user_files" in relative_path.parts
        or "__pycache__" in relative_path.parts
        or path.suffix == ".pyc"
        or relative_path.as_posix() == "meta.json"
    )


def build(output_path, version):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_output:
        temporary_path = Path(temporary_output.name)

    try:
        with zipfile.ZipFile(temporary_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(SOURCE_ROOT.rglob("*")):
                if not path.is_file() or should_skip(path) or path.relative_to(SOURCE_ROOT).as_posix() == "version.py":
                    continue
                archive.write(path, path.relative_to(SOURCE_ROOT).as_posix())

            archive.writestr("version.py", f'VERSION_STRING = "{version}"\n')

        os.replace(temporary_path, output_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Build a Migaku Anki add-on archive")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    version = get_version()
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    build(output_path, version)
    print(f"Built {output_path} ({version})")


if __name__ == "__main__":
    main()
