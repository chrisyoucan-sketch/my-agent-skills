# Action Title Review

Use this reference to score and improve ghost-deck titles against MBB-style standards.

## Must-Pass Checks

- Complete sentence, not a section label
- Clear so-what for an executive reader
- Active voice
- Maximum 15 words or roughly 2 lines
- Specific numbers when the source supports them
- No em dashes

## Quality Checks

- No banned words: `leverage`, `harness`, `transformative`, `synergy`, `paradigm`
- No weak hedging such as `could potentially`
- Consistent tense across the deck
- Parallel structure for titles covering similar content

## Score Bands

- 95-100: ready as written
- 90-94: minor polish only
- 80-89: improvement needed
- below 80: rewrite needed

## Output Shape

Use this structure when the user asks for a title review or when you run one implicitly:

```markdown
## Action Title Review

### Overall Score: [X]%

| # | Title | Score | Issues | Suggested Fix |
|---|-------|-------|--------|---------------|
| 1 | [title] | [X]% | [issues or Pass] | [rewrite or -] |

### Summary
- Titles passing (>=90%): X/Y
- Common issues: [...]
- Recommendation: PASS / REVISE
```

## Rewrite Heuristics

- Replace labels with conclusions
- Replace abstract claims with business impact
- Pull numbers into the title when available
- Prefer present tense unless the deck clearly describes a past event
