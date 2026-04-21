from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TEXT_ROLES = {"title", "subtitle", "body", "label", "note", "caption"}
SAFE_CHINESE_FONTS = {"Microsoft YaHei", "DengXian", "SimSun", "Source Han Sans SC", "PingFang SC"}
SAFE_LATIN_FONTS = {"Aptos", "Calibri", "Arial", "Segoe UI", "Helvetica"}


@dataclass
class Page:
    width: float
    height: float
    unit: str
    margin: float


def load_document(path: str | Path) -> dict[str, Any]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    page = doc.get("page", {})
    if page.get("unit", "in") != "in":
        raise ValueError("Only inch-based documents are supported.")
    if "slides" not in doc or not isinstance(doc["slides"], list) or not doc["slides"]:
        raise ValueError("Document must contain a non-empty slides list.")
    return doc


def parse_page(doc: dict[str, Any]) -> Page:
    page = doc["page"]
    return Page(
        width=float(page["width"]),
        height=float(page["height"]),
        unit=page.get("unit", "in"),
        margin=float(page.get("margin", 0.6)),
    )


def iter_slides(doc: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for slide in doc["slides"]:
        yield slide


def is_text_bearing(element: dict[str, Any]) -> bool:
    return bool(str(element.get("text", "")).strip()) or element.get("text_role") in TEXT_ROLES


def area(element: dict[str, Any]) -> float:
    return float(element["w"]) * float(element["h"])


def usable_area(page: Page) -> float:
    usable_width = max(page.width - 2 * page.margin, 0.0)
    usable_height = max(page.height - 2 * page.margin, 0.0)
    return usable_width * usable_height


def intersects(a: dict[str, Any], b: dict[str, Any], min_gap: float = 0.0) -> bool:
    ax1 = float(a["x"]) - min_gap
    ay1 = float(a["y"]) - min_gap
    ax2 = float(a["x"]) + float(a["w"]) + min_gap
    ay2 = float(a["y"]) + float(a["h"]) + min_gap

    bx1 = float(b["x"])
    by1 = float(b["y"])
    bx2 = float(b["x"]) + float(b["w"])
    by2 = float(b["y"]) + float(b["h"])

    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1


def out_of_bounds(element: dict[str, Any], page: Page, tolerance: float = 0.01) -> bool:
    x = float(element["x"])
    y = float(element["y"])
    w = float(element["w"])
    h = float(element["h"])
    return x < -tolerance or y < -tolerance or x + w > page.width + tolerance or y + h > page.height + tolerance


def enters_margin(element: dict[str, Any], page: Page, tolerance: float = 0.0) -> bool:
    x = float(element["x"])
    y = float(element["y"])
    w = float(element["w"])
    h = float(element["h"])
    return (
        x < page.margin - tolerance
        or y < page.margin - tolerance
        or x + w > page.width - page.margin + tolerance
        or y + h > page.height - page.margin + tolerance
    )


def estimate_lines(text: str) -> int:
    lines = [line for line in text.replace("\r", "").split("\n")]
    return max(len(lines), 1)


def estimate_text_capacity(element: dict[str, Any]) -> dict[str, float]:
    text = str(element.get("text", "")).strip()
    font_size = float(element.get("font_size", 16))
    line_height = float(element.get("line_height", 1.2))
    padding = float(element.get("padding", 0.08))
    inner_width = max(float(element["w"]) - 2 * padding, 0.1)
    inner_height = max(float(element["h"]) - 2 * padding, 0.1)

    chars_per_inch = max(72.0 / (font_size * 0.55), 1.0)
    chars_per_line = max(int(inner_width * chars_per_inch), 1)
    max_lines = max(int(inner_height * 72.0 / (font_size * line_height)), 1)

    text_len = len(text.replace("\n", ""))
    explicit_lines = estimate_lines(text)
    estimated_needed_lines = max(explicit_lines, int(math.ceil(text_len / chars_per_line)))

    return {
        "chars_per_line": float(chars_per_line),
        "max_lines": float(max_lines),
        "needed_lines": float(estimated_needed_lines),
        "overflow": 1.0 if estimated_needed_lines > max_lines else 0.0,
    }


def density_band(fill_ratio: float) -> str:
    if fill_ratio < 0.35:
        return "underfilled"
    if fill_ratio > 0.72:
        return "overfilled"
    return "balanced"


def density_score(fill_ratio: float) -> int:
    target = 0.54
    distance = abs(fill_ratio - target)
    score = max(0.0, 100.0 - distance * 220.0)
    return int(round(score))


def alignment_stats(elements: list[dict[str, Any]]) -> dict[str, float]:
    if len(elements) < 2:
        return {"left_edge_variance": 0.0, "top_edge_variance": 0.0}

    left_edges = [round(float(e["x"]), 2) for e in elements]
    top_edges = [round(float(e["y"]), 2) for e in elements]
    return {
        "left_edge_variance": unique_edge_variance(left_edges),
        "top_edge_variance": unique_edge_variance(top_edges),
    }


def unique_edge_variance(values: list[float]) -> float:
    unique = len(set(values))
    return float(unique) / float(len(values))


def font_risk(element: dict[str, Any]) -> str | None:
    family = str(element.get("font_family", "")).strip()
    if not family:
        return "missing-font-family"
    if family in SAFE_CHINESE_FONTS or family in SAFE_LATIN_FONTS:
        return None
    return f"font-fallback-risk:{family}"
