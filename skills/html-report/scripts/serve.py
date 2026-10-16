#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Serve an html-report directory on 127.0.0.1 and save review answers to DIR/state.json.

Commands:
  start DIR [--port N] [--idle-hours H]  Start in the background. Prints {"url", "dir", "pid", "state"} as JSON.
                                         Reuses a server that is already running for DIR; a restart
                                         takes the previous port when it is free, so open tabs reconnect.
  wait DIR [--timeout SECONDS]           Block until state.json has "submitted": true, then print the state JSON.
  status DIR                             Print server info and answer counts as JSON.
  stop DIR                               Stop the server for DIR. Succeeds when none is running.
  run DIR [--port N] [--idle-hours H]    Run in the foreground (start uses this).

HTTP API (127.0.0.1 only):
  GET  /api/state    Current state.json, or {} when no answers exist yet.
  PUT  /api/state    Replace state.json. Requires Content-Type: application/json, same-origin, at most 1 MB.
  GET  /api/version  Changes when any served file except state.json changes; pages poll it to reload.

Exit codes: 0 success; 2 usage error; 3 DIR or state missing; 4 server failed to start; 5 wait timed out.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from datetime import UTC, datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STATE_FILE = "state.json"
INFO_FILE = ".server.json"
LOG_FILE = ".server.log"
# Answers for one review page are a few KB; 1 MB rejects accidental uploads.
MAX_BODY = 1_000_000
# Long enough to read a long report; short enough not to leave servers running for days.
DEFAULT_IDLE_HOURS = 4.0
# Seconds to wait for the background server to bind its port.
START_TIMEOUT = 10.0


