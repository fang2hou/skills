---
name: natural-writing
description: >
  Rewrites, polishes, drafts, and reviews English, Chinese, and Japanese prose so it
  reads naturally while keeping facts, terms, and voice. Use to fix AI tone, translationese,
  stiff or slangy register, or keigo; not for code review or HTML reports.
license: MIT
compatibility: Optional validation and scan script requires Python 3.11+ (or uv). Core writing and review workflows require no external tools.
metadata:
  author: fang2hou
  version: "1.5.0"
  sources: "Orwell 1946; Strunk & White 1959; Williams 1981; Pinker 2014; Gowers 1954; Vercel 2026; Lv & Zhu 1952; Zhu Dexi 1982; Wang Li 1943; Yu Kwang-chung 1987; Honda 1976; Kinoshita 1981; Bunkacho 2007/2022; Iori 2016; Grice 1975; Brown & Levinson 1987"
---

# Natural Writing

Draft, review, diagnose, and rewrite English (`en`), Simplified Chinese (`zh-CN`), and Japanese (`ja`) prose so that meaning chooses the wording, rhetoric serves the thought, and register fits the reader.

## When to Use

- Drafting essays, technical documentation, announcements, reports, or workplace messages that must read clearly and naturally
- Editing or rewriting text that feels stiff, inflated, translationese, over-hedged, or pragmatically awkward
- Diagnosing why a passage sounds unnatural (collocation, metaphor mapping, social distance, false contrast, or nominalization) without flattening the author's voice
- Lightly polishing drafts while protecting every fact, number, technical term, causal claim, and stylistic choice that already works
- Calibrating register across languages (such as plain formal English, natural written Chinese without internet slang, or consistent Japanese `keitai` vs `jotai` without double honorifics)

## When NOT to Use

- Building interactive HTML review pages or visual dashboards (use `agent-report`)
- Reviewing source code diffs or pull request logic (use `review-and-fix`)
- Editing non-prose artifacts such as source code, configuration files, raw logs, CLI commands, or verbatim legal stipulations
- Word-for-word literal glossing where the user explicitly requests syntactic mirroring of the source language

## Hard Rules

1. **Preserve facts, scope qualifiers, and causal direction**: Keep every number, unit, date, named entity, citation, negation, temporal relation (`before` vs `while`), scope qualifier (`read-only` / `本番環境`), and epistemic hedge intact, because stylistic edits must not alter what is true or claimed.
2. **Protect technical and verbatim spans**: Keep inline code, CLI flags, file paths, URLs, version strings, direct quotations, and settled domain terminology verbatim (`idempotency`, `幂等`, `べき等性`), because replacing domain terms with everyday paraphrases or literal English calques degrades precision for technical readers.
3. **Evaluate context rather than applying a phrase ban**: Judge constructions such as `not X, but Y` (`不是……而是……`), passive voice, or metaphors like `接住` by whether the context, semantic opposition, and social relationship earn them, because every surface pattern has legitimate uses.
4. **Keep register anchored to clear written prose**: Strip bureaucratic padding and translationese without swinging into chat slang, internet memes, or rough shorthand (`绝绝子`, `狠狠拿捏`, `一把梭`, `no-brainer`, `めっちゃ`, `ヤバい`), because naturalness is clarity in the target register, not casualness.
5. **Leave working prose alone**: In `rewrite` and `light-polish` modes, keep any sentence or clause that is already clear, natural, and appropriate to its register unchanged, because gratuitous synonym swaps introduce drift and erase the author's voice.

## Inputs

| Input            | Required | Format                                                        | Default                                    |
| ---------------- | -------- | ------------------------------------------------------------- | ------------------------------------------ |
| Source text/task | Yes      | Draft text, file path, or writing prompt                      | None                                       |
| Mode             | No       | `generate`, `review`, `rewrite`, `light-polish`, `diagnose`   | `rewrite` for drafts; `generate` for specs |
| Language         | No       | `zh-CN`, `en`, `ja`                                           | Match the input text or target locale      |
| Audience & genre | No       | Genre (`technical-doc`, `public-essay`, `workplace`, etc.)    | Infer from text and state in Step 1        |
| Protected terms  | No       | List of domain terms, product names, or quotes to keep intact | All code, numbers, URLs, and settled terms |

