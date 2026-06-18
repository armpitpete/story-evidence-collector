import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


BATCH_ID = "parlparse_2003_01"
MERGE_GATE_FILE = Path("parlparse_batch_merge_gate_v21.json")
MANIFEST_FILE = Path("parlparse_batches/parlparse_2003_01_manifest.json")
ROWS_FILE = Path("parlparse_batches/parlparse_2003_01_rows.json")
COMMONS_INDEX_FILE = Path("mp_full_vote_index_v13.json")
OUTPUT_JSON_FILE = Path("parlparse_manual_merge_plan_v22.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_manual_merge_plan_v22.md")

DEDUPE_KEY_FIELDS = ["source_system", "division_id", "target_mp"]
FUTURE_OUTPUT_FILES = [
    "mp_combined_vote_index.json",
    "mp_combined_vote_index.md",
    "mp_combined_vote_index_merge_report.md",
]
FORBIDDEN_V22_OUTPUT_FILES = [
    "mp_combined_vote_index.json",
    "mp_combined_vote_index.md",
]

COVERAGE_WORDING_TO_PRESERVE = [
    "Commons Votes API rows are an available-source index from 2016-04-26 onward, not a full-career index.",
    "The ParlParse input here is one ready January 2003 batch only: parlparse_2003_01.",
    "This does not claim complete 2001-2016 coverage.",
    "1983-2001 remains unsolved unless a separate historic source route is found or explicitly excluded.",
    "Never claim full-career coverage until historic gaps are solved or clearly excluded.",
]


class JsonLoadResult:
    def __init__(self, path, exists, data=None, error=""):
        self.path = path
        self.exists = exists
        self.data = data
        self.error = error


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json_if_available(path):
    if not path.exists():
        return JsonLoadResult(path=path, exists=False, data=None)
    try:
        with path.open("r", encoding="utf-8") as file:
            return JsonLoadResult(path=path, exists=True, data=json.load(file))
    except json.JSONDecodeError as error:
        return JsonLoadResult(path=path, exists=True, data=None, error=f"json_decode_error: {error}")


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


def get_votes_from_commons_index(data):
    if not isinstance(data, dict):
        return []
    votes = data.get("votes", [])
    return votes if isinstance(votes, list) else []


def build_commons_index_status(result):
    if not result.exists:
        return {
            "commons_index_available": False,
            "commons_row_count": 0,
            "commons_index_status": "not_available_optional_for_v22_required_for_future_merge",
        }
    if result.error:
        return {
            "commons_index_available": True,
            "commons_row_count": 0,
            "commons_index_status": result.error,
        }
    rows = get_votes_from_commons_index(result.data)
    return {
        "commons_index_available": True,
        "commons_row_count": len(rows),
        "commons_index_status": "available" if rows else "available_but_no_votes_array_rows_found",
    }


def row_dedupe_key(row, target_mp):
    if not isinstance(row, dict):
        row = {}
    return {
        "source_system": clean_text(row.get("source_system")),
        "division_id": clean_text(row.get("division_id")),
        "target_mp": clean_text(target_mp),
    }


def duplicate_dedupe_keys(rows, target_mp):
    seen = set()
    duplicates = []
    for row in rows:
        key = row_dedupe_key(row, target_mp)
        key_tuple = tuple(key[field] for field in DEDUPE_KEY_FIELDS)
        if key_tuple in seen:
            duplicates.append(key)
        else:
            seen.add(key_tuple)
    return duplicates


def build_gate_status(gate_result):
    if not gate_result.exists:
        return {
            "v21_gate_available": False,
            "v21_gate_ready": False,
            "v21_gate_batch_id": "",
            "v21_gate_status": "not_available",
            "v21_gate_blockers": ["v21_merge_gate_report_missing"],
        }
    if gate_result.error:
        return {
            "v21_gate_available": True,
            "v21_gate_ready": False,
            "v21_gate_batch_id": "",
            "v21_gate_status": gate_result.error,
            "v21_gate_blockers": ["v21_merge_gate_report_invalid_json"],
        }

    data = gate_result.data if isinstance(gate_result.data, dict) else {}
    blockers = list(data.get("blockers", []))
    gate_batch_id = clean_text(data.get("batch_id"))
    status = clean_text(data.get("merge_gate_status"))

    if gate_batch_id != BATCH_ID:
        blockers.append("v21_merge_gate_batch_id_mismatch")

    ready = status == "ready_for_future_manual_merge" and not blockers
    return {
        "v21_gate_available": True,
        "v21_gate_ready": ready,
        "v21_gate_batch_id": gate_batch_id,
        "v21_gate_expected_batch_id": BATCH_ID,
        "v21_gate_status": status or "unknown",
        "v21_gate_blockers": blockers,
    }


