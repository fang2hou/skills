# figcraft-cli reference

Verified against `docs/cli.md` in `storytold/figcraft` and tested against `figcraft-cli` (v0.6.0 through v0.12.1 on macOS). Install the prebuilt release binary from GitHub Releases (`figcraft-cli-<version>-macos-universal.zip`; see [setup.md](setup.md)) or build from source with `cargo build --release -p figcraft-cli` (`target/release/figcraft-cli`).

**Exit codes**: `0` on success; `1` on runtime or validation failure; `2` on invalid CLI arguments (prints usage to stderr). The CLI never panics on malformed input.

Contents:

- [Global behavior](#global-behavior)
- [Subcommands](#subcommands)
- [Related binary: figcraft-server](#related-binary-figcraft-server)
- [Export and import gotchas](#export-and-import-gotchas)

## Global behavior

- **Fonts**: Uses built-in fonts plus system fonts, matching the desktop app. The first text layout indexes system fonts (~60 ms warm with ~900 font files). Pass `--no-system-fonts` or set `FIGCRAFT_NO_SYSTEM_FONTS=1` for deterministic CI renders.
- **File inputs**: Every subcommand that reads a file accepts `.figcraft`, FigCraft `.json`, Figma REST API JSON (`GET /v1/files/:key` saved as `.json`), `.svg`, and best-effort `.fig` files. For REST API JSON, image fills load from `images/<imageRef>.png|jpg…` beside the JSON file (falling back to a gray placeholder). `info` prints skipped `.fig` features as `note:` lines on stderr.

## Subcommands

### `info <file> [--json]`

Prints pages, node counts, top-level frames (`id`, `type`, `name`, `size`), and style/variable/image counts. File repairs and import warnings are written to stderr as `note:` lines (or included in the `notes` array when `--json` is passed).

### `export <file> -o <out> [--format png|jpg|svg|webp|pdf|fig] [--scale N] [--page NAME] [--node ID|NAME] [--bleed LENGTH] [--crop-marks] [--bleed-marks] [--cmyk]`

- **Directory output (`-o dir/`)**: Writes one file per top-level frame (for example `Home.png`), or one file per top-level layer when the page has no frames.
- **File output (`-o file.ext`)**: Exports the `--node` layer (by numeric ID `12`, `0:12`, or layer name), or the entire page when `--node` is omitted.
- **Format and scale**: Resolved from `--format`, then the output filename extension, then `png`. `--scale` (default `1`, max `64`) applies to raster formats.
- **Experimental `.fig` output**: Checked by reopening the file in FigCraft. Unsupported items (styles, variables, comments, Dev-Mode data) print as `note:` lines.
- **Nesting limit**: SVG and PDF exports fail if visible descendants exceed 256 levels deep; export a specific `--node` or flatten deep nesting.
- **PDF and print flags**: Exports one page per top-level frame in reading order with vector shapes, subset selectable fonts, gradients, clickable links, and rasterized shadows/blurs. `--bleed` accepts points, `3mm`, or `0.125in` (up to `2in`); `--crop-marks` and `--bleed-marks` set PDF `MediaBox` to the sheet and `BleedBox`/`TrimBox` to the frame; `--cmyk` converts sRGB to `DeviceCMYK` using `K = 1 − max(R,G,B)` and `C = (1 − R − K)/(1 − K)`.

```sh
figcraft-cli export app.figcraft -o exports/ --scale 2
figcraft-cli export app.figcraft -o hero.svg --node "Hero"
figcraft-cli export app.figcraft -o screens.pdf --page "Screens"
figcraft-cli export app.figcraft -o poster.pdf --node "Poster" --bleed 3mm --crop-marks --cmyk
figcraft-cli export app.figcraft -o handoff.fig
```

### `convert <in> <out>`

Converts between formats based on file extensions:

- **Inputs**: `.figcraft`, `.json` (FigCraft or Figma REST API), `.fig` (best effort), `.svg` (imported as an editable frame of groups, shapes, text, gradients, masks, and effects), and raster images (`.png`, `.jpg`, `.webp`, `.gif`, `.bmp`).
- **Outputs**: `.figcraft`, pretty-printed `.json`, `.svg`, raster images (page at `1x`), `.pdf` (one page per frame), and experimental `.fig`.

### `render <file> -o <out.png> [--scale N] [--page NAME]`

Renders an entire page including its background (defaulting to the first page) to PNG, JPG, or WebP. Pages larger than `16384` px are scaled down to fit.

### `run <script.json|script.jsonl> [--in <file>] [--out <file>]`

Executes a headless command session atomically. Each step prints one JSON result line to stdout, such as `{"command":"frame.create","ok":true,"result":{"id":2},"step":0}`. If any step fails, it prints `"ok": false`, exits `1`, and writes no output file.

Accepted script formats:

- A JSON array of `{"command": "<id>", "params": {...}, "as"?: "<name>"}`
- A JSON object `{"commands": [...]}`
- JSON Lines (`.jsonl`), with blank lines and `//` comment lines ignored

You can bind created node IDs with `"as": "<name>"` and reference them in later steps with `{"$ref": "<name>"}` (identical to MCP `batch`). When counting raw IDs in a fresh document, page 1 is ID `1` and the first created layer is ID `2`.

```json
[
  {
    "command": "frame.create",
    "as": "home",
    "params": { "preset": "iPhone 16", "x": 0, "y": 0, "name": "Home" }
  },
  {
    "command": "node.create",
    "params": {
      "type": "text",
      "parent": { "$ref": "home" },
      "x": 24,
      "y": 64,
      "text": "Welcome",
      "props": { "fontSize": 32 }
    }
  },
  {
    "command": "layout.add",
    "params": { "ids": [{ "$ref": "home" }], "direction": "vertical" }
  }
]
```

### `commands [--json] [--filter TEXT]`

Lists all 400+ commands in the registry with their label, keyboard shortcut, undoable marker (`*`), and parameter schema. Pass `--json` for machine-readable output.

### `mcp [--attach PORT]`

Runs the upstream stdio MCP server (headless by default, or attached to `figcraft --control <port>`). **Do not register `figcraft-cli mcp` for general agent sessions**: unlike `figcraft-live-mcp` ([mcp.md](mcp.md)), the upstream server is not lazy and does not share one instance across worktrees. Use `figcraft-cli mcp` only when a headless script specifically needs network collaboration (`collab.*`) or plugin directory commands (`plugin.directory.*`) that one-shot `run` does not expose.

### `plugin publish <folder> --server ws://host:port/[?key=KEY]`

Validates and publishes a plugin folder (`figcraft-plugin.json`, its `main` module, and optional `assets/`) to a `figcraft-server` plugin directory, printing the package name, version, byte size, and SHA-256 hash. Pass the server key in the URL or via `FIGCRAFT_SERVER_KEY` (never echoed).

### `perf [--layers N[,N...]] [--instances N[,N...]]`

Runs synthetic performance benchmarks (default `1000,10000` layers) covering build/normalize, save/load, `1440×900` renders, hit testing, edits, undo/redo, drag preview, `document.inspect`, and select-all + move.

## Related binary: figcraft-server

`figcraft-server` (built via `cargo build --release -p figcraft-server`) hosts share-link files and live collaboration rooms (`key`, `files`, `links`, `reports`, `block-ip`, `check`). See upstream `docs/server.md`.

## Export and import gotchas

- **`run` is atomic**: A single failed step exits `1` and writes nothing to `--out`.
- **SVG/PDF depth limit**: Visible descendants deeper than 256 levels fail export; target a subtree with `--node` or simplify nesting.
- **SVG outlines all text**: SVG export converts glyphs to `<path>` elements with no `<text>` nodes. Verify text placement from a rendered PNG rather than searching SVG markup.
- **Directory export writes frames, not pages**: `-o exports/` emits one file per top-level frame (or top-level layer if no frames exist).
- **Format precedence**: `--format` overrides the output file extension, which overrides the default (`png`). Maximum raster `--scale` is `64`.
