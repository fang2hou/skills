---
name: html-report
description: >
  Default output for any answer with several findings: a desktop HTML report or review
  page. Use unasked when told to investigate, summarize recent work or commits, compare,
  audit, or explain a system, or when the user must decide several questions.
license: MIT
compatibility: Requires file write access and a browser. Review pages need uv (or Python 3.11+) to run the bundled local server on 127.0.0.1.
metadata:
  author: fang2hou
  version: "1.4"
---

# HTML Report

Turns findings into one calm HTML page for reading on a desktop screen, and turns decisions the user must make into a review page whose answers land in `state.json` for the agent to read.

## When to Use

- **A request will produce several findings, even if nobody asked for a report.** Users rarely name the format. They ask you to look into a bug, summarize recent work, explain how a subsystem works, audit dependencies, or compare approaches. Decide from the request, before you start the research: if the answer will have several causes, files, trade-offs, tables, or diagrams, plan a report from the start. Answer in the terminal only when one or two paragraphs will cover it. If a terminal answer grows past about one screen while you write it, stop and put it in a report instead.
- The user asks for a report, summary, audit, comparison, or study guide.
- **A direction call needs the user.** They must weigh options side by side, approve or reject a list, or comment per item. A page beats a chat question when there are three or more questions, or when each choice needs its trade-offs shown.
- A long task should show its progress in a browser tab that refreshes as the agent works.

## When NOT to Use

- Short answers, or one question with obvious options: reply in the terminal or use the harness's question tool.
- Code, config, commands, or diffs the user will apply: put them in chat or in the files.
- Markdown that lives in git and gets diffed (README, ADR, CHANGELOG), unless the user asks for an HTML page under `docs/`.
- Product UI, websites, or slide decks: those are frontend work with their own design system.

## Hard Rules

Instructions the user gives in the current conversation (language, layout, colors, file location) override these rules and the template defaults.

1. **One self-contained file from the template, for desktop screens.** Start from [assets/template.html](assets/template.html). No CDN scripts, web fonts, or remote images, because the page must open offline and stay small. The page is read on a desktop monitor; do not add mobile layouts or test phone widths.
2. **Conclusion first.** The first screen holds a title that states the main finding and a `.summary` box with 2–5 points. The reader decides from these whether to read on.
3. **Formal, precise writing.** Follow [references/writing.md](references/writing.md), plus [references/writing-zh.md](references/writing-zh.md) for `zh-CN` or [references/writing-ja.md](references/writing-ja.md) for `ja`. Write in a formal register, keep established technical terms, put a space between CJK characters and Latin letters or digits, and do the final pass before Step 6.
4. **The reader's language.** Use the language the user names for the report, or else the language of their latest message. Set `<html lang>` to match (`zh-CN`, `ja`, `en`). Never default to the language of the sources, the repository, or these instructions. A quote in another language goes in a `.pair` block with the translation first, because the user decides from the translation and the agent acts on the original.
5. **Answers come back through a file.** Review pages run [scripts/serve.py](scripts/serve.py), and the agent reads `state.json`. Ask the user to copy and paste answers only when the server cannot run.
6. **Size budget.** The HTML stays under 150 KB without raster images; draw charts with inline SVG or CSS. Each raster image is WebP or JPEG, at most 1600 px wide and 200 KB, and the whole file stays under 1 MB. Base64 adds a third to an image's size.
7. **Keep the template's look.** Cream background, blue-black ink, one accent color, and status colors (`ok`, `warn`, `risk`) only for status. Prose stays in the narrow reading column. Only a comparison, a many-column table, or a large figure breaks out to 1080 px with `.wide`, so the one thing to compare side by side stands out. Use the big-number figures row when two to four numbers carry the main finding. No gradients, emoji headings, decorative icons, or animations, and no text below 14 px.
8. **Verify before handing over.** Render the page and fix what you see (Step 6).

## Workflow

### Step 1: Pick the purpose

The purpose sets the page type, what the page leads with, and where the file goes.

| Purpose                | Page type   | Lead with, then                                                                                                    | Location      |
| ---------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ | ------------- |
| Investigation or audit | Report      | The answer; then the evidence, its sources, and what is not verified                                               | tmp           |
| Project summary        | Report      | The outcome in numbers; then what changed, what is left, and the risks                                             | tmp           |
| Study material         | Report      | The core idea and what the reader can do after; then concepts from simple to complex, each example before its rule | `~/Downloads` |
| Direction decision     | Review page | The decision and the recommended option; then only the context each choice needs                                   | tmp           |
| Long-task progress     | Live report | Current status and the next step                                                                                   | tmp           |

