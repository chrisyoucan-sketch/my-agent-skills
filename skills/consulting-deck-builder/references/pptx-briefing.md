# PPTX Briefing

Use this reference only after the deck content is approved.
Its job is to convert content into a build brief for PowerPoint generation.

## Brand Intake

If the user wants a branded build brief and the brand system is missing, ask for:
- primary color
- accent color
- body text color
- dark background color
- logo placement
- font sizes, or confirm defaults

If the user only gives color names, infer reasonable hex values and say that you inferred them.

## Slide Types

Map each slide to one of these simple production types:
- cover
- title plus bullets
- table
- three-column
- four-card grid
- process flow
- closing or CTA

Do not overcomplicate the layout taxonomy.

## Output

Produce one copy-pasteable build brief that includes:
- slide count
- consistent design system
- one exact instruction block per slide
- general rules for title size, margins, logo placement, and closing slide treatment

## Build-Brief Rules

- use the approved deck titles and content verbatim unless the user asks for adaptation
- keep layout instructions concrete and deterministic
- specify colors and font sizes explicitly
- tell the builder to proceed slide by slide if interactive review is desired

## Handoff

If local slide generation is needed instead of a text brief:
- hand the approved content to `pptx-from-layouts`
- run `ppt-layout-polisher` afterward if spacing or overflow risk remains
