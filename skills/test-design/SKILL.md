---
name: test-design
description: >
  Designs structured test cases and coverage gaps from code, specs, or tickets. Use when
  users ask to design tests, generate test cases, edge case tests, boundary value tests,
  test plan, or /test-design.
license: MIT
compatibility: Requires file read/search access. LSP and git access improve code/spec tracing and test gap analysis.
metadata:
  author: fang2hou
  version: "1.1"
  sources: "review-and-fix skill; a month-end billing incident's countermeasure context; Go time docs; MDN Date docs"
---

# Test Design

Design the test plan before implementation escapes into review or release: extract risk-bearing domains from code or specs, then generate the exact cases needed to catch boundary, calendar, concurrency, state-transition, and library-semantic failures.

## When to Use

- User asks to design tests or generate test cases from code, specs, or a Jira ticket
- User wants edge case tests or boundary value tests before writing or shipping code
- User wants a feature-level test plan instead of test implementation
- User wants to compare planned coverage against existing tests and find gaps
- User says "design tests", "generate test cases", "edge case tests", "boundary value tests", "test plan", or "/test-design"

## When NOT to Use

- Writing test code as the primary task
- Reviewing a completed diff for bugs after implementation (use `review-and-fix`)
- Full release validation, exploratory QA execution, or production incident triage
- Performance benchmarking plans that do not require correctness or edge-case analysis

## Inputs

| Input                   | Required | Format                                                       | Example                                                          |
| ----------------------- | -------- | ------------------------------------------------------------ | ---------------------------------------------------------------- |
| Implementation artifact | Yes      | File path, function signature, code snippet, spec, or ticket | `billing/date.go`, `calculateRenewalDate(user, now)`, Jira story |
| Existing tests          | No       | Test files, test names, or "none"                            | `billing/date_test.go`, `renewal.spec.ts`                        |
| Business rule source    | No       | Spec note, ticket acceptance criteria, or doc excerpt        | "Month-end users renew on the last valid day of target month"    |

If the user gives only a ticket or prose requirement, extract the implied operations and data types from that artifact before generating cases.

## Hard Rules

1. **Design WHAT to test, not HOW to code the test**: Output test cases, not test implementation, unless the user explicitly asks for code later.
2. **Classify risk domains before generating cases**: Read the artifact and name which categories apply: date/time, boundary values, state transitions, concurrency, library/API gotchas, parsing/formatting, permissions, or external failures.
3. **Happy path is required but never sufficient**: Always include boundary, edge, error, and abnormal-condition cases for every applicable category.
4. **Every case needs an oracle**: Each test case must state expected behavior, not just input data.
5. **Library semantics are part of test design**: If the implementation relies on standard library or framework behavior, add at least one case that confirms normalization, coercion, mutation, defaulting, panic/throw, or timezone semantics.
6. **Record uncertainty explicitly**: If business behavior is unclear, create an `Open Question` instead of inventing an expectation.
7. **Gap analysis is mandatory when tests exist**: Mark each planned case as `covered`, `partial`, or `missing` against the current test suite.

## Workflow

Before starting, track the execution path:

- [ ] Phase 1 card and Gate 1
- [ ] Phase 2 category mapping and Gate 2
- [ ] Phase 3 cases
- [ ] Phase 4 gap analysis, oracle validation, and Gate 3

### Phase 1: Read the Artifact and Build a Test Design Card

#### Step 1: Resolve Scope and Inputs

1. Read the implementation files, spec, or ticket named by the user.
2. Read existing tests if they are provided or easy to locate from the same module.
3. Extract the business operation being validated: calculation, validation, transformation, state transition, retry flow, permission check, or external API handling.
4. Write this internal card before designing cases:

```text
Scope: [files/specs/tickets read]
Operation Under Test: [one sentence]
Primary Data Types: [date/time, number, string, enum/state, collection, async job, etc.]
Business Invariants: [rules that must always hold]
External Semantics: [library/API/database/timezone behavior relied on, or "none"]
Existing Test Surface: [files or "none"]
Unknowns: [missing rules, or "none"]
```

**Gate 1 — Pass only when ALL are true:**

- [ ] Scope and source files are explicit
- [ ] The operation under test is stated in one sentence
- [ ] Primary data types, invariants, external semantics, and unknowns are recorded

**Recovery if Gate 1 fails:** Read related functions, callers, tests, or spec sections; update the card. If behavior remains unclear, record it under `Unknowns` as an `Open Question` before continuing.

### Phase 2: Identify Applicable Risk Categories

#### Step 2: Map the Artifact to Failure Taxonomies

Classify which categories apply by reading actual code paths or spec rules, not by guessing.

| Signal in artifact                                                    | Category to apply     | Minimum action                                                   |
| --------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------- |
| `time`, `Date`, timezone, billing month, schedule, fiscal year        | Date/time/calendar    | Generate rollover, leap-year, timezone, DST, normalization cases |
| Comparisons, limits, counts, pagination, capacity, indexing           | Boundary values       | Generate min/max, off-by-one, empty, zero, overflow cases        |
| Retries, async jobs, locks, duplicate events, worker queues           | Concurrency / retry   | Generate idempotency, race-window, partial-failure cases         |
| Enums, statuses, lifecycle steps, toggles, approval flow              | State transitions     | Generate invalid combination and ordering cases                  |
| Standard library calls, serializers, parsers, SDKs, framework helpers | Library / API gotchas | Generate normalization/coercion/default/panic cases              |

