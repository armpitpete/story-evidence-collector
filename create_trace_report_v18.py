import json

import create_trace_report_v17 as v17


TRACE_JSON_OUTPUT_FILE = "trace_report_v18.json"
TRACE_MARKDOWN_OUTPUT_FILE = "trace_report_v18.md"


def has_status(record, status):
    return status in record.get("statuses", [])


def get_final_status(record):
    # v1.7 used current_status correctly as the final state, but the wording
    # in the Markdown report made it look as if historical events were the
    # same thing as the final state.
    return record.get("current_status", "unknown")


def get_status_note(record):
    skip_reasons = record.get("skip_reasons") or []

    if record.get("fetched") and "already_known" in skip_reasons:
        return "Fetched earlier. Seen again later and skipped as already known."

    if record.get("fetched") and record.get("skipped"):
        return "Fetched earlier. Later skip records also exist; final status remains fetched."

    if record.get("fetched"):
        return "Fetched successfully."

    if record.get("skipped"):
        reasons = ", ".join(skip_reasons) or "unspecified reason"
        return f"Skipped. Reason: {reasons}."

    if has_status(record, "seed"):
        return "Seen in the original seed list."

    if has_status(record, "filter_candidate"):
        return "Seen as a candidate URL."

    if has_status(record, "pending"):
        return "Seen in the pending queue."

    return "Seen in the pipeline."


def get_history_note(record):
    parts = []

    if has_status(record, "seed"):
        parts.append("seed URL")

    if has_status(record, "pending"):
        parts.append("queued")

    if has_status(record, "filter_candidate"):
        parts.append("kept as candidate")

    if record.get("fetched"):
        parts.append("fetched")

    for reason in record.get("skip_reasons") or []:
        if reason == "already_known":
            parts.append("later skipped as already known")
        else:
            parts.append(f"skipped: {reason}")

    if not parts:
        parts.append("seen")

    return " → ".join(parts)


def build_readable_trace_records(trace_records):
    readable_records = []

    for record in trace_records:
        readable_record = dict(record)
        readable_record["final_status"] = get_final_status(record)
        readable_record["status_note"] = get_status_note(record)
        readable_record["history_note"] = get_history_note(record)
        readable_records.append(readable_record)

    return readable_records


def count_records_with_status(trace_records, status):
    return len([
        record for record in trace_records
        if has_status(record, status)
    ])


def count_fetched_then_already_known(trace_records):
    return len([
        record for record in trace_records
        if record.get("fetched") and "already_known" in (record.get("skip_reasons") or [])
    ])


def build_summary_counts(trace_records):
    return {
        "unique_urls_traced": len(trace_records),
        "fetched_urls_final_status": len([
            record for record in trace_records
            if record.get("final_status") == "fetched"
        ]),
        "skipped_urls_final_status": len([
            record for record in trace_records
            if record.get("final_status") == "skipped"
        ]),
        "candidate_urls_final_status": len([
            record for record in trace_records
            if record.get("final_status") == "candidate"
        ]),
        "pending_urls_final_status": len([
            record for record in trace_records
            if record.get("final_status") == "pending"
        ]),
        "seed_urls_seen": count_records_with_status(trace_records, "seed"),
        "fetched_then_skipped_as_already_known": count_fetched_then_already_known(trace_records),
        "skip_reason_counts": v17.count_skip_reasons(trace_records),
        "final_status_counts": v17.count_by_key(trace_records, "final_status"),
    }


def build_fetched_records(trace_records):
    records = v17.build_fetched_records(trace_records)

    for record in records:
        matching_record = next(
            item for item in trace_records
            if item["url"] == record["url"]
        )
        record["final_status"] = matching_record["final_status"]
        record["status_note"] = matching_record["status_note"]
        record["history_note"] = matching_record["history_note"]

    return records


def build_skipped_records(trace_records):
    records = v17.build_skipped_records(trace_records)

    for record in records:
        matching_record = next(
            item for item in trace_records
            if item["url"] == record["url"]
        )
        record["final_status"] = matching_record["final_status"]
        record["status_note"] = matching_record["status_note"]
        record["history_note"] = matching_record["history_note"]

    return records


def build_fetched_then_already_known_records(trace_records):
    return [
        {
            "url": record["url"],
            "final_status": record["final_status"],
            "stages": record.get("stages") or [],
            "status_note": record["status_note"],
            "history_note": record["history_note"],
        }
        for record in trace_records
        if record.get("fetched") and "already_known" in (record.get("skip_reasons") or [])
    ]


def format_stage_list(stages):
    return " → ".join(stages or [])


