# Agent Skills Specification Quick Reference

Condensed rules from the [Agent Skills specification](https://agentskills.io/specification). Consult this during frontmatter authoring and validation.

## Frontmatter Fields

### `name` (Required)

- 1-64 characters
- Lowercase letters (a-z), numbers (0-9), and hyphens (-) only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (--)
- **Must match the parent directory name exactly**

Valid: `csv-analyzer`, `pdf-processing`, `code-review`
Invalid: `CSV-Analyzer` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive)

### `description` (Required)

- 1-1024 characters, non-empty
- Describe WHAT the skill does AND WHEN to use it
- Include specific keywords that help agents identify relevant tasks
- Recommended: stay under 250 characters for efficient listing

Good: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`
Poor: `Helps with PDFs.`

### `license` (Optional)

- Short license name or reference to a bundled license file
- Example: `MIT`, `Apache-2.0`, `Proprietary. See LICENSE.txt`

### `compatibility` (Optional)

- 1-500 characters
- Only include if the skill has specific environment requirements
- Describe: intended product, required system packages, network access, etc.
- Example: `Requires git, docker, jq, and access to the internet`

### `metadata` (Optional)

- Mapping of string keys to string values
- Use reasonably unique key names to avoid conflicts
- Common fields: `author`, `version`

### `allowed-tools` (Optional, Experimental)

- Space-separated list of tool names
- Support varies between agent implementations
- This field is optional and experimental; do not assume it grants access, restricts access, or changes runtime behavior
- Example: `Bash(git:*) Bash(jq:*) Read`

## Directory Structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: additional documentation
└── assets/           # Optional: templates, images, data files
```

## Content Rules

- SKILL.md body is valid Markdown after the frontmatter
- SKILL.md recommended under 500 lines and ~5000 tokens (~4 chars/token)
- All file references use forward-slash relative paths from the skill root, even on Windows
- Keep references one level deep from SKILL.md (avoid nested reference chains)
- Detailed reference material belongs in separate files, not inlined

## Progressive Disclosure

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens): Full SKILL.md body loaded when skill is activated
3. **Resources** (on demand): Files in `scripts/`, `references/`, `assets/` loaded only when needed

Tell the agent WHEN to load each file: "Read `references/api-errors.md` if the API returns a non-200 status code."

## Validation

Run `skills-ref validate ./my-skill` if the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) tool is available.
