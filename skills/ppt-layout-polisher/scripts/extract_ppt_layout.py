from __future__ import annotations

import argparse
import json

from pptx_layout_io import export_layout_json, pptx_to_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract normalized layout JSON from a PPTX file.")
    parser.add_argument("pptx_path", help="Path to the input .pptx file.")
    parser.add_argument("-o", "--output", help="Optional output JSON path.")
    parser.add_argument("--margin", type=float, default=0.6, help="Safety margin in inches. Default: 0.6")
    args = parser.parse_args()

    if args.output:
        export_layout_json(args.pptx_path, args.output, margin=args.margin)
        return

    print(json.dumps(pptx_to_document(args.pptx_path, margin=args.margin), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
