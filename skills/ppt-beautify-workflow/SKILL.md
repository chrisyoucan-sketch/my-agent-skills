---
name: ppt-beautify-workflow
description: Orchestrate a high-quality PowerPoint creation and beautification workflow that combines visual direction setting, `.pptx` generation or editing, and geometry-aware layout QA. Use when Codex needs to create, redesign, restyle, or polish slides, decks, presentations, or `.pptx` files; when the user asks for PPT beautification, layout refinement, page structure, cover or section page design, consultant-style decks, or when a presentation needs both stronger design and stricter alignment, overflow, and readability checks.
---

# PPT Beautify Workflow

## Overview

Use this skill as the top-level controller for PPT work that should look designed rather than merely assembled. This workflow combines three layers:

- visual exploration and design language definition
- `.pptx` generation or editing
- post-generation layout polishing and QA

Use this skill together with these local skills when available:

- `ppt-layout-polisher` for spacing, alignment, overflow, and safety-margin QA
- `pptx`, `pptx-from-layouts`, or another installed PPTX skill for `.pptx` creation/editing
- `frontend-design` if available in the environment; if it is not available, apply the same design principles directly

## Workflow Decision Tree

Classify the request before doing any slide work:

1. `new deck`
- Use when no deck exists yet or the user wants a full rebuild from notes or an outline.

2. `major redesign`
- Use when a deck exists but the user wants a noticeably better visual language, upgraded cover/section/content pages, or a template/style shift.

3. `layout polish`
- Use when the story and content are mostly settled, but spacing, alignment, readability, overflow, or visual balance need repair.

4. `surgical edit`
- Use when fewer than roughly 30% of slides need text-only or small edits without changing the overall layout system.

## Phase 1: Build Inputs

Start by creating or updating lightweight planning artifacts only when they add clarity:

- Read [workflow.md](references/workflow.md) for the full process.
- Use [design-tokens-template.md](references/design-tokens-template.md) when the deck needs a new visual system.
- Use [slide-plan-template.md](references/slide-plan-template.md) when slide types or page structures are still fuzzy.

At minimum, determine:

- deck goal and audience
- language and tone
- delivery context: internal report, client deck, investor deck, pitch, workshop, product review, etc.
- whether the deck should preserve an existing template or brand
- whether the task is `new deck`, `major redesign`, `layout polish`, or `surgical edit`

## Phase 2: Visual Direction

When the user wants beautification, redesign, or a new deck, define a visual system before editing the presentation file.

If a `frontend-design` skill is available:

- Use it to explore 2 to 3 strong visual directions.
- Prefer sample pages for cover, section divider, body page, and data page.
- Ask for HTML/CSS or component-style mockups that can be translated into PowerPoint.

If `frontend-design` is not available:

- Apply the same principle directly: commit to one clear aesthetic direction and define it explicitly.
- Avoid generic SaaS defaults, timid palettes, and repetitive layouts.
- Translate the chosen direction into PowerPoint-safe decisions: colors, font families, title treatment, card style, chart containers, section pages, and footer rules.

Always extract the chosen direction into a reusable design token set before building slides.

## Phase 3: Create Or Edit The Deck

Choose the production path that best matches the task:

- Use a PPTX creation skill when creating a deck from scratch.
- Use `pptx-from-layouts` when a template or layout system already exists.
- Use surgical editing only for small text changes or targeted fixes.
- Regenerate instead of patch-editing if the change affects many layouts, page types, or visual patterns.

During production:

- map each slide to one primary page type
- keep cover, section, content, and data pages visually consistent
- prefer layout changes before shrinking text
- favor strong hierarchy and short, scannable copy

## Phase 4: Layout Polish And QA

Always run `ppt-layout-polisher` on any deck that is intended for delivery, especially after regeneration or redesign.

Read these references from the `ppt-layout-polisher` skill as needed:

- `references/slide-types.md`
- `references/layout-rules.md`
- `references/spacing-system.md`
- `references/typography-rules.md`
- `references/overflow-and-overlap-rules.md`
- `references/font-fallback-rules.md`
- `references/output-checklist.md`

Use the local wrapper script in this skill when a real `.pptx` file exists:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-layout-qa.ps1 -InputPath .\deck.pptx
powershell -ExecutionPolicy Bypass -File scripts/run-layout-qa.ps1 -InputPath .\deck.pptx -AutoFix -Output .\deck-fixed.pptx
```

Treat these as hard gates:

- important content stays inside the safety margin
- body text remains readable
- no text overlaps or out-of-bounds elements
- repeated objects align cleanly
- spacing is consistent across cards, columns, and tables
- slide density feels balanced rather than crowded or empty

## Phase 5: Final Review

Before declaring the deck done:

- use [qa-checklist.md](references/qa-checklist.md)
- convert the deck to images or thumbnails when visual inspection is needed
- re-check any slide touched by auto-fix or late content edits
- prefer splitting a crowded slide over forcing dense copy into one frame

## Output Expectations

When the task is substantial, aim to leave behind these artifacts where useful:

- a `design-tokens.md` file or equivalent notes
- a `slide-plan.md` file or equivalent page map
- a polished `.pptx`
- a layout validation report from the QA phase when a real deck exists

## Resource Map

Use these bundled files in this skill:

- [workflow.md](references/workflow.md): end-to-end operating procedure
- [design-tokens-template.md](references/design-tokens-template.md): capture the chosen visual system
- [slide-plan-template.md](references/slide-plan-template.md): map content to page types
- [qa-checklist.md](references/qa-checklist.md): final acceptance checklist
- [run-layout-qa.ps1](scripts/run-layout-qa.ps1): wrapper for layout validation and optional auto-fix
