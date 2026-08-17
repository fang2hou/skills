# Scoring Rubric

Detailed criteria for each quality dimension. Score 1-5 per dimension, max 40 total.

## Contents

- General scale and thresholds
- Dimensions 1–2: specification and description
- Dimension 3: context economy and progressive disclosure
- Dimension 4: structural clarity
- Dimension 5: instruction quality and calibration
- Dimension 6: guardrails and validation
- Dimension 7: composability and script I/O
- Dimension 8: cross-platform compatibility
- Scoring guidance

## General Scale

| Score | Meaning                                           |
| ----- | ------------------------------------------------- |
| 1     | Missing or fundamentally broken                   |
| 2     | Present but inadequate                            |
| 3     | Acceptable — meets basic requirements             |
| 4     | Good — follows best practices                     |
| 5     | Excellent — exemplary, could serve as a reference |

## Dimension 1: Spec Compliance

Checks conformance to the Agent Skills specification.

| Score | Criteria                                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------------------- |
| 1     | No frontmatter, or both `name` and `description` missing                                                            |
| 2     | Frontmatter present but `name` or `description` violates spec rules                                                 |
| 3     | Valid `name` + `description`. Name matches directory name                                                           |
| 4     | Score 3 + optional fields (`license`, `compatibility`, `metadata`) used appropriately                               |
| 5     | Score 4 + metadata includes version + directory structure follows spec conventions (references/, scripts/, assets/) |

**Spec rules**: name is 1-64 chars, lowercase + hyphens only, no leading/trailing/consecutive hyphens, must match directory name. Description is 1-1024 chars, non-empty.

## Dimension 2: Description Quality

How well the description enables agent discovery and user understanding.

| Score | Criteria                                                                        |
| ----- | ------------------------------------------------------------------------------- |
| 1     | Missing or empty description                                                    |
| 2     | Vague or too short (e.g., "Helps with X")                                       |
| 3     | Describes what the skill does but not when to use it                            |
| 4     | Describes WHAT + WHEN + includes relevant trigger keywords                      |
| 5     | Score 4 + under 250 chars for listing efficiency + front-loads the key use case |

**Good**: "Extracts text from PDFs, fills forms, merges files. Use when working with PDF documents or when the user mentions forms or document extraction."

**Bad**: "Helps with PDFs."

## Dimension 3: Context Economy & Disclosure

How well the skill adds only missing context, keeps scope focused, and layers detail for on-demand loading.

| Score | Criteria                                                                                                                                                                                                |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Massive or monolithic content (>1000 lines), repeats general knowledge the agent already has, or relies on deep reference chains                                                                        |
| 2     | SKILL.md >500 lines or over-comprehensive instructions make the agent pursue steps that do not apply; references are poorly scoped or chained                                                           |
| 3     | SKILL.md <500 lines but includes content that could be split, explains agent-known material, or lacks a visible context-economy decision                                                                |
| 4     | Content is scoped to what the agent lacks; detailed material is in focused references linked directly from SKILL.md and loaded on demand; no reference chain exceeds one level                          |
| 5     | Score 4 + visibly applies the test “Would the agent get this wrong without this instruction?” to retain only high-signal content, with concise progressive disclosure and no over-comprehensive detours |

**Context-economy test**: For each instruction, ask whether the agent would get it wrong without the instruction. Remove explanations of broadly known concepts unless they prevent a demonstrated failure. References may be linked one level deep from SKILL.md, never through a chain of references.

**Token guidance**: Estimate ~4 characters per token. 500 lines at ~60 chars/line is ~7500 tokens, so keep SKILL.md under 500 lines and target under 5000 tokens; load detailed criteria on demand.

## Dimension 4: Structural Clarity

How well-organized and navigable the skill content is.

| Score | Criteria                                                                                 |
| ----- | ---------------------------------------------------------------------------------------- |
| 1     | Unstructured prose, no headings                                                          |
| 2     | Some headings but disorganized or inconsistent hierarchy                                 |
| 3     | Clear headings with logical section order                                                |
| 4     | Score 3 + consistent heading hierarchy + tables for structured data                      |
| 5     | Score 4 + sections follow a standard pattern (see below) + navigation aids to references |

**Standard section order** (not all required, but maintain this order when present):

1. Purpose / Description
2. When to Use
3. Required Tools / Prerequisites
4. Hard Rules / Constraints
5. Inputs
6. Workflow / Instructions
7. Verification
8. Output Contract
9. Failure Handling
10. References

