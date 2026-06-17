from collections import Counter
from pathlib import Path

import build_mp_voting_positions_v1 as base


base.MP_QUERY_FILE = Path("mp_query_corbyn_fixture.json")
base.DIVISION_RECORDS_FILE = Path("division_records_corbyn_fixture.json")
base.OUTPUT_JSON_FILE = Path("mp_voting_positions_corbyn_fixture_v12.json")
base.OUTPUT_MARKDOWN_FILE = Path("mp_voting_positions_corbyn_fixture_v12.md")

WEAK_EFFECT_MARKERS = [
    "new clause",
    "amendment",
    "remaining stages",
    "third reading",
]


def build_topic_counts(vote_positions):
    return Counter(item.get("topic") or "uncategorised" for item in vote_positions)


def is_weak_human_effect(text):
    lower_text = base.clean_text(text).lower()
    return any(marker in lower_text for marker in WEAK_EFFECT_MARKERS)


def add_human_effect_quality(report):
    needs_review = 0

    for item in report["vote_positions"]:
        if item["recorded_side"] not in {"Aye", "No"}:
            item["human_effect_quality"] = "not_applicable"
            continue

        if is_weak_human_effect(item["human_position"]):
            item["human_effect_quality"] = "needs_review"
            needs_review += 1
        else:
            item["human_effect_quality"] = "ready"

    report["human_effect_ready"] = len([
        item for item in report["vote_positions"]
        if item.get("human_effect_quality") == "ready"
    ])
    report["human_effect_needs_review"] = needs_review
    return report


def build_fixture_paragraph(report):
    mp_name = report["mp"]["mp_name"]

    if report.get("human_effect_needs_review", 0) > 0:
        return (
            f"Across the selected divisions checked in this fixture, {mp_name} has recorded votes that can be counted, "
            "but several human-readable vote meanings still need review because they refer to procedural labels such as new clauses or amendments. "
            "This fixture is useful for testing report shape and vote-side counting, but it is not yet strong enough to summarise a pattern of political priorities. "
            "It does not prove motive, private belief, or complete voting history."
        )

    return report["evidence_led_paragraph"].replace("supplied sample", "selected fixture")


def build_fixture_markdown(report):
    mp = report["mp"]
    topic_counts = build_topic_counts(report["vote_positions"])

    lines = []
    lines.append(f"# Long-serving MP Fixture Voting Positions Report — {mp['mp_name']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This fixture report uses selected official public division records only. It is not a complete voting history and it does not infer motive or private belief.")
    lines.append("")
    lines.append("## MP checked")
    lines.append("")
    lines.append(base.markdown_table(["Field", "Value"], [
        ["MP name", mp.get("mp_name", "")],
        ["Member ID", mp.get("member_id", "")],
        ["Constituency", mp.get("constituency", "")],
        ["Party", mp.get("party", "")],
    ]))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(base.markdown_table(["Metric", "Count"], [
        ["Selected divisions checked", report["divisions_checked"]],
        ["Recorded Aye positions", report["recorded_aye_positions"]],
        ["Recorded No positions", report["recorded_no_positions"]],
        ["Not recorded", report["not_recorded"]],
        ["Unable to determine", report["unable_to_determine"]],
        ["Human effects ready", report.get("human_effect_ready", 0)],
        ["Human effects needing review", report.get("human_effect_needs_review", 0)],
        ["Network requests made", report["network_requests_made"]],
    ]))
    lines.append("")
    lines.append("## Topic counts")
    lines.append("")
    lines.append(base.markdown_table(["Topic", "Selected divisions"], [
        [topic, count]
        for topic, count in topic_counts.most_common()
    ]))
    lines.append("")
    lines.append("## Evidence-led paragraph")
    lines.append("")
    lines.append(build_fixture_paragraph(report))
    lines.append("")
    lines.append("## Human-readable voting positions")
    lines.append("")
    lines.append(base.markdown_table(
        ["Date", "Division", "Topic", "Human-readable position", "Recorded side", "Meaning quality", "Source URL"],
        [
            [
                item["date"],
                item["division_number"],
                item["topic"],
                item["human_position"],
                item["recorded_side"],
                item.get("human_effect_quality", ""),
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
    lines.append("- It does not turn procedural labels into political meaning without review.")
    lines.append("- It only reports the selected official public division records checked in this fixture.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting long-serving MP fixture voting position report v1.2")
    print("No network requests will be made.")

    try:
        mp_query = base.load_mp_query()
        division_records = base.load_division_records()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    report = base.build_report(mp_query, division_records)
    report["fixture"] = "long_serving_mp_selected_divisions_v12"
    report["topic_counts"] = dict(build_topic_counts(report["vote_positions"]))
    report = add_human_effect_quality(report)

    base.save_json(base.OUTPUT_JSON_FILE, report)
    base.save_text(base.OUTPUT_MARKDOWN_FILE, build_fixture_markdown(report))

    print("Final summary")
    print("-------------")
    print(f"MP: {mp_query['mp_name']}")
    print(f"Selected divisions checked: {report['divisions_checked']}")
    print(f"Recorded Aye positions: {report['recorded_aye_positions']}")
    print(f"Recorded No positions: {report['recorded_no_positions']}")
    print(f"Not recorded: {report['not_recorded']}")
    print(f"Unable to determine: {report['unable_to_determine']}")
    print(f"Human effects ready: {report['human_effect_ready']}")
    print(f"Human effects needing review: {report['human_effect_needs_review']}")
    print(f"JSON output: {base.OUTPUT_JSON_FILE}")
    print(f"Markdown output: {base.OUTPUT_MARKDOWN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
