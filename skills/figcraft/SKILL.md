---
name: figcraft
description: >
  Drives FigCraft (the Rust design app, not the npm figcraft package) via its CLI,
  MCP, or JSON control channel to edit, batch-script, export, and screenshot-verify
  designs. Use when designing or prototyping UI in FigCraft or for .figcraft files.
license: MIT
compatibility: Auto-installs the prebuilt figcraft-cli release to ~/.local/bin when missing and verifies it before use; the desktop app is required only for attached mode.
metadata:
  author: fang2hou
  version: "1.1"
---

# FigCraft

Operate FigCraft (the open-source, pure-Rust interface design tool) from
scripts and coding agents: build and edit design documents, run command
batches, export PNG/SVG/PDF assets, and verify the result visually without
driving the GUI by hand.

## When to Use

- The user asks to design, mock up, or prototype a UI "in FigCraft" or in the
  Rust "Figma alternative".
- A `.figcraft` file (or a best-effort `.fig`/`.svg`/image import) needs
  inspecting, converting, rendering, or exporting.
- Generated design assets (PNG/SVG/WebP/PDF) or Dev-Mode code (CSS, HTML,
  React, Leptos, SwiftUI, Compose) must be produced reproducibly.
- An automated flow should drive the visible FigCraft app while the user
  watches (attached mode).

## When NOT to Use

- The npm package `figcraft` (XFlow's TypeScript SVG-diagram library with its
  `figcraft-mcp` server). That is a different product; do not `npm install figcraft`.
- Administering the self-hosted collaboration `figcraft-server` (share links,
  keys, IP blocks). Read the upstream `docs/server.md` directly.
- Developing FigCraft itself or writing WASM plugins. See the upstream
  repository's contributing guide and `docs/plugins.md`; this skill drives
  the released tool.

## Interfaces

Default to the CLI `run` script: it is headless, atomic, and replayable. Switch to MCP only when the work needs iterative visual checks or the visible app.

| Situation                                           | Interface          | Entry point                                                  |
| --------------------------------------------------- | ------------------ | ------------------------------------------------------------ |
| Inspect/convert/render/export an existing file once | CLI subcommands    | `figcraft-cli info\|convert\|render\|export`                 |
| Build or edit a document as one repeatable batch    | CLI run script     | `figcraft-cli run script.json --out out.figcraft`            |
| Iterative scripted editing with visual checks       | MCP headless       | `figcraft-cli mcp`                                           |
| Drive the running desktop app (user watching)       | MCP attached       | `figcraft --control 7979` + `figcraft-cli mcp --attach 7979` |
| Raw low-level control without MCP                   | JSON control layer | see [references/control.md](references/control.md)           |

All interfaces share one registry of 400+ commands (`frame.create`,
`layout.add`, `align.left`, `component.create`, `instance.place`,
`file.newFromTemplate`, …): anything clickable in the UI has a command id
usable from the CLI, MCP, and the control channel.

## Hard Rules

1. Never guess command ids or parameters. Discover first
   (`figcraft-cli commands --filter <text>` or MCP `list_commands`) and read
   the parameter docs before running.
2. Make multi-step edits one undo step: use MCP `batch` or a single `run`
   script, not a series of loose mutations.
3. Verify in two layers: the solved model first (`figcraft-cli convert
   out.figcraft check.json` gives exact `width`/`height`/`transform` per
   node), then pixels (`render`, or MCP `export` without `path` for the
   image inline). Command success alone is not a verified result.
4. In attached MCP mode, a failed call may still have applied. Never
   blind-retry; inspect the document state first.
5. `figcraft-cli run` is atomic: any failing step exits 1 and saves nothing.
   Fix the step and rerun the whole script.
6. For CI-stable renders pass `--no-system-fonts` (or set
   `FIGCRAFT_NO_SYSTEM_FONTS=1`).
7. Build with auto layout; never absolutely position text over shapes.
   Every layout frame declares `sizingH`/`sizingV`; check WCAG contrast
   (≥ 4.5:1 for body text) before rendering. See "Building designs".

## Setup: ensure the CLI is ready

