#!/usr/bin/env python3
"""Validate the fixed Complete MP report and analysis architecture contract."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "complete-mp-report-and-analysis-architecture-contract-v1.md"
EXPECTED_SHA256 = "bc729f66a923b1f97bde840a4ea9c5a7c33b03b5fbd4984c5b76468ab83a43a4"
PURPOSE = (
    "Build a complete, traceable public evidence record for each MP, then use that evidence "
    "to reveal significant patterns, relationships, changes and inconsistencies that are difficult "
    "to see through ordinary human reading—without overstating what the evidence proves."
)
SECTIONS = [
    "identity_and_parliamentary_career",
    "roles_and_committees",
    "voting_record_and_coverage",
    "financial_interests",
    "donations_and_political_finance",
    "outside_work_and_company_links",
    "speeches_and_questions",
    "public_positions_over_time",
    "changes_and_contradictions",
    "organisations_and_relationships",
    "evidence_gaps",
    "source_register",
    "human_review",
]
STATES = [
    "not_researched",
    "partial",
    "complete",
    "accepted_limit",
    "not_applicable",
    "blocked",
    "stale",
    "conflicting",
    "human_review_required",
]
PATTERNS = [
    "frequency",
    "time_change",
    "co_occurrence",
    "concentration",
    "network",
    "sequence",
    "gap",
    "cross_channel_consistency",
    "peer_deviation",
]
CLASSES = [
    "fact",
    "measured_pattern",
    "supported_inference",
    "unresolved_possibility",
    "unsupported_claim",
]
TRACE = [
    "official_source_record",
    "immutable_capture",
    "source_inventory",
    "canonical_source_record",
    "canonical_fact",
    "report_section_placement",
    "measurement_dataset",
    "measured_pattern",
    "interpretation_and_review_decision",
    "public_statement",
]
ROUTE = [
    "architecture_contract",
    "jeremy_corbyn_source_completion",
    "jeremy_corbyn_canonical_evidence_completion",
    "jeremy_corbyn_measured_analysis_proof",
    "jeremy_corbyn_pristine_proof_report",
    "contrasting_mp_shadow_proof",
    "calibration_cohort",
    "reusable_implementation_contract",
    "current_mp_controlled_expansion",
    "every_mp_completion_programme",
    "per_report_publication_gate",
]


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def extract_contract(text: str) -> dict[str, Any]:
    match = re.search(
        r"<!-- BEGIN COMPLETE_MP_REPORT_ANALYSIS_ARCHITECTURE_V1 -->\s*"
        r"```json\s*(.*?)\s*```\s*"
        r"<!-- END COMPLETE_MP_REPORT_ANALYSIS_ARCHITECTURE_V1 -->",
        text,
        re.DOTALL,
    )
    assert match, "deterministic architecture block missing"
    value = json.loads(match.group(1))
    assert isinstance(value, dict), "architecture block must be an object"
    return value


def main() -> int:
    text = CONTRACT.read_text(encoding="utf-8")
    assert PURPOSE in text, "governing purpose changed"
    assert "TODO" not in text and "TBD" not in text, "unfinished contract marker"

    headings = (
        "## Governing project purpose",
        "## Architecture layers",
        "## Complete MP report model and section catalogue",
        "## Readable report and evidence view",
        "## Full source-to-public-statement traceability chain",
        "## Section completeness states",
        "## Source authority, capture, checksum, version, refresh and correction rules",
        "## Allowed pattern families",
        "## Evidence and conclusion classes",
        "## Analytical safeguards",
        "## Peer-comparison rules",
        "## Pristine report acceptance standard",
        "## Route from the Jeremy Corbyn proof report to every MP",
        "## Failure and stop conditions",
        "## Architecture and implementation boundary",
        "## Deterministic contract block",
    )
    for heading in headings:
        assert text.count(heading) == 1, heading

    required_phrases = (
        "The readable report",
        "The **evidence view**",
        "without a skipped link",
        "Authority is claim-specific.",
        "Raw captures require SHA-256 checksums",
        "Corrections never overwrite history.",
        "Evidence confidence and analytical confidence are separate.",
        "Thresholds chosen after seeing the result invalidate the finding",
        "Baselines selected because they make the subject appear unusual are prohibited.",
        "Peer comparison is permitted only when:",
        "Publication remains separately authorised",
        "Passing a Jeremy Corbyn proof does not prove universal fitness.",
        "This lane does **not** authorise evidence capture",
    )
    for phrase in required_phrases:
        assert phrase in text, phrase

    value = extract_contract(text)
    assert hashlib.sha256(canonical(value)).hexdigest() == EXPECTED_SHA256
    assert set(value) == {
        "authority_base",
        "contract_version",
        "epistemic_classes",
        "layers",
        "pattern_families",
        "pristine_terminal_states",
        "route",
        "section_states",
        "sections",
        "source_controls",
        "traceability_chain",
    }
    assert value["authority_base"] == "e8273d415d513f055347d71a09d7c61517d609da"
    assert value["contract_version"] == "1"
    assert value["layers"] == [
        "evidence_record",
        "report_model",
        "measured_analysis",
        "interpretation_safeguard",
        "controlled_presentation",
    ]
    assert value["sections"] == SECTIONS
    assert value["section_states"] == STATES
    assert value["pristine_terminal_states"] == [
        "complete",
        "accepted_limit",
        "not_applicable",
    ]
    assert value["source_controls"] == [
        "authority",
        "capture",
        "checksum",
        "version",
        "refresh",
        "correction",
    ]
    assert value["pattern_families"] == PATTERNS
    assert value["epistemic_classes"] == CLASSES
    assert value["traceability_chain"] == TRACE
    assert value["route"] == ROUTE

    assert text.count("| `identity_and_parliamentary_career`") == 1
    assert text.count("| `human_review`") == 1
    assert text.count("A report is **pristine** only when") == 1
    assert len(re.findall(r"^\d+\. \*\*", text, re.MULTILINE)) >= 24

    print(
        "PASS: Complete MP report architecture, traceability, safeguards, "
        "pristine acceptance and controlled generalisation route are fixed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
