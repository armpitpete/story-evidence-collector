import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


INPUT_FILE = Path("parlparse_xml_sample_probe_v16.json")
OUTPUT_JSON_FILE = Path("parlparse_xml_sample_report_v16.json")
OUTPUT_MARKDOWN_FILE = Path("parlparse_xml_sample_report_v16.md")

USER_AGENT = "StoryEvidenceCollector/ParlParseXMLProbe/1.6"
REQUEST_TIMEOUT_SECONDS = 30
MAX_RAW_EXCERPT_CHARS = 260


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


def extract_xml_links(index_url, html):
    links = []
    for href in re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        if href.lower().endswith(".xml"):
            links.append(urljoin(index_url, href))
    return sorted(set(links))


def choose_xml_candidates(config, discovered_links):
    patterns = [clean_text(pattern) for pattern in config.get("preferred_filename_patterns", []) if clean_text(pattern)]
    chosen = []

    for pattern in patterns:
        for link in discovered_links:
            if pattern in link and link not in chosen:
                chosen.append(link)
                break

    for link in discovered_links:
        if len(chosen) >= int(config.get("max_xml_requests", 2)):
            break
        if link not in chosen:
            chosen.append(link)

    return chosen[: int(config.get("max_xml_requests", 2))]


def local_name(tag):
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def element_text(element):
    return clean_text(" ".join(element.itertext()))


def parse_xml_safely(xml_text):
    try:
        return ET.fromstring(xml_text), "ok", ""
    except ET.ParseError as error:
        return None, "parse_failed", str(error)


def is_division_element(element):
    tag = local_name(element.tag).lower()
    attrs = " ".join([clean_text(key) + " " + clean_text(value) for key, value in element.attrib.items()]).lower()
    if "division" in tag:
        return True
    if "division" in attrs:
        return True
    return False


def vote_side_from_text_or_attrs(element):
    joined = " ".join(
        [local_name(element.tag)]
        + [clean_text(key) for key in element.attrib.keys()]
        + [clean_text(value) for value in element.attrib.values()]
        + [element_text(element)]
    ).lower()

    if re.search(r"\b(aye|ayes|content|for)\b", joined):
        return "Aye-like"
    if re.search(r"\b(no|noes|not-content|against)\b", joined):
        return "No-like"
    return ""


def inspect_division_element(element):
    children = list(element)
    child_tags = sorted({local_name(child.tag) for child in children})[:20]
    attr_keys = sorted(element.attrib.keys())
    text = element_text(element)
    vote_indicators = []

    for descendant in element.iter():
        side = vote_side_from_text_or_attrs(descendant)
        if side and side not in vote_indicators:
            vote_indicators.append(side)

    possible_name_count = 0
    possible_id_count = 0
    for descendant in element.iter():
        attrs = descendant.attrib
        if any("name" in key.lower() for key in attrs.keys()):
            possible_name_count += 1
        if any("id" in key.lower() for key in attrs.keys()):
            possible_id_count += 1

    return {
        "tag": local_name(element.tag),
        "attribute_keys": attr_keys,
        "child_tags": child_tags,
        "vote_indicators": vote_indicators,
        "possible_name_attribute_elements": possible_name_count,
        "possible_id_attribute_elements": possible_id_count,
        "text_excerpt": text[:MAX_RAW_EXCERPT_CHARS],
    }


def inspect_xml(xml_url, xml_text, target_mp):
    root, parse_status, parse_error = parse_xml_safely(xml_text)
    if root is None:
        return {
            "xml_url": xml_url,
            "status": parse_status,
            "parse_error": parse_error,
            "characters_read": len(xml_text),
            "division_like_count": 0,
            "corbyn_mentioned": "corbyn" in xml_text.lower(),
            "sample_divisions": [],
        }

    division_like = [element for element in root.iter() if is_division_element(element)]
    sample_divisions = [inspect_division_element(element) for element in division_like[:3]]

    lower_text = xml_text.lower()
    target_present = clean_text(target_mp).split(",", 1)[0].lower() in lower_text if target_mp else False
    has_vote_indicators = any(item["vote_indicators"] for item in sample_divisions)
    has_source_trace = any(
        any(key.lower() in {"id", "gid", "url", "source", "oldstyleid"} for key in item["attribute_keys"])
        for item in sample_divisions
    )

    return {
        "xml_url": xml_url,
        "status": "ok",
        "characters_read": len(xml_text),
        "root_tag": local_name(root.tag),
        "division_like_count": len(division_like),
        "target_name_mentioned": target_present,
        "has_vote_indicators_in_samples": has_vote_indicators,
        "has_source_trace_in_samples": has_source_trace,
        "sample_divisions": sample_divisions,
    }


