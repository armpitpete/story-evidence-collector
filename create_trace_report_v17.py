from urllib.parse import urlparse, urlunparse, urldefrag
import json
import os
from datetime import datetime, timezone


INPUT_FILES = [
    {
        "filename": "seed_urls.json",
        "stage": "v1.1 seed URLs",
        "required": True,
    },
    {
        "filename": "sources_raw_v13.json",
        "stage": "v1.3 source records",
        "required": False,
    },
    {
        "filename": "link_queue_v13.json",
        "stage": "v1.3 pending link queue",
        "required": False,
    },
    {
        "filename": "link_queue_filtered_v14.json",
        "stage": "v1.4 filtered link queue",
        "required": False,
    },
    {
        "filename": "candidate_sources_raw_v15.json",
        "stage": "v1.5 fetched candidate sources",
        "required": False,
    },
    {
        "filename": "candidate_fetch_report_v15.json",
        "stage": "v1.5 candidate fetch report",
        "required": False,
    },
    {
        "filename": "followed_sources_raw_v16.json",
        "stage": "v1.6 followed source records",
        "required": False,
    },
    {
        "filename": "followed_fetch_report_v16.json",
        "stage": "v1.6 followed fetch report",
        "required": False,
    },
]

TRACE_JSON_OUTPUT_FILE = "trace_report_v17.json"
TRACE_MARKDOWN_OUTPUT_FILE = "trace_report_v17.md"


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value):
    if value is None:
        return ""

    return " ".join(str(value).split())


def load_json_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        item_count = len(data) if isinstance(data, list) else 1

        return data, {
            "filename": filename,
            "loaded": True,
            "status": "loaded",
            "item_count": item_count,
            "error": None,
        }

    except FileNotFoundError:
        return None, {
            "filename": filename,
            "loaded": False,
            "status": "missing",
            "item_count": 0,
            "error": None,
        }

    except json.JSONDecodeError as error:
        return None, {
            "filename": filename,
            "loaded": False,
            "status": "invalid_json",
            "item_count": 0,
            "error": str(error),
        }


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_text(filename, text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)


def normalize_url(raw_url):
    cleaned_url = clean_text(raw_url)

    if not cleaned_url:
        return None

    cleaned_url, _fragment = urldefrag(cleaned_url)
    parsed_url = urlparse(cleaned_url)

    if parsed_url.scheme.lower() not in {"http", "https"} or not parsed_url.netloc:
        return None

    path = parsed_url.path or "/"

    return urlunparse((
        parsed_url.scheme.lower(),
        parsed_url.netloc.lower(),
        path,
        parsed_url.params,
        parsed_url.query,
        "",
    ))


def build_url_key(raw_url):
    normalized_url = normalize_url(raw_url)

    if not normalized_url:
        return None

    parsed_url = urlparse(normalized_url)

    # Scheme is deliberately excluded so http://example/path and
    # https://example/path are treated as one traceable page.
    return urlunparse((
        "",
        parsed_url.netloc.lower(),
        parsed_url.path or "/",
        parsed_url.params,
        parsed_url.query,
        "",
    ))


def unique_preserve_order(values):
    seen = set()
    unique_values = []

    for value in values:
        if value is None or value == "":
            continue

        if value in seen:
            continue

        seen.add(value)
        unique_values.append(value)

    return unique_values


def count_by_key(items, key_name):
    counts = {}

    for item in items:
        value = item.get(key_name, "unknown")
        counts[value] = counts.get(value, 0) + 1

    return counts


def first_non_empty(values):
    for value in values:
        if value is not None and value != "":
            return value

    return None


def create_empty_trace(url):
    normalized_url = normalize_url(url)

    return {
        "url": normalized_url or url,
        "url_key": build_url_key(url),
        "first_seen_stage": None,
        "first_seen_file": None,
        "stages": [],
        "found_on": [],
        "depths": [],
        "statuses": [],
        "filter_statuses": [],
        "filter_reasons": [],
        "skip_reasons": [],
        "scrape_statuses": [],
        "robots_txt_statuses": [],
        "page_titles": [],
        "final_urls": [],
        "fetched": False,
        "skipped": False,
        "current_status": "unknown",
    }


def ensure_trace(traces, url, stage, filename):
    url_key = build_url_key(url)

    if not url_key:
        return None

    if url_key not in traces:
        traces[url_key] = create_empty_trace(url)

    trace = traces[url_key]

    if not trace["first_seen_stage"]:
        trace["first_seen_stage"] = stage
        trace["first_seen_file"] = filename

    if stage not in trace["stages"]:
        trace["stages"].append(stage)

    return trace


def append_if_present(trace, field_name, value):
    if trace is None:
        return

    if value is None or value == "":
        return

    trace[field_name].append(value)


