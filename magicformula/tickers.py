"""Fetch and filter the universe of NYSE / NASDAQ common-stock tickers."""
import pandas as pd

NASDAQ_LISTED_URL = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
OTHER_LISTED_URL = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"

INCLUDE_KEYWORDS = ["Common Stock", "Ordinary Shares", "Class A", "Class B", "Class C"]
EXCLUDE_KEYWORDS = [
    "Preferred", "ETF", "Unit", "Warrant", "Rights", "Bond", "Note", "Index", "Trust",
]


def clean_ticker(ticker: str | None) -> str | None:
    """Normalize a raw ticker symbol into the format yfinance expects."""
    if pd.isna(ticker):
        return None
    return str(ticker).replace("$", "-").replace(".", "-")


def fetch_nyse_common_stock_tickers(max_tickers: int | None = None) -> list[str]:
    """Download the NASDAQ symbol directories and return cleaned NYSE common-stock tickers."""
    nasdaq = pd.read_csv(NASDAQ_LISTED_URL, sep="|")
    other = pd.read_csv(OTHER_LISTED_URL, sep="|")

    nyse = other[other["Exchange"] == "N"]
    listings = pd.concat([nasdaq, nyse], ignore_index=True)

    security_name = listings["Security Name"]
    mask_include = security_name.str.contains("|".join(INCLUDE_KEYWORDS), case=False, na=False)
    mask_exclude = ~security_name.str.contains("|".join(EXCLUDE_KEYWORDS), case=False, na=False)
    mask = mask_include & mask_exclude

    tickers = [
        clean_ticker(t)
        for t in listings.loc[mask, "Symbol"]
        if pd.notna(t)
    ]

    if isinstance(max_tickers, int) and max_tickers > 0:
        tickers = tickers[:max_tickers]

    return tickers