Use [references/test-taxonomies.md](references/test-taxonomies.md) to expand each selected category into concrete scenarios and language-specific prompts.

#### Step 3: Extract the Exact Operations That Need Cases

For each selected category, list the operation and its failure surface.

Example:

```text
Operation: add one billing month to anchor date
Category: Date/time/calendar
Failure Surface: month-end normalization changes Feb 29/30/31 into March dates
Library Dependency: Go time.Time.AddDate
```

**Gate 2 — Pass only when ALL are true:**

- [ ] Every selected category is tied to a concrete operation
- [ ] Library/framework behavior is named where relevant
- [ ] At least one non-happy-path failure surface is written per category

**Recovery if Gate 2 fails:** Return to Step 2, inspect the relevant code path or rule, add the missing operation-to-risk mapping, and re-check every selected category.

### Phase 3: Generate Test Cases by Category

#### Step 4: Generate Baseline Cases First

Create 1-3 happy-path cases that prove the intended flow works for representative inputs. Keep them minimal; they are only the control group.

#### Step 5: Generate Non-Happy-Path Cases Systematically

For each applicable category, generate cases in this order:

1. **Boundary** — first legal value, last legal value, just-outside value
2. **Edge** — calendar anomalies, empty values, zero values, invalid combinations, duplicate delivery, missing dependencies
3. **Error / abnormal** — rejected input, thrown/panic path, timeout, parse failure, dependency failure
4. **Library gotcha** — normalization, coercion, mutation, silent default, timezone/local-time behavior

Every generated row must include:

- `ID`
- `Category`
- `Scenario`
- `Input / Setup`
- `Expected Behavior`
- `Priority` (`P0`, `P1`, `P2`, `P3`)
- `Evidence` (code path, spec rule, or ticket line)

Priority rubric:

- `P0`: legal/financial/security/invariant break or known incident pattern
- `P1`: likely user-facing regression at realistic boundaries
- `P2`: defensive case with lower probability or smaller blast radius
- `P3`: documentation-level or confirmatory case

### Phase 4: Compare Against Existing Tests

#### Step 6: Run Gap Analysis

If tests already exist:

1. Map each planned test case to an existing test, if any.
2. Mark the case as:
   - `covered`: an existing test exercises the same scenario and oracle
   - `partial`: nearby coverage exists, but the exact boundary or oracle is missing
   - `missing`: no existing test exercises the scenario
3. If only happy-path tests exist, state that explicitly instead of calling the suite "good coverage".

If no tests exist, mark all cases `missing` and note that the table is the initial design baseline.

#### Step 7: Ask the Missing-Behavior Question and Validate Oracles

Before finalizing, check whether any scenario exposes unclear expected behavior. Convert those into `Open Questions` with the missing rule called out.

Examples:

- "For Jan 31 + 1 month, should the result clamp to Feb 28/29, reject input, or preserve end-of-month semantics by business rule?"
- "If the same event is retried after partial success, should the second call return success, no-op, or duplicate error?"

**Oracle validation loop:** Inspect every generated row's `Expected Behavior`. For a missing or non-observable oracle, trace the evidence and add the expected outcome; if the rule is genuinely unclear, move the scenario to `Open Questions` rather than retaining an oracle-less case. Re-check the full table and repeat until every retained case has an explicit oracle.

**Gate 3 — Pass only when ALL are true:**

- [ ] Every applicable category produced concrete rows or an explicit `not applicable`
- [ ] Existing coverage is marked `covered`, `partial`, or `missing`
- [ ] Every retained row has an explicit oracle in `Expected Behavior`
- [ ] Unclear expectations are captured as `Open Questions`

**Recovery if Gate 3 fails:** Return to the failing phase: generate missing rows, mark coverage, or record unclear behavior as an `Open Question`; then rerun the oracle validation loop and re-check all four conditions.

## Gotchas

- Test the business contract over library documentation, target calendar anomalies rather than random dates, and do not infer boundary/oracle coverage from happy-path or similarly named tests.

## Output Contract

On completion, return these sections in order:

1. **Test Design Card**
2. **Applicable Categories**
3. **Test Case Table**. Stable field order for downstream consumers:
   `ID → Category → Scenario → Input / Setup → Expected Behavior → Priority → Existing Coverage → Evidence`

```text
| ID | Category | Scenario | Input / Setup | Expected Behavior | Priority | Existing Coverage | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

4. **Coverage Gaps Summary** — grouped by `missing` and `partial`
5. **Open Questions** — only if expectations are unclear
6. **Recommended Execution Order** — `P0` first, then `P1`, then the rest

When date/time, boundary, concurrency, library, or state-machine logic appears in the artifact, consult [references/test-taxonomies.md](references/test-taxonomies.md) before finalizing the table.
