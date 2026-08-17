---
name: polish-japanese-docs
description: >
  Polishes existing Japanese technical docs into natural technical-document prose — fixes
  translationese, normalizes register, and cleans awkward collocations. Use when asked to
  fix translationese, normalize doc tone, or /polish-japanese-docs.
license: MIT
compatibility: Requires file read/write access. No external services needed.
metadata:
  author: fang2hou
  version: "1.1"
---

# Polish Japanese Docs

Rewrite existing Japanese technical documentation — README, skill descriptions, internal engineering prose — into natural, concise, standard Japanese technical-document prose. Preserves all technical content, structure, and meaning.

## When to Use

- User asks to polish or clean up Japanese README / docs text
- User asks to remove translationese from Japanese docs
- User wants Japanese doc register normalized to standard business-technical tone
- User says "日本語を自然にして" or `/polish-japanese-docs`

## When NOT to Use

- Translating from English into Japanese (this skill polishes EXISTING Japanese)
- Writing new Japanese content from scratch
- Marketing copy, press releases, or customer-facing sales material
- Non-Japanese documentation
- Glossary management or terminology standardization projects

## Inputs

| Input       | Required | Format                   | Example                                                                   |
| ----------- | -------- | ------------------------ | ------------------------------------------------------------------------- |
| Target text | Yes      | File path or inline text | `README.md`, pasted Japanese paragraph                                    |
| Scope       | No       | Section or line range    | "スキル一覧 table only", "lines 10-30"                                    |
| Register    | No       | Tone directive           | "もう少しカジュアルに" (defaults to standard technical-document register) |

## Hard Rules

1. **Read the entire target text before editing**: Never start rewriting from partial context. Tone and terminology choices must be consistent across the whole document.
2. **Preserve structure**: Do not reorder sections, remove headings, change URLs, alter code blocks, or modify command examples unless the user explicitly asks.
3. **Preserve technical meaning**: The polished text must convey exactly the same information. If a phrasing change risks altering meaning, keep the original.
4. **No English substitution**: Do not replace Japanese text with English unless the English term is the standard industry convention (e.g., `README`, `CLI`, `PR`).
5. **Two-pass minimum**: Always perform a second pass focused specifically on tables, dense noun phrases, and headings — these are where residual awkwardness hides.
6. **Show evidence of cleanup**: After editing, briefly list the key awkward phrases that were fixed and what they became. This lets the user verify intent was preserved.
7. **Do not expand scope**: If you notice unrelated problems (broken links, incorrect commands, factual errors), flag them separately but do not fix them unless asked.

## Target Register

Standard Japanese technical-document register: natural, concise prose that any engineer reads without friction.

| Dimension          | Target                                                      | Avoid                                         |
| ------------------ | ----------------------------------------------------------- | --------------------------------------------- |
| Formality          | です/ます体 for prose; 体言止め for table cells and bullets | である体 (too academic), タメ口 (too casual)  |
| Headings           | Noun phrases or short verb phrases                          | Conversational sentences as headings          |
| Sentence length    | 1 idea per sentence; split if > ~60 characters              | Long compound sentences with multiple clauses |
| Katakana loanwords | Use when standard (インストール, テンプレート)              | Overuse where native Japanese is more natural |
| Technical terms    | Prefer terms your audience uses daily                       | Invented compounds that require decoding      |

Keep the Target Register table inline: register calibration is load-bearing for the two-pass workflow, so moving these criteria to a reference would add retrieval cost at the point where they guide every rewrite.

## Worked Example

For a translationese sentence, preserve the technical claim while changing the Japanese structure:

- Before: `設定の確認を行うことが必要となります。`
- After: `設定を確認する必要があります。`
- Rationale: Replace a calqued nominalized expression with a natural necessity expression without changing the requirement.

Apply the same discipline to dense terms:

- Before: `承認ゲート付きワークフロー`
- After: `承認ステップを含むワークフロー`
- Rationale: Replace a mixed-script calque with a phrase that states the workflow relationship naturally.

The example demonstrates wording changes only; headings, tables, code blocks, URLs, and commands remain in their original positions unless explicitly authorized.

Before Step 2, confirm all four Step 1 outputs: the full document was read, the document type was identified, register inconsistencies were noted, and the dominant problem category was recorded. If any item is missing, remain in Step 1.

## Workflow

### Step 1: Read and Assess

1. Read the entire target text end to end.
2. Identify the document type: README, SKILL.md description, internal wiki, commit/PR text, etc.
3. Note the current register and any inconsistencies (mixed formal/informal, mixed です/ます and である).
4. Identify the dominant problem category:
   - **Translationese**: Japanese that follows English sentence structure
   - **Collocation mismatch**: Words that are individually correct but unnatural together
   - **Register drift**: Inconsistent formality level across the document
   - **Overcompression**: Dense noun phrases that need unpacking

### Step 2: First Pass — Core Rewrite

Work through the document section by section:

1. **Fix translationese sentence structures**: Break long relative clauses, move modifiers closer to what they modify, prefer Japanese word order.
2. **Replace unnatural collocations**: See [references/phrase-patterns.md](references/phrase-patterns.md) for common patterns. Key signals:
   - Compound nouns that require mental decoding (e.g., `承認ゲート` → `承認ステップ`)
   - Verb-noun pairs that don't naturally co-occur in Japanese (e.g., `コンテキストを解決し` → `コンテキストを踏まえ`)
   - Imported metaphors that don't carry over (e.g., `修正導線` → `修正フロー`)
3. **Normalize register**: Standardize to the target register across all sections.
4. **Simplify dense noun phrases**: If a noun phrase has 3+ modifiers stacked, restructure it.

