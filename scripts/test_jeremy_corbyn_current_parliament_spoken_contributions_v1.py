#!/usr/bin/env python3
"""Build and verify the fixed Jeremy Corbyn spoken-contributions baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_complete_mp_report import (  # noqa: E402
    load_json,
    validate_report,
    write_outputs,
)

PACKET_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "current-parliament-spoken-contributions-v1.json"
)
SOURCE_NOTE_PATH = (
    ROOT
    / "docs"
    / "jeremy-corbyn-current-parliament-spoken-contributions-source-note-v1.md"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

MEMBER_ID = 185
SECTION_ID = "speeches_and_questions"
GAP_ID = "gap-speeches-questions-current-parliament-scope"
MEMBERS_SOURCE_ID = (
    "source-uk-parliament-members-api-corbyn-spoken-contributions-2026-07-21"
)
HANSARD_SOURCE_ID = (
    "source-uk-parliament-hansard-api-corbyn-spoken-contributions-2026-07-21"
)
EXPECTED_DEBATE_ROWS = 202
EXPECTED_CONTRIBUTIONS = 306
EXPECTED_DATE_FROM = "2024-07-17"
EXPECTED_DATE_TO = "2026-07-16"
EXPECTED_CAPTURE_TIMESTAMP = "2026-07-21T09:59:35Z"
FIXED_CAPTURE_SHA256 = (
    "b2776c11a5a17d9605f56434ec5b13d77e75567a9bf01f851bf48e2f440e6a88"
)
FIXED_CAPTURE_BYTE_LENGTH = 1650782
FIXED_ARTIFACT_ID = 8491239100
FIXED_ARTIFACT_DIGEST = (
    "sha256:30a68c8feda571c5d9f7d54549d54163b01e720a3eb1b3b0058fc02010dfc1de"
)
EXPECTED_VENUE_COUNTS = {
    "Commons Chamber": 280,
    "Westminster Hall": 26,
}
EXPECTED_OUTPUTS = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def by_id(records: list[dict], key: str) -> dict[str, dict]:
    result = {str(item[key]): item for item in records}
    assert len(result) == len(records), f"Duplicate {key}"
    return result


def section(report: dict, section_id: str) -> dict:
    return next(
        item
        for item in report["sections"]
        if item["section_id"] == section_id
    )


def source_status(raw_source: object) -> str:
    if raw_source == "RollingHansard":
        return "rolling_uncorrected"
    if raw_source in {"DailyHansard", "BoundVolume", "Historic"}:
        return "corrected"
    return "unspecified"


def load_fixed_capture(path: Path) -> dict:
    raw = path.read_bytes()
    assert len(raw) == FIXED_CAPTURE_BYTE_LENGTH
    assert hashlib.sha256(raw).hexdigest() == FIXED_CAPTURE_SHA256
    value = json.loads(raw.decode("utf-8"))
    assert isinstance(value, dict)
    assert value["captured_at"] == EXPECTED_CAPTURE_TIMESTAMP
    return value


def capture_search_results(capture: dict) -> list[dict]:
    results: list[dict] = []
    for page in capture["hansard_search_pages"]:
        results.extend(page["results"])
    return results


def capture_index_items(capture: dict) -> list[dict]:
    items: list[dict] = []
    for page in capture["member_index_pages"]:
        items.extend(page["items"])
    return items


def build_packet(capture: dict) -> dict:
    assert capture["capture_counts"]["member_index_authorised_debate_rows"] == (
        EXPECTED_DEBATE_ROWS
    )
    assert capture["capture_counts"]["hansard_search_reported_spoken_count"] == (
        EXPECTED_CONTRIBUTIONS
    )
    assert capture["capture_counts"]["official_request_count"] == 725
    assert len(capture["exclusions"]) == 1
    excluded = capture["exclusions"][0]
    assert excluded["reason"] == "venue_outside_authorised_boundary"
    assert excluded["item"]["value"]["section"] == "Written Corrections"

    permalink_failures = [
        item
        for item in capture["unresolved_records"]
        if item.get("stage") == "permalink_resolution"
        and item.get("reason") == "invalid_official_permalink"
    ]
    other_failures = [
        item
        for item in capture["unresolved_records"]
        if item not in permalink_failures
    ]
    assert len(permalink_failures) == EXPECTED_CONTRIBUTIONS
    assert len(other_failures) == 1
    assert other_failures[0]["stage"] == "set_reconciliation"
    assert other_failures[0]["count"] == EXPECTED_CONTRIBUTIONS

    search_results = capture_search_results(capture)
    search_by_id = by_id(search_results, "ContributionExtId")
    assert len(search_by_id) == EXPECTED_CONTRIBUTIONS

    index_items = capture_index_items(capture)
    index_by_debate = {
        item["value"]["debateWebsiteId"].upper(): item
        for item in index_items
        if item.get("value", {}).get("section")
        in {"Commons Chamber", "Westminster Hall"}
        and EXPECTED_DATE_FROM
        <= item.get("value", {}).get("sittingDate", "")[:10]
        <= EXPECTED_DATE_TO
    }
    assert len(index_by_debate) == EXPECTED_DEBATE_ROWS

    reconciliation_by_debate = by_id(
        capture["debate_reconciliation"], "debate_external_id"
    )
    assert len(reconciliation_by_debate) == EXPECTED_DEBATE_ROWS

    failure_by_id = by_id(permalink_failures, "contribution_external_id")
    assert set(failure_by_id) == set(search_by_id)

    records: list[dict] = []
    for contribution_id, search_item in search_by_id.items():
        contribution_id = contribution_id.upper()
        failure = failure_by_id[contribution_id]
        relative_permalink = failure["value"]
        assert isinstance(relative_permalink, str)
        assert relative_permalink.startswith("/Commons/")
        assert relative_permalink.endswith(contribution_id)
        official_permalink = "https://hansard.parliament.uk" + relative_permalink

        debate_id = str(search_item["DebateSectionExtId"]).upper()
        reconciliation = reconciliation_by_debate[debate_id]
        overview = reconciliation["debate_overview"]
        index_item = index_by_debate[debate_id]
        member_segment = failure["member_segment"]

        assert str(member_segment["ContentItemExtId"]).upper() == contribution_id
        assert str(member_segment["DebateSectionExtId"]).upper() == debate_id
        assert search_item["MemberId"] == MEMBER_ID
        assert str(search_item["ContributionExtId"]).upper() == contribution_id
        assert str(search_item["DebateSectionExtId"]).upper() == debate_id
        assert search_item["House"] == "Commons"
        assert search_item["Section"] in {
            "Commons Chamber",
            "Westminster Hall",
        }
        assert search_item["SittingDate"][:10] == overview["Date"][:10]
        assert search_item["Section"] == overview["Location"]
        assert str(search_item["ContributionTextFull"]).strip()

        records.append(
            {
                "contribution_external_id": contribution_id,
                "debate_external_id": debate_id,
                "member_id": MEMBER_ID,
                "attributed_to": search_item["AttributedTo"],
                "sitting_date": search_item["SittingDate"][:10],
                "house": search_item["House"],
                "venue": search_item["Section"],
                "debate_title": str(search_item["DebateSection"]).strip(),
                "contribution_type": "Spoken",
                "hrs_tag": search_item["HRSTag"],
                "hansard_section": search_item["HansardSection"],
                "order_in_debate_section": search_item[
                    "OrderInDebateSection"
                ],
                "item_id": search_item["ItemId"],
                "timecode": search_item["Timecode"],
                "full_text": search_item["ContributionTextFull"],
                "official_permalink": official_permalink,
                "official_permalink_resolver_return": relative_permalink,
                "source_raw_value": overview.get("Source"),
                "source_status": source_status(overview.get("Source")),
                "content_last_updated": overview.get("ContentLastUpdated"),
                "member_index_item": index_item,
                "member_segment": member_segment,
                "hansard_search_result": search_item,
                "reconciliation_evidence": {
                    "member_segment_reached_permalink_stage": True,
                    "content_item_ext_id_matched_full_debate_external_id": True,
                    "full_debate_member_id_185": True,
                    "full_debate_text_present": True,
                    "full_debate_date_matched_member_index": True,
                    "full_debate_venue_matched_member_index": True,
                    "hansard_search_external_id_matched": True,
                    "hansard_search_member_id_185": True,
                    "hansard_search_debate_id_matched": True,
                    "hansard_search_date_matched": True,
                    "hansard_search_venue_matched": True,
                    "official_relative_permalink_normalised": True,
                },
            }
        )

    records.sort(
        key=lambda item: (
            item["sitting_date"],
            item["venue"],
            item["debate_external_id"],
            item["order_in_debate_section"],
            item["contribution_external_id"],
        )
    )
    assert len(records) == EXPECTED_CONTRIBUTIONS
    assert len({item["contribution_external_id"] for item in records}) == (
        EXPECTED_CONTRIBUTIONS
    )
    assert records[0]["sitting_date"] == EXPECTED_DATE_FROM
    assert records[-1]["sitting_date"] == EXPECTED_DATE_TO
    venue_counts = dict(Counter(item["venue"] for item in records))
    assert venue_counts == EXPECTED_VENUE_COUNTS

    request_manifest = capture["raw_capture"]["request_manifest"]
    members_requests = [
        item
        for item in request_manifest
        if urlparse(item["url"]).netloc == "members-api.parliament.uk"
    ]
    hansard_requests = [
        item
        for item in request_manifest
        if urlparse(item["url"]).netloc == "hansard-api.parliament.uk"
    ]
    assert len(members_requests) == 11
    assert len(hansard_requests) == 714

    capture_date = EXPECTED_CAPTURE_TIMESTAMP[:10]
    members_manifest_sha = canonical_sha256(members_requests)
    hansard_manifest_sha = canonical_sha256(hansard_requests)

    sources = [
        {
            "source_id": MEMBERS_SOURCE_ID,
            "title": "UK Parliament Members API — Jeremy Corbyn contribution summary index",
            "publisher": "UK Parliament",
            "source_type": "parliamentary_record",
            "authority_level": "primary",
            "url": "https://members-api.parliament.uk/api/Members/185/ContributionSummary?page=1",
            "repository_path": "research/complete-mp-reports/jeremy-corbyn/current-parliament-spoken-contributions-v1.json",
            "server_path": "",
            "publication_date": None,
            "capture_date": capture_date,
            "coverage_from": EXPECTED_DATE_FROM,
            "coverage_to": EXPECTED_DATE_TO,
            "checksum": f"sha256:{members_manifest_sha}",
            "limitations": "The member index is used to enumerate and reconcile debate rows. Its displayed contribution totals and category counts are approximate navigation evidence and are not used as the accepted individual-contribution count.",
        },
        {
            "source_id": HANSARD_SOURCE_ID,
            "title": "UK Parliament Hansard API — Jeremy Corbyn current-Parliament spoken contributions",
            "publisher": "UK Parliament",
            "source_type": "parliamentary_record",
            "authority_level": "primary",
            "url": "https://hansard-api.parliament.uk/search/contributions/Spoken.json",
            "repository_path": "research/complete-mp-reports/jeremy-corbyn/current-parliament-spoken-contributions-v1.json",
            "server_path": "",
            "publication_date": None,
            "capture_date": capture_date,
            "coverage_from": EXPECTED_DATE_FROM,
            "coverage_to": EXPECTED_DATE_TO,
            "checksum": f"sha256:{hansard_manifest_sha}",
            "limitations": "Hansard is an edited record and the live result set may later change. The captured debate payload exposed numeric source value 2 rather than an explicit documented corrected/rolling label, so all 306 accepted records retain the raw value and are classified as source status unspecified without inference.",
        },
    ]

    facts: list[dict] = []
    for record in records:
        contribution_id = record["contribution_external_id"]
        fact_id = "fact-spoken-contribution-" + contribution_id.lower()
        facts.append(
            {
                "fact_id": fact_id,
                "section_id": SECTION_ID,
                "statement": (
                    f"On {record['sitting_date']}, official Hansard records "
                    f"Jeremy Corbyn making contribution {contribution_id} in "
                    f"{record['debate_title']!r} in the {record['venue']}."
                ),
                "fact_type": "speech",
                "date": record["sitting_date"],
                "date_from": None,
                "date_to": None,
                "source_ids": [MEMBERS_SOURCE_ID, HANSARD_SOURCE_ID],
                "confidence": "high",
                "evidence_status": "verified",
                "notes": (
                    "The official ContentItemExtId matches the full-debate "
                    "Items[].ExternalId for member ID 185 and the separate "
                    "Hansard spoken-search record. Exact official text and "
                    "metadata are preserved in the source packet. No topic "
                    "classification, summary of political meaning, policy "
                    "position, contradiction, motive, influence, accuracy, "
                    "legality, propriety or significance inference is made."
                ),
            }
        )

    gap = {
        "gap_id": GAP_ID,
        "section_id": SECTION_ID,
        "summary": (
            "The fixture covers 90 Commons written questions tabled in the "
            "current Parliament and 306 individual Commons Chamber or "
            "Westminster Hall spoken contributions by Jeremy Corbyn from "
            "17 July 2024 through 16 July 2026. Remaining gaps include written "
            "questions and spoken contributions before 4 July 2024, later "
            "question updates, future contributions and later Hansard "
            "corrections, tabled oral questions, written statements, Early Day "
            "Motions, committee oral evidence and any future unresolved "
            "official records."
        ),
        "severity": "high",
        "reason": "historic_gap",
        "date_from": None,
        "date_to": capture_date,
        "status": "open",
        "blocks_publication": True,
        "next_action": (
            "Open separately authorised lanes for pre-current-Parliament "
            "written questions and spoken contributions, future refreshes, "
            "tabled oral questions, written statements, Early Day Motions and "
            "committee oral evidence."
        ),
        "notes": (
            "The fixed capture reconciled 202 authorised debate rows to 306 "
            "unique official contribution identifiers with zero unresolved "
            "records after normalising the official permalink resolver's "
            "site-relative paths to the official Hansard host. All source "
            "status values remain unspecified because the payload exposed raw "
            "numeric value 2 without an explicit corrected/rolling label."
        ),
    }

    repaired_reconciliation: list[dict] = []
    for item in capture["debate_reconciliation"]:
        repaired = dict(item)
        repaired["accepted_segment_count"] = len(
            repaired["member_contribution_external_ids"]
        )
        repaired["unresolved_segment_count"] = 0
        repaired_reconciliation.append(repaired)

    packet = {
        "schema_version": "1",
        "packet_id": "jeremy-corbyn-current-parliament-spoken-contributions-v1",
        "subject": {
            "official_name": "Jeremy Corbyn",
            "uk_parliament_member_id": "185",
        },
        "section_id": SECTION_ID,
        "captured_at": EXPECTED_CAPTURE_TIMESTAMP,
        "scope": {
            "house": "House of Commons",
            "venues": ["Commons Chamber", "Westminster Hall"],
            "record_type": "individual_spoken_contribution_segments",
            "from_date": "2024-07-04",
            "to_capture_boundary": "2026-07-21",
            "accepted_date_from": EXPECTED_DATE_FROM,
            "accepted_date_to": EXPECTED_DATE_TO,
            "topic_classification_included": False,
            "summarisation_included": False,
            "policy_position_inference_included": False,
            "contradiction_analysis_included": False,
        },
        "capture_source": {
            "workflow_run_id": 29820459172,
            "workflow_artifact_id": FIXED_ARTIFACT_ID,
            "workflow_artifact_digest": FIXED_ARTIFACT_DIGEST,
            "filename": "capture-diagnostic.json",
            "byte_length": FIXED_CAPTURE_BYTE_LENGTH,
            "sha256": FIXED_CAPTURE_SHA256,
            "original_result": "permalink_normalisation_stop",
            "original_parser_issue": "The official Hansard permalink resolver returned valid site-relative /Commons/... paths. The diagnostic required an absolute https URL and therefore held every otherwise reconciled segment at the permalink stage.",
            "repair_basis": "All 306 held segments had already passed exact member, debate, identifier, date, venue and text-presence checks. The preserved relative paths are normalised only by prefixing https://hansard.parliament.uk. No official record was re-requested, altered, summarised or inferred during reconciliation.",
        },
        "official_api_contracts": {
            "members_index": "/api/Members/{id}/ContributionSummary?page={page}",
            "hansard_spoken_search": "/search/contributions/Spoken.json with house, date, memberId, skip, take and orderBy parameters",
            "member_debate_segments": "/debates/memberdebatecontributions/{memberId}.json?debateSectionExtId={id}",
            "full_debate": "/debates/debate/{debateSectionExtId}.json",
            "permalink_resolver": "/search/parlisearchredirect.json?externalId={externalId}",
        },
        "stable_identifier_method": {
            "primary": "official ContentItemExtId",
            "required_match": "exact full-debate Items[].ExternalId",
            "required_member_id": MEMBER_ID,
            "duplicate_policy": "reject duplicate exact contribution identifiers",
            "missing_or_unmatched_policy": "hold unresolved; never synthesize a key",
        },
        "five_explicit_results": {
            "captured_debate_row_count": EXPECTED_DEBATE_ROWS,
            "unique_individual_contribution_count": EXPECTED_CONTRIBUTIONS,
            "stable_identifier_method": "official ContentItemExtId matched exactly to full-debate Items[].ExternalId with MemberId 185",
            "exact_date_coverage": {
                "earliest_accepted_contribution_date": EXPECTED_DATE_FROM,
                "latest_accepted_contribution_date": EXPECTED_DATE_TO,
                "capture_timestamp_utc": EXPECTED_CAPTURE_TIMESTAMP,
            },
            "unresolved_record_count": 0,
        },
        "capture_checks": {
            "member_index_page_count": 11,
            "member_index_all_rows_fetched": 220,
            "member_index_rows_in_date_boundary": 203,
            "member_index_authorised_debate_rows": EXPECTED_DEBATE_ROWS,
            "member_index_excluded_rows": 1,
            "hansard_search_page_count": 4,
            "hansard_search_reported_spoken_count": EXPECTED_CONTRIBUTIONS,
            "hansard_search_unique_external_id_count": EXPECTED_CONTRIBUTIONS,
            "hansard_search_duplicate_external_id_count": 0,
            "accepted_unique_contribution_count": EXPECTED_CONTRIBUTIONS,
            "unresolved_record_count": 0,
            "official_request_count": 725,
            "venue_counts": venue_counts,
            "contribution_type_counts": {"Spoken": EXPECTED_CONTRIBUTIONS},
            "source_status_counts": dict(
                Counter(item["source_status"] for item in records)
            ),
            "source_raw_value_counts": {
                str(key): count
                for key, count in Counter(
                    item["source_raw_value"] for item in records
                ).items()
            },
            "member_index_displayed_total_contributions_sum": 306,
            "member_index_displayed_category_counts": capture[
                "capture_counts"
            ]["member_index_displayed_category_counts"],
            "member_index_displayed_category_sum": 271,
            "member_index_counts_used_as_authority": False,
            "raw_capture_manifest_canonical_sha256": capture["raw_capture"][
                "manifest_canonical_sha256"
            ],
            "raw_capture_total_response_bytes": capture["raw_capture"][
                "total_response_bytes"
            ],
        },
        "source_boundary": {
            "included": [
                "Official UK Parliament Members API contribution-summary pages required to cross the 4 July 2024 boundary",
                "Official Hansard spoken-contribution search records for Commons member ID 185",
                "Official Hansard member-by-debate segment responses, full debate responses and permalink resolver responses",
                "Commons Chamber and Westminster Hall individual contribution segments",
            ],
            "excluded": [
                "The Written Corrections row dated 22 October 2025",
                "Pre-4-July-2024 contributions and records after the fixed capture boundary",
                "Committee oral evidence, video or audio transcription, written statements, Early Day Motions, votes and tabled oral-question datasets",
                "Media, party, campaign, personal, social-media and commercial parliamentary sources",
                "Topic classification, summary of political meaning, policy-position inference and contradiction analysis",
            ],
        },
        "sources": sources,
        "records": records,
        "facts": facts,
        "coverage_gaps": [gap],
        "member_index_pages": capture["member_index_pages"],
        "hansard_search_pages": capture["hansard_search_pages"],
        "debate_reconciliation": repaired_reconciliation,
        "excluded_records": capture["exclusions"],
        "unresolved_records": [],
        "raw_capture": capture["raw_capture"],
        "decisions": {
            "section_status": "partial",
            "publication_status": "not_ready",
            "human_review_required": True,
            "public_output_authorised": False,
            "notes": "One neutral speech fact is created per accepted official contribution segment. The capture adds no claim, interpretation, relationship or policy-position record.",
        },
    }
    return packet


def preservation_hashes(report: dict) -> dict:
    return {
        "sources_before_spoken_lane": canonical_sha256(report["sources"]),
        "facts_before_spoken_lane": canonical_sha256(report["facts"]),
        "sections_except_speeches_and_questions": canonical_sha256(
            [
                item
                for item in report["sections"]
                if item["section_id"] != SECTION_ID
            ]
        ),
        "claims": canonical_sha256(report["claims"]),
        "interpretations": canonical_sha256(report["interpretations"]),
        "relationships": canonical_sha256(report["relationships"]),
        "publication": canonical_sha256(report["publication"]),
    }


def integrate_fixture(packet: dict) -> None:
    report = load_json(FIXTURE_PATH)
    validate_report(report)
    packet["preservation_hashes"] = preservation_hashes(report)

    speeches = section(report, SECTION_ID)
    existing_question_ids = [
        fact_id
        for fact_id in speeches["fact_ids"]
        if fact_id.startswith("fact-written-question-")
    ]
    assert len(existing_question_ids) == 90
    assert speeches["fact_ids"] == existing_question_ids
    assert speeches["claim_ids"] == []
    assert speeches["interpretation_ids"] == []
    assert speeches["relationship_ids"] == []
    assert speeches["gap_ids"] == [GAP_ID]

    report_sources = by_id(report["sources"], "source_id")
    report_facts = by_id(report["facts"], "fact_id")
    assert MEMBERS_SOURCE_ID not in report_sources
    assert HANSARD_SOURCE_ID not in report_sources
    assert not any(
        fact_id.startswith("fact-spoken-contribution-")
        for fact_id in report_facts
    )

    report["sources"].extend(packet["sources"])
    report["facts"].extend(packet["facts"])
    speech_fact_ids = [item["fact_id"] for item in packet["facts"]]
    speeches["fact_ids"].extend(speech_fact_ids)
    speeches["summary"] = (
        "Official UK Parliament records identify 90 Commons written questions "
        "tabled by Jeremy Corbyn in the current Parliament and 306 individual "
        "Commons Chamber or Westminster Hall spoken contributions from 17 July "
        "2024 through the fixed 21 July 2026 capture. Earlier and future records, "
        "later corrections and adjacent parliamentary record types remain outside "
        "the completed bounded baselines."
    )

    gap_map = by_id(report["coverage_gaps"], "gap_id")
    old_gap = gap_map[GAP_ID]
    gap_index = report["coverage_gaps"].index(old_gap)
    report["coverage_gaps"][gap_index] = packet["coverage_gaps"][0]

    validate_report(report)
    PACKET_PATH.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    FIXTURE_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    SOURCE_NOTE_PATH.write_text(render_source_note(packet), encoding="utf-8", newline="\n")


def render_source_note(packet: dict) -> str:
    checks = packet["capture_checks"]
    five = packet["five_explicit_results"]
    return f"""# Jeremy Corbyn current-Parliament spoken contributions — source note v1

