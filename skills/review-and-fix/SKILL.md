---
name: review-and-fix
description: >
  Reviews git diff changes with senior-engineer judgment: investigates context,
  adapts rigor to change type, weighs downstream impact, and guides user-approved
  fixes. Use when reviewing code changes and deciding whether to fix issues.
license: MIT
compatibility: Requires git, file read/write access, and LSP/linter tooling for best results.
metadata:
  author: fang2hou
  version: "2.1"
---

# Review and Fix

Review code changes as a senior engineer and architect would: investigate context first, think deeply about trade-offs, then organize findings for user action. Not a checklist robot — a thinking reviewer who adapts rigor to the situation.

## When to Use

- User asks to review their code changes or git diff
- User wants to review and fix issues in their code
- User asks to check the diff for problems
- User wants a thorough code review before committing
- User says "review and fix", "check my changes", or "fix the issues"
- Trigger phrases include: "review my changes", "review and fix", "check the diff", "code review", "fix the issues", and "/review-and-fix".

## When NOT to Use

- Full codebase auditing (use a broader code review tool)
- Security auditing specifically (use a dedicated security skill)
- Performance profiling (different domain)
- Generating tests (separate workflow)

## Inputs

| Input          | Required | Format             | Example                               |
| -------------- | -------- | ------------------ | ------------------------------------- |
| `$ARGUMENTS`   | No       | File paths or refs | `src/auth.rs`, `HEAD~3`, `main..HEAD` |
| Git diff scope | No       | Ref or path        | Defaults to staged + unstaged changes |

**Scope resolution**: If `$ARGUMENTS` provides paths, review only those files. If it provides git refs, diff those refs. Otherwise, review all uncommitted changes (staged + unstaged).

## Hard Rules

1. **Investigate before judging**: Never flag an issue without understanding WHY the code looks like that. History, constraints, and intent matter.
2. **Adapt rigor to context**: A hotfix in production gets different review than a new library API. Adjust your standards accordingly.
3. **No silent fixes**: Every fix must be presented to the user for approval before applying.
4. **Preserve intent**: Never change what the code does. Only fix HOW it does it.
5. **Evidence-based**: Every issue must cite a specific line, rule, or diagnostic — not a vague feeling.
6. **No suppression shortcuts**: Never suggest `as any`, `@ts-ignore`, `@ts-expect-error`, `unwrap()` to silence, or equivalent suppression mechanisms.

## Core Principle: Context Determines Rigor

**This is the single most important concept in this skill.** A senior engineer does not apply the same standards to every change. Before reviewing a single line of code, you must understand the NATURE of the change — because that determines which issues matter and which are noise.

| Change Type            | Review Focus                                                            | What to Deprioritize                 |
| ---------------------- | ----------------------------------------------------------------------- | ------------------------------------ |
| Hotfix / minimal patch | Correctness, no regressions, blast radius                               | Style, naming, refactoring           |
| Library / SDK code     | API stability, breaking changes, downstream panic risk, backward compat | Internal style, non-critical perf    |
| New feature            | Architecture, correctness, error handling, API design                   | Minor naming, premature optimization |
| Refactor               | Behavioral equivalence, no regressions                                  | New features, scope creep            |
| Config / infra         | Correct values, security, environment parity                            | Code style                           |

**If you cannot determine the change type, default to "new feature" rigor.** When in doubt, review MORE, not less.

## Workflow

### Phase 1: Investigate — Understand Before Judging

The goal of this phase is to build a complete mental model. Do NOT review code yet. Only observe and understand.

#### Step 1: Read the Git Diff

1. Run `git diff` (or `git diff <ref>`, or `git diff --staged`, or `git diff HEAD`) to get the full diff
2. Parse each changed file: added lines, removed lines, modified regions
3. **Classify the change type** using the table above (hotfix, library, new feature, refactor, config)
4. Build a mental model: what is the author trying to accomplish?

**Output**: Change summary per file (type, intent, scope).

#### Step 2: Gather External Context

If external context sources exist, use them to sharpen your understanding.

1. Check for linked tickets (Jira, GitHub issues) in commit messages or branch names
2. Look for design documents: `docs/`, `designs/`, `*.md` files mentioning the feature
3. Check Confluence pages if accessible (use MCP tools)
4. Read `AGENTS.md`, `CONTRIBUTING.md`, or project-level documentation for conventions

**Exit when** each listed source has been checked once, or no external context exists; record missing context and move on. Do not broaden the search beyond the change's documented scope.

#### Step 3: Run Automated Diagnostics

Observe the environment, then run what's available. **Do NOT assume any tool exists.**

1. **LSP diagnostics**: Try `lsp_diagnostics` on each changed file. If no LSP server is configured for that file type, skip silently.
2. **Linter discovery**: Observe project files and dependencies to find what it uses. Scan the declarations relevant to the changed language:
   - JavaScript/TypeScript: `package.json`, ESLint/Prettier config, `tsconfig`
   - Python: `pyproject.toml`, `setup.cfg`, `tox.ini`, `noxfile.py`
   - Rust/Go: `Cargo.toml`, `go.mod`, and `Makefile` or task-runner configs
     Verify each project-declared command is installed before running it. If nothing is found, skip.
