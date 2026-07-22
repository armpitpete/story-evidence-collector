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
- Exact current main before this closure record: `97ff94d78fa50f9f8a0d7cf2c3bf68d0aff1eb9f`
- PR #226 merged at exact reviewed head `2c71dbd139a78a5fd93c57d192d8edcdf02d3fbb`.
- PR #226 merge commit: `97ff94d78fa50f9f8a0d7cf2c3bf68d0aff1eb9f`.
- All previously accepted Complete MP Report evidence, fixture and regression baselines remain authoritative.

### Governing project purpose

> Build a complete, traceable public evidence record for each MP, then use that evidence to reveal significant patterns, relationships, changes and inconsistencies that are difficult to see through ordinary human reading—without overstating what the evidence proves.

Every future lane must materially improve at least one of:

- completeness of the public-role evidence record;
- traceability from report statements to fixed evidence;
- reproducible detection of significant patterns, relationships, changes or inconsistencies;
- safeguards that prevent evidence, measurement and interpretation from being conflated;
- production of a readable and evidence-backed MP report that can be generalised consistently.

A lane must not be selected merely because another source exists. It must have a defined role in the final report and analysis architecture.

## Closed lane

The **current-Parliament tabled oral questions source-interface proof** lane is complete.

The merged scope was exactly:

- `research/complete-mp-reports/jeremy-corbyn/current-parliament-tabled-oral-questions-source-interface-v1.md`
- `scripts/test_jeremy_corbyn_current_parliament_tabled_oral_questions_source_interface_v1.py`
- `.github/workflows/jeremy-corbyn-current-parliament-tabled-oral-questions-source-interface-test.yml`

The completed lane established that:

- the official UK Parliament Oral Questions API exposes `GET /oralquestions/list`;
- `parameters.askingMemberIds=185` returns records attributed to Jeremy Corbyn as asking member and MNIS member `185`;
- the fixed capture on `2026-07-22` returned 12 member-filtered records;
- seven records had `TabledWhen` dates within the inclusive current-Parliament boundary from `2024-07-04` through `2026-07-22`;
- five records were earlier;
- the interface provides answering-date filters but no supported tabled-date or parliamentary-session filter;
- current-Parliament selection must therefore be performed locally using `TabledWhen`;
- API `Id`, not session-resetting `UIN`, is the record identity for paging and deduplication;
- an invalid-member control returned zero records;
- a complete reproducible fixed inventory is possible for the records exposed by the official API at a fixed capture time.

The fixed evidence block is bound to SHA-256:

- `25cd378069d42a50c1a4c36d514f188767c4f2721cf95f6c8c5d2c3a48a40a5b`

The unbounded member-query response is bound to SHA-256:

- `f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa`

The lane created no canonical oral-question inventory, no Complete MP fixture records, no classification, no interpretation and no public output.

### Closure proof

At exact PR head `2c71dbd139a78a5fd93c57d192d8edcdf02d3fbb`, the following passed:

- dedicated tabled oral questions source-interface regression;
- Python compilation;
- fixed evidence identity and SHA-256 verification;
- exact member, paging, date-boundary and result-count assertions;
- invalid-member control assertions;
- exact three-file PR #226 scope enforcement;
- `git diff --check`;
- Project Control;
- Repository Release validation.

PR #226 is closed and merged. The source-interface proof lane is closed.

## Current lane

One bounded **master MP report and analysis architecture contract** lane is selected and authorised only after this `STATUS.md`-only closure-and-authority record merges and its resulting exact `main` is verified.

The architecture lane exists to define the complete system that connects accepted evidence lanes to one pristine, readable, traceable and analytically useful MP report before further individual source expansion is selected.

### Exact authorised scope

The architecture lane may create or change exactly:

- `docs/complete-mp-report-and-analysis-architecture-contract-v1.md`
- `scripts/test_complete_mp_report_and_analysis_architecture_contract_v1.py`
- `.github/workflows/complete-mp-report-and-analysis-architecture-contract-test.yml`

No other file is authorised.

### Architecture contract requirements

The contract must define:

1. the governing project purpose exactly as recorded above;
2. the intended users and the difference between the readable report and the underlying evidence view;
3. the report-layer architecture:
   - evidence record;
   - report model;
   - pattern detection;
   - interpretation safeguards;
   - controlled public presentation;
