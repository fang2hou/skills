# Conflict Resolution

Load this reference when Step 7 rebases a branch and Git reports conflicts. Keep
all conflict work in the worktree of the branch being rebased; never resolve it
in the main checkout.

## Mechanical conflicts

Imports, ordering, and adjacent edits are mechanical when both changes can be
represented without changing either task's intended behavior.

1. Inspect the conflicted files and both branch intents.
2. Combine both intents in the rebasing worktree; do not choose a side merely to
   make the conflict disappear.
3. Run the repository's declared gate command in that worktree.
4. Inspect `git diff --check` and `git status --porcelain`, then continue the
   rebase only after the gate is green.
5. Record the conflict, resolution, and gate result in the landing log.

## Semantic conflicts

A conflict spanning a feature, contract, migration, or file-wide structure is
semantic. Do not hand-resolve it from the conflict markers. Paste the
conflicted file paths, both task intents, and the rebase context into an
`agent prompt` to that branch's own idle agent. The agent must resolve and
re-verify in its worktree, then report the resulting commit and gate output.

If one side must win, make that a reported decision with the reason. Never
resolve a conflict by silently dropping one side, and do not continue the
landing sequence until the owning branch is accepted again.

## Success signal

A conflict is resolved only when the rebase exits successfully, the worktree is
clean, the branch still contains its intended commits, and the repository gate
passes. If any check fails, keep the branch in place, send it back with the
observed output, and rebuild the landing plan from the observed state.
