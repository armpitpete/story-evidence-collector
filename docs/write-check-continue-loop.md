# Write-Check-Continue Loop

Use this loop for long writing tasks where quality needs to be checked while the work is being made.

It is not a PR gate. A PR gate checks delivery safety. This loop checks whether the writing is good enough to continue.

## Core loop

```text
write one section
check the section
fix it if needed
continue only when it passes
stop when complete, unclear, or unsafe
```

## When to use it

Use this loop for:

- TWIS articles
- fiction scenes or chapters
- manuals and teaching guides
- project documents
- evidence-pack reports
- long explanation pages

It is most useful when the work can drift, repeat itself, lose evidence, or become too hard to repair at the end.

## Unit size

Work in one clear unit at a time.

Good default units:

- one heading section for an article
- one scene for fiction
- one teaching block for a manual
- one claim or evidence block for a report
- one decision section for a project document

## Quality check

After each section, check:

- is the main point clear?
- does the section do its job?
- is the language plain enough?
- is there repeated wording or repeated structure?
- is the tone still right?
- are factual claims supported or clearly marked?
- does the next section still follow logically?

## Continue rule

Continue when the section is good enough to carry the next section.

It does not need to be perfect. It needs to be clear, useful, and pointed in the right direction.

## Fix rule

Fix before continuing when the problem is local.

Fix if the section is:

- vague
- repetitive
- too clever
- too long
- weakly ordered
- missing a clear point
- using unsupported claims

## Stop rule

Stop when the problem is larger than the section.

Stop if:

- the argument is unclear
- the evidence is missing
- the tone has drifted
- the next section is uncertain
- the work needs a human decision
- continuing would make the piece harder to repair

## Difference from a coding-agent loop

A coding-agent loop checks files, diffs, tests, and repository safety.

A writing loop checks meaning, structure, evidence, tone, and reader clarity.

Both loops should continue only while the work stays inside the plan.
