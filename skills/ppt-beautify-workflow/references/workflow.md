# PPT Beautify Workflow

## Goal

Run every deck through the same three-layer system:

1. visual direction
2. `.pptx` production
3. layout QA

Do not skip the visual-direction step when the user asks for beautification or redesign. Do not skip the QA step when the deck is intended for delivery.

## Standard Sequence

### 1. Classify the request

Choose one:

- `new deck`
- `major redesign`
- `layout polish`
- `surgical edit`

### 2. Gather the minimum context

Capture:

- objective
- audience
- language
- deck length or expected slide count
- source materials
- brand or template constraints
- deadline sensitivity

### 3. Define the design system

Create a compact `design-tokens.md` using [design-tokens-template.md](design-tokens-template.md).

For redesigns or new decks, define:

- aesthetic direction
- dominant color
- support colors
- accent color
- typography pairing or fallback strategy
- title treatment
- body page pattern
- section page pattern
- chart and table styling rules

### 4. Map content to slide types

Create a compact `slide-plan.md` using [slide-plan-template.md](slide-plan-template.md).

Each slide gets one primary type only:

- cover
- section
- agenda
- single-column
- two-column
- image-text
- comparison
- timeline
- table
- cards
- summary

If a slide feels overloaded, split it before production.

### 5. Produce the deck

Choose the right production path:

- from scratch: PPTX creation workflow
- from template: template/layout workflow
- small text-only changes: surgical edit workflow

Keep the design token file beside the deck while building so visual decisions stay stable.

### 6. Run layout QA

For a real `.pptx`, run the wrapper in `scripts/run-layout-qa.ps1`.

Recommended commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-layout-qa.ps1 -InputPath .\deck.pptx
powershell -ExecutionPolicy Bypass -File scripts/run-layout-qa.ps1 -InputPath .\deck.pptx -AutoFix -Output .\deck-fixed.pptx
```

### 7. Review and iterate

If QA reveals density, overlap, overflow, or alignment issues:

- change layout before shrinking fonts
- split slides before compressing content
- re-run QA after each meaningful layout revision

## Mode Guidance

### New deck

Use the full workflow. Do not start by directly writing slide XML or placing shapes.

### Major redesign

Preserve content where possible, but rebuild visual language and page structures first.

### Layout polish

Skip deep visual exploration if the brand system is already fixed. Focus on page type correction, spacing, and readability.

### Surgical edit

Keep the existing visual system. Only use layout QA if the edit changes text length, object count, or placement.
