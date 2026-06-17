import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


QUERY_FILE = Path("mp_full_vote_query.json")
OUTPUT_JSON_FILE = Path("mp_full_vote_index_v13.json")
OUTPUT_MARKDOWN_FILE = Path("mp_full_vote_index_v13.md")
SOURCE_REPORT_FILE = Path("mp_vote_index_source_report_v13.md")

COMMONS_VOTES_API_BASE = "https://commonsvotes-api.parliament.uk/data"
USER_AGENT = "StoryEvidenceCollector/MPVoteIndex/1.3"
REQUEST_TIMEOUT_SECONDS = 30
POLITE_DELAY_SECONDS = 0.05

PAGINATION_STRATEGIES = [
    "page",
    "page_number",
    "skip_take",
    "skip_results_per_page",
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


def first_present(data, names, default=None):
    if not isinstance(data, dict):
        return default
    for name in names:
        if name in data:
            return data[name]
    return default


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        cells = [clean_text(cell).replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_query():
    data = load_json(QUERY_FILE)
    member_id = clean_text(data.get("member_id"))
    mp_name = clean_text(data.get("mp_name"))

    if not member_id:
        raise RuntimeError("mp_full_vote_query.json must include member_id.")
    if not mp_name:
        raise RuntimeError("mp_full_vote_query.json must include mp_name.")

    return {
        "mp_name": mp_name,
        "member_id": member_id,
        "constituency": clean_text(data.get("constituency")),
        "party": clean_text(data.get("party")),
        "party_source_status": clean_text(data.get("party_source_status")),
        "parliamentary_listing": clean_text(data.get("parliamentary_listing")),
        "source": clean_text(data.get("source")) or "commons_votes_api",
        "max_pages": int(data.get("max_pages", 100)),
        "results_per_page": int(data.get("results_per_page", 100)),
        "fetch_division_details": bool(data.get("fetch_division_details", True)),
        "max_division_detail_fetches": int(data.get("max_division_detail_fetches", 2500)),
    }


def fetch_json(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def build_search_url(member_id, page, results_per_page, strategy):
    params = {
        "queryParameters.memberId": member_id,
        "queryParameters.includeWhenMemberWasTeller": "false",
    }

    if strategy == "page":
        params["queryParameters.page"] = page
        params["queryParameters.resultsPerPage"] = results_per_page
    elif strategy == "page_number":
        params["queryParameters.pageNumber"] = page
        params["queryParameters.resultsPerPage"] = results_per_page
    elif strategy == "skip_take":
        params["queryParameters.skip"] = (page - 1) * results_per_page
        params["queryParameters.take"] = results_per_page
    elif strategy == "skip_results_per_page":
        params["queryParameters.skip"] = (page - 1) * results_per_page
        params["queryParameters.resultsPerPage"] = results_per_page
    else:
        raise RuntimeError(f"Unknown pagination strategy: {strategy}")

    return f"{COMMONS_VOTES_API_BASE}/divisions.json/search?{urlencode(params)}"


def extract_items(search_response):
    if isinstance(search_response, list):
        return search_response

    if not isinstance(search_response, dict):
        return []

    for key in ["items", "Items", "results", "Results", "data", "Data"]:
        value = search_response.get(key)
        if isinstance(value, list):
            return value

    return []


def extract_total_results(search_response):
    if not isinstance(search_response, dict):
        return None
    return first_present(search_response, ["totalResults", "TotalResults", "total", "Total"], None)


def extract_division_id(item):
    return clean_text(first_present(item, ["divisionId", "DivisionId", "id", "Id"], ""))


def division_id_set(items):
    return {extract_division_id(item) for item in items if extract_division_id(item)}


def probe_pagination_strategy(query, strategy):
    events = []
    page_results = []

    for page in [1, 2]:
        url = build_search_url(query["member_id"], page, query["results_per_page"], strategy)
        try:
            response = fetch_json(url)
            items = extract_items(response)
            ids = division_id_set(items)
            page_results.append({
                "page": page,
                "items": items,
                "ids": ids,
                "total_results": extract_total_results(response),
            })
            events.append({
                "stage": "pagination_probe",
                "strategy": strategy,
                "page": page,
                "url": url,
                "status": "ok",
                "items": len(items),
                "unique_division_ids": len(ids),
            })
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            events.append({
                "stage": "pagination_probe",
                "strategy": strategy,
                "page": page,
                "url": url,
                "status": "failed",
                "error": str(error),
            })
            return {
                "strategy": strategy,
                "usable": False,
                "reason": "probe_request_failed",
                "events": events,
                "first_page_items": [],
                "total_results": None,
            }

    first_items = page_results[0]["items"] if page_results else []
    first_ids = page_results[0]["ids"] if page_results else set()
    second_ids = page_results[1]["ids"] if len(page_results) > 1 else set()

    if not first_items:
        return {
            "strategy": strategy,
            "usable": False,
            "reason": "first_page_empty",
            "events": events,
            "first_page_items": [],
            "total_results": None,
        }

    if second_ids and first_ids != second_ids:
        return {
            "strategy": strategy,
            "usable": True,
            "reason": "second_page_differs",
            "events": events,
            "first_page_items": first_items,
            "total_results": page_results[0].get("total_results"),
        }

    if len(first_items) < query["results_per_page"]:
        return {
            "strategy": strategy,
            "usable": True,
            "reason": "single_page_result_set",
            "events": events,
            "first_page_items": first_items,
            "total_results": page_results[0].get("total_results"),
        }

    return {
        "strategy": strategy,
        "usable": False,
        "reason": "second_page_repeated_first_page",
        "events": events,
        "first_page_items": first_items,
        "total_results": page_results[0].get("total_results"),
    }


def choose_pagination_strategy(query):
    all_events = []

    for strategy in PAGINATION_STRATEGIES:
        result = probe_pagination_strategy(query, strategy)
        all_events.extend(result["events"])

        all_events.append({
            "stage": "pagination_strategy_result",
            "strategy": strategy,
            "status": "usable" if result["usable"] else "not_usable",
            "reason": result["reason"],
        })

        if result["usable"]:
            return strategy, result.get("total_results"), all_events

    return "page", None, all_events + [{
        "stage": "pagination_strategy_result",
        "strategy": "page",
        "status": "fallback",
        "reason": "no_probe_strategy_verified",
    }]


def fetch_member_division_search_pages(query):
    all_items = []
    source_events = []
    total_results = None
    seen_page_signatures = set()

    strategy, probe_total_results, probe_events = choose_pagination_strategy(query)
    total_results = probe_total_results
    source_events.extend(probe_events)
    source_events.append({
        "stage": "pagination_strategy_chosen",
        "strategy": strategy,
        "status": "chosen",
    })

    for page in range(1, query["max_pages"] + 1):
        url = build_search_url(query["member_id"], page, query["results_per_page"], strategy)
        try:
            response = fetch_json(url)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            source_events.append({
                "stage": "search_page",
                "page": page,
                "strategy": strategy,
                "url": url,
                "status": "failed",
                "error": str(error),
            })
            break

        items = extract_items(response)
        total_results = total_results or extract_total_results(response)
        ids = tuple(sorted(division_id_set(items)))

        source_events.append({
            "stage": "search_page",
            "page": page,
            "strategy": strategy,
            "url": url,
            "status": "ok",
            "items": len(items),
            "unique_division_ids": len(ids),
        })

        if not items:
            break

        if ids and ids in seen_page_signatures:
            source_events.append({
                "stage": "search_page",
                "page": page,
                "strategy": strategy,
                "url": url,
                "status": "stopped_repeated_page",
                "items": len(items),
                "unique_division_ids": len(ids),
            })
            break

        if ids:
            seen_page_signatures.add(ids)

        all_items.extend(items)

        if len(items) < query["results_per_page"]:
            break

        time.sleep(POLITE_DELAY_SECONDS)

    return all_items, total_results, source_events, strategy


def build_division_detail_url(division_id):
    return f"{COMMONS_VOTES_API_BASE}/division/{division_id}.json"


def fetch_division_detail(division_id):
    return fetch_json(build_division_detail_url(division_id))


def member_name_matches(member, query):
    if not isinstance(member, dict):
        return False

    member_id = clean_text(first_present(member, ["memberId", "MemberId", "id", "Id"], ""))
    if member_id and member_id == query["member_id"]:
        return True

    names = [
        first_present(member, ["name", "Name", "fullName", "FullName", "displayName", "DisplayName"], ""),
        first_present(member, ["listAs", "ListAs"], ""),
    ]
    target = query["mp_name"].casefold()
    return any(clean_text(name).casefold() == target for name in names if clean_text(name))


def get_member_lists(detail):
    if not isinstance(detail, dict):
        return [], [], []

    ayes = first_present(detail, ["ayes", "Ayes", "ayeMembers", "AyeMembers"], [])
    noes = first_present(detail, ["noes", "Noes", "noMembers", "NoMembers"], [])
    not_recorded = first_present(detail, ["noVoteRecorded", "NoVoteRecorded", "notRecorded", "NotRecorded"], [])

    return (
        ayes if isinstance(ayes, list) else [],
        noes if isinstance(noes, list) else [],
        not_recorded if isinstance(not_recorded, list) else [],
    )


def classify_member_vote_from_detail(detail, query):
    ayes, noes, not_recorded = get_member_lists(detail)
    in_aye = any(member_name_matches(member, query) for member in ayes)
    in_no = any(member_name_matches(member, query) for member in noes)
    in_not_recorded = any(member_name_matches(member, query) for member in not_recorded)

    if in_aye and in_no:
        return "Unable to determine", "mp_found_in_aye_and_no"
    if in_aye:
        return "Aye", "mp_found_in_aye_list"
    if in_no:
        return "No", "mp_found_in_no_list"
    if in_not_recorded:
        return "Not recorded", "mp_found_in_not_recorded_list"
    return "Not recorded", "mp_not_found_in_detail_member_lists"


def normalise_date(value):
    text = clean_text(value)
    if "T" in text:
        return text.split("T", 1)[0]
    return text


def build_source_url(division_id):
    if not division_id:
        return ""
    return f"https://votes.parliament.uk/votes/commons/division/{division_id}"


def build_vote_index_row(search_item, detail, query):
    division_id = clean_text(extract_division_id(search_item) or extract_division_id(detail))
    title = clean_text(first_present(detail, ["title", "Title"], "")) or clean_text(first_present(search_item, ["title", "Title"], ""))
    date = normalise_date(first_present(detail, ["date", "Date"], "")) or normalise_date(first_present(search_item, ["date", "Date"], ""))
    division_number = clean_text(first_present(detail, ["number", "Number", "divisionNumber", "DivisionNumber"], "")) or clean_text(first_present(search_item, ["number", "Number", "divisionNumber", "DivisionNumber"], ""))

    if detail:
        recorded_side, evidence_status = classify_member_vote_from_detail(detail, query)
    else:
        recorded_side = clean_text(first_present(search_item, ["memberVoted", "MemberVoted", "recordedVote", "RecordedVote"], "Unable to determine"))
        evidence_status = "detail_not_available"

    return {
        "date": date,
        "division_id": division_id,
        "division_number": division_number,
        "motion_title": title,
        "recorded_side": recorded_side,
        "meaning_quality": "needs_review",
        "topic": "uncategorised",
        "source_url": build_source_url(division_id),
        "evidence_status": evidence_status,
    }


def build_vote_index(query):
    search_items, total_results, source_events, pagination_strategy = fetch_member_division_search_pages(query)
    rows = []
    detail_fetches = 0
    seen_division_ids = set()

    for item in search_items:
        division_id = clean_text(extract_division_id(item))
        if division_id and division_id in seen_division_ids:
            continue
        if division_id:
            seen_division_ids.add(division_id)

        detail = None
        if query["fetch_division_details"] and division_id and detail_fetches < query["max_division_detail_fetches"]:
            try:
                detail = fetch_division_detail(division_id)
                detail_fetches += 1
                source_events.append({
                    "stage": "division_detail",
                    "division_id": division_id,
                    "url": build_division_detail_url(division_id),
                    "status": "ok",
                })
                time.sleep(POLITE_DELAY_SECONDS)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
                source_events.append({
                    "stage": "division_detail",
                    "division_id": division_id,
                    "url": build_division_detail_url(division_id),
                    "status": "failed",
                    "error": str(error),
                })

        rows.append(build_vote_index_row(item, detail, query))

    rows.sort(key=lambda item: (item.get("date") or "", item.get("division_id") or ""))

    return rows, total_results, source_events, detail_fetches, pagination_strategy


def safe_min_date(rows):
    dates = [row["date"] for row in rows if row.get("date")]
    return min(dates) if dates else ""


def safe_max_date(rows):
    dates = [row["date"] for row in rows if row.get("date")]
    return max(dates) if dates else ""


def build_report(query, rows, total_results, source_events, detail_fetches, pagination_strategy):
    side_counts = Counter(row["recorded_side"] for row in rows)
    failed_events = [event for event in source_events if event.get("status") == "failed"]
    repeated_events = [event for event in source_events if event.get("status") == "stopped_repeated_page"]

    coverage_warnings = [
        "This is a full-career index across the official/public vote records available to this run, not a claim that every possible historical record exists in the source.",
        "Do not describe this as a complete voting history unless source coverage is separately verified.",
    ]

    if rows:
        coverage_warnings.append(f"This run found records dated from {safe_min_date(rows)} to {safe_max_date(rows)} in the selected source.")
    if failed_events:
        coverage_warnings.append("Some source requests failed; check the source report before relying on coverage.")
    if repeated_events:
        coverage_warnings.append("Pagination returned a repeated page and the run stopped to avoid duplicate collection.")
    if total_results is not None and len(rows) < int(total_results):
        coverage_warnings.append("The source reported more total results than were written; check pagination and hard limits.")
    if len(rows) >= query["max_division_detail_fetches"]:
        coverage_warnings.append("The detail-fetch hard limit was reached before all rows could be checked in detail.")

    return {
        "generated_at": utc_now_iso(),
        "query": query,
        "source": "commons_votes_api",
        "pagination_strategy": pagination_strategy,
        "network_requests_made": True,
        "total_results_reported_by_source": total_results,
        "divisions_indexed": len(rows),
        "division_details_fetched": detail_fetches,
        "first_division_date_found": safe_min_date(rows),
        "latest_division_date_found": safe_max_date(rows),
        "recorded_aye": side_counts.get("Aye", 0),
        "recorded_no": side_counts.get("No", 0),
        "not_recorded": side_counts.get("Not recorded", 0),
        "unable_to_determine": side_counts.get("Unable to determine", 0),
        "source_events": source_events,
        "coverage_warnings": coverage_warnings,
        "votes": rows,
    }


def build_markdown(report):
    query = report["query"]
    lines = []
    lines.append(f"# Full-Career MP Vote Index — {query['mp_name']}")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report indexes the official/public vote records available to this run. It does not infer motive, private belief, or complete historical coverage beyond the selected source.")
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
    ]))
    lines.append("")
    lines.append("## Coverage summary")
    lines.append("")
    lines.append(markdown_table(["Metric", "Count / value"], [
        ["Pagination strategy", report.get("pagination_strategy", "")],
        ["Total results reported by source", report.get("total_results_reported_by_source", "")],
        ["Divisions indexed", report["divisions_indexed"]],
        ["Division details fetched", report["division_details_fetched"]],
        ["First division date found", report["first_division_date_found"]],
        ["Latest division date found", report["latest_division_date_found"]],
        ["Recorded Aye", report["recorded_aye"]],
        ["Recorded No", report["recorded_no"]],
        ["Not recorded", report["not_recorded"]],
        ["Unable to determine", report["unable_to_determine"]],
        ["Network requests made", report["network_requests_made"]],
    ]))
    lines.append("")
    lines.append("## Coverage warnings")
    lines.append("")
    for warning in report["coverage_warnings"]:
        lines.append(f"- {warning}")
    lines.append("")
    lines.append("## Vote index")
    lines.append("")
    lines.append(markdown_table(
        ["Date", "Division ID", "Division no.", "Motion title", "Recorded side", "Meaning quality", "Topic", "Source URL"],
        [
            [
                row["date"],
                row["division_id"],
                row["division_number"],
                row["motion_title"],
                row["recorded_side"],
                row["meaning_quality"],
                row["topic"],
                row["source_url"],
            ]
            for row in report["votes"]
        ],
    ))
    lines.append("")
    lines.append("## What this report does not prove")
    lines.append("")
    lines.append("- It does not prove motive or private belief.")
    lines.append("- It does not infer the human political meaning of each vote.")
    lines.append("- It does not prove complete historical coverage unless the selected source coverage is verified.")
    lines.append("- It does not treat absence from a division list as proof of why the MP did not vote.")
    return "\n".join(lines) + "\n"


