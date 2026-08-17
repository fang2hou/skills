# Exemplar Skill Patterns

Proven patterns extracted from high-quality skills and the Agent Skills specification. Apply these during Phase 3 (Optimization Plan) when proposing improvements.

## Contents

- Foundations and workflow contracts: Patterns 1–3
- Disclosure, failure, and validation structure: Patterns 4–7
- Intent and input framing: Patterns 8–10
- Evidence, safety, and authoring quality: Patterns 11–18

## Pattern 1: Gate Checkpoints

**Source**: Common best practice

**When to apply**: Multi-step workflow where failure at any step risks cascading errors.

```markdown
### Step N: [Action]

[Instructions...]

**Gate N** — Proceed only when ALL true:

- [ ] [Verifiable condition 1]
- [ ] [Verifiable condition 2]

_If gate fails_: [Specific recovery action, not "try again"]
```

**Why**: Each gate is a safe checkpoint. Prevents the agent from plowing through failures. The "If gate fails" clause provides automatic recovery direction.

## Pattern 2: Output Contract

**Source**: Common best practice across high-quality skills

**When to apply**: Skill produces artifacts (files, URLs, reports) that users or other skills consume.

```markdown
## Output Contract

On success, return exactly:

1. [Artifact 1 — format and content]
2. [Artifact 2 — format and content]

Example:
[Concrete example of actual expected output]
```

**Why**: Eliminates ambiguity about what "done" looks like. Makes the skill composable — other skills know what format to expect.

## Pattern 3: Hard Rules Section

**Source**: Common best practice across high-quality skills

**When to apply**: Skill has non-negotiable constraints that must survive any optimization or execution.

```markdown
## Hard Rules

1. [Constraint that must never be violated]
2. [Safety boundary]
3. [Compliance requirement]
```

**Why**: Separates absolute constraints from soft preferences. Agents prioritize hard rules over general instructions. Optimizers know not to touch these.

## Pattern 4: Progressive Reference Loading

**Source**: Agent Skills spec + common best practice

**When to apply**: Skill has detailed reference material that bloats SKILL.md beyond 300 lines.

```
skill-dir/
├── SKILL.md              (~200-400 lines — core workflow)
└── references/
    ├── detail-a.md       (loaded only when referenced)
    └── detail-b.md       (loaded only when referenced)
```

In SKILL.md, link with context so the agent knows WHEN to load:

```markdown
For detailed scoring criteria per level, see [scoring-rubric.md](scoring-rubric.md).
```

**Why**: Agents load full SKILL.md on invocation (~100-5000 tokens). References load on demand. Keeps base token cost low while preserving access to detailed content.

## Pattern 5: Failure Handling Section

**Source**: Common best practice

**When to apply**: Skill has steps that interact with external systems or can fail unpredictably.

```markdown
## Failure Handling

If any required condition fails, stop and ask a focused question:

| Failure Mode | Recovery Action                                |
| ------------ | ---------------------------------------------- |
| [Mode 1]     | [Specific recovery, e.g., "Ask user for X"]    |
| [Mode 2]     | [Specific recovery, e.g., "Retry with flag Y"] |

Error message examples:

- "[Exact error text agent should look for]"
```

**Why**: Prevents the agent from guessing when things go wrong. Concrete error examples help pattern-match failures.

## Pattern 6: Self-Correction Rules

**Source**: Synthesized from best practices

**When to apply**: Skill execution may drift from its intended path due to edge cases or agent behavior.

```markdown
## Self-Correction Rules

| Trigger                | Automatic Action      |
| ---------------------- | --------------------- |
| [Detectable condition] | [Specific correction] |
| [Another condition]    | [Another correction]  |
```

**Why**: Builds resilience into the skill. Common drifts get auto-corrected without user intervention. The table format makes triggers scannable.

## Pattern 7: Validation Checklist (Supporting File)

**Source**: Common best practice across high-quality skills

**When to apply**: Skill has complex multi-category validation that would clutter the main workflow.

```markdown
# references/validation-checklist.md

## A. [Category] Validation

- [ ] [Check 1]
- [ ] [Check 2]

## B. [Category] Validation

- [ ] [Check 3]
- [ ] [Check 4]

## Failure Policy

If any check in A-B fails:

1. [Specific remediation step]
2. [Escalation if remediation fails]
```

**Why**: Keeps main SKILL.md focused on workflow. Checklist can be loaded independently during verification phases. Categories make it clear which checks are blocking.

## Pattern 8: Intent Card

**Source**: This skill (improve-skill)

**When to apply**: Before modifying any existing skill. Captures the skill's identity to prevent optimization from drifting its purpose.

```
Intent: [one sentence — what problem does this skill solve?]
Domain: [workflow | expertise | hybrid]
Mandatory Rules: [list of untouchable constraints]
Existing Gates: [list of current checkpoints, or "none"]
Platform Dependencies: [list, or "none"]
```

**Why**: Crystallizes what must NOT change before any changes are made. The mandatory rules list directly informs which optimizations are safe.

## Pattern 9: When to Use Section

**Source**: Common across all high-quality skills

**When to apply**: Every skill should have this. It's the expanded version of the description.

