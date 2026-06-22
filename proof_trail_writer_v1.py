#!/usr/bin/env python3
"""
Write Proof Trail evidence files from one controlled input file.

This is a deliberately small v1 writer for story-evidence-collector.
It does not fetch web pages, extract claims with AI, create a database, or judge
truth. It turns reviewed or manually supplied input into stable proof-trail files
that a human can inspect.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("examples/proof_trail_input_v1.json")
DEFAULT_OUTPUT_DIR = Path("evidence")

SOURCE_TYPES = {
    "official_record",
    "government_page",
    "parliament_record",
    "court_document",
    "manifesto",
    "speech",
    "interview",
    "news_article",
    "press_release",
    "social_post",
    "video",
    "audio",
    "transcript",
    "screenshot",
    "other",
}

EVIDENCE_GRADES = {"A", "B", "C", "D", "E"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}


class ProofTrailWriterError(RuntimeError):
    """Raised when the writer cannot safely create Proof Trail files."""


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 form."""
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object from disk."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ProofTrailWriterError("Input file must contain a JSON object.")

    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Write formatted UTF-8 JSON without ASCII escaping."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def save_text(path: Path, content: str) -> None:
    """Write UTF-8 text."""
    with path.open("w", encoding="utf-8") as file:
        file.write(content.rstrip())
        file.write("\n")


def ensure_output_dirs(output_dir: Path) -> dict[str, Path]:
    """Create the Proof Trail output folders if they do not exist."""
    folders = {
        "sources": output_dir / "sources",
        "claims": output_dir / "claims",
        "evidence_items": output_dir / "evidence-items",
        "briefs": output_dir / "briefs",
        "archives": output_dir / "archives",
        "transcripts": output_dir / "transcripts",
    }

    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)

    return folders


def next_record_number(folder: Path, prefix: str, suffix: str) -> int:
    """Return the next safe four-digit record number for a folder/prefix."""
    highest_number = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d{{4}}){re.escape(suffix)}$")

    for path in folder.iterdir() if folder.exists() else []:
        match = pattern.match(path.name)
        if match:
            highest_number = max(highest_number, int(match.group(1)))

    return highest_number + 1


def record_id(prefix: str, number: int) -> str:
    """Build a stable record id such as source-0001."""
    return f"{prefix}-{number:04d}"


def normalise_grade(value: Any, default: str = "C") -> str:
    """Return a valid evidence grade."""
    grade = str(value or default).strip().upper()
    if grade not in EVIDENCE_GRADES:
        raise ProofTrailWriterError(f"Invalid evidence grade: {value!r}")
    return grade


def normalise_source_type(value: Any) -> str:
    """Return a valid source type."""
    source_type = str(value or "other").strip()
    if source_type not in SOURCE_TYPES:
        raise ProofTrailWriterError(f"Invalid source_type: {value!r}")
    return source_type


def normalise_confidence(value: Any) -> str:
    """Return a valid confidence value."""
    confidence = str(value or "medium").strip().lower()
    if confidence not in CONFIDENCE_LEVELS:
        raise ProofTrailWriterError(f"Invalid confidence: {value!r}")
    return confidence


def section(data: dict[str, Any], key: str) -> dict[str, Any]:
    """Read an optional nested object section from the input."""
    value = data.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ProofTrailWriterError(f"Input section {key!r} must be a JSON object.")
    return value


def build_source_record(source_input: dict[str, Any], source_id: str, collected_at: str) -> dict[str, Any]:
    """Build a source record matching Proof Trail Schema v1."""
    return {
        "id": source_id,
        "title": str(source_input.get("title", "")),
        "url": str(source_input.get("url", "")),
        "publisher": str(source_input.get("publisher", "")),
        "source_type": normalise_source_type(source_input.get("source_type")),
        "publication_date": str(source_input.get("publication_date", "")),
        "collected_at": str(source_input.get("collected_at") or collected_at),
        "archive_url": str(source_input.get("archive_url", "")),
        "local_copy_path": str(source_input.get("local_copy_path", "")),
        "author_or_speaker": str(source_input.get("author_or_speaker", "")),
        "body_or_organisation": str(source_input.get("body_or_organisation", "")),
        "reliability_grade": normalise_grade(source_input.get("reliability_grade"), default="C"),
        "notes": str(source_input.get("notes", "")),
    }


