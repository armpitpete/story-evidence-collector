import json
from pathlib import Path


INPUT_JSON_FILE = Path("subject_matches_v21.json")
OUTPUT_MARKDOWN_FILE = Path("subject_matches_v21.md")
MAX_EXCERPTS_PER_PAGE = 3
EXCERPT_RADIUS = 190


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_text(path, text):
    with path.open("w", encoding="utf-8") as file:
        file.write(text)


def clean_text(value):
    if not value:
        return ""
    return " ".join(str(value).split())


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [clean_text(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def find_positions(text, terms):
    text_lower = text.lower()
    positions = []
    for term in terms:
        term_lower = term.lower()
        start = 0
        while True:
            pos = text_lower.find(term_lower, start)
            if pos < 0:
                break
            positions.append({"term": term, "position": pos})
            start = pos + max(len(term_lower), 1)
    return sorted(positions, key=lambda item: item["position"])


def excerpt_at(text, position):
    start = max(0, position - EXCERPT_RADIUS)
    end = min(len(text), position + EXCERPT_RADIUS)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt += "…"
    return excerpt


def score_excerpt(excerpt, terms, subject):
    excerpt_lower = excerpt.lower()
    score = 0
    for term in terms:
        if term.lower() in excerpt_lower:
            score += 2
    if subject.lower() in excerpt_lower:
        score += 4
    return score


def get_match_text(match):
    parts = [
        match.get("page_title"),
        match.get("relevant_excerpt"),
        match.get("url"),
        match.get("source_url"),
        match.get("final_url"),
    ]
    return clean_text(" ".join([str(part) for part in parts if part]))


def strongest_excerpts(match, subject):
    terms = match.get("matched_terms") or []
    text = get_match_text(match)
    positions = find_positions(text, terms)
    excerpts = []
    seen = set()
    for item in positions:
        excerpt = excerpt_at(text, item["position"])
        key = excerpt.lower()
        if key in seen:
            continue
        seen.add(key)
        excerpts.append({
            "excerpt": excerpt,
            "score": score_excerpt(excerpt, terms, subject),
            "near_term": item["term"],
        })
    excerpts.sort(key=lambda item: (-item["score"], item["near_term"].lower()))
    return excerpts[:MAX_EXCERPTS_PER_PAGE]


def page_note(match):
    matched_terms = match.get("matched_terms") or []
    if not match.get("fetched_successfully"):
        return "This record matched the subject terms, but the page was not fetched successfully in this run."
    if len(matched_terms) >= 4:
        return "This fetched page contains several subject terms and is the strongest collected page for this subject in this run."
    if len(matched_terms) >= 2:
        return "This fetched page contains the subject terms and appears relevant to the subject."
    return "This fetched page contains at least one subject term; read the excerpt before treating it as strong evidence."


def plain_answer(report):
    subject = report.get("subject", "the subject")
    matches = report.get("matches") or []
    fetched = [match for match in matches if match.get("fetched_successfully")]
    strong = [match for match in fetched if len(match.get("matched_terms") or []) >= 3]
    if not matches:
        return f"The collected pages for this run did not contain matches for {subject}."
    if strong:
        titles = "; ".join([match.get("page_title", "Untitled page") for match in strong[:3]])
        return f"The collected pages include fetched page(s) that directly match {subject}. The strongest match is: {titles}."
    if fetched:
        titles = "; ".join([match.get("page_title", "Untitled page") for match in fetched[:3]])
        return f"The collected pages include fetched page(s) that mention {subject}. Matching page(s): {titles}."
    return f"The collected records mention {subject}, but no fetched page in this run gave a strong readable match."


def build_markdown(report):
    subject = report.get("subject", "Subject")
    matches = report.get("matches") or []
    lines = []
    lines.append(f"# Subject Evidence Summary — {subject}")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Plain-English answer")
    lines.append("")
    lines.append(plain_answer(report))
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report finds matching information inside the collected public pages for this run. It does not claim to find all information on the internet.")
    lines.append("")
    lines.append("## Search terms")
    lines.append("")
    lines.append(", ".join([f"`{term}`" for term in report.get("terms", [])]))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(table(["Metric", "Count"], [
        ["Records scanned", report.get("records_scanned", 0)],
        ["Matches found", report.get("matches_found", 0)],
        ["Fetched successful matches", report.get("fetched_matches", 0)],
        ["Unfetched/error matches", report.get("unfetched_or_error_matches", 0)],
        ["Network requests made by this report", report.get("network_requests_made", False)],
    ]))
    lines.append("")
    lines.append("## Matched pages")
    lines.append("")
    if matches:
        lines.append(table(["Page title", "URL", "Matched terms", "Stage", "Fetched"], [
            [
                match.get("page_title", "Untitled page"),
                match.get("url", ""),
                ", ".join(match.get("matched_terms") or []),
                match.get("pipeline_stage", ""),
                match.get("fetched_successfully", False),
            ]
            for match in matches
        ]))
    else:
        lines.append("No matching collected pages were found for this subject.")
    lines.append("")
    lines.append("## Strongest excerpts")
    lines.append("")
    if not matches:
        lines.append("No excerpts are available because no matching pages were found.")
        lines.append("")
    for index, match in enumerate(matches, start=1):
        lines.append(f"### {index}. {match.get('page_title', 'Untitled page')}")
        lines.append("")
        lines.append(f"URL: `{match.get('url', '')}`")
        lines.append("")
        lines.append(f"Stage: `{match.get('pipeline_stage', '')}`")
        lines.append("")
        lines.append(f"Fetched successfully: `{match.get('fetched_successfully', False)}`")
        lines.append("")
        lines.append(f"Matched terms: {', '.join([f'`{term}`' for term in match.get('matched_terms', [])])}")
        lines.append("")
        lines.append(f"What this page says about the subject: {page_note(match)}")
        lines.append("")
        excerpts = strongest_excerpts(match, subject)
        if excerpts:
            for excerpt_index, item in enumerate(excerpts, start=1):
                lines.append(f"**Excerpt {excerpt_index}:**")
                lines.append("")
                lines.append(item["excerpt"])
                lines.append("")
        else:
            lines.append("No readable excerpt was available for this match.")
            lines.append("")
    lines.append("## What this run proves")
    lines.append("")
    lines.append(f"- This run found {report.get('matches_found', 0)} collected page record(s) matching {subject}.")
    lines.append(f"- Of those, {report.get('fetched_matches', 0)} page record(s) were fetched successfully and had readable extracted text.")
    lines.append("- The listed excerpts show where the subject terms appeared in the collected page text.")
    lines.append("")
    lines.append("## What this run does not prove")
    lines.append("")
    lines.append("- It does not prove that every relevant page on the internet has been found.")
    lines.append("- It does not prove that every claim in a fetched page is true.")
    lines.append("- It does not prove that unfetched or skipped pages are irrelevant.")
    lines.append(f"- It only reports what the collected public pages for this run contained about {subject}.")
    lines.append("")
    lines.append("## Input files")
    lines.append("")
    lines.append(table(["File", "Stage", "Loaded", "Records", "Status"], [
        [
            item.get("filename", ""),
            item.get("stage", ""),
            item.get("loaded", False),
            item.get("record_count", 0),
            item.get("status", ""),
        ]
        for item in report.get("input_files", [])
    ]))
    return "\n".join(lines) + "\n"


def main():
    print("Starting subject report improvement v2.4")
    print("No network requests will be made.")
    report = load_json(INPUT_JSON_FILE)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Subject: {report.get('subject')}")
    print(f"Matches found: {report.get('matches_found')}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
