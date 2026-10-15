# Writing Effective Descriptions

Guide for writing the `description` field so skills trigger reliably on relevant prompts and stay quiet on near misses.

## Core Principles

1. **Third-person statement + imperative trigger**: Open with what the skill does in third person ("Extracts text from PDFs"), then give the activation clause as an instruction to the agent ("Use when the user mentions forms or document extraction"). Never write in first or second person ("I can help you…", "You can use this to…").
2. **Focus on user intent**: Describe what the user wants to achieve, not the skill's internal mechanics.
3. **Cover WHAT + WHEN**: State what the skill does and when to activate it. All "when to use" information belongs in the description; the body is not read until after activation.
4. **Include trigger keywords**: List words and phrases users actually use, including indirect ones ("even if they don't mention CSV").
5. **Explicit, not loud**: List applicable contexts plainly. Do not add "ALWAYS use this skill" or "CRITICAL"; current models are responsive enough that emphatic descriptions over-trigger on near misses.
6. **Draw the boundary with siblings**: When another skill shares keywords, name the distinguishing intent ("existing skills" vs "new skills"), or point to the sibling in the body's When NOT to Use section.
7. **Front-load and stay short**: The spec limit is 1024 characters, but clients truncate descriptions when the skill listing exceeds its context budget. Put the key use case in the first sentence and target about 250 characters.
8. **No angle brackets**: Some clients reject `<` and `>` in descriptions.

## Before/After Examples

**Vague** (fails to trigger):

```yaml
description: Process CSV files.
```

**Specific** (triggers reliably):

```yaml
description: >
  Analyzes CSV and tabular data files: computes summary statistics,
  adds derived columns, generates charts, and cleans messy data. Use when
  the user has a CSV, TSV, or Excel file and wants to explore, transform,
  or visualize the data, even if they don't mention "CSV" or "analysis."
```

**Over-emphatic** (over-triggers):

```yaml
description: CRITICAL - ALWAYS use this skill for ANY data or file question.
```

## Description Template

```
[Primary action verb + object]. Use when [trigger scenarios], [additional triggers], or when the user mentions [keywords].
```

Fill in:

- **Primary action**: "Extracts text from PDFs", "Deploys to Kubernetes", "Analyzes CSV data"
- **Trigger scenarios**: "working with PDF documents", "deploying applications"
- **Additional triggers**: "filling forms, merging files", "rolling back releases"
- **Keywords**: "PDFs, forms, document extraction", "deploy, rollback, release"

## Testing Descriptions

After writing a description, check it against these questions:

1. Would an agent match "analyze my sales data" to this skill?
2. Would an agent match "I need to clean up a spreadsheet" to this skill?
3. Would an agent wrongly activate on an unrelated request (for example "write a fibonacci function")?
4. Would a near miss that shares keywords but needs another skill stay out?

Agents usually consult a skill only when the task exceeds what they can do with basic tools. A one-step request such as "read this PDF" may not trigger even a perfect description, so judge triggering on substantive multi-step requests.

For trigger accuracy, create about 20 test queries with roughly half `should_trigger: true` and half `should_trigger: false`. Vary positive phrasing and include near-miss negatives that share keywords but require a different user intent. Judge the user's intended outcome, not keyword presence alone. For the full trigger-eval method, load [eval-guide.md](eval-guide.md) and read its "Trigger evals" section.
