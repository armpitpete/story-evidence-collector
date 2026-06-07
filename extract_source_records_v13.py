from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser
from scrapling.parser import Selector
import json
from datetime import datetime, timezone


SEED_URLS_FILE = "seed_urls.json"
SOURCES_OUTPUT_FILE = "sources_raw_v13.json"
LINK_QUEUE_OUTPUT_FILE = "link_queue_v13.json"
REPORT_OUTPUT_FILE = "source_report_v13.json"

USER_AGENT = "StoryEvidenceCollector/1.3"
REQUEST_TIMEOUT_SECONDS = 20
TEXT_EXCERPT_CHARACTER_LIMIT = 3000


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_seed_urls(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise RuntimeError(f"Missing seed URL file: {filename}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Seed URL file is not valid JSON: {filename}") from error

    seed_urls = data.get("seed_urls")

    if not isinstance(seed_urls, list):
        raise RuntimeError("seed_urls.json must contain a list called 'seed_urls'.")

    if len(seed_urls) == 0:
        raise RuntimeError("seed_urls.json must contain at least one URL.")

    cleaned_urls = []

    for index, url in enumerate(seed_urls, start=1):
        if not isinstance(url, str) or not url.strip():
            raise RuntimeError(f"Seed URL {index} is missing or empty.")

        cleaned_url = url.strip()
        parsed_url = urlparse(cleaned_url)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise RuntimeError(f"Seed URL {index} is not a valid HTTP/HTTPS URL: {cleaned_url}")

        cleaned_urls.append(cleaned_url)

    return cleaned_urls


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


def load_robots_parser(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
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


def is_same_domain(url, seed_url):
    return urlparse(url).netloc.lower() == urlparse(seed_url).netloc.lower()


def build_link_queue_items(links_found, found_on, seed_url):
    queued_at = utc_now_iso()
    queue_items = []

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


def build_blocked_source_record(seed_url, robots_report):
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


def build_error_source_record(seed_url, robots_report, error_message):
    return {
        "source_url": seed_url,
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
    }


def extract_source_record(seed_url):
    print(f"Checking robots.txt for seed: {seed_url}")
    robots_parser, robots_report = load_robots_parser(seed_url)
    print(f"robots.txt status: {robots_report['robots_txt_status']}")

    if robots_parser is None:
        return build_error_source_record(
            seed_url,
            robots_report,
            "Could not check robots.txt safely."
        )

    robots_allowed = robots_allows_url(robots_parser, seed_url)

    if not robots_allowed:
        print(f"Blocked by robots.txt: {seed_url}")
        return build_blocked_source_record(seed_url, robots_report)

    print(f"Fetching seed page only: {seed_url}")

    try:
        html, final_url = fetch_html(seed_url)
    except RuntimeError as error:
        print(error)
        return build_error_source_record(seed_url, robots_report, str(error))

    page = Selector(html)
    links_found = extract_links(page, final_url)

    source_record = {
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

    return source_record


def build_link_queue(source_records):
    queue = []
    seen_urls = set()

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


def validate_source_records(source_records):
    warnings = []

    if len(source_records) == 0:
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


def validate_link_queue(link_queue):
    warnings = []

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


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    source_records = []
    load_error = None

    print("Starting source record extraction and link queue build")
    print(f"Seed URL file: {SEED_URLS_FILE}")
    print(f"Sources output: {SOURCES_OUTPUT_FILE}")
    print(f"Link queue output: {LINK_QUEUE_OUTPUT_FILE}")
    print(f"Report output: {REPORT_OUTPUT_FILE}")
    print("")

    try:
        seed_urls = load_seed_urls(SEED_URLS_FILE)
    except RuntimeError as error:
        load_error = str(error)
        seed_urls = []
        print(load_error)

    for seed_url in seed_urls:
        print("")
        print(f"Seed URL: {seed_url}")
        source_record = extract_source_record(seed_url)
        source_records.append(source_record)

        print(f"Scrape status: {source_record['scrape_status']}")
        print(f"Page title: {source_record['page_title']}")
        print(f"Links found: {len(source_record['links_found'])}")

    link_queue = build_link_queue(source_records)

    source_validation_warnings = validate_source_records(source_records)
    link_queue_validation_warnings = validate_link_queue(link_queue)
    validation_warnings = source_validation_warnings + link_queue_validation_warnings
    validation_passed = len(validation_warnings) == 0

    report = {
        "seed_urls_file": SEED_URLS_FILE,
        "seed_urls_loaded": seed_urls,
        "seed_url_count": len(seed_urls),
        "source_records_saved": len(source_records),
        "ok_records": len([
            record for record in source_records
            if record.get("scrape_status") == "ok"
        ]),
        "failed_records": len([
            record for record in source_records
            if record.get("scrape_status") != "ok"
        ]),
        "link_queue_file": LINK_QUEUE_OUTPUT_FILE,
        "queued_links_saved": len(link_queue),
        "pending_links": len([
            item for item in link_queue
            if item.get("status") == "pending"
        ]),
        "links_fetched": 0,
        "load_error": load_error,
        "completed": load_error is None and validation_passed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
    }

    save_json(SOURCES_OUTPUT_FILE, source_records)
    save_json(LINK_QUEUE_OUTPUT_FILE, link_queue)
    save_json(REPORT_OUTPUT_FILE, report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Seed URLs loaded: {len(seed_urls)}")
    print(f"Source records saved: {len(source_records)}")
    print(f"Queued links saved: {len(link_queue)}")
    print(f"Links fetched from queue: {report['links_fetched']}")
    print(f"Sources file: {SOURCES_OUTPUT_FILE}")
    print(f"Link queue file: {LINK_QUEUE_OUTPUT_FILE}")
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