- A file the user will share goes to `~/Downloads` whatever its purpose. It is a plain report: no review form, and no local paths or references to this conversation that its reader cannot follow.
- Write into a project's `docs/` only when the user asks for project documentation there.
- When the purpose is unclear, use tmp and offer a `~/Downloads` copy in the hand-over.
- Live reports and review pages run `serve.py` (Step 5); a plain report opens as a file. A report that ends with questions is a review page.

### Step 2: Create the working directory

Build and verify every page in its own tmp directory, whatever its final location:

```bash
base="${TMPDIR:-/tmp}"; dir="${base%/}/html-report/$(date +%Y%m%d-%H%M)-<short-slug>"
mkdir -p "$dir" && cp <skill-dir>/assets/template.html "$dir/index.html"
```

One directory holds one page and one round of questions. After Step 6, copy a page bound for `~/Downloads` to `~/Downloads/<YYYYMMDD>-<short-slug>.html`, or a docs page to the path the user named. Never overwrite an existing file there.

### Step 3: Write the content

1. Read [references/writing.md](references/writing.md) and [references/components.md](references/components.md), plus the guide for the page language if there is one: [references/writing-zh.md](references/writing-zh.md) for `zh-CN`, [references/writing-ja.md](references/writing-ja.md) for `ja`.
2. Outline in the order Step 1 gives: a title that states the main finding, 2–5 summary points, and `h2` headings that each state their section's point. With five or more sections, add `<ol class="toc">` after the summary.
3. In `index.html`, replace `LANG` in `<html lang="LANG">` with the page language and set `<title>`. Fonts, line breaking, and the review controls' text all follow the `lang` tag. Then replace the placeholder masthead and summary inside `<main class="page">`.
4. Pick one component per idea from the "Choose by content shape" table in components.md. Draw a diagram where logic branches or parts depend on each other, use a table where items share fields, and leave the rest as short paragraphs.
5. Leave the template's `<style>` and `<script>` unchanged. Put page-specific CSS in a second, short `<style>` block.

### Step 4: Build the review form (review pages only)

Wrap the questions in `<form data-review>` inside `<main class="page">`. The template script adds the progress count, save status, Copy, and Submit controls; do not write them. For each question:

- Give every control a stable ASCII `name` and `value` (`zod-plan`, `all-at-once`) and a visible label in the page language. Never show an ID as the label.
- Mark questions the user must answer with `data-required="<name>"` on the `fieldset`.
- Use radio buttons for one answer, checkboxes for several, the `.seg` row for a verdict per item, and `<input type="text" name="<name>:note">` for an optional comment.
- Put the recommended option first with a chip in the page language (`推荐`, `おすすめ`, `Recommended`) and state each option's cost in its `.d` line.
- In a verdict list of more than 10 items, pre-select the recommended verdict and say so in the hint, so the user changes only the exceptions. Otherwise leave options unselected.
- Ask only what changes the next action. Keep a page to 10 questions or fewer, counting a verdict list as one question, and split larger reviews into rounds.
- Do not ask a question that applies only after a certain answer to another question on the same page ("If you chose Merge, how?"). Ask it in the next round, once the first answer is known.

### Step 5: Serve

Live reports and review pages need the server; plain reports do not.

```bash
uv run <skill-dir>/scripts/serve.py start "$dir"
# prints {"url": "http://127.0.0.1:PORT/", "dir": ..., "pid": ..., "state": ".../state.json"}
```

`start` reuses a running server for the same directory. Without uv, run the script with `python3` 3.11 or newer.

### Step 6: Verify

Verify before the user opens the page, so test answers never reach them.

1. Run `wc -c "$dir/index.html"` and compare it against the size budget. Confirm `<html lang>` holds the page language, not `LANG`.
2. Load the page at 1280 px wide with a browser tool, or take a headless screenshot: `"<chrome-binary>" --headless --screenshot=/tmp/check.png --window-size=1280,2400 "<url-or-file-url>"`. Check the screenshot, the console for errors, and that `document.documentElement.scrollWidth` does not exceed `clientWidth`. Chrome here is only for checking; Step 7 opens the page for the user.
3. On a review page, click one option and confirm `state.json` changed. Then close that tab and delete `state.json`.
4. If no browser runs at all, go through the read-through checklist at the end of components.md, and say in the hand-over that the page was checked by reading only.

