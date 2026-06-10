#!/usr/bin/env python3
"""
Build a seed URL file from TWIS website source candidate records.

This is a safe bridge step. It does not fetch pages, crawl, call Nutch,
or overwrite seed_urls.json. It writes a separate seed file for later review.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_INPUT = Path("website_source_candidates_v25.json")
DEFAULT_JSON_OUTPUT = Path("seed_urls_from_website_candidates_v26.json")
DEFAULT_MD_OUTPUT = Path("seed_urls_from_website_candidates_v26.md")
DEFAULT_ROLES = ["url"]
VALID_ROLES = {"url", "rssUrl", "secondaryUrl"}


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 form."""
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    """Load JSON from a local file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Write formatted UTF-8 JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def parse_roles(raw_roles: str) -> list[str]:
    """Parse and validate comma-separated URL roles."""
    roles = [role.strip() for role in raw_roles.split(",") if role.strip()]

    if not roles:
        raise ValueError("At least one role must be supplied.")

    invalid_roles = [role for role in roles if role not in VALID_ROLES]
    if invalid_roles:
        raise ValueError(
            "Invalid role(s): "
            + ", ".join(invalid_roles)
            + ". Valid roles are: "
            + ", ".join(sorted(VALID_ROLES))
        )

    deduped_roles: list[str] = []
    for role in roles:
        if role not in deduped_roles:
            deduped_roles.append(role)

    return deduped_roles


def is_valid_public_url(url: str) -> bool:
    """Return True for ordinary http/https URLs with a hostname."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def md_cell(value: Any) -> str:
    """Escape a value for a simple Markdown table cell."""
    text = str(value or "")
    return text.replace("|", "\\|").replace("\n", " ")


