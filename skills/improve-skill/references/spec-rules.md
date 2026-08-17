# Agent Skills Specification Rules

Validation checklist derived from the Agent Skills specification. Run this checklist during Phase 5 (Verify) or whenever spec compliance needs confirmation.

## Contents

- Frontmatter validation
- Directory structure
- Content rules
- Quality recommendations
- Validation outcome

## A. Frontmatter Validation

### name (Required)

- [ ] Present in YAML frontmatter between `---` markers
- [ ] 1-64 characters long
- [ ] Contains only lowercase letters (a-z), numbers (0-9), and hyphens (-)
- [ ] Does not start with a hyphen
- [ ] Does not end with a hyphen
- [ ] Contains no consecutive hyphens (--)
- [ ] Matches the parent directory name exactly

### description (Required)

- [ ] Present in YAML frontmatter
- [ ] 1-1024 characters long
- [ ] Non-empty (not just whitespace)
- [ ] Describes what the skill does
- [ ] Describes when to use it
- [ ] Includes specific keywords that help agents identify relevant tasks

### license (Optional)

- [ ] If present: short license name or reference to bundled license file
- [ ] Recommendation: keep it brief (e.g., "MIT", "Apache-2.0", "Proprietary. See LICENSE.txt")

### compatibility (Optional)

- [ ] If present: 1-500 characters
- [ ] Only included when the skill has specific environment requirements
- [ ] Describes: intended product, required system packages, network access, etc.

### metadata (Optional)

- [ ] If present: mapping of string keys to string values
- [ ] Key names are reasonably unique to avoid conflicts
- [ ] Common fields: `author`, `version`

### allowed-tools (Optional, Experimental)

- [ ] If present: space-delimited list of tool names
- [ ] Treat as optional metadata only; support and behavior vary, so do not infer availability, permissions, discovery, or runtime semantics from it

## B. Directory Structure

- [ ] Skill lives in its own named directory
- [ ] `SKILL.md` exists at the root of the skill directory
- [ ] Directory name matches the `name` field in frontmatter
- [ ] Optional subdirectories follow convention:
  - `scripts/` — executable code
  - `references/` — additional documentation
  - `assets/` — templates, images, data files
- [ ] No deeply nested reference chains: links resolve at most one level from SKILL.md; reference files do not require another reference to be loaded

## C. Content Rules

- [ ] SKILL.md body is valid Markdown after the frontmatter
- [ ] SKILL.md is under 500 lines (recommended)
- [ ] SKILL.md estimated under 5000 tokens (recommended, ~4 chars/token)
- [ ] All file references use paths relative to the skill root with forward-slash (`/`) separators; do not use absolute or backslash paths
- [ ] All file references resolve to existing files
- [ ] Detailed reference material is split into separate files, not inlined
- [ ] Progressive disclosure structure: metadata (~100 tokens) → instructions (<5000 tokens) → resources (on demand)

## D. Quality Recommendations

These are not strict spec rules, but strongly recommended:

- [ ] Description front-loads the key use case (first 50 chars should convey purpose)
- [ ] Description stays under 250 characters for efficient listing display
- [ ] Scripts in `scripts/` are self-contained or clearly document dependencies
- [ ] Scripts include helpful error messages for common failure modes
- [ ] Reference files are focused and individually useful (not monolithic)
- [ ] Instructions include step-by-step guidance
- [ ] Common edge cases are documented
- [ ] Inputs and expected outputs are explicitly described

## E. Validation Outcome

For each check:

- **PASS**: Condition is fully met
- **WARN**: Condition is partially met or a recommendation is not followed
- **FAIL**: Required condition is not met (blocks spec compliance)

Only items in sections A-C can produce FAIL outcomes. Section D items produce WARN at most.

A skill is **spec-compliant** when all A-C checks pass. A skill is **recommended-compliant** when all A-D checks pass.
