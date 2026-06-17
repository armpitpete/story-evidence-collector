import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import parse_parlparse_vote_rows_sample_v17 as sample_parser


INPUT_FILE = Path("parlparse_date_range_query_v18.json")
OUTPUT_JSON_FILE = Path("parlparse_date_range_rows_v18.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_date_range_rows_v18.md")

USER_AGENT = "StoryEvidenceCollector/ParlParseDateRange/1.8"
REQUEST_TIMEOUT_SECONDS = 30


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_text(path, text):
    with path.open("w", encoding="utf-8") as file:
        file.write(text)


def clean_text(value):
    if value is None:
        return ""
    if value is True:
        return "True"
    if value is False:
        return "False"
    return " ".join(str(value).split())


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [clean_text(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def parse_iso_date(value, field_name):
    try:
        return datetime.strptime(clean_text(value), "%Y-%m-%d").date()
    except ValueError as error:
        raise RuntimeError(f"{field_name} must be YYYY-MM-DD.") from error


def generate_date_urls(config):
    start_date = parse_iso_date(config.get("start_date"), "start_date")
    end_date = parse_iso_date(config.get("end_date"), "end_date")
    if end_date < start_date:
        raise RuntimeError("end_date must be on or after start_date.")

    max_xml_files = int(config.get("max_xml_files", 31))
    pattern = clean_text(config.get("base_url_pattern"))
    if "{date}" not in pattern:
        raise RuntimeError("base_url_pattern must contain {date}.")

    urls = []
    current = start_date
    while current <= end_date and len(urls) < max_xml_files:
        date_text = current.isoformat()
        urls.append({
            "date": date_text,
            "xml_url": pattern.replace("{date}", date_text),
        })
        current += timedelta(days=1)

    return urls


def fetch_text(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="replace")


def fetch_and_parse_url(entry, config, index):
    xml_url = entry["xml_url"]
    try:
        xml_text = fetch_text(xml_url)
    except HTTPError as error:
        if error.code == 404:
            return [], {
                "index": index,
                "date": entry["date"],
                "xml_url": xml_url,
                "status": "not_available",
                "rows_produced": 0,
                "division_elements_found": 0,
                "error": "404 not found",
            }
        return [], {
            "index": index,
            "date": entry["date"],
            "xml_url": xml_url,
            "status": "failed",
            "rows_produced": 0,
            "division_elements_found": 0,
            "error": str(error),
        }
    except (URLError, TimeoutError, UnicodeDecodeError) as error:
        return [], {
            "index": index,
            "date": entry["date"],
            "xml_url": xml_url,
            "status": "failed",
            "rows_produced": 0,
            "division_elements_found": 0,
            "error": str(error),
        }

    rows, event = sample_parser.parse_xml_file(xml_url, xml_text, config)
    event["index"] = index
    event["date"] = entry["date"]
    event["xml_url"] = xml_url
    event["status"] = "parsed" if event.get("status") == "ok" else event.get("status", "parsed")
    return rows, event


def run_date_range(config):
    if not bool(config.get("allow_network_probe", False)):
        return [], [{"status": "network_disabled"}], []

    date_urls = generate_date_urls(config)
    all_rows = []
    source_events = []

    for index, entry in enumerate(date_urls, start=1):
        rows, event = fetch_and_parse_url(entry, config, index)
        all_rows.extend(rows)
        source_events.append(event)

    return all_rows, source_events, date_urls


def field_missing_counts(rows):
    fields = [
        "date",
        "division_id",
        "division_number",
        "motion_title",
        "recorded_side",
        "source_url",
        "source_system",
        "evidence_status",
    ]
    return {field: len([row for row in rows if not clean_text(row.get(field))]) for field in fields}


def build_report(config, rows, source_events, date_urls):
    side_counts = Counter(row.get("recorded_side", "") for row in rows)
    event_counts = Counter(event.get("status", "") for event in source_events)
    evidence_counts = Counter(row.get("evidence_status", "") for row in rows)

    parsed_events = [event for event in source_events if event.get("status") == "parsed"]
    dates_with_rows = sorted({row.get("date") for row in rows if clean_text(row.get("date"))})

    return {
        "generated_at": utc_now_iso(),
        "purpose": config.get("purpose", ""),
        "target_mp": config.get("target_mp", ""),
        "target_member_id": config.get("target_member_id", ""),
        "start_date": config.get("start_date", ""),
        "end_date": config.get("end_date", ""),
        "max_xml_files": int(config.get("max_xml_files", 31)),
        "network_requests_made": bool(source_events),
        "xml_files_generated": len(date_urls),
        "xml_files_parsed": len(parsed_events),
        "xml_files_not_available": event_counts.get("not_available", 0),
        "xml_files_failed": event_counts.get("failed", 0),
        "rows_produced": len(rows),
        "dates_with_rows": dates_with_rows,
        "recorded_aye": side_counts.get("Aye", 0),
        "recorded_no": side_counts.get("No", 0),
        "not_recorded": side_counts.get("Not recorded", 0),
        "unable_to_determine": side_counts.get("Unable to determine", 0),
        "source_event_counts": dict(event_counts),
        "evidence_status_counts": dict(evidence_counts),
        "field_missing_counts": field_missing_counts(rows),
        "source_events": source_events,
        "rows": rows,
        "merge_now": False,
        "coverage_note": "This is a bounded ParlParse date-range sample. It does not claim full 2001-2016 coverage and does not merge with the main MP vote index.",
        "scaling_assessment": scaling_assessment(rows, source_events, config),
    }


def scaling_assessment(rows, source_events, config):
    parsed_count = len([event for event in source_events if event.get("status") == "parsed"])
    failed_count = len([event for event in source_events if event.get("status") == "failed"])
    if failed_count:
        return "Partial. The approach parsed some files, but failed requests must be handled before scaling."
    if parsed_count and rows:
        return "Promising. The date-range approach produced standard vote rows and can be widened later with explicit hard limits."
    if parsed_count and not rows:
        return "Technically works, but this date range produced no vote rows; choose a range with known divisions before scaling."
    return "Not proven. No XML files were parsed in this run."


def build_markdown(report):
    lines = []
    lines.append(f"# ParlParse Date Range Rows v1.8 — {report.get('target_mp', '')}")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(report.get("coverage_note", ""))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count / value"], [
        ["Target MP", report.get("target_mp", "")],
        ["Target member ID", report.get("target_member_id", "")],
        ["Date range", f"{report.get('start_date', '')} to {report.get('end_date', '')}"],
        ["Max XML files", report.get("max_xml_files", 0)],
        ["XML files generated", report.get("xml_files_generated", 0)],
        ["XML files parsed", report.get("xml_files_parsed", 0)],
        ["XML files not available", report.get("xml_files_not_available", 0)],
        ["XML files failed", report.get("xml_files_failed", 0)],
        ["Rows produced", report.get("rows_produced", 0)],
        ["Recorded Aye", report.get("recorded_aye", 0)],
        ["Recorded No", report.get("recorded_no", 0)],
        ["Not recorded", report.get("not_recorded", 0)],
        ["Unable to determine", report.get("unable_to_determine", 0)],
        ["Merge now", report.get("merge_now", False)],
        ["Network requests made", report.get("network_requests_made", False)],
    ]))
    lines.append("")
    lines.append("## Scaling assessment")
    lines.append("")
    lines.append(report.get("scaling_assessment", ""))
    lines.append("")
    lines.append("## Dates with rows")
    lines.append("")
    if report.get("dates_with_rows"):
        for date_text in report.get("dates_with_rows", []):
            lines.append(f"- {date_text}")
    else:
        lines.append("No dates produced vote rows in this bounded run.")
    lines.append("")
    lines.append("## Source file events")
    lines.append("")
    lines.append(markdown_table(
        ["Index", "Date", "Status", "Divisions", "Rows", "XML URL", "Error"],
        [
            [
                event.get("index", ""),
                event.get("date", ""),
                event.get("status", ""),
                event.get("division_elements_found", 0),
                event.get("rows_produced", 0),
                event.get("xml_url", ""),
                event.get("error", ""),
            ]
            for event in report.get("source_events", [])
        ],
    ))
    lines.append("")
    lines.append("## Evidence status counts")
    lines.append("")
    lines.append(markdown_table(["Evidence status", "Rows"], report.get("evidence_status_counts", {}).items()))
    lines.append("")
    lines.append("## Missing field counts")
    lines.append("")
    lines.append(markdown_table(["Field", "Rows missing value"], report.get("field_missing_counts", {}).items()))
    lines.append("")
    lines.append("## Vote rows")
    lines.append("")
    lines.append(markdown_table(
        ["Date", "Division ID", "Division no.", "Motion title", "Recorded side", "Source URL", "Evidence status"],
        [
            [
                row.get("date", ""),
                row.get("division_id", ""),
                row.get("division_number", ""),
                row.get("motion_title", ""),
                row.get("recorded_side", ""),
                row.get("source_url", ""),
                row.get("evidence_status", ""),
            ]
            for row in report.get("rows", [])
        ],
    ))
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge rows into the main MP vote index.")
    lines.append("- It does not claim full 2001-2016 coverage.")
    lines.append("- It does not publish raw XML extracts.")
    lines.append("- It does not infer human political meaning from vote titles.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting bounded ParlParse date range parser v1.8")
    try:
        config = load_json(INPUT_FILE)
        rows, source_events, date_urls = run_date_range(config)
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    report = build_report(config, rows, source_events, date_urls)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))

    print("Final summary")
    print("-------------")
    print(f"Date range: {report['start_date']} to {report['end_date']}")
    print(f"XML files generated: {report['xml_files_generated']}")
    print(f"XML files parsed: {report['xml_files_parsed']}")
    print(f"Rows produced: {report['rows_produced']}")
    print(f"Recorded Aye: {report['recorded_aye']}")
    print(f"Recorded No: {report['recorded_no']}")
    print(f"Not recorded: {report['not_recorded']}")
    print(f"Unable to determine: {report['unable_to_determine']}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
