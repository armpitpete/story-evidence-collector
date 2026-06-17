import calendar
import json
from datetime import date, datetime, timezone
from pathlib import Path


INPUT_FILE = Path("parlparse_import_batch_plan_v19.json")
OUTPUT_JSON_FILE = Path("parlparse_import_batch_plan_report_v19.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_import_batch_plan_v19.md")


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


def parse_date(value):
    return datetime.strptime(clean_text(value), "%Y-%m-%d").date()


def month_end_date(year, month):
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


def next_month(current):
    if current.month == 12:
        return date(current.year + 1, 1, 1)
    return date(current.year, current.month + 1, 1)


def build_batches(plan):
    target = plan["total_target_range"]
    start = parse_date(target["start_date"])
    end = parse_date(target["end_date"])
    batches = []
    current = date(start.year, start.month, 1)

    while current <= end:
        batch_start = max(current, start)
        batch_end = min(month_end_date(current.year, current.month), end)
        batch_id = f"parlparse_{current.year}_{current.month:02d}"
        max_xml_files = min(plan["hard_limits_per_batch"]["max_xml_files"], (batch_end - batch_start).days + 1)
        batches.append({
            "batch_id": batch_id,
            "start_date": batch_start.isoformat(),
            "end_date": batch_end.isoformat(),
            "max_xml_files": max_xml_files,
            "rows_file": plan["output_rules"]["rows_filename_format"].format(batch_id=batch_id),
            "report_file": plan["output_rules"]["report_filename_format"].format(batch_id=batch_id),
            "manifest_file": plan["output_rules"]["manifest_filename_format"].format(batch_id=batch_id),
            "status": "planned",
        })
        current = next_month(current)

    return batches


def build_manifest_template(plan):
    return {
        "batch_id": "parlparse_YYYY_MM",
        "target_mp": plan.get("target_mp", ""),
        "target_member_id": plan.get("target_member_id", ""),
        "date_range": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "limits": plan.get("hard_limits_per_batch", {}),
        "source_files": {
            "generated": 0,
            "parsed": 0,
            "not_available": 0,
            "failed": 0
        },
        "rows": {
            "produced": 0,
            "recorded_aye": 0,
            "recorded_no": 0,
            "not_recorded": 0,
            "unable_to_determine": 0
        },
        "checks": {
            "missing_required_fields": 0,
            "duplicate_keys_found": 0,
            "safe_to_merge_later": False
        },
        "outputs": {
            "rows_file": "",
            "report_file": ""
        }
    }


def build_report(plan):
    batches = build_batches(plan)
    first_batch_id = plan["batch_model"].get("first_production_safe_batch", "")
    first_batch = next((batch for batch in batches if batch["batch_id"] == first_batch_id), batches[0] if batches else {})
    return {
        "generated_at": utc_now_iso(),
        "version": plan.get("version", "v1.9"),
        "purpose": plan.get("purpose", ""),
        "target_mp": plan.get("target_mp", ""),
        "target_member_id": plan.get("target_member_id", ""),
        "network_requests_made": False,
        "merge_now": False,
        "total_target_range": plan.get("total_target_range", {}),
        "batch_model": plan.get("batch_model", {}),
        "hard_limits_per_batch": plan.get("hard_limits_per_batch", {}),
        "output_rules": plan.get("output_rules", {}),
        "dedupe_rule": plan.get("dedupe_rule", {}),
        "traceability_fields_required": plan.get("traceability_fields_required", []),
        "future_merge_rules": plan.get("future_merge_rules", []),
        "not_in_scope": plan.get("not_in_scope", []),
        "batch_count": len(batches),
        "first_production_safe_batch": first_batch,
        "batches": batches,
        "manifest_template": build_manifest_template(plan),
        "next_action": "Run one named batch only, starting with the first production-safe batch. Do not run the whole range and do not merge yet."
    }


