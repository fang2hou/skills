# Chinese Writing Guide (zh-CN)

Follow this guide together with [writing.md](writing.md) for every page with `lang="zh-CN"`. The reader is a senior engineer who reads technical English without effort.

## Spacing and punctuation

- Put one half-width space between Chinese characters and Latin letters or digits: `升级 zod 4`, `节省 180 KB`, `共 14 个文件`. Add no space next to full-width punctuation (`，。：；？！（）“”`). Keep `%` and `°C` attached to the number: `节省 30% 的内存`.
- In a short heading that ends with a number and a measure word, join them with `&nbsp;` (`3&nbsp;个`) so the balanced wrap cannot split them.
- Use full-width punctuation in Chinese sentences, with `“”` for quotes and `‘’` inside them. Keep half-width punctuation inside inline code, paths, commands, and English quotes.
- Inline code applies in Chinese text too: write 运行 `check-skills.sh` 后修改 `AGENTS.md`, not 运行 check-skills.sh 后修改 AGENTS.md. File names, paths, commands, and field names always go in `<code>`.

## Register

Plain Chinese means cutting empty phrases and padding, not writing like a chat message.

- No colloquial or slang verbs: 发版, 没人盯, 挂了, 崩了, 卡死, 兜底, 干掉, 一把梭.
- No corporate jargon: 赋能, 抓手, 闭环, 底层逻辑. Use 口径 only in its statistical sense (统计口径); for the basis of a judgment, write 依据.
- No shorthand metaphors coined for the occasion: 撞词, 贴线, 破线. Write 关键词重叠, 接近上限, 超出上限.
- No padded verb phrases: write 优化, not 进行优化; 一次性完成, not 一次性全量推进; 清洗数据, not 清洗并归整数据.
- Use a four-character term when it is the standard name for the idea (向下兼容, 平滑迁移, 按需加载, 故障隔离). Do not string idioms together for rhythm.

## Technical terms

- Keep common English terms in English: `tree-shaking`, `release gate`, `blue-green deploy`, `smoke test`, `fallback`, `workaround`, `dead-letter queue`. Do not coin 摇树优化 or 发布门禁.
- Keep English only for technical terms. Ordinary words go in Chinese: 同类 skill, not sibling; 小改动, not 小 edit; 开头先写用途, not 前置核心用途.
- Where Chinese engineering usage has a settled term, use it instead of a literal translation of the English metaphor: 灰度发布 for canary release, 主流程 for happy path, 影响范围 for blast radius, 时间窗口 for time window, 固定周期发布 for release train.
- Use standard terms such as 幂等, 背压, 熔断, and 最终一致性 as they are. Do not paraphrase them in everyday words or add a textbook definition in parentheses, unless the page is study material for beginners.

## Sentence shape

- Avoid `，即……` as a mechanical rendering of ", i.e.,". Connect with a verb (`耗时降至 50 ms，仅为原来的三分之一`), a colon, or parentheses.
- Drop translated frames such as 当……的情况下 and 通过对……的……实现了……, and drop 被 when the actor is clear. Put the condition before the result and prefer short clauses with verb predicates.

## Examples

| Avoid                                                   | Prefer                                                    | Why                                                              |
| ------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------- |
| 深夜发版没人盯                                          | 深夜无人值守发布                                          | 发版 is chat shorthand; 没人盯 implies neglect, not automation   |
| 服务挂了 / 节点崩了 / 卡死了 / 拿缓存兜底               | 服务异常退出 / 节点不可用 / 请求阻塞 / 降级到缓存         | Name the technical state instead of a casual word                |
| 把老接口干掉 / 一把梭全改了 / 一次性全量推进            | 下线旧接口 / 一次性完成                                   | Plain written verbs, without slang or bureaucratic padding       |
| 摇树优化 / 发布门禁 / 蓝绿部署                          | tree-shaking / release gate / blue-green deploy           | Engineers use the English term; a coined Chinese one reads oddly |
| 发布火车 / 金丝雀发布 / 快乐路径 / 爆炸半径             | 固定周期发布 / 灰度发布 / 主流程 / 影响范围               | Settled Chinese terms instead of literal metaphors               |
| 单一事实来源 / 理智检查                                 | 唯一可信数据源 / 合理性校验                               | Convey the meaning instead of the English words                  |
| 幂等性（多次执行与单次执行结果一致）                    | 幂等性                                                    | The reader knows the term                                        |
| 耗时 50 ms，即原来的三分之一                            | 耗时降至 50 ms，仅为原来的三分之一                        | A verb connects the clauses instead of `，即`                    |
| 当配置在没有经过校验的情况下被加载时                    | 加载未经校验的配置时                                      | No translated frame and no 被                                    |
| 无同域 sibling / 均为小 edit / 两条撞词 / 已贴线        | 没有同类 skill / 都是小改动 / 两条关键词重叠 / 已接近上限 | Ordinary words in Chinese; no coined metaphors                   |
| 通过对索引的重建实现了查询延迟从 120 ms 到 15 ms 的降低 | 重建索引后，查询延迟由 120 ms 降至 15 ms                  | A direct verb instead of a nominalized shell                     |
