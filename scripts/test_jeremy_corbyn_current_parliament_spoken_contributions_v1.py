#!/usr/bin/env python3
"""Resolve official UK Parliament spoken-contribution response shapes."""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

MEMBER_ID = 185
START_DATE = "2024-07-04"
CAPTURE_END_DATE = os.environ.get("CAPTURE_END_DATE", datetime.now(timezone.utc).date().isoformat())
OUT = Path(os.environ.get("CAPTURE_OUTPUT", "capture-diagnostic.json"))
UA = "story-evidence-collector/1.0 (+https://github.com/armpitpete/story-evidence-collector)"


def fetch(url: str, attempts: int = 4) -> tuple[bytes, dict]:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urlopen(req, timeout=90) as response:
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


def fetch_json(url: str) -> tuple[object, dict]:
    raw, metadata = fetch(url)
    try:
        return json.loads(raw.decode("utf-8-sig")), metadata
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


def main() -> int:
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    diagnostic: dict[str, object] = {
        "captured_at": captured_at,
        "member_id": MEMBER_ID,
        "start_date": START_DATE,
        "end_date": CAPTURE_END_DATE,
        "requests": [],
        "failures": [],
    }

    member_pages: list[dict] = []
    authorised_rows: list[dict] = []
    page = 1
    crossed_boundary = False
    while page <= 30 and not crossed_boundary:
        url = f"https://members-api.parliament.uk/api/Members/{MEMBER_ID}/ContributionSummary?page={page}"
        payload, meta = fetch_json(url)
        diagnostic["requests"].append(meta)
        items = first_list(payload)
        member_pages.append({"page": page, "payload": payload, "metadata": meta})
        dates: list[str] = []
        for item in items:
            value = item.get("value", {}) if isinstance(item, dict) else {}
            sitting_date = str(value.get("sittingDate", ""))[:10]
            if sitting_date:
                dates.append(sitting_date)
            if sitting_date >= START_DATE and value.get("section") in {"Commons Chamber", "Westminster Hall"}:
                authorised_rows.append(item)
            if sitting_date and sitting_date < START_DATE:
                crossed_boundary = True
        print(f"Members page {page}: {len(items)} items; {min(dates) if dates else '?'} to {max(dates) if dates else '?'}")
        page += 1
        time.sleep(0.2)

    diagnostic["members_pages"] = member_pages
    diagnostic["authorised_rows"] = authorised_rows
    diagnostic["member_index_summary"] = {
        "pages_requested": len(member_pages),
        "authorised_row_count": len(authorised_rows),
        "date_from": min(item["value"]["sittingDate"][:10] for item in authorised_rows),
        "date_to": max(item["value"]["sittingDate"][:10] for item in authorised_rows),
        "sections": {
            section: sum(item["value"]["section"] == section for item in authorised_rows)
            for section in ("Commons Chamber", "Westminster Hall")
        },
    }

    samples: list[dict] = []
    for item in authorised_rows[:3]:
        value = item["value"]
        ext_id = value["debateWebsiteId"]
        member_url = (
            f"https://hansard-api.parliament.uk/debates/memberdebatecontributions/{MEMBER_ID}.json?"
            + urlencode({"debateSectionExtId": ext_id})
        )
        debate_url = f"https://hansard-api.parliament.uk/debates/debate/{ext_id}.json"
        member_payload, member_meta = fetch_json(member_url)
        debate_payload, debate_meta = fetch_json(debate_url)
        diagnostic["requests"].extend([member_meta, debate_meta])
        samples.append({
            "index_item": item,
            "member_contributions": member_payload,
            "member_contributions_metadata": member_meta,
            "debate": debate_payload,
            "debate_metadata": debate_meta,
        })
        print(f"Sample {ext_id}: member type={type(member_payload).__name__}; debate type={type(debate_payload).__name__}")
        time.sleep(0.2)
    diagnostic["detail_samples"] = samples

    search_variants: list[dict] = []
    variants = [
        {
            "queryParameters.house": "Commons",
            "queryParameters.startDate": START_DATE,
            "queryParameters.endDate": CAPTURE_END_DATE,
            "queryParameters.memberId": str(MEMBER_ID),
            "queryParameters.skip": "0",
            "queryParameters.take": "20",
            "queryParameters.orderBy": "SittingDateAsc",
        },
        {
            "queryParameters.house": "Commons",
            "queryParameters.startDate": START_DATE + "T00:00:00",
            "queryParameters.endDate": CAPTURE_END_DATE + "T23:59:59",
            "queryParameters.memberId": str(MEMBER_ID),
            "queryParameters.skip": "0",
            "queryParameters.take": "20",
            "queryParameters.orderBy": "SittingDateAsc",
        },
        {
            "house": "Commons",
            "startDate": START_DATE,
            "endDate": CAPTURE_END_DATE,
            "memberId": str(MEMBER_ID),
            "skip": "0",
            "take": "20",
            "orderBy": "SittingDateAsc",
        },
        {
            "queryParameters.memberId": str(MEMBER_ID),
            "queryParameters.take": "20",
        },
    ]
    for number, params in enumerate(variants, 1):
        url = "https://hansard-api.parliament.uk/search/contributions/Spoken.json?" + urlencode(params)
        try:
            payload, meta = fetch_json(url)
            diagnostic["requests"].append(meta)
            search_variants.append({"number": number, "parameters": params, "payload": payload, "metadata": meta})
            print(f"Search variant {number}: {type(payload).__name__} {list(payload) if isinstance(payload, dict) else len(payload)}")
        except Exception as exc:
            search_variants.append({"number": number, "parameters": params, "error": str(exc)})
            diagnostic["failures"].append({"stage": "search_variant", "number": number, "error": str(exc)})
    diagnostic["search_variants"] = search_variants

    encoded = json.dumps(diagnostic, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    OUT.write_bytes(encoded)
    print(f"Wrote {OUT} ({len(encoded)} bytes; sha256={hashlib.sha256(encoded).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
