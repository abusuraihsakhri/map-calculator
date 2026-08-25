#!/usr/bin/env python3
"""CLI for Mean Arterial Pressure (MAP) Calculator."""
import argparse
import json
import sys

from map_calc import calculate_map, process_csv


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="map-calculator",
        description="Mean Arterial Pressure (MAP) Calculator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single calculation
    single = subparsers.add_parser("single", help="Single patient calculation")
    single.add_argument("--sbp", type=float, required=True, help="Systolic BP (mmHg)")
    single.add_argument("--dbp", type=float, required=True, help="Diastolic BP (mmHg)")
    single.add_argument("--hr", type=float, default=None, help="Heart rate (bpm)")
    single.add_argument("--icp", type=float, default=None, help="Intracranial pressure (mmHg)")

    # Batch processing
    batch = subparsers.add_parser("batch", help="Batch process CSV")
    batch.add_argument("-i", "--input", required=True, help="Input CSV path")
    batch.add_argument("-o", "--output", default="results.csv", help="Output CSV path")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_map(args.sbp, args.dbp, hr=args.hr, icp=args.icp)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "batch":
        results = process_csv(args.input, args.output)
        print(f"Processed {len(results)} records -> {args.output}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
