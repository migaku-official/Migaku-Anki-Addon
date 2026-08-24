#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
DIST_ROOT = ROOT / "dist"
VERSION_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*\Z")
BUILD_TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}--\d{4}\Z")


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


def get_default_output(version, build_timestamp=None):
    build_timestamp = build_timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d--%H%M")
    if not BUILD_TIMESTAMP_PATTERN.fullmatch(build_timestamp): raise ValueError(f"Invalid build timestamp: {build_timestamp!r}")
    archive_version = version[1:] if version.startswith("v") else version
    return DIST_ROOT / f"Migaku-Anki-Addon-v{archive_version}--{build_timestamp}.ankiaddon"


def get_output_path(output_arg, version, build_timestamp=None):
    default_output = get_default_output(version, build_timestamp)
    output_path = output_arg or default_output
    if not output_path.is_absolute(): output_path = ROOT / output_path
    if default_output.parent.resolve() in output_path.resolve().parents and output_path.name != default_output.name: raise ValueError(f"Archives written to dist must use {default_output.name}")
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
    if DIST_ROOT.exists(): shutil.rmtree(DIST_ROOT)
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
    parser.add_argument("--build-timestamp")
    args = parser.parse_args()
    version = get_version()
    output_path = get_output_path(args.output, version, args.build_timestamp)
    build(output_path, version)
    print(f"Built {output_path} ({version})")


if __name__ == "__main__":
    main()
