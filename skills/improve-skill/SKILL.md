---
name: improve-skill
description: Audits and improves Agent Skills for spec compliance and clarity. Scores 8 dimensions, drafts an approval-gated plan, and applies changes with self-correction gates. Use when creating, reviewing, or upgrading skills.
license: MIT
compatibility: Requires file read/write access to modify skills. Works with any agent supporting the Agent Skills standard.
metadata:
  author: fang2hou
  version: "1.2"
  sources: "Agent Skills specification; industry best practices"
---

# Improve Skill

Analyze, score, and optimize Agent Skills to production quality. Applies a unified 8-dimension quality framework with self-correcting execution gates.

## When to Use

- Creating a new skill and want quality assurance from the start
- Reviewing an existing skill for improvement opportunities
- Upgrading a skill to meet the Agent Skills specification
- Refactoring a bloated, unclear, or underperforming skill
- Auditing quality across a skill collection

## When NOT to Use

- Tasks that are not about writing, reviewing, or updating Agent Skills
- General code refactors unrelated to skills (use a code-focused refactoring skill instead)
- Situations where you cannot read the target skill files (this workflow is evidence-based)

## Inputs

| Input               | Required | Format                       | Examples                                |
| ------------------- | -------- | ---------------------------- | --------------------------------------- |
| Invocation argument | No       | Skill path or directory      | `agents/skills/my-skill`, `./my-skill/` |
| Invocation argument | No       | Skill name (resolver needed) | `my-skill`                              |

**Cross-platform note**: Clients that expose an invocation argument (for example a `$ARGUMENTS` placeholder) pass the target through it. If no such argument is available or it does not resolve to a skill directory, ask the user for the target skill path.

## Hard Rules

1. **Preserve intent**: Never alter a skill's core purpose. Optimization improves HOW, not WHAT.
2. **User approval required**: Present the optimization plan and get explicit approval before modifying files.
3. **Spec compliance**: All output must conform to the Agent Skills specification.
4. **No data loss**: Never delete content without relocating it (to references/ or restructuring).
5. **Measurable improvement**: Every optimization must improve at least one quality dimension score.
6. **Gate discipline**: Do not proceed past a gate until all its conditions are met.
7. **Context-cost discipline**: Do not increase context cost without a corresponding capability gain; removing content the agent already knows is an improvement.

## Workflow

### Phase 0: Target Acquisition

1. If an invocation argument specifies a skill path or name, locate it
2. If currently inside a skill directory, use the current directory
3. Otherwise, ask which skill to optimize
4. Read `SKILL.md` completely
5. Inventory all supporting files (references/, scripts/, assets/)
6. Read key supporting files to understand full scope
7. Before editing, copy the skill directory to a separate baseline snapshot for the later trial run

**Gate 0** — Proceed only when ALL true:

- [ ] Target skill directory identified
- [ ] SKILL.md read completely
- [ ] Supporting file inventory complete
- [ ] Pre-improvement baseline snapshot created

_If gate fails_: Ask user for the skill path or name. Do not guess.

### Phase 1: Intent & Rules Extraction

Crystallize what must NOT change; use Pattern 8 (Intent Card) in [references/exemplar-patterns.md](references/exemplar-patterns.md) for rationale.

1. **Core intent** — What problem does this skill solve? Who is the audience?
2. **Mandatory rules** — What constraints MUST be preserved? (Hard rules, safety, compliance)
3. **Check gates** — What verification points exist? Where should they exist?
4. **Domain type** — Is this a workflow, expertise/reference, or hybrid?
5. **Platform dependencies** — What relies on specific agent capabilities?
6. **Terminology set** — Which terms name recurring concepts, and what single term should be used for each?
7. **Script inventory** — Does the skill ship `scripts/`? If yes, record each script's interface and safety/portability assumptions.

Document this as an Intent Card:

```
Intent: [one sentence]
Domain: [workflow | expertise | hybrid]
Mandatory Rules: [list]
Existing Gates: [list or "none"]
Platform Dependencies: [list or "none"]
Terminology Set: [canonical term → meaning; list or "none"]
Ships Scripts: [yes — list scripts and interfaces | no]
```

