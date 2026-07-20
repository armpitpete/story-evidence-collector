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
- Complete MP Portfolio authority activation merged as `56c93095614518d66fa37ce3c0def1ffffb5f233`.
- Complete MP Portfolio implementation PR #170 merged as `da2fa879acd1783ab992c7dd68adb4be4e556123` from exact reviewed head `a183f5374bca4c617660e5a4010ddad0d7af45e0` using a merge commit.
- January 2003 vote-review queue implementation remains complete at merge `7d646f0a68ef6153c58111440ed9bca05ce3ce44` from exact reviewed implementation head `c546d6417713870e37e8c54ad855b7e12d41d030`.
- January 2003 seed-row shape implementation remains complete at merge `4cc7cef44ad92af1ed0f0d15f0fb9e9c063bde2b`.
- Repository Release v1 remains complete and authoritative.
- Backup-and-restore hardening remains complete, with the accepted backup and disposable restore retained on the private server.

## Current lane

Complete MP Portfolio local acceptance.

Goal: prove the merged read-only `MP Portfolio` view works in the actual local Streamlit application without regressing the existing Simple or Advanced source-check views.

No further repository implementation is authorised in this acceptance lane.

## Done

- Repository Release v1 is complete and authoritative.
- Backup-and-restore hardening is complete.
- The first real backup and disposable restore passed.
- January 2003 seed-row shape reconciliation is complete.
- January 2003 vote-review queue preparation is complete.
- The accepted restored database baseline remains 33 January 2003 ParlParse divisions, 33 member votes, one member, one source and one import.
- All 33 vote meanings remain `needs_review`.
- The repository contains bounded source collection, Evidence Pack v1, Proof Trail v1 and Complete MP Report v1 machinery.
- The existing Streamlit Simple and Advanced source-check interface remains present.
- The merged Streamlit application now exposes `Simple`, `MP Portfolio` and `Advanced` as three sidebar views.
- The `MP Portfolio` view consumes the committed Complete MP Report fixture read-only and validates it through the canonical validator before rendering.
- All 13 canonical report sections, explicit coverage states, source-linked facts and claims, coverage gaps, source register, publication state and human-review state are represented by the display model.
- The canonical generator proof writes only to an operating-system temporary directory outside the repository, records filename, byte size and SHA-256 metadata, and removes the directory before returning.
- The dedicated Complete MP Portfolio view test, Complete MP Report generator regression, Repository release validation and Project control all passed on exact implementation head `a183f5374bca4c617660e5a4010ddad0d7af45e0`.
- Implementation changed exactly the five authorised files.
- No real MP research, source expansion, SQLite access, private-server access, vote-meaning decision, publication decision or persistent generated portfolio output occurred.

## To do

Run one local human-facing acceptance check from exact merged `main` `da2fa879acd1783ab992c7dd68adb4be4e556123` and confirm:

- the application opens without a Python or Streamlit error;
- the sidebar shows `Simple`, `MP Portfolio` and `Advanced`;
- `Simple` still shows the existing source-check status and review controls;
- `Advanced` still opens its existing technical controls;
- `MP Portfolio` shows `Corbyn, Jeremy`, report status `not_ready`, human review `Required` and public output `Not authorised`;
- the coverage table contains all 13 canonical sections;
- the section expanders expose facts, claims and visible coverage gaps where present;
- the source register is visible;
- `Run disposable generator proof` reports five outputs and `Temporary directory removed: True`;
- no generated Complete MP Report files appear inside the repository.

After the human-facing acceptance passes, close this lane through a separate `STATUS.md`-only authority PR and activate the first real MP research lane separately.

## Next bounded gate

Human local-interface acceptance only. No code change is authorised unless the acceptance check reveals a reproducible defect.

ChatGPT Work remains parked until this acceptance gate passes. Codex is also parked unless a reproducible implementation defect is found.

## Stop point

Do not begin real MP research; edit the fixture, schema, canonical generator or specification; generate or review the real January 2003 packet; accept, reject, correct or rewrite any vote meaning; access the private server or SQLite; write persistent generated portfolio outputs; create human review decisions; mark any report publishable; or authorise public output. Stop for the local human-facing acceptance result.
