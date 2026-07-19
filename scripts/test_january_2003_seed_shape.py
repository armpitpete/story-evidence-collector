#!/usr/bin/env python3
"""Regression proof for January 2003 source-shape to SQLite normalisation."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server_imports"))

import audit_server_state as audit  # noqa: E402
import build_server_evidence_cache as importer  # noqa: E402


def main() -> int:
    rows = [
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
    ]
    manifest = {
        "batch_id": "parlparse_2003_01",
        "target_mp": "Corbyn, Jeremy",
        "target_member_id": "185",
    }

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        rows_path = root / "parlparse_2003_01_rows.json"
        manifest_path = root / "parlparse_2003_01_manifest.json"
        database_path = root / "mp_evidence_cache.sqlite"
        rows_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        context = importer.load_seed_manifest(manifest_path)
        importer.validate_seed_context("parlparse_2003_01", context)
        normalised, error = importer.normalise_seed_row(
            rows[0], "parlparse_2003_01", rows_path, context
        )
        assert error is None
        assert normalised is not None
        assert normalised["division_date"] == rows[0]["date"]
        assert normalised["recorded_vote"] == rows[0]["recorded_side"]
        assert normalised["vote_side"] == rows[0]["recorded_side"]
        assert normalised["target_mp"] == manifest["target_mp"]
        assert normalised["source_member_id"] == manifest["target_member_id"]
        assert normalised["meaning_quality"] == "needs_review"
        assert json.loads(normalised["source_trace"]) == rows[0]
        assert "target_mp" not in json.loads(normalised["source_trace"])
        assert "recorded_vote" not in json.loads(normalised["source_trace"])

        missing_context_row, missing_context_error = importer.normalise_seed_row(
            rows[0], "parlparse_2003_01", rows_path, {}
        )
        assert missing_context_row is None
        assert missing_context_error == "Skipped row missing required fields: target_mp"

        schema = (ROOT / "server_imports/mp_evidence_cache_schema.sql").read_text(encoding="utf-8")
        importer.initialise_database(database_path, schema)
        written, skipped, warnings = importer.apply_seed_rows(
            database_path,
            "parlparse_2003_01",
            rows_path,
            rows,
            "fixture-import-run",
            seed_context=context,
        )
        assert written == 3
        assert skipped == 0
        assert warnings == []

        with sqlite3.connect(database_path) as connection:
            values = connection.execute(
                "SELECT recorded_vote, vote_side, target_mp, meaning_quality, source_trace "
                "FROM member_votes ORDER BY division_key"
            ).fetchall()
        assert len(values) == 3
        assert {value[0] for value in values} == {"Aye", "No", "Not recorded"}
        assert all(value[0] == value[1] for value in values)
        assert all(value[2] == "Corbyn, Jeremy" for value in values)
        assert all(value[3] == "needs_review" for value in values)
        assert all("recorded_side" in json.loads(value[4]) for value in values)
        assert all("recorded_vote" not in json.loads(value[4]) for value in values)
        assert all("target_mp" not in json.loads(value[4]) for value in values)

        audit_result = audit.inspect_seed_rows(rows_path, manifest_path)
        assert audit_result["row_count"] == 3
        assert audit_result["source_shape_missing_canonical_field_counts"] == {
            "division_id": 0,
            "division_date": 3,
            "target_mp": 3,
            "recorded_vote": 3,
        }
        assert audit_result["normalised_missing_required_field_counts"] == {
            "division_id": 0,
            "division_date": 0,
            "target_mp": 0,
            "recorded_vote": 0,
        }
        assert audit_result["normalisation"]["classification"] == (
            "expected_source_import_distinction_with_explicit_normalisation_boundary"
        )
        assert audit_result["normalisation"]["target_mp_resolution"] == "manifest"
        assert audit_result["normalisation"]["recorded_vote_resolution"] == "recorded_side_alias"
        assert audit_result["normalisation"]["evidence_meaning_changed"] is False

        unresolved = audit.inspect_seed_rows(rows_path)
        assert unresolved["normalised_missing_required_field_counts"]["target_mp"] == 3
        assert unresolved["normalisation"]["classification"] == "unresolved_missing_import_fields"

        mismatch_path = root / "wrong_manifest.json"
        mismatch_path.write_text(json.dumps({**manifest, "batch_id": "other_batch"}), encoding="utf-8")
        mismatch = importer.load_seed_manifest(mismatch_path)
        try:
            importer.validate_seed_context("parlparse_2003_01", mismatch)
        except ValueError as exc:
            assert "identity mismatch" in str(exc)
        else:
            raise AssertionError("Mismatched manifest identity was accepted")

    print("PASS: January 2003 source shape resolves deterministically to canonical SQLite fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
