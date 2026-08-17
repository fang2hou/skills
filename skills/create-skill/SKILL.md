---
name: create-skill
description: >
  Creates spec-compliant Agent Skills from requirements through validated delivery, including intent analysis, domain research, and SKILL.md authoring. Use when creating, drafting, or scaffolding a new Agent Skill.
license: MIT
compatibility: Requires file write access to create skill files. Works with any agent supporting the Agent Skills standard.
metadata:
  author: fang2hou
  version: "2.2"
  sources: "Agent Skills specification (agentskills.io); first-principles skill creation methodology"
---

# Create Skill

End-to-end workflow for creating spec-compliant, production-quality Agent Skills. Optimized for shortest path from user intent to working skill.

## When to Use

- Creating a new Agent Skill from scratch — phrases include “create a skill” and “new skill”
- Scaffolding a skill from a concept or requirement — phrases include “build a skill” and “make a skill”
- Converting ad-hoc agent instructions into a reusable skill, or invoking this skill by name

## When NOT to Use

- Improving an existing skill (use improve-skill instead)
- General code generation unrelated to Agent Skills
- Editing skills without understanding its intent

## Inputs

| Input               | Required | Format               | Example                                   |
| ------------------- | -------- | -------------------- | ----------------------------------------- |
| Invocation argument | No       | Skill name or brief  | `csv-analyzer`, "a skill that parses CSV" |
| User context        | Yes      | Requirements, domain | "Must use pandas, output markdown tables" |

**Cross-platform note**: Clients that expose an invocation argument (for example a `$ARGUMENTS` placeholder) pass the skill name or brief through it. If no such argument is available or it does not resolve to a skill concept, ask the user what skill to create before proceeding.

## Hard Rules

1. **Spec compliance**: All output must conform to the Agent Skills specification.
2. **Domain-grounded**: Never generate skill content from generic knowledge alone. Gather project-specific or domain-specific context first; skipping this produces a generic, useless skill.
3. **No empty sections**: Every section must contain actionable content. Remove placeholders.
4. **Progressive disclosure**: SKILL.md under 500 lines. Move detailed material to `references/`.
5. **Validate before delivering**: Run the quality checklist before presenting the final skill.
6. **No vague instructions**: Every instruction must state WHAT to do, under WHICH condition, and HOW to verify the result. Phrases such as "handle appropriately", "as needed", "ensure quality", or "follow best practices" are detection signals: rewrite the instruction unless the surrounding text already supplies the condition, the default, and a verifiable outcome.

## Key Principles

- **Context economy**: Add what the agent lacks and omit what it already knows. Test every line: “Would the agent get this wrong without this instruction?”
- **Coherent scope units**: Encapsulate one coherent unit of work that composes with other skills. Split work that is too narrow or too broad.
- **Calibrate to fragility**: Use high freedom (goals, heuristics, and WHY) when approaches are valid and variation is safe; use low freedom (exact steps) when work is fragile or destructive. Explain why instead of stacking rigid directives where variation is safe.
- **Moderate detail**: Prefer concise stepwise guidance plus one working example over exhaustive documentation; over-comprehensive skills make agents pursue irrelevant instructions.
- **Provide defaults, not menus**: Pick one recommended approach and mention alternatives briefly as an escape hatch.
- **Favor procedures over declarations**: Teach HOW to approach a class of problems, not WHAT to produce for one instance.
- **Consistent terminology**: Choose one term per concept and reuse it verbatim across the skill and references.
- **No time-sensitive content**: State durable rules; put superseded guidance in a clearly labelled deprecated or old-patterns section.
- **Front-load critical content**: The first 200 lines should contain everything needed for basic execution.

## Workflow

### Phase 0: Intent Analysis and Requirements Capture

**Critical node — the quality of the entire skill depends on getting this right.**

Do not jump to structure or writing. Extract only intent details that change the skill's scope, instructions, or validation.

**Step 1: Analyze user intent.** Capture:

