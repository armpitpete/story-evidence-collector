import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


MP_QUERY_FILE = Path("mp_query.json")
DIVISION_RECORDS_FILE = Path("division_records_sample.json")
OUTPUT_JSON_FILE = Path("mp_voting_positions_v1.json")
OUTPUT_MARKDOWN_FILE = Path("mp_voting_positions_v1.md")


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


def name_key(value):
    return clean_text(value).casefold()


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [clean_text(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_mp_query():
    data = load_json(MP_QUERY_FILE)
    mp_name = clean_text(data.get("mp_name"))
    if not mp_name:
        raise RuntimeError("mp_query.json must include mp_name.")
    return {
        "mp_name": mp_name,
        "member_id": clean_text(data.get("member_id")),
        "constituency": clean_text(data.get("constituency")),
        "party": clean_text(data.get("party")),
    }


def load_division_records():
    data = load_json(DIVISION_RECORDS_FILE)
    if not isinstance(data, list):
        raise RuntimeError("division_records_sample.json must contain a list.")
    return data


def list_contains_name(items, target_name):
    if not isinstance(items, list):
        return False
    target_key = name_key(target_name)
    return any(name_key(item) == target_key for item in items)


def classify_vote(record, mp_name):
    if not isinstance(record, dict):
        return {
            "recorded_side": "Unable to determine",
            "human_position": "Unable to determine because the division record is malformed.",
            "status": "malformed_record",
        }

    aye_members = record.get("aye_members")
    no_members = record.get("no_members")

    if not isinstance(aye_members, list) or not isinstance(no_members, list):
        return {
            "recorded_side": "Unable to determine",
            "human_position": "Unable to determine because the member lists are missing or malformed.",
            "status": "malformed_member_lists",
        }

    in_aye = list_contains_name(aye_members, mp_name)
    in_no = list_contains_name(no_members, mp_name)

    if in_aye and in_no:
        return {
            "recorded_side": "Unable to determine",
            "human_position": "Unable to determine because the MP appears in both recorded lists.",
            "status": "conflicting_member_lists",
        }

    if in_aye:
        return {
            "recorded_side": "Aye",
            "human_position": f"was recorded as {clean_text(record.get('plain_aye_effect')) or 'voting Aye'}",
            "status": "recorded_aye",
        }

    if in_no:
        return {
            "recorded_side": "No",
            "human_position": f"was recorded as {clean_text(record.get('plain_no_effect')) or 'voting No'}",
            "status": "recorded_no",
        }

    return {
        "recorded_side": "Not recorded",
        "human_position": "was not recorded in this division list",
        "status": "not_recorded",
    }


def build_vote_position(record, mp_query):
    result = classify_vote(record, mp_query["mp_name"])
    return {
        "date": clean_text(record.get("date")) if isinstance(record, dict) else "",
        "division_number": clean_text(record.get("division_number")) if isinstance(record, dict) else "",
        "motion_title": clean_text(record.get("motion_title")) if isinstance(record, dict) else "",
        "topic": clean_text(record.get("topic")) if isinstance(record, dict) else "",
        "source_url": clean_text(record.get("source_url")) if isinstance(record, dict) else "",
        "recorded_side": result["recorded_side"],
        "human_position": result["human_position"],
        "status": result["status"],
    }


def build_pattern_paragraph(mp_query, vote_positions):
    mp_name = mp_query["mp_name"]
    recorded_positions = [item for item in vote_positions if item["recorded_side"] in {"Aye", "No"}]

    if not recorded_positions:
        return (
            f"Across the divisions checked in this run, {mp_name} was not recorded as voting Aye or No in the supplied sample records. "
            "This is a summary of the supplied records only. It does not prove motive or personal belief."
        )

    topic_counts = Counter(item["topic"] or "uncategorised" for item in recorded_positions)
    side_counts = Counter(item["recorded_side"] for item in recorded_positions)
    strongest_topics = ", ".join([topic for topic, _count in topic_counts.most_common(3)])
    main_side = side_counts.most_common(1)[0][0]

    return (
        f"Across the divisions checked in this run, {mp_name} was most often recorded on the {main_side} side of the supplied division records. "
        f"The recorded positions most often appeared under these topic label(s): {strongest_topics}. "
        "This is a summary of recorded votes in the supplied sample only. It does not prove motive, private belief, or complete voting history."
    )


def build_report(mp_query, division_records):
    vote_positions = [build_vote_position(record, mp_query) for record in division_records]
    side_counts = Counter(item["recorded_side"] for item in vote_positions)

    return {
        "generated_at": utc_now_iso(),
        "scope_note": "This report turns supplied division records into human-readable voting positions. It does not claim complete voting history and does not infer motive or private belief.",
        "network_requests_made": False,
        "mp": mp_query,
        "divisions_checked": len(division_records),
        "recorded_aye_positions": side_counts.get("Aye", 0),
        "recorded_no_positions": side_counts.get("No", 0),
        "not_recorded": side_counts.get("Not recorded", 0),
        "unable_to_determine": side_counts.get("Unable to determine", 0),
        "evidence_led_paragraph": build_pattern_paragraph(mp_query, vote_positions),
        "vote_positions": vote_positions,
    }


def build_markdown(report):
    mp = report["mp"]
    lines = []
    lines.append(f"# MP Voting Positions Report — {mp['mp_name']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(report["scope_note"])
    lines.append("")
    lines.append("## MP checked")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["MP name", mp.get("mp_name", "")],
        ["Member ID", mp.get("member_id", "")],
        ["Constituency", mp.get("constituency", "")],
        ["Party", mp.get("party", "")],
    ]))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count"], [
        ["Divisions checked", report["divisions_checked"]],
        ["Recorded Aye positions", report["recorded_aye_positions"]],
        ["Recorded No positions", report["recorded_no_positions"]],
        ["Not recorded", report["not_recorded"]],
        ["Unable to determine", report["unable_to_determine"]],
        ["Network requests made", report["network_requests_made"]],
    ]))
    lines.append("")
    lines.append("## Evidence-led paragraph")
    lines.append("")
    lines.append(report["evidence_led_paragraph"])
    lines.append("")
    lines.append("## Human-readable voting positions")
    lines.append("")
    lines.append(markdown_table(
        ["Date", "Division", "Topic", "Human-readable position", "Recorded side", "Source URL"],
        [
            [
                item["date"],
                item["division_number"],
                item["topic"],
                item["human_position"],
                item["recorded_side"],
                item["source_url"],
            ]
            for item in report["vote_positions"]
        ],
    ))
    lines.append("")
    lines.append("## What this report does not prove")
    lines.append("")
    lines.append("- It does not prove motive or private belief.")
    lines.append("- It does not prove complete voting history.")
    lines.append("- It does not explain why the MP was not recorded in any division list.")
    lines.append("- It only reports the supplied division records checked in this run.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting MP voting position report v1")
    print("No network requests will be made.")
    try:
        mp_query = load_mp_query()
        division_records = load_division_records()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    report = build_report(mp_query, division_records)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))

    print("Final summary")
    print("-------------")
    print(f"MP: {mp_query['mp_name']}")
    print(f"Divisions checked: {report['divisions_checked']}")
    print(f"Recorded Aye positions: {report['recorded_aye_positions']}")
    print(f"Recorded No positions: {report['recorded_no_positions']}")
    print(f"Not recorded: {report['not_recorded']}")
    print(f"Unable to determine: {report['unable_to_determine']}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
