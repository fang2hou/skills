# Instruction Patterns

Contents:

- [Calibration model](#calibration-model)
- [Gotchas](#gotchas)
- [Output-format template](#output-format-template)
- [Progress checklist](#progress-checklist)
- [Validation loop](#validation-loop)
- [Plan-validate-execute](#plan-validate-execute)
- [Worked input/output examples](#worked-inputoutput-examples)
- [Defaults, not menus](#defaults-not-menus)
- [Procedures over declarations](#procedures-over-declarations)

## Calibration model

Calibration matches instruction specificity to the fragility of the work. Calibrate each
section independently; one skill can use both freedom levels.

| Freedom level | Use when                                                                     | Instruction shape                                                                                  |
| ------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| High freedom  | Several approaches are valid and mistakes are cheap or reversible            | State the goal, useful heuristics, and why they matter; let the agent choose the route.            |
| Low freedom   | An operation is fragile, destructive, order-dependent, or must be consistent | Give the exact sequence, command, input shape, and expected result; say not to add flags or steps. |

Do not invent a middle tier. Explain why a constraint exists before rigid wording; that purpose lets an agent adapt safely. Reserve exact commands for parts where variation can cause failure.

Example:

```markdown
### Choose a parser (high freedom)

Select a parser that preserves the source's nested structure and explain the trade-off.

### Apply the migration (low freedom)

Run `tool migrate --check config.json`, then run the same command without `--check`.
Do not add flags. Stop if the check reports an error.
```

Why it works: exploration stays flexible while the irreversible step has an explicit, repeatable boundary.

## Gotchas

**When to apply:** Record facts that defy a reasonable assumption and can cause a wrong action. Put them in `SKILL.md`, not only a reference file, because the agent may not recognize the trigger for loading a reference.

```markdown
## Gotchas

- The manifest key is case-sensitive; `Timeout` is ignored even though the parser accepts it.
- A dry run still reads credentials, so use a least-privileged account for validation.
```

Why it works: the warning is visible while the agent plans work, before a hidden constraint turns into a failed or unsafe result. Keep each gotcha concrete and brief.

## Output-format template

**When to apply:** Use a template when callers or downstream tools need predictable fields or machine-readable output. Keep a short template inline; put long or reusable templates in `assets/` and link them from `SKILL.md`.

```markdown
## Output Contract

Return exactly:

1. `status`: `pass` or `fail`
2. `changed_files`: relative paths, in edit order
3. `checks`: each with `name`, `result`, and quoted evidence
```

Why it works: an agent can pattern-match the required shape and a consumer can validate it without guessing what prose means.

## Progress checklist

**When to apply:** Use a checklist for a multi-step workflow with observable gates or
recovery points. Keep it short enough to mark during execution.

```markdown
- [ ] Capture the requirements card and scope boundary.
- [ ] Gather one domain-specific source and record its gotchas.
- [ ] Draft, validate, and resolve every file reference.
- [ ] Run the trial run and baseline run; record what changed.
```

Why it works: the checklist externalizes state, prevents skipped phases, and makes the
completion condition visible instead of relying on memory.

## Validation loop

**When to apply:** Use when an output can be checked by a script or a stable reference
document. Repeat work, validation, and correction until the check passes; do not merely
assert that validation happened.

```markdown
1. Generate `result.json`.
2. Run `scripts/check-result.py result.json`.
3. If it fails, read the named field and expected type, fix the source, and run the check again.
4. Deliver only after the validator passes.
```

A reference-document validator is also valid:

```markdown
Compare each field with `references/schema.md`; record PASS or FAIL and quote the evidence.
Fix every FAIL, then repeat the comparison.
```

Why it works: the loop turns quality into an observable transition and gives failures a
specific recovery path. A validator may be a script or a concise reference checklist.

## Plan-validate-execute

**When to apply:** Use before batch, destructive, permission-changing, or otherwise
irreversible operations. Separate planning from execution and validate the plan against a
machine-readable source of truth.

```markdown
1. Emit `plan.json` with one operation per item.
2. Validate every `action` and `target` against `allowed-actions.json`.
3. If validation fails, name the invalid value and list the valid options.
4. Ask for the required approval only after the plan is valid.
5. Execute exactly the validated plan and report each result.
```

A useful error is `action "archivee" is invalid; valid options: "archive", "restore"`.
Do not silently coerce a value or execute a partially valid plan.

Why it works: a machine-readable plan makes scope inspectable, and explicit validation
errors let the agent repair inputs without guessing. Execution cannot drift from review.

## Worked input/output examples

**When to apply:** Add one realistic example when the correct shape, edge case, or decision
would otherwise be ambiguous. Choose an example that teaches a procedure, not a single
memorized answer.

```markdown
Input: `records.csv` has a blank `email` column and 12 duplicate IDs.

Output:

- `records.cleaned.csv` with blank emails preserved
- `duplicates.json` listing the 12 IDs
- a summary stating the row count before and after
```

Why it works: the agent sees the boundary behavior and the expected artifacts. One good
example is usually more useful than a catalogue of every possible input.

## Defaults, not menus

**When to apply:** Use whenever several compatible tools, formats, or strategies exist.
Choose one default, explain its reason, and mention alternatives only as an escape hatch.

```markdown
Use JSON Lines for streaming records because it bounds memory. Use CSV only when a
consumer explicitly requires tabular interchange.
```

Why it works: a default prevents option paralysis and inconsistent output while preserving
a clear route for a requirement that genuinely needs an alternative.

## Procedures over declarations

**When to apply:** Use for recurring work where the agent must decide and act across many
inputs. Replace statements about desired qualities with steps and observable results.

```markdown
For each endpoint, read its schema, send a valid request fixture, record the status and
response shape, then add one regression case for every failure observed.
```

Why it works: the procedure generalizes to new endpoints and gives the agent evidence to
check. A declaration such as “produce a robust API test” leaves the crucial decisions
implicit.
