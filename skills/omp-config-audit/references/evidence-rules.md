# Evidence Rules for Value-Liveness Audits

How to decide whether a model or engine ID referenced in `modelRoles.*` or `retry.fallbackChains.*` still resolves in the installed omp version. Every verdict in the report cites the step that produced it.

## Why a ladder

`omp models list --json` lists **chat models only**. Three classes of IDs never appear there and yield false "MISSING" verdicts:

1. **Decision models** — e.g. TypeSafe Jev (`typesafe/jev-*`); they answer over a decisions endpoint, not as chat models.
2. **Web engines** — `web/<engine>` IDs for the hosted web_search role.
3. **Image-generation models** — e.g. `google-antigravity/gemini-3-pro-image`.

Conversely, a string found inside the omp binary does not prove an ID is alive: the binary embeds its own CHANGELOG prose, so `grep -c typesafe/jev-latest` hits changelog sentences, not catalog entries.

## The ladder (stop at the first decisive step)

1. **Chat models**: check the selector in `omp models list --json` (`.models[].selector`). Present = alive. Absent = dead for chat IDs — this IS decisive for chat models.
2. **Binary presence**: `B=$(readlink -f $(which omp)); grep -ac "<id>" "$B"`. Zero hits = dead (the ID is not compiled in at all). Nonzero is inconclusive → step 3.
3. **Context check**: `grep -aoE '.{50}<id>.{50}' "$B" | head -3`. If every hit is changelog/release prose ("role now uses …"), treat as inconclusive → step 4. Catalog/code context (nearby JSON, provider tables) suggests alive but still verify if the ID is load-bearing.
4. **Live test** (decisive): exercise the ID through the harness's own tools in the current session:
   - judge role → `await judge("<state>", {"q": {"type": "bool", ...}})`; then confirm the real model in `~/.omp/cache/judgment-cache.db`: `SELECT provider, model FROM usage ORDER BY rowid DESC LIMIT 1;`
   - image role → `await tool.generate_image({"prompt": ..., "subject": ...})`; the result `details` name the provider and model.
   - web role → run a `web_search`; note the engine cannot be read from logs, so cross-check with step 5.
5. **Engine inventory**: `grep -aoE 'web/[a-z]+' "$B" | sort -u` — the compiled-in engine IDs. Filter obvious URL path fragments (`web/response-body`, `web/settings`, …); the survivors are the real engines. An ID absent here is dead even though search still works (fallbacks mask it).

## Recording evidence

For each audited ID, record in the report: ID, where it is referenced (layer + key), ladder steps run, verdict (alive / dead / inconclusive→tested), and the observation that decided it. Example row:

| ID | Referenced by | Steps | Verdict | Evidence |
| --- | --- | --- | --- | --- |
| `web/zai` | personal.base `modelRoles.web` | 2, 5 | dead | binary zero hits; engine inventory has no zai |
| `typesafe/jev-latest` | personal.base `modelRoles.judge` | 1, 2, 3, 4 | alive | live judge call; usage table: `typesafe / jev-1.14.0` |

## Known traps

- **Fail-soft roles**: a dead web-engine role does not error; web_search falls back silently. Only the ladder reveals it.
- **Strict selectors** (omp ≥ 18.14.0): provider-qualified selectors must match an exact model ID; near matches fail at selection time. Verify every pinned ID, not just the ones you suspect.
- **Catalog role defaults move** between versions (e.g. the `image` role default changed to Factory Droid models in 18.14.0); machines that pin roles explicitly are unaffected — state which layers pin and which inherit.
- **`omp gc --compress` on macOS 27**: APFS does not shrink, so compression is skipped (`0/N files` in the dry run). `gc.compress: true` is then a no-op, not an error — classify as ineffective, not stale.
