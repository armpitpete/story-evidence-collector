from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser
from scrapling.parser import Selector
import json
import time
from datetime import datetime, timezone


INPUT_QUEUE_FILE = "link_queue_filtered_v14.json"
CANDIDATE_SOURCES_OUTPUT_FILE = "candidate_sources_raw_v15.json"
REPORT_OUTPUT_FILE = "candidate_fetch_report_v15.json"

USER_AGENT = "StoryEvidenceCollector/1.5"
REQUEST_TIMEOUT_SECONDS = 20
TEXT_EXCERPT_CHARACTER_LIMIT = 3000
MAX_CANDIDATE_FETCHES = 3
POLITE_DELAY_SECONDS = 1


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


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


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


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).split())


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
    seen = set()

    for href in page.css("a::attr(href)").getall():
        cleaned_href = clean_text(href)

        if not cleaned_href:
            continue

        absolute_url = urljoin(base_url, cleaned_href)
        parsed_url = urlparse(absolute_url)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            continue

        if absolute_url in seen:
            continue

        seen.add(absolute_url)
        links.append(absolute_url)

    return links


def build_source_record(candidate_item, final_url, page, robots_report, robots_allowed):
    return {
        "source_url": candidate_item["url"],
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
        "found_on": candidate_item.get("found_on"),
        "depth": candidate_item.get("depth"),
    }


def build_blocked_source_record(candidate_item, robots_report):
    return {
        "source_url": candidate_item["url"],
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
        "found_on": candidate_item.get("found_on"),
        "depth": candidate_item.get("depth"),
    }


def build_error_source_record(candidate_item, robots_report, error_message):
    return {
        "source_url": candidate_item["url"],
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
        "found_on": candidate_item.get("found_on"),
        "depth": candidate_item.get("depth"),
    }


def fetch_candidate(candidate_item):
    url = candidate_item["url"]

    print(f"Checking robots.txt before candidate fetch: {url}")
    robots_parser, robots_report = load_robots_parser(url)
    print(f"robots.txt status: {robots_report['robots_txt_status']}")

    if robots_parser is None:
        return build_error_source_record(
            candidate_item,
            robots_report,
            "Could not check robots.txt safely."
        )

    robots_allowed = robots_allows_url(robots_parser, url)

    if not robots_allowed:
        print(f"Blocked by robots.txt: {url}")
        return build_blocked_source_record(candidate_item, robots_report)

    print(f"Fetching candidate: {url}")

    try:
        html, final_url = fetch_html(url)
    except RuntimeError as error:
        print(error)
        return build_error_source_record(candidate_item, robots_report, str(error))

    page = Selector(html)
    return build_source_record(candidate_item, final_url, page, robots_report, robots_allowed)


def validate_source_records(source_records):
    warnings = []

    for index, record in enumerate(source_records, start=1):
        if not record.get("source_url"):
            warnings.append(f"Candidate source record {index} is missing source_url.")

        if not record.get("scrape_status"):
            warnings.append(f"Candidate source record {index} is missing scrape_status.")

        if not record.get("robots_txt_url"):
            warnings.append(f"Candidate source record {index} is missing robots_txt_url.")

        if "robots_txt_checked" not in record:
            warnings.append(f"Candidate source record {index} is missing robots_txt_checked.")

        if "robots_allowed" not in record:
            warnings.append(f"Candidate source record {index} is missing robots_allowed.")

        if record.get("scrape_status") == "ok":
            if not record.get("final_url"):
                warnings.append(f"Candidate source record {index} is missing final_url.")

            if not record.get("page_title"):
                warnings.append(f"Candidate source record {index} is missing page_title.")

            if not record.get("text_excerpt"):
                warnings.append(f"Candidate source record {index} is missing text_excerpt.")

            if not isinstance(record.get("links_found"), list):
                warnings.append(f"Candidate source record {index} links_found is not a list.")

        if not record.get("found_on"):
            warnings.append(f"Candidate source record {index} is missing found_on.")

        if "depth" not in record:
            warnings.append(f"Candidate source record {index} is missing depth.")

    return warnings


