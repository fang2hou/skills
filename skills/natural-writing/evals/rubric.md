# Quality Evaluation Rubric (`evals/rubric.md`)

This rubric defines the reproducible evaluation protocol for judging generated, reviewed, and rewritten prose across Chinese (`zh-CN`), English (`en`), and Japanese (`ja`). Heuristic scripts (`scripts/validate.py`) verify structural integrity and factual invariants, while this 8-dimension rubric governs human and LLM-judge quality assessment.

Contents:

- [1. Eight Evaluation Dimensions (1–5 Scale)](#1-eight-evaluation-dimensions-15-scale)
- [2. Hard Failure Gates (Auto-Fail Conditions)](#2-hard-failure-gates-auto-fail-conditions)
- [3. Edge-Case Verification Matrix](#3-edge-case-verification-matrix)
- [4. Scoring and Aggregation Protocol](#4-scoring-and-aggregation-protocol)

---

## 1. Eight Evaluation Dimensions (1–5 Scale)

Score each dimension from **1 (broken)** to **5 (exemplary)**. Maximum score: **40 / 40**.

| #   | Dimension                        | Weight | Score 1 (Fail)                                                                      | Score 3 (Acceptable)                                                     | Score 5 (Exemplary)                                                                                      |
| --- | -------------------------------- | ------ | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| 1   | **Semantic Fidelity**            | Gate   | Alters causal claims, flips polarity, or changes who did what                       | Preserves core meaning with minor nuance shifts                          | Preserves 100% of propositions, causal direction, epistemic certainty, and scope boundaries              |
| 2   | **Linguistic Naturalness**       | High   | Reads like translationese, bureaucratic operators, or stitched-together templates   | Grammatical and readable, with occasional stiff collocations             | Idiomatic subject–verb flow and native collocations in `zh-CN`, `en`, or `ja`                            |
| 3   | **Clarity of Expression**        | High   | Buries actors in nominalizations, twisted modifiers (`ねじれ`), or vague nouns      | Meaning is recoverable on first read, with minor syntactic clutter       | Actors and actions align immediately; modifier attachment (`係り受け`) is unambiguous on first reading   |
| 4   | **Register & Pragmatic Fit**     | High   | Crosses social distance (`稳稳接住` in work docs), mixes `敬体/常体`, or uses slang | Matches broad genre, with minor stiffness or slight politeness inflation | Calibrates formality, politeness (`敬語`), and social distance ($D, P, R$) accurately to audience        |
| 5   | **Rhetorical Effectiveness**     | Medium | Uses dying/mixed metaphors, strawman `not X, but Y` contrasts, or empty triads      | Avoids glaring clichés; rhetoric is neutral                              | Every contrast is earned and every metaphor clarifies meaning or preserves intentional literary imagery  |
| 6   | **Information Completeness**     | Gate   | Drops numbers, units, versions, conditions, or required technical caveats           | Retains all major facts; trims only minor peripheral context             | Retains every verifiable fact, metric, unit, version, and boundary condition while cutting pure padding  |
| 7   | **Authorial Voice Preservation** | Medium | Flattens distinctive personal prose into uniform corporate or chatbot tone          | Preserves general stance while normalizing some characteristic phrasing  | Retains the writer's authentic rhythm, dry humor, or domain authority while fixing only real defects     |
| 8   | **Unnecessary Edit Restraint**   | High   | Rewrites already natural sentences or deletes valid contrasts/metaphors by rule     | Edits mostly defective spans, with 1–2 synonym swaps on working clauses  | Zero gratuitous edits: leaves working sentences, valid contrasts, and earned metaphors completely intact |

---

## 2. Hard Failure Gates (Auto-Fail Conditions)

A candidate output **automatically fails (`PASS = false`)** regardless of its total score if any of the following occur:

1. **Fact or Number Drift**: Any number, unit, percentage, version, port, date, or named entity in `must_preserve` is dropped or altered (checked mechanically via `scripts/validate.py --mode fact-check`).
2. **Causal Fabrication**: Temporal sequence (_"After update X, error Y stopped"_) is rewritten as verified causation (_"Update X fixed error Y"_) when a confounding variable is documented.
3. **Colloquial Slang Overcorrection**: A formal or professional text is rewritten with internet slang or rough shorthand (`绝绝子`, `狠狠拿捏`, `一把梭`, `blew up`, `no-brainer`, `ぶっちゃけ`, `死んだ`).
4. **False Positive Deletion of Valid Rhetoric**: A legitimate disambiguating contrast (`not X, but Y` / `不是……而是……` / `単なる〜ではなく`) or a domain-appropriate metaphor (`稳稳地接住` in clinical grief counseling; sustained literary metaphor in an essay) is mechanically erased.
5. **Terminology Corruption**: Settled technical terms (`idempotency`, `幂等性`, `べき等性`, `tree-shaking`, `灰度发布`, `正常系`) are replaced with amateur paraphrases or literal English calques (`金丝雀发布`, `摇树优化`, `ハッピーパス`).

---

## 3. Edge-Case Verification Matrix

Every evaluation run against `evals/cases.jsonl` must verify these eight mandatory edge cases:

| Edge Case Category                 | Test Case IDs                            | What Is Tested                                                                                                                                              |
| ---------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Context-sensitive metaphor**     | `eval.zh.01`, `eval.zh.02`, `eval.zh.07` | `"稳稳地接住"` is rewritten in an engineering ticket (`eval.zh.01`) but preserved in grief counseling (`eval.zh.02`).                                       |
| **Valid contrast preservation**    | `eval.zh.03`, `eval.en.02`, `eval.ja.05` | Genuine `"不是…而是…"`, `"X, not Y"`, and `"単なる〜ではなく"` contrasts that prevent errors are kept intact.                                               |
| **False contrast removal**         | `eval.zh.04`, `eval.en.06`               | Theatrical strawman contrasts (`"不仅是一次简单的…更是一场深刻涅槃"`) are collapsed into direct facts.                                                      |
| **Anti-colloquial overcorrection** | `eval.zh.05`, `eval.en.04`, `eval.ja.04` | Slang-heavy drafts are elevated to plain, dignified written prose without swinging into corporate buzzwords.                                                |
| **Literary metaphor preservation** | `eval.en.03`                             | Coherent literary imagery (_"silts up like an un-dredged harbor"_) is preserved untouched.                                                                  |
| **Technical term preservation**    | `eval.zh.06`, `eval.ja.04`               | Literal calques are repaired while standard technical terms (`幂等性`, `tree-shaking`) are protected.                                                       |
| **Information density & fidelity** | `eval.en.01`, `eval.en.05`, `eval.ja.03` | Clutter and nominalizations are cut while preserving 100% of metrics and causal uncertainty caveats.                                                        |
| **Register & Keigo calibration**   | `eval.ja.01`, `eval.ja.02`               | Unwarranted `〜させていただきます` and double keigo are fixed (`eval.ja.01`), while valid permission+benefit `〜させていただきます` is kept (`eval.ja.02`). |

---

## 4. Scoring and Aggregation Protocol

1. **Mechanical Pre-Check**: Run `uv run skills/natural-writing/scripts/validate.py --mode fact-check` on every rewrite case. Any missing invariant sets Gate 1/6 to `FAIL`.
2. **Assertion Grading**: Grade each case's `assertions` in `evals/cases.jsonl` with quoted evidence from the candidate output (`PASS` only when all assertions pass and zero `must_avoid` strings appear).
3. **Blind Rubric Scoring**: Score Dimensions 1–8 on the 1–5 scale. A configuration achieves production quality at **$\ge 34 / 40$ mean score** and **100% assertion pass rate** across all three languages.
