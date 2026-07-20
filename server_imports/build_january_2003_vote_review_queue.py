#!/usr/bin/env python3
"""Build a deterministic, read-only January 2003 vote-review queue.

The SQLite evidence cache is opened in read-only/query-only mode. The script
writes only the requested JSON and Markdown review packets beneath the
configured archive root. It never assigns political meaning or changes source
evidence, review state, or database content.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "january-2003-vote-review-queue-v1"
DEFAULT_ARCHIVE_ROOT = "/srv/story-evidence-collector"
DEFAULT_DATABASE_PATH = "db/mp_evidence_cache.sqlite"
DEFAULT_OUTPUT_DIR = "reports/review-queues/january-2003"
DEFAULT_JSON_FILENAME = "january-2003-vote-review-queue.json"
DEFAULT_MARKDOWN_FILENAME = "january-2003-vote-review-queue.md"
DEFAULT_DATE_FROM = "2003-01-01"
DEFAULT_DATE_TO = "2003-01-31"

REVIEW_FIELDS = (
    "decision",
    "reviewed_meaning",
    "evidence_url",
    "notes",
    "reviewer",
    "reviewed_at",
)

REQUIRED_COLUMNS = {
    "member_votes": {
        "vote_key",
        "source_system",
        "division_key",
        "member_key",
        "target_mp",
        "recorded_vote",
        "vote_side",
        "meaning_quality",
        "source_url",
        "source_path",
        "source_trace",
    },
    "divisions": {
        "division_key",
        "source_system",
        "division_id",
        "division_date",
        "division_title",
        "house",
        "source_url",
        "source_path",
        "source_trace",
    },
}

TECHNICAL_STATE_MAP = {
    ("aye", "mp_found_in_aye_list"): "recorded_aye",
    ("no", "mp_found_in_no_list"): "recorded_no",
    ("not recorded", "mp_not_found_in_sample_division"): "not_recorded",
    ("not recorded", "mp_not_found_in_division"): "not_recorded",
}


class QueueValidationError(ValueError):
    """Raised when a review queue cannot be emitted safely."""


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise QueueValidationError("Configuration JSON must be an object.")
    return data


def resolve_inside_root(root: Path, relative_or_absolute: str | Path) -> Path:
    candidate = Path(relative_or_absolute)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved_root = root.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise QueueValidationError(
            f"Unsafe path outside archive root: {candidate}"
        ) from exc
    return resolved_candidate


def validate_filename(filename: str, expected_suffix: str) -> str:
    candidate = Path(filename)
    if candidate.name != filename or candidate.suffix.lower() != expected_suffix:
        raise QueueValidationError(
            f"Output filename must be a plain {expected_suffix} filename: {filename!r}"
        )
    return filename


def open_read_only_database(database_path: Path) -> sqlite3.Connection:
    if not database_path.exists():
        raise QueueValidationError(f"Database does not exist: {database_path}")
    if not database_path.is_file():
        raise QueueValidationError(f"Database path is not a file: {database_path}")

    uri = f"file:{database_path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON;")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def _table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }


def validate_database_shape(connection: sqlite3.Connection) -> None:
    for table, required in REQUIRED_COLUMNS.items():
        present = _table_columns(connection, table)
        missing = sorted(required - present)
        if missing:
            raise QueueValidationError(
                f"Database table {table!r} is missing required columns: "
                + ", ".join(missing)
            )


def _normalise_token(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def classify_technical_state(
    recorded_vote: Any,
    vote_side: Any,
    evidence_status: Any,
) -> str:
    recorded = _normalise_token(recorded_vote)
    side = _normalise_token(vote_side)
    status = _normalise_token(evidence_status)

    if not recorded or not side or recorded != side:
        return "source_ambiguity"
    return TECHNICAL_STATE_MAP.get((recorded, status), "source_ambiguity")


def _required_text(value: Any, field: str, vote_key: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise QueueValidationError(
            f"{vote_key or '<unknown vote>'}: incomplete record: {field} is blank."
        )
    return text


def _parse_trace(raw_trace: Any, field: str, vote_key: str) -> dict[str, Any]:
    raw_text = _required_text(raw_trace, field, vote_key)
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise QueueValidationError(
            f"{vote_key}: incomplete record: {field} is not valid JSON."
        ) from exc
    if not isinstance(value, dict):
        raise QueueValidationError(
            f"{vote_key}: incomplete record: {field} must decode to an object."
        )
    return value


def _trace_first(trace: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = trace.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _assert_same_if_present(
    canonical: str,
    trace_value: str,
    label: str,
    vote_key: str,
) -> None:
    if trace_value and canonical != trace_value:
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: {label} differs between "
            "canonical record and source trace."
        )


def _fetch_rows(
    connection: sqlite3.Connection,
    date_from: str,
    date_to: str,
    target_mp: str,
) -> list[sqlite3.Row]:
    sql = """
        SELECT
          mv.vote_key,
          mv.source_system AS vote_source_system,
          mv.division_key,
          mv.member_key,
          mv.target_mp,
          mv.recorded_vote,
          mv.vote_side,
          mv.meaning_quality,
          mv.source_url AS vote_source_url,
          mv.source_path AS vote_source_path,
          mv.source_trace AS vote_source_trace,
          d.source_system AS division_source_system,
          d.division_id,
          d.division_date,
          d.division_title,
          d.house,
          d.source_url AS division_source_url,
          d.source_path AS division_source_path,
          d.source_trace AS division_source_trace
        FROM member_votes AS mv
        JOIN divisions AS d ON d.division_key = mv.division_key
        WHERE d.division_date >= ? AND d.division_date <= ?
    """
    parameters: list[Any] = [date_from, date_to]
    if target_mp:
        sql += " AND mv.target_mp = ?"
        parameters.append(target_mp)
    sql += " ORDER BY d.division_date, d.division_id, mv.vote_key"
    return connection.execute(sql, parameters).fetchall()


def _build_item(row: sqlite3.Row, position: int) -> dict[str, Any]:
    vote_key = _required_text(row["vote_key"], "vote_key", "")
    division_key = _required_text(row["division_key"], "division_key", vote_key)
    division_id = _required_text(row["division_id"], "division_id", vote_key)
    division_date = _required_text(row["division_date"], "division_date", vote_key)
    division_title = _required_text(
        row["division_title"], "division_title", vote_key
    )
    target_mp = _required_text(row["target_mp"], "target_mp", vote_key)
    member_key = _required_text(row["member_key"], "member_key", vote_key)
    recorded_vote = _required_text(
        row["recorded_vote"], "recorded_vote", vote_key
    )
    vote_side = _required_text(row["vote_side"], "vote_side", vote_key)
    meaning_quality = _required_text(
        row["meaning_quality"], "meaning_quality", vote_key
    )
    source_system = _required_text(
        row["vote_source_system"], "source_system", vote_key
    )

    if source_system != "parlparse":
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: expected parlparse, found "
            f"{source_system!r}."
        )
    if row["division_source_system"] != source_system:
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: vote and division source systems differ."
        )
    if meaning_quality != "needs_review":
        raise QueueValidationError(
            f"{vote_key}: record is outside this lane because meaning_quality is "
            f"{meaning_quality!r}, not 'needs_review'."
        )

    vote_trace = _parse_trace(
        row["vote_source_trace"], "member_votes.source_trace", vote_key
    )
    division_trace = _parse_trace(
        row["division_source_trace"], "divisions.source_trace", vote_key
    )
    if vote_trace != division_trace:
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: member-vote and division source traces differ."
        )

    source_url = _required_text(
        row["vote_source_url"] or row["division_source_url"],
        "source_url",
        vote_key,
    )
    vote_source_url = str(row["vote_source_url"] or "")
    division_source_url = str(row["division_source_url"] or "")
    if vote_source_url and division_source_url and vote_source_url != division_source_url:
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: vote and division source URLs differ."
        )

    source_xml_url = _required_text(
        _trace_first(vote_trace, "source_xml_url", "sourceXmlUrl"),
        "source_xml_url",
        vote_key,
    )
    evidence_status = _required_text(
        _trace_first(vote_trace, "evidence_status", "evidenceStatus"),
        "evidence_status",
        vote_key,
    )

    _assert_same_if_present(
        division_id,
        _trace_first(vote_trace, "division_id", "divisionId"),
        "division_id",
        vote_key,
    )
    _assert_same_if_present(
        division_date,
        _trace_first(vote_trace, "division_date", "divisionDate", "date"),
        "division_date",
        vote_key,
    )
    _assert_same_if_present(
        division_title,
        _trace_first(
            vote_trace,
            "division_title",
            "divisionTitle",
            "motion_title",
            "title",
            "subject",
        ),
        "division_title",
        vote_key,
    )
    _assert_same_if_present(
        recorded_vote,
        _trace_first(
            vote_trace,
            "recorded_vote",
            "recordedVote",
            "recorded_side",
            "vote_side",
            "side",
        ),
        "recorded_vote",
        vote_key,
    )
    _assert_same_if_present(
        source_url,
        _trace_first(vote_trace, "source_url", "sourceUrl"),
        "source_url",
        vote_key,
    )
    _assert_same_if_present(
        meaning_quality,
        _trace_first(vote_trace, "meaning_quality", "meaningQuality"),
        "meaning_quality",
        vote_key,
    )

    queue_state = classify_technical_state(
        recorded_vote, vote_side, evidence_status
    )
    if queue_state == "source_ambiguity":
        raise QueueValidationError(
            f"{vote_key}: source_ambiguity: recorded vote, vote side and "
            "evidence status do not form an authorised technical state."
        )

    return {
        "queue_position": position,
        "queue_state": queue_state,
        "division": {
            "division_key": division_key,
            "division_id": division_id,
            "division_date": division_date,
            "division_title": division_title,
            "house": str(row["house"] or ""),
            "source_url": source_url,
            "source_xml_url": source_xml_url,
        },
        "vote": {
            "vote_key": vote_key,
            "member_key": member_key,
            "target_mp": target_mp,
            "recorded_vote": recorded_vote,
            "vote_side": vote_side,
            "evidence_status": evidence_status,
            "meaning_quality": meaning_quality,
        },
        "source_trace": vote_trace,
        "review": {field: "" for field in REVIEW_FIELDS},
    }


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schema_version") != SCHEMA_VERSION:
        raise QueueValidationError("Packet schema_version is missing or incorrect.")
    scope = packet.get("scope")
    items = packet.get("items")
    if not isinstance(scope, dict) or not isinstance(items, list) or not items:
        raise QueueValidationError("Packet must contain a scope object and non-empty items list.")
    if scope.get("row_count") != len(items):
        raise QueueValidationError("Packet row_count does not match items length.")

    positions = [item.get("queue_position") for item in items]
    if positions != list(range(1, len(items) + 1)):
        raise QueueValidationError("Queue positions are not deterministic and contiguous.")

    vote_keys: set[str] = set()
    for item in items:
        state = item.get("queue_state")
        if state not in {"recorded_aye", "recorded_no", "not_recorded"}:
            raise QueueValidationError(
                f"Packet contains a refused technical state: {state!r}."
            )
        review = item.get("review")
        if not isinstance(review, dict) or tuple(review.keys()) != REVIEW_FIELDS:
            raise QueueValidationError("Reviewer fields are missing or out of order.")
        if any(review[field] != "" for field in REVIEW_FIELDS):
            raise QueueValidationError("Reviewer-decision fields must remain blank.")
        vote = item.get("vote", {})
        if vote.get("meaning_quality") != "needs_review":
            raise QueueValidationError(
                "This queue may contain only existing needs_review records."
            )
        vote_key = str(vote.get("vote_key") or "")
        if not vote_key or vote_key in vote_keys:
            raise QueueValidationError("Queue contains a missing or duplicate vote_key.")
        vote_keys.add(vote_key)


def build_packet(
    database_path: Path,
    *,
    date_from: str = DEFAULT_DATE_FROM,
    date_to: str = DEFAULT_DATE_TO,
    target_mp: str = "",
    expected_row_count: int | None = None,
) -> dict[str, Any]:
    if date_from > date_to:
        raise QueueValidationError("date_from must not be later than date_to.")
    if expected_row_count is not None and expected_row_count < 1:
        raise QueueValidationError("expected_row_count must be at least 1.")

    with open_read_only_database(database_path) as connection:
        validate_database_shape(connection)
        rows = _fetch_rows(connection, date_from, date_to, target_mp)

    if not rows:
        raise QueueValidationError(
            "No member-vote rows matched the requested date and target scope."
        )

    targets = sorted({str(row["target_mp"] or "").strip() for row in rows})
    if "" in targets:
        raise QueueValidationError("Matched rows contain a blank target_mp.")
    if not target_mp and len(targets) != 1:
        raise QueueValidationError(
            "Matched rows contain multiple target MPs; select one explicitly."
        )
    resolved_target = target_mp or targets[0]

    if expected_row_count is not None and len(rows) != expected_row_count:
        raise QueueValidationError(
            f"Expected {expected_row_count} rows but found {len(rows)}."
        )

    items = [_build_item(row, index) for index, row in enumerate(rows, start=1)]
    packet = {
        "schema_version": SCHEMA_VERSION,
        "scope": {
            "date_from": date_from,
            "date_to": date_to,
            "target_mp": resolved_target,
            "row_count": len(items),
        },
        "items": items,
    }
    validate_packet(packet)
    return packet


def serialise_packet(packet: dict[str, Any]) -> str:
    validate_packet(packet)
    return json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _markdown_text(value: Any) -> str:
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def render_markdown(packet: dict[str, Any]) -> str:
    validate_packet(packet)
    scope = packet["scope"]
    lines = [
        "# January 2003 Vote Review Queue",
        "",
        "This packet is a deterministic, read-only review aid. Recorded sides are "
        "technical source facts, not political interpretations.",
        "",
        f"- Target MP: `{_markdown_text(scope['target_mp'])}`",
        f"- Date range: `{scope['date_from']}` to `{scope['date_to']}`",
        f"- Records: `{scope['row_count']}`",
        f"- Schema: `{packet['schema_version']}`",
        "",
    ]

    for item in packet["items"]:
        division = item["division"]
        vote = item["vote"]
        review = item["review"]
        lines.extend(
            [
                f"## {item['queue_position']:03d} — "
                f"{_markdown_text(division['division_date'])} — "
                f"{_markdown_text(division['division_title'])}",
                "",
                f"- Queue state: `{item['queue_state']}`",
                f"- Division key: `{_markdown_text(division['division_key'])}`",
                f"- Division ID: `{_markdown_text(division['division_id'])}`",
                f"- Vote key: `{_markdown_text(vote['vote_key'])}`",
                f"- Member key: `{_markdown_text(vote['member_key'])}`",
                f"- Target MP: `{_markdown_text(vote['target_mp'])}`",
                f"- Recorded vote: `{_markdown_text(vote['recorded_vote'])}`",
                f"- Vote side: `{_markdown_text(vote['vote_side'])}`",
                f"- Evidence status: `{_markdown_text(vote['evidence_status'])}`",
                f"- Meaning quality: `{_markdown_text(vote['meaning_quality'])}`",
                f"- Source URL: {_markdown_text(division['source_url'])}",
                f"- Source XML URL: {_markdown_text(division['source_xml_url'])}",
                "",
                "### Source trace — preserved",
                "",
                "```json",
                json.dumps(
                    item["source_trace"],
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                "```",
                "",
                "### Reviewer fields — intentionally blank",
                "",
                f"- Decision: {review['decision']}",
                f"- Reviewed meaning: {review['reviewed_meaning']}",
                f"- Evidence URL: {review['evidence_url']}",
                f"- Notes: {review['notes']}",
                f"- Reviewer: {review['reviewer']}",
                f"- Reviewed at: {review['reviewed_at']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _atomic_write(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise QueueValidationError(
            f"Output already exists; use --overwrite after review: {path}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_packet(
    packet: dict[str, Any],
    output_dir: Path,
    *,
    json_filename: str = DEFAULT_JSON_FILENAME,
    markdown_filename: str = DEFAULT_MARKDOWN_FILENAME,
    overwrite: bool = False,
) -> tuple[Path, Path]:
    validate_packet(packet)
    validate_filename(json_filename, ".json")
    validate_filename(markdown_filename, ".md")

    json_path = output_dir / json_filename
    markdown_path = output_dir / markdown_filename
    if not overwrite:
        existing = [path for path in (json_path, markdown_path) if path.exists()]
        if existing:
            raise QueueValidationError(
                "Output already exists; use --overwrite after review: "
                + ", ".join(str(path) for path in existing)
            )

    json_content = serialise_packet(packet)
    markdown_content = render_markdown(packet)
    _atomic_write(json_path, json_content, overwrite=True)
    _atomic_write(markdown_path, markdown_content, overwrite=True)
    return json_path, markdown_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the deterministic January 2003 vote-review queue."
    )
    parser.add_argument("--config", type=Path)
    parser.add_argument("--archive-root")
    parser.add_argument("--database-path")
    parser.add_argument("--output-dir")
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--target-mp")
    parser.add_argument("--expected-row-count", type=int)
    parser.add_argument("--json-filename")
    parser.add_argument("--markdown-filename")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing generated packet files after deliberate review.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        queue_config = config.get("vote_review_queue", {})
        if not isinstance(queue_config, dict):
            raise QueueValidationError("vote_review_queue configuration must be an object.")

        archive_root = Path(
            args.archive_root
            or config.get("archive_root")
            or DEFAULT_ARCHIVE_ROOT
        )
        database_path = resolve_inside_root(
            archive_root,
            args.database_path
            or config.get("database_path")
            or DEFAULT_DATABASE_PATH,
        )
        output_dir = resolve_inside_root(
            archive_root,
            args.output_dir
            or queue_config.get("output_dir")
            or DEFAULT_OUTPUT_DIR,
        )
        date_from = (
            args.date_from
            or queue_config.get("date_from")
            or DEFAULT_DATE_FROM
        )
        date_to = (
            args.date_to
            or queue_config.get("date_to")
            or DEFAULT_DATE_TO
        )
        target_mp = str(
            args.target_mp
            if args.target_mp is not None
            else queue_config.get("target_mp", "")
        ).strip()

        expected_row_count = args.expected_row_count
        if expected_row_count is None:
            configured_count = queue_config.get("expected_row_count")
            expected_row_count = (
                int(configured_count)
                if configured_count not in (None, "")
                else None
            )

        json_filename = (
            args.json_filename
            or queue_config.get("json_filename")
            or DEFAULT_JSON_FILENAME
        )
        markdown_filename = (
            args.markdown_filename
            or queue_config.get("markdown_filename")
            or DEFAULT_MARKDOWN_FILENAME
        )

        packet = build_packet(
            database_path,
            date_from=str(date_from),
            date_to=str(date_to),
            target_mp=target_mp,
            expected_row_count=expected_row_count,
        )
        json_path, markdown_path = write_packet(
            packet,
            output_dir,
            json_filename=str(json_filename),
            markdown_filename=str(markdown_filename),
            overwrite=args.overwrite,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "database_mode": "read_only",
                    "network_access_used": False,
                    "row_count": packet["scope"]["row_count"],
                    "json_path": str(json_path),
                    "markdown_path": str(markdown_path),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (OSError, sqlite3.Error, QueueValidationError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "database_mode": "read_only",
                    "network_access_used": False,
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
