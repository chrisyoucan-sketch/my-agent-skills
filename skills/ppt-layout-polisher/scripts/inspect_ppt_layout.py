from __future__ import annotations

import argparse
import json

from detect_overflow_and_oob import detect_overflow_and_oob
from detect_text_overlap import detect_text_overlap
from layout_common import (
    alignment_stats,
    area,
    density_band,
    density_score,
    enters_margin,
    font_risk,
    is_text_bearing,
    iter_slides,
    load_document,
    out_of_bounds,
    parse_page,
    usable_area,
)


def inspect_doc(doc: dict) -> dict:
    page = parse_page(doc)
    results = []
    for slide in iter_slides(doc):
        elements = slide.get("elements", [])
        used_area = sum(area(element) for element in elements)
        fill_ratio = used_area / usable_area(page) if usable_area(page) else 0.0
        overlaps = detect_text_overlap(slide, page)
        bounds = detect_overflow_and_oob(slide, page)
        alignment = alignment_stats(elements)
        font_risks = []

        for element in elements:
            risk = font_risk(element)
            if risk:
                font_risks.append({"element_id": element["id"], "issue": risk})
            if enters_margin(element, page):
                font_risks.append({"element_id": element["id"], "issue": "enters-safety-margin"})
            if out_of_bounds(element, page):
                font_risks.append({"element_id": element["id"], "issue": "out-of-page-bounds"})

        hard_failures = len(overlaps) + len(bounds["out_of_bounds"]) + len(bounds["text_overflow"])
        score = max(0, density_score(fill_ratio) - hard_failures * 20)

        results.append(
            {
                "slide_id": slide["id"],
                "slide_type": slide.get("type", "unknown"),
                "fill_ratio": round(fill_ratio, 3),
                "density_band": density_band(fill_ratio),
                "density_score": density_score(fill_ratio),
                "quality_score": score,
                "alignment": alignment,
                "overlaps": overlaps,
                "overflow_and_bounds": bounds,
                "font_risks": font_risks,
                "text_element_count": sum(1 for e in elements if is_text_bearing(e)),
                "status": "pass" if score >= 75 and hard_failures == 0 else "revise",
            }
        )
    return {"page": doc["page"], "slides": results}


def inspect_document(path: str) -> dict:
    return inspect_doc(load_document(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect PowerPoint layout geometry from normalized JSON.")
    parser.add_argument("path", help="Path to layout JSON.")
    args = parser.parse_args()
    print(json.dumps(inspect_document(args.path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