## Result

The fixed official-source capture recorded:

- **{five['captured_debate_row_count']}** authorised member-index debate rows;
- **{five['unique_individual_contribution_count']}** unique individual spoken contribution segments;
- official `ContentItemExtId` identifiers matched exactly to full-debate `Items[].ExternalId` values for member ID `185`;
- accepted dates from **{five['exact_date_coverage']['earliest_accepted_contribution_date']}** through **{five['exact_date_coverage']['latest_accepted_contribution_date']}**;
- capture timestamp **{five['exact_date_coverage']['capture_timestamp_utc']}**;
- **{five['unresolved_record_count']}** unresolved records after the official site-relative permalink paths were normalised to the official Hansard host.

## Official request shapes

1. `GET https://members-api.parliament.uk/api/Members/185/ContributionSummary?page={{page}}`
2. `GET https://hansard-api.parliament.uk/search/contributions/Spoken.json` with `house=Commons`, the fixed date boundary, `memberId=185`, `skip`, `take=100` and `orderBy=SittingDateAsc`.
3. `GET https://hansard-api.parliament.uk/debates/memberdebatecontributions/185.json?debateSectionExtId={{id}}`
4. `GET https://hansard-api.parliament.uk/debates/debate/{{id}}.json`
5. `GET https://hansard-api.parliament.uk/search/parlisearchredirect.json?externalId={{id}}`

