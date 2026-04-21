from __future__ import annotations

import argparse
import json

from layout_common import intersects, is_text_bearing, load_document, parse_page


def detect_text_overlap(slide: dict, page) -> list[dict]:
    del page
    elements = slide.get("elements", [])
    findings = []
    for index, left in enumerate(elements):
        if not is_text_bearing(left):
            continue
        for right in elements[index + 1 :]:
            if not is_text_bearing(right):
                continue
            if intersects(left, right, min_gap=0.04):
                findings.append(
                    {
                        "left": left["id"],
                        "right": right["id"],
                        "issue": "text-overlap-or-collision-risk",
                    }
                )
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect overlap between text-bearing elements.")
    parser.add_argument("path", help="Path to layout JSON.")
    args = parser.parse_args()

    doc = load_document(args.path)
    page = parse_page(doc)
    output = {
        "slides": [
            {
                "slide_id": slide["id"],
                "overlaps": detect_text_overlap(slide, page),
            }
            for slide in doc["slides"]
        ]
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
