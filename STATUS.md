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
- Jeremy Corbyn regulated-donee donations baseline merged as `419ac75a5261f66149494805946d154a4ef41339` from exact reviewed implementation head `fd4f16a8c1767f00416f837336237944b82480ff` using a merge commit.
- Jeremy Corbyn outside-work-and-company-links baseline remains complete at merge `d9bac48a0561b2a807c24f72b32a757607dea9d6`.
- Jeremy Corbyn current financial-interests baseline remains complete at merge `e92262ccafa2e9628bc5e8f5bba6be4c14541750`.
- Jeremy Corbyn roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn identity-and-parliamentary-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

No implementation or research lane is active.

## Done

- The official Electoral Commission regulated-donee donations export for `Mr Jeremy Corbyn MP`, entity ID `1600`, was captured at `2026-07-20T18:28:55Z`.
- The search and export reconcile to 40 records across two pages, 29 columns and 40 unique `ECRef` identifiers. An earlier provisional reading of 43 was corrected and is not authoritative.
- The raw UTF-8-with-BOM CSV is reproducible byte-for-byte from the packet and validates against SHA-256 `d4edcdef02eacfc4d33212878627193d5905ef095bd35badf8c803a6c2251f99`.
- The capture contains 18 cash, 10 non-cash, 10 visit, one impermissible-donor and one unidentified-donor record.
- The mechanical all-row value is £429,626.42 only as a capture check. The 38 rows with accepted dates total £425,626.42; the two returned records total £4,000.00 and are not presented as retained funds.
- Every official row is preserved one-to-one as a `donation` fact. No party-wide donation, campaign-spending, loan, company-receipt or unrelated regulated-entity record was added.
- No donor relationship, personal-benefit, influence, motive, legality, propriety or political-significance inference was created.
- The `donations_and_political_finance` section is now `partial` with an explicit open wider-finance coverage gap.
- The report remains `not_ready`, human review remains required and public output remains unauthorised.
- Exactly five authorised implementation files changed in PR #191.
- Regulated-donee donations, identity-and-career, roles-and-committees, current financial-interests, outside-work/company-links, Complete MP Report fixture, Complete MP Portfolio view, Repository Release validation and Project Control all passed on exact head `fd4f16a8c1767f00416f837336237944b82480ff`.

## To do

Future work requires separately authorised bounded lanes. Remaining canonical areas include:

- speeches and parliamentary questions;
- public positions over time;
- changes and contradictions;
- organisations and evidenced relationships;
- broader historic voting coverage and human vote-meaning review;
- final evidence-gap, source-register, human-review and publication closure.

The accepted identity, roles, financial-interests, donations and outside-work/company sections remain deliberately `partial`; they do not claim exhaustive historical coverage.

## Next bounded gate

None. Open a separate `STATUS.md`-only authority PR naming one canonical section, exact official-source boundary, authorised files, validation and stop point before further research or implementation.

The recommended next lane is `speeches_and_parliamentary_questions`, beginning with one bounded official UK Parliament contribution dataset rather than an unbounded career-wide interpretation exercise.

## Stop point

Do not begin another MP or canonical section; alter accepted identity, roles, voting, financial-interests, donations, outside-work, positions, relationships or human-review records; infer influence, motive, legality or propriety; review January 2003 vote meanings; access or mutate the private server or SQLite; create unsupported claims or interpretations; mark a partial section complete; mark the report publishable; or authorise public output without a separately merged authority update.
