import json
from datetime import datetime, timezone
from pathlib import Path


INPUT_FILE = Path("mp_division_sources.json")
OUTPUT_JSON_FILE = Path("division_records_v11.json")
OUTPUT_REPORT_FILE = Path("division_records_report_v11.md")

REQUIRED_FIELDS = [
    "source_url",
    "date",
    "division_number",
    "motion_title",
    "topic",
    "aye_members",
    "no_members",
]

HUMAN_EFFECT_FIELDS = [
    "plain_aye_effect",
    "plain_no_effect",
]


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


def load_sources():
    data = load_json(INPUT_FILE)
    if not isinstance(data, dict):
        raise RuntimeError("mp_division_sources.json must contain an object.")
    sources = data.get("sources")
    if not isinstance(sources, list):
        raise RuntimeError("mp_division_sources.json must contain a sources list.")
    return data


def list_field(value):
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    return []


def validate_source(source):
    warnings = []
    if not isinstance(source, dict):
        return ["source_not_object"]

    for field in REQUIRED_FIELDS:
        value = source.get(field)
        if field in {"aye_members", "no_members"}:
            if not isinstance(value, list):
                warnings.append(f"missing_or_invalid_{field}")
        elif not clean_text(value):
            warnings.append(f"missing_{field}")

    for field in HUMAN_EFFECT_FIELDS:
        if not clean_text(source.get(field)):
            warnings.append("human_effect_needs_review")
            break

    return warnings


def source_status(warnings):
    if not warnings:
        return "ready"
    if "source_not_object" in warnings:
        return "skipped"
    if any(warning.startswith("missing_or_invalid_") or warning.startswith("missing_") for warning in warnings):
        return "incomplete"
    if "human_effect_needs_review" in warnings:
        return "needs_review"
    return "needs_review"


def normalise_source(source):
    return {
        "date": clean_text(source.get("date")),
        "division_number": clean_text(source.get("division_number")),
        "motion_title": clean_text(source.get("motion_title")),
        "plain_aye_effect": clean_text(source.get("plain_aye_effect")),
        "plain_no_effect": clean_text(source.get("plain_no_effect")),
        "topic": clean_text(source.get("topic")),
        "source_url": clean_text(source.get("source_url")),
        "aye_members": list_field(source.get("aye_members")),
        "no_members": list_field(source.get("no_members")),
    }


def build_outputs(source_data):
    records = []
    source_reports = []

    for index, source in enumerate(source_data.get("sources", []), start=1):
        warnings = validate_source(source)
        status = source_status(warnings)

        if status != "skipped" and isinstance(source, dict):
            records.append(normalise_source(source))

        source_reports.append({
            "index": index,
            "source_url": clean_text(source.get("source_url")) if isinstance(source, dict) else "",
            "division_number": clean_text(source.get("division_number")) if isinstance(source, dict) else "",
            "motion_title": clean_text(source.get("motion_title")) if isinstance(source, dict) else "",
            "status": status,
            "warnings": warnings,
        })

    ready_count = len([item for item in source_reports if item["status"] == "ready"])
    needs_review_count = len([item for item in source_reports if item["status"] == "needs_review"])
    incomplete_count = len([item for item in source_reports if item["status"] == "incomplete"])
    skipped_count = len([item for item in source_reports if item["status"] == "skipped"])

    report = {
        "generated_at": utc_now_iso(),
        "mp_name": clean_text(source_data.get("mp_name")),
        "member_id": clean_text(source_data.get("member_id")),
        "input_file": str(INPUT_FILE),
        "output_file": str(OUTPUT_JSON_FILE),
        "network_requests_made": False,
        "sources_checked": len(source_data.get("sources", [])),
        "records_written": len(records),
        "ready": ready_count,
        "needs_review": needs_review_count,
        "incomplete": incomplete_count,
        "skipped": skipped_count,
        "source_reports": source_reports,
    }

    return records, report


def build_markdown_report(report):
    lines = []
    lines.append("# MP Division Records Normalisation Report v1.1")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This local step normalises selected division source records into the MP voting-position input shape. It does not fetch pages, crawl, or infer vote meaning from titles alone.")
    lines.append("")
    lines.append("## MP checked")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["MP name", report["mp_name"]],
        ["Member ID", report["member_id"]],
    ]))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count"], [
        ["Sources checked", report["sources_checked"]],
        ["Records written", report["records_written"]],
        ["Ready", report["ready"]],
        ["Needs human-effect review", report["needs_review"]],
        ["Incomplete", report["incomplete"]],
        ["Skipped", report["skipped"]],
        ["Network requests made", report["network_requests_made"]],
    ]))
    lines.append("")
    lines.append("## Source results")
    lines.append("")
    lines.append(markdown_table(
        ["Index", "Division", "Motion title", "Status", "Warnings", "Source URL"],
        [
            [
                item["index"],
                item["division_number"],
                item["motion_title"],
                item["status"],
                ", ".join(item["warnings"]),
                item["source_url"],
            ]
            for item in report["source_reports"]
        ],
    ))
    lines.append("")
    lines.append("## What this report does not prove")
    lines.append("")
    lines.append("- It does not prove complete voting history.")
    lines.append("- It does not infer motive or private belief.")
    lines.append("- It does not infer the human meaning of Aye or No if plain-effect fields are missing.")
    lines.append("- It only normalises the selected records supplied in this run.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting MP division source normaliser v1.1")
    print("No network requests will be made.")
    try:
        source_data = load_sources()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    records, report = build_outputs(source_data)
    save_json(OUTPUT_JSON_FILE, records)
    save_text(OUTPUT_REPORT_FILE, build_markdown_report(report))

    print("Final summary")
    print("-------------")
    print(f"MP: {report['mp_name']}")
    print(f"Sources checked: {report['sources_checked']}")
    print(f"Records written: {report['records_written']}")
    print(f"Ready: {report['ready']}")
    print(f"Needs review: {report['needs_review']}")
    print(f"Incomplete: {report['incomplete']}")
    print(f"Network requests made: {report['network_requests_made']}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_REPORT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
