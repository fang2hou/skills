# Building designs in FigCraft — patterns and QA

Construction doctrine distilled from Figma's official agent guidance
(auto layout, tokens, semantic naming, section-by-section builds, screenshot
verification) and adapted to figcraft's command registry. Every pattern and
every pitfall below was verified against figcraft v0.6.0 (2026-10).

## The one rule that prevents most broken layouts

**An auto-layout frame never sizes itself.** Without `sizingH`/`sizingV`
(or explicit width/height) a frame solves to a fixed 100×100, and frames
clip their children by default (`clip: true`). Symptoms seen in practice:

- A 156 px button rendered 96 px wide — its parent row frame was 100×100
  and clipped it at the right edge.
- A sibling button vanished entirely — it started past the parent's clip
  edge.
- A nav divider landed at y=99 instead of ~75 — the nav frame defaulted to
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

### Button (the canonical hug pattern)

```json
{ "command": "frame.create", "params": { "parent": <row>, "x": 0, "y": 0, "name": "btn-primary", "props": { "layout": "horizontal", "sizingH": "hug", "sizingV": "hug", "padding": [15, 32, 15, 32], "cornerRadius": 10, "fill": "#111827", "mainAlign": "center", "crossAlign": "center" } } },
{ "command": "node.create", "params": { "type": "text", "parent": <btn>, "x": 0, "y": 0, "text": "Get in touch", "props": { "fontSize": 16, "fill": "#FFFFFF" } } }
```

The label is centered by the layout engine — never place text over a
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
center fixed-height text — center with a layout container instead.

## Tokens before values

- One accent color; neutrals from a gray ramp (e.g. Tailwind-ish
  `#111827`/`#4B5563`/`#6B7280`/`#E5E7EB`).
- Spacing on a 4/8 scale (8, 16, 24, 32, 64, 80); one `gap` and one `padding`
  rhythm per container level.
- Name every layer semantically (`nav`, `hero-title`, `btn-primary-label`) —
  `run` scripts and later edits both depend on names.
- Check contrast **before** rendering: body text needs ≥ 4.5:1 (WCAG AA).
  `#6B7280` on white ≈ 4.8:1 passes; `#9CA3AF` ≈ 2.8:1 fails and was caught
  only because the check ran.

## Verification loop (model first, pixels second)

1. **Model assertions** — `figcraft-cli convert out.figcraft out.json`
   dumps every node's solved `width`/`height`/`transform`. Assert each
   frame's size matches intent; any unexpected `100×100` is a missing
   hug/fill declaration. This catches clipped or vanished elements that
   pixels alone make ambiguous.
2. **Pixel checks** — render, then:
   - no ink on canvas edge rows/columns (nothing clipped at the frame);
   - row-band structure matches the intended element sequence;
   - color blobs appear where fills should be (sample exact hexes);
   - label centroids sit inside their containers (expect a few px of glyph
     side-bearing asymmetry — the model, not ink, is the centering truth);
   - side margins clean (e.g. nothing left of x=80 on an 80 px-margin page).
   - Judge element gaps from the model: ink gaps include text leading, so a
     24 px `gap` renders as ~33–60 px of ink separation depending on
     line-height.
3. Fix the script, rerun the whole `run` script (it is atomic), re-verify.

A worked example of the full pattern (page skeleton, nav, hero, buttons,
footer) lives in the skill's trial history: 17 steps, all frames sized,
verified by the loop above.

## Where the guidance comes from

Figma's agent guidance (auto layout for responsive intent, design tokens,
semantic naming, breaking screens into sections, screenshot validation,
WCAG) mapped onto figcraft's registry; see Figma's MCP skills documentation
and `docs/` in the figcraft repository for the upstream principles.
