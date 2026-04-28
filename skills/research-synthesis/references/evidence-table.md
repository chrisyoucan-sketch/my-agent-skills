# Evidence Table

Include an evidence table whenever the output contains multiple meaningful conclusions.

## Recommended Columns

| Column | Purpose |
| --- | --- |
| `Conclusion` | The claim or synthesis point being supported |
| `Primary support` | The main source or artifact behind the claim |
| `Source type` | Task-local, database, official primary, secondary, or model background |
| `Confidence` | High, Medium, or Low |
| `Conflict / caveat` | Any source conflict, ambiguity, or scope limit |
| `Notes` | Date, scope, definition issues, or next validation step |

## Usage Rules

1. Keep conclusions specific enough to be testable.
2. Use one row per key claim, not one row per paragraph.
3. If the best support is indirect, say so.
4. If multiple sources support the same row, name the most authoritative one and summarize the rest in `Notes`.
5. If the claim is disputed, do not hide that in prose alone; reflect it in `Conflict / caveat`.

## Confidence Shortcuts

- `High`: direct task-local or primary evidence, low ambiguity
- `Medium`: evidence is decent but incomplete, mixed, or partly indirect
- `Low`: evidence is weak, stale, thin, or materially conflicting
