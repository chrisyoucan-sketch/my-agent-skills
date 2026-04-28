# Source Priority

## Priority Order

Use this order unless the user explicitly overrides it:

1. Task-provided data, local documents, and database query results
2. Official primary sources
3. High-quality secondary sources
4. Model background knowledge for orientation only

Treat higher-priority evidence as more authoritative, but not automatically error-free. If two high-priority sources disagree, surface the disagreement.

## Working Rules

1. Read task-local material before browsing.
2. Use model knowledge to form hypotheses, search terms, and framing, not to replace missing citations.
3. Prefer sources with direct access to the underlying facts over commentary about those facts.
4. Prefer newer sources when the topic is time-sensitive, but do not discard older primary sources that define the official baseline.

## Conflict Handling

When sources conflict, classify the conflict:

- `version conflict`: same source family, different dates or revisions
- `definition conflict`: same label, different metric or scope
- `measurement conflict`: same target, different methodology
- `interpretation conflict`: same facts, different conclusions

Handle conflicts explicitly:

1. Identify which sources conflict.
2. State what exactly differs.
3. Explain the most likely reason if it is inferable.
4. State which source you are relying on and why.
5. Preserve unresolved conflicts in the output instead of smoothing them away.

## Confidence Discipline

Use confidence as an evidence judgment, not a tone marker.

- `High`: supported by strong task-local or primary evidence with little ambiguity
- `Medium`: supported, but with some gaps, assumptions, or source mismatch
- `Low`: plausible but incomplete, indirect, stale, or materially disputed

Do not assign `High` confidence when the claim depends mainly on model memory or secondary commentary.
