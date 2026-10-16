# Typography and Color

Why the template looks the way it does, and how to change it without losing readability. Load this only when changing fonts, sizes, or colors, or when writing a page in a language the template does not cover.

Contents:

- [Font stacks by language](#font-stacks-by-language)
- [Sizes and spacing](#sizes-and-spacing)
- [CJK line breaking and spacing](#cjk-line-breaking-and-spacing)
- [Color tokens](#color-tokens)
- [Corners](#corners)
- [Adding a language](#adding-a-language)

## Font stacks by language

Each language sets three tokens on `:lang(...)`: `--ui` for headings, tables, labels, and controls; `--body` for long prose; `--mono` for code. Because the tokens are set per element, an element with its own `lang` attribute switches fonts inside a page of another language.

| Language         | `--ui` (first choice → fallback)                                        | `--body`                                                          | Why                                                                                                                          |
| ---------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| zh-CN            | IBM Plex Sans SC → Source Han Sans SC VF → PingFang SC                  | FZPingXianYaSong-R-GBK → LXGW Neo ZhiSong Screen Full → Songti SC | The user prefers Song-style serif for long reading; FZ PingXian YaSong is drawn for screens.                                 |
| zh-TW, zh-HK     | IBM Plex Sans TC → Source Han Sans TC VF → PingFang TC                  | Source Han Serif TC → Songti TC                                   | Traditional glyph shapes need TC fonts.                                                                                      |
| ja               | IBM Plex Sans JP → Source Han Sans VF → Hiragino Sans                   | Hiragino Mincho ProN → Yu Mincho → Source Han Serif JP            | Mincho matches the Song-style preference. BIZ UDMincho is excluded: its Latin letters are monospaced and look broken.        |
| ko               | IBM Plex Sans KR → Source Han Sans K VF → Apple SD Gothic Neo           | same as `--ui`                                                    | Korean screen reading uses Gothic; Myeongjo fonts on macOS render thin at body sizes.                                        |
| en (and default) | IBM Plex Sans → IBM Plex Sans JP → system sans                          | Charter → Iowan Old Style → Georgia                               | Charter is a screen-friendly serif shipped with macOS. Plex Sans JP carries the same Latin glyphs when Plex Sans is missing. |
| code (all)       | JetBrainsMono Nerd Font → JetBrains Mono → IBM Plex Mono → ui-monospace | —                                                                 | The user's code font.                                                                                                        |

In Chinese and Japanese prose, `strong` switches to the `--ui` font, following the CJK convention of setting emphasis in Gothic/Hei inside Mincho/Song text. It also avoids fake bold: several Song fonts ship only one weight.

Family names must match what the system installed, not the marketing name. Check with `fc-list : family | rg -i "<name>"`. Variable-font installs often add a suffix, such as `Source Han Sans SC VF`.

## Sizes and spacing

The user found earlier reports too small (body 16.5 px, tables 13–14.5 px, labels 11–13 px). The template sets:

| Element               | Latin                 | CJK                   |
| --------------------- | --------------------- | --------------------- |
| Body text             | 18 px, line 1.65      | 17.5 px, line 1.8–1.9 |
| Letter spacing (body) | 0                     | zh 0.02em, ja 0.04em  |
| Line length           | 68ch                  | 36–38em               |
| Tables, controls      | 0.9em (about 16 px)   | 0.9em                 |
| Smallest text (chips) | 14 px                 | 14 px                 |
| h1 / h2 / h3          | 2em / 1.42em / 1.14em | same                  |

Rules when changing sizes:

- Keep at least a 1.25× step between heading levels; the user reads hierarchy from size, and small steps look flat.
- Do not set any text below 14 px.
- Keep CJK line height at 1.8 or more; CJK glyphs fill the em box and need more space between lines than Latin.
- Set letter spacing to 0 inside code, tables, and controls; tracking hurts dense text.

## CJK line breaking and spacing

- `text-autospace: normal` on `body` adds about an eighth of an em between CJK and Latin letters or digits. Writers must not type spaces there; a typed space is wider and becomes a line-break point.
- Korean turns autospace off and uses `word-break: keep-all`, so lines break at the spaces between words, not inside them.
- Japanese uses `line-break: strict` (no small kana or prolonged sound marks at line start) and `word-break: auto-phrase` on headings, which breaks at phrase boundaries. Chrome applies `auto-phrase` only when `lang="ja"`.
- `text-wrap: balance` on headings and `text-wrap: pretty` on prose avoid one-word last lines.

These properties are ignored by browsers that lack them; the page still reads correctly.

## Color tokens

Contrast ratios are against the cream background `--bg` `#faf6ef`. Every text color passes WCAG AA (4.5:1). Black is softened to blue-black for a calmer page without losing contrast.

| Token                | Value                | Contrast | Use                                              |
| -------------------- | -------------------- | -------- | ------------------------------------------------ |
| `--ink`              | `#28303b`            | 12.4     | Body text and headings                           |
| `--ink-2`            | `#4a5462`            | 7.1      | Secondary text, table headers                    |
| `--muted`            | `#646c78`            | 4.9      | Meta lines, hints, captions; the lightest text   |
| `--accent`           | `#3a5470`            | 7.3      | Links, focus, selected controls, one data series |
| `--ok` / `--ok-soft` | `#3d6a4c`            | 5.8      | Done, safe, keep                                 |
| `--warn`             | `#85571a`            | 5.8      | Needs attention                                  |
| `--risk`             | `#99392f`            | 6.5      | Breaking, unsafe, missing                        |
| `--line`, `--line-2` | `#e4dccf`, `#d3c9b8` | —        | Rules and borders only, never text               |

Do not add colors for decoration. If a chart needs a second series, use `--ink-2` or `--muted`, not a new hue. Never use a gray lighter than `--muted` for text; earlier reports used `#8a8175` (3.5:1), which the user found hard to read.

## Corners

Large surfaces (cards, the summary, question cards, the submit bar) use 14 px corners, upgraded to a 20 px squircle where `corner-shape` is supported. Small controls (options, buttons, inputs) use plain 8 px corners. A rounded element nested in another keeps concentric corners: inner radius = outer radius − the gap between them (count the border). When the gap is larger than the outer radius, use the small 8 px or 4 px radius.

## Controls and scrollbars

Radio buttons and checkboxes are drawn by the template at 1.15 em, so they match the option text instead of the small browser default. The page scrollbar is a thin thumb in the ink color, 3 px from the window edge. It shows while the page scrolls or the pointer nears the right edge, fades out after about a second, and can be dragged. Inner scroll areas (wide tables, code blocks) use the browser's thin scrollbar in the same color. Do not restyle these per page.

## Adding a language

1. Add a `:lang(xx)` block next to the others with `--ui`, `--body`, `--fs`, `--lh`, `--ls`, and `--measure`.
2. Choose fonts that are installed (`fc-list`), with a system fallback last.
3. Add the language to the `STRINGS` object in the page's copy of the template script, written natively, with the same keys as `en`. When the language will be used again, add it to `assets/template.html` as well.
4. Render a sample paragraph with mixed Latin text and digits, and check line breaks and spacing in a screenshot.