def inspect_sources(config):
    events = []
    discovered_links = []
    allow_network = bool(config.get("allow_network_probe", False))

    if not allow_network:
        return events, [], []

    for index, item in enumerate(config.get("index_urls", [])[: int(config.get("max_index_requests", 2))], start=1):
        url = clean_text(item.get("url"))
        label = clean_text(item.get("label"))
        try:
            html = fetch_text(url)
            xml_links = extract_xml_links(url, html)
            discovered_links.extend(xml_links)
            events.append({
                "stage": "index_fetch",
                "index": index,
                "label": label,
                "url": url,
                "status": "ok",
                "xml_links_found": len(xml_links),
            })
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as error:
            events.append({
                "stage": "index_fetch",
                "index": index,
                "label": label,
                "url": url,
                "status": "failed",
                "error": str(error),
                "xml_links_found": 0,
            })

    xml_candidates = choose_xml_candidates(config, sorted(set(discovered_links)))
    xml_reports = []

    for index, xml_url in enumerate(xml_candidates, start=1):
        try:
            xml_text = fetch_text(xml_url)
            xml_reports.append(inspect_xml(xml_url, xml_text, config.get("target_mp", "")))
            events.append({
                "stage": "xml_fetch",
                "index": index,
                "url": xml_url,
                "status": "ok",
                "characters_read": len(xml_text),
            })
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as error:
            xml_reports.append({
                "xml_url": xml_url,
                "status": "failed",
                "error": str(error),
                "division_like_count": 0,
                "sample_divisions": [],
            })
            events.append({
                "stage": "xml_fetch",
                "index": index,
                "url": xml_url,
                "status": "failed",
                "error": str(error),
            })

    return events, sorted(set(discovered_links)), xml_reports


def verdict(xml_reports):
    ok_reports = [report for report in xml_reports if report.get("status") == "ok"]
    any_divisions = any(report.get("division_like_count", 0) > 0 for report in ok_reports)
    any_vote_indicators = any(report.get("has_vote_indicators_in_samples") for report in ok_reports)
    any_trace = any(report.get("has_source_trace_in_samples") for report in ok_reports)

    if any_divisions and any_vote_indicators:
        suitable = "likely_yes_needs_parser"
        next_step = "Build a small ParlParse XML-to-vote-row parser for a bounded 2001-2016 sample, then compare its output shape with the Commons Votes API index."
    elif any_divisions:
        suitable = "partial_needs_deeper_sample"
        next_step = "Inspect a division-specific XML sample or adjust detection rules, because division-like elements were found but vote-side indicators were not clear."
    else:
        suitable = "not_proven"
        next_step = "Find a more direct divisions-only XML sample or use Public Whip data instead."

    return {
        "can_fetch_actual_xml": bool(ok_reports),
        "division_records_found": any_divisions,
        "vote_side_indicators_found": any_vote_indicators,
        "source_trace_found": any_trace,
        "suitable_for_future_parser": suitable,
        "merge_now": False,
        "next_step": next_step,
    }


def build_report(config, events, discovered_links, xml_reports):
    return {
        "generated_at": utc_now_iso(),
        "purpose": config.get("purpose", ""),
        "source_id": config.get("source_id", ""),
        "target_mp": config.get("target_mp", ""),
        "target_member_id": config.get("target_member_id", ""),
        "wanted_date_range": config.get("wanted_date_range", {}),
        "network_requests_made": bool(events),
        "index_links_discovered": len(discovered_links),
        "xml_reports_checked": len(xml_reports),
        "source_events": events,
        "xml_reports": xml_reports,
        "future_row_shape": config.get("future_row_shape", {}),
        "verdict": verdict(xml_reports),
    }


