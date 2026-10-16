---
name: html-report
description: >
  Builds readable single-file HTML reports and interactive review pages whose answers
  the agent reads back from a local JSON file. Use when the user asks for a report,
  audit, comparison, or write-up, or must choose, approve, or comment on items.
license: MIT
compatibility: Requires file write access and a browser. Review pages need uv (or Python 3.11+) to run the bundled local server on 127.0.0.1.
metadata:
  author: fang2hou
  version: "1.0"
  sources: "User report and review-page preferences; Claude Code artifacts docs; dogum/html-artifacts; MDN CSS Text 4; Orwell, Politics and the English Language"
---

# HTML Report

Turns findings into one calm, readable HTML page, and turns questions for the user into a page whose answers land in `state.json` for the agent to read.

## When to Use

- The user asks for a report, 技术报告, audit, investigation summary, comparison, or plan meant to be read, not applied.
- The answer would exceed about one screen of chat, or needs tables, side-by-side options, charts, or translated source quotes.
- The agent needs decisions with context: pick among options, approve or reject a list, triage items, or comment per item. A page beats a chat question when there are three or more questions, or when each choice needs its trade-offs shown.
- A long task should show its progress in a page that refreshes as the agent works.

## When NOT to Use

- Short answers, or one yes/no question: reply in chat or use the harness's question tool.
- Code, config, commands, or diffs the user will apply: put them in chat or in the files.
- Documents that live in git and get diffed (README, ADR, CHANGELOG): write Markdown.
- Product UI, websites, or slide decks: those are frontend work with their own design system.

## Hard Rules

Instructions the user gives in the current conversation (language, layout, colors, file location) override these rules and the template defaults.

1. **One self-contained file from the template.** Start from [assets/template.html](assets/template.html). No CDN scripts, web fonts, or remote images, because the page must open offline and stay small.
2. **Conclusion first.** The first screen holds a title that states the main finding and a summary box with 2–5 points. The reader decides from these whether to read on.
3. **Plain writing.** Follow [references/writing.md](references/writing.md) for every sentence, heading, label, and option.
4. **The reader's language.** Write in the user's conversation language and set `<html lang>` to match (`zh-CN`, `zh-TW`, `ja`, `ko`, `en`). Text quoted in another language gets a translation first and keeps the original, because the user decides from the translation and the agent acts on the original.
5. **Answers come back through a file.** Review pages run [scripts/serve.py](scripts/serve.py); the agent reads `state.json`. Ask the user to copy or paste answers only when the server cannot run.
6. **Size budget.** The finished HTML stays under 150 KB without raster images. Use inline SVG or CSS for charts. Each raster image is WebP or JPEG, at most 1600 px wide and 200 KB; the whole file stays under 1 MB. Base64 adds a third to an image's size.
7. **Keep the template's look.** Cream background, blue-black ink, one accent color, status colors only for status. Text stays in the narrow reading column; only a comparison, a many-column table, or a large figure breaks out with `.wide`, so the one thing to compare side by side stands out. Use the big-number figures row when two to four numbers carry the main finding. Do not add gradients, emoji headings, decorative icons, or animations. Do not shrink the type: body text is 17.5–18 px and nothing is smaller than 14 px, because the page is for reading.
8. **Verify before handing over.** Render the page and fix what you see (Step 6).

## Workflow

### Step 1: Choose the page type

| Type        | Use when                                     | Server                                         |
| ----------- | -------------------------------------------- | ---------------------------------------------- |
| Report      | The user only reads                          | None; open the file directly                   |
| Live report | The agent keeps updating it during long work | `serve.py start`; the page reloads on change   |
| Review page | The user must choose, approve, or comment    | `serve.py start`; answers land in `state.json` |

A report may end with a review section. Treat it as a review page.

### Step 2: Create the working directory

