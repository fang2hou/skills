# Phrase Patterns

Common awkward-to-natural phrase mappings for Japanese technical docs. Grounded in real cleanup work on an internal platform's skill descriptions and README text.

## Collocation Mismatches

Direct calques from English that are grammatically valid but unnatural in Japanese IT docs.

| Awkward                  | Natural                                         | Why                                                                                      |
| ------------------------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `ライブラリ癖`           | `ライブラリ固有の挙動`                          | 癖 is colloquial; 固有の挙動 is standard technical phrasing                              |
| `コンテキストを解決し`   | `コンテキストを踏まえ` / `コンテキストを取得し` | 解決 implies solving a problem; コンテキスト is gathered or considered, not solved       |
| `承認ゲート`             | `承認ステップ` / `承認チェック`                 | ゲート is a direct calque of "gate" that sounds mechanical in Japanese                   |
| `修正導線`               | `修正フロー` / `修正手順`                       | 導線 (wiring/routing) is a UI/UX term misapplied to workflow                             |
| `証拠付きレビュー`       | `根拠に基づくレビュー`                          | 証拠付き sounds like legal/forensic language, not engineering                            |
| `保守的な allowed-tools` | `必要最小限の allowed-tools`                    | 保守的 + English noun is an awkward mixed-script phrase; 必要最小限 is the actual intent |
| `品質改善提案ゲート`     | `品質チェックと改善提案`                        | Four-noun stack is unreadable; break with particles                                      |
| `スキル品質継続改善`     | `スキル品質の継続的改善`                        | Missing の and 的 makes it a compressed compound noun                                    |
| `差分変更内容`           | `差分の変更内容` / `変更差分`                   | Stacked nouns without particles; pick one framing                                        |

## Sentence Structure Patterns

| Pattern                                 | Problem                                       | Fix                                                      |
| --------------------------------------- | --------------------------------------------- | -------------------------------------------------------- |
| Long relative clause before noun        | Follows English structure                     | Move modifier closer to noun or split into two sentences |
| Multiple の chains: `AのBのCのD`        | Hard to parse past 2 levels                   | Restructure: `AにおけるBの、CとD` or split               |
| Passive where active is natural         | 翻訳調: "～が行われる" when "～する" suffices | Use active voice unless passive serves a purpose         |
| Subject-first with は in every sentence | Monotonous; follows English SVO pattern       | Vary sentence openings; drop obvious subjects            |

## Table Cell Compression

Table cells need extra attention because compressed phrasing amplifies problems.

| In Table (Awkward)                         | In Table (Natural)                               | Rule Applied                              |
| ------------------------------------------ | ------------------------------------------------ | ----------------------------------------- |
| `8項目スコアリングベース品質監査改善`      | `8 項目のスコアリングと改善案で最適化`           | Break noun stack; add particles           |
| `サブタスクストーリーエピックコンテキスト` | `サブタスク→ストーリー→エピックのコンテキスト`   | Use arrows or particles to show hierarchy |
| `要件仕様チェック補足資料整理支援`         | `要件整理から仕様チェック、補足資料整理まで支援` | Add から/まで to show process flow        |

## Heading Conventions

| Awkward Heading              | Natural Heading                      | Rule                                  |
| ---------------------------- | ------------------------------------ | ------------------------------------- |
| `スキルの追加の仕方について` | `スキルの追加手順`                   | Use noun phrase, not conversational   |
| `インストールするには`       | `インストール` or `インストール手順` | Drop conditional phrasing             |
| `注意しなければならないこと` | `注意事項` or `運用上の注意点`       | Use established 4-character compounds |
| `どうやって使うか`           | `使い方` or `利用方法`               | Noun phrase, not question             |

## Mixed-Script Compound Warning Signs

Phrases combining kanji + katakana + English are high-probability collocation mismatches. Check each one:

- `承認ゲート付きワークフロー` → `承認ステップを含むワークフロー`
- `エビデンスベースドレビュー` → `根拠に基づくレビュー`
- `コンテキスト解決ロジック` → `コンテキスト取得処理`
- `品質ゲートチェック` → `品質チェック`

## Quick Self-Check

After polishing, scan for these red flags:

1. Any 4+ character compound noun without particles → break it apart
2. Any `Xを解決` where X is not a problem → probably should be 取得/確認/参照
3. Any heading longer than ~15 characters → probably needs shortening
4. Any table cell you need to read twice → it needs rewriting
5. Any sentence with 3+ の in a row → restructure
6. Any mixed kanji-katakana-English compound → verify it's standard industry usage
