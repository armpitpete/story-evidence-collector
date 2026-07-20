# Jeremy Corbyn — regulated-donee donations source note v1

## Capture boundary

- **Entity:** `Mr Jeremy Corbyn MP`
- **Electoral Commission entity ID:** `1600`
- **Regulated group:** `Regulated donee`
- **Search type:** `Donations`
- **Search text:** `Jeremy Corbyn`
- **Captured:** `2026-07-20T18:28:55Z`
- **Raw export:** `jeremy-corbyn-regulated-donee-donations-raw-2026-07-20.csv`
- **Raw SHA-256:** `d4edcdef02eacfc4d33212878627193d5905ef095bd35badf8c803a6c2251f99`
- **Raw size:** `11085` bytes
- **Columns:** `29`
- **Pages shown:** `2`
- **Displayed items:** `40`
- **Export rows:** `40`
- **Unique ECRef values:** `40`

## Count correction

An earlier provisional manual reading of **43** was incorrect. The search page says **40 items found**, and the untouched CSV contains exactly **40 unique ECRef rows**. This source note and the machine-readable packet supersede the provisional count.

## Identity reconciliation

Every export row has:

- `RegulatedEntityName`: `Mr Jeremy Corbyn MP`
- `RegulatedEntityType`: `Regulated Donee`
- `RegulatedEntityId`: `1600`
- `RegisterName`: `Great Britain`

No row was selected by donor name alone.

## Donation-type reconciliation

| Export donation type | Rows | Mechanical value total |
|---|---:|---:|
| Cash | 18 | £329,912.19 |
| Non Cash | 10 | £64,792.76 |
| Visit | 10 | £30,921.47 |
| Impermissible Donor | 1 | £1,000.00 |
| Unidentified Donor | 1 | £3,000.00 |
| **All export rows** | **40** | **£429,626.42** |

The total is only a capture check. It is not presented as money retained. The 38 rows with accepted dates mechanically total £425,626.42. The two returned rows mechanically total £4,000.00.

## Regulated-donee types

| Type | Rows |
|---|---:|
| Leadership Candidate | 13 |
| MP - Member of Parliament | 14 |
| Member of Registered Political Party | 13 |

## Special records

- `I0260286` is an `Impermissible Donor` record, has no accepted date and is marked `Returned`.
- `U0248096` is an `Unidentified Donor` record, has no accepted date and is marked `Returned`.
- `V0033114` is marked as an aggregation.
- Six donor-name fields contain source-leading whitespace. That whitespace is preserved in the packet rather than silently corrected.

## Raw preservation

The raw CSV is not added as a sixth repository file. The packet preserves the exact 29-column field map for every row. The regression reconstructs the original UTF-8-with-BOM, CRLF CSV byte-for-byte and requires SHA-256 `d4edcdef02eacfc4d33212878627193d5905ef095bd35badf8c803a6c2251f99`.

## Scope and interpretation limits

The packet does not include party-wide donations, company receipts, campaign spending, loans, public funds, crowdfunding transaction lists or records for other regulated entities.

No relationship, personal-benefit, influence, motive, legality, propriety or political-significance conclusion is created.

The `donations_and_political_finance` section becomes `partial`. Loans, party/entity finance, campaign spending, threshold effects, records outside the Commission database and unresolved identity variants remain explicit open gaps.

The report remains `not_ready`, requires human review and has no authorised public output.
