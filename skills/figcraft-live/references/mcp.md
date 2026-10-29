# FigCraft MCP reference

Verified against `docs/mcp.md` in storytold/figcraft (main, 2026-10) and
exercised on figcraft-cli 0.12.1: both modes answer `initialize`, expose the
same 18 tools (`list_commands`, `run_command`, `batch`, `create_node`,
`set_properties`, `inspect_document`, `get_node`, `select`, `export`,
`screenshot`, `open_file`, `save_file`, `undo`, `redo`, `pointer`, `key`,
`type_text`, `inspect_ui`), and place images. The server lives in
`crates/mcp` and is launched through the CLI.

Contents: modes · protocol · client registration (wrapper) · manual attached launch · session loop · tools · example calls · conventions

## Modes

| Command                          | Backend                                                                   |
| -------------------------------- | ------------------------------------------------------------------------- |
| `figcraft-cli mcp`               | Headless: in-process engine, one untitled document, no window, CPU render |
| `figcraft-cli mcp --attach PORT` | Attached: drives a running app started with `figcraft --control PORT`     |

`--attach` also accepts `host:port`; the control channel listens on
127.0.0.1 only. Build first (`cargo build --release -p figcraft-cli`) and
call the binary by absolute path (`target/release/figcraft-cli`). Linux
AppImage: `FigCraft.AppImage cli mcp` works in place of `figcraft-cli mcp`.

## Protocol

Newline-delimited JSON-RPC 2.0 over stdio; MCP `2025-06-18` (clients on
`2025-03-26` and `2024-11-05` accepted). Frames are capped at 32 MiB before
the newline; oversized input yields JSON-RPC error `-32600` and closes the
session.

Attached-mode caveat: calls are never auto-replayed after a transport
failure because the edit may have applied; inspect before retrying. The next
explicit call reconnects.

## Client registration

Register one server, `figcraft`, at user level, pointing at the wrapper
`figcraft-live-mcp` (installed to `~/.local/bin` from the skill's
`scripts/` directory). Use the absolute path: GUI-launched clients do not
inherit the shell `PATH`, and JSON configs do not expand `~`.

Why a wrapper: `figcraft-cli mcp --attach PORT` exits at startup when no
app is listening (omp reports `MCP subprocess closed stdout before
responding`), so registering it directly warns in every session and fails
whenever the app is closed. The wrapper removes that:

1. If `127.0.0.1:$FIGCRAFT_CONTROL_PORT` (default 7979) is closed, it
   launches the app with `open -n -g -a FigCraft.app --args --control PORT`
   and waits up to `FIGCRAFT_LIVE_WAIT` seconds (default 30) for the port.
2. Port open: `exec figcraft-cli mcp --attach PORT` (live mode).
3. No app, a launch error, a timeout, a non-macOS host, or `--headless`:
   `exec figcraft-cli mcp` (headless; any extra args are passed through).

It logs its choice on stderr (`attached to the FigCraft app on port 7979`
or `headless mode, no live preview: <reason>`). Environment overrides:
`FIGCRAFT_CLI`, `FIGCRAFT_APP`, `FIGCRAFT_CONTROL_PORT`,
`FIGCRAFT_LIVE_WAIT`. Exit code 127 (message on stderr) means
`figcraft-cli` was not found. The launched app is not tied to the MCP session: it
keeps running, with its documents, after the client exits.

Optional second entry `figcraft-headless` with `"args": ["--headless"]` for
unattended runs next to the live server.

Claude Code:

```sh
install -m 755 <skill-dir>/scripts/figcraft-live-mcp ~/.local/bin/
claude mcp add --scope user figcraft -- "$HOME/.local/bin/figcraft-live-mcp"
```

Claude Desktop, project `.mcp.json`, and omp (same `mcpServers` shape as
the other servers there):

```json
{
  "mcpServers": {
    "figcraft": { "command": "/Users/<you>/.local/bin/figcraft-live-mcp" }
  }
}
```

Merge into the existing `mcpServers` object; never overwrite the file. omp
keeps one `mcp.json` per profile (`~/.omp/profiles/<name>/agent/mcp.json`
when `OMP_PROFILE` is set); edit the active one. In omp the tools mount as
`xd://mcp__figcraft_<tool>` devices (for example
`xd://mcp__figcraft_run_command`); write the tool's JSON arguments to that
path, or call them from `eval` with `tool.mcp__figcraft_<tool>(args)`.
Extra `args` are passed to `figcraft-cli mcp` only in headless mode:
`--no-system-fonts` (CI-stable text), `--automation-read-root DIR` /
`--automation-write-root DIR` (confine which files images and exports may
touch). In live mode the app confines files from the flags it was started
with, which the wrapper does not set.