Default install location: `~/.local/bin/figcraft-cli`. Run this sequence
automatically at the start of every FigCraft task: probe, auto-install the
prebuilt release when missing, then confirm status. Do not ask permission
for these steps; report the outcome (found, installed, or broken) in the
first progress note, and stop only when the checksum or status check fails.

1. Probe for an existing install:

   ```bash
   command -v figcraft-cli || command -v figcraft || command -v figcraft.cli
   ```

   - `figcraft-cli`: native CLI binary; use directly.
   - Linux AppImage: run `FigCraft.AppImage cli <subcommand>` in place of
     `figcraft-cli`; on Linux snap, the headless CLI is `figcraft.cli`.
   - The Homebrew `figcraft` cask and the macOS `.app` bundle contain no CLI
     binary; neither satisfies this probe.

2. Missing → auto-install the prebuilt release (macOS). Download the
   latest universal zip, verify its SHA-256, and unpack into `~/.local/bin`:

   ```bash
   tag=$(curl -sIL -o /dev/null -w '%{url_effective}' https://github.com/storytold/figcraft/releases/latest | sed 's#.*/tag/##')
   ver=${tag#v}
   asset="figcraft-cli-$ver-macos-universal.zip"
   tmp=$(mktemp -d)
   curl -sL -o "$tmp/$asset" "https://github.com/storytold/figcraft/releases/download/$tag/$asset"
   curl -sL -o "$tmp/SHA256SUMS.txt" "https://github.com/storytold/figcraft/releases/download/$tag/SHA256SUMS.txt"
   (cd "$tmp" && shasum -a 256 --check --ignore-missing SHA256SUMS.txt)
   unzip -q "$tmp/$asset" -d "$tmp"
   mkdir -p ~/.local/bin
   mv "$tmp"/figcraft-cli-*/figcraft-cli ~/.local/bin/
   chmod +x ~/.local/bin/figcraft-cli && rm -rf "$tmp"
   ```

   - Keep the zip's original asset filename: `shasum --check` matches names
     in `SHA256SUMS.txt`, so a renamed file verifies nothing and fails with
     "no file was verified".
   - Abort the install when the checksum line does not print `OK`.
   - Linux: download the release AppImage instead and call it as
     `FigCraft.AppImage cli <subcommand>`. Windows has no standalone CLI
     zip; build from source (step 4).
   - The current shell may not resolve `figcraft-cli` right after the
     install; use the absolute path `~/.local/bin/figcraft-cli` for the
     rest of the session. If a fresh shell still cannot find it, add
     `export PATH="$HOME/.local/bin:$PATH"` to the shell rc.

3. Status confirmation (always run, including when step 1 found an
   existing binary). Both must succeed before any other step:

   ```bash
   figcraft-cli --version
   figcraft-cli commands --filter frame | head
   ```

   An existing install that fails here is stale or broken; report it and
   reinstall via step 2 (`~/.local/bin` shadows it on `PATH`).

4. Or build from source (Rust 1.95+; the route for dev versions):

   ```bash
   git clone https://github.com/storytold/figcraft
   cd figcraft
   git clone https://github.com/storytold/craft-fonts ../craft-fonts # optional UI/text fonts
   cargo build --release -p figcraft-cli   # -> target/release/figcraft-cli
   ```

   Not on crates.io (`cargo install figcraft-cli` does not work).

## Workflow

### Step 1: Inspect the input (if any)

```bash
figcraft-cli info design.figcraft --json
```

Read pages, node counts, top-level frame ids/names/sizes, and `notes`
(repair and import warnings; they also print on stderr as `note:` lines).

### Step 2: Discover the exact commands

```bash
figcraft-cli commands --filter autoLayout
figcraft-cli commands --json --filter layout
```

or MCP `list_commands` with `{"filter": "layout"}`.

### Step 3: Make the edit (three routes)

Route A (batch script, headless and atomic): write `script.jsonl` with one
`{"command", "params"}` object per line. This page skeleton with a nav row
and a hug-sized button is the canonical auto-layout pattern; the parent ids
follow creation order (page 1, `Home` 2, `nav` 3, `content` 6, button 7):