def build_claim_record(
    claim_input: dict[str, Any],
    claim_id: str,
    source_record: dict[str, Any],
) -> dict[str, Any]:
    """Build a claim record matching Proof Trail Schema v1."""
    return {
        "id": claim_id,
        "source_id": source_record["id"],
        "speaker": str(claim_input.get("speaker") or source_record.get("author_or_speaker", "")),
        "body_or_organisation": str(
            claim_input.get("body_or_organisation") or source_record.get("body_or_organisation", "")
        ),
        "claim_text": str(claim_input.get("claim_text", "")),
        "plain_meaning": str(claim_input.get("plain_meaning", "")),
        "topic": str(claim_input.get("topic", "")),
        "position": str(claim_input.get("position", "")),
        "date_claimed": str(claim_input.get("date_claimed") or source_record.get("publication_date", "")),
        "confidence": normalise_confidence(claim_input.get("confidence")),
        "human_checked": bool(claim_input.get("human_checked", False)),
        "notes": str(claim_input.get("notes", "")),
    }


def build_evidence_item_record(
    evidence_input: dict[str, Any],
    evidence_item_id: str,
    claim_record: dict[str, Any],
    source_record: dict[str, Any],
) -> dict[str, Any]:
    """Build an evidence item record matching Proof Trail Schema v1."""
    return {
        "id": evidence_item_id,
        "claim_id": claim_record["id"],
        "source_id": source_record["id"],
        "excerpt": str(evidence_input.get("excerpt") or claim_record.get("claim_text", "")),
        "page_number": str(evidence_input.get("page_number", "")),
        "timestamp_start": str(evidence_input.get("timestamp_start", "")),
        "timestamp_end": str(evidence_input.get("timestamp_end", "")),
        "transcript_path": str(evidence_input.get("transcript_path", "")),
        "archive_url": str(evidence_input.get("archive_url") or source_record.get("archive_url", "")),
        "local_copy_path": str(evidence_input.get("local_copy_path") or source_record.get("local_copy_path", "")),
        "evidence_grade": normalise_grade(evidence_input.get("evidence_grade") or source_record.get("reliability_grade")),
        "human_checked": bool(evidence_input.get("human_checked", False)),
        "context_notes": str(evidence_input.get("context_notes", "")),
        "risk_notes": str(evidence_input.get("risk_notes", "")),
    }


def build_brief_markdown(
    brief_id: str,
    source_record: dict[str, Any],
    claim_record: dict[str, Any],
    evidence_item_record: dict[str, Any],
    assessment_input: dict[str, Any],
) -> str:
    """Build a human-readable Markdown evidence brief."""
    topic = str(assessment_input.get("topic") or claim_record.get("topic", ""))
    summary = str(assessment_input.get("summary", ""))
    what_is_proven = str(assessment_input.get("what_is_proven", ""))
    what_is_interpretation = str(assessment_input.get("what_is_interpretation", ""))
    what_needs_checking = str(assessment_input.get("what_needs_checking", ""))
    what_must_not_be_overstated = str(assessment_input.get("what_must_not_be_overstated", ""))
    possible_tension = str(assessment_input.get("possible_contradiction_or_tension", ""))

    timestamp_label = ""
    timestamp_start = evidence_item_record.get("timestamp_start", "")
    timestamp_end = evidence_item_record.get("timestamp_end", "")
    if timestamp_start or timestamp_end:
        timestamp_label = f"{timestamp_start} - {timestamp_end}".strip(" -")

    return f"""# Evidence Brief

Brief ID: `{brief_id}`

## Topic

{topic}

## Summary

{summary}

## Claim found

**Speaker/body:** {claim_record.get("speaker") or claim_record.get("body_or_organisation", "")}  
**Date:** {claim_record.get("date_claimed", "")}  
**Exact wording:** {claim_record.get("claim_text", "")}  
**Plain meaning:** {claim_record.get("plain_meaning", "")}  

## Source chain

**Original source:** {source_record.get("url", "")}  
**Archive copy:** {source_record.get("archive_url", "")}  
**Local copy:** {source_record.get("local_copy_path", "")}  
**Transcript:** {evidence_item_record.get("transcript_path", "")}  
**Video/audio timestamp:** {timestamp_label}  
**Collected at:** {source_record.get("collected_at", "")}  

## Evidence grade

{evidence_item_record.get("evidence_grade", "")}

## What is proven

{what_is_proven}

## What is interpretation

{what_is_interpretation}

## What needs checking

{what_needs_checking}

## What must not be overstated

{what_must_not_be_overstated}

## Possible contradiction or tension

{possible_tension}

## Human review status

- [ ] Source checked
- [ ] Archive checked
- [ ] Quote checked
- [ ] Context checked
- [ ] Risk wording checked
- [ ] Approved for TWIS use
"""


