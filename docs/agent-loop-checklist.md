# Agent Loop Checklist

Use this checklist before asking a coding agent to edit the repository.

Core rule:

> Plan the loop before running the agent.

## Goal

Write the exact change needed in one or two sentences.

The goal should be small enough that the expected diff is obvious before work starts.

## Allowed files

List the exact files or folders the agent may touch.

If the task only needs one file, name that one file.

## Forbidden changes

State what must not be changed.

Common forbidden changes:

- no unrelated cleanup
- no formatting sweep
- no dependency changes
- no schema changes unless requested
- no workflow changes unless requested
- no direct commits to `main`

## Check command

Define the command or inspection step that proves the work is safe.

Useful defaults:

```powershell
git status -sb
git diff --stat
git diff
```

Use project-specific checks when available.

## Review gate

Say what the diff should look like before the agent starts.

Example:

```text
Expected diff: one new markdown file, under 80 lines, no code changes.
```

## Stop rule

Stop immediately if the work moves outside the loop.

Stop if:

- the wrong files change
- the diff is larger than expected
- unrelated cleanup appears
- checks fail
- the agent cannot show the current diff
- the change feels unclear or hard to review

## Away-from-home rule

When away from the main PC, use branch and PR only.

Merge only when the PR is small, boring, and exact.