def fail(code: int, message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def resolve_dir(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        fail(
            3,
            f"Directory not found: {path}. Create it and put index.html inside, then retry.",
        )
    return path


def read_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def write_json_atomic(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def content_version(root: Path) -> int:
    newest = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name == STATE_FILE or name.startswith("."):
                continue
            try:
                newest = max(newest, (Path(dirpath) / name).stat().st_mtime_ns)
            except FileNotFoundError:
                continue
    return newest


def make_handler(root: Path, activity: dict):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt: str, *args) -> None:
            if not self.path.startswith("/api/version"):
                sys.stderr.write(f"{now_iso()} {fmt % args}\n")

        def send_json(self, status: int, data: dict) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def list_directory(self, path):
            self.send_error(404)

        def host_ok(self) -> bool:
            host = self.headers.get("Host", "").rsplit(":", 1)[0]
            if host in ("127.0.0.1", "localhost"):
                return True
            self.send_error(421, "Unexpected Host header")
            return False

        def do_GET(self) -> None:
            if not self.host_ok():
                return
            route = self.path.split("?", 1)[0]
            if route == "/api/version":
                self.send_json(200, {"version": content_version(root)})
                return
            activity["last"] = time.monotonic()
            if route == "/api/state":
                self.send_json(200, read_json(root / STATE_FILE) or {})
                return
            if any(part.startswith(".") for part in route.split("/")):
                self.send_error(404)
                return
            super().do_GET()

        def do_HEAD(self) -> None:
            self.send_error(405)

        def do_PUT(self) -> None:
            if not self.host_ok():
                return
            activity["last"] = time.monotonic()
            if self.path.split("?", 1)[0] != "/api/state":
                self.send_error(404)
                return
            origin = self.headers.get("Origin")
            if origin and origin != f"http://{self.headers.get('Host', '')}":
                self.send_json(403, {"error": "cross-origin write rejected"})
                return
            if not self.headers.get("Content-Type", "").startswith("application/json"):
                self.send_json(
                    415, {"error": "expected Content-Type: application/json"}
                )
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                self.send_json(413, {"error": f"body must be 1..{MAX_BODY} bytes"})
                return
            try:
                data = json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                self.send_json(400, {"error": "body is not valid JSON"})
                return
            if not isinstance(data, dict):
                self.send_json(400, {"error": "body must be a JSON object"})
                return
            data["updated"] = now_iso()
            write_json_atomic(root / STATE_FILE, data)
            self.send_json(200, data)

    return Handler


def server_alive(info: dict | None) -> bool:
    if not info:
        return False
    try:
        os.kill(int(info["pid"]), 0)
        with urllib.request.urlopen(f"{info['url']}api/version", timeout=2) as response:
            return response.status == 200
    except (OSError, KeyError, ValueError):
        return False


def cmd_run(root: Path, port: int, idle_hours: float) -> None:
    activity = {"last": time.monotonic()}
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(root, activity))
    except OSError as error:
        fail(
            4,
            f"Cannot bind 127.0.0.1:{port}: {error}. Retry with --port 0 to pick a free port.",
        )
    bound_port = server.server_address[1]
    info = {
        "url": f"http://127.0.0.1:{bound_port}/",
        "port": bound_port,
        "dir": str(root),
        "pid": os.getpid(),
        "state": str(root / STATE_FILE),
        "started": now_iso(),
    }
    write_json_atomic(root / INFO_FILE, info)

    def shutdown(*_args) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    def idle_watch() -> None:
        while True:
            time.sleep(60)
            if time.monotonic() - activity["last"] > idle_hours * 3600:
                sys.stderr.write(f"{now_iso()} idle for {idle_hours}h, stopping\n")
                shutdown()
                return

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    threading.Thread(target=idle_watch, daemon=True).start()
    sys.stderr.write(f"{now_iso()} serving {root} at {info['url']}\n")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def spawn_server(root: Path, port: int, idle_hours: float) -> dict | None:
    log = open(root / LOG_FILE, "a", encoding="utf-8")  # noqa: SIM115 - handed to the child process.
    command = [sys.executable, str(Path(__file__).resolve()), "run", str(root)]
    command += ["--port", str(port), "--idle-hours", str(idle_hours)]
    child = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    log.close()
    deadline = time.monotonic() + START_TIMEOUT
    while time.monotonic() < deadline:
        info = read_json(root / INFO_FILE)
        if info and info.get("pid") == child.pid and server_alive(info):
            return info
        if child.poll() is not None:
            return None
        time.sleep(0.1)
    child.terminate()
    return None


def cmd_start(root: Path, port: int, idle_hours: float) -> None:
    info = read_json(root / INFO_FILE)
    if server_alive(info):
        print(json.dumps(info, ensure_ascii=False))
        return
    # Reuse the previous port so a tab that is still open reconnects after a restart.
    last_port = int((info or {}).get("port") or 0)
    candidates = [port] if port else ([last_port, 0] if last_port else [0])
    for candidate in candidates:
        started = spawn_server(root, candidate, idle_hours)
        if started:
            print(json.dumps(started, ensure_ascii=False))
            return
    fail(4, f"Server did not start. See {root / LOG_FILE} for the error.")


def answer_counts(state: dict | None) -> dict:
    state = state or {}
    return {
        "answered": len(state.get("answers") or {}),
        "unanswered": len(state.get("unanswered") or []),
        "submitted": bool(state.get("submitted")),
    }


def cmd_wait(root: Path, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while True:
        state = read_json(root / STATE_FILE)
        if state and state.get("submitted"):
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return
        if time.monotonic() >= deadline:
            print(
                json.dumps(
                    {"status": "timeout", **answer_counts(state)}, ensure_ascii=False
                )
            )
            fail(
                5,
                f"No submission within {timeout:.0f}s. Read {root / STATE_FILE} for partial answers.",
            )
        time.sleep(1)


def cmd_status(root: Path) -> None:
    info = read_json(root / INFO_FILE)
    running = server_alive(info)
    result = {
        "running": running,
        **(info if running else {}),
        **answer_counts(read_json(root / STATE_FILE)),
    }
    print(json.dumps(result, ensure_ascii=False))


def pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def cmd_stop(root: Path) -> None:
    info = read_json(root / INFO_FILE)
    if not server_alive(info):
        print(json.dumps({"stopped": False, "reason": "not running"}))
        return
    pid = int(info["pid"])
    os.kill(pid, signal.SIGTERM)
    for _ in range(50):
        if not pid_running(pid):
            break
        time.sleep(0.1)
    print(json.dumps({"stopped": True, "pid": pid}))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "run"):
        p = sub.add_parser(name)
        p.add_argument("dir")
        p.add_argument(
            "--port", type=int, default=0, help="0 picks a free port (default)"
        )
        p.add_argument("--idle-hours", type=float, default=DEFAULT_IDLE_HOURS)
    p = sub.add_parser("wait")
    p.add_argument("dir")
    p.add_argument("--timeout", type=float, default=1800, help="seconds (default 1800)")
    for name in ("status", "stop"):
        sub.add_parser(name).add_argument("dir")
    args = parser.parse_args()
    root = resolve_dir(args.dir)
    if args.command == "run":
        cmd_run(root, args.port, args.idle_hours)
    elif args.command == "start":
        cmd_start(root, args.port, args.idle_hours)
    elif args.command == "wait":
        cmd_wait(root, args.timeout)
    elif args.command == "status":
        cmd_status(root)
    else:
        cmd_stop(root)


if __name__ == "__main__":
    main()
