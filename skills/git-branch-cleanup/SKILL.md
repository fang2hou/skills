---
name: git-branch-cleanup
description: Cleans up local Git worktrees and branches whose work is provably merged or absorbed, deleting each risk group only after its own confirmation. Use after merging PRs, after parallel agent worktree sessions, or to prune merged local branches.
license: MIT
compatibility: Requires the git CLI with worktree support, a remote named `origin` (or a supplied remote name), and a POSIX shell for the shown pipelines; a non-POSIX environment must supply equivalent extraction of worktree paths and their checked-out branch names. Check C additionally requires network access and a CLI that can query merged pull requests; every other check is offline git.
metadata:
  author: fang2hou
  version: "2.2"
  sources: "Validated in real multi-worktree sessions."
---

# Git Branch Cleanup

Remove local worktrees and branches whose changes are provably absorbed somewhere else, and only after the user approves each group.

Produce two independent groups based on risk:

- **Group 1 (landed)**: the work is on the remote default branch. Deleting loses nothing because the remote holds it.
- **Group 2 (absorbed locally)**: the work is in the branch currently checked out in this worktree (the integration branch) but not yet on the remote default. Deleting loses nothing _as long as that integration branch survives_.

A branch in Group 1 or Group 2 is a **candidate**. Every other branch is non-deletable here and is only reported.

## When to Use

- After merging pull requests, especially squash merges.
- After a fan-out agent session that left `worktree/*` or feature branches and worktree directories behind (e.g. herdr-managed worktrees), including ones already merged into the integration branch the agent is standing on.
- The user asks to clean up branches or worktrees, delete merged branches, or list what is safe to remove.

## When NOT to Use

- Deleting **remote** branches (out of scope; remotes are read-only here).
- Cleaning stashes, tags, or reflog entries.
- Any repository where the user has not confirmed the deletion list.
- Forcing removal of a dirty, locked, or unreadable worktree (always reported, never forced).

## Inputs

| Input              | Required                  | Format           | Example                       |
| ------------------ | ------------------------- | ---------------- | ----------------------------- |
| Remote name        | No (default `origin`)     | git remote name  | `upstream`                    |
| Integration branch | No (default current HEAD) | local branch     | `feature/integration`         |
| Dry run            | No (flag in user request) | request phrasing | user asks to only show a plan |

## Hard Rules

1. **Never delete before the user confirms the exact list.** Group 1 and Group 2 are confirmed separately; approving one never implies the other. No batch shortcuts, no "obviously safe" exceptions.
2. **A `[gone]` upstream alone never qualifies a branch for deletion.** A remote branch can be deleted while the work is unmerged. `[gone]` is only a hint to run the merge checks.
3. **Detect the default branch from `<remote>/HEAD`**, never hardcode `main`/`master`. If unset, run `git remote set-head <remote> --auto` first.
4. A branch belongs to **Group 1** only if it passes at least one of, against `DEFAULT`:
   - **Check A**: it is an ancestor of `DEFAULT` (ordinary merge)
   - **Check B**: `git cherry DEFAULT <branch>` prints only `-` lines (every commit is patch-equivalent, covering single-commit squash merges)
   - **Check C**: a merged PR whose head ref is this branch has `headRefOid` **equal to** the local tip AND `baseRefName` equal to the short name of `DEFAULT` (proving the merged PR is this exact branch state landed on this target)

   A branch belongs to **Group 2** only if it fails Group 1 and passes, against `INTEGRATION`, **Check A**, **Check B**, or **Check C with `baseRefName` equal to `INTEGRATION`** (same `headRefOid` equality). Group 1 always wins over Group 2.

   Everything else:
   - All applicable checks ran and failed → **unmerged** (report only)
   - Check C returned merged PRs for the branch, but none matches both the local tip and one of the two accepted bases (branch name reused, commits added after the PR merged, or the PR landed on a third branch such as a release line) → **manual review**
   - Check C could not run (CLI missing, no network) and the branch failed A and B against both targets → **unverified**, treated like manual review rather than "unmerged" because a multi-commit squash merge could not be tested

   Never delete manual-review, unverified, or unmerged branches in this skill, even on request, because their status is unproven. The user can delete them manually outside this skill if they choose.

