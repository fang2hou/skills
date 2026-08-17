# Trial-Run Procedure

## Contents

- [Purpose and evidence model](#purpose-and-evidence-model)
- [1. Snapshot the baseline](#1-snapshot-the-baseline)
- [2. Design realistic cases](#2-design-realistic-cases)
- [3. Run improved and baseline versions](#3-run-improved-and-baseline-versions)
- [4. Add assertions after first outputs](#4-add-assertions-after-first-outputs)
- [5. Grade and analyze](#5-grade-and-analyze)
- [6. Read execution traces](#6-read-execution-traces)
- [Trigger eval when description changed](#trigger-eval-when-description-changed)
- [Cross-configuration coverage](#cross-configuration-coverage)
- [Evidence record](#evidence-record)

## Purpose and evidence model

A trial run tests whether an existing skill changes realistic work, not merely whether its prose looks better. Compare the improved skill with a baseline run made from the exact pre-improvement snapshot. Use a fresh context for every run so prior reasoning, cached files, and remembered instructions do not contaminate the comparison.

Use two or three cases that exercise the changed guidance. Keep the task, input files, and expected-output description identical between improved and baseline runs. Run each case twice per configuration when practical; nondeterministic behavior is evidence, not noise to hide.

Record both output evidence and the execution trace. Final artifacts show what happened; traces show why: vague instructions cause trial-and-error, inapplicable instructions cause unnecessary steps, and option overload causes indecision or repeated branching.
Use **trigger eval** only for description activation testing; use **output-quality eval** for result grading with assertions. A **baseline run** is this skill's previous-version snapshot, and a **trial run** is one fresh-context execution used to gather evidence.

## 1. Snapshot the baseline

1. Resolve the target skill directory and read it completely.
2. Copy the entire directory, including references, scripts, and assets, to a separate baseline location before any edit.
3. Record the snapshot identifier and timestamp in the evidence record. Do not reconstruct a baseline from the edited files.
4. Keep the improved directory and baseline snapshot otherwise identical. If an input fixture must change, copy the same fixture into both runs and record the change.

A compact run manifest can be plain JSON:

```json
{
  "skill": "improve-skill",
  "baseline_snapshot": "baseline/improve-skill-before",
  "improved_path": "skills/improve-skill",
  "fresh_context": true,
  "cases": ["case-1", "case-2"]
}
```

## 2. Design realistic cases

Choose prompts from real work the skill is meant to improve. Vary phrasing and explicitness: one direct request, one underspecified request that should benefit from the workflow, and optionally one multi-step request. Do not choose toy prompts that only repeat the skill's headings.

For each case, write a human-readable expected result before running it. Include input files or a small fixture when the skill normally needs them. State observable properties, boundaries, and required artifacts; do not prescribe an exact sentence unless the sentence itself is the contract.

```json
{
  "id": "case-1",
  "prompt": "Review the target skill and propose the three safest improvements, then report evidence.",
  "inputs": ["fixtures/target-skill/SKILL.md"],
  "expected_output": "A before/after scorecard, three ranked changes, and evidence that every linked reference resolves."
}
```

Use the same prompt and inputs for the improved and baseline runs. Avoid adding hints to the improved prompt that the baseline does not receive.

## 3. Run improved and baseline versions

1. Start a fresh context for the improved version and run the case once.
2. Start another fresh context for the baseline snapshot and run the identical case once.
3. Repeat both configurations for a second trial when behavior may vary. A third trial is useful for a high-risk or nondeterministic case.
4. Capture final outputs, changed files, execution traces, elapsed time, and token or line-cost measurements available from the harness.
5. Never treat a successful process exit as proof that the output satisfies the case.

Use a run record with one row per configuration and trial:

```json
{
  "case": "case-1",
  "configuration": "improved",
  "trial": 1,
  "status": "completed",
  "elapsed_ms": 8420,
  "tokens": 2310,
  "output_path": "evidence/case-1/improved-1.txt",
  "trace_path": "evidence/case-1/improved-1.trace"
}
```

Compute deltas with the same units: improved minus baseline for elapsed time and tokens, and report the absolute and percentage change when meaningful. A capability gain can justify added cost; unexplained cost without a capability gain is a regression to investigate.

## 4. Add assertions after first outputs

Inspect the first improved and baseline outputs before finalizing assertions. Add assertions that distinguish the changed behavior and can be checked objectively. Each assertion must say what to inspect and what counts as PASS or FAIL.

Good assertions include: “the output file parses as JSON”; “the report names all three changed files”; “both axes have labels”; “the plan lists a valid option when the input value is invalid”; or “the script exits with code 2 for invalid input.”

Do not use “output is good,” subjective polish, or brittle exact-phrase matches. Check structure, fields, counts, invariants, valid paths, exit codes, and quoted evidence. If an assertion is only a style preference, send it to human review instead of mechanical grading.

```json
{
  "id": "A-1",
  "case": "case-1",
  "statement": "Every reference link in the report resolves to a non-empty file.",
  "check": "resolve_links_and_check_size",
  "introduced_after_first_output": true
}
```

## 5. Grade and analyze

Grade every assertion for every trial as PASS or FAIL. Quote the smallest output or trace excerpt that proves the result, and include the path or line range so another reviewer can reproduce it.

```json
{
  "assertion": "A-1",
  "configuration": "improved",
  "trial": 1,
  "result": "PASS",
  "evidence": "references/trial-run.md exists and is non-empty"
}
```

Apply these four pattern-analysis rules:

1. Drop assertions that pass in both configurations; they measure no improvement.
2. Investigate assertions that fail in both configurations; the assertion may be broken or the case may be too hard.
3. Study assertions that pass only with the improved version; they are the clearest evidence of capability gain.
4. Tighten instructions when the same case passes inconsistently across runs; inconsistency usually signals ambiguity, not luck.

Compare the improved and baseline scorecards, then explain which flips matter to the user's task. Record cost and latency deltas beside the capability evidence rather than hiding them.

## 6. Read execution traces

Read traces step by step, not only the final answer. Mark a step when the agent:

- tries several approaches because the instruction lacks a default or a success condition;
- follows a rule that does not apply to the case;
- spends tokens loading or explaining general knowledge it already has;
- branches through an option menu instead of choosing a default;
- skips a validator, repeats a failed action, or cannot identify the expected value.

Map each recurring correction to one focused instruction or Gotcha in SKILL.md. Do not paste the failed prompt's keywords into the description; generalize the category of failure. Re-run the affected case after the change and keep the baseline unchanged.

## Trigger eval when description changed

Run a compact trigger eval whenever the improvement changes `description`. Build a labelled query set of roughly 20 realistic queries: about half `should_trigger: true` and half `should_trigger: false`. Positives should vary in phrasing, explicitness, detail, and step count; negatives should be near-misses that share keywords but need another skill.

Run each query several times in a fresh context and compute its trigger rate as triggered runs divided by total runs. Treat roughly 0.5 as the useful decision threshold, then inspect borderline cases rather than tuning to one lucky run.

Keep a fixed split of about 60% train and 40% validation. Tune only on train, stop after roughly five iterations, and select the iteration with the best validation pass rate, which may not be the last one. Re-check that the description remains within the 1024-character limit after every iteration. Generalize failed queries into category-level wording to avoid keyword overfitting.

```json
{
  "query_id": "q-07",
  "query": "Compare two versions of a skill and explain which instructions should change.",
  "should_trigger": true,
  "runs": 4,
  "triggered": 3,
  "trigger_rate": 0.75,
  "split": "validation"
}
```

## Cross-configuration coverage

A skill augments the model and harness running it, so an improvement can help one configuration and hurt another. Add this step only when the target skill runs in more than one configuration; otherwise state that a single configuration is in scope.

Re-run the smallest revealing subset — usually two cases plus any borderline trigger query — in each reasoning strength and each agent implementation the skill must support. Do not re-run everything. Then read failures by configuration instead of averaging them:

- Fails only on a lower-reasoning configuration: the change relies on inference the model does not perform. Restore the missing step, default, or worked example.
- Fails only on a higher-reasoning configuration: the change over-constrains or over-explains, so the model follows instructions that do not apply. Cut them; this is a context-cost regression under Hard Rule 7.
- Fails only on one agent implementation: the change assumed a tool, path, or runtime behavior that implementation lacks. Describe the action generically and move the real requirement into `compatibility`.

Keep a single instruction set that works everywhere; fork per configuration only when a documented environment requirement makes one instruction impossible. Record which configurations were exercised — an untested configuration is an unknown, not a pass.

## Evidence record

Finish with a compact record containing the snapshot, cases, assertion matrix, trace findings, and deltas. State whether the improved version gained capability, spent more or fewer tokens, and changed latency. If a trial was infeasible, state the concrete blocker and provide the static evidence used instead; do not claim a pass without evidence.
