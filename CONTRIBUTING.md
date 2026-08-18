# Contributing

This document covers how changes land in this single-maintainer repository. Development setup lives in [DEVELOPMENT.md](./DEVELOPMENT.md); rules for AI agents live in [AGENTS.md](./AGENTS.md).

## Ground Rules

- Make the smallest coherent change that solves the requirement.
- Keep unrelated cleanup out of a skill or documentation change.
- Do not add a dependency, tool, or new top-level directory without approval.
- Do not change files under `skills/` that are unrelated to the requested skill.
- Keep the published skill name, directory name, and `SKILL.md` frontmatter synchronized.

## Change Submission

This repository does not require an issue-first process. For a bug fix or feature, prepare a focused pull request that explains the requested behavior, relevant context, and validation performed. Use the pull request description to provide the detail a reviewer needs rather than creating a separate tracking workflow.

## Pull Request Workflow

1. Branch from `main`.
2. Implement the smallest coherent change and keep the diff scoped.
3. Run `mise run check`; CI and the local command use the same validation entry point.
4. Commit with Conventional Commits; the local Cocogitto hook validates the message.
5. Open a pull request with the required description sections and a passing CI check.
6. The sole maintainer reviews the change and merges it, normally with squash merging.

## Review Expectations

The reviewer checks:

- The requested skill or documentation behavior is correct and complete.
- `mise run check` passes locally and in CI.
- The diff contains no accidental files, dependencies, or scope creep.
- Root documentation links resolve to files in the repository.
- The change does not expose secrets or other sensitive information.
- Any changed skill keeps its `SKILL.md` frontmatter and directory name synchronized.

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/), validated locally by the Cocogitto commit-msg hook:

```text
feat(skill): add a branch cleanup workflow
fix(check): reject mismatched skill names
docs(readme): clarify installation
```

Squash merging composes the `main` commit from two parts: the subject is the pull request title, and the body is the branch's commit messages concatenated (`PR_TITLE` + `COMMIT_MESSAGES`). CI validates the title with Cocogitto because that is the subject the history is read by; branch commit messages are not gated in CI, so a pull request never fails over them, but they do land in the body — keep them meaningful.

## AI-Assisted Pull Requests

AI-generated or AI-assisted pull requests follow the same quality bar. The description must include these five headings, using the wording synchronized with `.github/pull_request_template.md`:

- **Purpose**: Describe the purpose of this change.
- **Impact**: Describe the impact of this change.
- **Context**: Provide relevant context or background.
- **Risks**: Describe potential risks or concerns.
- **Testing**: Describe testing or validation performed.

Keep the GitHub pull request template synchronized with these five requirements.
