<div align="center">

# Personal Agent Skills

Reusable Agent Skills for coding agents, distributed through the `skills` CLI.

[![CI](https://github.com/fang2hou/skills/actions/workflows/check.yml/badge.svg)](https://github.com/fang2hou/skills/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

</div>

## Why

This repository collects focused [Agent Skills](https://agentskills.io/) that give coding agents reusable workflows for common engineering tasks.

- In scope: Markdown-based skills for creating, reviewing, testing, polishing, and coordinating coding work.
- Out of scope: application source code, runtime services, package libraries, or a general-purpose agent framework.

## Install

Requires Node.js ≥ 22.20 and the [`skills` CLI](https://skills.sh).

```bash
# Interactive (pick agents per machine)
npx skills add fang2hou/skills -g

# Non-interactive (e.g. CI or scripted setup)
npx skills add fang2hou/skills -g -a claude-code -a zed --skill '*' -y

# List available skills
npx skills add fang2hou/skills --list
```

Global installs write the canonical copy under `~/.agents/skills/` and give each selected agent a symlink.

## Use it

Install the skills globally, select the skills for the coding agents on a machine, and invoke them through those agents' normal skill interfaces. Use the `--list` command above to inspect the available collection before selecting.

## Skills

| Skill                                                | Description                                                                      |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- |
| [create-skill](skills/create-skill/)                 | Creates spec-compliant Agent Skills from requirements to delivery                |
| [git-branch-cleanup](skills/git-branch-cleanup/)     | Safely deletes local branches fully merged into the remote default branch        |
| [github-repo-baseline](skills/github-repo-baseline/) | Applies the standard settings baseline to a GitHub repository via the gh CLI     |
| [herdr-parallel-dev](skills/herdr-parallel-dev/)     | Orchestrates parallel multi-agent development with Herdr (one worktree per task) |
| [improve-skill](skills/improve-skill/)               | Audits and improves Agent Skills for spec compliance and clarity                 |
| [polish-japanese-docs](skills/polish-japanese-docs/) | Polishes Japanese technical docs into natural technical-document prose           |
| [review-and-fix](skills/review-and-fix/)             | Senior-level diff review with an interactive fix workflow                        |
| [test-design](skills/test-design/)                   | Designs structured test cases and coverage gaps from code, specs, or tickets     |

## For AI coding agents

Paste this instruction into an agent working on the repository:

```text
Work in this repository. Read AGENTS.md at the repository root first and follow it.
```

## Goal → Read

| Goal                      | Read                                 |
| ------------------------- | ------------------------------------ |
| Develop and validate      | [DEVELOPMENT.md](./DEVELOPMENT.md)   |
| Contribute a change       | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| Follow agent instructions | [AGENTS.md](./AGENTS.md)             |

## Environment Requirements

- Node.js ≥ 22.20 is required for the `npx skills` commands.
- Repository development tools are managed by [mise](https://mise.jdx.dev/); run `mise install` before `mise run check`.
- Installing or using these skills requires no repository-specific environment variables or external services.

## Updating

After editing a skill here: commit, push, then run `npx skills update -g -y` on other machines.

## License

MIT — see [LICENSE](./LICENSE).