## Operating Modes

| Mode           | Goal                                                                           | Allowed Intervention                                                      |
| -------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `generate`     | Draft original prose from a topic, outline, or notes                           | Plan structure, choose register, draft, and self-review before returning  |
| `review`       | Audit an existing text without overwriting it                                  | Identify issues, explain the underlying principle, and rate severity      |
| `rewrite`      | Revise unnatural, unclear, or poorly calibrated prose                          | Restructure clauses, fix collocations/register, cut clutter, keep voice   |
| `light-polish` | Fix only defects that obstruct comprehension or jar the ear                    | Minimal local edits; preserve sentence structure and rhythm wherever sane |
| `diagnose`     | Perform deep linguistic and pragmatic analysis of why a passage succeeds/fails | Analyze semantics, metaphor mapping, Gricean maxims, and social distance  |

## Three-Layer Architecture & Precedence

Timeless writing principles are kept apart from model quirks so rules do not decay when models change:

1. **Layer 1, core principles** (`rules/core.yaml`, `references/principles.md`): language-independent.
2. **Layer 2, language realization** (`rules/zh-CN.yaml`, `rules/en.yaml`, `rules/ja.yaml`): grammar, collocation, and register per language.
3. **Layer 3, versioned AI symptoms** (`patterns/symptoms.yaml`): observable model habits. A symptom match triggers contextual review (`review_only`), never automatic deletion.

**Precedence hierarchy**:

1. **Factual, causal, and terminology fidelity** (`core.fidelity.preserve_voice_and_facts`) outranks every stylistic rule.
2. **Pragmatic social distance and register fit** (`core.pragmatics.social_distance_and_register`, `core.pragmatics.epistemic_calibration`) outrank surface brevity.
3. **Conceptual clarity and actor-action alignment** (`core.clarity.*`, `core.syntax.*`, `core.logic.*`) outrank rhythm preferences.
4. **Rhythm and figurative concision** (`core.rhetoric.*`, `core.cohesion.*`) yield whenever preserving an earned literary metaphor or distinctive authorial voice requires them to yield.

## Standard 10-Step Workflow

### Step 1: Identify Purpose, Audience, Language, and Register

State the communicative goal (as a testable verb such as `configure`, `explain`, or `debug`), reader expertise, target language (`zh-CN`, `en`, `ja`), and register (`formal`, `professional`, `neutral`, `warm-supportive`, `literary`). For documentation (`technical-doc`), pick one content type (`Tutorial`: warm and predictable; `How-to`: terse and direct for a mid-task reader; `Reference`: neutral, exhaustive, quotable; `Conceptual`: teach-it-back clarity with analogies; `Troubleshooting`: empathetic without apology, acknowledge then fix) so a single page does one job rather than mixing three. Load the matching language guide from the References section below.

### Step 2: Extract the Intended Meaning and Invariants

Identify what the author is actually saying and lock the invariants that must survive untouched: numbers, units, entities, temporal order (`before` vs `while`), causal direction (`because` vs `coincided with`), scope qualifiers (`read-only` / `本番環境`), settled technical terms, and the author's stance.

**Gate 1 — Intent & Invariant Lock (proceed only when all are true):**

- [ ] Target language, genre, and register are explicitly identified
- [ ] Every checkable fact, temporal/scope qualifier, and protected technical term is inventoried
- [ ] Source text contains no unresolvable factual contradiction

_If gate fails_: If the source text contradicts itself on a factual claim or omits a required number in `generate` mode, stop and ask the user to clarify rather than guessing.

### Step 3: Check Factual, Semantic, and Logical Relations

Verify that every connective (`because`, `therefore`, `not X but Y`, `不是……而是……`, `したがって`) reflects a real relation between propositions:

- If a contrastive frame (`not X, but Y` / `不是……而是……` / `単なる〜ではなく`) negates a strawman nobody believed, delete the whole negative foil and state the positive claim directly; softening it into a milder strawman keeps the defect.
- If the contrast corrects a genuine misconception or disambiguates technical scope, keep it intact.

### Step 4: Check Collocation and Syntactic Naturalness

Test whether subjects and predicates pair naturally in the target language:

- Replace zombie nominalizations and verbal false limbs (`achieve a reduction`, `进行优化`, `実行を行う`) with direct verbs.
- Rewrite **spec-sheet voice** (`provides`, `is configurable`, `is explicitly labeled`), **personified artifacts** (`hand the browser a URL` $\to$ `the browser fetches the URL`; `the token holds` $\to$ `the token is stored`), and filler cadence verbs (`moves through`, `lands`, `carries`, `hits`) into literal actors and actions. Apply the **"by monkeys" test** for unintended passives and the **second-read test**: if you must re-read a sentence at speech pace to parse it, name the subject, action, and consequence directly.
- Strip translationese scaffolding (`在……的背景下`, `通过……的方式`, `〜によって…が〜される`) when active clauses or native topic-comment flow express the thought directly.
- Expand **telegraphic compression** into full predicates when prose is the target register: fused compounds doing finite-verb work (`直出`、`已清`、`同步改`、`换实现`), clipped locatives (`屏上`、`在三处`), and `每 + V + 一次` calques read as commit-log leakage; keep the shorthand in native headline genres (commit subjects, changelog bullets, titles) and prefer the accurate full term (`标签页` for browser tabs).
- Resolve bilingual glosses and literal English metaphor calques with the language guide loaded in Step 1: settled domain terms over calques, no literal-translation-plus-loanword glosses in Japanese, first-mention English anchors kept in Chinese, settled compounds kept in English.

### Step 5: Check Pragmatic Presuppositions and Social Distance

Verify that the tone matches the relationship between writer and reader:

- Remove unsolicited emotional performance or intimate metaphors (`我会稳稳地接住你的情绪`) in professional or informational prose; preserve them in counseling, caregiving, or physical descriptions where the context earns them.
- Remove chatbot wrapper residue (`Certainly!`, `希望这对你有帮助`), sycophantic praise, marketing rhetorical questions, and defensive throat-clearing.
- Replace **reader-pressuring minimizers** (`easy`, `simple`, `quick`, `简单`, `轻松`, `簡単`, `手軽`) with concrete descriptions (`"one command"`, `"default settings"`), and in documentation address the reader directly (`you`, imperative steps) rather than `the user`, `one can`, or stand-in `we`.
- In Japanese, keep `です・ます` and `だ・である` consistent across body text, and replace unwarranted `〜させていただく` or double honorifics (`ご覧になられる`) with standard polite forms (`いたします`, `ご覧になる`).

### Step 6: Test Whether Rhetoric Serves Meaning

Apply Orwell's image test:

- If a metaphor is a worn-out print cliché, mixes incompatible source domains, or dresses up a thin claim in grandiosity, replace it with a concrete statement.
- If a metaphor is fresh, literary, or domain-grounded, preserve it.

### Step 7: Calibrate Information Density and Rhythm

Cut words and sections that add zero semantic or pragmatic weight: stacked hedges, filler intensifiers (`very`, `just`, `really`), **summary-style transitions** that recap the previous paragraph (`With this setup complete…`, `Now that we've explored…`), **reused template framing** (`The question most teams face is whether…`), mechanical three-part parallelisms, and promotional `-ing` riders. Merge **stop-start fragments** (`Previously this was manual. Now it's automatic. This saves time.` $\to$ one sentence) and connect **cold-open body paragraphs** to their prior subject (`Because…`, `Once…`). Replace weasel qualifiers (`significantly`, `typically`, `generally`) and vague quantifiers (`near-zero`, `sub-second`, `most requests`) with cited figures when available in the source (or earn every detail when drafting in `generate` mode). In technical reports, state each metric once in its main home (summary or table, not both plus a conclusion), skip one-sentence subsections, keep metadata bullets short, and omit a closing summary when a table already closes the report.

### Step 8: Decide Intervention Scope by Mode

Compare candidate edits against the selected mode (`rewrite` vs `light-polish` vs `review`). Discard any edit that swaps synonyms on a working span (`そのため` $\to$ `ゆえに`) or adds unstated commitments not present in the source.

### Step 9: Run Fidelity and Restraint Verification Loop