3. **Build / type-check**: If discovered from observation, run it. If none found, skip.

**Key principle**: Every tool is optional. Missing tools are not errors — they're notes in the report. Record each attempted or skipped diagnostic and its reason.

#### Step 4: Historical and Codebase Context

For each changed file, understand its role in the larger system.

1. `git log --oneline -20 <file>` — how mature is this file?
2. `git blame` on changed regions — who wrote what, when, and why might they have done it that way?
3. **For high-churn files (50+ commits)**: review more carefully — this code has been around, changes here have history and reasons
4. **For library/SDK files**: investigate downstream consumers — will this change cause panics, breaking changes, or behavioral shifts for callers?
5. **For new files**: check if similar files exist — match established patterns
6. **When to research externally**: If the change involves an unfamiliar library, framework pattern, or domain concept, **search for documentation and real-world usage before forming opinions**. Use librarian agents or web search. A reviewer who doesn't understand the domain gives bad feedback.

**Research exit criterion**: For each unfamiliar library, framework pattern, or domain concept, stop when you have authoritative documentation or a real-world example that explains the relevant behavior and how it applies here. After two targeted searches without authoritative evidence, record the uncertainty and proceed conservatively; do not keep searching indefinitely.

**Investigation exit criteria**: End Phase 1 after every changed file has a change summary, relevant external and historical context has been checked, available diagnostics are recorded, and each unfamiliar concept is resolved with evidence or documented as uncertain. Do not continue investigating once these conditions are met.

### Phase 2: Think — Apply Judgment

Now that you have full context, think like a senior engineer. For detailed review dimensions, read [references/review-criteria.md](references/review-criteria.md).

#### Step 5: Deep Review

Review each changed region with the rigor appropriate to its change type (see table above).

**Universal checks** (apply to ALL change types):

1. **Correctness**: Logic errors, off-by-one, wrong conditions, missing edge cases
2. **Error handling**: Swallowed errors, missing propagation, empty catches
3. **Security**: Injection, hardcoded secrets, missing validation — only if the change touches trust boundaries

**Context-dependent checks** (apply based on change type):

| Dimension          | Hotfix | Library | New Feature | Refactor |
| ------------------ | :----: | :-----: | :---------: | :------: |
| Type safety        |   ○    |   ●●●   |     ●●      |    ●●    |
| API design         |   —    |   ●●●   |     ●●      |    ●     |
| Naming             |   —    |    ●    |     ●●      |    ○     |
| Complexity         |   ○    |    ●    |     ●●      |    ●●    |
| Performance        |   —    |    ○    |      ●      |    ○     |
| Concurrency safety |   ●    |   ●●●   |     ●●      |    ●●    |
| Downstream impact  |   ●●   |   ●●●   |      ●      |    ●●    |

**Legend**: ●●● = critical, ●● = important, ● = nice-to-have, ○ = only if obvious, — = skip

**For each issue found, record**:

- File, line(s)
- Category
- Severity: `critical` / `warning` / `suggestion`
- **Why it matters in THIS context** (not just "best practice says so")
- The specific risk or consequence if left unfixed

**When to search for more context during review**:

- You see an unfamiliar library function → search its docs before flagging usage as wrong
- The pattern looks odd but might be intentional → check git history for why it exists
- The change affects a public API → search for downstream consumers before suggesting breaking changes
- You're unsure about a language idiom → look it up, don't guess

**Search exit**: Stop a context search when you have evidence sufficient to explain the behavior and its consequence for this change. If two targeted searches yield no reliable answer, record the uncertainty and do not flag the behavior as wrong solely on assumption.

#### Step 6: Synthesize Findings

Think about findings as a WHOLE, not as isolated items.

1. Merge issues from automated diagnostics (Step 3) and manual review (Step 5)
2. Deduplicate overlapping findings
3. **Evaluate fix cost vs. benefit for each issue** — a senior engineer doesn't fix everything:
   - High benefit + low cost → recommend
   - High benefit + high cost → recommend, but flag scope
   - Low benefit + any cost → mention as optional, don't push
   - Issue exists but the change is a hotfix → note it, don't block the fix
4. **Think about cascading impact**: Will fixing issue A break B? Are there related issues that should be fixed together?
5. **Consider the library stability dimension**: If the change is in library/SDK code, any fix must preserve backward compatibility and not introduce panics for downstream consumers

### Phase 3: Organize — Present to User

#### Step 7: Present Findings and Interactive Fix Selection

Present a structured report that shows your thinking, not just a flat list.

1. **Context summary**: What you reviewed, what change type you identified, what tools you ran
2. **Findings table** with severity, description, and **why it matters in this context**:

```
┌────┬──────────┬───────────────────────────────────────────┬──────────────────┐
│ #  │ Severity │ Issue                                     │ Why It Matters    │
├────┼──────────┼───────────────────────────────────────────┼──────────────────┤
│ 1  │ critical │ unwrap() on user input can panic          │ Library API —    │
│    │          │                                           │ downstream crash │
│ 2  │ warning  │ Missing error context in fetch            │ Debugging cost   │
│ 3  │ suggest  │ Magic number 404 in handler              │ Low priority     │
└────┴──────────┴───────────────────────────────────────────┴──────────────────┘
```

3. **Ask the user** which fixes to apply. Default: apply all. User can opt out of specific fixes.

#### Step 8: Fix Planning

For each approved fix, plan with maximum effort.

1. Create a detailed plan per fix: what to change, why, before/after, risk, dependencies
2. Order fixes by dependency
3. Flag risky fixes that need extra verification
4. **Present the plan for final confirmation**

For common fix patterns and before/after examples, read [references/fix-patterns.md](references/fix-patterns.md). Use these as reference, not prescription — adapt to the project's actual patterns.

### Phase 4: Execute — Apply with Maximum Effort

#### Step 9: Execute Fixes

**The executing agent MUST use its deepest thinking mode and maximum programming effort.** This is not the time for quick edits — every fix should be crafted with care.

For each approved fix, run this validation loop before proceeding to the next fix:

1. Apply one fix in dependency order.
2. Re-run all available diagnostics on the modified file.
3. If diagnostics are clean, continue to the next approved fix.
4. If diagnostics report a new failure:
   - Stop and identify whether it is caused by the fix.
   - If a follow-up fix is needed and is not covered by the user's approval, present it to the user and obtain approval before applying it.
   - Apply the approved follow-up, then return to step 2.
5. Repeat steps 2–4 until diagnostics for the current fix are clean. Only then proceed.
6. If a fix causes cascading errors: STOP, revert, re-assess, adjust approach. If the cascade exceeds 5 files, stop and re-plan with the user.
7. Never leave a file in a broken state between fixes.
8. **Match the project's existing conventions** — if you don't know the convention, read similar files first.
9. If formatting tools are available, run them on modified files.

#### Step 10: Post-Fix Review

Maximum effort verification.

1. Enter this gate only after every approved fix has passed the Step 9 validation loop.
2. Re-run all available diagnostics on ALL changed files.
3. If any diagnostic fails:
   - Stop before generating the report and identify whether the failure is caused by an approved fix.
   - Present any unapproved follow-up fix to the user and obtain approval before applying it.
   - After approval, return to the Step 9 validation loop, then restart this gate.
4. Repeat steps 2–3 until all available diagnostics are clean. This is the gate's diagnostic exit criterion.
5. Run the build if available and run tests if available (unless told not to).
6. If a build or test failure needs a fix, present it to the user for approval, return to Step 9, and restart this gate after the approved fix passes validation.
7. Re-read `git diff` to review final state.
8. Verify every approved fix was applied correctly.
9. Check for unintended side effects.
10. Generate the final report only after all available diagnostics are clean and available build/tests pass or are explicitly unavailable or exempted.

## Gotchas

- **Staged vs unstaged**: `git diff` shows unstaged only. `git diff --staged` shows staged. Use `git diff HEAD` for everything. Missing staged changes = incomplete review.
- **Fix cascading**: A "simple" type fix can cascade into 20 files. If cascade exceeds 5 files, stop and re-plan with the user.
- **Generated files**: Skip review of autogenerated files (look for `// Code generated by`, `@generated` headers).
- **Hotfix review**: When reviewing a hotfix, resist the urge to refactor. The goal is correct + minimal, not beautiful.
- **Library changes**: A cosmetic fix in a library can break downstream consumers. Always consider: "could this change cause a panic or behavioral change for someone using this API?"
- **Unfamiliar patterns**: If something looks wrong but you're not sure, RESEARCH before flagging. It might be an established pattern you don't know. Ignorance disguised as feedback is worse than no feedback.

## Output Contract

Keep the human-readable report primary. On completion, return these sections in order:

1. **Context summary**: Change type, tools used, and scope reviewed
2. **Findings**: Each finding includes severity (`critical` / `warning` / `suggestion`), evidence (file/line, rule, or diagnostic), the issue, and why it matters here
3. **Diagnostics before/after**: Comparison of diagnostic results, including the final pass/fail table for each verification check
4. **Fixes applied**: Approved fixes that were applied and their validation results
5. **Fixes skipped with reason**: What the user chose not to fix and why
6. **Issues discovered but out of scope**: New issues found during post-fix review that were not part of the approved work

For downstream consumers, preserve this stable field order (a field contract, not a requirement to emit JSON):

```text
context_summary
findings[]: severity, evidence, issue, rationale
diagnostics_before_after
fixes_applied
fixes_skipped_with_reason
issues_discovered_out_of_scope
```

## References

- [Review Criteria](references/review-criteria.md) — Review dimensions with context-dependent weighting, loaded during Phase 2
- [Fix Patterns](references/fix-patterns.md) — Fix principles and illustrative examples, loaded during Phase 3-4