def build_row_eligibility(rows_result, manifest_result, gate_status):
    blockers = []
    rows = rows_result.data if rows_result.exists and not rows_result.error else []
    manifest = manifest_result.data if manifest_result.exists and not manifest_result.error else {}

    if not rows_result.exists:
        blockers.append("batch_rows_file_missing")
        rows = []
    elif rows_result.error:
        blockers.append("batch_rows_file_invalid_json")
        rows = []
    elif not isinstance(rows, list):
        blockers.append("batch_rows_file_is_not_a_list")
        rows = []

    if not manifest_result.exists:
        blockers.append("batch_manifest_missing")
        manifest = {}
    elif manifest_result.error:
        blockers.append("batch_manifest_invalid_json")
        manifest = {}

    non_dict_row_count = len([row for row in rows if not isinstance(row, dict)])
    if non_dict_row_count:
        blockers.append("batch_rows_include_non_object_rows")

    target_mp = manifest.get("target_mp", "") if isinstance(manifest, dict) else ""
    dict_rows = [row for row in rows if isinstance(row, dict)]
    side_counts = Counter(clean_text(row.get("recorded_side")) for row in dict_rows)
    duplicates = duplicate_dedupe_keys(dict_rows, target_mp)
    if duplicates:
        blockers.append("duplicate_dedupe_keys_found")

    if not gate_status.get("v21_gate_ready"):
        blockers.append("v21_merge_gate_not_ready")

    eligible = not blockers and len(dict_rows) > 0
    eligible_keys = [row_dedupe_key(row, target_mp) for row in dict_rows] if eligible else []

    return {
        "batch_id": BATCH_ID,
        "target_mp": target_mp,
        "rows_loaded": len(rows),
        "object_rows_loaded": len(dict_rows),
        "non_object_rows_loaded": non_dict_row_count,
        "rows_eligible_for_future_merge": len(dict_rows) if eligible else 0,
        "all_loaded_rows_are_eligible": eligible,
        "recorded_side_counts": dict(sorted(side_counts.items())),
        "eligible_dedupe_keys": eligible_keys,
        "duplicate_dedupe_keys": duplicates,
        "row_eligibility_blockers": blockers,
    }


def build_plan():
    gate_result = load_json_if_available(MERGE_GATE_FILE)
    manifest_result = load_json_if_available(MANIFEST_FILE)
    rows_result = load_json_if_available(ROWS_FILE)
    commons_result = load_json_if_available(COMMONS_INDEX_FILE)

    gate_status = build_gate_status(gate_result)
    row_eligibility = build_row_eligibility(rows_result, manifest_result, gate_status)
    commons_status = build_commons_index_status(commons_result)

    plan_blockers = []
    if not gate_status.get("v21_gate_ready"):
        plan_blockers.append("v21_merge_gate_not_ready")
    if row_eligibility.get("rows_eligible_for_future_merge", 0) == 0:
        plan_blockers.append("no_rows_eligible_for_future_merge")

    future_merge_blockers = []
    if not commons_status.get("commons_index_available"):
        future_merge_blockers.append("mp_full_vote_index_v13_json_must_be_available_before_actual_merge")
    elif commons_status.get("commons_index_status") != "available":
        future_merge_blockers.append("mp_full_vote_index_v13_json_shape_must_be_checked_before_actual_merge")
    future_merge_blockers.extend([
        "actual_merge_requires_a_separate_future_issue",
        "only_one_ParlParse_batch_is_ready_here_not_full_2001_2016_coverage",
        "1983_2001_historic_vote_source_gap_remains_unsolved",
        "meaning_quality_needs_review_must_not_be_presented_as_human_interpreted_vote_meaning",
    ])

    return {
        "generated_at": utc_now_iso(),
        "issue_scope": "MP v2.2 manual merge plan only",
        "batch_id": BATCH_ID,
        "network_requests_made": False,
        "merge_now": False,
        "combined_index_written": False,
        "forbidden_v22_output_files": FORBIDDEN_V22_OUTPUT_FILES,
        "v21_gate": gate_status,
        "row_eligibility": row_eligibility,
        "dedupe_key": {
            "name": "source-system division target-MP key",
            "fields": DEDUPE_KEY_FIELDS,
            "format": "source_system | division_id | target_mp",
            "reason": "Keeps ParlParse and Commons Votes API records traceable by source and prevents a target MP row from being merged twice for the same source division.",
        },
        "future_merge_outputs_to_write_later_not_now": FUTURE_OUTPUT_FILES,
        "future_merge_issue": {
            "title": "MP v2.3 — Manually merge Commons Votes API index with one ready ParlParse batch",
            "must_only_run_after": "v2.2 plan is reviewed and accepted",
            "must_not_claim": "full 2001-2016 coverage or full-career coverage",
        },
        "commons_index_status": commons_status,
        "coverage_wording_to_preserve": COVERAGE_WORDING_TO_PRESERVE,
        "plan_blockers": plan_blockers,
        "future_merge_blockers": future_merge_blockers,
        "manual_merge_plan_status": "ready_for_future_actual_merge_issue" if not plan_blockers else "blocked",
    }


