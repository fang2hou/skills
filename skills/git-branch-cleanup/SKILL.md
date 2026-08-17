---
name: git-branch-cleanup
description: Safely identifies local Git branches provably merged into the remote default branch, including squash merges, and deletes approved candidates only after explicit confirmation while protecting active worktrees. Use for local branch cleanup.
license: MIT
compatibility: Requires git CLI with worktree support and a POSIX shell for the shown Step 1 pipeline; non-POSIX environments must provide an equivalent way to extract branch names checked out in any worktree. A remote named `origin` (or a supplied remote name) is required. Check C additionally requires a CLI capable of the documented merged-PR query and network access; Checks A and B are offline git operations. When Check C cannot run, see Hard Rule 3 for the unverified classification.
metadata:
  author: fang2hou
  version: "1.5"
  sources: "Validated in a real multi-worktree session (2026-08-17): squash-merge leftovers, PR merge CLI branch-deletion side effects, git cherry limits on multi-commit squashes, branch-name reuse and post-merge-commit hazards"
---

# Git Branch Cleanup

Delete local branches whose changes are provably on the remote default branch — nothing else — and only after the user approves the list.

## When to Use

- After merging pull requests (especially squash merges), or when stale worktree/feature branches accumulate; this includes stale `worktree/*` or feature branches left over from agent sessions (e.g. herdr-managed worktrees).
- User asks to "clean up branches", "delete merged branches", "清理分支", or "把已合并的分支删掉"

## When NOT to Use

- Deleting **remote** branches — out of scope; remotes are read-only here
- Removing worktree **directories** — this skill only prunes stale worktree registrations
- Cleaning stashes, tags, or reflog entries
- Any repo where the user has not confirmed the deletion list

## Inputs

| Input       | Required                  | Format          | Example                |
| ----------- | ------------------------- | --------------- | ---------------------- |
| Remote name | No (default `origin`)     | git remote name | `upstream`             |
| Dry run     | No (flag in user request) | "just show me"  | user says "先看看就好" |

## Hard Rules

1. **Never delete before the user confirms the exact branch list.** No batch shortcuts, no "obviously safe" exceptions.
2. **`[gone]` upstream alone NEVER qualifies a branch for deletion.** A remote branch can be deleted manually while the work is unmerged. `[gone]` is only a hint to run the merge checks.
3. A branch is a deletion candidate ONLY if it passes at least one of:
   - **Check A**: `git merge-base --is-ancestor <branch> <default>` exits 0 (ordinary merge)
   - **Check B**: `git cherry <default> <branch>` output contains ONLY `-` lines (every commit patch-equivalent — single-commit squash merges)
   - **Check C**: a PR found by `gh pr list --state merged --search "head:<branch>" --json number,title,headRefOid` has `headRefOid` **equal to** the local tip (`git rev-parse <branch>`) — the merged PR is provably THIS branch state

   Classification when checks fail or cannot run:
   - All three checks RAN and failed → **unmerged** (report only)
   - C's search returns merged PRs but none matches the local tip (branch name reused, or commits added after the PR merged) → **manual review**
   - Check C cannot run (`gh` missing, no network) and the branch failed A and B → **unverified**, treated exactly like manual review — never "unmerged", because a squash-merged branch could not be tested
     Manual-review and unverified branches are NEVER deleted by this skill — not even on user request — because merge status is unproven; the user deletes them outside this skill if they choose.

4. **Detect the default branch from `<remote>/HEAD`** (e.g. `origin/HEAD`), never hardcode `main`/`master`. If unset: `git remote set-head <remote> --auto` first.
5. **Never touch branches checked out in any active worktree** (including the current branch). Build the untouchable set from `git worktree list` before classifying.
6. Use `git branch -d` for Check-A branches; `git branch -D` for Check-B/C branches (git cannot see their merge).

## Workflow

### Step 1: Build the untouchable set

```bash
git worktree list --porcelain | awk '/^branch /{print $2}' | sed 's#^refs/heads/##'
```

Step 1 must extract the names of every branch checked out in any worktree. The shown pipeline is the validated POSIX-shell implementation; a non-POSIX environment may use an equivalent command, but it must satisfy that extraction requirement.
Within this pipeline, the `sed` step is mandatory: porcelain emits fully-qualified refs
(`refs/heads/main`), while candidate branches are compared by short name
(`main`). Compare short names against short names only. Worktrees in detached
HEAD state emit no `branch` line and hold no branch — nothing to exclude from
them. Also add the current branch (`git branch --show-current`). The resulting
set is excluded from candidacy regardless of merge state.

### Step 2: Sync remote state and resolve the default branch

```bash
git fetch <remote> --prune
git remote set-head <remote> --auto   # only if <remote>/HEAD is missing
DEFAULT=$(git symbolic-ref --short refs/remotes/<remote>/HEAD)   # e.g. origin/main
```

`--prune` deletes stale **remote-tracking** refs only; it never touches local branches.

### Step 3: Classify every non-untouchable branch

For each branch `B` (skip the local counterpart of the default branch if it exists):

```bash
# Check A — ordinary merge (ancestor of remote default)
git merge-base --is-ancestor "$B" "$DEFAULT" && echo MERGED

# Check B — single-commit squash merge (all commits patch-equivalent)
git cherry "$DEFAULT" "$B"

# Check C — the merged PR is provably this branch state
TIP=$(git rev-parse "$B")
gh pr list --state merged --search "head:$B" --json number,title,headRefOid
# candidate via C ONLY if some returned PR has headRefOid == $TIP
```

