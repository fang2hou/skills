# Pragmatic Anomalies in AI and Human Prose

Many severe writing defects occur not in syntax or spelling, but in **pragmatics**—how sentences function in a communicative context between a writer and a reader (`grice-1975`, `brown-levinson-1987`, `lakoff-johnson-1980`). This reference analyzes the root mechanisms behind four representative case classes required for accurate diagnosis and editing.

Contents:

- [1. Case A: Metaphor, Register, and Intimacy Mismatch ("稳稳地接住你")](#1-case-a-metaphor-register-and-intimacy-mismatch-稳稳地接住你)
- [2. Case B: False Adversative Staging ("不是……而是……" / "Not X, but Y")](#2-case-b-false-adversative-staging-不是而是--not-x-but-y)
- [3. Case C: Colloquial Overcorrection ("绝绝子 / 狠狠拿捏 / Real talk")](#3-case-c-colloquial-overcorrection-绝绝子--狠狠拿捏--real-talk)
- [4. Case D: Taxonomy of 15 Pragmatic and Rhetorical Pathologies](#4-case-d-taxonomy-of-15-pragmatic-and-rhetorical-pathologies)
- [5. Contextual Decision Matrix](#5-contextual-decision-matrix)

---

## 1. Case A: Metaphor, Register, and Intimacy Mismatch ("稳稳地接住你")

### Phenomenon

In Chinese LLM outputs and stylized workplace/assistant prose, expressions such as:

- `"我会稳稳地接住你的情绪。"`
- `"你的表达，我稳稳地接住了。"`
- `"这个需求我们已经稳稳接住并闭环了。"`

are frequently used to mean simply _"I understand your point"_ or _"We have taken on this task."_

### Multi-Layer Linguistic Diagnosis

Why does this expression jar the reader in ordinary professional or informational communication? Over-frequency is only a surface symptom; five deeper mechanisms fail simultaneously:

1. **Conceptual Metaphor Mapping (`lakoff-johnson-1980`)**:
   - **Source Domain**: Physical catching of a falling, fragile, or heavy object (`接住`), modified by physical equilibrium (`稳稳地`).
   - **Target Domain**: Receiving an informational query or acknowledging a speaker's statement.
   - **Mapping Failure**: Routine communication is a collaborative exchange of propositions, not a crisis in which the speaker is falling or hurling a fragile burden that requires heroic physical stabilization by the listener.
2. **Semantic Precision (`orwell-1946`, `lv-zhu-1952`)**:
   - Saying `"我稳稳地接住了你的问题"` leaves the actual communicative state vague: Did you understand the root cause? Did you agree with the premise? Are you scheduling the fix? The spatial metaphor obscures the concrete action.
3. **Collocation Naturalness (`lv-zhu-1952`)**:
   - In standard Chinese, `接住` collocates with physical projectiles (`接住篮球`, `接住掉落的杯子`) or colloquially with a fast conversational turn (`接住话茬`). Pairing `稳稳地接住` with abstract nouns like `你的表达` or `你的诉求` is a pop-psychology calque (derived from therapeutic _holding environment_ / _emotional containment_).
4. **Social Distance and Face Calculus (`brown-levinson-1987`)**:
   - Using therapeutic containment language presupposes an asymmetric caregiver–client or intimate partner relationship (very low Social Distance $D$, high emotional vulnerability). Deploying it in an engineering ticket, customer support reply, or analytical discussion violates the reader's **Negative Face** (autonomy and professional boundary) through unsolicited emotional intimacy.
5. **Performative Self-Aggrandizement (`grice-1975` Maxim of Manner)**:
   - The adverb `稳稳地` spotlights the speaker's own poise and reliability rather than addressing the reader's problem.

### Context-Dependent Verdict

- **Rewrite in professional, technical, or general informational prose**:
  - ❌ `"你的表达我稳稳地接住了，接下来我们看怎么改。"`
  - ✅ `"我明白你的意思了。你希望重点解决的是……"` or `"核心问题在于……"`
- **Keep in legitimate contexts (Never ban `接住` globally)**:
  - **Physical action**: `"守门员起跳，稳稳地接住了这记高空传球。"` (Literal source domain — **Keep**)
  - **Counseling / psychological support**: In a grief-support or psychotherapy reflection where emotional containment is the explicit subject (`"好的咨询师不会急于给建议，而是先接住来访者失控的焦虑"` — **Keep**)
  - **Conversational idiom**: `"台上演员忘词时，搭档自然地接住了话头。"` (Idiomatic collocation — **Keep**)

---

## 2. Case B: False Adversative Staging ("不是……而是……" / "Not X, but Y")

### Phenomenon

Correlative contrastive constructions—Chinese `不是……而是……` (`并非……而是……`, `不只是……更是……`), English `not X, but Y` (`it's not merely X; it's Y`), and Japanese `〜ではなく、むしろ〜だ` (`単なる〜ではなく、〜である`)—are completely grammatical and indispensable in human reasoning.

However, models overuse them to manufacture drama:

- `"这不是一次简单的配置调整，而是一场深刻的架构变革。"`
- `"我们需要的不是答案，而是思考。"`
- `"It is not just a database migration; it is a reimagining of how data flows."`

### Multi-Layer Linguistic Diagnosis

1. **Presupposition and Strawman Negation (`grice-1975` Maxim of Relation & Quantity)**:
   - A correlative negation `Not X, but Y` pragmatically presupposes that the reader (or a salient interlocutor) believes, expects, or risks confusing the target with $X$.
   - When $X$ is a trivial strawman nobody claimed (_"not a simple tweak"_), the negative branch carries **zero information bits**. Its sole function is theatrical staging: making $Y$ sound profound by contrasting it against a fabricated miniature foil.
2. **False Dichotomy (`orwell-1946`, `pinker-2014`)**:
   - In `"我们需要的不是答案，而是思考"`, _answers_ and _thinking_ are not mutually exclusive opposites; thinking is the means to an answer. The syntax asserts a logical opposition that the semantics do not support.
3. **Macro-Level Cadence Fatigue (`fowler-1926`)**:
   - Even when individual contrasts are defensible, repeating `Not X, but Y` three times on a single page turns prose into a monotonous rhetorical formula.

### Five-Point Contextual Test for Adversative Contrasts

Before keeping or removing a `Not X, but Y` (`不是……而是……`) construction, ask:

1. **Real Opposition**: Are $X$ and $Y$ genuinely incompatible or easily confused in this domain?
2. **Informative Negation**: Does ruling out $X$ prevent a plausible reader mistake (e.g., `"The flag takes a file path, not a directory URL"`)?
3. **Proportional Scale**: Is $Y$ stated at its actual factual scale rather than inflated into a grandiose slogan?
4. **Directness Test**: If we delete `Not X, but` and state $Y$ directly, is any meaning lost?
5. **Document Density**: Does this construction appear repeatedly across adjacent paragraphs?

### Context-Dependent Verdict

- **Rewrite when negation is theatrical staging**:
  - ❌ `"这不仅是一次版本升级，更是一次开发范式的全面跃迁。"`
  - ✅ `"这次 2.0 版本升级调整了插件接口，将构建耗时缩短了 40%。"`
- **Keep when negation disambiguates or corrects a real belief**:
  - ✅ `"故障原因不是网关超时，而是下游鉴权服务的证书在零点过期。"` (Rules out the primary suspect hypothesis during incident triage — **Keep**)
  - ✅ `"Use `git revert`, not `git reset --hard`, because this branch is already shared with the team."` (Prevents a destructive mistake — **Keep**)

---

## 3. Case C: Colloquial Overcorrection ("绝绝子 / 狠狠拿捏 / Real talk")

### Phenomenon

When users instruct an AI to _"write naturally, concisely, and without AI flavor"_, models frequently misinterpret **"natural"** as **"hyper-casual, slang-heavy, or over-familiar"**:

- Chinese: `"我直接给你全搞完。"`, `"这个方案真的绝绝子，咱们把性能狠狠拿捏住。"`, `"说白了就是这么回事儿，懂的都懂。"`
- English: `"Look, real talk: this config is a total no-brainer and crushes latency."`
- Japanese: `"ぶっちゃけ、この設定でいい感じに爆速になります。"`

### Multi-Layer Linguistic Diagnosis

1. **Conflation of Medium and Register (`ye-shengtao-1934`, `gowers-1954`, `bunkacho-2022`)**:
   - Language varies along two orthogonal axes:
     - **Pretentious / Prefabricated vs. Authentic / Direct** (Clarity axis)
     - **Formal / Written (`书面语 / 文語的`) vs. Casual / Spoken (`口语 / 俗語`)** (Register axis)
   - AI boilerplate sits in the **Pretentious + Formal** quadrant. When told to leave that quadrant, an uncalibrated model jumps diagonally into **Performative + Slangy** instead of moving horizontally into **Direct + Register-Appropriate**.
2. **Positive-Politeness Overreach (`brown-levinson-1987`)**:
   - Slang and in-group memes (`绝绝子`, `狠狠拿捏`, `懂的都懂`) are solidarity markers restricted to low-distance ($D \approx 0$) peer groups. Using them in technical documentation, analytical essays, or professional assistance fabricates a fake persona—swapping "robotic stiffness" for "cringeworthy fellow-kids performance."
3. **Loss of Semantic Resolution (`orwell-1946`)**:
   - Slang predicates like `搞完`, `拿捏`, `一把梭`, `crushed it`, and `いい感じにやる` are just as vague as bureaucratic operators (`进行赋能`): neither tells the reader what concrete action occurred.

### Core Principle

- **Natural $\neq$ Colloquial filler** (`自然不等于口水话`)
- **Concise $\neq$ Rough or telegraphic** (`简洁不等于粗糙`)
- **Warm/Accessible $\neq$ Over-familiar** (`亲切不等于过度熟络`)

---

## 4. Case D: Taxonomy of 15 Pragmatic and Rhetorical Pathologies

Every common AI writing symptom maps to a specific violation of human pragmatic, rhetorical, or syntactic principles:

| #   | Pathology                            | Underlying Principle Violated                                                       | Diagnostic Mechanism & Why It Hurts the Reader                                                                                               |
| --- | ------------------------------------ | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Unnecessary self-reference**       | `core.concision.information_density` (`pinker-2014` Classic Style)                  | Narrating the writer's own act (_"In this response, I will analyze..."_, `"接下来我将从三个方面阐述"`) blocks the windowpane to the subject. |
| 2   | **Empty praise and validation**      | `core.pragmatics.social_distance_and_register` (`grice-1975` Quantity/Quality)      | Sycophantic openers (_"That's a profound and insightful question!"_, `"你敏锐地捕捉到了核心！"`) delay the answer and ring hollow.           |
| 3   | **Over-comforting / forced empathy** | `core.pragmatics.social_distance_and_register` (`brown-levinson-1987`)              | Unsolicited therapy-speak (_"我非常理解你此刻的焦虑与无助"_) on a routine technical bug crosses social boundaries ($D$).                     |
| 4   | **Mechanical triads & parallelism**  | `core.cohesion.old_before_new` (`fowler-1926`)                                      | Forcing every list or paragraph into three symmetrical items pads two real ideas with a third synonym.                                       |
| 5   | **Zero-information summaries**       | `core.concision.information_density` (`grice-1975` Quantity)                        | Closing paragraphs (`"综上所述，X 既有机遇也有挑战，需要我们持续探索"`) repeat what was just read without adding a decision or consequence.  |
| 6   | **Hollow grand narratives**          | `core.clarity.concrete_over_vague` (`orwell-1946` Pretentious diction)              | Opening a specific technical note with `"在数字化浪潮席卷全球的今天"` or `"Since the dawn of modern computing"` wastes context.              |
| 7   | **Incongruous metaphors**            | `core.rhetoric.figurative_coherence` (`lakoff-johnson-1980`)                        | Mapping ordinary tasks onto war, therapy, or cosmic alchemy (`"打赢数据治理攻坚战"`, `"catalyzing a tapestry"`).                             |
| 8   | **Excessive nominalization**         | `core.syntax.actors_and_actions` (`williams-1981`, `lv-zhu-1952`, `kinoshita-1981`) | Turning verbs into abstract nouns (`"通过对索引的重建实现了延迟的降低"`, `"遅延の削減の実現を行う"`) hides agency and clogs syntax.          |
| 9   | **Translationese (欧化/翻訳調)**     | `zh.syntax.europeanized_prepositions_and_passives` / `ja.syntax.translationese_*`   | Copying English passive, pronoun, and prepositional frames into Chinese or Japanese where native word order is cleaner.                      |
| 10  | **Pseudo-technical jargon**          | `core.clarity.meaning_chooses_word` (`orwell-1946`)                                 | Coining buzzwords (`颗粒度、抓手、赋能、闭环、打法、心智`, `synergistic paradigm`) to mimic expertise without falsifiable meaning.           |
| 11  | **Meaningless emphasis**             | `core.pragmatics.epistemic_calibration` (`strunk-white-1959`)                       | Sprinkling `极其、真正、本质上、至关重要的、crucial、pivotal、まさに` on every sentence, which devalues all emphasis.                        |
| 12  | **Unmotivated connectives**          | `core.logic.earned_contrast_and_connectives` (`pinker-2014`, `bunkacho-2022`)       | Starting consecutive sentences with `此外、同时、然而、因此` or `まず、次に、さらに、したがって` when clauses have no such logical link.     |
| 13  | **Manufactured suspense**            | `core.concision.information_density` (`grice-1975` Manner)                          | Staged cliffhangers (_"Here is where things get interesting"_, `"但真相果真如此吗？答案可能出乎所有人意料"`) in informational prose.         |
| 14  | **Over-inferring user intent**       | `core.pragmatics.epistemic_calibration` (`brown-levinson-1987`)                     | Psychoanalyzing the reader (_"你之所以这么问，背后其实是担心……"_) instead of answering the stated question.                                  |
| 15  | **Over-compression losing facts**    | `core.fidelity.preserve_voice_and_facts` (`orwell-1946` Rule vi)                    | Deleting necessary boundary conditions, units, or exceptions in a misguided pursuit of ultra-short sentences.                                |

---

## 5. Contextual Decision Matrix

Use this matrix during Step 5 and Step 6 of the workflow to decide whether an expression should be rewritten or preserved:

| Expression Class                   | Rewrite When...                                                                | Preserve When...                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| **Metaphor (`接住`, `tapestry`)**  | Source domain clashes with register/social distance or replaces a clearer verb | Literal action, domain-settled technical term, or coherent literary/therapeutic frame  |
| **Contrast (`不是…而是…`)**        | Negative half is a strawman nobody believed, used only for dramatic inflation  | Negative half rules out a real misconception or contrasts two concrete options         |
| **Passive (`被…`, `is X-ed`)**     | Agent is known and active voice is clearer, or `被` is a stiff English calque  | Patient is the persistent paragraph topic, actor is unknown/irrelevant, or idiom needs |
| **Colloquialism / Slang**          | Document is technical, analytical, official, or general professional prose     | Document is character dialogue, personal chat, or quotes a speaker verbatim            |
| **Hedges (`may`, `〜と思われる`)** | Stacked defensively (`could potentially`) or blurring verified facts (`事実`)  | Expressing genuine epistemic uncertainty with its basis stated (`意見・推測`)          |
| **Three-item list (Triad)**        | Items 2 and 3 largely repeat Item 1 for rhythmic padding                       | All three items represent distinct, non-overlapping components or facts                |
