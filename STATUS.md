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
- Exact starting head for this lane: `ea10b10930a2e68f7b5bdb87f672a43e83e18664`.
- January 2003 vote-review queue implementation remains complete at merge `7d646f0a68ef6153c58111440ed9bca05ce3ce44` from exact reviewed implementation head `c546d6417713870e37e8c54ad855b7e12d41d030`.
- January 2003 seed-row shape implementation remains complete at merge `4cc7cef44ad92af1ed0f0d15f0fb9e9c063bde2b`.
- Repository Release v1 remains complete and authoritative.
- Backup-and-restore hardening remains complete, with the accepted backup and disposable restore retained on the private server.

## Current lane

Complete MP Portfolio vertical slice.

Goal: add one read-only `MP Portfolio` view to the existing local Streamlit application, using the committed Complete MP Report v1 fixture, schema and deterministic generator, while preserving the existing Simple and Advanced source-check behaviour unchanged.

Authorised implementation scope:

- `twis_source_engine_ui_v24.py`
- `scripts/complete_mp_portfolio_view.py`
- `scripts/test_complete_mp_portfolio_view.py`
- `docs/complete-mp-portfolio-view-v1.md`
- `.github/workflows/complete-mp-portfolio-view-test.yml`

Existing read-only authorities that may be imported or consumed but must not be modified in this lane:

- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `schemas/complete-mp-report-v1.schema.json`
- `scripts/generate_complete_mp_report.py`
- `docs/complete-mp-report-specification-v1.md`

Required behaviour:

- add `MP Portfolio` as a third sidebar view without changing the existing Simple or Advanced view behaviour;
- validate the committed fixture through the canonical Complete MP Report validator before rendering;
- show the MP identity and publication state;
- show all 13 canonical report sections in canonical order with explicit coverage status;
- show section-linked facts, claims, interpretations, relationships and coverage gaps when present;
- resolve displayed source references to the fixture source register;
- make incomplete, unresearched and human-review-required sections visibly distinct in wording, without hiding them;
- show the canonical generated-output set and prove generation only in a disposable temporary directory outside the repository;
- keep the view read-only: no editing, approval, publication, network access, live-server access, SQLite access or repository output writes;
- fail closed on invalid structure, unresolved references or generator validation failure;
- add deterministic regression coverage for the display model, all 13 sections, source resolution, temporary output generation and preservation of the existing Simple and Advanced entry paths.

## Done

- Repository Release v1 is complete and authoritative.
- Backup-and-restore hardening is complete.
- The first real backup and disposable restore passed.
- January 2003 seed-row shape reconciliation is complete.
- January 2003 vote-review queue preparation is complete.
- The accepted restored database baseline remains 33 January 2003 ParlParse divisions, 33 member votes, one member, one source and one import.
- All 33 vote meanings remain `needs_review`.
- The repository contains bounded source collection, Evidence Pack v1, Proof Trail v1 and Complete MP Report v1 machinery.
- The canonical Complete MP Report fixture, schema and deterministic generator exist and remain deliberately incomplete, `not_ready` and unauthorised for public output.
- The existing Streamlit Simple and Advanced source-check interface is working locally.

## To do

- Implement the read-only Complete MP Portfolio display model.
- Integrate the new `MP Portfolio` view into the existing Streamlit sidebar.
- Render the committed fixture across all 13 canonical sections with visible evidence gaps and review state.
- Prove the canonical generator writes its five outputs only to a disposable temporary directory.
- Add the bounded user guide and deterministic regression workflow.
- Run the new portfolio-view test, Complete MP Report fixture test, Repository release validation and Project control.
- Open and review one implementation pull request changing only the five authorised files.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation change after Project control passes, then open one controlled Codex implementation pull request changing only the five authorised implementation files.

ChatGPT Work remains parked during this implementation lane. No real MP research starts until the read-only fixture-to-interface path is merged and proven.

## Stop point

Do not research or expand any real MP record; generate or review the real January 2003 packet; accept, reject, correct or rewrite any vote meaning; modify the Complete MP Report fixture, schema, canonical generator or specification; change existing Simple or Advanced behaviour; access the network, live server or SQLite; write generated portfolio outputs into the repository; create human review decisions; mark any report publishable; or authorise public output. Stop after the bounded implementation PR is complete, tested and reviewed.