def build_seed_urls(
    candidates: Any,
    roles_included: list[str],
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Build a deduplicated seed URL list and record included/skipped candidates.

    Returns:
        seed_urls, included_records, skipped_records
    """
    if not isinstance(candidates, list):
        raise ValueError("Candidate input must be a JSON list of records.")

    seed_urls: list[str] = []
    included: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            skipped.append({
                "index": index,
                "reason": "record is not an object",
                "url": "",
                "url_role": "",
                "source_name": "",
            })
            continue

        url = str(candidate.get("url", "")).strip()
        status = str(candidate.get("status", "")).strip()
        url_role = str(candidate.get("url_role", "")).strip()
        source_name = str(candidate.get("source_name", candidate.get("title", ""))).strip()

        base_skip = {
            "index": index,
            "url": url,
            "url_role": url_role,
            "source_name": source_name,
        }

        if status != "candidate":
            skipped.append({**base_skip, "reason": f"status is {status or 'missing'}, not candidate"})
            continue

        if url_role not in roles_included:
            skipped.append({**base_skip, "reason": f"url_role {url_role or 'missing'} not selected"})
            continue

        if not url:
            skipped.append({**base_skip, "reason": "missing url"})
            continue

        if not is_valid_public_url(url):
            skipped.append({**base_skip, "reason": "invalid or unsupported url"})
            continue

        if url in seen_urls:
            skipped.append({**base_skip, "reason": "duplicate url"})
            continue

        seen_urls.add(url)
        seed_urls.append(url)
        included.append({
            "index": index,
            "url": url,
            "url_role": url_role,
            "source_name": source_name,
            "source_tag": str(candidate.get("source_tag", "")).strip(),
        })

    return seed_urls, included, skipped


def make_seed_json(
    seed_urls: list[str],
    source_file: Path,
    roles_included: list[str],
    created_at: str,
) -> dict[str, Any]:
    """Create the v2.6 seed URL JSON output."""
    return {
        "seed_urls": seed_urls,
        "source_file": source_file.as_posix(),
        "roles_included": roles_included,
        "created_at": created_at,
    }


def make_markdown_report(
    seed_urls: list[str],
    included: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    input_path: Path,
    json_output_path: Path,
    roles_included: list[str],
) -> str:
    """Create the v2.6 Markdown report."""
    lines: list[str] = [
        "# Seed URLs from website source candidates v2.6",
        "",
        "This report lists seed URLs created from TWIS website source candidate records. It does not prove that the pages are relevant evidence.",
        "",
        "## Scope",
        "",
        "- No live crawl was run.",
        "- No public pages were fetched.",
        "- Nutch was not called.",
        "- `seed_urls.json` was not overwritten.",
        "- A separate seed file was created for review.",
        "",
        "## Files",
        "",
        f"- Input: `{input_path.as_posix()}`",
        f"- JSON output: `{json_output_path.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Roles included: {', '.join(roles_included)}",
        f"- Seed URLs written: {len(seed_urls)}",
        f"- Included candidate records: {len(included)}",
        f"- Skipped candidate records: {len(skipped)}",
        "",
        "## Included seed URLs",
        "",
    ]

    if included:
        lines.extend([
            "| # | Source | Role | URL | Tag |",
            "|---:|---|---|---|---|",
        ])
        for number, item in enumerate(included, start=1):
            lines.append(
                "| "
                f"{number} | "
                f"{md_cell(item.get('source_name'))} | "
                f"{md_cell(item.get('url_role'))} | "
                f"{md_cell(item.get('url'))} | "
                f"{md_cell(item.get('source_tag'))} |"
            )
    else:
        lines.append("No seed URLs were included.")

    lines.extend(["", "## Skipped candidates", ""])
    if skipped:
        lines.extend([
            "| Candidate index | Source | Role | URL | Reason |",
            "|---:|---|---|---|---|",
        ])
        for item in skipped:
            lines.append(
                "| "
                f"{item.get('index', '')} | "
                f"{md_cell(item.get('source_name'))} | "
                f"{md_cell(item.get('url_role'))} | "
                f"{md_cell(item.get('url'))} | "
                f"{md_cell(item.get('reason'))} |"
            )
    else:
        lines.append("No candidates were skipped.")

    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a seed URL file from TWIS website source candidate records."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Candidate JSON input path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--json-output",
        default=str(DEFAULT_JSON_OUTPUT),
        help=f"Seed URL JSON output path. Default: {DEFAULT_JSON_OUTPUT}",
    )
    parser.add_argument(
        "--md-output",
        default=str(DEFAULT_MD_OUTPUT),
        help=f"Markdown report output path. Default: {DEFAULT_MD_OUTPUT}",
    )
    parser.add_argument(
        "--roles",
        default=",".join(DEFAULT_ROLES),
        help="Comma-separated URL roles to include. Default: url. Options: url,rssUrl,secondaryUrl",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    json_output_path = Path(args.json_output)
    md_output_path = Path(args.md_output)

    if input_path.name == "seed_urls.json" or json_output_path.name == "seed_urls.json":
        print("ERROR: this script must not read from or write to seed_urls.json directly.")
        print("Use the separate v2.6 seed output file instead.")
        return 1

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        print("Run extract_twis_website_sources_v25.py first.")
        return 1

    try:
        roles_included = parse_roles(args.roles)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1

    try:
        candidates = load_json(input_path)
        seed_urls, included, skipped = build_seed_urls(candidates, roles_included)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1

    created_at = utc_now_iso()
    seed_json = make_seed_json(seed_urls, input_path, roles_included, created_at)
    write_json(json_output_path, seed_json)

    report = make_markdown_report(
        seed_urls=seed_urls,
        included=included,
        skipped=skipped,
        input_path=input_path,
        json_output_path=json_output_path,
        roles_included=roles_included,
    )
    md_output_path.write_text(report, encoding="utf-8")

    print(f"Roles included: {', '.join(roles_included)}")
    print(f"Seed URLs written: {len(seed_urls)}")
    print(f"Skipped candidates: {len(skipped)}")
    print(f"JSON output: {json_output_path}")
    print(f"Markdown output: {md_output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
