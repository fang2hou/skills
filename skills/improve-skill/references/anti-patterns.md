# Anti-Patterns & Fixes

Common skill quality issues with detection signals and concrete fixes. Reference this during Phase 3 (Optimization Plan) to cross-check proposed changes.

## Contents

- Frontmatter anti-patterns: AP-1–4
- Structure anti-patterns: AP-5–8
- Instruction anti-patterns: AP-9–12
- Safety anti-patterns: AP-13–15
- Composability anti-patterns: AP-16–17
- Cross-platform anti-patterns: AP-18–19
- Context, authoring, and trial-run anti-patterns: AP-20–32

## Frontmatter Anti-Patterns

### AP-1: Vague Description

**Detect**: Description under 20 words, lacks action verbs, or missing trigger keywords.

**Bad**: `description: Helps with deployment`

**Fix**: `description: Deploys applications through a repeatable release workflow. Use when deploying, rolling back, or checking deployment status. Triggers on 'deploy', 'rollback', 'release'.`

### AP-2: Name Mismatch

**Detect**: `name` field value differs from the directory name.

**Bad**: Directory `my-skill/` with `name: mySkill`

**Fix**: Make them match exactly: directory `my-skill/` with `name: my-skill`

### AP-3: Missing Compatibility

**Detect**: Skill requires specific tools, CLI access, or network resources but has no `compatibility` field.

**Fix**: Add `compatibility: Requires [specific requirements]`. Only add this when real requirements exist — not every skill needs it.

### AP-4: Description Too Long

**Detect**: Description exceeds 250 characters. Will be truncated in skill listings, losing critical context.

**Fix**: Front-load the key use case in the first 50 characters. Move detailed trigger examples to the "When to Use" section in the body.

## Structure Anti-Patterns

### AP-5: Monolithic SKILL.md

**Detect**: SKILL.md exceeds 500 lines.

**Fix**: Extract detailed reference material into `references/` directory. Keep SKILL.md as navigation hub + core workflow. Use clear links that point to real files in `references/`.

### AP-6: No Section Structure

**Detect**: Long prose blocks without markdown headings.

**Fix**: Break into standard sections. Recommended minimum: Purpose, When to Use, Workflow, Output. For complex skills add: Hard Rules, Inputs, Verification, Failure Handling.

### AP-7: Inverted Information Pyramid

**Detect**: Most important information (core workflow, key rules) buried deep in the file. Secondary information (background, philosophy) up front.

**Fix**: Front-load critical content. During context compaction, agents may truncate from the end. The first 200 lines should contain everything needed for basic execution.

### AP-8: Dead Reference Links

**Detect**: File references point to nonexistent files.

**Fix**: Either create the missing file with appropriate content, or remove the broken reference. Verify every reference resolves during Phase 5.

## Instruction Anti-Patterns

### AP-9: No Verification Section

**Detect**: Skill produces output or makes changes but has no step to confirm success.

**Fix**: Add a Verification section with concrete commands. Example: "Run the project's test command and confirm exit code 0. Run its lint command with no errors."

### AP-10: Implicit Inputs

**Detect**: Skill workflow assumes information (file paths, API keys, config values) without documenting it.

**Fix**: Add an explicit Inputs section listing all required and optional inputs with types and examples.

### AP-11: No Success Criteria

**Detect**: No definition of what "done" looks like. Skill just... ends.

**Fix**: Add explicit success criteria. "The skill is complete when: [concrete checklist]". Tie to verification commands where possible.

### AP-12: Ambiguous Steps

**Detect**: An instruction gives no condition, default, or verifiable result. Signal phrases include "handle appropriately", "process as needed", and "ensure quality".

**Fix**: Replace with specific actions. What tool to use, what command to run, what output to check, what constitutes pass/fail.

## Safety Anti-Patterns

### AP-13: No Guardrails

**Detect**: Skill can cause side effects (file writes, API calls, deployments) with no constraints section.

**Fix**: Add a Hard Rules or "Never Do" section. Example: "Never push to main directly. Never delete files without confirmation. Never store credentials in skill output."

### AP-14: No Escalation Path

**Detect**: Skill has no defined behavior for "I can't handle this" situations.

**Fix**: Define conditions that trigger asking the user: unresolvable errors, ambiguous requirements, out-of-scope requests. Example: "If [condition], stop and ask: [specific question]."

### AP-15: No Failure Handling

**Detect**: No mention of what happens when workflow steps fail.

**Fix**: Add a Failure Handling section mapping failure modes to recovery actions. Include example error messages so the agent knows what to look for.

## Composability Anti-Patterns

### AP-16: Hidden State

**Detect**: Skill assumes prior runs, session history, or external state that isn't documented.

**Fix**: Make each invocation self-contained. If state is genuinely needed, document it explicitly in an Inputs or Prerequisites section.

### AP-17: Unparseable Output

