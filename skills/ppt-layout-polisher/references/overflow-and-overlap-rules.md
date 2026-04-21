# Overflow And Overlap Rules

## Hard Failures

Reject the slide if any of these occur:

- one text-bearing element overlaps another text-bearing element
- text crosses the page bounds
- an element enters the safety margin without intentional full-bleed treatment
- body text is clipped by its text box
- two cards or columns visibly collide

## Soft Failures

Revise the slide if any of these occur:

- gap inconsistency between peer elements is visually obvious
- columns are nominally aligned but not actually sharing edges
- text blocks feel cramped due to low internal padding
- whitespace is concentrated in one corner while the rest is congested

## Overflow Response Order

When text does not fit:

1. increase the text box height if room exists
2. widen the text box if it does not break the layout
3. shorten the line length by changing layout type
4. reduce copy
5. split the content across slides
6. reduce font size only within the allowed range

Do not resolve overflow by forcing text to sit on top of nearby objects.

## Overlap Thresholds For Checks

For automated geometry checks:

- treat any positive-area intersection as a failure for text elements
- treat less than `0.04 in` separation between text-bearing elements as a collision risk
- treat any page-bound overflow beyond `0.01 in` as out of bounds
