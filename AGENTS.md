# AGENTS.md

This repository is a collection of Agent Skills for coding agents that need reusable, task-focused workflows.

## Commands

```bash
mise install
mise run format
mise run check
```

This repository has no `test`, `build`, or `dev` mise tasks. `mise run check` verifies Markdown formatting with oxfmt, runs the root skill-structure check, and runs the redacted Gitleaks scan; `mise run format` rewrites Markdown in place.

## Engineering Standards

Follow the shared engineering guidelines in the [AI Coding Guidelines portal](https://github.com/fang2hou/ai-coding-guidelines/blob/main/PORTAL.md). Read the portal recipe for the task before editing; repository documentation is the source of truth when it is more specific.

Project-specific overrides:

- None. This repository follows the shared standards.

## Layout

- `.github/` — GitHub Actions workflows and the pull request template.
- `scripts/` — repository validation scripts, including `check-skills.sh`.
- `skills/` — the seven installable Agent Skills; each has a `SKILL.md` and may have one-level `references/` content.

## Boundaries

Always:

- Run `mise run check` and require exit status 0 before every commit.
- When changing a file under `skills/`, keep the skill entrypoint at `skills/*/SKILL.md` and run `bash scripts/check-skills.sh` before opening a pull request.
- When adding a relative link in a root document, point it to an existing path in this repository and recheck the link before committing.

Never:

- Add `package.json`, `pnpm-lock.yaml`, `tsconfig.json`, or JavaScript/TypeScript source files; this repository validates Markdown and Bash instead.
- Commit a change when `mise run check` exits nonzero.
- Add another `AGENTS.md` below `skills/`; the root file is the canonical agent instruction surface.
- Change `skills/herdr-parallel-dev/scripts/verify-worktrees.sh` during a skill-content change unless the request names that path.

Ask first:

- Before adding a top-level directory or changing `mise.toml`, `.oxfmtrc.json`, `.pre-commit-config.yaml`, `.gitattributes`, `.github/workflows/`, or `scripts/check-skills.sh`.
- Before changing the install or update commands in `README.md`, including `npx skills add fang2hou/skills -g` or `npx skills update -g -y`.
- Before deleting or renaming any `skills/*/SKILL.md` or changing a published skill's frontmatter `name`.

## Confirmed Language Policy

| Item                      | Value                                                                        |
| ------------------------- | ---------------------------------------------------------------------------- |
| Conversation              | Follows the language used by the user                                        |
| Code / comments / commits | English                                                                      |
| UI language               | No UI in this repository; skill content follows the target document language |
| Tone                      | Clear, concise, and technical; use the target document's natural register    |

Do not infer UI language from conversation language.

## Project Conventions

- A skill directory's name must exactly match the `name` field in its `SKILL.md` frontmatter.
- Keep each skill's `references/` directory one level deep; keep `SKILL.md` below 500 lines when the workflow can remain complete and clear.
- `scripts/check-skills.sh` validates frontmatter delimiters, the lowercase skill-name format, the exact directory/name match, and a non-empty description no longer than 1024 characters; it warns above 250 description characters or 500 body lines.
- After changing a skill, use `npx skills add fang2hou/skills -g` to verify the installed distribution on this machine; on another machine, refresh it with `npx skills update -g -y`.

Depth: [DEVELOPMENT.md](./DEVELOPMENT.md) for workflow and toolchain, [CONTRIBUTING.md](./CONTRIBUTING.md) for pull request rules.
