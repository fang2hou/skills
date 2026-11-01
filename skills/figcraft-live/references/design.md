# Building designs in FigCraft: patterns and QA

Construction doctrine distilled from Figma's official agent guidance
(auto layout, tokens, semantic naming, section-by-section builds, screenshot
verification) and adapted to figcraft's command registry. Every pattern and
every pitfall below was verified against figcraft v0.6.0 (2026-10); the
`as`/`$ref` skeleton, default fill, and icon sizing were re-verified on 0.12.1.

Contents: the one rule that prevents most broken layouts · construction patterns · tokens before values · verification loop · where the guidance comes from

## The one rule that prevents most broken layouts

**An auto-layout frame never sizes itself.** Without `sizingH`/`sizingV`
(or explicit width/height) a frame solves to a fixed 100×100, and frames
clip their children by default (`clip: true`). Symptoms seen in practice:

- A 156 px button rendered 96 px wide because its parent row frame was 100×100
  and clipped it at the right edge.
- A sibling button vanished entirely because it started past the parent's clip
  edge.
- A nav divider landed at y=99 instead of ~75 because the nav frame defaulted to
  100 px tall; the layout only _looked_ right by accident.

Declare sizing on **every** layout frame:

| Declaration            | Use for                                                          |
| ---------------------- | ---------------------------------------------------------------- |
| `sizingH/-sizingV` hug | Content-sized: buttons, nav bars, badges, chips                  |
| `sizingH` fill         | Stretch across parent: nav/footer rows in a page column          |
| `sizingV` fill         | Take leftover space: main content area between header and footer |
| explicit width/height  | The page frame itself (e.g. 1440×900, or a frame preset)         |

## Construction patterns

### Page skeleton

Page frame = vertical layout, fixed viewport size, `padding: 0`. Children:
header (`sizingH: fill`, `sizingV: hug`), content (`fill`/`fill`), footer
(`fill`/`hug`). Equal-width rows come from `fill`, not from hand-set widths.

Name each step with `as` and point later steps at it with `{"$ref": name}`
instead of counting creation-order ids; the same lines work as MCP `batch`
tool commands and as `figcraft-cli run` steps (verified on
0.12.1). This page
with a nav row and content area solves to nav 390×56 and content 390×788:

```jsonl
{"command": "frame.create", "as": "page", "params": {"x": 0, "y": 0, "width": 390, "height": 844, "name": "Home", "props": {"fill": "#FFFFFF", "layout": "vertical", "padding": 0}}}
{"command": "frame.create", "as": "nav", "params": {"parent": {"$ref": "page"}, "name": "nav", "props": {"layout": "horizontal", "sizingH": "fill", "sizingV": "hug", "padding": [16, 20, 16, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}}}
{"command": "node.create", "params": {"type": "text", "parent": {"$ref": "nav"}, "text": "App", "name": "nav-title", "props": {"fontSize": 17, "fill": "#111827"}}}
{"command": "frame.create", "as": "content", "params": {"parent": {"$ref": "page"}, "name": "content", "props": {"layout": "vertical", "sizingH": "fill", "sizingV": "fill", "padding": 20, "gap": 16}}}
```

Frames get a white fill by default. Give transparent wrappers (rows,
icon boxes, tab items) `"fill": "none"` or they paint white blocks over a
tinted page.

### Icons without images

An icon is a `vector` layer built from SVG path data, stroked, with no
fill:

```json
{
  "command": "node.create",
  "params": {
    "type": "vector",
    "parent": { "$ref": "nav" },
    "path": "M15 18l-6-6 6-6",
    "height": 24,
    "name": "icon-back",
    "props": {
      "fill": "none",
      "stroke": "#111827",
      "strokeWeight": 2,
      "strokeCap": "round",
      "strokeJoin": "round"
    }
  }
}
```

Give one axis only (`height` above): the path keeps its aspect ratio.
Setting both `width` and `height` stretches it to the box (a 6×12
chevron became 24×24). For several icons of different shapes, wrap each in
a fixed 24×24 frame with centered layout so labels and rows align.
Brand logos and photos are images, not vectors: see
[images.md](images.md).

### Button (the canonical hug pattern)

