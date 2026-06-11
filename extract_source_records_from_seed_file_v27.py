#!/usr/bin/env python3
"""
Fetch source records from a selected seed URL file.

This is the first controlled targeted fetch step for the TWIS source engine.
It reads a seed JSON file, checks robots.txt for each seed, fetches seed pages
only when allowed, and writes source records plus a link queue.

It does not overwrite seed_urls.json, does not fetch queued links, does not call
Nutch, and does not crawl broadly.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from scrapling.parser import Selector


DEFAULT_INPUT = Path("seed_urls_from_website_candidates_v26.json")
DEFAULT_SOURCES_OUTPUT = Path("sources_raw_v27.json")
DEFAULT_LINK_QUEUE_OUTPUT = Path("link_queue_v27.json")
DEFAULT_REPORT_OUTPUT = Path("source_report_v27.json")

USER_AGENT = "StoryEvidenceCollector/2.7 (+https://thisweekinsmoke.uk/sources/)"
REQUEST_TIMEOUT_SECONDS = 20
TEXT_EXCERPT_CHARACTER_LIMIT = 3000
DEFAULT_MAX_SEEDS = 5
DEFAULT_DELAY_SECONDS = 1.0


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 form."""
    return datetime.now(timezone.utc).isoformat()


def save_json(path: Path, data: Any) -> None:
    """Write formatted UTF-8 JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def clean_text(value: Any) -> str:
    """Collapse whitespace and safely stringify a value."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def is_valid_public_url(url: str) -> bool:
    """Return True for ordinary http/https URLs with a hostname."""
    parsed_url = urlparse(url)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def load_seed_urls(input_path: Path, max_seeds: int) -> tuple[list[str], dict[str, Any]]:
    """Load and validate seed URLs from a selected seed JSON file."""
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise RuntimeError("Seed file must be a JSON object.")

    seed_urls_raw = data.get("seed_urls")
    if not isinstance(seed_urls_raw, list):
        raise RuntimeError("Seed file must contain a list called 'seed_urls'.")

    if max_seeds < 1:
        raise RuntimeError("max_seeds must be at least 1.")

    cleaned_urls: list[str] = []
    seen_urls: set[str] = set()
    skipped_inputs: list[dict[str, Any]] = []

    for index, raw_url in enumerate(seed_urls_raw, start=1):
        if not isinstance(raw_url, str) or not raw_url.strip():
            skipped_inputs.append({
                "index": index,
                "url": raw_url,
                "reason": "missing or empty url",
            })
            continue

        url = raw_url.strip()
        if not is_valid_public_url(url):
            skipped_inputs.append({
                "index": index,
                "url": url,
                "reason": "invalid or unsupported url",
            })
            continue

        if url in seen_urls:
            skipped_inputs.append({
                "index": index,
                "url": url,
                "reason": "duplicate url",
            })
            continue

        seen_urls.add(url)
        cleaned_urls.append(url)

        if len(cleaned_urls) >= max_seeds:
            break

    metadata = {
        "input_seed_url_count": len(seed_urls_raw),
        "selected_seed_url_count": len(cleaned_urls),
        "max_seeds": max_seeds,
        "skipped_inputs": skipped_inputs,
        "source_file_metadata": {
            key: value
            for key, value in data.items()
            if key != "seed_urls"
        },
    }

    return cleaned_urls, metadata