New servers load when the client reloads MCP servers or restarts, not in
the running session. Until then use the CLI route from SKILL.md.

## Manual attached launch

Only when debugging the wrapper. macOS (the app bundle ships the app
binary but no CLI):

```sh
/Applications/FigCraft.app/Contents/MacOS/FigCraft --control 7979
```

Wait for `FigCraft control server listening on 127.0.0.1:7979`, then run
`figcraft-cli mcp --attach 7979`. Confinement flags (`--automation-read-root`,
`--automation-write-root`) go on the app command, not on `mcp --attach`.
The app starts with no document: call `run_command {command: "file.new"}`
(or `open_file`) before editing, or every call fails with `no open
document`. The wrapper uses `open -n` so a second instance starts with
`--control` even while the user's own instance is running (observed: both
ran side by side).

## Session loop

1. `list_commands {filter}` for any command not already documented here.
2. `inspect_ui` (headless reports `"backend": "headless"`), then
   `run_command {command: "file.new"}`; reuse that document for the whole
   session.
3. Per section: `batch` the creates (and `image.place` calls), then
   `get_node` / `inspect_document` for the solved model, then `screenshot`
   to look at pixels. Fix and repeat; `undo` reverts a bad batch.
4. `save_file {path}` after each section (headless state is in memory only).
5. `export {ids, format, scale, path}` for deliverables.

## Tools

| Tool                                                                              | Behavior                                                                                                                                |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `list_commands {filter?}`                                                         | Every command: id, label, menu, shortcut, undoable flag, params doc.                                                                    |
| `run_command {command, params}`                                                   | Run any registry command (`align.left`, `layout.add`, `component.create`, `instance.place`, `inspect.code`, `file.newFromTemplate`, …). |
| `batch {commands: [{command, params}], label?}`                                   | Several commands as one undo step.                                                                                                      |
| `create_node {type, x, y, width, height, parent, index, name, text, path, props}` | Returns `{id, node}`.                                                                                                                   |
| `set_properties {ids, props}`                                                     | `node.set` on layers.                                                                                                                   |
| `inspect_document {depth, allPages}`                                              | Document as JSON.                                                                                                                       |
| `get_node {id, depth}`                                                            | One layer as JSON.                                                                                                                      |
| `select {ids}`                                                                    | Replace the selection.                                                                                                                  |
| `export {ids, format, scale \| size, path?, bleed?, cmyk?, svgOutlineText?, …}`   | png/jpg/svg/webp/pdf/fig; without `path`, returns MCP image content inline.                                                             |
| `screenshot {ids?, scale?, maxSize?, window?}`                                    | PNG of the page, layers, or app window.                                                                                                 |
| `open_file {path, variables?}` / `save_file {path?}`                              | Open `.figcraft`, `.json`, `.fig`, `.svg`, images; save the document.                                                                   |
| `undo` / `redo`                                                                   | Step the undo history.                                                                                                                  |
| `pointer {kind, x, y, to?, steps?, tool?, shift, alt, cmd, pressure?}`            | Mouse gestures.                                                                                                                         |
| `key {key, shift, alt, cmd}`                                                      | Shortcuts as if typed.                                                                                                                  |
| `type_text {text, id?}`                                                           | Type into the edited text, or replace a text layer.                                                                                     |
| `inspect_ui {}`                                                                   | Tool, view, status, and windows (attached mode).                                                                                        |

## Example calls

Start from a template:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "run_command",
    "arguments": { "command": "file.newFromTemplate", "params": { "template": "dashboard" } }
  }
}
```

Shape builder:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "run_command",
    "arguments": {
      "command": "shapeBuilder.merge",
      "params": {
        "ids": [2, 3],
        "points": [
          [120, 80],
          [160, 80]
        ]
      }
    }
  }
}
```

## Conventions

Coordinates, colors, ids, undo semantics, and the never-open-dialogs rule
are as in the "Conventions" section of SKILL.md. Headless fonts match
the desktop app; pass `--no-system-fonts` or set `FIGCRAFT_NO_SYSTEM_FONTS=1`
for CI-stable renders.
