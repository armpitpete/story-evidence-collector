import json
from collections import Counter
from pathlib import Path

import parse_parlparse_date_range_v18 as date_range_parser
import plan_parlparse_import_batches_v19 as batch_planner


PLAN_FILE = Path("parlparse_import_batch_plan_v19.json")
BATCH_ID = "parlparse_2003_01"
BATCH_FOLDER = Path("parlparse_batches")


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
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


def find_batch(plan_report, batch_id):
    for batch in plan_report.get("batches", []):
        if batch.get("batch_id") == batch_id:
            return batch
    raise RuntimeError(f"Batch not found in plan: {batch_id}")


def build_batch_config(plan, batch):
    return {
        "source_id": "parlparse_single_batch",
        "purpose": f"Run one production-safe ParlParse batch: {batch['batch_id']}",
        "target_mp": plan.get("target_mp", ""),
        "target_member_id": plan.get("target_member_id", ""),
        "start_date": batch["start_date"],
        "end_date": batch["end_date"],
        "max_xml_files": batch["max_xml_files"],
        "allow_network_probe": True,
        "base_url_pattern": plan.get("batch_model", {}).get("base_url_pattern", ""),
        "source_system": "parlparse",
        "meaning_quality": "needs_review",
        "topic": "uncategorised",
    }


def required_field_missing_count(rows, required_fields):
    return sum(
        1
        for row in rows
        for field in required_fields
        if not clean_text(row.get(field))
    )


def duplicate_keys(rows, key_fields, target_mp):
    seen = set()
    duplicates = []
    for row in rows:
        values = []
        for field in key_fields:
            if field == "target_mp":
                values.append(target_mp)
            else:
                values.append(clean_text(row.get(field)))
        key = tuple(values)
        if key in seen:
            duplicates.append(" | ".join(values))
        else:
            seen.add(key)
    return duplicates


def count_status(source_events, status):
    return len([event for event in source_events if event.get("status") == status])


def build_manifest(plan, batch, rows, date_range_report):
    limits = plan.get("hard_limits_per_batch", {})
    required_fields = plan.get("traceability_fields_required", [])
    key_fields = plan.get("dedupe_rule", {}).get("key_fields", [])
    side_counts = Counter(row.get("recorded_side", "") for row in rows)
    duplicate_key_values = duplicate_keys(rows, key_fields, plan.get("target_mp", ""))
    missing_required_fields = required_field_missing_count(rows, required_fields)
    failed_files = date_range_report.get("xml_files_failed", 0)
    rows_produced = len(rows)

    hard_stop_reasons = []
    if failed_files > int(limits.get("stop_if_failed_files_exceed", 5)):
        hard_stop_reasons.append("failed_file_limit_exceeded")
    if limits.get("stop_if_missing_required_fields") and missing_required_fields > 0:
        hard_stop_reasons.append("missing_required_fields")
    if limits.get("stop_if_duplicate_keys_found") and duplicate_key_values:
        hard_stop_reasons.append("duplicate_keys_found")
    if rows_produced > int(limits.get("max_rows", 500)):
        hard_stop_reasons.append("row_limit_exceeded")

    safe_to_merge_later = not hard_stop_reasons and rows_produced > 0

    return {
        "batch_id": batch["batch_id"],
        "target_mp": plan.get("target_mp", ""),
        "target_member_id": plan.get("target_member_id", ""),
        "date_range": {
            "start_date": batch["start_date"],
            "end_date": batch["end_date"],
        },
        "limits": limits,
        "source_files": {
            "generated": date_range_report.get("xml_files_generated", 0),
            "parsed": date_range_report.get("xml_files_parsed", 0),
            "not_available": date_range_report.get("xml_files_not_available", 0),
            "failed": failed_files,
        },
        "rows": {
            "produced": rows_produced,
            "recorded_aye": side_counts.get("Aye", 0),
            "recorded_no": side_counts.get("No", 0),
            "not_recorded": side_counts.get("Not recorded", 0),
            "unable_to_determine": side_counts.get("Unable to determine", 0),
        },
        "checks": {
            "missing_required_fields": missing_required_fields,
            "duplicate_keys_found": len(duplicate_key_values),
            "duplicate_keys": duplicate_key_values,
            "hard_stop_reasons": hard_stop_reasons,
            "safe_to_merge_later": safe_to_merge_later,
        },
        "outputs": {
            "manifest_file": batch["manifest_file"],
            "rows_file": batch["rows_file"],
            "report_file": batch["report_file"],
        },
        "merge_now": False,
        "coverage_note": "This is one production-safe ParlParse batch only. It is not merged into the main MP vote index and does not claim complete 2001-2016 coverage.",
    }


