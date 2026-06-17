import json
from datetime import datetime, timezone
from pathlib import Path


SUBJECT_QUERY_FILE = Path("subject_query.json")
CANDIDATE_SOURCES_FILE = Path("candidate_sources_raw_v15.json")
OUTPUT_JSON_REPORT_FILE = Path("subject_follow_priority_report_v23.json")
OUTPUT_MARKDOWN_REPORT_FILE = Path("subject_follow_priority_report_v23.md")
MAX_FOLLOW_FETCHES = 3
SAZAN_ARTICLE_SLUG = "the-sazan-island-deal-shows-how-public-land-becomes-private-power"


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
    if not value:
        return ""
    return " ".join(str(value).split())


def match_text(value):
    text = clean_text(value).lower()
    for old in ["-", "_", "/", ".", "?", "&", "=", ":"]:
        text = text.replace(old, " ")
    return clean_text(text)


def load_subject_query():
    data = load_json(SUBJECT_QUERY_FILE)
    subject = clean_text(data.get("subject"))
    terms = data.get("terms")

    if not subject:
        raise RuntimeError("subject_query.json needs a subject.")
    if not isinstance(terms, list) or not terms:
        raise RuntimeError("subject_query.json needs a terms list.")

    clean_terms = []
    seen = set()
    for term in terms:
        cleaned = clean_text(term)
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            clean_terms.append(cleaned)

    return {
        "subject": subject,
        "terms": clean_terms,
        "match_terms": [match_text(term) for term in clean_terms],
    }


def score_link(url, found_on, subject_query):
    url_text = match_text(url)
    found_on_text = match_text(found_on)
    matched_terms = []
    score = 0

    for term, match_term in zip(subject_query["terms"], subject_query["match_terms"]):
        if not match_term:
            continue
        matched = False
        if match_term in url_text:
            score += 10
            matched = True
        if match_term in found_on_text:
            score += 3
            matched = True
        if matched:
            matched_terms.append(term)

    return score, matched_terms


def has_sazan_article(url):
    return SAZAN_ARTICLE_SLUG in clean_text(url).lower()


def prioritise_links(records, subject_query):
    source_reports = []
    total_links = 0
    total_subject_links = 0
    sazan_present = False
    sazan_top_three = False

    for record_index, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        links = record.get("links_found")
        if not isinstance(links, list):
            continue

        found_on = record.get("final_url") or record.get("source_url") or ""
        scored = []

        for original_index, url in enumerate(links):
            score, matched_terms = score_link(url, found_on, subject_query)
            scored.append({
                "url": url,
                "score": score,
                "matched_terms": matched_terms,
                "original_index": original_index,
            })

        scored.sort(key=lambda item: (-item["score"], item["original_index"]))
        record["links_found"] = [item["url"] for item in scored]

        subject_links = [item for item in scored if item["score"] > 0]
        top_three = scored[:MAX_FOLLOW_FETCHES]

        total_links += len(scored)
        total_subject_links += len(subject_links)

        if any(has_sazan_article(item["url"]) for item in scored):
            sazan_present = True
        if any(has_sazan_article(item["url"]) for item in top_three):
            sazan_top_three = True

        source_reports.append({
            "record_index": record_index,
            "source_url": record.get("source_url"),
            "final_url": record.get("final_url"),
            "links_seen": len(scored),
            "subject_matching_links": len(subject_links),
            "top_three_after_priority": top_three,
            "subject_matching_urls": subject_links,
        })

    return {
        "records": records,
        "source_reports": source_reports,
        "total_links": total_links,
        "total_subject_links": total_subject_links,
        "sazan_present": sazan_present,
        "sazan_top_three": sazan_top_three,
    }


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        clean_row = [clean_text(value).replace("|", "\\|") for value in row]
        lines.append("| " + " | ".join(clean_row) + " |")
    return "\n".join(lines)


def build_report(subject_query, result):
    return {
        "generated_at": utc_now_iso(),
        "subject": subject_query["subject"],
        "terms": subject_query["terms"],
        "local_only": True,
        "candidate_sources_file_reordered_in_place": str(CANDIDATE_SOURCES_FILE),
        "max_follow_fetches": MAX_FOLLOW_FETCHES,
        "candidate_source_records_reported": len(result["source_reports"]),
        "follow_links_seen": result["total_links"],
        "subject_matching_follow_links": result["total_subject_links"],
        "sazan_article_present_when_checked": result["sazan_present"],
        "sazan_article_promoted_to_top_three_when_present": result["sazan_top_three"],
        "source_reports": result["source_reports"],
    }


def build_markdown(report):
    lines = []
    lines.append(f"# Subject Follow Priority Report v2.3 — {report['subject']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This local step reorders links already found inside fetched candidate pages before the existing follow limit is applied.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(
        ["Metric", "Count"],
        [
            ["Candidate source records reported", report["candidate_source_records_reported"]],
            ["Follow links seen", report["follow_links_seen"]],
            ["Subject-matching follow links", report["subject_matching_follow_links"]],
            ["Sazan article present", report["sazan_article_present_when_checked"]],
            ["Sazan article promoted to top three", report["sazan_article_promoted_to_top_three_when_present"]],
            ["Local only", report["local_only"]],
        ],
    ))
    lines.append("")
    lines.append("## Top links after prioritisation")
    lines.append("")

    top_rows = []
    for source_report in report["source_reports"]:
        found_on = source_report.get("final_url") or source_report.get("source_url")
        for item in source_report["top_three_after_priority"]:
            top_rows.append([
                found_on,
                item["url"],
                item["score"],
                ", ".join(item.get("matched_terms") or []),
                item["original_index"],
            ])

    if top_rows:
        lines.append(markdown_table(["Found on", "URL", "Score", "Matched terms", "Original index"], top_rows))
    else:
        lines.append("No links were available to prioritise.")

    lines.append("")
    lines.append("## Subject-matching follow links")
    lines.append("")

    match_rows = []
    for source_report in report["source_reports"]:
        found_on = source_report.get("final_url") or source_report.get("source_url")
        for item in source_report["subject_matching_urls"]:
            match_rows.append([
                found_on,
                item["url"],
                item["score"],
                ", ".join(item.get("matched_terms") or []),
                item["original_index"],
            ])

    if match_rows:
        lines.append(markdown_table(["Found on", "URL", "Score", "Matched terms", "Original index"], match_rows))
    else:
        lines.append("No subject-matching follow links were found.")

    return "\n".join(lines) + "\n"


def main():
    print("Starting subject follow-link prioritisation v2.3")

    try:
        subject_query = load_subject_query()
        records = load_json(CANDIDATE_SOURCES_FILE)
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    if not isinstance(records, list):
        print(f"FAILED: {CANDIDATE_SOURCES_FILE} must contain a list.")
        return 1

    result = prioritise_links(records, subject_query)
    report = build_report(subject_query, result)

    save_json(CANDIDATE_SOURCES_FILE, result["records"])
    save_json(OUTPUT_JSON_REPORT_FILE, report)
    save_text(OUTPUT_MARKDOWN_REPORT_FILE, build_markdown(report))

    print("Final summary")
    print("-------------")
    print(f"Subject: {report['subject']}")
    print(f"Follow links seen: {report['follow_links_seen']}")
    print(f"Subject-matching follow links: {report['subject_matching_follow_links']}")
    print(f"Sazan article present: {report['sazan_article_present_when_checked']}")
    print(f"Sazan article promoted to top three: {report['sazan_article_promoted_to_top_three_when_present']}")
    print(f"Report output: {OUTPUT_MARKDOWN_REPORT_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
