# Layer 2: Simplified Chinese (`zh-CN`) Realization Guide

This guide translates the universal principles in `references/principles.md` into the grammar, collocation patterns, register norms, and rhetorical traditions of modern Simplified Chinese (`zh-CN`). Load this file whenever generating, reviewing, or rewriting Chinese prose, alongside `rules/zh-CN.yaml`.

Contents:

- [1. Typological Foundations of Natural Chinese](#1-typological-foundations-of-natural-chinese)
- [2. Replacing Empty Light Verbs with Direct Predicates (`zh.syntax.empty_light_verbs`)](#2-replacing-empty-light-verbs-with-direct-predicates-zhsyntaxempty_light_verbs)
- [3. Curing Malignant Europeanization (`zh.syntax.europeanized_prepositions_and_passives`)](#3-curing-malignant-europeanization-zhsyntaxeuropeanized_prepositions_and_passives)
- [4. Metaphor Coherence and Social Distance (`zh.pragmatics.metaphor_and_intimacy_mismatch`)](#4-metaphor-coherence-and-social-distance-zhpragmaticsmetaphor_and_intimacy_mismatch)
- [5. Auditing Adversative Contrasts (`zh.logic.false_adversative_contrast`)](#5-auditing-adversative-contrasts-zhlogicfalse_adversative_contrast)
- [6. Register Calibration: Avoiding Both Officialese and Slang (`zh.register.colloquial_overcorrection`)](#6-register-calibration-avoiding-both-officialese-and-slang-zhregistercolloquial_overcorrection)
- [7. Collocation Integrity (`zh.collocation.natural_verb_object_pairing`)](#7-collocation-integrity-zhcollocationnatural_verb_object_pairing)
- [8. Parallelism and Four-Character Idioms (`zh.rhetoric.parallelism_and_four_char_cliche`)](#8-parallelism-and-four-character-idioms-zhrhetoricparallelism_and_four_char_cliche)
- [9. Technical Terminology and Calques (`zh.terminology.technical_precision_and_calques`)](#9-technical-terminology-and-calques-zhterminologytechnical_precision_and_calques)
- [10. Punctuation and CJK–Latin Spacing](#10-punctuation-and-cjklatin-spacing)

---

## 1. Typological Foundations of Natural Chinese

As established by Lv Shuxiang, Zhu Dexi (`lv-zhu-1952`, `zhu-dexi-1982`), Wang Li (`wang-li-1943`), and Yu Kwang-chung (`yu-kwangchung-1987`), modern Chinese differs structurally from English in four ways:

1. **Verb-centered clauses**: Chinese verbs do not require morphological nominalization to serve as subjects or objects (`研究这个问题很容易`), and serial verb chains (连动式) carry sequential actions cleanly without heavy prepositional scaffolding.
2. **Subject-predicate predicates (`主谓谓语句`, `zhu-dexi-1982`) and topic-comment flow**: Once a topic is established at the start of a sentence (`这批配置文件，我们已经校验过了`), Chinese does not need a passive marker (`被`) or repeated pronouns (`它们`) in subsequent clauses.
3. **Parataxis (意合) over hypotaxis (形合)**: Chronological and causal order (`Condition → Action → Result`) often makes explicit subordinating wrappers (`当……的时候`, `如果……的话`) redundant.
4. **Disyllabic and quadrisyllabic cadence**: Chinese rhythm balances two-syllable and four-syllable units; stacking five or six abstract nouns modified by multiple `的` particles chokes the clause's breath.

---

## 2. Replacing Empty Light Verbs with Direct Predicates (`zh.syntax.empty_light_verbs`)

In《语法修辞讲话》(`lv-zhu-1952`), Lv and Zhu identify the overuse of **omnipotent light verbs (万能动词 / 形式动词)**—such as `进行、加以、作出、予以、开展、实现`—as a primary source of wooden Chinese prose. These operators strip a real verb of its predicative force and turn it into an abstract noun object.

| Unnatural Nominalized Operator                 | Natural Verbal Predicate           | Mechanism                                                             |
| ---------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------- |
| `对数据库索引进行了重建，实现了查询延迟的降低` | `重建数据库索引后，查询延迟降低了` | Restores `重建` and `降低` as active finite predicates                |
| `我们将对该异常情况加以排查并作出响应`         | `我们会排查这一异常并及时处理`     | Cuts bureaucratic operators `加以` and `作出`                         |
| `针对用户反馈的问题开展深入的讨论`             | `深入讨论用户反馈的问题`           | Turns `深入` back into an adverbial modifier (`地/Ø`) before the verb |
| `本模块完成了对请求参数的校验工作`             | `本模块负责校验请求参数`           | Removes the empty shell `完成了对……的工作`                            |

**When to keep**: Keep a formal light verb only in statutory or regulatory formulations where fixed legal phrasing requires it (`依法予以行政处罚`), or when the nominalized object takes an indispensable quantitative modifier (`进行了三次全量压测`).

---

## 3. Curing Malignant Europeanization (`zh.syntax.europeanized_prepositions_and_passives`)

Translationese (翻译腔 / 恶性西化, `wang-li-1943`, `yu-kwangchung-1987`) enters Chinese when English prepositional phrases, passive voice, and relative clauses are mapped word-for-word:

1. **Prepositional wrappers**:
   - ❌ `在没有经过校验的情况下，配置文件被系统加载了。`
   - ✅ `系统加载了未经校验的配置文件。` (Or topic-comment: `配置文件未经校验就加载进了系统。`)
   - ❌ `通过对缓存策略的调整，我们使得接口吞吐量得到了翻倍。`
   - ✅ `调整缓存策略后，接口吞吐量翻了一倍。`
   - ❌ `关于是否升级内核的这个问题，对于目前的生产环境而言是比较敏感的。`
   - ✅ `目前的生产环境对升级内核比较敏感。`
2. **Stacked pre-nominal `的` chains**:
   - In Chinese, every relative clause precedes the head noun. More than two `的` modifiers before a single noun forces the reader to hold dangling qualifiers in working memory without knowing what noun they modify.
   - ❌ `这是一个由核心基础架构团队在去年第三季度针对高并发写入场景设计并落地的分布式限流组件。`
   - ✅ `这个分布式限流组件由核心基础架构团队在去年第三季度设计上线，专用于高并发写入场景。`
3. **Unmotivated `被` passives and `-性 / -化 / -度` noun stacks**:
   - ❌ `该方案的可读性与可维护性得到了显著的提升。`
   - ✅ `新方案更易读，也更好维护。`

---

## 4. Metaphor Coherence and Social Distance (`zh.pragmatics.metaphor_and_intimacy_mismatch`)

Chinese AI prose frequently imports pop-psychology or corporate-cult metaphors into ordinary communication (`lakoff-johnson-1980`, `brown-levinson-1987`):

- **Therapeutic / physical catching metaphors**: `稳稳地接住你的情绪`, `接住你的诉求`, `兜住底线`, `把问题收口`.
- **Corporate buzzword clusters (互联网黑话)**: `赋能、抓手、闭环、沉淀、打通、拉齐、颗粒度、底层逻辑、顶层设计、组合拳、心智、水位、链路（非网络场景）`.

| Context                         | Unnatural / Incongruous                                                        | Natural Revision                                                               | Verdict   |
| ------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | --------- |
| Technical Q&A / Workplace reply | `你的顾虑我稳稳地接住了，下面我们对齐一下颗粒度。`                             | `我理解你的顾虑，下面我们核对一下具体细节。`                                   | `rewrite` |
| Product documentation           | `通过多维度的策略组合拳，为开发者深度赋能，打造极致的生态闭环。`               | `提供命令行工具与 SDK，帮助开发者在同一工作流内完成构建、测试与发布。`         | `rewrite` |
| Sports / Physical narrative     | `外野手全速冲刺，在界墙前稳稳地接住了这记高飞球。`                             | `外野手全速冲刺，在界墙前稳稳地接住了这记高飞球。`                             | `keep`    |
| Psychological counseling essay  | `面对处于急性哀伤期的来访者，咨询师首先要接住对方的崩溃感，而非急于分析原因。` | `面对处于急性哀伤期的来访者，咨询师首先要接住对方的崩溃感，而非急于分析原因。` | `keep`    |

---

## 5. Auditing Adversative Contrasts (`zh.logic.false_adversative_contrast`)

Correlative patterns (`不是……而是……`, `并非……而是……`, `不只是……更是……`, `与其说……不如说……`) are valid Chinese syntax when two propositions stand in genuine opposition or when correcting a specific misconception. They become unnatural when used as a rhetorical trampoline to inflate an ordinary statement:

- ❌ **False contrast (Rewrite)**: `这次重构不是简单的代码清理，而是一次面向未来的架构涅槃。`
  - **Fix**: `这次重构清理了冗余模块，并将服务拆分为三个独立部署的单元。`
- ✅ **Genuine disambiguation (Keep)**: `限流阈值按每个租户的并发连接数计算，而不是按每秒请求数（QPS）计算。`
  - **Why keep**: Explicitly prevents engineers from configuring the wrong metric.

---

## 6. Register Calibration: Avoiding Both Officialese and Slang (`zh.register.colloquial_overcorrection`)

Following Ye Shengtao (`ye-shengtao-1934`), natural Chinese (`辞达`) sits between stiff bureaucratic formulas (`官样套话`) and performative internet slang (`网络口水话`):

| Register Defect               | Examples to Avoid in Professional/Expository Prose                          | Natural Standard Chinese Equivalent                                |
| ----------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Internet slang / memes**    | `绝绝子、狠狠拿捏、直接给你全搞完、一把梭、yyds、家人们谁懂啊、真香`        | `效果显著、准确掌握、一次性全部处理、直接全量执行`                 |
| **Casual spoken shorthand**   | `服务挂了、节点崩了、请求卡死了、深夜发版没人盯、把老接口干掉`              | `服务异常退出、节点不可用、请求阻塞、深夜无人值守发布、下线旧接口` |
| **Performative chat fillers** | `说白了、其实吧、讲真、不夸张地说、你看啊`                                  | State the proposition directly without conversational particles    |
| **Chatbot customer-service**  | `您好！非常高兴为您解答！希望以上内容对您有所帮助，如有疑问请随时告诉我哦~` | Omit wrapper entirely; begin with the answer and end on the point  |

---

## 7. Collocation Integrity (`zh.collocation.natural_verb_object_pairing`)

Check that every verb and object pair natively (`lv-zhu-1952`):

- ❌ `培养团队的技术水平` $\to$ ✅ `提高团队的技术水平` or `培养团队的工程能力` (`培养` pairs with organisms/habits/talent, not a scale/level `水平`).
- ❌ `拉齐各部门的认知水位` $\to$ ✅ `统一各部门对需求的理解` or `同步各部门的信息`.
- ❌ `沉淀出一套标准化的动作` $\to$ ✅ `总结出一套标准操作流程`.
- ❌ `强化了系统的低延迟` $\to$ ✅ `降低了系统延迟` or `保持了系统的低延迟`.

---

## 8. Parallelism and Four-Character Idioms (`zh.rhetoric.parallelism_and_four_char_cliche`)

1. **Settled four-character terms vs. decorative chains**:
   - Use four-character compounds when they are the concise, standard name for a concept: `向下兼容、平滑迁移、按需加载、故障隔离、循序渐进`.
   - Cut four-character chains that repeat the same idea three times for ceremonial sound:
     - ❌ `我们要统筹兼顾、协同推进、多措并举，确保迁移工作保质保量、平稳有序、万无一失地落地。`
     - ✅ `迁移前需先在预发环境验证回滚脚本，再按流量比例分批切换。`
2. **Breaking mechanical triads (三段式排比)**:
   - When a draft contains three parallel clauses (`它不仅是……更是……还是……`), check whether they express three distinct facts. If two of them are synonyms, collapse into one concrete sentence.

---

## 9. Technical Terminology and Calques (`zh.terminology.technical_precision_and_calques`)

In Chinese technical writing (`skills/html-report/references/writing-zh.md`):

- **Keep standard English terms in English** when Chinese engineers use the English term natively and coined translations sound bizarre: `tree-shaking` (not `摇树优化`), `release gate` (not `发布门禁`), `smoke test` (not `冒烟测试` in formal specs where `smoke test` is clearer, or use settled usage consistently), `blue-green deploy`, `fallback`, `workaround`, `dead-letter queue`.
- **Use settled Chinese engineering terms** instead of literal translations of English metaphors:
  - `灰度发布` (not `金丝雀发布` for _canary release_)
  - `主流程 / 正常路径` (not `快乐路径` for _happy path_)
  - `影响范围` (not `爆炸半径` for _blast radius_)
  - `唯一可信数据源` (not `单一事实来源` for _single source of truth_)
  - `合理性校验` (not `理智检查` for _sanity check_)
- **Distinguish first-mention English anchors from beginner definitions**:
  - **Keep** concise English original terms in parentheses on first mention when a technical draft uses them to anchor a concept (`脏矩形（Dirty Rectangle）`, `合成态锁（Composition Lock）`, `强制同步布局（Forced Synchronous Layout）`, `本地事务表（Transactional Outbox）`), then use the Chinese term alone on subsequent mentions.
  - **Cut** verbose textbook explanations in parentheses for basic terms (`幂等性（即多次执行结果一致）`, `背压（下游处理不过来时向上游反馈）`) when writing for engineering peers.
- **Technical report structural restraint**: In technical reports, avoid repeating the exact same metrics three times across `摘要` $\to$ `正文` $\to$ `结论/小结`, and do not create a `###` subheading for a single short sentence.

---

## 10. Punctuation and CJK–Latin Spacing

- Insert **one half-width space** between Chinese characters and Latin letters or Arabic numerals: `升级 Node 24`, `耗时 15 ms`, `节省 180 KB`.
- Do **not** add spaces adjacent to full-width Chinese punctuation (`，。：；？！（）“”《》`).
- Keep `%` and `°C` attached to the number: `内存占用下降 30%`.
- Use full-width curly quotes `“……”` (and `‘……’` nested inside) in Chinese sentences; keep half-width quotes inside inline code and commands.
- Avoid using `，即……` as a mechanical translation of English `, i.e.,`; connect clauses with a concrete verb (`耗时降至 50 ms，仅为原来的三分之一`), a colon, or parentheses.