```jsonl
{"command": "frame.create", "params": {"x": 0, "y": 0, "width": 390, "height": 844, "name": "Home", "props": {"fill": "#FFFFFF", "layout": "vertical", "padding": 0}}}
{"command": "frame.create", "params": {"parent": 2, "x": 0, "y": 0, "name": "nav", "props": {"layout": "horizontal", "sizingH": "fill", "sizingV": "hug", "padding": [16, 20, 16, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}}}
{"command": "node.create", "params": {"type": "text", "parent": 3, "x": 0, "y": 0, "text": "App", "name": "nav-title", "props": {"fontSize": 17, "fill": "#111827"}}}
{"command": "node.create", "params": {"type": "text", "parent": 3, "x": 0, "y": 0, "text": "Settings", "name": "nav-link", "props": {"fontSize": 15, "fill": "#4B5563"}}}
{"command": "frame.create", "params": {"parent": 2, "x": 0, "y": 0, "name": "content", "props": {"layout": "vertical", "sizingH": "fill", "sizingV": "fill", "padding": 20, "gap": 16}}}
{"command": "frame.create", "params": {"parent": 6, "x": 0, "y": 0, "name": "btn-primary", "props": {"layout": "horizontal", "sizingH": "hug", "sizingV": "hug", "padding": [12, 24, 12, 24], "cornerRadius": 10, "fill": "#111827", "mainAlign": "center", "crossAlign": "center"}}}
{"command": "node.create", "params": {"type": "text", "parent": 7, "x": 0, "y": 0, "text": "Continue", "name": "btn-primary-label", "props": {"fontSize": 15, "fill": "#FFFFFF"}}}
```

```bash
figcraft-cli run script.jsonl --in base.figcraft --out out.figcraft
```

Each step replies with `{"command": …, "ok": true, "result": …, "step": N}`;
capture the returned node ids instead of assuming them.

Route B (MCP headless): register `figcraft-cli mcp` with the agent's MCP
client (see [references/mcp.md](references/mcp.md)), then use `create_node`,
`set_properties`, `run_command`, and `batch`.

Route C (MCP attached): start the app with `figcraft --control 7979`, connect
`figcraft-cli mcp --attach 7979`, and use `inspect_ui`,
`pointer`, `key`, and `type_text` to drive the visible UI, plus `screenshot`
to capture the app window. Attached mode needs the desktop app; if it is
missing, proceed with Route A or B headlessly instead of blocking, and note
that `brew install --cask figcraft` (macOS) provides the app.

### Step 4: Verify (model first, pixels second)

1. Model: `figcraft-cli convert out.figcraft check.json`, then assert every
   frame's solved `width`/`height`/`transform` matches intent. An
   unintended `100×100` frame means a missing `sizingH`/`sizingV`
   declaration (and silently clipped children).
2. Pixels: `figcraft-cli render out.figcraft -o check.png` (or MCP `export`
   without `path`), then check: no ink on canvas edges, the row-band
   structure matches the intended element sequence, color blobs sit where
   fills belong, label ink lands inside its container. Judge element gaps
   from the model because ink gaps include text leading.

### Step 5: Save and export

- Document: `save_file` (MCP) or `--out` (`run`). Keep the `.figcraft` plain
  archive as the editable source.
- Assets: `figcraft-cli export out.figcraft -o exports/ --scale 2` (a
  directory output writes one file per top-level frame); `--node "Hero"` for
  one layer; `--format svg|webp|pdf|…`; print PDF with `--bleed 3mm
  --crop-marks`.
- Dev-Mode code: run the command `inspect.code` on the selection to emit
  CSS/HTML/React/Leptos/SwiftUI/Compose.

## Building designs

Auto layout is the construction system; absolute positioning is only for
full-bleed backgrounds. Core rules (full patterns and the QA checklist
live in [references/design.md](references/design.md)):

- Page frame: fixed viewport size, vertical layout, `padding: 0`. Header
  and footer rows `sizingH: fill` + `sizingV: hug`; the content area
  `fill`/`fill` between them.