1. Diff the draft against the Step 2 invariant list.
2. With Python available, write the original and the final text to temporary files and run the checks with the absolute path of this skill's directory (the folder you opened this SKILL.md from, written `<skill-dir>` below):
   ```bash
   uv run <skill-dir>/scripts/validate.py --mode fact-check --original orig.txt --rewritten final.txt
   uv run <skill-dir>/scripts/validate.py --mode scan --file final.txt
   ```
   Without `uv`, `python3` runs `fact-check`; `scan` also needs PyYAML.
3. Restore any number, unit, term, hedge, or qualifier that drifted (`fact-check` exit `2`). If `scan` flags `symptom.all.verification_narration_preface`, delete that sentence. Remove the temporary files.

**Gate 2 — Fidelity & Restraint Check (complete only when all are true):**

- [ ] Zero numbers, units, code spans, or domain terms were dropped or fabricated (`fact-check` exit code `0` when run)
- [ ] Temporal order, causal direction, and epistemic hedges match the source intent
- [ ] Every edited span fixed a concrete principle violation rather than swapping working words
- [ ] The reply begins with the deliverable itself, not with a status line

_If gate fails_: Revert the offending span edit, restore the exact invariant from Step 2, and re-run Step 9.

### Step 10: Deliver Output

Return the output matching the active mode in the Output Contract below.

## Output Contract & Worked Example

The reply is the deliverable: its first line is the document's `# Title` (or the polished passage itself) and its last section is the adjustments note below. Validator results, gate status, and scratch paths belong in tool output only, because readers receive this text as the finished document. The adjustments note states each fidelity outcome as a plain claim ("every figure is unchanged") without naming the tool or script that checked it. Do not wrap a requested Markdown document in an outer code fence or a `## Revised Text` heading.

- **`generate`**: Return the finished document directly starting with its `# Title`.
- **`rewrite` / `light-polish`**:
  1. Output the complete rewritten document directly (starting with its `# Title` when a document/report is requested, or the polished passage directly), followed by a horizontal rule (`---`).
  2. Below `---`, add a concise section in the **same language and register as the document** (`## 修订说明` / `## Key Adjustments & Preserved Elements` / `## 主な改訂点`) with 3–5 bullets naming the rule ID applied (`layer.category.name`), why it improved clarity or register, and which valid contrasts, technical anchors, or exceptions were preserved.
- **`review` / `diagnose`**:
  1. **Context & Register Assessment**: Target audience, register, and overall communicative effectiveness.
  2. **Findings**: Quoted span, rule ID (`core.*` or `zh|en|ja.*`), severity (`high`/`medium`/`low`), principle-based explanation of why it helps or hurts the reader, and concrete revision or preservation recommendation. When auditing files or patterns in batch, you may also emit a terse clickable `file:line - issue [rule_id]` list (or `✓ pass` for clean files) with no preamble.

### Worked Example (`rewrite` vs `keep` contextual judgment)

```json
{
  "case_rewrite": {
    "context": "Architecture review comment on database index rebuild (zh-CN, professional)",
    "input": "在推进存储层演进的背景下，我们对该慢查询索引进行了深度的重构，把检索延迟从 120 ms 降到了 15 ms。",
    "verdict": "rewrite",
    "output": "推进存储层升级时，我们重构了慢查询索引，将检索延迟从 120 ms 降至 15 ms。",
    "rationale": "zh.syntax.empty_light_verbs & zh.syntax.europeanized_prepositions_and_passives: removes '在……的背景下' and '进行了深度的重构', restoring active verb '重构' while keeping 120 ms -> 15 ms."
  },
  "case_keep": {
    "context": "TLS 1.3 security guide on 0-RTT replay limits (en, formal)",
    "input": "TLS 1.3 0-RTT data is not replay-safe across server restarts, but idempotent GET requests may use it when the application tracks session tickets.",
    "verdict": "keep",
    "output": "TLS 1.3 0-RTT data is not replay-safe across server restarts, but idempotent GET requests may use it when the application tracks session tickets.",
    "rationale": "Exemption triggered: 'not X, but Y' bounds a real security vulnerability against a safe operating exception, and 'idempotent' is the exact RFC term."
  }
}
```

## Failure Handling & Self-Correction