The capture made **{checks['official_request_count']}** polite sequential official requests: 11 Members API requests and 714 Hansard API requests. The raw request manifest checksum is `{checks['raw_capture_manifest_canonical_sha256']}`.

## Reconciliation

The Members API pages returned 220 rows before crossing the date boundary. Of 203 rows inside the authorised date period, 202 were Commons Chamber or Westminster Hall rows and one `Written Corrections` row was excluded. The 202 authorised rows resolved to 306 member segments. Each accepted segment required:

- an official `ContentItemExtId`;
- one exact full-debate `ExternalId` match;
- full-debate member ID `185`;
- matching debate ID, date and venue;
- non-empty official contribution text;
- one matching Hansard spoken-search result;
- one official permalink resolver response.

The resolver returned valid site-relative `/Commons/...` paths. The fixed packet prefixes only `https://hansard.parliament.uk`; it does not invent or rewrite the returned path.

## Counts

- Commons Chamber: {checks['venue_counts']['Commons Chamber']}
- Westminster Hall: {checks['venue_counts']['Westminster Hall']}
- Contribution endpoint type `Spoken`: {checks['contribution_type_counts']['Spoken']}
- Source status `unspecified`: {checks['source_status_counts']['unspecified']}

The debate payload exposed raw source value `2`, but not an explicit corrected, rolling or uncorrected label. The packet therefore preserves `2` and classifies the status as `unspecified` rather than inferring an enum mapping.

