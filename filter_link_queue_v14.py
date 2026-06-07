from urllib.parse import urlparse
import json


INPUT_QUEUE_FILE = "link_queue_v13.json"
FILTERED_QUEUE_OUTPUT_FILE = "link_queue_filtered_v14.json"
REPORT_OUTPUT_FILE = "source_report_v14.json"

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


def is_supported_http_url(url):
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def path_contains_any(path, markers):
    lowered_path = path.lower()
    return any(marker in lowered_path for marker in markers)


def classify_queue_item(item):
    url = item.get("url", "")
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()

    base = {
        "url": item.get("url"),
        "found_on": item.get("found_on"),
        "status": item.get("status"),
        "depth": item.get("depth"),
        "same_domain_as_seed": item.get("same_domain_as_seed"),
        "queued_at": item.get("queued_at"),
    }

    if not is_supported_http_url(url):
        return {
            **base,
            "filter_status": "skipped",
            "skip_reason": "unsupported_or_malformed_url",
        }

    if item.get("same_domain_as_seed") is not True:
        return {
            **base,
            "filter_status": "skipped",
            "skip_reason": "external_domain",
        }

    if path_contains_any(path, SKIP_PATH_PARTS):
        return {
            **base,
            "filter_status": "skipped",
            "skip_reason": "login_account_or_admin_link",
        }

    if path_contains_any(path, NAVIGATION_PATH_PARTS):
        return {
            **base,
            "filter_status": "skipped",
            "skip_reason": "navigation_or_tag_link",
        }

    return {
        **base,
        "filter_status": "candidate",
        "filter_reason": "same_domain_supported_non_utility_link",
    }


def filter_queue(queue_items):
    return [classify_queue_item(item) for item in queue_items]


def validate_filtered_queue(filtered_queue):
    warnings = []

    for index, item in enumerate(filtered_queue, start=1):
        if not item.get("url"):
            warnings.append(f"Filtered queue item {index} is missing url.")

        if not item.get("found_on"):
            warnings.append(f"Filtered queue item {index} is missing found_on.")

        if item.get("status") != "pending":
            warnings.append(f"Filtered queue item {index} does not have status pending.")

        if item.get("filter_status") not in {"candidate", "skipped"}:
            warnings.append(f"Filtered queue item {index} has invalid filter_status.")

        if item.get("filter_status") == "candidate" and not item.get("filter_reason"):
            warnings.append(f"Candidate queue item {index} is missing filter_reason.")

        if item.get("filter_status") == "skipped" and not item.get("skip_reason"):
            warnings.append(f"Skipped queue item {index} is missing skip_reason.")

    return warnings


def main():
    load_error = None

    print("Starting queue filter")
    print(f"Input queue file: {INPUT_QUEUE_FILE}")
    print(f"Filtered queue output: {FILTERED_QUEUE_OUTPUT_FILE}")
    print(f"Report output: {REPORT_OUTPUT_FILE}")
    print("")

    try:
        queue_items = load_json(INPUT_QUEUE_FILE)
    except RuntimeError as error:
        load_error = str(error)
        queue_items = []
        print(load_error)

    if not isinstance(queue_items, list):
        load_error = f"Input file must contain a list: {INPUT_QUEUE_FILE}"
        queue_items = []
        print(load_error)

    filtered_queue = filter_queue(queue_items)

    candidates = [
        item for item in filtered_queue
        if item.get("filter_status") == "candidate"
    ]
    skipped = [
        item for item in filtered_queue
        if item.get("filter_status") == "skipped"
    ]

    validation_warnings = validate_filtered_queue(filtered_queue)
    validation_passed = load_error is None and len(validation_warnings) == 0

    report = {
        "input_queue_file": INPUT_QUEUE_FILE,
        "filtered_queue_file": FILTERED_QUEUE_OUTPUT_FILE,
        "queued_links_loaded": len(queue_items),
        "candidate_links": len(candidates),
        "skipped_links": len(skipped),
        "links_fetched": 0,
        "load_error": load_error,
        "completed": validation_passed,
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
        "skip_reason_counts": build_skip_reason_counts(skipped),
    }

    save_json(FILTERED_QUEUE_OUTPUT_FILE, filtered_queue)
    save_json(REPORT_OUTPUT_FILE, report)

    print("Final summary")
    print("-------------")
    print(f"Queued links loaded: {len(queue_items)}")
    print(f"Candidate links: {len(candidates)}")
    print(f"Skipped links: {len(skipped)}")
    print(f"Links fetched: {report['links_fetched']}")
    print(f"Filtered queue file: {FILTERED_QUEUE_OUTPUT_FILE}")
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


def build_skip_reason_counts(skipped_items):
    counts = {}

    for item in skipped_items:
        reason = item.get("skip_reason", "unknown")
        counts[reason] = counts.get(reason, 0) + 1

    return counts


if __name__ == "__main__":
    main()
