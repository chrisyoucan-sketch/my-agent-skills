import argparse
import json
from pathlib import Path

from forecast_core import forecast_from_data


def main():
    parser = argparse.ArgumentParser(description="Forecast one company-quarter earnings.")
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument("--scenario", default="base", choices=["base", "bull", "bear"])
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = forecast_from_data(data, scenario=args.scenario)
    text = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        out = Path(args.output)
        out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
