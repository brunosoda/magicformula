# Magic Formula NYSE Stock Screener

A Python implementation of Joel Greenblatt's Magic Formula investing strategy for NYSE/NASDAQ-listed stocks. It screens and ranks stocks based on earnings yield (EY) and return on capital (ROC), and ships a Streamlit dashboard to explore the results.

## 📋 Overview

The Magic Formula is a quantitative investment strategy developed by Joel Greenblatt that ranks stocks based on two key metrics:
- **Earnings Yield (EY)**: EBIT / Enterprise Value - measures how cheap a stock is
- **Return on Capital (ROC)**: EBIT / (Net Working Capital + Net Fixed Assets) - measures how efficiently a company uses its capital

The project has three parts:
1. **Data collection** (`collect_data.py`) - fetches fundamental data for NYSE/NASDAQ stocks
2. **Ranking** (`rank_stocks.py`) - ranks stocks by combined EY + ROC score
3. **Dashboard** (`app.py`) - a Streamlit app to browse, filter, and chart the ranked results

Shared logic lives in the `magicformula/` package so all three entry points stay in sync.

## 📁 Project Structure

```
magicformula/
├── magicformula/            # Core library
│   ├── tickers.py           # Fetch & filter the NYSE/NASDAQ ticker universe
│   ├── fundamentals.py      # Pull EBIT/EV/EY/ROC per ticker via yfinance
│   ├── ranking.py           # Compute the Magic Formula ranking
│   └── io_utils.py          # Shared, relative file-path helpers
├── collect_data.py          # CLI: fetch fundamentals -> magic_formula_nyse_DDMMYYYY.csv
├── rank_stocks.py           # CLI: rank a fundamentals CSV -> ranking_magic_formula_nyse.csv
├── app.py                   # Streamlit dashboard
├── requirements.txt
└── README.md
```

## 📦 Requirements

```bash
pip install -r requirements.txt
```

- `pandas` - data manipulation and CSV handling
- `yfinance` - Yahoo Finance API for stock fundamentals
- `yahoo-fin` - additional Yahoo Finance utilities
- `streamlit` - the interactive dashboard
- `plotly` - charts inside the dashboard

## 🔧 Usage

### Step 1: Collect stock data

```bash
python collect_data.py                      # all tickers
python collect_data.py --max-tickers 200     # limit for a quick run
python collect_data.py --sleep 1.0           # slower, gentler on rate limits
```

Fetches NYSE/NASDAQ tickers, filters for common stocks, retrieves fundamentals, and saves `magic_formula_nyse_DDMMYYYY.csv` in the project root.

### Step 2: Rank stocks

```bash
python rank_stocks.py                        # ranks the most recently collected CSV
python rank_stocks.py --input path/to/file.csv
```

Adds `rank_EY`, `rank_ROC`, `score` (lower is better) and `out_in` (excludes negative EBIT/EV, per Greenblatt's criteria), then saves `ranking_magic_formula_nyse.csv`.

### Step 3: Explore the results in Streamlit

```bash
streamlit run app.py
```

Opens a dashboard with:
- **KPIs**: stocks screened, stocks passing the filter, top pick, data freshness
- **Ranking table**: sortable/filterable, with percent/compact-number formatting and a CSV download
- **Charts**: top-N stocks by score, and an Earnings Yield vs. Return on Capital scatter, both colored by score
- **Sidebar filters**: valid-stocks-only toggle, top-N slider, ticker search

If `ranking_magic_formula_nyse.csv` doesn't exist yet, the app will rank the most recent raw data file on the fly.

## 📊 Data Columns

### Raw fundamentals (`magic_formula_nyse_*.csv`)

| Column | Description |
|--------|-------------|
| Ticker | Stock symbol |
| EBIT | Earnings Before Interest and Taxes |
| EV | Enterprise Value (Market Cap + Debt - Cash) |
| EY | Earnings Yield (EBIT / EV) |
| ROC | Return on Capital (EBIT / (NWC + Net PPE)) |

### Ranking (`ranking_magic_formula_nyse.csv`)

Includes all columns above plus:
- `rank_EY`: rank by Earnings Yield (1 = highest)
- `rank_ROC`: rank by Return on Capital (1 = highest)
- `score`: combined rank (`rank_EY + rank_ROC`, lower is better)
- `out_in`: filter status (`in` = valid, `out` = negative EBIT/EV)

## 🎯 How the Magic Formula Works

1. **Earnings Yield (EY)** - how cheap a stock is relative to its earnings. Higher EY = cheaper. `EBIT / Enterprise Value`
2. **Return on Capital (ROC)** - how efficiently a company uses its capital. Higher ROC = more efficient. `EBIT / (Net Working Capital + Net Fixed Assets)`
3. **Ranking** - stocks are ranked separately by EY and ROC, then combined; the best stocks have the lowest combined score. Stocks with negative EBIT or EV are filtered out.

## ⚠️ Important Notes

- **API rate limits**: Yahoo Finance may throttle requests; increase `--sleep` in `collect_data.py` if you hit errors.
- **Data availability**: not all stocks have complete fundamentals; those are skipped automatically.
- **Market hours**: data is most accurate when markets are closed.
- **Run time**: collecting the full universe (~2,600 tickers) can take 30+ minutes.

## 📚 References

- [The Little Book That Beats the Market](https://www.magicformulainvesting.com/) by Joel Greenblatt

## 📄 License

This project is provided as-is for educational and research purposes.
