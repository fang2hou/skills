---
name: omp-config-audit
description: >
  Audits the dotfiles omp config layers against the installed omp release and upstream
  changelog — stale keys, dead model/engine IDs, changed defaults, new features, HTML
  report. Use when omp updates or web/judge/image roles silently degrade.
license: MIT
compatibility: Requires gh (GitHub API), the omp binary on PATH, Python 3 with PyYAML, and the agent-report skill for the HTML output.
metadata:
  author: fang2hou
  version: "1.0"
---

# omp Config Audit

Compares the dotfiles omp config baseline against the installed omp version and produces an evidence-backed HTML report: new-feature highlights, settings at risk, and exact changes to make.

## When to Use

- omp released new versions since the last audit and the user asks what changed / what to update.
- A role-configured subsystem (hosted web search, judge, image generation) silently degrades — usually a dead model or engine ID in `modelRoles` / `retry.fallbackChains`.
- Periodic check the user runs after upgrading omp ("check 一下设定和最新版本的差异").

## When NOT to Use

- omp bug reports or usage questions that are not about config drift.
- Editing the generated `~/.omp/agent/config.yml` directly — it is a build artifact; the sources are the layered YAML files in `~/dotfiles/omp/`.
- Theme auditing (separate concern; see the 主题 section of `~/dotfiles/omp/README.md`).

## Inputs

