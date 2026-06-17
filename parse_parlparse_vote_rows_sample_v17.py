import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


INPUT_FILE = Path("parlparse_vote_row_sample_query_v17.json")
OUTPUT_JSON_FILE = Path("parlparse_vote_rows_sample_v17.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_vote_rows_sample_v17.md")

USER_AGENT = "StoryEvidenceCollector/ParlParseVoteRows/1.7"
REQUEST_TIMEOUT_SECONDS = 30


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


def local_name(tag):
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def element_text(element):
    return clean_text(" ".join(element.itertext()))


def target_variants(target_mp):
    target = clean_text(target_mp)
    variants = set()
    if target:
        variants.add(target.casefold())
    if "," in target:
        last, first = [part.strip() for part in target.split(",", 1)]
        if first and last:
            variants.add(f"{first} {last}".casefold())
        if last:
            variants.add(last.casefold())
    return {variant for variant in variants if variant}


def text_matches_target(text, variants):
    lowered = clean_text(text).casefold()
    if not lowered:
        return False
    return any(variant in lowered for variant in variants)


def is_division_element(element):
    return local_name(element.tag).lower() == "division"


def infer_side_from_element(element):
    parts = [local_name(element.tag)]
    for key, value in element.attrib.items():
        parts.append(clean_text(key))
        parts.append(clean_text(value))
    joined = " ".join(parts).casefold()

    if re.search(r"\b(aye|ayes|content|telleraye|tellerayes)\b", joined):
        return "Aye"
    if re.search(r"\b(no|noes|not-content|against|tellerno|tellernoes)\b", joined):
        return "No"
    return ""


def find_target_side_in_division(division, target_mp):
    variants = target_variants(target_mp)
    sides_found = set()
    target_found = False

    for list_element in division.iter():
        tag = local_name(list_element.tag).lower()
        possible_side = infer_side_from_element(list_element)

        if tag != "mplist" and not possible_side:
            continue

        list_text = element_text(list_element)
        if text_matches_target(list_text, variants):
            target_found = True
            if possible_side:
                sides_found.add(possible_side)

    if len(sides_found) == 1:
        side = next(iter(sides_found))
        if side == "Aye":
            return "Aye", "mp_found_in_aye_list"
        if side == "No":
            return "No", "mp_found_in_no_list"

    if len(sides_found) > 1:
        return "Unable to determine", "mp_found_in_multiple_side_lists"

    if target_found:
        return "Unable to determine", "mp_found_but_side_unclear"

    return "Not recorded", "mp_not_found_in_sample_division"


def normalise_source_url(xml_url, division):
    attr_url = clean_text(division.attrib.get("url"))
    if attr_url:
        return urljoin(xml_url, attr_url)
    division_id = clean_text(division.attrib.get("id"))
    if division_id:
        return f"{xml_url}#{division_id}"
    return xml_url


def motion_title_from_nearby_context(division):
    title = clean_text(division.attrib.get("title"))
    if title:
        return title

    divnumber = clean_text(division.attrib.get("divnumber"))
    divdate = clean_text(division.attrib.get("divdate"))
    if divnumber or divdate:
        return f"ParlParse division {divnumber} on {divdate}".strip()
    return "ParlParse division"


def parse_division_to_row(xml_url, division, config):
    recorded_side, evidence_status = find_target_side_in_division(division, config.get("target_mp", ""))
    return {
        "date": clean_text(division.attrib.get("divdate")),
        "division_id": clean_text(division.attrib.get("id")),
        "division_number": clean_text(division.attrib.get("divnumber")),
        "motion_title": motion_title_from_nearby_context(division),
        "recorded_side": recorded_side,
        "meaning_quality": clean_text(config.get("meaning_quality")) or "needs_review",
        "topic": clean_text(config.get("topic")) or "uncategorised",
        "source_url": normalise_source_url(xml_url, division),
        "source_system": clean_text(config.get("source_system")) or "parlparse",
        "evidence_status": evidence_status,
        "source_xml_url": xml_url,
        "available_trace_fields": sorted(division.attrib.keys()),
    }


def parse_xml_file(xml_url, xml_text, config):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as error:
        return [], {
            "xml_url": xml_url,
            "status": "parse_failed",
            "error": str(error),
            "division_elements_found": 0,
            "rows_produced": 0,
        }

    divisions = [element for element in root.iter() if is_division_element(element)]
    rows = [parse_division_to_row(xml_url, division, config) for division in divisions]
    return rows, {
        "xml_url": xml_url,
        "status": "ok",
        "division_elements_found": len(divisions),
        "rows_produced": len(rows),
        "characters_read": len(xml_text),
    }