### Step 3: Second Pass — Tables, Headings, and Residual Cleanup

This pass catches problems the first pass misses. Tables and headings are denser than prose and need separate attention.

1. **Re-read every table cell**: Table descriptions are often compressed and accumulate awkward phrasing. Read each cell as if it were standalone text.
2. **Check every heading**: Headings should be scannable noun phrases. Replace conversational or verbose headings.
3. **Hunt for residual unnatural compounds**: After the first pass creates new sentences, some noun phrases that looked fine in the old context may now sound awkward. Fix them.
4. **Check particles and conjunctions**: Translationese often misuses は/が, overuses の chains, or drops particles that Japanese readers expect.

### Step 4: Verify — Search and Confirm

Do not rely on a single manual reread. Verify systematically:

1. **Build a bad-phrase checklist**: Collect every awkward phrase you identified in Step 1–2 into a flat list of literal strings.
2. **Search the final text for each bad phrase**: Use grep or text search — do not eyeball. Every phrase on the checklist must return zero hits in the polished output.
3. **If any bad phrase survives**: Fix it now. This is the most common failure mode — a phrase gets missed in one table cell or heading.
4. **Scan for the pattern classes** that generated those bad phrases (not just the exact strings):
   - 4+ kanji/katakana compound nouns without particles
   - `Xを解決` where X is not a problem
   - Mixed kanji-katakana-English compounds
   - Headings longer than ~15 characters
5. **Re-read the final text** from start to finish as a native reader would.
6. **Confirm structural integrity**: Sections, code blocks, URLs, and commands are unchanged.
7. **Produce the change summary**:

```
Fixed phrases:
- `旧フレーズ` → `新フレーズ` (理由)
- `旧フレーズ` → `新フレーズ` (理由)

Verified removed (search confirmed zero hits):
- `旧フレーズ1`
- `旧フレーズ2`
```

If any change feels ambiguous, flag it for user confirmation rather than silently committing.

## Gotchas

- **Grammatically valid ≠ natural**: `ライブラリ癖` is parseable but no one says it. Replace with a phrase that a Japanese engineer would actually write (e.g., `ライブラリ固有の挙動`). The skill's value is catching these — don't rely on grammar checkers.
- **Tables need a stricter pass than prose**: Table cells compress information, which amplifies collocation problems. A phrase that reads fine in a full sentence may sound bizarre in a table cell. Always re-read tables independently.
- **Headings should be noun phrases, not sentences**: Japanese technical docs conventionally use short noun phrases for headings (e.g., `インストール手順`), not conversational phrases (e.g., `インストールの仕方について`).
- **English-origin words carry wrong nuance in Japanese business writing**: `証拠付きレビュー` (evidence-backed review) is a direct calque; Japanese engineers say `根拠に基づくレビュー`. Similarly, `保守的な allowed-tools` mixes Japanese adjective with English noun unnaturally; restructure as `必要最小限の allowed-tools`.
- **Compound noun stacking is the #1 residual problem**: After fixing obvious translationese, the remaining issues are almost always stacked compound nouns like `品質改善提案ゲート` or `スキル品質継続改善`. Break them apart with particles or rephrase.
- **Don't over-correct katakana**: Some katakana words ARE standard (インストール, テンプレート, コンテキスト). Only replace katakana when a more natural alternative exists AND is actually used in the industry.
- **Mixed-script compounds need extra scrutiny**: Phrases mixing kanji + katakana + English like `修正導線` or `承認ゲート付き` are high-probability collocation mismatches. Check each one.
- **Register consistency across document**: A single です/ます sentence in a document otherwise using 体言止め is jarring. Pick one and apply consistently within each context (prose vs. table vs. heading).

## Escalation and Re-run

Autonomously correct surface-level translationese, collocation, register, and density problems when the technical meaning remains unchanged and the edit stays within the authorized scope. Preserve the original when uncertain.

Escalate before editing when:

- **Meaning may change**: Ask, “Which meaning is intended — [interpretation A] or [interpretation B], and may I apply [proposed rewrite]?” Include the original wording and both interpretations.
- **Terminology conflicts**: The document defines a term differently from the Target Register table or phrase reference. Ask, “Should the document-local definition or the register/reference meaning govern? Which term should I use?”
- **Structure would change**: A natural rewrite would reorder or remove sections, headings, tables, code blocks, URLs, or commands without explicit authorization. Ask, “May I make these exact structural changes: [list]?” Do not make them while waiting.

On a re-run against an already-polished document, read the whole document and repeat both passes and zero-hit verification. Preserve wording that already meets the register; do not churn it for variation. If no change is needed, return the unchanged text, an empty change summary, and only genuine flags or out-of-scope observations.

## Output Contract

On completion, return the following four fields in this exact order. **Polished text** is the primary artifact and must contain the full rewritten document or requested section.

1. **Polished text**: The full rewritten document or section.
2. **Change summary**: Each key change with `before`, `after`, and `rationale`.
3. **Flags**: Meaning, terminology, or authorization questions requiring user confirmation.
4. **Out-of-scope observations**: Unrelated issues noticed but not fixed (broken links, factual errors, etc.).

Use this stable field order for downstream consumers while keeping the human-readable report primary:

```text
OUTPUT_FIELDS (in order):
1. polished_text
2. change_summary (before, after, rationale)
3. flags
4. out_of_scope_observations
```

On a no-op re-run, set `polished_text` to the unchanged input, report `change_summary` as empty, and leave `flags` and `out_of_scope_observations` empty unless there is a real item to report.

## References

- [Phrase Patterns](references/phrase-patterns.md) — Common awkward-to-natural phrase mappings grounded in real doc cleanup work
