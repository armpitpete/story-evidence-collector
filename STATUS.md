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
- Exact starting head for this lane: `2d375687dd6fb688a23742c58da96b7b530e523c`.
- Jeremy Corbyn outside-work-and-company-links baseline is complete at merge `d9bac48a0561b2a807c24f72b32a757607dea9d6` from exact reviewed head `3dc595700fb01f5f1d8a63b1adef2388bdc86f69`.
- Jeremy Corbyn current financial-interests baseline remains complete at merge `e92262ccafa2e9628bc5e8f5bba6be4c14541750`.
- Jeremy Corbyn roles-and-committees baseline remains complete at merge `968d33dac9e80cdf0f6c9107c195c5f7d7f70a1b`.
- Jeremy Corbyn identity-and-parliamentary-career baseline remains complete at merge `93c8da204d9709a1490dfa24a7b722a5f6a85199`.
- Complete MP Portfolio vertical slice and local acceptance remain complete.
- January 2003 vote-review queue, Repository Release v1 and backup-and-restore hardening remain complete and authoritative.

## Current lane

Jeremy Corbyn Electoral Commission regulated-donee donations baseline.

Goal: replace the unresearched `donations_and_political_finance` section with a bounded official-source baseline of donations reported to the Electoral Commission where the regulated donee record identifies Jeremy Corbyn as the receiving regulated individual, without conflating those records with donations to political parties, companies, campaign organisations or other people.

Canonical section:

- `donations_and_political_finance`

Official source boundary:

- the Electoral Commission political-finance search/export for `Regulated donee` and `Donations`, searched for Jeremy Corbyn across all available reporting periods at one declared capture time;
- official Electoral Commission guidance defining regulated donees and the reporting scope for donations to regulated individuals;
- official Electoral Commission row/detail records only, including the Commission's entity name, regulated-donee type, donor, value, donation type, accepted/received/reported dates, purpose and reporting-period fields when displayed;
- an explicit unresolved record when a result cannot be attributed to Jeremy Corbyn without guessing.

Forbidden source classes and expansion:

- political-party donations, minor-party donations, non-party-campaigner donations, referendum donations, candidate or party campaign spending, party accounts, loans, public funds and company receipts unless a separate later lane authorises them;
- Parliament register gifts, visits or company-role entries already captured in other sections;
- crowdfunding platform transaction lists, party, campaign or personal websites, newspapers, broadcasters, social media, Wikipedia, commercial databases and search-result snippets;
- joining records by donor name alone, treating donations to an organisation as donations to Jeremy Corbyn, or inferring personal benefit, influence, motive, legality, propriety or political significance;
- aggregating values across records as a substantive conclusion; any mechanical reconciliation total must be labelled only as a capture check;
- changing `financial_interests`, `outside_work_and_company_links`, `organisations_and_relationships` or any other canonical section.

Authorised implementation scope:

- `research/complete-mp-reports/jeremy-corbyn/regulated-donee-donations-v1.json`
- `docs/jeremy-corbyn-regulated-donee-donations-source-note-v1.md`
- `fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json`
- `scripts/test_jeremy_corbyn_regulated_donee_donations_v1.py`
- `.github/workflows/jeremy-corbyn-regulated-donee-donations-test.yml`

Required behaviour:

- capture the complete official result set returned by the declared regulated-donee donation query, including pagination or the official export, at one timestamp;
- preserve Electoral Commission spelling, dates, values, donor status, donation type, purpose, reporting period and absent fields without correction or inference;
- retain the Commission's unique row or record identifier when available and reject duplicate identifiers;
- create one `donation` fact per accepted official row attributed to Jeremy Corbyn;
- do not combine, split, deduplicate or normalise records unless the official source itself identifies a correction or replacement, which must be preserved explicitly;
- keep donations to Jeremy Corbyn separate from donations to parties, campaign companies or other regulated entities;
- create no relationship, position, claim or interpretation record;
- leave the section `partial` with explicit open gaps for loans, campaign spending, party/entity finance, reporting thresholds, records outside the Commission database and any unresolved identity variants;
- keep the report `not_ready`, human review required and public output unauthorised;
- preserve every accepted identity, roles, voting, financial-interests and outside-work/company record unchanged;
- validate the complete fixture through the canonical Complete MP Report validator and deterministic generator;
- run the new lane regression, identity-and-career regression, roles-and-committees regression, current financial-interests regression, outside-work/company-links regression, Complete MP Report fixture test, Complete MP Portfolio view test, Repository Release validation and Project Control;
- change exactly the five authorised files.

## Done

- Repository Release v1 and backup/restore proof are complete.
- January 2003 seed-row shape and vote-review queue preparation are complete.
- The accepted Streamlit interface exposes `Simple`, `MP Portfolio` and `Advanced` views.
- Jeremy Corbyn identity-and-career, roles-and-committees, current financial-interests and current outside-work/company-links baselines are complete within their declared official-source scopes.
- The Electoral Commission confirms that regulated donees include holders of certain elective offices and party members, that accepted donations must be reported, and that reports are published monthly.
- The Electoral Commission search service provides a distinct `Regulated donee` plus `Donations` search separate from party donations, loans and spending.
- The `donations_and_political_finance` section remains `not_researched` in current `main`.

## To do

- Resolve the exact official Electoral Commission query and export parameters for Jeremy Corbyn without relying on donor-name matching.
- Capture the complete returned regulated-donee donation result set and declared search metadata.
- Reconcile pagination/export count, unique record identifiers and a mechanical value total only as capture checks.
- Create the machine-readable source packet and readable source note.
- Update only the donations-and-political-finance section, its official sources, donation facts and directly related coverage gaps.
- Add deterministic validation and CI.
- Open and review one five-file implementation PR.
- After implementation merge, close this lane through a separate `STATUS.md`-only authority PR.

## Next bounded gate

Merge this authority-only activation PR after Project Control passes. Then ChatGPT Work must resolve and capture the official Electoral Commission regulated-donee donation result set. Codex may encode the fixed packet only after the query, count and identity boundary are explicit.

## Stop point

Do not research another MP or canonical section; include party-wide donations, campaign spending, loans, company receipts or unrelated regulated donees; alter accepted identity, roles, voting, financial-interests, outside-work, speeches, positions, relationships or human-review records; infer personal benefit, influence, motive, legality or propriety; review January 2003 vote meanings; access or mutate the private server or SQLite; create claims or interpretations; mark the section complete; mark the report publishable; or authorise public output. Stop after one five-file implementation PR is complete, tested and reviewed.
