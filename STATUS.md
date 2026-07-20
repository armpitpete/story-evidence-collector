---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: AUTHORISED
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- Exact starting head for this lane: `f0b43bb082b877d7c0476e53ce7f1e68ed208d6a`.
- Complete MP Portfolio vertical-slice and local acceptance remain complete.
- Complete MP Portfolio implementation PR #170 remains merged as `da2fa879acd1783ab992c7dd68adb4be4e556123` from exact reviewed head `a183f5374bca4c617660e5a4010ddad0d7af45e0`.
- January 2003 vote-review queue implementation remains complete at merge `7d646f0a68ef6153c58111440ed9bca05ce3ce44`.
- Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn official identity and parliamentary-career baseline.

Goal: replace the fixture-only identity baseline for the Complete MP Report proof target with a narrowly sourced official parliamentary identity and service baseline, while leaving all other report sections, publication state and unresolved evidence gaps unchanged.

Canonical section:

- `identity_and_parliamentary_career`

Official source boundary:

- current UK Parliament member profile and biography/career records;
- official UK Parliament election or service records where needed to establish service dates and constituency continuity;
- another UK public-body primary record only when the Parliament record cannot supply a required field.

Forbidden source classes:

- Wikipedia;
- newspapers or broadcasters;
- party, campaign or personal websites;
- social media;
- unsourced aggregators;
- inference from search-result snippets.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/identity-and-parliamentary-career-v1.json`
- `docs/jeremy-corbyn-identity-career-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_identity_career_v1.py`
- `.github/workflows/jeremy-corbyn-identity-career-test.yml`

Required behaviour:

- record each official source with stable title, publisher, URL, capture date, authority level, coverage and limitations;
- record only narrowly worded facts directly supported by the named source;
- verify the subject display name, Parliament member ID, current constituency, current parliamentary affiliation and parliamentary service start date;
- preserve any unresolved historical party, boundary or service-period detail as an explicit coverage gap rather than inferring it;
- update the fixture subject identity status to `verified` only when every subject identity field resolves to official sources;
- keep the `identity_and_parliamentary_career` section `partial` unless the declared career scope has been fully assessed;
- keep the report `not_ready`, human review required and public output unauthorised;
- add no interpretation, contradiction, motive or wrongdoing claim;
- validate the complete fixture through the canonical Complete MP Report validator and generator;
- prove that all facts added to the fixture occur unchanged in the research packet and resolve to official source IDs;
- change exactly the five authorised files.

## Done

- Repository Release v1 is complete and authoritative.
- Backup and disposable restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The Streamlit application exposes accepted `Simple`, `MP Portfolio` and `Advanced` views.
- The current Complete MP Report proof target is `Corbyn, Jeremy`, but its committed identity baseline remains `fixture_unverified` and explicitly requires official refresh.

## To do

- Research the official identity and parliamentary-career baseline within the authorised source boundary.
- Create the machine-readable source-and-fact packet and readable source note.
- Update only the identity-and-career records and directly related source and gap references in the existing fixture.
- Add deterministic validation and CI.
- Run the new lane regression, canonical Complete MP Report test, Repository release validation and Project control.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project control passes. Then conduct the bounded official-source research and open one controlled five-file implementation PR.

ChatGPT Work owns source collection and fact extraction. Codex owns deterministic encoding, tests and fixture integration after the source packet is fixed. Neither may expand beyond this section or source boundary.

## Stop point

Do not research another MP or another canonical section; use non-official sources; infer missing service or party history; alter voting, finance, interests, speeches, positions, relationships or human-review records; review the January 2003 vote meanings; access or mutate the private server or SQLite; create interpretations; mark the identity-and-career section complete without full declared-scope evidence; mark the report publishable; or authorise public output. Stop after the five-file implementation PR is complete, tested and reviewed.
