# Jeremy Corbyn current-Parliament Early Day Motions source inventory v1

## Boundary

Inventory ID: `jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1`

Fixed capture: `2026-07-22T07:46:43Z`.

This source-interface proof covers House of Commons Early Day Motions returned by the official UK Parliament **Tabled by Member** filter for Jeremy Corbyn, member ID `185`, from `2024-07-04` through `2026-07-22`. The exact completeness query includes withdrawn motions and excludes motions merely signed by him.

The result set contains **six** current-Parliament records on one result page. It spans the `2024-26` and `2026-27` sessions, with tabled dates from `2024-09-02` through `2026-06-23`.

No canonical fixture, schema, generator, server or database file is changed. This proof does not classify a motion as a commitment or public position and creates no conduct, delivery, contradiction, importance, influence or publication assessment.

## Exact official query

`https://edm.parliament.uk/?MemberId=185&TabledFrom=04%2F07%2F2024&TabledTo=22%2F07%2F2026&IncludeSponsoredByMember=false&IncludeWithdrawn=true&IsPrayer=false&ShowAdvanced=true&Term=&page=1`

The deterministic regression replays this exact read-only query, proves the reported total and page count, rejects missing or duplicate official motion IDs and URLs, then reads every linked detail page.

## Fixed inventory

| Stable record | EDM | Session | Tabled | Title | Primary party displayed | Signatures at capture | Detail extract SHA-256 |
|---|---:|---|---|---|---|---:|---|
| `edm-62446` | 123 | 2024-26 | 2024-09-02 | Mutual Defence Agreement | Independent | 27 | `a92572bd1aa340a45e7d17835d8198060f371c180bb484f4a34f933845577fcd` |
| `edm-63037` | 682 | 2024-26 | 2025-01-22 | Israeli violence in the West Bank | Independent | 20 | `ca93513e5b4bc1b9919755fa62eb6d0777747c9ab46b10b00fb50c07495c72cf` |
| `edm-64576` | 2154 | 2024-26 | 2025-10-27 | Media Plurality and Press Freedom in Parliament | Independent | 27 | `b0cdcdc649b4d363b42b0b1a03c576a82c5bdbf4739eaf122c8cf32a059551ca` |
| `edm-65102` | 2664 | 2024-26 | 2026-01-21 | Situation of Kurdish people in Syria | Independent | 33 | `137aaac38ea627b03424c0a1ca37f457a1fa2f9a3de8fb27f316a2885a229405` |
| `edm-65889` | 171 | 2026-27 | 2026-05-20 | Arsenal Football Club, Premier League champions | Independent | 8 | `64d8754ea5035953e32cb1b0a0c46658e24018f8ea94c4c666902f038cb955bb` |
| `edm-66149` | 431 | 2026-27 | 2026-06-23 | Western Sahara | Your Party | 15 | `89d0715d81f436840c3ba29b2d73a0e0aaf87148f9a25d77bfefd208e127ffbe` |

Official detail pages:

- `https://edm.parliament.uk/early-day-motion/62446/mutual-defence-agreement`
- `https://edm.parliament.uk/early-day-motion/63037/israeli-violence-in-the-west-bank`
- `https://edm.parliament.uk/early-day-motion/64576/media-plurality-and-press-freedom-in-parliament`
- `https://edm.parliament.uk/early-day-motion/65102`
- `https://edm.parliament.uk/early-day-motion/65889/arsenal-football-club-premier-league-champions`
- `https://edm.parliament.uk/early-day-motion/66149/western-sahara`

## Completeness proof

The fixed query reports six records on page 1 of 1. The inventory preserves every returned official motion ID and URL, and the regression requires the result-page set to reconcile exactly with the six detail records.

Each detail record preserves:

- the stable official motion ID and EDM number;
- the official session and tabled date;
- the full official motion text;
- Jeremy Corbyn as the explicitly displayed primary sponsor;
- party and constituency exactly as displayed at capture;
- total, supporting and withdrawn-signature counts as a dated snapshot;
- the displayed no-amendments statement;
- a checksum over the canonical extracted detail fields.

`edm-64576` displays 26 current supporters and one withdrawn signature, reconciling to 27 total signatures. A withdrawn signature is not treated as a withdrawn motion.

None of the six detail pages separately exposes a Boolean prayer label or whole-motion-withdrawal label. Those fields remain `null` and are listed as unresolved rather than inferred. All six pages identify the records as `EDM (Early Day Motion)` and state that no amendments have yet been submitted.

Signature totals are snapshots and may change after capture. The fixed JSON and its checksums preserve the captured values; a future refresh requires separate authority rather than silent mutation.

## Checksums

- Result-page extract SHA-256: `5a6c01c64f854d96b6a144417efff7e71bb92919641851406ff01e07e896e624`
- Full canonical capture SHA-256: `d53049aeb5ddb3a3e7bdca96a2d251e95091e5a68dfa8af98b60c8f5deab2ce6`

Checksums use UTF-8 canonical JSON with sorted keys and compact separators. The full capture checksum excludes only its own `capture_sha256` field. Each detail checksum excludes only that record's `detail_extract_sha256` field.

## Exclusions and stop point

This first phase excludes:

- motions tabled by another Member and merely signed by Jeremy Corbyn;
- records tabled before 4 July 2024;
- future EDM refreshes;
- canonical fixture integration;
- schema or generator changes;
- commitment or public-position promotion by implication;
- conduct comparison, delivery, fulfilment or contradiction analysis;
- public-output authorisation.

Stop for owner review after the exact four-file draft PR is green. Any fixture integration or scope expansion requires a separate gate.