def add_status(trace, status):
    append_if_present(trace, "statuses", status)


def add_queue_item_trace(traces, item, stage, filename):
    if not isinstance(item, dict):
        return

    trace = ensure_trace(traces, item.get("url"), stage, filename)

    if trace is None:
        return

    append_if_present(trace, "found_on", item.get("found_on"))
    append_if_present(trace, "depths", item.get("depth"))
    add_status(trace, item.get("status"))

    if item.get("filter_status"):
        append_if_present(trace, "filter_statuses", item.get("filter_status"))
        add_status(trace, f"filter_{item.get('filter_status')}")

    if item.get("filter_reason"):
        append_if_present(trace, "filter_reasons", item.get("filter_reason"))

    if item.get("skip_reason"):
        append_if_present(trace, "skip_reasons", item.get("skip_reason"))
        trace["skipped"] = True
        add_status(trace, f"skipped_{item.get('skip_reason')}")


def add_source_record_trace(traces, record, stage, filename):
    if not isinstance(record, dict):
        return

    trace = ensure_trace(traces, record.get("source_url"), stage, filename)

    if trace is None:
        return

    trace["fetched"] = record.get("scrape_status") == "ok"
    append_if_present(trace, "found_on", record.get("found_on"))
    append_if_present(trace, "depths", record.get("depth"))
    append_if_present(trace, "scrape_statuses", record.get("scrape_status"))
    append_if_present(trace, "robots_txt_statuses", record.get("robots_txt_status"))
    append_if_present(trace, "page_titles", record.get("page_title"))
    append_if_present(trace, "final_urls", record.get("final_url"))
    add_status(trace, record.get("scrape_status"))

    if record.get("scrape_status") == "blocked_by_robots_txt":
        trace["skipped"] = True
        append_if_present(trace, "skip_reasons", "blocked_by_robots_txt")

    if record.get("scrape_status") == "error":
        append_if_present(trace, "skip_reasons", "fetch_error")

    final_url = record.get("final_url")

    if final_url and final_url != record.get("source_url"):
        final_trace = ensure_trace(traces, final_url, stage, filename)

        if final_trace is not None:
            final_trace["fetched"] = trace["fetched"]
            append_if_present(final_trace, "scrape_statuses", record.get("scrape_status"))
            append_if_present(final_trace, "robots_txt_statuses", record.get("robots_txt_status"))
            append_if_present(final_trace, "page_titles", record.get("page_title"))
            append_if_present(final_trace, "final_urls", final_url)
            add_status(final_trace, record.get("scrape_status"))


def add_fetch_report_trace(traces, report, stage, filename):
    if not isinstance(report, dict):
        return

    for url in report.get("fetched_urls", []):
        trace = ensure_trace(traces, url, stage, filename)

        if trace is not None:
            trace["fetched"] = True
            add_status(trace, "fetched")

    for url in report.get("robots_blocked_urls", []):
        trace = ensure_trace(traces, url, stage, filename)

        if trace is not None:
            trace["skipped"] = True
            append_if_present(trace, "skip_reasons", "blocked_by_robots_txt")
            add_status(trace, "blocked_by_robots_txt")

    for url in report.get("failed_urls", []):
        trace = ensure_trace(traces, url, stage, filename)

        if trace is not None:
            append_if_present(trace, "skip_reasons", "fetch_error")
            add_status(trace, "fetch_error")

    for item in report.get("skipped_urls", []):
        if not isinstance(item, dict):
            continue

        trace = ensure_trace(traces, item.get("url"), stage, filename)

        if trace is None:
            continue

        trace["skipped"] = True
        append_if_present(trace, "found_on", item.get("found_on"))
        append_if_present(trace, "skip_reasons", item.get("skip_reason"))
        add_status(trace, f"skipped_{item.get('skip_reason')}")


def process_seed_urls(traces, data, stage, filename):
    if not isinstance(data, dict):
        return

    seed_urls = data.get("seed_urls", [])

    if not isinstance(seed_urls, list):
        return

    for url in seed_urls:
        trace = ensure_trace(traces, url, stage, filename)

        if trace is not None:
            add_status(trace, "seed")


def process_file(traces, filename, stage, data):
    if filename == "seed_urls.json":
        process_seed_urls(traces, data, stage, filename)
        return

    if filename in {
        "sources_raw_v13.json",
        "candidate_sources_raw_v15.json",
        "followed_sources_raw_v16.json",
    }:
        if isinstance(data, list):
            for record in data:
                add_source_record_trace(traces, record, stage, filename)
        return

    if filename in {
        "link_queue_v13.json",
        "link_queue_filtered_v14.json",
    }:
        if isinstance(data, list):
            for item in data:
                add_queue_item_trace(traces, item, stage, filename)
        return

    if filename in {
        "candidate_fetch_report_v15.json",
        "followed_fetch_report_v16.json",
    }:
        add_fetch_report_trace(traces, data, stage, filename)
        return


