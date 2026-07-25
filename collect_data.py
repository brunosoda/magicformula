"""Fetch NYSE/NASDAQ common-stock fundamentals and save them to a date-stamped CSV.

Usage:
    python collect_data.py [--max-tickers 200] [--sleep 0.5]
"""
import argparse

from magicformula.fundamentals import collect_fundamentals
from magicformula.io_utils import data_file_path
from magicformula.tickers import fetch_nyse_common_stock_tickers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-tickers", type=int, default=None,
        help="Limit the number of tickers processed (default: no limit).",
    )
    parser.add_argument(
        "--sleep", type=float, default=0.5,
        help="Delay in seconds between API calls, to avoid rate limiting (default: 0.5).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tickers = fetch_nyse_common_stock_tickers(max_tickers=args.max_tickers)
    print(f"Fetched {len(tickers)} tickers to process.")

    def on_progress(i, total, ticker, result):
        status = f"EY={result['EY']:.4f}, ROC={result['ROC']}" if result else "insufficient data"
        print(f"[{i}/{total}] {ticker}: {status}")

    df = collect_fundamentals(tickers, sleep_seconds=args.sleep, on_progress=on_progress)

    output_path = data_file_path()
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")


if __name__ == "__main__":
    main()
