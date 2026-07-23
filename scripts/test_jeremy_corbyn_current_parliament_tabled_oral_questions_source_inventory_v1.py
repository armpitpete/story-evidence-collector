#!/usr/bin/env python3
"""Controlled capture probe for the authorised tabled oral-questions inventory lane."""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = (
    "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list"
    "?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100"
)
OUT = Path("probe-output")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        URL,
        headers={"Accept": "application/json", "User-Agent": "story-evidence-collector/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        status = response.status
        content_type = response.headers.get("Content-Type")
    parsed = json.loads(raw)
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    sha256 = hashlib.sha256(raw).hexdigest()
    (OUT / "member-query-response.json").write_bytes(raw)
    (OUT / "capture-metadata.json").write_text(
        json.dumps(
            {
                "captured_at_utc": captured_at,
                "content_type": content_type,
                "http_status": status,
                "raw_sha256": sha256,
                "url": URL,
                "paging": parsed.get("PagingInfo"),
                "record_count": len(parsed.get("Response") or []),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"CAPTURED_AT={captured_at}")
    print(f"RAW_SHA256={sha256}")
    print(f"RECORD_COUNT={len(parsed.get('Response') or [])}")
    print(f"PAGING={json.dumps(parsed.get('PagingInfo'), sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