```json
{ "command": "frame.create", "as": "btn", "params": { "parent": { "$ref": "row" }, "name": "btn-primary", "props": { "layout": "horizontal", "sizingH": "hug", "sizingV": "hug", "padding": [15, 32, 15, 32], "cornerRadius": 10, "fill": "#111827", "mainAlign": "center", "crossAlign": "center" } } },
{ "command": "node.create", "params": { "type": "text", "parent": { "$ref": "btn" }, "text": "Get in touch", "props": { "fontSize": 16, "fill": "#FFFFFF" } } }
```

The layout engine centers the label; never place text over a
rectangle with absolute coordinates, and never fix a label's width.
A text node's box centers correctly even when its glyph ink does not fill
the box symmetrically (side bearings).

### Divider without a line node

Give the frame a one-sided stroke instead of adding line layers:

```json
"stroke": "#E5E7EB", "strokeWeight": 1, "strokeSides": [false, false, true, false]
```

`strokeSides` is `[top, right, bottom, left]` booleans.

### Circle avatar / icon badge

Frame with `cornerRadius` = half the size, layout-centered initials:

```json
{
  "width": 120,
  "height": 120,
  "props": {
    "cornerRadius": 60,
    "fill": "#4F46E5",
    "layout": "horizontal",
    "mainAlign": "center",
    "crossAlign": "center"
  }
}
```

### Wrapping body text

Fixed width + `textAutoResize: "height"` (fixed width, hug height). Leave
`textAutoResize` at its default (hug both) for headings and labels; use
`none` only as a last resort.

### Text alignment traps

`textAlignVertical` accepts `top|middle|bottom` and does **not** geometrically
center fixed-height text; center with a layout container instead.

## Tokens before values

- One accent color; neutrals from a gray ramp (e.g. Tailwind-ish
  `#111827`/`#4B5563`/`#6B7280`/`#E5E7EB`).
- Spacing on a 4/8 scale (8, 16, 24, 32, 64, 80); one `gap` and one `padding`
  rhythm per container level.
- Name every layer semantically (`nav`, `hero-title`, `btn-primary-label`), since
  `run` scripts and later edits both depend on names.
- Check contrast **before** rendering: body text needs ≥ 4.5:1 (WCAG AA).
  `#6B7280` on white ≈ 4.8:1 passes; `#9CA3AF` ≈ 2.8:1 fails and was caught
  only because the check ran.

## Verification loop (model first, pixels second)

1. **Model assertions**: MCP `inspect {id, depth}` (`node.get`) or
   `inspect {depth}` (`document.inspect`)
   report solved `width`/`height` and `absoluteBounds`; on the CLI,
   `figcraft-cli convert out.figcraft out.json` dumps every node's solved
   `width`/`height`/`transform`. Assert each
   frame's size matches intent; any unexpected `100×100` is a missing
   hug/fill declaration. This catches clipped or vanished elements that
   pixels alone make ambiguous.
2. **Pixel checks**: render, then verify:
   - no ink on canvas edge rows/columns (nothing clipped at the frame);
   - row-band structure matches the intended element sequence;
   - color blobs appear where fills should be (sample exact hexes);
   - label centroids sit inside their containers (expect a few px of glyph
     side-bearing asymmetry; the model, not ink, is the centering truth);
   - side margins clean (e.g. nothing left of x=80 on an 80 px-margin page).
   - Judge element gaps from the model: ink gaps include text leading, so a
     24 px `gap` renders as ~33–60 px of ink separation depending on
     line-height.
3. Fix and re-verify: MCP `exec {command: "edit.undo"}` the bad batch or
   patch the layer with `node.set`, then look again; on the CLI, rerun
   the whole `run` script (it is atomic).

Extend the page skeleton section by section and verify each section with
the loop above. Pixel checks include placed images: see
[images.md](images.md#checks-after-placing).

## Where the guidance comes from

Figma's agent guidance (auto layout for responsive intent, design tokens,
semantic naming, breaking screens into sections, screenshot validation,
WCAG) mapped onto figcraft's registry; see Figma's agent-tooling documentation
and `docs/` in the figcraft repository for the upstream principles.