def fetch_text_url(url: str) -> tuple[str, str]:
    """Fetch a URL as text and return text plus final URL."""
    request = Request(url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        final_url = response.geturl()
        raw_bytes = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        text = raw_bytes.decode(charset, errors="replace")
        return text, final_url


def load_robots_parser(base_url: str) -> tuple[RobotFileParser | None, dict[str, Any]]:
    """Load and parse robots.txt for a URL's host."""
    robots_url = urljoin(base_url, "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        robots_text, _final_url = fetch_text_url(robots_url)
        parser.parse(robots_text.splitlines())

        return parser, {
            "robots_txt_url": robots_url,
            "robots_txt_checked": True,
            "robots_txt_status": "loaded",
            "robots_txt_error": None,
        }

    except HTTPError as error:
        if error.code == 404:
            parser.parse([])
            return parser, {
                "robots_txt_url": robots_url,
                "robots_txt_checked": True,
                "robots_txt_status": "not_found_treated_as_allowed",
                "robots_txt_error": None,
            }

        return None, {
            "robots_txt_url": robots_url,
            "robots_txt_checked": False,
            "robots_txt_status": f"http_error_{error.code}",
            "robots_txt_error": str(error),
        }

    except URLError as error:
        return None, {
            "robots_txt_url": robots_url,
            "robots_txt_checked": False,
            "robots_txt_status": "network_error",
            "robots_txt_error": str(error.reason),
        }

    except TimeoutError as error:
        return None, {
            "robots_txt_url": robots_url,
            "robots_txt_checked": False,
            "robots_txt_status": "timeout",
            "robots_txt_error": str(error),
        }

    except OSError as error:
        return None, {
            "robots_txt_url": robots_url,
            "robots_txt_checked": False,
            "robots_txt_status": "os_error",
            "robots_txt_error": str(error),
        }


def robots_allows_url(parser: RobotFileParser | None, url: str) -> bool:
    """Return whether robots.txt allows this user agent to fetch the URL."""
    if parser is None:
        return False
    return parser.can_fetch(USER_AGENT, url)


def extract_page_title(page: Selector) -> str:
    """Extract a page title."""
    return clean_text(page.css("title::text").get())


def extract_visible_text_excerpt(page: Selector) -> str:
    """Extract a short visible text excerpt from the page body."""
    text_parts: list[str] = []

    for text_node in page.css("body ::text").getall():
        cleaned = clean_text(text_node)
        if cleaned:
            text_parts.append(cleaned)

    full_text = " ".join(text_parts)
    return full_text[:TEXT_EXCERPT_CHARACTER_LIMIT]


def extract_links(page: Selector, base_url: str) -> list[str]:
    """Extract absolute HTTP/HTTPS links from a page."""
    links: list[str] = []
    seen_urls: set[str] = set()

    for href in page.css("a::attr(href)").getall():
        cleaned_href = clean_text(href)
        if not cleaned_href:
            continue

        absolute_url = urljoin(base_url, cleaned_href)
        parsed_url = urlparse(absolute_url)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            continue

        if absolute_url in seen_urls:
            continue

        seen_urls.add(absolute_url)
        links.append(absolute_url)

    return links


def is_same_domain(url: str, seed_url: str) -> bool:
    """Return whether two URLs share the same hostname."""
    return urlparse(url).netloc.lower() == urlparse(seed_url).netloc.lower()


def build_link_queue_items(links_found: list[str], found_on: str, seed_url: str) -> list[dict[str, Any]]:
    """Create pending link queue records from extracted links."""
    queued_at = utc_now_iso()
    queue_items: list[dict[str, Any]] = []

    for link in links_found:
        queue_items.append({
            "url": link,
            "found_on": found_on,
            "status": "pending",
            "depth": 1,
            "same_domain_as_seed": is_same_domain(link, seed_url),
            "queued_at": queued_at,
        })

    return queue_items


def build_blocked_source_record(seed_url: str, robots_report: dict[str, Any]) -> dict[str, Any]:
    """Create a source record for a seed blocked by robots.txt."""
    return {
        "source_url": seed_url,
        "final_url": None,
        "page_title": "",
        "text_excerpt": "",
        "links_found": [],
        "robots_txt_url": robots_report["robots_txt_url"],
        "robots_txt_checked": robots_report["robots_txt_checked"],
        "robots_txt_status": robots_report["robots_txt_status"],
        "robots_allowed": False,
        "scrape_status": "blocked_by_robots_txt",
        "error": None,
        "scraped_at": utc_now_iso(),
    }


def build_error_source_record(seed_url: str, robots_report: dict[str, Any], error_message: str) -> dict[str, Any]:
    """Create a source record for a failed seed fetch."""
    return {
        "source_url": seed_url,
        "final_url": None,
        "page_title": "",
        "text_excerpt": "",
        "links_found": [],
        "robots_txt_url": robots_report.get("robots_txt_url"),
        "robots_txt_checked": robots_report.get("robots_txt_checked", False),
        "robots_txt_status": robots_report.get("robots_txt_status", "not_checked"),
        "robots_allowed": False,
        "scrape_status": "error",
        "error": error_message,
        "scraped_at": utc_now_iso(),
    }


def extract_source_record(seed_url: str) -> dict[str, Any]:
    """Check robots.txt and fetch one seed URL if allowed."""
    print(f"Checking robots.txt for seed: {seed_url}")
    robots_parser, robots_report = load_robots_parser(seed_url)
    print(f"robots.txt status: {robots_report['robots_txt_status']}")

    if robots_parser is None:
        return build_error_source_record(
            seed_url,
            robots_report,
            "Could not check robots.txt safely.",
        )

    robots_allowed = robots_allows_url(robots_parser, seed_url)

    if not robots_allowed:
        print(f"Blocked by robots.txt: {seed_url}")
        return build_blocked_source_record(seed_url, robots_report)

    print(f"Fetching seed page only: {seed_url}")

    try:
        html, final_url = fetch_text_url(seed_url)
    except HTTPError as error:
        return build_error_source_record(seed_url, robots_report, f"HTTP error {error.code} while fetching {seed_url}")
    except URLError as error:
        return build_error_source_record(seed_url, robots_report, f"Network error while fetching {seed_url}: {error.reason}")
    except TimeoutError as error:
        return build_error_source_record(seed_url, robots_report, f"Timed out while fetching {seed_url}: {error}")
    except OSError as error:
        return build_error_source_record(seed_url, robots_report, f"OS error while fetching {seed_url}: {error}")

    page = Selector(html)
    links_found = extract_links(page, final_url)

    return {
        "source_url": seed_url,
        "final_url": final_url,
        "page_title": extract_page_title(page),
        "text_excerpt": extract_visible_text_excerpt(page),
        "links_found": links_found,
        "robots_txt_url": robots_report["robots_txt_url"],
        "robots_txt_checked": robots_report["robots_txt_checked"],
        "robots_txt_status": robots_report["robots_txt_status"],
        "robots_allowed": robots_allowed,
        "scrape_status": "ok",
        "error": None,
        "scraped_at": utc_now_iso(),
    }


def build_link_queue(source_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a deduplicated pending link queue from source records."""
    queue: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for source_record in source_records:
        if source_record.get("scrape_status") != "ok":
            continue

        found_on = source_record.get("final_url") or source_record.get("source_url")
        seed_url = source_record.get("source_url")
        links_found = source_record.get("links_found", [])

        for queue_item in build_link_queue_items(links_found, found_on, seed_url):
            link_url = queue_item["url"]

            if link_url in seen_urls:
                continue

            seen_urls.add(link_url)
            queue.append(queue_item)

    return queue


def validate_source_records(source_records: list[dict[str, Any]]) -> list[str]:
    """Return validation warnings for source records."""
    warnings: list[str] = []

    if not source_records:
        warnings.append("No source records were created.")

    for index, record in enumerate(source_records, start=1):
        if not record.get("source_url"):
            warnings.append(f"Source record {index} is missing source_url.")

        if record.get("scrape_status") == "ok":
            if not record.get("final_url"):
                warnings.append(f"Source record {index} is missing final_url.")
            if not record.get("page_title"):
                warnings.append(f"Source record {index} is missing page_title.")
            if not record.get("text_excerpt"):
                warnings.append(f"Source record {index} is missing text_excerpt.")
            if not isinstance(record.get("links_found"), list):
                warnings.append(f"Source record {index} links_found is not a list.")

        if not record.get("robots_txt_url"):
            warnings.append(f"Source record {index} is missing robots_txt_url.")
        if "robots_txt_checked" not in record:
            warnings.append(f"Source record {index} is missing robots_txt_checked.")
        if not record.get("robots_txt_status"):
            warnings.append(f"Source record {index} is missing robots_txt_status.")
        if "robots_allowed" not in record:
            warnings.append(f"Source record {index} is missing robots_allowed.")
        if not record.get("scrape_status"):
            warnings.append(f"Source record {index} is missing scrape_status.")

    return warnings


def validate_link_queue(link_queue: list[dict[str, Any]]) -> list[str]:
    """Return validation warnings for queued links."""
    warnings: list[str] = []

    for index, item in enumerate(link_queue, start=1):
        if not item.get("url"):
            warnings.append(f"Link queue item {index} is missing url.")
        if not item.get("found_on"):
            warnings.append(f"Link queue item {index} is missing found_on.")
        if item.get("status") != "pending":
            warnings.append(f"Link queue item {index} does not have status pending.")
        if item.get("depth") != 1:
            warnings.append(f"Link queue item {index} does not have depth 1.")
        if "same_domain_as_seed" not in item:
            warnings.append(f"Link queue item {index} is missing same_domain_as_seed.")
        if not item.get("queued_at"):
            warnings.append(f"Link queue item {index} is missing queued_at.")

    return warnings


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch source records from a selected seed URL file."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Seed URL JSON input path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--sources-output",
        default=str(DEFAULT_SOURCES_OUTPUT),
        help=f"Source records JSON output path. Default: {DEFAULT_SOURCES_OUTPUT}",
    )
    parser.add_argument(
        "--link-queue-output",
        default=str(DEFAULT_LINK_QUEUE_OUTPUT),
        help=f"Link queue JSON output path. Default: {DEFAULT_LINK_QUEUE_OUTPUT}",
    )
    parser.add_argument(
        "--report-output",
        default=str(DEFAULT_REPORT_OUTPUT),
        help=f"Run report JSON output path. Default: {DEFAULT_REPORT_OUTPUT}",
    )
    parser.add_argument(
        "--max-seeds",
        type=int,
        default=DEFAULT_MAX_SEEDS,
        help=f"Maximum seed URLs to fetch. Default: {DEFAULT_MAX_SEEDS}",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help=f"Delay between attempted seed fetches. Default: {DEFAULT_DELAY_SECONDS}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    sources_output = Path(args.sources_output)
    link_queue_output = Path(args.link_queue_output)
    report_output = Path(args.report_output)

    if input_path.name == "seed_urls.json":
        print("ERROR: v2.7 should not read seed_urls.json directly.")
        print("Use a selected seed file such as seed_urls_from_website_candidates_v26.json.")
        return 1

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}")
        print("Run build_seed_urls_from_candidates_v26.py first.")
        return 1

    if args.delay_seconds < 0:
        print("ERROR: delay-seconds must not be negative.")
        return 1

    load_error = None
    source_records: list[dict[str, Any]] = []
    seed_metadata: dict[str, Any] = {}

    print("Starting v2.7 targeted source record extraction")
    print(f"Seed input: {input_path}")
    print(f"Max seeds: {args.max_seeds}")
    print(f"Delay seconds: {args.delay_seconds}")
    print(f"Sources output: {sources_output}")
    print(f"Link queue output: {link_queue_output}")
    print(f"Report output: {report_output}")
    print("")

    try:
        seed_urls, seed_metadata = load_seed_urls(input_path, args.max_seeds)
    except (OSError, json.JSONDecodeError, RuntimeError) as error:
        load_error = str(error)
        seed_urls = []
        print(f"ERROR: {load_error}")

    for index, seed_url in enumerate(seed_urls, start=1):
        print("")
        print(f"Seed {index} of {len(seed_urls)}: {seed_url}")
        source_record = extract_source_record(seed_url)
        source_records.append(source_record)

        print(f"Scrape status: {source_record['scrape_status']}")
        print(f"Page title: {source_record['page_title']}")
        print(f"Links found: {len(source_record['links_found'])}")

        if index < len(seed_urls) and args.delay_seconds > 0:
            print(f"Waiting {args.delay_seconds} seconds before next seed.")
            time.sleep(args.delay_seconds)

    link_queue = build_link_queue(source_records)

    source_validation_warnings = validate_source_records(source_records)
    link_queue_validation_warnings = validate_link_queue(link_queue)
    validation_warnings = source_validation_warnings + link_queue_validation_warnings
    validation_passed = len(validation_warnings) == 0

    report = {
        "version": "v2.7",
        "seed_input_file": input_path.as_posix(),
        "seed_metadata": seed_metadata,
        "seed_urls_loaded": seed_urls,
        "seed_url_count": len(seed_urls),
        "max_seeds": args.max_seeds,
        "delay_seconds": args.delay_seconds,
        "user_agent": USER_AGENT,
        "source_records_file": sources_output.as_posix(),
        "source_records_saved": len(source_records),
        "ok_records": len([record for record in source_records if record.get("scrape_status") == "ok"]),
        "failed_records": len([record for record in source_records if record.get("scrape_status") != "ok"]),
        "link_queue_file": link_queue_output.as_posix(),
        "queued_links_saved": len(link_queue),
        "pending_links": len([item for item in link_queue if item.get("status") == "pending"]),
        "links_fetched_from_queue": 0,
        "load_error": load_error,
        "completed": load_error is None and validation_passed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
        "completed_at": utc_now_iso(),
    }

    save_json(sources_output, source_records)
    save_json(link_queue_output, link_queue)
    save_json(report_output, report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Seed URLs loaded: {len(seed_urls)}")
    print(f"Source records saved: {len(source_records)}")
    print(f"OK records: {report['ok_records']}")
    print(f"Failed records: {report['failed_records']}")
    print(f"Queued links saved: {len(link_queue)}")
    print(f"Links fetched from queue: {report['links_fetched_from_queue']}")
    print(f"Sources file: {sources_output}")
    print(f"Link queue file: {link_queue_output}")
    print(f"Report file: {report_output}")

    print("")
    print("Validation")
    print("----------")
    if validation_passed:
        print("Validation passed.")
    else:
        print("Validation failed.")
        for warning in validation_warnings:
            print(f"- {warning}")

    return 0 if load_error is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
