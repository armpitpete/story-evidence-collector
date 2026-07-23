# Jeremy Corbyn current-Parliament tabled oral questions source inventory v1

## Purpose

Freeze the complete official member-query universe for oral questions tabled by Jeremy Corbyn at one declared capture time, then apply the current-Parliament boundary locally to `TabledWhen`. This is source evidence only; it creates no canonical Complete MP source, fact, classification, interpretation or public statement.

## Authority and fixed capture

- Exact starting `main`: `6e65e5ccd70bbed91f678e067105933ec049f17b`
- Captured at: `2026-07-23T17:27:27Z`
- Boundary: `2024-07-04` through `2026-07-23`, inclusive
- Member/MNIS ID: `185`
- Official operation: `GET /oralquestions/list`
- Exact request: `https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100`
- Paging: `Skip=0`, `Take=100`, `Total=12`, `GlobalTotal=12`
- Raw response SHA-256: `9d3b31f77d8e53c018039713fad830bc1e99b73bc5ca7c6a7bd0d67603cd35f9`
- Deterministic gzip SHA-256: `b7126e70594e3d4ce468e00f26dddb13ca5606de9dd1fed26ac138a5d6071a7f`
- Canonical packet payload SHA-256: `13c94b8044c54415e6f04c307f79f5a5a0935afe8240121caef3c805eb194fb5`

The packet stores a deterministic gzip-compressed, base64-encoded copy of the exact response. Decompression reconstructs the original 12,046 UTF-8 bytes, whose raw checksum is verified separately from every transformed checksum.

## Source-interface continuity

The merged source-interface proof remains authoritative: use `parameters.askingMemberIds=185`, collect every page to `PagingInfo.Total`, deduplicate by API `Id`, and apply the inclusive current-Parliament boundary locally to `TabledWhen`. Unsupported tabled-date parameters and answering-date filters are not completeness boundaries. `UIN` is preserved but is not globally unique.

## Complete member-query universe

| API ID | UIN | Tabled | Answering | Type | Status | Answering body | Boundary result | Official question text |
|---:|---:|---|---|---:|---:|---|---|---|
| `122465` | `902058` | 2020-04-23 | 2020-04-29 | `1` | `11` | Department for International Development | pre-Parliament exclusion | What steps she is taking to ensure that universal healthcare is available as a right in countries that are in receipt of support through her Department's aid programmes. |
| `127241` | `902893` | 2020-05-13 | 2020-05-20 | `1` | `5` | Prime Minister | pre-Parliament exclusion | If he will list his official engagements for Wednesday 20th May. |
| `271822` | `903396` | 2023-01-25 | 2023-01-31 | `2` | `5` | Foreign, Commonwealth and Development Office | pre-Parliament exclusion | If he will make a statement on his departmental responsibilities. |
| `271823` | `903371` | 2023-01-25 | 2023-01-31 | `1` | `5` | Foreign, Commonwealth and Development Office | pre-Parliament exclusion | Whether it remains the Government's policy that Israeli settlements in the Palestinian Territories are illegal. |
| `287272` | `905348` | 2023-06-07 | 2023-06-13 | `1` | `5` | Foreign, Commonwealth and Development Office | pre-Parliament exclusion | What recent steps he has taken to reach a diplomatic agreement with Mauritius on resettlement and sovereignty of the Chagos Islands. |
| `319088` | `900072` | 2024-07-18 | 2024-07-25 | `1` | `5` | Cabinet Office | included | Whether he plans to take steps to consolidate the number of national pay bargaining units in the civil service. |
| `319553` | `900153` | 2024-07-24 | 2024-07-30 | `1` | `5` | Foreign, Commonwealth and Development Office | included | What assessment he has made of the potential implications for his policies of the International Court of Justice's advisory opinion entitled Legal consequences arising from the policies and practices of Israel in the Occupied Palestinian Territory, including East Jerusalem, published on 19 July 2024. |
| `332039` | `901261` | 2024-11-12 | 2024-11-18 | `1` | `5` | Ministry of Defence | included | Whether he has had recent discussions with Cabinet colleagues on potential risks arising from the use of nuclear weapons. |
| `373735` | `904786` | 2025-06-18 | 2025-06-24 | `1` | `5` | Foreign, Commonwealth and Development Office | included | Whether he has made an assessment of the potential merits of supporting Pious Projects' Paediatric Hospital in Gaza. |
| `374007` | `904875` | 2025-06-19 | 2025-06-25 | `1` | `5` | Prime Minister | included | If he will list his official engagements for Wednesday 25 June. |
| `404663` | `907375` | 2026-01-14 | 2026-01-20 | `1` | `11` | Foreign, Commonwealth and Development Office | included | What assessment she has made of the potential implications for her policies of the steps Israel is taking to establish the E1 settlement in the occupied West Bank. |
| `411372` | `908076` | 2026-02-25 | 2026-03-03 | `1` | `11` | Foreign, Commonwealth and Development Office | included | What steps she is taking with Cabinet colleagues to conduct due diligence when licensing arms transfers to the United Arab Emirates to prevent weapons being used by the Rapid Support Forces in Sudan. |

The API serialized `QuestionType` and `Status` as numeric values. Their labels remain unresolved rather than inferred.

## Current-Parliament selection

Included API IDs: `319088`, `319553`, `332039`, `373735`, `374007`, `404663`, `411372`.

Excluded as tabled before the current Parliament: `122465`, `127241`, `271822`, `271823`, `287272`.

The bounded result is seven included records and five explicit pre-current-Parliament exclusions. Included tabled dates run from `2024-07-18` through `2026-02-25`.

## Source controls

**Authority:** the official UK Parliament API is authoritative only for fields it exposes.

**Capture:** the exact response is stored losslessly and bound to raw and compressed checksums.

**Version:** this is immutable v1 evidence; a later capture creates a new version and does not overwrite it.

**Refresh:** a new record/correction, changed total or stable field, interface/schema change, or separately authorised manual refresh triggers review.

**Correction:** retain v1, make a new capture, identify downstream effects and revalidate before fixture integration.

## Drift reconciliation

The raw checksum differs from the `2026-07-22` interface proof, whose raw bytes were not retained. The material interface assertions remain stable: the same twelve IDs, seven selected IDs, paging totals, dates, attribution, UINs, question-type values, status values and answering bodies. The drift is recorded; it is not silently ignored or used to overwrite the earlier proof.

## What this proves

At `2026-07-23T17:27:27Z`, the official member query exposed twelve records attributed to Jeremy Corbyn through member and MNIS ID `185`; all twelve were captured in one complete page; seven met the inclusive current-Parliament boundary; five were explicitly excluded as earlier; and the exact official response can be reconstructed and validated offline.

## What this does not prove

It does not prove completeness beyond the public API or turn a question into evidence of a commitment, public position, motive, ideology, importance, influence, effectiveness, delivery, fulfilment, contradiction or wrongdoing. A question asked is recorded only as a question asked.

## Explicit boundary

This lane does not authorise canonical Complete MP fixture integration; canonical source or fact creation; changes to existing fixtures, source-interface files, schemas, generators, servers or databases; classification; relationships; analysis; section completion; final-report production; public output; publication; deployment; or generalisation.

## Validation contract

Require deterministic offline decompression, raw and transformed checksum validation, exact record reconstruction, exact member attribution, ID uniqueness, paging and boundary reconciliation, the unchanged source-interface regression, bounded read-only live replay, exact four-file scope, `git diff --check`, Project Control, Repository Release validation and a draft exact-head stop.