5. **The current worktree and its branch are untouchable**, as is `INTEGRATION` and the local counterpart of `DEFAULT`. Build that untouchable set before classifying.
6. **A branch held by another worktree is cleanable, but the worktree goes first.** Remove the worktree only when `git status --porcelain` in it is empty and it is not locked; then delete the branch. Never pass `--force` to `git worktree remove`, and never delete a branch still checked out somewhere.
7. **The delete flag depends on HEAD, not on the proof target.** `git branch -d` only accepts branches merged into the current HEAD, so a Group 1 branch that landed on `DEFAULT` without being in `INTEGRATION` would be refused. Choose per branch: `-d` when `git merge-base --is-ancestor <branch> HEAD` exits 0, `-D` otherwise. `-D` is safe here only because the branch carries recorded proof from Hard Rule 4; never use it on a branch without that proof.
8. **Group 2 deletions are unrecoverable once `INTEGRATION` is discarded.** If `INTEGRATION` has no upstream or is ahead of its upstream, say so in the Group 2 prompt so the user decides with that in view.

## Workflow

### Step 1: Snapshot state in one pass

```bash
REMOTE=origin
git fetch "$REMOTE" --prune
git remote set-head "$REMOTE" --auto            # only if <remote>/HEAD is missing
DEFAULT=$(git symbolic-ref --short "refs/remotes/$REMOTE/HEAD")   # e.g. origin/main
INTEGRATION=$(git branch --show-current)        # or the user-supplied branch; empty when detached
CURRENT_WT=$(git rev-parse --show-toplevel)

# worktree path + branch pairs (detached worktrees emit no branch line)
git worktree list --porcelain |
  awk '/^worktree /{p=substr($0,10)} /^branch /{b=substr($0,8); sub(/^refs\/heads\//,"",b); print p"\t"b}'

# every local branch with tip, upstream, tracking state, subject
git for-each-ref --format='%(refname:short)%09%(objectname)%09%(upstream:short)%09%(upstream:track)%09%(contents:subject)' refs/heads
```

`--prune` deletes stale **remote-tracking** refs only; it never touches local branches. `substr` is mandatory in both places: `$2` truncates any worktree path containing a space, and porcelain emits fully-qualified refs (`refs/heads/main`) while branches are compared by short name. Compare short names against short names only.

If `$INTEGRATION` is empty (the current worktree is in detached HEAD and the user named no branch), there is no Group 2 target. Skip Step 5's Group 2 entirely, state that in the report, and never substitute `DEFAULT` or `HEAD` for it. Skip every `--merged "$INTEGRATION"` and `git cherry "$INTEGRATION"` invocation in that case; running them with an empty value compares against the wrong ref or fails.

Untouchable set: the branch of `$CURRENT_WT`, `$INTEGRATION` when non-empty, and the local branch matching `$DEFAULT`.

### Step 2: Batch the merge checks

Run the cheap set operations once each instead of per branch:

```bash
git branch --merged "$DEFAULT"     --format='%(refname:short)'   # Check A vs DEFAULT
git branch --merged "$INTEGRATION" --format='%(refname:short)'   # Check A vs INTEGRATION
gh pr list --state merged --limit 100 --json number,title,headRefName,headRefOid,baseRefName
```

The PR query is **one** call: index it by `headRefName`, then require both `headRefOid` equal to the local tip from Step 1 and `baseRefName` equal to the short name of `DEFAULT` (Group 1) or to `INTEGRATION` (Group 2). Any other base (a release line or another feature branch) is not proof for either group. Only when a branch is absent from that window, fall back to `gh pr list --state merged --search "head:<branch>" --json number,title,headRefOid,baseRefName` for that branch alone.

Then run `git cherry` only on the branches still unclassified:

```bash
git cherry "$DEFAULT" "$B"        # Check B vs DEFAULT
git cherry "$INTEGRATION" "$B"    # Check B vs INTEGRATION
```

Empty output means no commits ahead, which Check A already caught; treat only "non-empty and all lines start with `-`" as a pass.

### Step 3: Classify

Assign each non-untouchable branch exactly one bucket, in this precedence: **Group 1** → **Group 2** → **manual review** → **unverified** → **unmerged**, per Hard Rule 4.

Record per branch: which check proved it, the target it was proved against, tip subject, upstream state (`[gone]` / ahead-behind / none) as context only (Hard Rule 2), PR number and title when Check C applied, and the worktree path holding it plus that worktree's dirty/locked state.