def build_markdown(report):
    gate = report.get("v21_gate", {})
    eligibility = report.get("row_eligibility", {})
    commons = report.get("commons_index_status", {})
    future_issue = report.get("future_merge_issue", {})
    dedupe = report.get("dedupe_key", {})

    lines = []
    lines.append("# ParlParse Manual Merge Plan v2.2")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This is a plan/report only. It does not merge rows, fetch data, run new ParlParse batches, or write a combined MP vote index.")
    lines.append("")
    lines.append("## Safety result")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Network requests made", report.get("network_requests_made", False)],
        ["Merge now", report.get("merge_now", False)],
        ["Combined index written", report.get("combined_index_written", False)],
        ["Manual merge plan status", report.get("manual_merge_plan_status", "")],
        ["Forbidden v2.2 output files", ", ".join(report.get("forbidden_v22_output_files", []))],
    ]))
    lines.append("")
    lines.append("## Is the v2.1 merge gate ready?")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["v2.1 gate available", gate.get("v21_gate_available", False)],
        ["v2.1 gate batch ID", gate.get("v21_gate_batch_id", "")],
        ["Expected batch ID", gate.get("v21_gate_expected_batch_id", BATCH_ID)],
        ["v2.1 gate status", gate.get("v21_gate_status", "")],
        ["v2.1 gate ready", gate.get("v21_gate_ready", False)],
        ["v2.1 gate blockers", ", ".join(gate.get("v21_gate_blockers", [])) or "none"],
    ]))
    lines.append("")
    lines.append("## What rows would be eligible for future merge?")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Batch ID", eligibility.get("batch_id", "")],
        ["Target MP", eligibility.get("target_mp", "")],
        ["Rows loaded", eligibility.get("rows_loaded", 0)],
        ["Object rows loaded", eligibility.get("object_rows_loaded", 0)],
        ["Non-object rows loaded", eligibility.get("non_object_rows_loaded", 0)],
        ["Rows eligible for future merge", eligibility.get("rows_eligible_for_future_merge", 0)],
        ["All loaded rows eligible", eligibility.get("all_loaded_rows_are_eligible", False)],
        ["Recorded side counts", json.dumps(eligibility.get("recorded_side_counts", {}), ensure_ascii=False)],
        ["Duplicate dedupe keys", len(eligibility.get("duplicate_dedupe_keys", []))],
        ["Row eligibility blockers", ", ".join(eligibility.get("row_eligibility_blockers", [])) or "none"],
    ]))
    lines.append("")
    lines.append("## Dedupe key for a future merge")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Name", dedupe.get("name", "")],
        ["Fields", ", ".join(dedupe.get("fields", []))],
        ["Format", dedupe.get("format", "")],
        ["Reason", dedupe.get("reason", "")],
    ]))
    lines.append("")
    lines.append("## Future output names")
    lines.append("")
    lines.append("A later merge issue would write these files. v2.2 does not write them.")
    lines.append("")
    for filename in report.get("future_merge_outputs_to_write_later_not_now", []):
        lines.append(f"- `{filename}`")
    lines.append("")
    lines.append("## Commons Votes API index availability")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Commons index available", commons.get("commons_index_available", False)],
        ["Commons row count", commons.get("commons_row_count", 0)],
        ["Commons index status", commons.get("commons_index_status", "")],
    ]))
    lines.append("")
    lines.append("## Coverage wording to preserve")
    lines.append("")
    for item in report.get("coverage_wording_to_preserve", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Blockers remaining")
    lines.append("")
    if report.get("plan_blockers"):
        lines.append("Plan blockers:")
        for blocker in report.get("plan_blockers", []):
            lines.append(f"- `{blocker}`")
    else:
        lines.append("No v2.2 plan blockers found.")
    lines.append("")
    lines.append("Future merge blockers / limits:")
    for blocker in report.get("future_merge_blockers", []):
        lines.append(f"- `{blocker}`")
    lines.append("")
    lines.append("## Exact future issue")
    lines.append("")
    lines.append(f"Next actual-merge issue: **{future_issue.get('title', '')}**")
    lines.append("")
    lines.append(f"Run only after: {future_issue.get('must_only_run_after', '')}")
    lines.append("")
    lines.append(f"Must not claim: {future_issue.get('must_not_claim', '')}")
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not create `mp_combined_vote_index.json`.")
    lines.append("- It does not create `mp_combined_vote_index.md`.")
    lines.append("- It does not merge Commons Votes API and ParlParse rows.")
    lines.append("- It does not fetch new data from the web.")
    lines.append("- It does not run any new ParlParse import batch.")
    lines.append("- It does not claim full 2001-2016 or full-career coverage.")
    return "\n".join(lines) + "\n"


def main():
    print("Planning manual ParlParse batch merge v2.2")
    report = build_plan()
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Batch ID: {report['batch_id']}")
    print(f"v2.1 gate ready: {report['v21_gate']['v21_gate_ready']}")
    print(f"Rows eligible for future merge: {report['row_eligibility']['rows_eligible_for_future_merge']}")
    print(f"Manual merge plan status: {report['manual_merge_plan_status']}")
    print(f"Plan blockers: {', '.join(report['plan_blockers']) or 'none'}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    return 0 if report["manual_merge_plan_status"] == "ready_for_future_actual_merge_issue" else 1


if __name__ == "__main__":
    raise SystemExit(main())
