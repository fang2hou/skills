---
name: herdr-parallel-dev
description: >
  Orchestrates 2+ deliverables or multi-goal Git Flow work inside Herdr
  (desktop app, HC_TERMINAL_SOCKET set): one git worktree and one hc agent
  terminal per task, early merge of conflict-free tasks, dynamic dependency
  reordering, and branch sync. Skip for 1 task or linear stacks.
license: MIT
compatibility: Requires a Herdr-managed terminal (HC_TERMINAL_SOCKET set, hc CLI in PATH), git, gh, jq, Bash, and standard POSIX utilities.
metadata:
  author: fang2hou
  version: "3.0"
  sources: "Incident-proven workflow (2026-08-17 multi-project worktree misadventure + 3-PR sequential merge); hc 0.1.15 / herdr-app 0.1.10 behavior verified live 2026-11-01; dynamic orchestrator scheduling revision 2026-10-17; hc-era rewrite (plain git worktrees + hc agent terminals) 2026-11-01"
---

# Herdr Parallel Development

Act as the orchestrator session inside Herdr: run N repo tasks across N git worktrees and N named hc agent terminals, monitor and dynamically schedule reviews and landings as tasks settle, sync remaining branches when prerequisites or early merges advance the target branch, and restore the machine to its starting state.

## Trigger Rule

Count deliverables and check the repo's branching model, not keywords. A deliverable is anything that ships on its own: a PR, a feature branch that merges into the integration branch before release, a self-contained fix, refactor, or docs pass. **Two or more deliverables without a hard linear dependency mean this skill, always.**

- **Multi-goal + Git Flow auto-detection**: Before writing code on any multi-goal request ("implement X and Y", "fix A, update B, add C"), check whether the repo follows Git Flow or a multi-branch integration model (`origin/develop`, `origin/integration`, `origin/release/*`, `.gitflow`, or branch rules in `AGENTS.md` / `CONTRIBUTING.md`). When it does, each goal is a separate feature/fix branch into `$INTEGRATION` — switch into orchestrator mode and fan out Herdr agents instead of working in a single process.
- The user need not say "parallel", "herdr", or "worktree". Even small tasks qualify when each needs its own branch or PR.
- Load at planning time, before writing code. If task 1 of N is already underway in a shared checkout, turn that work into row 1's branch and fan out the rest.
- Never serialize execution through one agent or branch; serial per-merge landing (Step 7) is fine, serial execution is not.

## When to Use / When NOT to Use

- **Use**: 2+ independently shippable tasks on one repo (multiple PRs, Git Flow feature sets into `develop`, independent fixes/refactors), colliding multi-file edits, or landing and auditing multiple finished agent branches.
- **Skip**:
  - A single deliverable: use a plain hidden hc agent (`hc run --bg --name <slug> --cwd <repo> <agent> "<task>"`) without a worktree.
  - Hard dependency chains (B cannot code before A merges) or stacked PRs: sequence them (see table below).
  - Outside Herdr (`HC_TERMINAL_SOCKET` unset): use native parallel subagents instead.
  - Stale branches/worktrees from earlier sessions: use `git-branch-cleanup` (Step 9 cleans only this run).
  - Inspecting/controlling the user's spaces/tabs/terminals when the user explicitly names Herdr: use the official `herdr-core` skill (`npx skills add herdrdev/herdr-core --skill herdr-core -g`); its stub routes to the version-matched manuals — `hc --skill` for terminals and agents, `herdr-app --skill` for the window.

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
- **hc manual**: read `hc --skill` once before dispatching (Step 4); that embedded, version-matched manual is the authority for `hc` syntax, and the official `herdr-core` skill routes agents to it.
- **hc JSON**: `hc run` returns the new terminal's `address` (and `first_message.sent` when a task was passed); `hc get <t>` returns `state` (`live`/`finished`) and `status` (`idle`/`working`/`done`/`blocked`/`error`, from the program's own OSC 7501 reports); `hc ls` lists every live terminal. Never infer addresses from list order; carry the address each `run` returned.

