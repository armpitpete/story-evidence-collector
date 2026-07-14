#!/usr/bin/env python3
"""Generate Complete MP Report v1 outputs from structured JSON.

The generator is offline and deterministic. It validates the input against the
repository JSON Schema, enforces cross-record contract rules, and renders
Markdown views. It does not research, browse, infer facts, resolve
contradictions or authorise publication.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = ROOT / "schemas" / "complete-mp-report-v1.schema.json"

CANONICAL_SECTIONS = (
    ("identity_and_parliamentary_career", "Identity and parliamentary career"),
    ("roles_and_committees", "Roles and committees"),
    ("voting_record_and_coverage", "Voting record and coverage"),
    ("financial_interests", "Financial interests"),
    ("donations_and_political_finance", "Donations and political finance"),
    ("outside_work_and_company_links", "Outside work and company links"),
    ("speeches_and_questions", "Speeches and parliamentary questions"),
    ("public_positions_over_time", "Public positions over time"),
    ("changes_and_contradictions", "Changes and contradictions"),
    ("organisations_and_relationships", "Organisations and evidenced relationships"),
    ("evidence_gaps", "Evidence gaps"),
    ("source_register", "Source register"),
    ("human_review", "Human review"),
)
SECTION_IDS = tuple(section_id for section_id, _ in CANONICAL_SECTIONS)
SECTION_TITLES = dict(CANONICAL_SECTIONS)


class ReportValidationError(ValueError):
    """Raised when a report cannot be rendered safely."""


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReportValidationError(f"Input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReportValidationError(f"Input is not valid JSON: {exc}") from exc

    if not isinstance(value, dict):
        raise ReportValidationError("Top-level report value must be an object.")
    return value


def load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReportValidationError(f"JSON Schema does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReportValidationError(f"JSON Schema is not valid JSON: {exc}") from exc

    if not isinstance(schema, dict):
        raise ReportValidationError("JSON Schema root must be an object.")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ReportValidationError(
            "Complete MP Report schema must declare JSON Schema Draft 2020-12."
        )
    return schema


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def _resolve_local_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ReportValidationError(
            f"Unsupported non-local JSON Schema reference: {reference}"
        )

    current: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ReportValidationError(
                f"Unresolvable JSON Schema reference: {reference}"
            )
        current = current[token]

    if not isinstance(current, dict):
        raise ReportValidationError(
            f"JSON Schema reference does not resolve to an object: {reference}"
        )
    return current


def _valid_format(value: str, format_name: str) -> bool:
    try:
        if format_name == "date":
            date.fromisoformat(value)
            return True
        if format_name == "date-time":
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None
    except ValueError:
        return False
    return True


def _schema_errors(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
) -> list[str]:
    if "$ref" in schema:
        target = _resolve_local_ref(root_schema, schema["$ref"])
        return _schema_errors(value, target, root_schema, path)

    errors: list[str] = []

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}.")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in the allowed enum.")

    expected_types = schema.get("type")
    if expected_types is not None:
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_json_type_matches(value, item) for item in expected_types):
            errors.append(
                f"{path}: expected type {' or '.join(expected_types)}, "
                f"found {type(value).__name__}."
            )
            return errors

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string is shorter than {min_length}.")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: value does not match pattern {pattern!r}.")
        format_name = schema.get("format")
        if isinstance(format_name, str) and not _valid_format(value, format_name):
            errors.append(f"{path}: value is not a valid {format_name}.")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: array has fewer than {min_items} items.")
        if isinstance(max_items, int) and len(value) > max_items:
            errors.append(f"{path}: array has more than {max_items} items.")
        if schema.get("uniqueItems") is True:
            seen: set[str] = set()
            for index, item in enumerate(value):
                marker = json.dumps(
                    item, sort_keys=True, ensure_ascii=False, separators=(",", ":")
                )
                if marker in seen:
                    errors.append(f"{path}[{index}]: duplicate array item.")
                seen.add(marker)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _schema_errors(item, item_schema, root_schema, f"{path}[{index}]")
                )

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{path}: missing required property {key!r}.")

        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, property_schema in properties.items():
                if key in value and isinstance(property_schema, dict):
                    errors.extend(
                        _schema_errors(
                            value[key],
                            property_schema,
                            root_schema,
                            f"{path}.{key}",
                        )
                    )

        if schema.get("additionalProperties") is False and isinstance(properties, dict):
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}.")

    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        for index, item_schema in enumerate(all_of):
            if isinstance(item_schema, dict):
                errors.extend(
                    _schema_errors(
                        value,
                        item_schema,
                        root_schema,
                        f"{path}.allOf[{index}]",
                    )
                )

    if_schema = schema.get("if")
    then_schema = schema.get("then")
    if isinstance(if_schema, dict) and isinstance(then_schema, dict):
        if not _schema_errors(value, if_schema, root_schema, path):
            errors.extend(_schema_errors(value, then_schema, root_schema, path))

    return errors


def validate_against_schema(
    report: dict[str, Any],
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> None:
    schema = load_schema(schema_path)
    errors = _schema_errors(report, schema, schema, "$")
    if errors:
        shown = "\n".join(f"- {error}" for error in errors[:20])
        remainder = len(errors) - 20
        if remainder:
            shown += f"\n- ... and {remainder} more schema error(s)."
        raise ReportValidationError(f"Schema validation failed:\n{shown}")


def require_object(report: dict[str, Any], key: str) -> dict[str, Any]:
    value = report.get(key)
    if not isinstance(value, dict):
        raise ReportValidationError(f"{key} must be an object.")
    return value


def require_list(report: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = report.get(key)
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ReportValidationError(f"{key} must be an array of objects.")
    return value


def build_id_map(
    records: list[dict[str, Any]],
    id_field: str,
    label: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        record_id = clean(record.get(id_field))
        if not record_id:
            raise ReportValidationError(f"{label}[{index}] is missing {id_field}.")
        if record_id in result:
            raise ReportValidationError(f"Duplicate {label} ID: {record_id}")
        result[record_id] = record
    return result


def require_refs(
    records: list[dict[str, Any]],
    ref_field: str,
    allowed: set[str],
    label: str,
) -> None:
    for record in records:
        record_id = next(
            (
                clean(value)
                for key, value in record.items()
                if key.endswith("_id") and clean(value)
            ),
            "<unknown>",
        )
        refs = record.get(ref_field, [])
        if not isinstance(refs, list):
            raise ReportValidationError(
                f"{label} {record_id}: {ref_field} must be an array."
            )
        missing = sorted(
            clean(reference)
            for reference in refs
            if clean(reference) not in allowed
        )
        if missing:
            raise ReportValidationError(
                f"{label} {record_id}: unresolved {ref_field}: "
                + ", ".join(missing)
            )


def validate_section_ownership(
    section_map: dict[str, dict[str, Any]],
    records: list[dict[str, Any]],
    id_field: str,
    ref_field: str,
    label: str,
) -> None:
    memberships: dict[str, list[str]] = {}
    for section_id, section in section_map.items():
        for record_id in section[ref_field]:
            memberships.setdefault(record_id, []).append(section_id)

    for record in records:
        record_id = clean(record[id_field])
        declared_section = clean(record["section_id"])
        listed_sections = memberships.get(record_id, [])

        if not listed_sections:
            raise ReportValidationError(
                f"Orphan {label} {record_id}: not listed by any section."
            )
        if len(listed_sections) > 1:
            raise ReportValidationError(
                f"Multiply listed {label} {record_id}: "
                + ", ".join(sorted(listed_sections))
            )
        if listed_sections[0] != declared_section:
            raise ReportValidationError(
                f"Cross-section {label} {record_id}: listed under "
                f"{listed_sections[0]} but declares {declared_section}."
            )


def validate_publishable_state(
    publication: dict[str, Any],
    claims: list[dict[str, Any]],
    interpretations: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> None:
    if publication.get("status") != "publishable":
        return

    if publication.get("human_review_required") is not False:
        raise ReportValidationError(
            "A publishable report cannot retain human_review_required=true."
        )
    if publication.get("public_output_authorised") is not True:
        raise ReportValidationError(
            "A publishable report requires public_output_authorised=true."
        )

    approved_by = clean(publication.get("approved_by"))
    approved_at = clean(publication.get("approved_at"))
    if not approved_by or not approved_at:
        raise ReportValidationError(
            "A publishable report requires approved_by and approved_at."
        )

    blocking = [
        clean(gap["gap_id"])
        for gap in gaps
        if gap["status"] == "open" and gap["blocks_publication"] is True
    ]
    if blocking:
        raise ReportValidationError(
            "Publishable report has blocking gaps: " + ", ".join(sorted(blocking))
        )

    unsupported = [
        clean(claim["claim_id"])
        for claim in claims
        if claim["status"] == "unsupported"
    ]
    if unsupported:
        raise ReportValidationError(
            "Publishable report has unsupported claims: "
            + ", ".join(sorted(unsupported))
        )

    private_wording = [
        clean(claim["claim_id"])
        for claim in claims
        if claim["public_wording_allowed"] is not True
    ]
    if private_wording:
        raise ReportValidationError(
            "Publishable report has claims not authorised for public wording: "
            + ", ".join(sorted(private_wording))
        )

    unapproved = [
        clean(item["interpretation_id"])
        for item in interpretations
        if item["approved_for_publication"] is not True
    ]
    if unapproved:
        raise ReportValidationError(
            "Publishable report has unapproved interpretations: "
            + ", ".join(sorted(unapproved))
        )

    matching_reviews = [
        review
        for review in reviews
        if review["review_type"] == "publication"
        and review["status"] == "approved"
        and clean(review["reviewer"]) == approved_by
        and clean(review["reviewed_at"]) == approved_at
    ]
    if not matching_reviews:
        raise ReportValidationError(
            "Publishable report lacks a traceable matching publication approval "
            "review decision."
        )


def validate_report(
    report: dict[str, Any],
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> None:
    validate_against_schema(report, schema_path)

    if report["schema_version"] != SCHEMA_VERSION:
        raise ReportValidationError(f"schema_version must be {SCHEMA_VERSION!r}.")

    subject = require_object(report, "subject")
    publication = require_object(report, "publication")
    sections = require_list(report, "sections")
    sources = require_list(report, "sources")
    facts = require_list(report, "facts")
    claims = require_list(report, "claims")
    interpretations = require_list(report, "interpretations")
    relationships = require_list(report, "relationships")
    gaps = require_list(report, "coverage_gaps")
    reviews = require_list(report, "review_decisions")

    section_map = build_id_map(sections, "section_id", "section")
    actual_sections = set(section_map)
    expected_sections = set(SECTION_IDS)
    if actual_sections != expected_sections or len(sections) != len(SECTION_IDS):
        missing = sorted(expected_sections - actual_sections)
        extra = sorted(actual_sections - expected_sections)
        details: list[str] = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unexpected: " + ", ".join(extra))
        raise ReportValidationError(
            "Canonical section set invalid: " + "; ".join(details)
        )

    source_map = build_id_map(sources, "source_id", "source")
    fact_map = build_id_map(facts, "fact_id", "fact")
    claim_map = build_id_map(claims, "claim_id", "claim")
    interpretation_map = build_id_map(
        interpretations, "interpretation_id", "interpretation"
    )
    relationship_map = build_id_map(
        relationships, "relationship_id", "relationship"
    )
    gap_map = build_id_map(gaps, "gap_id", "coverage gap")
    build_id_map(reviews, "review_id", "review")

    source_ids = set(source_map)
    fact_ids = set(fact_map)
    claim_ids = set(claim_map)
    interpretation_ids = set(interpretation_map)
    relationship_ids = set(relationship_map)
    gap_ids = set(gap_map)

    identity_source_ids = subject.get("identity_source_ids")
    if not isinstance(identity_source_ids, list) or not identity_source_ids:
        raise ReportValidationError(
            "subject.identity_source_ids must contain at least one source ID."
        )
    require_refs([subject], "identity_source_ids", source_ids, "subject")

    for records, label in (
        (facts, "fact"),
        (claims, "claim"),
        (relationships, "relationship"),
    ):
        require_refs(records, "source_ids", source_ids, label)

    require_refs(claims, "fact_ids", fact_ids, "claim")
    require_refs(interpretations, "fact_ids", fact_ids, "interpretation")
    require_refs(interpretations, "claim_ids", claim_ids, "interpretation")

    for review in reviews:
        require_refs([review], "related_fact_ids", fact_ids, "review")
        require_refs([review], "related_claim_ids", claim_ids, "review")
        require_refs([review], "related_gap_ids", gap_ids, "review")

    reference_sets = (
        ("fact_ids", fact_ids),
        ("claim_ids", claim_ids),
        ("interpretation_ids", interpretation_ids),
        ("relationship_ids", relationship_ids),
        ("gap_ids", gap_ids),
    )
    for section_id, section in section_map.items():
        for ref_field, allowed in reference_sets:
            missing = sorted(
                clean(reference)
                for reference in section[ref_field]
                if clean(reference) not in allowed
            )
            if missing:
                raise ReportValidationError(
                    f"Section {section_id}: unresolved {ref_field}: "
                    + ", ".join(missing)
                )

    for records, id_field, ref_field, label in (
        (facts, "fact_id", "fact_ids", "fact"),
        (claims, "claim_id", "claim_ids", "claim"),
        (
            interpretations,
            "interpretation_id",
            "interpretation_ids",
            "interpretation",
        ),
        (
            relationships,
            "relationship_id",
            "relationship_ids",
            "relationship",
        ),
        (gaps, "gap_id", "gap_ids", "coverage gap"),
    ):
        validate_section_ownership(
            section_map, records, id_field, ref_field, label
        )

    validate_publishable_state(
        publication, claims, interpretations, gaps, reviews
    )


def markdown_cell(value: Any) -> str:
    return clean(value).replace("|", "\\|")


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(markdown_cell(item) for item in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(markdown_cell(item) for item in row) + " |"
        for row in rows
    )
    return "\n".join(lines)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "mp-report"


def section_records(
    section: dict[str, Any],
    ref_field: str,
    records: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    return [records[record_id] for record_id in section[ref_field]]


def render_full_profile(report: dict[str, Any]) -> str:
    subject = report["subject"]
    publication = report["publication"]
    section_map = {item["section_id"]: item for item in report["sections"]}
    facts = {item["fact_id"]: item for item in report["facts"]}
    claims = {item["claim_id"]: item for item in report["claims"]}
    interpretations = {
        item["interpretation_id"]: item for item in report["interpretations"]
    }
    relationships = {
        item["relationship_id"]: item for item in report["relationships"]
    }
    gaps = {item["gap_id"]: item for item in report["coverage_gaps"]}

    lines = [
        f"# Complete MP Report — {subject['display_name']}",
        "",
        f"Generated from structured records: `{report['generated_at']}`",
        "",
        "## Report status",
        "",
        markdown_table(
            ["Field", "Value"],
            [
                ["Report ID", report["report_id"]],
                ["Schema version", report["schema_version"]],
                ["Publication status", publication["status"]],
                ["Human review required", publication["human_review_required"]],
                ["Public output authorised", publication["public_output_authorised"]],
                ["Identity status", subject["identity_status"]],
                ["Parliament member ID", subject["parliament_member_id"]],
                ["Current constituency", subject.get("current_constituency", "")],
                ["Current party", subject.get("current_party", "")],
            ],
        ),
        "",
        "## Scope",
        "",
        report["scope"]["scope_statement"],
        "",
        "This report records public evidence and explicit coverage limits. "
        "It does not infer motive, private belief or wrongdoing.",
        "",
    ]

    for section_id, default_title in CANONICAL_SECTIONS:
        section = section_map[section_id]
        lines.extend(
            [
                f"## {section.get('title') or default_title}",
                "",
                f"**Coverage status:** `{section['status']}`",
                "",
            ]
        )
        if clean(section["summary"]):
            lines.extend([clean(section["summary"]), ""])

        fact_rows = section_records(section, "fact_ids", facts)
        claim_rows = section_records(section, "claim_ids", claims)
        interpretation_rows = section_records(
            section, "interpretation_ids", interpretations
        )
        relationship_rows = section_records(
            section, "relationship_ids", relationships
        )
        gap_rows = section_records(section, "gap_ids", gaps)

        if fact_rows:
            lines.extend(["### Recorded facts", ""])
            for item in fact_rows:
                lines.append(
                    f"- **{item['fact_id']}** — {item['statement']} "
                    f"_(confidence: {item['confidence']}; "
                    f"evidence: {item['evidence_status']}; "
                    f"sources: {', '.join(item['source_ids'])})_"
                )
            lines.append("")

        if claim_rows:
            lines.extend(["### Claims", ""])
            for item in claim_rows:
                public_note = (
                    "public wording allowed"
                    if item["public_wording_allowed"]
                    else "not authorised for public wording"
                )
                lines.append(
                    f"- **{item['claim_id']}** — {item['statement']} "
                    f"_(status: {item['status']}; {public_note})_"
                )
            lines.append("")

        if interpretation_rows:
            lines.extend(["### Labelled interpretations", ""])
            for item in interpretation_rows:
                lines.append(
                    f"- **{item['interpretation_id']}** — {item['statement']} "
                    f"_(approved for publication: "
                    f"{item['approved_for_publication']})_"
                )
            lines.append("")

        if relationship_rows:
            lines.extend(["### Evidenced relationships", ""])
            lines.append(
                markdown_table(
                    [
                        "ID",
                        "Subject",
                        "Relationship",
                        "Object",
                        "Confidence",
                        "Public chart",
                    ],
                    [
                        [
                            item["relationship_id"],
                            item["subject"],
                            item["neutral_label"],
                            item["object"],
                            item["confidence"],
                            item["public_chart"],
                        ]
                        for item in relationship_rows
                    ],
                )
            )
            lines.append("")

        if gap_rows:
            lines.extend(["### Coverage gaps", ""])
            for item in gap_rows:
                lines.append(
                    f"- **{item['gap_id']}** — {item['summary']} "
                    f"_(severity: {item['severity']}; "
                    f"status: {item['status']}; "
                    f"blocks publication: {item['blocks_publication']})_"
                )
            lines.append("")

        if not any(
            (fact_rows, claim_rows, interpretation_rows, relationship_rows, gap_rows)
        ):
            lines.extend(["No structured records are attached to this section.", ""])

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This Markdown file is a deterministic view of the supplied records. "
            "It is not independent verification and does not upgrade fixture, "
            "partial or unreviewed material into publication evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def render_source_register(report: dict[str, Any]) -> str:
    rows = []
    for item in sorted(report["sources"], key=lambda value: value["source_id"]):
        rows.append(
            [
                item["source_id"],
                item["title"],
                item["publisher"],
                item["source_type"],
                item["authority_level"],
                item.get("publication_date", ""),
                item["capture_date"],
                item.get("url")
                or item.get("repository_path")
                or item.get("server_path")
                or "",
                item["limitations"],
            ]
        )
    return "\n".join(
        [
            f"# Source Register — {report['subject']['display_name']}",
            "",
            markdown_table(
                [
                    "Source ID",
                    "Title",
                    "Publisher",
                    "Type",
                    "Authority",
                    "Publication date",
                    "Capture date",
                    "Location",
                    "Limitations",
                ],
                rows,
            ),
            "",
            "This register records source identity and limits. Inclusion does "
            "not by itself prove every claim made from the source.",
            "",
        ]
    )


def render_coverage_report(report: dict[str, Any]) -> str:
    section_map = {item["section_id"]: item for item in report["sections"]}
    gap_map = {item["gap_id"]: item for item in report["coverage_gaps"]}
    lines = [
        f"# Coverage Report — {report['subject']['display_name']}",
        "",
        "## Section coverage",
        "",
        markdown_table(
            ["Section", "Status", "Summary", "Open gaps"],
            [
                [
                    SECTION_TITLES[section_id],
                    section_map[section_id]["status"],
                    section_map[section_id]["summary"],
                    sum(
                        1
                        for gap_id in section_map[section_id]["gap_ids"]
                        if gap_map[gap_id]["status"] == "open"
                    ),
                ]
                for section_id in SECTION_IDS
            ],
        ),
        "",
        "## Gap register",
        "",
    ]
    if report["coverage_gaps"]:
        lines.append(
            markdown_table(
                [
                    "Gap ID",
                    "Section",
                    "Severity",
                    "Status",
                    "Blocks publication",
                    "Summary",
                    "Next action",
                ],
                [
                    [
                        item["gap_id"],
                        SECTION_TITLES[item["section_id"]],
                        item["severity"],
                        item["status"],
                        item["blocks_publication"],
                        item["summary"],
                        item["next_action"],
                    ]
                    for item in sorted(
                        report["coverage_gaps"],
                        key=lambda value: value["gap_id"],
                    )
                ],
            )
        )
    else:
        lines.append("No coverage gaps were recorded.")
    lines.extend(
        [
            "",
            "Coverage status describes the declared scope only. It is not a "
            "claim that every possible public record exists.",
            "",
        ]
    )
    return "\n".join(lines)


def render_human_review(report: dict[str, Any]) -> str:
    lines = [
        f"# Human Review Record — {report['subject']['display_name']}",
        "",
        markdown_table(
            ["Publication field", "Value"],
            [
                ["Status", report["publication"]["status"]],
                [
                    "Human review required",
                    report["publication"]["human_review_required"],
                ],
                [
                    "Public output authorised",
                    report["publication"]["public_output_authorised"],
                ],
                ["Approved by", report["publication"].get("approved_by", "")],
                ["Approved at", report["publication"].get("approved_at", "")],
                ["Notes", report["publication"].get("notes", "")],
            ],
        ),
        "",
        "## Review decisions",
        "",
    ]
    if report["review_decisions"]:
        lines.append(
            markdown_table(
                [
                    "Review ID",
                    "Type",
                    "Status",
                    "Reviewer",
                    "Reviewed at",
                    "Decision",
                ],
                [
                    [
                        item["review_id"],
                        item["review_type"],
                        item["status"],
                        item["reviewer"],
                        item["reviewed_at"],
                        item["decision"],
                    ]
                    for item in sorted(
                        report["review_decisions"],
                        key=lambda value: value["review_id"],
                    )
                ],
            )
        )
    else:
        lines.append("No human review decisions were recorded.")
    lines.extend(
        [
            "",
            "The generator displays review records but cannot create, approve "
            "or replace human editorial judgement.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], output_dir: Path) -> list[Path]:
    validate_report(report)
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(report["subject"]["display_name"])
    outputs = {
        output_dir / f"{slug}-full-profile.json": (
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        ),
        output_dir / f"{slug}-full-profile.md": render_full_profile(report),
        output_dir / f"{slug}-source-register.md": render_source_register(report),
        output_dir / f"{slug}-coverage-report.md": render_coverage_report(report),
        output_dir / f"{slug}-human-review.md": render_human_review(report),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    return sorted(outputs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Complete MP Report v1 outputs from one JSON fixture "
            "or structured export."
        )
    )
    parser.add_argument("input", type=Path, help="Complete MP Report v1 JSON input.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated/complete-mp-reports"),
        help="Output folder. Default: generated/complete-mp-reports",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = load_json(args.input)
        outputs = write_outputs(report, args.output_dir)
    except ReportValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Complete MP Report v1 generated.")
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
