from __future__ import annotations

import argparse
import json

from layout_common import area, density_band, density_score, load_document, parse_page, usable_area


def score_slide_density(slide: dict, page) -> dict:
    used_area = sum(area(element) for element in slide.get("elements", []))
    fill_ratio = used_area / usable_area(page) if usable_area(page) else 0.0
    return {
        "slide_id": slide["id"],
        "used_area": round(used_area, 3),
        "usable_area": round(usable_area(page), 3),
        "fill_ratio": round(fill_ratio, 3),
        "density_band": density_band(fill_ratio),
        "density_score": density_score(fill_ratio),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score slide density from normalized geometry.")
    parser.add_argument("path", help="Path to layout JSON.")
    args = parser.parse_args()

    doc = load_document(args.path)
    page = parse_page(doc)
    output = {"slides": [score_slide_density(slide, page) for slide in doc["slides"]]}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
