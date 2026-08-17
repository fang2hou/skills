# CI Failure Triage

Load this reference when a landing gate is red or a run must be classified
before Step 7 can continue. Nothing lands while the target branch's CI is red.

## Classify the failure

Use the configured forge's verified run-inspection interface to read the failed
step and its logs. Classify the first actionable failure, not downstream
cancellations:

- **Infrastructure** — runner setup, action download, or transient network
  failures (for example HTTP 429). Rerun only the failed jobs, then watch the
  new run to a terminal result.
- **Regression** — a failure inside the project's own check or deploy steps.
  Stop the landing sequence, fix the owning branch, push the fix, and rerun the
  repository gate before resuming.

On GitHub, the concrete baseline is `gh run view <id> --log-failed`, followed by
`gh run rerun <id> --failed` for an infrastructure failure and `gh run watch
<new-id> --exit-status`. These commands are GitHub-forge-specific examples,
not universal syntax.

## Regression loop

1. Capture the failed job, step, and relevant log lines in the review or landing
   log.
2. Re-prompt the owning agent with the exact failure and expected behavior, or
   take over after the documented escalation threshold.
3. Re-run the repository's gate command in the owning worktree.
4. Push the corrected branch and re-check the PR's required checks through the
   configured forge interface.
5. Resume only when the target branch and the next branch's required checks are
   green.

For a non-GitHub forge, substitute only a verified interface that exposes the
same outcomes: failed-step logs, a safe failed-job rerun, terminal success or
failure, and the checks required for merge. Do not invent command names or
assume that a green deploy means CI is green.

## Success signal

Record the run identifier, classification, rerun (if any), and terminal result.
The triage gate passes only when the required checks are completed
successfully and the target branch is mergeable; a missing or ambiguous run is
not green.
