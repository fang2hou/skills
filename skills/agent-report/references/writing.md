# Report Prose

Language quality — register, technical terms, sentence shape, and the spacing and punctuation conventions of `en`, `zh-CN`, and `ja` — comes from the **natural-writing** skill in this repository. This file adds only what a report page adds to prose; do not restate natural-writing's rules here or in the page.

Apply this file and natural-writing to every heading, sentence, table cell, option label, and hint.

## When writing (Step 3)

Draft through natural-writing: load it before you write, tell it the genre (`technical-doc` for most reports), the page language, and the audience (a senior engineer who reads technical English). Its `generate` mode shapes the draft, `rewrite` fixes a rough one. On top of it, a report page asks for:

**Structure**

- **The title states the finding in one line.** "3 of 12 dependencies can be removed now", not "Dependency analysis report". Keep it to about 10 English words or 20 CJK characters; a longer title wraps, and the balanced wrap can split a word. Put the cause and scope in `.meta` and the category and date in `.kicker`.
- **Summary first.** 2–5 points, each one or two short sentences (about 40 English words or 80 CJK characters) carrying its number or decision. A reader who stops after the summary must know what happened and what to do.
- **Title, summary, and sections agree.** The same counts and the same claims everywhere. If a section changes a conclusion while you write it, update the title and summary to match.
- **Headings state the section's point**, not its topic: "Upgrade zod 4 separately", not "About zod".
- **Short paragraphs** of three or four sentences at most. Three or more parallel findings go in a list or table, not in one paragraph. Put logs and raw output in `details` blocks.
- **Show structure once.** A branching process or parts that depend on each other get an inline SVG diagram; records with the same fields get a table. Do not follow a table with prose or a list that restates its rows; add a column for the reason instead.
- **Recommendation before alternatives.** Say which option you recommend and why, then show the others.
- **Mark guesses once, at the claim**: "likely", "not verified", "not measured".

**Numbers, quotes, and review text**

- **Numbers.** Use digits in every language. Give each number a unit and a point of comparison ("180 KB smaller, from 1.2 MB to 1.02 MB"), round to what matters, and name the source of any fact the reader might doubt: a command, a path, or a link.
- **Translated quotes.** In a `pair` block, the translation comes first in the page language, then the original with its `origLang`. Translate the meaning, not the word order, and leave identifiers and commands as they are. Never leave a passage the user must decide on untranslated.
- **Questions and options.** A question is one sentence that names the decision and ends with a question mark. An option label is 2–8 words naming the choice, never an internal ID or slug. The `desc` line under it states the cost, and the `hint` under a question says what the answer affects.

## When reviewing (Step 6, once)

Run exactly one prose review before the page goes to the user: natural-writing `review` mode over the page's text — title, summary, headings, paragraphs, table cells, option labels — in the page language. Fix what it flags together with the report-specific checks:

- [ ] The title and summary alone give the conclusion and the key numbers, and they agree with the sections.
- [ ] Every count matches the items it counts: recount each group against its list, and check that no item sits in two groups meant to exclude each other.
- [ ] No paragraph or list restates a table or figure, and no sentence cites a label the reader has not seen.
- [ ] Paths, commands, and identifiers are in `<code>`; proposed replacement text is in a `details` block or a table.
- [ ] Every foreign-language quote has a translation above it, and every option label is in the page language.

There is no second review round; what this pass approves is what the user reads.