## Dimension 5: Instruction Quality & Calibration

How actionable, purposeful, and appropriately specific the instructions are.

| Score | Criteria                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | No actionable instructions                                                                                                                                                                                                                                                                                                                                                                               |
| 2     | Instructions are vague, or stack rigid directives without rationale; no usable defaults, procedure, or success signal                                                                                                                                                                                                                                                                                    |
| 3     | Step-by-step procedures with clear actions and a reasonable default approach                                                                                                                                                                                                                                                                                                                             |
| 4     | Score 3 + calibration matches specificity to fragility (high freedom for tolerant choices, low freedom for fragile operations), explains WHY, chooses defaults instead of menus, teaches reusable procedures over one-off declarations, uses consistent terminology, avoids time-sensitive rules, and includes applicable Gotchas in SKILL.md, output templates, progress checklists, or worked examples |
| 5     | Score 4 + every fragile step has explicit inputs, outputs, validation, and edge-case criteria; WHY-bearing guidance replaces directive stacking, and the instruction patterns are complete, concise, and demonstrably usable                                                                                                                                                                             |

**Key test**: Could a capable agent execute each step unambiguously without guessing, while retaining freedom where variation is safe?

## Dimension 6: Guardrails & Validation

How well the skill prevents errors, validates work, handles failures, and maintains boundaries.

| Score | Criteria                                                                                                                                                                                                                                                                                                          |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | No error handling, constraints, safety measures, or validation                                                                                                                                                                                                                                                    |
| 2     | Basic error mentions (“if X fails, stop”) without a recovery or validation procedure                                                                                                                                                                                                                              |
| 3     | Explicit error handling for known failure modes and at least one concrete success check                                                                                                                                                                                                                           |
| 4     | Score 3 + validation loops (do → run a validator/checklist → fix → repeat), plan-validate-execute for batch or destructive operations, escalation paths, “never do” constraints, and fallback strategies                                                                                                          |
| 5     | Score 4 + gate checkpoints, auto-recovery, and regression guards; when `scripts/` ships, scripts are non-interactive, give helpful errors naming the problem and expected values, solve the task rather than defer it, contain no unexplained magic constants, and provide `--dry-run` for destructive operations |

**Escalation model**: Define when to stop and ask the user versus when to auto-recover. A validator may be a script or a focused reference checklist.

## Dimension 7: Composability & Script I/O

How well the skill composes with other skills and handles repeated invocations and tool/script boundaries.

| Score | Criteria                                                                                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Hidden state, undocumented assumptions, or output that cannot be consumed reliably                                                                                  |
| 2     | Mostly stateless but has implicit dependencies, mixed human/data output, or undocumented failure signals                                                            |
| 3     | Stateless, safe to re-run, and has a clear input/output contract                                                                                                    |
| 4     | Score 3 + tool/script output is structured and machine-readable; data is on stdout, diagnostics are on stderr, and distinct exit codes are documented               |
| 5     | Score 4 + operations are idempotent under retry, output size is predictable or paginated, and downstream consumers can rely on stable schemas and failure semantics |

## Dimension 8: Cross-Platform Compatibility

How portable and implementation-neutral the skill is across agent environments.

| Score | Criteria                                                                                                                                                                                                         |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Heavily tied to one platform's proprietary behavior throughout                                                                                                                                                   |
| 2     | Some platform-specific features without fallbacks, portable path rules, or clear boundaries                                                                                                                      |
| 3     | Core instructions are agent-agnostic, with limited optional platform hints and forward-slash relative paths                                                                                                      |
| 4     | Fully standard-compliant; platform features and `allowed-tools` are clearly marked optional and experimental, with no assumed runtime behavior; all references use forward-slash relative paths                  |
| 5     | Score 4 + real environment requirements are documented in `compatibility`, optional metadata is treated as non-authoritative, and portability is tested or explicitly documented across multiple implementations |

**Key rule**: Describe WHAT to do, not HOW a specific agent does it. Do not infer tool availability, permissions, discovery, or runtime semantics from `allowed-tools`; it is optional experimental metadata only. Use paths relative to the skill root with `/` separators.

## Scoring Guidance

- Score based on evidence from reading the actual skill content
- When in doubt, score lower — it creates clearer improvement targets
- A skill scoring 30+/40 is production quality
- A skill scoring 35+/40 is exemplary and could serve as a reference
- Focus optimization effort on the lowest-scoring dimensions first