**Gate 1** — Proceed only when ALL true:

- [ ] Intent card completed
- [ ] Mandatory rules identified and flagged as untouchable
- [ ] Domain type classified
- [ ] Terminology set and script inventory captured

_If gate fails_: Re-read SKILL.md focusing on purpose statements and constraint sections.

### Phase 2: Quality Audit

Score the skill across 8 dimensions (1-5 each, max 40). Load [references/scoring-rubric.md](references/scoring-rubric.md) for detailed criteria and evidence guidance.

When a trial run is feasible, use [references/trial-run.md](references/trial-run.md) and grade objective assertions against improved and baseline runs; otherwise mark the scorecard static-evidence-only.

| #   | Dimension                         | What to Assess                                                          |
| --- | --------------------------------- | ----------------------------------------------------------------------- |
| 1   | Spec Compliance                   | Frontmatter fields, naming rules, directory structure                   |
| 2   | Description Quality               | Specificity, keywords, length, WHAT + WHEN coverage                     |
| 3   | Context Economy & Disclosure      | Agent-known content omitted, scoped references, one-level navigation    |
| 4   | Structural Clarity                | Section organization, logical flow, navigability                        |
| 5   | Instruction Quality & Calibration | Fragility-matched specificity, WHY, defaults, procedures, patterns      |
| 6   | Guardrails & Validation           | Validation loops, plan gates, safety, robust scripts when shipped       |
| 7   | Composability & Script I/O        | Structured output, stderr diagnostics, exit codes, retry-safe runs      |
| 8   | Cross-Platform Compatibility      | Portable instructions, paths, optional metadata, no runtime assumptions |

Present as a scorecard:

```
┌───┬───────────────────────────────────┬───────┬──────────────────────────────┐
│ # │ Dimension                         │ Score │ Key Finding                  │
├───┼───────────────────────────────────┼───────┼──────────────────────────────┤
│ 1 │ Spec Compliance                   │  ?/5  │ ...                          │
│ 2 │ Description Quality               │  ?/5  │ ...                          │
│ 3 │ Context Economy & Disclosure      │  ?/5  │ ...                          │
│ 4 │ Structural Clarity                │  ?/5  │ ...                          │
│ 5 │ Instruction Quality & Calibration │  ?/5  │ ...                          │
│ 6 │ Guardrails & Validation           │  ?/5  │ ...                          │
│ 7 │ Composability & Script I/O        │  ?/5  │ ...                          │
│ 8 │ Cross-Platform Compatibility      │  ?/5  │ ...                          │
├───┼───────────────────────────────────┼───────┼──────────────────────────────┤
│   │ TOTAL                             │ ??/40 │                              │
└───┴───────────────────────────────────┴───────┴──────────────────────────────┘
```

**Gate 2** — Proceed only when ALL true:

- [ ] All 8 dimensions scored with evidence
- [ ] Top 3 improvement areas identified and ranked by impact
- [ ] No dimension scored without reading the relevant content
- [ ] Trial-run behavior is included when a trial run was performed; otherwise the scorecard is marked static-evidence-only

_If gate fails_: Re-assess weak evidence; read more source files. For new checkpoints, use Pattern 1's gate shape in [references/exemplar-patterns.md](references/exemplar-patterns.md).

### Phase 3: Optimization Plan

Record: change (section/field/structure); rationale (best practice/spec); before/after; impact (expected score); risk (intent drift/reference breakage).

Cross-check the plan against known anti-patterns. See [references/anti-patterns.md](references/anti-patterns.md).

Present the plan to the user. **Wait for explicit approval before proceeding.**

**Gate 3** — Proceed only when ALL true:

- [ ] Plan presented with before/after examples
- [ ] User explicitly approved (full plan or approved subset)
- [ ] No approved change violates any Hard Rule

_If gate fails_: Revise the plan based on user feedback. Present again.

### Phase 4: Execute with Self-Correction

Apply approved changes by increasing risk: frontmatter fixes (lowest risk) → description improvements → structural reorganization → content splits to `references/` → new sections (verification, guardrails, failure handling) → content rewrites (highest risk).

**Self-correction triggers during execution:**

