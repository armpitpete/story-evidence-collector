from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser
from scrapling.parser import Selector
import json
import os
import time
from datetime import datetime, timezone


INPUT_CANDIDATE_SOURCES_FILE = "candidate_sources_raw_v15.json"
FOLLOWED_SOURCES_OUTPUT_FILE = "followed_sources_raw_v16.json"
REPORT_OUTPUT_FILE = "followed_fetch_report_v16.json"

OPTIONAL_KNOWN_URL_FILES = [
    {
        "filename": "sources_raw_v13.json",
        "kind": "source_records",
        "url_fields": ["source_url", "final_url"],
    },
    {
        "filename": "source_records_v13.json",
        "kind": "source_records",
        "url_fields": ["source_url", "final_url"],
    },
    {
        "filename": "link_queue_v13.json",
        "kind": "queue",
        "url_fields": ["url"],
    },
    {
        "filename": "link_queue_filtered_v14.json",
        "kind": "filtered_queue",
        "url_fields": ["url"],
    },
    {
        "filename": "candidate_sources_raw_v15.json",
        "kind": "candidate_source_records",
        "url_fields": ["source_url", "final_url"],
    },
]

SKIP_PATH_PARTS = [
    "/login",
    "/logout",
    "/account",
    "/admin",
    "/signin",
    "/sign-in",
    "/signup",
    "/sign-up",
    "/register",
]

NAVIGATION_PATH_PARTS = [
    "/tag/",
]

USER_AGENT = "StoryEvidenceCollector/1.6"
REQUEST_TIMEOUT_SECONDS = 20
TEXT_EXCERPT_CHARACTER_LIMIT = 3000
MAX_FOLLOW_FETCHES = 3
POLITE_DELAY_SECONDS = 1
FOLLOW_EXTERNAL_DOMAINS = False


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise RuntimeError(f"Missing input file: {filename}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Input file is not valid JSON: {filename}") from error


def load_optional_json(filename):
    if not os.path.exists(filename):
        return None, {
            "filename": filename,
            "loaded": False,
            "status": "missing",
            "item_count": 0,
            "error": None,
        }

    try:
        data = load_json(filename)
    except RuntimeError as error:
        return None, {
            "filename": filename,
            "loaded": False,
            "status": "error",
            "item_count": 0,
            "error": str(error),
        }

    item_count = len(data) if isinstance(data, list) else 1

    return data, {
        "filename": filename,
        "loaded": True,
        "status": "loaded",
        "item_count": item_count,
        "error": None,
    }


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).split())


def normalize_url(raw_url, base_url=None):
    cleaned_url = clean_text(raw_url)

    if not cleaned_url:
        return None, "empty_url"

    if cleaned_url.startswith("#"):
        return None, "fragment_only"

    parsed_raw = urlparse(cleaned_url)

    if parsed_raw.scheme and parsed_raw.scheme.lower() not in {"http", "https"}:
        return None, "unsupported_url_scheme"

    absolute_url = urljoin(base_url or "", cleaned_url)
    absolute_url, _fragment = urldefrag(absolute_url)
    parsed_url = urlparse(absolute_url)

    if parsed_url.scheme.lower() not in {"http", "https"} or not parsed_url.netloc:
        return None, "unsupported_or_malformed_url"

    normalised_path = parsed_url.path or "/"

    return urlunparse((
        parsed_url.scheme.lower(),
        parsed_url.netloc.lower(),
        normalised_path,
        parsed_url.params,
        parsed_url.query,
        "",
    )), None


def build_url_key(raw_url, base_url=None):
    normalised_url, skip_reason = normalize_url(raw_url, base_url)

    if skip_reason:
        return None, skip_reason

    parsed_url = urlparse(normalised_url)

    # Scheme is deliberately excluded so http://example/path and
    # https://example/path are treated as the same known page.
    return urlunparse((
        "",
        parsed_url.netloc.lower(),
        parsed_url.path or "/",
        parsed_url.params,
        parsed_url.query,
        "",
    )), None


def is_same_domain(url, source_url):
    return urlparse(url).netloc.lower() == urlparse(source_url).netloc.lower()


def path_contains_any(path, markers):
    lowered_path = path.lower()
    return any(marker in lowered_path for marker in markers)


def classify_supported_follow_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()

    if path_contains_any(path, SKIP_PATH_PARTS):
        return "login_account_or_admin_link"

    if path_contains_any(path, NAVIGATION_PATH_PARTS):
        return "navigation_or_tag_link"

    return None


