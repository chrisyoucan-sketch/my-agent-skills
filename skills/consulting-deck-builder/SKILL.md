---
name: consulting-deck-builder
description: Build consultant-ready presentation storylines and slide content using the Pyramid Principle, SCR flow, and MBB-style action-title standards. Use when Codex needs to turn raw notes, documents, meeting output, or business context into a McKinsey-style deck outline, ghost deck, action titles, slide bullets, speaker notes, review feedback, or a PowerPoint build brief.
---

# Consulting Deck Builder

## Overview

Turn raw business context into a consultant-style deck before touching slide design.
Prioritize storyline clarity, action titles, and proof-based slide content.

Use this skill when the user wants:
- a McKinsey-style or consultant-style deck
- a ghost deck from messy notes or source files
- stronger action titles, storyline, or slide logic
- a PowerPoint build brief that can be handed to a `.pptx` workflow

If the user needs the actual `.pptx` file after the content is ready, hand off to:
- `pptx-from-layouts` for generation from structured outline/content
- `ppt-layout-polisher` for final spacing, overflow, and layout QA

## Workflow

1. Build the deck story first.
- Read [references/deck-builder.md](references/deck-builder.md).
- Extract situation, complication, resolution, evidence, audience, and decision needed.
- Decide the slide count from context instead of asking the user to outline the deck.

2. Produce a ghost deck.
- Write one action title per slide.
- Keep titles under 15 words, in active voice, with a clear so-what.
- Where the source provides numbers, use them.
- Present titles as a numbered deck table with a confidence score.

3. Review titles before expanding content.
- Read [references/action-title-review.md](references/action-title-review.md).
- Tighten any title that is vague, label-like, hedged, or non-executive.

4. Review horizontal logic.
- Read [references/storyline-review.md](references/storyline-review.md).
- Check whether the titles alone tell a full SCR narrative.
- Remove redundancy and patch missing logic steps before writing slide bodies.

5. Write slide content.
- Use 3-5 bullets per slide that prove the title, not merely relate to it.
- Add one callout per slide when helpful.
- Add 2-3 sentences of speaker notes.
- Add source tags for factual claims.

6. Review vertical logic.
- Read [references/slide-content-review.md](references/slide-content-review.md).
- Fix any bullet that fails to prove the title or any numeric claim that lacks traceability.

7. Prepare for PowerPoint only after the content passes review.
- If the user wants a build prompt for PowerPoint, read [references/pptx-briefing.md](references/pptx-briefing.md).
- If the user wants a `.pptx` generated locally, convert the approved deck into the input format expected by the selected PPT skill.

## Output Contract

Default output order:
1. Ghost deck table with action titles and confidence scores
2. Short storyline read-through in 3-4 sentences
3. Full slide content with bullets, callouts, notes, and sources
4. Review findings and fixes if any
5. PPT build brief only if the user asks for slide production

## Rules

- Do not ask the user to draft titles or structure if enough context exists to infer them.
- Do not use label titles like `Overview`, `Next steps`, or `Market context` unless the user explicitly wants generic headings.
- Do not use buzzwords such as `leverage`, `harness`, `transformative`, `synergy`, or `paradigm`.
- Do not use em dashes.
- Keep the deck decision-oriented. The final slides should make the audience's required decision obvious.
- Treat every numeric claim as auditable. If a number is missing or weakly supported, say so.

## References

- [references/deck-builder.md](references/deck-builder.md): main deck-construction process
- [references/action-title-review.md](references/action-title-review.md): title scoring and rewrite rules
- [references/storyline-review.md](references/storyline-review.md): horizontal logic and SCR checks
- [references/slide-content-review.md](references/slide-content-review.md): vertical logic and fact-check checks
- [references/pptx-briefing.md](references/pptx-briefing.md): transform approved content into a PowerPoint build brief
