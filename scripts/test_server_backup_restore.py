#!/usr/bin/env python3
"""Regression tests for private archive backup and disposable restore tooling."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Callable, TypeVar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server_imports.create_server_backup import (  # noqa: E402
    MANIFEST_NAME,
    BackupError,
    create_backup,
    database_sidecar_paths,
    file_sha256,
)
from server_imports.verify_restore_server_backup import (  # noqa: E402
    VerificationError,
    restore_backup,
    verify_backup,
)

T = TypeVar("T", bound=BaseException)


def expect_error(error_type: type[T], action: Callable[[], object], contains: str) -> T:
    try:
        action()
    except error_type as exc:
        if contains not in str(exc):
            raise AssertionError(
                f"expected {error_type.__name__} containing {contains!r}, got: {exc}"
            ) from exc
        return exc
    raise AssertionError(f"expected {error_type.__name__}: {contains}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_sample_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            CREATE TABLE sources (
                source_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL
            );
            CREATE TABLE member_votes (
                vote_key TEXT PRIMARY KEY,
                target_mp TEXT NOT NULL,
                recorded_vote TEXT NOT NULL,
                meaning_quality TEXT NOT NULL
            );
            INSERT INTO sources VALUES ('source-1', 'Fixture source');
            INSERT INTO member_votes VALUES ('vote-1', 'Fixture MP', 'aye', 'needs_review');
            """
        )
        connection.commit()
    finally:
        connection.close()


def create_sample_archive(root: Path) -> None:
    for relative in (
        "raw/commons-votes",
        "raw/members",
        "raw/parlparse",
        "raw/hansard",
        "raw/interests",
        "raw/committees",
        "reports/coverage",
        "reports/mp",
        "reports/divisions",
        "logs/imports",
        "logs/validation",
        "backups",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)

    write_text(root / "raw/parlparse/source.json", '{"fixture": true}\n')
    write_text(root / "reports/coverage/current.md", "# Fixture coverage\n")
    write_text(root / "logs/imports/run.json", '{"status": "ok"}\n')
    create_sample_database(root / "db/mp_evidence_cache.sqlite")


def archive_fingerprint(root: Path, include_database: bool = True) -> dict[str, str]:
    fingerprint: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "backups":
            continue
        if not include_database and relative.as_posix() == "db/mp_evidence_cache.sqlite":
            continue
        if path.is_file():
            fingerprint[relative.as_posix()] = file_sha256(path)
    return fingerprint


def database_content(path: Path) -> dict[str, list[tuple]]:
    connection = sqlite3.connect(path)
    try:
        return {
            "sources": connection.execute(
                "SELECT source_id, source_name FROM sources ORDER BY source_id"
            ).fetchall(),
            "member_votes": connection.execute(
                "SELECT vote_key, target_mp, recorded_vote, meaning_quality "
                "FROM member_votes ORDER BY vote_key"
            ).fetchall(),
        }
    finally:
        connection.close()


def rewrite_manifest(backup: Path, mutator: Callable[[dict], None]) -> None:
    path = backup / MANIFEST_NAME
    manifest = json.loads(path.read_text(encoding="utf-8"))
    mutator(manifest)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_manifest_file_hash(manifest: dict, relative_path: str, file_path: Path) -> None:
    for entry in manifest["entries"]:
        if entry.get("path") == relative_path and entry.get("type") == "file":
            entry["size_bytes"] = file_path.stat().st_size
            entry["sha256"] = file_sha256(file_path)
            return
    raise AssertionError(f"manifest file entry not found: {relative_path}")


def test_happy_path(work: Path) -> None:
    archive = work / "archive"
    create_sample_archive(archive)
    before = archive_fingerprint(archive)

    backup = create_backup(
        archive_root=archive,
        backup_name="backup-test-happy-path",
    )
    after = archive_fingerprint(archive)
    assert before == after, "backup creation changed source archive file content"
    assert backup.parent == archive / "backups"
    manifest_entries = json.loads(
        (backup / MANIFEST_NAME).read_text(encoding="utf-8")
    )["entries"]
    assert any(
        entry.get("path") == "backups" and entry.get("type") == "directory"
        for entry in manifest_entries
    )
    assert not any(
        entry.get("path", "").startswith("backups/") for entry in manifest_entries
    )

    report = verify_backup(backup)
    assert report["database_quick_check"] == ["ok"]
    assert report["checked_files"] == 4

    restored = work / "restored-archive"
    restore_report = restore_backup(backup, restored)
    assert restored.exists()
    assert (restored / "backups").is_dir()
    assert not any((restored / "backups").iterdir())
    assert restore_report["restored_verification"]["database_quick_check"] == ["ok"]
    assert archive_fingerprint(restored, include_database=False) == archive_fingerprint(
        archive, include_database=False
    )
    assert database_content(restored / "db/mp_evidence_cache.sqlite") == database_content(
        archive / "db/mp_evidence_cache.sqlite"
    )

    expect_error(
        VerificationError,
        lambda: restore_backup(backup, restored),
        "restore target already exists",
    )


