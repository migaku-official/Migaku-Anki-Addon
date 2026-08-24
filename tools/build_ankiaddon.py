#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
VERSION_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*\Z")


def get_version():
    configured_version = os.environ.get("MIGAKU_VERSION", "").strip()
    if configured_version:
        version = configured_version
    else:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT,
            text=True,
        ).strip()

    if version == "git" or not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"Invalid add-on version: {version!r}")

    return version


def get_default_output(version, build_date=None):
    build_date = build_date or datetime.now(timezone.utc).strftime("%Y%m%d")
    archive_version = version[1:] if version.startswith("v") else version
    return ROOT / "dist" / f"Migaku-Anki-Addon-v{archive_version}--{build_date}.ankiaddon"


def get_output_path(output_arg, version, build_date=None):
    default_output = get_default_output(version, build_date)
    output_path = output_arg or default_output
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    if output_path.parent.resolve() == default_output.parent.resolve() and output_path.name != default_output.name:
        raise ValueError(f"Archives written to dist must use {default_output.name}")
    return output_path


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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    version = get_version()
    output_path = get_output_path(args.output, version)
    build(output_path, version)
    print(f"Built {output_path} ({version})")


if __name__ == "__main__":
    main()
