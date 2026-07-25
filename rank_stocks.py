"""Rank a fundamentals CSV using the Magic Formula and save the sorted result.

Usage:
    python rank_stocks.py [--input path/to/magic_formula_nyse_DDMMYYYY.csv]
"""
import argparse
import sys

import pandas as pd

from magicformula.io_utils import latest_data_file, ranking_file_path
from magicformula.ranking import compute_ranking


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=str, default=None,
        help="Raw fundamentals CSV to rank (default: most recently collected file).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = args.input or latest_data_file()
    if not input_path:
        sys.exit("No fundamentals CSV found. Run collect_data.py first, or pass --input.")

    df = pd.read_csv(input_path)
    df_ranked = compute_ranking(df)

    output_path = ranking_file_path()
    df_ranked.to_csv(output_path, index=False)

    print(f"Ranked {len(df_ranked)} stocks from {input_path}")
    print(f"Saved to {output_path}")
    print(df_ranked.head(20))


if __name__ == "__main__":
    main()