| Input | Required | Format | Example |
| ----- | -------- | ------ | ------- |
| Baseline version | No (auto-detected) | semver | `18.12.0` |
| Report language | No (defaults to the user's language, typically `zh-CN`) | locale | `zh-CN` |

## Hard Rules

1. **Read-only until confirmed.** The audit proposes YAML diffs and a README update; apply them only after the user confirms. The generated `config.yml` is never edited.
2. **Audit the installed version.** Schema truth comes from the installed binary (`omp config list --json`); if a newer release exists, note it as an upgrade step, do not audit an uninstalled schema.
3. **Dead-value claims need ladder evidence.** A model/engine ID is declared dead only per the ladder in [references/evidence-rules.md](references/evidence-rules.md); `omp models list` absence alone is not evidence.
4. **The report is produced with the agent-report skill** (report.json → kit renderer → HTML export). Never hand-write the HTML.

## Workflow

### Step 1: Determine scope

- Baseline: the `基准版本` line in the `## 优化记录` header of `~/dotfiles/omp/README.md`. Do not infer it from git log — adoption commits lag README updates.
- Installed: `omp --version`. Latest: `gh api repos/can1357/oh-my-pi/releases -q '.[0].tag_name'`.
- Gap = versions in `(baseline, installed]`. If installed < latest, say so and suggest upgrading first (mise: `mise use -g github-can1357-oh-my-pi@latest`), then continue auditing what is installed.

### Step 2: Gather evidence

- Release bodies for every gap version: `gh api repos/can1357/oh-my-pi/releases/tags/<tag> -q '.body'` into `/tmp/omp-audit/<tag>.md`.
- Upstream changelog (authoritative; release bodies are its curated cut): `curl -sL https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/CHANGELOG.md`.
- Current config state: `omp config list --json > /tmp/omp-audit/schema.json` and the six layer files `~/dotfiles/omp/{base,personal.base,personal.normal,work.base,work.normal,work.secret}.yaml`.

### Step 3: Extract changes in parallel

Total notes are typically 150–350 lines per version; spawn 3 read-only scouts at roughly 1000 lines each, one per segment of consecutive versions. Each scout returns per version: **Highlights** (user-visible capabilities, 1–5 bullets), **Config-relevant changes** (new keys with defaults, changed defaults, renamed/removed keys, quoted verbatim), **Risk items** (breaking changes, silent behavior flips). Cross-check scout output against the CHANGELOG.md sections for the same versions; the changelog wins on conflict.

### Step 4: Key-level validation

4. Run the bundled script: `python3 scripts/keycheck.py <schema.json> <layer.yaml>...`. It flattens each YAML layer and reports keys that are absent from the schema, after excluding children of record-typed parents (`modelRoles`, `retry.fallbackChains`, `task.agentModelOverrides`, `edit.modelVariants`, `providers.maxInFlightRequests`, `tools.approval`) — those children are dynamically named and schema-invisible, so a naive set-diff floods false positives. Zero stale keys is a real result; report it as such.
5. Record-valued keys whose values bind to a registry also need value checks, not just key checks: every `task.agentModelOverrides.<name>` must name a bundled agent (scout, reviewer, security-reviewer, seance, task, sonic — verify via `grep -ac "<name>" "$(readlink -f $(which omp))"` plus the `~/.omp/agent/agents` dir for custom agents; the 2026-10 audit found a `librarian` override that could never bind). A valid key with an unbindable value is a dead value.

### Step 5: Value liveness audit

For every model/engine ID referenced by `modelRoles.*` and `retry.fallbackChains.*`, follow the ladder in [references/evidence-rules.md](references/evidence-rules.md). The decisive inventory is `omp models --kind all --json` (chat-only `omp models list` hides decision models, web engines, and image models; binary grep is a weak signal that wrongly condemns catalog-era IDs). Live-test load-bearing roles (judge / image / web) even when the catalog lists them, and treat "present under a different provider" as a stale-provider-path finding with replacement candidates. Record the evidence next to each verdict; "probably dead" is not a deliverable.

### Step 6: Behavior drift and adoption filter

- For each key the layers set explicitly, check whether a gap version changed its default or semantics; flag flips that conflict with an explicit user stance (example pattern: `providers.openai-codex.daybreak` default-on vs the user's `codexResets.autoRedeem: "no"`).
- Filter adoption candidates through the design principles in `~/dotfiles/omp/README.md` (personal: capability over request volume; base: conservative; work: Bedrock cost/compliance). Categorize: recommend / optional / rejected-with-reason.

### Step 7: Report and propose

- Produce the HTML report with the agent-report skill: audit purpose, `lang` from the user's language, conclusion first (dead values → behavior changes → highlights → adoption), evidence tables, verification log. Export to HTML and open it.
- In chat, deliver the exact YAML diffs per layer and the proposed `## 优化记录` update (new baseline version + adoption table rows). Apply nothing yet.

### Step 8: Apply and verify (only after user confirmation)

Edit the layer YAMLs, then rebuild and verify on personal machines: `omp_profile normal` and `omp config get <key>` for each changed key; work machines rebuild on next `ompn`. Update the README baseline line and date. Commit per repo convention.

## Gotchas

- `omp config list --json` returns **effective merged values**, not pristine defaults — a differing value means "we set it or a default", distinguish via the YAML layers.
- Web engines and many models are catalog data entries, not compiled-in strings: binary grep zero-hits is not a death verdict, and nonzero hits are usually embedded CHANGELOG prose. Only the full catalog (`omp models --kind all --json`) plus a live test decide.
- `~/.omp/cache/judgment-cache.db` table `usage` records the actual provider+model per judgment — ground truth for what the judge role really resolves to.
- On macOS 27 (darwin 27) `gc.compress` is skipped entirely (APFS does not shrink); verify with `omp gc --compress` dry-run showing `0/N` before claiming it still matters.
- Old omp versions are not installable (`mise ls-remote github-can1357-oh-my-pi` lists only recent tags), so schema-diffing against the baseline binary is impossible; CHANGELOG.md is the substitute.
- A dead web-engine role fails soft: web_search keeps working through fallbacks, so breakage is invisible until you test which engine actually served a query.
- Run the audit's verification slice in a fresh context (subagent with the skill, no conversation history) before delivering: the 2026-10 trial caught a wrong ladder rule the authoring session had already committed to.

## Output Contract

1. HTML report path, opened in the browser.
2. Findings summary: stale keys (usually none), dead values with evidence, behavior changes, adoption candidates.
3. Exact proposed diffs for the affected YAML layers and the README `优化记录` section.
4. After user-approved changes: rebuild + `omp config get` verification results and the README baseline bump.
