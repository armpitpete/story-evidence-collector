#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn regulated-donee donations v1."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from generate_complete_mp_report import load_json, validate_report, write_outputs

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "regulated-donee-donations-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

EXPORT_SOURCE_ID = (
    "source-electoral-commission-corbyn-"
    "regulated-donee-export-2026-07-20"
)
GUIDANCE_SOURCE_ID = (
    "source-electoral-commission-regulated-donee-guidance"
)
RAW_SHA256 = "d4edcdef02eacfc4d33212878627193d5905ef095bd35badf8c803a6c2251f99"
EXPECTED_COLUMNS = [
    "ECRef",
    "RegulatedEntityName",
    "RegulatedEntityType",
    "Value",
    "AcceptedDate",
    "AccountingUnitName",
    "DonorName",
    "AccountingUnitsAsCentralParty",
    "IsSponsorship",
    "DonorStatus",
    "RegulatedDoneeType",
    "CompanyRegistrationNumber",
    "Postcode",
    "DonationType",
    "NatureOfDonation",
    "PurposeOfVisit",
    "DonationAction",
    "ReceivedDate",
    "ReportedDate",
    "IsReportedPrePoll",
    "ReportingPeriodName",
    "IsBequest",
    "IsAggregation",
    "RegulatedEntityId",
    "AccountingUnitId",
    "DonorId",
    "CampaigningName",
    "RegisterName",
    "IsIrishSource",
]
DONATION_TYPE_COUNTS = {
    "Cash": 18,
    "Impermissible Donor": 1,
    "Non Cash": 10,
    "Unidentified Donor": 1,
    "Visit": 10,
}
DONATION_TYPE_TOTALS = {
    "Cash": Decimal("329912.19"),
    "Impermissible Donor": Decimal("1000.00"),
    "Non Cash": Decimal("64792.76"),
    "Unidentified Donor": Decimal("3000.00"),
    "Visit": Decimal("30921.47"),
}
DONEE_TYPE_COUNTS = {
    "Leadership Candidate": 13,
    "MP - Member of Parliament": 14,
    "Member of Registered Political Party": 13,
}
DONOR_STATUS_COUNTS = {
    "Company": 3,
    "Impermissible Donor": 1,
    "Individual": 8,
    "Other": 5,
    "Trade Union": 18,
    "Unidentifiable Donor": 1,
    "Unincorporated Association": 4,
}
EXPECTED_OUTPUTS = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}


def load_packet() -> dict:
    value = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def by_id(records: list[dict], key: str) -> dict[str, dict]:
    result = {item[key]: item for item in records}
    assert len(result) == len(records), f"Duplicate {key}"
    return result


def section(report: dict, section_id: str) -> dict:
    return next(
        item
        for item in report["sections"]
        if item["section_id"] == section_id
    )


def money(value: str) -> Decimal:
    return Decimal(value.replace("£", "").replace(",", ""))


def reconstruct_raw_csv(packet: dict) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=packet["raw_export"]["columns"],
        lineterminator="\r\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()
    for record in packet["records"]:
        writer.writerow(record["fields"])
    return b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")


def test_packet_capture() -> None:
    packet = load_packet()

    assert packet["section_id"] == "donations_and_political_finance"
    assert packet["subject"] == {
        "official_name": "Jeremy Corbyn",
        "electoral_commission_entity_name": "Mr Jeremy Corbyn MP",
        "electoral_commission_entity_id": "1600",
    }

    query = packet["query"]
    assert query["regulated_group"] == "Regulated donee"
    assert query["search_type"] == "Donations"
    assert query["search_text"] == "Jeremy Corbyn"
    assert query["pre_poll_included"] is True
    assert query["post_poll_included"] is True
    assert query["time_restriction"] is None

    raw = packet["raw_export"]
    assert raw["displayed_result_count"] == 40
    assert raw["export_row_count"] == 40
    assert raw["page_count"] == 2
    assert raw["column_count"] == 29
    assert raw["columns"] == EXPECTED_COLUMNS
    assert raw["byte_length"] == 11085
    assert raw["sha256"] == RAW_SHA256
    assert "43 was incorrect" in raw["provisional_count_correction"]

    records = packet["records"]
    assert len(records) == 40
    records_by_id = by_id(records, "record_id")
    assert len(records_by_id) == 40

    reconstructed = reconstruct_raw_csv(packet)
    assert len(reconstructed) == raw["byte_length"]
    assert hashlib.sha256(reconstructed).hexdigest() == RAW_SHA256

    fields = [record["fields"] for record in records]
    assert {item["RegulatedEntityName"] for item in fields} == {
        "Mr Jeremy Corbyn MP"
    }
    assert {item["RegulatedEntityType"] for item in fields} == {
        "Regulated Donee"
    }
    assert {item["RegulatedEntityId"] for item in fields} == {"1600"}
    assert {item["RegisterName"] for item in fields} == {"Great Britain"}

    assert Counter(item["DonationType"] for item in fields) == (
        DONATION_TYPE_COUNTS
    )
    assert Counter(item["RegulatedDoneeType"] for item in fields) == (
        DONEE_TYPE_COUNTS
    )
    assert Counter(item["DonorStatus"] for item in fields) == (
        DONOR_STATUS_COUNTS
    )

    totals: dict[str, Decimal] = {}
    for item in fields:
        totals.setdefault(item["DonationType"], Decimal("0"))
        totals[item["DonationType"]] += money(item["Value"])
    assert totals == DONATION_TYPE_TOTALS
    assert sum(totals.values()) == Decimal("429626.42")

    accepted_rows = [item for item in fields if item["AcceptedDate"]]
    returned_rows = [item for item in fields if not item["AcceptedDate"]]
    assert len(accepted_rows) == 38
    assert len(returned_rows) == 2
    assert sum(money(item["Value"]) for item in accepted_rows) == Decimal(
        "425626.42"
    )
    assert sum(money(item["Value"]) for item in returned_rows) == Decimal(
        "4000.00"
    )

    impermissible = records_by_id["I0260286"]["fields"]
    assert impermissible["DonationType"] == "Impermissible Donor"
    assert impermissible["DonorStatus"] == "Impermissible Donor"
    assert impermissible["DonationAction"] == "Returned"
    assert impermissible["AcceptedDate"] == ""

    unidentified = records_by_id["U0248096"]["fields"]
    assert unidentified["DonationType"] == "Unidentified Donor"
    assert unidentified["DonorStatus"] == "Unidentifiable Donor"
    assert unidentified["DonorName"] == ""
    assert unidentified["DonationAction"] == "Returned"
    assert unidentified["AcceptedDate"] == ""

    assert records_by_id["V0033114"]["fields"]["IsAggregation"] == "True"

    leading_space_ids = {
        record["record_id"]
        for record in records
        if record["fields"]["DonorName"]
        != record["fields"]["DonorName"].lstrip()
    }
    assert leading_space_ids == {
        "V0833966",
        "NC0260285",
        "NC0260284",
        "C0256326",
        "C0250138",
        "C0221123",
    }

    sources = by_id(packet["sources"], "source_id")
    assert set(sources) == {EXPORT_SOURCE_ID, GUIDANCE_SOURCE_ID}

    export_source = sources[EXPORT_SOURCE_ID]
    assert export_source["publisher"] == "Electoral Commission"
    assert export_source["source_type"] == "regulator"
    assert export_source["authority_level"] == "primary"
    assert export_source["checksum"] == f"sha256:{RAW_SHA256}"
    parsed = urlparse(export_source["url"])
    assert parsed.scheme == "https"
    assert parsed.netloc == "search.electoralcommission.org.uk"

    guidance_source = sources[GUIDANCE_SOURCE_ID]
    assert guidance_source["publisher"] == "Electoral Commission"
    assert guidance_source["source_type"] == "official_secondary"


