# First real Evidence Pack plan v1

This plan defines the first real or sandbox Evidence Pack task before creating multi-file pack content.

The aim is to prove the workflow with a bounded, low-risk topic.

Do not start with a live political accusation, a legal claim, a medical claim, or a claim about a private person.

## Proposed first pack

Use a sandbox research pack about the project itself.

Suggested pack ID:

```text
2026-06-24-story-evidence-collector-foundation
```

Suggested research question:

```text
What does the current Story Evidence Collector foundation prove, and what does it not prove yet?
```

## Why this is the right first pack

This is the safest first real pack because the sources are project-owned and already inside the repository.

It tests the pack workflow without needing live web collection, legal judgement, hostile fact-checking, or public accusation handling.

It still behaves like a real evidence pack because it must connect:

- source records
- claims
- evidence items
- search notes
- timeline entries
- review notes
- output briefs

## Source boundary

Use only repository files and repository history for the first pass.

Allowed first-pass sources:

- `README.md`
- `docs/evidence-pack-v1-docs-index.md`
- `docs/evidence-pack-validation-v1.md`
- `docs/evidence-pack-v1-validation-rules-summary.md`
- `docs/evidence-pack-starter-template-v1.md`
- `fixtures/evidence-packs/2026-06-22-example-topic/`
- `.github/workflows/evidence-pack-validation.yml`
- validator scripts under `scripts/`

Do not use external websites in the first pass.

Do not use political sources in the first pass.

Do not use patient, NHS, personal, private, or unpublished material in the first pass.

## Claims to test

The first pack should test small structural claims only.

Example claims:

1. The project has an Evidence Pack v1 manifest schema.
2. The project has a valid example Evidence Pack fixture.
3. The validator checks required manifest fields and required files.
4. The validator rejects unsafe parent-traversal paths.
5. The validator rejects JSONL records without IDs.
6. The validator rejects duplicate JSONL IDs inside the same JSONL file.
7. The current validator checks structure only, not truth or publishability.

## Stop point

The first pass is complete when:

- the pack folder exists.
- every required record file exists.
- every required output file exists.
- the pack validates locally.
- the final brief says what is proven and what is not proven.
- the pack does not overclaim.

Do not expand into a real TWIS article at this stage.

Do not add external sources until the internal workflow pack validates.

## Expected pack folder

Create the pack under:

```text
fixtures/evidence-packs/2026-06-24-story-evidence-collector-foundation/
```

Use the same required structure as the example fixture:

```text
pack.json
README.md
sources/source-records.jsonl
sources/source-authority-map.jsonl
claims/claim-records.jsonl
evidence/evidence-items.jsonl
search/search-diary.jsonl
search/negative-evidence-log.jsonl
timeline/public-record-timeline.jsonl
timeline/denial-checks.jsonl
review/human-review.jsonl
output/final-brief.md
output/evidence-summary.md
output/contradiction-brief.md
```

## Validation commands

Validate the new pack:

```powershell
python scripts\validate_evidence_pack.py fixtures\evidence-packs\2026-06-24-story-evidence-collector-foundation
```

Validate all fixture packs:

```powershell
python scripts\validate_all_evidence_packs.py
```

Run failure regression tests:

```powershell
python scripts\test_evidence_pack_validator_failures.py
```

## Safety wording

Use this wording in the output brief unless the pack proves something narrower:

```text
This pack proves that the current repository contains the documented Evidence Pack v1 foundation and validation structure. It does not prove that any external political, public-service, or news claim is true.
```

## Good enough rule

Good enough means the first real/sandbox pack validates and makes no claim beyond the repository evidence it contains.

The first pack is a workflow proof, not a publication pack.
