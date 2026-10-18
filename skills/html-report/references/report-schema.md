# Report JSON Reference

The report is data, not markup: the agent writes `report.json`, and the renderer
(fang2hou/report-kit, vendored prebuilt in `assets/report-template.html`) turns it
into a single self-contained `index.html`. This file is the authoring contract;
`scripts/build.py` guards the shape before injecting the data.

Rich text fields (noted per block) hold a small trusted subset of HTML —
`<strong>`, `<code>`, `<a href>`, `<span class="chip ok|warn|risk|accent">`,
`<time>`, `<br>`. The report author is trusted (same model as the old
hand-written template); never render untrusted input through these fields.

## Top level

```json
{
  "lang": "zh-CN",
  "title": "3 of 12 dependencies can be removed now",
  "kicker": "Dependency audit · 2026-10-16",
  "meta": "Scope and sources in one line.",
  "summary": ["<strong>Remove 3 packages</strong>: lodash, moment, classnames."],
  "sections": [{ "id": "optional-anchor", "heading": "Packages to remove", "blocks": [] }],
  "review": { "questions": [] }
}
```

- `lang` drives fonts, line breaking, and every UI string (`zh-CN`, `ja`, `en`).
  Write all visible text in this language.
- `summary` renders in the conclusion box; each point is rich text.
- With five or more sections the renderer adds a table of contents automatically;
  optional `id` gives an anchor a stable name (each-key and TOC link).
- `review` is optional; a report that ends with questions is a review page.

## Blocks

One block per idea; most sections need only paragraphs plus at most one
component. Pick by content shape using the table in [components.md](components.md).

| Block       | Fields                                          | Rich text                        | Notes                                                                                                                                                                                |
| ----------- | ----------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `p`         | `text`                                          | yes                              | The default. Anything that needs no box.                                                                                                                                             |
| `ul` / `ol` | `items: string[]`                               | yes                              | Plain lists.                                                                                                                                                                         |
| `steps`     | `items: string[]`                               | yes                              | Ordered actions only; numbering is automatic.                                                                                                                                        |
| `callout`   | `variant?: "ok"\|"warn"\|"risk"`, `text`        | yes                              | Plain for notes; a variant only when the status is real.                                                                                                                             |
| `card`      | `text`                                          | yes                              | A framed aside. Use sparingly.                                                                                                                                                       |
| `kv`        | `entries: {k, v}[]`                             | `v` yes                          | A few facts about one thing.                                                                                                                                                         |
| `figures`   | `items: {value, label}[]`                       | no                               | 2–4 numbers that carry the finding; unit inside `value`.                                                                                                                             |
| `table`     | `columns`, `rows: string[][]`, `num?: number[]` | cells yes                        | `num` lists right-aligned column indexes. Wrap chips and `<time>` in cells freely.                                                                                                   |
| `bars`      | `items: {label, value, display}[]`, `max?`      | no                               | One measure across ≤ ~12 items; sort by value; `value ÷ max` sets the bar.                                                                                                           |
| `compare`   | `wide?: boolean`, `cards[]`                     | `heading`, `text`, pros/cons yes | `cards[].pick` marks the recommendation; `cards[].badge` floats a small label on the card's top border (`推荐`). Keep pros/cons to three lines.                                      |
| `pair`      | `tr`, `orig`, `origLang`                        | yes                              | A quote in another language: translation first, original keeps its language.                                                                                                         |
| `details`   | `summary`, `pre?`, `body?: string[]`            | `body` yes                       | Evidence most readers skip. `pre` is plain text (already code-styled).                                                                                                               |
| `figure`    | `svg`, `caption`, `wide?`                       | caption no                       | Inline SVG: `viewBox`, no fixed size, `currentColor` + CSS variables, text ≥ 14. For structured diagrams render Mermaid first — see [diagrams.md](diagrams.md) — then paste the SVG. |

`id` is optional on every block; it makes list keys structural for pages whose
blocks repeat.

## Review questions

All questions land in one form; the renderer adds the progress count, submit
bar, localStorage, and the server round-trip. Ask only what changes the next
action; keep a page to 10 questions, a verdict list counting as one.

`id` must be ASCII (it becomes the form field name) and stable across rounds.
State comes back as `state.json` with `answers[id] = {value, label?}` and
`answers["id:note"] = {value}` — act on `value`, quote `label`.

```json
{
  "type": "choice",
  "id": "zod-plan",
  "text": "How should we upgrade zod?",
  "hint": "This sets the PR size.",
  "cols": true,
  "note": true,
  "options": [
    { "value": "all-at-once", "label": "All at once", "desc": "One PR, about 400 lines" },
    {
      "value": "per-form",
      "label": "One form at a time",
      "desc": "5 PRs, both APIs live for a while"
    }
  ]
}
```

- `cols` lays two or three short options side by side; `note` adds an optional
  comment field; `multiple: true` switches to checkboxes (answers come back as
  arrays). Put the recommended option first and state its cost in `desc`.

```json
{
  "type": "verdict",
  "id": "packages",
  "text": "Decide each package",
  "items": [
    {
      "id": "lodash",
      "label": "lodash",
      "chip": "72 KB",
      "hint": "No imports left since September.",
      "verdicts": [
        { "value": "remove", "label": "Remove", "tone": "risk" },
        { "value": "keep", "label": "Keep", "tone": "ok" },
        { "value": "later", "label": "Later", "tone": "warn" }
      ]
    }
  ]
}
```

- One verdict row per item. `tone` colors the pill by what the choice does:
  `risk` destructive/irreversible, `ok` safe/unchanged, `warn` deferral. Give
  the same verdict the same tone on every item. `chip` shows a short fact next
  to the item name. In a list of more than 10, pre-select the recommendation by
  noting it in the hint so the user changes only exceptions.

```json
{
  "type": "text",
  "id": "extra-notes",
  "text": "Anything else I should know?",
  "multiline": true,
  "placeholder": "Optional"
}
```

- Free text; `multiline` for answers longer than one line. Text answers are
  never required.

## Regenerating the template

`assets/report-template.html` is a build artifact of
[fang2hou/report-kit](https://github.com/fang2hou/report-kit): run
`pnpm exec vite build` there and copy `build/index.html` over it. The marker
`<script id="report-data" type="application/json">null</script>` (or at minimum
a `<body>` tag) must survive; `build.py` fails loudly if it does not.
