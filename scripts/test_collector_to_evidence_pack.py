#!/usr/bin/env python3
"""Regression tests for the collector-to-Evidence-Pack v1 bridge."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "scripts/create_draft_evidence_pack_from_collector.py"
VALIDATOR = REPO_ROOT / "scripts/validate_evidence_pack.py"
FIXTURE = (
    REPO_ROOT
    / "fixtures/collector-runs/2026-06-27-west-built-cheap-china-system/sources_raw_v13.json"
)
PACK_ID = "2026-06-27-west-built-cheap-china-system-collector-draft"
CREATED_AT = "2026-06-27T16:30:00Z"
EXPECTED_URLS = {
    "https://www.reuters.com/world/china/eu-impose-3-euro-duty-small-e-commerce-parcels-july-2026-2025-12-12/",
    "https://ec.europa.eu/commission/presscorner/api/files/document/print/en/ip_25_410/IP_25_410_EN.pdf",
    "https://www.theguardian.com/business/article/2024/aug/14/revealed-how-uks-poor-paid-price-of-cheapflation-in-cost-of-living-crisis",
    "https://www.reuters.com/business/retail-consumer/hot-wheels-gi-joes-aplenty-shein-temu-amid-worry-over-fake-products-2024-11-29/",
    "https://www.reuters.com/world/us/ny-fed-report-says-americans-pay-almost-all-trumps-tariffs-2026-02-12/",
}


def bridge_command(source_records: Path, output_root: Path, overwrite: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(BRIDGE),
        "--source-records",
        str(source_records),
        "--output-root",
        str(output_root),
        "--pack-id",
        PACK_ID,
        "--title",
        "Draft Evidence Pack — West Built the Cheap China System",
        "--research-question",
        "What public evidence supports or limits the article's claims about low-value parcel duties, platform use and consumer price effects?",
        "--scope",
        "Controlled collector-to-pack integration fixture using five external sources already recorded in the reviewed TWIS Evidence Pack. Source metadata only; no claims or publication decision.",
        "--created-at",
        CREATED_AT,
        "--editorial-risk",
        "high",
    ]
    if overwrite:
        command.append("--overwrite")
    return command


def run(command: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    if expect_success and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    if not expect_success and result.returncode == 0:
        raise AssertionError(f"command unexpectedly succeeded: {' '.join(command)}")
    return result


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def snapshot(path: Path) -> dict[str, bytes]:
    return {
        item.relative_to(path).as_posix(): item.read_bytes()
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def assert_pack_safety(pack_dir: Path) -> None:
    manifest = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "draft"
    assert manifest["publishability"] == "not_ready"
    assert manifest["human_review_required"] is True
    assert manifest["editorial_risk"] == "high"

    source_records = load_jsonl(pack_dir / manifest["records"]["source_records"])
    assert len(source_records) == 5
    assert {record["url"] for record in source_records} == EXPECTED_URLS
    assert all(record["source_type"] == "collector_page" for record in source_records)
    assert all("have not been assessed" in record["notes"] for record in source_records)

    for field in (
        "source_authority_map",
        "claim_records",
        "evidence_items",
        "negative_evidence_log",
        "public_record_timeline",
        "denial_checks",
    ):
        assert load_jsonl(pack_dir / manifest["records"][field]) == [], field

    search_records = load_jsonl(pack_dir / manifest["records"]["search_diary"])
    review_records = load_jsonl(pack_dir / manifest["records"]["human_review"])
    assert len(search_records) == 1
    assert len(review_records) == 1
    assert review_records[0]["decision"] == "not_reviewed"
    assert review_records[0]["safe_wording"] == "No public wording is authorised."

    final_brief = (pack_dir / manifest["outputs"]["final_brief"]).read_text(
        encoding="utf-8"
    )
    contradiction_brief = (
        pack_dir / manifest["outputs"]["contradiction_brief"]
    ).read_text(encoding="utf-8")
    assert "Publication state: not ready" in final_brief
    assert "No factual claims" in final_brief
    assert "No contradiction analysis was performed" in contradiction_brief


def test_success_and_determinism(temp_root: Path) -> None:
    run_a = temp_root / "run-a"
    run_b = temp_root / "run-b"

    first = run(bridge_command(FIXTURE, run_a))
    assert "Source records: 5" in first.stdout
    assert "Claims generated: 0" in first.stdout
    assert "Publishability: not_ready" in first.stdout

    pack_a = run_a / PACK_ID
    pack_b = run_b / PACK_ID
    run(bridge_command(FIXTURE, run_b))

    run([sys.executable, str(VALIDATOR), str(pack_a)])
    run([sys.executable, str(VALIDATOR), str(pack_b)])
    assert_pack_safety(pack_a)
    assert_pack_safety(pack_b)
    assert snapshot(pack_a) == snapshot(pack_b)

    overwrite_rejected = run(bridge_command(FIXTURE, run_a), expect_success=False)
    assert "output pack already exists" in overwrite_rejected.stderr

    run(bridge_command(FIXTURE, run_a, overwrite=True))
    run([sys.executable, str(VALIDATOR), str(pack_a)])
    assert snapshot(pack_a) == snapshot(pack_b)


def test_duplicate_and_missing_url_rejection(temp_root: Path) -> None:
    duplicate_path = temp_root / "duplicate.json"
    duplicate_path.write_text(
        json.dumps(
            [
                {
                    "source_url": "https://example.invalid/report#section-one",
                    "page_title": "First",
                },
                {
                    "source_url": "https://example.invalid/report#section-two",
                    "page_title": "Duplicate",
                },
            ]
        ),
        encoding="utf-8",
    )
    duplicate_result = run(
        bridge_command(duplicate_path, temp_root / "duplicate-output"),
        expect_success=False,
    )
    assert "duplicate normalised URL" in duplicate_result.stderr

    missing_path = temp_root / "missing-url.json"
    missing_path.write_text(json.dumps([{"page_title": "No URL"}]), encoding="utf-8")
    missing_result = run(
        bridge_command(missing_path, temp_root / "missing-output"),
        expect_success=False,
    )
    assert "missing source URL" in missing_result.stderr


def main() -> int:
    assert BRIDGE.is_file(), BRIDGE
    assert VALIDATOR.is_file(), VALIDATOR
    assert FIXTURE.is_file(), FIXTURE

    with tempfile.TemporaryDirectory(prefix="collector-pack-test-") as temporary:
        temp_root = Path(temporary)
        test_success_and_determinism(temp_root)
        test_duplicate_and_missing_url_rejection(temp_root)

    print("PASS: collector-to-Evidence-Pack bridge is deterministic and draft-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