A candidate whose worktree is dirty or locked is **blocked**: keep it in its group's table, mark it not deletable this run, and state the reason.

### Step 4: Question 1 — Group 1 (landed on the remote default)

Show the Group 1 table in the user's conversation language:

```
| Branch | Tip | Proof | Worktree | Upstream |
```

Ask a single yes/no question: delete **all** of Group 1? The work is on `$DEFAULT`, so all-or-nothing is the appropriate default; accept a subset if the user names one.

### Step 5: Question 2 — Group 2 (absorbed into the integration branch)

Show the Group 2 table with the same columns plus the proof target `$INTEGRATION`, and state whether `$INTEGRATION` is pushed (Hard Rule 8).

Ask the user to opt in **per branch or subset**; the default is to delete nothing in this group. This group is never covered by the Group 1 answer.

Also show the manual-review/unverified and unmerged tables for reference; these are not deletable here.

**Gate (proceed to Step 6 only when all are true):**

- The exact per-group sets were shown and explicitly confirmed.
- Manual-review, unverified, unmerged, and blocked rows are excluded.
- The user did not request a dry run.

This gate is mandatory and cannot be bypassed by a caller, automation, or prompt; this skill has no auto-approve or unattended-delete path. If the user asked for a dry run, stop here and report the tables only.

**Validation loop:** if evidence is disputed or stale, re-run the relevant check and refresh PR/SHA evidence before presenting a revised table. A SHA mismatch stays manual review and is never promoted without proof.

### Step 6: Remove worktrees, then delete branches

Remove worktrees first, since Git refuses to delete a branch held by a worktree:

```bash
git -C "$WT" status --porcelain      # must be empty
git worktree remove "$WT"            # never --force
```

Then delete the branches. Write the approved list to a sorted file first; enumerating it
from memory while executing risks silently skipping a branch. Keep the file inside this
repository's git directory so a concurrent cleanup in another repository cannot overwrite
it, and so the path survives separate shell calls. Use the harness's file-write tool if
shell redirection is blocked. Compute the flag per branch (Hard Rule 7):

```bash
GBC="$(git rev-parse --absolute-git-dir)/gbc"   # per-repo, per-worktree scratch prefix
printf '%s\n' <approved branches> | sort > "$GBC-approved.txt"   # sorted: comm requires it
while read -r B; do
  if git merge-base --is-ancestor "$B" HEAD; then FLAG=-d; else FLAG=-D; fi
  git branch "$FLAG" "$B" || echo "FAILED: $B" >&2
done < "$GBC-approved.txt"
```

The flag reported for each branch in the tables must be the flag actually executed; compute it before presenting the tables so the two never diverge.

Never include manual-review, unverified, unmerged, or blocked branches. If a deletion fails because the branch is still checked out somewhere, report it as still active instead of forcing it.

**Reconcile before reporting anything as deleted.** Never state an outcome you did not observe:

```bash
GBC="$(git rev-parse --absolute-git-dir)/gbc"
git for-each-ref --format='%(refname:short)' refs/heads | sort > "$GBC-after.txt"
comm -12 "$GBC-approved.txt" "$GBC-after.txt"   # must be empty
```

Every line `comm` prints is an approved branch that still exists. For each one, either issue the missing deletion or report it with the error that blocked it. Call a branch deleted only when this comparison is empty or every remaining line has a recorded failure reason.

### Step 7: Final state

```bash
git worktree prune                   # drops registrations of already-deleted dirs only; safe
git worktree list
git branch -vv
rm -f "$(git rev-parse --absolute-git-dir)"/gbc-approved.txt "$(git rev-parse --absolute-git-dir)"/gbc-after.txt
```

Report the post-cleanup worktree list and branch list together, so the user sees both dimensions of the result.

The run is complete when all of these hold: every approved candidate is either deleted or reported with its failure reason; no worktree was removed with `--force`; every non-candidate bucket appears in the report; and the post-cleanup worktree and branch lists were produced from actual command output rather than predicted.

## Failure Handling

