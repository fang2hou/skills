# Layer 1: Durable Human Expression Principles

These ten principles form **Layer 1 (`layer: core`)** of the `natural-writing` skill (`rules/core.yaml`). They are independent of any AI model architecture and apply across English, Chinese, and Japanese. Every language rule in Layer 2 and every symptom check in Layer 3 derives its authority from one or more of these principles.

Contents:

- [Precedence Hierarchy](#precedence-hierarchy)
- [P1. Meaning Chooses the Word (`core.clarity.meaning_chooses_word`)](#p1-meaning-chooses-the-word-coreclaritymeaning_chooses_word)
- [P2. Concrete Specifics Over Cloudy Abstraction (`core.clarity.concrete_over_vague`)](#p2-concrete-specifics-over-cloudy-abstraction-coreclarityconcrete_over_vague)
- [P3. Align Grammatical Subjects and Verbs with Actors and Actions (`core.syntax.actors_and_actions`)](#p3-align-grammatical-subjects-and-verbs-with-actors-and-actions-coresyntaxactors_and_actions)
- [P4. High Information Density, Low Cognitive Friction (`core.concision.information_density`)](#p4-high-information-density-low-cognitive-friction-coreconcisioninformation_density)
- [P5. Earned Contrast and Honest Connectives (`core.logic.earned_contrast_and_connectives`)](#p5-earned-contrast-and-honest-connectives-corelogicearned_contrast_and_connectives)
- [P6. Figurative Coherence and Functional Rhetoric (`core.rhetoric.figurative_coherence`)](#p6-figurative-coherence-and-functional-rhetoric-corerhetoricfigurative_coherence)
- [P7. Social Distance and Register Fit (`core.pragmatics.social_distance_and_register`)](#p7-social-distance-and-register-fit-corepragmaticssocial_distance_and_register)
- [P8. Epistemic Calibration: Fact vs. Inference (`core.pragmatics.epistemic_calibration`)](#p8-epistemic-calibration-fact-vs-inference-corepragmaticsepistemic_calibration)
- [P9. Old-Before-New Cohesion and Organic Rhythm (`core.cohesion.old_before_new`)](#p9-old-before-new-cohesion-and-organic-rhythm-corecohesionold_before_new)
- [P10. Fidelity to Facts, Precision, and Authorial Voice (`core.fidelity.preserve_voice_and_facts`)](#p10-fidelity-to-facts-precision-and-authorial-voice-corefidelitypreserve_voice_and_facts)

---

## Precedence Hierarchy

When two principles pull in different directions, resolve the conflict in this exact order:

1. **Factual, causal, and terminological fidelity (`P10`)** always wins. Never alter a fact, drop a required condition, or replace a precise technical term to make a sentence shorter or punchier.
2. **Pragmatic & register appropriateness (`P7`, `P8`)** outranks surface brevity (`P4`). In diplomatic, legal, or polite Japanese/Chinese correspondence, required courtesy or epistemic qualifiers are not "clutter."
3. **Conceptual clarity and syntactic agency (`P1`, `P2`, `P3`, `P5`)** outrank rhythmic or stylistic preferences (`P6`, `P9`).
4. **Authorial voice (`P10`)** outranks default stylistic normalization: if an author's sentence is clear, accurate, and effective, leave their idiosyncratic rhythm intact.

---

## P1. Meaning Chooses the Word (`core.clarity.meaning_chooses_word`)

- **Theoretical Basis**: `orwell-1946`, `ye-shengtao-1934`, `zhu-guangqian-1946`
- **Principle**: Formulate the concrete thought first, then select the exact words that cover that meaning; never allow prefabricated phrase strips or fashionable buzzwords to dictate the thought.
- **Cognitive Mechanism**: Prefabricated phrases activate broad associative schemas rather than precise referents, concealing fuzzy thinking from both writer and reader.
- **Editorial Check**: Can you state in plain words what state of the world this clause describes? If removing the buzzwords leaves no proposition, rewrite around the real claim or cut the sentence.

## P2. Concrete Specifics Over Cloudy Abstraction (`core.clarity.concrete_over_vague`)

- **Theoretical Basis**: `orwell-1946`, `strunk-white-1959`, `kinoshita-1981`, `vercel-writing-2026`
- **Principle**: Name specific objects, quantities, failure modes, and literal actions rather than dissolving them into high-level category nouns (_phenomena, elements, aspects, 维度, 生态, 側面_), weasel qualifiers (`significantly`, `many`, `often`, `typically`, `generally`), vague quantifiers (`near-zero`, `sub-second`, `most requests`), or filler cadence verbs (`moves through`, `lands`, `carries`, `hits`).
- **Cognitive Mechanism**: Concrete nouns, cited figures (`99.37% of requests see zero cold starts`), and literal step verbs allow readers to construct a mental model immediately; stacked abstractions and vague quantifiers force readers to guess what concrete reality is being summarized.
- **Exception**: When defining a genuinely abstract mathematical, philosophical, or architectural invariant, or when the source text provides no lower-level data (never invent specifics to fake concreteness).

## P3. Align Grammatical Subjects and Verbs with Actors and Actions (`core.syntax.actors_and_actions`)

- **Theoretical Basis**: `orwell-1946`, `williams-1981`, `pinker-2014`, `lv-zhu-1952`, `zhu-dexi-1982`, `vercel-writing-2026`
- **Principle**: Cast the semantic agent as the grammatical subject and the key action as a finite verb, rather than locking the action inside an abstract nominalization paired with a weak light verb (_make, perform, conduct, 进行, 作出, 行う_), reading from a datasheet in **spec-sheet voice** (`provides`, `is configurable`, `is explicitly labeled`), or assigning human-physical actions to **personified artifacts** (`hand the browser a URL` $\to$ `the browser fetches the URL`; `the token holds` $\to$ `the token is stored`). Apply the **"by monkeys" mental test** to catch unintended passives and the speech-pace **second-read test**: if you must re-read a sentence to parse it, name the subject, the action, and the consequence, and cut metaphor verbs or pronouns reaching back several sentences.
- **Cognitive Mechanism**: Clauses built around real verbs and literal agents require fewer tokens and less syntactic tree-building than nominalized noun phrases or datasheet predicates.
- **Exception**: Established technical nouns (`authentication`, `serialization`, `幂等性`, `排他制御`) or compact topic references (`This migration...`) that anchor old-before-new cohesion, or intentional patient-topic continuity (`the token is stored`).

## P4. High Information Density, Low Cognitive Friction (`core.concision.information_density`)

- **Theoretical Basis**: `strunk-white-1959`, `zinsser-1976`, `grice-1975` (Maxim of Quantity & Manner), `vercel-writing-2026`
- **Principle**: Every sentence and paragraph must advance the reader's understanding. Cut throat-clearing run-ups, **summary-style paragraph transitions** that recap the previous paragraph (`With this setup complete…`, `Now that we've explored…`), **reused template framing** (`The question most teams face is whether…`), marketing rhetorical questions, filler intensifiers (`very`, `just`, `really`), and one-line closers that restate the paragraph above. When drafting (`generate` mode), earn every detail—cut implementation trivia if general phrasing would not change the reader's understanding or action (while strictly preserving all source facts under `P10` in `rewrite`/`light-polish` modes).
- **Cognitive Mechanism**: Reader attention is finite. Words and recap transitions that carry zero semantic or pragmatic payload dilute the salience of the actual argument.
- **Exception**: Deliberate pedagogical signposting in long reference manuals, one-paragraph page TL;DRs and section summary openers in documentation (`vercel-writing-2026`), or rhythmic repetition in literary speeches.

## P5. Earned Contrast and Honest Connectives (`core.logic.earned_contrast_and_connectives`)

- **Theoretical Basis**: `grice-1975` (Maxim of Relation & Manner), `pinker-2014`, `strunk-white-1959`
- **Principle**: Use adversative (`not X, but Y`, `不是……而是……`, `〜ではなく〜だ`), causal (`therefore`, `因此`, `したがって`), and concessive (`although`, `尽管`) markers only when the propositions stand in that exact logical relation.
- **Cognitive Mechanism**: Contrastive markers instruct the reader's brain to allocate extra processing effort to resolve an opposition. When the negative branch is a strawman nobody held, the reader experiences theatrical manipulation rather than insight.
- **Exception**: Genuine correction of a common misconception, scope boundary disambiguation, or explicit contrast between two real alternatives.

## P6. Figurative Coherence and Functional Rhetoric (`core.rhetoric.figurative_coherence`)

- **Theoretical Basis**: `orwell-1946`, `lakoff-johnson-1980`, `zhu-guangqian-1946`, `fowler-1926`
- **Principle**: Rhetoric is not ornament pasted onto plain thought; it is an instrument for making meaning clearer or more vivid. Metaphors must map a coherent source domain onto the target domain, fit the register, and avoid mixing incompatible images.
- **Cognitive Mechanism**: Living metaphors leverage sensory-motor schemas to illuminate abstract relationships; dying or mixed metaphors trigger conflicting schemas or dead noise.
- **Exception**: Fully lexicalized dead metaphors that function as standard technical terms (`deadlock`, `bottleneck`, `缓存击穿`, `スレッドプール`).

## P7. Social Distance and Register Fit (`core.pragmatics.social_distance_and_register`)

- **Theoretical Basis**: `brown-levinson-1987`, `gowers-1954`, `bunkacho-2007`, `bunkacho-2022`, `ye-shengtao-1934`, `vercel-writing-2026`
- **Principle**: Calibrate formality, politeness, and emotional intimacy to the social distance ($D$), relative power ($P$), imposition ($R$), and content type (`Tutorial`: warm and predictable; `How-to`: terse and direct for a mid-task reader; `Reference`: neutral, exhaustive, quotable; `Conceptual`: teach-it-back clarity with analogies; `Troubleshooting`: empathetic without apology—acknowledge then fix). Avoid pompous institutional distance, unsolicited emotional intimacy, internet slang, and **reader-pressuring minimizers** (`easy`, `simple`, `quick`, `简单`, `轻松`, `簡単`, `手軽`—replace with concrete descriptions like `"one command"` or `"default settings"`).
- **Cognitive Mechanism**: Register violations and difficulty minimizers shift the reader's attention from the message to the writer's inappropriate posture—either lecturing like a bureaucrat, acting like an uninvited therapist, or pressuring a struggling reader by calling a task "easy."
- **Exception**: Fiction dialogue, intentional persona writing, intimate personal correspondence, or settled technical names containing those words (_Simple Mail Transfer Protocol_, _quicksort_).

## P8. Epistemic Calibration: Fact vs. Inference (`core.pragmatics.epistemic_calibration`)

- **Theoretical Basis**: `kinoshita-1981`, `grice-1975` (Maxim of Quality), `orwell-1946`
- **Principle**: Distinguish verified facts from inferences, hypotheses, and value judgments. State facts directly without defensive hedge-stacking (`could potentially arguably`); state genuine uncertainty once, naming its basis, without inflating routine facts into "pivotal historic milestones."
- **Cognitive Mechanism**: Both over-hedging (evading commitment) and over-claiming (advertising language) erode reader trust in the writer's epistemic reliability.
- **Exception**: Legal, medical, or regulatory disclaimers where specific modal qualifiers are mandated by statute or standard of care.

## P9. Old-Before-New Cohesion and Organic Rhythm (`core.cohesion.old_before_new`)

- **Theoretical Basis**: `williams-1981`, `honda-1976`, `tanizaki-1934`, `pinker-2014`, `vercel-writing-2026`
- **Principle**: Link sentences and paragraphs by placing familiar context before new information, carrying the prior subject forward so body paragraphs never **cold-open** like standalone headings without antecedents (`Because…`, `Once…`), ordering modifiers so syntactic dependencies resolve on the first pass, and merging **stop-start choppy fragments** (`Previously this was manual. Now it's automatic. This saves time.` $\to$ one sentence) while reserving short sentences for genuine emphasis.
- **Cognitive Mechanism**: Readers integrate new propositions by attaching them to active nodes in working memory ("old-before-new"); cold-open paragraphs, stop-start fragments, and mechanical triads break discourse continuity and signal template generation.
- **Exception**: Exhaustive enumerations where a system genuinely has three components, or parallel clauses used once for deliberate climactic emphasis.

## P10. Fidelity to Facts, Precision, and Authorial Voice (`core.fidelity.preserve_voice_and_facts`)

- **Theoretical Basis**: `orwell-1946` (Rule vi), `pinker-2014`, `kinoshita-1981`
- **Principle**: An edit is valid only if it preserves 100% of the author's verified facts, numbers, causal direction, technical terminology, and personal voice. Never flatten a lively human essay into sterile corporate prose, and never edit a sentence that already works.
- **Cognitive Mechanism**: Style serves truth and voice. If an editorial rule strips away the author's distinctive perspective or alters a technical boundary condition, the edit has failed its primary purpose.
- **Exception**: None. This principle is the top-level invariant of the skill.
