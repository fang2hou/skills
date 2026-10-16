# Components

Markup for every component the template styles. Copy the snippet, replace the text, and keep the class names; the template's CSS and script depend on them.

Contents:

- [Choose by content shape](#choose-by-content-shape)
- [Page frame](#page-frame)
- [Reading components](#reading-components)
- [Data components](#data-components)
- [Diagrams and images](#diagrams-and-images)
- [Review components](#review-components)
- [Read-through checklist](#read-through-checklist)

## Choose by content shape

Use one component per idea. If two components could show the same content, pick the first match in this table.

| The content is…                                     | Use                                    |
| --------------------------------------------------- | -------------------------------------- |
| The result the reader must take away                | Summary box                            |
| A warning, risk, or decision the reader must notice | Callout (`warn`, `risk`, `ok`, plain)  |
| 2–4 numbers that carry the main finding             | Figures row                            |
| A few facts about one thing (owner, version, date)  | Key-value list                         |
| Records with the same fields                        | Table                                  |
| One measure across a few items                      | Bars                                   |
| A trend over time or a flow between parts           | Inline SVG                             |
| Options the reader weighs against each other        | Compare cards                          |
| An ordered procedure                                | Steps                                  |
| Text quoted from another language                   | Pair                                   |
| Evidence most readers skip: logs, raw output        | Details                                |
| A status word inside a sentence or table cell       | Chip                                   |
| A question for the user                             | Review components                      |
| Anything else                                       | Paragraphs and lists; they need no box |

Most sections need only headings, paragraphs, and at most one component. A page where every block sits in a box reads as noise.

## Page frame

Everything goes inside `<main class="page">`. Children use the narrow reading column. Add `class="wide"` to a compare grid, a table with many columns, or a large figure to let it break out to 1080 px. The contrast is deliberate: text stays narrow and easy to read, and the one thing the reader should look at side by side gets the full width. Use it for at most a few blocks per page; if everything is wide, nothing stands out.

```html
<header class="masthead">
  <p class="kicker">依赖审计 · 2026-10-16</p>
  <h1>12个依赖里有3个可以直接删除</h1>
  <p class="meta">范围：apps/web 的 package.json。依据：pnpm why、代码搜索、发布记录。</p>
</header>
```

Table of contents for reports with five or more sections; give each `h2` a matching `id`:

```html
<ol class="toc">
  <li><a href="#remove">可以删除的包</a></li>
  <li><a href="#zod">zod 升级</a></li>
</ol>
```

## Reading components

Summary box, directly after the masthead:

```html
<section class="summary">
  <h2>结论</h2>
  <ul>
    <li><strong>可删除3个</strong>：lodash、moment、classnames。删除后体积减少约180 KB。</li>
    <li>zod 4需要单独升级，影响14个文件。</li>
  </ul>
</section>
```

Callout. Plain for notes; `ok`, `warn`, `risk` only when the status is real:

```html
<div class="callout warn">
  <p><strong>zod 4的升级要单独做。</strong>它改了错误信息的结构。</p>
</div>
```

Chip, inside text or a table cell. Variants: `ok`, `warn`, `risk`, `accent`, or none for neutral:

```html
<span class="chip ok">删除</span>
```

Steps:

```html
<ol class="steps">
  <li>删除三个包并运行 <code>pnpm install</code>。</li>
  <li>跑完整测试和构建。</li>
</ol>
```

Pair, for a quote in another language. The translation comes first; the original keeps its `lang`:

```html
<div class="pair">
  <p class="tr">Zod 4 把错误自定义统一到 <code>error</code> 参数。</p>
  <p class="orig" lang="en">
    Zod 4 standardizes error customization under a single <code>error</code> param.
  </p>
</div>
```

Details, for evidence. Printing opens every `details` automatically:

```html
<details>
  <summary>搜索命令与完整输出</summary>
  <pre><code>$ rg -l "from 'lodash'" apps/web</code></pre>
</details>
```

Card, for a self-contained aside that needs a frame. Use sparingly:

```html
<div class="card"><p>…</p></div>
```

Key-value list, for a few facts about one thing. Use a table instead when several things share the same fields:

```html
<dl class="kv">
  <dt>负责人</dt>
  <dd>前端组</dd>
  <dt>当前版本</dt>
  <dd>zod 3.23.8</dd>
</dl>
```

## Data components

Figures row, right after the summary when two to four numbers carry the main finding. Put the unit in the number and keep each label to a few words:

```html
<div class="figures">
  <div><b>12</b><span>依赖总数</span></div>
  <div><b>180 KB</b><span>预计减少的体积</span></div>
</div>
```

Table. Always wrap it so wide tables scroll instead of breaking the page; right-align numbers with `num`:

```html
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>包</th>
        <th class="num">体积</th>
        <th>结论</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>moment</td>
        <td class="num">96 KB</td>
        <td><span class="chip ok">删除</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

Bars, for one measure across up to about 12 items. Set each `--v` to value ÷ axis maximum as a percentage, using one maximum for all bars; sort by value and print the value:

```html
<div class="bars">
  <span>moment</span><span class="track"><i style="--v: 53%"></i></span
  ><span class="v">96 KB</span> <span>lodash</span
  ><span class="track"><i style="--v: 40%"></i></span><span class="v">72 KB</span>
</div>
```

Compare cards. Mark the recommended option with `pick` and a chip; keep pros and cons to three lines each:

```html
<div class="compare wide">
  <article class="pick">
    <h3>一次性升级 <span class="chip accent">推荐</span></h3>
    <p>一个 PR 改完14个文件。</p>
    <ul class="pros">
      <li>改动集中，好审查</li>
    </ul>
    <ul class="cons">
      <li>PR 较大，约400行</li>
    </ul>
  </article>
  <article>…</article>
</div>
```

## Diagrams and images

Draw charts and diagrams as inline SVG. Rules:

- Set `viewBox` and no fixed `width`/`height`, so the figure scales.
- Use `currentColor` and the template's CSS variables (`var(--accent)`, `var(--line-2)`, `var(--muted)`) for strokes and fills. Use at most one accent color plus gray.
- Label lines and boxes directly; add a legend only when direct labels do not fit.
- Bars and areas start at zero. Say the unit in the caption.
- Text inside SVG uses `font-family="inherit"` and a `font-size` of at least 14.

```html
<figure>
  <svg
    viewBox="0 0 520 90"
    role="img"
    aria-label="请求流程：浏览器到缓存再到源站"
    font-family="inherit"
    font-size="15"
  >
    <g fill="none" stroke="var(--line-2)" stroke-width="1.5">
      <rect x="1" y="20" width="120" height="48" rx="8" />
      <rect x="200" y="20" width="120" height="48" rx="8" />
      <rect x="399" y="20" width="120" height="48" rx="8" />
      <path d="M121 44h79M320 44h79" stroke="var(--accent)" />
    </g>
    <g fill="currentColor" text-anchor="middle">
      <text x="61" y="49">浏览器</text>
      <text x="260" y="49">缓存</text>
      <text x="459" y="49">源站</text>
    </g>
  </svg>
  <figcaption>命中缓存时，请求不到源站。</figcaption>
</figure>
```

Use a raster image only for something that cannot be drawn: a screenshot, a photo. Resize and compress it first (for example `cwebp -q 75 -resize 1600 0 in.png -o out.webp`), then embed it as a data URI or keep it as a file next to `index.html` and reference it with a relative path. A served directory serves sibling files; a plain report must embed.

## Review components

All review components go inside one `<form data-review>`. The template script adds the submit bar; do not write one.

Single choice, as option cards. Add `cols` to the `options` div for two or three short options side by side:

```html
<fieldset class="q" data-required="zod-plan">
  <legend>zod 用哪种方式升级？</legend>
  <p class="hint">影响 PR 的大小和审查方式。</p>
  <div class="options cols">
    <label class="option"
      ><input type="radio" name="zod-plan" value="all-at-once" /><span class="t">一次性升级</span
      ><span class="d">一个 PR，约400行</span></label
    >
    <label class="option"
      ><input type="radio" name="zod-plan" value="per-form" /><span class="t">逐个表单迁移</span
      ><span class="d">5个 PR，两套 API 并存</span></label
    >
  </div>
  <input type="text" name="zod-plan:note" placeholder="补充说明（可选）" />
</fieldset>
```

Multiple choice: the same markup with `type="checkbox"` and one shared `name`. The answer `value` becomes an array.

Verdict per item, for reviewing a list. One `fieldset.item` per item inside a `fieldset.q`. The pill row sits to the right of the item name and hint when the card is wide enough, and below them on a narrow screen. Keep each pill label to about four CJK characters or two English words so the row fits beside the text.

Tone classes color each pill by what the choice does: `risk` for a destructive or irreversible action (delete, reject), `ok` for the safe or unchanged outcome (keep, approve), `warn` for a deferral or partial answer (later, unsure). A pill without a class gets a neutral dot and the accent color when selected. Give the same verdict the same tone on every item, so a color means one thing across the page:

```html
<fieldset class="q">
  <legend>逐项确认</legend>
  <fieldset class="item" data-required="lodash">
    <legend>lodash <span class="chip">72 KB</span></legend>
    <p class="hint">2026年9月重构后已无引用。</p>
    <div class="seg">
      <label class="risk"
        ><input type="radio" name="lodash" value="remove" /><span>删除</span></label
      >
      <label class="ok"><input type="radio" name="lodash" value="keep" /><span>保留</span></label>
      <label class="warn"
        ><input type="radio" name="lodash" value="later" /><span>以后再说</span></label
      >
    </div>
    <input type="text" name="lodash:note" placeholder="备注（可选）" />
  </fieldset>
</fieldset>
```

Free text, for an open question. Use `textarea` only when the answer may run longer than one line:

```html
<fieldset class="q">
  <legend>还有什么要我注意的？</legend>
  <textarea name="extra-notes" placeholder="可以留空"></textarea>
</fieldset>
```

When an item quotes foreign-language text the user must judge (a memory entry, an issue title), put a `.pair` inside the item so the translation sits above the original.

## Read-through checklist

Use this when no browser can render the page:

- [ ] `<html lang>` matches the page language; `<title>` is set; there is one `h1`.
- [ ] The masthead and summary placeholders from the template are gone.
- [ ] Every table sits in `.table-wrap`; every SVG has a `viewBox` and no fixed width.
- [ ] Every form control has a `name`; radio groups share one `name`; every `value` is an ASCII ID; every visible label is in the page language.
- [ ] Every `data-required` value names a control inside its `fieldset`.
- [ ] No `<script src>`, `<link rel="stylesheet">`, web font, or remote image remains.
- [ ] Foreign-language quotes sit in `.pair` blocks with a `lang` attribute.
- [ ] `wc -c index.html` is within the size budget.