4. the complete intended MP report section catalogue;
5. section completeness states and the evidence required to justify each state;
6. the traceability chain from official source through capture, inventory, canonical fact, report section, measured finding and public statement;
7. source-authority, capture-date, checksum, versioning, refresh and correction rules;
8. the allowed pattern families, including frequency, time change, co-occurrence, concentration, network, sequence, gap, cross-channel consistency and peer deviation;
9. the required distinction between:
   - fact;
   - measured pattern;
   - supported inference;
   - unresolved possibility;
   - unsupported claim;
10. confidence, comparison-baseline, materiality, alternative-explanation and non-proof requirements for analytical findings;
11. rules for peer comparison that prevent misleading comparisons between unlike MPs, roles, time periods or evidence coverage;
12. acceptance criteria for calling one report pristine;
13. the ordered path from the Jeremy Corbyn proof report to a reusable report for every MP;
14. failure and stop conditions when evidence is incomplete, conflicting, stale, inaccessible or incapable of supporting an interpretation;
15. the boundary between architecture definition and later implementation.

The contract must map accepted repository capabilities to the architecture without claiming that currently deferred evidence, analysis or public output already exists.

### Required proof

Before the architecture contract lane can close, require:

- the contract to contain every required architecture component and boundary;
- the deterministic regression to reject removal or weakening of the governing purpose, layer separation, report completeness rules, traceability chain, analytical labels, comparison safeguards, pristine-report acceptance standard or explicit exclusions;
- the workflow to compile and run the regression;
- exact three-file scope enforcement;
- `git diff --check`;
- Project Control and Repository Release validation to pass;
- a draft PR at an exact head for owner review.

### Explicit exclusions

The architecture contract lane does not authorise:

- capture of the fixed tabled oral-question inventory;
- canonical oral-question fixture integration;
- collection or integration of another evidence source;
- changes to the Complete MP fixture, schemas, generators, server or database;
- implementation of pattern-detection algorithms;
- production of any new pattern finding about Jeremy Corbyn or another MP;
- commitment-versus-conduct comparison;
- delivery, fulfilment or broken-promise assessment;
- contradiction, ideology, motive, influence, importance, effectiveness or outcome analysis;
- reclassification of existing facts, claims, interpretations or relationships;
- creation of the final Jeremy Corbyn report;
- public-output authorisation, publication or deployment;
- generalisation to other MPs.

## Done

- The current-Parliament Early Day Motions canonical fixture-integration lane is closed.
- The current-Parliament tabled oral questions source-interface proof lane is closed.
- PR #226 merged at exact authorised head.
- The governing project purpose is recorded as repository completion authority.
- The master MP report and analysis architecture contract lane is selected.
- Its exact future three-file scope, requirements, proof obligations and exclusions are recorded.

## To do

- merge this `STATUS.md`-only closure, purpose and lane-authority PR after Project Control and Repository Release validation pass;
- verify the resulting exact `main` merge commit;
- from that exact `main`, open one draft three-file master MP report and analysis architecture contract PR;
- change only the three authorised architecture-contract files;
- define the master report and analysis architecture without implementing evidence capture, pattern detection, interpretation or public output;
- run the dedicated regression, exact-scope check, `git diff --check`, Project Control and Repository Release validation;
- stop at an exact PR head for owner review.

## Next bounded gate

After this `STATUS.md`-only authority PR merges, verify the resulting exact `main`. From that exact `main`, open one draft three-file master MP report and analysis architecture contract PR using only the authorised scope above. Define the complete report model, evidence-to-finding traceability, pattern families, interpretation safeguards, pristine-report acceptance standard and Jeremy-Corbyn-to-all-MPs path. Run all required checks and stop at an exact PR head for owner review.

## Stop point

Do not begin the architecture contract lane before this closure-and-authority record merges and the resulting exact `main` is verified. Do not create or modify any architecture-contract file within this lane-authority PR. Do not capture the fixed oral-question inventory, integrate oral questions, select another evidence source, modify the Complete MP fixture, implement pattern detection, produce analytical findings, compare commitments with conduct, assess delivery or fulfilment, perform contradiction analysis, create the final Jeremy Corbyn report, generalise to other MPs, authorise public output, publish or deploy.
