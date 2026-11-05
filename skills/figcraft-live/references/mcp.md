# The figcraft-live MCP server

`scripts/figcraft-live-mcp` (installed to `~/.local/bin/figcraft-live-mcp`) is a self-contained Bash MCP server registered under the name **`figcraft-live`**. It avoids the bare name `figcraft`, which an official FigCraft server may claim later. The script runs a stdio JSON-RPC loop that proxies an 8-tool surface onto the app's loopback control channel ([control.md](control.md)). It was verified against the live app and `figcraft-cli` 0.12.1 on macOS (Bash 3.2) over raw stdio across every tool, cold-port launch, instance adoption, and the `stop` guard.

Contents:

- [Design](#design)
- [Registration](#registration)
- [Environment and CLI flags](#environment-and-cli-flags)
- [Protocol](#protocol)
- [Debugging](#debugging)

## Design

- **Lazy by construction**: `initialize` and `tools/list` reply from static JSON without opening a socket or launching a process. The server sends the first control-channel byte only when a tool call requires it, and only `ensure` can launch the app. Because the server is a single Bash read loop, you can mount it across every session and run multiple sessions concurrently.
- **Instance resolution** (used by `ensure` and read/write tools):
  1. `FIGCRAFT_PORT` if set (if that port is busy with a non-FigCraft process, resolution fails immediately).
  2. The remembered port for this repository (`~/.local/state/figcraft/<key>`).
  3. Port `7979`, then a deterministic port derived from `git rev-parse --git-common-dir` (identical across every worktree of a repository, ensuring one window per repo), then the next two sequential ports.
- **Adopt vs. start**: The first candidate port that answers `window.list` as FigCraft is **adopted** (`origin: adopted`). Adopted windows belong to the user and persist across sessions; `stop` refuses to close them without `force: true`. If no candidate port answers, `ensure` acquires a `mkdir` lock in the state directory and launches the app on the first closed candidate port (`open -n -g` on macOS so the window opens in the background). Concurrent agents waiting on the lock adopt the winner's instance. A server-launched instance is marked `origin: started` and can be closed with `stop` (`app.quit`, which discards unsaved changes).
- **Tool semantics**: Every tool returns the control channel's reply as a single JSON text block containing `ok` or `error`. `render` also returns the rendered PNG inline as MCP image content when the file is 8 MB or smaller. Each control call opens one TCP connection with a 65s read timeout (the app's UI thread times out after 60s).

## Registration

Registration is the agent's job: see the spec table in [SKILL.md](../SKILL.md#setup) for name, transport, command, scope, and timeout. Constraints that apply to every client:

- Use an absolute command path; GUI-launched clients do not inherit your shell `PATH`.
- Keep the effective timeout at or above 60 seconds, because `ensure` may wait up to `FIGCRAFT_START_WAIT` (default 30s) on a cold launch. Some clients take the timeout in seconds, others in milliseconds.
- Tool names may be namespaced by the server name, and a client may normalize the hyphen to an underscore. Use the exact names the client lists.
- Do not register the upstream `figcraft-cli mcp` subcommand in its place: it is not lazy and either launches a process or prints warnings on every session start.
- Verify after registering with the stdio test in [Debugging](#debugging).

## Environment and CLI flags

| Variable / Flag       | Effect                                                                      |
| --------------------- | --------------------------------------------------------------------------- |
| `FIGCRAFT_APP`        | App bundle path on macOS (`/Applications/FigCraft.app`) or binary on Linux  |
| `FIGCRAFT_PORT`       | Pins the loopback control port; fails if busy with a non-FigCraft process   |
| `FIGCRAFT_PROJECT`    | Pins the project root directory (default: the server's working directory)   |
| `FIGCRAFT_START_WAIT` | Maximum seconds to wait for the control port on cold launch (default: `30`) |
| `--project <dir>`     | CLI flag equivalent to `FIGCRAFT_PROJECT`                                   |
| `--version`           | Prints `figcraft-live-mcp <version>` and exits `0`                          |
| `--help` / `-h`       | Prints usage, environment variables, and exit codes, then exits `0`         |

**Exit codes**: `0` on clean EOF, `--help`, or `--version`; `1` when `jq` is missing; `2` on invalid CLI arguments. Tool-level errors inside the JSON-RPC loop return MCP `isError: true` result blocks instead of terminating the server.

**Runtime dependencies**: `bash` (3.2 or newer) and `jq`. Inline PNG encoding uses `openssl` or `base64`. Launching the app uses `open` on macOS, or `FIGCRAFT_APP` / `FigCraft.AppImage` on Linux.

## Protocol

The server speaks newline-delimited JSON-RPC 2.0 over stdio for MCP protocol versions `2025-06-18`, `2025-03-26`, and `2024-11-05`:

- `initialize`: Returns `capabilities.tools` and embeds the demand-gate summary in `instructions` so every client session receives the contract automatically.
- `tools/list`, `tools/call`, `ping`: Handled directly in the stdio loop.
- `notifications/*`: Ignored silently.
- Error handling: Non-JSON lines return `-32700` (`parse error`), and unknown methods return `-32601` (`method not found`). Tool execution runs in a subshell; any nonzero exit or `die` message is caught and returned as a normal MCP tool result with `isError: true` so the server process never crashes.

## Debugging

Test the server directly over stdio (one JSON-RPC line per request):

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"status","arguments":{}}}' \
  | ~/.local/bin/figcraft-live-mcp | jq .
```

Use `status` to inspect port resolution, remove stale state files under `~/.local/state/figcraft/` if ports changed, and inspect the app directly over the loopback socket ([control.md](control.md)) when needed. The server writes only startup and launch diagnostics to stderr.
