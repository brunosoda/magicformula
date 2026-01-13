import os
import time
from datetime import datetime

import pandas as pd
import yfinance as yf
from yahoo_fin import stock_info as si  # (mantido, mesmo não sendo usado aqui)

"""
# Lista estática atualizada em dias úteis
url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
df = pd.read_csv(url, sep="|")
nyse = df[df['Exchange'] == 'N']  # “N” representa NYSE
tickers = nyse['ACT Symbol'].tolist()
"""

# =========================
# CONFIG
# =========================
# Limite de tickers a processar.
# Use None para rodar todos (ou um número, ex: 200).
# MAX_TICKERS = None
MAX_TICKERS = None

# Delay entre chamadas (ajuda a evitar rate limit)
SLEEP_SECONDS = 0.5
# =========================


# URLs da FTP
ftp_nasdaq = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
ftp_other = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"

# Ler arquivos
nasdaq = pd.read_csv(ftp_nasdaq, sep="|")
other = pd.read_csv(ftp_other, sep="|")

# Filtrar apenas NYSE no arquivo 'otherlisted'
nyse = other[other["Exchange"] == "N"]  # "N" = NYSE

# Concatenar todos
tickers_raw = pd.concat([nasdaq, nyse], ignore_index=True)

# Palavras-chave para incluir e excluir
include_keywords = ["Common Stock", "Ordinary Shares", "Class A", "Class B", "Class C"]
exclude_keywords = ["Preferred", "ETF", "Unit", "Warrant", "Rights", "Bond", "Note", "Index", "Trust"]

# Criar máscaras
mask_include = tickers_raw["Security Name"].str.contains(
    "|".join(include_keywords),
    case=False,
    na=False
)
mask_exclude = ~tickers_raw["Security Name"].str.contains(
    "|".join(exclude_keywords),
    case=False,
    na=False
)

# Combinar filtros
mask = mask_include & mask_exclude

# Função para limpar tickers para yfinance
def clean_ticker(t):
    if pd.isna(t):
        return None
    t = str(t)
    # Troca $ por - e ponto por -
    t = t.replace("$", "-").replace(".", "-")
    return t

# Aplicar filtro e limpeza
tickers = [
    clean_ticker(t)
    for t in tickers_raw.loc[mask, "Symbol"]
    if pd.notna(t)
]

# Aplicar limite de iteração (se definido)
if isinstance(MAX_TICKERS, int) and MAX_TICKERS > 0:
    tickers = tickers[:MAX_TICKERS]

def get_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)

        income_stmt = stock.income_stmt
        balance = stock.balance_sheet
        fast = stock.fast_info

        # EBIT
        ebit = None
        for key in ["EBIT", "Operating Income"]:
            if key in income_stmt.index:
                ebit = income_stmt.loc[key].iloc[0]
                break

        # Market Cap
        market_cap = fast.get("marketCap", None)

        # Dívida total
        total_debt = balance.loc["Total Debt"].iloc[0] if "Total Debt" in balance.index else 0

        # Caixa
        cash = None
        for key in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
            if key in balance.index:
                cash = balance.loc[key].iloc[0]
                break
        if cash is None:
            cash = 0

        # EV = MarketCap + Debt - Cash
        ev = market_cap + total_debt - cash if market_cap else None

        # Outros dados
        total_assets = balance.loc["Total Assets"].iloc[0] if "Total Assets" in balance.index else None
        current_liabilities = (
            balance.loc["Current Liabilities"].iloc[0]
            if "Current Liabilities" in balance.index
            else None
        )
        net_fixed_assets = balance.loc["Net PPE"].iloc[0] if "Net PPE" in balance.index else None

        if ebit is None or ev is None:
            print(f"{ticker}: Dados insuficientes.")
            return None

        # Cálculos
        ey = ebit / ev if ev else None
        nwc = (total_assets - current_liabilities) if total_assets and current_liabilities else None
        roc = (ebit / (nwc + net_fixed_assets)) if ebit and nwc and net_fixed_assets else None

        print(f"{ticker}: EBIT={ebit}, EV={ev}, EY={ey}, ROC={roc}")

        return {
            "Ticker": ticker,
            "EBIT": ebit,
            "EV": ev,
            "EY": ey,
            "ROC": roc,
        }

    except Exception as e:
        print(f"Erro {ticker}: {e}")
        return None

results = []

for i, ticker in enumerate(tickers, start=1):
    data = get_fundamentals(ticker)
    if data:
        results.append(data)

    print(f"{i}/{len(tickers)} - {ticker}")
    time.sleep(SLEEP_SECONDS)

# =========================
# SALVAR CSV NA PASTA DA APLICAÇÃO
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data no formato DDMMYYYY (ex: 07012026)
today_str = datetime.now().strftime("%d%m%Y")

filename = f"magic_formula_nyse_{today_str}.csv"
file_path = os.path.join(BASE_DIR, filename)

df = pd.DataFrame(results)
df.to_csv(file_path, index=False)

print(f"Arquivo salvo em: {file_path}")
