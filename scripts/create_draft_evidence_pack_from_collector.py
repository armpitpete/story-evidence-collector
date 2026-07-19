#!/usr/bin/env python3
"""Create a draft Evidence Pack v1 skeleton from collector source records.

This bridge copies source metadata into a reviewable pack structure. It does not
create claims, evidence conclusions, source-authority judgements, contradiction
findings, or publication approval.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urlsplit


PACK_ID_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$"
)

RECORD_PATHS = {
    "source_records": "sources/source-records.jsonl",
    "source_authority_map": "sources/source-authority-map.jsonl",
    "claim_records": "claims/claim-records.jsonl",
    "evidence_items": "evidence/evidence-items.jsonl",
    "search_diary": "search/search-diary.jsonl",
    "negative_evidence_log": "search/negative-evidence-log.jsonl",
    "public_record_timeline": "timeline/public-record-timeline.jsonl",
    "denial_checks": "timeline/denial-checks.jsonl",
    "human_review": "review/human-review.jsonl",
}

OUTPUT_PATHS = {
    "final_brief": "output/final-brief.md",
    "evidence_summary": "output/evidence-summary.md",
    "contradiction_brief": "output/contradiction-brief.md",
}


class BridgeError(ValueError):
    """Raised when collector input cannot be converted safely."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise BridgeError(f"could not read collector input {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BridgeError(f"collector input is not valid JSON: {exc}") from exc


def normalise_url(value: Any, record_number: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BridgeError(f"collector record {record_number}: missing source URL")

    clean_url, _fragment = urldefrag(value.strip())
    parsed = urlsplit(clean_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise BridgeError(
            f"collector record {record_number}: source URL must be absolute http/https: {value!r}"
        )
    return clean_url


def optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def collector_source_records(data: Any, input_path: Path, created_at: str) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        raise BridgeError("collector input must be a JSON list")
    if not data:
        raise BridgeError("collector input must contain at least one source record")

    converted: list[dict[str, Any]] = []
    seen_urls: dict[str, int] = {}

    for index, raw_record in enumerate(data, start=1):
        if not isinstance(raw_record, dict):
            raise BridgeError(f"collector record {index}: expected an object")

        raw_url = raw_record.get("final_url") or raw_record.get("source_url")
        url = normalise_url(raw_url, index)
        first_seen = seen_urls.get(url)
        if first_seen is not None:
            raise BridgeError(
                f"collector record {index}: duplicate normalised URL {url!r}; "
                f"first seen in record {first_seen}"
            )
        seen_urls[url] = index

        title = optional_string(raw_record.get("page_title")) or url
        collected_at = optional_string(raw_record.get("scraped_at")) or created_at
        hostname = urlsplit(url).hostname or "unknown"
        scrape_status = raw_record.get("scrape_status")
        robots_checked = raw_record.get("robots_txt_checked")
        robots_allowed = raw_record.get("robots_allowed")

        notes = (
            f"Imported from collector file {input_path.name}; "
            f"scrape_status={scrape_status!r}; "
            f"robots_txt_checked={robots_checked!r}; "
            f"robots_allowed={robots_allowed!r}. "
            "Source relevance, authority and factual use have not been assessed."
        )

        converted.append(
            {
                "id": f"source-collector-{index:04d}",
                "source_type": "collector_page",
                "title": title,
                "publisher": hostname,
                "published_at": None,
                "collected_at": collected_at,
                "url": url,
                "archive_url": None,
                "local_copy_path": None,
                "source_location": f"Collector source record {index}.",
                "notes": notes,
            }
        )

    return converted


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(
        json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in records
    )
    path.write_text(content, encoding="utf-8")


def markdown_source_list(source_records: list[dict[str, Any]]) -> str:
    lines = [
        "# Draft Evidence Summary",
        "",
        "This file lists collector source metadata only.",
        "",
        "No factual claims, source-authority assessments or evidence conclusions were generated.",
        "",
        "## Collected sources",
        "",
    ]
    for record in source_records:
        lines.append(f"- **{record['title']}** — {record['url']}")
    lines.extend(
        [
            "",
            "## Review requirement",
            "",
            "A human must assess relevance, provenance, authority, factual support and publication risk before using any source.",
            "",
        ]
    )
    return "\n".join(lines)


def build_pack(
    source_records: list[dict[str, Any]],
    pack_id: str,
    title: str,
    research_question: str,
    scope: str,
    created_at: str,
    editorial_risk: str,
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]], dict[str, str]]:
    source_ids = [record["id"] for record in source_records]

    records: dict[str, list[dict[str, Any]]] = {
        "source_records": source_records,
        "source_authority_map": [],
        "claim_records": [],
        "evidence_items": [],
        "search_diary": [
            {
                "id": "search-collector-0001",
                "searched_at": created_at,
                "query": research_question,
                "source_types_checked": ["collector_supplied_public_web_pages"],
                "results_summary": (
                    f"Collector input supplied {len(source_records)} source record(s). "
                    "No relevance, authority, claim or evidence assessment was generated."
                ),
                "useful_results": source_ids,
                "dead_ends": [],
                "stop_reason": "Draft pack skeleton created; human evidence review is required.",
            }
        ],
        "negative_evidence_log": [],
        "public_record_timeline": [],
        "denial_checks": [],
        "human_review": [
            {
                "id": "review-pending-0001",
                "reviewed_at": None,
                "reviewer": None,
                "review_area": "collector_to_evidence_pack_conversion",
                "decision": "not_reviewed",
                "safe_wording": "No public wording is authorised.",
                "unresolved_risk": (
                    "All source relevance, authority, factual claims, contradiction analysis "
                    "and publication decisions require human review."
                ),
            }
        ],
    }

    outputs = {
        "final_brief": "\n".join(
            [
                "# Draft Final Brief",
                "",
                "**Publication state: not ready.**",
                "",
                f"Research question: {research_question}",
                "",
                f"Collector sources preserved: {len(source_records)}",
                "",
                "No factual claims, evidence findings, contradiction findings or publication conclusions have been produced.",
                "",
                "Human review is required before further use.",
                "",
            ]
        ),
        "evidence_summary": markdown_source_list(source_records),
        "contradiction_brief": "\n".join(
            [
                "# Draft Contradiction Brief",
                "",
                "No contradiction analysis was performed.",
                "",
                "The collector-to-pack bridge preserves source metadata only. Human review is required.",
                "",
            ]
        ),
    }

    manifest = {
        "pack_schema_version": "1",
        "pack_id": pack_id,
        "title": title,
        "status": "draft",
        "created_at": created_at,
        "updated_at": created_at,
        "research_question": research_question,
        "scope": scope,
        "editorial_risk": editorial_risk,
        "publishability": "not_ready",
        "human_review_required": True,
        "records": RECORD_PATHS,
        "outputs": OUTPUT_PATHS,
        "notes": (
            "Generated from collector source metadata only. No claims, evidence conclusions, "
            "authority ratings or publication approval were generated."
        ),
    }

    return manifest, records, outputs


def ensure_safe_pack_path(output_root: Path, pack_id: str) -> Path:
    if not PACK_ID_PATTERN.fullmatch(pack_id):
        raise BridgeError(
            "pack_id must match YYYY-MM-DD-topic-name using lowercase letters, numbers and hyphens"
        )

    root = output_root.resolve()
    pack_dir = (root / pack_id).resolve()
    if pack_dir.parent != root:
        raise BridgeError("unsafe output path")
    return pack_dir


def write_pack(
    pack_dir: Path,
    manifest: dict[str, Any],
    records: dict[str, list[dict[str, Any]]],
    outputs: dict[str, str],
    overwrite: bool,
) -> None:
    if pack_dir.exists():
        if not overwrite:
            raise BridgeError(f"output pack already exists: {pack_dir}")
        if not pack_dir.is_dir():
            raise BridgeError(f"output pack path is not a directory: {pack_dir}")
        shutil.rmtree(pack_dir)

    pack_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = Path(
        tempfile.mkdtemp(prefix=f".{pack_dir.name}-", dir=str(pack_dir.parent))
    )

    try:
        write_json(temporary_dir / "pack.json", manifest)
        for field, relative_path in RECORD_PATHS.items():
            write_jsonl(temporary_dir / relative_path, records[field])
        for field, relative_path in OUTPUT_PATHS.items():
            output_path = temporary_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(outputs[field], encoding="utf-8")
        temporary_dir.rename(pack_dir)
    except Exception:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a draft Evidence Pack v1 skeleton from collector source records."
    )
    parser.add_argument("--source-records", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--pack-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--research-question", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--created-at", required=True)
    parser.add_argument(
        "--editorial-risk", choices=("low", "medium", "high"), default="high"
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        pack_dir = ensure_safe_pack_path(args.output_root, args.pack_id)
        source_data = read_json(args.source_records)
        source_records = collector_source_records(
            source_data, args.source_records, args.created_at
        )
        manifest, records, outputs = build_pack(
            source_records=source_records,
            pack_id=args.pack_id,
            title=args.title,
            research_question=args.research_question,
            scope=args.scope,
            created_at=args.created_at,
            editorial_risk=args.editorial_risk,
        )
        write_pack(pack_dir, manifest, records, outputs, args.overwrite)
    except BridgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Draft Evidence Pack created.")
    print(f"Pack folder: {pack_dir}")
    print(f"Source records: {len(source_records)}")
    print("Claims generated: 0")
    print("Evidence conclusions generated: 0")
    print("Publishability: not_ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
