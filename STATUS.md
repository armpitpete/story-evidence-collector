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
- Jeremy Corbyn current-Parliament written-questions baseline merged as `e1b21c1e4de1eefb827ac1f337017858510bc192` from exact reviewed implementation head `324590ec9c2db1ad3bbbc92ce33de06c2cb430a1` using a merge commit.
- Jeremy Corbyn regulated-donee donations baseline remains complete at merge `419ac75a5261f66149494805946d154a4ef41339`.
- Jeremy Corbyn outside-work-and-company-links baseline remains complete at merge `d9bac48a0561b2a807c24f72b32a757607dea9d6`.
- Jeremy Corbyn current financial-interests baseline remains complete at merge `e92262ccafa2e9628bc5e8f5bba6be4c14541750`.
- Jeremy Corbyn roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn identity-and-parliamentary-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

No implementation or research lane is active.

## Done

- The official UK Parliament Members API capture was fixed at `2026-07-20T20:00:41Z` for member ID `185`.
- The API reported 251 all-career written-question records across 13 page requests, with 251 unique internal question IDs and 251 unique tabled-date/UIN pairs.
- Exactly 90 Commons written questions fall inside the authorised `2024-07-04` through `2026-07-20` boundary.
- All 90 preserved detail payloads directly record `askingMemberId: 185` and match their index item by internal question ID, UIN, tabled date and House.
- The original diagnostic `STOP` was reconciled as a validator field-path error: the official detail payload uses direct `askingMemberId` and sets nested `askingMember` to null.
- The diagnostic capture is fixed by SHA-256 `af77384595f9bc8898e3a4812984bd3b3d95d84e1cf175bef386ed2f62ccec4b`.
- At capture time, 89 questions had answer dates and answer text; internal question ID `1919112`, UIN `12037`, remained unanswered.
- One neutral `question` fact was created per in-scope official record.
- No topic classification, policy-position inference, contradiction analysis, relationship, motive, influence, legality, propriety or significance conclusion was created.
- The canonical `speeches_and_questions` section is now `partial`, with spoken contributions and wider parliamentary record types still outside the accepted baseline.
- Exactly five authorised implementation files changed in PR #194.
- Current-Parliament written questions, identity-and-career, roles-and-committees, financial-interests, outside-work/company-links, regulated-donee donations, Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control all passed on exact head `324590ec9c2db1ad3bbbc92ce33de06c2cb430a1`.
- The report remains `not_ready`, human review remains required and public output remains unauthorised.

## To do

Future work requires separately authorised bounded lanes. Remaining canonical areas include:

- current-Parliament spoken contributions, with an official Hansard/member-record boundary;
- pre-4-July-2024 written-question history and future answer-state refreshes;
- public positions over time;
- changes and contradictions, only after dated position evidence exists;
- organisations and evidenced relationships;
- broader historic voting coverage and human vote-meaning review;
- final evidence-gap, source-register, human-review and publication closure.

The accepted identity, roles, financial-interests, donations, outside-work/company-links and speeches-and-questions sections remain deliberately `partial`; they do not claim exhaustive historical coverage.

## Next bounded gate

None. Open a separate `STATUS.md`-only authority PR naming one canonical section, exact official-source boundary, authorised files, validation and stop point before further research or implementation.

The recommended next lane is the current-Parliament spoken-contributions subset of `speeches_and_questions`, bounded by UK Parliament member ID `185`, a declared date range and official Hansard/member contribution records. It must remain an index of what was said, not policy-position or contradiction analysis.

## Stop point

Do not begin another MP or canonical section; collect spoken contributions; alter accepted identity, roles, voting, financial-interests, donations, outside-work/company-links, written questions, positions, relationships or human-review records; infer policy positions, contradictions, influence, motive, legality or propriety; review January 2003 vote meanings; access or mutate the private server or SQLite; create unsupported claims or interpretations; mark a partial section complete; mark the report publishable; or authorise public output without a separately merged authority update.
