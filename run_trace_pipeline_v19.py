import json
import subprocess
import sys
from pathlib import Path


PIPELINE_STEPS = [
    "scrape_all_quote_pages_v11.py",
    "extract_source_records_v12.py",
    "extract_source_records_v13.py",
    "filter_link_queue_v14.py",
    "fetch_candidate_links_v15.py",
    "follow_fetched_candidate_links_v16.py",
    "create_trace_report_v17.py",
    "create_trace_report_v18.py",
]

TRACE_JSON_FILE = Path("trace_report_v18.json")
TRACE_MARKDOWN_FILE = Path("trace_report_v18.md")


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


def load_trace_report():
    if not TRACE_JSON_FILE.exists():
        print(f"FAILED: {TRACE_JSON_FILE} not found")
        return None

    try:
        with TRACE_JSON_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
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

    print("Pipeline complete.")
    return True


def main():
    print("Story Evidence Collector pipeline v1.9")
    print("Running existing safe pipeline only.")
    print("No new crawling or fetching logic is added by this runner.")

    for script_name in PIPELINE_STEPS:
        if not run_step(script_name):
            print("")
            print("Pipeline stopped.")
            return 1

    if not print_final_summary():
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
