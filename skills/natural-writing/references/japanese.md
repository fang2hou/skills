# Layer 2: Japanese (`ja`) Realization Guide

This guide translates the universal principles in `references/principles.md` into the head-final syntax, honorific system (`敬語`), style register (`文体`), and composition traditions of modern Japanese (`ja`). Load this file whenever generating, reviewing, or rewriting Japanese prose, alongside `rules/ja.yaml`.

Contents:

- [1. Structural Pillars of Clear Japanese Prose](#1-structural-pillars-of-clear-japanese-prose)
- [2. Style Consistency: Keitai (`です・ます`) vs. Jotai (`だ・である`) (`ja.register.style_consistency_keitai_jotai`)](#2-style-consistency-keitai-ですます-vs-jotai-だである-jaregisterstyle_consistency_keitai_jotai)
- [3. Keigo Calibration and the `〜させていただく` Syndrome (`ja.pragmatics.keigo_inflation_and_sasete_itadaku`)](#3-keigo-calibration-and-the-させていただく-syndrome-japragmaticskeigo_inflation_and_sasete_itadaku)
- [4. Cutting Sino-Japanese Light-Verb Padding (`ja.syntax.sino_nominalization_and_light_verbs`)](#4-cutting-sino-japanese-light-verb-padding-jasyntaxsino_nominalization_and_light_verbs)
- [5. Modifier Ordering and Unambiguous _Kakariuke_ (`ja.syntax.modifier_order_and_kakariuke`)](#5-modifier-ordering-and-unambiguous-kakariuke-jasyntaxmodifier_order_and_kakariuke)
- [6. Curing Translationese Pronouns and Passives (`ja.syntax.translationese_pronouns_and_passives`)](#6-curing-translationese-pronouns-and-passives-jasyntaxtranslationese_pronouns_and_passives)
- [7. Separating Fact (`事実`) from Inference (`意見`) (`ja.pragmatics.vague_evasion_and_hedging`)](#7-separating-fact-事実-from-inference-意見-japragmaticsvague_evasion_and_hedging)
- [8. Register Calibration: Avoiding Casual Slang (`ja.register.colloquial_overcorrection`)](#8-register-calibration-avoiding-casual-slang-jaregistercolloquial_overcorrection)
- [9. Balancing Kango, Wago, and Katakana Loanwords (`ja.terminology.katakana_and_calque_balance`)](#9-balancing-kango-wago-and-katakana-loanwords-jaterminologykatakana_and_calque_balance)
- [10. Punctuation and Japanese–Latin Spacing](#10-punctuation-and-japaneselatin-spacing)

---

## 1. Structural Pillars of Clear Japanese Prose

Modern Japanese composition theory—developed by Tanizaki (`tanizaki-1934`), Iwabuchi (`iwabuchi-1960`), Honda Katsuichi (`honda-1976`), Kinoshita Koreo (`kinoshita-1981`), the Agency for Cultural Affairs (`bunkacho-2007`, `bunkacho-2022`), and _Yasashii Nihongo_ researchers (`iori-yasashii-2016`)—identifies four structural priorities:

1. **Predicates sit at the end of the clause**: If a sentence strings together four clauses (`〜であり、〜ため、〜において、〜と考えられる`), the reader cannot tell whether the sentence is affirmative, negative, factual, or speculative until the final words. Keep sentences focused on one main proposition (`一文一義`).
2. **Modifiers precede their heads**: Misordered modifiers create _kakariuke_ ambiguity (`係り受けのねじれ`), where a modifier accidentally attaches to the wrong noun or verb.
3. **Politeness and register are grammatically encoded in every predicate**: Mixing `です・ます` and `だ・である`, or inflating honorifics (`〜させていただく`), immediately disrupts reader trust.
4. **Understood subjects and pronouns are naturally omitted**: Repeating `彼・彼女・それ・あなた` or inanimate passive chains (`〜によって…が〜される`) produces stiff translationese (`翻訳調`).

---

## 2. Style Consistency: Keitai (`です・ます`) vs. Jotai (`だ・である`) (`ja.register.style_consistency_keitai_jotai`)

Following _Kouyoubun Sakusei no Kangaekata_ (`bunkacho-2022`) and Kinoshita (`kinoshita-1981`):

- **Choose one base style per document and maintain it across all body paragraphs**:
  - **`です・ます` (敬体)**: Default for public explanations, user documentation, technical guides, reports addressed to stakeholders, and business communication.
  - **`だ・である` (常体)**: Default for academic papers, internal engineering specs, encyclopedia entries, and critical essays.
- **Avoid monotonous predicate endings**: Even within `だ・である` or `です・ます`, vary the final verb (`〜する / 〜になる / 〜できる / 〜が見られる`) rather than ending three consecutive sentences with `〜である。〜である。〜である。`
- **Valid exemptions**: Headings (`見出し`), table cells, status labels, and compact bullet items may use noun endings (`体言止め`, e.g., `設定ファイルの検証`, `影響範囲の特定`) without violating body-text consistency.

---

## 3. Keigo Calibration and the `〜させていただく` Syndrome (`ja.pragmatics.keigo_inflation_and_sasete_itadaku`)

In『敬語の指針』(`bunkacho-2007`), the Agency for Cultural Affairs warns against two pervasive honorific errors in modern business and AI-generated Japanese:

1. **Overuse of `〜させていただく` (させていただく症候群)**:
   - `〜させていただく` is appropriate **only** when two conditions hold: (a) the speaker has sought or presupposes permission from the addressee/third party, and (b) the speaker derives a clear benefit from performing the action.
   - When announcing an organization's own action, stating a fact, or explaining a document, `〜させていただく` is roundabout and cloying:
     - ❌ `本日は新機能についてご説明させていただきます。` $\to$ ✅ `本日は新機能についてご説明します（ご説明いたします）。`
     - ❌ `来月より料金を改定させていただきます。` $\to$ ✅ `来月より料金を改定いたします。`
   - **Valid exception (Keep)**: `お送りいただいた資料を拝見させていただきました。` or `都合により本日は早退させていただきます。` (Permission and personal benefit are genuine — **Keep**).
2. **Double honorifics (`二重敬語`) and misapplied respect (`尊敬語` vs `謙譲語`)**:
   - ❌ `担当者がおっしゃられていました` $\to$ ✅ `担当者（またはお客様）がおっしゃっていました`
   - ❌ `ご確認していただけますでしょうか` $\to$ ✅ `ご確認いただけますでしょうか`

---

## 4. Cutting Sino-Japanese Light-Verb Padding (`ja.syntax.sino_nominalization_and_light_verbs`)

Just as English suffers from Orwellian operators and Chinese from `进行/加以`, Japanese suffers from stacking Sino-Japanese verbal nouns (`サ変動詞語幹`) with empty light verbs (`行う、実施する、実行する`) and roundabout potential/copula tails (`kinoshita-1981`, `bunkacho-2022`, `iori-yasashii-2016`):

| Padded Japanese Construction                                               | Clean Natural Predicate                              | Principle Applied                                     |
| -------------------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------- |
| `インデックスの再構築を実行することが可能であり、遅延の削減を実現します。` | `インデックスを再構築でき、レイテンシを短縮します。` | Cuts `〜の実行を行う` and `〜することが可能である`    |
| `設定ファイルの読み込みを行う際にエラーが発生することになります。`         | `設定ファイルを読み込むとエラーが発生します。`       | Replaces `〜を行う際に` and `〜ことになる` with verbs |
| `データの削除を実施する運びとなりました。`                                 | `データを削除することになりました（削除します）。`   | Removes bureaucratic nominalization padding           |

---

## 5. Modifier Ordering and Unambiguous _Kakariuke_ (`ja.syntax.modifier_order_and_kakariuke`)

Honda Katsuichi's『日本語の作文技術』(`honda-1976`) establishes deterministic rules to prevent Japanese sentences from twisting (`ねじれ`) or attaching modifiers to the wrong head:

1. **Long modifiers before short modifiers (`長い修飾語は前に、短い修飾語は後に`)**:
   - ❌ `白い昨日駅前のパン屋で買った皿` (_Was the bakery white, or the plate?_)
   - ✅ `昨日駅前のパン屋で買った白い皿` (_Unambiguous: the plate bought yesterday is white._)
2. **Macro-condition before micro-detail (`大状況から小状況へ`)** and **comma placement at structural boundaries**:
   - ❌ `管理者が承認した設定変更を適用するスクリプトを実行した。` (_Did the administrator approve the setting change, or the script?_)
   - ✅ `管理者が承認した設定変更を適用するため、スクリプトを実行した。` (Or: `設定変更が管理者に承認された後、適用スクリプトを実行した。`)

---

## 6. Curing Translationese Pronouns and Passives (`ja.syntax.translationese_pronouns_and_passives`)

Japanese LLM outputs frequently read like mechanical translations from English (`翻訳調`, `tanizaki-1934`):

1. **Drop redundant pronouns (`あなた、彼、彼女、それ、それら`)**:
   - ❌ `あなたがこのフラグを有効にすると、それはキャッシュを無効化し、あなたのアプリケーションのメモリ使用量を削減します。`
   - ✅ `このフラグを有効にすると、キャッシュが無効化され、アプリケーションのメモリ使用量を削減できます。`
2. **Replace English-calqued inanimate passives (`〜によって…が〜される`) with active or natural intransitive clauses**:
   - ❌ `キャッシュによってリクエストの 30% が吸収されています。`
   - ✅ `キャッシュがリクエストの 30% を処理しています。`
3. **Avoid mechanical transition chains (`まず…次に…さらに…最後に…結論として`) and theatrical AI copulas (`単なる〜ではなく、まさに〜と言えるでしょう`)**:
   - Do not merely soften a theatrical contrast into a milder strawman (`単なる UI の改修ではなくパラダイムシフト` $\to$ ❌ `表層的な改修ではなくアーキテクチャ変更である`); delete the negative foil completely and state the concrete change directly:
   - ❌ `このアップデートは単なるバグ修正ではなく、まさに開発体験のパラダイムシフトと言えるでしょう。`
   - ✅ `このアップデートではバグ修正に加え、ビルド時間を 40% 短縮しました。`

---

## 7. Separating Fact (`事実`) from Inference (`意見`) (`ja.pragmatics.vague_evasion_and_hedging`)

Kinoshita Koreo (`kinoshita-1981`) stresses that muddy Japanese prose blurs observed facts with the writer's conjecture through evasive sentence endings:

- **Watch patterns**: `〜といったような状況が見受けられます`, `〜かと思われます`, `〜という側面も否定できないのではないでしょうか`, `〜的な部分がある`.
- **Rule**:
  - When stating a verified **fact (`事実`)**, end definitively (`〜です / 〜である / 〜ました`): `メモリ使用量が上限の 8 GB に達しました。` (never `達したかと思われます`).
  - When stating an **inference or opinion (`意見・推測`)**, name the evidence and state the degree of certainty cleanly: `ログのタイムスタンプから、デッドロックが原因と推測されます。`

---

## 8. Register Calibration: Avoiding Casual Slang (`ja.register.colloquial_overcorrection`)

Plain, readable Japanese (`わかりやすい日本語`, `bunkacho-2022`) is not spoken slang (`話し言葉・俗語`):

| Spoken / Slang Overcorrection (Avoid in Written Docs)  | Natural Written Japanese (`です・ます` / `常体`)   |
| ------------------------------------------------------ | -------------------------------------------------- |
| `夜中にリリースして誰も見ていない時にサーバーが死んだ` | `深夜の無人リリース中にサーバーが異常終了しました` |
| `ぶっちゃけ、この設定でいい感じに処理できます`         | `この設定で適切に処理できます`                     |
| `古い API をバッサリ消す`                              | `旧 API を廃止する`                                |

---

## 9. Balancing Kango, Wago, and Katakana Loanwords (`ja.terminology.katakana_and_calque_balance`)

- **Prefer settled Kango/Wago over unnecessary Katakana business jargon** (`bunkacho-2022`):
  - Write `要件` (not `リクワイアメント`), `課題 / 問題` (not `イシュー`), `合意する` (not `アグリーする`), `優先順位` (not `プライオリティ`), `根拠 / 証拠` (not `エビデンス` when everyday Japanese suffices).
- **Use settled Japanese engineering terms over literal English metaphor calques**:
  - `正常系` (not `ハッピーパス` or `黄金の道（ゴールデンパス）` for _happy path_ / _golden path_)
  - `影響範囲` (not `爆発半径` for _blast radius_)
  - `妥当性確認` (not `正気チェック` for _sanity check_)
  - `信頼できる唯一の情報源` (not `唯一の真実の源` for _single source of truth_)
- **Collapse `<直訳漢字>（<定着カタカナ語>）` translationese glosses to the settled term**:
  - AI drafts often translate an English technical noun literally into Kanji and place the actual Japanese Katakana term in parentheses (`鍵の回転（ローテーション）`, `メモリの足跡（メモリフットプリント）`, `負荷の均衡（ロードバランシング）`). Delete the unnatural literal Kanji prefix and write the settled term directly (`鍵のローテーション`, `メモリフットプリント`, `ロードバランシング`).
- **Keep established technical Katakana and English identifiers intact**: `パイプライン`, `ロールバック`, `キャッシュ`, `レイテンシ`, `べき等性`, `tree-shaking`, `fallback`.
- **Technical report structural restraint**: Avoid repeating the same metrics three times across `概要`, `計測結果 / 構成比較`, and `まとめ / 結論`. Keep metadata bullets (`発生日時`, `対象システム`) short and put multi-clause causal narratives in body sentences.

---

## 10. Punctuation and Japanese–Latin Spacing

- Insert **one half-width space** between Japanese characters and Latin letters or digits (`Node 24 への更新`, `180 KB 削減`), or follow the target repository's established convention consistently; never add spaces next to full-width punctuation (`、。：；？！（）「」『』`).
- Keep `%` and `°C` attached to the number (`メモリを 30% 削減`).
- Use `「……」` for primary quotations and `『……』` for nested quotes or book/document titles.
