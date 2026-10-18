---
name: agent-report
description: >
  Default output for any answer with several findings: a desktop HTML report or review
  page. Use unasked when told to investigate, summarize recent work or commits, compare,
  audit, or explain a system, or when the user must decide several questions.
license: MIT
compatibility: Requires file write access and a browser. Requires Node 24 + pnpm for the kit. Interactive reports run one local SvelteKit Node service on 127.0.0.1; the agent must keep polling during collection. PDF export additionally requires Chrome/Chromium. Background subagents are optional.
metadata:
  author: fang2hou
  version: "2.3"
---

# Agent Report

Turns findings into one calm HTML page for reading on a desktop screen, and turns decisions the user must make into a review page whose answers land in `state.json` for the agent to read.

The page is data-driven: you write `report.json`, and the renderer
([fang2hou/agent-report-kit](https://github.com/fang2hou/agent-report-kit), cloned by Step 2) compiles
it into a local interactive report or exports a self-contained `index.html` / PDF. You never write HTML, CSS, or JS for a page —
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

1. **Use the kit for every output.** Local reports run the kit’s SvelteKit service; HTML and PDF are explicit exports from the same JSON and components. An HTML export inlines its assets and works offline. No CDN scripts, web fonts, or remote images. The page is read on a desktop monitor; do not add mobile layouts or test phone widths.
2. **Conclusion first.** The first screen holds a title that states the main finding and a summary box with 2–5 points. The reader decides from these whether to read on.
3. **Prose through natural-writing.** Language quality — register, technical terms, sentence shape, CJK spacing — belongs to the `natural-writing` skill in this repository. Load it when drafting (Step 3) and review with it exactly once before hand-over (Step 6). [references/writing.md](references/writing.md) adds only the report-specific rules: structure, numbers, translated quotes, and question wording.
4. **The reader's language.** Set the report's `lang` field to the language the user names, or else the language of their latest message (`zh-CN`, `ja`, `en`). Fonts, line breaking, and every UI string follow it. Never default to the language of the sources, the repository, or these instructions. A quote in another language goes in a `pair` block with the translation first, because the user decides from the translation and the agent acts on the original.
5. **Answers come back through a file.** Review pages run the kit's server (`$kit/tools/serve.ts`), and the agent reads `state.json`. Ask the user to copy and paste answers only when the server cannot run. Exported HTML carries no server UI or requests, even when hosted over HTTP. Verify the export once in Step 6 before delivering.
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
- Default to a temporary local website for a complex decision or ongoing discussion. Use an HTML or PDF export when the user wants a file to keep or share. A report that ends with questions is a review page.

### Step 2: Create the working directory and fetch the renderer

```bash
base="${TMPDIR:-/tmp}"
dir="${base%/}/agent-report/$(date +%Y%m%d-%H%M%S)-<short-slug>"
mkdir -p "$dir"
kit="$HOME/.local/share/agent-report-kit"
```

Use a kit checkout supplied by the user when present. Otherwise clone
`https://github.com/fang2hou/agent-report-kit` into `$kit` and run
`pnpm -C "$kit" install --frozen-lockfile`. Reuse a compatible existing checkout;
inspect its status and revision before updating. Do not pull a checkout with
local changes or update it while another report is being built. Record the kit
revision so a report can be reproduced. The kit serializes its CLI builds.

One directory holds `report.json`, session state, and one round of questions.
Keep state after closing the service. Copy requested share files to Downloads
or the user’s named path without overwriting an existing file.

### Step 3: Write report.json

1. Read `$kit/docs/report-schema.md` — the authoring contract for every field — and `$kit/docs/components.md` for which component fits which content shape. Both live in the cloned renderer repo, next to the schema that enforces them. Then load the `natural-writing` skill for the page language and [references/writing.md](references/writing.md), and draft through natural-writing (`generate` mode, genre `technical-doc`, audience matching the reader and the report language).
2. Outline in the order Step 1 gives: a title that states the main finding, 2–5 summary points, and section headings that each state their section's point.
3. Write `$dir/report.json` with `lang` set per Hard Rule 4. Rich-text fields take the trusted subset listed in the kit's report-schema.md (`<strong>`, `<code>`, chips, `<time>`); everything else is plain data.
4. Pick one block per idea from the "Choose by content shape" table in `$kit/docs/components.md`. Use a `table` block where items share fields, a `figures` row when two to four numbers carry the finding, `bars` for one measure across items, `compare` cards for options weighed against each other. Leave the rest as short `p` blocks. The kit supplies the TOC for every section, the review area, and every question, including short reports. Do not add a manual TOC block or alter the renderer to compensate for a missing one; verify those targets in Step 6.
5. Structured diagrams (flows, lifecycles, dependencies, file trees): hand-write them as inline SVG in a `figure` block, following the figure rules in `$kit/docs/report-schema.md` — `viewBox` for scaling, `currentColor` plus CSS variables for strokes, direct labels over legends, and text at 14 px or larger.

### Step 4: Add review questions (review pages only)

Write the `review.questions` array per report-schema.md. For each question:

- Give every question and option a stable ASCII `id`/`value` (`zod-plan`, `all-at-once`) and a visible label in the page language. Never show an ID as the label.
- Use `choice` for one answer (`multiple` for several), `verdict` for a decision per item with tone-colored pills, and `text` for free answers; `note: true` adds an optional comment field.
- Put the recommended option first with `badge: "推荐"` on a compare card, or first in `options` with its cost in `desc`.
- In a verdict list of more than 10 items, name the pre-selected recommendation in the hint, so the user changes only the exceptions.
- Ask only what changes the next action. Keep a page to 10 questions or fewer, counting a verdict list as one question, and split larger reviews into rounds.
- Do not ask a question that applies only after a certain answer to another question on the same page ("If you chose Merge, how?"). Ask it in the next round, once the first answer is known.

### Step 5: Start locally or export

For local reading and discussion, only `report.json` is needed:

```bash
pnpm -C "$kit" report:start "$dir"
# JSON: url, pid, state, ownerPid (when detected), leaseSeconds
```

Normally omit `--owner-pid`: the CLI searches for a stable harness ancestor. Do not pass `$$` from a tool command; that is usually a temporary shell that exits as soon as the command returns. Supply a PID only after verifying it belongs to the long-lived agent process.

The kit validates and reads JSON in its SvelteKit app. Reuse the same session
when editing content; saving `report.json` reloads the page and preserves its
answers and discussion. Do not rebuild an HTML export for each local edit.

For shareable files:

```bash
pnpm -C "$kit" export:html "$dir/report.json" "$dir/index.html"
pnpm -C "$kit" export:pdf "$dir/report.json" "$dir/report.pdf"
```

These are separate commands: generate only the requested format. HTML stays
interactive for offline reading, with local form drafts but no service or chat.
PDF preserves the report and questions in a print layout; details are expanded.
If Chrome is not found, set `CHROME_BIN` to an installed Chrome/Chromium binary,
or offer browser Print → Save as PDF. Do not claim a PDF exists until verified.

### Step 6: Verify

Verify before the user opens the page, so test answers never reach them.

1. Check an HTML export against the size budget in the kit’s schema guide. For a PDF, render pages and inspect page breaks, wide tables, and the last page for missing content.
2. Load the page at 1280 px wide with a browser tool, or take a headless screenshot: `"<chrome-binary>" --headless --screenshot=/tmp/check.png --window-size=1280,2400 "<url-or-file-url>"`. Check the screenshot, the console for errors, and that `document.documentElement.scrollWidth` does not exceed `clientWidth`. Confirm the UI chrome (summary heading, submit button) is in `lang`. Chrome here is only for checking; Step 7 opens the page for the user.
3. Exercise review autosave, Submit, a text-selection question, and a follow-up in a separate scratch session. Poll its events, post a reply, and confirm it appears in the browser. Stop that scratch session. Do not write test responses into the real review or delete state while a service is running.
4. Check TOC links at the actual desktop/panel width: every section, the review area, and each question must jump to a unique target. For HTML exports, verify both `file://` and ordinary static HTTP hosting: no connection chip, chat, or `/api/*` requests. Report renderer defects rather than patching the generated file.
5. If no browser runs at all, walk the report JSON against the read-through checklist at the end of `$kit/docs/components.md`, and say in the hand-over that the page was checked by reading only.
6. Run the single prose review: `natural-writing` in `review` mode over the page text in the page language, plus the report checklist at the end of [references/writing.md](references/writing.md). Fix what it flags, rebuild, and hand over — there is no second review round.

### Step 7: Open, hand over, and collect answers

1. Open the URL, or the file path for a plain report (the `~/Downloads` or docs copy when one was made), in the user's default browser: `open "<url-or-file>"` on macOS, `xdg-open` on Linux, `start "" "<url-or-file>"` on Windows. Do not name a browser with `open -a`.
2. Reply with one line on what the page holds and its path or URL. For a review page, also say what the user needs to decide and that Submit sends the answers back.
3. Assign one collection owner. Use a background subagent if the harness can keep it running and deliver its messages while you work. Give it the report directory, kit path, evidence/context, last acknowledged cursor, and the following job: poll at most every 5 seconds, answer explanation questions on the page, forward new decisions and modification requests to the main agent, acknowledge handled events, and stop when told the discussion is complete. The main agent owns execution and file changes.
4. If no suitable subagent exists, the **main agent performs the same loop**. Keep the turn active while awaiting webpage input; do not hand over a final response and expect a shell process to wake an inactive model. A CLI such as pi without subagent extensions uses this foreground loop. Tell the user they can now answer or ask on the page.

```bash
pnpm -C "$kit" report:poll "$dir" --wait 5
# {session,cursor,events:[{id,type,message?,state?}],state}
```

The default cursor is the last acknowledged event. An empty poll waits up to
5 seconds and renews the listener lease. Process each batch before polling
again. Form autosaves are drafts; act on decisions after `submitted: true`.
Unsent chat text is not read. A user message includes its own `message.id` and
may be a follow-up; reply to that message id, not a guessed root id:

```bash
node "$kit/tools/serve.ts" reply "$dir" <message-id> "<explanation>"
node "$kit/tools/serve.ts" ack "$dir" <batch-cursor>
```

A reply defaults to an idempotency key per incoming message; retrying it does
not add duplicates. For an intentional second reply, pass a distinct `--key`.
Acknowledge only after replying or delivering a decision to the main agent.
Unacknowledged events are returned again, including after a service restart.
Only one agent consumes/acknowledges a session; do not let the main agent and
subagent compete for its cursor.

The service expires after 60 seconds without agent polling, even when a
browser remains open. When a stable owning harness PID is detected or supplied
with `--owner-pid`, its exit also closes the service. Ordinary browser requests
do not renew the lease. `status` checks the server; the page separately shows
whether an agent polled recently. If other work will exceed the lease, keep a
collection subagent active or explicitly close and later resume the session.

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

Act on `value` and quote `label` when confirming back to the user. Summarize the decisions in one to three lines before acting, and ask in chat only about the items in `unanswered`. After handling submission and outstanding discussions, explicitly close the session with `pnpm -C "$kit" report:stop "$dir"` and verify `status` reports `running:false`. Stop it on cancellation and error paths too. Keep the report and collected data; closing removes runtime contact metadata. If the harness is killed, owner/lease cleanup is the fallback, not a substitute for this step.

For a new round of questions, create a new directory, so prior submissions and event cursors do not enter the new round.

## Failure Handling

| Symptom                                                            | Action                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `build.ts` prints `INVALID`                                        | The line names the JSON field; fix `report.json` and re-run. The field reference is `$kit/docs/report-schema.md` in the cloned renderer.                                                                                                                            |
| `git clone` or `pnpm install` fails (no Node 24 / no pnpm)         | Install Node 24 and pnpm (mise or corepack), or retry on a machine that has them; the renderer cannot compile without them.                                                                                                                                         |
| 页面左上显示"未连接"，划词没有提问气泡                             | The page was served over http but the server stopped. Start it again with `serve.ts start "$dir"` and reload. Opened as a `file://` artifact there is no chip at all (by design), answers stay in the browser with Copy answers, and selection chat is unavailable. |
| `serve.ts reply` rejects an id                                     | The question id does not exist in `$dir/chat.json`. Run `serve.ts poll "$dir"` to inspect incoming message ids, then reply to one of those ids.                                                                                                                     |
| `serve.ts start` fails                                             | Read `$dir/.server.log` (usually a busy port — pass `--port`). If the server cannot run at all, deliver the page as a file; answers then stay in the browser and the user sends them with Copy answers.                                                             |
| `serve.ts` reports a missing directory                             | The directory does not exist. Run Step 2 first.                                                                                                                                                                                                                     |
| The page says it is offline, or `state.json` is missing at the end | The agent lease expired or its owning process exited. Run `serve.ts start "$dir"` again; use `--port` if a fixed URL is needed. Open the returned URL and ask the user to reload, and the page sends the answers it kept in the browser.                            |
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
3. After a review: decisions, unanswered items, and verified session closure; state files stay available. For exports, state the generated formats and any format that could not be verified.

## References

- The cloned renderer repo (`$kit`) owns the template content: `docs/report-schema.md` (authoring contract), `docs/components.md` (content shapes, visual contract, read-through checklist), `docs/typography.md` (fonts and color tokens), and `docs/session-protocol.md` (commands, HTTP API, event delivery, and lifecycle). This skill deliberately carries none of it — changing the look, a component, or the server means changing agent-report-kit, not this file.
- The `natural-writing` skill (same repository): register, terms, and sentence shape per language (`en`, `zh-CN`, `ja`); loaded in Step 3 and reviewed with in Step 6.
- [references/writing.md](references/writing.md): the report-specific prose rules — structure, numbers, quotes, questions — on top of natural-writing; read in Step 3.