def finalize_trace_records(traces):
    trace_records = []

    for trace in traces.values():
        trace["found_on"] = unique_preserve_order(trace["found_on"])
        trace["depths"] = unique_preserve_order(trace["depths"])
        trace["statuses"] = unique_preserve_order(trace["statuses"])
        trace["filter_statuses"] = unique_preserve_order(trace["filter_statuses"])
        trace["filter_reasons"] = unique_preserve_order(trace["filter_reasons"])
        trace["skip_reasons"] = unique_preserve_order(trace["skip_reasons"])
        trace["scrape_statuses"] = unique_preserve_order(trace["scrape_statuses"])
        trace["robots_txt_statuses"] = unique_preserve_order(trace["robots_txt_statuses"])
        trace["page_titles"] = unique_preserve_order(trace["page_titles"])
        trace["final_urls"] = unique_preserve_order(trace["final_urls"])

        if trace["fetched"]:
            trace["current_status"] = "fetched"
        elif trace["skipped"]:
            trace["current_status"] = "skipped"
        elif "filter_candidate" in trace["statuses"]:
            trace["current_status"] = "candidate"
        elif "pending" in trace["statuses"]:
            trace["current_status"] = "pending"
        elif "seed" in trace["statuses"]:
            trace["current_status"] = "seed"
        else:
            trace["current_status"] = "seen"

        trace_records.append(trace)

    return sorted(trace_records, key=lambda item: item["url"])


def build_stage_counts(loaded_files):
    stage_counts = {}

    for file_report in loaded_files:
        stage = file_report["stage"]
        stage_counts[stage] = {
            "filename": file_report["filename"],
            "loaded": file_report["loaded"],
            "item_count": file_report["item_count"],
            "status": file_report["status"],
        }

    return stage_counts


def count_skip_reasons(trace_records):
    counts = {}

    for record in trace_records:
        for reason in record.get("skip_reasons", []):
            counts[reason] = counts.get(reason, 0) + 1

    return counts


def build_summary_counts(trace_records):
    return {
        "unique_urls_traced": len(trace_records),
        "fetched_urls": len([item for item in trace_records if item["fetched"]]),
        "skipped_urls": len([item for item in trace_records if item["skipped"]]),
        "candidate_urls": len([
            item for item in trace_records
            if item["current_status"] == "candidate"
        ]),
        "pending_urls": len([
            item for item in trace_records
            if item["current_status"] == "pending"
        ]),
        "seed_urls": len([
            item for item in trace_records
            if item["current_status"] == "seed"
        ]),
        "skip_reason_counts": count_skip_reasons(trace_records),
        "current_status_counts": count_by_key(trace_records, "current_status"),
    }


def build_fetched_records(trace_records):
    return [
        {
            "url": record["url"],
            "final_url": first_non_empty(record["final_urls"]),
            "page_title": first_non_empty(record["page_titles"]),
            "scrape_status": first_non_empty(record["scrape_statuses"]),
            "robots_txt_status": first_non_empty(record["robots_txt_statuses"]),
            "found_on": record["found_on"],
            "depths": record["depths"],
            "stages": record["stages"],
        }
        for record in trace_records
        if record["fetched"]
    ]


def build_skipped_records(trace_records):
    return [
        {
            "url": record["url"],
            "skip_reasons": record["skip_reasons"],
            "found_on": record["found_on"],
            "depths": record["depths"],
            "stages": record["stages"],
        }
        for record in trace_records
        if record["skipped"]
    ]


def format_markdown_table(headers, rows):
    if not rows:
        return "_None._\n"

    output = []
    output.append("| " + " | ".join(headers) + " |")
    output.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        cleaned_cells = [
            clean_text(cell).replace("|", "\\|")
            for cell in row
        ]
        output.append("| " + " | ".join(cleaned_cells) + " |")

    return "\n".join(output) + "\n"


def build_trace_chain(record):
    chain = []

    if record.get("found_on"):
        for parent in record["found_on"]:
            chain.append(f"{parent} → {record['url']}")

    if not chain:
        chain.append(record["url"])

    return "; ".join(chain)


