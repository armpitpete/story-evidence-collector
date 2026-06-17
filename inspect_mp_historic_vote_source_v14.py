import json
from datetime import datetime, timezone
from pathlib import Path


INPUT_FILE = Path("mp_historic_vote_source_candidates_v14.json")
OUTPUT_REPORT_FILE = Path("mp_historic_vote_source_report_v14.md")
OUTPUT_JSON_FILE = Path("mp_historic_vote_source_report_v14.json")


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


def rank_candidate(candidate):
    verdict = clean_text(candidate.get("verdict")).lower()
    if "best first" in verdict:
        return 1
    if "second" in verdict:
        return 2
    if "metadata" in verdict:
        return 3
    return 4


def readiness(candidate):
    bulk = clean_text(candidate.get("bulk_suitability")).lower()
    risk = clean_text(candidate.get("risk")).lower()
    if "strong" in bulk and "schema inspection" in risk:
        return "promising_needs_shape_inspection"
    if "weak" in bulk:
        return "not_primary_for_bulk_index"
    if "unknown" in bulk:
        return "needs_source_shape_check"
    return "needs_review"


def build_report_data(data):
    candidates = data.get("candidates", [])
    ranked = sorted(candidates, key=rank_candidate)
    return {
        "generated_at": utc_now_iso(),
        "purpose": data.get("purpose", ""),
        "target_mp": data.get("target_mp", {}),
        "network_requests_made": False,
        "recommended_first_route": ranked[0].get("source_id") if ranked else "",
        "candidates": [
            {
                **candidate,
                "readiness": readiness(candidate),
                "rank": index,
            }
            for index, candidate in enumerate(ranked, start=1)
        ],
        "next_action": "Inspect ParlParse raw data file structure first, because it is the strongest candidate for long-period historic vote indexing.",
    }


def build_markdown(report):
    target = report.get("target_mp", {})
    candidates = report.get("candidates", [])
    lines = []
    lines.append("# Historic MP Vote Source Report v1.4")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(report.get("purpose", ""))
    lines.append("")
    lines.append("## Target gap")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["MP", target.get("mp_name", "")],
        ["Member ID", target.get("member_id", "")],
        ["Known parliamentary start date", target.get("known_parliamentary_start_date", "")],
        ["Current Commons Votes API start date", target.get("current_available_commons_votes_start_date", "")],
        ["Network requests made by this inspection", report.get("network_requests_made", False)],
    ]))
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"Recommended first route: `{report.get('recommended_first_route', '')}`")
    lines.append("")
    lines.append(report.get("next_action", ""))
    lines.append("")
    lines.append("## Source candidates")
    lines.append("")
    lines.append(markdown_table(
        ["Rank", "Source", "Type", "Likely coverage", "Bulk suitability", "Readiness", "Verdict"],
        [
            [
                candidate.get("rank", ""),
                candidate.get("name", ""),
                candidate.get("source_type", ""),
                candidate.get("likely_date_coverage", ""),
                candidate.get("bulk_suitability", ""),
                candidate.get("readiness", ""),
                candidate.get("verdict", ""),
            ]
            for candidate in candidates
        ],
    ))
    lines.append("")
    lines.append("## Candidate details")
    lines.append("")
    for candidate in candidates:
        lines.append(f"### {candidate.get('rank')}. {candidate.get('name')}")
        lines.append("")
        lines.append(markdown_table(["Question", "Answer"], [
            ["Source URL", candidate.get("source_url", "")],
            ["Known value", candidate.get("known_value", "")],
            ["Can identify MP consistently?", candidate.get("can_identify_mp_consistently", "")],
            ["Can provide date/title/source/side?", candidate.get("can_provide_division_date_title_url_side", "")],
            ["Licensing / attribution", candidate.get("licensing_or_attribution", "")],
            ["Risk", candidate.get("risk", "")],
            ["Readiness", candidate.get("readiness", "")],
        ]))
        lines.append("")
    lines.append("## What this report decides")
    lines.append("")
    lines.append("- The current Commons Votes API report is useful from 2016 onward, but not full-career for a long-serving MP.")
    lines.append("- The next practical route is to inspect ParlParse raw data before trying paid/keyed APIs or page scraping.")
    lines.append("- Historic vote rows should not be merged until source shape, coverage, and attribution rules are understood.")
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not scrape historic votes.")
    lines.append("- It does not crawl source websites.")
    lines.append("- It does not claim pre-2016 coverage is solved.")
    lines.append("- It does not publish historic raw datasets.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting historic MP vote source inspection v1.4")
    print("No network requests will be made.")
    data = load_json(INPUT_FILE)
    report = build_report_data(data)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_REPORT_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Candidates checked: {len(report.get('candidates', []))}")
    print(f"Recommended first route: {report.get('recommended_first_route')}")
    print(f"Markdown output: {OUTPUT_REPORT_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
