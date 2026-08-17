# Writing Effective Descriptions

Guide for writing the `description` field so skills trigger reliably on relevant prompts.

## Core Principles

1. **Third-person statement + imperative trigger**: Open with what the skill does in third person ("Extracts text from PDFs"), then give the activation clause as an instruction to the agent ("Use when the user mentions forms or document extraction"). Never write in first or second person ("I can help you…", "You can use this to…").
2. **Focus on user intent**: Describe what the user wants to achieve, not the skill's internal mechanics.
3. **Cover WHAT + WHEN**: State what the skill does and when to activate it.
4. **Include trigger keywords**: List words and phrases users might use.
5. **Be pushy about scope**: Explicitly list applicable contexts, including indirect mentions.
6. **Target 250 chars**: The spec's hard limit is 1024 characters; keep to roughly 250 so listings do not truncate the key use case. Front-load that use case.

## Before/After Examples

**Vague** (fails to trigger):

```yaml
description: Process CSV files.
```

**Specific** (triggers reliably):

```yaml
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
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

After writing a description, test it mentally against these questions:

1. Would an agent match "analyze my sales data" to this skill?
2. Would an agent match "I need to clean up a spreadsheet" to this skill?
3. Would an agent match an unrelated request (e.g., "write a fibonacci function") and wrongly activate?
4. Would a near-miss that shares keywords but needs another skill stay out?

For trigger accuracy, create about 20 test queries with roughly half `should_trigger: true`
and half `should_trigger: false`. Vary positive phrasing and include near-miss negatives that
share keywords but require a different user intent. Judge the user's intended outcome, not
keyword presence alone. For the full trigger-eval method, load [references/eval-guide.md](eval-guide.md)
and read its "Trigger evals" section.
