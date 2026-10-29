---
name: figcraft-live
description: >
  Pair-designs live in the FigCraft desktop app (github.com/storytold/figcraft) over MCP:
  the user watches the canvas while the agent builds layouts, places images, and exports.
  Use for FigCraft or .figcraft work.
license: MIT
compatibility: macOS with the FigCraft desktop app for live editing; needs figcraft-cli (auto-installed to ~/.local/bin) and falls back to a headless session with no preview elsewhere.
metadata:
  author: fang2hou
  version: "2.1"
---

# FigCraft Live

Design inside [FigCraft](https://github.com/storytold/figcraft) with the user
watching. The default channel is live MCP: the agent creates layers, places
images, and checks screenshots while the user sees each change on the canvas
and can intervene. The wrapper `figcraft-live-mcp` starts the app and attaches
automatically. Headless MCP (no window) and CLI `run` scripts are fallbacks
for unattended work, CI, and replayable batches.

## When to Use

- The user asks to design, mock up, or prototype a UI in FigCraft.
- The user wants to watch, steer, or hand-tweak the design while the agent
  edits it ("live", "preview", "pair on this design").
- A `.figcraft` file (or a best-effort `.fig`/`.svg`/image import) needs
  inspecting, converting, rendering, or exporting.
- Design assets (PNG/SVG/WebP/PDF) or Dev-Mode code (CSS, HTML, React,
  Leptos, SwiftUI, Compose) must be produced reproducibly.

## When NOT to Use

- The npm package `figcraft` (a TypeScript SVG-diagram library): a different
  product; never `npm install figcraft`.
- Administering `figcraft-server` (share links, keys, IP blocks): read the
  upstream `docs/server.md`.
- Developing FigCraft itself or writing WASM plugins: see the upstream
  repository's contributing guide and `docs/plugins.md`.

## Interfaces

Default to live MCP: the wrapper launches the app with its control channel
(port 7979), attaches `figcraft-cli mcp --attach` to it, and keeps one live
document across calls with inline screenshots and every command (including
`image.place`).

| Situation                                                | Interface          | Entry point                                                        |
| -------------------------------------------------------- | ------------------ | ------------------------------------------------------------------ |
| Design, edit, add images, verify visually (default)      | MCP live           | MCP server `figcraft` = `figcraft-live-mcp` (app attached)         |
| App cannot start (no app, non-macOS, SSH), or unattended | MCP headless       | same server, automatic fallback; or `figcraft-live-mcp --headless` |
| MCP tools not mounted in this session yet                | CLI run script     | `figcraft-cli run script.jsonl --out out.figcraft`                 |
| Replayable batch, CI, or scripted exports                | CLI run script     | `figcraft-cli run` / `render` / `export`                           |
| Inspect/convert/render/export an existing file once      | CLI subcommands    | `figcraft-cli info\|convert\|render\|export`                       |
| Raw low-level control without MCP                        | JSON control layer | [references/control.md](references/control.md)                     |

All interfaces share one registry of 400+ commands (`frame.create`,
`layout.add`, `image.place`, `component.create`, …): anything clickable in the
UI has a command id usable from MCP `run_command`, the CLI, and the control
channel. Tool names carry a client-specific prefix (for example
`mcp__figcraft__run_command`); this skill uses the bare names.

## Hard Rules

1. Discover commands before using them (`list_commands {filter}` over MCP,
   `figcraft-cli commands --filter <text>` on the CLI) and read their
   parameter docs; guessed ids and params fail.
2. Group related edits into one undo step with `batch`, one section per
   batch. A failing batch rolls back entirely and the error names the step.
3. Work in your own document and save it. Start with `file.new` (or
   `open_file`) so the user's other tabs stay untouched, then `save_file
   {path}` after each completed section. The saved `.figcraft` is the source
   of truth; a headless document is lost when the server exits.
4. The user shares the canvas. Re-read a layer with `get_node` before editing
   anything the user may have touched. Do not use `pointer`, `key`, or
   `type_text` unless asked: they act on the user's tool, selection, and
   keyboard focus. Build section by section so the user sees steady
   progress, and `select` the section just built to highlight it.
5. In live mode a failed call may still have applied. Inspect the document
   before retrying.
6. Images enter only as a local file `path` or base64 `data` (no URL
   parameter): obtain the file first, then place it. See
   [references/images.md](references/images.md).
7. Build with auto layout; never absolutely position text over shapes. Every
   layout frame declares `sizingH`/`sizingV`, and body text needs contrast of
   at least 4.5:1. See [references/design.md](references/design.md).
8. A command succeeding is not a verified result: verify as in Step 4.

## Setup

Run this at the start of every FigCraft task without asking permission, and
report the outcome (CLI found or installed; MCP mounted or not; live or
headless) in the first progress note.

1. CLI: `command -v figcraft-cli`, then `figcraft-cli --version` and
   `figcraft-cli commands --filter frame | head`. Missing or failing → install
   or rebuild per [references/setup.md](references/setup.md) (checksum-verified
   release into `~/.local/bin`; stop if the checksum is not `OK`).
2. Wrapper: copy `scripts/figcraft-live-mcp` from this skill's directory to
   `~/.local/bin/` (`install -m 755`) and re-copy when the skill's copy
   differs. Live mode needs macOS `open` and `nc`; without them it falls back
   to headless.
3. MCP: the session should list FigCraft tools (`list_commands`,
   `run_command`, `batch`, `screenshot`, …) under a `figcraft` server. Mounted
   → call `inspect_ui` as the smoke test. Not registered → register `figcraft`
   pointing at the wrapper's absolute path (commands and JSON for Claude Code,
   Claude Desktop, and omp are in [references/mcp.md](references/mcp.md)). A
   new registration is not live until the client reloads MCP servers: tell the
   user and continue on the CLI route (`image.place` works there too).
4. The first MCP connection starts the app if needed (up to 30 s) and leaves
   it running, so the user keeps the design open.

## Workflow

### Step 1: Connect, then open or start a document

- `inspect_ui`: `backend: "headless"` means the user cannot watch (say so and
  offer screenshots or exported PNGs); otherwise the app is attached and
  `status.documents` counts the open tabs.
- Existing file: `open_file {path}` returns an outline plus any
  `warnings`/`repairs`. CLI: `figcraft-cli info design.figcraft --json`.
- New design: `run_command {command: "file.new", params: {name?}}` (or
  `file.newFromTemplate`) even when tabs are open. A fresh app with zero
  documents rejects every edit with `no open document`. Reuse your document
  for the rest of the session; each `file.new` adds a tab.

### Step 2: Discover commands

`list_commands {filter: "image"}` (or `layout`, `frame`, …) returns each
command's id, shortcut, and parameter doc.

### Step 3: Make the edit

Build one section at a time with `batch`. Name a step with `as` and reference
its new id with `{"$ref": name}` instead of counting ids; this also works in
`figcraft-cli run` scripts:

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

Print each result's ids and `warnings`; do not discard them. Single layers can
use `create_node` / `set_properties`. Images: `run_command {command:
"image.place", params: {path, parent, width, height}}` (see
[references/images.md](references/images.md)). More patterns (buttons, icons,
dividers, avatars) are in [references/design.md](references/design.md).

CLI fallback: write the same `{"command", "params"}` objects, one per line, to
`script.jsonl` and run `figcraft-cli run script.jsonl --in base.figcraft --out
out.figcraft`. It is atomic: any failing step exits 1 and saves nothing, so
fix the step and rerun the whole script.

### Step 4: Verify (model first, pixels second)

1. Model: `get_node {id, depth}` or `inspect_document {depth}` give solved
   `width`/`height` and `absoluteBounds` (CLI: `figcraft-cli convert
   out.figcraft check.json`). A frame at `100×100` means a missing
   `sizingH`/`sizingV`, with children silently clipped.
2. Pixels: `screenshot {ids?, scale?}` or `export` without `path` returns the
   image inline (CLI: `figcraft-cli render out.figcraft -o check.png`). Look
   for: nothing clipped at the canvas edge, the intended element order, fills
   where expected, labels inside containers, every placed image visible and
   cropped as intended. Judge gaps from the model, not ink, because ink
   includes text leading.
3. Fix with `undo` or `set_properties`, then verify again before the next
   section.

### Step 5: Save and export

- `save_file {path}` (or `--out` on `run`). Keep the `.figcraft` archive as the
  editable source.
- Assets: `export {ids, format, scale, path}` (inline image without `path`), or
  `figcraft-cli export out.figcraft -o exports/ --scale 2`. Options (`--node`,
  `--format`, PDF bleed and crop marks) and export quirks are in
  [references/cli.md](references/cli.md).
- Dev-Mode code: `run_command {command: "inspect.code"}` on the selection
  emits CSS/HTML/React/Leptos/SwiftUI/Compose.

## Conventions

- Coordinates are page units, y grows down; `x`/`y` are relative to the parent.
- Colors are `"#RRGGBB"` or `"#RRGGBBAA"`.
- Creation commands return `{"id": N}`: capture ids from results or use
  `as`/`$ref`; never assume them.
- Every mutation is one undo step; programmatic calls never open dialogs.
- Live sessions use the app's fonts, system fonts included. For CI-stable
  renders use the CLI with `--no-system-fonts` (or `FIGCRAFT_NO_SYSTEM_FONTS=1`).

## Failure Handling

| Symptom                                                    | Cause and action                                                                               |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `no open document`, or `screenshot` says the page is empty | Fresh app: run `file.new` or `open_file`.                                                      |
| `inspect_ui` reports `backend: "headless"`                 | No app: the wrapper fell back (reason on its stderr). Tell the user; continue without preview. |
| A frame solves to 100×100, or an element is missing        | Parent frame lacks `sizingH`/`sizingV`; fix the parent, not the child.                         |
| `unsupported image: …format could not be determined`       | Not an image file, or wrong path; check the file, convert to PNG/JPG/WebP.                     |
| `automation path rejected`                                 | File outside the app's or server's `--automation-read-root`/`-write-root`; move the file.      |
| Attached call fails with "may have completed"              | Transport loss after send: `get_node`/`inspect_document`, then retry only if not applied.      |
| New MCP server not listed                                  | Client has not reloaded servers; tell the user, use the CLI route meanwhile.                   |

## Gotchas

- **Auto-layout frames never size themselves.** Without `sizingH`/`sizingV`
  (or explicit width/height) a frame solves to a fixed 100×100, and frames
  clip children by default.
- **Frames default to a white fill.** Wrappers need `"fill": "none"`.
- **Vector icons stretch** when both `width` and `height` are given; give one.
  See [references/design.md](references/design.md).
- **An app already running without the control port cannot be attached.** The
  wrapper opens a second instance (`open -n`), so two FigCraft windows appear.
  Never kill the user's instance; let them quit it.
- **The attached app survives the MCP session** with its unsaved documents
  still open; a headless document does not.
- **`image.place` input**: a local path or base64 `data` only. In live mode
  the app opens the path, so it must exist on that machine and sit inside
  `--automation-read-root` when one is set.
- **Headless-only features**: `collab.*` and plugin-directory commands need an
  MCP session (live or headless); one-shot `run` has no network link.

## Output Contract

On completion, report:

1. The interface used (live MCP, headless MCP, or CLI, and why when not live;
   headless means the user could not watch).
2. The document path(s) created or modified, with key node ids and names.
3. Every placed image (source path, target node id, mode) and every exported
   asset path with format and scale.
4. How the result was verified (model check, pixel check) and any warnings the
   tools printed.

## References

- [references/mcp.md](references/mcp.md): MCP tool catalogue, the wrapper,
  client registration (Claude Code, Claude Desktop, omp), session loop.
- [references/images.md](references/images.md): `image.place`, fills, avatars,
  adjustments, SVG import, image checks.
- [references/design.md](references/design.md): construction patterns (page
  skeleton, buttons, icons, tokens) and the verification checklist.
- [references/setup.md](references/setup.md): CLI probe, install, build, app notes.
- [references/cli.md](references/cli.md): `figcraft-cli` subcommands, flags,
  exit codes, export gotchas.
- [references/control.md](references/control.md): raw JSON control protocol.
