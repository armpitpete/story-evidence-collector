#!/usr/bin/env python3
"""Read-only display model for the Complete MP Portfolio Streamlit view.

The module consumes the canonical Complete MP Report v1 fixture, validator and
generator. It does not browse, research, edit evidence, write to SQLite or
create publication decisions.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.generate_complete_mp_report import (
        CANONICAL_SECTIONS,
        ReportValidationError,
        load_json,
        slugify,
        validate_report,
        write_outputs,
    )
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    from generate_complete_mp_report import (  # type: ignore[no-redef]
        CANONICAL_SECTIONS,
        ReportValidationError,
        load_json,
        slugify,
        validate_report,
        write_outputs,
    )

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_PATH = (
    ROOT / "fixtures" / "complete-mp-reports" / "jeremy-corbyn-fixture-v1.json"
)

STATUS_MESSAGES = {
    "complete": "Complete for the report's declared scope.",
    "partial": "Useful evidence exists, but a material boundary remains.",
    "not_available": "The required evidence is not publicly available from the recorded source boundary.",
    "not_researched": "This research lane has not yet been completed.",
    "human_review_required": "Evidence or wording requires a human decision before it can progress.",
}


class PortfolioViewError(ValueError):
    """Raised when the portfolio cannot be rendered safely."""


def _index(records: list[dict[str, Any]], id_field: str) -> dict[str, dict[str, Any]]:
    return {str(record[id_field]): record for record in records}


def _source_view(source: dict[str, Any]) -> dict[str, Any]:
    location = (
        source.get("url")
        or source.get("repository_path")
        or source.get("server_path")
        or ""
    )
    return {
        "source_id": source["source_id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "source_type": source["source_type"],
        "authority_level": source["authority_level"],
        "capture_date": source["capture_date"],
        "location": location,
        "limitations": source["limitations"],
    }


def _resolve_sources(
    source_ids: list[str], source_map: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    return [_source_view(source_map[source_id]) for source_id in source_ids]


def _fact_view(
    fact: dict[str, Any], source_map: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "fact_id": fact["fact_id"],
        "statement": fact["statement"],
        "fact_type": fact["fact_type"],
        "date": fact.get("date"),
        "date_from": fact.get("date_from"),
        "date_to": fact.get("date_to"),
        "confidence": fact["confidence"],
        "evidence_status": fact["evidence_status"],
        "notes": fact.get("notes", ""),
        "sources": _resolve_sources(fact["source_ids"], source_map),
    }


def _claim_view(
    claim: dict[str, Any], source_map: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "claim_id": claim["claim_id"],
        "statement": claim["statement"],
        "claim_kind": claim["claim_kind"],
        "status": claim["status"],
        "fact_ids": list(claim["fact_ids"]),
        "public_wording_allowed": claim["public_wording_allowed"],
        "risk_level": claim["risk_level"],
        "notes": claim.get("notes", ""),
        "sources": _resolve_sources(claim["source_ids"], source_map),
    }


def _interpretation_view(interpretation: dict[str, Any]) -> dict[str, Any]:
    return {
        "interpretation_id": interpretation["interpretation_id"],
        "statement": interpretation["statement"],
        "fact_ids": list(interpretation["fact_ids"]),
        "claim_ids": list(interpretation["claim_ids"]),
        "risk_level": interpretation["risk_level"],
        "approved_for_publication": interpretation["approved_for_publication"],
        "notes": interpretation.get("notes", ""),
    }


def _relationship_view(
    relationship: dict[str, Any], source_map: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "relationship_id": relationship["relationship_id"],
        "subject": relationship["subject"],
        "neutral_label": relationship["neutral_label"],
        "object": relationship["object"],
        "date_from": relationship.get("date_from"),
        "date_to": relationship.get("date_to"),
        "confidence": relationship["confidence"],
        "public_chart": relationship["public_chart"],
        "notes": relationship.get("notes", ""),
        "sources": _resolve_sources(relationship["source_ids"], source_map),
    }


def _gap_view(gap: dict[str, Any]) -> dict[str, Any]:
    return {
        "gap_id": gap["gap_id"],
        "summary": gap["summary"],
        "severity": gap["severity"],
        "reason": gap["reason"],
        "next_action": gap["next_action"],
        "status": gap["status"],
        "blocks_publication": gap["blocks_publication"],
        "date_from": gap.get("date_from"),
        "date_to": gap.get("date_to"),
    }


def canonical_output_filenames(report: dict[str, Any]) -> list[str]:
    """Return the five canonical generator filenames for one report."""

    slug = slugify(report["subject"]["display_name"])
    return [
        f"{slug}-coverage-report.md",
        f"{slug}-full-profile.json",
        f"{slug}-full-profile.md",
        f"{slug}-human-review.md",
        f"{slug}-source-register.md",
    ]


def build_portfolio_view(report: dict[str, Any]) -> dict[str, Any]:
    """Validate canonical input and build a deterministic read-only display model."""

    try:
        validate_report(report)
    except ReportValidationError as exc:
        raise PortfolioViewError(str(exc)) from exc

    section_map = _index(report["sections"], "section_id")
    source_map = _index(report["sources"], "source_id")
    fact_map = _index(report["facts"], "fact_id")
    claim_map = _index(report["claims"], "claim_id")
    interpretation_map = _index(report["interpretations"], "interpretation_id")
    relationship_map = _index(report["relationships"], "relationship_id")
    gap_map = _index(report["coverage_gaps"], "gap_id")

    sections: list[dict[str, Any]] = []
    for position, (section_id, canonical_title) in enumerate(CANONICAL_SECTIONS, start=1):
        section = section_map[section_id]
        status = section["status"]
        sections.append(
            {
                "position": position,
                "section_id": section_id,
                "title": section.get("title") or canonical_title,
                "status": status,
                "status_message": STATUS_MESSAGES[status],
                "summary": section["summary"],
                "facts": [
                    _fact_view(fact_map[record_id], source_map)
                    for record_id in section["fact_ids"]
                ],
                "claims": [
                    _claim_view(claim_map[record_id], source_map)
                    for record_id in section["claim_ids"]
                ],
                "interpretations": [
                    _interpretation_view(interpretation_map[record_id])
                    for record_id in section["interpretation_ids"]
                ],
                "relationships": [
                    _relationship_view(relationship_map[record_id], source_map)
                    for record_id in section["relationship_ids"]
                ],
                "coverage_gaps": [
                    _gap_view(gap_map[record_id]) for record_id in section["gap_ids"]
                ],
            }
        )

    return {
        "report_id": report["report_id"],
        "title": report["title"],
        "generated_at": report["generated_at"],
        "subject": dict(report["subject"]),
        "scope": dict(report["scope"]),
        "publication": dict(report["publication"]),
        "sections": sections,
        "sources": [
            _source_view(source)
            for source in sorted(report["sources"], key=lambda item: item["source_id"])
        ],
        "review_decisions": [dict(item) for item in report["review_decisions"]],
        "output_filenames": canonical_output_filenames(report),
    }


def load_fixture_portfolio(
    fixture_path: Path = DEFAULT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Load and validate the committed fixture, then return its display model."""

    try:
        report = load_json(fixture_path)
    except ReportValidationError as exc:
        raise PortfolioViewError(str(exc)) from exc
    return build_portfolio_view(report)


def generate_temporary_preview(report: dict[str, Any]) -> dict[str, Any]:
    """Generate canonical outputs in an OS temporary folder and remove it.

    Only output metadata is returned. The generated files and their containing
    directory are removed before this function returns.
    """

    try:
        validate_report(report)
    except ReportValidationError as exc:
        raise PortfolioViewError(str(exc)) from exc

    temporary_directory = ""
    files: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="story-evidence-mp-portfolio-") as value:
        output_dir = Path(value).resolve()
        temporary_directory = str(output_dir)
        if output_dir == ROOT or ROOT in output_dir.parents:
            raise PortfolioViewError(
                "Disposable generator output must be outside the repository."
            )

        try:
            outputs = write_outputs(report, output_dir)
        except ReportValidationError as exc:
            raise PortfolioViewError(str(exc)) from exc

        for path in outputs:
            content = path.read_bytes()
            files.append(
                {
                    "filename": path.name,
                    "size_bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )

    if Path(temporary_directory).exists():
        raise PortfolioViewError("Disposable generator directory was not removed.")

    return {
        "temporary_directory": temporary_directory,
        "removed": True,
        "files": sorted(files, key=lambda item: item["filename"]),
    }
