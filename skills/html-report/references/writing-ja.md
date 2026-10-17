# Japanese Writing Guide (ja)

Follow this guide together with [writing.md](writing.md) for every page with `lang="ja"`. The reader is a senior engineer who reads technical English without effort.

## Spacing and punctuation

- Put one half-width space between Japanese text and Latin letters or digits: `zod 4 への更新`, `180 KB 削減`, `回答済み 3/5`. Add no space next to full-width punctuation (`、。：；？！（）「」『』`). Keep `%` and `°C` attached to the number: `メモリを 30% 削減`.
- In a short heading that ends with a number and a counter, join them with `&nbsp;` (`3&nbsp;個`) so the counter cannot wrap to its own line.
- Quote with `「」`, and with `『』` inside them. Use the full-width colon in Japanese text (`対象：9 スキル`), not `: `. Keep half-width punctuation inside inline code, paths, commands, and English quotes.

## Register

- Write body text in です・ます throughout and never mix in だ・である. Headings, table cells, status chips, and short list labels may end in a noun (体言止め).
- Plain Japanese means cutting ornament and long preambles, not writing casually. Avoid 夜中にリリースして誰も見ていない, サーバーが落ちた, 死んだ, 固まった, いい感じに処理する, and バッサリ消す. Write 深夜の無人リリース, 異常終了, 応答停止, 適切に処理する, and 廃止する.

## Technical terms

- Keep established English terms and loanwords: `tree-shaking`, `release gate`, `blue-green deploy`, `smoke test`, `fallback`, and パイプライン, ロールバック, キャッシュ, レイテンシ.
- Where Japanese engineering usage has a settled term, use it instead of a literal translation of the English metaphor: 正常系 for happy path, 影響範囲 for blast radius, 妥当性確認 for sanity check, メンテナンス時間枠 for time window, 定期リリース for release train.
- Prefer a common kango word over a rare katakana loan: 要件, not リクワイアメント; 課題, not イシュー. Use standard terms such as べき等性 and バックプレッシャー as they are, without an everyday paraphrase or a textbook definition in parentheses.

## Sentence shape

- Cut light-verb padding and nominalizations. Write インデックスを再構築でき, not インデックスの再構築を実行することが可能であり; 使う or 使用する, not 使用を行う.
- Prefer the active voice: キャッシュがリクエストの 30% を削減します, not キャッシュによってリクエストの 30% が削減されています.
- Avoid すなわち as a mechanical rendering of ", i.e.,", and do not open sentence after sentence with まず, 次に, and さらに.

## Examples

| Avoid                                                                      | Prefer                                                                | Why                                                     |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------- |
| 夜中にリリースして誰も見ていない                                           | 深夜の無人リリース                                                    | A short written term replaces a spoken description      |
| サーバーが落ちた / 死んだ / 固まった                                       | サーバーが異常終了した / 応答が停止した                               | Name the exact state, as an incident report would       |
| リリーストレイン / ハッピーパス / 爆発半径                                 | 定期リリース / 正常系 / 影響範囲                                      | Settled Japanese terms instead of literal metaphors     |
| 正気チェック / 唯一の真実の源 / リクワイアメント                           | 妥当性確認 / 信頼できる唯一の情報源 / 要件                            | No odd calques or needless katakana                     |
| インデックスの再構築を実行することが可能であり、遅延の削減を実現します     | インデックスを再構築でき、レイテンシを 120 ms から 15 ms に短縮します | Direct verbs instead of 実行することが可能 and 実現     |
| 未検証のまま設定が読み込まれた場合において、エラーが発生することになります | 未検証の設定を読み込むとエラーが発生します                            | A short condition instead of 場合において and a passive |
