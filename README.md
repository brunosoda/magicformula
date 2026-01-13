# Magic Formula NYSE Stock Screener

A Python implementation of Joel Greenblatt's Magic Formula investing strategy for NYSE-listed stocks. This tool automatically screens and ranks stocks based on earnings yield (EY) and return on capital (ROC) metrics.

## 📋 Overview

The Magic Formula is a quantitative investment strategy developed by Joel Greenblatt that ranks stocks based on two key metrics:
- **Earnings Yield (EY)**: EBIT / Enterprise Value - measures how cheap a stock is
- **Return on Capital (ROC)**: EBIT / (Net Working Capital + Net Fixed Assets) - measures how efficiently a company uses its capital

This project consists of two main scripts:
1. **Data Collection**: Fetches fundamental data for NYSE stocks and calculates Magic Formula metrics
2. **Ranking**: Ranks stocks based on the combined EY and ROC scores

## 🚀 Features

- Automatically fetches NYSE stock tickers from NASDAQ FTP servers
- Filters for common stocks (excludes ETFs, preferred stocks, warrants, etc.)
- Calculates EBIT, Enterprise Value, Earnings Yield, and Return on Capital
- Ranks stocks using the Magic Formula methodology
- Exports results to CSV files with date stamps
- Configurable ticker limits and rate limiting to avoid API throttling

## 📦 Requirements

Install the required dependencies:

```bash
pip install pandas yfinance yahoo-fin
```

### Dependencies
- `pandas` - Data manipulation and CSV handling
- `yfinance` - Yahoo Finance API for stock data
- `yahoo-fin` - Additional Yahoo Finance utilities

## 📁 Project Structure

```
magic_formula/
├── apps/
│   ├── magic_formula_nyse.py          # Main data collection script
│   ├── ranking_nyse.py                 # Ranking and scoring script
│   ├── magic_formula_nyse_*.csv        # Generated data files (date-stamped)
│   └── ranking_magic_formula_nyse.csv  # Final ranked results
└── README.md
```

## 🔧 Usage

### Step 1: Collect Stock Data

Run the main script to fetch and calculate Magic Formula metrics:

```bash
python magic_formula_nyse.py
```

This script will:
- Fetch NYSE tickers from NASDAQ FTP servers
- Filter for common stocks only
- Retrieve fundamental data (EBIT, market cap, debt, cash, etc.)
- Calculate EY and ROC for each stock
- Save results to `magic_formula_nyse_DDMMYYYY.csv`

**Configuration Options** (in `magic_formula_nyse.py`):
- `MAX_TICKERS`: Limit the number of tickers to process (set to `None` for all)
- `SLEEP_SECONDS`: Delay between API calls to avoid rate limiting (default: 0.5)

### Step 2: Rank Stocks

After collecting data, run the ranking script:

```bash
python ranking_nyse.py
```

**Note**: Update the CSV path in `ranking_nyse.py` to match your generated file.

This script will:
- Read the collected data
- Rank stocks by EY and ROC separately
- Calculate a combined score (lower is better)
- Filter out stocks with negative EBIT or EV
- Save ranked results to `ranking_magic_formula_nyse.csv`

## 📊 Output Format

### Data Collection Output (`magic_formula_nyse_*.csv`)

| Column | Description |
|--------|-------------|
| Ticker | Stock symbol |
| EBIT | Earnings Before Interest and Taxes |
| EV | Enterprise Value (Market Cap + Debt - Cash) |
| EY | Earnings Yield (EBIT / EV) |
| ROC | Return on Capital (EBIT / (NWC + Net PPE)) |

### Ranking Output (`ranking_magic_formula_nyse.csv`)

Includes all columns from data collection plus:
- `rank_EY`: Rank by Earnings Yield (1 = highest)
- `rank_ROC`: Rank by Return on Capital (1 = highest)
- `score`: Combined rank (rank_EY + rank_ROC, lower is better)
- `out_in`: Filter status ("in" = valid, "out" = negative EBIT/EV)

## 🎯 How the Magic Formula Works

1. **Earnings Yield (EY)**: Measures how cheap a stock is relative to its earnings
   - Higher EY = cheaper stock
   - Formula: EBIT / Enterprise Value

2. **Return on Capital (ROC)**: Measures how efficiently a company uses its capital
   - Higher ROC = more efficient
   - Formula: EBIT / (Net Working Capital + Net Fixed Assets)

3. **Ranking**: Stocks are ranked separately by EY and ROC, then combined
   - Best stocks have low combined rank scores
   - Stocks with negative EBIT or EV are filtered out

## ⚙️ Configuration

### Adjusting Ticker Limits

In `magic_formula_nyse.py`:
```python
MAX_TICKERS = None  # Process all tickers
# or
MAX_TICKERS = 200   # Process first 200 tickers
```

### Rate Limiting

Adjust the delay between API calls:
```python
SLEEP_SECONDS = 0.5  # 0.5 seconds between requests
```

### Updating CSV Paths

In `ranking_nyse.py`, update the file paths:
```python
csv_path = "path/to/your/magic_formula_nyse_*.csv"
output_path = "path/to/your/ranking_magic_formula_nyse.csv"
```

## ⚠️ Important Notes

- **API Rate Limits**: Yahoo Finance may throttle requests. Adjust `SLEEP_SECONDS` if you encounter rate limiting errors.
- **Data Availability**: Not all stocks will have complete fundamental data. The script skips stocks with insufficient data.
- **Market Hours**: Data is most accurate when markets are closed (after-hours or weekends).
- **File Paths**: The ranking script uses hardcoded paths. Update them to match your system.

## 📝 Example Workflow

1. Run `magic_formula_nyse.py` to collect data (may take 30+ minutes for all stocks)
2. Wait for completion and note the generated CSV filename
3. Update the CSV path in `ranking_nyse.py`
4. Run `ranking_nyse.py` to generate rankings
5. Review `ranking_magic_formula_nyse.csv` for top-ranked stocks

## 🔍 Filtering Logic

The script automatically filters stocks to include only:
- Common stocks
- Ordinary shares
- Class A, B, C shares

And excludes:
- Preferred stocks
- ETFs
- Units
- Warrants
- Rights
- Bonds
- Notes
- Index funds
- Trusts

## 📚 References

- [The Little Book That Beats the Market](https://www.magicformulainvesting.com/) by Joel Greenblatt
- Magic Formula methodology focuses on finding good companies at bargain prices

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is provided as-is for educational and research purposes.

