# Ablation Study Design and Empirical Evaluation (`evals/ablation.md`)

This document defines the ablation and `improve-skill` trial-run protocol for `natural-writing` and records two empirical evaluations:

1. A five-system zero-n-gram-leakage ablation scored by an independent blinded judge subagent (`BlindedJudgeV2`).
2. A live field trial on `pi` agent + `zai/glm-5.3-flashx` (2026-10-18): 9 technical-report cases (zh-CN / en / ja × Frontend / Backend / Architecture), directly judged by the primary model, driving the `v1.1.0 → v1.2.1` optimization.

Contents:

- [1. Experimental Protocol, Bidirectional N-Gram Anti-Leakage Guard, and Blinding](#1-experimental-protocol-bidirectional-n-gram-anti-leakage-guard-and-blinding)
- [2. Zero-Leakage Held-Out Benchmark Subset (9 Cases + 1 Conflict Probe)](#2-zero-leakage-held-out-benchmark-subset-9-cases--1-conflict-probe)
- [3. Mechanical Assertion Matrix & Blinded Rubric Results](#3-mechanical-assertion-matrix--blinded-rubric-results)
- [4. Case-by-Case Qualitative Analysis](#4-case-by-case-qualitative-analysis)
- [5. Key Findings on Layer 2, Layer 3, and v1.1.0 Improvements](#5-key-findings-on-layer-2-layer-3-and-v110-improvements)
- [6. Field Trial: pi + zai/glm-5.3-flashx (v1.2.x)](#6-field-trial-pi--zaiglm-53-flashx-v12x)
- [7. Reproducing the Evaluation](#7-reproducing-the-evaluation)
- [8. improve-skill Pass: v1.2.1 → v1.3.0](#8-improve-skill-pass-v121--v130)

---

## 1. Experimental Protocol, Bidirectional N-Gram Anti-Leakage Guard, and Blinding

To ensure the evaluation measures genuine generalization rather than example memorization or evaluator bias, four methodological controls are enforced:

1. **Strict Bidirectional N-Gram Anti-Leakage Guard (`scripts/validate.py` Step 7)**:
   - Step 7 of `scripts/validate.py` mechanically checks that no `input_text` or `reference_output` across all 19 cases in `evals/cases.jsonl` shares **any Latin 3-word window (`0` overlaps permitted)** or **any non-inflectional CJK 4-gram** with any of the 17 shipped files (`SKILL.md`, `README.md`, `rules/*.yaml`, `patterns/symptoms.yaml`, `examples/*.jsonl`, `references/*.md`).
   - Every evaluation subagent is explicitly forbidden from reading `evals/`.
2. **Five Isolated Fresh-Context Subagents**:
   - **Condition 0 (`ZeroLeakC0` / `System K` — Baseline, No Skill)**: Reads zero repository files; prompted to remove AI flavor and make the passages natural and clear.
   - **Condition 1 (`ZeroLeakC1` / `System L` — Layer 1 Core Only)**: Reads only `rules/core.yaml` and `references/principles.md`.
   - **Condition 2 (`ZeroLeakC2` / `System M` — Layer 1 + Layer 2 Language Rules)**: Reads `rules/{core,zh-CN,en,ja}.yaml` (no access to `SKILL.md` or `patterns/symptoms.yaml`).
   - **Pre-Improvement Snapshot (`TrialBaselineV1` / `System N` — v1.0.0 Skill)**: Reads the pre-`improve-skill` v1.0.0 snapshot (captured in `/tmp/natural-writing-baseline-snapshot` before Phase 4 edits and removed after trial completion).
   - **Condition 3 (`TrialImprovedV1_1` / `System W` — v1.1.0 Full Skill: Layer 1 + 2 + 3)**: Reads the optimized v1.1.0 `SKILL.md`, `references/pragmatics.md`, `rules/{zh-CN,en,ja}.yaml`, and `patterns/symptoms.yaml`.
3. **Mechanical Token Grading + Blinded Independent Judge (`BlindedJudgeV2`)**:
   - All five systems' outputs are first graded mechanically by script against the pre-registered `expected_action`, `must_preserve`, and `must_avoid` arrays in `evals/cases.jsonl` (including the strict `"バグ"` ban in `eval.ja.04`).
   - Outputs from all five systems were also anonymized (`System K`, `System L`, `System M`, `System N`, `System W`) and scored by an independent fresh-context `BlindedJudgeV2` subagent that read **only** `evals/rubric.md`.

---

## 2. Zero-Leakage Held-Out Benchmark Subset (9 Cases + 1 Conflict Probe)

The live trial evaluated 10 cases from `evals/cases.jsonl`: **4 rewrite cases** (`expected_action: rewrite`), **5 restraint/preservation control cases** (`expected_action: keep`), and **1 contradictory-source-fact probe** (`eval.en.07`, `expected_action: escalate`):

### Rewrite Cases (`expected_action: rewrite`)

1. **`eval.zh.01`** (_Ticket reply on monthly settlement aggregation_): `"各位对账期延迟的担忧已稳稳地接住！下周咱对齐口径，靠组合拳彻底闭环月结报表卡顿，将汇总时长由 42 秒缩短至 5 秒内。"`
   - `must_preserve`: `["42 秒", "5 秒", "月结报表"]` | `must_avoid`: `["稳稳地接住", "对齐口径", "组合拳", "彻底闭环", "绝绝子", "一把梭"]`
2. **`eval.en.01`** (_Storage runbook for cordoning a raid0 array_): `"Fantastic inquiry! Let us jump straight in. Ahead of invoking the v3.1 cordon utility, a verification of raid0 array health must be executed by our duty operator, fostering ironclad resilience while highlighting our dedication to zero packet drops. Whenever rebuilding sectors surpass 0.5% on port 6800, cordoning aborts. Such discipline guarantees victory. Hope that clears things up!"`
   - `must_preserve`: `["v3.1", "raid0", "0.5%", "6800", "aborts"]` | `must_avoid`: `["Fantastic inquiry", "jump straight in", "Ahead of invoking", "highlighting our dedication", "guarantees victory", "Hope that clears things up"]`
3. **`eval.ja.01`** (_Enterprise payment notification API v4.1 notice_): `"今朝は、決済通知 API（v4.1）の改定内容をご連絡させていただきます。併せて、先月ご担当者様が申されていた再試行周期（15 秒）の件も反映させていただきます。これにて通知遅延は収束するのだ。"`
   - `must_preserve`: `["v4.1", "15 秒", "決済通知 API", "再試行周期"]` | `must_avoid`: `["ご連絡させていただきます", "反映させていただきます", "申されていた", "収束するのだ"]`
4. **`eval.ja.04`** (_Executive postmortem on port 9090 aggregation batch_): `"正直、未明の無人稼働中にポート 9090 の集計処理が落ちたので、バグの緊急度を揃えた上で旧クエリをスパッと捨てて、カナリア配備の煙試験をいい具合に整えました。"`
   - `must_preserve`: `["9090", "集計処理"]` | `must_avoid`: `["正直", "落ちた", "スパッと", "いい具合に", "バグ", "カナリア配備", "煙試験"]`

### Restraint / Preservation Cases (`expected_action: keep`)

5. **`eval.zh.02`** (_Adolescent sandplay therapy manual_): `"每当受访少年在沙盘旁因恐惧而颤抖时，督导师切勿立刻盘问缘由，应当稳稳地接住少年涌出的惊惶与羞怯，帮他重建内在信任。"`
6. **`eval.zh.03`** (_Queue backlog postmortem root cause_): `"昨夜队列积压并非源于交换机网卡丢包，而是源于风控消费者把批量拉取参数（`max.poll.records`）由 500 误改成了 10。"`
7. **`eval.en.02`** (_ChaCha20 cryptography SDK doc_): `"Each ChaCha20 cipher call demands a distinct 96-bit nonce per packet under one secret key, never a shared salt across sessions; repeating any nonce destroys stream confidentiality."`
8. **`eval.en.03`** (_Signed distributed-clocks essay_): `"Monotonic time across distant datacenters resembles wet elastic unlike a brass yardstick: each blade lengthens or shortens its ticks with crystal warmth, until two cabinets four aisles away dispute which ledger entry arrived first."`
9. **`eval.ja.02`** (_Client encrypted audit-record permission email_): `"御社から受領した暗号化済み証跡記録を、原因究明のため 12 月 20 日まで使用させていただきます。"`

### Contradictory Source-Fact Escalation Probe (`expected_action: escalate`)

10. **`eval.en.07`** (_Release draft with contradictory figures and `[TBD]`_): `"Amid our relentless pursuit of excellence, the v5.2 cache patch reduced p99 latency from 80 ms to [TBD] ms while simultaneously increasing p99 latency by 45% across every production node."`

---

## 3. Mechanical Assertion Matrix & Blinded Rubric Results

### 3.1 Summary Table (Mechanical Script + `BlindedJudgeV2` Rubric)

_(Note: Single-run wall-clock times reflect one parallel subagent execution per configuration and are reported as non-causal observations.)_

| Configuration (Blinded ID)                      | Mechanical Case Pass (9 Cases, Strict `must_avoid`)                | Mechanical Token Checks Passed (out of 59) | Blinded Hard Gate Failures | Keep Restraint Rate (5 Cases) | 9-Case Mean Rubric Score (/40) |
| ----------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ | -------------------------- | ----------------------------- | ------------------------------ |
| **Condition 0: Baseline (`System K`)**          | 8 / 9 (`ja.04`: kept `カナリア配備`)                               | 58 / 59 (98.3%)                            | 0                          | 5 / 5 (100%)                  | **38.33** (345 / 360)          |
| **Condition 1: Layer 1 Core (`System L`)**      | 7 / 9 (`zh.01`: `对齐口径`; `ja.04`: `バグ, カナリア配備`)         | 56 / 59 (94.9%)                            | 0                          | 5 / 5 (100%)                  | **39.11** (352 / 360)          |
| **Condition 2: Layer 1 + 2 (`System M`)**       | 8 / 9 (`ja.04`: kept `バグ`, fixed both calques)                   | **58 / 59 (98.3%)**                        | 0                          | 5 / 5 (100%)                  | **38.89** (350 / 360)          |
| **Pre-Improvement v1.0.0 (`System N`)**         | 7 / 9 (`zh.01`: `对齐口径`; `ja.04`: `バグ, カナリア配備, 煙試験`) | 55 / 59 (93.2%)                            | **1** (`ja.04` Gate §2.5)  | 5 / 5 (100%)                  | **38.44** (346 / 360)          |
| **Condition 3: v1.1.0 Full Skill (`System W`)** | **8 / 9** (`ja.04`: kept `バグ`, fixed both calques)               | **58 / 59 (98.3%)**                        | **0**                      | 5 / 5 (100%)                  | **39.56** (356 / 360)          |

### 3.2 Per-Case Blinded Rubric Breakdown (Out of 40)

| Case ID      | C0 (`K`) | C1 (`L`) | C2 (`M`) | v1.0.0 (`N`)            | v1.1.0 (`W`) | Key Finding                                                                                     |
| ------------ | -------- | -------- | -------- | ----------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| `eval.zh.01` | 33       | 37       | 35       | 38                      | **38**       | `W` replaced all 4 buzzwords; `L` kept `对齐口径`; `K` slipped into casual register.            |
| `eval.en.01` | 38       | 40       | 37       | 40                      | **40**       | Clean spans left verbatim by `L`, `N`, `W`.                                                     |
| `eval.ja.01` | 38       | 38       | 39       | 38                      | **39**       | `M`/`W` repaired keigo and `収束するのだ`.                                                      |
| `eval.ja.04` | 36       | 37       | 39       | **30 (GATE FAIL §2.5)** | **39**       | `N` left unseen calque `煙試験` unfixed; `W` generalized to `カナリアリリースのスモークテスト`. |
| 5 Keep Cases | 40 × 5   | 40 × 5   | 40 × 5   | 40 × 5                  | **40 × 5**   | All configurations preserved all 5 control cases verbatim.                                      |

---

## 4. Case-by-Case Qualitative Analysis

### 4.1 `eval.ja.04`: Unseen Calque Generalization

- **v1.0.0 (`System N`, 30/40, Gate 5 FAIL)**: Retained raw literal calque `カナリア配備の煙試験` and padded the ending with bureaucratic `体制を整えました`.
- **v1.1.0 (`System W`, 39/40, Gate 5 PASS)**: Generalized the Step 4 calque instruction to unseen inputs (`カナリア配備の煙試験` → `カナリアリリースのスモークテスト`) and repaired the collocation `緊急度を揃えた` → `緊急度を評価した`. Under the strict mechanical `must_avoid` check, `L`, `M`, `N`, `W` all retained `バグ` as standard technical vocabulary.

### 4.2 `eval.zh.01`: Avoiding Both Slang Rebound and Proposition Drop

- `K` rewrote into casual chat; `L` dropped the named defect and kept `对齐口径`; `W` passed 100% of mechanical checks, replacing all four defective spans with plain professional Chinese.

### 4.3 `eval.en.07`: Gate 1 Factual Contradiction Escalation

- All five systems escalated without inventing a figure for `[TBD]`; `W` (v1.1.0) cited Gate 1 and asked a concise English clarification question.

---

## 5. Key Findings on Layer 2, Layer 3, and v1.1.0 Improvements

1. **Zero-Leakage Generalization**: With every Latin 3-word window and non-inflectional CJK 4-gram disjoint from the skill corpus, the full skill achieves **39.56 / 40** blinded rubric mean, **zero hard-gate failures**, and **58/59 mechanical token checks**.
2. **v1.0.0 → v1.1.0 gain**: Rubric mean **38.44 → 39.56**; hard gates **4/5 → 5/5**; mechanical token checks **55/59 → 58/59** (`对齐口径`, `カナリア配備`, `煙試験` flipped to PASS).

---

## 6. Field Trial: pi + zai/glm-5.3-flashx (v1.2.x)

### 6.1 Setup

- **Harness**: `pi --model zai/glm-5.3-flashx --no-session --no-skills --skill skills/natural-writing --mode json -p <prompt>` (model registered in `~/.pi/agent/models.json` as a verbatim clone of the `glm-5.3-flash` catalog entry with only `id`/`name` changed).
- **Matrix**: 9 cases — zh-CN / en / ja × Frontend / Backend / Architecture Design. Each prompt embeds a realistic draft mixing AI inflation, internet slang, officialese, translationese, literal calques, and hard engineering figures, and requests a full Markdown technical report.
- **Judging**: the primary model directly read every output and tool-call trace (no subagents). Scores below are the strict re-judgment after dock verification-narration leaks and case-specific residuals.
- **Rounds**: Round 1 = `v1.1.0`; Round 2 = `v1.2.0`; Round 3 = `v1.2.1` (tightened output contract + repaired `fact-check`), re-running only the 4 cases that leaked validator narration in Round 2.
- **Caveat**: Round 1/2 raw artifacts were deleted during cleanup (recorded as a process error); verdicts below rest on the quoted excerpts preserved in this record and the session transcript. Round 3 artifacts are kept at `~/.local/share/natural-writing-evals/round3-v1.2.1-artifacts/` (outside the repository).

### 6.2 Round 1 (`v1.1.0`) Failure Modes (drove the v1.2.x design)

1. `<直訳漢字>（<定着カタカナ語>）` calque residue in Japanese (`トークンの回転（ローテーション）` kept verbatim in `ja_arch`).
2. Chinese first-mention English anchors deleted (`（Dirty Rectangle）`, `（Composition Lock）` dropped in `zh_frontend`).
3. Theatrical contrast softened into a milder strawman (`ja_frontend`: `表層的な改修ではなく、アーキテクチャ変更である`).
4. Sandwich repetition: the same metrics repeated 3× across Summary/Body/Table/Conclusion; one-sentence stub `###` subsections.
5. Delivery wrapper noise: every case opened with `fact-check exit 0`-style narration, wrapped the document in ` ```markdown ` fences, leaked `/tmp/...` paths.
6. **Validator defects amplifying (5)**: heading numbers (`## 1.`, `### 3.1`) flagged as fabricated numbers, forcing heading-number stripping; CJK digit spacing (`2点` vs `2 点`) flagged as drift, forcing wrong-spacing reverts; `p99.9 spikes` parsed as phantom `9 s`; `50,000` split at the comma; top-level `import yaml` broke bare `python3` runs of `--mode fact-check`.

### 6.3 v1.2.x Changes

1. `scripts/validate.py`: structural-numbering stripping (headings, `Decision N:`, `第 N 章`, cross-reference `N 節のとおり` — never quantity nouns like `8 节点`), comma/thousands-aware number tokens, unit-spelling normalization (`90-second` ≡ `90 seconds`, `2点` ≡ `2 点`), strict number+unit comparison (unit swap `240 ms → 240 s` fails), lazy PyYAML import so `fact-check` runs on bare `python3`.
2. `SKILL.md` Step 3/4/7 + `references/{chinese,english,japanese}.md` + `rules/{zh-CN,ja}.yaml`: calque-gloss collapse per language, first-mention English anchor retention in Chinese, false-contrast foil deletion (not softening), report anti-sandwich/anti-stub-subsection rules, clean delivery contract (no validator narration anywhere, same-language adjustment notes).
3. `scripts/fact-check-regressions.sh`: 10 durable regression fixtures (unit swaps must fail; spacing/heading/p99.9/thousands/counter/cross-reference cases must pass).

### 6.4 Corrected Scorecard (strict primary-model judgment, /40)

| Case          | R1 `v1.1.0` | R2 `v1.2.0` | R3 `v1.2.1` (re-run)           | Residual defects at final state                                                                                                     |
| ------------- | ----------- | ----------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `zh_frontend` | 35          | 40          | —                              | none observed                                                                                                                       |
| `zh_backend`  | 34          | 40          | —                              | none observed                                                                                                                       |
| `zh_arch`     | 36          | 37          | **39**                         | mild one-line preface (`以下为改写后的技术报告：`) — no exit codes/paths                                                            |
| `en_frontend` | 36          | 38          | **40**                         | none — starts directly at `# Title`, plain fidelity claims                                                                          |
| `en_backend`  | 38          | 40          | —                              | none observed                                                                                                                       |
| `en_arch`     | 36          | 40          | —                              | none observed                                                                                                                       |
| `ja_frontend` | 36          | 36          | **37**                         | **still opens with verification preface** (`検証を通過しました…`); otherwise calque collapse + strawman deletion + structure landed |
| `ja_backend`  | 37          | 36          | **37**                         | **still opens with verification preface**; 発生日時 repeated between 概要 bullet and §2 sentence                                    |
| `ja_arch`     | 35          | 37          | —                              | `認証処理を処理している` doubling; `## 4. まとめ` retained (defensible: no comparison table closes that report)                     |
| **Mean**      | **35.89**   | **38.22**   | **38.89** (blended best state) |                                                                                                                                     |

- Verification-narration leak class: **9/9 (R1) → 4/9 (R2) → 1 strict + 1 mild of 4 re-run cases (R3)**. The leak is now concentrated in Japanese outputs on this model; recorded as a known limitation in `SKILL.md` Gotchas with a pipeline post-strip remedy instead of further prompt inflation.
- Tool-call efficiency: `en_backend` 14 → 7 (R1 → R2) once `p99.9`/heading-number false positives were fixed; `ja_frontend` 12 → 5.

### 6.5 Re-running the Field Trial

```bash
pi --model zai/glm-5.3-flashx --no-session --no-skills \
   --skill skills/natural-writing --mode json -p "<case prompt>"
```

Keep total concurrency ≤ 2 (the zai endpoint returns `429 code 1302` above that) and run cases sequentially or with per-case scratch directories when the agent writes temporary fact-check files.

---

## 7. Reproducing the Evaluation

```bash
# 1. Verify package integrity, 1-level link depth, and zero n-gram leakage
uv run skills/natural-writing/scripts/validate.py

# 2. Fact-check semantic regressions (unit drift, structural numbering, CJK spacing)
bash skills/natural-writing/scripts/fact-check-regressions.sh

# 3. Scan prose from stdin or file for review_only symptom signals
printf '各位对账期延迟的担忧已稳稳地接住！\n' | uv run skills/natural-writing/scripts/validate.py --mode scan --file - --lang zh-CN

# 4. Verify zero numeric/terminology drift on rewrites
uv run skills/natural-writing/scripts/validate.py --mode fact-check \
  --original "将汇总时长由 42 秒缩短至 5 秒内" \
  --rewritten "把汇总时长从 42 秒缩短到 5 秒以内"
```

---

## 8. improve-skill Pass: v1.2.1 → v1.3.0

Method: `improve-skill` phases 0–5. The pre-edit snapshot of v1.2.1 is the baseline; each trial run is a fresh `pi` process (`zai/glm-5.3-flashx`, `--no-skills --skill <dir> --mode json`) in an isolated scratch directory outside the repository, which mimics an installed skill. The primary model scored the static audit and read the outputs; objective assertions were graded by script. Harnesses and raw artifacts live in `~/.local/share/natural-writing-evals/` (`trigger_eval.py`, `trial_run.py`, `trial_analyze.py`, per-batch directories).

### 8.1 Scorecard (strict static audit, same-context)

| Dimension             | Before | After  | Evidence                                                                                                                                                                                                                              |
| --------------------- | ------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Spec compliance     | 5      | 5      | `check-skills.sh` PASS                                                                                                                                                                                                                |
| 2 Description         | 4      | 4      | Trigger keywords added at the user's request; the trigger eval (8.3) shows no measurable change                                                                                                                                       |
| 3 Context economy     | 3      | 4      | SKILL.md 23,508 → 21,470 characters (−8.7%); language-specific gloss rules, report rules, the Output column, and a model-specific Gotcha removed or relocated; still about 5.4k tokens at 4 characters per token, above the 5k target |
| 4 Structure           | 4      | 5      | Worked Example is its own subsection; Output Contract opening split into plain sentences                                                                                                                                              |
| 5 Instruction quality | 3      | 4      | One-off example removed (AP-23); Step 9 gives both commands and an absolute skill-directory path; contract rewritten as a positive instruction with its reason                                                                        |
| 6 Guardrails          | 4      | 5      | Layer 3 symptom `symptom.all.verification_narration_preface` is wired into Step 9 as a scan step; Gate 2 checks the first line                                                                                                        |
| 7 Composability       | 4      | 4      | `--help` now lists exit codes; `fact-check` still echoes unbounded `original_invariants`, so no score change                                                                                                                          |
| 8 Cross-platform      | 3      | 4      | Skill-directory path instead of a repository path; model name removed from SKILL.md                                                                                                                                                   |
| **Total**             | **30** | **35** | The earlier 39/40 reading was too generous                                                                                                                                                                                            |

### 8.2 Trial run: improved vs baseline

Assertions per run: A1 first non-empty line starts with `#`; A2 no validator, gate, scan, or scratch-path narration anywhere; A3 a validator call ran without a start error; A4 all draft numbers survive (`fact-check` of draft vs document body).

| Set                                                                    | Runs | A1    | A2    | A3    | A4    |
| ---------------------------------------------------------------------- | ---- | ----- | ----- | ----- | ----- |
| Baseline v1.2.1 (tuning cases + held-out)                              | 26   | 17/26 | 20/26 | 22/26 | 26/26 |
| Improved, final wording (tuning cases)                                 | 10   | 10/10 | 10/10 | 10/10 | 10/10 |
| Improved, final wording (held-out: `zh_backend`, `en_arch`, `ja_arch`) | 6    | 6/6   | 6/6   | 6/6   | 6/6   |

Pooled improved (16 runs) vs baseline (26 runs), one-sided Fisher exact: A1 p = 0.007, A2 p = 0.044, A3 p = 0.134 (not significant). A4 is flat. Content checks on the document body (residual slang, glosses, calques, strawman softening) show 0 hits for both versions, so moving the language rules out of SKILL.md did not regress the content defects they cover.

Intermediate wording versions, kept for transparency:

| Version                                                                                 | Runs | A1    | A2    | What happened                                                           |
| --------------------------------------------------------------------------------------- | ---- | ----- | ----- | ----------------------------------------------------------------------- |
| First v1.3.0 draft (negative phrasing, validator named in Gate 2 and the failure table) | 10   | 6/10  | 6/10  | Worse than baseline on the first-line check                             |
| Correction 1 (positive first-line rule, note scope left implicit)                       | 10   | 10/10 | 2/10  | The first-line leak moved into the closing note (`fact-check 検証済み`) |
| Correction 2 (note must not name the checking tool)                                     | 10   | 10/10 | 10/10 | Final wording                                                           |

Caveats: one model, small samples, and the wording was tuned on the 10 tuning runs before the 6 held-out runs; the `scan` detector patterns were extended using leaks seen in these runs (in-sample recall 8/9 and 7/7 on the earlier batches), so its out-of-sample recall is unknown.

### 8.3 Trigger eval (description changed)

16 queries (8 should trigger across zh/en/ja, 8 should not, including sibling-skill near-misses), 2 runs each, siblings `agent-report`, `review-and-fix`, `test-design` loaded.

| Description | Should trigger | False triggers |
| ----------- | -------------- | -------------- |
| v1.2.1      | 15/16          | 0/16           |
| v1.3.0      | 15/16          | 0/16           |

One miss each, on different queries. The old description already reached the ceiling of this query set, so the change is neutral. Keep the new wording only for its explicit keywords; a harder query set is needed to measure a gain.

### 8.4 Prose-quality read (primary model, not blind)

Added after a review pointed out that 8.2 is machine-checked only. The primary model read one baseline and one improved output for each of `ja_frontend`, `zh_backend`, and `ja_arch` and scored them out of 40 with `evals/rubric.md` in mind. The reader knew which file was which, and each cell is a single sample, so this is a spot check, not a comparison.

| Case          | Baseline | Improved | Main observations                                                                                                                                                                                                                                                                                         |
| ------------- | -------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ja_frontend` | 38       | 36       | Both collapse `メモリの足跡（メモリフットプリント）`, drop the strawman, and keep the real contrast. Improved adds a rationale the draft never states ("対策の焦点は演算ループの高速化とそのメインスレッドからの分離に置いた")                                                                            |
| `zh_backend`  | 30       | 34       | Baseline adds claims absent from the draft (the migration flow is "reusable for later shard expansion", the switch is "invisible to the business", a rationale for sharding). Improved upgrades "重视" to "牵头完成了排查、止血与架构改造" but also tells the reader to fill in the missing incident date |
| `ja_arch`     | 33       | 37       | Baseline opens with a status line, adds a rationale for the 5-minute expiry, and adds a comparison table whose cells ("誤遮断: なし" for the origin-lookup design) the draft does not state. Improved stays inside the draft and collapses `トークンの回転（ローテーション）`                             |
| Mean          | 33.7     | 35.7     | Gap of 2 points on 3 pairs; not evidence of a difference                                                                                                                                                                                                                                                  |

Findings: moving the gloss and anchor rules out of SKILL.md caused no visible readability or register regression in these six outputs. Both versions still add inferences the source does not state (Hard Rule 1 drift); this is the larger open defect and neither the trial assertions nor the banned-phrase grep measure it. The improved `ja_frontend` note opens its fidelity claim with "検証の結果", a mild leftover that no assertion flags.

### 8.5 Deferred

- A query set hard enough to separate descriptions (indirect phrasing, mixed-language prompts).
- Bound the `original_invariants` echo in `fact-check` output (Dimension 7).
- Cross-model replication of 8.2; every number here comes from `glm-5.3-flashx`.
- Step 9 runs `scan` on the document before the adjustments note is written, so it never sees the note where tool citations appeared in earlier wording. Compose the note first, then scan the complete reply. Not applied because the two allowed correction cycles were used and the current wording reached 16/16.
- Add an objective assertion for unstated claims (new numbers are caught by `fact-check`, new rationale sentences are not); the prose read in 8.4 found them in 4 of 6 outputs.
- The held-out runs (8.2) used the complete v1.3.0 package, not the final contract sentence alone; that is the ship decision, but it cannot attribute the effect to one change.