def build_output_paths(output_dir: Path) -> tuple[dict[str, Path], dict[str, str]]:
    """Create output folders and reserve the next matching record IDs and paths."""
    folders = ensure_output_dirs(output_dir)

    source_number = next_record_number(folders["sources"], "source", ".json")
    claim_number = next_record_number(folders["claims"], "claim", ".json")
    evidence_item_number = next_record_number(folders["evidence_items"], "evidence-item", ".json")
    brief_number = next_record_number(folders["briefs"], "brief", ".md")

    ids = {
        "source": record_id("source", source_number),
        "claim": record_id("claim", claim_number),
        "evidence_item": record_id("evidence-item", evidence_item_number),
        "brief": record_id("brief", brief_number),
    }

    paths = {
        "source": folders["sources"] / f"{ids['source']}.json",
        "claim": folders["claims"] / f"{ids['claim']}.json",
        "evidence_item": folders["evidence_items"] / f"{ids['evidence_item']}.json",
        "brief": folders["briefs"] / f"{ids['brief']}.md",
    }

    existing_paths = [path for path in paths.values() if path.exists()]
    if existing_paths:
        existing_list = ", ".join(path.as_posix() for path in existing_paths)
        raise ProofTrailWriterError(f"Refusing to overwrite existing files: {existing_list}")

    return paths, ids


def write_proof_trail(input_data: dict[str, Any], output_dir: Path) -> dict[str, str]:
    """Write one source, claim, evidence item, and brief from controlled input."""
    collected_at = utc_now_iso()
    paths, ids = build_output_paths(output_dir)

    source_record = build_source_record(section(input_data, "source"), ids["source"], collected_at)
    claim_record = build_claim_record(section(input_data, "claim"), ids["claim"], source_record)
    evidence_item_record = build_evidence_item_record(
        section(input_data, "evidence"),
        ids["evidence_item"],
        claim_record,
        source_record,
    )
    brief_markdown = build_brief_markdown(
        ids["brief"],
        source_record,
        claim_record,
        evidence_item_record,
        section(input_data, "assessment"),
    )

    save_json(paths["source"], source_record)
    save_json(paths["claim"], claim_record)
    save_json(paths["evidence_item"], evidence_item_record)
    save_text(paths["brief"], brief_markdown)

    return {key: path.as_posix() for key, path in paths.items()}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Write Proof Trail evidence files from one controlled input JSON file."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Controlled input JSON path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Proof Trail output directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    return parser.parse_args()


def main() -> int:
    """Run the Proof Trail writer."""
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        return 1

    try:
        input_data = load_json(input_path)
        written_paths = write_proof_trail(input_data, output_dir)
    except (OSError, json.JSONDecodeError, ProofTrailWriterError) as error:
        print(f"ERROR: {error}")
        return 1

    print("Proof Trail files written")
    print("-------------------------")
    for label, path in written_paths.items():
        print(f"{label}: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
