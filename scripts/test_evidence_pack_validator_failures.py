#!/usr/bin/env python3
"""Regression tests for evidence pack validator failure cases.

These tests build temporary invalid evidence packs from the known-good example
fixture. They prove that the validator rejects bad structure without keeping
broken evidence packs under the normal valid fixture tree.

The tests are structural only.
They do not prove truth, fairness, publishability, or human review.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from validate_evidence_pack import validate_pack


REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_PACK = REPO_ROOT / "fixtures" / "evidence-packs" / "2026-06-22-example-topic"
FAILURE_CASES = (
    REPO_ROOT
    / "fixtures"
    / "invalid-evidence-packs"
    / "validator-failure-cases.json"
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def set_dotted_value(data: dict[str, Any], dotted_path: str, value: Any) -> None:
    parts = dotted_path.split(".")
    current: Any = data

    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Cannot set missing path: {dotted_path}")
        current = current[part]

    if not isinstance(current, dict):
        raise TypeError(f"Cannot set field on non-object path: {dotted_path}")

    current[parts[-1]] = value


def remove_field(data: dict[str, Any], dotted_path: str) -> None:
    parts = dotted_path.split(".")
    current: Any = data

    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Cannot remove missing path: {dotted_path}")
        current = current[part]

    if not isinstance(current, dict):
        raise TypeError(f"Cannot remove field from non-object path: {dotted_path}")

    current.pop(parts[-1], None)


def apply_case(pack_dir: Path, case: dict[str, Any]) -> None:
    pack_json = pack_dir / "pack.json"
    manifest = load_json(pack_json)

    for dotted_path in case.get("remove", []):
        remove_field(manifest, dotted_path)

    for dotted_path, value in case.get("set", {}).items():
        set_dotted_value(manifest, dotted_path, value)

    for field, value in case.get("add", {}).items():
        manifest[field] = value

    write_json(pack_json, manifest)

    for relative_path, text in case.get("append_text", {}).items():
        target = pack_dir / relative_path
        with target.open("a", encoding="utf-8") as handle:
            handle.write(text)


def run_case(case: dict[str, Any], temp_root: Path) -> list[str]:
    case_name = case["name"]
    pack_dir = temp_root / case_name

    shutil.copytree(VALID_PACK, pack_dir)
    apply_case(pack_dir, case)

    return validate_pack(pack_dir)


def main() -> int:
    cases = load_json(FAILURE_CASES)

    if not isinstance(cases, list) or not cases:
        print(f"FAIL: no validator failure cases found in {FAILURE_CASES}")
        return 1

    failed = False

    with tempfile.TemporaryDirectory(prefix="twis-validator-failure-tests-") as temp:
        temp_root = Path(temp)

        for case in cases:
            case_name = case.get("name", "<unnamed>")
            errors = run_case(case, temp_root)
            expected_errors = case.get("expected_errors", [])

            if not errors:
                failed = True
                print(f"FAIL: {case_name}")
                print("- validator unexpectedly passed")
                print()
                continue

            missing_expected = [
                expected
                for expected in expected_errors
                if not any(expected in error for error in errors)
            ]

            if missing_expected:
                failed = True
                print(f"FAIL: {case_name}")
                print("- missing expected errors:")
                for expected in missing_expected:
                    print(f"  - {expected}")
                print("- actual errors:")
                for error in errors:
                    print(f"  - {error}")
                print()
                continue

            print(f"PASS: {case_name}")

    if failed:
        print("One or more validator failure regression tests failed.")
        return 1

    print(f"All validator failure regression tests passed. Count: {len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())