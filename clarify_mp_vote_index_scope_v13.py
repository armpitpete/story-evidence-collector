import json
from pathlib import Path


INPUT_JSON_FILE = Path("mp_full_vote_index_v13.json")
OUTPUT_MARKDOWN_FILE = Path("mp_full_vote_index_v13.md")


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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


def coverage_verdict(report):
    query = report.get("query", {})
    first_found = clean_text(report.get("first_division_date_found"))
    known_start = clean_text(query.get("known_parliamentary_start_date"))

    if known_start and first_found and first_found > known_start:
        return (
            f"Partial historic coverage. This run found Commons Votes API records from {first_found}, "
            f"but the project-supplied parliamentary start date is {known_start}. Pre-{first_found[:4]} voting records are not covered by this source run."
        )

    if first_found:
        return f"Available-source coverage starts at {first_found} for this run. Verify source coverage before describing it as complete."

    return "No vote records were found in this run."


def build_markdown(report):
    query = report.get("query", {})
    votes = report.get("votes", [])

    lines = []
    lines.append(f"# Available Commons Votes MP Vote Index — {query.get('mp_name', '')}")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report indexes the Commons Votes API records available to this run. It is not a complete career voting history unless separate source coverage proves that the API contains the whole career record.")
    lines.append("")
    lines.append("## Coverage verdict")
    lines.append("")
    lines.append(coverage_verdict(report))
    lines.append("")
    lines.append("## MP checked")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["MP name", query.get("mp_name", "")],
        ["Member ID", query.get("member_id", "")],
        ["Constituency", query.get("constituency", "")],
        ["Party", query.get("party", "")],
        ["Party source status", query.get("party_source_status", "")],
        ["Parliamentary listing", query.get("parliamentary_listing", "")],
        ["Known parliamentary start date", query.get("known_parliamentary_start_date", "")],
        ["Known start source status", query.get("known_parliamentary_start_source_status", "")],
    ]))
    lines.append("")
    lines.append("## Coverage summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count / value"], [
        ["Pagination strategy", report.get("pagination_strategy", "")],
        ["Total results reported by source", report.get("total_results_reported_by_source", "")],
        ["Divisions indexed", report.get("divisions_indexed", 0)],
        ["Division details fetched", report.get("division_details_fetched", 0)],
        ["First division date found", report.get("first_division_date_found", "")],
        ["Latest division date found", report.get("latest_division_date_found", "")],
        ["Recorded Aye", report.get("recorded_aye", 0)],
        ["Recorded No", report.get("recorded_no", 0)],
        ["Not recorded", report.get("not_recorded", 0)],
        ["Unable to determine", report.get("unable_to_determine", 0)],
        ["Network requests made", report.get("network_requests_made", False)],
    ]))
    lines.append("")
    lines.append("## Coverage warnings")
    lines.append("")
    for warning in report.get("coverage_warnings", []):
        lines.append(f"- {warning}")
    lines.append("- This report should be described as an available-source index, not a full-career record, until pre-2016 / historic voting data is added and checked.")
    lines.append("")
    lines.append("## Vote index")
    lines.append("")
    lines.append(markdown_table(
        ["Date", "Division ID", "Division no.", "Motion title", "Recorded side", "Meaning quality", "Topic", "Source URL"],
        [
            [
                row.get("date", ""),
                row.get("division_id", ""),
                row.get("division_number", ""),
                row.get("motion_title", ""),
                row.get("recorded_side", ""),
                row.get("meaning_quality", ""),
                row.get("topic", ""),
                row.get("source_url", ""),
            ]
            for row in votes
        ],
    ))
    lines.append("")
    lines.append("## What this report does not prove")
    lines.append("")
    lines.append("- It does not prove motive or private belief.")
    lines.append("- It does not infer the human political meaning of each vote.")
    lines.append("- It does not cover pre-2016 voting records unless another historic source is added.")
    lines.append("- It does not prove complete historical coverage unless selected source coverage is verified.")
    lines.append("- It does not treat absence from a division list as proof of why the MP did not vote.")
    return "\n".join(lines) + "\n"


def main():
    print("Clarifying MP vote index scope v1.3")
    report = load_json(INPUT_JSON_FILE)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Markdown output clarified:", OUTPUT_MARKDOWN_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
