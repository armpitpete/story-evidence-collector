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
- Exact current main: `c186f62a68a944d8dde8c3b20e7a0e6e6d662847`
- PR #228 merged at exact reviewed head `9eb9e62e74ff21285b1ee50c464a4166da1f1bcf`.
- PR #228 merge commit: `c186f62a68a944d8dde8c3b20e7a0e6e6d662847`.
- The Complete MP report and analysis architecture contract v1 is authoritative.
- All previously accepted Complete MP Report evidence, fixture and regression baselines remain authoritative.

### Governing project purpose

> Build a complete, traceable public evidence record for each MP, then use that evidence to reveal significant patterns, relationships, changes and inconsistencies that are difficult to see through ordinary human reading—without overstating what the evidence proves.

Every future lane must materially improve evidence completeness, traceability, reproducibility or interpretation safety. The existence of another available source is not by itself a reason to add a lane.

## Closed lane

The **master MP report and analysis architecture contract** lane is complete.

The merged scope was exactly:

- `docs/complete-mp-report-and-analysis-architecture-contract-v1.md`
- `scripts/test_complete_mp_report_and_analysis_architecture_contract_v1.py`
- `.github/workflows/complete-mp-report-and-analysis-architecture-contract-test.yml`

The merged contract fixes:

- the thirteen-section Complete MP report catalogue;
- readable-report and evidence-view separation;
- the complete source-to-public-statement traceability chain;
- section completeness states;
- source authority, capture, checksum, version, refresh and correction controls;
- the nine allowed pattern families;
- the distinction between fact, measured pattern, supported inference, unresolved possibility and unsupported claim;
- confidence, materiality, baseline, alternative-explanation, non-proof and peer-comparison safeguards;
- the pristine-report acceptance standard;
- the ordered route from Jeremy Corbyn source completion to controlled every-MP expansion;
- failure and stop conditions;
- the boundary requiring separate authority for every implementation lane.

At exact PR head `9eb9e62e74ff21285b1ee50c464a4166da1f1bcf`, the dedicated deterministic regression, exact three-file scope enforcement, `git diff --check`, Project Control and Repository Release validation passed.

PR #228 is closed and merged. No evidence capture, fixture integration, analysis implementation, finding, public output, publication or deployment was performed.

## Current lane

The next architecture-ordered phase is **Jeremy Corbyn source completion**.

One bounded **current-Parliament tabled oral questions fixed source-inventory proof** lane is selected and authorised only after this `STATUS.md`-only authority record merges and the resulting exact `main` is verified.

This lane exists because the completed source-interface proof established that a complete reproducible fixed inventory is possible from the official UK Parliament Oral Questions API by:

- querying all records with `parameters.askingMemberIds=185`;
- paging to `PagingInfo.Total`;
- using API `Id` as the paging and deduplication identity;
- applying the inclusive current-Parliament boundary locally to `TabledWhen`;
- excluding records before `2024-07-04`;
- not using answering-date, unsupported tabled-date or session parameters as the completeness boundary.

The lane must create a fixed, checksum-bound source packet and source note. It must not integrate the records into the canonical Complete MP fixture.

## Exact future implementation scope

