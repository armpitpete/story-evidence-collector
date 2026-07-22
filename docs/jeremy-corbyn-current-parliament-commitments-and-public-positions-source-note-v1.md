# Jeremy Corbyn current-Parliament commitments and public positions — source note v1

## Fixed result

The fixed candidate capture records:

- **8** source documents or pages: one accepted official Hansard packet and seven dated first-party pages;
- **109** reviewed candidate statement occurrences;
- **48** accepted neutral statement occurrences;
- **8** explicit personal commitments;
- **0** conditional personal commitments;
- **8** collective commitments;
- **32** public positions;
- **19** unresolved statement forms;
- **42** excluded candidates;
- **0** duplicate accepted record identifiers;
- accepted statement dates from **2024-07-18** through **2026-07-16**;
- capture timestamp **2026-07-21T13:29:25Z**;
- fixed candidate-capture checksum `fc5651b9f5647bcbfee822121f3188b0438fc826ad604351d044a8144e3df3db`.

## Source boundary

The inventory contains the already accepted official UK Parliament Hansard spoken-contributions packet plus seven dated first-party pages published by Jeremy Corbyn MP or the Peace & Justice Project. The packet preserves the captured attributable text, publication date, URL and a SHA-256 checksum for each first-party page excerpt used by this bounded baseline.

The existing Hansard packet remains the authority for its 306 contribution occurrences and is not duplicated or altered by this lane.

## Statement-form boundary

Accepted records use only these literal forms:

- `explicit_personal_commitment`;
- `conditional_personal_commitment`;
- `collective_commitment`;
- `public_position`.

Potential passages whose actor, quotation boundary, referenced statement or action object could not be resolved without interpretation remain `unresolved_statement_form`.

Procedural future statements, hopes, predictions, hypothetical language, quoted words from other speakers and other non-undertakings are preserved as excluded candidates rather than promoted into commitments.

## Fixture representation

The Complete MP Report v1 schema can represent this bounded evidence without change. Each accepted occurrence is encoded as a neutral `position` fact in `public_positions_over_time`. The occurrence class, exact quotation, surrounding context, actor, collective issuer, explicit condition and explicit deadline remain in the fact notes.

The fixture adds no claim, interpretation or relationship record. It does not compare statements with votes, questions, later speeches, amendments, organisational conduct or outcomes.

## Publication boundary

`public_positions_over_time` remains `partial`. `changes_and_contradictions` remains unchanged and human-review-required. The report remains `not_ready`, human review remains required and public output remains unauthorised.
