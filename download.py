from pathlib import Path

import yfinance as yf

OUTPUT = Path("data")
OUTPUT.mkdir(exist_ok=True)

ticker = "NQ=F"

print("Downloading price data...")

df = yf.download(
    ticker,
    period="60d",
    interval="5m",
    auto_adjust=False
)

df = df.reset_index()

if hasattr(df.columns, "levels"):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

df.to_csv(OUTPUT / "NQ_5m.csv", index=False)

print(f"Saved {len(df)} candles.")