The later source-inventory PR may create or change exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-tabled-oral-questions-source-inventory-v1.json`
- `docs/jeremy-corbyn-current-parliament-tabled-oral-questions-source-note-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_tabled_oral_questions_source_inventory_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-tabled-oral-questions-source-inventory-test.yml`

No other file is authorised.

## Source-inventory contract

The later lane must:

1. use only the official UK Parliament Oral Questions API already established by the merged source-interface proof;
2. identify Jeremy Corbyn through member and MNIS ID `185`;
3. record one declared UTC capture timestamp and inclusive current-Parliament boundary from `2024-07-04` through the capture date;
4. preserve the exact request URL, supported parameters, paging metadata, response ordering and total counts;
5. page until every record in `PagingInfo.Total` has been retrieved;
6. preserve every member-query record needed to prove the local date selection, including records excluded as pre-current-Parliament;
7. use API `Id` as the stable inventory identity and preserve `UIN` only as source data;
8. require unique API IDs and record any repeated or session-resetting UIN neutrally;
9. preserve exact official fields needed for later neutral fixture integration, including question text, tabled date, answering date, answering body, question type, status, asking-member identity, UIN and official ID;
10. store raw-response, page, record and canonical-packet SHA-256 values without presenting a transformed checksum as the raw checksum;
11. document source authority, coverage, capture, version, refresh trigger, limitations and correction handling;
12. state precisely what the fixed inventory does and does not establish;
13. create no classification, interpretation, relationship, delivery, contradiction or public statement;
14. leave every existing fixture section, gap and publication state unchanged.

A read-only live replay may test the supported member query and current totals, but it must not silently refresh or rewrite the fixed packet. A changed live source must be reported as drift and reconciled separately.

## Required validation

Before the later lane can close, require:

- Python compilation of the dedicated regression;
- deterministic offline validation of the fixed packet and every recorded checksum;
- exact member attribution, API-ID uniqueness, paging, total-count, ordering and current-Parliament date-boundary assertions;
- exact inclusion and exclusion reconciliation against the fixed member-query universe;
- proof that unsupported parameters are not used as the completeness boundary;
- preservation of the merged source-interface conclusion and limitations;
- a controlled read-only live replay or a documented network-unavailable result that does not weaken offline proof;
- exact four-file scope enforcement;
- `git diff --check`;
- Project Control;
- Repository Release validation;
- the existing tabled oral questions source-interface regression;
- a draft PR at an exact head for owner review.

## Failure and stop conditions

Stop the later lane if:

- the exact base, head, four-file scope or governing architecture changes;
- official member attribution is ambiguous or no longer resolves to ID `185`;
- paging totals, page content, ordering or deduplication cannot be reconciled;
- a record needed for the bounded inventory lacks a stable API `Id` or usable `TabledWhen`;
- duplicate API IDs or inconsistent records cannot be resolved without inference;
- capture bytes, raw checksums, canonical checksums or record lineage cannot be reproduced;
- the official interface changes materially and the fixed source-interface proof no longer describes it;
- current-Parliament inclusion cannot be applied deterministically to `TabledWhen`;
- completing the lane would require a fixture, schema, generator, existing regression, server, database or public-output change;
- the evidence would support only an unresolved possibility or unsupported claim;
- any result would be framed as proof of motive, importance, influence, effectiveness, wrongdoing, delivery, fulfilment or contradiction.

A stop must be recorded visibly. Do not substitute search results, secondary parliamentary sites, manual lists, broader claims or relaxed tests to make the inventory appear complete.

## Explicit exclusions

This authority record and the later source-inventory lane do not authorise:

- canonical Complete MP fixture integration;
- creation of canonical source or fact records in the fixture;
- changes to the existing source-interface note or regression;
- schema, generator, server or database changes;
- oral-question content classification;
- commitment or public-position promotion;
- topic, ideology, motive, importance, influence, effectiveness or outcome analysis;
- commitment-versus-conduct, delivery, fulfilment, broken-promise or contradiction assessment;
- section completion or pristine-report status;
- final-report production;
- public output, publication or deployment;
- generalisation to another MP.

## Done

- The current-Parliament tabled oral questions source-interface proof lane is closed.
- The master MP report and analysis architecture contract is merged and authoritative.
- PR #228 merged at exact authorised head.
- The next ordered phase is Jeremy Corbyn source completion.
- One bounded tabled oral questions fixed source-inventory lane is selected.
- Its exact future four-file scope, validation, stop conditions and exclusions are recorded.

## To do

- merge this `STATUS.md`-only closure-and-authority PR after Project Control passes;
- treat Repository Release validation as path-inapplicable if its current workflow does not trigger for `STATUS.md`;
- verify the resulting exact `main`;
- from that exact `main`, open one draft four-file tabled oral questions source-inventory PR;
- change only the four authorised future implementation files;
- create the fixed official source packet and source note without fixture integration;
- run every required validation;
- stop at an exact draft PR head for owner review.

## Next bounded gate

After this `STATUS.md`-only authority PR merges, verify the resulting exact `main`. From that exact `main`, open one draft four-file current-Parliament tabled oral questions fixed source-inventory PR using only the authorised scope. Create the checksum-bound packet, source note, deterministic regression and workflow, run every required check, and stop at an exact PR head for owner review.

## Stop point

Do not begin the four-file source-inventory implementation before this authority record merges and the resulting exact `main` is verified. Do not capture or integrate oral-question evidence in this authority PR. Do not modify the Complete MP fixture, schema, generator, existing source-interface proof, server or database. Do not classify content, implement analysis, create findings, complete a report section, generalise to another MP, authorise public output, publish or deploy.