def main():
    load_error = None
    fetched_records = []

    print("Starting strict limited candidate fetch")
    print(f"Input queue file: {INPUT_QUEUE_FILE}")
    print(f"Candidate sources output: {CANDIDATE_SOURCES_OUTPUT_FILE}")
    print(f"Report output: {REPORT_OUTPUT_FILE}")
    print(f"Max candidate fetches: {MAX_CANDIDATE_FETCHES}")
    print("")

    try:
        filtered_queue = load_json(INPUT_QUEUE_FILE)
    except RuntimeError as error:
        load_error = str(error)
        filtered_queue = []
        print(load_error)

    if not isinstance(filtered_queue, list):
        load_error = f"Input file must contain a list: {INPUT_QUEUE_FILE}"
        filtered_queue = []
        print(load_error)

    candidate_items = [
        item for item in filtered_queue
        if item.get("filter_status") == "candidate"
    ]

    skipped_items = [
        item for item in filtered_queue
        if item.get("filter_status") == "skipped"
    ]

    selected_candidates = candidate_items[:MAX_CANDIDATE_FETCHES]
    candidates_skipped_by_limit = candidate_items[MAX_CANDIDATE_FETCHES:]

    print(f"Candidate links loaded: {len(candidate_items)}")
    print(f"Skipped queue items ignored: {len(skipped_items)}")
    print(f"Candidate links selected: {len(selected_candidates)}")
    print(f"Candidate links skipped by limit: {len(candidates_skipped_by_limit)}")
    print("")

    for index, candidate_item in enumerate(selected_candidates, start=1):
        print(f"Candidate fetch {index} of {len(selected_candidates)}")
        record = fetch_candidate(candidate_item)
        fetched_records.append(record)

        if index < len(selected_candidates):
            print(f"Waiting {POLITE_DELAY_SECONDS} second before next candidate")
            print("")
            time.sleep(POLITE_DELAY_SECONDS)

    validation_warnings = validate_source_records(fetched_records)
    validation_passed = load_error is None and len(validation_warnings) == 0

    links_fetched = len([
        record for record in fetched_records
        if record.get("scrape_status") == "ok"
    ])
    links_skipped_by_robots = len([
        record for record in fetched_records
        if record.get("scrape_status") == "blocked_by_robots_txt"
    ])
    links_failed = len([
        record for record in fetched_records
        if record.get("scrape_status") == "error"
    ])

    report = {
        "input_queue_file": INPUT_QUEUE_FILE,
        "candidate_links_loaded": len(candidate_items),
        "skipped_links_ignored": len(skipped_items),
        "max_candidate_fetches": MAX_CANDIDATE_FETCHES,
        "candidate_links_selected": len(selected_candidates),
        "links_fetched": links_fetched,
        "links_skipped_by_limit": len(candidates_skipped_by_limit),
        "links_skipped_by_robots": links_skipped_by_robots,
        "links_failed": links_failed,
        "completed": validation_passed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
        "load_error": load_error,
        "fetched_urls": [
            record["source_url"] for record in fetched_records
            if record.get("scrape_status") == "ok"
        ],
        "robots_blocked_urls": [
            record["source_url"] for record in fetched_records
            if record.get("scrape_status") == "blocked_by_robots_txt"
        ],
        "failed_urls": [
            record["source_url"] for record in fetched_records
            if record.get("scrape_status") == "error"
        ],
    }

    save_json(CANDIDATE_SOURCES_OUTPUT_FILE, fetched_records)
    save_json(REPORT_OUTPUT_FILE, report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Candidate links loaded: {len(candidate_items)}")
    print(f"Candidate links selected: {len(selected_candidates)}")
    print(f"Links fetched: {links_fetched}")
    print(f"Links skipped by limit: {len(candidates_skipped_by_limit)}")
    print(f"Links skipped by robots: {links_skipped_by_robots}")
    print(f"Links failed: {links_failed}")
    print(f"Candidate sources file: {CANDIDATE_SOURCES_OUTPUT_FILE}")
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
