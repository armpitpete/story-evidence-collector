# Proof Trail Writer v1

## Purpose

`proof_trail_writer_v1.py` turns one controlled input JSON file into the first Proof Trail file set.

It does not fetch pages, extract claims automatically, judge truth, create a database, or perform contradiction matching.

Its job is simple:

```text
one controlled input
→ one source JSON record
→ one claim JSON record
→ one evidence item JSON record
→ one Markdown evidence brief
```

## Run

From the repository root:

```powershell
python .\proof_trail_writer_v1.py
```

Default input:

```text
examples/proof_trail_input_v1.json
```

Default output directory:

```text
evidence/
```

Explicit run:

```powershell
python .\proof_trail_writer_v1.py --input .\examples\proof_trail_input_v1.json --output-dir .\evidence
```

## Output files

A first run should create:

```text
evidence/sources/source-0001.json
evidence/claims/claim-0001.json
evidence/evidence-items/evidence-item-0001.json
evidence/briefs/brief-0001.md
```

If those files already exist, the writer uses the next available number, for example `source-0002.json`.

## Safety limits

The writer is deliberately limited.

It does not:

- fetch live web pages
- bypass `robots.txt`
- crawl links
- call an AI model
- decide whether a claim is true
- decide whether there is a contradiction
- write to a database
- overwrite existing Proof Trail files

## Quality rule

The writer creates evidence files for human review. It must not make stronger claims than the input supports.

The generated brief keeps the required review sections:

- source chain
- evidence grade
- what is proven
- what is interpretation
- what needs checking
- what must not be overstated
- human review checklist
