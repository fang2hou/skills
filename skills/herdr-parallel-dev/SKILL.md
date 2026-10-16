---
name: herdr-parallel-dev
description: >
  Orchestrates 2+ deliverables or multi-goal Git Flow work inside Herdr
  (HERDR_ENV=1): one worktree and agent per task, early merge of conflict-free
  tasks, dynamic dependency reordering, and branch sync. Skip for 1 task or
  linear stacks.
license: MIT
compatibility: Requires HERDR_ENV=1, herdr CLI, git, gh, jq, Bash, and standard POSIX utilities inside a Herdr-managed pane.
metadata:
  author: fang2hou
  version: "2.4"
  sources: "Incident-proven workflow (2026-08-17 multi-project worktree misadventure + 3-PR sequential merge); herdr CLI behavior verified 2026-08-18; Git Flow multi-goal detection and dynamic orchestrator scheduling revision 2026-10-17"
---

# Herdr Parallel Development

Act as the orchestrator session inside Herdr: run N repo tasks across N herdr-managed git worktrees and agents, monitor and dynamically schedule reviews and landings as tasks settle, sync remaining branches when prerequisites or early merges advance the target branch, and restore the machine to its starting state.

## Trigger Rule

Count deliverables and check the repo's branching model, not keywords. A deliverable is anything that ships on its own: a PR, a feature branch that merges into the integration branch before release, a self-contained fix, refactor, or docs pass. **Two or more deliverables without a hard linear dependency mean this skill, always.**

- **Multi-goal + Git Flow auto-detection**: Before writing code on any multi-goal request ("implement X and Y", "fix A, update B, add C"), check whether the repo follows Git Flow or a multi-branch integration model (`origin/develop`, `origin/integration`, `origin/release/*`, `.gitflow`, or branch rules in `AGENTS.md` / `CONTRIBUTING.md`). When it does, each goal is a separate feature/fix branch into `$INTEGRATION` — switch into orchestrator mode and fan out Herdr agents instead of working in a single process.
- The user need not say "parallel", "herdr", or "worktree". Even small tasks qualify when each needs its own branch or PR.
- Load at planning time, before writing code. If task 1 of N is already underway in a shared checkout, turn that work into row 1's branch and fan out the rest.
- Never serialize execution through one agent or branch; serial per-merge landing (Step 7) is fine, serial execution is not.

## When to Use / When NOT to Use

- **Use**: 2+ independently shippable tasks on one repo (multiple PRs, Git Flow feature sets into `develop`, independent fixes/refactors), colliding multi-file edits, or landing and auditing multiple finished agent branches.
- **Skip**:
  - A single deliverable: use a plain herdr agent in a sibling pane without a worktree.
  - Hard dependency chains (B cannot code before A merges) or stacked PRs: sequence them (see table below).
  - Outside Herdr (`HERDR_ENV != 1`): use native parallel subagents instead.
  - Stale branches/worktrees from earlier sessions: use `git-branch-cleanup` (Step 9 cleans only this run).
  - Inspecting/controlling user panes when the user explicitly names Herdr: use the base `herdr` skill (`npx skills add ogulcancelik/herdr -g`).

## Parallel, Phased, or Sequential

Decide before Step 1, record the initial verdict per task in the run table, and update it dynamically in Steps 5–7 as tasks progress:

| Situation                                                       | Verdict                                                 | Why                                                                       |
| --------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------- |
| 2+ deliverables, no ordering need between them                  | Fan out all now; land opportunistically as tasks settle | Fast conflict-free tasks land early without waiting for slow siblings     |
| Multi-goal request on a Git Flow repo (`develop` / `release/*`) | Fan out one feature/fix branch per goal                 | Git Flow isolates each goal on its own branch into `$INTEGRATION`         |
| Soft / late-discovered dependency (slow C must land before A/B) | Fan out all now; hold A and B at Step 7 until C lands   | Parallel coding saves time; A and B pull/rebase onto `$BASE` once C lands |
| Hard prerequisite (B cannot start without A's new schema)       | Land A first, then fan out B and its siblings           | Agents cannot code against contracts that do not exist yet                |
| Stacked PRs, each based on the previous one                     | Sequential by design                                    | A linear rebase chain cannot be produced in parallel                      |
| Same-file hotspot shared by every task                          | Re-slice the tasks, or sequence them                    | Conflict-resolution cost exceeds the parallel gain                        |
| Two trivial chores an agent finishes in minutes                 | Serial batch is acceptable                              | Worktree setup costs ~1 min/task; anything needing its own PR fans out    |

## Inputs

| Input        | Required | Format                                             | Example                               |
| ------------ | -------- | -------------------------------------------------- | ------------------------------------- |
| Project path | Yes      | absolute path                                      | `/Users/me/Developer/projects/my-app` |
| Task list    | Yes      | 1–8 self-contained tasks                           | each becomes one worktree + one agent |
| Landing mode | Yes      | `integration` / `pr`                               | see Step 7                            |
| Base branch  | No       | branch, default `origin/<integration>` from Step 1 | a work branch in `integration` mode   |

Cap concurrency at 8 worktrees; queue excess tasks and dispatch as earlier agents settle.

## Forge Boundaries & Tool Contract

- **Forge**: `gh` commands are the **GitHub-forge-specific** baseline. Load [Forge Adaptation](references/forge-adaptation.md) before Step 1 when the repo is not on GitHub, `gh` is unavailable, or forge behavior differs; use only a verified client/API.
- **Herdr JSON**: workspace creation returns `.result.workspace.workspace_id`, worktree creation returns `.result.root_pane.pane_id` and `.result.worktree.path`, and listing returns `.result.worktrees[]`. Never infer IDs from pane order.

## Hard Rules

1. **Bind the repo explicitly on every worktree creation.** Pass `--workspace <project-space-id>` (preferred) or `--cwd <absolute-project-path>` so herdr never targets a recently focused foreign repo. Trust a workspace ID only from `herdr worktree list --cwd "$PROJECT"` or `workspace create --cwd "$PROJECT"`.
2. **Let herdr own the layout.** Pass no `--path`, no `--label`, and `--no-focus` while dispatching.
3. **Verify every worktree before dispatching** with `scripts/verify-worktrees.sh "$PROJECT" <created-paths...>`. Remove and recreate any wrong-origin worktree.
4. **Start every agent prompt with a guard check.** The agent checks `git remote get-url origin` and a known path before working.
5. **One worktree = one branch = one agent.** Never share a worktree.
6. **Write self-contained agent prompts.** Include the guard check, ground truth, task, verification gate, commit rules, and “decide and document; do not ask.”
7. **Land only on a green gate.** Never merge or advance while target CI is red; Deploy does not substitute for CI.
8. **Retire agents before removing worktrees.** Stop the agent (`ctrl+c`, then `ctrl+d`; confirm absent from `herdr agent list`) before `herdr worktree remove`.
9. **Clean up only this run's objects** after merge proof. Use `git branch -D` only for squash-merged run branches; leave pre-existing spaces/branches untouched.
10. **Fan out all parallelizable tasks before reviewing or landing.** Dispatch all independent or soft-dependent worktrees/agents first (Step 4), then run the orchestrator loop (Steps 5–7) to review and opportunistically land early tasks while slower siblings work.

## Run Table

State lives in this session, not on disk, so two runs never collide. Keep one row per task:

| task | branch | worktree workspace | pane | worktree path | agent | status | deliverable |
| ---- | ------ | ------------------ | ---- | ------------- | ----- | ------ | ----------- |

The fixed field order is `task`, `branch`, `worktree_workspace`, `pane`, `worktree_path`, `agent`, `status`, `deliverable`; keep it in the human table and downstream exports. Also record the project's space as **already open** (leave it) or **opened by this run** (close it in Step 9).

After interruption, rebuild the table from `herdr worktree list --cwd "$PROJECT"`, `herdr agent list`, and `gh pr list` (**GitHub-forge-specific; use a verified review-list equivalent elsewhere**). Never recreate a worktree whose branch exists; adopt it and continue from observed state.

## Workflow

### Step 1: Detect Git Flow / branching model and fix the landing mode

```bash
git -C "$PROJECT" remote get-url origin                            # expected repo
DEFAULT=$(git -C "$PROJECT" symbolic-ref --short refs/remotes/origin/HEAD)   # do not hardcode
DEFAULT=${DEFAULT#origin/} && echo "default branch: $DEFAULT"
git -C "$PROJECT" branch -r --format='%(refname:short)' | grep -E '^origin/(develop|devel|integration|mainline|release/.*)$' || true
git -C "$PROJECT" config --get-regexp '^gitflow\.' || test -f "$PROJECT/.gitflow" || true
grep -rniE "git ?flow|integration branch|merge into (develop|main)" "$PROJECT/AGENTS.md" "$PROJECT/CONTRIBUTING.md" "$PROJECT/README.md" 2>/dev/null | head
gh repo view --json squashMergeAllowed,deleteBranchOnMerge --jq '{squash: .squashMergeAllowed, deleteOnMerge: .deleteBranchOnMerge}' # GitHub-forge-specific
ls "$PROJECT/.github/workflows/"                                   # GitHub Actions baseline; use verified CI discovery elsewhere
grep -n "merge" "$PROJECT/AGENTS.md" "$PROJECT/CONTRIBUTING.md" 2>/dev/null | head
```

Record the default branch, the integration branch, whether the repo uses Git Flow, merge method (squash unless the repo says otherwise), head auto-delete behavior, and workflow names that must be green.
`INTEGRATION` is where finished work merges: `develop` (or documented integration branch) on Git Flow/release-train repos; `$DEFAULT` on trunk-based repos. Decide it from remote branches, `.gitflow`, and `AGENTS.md` / `CONTRIBUTING.md`, never `origin/HEAD` alone. On Git Flow multi-goal requests, each goal branches off `origin/$INTEGRATION`. Landing modes:

- **`pr`** (default for N PRs and Git Flow feature sets): each task ships its own PR to `$INTEGRATION`.
- **`integration`**: one work branch off `$INTEGRATION`; task branches merge into it and ship as one PR.
  Bind the mode's base once and carry it in the run table:

```bash
INTEGRATION=develop                      # discovered above; trunk-based repos: "$DEFAULT"
MODE=pr                                   # or: MODE=integration
WORK_BRANCH=""                            # integration mode: the work branch name
if [ "$MODE" = integration ]; then BASE="$WORK_BRANCH"; else BASE="origin/$INTEGRATION"; fi
git -C "$PROJECT" rev-parse --verify "$BASE"   # fail here, not at create time
```

### Step 2: Plan branches

For each task choose a `type/slug` branch, an agent name `<slug>-pr` matching `[a-z][a-z0-9_-]{0,31}`, and a blast radius: isolated infra lands first for attribution; docs/style second as baseline; widest-surface feature last. Compute the conflict surface (files touched by ≥2 tasks via `git diff --name-only`) to set Step 7 order.

### Step 3: Create worktrees inside the project's herdr space

Worktrees belong to the project's space, nested under it exactly as the TUI's New Worktree action (`prefix+shift+g`) creates them. Resolve that space once, then create each worktree against it:

```bash
SPACE=$(herdr worktree list --cwd "$PROJECT" | jq -r '.result.worktrees[] | select(.is_linked_worktree == false) | .open_workspace_id // empty' | head -1)
SPACE_OPENED_BY_RUN=no
if [ -z "$SPACE" ]; then
  SPACE=$(herdr workspace create --cwd "$PROJECT" --no-focus | jq -r '.result.workspace.workspace_id')
  SPACE_OPENED_BY_RUN=yes
fi
herdr worktree create --workspace "$SPACE" --branch feat/rolldown-bundler --base "$BASE" --no-focus
# record .result.workspace.workspace_id, .result.root_pane.pane_id, .result.worktree.path
```

One create per task. Each yields its own workspace labelled with the branch and nested under `$SPACE`; do not expect the pane in the caller's workspace. `$BASE` is `origin/$INTEGRATION` in `pr` mode and the work branch in `integration` mode. Then gate dispatch:

```bash
SKILL_DIR=<directory containing this SKILL.md>
"$SKILL_DIR/scripts/verify-worktrees.sh" "$PROJECT" <created-paths...>   # runs skills/herdr-parallel-dev/scripts/verify-worktrees.sh
```

Exit 0 dispatches; any FAIL row means stop and fix first.

### Step 4: Dispatch agents

```bash
sleep 3                                                   # new pane needs a settled shell
herdr agent start rolldown-pr --kind omp --pane <pane-id> # returns when ready
herdr agent prompt rolldown-pr '<full self-contained brief>'
sleep 6 && herdr agent get rolldown-pr                    # must report agent_status "working"
```

`agent_pane_busy` means wait and retry; never dispatch into a non-shell pane. Pick the agent kind from the installed list (`herdr agent` prints it); `omp` is common. The brief's gate command comes from AGENTS.md/README (for example `mise run check`), never an assumption.

Prompt template (all parts mandatory):

```
<ONE-LINE TASK>. You are in a dedicated worktree on branch <branch> (base <base>) of the <repo-name> repo.

Guard check: run `git remote get-url origin` — it must equal <expected-url> and <one known path> must exist. If either check fails, stop and report immediately; do not work in a different repo.

Ground truth (verify yourself): <files, symbols, current behavior, pointers>
Task: <numbered steps including verification and the repo's gate command>
Deliver: Conventional Commits (English), push the branch, and report its tip. In `pr` mode, open a review request through the configured forge (GitHub: `gh pr create --base <integration>`); in `integration` mode, do not open one. Do not merge.
Rules: <package manager>, stay in your worktree, no unrelated refactors, decide and document; do not ask.
```

The 6-second check matters: a prompt that failed to land leaves the agent `idle`; resend or read the pane before assuming work started.

### Step 5: Monitor and dynamically schedule (Orchestrator Loop)

The current session is the active scheduler across all running herdr panes. Poll and react as individual agents settle instead of waiting passively for every agent to finish at once:

```bash
herdr agent wait <name> --timeout 300000   # returns on first settled state
herdr agent get <name>                     # idle | working | blocked | done
herdr agent read <name> --source visible --lines 12   # TUI agents: viewport only
```

Loop `wait` in ~5-minute cycles across active agents. Full-screen agents use the alternate screen, so read `visible` rather than `recent-unwrapped`. On `blocked` (approval/question UI), read the pane and resolve via `agent prompt` or `send-keys`. An agent in the wrong repo gets `send-keys <name> ctrl+c` immediately; verify the foreign worktree is clean before touching it.

**Dynamic orchestration rules while monitoring** (load [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md) for detailed procedures):

1. **Immediate review on settle**: As soon as an agent reaches `done` or `idle`, run Step 6 on that worktree while sibling agents continue working.
2. **Opportunistic early merge (1+ tasks)**: When one or more tasks are `accepted (ready to land)`, have no file overlap (`git diff --name-only "$BASE...$b"`), and have no logical dependency on still-running tasks, advance them immediately to Step 7 and land them while slower tasks continue.
3. **Late-discovered dependency reorder**: If a slower task (e.g., Task 3) turns out to be a prerequisite for earlier-finishing tasks (Tasks 1 and 2), mark Tasks 1 and 2 `accepted (held for <Task 3>)`, wait for Task 3 to pass Step 6 and land first, then sync Tasks 1 and 2 onto the updated `$BASE` before landing them.
4. **Proactive base sync**: After any merge into `$INTEGRATION` (or `WORK_BRANCH`), sync held/next branches (`git fetch origin --prune && git rebase "$BASE"`, re-run repo gate, `push --force-with-lease`). If a still-`working` agent needs the new base mid-flight, prompt it to commit or stash its dirty tree first, then `git fetch origin && git rebase origin/$INTEGRATION` (or `git pull --rebase`), re-run the gate, and continue.
   **Stall escalation:** `working` across two cycles (~10 min) with zero worktree changes (`git status --porcelain` before/after), or over ~60 min total, means read the pane and steer with a specific prompt. Still unresponsive → `ctrl+c` and take over in that worktree.

### Step 6: Accept, hold, or send back

For each settled agent, verify the deliverable yourself, never its summary:

```bash
git -C <worktree> log --oneline "$BASE"..HEAD     # real commits exist
git -C <worktree> status --porcelain              # nothing stranded uncommitted
git -C <worktree> diff "$BASE"...HEAD --stat      # scope matches task
gh pr list --head <branch>                        # GitHub-forge-specific; pr mode only
```

Run the repo gate in the worktree, then decide:

- **Accept (ready to land)**: scope is clean, gate is green, and no unmerged prerequisite or file-hotspot conflict blocks it. Leave the agent alive/idle for Steps 7–8; eligible for immediate landing.
- **Accept (held for `<task>`)**: deliverable passes verification, but dynamic scheduling found it must land after a still-running prerequisite `<task>`. Leave the agent alive/idle; once `<task>` lands, sync this branch with `$BASE`, re-run the repo gate, and land.
- **Send back**: reply via `agent prompt` with the specific defect, expected behavior, verification, failing command, and output (never a vague request), then return to Step 5; two failed round trips on one defect means take over and record why.
- **Drop**: remove an unsalvageable task from the landing plan and record the reason.

### Step 7: Land (Opportunistic Batch or Full Wave)

Step 7 runs either for the full set of accepted tasks or for an opportunistic early batch (one or more `accepted (ready to land)` tasks with zero file overlap and no dependency on still-running tasks).

#### Phase A: Plan or Re-plan (Gate 7A)

Order the batch's accepted branches by dependency edges first, then blast radius: foundational/prerequisite task first, isolated infra second, docs/style third, widest-surface feature last so it rebases onto the updated baseline. If a slower prerequisite task is still running, hold dependent accepted tasks out of the current batch. Write ordered branches, held branches (with dependency reason), target base, landing mode, and rationale in the run and landing tables. The user decides ambiguous mode/order.

**Gate 7A:** every branch in the current landing batch is accepted, has no unmerged prerequisite, is tied to this run, and has its mode/base/order recorded before any merge.

#### Phase B: Validate (Gate 7B)

```bash
for b in <ordered batch branches>; do
  git -C "$PROJECT" log --oneline "$BASE..$b" --stat
  git -C "$PROJECT" diff --name-only "$BASE...$b"
done
```

Confirm touched files match tasks, no dropped or held task is included, no silent conflict exists with still-running tasks, the repository gate is green, and required review checks are green. In GitHub mode, `gh pr list --head <branch>` and run-status queries are the forge-specific baseline; use a verified equivalent elsewhere (load [Forge Adaptation](references/forge-adaptation.md) before this phase when the forge is not GitHub).

**Gate 7B:** stop on unexpected scope/review state, required checks, or mergeability; record evidence before proceeding.

#### Phase C: Execute and Sync Downstream (Gate 7C)

**Mode `integration`** (children merge into the work branch, which ships as one review request once all non-dropped tasks land):

```bash
git -C "$PROJECT" checkout <work-branch> && git -C "$PROJECT" pull --ff-only
for b in <ordered batch branches>; do
  git -C "$PROJECT" merge --squash "$b" && git -C "$PROJECT" commit   # or --no-ff, per repo convention
  <repo gate command>                                                 # green before next branch
  git -C <next-worktree> fetch origin --prune
  git -C <next-worktree> rebase <work-branch>                         # or: git pull --rebase origin <work-branch>
  <repo gate command in next-worktree>                                # re-verify after sync when prerequisite changed contracts
  git -C <next-worktree> push --force-with-lease
done
git -C "$PROJECT" push
# When all non-dropped tasks have landed:
gh pr create --base <integration> --head <work-branch>  # GitHub-forge-specific
```

**Mode `pr`** (one review request per task, strictly sequential per merge and CI-gated; GitHub-forge-specific baseline syntax):

```bash
gh pr merge <N> --squash                          # 1. merge, per repo convention
gh run list --branch <integration> --limit 2 --json databaseId,name
gh run watch <ci-run-id> --exit-status            # 2. green required (Hard Rule 7)
git -C <next-worktree> fetch origin --prune       # 3. sync next or formerly held branch with updated $INTEGRATION
git -C <next-worktree> rebase origin/<integration> # or: git -C <next-worktree> pull --rebase origin <integration>
<repo gate command in next-worktree>              # 4. re-verify locally if the prior merge was a prerequisite
git -C <next-worktree> push --force-with-lease
# 5. required checks completed and mergeable, then repeat
```

Another forge's equivalent must merge exactly one accepted review request, identify and await its required CI checks, and sync/rebase the next branch only after green checks. When an opportunistic batch finishes while slower tasks are still running, return to Step 5 to monitor the remaining tasks and run Step 7 again when the next batch or prerequisite settles.

**Gate 7C:** after each merge, observe proof that expected content is on the target and required CI is green; after syncing any downstream or formerly held branch onto the updated `$BASE`, confirm its worktree gate is green before merging it; record merge/run identifiers before advancing. Load [Conflict Resolution](references/conflict-resolution.md) when a Step 7 rebase/pull reports conflicts. Load [CI Failure Triage](references/ci-triage.md) when a landing gate is red or a run needs classification.

### Step 8: Post-merge consistency audit

Once everything is on the target branch and green: (1) **sync**: for squash merges, compare each squash commit with its branch tip's touched files; (2) **coherence**: check that the ADR index, architecture map, README/DEVELOPMENT commands, `mise.toml`/`package.json`, and shared concepts agree (`git log --oneline` plus targeted `git show <squash> -- <shared-files>`); (3) **style propagation**: if an early branch changed global style and a later branch touched the same files, verify conformance. Rebase merges content, not intent; re-prompt the later agent with “realign <files> to the structure from commit <A-squash>, keep B's facts, zero code changes,” then land the follow-up.

### Step 9: Retire agents, then remove worktrees

Only after merge proof (PR shows merged or content is on target), retire first because `worktree remove` kills the pane and agent:

```bash
herdr agent send-keys <name> ctrl+c
sleep 1
if herdr agent get <name> >/dev/null 2>&1; then herdr agent send-keys <name> ctrl+d; sleep 2; fi
herdr agent list | jq -r '.result.agents[].name'   # <name> must be absent before removal
herdr worktree remove --workspace <worktree-workspace-id>
test ! -e <worktree-path> && echo "gone: <worktree-path>"
herdr worktree list --cwd "$PROJECT" | jq -c '.result.worktrees[] | {branch, path}'
git -C "$PROJECT" fetch --prune
git -C "$PROJECT" branch -vv
git -C "$PROJECT" branch -D <branch...>                   # squash-merged only
if [ "$SPACE_OPENED_BY_RUN" = yes ]; then herdr workspace close "$SPACE"; fi
```

Removal deletes the checkout, prunes registration, and closes its workspace without deleting the branch; if still listed in `herdr worktree list`, fix the failure rather than closing the workspace by ID. On `dirty_worktree_requires_force`, inspect `git status --porcelain` and `git diff` first and `--force` only when worthless or committed elsewhere. Before any `--force`, `branch -D`, or `push --force-with-lease`, record branch tip, remote tip, worktree path, and status; load [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md) for recovery proofs. Confirm merge proof before `branch -D`, and leave `~/.herdr/worktrees/<repo>/` in place.

## Verification

The run is done only when observed:

- [ ] Every task row is accepted or dropped with a reason.
- [ ] `verify-worktrees.sh "$PROJECT" <paths>` exited 0 before any agent started.
- [ ] Every accepted branch's content is on target (`git -C "$PROJECT" log --oneline <base>..<target>`) or its PR reads merged.
- [ ] Target CI is green on its latest run; Step 8 found no unresolved sync, coherence, or style drift.
- [ ] `herdr agent list` contains none of this run's names; `herdr worktree list --cwd "$PROJECT"` contains none of its paths.
- [ ] `git -C "$PROJECT" branch -vv` has no leftover run branch without a recorded reason.
- [ ] `herdr workspace list` shows the project's space exactly as found (closed again only if this run opened it).

`scripts/verify-worktrees.sh` emits TSV (`status`, `worktree`, `branch`, `url`, `dirty`, `ahead`) or `--format json` (`status`, `count`, `results`, `expected_url`) on stdout and diagnostics on stderr (exit 0 pass, 1 fail, 2 usage/env error).

## Failure Handling

| Failure                         | Signal                                      | Action                                                                                    |
| ------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Worktree on wrong repo          | verifier FAIL or agent guard-check report   | Remove, fix binding, recreate; never edit in place.                                       |
| `agent_pane_busy`               | `agent start` error                         | Wait for shell prompt and retry.                                                          |
| Prompt did not land             | `agent get` still `idle` after ~6s          | Re-send; read pane before assuming work started.                                          |
| Agent `blocked` / stalled       | approval UI or no diff across two 5m cycles | Read pane; answer/steer via `agent prompt` or `send-keys`, else `ctrl+c` and take over.   |
| Deliverable rejected twice      | same defect after two send-backs            | Take over in that worktree and record why.                                                |
| Late prerequisite discovered    | settled task A/B needs still-running task C | Mark A/B `accepted (held for C)`, land C first, sync A/B onto `$BASE`, re-gate, and land. |
| Rebase conflict, semantic       | conflicting files span a feature            | Hand to that branch's agent with both intents; never drop one side.                       |
| CI red (infra vs regression)    | HTTP 429/setup vs project check failure     | Infra: rerun failed jobs; regression: stop landing, fix branch, re-run gates.             |
| `dirty_worktree_requires_force` | `worktree remove` exits 1                   | Inspect/report uncommitted work; `--force` only once confirmed worthless.                 |
| Interrupted run                 | table lost                                  | Rebuild from `worktree list`, `agent list`, and `gh pr list` (or forge equivalent).       |

Stop and ask the user when landing mode is ambiguous, a merge needs force-pushing a shared branch, uncommitted agent work has value you cannot judge, or cleanup would touch an object this run did not create.

## Gotchas

- `worktree create` without `--workspace` or `--cwd` can target the wrong repo; verify via `remote get-url origin` (Hard Rule 1).
- Git Flow points `origin/HEAD` at `main` while features target `develop`; Step 1 resolves `$INTEGRATION` explicitly.
- `--label` overwrites the branch handle in the sidebar; `--no-focus` prevents stealing focus.
- A fresh pane rejects `agent start` with `agent_pane_busy` until the shell settles; `agent prompt` without `--wait` needs `agent get` to confirm `working`.
- An `idle`/`done` agent still holds its pane and name until retired; squash-merged branches require `git branch -D` after merge proof; resolve rebase conflicts inside the branch's worktree, never the main checkout.

## Output Contract

On completion, return:

1. Run table in fixed order `task → branch → worktree workspace → pane → worktree path → agent → status → deliverable` (PR URL or branch tip), including held/reordered tasks, dropped tasks, and reasons.
2. Review log: first-time accepts, held-for-prerequisite holds, send-backs with defects and round trips, and manual takeovers.
3. Landing log: mode, batch waves (early opportunistic merges vs prerequisite-first reorders), downstream branch syncs (`fetch` + `rebase`/`pull`), each gate outcome, and flakes rerun.
4. Audit results: sync, coherence, and style-propagation findings with fixes.
5. Cleanup report: agents stopped, worktrees removed, branches deleted with proof basis, space closed/left open and why, preserved objects, and final `git branch -vv`, `herdr worktree list --cwd "$PROJECT"`, and `herdr workspace list`.

Stable run-table fields for downstream consumers:

```text
task | branch | worktree_workspace | pane | worktree_path | agent | status | deliverable
```

## References

- [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md): load during Steps 5–7 for early-merge batching, late prerequisite reordering, and mid-flight branch sync, or during Step 9 for force-operation recovery proofs
- [Forge Adaptation](references/forge-adaptation.md): load before Step 1 or Step 7B when the repo is not hosted on GitHub or `gh` is unavailable
- [Conflict Resolution](references/conflict-resolution.md): load during Steps 5 or 7C when rebasing or pulling onto the updated integration branch reports conflicts
- [CI Failure Triage](references/ci-triage.md): load during Step 7C when a landing gate is red or a CI run needs infrastructure vs regression classification