- **Outcome:** What should the skill reliably enable beyond the surface request?
- **Audience/context:** Who will use it, under what task conditions, and what domain knowledge do they lack?
- **Success:** What observable result proves the skill worked?
- **Boundary:** What should this skill explicitly not attempt?

**Step 2: Capture requirements.**

1. **Purpose**: What problem does it solve? One sentence that would make a stranger understand the value.
2. **Triggers**: When should an agent activate this skill? List 3-5 realistic user prompts — these are the phrases that will cause the skill to be loaded, so they must match how users actually talk.
3. **Scope boundary**: What is IN scope? What is explicitly OUT of scope? Scope creep is the #1 cause of bloated skills.
4. **Domain type**: Workflow (step-by-step process), Expertise (domain knowledge), or Hybrid?

Output as a Requirements Card:

```
Intent: [WHY the user wants this — the real goal]
Purpose: [one sentence]
Domain: [workflow | expertise | hybrid]
Triggers: [3-5 example user prompts]
In Scope: [list]
Out of Scope: [list]
```

**Edge cases**:

- If the skill name already exists in the workspace, warn the user and confirm: overwrite, version, or pick a new name.
- If requirements are contradictory (e.g., "expertise" domain but trigger list implies "workflow"), flag the conflict and ask for clarification.
- If the user provides only a tool name (e.g., "make a jq skill"), treat it as a starting concept — still analyze intent before designing.

**Gate 0** — Proceed only when ALL are true:

- [ ] Intent is understood (you can articulate WHY, not just WHAT)
- [ ] Purpose is specific (not "helps with X")
- [ ] At least 3 trigger scenarios documented
- [ ] Scope boundary explicitly defined
- [ ] No name collision with existing skills (or user confirmed overwrite)

_If gate fails_: Ask the user clarifying questions. Do not assume. Do not guess. If no user is reachable, record each unanswered question, proceed with the most defensible assumption, and label those assumptions in the delivered output.

### Phase 1: Context Gathering

**Critical node — the #1 cause of bad skills is skipping this phase.**

You MUST gather knowledge the target agent would not have on its own. The agent using this skill will only be as good as the knowledge you embed in it.

**Mandatory actions — attempt each one and record the observable evidence (or why the source class is unavailable):**

1. **Codebase exploration**: Search relevant files, patterns, conventions, and APIs; record the search scope, queries, and paths or findings. If no related codebase is available, record that fact and why.
2. **Documentation lookup**: Read official documentation and at least one real-world example for each external tool or library involved; record the URLs or identifiers and the usage detail extracted. If none is involved or docs are inaccessible, record the reason.
3. **Existing skill analysis**: Read 1–2 comparable skills in the workspace; record their paths and conventions reused. If no comparable skill exists, record the search scope and why the class is unavailable.
4. **High-signal expertise sources**: Read available transcripts or corrections, runbooks, style guides, API specs or schemas, review comments, version-control fixes, or failure/resolution records; record source identifiers and the concrete lesson. If none is accessible, list the classes checked and why.
5. **Gotchas hunt**: Search gathered sources for non-obvious constraints and record each gotcha with its source and consequence; if none is found, record exactly “No domain-specific gotchas identified during research” and what was checked.

**Sources priority:**

1. Hands-on corrections, real failure cases, and version-control fixes
2. Existing project files, runbooks, style guides, API specs, and schemas
3. Official documentation and code review comments
4. User-provided knowledge and corrections
5. Real-world examples from open-source projects

**Edge cases**:

- If no codebase or external docs are available and the user cannot provide domain expertise, proceed with a disclaimer: "This skill was authored from general knowledge. Review and update with domain-specific details before production use."
- If context gathering reveals the task is too broad for a single skill (e.g., "build a CI/CD pipeline"), suggest splitting into multiple focused skills.

**Gate 1** — Proceed only when ALL are true:

