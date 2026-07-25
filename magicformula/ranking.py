"""Rank stocks by Joel Greenblatt's Magic Formula: combined Earnings Yield + Return on Capital rank."""
import pandas as pd


def compute_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Add rank/score/status columns and sort so the best-ranked stocks come first."""
    df = df.copy()
    df["rank_EY"] = df["EY"].rank(ascending=False)
    df["rank_ROC"] = df["ROC"].rank(ascending=False)
    df["score"] = df["rank_EY"] + df["rank_ROC"]

    # Greenblatt excludes companies with negative earnings or enterprise value.
    df["out_in"] = df.apply(
        lambda row: "out" if row["EBIT"] <= 0 or row["EV"] <= 0 else "in",
        axis=1,
    )

    return df.sort_values(by=["out_in", "score"]).reset_index(drop=True)