```bash
base="${TMPDIR:-/tmp}"; dir="${base%/}/html-report/$(date +%Y%m%d-%H%M)-<short-slug>"
mkdir -p "$dir" && cp <skill-dir>/assets/template.html "$dir/index.html"
```

Write to a project path instead when the user names one or when the report belongs to that project. One directory holds one page and one round of questions.

### Step 3: Write the content

1. Read [references/writing.md](references/writing.md) and [references/components.md](references/components.md).
2. Outline before writing: the title states the main finding, the summary lists the 2–5 points that matter, and each section heading states that section's point.
3. Edit `<html lang>` and `<title>`, then replace the placeholder masthead and summary inside `<main class="page">`.
4. Pick one component per idea, using the "Choose by content shape" table in components.md. Leave the template's `<style>` and `<script>` unchanged; put any page-specific CSS in a second short `<style>` block.
5. For a long report with five or more sections, add the table of contents after the summary.

### Step 4: Build the review form (review pages only)

Wrap the questions in `<form data-review>`; the template script adds the progress count, save status, Copy, and Submit controls by itself. For each question:

- Give every input a stable ASCII `name` and `value` (`zod-plan`, `all-at-once`). Show the user a label written in the page language. Never show an ID as the label.
- Mark questions the user must answer with `data-required="<name>"` on the `fieldset`.
- Use radio buttons for one answer, checkboxes for several, the `.seg` row for a verdict per item, and an `<input type="text" name="<name>:note">` for an optional comment. Color verdict pills by consequence (`risk` deletes or cannot be undone, `ok` keeps things as they are, `warn` defers), the same way on every item.
- Put the recommended option first and mark it with a `推荐`/`Recommended` chip; write each option's cost in its description.
- For lists over 10 items, pre-select the recommended verdict and say so in the hint, so the user changes only the exceptions. Otherwise leave options unselected.
- Ask only what changes the next action. Keep a page to ten questions or fewer; a verdict list counts as one question however many items it holds. Split larger reviews into rounds.

### Step 5: Serve

For a live report or review page:

```bash
uv run <skill-dir>/scripts/serve.py start "$dir"
# prints {"url": "http://127.0.0.1:PORT/", "dir": ..., "pid": ..., "state": ".../state.json"}
```

`start` reuses a running server for the same directory. Without uv, run it with `python3` 3.11 or newer. A plain report needs no server.

### Step 6: Verify

Verify before the user opens the page, so test answers never reach them.

1. Run `wc -c "$dir/index.html"` and compare against the size budget.
2. With a browser tool, load the page at 1280 px and 400 px wide. Check the screenshots, the console for errors, and that `document.documentElement.scrollWidth` does not exceed `clientWidth`.
3. On a review page, click one option and confirm `state.json` changed. Then reset: run `localStorage.clear()` in that tab, close it, and delete `state.json`. The page keeps a browser copy of its answers and sends it back on the next load, so deleting the file alone does not reset it.
4. Without a browser tool, take headless screenshots: `"<chrome-binary>" --headless --screenshot=/tmp/check.png --window-size=1280,2400 "<url-or-file-url>"`, and repeat at `400,2400`.
5. If no browser runs at all, run the read-through checklist at the end of components.md, and say in the hand-over that the page was checked by reading only.

### Step 7: Open, hand over, and collect answers

Open the URL, or the file path for a plain report. If the agent instructions name a browser for opening pages, use it (macOS: `open -a "Google Chrome" "<url>"`); otherwise use `open` on macOS, `xdg-open` on Linux, or `start "" "<url>"` on Windows.

Reply in chat with one line on what the page holds plus its path or URL. For a review page, also say what the user needs to decide and that Submit sends the answers back.

- If the harness can run a background command and notify you when it exits, run `uv run <skill-dir>/scripts/serve.py wait "$dir" --timeout 3600` in the background and end your turn. It exits 0 and prints the state when the user clicks Submit.
- Otherwise end your turn. When the user says they are done, read `$dir/state.json` directly; the page saves every change within a second, Submit or not.
- If `wait` exits 5 (timeout), read `state.json` for partial answers and ask in chat about the rest.