def build_markdown_report(report):
    counts = report["summary_counts"]
    lines = []

    lines.append("# Story Evidence Collector Trace Report v1.8")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Plain-English summary")
    lines.append("")
    lines.append(
        "This report explains what happened to each URL already present in the saved pipeline files. "
        "It does not fetch any pages and it does not make any network requests."
    )
    lines.append("")
    lines.append(
        "The report now separates final status from history. Final status answers: "
        "`Where did this URL end up?` History answers: `What happened to it along the way?`"
    )
    lines.append("")
    lines.append(
        "A URL can be fetched earlier and then skipped later as `already_known`. "
        "That is not a contradiction. It means the collector avoided fetching the same URL again."
    )
    lines.append("")
    lines.append(
        "`Seed URLs seen` means URLs that appeared in the original seed file. "
        "A seed URL can later become fetched, so this count is separate from final status."
    )
    lines.append("")
    lines.append("## Summary counts")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["Metric", "Count"],
        [
            ["Unique URLs traced", counts["unique_urls_traced"]],
            ["Fetched URLs final status", counts["fetched_urls_final_status"]],
            ["Skipped URLs final status", counts["skipped_urls_final_status"]],
            ["Candidate URLs final status", counts["candidate_urls_final_status"]],
            ["Pending URLs final status", counts["pending_urls_final_status"]],
            ["Seed URLs seen", counts["seed_urls_seen"]],
            [
                "Fetched earlier, later skipped as already known",
                counts["fetched_then_skipped_as_already_known"],
            ],
        ]
    ))
    lines.append("")
    lines.append("## Status wording")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["Wording", "Meaning"],
        [
            ["Final status", "The best plain-English status after all saved pipeline files are read."],
            ["History", "The stages and events seen before the final status was decided."],
            ["Seed URLs seen", "URLs from seed_urls.json, even if they later became fetched URLs."],
            [
                "Fetched earlier, later skipped as already known",
                "The URL was fetched once, then skipped later to avoid duplication.",
            ],
        ]
    ))
    lines.append("")
    lines.append("## Pipeline stage summary")
    lines.append("")
    lines.append(v17.format_markdown_table(
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
    lines.append("## Final URL status")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final status", "Plain-English note"],
        [
            [
                record["url"],
                record["final_status"],
                record["status_note"],
            ]
            for record in report["url_trace_records"]
        ]
    ))
    lines.append("")
    lines.append("## Fetched earlier, skipped later as already known")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final status", "History", "Plain-English note"],
        [
            [
                record["url"],
                record["final_status"],
                record["history_note"],
                record["status_note"],
            ]
            for record in report["fetched_then_already_known_records"]
        ]
    ))
    lines.append("")
    lines.append("## Fetched source table")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final URL", "Title", "Robots", "Plain-English note"],
        [
            [
                record["url"],
                record.get("final_url") or "",
                record.get("page_title") or "",
                record.get("robots_txt_status") or "",
                record.get("status_note") or "",
            ]
            for record in report["fetched_records"]
        ]
    ))
    lines.append("")
    lines.append("## Skipped URL table")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final status", "Skip reason", "Plain-English note"],
        [
            [
                record["url"],
                record["final_status"],
                ", ".join(record.get("skip_reasons") or []),
                record.get("status_note") or "",
            ]
            for record in report["skipped_records"]
        ]
    ))
    lines.append("")
    lines.append("## Historical events")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final status", "History", "Stages"],
        [
            [
                record["url"],
                record["final_status"],
                record["history_note"],
                format_stage_list(record.get("stages") or []),
            ]
            for record in report["url_trace_records"]
        ]
    ))
    lines.append("")
    lines.append("## Trace chains")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["URL", "Final status", "Trace"],
        [
            [
                record["url"],
                record["final_status"],
                v17.build_trace_chain(record),
            ]
            for record in report["url_trace_records"]
        ]
    ))
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    lines.append(v17.format_markdown_table(
        ["Check", "Result"],
        [
            ["Validation passed", report["validation_passed"]],
            ["Network requests made", report["network_requests_made"]],
            ["Warnings", "; ".join(report["validation_warnings"]) or "None"],
        ]
    ))

    return "\n".join(lines) + "\n"


def main():
    print("Starting trace report build v1.8")
    print("No network requests will be made.")
    print("")

    loaded_files = []
    traces = {}

    for file_config in v17.INPUT_FILES:
        filename = file_config["filename"]
        stage = file_config["stage"]

        data, load_report = v17.load_json_file(filename)
        load_report["stage"] = stage
        load_report["required"] = file_config["required"]
        loaded_files.append(load_report)

        print(f"{filename}: {load_report['status']}")

        if load_report["loaded"]:
            v17.process_file(traces, filename, stage, data)

    trace_records = v17.finalize_trace_records(traces)
    trace_records = build_readable_trace_records(trace_records)
    validation_warnings = v17.validate_report(loaded_files, trace_records)
    validation_passed = len(validation_warnings) == 0

    report = {
        "generated_at": v17.utc_now_iso(),
        "network_requests_made": False,
        "input_files": loaded_files,
        "summary_counts": build_summary_counts(trace_records),
        "stage_counts": v17.build_stage_counts(loaded_files),
        "url_trace_records": trace_records,
        "fetched_records": build_fetched_records(trace_records),
        "skipped_records": build_skipped_records(trace_records),
        "fetched_then_already_known_records": build_fetched_then_already_known_records(trace_records),
        "validation_passed": validation_passed,
        "validation_warnings": validation_warnings,
    }

    markdown_report = build_markdown_report(report)

    v17.save_json(TRACE_JSON_OUTPUT_FILE, report)
    v17.save_text(TRACE_MARKDOWN_OUTPUT_FILE, markdown_report)

    print("")
    print("Final summary")
    print("-------------")
    print(f"Unique URLs traced: {report['summary_counts']['unique_urls_traced']}")
    print(f"Fetched URLs final status: {report['summary_counts']['fetched_urls_final_status']}")
    print(f"Skipped URLs final status: {report['summary_counts']['skipped_urls_final_status']}")
    print(f"Seed URLs seen: {report['summary_counts']['seed_urls_seen']}")
    print(
        "Fetched earlier, later skipped as already known: "
        f"{report['summary_counts']['fetched_then_skipped_as_already_known']}"
    )
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
