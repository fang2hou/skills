# figcraft-cli reference

Verified against `docs/cli.md` in storytold/figcraft and the v0.6.0 macOS
release binary (2026-10). Install the prebuilt binary from GitHub Releases
(`figcraft-cli-<version>-macos-universal.zip`; see SKILL.md Setup) or build
with `cargo build --release -p figcraft-cli` →
`target/release/figcraft-cli`. "The CLI never panics on input." Exit codes:
bad arguments → usage on stderr and exit 2; failures → exit 1.

Contents: global behavior · subcommands (`info`, `export`, `convert`, `render`, `run`, `commands`, `mcp`, `plugin publish`, `perf`) · related binary

## Global behavior

- **Fonts**: built-in plus system fonts, identical to the desktop app. The
  first text layout indexes system fonts (~60 ms warm with ~900 files). Every
  subcommand accepts `--no-system-fonts`, or set `FIGCRAFT_NO_SYSTEM_FONTS=1`
  for reproducible CI renders.
- **File inputs**: every subcommand that reads a file also accepts public
  REST API file JSON (a `GET /v1/files/:key` response saved as `.json`).
  Image fills load from `images/<imageRef>.png|jpg…` beside the JSON, else a
  grey placeholder. `.fig` files are read best-effort; `info` reports skips
  as `note:` lines.

## Subcommands

### `info <file> [--json]`

Pages, node counts, top-level frames (id, type, name, size), and
style/variable/image counts. Repairs and import warnings go to stderr as
`note:` lines (the `notes` field with `--json`).

### `export <file> -o <out> [--format png|jpg|svg|webp|pdf|fig] [--scale N] [--page NAME] [--node ID|NAME] [--bleed LENGTH] [--crop-marks] [--bleed-marks] [--cmyk]`

- Directory output: one file per top-level frame (e.g. `Home.png`); with no
  frames, one per top-level layer.
- Image-extension output: the `--node` layer, or the whole page.
- `--node` takes a layer id (`12` or `0:12`) or name.
- Format: from `--format`, else the output extension, else png. `--scale`
  (default 1, max 64) applies to raster formats.
- `--format fig` / `.fig` output is experimental; checked only by reopening
  in FigCraft. Omissions (styles, variables, comments, Dev-Mode data) print
  as `note:` lines.
- SVG/PDF fail with an error (destination kept) when visible descendants
  exceed 256 levels deep; use `--node` or reduce nesting.
- PDF: one page per top-level frame in reading order; vector shapes, text,
  gradients; real selectable text with subset fonts; clickable links;
  shadows and blurs rasterized. Print options: `--bleed` (points, or `3mm` /
  `0.125in`, up to 2 in), `--crop-marks`, `--bleed-marks`; boxes set
  MediaBox to the sheet and BleedBox/TrimBox to the frame. `--cmyk` uses a
  naive sRGB→CMYK conversion (`K = 1 − max(R,G,B)`,
  `C = (1 − R − K)/(1 − K)`) emitting DeviceCMYK without output intent.

```sh
figcraft-cli export app.figcraft -o exports/ --scale 2
figcraft-cli export app.figcraft -o hero.svg --node "Hero"
figcraft-cli export app.figcraft -o screens.pdf --page "Screens"
figcraft-cli export app.figcraft -o poster.pdf --node "Poster" --bleed 3mm --crop-marks --cmyk
figcraft-cli export app.figcraft -o handoff.fig
```

### `convert <in> <out>`

Routes by extension.

- Inputs: `.figcraft`; `.json` (FigCraft or REST API); `.fig` (best effort);
  `.svg` (editable frame: groups, shapes, text, gradients, masks, effects);
  images `.png/.jpg/.webp/.gif/.bmp` (become an image layer).
- Outputs: `.figcraft`; `.json` (pretty); `.svg`; images (page at 1x);
  `.pdf` (one page per frame); `.fig` (experimental).

### `render <file> -o <out.png> [--scale N] [--page NAME]`

Whole page including background (default: the first page) as png/jpg/webp.
Large pages are scaled to fit 16384 px.

### `run <script.json|script.jsonl> [--in <file>] [--out <file>]`

Headless command session. Each step replies as one JSON line, e.g.
`{"command":"frame.create","ok":true,"result":{"id":2},"step":0}`. A failing
step produces `"ok": false`, exit 1, and saves nothing (`run` is atomic).

Accepted script formats: a JSON array of `{"command": id, "params": {...}}`,
an object `{"commands": [...]}`, or JSON lines (blank and `//` comment lines
skipped). Ids are assigned in order (the first page is 1, the first layer
is 2). Start from templates via `template.list` / `file.newFromTemplate`.

```json
[
  {
    "command": "frame.create",
    "params": { "preset": "iPhone 16", "x": 0, "y": 0, "name": "Home" }
  },
  {
    "command": "node.create",
    "params": {
      "type": "text",
      "parent": 2,
      "x": 24,
      "y": 64,
      "text": "Welcome",
      "props": { "fontSize": 32 }
    }
  },
  { "command": "layout.add", "params": { "ids": [2], "direction": "vertical" } }
]
```

### `commands [--json] [--filter TEXT]`

Lists every command with label, shortcut, undoable flag (`*`), and parameter
docs. `--json` for machine-readable output. This is the discovery entry
point for the 400+ command registry.

### `mcp [--attach PORT]`

Serves MCP on stdio; headless by default, or attached to an app started with
`figcraft --control PORT`. Headless sessions can host/join/publish live
sessions (`collab.*`) and use plugin directories (`plugin.directory.*`);
one-shot `run` cannot (no network link). See [mcp.md](mcp.md).

### `plugin publish <folder> --server ws://host:port/[?key=KEY]`

Publishes a plugin folder (`figcraft-plugin.json`, its `main` module,
optional `assets/`) to a server's plugin directory; prints name, version,
size, SHA-256. The server key comes from the address or the
`FIGCRAFT_SERVER_KEY` env var and is never printed. The bundle is checked
locally and again by the server.

### `perf [--layers N[,N...]] [--instances N[,N...]]`

Benchmarks synthetic documents (default `1000,10000` layers): build/normalise,
save/load, 1440×900 renders (100% and fit), hit testing, edits, undo/redo,
drag preview, normalize after edit, `document.inspect`, select-all + move.
Use a release build; `cargo xtask bench` runs 1k/10k/50k plus UI benchmarks.

## Related binary

`figcraft-server` (built separately via `cargo build --release -p
figcraft-server`) manages share-link files and live sessions: `key`, `files`,
`links`, `reports`, `block-ip`, `check`. See the upstream `docs/server.md`.