def build_batch_report(manifest, date_range_report):
    checks = manifest.get("checks", {})
    source_files = manifest.get("source_files", {})
    rows = manifest.get("rows", {})
    lines = []
    lines.append(f"# ParlParse Batch Report — {manifest.get('batch_id', '')}")
    lines.append("")
    lines.append(manifest.get("coverage_note", ""))
    lines.append("")
    lines.append("## Batch summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count / value"], [
        ["Target MP", manifest.get("target_mp", "")],
        ["Target member ID", manifest.get("target_member_id", "")],
        ["Date range", f"{manifest['date_range']['start_date']} to {manifest['date_range']['end_date']}"],
        ["Generated XML files", source_files.get("generated", 0)],
        ["Parsed XML files", source_files.get("parsed", 0)],
        ["Not available XML files", source_files.get("not_available", 0)],
        ["Failed XML files", source_files.get("failed", 0)],
        ["Rows produced", rows.get("produced", 0)],
        ["Recorded Aye", rows.get("recorded_aye", 0)],
        ["Recorded No", rows.get("recorded_no", 0)],
        ["Not recorded", rows.get("not_recorded", 0)],
        ["Unable to determine", rows.get("unable_to_determine", 0)],
        ["Missing required fields", checks.get("missing_required_fields", 0)],
        ["Duplicate keys found", checks.get("duplicate_keys_found", 0)],
        ["Safe to merge later", checks.get("safe_to_merge_later", False)],
        ["Merge now", manifest.get("merge_now", False)],
    ]))
    lines.append("")
    lines.append("## Hard stop result")
    lines.append("")
    if checks.get("hard_stop_reasons"):
        for reason in checks.get("hard_stop_reasons", []):
            lines.append(f"- `{reason}`")
    else:
        lines.append("No hard stop rule was triggered.")
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
            for event in date_range_report.get("source_events", [])
        ],
    ))
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge rows into the main MP vote index.")
    lines.append("- It does not run all ParlParse batches.")
    lines.append("- It does not publish raw XML extracts.")
    lines.append("- It does not infer human political meaning from votes.")
    lines.append("- It does not claim complete 2001-2016 coverage.")
    return "\n".join(lines) + "\n"


def main():
    print("Running production-safe ParlParse batch v2.0")
    plan = load_json(PLAN_FILE)
    plan_report = batch_planner.build_report(plan)
    batch = find_batch(plan_report, BATCH_ID)
    config = build_batch_config(plan, batch)

    rows, source_events, date_urls = date_range_parser.run_date_range(config)
    date_range_report = date_range_parser.build_report(config, rows, source_events, date_urls)
    manifest = build_manifest(plan, batch, rows, date_range_report)

    save_json(Path(batch["rows_file"]), rows)
    save_json(Path(batch["manifest_file"]), manifest)
    save_text(Path(batch["report_file"]), build_batch_report(manifest, date_range_report))

    print("Final summary")
    print("-------------")
    print(f"Batch ID: {manifest['batch_id']}")
    print(f"Rows produced: {manifest['rows']['produced']}")
    print(f"XML files parsed: {manifest['source_files']['parsed']}")
    print(f"XML files not available: {manifest['source_files']['not_available']}")
    print(f"XML files failed: {manifest['source_files']['failed']}")
    print(f"Safe to merge later: {manifest['checks']['safe_to_merge_later']}")
    print(f"Hard stop reasons: {', '.join(manifest['checks']['hard_stop_reasons']) or 'none'}")
    print(f"Manifest: {batch['manifest_file']}")
    print(f"Rows: {batch['rows_file']}")
    print(f"Report: {batch['report_file']}")

    if manifest["checks"]["hard_stop_reasons"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