def build_markdown(report):
    verdict_data = report.get("verdict", {})
    date_range = report.get("wanted_date_range", {})
    lines = []
    lines.append("# ParlParse XML Sample Report v1.6")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at', '')}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report inspects actual ParlParse XML samples only. It does not merge rows, publish raw XML, crawl recursively, or claim full-career coverage.")
    lines.append("")
    lines.append("## Target")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Source ID", report.get("source_id", "")],
        ["Target MP", report.get("target_mp", "")],
        ["Target member ID", report.get("target_member_id", "")],
        ["Wanted date range", f"{date_range.get('start', '')} to {date_range.get('end', '')}"],
        ["Network requests made", report.get("network_requests_made", False)],
        ["XML links discovered", report.get("index_links_discovered", 0)],
        ["XML reports checked", report.get("xml_reports_checked", 0)],
    ]))
    lines.append("")
    lines.append("## Source events")
    lines.append("")
    lines.append(markdown_table(
        ["Stage", "Index", "Status", "XML links / chars", "URL", "Error"],
        [
            [
                event.get("stage", ""),
                event.get("index", ""),
                event.get("status", ""),
                event.get("xml_links_found", event.get("characters_read", "")),
                event.get("url", ""),
                event.get("error", ""),
            ]
            for event in report.get("source_events", [])
        ],
    ))
    lines.append("")
    lines.append("## XML sample results")
    lines.append("")
    lines.append(markdown_table(
        ["XML URL", "Status", "Division-like elements", "Vote indicators", "Source trace", "Target mentioned"],
        [
            [
                sample.get("xml_url", ""),
                sample.get("status", ""),
                sample.get("division_like_count", 0),
                sample.get("has_vote_indicators_in_samples", ""),
                sample.get("has_source_trace_in_samples", ""),
                sample.get("target_name_mentioned", ""),
            ]
            for sample in report.get("xml_reports", [])
        ],
    ))
    lines.append("")
    lines.append("## Sample division fields")
    lines.append("")
    for sample in report.get("xml_reports", []):
        lines.append(f"### {sample.get('xml_url', '')}")
        lines.append("")
        for index, division in enumerate(sample.get("sample_divisions", [])[:3], start=1):
            lines.append(f"#### Division-like sample {index}")
            lines.append("")
            lines.append(markdown_table(["Field", "Value"], [
                ["Tag", division.get("tag", "")],
                ["Attribute keys", ", ".join(division.get("attribute_keys", []))],
                ["Child tags", ", ".join(division.get("child_tags", []))],
                ["Vote indicators", ", ".join(division.get("vote_indicators", []))],
                ["Possible name attribute elements", division.get("possible_name_attribute_elements", 0)],
                ["Possible ID attribute elements", division.get("possible_id_attribute_elements", 0)],
                ["Small text excerpt", division.get("text_excerpt", "")],
            ]))
            lines.append("")
    lines.append("## Future row shape")
    lines.append("")
    lines.append(markdown_table(["Field", "Target value / rule"], report.get("future_row_shape", {}).items()))
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(markdown_table(["Field", "Value"], [
        ["Can fetch actual XML", verdict_data.get("can_fetch_actual_xml", False)],
        ["Division records found", verdict_data.get("division_records_found", False)],
        ["Vote-side indicators found", verdict_data.get("vote_side_indicators_found", False)],
        ["Source trace found", verdict_data.get("source_trace_found", False)],
        ["Suitable for future parser", verdict_data.get("suitable_for_future_parser", "")],
        ["Merge now", verdict_data.get("merge_now", False)],
        ["Next step", verdict_data.get("next_step", "")],
    ]))
    lines.append("")
    lines.append("## What this report does not do")
    lines.append("")
    lines.append("- It does not merge historic votes into the MP vote index.")
    lines.append("- It does not publish large raw XML extracts.")
    lines.append("- It does not solve the 1983-2001 gap.")
    lines.append("- It does not infer human political meaning from votes.")
    return "\n".join(lines) + "\n"


def main():
    print("Starting ParlParse XML sample inspection v1.6")
    config = load_json(INPUT_FILE)
    events, discovered_links, xml_reports = inspect_sources(config)
    report = build_report(config, events, discovered_links, xml_reports)
    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    print("Final summary")
    print("-------------")
    print(f"XML links discovered: {report['index_links_discovered']}")
    print(f"XML reports checked: {report['xml_reports_checked']}")
    print(f"Suitable for future parser: {report['verdict']['suitable_for_future_parser']}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