The member-index rows displayed 306 total contributions, while their displayed category counters summed to 271. Those approximate counters are retained as navigation evidence only and are not used to classify individual segments.

## Fixed-capture provenance

- Workflow run: `29820459172`
- Artifact ID: `{FIXED_ARTIFACT_ID}`
- Artifact digest: `{FIXED_ARTIFACT_DIGEST}`
- Diagnostic byte length: `{FIXED_CAPTURE_BYTE_LENGTH}`
- Diagnostic SHA-256: `{FIXED_CAPTURE_SHA256}`

## Exclusions and interpretation boundary

The capture excludes pre-4-July-2024 contributions, future records and later corrections, committee oral evidence, video/audio transcription, written statements, Early Day Motions, votes, tabled oral-question datasets and non-official sources.

No topic classification, summarisation of political meaning, policy-position inference, contradiction analysis, motive, influence, accuracy, legality, propriety or significance claim is made. The report remains `partial`, `not_ready`, human-review-required and unauthorised for public output.
"""


def current_preservation_hashes(report: dict, packet: dict) -> dict:
    new_source_ids = {item["source_id"] for item in packet["sources"]}
    new_fact_ids = {item["fact_id"] for item in packet["facts"]}
    return {
        "sources_before_spoken_lane": canonical_sha256(
            [
                item
                for item in report["sources"]
                if item["source_id"] not in new_source_ids
            ]
        ),
        "facts_before_spoken_lane": canonical_sha256(
            [
                item
                for item in report["facts"]
                if item["fact_id"] not in new_fact_ids
            ]
        ),
        "sections_except_speeches_and_questions": canonical_sha256(
            [
                item
                for item in report["sections"]
                if item["section_id"] != SECTION_ID
            ]
        ),
        "claims": canonical_sha256(report["claims"]),
        "interpretations": canonical_sha256(report["interpretations"]),
        "relationships": canonical_sha256(report["relationships"]),
        "publication": canonical_sha256(report["publication"]),
    }


def test_packet_and_fixture() -> None:
    packet = load_json(PACKET_PATH)
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    assert packet["packet_id"] == (
        "jeremy-corbyn-current-parliament-spoken-contributions-v1"
    )
    assert packet["captured_at"] == EXPECTED_CAPTURE_TIMESTAMP
    assert packet["five_explicit_results"] == {
        "captured_debate_row_count": EXPECTED_DEBATE_ROWS,
        "unique_individual_contribution_count": EXPECTED_CONTRIBUTIONS,
        "stable_identifier_method": "official ContentItemExtId matched exactly to full-debate Items[].ExternalId with MemberId 185",
        "exact_date_coverage": {
            "earliest_accepted_contribution_date": EXPECTED_DATE_FROM,
            "latest_accepted_contribution_date": EXPECTED_DATE_TO,
            "capture_timestamp_utc": EXPECTED_CAPTURE_TIMESTAMP,
        },
        "unresolved_record_count": 0,
    }
    checks = packet["capture_checks"]
    assert checks["member_index_authorised_debate_rows"] == EXPECTED_DEBATE_ROWS
    assert checks["accepted_unique_contribution_count"] == EXPECTED_CONTRIBUTIONS
    assert checks["unresolved_record_count"] == 0
    assert checks["venue_counts"] == EXPECTED_VENUE_COUNTS
    assert checks["contribution_type_counts"] == {"Spoken": 306}
    assert checks["source_status_counts"] == {"unspecified": 306}
    assert checks["source_raw_value_counts"] == {"2": 306}
    assert checks["member_index_counts_used_as_authority"] is False

    records = packet["records"]
    assert len(records) == EXPECTED_CONTRIBUTIONS
    record_ids = [item["contribution_external_id"] for item in records]
    assert len(set(record_ids)) == EXPECTED_CONTRIBUTIONS
    assert records[0]["sitting_date"] == EXPECTED_DATE_FROM
    assert records[-1]["sitting_date"] == EXPECTED_DATE_TO
    for record in records:
        assert record["member_id"] == MEMBER_ID
        assert record["house"] == "Commons"
        assert record["venue"] in EXPECTED_VENUE_COUNTS
        assert record["contribution_type"] == "Spoken"
        assert record["full_text"].strip()
        permalink = urlparse(record["official_permalink"])
        assert permalink.scheme == "https"
        assert permalink.netloc == "hansard.parliament.uk"
        assert all(record["reconciliation_evidence"].values())

    packet_sources = by_id(packet["sources"], "source_id")
    report_sources = by_id(report["sources"], "source_id")
    assert set(packet_sources) == {MEMBERS_SOURCE_ID, HANSARD_SOURCE_ID}
    for source_id, source in packet_sources.items():
        assert report_sources[source_id] == source

    packet_facts = by_id(packet["facts"], "fact_id")
    report_facts = by_id(report["facts"], "fact_id")
    assert len(packet_facts) == EXPECTED_CONTRIBUTIONS
    expected_speech_fact_ids = [
        "fact-spoken-contribution-" + item.lower() for item in record_ids
    ]
    assert list(packet_facts) == expected_speech_fact_ids
    for fact_id, fact in packet_facts.items():
        assert report_facts[fact_id] == fact
        assert fact["fact_type"] == "speech"
        assert fact["source_ids"] == [MEMBERS_SOURCE_ID, HANSARD_SOURCE_ID]
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert "No topic classification" in fact["notes"]

    speeches = section(report, SECTION_ID)
    question_fact_ids = [
        fact_id
        for fact_id in speeches["fact_ids"]
        if fact_id.startswith("fact-written-question-")
    ]
    assert len(question_fact_ids) == 90
    assert speeches["fact_ids"][:90] == question_fact_ids
    assert speeches["fact_ids"][90:] == expected_speech_fact_ids
    assert speeches["status"] == "partial"
    assert speeches["claim_ids"] == []
    assert speeches["interpretation_ids"] == []
    assert speeches["relationship_ids"] == []
    assert speeches["gap_ids"] == [GAP_ID]

    packet_gap = packet["coverage_gaps"][0]
    report_gap = by_id(report["coverage_gaps"], "gap_id")[GAP_ID]
    assert report_gap == packet_gap
    assert report_gap["status"] == "open"
    assert report_gap["blocks_publication"] is True
    for phrase in (
        "written questions",
        "spoken contributions",
        "oral questions",
        "written statements",
        "Early Day Motions",
        "committee oral evidence",
    ):
        assert phrase.casefold() in (
            report_gap["summary"] + " " + report_gap["next_action"]
        ).casefold()

    assert current_preservation_hashes(report, packet) == packet[
        "preservation_hashes"
    ]
    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False


def test_deterministic_generation() -> None:
    report = load_json(FIXTURE_PATH)
    validate_report(report)
    with (
        tempfile.TemporaryDirectory() as first_dir,
        tempfile.TemporaryDirectory() as second_dir,
    ):
        first = Path(first_dir)
        second = Path(second_dir)
        write_outputs(report, first)
        write_outputs(report, second)
        first_outputs = {
            path.name: path.read_bytes()
            for path in sorted(first.iterdir())
            if path.is_file()
        }
        second_outputs = {
            path.name: path.read_bytes()
            for path in sorted(second.iterdir())
            if path.is_file()
        }
        assert set(first_outputs) == EXPECTED_OUTPUTS
        assert first_outputs == second_outputs
        profile = first_outputs[
            "corbyn-jeremy-full-profile.md"
        ].decode("utf-8")
        source_register = first_outputs[
            "corbyn-jeremy-source-register.md"
        ].decode("utf-8")
        coverage = first_outputs[
            "corbyn-jeremy-coverage-report.md"
        ].decode("utf-8")
        assert "306 individual" in section(
            report, SECTION_ID
        )["summary"]
        for contribution_id in (
            "6B949895-BD1C-46C3-AC29-9BC88A1B26E2",
            "74CCA2F1-4F0F-4F65-8974-686D8A2BFA58",
        ):
            assert contribution_id in profile
        assert MEMBERS_SOURCE_ID in source_register
        assert HANSARD_SOURCE_ID in source_register
        assert GAP_ID in coverage


def integrate_capture(path: Path) -> None:
    capture = load_fixed_capture(path)
    packet = build_packet(capture)
    integrate_fixture(packet)
    test_packet_and_fixture()
    test_deterministic_generation()
    print(
        "PASS - fixed Jeremy Corbyn spoken-contributions capture integrated"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--integrate-capture",
        type=Path,
        help="Integrate the frozen workflow capture into the five authorised files.",
    )
    args = parser.parse_args(argv)
    if args.integrate_capture:
        integrate_capture(args.integrate_capture)
    else:
        test_packet_and_fixture()
        test_deterministic_generation()
        print(
            "PASS - Jeremy Corbyn current-Parliament spoken contributions baseline v1"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
