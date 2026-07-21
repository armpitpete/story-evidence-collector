#!/usr/bin/env python3
"""One-shot official-source diagnostic for the authorised spoken-contributions lane."""

from __future__ import annotations

import hashlib
import json
import os
import sys
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
            with urlopen(req, timeout=60) as response:
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


def recursive_key_values(value: object, wanted: tuple[str, ...]) -> dict[str, list[object]]:
    found = {key: [] for key in wanted}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, item in node.items():
                if key in found:
                    found[key].append(item)
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return {key: vals for key, vals in found.items() if vals}


def date_strings(value: object) -> list[str]:
    keys = (
        "date", "Date", "sittingDate", "SittingDate", "contributionDate",
        "ContributionDate", "debateDate", "DebateDate"
    )
    values = recursive_key_values(value, keys)
    dates: list[str] = []
    for candidates in values.values():
        for candidate in candidates:
            if isinstance(candidate, str) and len(candidate) >= 10:
                text = candidate[:10]
                if text[4:5] == "-" and text[7:8] == "-":
                    dates.append(text)
    return sorted(set(dates))


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
    page = 1
    while page <= 30:
        url = f"https://members-api.parliament.uk/api/Members/{MEMBER_ID}/ContributionSummary?page={page}"
        try:
            payload, meta = fetch_json(url)
        except Exception as exc:
            diagnostic["failures"].append({"stage": "members_page", "page": page, "error": str(exc)})
            break
        diagnostic["requests"].append(meta)
        items = first_list(payload)
        dates = date_strings(items)
        member_pages.append({
            "page": page,
            "item_count": len(items),
            "dates": dates,
            "payload": payload,
            "metadata": meta,
        })
        print(f"Members page {page}: {len(items)} items; dates={dates[:1]}..{dates[-1:]}")
        if dates and min(dates) <= START_DATE:
            break
        if not items:
            break
        page += 1
        time.sleep(0.25)
    diagnostic["members_pages"] = member_pages

    query = urlencode({
        "queryParameters.house": "Commons",
        "queryParameters.startDate": START_DATE,
        "queryParameters.endDate": CAPTURE_END_DATE,
        "queryParameters.memberId": str(MEMBER_ID),
        "queryParameters.skip": "0",
        "queryParameters.take": "1000",
        "queryParameters.orderBy": "SittingDateAsc",
    })
    hansard_url = f"https://hansard-api.parliament.uk/search/contributions/Spoken.json?{query}"
    try:
        payload, meta = fetch_json(hansard_url)
        diagnostic["requests"].append(meta)
        diagnostic["hansard_search"] = {"payload": payload, "metadata": meta}
        diagnostic["hansard_search_shape"] = {
            "top_level_type": type(payload).__name__,
            "top_level_keys": sorted(payload) if isinstance(payload, dict) else [],
            "result_count_guess": len(first_list(payload)),
            "first_result_key_values": recursive_key_values(
                first_list(payload)[:1],
                (
                    "MemberId", "memberId", "DebateSectionExtId", "debateSectionExtId",
                    "ContributionExtId", "contributionExtId", "ExternalId", "externalId",
                    "SittingDate", "sittingDate", "House", "house", "Section", "section",
                    "ContributionText", "contributionText", "ContributionType", "contributionType",
                ),
            ),
        }
        print(json.dumps(diagnostic["hansard_search_shape"], indent=2, ensure_ascii=False))
    except Exception as exc:
        diagnostic["failures"].append({"stage": "hansard_search", "error": str(exc), "url": hansard_url})

    encoded = json.dumps(diagnostic, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    OUT.write_bytes(encoded)
    print(f"Wrote {OUT} ({len(encoded)} bytes; sha256={hashlib.sha256(encoded).hexdigest()})")
    return 0 if not diagnostic["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
