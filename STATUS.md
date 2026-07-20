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
- Exact starting head for this lane: `32f4f8e0b882054b4c7898b4a26fa9012a1a45df`.
- Jeremy Corbyn official identity-and-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199` from exact reviewed head `e22c9d6d262867e19f2b059677acc3ba9e6fcd4c`.
- Complete MP Portfolio vertical-slice and local acceptance remain complete.
- January 2003 vote-review queue implementation remains complete at merge `7d646f0a68ef6153c58111440ed9bca05ce3ce44`.
- Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn official roles and committees baseline.

Goal: replace the unresearched `roles_and_committees` section with a narrowly sourced official UK Parliament baseline of the current and previous posts, opposition post and committee memberships displayed on the member career record, without claiming exhaustive historic coverage.

Canonical section:

- `roles_and_committees`

Official source boundary:

- Jeremy Corbyn's UK Parliament member career record;
- the official UK Parliament committee summary pages linked from that career record, used only to identify committee names and committee type;
- another UK Parliament primary record only if a displayed role or membership cannot be encoded without it.

Forbidden source classes:

- Wikipedia;
- newspapers or broadcasters;
- party, campaign or personal websites;
- social media;
- unsourced aggregators;
- search-result snippets;
- inference about duties, performance, influence or motive.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/roles-and-committees-v1.json`
- `docs/jeremy-corbyn-roles-committees-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_roles_committees_v1.py`
- `.github/workflows/jeremy-corbyn-roles-committees-test.yml`

Required behaviour:

- record the official member career source and linked official committee sources with title, publisher, URL, capture date, authority, coverage and limitations;
- record only the current and previous posts, opposition post and committee memberships explicitly displayed by UK Parliament;
- preserve exact start and end dates when displayed;
- distinguish `role` facts from `committee` facts;
- record the current Parliamentary Leader, Your Party post separately from the previous Leader of the Labour Party and Leader of HM Official Opposition posts;
- record Social Security and Justice Committee memberships separately, including their official dates and Commons committee identity;
- leave the section `partial` and replace the generic unresearched gap with an explicit open historic-coverage gap;
- keep the report `not_ready`, human review required and public output unauthorised;
- add no claims, interpretations, relationship records, performance assessment or political inference;
- leave every other canonical section and existing fact unchanged;
- validate the complete fixture through the canonical Complete MP Report validator and generator;
- prove all role and committee facts added to the fixture occur unchanged in the research packet and resolve only to official source IDs;
- change exactly the five authorised files.

## Done

- Repository Release v1 is complete and authoritative.
- Backup and disposable restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The Streamlit application exposes accepted `Simple`, `MP Portfolio` and `Advanced` views.
- Jeremy Corbyn's official identity and parliamentary-career baseline is present and verified within its declared scope.
- The `roles_and_committees` section remains `not_researched` in the current fixture.

## To do

- Collect the bounded official roles-and-committees source packet.
- Create the machine-readable packet and readable source note.
- Update only the roles-and-committees section, its official sources, facts and directly related gaps in the fixture.
- Add deterministic validation and CI.
- Run the new lane regression, canonical Complete MP Report test, Complete MP Portfolio view test, Repository release validation and Project control.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project control passes. Then conduct the bounded official-source research and open one controlled five-file implementation PR.

ChatGPT Work owns source collection and fact extraction. Codex owns deterministic encoding, tests and fixture integration after the source packet is fixed. Neither may expand beyond this section or source boundary.

## Stop point

Do not research another MP or canonical section; alter identity, voting, finance, interests, speeches, positions, relationships or human-review records; treat a party-leadership post as a parliamentary party-affiliation fact; infer duties or influence; review January 2003 vote meanings; access or mutate the private server or SQLite; create claims or interpretations; mark the section complete; mark the report publishable; or authorise public output. Stop after the five-file implementation PR is complete, tested and reviewed.
