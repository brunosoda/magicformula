"""Pull Magic Formula fundamentals (EBIT, EV, EY, ROC) for individual tickers via yfinance."""
import time
from collections.abc import Callable, Iterable

import pandas as pd
import yfinance as yf

EBIT_KEYS = ["EBIT", "Operating Income"]
CASH_KEYS = ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]


def _first_available(statement: pd.DataFrame, keys: list[str]):
    for key in keys:
        if key in statement.index:
            return statement.loc[key].iloc[0]
    return None


def get_fundamentals(ticker: str) -> dict | None:
    """Fetch EBIT, EV, EY and ROC for a single ticker. Returns None if data is insufficient."""
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.income_stmt
        balance = stock.balance_sheet
        fast = stock.fast_info

        ebit = _first_available(income_stmt, EBIT_KEYS)
        market_cap = fast.get("marketCap", None)
        total_debt = balance.loc["Total Debt"].iloc[0] if "Total Debt" in balance.index else 0
        cash = _first_available(balance, CASH_KEYS) or 0

        ev = market_cap + total_debt - cash if market_cap else None

        total_assets = balance.loc["Total Assets"].iloc[0] if "Total Assets" in balance.index else None
        current_liabilities = (
            balance.loc["Current Liabilities"].iloc[0]
            if "Current Liabilities" in balance.index
            else None
        )
        net_fixed_assets = balance.loc["Net PPE"].iloc[0] if "Net PPE" in balance.index else None

        if ebit is None or ev is None:
            return None

        earnings_yield = ebit / ev if ev else None
        net_working_capital = (
            (total_assets - current_liabilities) if total_assets and current_liabilities else None
        )
        return_on_capital = (
            ebit / (net_working_capital + net_fixed_assets)
            if ebit and net_working_capital and net_fixed_assets
            else None
        )

        return {
            "Ticker": ticker,
            "EBIT": ebit,
            "EV": ev,
            "EY": earnings_yield,
            "ROC": return_on_capital,
        }

    except Exception:
        return None


def collect_fundamentals(
    tickers: Iterable[str],
    sleep_seconds: float = 0.5,
    on_progress: Callable[[int, int, str, dict | None], None] | None = None,
) -> pd.DataFrame:
    """Fetch fundamentals for every ticker, sleeping between calls to avoid rate limits.

    `on_progress(index, total, ticker, result)` is called after each ticker, if provided.
    """
    tickers = list(tickers)
    results = []

    for i, ticker in enumerate(tickers, start=1):
        data = get_fundamentals(ticker)
        if data:
            results.append(data)
        if on_progress:
            on_progress(i, len(tickers), ticker, data)
        time.sleep(sleep_seconds)

    return pd.DataFrame(results)
