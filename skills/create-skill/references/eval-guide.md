# Evaluation Guide

Contents:

- [Evaluation terms](#evaluation-terms)
- [Trigger evals](#trigger-evals)
- [Output-quality evals](#output-quality-evals)
- [Reading traces and iterating](#reading-traces-and-iterating)
- [Cross-model and cross-agent coverage](#cross-model-and-cross-agent-coverage)

## Evaluation terms

- A **trial run** executes the skill on a realistic task in a fresh context to gather
  evidence.
- A **baseline run** uses the same prompt without the skill for a new skill, or a snapshot
  of the previous version when improving an existing skill.
- An **assertion** is one objectively checkable statement about an output.
- A **trigger eval** tests whether the description activates for the right requests.
- An **output-quality eval** tests whether the activated skill produces the required result.

Record the prompt, context, configuration, elapsed time, token or output cost when
available, and the exact evidence used for every judgment. Keep the query and test splits
fixed so iterations are comparable.

## Trigger evals

### Build the query set

Create about 20 realistic queries: roughly half labelled `should_trigger: true` and half
labelled `should_trigger: false`. Positives should vary in phrasing, explicitness, detail,
and step count. Include valuable cases where the skill helps but the connection is indirect.
Negatives should be near misses: they share words or subject matter with the skill but
actually require another skill or no skill.

Do not make negatives random unrelated prompts. A description that rejects an unrelated
prompt but activates on every keyword match has not been tested meaningfully.

A plain JSON query set can look like this:

```json
[
  {
    "id": "p01",
    "query": "Turn these ad-hoc instructions into a reusable skill",
    "should_trigger": true
  },
  {
    "id": "p02",
    "query": "Review the existing skill and tighten its scope",
    "should_trigger": false
  },
  {
    "id": "p03",
    "query": "I need a new skill for validating release notes",
    "should_trigger": true
  },
  { "id": "p04", "query": "Write release notes for this commit", "should_trigger": false }
]
```

Expand the small example to the target set. Label the reason for each near miss in a
separate note so a failure can be generalized by category rather than by copying keywords.

### Measure nondeterministic activation

Run every query several times in a fresh context. Record each activation as `1` or `0` and
compute a trigger rate:

```text
trigger_rate(query) = activations / repeated_runs
```

Use an approximate 0.5 threshold as a decision signal, not as proof of correctness. Review
false positives and false negatives separately; a high average can hide a dangerous near
miss.

### Fixed train/validation iteration

Split the labelled queries once into approximately 60% train and 40% validation. Keep the
split fixed. Tune the description only on train, then evaluate the candidate on validation.
Select the iteration with the best validation pass rate; it may not be the last iteration.
Stop after roughly five iterations unless a concrete failure justifies another pass.

After each iteration:

1. Inspect failed query categories, not just their exact words.
2. Make the smallest description change that addresses a category.
3. Re-run train and then validation using the fixed split.
4. Record pass rates and the selected iteration.

Re-check the 1024-character description limit after every iteration. Optimization tends to
make descriptions grow; trim repetition and move detail into the body.

### Avoid overfitting

Do not paste a failed query into the description. Generalize the underlying category, such
as “indirect requests to create a reusable workflow,” and add one representative phrase at
most. Preserve near-miss negatives while changing the description; otherwise activation
appears to improve only because the test became easier.

## Output-quality evals

### Test-case anatomy

Each case includes a realistic prompt, a human-readable expected output, optional input
files or fixtures, and assertions added after seeing the first run's output. The expected
output explains required behavior and boundaries; it is not an exact answer string.

```json
[
  {
    "id": "case-01",
    "prompt": "Create a skill that validates JSON configuration files and reports errors.",
    "expected_output": "A complete skill with valid frontmatter, a scoped workflow, and an error report that names the invalid field.",
    "input_files": ["fixtures/config.json"],
    "assertions": []
  }
]
```

Run the first case before finalizing assertions. Add assertions based on observable failure
modes, then keep only checks that are objective and reproducible.

### Write objective assertions

Good assertions can be checked mechanically or by quoting a precise output location:

```json
[
  { "id": "a1", "statement": "The frontmatter name equals the directory name." },
  { "id": "a2", "statement": "Every reference link resolves to a non-empty file." },
  { "id": "a3", "statement": "The error report identifies the invalid field and expected type." }
]
```

Weak assertions are “the output is good,” “the prose is polished,” or brittle requirements
for an exact phrase when equivalent wording is valid. Keep style, tone, and polish for
human review rather than pretending they are mechanical assertions.

### Compare skill and baseline

Run every test case twice with the skill and twice as a baseline run. For a new skill, the
baseline has no skill loaded. For an improvement, the baseline uses the previous-version
snapshot. Use equivalent fresh contexts and inputs.

Grade each assertion `PASS` or `FAIL` and quote the evidence:

```text
case-01 / a2: PASS — `references/spec-quickref.md` is linked and non-empty.
case-01 / a3: FAIL — output says “invalid config” but names no field or expected type.
```

Record elapsed time and token or output cost for each run. Report the delta so the skill's
benefit is weighed against the context and latency it costs.

### Analyze assertion patterns

Apply all four rules after comparison:

1. **Pass in both configurations:** Drop the assertion; it measures no skill-specific value.
2. **Fail in both configurations:** Investigate the case or assertion. It may be broken,
   underspecified, or too difficult; do not claim the skill caused the failure.
3. **Pass only with the skill:** Study this evidence. It identifies where the skill adds
   value and which instruction deserves preservation.
4. **Inconsistent across repeated runs:** Tighten the relevant instruction or assertion.
   Inconsistency usually signals ambiguity, not luck to average away.

## Reading traces and iterating

Read the execution trace, not only the final artifact. Wasted or unproductive steps usually
mean the instructions are too vague, include rules that do not apply, or offer too many
options without a default. Each human correction is evidence: turn it into a Gotchas entry
in `SKILL.md` or an instruction fix, then repeat the trial run.

If the baseline already succeeds, state that result explicitly and consider whether the skill
adds enough value to justify its context cost. Do not add instructions merely to make the
skill look different. Keep the iteration that has the strongest validation evidence, not
necessarily the newest text.

## Cross-model and cross-agent coverage

A skill only augments the model and harness executing it, so its effectiveness varies with
both. Add this step only when the skill will actually run in more than one configuration;
a single-configuration skill needs no extra runs.

1. List the configurations the skill must support: each reasoning strength you expect to run
   it on, and each agent implementation whose tools, discovery, or permissions differ.
2. Re-run the smallest revealing subset in every configuration — typically two output-quality
   cases plus any trigger query whose rate sat near the threshold. Do not re-run the whole set.
3. Compare failures by configuration rather than averaging them:
   - Fails only on a lower-reasoning configuration: the instruction relies on inference the
     model does not perform. Add the missing step, default, or worked example.
   - Fails only on a higher-reasoning configuration: the skill likely over-constrains or
     over-explains, so the model pursues instructions that do not apply. Cut them.
   - Fails only on one agent implementation: the skill assumes a tool, path, or runtime
     behavior that implementation does not provide. Describe the action generically and move
     the real requirement into `compatibility`.
4. Keep one instruction set that works everywhere. Fork guidance per configuration only when a
   documented environment requirement makes a single instruction impossible.

Record which configurations were exercised. An untested configuration is an unknown, not a pass.
