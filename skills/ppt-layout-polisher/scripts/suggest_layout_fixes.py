from __future__ import annotations

import argparse
import json

from detect_overflow_and_oob import detect_overflow_and_oob
from detect_text_overlap import detect_text_overlap
from layout_common import density_band, font_risk, load_document, parse_page
from score_slide_density import score_slide_density


def suggest_fixes(slide: dict, page) -> list[str]:
    suggestions: list[str] = []
    density = score_slide_density(slide, page)
    overlaps = detect_text_overlap(slide, page)
    bounds = detect_overflow_and_oob(slide, page)

    if density["density_band"] == "overfilled":
        suggestions.append("Split the slide or switch to a higher-capacity layout before shrinking text.")
    if density["density_band"] == "underfilled":
        suggestions.append("Enlarge the focal block or tighten the composition around a clearer alignment axis.")
    if overlaps:
        suggestions.append("Separate overlapping text-bearing elements and restore at least 0.04 in of clear gap.")
    if bounds["text_overflow"]:
        suggestions.append("Increase text-box height, reduce copy, or split the content across slides.")
    if bounds["out_of_bounds"]:
        suggestions.append("Move out-of-bounds elements back inside the page and preserve the outer safety margin.")
    if bounds["margin_violations"]:
        suggestions.append("Pull elements inward to respect the slide safety margin.")

    for element in slide.get("elements", []):
        risk = font_risk(element)
        if risk:
            suggestions.append(f"Replace risky font on element {element['id']} with an approved fallback chain.")

    text_counts = sum(1 for element in slide.get("elements", []) if element.get("text"))
    if density_band(density["fill_ratio"]) == "balanced" and not overlaps and not bounds["text_overflow"] and text_counts > 4:
        suggestions.append("Check whether several text blocks can share stronger left-edge alignment or become cards.")

    if not suggestions:
        suggestions.append("Layout passes the current automatic checks. Perform a final visual review for hierarchy and weight.")
    return suggestions


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest layout fixes from normalized geometry.")
    parser.add_argument("path", help="Path to layout JSON.")
    args = parser.parse_args()

    doc = load_document(args.path)
    page = parse_page(doc)
    output = {
        "slides": [
            {
                "slide_id": slide["id"],
                "suggestions": suggest_fixes(slide, page),
            }
            for slide in doc["slides"]
        ]
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
