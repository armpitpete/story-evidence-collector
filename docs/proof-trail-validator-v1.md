# Proof Trail Validator v1

proof_trail_validator_v1.py validates local Proof Trail evidence files.

It checks the files produced by proof_trail_writer_v1.py and reports structural errors and safety warnings.

## Run

py .\proof_trail_validator_v1.py --evidence-dir .\evidence

Strict mode:

py .\proof_trail_validator_v1.py --evidence-dir .\evidence --warnings-as-errors

## Checks

The validator checks:

- source records exist
- claim records exist
- evidence item records exist
- Markdown briefs exist
- required fields are present
- source references point to known source records
- claim references point to known claim records
- evidence grades are valid
- confidence values are valid
- Grade E evidence is not used alone without warning
- serious wording is flagged when not human checked
- claims without dates are flagged
- sources without archive or local copy paths are flagged
- evidence briefs include caution sections
- evidence briefs avoid obvious overclaiming phrases

## Boundaries

The validator does not fetch pages, crawl links, call AI, judge truth, decide motive, prove accusations, create a database, or publish anything.

## Good enough for v1

A v1 pass means the evidence folder has readable, linked, structurally valid Proof Trail files.

Warnings do not always mean failure. They identify places that need human checking before TWIS uses the evidence.
