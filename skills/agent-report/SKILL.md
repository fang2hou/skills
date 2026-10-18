---
name: agent-report
description: >
  Default output for any answer with several findings: a desktop HTML report or review
  page. Use unasked when told to investigate, summarize recent work or commits, compare,
  audit, or explain a system, or when the user must decide several questions.
license: MIT
compatibility: Requires file write access and a browser. Building a page needs Node 24 + pnpm (the skill clones the renderer); review pages run the kit’s zero-dependency Node server (`tools/serve.ts`) on 127.0.0.1 — no extra runtime beyond Node.
metadata:
  author: fang2hou
  version: "2.2"
---

# Agent Report

Turns findings into one calm HTML page for reading on a desktop screen, and turns decisions the user must make into a review page whose answers land in `state.json` for the agent to read.

The page is data-driven: you write `report.json`, and the renderer
([fang2hou/agent-report-kit](https://github.com/fang2hou/agent-report-kit), cloned by Step 2) compiles
it into a single self-contained `index.html`. You never write HTML, CSS, or JS for a page —
content and chrome stay separated, and every page gets the same theme, fonts, and review
machinery.

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

Instructions the user gives in the current conversation (language, layout, colors, file location) override these rules and the renderer defaults.

1. **One self-contained file, compiled by the renderer.** Every page comes out of `node tools/build.ts` in the cloned agent-report-kit repo, which validates `report.json`, compiles, and injects the data in one step. No CDN scripts, web fonts, or remote images, because the page must open offline and stay small. The page is read on a desktop monitor; do not add mobile layouts or test phone widths.
2. **Conclusion first.** The first screen holds a title that states the main finding and a summary box with 2–5 points. The reader decides from these whether to read on.
3. **Prose through natural-writing.** Language quality — register, technical terms, sentence shape, CJK spacing — belongs to the `natural-writing` skill in this repository. Load it when drafting (Step 3) and review with it exactly once before hand-over (Step 6). [references/writing.md](references/writing.md) adds only the report-specific rules: structure, numbers, translated quotes, and question wording.
4. **The reader's language.** Set the report's `lang` field to the language the user names, or else the language of their latest message (`zh-CN`, `ja`, `en`). Fonts, line breaking, and every UI string follow it. Never default to the language of the sources, the repository, or these instructions. A quote in another language goes in a `pair` block with the translation first, because the user decides from the translation and the agent acts on the original.
5. **Answers come back through a file.** Review pages run the kit's server (`$kit/tools/serve.ts`), and the agent reads `state.json`. Ask the user to copy and paste answers only when the server cannot run. The handed-over artifact carries no server UI: on a page opened as a file the renderer hides the top-left connection chip and the chat channel entirely — verify that once in Step 6 before delivering.
6. **Budgets live in the kit.** The renderer sets the size and media budgets (inline-SVG figure rules, raster-image limits) — they are documented in `$kit/docs/report-schema.md` next to the schema that enforces them. Check what the compile step prints against that budget; a page that cannot stay inside it is carrying content that belongs in a linked file, not in the page.
7. **The renderer owns the look.** Theme, components, default buttons, and chrome strings are the kit's code, documented in `$kit/docs/components.md` and `$kit/docs/typography.md` — changing them means changing agent-report-kit, never the page. Do not fight the renderer with custom markup: if the content does not fit a component, the content shape is wrong. Style or component work in agent-report-kit requires no change here.
8. **Verify before handing over.** Build and render the page, and fix what you see (Step 6).

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
- Live reports and review pages run `serve.ts` (Step 5); a plain report opens as a file. A report that ends with questions is a review page.

### Step 2: Create the working directory and fetch the renderer

```bash
base="${TMPDIR:-/tmp}"; dir="${base%/}/agent-report/$(date +%Y%m%d-%H%M)-<short-slug>"
mkdir -p "$dir"
kit="$HOME/.local/share/agent-report-kit"   # one clone, reused by every report
if [ -d "$kit/.git" ]; then git -C "$kit" pull --ff-only -q && pnpm -C "$kit" install --silent; else
  git clone --depth 1 https://github.com/fang2hou/agent-report-kit "$kit" && pnpm -C "$kit" install --silent
fi
```

Pull and `pnpm install` are cheap; a fresh clone takes one round of installs. One report directory holds `report.json`, the compiled `index.html`, and one round of questions. After Step 6, copy a page bound for `~/Downloads` to `~/Downloads/<YYYYMMDD>-<short-slug>.html`, or a docs page to the path the user named. Never overwrite an existing file there.

### Step 3: Write report.json

1. Read `$kit/docs/report-schema.md` — the authoring contract for every field — and `$kit/docs/components.md` for which component fits which content shape. Both live in the cloned renderer repo, next to the schema that enforces them. Then load the `natural-writing` skill for the page language and [references/writing.md](references/writing.md), and draft through natural-writing (`generate` mode, genre `technical-doc`, audience a senior engineer who reads technical English).
2. Outline in the order Step 1 gives: a title that states the main finding, 2–5 summary points, and section headings that each state their section's point.
3. Write `$dir/report.json` with `lang` set per Hard Rule 4. Rich-text fields take the trusted subset listed in the kit's report-schema.md (`<strong>`, `<code>`, chips, `<time>`); everything else is plain data.
4. Pick one block per idea from the "Choose by content shape" table in `$kit/docs/components.md`. Use a `table` block where items share fields, a `figures` row when two to four numbers carry the finding, `bars` for one measure across items, `compare` cards for options weighed against each other. Leave the rest as short `p` blocks. With five or more sections the table of contents appears on its own.
5. Structured diagrams (flows, lifecycles, dependencies, file trees): hand-write them as inline SVG in a `figure` block, following the figure rules in `$kit/docs/report-schema.md` — `viewBox` for scaling, `currentColor` plus CSS variables for strokes, direct labels over legends, and text at 14 px or larger.

### Step 4: Add review questions (review pages only)

Write the `review.questions` array per report-schema.md. For each question:

- Give every question and option a stable ASCII `id`/`value` (`zod-plan`, `all-at-once`) and a visible label in the page language. Never show an ID as the label.
- Use `choice` for one answer (`multiple` for several), `verdict` for a decision per item with tone-colored pills, and `text` for free answers; `note: true` adds an optional comment field.
- Put the recommended option first with `badge: "推荐"` on a compare card, or first in `options` with its cost in `desc`.
- In a verdict list of more than 10 items, name the pre-selected recommendation in the hint, so the user changes only the exceptions.
- Ask only what changes the next action. Keep a page to 10 questions or fewer, counting a verdict list as one question, and split larger reviews into rounds.
- Do not ask a question that applies only after a certain answer to another question on the same page ("If you chose Merge, how?"). Ask it in the next round, once the first answer is known.

### Step 5: Compile and serve

```bash
node "$kit/tools/build.ts" "$dir/report.json" "$dir/index.html"
# OK: <dir>/index.html (NNNNN bytes)   — INVALID lines name the field to fix
node "$kit/tools/serve.ts" start "$dir"
# prints {"url": "http://127.0.0.1:PORT/", "dir": ..., "pid": ..., "state": ".../state.json"}
```

The compile step validates the JSON against the schema, builds the renderer, and injects the data in one command. Plain reports stop after it. `start` reuses a running server for the same directory. To change a served page, edit `report.json`, re-run the build command, and open tabs reload within two seconds keeping answers and scroll position.

### Step 6: Verify

Verify before the user opens the page, so test answers never reach them.

1. Check the size the compile step printed against the 1 MB budget.
2. Load the page at 1280 px wide with a browser tool, or take a headless screenshot: `"<chrome-binary>" --headless --screenshot=/tmp/check.png --window-size=1280,2400 "<url-or-file-url>"`. Check the screenshot, the console for errors, and that `document.documentElement.scrollWidth` does not exceed `clientWidth`. Confirm the UI chrome (summary heading, submit button) is in `lang`. Chrome here is only for checking; Step 7 opens the page for the user.
3. On a review page, click one option and confirm `state.json` changed. Then close that tab and delete `state.json`.
4. Open the compiled file itself as `file://` once: the top-left connection chip and the whole chat channel must not appear — the artifact the user keeps is server-free. If any server UI shows, the renderer is broken; report it rather than patching the page.
5. If no browser runs at all, walk the report JSON against the read-through checklist at the end of `$kit/docs/components.md`, and say in the hand-over that the page was checked by reading only.
6. Run the single prose review: `natural-writing` in `review` mode over the page text in the page language, plus the report checklist at the end of [references/writing.md](references/writing.md). Fix what it flags, rebuild, and hand over — there is no second review round.

### Step 7: Open, hand over, and collect answers

1. Open the URL, or the file path for a plain report (the `~/Downloads` or docs copy when one was made), in the user's default browser: `open "<url-or-file>"` on macOS, `xdg-open` on Linux, `start "" "<url-or-file>"` on Windows. Do not name a browser with `open -a`.
2. Reply with one line on what the page holds and its path or URL. For a review page, also say what the user needs to decide and that Submit sends the answers back.
3. Collect the answers:
   - If the harness can run a background command and notify you when it exits, run `node "$kit/tools/serve.ts" wait "$dir" --timeout 3600` in the background and end your turn. It exits 0 and prints the state when the user clicks Submit.
   - Selection questions: the served page shows the connection chip top left; the user can select any text and send a question. Watch for them with `node "$kit/tools/serve.ts" chat "$dir" --wait 3600` in the background — one JSON line per question: `{"id", "quote", "text"}`. Poll `chat` without `--wait` when the user mentions a question.
   - Answer with `node "$kit/tools/serve.ts" reply "$dir" <id> "<answer>"`; the id may be the question or any follow-up in its thread. The page underlines the quoted text and shows the answer on hover. Track the last id you answered and pass `--since` on the next watch.
   - Discussions survive reloads and your page edits: the page rebuilds them from `chat.json`, and the connection chip opens the list, so editing the page mid-discussion is safe.
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

Act on `value` and quote `label` when confirming back to the user. Summarize the decisions in one to three lines before acting, and ask in chat only about the items in `unanswered`. When the review is finished, stop the server with `node "$kit/tools/serve.ts" stop "$dir"` and keep the directory.

For a new round of questions, create a new directory, because `wait` returns at once when `state.json` already says `submitted`.

## Failure Handling

| Symptom                                                            | Action                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `build.ts` prints `INVALID`                                        | The line names the JSON field; fix `report.json` and re-run. The field reference is `$kit/docs/report-schema.md` in the cloned renderer.                                                                                                                            |
| `git clone` or `pnpm install` fails (no Node 24 / no pnpm)         | Install Node 24 and pnpm (mise or corepack), or retry on a machine that has them; the renderer cannot compile without them.                                                                                                                                         |
| 页面左上显示"未连接"，划词没有提问气泡                             | The page was served over http but the server stopped. Start it again with `serve.ts start "$dir"` and reload. Opened as a `file://` artifact there is no chip at all (by design), answers stay in the browser with Copy answers, and selection chat is unavailable. |
| `serve.ts reply` exits 6                                           | The question id does not exist in `$dir/chat.json`. Run `serve.ts chat "$dir"` to list questions, then reply to one of those ids.                                                                                                                                   |
| `serve.ts start` exits 4                                           | Read `$dir/.server.log` (usually a busy port — pass `--port`). If the server cannot run at all, deliver the page as a file; answers then stay in the browser and the user sends them with Copy answers.                                                             |
| `serve.ts` exits 3                                                 | The directory does not exist. Run Step 2 first.                                                                                                                                                                                                                     |
| The page says it is offline, or `state.json` is missing at the end | The server stopped (it exits after 4 hours without requests). Run `serve.ts start "$dir"` again; it takes the previous port when that port is free. Ask the user to reload, and the page sends the answers it kept in the browser.                                  |
| Fonts look like the system default in the screenshot               | The renderer's font stacks expect locally installed families; check with `fc-list : family \| rg -i "<name>"`. A missing family falls back — see `$kit/docs/typography.md`.                                                                                         |

## Gotchas

- A page opened from `file://` cannot write files, which is why review pages need `serve.ts`. On `file://` the page keeps answers in the browser and offers Copy answers as the last resort.
- A typed space between CJK text and a number is a line-break point: a Japanese heading once broke as "3 / 個". In short headings, join a trailing number and its counter with `&nbsp;` (`3&nbsp;個`) — rich-text fields accept it.
- Fonts follow the `lang` field. Japanese quoted inside a Chinese report needs the `pair` block with `origLang: "ja"`, or its kanji render in Chinese glyph shapes.
- Submit with unanswered required items first highlights them. A second click submits anyway and records them in `unanswered`.
- macOS `$TMPDIR` lives under `/var/folders`, and the system purges files there after a few days without access. When a tmp report looks worth keeping, offer to copy it to `~/Downloads`.

## Output Contract

1. The final page path (the `~/Downloads` or docs copy when one was made), the URL when served, opened in the default browser.
2. One chat line on what the page holds and, for a review page, what the user must decide.
3. After a review: the decisions read from `state.json`, the unanswered items, and the server stopped.

## References

- The cloned renderer repo (`$kit`) owns the template content: `docs/report-schema.md` (authoring contract), `docs/components.md` (content shapes, visual contract, read-through checklist), `docs/typography.md` (fonts and color tokens), and `tools/serve.ts --help` (commands, HTTP API, exit codes). This skill deliberately carries none of it — changing the look, a component, or the server means changing agent-report-kit, not this file.
- The `natural-writing` skill (same repository): register, terms, and sentence shape per language (`en`, `zh-CN`, `ja`); loaded in Step 3 and reviewed with in Step 6.
- [references/writing.md](references/writing.md): the report-specific prose rules — structure, numbers, quotes, questions — on top of natural-writing; read in Step 3.
