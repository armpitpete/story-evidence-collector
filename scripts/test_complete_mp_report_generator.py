#!/usr/bin/env python3
"""Fixture regression test for Complete MP Report v1 generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from generate_complete_mp_report import load_json, validate_report, write_outputs

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)
SCHEMA = ROOT / "schemas" / "complete-mp-report-v1.schema.json"

EXPECTED_FILENAMES = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}


def read_outputs(folder: Path) -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(folder.iterdir())
        if path.is_file()
    }


def main() -> int:
    json.loads(SCHEMA.read_text(encoding="utf-8"))

    report = load_json(FIXTURE)
    validate_report(report)

    assert report["publication"]["status"] == "not_ready"
    assert len(report["sections"]) == 13

    with (
        tempfile.TemporaryDirectory() as first_dir,
        tempfile.TemporaryDirectory() as second_dir,
    ):
        first = Path(first_dir)
        second = Path(second_dir)

        write_outputs(report, first)
        write_outputs(report, second)

        first_outputs = read_outputs(first)
        second_outputs = read_outputs(second)

        assert set(first_outputs) == EXPECTED_FILENAMES
        assert first_outputs == second_outputs
        assert (
            "# Complete MP Report — Corbyn, Jeremy"
            in first_outputs["corbyn-jeremy-full-profile.md"]
        )
        assert "not_ready" in first_outputs["corbyn-jeremy-human-review.md"]
        assert (
            "Historic vote coverage is incomplete"
            in first_outputs["corbyn-jeremy-coverage-report.md"]
        )

    print("PASS: Complete MP Report v1 fixture generation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
