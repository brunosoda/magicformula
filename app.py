"""Streamlit dashboard for the Magic Formula stock screener.

Run with:
    streamlit run app.py
"""
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from magicformula.io_utils import latest_data_file, ranking_file_path
from magicformula.ranking import compute_ranking

# Sequential "blue" ramp from the design system, dark -> light, so the best
# (lowest) score renders darkest and quality fades toward the light end.
SEQUENTIAL_BLUE_DARK_TO_LIGHT = [
    "#0d366b", "#104281", "#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5",
    "#5598e7", "#6da7ec", "#86b6ef", "#9ec5f4", "#b7d3f6", "#cde2fb",
]

st.set_page_config(page_title="Magic Formula Screener", page_icon="📈", layout="wide")


@st.cache_data
def load_ranking(path: str, mtime: float) -> pd.DataFrame:
    # mtime is part of the cache key so the cache invalidates when the file changes.
    return pd.read_csv(path)


def resolve_ranking_dataframe() -> tuple[pd.DataFrame | None, str | None]:
    """Load the saved ranking CSV if present, otherwise rank the latest raw data on the fly."""
    ranking_path = ranking_file_path()
    if os.path.exists(ranking_path):
        return load_ranking(ranking_path, os.path.getmtime(ranking_path)), ranking_path

    data_path = latest_data_file()
    if data_path:
        raw = load_ranking(data_path, os.path.getmtime(data_path))
        return compute_ranking(raw), data_path

    return None, None


st.title("📈 Magic Formula Stock Screener")
st.caption(
    "Joel Greenblatt's Magic Formula ranks stocks by combining "
    "**Earnings Yield** (cheapness) and **Return on Capital** (quality). "
    "Lower combined score = better rank."
)

df, source_path = resolve_ranking_dataframe()

if df is None:
    st.warning(
        "No data found yet. Run `python collect_data.py` to fetch fundamentals, "
        "then `python rank_stocks.py` to build the ranking."
    )
    st.stop()

data_date = datetime.fromtimestamp(os.path.getmtime(source_path)).strftime("%Y-%m-%d %H:%M")

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")
only_valid = st.sidebar.checkbox(
    "Only valid stocks (positive EBIT & EV)", value=True,
    help="Greenblatt excludes companies with negative earnings or enterprise value.",
)
top_n = st.sidebar.slider("Show top N stocks", min_value=5, max_value=100, value=20, step=5)
ticker_search = st.sidebar.text_input("Search ticker").strip().upper()

filtered = df.copy()
if only_valid:
    filtered = filtered[filtered["out_in"] == "in"]
if ticker_search:
    filtered = filtered[filtered["Ticker"].str.upper().str.contains(ticker_search, na=False)]

filtered = filtered.sort_values("score").reset_index(drop=True)
top_stocks = filtered.head(top_n)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Stocks screened", len(df))
col2.metric("Passing filter", len(filtered))
col3.metric("Top pick", top_stocks.iloc[0]["Ticker"] if len(top_stocks) else "—")
col4.metric("Data as of", data_date)

st.divider()

# ---------------------------------------------------------------------------
# Ranking table
# ---------------------------------------------------------------------------
tab_table, tab_charts = st.tabs(["📋 Ranking table", "📊 Charts"])

with tab_table:
    st.subheader(f"Top {len(top_stocks)} ranked stocks")
    display_df = top_stocks[["Ticker", "EBIT", "EV", "EY", "ROC", "rank_EY", "rank_ROC", "score"]].copy()
    display_df.insert(0, "Rank", range(1, len(display_df) + 1))

    st.dataframe(
        display_df,
        hide_index=True,
        width='stretch',
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="%d"),
            "EBIT": st.column_config.NumberColumn("EBIT", format="compact"),
            "EV": st.column_config.NumberColumn("Enterprise Value", format="compact"),
            "EY": st.column_config.NumberColumn("Earnings Yield", format="percent"),
            "ROC": st.column_config.NumberColumn("Return on Capital", format="percent"),
            "rank_EY": st.column_config.NumberColumn("EY Rank", format="%d"),
            "rank_ROC": st.column_config.NumberColumn("ROC Rank", format="%d"),
            "score": st.column_config.NumberColumn("Score", help="rank_EY + rank_ROC, lower is better"),
        },
    )

    st.download_button(
        "Download filtered results as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="magic_formula_filtered.csv",
        mime="text/csv",
    )

with tab_charts:
    if top_stocks.empty:
        st.info("No stocks match the current filters.")
    else:
        st.subheader(f"Top {len(top_stocks)} by score")
        bar_df = top_stocks.sort_values("score", ascending=False)
        fig_bar = px.bar(
            bar_df,
            x="score",
            y="Ticker",
            orientation="h",
            color="score",
            color_continuous_scale=SEQUENTIAL_BLUE_DARK_TO_LIGHT,
            labels={"score": "Score (lower is better)"},
        )
        fig_bar.update_layout(
            yaxis={"categoryorder": "total descending"},
            coloraxis_colorbar_title="Score",
            height=max(350, 22 * len(bar_df)),
        )
        st.plotly_chart(fig_bar, width='stretch', theme="streamlit")

        st.subheader("Earnings Yield vs. Return on Capital")
        scatter_df = filtered.dropna(subset=["EY", "ROC"])
        fig_scatter = px.scatter(
            scatter_df,
            x="EY",
            y="ROC",
            color="score",
            color_continuous_scale=SEQUENTIAL_BLUE_DARK_TO_LIGHT,
            hover_name="Ticker",
            hover_data={"EBIT": ":.2s", "EV": ":.2s", "score": True, "EY": ":.1%", "ROC": ":.1%"},
            labels={"EY": "Earnings Yield", "ROC": "Return on Capital", "score": "Score"},
        )
        fig_scatter.update_xaxes(tickformat=".0%")
        fig_scatter.update_yaxes(tickformat=".0%")
        fig_scatter.update_layout(coloraxis_colorbar_title="Score")
        st.plotly_chart(fig_scatter, width='stretch', theme="streamlit")
