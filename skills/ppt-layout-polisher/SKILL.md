---
name: ppt-layout-polisher
description: Plan, refine, and quality-check PowerPoint slide layouts so slides stay tidy, readable, aligned, and visually balanced. Use when Codex needs to create or repair `.pptx` slide layouts, choose page structures, distribute content across slides, prevent overcrowding or excessive blank space, avoid text-box collisions, prevent text overlap or out-of-bounds elements, reduce font fallback and garbled text risk, or adjust alignment and spacing by visual design rules.
---

# PPT Layout Polisher

## Overview

Turn raw slide content into balanced, presentation-ready layouts.
Prioritize layout quality over squeezing all content onto one page.
Treat each slide as a composition problem with three non-negotiable goals:

- preserve readability
- preserve spatial order
- preserve visual balance

Use this skill together with any `.pptx` creation or editing workflow.
This skill focuses on layout decisions, spacing, alignment, overflow prevention, and post-generation quality control.

## Workflow

1. Classify the slide before placing anything.
- Read [references/slide-types.md](references/slide-types.md).
- Map each slide to one primary type only.
- Prefer `cover`, `section`, `agenda`, `single-column`, `two-column`, `image-text`, `comparison`, `timeline`, `table`, `cards`, or `summary`.
- If a slide does not fit one of these types, simplify the content first instead of inventing a dense custom layout.

2. Estimate content density.
- Read [references/layout-rules.md](references/layout-rules.md) and [references/spacing-system.md](references/spacing-system.md).
- Judge whether the slide is `underfilled`, `balanced`, or `overfilled`.
- Use layout changes before using small font sizes.
- If content is overfilled, do one of these in order:
  - split the slide
  - change the layout type
  - reduce secondary copy
  - convert prose into bullets
  - reduce font size within the allowed range

3. Apply typography rules.
- Read [references/typography-rules.md](references/typography-rules.md).
- Keep clear hierarchy between title, subtitle, body, labels, and notes.
- Do not let body text become too small to read.
- Keep line lengths moderate. Prefer narrower text blocks over very long lines.

4. Place elements on a grid.
- Use the margins, gutters, and rhythm in [references/spacing-system.md](references/spacing-system.md).
- Align related elements to shared left edges, centers, or baselines.
- Do not place objects by eye alone when a stable alignment rule is available.

5. Run safety checks before finalizing.
- Read [references/overflow-and-overlap-rules.md](references/overflow-and-overlap-rules.md) and [references/font-fallback-rules.md](references/font-fallback-rules.md).
- Reject layouts with:
  - text-box overlap
  - text running outside a shape
  - objects crossing page bounds
  - inconsistent edge alignment
  - unreadable density
  - unsupported fonts likely to cause garbled text

6. Use the scripts when geometry data is available.
- Read [references/layout-contract.md](references/layout-contract.md).
- If the input is a real `.pptx`, first use `scripts/extract_ppt_layout.py` or `scripts/validate_ppt_layout.py`.
- Use `scripts/inspect_ppt_layout.py` to inspect one layout JSON document.
- Use `scripts/detect_text_overlap.py` and `scripts/detect_overflow_and_oob.py` to isolate geometry failures.
- Use `scripts/score_slide_density.py` to score spacing balance.
- Use `scripts/suggest_layout_fixes.py` to turn findings into correction actions.
- Use `scripts/auto_fix_ppt_layout.py` for first-pass repair of margins, alignment drift, overlap risk, and font fallback issues in `.pptx` files.

7. Iterate until the slide passes.
- Follow [references/output-checklist.md](references/output-checklist.md).
- If the slide fails any hard gate, revise the layout and check again.
- Do not accept a layout only because every item technically fits.

## Quality Gates

- Reject slides where body text must drop below the minimum size in [references/typography-rules.md](references/typography-rules.md) unless the user explicitly accepts the tradeoff.
- Reject slides with any overlap between text-bearing elements.
- Reject slides where elements enter the outer safety margin.
- Reject slides with clearly uneven visual weight unless the slide type intentionally calls for an asymmetrical hero layout.
- Reject slides that are mostly empty unless the slide is a `cover` or `section` page.
- Reject slides that are packed edge-to-edge without breathable whitespace.
- Reject font choices outside the approved fallback chains in [references/font-fallback-rules.md](references/font-fallback-rules.md) when the deck is intended for Windows-based editing or playback.

## References

- [references/slide-types.md](references/slide-types.md): slide archetypes and default placement intent
- [references/layout-rules.md](references/layout-rules.md): density, visual balance, and placement rules
- [references/typography-rules.md](references/typography-rules.md): font hierarchy, line length, and sizing limits
- [references/spacing-system.md](references/spacing-system.md): margins, gutters, spacing scale, and alignment rhythm
- [references/overflow-and-overlap-rules.md](references/overflow-and-overlap-rules.md): overlap, bounds, and overflow gates
- [references/font-fallback-rules.md](references/font-fallback-rules.md): safe font stacks and anti-garbled-text rules
- [references/output-checklist.md](references/output-checklist.md): final QA checklist
- [references/layout-contract.md](references/layout-contract.md): JSON input schema for the scripts
- [references/example-layout.json](references/example-layout.json): sample geometry document for testing

## Script Usage

Run the scripts from the skill folder or pass full paths.

```powershell
python scripts/extract_ppt_layout.py input.pptx -o layout.json
python scripts/validate_ppt_layout.py input.pptx -o report.json
python scripts/auto_fix_ppt_layout.py input.pptx -o fixed.pptx --report fix-report.json
python scripts/inspect_ppt_layout.py references/example-layout.json
python scripts/detect_text_overlap.py references/example-layout.json
python scripts/detect_overflow_and_oob.py references/example-layout.json
python scripts/score_slide_density.py references/example-layout.json
python scripts/suggest_layout_fixes.py references/example-layout.json
```

Use the scripts as a geometry QA layer after generating slide elements.
If a `.pptx` editing pipeline can export element positions, normalize that output into the contract in [references/layout-contract.md](references/layout-contract.md) first.