### Step 8: Act on the answers

`state.json` looks like this:

```json
{
  "answers": {
    "zod-plan": { "value": "all-at-once", "label": "一次性升级" },
    "zod-plan:note": { "value": "下周再合并" },
    "extra": { "value": ["licenses"], "label": ["许可证"] }
  },
  "unanswered": ["moment"],
  "submitted": true,
  "submittedAt": "2026-10-16T09:12:03.000Z",
  "updated": "2026-10-16T09:12:03+00:00"
}
```

Act on `value`; quote `label` when confirming back to the user. Summarize the decisions in one to three lines before acting, and ask in chat only about items listed in `unanswered`. When the review is finished, stop the server with `uv run <skill-dir>/scripts/serve.py stop "$dir"` and keep the directory.

To change a served page, edit `index.html` in place: open pages reload within two seconds and keep their answers and scroll position. For a new round of questions, create a new directory, because `wait` returns at once when `state.json` already says `submitted`.

## Failure Handling

| Symptom                                                  | Action                                                                                                                                                                                             |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `serve.py start` exits 4                                 | Read `$dir/.server.log`. If Python is older than 3.11 or no Python runs, deliver the page as a file: answers then stay in the browser, and the user sends them with Copy answers.                  |
| `serve.py` exits 3                                       | The directory does not exist; create it and copy the template first.                                                                                                                               |
| The page says it is not connected                        | The server stopped (it exits after 4 hours without requests). Run `serve.py start "$dir"` again; it takes the previous port, so the open tab reconnects, and the answers in `state.json` are kept. |
| `state.json` is missing when the user says they are done | The page never reached the server. Run `serve.py status "$dir"`, restart if needed, and ask the user to reload the page; on load it sends the answers it kept in the browser.                      |
| Fonts look like the system default in screenshots        | A family name does not match the installed font; check it with `fc-list` and fix the stack.                                                                                                        |

## Gotchas

- A page opened from `file://` cannot write files. That is why review pages need `serve.py`. On `file://` the template keeps answers in the browser and offers Copy answers as the last resort.
- Installed font names often differ from the marketing names. On the author's Mac, LXGW Neo ZhiSong installs as `LXGW Neo ZhiSong Screen Full` and Source Han Sans as `Source Han Sans SC VF`; a stack that lists only the short names falls through to the system font. Before adding a font, check the exact name with `fc-list : family | rg -i "<name>"`.
- In Chinese and Japanese text, do not type spaces between CJK characters and Latin letters or digits. The template's `text-autospace` adds a small gap, and a typed space creates a line-break point: a Japanese heading broke as "3 / 個". Korean is the opposite: it uses real spaces, so the template turns autospace off for `lang="ko"`.
- Fonts follow the `lang` attribute. Japanese quoted inside a Chinese report needs an element with `lang="ja"`, or its kanji render in Chinese glyph shapes.
- Submit with unanswered required items first highlights them; a second click submits and records them in `unanswered`.
- macOS `$TMPDIR` lives under `/var/folders` and the system purges files there after days without access. Tell the user to copy a report they want to keep, or write it to a project path.

## Output Contract

1. The page path, and the URL when served.
2. One chat line on what the page holds and, for a review page, what the user must decide.
3. After a review: the decisions read from `state.json`, the unanswered items, and the server stopped.

## References

- [references/writing.md](references/writing.md): load before writing any text in Step 3.
- [references/components.md](references/components.md): load in Step 3 to choose markup; holds the read-through checklist for Step 6.
- [references/typography.md](references/typography.md): load only when changing fonts, sizes, or colors, or when writing in a language the template does not cover.
- `scripts/serve.py --help`: commands, HTTP API, and exit codes of the local server.
