# Project Entry Rules

This repository follows **Recursive Project Improvement Standard v1.0**.

## Mandatory entry sequence

Before making any change: read this file, read `STATUS.md` and every authority file it names, resolve the exact current repository head, state the current authority and bounded lane, then complete only that lane. Update `STATUS.md` before session closure or promotion.

Do not begin a new lane automatically.

## One-lane rule

Use one project, one authority, one bounded goal, one implementation contract, one validation set, one review point and one promotion or stop point.

When multiple open pull requests represent independent lanes, select one active lane explicitly and mark the others waiting or blocked.

## Stop conditions

Stop only for authority conflict, unclear scope, unexplained validation failure, a necessary forbidden change, irreversible action requiring approval, or genuine external-access requirements.

## New-chat bootstrap

```text
Continue work on `armpitpete/story-evidence-collector`.

Before acting:
1. read `AGENTS.md`;
2. read `STATUS.md` and every authority file it names;
3. verify the exact repository head;
4. report Done, To do and Next bounded gate;
5. continue only the complete authorised lane.

Use one project, one authority, one bounded goal, one implementation contract,
one validation set, one review point, and one promotion or stop point.

Do not rely on previous-chat memory when repository authority can be checked.
```

## Completion authority

`STATUS.md` is the sole repository-level completion authority. Issues, PRs, server inventories and report specifications are supporting evidence only.
