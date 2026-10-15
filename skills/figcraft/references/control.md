# FigCraft JSON control protocol

Verified against `docs/control-protocol.md` in storytold/figcraft (v0.6.0,
2026-10). For agents, the upstream docs recommend the MCP wrapper
(`figcraft-cli mcp --attach PORT`) — it returns images inline. Use this raw
protocol only when MCP is unavailable or you need window-level control
without registering a client.

## Start

```sh
figcraft --control 7979 [file.figcraft|file.svg|image]
# from a source checkout:
cargo run -p figcraft -- --control 7979
```

The app listens on `127.0.0.1:<port>` only — no external network exposure.

## Message format

Newline-delimited JSON: one request object per line, one reply line per
request, in order.

```
request:  {"id": 1, "method": "engine.execute", "params": {...}}
reply:    {"id": 1, "ok": true, "result": ...}
          {"id": 1, "ok": false, "error": "message"}
```

Requests run on the UI thread at the start of the next frame. A UI request
unanswered within 60 s returns a timeout error. Non-JSON lines get
`{"id": null, "ok": false, "error": "bad JSON: …"}`.

## Limits

| Limit              | Value                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------- |
| Network            | Loopback socket only (`127.0.0.1`)                                                                   |
| Request line size  | 32 MiB; oversize lines get `message too large` and the connection closes                             |
| Active connections | 8; extras are closed immediately                                                                     |
| Inactivity timeout | 60 s on socket reads/writes (idle clients release their worker)                                      |
| Queues             | Socket queue and UI queue each hold 8 requests; a full queue replies `control request queue is full` |
| Dialogs            | Programmatic calls never open dialogs — dialog requests are dropped                                  |

## Methods

### Commands and documents

- `engine.execute {command, params?}` — run any command (the same ids as
  menus, shortcuts, CLI, and MCP). Creation commands return `{"id": N}`.

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

- `engine.commands {}` — list all commands with id, label, params, menu,
  shortcut, undoable.
- `document.inspect {depth?, allPages?}` — the active document as JSON
  (pages, selection, styles, colorProfile, undo history, …).
- `node.get {id, depth?}` — one layer with all its properties (bounds,
  fills, layout, overrides, devStatus, …).

### UI driving

- `ui.inspect {}` — full UI state: panels, tool, cursor, view, timing,
  prototype player, live-session state, tabs.
- `ui.pointer {kind, x,y | sx,sy, to?, steps?, shift?, alt?, cmd?, ctrl?, pressure?, pressureTo?}` —
  mouse gestures: `down`, `move`, `up`, `click`, `double`, `hover`, `drag`.
  Positions in page coordinates or screen pixels. Returns
  `{selection, tool}`.
- `ui.key {key, shift?, alt?, cmd?, ctrl?}` — keys as typed on the canvas
  (shortcuts, tools, nudges, text editing). Returns `{"command": id}` for
  shortcuts.
- `ui.type {text}` — type into the text being edited.
- `ui.input {events}` — raw window input reaching panels and fields:
  `{move:[x,y]}`, `{down:[x,y], button?}` / `{up:[x,y], button?}`,
  `{key, …}`, `{text}`, `{scroll:[dx,dy]}`, `{leave:true}`,
  `{hold:{alt, …}}`, `{gamepad: …}`. All events of one call arrive in one
  frame — send press and release as separate calls. Returns `{queued}`.
- `ui.menu.invoke {id}` — invoke a menu item (may open a dialog). Returns
  `{ok, lastError}`.
- `ui.set {...}` — switch panels/modes: `rightTab`, `leftTab`, `theme`,
  `home`, `palette`, `mainMenu`, `variables`, `colorPicker`,
  `contextMenu`, `preview`, comment and Dev-Mode options,
  `resetFrameStats`, and more. Returns the `ui.inspect` state.
- `ui.screenshot {path}` — whole-window PNG including UI; needs a visible
  window. Returns `{path, width, height}`, or an error after 60 s.
- `ui.render {path, scale?, ids?}` — document PNG without UI chrome; works
  without a window; without `ids`, exports the selection.

### Windows

- `window.new {path?, index?}` — open a window with a moved tab, a file, or
  a new file. Returns `{window}`.
- `window.list {}` — every window: `[{id, main, title, files, active,
  focused}]`.
- `window.focus {id}` — bring a window to the front; it becomes the target
  for requests sent without a `window` param.

Every method takes an optional `window` id (`0` = main window); without it,
requests go to the window that was last in front. Unknown ids are errors.

### App

- `app.quit {}` — close all windows without asking about unsaved changes.

## Shell session example

`/dev/tcp` redirects are bash-only — zsh has no `/dev/tcp`. Run these under
`bash`, or use any socket library.

```sh
port=7979
figcraft --control $port &
exec 3<>/dev/tcp/127.0.0.1/$port
echo '{"id":1,"method":"engine.execute","params":{"command":"frame.create","params":{"preset":"iPhone 16","x":0,"y":0}}}' >&3
read -r reply <&3; echo "$reply"
echo '{"id":2,"method":"ui.screenshot","params":{"path":"/tmp/figcraft.png"}}' >&3
read -r reply <&3; echo "$reply"
```

## Where implemented

`crates/ui-egui/src/control.rs` and `apps/figcraft/src/control_server.rs` in
the figcraft repository.
