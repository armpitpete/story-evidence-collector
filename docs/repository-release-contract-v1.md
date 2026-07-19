# Story Evidence Collector — Repository Release Contract v1

## Purpose

This contract defines when the Story Evidence Collector repository is complete as a bounded, testable public-source evidence toolkit.

It separates three different states that must not be conflated:

1. **Repository release complete** — the machinery, contracts, tests and operator documentation are coherent and passing.
2. **Evidence work complete** — a declared research scope has been collected and reviewed.
3. **Publication authorised** — a human has approved factual sufficiency, wording, uncertainty and risk.

This repository release can be complete while particular research packs and the private archive remain incomplete.

## Product statement

Story Evidence Collector v1 is a toolkit that can:

- collect bounded metadata and visible text from allowed public pages;
- preserve source, queue, trace and subject-report records;
- create a complete draft Evidence Pack skeleton from collector source metadata;
- validate Evidence Pack structure, IDs, paths and cross-references;
- write and validate Proof Trail records;
- generate deterministic Complete MP Report views from structured inputs;
- inspect private archive and SQLite state without modifying them;
- keep human review and publication decisions explicit.

It is not an automated journalist, truth engine, unrestricted crawler or completed political database.

## Required release components

Repository Release v1 requires all of the following.

### 1. Singular project authority

- root `AGENTS.md` defines entry, lane and stop rules;
- root `STATUS.md` is the sole repository completion authority;
- project-control CI rejects missing, malformed or competing authority.

### 2. Bounded collection path

- reviewed seed input is supported;
- supported fetch paths check `robots.txt`;
- bounded page and delay limits are available;
- source records preserve URL, title, visible excerpt, links and collection status;
- trace and subject reports can be produced;
- the local Streamlit interface exposes only bounded local actions.

### 3. Collector-to-pack integration

- collector source metadata can be converted into a complete Evidence Pack directory;
- output is deterministic for identical input and declared timestamps;
- generated packs remain `draft`, `not_ready` and human-review required;
- the bridge does not generate claims, evidence conclusions, authority ratings or publication approval;
- malformed, missing and duplicate URLs are rejected;
- overwrite requires an explicit flag.

### 4. Evidence Pack v1

- manifest schema exists;
- single-pack and all-pack validators exist;
- six controlled packs validate;
- invalid fixture cases prove expected failures;
- path traversal, duplicate IDs and core cross-references are checked;
- structural validation does not claim truth or publishability.

### 5. Proof Trail v1

- controlled input can be written into source, claim, evidence-item and brief files;
- generated files can be validated offline;
- provenance and human approval remain explicit.

### 6. Complete MP Report v1 contract

- canonical schema and 13-section specification exist;
- deterministic generator and regression test exist;
- included fixture remains explicitly unverified, incomplete, `not_ready` and not authorised for public use;
- generator rejects unsafe publication states and unresolved references.

### 7. Private archive inspection

- read-only inventory tooling exists;
- inventory reports archive folders, disk state, SQLite integrity and counts, source coverage, logs, backups and repository state;
- the tool performs no network, import, database, permission or repository writes.

### 8. Release validation

One offline GitHub Actions workflow must pass:

- Python compilation;
- all committed Evidence Pack validation;
- Evidence Pack validator failure regressions;
- Proof Trail writer and validator smoke test;
- Complete MP Report fixture regression;
- collector-to-Evidence-Pack integration regression;
- read-only server inventory missing-path smoke test.

Project-control CI must also pass on the exact release head.

### 9. Operator documentation

The README must identify:

- current product boundaries;
- primary entry points;
- validation commands;
- human-review requirements;
- private-server separation;
- controlled fixture status;
- historical scripts as lineage rather than the current product map.

## Release acceptance rule

The repository may be marked `AUTHORITATIVE` for Release v1 when:

1. every required release component above exists on `main`;
2. the release-validation workflow passes on the exact candidate head;
3. project-control CI passes on the exact candidate head;
4. README and status authority match the merged implementation;
5. no open PR is presented as a competing active completion lane.

## Explicit non-claims

Release v1 does not claim:

- complete coverage of any MP's career;
- complete UK parliamentary history;
- that collected sources are true or sufficient;
- that a structural Evidence Pack is publication-ready;
- that automated output replaces editorial, legal or reputational review;
- that the private archive contains every expected raw source;
- that backups or operational retention are complete;
- that public web sources will remain available.

## Reviewed operational exceptions

The private-server inventory reviewed on 19 July 2026 records:

- SQLite integrity check `ok`;
- one MP, 33 divisions and 33 member votes;
- ParlParse-only coverage from 7–31 January 2003;
- all 33 vote meanings marked `needs_review`;
- empty raw evidence areas;
- no validation logs;
- no backups;
- a server-only seed-row canonical-field report requiring reconciliation.

These exceptions block claims of evidence completeness and production durability. They do not invalidate the repository's bounded tooling release, provided they remain visible in `STATUS.md` and are not misrepresented as complete.

## Post-release lanes

After Release v1, changes must use separate bounded lanes. Likely categories are:

- private-server backup and restore hardening;
- seed-row shape reconciliation;
- source imports and coverage expansion;
- live-source identity refresh;
- human evidence review;
- publication workflow;
- dependency maintenance;
- specific collector defects exposed by real use.

No post-release lane may silently redefine Release v1 or convert an incomplete fixture into a completion claim.
