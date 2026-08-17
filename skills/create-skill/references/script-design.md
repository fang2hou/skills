# Script Design for Agentic Use

Contents:

- [Hard requirements](#hard-requirements)
- [Interface](#interface)
- [Robustness](#robustness)
- [Packaging](#packaging)

Use this guide before adding `scripts/` to a skill. Scripts are part of the skill's
interface: an agent must be able to run them, interpret them, and retry them without a
conversation with the author.

## Hard requirements

### Non-interactive execution

Never prompt for input. Agents commonly run non-interactive shells, so a prompt can hang
forever. Take input through flags, environment variables, or stdin, and fail with a usage
message when required input is absent.

```text
Bad:  "Press y to continue"
Good: --confirm is required for the non-dry-run path; otherwise exit with usage guidance.
```

### Stable paths

Document paths relative to the skill root and write them with forward slashes, including
when the host is Windows. Do not rely on the process's current directory unless the
interface defines it.

```text
Bad:  ..\output\report.json
Good: references/schema.md or ./output/report.json
```

### Helpful errors

An error must state what was wrong, what was expected, and what to try next. Do not expose a
raw stack trace as the only recovery path.

```text
Invalid --format "jso"; expected one of: json, csv. Try --format json.
```

### Solve, do not defer

The script handles expected missing-file, permission, and malformed-input cases itself.
It should explain and exit cleanly instead of telling the agent to investigate an
unimplemented condition.

## Interface

### Self-documenting help

`--help` is concise and documents inputs, defaults, outputs, destructive flags, and exit
codes. It must work without network access or a project-specific setup.

### Input channels

Use flags for explicit per-run choices, environment variables for secrets or stable
configuration, and stdin for streamed records. Define precedence when more than one channel
can provide the same value. Never read a secret from a positional argument that appears in
process listings.

### Distinct exit codes

Document stable, distinct codes, for example: `0` success; `2` usage or validation error;
`3` missing input; `4` permission or external-operation failure. Select codes that match the
host language and keep them stable for callers.

### Structured streams

Write machine-readable results (JSON, CSV, or TSV) to stdout. Write diagnostics, progress,
and human-readable errors to stderr so stdout remains pipeable.

```text
stdout: {"status":"ok","count":18}
stderr: processed 18 records from input.csv
```

### Predictable output size

Do not dump an unbounded record set. Summarize by default and offer `--limit`, cursors, or
pagination for detail. State whether the limit applies before or after filtering. Keep
individual pages small enough for the consuming harness.

## Robustness

### Idempotency

A retry with the same inputs should not duplicate changes. Detect an existing output,
replace it atomically, or record a stable operation key. Document any operation that cannot
be idempotent and require an explicit opt-in.

### Dry runs and safe defaults

Destructive operations default to a no-op preview. Provide `--dry-run` and show the exact
planned targets; require an explicit flag for execution. Never treat an empty target list as
“all targets.”

### Explain constants

Avoid unexplained magic numbers. Every tuned limit, timeout, retry count, or page size gets
a one-line rationale comment and, when useful, a flag with a documented default.

```python
PAGE_SIZE = 100  # Keeps one response below the harness output limit while remaining useful.
```

## Packaging

### One-command, self-contained scripts

Declare dependencies inline so the script runs in one documented command without a hidden
installation step. Examples include a PEP 723 header with `uv run script.py`, a Deno import
map, or an inline bundle. Keep the script's dependency versions explicit.

### Pin one-off runners

When a runner is fetched for a one-off operation, pin its version (for example,
`runner@1.2.3`) so retries do not silently change behavior. Prefer a bundled script when
execution is repeated.

### State prerequisites

Put required system packages, network access, credentials, and supported environments in
`SKILL.md` or its `compatibility` field. Do not hide prerequisites in a script comment that
the agent will see only after a failed run.

```text
Bad:  run tool   # assumes an unmentioned package and network access
Good: uv run --script scripts/check.py --help
      Prerequisite: Python 3.11+; no network access after dependencies are cached.
```
