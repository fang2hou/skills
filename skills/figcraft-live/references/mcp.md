# The figcraft MCP server

`scripts/figcraft-mcp` (installed to `~/.local/bin/figcraft-mcp`) is a
self-contained bash MCP server: a stdio JSON-RPC loop that proxies a small
tool surface onto the app's loopback control channel
([control.md](control.md)). Exercised against the live app with
figcraft-cli 0.12.1 on macOS (bash 3.2) and verified over raw stdio: every
tool, the launch path on a cold port, the adopt path, and the stop guard.

Contents: design · registration · env · protocol · debugging

## Design

**Lazy by construction.** `initialize` and `tools/list` are answered from
static data — mounting the server touches nothing but stdin/stdout. The
first control-channel byte is sent only when a tool call needs it, and only
`ensure` may launch the app. The server process itself is one bash loop:
safe to mount in every session, several at once.

**Instance resolution** (inside `ensure` and the read tools):

1. `FIGCRAFT_PORT` if set (a busy non-FigCraft port is a hard error).
2. The remembered port for this repository (`~/.local/state/figcraft/<key>`).
3. Port 7979, then a port derived from
   `git rev-parse --git-common-dir` (identical in every worktree of the
   repository — one instance per repo), then the next two ports.

The first port answering `window.list` as FigCraft is **adopted** (the
user's window, kept alive across sessions; `stop` refuses it without
`force`). When none answers, `ensure` launches the app on the first closed
candidate (`open -n -g` on macOS, so the window appears in the background)
under a mkdir lock in the state dir — concurrent agents race-safely end up
adopting the winner's instance. A launched instance is `origin: started`
and may be `stop`ped (`app.quit`, unsaved changes discarded).

**Tool semantics.** Tools return the control channel's reply as one JSON
text block (`ok`/`error` inside; check `ok`, the call itself succeeds).
`render` additionally returns the PNG inline as MCP image content.
Time-bounded calls: one request per connection, 65 s read timeout (the
channel times UI requests out at 60 s).

## Registration

Global (user level) is the intended scope: the server is lazy, so mounting
it everywhere costs one bash process per session and never a window. Set
the client's MCP timeout to at least 60000 ms — `ensure` may spend up to
`FIGCRAFT_START_WAIT` (default 30 s) launching the app.

omp — `~/.omp/agent/mcp.json` (merge into the existing `mcpServers`; a
named profile reads `~/.omp/profiles/<name>/agent/mcp.json` instead; then
`/mcp reload`):

```json
{
  "mcpServers": {
    "figcraft": {
      "type": "stdio",
      "command": "/Users/<you>/.local/bin/figcraft-mcp",
      "timeout": 120000
    }
  }
}
```

Tools mount as `xd://mcp__figcraft_<tool>` (for example
`xd://mcp__figcraft_ensure`); project `.omp/mcp.json` works identically
when you want it per-repo only.

Claude Code (user scope):

```sh
claude mcp add --scope user figcraft ~/.local/bin/figcraft-mcp
```

Claude Desktop — `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "figcraft": { "command": "/Users/<you>/.local/bin/figcraft-mcp" }
  }
}
```

Always the absolute path: GUI-launched clients do not inherit the shell
`PATH`. Do not register the upstream `figcraft-cli mcp` instead — it is not
lazy: a mounted stdio server of theirs launches or warns with every session,
which is what this server exists to avoid.

## Environment

| Variable              | Effect                                                       |
| --------------------- | ------------------------------------------------------------ |
| `FIGCRAFT_APP`        | App bundle dir (macOS) or binary/AppImage path (Linux).      |
| `FIGCRAFT_PORT`       | Pin the control port; busy-and-not-FigCraft is a hard error. |
| `FIGCRAFT_PROJECT`    | Pin the project root (default: the server's working dir).    |
| `FIGCRAFT_START_WAIT` | Launch wait seconds (default 30).                            |

Requires `bash` (3.2 suffices) and `jq`; the image inline path uses
`openssl` or `base64`. macOS `open` launches the app; elsewhere set
`FIGCRAFT_APP` to the binary/AppImage.

## Protocol

NDJSON JSON-RPC 2.0 over stdio, MCP `2025-06-18` (client versions
`2025-03-26` and `2024-11-05` echoed). Handled: `initialize` (capabilities:
tools; `instructions` carries the demand-gate summary so every session
knows the contract), `tools/list`, `tools/call`, `ping`; notifications are
ignored, malformed lines get `-32700`, unknown methods `-32601`. A tool
failure (including "not running; call ensure") is a normal result with
`isError: true`, never a crashed server: the dispatcher runs each call in
a subshell and converts any error into a message block.

## Debugging

Drive the server by hand — one JSON-RPC line in, one line out:

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"status","arguments":{}}}' \
  | ~/.local/bin/figcraft-mcp | jq .
```

Check the resolution state with `status`, delete stale state under
`~/.local/state/figcraft/` when ports changed, and inspect the app side
with the raw channel ([control.md](control.md)). The server logs to stderr
(only startup and launch messages).