def build_markdown(report):
    lines = []
    target_range = report.get("total_target_range", {})
    first_batch = report.get("first_production_safe_batch", {})

    lines.append("# ParlParse Import Batch Plan v1.9")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(report.get("purpose", ""))
    lines.append("")
    lines.append("This is a plan only. It does not fetch files, import rows, merge data, or claim complete coverage.")
    lines.append("")
    lines.append("## Target")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Target MP", report.get("target_mp", "")],
        ["Target member ID", report.get("target_member_id", "")],
        ["Target range", f"{target_range.get('start_date', '')} to {target_range.get('end_date', '')}"],
        ["Batch model", report.get("batch_model", {}).get("unit", "")],
        ["Planned batches", report.get("batch_count", 0)],
        ["Network requests made", report.get("network_requests_made", False)],
        ["Merge now", report.get("merge_now", False)],
    ]))
    lines.append("")
    lines.append("## First production-safe batch")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Batch ID", first_batch.get("batch_id", "")],
        ["Start date", first_batch.get("start_date", "")],
        ["End date", first_batch.get("end_date", "")],
        ["Max XML files", first_batch.get("max_xml_files", "")],
        ["Rows file", first_batch.get("rows_file", "")],
        ["Report file", first_batch.get("report_file", "")],
        ["Manifest file", first_batch.get("manifest_file", "")],
    ]))
    lines.append("")
    lines.append("## Hard limits per batch")
    lines.append("")
    lines.append(markdown_table(["Limit", "Value"], report.get("hard_limits_per_batch", {}).items()))
    lines.append("")
    lines.append("## Output naming rules")
    lines.append("")
    lines.append(markdown_table(["Rule", "Value"], report.get("output_rules", {}).items()))
    lines.append("")
    lines.append("## Dedupe rule")
    lines.append("")
    dedupe = report.get("dedupe_rule", {})
    lines.append(markdown_table(["Field", "Value"], [
        ["Key fields", ", ".join(dedupe.get("key_fields", []))],
        ["Note", dedupe.get("note", "")],
    ]))
    lines.append("")
    lines.append("## Required traceability fields")
    lines.append("")
    for field in report.get("traceability_fields_required", []):
        lines.append(f"- `{field}`")
    lines.append("")
    lines.append("## Safe stop rules")
    lines.append("")
    limits = report.get("hard_limits_per_batch", {})
    lines.append(f"- Stop if failed files exceed `{limits.get('stop_if_failed_files_exceed')}`.")
    lines.append(f"- Stop if missing required fields: `{limits.get('stop_if_missing_required_fields')}`.")
    lines.append(f"- Stop if duplicate keys are found: `{limits.get('stop_if_duplicate_keys_found')}`.")
    lines.append(f"- Stop if rows exceed `{limits.get('max_rows')}`.")
    lines.append("")
    lines.append("## Planned batches")
    lines.append("")
    lines.append(markdown_table(
        ["Batch ID", "Start", "End", "Max XML", "Status"],
        [
            [
                batch.get("batch_id", ""),
                batch.get("start_date", ""),
                batch.get("end_date", ""),
                batch.get("max_xml_files", ""),
                batch.get("status", ""),
            ]
            for batch in report.get("batches", [])
        ],
    ))
    lines.append("")
    lines.append("## Future merge rules")
    lines.append("")
    for rule in report.get("future_merge_rules", []):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("## Not in scope")
    lines.append("")
    for item in report.get("not_in_scope", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Next action")
    lines.append("")
    lines.append(report.get("next_action", ""))
    return "\n".join(lines) + "\n"


def main():
    print("Planning safe ParlParse import batches v1.9")
    plan = load_json(INPUT_FILE)
    report = build_report(plan)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Target MP: {report['target_mp']}")
    print(f"Planned batches: {report['batch_count']}")
    print(f"First batch: {report['first_production_safe_batch'].get('batch_id')}")
    print(f"Network requests made: {report['network_requests_made']}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