def build_source_markdown(report):
    lines = []
    lines.append("# MP Vote Index Source Report v1.3")
    lines.append("")
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Source events")
    lines.append("")
    lines.append(markdown_table(
        ["Stage", "Strategy", "Page / division", "Status", "Items", "Unique IDs", "URL", "Error / reason"],
        [
            [
                event.get("stage", ""),
                event.get("strategy", ""),
                event.get("page", event.get("division_id", "")),
                event.get("status", ""),
                event.get("items", ""),
                event.get("unique_division_ids", ""),
                event.get("url", ""),
                event.get("error", event.get("reason", "")),
            ]
            for event in report["source_events"]
        ],
    ))
    return "\n".join(lines) + "\n"


def main():
    print("Starting full-career MP vote index v1.3")
    try:
        query = load_query()
    except RuntimeError as error:
        print(f"FAILED: {error}")
        return 1

    rows, total_results, source_events, detail_fetches, pagination_strategy = build_vote_index(query)
    report = build_report(query, rows, total_results, source_events, detail_fetches, pagination_strategy)

    save_json(OUTPUT_JSON_FILE, report)
    save_text(OUTPUT_MARKDOWN_FILE, build_markdown(report))
    save_text(SOURCE_REPORT_FILE, build_source_markdown(report))

    print("Final summary")
    print("-------------")
    print(f"MP: {query['mp_name']}")
    print(f"Pagination strategy: {pagination_strategy}")
    print(f"Divisions indexed: {report['divisions_indexed']}")
    print(f"First division date found: {report['first_division_date_found']}")
    print(f"Latest division date found: {report['latest_division_date_found']}")
    print(f"Recorded Aye: {report['recorded_aye']}")
    print(f"Recorded No: {report['recorded_no']}")
    print(f"Not recorded: {report['not_recorded']}")
    print(f"Unable to determine: {report['unable_to_determine']}")
    print(f"JSON output: {OUTPUT_JSON_FILE}")
    print(f"Markdown output: {OUTPUT_MARKDOWN_FILE}")
    print(f"Source report: {SOURCE_REPORT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
