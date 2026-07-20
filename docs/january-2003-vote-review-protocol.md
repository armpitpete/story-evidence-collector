# January 2003 Vote Review Protocol

## Purpose

This protocol governs the human-review packet for the existing January 2003
ParlParse member-vote records whose `meaning_quality` remains `needs_review`.

The queue is a review aid. It does not decide what a division meant, what an MP
intended, whether a recorded side supports a broader political claim, or
whether any output is safe to publish.

## Authority boundary

The implementation lane may:

- read the accepted SQLite cache in read-only mode;
- copy existing canonical and source-trace values into a private packet;
- classify only the technical source state:
  - `recorded_aye`;
  - `recorded_no`;
  - `not_recorded`;
  - `source_ambiguity`;
- leave every reviewer-decision field blank;
- refuse incomplete, contradictory or ambiguous records.

The implementation lane must not:

- accept, reject, correct or rewrite a vote meaning;
- infer political meaning from `Aye`, `No`, a title or metadata;
- write to the SQLite cache;
- import, refresh or expand evidence;
- commit the real 33-record packet to GitHub;
- change publication state.

## Packet fields

Each queue item contains:

- stable queue position;
- division key, division ID and date;
- motion or division title;
- canonical `recorded_vote` and `vote_side`;
- source URL and source XML URL;
- source evidence status;
- existing `meaning_quality`;
- the preserved source-trace object;
- blank reviewer fields.

The JSON packet is the machine-readable authority. The Markdown packet is a
human-readable rendering of the same values.

## Technical states

Technical states describe only what the stored source evidence says.

| State | Meaning |
|---|---|
| `recorded_aye` | Canonical side is `Aye` and the source trace records the MP in the Aye list. |
| `recorded_no` | Canonical side is `No` and the source trace records the MP in the No list. |
| `not_recorded` | Canonical value is `Not recorded` and the source trace records that the MP was not found in the sampled division. |
| `source_ambiguity` | Required evidence is missing, contradictory or outside the approved combinations. The generator refuses to emit the packet. |

A technical state is not a policy interpretation.

## Human evidence standard

A later, separately authorised reviewer must use the source XML and enough
division context to identify what was voted on. A title alone is not sufficient
when wording, amendments, procedural context or linked motions could change the
meaning.

The reviewer must:

1. open the source XML URL and source page;
2. verify the member identity and recorded side;
3. identify the exact motion, amendment or procedural question;
4. retain a direct evidence URL for the interpretation;
5. record uncertainty rather than resolve it by inference;
6. avoid converting a recorded side into motive, endorsement or broad policy
   position without further evidence.

## Permitted reviewer decisions

These values are permitted only during a later human-review lane:

- `confirmed_from_source` — the proposed meaning is directly supported by the
  authoritative source context;
- `corrected_from_source` — the source supports a different, explicitly
  evidenced meaning;
- `unresolved` — the available source does not support a safe conclusion;
- `excluded_from_publication_scope` — the record should not be used in the
  declared publication scope.

`reviewed_meaning`, `evidence_url`, `notes`, `reviewer` and `reviewed_at` must
remain blank unless that later lane explicitly authorises decisions.

## Private-server procedure

From the private server checkout:

```bash
sudo -iu storyevidence
cd /home/storyevidence/story-evidence-collector

python3 server_imports/build_january_2003_vote_review_queue.py \
  --config server_imports/example_config.example.json
```

The example configuration expects:

- the SQLite database beneath `/srv/story-evidence-collector/db/`;
- output beneath
  `/srv/story-evidence-collector/reports/review-queues/january-2003/`;
- exactly 33 matching January 2003 records.

The command refuses existing output unless `--overwrite` is supplied
deliberately. Generated JSON and Markdown packets remain private server
artifacts and must not be committed.

## Validation

Run:

```bash
python3 scripts/test_january_2003_vote_review_queue.py
python3 -m compileall -q .
```

The regression proof uses only a disposable SQLite database. It proves
deterministic ordering and bytes, required fields, unchanged source traces,
blank reviewer fields, read-only database access, path containment, and
refusal of incomplete or ambiguous records.

## Stop point

After the generator, schema, protocol, configuration and regression proof are
reviewed, stop. Do not perform the 33 human meaning decisions in this lane.
