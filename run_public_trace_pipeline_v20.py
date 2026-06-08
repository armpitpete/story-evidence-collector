import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urldefrag


PIPELINE_STEPS = [
    "extract_source_records_v13.py",
    "filter_link_queue_v14.py",
    "fetch_candidate_links_v15.py",
    "follow_fetched_candidate_links_v16.py",
    "create_trace_report_v17.py",
    "create_trace_report_v18.py",
]

TRACE_JSON_FILE = Path("trace_report_v18.json")
TRACE_MARKDOWN_FILE = Path("trace_report_v18.md")

SOURCE_RECORD_FILES_TO_SANITISE = [
    Path("sources_raw_v13.json"),
    Path("candidate_sources_raw_v15.json"),
]

QUEUE_FILES_TO_SANITISE = [
    Path("link_queue_v13.json"),
    Path("link_queue_filtered_v14.json"),
]


def run_step(script_name):
    print("")
    print(f"Running: {script_name}")
    print("-" * (9 + len(script_name)))

    script_path = Path(script_name)

    if not script_path.exists():
        print(f"FAILED: missing script: {script_name}")
        return False

    result = subprocess.run([sys.executable, script_name])

    if result.returncode != 0:
        print(f"FAILED: {script_name}")
        return False

    print(f"OK: {script_name}")
    return True


def strip_fragment(value):
    if not isinstance(value, str):
        return value

    stripped_value = value.strip()

    if not stripped_value:
        return stripped_value

    cleaned_url, _fragment = urldefrag(stripped_value)
    return cleaned_url


