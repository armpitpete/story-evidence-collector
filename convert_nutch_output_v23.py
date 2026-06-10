#!/usr/bin/env python3
"""
Convert Nutch-style discovery output into TWIS candidate source records.

This script is deliberately limited. It does not crawl, fetch pages, call Nutch,
or decide whether a discovered page is evidence. It only converts already
available discovery records into a stable candidate-source JSON shape.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_INPUT = Path("testdata/nutch_discovery_sample_v23.json")
DEFAULT_JSON_OUTPUT = Path("candidate_sources_discovered_v23.json")
DEFAULT_MD_OUTPUT = Path("candidate_sources_discovered_v23.md")


def utc_date() -> str:
    """Return today's UTC date in YYYY-MM-DD form."""
    return datetime.now(timezone.utc).date().isoformat()


def load_json(path: Path) -> Any:
    """Load JSON from a local file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Write formatted UTF-8 JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def extract_records(raw: Any) -> list[Any]:
    """
    Accept a plain list or a simple wrapper object.

    The fixture currently uses a list. The wrapper support gives the later
    Nutch adapter some room without changing this converter.
    """
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ("records", "candidates", "documents", "urls", "items"):
            value = raw.get(key)
            if isinstance(value, list):
                return value

    return []


def is_valid_public_url(url: str) -> bool:
    """Return True for ordinary http/https URLs with a network location."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def derive_domain(url: str) -> str:
    """Derive a lower-case source domain from a URL."""
    return urlparse(url).netloc.lower()


def normalise_candidate(record: Any, found_date: str, index: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """
    Convert one raw discovery record into the v2.3 candidate shape.

    Returns:
        (candidate, None) for valid records
        (None, skipped_record) for invalid records
    """
    if not isinstance(record, dict):
        return None, {
            "index": index,
            "reason": "record is not an object",
            "record": record,
        }

    url = str(record.get("url", "")).strip()

    if not url:
        return None, {
            "index": index,
            "reason": "missing url",
            "record": record,
        }

    if not is_valid_public_url(url):
        return None, {
            "index": index,
            "reason": "invalid or unsupported url",
            "url": url,
            "record": record,
        }

    source_domain = str(record.get("source_domain", "")).strip().lower()
    if not source_domain:
        source_domain = derive_domain(url)

    crawl_depth_raw = record.get("crawl_depth", 0)
    try:
        crawl_depth = int(crawl_depth_raw)
    except (TypeError, ValueError):
        crawl_depth = 0

    candidate = {
        "url": url,
        "title": str(record.get("title", "")).strip(),
        "source_domain": source_domain,
        "discovered_from": str(record.get("discovered_from", "")).strip(),
        "discovery_method": str(record.get("discovery_method", "nutch")).strip() or "nutch",
        "crawl_depth": crawl_depth,
        "date_found": str(record.get("date_found", "")).strip() or found_date,
        "status": str(record.get("status", "candidate")).strip() or "candidate",
    }

    return candidate, None


def convert_records(raw_records: list[Any], found_date: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert records and collect skipped records with reasons."""
    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for index, record in enumerate(raw_records, start=1):
        candidate, skipped_record = normalise_candidate(record, found_date, index)

        if skipped_record is not None:
            skipped.append(skipped_record)
            continue

        assert candidate is not None

        url = candidate["url"]
        if url in seen_urls:
            skipped.append({
                "index": index,
                "reason": "duplicate url",
                "url": url,
                "record": record,
            })
            continue

        seen_urls.add(url)
        candidates.append(candidate)

    return candidates, skipped


def make_markdown_report(
    candidates: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    input_path: Path,
    json_output_path: Path,
) -> str:
    """Create the human-readable v2.3 Markdown report."""
    lines: list[str] = [
        "# Nutch discovery candidate report v2.3",
        "",
        "This report lists candidate pages discovered from the supplied Nutch output sample. It does not prove that the pages are relevant evidence.",
        "",
        "## Scope",
        "",
        "- No live crawl was run.",
        "- No public pages were fetched.",
        "- No evidence judgement was made.",
        "- These are candidate pages only.",
        "",
        "## Files",
        "",
        f"- Input: `{input_path.as_posix()}`",
        f"- JSON output: `{json_output_path.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Candidate records written: {len(candidates)}",
        f"- Skipped records: {len(skipped)}",
        "",
    ]

    lines.extend([
        "## Candidate pages",
        "",
    ])

    if candidates:
        lines.extend([
            "| # | Title | URL | Source domain | Discovered from | Crawl depth | Discovery method |",
            "|---:|---|---|---|---|---:|---|",
        ])

        for number, candidate in enumerate(candidates, start=1):
            title = candidate["title"] or "Untitled"
            url = candidate["url"]
            source_domain = candidate["source_domain"]
            discovered_from = candidate["discovered_from"] or "Not supplied"
            crawl_depth = candidate["crawl_depth"]
            discovery_method = candidate["discovery_method"]
            lines.append(
                f"| {number} | {title} | {url} | {source_domain} | {discovered_from} | {crawl_depth} | {discovery_method} |"
            )
    else:
        lines.append("No valid candidate pages were found.")

    lines.extend([
        "",
        "## Skipped records",
        "",
    ])

    if skipped:
        lines.extend([
            "| Input index | Reason | URL if present |",
            "|---:|---|---|",
        ])
        for item in skipped:
            lines.append(
                f"| {item.get('index', '')} | {item.get('reason', '')} | {item.get('url', '')} |"
            )
    else:
        lines.append("No records were skipped.")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Nutch-style discovery JSON into candidate_sources_discovered_v23.json."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Input JSON path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--json-output",
        default=str(DEFAULT_JSON_OUTPUT),
        help=f"Candidate JSON output path. Default: {DEFAULT_JSON_OUTPUT}",
    )
    parser.add_argument(
        "--md-output",
        default=str(DEFAULT_MD_OUTPUT),
        help=f"Markdown report output path. Default: {DEFAULT_MD_OUTPUT}",
    )
    parser.add_argument(
        "--date-found",
        default=utc_date(),
        help="Date to use for missing date_found fields. Default: today's UTC date.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    json_output_path = Path(args.json_output)
    md_output_path = Path(args.md_output)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        return 1

    raw = load_json(input_path)
    raw_records = extract_records(raw)

    candidates, skipped = convert_records(raw_records, args.date_found)

    write_json(json_output_path, candidates)

    report = make_markdown_report(
        candidates=candidates,
        skipped=skipped,
        input_path=input_path,
        json_output_path=json_output_path,
    )
    md_output_path.write_text(report, encoding="utf-8")

    print(f"Candidate records written: {len(candidates)}")
    print(f"Skipped records: {len(skipped)}")
    print(f"JSON output: {json_output_path}")
    print(f"Markdown output: {md_output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
