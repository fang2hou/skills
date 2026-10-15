# Agent Skills Specification Quick Reference

Condensed rules from the [Agent Skills specification](https://agentskills.io/specification). Consult this during frontmatter authoring and validation.

Contents:

- [Frontmatter fields](#frontmatter-fields)
- [Client constraints](#client-constraints)
- [Client-specific fields](#client-specific-fields)
- [Directory structure](#directory-structure)
- [Content rules](#content-rules)
- [Progressive disclosure](#progressive-disclosure)
- [Validation](#validation)

## Frontmatter Fields

### `name` (Required)

- 1-64 characters
- Lowercase letters (a-z), numbers (0-9), and hyphens (-) only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (--)
- **Must match the parent directory name exactly**

Valid: `csv-analyzer`, `processing-pdfs`, `code-review`
Invalid: `CSV-Analyzer` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive)

### `description` (Required)

- 1-1024 characters, non-empty
- Describe WHAT the skill does AND WHEN to use it
- Include specific keywords that help agents identify relevant tasks
- Recommended: put the key use case in the first sentence and stay near 250 characters, because clients truncate descriptions when the skill listing exceeds its context budget

Good: `Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.`
Poor: `Helps with PDFs.`

### `license` (Optional)

- Short license name or reference to a bundled license file
- Example: `MIT`, `Apache-2.0`, `Proprietary. See LICENSE.txt`

### `compatibility` (Optional)

- 1-500 characters
- Only include if the skill has specific environment requirements; most skills do not need it
- Describe: intended product, required system packages, network access, etc.
- Example: `Requires git, docker, jq, and access to the internet`

### `metadata` (Optional)

- Mapping of string keys to string values
- Use reasonably unique key names to avoid conflicts
- Common fields: `author`, `version`

### `allowed-tools` (Optional, Experimental)

- Space-separated list of tools the skill pre-approves
- Support varies between agent implementations
- Do not assume it grants access, restricts access, or changes runtime behavior; in at least one client it pre-approves tools without a workspace-trust check, so list only tools the skill needs
- Example: `Bash(git:*) Bash(jq:*) Read`

## Client Constraints

Some clients validate more strictly than the specification. Meet these so one skill works everywhere:

- `name` and `description` contain no XML tags or angle brackets.
- `name` does not contain the reserved words `anthropic` or `claude`.
- Upload paths for Claude apps and the Skills API accept only the six spec fields above and reject any other frontmatter key.
- Descriptions are listed under a shared context budget and may be cut short; a description that front-loads its use case survives truncation.

## Client-Specific Fields

Use these only when the user targets that client. In a portable skill, express the same intent in the body (for example a confirmation step) instead.

| Need                                 | Client mechanism                                                                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Run only on explicit user request    | Claude Code and Cursor: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml` |
| Hide from the user's command menu    | Claude Code: `user-invocable: false`                                                                                               |
| Extra trigger text                   | Claude Code: `when_to_use` (counts toward the same truncation cap as `description`)                                                |
| Named arguments                      | Claude Code: `argument-hint`, `arguments`, `$ARGUMENTS`, `$N`                                                                      |
| Run in an isolated subagent          | Claude Code: `context: fork` with `agent`                                                                                          |
| Scope to file paths                  | Cursor and Claude Code: `paths`                                                                                                    |
| Display name, icon, MCP dependencies | Codex: `agents/openai.yaml` beside `SKILL.md`                                                                                      |

Client field sets change between releases. Before relying on one, read the target client's current skills documentation.

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
- Keep references one level deep from SKILL.md (avoid nested reference chains); agents may read nested files only partially
- Give reference files over 100 lines a contents list at the top
- Detailed reference material belongs in separate files, not inlined

## Progressive Disclosure

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens): Full SKILL.md body loaded when skill is activated
3. **Resources** (on demand): Files in `scripts/`, `references/`, `assets/` loaded only when needed; scripts can run without their source entering context

Tell the agent WHEN to load each file: "Read `references/api-errors.md` if the API returns a non-200 status code."

## Validation

Run `skills-ref validate ./my-skill` if the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) tool is available.