- Passes A, or B with only `-` lines, or C with SHA equality → **candidate** (record which check passed; for C record PR number and title)
- C's search returns merged PRs but none matches `$TIP` → **manual review** (name reused, or commits added after merge)
- `gh` invocation itself fails (missing CLI, network error) → mark C **unverified** for ALL branches that failed A and B, and say so once in the report
- Fails all three executed checks → **unmerged** (report only)
- Also record per branch: tip subject (`git log -1 --format=%s "$B"`) and upstream state from `git branch -vv` (`[gone]` / ahead-behind / no upstream) as context columns — never as the decision criterion (Hard Rule 2).

### Step 4: Present the list and ask

Show one table in the user's conversation language, three sections:

```
| Branch | Tip | Why safe | Upstream |
| deletable candidates … |
— manual review / unverified — kept, not deletable here —
| rows with PR number/title and SHA mismatch, or "Check C unavailable" … |
— unmerged, not deletable —
| unmerged rows … |
```

For downstream consumers, candidate rows have this stable field order: `branch | check that proved merge | delete flag | classification`. The human-facing table may also show Tip and Upstream as context columns; candidate delete flags are `-d` for Check A and `-D` for Check B/C, and their classification is `candidate`.

Ask the user to confirm which **candidates** to delete (all / a subset / none). Manual-review and unverified rows are informational only: if the user wants them gone, they run the deletion themselves outside this skill. This gate is mandatory even when the list has one row.

**Gate 4 — Proceed to Step 5 only when ALL are true:**

- The exact candidate subset was shown and explicitly confirmed by the user.
- Manual-review, unverified, and unmerged rows are excluded.
- The user did not request a dry run.

This confirmation gate is mandatory and cannot be bypassed by a caller, automation, or prompt; this skill has no auto-approve or unattended-delete path. If the user asked for a dry run, stop here.

**Validation loop:** If evidence is disputed or stale, re-run the relevant merge check and refresh the PR/SHA evidence before presenting a revised table. A SHA mismatch remains manual review and is never promoted without proof.

### Step 5: Delete approved candidates only

```bash
git branch -d <check-A-branches>
git branch -D <check-B/C-branches>
```

Never include manual-review, unverified, or unmerged branches in either command. If a deletion fails because the branch is checked out somewhere, do NOT force it — report it as still active.

### Step 6: Finalize and report

```bash
git worktree prune   # drops registrations of deleted worktree dirs only; safe
git branch -vv
```

Report: deleted branches, manual-review/unverified rows (kept), skipped-unmerged branches, final branch list.

## Gotchas

- **Multi-commit squash merges defeat patch-id.** When a PR with several commits is squash-merged, the resulting single commit matches NO individual patch-id: `git cherry` reports every branch commit as `+` even though the content is fully on the default branch (verified on a real two-commit squash: both commits `+`). That is why Check C exists — PR merge status is authoritative for this case.
- **Offline runs must not mislabel squash leftovers.** Without `gh`/network, Check C cannot distinguish a multi-commit-squash-merged branch from a truly unmerged one — hence the unverified classification (kept, reported) instead of "unmerged". Never present unverified branches as definitively unmerged.
- **Check C's SHA equality is load-bearing.** Without comparing `headRefOid` to the local tip, two hazards slip through: a branch NAME reused by a later PR (wrong PR matches), and commits pushed/committed locally AFTER the PR merged (ahead of the merged state). SHA mismatch = manual review, never a candidate.
- **`git cherry` false `-`**: patch-id can rarely match by coincidence. Mitigation: the confirmation table always shows tip subjects so the user can veto anything suspicious.
- **Squash-merged branches look unmerged to git**: `git branch --merged` and `-d` both refuse, because the original commits are not ancestors of the default branch. Use `-D` for Check-B/C branches only.
- **`gh pr merge --delete-branch` can delete the local branch currently checked out in a worktree**, leaving that worktree on an unexpected ref. After using gh to merge, check `git branch -vv` and worktree integrity before running this skill.
- **The default branch is often checked out in the primary worktree** — it appears in the untouchable set anyway (Step 1); never attempt to "clean" it. If it is merely behind, offer a fast-forward (`git merge --ff-only`) only when that worktree is clean, and separately from branch deletion.
- **`<remote>/HEAD` may be unset in fresh clones** — always resolve via Step 2 rather than assuming, and never hardcode the remote name in HEAD lookups.
- Branches with no upstream configured are treated like any other: run all three checks; never delete them just for being "orphaned".

## Output Contract

The human-readable report is primary. On completion, return:

1. The confirmation table that was approved (branch / tip / why safe / upstream)
2. Deletion results: succeeded, failed-with-reason (e.g. checked out elsewhere)
3. Manual-review and unverified rows kept in place, with PR number/title and the SHA mismatch or "Check C unavailable" reason shown
4. Unmerged branches left in place, with their ahead-commit count
5. Final `git branch -vv` output after execution; for a dry run, state that no deletion was attempted and omit a post-deletion final state

Stable fields for downstream consumers, in this order:

```text
candidate: branch | check that proved merge | delete flag | classification
dry_run: candidate table | manual-review/unverified rows | unmerged rows
execute: approved candidate table | deletion results | kept rows | final branch list
```

For a dry run, return the candidate and non-deletable tables only; do not execute deletion commands, report deletion results, or claim a post-deletion final state.
