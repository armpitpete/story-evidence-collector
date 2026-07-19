#!/usr/bin/env python3
"""Read-only inventory for the Story Evidence Collector server archive.

The script inspects the private evidence archive and repository checkout without
modifying either one. It does not use the network, import data, alter SQLite,
or print raw evidence contents.

Default output is Markdown on stdout. Use ``--format json`` for machine-readable
output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_ARCHIVE_ROOT = Path("/srv/story-evidence-collector")
DEFAULT_REPO_ROOT = Path("/home/storyevidence/story-evidence-collector")
DEFAULT_DATABASE = Path("db/mp_evidence_cache.sqlite")
DEFAULT_SEED_ROWS = Path("parlparse_batches/parlparse_2003_01_rows.json")
DEFAULT_SEED_MANIFEST = Path("parlparse_batches/parlparse_2003_01_manifest.json")
TARGET_MP_ALIASES = ("target_mp", "targetMp", "member_name", "memberName", "mp_name", "name")
RECORDED_VOTE_ALIASES = (
    "recorded_vote",
    "recordedVote",
    "vote",
    "member_vote",
    "memberVote",
    "side",
    "recorded_side",
)
EXPECTED_ARCHIVE_DIRS = (
    "raw",
    "raw/commons-votes",
    "raw/members",
    "raw/parlparse",
    "raw/hansard",
    "raw/interests",
    "raw/committees",
    "db",
    "reports",
    "reports/coverage",
    "reports/mp",
    "reports/divisions",
    "logs",
    "logs/imports",
    "logs/validation",
    "backups",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def iso_mtime(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    except OSError:
        return ""


def human_bytes(value: int) -> str:
    size = float(value)
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def mode_string(path: Path) -> str:
    try:
        return stat.filemode(path.stat().st_mode)
    except OSError:
        return ""


def owner_ids(path: Path) -> dict[str, int | None]:
    try:
        info = path.stat()
        return {"uid": info.st_uid, "gid": info.st_gid}
    except OSError:
        return {"uid": None, "gid": None}


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_summary(path: Path, include_hash: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "mode": mode_string(path),
        "modified_at": iso_mtime(path),
        **owner_ids(path),
    }
    if path.is_file():
        try:
            result["size_bytes"] = path.stat().st_size
        except OSError:
            result["size_bytes"] = None
        if include_hash:
            try:
                result["sha256"] = file_sha256(path)
            except OSError as exc:
                result["sha256_error"] = str(exc)
    return result


def summarise_tree(path: Path, max_files: int = 100_000) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "files": 0,
        "directories": 0,
        "bytes": 0,
        "truncated": False,
        "errors": [],
    }
    if not path.exists() or not path.is_dir():
        return summary

    for root, dirs, files in os.walk(path, followlinks=False):
        summary["directories"] += len(dirs)
        for name in files:
            if summary["files"] >= max_files:
                summary["truncated"] = True
                return summary
            file_path = Path(root) / name
            try:
                if file_path.is_symlink():
                    continue
                summary["bytes"] += file_path.stat().st_size
                summary["files"] += 1
            except OSError as exc:
                summary["errors"].append(f"{file_path}: {exc}")
    return summary


def run_read_only_git(repo_root: Path, args: Iterable[str]) -> dict[str, Any]:
    command = ["git", "-C", str(repo_root), *args]
    try:
        process = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        return {
            "command": command,
            "returncode": process.returncode,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "returncode": None, "stdout": "", "stderr": str(exc)}


def table_columns(connection: sqlite3.Connection, table: str) -> list[str]:
    escaped = table.replace('"', '""')
    rows = connection.execute(f'PRAGMA table_info("{escaped}")').fetchall()
    return [str(row[1]) for row in rows]


def safe_count(connection: sqlite3.Connection, table: str) -> int | None:
    escaped = table.replace('"', '""')
    try:
        row = connection.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return None


def grouped_count(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    table_escaped = table.replace('"', '""')
    column_escaped = column.replace('"', '""')
    try:
        rows = connection.execute(
            f'SELECT "{column_escaped}", COUNT(*) '
            f'FROM "{table_escaped}" '
            f'GROUP BY "{column_escaped}" '
            f'ORDER BY COUNT(*) DESC, "{column_escaped}" '
            f'LIMIT ?',
            (limit,),
        ).fetchall()
        return [{"value": row[0], "count": row[1]} for row in rows]
    except sqlite3.Error:
        return []


def scalar_query(connection: sqlite3.Connection, query: str) -> Any:
    try:
        row = connection.execute(query).fetchone()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def inspect_database(database_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": path_summary(database_path, include_hash=database_path.is_file()),
        "opened_read_only": False,
        "quick_check": [],
        "tables": {},
        "source_system_counts": {},
        "meaning_quality_counts": [],
        "vote_date_range": {},
        "distinct_target_mps": None,
        "errors": [],
    }
    if not database_path.is_file():
        return result

    uri = f"file:{database_path.resolve()}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=10)
    except sqlite3.Error as exc:
        result["errors"].append(f"Could not open database read-only: {exc}")
        return result

    try:
        result["opened_read_only"] = True
        result["quick_check"] = [row[0] for row in connection.execute("PRAGMA quick_check").fetchall()]
        table_rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for (table_name,) in table_rows:
            columns = table_columns(connection, table_name)
            result["tables"][table_name] = {
                "row_count": safe_count(connection, table_name),
                "columns": columns,
            }

        for table in ("sources", "divisions", "member_votes"):
            details = result["tables"].get(table)
            if details and "source_system" in details["columns"]:
                result["source_system_counts"][table] = grouped_count(connection, table, "source_system")

        vote_columns = result["tables"].get("member_votes", {}).get("columns", [])
        if "meaning_quality" in vote_columns:
            result["meaning_quality_counts"] = grouped_count(connection, "member_votes", "meaning_quality")
        if "target_mp" in vote_columns:
            result["distinct_target_mps"] = scalar_query(
                connection,
                "SELECT COUNT(DISTINCT target_mp) FROM member_votes",
            )

        division_columns = result["tables"].get("divisions", {}).get("columns", [])
        if "division_date" in division_columns:
            result["vote_date_range"] = {
                "earliest": scalar_query(connection, "SELECT MIN(division_date) FROM divisions"),
                "latest": scalar_query(connection, "SELECT MAX(division_date) FROM divisions"),
            }
    except sqlite3.Error as exc:
        result["errors"].append(str(exc))
    finally:
        connection.close()

    return result


def extract_rows_container(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("rows", "vote_rows", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def first_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def inspect_seed_rows(seed_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    manifest_file = (
        path_summary(manifest_path, include_hash=manifest_path.is_file())
        if manifest_path is not None
        else {"path": "", "exists": False, "is_file": False, "is_dir": False}
    )
    result: dict[str, Any] = {
        "file": path_summary(seed_path, include_hash=seed_path.is_file()),
        "manifest": manifest_file,
        "row_count": 0,
        "source_shape_missing_canonical_field_counts": {},
        "normalised_missing_required_field_counts": {},
        "missing_required_field_counts": {},
        "meaning_quality_counts": {},
        "normalisation": {
            "classification": "not_available",
            "target_mp_resolution": "unresolved",
            "recorded_vote_resolution": "unresolved",
            "source_trace_policy": "preserve_original_row",
            "evidence_meaning_changed": False,
        },
        "errors": [],
    }
    if not seed_path.is_file():
        return result

    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
        rows = extract_rows_container(data)
        result["row_count"] = len(rows)

        manifest: dict[str, Any] = {}
        if manifest_path is not None and manifest_path.is_file():
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest_data, dict):
                raise ValueError("Seed manifest JSON must be an object.")
            manifest = manifest_data

        canonical_fields = ("division_id", "division_date", "target_mp", "recorded_vote")
        source_missing = {
            field: sum(1 for row in rows if row.get(field) in (None, ""))
            for field in canonical_fields
        }
        result["source_shape_missing_canonical_field_counts"] = source_missing

        context_target_mp = first_value(manifest, *TARGET_MP_ALIASES)
        required_resolvers = {
            "division_id": lambda row: first_value(
                row, "division_id", "divisionId", "division_number", "source_division_id", "id"
            ),
            "division_date": lambda row: first_value(row, "division_date", "divisionDate", "date"),
            "target_mp": lambda row: first_value(row, *TARGET_MP_ALIASES) or context_target_mp,
            "recorded_vote": lambda row: first_value(row, *RECORDED_VOTE_ALIASES),
        }
        normalised_missing = {
            field: sum(1 for row in rows if resolver(row) in (None, ""))
            for field, resolver in required_resolvers.items()
        }
        result["normalised_missing_required_field_counts"] = normalised_missing
        result["missing_required_field_counts"] = dict(normalised_missing)

        raw_target_rows = sum(1 for row in rows if first_value(row, *TARGET_MP_ALIASES))
        recorded_side_rows = sum(1 for row in rows if row.get("recorded_side") not in (None, ""))
        raw_recorded_vote_rows = sum(1 for row in rows if row.get("recorded_vote") not in (None, ""))
        if rows and not any(normalised_missing.values()):
            classification = "expected_source_import_distinction_with_explicit_normalisation_boundary"
        else:
            classification = "unresolved_missing_import_fields"
        result["normalisation"] = {
            "classification": classification,
            "target_mp_resolution": (
                "row"
                if raw_target_rows == len(rows) and rows
                else "manifest"
                if context_target_mp and raw_target_rows < len(rows)
                else "unresolved"
            ),
            "recorded_vote_resolution": (
                "recorded_vote"
                if raw_recorded_vote_rows == len(rows) and rows
                else "recorded_side_alias"
                if recorded_side_rows == len(rows) and rows
                else "mixed_or_unresolved"
            ),
            "source_trace_policy": "preserve_original_row",
            "evidence_meaning_changed": False,
        }

        quality_counts: dict[str, int] = {}
        for row in rows:
            quality = str(row.get("meaning_quality") or row.get("meaningQuality") or "")
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        result["meaning_quality_counts"] = quality_counts
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result["errors"].append(str(exc))

    return result



def newest_files(path: Path, limit: int = 10) -> list[dict[str, Any]]:
    if not path.is_dir():
        return []
    records: list[dict[str, Any]] = []
    try:
        for item in path.iterdir():
            if item.is_file() and not item.is_symlink():
                records.append(
                    {
                        "name": item.name,
                        "size_bytes": item.stat().st_size,
                        "modified_at": iso_mtime(item),
                    }
                )
    except OSError:
        return []
    records.sort(key=lambda item: item["modified_at"], reverse=True)
    return records[:limit]


def collect_inventory(archive_root: Path, repo_root: Path) -> dict[str, Any]:
    database_path = archive_root / DEFAULT_DATABASE
    seed_path = repo_root / DEFAULT_SEED_ROWS
    seed_manifest_path = repo_root / DEFAULT_SEED_MANIFEST
    disk: dict[str, Any] = {}
    if archive_root.exists():
        try:
            usage = shutil.disk_usage(archive_root)
            disk = {
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "free_gb": round(usage.free / (1024**3), 3),
            }
        except OSError as exc:
            disk = {"error": str(exc)}

    directories = {
        relative: path_summary(archive_root / relative)
        for relative in EXPECTED_ARCHIVE_DIRS
    }

    raw_summaries = {
        relative: summarise_tree(archive_root / relative)
        for relative in (
            "raw/commons-votes",
            "raw/members",
            "raw/parlparse",
            "raw/hansard",
            "raw/interests",
            "raw/committees",
        )
    }

    return {
        "audit": {
            "generated_at": utc_now(),
            "mode": "read_only",
            "network_access_used": False,
            "archive_modified": False,
            "database_modified": False,
        },
        "archive_root": path_summary(archive_root),
        "repo_root": path_summary(repo_root),
        "disk": disk,
        "expected_directories": directories,
        "raw_area_summaries": raw_summaries,
        "database": inspect_database(database_path),
        "seed_rows": inspect_seed_rows(seed_path, seed_manifest_path),
        "recent_import_logs": newest_files(archive_root / "logs/imports"),
        "recent_validation_logs": newest_files(archive_root / "logs/validation"),
        "recent_backups": newest_files(archive_root / "backups"),
        "git": {
            "head": run_read_only_git(repo_root, ["rev-parse", "HEAD"]),
            "branch": run_read_only_git(repo_root, ["branch", "--show-current"]),
            "status": run_read_only_git(repo_root, ["status", "--short", "--branch"]),
        },
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    def cell(value: Any) -> str:
        return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    audit = report["audit"]
    lines.append("# Story Evidence Collector Server Inventory")
    lines.append("")
    lines.append(f"Generated: `{audit['generated_at']}`")
    lines.append("")
    lines.append("## Safety statement")
    lines.append("")
    lines.append("- Read-only inspection only.")
    lines.append("- No network access used.")
    lines.append("- No imports, database writes, permission changes, deletions, moves, or repository updates performed.")
    lines.append("- Raw evidence contents are not included in this report.")
    lines.append("")

    lines.append("## Archive and disk")
    lines.append("")
    archive = report["archive_root"]
    disk = report["disk"]
    lines.append(markdown_table(
        ["Item", "Value"],
        [
            ["Archive root", archive.get("path")],
            ["Exists", archive.get("exists")],
            ["Mode", archive.get("mode")],
            ["UID:GID", f"{archive.get('uid')}:{archive.get('gid')}"],
            ["Free space", human_bytes(int(disk.get("free_bytes", 0))) if "free_bytes" in disk else disk.get("error", "")],
            ["Free GB", disk.get("free_gb", "")],
        ],
    ))
    lines.append("")

    lines.append("## Expected folders")
    lines.append("")
    lines.append(markdown_table(
        ["Folder", "Exists", "Mode", "UID:GID"],
        [
            [name, details.get("exists"), details.get("mode"), f"{details.get('uid')}:{details.get('gid')}"]
            for name, details in report["expected_directories"].items()
        ],
    ))
    lines.append("")

    lines.append("## Raw evidence areas")
    lines.append("")
    lines.append(markdown_table(
        ["Area", "Exists", "Files", "Directories", "Stored size", "Truncated"],
        [
            [
                name,
                details.get("exists"),
                details.get("files"),
                details.get("directories"),
                human_bytes(int(details.get("bytes", 0))),
                details.get("truncated"),
            ]
            for name, details in report["raw_area_summaries"].items()
        ],
    ))
    lines.append("")

    database = report["database"]
    db_file = database["file"]
    lines.append("## SQLite evidence cache")
    lines.append("")
    lines.append(markdown_table(
        ["Item", "Value"],
        [
            ["Path", db_file.get("path")],
            ["Exists", db_file.get("exists")],
            ["Size", human_bytes(int(db_file.get("size_bytes", 0))) if db_file.get("size_bytes") is not None else ""],
            ["Modified", db_file.get("modified_at")],
            ["SHA-256", db_file.get("sha256", "")],
            ["Opened read-only", database.get("opened_read_only")],
            ["Quick check", ", ".join(str(item) for item in database.get("quick_check", []))],
            ["Distinct target MPs", database.get("distinct_target_mps")],
            ["Earliest division date", database.get("vote_date_range", {}).get("earliest", "")],
            ["Latest division date", database.get("vote_date_range", {}).get("latest", "")],
        ],
    ))
    lines.append("")

    lines.append("### Table counts")
    lines.append("")
    lines.append(markdown_table(
        ["Table", "Rows", "Columns"],
        [
            [name, details.get("row_count"), ", ".join(details.get("columns", []))]
            for name, details in database.get("tables", {}).items()
        ],
    ))
    lines.append("")

    if database.get("source_system_counts"):
        lines.append("### Source-system counts")
        lines.append("")
        source_rows: list[list[Any]] = []
        for table, entries in database["source_system_counts"].items():
            for entry in entries:
                source_rows.append([table, entry.get("value"), entry.get("count")])
        lines.append(markdown_table(["Table", "Source system", "Rows"], source_rows))
        lines.append("")

    if database.get("meaning_quality_counts"):
        lines.append("### Meaning-quality counts")
        lines.append("")
        lines.append(markdown_table(
            ["Meaning quality", "Rows"],
            [[entry.get("value"), entry.get("count")] for entry in database["meaning_quality_counts"]],
        ))
        lines.append("")

    seed = report["seed_rows"]
    seed_file = seed["file"]
    manifest_file = seed.get("manifest", {})
    normalisation = seed.get("normalisation", {})
    lines.append("## January 2003 seed rows")
    lines.append("")
    lines.append(markdown_table(
        ["Item", "Value"],
        [
            ["Rows path", seed_file.get("path")],
            ["Rows file exists", seed_file.get("exists")],
            ["Rows size", human_bytes(int(seed_file.get("size_bytes", 0))) if seed_file.get("size_bytes") is not None else ""],
            ["Rows modified", seed_file.get("modified_at")],
            ["Rows SHA-256", seed_file.get("sha256", "")],
            ["Manifest path", manifest_file.get("path", "")],
            ["Manifest exists", manifest_file.get("exists", False)],
            ["Rows", seed.get("row_count")],
            ["Raw exact canonical omissions", json.dumps(seed.get("source_shape_missing_canonical_field_counts", {}), sort_keys=True)],
            ["Missing after normalisation", json.dumps(seed.get("normalised_missing_required_field_counts", {}), sort_keys=True)],
            ["Boundary classification", normalisation.get("classification", "")],
            ["Target MP resolution", normalisation.get("target_mp_resolution", "")],
            ["Recorded vote resolution", normalisation.get("recorded_vote_resolution", "")],
            ["Meaning quality", json.dumps(seed.get("meaning_quality_counts", {}), sort_keys=True)],
        ],
    ))
    lines.append("")
    for heading, key in (
        ("Recent import logs", "recent_import_logs"),
        ("Recent validation logs", "recent_validation_logs"),
        ("Recent backups", "recent_backups"),
    ):
        lines.append(f"## {heading}")
        lines.append("")
        records = report.get(key, [])
        if records:
            lines.append(markdown_table(
                ["Name", "Size", "Modified"],
                [[item.get("name"), human_bytes(int(item.get("size_bytes", 0))), item.get("modified_at")] for item in records],
            ))
        else:
            lines.append("None found.")
        lines.append("")

    lines.append("## Repository checkout")
    lines.append("")
    git = report["git"]
    lines.append(markdown_table(
        ["Check", "Return code", "Result", "Error"],
        [
            ["HEAD", git["head"].get("returncode"), git["head"].get("stdout"), git["head"].get("stderr")],
            ["Branch", git["branch"].get("returncode"), git["branch"].get("stdout"), git["branch"].get("stderr")],
            ["Status", git["status"].get("returncode"), git["status"].get("stdout"), git["status"].get("stderr")],
        ],
    ))
    lines.append("")

    errors: list[str] = []
    errors.extend(database.get("errors", []))
    errors.extend(seed.get("errors", []))
    for details in report["raw_area_summaries"].values():
        errors.extend(details.get("errors", []))
    lines.append("## Audit errors")
    lines.append("")
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("No audit errors recorded.")
    lines.append("")

    lines.append("## Interpretation boundary")
    lines.append("")
    lines.append("This inventory reports what files and database records exist. It does not prove that the underlying source coverage is complete, current, correctly interpreted, or publication-ready.")
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Story Evidence Collector server inventory.")
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = collect_inventory(args.archive_root, args.repo_root)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(build_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
