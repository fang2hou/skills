# FigCraft JSON control protocol

Verified against `docs/control-protocol.md` in `storytold/figcraft` (v0.6.0) and live-tested with `figcraft-cli` 0.12.1 across `window.list`, `engine.execute` (including `command.batch`), `document.inspect`, `node.get`, `ui.render`, `file.new`, `file.save`, `file.close`, and `app.quit`. The `figcraft-live` MCP server proxies its tool calls over this loopback protocol; use this reference when debugging the server or driving the socket directly.

Contents:

- [MCP tools to control methods](#mcp-tools-to-control-methods)
- [Starting the control listener](#starting-the-control-listener)
- [Message format](#message-format)
- [Protocol limits](#protocol-limits)
- [Methods](#methods)
- [Shell session example](#shell-session-example)
- [Upstream implementation](#upstream-implementation)

## MCP tools to control methods

The `figcraft-live` MCP server ([mcp.md](mcp.md)) maps each MCP tool to the following control methods:

| MCP Tool   | Control Method(s)                                                         |
| ---------- | ------------------------------------------------------------------------- |
| `status`   | `window.list` (health probe and open window/tab list)                     |
| `ensure`   | Adopt-or-launch instance resolution, then `file.open` or `file.new`       |
| `exec`     | `engine.execute {command, params}`                                        |
| `batch`    | `engine.execute {command: "command.batch", params: {label?, commands[]}}` |
| `inspect`  | `node.get {id, depth}` (with `id`) or `document.inspect {depth}`          |
| `render`   | `ui.render {path, scale?, ids?}` or `ui.screenshot {path}` (`window`)     |
| `commands` | `engine.commands {}` (filtered client-side by regex when `filter` is set) |
| `stop`     | `app.quit {}` (guarded when `origin` is `adopted`)                        |

## Starting the control listener

```sh
figcraft --control 7979 [file.figcraft|file.svg|image]
# Or from a source checkout:
cargo run -p figcraft -- --control 7979
```

The app listens on `127.0.0.1:<port>` only and never binds to external network interfaces.

## Message format

The socket uses newline-delimited JSON (NDJSON): send one JSON request line and read one JSON reply line in order.

```json
{"id": 1, "method": "engine.execute", "params": {"command": "frame.create", "params": {"width": 390, "height": 844}}}
{"id": 1, "ok": true, "result": {"id": 2}}
{"id": 1, "ok": false, "error": "message"}
```

Requests execute on the UI thread at the start of the next frame. If a UI request does not complete within 60s, the server replies with a timeout error. Malformed JSON lines return `{"id": null, "ok": false, "error": "bad JSON: …"}`.

## Protocol limits

| Limit              | Value                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| Network binding    | Loopback socket only (`127.0.0.1`)                                                                   |
| Request line size  | 32 MiB max; larger lines return `message too large` and close the connection                         |
| Active connections | 8 concurrent connections max; additional connections are closed immediately                          |
| Inactivity timeout | 60s on socket reads and writes (idle clients release their worker slot)                              |
| Request queues     | Socket queue and UI queue hold 8 requests each; a full queue returns `control request queue is full` |
| Native dialogs     | Programmatic calls never open OS file dialogs; dialog-triggering requests are dropped                |

## Methods

### Commands and documents

- `engine.execute {command, params?}`: Runs any registry command (using the same IDs as menus, shortcuts, CLI, and MCP). Creation commands return `{"id": N}`.

  ```json
  {
    "id": 1,
    "method": "engine.execute",
    "params": {
      "command": "shape.rectangle",
      "params": { "x": 10, "y": 10, "width": 100, "height": 50 }
    }
  }
  ```

- `engine.commands {}`: Lists all commands with `id`, `label`, `params`, `menu`, `shortcut`, and `undoable`.
- `document.inspect {depth?, allPages?}`: Dumps the active document tree as JSON (pages, selection, styles, `colorProfile`, undo history).
- `node.get {id, depth?}`: Returns one layer and its full property set (bounds, fills, layout, overrides, `devStatus`).

### UI driving

- `ui.inspect {}`: Returns full UI state (panels, active tool, cursor, viewport, frame timing, prototype player, collaboration state, and open tabs).
- `ui.pointer {kind, x,y | sx,sy, to?, steps?, shift?, alt?, cmd?, ctrl?, pressure?, pressureTo?}`: Simulates mouse gestures (`down`, `move`, `up`, `click`, `double`, `hover`, `drag`) in page coordinates or screen pixels. Returns `{selection, tool}`.
- `ui.key {key, shift?, alt?, cmd?, ctrl?}`: Sends canvas keystrokes (shortcuts, tool switches, nudges, text editing). Returns `{"command": id}` when a shortcut triggers.
- `ui.type {text}`: Types text into the active text-editing node.
- `ui.input {events}`: Sends raw window events reaching panels and text fields: `{move:[x,y]}`, `{down:[x,y], button?}`, `{up:[x,y], button?}`, `{key, …}`, `{text}`, `{scroll:[dx,dy]}`, `{leave:true}`, `{hold:{alt, …}}`, `{gamepad: …}`. All events in a single call arrive in the same frame, so send press and release in separate calls. Returns `{queued}`.
- `ui.menu.invoke {id}`: Invokes a menu item by ID. Returns `{ok, lastError}`.
- `ui.set {...}`: Switches panels or UI modes (`rightTab`, `leftTab`, `theme`, `home`, `palette`, `mainMenu`, `variables`, `colorPicker`, `contextMenu`, `preview`, comment/Dev-Mode options, `resetFrameStats`). Returns the updated `ui.inspect` state.
- `ui.screenshot {path}`: Captures the entire window including UI chrome to a PNG file (requires a visible window). Returns `{path, width, height}`, or times out after 60s.
- `ui.render {path, scale?, ids?}`: Renders document layers to a PNG file without UI chrome (works even when the window is in the background). **When `ids` is omitted, it exports only the current selection.**

### Windows and app lifecycle

- `window.new {path?, index?}`: Opens a new window with a moved tab, a file path, or an empty document. Returns `{window}`.
- `window.list {}`: Lists open windows: `[{id, main, title, files, active, focused}]`.
- `window.focus {id}`: Brings a window to the front and makes it the default target for calls that omit `window`.
- `app.quit {}`: Closes all windows immediately without prompting to save unsaved changes.

Every method accepts an optional `window` ID (`0` is the main window). When omitted, requests target the most recently focused window.

## Shell session example

`/dev/tcp` redirection is a Bash built-in (not supported in `zsh`). Run this snippet in `bash`:

```sh
port=7979
figcraft --control "$port" &
exec 3<>/dev/tcp/127.0.0.1/"$port"
echo '{"id":1,"method":"engine.execute","params":{"command":"frame.create","params":{"preset":"iPhone 16","x":0,"y":0}}}' >&3
read -r reply <&3; echo "$reply"
echo '{"id":2,"method":"ui.screenshot","params":{"path":"/tmp/figcraft.png"}}' >&3
read -r reply <&3; echo "$reply"
exec 3<&- 3>&-
```

## Upstream implementation

Implemented in `crates/ui-egui/src/control.rs` and `apps/figcraft/src/control_server.rs` in the `storytold/figcraft` repository.
