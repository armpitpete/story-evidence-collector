# January 2003 seed-row shape reconciliation

## Decision

The apparent discrepancy is a combination of three things:

1. **Expected source/import distinction.** The ParlParse batch generator emits source-shaped rows using `date` and `recorded_side`. Target identity belongs to the batch plan and manifest. SQLite deliberately stores a canonical row-level shape using `division_date`, `recorded_vote`, `vote_side` and `target_mp`.
2. **Alias and normalisation boundary.** Importing the source shape requires `date → division_date`, `recorded_side → recorded_vote/vote_side`, and manifest `target_mp`/`target_member_id` → canonical member-vote identity.
3. **Real repository defect, now repaired.** The current importer accepted row-level aliases but did not accept `recorded_side` or manifest-level target identity. The successful private-server import therefore depended on an uncommitted importer-ready transformation that was not represented by repository code, tests or operator documentation. The read-only audit also reported canonical names as absent without showing whether the source shape was fully normalisable.

This is not a vote-value conflict and not an evidence-meaning defect.

## Repository evidence

- `parse_parlparse_vote_rows_sample_v17.py` emits `date` and `recorded_side` per division.
- `parlparse_import_batch_plan_v19.json` and the January manifest hold `target_mp` and `target_member_id` once for the batch.
- `server_imports/mp_evidence_cache_schema.sql` stores canonical `target_mp`, `recorded_vote` and `vote_side` columns in `member_votes`.
- The January rows file is generated locally and excluded from committed evidence. The repository contains the generation machinery and manifest fixture, not 33 committed evidence rows.
- Historical issue #47 explicitly required a local importer-ready transformation before the first server import.

## Deterministic mapping

| Source or context | Canonical SQLite field | Rule |
| --- | --- | --- |
| row `date` | `division_date` | accepted alias |
| row `recorded_side` | `recorded_vote` | accepted alias; value unchanged |
| row `recorded_side` | `vote_side` | accepted alias; value unchanged |
| manifest `target_mp` | `target_mp` | batch context copied to each canonical member-vote row |
| manifest `target_member_id` | member identity | batch context used for the canonical member key |
| complete original row | `source_trace` | JSON-preserved without injecting canonical fields |
| ParlParse `meaning_quality` | `meaning_quality` | remains `needs_review` |

Row-level canonical fields still take precedence when present. A manifest is only contextual input; its `batch_id` must match the selected seed ID.

## Audit output

The read-only inventory now reports both:

- exact canonical names absent from the raw/source-shaped row file; and
- fields still missing after approved aliases and manifest context are applied.

A raw omission is therefore not reported as an import defect when the canonical record is deterministically resolvable.

## Safety boundary

This reconciliation changes no vote, meaning, source, MP coverage or publication state. It performs no live import and does not alter the retained backup or disposable restore.
