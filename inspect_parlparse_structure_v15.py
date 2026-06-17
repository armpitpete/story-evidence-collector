import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


INPUT_FILE = Path("parlparse_source_probe_v15.json")
OUTPUT_JSON_FILE = Path("parlparse_structure_report_v15.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_structure_report_v15.md")

USER_AGENT = "StoryEvidenceCollector/ParlParseProbe/1.5"
REQUEST_TIMEOUT_SECONDS = 20

SIGNAL_RULES = [
    {
        "signal": "structured_public_parliament_data",
        "patterns": [
            "Structured versions of publicly available data from the UK parliament",
            "source code that was used to generate the data",
        ],
    },
    {
        "signal": "engine_for_twf_publicwhip",
        "patterns": [
            "engine",
            "TheyWorkForYou",
            "Public Whip",
        ],
    },
    {
        "signal": "debate_xml_has_divisions_and_votes",
        "patterns": [
            "XML files containing Debates",
            "divisions and how each MP or Lord voted",
        ],
    },
    {
        "signal": "commons_debate_xml_starts_2001",
        "patterns": [
            "start of the 2001 parliament",
        ],
    },
    {
        "signal": "members_have_stable_identifiers",
        "patterns": [
            "unique identifier",
            "person_id",
            "member",
        ],
    },
    {
        "signal": "members_data_goes_back_to_19th_century",
        "patterns": [
            "MP data goes back to the start of Hansard at the start of the 19th century",
        ],
    },
    {
        "signal": "voting_record_points_to_public_whip",
        "patterns": [
            "Voting Record",
            "Public Whip project",
        ],
    },
    {
        "signal": "data_browsing_available",
        "patterns": [
            "browse the list of available files",
        ],
    },
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


def fetch_text(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="replace")


def strip_html(text):
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return clean_text(text)


def find_signals(page_text):
    lowered = page_text.lower()
    found = []
    for rule in SIGNAL_RULES:
        if all(pattern.lower() in lowered for pattern in rule["patterns"]):
            found.append(rule["signal"])
    return found


def probe_sources(config):
    events = []
    signals = set()
    allow_network = bool(config.get("allow_network_probe", False))
    max_requests = int(config.get("max_source_requests", 5))

    if not allow_network:
        return events, signals

    for index, item in enumerate(config.get("probe_urls", [])[:max_requests], start=1):
        url = clean_text(item.get("url"))
        label = clean_text(item.get("label"))
        if not url:
            continue

        try:
            page_text = strip_html(fetch_text(url))
            page_signals = find_signals(page_text)
            signals.update(page_signals)
            events.append({
                "index": index,
                "label": label,
                "url": url,
                "status": "ok",
                "characters_read": len(page_text),
                "signals": page_signals,
            })
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as error:
            events.append({
                "index": index,
                "label": label,
                "url": url,
                "status": "failed",
                "error": str(error),
                "signals": [],
            })

    return events, signals


def answer_questions(config, signals):
    signal_set = set(signals)
    answers = []

    answers.append({
        "question": "Does the source expose structured division/vote records?",
        "answer": "Partly. ParlParse Hansard XML appears to include divisions and how each MP or Lord voted, but only from the start of the 2001 Commons parliament according to the inspected source notes.",
        "status": "partial_yes",
        "supporting_signals": ["debate_xml_has_divisions_and_votes", "commons_debate_xml_starts_2001"],
    })
    answers.append({
        "question": "Does it cover pre-2016?",
        "answer": "Yes, for Commons debate XML from 2001 onward. That can help with 2001-2016 but does not solve 1983-2001.",
        "status": "partial_yes",
        "supporting_signals": ["commons_debate_xml_starts_2001"],
    })
    answers.append({
        "question": "Does it go back to the 1983 start point needed for Corbyn?",
        "answer": "Not for the inspected Commons debate XML route. Member metadata goes back much further, but vote/division XML coverage is reported from 2001 for Commons debates.",
        "status": "no_for_vote_rows",
        "supporting_signals": ["members_data_goes_back_to_19th_century", "commons_debate_xml_starts_2001"],
    })
    answers.append({
        "question": "Can Jeremy Corbyn be matched by stable person/member ID?",
        "answer": "Likely yes. The members data describes stable unique identifiers, person IDs and membership IDs. A later issue should resolve the exact ParlParse/Public Whip person/member ID for Corbyn before extracting votes.",
        "status": "likely_yes_needs_exact_id_resolution",
        "supporting_signals": ["members_have_stable_identifiers"],
    })
    answers.append({
        "question": "Can future rows be traced to a source URL or source identifier?",
        "answer": "Likely yes for XML-derived debate/division rows, because the Hansard examples include IDs and source URLs. This still needs a sample file inspection before merging.",
        "status": "likely_yes_needs_sample_file",
        "supporting_signals": ["debate_xml_has_divisions_and_votes"],
    })
    answers.append({
        "question": "What licence or attribution notes must be kept?",
        "answer": "Keep mySociety / TheyWorkForYou / Public Whip attribution and inspect the repository/source licence before publishing derived historic data. Do not publish large raw extracts by default.",
        "status": "needs_licence_check",
        "supporting_signals": ["engine_for_twf_publicwhip"],
    })
    answers.append({
        "question": "Is ParlParse enough on its own for full 1983-2016 coverage?",
        "answer": "No, not based on this source-shape probe. It appears useful for 2001-2016 Commons debate XML vote rows, while the 1983-2001 gap likely needs Public Whip historic records or another official/archive route.",
        "status": "no",
        "supporting_signals": ["voting_record_points_to_public_whip", "commons_debate_xml_starts_2001"],
    })

    for answer in answers:
        answer["signals_present"] = all(signal in signal_set for signal in answer.get("supporting_signals", []))
    return answers


def verdict_from_answers(answers):
    return {
        "suitable_for_future_merge": "partial",
        "best_next_step": "Inspect one or two actual ParlParse scrapedxml/debates XML files containing divisions, then resolve Jeremy Corbyn's ParlParse/Public Whip member ID. Treat this as 2001-2016 coverage only until older source data is found.",
        "coverage_assessment": "Likely useful for 2001-2016. Not enough for 1983-2001 based on this probe.",
        "merge_now": False,
    }


def build_report(config, events, signals):
    answers = answer_questions(config, signals)
    return {
        "generated_at": utc_now_iso(),
        "source_id": config.get("source_id", ""),
        "source_url": config.get("source_url", ""),
        "target_mp": config.get("target_mp", ""),
        "target_member_id": config.get("target_member_id", ""),
        "wanted_date_range": config.get("wanted_date_range", {}),
        "max_source_requests": config.get("max_source_requests", 5),
        "network_requests_made": bool(events),
        "source_events": events,
        "signals_found": sorted(signals),
        "answers": answers,
        "verdict": verdict_from_answers(answers),
    }


def build_markdown(report):
    verdict = report.get("verdict", {})
    lines = []
    lines.append("# ParlParse Structure Report v1.5")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report inspects the source shape only. It does not merge historic votes, publish raw datasets, crawl recursively, or claim full-career coverage.")
    lines.append("")
    lines.append("## Target")
    lines.append("")
    date_range = report.get("wanted_date_range", {})
    lines.append(markdown_table(["Field", "Value"], [
        ["Source ID", report.get("source_id", "")],
        ["Source URL", report.get("source_url", "")],
        ["Target MP", report.get("target_mp", "")],
        ["Target member ID", report.get("target_member_id", "")],
        ["Wanted date range", f"{date_range.get('start', '')} to {date_range.get('end', '')}"],
        ["Network requests made", report.get("network_requests_made", False)],
        ["Max source requests", report.get("max_source_requests", "")],
    ]))
    lines.append("")
    lines.append("## Source events")
    lines.append("")
    lines.append(markdown_table(
        ["Index", "Label", "Status", "Signals", "URL", "Error"],
        [
            [
                event.get("index", ""),
                event.get("label", ""),
                event.get("status", ""),
                ", ".join(event.get("signals", [])),
                event.get("url", ""),
                event.get("error", ""),
            ]
            for event in report.get("source_events", [])
        ],
    ))
    lines.append("")
    lines.append("## Signals found")
    lines.append("")
    for signal in report.get("signals_found", []):
        lines.append(f"- `{signal}`")
    lines.append("")
    lines.append("## Inspection answers")
    lines.append("")
    lines.append(markdown_table(
        ["Question", "Status", "Answer"],
        [
            [answer.get("question", ""), answer.get("status", ""), answer.get("answer", "")]
            for answer in report.get("answers", [])
        ],
    ))
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Suitable for future merge", verdict.get("suitable_for_future_merge", "")],
        ["Merge now", verdict.get("merge_now", False)],
        ["Coverage assessment", verdict.get("coverage_assessment", "")],
        ["Best next step", verdict.get("best_next_step", "")],
    ]))
    lines.append("")
    lines.append("## What this report decides")
    lines.append("")
    lines.append("- ParlParse is useful, but likely only solves part of the missing historic range for vote rows.")
    lines.append("- The inspected Commons debate XML route appears useful from 2001 onward, not 1983 onward.")
    lines.append("- Member identifiers appear usable, but the exact Corbyn ParlParse/Public Whip ID still needs resolving.")
    lines.append("- The next issue should inspect actual XML sample files before building a merger.")
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge historic votes into the MP vote index.")
    lines.append("- It does not solve the 1983-2001 gap.")
    lines.append("- It does not publish raw historic vote data.")
    lines.append("- It does not infer human political meaning from votes.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting ParlParse structure inspection v1.5")
    config = load_json(INPUT_FILE)
    events, signals = probe_sources(config)
    report = build_report(config, events, signals)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Source events: {len(events)}")
    print(f"Signals found: {len(signals)}")
    print(f"Suitable for future merge: {report['verdict']['suitable_for_future_merge']}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
