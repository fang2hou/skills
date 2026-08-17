# Test Taxonomies

Detailed prompts for turning risky domains into concrete test cases during test planning.

## Contents

- How to Use This Reference
- Date / Time / Calendar
- Boundary Values
- Concurrency / Retry / Partial Failure
- Library / API Gotchas
- State Transitions
- Turning prompts into rows
- Output quality checks

## How to Use This Reference

1. Read the implementation or spec first.
2. Select only the categories that the artifact actually uses.
3. For each selected category, turn the prompts below into explicit test rows with input, oracle, and priority.
4. Mark categories that do not apply as `not applicable` instead of silently skipping them.

## 1. Date / Time / Calendar

Apply when the artifact parses, stores, compares, adds, subtracts, truncates, rounds, schedules, or groups by time.

### Mandatory prompts

- Month-end rollover: 28th / 29th / 30th / 31st plus or minus one month
- Leap year vs non-leap year: Feb 28, Feb 29, Mar 1 across year boundaries
- Timezone conversion: same instant rendered in business timezone vs system timezone
- DST boundary: spring-forward gap and fall-back overlap
- Fiscal or reporting cutover: month-end, quarter-end, year-end, fiscal year start/end
- Invalid or impossible calendar dates: input rejects, clamps, normalizes, or silently shifts
- Equality and ordering: same wall-clock string in different zones, midnight boundary, inclusive/exclusive end times

### Impossible target date pattern

If the business rule says "same day next month" or "month-end user", generate a case specifically for an impossible target date.

Example row:

| Category           | Scenario                            | Input / Setup                                           | Expected Behavior                                                                               |
| ------------------ | ----------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Date/time/calendar | End-of-month rollover from leap day | Anchor date `2024-02-29`, add `+1 year` or `+12 months` | Behavior matches business contract; no silent shift to an unintended date without explicit rule |

### Go-specific prompts

- `time.Time.AddDate` uses wall-time calendar arithmetic and can normalize impossible dates into later valid dates; test Jan 29/30/31 and Feb 29 anchors explicitly.
- `time.Date` also accepts out-of-range components and normalizes them; test invalid month/day construction if code builds dates manually.
- `AddDate`, `Round`, `Truncate`, `UTC`, `Local`, and `In` strip monotonic clock readings; avoid equality assumptions that depend on `==` semantics.
- `time.Time ==` compares location and monotonic data, not just the instant; if code checks equality, test `Equal()` semantics vs raw struct equality expectations.
- Go deliberately does not define `time.Day`; if code uses `24 * time.Hour` for calendar-day logic, test DST crossings because "24 hours later" may not mean "next local day".

Evidence: Go `time` docs say `AddDate` is a wall-time computation, strips monotonic readings, and the package avoids day-sized durations because DST transitions make them ambiguous.

### TypeScript / JavaScript prompts

- `Date.prototype.setMonth()` mutates the object in place; test shared-reference callers if the same object is reused.
- `setMonth()` and the `Date` constructor normalize out-of-range values; test `Jan 31 -> February` explicitly.
- `Date` APIs operate in local time unless UTC variants are used; test whether business logic accidentally depends on machine timezone.
- Crossing DST with local-time setters can change elapsed timestamps by 23 or 25 hours rather than exactly 24 hours per day.
- `undefined`, `NaN`, or partial date parsing can produce `Invalid Date`; test coercion and rejected input behavior explicitly.

Evidence: MDN documents that `setMonth()` reuses the current day-of-month, normalizes overflow, mutates in place, and can cross DST with non-intuitive timestamp differences.

## 2. Boundary Values

Apply when logic compares counts, ranges, thresholds, lengths, capacities, money, IDs, pagination, or indexes.

### Mandatory prompts

- Minimum legal value
- Maximum legal value
- Just below minimum
- Just above maximum
- Empty / null / nil / zero-value input
- One element vs many elements
- Overflow, underflow, truncation, or precision loss
- Inclusive vs exclusive endpoints

### Typical scenario families

| Pattern          | Example prompts                                                                        |
| ---------------- | -------------------------------------------------------------------------------------- |
| Off-by-one       | first item, last item, `limit`, `limit+1`, `index==len`, `index==len-1`                |
| Empty and zero   | empty string, empty array, nil slice, `0`, `false`, missing optional field             |
| Numeric caps     | max balance, max page size, integer overflow, decimal rounding                         |
| Parsing boundary | shortest valid string, longest valid string, invalid delimiter, malformed numeric text |

## 3. Concurrency / Retry / Partial Failure

Apply when the artifact uses goroutines, async tasks, locks, queues, retries, webhooks, message handlers, cron jobs, or external side effects.

### Mandatory prompts

- Same request delivered twice
- Retry after partial success
- Timeout between validation and commit
- Race between two writers or writer/reader
- Out-of-order completion
- External dependency succeeds once and fails once
- Lock missing, double release, or stale state visibility

### Concrete questions

- If the same operation is retried, is the result idempotent, duplicate-safe, or corrupting?
- Can validation pass and then become false before mutation happens?
- If step 2 fails after step 1 succeeded, what state should remain visible?
- Is eventual consistency acceptable, and if yes, for how long?

## 4. Library / API Gotchas

Apply whenever code relies on standard library helpers, framework utilities, SDKs, parsers, serializers, or hidden defaults.

### Mandatory prompts

- Normalization or coercion: invalid input becomes valid-looking output
- Silent defaults: omitted field gets default value without explicit acknowledgment
- Mutation: helper mutates the passed object, map, slice, or options object
- Panic / throw / exception path
- Nil / null / undefined behavior
- Unit mismatch: seconds vs milliseconds, bytes vs characters, local time vs UTC
- Ordering dependency: call sequence matters even if types allow misuse

### High-value examples

- Serializer omits zero values and changes API payload semantics
- Parser accepts malformed input and substitutes a default value
- SDK retries automatically, causing duplicate side effects
- Helper sorts or normalizes input, masking a bug that business rules need surfaced

## 5. State Transitions

Apply when entities move through statuses, steps, modes, or permission states.

### Mandatory prompts

- Valid transition forward
- Invalid transition forward
- Repeat same transition twice
- Transition backward
- Two flags or statuses set in an impossible combination
- Transition allowed only after prerequisite step
- Transition with stale version or stale timestamp

### Concrete questions

- Which states are terminal?
- Which combinations are impossible but still representable in code?
- Does ordering matter even if all individual operations succeed?
- If two transitions happen concurrently, which one wins?

## 6. Turning prompts into rows

For each row, state:

1. Exact input or setup values
2. Expected behavior or oracle
3. Why this row exists (code path, spec statement, or library semantic)
4. Priority based on user impact and blast radius

Bad row:

```text
Edge case: month end
```

Good row:

```text
ID: DT-03
Category: Date/time/calendar
Scenario: Jan 31 subscription renewal plus one month
Input / Setup: anchor date `2025-01-31`, business timezone `Asia/Tokyo`
Expected Behavior: renews on last valid day of February if contract says "month-end preserved"; otherwise reject as unsupported and surface explicit error
Priority: P0
Evidence: billing rule in ticket + use of AddDate/setMonth in implementation
```

## 7. Output quality checks

Before returning the test plan, verify:

- Every applicable category produced at least one non-happy-path row
- Every row has a real oracle, not just an input
- Known library semantics are tested explicitly when relevant
- Existing tests are marked `covered`, `partial`, or `missing`
- Open questions are separated from asserted expectations
