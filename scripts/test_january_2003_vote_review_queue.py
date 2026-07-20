#!/usr/bin/env python3
"""Disposable regression proof for the January 2003 vote-review queue."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server_imports"))

import build_january_2003_vote_review_queue as queue  # noqa: E402


FIXTURE_ROWS = (
    {
        "date": "2003-01-14",
        "division_id": "uk.org.publicwhip/debate/2003-01-14a.77.0",
        "division_number": "77",
        "motion_title": "Fixture division two",
        "recorded_side": "No",
        "meaning_quality": "needs_review",
        "source_system": "parlparse",
        "source_url": "https://example.invalid/division/77",
        "source_xml_url": "https://example.invalid/debates2003-01-14.xml",
        "evidence_status": "mp_found_in_no_list",
    },
    {
        "date": "2003-01-07",
        "division_id": "uk.org.publicwhip/debate/2003-01-07a.42.0",
        "division_number": "42",
        "motion_title": "Fixture division one",
        "recorded_side": "Aye",
        "meaning_quality": "needs_review",
        "source_system": "parlparse",
        "source_url": "https://example.invalid/division/42",
        "source_xml_url": "https://example.invalid/debates2003-01-07.xml",
        "evidence_status": "mp_found_in_aye_list",
    },
    {
        "date": "2003-01-31",
        "division_id": "uk.org.publicwhip/debate/2003-01-31a.99.0",
        "division_number": "99",
        "motion_title": "Fixture division three",
        "recorded_side": "Not recorded",
        "meaning_quality": "needs_review",
        "source_system": "parlparse",
        "source_url": "https://example.invalid/division/99",
        "source_xml_url": "https://example.invalid/debates2003-01-31.xml",
        "evidence_status": "mp_not_found_in_sample_division",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_database(
    database_path: Path,
    rows: tuple[dict[str, str], ...] = FIXTURE_ROWS,
) -> None:
    schema = (ROOT / "server_imports/mp_evidence_cache_schema.sql").read_text(
        encoding="utf-8"
    )
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema)
        connection.execute(
            """
            INSERT INTO imports (
              import_run_id, importer_name, importer_version, started_at,
              finished_at, dry_run, network_access_used, rows_read,
              rows_written, warning_count, error_count, status
            ) VALUES (
              'fixture-import', 'fixture', '1', '2003-02-01T00:00:00+00:00',
              '2003-02-01T00:00:00+00:00', 0, 0, ?, ?, 0, 0, 'ok'
            )
            """,
            (len(rows), len(rows)),
        )
        connection.execute(
            """
            INSERT INTO members (
              member_key, source_system, source_member_id, display_name,
              source_trace, import_run_id
            ) VALUES (
              'parlparse|member|185', 'parlparse', '185',
              'Corbyn, Jeremy', '{}', 'fixture-import'
            )
            """
        )
        for row in rows:
            division_key = f"parlparse|division|{row['division_id']}"
            vote_key = f"parlparse|{row['division_id']}|Corbyn, Jeremy"
            trace = json.dumps(row, sort_keys=True, ensure_ascii=False)
            connection.execute(
                """
                INSERT INTO divisions (
                  division_key, source_system, division_id, division_date,
                  division_title, house, source_url, source_path,
                  source_trace, import_run_id
                ) VALUES (?, 'parlparse', ?, ?, ?, 'commons', ?, ?, ?, 'fixture-import')
                """,
                (
                    division_key,
                    row["division_id"],
                    row["date"],
                    row["motion_title"],
                    row["source_url"],
                    "/private/fixture.json",
                    trace,
                ),
            )
            connection.execute(
                """
                INSERT INTO member_votes (
                  vote_key, source_system, division_key, member_key, target_mp,
                  recorded_vote, vote_side, meaning_quality, source_url,
                  source_path, source_trace, import_run_id
                ) VALUES (
                  ?, 'parlparse', ?, 'parlparse|member|185', 'Corbyn, Jeremy',
                  ?, ?, ?, ?, ?, ?, 'fixture-import'
                )
                """,
                (
                    vote_key,
                    division_key,
                    row["recorded_side"],
                    row["recorded_side"],
                    row["meaning_quality"],
                    row["source_url"],
                    "/private/fixture.json",
                    trace,
                ),
            )
        connection.commit()


def assert_refused(callable_object, fragment: str) -> None:
    try:
        callable_object()
    except queue.QueueValidationError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"Expected QueueValidationError containing {fragment!r}")


def main() -> int:
    schema_document = json.loads(
        (ROOT / "server_imports/january_2003_vote_review_queue_schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        schema_document["properties"]["schema_version"]["const"]
        == queue.SCHEMA_VERSION
    )
    review_schema = (
        schema_document["properties"]["items"]["items"]["properties"]["review"]
    )
    assert all(
        review_schema["properties"][field]["const"] == ""
        for field in queue.REVIEW_FIELDS
    )

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        database_path = root / "mp_evidence_cache.sqlite"
        create_database(database_path)
        before_hash = sha256(database_path)

        packet = queue.build_packet(
            database_path,
            expected_row_count=3,
        )
        queue.validate_packet(packet)

        assert packet["scope"] == {
            "date_from": "2003-01-01",
            "date_to": "2003-01-31",
            "target_mp": "Corbyn, Jeremy",
            "row_count": 3,
        }
        assert [item["division"]["division_date"] for item in packet["items"]] == [
            "2003-01-07",
            "2003-01-14",
            "2003-01-31",
        ]
        assert [item["queue_state"] for item in packet["items"]] == [
            "recorded_aye",
            "recorded_no",
            "not_recorded",
        ]
        assert all(
            item["vote"]["meaning_quality"] == "needs_review"
            for item in packet["items"]
        )
        assert all(
            all(item["review"][field] == "" for field in queue.REVIEW_FIELDS)
            for item in packet["items"]
        )

        original_by_id = {row["division_id"]: row for row in FIXTURE_ROWS}
        for item in packet["items"]:
            division_id = item["division"]["division_id"]
            assert item["source_trace"] == original_by_id[division_id]
            assert item["division"]["source_xml_url"] == original_by_id[
                division_id
            ]["source_xml_url"]
            assert item["vote"]["evidence_status"] == original_by_id[
                division_id
            ]["evidence_status"]

        first_output = root / "first"
        second_output = root / "second"
        first_json, first_markdown = queue.write_packet(packet, first_output)
        second_json, second_markdown = queue.write_packet(packet, second_output)
        assert first_json.read_bytes() == second_json.read_bytes()
        assert first_markdown.read_bytes() == second_markdown.read_bytes()
        assert sha256(database_path) == before_hash

        with queue.open_read_only_database(database_path) as connection:
            try:
                connection.execute("DELETE FROM member_votes")
            except sqlite3.OperationalError as exc:
                assert "readonly" in str(exc).casefold() or "read-only" in str(exc).casefold()
            else:
                raise AssertionError("Read-only connection accepted a database write")

        assert_refused(
            lambda: queue.build_packet(database_path, expected_row_count=33),
            "Expected 33 rows but found 3",
        )
        assert (
            queue.classify_technical_state(
                "Aye", "Aye", "mp_found_in_no_list"
            )
            == "source_ambiguity"
        )

        incomplete_path = root / "incomplete.sqlite"
        incomplete_rows = tuple(
            {key: value for key, value in row.items() if key != "source_xml_url"}
            if index == 0
            else row
            for index, row in enumerate(FIXTURE_ROWS)
        )
        create_database(incomplete_path, incomplete_rows)
        assert_refused(
            lambda: queue.build_packet(incomplete_path, expected_row_count=3),
            "source_xml_url is blank",
        )

        ambiguous_path = root / "ambiguous.sqlite"
        ambiguous_rows = tuple(
            {**row, "evidence_status": "mp_found_in_no_list"}
            if row["recorded_side"] == "Aye"
            else row
            for row in FIXTURE_ROWS
        )
        create_database(ambiguous_path, ambiguous_rows)
        assert_refused(
            lambda: queue.build_packet(ambiguous_path, expected_row_count=3),
            "source_ambiguity",
        )

        outside = root.parent / "outside-review-packet"
        assert_refused(
            lambda: queue.resolve_inside_root(root, outside),
            "Unsafe path outside archive root",
        )

    print(
        "PASS: deterministic read-only vote-review queue preserves evidence, "
        "keeps decisions blank and refuses incomplete or ambiguous records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