| Trigger                                      | Automatic Action                                            |
| -------------------------------------------- | ----------------------------------------------------------- |
| SKILL.md exceeds 500 lines after edit        | Split overflow content into references/                     |
| Description exceeds 250 chars                | Tighten to front-load the key use case                      |
| `name` doesn't match directory name          | Fix name field to match directory                           |
| File reference points to nonexistent file    | Create the missing file or remove the reference             |
| Score regresses on any dimension             | Stop, identify the cause, fix before continuing             |
| Mandatory rule accidentally altered          | Immediately revert that specific change                     |
| A time-sensitive statement is introduced     | Replace it with a timeless rule or Old patterns section     |
| An option menu has no selected default       | Choose one default and keep alternatives as an escape hatch |
| A reference chain goes deeper than one level | Link directly from SKILL.md or flatten the chain            |
| A path contains a backslash                  | Rewrite it as a forward-slash relative path                 |
| Gotchas are moved out of SKILL.md            | Restore trigger-critical Gotchas to SKILL.md                |

After each major edit, re-read the modified file to verify correctness.

**Gate 4** — Proceed only when ALL true:

- [ ] All approved changes applied
- [ ] No self-correction trigger left unresolved
- [ ] All file references resolve to existing files
- [ ] SKILL.md is under 500 lines

_If gate fails_: Apply the relevant self-correction rule. If stuck after 2 attempts, report to user.

### Phase 5: Verify & Report

1. **Re-audit**: Run Phase 2 scoring on the optimized skill
2. **Compare**: Build before/after scorecard
3. **Validate spec**: Check all Agent Skills spec rules. See [references/spec-rules.md](references/spec-rules.md)
4. **Check references**: Verify all linked files exist and are non-empty
5. **Trial run**: In a fresh context, run the improved skill and a baseline run from the pre-improvement snapshot on the same realistic task. Read both execution traces and record assertions that pass only with the improved version. Follow [references/trial-run.md](references/trial-run.md) when designing cases and grading evidence.
6. **Token and line estimate**: Record the approximate token cost and line-count delta for SKILL.md

The baseline must be a copy of the skill directory made before editing, not a reconstruction after the fact. If a trial run is infeasible, state the concrete reason and the evidence used instead.

Output the final report:

```
┌──────────────────────────────────────┬────────┬───────┬────────┐
│ Dimension                            │ Before │ After │ Change │
├──────────────────────────────────────┼────────┼───────┼────────┤
│ 1. Spec Compliance                   │  X/5   │  Y/5  │  +Z    │
│ 2. Description Quality               │  X/5   │  Y/5  │  +Z    │
│ 3. Context Economy & Disclosure      │  X/5   │  Y/5  │  +Z    │
│ 4. Structural Clarity                │  X/5   │  Y/5  │  +Z    │
│ 5. Instruction Quality & Calibration │  X/5   │  Y/5  │  +Z    │
│ 6. Guardrails & Validation           │  X/5   │  Y/5  │  +Z    │
│ 7. Composability & Script I/O        │  X/5   │  Y/5  │  +Z    │
│ 8. Cross-Platform Compatibility      │  X/5   │  Y/5  │  +Z    │
├──────────────────────────────────────┼────────┼───────┼────────┤
│ TOTAL                                │ XX/40  │ YY/40 │ +ZZ    │
└──────────────────────────────────────┴────────┴───────┴────────┘

Estimated tokens: ~NNNN (SKILL.md) + ~NNNN (references)
SKILL.md lines: BEFORE N → AFTER M (delta ±D)
Spec compliance: PASS / FAIL [details]
File integrity: All references resolve / [broken refs]
Trial-run evidence: [task, baseline comparison, assertions flipped, cost/latency delta] / NOT FEASIBLE [reason]
```

**Gate 5** — Optimization complete when ALL true:

- [ ] Total score improved (or maintained if already high quality)
- [ ] No dimension score regressed from Phase 2 baseline
- [ ] Spec compliance passes all checks
- [ ] All file references resolve to existing, non-empty files
- [ ] Trial-run evidence includes the improved-vs-baseline task and assertions, or an explicit reason the trial run was not feasible

