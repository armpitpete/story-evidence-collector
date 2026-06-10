#!/usr/bin/env python3
"""
Extract source candidates from the TWIS website sources page.

This is a safe local extractor. It reads the local TWIS Astro source page and
turns its source map into candidate records. It does not crawl, fetch public
pages, call Nutch, or decide whether any source is evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_INPUT = Path("../thisweekinsmoke/src/pages/sources/index.astro")
DEFAULT_JSON_OUTPUT = Path("website_source_candidates_v25.json")
DEFAULT_MD_OUTPUT = Path("website_source_candidates_v25.md")

URL_ROLES = ("url", "rssUrl", "secondaryUrl")

SOURCE_OBJECT_RE = re.compile(
    r"\{\s*name:\s*'(?P<name>(?:\\.|[^'\\])*)'\s*,(?P<body>.*?)use:\s*'(?P<use>(?:\\.|[^'\\])*)'\s*\}",
    re.DOTALL,
)

FIELD_RE = re.compile(
    r"(?P<key>name|tag|url|rssUrl|secondaryUrl):\s*'(?P<value>(?:\\.|[^'\\])*)'",
    re.DOTALL,
)


def utc_date() -> str:
    """Return today's UTC date in YYYY-MM-DD form."""
    return datetime.now(timezone.utc).date().isoformat()


def clean_js_string(value: str) -> str:
    """Clean a simple single-quoted JavaScript string value."""
    return value.replace("\\'", "'").replace('\\"', '"').strip()


def is_public_url(url: str) -> bool:
    """Return True for ordinary http/https URLs with a hostname."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def source_domain(url: str) -> str:
    """Return lower-case domain from a URL."""
    return urlparse(url).netloc.lower()


def read_sources_page(path: Path) -> str:
    """Read the local TWIS website sources page."""
    return path.read_text(encoding="utf-8")


def extract_source_entries(page_text: str) -> list[dict[str, str]]:
    """Extract source entries from the Astro file's sourceGroups data."""
    entries: list[dict[str, str]] = []

    for match in SOURCE_OBJECT_RE.finditer(page_text):
        entry: dict[str, str] = {
            "name": clean_js_string(match.group("name")),
            "use": clean_js_string(match.group("use")),
        }

        body = match.group("body")
        for field_match in FIELD_RE.finditer(body):
            key = field_match.group("key")
            value = clean_js_string(field_match.group("value"))
            entry[key] = value

        entries.append(entry)

    return entries


def make_candidate(entry: dict[str, str], url: str, role: str, found_date: str) -> dict[str, Any]:
    """Create one candidate record from one URL field."""
    source_name = entry.get("name", "")

    return {
        "url": url,
        "title": source_name,
        "source_domain": source_domain(url),
        "discovered_from": "TWIS website sources page",
        "discovery_method": "twis_website_sources",
        "crawl_depth": 0,
        "date_found": found_date,
        "status": "candidate",
        "source_name": source_name,
        "source_tag": entry.get("tag", ""),
        "source_use": entry.get("use", ""),
        "url_role": role,
    }


def entries_to_candidates(entries: list[dict[str, str]], found_date: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert extracted entries into candidate records and skipped URL notes."""
    candidates: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for entry_index, entry in enumerate(entries, start=1):
        for role in URL_ROLES:
            raw_url = entry.get(role, "").strip()
            if not raw_url:
                continue

            if not is_public_url(raw_url):
                skipped.append({
                    "entry_index": entry_index,
                    "source_name": entry.get("name", ""),
                    "url_role": role,
                    "url": raw_url,
                    "reason": "invalid or unsupported url",
                })
                continue

            candidates.append(make_candidate(entry, raw_url, role, found_date))

    return candidates, skipped


def write_json(path: Path, data: Any) -> None:
    """Write formatted UTF-8 JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def md_cell(value: Any) -> str:
    """Escape a value for a simple Markdown table cell."""
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ")


def make_markdown_report(
    candidates: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    input_path: Path,
    json_output_path: Path,
) -> str:
    """Create a readable Markdown report."""
    unique_sources = sorted({candidate["source_name"] for candidate in candidates if candidate.get("source_name")})
    unique_domains = sorted({candidate["source_domain"] for candidate in candidates if candidate.get("source_domain")})

    lines: list[str] = [
        "# TWIS website source candidates v2.5",
        "",
        "This report lists candidate URLs extracted from the local TWIS website sources page. It does not prove that the pages are relevant evidence.",
        "",
        "## Scope",
        "",
        "- No live crawl was run.",
        "- No public pages were fetched.",
        "- Nutch was not called.",
        "- These are candidate source/search URLs only.",
        "",
        "## Files",
        "",
        f"- Input: `{input_path.as_posix()}`",
        f"- JSON output: `{json_output_path.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Candidate URL records written: {len(candidates)}",
        f"- Source names represented: {len(unique_sources)}",
        f"- Source domains represented: {len(unique_domains)}",
        f"- Skipped URL fields: {len(skipped)}",
        "",
        "## Candidate URLs",
        "",
    ]

    if candidates:
        lines.extend([
            "| # | Source | Role | URL | Domain | Tag |",
            "|---:|---|---|---|---|---|",
        ])
        for index, candidate in enumerate(candidates, start=1):
            lines.append(
                "| "
                f"{index} | "
                f"{md_cell(candidate['source_name'])} | "
                f"{md_cell(candidate['url_role'])} | "
                f"{md_cell(candidate['url'])} | "
                f"{md_cell(candidate['source_domain'])} | "
                f"{md_cell(candidate['source_tag'])} |"
            )
    else:
        lines.append("No candidate URLs were found.")

    lines.extend(["", "## Skipped URL fields", ""])
    if skipped:
        lines.extend([
            "| Source | Role | URL | Reason |",
            "|---|---|---|---|",
        ])
        for item in skipped:
            lines.append(
                "| "
                f"{md_cell(item.get('source_name'))} | "
                f"{md_cell(item.get('url_role'))} | "
                f"{md_cell(item.get('url'))} | "
                f"{md_cell(item.get('reason'))} |"
            )
    else:
        lines.append("No URL fields were skipped.")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract source candidates from the local TWIS website sources page."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Input Astro file. Default: {DEFAULT_INPUT}",
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
        help="Date to use for candidate records. Default: today's UTC date.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    json_output_path = Path(args.json_output)
    md_output_path = Path(args.md_output)

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        print("Expected local sibling repo path by default:")
        print(f"  {DEFAULT_INPUT}")
        return 1

    page_text = read_sources_page(input_path)
    entries = extract_source_entries(page_text)
    candidates, skipped = entries_to_candidates(entries, args.date_found)

    write_json(json_output_path, candidates)

    report = make_markdown_report(
        candidates=candidates,
        skipped=skipped,
        input_path=input_path,
        json_output_path=json_output_path,
    )
    md_output_path.write_text(report, encoding="utf-8")

    print(f"Source entries parsed: {len(entries)}")
    print(f"Candidate URL records written: {len(candidates)}")
    print(f"Skipped URL fields: {len(skipped)}")
    print(f"JSON output: {json_output_path}")
    print(f"Markdown output: {md_output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
