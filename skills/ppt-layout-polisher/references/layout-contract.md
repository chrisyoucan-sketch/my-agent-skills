# Layout Contract

The scripts in `scripts/` read a normalized JSON document.
This keeps the skill independent from any specific `.pptx` library.

## Document Shape

```json
{
  "page": {
    "width": 13.333,
    "height": 7.5,
    "unit": "in",
    "margin": 0.6
  },
  "slides": [
    {
      "id": "slide-1",
      "type": "two-column",
      "title": "Optional title",
      "elements": [
        {
          "id": "title",
          "kind": "title",
          "text_role": "title",
          "x": 0.8,
          "y": 0.5,
          "w": 11.7,
          "h": 0.7,
          "text": "Quarterly Review",
          "font_family": "Microsoft YaHei",
          "font_size": 28,
          "line_height": 1.2,
          "padding": 0.08
        }
      ]
    }
  ]
}
```

## Required Page Fields

- `width`
- `height`
- `unit`: must be `in`
- `margin`: optional outer safety margin in inches; defaults to `0.6`

## Required Slide Fields

- `id`
- `type`
- `elements`

## Required Element Fields

- `id`
- `kind`
- `x`
- `y`
- `w`
- `h`

## Recommended Element Fields

- `text_role`: `title`, `subtitle`, `body`, `label`, `note`, `caption`, or `none`
- `text`
- `font_family`
- `font_size`
- `line_height`
- `padding`

## Kind Values

Recommended `kind` values:

- `title`
- `subtitle`
- `text`
- `image`
- `shape`
- `chart`
- `table`
- `card`
- `icon`
- `group`

The scripts treat elements with a non-empty `text` field as text-bearing.

## Coordinate Rules

- `x`, `y`, `w`, and `h` are measured in inches
- `x`, `y` represent top-left origin from the page corner
- all measurements must be non-negative
- `w` and `h` must be positive
