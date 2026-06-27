#!/usr/bin/env python3
"""Validate every TWIS evidence pack under a root folder.

Validator v1 scans one parent folder and validates each direct child folder
that contains a pack.json file.

It does not make editorial judgements.
It does not decide whether evidence is true.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validate_evidence_pack import validate_pack


def find_pack_dirs(root: Path) -> list[Path]:
    """Return direct child folders that look like evidence packs."""

    if not root.exists():
        raise FileNotFoundError(f"Evidence pack root does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Evidence pack root is not a folder: {root}")

    return sorted(
        child
        for child in root.iterdir()
        if child.is_dir() and (child / "pack.json").exists()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate every TWIS evidence pack under a root folder."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default="fixtures/evidence-packs",
        help="Folder containing evidence pack folders. Default: fixtures/evidence-packs",
    )
    args = parser.parse_args()

    root = Path(args.root)

    try:
        pack_dirs = find_pack_dirs(root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not pack_dirs:
        print(f"No evidence packs found under: {root}")
        return 1

    failed = False

    for pack_dir in pack_dirs:
        errors = validate_pack(pack_dir)

        if errors:
            failed = True
            print(f"FAIL: {pack_dir}")
            for error in errors:
                print(f"- {error}")
            print()
        else:
            print(f"PASS: {pack_dir}")

    if failed:
        print("One or more evidence packs failed validation.")
        return 1

    print(f"All evidence packs passed validation. Count: {len(pack_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
