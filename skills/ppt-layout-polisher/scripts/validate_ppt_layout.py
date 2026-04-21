from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_ppt_layout import inspect_doc
from pptx_layout_io import export_layout_json, pptx_to_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate layout quality directly from a PPTX file.")
    parser.add_argument("pptx_path", help="Path to the input .pptx file.")
    parser.add_argument("-o", "--output", help="Optional output JSON report path.")
    parser.add_argument("--export-layout", help="Optional path for exported normalized layout JSON.")
    parser.add_argument("--margin", type=float, default=0.6, help="Safety margin in inches. Default: 0.6")
    args = parser.parse_args()

    doc = pptx_to_document(args.pptx_path, margin=args.margin)
    report = inspect_doc(doc)

    if args.export_layout:
        export_layout_json(args.pptx_path, args.export_layout, margin=args.margin)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
