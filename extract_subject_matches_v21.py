import json
import re
from datetime import datetime, timezone
from pathlib import Path


SUBJECT_QUERY_FILE = Path("subject_query.json")
OUTPUT_JSON_FILE = Path("subject_matches_v21.json")
OUTPUT_MARKDOWN_FILE = Path("subject_matches_v21.md")

SOURCE_FILES = [
    {
        "filename": Path("sources_raw_v13.json"),
        "stage": "seed source records v1.3",
    },
    {
        "filename": Path("candidate_sources_raw_v15.json"),
        "stage": "candidate source records v1.5",
    },
    {
        "filename": Path("followed_sources_raw_v16.json"),
        "stage": "followed source records v1.6",
    },
]

EXCERPT_RADIUS = 220


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json_file(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def save_text_file(path, text):
    with path.open("w", encoding="utf-8") as file:
        file.write(text)


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).split())


def load_subject_query():
    if not SUBJECT_QUERY_FILE.exists():
        raise RuntimeError(f"Missing subject query file: {SUBJECT_QUERY_FILE}")

    data = load_json_file(SUBJECT_QUERY_FILE)

    subject = clean_text(data.get("subject"))
    terms = data.get("terms")

    if not subject:
        raise RuntimeError("subject_query.json must include a non-empty subject.")

    if not isinstance(terms, list) or len(terms) == 0:
        raise RuntimeError("subject_query.json must include a non-empty terms list.")

    clean_terms = []
    seen_terms = set()

    for term in terms:
        clean_term = clean_text(term)

        if not clean_term:
            continue

        lower_term = clean_term.lower()

        if lower_term in seen_terms:
            continue

        seen_terms.add(lower_term)
        clean_terms.append(clean_term)

    if len(clean_terms) == 0:
        raise RuntimeError("subject_query.json terms list contains no usable terms.")

    return {
        "subject": subject,
        "terms": clean_terms,
    }


def load_source_records():
    all_records = []
    file_reports = []

    for source_file in SOURCE_FILES:
        path = source_file["filename"]
        stage = source_file["stage"]

        if not path.exists():
            file_reports.append({
                "filename": str(path),
                "stage": stage,
                "loaded": False,
                "record_count": 0,
                "status": "missing",
            })
            continue

        data = load_json_file(path)

        if not isinstance(data, list):
            file_reports.append({
                "filename": str(path),
                "stage": stage,
                "loaded": False,
                "record_count": 0,
                "status": "not_a_list",
            })
            continue

        usable_records = [record for record in data if isinstance(record, dict)]

        for record in usable_records:
            all_records.append({
                "stage": stage,
                "record": record,
            })

        file_reports.append({
            "filename": str(path),
            "stage": stage,
            "loaded": True,
            "record_count": len(usable_records),
            "status": "loaded",
        })

    return all_records, file_reports


def find_matched_terms(text, terms):
    text_lower = text.lower()
    matched_terms = []

    for term in terms:
        if term.lower() in text_lower:
            matched_terms.append(term)

    return matched_terms


def find_first_match_position(text, matched_terms):
    text_lower = text.lower()
    positions = []

    for term in matched_terms:
        position = text_lower.find(term.lower())

        if position >= 0:
            positions.append(position)

    if not positions:
        return 0

    return min(positions)


def highlight_terms(excerpt, matched_terms):
    highlighted = excerpt

    for term in sorted(matched_terms, key=len, reverse=True):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        highlighted = pattern.sub(lambda match: f"**{match.group(0)}**", highlighted)

    return highlighted


def build_relevant_excerpt(text, matched_terms):
    clean = clean_text(text)

    if not clean:
        return ""

    first_position = find_first_match_position(clean, matched_terms)
    start = max(0, first_position - EXCERPT_RADIUS)
    end = min(len(clean), first_position + EXCERPT_RADIUS)
    excerpt = clean[start:end].strip()

    if start > 0:
        excerpt = "…" + excerpt

    if end < len(clean):
        excerpt = excerpt + "…"

    return excerpt


def build_search_text(record):
    parts = [
        record.get("page_title"),
        record.get("source_url"),
        record.get("final_url"),
        record.get("text_excerpt"),
    ]

    links_found = record.get("links_found")

    if isinstance(links_found, list):
        parts.extend(links_found)

    return clean_text(" ".join([str(part) for part in parts if part]))


def build_match(stage_record, terms):
    stage = stage_record["stage"]
    record = stage_record["record"]
    search_text = build_search_text(record)
    matched_terms = find_matched_terms(search_text, terms)

    if not matched_terms:
        return None

    scrape_status = record.get("scrape_status") or "unknown"
    fetched_successfully = scrape_status == "ok"
    url = record.get("final_url") or record.get("source_url") or ""

    return {
        "page_title": clean_text(record.get("page_title")) or "Untitled page",
        "url": url,
        "source_url": record.get("source_url"),
        "final_url": record.get("final_url"),
        "matched_terms": matched_terms,
        "relevant_excerpt": build_relevant_excerpt(search_text, matched_terms),
        "pipeline_stage": stage,
        "scrape_status": scrape_status,
        "fetched_successfully": fetched_successfully,
    }