def build_markdown_report(report):
    lines = []

    lines.append("# Story Evidence Collector Trace Report v1.7")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Summary counts")
    lines.append("")
    lines.append(format_markdown_table(
        ["Metric", "Count"],
        [
            ["Unique URLs traced", report["summary_counts"]["unique_urls_traced"]],
            ["Fetched URLs", report["summary_counts"]["fetched_urls"]],
            ["Skipped URLs", report["summary_counts"]["skipped_urls"]],
            ["Candidate URLs", report["summary_counts"]["candidate_urls"]],
            ["Pending URLs", report["summary_counts"]["pending_urls"]],
            ["Seed URLs", report["summary_counts"]["seed_urls"]],
        ]
    ))
    lines.append("")
    lines.append("## Pipeline stage summary")
    lines.append("")
    lines.append(format_markdown_table(
        ["Stage", "File", "Loaded", "Items", "Status"],
        [
            [
                stage,
                details["filename"],
                details["loaded"],
                details["item_count"],
                details["status"],
            ]
            for stage, details in report["stage_counts"].items()
        ]
    ))
    lines.append("")
    lines.append("## Fetched source table")
    lines.append("")
    lines.append(format_markdown_table(
        ["URL", "Final URL", "Title", "Robots", "Found on"],
        [
            [
                record["url"],
                record.get("final_url") or "",
                record.get("page_title") or "",
                record.get("robots_txt_status") or "",
                ", ".join(record.get("found_on") or []),
            ]
            for record in report["fetched_records"]
        ]
    ))
    lines.append("")
    lines.append("## Skipped URL table")
    lines.append("")
    lines.append(format_markdown_table(
        ["URL", "Skip reason", "Found on"],
        [
            [
                record["url"],
                ", ".join(record.get("skip_reasons") or []),
                ", ".join(record.get("found_on") or []),
            ]
            for record in report["skipped_records"]
        ]
    ))
    lines.append("")
    lines.append("## Trace chains")
    lines.append("")
    lines.append(format_markdown_table(
        ["URL", "Current status", "Stages", "Trace"],
        [
            [
                record["url"],
                record["current_status"],
                " → ".join(record.get("stages") or []),
                build_trace_chain(record),
            ]
            for record in report["url_trace_records"]
        ]
    ))
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    lines.append(format_markdown_table(
        ["Check", "Result"],
        [
            ["Validation passed", report["validation_passed"]],
            ["Network requests made", report["network_requests_made"]],
            ["Warnings", "; ".join(report["validation_warnings"]) or "None"],
        ]
    ))

    return "\n".join(lines) + "\n"


def validate_report(loaded_files, trace_records):
    warnings = []

    for file_report in loaded_files:
        if file_report["required"] and not file_report["loaded"]:
            warnings.append(f"Required input missing: {file_report['filename']}")

        if file_report["status"] == "invalid_json":
            warnings.append(f"Invalid JSON input: {file_report['filename']}")

    if len(trace_records) == 0:
        warnings.append("No URL trace records were created.")

    fetched_records = [record for record in trace_records if record["fetched"]]
    skipped_records = [record for record in trace_records if record["skipped"]]

    if len(fetched_records) == 0:
        warnings.append("No fetched records were found in existing inputs.")

    if len(skipped_records) == 0:
        warnings.append("No skipped records were found in existing inputs.")

    return warnings


def main():
    print("Starting trace report build v1.7")
    print("No network requests will be made.")
    print("")

    loaded_files = []
    traces = {}

    for file_config in INPUT_FILES:
        filename = file_config["filename"]
        stage = file_config["stage"]

        data, load_report = load_json_file(filename)
        load_report["stage"] = stage
        load_report["required"] = file_config["required"]
        loaded_files.append(load_report)

        print(f"{filename}: {load_report['status']}")

        if load_report["loaded"]:
            process_file(traces, filename, stage, data)

    trace_records = finalize_trace_records(traces)
    validation_warnings = validate_report(loaded_files, trace_records)
    validation_passed = len(validation_warnings) == 0

    report = {
        "generated_at": utc_now_iso(),
        "network_requests_made": False,
        "input_files": loaded_files,
        "summary_counts": build_summary_counts(trace_records),
        "stage_counts": build_stage_counts(loaded_files),
        "url_trace_records": trace_records,
        "fetched_records": build_fetched_records(trace_records),
        "skipped_records": build_skipped_records(trace_records),
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
    }

    markdown_report = build_markdown_report(report)

    save_json(TRACE_JSON_OUTPUT_FILE, report)
    save_text(TRACE_MARKDOWN_OUTPUT_FILE, markdown_report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Unique URLs traced: {report['summary_counts']['unique_urls_traced']}")
    print(f"Fetched URLs: {report['summary_counts']['fetched_urls']}")
    print(f"Skipped URLs: {report['summary_counts']['skipped_urls']}")
    print(f"Trace JSON file: {TRACE_JSON_OUTPUT_FILE}")
    print(f"Trace Markdown file: {TRACE_MARKDOWN_OUTPUT_FILE}")
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
