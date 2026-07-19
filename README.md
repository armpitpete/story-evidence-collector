# Story Evidence Collector

Story Evidence Collector is a bounded public-source research toolkit for turning allowed web-source collection into traceable, reviewable evidence records.

It provides four connected layers:

```text
public source collection
        ↓
trace and subject reports
        ↓
draft Evidence Pack v1
        ↓
validated, human-reviewed outputs
```

The system preserves provenance and missing evidence. It does not decide that a claim is true, infer motive, bypass access controls, or authorise publication.

## Current repository status

`STATUS.md` is the sole repository-level completion authority. Read it before changing the project.

The repository currently includes:

- bounded public-page collection with robots checks and polite limits;
- source, queue, trace and subject-report outputs;
- a local Streamlit control panel;
- Evidence Pack v1 manifests, validators and six controlled fixture packs;
- a deterministic collector-to-Evidence-Pack bridge;
- Proof Trail v1 writer and validator tools;
- Complete MP Report v1 schema, generator and deliberately incomplete fixture;
- read-only private-server inventory tooling;
- project-control and subsystem CI workflows.

## Product boundary

### The toolkit can

- read reviewed seed URLs;
- check `robots.txt` before supported fetch operations;
- fetch a bounded number of public pages;
- preserve page title, visible-text excerpt, discovered links and collection status;
- prioritise and follow candidate links within configured limits;
- produce trace and subject-match reports;
- convert collector source metadata into a complete **draft** Evidence Pack folder;
- validate pack structure, IDs, paths and cross-references;
- write and validate Proof Trail records;
- generate deterministic Complete MP Report views from already structured records;
- report private archive and SQLite state without modifying it.

### The toolkit does not

- access paid, private, login-only, blocked or restricted material;
- evade `robots.txt` or site controls;
- decide whether evidence is true or sufficient;
- generate publication-safe factual claims from collected text;
- infer political motive, guilt, relationships or contradictions;
- mark a pack reviewed or publishable without human decisions;
- claim complete historical MP coverage;
- publish, commit or upload research automatically.

## Architecture

```text
seed URLs / reviewed source map
        │
        ├── selected-seed fetcher
        └── public trace pipeline
                    │
                    ▼
          collector JSON records
                    │
                    ▼
  create_draft_evidence_pack_from_collector.py
                    │
                    ▼
             Evidence Pack v1
                    │
                    ├── structural validator
                    ├── human review
                    └── optional report views
```

Private evidence storage is separate:

```text
GitHub repository: machinery, schemas, tests and controlled fixtures
Private server:     raw evidence, SQLite cache, reports, logs and backups
```

See `docs/repository-release-contract-v1.md` for the release completion boundary.

## Install

Python 3.12 is used by CI.

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` currently installs Scrapling and Streamlit for the collection and local-interface paths. Most validators, generators and regression tests are standard-library only.

## Primary entry points

### Local control panel

```bash
python -m streamlit run twis_source_engine_ui_v24.py
```

See [Simple Mode user guide v1](docs/simple-mode-user-guide-v1.md).

The interface runs local, bounded repository actions. It is not a deployed crawler and does not publish outputs.

### Public trace and subject pipeline

```bash
python run_public_trace_pipeline_v20.py
```

The runner coordinates the existing source extraction, queue filtering, candidate prioritisation, bounded candidate/follow processing, trace reporting and subject reporting steps.

### Selected-seed source fetcher

```bash
python extract_source_records_from_seed_file_v27.py \
  --input seed_urls_from_website_candidates_v26.json \
  --max-seeds 5 \
  --delay-seconds 1
```

This fetches reviewed seed URLs only. It does not automatically fetch the queued links it discovers.

### Collector to draft Evidence Pack

```bash
python scripts/create_draft_evidence_pack_from_collector.py \
  --source-records fixtures/collector-runs/2026-06-27-west-built-cheap-china-system/sources_raw_v13.json \
  --output-root generated/evidence-packs \
  --pack-id 2026-06-27-west-built-cheap-china-system-collector-draft \
  --title "Draft Evidence Pack — West Built the Cheap China System" \
  --research-question "What public evidence supports or limits the article's claims about low-value parcel duties, platform use and consumer price effects?" \
  --scope "Source metadata only; no claims or publication decision." \
  --created-at 2026-06-27T16:30:00Z \
  --editorial-risk high
```

The bridge always creates a `draft`, `not_ready`, human-review-required pack. It creates no factual claims, evidence conclusions or authority ratings.

See [Collector to Evidence Pack bridge v1](docs/collector-to-evidence-pack-v1.md).

### Validate Evidence Packs

Validate one pack:

```bash
python scripts/validate_evidence_pack.py fixtures/evidence-packs/2026-06-27-west-built-cheap-china-system
```

Validate every committed controlled pack:

```bash
python scripts/validate_all_evidence_packs.py
```

Evidence Pack documentation starts at [Evidence Pack v1 docs index](docs/evidence-pack-v1-docs-index.md).

### Proof Trail v1

```bash
python proof_trail_writer_v1.py \
  --input examples/proof_trail_input_v1.json \
  --output-dir generated/proof-trail

python proof_trail_validator_v1.py \
  --evidence-dir generated/proof-trail
```

See [Proof Trail schema v1](docs/proof-trail-schema-v1.md).

### Complete MP Report v1 fixture

```bash
python scripts/test_complete_mp_report_generator.py
```

The included Jeremy Corbyn fixture proves schema enforcement and deterministic output only. It is `fixture_unverified`, `not_ready`, not authorised for public output and incomplete across most research lanes.

See [Complete MP Report specification v1](docs/complete-mp-report-specification-v1.md).

### Read-only private-server inventory

From the private server checkout:

```bash
python3 server_imports/audit_server_state.py
```

The inventory reports archive folders, disk state, SQLite integrity and counts, source coverage, logs, backups and repository state. It performs no imports or writes.

See [Read-only server inventory](docs/read-only-server-inventory.md).

## Controlled Evidence Pack fixtures

Six controlled packs are committed:

1. `2026-06-22-example-topic`
2. `2026-06-24-story-evidence-collector-foundation`
3. `2026-06-25-code-of-practice-statistics-method`
4. `2026-06-25-power-profile-generic-leadership-mp`
5. `2026-06-26-the-politics-of-calling-people-ordinary`
6. `2026-06-27-west-built-cheap-china-system`

Fixtures prove repository structure and workflow behaviour. They do not automatically establish truth or publishability.

## Validation

Run the repository release gate locally:

```bash
python -m compileall -q .
python scripts/validate_all_evidence_packs.py
python scripts/test_evidence_pack_validator_failures.py
python scripts/test_complete_mp_report_generator.py
python scripts/test_collector_to_evidence_pack.py
```

GitHub Actions runs the same deterministic core checks without network access.

## Historical scripts

Versioned filenames remain in the repository as implementation lineage and bounded stage tools. They are not a requirement to understand the current product. Use the primary entry points above unless a document or repair contract names a specific historical stage.

## Safety and review rule

Collection is not publication.

A source record shows what was collected. An Evidence Pack shows how records are organised and reviewed. A generated report formats approved structured records. Human reviewers remain responsible for factual sufficiency, fair wording, legal and reputational risk, uncertainty and publication approval.
