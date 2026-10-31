# Evidence Rules for Value-Liveness Audits

How to decide whether a model or engine ID referenced in `modelRoles.*` or `retry.fallbackChains.*` still resolves in the installed omp version. Every verdict in the report cites the step that produced it.

## Why a ladder

The default `omp models list` shows **chat models only**. Decision models (TypeSafe Jev), web engines (`web/*`), and image-generation models are different catalog kinds and never appear there — a naive check reports false "MISSING" verdicts.

The opposite trap: a string search over the omp binary. Web engines and many models are **catalog data entries, not compiled-in strings** in current omp versions; engine implementations ship as chunk files (`brave-s1bjy3ya.js`), and the `web/*` strings that do appear in the binary are Bun module-table names. Binary grep zero-hits therefore does **not** mean an ID is dead. In a 2026-10 audit this rule wrongly condemned `web/zai` and `web/brave` (both alive); a fresh-context trial run caught it.

## The ladder (stop at the first decisive step)

1. **Full catalog inventory** (decisive for existence): `omp models --kind all --json` — chat, image, judge, search, video, embedding, rerank, tiny, tts, stt. Match the full selector (provider-qualified) against `.models[].selector`.
   - Present = the ID resolves.
   - Absent under the same provider but present under another = **stale provider path** (the model lives, the selector does not). Example: `openai-codex/gpt-image-1` dead while `openrouter/openai/gpt-image-1` and `openai-codex/gpt-image-2` exist. Report the replacement candidates.
2. **Live test** (decisive for load-bearing roles — run it even when step 1 passes, because credentials and routes can still break):
   - judge role → `await judge("<state>", {"q": {"type": "bool", ...}})`; confirm the real model in `~/.omp/cache/judgment-cache.db`: `SELECT provider, model FROM usage ORDER BY rowid DESC LIMIT 1;`
   - image role → `await tool.generate_image({"prompt": ..., "subject": ...})`; the result `details` name the provider and model.
   - web role → run a `web_search` through the configured engine; logs do not record which engine served, so cross-check the catalog entry and note the ambiguity.
3. **Binary grep** (weak signal, never a verdict): `grep -ac "<id>" "$(readlink -f $(which omp))"`. Nonzero hits are usually embedded CHANGELOG prose or module names, not catalog entries — inspect context with `grep -aoE '.{50}<id>.{50}'` and treat any conclusion from it as a hypothesis for steps 1–2 to confirm or kill.

## Recording evidence

For each audited ID, record: ID, where it is referenced (layer + key), ladder steps run, verdict (alive / dead / stale provider path), and the observation that decided it.

| ID                         | Referenced by        | Steps | Verdict             | Evidence                                                                                        |
| -------------------------- | -------------------- | ----- | ------------------- | ----------------------------------------------------------------------------------------------- |
| `openai-codex/gpt-image-1` | fallbackChains.image | 1     | stale provider path | catalog image kind: openai-codex has only `gpt-image-2`; `openrouter/openai/gpt-image-1` exists |
| `typesafe/jev-latest`      | modelRoles.judge     | 1, 2  | alive               | catalog judge kind; live call; usage table `typesafe / jev-1.14.0`                              |
| `web/zai`                  | modelRoles.web       | 1, 2  | alive               | catalog search kind (22 engines); live web_search OK                                            |

## Known traps

- **Fail-soft roles**: a dead engine or fallback entry does not error; web_search keeps working through fallbacks and a dead image fallback is invisible while the primary serves. Only the ladder reveals it.
- **Changelog prose can be stale about aliases**: 18.12.2's note "`jev-latest` … answered as `jev-1.13.0`" was true then; the judgment-cache `usage` table in 2026-10 showed `jev-1.14.0`. Live-test evidence outranks release-note prose for what an alias serves today.
- **Strict selectors** (omp ≥ 18.14.0): provider-qualified selectors must match an exact catalog ID; near matches fail at selection time. A selector that was valid at adoption can rot when providers reshuffle their catalogs — verify every pinned ID each audit.
- **`omp models list` vs `--kind all`**: the bare command is chat-only. Always use `--kind all` (or `--kind search` / `--kind image` / `--kind judge`) for non-chat IDs.
- **Catalog role defaults move** between versions; machines that pin roles explicitly are unaffected — state which layers pin and which inherit.
- **`omp gc --compress` on macOS 27**: APFS does not shrink, so compression is skipped (`0/N files` in the dry run). `gc.compress: true` is then ineffective, not stale.