- [ ] At least one high-signal source consulted (or disclaimer added)
- [ ] Gotchas hunt performed; findings recorded, or "no domain-specific gotchas identified during research" stated explicitly
- [ ] Not relying solely on generic knowledge without disclaimer
- [ ] Unavailable source classes recorded

_If gate fails_: You have NOT gathered enough context. Search more. Read more files. Ask the user. Do NOT proceed to Phase 2 with generic knowledge alone.

### Phase 2: Author and Structure

Design the structure AND write the content. These are one activity, not two.

**Step 1: Plan the structure.** Decide:

```
skill-name/
├── SKILL.md          # Always required
├── references/       # Only if SKILL.md would exceed ~300 lines
├── scripts/          # Only if reusable executable logic is needed
└── assets/           # Only if templates/data files are needed
```

Content split:

| Location      | Content                                              |
| ------------- | ---------------------------------------------------- |
| SKILL.md body | Core workflow, hard rules, gotchas, key instructions |
| references/   | Detailed criteria, extended examples, lookup tables  |
| scripts/      | Reusable code the agent would otherwise reinvent     |

#### Calibrate each section

| Freedom level    | Use when                                                               | Instruction shape                                                                       |
| ---------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **High freedom** | Multiple approaches are valid and mistakes are cheap or reversible     | State goals, heuristics, and WHY; let the agent choose the route.                       |
| **Low freedom**  | Work is fragile, destructive, order-dependent, or consistency-critical | Give the exact sequence, command, inputs, and expected result; do not invite variation. |

Most skills mix both levels. Calibrate per section rather than applying one control level to the whole skill.

#### Instruction patterns

Use the pattern that matches the work: **Gotchas**, **output-format template**, **progress checklist**, **validation loop**, **plan-validate-execute**, **worked examples**, or **bundled script**. Load [references/instruction-patterns.md](references/instruction-patterns.md) when choosing patterns, calibrating freedom, or needing concrete templates.

#### Bundled scripts

Only when the skill will ship `scripts/`, load [references/script-design.md](references/script-design.md) before writing a script; it defines the non-interactive interface, robustness, and packaging requirements.

**Step 2: Write frontmatter.** For complete field rules, see [references/spec-quickref.md](references/spec-quickref.md).

```yaml
---
name: skill-name # Required: lowercase, hyphens, matches directory
description: > # Required: WHAT + WHEN, under 1024 chars
  [What it does]. Use when [trigger scenarios].
license: MIT # Optional
compatibility: ... # Optional: only if specific env requirements exist
metadata: # Optional
  author: ...
  version: "1.0"
---
```

The description field is the MOST IMPORTANT line in the entire skill. It determines whether the skill triggers at all. It must cover both WHAT and WHEN, and include the trigger phrases from Phase 0. For guidance, see [references/description-guide.md](references/description-guide.md).

**Step 3: Write body content.** Use this section order (include only sections with substantive content):

```markdown
# [Skill Title]

One-sentence summary.

## When to Use

- [Trigger scenario 1]
- [Trigger scenario 2]

## When NOT to Use

- [Out-of-scope scenario]

## Inputs

| Input | Required | Format | Example |
| ----- | -------- | ------ | ------- |

## Hard Rules

1. [Non-negotiable constraint]

## Workflow

### Step 1: [Action]

[Instructions with expected result]

## Gotchas

- [Non-obvious fact that defies reasonable assumptions]

## Output Contract

On completion, return:

1. [Expected output]
```

**Anti-vagueness rule** — every instruction must pass this test:
Can someone unfamiliar with this domain read the instruction and know EXACTLY what to do, without guessing?

If the answer is no, rewrite it. Bad examples and their fixes:

- ❌ "Handle errors appropriately" → ✅ "If the API returns non-200, log the status code and retry once with exponential backoff"
- ❌ "Follow the project's conventions" → ✅ "Read `src/auth/middleware.ts` and mirror its error handling pattern"
- ❌ "Optimize if needed" → ✅ "If the function processes >1000 items, use batching with batch size 100"