```markdown
## When to Use

Use this skill when:

- [Specific trigger scenario 1]
- [Specific trigger scenario 2]
- [Specific trigger scenario 3]

Do NOT use this skill when:

- [Out-of-scope scenario]
```

**Why**: Agents match skills to tasks based on description + this section. The "Do NOT use" list prevents false matches, which waste tokens and user time.

## Pattern 10: Input Documentation

**Source**: Common best practice

**When to apply**: Skill requires information to operate that isn't obvious from the invocation.

```markdown
## Inputs

| Input  | Required | Format        | Example            |
| ------ | -------- | ------------- | ------------------ |
| [Name] | Yes/No   | [Type/format] | [Concrete example] |
```

**Why**: Removes guesswork. The agent knows exactly what to gather before starting. The table format is scannable and structured.

## Pattern 11: Validation Loop

**Source**: Common best practice for observable workflows

**When to apply**: Work can be checked by a script validator or a focused reference-document checklist.

```markdown
### Validate

1. Do the work.
2. Run `[validator command]` or load `[reference-checklist.md]`.
3. Fix every reported failure.
4. Repeat until all checks pass.

Pass condition: [objective result, such as valid JSON and exit code 0].
```

**Why**: A loop turns validation into a completion condition instead of a one-time suggestion. The validator can be executable or a document whose checks are applied consistently.

## Pattern 12: Plan-Validate-Execute

**Source**: Safety pattern for irreversible or high-volume operations

**When to apply**: A batch or destructive operation must be reviewed before it changes state.

```markdown
1. Emit a structured plan without executing it.
2. Validate every plan field against the machine-readable source of truth.
3. If invalid, name the field and invalid value, then list valid options:
   {"error":"invalid value","field":"mode","value":"fast-ish","valid_options":["safe","fast"]}
4. Execute only a validated plan; support `--dry-run` when the operation is destructive.
```

**Why**: Separating planning, validation, and execution makes side effects reviewable and gives the agent a precise recovery path for invalid values.

## Pattern 13: Progress Checklist

**Source**: Common best practice for multi-step workflows

**When to apply**: Several ordered actions, gates, or deliverables must remain visible during execution.

```markdown
Progress:

- [ ] Capture inputs and constraints
- [ ] Apply the approved change
- [ ] Run validation and fix failures
- [ ] Report outputs and evidence
```

**Why**: A checklist prevents skipped steps and makes incomplete work obvious without adding a second prose workflow.

## Pattern 14: Output Format Template

**Source**: Common best practice for composable outputs

**When to apply**: Users or downstream skills need a stable result shape. Keep a short stable template inline; place a long or conditional template in `assets/` and link it from SKILL.md.

```markdown
## Output

Return:
{"status":"pass","changed_files":[],"evidence":[]}

For the long or conditional form, load `assets/output-template.json` from SKILL.md.
```

**Why**: Inline templates are immediately available for simple outputs. `assets/` avoids bloating SKILL.md when the format has many fields or branches.

## Pattern 15: Worked Input/Output Examples

**Source**: Common best practice for ambiguous transformations

**When to apply**: An instruction has multiple plausible interpretations or the expected result is easier to show than describe.

```json
{
  "input": { "path": "reports/raw.csv", "delimiter": "," },
  "output": { "path": "reports/clean.csv", "columns": ["id", "amount"], "validated": true }
}
```

**Why**: A compact realistic example gives the agent a pattern to generalize while keeping the procedure reusable. It also anchors field names and output shape without prescribing irrelevant details.

## Pattern 16: Calibrated Instruction Block

**Source**: Best practice for matching control to task fragility

**When to apply**: A workflow contains both tolerant choices and operations where variation can cause failure.

| High freedom — explain the goal                                                         | Low freedom — specify the exact operation                                                            |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| “Choose any deterministic parser that preserves the stated fields; explain the choice.” | “Run the validator after editing. Do not add flags because its exit codes are part of the contract.” |

```markdown
Use high freedom for [tolerant decision] because [why variation is safe].
Use low freedom for [fragile operation] because [failure risk and required invariant].
```

**Why**: Calibration avoids both needless rigidity and unsafe guessing. WHY-bearing instructions help the agent adapt when circumstances change.

## Pattern 17: Bundled Script Interface

**Source**: Best practice for repeated agentic execution

**When to apply**: Repeated logic is reliable enough to bundle as a script rather than reinvent on each run.

```text
Usage: scripts/check.py --input PATH [--format json] [--dry-run]
--help              Show usage and exit
--input PATH        Read input from PATH (required)
--format json       Emit structured JSON on stdout
--dry-run           Preview destructive changes without applying them

Exit codes:
0  success
2  usage or invalid input
3  validation failure

stdout: machine-readable result only
stderr: diagnostics and remediation hints
```

**Why**: A documented, non-interactive interface is retryable and composable. Flags make inputs explicit, structured stdout is consumable, and distinct exit codes let callers recover deterministically.

## Pattern 18: Old Patterns Section

**Source**: Maintenance pattern for durable guidance

**When to apply**: A prior approach remains useful for migration context but must not be mistaken for the current default.

```markdown
## Old Patterns

The following guidance is superseded. Keep it only for migration or compatibility:

- [Old approach]: [why it was replaced and what to use now]
```

**Why**: Labeling superseded material preserves useful history without introducing time-sensitive instructions into the active procedure.
