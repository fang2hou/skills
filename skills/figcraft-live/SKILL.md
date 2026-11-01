---
name: figcraft-live
description: >
  Live design in the FigCraft desktop app (github.com/storytold/figcraft)
  through a lazy MCP server: it mounts globally without launching anything,
  starts the app only when the ensure tool is called, shares one instance per
  repository across worktrees and agents, and covers files, assets, and CI
  headlessly via figcraft-cli. Use for FigCraft or .figcraft work.
license: MIT
compatibility: >
  live editing: the FigCraft desktop app plus the figcraft-live-mcp server
  (bash
  and jq; launching needs macOS open, or FIGCRAFT_APP pointing at the
  binary/AppImage elsewhere); file work (inspect, render, export, run):
  anywhere figcraft-cli runs.
metadata:
  author: fang2hou
  version: "4.1"
---

# FigCraft Live

One lazy MCP server, `figcraft-live` (this skill's
`scripts/figcraft-live-mcp`), is the
live interface to the FigCraft desktop app: it mounts in every session
without starting anything, and the app opens only when a design task actually
needs it — at most one window per repository, shared by every worktree and
every agent. Headless `figcraft-cli` handles file work (inspect, convert,
render, export, atomic scripts) without the app.

## The demand gate

- The server registers **globally** (user level) and mounts silently: no
  window, no app, no per-project setup. Several agents may mount it at once.