def build_sample(config):
    if not bool(config.get("allow_network_probe", False)):
        return [], [{"status": "network_disabled"}]

    rows = []
    source_events = []
    xml_files = config.get("xml_files", [])[: int(config.get("max_xml_files", 2))]

    for index, xml_url in enumerate(xml_files, start=1):
        try:
            xml_text = fetch_text(xml_url)
            file_rows, event = parse_xml_file(xml_url, xml_text, config)
            rows.extend(file_rows)
            event["index"] = index
            event["fetch_status"] = "ok"
            source_events.append(event)
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as error:
            source_events.append({
                "index": index,
                "xml_url": xml_url,
                "status": "fetch_failed",
                "fetch_status": "failed",
                "error": str(error),
                "division_elements_found": 0,
                "rows_produced": 0,
            })

    return rows, source_events


def field_missing_counts(rows):
    fields = [
        "date",
        "division_id",
        "division_number",
        "motion_title",
        "recorded_side",
        "source_url",
        "source_system",
        "evidence_status",
    ]
    return {field: len([row for row in rows if not clean_text(row.get(field))]) for field in fields}


def build_report(config, rows, source_events):
    side_counts = Counter(row.get("recorded_side", "") for row in rows)
    evidence_counts = Counter(row.get("evidence_status", "") for row in rows)
    missing_counts = field_missing_counts(rows)

    return {
        "generated_at": utc_now_iso(),
        "purpose": config.get("purpose", ""),
        "target_mp": config.get("target_mp", ""),
        "target_member_id": config.get("target_member_id", ""),
        "network_requests_made": bool(source_events),
        "xml_files_requested": len(config.get("xml_files", [])[: int(config.get("max_xml_files", 2))]),
        "rows_produced": len(rows),
        "recorded_aye": side_counts.get("Aye", 0),
        "recorded_no": side_counts.get("No", 0),
        "not_recorded": side_counts.get("Not recorded", 0),
        "unable_to_determine": side_counts.get("Unable to determine", 0),
        "evidence_status_counts": dict(evidence_counts),
        "field_missing_counts": missing_counts,
        "source_events": source_events,
        "rows": rows,
        "merge_now": False,
        "coverage_note": "This is a bounded ParlParse XML sample parser. It does not claim full historic coverage and does not merge with the main MP vote index.",
    }


def build_markdown(report):
    lines = []
    lines.append(f"# ParlParse Vote Rows Sample v1.7 — {report.get('target_mp', '')}")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(report.get("coverage_note", ""))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count / value"], [
        ["Target MP", report.get("target_mp", "")],
        ["Target member ID", report.get("target_member_id", "")],
        ["XML files requested", report.get("xml_files_requested", 0)],
        ["Rows produced", report.get("rows_produced", 0)],
        ["Recorded Aye", report.get("recorded_aye", 0)],
        ["Recorded No", report.get("recorded_no", 0)],
        ["Not recorded", report.get("not_recorded", 0)],
        ["Unable to determine", report.get("unable_to_determine", 0)],
        ["Merge now", report.get("merge_now", False)],
        ["Network requests made", report.get("network_requests_made", False)],
    ]))
    lines.append("")
    lines.append("## Source events")
    lines.append("")
    lines.append(markdown_table(
        ["Index", "Status", "Divisions found", "Rows produced", "XML URL", "Error"],
        [
            [
                event.get("index", ""),
                event.get("status", ""),
                event.get("division_elements_found", 0),
                event.get("rows_produced", 0),
                event.get("xml_url", ""),
                event.get("error", ""),
            ]
            for event in report.get("source_events", [])
        ],
    ))
    lines.append("")
    lines.append("## Evidence status counts")
    lines.append("")
    lines.append(markdown_table(["Evidence status", "Rows"], report.get("evidence_status_counts", {}).items()))
    lines.append("")
    lines.append("## Missing field counts")
    lines.append("")
    lines.append(markdown_table(["Field", "Rows missing value"], report.get("field_missing_counts", {}).items()))
    lines.append("")
    lines.append("## Vote rows")
    lines.append("")
    lines.append(markdown_table(
        ["Date", "Division ID", "Division no.", "Motion title", "Recorded side", "Source URL", "Evidence status"],
        [
            [
                row.get("date", ""),
                row.get("division_id", ""),
                row.get("division_number", ""),
                row.get("motion_title", ""),
                row.get("recorded_side", ""),
                row.get("source_url", ""),
                row.get("evidence_status", ""),
            ]
            for row in report.get("rows", [])
        ],
    ))
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge rows into the main MP vote index.")
    lines.append("- It does not claim full historic coverage.")
    lines.append("- It does not publish raw XML extracts.")
    lines.append("- It does not infer human political meaning from vote titles.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting bounded ParlParse XML vote row parser v1.7")
    config = load_json(INPUT_FILE)
    rows, source_events = build_sample(config)
    report = build_report(config, rows, source_events)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"Rows produced: {report['rows_produced']}")
    print(f"Recorded Aye: {report['recorded_aye']}")
    print(f"Recorded No: {report['recorded_no']}")
    print(f"Not recorded: {report['not_recorded']}")
    print(f"Unable to determine: {report['unable_to_determine']}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
