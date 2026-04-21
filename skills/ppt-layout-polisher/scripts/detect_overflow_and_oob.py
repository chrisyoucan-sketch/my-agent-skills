from __future__ import annotations

import argparse
import json

from layout_common import enters_margin, estimate_text_capacity, is_text_bearing, load_document, out_of_bounds, parse_page


def detect_overflow_and_oob(slide: dict, page) -> dict:
    findings = {"text_overflow": [], "out_of_bounds": [], "margin_violations": []}
    for element in slide.get("elements", []):
        if out_of_bounds(element, page):
            findings["out_of_bounds"].append({"element_id": element["id"], "issue": "out-of-page-bounds"})
        if enters_margin(element, page):
            findings["margin_violations"].append({"element_id": element["id"], "issue": "enters-safety-margin"})
        if is_text_bearing(element):
            capacity = estimate_text_capacity(element)
            if capacity["overflow"] > 0:
                findings["text_overflow"].append(
                    {
                        "element_id": element["id"],
                        "issue": "estimated-text-overflow",
                        "needed_lines": int(capacity["needed_lines"]),
                        "max_lines": int(capacity["max_lines"]),
                    }
                )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect text overflow and out-of-bounds elements.")
    parser.add_argument("path", help="Path to layout JSON.")
    args = parser.parse_args()

    doc = load_document(args.path)
    page = parse_page(doc)
    output = {
        "slides": [
            {
                "slide_id": slide["id"],
                "findings": detect_overflow_and_oob(slide, page),
            }
            for slide in doc["slides"]
        ]
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
