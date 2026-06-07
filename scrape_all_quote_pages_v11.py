from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser
from scrapling.parser import Selector
import json
import time


SEED_URLS_FILE = "seed_urls.json"
QUOTES_OUTPUT_FILE = "quotes_all_pages_v11.json"
REPORT_OUTPUT_FILE = "scrape_report_v11.json"

USER_AGENT = "StoryEvidenceCollector/1.1"
REQUEST_TIMEOUT_SECONDS = 20
POLITE_DELAY_SECONDS = 1
EXPECTED_QUOTE_COUNT = 100


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
            return response.read().decode("utf-8", errors="replace")

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


def parse_quotes(page, source_url):
    quotes = []

    for quote in page.css(".quote"):
        text = quote.css(".text::text").get()
        author = quote.css(".author::text").get()
        tags = [tag.strip() for tag in quote.css(".tags .tag::text").getall()]

        quotes.append({
            "source_url": source_url,
            "text": text.strip() if text else "",
            "author": author.strip() if author else "",
            "tags": tags,
        })

    return quotes


def find_next_url(page, current_url):
    next_href = page.css(".next a::attr(href)").get()

    if not next_href:
        return None

    return urljoin(current_url, next_href)


def validate_quotes(quotes):
    warnings = []

    if len(quotes) == 0:
        warnings.append("No quotes were found.")

    if len(quotes) < EXPECTED_QUOTE_COUNT:
        warnings.append(
            f"Expected {EXPECTED_QUOTE_COUNT} quotes, but only found {len(quotes)}."
        )

    for index, quote in enumerate(quotes, start=1):
        if not quote.get("source_url"):
            warnings.append(f"Quote {index} is missing source_url.")

        if not quote.get("text"):
            warnings.append(f"Quote {index} is missing text.")

        if not quote.get("author"):
            warnings.append(f"Quote {index} is missing author.")

    return warnings


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def scrape_seed_url(seed_url):
    current_url = seed_url
    quotes = []
    pages_scraped = 0
    failed_url = None
    robots_blocked_url = None

    print(f"Checking robots.txt for seed: {seed_url}")
    robots_parser, robots_report = load_robots_parser(seed_url)
    print(f"robots.txt status: {robots_report['robots_txt_status']}")

    if robots_parser is None:
        failed_url = robots_report["robots_txt_url"]
        print("Could not check robots.txt safely. Seed scrape stopped before fetching pages.")
    else:
        while current_url:
            print(f"Checking robots permission for: {current_url}")

            if not robots_allows_url(robots_parser, current_url):
                robots_blocked_url = current_url
                print(f"Blocked by robots.txt: {current_url}")
                break

            print(f"Fetching page {pages_scraped + 1}: {current_url}")

            try:
                html = fetch_html(current_url)
            except RuntimeError as error:
                failed_url = current_url
                print("")
                print("Scrape stopped because a page failed.")
                print(error)
                break

            page = Selector(html)

            page_quotes = parse_quotes(page, current_url)
            quotes.extend(page_quotes)
            pages_scraped += 1

            print(f"Found {len(page_quotes)} quotes on this page")
            print(f"Total quotes for this seed so far: {len(quotes)}")

            current_url = find_next_url(page, current_url)

            if current_url:
                print(f"Waiting {POLITE_DELAY_SECONDS} second before next page")
                print("")
                time.sleep(POLITE_DELAY_SECONDS)
            else:
                print("")
                print("No next page found for this seed.")

    return {
        "seed_url": seed_url,
        "quotes": quotes,
        "pages_scraped": pages_scraped,
        "failed_url": failed_url,
        "robots_blocked_url": robots_blocked_url,
        "robots_report": robots_report,
    }


def main():
    all_quotes = []
    seed_reports = []
    load_error = None

    print("Starting quote scrape")
    print(f"Seed URL file: {SEED_URLS_FILE}")
    print(f"Quotes output: {QUOTES_OUTPUT_FILE}")
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
        result = scrape_seed_url(seed_url)
        all_quotes.extend(result["quotes"])
        seed_reports.append({
            "seed_url": result["seed_url"],
            "pages_scraped": result["pages_scraped"],
            "quotes_saved": len(result["quotes"]),
            "failed_url": result["failed_url"],
            "robots_blocked_url": result["robots_blocked_url"],
            "robots_txt_url": result["robots_report"]["robots_txt_url"],
            "robots_txt_checked": result["robots_report"]["robots_txt_checked"],
            "robots_txt_status": result["robots_report"]["robots_txt_status"],
            "robots_txt_error": result["robots_report"]["robots_txt_error"],
        })

    validation_warnings = validate_quotes(all_quotes)
    validation_passed = len(validation_warnings) == 0

    failed_urls = [report["failed_url"] for report in seed_reports if report["failed_url"]]
    robots_blocked_urls = [
        report["robots_blocked_url"]
        for report in seed_reports
        if report["robots_blocked_url"]
    ]

    completed = (
        load_error is None
        and len(failed_urls) == 0
        and len(robots_blocked_urls) == 0
        and validation_passed
    )

    report = {
        "seed_urls_file": SEED_URLS_FILE,
        "seed_urls_loaded": seed_urls,
        "seed_url_count": len(seed_urls),
        "seed_reports": seed_reports,
        "pages_scraped": sum(report["pages_scraped"] for report in seed_reports),
        "quotes_saved": len(all_quotes),
        "failed_urls": failed_urls,
        "load_error": load_error,
        "completed": completed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
        "robots_blocked_urls": robots_blocked_urls,
    }

    save_json(QUOTES_OUTPUT_FILE, all_quotes)
    save_json(REPORT_OUTPUT_FILE, report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Seed URLs loaded: {len(seed_urls)}")
    print(f"Pages scraped: {report['pages_scraped']}")
    print(f"Quotes saved: {len(all_quotes)}")
    print(f"Quotes file: {QUOTES_OUTPUT_FILE}")
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
