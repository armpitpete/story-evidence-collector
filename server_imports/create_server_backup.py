#!/usr/bin/env python3
"""Create an atomic, checksummed backup of the private evidence archive.

The live archive is read only. The backup store itself is excluded to avoid
recursive snapshots. SQLite is copied through its online backup API so the
backup database is transactionally consistent even if the source is open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_ARCHIVE_ROOT = Path("/srv/story-evidence-collector")
DEFAULT_DATABASE_RELATIVE_PATH = Path("db/mp_evidence_cache.sqlite")
DEFAULT_BACKUP_DIR_NAME = "backups"
MANIFEST_NAME = "manifest.json"
SNAPSHOT_DIR_NAME = "archive"
MANIFEST_SCHEMA_VERSION = "1"
BACKUP_NAME_PATTERN = re.compile(r"^backup-[0-9A-Za-z][0-9A-Za-z._-]*$")


class BackupError(RuntimeError):
    """Raised when a safe backup cannot be created."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_backup_name() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"backup-{timestamp}-{uuid.uuid4().hex[:8]}"


def mode_text(path: Path) -> str:
    return f"{stat.S_IMODE(path.stat().st_mode):04o}"


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_backup_name(name: str) -> str:
    if not BACKUP_NAME_PATTERN.fullmatch(name):
        raise BackupError(
            "backup name must start with 'backup-' and contain only letters, "
            "numbers, dots, underscores and hyphens"
        )
    return name


def ensure_directory(path: Path, label: str) -> None:
    if not path.exists():
        raise BackupError(f"{label} does not exist: {path}")
    if not path.is_dir():
        raise BackupError(f"{label} is not a directory: {path}")
    if path.is_symlink():
        raise BackupError(f"{label} must not be a symlink: {path}")


def relative_parts_are_safe(relative: Path) -> bool:
    return not relative.is_absolute() and ".." not in relative.parts


def database_sidecar_paths(database_relative_path: Path) -> set[Path]:
    database_text = database_relative_path.as_posix()
    return {
        Path(f"{database_text}-wal"),
        Path(f"{database_text}-shm"),
        Path(f"{database_text}-journal"),
    }


def iter_source_entries(
    archive_root: Path,
    excluded_top_level_names: set[str],
    database_relative_path: Path,
) -> Iterable[tuple[str, Path, Path]]:
    """Yield (kind, source, relative) in stable order.

    The live SQLite file is skipped because it is copied separately using the
    SQLite backup API. Symlinks and special files are rejected rather than
    followed or silently omitted.
    """

    database_relative_path = Path(database_relative_path)
    excluded_database_paths = {database_relative_path} | database_sidecar_paths(
        database_relative_path
    )
    for root_text, directory_names, file_names in os.walk(
        archive_root, topdown=True, followlinks=False
    ):
        root = Path(root_text)
        relative_root = root.relative_to(archive_root)

        kept_directories: list[str] = []
        for name in sorted(directory_names):
            source = root / name
            relative = relative_root / name
            if len(relative.parts) == 1 and name in excluded_top_level_names:
                continue
            if source.is_symlink():
                raise BackupError(f"archive contains a directory symlink: {relative}")
            kept_directories.append(name)
            yield "directory", source, relative
        directory_names[:] = kept_directories

        for name in sorted(file_names):
            source = root / name
            relative = relative_root / name
            if relative in excluded_database_paths:
                continue
            if source.is_symlink():
                raise BackupError(f"archive contains a file symlink: {relative}")
            try:
                mode = source.stat().st_mode
            except OSError as exc:
                raise BackupError(f"could not stat archive entry {relative}: {exc}") from exc
            if not stat.S_ISREG(mode):
                raise BackupError(f"archive contains a non-regular file: {relative}")
            yield "file", source, relative


def copy_regular_file_stable(source: Path, destination: Path, relative: Path) -> None:
    before_stat = source.stat()
    before_hash = file_sha256(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=False)
    after_stat = source.stat()
    after_hash = file_sha256(source)
    destination_hash = file_sha256(destination)

    if (
        before_stat.st_size != after_stat.st_size
        or before_stat.st_mtime_ns != after_stat.st_mtime_ns
        or before_hash != after_hash
    ):
        raise BackupError(f"archive file changed while it was being copied: {relative}")
    if destination_hash != after_hash:
        raise BackupError(f"copied archive file failed checksum comparison: {relative}")


def copy_archive_entries(
    archive_root: Path,
    snapshot_root: Path,
    excluded_top_level_names: set[str],
    database_relative_path: Path,
) -> None:
    snapshot_root.mkdir(parents=True, exist_ok=False)
    directories_to_copy_metadata: list[tuple[Path, Path]] = []
    for kind, source, relative in iter_source_entries(
        archive_root,
        excluded_top_level_names=excluded_top_level_names,
        database_relative_path=database_relative_path,
    ):
        destination = snapshot_root / relative
        if kind == "directory":
            destination.mkdir(parents=True, exist_ok=True)
            directories_to_copy_metadata.append((source, destination))
        else:
            copy_regular_file_stable(source, destination, relative)

    for source, destination in sorted(
        directories_to_copy_metadata,
        key=lambda item: len(item[1].parts),
        reverse=True,
    ):
        shutil.copystat(source, destination, follow_symlinks=False)
    shutil.copystat(archive_root, snapshot_root, follow_symlinks=False)


def sqlite_quick_check(database_path: Path) -> list[str]:
    uri = f"file:{database_path.resolve()}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=30)
    except sqlite3.Error as exc:
        raise BackupError(f"could not open SQLite database read-only: {exc}") from exc
    try:
        return [str(row[0]) for row in connection.execute("PRAGMA quick_check").fetchall()]
    except sqlite3.Error as exc:
        raise BackupError(f"SQLite quick_check failed to execute: {exc}") from exc
    finally:
        connection.close()


