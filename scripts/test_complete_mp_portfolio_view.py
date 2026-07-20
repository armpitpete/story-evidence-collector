#!/usr/bin/env python3
"""Deterministic regression proof for the read-only MP Portfolio view."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.complete_mp_portfolio_view import (  # noqa: E402
    DEFAULT_FIXTURE_PATH,
    build_portfolio_view,
    canonical_output_filenames,
    generate_temporary_preview,
    load_fixture_portfolio,
)
from scripts.generate_complete_mp_report import (  # noqa: E402
    CANONICAL_SECTIONS,
    load_json,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    report = load_json(DEFAULT_FIXTURE_PATH)
    model = build_portfolio_view(report)
    loaded_model = load_fixture_portfolio()

    require(model == loaded_model, "Fixture loading must produce the same display model.")
    require(model["subject"]["display_name"] == "Corbyn, Jeremy", "Fixture subject changed.")
    require(model["publication"]["status"] == "not_ready", "Fixture must remain not_ready.")
    require(model["publication"]["human_review_required"] is True, "Human review must remain required.")
    require(model["publication"]["public_output_authorised"] is False, "Public output must remain unauthorised.")

    expected_section_ids = [section_id for section_id, _ in CANONICAL_SECTIONS]
    actual_section_ids = [section["section_id"] for section in model["sections"]]
    require(actual_section_ids == expected_section_ids, "All 13 sections must remain in canonical order.")
    require(len(model["sections"]) == 13, "Exactly 13 canonical sections are required.")

    allowed_statuses = {
        "complete",
        "partial",
        "not_available",
        "not_researched",
        "human_review_required",
    }
    for position, section in enumerate(model["sections"], start=1):
        require(section["position"] == position, "Section positions must be deterministic.")
        require(section["status"] in allowed_statuses, "Unexpected coverage status.")
        require(bool(section["status_message"]), "Coverage status wording must remain visible.")
        require(bool(section["summary"]), "Every section must keep an explicit summary.")

        for record_group in ("facts", "claims", "relationships"):
            for record in section[record_group]:
                require(record["sources"], f"{record_group} record lost its source resolution.")
                for source in record["sources"]:
                    require(bool(source["source_id"]), "Resolved source ID is missing.")
                    require(bool(source["title"]), "Resolved source title is missing.")
                    require(bool(source["limitations"]), "Resolved source limitations are missing.")

    identity = model["sections"][0]
    require(identity["facts"], "Identity fixture fact must be visible.")
    require(identity["coverage_gaps"], "Identity coverage gap must be visible.")

    voting = next(
        section
        for section in model["sections"]
        if section["section_id"] == "voting_record_and_coverage"
    )
    require(len(voting["facts"]) == 2, "Voting fixture facts must remain visible.")
    require(len(voting["claims"]) == 1, "Voting coverage claim must remain visible.")
    require(voting["coverage_gaps"], "Voting coverage gap must remain visible.")

    expected_outputs = canonical_output_filenames(report)
    require(model["output_filenames"] == expected_outputs, "Canonical output set changed.")
    require(len(expected_outputs) == 5, "Generator must expose exactly five outputs.")

    first_preview = generate_temporary_preview(report)
    second_preview = generate_temporary_preview(report)
    require(first_preview["removed"] is True, "First temporary preview was not removed.")
    require(second_preview["removed"] is True, "Second temporary preview was not removed.")
    require(not Path(first_preview["temporary_directory"]).exists(), "First temporary directory still exists.")
    require(not Path(second_preview["temporary_directory"]).exists(), "Second temporary directory still exists.")
    require(ROOT not in Path(first_preview["temporary_directory"]).parents, "Preview was written inside the repository.")
    require(ROOT not in Path(second_preview["temporary_directory"]).parents, "Preview was written inside the repository.")
    require(
        first_preview["files"] == second_preview["files"],
        "Repeated disposable generation must produce identical filenames, sizes and hashes.",
    )
    require(
        [item["filename"] for item in first_preview["files"]] == expected_outputs,
        "Disposable generator output names do not match the canonical set.",
    )

    ui_path = ROOT / "twis_source_engine_ui_v24.py"
    ui_source = ui_path.read_text(encoding="utf-8")
    compile(ui_source, str(ui_path), "exec")
    require("def render_simple_mode()" in ui_source, "Simple mode entry point was removed.")
    require("def render_advanced_mode()" in ui_source, "Advanced mode entry point was removed.")
    require("def render_mp_portfolio()" in ui_source, "MP Portfolio entry point is missing.")
    require(
        'options=["Simple", "MP Portfolio", "Advanced"]' in ui_source,
        "Sidebar must preserve Simple and Advanced while adding MP Portfolio.",
    )
    require('if view == "Simple":' in ui_source, "Simple route changed unexpectedly.")
    require('elif view == "MP Portfolio":' in ui_source, "MP Portfolio route is missing.")
    require("render_advanced_mode()" in ui_source, "Advanced route changed unexpectedly.")

    print("PASS — Complete MP Portfolio view is validated, deterministic and read-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