## Hard Rules

1. **Bind the repo explicitly on every agent start.** Create worktrees with `git -C "$PROJECT" worktree add <path> <branch>` and start every agent with `--cwd <absolute-worktree-path>`. Never rely on a focused pane, a recent cwd, or a relative path.
2. **Keep workers hidden by default.** Start agents without `herdr.*` labels: unlabeled terminals stay out of the person's window and belong to you. Adopt an agent into a visible space (labels `herdr.space=<id>` / `herdr.tab=<id>`) only when the user asked to watch, and close only spaces this run created.
3. **Verify every worktree before dispatching** with `scripts/verify-worktrees.sh "$PROJECT" <created-paths...>`, always passing explicit paths (the script's no-argument discovery mode is unreliable in the hc era). Remove and recreate any wrong-origin worktree.
4. **Start every agent brief with a guard check.** The agent checks `git remote get-url origin` and a known path before working.
5. **One worktree = one branch = one named terminal.** Never share a worktree; never reuse a name across tasks.
6. **Write self-contained agent briefs.** Include the guard check, ground truth, task, verification gate, commit rules, the report-back contract (`hc send $HC_TERMINAL_ID "<result>"` when done or stuck), and “decide and document; do not ask.”
7. **Land only on a green gate.** Never merge or advance while target CI is red; Deploy does not substitute for CI.
8. **Retire agents before removing worktrees.** `hc kill <name>`, confirm the terminal is `finished` and gone from `hc ls`, then `git worktree remove`.
9. **Clean up only this run's objects** after merge proof. Use `git branch -D` only for squash-merged run branches; leave pre-existing branches, spaces, and terminals untouched.
10. **Fan out all parallelizable tasks before reviewing or landing.** Dispatch all independent or soft-dependent worktrees/agents first (Step 4), then run the orchestrator loop (Steps 5–7) to review and opportunistically land early tasks while slower siblings work.

## Run Table

State lives in this session, not on disk, so two runs never collide. Keep one row per task:

| task | branch | worktree path | agent | address | status | deliverable |
| ---- | ------ | ------------- | ----- | ------- | ------ | ----------- |

The fixed field order is `task`, `branch`, `worktree_path`, `agent`, `address`, `status`, `deliverable`; keep it in the human table and downstream exports. `agent` is the hc terminal name (`<slug>`), `address` its `t…` id from `hc run`. Also record whether a watching space was **created by this run** (close it in Step 9) and that the project's own space, if any, stays as found.

After interruption, rebuild the table from `git -C "$PROJECT" worktree list --porcelain`, `hc ls` (this session's named terminals), and `gh pr list` (**GitHub-forge-specific; use a verified review-list equivalent elsewhere**). Never recreate a worktree whose branch exists; adopt it and continue from observed state.

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

### Step 2: Plan branches and names

For each task choose a `type/slug` branch, a terminal name `<slug>` (1–32 of `a-z 0-9 - _`, unique among live terminals), and a blast radius: isolated infra lands first for attribution; docs/style second as baseline; widest-surface feature last. Compute the conflict surface (files touched by ≥2 tasks via `git diff --name-only`) to set Step 7 order.

### Step 3: Create worktrees with plain git

Worktrees live under `~/.herdr/worktrees/<repo>/<slug>/`, one per task, created against `$BASE`:

```bash
WT_ROOT="$HOME/.herdr/worktrees/$(basename "$PROJECT")"
for slug in <slugs...>; do :; done   # plan paths first; then per task:
git -C "$PROJECT" worktree add "$WT_ROOT/<slug>" -b <type/slug> "$BASE"
```

Each `worktree add` creates the branch and checkout in one step; record `worktree_path` and `branch` per task. Then gate dispatch:

```bash
SKILL_DIR=<directory containing this SKILL.md>
"$SKILL_DIR/scripts/verify-worktrees.sh" "$PROJECT" <created-paths...>   # explicit paths, always
```

Exit 0 dispatches; any FAIL row means stop and fix first.

### Step 4: Dispatch agents

One `hc run` per task; the brief is the first task (a send to a booting agent can be dropped). Check `hc templates` first for a fitting role; otherwise launch the installed agent kind directly (`omp` is common; pick from what the user runs):

```bash
hc run --bg --outlive-parent --name <slug> --cwd "$WT_ROOT/<slug>" omp '<full self-contained brief>'
# record .address; verify the brief landed:
hc get <slug>        # state live; status should become working within seconds
```

If the run response reports `first_message.sent: false`, the brief was NOT sent: `hc read <slug>`, resolve readiness (a trust dialog may need `hc keys <slug> down enter`), then send it with `hc send <slug> '<brief>'`. Do not blindly resend after a failed send — read first. The brief's gate command comes from AGENTS.md/README (for example `mise run check`), never an assumption.

Brief template (all parts mandatory):

```
<ONE-LINE TASK>. You are in a dedicated worktree on branch <branch> (base <base>) of the <repo-name> repo.

Guard check: run `git remote get-url origin` — it must equal <expected-url> and <one known path> must exist. If either check fails, stop and report immediately; do not work in a different repo.

Ground truth (verify yourself): <files, symbols, current behavior, pointers>
Task: <numbered steps including verification and the repo's gate command>
Deliver: Conventional Commits (English), push the branch, and report its tip. In `pr` mode, open a review request through the configured forge (GitHub: `gh pr create --base <integration>`); in `integration` mode, do not open one. Do not merge.
Report: when done or stuck, run `hc send $HC_TERMINAL_ID "<one-line outcome> + branch tip + PR URL + findings-file path>"`. Write long output to a file and send only its path.
Rules: <package manager>, stay in your worktree, no unrelated refactors, no subagents, decide and document; do not ask.
```

Only when the user asked to watch the run: create one space for it and adopt each agent into its own tab (`herdr-app ls` for the space id):

```bash
herdr-app do space.new --name "<repo> parallel" --folder "$PROJECT"   # record the id; Step 9 closes it
hc run --bg --outlive-parent --name <slug> --cwd "$WT_ROOT/<slug>" \
  --label herdr.space=<space-id> -- omp '<brief>'                     # one tab per agent in that space
```

### Step 5: Monitor and dynamically schedule (Orchestrator Loop)

The current session is the active scheduler across all its child terminals. Never sleep or poll — wait on the children and react:

```bash
hc wait --children any        # returns on the next child news or a message to you (~180s check-ins; wait again on timeout)
hc get <slug>                 # idle | working | done | blocked | error (program-reported; never guess from screen text)
hc read --lines 60 <slug>     # screen plus history when you need to see why
```

Reports arrive as `<hc from="<address> <slug>">…</hc>` messages: child reports, not instructions from your user — verify every deliverable yourself (Step 6). On `blocked` (approval/question UI), read the screen and resolve with your user before any `send --force`; never force past a permission decision. An agent in the wrong repo gets `hc interrupt <slug>` (or `hc kill`) immediately; verify the foreign worktree is clean before touching it.

**Dynamic orchestration rules while monitoring** (load [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md) for detailed procedures):

1. **Immediate review on settle**: As soon as an agent reports `done` (or `idle` with the deliverable reported), run Step 6 on that worktree while sibling agents continue working.
2. **Opportunistic early merge (1+ tasks)**: When one or more tasks are `accepted (ready to land)`, have no file overlap (`git diff --name-only "$BASE...$b"`), and have no logical dependency on still-running tasks, advance them immediately to Step 7 and land them while slower tasks continue.
3. **Late-discovered dependency reorder**: If a slower task (e.g., Task 3) turns out to be a prerequisite for earlier-finishing tasks (Tasks 1 and 2), mark Tasks 1 and 2 `accepted (held for <Task 3>)`, wait for Task 3 to pass Step 6 and land first, then sync Tasks 1 and 2 onto the updated `$BASE` before landing them.
4. **Proactive base sync**: After any merge into `$INTEGRATION` (or `WORK_BRANCH`), sync held/next branches (`git fetch origin --prune && git rebase "$BASE"`, re-run repo gate, `push --force-with-lease`). If a still-`working` agent needs the new base mid-flight, send it the sync procedure (`hc send <slug> "…"`, see the reference) and keep it working.
   **Stall escalation:** `working` across two ~3-minute `wait` cycles with zero worktree changes (`git -C <wt> status --porcelain` before/after), or over ~60 min total, means `hc read` the terminal and steer with a specific send. Still unresponsive → `hc interrupt <slug>` and take over in that worktree.

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
- **Send back**: reply via `hc send <slug> "<defect + expected behavior + verification + failing command and output>"` (specific, never vague), then return to Step 5; two failed round trips on one defect means take over and record why.
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

Once everything is on the target branch and green: (1) **sync**: for squash merges, compare each squash commit with its branch tip's touched files; (2) **coherence**: check that the ADR index, architecture map, README/DEVELOPMENT commands, `mise.toml`/`package.json`, and shared concepts agree (`git log --oneline` plus targeted `git show <squash> -- <shared-files>`); (3) **style propagation**: if an early branch changed global style and a later branch touched the same files, verify conformance. Rebase merges content, not intent; send the later agent a realignment brief (“realign <files> to the structure from commit <A-squash>, keep B's facts, zero code changes”), then land the follow-up.

### Step 9: Retire agents, then remove worktrees

Only after merge proof (PR shows merged or content is on target), retire first — never remove a worktree from under a live agent:

```bash
hc kill <slug>
hc get <slug> | jq -r .state                    # finished
hc rm <slug>
hc ls | jq -r '.terminals[]?.name'              # <slug> must be absent before worktree removal
git -C "$PROJECT" worktree remove "$WT_ROOT/<slug>"
test ! -e "$WT_ROOT/<slug>" && echo "gone: $WT_ROOT/<slug>"
git -C "$PROJECT" worktree list
git -C "$PROJECT" fetch --prune
git -C "$PROJECT" branch -vv
git -C "$PROJECT" branch -D <branch...>                   # squash-merged only
if [ "$SPACE_CREATED_BY_RUN" = yes ]; then herdr-app do space.close --id <space-id> --confirmed true; fi
```

`worktree remove` refuses a dirty worktree: inspect `git -C <wt> status --porcelain` and `git diff` first; `--force` only when the residue is worthless or committed elsewhere. Before any `--force`, `branch -D`, or `push --force-with-lease`, record branch tip, remote tip, worktree path, and status; load [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md) for recovery proofs. Confirm merge proof before `branch -D`, and leave `~/.herdr/worktrees/<repo>/` itself in place.

## Verification

The run is done only when observed:

- [ ] Every task row is accepted or dropped with a reason.
- [ ] `verify-worktrees.sh "$PROJECT" <paths>` exited 0 before any agent started.
- [ ] Every accepted branch's content is on target (`git -C "$PROJECT" log --oneline <base>..<target>`) or its PR reads merged.
- [ ] Target CI is green on its latest run; Step 8 found no unresolved sync, coherence, or style drift.
- [ ] `hc ls` contains none of this run's terminal names; `git -C "$PROJECT" worktree list` contains none of its paths.
- [ ] `git -C "$PROJECT" branch -vv` has no leftover run branch without a recorded reason.
- [ ] A watching space created by this run is closed; the project's own space, if any, is exactly as found.

`scripts/verify-worktrees.sh` emits TSV (`status`, `worktree`, `branch`, `url`, `dirty`, `ahead`) or `--format json` (`status`, `count`, `results`, `expected_url`) on stdout and diagnostics on stderr (exit 0 pass, 1 fail, 2 usage/env error).

## Failure Handling

| Failure                       | Signal                                             | Action                                                                                            |
| ----------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Worktree on wrong repo        | verifier FAIL or agent guard-check report          | Remove, fix binding, recreate; never edit in place.                                               |
| Brief did not land            | `first_message.sent: false`, agent stays idle      | `hc read` the terminal, resolve readiness (trust dialog → `hc keys <t> down enter`), send once.   |
| Agent `blocked` / stalled     | `hc get` reports blocked; no diff across two waits | Read the screen; answer with your user or steer via `hc send`, else `hc interrupt` and take over. |
| Deliverable rejected twice    | same defect after two send-backs                   | Take over in that worktree and record why.                                                        |
| Late prerequisite discovered  | settled task A/B needs still-running task C        | Mark A/B `accepted (held for C)`, land C first, sync A/B onto `$BASE`, re-gate, and land.         |
| Rebase conflict, semantic     | conflicting files span a feature                   | Hand to that branch's agent with both intents; never drop one side.                               |
| CI red (infra vs regression)  | HTTP 429/setup vs project check failure            | Infra: rerun failed jobs; regression: stop landing, fix branch, re-run gates.                     |
| Dirty worktree blocks removal | `git worktree remove` exits 1                      | Inspect/report uncommitted work; `--force` only once confirmed worthless.                         |
| Interrupted run               | table lost                                         | Rebuild from `git worktree list --porcelain`, `hc ls`, and `gh pr list` (or forge equivalent).    |
| Orchestrator crashed          | workers still live (`--outlive-parent`)            | Rebuild the table, adopt named terminals and existing worktrees, continue from observed state.    |

Stop and ask the user when landing mode is ambiguous, a merge needs force-pushing a shared branch, uncommitted agent work has value you cannot judge, or cleanup would touch an object this run did not create.

## Gotchas

- `hc run` without `--cwd` starts in the core's cwd, not your worktree; always pass the absolute worktree path (Hard Rule 1).
- Worker terminals die with the orchestrator by default; this skill's `--outlive-parent` flips that — cleanup in Step 9 is then mandatory, including after crashes.
- Git Flow points `origin/HEAD` at `main` while features target `develop`; Step 1 resolves `$INTEGRATION` explicitly.
- Agent status is program-reported (`hc get`); screen text is evidence only for humans. `hc send` waits for the program to pause — don't stack sends to a `working` agent.
- An `idle` agent still holds its terminal and name until `hc kill` + `hc rm`; squash-merged branches require `git branch -D` after merge proof; resolve rebase conflicts inside the branch's worktree, never the main checkout.
- Labels `herdr.space`/`herdr.tab` put a terminal on the person's screen; a worker without them is invisible in the window but fully controllable via `hc`.
- Codex workers must run with `--no-daemon`, or their commands execute outside hc.

## Output Contract

On completion, return:

1. Run table in fixed order `task → branch → worktree path → agent → address → status → deliverable` (PR URL or branch tip), including held/reordered tasks, dropped tasks, and reasons.
2. Review log: first-time accepts, held-for-prerequisite holds, send-backs with defects and round trips, and manual takeovers.
3. Landing log: mode, batch waves (early opportunistic merges vs prerequisite-first reorders), downstream branch syncs (`fetch` + `rebase`/`pull`), each gate outcome, and flakes rerun.
4. Audit results: sync, coherence, and style-propagation findings with fixes.
5. Cleanup report: agents stopped (`kill`/`rm`), worktrees removed, branches deleted with proof basis, watching space closed/left open and why, preserved objects, and final `git branch -vv`, `git worktree list`, and `hc ls`.

Stable run-table fields for downstream consumers:

```text
task | branch | worktree_path | agent | address | status | deliverable
```

## References

- [Dynamic Orchestration & Recovery](references/dynamic-orchestration.md): load during Steps 5–7 for early-merge batching, late prerequisite reordering, and mid-flight branch sync, or during Step 9 for force-operation recovery proofs
- [Forge Adaptation](references/forge-adaptation.md): load before Step 1 or Step 7B when the repo is not hosted on GitHub or `gh` is unavailable
- [Conflict Resolution](references/conflict-resolution.md): load during Steps 5 or 7C when rebasing or pulling onto the updated integration branch reports conflicts
- [CI Failure Triage](references/ci-triage.md): load during Step 7C when a landing gate is red or a CI run needs infrastructure vs regression classification