def load_json_file(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def sanitise_url_list(urls, found_on=None):
    if not isinstance(urls, list):
        return urls, 0, 0

    clean_urls = []
    seen = set()
    changed_count = 0
    dropped_count = 0
    clean_found_on = strip_fragment(found_on)

    for raw_url in urls:
        clean_url = strip_fragment(raw_url)

        if clean_url != raw_url:
            changed_count += 1

        if not clean_url:
            dropped_count += 1
            continue

        if clean_found_on and clean_url == clean_found_on:
            dropped_count += 1
            continue

        if clean_url in seen:
            dropped_count += 1
            continue

        seen.add(clean_url)
        clean_urls.append(clean_url)

    return clean_urls, changed_count, dropped_count


def sanitise_source_records(path):
    if not path.exists():
        return {
            "file": str(path),
            "loaded": False,
            "changed_urls": 0,
            "dropped_urls": 0,
        }

    data = load_json_file(path)

    if not isinstance(data, list):
        return {
            "file": str(path),
            "loaded": True,
            "changed_urls": 0,
            "dropped_urls": 0,
            "warning": "expected_list",
        }

    changed_count = 0
    dropped_count = 0

    for record in data:
        if not isinstance(record, dict):
            continue

        for field_name in ["source_url", "final_url", "found_on"]:
            original_url = record.get(field_name)
            clean_url = strip_fragment(original_url)

            if clean_url != original_url:
                record[field_name] = clean_url
                changed_count += 1

        links_found, link_changes, link_drops = sanitise_url_list(
            record.get("links_found"),
            record.get("final_url") or record.get("source_url"),
        )

        if isinstance(record.get("links_found"), list):
            record["links_found"] = links_found
            changed_count += link_changes
            dropped_count += link_drops

    save_json_file(path, data)

    return {
        "file": str(path),
        "loaded": True,
        "changed_urls": changed_count,
        "dropped_urls": dropped_count,
    }


def sanitise_queue(path):
    if not path.exists():
        return {
            "file": str(path),
            "loaded": False,
            "changed_urls": 0,
            "dropped_urls": 0,
        }

    data = load_json_file(path)

    if not isinstance(data, list):
        return {
            "file": str(path),
            "loaded": True,
            "changed_urls": 0,
            "dropped_urls": 0,
            "warning": "expected_list",
        }

    clean_items = []
    seen_urls = set()
    changed_count = 0
    dropped_count = 0

    for item in data:
        if not isinstance(item, dict):
            dropped_count += 1
            continue

        original_url = item.get("url")
        original_found_on = item.get("found_on")
        clean_url = strip_fragment(original_url)
        clean_found_on = strip_fragment(original_found_on)

        if clean_url != original_url:
            item["url"] = clean_url
            changed_count += 1

        if clean_found_on != original_found_on:
            item["found_on"] = clean_found_on
            changed_count += 1

        if not clean_url:
            dropped_count += 1
            continue

        if clean_found_on and clean_url == clean_found_on:
            dropped_count += 1
            continue

        if clean_url in seen_urls:
            dropped_count += 1
            continue

        seen_urls.add(clean_url)
        clean_items.append(item)

    save_json_file(path, clean_items)

    return {
        "file": str(path),
        "loaded": True,
        "changed_urls": changed_count,
        "dropped_urls": dropped_count,
    }


def print_sanitise_report(title, reports):
    print("")
    print(title)
    print("-" * len(title))

    for report in reports:
        if report.get("loaded") is False:
            print(f"{report['file']}: missing")
            continue

        warning = report.get("warning")
        if warning:
            print(f"{report['file']}: warning={warning}")
            continue

        print(
            f"{report['file']}: "
            f"changed={report['changed_urls']} "
            f"dropped={report['dropped_urls']}"
        )


def sanitise_after_source_extraction():
    source_reports = [
        sanitise_source_records(Path("sources_raw_v13.json")),
    ]
    queue_reports = [
        sanitise_queue(Path("link_queue_v13.json")),
    ]

    print_sanitise_report("Sanitised v1.3 source outputs", source_reports + queue_reports)


def sanitise_after_queue_filter():
    reports = [
        sanitise_queue(Path("link_queue_filtered_v14.json")),
    ]

    print_sanitise_report("Sanitised v1.4 filtered queue", reports)


def sanitise_after_candidate_fetch():
    reports = [
        sanitise_source_records(Path("candidate_sources_raw_v15.json")),
    ]

    print_sanitise_report("Sanitised v1.5 candidate outputs", reports)


def load_trace_report():
    if not TRACE_JSON_FILE.exists():
        print(f"FAILED: {TRACE_JSON_FILE} not found")
        return None

    try:
        return load_json_file(TRACE_JSON_FILE)
    except json.JSONDecodeError as error:
        print(f"FAILED: {TRACE_JSON_FILE} is not valid JSON: {error}")
        return None


def print_final_summary():
    report = load_trace_report()

    if report is None:
        return False

    print("")
    print("Final summary")
    print("-------------")

    if TRACE_MARKDOWN_FILE.exists():
        print("trace_report_v18.md generated")
    else:
        print("FAILED: trace_report_v18.md not found")
        return False

    network_requests_made = report.get("network_requests_made")
    validation_passed = report.get("validation_passed")

    print(f"network_requests_made: {network_requests_made}")

    if validation_passed is True:
        print("validation passed")
    else:
        print("FAILED: validation did not pass")
        return False

    print("Public trace pipeline complete.")
    return True


def main():
    print("Story Evidence Collector public trace pipeline v2.0")
    print("Running general source/link/report pipeline only.")
    print("The old quote-demo scraper is not run.")
    print("No new crawling or fetching logic is added by this runner.")

    if not run_step("extract_source_records_v13.py"):
        print("Pipeline stopped.")
        return 1

    sanitise_after_source_extraction()

    if not run_step("filter_link_queue_v14.py"):
        print("Pipeline stopped.")
        return 1

    sanitise_after_queue_filter()

    if not run_step("fetch_candidate_links_v15.py"):
        print("Pipeline stopped.")
        return 1

    sanitise_after_candidate_fetch()

    for script_name in [
        "follow_fetched_candidate_links_v16.py",
        "create_trace_report_v17.py",
        "create_trace_report_v18.py",
    ]:
        if not run_step(script_name):
            print("Pipeline stopped.")
            return 1

    if not print_final_summary():
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
