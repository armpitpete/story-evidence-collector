---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
status: AUTHORISED
authority_ref: main
---

# Story Evidence Collector — Current Status

## Current authority

- Repository: `armpitpete/story-evidence-collector`
- Governing branch: `main`
- Session baseline: merge commit `a30a72b4bed14bc76b4f4ae2c0cdbc83527a49bf`.
- Active supporting authority: PR #144 at exact head `1f49813ddfc50b42a705b8942ed255e7cd8499c2`, limited to the read-only server inventory design and implementation.
- Waiting supporting authority: PR #145 at exact head `ced084e95c76eb6ba0049b44e88bfeceeb02e0c1`.

## Current lane

Rebuild the read-only server inventory from PR #144 onto the current `main`, preserving only `docs/read-only-server-inventory.md` and `server_imports/audit_server_state.py`. PR #145 is waiting and must not be modified or promoted in this lane.

## Done

- PR #146 merged as merge commit `a30a72b4bed14bc76b4f4ae2c0cdbc83527a49bf`, establishing `AGENTS.md`, this singular completion authority, and project-control CI.
- PR #144 contains a bounded, read-only server inventory covering archive state, SQLite integrity and counts, seed-row state, logs, backups, disk space and repository state.
- PR #145 contains a deterministic Complete MP Report v1 proposal with a passing fixture workflow, but it remains outside the active lane.
- PR #144 and PR #145 both diverged from the new project-control main and are not directly mergeable in their current form.

## To do

- Recreate the two-file PR #144 change on a new branch from the current `main` without altering its read-only safety boundary.
- Validate Python compilation and the project-control workflow on the rebuilt branch.
- Review the exact two-file diff and merge the rebuilt server-inventory PR.
- Close PR #144 as superseded by the rebuilt exact-scope PR.
- Run the merged inventory on the private server and record a reviewed, non-sensitive result before activating PR #145.

## Next bounded gate

Create and review a current-main replacement for PR #144 containing exactly `docs/read-only-server-inventory.md` and `server_imports/audit_server_state.py`; merge it only after its exact diff and validation pass.

## Stop point

Do not modify, refresh or merge PR #145, expand MP evidence coverage, add collector features, or begin another lane before the server inventory implementation is merged and its private-server execution result has been reviewed.