_If gate fails_: Return to Phase 4 to fix regressions. Maximum 2 correction cycles before escalating to user.

## Self-Correction Protocol

When execution drifts off track, these rules trigger automatically:

1. **Drift detection**: After each phase, compare current state against the phase's gate conditions.
2. **Auto-retry**: If a gate fails, attempt the phase-specific correction documented in each gate's "If gate fails" section.
3. **Escalation**: If the same gate fails twice after correction attempts, stop and report to user with:
   - Which gate failed
   - What correction was attempted
   - What manual input is needed
4. **Regression guard**: If any quality dimension drops during optimization, immediately revert the change that caused it and report the regression.
5. **Scope lock**: If during execution you discover the skill needs changes beyond the approved plan, do NOT apply them. Note them as "Deferred Recommendations" in the final report.

## Key Patterns to Apply

When optimizing, draw from these proven patterns. Full catalog with examples at [references/exemplar-patterns.md](references/exemplar-patterns.md).

| #   | Pattern                       | When to Apply                                          |
| --- | ----------------------------- | ------------------------------------------------------ |
| 1   | Gate Checkpoints              | Multi-step workflow with failure risk                  |
| 2   | Output Contract               | Skill produces artifacts others consume                |
| 3   | Hard Rules Section            | Skill has non-negotiable constraints                   |
| 4   | Progressive Reference Loading | SKILL.md > 300 lines or detailed criteria              |
| 5   | Failure Handling Section      | Skill has steps that can fail                          |
| 6   | Self-Correction Rules         | Execution may drift from intent                        |
| 7   | Validation Checklist          | Multi-category validation would clutter the workflow   |
| 8   | Intent Card                   | Any existing skill is about to be modified             |
| 9   | When to Use Section           | Every skill; prevents false activation                 |
| 10  | Input Documentation           | Skill assumes implicit inputs                          |
| 11  | Validation Loop               | A script or checklist can objectively verify work      |
| 12  | Plan-Validate-Execute         | Batch or destructive operations need a safe plan       |
| 13  | Progress Checklist            | Workflow has several ordered steps or gates            |
| 14  | Output Format Template        | Outputs vary or another skill consumes the result      |
| 15  | Worked Input/Output Examples  | A step has ambiguous inputs or expected outputs        |
| 16  | Calibrated Instruction Block  | Some steps are fragile while others allow choice       |
| 17  | Bundled Script Interface      | Repeated logic merits a tested, non-interactive script |
| 18  | Old Patterns Section          | Superseded guidance must remain discoverable           |

Numbers match the pattern numbers in [references/exemplar-patterns.md](references/exemplar-patterns.md). A skill that lacks a verification step needs Pattern 11 (Validation Loop), not a prose "verification" section.

## Output Contract

On completion, always return:

1. Before/after scorecard (table format as shown in Phase 5)
2. Summary of changes made (bulleted list)
3. List of files modified and created
4. Trial-run evidence: realistic task, baseline comparison, assertions that flipped, and cost/latency delta
5. `SKILL.md` token estimate and line-count delta
6. Deferred recommendations (low-priority items not addressed)

Keep the human-readable report primary. Downstream consumers may rely on these stable fields, in this order:

```yaml
output_fields:
  - before_after_scorecard
  - changes_summary
  - files_modified_and_created
  - trial_run_evidence
  - skill_token_estimate_and_line_count_delta
  - deferred_recommendations
```

Do not include internal reasoning or optimization logic in the output.

## References

- [Scoring Rubric](references/scoring-rubric.md) — WHEN to load: for detailed 1-5 scoring criteria across all 8 dimensions
- [Spec Validation Rules](references/spec-rules.md) — WHEN to load: during Phase 5 spec compliance checks
- [Anti-Patterns](references/anti-patterns.md) — WHEN to load: during Phase 3 plan review to detect known failure modes
- [Exemplar Patterns](references/exemplar-patterns.md) — WHEN to load: when selecting a reusable pattern for an approved improvement
- [Trial-Run Procedure](references/trial-run.md) — WHEN to load: when an existing skill is being improved and you need baseline comparison, assertions, trace analysis, cross-configuration coverage, or trigger evals
