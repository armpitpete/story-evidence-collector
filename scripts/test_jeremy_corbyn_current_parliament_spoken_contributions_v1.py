#!/usr/bin/env python3
"""Verify the fixed spoken baseline with the exact later EDM extension."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import test_jeremy_corbyn_current_parliament_early_day_motions_fixture_integration_v1 as edm  # noqa: E402

ORIGINAL_COMMIT = "426920b968927a4293b595eeda726d1b57d388bf"
ORIGINAL_SCRIPT_PATH = (
    "scripts/test_jeremy_corbyn_current_parliament_spoken_contributions_v1.py"
)
FIXTURE_RELATIVE_PATH = (
    "fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json"
)
FIXTURE_PATH = ROOT / FIXTURE_RELATIVE_PATH


def git_show_text(commit: str, relative_path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
    ).decode("utf-8")


def load_original_namespace() -> dict[str, Any]:
    source = git_show_text(ORIGINAL_COMMIT, ORIGINAL_SCRIPT_PATH)
    namespace: dict[str, Any] = {
        "__name__": "_fixed_spoken_contributions_regression",
        "__file__": str(ROOT / ORIGINAL_SCRIPT_PATH),
    }
    exec(
        compile(
            source,
            f"{ORIGINAL_COMMIT}:{ORIGINAL_SCRIPT_PATH}",
            "exec",
        ),
        namespace,
    )
    return namespace


def load_historical_fixture() -> dict[str, Any]:
    value = json.loads(git_show_text(ORIGINAL_COMMIT, FIXTURE_RELATIVE_PATH))
    assert isinstance(value, dict)
    return value


def exact_edm_fixture(
    historical: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    inventory = edm.load_json(edm.INVENTORY_PATH)
    motions = edm.validate_inventory(inventory)
    expected = copy.deepcopy(historical)

    source = edm.source_record()
    source_ids = [item["source_id"] for item in expected["sources"]]
    assert source["source_id"] not in source_ids
    expected["sources"].append(source)

    facts = [edm.fact_record(row) for row in motions]
    edm_fact_ids = [item["fact_id"] for item in facts]
    existing_fact_ids = [item["fact_id"] for item in expected["facts"]]
    assert not set(edm_fact_ids).intersection(existing_fact_ids)
    expected["facts"].extend(facts)

    historical_section = edm.find_section(historical)
    expected_section = edm.find_section(expected)
    assert expected_section == historical_section
    expected_section["summary"] = edm.EXPECTED_SUMMARY
    expected_section["fact_ids"] = historical_section["fact_ids"] + edm_fact_ids
    expected_section["status"] = "partial"

    return expected, motions


def main() -> int:
    if len(sys.argv) != 1:
        raise AssertionError("capture integration is not authorised in this repair")

    original = load_original_namespace()
    historical = load_historical_fixture()
    expected_current, motions = exact_edm_fixture(historical)
    current = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert current == expected_current
    original["validate_report"](current)
    edm.validate_integration(current, motions)

    original_load_json = original["load_json"]
    original_fixture_path = Path(original["FIXTURE_PATH"]).resolve()

    def load_json_with_historical_fixture(path: Path) -> dict[str, Any]:
        if Path(path).resolve() == original_fixture_path:
            return copy.deepcopy(historical)
        return original_load_json(path)

    original["load_json"] = load_json_with_historical_fixture
    result = original["main"]([])
    assert result == 0

    print(
        "PASS — fixed spoken-contributions baseline preserved with the exact "
        "six-EDM fixture extension"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
