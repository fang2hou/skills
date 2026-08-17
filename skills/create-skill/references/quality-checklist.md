# Quality Checklist

Full validation checklist for Agent Skills. Run during Phase 3 (Validation).

## A. Frontmatter Validation

### name (Required)

- [ ] Present in YAML frontmatter between `---` markers
- [ ] 1-64 characters long
- [ ] Contains only lowercase letters (a-z), numbers (0-9), and hyphens (-)
- [ ] Does not start or end with a hyphen
- [ ] Contains no consecutive hyphens (--)
- [ ] Matches the parent directory name exactly

### description (Required)

- [ ] Present in YAML frontmatter
- [ ] 1-1024 characters long
- [ ] Non-empty (not just whitespace)
- [ ] Describes what the skill does
- [ ] Describes when to use it
- [ ] Includes specific keywords for agent matching

### Optional fields

- [ ] `license`: Short name or file reference (if present)
- [ ] `compatibility`: 1-500 chars, only if specific requirements exist (if present)
- [ ] `metadata`: String keys to string values (if present)

## B. Directory Structure

- [ ] Skill lives in its own named directory
- [ ] `SKILL.md` exists at the root of the skill directory
- [ ] Directory name matches the `name` field in frontmatter
- [ ] Optional subdirectories follow convention: `scripts/`, `references/`, `assets/`
- [ ] No deeply nested reference chains (max 1 level from SKILL.md)

## C. Content Quality

- [ ] SKILL.md body is valid Markdown after the frontmatter
- [ ] SKILL.md is under 500 lines
- [ ] SKILL.md estimated under 5000 tokens (~4 chars/token)
- [ ] All file references use relative paths from the skill root directory
- [ ] All file references resolve to existing files
- [ ] No placeholder or TODO sections remain
- [ ] No instruction lacks a condition, a default, or a verifiable result (signal phrases: "handle appropriately", "as needed", "ensure quality", "follow best practices")
- [ ] Every section contains actionable content

## D. Instruction Quality

- [ ] Workflow steps have clear actions with expected results
- [ ] Inputs are documented with types and examples
- [ ] Success criteria are explicitly defined
- [ ] Error/failure modes have defined recovery actions
- [ ] Gotchas section lists non-obvious domain facts

## E. Progressive Disclosure

- [ ] Detailed reference material is split into `references/`
- [ ] SKILL.md links to references with context (when to load each file)
- [ ] Reference files are focused and individually useful (not monolithic)
- [ ] Estimated token count: SKILL.md ~100-5000, references loaded on demand

## F. Imported Criteria Policy

The following new checks are mandatory workflow requirements and can be **FAIL**:

- [ ] **No time-sensitive content:** instructions do not depend on dates or temporary API behavior; superseded guidance is clearly labelled as deprecated/old patterns
- [ ] **Forward-slash relative paths:** every path uses `/` and is relative to the skill root
- [ ] **Gotchas in SKILL.md:** non-obvious facts that affect execution are visible in the navigation hub
- [ ] **Trial-run evidence recorded:** the output states what was run, the with-skill and baseline outcomes, and what changed as a result
- [ ] **Script design (only when `scripts/` exists):** scripts meet the non-interactive, interface, robustness, and packaging requirements in `references/script-design.md`

The following imported checks are quality recommendations and produce **WARN** at most:

- [ ] **Context economy:** each line adds knowledge the agent lacks; test “would the agent get this wrong without this?”
- [ ] **Calibration:** sections with different fragility use high freedom or low freedom instructions appropriately
- [ ] **Defaults, not menus:** one default approach is selected wherever alternatives exist
- [ ] **Consistent terminology:** one term is used for each concept throughout the skill and references

Sections A-C and the mandatory checks above can FAIL. Sections D-E and the advisory checks
above produce WARN at most. Apply the script check only when the skill ships `scripts/`.

## Validation Outcome

- **PASS**: Condition fully met
- **WARN**: Recommendation not followed (non-blocking)
- **FAIL**: Required condition not met (must fix before delivering)

Sections A-C and mandatory F checks can FAIL. Sections D-E and advisory F checks produce
WARN at most.

A skill is **spec-compliant** when all A-C checks pass.
A skill is **workflow-complete** when all mandatory F checks pass.
A skill is **recommended-compliant** when all A-F checks pass.
