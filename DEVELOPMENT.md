# Development

This document describes how humans and AI agents change the Agent Skills in this repository. User-facing installation lives in [README.md](./README.md); agent-facing operating rules live in [AGENTS.md](./AGENTS.md).

## Setup

All development tools are managed by mise.

```bash
mise install
```

| Tool      | Version | Purpose                                                                         | Managed via |
| --------- | ------- | ------------------------------------------------------------------------------- | ----------- |
| Node.js   | 24      | Runs the `npx skills` distribution CLI                                          | `mise.toml` |
| prek      | latest  | Runs the configured Git hooks for staged changes and commit messages            | `mise.toml` |
| Cocogitto | latest  | Validates Conventional Commit messages locally and the pull request title in CI | `mise.toml` |
| Gitleaks  | latest  | Scans tracked content for secrets during validation                             | `mise.toml` |
| oxfmt     | latest  | Formats and format-checks the repository's Markdown                             | `mise.toml` |

Do not substitute these tools without explicit approval under the shared toolchain standards.

## Commands

```bash
mise run format
mise run check
```

`mise run check` is the same validation entry point used by CI: it runs `oxfmt --check .`, `bash scripts/check-skills.sh`, and a redacted Gitleaks scan. `mise run format` rewrites Markdown in place with oxfmt, configured by `.oxfmtrc.json`. This repository has no `test`, `e2e`, `build`, or `dev` mise tasks.

## Workflow

1. Branch from `main`.
2. Implement the smallest coherent change.
3. Run `mise run check` and resolve every failure.
4. Commit with Conventional Commits; the local Cocogitto commit-msg hook validates the message. Only the pull request title reaches `main` under squash merging, and CI validates that title.
5. Open a pull request using [CONTRIBUTING.md](./CONTRIBUTING.md).

## Layout

- `.github/` — GitHub Actions workflows and the pull request template.
- `scripts/` — repository validation scripts, including `check-skills.sh`.
- `skills/` — installable Agent Skills, each centered on a `SKILL.md` with optional one-level `references/` content.

## Coding Standards

Follow the shared coding standards in the [AI Coding Guidelines portal](https://github.com/fang2hou/ai-coding-guidelines/blob/main/PORTAL.md). Project-specific rules and boundaries are recorded in [AGENTS.md](./AGENTS.md); there are no additional overrides.

## Skill Authoring and Modification

1. Read [AGENTS.md](./AGENTS.md), the target skill's `SKILL.md`, and any references needed for the requested behavior.
2. For a new skill, create a directory under `skills/` with `SKILL.md` as its entrypoint. Set the frontmatter `name` to exactly the directory name and keep `references/` no deeper than one level.
3. Keep the skill workflow complete and focused; keep `SKILL.md` below 500 lines when possible.
4. Run `bash scripts/check-skills.sh`. It scans `skills/*/SKILL.md`, requires opening and closing YAML frontmatter, checks a one-to-64-character lowercase name with no edge or consecutive hyphens, requires the name to match the parent directory, and requires a non-empty description of at most 1024 characters. Descriptions above 250 characters and bodies above 500 lines produce warnings rather than failures.
5. Run `mise run check`, then use `npx skills add fang2hou/skills -g` to install and exercise the updated distribution on this machine. Global installs place the canonical copy under `~/.agents/skills/`.
6. On another machine, refresh the installed skills with `npx skills update -g -y`.

## Validation

`mise run check` is the only validation entry point. It runs the same oxfmt format check, `bash scripts/check-skills.sh`, and redacted Gitleaks logic locally and in CI; do not maintain separate local and CI validation paths. There is no unit-test or end-to-end task in this Markdown and Bash repository.