**Step 4: Create reference files** when SKILL.md would exceed ~300 lines or a detail block is only needed in specific situations. Link with context:

```markdown
See `references/<file>.md` for [purpose, loaded when Y].
```

**Gate 2** — Proceed only when ALL are true:

- [ ] Frontmatter passes all spec validation rules (name matches directory, description has WHAT+WHEN)
- [ ] Body content is actionable (every instruction passes the anti-vagueness test)
- [ ] All file references point to files that EXIST and are NON-EMPTY
- [ ] No placeholder or TODO sections remain
- [ ] SKILL.md is under 500 lines
- [ ] Gotchas section has at least one non-obvious insight, or explicitly states that none were identified during research

_If gate fails_: Fix the specific issue. Remove empty sections, validate frontmatter, create missing files. Maximum 2 correction cycles before escalating to user.

### Phase 3: Validation

Run the quality checklist. For the full checklist, see [references/quality-checklist.md](references/quality-checklist.md).

If the optional `skills-ref` CLI is available, run `skills-ref validate ./skill-name` for automated spec checking; otherwise perform the Quick validation checks below and record that the CLI was unavailable.

**Quick validation**:

1. **Spec compliance**: Frontmatter fields valid, name matches directory, body is Markdown
2. **Description quality**: Covers both WHAT and WHEN, includes trigger keywords from Phase 0
3. **Progressive disclosure**: SKILL.md under 500 lines, references load on demand
4. **No vague instructions**: No banned phrases, every step passes anti-vagueness test
5. **File integrity**: All references resolve to existing, non-empty files

**Success criteria** — the skill is complete when:

- [ ] All spec compliance checks PASS
- [ ] All sections contain actionable content (no placeholders)
- [ ] SKILL.md line count is confirmed under 500
- [ ] Every file reference resolves to a real file
- [ ] A user unfamiliar with the skill can read SKILL.md and understand what it does and how to invoke it

Present results:

```
┌──────────────────────────────┬────────┬──────────────────────────┐
│ Check                        │ Result │ Detail                   │
├──────────────────────────────┼────────┼──────────────────────────┤
│ Frontmatter spec compliance  │ PASS   │ All fields valid         │
│ Name matches directory       │ PASS   │ Both: skill-name         │
│ Description quality          │ PASS   │ WHAT + WHEN covered      │
│ Body under 500 lines         │ PASS   │ N lines                  │
│ File references valid        │ PASS   │ All resolve              │
│ No placeholder sections      │ PASS   │ All sections populated   │
│ Anti-vagueness check         │ PASS   │ No banned phrases        │
└──────────────────────────────┴────────┴──────────────────────────┘
```

**Gate 3** — Proceed to Phase 4 only when ALL true:

- [ ] All spec compliance checks PASS
- [ ] No vague instructions remain
- [ ] All file references resolve

_If gate fails_: Return to Phase 2. Maximum 2 correction cycles before escalating.

### Phase 4: Trial Run and Iterate

Before delivery, run the skill at least once on a realistic task in a **fresh context** — a session with no prior conversation about this skill and no memory of authoring it. Run the same task as a **baseline run** without the skill in a separate fresh context, then compare the outcomes.

1. Read the execution trace, not just the final output. Record wasted steps, ambiguity, and unproductive paths.
2. Turn every correction you had to make into either a Gotchas entry in `SKILL.md` or a specific instruction fix. If the run needed no corrections, state that explicitly.
3. If the baseline already succeeds, say so explicitly and consider whether the skill adds enough value to justify its context cost.
4. Repeat the trial after fixes when the evidence shows the skill is ambiguous or incomplete. For high-stakes skills, skills reused across a team, skills that will run on more than one model or agent implementation, or cases where trigger accuracy matters, load [references/eval-guide.md](references/eval-guide.md).

**Gate 4** — Deliver only when ALL are true:

- [ ] At least one trial run and a baseline run completed in fresh contexts, with outcomes recorded
- [ ] The execution trace was reviewed, not only the final output
- [ ] Every correction observed maps to a Gotchas entry or instruction fix, or the record states that none were needed
- [ ] The comparison states whether the skill adds value; a successful baseline is not hidden

