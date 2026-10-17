# Layer 2: English (`en`) Realization Guide

This guide translates the universal principles in `references/principles.md` into the syntax, lexicon, cohesion patterns, and register norms of modern English (`en`). Load this file whenever generating, reviewing, or rewriting English prose, alongside `rules/en.yaml`.

Contents:

- [1. Core Mechanics of Clear English Prose](#1-core-mechanics-of-clear-english-prose)
- [2. De-Nominalization and Verbal False Limbs (`en.syntax.nominalization_and_false_limbs`)](#2-de-nominalization-and-verbal-false-limbs-ensyntaxnominalization_and_false_limbs)
- [3. Plain Words Over Pretentious Diction (`en.diction.pretentious_and_inflated_lexicon`)](#3-plain-words-over-pretentious-diction-endictionpretentious_and_inflated_lexicon)
- [4. Pruning Dying and Mixed Metaphors (`en.rhetoric.dying_and_mixed_metaphors`)](#4-pruning-dying-and-mixed-metaphors-enrhetoricdying_and_mixed_metaphors)
- [5. Auditing Theatrical Negation and Strawmen (`en.logic.theatrical_negation_and_strawmen`)](#5-auditing-theatrical-negation-and-strawmen-enlogictheatrical_negation_and_strawmen)
- [6. Cutting Shallow Participial Riders (`en.syntax.dangling_participle_riders`)](#6-cutting-shallow-participial-riders-ensyntaxdangling_participle_riders)
- [7. Windowpane Prose vs. Metadiscourse (`en.pragmatics.metadiscourse_and_throat_clearing`)](#7-windowpane-prose-vs-metadiscourse-enpragmaticsmetadiscourse_and_throat_clearing)
- [8. Register Calibration: Plain English Is Not Chat Slang (`en.register.anti_slang_calibration`)](#8-register-calibration-plain-english-is-not-chat-slang-enregisteranti_slang_calibration)
- [9. Old-Before-New Cohesion, End-Focus, and Cadence (`en.cohesion.sentence_variety_and_end_focus`)](#9-old-before-new-cohesion-end-focus-and-cadence-encohesionsentence_variety_and_end_focus)

---

## 1. Core Mechanics of Clear English Prose

Drawing on Orwell (`orwell-1946`), Strunk & White (`strunk-white-1959`), Zinsser (`zinsser-1976`), Williams (`williams-1981`), Pinker (`pinker-2014`), and Gowers (`gowers-1954`), natural English prose rests on four structural habits:

1. **Grammatical subjects name concrete characters or systems; finite verbs name their actions.**
2. **Everyday words carry the argument; technical terms are used for precision, never for ornament.**
3. **Clauses move from familiar context ("old") to weighty new information ("new") at the sentence end.**
4. **The prose directs the reader's gaze to the world rather than narrating the writer's own mental or drafting process.**

---

## 2. De-Nominalization and Verbal False Limbs (`en.syntax.nominalization_and_false_limbs`)

Orwell called padded verb phrases **operators or verbal false limbs** (`orwell-1946`); Pinker calls abstract nouns derived from verbs **zombie nouns** (`pinker-2014`); Williams shows that unpacking nominalizations into subject–verb clauses is the single most effective edit in English (`williams-1981`).

| Padded Operator / Nominalization                                                           | Direct Subject–Verb Revision                                             | Why It Improves Comprehension                                      |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `An optimization of the index achieved a reduction in query latency from 120 ms to 15 ms.` | `Rebuilding the index cut query latency from 120 ms to 15 ms.`           | Names the concrete action (_rebuilding_) and uses a crisp verb     |
| `The new policy has the effect of rendering legacy tokens inoperative.`                    | `The new policy invalidates legacy tokens.`                              | Replaces Orwell's _have the effect of rendering X_ with one verb   |
| `Gallery 825 serves as the organization's exhibition space and boasts four rooms.`         | `Gallery 825 is the organization's exhibition space and has four rooms.` | Restores simple _is_ and _has_ over pretentious copula substitutes |
| `By examination of the audit logs, a determination was made that...`                       | `Inspecting the audit logs showed that...`                               | Eliminates passive nominalization and names the evidence source    |

**When to keep**: Keep a nominalization when it refers back to a previous clause as a compact topic link (_"The database **migration** took four hours. This **migration** also..."_) or when it is an immutable technical noun (_authentication_, _garbage collection_, _linearizability_).

---

## 3. Plain Words Over Pretentious Diction (`en.diction.pretentious_and_inflated_lexicon`)

Both human bureaucrats (`gowers-1954`) and LLMs reach for Latinate or promotional vocabulary to make routine facts sound momentous:

- **Replace pompous verb/preposition substitutes**:
  - `utilize` $\to$ `use`
  - `facilitate / enable` $\to$ name the exact action (`let`, `help`, `speed up`, `route`)
  - `prior to` $\to$ `before`; `subsequent to` $\to$ `after`; `in order to` $\to$ `to`
  - `with respect to / in regard to` $\to$ `about`, `for`, `on`
- **Strip inflated significance and sales dressing**:
  - Cut phrases that tell the reader how impressed to feel: `stands as a testament to`, `a pivotal milestone in the evolving landscape`, `plays a crucial role in shaping`, `rich tapestry`, `nestled in the heart of`, `delve into the intricacies of`.
  - Keep the underlying factual proposition and let the data or example speak for itself.

---

## 4. Pruning Dying and Mixed Metaphors (`en.rhetoric.dying_and_mixed_metaphors`)

Apply Orwell's image test (`orwell-1946`) and Lakoff & Johnson's domain coherence test (`lakoff-johnson-1980`):

- **Mixed / clashing metaphors**:
  - ❌ `This library acts as the North Star that unlocks the bottleneck and weaves a seamless tapestry of microservices.` (Collides celestial navigation, lock-picking, plumbing, and weaving in 17 words.)
  - ✅ `This library standardizes service discovery and removes the routing bottleneck between microservices.`
- **Valid figurative or technical metaphors (Keep)**:
  - Technical terms that originated as metaphors (_deadlock, memory leak, backpressure, handshake, tree-shaking_) are lexicalized dead metaphors. Never paraphrase them.
  - Fresh, intentional analogies in essays or explanations (_"A distributed lock without fencing tokens is like a hall pass with no expiration time"_) clarify structure and should be preserved.

---

## 5. Auditing Theatrical Negation and Strawmen (`en.logic.theatrical_negation_and_strawmen`)

Correlative contrasts (`not X, but Y`; `it's not merely X—it's Y`; `this does not mean X; it means Y`) and defensive strawman openers (`Some might argue that...`, `A tempting approach would be...`, `To be clear, I am not saying...`) require a strict presupposition check (`grice-1975`):

- **Rewrite when the negative half is a theatrical foil**:
  - ❌ `Caching is not just an optimization technique; it is the foundational heartbeat of modern web architecture.`
  - ✅ `Caching reduces database load and keeps response times predictable under traffic spikes.`
- **Keep when the negative half corrects a real expectation or weights a genuine alternative**:
  - ✅ `The parser validates syntax, not type safety; run the type checker in a separate build step.` (Prevents a real engineering error — **Keep**)
  - ✅ `We considered rotating keys via a daily cron restart, which would drop active connections, so we implemented in-place reload instead.` (Documents a real architectural tradeoff — **Keep**)

---

## 6. Cutting Shallow Participial Riders (`en.syntax.dangling_participle_riders`)

A pervasive syntactic defect in AI-generated and press-release English is bolting a participial `-ing` clause onto the end of a factual sentence to claim unearned significance:

- **Watch patterns**: `..., highlighting the importance of...`, `..., underscoring its commitment to...`, `..., fostering a vibrant ecosystem of...`, `..., ensuring seamless integration across...`, `..., reflecting a broader shift toward...`.
- **Diagnosis**: A participle phrase at the end of a clause cannot express a rigorous causal or evidentiary relation; it merely glues a vague value judgment onto a fact.
- **Fix**: Delete the `-ing` rider if it states an unsupported generality. If it contains a real causal fact, promote it to a finite clause with an explicit connective (_because_, _which cut_, _so that_).
  - ❌ `The team migrated the queue to Kafka in 2024, underscoring their commitment to scalable reliability and setting the stage for future growth.`
  - ✅ `The team migrated the queue to Kafka in 2024 to handle peak bursts of 50,000 messages per second.`

---

## 7. Windowpane Prose vs. Metadiscourse (`en.pragmatics.metadiscourse_and_throat_clearing`)

In _Classic Style_ (`pinker-2014`), the writer does not narrate their own outline or stage fake candor:

- **Cut staged run-ups and candor**: `Let's dive in.`, `Here's what you need to know.`, `Honestly? Here's the thing:`, `Without further ado, let's explore...`
- **Cut self-describing document chatter**: `This section is organized by...`, `It is worth noting that...`, `It should be mentioned that...`
- **Cut defensive hedge stacks**: `It could potentially be argued that the change might somewhat affect latency.` $\to$ `The change may increase tail latency by 5–10 ms.` (Keep a single honest modal verb when uncertainty is real.)

---

## 8. Register Calibration: Plain English Is Not Chat Slang (`en.register.anti_slang_calibration`)

Sir Ernest Gowers (`gowers-1954`) and the _Federal Plain Language Guidelines_ (`plain-language-2010`) emphasize that **plain English is clear, dignified, and direct—not slangy or flippant**:

| Overly Pompous / AI-Inflated                                          | Overly Colloquial / Slang Overcorrection                    | Calibrated Natural English (Professional/Technical)             |
| --------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| `The service experienced an unanticipated termination event.`         | `The service totally blew up during the late-night push.`   | `The service crashed during the unattended late-night release.` |
| `It is imperative to effectuate the deprecation of legacy endpoints.` | `We need to nuke the old endpoints ASAP—it's a no-brainer.` | `We must remove the legacy endpoints before the v3.0 release.`  |

---

## 9. Old-Before-New Cohesion, End-Focus, and Cadence (`en.cohesion.sentence_variety_and_end_focus`)

1. **Old-before-new**: Start a sentence with a reference to what the reader just read, and put the new or complex point at the end (`williams-1981`).
2. **Avoid mechanical triads and em-dash addiction**:
   - Do not force examples or adjectives into groups of three (_"fast, reliable, and scalable"_ on every paragraph) unless there are three distinct properties with evidence.
   - Use em dashes (`—`) sparingly and only when the author's voice calls for a sharp parenthetical turn; usually a comma, colon, parentheses, or separate sentence states the logical relation more clearly.
3. **Vary sentence length organically**: Alternate medium explanatory clauses with concise, fact-bearing statements—never with hollow one-line dramatic fragments (_"And that changes everything."_, _"Full stop."_).
4. **Technical report restraint**: Keep settled domain compounds (`cold-start cache stampede`, `mark-assist stall`) intact for peer engineers rather than paraphrasing them into folksy clauses, and do not duplicate `## Summary` sentences verbatim inside a two-sentence `## Background` stub.