def deduplicate_matches(matches):
    deduped = []
    seen_keys = set()

    for match in matches:
        key = (
            match.get("url"),
            tuple(sorted(term.lower() for term in match.get("matched_terms", []))),
        )

        if key in seen_keys:
            continue

        seen_keys.add(key)
        deduped.append(match)

    return deduped


def build_subject_report(subject_query, stage_records, file_reports):
    matches = []

    for stage_record in stage_records:
        match = build_match(stage_record, subject_query["terms"])

        if match is not None:
            matches.append(match)

    matches = deduplicate_matches(matches)

    fetched_matches = [match for match in matches if match["fetched_successfully"]]
    unfetched_matches = [match for match in matches if not match["fetched_successfully"]]

    return {
        "generated_at": utc_now_iso(),
        "subject": subject_query["subject"],
        "terms": subject_query["terms"],
        "scope_note": "This report finds all matching information inside the collected public pages for this run.",
        "network_requests_made": False,
        "input_files": file_reports,
        "records_scanned": len(stage_records),
        "matches_found": len(matches),
        "fetched_matches": len(fetched_matches),
        "unfetched_or_error_matches": len(unfetched_matches),
        "matches": matches,
    }


def markdown_table(headers, rows):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        clean_row = []

        for value in row:
            cell = clean_text(value)
            cell = cell.replace("|", "\\|")
            clean_row.append(cell)

        lines.append("| " + " | ".join(clean_row) + " |")

    return "\n".join(lines)


def build_markdown_report(report):
    lines = []

    lines.append(f"# Subject Match Report — {report['subject']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(report["scope_note"])
    lines.append("")
    lines.append("It does not claim to find all information on the internet.")
    lines.append("")
    lines.append("## Search terms")
    lines.append("")
    lines.append(", ".join([f"`{term}`" for term in report["terms"]]))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(
        ["Metric", "Count"],
        [
            ["Records scanned", report["records_scanned"]],
            ["Matches found", report["matches_found"]],
            ["Fetched successful matches", report["fetched_matches"]],
            ["Unfetched/error matches", report["unfetched_or_error_matches"]],
            ["Network requests made by this report", report["network_requests_made"]],
        ]
    ))
    lines.append("")
    lines.append("## Input files")
    lines.append("")
    lines.append(markdown_table(
        ["File", "Stage", "Loaded", "Records", "Status"],
        [
            [
                file_report["filename"],
                file_report["stage"],
                file_report["loaded"],
                file_report["record_count"],
                file_report["status"],
            ]
            for file_report in report["input_files"]
        ]
    ))
    lines.append("")
    lines.append("## Matching pages")
    lines.append("")

    if report["matches_found"] == 0:
        lines.append("No matching collected pages were found for this subject.")
        return "\n".join(lines) + "\n"

    lines.append(markdown_table(
        ["Page title", "URL", "Matched terms", "Stage", "Fetched"],
        [
            [
                match["page_title"],
                match["url"],
                ", ".join(match["matched_terms"]),
                match["pipeline_stage"],
                match["fetched_successfully"],
            ]
            for match in report["matches"]
        ]
    ))
    lines.append("")
    lines.append("## Relevant excerpts")
    lines.append("")

    for index, match in enumerate(report["matches"], start=1):
        lines.append(f"### {index}. {match['page_title']}")
        lines.append("")
        lines.append(f"URL: `{match['url']}`")
        lines.append("")
        lines.append(f"Stage: `{match['pipeline_stage']}`")
        lines.append("")
        lines.append(f"Fetched successfully: `{match['fetched_successfully']}`")
        lines.append("")
        lines.append(f"Matched terms: {', '.join([f'`{term}`' for term in match['matched_terms']])}")
        lines.append("")
        excerpt = highlight_terms(match["relevant_excerpt"], match["matched_terms"])
        lines.append(excerpt or "No excerpt available.")
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    print("Starting subject match extraction v2.1")
    print("No network requests will be made.")
    print("")

    try:
        subject_query = load_subject_query()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    stage_records, file_reports = load_source_records()
    report = build_subject_report(subject_query, stage_records, file_reports)
    markdown_report = build_markdown_report(report)

    save_json_file(OUTPUT_JSON_FILE, report)
    save_text_file(OUTPUT_MARKDOWN_FILE, markdown_report)

    print("Final summary")
    print("-------------")
    print(f"Subject: {report['subject']}")
    print(f"Records scanned: {report['records_scanned']}")
    print(f"Matches found: {report['matches_found']}")
    print(f"Fetched successful matches: {report['fetched_matches']}")
    print(f"Network requests made: {report['network_requests_made']}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
