#!/usr/bin/env python3
"""Verify a private archive backup and optionally restore it to a new target.

This tool never restores over an existing directory. Verification checks every
manifest entry, rejects path traversal and symlinks, detects missing or extra
files, validates sizes and SHA-256 hashes, and runs SQLite quick_check.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import stat
import uuid
from pathlib import Path
from typing import Any

try:
    from .create_server_backup import (
        MANIFEST_NAME,
        MANIFEST_SCHEMA_VERSION,
        SNAPSHOT_DIR_NAME,
        BackupError,
        file_sha256,
        relative_parts_are_safe,
        sqlite_quick_check,
    )
except ImportError:  # Direct script execution from server_imports/.
    from create_server_backup import (  # type: ignore
        MANIFEST_NAME,
        MANIFEST_SCHEMA_VERSION,
        SNAPSHOT_DIR_NAME,
        BackupError,
        file_sha256,
        relative_parts_are_safe,
        sqlite_quick_check,
    )


class VerificationError(RuntimeError):
    """Raised when a backup cannot be verified or safely restored."""


def safe_relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{label} must be a non-empty string")
    relative = Path(value)
    if not relative_parts_are_safe(relative):
        raise VerificationError(f"{label} is unsafe: {value}")
    return relative


def load_manifest(backup_directory: Path) -> dict[str, Any]:
    manifest_path = backup_directory / MANIFEST_NAME
    if not manifest_path.exists() or not manifest_path.is_file() or manifest_path.is_symlink():
        raise VerificationError(f"safe manifest file not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"could not read manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise VerificationError("manifest must contain a JSON object")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise VerificationError(
            f"unsupported manifest schema version: {manifest.get('schema_version')!r}"
        )
    if manifest.get("snapshot_directory") != SNAPSHOT_DIR_NAME:
        raise VerificationError("manifest snapshot_directory is not supported")
    return manifest


def parse_mode(value: Any, label: str) -> int:
    if (
        not isinstance(value, str)
        or len(value) != 4
        or any(character not in "01234567" for character in value)
    ):
        raise VerificationError(f"{label} must be a four-digit octal mode")
    return int(value, 8)


def normalise_manifest_entries(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_entries = manifest.get("entries")
    if not isinstance(raw_entries, list):
        raise VerificationError("manifest entries must be a list")

    entries: dict[str, dict[str, Any]] = {}
    for index, raw_entry in enumerate(raw_entries, start=1):
        if not isinstance(raw_entry, dict):
            raise VerificationError(f"manifest entry {index} must be an object")
        relative = safe_relative_path(raw_entry.get("path"), f"manifest entry {index} path")
        path_text = relative.as_posix()
        if path_text in entries:
            raise VerificationError(f"duplicate manifest path: {path_text}")

        entry_type = raw_entry.get("type")
        mode = parse_mode(raw_entry.get("mode"), f"manifest entry {index} mode")
        if entry_type == "directory":
            entries[path_text] = {
                "path": path_text,
                "type": "directory",
                "mode": mode,
            }
        elif entry_type == "file":
            size = raw_entry.get("size_bytes")
            digest = raw_entry.get("sha256")
            if not isinstance(size, int) or size < 0:
                raise VerificationError(f"invalid size for manifest file: {path_text}")
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise VerificationError(f"invalid SHA-256 for manifest file: {path_text}")
            entries[path_text] = {
                "path": path_text,
                "type": "file",
                "mode": mode,
                "size_bytes": size,
                "sha256": digest,
            }
        else:
            raise VerificationError(
                f"manifest entry has unsupported type {entry_type!r}: {path_text}"
            )
    return entries


def actual_snapshot_entries(snapshot_root: Path) -> dict[str, str]:
    if not snapshot_root.exists() or not snapshot_root.is_dir() or snapshot_root.is_symlink():
        raise VerificationError(f"safe snapshot directory not found: {snapshot_root}")

    actual: dict[str, str] = {}
    for path in sorted(snapshot_root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(snapshot_root)
        if not relative_parts_are_safe(relative):
            raise VerificationError(f"unsafe path in snapshot: {relative}")
        path_text = relative.as_posix()
        if path.is_symlink():
            raise VerificationError(f"snapshot contains a symlink: {path_text}")
        if path.is_dir():
            actual[path_text] = "directory"
        elif path.is_file():
            actual[path_text] = "file"
        else:
            raise VerificationError(f"snapshot contains a special file: {path_text}")
    return actual


def verify_snapshot(
    snapshot_root: Path,
    entries: dict[str, dict[str, Any]],
    database_relative_path: Path,
    archive_root_mode: int,
) -> dict[str, Any]:
    actual = actual_snapshot_entries(snapshot_root)
    actual_root_mode = stat.S_IMODE(snapshot_root.stat().st_mode)
    if actual_root_mode != archive_root_mode:
        raise VerificationError(
            f"archive root mode mismatch: expected {archive_root_mode:04o}, "
            f"got {actual_root_mode:04o}"
        )
    expected_types = {path: entry["type"] for path, entry in entries.items()}

    missing = sorted(set(expected_types) - set(actual))
    extra = sorted(set(actual) - set(expected_types))
    wrong_types = sorted(
        path
        for path in set(actual).intersection(expected_types)
        if actual[path] != expected_types[path]
    )
    if missing:
        raise VerificationError(f"snapshot is missing manifest entries: {missing}")
    if extra:
        raise VerificationError(f"snapshot contains unmanifested entries: {extra}")
    if wrong_types:
        raise VerificationError(f"snapshot entry types do not match: {wrong_types}")

    checked_files = 0
    checked_bytes = 0
    for path_text, entry in sorted(entries.items()):
        path = snapshot_root / Path(path_text)
        actual_mode = stat.S_IMODE(path.stat().st_mode)
        if actual_mode != entry["mode"]:
            raise VerificationError(
                f"mode mismatch for {path_text}: expected {entry['mode']:04o}, "
                f"got {actual_mode:04o}"
            )
        if entry["type"] != "file":
            continue
        size = path.stat().st_size
        if size != entry["size_bytes"]:
            raise VerificationError(
                f"size mismatch for {path_text}: expected {entry['size_bytes']}, got {size}"
            )
        digest = file_sha256(path)
        if digest != entry["sha256"]:
            raise VerificationError(f"checksum mismatch for {path_text}")
        checked_files += 1
        checked_bytes += size

    database_text = database_relative_path.as_posix()
    database_entry = entries.get(database_text)
    if not database_entry or database_entry.get("type") != "file":
        raise VerificationError(
            f"manifest does not contain database file: {database_text}"
        )
    database_path = snapshot_root / database_relative_path
    try:
        database_check = sqlite_quick_check(database_path)
    except BackupError as exc:
        raise VerificationError(str(exc)) from exc
    if database_check != ["ok"]:
        raise VerificationError(f"SQLite quick_check is not ok: {database_check}")

    return {
        "checked_files": checked_files,
        "checked_bytes": checked_bytes,
        "database_quick_check": database_check,
    }


def verify_backup(backup_directory: Path) -> dict[str, Any]:
    backup_directory = Path(backup_directory).resolve()
    if (
        not backup_directory.exists()
        or not backup_directory.is_dir()
        or backup_directory.is_symlink()
    ):
        raise VerificationError(f"safe backup directory not found: {backup_directory}")

    manifest = load_manifest(backup_directory)
    entries = normalise_manifest_entries(manifest)
    database_relative_path = safe_relative_path(
        manifest.get("database_relative_path"), "database_relative_path"
    )
    archive_root_mode = parse_mode(manifest.get("archive_root_mode"), "archive_root_mode")
    snapshot_root = backup_directory / SNAPSHOT_DIR_NAME
    report = verify_snapshot(
        snapshot_root, entries, database_relative_path, archive_root_mode
    )
    report.update(
        {
            "backup_directory": str(backup_directory),
            "backup_name": manifest.get("backup_name"),
            "created_at": manifest.get("created_at"),
            "entry_count": len(entries),
        }
    )
    return report


def copy_manifest_entries(
    snapshot_root: Path,
    target_root: Path,
    entries: dict[str, dict[str, Any]],
    archive_root_mode: int,
) -> None:
    target_root.mkdir(parents=False, exist_ok=False)
    target_root.chmod(0o700)
    directory_paths = sorted(
        (Path(path) for path, entry in entries.items() if entry["type"] == "directory"),
        key=lambda path: (len(path.parts), path.as_posix()),
    )
    for relative in directory_paths:
        (target_root / relative).mkdir(parents=True, exist_ok=True)

    file_paths = sorted(
        Path(path) for path, entry in entries.items() if entry["type"] == "file"
    )
    for relative in file_paths:
        source = snapshot_root / relative
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)
        os.chmod(destination, entries[relative.as_posix()]["mode"])

    for relative in sorted(
        directory_paths, key=lambda path: len(path.parts), reverse=True
    ):
        os.chmod(target_root / relative, entries[relative.as_posix()]["mode"])
    os.chmod(target_root, archive_root_mode)


def restore_backup(backup_directory: Path, target_root: Path) -> dict[str, Any]:
    backup_directory = Path(backup_directory).resolve()
    target_root = Path(target_root).resolve()
    if target_root.exists():
        raise VerificationError(f"restore target already exists: {target_root}")
    if target_root == backup_directory or backup_directory in target_root.parents:
        raise VerificationError("restore target must not be inside the backup directory")

    manifest = load_manifest(backup_directory)
    entries = normalise_manifest_entries(manifest)
    database_relative_path = safe_relative_path(
        manifest.get("database_relative_path"), "database_relative_path"
    )
    archive_root_mode = parse_mode(manifest.get("archive_root_mode"), "archive_root_mode")
    snapshot_root = backup_directory / SNAPSHOT_DIR_NAME
    source_report = verify_snapshot(
        snapshot_root, entries, database_relative_path, archive_root_mode
    )

    target_root.parent.mkdir(parents=True, exist_ok=True)
    partial_target = target_root.with_name(
        f".partial-{target_root.name}-{uuid.uuid4().hex}"
    )
    if partial_target.exists():
        raise VerificationError(f"partial restore target already exists: {partial_target}")

    try:
        copy_manifest_entries(
            snapshot_root, partial_target, entries, archive_root_mode
        )
        restored_report = verify_snapshot(
            partial_target, entries, database_relative_path, archive_root_mode
        )
        partial_target.replace(target_root)
    except Exception:
        shutil.rmtree(partial_target, ignore_errors=True)
        raise

    return {
        "backup_directory": str(backup_directory),
        "restore_target": str(target_root),
        "source_verification": source_report,
        "restored_verification": restored_report,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify or safely restore a Story Evidence Collector backup."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify", help="Verify a backup in place.")
    verify_parser.add_argument("backup_directory", type=Path)

    restore_parser = subparsers.add_parser(
        "restore", help="Restore a verified backup into a new disposable directory."
    )
    restore_parser.add_argument("backup_directory", type=Path)
    restore_parser.add_argument("target_root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify":
            report = verify_backup(args.backup_directory)
            print("Backup verification passed.")
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            report = restore_backup(args.backup_directory, args.target_root)
            print("Backup restore passed.")
            print(json.dumps(report, indent=2, sort_keys=True))
    except (VerificationError, BackupError, OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
