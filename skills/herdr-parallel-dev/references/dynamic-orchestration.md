# Dynamic Orchestration & Force Recovery

Load this reference during Steps 5–7 when dynamic scheduling is needed (opportunistic early merges, late-discovered dependency reordering, or syncing downstream branches) or during Step 9 before any `--force`, `branch -D`, or `push --force-with-lease`.

## Contents

- [Dynamic Orchestration Loop (Steps 5–7)](#dynamic-orchestration-loop-steps-57)
- [Force and Recovery Protocol (Steps 7 & 9)](#force-and-recovery-protocol-steps-7--9)

## Dynamic Orchestration Loop (Steps 5–7)

The orchestrator session actively manages all running Herdr panes and reacts as individual tasks settle:

1. **Immediate review on settle**: As soon as an agent reaches `done` or `idle`, run Step 6 on that worktree while sibling agents continue working.
2. **Opportunistic early merge (1+ tasks)**: When one or more tasks are `accepted (ready to land)`, have no file overlap (`git diff --name-only "$BASE...$b"`), and have no logical dependency on still-running tasks, advance them immediately to Step 7 and land them sequentially while slower tasks continue.
3. **Late-discovered dependency reorder**: If inspecting a settled task or a running agent reveals that a slower task (for example Task 3) introduces a foundational contract, migration, or shared helper that earlier-finishing tasks (Tasks 1 and 2) depend on:
   - Mark Tasks 1 and 2 `accepted (held for <Task 3>)` in the run table and keep their agents alive/idle.
   - Wait for Task 3 to finish and pass Step 6.
   - Land Task 3 first (Step 7), wait for target CI to turn green, and then sync Tasks 1 and 2 onto the updated `$BASE` before landing them.
4. **Proactive base sync for held or running tasks**: Whenever an early batch or a prerequisite task merges into `$INTEGRATION` (or `WORK_BRANCH`), update the remaining branches before they merge:
   - **Held (`accepted (held)`) or next-to-land branch**: in its worktree, run `git fetch origin --prune && git rebase "$BASE"` (or `git pull --rebase origin <target>`), re-run the repository gate command locally to confirm compatibility with the newly merged prerequisite, and `git push --force-with-lease`.
   - **Still-`working` agent that needs the new base immediately**: prompt the agent to save its dirty state before rebasing (`herdr agent prompt <name> "origin/$INTEGRATION has advanced with <merged-branch>; commit or stash your work-in-progress first, run git fetch origin && git rebase origin/$INTEGRATION (or git pull --rebase origin $INTEGRATION), pop any stash, re-run <gate>, and continue"`).

## Force and Recovery Protocol (Steps 7 & 9)

Before any `--force`, `branch -D`, or `push --force-with-lease`, record the branch tip, remote tip, worktree path, and `git status --porcelain`.

- **Local branch deleted by mistake**: restore it at the saved (or verified reflog) tip (`git branch <branch> <saved-sha>`) and prove `git rev-parse <branch>` equals it.
- **Force-push mistake**: restore the saved remote tip only after checking the target and lease (`git push --force-with-lease origin <saved-sha>:refs/heads/<branch>`), then fetch and prove `git ls-remote origin refs/heads/<branch>` equals it.
- **Worktree removed by mistake**: its committed branch still exists; recreate with explicit `--cwd "$PROJECT"` or trusted `--workspace`, rerun `scripts/verify-worktrees.sh`, and prove the recovered path is listed, on the expected branch, and at the saved tip.
- **Uncommitted files deleted by forced removal**: these have no git undo; recover only from a separately saved patch/backup, otherwise report the loss and stop.
