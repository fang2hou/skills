# Writing Rules

Apply these rules to every heading, sentence, table cell, option label, and hint in a report or review page. For a Chinese page (`zh-CN`), also follow [writing-zh.md](writing-zh.md); for a Japanese page (`ja`), also follow [writing-ja.md](writing-ja.md).

## Prose

1. **Formal register, plain words.** Cut buzzwords such as "game changer" and "leverage synergies", and stock idioms such as "round out the picture" or "half out of the door"; state the fact instead. Do not drop into chat shorthand either. Write "the service crashed during an unattended late-night release", not "it blew up during the late-night push with nobody watching".
2. **Keep established technical terms.** The reader is a senior engineer who reads technical English. Use the field's term instead of an everyday paraphrase or a word-for-word translation of an English metaphor, and do not define common terms. Study material for beginners is the exception: define each new term once, where it first appears.
3. **Verbs, not nominalizations.** Write "use", not "utilize"; "rebuilding the index cut query latency from 120 ms to 15 ms", not "an optimization of the index achieved a reduction in latency".
4. **Cut filler and use the active voice.** Delete "basically", "it is worth noting that", and "it should be mentioned that". Write "the cache absorbs 30% of requests", not "30% of requests are absorbed by the cache", unless the actor is unknown.
5. **One idea per sentence.** If a sentence needs a semicolon, a second "but", or a pair of dashes around an aside, split it. Join clauses with a comma, colon, or parentheses rather than an em dash (`—`) or Chinese `——`.
6. **Name things the reader can see.** Do not cite labels the reader has never seen, such as a rubric's "Dimension 2", a rule number like "AP-35", or a check called "Check C". Say what the label checks: "the description-quality score", "the rule that both skills name each other".
7. **Mark code as code.** Put paths, file names, commands, config keys, field names, and identifiers in `<code>`. Put proposed replacement text, such as a rewritten description or a config line, in its own `<pre>` block or a before-and-after table, never inline in a sentence.

## Structure

- **The title states the finding in one line.** "3 of 12 dependencies can be removed now", not "Dependency analysis report". Keep it to about 10 English words or 20 CJK characters; a longer title wraps, and the balanced wrap can split a word. Put the cause and scope in `.meta` and the category and date in `.kicker`.
- **Summary first.** 2–5 points, each one or two short sentences (about 40 English words or 80 CJK characters) carrying its number or decision. A reader who stops after the summary must know what happened and what to do.
- **Title, summary, and sections agree.** The same counts and the same claims everywhere. If a section changes a conclusion while you write it, update the title and summary to match.
- **Headings state the section's point**, not its topic: "Upgrade zod 4 separately", not "About zod".
- **Short paragraphs** of three or four sentences at most. Three or more parallel findings go in a list or table, not in one paragraph. Put logs and raw output in `<details>`.
- **Show structure once.** A branching process or parts that depend on each other get an inline SVG diagram; records with the same fields get a table. Do not follow a table with prose or a list that restates its rows; add a column for the reason instead.
- **Recommendation before alternatives.** Say which option you recommend and why, then show the others.
- **Mark guesses once, at the claim**: "likely", "not verified", "not measured".

## Numbers, quotes, and review text

- **Numbers.** Use digits in every language. Give each number a unit and a point of comparison ("180 KB smaller, from 1.2 MB to 1.02 MB"), round to what matters, and name the source of any fact the reader might doubt: a command, a path, or a link.
- **Translated quotes.** In a `.pair` block, the translation comes first in the page language, then the original with its `lang` attribute. Translate the meaning, not the word order, and leave identifiers and commands as they are. Never leave a passage the user must decide on untranslated.
- **Questions and options.** A question is one sentence that names the decision and ends with a question mark. An option label is 2–8 words naming the choice, never an internal ID or slug. The `.d` line under it states the cost, and the `.hint` under a question says what the answer affects.

## Final pass

Reread the page once before Step 6 and fix what is unclear or wrong:

- [ ] The title and summary alone give the conclusion and the key numbers, and they agree with the sections.
- [ ] Every count matches the items it counts: recount each group against its list, and check that no item sits in two groups meant to exclude each other.
- [ ] No paragraph or list restates a table or figure, and no sentence cites a label the reader has not seen.
- [ ] Paths, commands, and identifiers are in `<code>`; proposed replacement text is in `<pre>` or a table.
- [ ] The register is formal throughout, with accurate terms and no chat slang, word-for-word calques, or needless definitions.
- [ ] A `zh-CN` or `ja` page follows its language guide, including the space between CJK text and Latin letters or digits.
- [ ] Every foreign-language quote has a translation above it, and every option label is in the page language.