| Failure                                                             | Recovery                                                                                                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `git fetch` fails (offline, auth, unreachable remote)               | Continue with the stale remote-tracking refs, and mark every Group 1 result as based on unfetched state; do not delete Group 1 until a fetch succeeds. |
| `<remote>/HEAD` still unresolved after `git remote set-head --auto` | Stop and ask which branch is the default. Never fall back to `main`/`master`.                                                                          |
| PR query fails (CLI missing, no GitHub host, not authenticated)     | Check C is unavailable: report it once, and classify every branch that failed A and B as unverified, never as unmerged.                                |
| PR query succeeds but returns no PR for a branch                    | Not evidence of anything: the branch keeps whatever A/B produced.                                                                                      |
| `git worktree remove` refuses (dirty, untracked files, locked)      | Leave it; mark the branch blocked with the reason. Never add `--force`, and never delete a branch whose worktree survives.                             |
| Worktree directory is already gone from disk                        | `git worktree prune` clears the registration; then treat the branch as unheld and proceed normally.                                                    |
| `git branch -d` refuses ("not fully merged")                        | Expected when the proof target is not an ancestor of HEAD. Re-run that single branch with `-D` **only if** its Hard Rule 4 proof is recorded.          |
| A branch disappeared between classification and deletion            | Treat as already done; re-read `git branch -vv` before reporting so the final state reflects reality.                                                  |
| Some deletions succeed and others fail                              | Never re-run the whole batch. Report per branch, then retry only the failures whose cause you fixed.                                                   |

Batch commands hide partial failure: `git branch -d a b` can delete `b` while refusing `a` with exit code 1. Delete one branch per command so each result is attributable.

## Gotchas

- **Worktree-held branches are the common case after agent sessions.** Treating them as untouchable makes the skill a no-op exactly when it is needed; the correct order is prove merged → remove clean worktree → delete branch (Hard Rule 6).
- **`INTEGRATION` equal to the local default branch collapses Group 2 to empty.** That is expected; say so explicitly instead of presenting an empty table as a finding.
- **Multi-commit squash merges defeat patch-id.** When a PR with several commits is squash-merged, the single resulting commit matches no individual patch-id: `git cherry` reports every branch commit as `+` even though the content is on the default branch (verified on a real two-commit squash). Check C covers this case because PR merge status is authoritative there.
- **Offline runs must not mislabel squash leftovers.** Without the PR query, a multi-commit squash-merged branch is indistinguishable from an unmerged one, so classify it as unverified (kept and reported). Never present unverified branches as definitively unmerged.
- **Check C's SHA equality is load-bearing.** Without comparing `headRefOid` to the local tip, two hazards slip through: a branch name reused by a later PR, and commits made locally after the PR merged. SHA mismatch means manual review, never a candidate.
- **`git cherry` false `-`**: patch-id can rarely match by coincidence. The tables always show tip subjects so the user can veto anything suspicious.
- **Squash-merged branches look unmerged to git**: `git branch --merged` and `-d` both refuse because the original commits are not ancestors of the target. That is why Hard Rule 7 allows `-D`, and only for a branch whose Hard Rule 4 proof is recorded.
- **`gh pr merge --delete-branch` can delete the local branch currently checked out in a worktree**, leaving that worktree on an unexpected ref. After merging with `gh`, check `git branch -vv` and worktree integrity before running this skill.
- **The default branch is usually checked out in the primary worktree** and lands in the untouchable set anyway. If it is behind, offer a fast-forward (`git merge --ff-only`) only when that worktree is clean, and separately from deletion.
- **`<remote>/HEAD` may be unset in fresh clones.** Always resolve it in Step 1, and never hardcode the remote name in HEAD lookups.
- Branches with no upstream are treated like any other: run the checks; never delete them just for being orphaned.

## Output Contract

The human-readable report is primary. On completion, return:

1. The approved Group 1 and Group 2 tables (branch / tip / proof / worktree / upstream)
2. Results: worktrees removed, branches deleted, and each failure with its reason (dirty worktree, locked, still checked out)
3. Manual-review and unverified rows kept in place, with PR number/title and the SHA mismatch or "Check C unavailable" reason
4. Unmerged branches left in place with their ahead-commit count
5. Final `git worktree list` and `git branch -vv` output; for a dry run, state that nothing was removed and omit any post-cleanup state

Stable fields for downstream consumers, in this order:

```text
candidate: branch | group | proof target | check that proved merge | delete flag | worktree path | classification
dry_run: group1 table | group2 table | manual-review/unverified rows | unmerged rows
execute: approved group tables | worktree removal results | branch deletion results | kept rows | final worktree list | final branch list
```

For a dry run, return the tables only; do not run removal or deletion commands, and do not claim a post-cleanup state.
