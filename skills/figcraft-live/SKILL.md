---
name: figcraft-live
description: >
  On-demand live design in the FigCraft desktop app (github.com/storytold/figcraft)
  through the figcraft-live middleware: the app starts only when a command
  actually edits the canvas, one instance per repository is shared across git
  worktrees, and headless figcraft-cli covers files, assets, and CI. Use for
  FigCraft or .figcraft work.
license: MIT
compatibility: >
  live editing: macOS with the FigCraft desktop app, plus bash, jq, and nc for
  the figcraft-live middleware; file work (inspect, render, export, run):
  anywhere figcraft-cli runs.
metadata:
  author: fang2hou
  version: "3.0"
---

# FigCraft Live

Live FigCraft editing goes through one middleware: `figcraft-live` (this
skill's `scripts/figcraft-live`, installed to `~/.local/bin`). It speaks the
app's loopback control channel, so **nothing is registered in any MCP client
and nothing starts when an agent session starts**. The desktop app launches at
the exact moment a subcommand needs the canvas — never before — and one
instance per repository serves every git worktree of that repository.

`figcraft-cli` (headless, file-based) handles everything that does not need
the app: inspecting, converting, rendering, exporting, and atomic batch
scripts. It is the only route on non-macOS hosts and in CI.

## The demand gate

The app may start only through one of two triggers:

1. A live subcommand must touch the canvas: `exec`, `batch`, `inspect`, or
   `render` auto-starts the app when it is down (`start` is the explicit
   form).
2. The user asks for live design work.

Everything else never starts anything: `status` and `rpc` only observe,
`figcraft-cli` file subcommands never launch the app, and no code path here
registers an MCP server. Announce the first launch ("starting FigCraft,
port N") in the progress note, and never replace a failed live start with a
silent headless run — report the failure and continue on the file route only
with the user's knowledge.

## Three states

Pick the state from what the task needs, not from the session:

| State  | When                                                       | App                    | Entry points                                      |
| ------ | ---------------------------------------------------------- | ---------------------- | ------------------------------------------------- |
| `off`  | Default. No design work in this project.                   | Never started.         | —                                                 |
| `file` | Read, convert, render, export, or script an existing file; | Never started (the CLI | `figcraft-cli info\|convert\|render\|export\|run` |
|        | CI, servers, non-macOS hosts.                              | is headless).          |                                                   |
| `live` | Build or edit a design; the user may watch the canvas.     | Started by the first   | `figcraft-live exec\|batch\|inspect\|render`      |
|        |                                                            | live command.          |                                                   |

Escalation rule: `file` first whenever it satisfies the task (it is atomic,
reproducible, and disturbs nothing), `live` only when the canvas must change
or be seen. A task may use both: design in `live`, then re-export assets
deterministically in `file`.

## Project phases

| Phase                                                    | Strategy                                                                                                                                                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Greenfield design, design sprint, pair-design            | `live`, sustained: start once, keep the app open, build section by section, `file.save` after each section. The user watches and can intervene.                                           |
| Implementation: the design exists, code is being written | `file` by default (`export`, `render`, `inspect.code` reads). Escalate to `live` for the occasional design fix; leave the app running across follow-ups, or `stop` when done for the day. |
| Occasional tweaks between coding sessions                | `live` on demand: the first command starts the app, later commands reuse it. No registration to remember, no reload to perform.                                                           |
| Inherited project with no design file                    | `off`. If the user wants a design born, go `live`; deliver assets via `file` afterwards.                                                                                                  |
| CI, servers, SSH boxes, non-macOS                        | `file` only.                                                                                                                                                                              |

Wind-down: leaving the app running is fine — the instance and its documents
survive every command and session. `figcraft-live stop` is for end-of-phase
cleanup; it quits **without asking about unsaved changes**, so save first
(Hard Rule 3), and it refuses adopted instances without `--force` (see below).

## One instance per repository

All worktrees of a repository share one app instance, so there is one window,
one canvas, one design file — not one instance per checkout.

- `figcraft-live` derives its control port from
  `git rev-parse --git-common-dir`, which is identical in every worktree of a
  repository; the resolution order is `FIGCRAFT_PORT` (pinned), the remembered
  port (`~/.local/state/figcraft-live/<key>`), port 7979, then a
  repo-derived port. State lives in `~/.local/state/figcraft-live/`.
- **Adopt before launch**: if any probed port already answers as FigCraft, the
  middleware attaches to that instance instead of opening a second window. An
  instance you did not start is `origin: adopted`; `stop` refuses it without
  `--force` because `app.quit` discards unsaved changes in every window.
- The design file is one canonical path in the repository (for example
  `design/app.figcraft`, committed like source). Every worktree opens and
  saves that same path: `file.open {path}` at session start (`reload: true`
  refreshes a tab that is already open; a tab whose file changed on disk
  reports `stale: true`), `file.save {path}` after each section. Saving over
  a file another app rewrote since open needs `overwrite: true` — with
  worktrees that usually means another session saved first: re-open instead.
- The shared instance serializes edits but does not merge them: never run two
  concurrent edit sessions on one design file. Re-read the nodes you touch
  (`figcraft-live inspect <id>`) before editing when another session or the
  user may have changed the document.

## Setup

Run at the start of every FigCraft task without asking permission; report the
outcome (CLI found or installed; middleware installed; app running or not) in
the first progress note. Nothing here starts the app.

1. CLI: `command -v figcraft-cli`, then `figcraft-cli --version` and
   `figcraft-cli commands --filter frame | head`. Missing or failing →
   install or rebuild per [references/setup.md](references/setup.md)
   (checksum-verified release into `~/.local/bin`; stop if the checksum is
   not `OK`).
2. Middleware: copy `scripts/figcraft-live` from this skill's directory to
   `~/.local/bin/` (`install -m 755`) and re-copy when the skill's copy
   differs. Needs `bash`, `jq`, and `nc`; launching additionally needs macOS
   `open`.
3. Smoke, in this order:
   - `figcraft-live status` — resolves the project and port, reports the app
     state, starts nothing.
   - On first real use: `figcraft-live exec file.new {"name": ...}` (or
     `file.open`) — this is the moment the app may start (up to 30 s); say so
     before running it.

## Hard Rules

1. Discover commands before using them (`figcraft-cli commands --filter
   <text>`, full docs with `--json`) and read their parameter docs. Guessed
   ids and params fail. All interfaces share one 400+ command registry.
2. Group related edits into one undo step: `figcraft-live batch` with
   `{label?, commands: [{command, params, as?}]}` (registry command
   `command.batch`), one section per batch. A failing batch rolls back
   entirely and the error names the step.
3. Work in your own document and save it. Start with `file.new` or
   `file.open` so the user's other tabs stay untouched, then `file.save
   {path}` after each completed section. The saved `.figcraft` file is the
   source of truth; unsaved live state lives only in the app.
4. The user shares the canvas. Re-read a layer (`figcraft-live inspect <id>`)
   before editing anything the user may have touched. Never use `ui.pointer`,
   `ui.key`, or `ui.type` unless asked: they act on the user's tool,
   selection, and keyboard focus. Build section by section so the user sees
   steady progress, then `select.set {ids}` (and `view.zoomSelection`) to
   highlight what was built.
5. A failed call may still have applied. Inspect the document before
   retrying.
6. Images enter only as a local file `path` or base64 `data` (no URL
   parameter): obtain the file first, then `image.place`. See
   [references/images.md](references/images.md).
7. Build with auto layout; never absolutely position text over shapes. Every
   layout frame declares `sizingH`/`sizingV`, and body text needs contrast of
   at least 4.5:1. See [references/design.md](references/design.md).
8. A command succeeding is not a verified result: verify as in Step 4 of the
   Workflow.

## Workflow

### Step 0: choose the state

Apply the phase table. When unsure, start `file` (safe, silent) and escalate
to `live` when the canvas must change.

### Step 1: connect, then open or start a document

- `figcraft-live status` first: `port` + `origin` + `app: running …` (window
  and tab list) or `app: not running`.
- Existing file: `figcraft-live exec file.open {"path": ...}` returns a
  summary (`name`, `pages`, `layers`, `images`) plus `warnings`/`repairs`, or
  the tab index when already open. Headless read of the same file:
  `figcraft-cli info design.figcraft --json`.
- New design: `figcraft-live exec file.new {"name?": ...}` (or
  `file.newFromTemplate`) even when tabs are open — a fresh app with zero
  documents rejects every edit with `no open document`. Reuse your document
  for the rest of the session; each `file.new` adds a tab.
- Smoke the UI state read-only: `figcraft-live rpc ui.inspect {}`.

### Step 2: Discover commands

`figcraft-cli commands --filter image` (or `layout`, `frame`, …) lists each
command's id, label, shortcut, and parameter doc. In-app equivalent:
`figcraft-live rpc engine.commands {}` (no filter; grep locally).

### Step 3: Make the edit

Build one section at a time with `batch`. Name a step with `as` and reference
its new id with `{"$ref": name}` instead of counting ids — the same shape
works in headless `figcraft-cli run` scripts:

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

Run it: `figcraft-live batch section.json` (or pipe on stdin with `-`; use
`-` or a file instead of shell quoting for payloads with base64 images).
Print each result's ids and `warnings`; do not discard them. Single layers
can use `node.create` / `node.set` via `exec`. Images: `image.place`
([references/images.md](references/images.md)). More patterns (buttons,
icons, dividers, avatars) are in [references/design.md](references/design.md).

Headless alternative (state in the file, not the app): write the same
`{"command", "params"}` objects, one per line, to `script.jsonl` and run
`figcraft-cli run script.jsonl --in base.figcraft --out out.figcraft`. It is
atomic: any failing step exits 1 and saves nothing, so fix the step and rerun
the whole script.

### Step 4: Verify (model first, pixels second)

1. Model: `figcraft-live inspect <id> <depth>` (`node.get`) or
   `figcraft-live inspect <depth>` (`document.inspect`) give solved
   `width`/`height` and `absoluteBounds` (CLI: `figcraft-cli convert
   out.figcraft check.json`). A frame at `100×100` means a missing
   `sizingH`/`sizingV`, with children silently clipped.
2. Pixels: `figcraft-live render check.png --ids '[<frameId>]'` (`ui.render`).
   **Without `--ids` it renders the current selection**, not the page — pass
   the frame ids explicitly, or `select.set` first. `--ui` captures the whole
   app window (`ui.screenshot`) when the chrome itself matters. Headless:
   `figcraft-cli render out.figcraft -o check.png`. Look for: nothing clipped
   at the canvas edge, the intended element order, fills where expected,
   labels inside containers, every placed image visible and cropped as
   intended. Judge gaps from the model, not ink, because ink includes text
   leading.
3. Fix with `edit.undo` or `node.set`, then verify again before the next
   section.

### Step 5: Save and export

- `figcraft-live exec file.save {"path": ...}` after each section. Keep the
  `.figcraft` archive as the editable source.
- Assets: `figcraft-live exec file.export {"ids", "format", "scale", "path"}`
  in the app, or the richer headless `figcraft-cli export out.figcraft -o
  exports/ --scale 2` (PDF bleed/crop marks, per-node and per-page output).
  Options and export quirks: [references/cli.md](references/cli.md).
- Dev-Mode code: `figcraft-live exec inspect.code {"id?", "language":
  "css|html|react|leptos|vue|tailwind|swiftui|compose|arkui|flutter"}` on a
  layer (default: the selection; default language `css`).

### Step 6: Wind down

Leave the app running when design work continues soon (the user keeps the
canvas). At the end of a design phase: save, then `figcraft-live stop`
(`--force` required for adopted instances; unsaved changes are discarded).

## Conventions

- Coordinates are page units, y grows down; `x`/`y` are relative to the
  parent.
- Colors are `"#RRGGBB"` or `"#RRGGBBAA"`.
- Creation commands return `{"id": N}`: capture ids from results or use
  `as`/`$ref`; never assume them.
- Every mutation is one undo step (`edit.undo` / `edit.redo` step the
  history); programmatic calls never open dialogs.
- Live sessions use the app's fonts, system fonts included. For CI-stable
  renders use the CLI with `--no-system-fonts` (or
  `FIGCRAFT_NO_SYSTEM_FONTS=1`).
- Former MCP tool names map to the registry and control methods:

| MCP tool (old)          | Controller route                                              |
| ----------------------- | ------------------------------------------------------------- |
| `run_command`           | `figcraft-live exec <command> <params>` (`engine.execute`)    |
| `batch`                 | `figcraft-live batch <file\|->` (`command.batch`)             |
| `inspect_document`      | `figcraft-live inspect <depth>` (`document.inspect`)          |
| `get_node`              | `figcraft-live inspect <id> <depth>` (`node.get`)             |
| `select`                | `figcraft-live exec select.set {"ids"}`                       |
| `screenshot`            | `figcraft-live render out.png [--ids] [--ui]`                 |
| `export`                | `figcraft-live exec file.export {...}`                        |
| `open_file`/`save_file` | `figcraft-live exec file.open` / `file.save`                  |
| `undo`/`redo`           | `figcraft-live exec edit.undo` / `edit.redo`                  |
| `list_commands`         | `figcraft-cli commands [--filter]` (`engine.commands` in-app) |
| `inspect_ui`            | `figcraft-live rpc ui.inspect {}`                             |

## Failure Handling

| Symptom                                              | Cause and action                                                                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `no open document`                                   | Fresh app: `file.new` or `file.open`.                                                                                |
| `cannot connect` / `status` says not running         | Expected before the first live command; run one, or `figcraft-live start`.                                           |
| Launch fails, or the port never opens                | Non-macOS host, missing app, or `open` unavailable: report it; use the `file` route instead.                         |
| `FIGCRAFT_PORT=… is busy and is not FigCraft`        | A pinned port is occupied by a foreign service; free it or repin.                                                    |
| `stop` refuses an adopted instance                   | By design: save first, then `--force`.                                                                               |
| A frame solves to 100×100, or an element missing     | Parent frame lacks `sizingH`/`sizingV`; fix the parent, not the child.                                               |
| `unsupported image: …format could not be determined` | Not an image file, or wrong path; check the file, convert to PNG/JPG/WebP.                                           |
| `automation path rejected`                           | File outside the app's `--automation-read-root`/`-write-root`; move the file or restart the app without confinement. |
| A call fails mid-edit                                | It may have applied: `inspect` the document, then retry only what is missing.                                        |
| `control request queue is full`                      | More than 8 queued requests; back off, send smaller batches.                                                         |
| Render looks tiny or empty                           | `ui.render` without `ids` renders the selection; pass the frame ids.                                                 |

## Gotchas

- **Auto-layout frames never size themselves.** Without `sizingH`/`sizingV`
  (or explicit width/height) a frame solves to a fixed 100×100, and frames
  clip children by default.
- **Frames default to a white fill.** Wrappers need `"fill": "none"`.
- **Vector icons stretch** when both `width` and `height` are given; give one.
  See [references/design.md](references/design.md).
- **An app already running without a control port cannot be attached.** The
  middleware opens its own instance (`open -n`), so two FigCraft windows
  appear. Never kill the user's instance; let them quit it.
- **`ui.render` renders the selection by default** — almost always pass
  `--ids`.
- **`image.place` input**: a local path or base64 `data` only. In live mode
  the app opens the path, so it must exist on that machine and sit inside
  `--automation-read-root` when one is set. Use stdin (`-`) for large base64
  payloads; shell arguments cap out first.
- **`file.save` refuses to clobber external writes** without `overwrite:
  true`; with worktrees that means another session saved the file — re-open
  instead of force-saving over it.

## Output Contract

On completion, report:

1. The state used (`file` or `live`; for `live`: whether the app was started
   or adopted, and the port), and why when not live.
2. The document path(s) created or modified, with key node ids and names.
3. Every placed image (source path, target node id, mode) and every exported
   asset path with format and scale.
4. How the result was verified (model check, pixel check) and any warnings
   the tools printed.

## References

- [references/control.md](references/control.md): the controller, the control
  protocol (methods, limits), and the tool-to-method map.
- [references/images.md](references/images.md): `image.place`, fills, avatars,
  adjustments, SVG import, image checks.
- [references/design.md](references/design.md): construction patterns (page
  skeleton, buttons, icons, tokens) and the verification checklist.
- [references/setup.md](references/setup.md): CLI probe, install, build, app
  notes.
- [references/cli.md](references/cli.md): `figcraft-cli` subcommands, flags,
  exit codes, export gotchas.
