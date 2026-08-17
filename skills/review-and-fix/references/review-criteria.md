# Review Criteria

Review dimensions for Phase 2 (Think). This is NOT a checklist to mechanically apply — it's a thinking framework. The weight you give each dimension depends on the change type, as defined in the SKILL.md context-rigor table.

## How to Use This Reference

1. Identify the change type (hotfix, library, new feature, refactor, config)
2. Check the rigor matrix in SKILL.md to know which dimensions matter most
3. For each dimension your change type requires, read the guidance below
4. **Adapt, don't follow blindly** — if the project has a reason to deviate, respect that reason

## Review Dimensions

### 1. Correctness (Universal — always check)

**The only dimension that applies to every change type equally.** A wrong hotfix is worse than no hotfix.

**Think about**:

- Does the code do what the diff message / ticket says it should do?
- Are boundary conditions handled? Off-by-one, empty input, nil/None/null?
- Are there edge cases the author clearly didn't think about?
- Does the change handle failure paths, or only the happy path?

**When to research**: If the logic involves domain-specific rules (tax calculation, authentication flow, encoding), verify your understanding before flagging something as "wrong."

### 2. Error Handling (Universal — always check)

**Think about**:

- Are errors properly propagated, not swallowed?
- Does the error carry enough context for someone debugging at 3am?
- In library code: does the error type make sense for downstream consumers? Could an error path cause a panic?

**Nuance for different contexts**:

- **Hotfix**: Focus on "does the error path make the situation worse?" If the error handling is imperfect but doesn't make things worse, note it but don't block.
- **Library**: Every public error is a compatibility commitment. Changing error types is a breaking change. Adding new error variants is usually fine.
- **New feature**: This is where you set the error handling pattern. Get it right now, or every caller will copy the wrong pattern.

### 3. Security (Check when change touches trust boundaries)

Not every change needs a security review. Focus on:

- Input from external sources (user input, API responses, file contents)
- Authentication/authorization logic
- Cryptographic operations
- SQL/query construction
- File path handling

**Skip for**: Internal refactors, pure computation, config changes that don't affect access control.

### 4. Type Safety

**Think about**:

- Does the type system catch the failure modes, or can invalid states be represented?
- Are there unsafe escapes (unwrap, type assertions, interface{}) that bypass the type system at critical points?
- Do generic constraints communicate the actual requirements?

**Context-dependent**:

- **Library**: Type safety is part of the API contract. An `interface{}` / `any` in a public API forces every caller to do their own type checking — that's a design smell.
- **Hotfix**: If the existing code already has weak typing, fixing it is scope creep. Note it, don't fix it.
- **Rust specific**: `.clone()` to satisfy the borrow checker is sometimes the right answer. Don't flag every clone — flag clones that mask an ownership design problem.

### 5. API Design

**Primarily for library and new feature changes.**

**Think about**:

- Can this API be used incorrectly? If yes, redesign to make misuse impossible.
- Is the API consistent with the rest of the codebase? If the codebase uses builder patterns, don't introduce a function with 8 parameters.
- Does the change maintain backward compatibility? For libraries: can existing callers keep working without changes?
- Is the abstraction at the right level? Too low-level = leaky. Too high-level = inflexible.

**Critical question for library changes**: "If I make this change, will any existing consumer break? Will any consumer panic?"

### 6. Concurrency Safety

**Think about**:

- Is shared state properly synchronized?
- Can two concurrent executions interfere with each other?
- Are there deadlock risks from lock ordering?
- In async code (Rust, Go, Lua coroutines): are there blocking operations in async context?

**Context-dependent**:

- **Library**: Concurrency safety is a contract. If your library is used from multiple threads, every public API must be safe. Document the threading model.
- **Hotfix**: If the hotfix introduces shared mutable state, that's critical. If it doesn't touch concurrency, skip.

### 7. Complexity

**Think about**:

- Can someone unfamiliar with this code understand it in one reading?
- Is the complexity inherent to the problem, or accidental (created by the implementation)?
- Would extracting a helper make the intent clearer, or just spread the logic across more locations?

**Context-dependent**:

- **Hotfix**: Don't suggest refactoring. The goal is minimal correct change.
- **New feature**: Set the standard early. A 50-line function will grow to 200 lines if you don't catch it now.

### 8. Performance

**Only flag issues that are clearly wasteful for the use case.** Don't micro-optimize.

**Think about**:

- Is there an algorithmic problem (O(n²) when O(n) is possible)?
- Are there unnecessary allocations in a hot path?
- Is there an N+1 query pattern?

**Don't flag**: Minor allocation differences in cold paths, stylistic choices that don't affect runtime.

### 9. Naming and Style

**Lowest priority in almost every context.** Only flag if:

- The name is actively misleading (function named `get` that mutates state)
- The convention is inconsistent within the same module (not across the whole codebase)
- The change introduces a new public API where naming is a commitment

### 10. Downstream Impact

**Primarily for library and refactoring changes.**

**Think about**:

- Who depends on this code? Search for importers and callers.
- If this behavior changes, what breaks downstream?
- Could this change cause panics in consuming applications?
- Is there a deprecation path, or is this a silent breaking change?

**When to research**: For library changes, actually search for downstream consumers. Don't assume. If you can't find consumers (closed-source), be conservative — assume the most fragile usage pattern.

## Severity Framework

Severity is not absolute — it depends on context:

| Context     | Critical                                      | Warning                         | Suggestion        |
| ----------- | --------------------------------------------- | ------------------------------- | ----------------- |
| Library     | Downstream panic, breaking change, API misuse | Missing validation, weak typing | Naming, style     |
| Hotfix      | Regression, wrong fix, introduced bug         | Missing edge case               | — (don't suggest) |
| New feature | Logic error, security hole, data loss         | Poor error handling, API design | Style, minor perf |
| Refactor    | Behavioral change, regression                 | Inconsistent with old behavior  | Style             |

**Rule of thumb**: If you can't articulate WHY an issue matters for THIS change type, it's probably a suggestion, not a warning.