_If gate fails_: Fix the evidence-backed issue, run the trial and baseline again, and update the record. If the baseline remains as good, report that no additional value was demonstrated instead of adding needless instructions.

## Self-Correction Protocol

### Content-Level Rules

| Trigger                                                 | Automatic Action                                                                                                             |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| SKILL.md exceeds 500 lines                              | Split overflow into `references/`                                                                                            |
| Description over 250 chars (hard limit 1024)            | Front-load key use case, move details to body                                                                                |
| `name` doesn't match directory                          | Fix name field to match directory                                                                                            |
| File reference points to void                           | Create the file or remove the reference                                                                                      |
| Vague instruction detected                              | Replace with specific action + expected result                                                                               |
| Empty section found                                     | Remove it entirely — no empty sections ever                                                                                  |
| No gotchas identified                                   | Stop and re-examine the domain. If none are found, explicitly state “No domain-specific gotchas identified during research.” |
| Generic knowledge explains what the agent already knows | Delete or rewrite the line with domain-specific value; apply the context-economy test                                        |
| Time-sensitive statement present                        | Replace it with a durable rule or label superseded material as deprecated/old patterns                                       |
| Multiple options offered with no default                | Choose one default and mention alternatives in one escape clause                                                             |
| Reference chain is deeper than one level                | Link directly from `SKILL.md` or move the detail to a directly linked file                                                   |
| Windows-style backslash path                            | Replace it with a forward-slash relative path                                                                                |
| Script requires interactive input                       | Accept flags, environment variables, or stdin and fail with usage guidance                                                   |

### Workflow-Level Protocol

1. **Drift detection**: After each phase, compare the output against the phase's gate conditions AND the Requirements Card from Phase 0. If the output doesn't serve the stated intent, you've drifted.
2. **Auto-retry**: If a gate fails, attempt the phase-specific correction documented in the gate's "If gate fails" section.
3. **Escalation**: If the same gate fails twice after correction attempts, stop and report to the user with: which gate failed, what correction was attempted, what manual input is needed.
4. **Regression guard**: If a later phase invalidates work from an earlier phase, do NOT silently patch — return to the failing phase.
5. **Scope lock**: If during authoring you discover the skill needs capabilities beyond the Requirements Card, do NOT expand scope. Note them as "Deferred Recommendations" in the output.

## Output Contract

On completion, deliver:

1. **Skill directory**: Complete skill directory with all files created, ready to use
2. **Validation results**: The check/result/detail table shown in Phase 3, one row per check
3. **Design decisions**: Brief summary of structural choices (why this layout, why these sections)
4. **Deferred recommendations**: List of ideas surfaced during creation but not included (scope limit reached, ambiguity unresolved, etc.)
5. **Trial-run evidence**: What realistic task was run, the with-skill and baseline outcomes, what the execution trace revealed, and what changed as a result

Keep the human-readable report as the primary deliverable. When another skill consumes it, preserve these stable fields in this order:

```text
fields (stable order):
1. skill_directory
2. validation_results
3. design_decisions
4. deferred_recommendations
5. trial_run_evidence
```

This skill is **idempotent**: running it again with the same requirements produces an equivalent skill. If a skill directory already exists, it will be overwritten after confirmation.

## References

- [Spec Quick Reference](references/spec-quickref.md) — frontmatter and structure rules
- [Description Guide](references/description-guide.md) — writing descriptions that trigger reliably
- [Quality Checklist](references/quality-checklist.md) — full validation checklist
- [Instruction Patterns](references/instruction-patterns.md) — load when selecting patterns or calibrating instruction freedom
- [Script Design](references/script-design.md) — load before adding `scripts/`
- [Evaluation Guide](references/eval-guide.md) — load for high-stakes skills, team reuse, multi-model or multi-agent targets, or trigger-accuracy evaluation