### Step 7: Open, hand over, and collect answers

1. Open the URL, or the file path for a plain report (the `~/Downloads` or docs copy when one was made), in the user's default browser: `open "<url-or-file>"` on macOS, `xdg-open` on Linux, `start "" "<url-or-file>"` on Windows. Do not name a browser with `open -a`.
2. Reply with one line on what the page holds and its path or URL. For a review page, also say what the user needs to decide and that Submit sends the answers back.
3. Collect the answers:
   - If the harness can run a background command and notify you when it exits, run `uv run <skill-dir>/scripts/serve.py wait "$dir" --timeout 3600` in the background and end your turn. It exits 0 and prints the state when the user clicks Submit.
   - Otherwise end your turn. When the user says they are done, read `$dir/state.json`; the page saves every change within a second, Submit or not.
   - If `wait` exits 5 (timeout), read `state.json` for partial answers and ask in chat about the rest.

### Step 8: Act on the answers

`state.json` looks like this:

```json
{
  "answers": {
    "zod-plan": { "value": "all-at-once", "label": "All at once" },
    "zod-plan:note": { "value": "Merge it next week" },
    "extra": { "value": ["licenses"], "label": ["Licenses"] }
  },
  "unanswered": ["moment"],
  "submitted": true,
  "submittedAt": "2026-10-16T09:12:03.000Z",
  "updated": "2026-10-16T09:12:03+00:00"
}
```

Act on `value` and quote `label` when confirming back to the user. Summarize the decisions in one to three lines before acting, and ask in chat only about the items in `unanswered`. When the review is finished, stop the server with `uv run <skill-dir>/scripts/serve.py stop "$dir"` and keep the directory.

To change a served page, edit `index.html` in place: open tabs reload within two seconds and keep their answers and scroll position. For a new round of questions, create a new directory, because `wait` returns at once when `state.json` already says `submitted`.

## Failure Handling

| Symptom                                                            | Action                                                                                                                                                                                                                             |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `serve.py start` exits 4                                           | Read `$dir/.server.log`. If no Python 3.11+ runs, deliver the page as a file; answers then stay in the browser and the user sends them with Copy answers.                                                                          |
| `serve.py` exits 3                                                 | The directory does not exist. Run Step 2 first.                                                                                                                                                                                    |
| The page says it is offline, or `state.json` is missing at the end | The server stopped (it exits after 4 hours without requests). Run `serve.py start "$dir"` again; it takes the previous port when that port is free. Ask the user to reload, and the page sends the answers it kept in the browser. |
| Fonts look like the system default in the screenshot               | A family name does not match the installed font. Check it with `fc-list : family \| rg -i "<name>"` and fix the stack.                                                                                                             |

## Gotchas

- A page opened from `file://` cannot write files, which is why review pages need `serve.py`. On `file://` the template keeps answers in the browser and offers Copy answers as the last resort.
- A typed space between CJK text and a number is a line-break point: a Japanese heading once broke as "3 / 個". In short headings, join a trailing number and its counter with `&nbsp;` (`3&nbsp;個`).
- Fonts follow the `lang` attribute. Japanese quoted inside a Chinese report needs an element with `lang="ja"`, or its kanji render in Chinese glyph shapes.
- Submit with unanswered required items first highlights them. A second click submits anyway and records them in `unanswered`.
- macOS `$TMPDIR` lives under `/var/folders`, and the system purges files there after a few days without access. When a tmp report looks worth keeping, offer to copy it to `~/Downloads`.

## Output Contract

1. The final page path (the `~/Downloads` or docs copy when one was made), the URL when served, opened in the default browser.
2. One chat line on what the page holds and, for a review page, what the user must decide.
3. After a review: the decisions read from `state.json`, the unanswered items, and the server stopped.

## References

- [references/writing.md](references/writing.md): prose and structure rules for every page; read in Step 3.
- [references/writing-zh.md](references/writing-zh.md): Simplified Chinese register, terms, spacing, and punctuation; read when `lang="zh-CN"`.
- [references/writing-ja.md](references/writing-ja.md): Japanese register, terms, spacing, and punctuation; read when `lang="ja"`.
- [references/components.md](references/components.md): which component fits which content, markup snippets, and the read-through checklist for Step 6.
- [references/typography.md](references/typography.md): font stacks, sizes, colors, and adding a language; read only when changing them.
- `scripts/serve.py --help`: commands, HTTP API, and exit codes of the local server.