def test_fixture_integration() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    packet_sources = by_id(packet["sources"], "source_id")
    packet_facts = by_id(packet["facts"], "fact_id")
    packet_gaps = by_id(packet["coverage_gaps"], "gap_id")

    report_sources = by_id(report["sources"], "source_id")
    report_facts = by_id(report["facts"], "fact_id")
    report_gaps = by_id(report["coverage_gaps"], "gap_id")

    expected_fact_ids = [
        f"fact-regulated-donee-donation-{record['record_id'].lower()}"
        for record in packet["records"]
    ]
    assert len(expected_fact_ids) == 40
    assert list(packet_facts) == expected_fact_ids

    donations = section(report, "donations_and_political_finance")
    assert donations["status"] == "partial"
    assert donations["fact_ids"] == expected_fact_ids
    assert donations["claim_ids"] == []
    assert donations["interpretation_ids"] == []
    assert donations["relationship_ids"] == []
    assert donations["gap_ids"] == [
        "gap-donations-political-finance-scope"
    ]

    for source_id, source in packet_sources.items():
        assert source == report_sources[source_id]

    for fact_id, fact in packet_facts.items():
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "donations_and_political_finance"
        assert fact["fact_type"] == "donation"
        assert fact["source_ids"] == [EXPORT_SOURCE_ID]
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"

    assert packet_facts[
        "fact-regulated-donee-donation-i0260286"
    ]["date"] is None
    assert "marked Returned" in packet_facts[
        "fact-regulated-donee-donation-i0260286"
    ]["statement"]

    assert packet_facts[
        "fact-regulated-donee-donation-u0248096"
    ]["date"] is None
    assert "[blank donor name]" in packet_facts[
        "fact-regulated-donee-donation-u0248096"
    ]["statement"]

    assert set(packet_gaps) == {
        "gap-donations-political-finance-scope"
    }
    assert packet_gaps[
        "gap-donations-political-finance-scope"
    ] == report_gaps["gap-donations-political-finance-scope"]
    assert "gap-donations" not in report_gaps
    assert report_gaps[
        "gap-donations-political-finance-scope"
    ]["status"] == "open"
    assert report_gaps[
        "gap-donations-political-finance-scope"
    ]["blocks_publication"] is True

    assert not any(
        item["section_id"] == "donations_and_political_finance"
        for item in report["claims"]
    )
    assert not any(
        item["section_id"] == "donations_and_political_finance"
        for item in report["interpretations"]
    )
    assert not any(
        item["section_id"] == "donations_and_political_finance"
        for item in report["relationships"]
    )

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

        for ec_ref in [
            "V0833967",
            "C0594073",
            "NC0260285",
            "I0260286",
            "U0248096",
        ]:
            assert ec_ref in profile

        assert EXPORT_SOURCE_ID in source_register
        assert GUIDANCE_SOURCE_ID in source_register
        assert "gap-donations-political-finance-scope" in coverage


def main() -> int:
    test_packet_capture()
    test_fixture_integration()
    test_deterministic_generation()
    print(
        "PASS - Jeremy Corbyn regulated-donee donations baseline v1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
