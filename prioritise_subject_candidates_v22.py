import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse


SUBJECT_QUERY_FILE = Path("subject_query.json")
INPUT_QUEUE_FILE = Path("link_queue_filtered_v14.json")
OUTPUT_QUEUE_FILE = Path("link_queue_filtered_v22.json")
OUTPUT_JSON_REPORT_FILE = Path("subject_candidate_priority_report_v22.json")
OUTPUT_MARKDOWN_REPORT_FILE = Path("subject_candidate_priority_report_v22.md")


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


def normalise_for_match(value):
    text = unquote(clean_text(value)).lower()

    replacements = {
        "-": " ",
        "_": " ",
        "/": " ",
        ".": " ",
        "?": " ",
        "&": " ",
        "=": " ",
        ":": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return clean_text(text)


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
        "normalised_terms": [normalise_for_match(term) for term in clean_terms],
    }


def load_queue():
    if not INPUT_QUEUE_FILE.exists():
        raise RuntimeError(f"Missing input queue file: {INPUT_QUEUE_FILE}")

    queue = load_json_file(INPUT_QUEUE_FILE)

    if not isinstance(queue, list):
        raise RuntimeError(f"Input queue must be a list: {INPUT_QUEUE_FILE}")

    return [item for item in queue if isinstance(item, dict)]


def get_url_path_text(url):
    parsed = urlparse(url or "")
    return " ".join([
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
    ])


def score_candidate(item, subject_query):
    url = clean_text(item.get("url"))
    found_on = clean_text(item.get("found_on"))

    url_text = normalise_for_match(" ".join([url, get_url_path_text(url)]))
    found_on_text = normalise_for_match(found_on)
    combined_text = normalise_for_match(" ".join([url, found_on]))

    matched_terms = []
    score = 0

    for term, normalised_term in zip(subject_query["terms"], subject_query["normalised_terms"]):
        if not normalised_term:
            continue

        term_matched = False

        if normalised_term in url_text:
            score += 10
            term_matched = True

        if normalised_term in found_on_text:
            score += 3
            term_matched = True

        if normalised_term in combined_text:
            score += 1
            term_matched = True

        if term_matched:
            matched_terms.append(term)

    return score, matched_terms


def prioritise_queue(queue, subject_query):
    scored_items = []

    for original_index, item in enumerate(queue):
        score, matched_terms = score_candidate(item, subject_query)
        item_with_priority = dict(item)
        item_with_priority["subject_priority_score_v22"] = score
        item_with_priority["subject_priority_matched_terms_v22"] = matched_terms
        item_with_priority["subject_priority_original_index_v22"] = original_index
        scored_items.append(item_with_priority)

    return sorted(
        scored_items,
        key=lambda item: (
            item.get("filter_status") != "candidate",
            -int(item.get("subject_priority_score_v22", 0)),
            int(item.get("subject_priority_original_index_v22", 0)),
        )
    )


def build_report(subject_query, original_queue, prioritised_queue):
    candidate_items = [
        item for item in prioritised_queue
        if item.get("filter_status") == "candidate"
    ]
    skipped_items = [
        item for item in prioritised_queue
        if item.get("filter_status") != "candidate"
    ]
    subject_matching_candidates = [
        item for item in candidate_items
        if int(item.get("subject_priority_score_v22", 0)) > 0
    ]

    top_candidates = candidate_items[:3]

    return {
        "generated_at": utc_now_iso(),
        "subject": subject_query["subject"],
        "terms": subject_query["terms"],
        "network_requests_made": False,
        "input_queue_file": str(INPUT_QUEUE_FILE),
        "output_queue_file": str(OUTPUT_QUEUE_FILE),
        "original_queue_items": len(original_queue),
        "prioritised_queue_items": len(prioritised_queue),
        "candidate_items": len(candidate_items),
        "skipped_items": len(skipped_items),
        "subject_matching_candidates": len(subject_matching_candidates),
        "top_candidates_for_existing_fetch_limit": [
            {
                "url": item.get("url"),
                "score": item.get("subject_priority_score_v22"),
                "matched_terms": item.get("subject_priority_matched_terms_v22"),
                "original_index": item.get("subject_priority_original_index_v22"),
            }
            for item in top_candidates
        ],
        "subject_matching_candidate_urls": [
            {
                "url": item.get("url"),
                "score": item.get("subject_priority_score_v22"),
                "matched_terms": item.get("subject_priority_matched_terms_v22"),
                "original_index": item.get("subject_priority_original_index_v22"),
            }
            for item in subject_matching_candidates
        ],
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

    lines.append(f"# Subject Candidate Priority Report v2.2 — {report['subject']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report reorders already collected candidate URLs so subject-matching candidates are fetched first within the existing hard limits.")
    lines.append("")
    lines.append("No network requests are made by this prioritisation step.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(
        ["Metric", "Count"],
        [
            ["Original queue items", report["original_queue_items"]],
            ["Prioritised queue items", report["prioritised_queue_items"]],
            ["Candidate items", report["candidate_items"]],
            ["Skipped items", report["skipped_items"]],
            ["Subject-matching candidates", report["subject_matching_candidates"]],
            ["Network requests made", report["network_requests_made"]],
        ]
    ))
    lines.append("")
    lines.append("## Top candidates for existing fetch limit")
    lines.append("")

    if report["top_candidates_for_existing_fetch_limit"]:
        lines.append(markdown_table(
            ["URL", "Score", "Matched terms", "Original index"],
            [
                [
                    item["url"],
                    item["score"],
                    ", ".join(item.get("matched_terms") or []),
                    item["original_index"],
                ]
                for item in report["top_candidates_for_existing_fetch_limit"]
            ]
        ))
    else:
        lines.append("No candidate URLs were available.")

    lines.append("")
    lines.append("## Subject-matching candidate URLs")
    lines.append("")

    if report["subject_matching_candidate_urls"]:
        lines.append(markdown_table(
            ["URL", "Score", "Matched terms", "Original index"],
            [
                [
                    item["url"],
                    item["score"],
                    ", ".join(item.get("matched_terms") or []),
                    item["original_index"],
                ]
                for item in report["subject_matching_candidate_urls"]
            ]
        ))
    else:
        lines.append("No subject-matching candidate URLs were found in the filtered queue.")

    return "\n".join(lines) + "\n"


def main():
    print("Starting subject candidate prioritisation v2.2")
    print("No network requests will be made.")
    print("")

    try:
        subject_query = load_subject_query()
        queue = load_queue()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    prioritised_queue = prioritise_queue(queue, subject_query)
    report = build_report(subject_query, queue, prioritised_queue)
    markdown_report = build_markdown_report(report)

    save_json_file(OUTPUT_QUEUE_FILE, prioritised_queue)
    save_json_file(OUTPUT_JSON_REPORT_FILE, report)
    save_text_file(OUTPUT_MARKDOWN_REPORT_FILE, markdown_report)

    print("Final summary")
    print("-------------")
    print(f"Subject: {report['subject']}")
    print(f"Candidate items: {report['candidate_items']}")
    print(f"Subject-matching candidates: {report['subject_matching_candidates']}")
    print(f"Network requests made: {report['network_requests_made']}")
    print(f"Prioritised queue output: {OUTPUT_QUEUE_FILE}")
    print(f"Report output: {OUTPUT_MARKDOWN_REPORT_FILE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