**Detect**: Skill output is free-form prose with no structured format.

**Fix**: Define an Output Contract specifying the exact format: table, JSON, structured text block. Include a concrete example.

## Cross-Platform Anti-Patterns

### AP-18: Platform-Locked Instructions

**Detect**: Workflow instructions use proprietary runtime syntax or product-specific tool names as if every agent supports them.

**Bad**: "Use the platform's private command syntax to perform every file operation."

**Fix**: Describe WHAT to do in agent-agnostic language. Move implementation-specific features to clearly marked optional sections or the `compatibility` field.

### AP-19: Hard-Coded Tool Names

**Detect**: Instructions reference tools by platform-specific identifiers (for example, a proprietary file reader or shell tool).

**Fix**: Describe the action generically: "run the following command", "read the file contents". Agents will map to their available tools.

### AP-20: Agent-Known Explanation

**Detect**: The skill explains broad concepts the agent already knows instead of adding task-specific constraints.

**Bad**: "JSON is a text format made of objects and arrays. Here is what an object is..."

**Fix**: Keep only context that prevents a demonstrated mistake; apply the test “Would the agent get this wrong without this instruction?”

### AP-21: Rigid Directive Stack Without Rationale

**Detect**: Many MUST/NEVER/ALWAYS directives constrain ordinary choices without explaining the risk or purpose.

**Bad**: "Always use A. Never use B. Must do C. Do not change D." (no reason)

**Fix**: Calibrate freedom to fragility and state WHY a low-freedom instruction is necessary.

### AP-22: Option Menu Without Default

**Detect**: The skill lists several tools, methods, or formats but does not select a default.

**Bad**: "Use A, B, C, or D depending on your preference."

**Fix**: Pick one default approach; mention alternatives only as an escape hatch when the default cannot work.

### AP-23: Declarative One-Off Answer

**Detect**: Guidance gives the answer for one example instead of a procedure reusable across similar tasks.

**Bad**: "For this file, change line 12 to value X."

**Fix**: Teach the generalized steps, inputs, decision points, and validation that produce the answer for each case.

### AP-24: Time-Sensitive Guidance

**Detect**: Instructions depend on a date, temporary cutoff, current release, or “before/after” version statement.

**Bad**: "Before <cutoff date>, use the old API."

**Fix**: State the durable rule and put genuinely superseded guidance in a clearly labeled Old patterns or deprecated section.

### AP-25: Terminology Drift

**Detect**: One concept is named with multiple terms across sections or references.

**Bad**: The workflow alternates among “trigger test,” “activation eval,” and “discovery check” for the same operation.

**Fix**: Capture a terminology set, choose one canonical term, and use it verbatim everywhere.

### AP-26: Trigger-Critical Gotcha Buried

**Detect**: An environment-specific fact that changes the next action appears only in a reference file with no reliable trigger to load it.

**Bad**: The main workflow says “run the validator,” while the reference alone warns that it cannot accept interactive input.

**Fix**: Keep trigger-critical Gotchas in SKILL.md; link optional detail one level deep.

### AP-27: Deep Reference Chain

**Detect**: SKILL.md links to a reference that links to another reference, or deeper.

**Bad**: `SKILL.md → workflow.md → details.md → examples.md`

**Fix**: Link each needed reference directly from SKILL.md and keep navigation one level deep.

### AP-28: Backslash Path

**Detect**: A skill or reference uses Windows-style backslashes in a path.

**Bad**: `references\scoring-rubric.md`

**Fix**: Use forward-slash paths relative to the skill root: `references/scoring-rubric.md`.

### AP-29: Interactive Script

**Detect**: A bundled script prompts, reads from a TTY, or waits for confirmation during normal execution.

**Bad**: `input("Continue? [y/N] ")`

**Fix**: Take input through flags, environment variables, or stdin; expose concise `--help` and fail with a usage message instead of blocking.

### AP-30: Opaque Script Error or Magic Constant

**Detect**: Errors do not name the problem or expected values, or tuned constants appear without an explanation.

**Bad**: `Error: invalid input` and `TIMEOUT = 37` with no rationale.

**Fix**: Write helpful diagnostics to stderr that state what was wrong, what was expected, and what to try; comment the rationale for every tuned constant.

### AP-31: Mixed Script Streams

**Detect**: Machine-readable data and human diagnostics are mixed on stdout.

**Bad**: `{"ok":true}` followed by `warning: skipped 3 files` in the same output stream.

**Fix**: Emit structured data only on stdout and diagnostics on stderr; document the schema and how callers interpret each exit code.

### AP-32: No Trial Run or Baseline

**Detect**: An improvement is judged by static reading only, with no fresh-context trial run against a pre-improvement baseline.

**Bad**: "The rewrite looks clearer, so it is complete."

**Fix**: Snapshot before editing, run the same realistic task with improved and baseline versions, inspect traces, and record objective assertions that flipped.
