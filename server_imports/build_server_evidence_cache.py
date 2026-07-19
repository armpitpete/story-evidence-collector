#!/usr/bin/env python3
"""Controlled server evidence-cache importer.

This script prepares and seeds the private server evidence cache for the MP
evidence pipeline. It is deliberately cautious:

- dry-run is the default
- no network access is performed
- writes are restricted to the configured archive root
- database creation requires --apply --init-db
- seed imports require an explicit local rows file
- source-shaped batches may use an explicit reviewed manifest for batch context
- an import/check log is written when the log directory is writable
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMPORTER_NAME = "build_server_evidence_cache"
IMPORTER_VERSION = "0.3"
DEFAULT_ARCHIVE_ROOT = "/srv/story-evidence-collector"
DEFAULT_MINIMUM_FREE_GB = 40

TARGET_MP_ALIASES = ("target_mp", "targetMp", "member_name", "memberName", "mp_name", "name")
TARGET_MEMBER_ID_ALIASES = ("target_member_id", "member_id", "memberId", "source_member_id")
RECORDED_VOTE_ALIASES = (
    "recorded_vote",
    "recordedVote",
    "vote",
    "member_vote",
    "memberVote",
    "side",
    "recorded_side",
)
VOTE_SIDE_ALIASES = ("vote_side", "voteSide", "side", "recorded_side")


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
    seed_id: str = ""
    seed_rows_path: str = ""
    seed_manifest_path: str = ""
    rows_read: int = 0
    rows_written: int = 0
    rows_skipped: int = 0
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
            "seed_id": self.seed_id,
            "seed_rows_path": self.seed_rows_path,
            "seed_manifest_path": self.seed_manifest_path,
            "rows_read": self.rows_read,
            "rows_written": self.rows_written,
            "rows_skipped": self.rows_skipped,
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


def first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def load_seed_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Seed rows file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = (
            data.get("rows")
            or data.get("vote_rows")
            or data.get("items")
            or data.get("data")
            or []
        )
    else:
        raise ValueError("Seed rows JSON must be a list or object containing a rows list.")
    if not isinstance(rows, list):
        raise ValueError("Seed rows value must be a list.")
    return [row for row in rows if isinstance(row, dict)]


def load_seed_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Seed manifest file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Seed manifest JSON must be an object.")
    return data


def validate_seed_context(seed_id: str, seed_context: dict[str, Any]) -> None:
    context_id = str(first_value(seed_context, "batch_id", "seed_id"))
    if context_id and context_id != seed_id:
        raise ValueError(
            f"Seed manifest identity mismatch: expected {seed_id!r}, found {context_id!r}."
        )


def normalise_seed_row(
    row: dict[str, Any],
    seed_id: str,
    seed_path: Path,
    seed_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    context = seed_context if isinstance(seed_context, dict) else {}
    source_system = str(first_value(row, "source_system", "sourceSystem") or "parlparse")
    division_id = str(first_value(row, "division_id", "divisionId", "division_number", "source_division_id", "id"))
    division_date = str(first_value(row, "division_date", "divisionDate", "date"))
    target_mp = str(first_value(row, *TARGET_MP_ALIASES) or first_value(context, *TARGET_MP_ALIASES))

    missing = [
        name
        for name, value in (
            ("division_id", division_id),
            ("division_date", division_date),
            ("target_mp", target_mp),
        )
        if not value
    ]
    if missing:
        return None, f"Skipped row missing required fields: {', '.join(missing)}"

    source_member_id = str(
        first_value(row, *TARGET_MEMBER_ID_ALIASES)
        or first_value(context, *TARGET_MEMBER_ID_ALIASES)
    )
    member_key = f"{source_system}|member|{source_member_id or target_mp}"
    division_key = f"{source_system}|division|{division_id}"
    vote_key = f"{source_system}|{division_id}|{target_mp}"

    recorded_vote = str(first_value(row, *RECORDED_VOTE_ALIASES))
    vote_side = str(first_value(row, *VOTE_SIDE_ALIASES) or recorded_vote)
    source_url = str(first_value(row, "source_url", "sourceUrl"))
    source_path = str(first_value(row, "source_path", "sourcePath") or seed_path)
    division_title = str(first_value(row, "division_title", "divisionTitle", "title", "motion_title", "subject"))
    house = str(first_value(row, "house") or "commons")
    meaning_quality = str(first_value(row, "meaning_quality", "meaningQuality") or "needs_review")

    if source_system == "parlparse":
        meaning_quality = "needs_review"

    trace = json.dumps(row, sort_keys=True, ensure_ascii=False)

    return {
        "source_id": f"seed:{seed_id}",
        "source_system": source_system,
        "source_name": seed_id,
        "source_path": source_path,
        "member_key": member_key,
        "source_member_id": source_member_id,
        "target_mp": target_mp,
        "division_key": division_key,
        "division_id": division_id,
        "division_date": division_date,
        "division_title": division_title,
        "house": house,
        "vote_key": vote_key,
        "recorded_vote": recorded_vote,
        "vote_side": vote_side,
        "meaning_quality": meaning_quality,
        "source_url": source_url,
        "source_trace": trace,
    }, None



def apply_seed_rows(
    db_path: Path,
    seed_id: str,
    seed_path: Path,
    rows: list[dict[str, Any]],
    import_run_id: str,
    seed_context: dict[str, Any] | None = None,
) -> tuple[int, int, list[str]]:
    written = 0
    skipped = 0
    messages: list[str] = []
    now = utc_now()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(
            """
            INSERT OR REPLACE INTO imports (
              import_run_id, importer_name, importer_version, started_at, finished_at,
              dry_run, network_access_used, input_path, output_path, rows_read,
              rows_written, warning_count, error_count, status
            ) VALUES (?, ?, ?, ?, ?, 0, 0, ?, ?, ?, 0, 0, 0, 'ok')
            """,
            (import_run_id, IMPORTER_NAME, IMPORTER_VERSION, now, now, str(seed_path), str(db_path), len(rows)),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO sources (
              source_id, source_system, source_name, source_path, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (f"seed:{seed_id}", "parlparse", seed_id, str(seed_path), now),
        )

        for row in rows:
            normalised, error = normalise_seed_row(row, seed_id, seed_path, seed_context)
            if error:
                skipped += 1
                messages.append(error)
                conn.execute(
                    """
                    INSERT INTO validation_messages (
                      import_run_id, severity, message_code, message, related_path, created_at
                    ) VALUES (?, 'warning', 'seed_row_skipped', ?, ?, ?)
                    """,
                    (import_run_id, error, str(seed_path), now),
                )
                continue

            assert normalised is not None

            conn.execute(
                """
                INSERT OR IGNORE INTO members (
                  member_key, source_system, source_member_id, display_name, source_trace, import_run_id
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    normalised["member_key"],
                    normalised["source_system"],
                    normalised["source_member_id"],
                    normalised["target_mp"],
                    normalised["source_trace"],
                    import_run_id,
                ),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO divisions (
                  division_key, source_system, division_id, division_date, division_title,
                  house, source_url, source_path, source_trace, import_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalised["division_key"],
                    normalised["source_system"],
                    normalised["division_id"],
                    normalised["division_date"],
                    normalised["division_title"],
                    normalised["house"],
                    normalised["source_url"],
                    normalised["source_path"],
                    normalised["source_trace"],
                    import_run_id,
                ),
            )
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO member_votes (
                  vote_key, source_system, division_key, member_key, target_mp,
                  recorded_vote, vote_side, meaning_quality, source_url, source_path,
                  source_trace, import_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalised["vote_key"],
                    normalised["source_system"],
                    normalised["division_key"],
                    normalised["member_key"],
                    normalised["target_mp"],
                    normalised["recorded_vote"],
                    normalised["vote_side"],
                    normalised["meaning_quality"],
                    normalised["source_url"],
                    normalised["source_path"],
                    normalised["source_trace"],
                    import_run_id,
                ),
            )
            written += cursor.rowcount

        conn.execute(
            """
            UPDATE imports
            SET rows_written = ?, warning_count = ?, error_count = ?, status = ?
            WHERE import_run_id = ?
            """,
            (written, skipped, 0, "ok", import_run_id),
        )
        conn.commit()

    return written, skipped, messages


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare/check the server MP evidence cache.")
    parser.add_argument("--config", type=Path, help="Path to JSON config. Example: server_imports/example_config.example.json")
    parser.add_argument("--archive-root", help="Server archive root. Default comes from config or /srv/story-evidence-collector")
    parser.add_argument("--apply", action="store_true", help="Allow controlled writes such as database initialisation or seed import.")
    parser.add_argument("--init-db", action="store_true", help="Initialise or validate the SQLite schema. Requires --apply for database writes.")
    parser.add_argument("--seed-id", help="Identifier for a small controlled seed import, for example parlparse_2003_01.")
    parser.add_argument("--seed-rows", type=Path, help="Local JSON rows file for the seed import. No web fetch is performed.")
    parser.add_argument("--seed-manifest", type=Path, help="Reviewed local batch manifest supplying target identity context when rows use source shape.")
    parser.add_argument("--no-log", action="store_true", help="Do not write an import/check log.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = load_config(args.config)

    archive_root_value = args.archive_root or config.get("archive_root") or DEFAULT_ARCHIVE_ROOT
    archive_root = Path(archive_root_value)
    expected_user = config.get("expected_user")
    current_user = getpass.getuser()

    seed_config = config.get("seed_import", {}) if isinstance(config.get("seed_import", {}), dict) else {}
    seed_id = args.seed_id or seed_config.get("seed_id") or ""
    seed_rows_value = args.seed_rows or seed_config.get("rows_path") or ""
    seed_rows_path = Path(seed_rows_value) if seed_rows_value else None
    seed_manifest_value = args.seed_manifest or seed_config.get("manifest_path") or ""
    seed_manifest_path = Path(seed_manifest_value) if seed_manifest_value else None

    result = CheckResult(
        archive_root=str(archive_root),
        current_user=current_user,
        expected_user=expected_user,
        dry_run=not args.apply,
        apply=args.apply,
        init_db=args.init_db,
        seed_id=str(seed_id),
        seed_rows_path=str(seed_rows_path or ""),
        seed_manifest_path=str(seed_manifest_path or ""),
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
            except Exception as exc:
                result.errors.append(f"Database schema check failed: {exc}")

        if seed_rows_path is not None:
            if not seed_id:
                result.errors.append("Seed rows path was supplied without --seed-id or seed_import.seed_id.")
            else:
                try:
                    seed_rows = load_seed_rows(seed_rows_path)
                    seed_context = load_seed_manifest(seed_manifest_path)
                    validate_seed_context(str(seed_id), seed_context)
                    result.rows_read = len(seed_rows)

                    if args.apply:
                        if not db_path.exists():
                            result.errors.append(f"Database does not exist yet: {db_path}")
                        else:
                            written, skipped, messages = apply_seed_rows(
                                db_path,
                                str(seed_id),
                                seed_rows_path,
                                seed_rows,
                                import_run_id,
                                seed_context=seed_context,
                            )
                            result.rows_written = written
                            result.rows_skipped = skipped
                            result.warnings.extend(messages)
                    else:
                        skipped = 0
                        for row in seed_rows:
                            _, error = normalise_seed_row(
                                row,
                                str(seed_id),
                                seed_rows_path,
                                seed_context,
                            )
                            if error:
                                skipped += 1
                                result.warnings.append(error)
                        result.rows_skipped = skipped
                        result.warnings.append("Seed rows checked in dry-run mode; database was not written.")
                except Exception as exc:
                    result.errors.append(f"Seed import failed: {exc}")

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
