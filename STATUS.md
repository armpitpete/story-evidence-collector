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
- Jeremy Corbyn current-Parliament spoken-contributions baseline merged as `098cc5f77ef30e4c259a164f70e79b8451d138c9` from exact reviewed implementation head `ab36c84dd089adbb3bae151bd4547423a297741b` using a merge commit.
- The prerequisite written-question fact-boundary repair remains complete at merge `5f817cec57d6d8f9f08f7bc2b5e54c94b6f6c04e`.
- The prerequisite written-question shared-gap repair remains complete at merge `82abd117fce3da51f564cfc0139d9fc2ebc64617`.
- Jeremy Corbyn current-Parliament written-questions baseline remains complete at merge `e1b21c1e4de1eefb827ac1f337017858510bc192`.
- Jeremy Corbyn regulated-donee donations, outside-work/company-links, current financial-interests, roles-and-committees and identity-and-parliamentary-career baselines remain complete within their declared official-source scopes.
- Complete MP Portfolio vertical slice, January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

No implementation or research lane is active.

## Done

- The fixed official-source capture was taken at `2026-07-21T09:59:35Z` for UK Parliament member ID `185`.
- The accepted spoken-contribution date coverage is `2024-07-17` through `2026-07-16`, inside the authorised current-Parliament boundary beginning `2024-07-04`.
- Eleven Members API requests returned 220 member-index rows before crossing the boundary; 203 rows fell inside the authorised date period.
- Exactly 202 in-scope Commons Chamber or Westminster Hall debate rows were accepted. One `Written Corrections` row was excluded because its venue was outside the authorised boundary.
- The 202 accepted debate rows resolved to exactly 306 unique individual spoken contribution segments.
- The accepted stable key is the official `ContentItemExtId`, matched exactly to the full-debate `Items[].ExternalId`, UK Parliament member ID `185` and the separate Hansard spoken-search `ContributionExtId`.
- Exact-identifier duplicate removal found no duplicate accepted contribution identifier.
- The accepted venue totals are 272 Commons Chamber segments and 34 Westminster Hall segments.
- The capture made 725 polite sequential official requests: 11 Members API requests and 714 Hansard API requests.
- Every accepted segment has an official identifier, speaker identity, date, venue, non-empty full text, debate reconciliation and official permalink resolver result.
- The official permalink resolver returned site-relative `/Commons/...` paths. The packet normalises only by prefixing the official `https://hansard.parliament.uk` host.
- The unresolved-record count is exactly 0 after that deterministic official-host normalisation.
- The debate payload exposed raw source value `2` without an explicit corrected, rolling or uncorrected label. All 306 accepted records preserve the raw value and use source status `unspecified` without inferred enum mapping.
- The member-index rows displayed 306 total contributions while approximate category counters summed to 271. Those counters remain navigation evidence only and do not classify individual segments.
- The frozen diagnostic is 1,650,782 bytes with SHA-256 `b2776c11a5a17d9605f56434ec5b13d77e75567a9bf01f851bf48e2f440e6a88`; its request-manifest checksum is `93b729e40a8bb6cadd87033f635d825436a2376f42754f46b1c57837dd04fef8`.
- One neutral `speech` fact was added per accepted individual contribution segment.
- All 90 accepted current-Parliament written-question facts and sources remain unchanged and in their accepted order before the speech facts in `speeches_and_questions`.
- No topic classification, summarisation of political meaning, policy-position inference, contradiction analysis, relationship, motive, influence, accuracy, legality, propriety or significance conclusion was created.
- Exactly five authorised implementation files changed in PR #197.
- Spoken contributions, written questions, identity-and-career, roles-and-committees, current financial interests, regulated-donee donations, outside-work/company-links, Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control all passed on exact head `ab36c84dd089adbb3bae151bd4547423a297741b`.
- The canonical `speeches_and_questions` section remains `partial` because pre-4-July-2024 spoken history, future contributions and later corrections, tabled oral questions, written statements, Early Day Motions and committee oral evidence remain outside the accepted baseline.
- The report remains `not_ready`, human review remains required and public output remains unauthorised.

## To do

Future work requires separately authorised bounded lanes. Remaining canonical areas include:

- spoken contributions before 4 July 2024 and separately controlled future/correction refreshes;
- written-question history before 4 July 2024 and future answer-state refreshes;
- tabled oral questions, written statements, Early Day Motions and committee oral evidence, each through its own official-source lane;
- public positions over time;
- changes and contradictions, only after dated position evidence exists;
- organisations and evidenced relationships;
- broader historic voting coverage and human vote-meaning review;
- final evidence-gap, source-register, human-review and publication closure.

The accepted identity, roles, financial-interests, donations, outside-work/company-links and speeches-and-questions sections remain deliberately `partial`; they do not claim exhaustive historical coverage.

## Next bounded gate

None. Open a separate `STATUS.md`-only authority PR naming one canonical section, exact official-source boundary, authorised files, validation and stop point before further research or implementation.

The commitment-versus-conduct system remains parked. It may not begin until a separately reviewed authority lane defines the required commitment evidence, conduct evidence, comparison method, uncertainty handling and publication boundary.

## Stop point

Do not begin another MP or canonical section; collect pre-4-July-2024 or future spoken contributions; refresh current records; begin commitment-versus-conduct, topic, position or contradiction analysis; include media, party, campaign, personal or commercial sources; include video/audio transcription, committee evidence, written statements, Early Day Motions, voting or oral-question datasets; alter accepted identity, roles, voting, financial-interests, donations, outside-work/company-links, written-question or spoken-contribution records; infer accuracy, influence, motive, legality, propriety or significance; review January 2003 vote meanings; access or mutate the private server or SQLite; create unsupported claims or interpretations; mark a partial section complete; mark the report publishable; or authorise public output without a separately merged authority update.