- Buttons, chips, nav bars: hug frames with `padding`, `cornerRadius`, and
  `mainAlign`/`crossAlign: center`; the label is a child text node. Never
  fix a label's width and never center text by hand-computed coordinates.
- Dividers: a frame's one-sided stroke (`strokeSides: [t, r, b, l]`
  booleans), not separate line layers.
- Wrapping body text: fixed width + `textAutoResize: "height"`; headings
  and labels keep the default hug.
- Tokens before values: one accent color, a gray ramp, a 4/8 spacing scale,
  semantic layer names; body-text contrast ≥ 4.5:1 (WCAG AA).
- Build and verify section by section (nav, then hero, then footer). Treat the
  `run` script as the single source of truth: edit it and rerun the whole
  script instead of patching the document.

## Shared conventions

- Coordinates are page units with y growing down; `x`/`y` are relative to
  the parent node.
- Colors are `"#RRGGBB"` or `"#RRGGBBAA"`.
- Node ids are assigned in creation order (the first page is 1, the first
  layer is 2). Creation commands return `{"id": N}`; always capture ids from
  results.
- Every mutation is one undo step; programmatic calls never open dialogs.

## Gotchas

- **Auto-layout frames never size themselves.** Without `sizingH`/`sizingV`
  (or explicit width/height) a frame solves to a fixed 100×100, and frames
  clip children by default. A missing or half-clipped element almost
  always means a parent frame lacks a hug/fill declaration.
- **Attached MCP calls are not replayed.** After a transport failure the
  next explicit call reconnects, but the failed call may have applied;
  inspect before retrying.
- **`run` is all-or-nothing.** A failing step exits 1 and writes no output
  file.
- **SVG/PDF export fails beyond 256 nesting levels** of visible descendants;
  export a specific `--node` or reduce nesting.
- **Directory export granularity.** `-o exports/` writes one file per
  top-level frame (or per top-level layer when there are no frames), not one
  per page.
- **Format precedence.** `--format` wins, then the output extension, then
  png; raster `--scale` max is 64.
- **`.fig` import is best-effort**: check `info` notes for skipped
  features.
- **Headless `run` has no network link**: collab (`collab.*`) and
  plugin-directory commands need `figcraft-cli mcp` (headless or attached).
- **Control-channel limits** (attached/raw mode): loopback only, 8
  connections, 8 queued requests, 60 s timeouts, 32 MiB lines;
  dialog-opening requests are dropped.
- **`textAlignVertical: "middle"` does not geometrically center** a
  fixed-height text box (valid values are `top|middle|bottom`). Center
  labels with a layout container (`mainAlign`/`crossAlign: center`). The
  text box centers even when its glyph ink does not fill the box
  symmetrically, so judge centering from the model, not ink centroids.
- **SVG export outlines all text**: glyph paths, with no `<text>` elements to
  grep. Verify text positions from a rendered PNG (pixel sampling), not the
  SVG markup.
- **macOS double-click does not load `.figcraft` files (v0.6.0).** The app
  declares the document type but does not handle LaunchServices document
  Apple Events: double-click launches the app without the file, and a
  stale LaunchServices registration blocks the launch with "cannot
  open" (repair with `lsregister -f /Applications/FigCraft.app`). To open a
  file, drop it into the app window or run
  `open -a FigCraft --args <file>` (argv delivery works; Apple-Event
  delivery does not).
- **The npm `figcraft` package is unrelated** (TypeScript SVG diagrams);
  never install it for this tool.

## Output Contract

On completion, report:

1. The document path(s) created or modified, with key node ids and names.
2. Every exported asset path with format and scale.
3. How the result was verified (model check via `convert`, pixel check via
   `render` or `export`) and any `note:` warnings the tool printed.

## References

- [references/cli.md](references/cli.md): full `figcraft-cli` subcommand,
  flag, and exit-code reference.
- [references/mcp.md](references/mcp.md): MCP tool catalogue and client
  registration (`claude mcp add`, `.mcp.json`).
- [references/control.md](references/control.md): raw JSON control protocol
  for driving the desktop app.
- [references/design.md](references/design.md): design-construction
  patterns (page skeleton, buttons, tokens) and the verification loop.
