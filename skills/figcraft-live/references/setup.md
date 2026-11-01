# FigCraft setup

Install and verify `figcraft-cli` (the headless batch runner and command
registry browser) and note app quirks. The MCP server
(`scripts/figcraft-mcp`, `install -m 755` to `~/.local/bin`) needs only
`bash` and `jq`; registration lives in
[mcp.md](mcp.md). SKILL.md links here when the CLI probe fails or the
status check fails.

Contents: probe · install (macOS) · status check · build from source · app notes

## 1. Probe

```bash
command -v figcraft-cli || command -v figcraft || command -v figcraft.cli
```

- `figcraft-cli`: native CLI binary; use directly.
- Linux AppImage: run `FigCraft.AppImage cli <subcommand>` in place of
  `figcraft-cli`; on Linux snap the headless CLI is `figcraft.cli`.
- The Homebrew `figcraft` cask and the macOS `.app` bundle contain no CLI
  binary; neither satisfies this probe.

## 2. Install the prebuilt release (macOS)

Download the latest universal zip, verify its SHA-256, and unpack into
`~/.local/bin`:

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

- Keep the zip's original asset filename: `shasum --check` matches names in
  `SHA256SUMS.txt`, so a renamed file verifies nothing and fails with "no
  file was verified".
- Abort the install when the checksum line does not print `OK`.
- Linux: download the release AppImage instead and call it as
  `FigCraft.AppImage cli <subcommand>`. Windows has no standalone CLI zip;
  build from source.
- The current shell may not resolve `figcraft-cli` right after the install;
  use the absolute path `~/.local/bin/figcraft-cli` for the rest of the
  session. If a fresh shell still cannot find it, add
  `export PATH="$HOME/.local/bin:$PATH"` to the shell rc.

## 3. Status check

Run it every time, including when the probe found a binary. Both commands
must succeed before anything else:

```bash
figcraft-cli --version
figcraft-cli commands --filter frame | head
```

An existing install that fails here is stale or broken: report it and
reinstall via step 2 (`~/.local/bin` shadows it on `PATH`).

## 4. Build from source (Rust 1.95+; for dev versions)

```bash
git clone https://github.com/storytold/figcraft
cd figcraft
git clone https://github.com/storytold/craft-fonts ../craft-fonts # optional UI/text fonts
cargo build --release -p figcraft-cli   # -> target/release/figcraft-cli
```

Not on crates.io (`cargo install figcraft-cli` does not work).

## App notes

- **macOS double-click does not load `.figcraft` files (v0.6.0).** The app
  declares the document type but does not handle LaunchServices document
  Apple Events: double-click launches the app without the file, and a stale
  registration blocks the launch with "cannot open" (repair with
  `lsregister -f /Applications/FigCraft.app`). Open a file by dropping it
  into the app window, with MCP `open_file`, or with
  `open -a FigCraft --args <file>` (argv delivery works).
- Brew installs the app: `brew install --cask figcraft`.