| Failure or Drift Signal                                                                                  | Recovery Action                                                                                     |
| -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `fact-check` exits with code `2` (dropped number, version, code span, or term)                           | Restore the exact missing token from the original text and re-run `validate.py --mode fact-check`   |
| Rewrite shifts timing (`before` $\to$ `while`) or upgrades correlation (`coincided with` $\to$ `caused`) | Revert the clause to match the source's exact temporal preposition and epistemic verb               |
| Rewrite introduces casual slang (`绝绝子`, `めっちゃ`, `no-brainer`)                                     | Replace slang with plain formal wording matching Step 1's register                                  |
| Candidate edit deletes a valid contrast (`in seconds, not milliseconds`, `不是内存泄漏，而是连接池耗尽`) | Restore the contrast because the negated branch disambiguates a real technical misconception        |
| Source draft has contradictory facts or missing required figures                                         | Do not invent figures; preserve the ambiguity explicitly or ask the user to supply the missing fact |
| `validate.py --mode scan --file <path>` exits with code `3`                                              | Verify the file path exists, or pass inline text via `--text "<prose>"` or stdin via `--file -`     |

## Gotchas

- **Over-pruning valid contrasts**: Writers use `not X, but Y` (`不是……而是……`, `〜ではなく〜だ`) legitimately when correcting a plausible misunderstanding ("The timeout is set in seconds, not milliseconds"). Keep any contrast whose negative branch carries disambiguating information.
- **Slang rebound when asked for "natural" tone**: Instructing a model to "sound human" or "remove AI flavor" frequently triggers internet slang or chat fillers. Anchor "natural" to clear, unpretentious written prose in the document's register.
- **Passive voice in Japanese and scientific prose**: English style guides favor active voice, but Japanese uses passive and intransitive constructions (`〜が修正されました`) to maintain topic continuity or polite neutrality, and scientific English uses passive voice when the actor is immaterial ("Samples were eluted at 4 °C"). Apply `core.cohesion.old_before_new` rather than forcing awkward active subjects.
- **Symptom fixation**: A text with zero matches in `patterns/symptoms.yaml` can still be poor prose if its logic is circular or its nouns are abstract; conversely, a passage that matches two surface patterns may be completely natural in its genre. Judge by Layer 1 and Layer 2 principles.

## References

Load only the files needed for the current language and task:

| Situation                                                                  | File to Read                                                                                                                             |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Understanding Orwell (1946) analysis and cross-linguistic writing theory   | [references/foundations.md](references/foundations.md)                                                                                   |
| Checking bibliography, primary citations, scope, and source limits         | [references/sources.md](references/sources.md)                                                                                           |
| Reviewing Layer 1 durable human expression principles                      | [references/principles.md](references/principles.md)                                                                                     |
| Diagnosing pragmatic anomalies (metaphors, false contrasts, register)      | [references/pragmatics.md](references/pragmatics.md)                                                                                     |
| Writing or editing Simplified Chinese (`zh-CN`)                            | [references/chinese.md](references/chinese.md)                                                                                           |
| Writing or editing English (`en`)                                          | [references/english.md](references/english.md)                                                                                           |
| Writing or editing Japanese (`ja`)                                         | [references/japanese.md](references/japanese.md)                                                                                         |
| Inspecting machine-readable Layer 1 & Layer 2 rules                        | [rules/core.yaml](rules/core.yaml), [rules/zh-CN.yaml](rules/zh-CN.yaml), [rules/en.yaml](rules/en.yaml), [rules/ja.yaml](rules/ja.yaml) |
| Inspecting Layer 3 versioned AI symptoms and schema                        | [patterns/symptoms.yaml](patterns/symptoms.yaml), [patterns/schema.json](patterns/schema.json)                                           |
| Consulting annotated positive/negative/exception examples                  | [examples/zh-CN.jsonl](examples/zh-CN.jsonl), [examples/en.jsonl](examples/en.jsonl), [examples/ja.jsonl](examples/ja.jsonl)             |
| Running evaluations, scoring rubrics, or ablation comparisons              | [evals/cases.jsonl](evals/cases.jsonl), [evals/rubric.md](evals/rubric.md), [evals/ablation.md](evals/ablation.md)                       |
| Running fact-check regression fixtures after editing `scripts/validate.py` | Execute [scripts/fact-check-regressions.sh](scripts/fact-check-regressions.sh)                                                           |
