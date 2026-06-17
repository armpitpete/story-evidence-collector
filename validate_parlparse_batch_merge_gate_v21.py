import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


BATCH_ID = "parlparse_2003_01"
MANIFEST_FILE = Path("parlparse_batches/parlparse_2003_01_manifest.json")
ROWS_FILE = Path("parlparse_batches/parlparse_2003_01_rows.json")
COMMONS_INDEX_FILE = Path("mp_full_vote_index_v13.json")
OUTPUT_JSON_FILE = Path("parlparse_batch_merge_gate_v21.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_batch_merge_gate_v21.md")

REQUIRED_TRACEABILITY_FIELDS = [
    "source_system",
    "source_xml_url",
    "source_url",
    "division_id",
    "division_number",
    "date",
    "recorded_side",
    "evidence_status",
]

REQUIRED_ROW_FIELDS = [
    "date",
    "division_id",
    "division_number",
    "motion_title",
    "recorded_side",
    "meaning_quality",
    "topic",
    "source_url",
    "source_system",
    "evidence_status",
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


def missing_fields_for_row(row, required_fields):
    return [field for field in required_fields if not clean_text(row.get(field))]


def duplicate_keys(rows, target_mp):
    seen = set()
    duplicates = []
    for row in rows:
        key = (clean_text(row.get("source_system")), clean_text(row.get("division_id")), clean_text(target_mp))
        if key in seen:
            duplicates.append(" | ".join(key))
        else:
            seen.add(key)
    return duplicates


def validate_rows(rows, manifest):
    target_mp = manifest.get("target_mp", "")
    failures = []
    row_failures = []

    for index, row in enumerate(rows, start=1):
        missing = missing_fields_for_row(row, REQUIRED_TRACEABILITY_FIELDS)
        if missing:
            row_failures.append({"row_number": index, "division_id": row.get("division_id", ""), "failure": "missing_traceability_fields", "fields": missing})
        if clean_text(row.get("source_system")) != "parlparse":
            row_failures.append({"row_number": index, "division_id": row.get("division_id", ""), "failure": "wrong_source_system", "value": row.get("source_system", "")})
        if clean_text(row.get("meaning_quality")) != "needs_review":
            row_failures.append({"row_number": index, "division_id": row.get("division_id", ""), "failure": "wrong_meaning_quality", "value": row.get("meaning_quality", "")})

    duplicates = duplicate_keys(rows, target_mp)
    if duplicates:
        failures.append("duplicate_dedupe_keys")
    if row_failures:
        failures.append("row_level_validation_failures")

    return {"row_count": len(rows), "row_failures": row_failures, "duplicate_keys": duplicates, "duplicate_key_count": len(duplicates), "failures": failures}


def load_commons_index_shape():
    if not COMMONS_INDEX_FILE.exists():
        return {"commons_index_available": False, "commons_row_count": 0, "compatible_fields": [], "parlparse_only_fields": [], "commons_only_fields": [], "shape_status": "not_checked"}

    data = load_json(COMMONS_INDEX_FILE)
    commons_rows = data.get("votes", []) if isinstance(data, dict) else []
    if not commons_rows:
        return {"commons_index_available": True, "commons_row_count": 0, "compatible_fields": [], "parlparse_only_fields": [], "commons_only_fields": [], "shape_status": "not_checked_no_commons_rows"}

    commons_fields = set().union(*(row.keys() for row in commons_rows if isinstance(row, dict)))
    parlparse_fields = set(REQUIRED_ROW_FIELDS + ["source_xml_url", "available_trace_fields"])
    return {"commons_index_available": True, "commons_row_count": len(commons_rows), "compatible_fields": sorted(commons_fields & parlparse_fields), "parlparse_only_fields": sorted(parlparse_fields - commons_fields), "commons_only_fields": sorted(commons_fields - parlparse_fields), "shape_status": "checked"}


def build_report():
    blockers = []
    manifest_exists = MANIFEST_FILE.exists()
    rows_file_exists = ROWS_FILE.exists()

    manifest = load_json(MANIFEST_FILE) if manifest_exists else {}
    rows = load_json(ROWS_FILE) if rows_file_exists else []
    if not isinstance(rows, list):
        rows = []
        blockers.append("rows_file_is_not_a_list")

    if not manifest_exists:
        blockers.append("batch_manifest_missing")
    if not rows_file_exists:
        blockers.append("batch_rows_file_missing")
    if manifest_exists and manifest.get("checks", {}).get("safe_to_merge_later") is not True:
        blockers.append("manifest_not_safe_to_merge_later")
    if manifest_exists and manifest.get("merge_now") is not False:
        blockers.append("manifest_merge_now_not_false")

    row_validation = validate_rows(rows, manifest) if rows else {"row_count": 0, "row_failures": [], "duplicate_keys": [], "duplicate_key_count": 0, "failures": ["no_rows_to_validate"]}
    blockers.extend(row_validation.get("failures", []))
    commons_shape = load_commons_index_shape()
    merge_gate_status = "blocked" if blockers else "ready_for_future_manual_merge"

    return {
        "generated_at": utc_now_iso(),
        "batch_id": BATCH_ID,
        "network_requests_made": False,
        "merge_now": False,
        "merged_index_written": False,
        "manifest_exists": manifest_exists,
        "rows_file_exists": rows_file_exists,
        "manifest_safe_to_merge_later": manifest.get("checks", {}).get("safe_to_merge_later"),
        "manifest_merge_now": manifest.get("merge_now"),
        "target_mp": manifest.get("target_mp", ""),
        "rows_produced_in_manifest": manifest.get("rows", {}).get("produced", 0),
        "rows_loaded": len(rows),
        "row_validation": row_validation,
        "commons_index_shape": commons_shape,
        "blockers": blockers,
        "merge_gate_status": merge_gate_status,
        "next_action": "Create a separate future issue for manual merge only after this merge gate remains ready and coverage wording is preserved.",
    }


def build_markdown(report):
    row_validation = report.get("row_validation", {})
    commons_shape = report.get("commons_index_shape", {})
    lines = []
    lines.append("# ParlParse Batch Merge Gate v2.1")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report validates one safe ParlParse batch for a future manual merge. It does not merge rows, fetch data, alter Commons Votes API rows, or claim full coverage.")
    lines.append("")
    lines.append("## Merge gate decision")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Batch ID", report.get("batch_id", "")],
        ["Merge gate status", report.get("merge_gate_status", "")],
        ["Target MP", report.get("target_mp", "")],
        ["Network requests made", report.get("network_requests_made", False)],
        ["Merge now", report.get("merge_now", False)],
        ["Merged index written", report.get("merged_index_written", False)],
    ]))
    lines.append("")
    lines.append("## Required checks")
    lines.append("")
    lines.append(markdown_table(["Check", "Result"], [
        ["Batch manifest exists", report.get("manifest_exists", False)],
        ["Batch rows file exists", report.get("rows_file_exists", False)],
        ["Manifest safe_to_merge_later", report.get("manifest_safe_to_merge_later")],
        ["Manifest merge_now", report.get("manifest_merge_now")],
        ["Rows produced in manifest", report.get("rows_produced_in_manifest", 0)],
        ["Rows loaded", report.get("rows_loaded", 0)],
        ["Duplicate keys", row_validation.get("duplicate_key_count", 0)],
        ["Row-level failures", len(row_validation.get("row_failures", []))],
    ]))
    lines.append("")
    lines.append("## Commons Votes API shape comparison")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Commons index available", commons_shape.get("commons_index_available", False)],
        ["Commons row count", commons_shape.get("commons_row_count", 0)],
        ["Shape status", commons_shape.get("shape_status", "")],
        ["Compatible fields", ", ".join(commons_shape.get("compatible_fields", []))],
        ["ParlParse-only fields", ", ".join(commons_shape.get("parlparse_only_fields", []))],
        ["Commons-only fields", ", ".join(commons_shape.get("commons_only_fields", []))],
    ]))
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if report.get("blockers"):
        for blocker in report.get("blockers", []):
            lines.append(f"- `{blocker}`")
    else:
        lines.append("No blockers found.")
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge rows into the main MP vote index.")
    lines.append("- It does not create a combined index.")
    lines.append("- It does not run new ParlParse batches.")
    lines.append("- It does not fetch data from the web.")
    lines.append("- It does not infer human political meaning from vote titles.")
    lines.append("- It does not claim full 2001-2016 or full-career coverage.")
    lines.append("")
    lines.append("## Next action")
    lines.append("")
    lines.append(report.get("next_action", ""))
    return "\n".join(lines) + "\n"


def main():
    print("Validating ParlParse batch merge gate v2.1")
    report = build_report()
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Batch ID: {report['batch_id']}")
    print(f"Rows loaded: {report['rows_loaded']}")
    print(f"Merge gate status: {report['merge_gate_status']}")
    print(f"Blockers: {', '.join(report['blockers']) or 'none'}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    return 0 if report["merge_gate_status"] == "ready_for_future_manual_merge" else 1


if __name__ == "__main__":
    raise SystemExit(main())
