# Writing Rules

Use these rules for every heading, sentence, table cell, option label, and hint in a report or review page. They adapt George Orwell's six rules from "Politics and the English Language" to reports read on screen, in any language.

Contents:

- [Orwell's rules, applied](#orwells-rules-applied)
- [Structure](#structure)
- [Numbers and evidence](#numbers-and-evidence)
- [Chinese, Japanese, and Korean](#chinese-japanese-and-korean)
- [Translated quotes](#translated-quotes)
- [Option and question text](#option-and-question-text)
- [Final pass](#final-pass)

## Orwell's rules, applied

1. **No stock phrases or decorative metaphors.** Cut "a game changer", "the tip of the iceberg", "赋能", "抓手", "闭环", "底层逻辑". Say the plain fact instead.
2. **Short words over long ones.** "use", not "utilize"; "用", not "进行使用"; "使う", not "使用する" when either fits.
3. **Cut every word you can.** Delete "basically", "it is worth noting that", "需要注意的是", "值得一提的是", "～と言えるでしょう". If a sentence still says the same thing without a word, the word goes.
4. **Active voice.** "The cache drops 30% of requests", not "30% of requests are dropped". In Chinese, avoid 被 sentences unless the doer is unknown.
5. **Plain words over jargon.** Write "the page loads in 2 seconds", not "TTI is 2s", unless the reader works with that term daily. When a field term has no plain replacement, keep it and explain it once, in one clause, the first time it appears.
6. **Break any rule above rather than write something unclear.** Clarity wins over rule-following.

Two more rules from the user this skill serves:

- **Do not over-explain.** The reader is technical. Skip definitions of common terms and do not restate a table in prose.
- **One idea per sentence.** If a sentence needs a semicolon or a second "but", split it.

## Structure

- **Title states the finding, in one line.** "3 of 12 dependencies can be removed now", not "Dependency analysis report". Keep it to about 10 English words or 20 CJK characters: a longer title wraps, and in Chinese the balanced wrap can split a word ("上线｜后"). Put the cause and scope in the meta line; the kicker line above the title carries the category and date.
- **Summary first.** 2–5 points, each a full sentence with the number or decision in it. A reader who stops after the summary must know what happened and what to do.
- **Headings state the point of their section**, not its topic: "Upgrade zod 4 separately", not "About zod".
- **Short paragraphs.** Three to four sentences at most. Put detail, logs, and raw output in `<details>`.
- **Recommendation before alternatives.** When options are compared, say which one you recommend and why, then show the others.
- **Say what you do not know.** Mark guesses as guesses once, at the claim, in plain words: "likely", "not verified", "not measured".

## Numbers and evidence

- Give every number a unit and a comparison point: "180 KB smaller (from 1.2 MB to 1.02 MB)".
- Round to what matters: "about 40%" rather than "39.87%" unless precision is the point.
- Name the source of each fact the reader might doubt: a command, a file path, a link.
- Use digits for numbers in all languages.

## Chinese, Japanese, and Korean

- Do not type spaces between CJK characters and Latin letters or digits in Chinese or Japanese; the template adds the gap. Korean keeps its normal word spaces.
- Use full-width punctuation in CJK sentences: `，。：；？！（）`, with `“”` for Simplified Chinese quotes and `「」` for Japanese and Traditional Chinese. Keep half-width punctuation inside code, paths, and English quotes.
- **Chinese**: avoid 翻译腔. Cut "进行" before verbs ("进行优化" → "优化"), strings of "的", and "对……进行……". Avoid stacks of four-character phrases. Prefer "可以删除" over "具备删除的可行性".
- **Japanese**: use です・ます throughout a page; do not mix in だ・である. Prefer a common Japanese word over a rare katakana loanword (要件, not リクワイアメント); everyday loanwords such as チェック are fine.
- **Korean**: use 합니다체 throughout. Keep Korean particles attached to the word they follow, including after Latin words ("PR로", "API를").

## Translated quotes

When a source is in a language other than the page language (English docs, a Japanese spec, an issue comment):

- Show the translation first, in the page language, then the original in a `.pair` block with the correct `lang` attribute. See components.md.
- Translate meaning, not word order. Keep identifiers, commands, and product names untranslated.
- Never leave a decision-relevant passage untranslated: the user must be able to decide from the translation alone.

## Option and question text

- A question is one sentence that ends with a question mark and names the decision: "How should we upgrade zod?"
- An option label is 2–8 words naming the choice. The description below it states the cost or consequence in one short line.
- The hint under a question says what the answer affects, not how to click.
- Labels never show internal IDs, enum values, or file-safe slugs. Those go in `name` and `value`.

## Final pass

Before Step 6 of the workflow, reread the page once and check:

- [ ] The title and summary alone tell the reader the result.
- [ ] No sentence has more than one idea.
- [ ] No word from Rule 1 or Rule 3 survives.
- [ ] Every number has a unit and a comparison point.
- [ ] Every foreign-language quote has a translation before it.
- [ ] Every option label is in the page language.
