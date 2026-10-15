---
name: github-repo-baseline
description: >
  Applies the standard GitHub repository baseline via the gh CLI: squash-only merges,
  immutable releases, auto-deleted PR branches, and a Protect Default Branch ruleset.
  Use for standard GitHub settings, branch protection, or initializing a repository.
license: MIT
compatibility: Requires `gh` CLI authenticated with admin access to the target repository.
metadata:
  author: fang2hou
  version: "1.1"
---

# GitHub Repo Baseline

Configure any GitHub repository to the standard baseline (squash-only linear history
via PRs, auto-cleaned branches, and immutable releases) in one idempotent pass using `gh`.

## When to Use

- A new repository was just created and needs the standard settings.
- The user asks to "apply standard GitHub settings", "set up branch protection", or
  "make this repo squash merge only".
- Auditing a repo and fixing drift from the baseline.

## When NOT to Use

- Organization-level policy rollout (this skill is per-repository only).
- Repositories the user does not admin (all three steps require admin access).
- Forks of active upstreams: merge settings apply, but the baseline's protection
  model targets repos the user owns.

## Inputs

| Input             | Required                    | Format                     | Example                               |
| ----------------- | --------------------------- | -------------------------- | ------------------------------------- |
| Repository        | No (defaults to cwd's repo) | `owner/name` or gh repo ID | `fang2hou/dotfiles`                   |
| Skip immutability | No                          | flag                       | user opts out of release immutability |

## Hard Rules

1. Never enable release immutability silently; it has irreversible effects (see
   Gotchas). State it explicitly before applying and let the user opt out.
2. Never set `required_approving_review_count` above 0. The baseline targets personal
   projects; team projects need explicit user instruction.
3. Change nothing before the user confirms the planned changes (Step 2). The writes
   alter a shared remote repository, and an audit-only request stops at the plan.
4. All three layers must be verified after applying (Step 6). A 2xx response alone is
   not a verified result.
5. Use the REST API via `gh api`, not the GitHub web UI, so every change is scripted,
   repeatable, and verifiable.

## Baseline Definition

Three layers, all required:

| Layer      | Setting                   | Value                                                                                  |
| ---------- | ------------------------- | -------------------------------------------------------------------------------------- |
| Repo merge | Allowed merge methods     | squash only (`allow_merge_commit`/`allow_rebase_merge`/`allow_auto_merge` all `false`) |
| Repo merge | Squash default message    | title = `PR_TITLE`, body = `COMMIT_MESSAGES` ("Title and Detail")                      |
| Repo PR    | Suggest updating branches | `allow_update_branch: true`                                                            |
| Repo PR    | Auto-delete head branch   | `delete_branch_on_merge: true`                                                         |
| Release    | Immutable releases        | enabled                                                                                |
| Ruleset    | Target                    | default branch (`~DEFAULT_BRANCH`), enforcement `active`                               |
| Ruleset    | Rules                     | `deletion`, `non_fast_forward`, `required_linear_history`, `pull_request`              |
| Ruleset    | pull_request params       | `allowed_merge_methods: ["squash"]`, approving reviews `0`                             |

## Workflow

Set `REPO` first: use the repository the user named, otherwise resolve it from the cwd:

```bash
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)   # or REPO=owner/name from the user
```

### Step 1: Confirm admin access

```bash
gh api /repos/$REPO --jq '{repo: .full_name, admin: .permissions.admin, fork: .fork}'
```

- `admin: false` → stop; report that admin access is required.
- `fork: true` → warn the user that upstream settings may conflict before continuing.

### Step 2: Show the plan and confirm

Read the current state with the Step 6 commands. Run the Step 4 lookup first; when it
returns empty, skip the by-id ruleset read and record the ruleset as missing. A missing
ruleset or `enabled: false` is simply a row to change.
Show one table, `Setting | Current | Baseline`, covering every Baseline Definition row,
and state the release-immutability warning from Gotchas. Ask for one confirmation
that also offers the immutability opt-out.

- Every row already matches → report "already at baseline" and stop.
- The user asked only to audit or check drift → stop after the table.
- The user confirms → continue with Step 3; skip Step 5 if they opted out.

### Step 3: Repo merge and PR settings

```bash
gh api --method PATCH /repos/$REPO --input - <<'EOF'
{
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "allow_auto_merge": false,
  "squash_merge_commit_title": "PR_TITLE",
  "squash_merge_commit_message": "COMMIT_MESSAGES",
  "allow_update_branch": true,
  "delete_branch_on_merge": true
}
EOF
```

### Step 4: Ruleset "Protect Default Branch"

Idempotent: look up an existing ruleset by name, PUT to update it, POST to create.

```bash
RULESET_ID=$(gh api /repos/$REPO/rulesets --jq '[.[] | select(.name == "Protect Default Branch") | .id][0]')
```

`gh` prints an empty string when no ruleset matches. When `RULESET_ID` is empty,
create the ruleset and capture its id from the response, because Step 6 reads it:

```bash
RULESET_ID=$(gh api --method POST /repos/$REPO/rulesets --jq .id --input - <<'EOF'
{
  "name": "Protect Default Branch",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "allowed_merge_methods": ["squash"],
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "required_reviewers": []
      }
    }
  ]
}
EOF
)
```

If `RULESET_ID` is non-empty, send the identical body with
`gh api --method PUT /repos/$REPO/rulesets/$RULESET_ID --input -` instead
(PUT replaces the full ruleset and keeps the id).

### Step 5: Release immutability

Skip this step if the user opted out in Step 2.

```bash
gh api --method PUT /repos/$REPO/immutable-releases
```

Returns `204` with no body on success. This endpoint has no request body.

### Step 6: Verify

```bash
gh api /repos/$REPO --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge, auto: .allow_auto_merge, title: .squash_merge_commit_title, body: .squash_merge_commit_message, update_branch: .allow_update_branch, delete_head: .delete_branch_on_merge}'
gh api /repos/$REPO/rulesets/$RULESET_ID --jq '{enforcement, rules: [.rules[].type], merge_methods: (.rules[] | select(.type == "pull_request") | .parameters.allowed_merge_methods)}'
gh api /repos/$REPO/immutable-releases   # {"enabled":true,...}
```

Every value must match the Baseline Definition table (immutability may be `false`
only when the user opted out). Report any mismatch. Read rule details from the by-id
endpoint; the list endpoint omits them (see Gotchas).

## Gotchas

- **Release immutability is effectively one-way.** Tags published while it is enabled
  can never be reused, not even after disabling the setting. Deleting a release
  still burns its tag name forever.
- **Immutable releases break naive release CI.** Assets cannot be attached after
  publishing. CI must create a draft release, upload assets, then publish.
- **Merge methods are enforced at two layers.** Repo settings hide the other merge
  buttons; the ruleset's `pull_request` rule blocks them at the branch level. Both are
  needed because repo settings alone still allow direct pushes to bypass PR review.
- **`deletion` and `delete_branch_on_merge` are unrelated.** The first protects the
  default branch from deletion; the second cleans up PR head branches after merge.
- **Ruleset creation is not idempotent.** A bare POST with the same name creates a
  duplicate, so always check by name first (Step 3).
- **The ruleset list endpoint returns summaries only.** `GET /repos/{repo}/rulesets`
  omits the `rules` array; filtering it with `[.rules[].type]` fails with
  "cannot iterate over: null". Use `GET /repos/{repo}/rulesets/{id}` for details.
- **Fine-grained PATs** need "Administration: write" (rulesets, repo settings) and
  "Metadata: read" on the target repo; classic `repo` scope already covers it.
- **Emergency hotfixes** under this baseline require an admin bypass entry in the
  ruleset or temporarily setting `enforcement: "disabled"`. Do not add bypass actors
  unless the user asks.

## Output Contract

On completion, return a verification table:

| Setting | Expected | Actual | Status |
| ------- | -------- | ------ | ------ |

…one row per Baseline Definition entry, plus a line for the ruleset (enforcement +
rule list) and immutable releases (`enabled: true`). Flag every mismatch as a
follow-up action.