def test_checksum_corruption(work: Path) -> None:
    archive = work / "checksum-archive"
    create_sample_archive(archive)
    backup = create_backup(
        archive_root=archive,
        backup_name="backup-test-checksum-corruption",
    )
    corrupted = backup / "archive/raw/parlparse/source.json"
    corrupted.write_text("corrupted\n", encoding="utf-8")
    expect_error(VerificationError, lambda: verify_backup(backup), "mismatch")


def test_manifest_path_traversal(work: Path) -> None:
    archive = work / "traversal-archive"
    create_sample_archive(archive)
    backup = create_backup(
        archive_root=archive,
        backup_name="backup-test-path-traversal",
    )

    def mutate(manifest: dict) -> None:
        manifest["entries"][0]["path"] = "../escape"

    rewrite_manifest(backup, mutate)
    expect_error(VerificationError, lambda: verify_backup(backup), "unsafe")


def test_damaged_sqlite_even_with_matching_manifest_hash(work: Path) -> None:
    archive = work / "sqlite-archive"
    create_sample_archive(archive)
    backup = create_backup(
        archive_root=archive,
        backup_name="backup-test-damaged-sqlite",
    )
    database_relative = "db/mp_evidence_cache.sqlite"
    database = backup / "archive" / database_relative
    database.write_bytes(b"not a sqlite database\n")

    def mutate(manifest: dict) -> None:
        update_manifest_file_hash(manifest, database_relative, database)

    rewrite_manifest(backup, mutate)
    expect_error(
        VerificationError,
        lambda: verify_backup(backup),
        "SQLite",
    )


def test_sqlite_sidecars_are_excluded(work: Path) -> None:
    archive = work / "sidecar-archive"
    create_sample_archive(archive)
    database = archive / "db/mp_evidence_cache.sqlite"
    connection = sqlite3.connect(database)
    try:
        mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        assert str(mode).lower() == "wal"
        connection.execute(
            "INSERT INTO member_votes VALUES (?, ?, ?, ?)",
            ("vote-2", "Fixture MP", "no", "needs_review"),
        )
        connection.commit()

        sidecars = [
            archive / "db/mp_evidence_cache.sqlite-wal",
            archive / "db/mp_evidence_cache.sqlite-shm",
        ]
        assert all(path.exists() for path in sidecars)

        backup = create_backup(
            archive_root=archive,
            backup_name="backup-test-sidecar-exclusion",
        )
        manifest = json.loads((backup / MANIFEST_NAME).read_text(encoding="utf-8"))
        manifest_paths = {entry["path"] for entry in manifest["entries"]}
        for sidecar in sidecars:
            relative = sidecar.relative_to(archive).as_posix()
            assert relative not in manifest_paths
            assert not (backup / "archive" / relative).exists()
            assert sidecar.exists(), "backup creation must not delete source sidecars"
        assert verify_backup(backup)["database_quick_check"] == ["ok"]
        restored = work / "sidecar-restored"
        restore_backup(backup, restored)
        restored_votes = database_content(
            restored / "db/mp_evidence_cache.sqlite"
        )["member_votes"]
        assert len(restored_votes) == 2
    finally:
        connection.close()

    excluded = {
        path.as_posix()
        for path in database_sidecar_paths(Path("db/mp_evidence_cache.sqlite"))
    }
    assert "db/mp_evidence_cache.sqlite-journal" in excluded


def test_source_symlink_refusal(work: Path) -> None:
    archive = work / "symlink-archive"
    create_sample_archive(archive)
    target = archive / "raw/parlparse/source.json"
    symlink = archive / "raw/parlparse/unsafe-link.json"
    try:
        symlink.symlink_to(target)
    except (OSError, NotImplementedError):
        return
    expect_error(
        BackupError,
        lambda: create_backup(
            archive_root=archive,
            backup_name="backup-test-symlink-refusal",
        ),
        "symlink",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="story-evidence-backup-test-") as temporary:
        work = Path(temporary)
        test_happy_path(work)
        test_checksum_corruption(work)
        test_manifest_path_traversal(work)
        test_damaged_sqlite_even_with_matching_manifest_hash(work)
        test_sqlite_sidecars_are_excluded(work)
        test_source_symlink_refusal(work)
    print("PASS: server backup and disposable restore regression suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
