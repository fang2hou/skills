# FigCraft setup

Install and verify `figcraft-cli` (the headless batch runner and command registry browser) and review macOS app notes. The MCP server (`scripts/figcraft-live-mcp`, installed with `install -m 755` to `~/.local/bin` under the server name `figcraft-live`) requires only `bash` and `jq`; see [mcp.md](mcp.md) for client registration.

Contents:

- [1. Probe for an existing CLI](#1-probe-for-an-existing-cli)
- [2. Install the prebuilt release (macOS)](#2-install-the-prebuilt-release-macos)
- [3. Run the status check](#3-run-the-status-check)
- [4. Build from source (Rust 1.95+)](#4-build-from-source-rust-195)
- [5. macOS app notes](#5-macos-app-notes)

## 1. Probe for an existing CLI

```bash
command -v figcraft-cli || command -v figcraft || command -v figcraft.cli
```

- `figcraft-cli`: Native CLI binary; call it directly.
- Linux AppImage: Run `FigCraft.AppImage cli <subcommand>` instead of `figcraft-cli`. On Linux Snap installs, the headless binary is `figcraft.cli`.
- The Homebrew `figcraft` cask and the macOS `.app` bundle do not include `figcraft-cli`; neither satisfies this probe.

## 2. Install the prebuilt release (macOS)

Download the latest universal release archive, verify its SHA-256 checksum, and install the binary into `~/.local/bin`:

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

- **Preserve the archive filename**: `shasum --check` matches the exact filename recorded in `SHA256SUMS.txt`. Renaming the zip causes verification to fail with `no file was verified`.
- **Stop on checksum failure**: Abort the installation if `shasum` does not print `OK`.
- **Linux and Windows**: On Linux, download the release AppImage and invoke `FigCraft.AppImage cli <subcommand>`. Windows does not ship a standalone CLI archive; build from source instead.
- **PATH resolution**: If the current shell caches command lookups, invoke `~/.local/bin/figcraft-cli` by absolute path for the rest of the session. If a new shell cannot find it, add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile.

## 3. Run the status check

Run both commands before starting headless file work, even when Step 1 found an existing binary:

```bash
figcraft-cli --version
figcraft-cli commands --filter frame | head
```

If either command fails, the installed binary is broken or outdated; reinstall it using Step 2 (`~/.local/bin` takes precedence on `PATH`).

## 4. Build from source (Rust 1.95+)

Use a source build when testing unreleased changes or running on platforms without a prebuilt CLI binary:

```bash
git clone https://github.com/storytold/figcraft
cd figcraft
git clone https://github.com/storytold/craft-fonts ../craft-fonts # optional UI and text fonts
cargo build --release -p figcraft-cli # outputs target/release/figcraft-cli
```

`figcraft-cli` is not published to crates.io (`cargo install figcraft-cli` will fail).

## 5. macOS app notes

- **Double-clicking `.figcraft` files in Finder does not open them (v0.6.0)**: The app bundle declares the document type in `Info.plist` but does not handle LaunchServices document Apple Events. Double-clicking opens an empty app window, and a stale LaunchServices registration can block launch with a `cannot open` dialog (reset it with `lsregister -f /Applications/FigCraft.app`). Open files with the MCP `ensure {path}` tool, by dragging the file into the window, or via `open -a FigCraft --args <file>`.
- **Homebrew desktop install**: Run `brew install --cask figcraft` to install `/Applications/FigCraft.app`.