def copy_sqlite_database(source: Path, destination: Path) -> list[str]:
    if not source.exists() or not source.is_file() or source.is_symlink():
        raise BackupError(f"source SQLite database is missing or unsafe: {source}")

    source_check = sqlite_quick_check(source)
    if source_check != ["ok"]:
        raise BackupError(f"source SQLite quick_check is not ok: {source_check}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    source_uri = f"file:{source.resolve()}?mode=ro"
    try:
        with sqlite3.connect(source_uri, uri=True, timeout=30) as source_connection:
            with sqlite3.connect(destination) as destination_connection:
                source_connection.backup(destination_connection)
                destination_connection.commit()
                destination_connection.execute("PRAGMA journal_mode=DELETE").fetchone()
                destination_connection.commit()
    except sqlite3.Error as exc:
        raise BackupError(f"SQLite backup operation failed: {exc}") from exc

    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(f"{destination}{suffix}")
        if sidecar.exists():
            sidecar.unlink()

    shutil.copystat(source, destination, follow_symlinks=False)
    destination_check = sqlite_quick_check(destination)
    if destination_check != ["ok"]:
        raise BackupError(f"backup SQLite quick_check is not ok: {destination_check}")
    return destination_check


def build_manifest_entries(snapshot_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(snapshot_root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(snapshot_root)
        if not relative_parts_are_safe(relative):
            raise BackupError(f"unsafe snapshot path: {relative}")
        if path.is_symlink():
            raise BackupError(f"snapshot contains a symlink: {relative}")
        if path.is_dir():
            entries.append(
                {
                    "path": relative.as_posix(),
                    "type": "directory",
                    "mode": mode_text(path),
                }
            )
        elif path.is_file():
            entries.append(
                {
                    "path": relative.as_posix(),
                    "type": "file",
                    "mode": mode_text(path),
                    "size_bytes": path.stat().st_size,
                    "sha256": file_sha256(path),
                }
            )
        else:
            raise BackupError(f"snapshot contains a special file: {relative}")
    return entries


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def create_backup(
    archive_root: Path = DEFAULT_ARCHIVE_ROOT,
    backup_root: Path | None = None,
    backup_name: str | None = None,
    database_relative_path: Path = DEFAULT_DATABASE_RELATIVE_PATH,
) -> Path:
    archive_root = Path(archive_root).resolve()
    ensure_directory(archive_root, "archive root")

    database_relative_path = Path(database_relative_path)
    if not relative_parts_are_safe(database_relative_path):
        raise BackupError("database path must be relative and stay inside the archive")

    backup_root = (
        Path(backup_root).resolve()
        if backup_root is not None
        else (archive_root / DEFAULT_BACKUP_DIR_NAME).resolve()
    )
    backup_root.mkdir(parents=True, exist_ok=True)
    ensure_directory(backup_root, "backup root")

    name = validate_backup_name(backup_name or default_backup_name())
    final_directory = backup_root / name
    if final_directory.exists():
        raise BackupError(f"backup destination already exists: {final_directory}")

    partial_directory = backup_root / f".partial-{name}-{uuid.uuid4().hex}"
    if partial_directory.exists():
        raise BackupError(f"partial backup path unexpectedly exists: {partial_directory}")

    excluded_top_level_names: set[str] = set()
    try:
        backup_relative = backup_root.relative_to(archive_root)
    except ValueError:
        backup_relative = None
    if backup_relative is not None:
        if not backup_relative.parts:
            raise BackupError("backup root must not be the archive root")
        if len(backup_relative.parts) != 1:
            raise BackupError(
                "a backup root inside the archive must be a direct child directory"
            )
        excluded_top_level_names.add(backup_relative.parts[0])

    try:
        partial_directory.mkdir(parents=False, exist_ok=False)
        partial_directory.chmod(0o700)
        snapshot_root = partial_directory / SNAPSHOT_DIR_NAME
        copy_archive_entries(
            archive_root,
            snapshot_root,
            excluded_top_level_names=excluded_top_level_names,
            database_relative_path=database_relative_path,
        )

        database_source = archive_root / database_relative_path
        database_destination = snapshot_root / database_relative_path
        database_check = copy_sqlite_database(database_source, database_destination)

        manifest = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "backup_name": name,
            "created_at": utc_now(),
            "source_archive_root": str(archive_root),
            "archive_root_mode": mode_text(snapshot_root),
            "snapshot_directory": SNAPSHOT_DIR_NAME,
            "database_relative_path": database_relative_path.as_posix(),
            "database_quick_check": database_check,
            "excluded_top_level_names": sorted(excluded_top_level_names),
            "excluded_database_sidecars": sorted(
                path.as_posix() for path in database_sidecar_paths(database_relative_path)
            ),
            "entries": build_manifest_entries(snapshot_root),
        }
        write_json_atomic(partial_directory / MANIFEST_NAME, manifest)
        partial_directory.replace(final_directory)
    except Exception:
        shutil.rmtree(partial_directory, ignore_errors=True)
        raise

    return final_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an atomic, checksummed backup of the private evidence archive."
    )
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--backup-root", type=Path, default=None)
    parser.add_argument("--backup-name", default=None)
    parser.add_argument(
        "--database-relative-path",
        type=Path,
        default=DEFAULT_DATABASE_RELATIVE_PATH,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        backup_directory = create_backup(
            archive_root=args.archive_root,
            backup_root=args.backup_root,
            backup_name=args.backup_name,
            database_relative_path=args.database_relative_path,
        )
    except (BackupError, OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}")
        return 1

    print("Backup created successfully.")
    print(f"Backup directory: {backup_directory}")
    print(f"Manifest: {backup_directory / MANIFEST_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
