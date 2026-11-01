# Building designs in FigCraft: patterns and QA

Construction patterns and verification checks adapted from Figma's official agent guidance (auto layout, tokens, semantic naming, section-by-section builds, and visual QA) for FigCraft's command registry. Verified against FigCraft v0.6.0 through v0.12.1.

Contents:

- [The one rule that prevents broken layouts](#the-one-rule-that-prevents-broken-layouts)
- [Construction patterns](#construction-patterns)
- [Tokens before values](#tokens-before-values)
- [Verification loop (model first, pixels second)](#verification-loop-model-first-pixels-second)
- [Provenance](#provenance)

## The one rule that prevents broken layouts

**An auto-layout frame never sizes itself automatically.** Without `sizingH` and `sizingV` (or explicit `width` and `height`), a frame defaults to a fixed `100×100` box with `clip: true`. Common failure symptoms:

- A `156` px button renders `96` px wide because its parent row frame stayed at `100×100` and clipped the right edge.
- A second button in a row disappears completely because its `x` position starts past the parent's `100` px clip boundary.
- A navigation divider lands at `y = 99` instead of `y = 75` because the nav frame defaulted to `100` px tall.

Declare sizing on **every** auto-layout frame:

| Declaration                     | When to use                                                                  |
| ------------------------------- | ---------------------------------------------------------------------------- |
| `sizingH` / `sizingV` = `"hug"` | Content-sized containers: buttons, nav bars, badges, chips                   |
| `sizingH` = `"fill"`            | Full-width rows inside a vertical parent: headers, footers, cards, list rows |
| `sizingV` = `"fill"`            | Flexible body containers that take remaining vertical space                  |
| Explicit `width` / `height`     | Root page frames (for example `390×844` mobile or `1440×900` desktop)        |

## Construction patterns

### Page skeleton

Give the root page frame a vertical layout, fixed viewport dimensions, and `padding: 0`. Typical children are a header (`sizingH: "fill"`, `sizingV: "hug"`), a main content area (`fill` / `fill`), and a footer (`fill` / `hug`). Let `sizingH: "fill"` create equal-width rows instead of calculating manual pixel widths.

Bind each created frame with `as` and reference it in child steps with `{"$ref": "<name>"}` instead of counting numeric IDs. The same step objects work in both MCP `batch` and `figcraft-cli run`. In the example below, the `390×844` page solves to a `390×56` `nav` bar and a `390×788` `content` area:

```jsonl
{"command": "frame.create", "as": "page", "params": {"x": 0, "y": 0, "width": 390, "height": 844, "name": "Home", "props": {"fill": "#FFFFFF", "layout": "vertical", "padding": 0}}}
{"command": "frame.create", "as": "nav", "params": {"parent": {"$ref": "page"}, "name": "nav", "props": {"layout": "horizontal", "sizingH": "fill", "sizingV": "hug", "padding": [16, 20, 16, 20], "mainAlign": "spaceBetween", "crossAlign": "center"}}}
{"command": "node.create", "params": {"type": "text", "parent": {"$ref": "nav"}, "text": "App", "name": "nav-title", "props": {"fontSize": 17, "fill": "#111827"}}}
{"command": "frame.create", "as": "content", "params": {"parent": {"$ref": "page"}, "name": "content", "props": {"layout": "vertical", "sizingH": "fill", "sizingV": "fill", "padding": 20, "gap": 16}}}
```

Frames default to an opaque white fill (`#FFFFFF`). Set `"fill": "none"` on structural wrapper frames (rows, icon holders, tab items) so they do not paint white rectangles over tinted backgrounds.

### Vector icons

Build icons as `vector` layers from SVG path data with a stroke and `"fill": "none"`:

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

Pass only one dimension (`height` above) so the path scales proportionally. Passing both `width` and `height` stretches non-square paths to fill the bounding box (turning a `6×12` chevron into `24×24`). To align multiple icons of different proportions, place each vector inside a fixed `24×24` wrapper frame with centered layout and `"fill": "none"`. For brand logos and photos, use raster or imported SVG assets ([images.md](images.md)).

### Button (canonical hug pattern)

```json
[
  {
    "command": "frame.create",
    "as": "btn",
    "params": {
      "parent": { "$ref": "row" },
      "name": "btn-primary",
      "props": {
        "layout": "horizontal",
        "sizingH": "hug",
        "sizingV": "hug",
        "padding": [15, 32, 15, 32],
        "cornerRadius": 10,
        "fill": "#111827",
        "mainAlign": "center",
        "crossAlign": "center"
      }
    }
  },
  {
    "command": "node.create",
    "params": {
      "type": "text",
      "parent": { "$ref": "btn" },
      "text": "Get in touch",
      "props": { "fontSize": 16, "fill": "#FFFFFF" }
    }
  }
]
```

Let the auto-layout frame center the text label and compute the button size from padding. Never float text over a separate rectangle with absolute coordinates, and never hard-code a button label's width.

### Divider without a line node

Add a single-sided stroke to the container frame instead of inserting extra line layers:

```json
{
  "stroke": "#E5E7EB",
  "strokeWeight": 1,
  "strokeSides": [false, false, true, false]
}
```

`strokeSides` is a four-boolean array: `[top, right, bottom, left]`.

### Circle avatar or icon badge

Use a square frame with `cornerRadius` set to half its width/height and centered layout:

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

### Wrapping body text and vertical alignment

- **Multi-line body text**: Set an explicit `width` (or `sizingH: "fill"` inside a sized parent) with `textAutoResize: "height"` so the width stays fixed and the height hugs wrapped lines. Leave headings and short labels at the default (`hug` on both axes); avoid `textAutoResize: "none"`.
- **Vertical centering**: `textAlignVertical` (`top` | `middle` | `bottom`) does not geometrically center fixed-height text boxes. Center text vertically by placing it inside an auto-layout frame with `crossAlign: "center"`.

## Tokens before values

- **Color palette**: Pick one accent color and a consistent neutral ramp (such as `#111827`, `#4B5563`, `#6B7280`, `#E5E7EB`).
- **Spacing scale**: Stick to a `4`/`8` px scale (`8`, `16`, `24`, `32`, `64`, `80`) with one `gap` and `padding` rhythm per container depth.
- **Semantic layer names**: Name every layer clearly (`nav`, `hero-title`, `btn-primary-label`) so `inspect` output and subsequent edits stay readable.
- **WCAG contrast check**: Verify contrast before rendering. Body text requires at least `4.5:1` (WCAG AA): `#6B7280` on `#FFFFFF` (`4.8:1`) passes, whereas `#9CA3AF` on `#FFFFFF` (`2.8:1`) fails.

## Verification loop (model first, pixels second)

Run this two-step check after each section batch:

1. **Model check (`inspect`)**: Call MCP `inspect {id, depth}` (`node.get`) or `inspect {depth}` (`document.inspect`) to inspect solved `width`, `height`, and `absoluteBounds` (or run `figcraft-cli convert out.figcraft out.json` on the CLI). Confirm that every frame solved to its intended dimensions and that no container silently fell back to `100×100`.
2. **Pixel check (`render {ids: [<frame_id>]}`)**: Render the frame and verify:
   - No ink touches the outer canvas edge (unless full-bleed is intended), confirming nothing is clipped.
   - Top-to-bottom and left-to-right visual order matches the layout hierarchy.
   - Expected background fills, strokes, and placed images are visible ([images.md](images.md#checks-after-placing)).
   - Labels sit inside their containers. Judge spacing from the model's `gap` and `absoluteBounds` rather than raw ink pixel distance, because glyph ascenders/descenders and line-height add visual whitespace.
3. **Repair and re-verify**: If a section fails verification, undo the batch with `exec {command: "edit.undo"}` or patch the specific layer with `exec {command: "node.set", params: {...}}`, then re-run `inspect` and `render`.

## Provenance

Adapted from Figma's official agent design guidance (auto layout for responsive structure, design tokens, semantic layer naming, section-by-section construction, visual QA, and WCAG contrast) mapped onto FigCraft's command registry.
