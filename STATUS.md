---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: AUTHORITATIVE
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- Jeremy Corbyn current financial-interests baseline merged as `e92262ccafa2e9628bc5e8f5bba6be4c14541750` from exact reviewed implementation head `4dce322af5220c62b7b20537094ab7d683b966d9` using a merge commit.
- The prerequisite roles-regression boundary repair is complete through PR #181.
- Jeremy Corbyn official roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn official identity-and-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

No implementation or research lane is active.

## Done

- The current UK Parliament Registered Interests snapshot for member ID `185` was captured at `2026-07-20T15:53:04Z`.
- The captured register version is dated 13 July 2026.
- All two displayed pagination pages were captured: 20 entries on page 1 and 9 on page 2.
- The captured total is 29 entries across three official categories: 13 gifts, benefits and hospitality entries; 12 visits outside the UK; and 4 miscellaneous entries.
- Official source spelling variants, repeated entries, absent fields and nested donor records are preserved without normalisation or inference.
- The `financial_interests` section is now `partial`, with 29 one-to-one `interest` facts and an explicit open historical-register and retention-boundary gap.
- No entry was reclassified as a donation, employment, company, relationship or position fact.
- No aggregate value, legality, propriety, influence, motive, benefit or political-significance conclusion was added.
- The report remains `not_ready`, human review remains required and public output remains unauthorised.
- Exactly five authorised implementation files changed in PR #182.
- The research packet and shared fixture remain readable, indented JSON after the final formatting repair.
- Jeremy Corbyn current financial-interests test, identity-and-career test, roles-and-committees test, Complete MP Report fixture test, Complete MP Portfolio view test, Repository release validation and Project control all passed on exact head `4dce322af5220c62b7b20537094ab7d683b966d9`.

## Remaining portfolio work

Future work requires separately authorised bounded lanes. Remaining areas include:

- donations and political finance;
- outside work and company links;
- speeches and parliamentary questions;
- public positions over time;
- changes and contradictions;
- organisations and evidenced relationships;
- historic voting coverage and human vote-meaning review;
- final evidence-gap, source-register, human-review and publication closure.

The accepted identity-and-career, roles-and-committees and financial-interests sections remain deliberately `partial`; they do not claim exhaustive historical coverage.

## Next bounded gate

None. Open a separate `STATUS.md`-only authority PR naming one canonical section, exact official-source boundary, authorised files, validation and stop point before beginning further research or implementation.

## Stop point

Do not begin another MP or canonical section; alter accepted identity, roles, voting, finance, interests, speeches, positions, relationships or human-review records; review January 2003 vote meanings; access or mutate the private server or SQLite; create unsupported claims or interpretations; mark a partial section complete; mark the report publishable; or authorise public output without a separately merged authority update.