- **Only the `ensure` tool may launch the app.** It first looks for an
  already-running controllable instance and attaches to it (adopting the
  user's window instead of opening another); it launches the app only when
  none runs. Announce the launch before calling it.
- Every other tool (`status`, `commands`, `inspect`, `render`, `exec`,
  `batch`, `stop`) never starts anything — they reuse the running instance
  or fail with a pointer to `ensure`.
- Never work around the gate (launching the app by hand, shell, or a second
  registration) and never replace a failed launch with silent headless
  editing: report and let the user decide.

## Setup

One-time install (per machine, not per project):

1. Server: `install -m 755 <skill-dir>/scripts/figcraft-live-mcp
   ~/.local/bin/` (needs `bash` and `jq`). Register it globally for your
   client — omp: `~/.omp/agent/mcp.json`; Claude Code: `claude mcp add
   --scope user figcraft-live ~/.local/bin/figcraft-live-mcp`; snippets
   and the timeout caveat: [references/mcp.md](references/mcp.md).
2. CLI (headless file route, offline command discovery):
   `figcraft-cli` from the GitHub release, checksum-verified:
   [references/setup.md](references/setup.md).

Per-task check, reported in the first progress note: the session lists the
`figcraft-live` tools (mounted), `figcraft-cli --version` works (file route
ready). Neither check starts the app.

## Tools

All tools take a single JSON object and reply with one text block of JSON
(the control channel's reply, `ok`/`error` inside). Tool names carry the
client's server prefix (omp: `mcp__figcraft_live_status`, …).

| Tool                                   | Starts the app         | Purpose                                                                                                                                                                                   |
| -------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `status {}`                            | never                  | Running? port, origin (started/adopted), open windows and documents.                                                                                                                      |
| `ensure {path?, name?, raise?}`        | **yes — the only one** | Adopt or launch the shared instance; `path` opens the design file or reuses its open tab (reports `already`/`new` and `stale`); `name` starts a new document; `raise` focuses the window. |
| `exec {command, params?}`              | never                  | One registry command (`file.save`, `node.set`, `select.set`, `edit.undo`, `image.place`, `inspect.code`, …).                                                                              |
| `batch {label?, commands[]}`           | never                  | Many commands as ONE undo step (`command.batch`); name steps with `as`, reference with `{"$ref": name}`. One design section per batch.                                                    |
| `inspect {id?, depth?}`                | never                  | `node.get` for one layer, or `document.inspect` for solved sizes/bounds/history.                                                                                                          |
| `render {ids, scale?, path?, window?}` | never                  | PNG via `ui.render`, returned inline. **Without `ids` it renders the current selection** — pass the frame ids. `window: true` captures the app window.                                    |
| `commands {filter?}`                   | never                  | In-app registry listing (regex on id/label). Offline: `figcraft-cli commands --filter X`.                                                                                                 |
| `stop {force?}`                        | never                  | `app.quit` of an instance this server started. Discards unsaved changes; adopted instances need `force: true`.                                                                            |

### Standard session

1. `status` — is an instance up, and which documents are open?
2. `ensure {path: "design/app.figcraft"}` — the canvas moment: adopts the
   running instance (or launches it, announced) and makes your design file
   the active tab. New design: `ensure {name: "..."}`. If `ensure` fails,
   STOP — do not edit whatever tab happens to be active.
3. Discover: `commands {filter: "layout"}` when unsure about ids or params.
4. Edit per section: `batch` (see below), capturing returned ids.
5. Verify: `inspect` (model: solved sizes, `absoluteBounds`) then `render
   {ids}` (pixels: nothing clipped, fills where expected).
6. Persist: `exec {command: "file.save", params: {path}}` after each
   section; the saved `.figcraft` file is the source of truth.
7. Wind down: leave the app running while design continues; `stop` at the
   end of the phase (save first).

Section example (`as`/`$ref` instead of counting ids):

```json
{
  "label": "nav",
  "commands": [
    {
      "command": "frame.create",
      "as": "page",
      "params": {
        "width": 390,
        "height": 844,
        "name": "Home",
        "props": { "fill": "#FFFFFF", "layout": "vertical", "padding": 0 }
      }
    },
    {
      "command": "frame.create",
      "as": "nav",
      "params": {
        "parent": { "$ref": "page" },
        "name": "nav",
        "props": {
          "layout": "horizontal",
          "sizingH": "fill",
          "sizingV": "hug",
          "padding": [16, 20, 16, 20],
          "mainAlign": "spaceBetween",
          "crossAlign": "center"
        }
      }
    },
    {
      "command": "node.create",
      "params": {
        "type": "text",
        "parent": { "$ref": "nav" },
        "text": "App",
        "name": "nav-title",
        "props": { "fontSize": 17, "fill": "#111827" }
      }
    }
  ]
}
```

## Editing rules

1. Discover before use: guessed ids and params fail (`commands`, or
   `figcraft-cli commands` offline).
2. One section per `batch` (single undo step). A failing batch rolls back
   entirely and names the step.
3. Work in your own document (`ensure` opens it) and `file.save` after each
   section; never edit in a tab you did not open — check `status` when in
   doubt.
4. The user shares the canvas: `inspect` a layer before re-editing it; never
   touch `ui.pointer`/`ui.key`/`ui.type` (raw control methods) unless asked.
   Highlight finished sections with `select.set` + `view.zoomSelection`.
5. A failed call may still have applied: `inspect` before retrying.
6. Images: local `path` or base64 `data` only (no URL) — see
   [references/images.md](references/images.md).
7. Build with auto layout; every layout frame declares `sizingH`/`sizingV`;
   body text contrast ≥ 4.5:1 — see
   [references/design.md](references/design.md).
8. A succeeding command is not a verified result: verify (step 5 above).

## Worktrees and multiple agents

- The instance is keyed by `git rev-parse --git-common-dir`: every worktree
  of a repository resolves the same control port, so three agents in three
  worktrees share one window and one canvas — the first `ensure` starts it,
  the rest adopt it (a launch lock prevents double starts).
- Keep one canonical design file path in the repository; `ensure {path}`
  reuses its open tab and reports `stale` when the file changed on disk.
  `file.save` refuses to overwrite a file another session saved meanwhile
  (use `overwrite: true` only after re-opening, not blindly).
- Do not run two concurrent edit sessions on one file: the shared instance
  serializes edits but merges nothing.
- Only `stop` instances the server started; adopted windows belong to the
  user.

## Headless file route

No app, no window, atomic — for reads, exports, CI, non-macOS, or when the
gate must stay closed:

| Need                                   | Command                                                               |
| -------------------------------------- | --------------------------------------------------------------------- |
| Inspect/convert a file                 | `figcraft-cli info <file> [--json]`, `convert <in> <out>`             |
| Render/export assets                   | `render <file> -o out.png`, `export <file> -o dir/ --scale 2`         |
| Scripted edits (one undo unit, atomic) | `figcraft-cli run script.jsonl --in base.figcraft --out out.figcraft` |
| Command discovery                      | `figcraft-cli commands --filter TEXT`                                 |

Same `{command, params}` objects as `batch`. Full reference:
[references/cli.md](references/cli.md).

## Failure Handling

| Symptom                                             | Action                                                                                                                                 |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Tool says "not running; call ensure"                | Expected before the first `ensure`; run it (announcing the launch).                                                                    |
| `ensure` fails: app/launch error                    | Report; continue headless (`figcraft-cli`) only with the user's knowledge.                                                             |
| `ensure` reports `stale: true`                      | The file changed on disk since the tab read it: re-open (`file.open` with `reload: true`, tab must be clean) or confirm with the user. |
| `no open document`                                  | The active tab closed; `ensure` again (path or name).                                                                                  |
| A frame solves to 100×100 / children vanish         | Missing `sizingH`/`sizingV` on the parent; fix the parent.                                                                             |
| Render looks tiny or empty                          | `render` without `ids` renders the selection; pass the frame ids.                                                                      |
| `unsupported image: format could not be determined` | Not an image file or wrong path; convert to PNG/JPG/WebP.                                                                              |
| `automation path rejected`                          | File outside the app's `--automation-read-root`/`-write-root`.                                                                         |
| `control request queue is full`                     | Back off; smaller batches.                                                                                                             |
| `stop` refuses an adopted instance                  | By design (unsaved changes lost); save, then `force: true`.                                                                            |

## Gotchas

- Auto-layout frames never size themselves: no `sizingH`/`sizingV` → fixed
  100×100, and frames clip children by default.
- Frames default to a white fill; wrappers need `"fill": "none"`.
- Vector icons stretch when given both `width` and `height`; give one.
- An app running without a control port cannot be attached: `ensure` opens
  its own instance, so two windows appear — let the user quit theirs; never
  kill it.
- Creation commands return `{"id": N}`: capture ids or use `as`/`$ref`;
  never assume them. Coordinates are page units (y down), `x`/`y` relative
  to the parent; colors `#RRGGBB[AA]`.
- Live sessions use app/system fonts; CI-stable renders need
  `--no-system-fonts` (file route).

## Output Contract

On completion, report:

1. The interface used: MCP live (instance started or adopted, port) or
   headless CLI — and why, when not live.
2. Document path(s) with key node ids and names.
3. Every placed image (source, target node, mode) and exported asset (path,
   format, scale).
4. Verification performed (model check, pixel check) and tool warnings.

## References

- [references/mcp.md](references/mcp.md): server design, registration per
  client, env vars, protocol notes.
- [references/control.md](references/control.md): the loopback control
  protocol the server speaks (methods, limits), for debugging.
- [references/images.md](references/images.md): placing images, fills,
  avatars, adjustments, checks.
- [references/design.md](references/design.md): construction patterns and
  the verification checklist.
- [references/setup.md](references/setup.md): CLI probe, install, build, app
  notes.
- [references/cli.md](references/cli.md): `figcraft-cli` subcommands, flags,
  exit codes, export gotchas.
