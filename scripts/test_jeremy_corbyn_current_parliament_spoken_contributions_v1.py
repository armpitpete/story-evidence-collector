#!/usr/bin/env python3
"""Produce one fixed official-source capture for the authorised spoken-contributions lane."""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

MEMBER_ID = 185
START_DATE = "2024-07-04"
CAPTURE_END_DATE = os.environ.get(
    "CAPTURE_END_DATE", datetime.now(timezone.utc).date().isoformat()
)
OUT = Path(os.environ.get("CAPTURE_OUTPUT", "fixed-capture.json"))
UA = (
    "story-evidence-collector/1.0 "
    "(+https://github.com/armpitpete/story-evidence-collector)"
)
AUTHORISED_VENUES = {"Commons Chamber", "Westminster Hall"}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def fetch(url: str, attempts: int = 5) -> tuple[bytes, dict]:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(
                url,
                headers={"User-Agent": UA, "Accept": "application/json"},
            )
            with urlopen(req, timeout=120) as response:
                raw = response.read()
                return raw, {
                    "url": url,
                    "status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "byte_length": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            if attempt == attempts:
                break
            time.sleep(attempt * 2)
    raise RuntimeError(f"Failed after {attempts} attempts: {url}: {last}")


def fetch_json(url: str, requests: list[dict]) -> object:
    raw, metadata = fetch(url)
    requests.append(metadata)
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except Exception as exc:
        metadata["body_prefix"] = raw[:500].decode("utf-8", errors="replace")
        raise RuntimeError(f"Non-JSON response: {metadata}") from exc


def first_list(value: object) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "Items", "results", "Results", "value", "Value"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return candidate
    return []


def flatten_debate_items(debate: dict) -> list[dict]:
    result = list(debate.get("Items", []))
    for child in debate.get("ChildDebates", []):
        if isinstance(child, dict):
            result.extend(flatten_debate_items(child))
    return result


def source_status(raw_source: object) -> str:
    if raw_source == "RollingHansard":
        return "rolling_uncorrected"
    if raw_source in {"DailyHansard", "BoundVolume", "Historic"}:
        return "corrected"
    return "unspecified"


def main() -> int:
    captured_at = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    requests: list[dict] = []
    failures: list[dict] = []
    exclusions: list[dict] = []

    member_pages: list[dict] = []
    all_member_rows: list[dict] = []
    crossed_boundary = False
    page = 1
    while page <= 100 and not crossed_boundary:
        url = (
            "https://members-api.parliament.uk/api/Members/"
            f"{MEMBER_ID}/ContributionSummary?page={page}"
        )
        payload = fetch_json(url, requests)
        items = first_list(payload)
        member_pages.append(
            {
                "page": page,
                "item_count": len(items),
                "payload_total_results": payload.get("totalResults")
                if isinstance(payload, dict)
                else None,
                "payload_canonical_sha256": canonical_sha256(payload),
                "items": items,
            }
        )
        for item in items:
            value = item.get("value", {}) if isinstance(item, dict) else {}
            sitting_date = str(value.get("sittingDate", ""))[:10]
            if sitting_date and sitting_date < START_DATE:
                crossed_boundary = True
            all_member_rows.append(item)
        print(f"Members page {page}: {len(items)} rows", flush=True)
        page += 1
        time.sleep(0.15)

    in_date_rows = [
        item
        for item in all_member_rows
        if str(item.get("value", {}).get("sittingDate", ""))[:10]
        >= START_DATE
        and str(item.get("value", {}).get("sittingDate", ""))[:10]
        <= CAPTURE_END_DATE
    ]
    authorised_rows: list[dict] = []
    for item in in_date_rows:
        value = item["value"]
        if value.get("house") != "Commons":
            exclusions.append(
                {
                    "stage": "member_index",
                    "reason": "non_commons_house",
                    "item": item,
                }
            )
        elif value.get("section") not in AUTHORISED_VENUES:
            exclusions.append(
                {
                    "stage": "member_index",
                    "reason": "venue_outside_authorised_boundary",
                    "item": item,
                }
            )
        else:
            authorised_rows.append(item)

    # Exact Hansard spoken-contribution index, paged at the documented maximum 100.
    search_pages: list[dict] = []
    search_results: list[dict] = []
    skip = 0
    spoken_total: int | None = None
    while spoken_total is None or skip < spoken_total:
        params = {
            "queryParameters.house": "Commons",
            "queryParameters.startDate": START_DATE,
            "queryParameters.endDate": CAPTURE_END_DATE,
            "queryParameters.memberId": str(MEMBER_ID),
            "queryParameters.skip": str(skip),
            "queryParameters.take": "100",
            "queryParameters.orderBy": "SittingDateAsc",
        }
        url = (
            "https://hansard-api.parliament.uk/search/contributions/Spoken.json?"
            + urlencode(params)
        )
        payload = fetch_json(url, requests)
        if not isinstance(payload, dict):
            raise RuntimeError("Hansard spoken search did not return an object")
        results = payload.get("Results", [])
        spoken_total = int(payload.get("SpokenResultCount", 0))
        search_pages.append(
            {
                "skip": skip,
                "take": 100,
                "result_count": len(results),
                "reported_spoken_result_count": spoken_total,
                "reported_total_result_count": payload.get("TotalResultCount"),
                "reported_corrections_result_count": payload.get(
                    "CorrectionsResultCount"
                ),
                "payload_canonical_sha256": canonical_sha256(payload),
                "results": results,
            }
        )
        search_results.extend(results)
        print(
            f"Hansard search skip {skip}: {len(results)} of {spoken_total}",
            flush=True,
        )
        if not results:
            break
        skip += len(results)
        time.sleep(0.15)

    search_by_id: dict[str, dict] = {}
    duplicate_search_ids: list[str] = []
    for item in search_results:
        ext_id = str(item.get("ContributionExtId", "")).upper()
        if not ext_id:
            failures.append(
                {
                    "stage": "hansard_search",
                    "reason": "missing_contribution_external_id",
                    "item": item,
                }
            )
        elif ext_id in search_by_id:
            duplicate_search_ids.append(ext_id)
        else:
            search_by_id[ext_id] = item

    records: list[dict] = []
    seen_ids: set[str] = set()
    debate_reconciliation: list[dict] = []

    for row_number, index_item in enumerate(authorised_rows, 1):
        value = index_item["value"]
        debate_ext_id = str(value.get("debateWebsiteId", "")).upper()
        date = str(value.get("sittingDate", ""))[:10]
        venue = value.get("section")
        if not debate_ext_id:
            failures.append(
                {
                    "stage": "member_index",
                    "reason": "missing_debate_external_id",
                    "index_item": index_item,
                }
            )
            continue

        member_url = (
            "https://hansard-api.parliament.uk/debates/"
            f"memberdebatecontributions/{MEMBER_ID}.json?"
            + urlencode({"debateSectionExtId": debate_ext_id})
        )
        debate_url = (
            "https://hansard-api.parliament.uk/debates/debate/"
            f"{debate_ext_id}.json"
        )
        try:
            member_payload = fetch_json(member_url, requests)
            debate_payload = fetch_json(debate_url, requests)
        except Exception as exc:
            failures.append(
                {
                    "stage": "debate_fetch",
                    "debate_external_id": debate_ext_id,
                    "error": str(exc),
                }
            )
            continue

        if not isinstance(member_payload, list) or not isinstance(
            debate_payload, dict
        ):
            failures.append(
                {
                    "stage": "debate_shape",
                    "debate_external_id": debate_ext_id,
                    "member_payload_type": type(member_payload).__name__,
                    "debate_payload_type": type(debate_payload).__name__,
                }
            )
            continue

        overview = debate_payload.get("Overview", {})
        debate_items = flatten_debate_items(debate_payload)
        items_by_external_id: dict[str, list[dict]] = {}
        for debate_item in debate_items:
            ext = str(debate_item.get("ExternalId", "")).upper()
            if ext:
                items_by_external_id.setdefault(ext, []).append(debate_item)

        accepted_for_row = 0
        unresolved_for_row = 0
        member_ids_for_row: list[str] = []
        for member_segment in member_payload:
            contribution_id = str(
                member_segment.get("ContentItemExtId", "")
            ).upper()
            member_ids_for_row.append(contribution_id)
            reasons: list[str] = []
            if not contribution_id:
                reasons.append("missing_content_item_external_id")
            if str(member_segment.get("DebateSectionExtId", "")).upper() != debate_ext_id:
                reasons.append("member_segment_debate_id_mismatch")
            matches = items_by_external_id.get(contribution_id, [])
            if len(matches) != 1:
                reasons.append(
                    "full_debate_external_id_match_count_" + str(len(matches))
                )
                debate_item = None
            else:
                debate_item = matches[0]
            search_item = search_by_id.get(contribution_id)
            if search_item is None:
                reasons.append("missing_from_hansard_spoken_search")
            if contribution_id in seen_ids:
                reasons.append("duplicate_contribution_external_id")

            if debate_item is not None:
                if debate_item.get("MemberId") != MEMBER_ID:
                    reasons.append("full_debate_member_id_mismatch")
                if not str(debate_item.get("Value", "")).strip():
                    reasons.append("missing_full_contribution_text")
                if str(overview.get("ExtId", "")).upper() != debate_ext_id:
                    reasons.append("debate_overview_external_id_mismatch")
                if str(overview.get("Date", ""))[:10] != date:
                    reasons.append("debate_date_mismatch")
                if overview.get("House") != "Commons":
                    reasons.append("debate_house_mismatch")
                if overview.get("Location") != venue:
                    reasons.append("debate_venue_mismatch")

            if search_item is not None:
                if search_item.get("MemberId") != MEMBER_ID:
                    reasons.append("search_member_id_mismatch")
                if str(search_item.get("DebateSectionExtId", "")).upper() != debate_ext_id:
                    reasons.append("search_debate_id_mismatch")
                if str(search_item.get("SittingDate", ""))[:10] != date:
                    reasons.append("search_date_mismatch")
                if search_item.get("House") != "Commons":
                    reasons.append("search_house_mismatch")
                if search_item.get("Section") != venue:
                    reasons.append("search_venue_mismatch")

            if reasons:
                unresolved_for_row += 1
                failures.append(
                    {
                        "stage": "segment_reconciliation",
                        "debate_external_id": debate_ext_id,
                        "contribution_external_id": contribution_id or None,
                        "reasons": reasons,
                        "member_segment": member_segment,
                    }
                )
                continue

            assert debate_item is not None
            assert search_item is not None
            seen_ids.add(contribution_id)
            accepted_for_row += 1

            redirect_url = (
                "https://hansard-api.parliament.uk/search/"
                "parlisearchredirect.json?"
                + urlencode({"externalId": contribution_id})
            )
            try:
                permalink = fetch_json(redirect_url, requests)
            except Exception as exc:
                failures.append(
                    {
                        "stage": "permalink_resolution",
                        "debate_external_id": debate_ext_id,
                        "contribution_external_id": contribution_id,
                        "error": str(exc),
                    }
                )
                seen_ids.remove(contribution_id)
                accepted_for_row -= 1
                unresolved_for_row += 1
                continue
            if not isinstance(permalink, str) or not permalink.startswith("https://"):
                failures.append(
                    {
                        "stage": "permalink_resolution",
                        "debate_external_id": debate_ext_id,
                        "contribution_external_id": contribution_id,
                        "reason": "invalid_official_permalink",
                        "value": permalink,
                    }
                )
                seen_ids.remove(contribution_id)
                accepted_for_row -= 1
                unresolved_for_row += 1
                continue

            status = source_status(overview.get("Source"))
            records.append(
                {
                    "contribution_external_id": contribution_id,
                    "debate_external_id": debate_ext_id,
                    "debate_numeric_id": overview.get("Id"),
                    "member_id": MEMBER_ID,
                    "attributed_to": debate_item.get("AttributedTo"),
                    "sitting_date": date,
                    "house": overview.get("House"),
                    "venue": overview.get("Location"),
                    "debate_title": overview.get("Title"),
                    "contribution_type": debate_item.get("ItemType"),
                    "hrs_tag": debate_item.get("HRSTag"),
                    "hansard_section": debate_item.get("HansardSection"),
                    "order_in_section": debate_item.get("OrderInSection"),
                    "timecode": debate_item.get("Timecode"),
                    "uin": debate_item.get("UIN"),
                    "is_reiteration": debate_item.get("IsReiteration"),
                    "full_text": debate_item.get("Value"),
                    "official_permalink": permalink,
                    "source_raw_value": overview.get("Source"),
                    "source_status": status,
                    "content_last_updated": overview.get("ContentLastUpdated"),
                    "member_segment": member_segment,
                    "search_result": search_item,
                    "cross_checks": {
                        "member_segment_matches_debate": True,
                        "full_debate_external_id_unique": True,
                        "full_debate_member_id_185": True,
                        "full_debate_date_matches_index": True,
                        "full_debate_venue_matches_index": True,
                        "search_external_id_matches": True,
                        "search_member_id_185": True,
                        "search_debate_id_matches": True,
                        "search_date_matches": True,
                        "search_venue_matches": True,
                        "official_permalink_resolved": True,
                    },
                }
            )

        debate_reconciliation.append(
            {
                "row_number": row_number,
                "debate_external_id": debate_ext_id,
                "sitting_date": date,
                "venue": venue,
                "displayed_total_contributions": value.get("totalContributions"),
                "displayed_category_counts": {
                    key: value.get(key)
                    for key in (
                        "speechCount",
                        "questionCount",
                        "supplementaryQuestionCount",
                        "interventionCount",
                        "answerCount",
                        "pointsOfOrderCount",
                        "statementsCount",
                    )
                },
                "member_segment_count": len(member_payload),
                "accepted_segment_count": accepted_for_row,
                "unresolved_segment_count": unresolved_for_row,
                "member_contribution_external_ids": member_ids_for_row,
                "member_payload_canonical_sha256": canonical_sha256(
                    member_payload
                ),
                "full_debate_payload_canonical_sha256": canonical_sha256(
                    debate_payload
                ),
                "debate_overview": overview,
            }
        )
        print(
            f"Debate {row_number}/{len(authorised_rows)} {date} "
            f"{accepted_for_row}/{len(member_payload)} accepted",
            flush=True,
        )
        time.sleep(0.10)

    search_ids = set(search_by_id)
    accepted_ids = {item["contribution_external_id"] for item in records}
    search_only_ids = sorted(search_ids - accepted_ids)
    detail_only_ids = sorted(accepted_ids - search_ids)
    if search_only_ids:
        failures.append(
            {
                "stage": "set_reconciliation",
                "reason": "search_ids_not_accepted_from_debate_rows",
                "count": len(search_only_ids),
                "ids": search_only_ids,
            }
        )
    if detail_only_ids:
        failures.append(
            {
                "stage": "set_reconciliation",
                "reason": "accepted_ids_missing_from_search",
                "count": len(detail_only_ids),
                "ids": detail_only_ids,
            }
        )

    records.sort(
        key=lambda item: (
            item["sitting_date"],
            item["venue"],
            item["debate_external_id"],
            item["order_in_section"] if item["order_in_section"] is not None else -1,
            item["contribution_external_id"],
        )
    )

    displayed_category_counts = Counter()
    displayed_total = 0
    for row in authorised_rows:
        value = row["value"]
        displayed_total += int(value.get("totalContributions") or 0)
        for key in (
            "speechCount",
            "questionCount",
            "supplementaryQuestionCount",
            "interventionCount",
            "answerCount",
            "pointsOfOrderCount",
            "statementsCount",
        ):
            displayed_category_counts[key] += int(value.get(key) or 0)

    request_manifest = [
        {
            "sequence": number,
            **metadata,
        }
        for number, metadata in enumerate(requests, 1)
    ]
    raw_capture_manifest_sha256 = canonical_sha256(request_manifest)

    packet = {
        "packet_id": "jeremy-corbyn-current-parliament-spoken-contributions-fixed-capture-v1",
        "captured_at": captured_at,
        "subject": {
            "official_name": "Jeremy Corbyn",
            "uk_parliament_member_id": str(MEMBER_ID),
        },
        "scope": {
            "house": "House of Commons",
            "venues": sorted(AUTHORISED_VENUES),
            "date_from_authorised": START_DATE,
            "date_to_capture_boundary": CAPTURE_END_DATE,
            "record_type": "individual_spoken_contribution_segments",
            "topic_classification_included": False,
            "summarisation_included": False,
            "position_inference_included": False,
            "contradiction_analysis_included": False,
        },
        "official_endpoint_shapes": {
            "member_index": "/api/Members/{id}/ContributionSummary?page={page}",
            "hansard_spoken_search": (
                "/search/contributions/Spoken.json?"
                "queryParameters.house={house}&"
                "queryParameters.startDate={start_date}&"
                "queryParameters.endDate={end_date}&"
                "queryParameters.memberId={member_id}&"
                "queryParameters.skip={skip}&"
                "queryParameters.take={take}&"
                "queryParameters.orderBy=SittingDateAsc"
            ),
            "member_debate_segments": (
                "/debates/memberdebatecontributions/{memberId}.json?"
                "debateSectionExtId={debateSectionExtId}"
            ),
            "full_debate": (
                "/debates/debate/{debateSectionExtId}.json"
            ),
            "official_permalink_resolver": (
                "/search/parlisearchredirect.json?externalId={externalId}"
            ),
        },
        "stable_identifier_method": {
            "primary": "member segment ContentItemExtId",
            "required_full_debate_match": "Items[].ExternalId",
            "required_member_id": MEMBER_ID,
            "duplicate_policy": "reject duplicate exact contribution external identifiers",
            "missing_or_unmatched_policy": "hold as unresolved; do not synthesize a key",
        },
        "five_explicit_results": {
            "captured_debate_row_count": len(authorised_rows),
            "unique_individual_contribution_count": len(records),
            "stable_identifier_method": (
                "official ContentItemExtId matched exactly to full-debate "
                "Items[].ExternalId with MemberId 185"
            ),
            "exact_date_coverage": {
                "earliest_accepted_contribution_date": min(
                    (item["sitting_date"] for item in records), default=None
                ),
                "latest_accepted_contribution_date": max(
                    (item["sitting_date"] for item in records), default=None
                ),
                "capture_timestamp_utc": captured_at,
            },
            "unresolved_record_count": len(failures),
        },
        "capture_counts": {
            "member_index_page_count": len(member_pages),
            "member_index_all_rows_fetched": len(all_member_rows),
            "member_index_rows_in_date_boundary": len(in_date_rows),
            "member_index_authorised_debate_rows": len(authorised_rows),
            "member_index_excluded_rows": len(exclusions),
            "hansard_search_page_count": len(search_pages),
            "hansard_search_reported_spoken_count": spoken_total,
            "hansard_search_unique_external_id_count": len(search_by_id),
            "hansard_search_duplicate_external_id_count": len(
                duplicate_search_ids
            ),
            "accepted_unique_contribution_count": len(records),
            "search_only_external_id_count": len(search_only_ids),
            "detail_only_external_id_count": len(detail_only_ids),
            "official_request_count": len(request_manifest),
            "venue_counts": dict(Counter(item["venue"] for item in records)),
            "contribution_type_counts": dict(
                Counter(item["contribution_type"] for item in records)
            ),
            "source_status_counts": dict(
                Counter(item["source_status"] for item in records)
            ),
            "source_raw_value_counts": {
                str(key): value
                for key, value in Counter(
                    item["source_raw_value"] for item in records
                ).items()
            },
            "member_index_displayed_total_contributions_sum": displayed_total,
            "member_index_displayed_category_counts": dict(
                displayed_category_counts
            ),
            "member_index_displayed_category_sum": sum(
                displayed_category_counts.values()
            ),
        },
        "member_index_pages": member_pages,
        "hansard_search_pages": search_pages,
        "debate_reconciliation": debate_reconciliation,
        "records": records,
        "exclusions": exclusions,
        "unresolved_records": failures,
        "duplicate_search_external_ids": sorted(duplicate_search_ids),
        "raw_capture": {
            "manifest_canonical_sha256": raw_capture_manifest_sha256,
            "request_count": len(request_manifest),
            "total_response_bytes": sum(
                item["byte_length"] for item in request_manifest
            ),
            "request_manifest": request_manifest,
        },
    }

    encoded = json.dumps(
        packet, indent=2, ensure_ascii=False, sort_keys=True
    ).encode("utf-8") + b"\n"
    OUT.write_bytes(encoded)
    print(
        f"Wrote {OUT} ({len(encoded)} bytes; "
        f"sha256={hashlib.sha256(encoded).hexdigest()})",
        flush=True,
    )
    print(json.dumps(packet["five_explicit_results"], indent=2), flush=True)
    print(json.dumps(packet["capture_counts"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