def fetch_html(url):
    req = Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            html = response.read().decode("utf-8", errors="replace")
            return html, final_url

    except HTTPError as error:
        raise RuntimeError(f"HTTP error {error.code} while fetching {url}") from error

    except URLError as error:
        raise RuntimeError(f"Network error while fetching {url}: {error.reason}") from error

    except TimeoutError as error:
        raise RuntimeError(f"Timed out while fetching {url}") from error


def load_robots_parser(url):
    robots_url = urljoin(url, "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)

    req = Request(
        robots_url,
        headers={"User-Agent": USER_AGENT}
    )

    try:
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            robots_text = response.read().decode("utf-8", errors="replace")

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


def robots_allows_url(parser, url):
    if parser is None:
        return False

    return parser.can_fetch(USER_AGENT, url)


def extract_page_title(page):
    title = page.css("title::text").get()
    return clean_text(title)


def extract_visible_text_excerpt(page):
    text_parts = []

    for text_node in page.css("body ::text").getall():
        cleaned = clean_text(text_node)
        if cleaned:
            text_parts.append(cleaned)

    full_text = " ".join(text_parts)
    return full_text[:TEXT_EXCERPT_CHARACTER_LIMIT]


def extract_links(page, base_url):
    links = []
    seen_keys = set()

    for href in page.css("a::attr(href)").getall():
        normalised_url, skip_reason = normalize_url(href, base_url)

        if skip_reason:
            continue

        url_key, key_skip_reason = build_url_key(normalised_url)

        if key_skip_reason:
            continue

        if url_key in seen_keys:
            continue

        seen_keys.add(url_key)
        links.append(normalised_url)

    return links


def add_known_url_key(known_url_keys, raw_url):
    url_key, skip_reason = build_url_key(raw_url)

    if skip_reason:
        return False

    known_url_keys.add(url_key)
    return True


def add_known_url_keys_from_record(known_url_keys, record, url_fields):
    added_count = 0

    if not isinstance(record, dict):
        return added_count

    for field_name in url_fields:
        if add_known_url_key(known_url_keys, record.get(field_name)):
            added_count += 1

    return added_count


def load_known_url_keys():
    known_url_keys = set()
    file_reports = []

    for file_config in OPTIONAL_KNOWN_URL_FILES:
        filename = file_config["filename"]
        data, file_report = load_optional_json(filename)
        file_report["kind"] = file_config["kind"]
        file_report["known_urls_added"] = 0

        if data is None:
            file_reports.append(file_report)
            continue

        if isinstance(data, list):
            for record in data:
                file_report["known_urls_added"] += add_known_url_keys_from_record(
                    known_url_keys,
                    record,
                    file_config["url_fields"]
                )

        elif isinstance(data, dict):
            file_report["known_urls_added"] += add_known_url_keys_from_record(
                known_url_keys,
                data,
                file_config["url_fields"]
            )

        else:
            file_report["status"] = "unsupported_json_shape"
            file_report["error"] = "Expected a list or object."

        file_reports.append(file_report)

    return known_url_keys, file_reports


def get_source_page_url(candidate_record):
    return (
        candidate_record.get("final_url")
        or candidate_record.get("source_url")
        or candidate_record.get("url")
    )


def build_follow_candidates(candidate_records, known_url_keys):
    follow_candidates = []
    skipped_links = []
    discovered_count = 0
    seen_this_run_keys = set()

    for candidate_record in candidate_records:
        if not isinstance(candidate_record, dict):
            skipped_links.append({
                "url": None,
                "found_on": None,
                "skip_reason": "invalid_candidate_record",
            })
            continue

        if candidate_record.get("scrape_status") != "ok":
            skipped_links.append({
                "url": candidate_record.get("source_url"),
                "found_on": candidate_record.get("source_url"),
                "skip_reason": "candidate_page_not_successfully_fetched",
            })
            continue

        source_page_url = get_source_page_url(candidate_record)
        links_found = candidate_record.get("links_found", [])

        if not isinstance(links_found, list):
            skipped_links.append({
                "url": source_page_url,
                "found_on": source_page_url,
                "skip_reason": "links_found_not_list",
            })
            continue

        for raw_link in links_found:
            discovered_count += 1
            normalised_url, skip_reason = normalize_url(raw_link, source_page_url)

            if skip_reason:
                skipped_links.append({
                    "url": raw_link,
                    "found_on": source_page_url,
                    "skip_reason": skip_reason,
                })
                continue

            if FOLLOW_EXTERNAL_DOMAINS is False and not is_same_domain(normalised_url, source_page_url):
                skipped_links.append({
                    "url": normalised_url,
                    "found_on": source_page_url,
                    "skip_reason": "external_domain",
                })
                continue

            filter_skip_reason = classify_supported_follow_url(normalised_url)

            if filter_skip_reason:
                skipped_links.append({
                    "url": normalised_url,
                    "found_on": source_page_url,
                    "skip_reason": filter_skip_reason,
                })
                continue

            url_key, key_skip_reason = build_url_key(normalised_url)

            if key_skip_reason:
                skipped_links.append({
                    "url": normalised_url,
                    "found_on": source_page_url,
                    "skip_reason": key_skip_reason,
                })
                continue

            if url_key in known_url_keys:
                skipped_links.append({
                    "url": normalised_url,
                    "found_on": source_page_url,
                    "skip_reason": "already_known",
                })
                continue

            if url_key in seen_this_run_keys:
                skipped_links.append({
                    "url": normalised_url,
                    "found_on": source_page_url,
                    "skip_reason": "duplicate_in_v16_run",
                })
                continue

            seen_this_run_keys.add(url_key)
            follow_candidates.append({
                "url": normalised_url,
                "url_key": url_key,
                "found_on": source_page_url,
                "status": "pending",
                "depth": int(candidate_record.get("depth", 1) or 1) + 1,
                "queued_at": utc_now_iso(),
                "source_candidate_url": candidate_record.get("source_url"),
                "source_candidate_final_url": candidate_record.get("final_url"),
            })

    return follow_candidates, skipped_links, discovered_count


def build_source_record(follow_item, final_url, page, robots_report, robots_allowed):
    return {
        "source_url": follow_item["url"],
        "final_url": final_url,
        "page_title": extract_page_title(page),
        "text_excerpt": extract_visible_text_excerpt(page),
        "links_found": extract_links(page, final_url),
        "robots_txt_url": robots_report["robots_txt_url"],
        "robots_txt_checked": robots_report["robots_txt_checked"],
        "robots_txt_status": robots_report["robots_txt_status"],
        "robots_allowed": robots_allowed,
        "scrape_status": "ok",
        "error": None,
        "scraped_at": utc_now_iso(),
        "found_on": follow_item.get("found_on"),
        "depth": follow_item.get("depth"),
        "source_candidate_url": follow_item.get("source_candidate_url"),
        "source_candidate_final_url": follow_item.get("source_candidate_final_url"),
    }


def build_blocked_source_record(follow_item, robots_report):
    return {
        "source_url": follow_item["url"],
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
        "found_on": follow_item.get("found_on"),
        "depth": follow_item.get("depth"),
        "source_candidate_url": follow_item.get("source_candidate_url"),
        "source_candidate_final_url": follow_item.get("source_candidate_final_url"),
    }


def build_error_source_record(follow_item, robots_report, error_message):
    return {
        "source_url": follow_item["url"],
        "final_url": None,
        "page_title": "",
        "text_excerpt": "",
        "links_found": [],
        "robots_txt_url": robots_report["robots_txt_url"],
        "robots_txt_checked": robots_report["robots_txt_checked"],
        "robots_txt_status": robots_report["robots_txt_status"],
        "robots_allowed": robots_report["robots_txt_checked"],
        "scrape_status": "error",
        "error": error_message,
        "scraped_at": utc_now_iso(),
        "found_on": follow_item.get("found_on"),
        "depth": follow_item.get("depth"),
        "source_candidate_url": follow_item.get("source_candidate_url"),
        "source_candidate_final_url": follow_item.get("source_candidate_final_url"),
    }


def fetch_followed_url(follow_item):
    url = follow_item["url"]

    print(f"Checking robots.txt before followed fetch: {url}")
    robots_parser, robots_report = load_robots_parser(url)
    print(f"robots.txt status: {robots_report['robots_txt_status']}")

    if robots_parser is None:
        return build_error_source_record(
            follow_item,
            robots_report,
            "Could not check robots.txt safely."
        )

    robots_allowed = robots_allows_url(robots_parser, url)

    if not robots_allowed:
        print(f"Blocked by robots.txt: {url}")
        return build_blocked_source_record(follow_item, robots_report)

    print(f"Fetching followed page: {url}")

    try:
        html, final_url = fetch_html(url)
    except RuntimeError as error:
        print(error)
        return build_error_source_record(follow_item, robots_report, str(error))

    page = Selector(html)
    return build_source_record(follow_item, final_url, page, robots_report, robots_allowed)


def validate_source_records(source_records):
    warnings = []

    for index, record in enumerate(source_records, start=1):
        if not record.get("source_url"):
            warnings.append(f"Followed source record {index} is missing source_url.")

        if not record.get("scrape_status"):
            warnings.append(f"Followed source record {index} is missing scrape_status.")

        if not record.get("robots_txt_url"):
            warnings.append(f"Followed source record {index} is missing robots_txt_url.")

        if "robots_txt_checked" not in record:
            warnings.append(f"Followed source record {index} is missing robots_txt_checked.")

        if "robots_allowed" not in record:
            warnings.append(f"Followed source record {index} is missing robots_allowed.")

        if record.get("scrape_status") == "ok":
            if not record.get("final_url"):
                warnings.append(f"Followed source record {index} is missing final_url.")

            if not record.get("page_title"):
                warnings.append(f"Followed source record {index} is missing page_title.")

            if not record.get("text_excerpt"):
                warnings.append(f"Followed source record {index} is missing text_excerpt.")

            if not isinstance(record.get("links_found"), list):
                warnings.append(f"Followed source record {index} links_found is not a list.")

        if not record.get("found_on"):
            warnings.append(f"Followed source record {index} is missing found_on.")

        if "depth" not in record:
            warnings.append(f"Followed source record {index} is missing depth.")

    return warnings


def count_skips(skipped_items, reasons):
    return len([
        item for item in skipped_items
        if item.get("skip_reason") in reasons
    ])


def build_robots_blocked_skip_details(followed_records):
    return [
        {
            "url": record.get("source_url"),
            "found_on": record.get("found_on"),
            "skip_reason": "blocked_by_robots_txt",
            "robots_txt_url": record.get("robots_txt_url"),
            "robots_txt_status": record.get("robots_txt_status"),
        }
        for record in followed_records
        if record.get("scrape_status") == "blocked_by_robots_txt"
    ]


def build_skip_reason_counts(skipped_items):
    counts = {}

    for item in skipped_items:
        reason = item.get("skip_reason", "unknown")
        counts[reason] = counts.get(reason, 0) + 1

    return counts


def main():
    load_error = None
    followed_records = []

    print("Starting limited followed-link fetch")
    print(f"Input candidate sources file: {INPUT_CANDIDATE_SOURCES_FILE}")
    print(f"Followed sources output: {FOLLOWED_SOURCES_OUTPUT_FILE}")
    print(f"Report output: {REPORT_OUTPUT_FILE}")
    print(f"Max follow fetches: {MAX_FOLLOW_FETCHES}")
    print(f"Follow external domains: {FOLLOW_EXTERNAL_DOMAINS}")
    print("")

    try:
        candidate_records = load_json(INPUT_CANDIDATE_SOURCES_FILE)
    except RuntimeError as error:
        load_error = str(error)
        candidate_records = []
        print(load_error)

    if not isinstance(candidate_records, list):
        load_error = f"Input file must contain a list: {INPUT_CANDIDATE_SOURCES_FILE}"
        candidate_records = []
        print(load_error)

    fetched_candidate_records = [
        record for record in candidate_records
        if isinstance(record, dict) and record.get("scrape_status") == "ok"
    ]

    known_url_keys, known_file_reports = load_known_url_keys()
    follow_candidates, skipped_links_before_limit, discovered_links = build_follow_candidates(
        candidate_records,
        known_url_keys
    )

    selected_follow_candidates = follow_candidates[:MAX_FOLLOW_FETCHES]
    candidates_skipped_by_limit = follow_candidates[MAX_FOLLOW_FETCHES:]

    skipped_links = list(skipped_links_before_limit)

    for item in candidates_skipped_by_limit:
        skipped_links.append({
            "url": item["url"],
            "found_on": item.get("found_on"),
            "skip_reason": "skipped_by_limit",
        })

    print(f"Fetched candidate pages loaded: {len(fetched_candidate_records)}")
    print(f"Links discovered from fetched candidates: {discovered_links}")
    print(f"Known URL keys loaded: {len(known_url_keys)}")
    print(f"Follow candidates after known-url checks: {len(follow_candidates)}")
    print(f"Follow candidates selected: {len(selected_follow_candidates)}")
    print(f"Follow candidates skipped by limit: {len(candidates_skipped_by_limit)}")
    print("")

    for index, follow_item in enumerate(selected_follow_candidates, start=1):
        print(f"Followed fetch {index} of {len(selected_follow_candidates)}")
        record = fetch_followed_url(follow_item)
        followed_records.append(record)

        if index < len(selected_follow_candidates):
            print(f"Waiting {POLITE_DELAY_SECONDS} second before next followed fetch")
            print("")
            time.sleep(POLITE_DELAY_SECONDS)

    validation_warnings = validate_source_records(followed_records)
    validation_passed = load_error is None and len(validation_warnings) == 0

    links_fetched = len([
        record for record in followed_records
        if record.get("scrape_status") == "ok"
    ])
    links_skipped_by_robots = len([
        record for record in followed_records
        if record.get("scrape_status") == "blocked_by_robots_txt"
    ])
    links_failed = len([
        record for record in followed_records
        if record.get("scrape_status") == "error"
    ])

    skip_reason_counts = build_skip_reason_counts(skipped_links)
    robots_blocked_skip_details = build_robots_blocked_skip_details(followed_records)
    all_skipped_urls = skipped_links + robots_blocked_skip_details

    report = {
        "input_candidate_sources_file": INPUT_CANDIDATE_SOURCES_FILE,
        "followed_sources_file": FOLLOWED_SOURCES_OUTPUT_FILE,
        "max_follow_fetches": MAX_FOLLOW_FETCHES,
        "follow_external_domains": FOLLOW_EXTERNAL_DOMAINS,
        "fetched_candidate_pages_loaded": len(fetched_candidate_records),
        "candidate_records_loaded": len(candidate_records),
        "links_discovered_from_fetched_candidates": discovered_links,
        "known_url_files": known_file_reports,
        "known_url_keys_loaded": len(known_url_keys),
        "links_ignored_as_non_http_or_unsafe": count_skips(
            skipped_links,
            {
                "empty_url",
                "fragment_only",
                "unsupported_url_scheme",
                "unsupported_or_malformed_url",
                "external_domain",
            }
        ),
        "links_skipped_as_login_account_or_admin": count_skips(
            skipped_links,
            {"login_account_or_admin_link"}
        ),
        "links_skipped_as_navigation_or_tag": count_skips(
            skipped_links,
            {"navigation_or_tag_link"}
        ),
        "links_already_known": count_skips(skipped_links, {"already_known"}),
        "links_ignored_or_skipped_before_fetch": len(skipped_links),
        "skip_reason_counts": skip_reason_counts,
        "follow_candidates_after_known_url_checks": len(follow_candidates),
        "follow_links_selected": len(selected_follow_candidates),
        "links_fetched": links_fetched,
        "links_skipped_by_limit": len(candidates_skipped_by_limit),
        "links_skipped_by_robots": links_skipped_by_robots,
        "links_failed": links_failed,
        "completed": validation_passed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
        "load_error": load_error,
        "fetched_urls": [
            record["source_url"] for record in followed_records
            if record.get("scrape_status") == "ok"
        ],
        "robots_blocked_urls": [
            record["source_url"] for record in followed_records
            if record.get("scrape_status") == "blocked_by_robots_txt"
        ],
        "robots_blocked_url_details": robots_blocked_skip_details,
        "failed_urls": [
            record["source_url"] for record in followed_records
            if record.get("scrape_status") == "error"
        ],
        "followed_url_sources": [
            {
                "url": item["url"],
                "found_on": item.get("found_on"),
                "depth": item.get("depth"),
            }
            for item in selected_follow_candidates
        ],
        "skipped_urls": all_skipped_urls,
    }

    save_json(FOLLOWED_SOURCES_OUTPUT_FILE, followed_records)
    save_json(REPORT_OUTPUT_FILE, report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Fetched candidate pages loaded: {len(fetched_candidate_records)}")
    print(f"Links discovered from fetched candidates: {discovered_links}")
    print(f"Follow links selected: {len(selected_follow_candidates)}")
    print(f"Links fetched: {links_fetched}")
    print(f"Links skipped by limit: {len(candidates_skipped_by_limit)}")
    print(f"Links skipped by robots: {links_skipped_by_robots}")
    print(f"Links failed: {links_failed}")
    print(f"Followed sources file: {FOLLOWED_SOURCES_OUTPUT_FILE}")
    print(f"Report file: {REPORT_OUTPUT_FILE}")

    print("")
    print("Validation")
    print("----------")

    if validation_passed:
        print("Validation passed.")
    else:
        print("Validation failed.")
        for warning in validation_warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
