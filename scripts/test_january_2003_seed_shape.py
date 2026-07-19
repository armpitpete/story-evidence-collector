#!/usr/bin/env python3
"""One-time branch bootstrap; replaced by the final regression test in the next commit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one match in {path}: {old[:80]!r}; found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_between(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def patch_importer() -> None:
    path = ROOT / "server_imports/build_server_evidence_cache.py"
    replace_once(
        path,
        '- seed imports require an explicit local rows file\n',
        '- seed imports require an explicit local rows file\n- source-shaped batches may use an explicit reviewed manifest for batch context\n',
    )
    replace_once(
        path,
        'IMPORTER_VERSION = "0.2"\nDEFAULT_ARCHIVE_ROOT = "/srv/story-evidence-collector"\nDEFAULT_MINIMUM_FREE_GB = 40\n',
        '''IMPORTER_VERSION = "0.3"\nDEFAULT_ARCHIVE_ROOT = "/srv/story-evidence-collector"\nDEFAULT_MINIMUM_FREE_GB = 40\n\nTARGET_MP_ALIASES = ("target_mp", "targetMp", "member_name", "memberName", "mp_name", "name")\nTARGET_MEMBER_ID_ALIASES = ("target_member_id", "member_id", "memberId", "source_member_id")\nRECORDED_VOTE_ALIASES = (\n    "recorded_vote",\n    "recordedVote",\n    "vote",\n    "member_vote",\n    "memberVote",\n    "side",\n    "recorded_side",\n)\nVOTE_SIDE_ALIASES = ("vote_side", "voteSide", "side", "recorded_side")\n''',
    )
    replace_once(
        path,
        '    seed_id: str = ""\n    seed_rows_path: str = ""\n    rows_read: int = 0\n',
        '    seed_id: str = ""\n    seed_rows_path: str = ""\n    seed_manifest_path: str = ""\n    rows_read: int = 0\n',
    )
    replace_once(
        path,
        '            "seed_id": self.seed_id,\n            "seed_rows_path": self.seed_rows_path,\n            "rows_read": self.rows_read,\n',
        '            "seed_id": self.seed_id,\n            "seed_rows_path": self.seed_rows_path,\n            "seed_manifest_path": self.seed_manifest_path,\n            "rows_read": self.rows_read,\n',
    )

    replacement = '''def load_seed_manifest(path: Path | None) -> dict[str, Any]:\n    if path is None:\n        return {}\n    if not path.exists():\n        raise FileNotFoundError(f"Seed manifest file not found: {path}")\n    data = json.loads(path.read_text(encoding="utf-8"))\n    if not isinstance(data, dict):\n        raise ValueError("Seed manifest JSON must be an object.")\n    return data\n\n\ndef validate_seed_context(seed_id: str, seed_context: dict[str, Any]) -> None:\n    context_id = str(first_value(seed_context, "batch_id", "seed_id"))\n    if context_id and context_id != seed_id:\n        raise ValueError(\n            f"Seed manifest identity mismatch: expected {seed_id!r}, found {context_id!r}."\n        )\n\n\ndef normalise_seed_row(\n    row: dict[str, Any],\n    seed_id: str,\n    seed_path: Path,\n    seed_context: dict[str, Any] | None = None,\n) -> tuple[dict[str, Any] | None, str | None]:\n    context = seed_context if isinstance(seed_context, dict) else {}\n    source_system = str(first_value(row, "source_system", "sourceSystem") or "parlparse")\n    division_id = str(first_value(row, "division_id", "divisionId", "division_number", "source_division_id", "id"))\n    division_date = str(first_value(row, "division_date", "divisionDate", "date"))\n    target_mp = str(first_value(row, *TARGET_MP_ALIASES) or first_value(context, *TARGET_MP_ALIASES))\n\n    missing = [\n        name\n        for name, value in (\n            ("division_id", division_id),\n            ("division_date", division_date),\n            ("target_mp", target_mp),\n        )\n        if not value\n    ]\n    if missing:\n        return None, f"Skipped row missing required fields: {', '.join(missing)}"\n\n    source_member_id = str(\n        first_value(row, *TARGET_MEMBER_ID_ALIASES)\n        or first_value(context, *TARGET_MEMBER_ID_ALIASES)\n    )\n    member_key = f"{source_system}|member|{source_member_id or target_mp}"\n    division_key = f"{source_system}|division|{division_id}"\n    vote_key = f"{source_system}|{division_id}|{target_mp}"\n\n    recorded_vote = str(first_value(row, *RECORDED_VOTE_ALIASES))\n    vote_side = str(first_value(row, *VOTE_SIDE_ALIASES) or recorded_vote)\n    source_url = str(first_value(row, "source_url", "sourceUrl"))\n    source_path = str(first_value(row, "source_path", "sourcePath") or seed_path)\n    division_title = str(first_value(row, "division_title", "divisionTitle", "title", "motion_title", "subject"))\n    house = str(first_value(row, "house") or "commons")\n    meaning_quality = str(first_value(row, "meaning_quality", "meaningQuality") or "needs_review")\n\n    if source_system == "parlparse":\n        meaning_quality = "needs_review"\n\n    trace = json.dumps(row, sort_keys=True, ensure_ascii=False)\n\n    return {\n        "source_id": f"seed:{seed_id}",\n        "source_system": source_system,\n        "source_name": seed_id,\n        "source_path": source_path,\n        "member_key": member_key,\n        "source_member_id": source_member_id,\n        "target_mp": target_mp,\n        "division_key": division_key,\n        "division_id": division_id,\n        "division_date": division_date,\n        "division_title": division_title,\n        "house": house,\n        "vote_key": vote_key,\n        "recorded_vote": recorded_vote,\n        "vote_side": vote_side,\n        "meaning_quality": meaning_quality,\n        "source_url": source_url,\n        "source_trace": trace,\n    }, None\n'''
    replace_between(path, "def normalise_seed_row(", "\n\n\ndef apply_seed_rows(", replacement)
    replace_once(
        path,
        '    import_run_id: str,\n) -> tuple[int, int, list[str]]:\n',
        '    import_run_id: str,\n    seed_context: dict[str, Any] | None = None,\n) -> tuple[int, int, list[str]]:\n',
    )
    replace_once(
        path,
        '            normalised, error = normalise_seed_row(row, seed_id, seed_path)\n',
        '            normalised, error = normalise_seed_row(row, seed_id, seed_path, seed_context)\n',
    )
    replace_once(
        path,
        '    parser.add_argument("--seed-rows", type=Path, help="Local JSON rows file for the seed import. No web fetch is performed.")\n',
        '    parser.add_argument("--seed-rows", type=Path, help="Local JSON rows file for the seed import. No web fetch is performed.")\n    parser.add_argument("--seed-manifest", type=Path, help="Reviewed local batch manifest supplying target identity context when rows use source shape.")\n',
    )
    replace_once(
        path,
        '    seed_rows_value = args.seed_rows or seed_config.get("rows_path") or ""\n    seed_rows_path = Path(seed_rows_value) if seed_rows_value else None\n',
        '    seed_rows_value = args.seed_rows or seed_config.get("rows_path") or ""\n    seed_rows_path = Path(seed_rows_value) if seed_rows_value else None\n    seed_manifest_value = args.seed_manifest or seed_config.get("manifest_path") or ""\n    seed_manifest_path = Path(seed_manifest_value) if seed_manifest_value else None\n',
    )
    replace_once(
        path,
        '        seed_id=str(seed_id),\n        seed_rows_path=str(seed_rows_path or ""),\n',
        '        seed_id=str(seed_id),\n        seed_rows_path=str(seed_rows_path or ""),\n        seed_manifest_path=str(seed_manifest_path or ""),\n',
    )

    seed_block = '''        if seed_rows_path is not None:\n            if not seed_id:\n                result.errors.append("Seed rows path was supplied without --seed-id or seed_import.seed_id.")\n            else:\n                try:\n                    seed_rows = load_seed_rows(seed_rows_path)\n                    seed_context = load_seed_manifest(seed_manifest_path)\n                    validate_seed_context(str(seed_id), seed_context)\n                    result.rows_read = len(seed_rows)\n\n                    if args.apply:\n                        if not db_path.exists():\n                            result.errors.append(f"Database does not exist yet: {db_path}")\n                        else:\n                            written, skipped, messages = apply_seed_rows(\n                                db_path,\n                                str(seed_id),\n                                seed_rows_path,\n                                seed_rows,\n                                import_run_id,\n                                seed_context=seed_context,\n                            )\n                            result.rows_written = written\n                            result.rows_skipped = skipped\n                            result.warnings.extend(messages)\n                    else:\n                        skipped = 0\n                        for row in seed_rows:\n                            _, error = normalise_seed_row(\n                                row,\n                                str(seed_id),\n                                seed_rows_path,\n                                seed_context,\n                            )\n                            if error:\n                                skipped += 1\n                                result.warnings.append(error)\n                        result.rows_skipped = skipped\n                        result.warnings.append("Seed rows checked in dry-run mode; database was not written.")\n                except Exception as exc:\n                    result.errors.append(f"Seed import failed: {exc}")\n'''
    replace_between(path, "        if seed_rows_path is not None:\n", "\n        if not args.no_log", seed_block)


def patch_audit() -> None:
    path = ROOT / "server_imports/audit_server_state.py"
    replace_once(
        path,
        'DEFAULT_SEED_ROWS = Path("parlparse_batches/parlparse_2003_01_rows.json")\n',
        '''DEFAULT_SEED_ROWS = Path("parlparse_batches/parlparse_2003_01_rows.json")\nDEFAULT_SEED_MANIFEST = Path("parlparse_batches/parlparse_2003_01_manifest.json")\nTARGET_MP_ALIASES = ("target_mp", "targetMp", "member_name", "memberName", "mp_name", "name")\nRECORDED_VOTE_ALIASES = (\n    "recorded_vote",\n    "recordedVote",\n    "vote",\n    "member_vote",\n    "memberVote",\n    "side",\n    "recorded_side",\n)\n''',
    )
    replacement = '''def first_value(row: dict[str, Any], *keys: str) -> Any:\n    for key in keys:\n        value = row.get(key)\n        if value not in (None, ""):\n            return value\n    return ""\n\n\ndef inspect_seed_rows(seed_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:\n    manifest_file = (\n        path_summary(manifest_path, include_hash=manifest_path.is_file())\n        if manifest_path is not None\n        else {"path": "", "exists": False, "is_file": False, "is_dir": False}\n    )\n    result: dict[str, Any] = {\n        "file": path_summary(seed_path, include_hash=seed_path.is_file()),\n        "manifest": manifest_file,\n        "row_count": 0,\n        "source_shape_missing_canonical_field_counts": {},\n        "normalised_missing_required_field_counts": {},\n        "missing_required_field_counts": {},\n        "meaning_quality_counts": {},\n        "normalisation": {\n            "classification": "not_available",\n            "target_mp_resolution": "unresolved",\n            "recorded_vote_resolution": "unresolved",\n            "source_trace_policy": "preserve_original_row",\n            "evidence_meaning_changed": False,\n        },\n        "errors": [],\n    }\n    if not seed_path.is_file():\n        return result\n\n    try:\n        data = json.loads(seed_path.read_text(encoding="utf-8"))\n        rows = extract_rows_container(data)\n        result["row_count"] = len(rows)\n\n        manifest: dict[str, Any] = {}\n        if manifest_path is not None and manifest_path.is_file():\n            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))\n            if not isinstance(manifest_data, dict):\n                raise ValueError("Seed manifest JSON must be an object.")\n            manifest = manifest_data\n\n        canonical_fields = ("division_id", "division_date", "target_mp", "recorded_vote")\n        source_missing = {\n            field: sum(1 for row in rows if row.get(field) in (None, ""))\n            for field in canonical_fields\n        }\n        result["source_shape_missing_canonical_field_counts"] = source_missing\n\n        context_target_mp = first_value(manifest, *TARGET_MP_ALIASES)\n        required_resolvers = {\n            "division_id": lambda row: first_value(\n                row, "division_id", "divisionId", "division_number", "source_division_id", "id"\n            ),\n            "division_date": lambda row: first_value(row, "division_date", "divisionDate", "date"),\n            "target_mp": lambda row: first_value(row, *TARGET_MP_ALIASES) or context_target_mp,\n            "recorded_vote": lambda row: first_value(row, *RECORDED_VOTE_ALIASES),\n        }\n        normalised_missing = {\n            field: sum(1 for row in rows if resolver(row) in (None, ""))\n            for field, resolver in required_resolvers.items()\n        }\n        result["normalised_missing_required_field_counts"] = normalised_missing\n        result["missing_required_field_counts"] = dict(normalised_missing)\n\n        raw_target_rows = sum(1 for row in rows if first_value(row, *TARGET_MP_ALIASES))\n        recorded_side_rows = sum(1 for row in rows if row.get("recorded_side") not in (None, ""))\n        raw_recorded_vote_rows = sum(1 for row in rows if row.get("recorded_vote") not in (None, ""))\n        if rows and not any(normalised_missing.values()):\n            classification = "expected_source_import_distinction_with_explicit_normalisation_boundary"\n        else:\n            classification = "unresolved_missing_import_fields"\n        result["normalisation"] = {\n            "classification": classification,\n            "target_mp_resolution": (\n                "row"\n                if raw_target_rows == len(rows) and rows\n                else "manifest"\n                if context_target_mp and raw_target_rows < len(rows)\n                else "unresolved"\n            ),\n            "recorded_vote_resolution": (\n                "recorded_vote"\n                if raw_recorded_vote_rows == len(rows) and rows\n                else "recorded_side_alias"\n                if recorded_side_rows == len(rows) and rows\n                else "mixed_or_unresolved"\n            ),\n            "source_trace_policy": "preserve_original_row",\n            "evidence_meaning_changed": False,\n        }\n\n        quality_counts: dict[str, int] = {}\n        for row in rows:\n            quality = str(row.get("meaning_quality") or row.get("meaningQuality") or "")\n            quality_counts[quality] = quality_counts.get(quality, 0) + 1\n        result["meaning_quality_counts"] = quality_counts\n    except (OSError, json.JSONDecodeError, ValueError) as exc:\n        result["errors"].append(str(exc))\n\n    return result\n'''
    replace_between(path, "def inspect_seed_rows(", "\n\n\ndef newest_files(", replacement)
    replace_once(
        path,
        '    seed_path = repo_root / DEFAULT_SEED_ROWS\n',
        '    seed_path = repo_root / DEFAULT_SEED_ROWS\n    seed_manifest_path = repo_root / DEFAULT_SEED_MANIFEST\n',
    )
    replace_once(
        path,
        '        "seed_rows": inspect_seed_rows(seed_path),\n',
        '        "seed_rows": inspect_seed_rows(seed_path, seed_manifest_path),\n',
    )
    markdown = '''    seed = report["seed_rows"]\n    seed_file = seed["file"]\n    manifest_file = seed.get("manifest", {})\n    normalisation = seed.get("normalisation", {})\n    lines.append("## January 2003 seed rows")\n    lines.append("")\n    lines.append(markdown_table(\n        ["Item", "Value"],\n        [\n            ["Rows path", seed_file.get("path")],\n            ["Rows file exists", seed_file.get("exists")],\n            ["Rows size", human_bytes(int(seed_file.get("size_bytes", 0))) if seed_file.get("size_bytes") is not None else ""],\n            ["Rows modified", seed_file.get("modified_at")],\n            ["Rows SHA-256", seed_file.get("sha256", "")],\n            ["Manifest path", manifest_file.get("path", "")],\n            ["Manifest exists", manifest_file.get("exists", False)],\n            ["Rows", seed.get("row_count")],\n            ["Raw exact canonical omissions", json.dumps(seed.get("source_shape_missing_canonical_field_counts", {}), sort_keys=True)],\n            ["Missing after normalisation", json.dumps(seed.get("normalised_missing_required_field_counts", {}), sort_keys=True)],\n            ["Boundary classification", normalisation.get("classification", "")],\n            ["Target MP resolution", normalisation.get("target_mp_resolution", "")],\n            ["Recorded vote resolution", normalisation.get("recorded_vote_resolution", "")],\n            ["Meaning quality", json.dumps(seed.get("meaning_quality_counts", {}), sort_keys=True)],\n        ],\n    ))\n    lines.append("")\n'''
    replace_between(path, '    seed = report["seed_rows"]\n', '    for heading, key in (\n', markdown)


def patch_readme_and_config() -> None:
    readme = ROOT / "server_imports/README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Controlled seed import\n"
    if text.count(marker) != 1:
        raise RuntimeError("Controlled seed import heading not found exactly once")
    replacement = '''## Controlled seed import\n\nThe importer can check or import one small local seed rows file. Source-shaped batch rows may be paired with their reviewed batch manifest.\n\nDry-run seed check:\n\n```bash\npython3 server_imports/build_server_evidence_cache.py \\\n  --config server_imports/example_config.example.json \\\n  --seed-id parlparse_2003_01 \\\n  --seed-rows /path/to/local/parlparse_2003_01_rows.json \\\n  --seed-manifest /path/to/local/parlparse_2003_01_manifest.json\n```\n\nApply seed import:\n\n```bash\npython3 server_imports/build_server_evidence_cache.py \\\n  --config server_imports/example_config.example.json \\\n  --seed-id parlparse_2003_01 \\\n  --seed-rows /path/to/local/parlparse_2003_01_rows.json \\\n  --seed-manifest /path/to/local/parlparse_2003_01_manifest.json \\\n  --apply\n```\n\n### January 2003 shape boundary\n\nThe generated ParlParse row artifact is a source-shaped batch:\n\n- `date` is normalised to SQLite `division_date`;\n- `recorded_side` is normalised to SQLite `recorded_vote` and `vote_side`;\n- `target_mp` and `target_member_id` may be supplied once by the reviewed batch manifest rather than repeated in every source row;\n- the original row is retained unchanged in `source_trace`;\n- ParlParse `meaning_quality` remains `needs_review`.\n\nThe rows file is generated locally and is not a committed evidence artifact. The repository commits the parser, batch plan, manifest fixture, importer machinery and tests.\n\nSeed import rules:\n\n- dry-run is still the default;\n- `--apply` is required before database rows are written;\n- the rows and manifest files must already exist locally;\n- the manifest batch identity must match the selected seed ID;\n- no web fetch or bulk import is performed;\n- skipped rows are counted and reported;\n- database files, logs, generated rows, raw evidence and server output must not be committed.\n'''
    readme.write_text(text[: text.index(marker)] + replacement, encoding="utf-8")

    config_path = ROOT / "server_imports/example_config.example.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["seed_import"]["manifest_path"] = ""
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


FINAL_DOC = '''# January 2003 seed-row shape reconciliation\n\n## Decision\n\nThe apparent discrepancy is a combination of three things:\n\n1. **Expected source/import distinction.** The ParlParse batch generator emits source-shaped rows using `date` and `recorded_side`. Target identity belongs to the batch plan and manifest. SQLite deliberately stores a canonical row-level shape using `division_date`, `recorded_vote`, `vote_side` and `target_mp`.\n2. **Alias and normalisation boundary.** Importing the source shape requires `date → division_date`, `recorded_side → recorded_vote/vote_side`, and manifest `target_mp`/`target_member_id` → canonical member-vote identity.\n3. **Real repository defect, now repaired.** The current importer accepted row-level aliases but did not accept `recorded_side` or manifest-level target identity. The successful private-server import therefore depended on an uncommitted importer-ready transformation that was not represented by repository code, tests or operator documentation. The read-only audit also reported canonical names as absent without showing whether the source shape was fully normalisable.\n\nThis is not a vote-value conflict and not an evidence-meaning defect.\n\n## Repository evidence\n\n- `parse_parlparse_vote_rows_sample_v17.py` emits `date` and `recorded_side` per division.\n- `parlparse_import_batch_plan_v19.json` and the January manifest hold `target_mp` and `target_member_id` once for the batch.\n- `server_imports/mp_evidence_cache_schema.sql` stores canonical `target_mp`, `recorded_vote` and `vote_side` columns in `member_votes`.\n- The January rows file is generated locally and excluded from committed evidence. The repository contains the generation machinery and manifest fixture, not 33 committed evidence rows.\n- Historical issue #47 explicitly required a local importer-ready transformation before the first server import.\n\n## Deterministic mapping\n\n| Source or context | Canonical SQLite field | Rule |\n| --- | --- | --- |\n| row `date` | `division_date` | accepted alias |\n| row `recorded_side` | `recorded_vote` | accepted alias; value unchanged |\n| row `recorded_side` | `vote_side` | accepted alias; value unchanged |\n| manifest `target_mp` | `target_mp` | batch context copied to each canonical member-vote row |\n| manifest `target_member_id` | member identity | batch context used for the canonical member key |\n| complete original row | `source_trace` | JSON-preserved without injecting canonical fields |\n| ParlParse `meaning_quality` | `meaning_quality` | remains `needs_review` |\n\nRow-level canonical fields still take precedence when present. A manifest is only contextual input; its `batch_id` must match the selected seed ID.\n\n## Audit output\n\nThe read-only inventory now reports both:\n\n- exact canonical names absent from the raw/source-shaped row file; and\n- fields still missing after approved aliases and manifest context are applied.\n\nA raw omission is therefore not reported as an import defect when the canonical record is deterministically resolvable.\n\n## Safety boundary\n\nThis reconciliation changes no vote, meaning, source, MP coverage or publication state. It performs no live import and does not alter the retained backup or disposable restore.\n'''

FINAL_TEST = '''#!/usr/bin/env python3\n"""Regression proof for January 2003 source-shape to SQLite normalisation."""\n\nfrom __future__ import annotations\n\nimport json\nimport sqlite3\nimport sys\nimport tempfile\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(ROOT / "server_imports"))\n\nimport audit_server_state as audit  # noqa: E402\nimport build_server_evidence_cache as importer  # noqa: E402\n\n\ndef main() -> int:\n    rows = [\n        {\n            "date": "2003-01-07",\n            "division_id": "uk.org.publicwhip/debate/2003-01-07a.42.0",\n            "division_number": "42",\n            "motion_title": "Fixture division one",\n            "recorded_side": "Aye",\n            "meaning_quality": "needs_review",\n            "source_system": "parlparse",\n            "source_url": "https://example.invalid/division/42",\n            "source_xml_url": "https://example.invalid/debates2003-01-07.xml",\n            "evidence_status": "mp_found_in_aye_list",\n        },\n        {\n            "date": "2003-01-14",\n            "division_id": "uk.org.publicwhip/debate/2003-01-14a.77.0",\n            "division_number": "77",\n            "motion_title": "Fixture division two",\n            "recorded_side": "No",\n            "meaning_quality": "needs_review",\n            "source_system": "parlparse",\n            "source_url": "https://example.invalid/division/77",\n            "source_xml_url": "https://example.invalid/debates2003-01-14.xml",\n            "evidence_status": "mp_found_in_no_list",\n        },\n        {\n            "date": "2003-01-31",\n            "division_id": "uk.org.publicwhip/debate/2003-01-31a.99.0",\n            "division_number": "99",\n            "motion_title": "Fixture division three",\n            "recorded_side": "Not recorded",\n            "meaning_quality": "needs_review",\n            "source_system": "parlparse",\n            "source_url": "https://example.invalid/division/99",\n            "source_xml_url": "https://example.invalid/debates2003-01-31.xml",\n            "evidence_status": "mp_not_found_in_sample_division",\n        },\n    ]\n    manifest = {\n        "batch_id": "parlparse_2003_01",\n        "target_mp": "Corbyn, Jeremy",\n        "target_member_id": "185",\n    }\n\n    with tempfile.TemporaryDirectory() as temporary:\n        root = Path(temporary)\n        rows_path = root / "parlparse_2003_01_rows.json"\n        manifest_path = root / "parlparse_2003_01_manifest.json"\n        database_path = root / "mp_evidence_cache.sqlite"\n        rows_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")\n        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")\n\n        context = importer.load_seed_manifest(manifest_path)\n        importer.validate_seed_context("parlparse_2003_01", context)\n        normalised, error = importer.normalise_seed_row(\n            rows[0], "parlparse_2003_01", rows_path, context\n        )\n        assert error is None\n        assert normalised is not None\n        assert normalised["division_date"] == rows[0]["date"]\n        assert normalised["recorded_vote"] == rows[0]["recorded_side"]\n        assert normalised["vote_side"] == rows[0]["recorded_side"]\n        assert normalised["target_mp"] == manifest["target_mp"]\n        assert normalised["source_member_id"] == manifest["target_member_id"]\n        assert normalised["meaning_quality"] == "needs_review"\n        assert json.loads(normalised["source_trace"]) == rows[0]\n        assert "target_mp" not in json.loads(normalised["source_trace"])\n        assert "recorded_vote" not in json.loads(normalised["source_trace"])\n\n        missing_context_row, missing_context_error = importer.normalise_seed_row(\n            rows[0], "parlparse_2003_01", rows_path, {}\n        )\n        assert missing_context_row is None\n        assert missing_context_error == "Skipped row missing required fields: target_mp"\n\n        schema = (ROOT / "server_imports/mp_evidence_cache_schema.sql").read_text(encoding="utf-8")\n        importer.initialise_database(database_path, schema)\n        written, skipped, warnings = importer.apply_seed_rows(\n            database_path,\n            "parlparse_2003_01",\n            rows_path,\n            rows,\n            "fixture-import-run",\n            seed_context=context,\n        )\n        assert written == 3\n        assert skipped == 0\n        assert warnings == []\n\n        with sqlite3.connect(database_path) as connection:\n            values = connection.execute(\n                "SELECT recorded_vote, vote_side, target_mp, meaning_quality, source_trace "\n                "FROM member_votes ORDER BY division_key"\n            ).fetchall()\n        assert len(values) == 3\n        assert {value[0] for value in values} == {"Aye", "No", "Not recorded"}\n        assert all(value[0] == value[1] for value in values)\n        assert all(value[2] == "Corbyn, Jeremy" for value in values)\n        assert all(value[3] == "needs_review" for value in values)\n        assert all("recorded_side" in json.loads(value[4]) for value in values)\n        assert all("recorded_vote" not in json.loads(value[4]) for value in values)\n        assert all("target_mp" not in json.loads(value[4]) for value in values)\n\n        audit_result = audit.inspect_seed_rows(rows_path, manifest_path)\n        assert audit_result["row_count"] == 3\n        assert audit_result["source_shape_missing_canonical_field_counts"] == {\n            "division_id": 0,\n            "division_date": 3,\n            "target_mp": 3,\n            "recorded_vote": 3,\n        }\n        assert audit_result["normalised_missing_required_field_counts"] == {\n            "division_id": 0,\n            "division_date": 0,\n            "target_mp": 0,\n            "recorded_vote": 0,\n        }\n        assert audit_result["normalisation"]["classification"] == (\n            "expected_source_import_distinction_with_explicit_normalisation_boundary"\n        )\n        assert audit_result["normalisation"]["target_mp_resolution"] == "manifest"\n        assert audit_result["normalisation"]["recorded_vote_resolution"] == "recorded_side_alias"\n        assert audit_result["normalisation"]["evidence_meaning_changed"] is False\n\n        unresolved = audit.inspect_seed_rows(rows_path)\n        assert unresolved["normalised_missing_required_field_counts"]["target_mp"] == 3\n        assert unresolved["normalisation"]["classification"] == "unresolved_missing_import_fields"\n\n        mismatch_path = root / "wrong_manifest.json"\n        mismatch_path.write_text(json.dumps({**manifest, "batch_id": "other_batch"}), encoding="utf-8")\n        mismatch = importer.load_seed_manifest(mismatch_path)\n        try:\n            importer.validate_seed_context("parlparse_2003_01", mismatch)\n        except ValueError as exc:\n            assert "identity mismatch" in str(exc)\n        else:\n            raise AssertionError("Mismatched manifest identity was accepted")\n\n    print("PASS: January 2003 source shape resolves deterministically to canonical SQLite fields")\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''

FINAL_WORKFLOW = '''name: January 2003 seed shape test\n\non:\n  pull_request:\n    paths:\n      - "server_imports/build_server_evidence_cache.py"\n      - "server_imports/audit_server_state.py"\n      - "server_imports/README.md"\n      - "server_imports/example_config.example.json"\n      - "docs/january-2003-seed-row-shape-reconciliation.md"\n      - "scripts/test_january_2003_seed_shape.py"\n      - ".github/workflows/january-2003-seed-shape-test.yml"\n  push:\n    branches: [main]\n    paths:\n      - "server_imports/build_server_evidence_cache.py"\n      - "server_imports/audit_server_state.py"\n      - "server_imports/README.md"\n      - "server_imports/example_config.example.json"\n      - "docs/january-2003-seed-row-shape-reconciliation.md"\n      - "scripts/test_january_2003_seed_shape.py"\n      - ".github/workflows/january-2003-seed-shape-test.yml"\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  reconcile-seed-shape:\n    runs-on: ubuntu-latest\n    timeout-minutes: 5\n    steps:\n      - name: Check out repository\n        uses: actions/checkout@v4\n      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Compile reconciliation code\n        run: python -m py_compile server_imports/build_server_evidence_cache.py server_imports/audit_server_state.py scripts/test_january_2003_seed_shape.py\n      - name: Prove source-to-canonical mapping\n        run: python scripts/test_january_2003_seed_shape.py\n'''


def write_final_files() -> None:
    (ROOT / "docs/january-2003-seed-row-shape-reconciliation.md").write_text(FINAL_DOC, encoding="utf-8")
    (ROOT / "scripts/test_january_2003_seed_shape.py").write_text(FINAL_TEST, encoding="utf-8")
    (ROOT / ".github/workflows/january-2003-seed-shape-test.yml").write_text(FINAL_WORKFLOW, encoding="utf-8")


def main() -> int:
    if "--bootstrap" not in sys.argv:
        raise SystemExit("This temporary file must be run with --bootstrap")
    patch_importer()
    patch_audit()
    patch_readme_and_config()
    write_final_files()

    run(sys.executable, "-m", "py_compile", "server_imports/build_server_evidence_cache.py", "server_imports/audit_server_state.py", "scripts/test_january_2003_seed_shape.py")
    run(sys.executable, "scripts/test_january_2003_seed_shape.py")
    run(sys.executable, "-m", "compileall", "-q", ".")
    run(sys.executable, "scripts/validate_all_evidence_packs.py")
    run(sys.executable, "scripts/test_evidence_pack_validator_failures.py")
    run(sys.executable, "scripts/test_complete_mp_report_generator.py")
    run(sys.executable, "scripts/test_collector_to_evidence_pack.py")

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run(
        "git",
        "add",
        "server_imports/build_server_evidence_cache.py",
        "server_imports/audit_server_state.py",
        "server_imports/README.md",
        "server_imports/example_config.example.json",
        "docs/january-2003-seed-row-shape-reconciliation.md",
        "scripts/test_january_2003_seed_shape.py",
        ".github/workflows/january-2003-seed-shape-test.yml",
    )
    run("git", "commit", "-m", "Reconcile January 2003 seed row shape")
    run("git", "push", "origin", "HEAD:agent/reconcile-january-2003-seed-shape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
