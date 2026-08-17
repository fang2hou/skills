# Fix Patterns

Principles and illustrative examples for Phase 3-4 (Plan and Execute). Use these as REFERENCE, not prescription — always adapt to the project's actual patterns and the specific context of the change.

## Fix Principles (Apply to Every Fix)

1. **Match the project's existing style.** Before writing a fix, read similar code in the same module. Mirror its patterns, even if you'd write it differently from scratch.
2. **Minimal scope.** Fix only the identified issue. Don't refactor adjacent code, don't "improve" unrelated names, don't add features.
3. **Consider blast radius.** For library/SDK code, every fix is a potential breaking change. Ask: "could this fix cause a panic or behavioral change for downstream consumers?"
4. **Preserve backward compatibility.** If the code being fixed is part of a public API, prefer adding over changing. Deprecate the old way, don't remove it.
5. **Think about the next person.** A fix should leave the code clearer than you found it — but only for the thing you fixed. Don't "clean up" everything in sight.

## Illustrative Patterns

These examples demonstrate THINKING, not templates. The languages shown reflect common project types (Rust, Go, Lua, TypeScript, Python). Adapt to whatever language you're actually working in.

### Error Handling: Silenced Error → Proper Propagation

**The principle**: Errors should carry context and propagate to someone who can handle them. How you do this depends on the language's error model.

**Rust** — use `Result` + `?`, add context with `.map_err()`:

```rust
// Think: what information does the caller need to debug this?
let user = fetch_user(id)
    .map_err(|e| AppError::UserFetchFailed { id, source: e })?;
```

**Go** — wrap with `fmt.Errorf("doing what: %w", err)`:

```go
user, err := fetchUser(id)
if err != nil {
    return fmt.Errorf("fetch user %d: %w", id, err)
}
```

**Lua** — return nil + error message, propagate upward:

```lua
local user, err = fetch_user(id)
if not user then
    return nil, ("fetch user %s: %s"):format(id, tostring(err))
end
```

**When NOT to fix**: If this is a hotfix and the error handling is imperfect but doesn't make the situation worse. Note it, don't block.

### Error Handling: Panic in Library Code → Result Type

**The principle**: Library code must never panic on invalid input. Return an error the caller can handle.

```rust
// Library function: callers depend on this not panicking
pub fn parse_config(raw: &str) -> Result<Config, ConfigError> {
    let parsed: Value = serde_json::from_str(raw)
        .map_err(ConfigError::InvalidJson)?;
    let port = parsed["port"].as_u64()
        .ok_or(ConfigError::MissingField("port"))?
        .try_into()
        .map_err(|_| ConfigError::InvalidPort)?;
    Ok(Config { port })
}
```

**When NOT to fix**: If the function is explicitly documented as panicking (e.g., `Index::index` trait impl) and callers expect it.

### Type Safety: Unsafe Escape → Safe Abstraction

**The principle**: If the type system can catch the error at compile time, let it. Don't bypass with assertions or casts.

**Go** — replace `interface{}` with concrete types:

```go
// Instead of: func process(data interface{}) string { ... }
type Input struct {
    Name string `json:"name"`
}
func process(data Input) string {
    return data.Name
}
```

**Rust** — replace `.unwrap()` with `Option`/`Result` propagation:

```rust
// Instead of: fn get_first(items: &[Item]) -> Item { items.first().unwrap().clone() }
fn get_first(items: &[Item]) -> Option<&Item> {
    items.first()
}
```

**When NOT to fix**: If the unwrap/assertion is in a test helper or after a condition that guarantees safety, and the surrounding code makes this clear.

### Complexity: Deep Nesting → Early Returns

**The principle**: Every level of nesting adds cognitive load. Early returns flatten the happy path.

```rust
// Instead of nesting:
fn get_discount(user: Option<&User>, order: &Order) -> f64 {
    let user = match user {
        Some(u) => u,
        None => return 0.0,
    };
    if !user.is_premium {
        return 0.0;
    }
    if order.total > 100.0 { 0.2 } else { 0.1 }
}
```

**When NOT to fix**: In a hotfix, or if the nesting is actually clearer than early returns would be (e.g., a match chain where each branch is short).

### API Design: Boolean Trap → Options Struct

**The principle**: If a function takes multiple booleans, callers can't tell which is which. Use named parameters or an options struct.

```go
// Instead of: func NewServer(true, false, true, 8080)
type ServerConfig struct {
    EnableTLS   bool
    EnableAuth  bool
    EnableCache bool
    Port        int
}
func NewServer(cfg ServerConfig) *Server { ... }
```

**When NOT to fix**: If this is a hotfix adding one boolean to an existing function, and refactoring to options would be scope creep. Note for future.

### Security: SQL Injection → Parameterized Queries

**The principle**: Never concatenate user input into queries. Use parameterized queries. This is non-negotiable regardless of change type.

```go
// Instead of: fmt.Sprintf("SELECT * FROM users WHERE id = '%s'", userID)
row := db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", userID)
```

**This is always critical. No exceptions.**

### Performance: Sequential → Parallel for Independent Operations

**The principle**: If two operations are independent and both are I/O-bound, run them concurrently.

```rust
// Instead of sequential:
let (users, config) = tokio::join!(fetch_users(), fetch_config());
let users = users?;
let config = config?;
```

```go
// Using errgroup:
var eg errgroup.Group
eg.Go(func() error { ... })
eg.Go(func() error { ... })
if err := eg.Wait(); err != nil { return err }
```

**When NOT to fix**: If the operations are fast (microseconds), the concurrency overhead is worse than sequential execution. Don't optimize what's already fast enough.

## Fix Execution Checklist

Before applying ANY fix, answer these questions honestly:

1. **Does this fix preserve the original intent?** The author wanted to accomplish X. Does my fix still accomplish X?
2. **Does this fix match the project's conventions?** Have I read similar code in the codebase? Am I mirroring its patterns?
3. **Will this fix cascade?** Will changing this one thing require changes in 5 other files? If yes, re-plan.
4. **Is the scope minimal?** Am I changing only what's needed for this fix, nothing more?
5. **Is there a test that covers this code path?** If yes, run it after. If no, should I suggest adding one?
6. **For library code: is this backward compatible?** Will existing callers keep working? Could this cause a panic downstream?

If any answer makes you uncertain, re-plan before executing. A bad fix is worse than no fix.
