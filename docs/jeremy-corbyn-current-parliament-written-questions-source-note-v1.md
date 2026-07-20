# Jeremy Corbyn — current-Parliament written questions source note v1

## Capture boundary

- **Subject:** Jeremy Corbyn
- **UK Parliament member ID:** `185`
- **House:** Commons
- **Record type:** written questions
- **Authorised date boundary:** `2024-07-04` through `2026-07-20`
- **Captured:** `2026-07-20T20:00:41Z`
- **Diagnostic capture:** `jeremy-corbyn-current-parliament-written-questions-capture-2026-07-20.json`
- **Diagnostic SHA-256:** `af77384595f9bc8898e3a4812984bd3b3d95d84e1cf175bef386ed2f62ccec4b`
- **Diagnostic size:** `2380198` bytes

Spoken contributions, debates, interventions, oral questions, written statements and Early Day Motions are outside this lane.

## Result reconciliation

The official Members API reported **251** all-career written-question records across **13** page requests. The capture contains:

- **251** unique internal question IDs;
- **251** unique date/UIN pairs;
- **90** records inside the authorised current-Parliament date boundary;
- first in-scope tabled date: **18 July 2024**;
- latest in-scope tabled date: **1 July 2026**.

The 90 in-scope records divide mechanically by tabled year as follows:

| Year | Questions |
|---|---:|
| 2024 | 14 |
| 2025 | 15 |
| 2026 | 61 |
| **Total** | **90** |

## Diagnostic STOP correction

The original capture ended with a diagnostic `STOP` because its validator looked for a nested `askingMember` object.

The official detail responses instead use this shape:

- direct field `value.askingMemberId = 185`;
- nested field `value.askingMember = null`.

All 90 preserved detail payloads have direct asking-member ID `185`. Each also matches its Members API index item by:

- internal question ID;
- UIN;
- tabled date;
- Commons house identity.

The failure was therefore a validator field-path error, not missing or conflicting evidence. No official record was re-requested, altered or inferred during reconciliation.

## Answer-status checks

At capture time:

- **89** questions had an answer date and answer text;
- **1** question had no answer date or answer text;
- unanswered record: internal question ID `1919112`, UIN `12037`;
- **0** questions were marked withdrawn;
- **86** were named-day questions;
- **27** recorded that the member had an interest;
- **1** answer was marked as a holding answer;
- **0** answers were marked as corrections;
- **0** attachments were recorded.

These are capture checks, not evaluations of the questions or answers.

## Proof preservation

The packet preserves:

- the diagnostic capture checksum and parser-failure provenance;
- the Members API OpenAPI contract and all 13 page-response hashes;
- compact reconciliation metadata for all 251 member-index records;
- the exact official index wrapper for every in-scope question;
- the exact official detail payload for every in-scope question;
- packet-internal canonical JSON checksums for each preserved index item and detail payload;
- one factual report record per in-scope question.

The diagnostic branch did not retain individual raw-response byte hashes for the 90 detail responses because it rejected each record before promotion. The complete diagnostic JSON is fixed by SHA-256 `af77384595f9bc8898e3a4812984bd3b3d95d84e1cf175bef386ed2f62ccec4b`, and every parsed detail payload is preserved in the packet.

## Interpretation limits

No question is classified as a policy position, contradiction, topic, motive, influence, legality or propriety finding.

The `speeches_and_questions` section becomes `partial`, not complete. Earlier written questions, later updates, spoken contributions, oral questions, written statements and Early Day Motions remain explicit open gaps.

The Complete MP Report remains `not_ready`, requires human review and has no authorised public output.
