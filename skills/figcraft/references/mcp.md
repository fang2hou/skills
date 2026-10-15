# FigCraft MCP reference

Verified against `docs/mcp.md` in storytold/figcraft (v0.6.0, 2026-10). The
server lives in `crates/mcp` and is launched through the CLI.

Contents: modes · protocol · client registration · tools · example calls · conventions

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

```sh
claude mcp add figcraft -- /path/to/figcraft-cli mcp
claude mcp add figcraft-app -- /path/to/figcraft-cli mcp --attach 7979
```

`.mcp.json` / Claude Desktop:

```json
{
  "mcpServers": {
    "figcraft": { "command": "/path/to/figcraft-cli", "args": ["mcp"] },
    "figcraft-app": { "command": "/path/to/figcraft-cli", "args": ["mcp", "--attach", "7979"] }
  }
}
```

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
are as in the "Shared conventions" section of SKILL.md. Headless fonts match
the desktop app; pass `--no-system-fonts` or set `FIGCRAFT_NO_SYSTEM_FONTS=1`
for CI-stable renders.
