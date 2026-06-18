#!/usr/bin/env python3
"""Controlled server evidence-cache importer skeleton.

This script prepares the private server evidence cache for the MP evidence
pipeline. It is deliberately cautious:

- dry-run is the default
- no network access is performed
- writes are restricted to the configured archive root
- database creation requires --apply --init-db
- an import/check log is written when the log directory is writable
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import sqlite3
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPORTER_NAME = "build_server_evidence_cache"
IMPORTER_VERSION = "0.1"
DEFAULT_ARCHIVE_ROOT = "/srv/story-evidence-collector"
DEFAULT_MINIMUM_FREE_GB = 40


@dataclass
class CheckResult:
    archive_root: str
    current_user: str
    expected_user: str | None
    dry_run: bool
    apply: bool
    init_db: bool
    network_access_used: bool = False
    database_path: str = ""
    log_path: str = ""
    free_gb: float = 0.0
    rows_read: int = 0
    rows_written: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "failed" if self.errors else "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "importer_name": IMPORTER_NAME,
            "importer_version": IMPORTER_VERSION,
            "archive_root": self.archive_root,
            "current_user": self.current_user,
            "expected_user": self.expected_user,
            "dry_run": self.dry_run,
            "apply": self.apply,
            "init_db": self.init_db,
            "network_access_used": self.network_access_used,
            "database_path": self.database_path,
            "log_path": self.log_path,
            "free_gb": round(self.free_gb, 3),
            "rows_read": self.rows_read,
            "rows_written": self.rows_written,
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "warnings": self.warnings,
            "errors": self.errors,
            "status": self.status,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_inside_root(root: Path, relative_or_absolute: str) -> Path:
    candidate = Path(relative_or_absolute)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved_root = root.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Unsafe path outside archive root: {candidate}") from exc
    return resolved_candidate


def read_schema(schema_path: Path) -> str:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return schema_path.read_text(encoding="utf-8")


def check_write_access(path: Path) -> None:
    test_path = path / f".write-test-{uuid.uuid4().hex}.tmp"
    test_path.write_text("write test\n", encoding="utf-8")
    test_path.unlink()


def disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024 ** 3)


def initialise_database(db_path: Path, schema_sql: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()


def write_log(log_dir: Path, result: CheckResult, import_run_id: str) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    log_path = log_dir / f"{timestamp}__{IMPORTER_NAME}__{import_run_id}.json"
    result.log_path = str(log_path)
    log_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return log_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare/check the server MP evidence cache.")
    parser.add_argument("--config", type=Path, help="Path to JSON config. Example: server_imports/example_config.example.json")
    parser.add_argument("--archive-root", help="Server archive root. Default comes from config or /srv/story-evidence-collector")
    parser.add_argument("--apply", action="store_true", help="Allow controlled writes such as database initialisation.")
    parser.add_argument("--init-db", action="store_true", help="Initialise or validate the SQLite schema. Requires --apply for database writes.")
    parser.add_argument("--no-log", action="store_true", help="Do not write an import/check log.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = load_config(args.config)

    archive_root_value = args.archive_root or config.get("archive_root") or DEFAULT_ARCHIVE_ROOT
    archive_root = Path(archive_root_value)
    expected_user = config.get("expected_user")
    current_user = getpass.getuser()

    result = CheckResult(
        archive_root=str(archive_root),
        current_user=current_user,
        expected_user=expected_user,
        dry_run=not args.apply,
        apply=args.apply,
        init_db=args.init_db,
    )

    import_run_id = uuid.uuid4().hex

    try:
        if not archive_root.exists():
            result.errors.append(f"Archive root does not exist: {archive_root}")
            print(json.dumps(result.to_dict(), indent=2))
            return 2

        if not archive_root.is_dir():
            result.errors.append(f"Archive root is not a directory: {archive_root}")
            print(json.dumps(result.to_dict(), indent=2))
            return 2

        if expected_user and current_user != expected_user:
            result.warnings.append(f"Current user is {current_user!r}; expected {expected_user!r}.")

        min_free_gb = float(config.get("minimum_free_gb", DEFAULT_MINIMUM_FREE_GB))
        result.free_gb = disk_free_gb(archive_root)
        if result.free_gb < min_free_gb:
            result.errors.append(
                f"Free space {result.free_gb:.2f} GB is below threshold {min_free_gb:.2f} GB."
            )

        log_dir_value = config.get("log_dir", "logs/imports")
        log_dir = resolve_inside_root(archive_root, log_dir_value)
        if not log_dir.exists():
            if args.apply:
                log_dir.mkdir(parents=True, exist_ok=True)
            else:
                result.errors.append(f"Log directory does not exist in dry-run mode: {log_dir}")

        if log_dir.exists():
            try:
                check_write_access(log_dir)
            except OSError as exc:
                result.errors.append(f"Log directory is not writable: {log_dir}: {exc}")

        db_path_value = config.get("database_path", "db/mp_evidence_cache.sqlite")
        db_path = resolve_inside_root(archive_root, db_path_value)
        result.database_path = str(db_path)

        schema_path_value = config.get("schema_path", "server_imports/mp_evidence_cache_schema.sql")
        schema_path = Path(schema_path_value)

        if args.init_db:
            try:
                schema_sql = read_schema(schema_path)
                if args.apply:
                    initialise_database(db_path, schema_sql)
                    result.rows_written = 0
                else:
                    result.warnings.append("--init-db requested in dry-run mode; database was not written.")
            except Exception as exc:  # noqa: BLE001 - report all startup failures clearly
                result.errors.append(f"Database schema check failed: {exc}")

        if not args.no_log and log_dir.exists() and os.access(log_dir, os.W_OK):
            try:
                write_log(log_dir, result, import_run_id)
            except OSError as exc:
                result.errors.append(f"Could not write import log: {exc}")

        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return 1 if result.errors else 0

    except ValueError as exc:
        result.errors.append(str(exc))
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
