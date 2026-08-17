# Forge Adaptation

Load this reference before Step 1 when the repository is not hosted on GitHub,
when `gh` is unavailable, or when the repository's forge behavior differs from
the GitHub baseline.

## Required outcomes

A substitute forge client or API must provide verified equivalents for these
outcomes; command names and flags are intentionally not prescribed:

1. Discover the canonical default branch, merge policy, required checks, and
   automatic head-branch deletion behavior.
2. Create and list review requests, inspect their required checks, and report a
   merged state for `pr` mode.
3. Merge one accepted change using the repository's chosen method, without
   advancing while required checks are red.
4. Identify a CI run, inspect failed-step logs, rerun an infrastructure failure
   safely, and wait for a terminal result.
5. Report stable identifiers and statuses sufficient to rebuild the run table
   after interruption.

Use the forge's verified local documentation or client help to map each
outcome. If no verified interface can provide one of them, stop before landing
and ask the user rather than inventing a command.

## GitHub baseline

The main workflow's `gh repo view`, `gh pr create`, `gh pr list`, `gh pr merge`,
and `gh run ...` examples are GitHub-forge-specific. They are concrete
reference syntax only; they do not make GitHub semantics a requirement for the
core worktree, branch, rebase, validation, or cleanup rules.

When adapting, preserve the same gates, evidence, and recovery observables:
accepted review state before landing, green required checks after each merge,
recorded run/review identifiers, and proof that merged content is on the target
branch.
