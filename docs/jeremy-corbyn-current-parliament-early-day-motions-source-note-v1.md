# Jeremy Corbyn current-Parliament Early Day Motions source inventory v1

## Boundary

Inventory ID: `jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1`

Fixed capture: `2026-07-22T07:46:43Z`.

This source-interface proof covers House of Commons Early Day Motions officially returned as **tabled by Jeremy Corbyn**, member ID `185`, from `2024-07-04` through `2026-07-22`. The exact query includes Published and Withdrawn motions and sets `includeSponsoredByMember=false`, so motions merely signed or secondarily sponsored by him do not enter the inventory.

The result set contains **six** current-Parliament records in one API page. It spans the `2024-26` and `2026-27` sessions, with tabled dates from `2024-09-02` through `2026-06-23`.

No canonical fixture, schema, generator, server or database file is changed. This proof does not classify a motion as a commitment or public position and creates no conduct, delivery, contradiction, importance, influence or publication assessment.

## Exact official interfaces

Human-facing member/date search fixed at capture:

`https://edm.parliament.uk/?MemberId=185&TabledFrom=04%2F07%2F2024&TabledTo=22%2F07%2F2026&IncludeSponsoredByMember=false&IncludeWithdrawn=true&IsPrayer=false&ShowAdvanced=true&Term=&page=1`

Supported UK Parliament Early Day Motions API query used by deterministic CI:

`https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotions/list?parameters.memberId=185&parameters.includeSponsoredByMember=false&parameters.tabledStartDate=2024-07-04&parameters.tabledEndDate=2026-07-22&parameters.statuses=Published&parameters.statuses=Withdrawn&parameters.skip=0&parameters.take=100`

Official detail template:

`https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/{official_motion_id}`

The API response reports `Skip=0`, `Take=100`, `Total=6` and `GlobalTotal=6`. Every returned item has `MemberId=185`, an explicit Jeremy Corbyn primary-sponsor object, full motion text and a stable official motion ID. The regression then reads every corresponding official detail endpoint and reconciles sponsor order, supporter and withdrawn-signature counts, amendment data and primary-sponsor date.

The human-facing EDM HTML interface applies a managed browser challenge to GitHub-hosted runners. CI therefore uses Parliament's supported JSON motions API rather than bypassing that challenge. The official API result set reconciles exactly with the six human-facing records fixed at capture.

## Fixed inventory

| Stable record | EDM | Session | Tabled | Title | Primary party displayed | Signatures at capture | Detail extract SHA-256 |
|---|---:|---|---|---|---|---:|---|
| `edm-62446` | 123 | 2024-26 | 2024-09-02 | Mutual Defence Agreement | Independent | 27 | `3b03a3436a0fabb4e5cd998e10a073a9efc666808d70e672a4f9113106924de8` |
| `edm-63037` | 682 | 2024-26 | 2025-01-22 | Israeli violence in the West Bank | Independent | 20 | `0b3807a74b22ac1bdd939d9289cf81b927ec35c99fed80b6b78d433926b47430` |
| `edm-64576` | 2154 | 2024-26 | 2025-10-27 | Media Plurality and Press Freedom in Parliament | Independent | 27 | `0173650ff6737dce5956f15ea5f48bcbaff4d56cdd3db41462a2853ec849d2da` |
| `edm-65102` | 2664 | 2024-26 | 2026-01-21 | Situation of Kurdish people in Syria | Independent | 33 | `1a80546fd83ae3a87cbac958f253dade6348fb1312d93c794ac0015ee41efd6c` |
| `edm-65889` | 171 | 2026-27 | 2026-05-20 | Arsenal Football Club, Premier League champions | Independent | 8 | `41284d14399891f6b2f538828452b0325b2a5e44f1aeed643e5db38076ff89d6` |
| `edm-66149` | 431 | 2026-27 | 2026-06-23 | Western Sahara | Your Party | 15 | `ae8b834bf3fd11075f860e4bf714f4b322886a60670bd139fd47bc796328deb9` |

Official publication and API detail records:

- `https://edm.parliament.uk/early-day-motion/62446/mutual-defence-agreement`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/62446`
- `https://edm.parliament.uk/early-day-motion/63037/israeli-violence-in-the-west-bank`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/63037`
- `https://edm.parliament.uk/early-day-motion/64576/media-plurality-and-press-freedom-in-parliament`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/64576`
- `https://edm.parliament.uk/early-day-motion/65102`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/65102`
- `https://edm.parliament.uk/early-day-motion/65889/arsenal-football-club-premier-league-champions`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/65889`
- `https://edm.parliament.uk/early-day-motion/66149/western-sahara`
- `https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/66149`

## Completeness proof

The fixed official API query reports six records with `Total=6` and `GlobalTotal=6` in a single page of capacity 100. The inventory preserves every returned official motion ID and reconciles every list result to one official detail response.

Each fixed record preserves:

- the stable official motion ID and EDM number;
- the official session and tabled date;
- the full official motion text;
- Jeremy Corbyn as the explicitly displayed primary sponsor;
- party and constituency exactly as displayed at capture;
- raw official status code and explicit amendment/prayer linkage fields;
- total, supporting and withdrawn-signature counts as a dated snapshot;
- the no-amendments result;
- a checksum over the canonical extracted detail fields.

`edm-64576` contains 26 current supporters and one withdrawn signature, reconciling to 27 total signatures. A withdrawn signature is not treated as a withdrawn motion.

The fixed human-facing detail pages did not separately label whole-motion withdrawal or expose a standalone prayer Boolean. Those page-level fields remain `null` and unresolved rather than inferred. The API separately preserves raw status code `0`, a null amendment target and a null praying-against-instrument link for all six records.

Signature totals are capture-time snapshots. The fixed JSON and checksums preserve those values; a future refresh requires separate authority rather than silent mutation.

## Checksums

- Result-page extract SHA-256: `e2fe2622d0e0b6d966572a956be779fb89a5a515b3f5d05769aae9ec09920820`
- Full canonical capture SHA-256: `4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a`

Checksums use UTF-8 canonical JSON with sorted keys and compact separators. The full capture checksum excludes only its own `capture_sha256` field. Each detail checksum excludes only that record's `detail_extract_sha256` field.

## Exclusions and stop point

This first phase excludes:

- motions tabled by another Member and merely signed or secondarily sponsored by Jeremy Corbyn;
- records tabled before 4 July 2024;
- future EDM refreshes;
- canonical fixture integration;
- schema or generator changes;
- commitment or public-position promotion by implication;
- conduct comparison, delivery, fulfilment or contradiction analysis;
- public-output authorisation.

Stop for owner review after the exact four-file draft PR is green. Any fixture integration or scope expansion requires a separate gate.
